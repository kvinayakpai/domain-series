"""The planning layer: a model may PROPOSE a query plan; code checks every part of it against the ontology and runs it.

Why: the one-number resolver refuses questions that need several tables, a list, a comparison or a premise check, although the records can answer them.
A model is good at proposing which tables to join. It is not trusted to say what the data holds or to write the answer.

The model never writes SQL and never writes the answer. It writes a plan in a small fixed form (below). Code then:
  1. refuses at once when the registry says no record can hold the question (why, who, demand, lost sale ...);
  2. checks every table, column, join, value, function and aggregate against the ontology (anything not defined is refused, not repaired);
  3. checks the period: a date outside a table's coverage is refused, and every day, month-day or year in the question must be in the plan;
  4. compiles the SQL itself, runs it read-only, and writes the answer from the rows, showing the plan in plain words.

Plan form (JSON):
 {"from": "<table>", "joins": [{"table": "<table>", "type": "inner|left", "on": [[<node>, <node>], ...]}],
  "where": [<cond>], "group_by": [<node>], "select": [{"as": "<name>", "expr": <node>}], "having": [<cond>],
  "order_by": [{"by": "<name>", "dir": "asc|desc"}], "limit": <int, at most 200>}
 or {"cannot": "<why no plan is possible>"}
 node: {"col": "<table>.<column>"} | {"lit": <value>} | {"ref": "<select name>"} (only in having / order_by)
       {"fn": "day|hour|abs|round", "arg": node} | {"fn": "days_between|hours_between", "args": [node, node]}
       {"op": "+|-|*|/", "args": [node, node]} | {"agg": "count|count_distinct|sum|avg|min|max", "arg": node or "*"}
 cond: {"op": "=|!=|<|<=|>|>=", "args": [node, node]} | {"op": "in", "arg": node, "values": [..]} | {"op": "between", "arg": node, "low": v, "high": v}
       {"op": "is_null|not_null", "arg": node} | {"op": "or|and", "args": [cond, cond, ...]}
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import csv
import sqlite3
import resolver as R

SKU_COLS = {"sku", "sku_scanned", "sku_booked", "asn_sku"}
GROUPS = {**{c: "sku" for c in SKU_COLS}, "shipment_id": "shipment", "sscc": "sscc", "order_id": "order", "bill_id": "bill", "bill_ref": "bill",
          "rrn": "rrn", "grn_id": "grn", "refund_id": "refund", "gtin": "gtin", "gtin_scanned": "gtin"}
MAX_LIMIT = 200
MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}


_PDB = None


def planner_db():
    """Its own read-only-in-practice copy of the records: every empty cell is NULL, so 'no RRN' and 'not completed' can be asked for as is_null."""
    global _PDB
    if _PDB is None:
        _PDB = sqlite3.connect(":memory:")
        for stem_, t in R.onto().tables.items():
            rows = list(csv.DictReader(open(R.DATA / f"{stem_}.csv")))
            cols = list(rows[0])
            _PDB.execute(f'create table "{stem_}" ({", ".join(chr(34) + c + chr(34) + " " + ("real" if t["cols"][c]["kind"] == "number" else "text") for c in cols)})')
            _PDB.executemany(f'insert into "{stem_}" values ({",".join("?" * len(cols))})', [[(None if r[c] == "" else r[c]) for c in cols] for r in rows])
    return _PDB


class PlanError(Exception):
    """layer 'ontology' by default; SchemaError is layer 'schema': the plan names a table, column or form that does not exist."""
    layer = "ontology"


class SchemaError(PlanError):
    layer = "schema"


def ps(info):
    return list(info.get("params", [])) + ([info["param"]] if "param" in info else [])


def schema_text():
    """The schema as the model sees it, built from the ontology."""
    o = R.onto(); lines = []
    for stem_, t in sorted(o.tables.items()):
        cov = f", covers {t['start']} to {t['end']}" if t["start"] else ""
        lines.append(f"- {stem_} ({t['label']}; one row = {t['grain']}{cov})")
        for n, c in t["cols"].items():
            extra = ""
            if c["kind"] == "code" and c["values"]:
                extra = " values: " + ", ".join(sorted(set(c["values"].values())))
            if c["kind"] == "number":
                extra = f" ({c['unit']}{'' if c['additive'] in (None, True) else ', not additive: never sum it'})"
            lines.append(f"    {n}: {c['kind']}{extra}")
    lines.append("Products (sku): " + ", ".join(f"{v} = {lab}" for v, _, lab in o.products))
    lines.append("Columns that can be joined (same group only): " + "; ".join(f"{g}: " + ", ".join(sorted(k for k, v in GROUPS.items() if v == g)) for g in sorted(set(GROUPS.values()))))
    return "\n".join(lines)


def prompt_for(question):
    return f"""You plan a query over one grocery store's records. You do not answer the question and you do not write SQL.
