"""Planner benchmark, version 3 instructions. MODEL=... INSTR_V3=1 python3 plan_eval3.py OUTDIR questions.json BATCH NBATCH
Asks the model for a plan per question in this batch, checks and runs each plan (schema, ontology, knowledge layer), and writes
plans.json (the raw plans), results.json (decision, layer, rows per question) and summary.json."""
import json, os, re, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
qs = json.load(open(sys.argv[2])); b, nb = int(sys.argv[3]), int(sys.argv[4])
size = -(-len(qs) // nb); qs = qs[(b - 1) * size: b * size]
plans, results, c = {}, {}, collections.Counter()
for x in qs:
    t = P.model_plan_raw(x["question"]); plan = None
    if t:
        m = re.search(r"\{.*\}", t, re.S)
        try: plan = json.loads(m.group(0)) if m else None
        except Exception: plan = None
    plans[x["id"]] = plan if plan is not None else {"raw": (t or "")[:400], "error": P.LAST_ERROR if t is None else "unparsable"}
    try: r = P.run_plan(x["question"], plan) if plan is not None else dict(decision="no_plan", message="no usable plan")
    except Exception as e: r = dict(decision="no_plan", message=f"error {type(e).__name__}")
    c[r["decision"]] += 1
    if t is None: c["no_reply"] += 1
    results[x["id"]] = {k: v for k, v in r.items() if k in ("decision", "layer", "declared_layer", "failed_layer", "message", "columns", "rows", "row_count", "answered_parts", "total_parts", "parts")}
    (out / "plans.json").write_text(json.dumps(plans, indent=1, ensure_ascii=False))
    (out / "results.json").write_text(json.dumps(results, indent=1, default=str, ensure_ascii=False))
    if c["no_reply"] >= 8 and c["no_reply"] == len(results): print("STOP: no usable reply", P.LAST_ERROR); break
(out / "summary.json").write_text(json.dumps({"model": os.environ.get("MODEL"), "batch": b, **c}, indent=1)); print(dict(c))
