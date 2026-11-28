"""The planning panel (mixture of experts): three expert planners each propose a plan; code checks every plan through the
schema layer, the ontology layer and the knowledge layer, and code picks the answer. No model writes the answer.

Experts, in order of trust: Opus, Sonnet, Haiku (chosen from the 55-question comparison of 28 Nov 2026).

How the panel decides, for each question:
 1. Every expert's plan is checked and run. A plan that fails a check is not a candidate.
 2. No candidate: a polite refusal. The reason comes from the knowledge layer when it says what is not recorded,
    then from a date outside the records, then from the strongest expert's refusal.
 3. The layer, in the owner's order: schema, then ontology, then the knowledge layer. The planners vote at each step:
    the panel answers at the first layer that at least half of the valid plans reach (a plan at a lower layer counts
    for the higher layers too). Among the plans at that layer, the one whose result most other planners also reached
    wins; then the one with more answered parts; then the expert order.
 4. The layer of the answer: schema when one table answers with its columns as they are; ontology when it needs a join,
    arithmetic or a day count; knowledge when the knowledge layer has to say what is not recorded or which stand-in is used.

python3 moe.py PLANS_DIR QUESTIONS.json OUT_DIR   (PLANS_DIR holds plans-<expert>.json for each expert)"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import planner as P

EXPERTS = ["opus", "sonnet", "haiku"]
LAYER_RANK = {"schema": 0, "ontology": 1, "knowledge": 2}


def norm(rows):
    out = []
    for r in rows or []:
        out.append(tuple("" if v is None else (f"{round(float(v), 2):g}" if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)) for v in r))
    return out


def same(a, b):
    """Identical results: the same number of rows, and each row of the narrower result sits inside a row of the wider one."""
    if len(a) != len(b): return False
    if not a: return True
    small, big = (a, b) if len(a[0]) <= len(b[0]) else (b, a)
    left = list(big)
    for r in small:
        hit = next((x for x in left if all(v in x for v in r)), None)
        if hit is None: return False
        left.remove(hit)
    return True


def answered_parts(r):
    return [p for p in (r.get("parts") or [r]) if p.get("decision") == "answer"]


def layer_of(question, r):
    k = P.knowledge_notes(question)
    if k["not_recorded"] or k["stand_ins"]: return "knowledge"
    parts = answered_parts(r)
    if parts and all(p.get("declared_layer") == "knowledge" for p in parts): return "knowledge"
    return r.get("layer") or ("ontology" if any(p.get("layer") == "ontology" for p in parts) else "schema")


def refusal(question, results):
    hard, _ = P.R.registry_layer(question)
    if hard:
        why = "the knowledge layer says this is not recorded: " + "; ".join(hard)
    else:
        msgs = [results[e].get("message", "") for e in EXPERTS if e in results]
        outside = next((m for m in msgs if "outside the records" in m or "not from that year" in m), None)
        why = P.reason(outside or next((m for m in msgs if m), "no table or definition in the records answers it."))
    return dict(decision="no_record", layer="refused", expert=None, support=0, candidates=0, reply=P.PREFIX + why)


def panel(question, plans):
    """plans: expert -> plan (or None). Returns the panel's decision, the expert whose plan answered, and the reply."""
    results = {}
    for e in EXPERTS:
        pl = plans.get(e)
        if pl is None or (isinstance(pl, dict) and ("raw" in pl or not pl)):
            results[e] = dict(decision="no_plan", message=P.PREFIX + "no usable plan was returned.")
            continue
        try:
            results[e] = P.run_plan(question, pl)
        except Exception as ex:  # noqa: BLE001  fail closed
            results[e] = dict(decision="no_record", message=P.PREFIX + f"the plan could not be checked ({type(ex).__name__}).")
    cands = [e for e in EXPERTS if results[e]["decision"] == "answer"]
    if not cands:
        out = refusal(question, results)
        out["experts"] = {e: results[e].get("decision") for e in EXPERTS}
        return out, results
    sig = {e: [norm(p.get("rows")) for p in answered_parts(results[e])] for e in cands}
    support = {e: sum(1 for f in cands if f != e and any(same(x, y) for x in sig[e] for y in sig[f])) for e in cands}
    # the layer, in the owner's order: schema, then ontology, then the knowledge layer. The planners vote at each step:
    # the panel stops at the first layer that at least half of the valid plans reach (a plan at a lower layer counts for the higher ones too)
    lay_e = {e: layer_of(question, results[e]) for e in cands}
    lay = next(L for L in ("schema", "ontology", "knowledge") if 2 * sum(1 for e in cands if LAYER_RANK[lay_e[e]] <= LAYER_RANK[L]) >= len(cands))
    at = [e for e in cands if lay_e[e] == lay]
    votes = sum(1 for e in cands if LAYER_RANK[lay_e[e]] <= LAYER_RANK[lay])
    best = sorted(at, key=lambda e: (-support[e], -len(sig[e]), EXPERTS.index(e)))[0]
    r = results[best]; agree = support[best] + 1
    head = (f"Answered from the {lay} layer ({votes} of {len(cands)} valid plans reached it). "
            + (f"{agree} of 3 planners reached this result." if agree > 1 else "The planners' results differ; this is the plan ranked first at that layer."))
    # each part names the layer its figures came from; the head names the layer the whole answer needed
    reply = head + "\n" + re.sub(r"answered from the ([a-z/]+) layer\.", r"figures from the \1 layer.", re.sub(r"(?m)^answered from the ([a-z/]+) layer\.", r"Figures from the \1 layer.", P.render(question, r)))
    return dict(decision="answer", layer=lay, expert=best, support=agree, layer_votes=votes, candidates=len(cands), expert_layers=lay_e, experts={e: results[e].get("decision") for e in EXPERTS}, reply=reply), results


def load_plans(d):
    out = {}
    for e in EXPERTS:
        f = Path(d) / f"plans-{e}.json"
        out[e] = json.load(open(f)) if f.exists() else {}
    return out


if __name__ == "__main__":
    plans_dir, qfile, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3]); out_dir.mkdir(parents=True, exist_ok=True)
    plans = load_plans(plans_dir); qs = json.load(open(qfile)); rows = []; md = ["# Store 014 benchmark: the planning panel's answers\n"]
    for x in qs:
        res, _ = panel(x["question"], {e: plans[e].get(x["id"]) for e in EXPERTS})
        rows.append(dict(id=x["id"], question=x["question"], **{k: v for k, v in res.items()}))
        md.append(f"## {x['id']}: {x['question']}\n\n{res['reply']}\n")
    json.dump(rows, open(out_dir / "panel-results.json", "w"), indent=1, default=str, ensure_ascii=False)
    (out_dir / "panel-answers.md").write_text("\n".join(md))
    from collections import Counter
    print(Counter((r["decision"], r["layer"]) for r in rows)); print("support:", Counter(r["support"] for r in rows if r["decision"] == "answer"))
