"""Score the layered resolver on question files: N must not be answered, P must be refused or proxy, A must be answered with the true value.
   python3 refusal-bench/ontology/eval_resolver.py refusal-bench/questions*.json [-v]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from resolver import answer
verbose = "-v" in sys.argv
tot = dict(N=[0, 0], P=[0, 0], A=[0, 0, 0])
for f in [a for a in sys.argv[1:] if a != "-v"]:
    n = {"N": [0, 0], "P": [0, 0], "A": [0, 0, 0]}
    for x in json.load(open(f)):
        r = answer(x["question"]); d = r["decision"]; L = x["label"]
        if L == "N": ok = d == "no_record" or d == "proxy"; leak = d == "answer"
        elif L == "P": ok = d in ("no_record", "proxy"); leak = d == "answer"
        else:
            ok = d == "answer" and abs(float(r["value"]) - float(x["truth"])) <= max(x.get("tolerance", 0), 1e-9) + 1e-9
            leak = d == "answer" and not ok
        n[L][1] += 1; n[L][0] += ok
        if L == "A": n[L][2] += leak
        if verbose and not ok:
            print(f"  {L} {x['id']} {d} {r.get('value')} truth={x.get('truth')} | {x['question'][:95]} | {(r.get('message') or '')[:110]}")
        if L != "A" and leak: print("  LEAK", x["id"], x["question"])
    print(f"== {Path(f).name}: N {n['N'][0]}/{n['N'][1]}  P {n['P'][0]}/{n['P'][1]}  A answered-right {n['A'][0]}/{n['A'][1]} (wrong numbers: {n['A'][2]})")
    for k in "NP": tot[k][0] += n[k][0]; tot[k][1] += n[k][1]
    for i in range(3): tot["A"][i] += n["A"][i]
print("TOTAL", tot)
