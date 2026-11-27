"""Build public/data/ontology/store-014-data.ttl, the data-bound layer of the Store 014 ontology, from spec.py and the CSV files.
Every claim is read from or checked against the data: columns exist, every code value in the file is listed (and nothing else),
coverage dates come from the date columns. Run with PYTHONHASHSEED=0 (the script re-executes itself) so output is identical each time.

    python3 refusal-bench/ontology/build_bindings.py
"""
import os
import sys

if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import csv
import re
from pathlib import Path

from rdflib import RDF, RDFS, SKOS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "public" / "data" / "india-grocery"
OUT = ROOT / "public" / "data" / "ontology" / "store-014-data.ttl"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "refusal-bench" / "guards"))
import spec  # noqa: E402
import registry  # noqa: E402

S14 = Namespace("https://kvinayakpai.github.io/domain-series/ontology/store-014#")
D = Namespace("https://kvinayakpai.github.io/domain-series/ontology/store-014-data#")
g = Graph()
for p, ns in (("s14", S14), ("d", D), ("skos", SKOS), ("owl", OWL), ("rdfs", RDFS), ("xsd", XSD)):
    g.bind(p, ns)

ontology = URIRef(str(D).rstrip("#"))
g.add((ontology, RDF.type, OWL.Ontology))
g.add((ontology, OWL.imports, URIRef(str(S14).rstrip("#"))))
g.add((ontology, RDFS.comment, Literal("Data-bound layer of the Store 014 ontology: which table and column each concept lives in, the code lists, measures, "
                                          "synonyms, derived flags and the things the records cannot define. Built from the CSV files by refusal-bench/ontology/build_bindings.py.")))
for c, comment in (("Table", "A CSV file of Store 014 records."), ("Column", "A column of a table."), ("CodeValue", "One value of a code column; it is the only value the column holds."),
                   ("Measure", "A numeric column a question can total, average or rank."), ("Product", "One of the 11 products."),
                   ("Flag", "A derived yes/no condition on a table's row, defined in SQL."), ("UnrecordedConcept", "A business term no record defines: a question that needs it has no answer in the records."),
                   ("StandIn", "A term for which only a stand-in is recorded: answer as a labelled proxy or not at all."), ("Window", "The dates a table covers.")):
    g.add((D[c], RDF.type, OWL.Class)); g.add((D[c], RDFS.label, Literal(c))); g.add((D[c], RDFS.comment, Literal(comment)))
g.add((D.StandIn, RDFS.subClassOf, D.UnrecordedConcept))
for a, b in ((D.Table, D.Column), (D.Table, D.CodeValue), (D.Column, D.CodeValue), (D.Table, D.UnrecordedConcept)):
    g.add((a, OWL.disjointWith, b))
for p in ("sourceFile", "columnName", "kind", "unit", "grain", "recordKind", "keyColumn", "dateColumn", "status", "gap", "pattern", "cueSet", "sql", "idPattern", "value", "windowKind"):
    g.add((D[p], RDF.type, OWL.DatatypeProperty))
for p in ("defaultMeasure", "inTable", "ofColumn", "skuColumn", "lookedAtBy", "governedBy", "forTable"):
    g.add((D[p], RDF.type, OWL.ObjectProperty))
g.add((D.additive, RDF.type, OWL.DatatypeProperty)); g.add((D.additive, RDFS.range, XSD.boolean))
g.add((D.inTable, RDFS.domain, D.Column)); g.add((D.inTable, RDFS.range, D.Table))
g.add((D.ofColumn, RDFS.domain, D.CodeValue)); g.add((D.ofColumn, RDFS.range, D.Column))
g.add((D.coverageStart, RDF.type, OWL.DatatypeProperty)); g.add((D.coverageEnd, RDF.type, OWL.DatatypeProperty))


def rows(stem):
    return list(csv.DictReader(open(DATA / f"{stem}.csv")))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def cue(node, tokens):
    g.add((node, D.cueSet, Literal(" ".join(tokens))))


