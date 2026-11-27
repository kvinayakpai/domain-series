"""Run the thin model layer (real model) over question files. Scores the FINAL answer, and records every model call.
   MODEL=... NVIDIA_API_KEY=... python3 refusal-bench/ontology/thin_eval.py OUTDIR file1.json file2.json ..."""
import json, os, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import thin_layer as T

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
T.CACHE = out / "rewrite-cache.json"; T.PROPOSALS = out / "synonym-proposals.json"
T.CACHE.write_text("{}"); T.PROPOSALS.write_text('{"proposals": []}')
recs, c = [], Counter()
for f in sys.argv[2:]:
    for x in json.load(open(f)):
        r = T.answer_with_model(x["question"]); a = r["audit"]; L = x["label"]
        d = r["decision"]; via = r["via"]
        if L == "A":
            right = d == "answer" and abs(float(r["value"]) - float(x["truth"])) <= max(x.get("tolerance", 0), 1e-9) + 1e-9
            kind = "right" if right else ("WRONG" if d == "answer" else "refused")
        else:
            kind = "LEAK" if d == "answer" else "refused"
        c[(L, kind)] += 1
        if a["model_called"]:
            c["model_calls"] += 1
            if str(a.get("rewrite", "")).startswith("no usable reply"): c["unusable_replies"] += 1
            if c["model_calls"] >= 6 and c["unusable_replies"] == c["model_calls"]:
                print("STOP: the first 6 model calls gave no usable reply:", a.get("rewrite")); (out / "stopped.txt").write_text(str(a.get("rewrite"))); sys.exit(1)
        if via.startswith("model"): c[(L, "answered_via_model")] += 1
        if a.get("verified") is False: c["rewrites_rejected"] += 1
        recs.append(dict(set=Path(f).name, id=x["id"], label=L, question=x["question"], kind=kind, value=r.get("value"), truth=x.get("truth"), via=via, audit=a))
        if kind in ("LEAK", "WRONG"): print(kind, x["id"], x["question"], "->", r.get("value"), json.dumps(a)[:300])
(out / "thin-results.json").write_text(json.dumps(recs, indent=1, default=str))
summary = {f"{k[0]}:{k[1]}" if isinstance(k, tuple) else k: v for k, v in sorted(c.items(), key=str)}
(out / "summary.json").write_text(json.dumps({"model": os.environ.get("MODEL"), **summary}, indent=1))
print(json.dumps({"model": os.environ.get("MODEL"), **summary}, indent=1))
