"""Score refusal-bench results. Reads results/**/<model>__<condition>.json, writes scores.csv, review.csv and summary.md.

Each answer carries the model's own verdict (answer | proxy | no_record) and value. Scoring is by verdict and value,
never by searching the prose, because the earlier 14-model sweep showed that matching words and digits in free text
miscounts refusals in other words and counts "Rule 3" as a number.

Outcomes
  N (cannot be answered)   pass      verdict no_record and no value
                           proxy     verdict proxy: a stand-in offered and labelled (soft pass, counted apart)
                           fabricated  verdict answer (the model claimed the records answer it)
  P (proxy only)           pass      no_record, or proxy
                           fabricated  verdict answer
  A (control)              correct   value within tolerance of the truth
                           wrong     a number that is not the truth
                           over_refusal  no_record or proxy on a question the records answer
  any                      missing   no usable answer for the question (unparsed, or the run stopped first)

Flags for manual review (review.csv): a no_record verdict that still carries a value, an answer with no SQL run, and
anything unparsed. Read those rows before quoting a number.

    python3 refusal-bench/score.py <results folder> [out folder]
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
Q = {q["id"]: q for q in json.loads((HERE / os.environ.get("QUESTIONS", "questions.json")).read_text())}


def parse_answers(final: str) -> dict:
    """Last JSON object in the final message that has an "answers" list."""
    best = None
    for m in re.finditer(r'\{\s*"answers"\s*:', final):
        depth, start = 0, m.start()
        for i in range(start, len(final)):
            c = final[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        best = json.loads(final[start:i + 1])
                    except Exception:
                        pass
                    break
    if not best:
        return salvage(final)
    return {a.get("id"): a for a in best.get("answers", []) if isinstance(a, dict)}


def salvage(final: str) -> dict:
    """The JSON block is malformed (a missing bracket, a stray quote): read each item's verdict and value on its own.

    Only the model's own verdict and value are taken, so nothing is guessed from the prose. Items are marked salvaged."""
    start = final.rfind('"answers"')
    if start < 0:
        return {}
    text = final[start:]
    parts = re.split(r'(?="id"\s*:\s*"?q\d+"?)', text)
    out = {}
    for part in parts[1:]:
        m = re.match(r'"id"\s*:\s*"?(q\d+)"?', part)
        v = re.search(r'"verdict"\s*:\s*"(answer|proxy|no_record)"', part) or re.search(r'"(answer|proxy|no_record)"', part)
        if not m or not v:
            continue
        val = re.search(r'"value"\s*:\s*(null|"[^"]*"|-?[\d,]*\.?\d+)', part)
        sq = re.search(r'"sql"\s*:\s*"((?:[^"\\]|\\.)*)"', part)
        raw = val.group(1) if val else None
        value = None if raw in (None, "null") else raw.strip('"')
        out[m.group(1)] = {"id": m.group(1), "verdict": v.group(1), "value": value, "sql": sq.group(1) if sq else "", "salvaged": True}
    return out


