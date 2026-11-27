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
BROAD = [r"\bso far\b", r"\bthis year\b", r"\bover the (last )?year\b", r"\blast (six|twelve|\d+) months\b", r"\bquarter\b", r"\bever\b", r"\ball time\b",
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
    for m in months:
        if m == "june":
            continue
        if m == "may":
            if may_days and all(d >= 4 for d in may_days) and till:
                continue          # explicit days inside the till window, e.g. "from 4 May to 31 May"
            if till:
                proxy.append("May is a part month in the till lines (4 May to 28 June)")
            else:
                reasons.append("May is outside this table (June only)")
        else:
            reasons.append(f"{m} is outside the records")
    return reasons, proxy


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
    if not (intent and entity):
        return {"decision": "no_record", "reasons": ["not a certified measure: no count, total or price of anything the 21 tables hold"]}
    return {"decision": "pass", "reasons": [], "tables": entity}
