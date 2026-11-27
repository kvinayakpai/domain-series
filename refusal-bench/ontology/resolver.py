"""Layered question resolver for Store 014. No model anywhere: the same question gives the same answer, byte for byte.

    answer(question) -> {"decision": "answer" | "no_record" | "proxy", "value", "sql", "params", "trace", "layers", "message"}

Order of checks, as asked for:
  1 SCHEMA    the words of the question are matched to tables, columns and code values that exist in the CSV files
  2 ONTOLOGY  every word must be defined: a noun, a measure, a code value, a derived flag, a product, or a glue word.
              The measure must make sense (no summing of prices); a filter must belong to the table it is applied to.
  3 REGISTRY  the knowledge layer: what the records cannot define (who, why, what did not happen, outside the store), stand-ins
              (proxies), and the dates the records cover
  4 COMPILE   SQL is written by this code from the ontology bindings and run on the CSV files loaded into SQLite
If any check fails the answer is "no record" (or a labelled stand-in) naming the layer and the reason. Nothing is guessed.
When two readings of a question both compile, they must give the same number; otherwise the question is refused as ambiguous.
"""
import csv
import re
import sqlite3
import sys
from pathlib import Path

from rdflib import RDF, RDFS, SKOS, Graph, Namespace

ROOT = Path(__file__).resolve().parents[2]
ONT = ROOT / "public" / "data" / "ontology"
DATA = ROOT / "public" / "data" / "india-grocery"
sys.path.insert(0, str(ROOT / "refusal-bench" / "guards"))
D = Namespace("https://kvinayakpai.github.io/domain-series/ontology/store-014-data#")
S14 = Namespace("https://kvinayakpai.github.io/domain-series/ontology/store-014#")

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
AGG_CUES = {  # token sets, checked on stemmed tokens
    "count": [["how", "many"], ["number", "of"], ["count"]],
    "much": [["how", "much"]],
    "sum": [["total"], ["sum"], ["altogether"]],
    "avg": [["average"], ["mean"]],
    "max": [["highest"], ["largest"], ["biggest"], ["maximum"], ["peak"]],
    "min": [["lowest"], ["smallest"], ["minimum"]],
}
DISTINCT = {"distinct", "different", "unique"}
COMPARATORS = [(r"(?:more than|greater than|above|over)\s+(\d+(?:\.\d+)?)", ">"), (r"(?:less than|fewer than|below|under)\s+(\d+(?:\.\d+)?)", "<"),
               (r"at least\s+(\d+(?:\.\d+)?)", ">="), (r"at most\s+(\d+(?:\.\d+)?)", "<=")]


def stem(t):
    t = t.replace("’", "'")
    if t.endswith("'s"):
        t = t[:-2]
    t = t.rstrip("'")
    if t.endswith("ed") and len(t) > 5 and not t.endswith("eed"):
        return t[:-2]
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("s") and not t.endswith("ss") and len(t) > 3:
        return t[:-1]
    return t


def tokenize(text):
    text = text.lower().replace("’", "'")
    text = re.sub(r"(\d)\s+(kg|ml|g|l)\b", r"\1\2", text)
    return re.findall(r"\d{1,2}:\d{2}|[a-z0-9]+(?:[-'][a-z0-9]+)*", text)


