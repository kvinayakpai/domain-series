"""Certified query catalogue: the only SQL that ever runs. A question that passes the guard is matched to exactly one reviewed
measure; the measure's SQL is fixed text with typed parameters (a sku, a category value, a time). The model writes no SQL.
Ambiguous or unmatched questions return no_record. Same question, same data -> same answer, byte for byte.
answer(question) -> {"decision": "answer"|"no_record"|"proxy", "value": ..., "measure": id, "sql": ..., "params": ...}
"""
import re
import sqlite3
import csv
from pathlib import Path

from guard import decide

DATA = Path(__file__).resolve().parents[2] / "public" / "data" / "india-grocery"
_DB = None


def db():
    global _DB
    if _DB is None:
        _DB = sqlite3.connect(":memory:")
        for f in sorted(DATA.glob("*.csv")):
            rows = list(csv.DictReader(open(f)))
            cols = list(rows[0])
            t = f.stem.replace("-", "_")
            _DB.execute(f'create table {t} ({", ".join(c + " text" for c in cols)})')
            _DB.executemany(f'insert into {t} values ({",".join("?" * len(cols))})', [[r[c] for c in cols] for r in rows])
    return _DB


def products():
    return [dict(sku=r[0], name=r[1], pack=r[2], price=float(r[3])) for r in db().execute("select sku,name,pack,price_inr from products")]


def find_sku(ql):
    """A product is named by words from its name (toned milk, sunflower oil, atta, rice) plus, where it comes in several sizes, the size
    (5 kg). The product with the most name words in the question wins; a tie, or no match, returns None: the question is refused."""
    norm = re.sub(r"(\d)\s*(kg|l|g|ml)\b", r"\1\2", ql)
    toks = set(re.findall(r"[a-z0-9]+", norm)) | {w.rstrip("s") for w in re.findall(r"[a-z0-9]+", norm)}
    scored = []
    for p in products():
        words = {w for w in re.findall(r"[a-z]+", p["name"].lower()) if w not in ("whole", "wheat", "pouch", "kg", "l", "g", "ml", "sona", "masoori")}
        sc = len(words & toks)
        if sc:
            scored.append((sc, p["sku"], re.sub(r"\s", "", p["pack"].lower())))
    if not scored:
        return None
    best = max(sc for sc, _, _ in scored)
    cands = [c for c in scored if c[0] == best]
    sized = [c for c in cands if c[2] in toks]
    if sized and len(sized) < len(cands):
        cands = sized
    return cands[0][1] if len(cands) == 1 else None


# measure = (id, full-match regex over the normalised question, sql, parameter builder). The whole question must match one template:
# an extra qualifier (a threshold, a grouping, a second filter) means no template matches and the question is refused.
def norm(q):
    ql = q.lower().strip()
    ql = re.sub(r"[?.]+$", "", ql)
    ql = re.sub(r",? in rupees\b", "", ql)
    ql = re.sub(r"\b(in|for|during) june 2026\b", "", ql)
    ql = re.sub(r"\b(at|by|from) store 014\b", "", ql)
    ql = re.sub(r"\bstore 014\b", "", ql)
    return re.sub(r"\s+", " ", ql).strip()


M = []


def measure(mid, pattern, sql, kind="plain"):
    M.append(dict(id=mid, pat=re.compile(pattern), sql=sql, kind=kind))


