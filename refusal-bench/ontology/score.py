"""Score every planner on the 291-question benchmark against the planning panel, and list what needs a check against the records.

python3 score.py QUESTIONS.json PANEL_PLANS_DIR NVIDIA_RESULTS_DIR OUT_DIR

For each model and question the model's own plan is checked and run exactly as the panel's plans are. Outcomes:
  same as panel      both answered and at least one result part is identical to a part of the panel's answer
  differs            both answered, no identical part
  refused, panel answered / answered, panel refused / both refused
  invalid plan       the checks refused the plan (a table, column, join, date or sum that is not allowed): the code caught a mistake
  no plan            the model gave no usable reply
Layer: the layer code verified for the model's answer (schema, ontology, knowledge), and whether the model's own claim matched."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import planner as P
import moe as M


def merged_nvidia(d):
    """model name -> {question id -> plan} from every batch folder of a run."""
    out = defaultdict(dict)
    for f in Path(d).glob("*/batch-*/plans.json"):
        out[f.parent.parent.name].update(json.load(open(f)))
    return dict(out)


def run(question, plan):
    if plan is None or (isinstance(plan, dict) and ("raw" in plan or not plan)):
        return dict(decision="no_plan")
    try:
        return P.run_plan(question, plan)
    except Exception as ex:  # noqa: BLE001
        return dict(decision="no_record", message=f"crash {type(ex).__name__}")


def outcome(r, pr):
    a = r["decision"] == "answer"; pa = pr["decision"] == "answer"
    if r["decision"] == "no_plan": return "no plan"
    if a and pa:
        mine = [M.norm(p.get("rows")) for p in M.answered_parts(r)]; theirs = [M.norm(p.get("rows")) for p in M.answered_parts(pr)]
        return "same as panel" if any(M.same(x, y) for x in mine for y in theirs) else "differs"
    if a: return "answered, panel refused"
    if pa: return "refused, panel answered"
    return "both refused"


def kind_of_refusal(r):
    m = r.get("message", "")
    if r["decision"] == "no_plan": return "no plan"
    if "no valid query plan" in m: return "said cannot"
    if "refused the plan" in m or "could not be checked" in m or "crash" in m: return "invalid plan"
    return "other"


if __name__ == "__main__":
    qfile, panel_dir, nv_dir, out = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
    qs = json.load(open(qfile))
    experts = M.load_plans(panel_dir)
    models = {**{e: experts[e] for e in M.EXPERTS}, **merged_nvidia(nv_dir)}
    panel = {}; panel_results = {}
    for x in qs:
        res, results = M.panel(x["question"], {e: experts[e].get(x["id"]) for e in M.EXPERTS})
        panel[x["id"]] = res; panel_results[x["id"]] = results.get(res["expert"]) if res["decision"] == "answer" else dict(decision="no_record")
    card = {}; per_q = defaultdict(dict)
    for m, plans in models.items():
        c = Counter(); layers = Counter(); claim = Counter()
        for x in qs:
            r = run(x["question"], plans.get(x["id"]))
            o = outcome(r, panel_results[x["id"]]); c[o] += 1
            if r["decision"] == "answer":
                c["answered"] += 1
                lay = M.layer_of(x["question"], r); layers[lay] += 1
                declared = [p.get("declared_layer") for p in M.answered_parts(r) if p.get("declared_layer")]
                if declared: claim["claim matches" if lay in declared or (lay == "knowledge") == ("knowledge" in declared) else "claim differs"] += 1
            else:
                c["refused"] += 1; c["refusal: " + kind_of_refusal(r)] += 1
            per_q[x["id"]][m] = o
        card[m] = dict(outcomes=dict(c), layers=dict(layers), layer_claims=dict(claim), plans_received=sum(1 for x in qs if plans.get(x["id"]) is not None and "raw" not in (plans.get(x["id"]) or {})))
    card["panel"] = dict(outcomes=dict(Counter(("answered" if v["decision"] == "answer" else "refused") for v in panel.values())),
                         layers=dict(Counter(v["layer"] for v in panel.values())), support=dict(Counter(v["support"] for v in panel.values() if v["decision"] == "answer")))
    json.dump(dict(card=card, per_question=per_q, panel={k: {kk: vv for kk, vv in v.items() if kk != "reply"} for k, v in panel.items()}), open(out / "scorecard.json", "w"), indent=1, default=str)
    json.dump({k: v["reply"] for k, v in panel.items()}, open(out / "panel-replies.json", "w"), indent=1, ensure_ascii=False)
    for m, v in card.items(): print(m, v)
