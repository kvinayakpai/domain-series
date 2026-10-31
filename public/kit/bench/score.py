"""Score answers to the Store 014 Bench.

    python score.py answers.json            # prints each question's result and the totals
    python score.py answers.json --json     # the same, as JSON

answers.json maps each question id to an object with the fields questions.json asks for, e.g.
{"payments.twice": {"customers": 24}, "logistics.claim": {"shipment_id": "...", "sscc": "...", "line": 1}}.
A question left out, or a field missing, scores as wrong. No model is called.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(rule, got, want):
    kind = rule[0]
    if got is None:
        return want is None
    if kind == "exact":
        return got == want
    if kind == "within_pct":
        return isinstance(got, (int, float)) and abs(got - want) <= abs(want) * rule[1] / 100
    if kind == "within_abs":
        return isinstance(got, (int, float)) and abs(got - want) <= rule[1] + 1e-9
    if kind == "same_set":
        return isinstance(got, list) and sorted(map(str, got)) == sorted(map(str, want))
    if kind == "overlaps":
        return isinstance(got, list) and bool(set(map(str, got)) & set(rule[1]))
    raise ValueError(f"unknown rule {kind}")


def score(answers: dict) -> dict:
    key = json.loads((HERE / "answer-key.json").read_text())
    out = []
    for qid, k in key["answers"].items():
        a = answers.get(qid) or {}
        fields = {f: check(rule, a.get(f), k["gold"][f]) for f, rule in k["rule"].items()}
        out.append({"id": qid, "right": all(fields.values()), "fields": fields})
    by = {}
    for r in out:
        d = r["id"].split(".")[0]
        by.setdefault(d, [0, 0])
        by[d][0] += r["right"]
        by[d][1] += 1
    return {"right": sum(r["right"] for r in out), "of": len(out), "by_domain": {d: {"right": v[0], "of": v[1]} for d, v in by.items()},
            "questions": out}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    s = score(json.loads(Path(sys.argv[1]).read_text()))
    if "--json" in sys.argv:
        print(json.dumps(s, indent=1))
    else:
        for r in s["questions"]:
            print(f"{'right' if r['right'] else 'wrong':5s}  {r['id']}" + ("" if r["right"] else f"  ({', '.join(f for f, ok in r['fields'].items() if not ok)})"))
        print(f"\n{s['right']} of {s['of']} right: " + ", ".join(f"{d} {v['right']} of {v['of']}" for d, v in s["by_domain"].items()))
