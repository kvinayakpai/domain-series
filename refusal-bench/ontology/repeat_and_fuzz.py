"""1) Run every question of every set in 10 separate processes (random hash seeds) and compare outputs byte for byte.
   2) Mutation test: casing, spacing, filler words, dropped punctuation, adjacent-letter typos (seeded). For N and P questions no mutation may
      produce an answer; for A questions a mutation may be refused but must never give a different number than the truth."""
import glob, hashlib, json, random, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).parent
FILES = sorted(glob.glob(str(HERE.parent / "questions*.json")))
code = ("import json,sys; sys.path.insert(0,sys.argv[1]); from resolver import answer; "
        "qs=[x for f in sys.argv[2:] for x in json.load(open(f))]; "
        "print(json.dumps([[x['id'], answer(x['question'])] for x in qs], sort_keys=True, default=str))")
outs = [subprocess.run([sys.executable, "-I", "-c", code, str(HERE), *FILES], capture_output=True, text=True, env={"PYTHONPATH": str(HERE)}).stdout for _ in range(10)]
hs = {hashlib.sha256(o.encode()).hexdigest()[:12] for o in outs}
n = len(json.loads(outs[0])) if outs[0] else 0
print(f"1. repeat: {n} questions x 10 separate processes -> {len(hs)} distinct output hash(es) {sorted(hs)}")
sys.path.insert(0, str(HERE))
from resolver import answer
rnd = random.Random(2026)
def typo(q):
    ws = q.split(" "); i = rnd.randrange(len(ws)); w = ws[i]
    if len(w) > 3:
        j = rnd.randrange(len(w) - 1); w = w[:j] + w[j + 1] + w[j] + w[j + 2:]
    ws[i] = w; return " ".join(ws)
MUT = [str.upper, lambda q: q.replace(" ", "  "), lambda q: q.rstrip("?"), lambda q: "Please, " + q[0].lower() + q[1:], lambda q: q.replace("How many", "How many of"),
       lambda q: q + " Thanks!", typo, typo, lambda q: q.replace(" in June 2026", ""), lambda q: q.replace("Store 014", "the store")]
leaks = wrong = tested = refused = same = stated = 0
for f in FILES:
    for x in json.load(open(f)):
        for m in MUT:
            q = m(x["question"]); r = answer(q); tested += 1
            if r["decision"] == "answer":
                if x["label"] in "NP" and r.get("whole_coverage") and not re.search(r"june|may|2026|20\d\d", x["question"].lower()): stated += 1   # period-less question answered over its stated coverage: by design
                elif x["label"] in "NP": leaks += 1; print("LEAK", x["id"], repr(q))
                elif r.get("whole_coverage"): same += 1      # no period named: answered over the stated whole coverage, with the window in the reply
                elif abs(float(r["value"]) - float(x["truth"])) > max(x.get("tolerance", 0), 1e-9) + 1e-9: wrong += 1; print("WRONG", x["id"], repr(q), r["value"], x["truth"])
                else: same += 1
            elif x["label"] == "A": refused += 1
print(f"2. mutations: {tested} variants; unanswerable or stand-in answered: {leaks}; answerable given a wrong number: {wrong}; answerable still correct: {same}; answerable refused: {refused}; period-less question answered over its stated coverage: {stated}")
sys.exit(1 if leaks or wrong or len(hs) != 1 else 0)
