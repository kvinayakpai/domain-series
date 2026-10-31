"""June at Store 014 on one map: which records copy each other, which observe the world, and what
joining them across the shelf, the truck and the money finds. Scored against the answer keys.

Reads the downloadable records in public/data/india-grocery and the three analyses' outputs
(retail-ai.json, logistics-ai.json, payments-ai.json), and writes src/data/finale.json, which the
finale post quotes:

  1. joins: twelve joins between June's records, and how often each pair agrees. A join that always
     agrees is a copy: one record was written from the other, or both from one event, and a data
     test on it can only pass. A join that sometimes disagrees has an observation of the world on
     at least one side.
  2. the map: the records as nodes, the joins as edges, what each record looks at in the world, and
     the KPIs that read each record.
  3. the trace: on Tuesday 23 June at 20:00, a silence at the store followed across the map to the
     warehouse. Scored against the answer key.
  4. incidents: June's three failures, when each harm began, when two records first disagreed about
     it, when the store found it, what it cost, and what the ledger showed.
  5. agents: the scripted assistants and the replenishment agent across the series.

Everything in 1 and 3 is computed from the records alone; the answer keys are read only to score.
Parts 4 and 5 gather numbers the three analyses and the world's export already computed.

    python3 scripts/analysis/finale.py

Needs duckdb and pandas.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public" / "data" / "india-grocery"
SRC = ROOT / "src" / "data"
OUT = SRC / "finale.json"
MAP_OUT = DATA / "store-014-map.json"  # the map as data, for anyone building a domain layer

HERO, ONE_KG = "ATTA-WW-5KG", "ATTA-WW-1KG"
TRACE_AT = "2026-06-23T20:00"  # Tuesday evening: the store's silence flag on 5 kg atta

TABLES = {
    "till_lines": ("pos-lines-may-june.csv", {"gtin_scanned": "VARCHAR"}),
    "book": ("inventory-book-june.csv", {}),
    "daily_sales": ("daily-sales-june.csv", {}),
    "shelf_audits": ("shelf-audits-june.csv", {}),
    "stock_counts": ("stock-counts-june.csv", {}),
    "write_offs": ("write-offs-june.csv", {}),
    "fresh": ("fresh-deliveries-june.csv", {}),
    "picks": ("dc-pick-confirmations-june.csv", {}),
    "notice": ("shipping-notice-lines-june.csv", {"sscc": "VARCHAR", "gtin": "VARCHAR"}),
    "pallets": ("pallets-june.csv", {"sscc": "VARCHAR"}),
    "receipts": ("goods-receipts-june.csv", {"sscc": "VARCHAR"}),
    "dc_corrections": ("dc-stock-adjustments-june.csv", {}),
    "till_payments": ("pos-payments-june.csv", {"rrn": "VARCHAR", "note": "VARCHAR"}),
    "provider": ("psp-upi-report-june.csv", {"rrn": "VARCHAR", "bill_ref": "VARCHAR"}),
    "settlements": ("upi-settlements-june.csv", {}),
    "refunds": ("upi-refunds-june.csv", {"rrn": "VARCHAR"}),
    "complaints": ("customer-complaints-june.csv", {"rrn": "VARCHAR"}),
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name, (file, types) in TABLES.items():
        opt = f", types={json.dumps(types).replace(chr(34), chr(39))}" if types else ""
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('{DATA / file}'{opt})")
    return con


def rows(con, sql: str) -> list[dict]:
    return json.loads(con.execute(sql).df().to_json(orient="records", date_format="iso"))


def one(con, sql: str) -> dict:
    return rows(con, sql)[0]


def hours(a: str, b: str) -> float:
    return (datetime.fromisoformat(b[:16]) - datetime.fromisoformat(a[:16])).total_seconds() / 3600


def load(name: str) -> dict:
    return json.loads((SRC / name).read_text())


# ---------- 1. joins ----------
# Each join returns compared (rows it can compare) and agree (rows where the two records agree).
# The sql is shown in the post's companion material as written here.
JOINS = [
    # The truck.
    {"id": "picks-notice", "domain": "truck", "a": "picks", "b": "notice",
     "how": "shipment and line: item and cases",
     "sql": ("SELECT count(*) AS compared, sum(CASE WHEN p.sku = n.sku AND p.cases_confirmed = n.cases THEN 1 ELSE 0 END) AS agree "
             "FROM picks p JOIN notice n USING (shipment_id, line)")},
    {"id": "notice-labels", "domain": "truck", "a": "notice", "b": "labels",
     "how": "pallet (SSCC): cases",
     "sql": ("SELECT count(*) AS compared, sum(CASE WHEN n.cases = p.cases THEN 1 ELSE 0 END) AS agree "
             "FROM (SELECT sscc, sum(cases) AS cases FROM notice GROUP BY sscc) n JOIN pallets p USING (sscc)")},
    {"id": "notice-receipts", "domain": "truck", "a": "notice", "b": "receipts",
     "how": "shipment and line: item and units",
     "sql": ("SELECT count(*) AS compared, sum(CASE WHEN r.sku_booked = n.sku AND r.units_booked = n.units THEN 1 ELSE 0 END) AS agree "
             "FROM receipts r JOIN notice n ON r.shipment_id = n.shipment_id AND r.line = n.line")},
    {"id": "receipts-counts", "domain": "truck", "a": "receipts", "b": "counts",
     "how": "item: the last receipt before each count survives it",
     "sql": ("WITH pairs AS (SELECT c.count_ts, c.sku, c.adjustment, r.units_booked, "
             "row_number() OVER (PARTITION BY c.count_ts, c.sku ORDER BY r.received_ts DESC) AS k "
             "FROM stock_counts c JOIN receipts r ON r.sku_booked = c.sku AND r.received_ts < c.count_ts) "
             "SELECT count(*) AS compared, sum(CASE WHEN adjustment > -0.5 * units_booked THEN 1 ELSE 0 END) AS agree "
             "FROM pairs WHERE k = 1")},
    # The shelf.
    {"id": "book-ledger", "domain": "shelf", "a": "book", "b": "lines",
     "how": "item and day: yesterday's book, plus receipts and deliveries, minus sales and write-offs, plus counts",
     "sql": ("WITH inflow AS (SELECT CAST(received_ts AS DATE) AS date, sku_booked AS sku, sum(units_booked) AS u FROM receipts GROUP BY ALL "
             "UNION ALL SELECT CAST(delivery_ts AS DATE), sku, sum(units) FROM fresh GROUP BY ALL), "
             "adj AS (SELECT CAST(count_ts AS DATE) AS date, sku, sum(adjustment) AS a FROM stock_counts "
             "WHERE strftime(count_ts, '%H:%M') < '22:00' GROUP BY ALL "
             "UNION ALL SELECT CAST(count_ts AS DATE) + 1, sku, sum(adjustment) FROM stock_counts "
             "WHERE strftime(count_ts, '%H:%M') >= '22:00' GROUP BY ALL), "
             "d AS (SELECT b.date, b.sku, b.book_on_hand_close AS book, "
             "lag(b.book_on_hand_close) OVER (PARTITION BY b.sku ORDER BY b.date) AS prev, "
             "coalesce((SELECT sum(u) FROM inflow i WHERE i.date = b.date AND i.sku = b.sku), 0) AS inflow, "
             "coalesce((SELECT sum(units_sold) FROM daily_sales s WHERE s.date = b.date AND s.sku = b.sku), 0) AS sold, "
             "coalesce((SELECT sum(units) FROM write_offs w WHERE w.date = b.date AND w.sku = b.sku), 0) AS written_off, "
             "coalesce((SELECT sum(a) FROM adj WHERE adj.date = b.date AND adj.sku = b.sku), 0) AS counted "
             "FROM book b) "
             "SELECT count(*) AS compared, sum(CASE WHEN book = prev + inflow - sold - written_off + counted THEN 1 ELSE 0 END) AS agree "
             "FROM d WHERE prev IS NOT NULL")},
    {"id": "book-counts", "domain": "shelf", "a": "book", "b": "counts",
     "how": "item: the books against a count of shelf and backroom",
     "sql": "SELECT count(*) AS compared, sum(CASE WHEN adjustment = 0 THEN 1 ELSE 0 END) AS agree FROM stock_counts"},
    {"id": "book-audits", "domain": "shelf", "a": "book", "b": "audits",
     "how": "item and hour: stock on the books against a look at the shelf",
     "sql": ("WITH a AS (SELECT audit_ts, sku, status, CAST(audit_ts AS DATE) AS date FROM shelf_audits), "
             "b AS (SELECT a.*, "
             "coalesce((SELECT book_on_hand_close FROM book k WHERE k.sku = a.sku AND k.date = a.date - 1), 0) "
             "+ coalesce((SELECT sum(units_booked) FROM receipts r WHERE r.sku_booked = a.sku AND CAST(r.received_ts AS DATE) = a.date AND r.received_ts <= a.audit_ts), 0) "
             "+ coalesce((SELECT sum(units) FROM fresh f WHERE f.sku = a.sku AND CAST(f.delivery_ts AS DATE) = a.date AND f.delivery_ts <= a.audit_ts), 0) "
             "- coalesce((SELECT sum(qty) FROM till_lines l WHERE l.sku_scanned = a.sku AND CAST(l.bill_ts AS DATE) = a.date AND l.bill_ts <= a.audit_ts), 0) "
             "+ coalesce((SELECT sum(adjustment) FROM stock_counts c WHERE c.sku = a.sku AND CAST(c.count_ts AS DATE) = a.date AND c.count_ts <= a.audit_ts), 0) "
             "AS book_at_audit FROM a) "
             "SELECT count(*) AS compared, sum(CASE WHEN (status = 'empty') = (book_at_audit <= 0) THEN 1 ELSE 0 END) AS agree FROM b")},
    # Across the shelf and the money: one checkout writes both.
    {"id": "lines-payments", "domain": "shelf-money", "a": "lines", "b": "payments",
     "how": "bill: every bill on the till lines has one approved payment",
     "sql": ("SELECT count(*) AS compared, sum(CASE WHEN approved = 1 THEN 1 ELSE 0 END) AS agree FROM "
             "(SELECT l.bill_id, (SELECT count(*) FROM till_payments p WHERE p.bill_id = l.bill_id AND p.till_status = 'approved') AS approved "
             "FROM (SELECT DISTINCT bill_id FROM till_lines WHERE bill_ts >= '2026-06-01') l)")},
    # The money.
    {"id": "payments-provider", "domain": "money", "a": "payments", "b": "provider",
     "how": "RRN: approved UPI payments against the provider's status and amount",
     "sql": ("SELECT count(*) AS compared, sum(CASE WHEN p.status = 'success' AND p.amount_inr = t.amount_inr THEN 1 ELSE 0 END) AS agree "
             "FROM till_payments t LEFT JOIN provider p USING (rrn) WHERE t.tender = 'UPI' AND t.till_status = 'approved'")},
    {"id": "timeouts-provider", "domain": "money", "a": "payments", "b": "provider",
     "how": "amount and time: timeouts against the provider's final status",
     "sql": None},  # the payments analysis's matcher; read from payments-ai.json below
    {"id": "provider-settlements", "domain": "money", "a": "provider", "b": "settlements",
     "how": "day: each settlement against the previous day's successes",
     "sql": ("WITH s AS (SELECT CAST(status_ts AS DATE) + 1 AS settlement_date, count(*) AS credits, round(sum(amount_inr), 2) AS gross "
             "FROM provider WHERE status = 'success' GROUP BY ALL) "
             "SELECT count(*) AS compared, sum(CASE WHEN x.upi_credits = coalesce(s.credits, 0) AND abs(x.gross_inr - coalesce(s.gross, 0)) <= 0.01 "
             "THEN 1 ELSE 0 END) AS agree FROM settlements x LEFT JOIN s USING (settlement_date)")},
    {"id": "provider-refunds", "domain": "money", "a": "provider", "b": "refunds",
     "how": "RRN: each refund names a success for the same amount",
     "sql": ("SELECT count(*) AS compared, sum(CASE WHEN p.status = 'success' AND p.amount_inr = r.amount_inr THEN 1 ELSE 0 END) AS agree "
             "FROM refunds r LEFT JOIN provider p USING (rrn)")},
]

# What each record is, what writes it, and what in the world it looks at. "part" means it sees the
# thing only sometimes or only in part; a record with nothing here repeats what other records say.
RECORDS = {
    "picks": {"name": "Pick confirmations", "domain": "truck", "file": "dc-pick-confirmations-june.csv",
              "written_by": "a scan of the slot's label as the picker takes the cases", "looks_at": {"slot": "part"},
              "sees": "where the picker stood, not what they took"},
    "notice": {"name": "Shipping notice", "domain": "truck", "file": "shipping-notice-lines-june.csv",
               "written_by": "the warehouse system, from the pick confirmations", "looks_at": {}},
    "labels": {"name": "Pallet labels", "domain": "truck", "file": "pallets-june.csv",
               "written_by": "the warehouse system, from the notice; no pallet was weighed", "looks_at": {}},
    "receipts": {"name": "Goods receipts", "domain": "shelf", "file": "goods-receipts-june.csv",
                 "written_by": "a scan of the pallet label at the store, matched to the notice", "looks_at": {}},
    "corrections": {"name": "Warehouse corrections", "domain": "truck", "file": "dc-stock-adjustments-june.csv",
                    "written_by": "a count of a warehouse slot", "looks_at": {"slot": "all"},
                    "sees": "what is left in a slot"},
    "book": {"name": "Book stock", "domain": "shelf", "file": "inventory-book-june.csv",
             "written_by": "the store's system, from receipts, sales, write-offs and counts", "looks_at": {}},
    "lines": {"name": "Till lines", "domain": "shelf", "file": "pos-lines-may-june.csv",
              "written_by": "a scan of each item at the till", "looks_at": {"shelf": "part"},
              "sees": "a sale proves the item was there; no sale proves nothing"},
    "counts": {"name": "Stock counts", "domain": "shelf", "file": "stock-counts-june.csv",
               "written_by": "staff counting the shelf and the backroom", "looks_at": {"shelf": "all", "backroom": "all"},
               "sees": "what is on the shelf and in the backroom"},
    "audits": {"name": "Shelf audits", "domain": "shelf", "file": "shelf-audits-june.csv",
               "written_by": "a person looking at the shelf", "looks_at": {"shelf": "all"},
               "sees": "whether the shelf has the item"},
    "payments": {"name": "Till payments", "domain": "money", "file": "pos-payments-june.csv",
                 "written_by": "the till: the provider's answer, or its own timeout", "looks_at": {}},
    "provider": {"name": "Provider's UPI report", "domain": "money", "file": "psp-upi-report-june.csv",
                 "written_by": "UPI's final status for every payment", "looks_at": {"customer_account": "all", "store_account": "all"},
                 "sees": "whether the customer was debited and the store credited"},
    "settlements": {"name": "Settlements", "domain": "money", "file": "upi-settlements-june.csv",
                    "written_by": "the store's bank, from the provider's successes", "looks_at": {}},
    "refunds": {"name": "Refunds", "domain": "money", "file": "upi-refunds-june.csv",
                "written_by": "the store, after a complaint", "looks_at": {}},
    "complaints": {"name": "Complaints", "domain": "money", "file": "customer-complaints-june.csv",
                   "written_by": "a customer calling the store", "looks_at": {"customer_account": "part"},
                   "sees": "a customer's account, if they call"},
}
THINGS = {
    "slot": "A warehouse slot",
    "pallet": "What is on a pallet",
    "shelf": "The shelf",
    "backroom": "The backroom",
    "customer_account": "The customer's bank account",
    "store_account": "The store's bank account",
}
# The headline KPI of each domain post: the record it reads, and the observations that can contradict
# it. src/lib/kpis.ts (and /kpis/domain-kpis.yaml) has all eighteen, with their blind spots.
KPIS = [
    {"id": "osa", "name": "On-shelf availability", "reads": ["book"], "contradicted_by": ["audits", "counts", "lines"],
     "rule": "Book stock is a belief. When an item stops selling while the books show stock, ask for a shelf check."},
    {"id": "otif", "name": "On time, in full (OTIF)", "reads": ["receipts", "notice"], "contradicted_by": ["counts", "corrections"],
     "rule": "A receipt booked by scanning a pallet label is a copy of the notice. Check it against the next count."},
    {"id": "success-rate", "name": "Payment success rate", "reads": ["payments"], "contradicted_by": ["provider"],
     "rule": "A timeout is a question, not a failure. Match it to the provider's final status before calling it failed."},
]
RULES = [
    "Before acting on a KPI, find the record it reads. If that record is a copy, find an observation that can contradict it, and join it.",
    "A join that has never disagreed is a copy. A test on it can only pass.",
    "Silence and timeouts are questions: no sale while the books show stock, and no answer from the bank, are not zeros.",
    "When an observation disagrees, follow the copies back to the event that wrote them, across departments.",
    "Name the things no record looks at. In June at Store 014, nothing looked at what was on a pallet.",
]
# The KPIs that read each record, as they are usually computed (src/lib/kpis.ts has the full list).
READS = {
    "notice": [("otif", "OTIF, the warehouse's report")],
    "receipts": [("otif", "OTIF, the store's scorecard")],
    "book": [("osa", "On-shelf availability")],
    "lines": [("forecast", "Forecast accuracy")],
    "payments": [("success-rate", "Payment success rate")],
}


def disagreeing_audits(con) -> list[dict]:
    """The shelf audits that disagree with the books: the join's own rows."""
    sql = next(j["sql"] for j in JOINS if j["id"] == "book-audits")
    body = sql[: sql.rindex("SELECT count(*)")]
    return rows(con, body + "SELECT audit_ts, sku, status, book_at_audit FROM b WHERE (status = 'empty') <> (book_at_audit <= 0) ORDER BY audit_ts")