Reply with ONE JSON object in the plan form below, or {{"cannot": "<reason>"}} when the records cannot answer the question or the plan cannot be expressed in this form.
Use only the tables and columns listed. Take every date, number, product and status from the question. Do not invent values. If the question gives a claim (a number or a reason) as its premise, plan the query that checks the data, not the claim.
Dates and times are text such as 2026-06-11T14:20 (use fn day for the date, hour for the hour). Put one date in a condition as {{"lit": "2026-06-11"}} and use fn day on the column.
Do not sum a column marked not additive. Join tables only on columns of the same group. A table can appear once.

PLAN FORM
{__doc__.split('Plan form (JSON):')[1].strip()}

EXAMPLE 1  (How many units of curd were sold on 5 June 2026?)
{{"from": "daily-sales-june", "where": [{{"op": "=", "args": [{{"col": "daily-sales-june.sku"}}, {{"lit": "CURD-500G"}}]}}, {{"op": "=", "args": [{{"col": "daily-sales-june.date"}}, {{"lit": "2026-06-05"}}]}}], "select": [{{"as": "units", "expr": {{"agg": "sum", "arg": {{"col": "daily-sales-june.units_sold"}}}}}}]}}
EXAMPLE 2  (Which shelf audits found an item empty while the book showed stock?)
{{"from": "shelf-audits-june", "joins": [{{"table": "inventory-book-june", "type": "inner", "on": [[{{"col": "shelf-audits-june.sku"}}, {{"col": "inventory-book-june.sku"}}], [{{"fn": "day", "arg": {{"col": "shelf-audits-june.audit_ts"}}}}, {{"col": "inventory-book-june.date"}}]]}}], "where": [{{"op": "=", "args": [{{"col": "shelf-audits-june.status"}}, {{"lit": "empty"}}]}}, {{"op": ">", "args": [{{"col": "inventory-book-june.book_on_hand_close"}}, {{"lit": 0}}]}}], "select": [{{"as": "audit_ts", "expr": {{"col": "shelf-audits-june.audit_ts"}}}}, {{"as": "sku", "expr": {{"col": "shelf-audits-june.sku"}}}}, {{"as": "book_stock", "expr": {{"col": "inventory-book-june.book_on_hand_close"}}}}]}}

SCHEMA
{schema_text()}