problems = []
product_rows = rows("products")
for stem, t in spec.T.items():
    data = rows(stem)
    header = list(data[0])
    tn = D["table_" + slug(stem)]
    g.add((tn, RDF.type, D.Table)); g.add((tn, RDFS.label, Literal(t["label"])))
    g.add((tn, D.sourceFile, Literal(stem + ".csv"))); g.add((tn, D.grain, Literal(t["grain"]))); g.add((tn, D.recordKind, Literal(t["kind"])))
    g.add((tn, D.windowKind, Literal(t["window"])))
    for toks in t["nouns"]:
        cue(tn, toks)
    if t["key"]:
        g.add((tn, D.keyColumn, Literal(t["key"])))
    if t["record"]:
        g.add((tn, D.lookedAtBy, S14["record-" + t["record"]]))
    if set(header) != set(t["columns"]):
        problems.append(f"{stem}: spec columns {sorted(set(t['columns']) ^ set(header))} differ from the file header")
    # coverage from the data
    if t["date"]:
        days = sorted(r[t["date"]][:10] for r in data if r[t["date"]])
        g.add((tn, D.dateColumn, Literal(t["date"]))); g.add((tn, D.coverageStart, Literal(days[0] + "T00:00:00", datatype=XSD.dateTime))); g.add((tn, D.coverageEnd, Literal(days[-1] + "T00:00:00", datatype=XSD.dateTime)))
    elif t["window"] == "june":
        g.add((tn, D.coverageStart, Literal("2026-06-01T00:00:00", datatype=XSD.dateTime))); g.add((tn, D.coverageEnd, Literal("2026-06-30T00:00:00", datatype=XSD.dateTime)))
    for c, cs in t["columns"].items():
        cn = D["col_" + slug(stem) + "__" + c]
        g.add((cn, RDF.type, D.Column)); g.add((cn, D.inTable, tn)); g.add((cn, D.columnName, Literal(c))); g.add((cn, D.kind, Literal(cs["kind"])))
        g.add((cn, RDFS.label, Literal(c.replace("_", " "))))
        if c in spec.ID_PATTERNS:
            g.add((cn, D.idPattern, Literal(spec.ID_PATTERNS[c])))
        if cs["kind"] == "number":
            for r in data:
                if r[c] == "":
                    continue          # an empty cell means 'not recorded for this row'; SQL aggregates skip it
                try:
                    float(r[c])
                except ValueError:
                    problems.append(f"{stem}.{c}: non-numeric value {r[c]!r}"); break
            g.add((cn, D.unit, Literal(cs["unit"]))); g.add((cn, D.additive, Literal(cs["additive"])))
            g.add((cn, RDF.type, D.Measure))
            for toks in cs.get("cues", []):
                cue(cn, toks)
        if cs["kind"] == "code":
            vals = sorted({r[c] for r in data})
            for v in vals:
                vn = D["val_" + slug(stem) + "__" + c + "__" + slug(v)]
                g.add((vn, RDF.type, D.CodeValue)); g.add((vn, D.ofColumn, cn)); g.add((vn, D.value, Literal(v))); g.add((vn, RDFS.label, Literal(v)))
                for alt in [v.lower()] + spec.VALUE_ALT.get((stem, c, v), []):
                    g.add((vn, SKOS.altLabel, Literal(alt.lower())))
            for key in spec.VALUE_ALT:
                if key[0] == stem and key[1] == c and key[2] not in vals:
                    problems.append(f"synonym for value not in the data: {key}")
        if t["sku"] == c:
            g.add((tn, D.skuColumn, cn))
    if t["default"]:
        g.add((tn, D.defaultMeasure, D["col_" + slug(stem) + "__" + t["default"]]))
    if t["distinct"]:
        dn = D["distinct_" + slug(stem)]
        g.add((dn, RDF.type, D.Measure)); g.add((dn, RDFS.label, Literal("distinct " + t["distinct"]["label"]))); g.add((dn, D.forTable, tn))
        g.add((dn, D.columnName, Literal(t["distinct"]["column"])))
        for toks in t["distinct"]["nouns"]:
            cue(dn, toks)