def joins(con, pai: dict) -> list[dict]:
    out = []
    for j in JOINS:
        if j["sql"] is None:
            m = pai["matcher"]
            r = {"compared": m["timeouts"], "agree": m["outcomes"]["never debited"]}
        else:
            r = one(con, j["sql"])
        compared, agree = int(r["compared"]), int(r["agree"] or 0)
        out.append({k: j[k] for k in ("id", "domain", "a", "b", "how")} | {
            "sql": j["sql"], "compared": compared, "agree": agree, "share": round(agree / compared, 4),
            "kind": "copy" if agree == compared else "observation"})
    return out


# ---------- 3. the trace ----------
TRACE_SQL = f"""
WITH silent AS (                       -- the store: no 5 kg sale since 16:00, with 63 on the books
  SELECT '{HERO}' AS sku, TIMESTAMP '{TRACE_AT}' AS at),
receipt AS (                           -- the books: the last receipt of the item before the silence
  SELECT r.* FROM receipts r, silent s WHERE r.sku_booked = s.sku AND r.received_ts <= s.at
  ORDER BY r.received_ts DESC LIMIT 1),
line AS (                              -- the receipt copied the notice; the notice copied the pick
  SELECT p.pick_ts, p.shipment_id, p.line, p.sku, p.slot, p.cases_confirmed, p.confirmed_by, n.sscc, n.units
  FROM picks p JOIN notice n USING (shipment_id, line) JOIN receipt r USING (shipment_id, line)),
nearby AS (                            -- the warehouse: corrections in the same aisle and bay since the pick
  SELECT c.* FROM dc_corrections c, line l, silent s
  WHERE c.adjusted_ts BETWEEN l.pick_ts AND s.at AND split_part(c.slot, '-', 1) || split_part(c.slot, '-', 2)
        = split_part(l.slot, '-', 1) || split_part(l.slot, '-', 2) AND c.slot <> l.slot)
SELECT l.shipment_id, l.line, l.sscc, l.sku AS noticed_sku, l.units AS noticed_units, l.cases_confirmed,
       l.slot AS pick_slot, l.confirmed_by, l.pick_ts, r.grn_id, r.received_ts, r.receipt_method,
       c.adjusted_ts, c.sku AS short_sku, c.slot AS short_slot, c.cases AS short_cases, c.units AS short_units,
       c.reason
FROM line l, receipt r, nearby c WHERE c.cases = -l.cases_confirmed
"""


