"""Check the data-bound ontology layer three ways, then prove the checks can fail.
  1. pySHACL: the bindings against store-014-data-shapes.ttl (with the base ontology merged in, OWL-RL inference on)
  2. HermiT through Owlready2: the merged ontology is consistent
  3. the data: every column and code value in the bindings exists in the CSV files, and every code value in the files is bound
  4. planted faults: a column in no table, a flag on a missing table, and a bill that is also a table are each caught
"""
import csv
import os
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import RDF, Graph, Literal, Namespace
from rdflib.namespace import OWL

ONT = Path(__file__).resolve().parents[2] / "public" / "data" / "ontology"
DATA = Path(__file__).resolve().parents[2] / "public" / "data" / "india-grocery"
D = Namespace("https://kvinayakpai.github.io/domain-series/ontology/store-014-data#")

base = Graph().parse(ONT / "store-014.ttl")
data = Graph().parse(ONT / "store-014-data.ttl")
shapes = Graph().parse(ONT / "store-014-data-shapes.ttl")
merged = base + data
merged.remove((None, OWL.imports, None))      # the base is already merged in; stop the reasoner fetching it from the web
ok = True


def shacl(g):
    return validate(g, shacl_graph=shapes, inference="rdfs", advanced=False)


conforms, _, text = shacl(merged)
print("1. SHACL:", "conforms" if conforms else "VIOLATIONS\n" + text); ok &= conforms

# 2. reasoner
import owlready2  # noqa: E402
owlready2.JAVA_EXE = "java"
tmp = Path("/tmp/store-014-merged.owl"); merged.serialize(tmp, format="xml")
onto = owlready2.get_ontology(f"file://{tmp}").load()
try:
    with onto:
        owlready2.sync_reasoner_hermit(infer_property_values=False, debug=0)
    inc = list(owlready2.default_world.inconsistent_classes())
    print("2. HermiT: consistent" if not inc else f"2. HermiT: inconsistent classes {inc}"); ok &= not inc
except Exception as e:  # noqa: BLE001
    print("2. HermiT failed to run:", str(e)[:200]); ok = False

# 3. data
bad = []
for t in data.subjects(RDF.type, D.Table):
    stem = str(data.value(t, D.sourceFile))[:-4]
    header = list(csv.DictReader(open(DATA / f"{stem}.csv")).fieldnames)
    cols = {str(data.value(c, D.columnName)) for c in data.subjects(D.inTable, t)}
    if cols != set(header):
        bad.append(f"{stem}: bound columns differ from the file header: {sorted(cols ^ set(header))}")
    for c in data.subjects(D.inTable, t):
        if str(data.value(c, D.kind)) == "code":
            name = str(data.value(c, D.columnName))
            bound = {str(data.value(v, D.value)) for v in data.subjects(D.ofColumn, c)}
            actual = {r[name] for r in csv.DictReader(open(DATA / f"{stem}.csv"))}
            if bound != actual:
                bad.append(f"{stem}.{name}: code list differs from the data: {sorted(bound ^ actual)}")
print("3. data:", "every bound column and code value matches the CSV files" if not bad else "\n".join(bad)); ok &= not bad

# 4. the checks can fail
faults = {
    "column in no table": lambda g: g.add((D.col_orphan, RDF.type, D.Column)),
    "flag without a table": lambda g: (g.add((D.flag_x, RDF.type, D.Flag)), g.add((D.flag_x, D.sql, Literal("1=1")))),
    "unrecorded term with an invalid gap kind": lambda g: (g.add((D.u_x, RDF.type, D.UnrecordedConcept)), g.add((D.u_x, D.gap, Literal("whenever")))),
    "a table that is also a column (disjoint)": lambda g: (g.add((D.table_products, RDF.type, D.Column))),
}
for name, plant in faults.items():
    g2 = Graph(); [g2.add(t) for t in merged]
    plant(g2)
    c2, _, _ = shacl(g2)
    caught = not c2
    if name.startswith("a table that is also"):
        t2 = Path("/tmp/planted.owl"); g2.serialize(t2, format="xml")
        w = owlready2.World(); o2 = w.get_ontology(f"file://{t2}").load()
        try:
            with o2:
                owlready2.sync_reasoner_hermit(w, infer_property_values=False, debug=0)
            caught = bool(list(w.inconsistent_classes())) or bool(list(w.individuals_inconsistent())) if hasattr(w, "individuals_inconsistent") else bool(list(w.inconsistent_classes()))
        except owlready2.OwlReadyInconsistentOntologyError:
            caught = True
    print(f"4. planted fault '{name}':", "caught" if caught else "NOT CAUGHT"); ok &= caught
print("ALL CHECKS PASS" if ok else "CHECKS FAILED"); sys.exit(0 if ok else 1)
