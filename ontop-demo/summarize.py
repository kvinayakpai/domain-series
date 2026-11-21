"""Count what Ontop's bootstrap made from Store 014's tables, and look for the two things no table holds.

    python3 ontop-demo/summarize.py <ontology.owl> <mapping.obda> > summary.json
"""
import json
import re
import sys
from pathlib import Path

from rdflib import Graph, RDF, OWL, RDFS


def local(iri: str) -> str:
    return re.split(r"[#/]", str(iri).rstrip("/"))[-1]


g = Graph()
g.parse(sys.argv[1])
classes = sorted(local(c) for c in g.subjects(RDF.type, OWL.Class))
obj = sorted(local(p) for p in g.subjects(RDF.type, OWL.ObjectProperty))
data = sorted(local(p) for p in g.subjects(RDF.type, OWL.DatatypeProperty))
sub = sorted(f"{local(a)} < {local(b)}" for a, b in g.subject_objects(RDFS.subClassOf))
mapping = Path(sys.argv[2]).read_text(errors="replace")
words = ("demand", "lost", "walk", "left")
names = classes + obj + data
print(json.dumps({
    "classes": len(classes),
    "object_properties": len(obj),
    "datatype_properties": len(data),
    "subclass_axioms": len(sub),
    "class_names": classes,
    "object_property_names": obj,
    "names_mentioning_demand_or_lost_sale": [n for n in names if any(w in n.lower() for w in words)],
    "mapping_assertions": len(re.findall(r"^mappingId", mapping, flags=re.M)),
}, indent=2))
