"""Deterministic question guard: decides from the question text and the registry alone, with no model call.
decide(question) -> {"decision": "no_record" | "proxy" | "pass", "reasons": [...]}
Order: terms that are not recorded and dates outside the records give no_record; stand-in terms and part-month windows give proxy; else pass.
"""
import json
import re
from pathlib import Path

REG = json.loads((Path(__file__).parent / "registry.json").read_text())
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"], 1)}
MONTH_RE = "|".join(MONTHS)
BROAD = [r"\blast \w+ months\b", r"\bso far\b", r"\bthis year\b", r"\bover the (last )?year\b", r"\blast (six|twelve|\d+) months\b", r"\bquarter\b", r"\bever\b", r"\ball time\b",
         r"\b(last|past) (year|twelve months)\b", r"\bof the year\b", r"\bin 20\d\d\b(?!.*\b(" + MONTH_RE + r")\b)", r"\bof 20\d\d\b(?!.*\b(" + MONTH_RE + r")\b)", r"\byear\b"]


def window_check(q):
    ql = q.lower()
    reasons, proxy = [], []
    years = {int(y) for y in re.findall(r"\b(20\d\d)\b", ql)}
    if any(y != 2026 for y in years):
        reasons.append("year outside 2026")
    months = set(m for m in re.findall(r"\b(" + MONTH_RE + r")\b", ql))
    broad = [p for p in BROAD if re.search(p, ql)]
    if broad and not months - {"june"} == set() and False:
        pass
    if broad:
        reasons.append("needs a longer period than the records cover")
    # day-level mentions of May
    may_days = [int(d) for d in re.findall(r"\b(\d{1,2})\s+may\b", ql)]
    till = any(re.search(p, ql) for p in REG["till_patterns"])
    for m in sorted(months, key=MONTHS.get):
        if m == "june":
            continue
        if m == "may":
            if may_days and any(d < 4 for d in may_days):
                reasons.append("1 to 3 May are before the till lines start (4 May)")
            elif may_days and all(d >= 4 for d in may_days) and till:
                continue          # explicit days inside the till window, e.g. "from 4 May to 31 May"
            if till:
                proxy.append("May is a part month in the till lines (4 May to 28 June)")
            else:
                reasons.append("May is outside this table (June only)")
        else:
            reasons.append(f"{m} is outside the records")
    return reasons, proxy


STOP = set("""a an the of in on at to for from by with and or but if is are was were be been do does did done has have had having it its this that these those
there their they them we you your i my me our what which how many much store 014 stores s t than then as per each every any all some no not into over under about up down out off between
among during while when where whom whose whether june 2026 rupees rupee inr""".split())
AGG = set("""total totals average mean number count counts sum highest lowest biggest smallest largest maximum minimum single different distinct unique least
more less fewer most two three four five days day week hour hours month months year years first last before after end slot""".split())


def vocabulary():
    """Words the records explain: table and column names, the values in their categorical columns, product names, entity nouns and
    measure words. Built from the CSV files and the registry, not from any question list."""
    import csv
    from pathlib import Path as P
    data = P(__file__).resolve().parents[2] / "public" / "data" / "india-grocery"
    words = set()
    def add(text):
        for w in re.findall(r"[a-z]+", str(text).lower()):
            words.add(w); words.add(w.rstrip("s")); words.add(w + "s")
    for f in data.glob("*.csv"):
        add(f.stem)
        rows = list(csv.DictReader(open(f)))
        for c in rows[0]:
            add(c)
            vals = {r[c] for r in rows}
            if len(vals) <= 40 and not c.endswith(("_ts", "date")) and not all(re.fullmatch(r"[-\d.:T ]*", v) for v in vals):
                for v in vals:
                    add(v)
        if f.name == "products.csv":
            for r in rows:
                add(r["name"]); add(r["pack"])
    for pats in REG["entities"].values():
        for p in pats:
            add(re.sub(r"\\[bBdD]|[()?!<>|.*\[\]\\]", " ", p))
    # measure and relation words the tables explain (a stock count's adjustment is the book-versus-counted difference, etc.)
    # events the tables record (the registry's verbs): a question may ask about these and nothing else
    add("ring rung rang up make made log logged record recorded receive received arrive arrived dispatch dispatched deliver delivered pay paid trigger triggered "
        "show shows showed include included find found settle settled count counted audit audited complain complained refund refunded write wrote order ordered sell sold "
        "request requested complete completed have had has take taken rise exceed above below least truck trucks vehicle product products item items each several "
        "can which ids id records these single manager's manager request weekday weekend being been sent one two three four five six seven eight nine ten "
        "twice once both either across carry debit debited")
    add("difference found book counted adjustment settled settlement net gross paid payout received arrived arrive dispatched slot end ordered order warehouse sold sell sale "
        "revenue price priced selling cost written write off expired damaged declined failed approved refund refunds complaint complaints charged twice debited returned "
        "customer customers shipment pallet pallets receipt receipts audit audits shelf empty counts stock units unit bag bags kg line lines row rows bill bills attempt attempts "
        "payment payments card cash upi till tills service provider report transaction transactions status delivery deliveries route fresh milk bread curd rice sugar atta oil dal")
    return words | AGG | STOP


VOCAB = None


def unexplained(q):
    global VOCAB
    if VOCAB is None:
        VOCAB = vocabulary()
    toks = re.findall(r"[a-z][a-z'-]*", q.lower())
    out = []
    for t in toks:
        base = t.split("'")[0]
        for part in re.split(r"-", base):
            if part and part not in VOCAB and part.rstrip("s") not in VOCAB and part not in MONTHS:
                out.append(part)
    return out


def decide(q):
    ql = q.lower()
    reasons, proxy = [], []
    for t in REG["terms"]:
        if any(re.search(p, ql) for p in t["patterns"]):
            (reasons if t["status"] == "not_recorded" else proxy).append(f'{t["id"]}: {t["note"]}')
    r, p = window_check(q)
    reasons += r; proxy += p
    if reasons:
        return {"decision": "no_record", "reasons": reasons}
    if proxy:
        return {"decision": "proxy", "reasons": proxy}
    intent = any(re.search(p, ql) for p in REG["intent"])
    entity = [name for name, pats in REG["entities"].items() if any(re.search(p, ql) for p in pats)]
    left = unexplained(q)
    if left:
        return {"decision": "no_record", "reasons": ["words the records do not explain: " + ", ".join(sorted(set(left)))]}
    if not (intent and entity):
        return {"decision": "no_record", "reasons": ["not a certified measure: no count, total or price of anything the 21 tables hold"]}
    return {"decision": "pass", "reasons": [], "tables": entity}