Question: {question}"""


# ----------------------------------------------------------------------------- checking and compiling
class Ctx:
    def __init__(self, plan):
        o = R.onto(); self.o = o; self.params = []; self.tables = []; self.aliases = set(); self.dates = []; self.ranges = []
        t = plan.get("from"); self.need_table(t); self.tables.append(t)

    def need_table(self, name):
        if name not in self.o.tables:
            raise SchemaError(f"table '{name}' is not defined")
        if name in self.tables:
            raise SchemaError(f"table '{name}' appears twice (a self-join is not allowed)")


def col_of(ctx, ref):
    if not isinstance(ref, str) or ref.count(".") != 1:
        raise SchemaError(f"column reference '{ref}' must be table.column")
    t, c = ref.split(".")
    if t not in ctx.tables:
        raise SchemaError(f"table '{t}' is not in this plan's from or joins")
    cols = ctx.o.tables[t]["cols"]
    if c not in cols:
        raise SchemaError(f"column '{c}' is not in table '{t}'")
    return t, c, cols[c]


def node(ctx, n, allow_agg=False, allow_ref=False, refs=None):
    """Return (sql, type, info) where type is number|time|id|code|text|bool and info carries the column for literal checks."""
    if not isinstance(n, dict):
        raise SchemaError("a node must be an object")
    keys = set(n)
    if keys == {"col"}:
        t, c, meta = col_of(ctx, n["col"])
        return f'"{t}"."{c}"', meta["kind"], dict(table=t, col=c, meta=meta)
    if keys == {"lit"}:
        v = n["lit"]
        if not isinstance(v, (int, float, str)) or isinstance(v, bool):
            raise PlanError("a literal must be a number or text")
        return "?", "lit", dict(value=v, param=v)
    if keys == {"ref"}:
        if not allow_ref or n["ref"] not in (refs or {}):
            raise PlanError(f"'{n['ref']}' is not a select name usable here")
        return f'"{n["ref"]}"', refs[n["ref"]], {}
    if keys == {"fn", "arg"}:
        s, ty, info = node(ctx, n["arg"], allow_agg, allow_ref, refs)
        fn = n["fn"]
        if fn == "day":
            if ty != "time": raise PlanError("day() needs a date or time column")
            return f"substr({s},1,10)", "time", {k: info[k] for k in ("meta", "table", "col") if k in info} | {"params": ps(info)}
        if fn == "hour":
            if ty != "time": raise PlanError("hour() needs a time column")
            return f"cast(substr({s},12,2) as integer)", "number", {"params": ps(info)}
        if fn in ("abs", "round"):
            if ty != "number": raise PlanError(f"{fn}() needs a number")
            return f"{fn}({s})", "number", {"params": ps(info)}
        raise SchemaError(f"function '{fn}' is not defined")
    if keys == {"fn", "args"} and n["fn"] in ("days_between", "hours_between") and isinstance(n["args"], list) and len(n["args"]) == 2:
        a, ta, ia = node(ctx, n["args"][0], allow_agg, allow_ref, refs); b, tb, ib = node(ctx, n["args"][1], allow_agg, allow_ref, refs)
        if ta != "time" or tb != "time": raise PlanError(f"{n['fn']} needs two time columns")
        k = "24.0 * " if n["fn"] == "hours_between" else ""
        return f"({k}(julianday({a}) - julianday({b})))", "number", {"params": ps(ia) + ps(ib)}
    if keys == {"op", "args"} and n["op"] in "+-*/" and n["op"] and isinstance(n["args"], list) and len(n["args"]) == 2:
        a, ta, ia = node(ctx, n["args"][0], allow_agg, allow_ref, refs); b, tb, ib = node(ctx, n["args"][1], allow_agg, allow_ref, refs)
        for ty, i in ((ta, ia), (tb, ib)):
            if ty not in ("number", "lit") or (ty == "lit" and not isinstance(i["value"], (int, float))):
                raise PlanError("arithmetic needs numbers")
        sql = f"({a} {n['op']} {b})" if n["op"] != "/" else f"({a} * 1.0 / nullif({b}, 0))"
        return sql, "number", {"params": ps(ia) + ps(ib)}
    if keys == {"agg", "arg"}:
        if not allow_agg: raise PlanError("an aggregate is not allowed here")
        ag = n["agg"]
        if ag not in ("count", "count_distinct", "sum", "avg", "min", "max"):
            raise SchemaError(f"aggregate '{ag}' is not defined")
        if n["arg"] == "*":
            if ag != "count": raise PlanError("only count can take *")
            return "count(*)", "number", {}
        s, ty, info = node(ctx, n["arg"], False, allow_ref, refs)
        if ag in ("sum", "avg"):
            if ty != "number": raise PlanError(f"{ag} needs a number column")
            if "meta" in info and info["meta"]["additive"] is False and ag == "sum":
                raise PlanError(f"column {info['col']} is not additive and cannot be summed")
        if ag in ("min", "max") and ty not in ("number", "time"):
            raise PlanError(f"{ag} needs a number or time column")
        sql = f"count(distinct {s})" if ag == "count_distinct" else f"{ag}({s})"
        return sql, "number" if ag != "min" and ag != "max" else ty, {"params": ps(info)}
    raise SchemaError(f"node {json.dumps(n)[:80]} is not in the plan form")


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$")


def check_literal(ctx, info, value, other_ty):
    """A literal compared with a column must be a value that column can hold."""
    meta = info.get("meta")
    if meta is None:
        return
    k = meta["kind"]
    if k == "number":
        if not isinstance(value, (int, float)): raise PlanError(f"{info['col']} is a number; '{value}' is not")
    elif k == "time":
        if not isinstance(value, str) or not DATE_RE.match(value): raise PlanError(f"{info['col']} is a date or time; '{value}' is not in the form 2026-06-11 or 2026-06-11T14:20")
        ctx.dates.append((info["table"], value))
    elif k == "code":
        if value not in set(meta["values"].values()): raise PlanError(f"'{value}' is not a defined value of {info['col']}")
    elif k == "id":
        if info["col"] in SKU_COLS:
            if value not in {v for v, _, _ in ctx.o.products}: raise PlanError(f"'{value}' is not a defined product")
        elif meta["idpat"] and not re.fullmatch(meta["idpat"], str(value), re.I): raise PlanError(f"'{value}' does not look like a {info['col']}")
        elif not isinstance(value, str) or len(value) > 40 or not re.fullmatch(r"[A-Za-z0-9\-_.]+", value): raise PlanError(f"'{value}' is not a valid id")
    else:
        if not isinstance(value, str) or len(value) > 60: raise PlanError("text literal too long")


def cond(ctx, c, having=False, refs=None):
    if not isinstance(c, dict) or "op" not in c:
        raise PlanError("a condition needs an op")
    op = c["op"]; ar = dict(allow_agg=having, allow_ref=having, refs=refs)
    if op in ("and", "or"):
        if not isinstance(c.get("args"), list) or not c["args"]: raise PlanError(f"'{op}' needs conditions")
        parts = [cond(ctx, x, having, refs) for x in c["args"]]
        return "(" + f" {op.upper()} ".join(parts) + ")"
    if op in ("=", "!=", "<", "<=", ">", ">="):
        if set(c) != {"op", "args"} or not isinstance(c["args"], list) or len(c["args"]) != 2: raise PlanError("a comparison needs two arguments")
        a, ta, ia = node(ctx, c["args"][0], **ar); b, tb, ib = node(ctx, c["args"][1], **ar)
        if ta == "lit" and tb == "lit": raise PlanError("a comparison of two literals")
        if ta == "lit": check_literal(ctx, ib, ia["value"], tb)
        elif tb == "lit": check_literal(ctx, ia, ib["value"], ta)
        else:
            if ta != tb and not {ta, tb} <= {"id", "text", "code"}: raise PlanError(f"cannot compare {ta} with {tb}")
        if "meta" in ia and "meta" in ib and ia["meta"]["kind"] == "number" and ib["meta"]["kind"] == "number" and ia["meta"]["unit"] != ib["meta"]["unit"]:
            raise PlanError(f"cannot compare {ia['meta']['unit']} with {ib['meta']['unit']}")
        ctx.params.extend(ps(ia)); ctx.params.extend(ps(ib))
        for lit_info, col_info in ((ia, ib), (ib, ia)):
            if "value" in lit_info and col_info.get("meta", {}).get("kind") == "time" and isinstance(lit_info["value"], str):
                ctx.ranges.append((col_info["table"], op if lit_info is ib else {"<": ">", "<=": ">=", ">": "<", ">=": "<="}.get(op, op), [lit_info["value"]]))
        return f"({a} {op} {b})"
    if op == "in":
        if set(c) != {"op", "arg", "values"} or not isinstance(c["values"], list) or not c["values"] or len(c["values"]) > 30: raise PlanError("'in' needs arg and 1 to 30 values")
        a, ta, ia = node(ctx, c["arg"], **ar)
        for v in c["values"]: check_literal(ctx, ia, v, ta)
        ctx.params.extend(ps(ia)); ctx.params.extend(c["values"])
        if ia.get("meta", {}).get("kind") == "time": ctx.ranges.append((ia["table"], "in", list(c["values"])))
        return f"({a} in ({','.join('?' * len(c['values']))}))"
    if op == "between":
        if set(c) != {"op", "arg", "low", "high"}: raise PlanError("'between' needs arg, low, high")
        a, ta, ia = node(ctx, c["arg"], **ar)
        check_literal(ctx, ia, c["low"], ta); check_literal(ctx, ia, c["high"], ta)
        ctx.params.extend(ps(ia)); ctx.params.extend([c["low"], c["high"]])
        if ia.get("meta", {}).get("kind") == "time": ctx.ranges.append((ia["table"], "between", [c["low"], c["high"]]))
        return f"({a} between ? and ?)"
    if op in ("is_null", "not_null"):
        if set(c) != {"op", "arg"}: raise PlanError(f"'{op}' needs arg")
        a, ta, ia = node(ctx, c["arg"], **ar)
        return f"({a} is {'' if op == 'is_null' else 'not '}null)"
    raise SchemaError(f"condition op '{op}' is not defined")


def expand_params(ctx, parts):
    return parts


def compile_plan(plan):
    """Return (sql, params, description). Raises PlanError for anything not defined."""
    if not isinstance(plan, dict): raise SchemaError("the plan is not an object")
    allowed = {"from", "joins", "where", "group_by", "select", "having", "order_by", "limit", "covers"}
    extra = set(plan) - allowed
    if extra: raise SchemaError(f"plan keys not defined: {sorted(extra)}")
    ctx = Ctx(plan)
    seen_params = []
    # joins
    join_sql = []
    for j in plan.get("joins", []):
        if not isinstance(j, dict) or set(j) - {"table", "type", "on"}: raise PlanError("a join needs table, type, on")
        ctx.need_table(j["table"])
        if j.get("type", "inner") not in ("inner", "left"): raise PlanError("join type must be inner or left")
        ctx.tables.append(j["table"])
        if not isinstance(j.get("on"), list) or not j["on"]: raise PlanError("a join needs at least one 'on' pair")
        ons = []
        for pair in j["on"]:
            if not isinstance(pair, list) or len(pair) != 2: raise PlanError("an 'on' pair has two nodes")
            (a, ta, ia), (b, tb, ib) = node(ctx, pair[0]), node(ctx, pair[1])
            ga = group_of(pair[0], ia); gb = group_of(pair[1], ib)
            if ga is None or ga != gb: raise PlanError(f"cannot join {json.dumps(pair[0])[:60]} to {json.dumps(pair[1])[:60]}: not the same kind of key")
            ons.append(f"{a} = {b}")
        join_sql.append(f'{"left" if j.get("type") == "left" else "inner"} join "{j["table"]}" on {" and ".join(ons)}')
    # where
    where = [cond(ctx, c) for c in plan.get("where", [])]
    where_params = list(ctx.params); ctx.params.clear()
    # select
    sel = plan.get("select")
    if not isinstance(sel, list) or not sel or len(sel) > 12: raise PlanError("select needs 1 to 12 items")
    refs = {}; sel_sql = []; sel_params = []; has_agg = False
    for s in sel:
        if not isinstance(s, dict) or set(s) != {"as", "expr"} or not re.fullmatch(r"[a-z][a-z0-9_]{0,30}", str(s["as"])): raise PlanError("a select item needs 'as' (a lowercase name) and 'expr'")
        if s["as"] in refs: raise PlanError("duplicate select name")
        q, ty, info = node(ctx, s["expr"], allow_agg=True)
        if "param" in info or "value" in info: raise PlanError("a select item cannot be a bare literal")
        has_agg = has_agg or "agg" in json.dumps(s["expr"])
        refs[s["as"]] = ty; sel_sql.append(f'{q} as "{s["as"]}"'); sel_params.extend(ps(info))
    gb = []
    for g in plan.get("group_by", []):
        q, ty, info = node(ctx, g)
        if ps(info) or "value" in info: raise PlanError("group_by cannot hold a literal")
        gb.append(q)
    if has_agg:
        for s in sel:
            if "agg" not in json.dumps(s["expr"]) and not any(node(ctx, s["expr"])[0] == x for x in gb):
                raise PlanError(f"select '{s['as']}' must be aggregated or in group_by")
    elif gb: raise PlanError("group_by without an aggregate")
    having = [cond(ctx, c, having=True, refs=refs) for c in plan.get("having", [])]
    having_params = list(ctx.params); ctx.params.clear()
    order = []
    for ob in plan.get("order_by", []):
        if not isinstance(ob, dict) or set(ob) - {"by", "dir"} or ob.get("by") not in refs or ob.get("dir", "asc") not in ("asc", "desc"): raise PlanError("order_by needs a select name and asc or desc")
        order.append(f'"{ob["by"]}" {ob.get("dir", "asc")}')
    lim = plan.get("limit", MAX_LIMIT)
    if not isinstance(lim, int) or not 1 <= lim <= MAX_LIMIT: raise PlanError(f"limit must be 1 to {MAX_LIMIT}")
    sql = f'select {", ".join(sel_sql)} from "{plan["from"]}" ' + " ".join(join_sql)
    if where: sql += " where " + " and ".join(where)
    if gb: sql += " group by " + ", ".join(gb)
    if having: sql += " having " + " and ".join(having)
    if order: sql += " order by " + ", ".join(order)
    sql += f" limit {lim}"
    # parameter order follows the text of the SQL: select, where, having
    params = sel_params + where_params + having_params
    # coverage: a date test that can only select rows outside a table's records is refused
    for t, op, lits in ctx.ranges:
        tb = R.onto().tables[t]
        if not tb["start"]: continue
        lo, hi = tb["start"], tb["end"]; d = [x[:10] for x in lits]
        out = ((op in ("=", "in") and any(x < lo or x > hi for x in d)) or (op == "between" and (d[0] > hi or d[1] < lo)) or
               (op in (">", ">=") and d[0] > hi) or (op in ("<", "<=") and d[0] < lo))
        if out:
            raise PlanError(f"{', '.join(d)} is outside the records of '{t}' ({lo} to {hi})")
    return sql, params, ctx


def group_of(n, info):
    if set(n) == {"col"}:
        if info["col"] in ("date", "settlement_date"): return "day"
        return GROUPS.get(info["col"])
    if n.get("fn") == "day" and isinstance(n.get("arg"), dict) and set(n["arg"]) == {"col"}:
        return "day"
    return None


def question_dates(question):
    """Days, month-days and years named in the question; each must appear in the plan."""
    q = question.lower(); out = []
    for m in re.finditer(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(MONTHS) + r")\b(?:\s+(\d{4}))?", q):
        out.append(("day", int(m.group(1)), MONTHS[m.group(2)], m.group(3)))
    for y in re.findall(r"\b(20\d{2})\b", q): out.append(("year", y))
    return out


def date_check(question, ctx_dates, tables):
    """Every day, month-day and year named in the question must be in the plan, unless the plan's tables lie wholly inside that year."""
    o = R.onto().tables
    years_covered = {y for t in tables if o[t]["start"] for y in (o[t]["start"][:4], o[t]["end"][:4])}
    lits = [d for _, d in ctx_dates]
    for item in question_dates(question):
        if item[0] == "year":
            if not any(l.startswith(item[1]) for l in lits) and item[1] not in years_covered:
                raise PlanError(f"the question names {item[1]} but the plan has no date in that year and the records are not from that year")
        else:
            _, d, mth, yr = item
            if not any(l[5:10] == f"{mth:02d}-{d:02d}" and (yr is None or l[:4] == yr) for l in lits):
                raise PlanError(f"the question names day {d} of month {mth} but the plan has no such date")


