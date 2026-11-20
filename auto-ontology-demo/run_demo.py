"""Drive a running Auto-Ontology through its REST API, with no clicks.

Signs in as the bootstrap admin, turns on semantic compilation (the step that drafts
the ontology from the ingested tables), waits for it to finish, then saves what it
drafted and asks it a fixed set of questions. Everything goes to the output folder,
including partial results when a step fails or runs out of time.

    python3 auto-ontology-demo/run_demo.py <out-dir>

Reads APP_URL, AUTO_ONTOLOGY_ADMIN_EMAIL and AUTO_ONTOLOGY_ADMIN_PASSWORD, and
BUDGET_MIN (minutes for compilation and questions together, default 290).
Standard library only.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("APP_URL", "http://localhost:3000").rstrip("/")
INGESTION = os.environ.get("INGESTION_URL", "http://localhost:3002").rstrip("/")
EMAIL = os.environ["AUTO_ONTOLOGY_ADMIN_EMAIL"]
PASSWORD = os.environ["AUTO_ONTOLOGY_ADMIN_PASSWORD"]
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
QUESTIONS = json.loads(Path(__file__).with_name("questions.json").read_text())
BUDGET_S = float(os.environ.get("BUDGET_MIN", "290")) * 60
ASK_TIMEOUT_S = float(os.environ.get("ASK_TIMEOUT_MIN", "40")) * 60
START = time.time()
cookies: dict[str, str] = {}
run: dict = {"started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "phases": {}}


def log(message: str) -> None:
    print(f"[{(time.time() - START) / 60:6.1f} min] {message}", flush=True)


def left() -> float:
    return BUDGET_S - (time.time() - START)


_last_checkpoint = 0.0


def checkpoint(note: str, force: bool = False) -> None:
    """Push the results so far to the branch (every 10 minutes at most), with log tails."""
    global _last_checkpoint
    if os.environ.get("CHECKPOINT_PUSH") != "1" or (not force and time.time() - _last_checkpoint < 600):
        return
    _last_checkpoint = time.time()
    scrub = [s for s in os.environ.get("SCRUB", "").split("|") if s]
    logs = OUT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    for name, lines in (("auto-ontology-ingestion-service", "200"), ("auto-ontology", "80"), ("model-adapter", "300"), ("ollama", "40")):
        try:
            tail = subprocess.run(["docker", "logs", "--tail", lines, name], capture_output=True, text=True, timeout=60)
            text = tail.stdout + tail.stderr
            for secret in scrub:
                text = text.replace(secret, "[redacted]")
            (logs / f"progress-{name}.log").write_text(text)
        except Exception:
            pass
    branch = os.environ.get("GITHUB_REF_NAME", "")
    try:
        subprocess.run(["git", "add", str(OUT)], capture_output=True, timeout=120)
        subprocess.run(["git", "commit", "-q", "-m", f"Auto-Ontology demo progress: {note}"], capture_output=True, timeout=120)
        for _ in range(3):  # each run writes its own folder, so a rebase never conflicts
            subprocess.run(["git", "pull", "-q", "--rebase", "origin", branch], capture_output=True, timeout=120)
            if subprocess.run(["git", "push", "-q", "origin", f"HEAD:{branch}"], capture_output=True, timeout=120).returncode == 0:
                return
            time.sleep(5)
    except Exception:
        return


def save(name: str, payload: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if isinstance(payload, (bytes, str)):
        path.write_bytes(payload if isinstance(payload, bytes) else payload.encode())
    else:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")


def request(method: str, url: str, body: object = None, timeout: float = 120, accept: str = "application/json"):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Accept": accept, "Origin": BASE}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    response = urlopen(Request(url, data=data, headers=headers, method=method), timeout=timeout)
    for header in response.headers.get_all("Set-Cookie") or []:
        pair = header.split(";", 1)[0]
        if "=" in pair:
            key, value = pair.split("=", 1)
            cookies[key.strip()] = value.strip()
    return response


def call(method: str, path: str, body: object = None, timeout: float = 120):
    with request(method, BASE + path, body, timeout) as response:
        payload = response.read()
    return json.loads(payload) if payload else None


def phase(name: str):
    def wrap(fn):
        def inner(*args, **kwargs):
            began = time.time()
            record = run["phases"].setdefault(name, {})
            log(f"{name}: start")
            try:
                result = fn(record, *args, **kwargs)
                record.setdefault("status", "ok")
                return result
            except Exception as error:  # keep going: later steps save what exists
                record["status"] = "failed"
                record["error"] = f"{type(error).__name__}: {error}"
                if isinstance(error, HTTPError):
                    try:
                        record["error_body"] = error.read().decode()[:4000]
                    except Exception:
                        pass
                record["traceback"] = traceback.format_exc()[-4000:]
                log(f"{name}: FAILED {record['error']}")
                return None
            finally:
                record["minutes"] = round((time.time() - began) / 60, 1)
                save("run.json", run)
                checkpoint(f"{name} {record.get('status')}", force=True)
        return inner
    return wrap


@phase("sign_in")
def sign_in(record: dict) -> None:
    deadline = time.time() + 1800
    while True:
        try:
            call("POST", "/api/auth/sign-in/email", {"email": EMAIL, "password": PASSWORD}, timeout=60)
            call("GET", "/api/terms?limit=1")
            record["tries_until_signed_in"] = record.get("tries", 0) + 1
            return
        except (HTTPError, URLError, ConnectionError, TimeoutError) as error:
            record["tries"] = record.get("tries", 0) + 1
            record["last_wait_reason"] = f"{type(error).__name__}: {error}"
            if time.time() > deadline:
                raise
            time.sleep(15)


@phase("compile")
def compile_ontology(record: dict) -> None:
    call("PUT", "/api/configurations/semantic-compilation", {"enabled": True})
    polls = record.setdefault("polls", [])
    while True:
        status = call("GET", "/api/semantic-compilation/status")
        polls.append({"minute": round((time.time() - START) / 60, 1), **(status or {})})
        if len(polls) % 5 == 1:
            log(f"compile status {status}")
        if status and not status.get("running") and (status.get("last_success_at") or status.get("last_failure_at")):
            record["result"] = "succeeded" if status.get("last_success_at") else "failed"
            record["final_status"] = status
            if not status.get("last_success_at"):
                record["status"] = "failed"
            return
        if left() < 45 * 60:  # keep time for saving the draft and asking questions
            record["status"] = "timed_out"
            record["final_status"] = status
            return
        save("run.json", run)
        checkpoint(f"compiling, minute {polls[-1]['minute']}")
        time.sleep(60)


@phase("collect")
def collect(record: dict) -> None:
    terms, skip = [], 0
    while True:
        page = call("GET", f"/api/terms?skip={skip}&limit=100")
        batch = (page or {}).get("terms") or []
        terms.extend(batch)
        skip += len(batch)
        if not batch or skip >= (page or {}).get("total", 0):
            break
    save("terms.json", terms)
    record["terms"] = len(terms)
    details, related = {}, {}
    for term in terms:
        term_id = term["id"]
        try:
            details[term_id] = call("GET", f"/api/exploration/terms/{term_id}/details")
        except HTTPError as error:
            details[term_id] = {"error": error.code}
        try:
            related[term_id] = call("GET", f"/api/exploration/nodes/{term_id}/relationships?layer=semantic")
        except HTTPError as error:
            related[term_id] = {"error": error.code}
    save("term-details.json", details)
    save("term-relationships.json", related)


@phase("export")
def export(record: dict) -> None:
    """Export the draft as Apache Ossie YAML and, either way, in Auto-Ontology's own format."""
    record["files"] = {}
    for fmt in ("ossie", "auto_ontology"):
        body = {"format": fmt, "include_ontology": True} if fmt == "ossie" else {"format": fmt}
        try:
            with request("POST", BASE + "/api/model/export", body, timeout=600, accept="application/x-yaml, application/zip") as response:
                kind = response.headers.get("Content-Type", "")
                payload = response.read()
        except HTTPError as error:  # a refusal is a finding too: keep its reason
            record[f"{fmt}_refused"] = {"code": error.code, "body": error.read().decode()[:4000]}
            continue
        name = f"store014-{fmt.replace('_', '-')}.{'zip' if 'zip' in kind else 'yaml'}"
        save(name, payload)
        record["files"][name] = len(payload)
    if not record["files"]:
        record["status"] = "failed"