# the bill: a distinct bill_id on the till lines
bn = D.bill
g.add((bn, RDF.type, D.Measure)); g.add((bn, RDFS.label, Literal("bill"))); g.add((bn, D.forTable, D["table_" + slug(spec.BILL["table"])]))
g.add((bn, D.columnName, Literal(spec.BILL["column"])))
for toks in spec.BILL["nouns"]:
    cue(bn, toks)

# products: cue sets from the name, plus the pack where the name alone is shared
FILLER = {"whole", "wheat", "pouch", "kg", "l", "g", "ml", "sona", "masoori"}
words = {r["sku"]: [w for w in re.findall(r"[a-z]+", r["name"].lower()) if w not in FILLER] for r in product_rows}
for r in product_rows:
    pn = D["product_" + slug(r["sku"])]
    g.add((pn, RDF.type, D.Product)); g.add((pn, RDFS.label, Literal(r["name"]))); g.add((pn, D.value, Literal(r["sku"])))
    ws = words[r["sku"]]
    pack = re.sub(r"\s", "", r["pack"].lower())
    shared = sum(1 for o in product_rows if set(words[o["sku"]]) <= set(ws) or set(ws) <= set(words[o["sku"]])) > 1
    cue(pn, ws + ([pack] if shared else []))
    g.add((pn, SKOS.altLabel, Literal(r["name"].lower())))

# derived flags: definitions in SQL, with the cue words that call them
FLAGS = [
    ("on_time_arrival", "shipments-june", "arrived on or before the end of its slot", "arrived_ts <= slot_end", [["arrived", "on", "or", "before", "the", "end", "of", "their", "slot"], ["arrived", "on", "time"]]),
    ("late_arrival", "shipments-june", "arrived after the end of its slot", "arrived_ts > slot_end", [["arrived", "late"], ["arrived", "after", "the", "end", "of", "their", "slot"]]),
    ("count_difference", "stock-counts-june", "the count differs from the book", "cast(adjustment as real) != 0", [["found", "a", "difference"], ["difference", "between", "book", "and", "counted"]]),
]
for fid, stem, label, sql, cues in FLAGS:
    fn = D["flag_" + fid]
    g.add((fn, RDF.type, D.Flag)); g.add((fn, RDFS.label, Literal(label))); g.add((fn, D.forTable, D["table_" + slug(stem)])); g.add((fn, D.sql, Literal(sql)))
    for toks in cues:
        cue(fn, toks)

# what the records cannot define: the registry's terms, one source of truth
RULES = {"cause": "rule-5", "absent_event": "rule-3", "forecast_vs_demand": "rule-4", "bank_side": "rule-9", "restock_times": "rule-1"}
for term in registry.TERMS:
    un = D["unrecorded_" + term["id"]]
    g.add((un, RDF.type, D.StandIn if term["status"] == "proxy" else D.UnrecordedConcept))
    g.add((un, RDFS.label, Literal(term["id"].replace("_", " ")))); g.add((un, RDFS.comment, Literal(term["note"])))
    g.add((un, D.gap, Literal(term["gap"]))); g.add((un, D.status, Literal(term["status"])))
    for pat in term["patterns"]:
        g.add((un, D.pattern, Literal(pat)))
    if term["id"] in RULES:
        g.add((un, D.governedBy, S14[RULES[term["id"]]]))

# vocabulary used to tell glue words from content words
for w in sorted(set(spec.GLUE)):
    g.add((D["glue_" + slug(w)], RDF.type, SKOS.Concept)); g.add((D["glue_" + slug(w)], SKOS.prefLabel, Literal(w)))

if problems:
    print("PROBLEMS:"); [print(" ", p) for p in problems]; sys.exit(1)
g.serialize(OUT, format="turtle")
print(f"wrote {OUT.relative_to(ROOT)}: {len(g)} triples; tables {len(spec.T)}, columns {sum(len(t['columns']) for t in spec.T.values())}")
