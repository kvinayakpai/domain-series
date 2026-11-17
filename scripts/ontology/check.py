"""Checks the Store 014 ontology with open-source tools and writes it in more formats.

Run after `node scripts/ontology/build.mjs`, then run `node scripts/ontology/check.mjs`:

    pip install rdflib pyshacl owlrl owlready2 pyoxigraph pylode
    python3 scripts/ontology/check.py

It reads public/data/ontology/store-014.ttl (OWL), store-014-shapes.ttl (SHACL) and store-014-june.ttl
(a small knowledge graph of June), and
  - writes the ontology as JSON-LD, RDF/XML and N-Triples with rdflib, and reads each one back;
  - validates the June graph against the shapes with pySHACL and writes the report;
  - runs the OWL 2 RL rules (owlrl) and the HermiT reasoner (Java, bundled with Owlready2);
  - asks three SPARQL questions of Oxigraph (Rust);
  - writes the ontology's documentation page with pyLODE;
and records what each tool said in src/data/ontology-check.json, which the post and its tests read.
"""
import importlib.metadata as md
import json
import os
import pathlib
import sys
import tempfile

# rdflib writes RDF/XML in set order, which follows Python's hash seed. Fix the seed, so the files only
# change when the ontology does.
if os.environ.get('PYTHONHASHSEED') != '0':
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable, *sys.argv])

import owlready2
import owlrl
import pyoxigraph as ox
import pyshacl
import rdflib
from rdflib import RDF, Namespace
from rdflib.compare import isomorphic, to_canonical_graph

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / 'public' / 'data' / 'ontology'
OUT = ROOT / 'src' / 'data' / 'ontology-check.json'
NS = 'https://kvinayakpai.github.io/domain-series/ontology/store-014#'
S14 = Namespace(NS)
SH = Namespace('http://www.w3.org/ns/shacl#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')

ont = rdflib.Graph().parse(D / 'store-014.ttl')
june = rdflib.Graph().parse(D / 'store-014-june.ttl')
shapes = rdflib.Graph().parse(D / 'store-014-shapes.ttl')
local = lambda u: str(u).split('#')[-1]
result = {'tools': {p: md.version(p) for p in ['rdflib', 'pyshacl', 'owlrl', 'owlready2', 'pyoxigraph', 'pylode']}}

# ---------- the counts ----------
things = json.loads((ROOT / 'src' / 'data' / 'ontology.json').read_text())['things']
classes = {local(c) for c in ont.subjects(RDF.type, OWL.Class) if str(c).startswith(NS)}
result['triples'] = {'ontology': len(ont), 'june': len(june), 'shapes': len(shapes)}
result['counts'] = {
    'things': len(things),
    'classes': len(classes),
    'object_properties': len({p for p in ont.subjects(RDF.type, OWL.ObjectProperty) if str(p).startswith(NS)}),
    'datatype_properties': len({p for p in ont.subjects(RDF.type, OWL.DatatypeProperty) if str(p).startswith(NS)}),
    'rules': len(set(ont.subjects(RDF.type, S14.Rule))),
    'records': len(set(ont.subjects(RDF.type, S14.Record))),
    'shapes': len(set(shapes.subjects(RDF.type, SH.NodeShape))),
}

# ---------- one ontology, more formats (rdflib) ----------
context = {'s14': NS, 'owl': str(OWL), 'rdfs': 'http://www.w3.org/2000/01/rdf-schema#', 'xsd': 'http://www.w3.org/2001/XMLSchema#',
           'skos': 'http://www.w3.org/2004/02/skos/core#', 'prov': 'http://www.w3.org/ns/prov#', 'dcterms': 'http://purl.org/dc/terms/'}
formats = {'json-ld': 'store-014.jsonld', 'xml': 'store-014.rdf', 'nt': 'store-014.nt'}
# Canonical blank-node labels and a fixed order, so the files only change when the ontology does.
canon = rdflib.Graph()
for t in sorted(to_canonical_graph(ont)):
    canon.add(t)
for prefix, ns in context.items():
    canon.bind(prefix, ns)
jsonld = json.loads(canon.serialize(format='json-ld', context=context))
jsonld['@graph'] = sorted(jsonld['@graph'], key=lambda n: n.get('@id', ''))
(D / formats['json-ld']).write_text(json.dumps(jsonld, indent=2, sort_keys=True, ensure_ascii=False) + '\n')
(D / formats['xml']).write_text(canon.serialize(format='xml'))
(D / formats['nt']).write_text(''.join(sorted(canon.serialize(format='nt').splitlines(keepends=True))))
result['formats'] = {}
for fmt, f in formats.items():
    back = rdflib.Graph().parse(D / f, format=fmt)
    result['formats'][f] = {'bytes': (D / f).stat().st_size, 'triples': len(back), 'same_graph': isomorphic(back, ont)}
result['formats']['store-014.ttl'] = {'bytes': (D / 'store-014.ttl').stat().st_size, 'triples': len(ont), 'same_graph': True}

# ---------- SHACL (pySHACL) ----------
data = june + ont
conforms, report, _ = pyshacl.validate(data, shacl_graph=shapes, inference='none')
violations = []
for r in report.subjects(RDF.type, SH.ValidationResult):
    source = report.value(r, SH.sourceShape)
    node_shape = source if (source, RDF.type, SH.NodeShape) in shapes else next(shapes.subjects(SH.property, source))
    message = str(report.value(r, SH.resultMessage))
    violations.append({'focus': local(report.value(r, SH.focusNode)), 'shape': local(node_shape),
                       'rule': int(message.split(':')[0].replace('Rule ', '')), 'message': message})
violations.sort(key=lambda v: (v['rule'], v['focus']))
stable_report = rdflib.Graph()
for t in sorted(to_canonical_graph(report)):
    stable_report.add(t)