# ---------------------------------------------------------------- load the ontology once
class Onto:
    def __init__(self):
        g = Graph()
        g.parse(ONT / "store-014.ttl"); g.parse(ONT / "store-014-data.ttl")
        self.g = g
        L = lambda s, p: sorted(str(o) for o in g.objects(s, p))
        self.tables = {}
        for t in sorted(g.subjects(RDF.type, D.Table)):
            stemname = str(g.value(t, D.sourceFile))[:-4]
            cols = {}
            for c in sorted(g.subjects(D.inTable, t)):
                name = str(g.value(c, D.columnName))
                cols[name] = dict(iri=c, kind=str(g.value(c, D.kind)), unit=str(g.value(c, D.unit)) if g.value(c, D.unit) else None,
                                  additive=bool(g.value(c, D.additive).toPython()) if g.value(c, D.additive) is not None else None,
                                  cues=[x.split() for x in L(c, D.cueSet)], idpat=str(g.value(c, D.idPattern)) if g.value(c, D.idPattern) else None, values={})
                for v in g.subjects(D.ofColumn, c):
                    val = str(g.value(v, D.value))
                    for ph in sorted({str(x) for x in g.objects(v, SKOS.altLabel)} | {val.lower()}):
                        cols[name]["values"][ph] = val
            self.tables[stemname] = dict(iri=t, stem=stemname, label=str(g.value(t, RDFS.label)), grain=str(g.value(t, D.grain)), nouns=[x.split() for x in L(t, D.cueSet)],
                                         date=str(g.value(t, D.dateColumn)) if g.value(t, D.dateColumn) else None,
                                         start=str(g.value(t, D.coverageStart))[:10] if g.value(t, D.coverageStart) else None,
                                         end=str(g.value(t, D.coverageEnd))[:10] if g.value(t, D.coverageEnd) else None,
                                         window=str(g.value(t, D.windowKind)), sku=None, cols=cols, kind=str(g.value(t, D.recordKind)),
                                         key=str(g.value(t, D.keyColumn)) if g.value(t, D.keyColumn) else None)
            dm = g.value(t, D.defaultMeasure)
            self.tables[stemname]["default"] = str(g.value(dm, D.columnName)) if dm is not None else None
            sc = g.value(t, D.skuColumn)
            if sc is not None:
                self.tables[stemname]["sku"] = str(g.value(sc, D.columnName))
        by_iri = {v["iri"]: k for k, v in self.tables.items()}
        self.products = [(str(g.value(p, D.value)), [x.split() for x in L(p, D.cueSet)], str(g.value(p, RDFS.label))) for p in sorted(g.subjects(RDF.type, D.Product))]
        self.flags = [(str(f).split("#")[-1], by_iri[g.value(f, D.forTable)], str(g.value(f, D.sql)), [x.split() for x in L(f, D.cueSet)], str(g.value(f, RDFS.label)))
                      for f in sorted(g.subjects(RDF.type, D.Flag))]
        self.distincts = [(by_iri[g.value(m, D.forTable)], str(g.value(m, D.columnName)), [x.split() for x in L(m, D.cueSet)], str(g.value(m, RDFS.label)))
                          for m in sorted(g.subjects(D.forTable, None)) if (m, RDF.type, D.Measure) in g]
        self.unrecorded = [(str(u).split("unrecorded_")[-1], str(g.value(u, D.status)), str(g.value(u, D.gap)), str(g.value(u, RDFS.comment)), L(u, D.pattern),
                            [str(r).split("#")[-1] for r in g.objects(u, D.governedBy)]) for u in sorted(set(g.subjects(RDF.type, D.UnrecordedConcept)) | set(g.subjects(RDF.type, D.StandIn)))]
        self.packs = {r["sku"]: re.sub(r"\s", "", r["pack"].lower()) for r in csv.DictReader(open(DATA / "products.csv"))}
        self.glue = {stem(str(g.value(x, SKOS.prefLabel))) for x in g.subjects(RDF.type, SKOS.Concept)}


ONTO = None
_DB = None


def onto():
    global ONTO
    if ONTO is None:
        ONTO = Onto()
    return ONTO


def db():
    global _DB
    if _DB is None:
        _DB = sqlite3.connect(":memory:")
        for stem_, t in onto().tables.items():
            rows = list(csv.DictReader(open(DATA / f"{stem_}.csv")))
            cols = list(rows[0])
            _DB.execute(f'create table "{stem_}" ({", ".join(chr(34) + c + chr(34) + " " + ("real" if t["cols"][c]["kind"] == "number" else "text") for c in cols)})')
            _DB.executemany(f'insert into "{stem_}" values ({",".join("?" * len(cols))})',
                            [[(None if r[c] == "" and t["cols"][c]["kind"] == "number" else r[c]) for c in cols] for r in rows])
    return _DB