@phase("coverage")
def coverage(record: dict) -> None:
    results = []
    for item in QUESTIONS:
        began = time.time()
        try:
            result = call("POST", "/api/question-entity-coverage", {"question": item["question"]}, timeout=1800)
        except HTTPError as error:
            result = {"error": error.code, "body": error.read().decode()[:2000]}
        except Exception as error:
            result = {"error": f"{type(error).__name__}: {error}"}
        results.append({**item, "seconds": round(time.time() - began), "result": result})
        save("coverage.json", results)
        log(f"coverage: {item['id']} done")
    record["questions"] = len(results)


def ask_one(question: str, timeout: float) -> dict:
    events, steps = [], []
    began = time.time()
    with request("POST", BASE + "/api/chat/completions", {"question": question}, timeout=timeout, accept="text/event-stream") as response:
        while True:
            line = response.readline()
            if not line:
                break
            text = line.decode("utf-8", "replace").strip()
            if not text.startswith("data:"):
                continue
            data = text[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "step":
                steps.append({k: event.get(k) for k in ("node", "phase", "thought")})
            else:
                events.append(event)
            if time.time() - began > timeout:
                events.append({"type": "error", "message": "stopped: time limit"})
                break
    return {"seconds": round(time.time() - began), "steps": steps, "events": events}


@phase("ask")
def ask(record: dict) -> None:
    answers = []
    for item in [q for q in QUESTIONS if q.get("ask")]:
        if left() < 5 * 60:
            answers.append({**item, "skipped": "out of time"})
            continue
        try:
            outcome = ask_one(item["question"], min(ASK_TIMEOUT_S, left() - 120))
        except Exception as error:
            outcome = {"error": f"{type(error).__name__}: {error}"}
        answers.append({**item, **outcome})
        save("answers.json", answers)
        log(f"ask: {item['id']} done")
        checkpoint(f"asked {item['id']}")
    record["asked"] = len([a for a in answers if "skipped" not in a])


@phase("switch_model")
def switch_model(record: dict) -> None:
    """Answer with a second model, if one is set, through the model adapter."""
    model = os.environ.get("ANSWER_MODEL", "")
    record["answer_model"] = model or "same as the draft"
    if model:
        body = json.dumps({"model": model}).encode()
        adapter = os.environ.get("ADAPTER_URL", "http://localhost:8000").rstrip("/")
        with urlopen(Request(adapter + "/admin/chat-model", data=body, headers={"Content-Type": "application/json"}), timeout=60) as response:
            record["adapter_says"] = json.load(response)


def ingestion_status() -> None:
    try:
        with urlopen(INGESTION + "/semantic/status", timeout=30) as response:
            run["ingestion_semantic_status"] = json.load(response)
    except Exception as error:
        run["ingestion_semantic_status"] = f"{type(error).__name__}: {error}"


def main() -> int:
    sign_in()
    if run["phases"]["sign_in"]["status"] != "ok":
        return 1
    compile_ontology()
    ingestion_status()
    collect()
    export()
    switch_model()
    coverage()
    ask()
    run["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save("run.json", run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