def trace(con, lai: dict, key_logistics: dict) -> dict:
    hit = rows(con, TRACE_SQL)
    assert len(hit) == 1, hit
    h = hit[0]
    silence = next(t for t in lai["tests"]["domain"] if t["name"].startswith("No item goes longer"))["failing"][0]
    truth = next(p for p in key_logistics["pallet_contents_june"] if p["sscc"] == h["sscc"] and p["line"] == h["line"])
    m = lai["mirror"]
    named = {"shipment_id": h["shipment_id"], "line": h["line"], "sku": h["short_sku"], "units": h["short_units"]}
    right = truth["sku_actual"] == named["sku"] and truth["units_actual"] == -named["units"]
    return {
        "at": TRACE_AT, "sql": TRACE_SQL.strip(), "silence": silence, "hit": h,
        "names": named, "answer_key": {"sku": truth["sku_actual"], "units": truth["units_actual"]}, "right": right,
        "warehouse_pair_complete": m["warehouse_pair_complete"][:16], "store_count": m["store_count"][:16],
        "hours_before_pair": round(hours(TRACE_AT, m["warehouse_pair_complete"]), 1),
        "hours_before_count": round(hours(TRACE_AT, m["store_count"]), 1),
    }


# ---------- 4 and 5 ----------
def incidents(retail: dict, rai: dict, logistics: dict, lai: dict, payments: dict, pai: dict,
              key_retail: dict, key_payments: dict, audits: list[dict]) -> list[dict]:
    rep = key_retail["story"]["episode"]
    audit = next(a for a in audits if a["sku"] == HERO and rep["start"] <= a["audit_ts"][:16] <= rep["end"])
    rflag = rai["detector"]["hero_flags"][0]
    lep = logistics["story"]["episode"]
    lst = logistics["story"]
    m, f = pai["matcher"], pai["find"]
    slow = payments["story"]["slowdown"]
    debits = sorted(c["paid_ts"] for c in key_payments["charged_twice"])
    per = f["per_charge"]
    complaint_days = [x["complaint_days"] for x in per if x["complaint_days"] is not None]
    return [
        {"id": "shelf", "post": "retail", "title": "5 kg atta in the wrong bay", "when": "10–13 June",
         "harm": "the shelf stood empty while the books showed stock", "harm_start": rep["start"],
         "joined": {"ts": rflag["flag_ts"], "records": ["lines", "book"],
                    "what": f"no 5 kg sale for {rflag['open_hours_to_flag']:.0f} open hours, with {rflag['book_at_flag']} on the books"},
         "also": {"ts": audit["audit_ts"][:16], "records": ["audits", "book"], "hours": round(hours(rep["start"], audit["audit_ts"]), 1),
                  "what": f"a shelf audit recorded the shelf empty while the books showed {int(audit['book_at_audit'])}"},
         "found": {"ts": rep["end"], "by": "staff found the bags in the wrong bay"},
         "cost": f"{rep['lost_units']} bags not sold", "cost_inr": rep["lost_value_inr"],
         "ledger": "Nothing. No record holds a sale that did not happen.",
         "hours_joined": round(hours(rep["start"], rflag["flag_ts"]), 1), "hours_found": round(hours(rep["start"], rep["end"]), 1)},
        {"id": "truck", "post": "logistics", "title": "1 kg packs on a 5 kg pallet line", "when": "22–27 June",
         "harm": "the 5 kg shelf stood empty while the books showed 63", "harm_start": lep["start"],
         "joined": {"ts": TRACE_AT, "records": ["lines", "book", "receipts", "notice", "picks", "corrections"],
                    "what": "the store's silence, followed to the pick, beside the warehouse's short 1 kg slot"},
         "also": {"ts": lai["mirror"]["warehouse_pair_complete"][:16], "records": ["corrections"],
                  "hours": round(hours(lep["start"], lai["mirror"]["warehouse_pair_complete"]), 1),
                  "what": "the warehouse's two corrections pair up"},
         "found": {"ts": lai["mirror"]["store_count"][:16], "by": "a count the manager asked for after complaints"},
         "cost": f"{lep['lost_units']} bags not sold", "cost_inr": lep["lost_value_inr"],
         "ledger": (f"Four stock corrections in two buildings, netting to ₹{round(lst['adjustments_net']['value_at_cost_inr'])} at cost "
                    f"(₹{lai['mirror']['gross_atta_value_inr']:,} gross)."),
         "hours_joined": round(hours(lep["start"], TRACE_AT), 1), "hours_found": round(hours(lep["start"], lai["mirror"]["store_count"]), 1),
         "hours_pair": round(hours(lep["start"], lai["mirror"]["warehouse_pair_complete"]), 1)},
        {"id": "money", "post": "payments", "title": "Timeouts the bank had already paid",
         "when": f"{int(debits[0][8:10])}–{int(debits[-1][8:10])} June",
         "harm": f"{m['extra_charges']} extra debits on {m['customers']} customers", "harm_start": min(debits),
         "slowdown": {"start": slow["start"], "end": slow["end"], "extra_charges": slow["extra_charges"]},
         "joined": {"days_median": f["matcher_median_days"], "records": ["payments", "provider"],
                    "what": "each timeout matched to the provider's next-morning file by amount and time"},
         "found": {"days_median": f["complaint_median_days"], "by": "the customer's complaint",
                   "never": f["never_complained"]},
         "cost": f"₹{m['extra_inr']:,.2f} taken twice", "cost_inr": m["extra_inr"],
         "ledger": (f"UPI credits like any other. ₹{m['extra_inr'] - f['not_refunded_inr']:,.2f} went back after complaints; "
                    f"₹{f['not_refunded_inr']:,.2f} was still in suspense when June closed."),
         "hours_joined": round(f["matcher_median_days"] * 24, 1), "hours_found": round(median(complaint_days) * 24, 1)},
    ]