# ---------------------------------------------------------------- helpers
def has_cue(stoks, cue):
    return all(stem(c) in stoks for c in cue)


def find_phrase(toks, phrase_toks, used):
    """index list of a contiguous phrase in the stemmed tokens not already used, else None"""
    n = len(phrase_toks)
    for i in range(len(toks) - n + 1):
        if toks[i:i + n] == phrase_toks and not any(j in used for j in range(i, i + n)):
            return list(range(i, i + n))
    return None


def refusal(decision, layers, message, trace=None, **kw):
    return dict(decision=decision, layers=layers, message=message, trace=trace or [], **kw)


# ---------------------------------------------------------------- layer 3: the knowledge layer
def registry_layer(question):
    from guard import window_check
    ql = question.lower()
    hard, proxy, notes = [], [], []
    for tid, status, gap, comment, pats, rules in onto().unrecorded:
        if any(re.search(p, ql) for p in pats):
            (hard if status == "not_recorded" else proxy).append(f"{tid} ({gap}): {comment}" + (f" [{', '.join(rules)}]" if rules else ""))
    r, p = window_check(question)
    hard += r; proxy += p
    return hard, proxy


# ---------------------------------------------------------------- the parse of one reading of a question
def read_one(question, subject, toks, stoks):
    """Try to read the whole question as `subject` (table or a bill/distinct measure). Returns (plan, None) or (None, reason)."""
    O = onto()
    kind, tstem = subject[0], subject[1]
    T = O.tables[tstem]
    used, trace = set(), []
    # the subject's own words
    cues = subject[2] if kind != "table" else [c for c in T["nouns"] if has_cue(stoks, c)]
    trace.append(("schema" if kind == "table" else "ontology", f"subject: {T['label']}" if kind == "table" else f"subject: {subject[3]}", " ".join(cues[0]) if cues else ""))
    where, params = [], []
    # identifier literals (shipment SHP-260606)
    for i, t in enumerate(toks):
        for cname, c in T["cols"].items():
            if c["idpat"] and re.fullmatch(c["idpat"], t):
                where.append(f'"{cname}" = ?'); params.append(t.upper()); used.add(i); trace.append(("schema", f"{cname} = {t.upper()}", t))
    # code values of this table, longest phrase first
    phrases = sorted(((ph, cname, val) for cname, c in T["cols"].items() for ph, val in c["values"].items()), key=lambda x: (-len(x[0].split()), x[0], x[1]))
    for ph, cname, val in phrases:
        ptoks = [stem(w) for w in tokenize(ph)]
        idx = find_phrase(stoks, ptoks, used)
        if idx:
            where.append(f'"{cname}" = ?'); params.append(val); used.update(idx); trace.append(("schema", f"{cname} = '{val}'", ph))
    # products
    sku_hits = []
    for sku, cuesets, label in O.products:
        for cs in cuesets:
            if cs and has_cue(stoks, cs):
                sku_hits.append((len(cs), sku, label, cs))
    if sku_hits:
        best = max(h[0] for h in sku_hits)
        top = sorted({(h[1], h[2]) for h in sku_hits if h[0] == best})
        if len(top) > 1:
            return None, ("ontology", f"the product is not named uniquely: could be {', '.join(t[1] for t in top)}")
        sku, label = top[0]
        if T["stem"] == "products":
            where.append('"sku" = ?')
        elif T["sku"]:
            where.append(f'"{T["sku"]}" = ?')
        else:
            return None, ("schema", f"{T['label']} records have no product column, so a question about {label} cannot be answered from them")
        params.append(sku); trace.append(("ontology", f"product {sku}", label))
        for i, x in enumerate(stoks):
            if x == O.packs.get(sku):
                used.add(i)
        for cs in [c for h in sku_hits if h[0] == best for c in [h[3]]]:
            for w in cs:
                for i, x in enumerate(stoks):
                    if x == stem(w):
                        used.add(i)
    else:
        # a product family word with no full match (atta without a size, milk without a kind)
        fam = {}
        for sku, cuesets, label in O.products:
            for cs in cuesets:
                for w in cs:
                    fam.setdefault(stem(w), set()).add(label)
        for i, x in enumerate(stoks):
            if x in fam and len(fam[x]) > 1 and i not in used:
                return None, ("ontology", f"'{toks[i]}' names more than one product ({', '.join(sorted(fam[x]))}); say which")
    if not sku_hits and T["sku"] and re.search(r"\b(a|any) product\b", question.lower()):     # "a product" with no name: any product
        for i, x in enumerate(stoks):
            if x == "product":
                used.add(i)
    # derived flags
    for fid, ftab, sql, fcues, flabel in O.flags:
        for fc in fcues:
            if ftab == tstem and has_cue(stoks, fc):
                if f"({sql})" not in where:
                    where.append(f"({sql})"); trace.append(("ontology", f"flag {fid}: {flabel}", " ".join(fc)))
                for w in fc:
                    for i, x in enumerate(stoks):
                        if x == stem(w):
                            used.add(i)
    for c in cues:                       # the subject's own words, consumed after the code values so a value may share a word with a noun
        for w in c:
            for i, x in enumerate(stoks):
                if x == stem(w):
                    used.add(i)
    if "all" in stoks and "product" in stoks and not kind == "table_products":
        for i, x in enumerate(stoks):
            if x in ("all", "product"):
                used.add(i)
    for m_ in re.finditer(r"\bat least one\b", question.lower()):
        for i, x in enumerate(toks):
            if x in ("at", "least", "one"):
                used.add(i)
    # aggregate cue
    agg = None
    for a, cuesets in AGG_CUES.items():
        for cs in cuesets:
            if has_cue(stoks, cs):
                if a in ("count", "sum", "much") and agg in ("avg", "max", "min"):
                    continue
                agg = a if agg is None or a in ("avg", "max", "min") else agg
                for w in cs:
                    for i, x in enumerate(stoks):
                        if x == stem(w):
                            used.add(i)
    distinct = bool(DISTINCT & set(stoks))
    for i, x in enumerate(stoks):
        if x in DISTINCT:
            used.add(i)
    on_days = bool(re.search(r"\bon how many (?:different )?days\b", question.lower()))
    # time of day: "dispatched before 05:00"
    m = re.search(r"\b(before|after)\s+(\d{1,2}):(\d{2})\b", question.lower())
    if m:
        tcols = [c for c, cc in T["cols"].items() if cc["kind"] == "time" and stem(re.split(r"_", c)[0]) in stoks]
        if len(tcols) != 1:
            return None, ("ontology", "a time of day needs exactly one named timestamp column of this record kind (dispatched, arrived, received ...)")
        where.append(f"substr(\"{tcols[0]}\",12,5) {'<' if m.group(1) == 'before' else '>'} ?"); params.append("%02d:%s" % (int(m.group(2)), m.group(3)))
        trace.append(("schema", f"{tcols[0]} {m.group(1)} {m.group(2)}:{m.group(3)}", m.group(0)))
        for i, t in enumerate(toks):
            if t in (m.group(1), f"{m.group(2)}:{m.group(3)}") or t == f"{int(m.group(2)):02d}:{m.group(3)}":
                used.add(i)
    # measure: a numeric column of this table named by its cue words
    measure = None
    mcands = []
    for cname, c in T["cols"].items():
        if c["kind"] == "number":
            for cs in c["cues"]:
                if has_cue(stoks, cs):
                    mcands.append((len(cs), cname, cs))
    if not mcands and T.get("default") and agg in ("max", "min", "avg", "sum", "much") and kind == "table":
        measure = T["default"]; trace.append(("ontology", f"default measure of {T['label']}: {measure}", "(none named)"))
    if mcands:
        best = max(x[0] for x in mcands)
        names = sorted({x[1] for x in mcands if x[0] == best})
        if len(names) > 1:
            return None, ("ontology", f"more than one measure of {T['label']} fits ({', '.join(names)})")
        measure = names[0]
        for x in mcands:
            if x[1] == measure:
                for w in x[2]:
                    for i, s_ in enumerate(stoks):
                        if s_ == stem(w):
                            used.add(i)
    # numeric comparator (applies to the measure, or to a priced column named in the question)
    cmp_ = None
    for pat, op in COMPARATORS:
        cm = re.search(pat, question.lower())
        if cm:
            cmp_ = (op, float(cm.group(1)), cm.group(0))
            for t in re.findall(r"[a-z]+|\d+(?:\.\d+)?", cm.group(0)):
                for i, x in enumerate(toks):
                    if x == t:
                        used.add(i)
            break
    # date window
    q = question.lower()
    win = None
    rng = re.search(r"from (\d{1,2}) (" + "|".join(MONTHS) + r") to (\d{1,2}) (" + "|".join(MONTHS) + r")(?: 2026)?", q)
    if rng and T["date"]:
        d1 = "2026-%02d-%02d" % (MONTHS.index(rng.group(2)) + 1, int(rng.group(1)))
        d2 = "2026-%02d-%02d" % (MONTHS.index(rng.group(4)) + 1, int(rng.group(3)))
        if d1 < T["start"] or d2 > T["end"]:
            return None, ("registry", f"the records of {T['label']} cover {T['start']} to {T['end']}, not {d1} to {d2}")
        win = (d1, d2)
        where.append(f'substr("{T["date"]}",1,10) between ? and ?'); params += list(win); trace.append(("registry", f"window {d1} to {d2}", rng.group(0)))
        for i, x in enumerate(toks):
            if x in (rng.group(1), rng.group(3), rng.group(2), rng.group(4), "from", "to", "2026"):
                used.add(i)
    june = re.search(r"\b(?:in|for|during|of) june(?: 2026)?\b|\bjune 2026\b", q)
    if not win and june:
        if T["date"]:
            win = ("2026-06-01", "2026-06-30")
            where.append(f'substr("{T["date"]}",1,10) between ? and ?'); params += list(win); trace.append(("registry", "window June 2026", june.group(0)))
        elif T["window"] == "june":
            win = (T["start"], T["end"]); trace.append(("registry", "this record kind covers June 2026 only", june.group(0)))
        else:
            return None, ("registry", f"{T['label']} records are not dated, so a period cannot be applied")
        for i, x in enumerate(toks):
            if x in ("june", "2026"):
                used.add(i)
    whole = False
    if not win and T["date"]:
        win = (T["start"], T["end"]); whole = True; trace.append(("registry", f"no period named: whole coverage {T['start']} to {T['end']}", "(none)"))
    # ---- decide the aggregate and the expression
    expr, how = None, None
    if cmp_ and not measure:
        return None, ("ontology", "a comparison needs a named measure (for example 'selling price above 100 rupees')")
    if on_days:
        if not T["date"]:
            return None, ("schema", f"{T['label']} records have no date column, so days cannot be counted")
        how = "count_distinct_day"; expr = f'count(distinct substr("{T["date"]}",1,10))'
        if cmp_:
            where.append(f'"{measure}" {cmp_[0]} ?'); params.append(cmp_[1])
    elif kind in ("bill", "distinct") and (measure or cmp_):
        return None, ("ontology", f"a {subject[3]} is counted here; it cannot also carry a measure ({measure or 'comparison'})")
    elif kind in ("bill", "distinct") and agg in ("avg", "max", "min", "sum", "much"):
        return None, ("ontology", f"a {subject[3]} is counted here; its average, total or extreme needs a grouped value that is not defined")
    elif kind == "bill":
        how = "count_distinct"; expr = f'count(distinct "{subject[4]}")'
    elif kind == "distinct":
        how = "count_distinct"; expr = f'count(distinct "{subject[4]}")'
    elif distinct and "bill" in stoks and "bill_id" in T["cols"]:
        how = "count_distinct"; expr = 'count(distinct "bill_id")'; used |= {i for i, x in enumerate(stoks) if x == "bill"}
    elif distinct and re.search(r"\bproduct", question.lower()) and T["sku"] and tstem != "products":
        how = "count_distinct"; expr = f'count(distinct "{T["sku"]}")'
        used |= {i for i, x in enumerate(stoks) if x == "product"}
    elif measure:
        c = T["cols"][measure]
        if cmp_:
            where.append(f'"{measure}" {cmp_[0]} ?'); params.append(cmp_[1]); expr = "count(*)"; how = "count"
        elif agg in ("max", "min", "avg"):
            expr = f'{ {"max": "max", "min": "min", "avg": "avg"}[agg] }("{measure}")'; how = agg
        elif agg in ("count", "sum", "much") or (agg is None and c["additive"]):
            if not c["additive"]:
                return None, ("ontology", f"{measure.replace('_', ' ')} ({c['unit']}) is not additive: it cannot be totalled across rows")
            if agg == "count" and c["unit"] == "rupees":
                return None, ("ontology", "'how many' counts things; an amount in rupees is asked for with 'how much' or 'total'")
            if agg == "much" and c["unit"] != "rupees":
                return None, ("ontology", f"'how much' asks for an amount in rupees; {c['unit']} are counted with 'how many'")
            expr = f'sum("{measure}")'; how = "sum"
        elif agg is None:
            expr = f'max("{measure}")'; how = "lookup"
        else:
            return None, ("ontology", "unrecognised aggregate")
    else:
        if agg == "much":
            return None, ("ontology", "'how much' needs an amount (rupees) of this record kind; none is named")
        if agg in ("max", "min", "avg", "sum"):
            return None, ("ontology", f"which measure of {T['label']}? the question names none")
        expr = "count(*)"; how = "count"
    # ---- every remaining word must be defined
    own = set()
    for cname, cc in T["cols"].items():
        if cc["kind"] in ("id", "number"):      # an id or a measure word is never free: it must be matched as a noun, a cue or a filter
            continue
        for w in re.split(r"[_]", cname):
            if w not in ("ts", "inr", "id"):
                own.add(stem(w))
    left = [toks[i] for i, x in enumerate(stoks) if i not in used and x not in O.glue and x not in own and not re.fullmatch(r"\d{4}|\d+(\.\d+)?", x)]
    # numbers: only those used by a comparator, a time or an id may remain; a stray number means an unmodelled condition
    stray = [toks[i] for i, x in enumerate(stoks) if i not in used and re.fullmatch(r"\d+(\.\d+)?", x) and x not in ("2026", "014")]
    left += stray
    if left:
        return None, ("ontology", "not defined for this record kind: " + ", ".join(sorted(set(left))))
    if how == "lookup":
        cnt = db().execute(f'select count(*) from "{tstem}"' + (" where " + " and ".join(where) if where else ""), params).fetchone()[0]
        if cnt != 1:
            return None, ("ontology", f"asking for a {measure.replace('_', ' ')} without a total, average or extreme needs exactly one matching record; found {cnt}")
    sql = f'select {expr} from "{tstem}"' + (" where " + " and ".join(where) if where else "")
    return dict(sql=sql, params=tuple(params), how=how, table=tstem, trace=trace, measure=measure, window=win, whole=whole), None