stable_report.bind('sh', SH)
stable_report.bind('s14', S14)
stable_report.bind('june', 'https://kvinayakpai.github.io/domain-series/ontology/store-014/june#')
(D / 'store-014-june-report.ttl').write_text(stable_report.serialize(format='turtle'))
result['shacl'] = {'python': {'conforms': conforms, 'count': len(violations), 'violations': violations}}

# ---------- OWL 2 RL rules (owlrl) ----------
closure = rdflib.Graph()
for t in data:
    closure.add(t)
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(closure)
debit = rdflib.URIRef('https://kvinayakpai.github.io/domain-series/ontology/store-014/june#debit-617118013344')
refund = rdflib.URIRef('https://kvinayakpai.github.io/domain-series/ontology/store-014/june#refund-B260620-110056')
result['owlrl'] = {
    'triples_after': len(closure),
    'inferred': len(closure) - len(data),
    'debit_returned_by_refund': (debit, S14.returnedBy, refund) in closure and (debit, S14.returnedBy, refund) not in data,
}

# ---------- HermiT (Java), through Owlready2 ----------
with tempfile.TemporaryDirectory() as tmp:
    f = pathlib.Path(tmp) / 'store-014-and-june.owl'
    f.write_text(data.serialize(format='xml'))
    world = owlready2.World()
    onto = world.get_ontology(f.as_uri()).load()
    try:
        with onto:
            owlready2.sync_reasoner_hermit(world, infer_property_values=False, debug=0)
        consistent = True
    except owlready2.OwlReadyInconsistentOntologyError:
        consistent = False
    # And a check that HermiT is really reasoning: one thing that is both a sale and a lost sale.
    bad = rdflib.Graph()
    for t in data:
        bad.add(t)
    both = rdflib.URIRef('urn:example:both')
    bad.add((both, RDF.type, S14.Sale))
    bad.add((both, RDF.type, S14.LostSale))
    g = pathlib.Path(tmp) / 'contradiction.owl'
    g.write_text(bad.serialize(format='xml'))
    world2 = owlready2.World()
    onto2 = world2.get_ontology(g.as_uri()).load()
    try:
        with onto2:
            owlready2.sync_reasoner_hermit(world2, infer_property_values=False, debug=0)
        caught = False
    except owlready2.OwlReadyInconsistentOntologyError:
        caught = True
    result['hermit'] = {'consistent': consistent, 'classes_loaded': len(list(onto.classes())), 'catches_sale_and_lost_sale': caught}

# ---------- SPARQL (Oxigraph) ----------
store = ox.Store()
store.load((D / 'store-014.ttl').read_bytes(), format=ox.RdfFormat.TURTLE)
store.load((D / 'store-014-june.ttl').read_bytes(), format=ox.RdfFormat.TURTLE)
PREFIX = f'PREFIX s14: <{NS}>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
QUERIES = {
    'book_but_empty': """# Rule 2: the books say in stock, a shelf check saw none.
SELECT ?item ?book ?seen ?checked WHERE {
  ?b a s14:Stock ; s14:basis s14:Believed ; s14:ofItem ?i ; s14:quantity ?book .
  ?s a s14:Stock ; s14:basis s14:Seen ; s14:ofItem ?i ; s14:quantity ?seen ; s14:at ?checked .
  ?i rdfs:label ?item .
  FILTER (?book > 0 && ?seen = 0)
}""",
    'debit_without_approval': """# Rule 10: debits with no approved payment.
SELECT ?rrn ?amount ?bill WHERE {
  ?d a s14:Debit ; s14:fromAttempt ?a ; s14:amountInr ?amount .
  OPTIONAL { ?d s14:rrn ?rrn }
  ?a s14:forBill/s14:billId ?bill .
  FILTER NOT EXISTS { ?a s14:tillStatus s14:Approved }
}""",
    'refund_clock': """# Rule 11: start the refund clock at the debit.
SELECT ?bill (?refunded - ?debited AS ?fromDebit) (?refunded - ?complained AS ?fromComplaint) WHERE {
  ?refund a s14:Refund ; s14:answers ?debit ; s14:at ?refunded .
  ?debit s14:at ?debited ; s14:fromAttempt/s14:forBill/s14:billId ?bill .
  ?complaint s14:asksFor ?refund ; s14:at ?complained .
}""",
}
result['sparql'] = {}
for name, q in QUERIES.items():
    rows = []
    solutions = store.query(PREFIX + q)
    names = [v.value for v in solutions.variables]
    for sol in solutions:
        rows.append({n: sol[n].value for n in names if sol[n] is not None})
    result['sparql'][name] = {'query': q, 'rows': rows}
(D / 'store-014-queries.rq').write_text('\n\n'.join(PREFIX + q for q in QUERIES.values()) + '\n')

# ---------- documentation (pyLODE) ----------
from pylode import OntPub  # noqa: E402

OntPub(ontology=str(D / 'store-014.ttl')).make_html(destination=str(D / 'store-014.html'))
result['pylode'] = {'page': 'store-014.html', 'bytes': (D / 'store-014.html').stat().st_size}

# Keep the JavaScript side's results, if check.mjs has run before.
if OUT.exists():
    old = json.loads(OUT.read_text())
    if 'javascript' in old.get('shacl', {}):
        result['shacl']['javascript'] = old['shacl']['javascript']
        result['tools'].update({k: v for k, v in old['tools'].items() if k not in result['tools']})
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: result[k] for k in ['counts', 'triples', 'owlrl', 'hermit']}, indent=1))
print('violations', result['shacl']['python']['count'])
for name, q in result['sparql'].items():
    print(name, q['rows'])
