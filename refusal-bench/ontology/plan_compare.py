"""Compare a model's plans with Opus's. python3 plan_compare.py MODEL_PLANS.json [OPUS_PLANS.json]
For each question: answered parts and their rows, then how many question answers match Opus (same rows in every part both answered), conflict, or are refused where Opus answered."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
qs = json.load(open("/tmp/ct/v2-questions.json")); mine = json.load(open(sys.argv[1])); opus = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "/tmp/ct/plans-opus-v2.json"))
def run(q, plan):
    try:
        if not isinstance(plan, dict) or "raw" in plan: return None
        r = P.run_plan(q, plan)
    except Exception: return None
    parts = r.get("parts") or [r]
    return [(p["decision"], [tuple(map(str, row)) for row in p.get("rows", [])] if p["decision"] == "answer" else None) for p in parts]
def norm(rows): return sorted(rows)
def fits(a, b):
    """Same number of rows, and each row of the narrower answer has all its values inside the matching row of the wider one."""
    if len(a) != len(b): return False
    a, b = sorted(a, key=lambda r: sorted(r)), sorted(b, key=lambda r: sorted(r))
    small, big = (a, b) if len(a[0] if a else ()) <= len(b[0] if b else ()) else (b, a)
    rem = list(big)
    for r in small:
        hit = next((x for x in rem if all(v in x for v in r)), None)
        if hit is None: return False
        rem.remove(hit)
    return True
tot = dict(answered=0, same=0, conflict=0, refused_opus_answered=0, answered_opus_refused=0, cannot_or_bad=0)
detail = {}
for x in qs:
    a = run(x["question"], mine.get(x["id"])); o = run(x["question"], opus.get(x["id"]))
    ans = lambda r: bool(r) and any(d == "answer" for d, _ in r)
    if not a: tot["cannot_or_bad"] += 1
    if ans(a): tot["answered"] += 1
    if ans(a) and ans(o):
        orows = [norm(rr) for d, rr in o if d == "answer"]; arows = [norm(rr) for d, rr in a if d == "answer"]
        same = all(any(fits(ar, orr) for orr in orows) for ar in arows) or all(any(fits(orr, ar) for ar in arows) for orr in orows)
        tot["same" if same else "conflict"] += 1; detail[x["id"]] = "same" if same else "conflict"
    elif ans(o) and not ans(a): tot["refused_opus_answered"] += 1; detail[x["id"]] = "refused, Opus answered"
    elif ans(a) and not ans(o): tot["answered_opus_refused"] += 1; detail[x["id"]] = "answered, Opus refused"
print(json.dumps(tot)); print({k: v for k, v in detail.items() if v != "same"})