def describe(plan):
    """Plain words for the plan, written by code from the checked plan, not by the model."""
    o = R.onto().tables
    def nd(n):
        if "col" in n: return n["col"].replace("-june", "").replace("-", " ")
        if "lit" in n: return repr(n["lit"])
        if "ref" in n: return n["ref"]
        if "fn" in n: return f"{n['fn']}({', '.join(nd(a) for a in ([n['arg']] if 'arg' in n else n['args']))})"
        if "op" in n: return f" {n['op']} ".join(nd(a) for a in n["args"])
        if "agg" in n: return f"{n['agg'].replace('_', ' ')} of {n['arg'] if n['arg'] == '*' else nd(n['arg'])}"
        return "?"
    def cd(c):
        op = c["op"]
        if op in ("and", "or"): return "(" + f" {op} ".join(cd(x) for x in c["args"]) + ")"
        if op == "in": return f"{nd(c['arg'])} in {c['values']}"
        if op == "between": return f"{nd(c['arg'])} between {c['low']} and {c['high']}"
        if op in ("is_null", "not_null"): return f"{nd(c['arg'])} is {'' if op == 'is_null' else 'not '}empty"
        return f"{nd(c['args'][0])} {op} {nd(c['args'][1])}"
    parts = ["From " + o[plan["from"]]["label"] + " records"]
    for j in plan.get("joins", []):
        parts.append(f"{j.get('type', 'inner')}-join {o[j['table']]['label']} records on " + " and ".join(f"{nd(a)} = {nd(b)}" for a, b in j["on"]))
    if plan.get("where"): parts.append("keep rows where " + " and ".join(cd(c) for c in plan["where"]))
    if plan.get("group_by"): parts.append("group by " + ", ".join(nd(g) for g in plan["group_by"]))
    if plan.get("having"): parts.append("keep groups where " + " and ".join(cd(c) for c in plan["having"]))
    parts.append("report " + ", ".join(f"{s['as']} = {nd(s['expr'])}" for s in plan["select"]))
    if plan.get("order_by"): parts.append("sorted by " + ", ".join(f"{o_['by']} {o_.get('dir', 'asc')}" for o_ in plan["order_by"]))
    return "; ".join(parts) + "."


