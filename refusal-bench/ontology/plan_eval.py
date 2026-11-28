"""Ask a real model for plans over a question file and run them through the planning layer (one planner).
   MODEL=... [BASE_URL=... KEY_ENV=...] python3 plan_eval.py OUTDIR questions.json"""
import json, os, re, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
qs = json.load(open(sys.argv[2])); raw = {}; recs = []; c = collections.Counter()
for x in qs:
    t = P.model_plan_raw(x["question"]); raw[x["id"]] = t
    plan = None
    if t:
        m = re.search(r"\{.*\}", t, re.S)
        try: plan = json.loads(m.group(0)) if m else None
        except Exception: plan = None
    r = P.answer_by_plan(x["question"], lambda q: plan)
    c[(r["decision"], r.get("failed_layer"))] += 1
    if t is None: c["no_reply"] += 1
    recs.append(dict(id=x["id"], question=x["question"], decision=r["decision"], failed_layer=r.get("failed_layer"), message=r["message"], columns=r.get("columns"), rows=(r.get("rows") or [])[:6], row_count=r.get("row_count"), plan=r.get("plan_in_words"), error=(P.LAST_ERROR if t is None else None)))
    if c["no_reply"] >= 6 and c["no_reply"] == len(recs):
        print("STOP: no usable reply", P.LAST_ERROR); break
(out / "plans.json").write_text(json.dumps(raw, indent=1, ensure_ascii=False)); (out / "plan-results.json").write_text(json.dumps(recs, indent=1, default=str, ensure_ascii=False))
(out / "summary.json").write_text(json.dumps({"model": os.environ.get("MODEL"), **{f"{k[0]}:{k[1]}" if isinstance(k, tuple) else k: v for k, v in sorted(c.items(), key=str)}}, indent=1))
print(open(out / "summary.json").read())
