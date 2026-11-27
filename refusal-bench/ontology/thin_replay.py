"""Replay saved model replies through the thin layer. python3 thin_replay.py OUTDIR REPLIES.json questions.json..."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import thin_layer as T
replies = json.load(open(sys.argv[2])); qs = [x for f in sys.argv[3:] for x in json.load(open(f))]
byq = {x["question"]: replies.get(x["id"]) for x in qs}
def rewriter(question):
    t = byq.get(question)
    if not t: T.LAST_ERROR = "no reply saved"; return None
    m = re.search(r"\{.*\}", t, re.S)
    if not m: T.LAST_ERROR = "no JSON in the reply"; return None
    try: return json.loads(m.group(0))
    except Exception as e: T.LAST_ERROR = f"bad JSON: {e}"; return None
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
T.CACHE = out / "rewrite-cache.json"; T.PROPOSALS = out / "synonym-proposals.json"
T.CACHE.write_text("{}"); T.PROPOSALS.write_text('{"proposals": []}')
import collections; c = collections.Counter(); recs = []
for x in qs:
    r = T.answer_with_model(x["question"], rewriter=rewriter); a = r["audit"]; L = x["label"]; d = r["decision"]
    if L in ("A", "E") and d == "answer":
        kind = "right" if abs(float(r["value"]) - float(x["truth"])) < 1e-9 else "WRONG"
    elif L == "A": kind = "refused"
    elif L == "E": kind = "refused (allowed)"
    else: kind = "LEAK" if d == "answer" else "refused"
    c[(L, kind)] += 1
    if a["model_called"]: c["model_calls"] += 1
    if r["via"].startswith("model"): c["answered_via_model"] += 1
    if a.get("verified") is False: c["rewrites_rejected"] += 1
    recs.append(dict(id=x["id"], question=x["question"], kind=kind, value=r.get("value"), via=r["via"], audit=a))
    if kind in ("LEAK", "WRONG"): print(kind, x["id"], x["question"], r.get("value"), json.dumps(a)[:300])
(out / "results.json").write_text(json.dumps(recs, indent=1, default=str))
print({f"{k[0]}:{k[1]}" if isinstance(k, tuple) else k: v for k, v in sorted(c.items(), key=str)})