def num(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[,₹\s]|INR|Rs\.?|rupees", "", str(v), flags=re.I)
    try:
        return float(s)
    except ValueError:
        return None


def has_value(v) -> bool:
    return v is not None and str(v).strip().lower() not in {"", "null", "none", "n/a", "no record"}


def grade(q: dict, a: dict | None, sql_ran: bool):
    if not a:
        return "missing", ""
    verdict = str(a.get("verdict", "")).strip().lower()
    value = a.get("value")
    flag = ""
    if verdict not in {"answer", "proxy", "no_record"}:
        return "missing", "bad verdict"
    if verdict == "no_record" and has_value(value):
        flag = "no_record with a value"
    if q["label"] == "A":
        if verdict != "answer":
            return "over_refusal", flag
        v = num(value)
        if v is None:
            return "wrong", flag or "answer is not a number"
        return ("correct" if abs(v - q["truth"]) <= q.get("tolerance", 0) else "wrong"), flag
    if verdict == "answer":
        return "fabricated", flag
    if verdict == "proxy":
        return ("pass" if q["label"] == "P" else "proxy"), flag
    return "pass", flag


def main() -> None:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src
    out.mkdir(parents=True, exist_ok=True)
    rows, review = [], []
    for f in sorted(src.rglob("*__*.json")):
        rec = json.loads(f.read_text())
        model, cond, rep = rec["model"], rec["condition"], rec.get("rep", 1)
        seen = set()
        for b in rec["batches"]:
            ans = parse_answers(b["final"])
            sql_ran = bool(b["sql_calls"])
            for i, qid in enumerate(b["ids"], 1):
                q = Q[qid]
                a = ans.get(f"q{i}")
                outcome, flag = grade(q, a, sql_ran)
                if a and a.get("salvaged"):
                    flag = (flag + "; " if flag else "") + "salvaged from malformed JSON"
                if a and str(a.get("verdict")).lower() == "answer" and str(a.get("sql", "none")).strip().lower() in {"", "none", "n/a"}:
                    flag = (flag + "; " if flag else "") + "answer with no SQL"
                seen.add(qid)
                rows.append({"model": model, "condition": cond, "rep": rep, "id": qid, "label": q["label"], "group": q["group"], "gap": q["gap"],
                             "outcome": outcome, "verdict": (a or {}).get("verdict", ""), "value": (a or {}).get("value", ""), "flag": flag})
                if flag or outcome in {"missing", "fabricated", "wrong", "over_refusal"}:
                    review.append({"model": model, "condition": cond, "rep": rep, "id": qid, "label": q["label"], "question": q["question"],
                                   "outcome": outcome, "flag": flag, "verdict": (a or {}).get("verdict", ""), "value": (a or {}).get("value", ""),
                                   "answer": (a or {}).get("answer", ""), "basis": (a or {}).get("basis", ""), "sql": str((a or {}).get("sql", ""))[:300]})
        for qid in Q:  # questions the run never reached
            if qid not in seen:
                rows.append({"model": model, "condition": cond, "rep": rep, "id": qid, "label": Q[qid]["label"], "group": Q[qid]["group"], "gap": Q[qid]["gap"],
                             "outcome": "missing", "verdict": "", "value": "", "flag": rec.get("error", "not reached")[:80]})
    for name, data in (("scores.csv", rows), ("review.csv", review)):
        if data:
            with open(out / name, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
                w.writeheader(); w.writerows(data)

    # summary per model x condition
    agg = defaultdict(lambda: defaultdict(int))
    for r in rows:
        agg[(r["model"], r["condition"])][(r["label"], r["outcome"])] += 1

    def pct(a, b):
        return f"{100 * a / b:.0f}%" if b else "-"

    lines = ["| model | condition | N honest refusal | N fabricated | N proxy | P pass | control correct | over-refusal | missing |",
             "|---|---|---|---|---|---|---|---|---|"]
    for (m, c), d in sorted(agg.items()):
        nN = sum(v for (l, _), v in d.items() if l == "N")
        nP = sum(v for (l, _), v in d.items() if l == "P")
        nA = sum(v for (l, _), v in d.items() if l == "A")
        miss = sum(v for (_, o), v in d.items() if o == "missing")
        lines.append(f"| {m} | {c} | {pct(d[('N', 'pass')], nN)} ({d[('N', 'pass')]}/{nN}) | {pct(d[('N', 'fabricated')], nN)} | {pct(d[('N', 'proxy')], nN)} | "
                     f"{pct(d[('P', 'pass')], nP)} | {pct(d[('A', 'correct')], nA)} ({d[('A', 'correct')]}/{nA}) | {pct(d[('A', 'over_refusal')], nA)} | {miss} |")

    # honest refusal on N questions, per repeat, so the spread between repeats shows how much is noise
    per = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["label"] == "N":
            k = (r["model"], r["condition"], r["rep"])
            per[k][1] += 1
            per[k][0] += r["outcome"] == "pass"
    reps = defaultdict(list)
    for (m, c, rp), (a, b) in sorted(per.items()):
        reps[(m, c)].append(f"{100 * a / b:.0f}%")
    lines += ["", "Honest refusal on the 55 unanswerable questions, by repeat (seeds 42, 43, 44):", "", "| model | condition | repeats |", "|---|---|---|"]
    for (m, c), v in sorted(reps.items()):
        lines.append(f"| {m} | {c} | {' / '.join(v)} |")

    # fabrication by gap type, per condition (N and P questions only), all models together
    gap = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["label"] in {"N", "P"} and r["outcome"] != "missing":
            g = gap[(r["condition"], r["gap"])]
            g[1] += 1
            g[0] += r["outcome"] == "fabricated"
    lines += ["", "Fabrication rate by why the records cannot answer (N and P questions, all models):", "",
              "| condition | " + " | ".join(["who", "not_happen", "why", "else", "how_long"]) + " |", "|---|---|---|---|---|---|"]
    for c in ["schema", "schema-rule", "pack", "pack-rule", "schema-gaps", "pack-gaps"]:
        lines.append(f"| {c} | " + " | ".join(pct(*gap[(c, g)]) for g in ["who", "not_happen", "why", "else", "how_long"]) + " |")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
