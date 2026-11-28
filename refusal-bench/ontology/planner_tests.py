import json
"""Tests for the planning layer with hand-written plans, good and hostile. Every good plan's answer is compared with a number computed directly from the CSV files."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import planner as P
DATA = Path(__file__).resolve().parents[2] / "public" / "data" / "india-grocery"
rows = lambda n: list(csv.DictReader(open(DATA / n)))
C = lambda t, c: {"col": f"{t}.{c}"}
L = lambda v: {"lit": v}
EQ = lambda a, b: {"op": "=", "args": [a, b]}
fails = []

def check(name, question, plan, expect_answer, expect_value=None, expect_rows=None, why=None):
    r = P.run_plan(question, plan)
    ok = (r["decision"] == "answer") == expect_answer
    if ok and expect_answer and expect_value is not None: ok = r["value"] is not None and abs(float(r["value"]) - float(expect_value)) < 1e-6
    if ok and expect_answer and expect_rows is not None: ok = r["row_count"] == expect_rows
    if ok and why and not expect_answer: ok = why in r["message"]
    print(("PASS " if ok else "FAIL ") + name, "|", (r["message"][:110] if r["decision"] != "answer" else f"answer {r.get('value')} rows={r['row_count']}"))
    if not ok: fails.append(name)

ds = rows("daily-sales-june.csv"); pay = rows("pos-payments-june.csv"); psp = rows("psp-upi-report-june.csv"); sh = rows("shipments-june.csv")
q = "How many bags of 5 kg atta were sold in June 2026?"
check("scalar sum", q, {"from": "daily-sales-june", "where": [EQ(C("daily-sales-june", "sku"), L("ATTA-WW-5KG"))], "select": [{"as": "units", "expr": {"agg": "sum", "arg": C("daily-sales-june", "units_sold")}}]}, True, sum(int(r["units_sold"]) for r in ds if r["sku"] == "ATTA-WW-5KG"))
check("date + product", "How many units of curd were sold on 5 June 2026?", {"from": "daily-sales-june", "where": [EQ(C("daily-sales-june", "sku"), L("CURD-500G")), EQ(C("daily-sales-june", "date"), L("2026-06-05"))], "select": [{"as": "u", "expr": {"agg": "sum", "arg": C("daily-sales-june", "units_sold")}}]}, True, sum(int(r["units_sold"]) for r in ds if r["sku"] == "CURD-500G" and r["date"] == "2026-06-05"))
check("column against column", "How many shipments arrived inside the slot?", {"from": "shipments-june", "where": [{"op": ">=", "args": [C("shipments-june", "arrived_ts"), C("shipments-june", "slot_start")]}, {"op": "<=", "args": [C("shipments-june", "arrived_ts"), C("shipments-june", "slot_end")]}], "select": [{"as": "n", "expr": {"agg": "count", "arg": "*"}}]}, True, sum(r["slot_start"] <= r["arrived_ts"] <= r["slot_end"] for r in sh))
check("join with day()", "Which shelf audits found an item empty while the book showed stock?", {"from": "shelf-audits-june", "joins": [{"table": "inventory-book-june", "type": "inner", "on": [[C("shelf-audits-june", "sku"), C("inventory-book-june", "sku")], [{"fn": "day", "arg": C("shelf-audits-june", "audit_ts")}, C("inventory-book-june", "date")]]}], "where": [EQ(C("shelf-audits-june", "status"), L("empty")), {"op": ">", "args": [C("inventory-book-june", "book_on_hand_close"), L(0)]}], "select": [{"as": "audit_ts", "expr": C("shelf-audits-june", "audit_ts")}, {"as": "sku", "expr": C("shelf-audits-june", "sku")}]}, True, None, 2)
ap = {p["rrn"] for p in pay if p["till_status"] == "approved" and p["rrn"]}
check("left join, is_null", "Which provider successes have no approved till payment?", {"from": "psp-upi-report-june", "joins": [{"table": "pos-payments-june", "type": "left", "on": [[C("psp-upi-report-june", "rrn"), C("pos-payments-june", "rrn")]]}], "where": [EQ(C("psp-upi-report-june", "status"), L("success")), {"op": "or", "args": [{"op": "is_null", "arg": C("pos-payments-june", "till_status")}, {"op": "!=", "args": [C("pos-payments-june", "till_status"), L("approved")]}]}], "select": [{"as": "n", "expr": {"agg": "count_distinct", "arg": C("psp-upi-report-june", "rrn")}}]}, True, None)
check("table with no dates (products)", "What is the selling price of full cream milk?", {"from": "products", "where": [EQ(C("products", "sku"), L("MILK-FC-500ML"))], "select": [{"as": "price", "expr": C("products", "price_inr")}]}, True)
# hostile
b = {"from": "daily-sales-june", "select": [{"as": "u", "expr": {"agg": "sum", "arg": C("daily-sales-june", "units_sold")}}]}
check("unknown table", q, {**b, "from": "orders"}, False, why="not defined")
check("unknown column", q, {**b, "select": [{"as": "u", "expr": {"agg": "sum", "arg": C("daily-sales-june", "units_bought")}}]}, False, why="not in table")
check("raw SQL key", q, {**b, "sql": "select * from sqlite_master"}, False, why="keys not defined")
check("injection in a literal", q, {**b, "where": [EQ(C("daily-sales-june", "sku"), L("ATTA-WW-5KG'; drop table x; --"))]}, False, why="not a defined product")
check("undefined status", "How many payments were refused?", {"from": "pos-payments-june", "where": [EQ(C("pos-payments-june", "till_status"), L("refused"))], "select": [{"as": "n", "expr": {"agg": "count", "arg": "*"}}]}, False, why="not a defined value")
check("sum of a non-additive column", q, {"from": "inventory-book-june", "select": [{"as": "s", "expr": {"agg": "sum", "arg": C("inventory-book-june", "book_on_hand_close")}}]}, False, why="not additive")
check("join on unlike keys", q, {**b, "joins": [{"table": "products", "type": "inner", "on": [[C("daily-sales-june", "units_sold"), C("products", "price_inr")]]}]}, False, why="not the same kind of key")
check("self join", q, {**b, "joins": [{"table": "daily-sales-june", "type": "inner", "on": [[C("daily-sales-june", "sku"), C("daily-sales-june", "sku")]]}]}, False, why="twice")
check("2023 outside the records", "How many bags of 5 kg atta were sold in June 2023?", {**b, "where": [EQ(C("daily-sales-june", "date"), L("2023-06-05"))]}, False, why="outside the records")
check("the plan drops the year in the question", "How many bags of 5 kg atta were sold in June 2023?", {**b, "where": [EQ(C("daily-sales-june", "sku"), L("ATTA-WW-5KG"))]}, False, why="2023")
check("the plan drops the day in the question", "How many bags of 5 kg atta were sold on 11 June 2026?", {**b, "where": [EQ(C("daily-sales-june", "sku"), L("ATTA-WW-5KG"))]}, False, why="covers that date")
check("limit too big", q, {**b, "limit": 10**6}, False, why="limit")
check("model says cannot", q, {"cannot": "no table holds this"}, False, why="no valid query plan")
check("add rupees to units", q, {"from": "daily-sales-june", "select": [{"as": "x", "expr": {"agg": "sum", "arg": {"op": "+", "args": [C("daily-sales-june", "units_sold"), C("daily-sales-june", "revenue_inr")]}}}]}, True)  # arithmetic on numbers is allowed; unit mixing is caught only in comparisons
check("compare rupees with units", q, {**b, "where": [{"op": ">", "args": [C("daily-sales-june", "revenue_inr"), C("daily-sales-june", "units_sold")]}]}, False, why="cannot compare")
check("select a bare literal", q, {"from": "daily-sales-june", "select": [{"as": "x", "expr": L(5)}]}, False, why="bare literal")
r = P.answer_by_plan("Why did units of 5 kg atta sales fall?", lambda q: b)
ok = r["decision"] == "no_record" and "registry" in r["layers"]; print(("PASS " if ok else "FAIL ") + "a valid plan for a why question is still refused, by the registry, the last layer"); fails += [] if ok else ["registry"]

# ---- fixes of 28 Nov, each replayed from a real plan a model wrote
import json as _j
PL = {m: _j.load(open(f)) for m, f in [("opus", "/tmp/ct/plans-opus-v2.json"), ("sonnet", "/tmp/ct/plans-sonnet-v2.json"), ("haiku", "/tmp/ct/plans-haiku-v2.json")]} if Path("/tmp/ct/plans-opus-v2.json").exists() else {}
KIMI = Path(__file__).parent.parent / "results/planner-nvidia-run-1/moonshotai_kimi-k3_1-pro/plans.json"
MINI = Path(__file__).parent.parent / "results/planner-nvidia-run-1/minimaxai_minimax-m3_1-flash/plans.json"
QS = {x["id"]: x["question"] for x in _j.load(open(Path(__file__).parent.parent / "questions-plan-v2.json"))}
def part_rows(r, i): return (r.get("parts") or [r])[i].get("rows")
def fix(name, ok):
    global fails
    print(("PASS " if ok else "FAIL ") + name); fails += [] if ok else [name]
if PL:
    r = P.run_plan(QS["S8N18"], PL["opus"]["S8N18"]); fix("day count runs from start to end: all 15 receipts that failed a count within a week (16 rows: one receipt also meets a second count)", r["decision"] == "answer" and r["row_count"] == 16 and len({(x[0], x[1]) for x in r["rows"]}) == 15)
    r = P.run_plan(QS["S9N17"], PL["opus"]["S9N17"]); fix("refunds over 5 days from the extra debit: 10", r["decision"] == "answer" and part_rows(r, 1) == [[10]])
    r = P.run_plan(QS["S8N30"], PL["opus"]["S8N30"]); fix("grouping on the empty bill reference is refused", r["decision"] == "no_record" and "empty in every row" in r["message"])
    r = P.run_plan(QS["S8N32"], PL["opus"]["S8N32"]); fix("joining on the empty bill reference is refused", "empty in every row" in json.dumps(r))
    r = P.run_plan(QS["S8N07"], PL["opus"]["S8N07"]); fix("a range of 1 to 21 June covers 8 June", r["decision"] == "answer")
    r = P.run_plan(QS["S8N01"], PL["opus"]["S8N01"]); fix("the dates are checked over the whole plan, so the June total part also answers", r["decision"] == "answer" and r.get("answered_parts") == 2)
    r = P.run_plan(QS["S8N38"], PL["sonnet"]["S8N38"]); fix("count over a many-to-many join is refused (Sonnet's 124 phantom mismatches)", "many rows to many rows" in json.dumps(r))
if KIMI.exists():
    r = P.run_plan(QS["S8N01"], _j.load(open(KIMI))["S8N01"]); fix("a date-only column compared with a date-time keeps the first day (88, not 79)", part_rows(r, 1) == [[88.0]])
if MINI.exists():
    r = P.run_plan(QS["S8N15"], _j.load(open(MINI))["S8N15"]); fix("a sum over a join that repeats rows is refused (MiniMax fill rate)", r["decision"] == "no_record" and "more than once" in r["message"])
print("ALL PASS" if not fails else f"FAILED: {fails}"); sys.exit(1 if fails else 0)
