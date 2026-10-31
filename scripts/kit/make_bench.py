"""Build the Store 014 Bench: the series' 21 assistant questions plus one across domains, in a form any
assistant or agent can answer, an answer key, a scorer, and three scripted baselines.

    python3 scripts/kit/make_bench.py

Writes public/kit/bench/ (questions.json, answer-key.json, score.py, baselines/, README.md) and
public/kit/store-014-bench.zip, and checks that the scorer gives each baseline the score the
series reports. Every gold answer comes from the analyses' outputs (src/data/*-ai.json, finale.json),
which score themselves against the world's answer keys. No language model is called, here or in
the scorer.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "data"
OUT = ROOT / "public" / "kit" / "bench"
ZIP = ROOT / "public" / "kit" / "store-014-bench.zip"
RECORDS = "https://kvinayakpai.github.io/domain-series/data/"

R = json.loads((SRC / "retail-ai.json").read_text())["assistant"]
L = json.loads((SRC / "logistics-ai.json").read_text())["assistant"]
P = json.loads((SRC / "payments-ai.json").read_text())["assistant"]
F = json.loads((SRC / "finale.json").read_text())
Q = {**{f"retail.{q['id']}": q for q in R["questions"]}, **{f"logistics.{q['id']}": q for q in L["questions"]},
     **{f"payments.{q['id']}": q for q in P["questions"]}}

# For each question: the answer's fields, the scoring rule, and how the series' scripted assistant's
# naive and domain answers read in that form. The values come from the analyses' outputs.
ENUM_WHY = ["empty_shelf", "demand_fell", "switching", "other"]
ENUM_WHY_L = ["delivery", "theft", "counting", "demand_fell", "other"]
ENUM_WHOSE = ["customers", "store", "unclaimed", "other"]
ENUM_X = ["pallet_line", "empty_shelf", "demand_fell", "theft", "other"]


def spec() -> dict:
    g = lambda k: Q[k]["gold"]
    n = lambda k: Q[k]["naive"]
    d = lambda k: Q[k]["domain"]
    t = F["trace"]
    bursts = ["2026-06-20T18:00", "2026-06-20T19:00"]
    tim = lambda v: {"late_credit": v.get("late credit", 0), "debited_and_returned": v.get("debited and returned", 0),
                     "never_debited": v.get("never debited", 0)}
    return {
        "retail.sold": {"answer": {"bags": "integer"}, "rule": {"bags": ["exact"]}, "gold": {"bags": g("retail.sold")["value"]},
                        "naive": {"bags": n("retail.sold")["value"]}, "domain": {"bags": d("retail.sold")["value"]}},
        "retail.why": {"answer": {"cause": ENUM_WHY}, "rule": {"cause": ["exact"]}, "gold": {"cause": "empty_shelf"},
                       "naive": {"cause": "switching"}, "domain": {"cause": "empty_shelf" if d("retail.why")["says_shelf_empty"] else "other"}},
        "retail.in_stock": {"answer": {"on_shelf": "boolean"}, "rule": {"on_shelf": ["exact"]}, "gold": {"on_shelf": g("retail.in_stock")["on_shelf"]},
                            "naive": {"on_shelf": n("retail.in_stock")["on_shelf"]}, "domain": {"on_shelf": d("retail.in_stock")["on_shelf"]}},
        "retail.demand": {"answer": {"per_day": "number"}, "rule": {"per_day": ["within_pct", 10]}, "gold": {"per_day": g("retail.demand")["value"]},
                          "naive": {"per_day": n("retail.demand")["value"]}, "domain": {"per_day": d("retail.demand")["value"]}},
        "retail.switching": {"answer": {"switching": "boolean"}, "rule": {"switching": ["exact"]}, "gold": {"switching": g("retail.switching")["switching"]},
                             "naive": {"switching": n("retail.switching")["switching"]}, "domain": {"switching": d("retail.switching")["switching"]}},
        "retail.availability": {"answer": {"share": "number between 0 and 1"}, "rule": {"share": ["within_abs", 0.05]},
                                "gold": {"share": g("retail.availability")["value"]},
                                "naive": {"share": n("retail.availability")["value"]}, "domain": {"share": d("retail.availability")["value"]}},
        "retail.lost": {"answer": {"bags": "number"}, "rule": {"bags": ["within_pct", 20]}, "gold": {"bags": g("retail.lost")["value"]},
                        "naive": {"bags": n("retail.lost")["value"]}, "domain": {"bags": d("retail.lost")["value"]}},
        "logistics.slot": {"answer": {"deliveries": "integer"}, "rule": {"deliveries": ["exact"]}, "gold": {"deliveries": g("logistics.slot")["value"]},
                           "naive": {"deliveries": n("logistics.slot")["value"]}, "domain": {"deliveries": d("logistics.slot")["value"]}},
        "logistics.in_full": {"answer": {"in_full": "boolean"}, "rule": {"in_full": ["exact"]}, "gold": {"in_full": g("logistics.in_full")["in_full"]},
                              "naive": {"in_full": n("logistics.in_full")["in_full"]}, "domain": {"in_full": d("logistics.in_full")["in_full"]}},
        "logistics.otif": {"answer": {"share": "number between 0 and 1"}, "rule": {"share": ["within_abs", 0.02]}, "gold": {"share": g("logistics.otif")["value"]},
                           "naive": {"share": n("logistics.otif")["value"]}, "domain": {"share": d("logistics.otif")["value"]}},
        "logistics.why": {"answer": {"cause": ENUM_WHY_L}, "rule": {"cause": ["exact"]}, "gold": {"cause": "delivery"},
                          "naive": {"cause": "theft"}, "domain": {"cause": "delivery" if d("logistics.why")["names_delivery"] else "other"}},
        "logistics.theft": {"answer": {"theft": "boolean"}, "rule": {"theft": ["exact"]}, "gold": {"theft": g("logistics.theft")["theft"]},
                            "naive": {"theft": n("logistics.theft")["theft"]}, "domain": {"theft": d("logistics.theft")["theft"]}},
        "logistics.claim": {"answer": {"shipment_id": "string", "sscc": "string", "line": "integer"},
                            "rule": {"shipment_id": ["exact"], "sscc": ["exact"], "line": ["exact"]},
                            "gold": dict(zip(("shipment_id", "sscc", "line"), g("logistics.claim")["value"])),
                            "naive": {"shipment_id": None, "sscc": None, "line": None},
                            "domain": dict(zip(("shipment_id", "sscc", "line"), d("logistics.claim")["value"]))},
        "logistics.lost": {"answer": {"bags": "number"}, "rule": {"bags": ["within_pct", 20]}, "gold": {"bags": g("logistics.lost")["value"]},
                           "naive": {"bags": n("logistics.lost")["value"]}, "domain": {"bags": d("logistics.lost")["value"]}},
        "payments.attempts": {"answer": {"attempts": "integer"}, "rule": {"attempts": ["exact"]}, "gold": {"attempts": g("payments.attempts")["value"]},
                              "naive": {"attempts": n("payments.attempts")["value"]}, "domain": {"attempts": d("payments.attempts")["value"]}},
        "payments.twice": {"answer": {"customers": "integer"}, "rule": {"customers": ["exact"]}, "gold": {"customers": g("payments.twice")["value"]},
                           "naive": {"customers": n("payments.twice")["value"]}, "domain": {"customers": d("payments.twice")["value"]}},
        "payments.timeouts": {"answer": {"late_credit": "integer", "debited_and_returned": "integer", "never_debited": "integer"},
                              "rule": {"late_credit": ["exact"], "debited_and_returned": ["exact"], "never_debited": ["exact"]},
                              "gold": tim(g("payments.timeouts")["value"]),
                              "naive": tim(n("payments.timeouts")["value"]), "domain": tim(d("payments.timeouts")["value"])},
        "payments.suspense": {"answer": {"whose": ENUM_WHOSE}, "rule": {"whose": ["exact"]}, "gold": {"whose": "customers"},
                              "naive": {"whose": "unclaimed"}, "domain": {"whose": "customers" if d("payments.suspense")["names_customers"] else "other"}},
        "payments.wait": {"answer": {"median_days_from_debit": "number", "unrefunded": "integer"},
                          "rule": {"median_days_from_debit": ["within_abs", 0.5], "unrefunded": ["exact"]},
                          "gold": {"median_days_from_debit": g("payments.wait")["value"], "unrefunded": g("payments.wait")["unrefunded"]},
                          "naive": {"median_days_from_debit": n("payments.wait")["value"], "unrefunded": n("payments.wait")["unrefunded"]},
                          "domain": {"median_days_from_debit": d("payments.wait")["value"], "unrefunded": d("payments.wait")["unrefunded"]}},
        "payments.declines": {"answer": {"burst_hours": "list of hours, as YYYY-MM-DDTHH:00, when the rate was not acceptable; empty if none"},
                              "rule": {"burst_hours": ["overlaps", bursts]}, "gold": {"burst_hours": bursts},
                              "naive": {"burst_hours": []}, "domain": {"burst_hours": bursts if d("payments.declines")["says_burst"] else []}},
        "payments.refund_now": {"answer": {"rrns": "list of the RRNs of the extra charges to refund"}, "rule": {"rrns": ["same_set"]},
                                "gold": {"rrns": g("payments.refund_now")["value"]},
                                "naive": {"rrns": n("payments.refund_now")["value"]}, "domain": {"rrns": d("payments.refund_now")["value"]}},
        "across.trace": {"answer": {"cause": ENUM_X, "shipment_id": "string or null", "line": "integer or null", "actual_sku": "string or null"},
                         "rule": {"cause": ["exact"], "shipment_id": ["exact"], "line": ["exact"], "actual_sku": ["exact"]},
                         "gold": {"cause": "pallet_line", "shipment_id": t["names"]["shipment_id"], "line": t["names"]["line"],
                                  "actual_sku": t["answer_key"]["sku"]},
                         # Scripted readings of the same records: with the schema, a sales silence is demand falling;
                         # with the retail layer it is an empty shelf; with the map it is followed to the warehouse.
                         "naive": {"cause": "demand_fell", "shipment_id": None, "line": None, "actual_sku": None},
                         "domain": {"cause": "empty_shelf", "shipment_id": None, "line": None, "actual_sku": None},
                         "map": {"cause": "pallet_line", "shipment_id": t["names"]["shipment_id"], "line": t["names"]["line"],
                                 "actual_sku": t["names"]["sku"]}},
    }


TEXT = {
    "across.trace": ("It is 20:00 on Tuesday 23 June. Why has 5 kg atta stopped selling at Store 014 this evening, and if a "
                     "delivery is to blame, which shipment and line, and what was really on it?"),
}
AS_OF = {"retail": R["as_of"], "logistics": L["as_of"], "payments": P["as_of"], "across": F["trace"]["at"]}
SOURCE = {"retail": "retail/technical/", "logistics": "logistics/technical/", "payments": "payments/technical/", "across": "who-saw-what/"}

SCORE_PY = r'''"""Score answers to the Store 014 Bench.

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
'''

README = """# Store 014 Bench

Twenty-two questions about one month at Store 014, the fictional Bengaluru supermarket of the series
*Why Domain Matters* (https://kvinayakpai.github.io/domain-series/). Seven on the shelf, seven on the
truck, seven on the money, and one across them. Each has an answer key from the synthetic world,
which knows what really happened, so an assistant's or an agent's answers can be scored, not judged.

## What is here

- `questions.json`: each question, the time it is asked, and the fields an answer must have.
- `answer-key.json`: the gold answers and the scoring rule for each field.
- `score.py`: the scorer. Plain Python 3, no packages, no model calls.
- `baselines/`: the answers of the series' scripted assistant (rules, not a language model), given
  the schema only (`schema-only.json`), the three posts' domain layers (`domain-layers.json`), and
  the domain layers plus the map of who saw what (`map.json`).

## Run your own

1. Download the records: https://kvinayakpai.github.io/domain-series/data/ (CSV files, one month).
2. Give your assistant the records it would have in your setting, and ask each question. Use only
   rows timestamped before the question's `as_of`.
3. Write its answers as one JSON object, keyed by question id, each answer an object with the
   fields `questions.json` lists.
4. `python score.py answers.json`

Run it twice, once with the schema alone and once with a domain layer (the series' layers are in the
technical companions, and the map is `store-014-map.json` next to the records), and compare.

## Baselines

| Answers | Right |
|---|---|
BASELINE_ROWS

The questions come from the series' three technical companions and its last post. Because the world
is synthetic and seeded, every reader sees the same month, and the answer key is complete.
"""


def main() -> None:
    sp = spec()
    questions, answers = [], {}
    for qid, s in sp.items():
        dom = qid.split(".")[0]
        q = Q.get(qid)
        questions.append({"id": qid, "domain": dom, "as_of": AS_OF[dom], "question": TEXT.get(qid) or q["question"],
                          "answer": s["answer"], "scoring": (q["check"] if q else "names the shipment, the line and what was on it"),
                          "from": f"https://kvinayakpai.github.io/domain-series/{SOURCE[dom]}"})
        answers[qid] = {"gold": s["gold"], "rule": s["rule"], "why": (q["gold"]["why"] if q else
                        "Line 1 of SHP-260622 held 160 packs of 1 kg atta, from the answer key.")}
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "baselines").mkdir(parents=True)
    (OUT / "questions.json").write_text(json.dumps({"about": "Store 014 Bench: questions. Records: " + RECORDS, "questions": questions},
                                                   indent=1, ensure_ascii=False) + "\n")
    (OUT / "answer-key.json").write_text(json.dumps({"about": "Store 014 Bench: answer key and scoring rules.", "answers": answers},
                                                    indent=1, ensure_ascii=False) + "\n")
    (OUT / "score.py").write_text(SCORE_PY)
    base = {
        "schema-only": {qid: s["naive"] for qid, s in sp.items()},
        "domain-layers": {qid: s["domain"] for qid, s in sp.items()},
        "map": {qid: s.get("map", s["domain"]) for qid, s in sp.items()},
    }
    sys.path.insert(0, str(OUT))
    import score as scorer
    results = {}
    for name, ans in base.items():
        (OUT / "baselines" / f"{name}.json").write_text(json.dumps(ans, indent=1, ensure_ascii=False) + "\n")
        results[name] = scorer.score(ans)
    # The scorer must agree with the series: one right per domain with the schema, seven with each layer.
    s0, s1, s2 = results["schema-only"], results["domain-layers"], results["map"]
    assert [s0["by_domain"][d]["right"] for d in ("retail", "logistics", "payments")] == [R["score"]["naive"], L["score"]["naive"], P["score"]["naive"]]
    assert [s1["by_domain"][d]["right"] for d in ("retail", "logistics", "payments")] == [R["score"]["domain"], L["score"]["domain"], P["score"]["domain"]]
    assert s2["right"] == s2["of"] and s1["by_domain"]["across"]["right"] == 0
    label = {"schema-only": "Scripted assistant, schema only", "domain-layers": "Scripted assistant, with the three domain layers",
             "map": "Scripted assistant, with the domain layers and the map"}
    rows = "\n".join(f"| {label[k]} | {v['right']} of {v['of']} |" for k, v in results.items())
    (OUT / "README.md").write_text(README.replace("BASELINE_ROWS", rows))
    (ROOT / "src" / "data" / "bench.json").write_text(json.dumps({
        "questions": len(questions), "by_domain": {d: sum(q["domain"] == d for q in questions) for d in ("retail", "logistics", "payments", "across")},
        "baselines": {k: {"right": v["right"], "of": v["of"], "by_domain": v["by_domain"]} for k, v in results.items()},
        "sample": [{"id": q["id"], "as_of": q["as_of"], "question": q["question"], "answer": q["answer"]}
                   for q in questions if q["id"] in ("retail.availability", "logistics.claim", "payments.wait", "across.trace")],
    }, indent=1, ensure_ascii=False) + "\n")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                z.write(p, Path("store-014-bench") / p.relative_to(OUT))
    shutil.rmtree(OUT / "__pycache__", ignore_errors=True)
    # Run the scorer the way a reader would.
    subprocess.run([sys.executable, str(OUT / "score.py"), str(OUT / "baselines" / "map.json")], check=True, stdout=subprocess.DEVNULL)
    shutil.rmtree(OUT / "__pycache__", ignore_errors=True)
    for k, v in results.items():
        print(f"{k:14s} {v['right']} of {v['of']}  {v['by_domain']}")
    print(f"wrote {OUT.relative_to(ROOT)} and {ZIP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
