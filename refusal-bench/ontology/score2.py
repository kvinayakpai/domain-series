"""Score step 2: every model planned each question AT the layer the panel assigned (269 questions; the 22 refusals are not run).

python3 score2.py STEP2_QUESTIONS.json PANEL_PLANS_DIR OUT_DIR  [--haiku DIR_WITH_plans-haiku-b*.json]  [--nvidia RESULTS_DIR]  [--claude NAME=DIR ...]

Each model's plan goes through step2.run_at (checked, run, refused if it uses more than the assigned layer).
Outcome per question, against the panel's answer: same as panel / differs / refused, panel answered (said cannot, invalid plan, beyond the layer) / no plan."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import moe as M
import score as S
import step2


def run_at(question, plan, layer):
    if plan is None or (isinstance(plan, dict) and ("raw" in plan or not plan)): return dict(decision="no_plan")
    try: return step2.run_at(question, plan, layer)
    except Exception as ex:  # noqa: BLE001
        return dict(decision="no_record", message=f"crash {type(ex).__name__}")


def kind(r):
    if r.get("beyond_layer"): return "beyond the layer"
    return S.kind_of_refusal(r)


def load_dir(d, pattern):
    out = {}
    for f in sorted(Path(d).glob(pattern)): out.update(json.load(open(f)))
    return out


if __name__ == "__main__":
    qfile, panel_dir, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    opts = {}; a = sys.argv[4:]
    models = {}
    while a:
        k, v = a.pop(0), a.pop(0)
        if k == "--haiku": models["haiku"] = load_dir(v, "plans-haiku-b*.json")
        elif k == "--nvidia": models.update(S.merged_nvidia(v))
        elif k == "--claude": n, d = v.split("="); models[n] = load_dir(d, f"plans-{n}-b*.json")
    qs = json.load(open(qfile))
    experts = M.load_plans(panel_dir)
    ref = {}
    for x in qs:
        res, results = M.panel(x["question"], {e: experts[e].get(x["id"]) for e in M.EXPERTS})
        ref[x["id"]] = (res, results.get(res["expert"]) if res["decision"] == "answer" else dict(decision="no_record"))
    card, per_q, by_layer = {}, defaultdict(dict), {}
    for m, plans in models.items():
        c = Counter(); lay = defaultdict(Counter)
        for x in qs:
            r = run_at(x["question"], plans.get(x["id"]), x["layer"])
            o = S.outcome(r, ref[x["id"]][1])
            if o == "refused, panel answered": o += f" ({kind(r)})"
            c[o] += 1; lay[x["layer"]][o.split(" (")[0]] += 1; per_q[x["id"]][m] = o
        n = len(qs); same = c["same as panel"]
        card[m] = dict(questions=n, same_as_panel=same, same_pct=round(100 * same / n, 1), outcomes=dict(c), by_assigned_layer={k: dict(v) for k, v in lay.items()})
    json.dump(dict(card=card, per_question=per_q), open(out / "scorecard-step2.json", "w"), indent=1, default=str)
    for m, v in card.items(): print(m, v["same_as_panel"], f"{v['same_pct']}%", v["outcomes"])