def run_plan(question, plan):
    """Check and run a plan. Returns a result dict like the resolver's."""
    if isinstance(plan, dict) and set(plan) == {"plans"}:
        return run_parts(question, plan["plans"])
    if isinstance(plan, dict) and set(plan) == {"cannot"}:
        return dict(decision="no_record", layers=["schema"], failed_layer="schema", message="I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).", trace=[], model_reason=str(plan["cannot"])[:200])
    try:
        sql, params, ctx = compile_plan(plan)
        date_check(question, ctx.dates, ctx.tables)
    except Exception as e:  # noqa: BLE001  fail closed: anything unexpected is a refusal, never an answer
        if not isinstance(e, PlanError):
            return dict(decision="no_record", layers=["schema"], failed_layer="schema", message=f"I can't answer this from Store 014's records: the plan could not be checked ({type(e).__name__}).", trace=[])
        return dict(decision="no_record", layers=[e.layer], failed_layer=e.layer, message=f"I can't answer this from Store 014's records: the {e.layer} layer refused the plan ({e}).", trace=[])
    cur = planner_db().execute(sql, params)
    cols = [d[0] for d in cur.description]; rows = cur.fetchall()
    used = "schema" if not plan.get("joins") and not any(k in json.dumps(plan) for k in ('"fn"', '"op": "/"', '"agg": "count_distinct"')) else "ontology"
    return dict(decision="answer", layers=[used], covers=str(plan.get("covers", ""))[:240], columns=cols, rows=[list(r) for r in rows[:50]], row_count=len(rows),
                sql=sql, params=params, plan_in_words=describe(plan), message=("No rows matched this plan. That is the records' answer to it, but check the plan in words below: an empty result is not the same as 'no'." if not rows else f"{len(rows)} row(s)."), value=(rows[0][0] if len(rows) == 1 and len(cols) == 1 else None), trace=[])


