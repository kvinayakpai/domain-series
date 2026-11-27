"""Score the guard on a question set by its own label: N -> no_record, P -> no_record or proxy, A -> pass. No model, no results needed.
    python3 refusal-bench/guards/evaluate.py refusal-bench/questions.json [more files]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from guard import decide  # noqa: E402

for f in sys.argv[1:]:
    qs = json.load(open(f)); bad = []; n = {"N": [0, 0], "P": [0, 0], "A": [0, 0]}
    for q in qs:
        d = decide(q["question"])["decision"]; ok = (d == "no_record") if q["label"] == "N" else (d in ("no_record", "proxy")) if q["label"] == "P" else d == "pass"
        n[q["label"]][1] += 1; n[q["label"]][0] += ok
        if not ok: bad.append((q["id"], q["label"], d, q["question"][:90]))
    print(f"== {Path(f).name}: N right {n['N'][0]}/{n['N'][1]}, P right {n['P'][0]}/{n['P'][1]}, A right {n['A'][0]}/{n['A'][1]}")
    for b in bad: print("   MISS", b)
