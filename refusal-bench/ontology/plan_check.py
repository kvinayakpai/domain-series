"""Check plans the way the system will, and say why each one is refused. python3 plan_check.py PLANS.json QUESTIONS.json
PLANS.json maps id -> a plan (object) or its JSON text. Prints the decision per id and the layer that refused it, never the answer."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
plans = json.load(open(sys.argv[1])); qs = json.load(open(sys.argv[2]))
for x in qs:
    t = plans.get(x["id"])
    plan = t if isinstance(t, (dict, type(None))) else (lambda m: json.loads(m.group(0)) if m else None)(re.search(r"\{.*\}", t, re.S))
    r = P.run_plan(x["question"], plan) if plan is not None else dict(decision="no_record", message="no plan")
    if r["decision"] == "answer":
        parts = r.get("parts") or [r]
        print(x["id"], "OK", [(p["decision"], p.get("row_count")) if p["decision"] == "answer" else ("refused", p["message"][50:170]) for p in parts])
    else:
        print(x["id"], "REFUSED", r["message"][38:200])