def registry_veto(question, r):
    """Layer 3, last: the knowledge layer. What the schema and ontology allowed is still refused when the registry says no record holds it."""
    hard, proxy = R.registry_layer(question)
    if hard:
        return dict(decision="no_record", layers=["registry"], failed_layer="registry", message="I can't answer this from Store 014's records: the knowledge layer says " + "; ".join(hard), trace=[])
    if proxy:
        r = {**r, "proxy_notes": proxy, "layers": r["layers"] + ["registry (stand-in noted)"]}
    return r


def answer_by_plan(question, planner):
    """One planner: layer 1 schema, layer 2 ontology, layer 3 registry."""
    plan = planner(question)
    if plan is None:
        return dict(decision="no_record", layers=["schema"], failed_layer="schema", message="I can't answer this from Store 014's records: no usable plan was returned.", trace=[])
    r = run_plan(question, plan)
    return registry_veto(question, r) if r["decision"] == "answer" else r


def _vals(row):
    out = set()
    for v in row:
        if v is None: continue
        out.add(round(float(v), 4) if isinstance(v, (int, float)) else str(v))
    return out


def agree(a, b):
    """Two answers agree when they have the same number of rows and, row by row, every value of the narrower row is in the wider row."""
    if a["row_count"] != b["row_count"]: return False
    for ra, rb in zip(sorted(a["rows"], key=lambda r: json.dumps(r, default=str)), sorted(b["rows"], key=lambda r: json.dumps(r, default=str))):
        va, vb = _vals(ra), _vals(rb)
        if not (va <= vb or vb <= va): return False
    return True


