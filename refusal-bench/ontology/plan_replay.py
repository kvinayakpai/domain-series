"""Replay saved model plans through the planning layer. python3 plan_replay.py OUTDIR PLANS.json QUESTIONS.json"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
plans = json.load(open(sys.argv[2])); qs = json.load(open(sys.argv[3]))
byq = {x["question"]: plans.get(x["id"]) for x in qs}
def planner(question):
    t = byq.get(question)
    if not t: return None
    m = re.search(r"\{.*\}", t, re.S)
    try: return json.loads(m.group(0)) if m else None
    except Exception: return None
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); recs = []
for x in qs:
    r = P.answer_by_plan(x["question"], planner)
    recs.append(dict(id=x["id"], question=x["question"], decision=r["decision"], layers=r["layers"], message=r["message"], columns=r.get("columns"), rows=(r.get("rows") or [])[:8], row_count=r.get("row_count"), sql=r.get("sql"), plan_in_words=r.get("plan_in_words")))
(out / "plan-results.json").write_text(json.dumps(recs, indent=1, default=str, ensure_ascii=False))
import collections
print(collections.Counter(r["decision"] for r in recs))
for r in recs:
    print(r["id"], r["decision"], "|", (f"{r['row_count']} rows {r['rows'][:2]}" if r["decision"] == "answer" else r["message"][38:150]))