P = r"(?P<p>[a-z0-9 ]+?)"
measure("units_sold", rf"how many units of {P} were sold", "select sum(cast(units_sold as real)) from daily_sales_june where sku=?", "sku")
measure("bags_sold", rf"how many bags of {P} were sold", "select sum(cast(units_sold as real)) from daily_sales_june where sku=?", "sku")
measure("revenue_sku", rf"what was the total revenue from {P}", "select round(sum(cast(revenue_inr as real)),2) from daily_sales_june where sku=?", "sku")
measure("write_off_units", rf"how many units of {P} were written off", "select sum(cast(units as real)) from write_offs_june where sku=?", "sku")
measure("write_off_lines", r"how many write-?off lines had the reason '(?P<p>expired|damaged)'", "select count(*) from write_offs_june where reason=?", "text")
measure("write_off_units_reason", r"how many units were written off as (?P<p>expired|damaged)", "select sum(cast(units as real)) from write_offs_june where reason=?", "text")
measure("store_order_lines", rf"how many store order lines were created for {P}", "select count(*) from store_orders_june where sku=?", "sku")
measure("fresh_delivery_rows", rf"how many fresh-delivery rows are there for {P}", "select count(*) from fresh_deliveries_june where sku=?", "sku")
measure("goods_receipt_lines_sku", rf"how many goods-receipt lines were booked for {P}", "select count(*) from goods_receipts_june where sku_booked=?", "sku")
measure("goods_receipt_lines", r"how many goods-receipt lines were booked", "select count(*) from goods_receipts_june")
measure("forecast_rows_sku", rf"how many forecast rows are there for {P}", "select count(*) from forecasts_june where sku=?", "sku")
measure("shelf_on_shelf", rf"how many shelf-audit rows show {P} as on shelf", "select count(*) from shelf_audits_june where sku=? and status='on shelf'", "sku")
measure("shelf_empty_any", r"how many shelf-audit rows show a product as empty", "select count(*) from shelf_audits_june where status='empty'")
measure("shelf_rows", r"how many shelf-audit rows were recorded", "select count(*) from shelf_audits_june")
measure("refunds_total", r"how many upi refunds did make", "select count(*) from upi_refunds_june")
measure("refunds_complaint", r"how many upi refunds were triggered by a customer complaint", "select count(*) from upi_refunds_june where trigger='customer complaint'")
measure("refunds_amount", r"what was the total amount of upi refunds made", "select round(sum(cast(amount_inr as real)),2) from upi_refunds_june")
measure("refund_biggest", r"what was the biggest single upi refund", "select max(cast(amount_inr as real)) from upi_refunds_june")
measure("tender_status", r"how many (?P<t>cash|card|upi) payment attempts were (?P<s>approved|declined|failed)( at the tills)?", "select count(*) from pos_payments_june where tender=? and till_status=?", "tender")
measure("status_any_tender", r"how many payment attempts at the tills had the status (?P<s>approved|declined|failed)", "select count(*) from pos_payments_june where till_status=?", "status")
measure("attempts_total", r"how many payment attempts were recorded at the tills", "select count(*) from pos_payments_june")
measure("complaints_total", r"how many customer complaints about payments were logged|how many complaints were logged", "select count(*) from customer_complaints_june")
measure("complaints_debit_failed", r"how many complaints were about a debit while the till said failed", "select count(*) from customer_complaints_june where kind='debited but the till said failed'")
measure("complaints_charged_twice", r"how many complaints were about being charged twice", "select count(*) from customer_complaints_june where kind='charged twice'")
measure("shipments_before", r"how many shipments were dispatched before (?P<h>\d{1,2}):(?P<m>\d{2})", "select count(*) from shipments_june where substr(dispatched_ts,12,5) < ?", "time")
measure("shipments_total", r"how many (truck )?shipments arrived from the warehouse", "select count(*) from shipments_june")
measure("pallets_by_shipment", r"how many pallets did shipment (?P<p>shp-\d{6}) carry", "select pallets from shipments_june where shipment_id=?", "upper")
measure("pallets_total", r"how many pallets arrived from the warehouse", "select count(*) from pallets_june")
measure("settlement_days", r"on how many days did receive a upi settlement|how many upi settlements did receive", "select count(distinct settlement_date) from upi_settlements_june")
measure("largest_net_settlement", r"what was the largest net upi settlement received in a single day", "select max(cast(net_inr as real)) from upi_settlements_june")
measure("net_settled_total", r"what was the total net upi amount settled to", "select round(sum(cast(net_inr as real)),2) from upi_settlements_june")
measure("shipping_notice_units", r"what was the total number of units on the shipping notices", "select sum(cast(units as real)) from shipping_notice_lines_june")
measure("avg_selling_price", r"what is the average selling price across all of 's products", "select round(avg(cast(price_inr as real)),2) from products")
measure("selling_price_sku", rf"what is the selling price of {P}", "select price_inr from products where sku=?", "sku")
measure("stock_counts_trigger", r"how many stock counts were triggered by a manager's request after complaints", "select count(*) from stock_counts_june where trigger='manager request after complaints'")
measure("stock_count_diffs", r"how many stock counts found a difference between book and counted stock", "select count(*) from stock_counts_june where cast(adjustment as real) != 0")
measure("psp_failed", r"how many transactions in the upi service provider's report have the status (?P<p>failed|success|returned)", "select count(*) from psp_upi_report_june where status=?", "text")
measure("bills_rung", r"how many bills did ring up", "select count(distinct bill_id) from pos_lines_may_june where bill_ts >= '2026-06-01' and bill_ts < '2026-07-01'")
measure("units_ordered", r"how many units in total did order from the warehouse", "select sum(cast(units as real)) from store_orders_june")
measure("product_count", r"how many products does sell in these records", "select count(*) from products")
measure("revenue_from", rf"what was the revenue from {P}", "select round(sum(cast(revenue_inr as real)),2) from daily_sales_june where sku=?", "sku")
measure("distinct_orders", r"how many distinct store orders .* were sent to the warehouse", "select count(distinct order_id) from store_orders_june")
measure("distinct_bills", r"how many distinct bills were rung up at the tills", "select count(distinct bill_id) from pos_lines_may_june where bill_ts >= '2026-06-01' and bill_ts < '2026-07-01'")


def answer(question):
    g = decide(question)
    if g["decision"] != "pass":
        return {"decision": g["decision"], "reasons": g["reasons"]}
    ql = norm(question)
    hits = [(m, m["pat"].fullmatch(ql)) for m in M if m["pat"].fullmatch(ql)]
    if len(hits) != 1:
        return {"decision": "no_record", "reasons": [f"{len(hits)} certified templates match the whole question; exactly one is required"]}
    m, mm = hits[0]
    kind = m["kind"]
    if kind == "sku":
        sku = find_sku(mm.group("p"))
        if sku is None:
            return {"decision": "no_record", "reasons": ["the product is not named uniquely"]}
        params = (sku,)
    elif kind == "text":
        params = (mm.group("p"),)
    elif kind == "upper":
        params = (mm.group("p").upper(),)
    elif kind == "tender":
        params = ({"upi": "UPI"}.get(mm.group("t"), mm.group("t")), mm.group("s"))
    elif kind == "status":
        params = (mm.group("s"),)
    elif kind == "time":
        params = ("%02d:%s" % (int(mm.group("h")), mm.group("m")),)
    else:
        params = ()
    value = db().execute(m["sql"], params).fetchone()[0]
    if isinstance(value, float) and value == int(value) and "round" not in m["sql"] and "max(" not in m["sql"]:
        value = int(value)
    return {"decision": "answer", "measure": m["id"], "value": value, "sql": m["sql"], "params": params}


if __name__ == "__main__":
    import sys
    print(answer(" ".join(sys.argv[1:])))
