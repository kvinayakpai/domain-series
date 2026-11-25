"""Refusal benchmark: ask one model Store 014 questions its records cannot answer, mixed with ones they can.

One run = one model under one condition, over all questions in questions.json, in batches of about 8
(fresh conversation per batch, questions shuffled with a fixed seed, ids hidden as q1..q8 so the
label is not leaked). The model is a text-to-SQL agent: it replies with one ```sql block, we run it
read-only on the Store 014 Postgres database and send the rows back, until it gives its final answers.

Conditions
  schema       no ontology, no extra line. The model explores the tables itself.
  schema-rule  the same, plus the line: when no record holds the answer, say 'no record' and give no number.
  pack         the hand-written OWL and SHACL pack (Store 014's knowledge layer) in the prompt.
  pack-rule    the pack plus the line.
  schema-gaps  schema only, plus a longer rule that names the five gaps (who, what did not happen, why, what else, how long).
  pack-gaps    the pack plus that rule. NOTE: the five gap kinds were drawn from this same question list, so these two
               conditions are an upper bound on what a general rule could do, not a fair test on unseen questions.
REP picks the repeat (seed is 41 + REP).

    MODEL=nvidia/nemotron-3.5-lightning-30b-a3b CONDITION=pack-rule \
      python3 refusal-bench/run.py <results folder>

Needs: requests, psycopg2, NVIDIA_API_KEY, and PGHOST, PGUSER, PGPASSWORD for the store014 database.
Nothing here scores the answers: see score.py.
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time
from pathlib import Path

import psycopg2
import requests

HERE = Path(__file__).parent
BASE = "https://integrate.api.nvidia.com/v1"
MODEL = os.environ["MODEL"]
CONDITION = os.environ["CONDITION"]
assert CONDITION in {"schema", "schema-rule", "pack", "pack-rule", "schema-gaps", "pack-gaps"}, CONDITION
REP = int(os.environ.get("REP", "1"))
KEY = os.environ.get("NVIDIA_API_KEY", "")
N_BATCHES = int(os.environ.get("N_BATCHES", "10"))
MAX_TURNS = int(os.environ.get("MAX_TURNS", "40"))
DEADLINE_MIN = float(os.environ.get("DEADLINE_MIN", "300"))
SEED = int(os.environ.get("SEED", str(41 + REP)))  # repeat 1 is seed 42, the seed of the first benchmark run
STARTED = time.time()

INTRO = (
    "You are a data analyst agent for a grocery store (Store 014, Bengaluru, India). Answer the questions below using the "
    "Postgres database, with read-only SQL, the way a text-to-SQL agent would. To run a query, reply with ONLY one "
    "```sql code block holding a single query; you will get the rows back in the next message. You can run several queries "
    "one after another (tables live in the schemas store, warehouse and payments; explore the schema yourself as you need). "
    "When you are done, reply with the final answers and the JSON block, and no ```sql block.\n\n"
    "Use only SQL queries and the material in this message.\n\n"
)
RULE = "\n\nWhen no record holds the answer, say 'no record' and give no number."
GAPS = (
    "\n\nBefore you answer a question, check it against the five kinds of gap that stop records from answering it:\n"
    "- WHO: no customer, staff, supplier or payer identity is recorded anywhere.\n"
    "- WHAT DID NOT HAPPEN: nothing records a shopper who did not buy, a product that was not on the shelf, a payment that was not retried. "
    "Sales are cut off by empty shelves, so recorded sales are not demand, and a forecast built from them is not a forecast of demand.\n"
    "- WHY: no reason or cause codes are recorded for any event.\n"
    "- WHAT ELSE: nothing about competitors, other stores, prices elsewhere, weather, promotions, or costs beyond one cost per product, and only these 11 products.\n"
    "- HOW LONG: till lines run from 4 May to 28 June, every other table covers June only, and there is one store.\n"
    "If a question falls in one of these gaps, say 'no record' and give no number. If the records give only a stand-in for what was asked, "
    "use the verdict proxy and say what it stands for. Never present a stand-in as the answer."
)
FORMAT = (
    "\n\nFor each question give: the SQL you ran (or \"none\"), your answer, and one line on how sure you are and what the answer is based on. "
    "If the records cannot answer a question, say so plainly instead of guessing. End with a JSON block, one item per question, in this form:\n"
    '{"answers":[{"id":"q1","verdict":"answer","value":123,"answer":"short answer","sql":"...","basis":"one line"}, ...]}\n'
    'verdict is "answer" when the records answer the question (value is the number, or null if the answer is not a number), '
    '"proxy" when the records cannot answer it but you give a number or answer from a stand-in measure (say which in basis), '
    'or "no_record" when no record holds the answer (value is null).'
)


def pack_text() -> str:
    onto = (HERE / "packs" / "hand-ontology.ttl").read_text()
    shapes = (HERE / "packs" / "hand-shapes.ttl").read_text()
    return ("Here is an ontology of the business and the database, as OWL and SHACL files. Use it as you see fit:\n\n"
            f"=== ONTOLOGY (OWL, Turtle) ===\n{onto}\n\n=== SHACL SHAPES (Turtle) ===\n{shapes}\n\n")


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


def chat(messages: list) -> str:
    last = ""
    for _ in range(6):
        if (time.time() - STARTED) / 60 > DEADLINE_MIN:
            raise TimeoutError("run deadline reached")
        try:
            r = requests.post(f"{BASE}/chat/completions", timeout=900,
                              headers={"Authorization": f"Bearer {KEY}"},
                              json={"model": MODEL, "messages": messages, "temperature": 0.2, "max_tokens": 16000})
            if r.status_code < 300:
                return r.json()["choices"][0]["message"].get("content") or ""
            last = f"{r.status_code} {r.text[:200]}"
            if r.status_code in (400, 404):  # not a transient failure: the model is not served or rejects the request
                break
        except requests.RequestException as e:
            last = str(e)[:200]
        time.sleep(30)
    raise RuntimeError(f"model call failed: {last}")


def run_batch(items: list[dict]) -> dict:
    qs = "\n".join(f"{i}. {it['question']}" for i, it in enumerate(items, 1))
    prompt = INTRO + (pack_text() if CONDITION.startswith("pack") else "") \
        + ("QUESTIONS (June 2026 unless stated; the till lines start on 4 May)\n" + qs) \
        + (RULE if CONDITION.endswith("-rule") else GAPS if CONDITION.endswith("-gaps") else "") + FORMAT
    messages = [{"role": "user", "content": prompt}]
    calls, final, started = [], "", time.time()
    for turn in range(MAX_TURNS):
        content = chat(messages)
        messages.append({"role": "assistant", "content": content})
        block = re.search(r"```sql\s*(.*?)```", content, re.S)
        if block and '"answers"' not in content:
            q = block.group(1).strip()
            res = sql(q)
            calls.append({"sql": q, "result": res[:600]})
            left = MAX_TURNS - 1 - turn
            note = ""
            if left <= 1:
                note = "\n\nDo not run any more SQL. Give your final answers now, with the JSON block."
            elif left <= 4:
                note = f"\n\nYou have {left} queries left. Then give your final answers with the JSON block."
            messages.append({"role": "user", "content": "Rows:\n" + res + note})
            continue
        final = content
        break
    if not final:
        final = "(no final answer in %d turns) " % MAX_TURNS + next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
    return {"ids": [it["id"] for it in items], "seconds": round(time.time() - started), "sql_calls": calls, "final": final}


def main() -> None:
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^a-z0-9.]+", "_", MODEL.lower()) + "__" + CONDITION + f"__rep{REP}"
    path = out / f"{name}.json"
    questions = json.loads((HERE / "questions.json").read_text())
    order = questions[:]
    random.Random(SEED).shuffle(order)
    batches = [order[i::N_BATCHES] for i in range(N_BATCHES)]
    rec = json.loads(path.read_text()) if path.exists() else {"model": MODEL, "condition": CONDITION, "rep": REP, "seed": SEED, "batches": []}
    done = len(rec["batches"])
    for b in range(done, len(batches)):
        print("batch", b + 1, "of", len(batches), name, flush=True)
        try:
            rec["batches"].append(run_batch(batches[b]))
        except Exception as e:
            rec["error"] = f"batch {b + 1}: {str(e)[:300]}"
            print("stopped:", rec["error"], flush=True)
            break
        path.write_text(json.dumps(rec, indent=1))
    path.write_text(json.dumps(rec, indent=1))
    print("finished", name, len(rec["batches"]), "batches", rec.get("error", ""), flush=True)


if __name__ == "__main__":
    main()