def agents(rai: dict, lai: dict, pai: dict, retail: dict) -> dict:
    ag = retail["agents"]["seeds"]
    return {
        "assistants": {
            "retail": rai["assistant"]["score"], "logistics": lai["assistant"]["score"], "payments": pai["assistant"]["score"],
            "naive": rai["assistant"]["score"]["naive"] + lai["assistant"]["score"]["naive"] + pai["assistant"]["score"]["naive"],
            "domain": rai["assistant"]["score"]["domain"] + lai["assistant"]["score"]["domain"] + pai["assistant"]["score"]["domain"],
            "of": rai["assistant"]["score"]["of"] + lai["assistant"]["score"]["of"] + pai["assistant"]["score"]["of"],
        },
        "replenishment": {
            "junes": ag["n"], "seeds": [ag["first"], ag["last"]],
            "lost_bags_mean": {k: ag["runs"][k]["mean"]["hero_lost_units"] for k in ("none", "naive", "domain")},
            "checks_mean": ag["runs"]["domain"]["mean"]["checks"],
            "checks_found_gap_mean": ag["runs"]["domain"]["mean"]["checks_found_gap"],
        },
    }


def main() -> None:
    con = connect()
    retail, rai = load("retail.json"), load("retail-ai.json")
    logistics, lai = load("logistics.json"), load("logistics-ai.json")
    payments, pai = load("payments.json"), load("payments-ai.json")
    key_retail = json.loads((DATA / "answer-key-retail.json").read_text())
    key_logistics = json.loads((DATA / "answer-key-logistics.json").read_text())
    key_payments = json.loads((DATA / "answer-key-payments.json").read_text())

    js = joins(con, pai)
    copies = [j for j in js if j["kind"] == "copy"]
    obs = [j for j in js if j["kind"] == "observation"]
    t = trace(con, lai, key_logistics)
    audits = disagreeing_audits(con)
    inc = incidents(retail, rai, logistics, lai, payments, pai, key_retail, key_payments, audits)
    pallets_checked = one(con, "SELECT count(*) AS n, sum(CASE WHEN weight_check <> 'not weighed' THEN 1 ELSE 0 END) AS checked FROM pallets")
    label_receipts = one(con, "SELECT count(*) AS n, sum(CASE WHEN receipt_method LIKE 'pallet label%' THEN 1 ELSE 0 END) AS by_label FROM receipts")
    slot_picks = one(con, "SELECT count(*) AS n, sum(CASE WHEN confirmed_by = 'slot label scan' THEN 1 ELSE 0 END) AS by_slot FROM picks")
    no_rrn = one(con, "SELECT count(*) AS n, sum(CASE WHEN rrn IS NULL THEN 1 ELSE 0 END) AS without FROM till_payments "
                      "WHERE tender = 'UPI' AND till_status = 'failed: no response'")

    out = {
        "about": ("June at Store 014 on one map: which records copy each other, which observe the world, and what joining "
                  "them across the shelf, the truck and the money finds. Generated by scripts/analysis/finale.py from the "
                  "records in public/data/india-grocery and the three analyses' outputs."),
        "joins": js,
        "summary": {"joins": len(js), "copies": len(copies), "observations": len(obs),
                    "rows_compared_in_copies": sum(j["compared"] for j in copies)},
        "audits_disagreeing": audits,
        "evidence": {"pallets": pallets_checked, "receipts_by_label": label_receipts, "picks_by_slot_scan": slot_picks,
                     "timeouts_without_rrn": no_rrn},
        "map": {"records": RECORDS, "things": THINGS, "reads": {k: [{"kpi": a, "name": b} for a, b in v] for k, v in READS.items()},
                "kpis": KPIS, "rules": RULES,
                "unseen": [k for k in THINGS if not any(k in r["looks_at"] for r in RECORDS.values())]},
        "trace": t,
        "incidents": inc,
        "agents": agents(rai, lai, pai, retail),
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    public = {
        "about": ("Store 014's records in June 2026 as a map: what writes each record, what it looks at in the world, how often "
                  "each join agrees, and which record each headline KPI reads. A starting point for a domain layer: give it to an "
                  "agent with the schema. Built by scripts/analysis/finale.py in kvinayakpai/domain-series from the records next "
                  "to this file. Synthetic world, seed 42."),
        "records": [{"id": k, **{x: v[x] for x in ("name", "domain", "file", "written_by")},
                     "looks_at": [{"thing": t, "how": h} for t, h in v["looks_at"].items()], **({"sees": v["sees"]} if "sees" in v else {})}
                    for k, v in RECORDS.items()],
        "things": [{"id": k, "name": v, "looked_at_by": [r for r, rv in RECORDS.items() if k in rv["looks_at"]]} for k, v in THINGS.items()],
        "joins": [{x: j[x] for x in ("id", "a", "b", "how", "compared", "agree", "kind", "sql")} for j in js],
        "kpis": KPIS,
        "rules": RULES,
    }
    MAP_OUT.write_text(json.dumps(public, indent=1, ensure_ascii=False) + "\n")
    for j in js:
        print(f"{j['id']:22s} {j['agree']:>6} of {j['compared']:<6} {j['kind']}")
    print("trace:", t["names"], "right" if t["right"] else "WRONG", f"{t['hours_before_pair']} h before the pair, {t['hours_before_count']} h before the count")
    print("unseen:", out["map"]["unseen"])
    for i in inc:
        print(i["id"], i["hours_joined"], "h joined vs", i["hours_found"], "h found")
    print("agents:", out["agents"])
    print(f"wrote {OUT.relative_to(ROOT)} and {MAP_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
