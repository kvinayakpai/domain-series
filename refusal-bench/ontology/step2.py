"""Step 2 of the benchmark: a model plans ONE question at the layer the panel assigned; code refuses any plan that goes beyond it.
LAYER_NOTES is the text every model is given (NVIDIA models and Haiku alike). run_at() is the code check."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P

RANK = {"schema": 0, "ontology": 1, "knowledge": 2}

LAYER_NOTES = {
    "schema": 'LAYER FOR THIS QUESTION: SCHEMA. The panel decided one table answers it with its columns as they are. Plan it from ONE table only: no joins, no arithmetic between columns, no days_between. Set "layer": "schema". Do not use another layer. If one table cannot answer it, reply {"cannot": "<what is missing>"}.',
    "ontology": 'LAYER FOR THIS QUESTION: ONTOLOGY. The panel decided no single table answers it, but joins or a definition from the ontology do. Plan it with joins, arithmetic or the definitions below; set "layer": "ontology". Do not use the knowledge layer. If joins and definitions cannot answer it, reply {"cannot": "<what is missing>"}.',
    "knowledge": 'LAYER FOR THIS QUESTION: KNOWLEDGE. The panel decided the records alone cannot answer it (something is not recorded, or only a stand-in exists). Plan only the recorded evidence or a labelled stand-in, set "layer": "knowledge", and say in "covers" what is not recorded. If nothing in the records helps, reply {"cannot": "<what is missing>"}.',
}


def run_at(question, plan, layer):
    """Check and run a plan, then refuse it if it uses more than the assigned layer allows (knowledge allows everything)."""
    r = P.run_plan(question, plan)
    if r.get("decision") != "answer" or layer == "knowledge": return r
    used = r.get("layer") or "schema"
    if RANK.get(used, 0) > RANK[layer]:
        return dict(decision="no_record", layers=[used], failed_layer=used, message=P.PREFIX + f"the plan needs the {used} layer, beyond the {layer} layer this question was assigned.", trace=[], beyond_layer=True)
    return r
