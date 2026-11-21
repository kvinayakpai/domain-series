"""Give a model an OWL and SHACL pack, a read-only SQL tool and four questions about 5 kg atta.

For each run in matrix.json (model, pack, whether a "say no record, never a number" line is added)
the model answers the questions as a text-to-SQL agent would. The raw final answers and every SQL
call are written to results/<model>-<pack>[-rule].json. Nothing here scores the answers.

    python3 owl-packs-test/run.py <results folder> [model ...]

Needs: requests, psycopg2 (and PGHOST, PGUSER, PGPASSWORD, PGPORT if not the defaults). NVIDIA_API_KEY for nemotron; an Ollama server on :11434 for qwen.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import psycopg2
import requests

HERE = Path(__file__).parent
MODELS = {
    "nemotron": {"base": "https://integrate.api.nvidia.com/v1", "key": os.environ.get("NVIDIA_API_KEY", ""),
                 "name": "nvidia/nemotron-3.5-lightning-30b-a3b"},
    "qwen": {"base": "http://localhost:11434/v1", "key": "ollama", "name": "qwen-16k"},
    # Qwen on NVIDIA's own GPUs through the free hosted API. These models take no tool calls, so the model
    # writes a ```sql block, we run it and send the rows back (protocol "text").
    "nim": {"base": "https://integrate.api.nvidia.com/v1", "key": os.environ.get("NVIDIA_API_KEY", ""),
                 "name": os.environ.get("NIM_MODEL", "google/gemma-3-12b-it"), "protocol": "text"},
}
TEXT_INTRO = (
    "You are a data analyst agent for a grocery store (Store 014, India). Answer the questions below using the "
    "Postgres database, with read-only SQL, the way a text-to-SQL agent would. To run a query, reply with ONLY one "
    "```sql code block holding a single query; you will get the rows back in the next message. You can run several queries "
    "one after another (tables live in the schemas store, warehouse and payments; explore the schema yourself as you need). "
    "When you are done, reply with the final answers and the JSON block, and no ```sql block.\n\n"
    "Use only SQL queries and the material in this message.\n\n"
)
INTRO = (
    "You are a data analyst agent for a grocery store (Store 014, India). Answer the questions below using the "
    "Postgres database, with read-only SQL, the way a text-to-SQL agent would. Call the run_sql tool to run a query "
    "(tables live in the schemas store, warehouse and payments; explore the schema yourself as you need).\n\n"
    "Use only the run_sql tool and the material in this message.\n\n"
)
RULE = ("\n\nWhen no record holds the answer, say 'no record' and give no number.")
QUESTIONS = (
    "\n\nQUESTIONS\n1. How many bags of 5 kg atta were sold in June 2026?\n2. How many shoppers left without 5 kg atta in June 2026?\n"
    "3. What was on-shelf availability for 5 kg atta in June 2026?\n4. What were the lost sales of 5 kg atta in June 2026?\n\n"
    "For each question give: the SQL you ran (or \"none\"), your answer, and one line on how sure you are and what the answer is based on. "
    "If the records cannot answer a question, say so plainly instead of guessing. End with a JSON block:\n"
    '{"answers":[{"id":1,"sql":"...","answer":"...","basis":"..."}, ... 4 items]}'
)
TOOL = [{"type": "function", "function": {
    "name": "run_sql", "description": "Run one read-only SQL query on the Store 014 database and return the rows.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}]


def pack_text(pack: str) -> str:
    onto = (HERE / "packs" / f"{pack}-ontology.ttl").read_text()
    shapes = (HERE / "packs" / f"{pack}-shapes.ttl").read_text()
    return f"=== ONTOLOGY (OWL, Turtle) ===\n{onto}\n\n=== SHACL SHAPES (Turtle) ===\n{shapes}"


def sql(query: str) -> str:
    try:
        con = psycopg2.connect(dbname="store014",
                               options="-c default_transaction_read_only=on -c statement_timeout=30000")
        with con, con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchmany(60)
            out = "\n".join("|".join("" if v is None else str(v) for v in r) for r in rows)
        con.close()
        return out[:4000] or "(no rows)"
    except Exception as e:  # the model sees the error, as a text-to-SQL agent would
        return f"ERROR: {str(e)[:500]}"


def chat(cfg: dict, messages: list) -> dict:
    text = cfg.get("protocol") == "text"
    last = ""
    for attempt in range(6):
        try:
            r = requests.post(f"{cfg['base']}/chat/completions", timeout=900,
                              headers={"Authorization": f"Bearer {cfg['key']}"},
                              json={"model": cfg["name"], "messages": messages, **({} if text else {"tools": TOOL}), "temperature": 0.2, "max_tokens": 16000})
            if r.status_code < 300:
                return r.json()["choices"][0]["message"]
            last = f"{r.status_code} {r.text[:200]}"
        except requests.RequestException as e:
            last = str(e)[:200]
        time.sleep(30)
    raise RuntimeError(f"model call failed 6 times: {last}")


def run_one(model: str, pack: str, rule: bool) -> dict:
    cfg = MODELS[model]
    text = cfg.get("protocol") == "text"
    prompt = (TEXT_INTRO if text else INTRO) + "Here is an ontology of the business and the database, as OWL and SHACL files. Use it as you see fit:\n\n" + pack_text(pack) + (RULE if rule else "") + QUESTIONS
    messages = [{"role": "user", "content": prompt}]
    calls, final, started = [], "", time.time()
    for _ in range(16):
        msg = chat(cfg, messages)
        if text:
            import re
            content = msg.get("content") or ""
            block = re.search(r"```sql\s*(.*?)```", content, re.S)
            messages.append({"role": "assistant", "content": content})
            if block and '"answers"' not in content:
                q = block.group(1).strip()
                res = sql(q)
                calls.append({"sql": q, "result": res[:600]})
                messages.append({"role": "user", "content": "Rows:\n" + res})
                continue
            final = content
            break
        messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls") and v is not None})
        if not msg.get("tool_calls"):
            final = msg.get("content") or ""
            break
        for tc in msg["tool_calls"]:
            try:
                q = json.loads(tc["function"]["arguments"]).get("query", "")
            except Exception:
                q = ""
            res = sql(q)
            calls.append({"sql": q, "result": res[:600]})
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": res})
    if not final and text:
        final = "(no final answer in 16 turns) " + next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
    return {"model": cfg["name"], "pack": pack, "rule_line": rule, "prompt_chars": len(prompt),
            "seconds": round(time.time() - started), "sql_calls": calls, "final": final}


def main() -> None:
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[2:])
    for run in json.loads((HERE / "matrix.json").read_text()):
        if only and run["model"] not in only:
            continue
        tag = re.sub(r"[^a-z0-9.]+", "_", MODELS[run["model"]]["name"].lower()) if run["model"] == "nim" else run["model"]
        name = f"{tag}-{run['pack']}{'-rule' if run['rule'] else ''}"
        print("running", name, flush=True)
        try:
            rec = run_one(run["model"], run["pack"], run["rule"])
        except Exception as e:
            rec = {"model": run["model"], "pack": run["pack"], "rule_line": run["rule"], "error": str(e)[:300]}
        (out / f"{name}.json").write_text(json.dumps(rec, indent=2))
        print("done", name, rec.get("seconds"), rec.get("error", ""), flush=True)


if __name__ == "__main__":
    main()