def answer_by_plans(question, planners):
    """Two or more independent planners. Each plan goes through the schema layer, then the ontology layer; the results must agree; the registry has the last word."""
    results = [run_plan(question, p) if (p := pl(question)) is not None and not isinstance(p, type(None)) else dict(decision="no_record", layers=["schema"], failed_layer="schema", message="no usable plan", trace=[]) for pl in planners]
    answered = [r for r in results if r["decision"] == "answer"]
    if len(answered) == len(results) and all(agree(answered[0], r) for r in answered[1:]):
        best = max(answered, key=lambda r: len(r["columns"]))
        return registry_veto(question, {**best, "planners_agreeing": len(answered)})
    hard, _ = R.registry_layer(question)
    if hard:   # whatever the planners did, the knowledge layer says no record holds it: say that, it is the real reason
        return dict(decision="no_record", layers=["registry"], failed_layer="registry", message="I can't answer this from Store 014's records: the knowledge layer says " + "; ".join(hard), trace=[])
    if not answered:
        first = results[0]; layer = first.get("failed_layer", "schema")
        return dict(decision="no_record", layers=[layer], failed_layer=layer, message=first["message"], trace=[], planners=len(results))
    why = f"only {len(answered)} of {len(results)} plans passed the schema and ontology layers" if len(answered) < len(results) else "the plans gave different results"
    return dict(decision="no_record", layers=["ontology"], failed_layer="agreement", message=f"I can't answer this from Store 014's records with confidence: {why}.", trace=[], answered=len(answered), planners=len(results))


LAST_ERROR = ""