def answer(question):
    question = re.sub(r"\s+", " ", question.strip())
    O = onto()
    toks = tokenize(re.sub(r"\bstore 014('s)?\b", " ", question, flags=re.I))
    toks = [t for t in toks if t != "014"]
    stoks = [stem(t) for t in toks]
    layers = {"schema": "not run", "ontology": "not run", "registry": "not run"}
    # ---- layers 1 and 2: which record kind is the question about?
    subs = []
    for tstem, T in O.tables.items():
        sc = [len(c) for c in T["nouns"] if has_cue(stoks, c)]
        if sc:
            subs.append((max(sc), ("table", tstem, [c for c in T["nouns"] if has_cue(stoks, c)])))
    for tstem, col, cuesets, label in O.distincts:
        sc = [len(c) for c in cuesets if has_cue(stoks, c)]
        if sc:
            subs.append((max(sc) + 0.5, ("distinct", tstem, [c for c in cuesets if has_cue(stoks, c)], label, col)))
    # measure-only readings (no table noun): a numeric column whose cue words are all present
    if True:
        for tstem, T in O.tables.items():
            for cname, c in T["cols"].items():
                if c["kind"] == "number":
                    sc = [len(cs) for cs in c["cues"] if has_cue(stoks, cs)]
                    if sc:
                        subs.append((max(sc), ("table", tstem, [])))
    bills = [(1, ("bill", "pos-lines-may-june", [["bill"]], "bill", "bill_id"))] if "bill" in stoks else []
    subs += bills
    hard, proxy = registry_layer(question)
    if not subs:
        layers.update(schema="no table, column or measure of the 21 records is named in the question", ontology="no defined measure or record kind", registry="; ".join(hard + proxy) or "nothing to flag")
        msg = "I can't answer this from Store 014's records: " + (("; ".join(hard + proxy)) if hard or proxy else "it does not ask for a count, total, average or price of anything the records hold.")
        return refusal("no_record" if hard or not proxy else "proxy", layers, msg)
    top = max(s[0] for s in subs)
    cands = [s[1] for s in subs if s[0] == top]
    # two different record kinds named in one question: a join is not defined
    readings, why = [], []
    for sub in cands:
        plan, err = read_one(question, sub, toks, stoks)
        if plan:
            readings.append(plan)
        else:
            why.append(err)
    if readings:
        # other record-kind nouns left unconsumed make this a join: refuse. read_one already rejects stray words, so reaching here means none.
        pass
    layers["schema"] = "ok" if readings else (next((w[1] for w in why if w[0] == "schema"), "ok"))
    layers["ontology"] = "ok" if readings else (next((w[1] for w in why if w[0] == "ontology"), "ok"))
    layers["registry"] = "; ".join(hard + proxy) if (hard or proxy) else "ok"
    if hard:
        return refusal("no_record", layers, "I can't answer this from Store 014's records: " + "; ".join(hard))
    if not readings:
        return refusal("no_record", layers, "I can't answer this from Store 014's records: " + "; ".join(sorted({w[1] for w in why})))
    vals = []
    for p in readings:
        v = db().execute(p["sql"], p["params"]).fetchone()[0]
        vals.append(None if v is None else round(float(v), 2))
    if len({v for v in vals}) != 1 or vals[0] is None:
        return refusal("no_record", layers, "I can't answer this reliably: the question reads two ways that give different numbers" if vals[0] is not None else
                       "I can't answer this: the records hold no matching rows", trace=[t for p in readings for t in p["trace"]])
    p = readings[0]
    value = vals[0]
    if p["how"] in ("count", "count_distinct", "count_distinct_day") or (p["how"] == "sum" and value == int(value) and not any("rupee" in str(O.tables[p["table"]]["cols"][p["measure"]]["unit"]) for _ in [0])):
        value = int(value)
    if proxy:
        layers["registry"] = "; ".join(proxy)
        return refusal("proxy", layers, "The records hold only a stand-in for this: " + "; ".join(proxy), value=value, sql=p["sql"], params=p["params"], trace=p["trace"])
    return dict(decision="answer", value=value, sql=p["sql"], params=p["params"], layers=layers, trace=p["trace"], window=p["window"], whole_coverage=p["whole"],
                message=(f"No period was named, so this covers everything the records hold for this record kind: {p['window'][0]} to {p['window'][1]}." if p["whole"] else None))


if __name__ == "__main__":
    import json
    print(json.dumps(answer(" ".join(sys.argv[1:])), indent=1, default=str))
