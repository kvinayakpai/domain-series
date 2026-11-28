"""Planner test with the three-layer instructions. MODEL=... INSTR_V2=1 python3 plan_eval2.py OUTDIR questions.json
Saves each plan, runs it through run_plan (schema, ontology, knowledge layer), writes plans.json, report.md and summary.json."""
import json, os, re, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
qs = json.load(open(sys.argv[2])); plans = {}; c = collections.Counter(); md = []; stat = {}
for x in qs:
    t = P.model_plan_raw(x["question"]); plan = None
    if t:
        m = re.search(r"\{.*\}", t, re.S)
        try: plan = json.loads(m.group(0)) if m else None
        except Exception: plan = None
    plans[x["id"]] = plan if plan is not None else {"raw": (t or "")[:300], "error": P.LAST_ERROR if t is None else "unparsable"}
    try: r = P.run_plan(x["question"], plan) if plan is not None else dict(decision="no_record", layers=["schema"], failed_layer="schema", message="I can't answer this from Store 014's records: no usable plan was returned.", trace=[])
    except Exception as e: r = dict(decision="no_record", layers=["schema"], failed_layer="schema", message=f"I can't answer this from Store 014's records: error {type(e).__name__}", trace=[])
    stat[x["id"]] = r["decision"]; c[r["decision"]] += 1
    if t is None: c["no_reply"] += 1
    md.append(f"## {x['id']}: {x['question']}\n\n{P.render(x['question'], r)}\n")
    if c["no_reply"] >= 6 and c["no_reply"] == len(stat): print("STOP", P.LAST_ERROR); break
(out / "plans.json").write_text(json.dumps(plans, indent=1, ensure_ascii=False)); (out / "report.md").write_text("\n".join(md))
(out / "summary.json").write_text(json.dumps({"model": os.environ.get("MODEL"), **c, "per_question": stat}, indent=1)); print(c)