def model_plan_raw(question):
    """Ask an OpenAI-compatible endpoint (NVIDIA or Gemini, chosen by BASE_URL, MODEL, KEY_ENV) for a plan. Returns the raw reply text or None."""
    global LAST_ERROR
    import os, time, requests
    base = os.environ.get("BASE_URL", "https://integrate.api.nvidia.com/v1"); model = os.environ["MODEL"]
    think_off = "nvidia" in base
    for attempt in range(4):
        try:
            body = {"model": model, "messages": [{"role": "user", "content": prompt_for(question)}], "temperature": 0, "max_tokens": 16000}
            if think_off: body["chat_template_kwargs"] = {"enable_thinking": False}
            r = requests.post(f"{base}/chat/completions", timeout=int(os.environ.get("TIMEOUT", "240")), headers={"Authorization": "Bearer " + os.environ[os.environ.get("KEY_ENV", "NVIDIA_API_KEY")]}, json=body)
            if r.status_code in (400, 422) and think_off: think_off = False; continue
            if r.status_code in (429, 503, 529): LAST_ERROR = f"HTTP {r.status_code}"; time.sleep(min(30, 5 * (attempt + 1))); continue
            if r.status_code >= 400: LAST_ERROR = f"HTTP {r.status_code}: {r.text[:200]}"; return None
            return r.json()["choices"][0]["message"].get("content") or ""
        except Exception as e:  # noqa: BLE001
            LAST_ERROR = f"{type(e).__name__}: {str(e)[:150]}"; time.sleep(3)
    return None


def run_parts(question, parts):
    """A question with several parts: every part is checked and run on its own. Parts that pass are answered; the rest are listed with the layer that refused them."""
    if not isinstance(parts, list) or not 1 <= len(parts) <= 4:
        return dict(decision="no_record", layers=["schema"], failed_layer="schema", message="I can't answer this from Store 014's records: the plan has no valid parts.", trace=[])
    out = [run_plan(question, p) for p in parts]
    ok = [r for r in out if r["decision"] == "answer"]
    if not ok:
        return out[0]
    return dict(decision="answer", layers=sorted({l for r in ok for l in r["layers"]}), parts=out, answered_parts=len(ok), total_parts=len(out), columns=ok[0]["columns"], rows=ok[0]["rows"], row_count=ok[0]["row_count"], message=f"{len(ok)} of {len(out)} part(s) answered.", trace=[])


def knowledge_notes(question):
    """Layer 3, the knowledge layer, as notes: what the records do not hold, and which stand-ins apply."""
    hard, proxy = R.registry_layer(question)
    return {"not_recorded": hard, "stand_ins": proxy}


def render(question, r):
    """The reply, written by code from the checked result. The model's words appear only as the labelled 'plan covers' note."""
    k = knowledge_notes(question)
    lines = []
    def table(res):
        if res["row_count"] == 0: return ["No rows matched."]
        cols = res["columns"]; out = []
        if res["row_count"] == 1 and len(cols) <= 6:
            out.append("; ".join(f"{c} = {v}" for c, v in zip(cols, res["rows"][0])))
        else:
            out.append(f"{res['row_count']} rows (columns: {', '.join(cols)}):")
            out += ["  " + " | ".join("" if v is None else str(v) for v in row) for row in res["rows"][:10]]
            if res["row_count"] > 10: out.append(f"  ... and {res['row_count'] - 10} more")
        return out
    if r["decision"] != "answer":
        lines.append(r["message"])
        if k["not_recorded"]: lines.append("Not recorded: " + "; ".join(k["not_recorded"]))
        return "\n".join(lines)
    parts = r.get("parts") or [r]
    for i, part in enumerate(parts, 1):
        head = f"Part {i}: " if len(parts) > 1 else ""
        if part["decision"] != "answer":
            lines.append(f"{head}not answered: {part['message'][38:]}")
            continue
        lines.append(f"{head}answered from the {'/'.join(part['layers'])} layer. " + (f"(Plan covers: {part['covers']})" if part.get("covers") else ""))
        lines += table(part)
        lines.append("  How it was found: " + part["plan_in_words"])
    if k["not_recorded"]: lines.append("Not recorded, so not answered: " + "; ".join(k["not_recorded"]))
    if k["stand_ins"]: lines.append("Stand-ins used (not the real thing): " + "; ".join(k["stand_ins"]))
    return "\n".join(lines)


def answer_cascade(question, planner):
    """Opus-style single planner. Schema, then ontology (inside the plan checks), then the knowledge layer as notes. A refusal says which layer could not help."""
    plan = planner(question)
    if plan is None:
        r = dict(decision="no_record", layers=["schema"], failed_layer="schema", message="I can't answer this from Store 014's records: no usable plan was returned.", trace=[])
    else:
        r = run_plan(question, plan)
    r["reply"] = render(question, r)
    return r
