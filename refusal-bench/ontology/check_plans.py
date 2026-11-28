"""Self-check for a planner's file: python3 -I /tmp/moe/check_plans.py QUESTIONS.json PLANS.json
Prints, per plan, whether the code accepts it (OK / REFUSED + the reason). Does not show any answers' values."""
import json, sys
sys.path.insert(0, "/home/claude/domain-series/refusal-bench/ontology")
import planner as P
qs = {q["id"]: q["question"] for q in json.load(open(sys.argv[1]))}
plans = json.load(open(sys.argv[2]))
bad = 0
for qid, plan in plans.items():
    if qid not in qs: print(qid, "NOT A BENCHMARK ID"); bad += 1; continue
    if isinstance(plan, dict) and "cannot" in plan: print(qid, "cannot:", str(plan["cannot"])[:90]); continue
    r = P.run_plan(qs[qid], plan)
    if r["decision"] == "answer": print(qid, "OK", r.get("layer"), "rows:", r.get("row_count"))
    else: bad += 1; print(qid, "REFUSED:", r["message"][:230])
print("plans:", len(plans), "refused by the checker:", bad)
