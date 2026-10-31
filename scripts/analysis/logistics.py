"""What a data team can find in the logistics records, scored against the answer key.

Reads the downloadable records in public/data/india-grocery and writes src/data/logistics-ai.json,
which the logistics post, its technical companion and the demo quote:

  1. the pipeline's data tests on the shipping records, which pass, and five domain tests, which do not
  2. a mirror-pair test on count corrections, in each building and across the two, and the trace
     query that names the pallet line
  3. OTIF from the records three ways, and once more after reconciling receipts with counts
  4. a scripted assistant answering seven questions at the supplier review, with the schema only and
     with a domain layer

Everything is built from the records alone. The answer key (answer-key-logistics.json, and for lost
sales answer-key-retail.json) is read only to score the results. The store-side gap detector is the
retail analysis's, imported from retail.py.

    python3 scripts/analysis/logistics.py

Needs duckdb, numpy and pandas. The notebook notebooks/logistics.ipynb walks through the same steps.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import retail as R

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public" / "data" / "india-grocery"
OUT = ROOT / "src" / "data" / "logistics-ai.json"

HERO, ONE_KG = "ATTA-WW-5KG", "ATTA-WW-1KG"
NAME = {HERO: "5 kg atta", ONE_KG: "1 kg atta"}
AS_OF = "2026-06-29T09:00"  # the supplier review, with June's records
WINDOW_DAYS = 7  # corrections pair within a week
TOLERANCE = 0.15  # and within 15% of each other in cases
GAP = ("2026-06-23", "2026-06-26")  # the days the 5 kg shelf stood empty after the delivery

TABLES = {
    "products": ("products.csv", {"gtin": "VARCHAR"}),
    "shipments": ("shipments-june.csv", {}),
    "notice_lines": ("shipping-notice-lines-june.csv", {"sscc": "VARCHAR", "gtin": "VARCHAR"}),
    "picks": ("dc-pick-confirmations-june.csv", {}),
    "pallets": ("pallets-june.csv", {"sscc": "VARCHAR"}),
    "goods_receipts": ("goods-receipts-june.csv", {"sscc": "VARCHAR"}),
    "dc_adjustments": ("dc-stock-adjustments-june.csv", {}),
    "stock_counts": ("stock-counts-june.csv", {}),
    "store_orders": ("store-orders-june.csv", {}),
    "daily_sales": ("daily-sales-june.csv", {}),
    "inventory_book": ("inventory-book-june.csv", {}),
    "forecasts": ("forecasts-june.csv", {}),
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name, (file, types) in TABLES.items():
        opt = f", types={json.dumps(types).replace('\"', chr(39))}" if types else ""
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('{DATA / file}'{opt})")
    return con


def rows(con, sql: str) -> list[dict]:
    return json.loads(con.execute(sql).df().to_json(orient="records", date_format="iso"))


def fmt(ts: str) -> str:
    return datetime.fromisoformat(ts[:16]).strftime("%a %-d %b, %H:%M")


def day(ts: str) -> str:
    return datetime.fromisoformat(ts[:16]).strftime("%a %-d %b")


# ---------------------------------------------------------------- 1. data tests
GENERIC_TESTS = [
    ("Shipments: arrival after dispatch, a 30-minute slot",
     "SELECT * FROM shipments WHERE arrived_ts <= dispatched_ts OR slot_end - slot_start <> INTERVAL 30 MINUTE"),
    ("Shipping notice: shipment, pallet and line are unique",
     "SELECT shipment_id, sscc, line, count(*) AS n FROM notice_lines GROUP BY ALL HAVING count(*) > 1"),
    ("Shipping notice: every item and barcode is in the product master, units are cases times the case size",
     ("SELECT n.* FROM notice_lines n LEFT JOIN products p ON p.sku = n.sku AND p.gtin = n.gtin "
      "WHERE p.sku IS NULL OR n.units <> n.cases * p.case_units")),
    ("Pick confirmations: one per notice line, same order, item and cases, confirmed by a scan",
     ("SELECT n.*, p.cases_confirmed FROM notice_lines n LEFT JOIN picks p USING (shipment_id, line) "
      "WHERE p.sku IS NULL OR p.sku <> n.sku OR p.order_id <> n.order_id OR p.cases_confirmed <> n.cases "
      "OR p.confirmed_by IS NULL OR p.cases_confirmed > p.cases_ordered")),
    ("Pallets: every pallet on a notice is in the pallet table, with the same tare on every pallet",
     ("WITH w AS (SELECT n.sscc, sum(n.cases * p.case_kg) AS cases_kg FROM notice_lines n JOIN products p USING (sku) "
      "GROUP BY n.sscc), t AS (SELECT round(pl.notice_kg - w.cases_kg, 1) AS tare FROM w LEFT JOIN pallets pl USING (sscc)) "
      "SELECT tare, count(*) AS pallets FROM t GROUP BY tare HAVING (SELECT count(DISTINCT tare) FROM t) <> 1 OR tare IS NULL")),
    ("Goods receipts: every notice line booked, as its shipping notice says",
     ("SELECT n.*, r.sku_booked, r.units_booked FROM notice_lines n LEFT JOIN goods_receipts r USING (shipment_id, sscc, line) "
      "WHERE r.grn_id IS NULL OR r.asn_sku <> n.sku OR r.asn_units <> n.units OR r.sku_booked <> r.asn_sku "
      "OR r.units_booked <> r.asn_units")),
    ("Goods receipts: booked when the truck arrived",
     "SELECT r.* FROM goods_receipts r JOIN shipments s USING (shipment_id) WHERE r.received_ts <> s.arrived_ts"),
    ("Store orders: every order line is on the next morning's shipping notice",
     ("SELECT o.* FROM store_orders o LEFT JOIN notice_lines n ON n.order_id = o.order_id AND n.sku = o.sku "
      "WHERE n.sku IS NULL AND CAST(o.created_ts AS DATE) < (SELECT max(CAST(arrived_ts AS DATE)) FROM shipments)")),
    ("Warehouse adjustments: units are cases times the case size, value is units at cost",
     ("SELECT a.* FROM dc_adjustments a JOIN products p USING (sku) WHERE a.units <> a.cases * p.case_units "
      "OR abs(a.value_at_cost_inr - a.units * p.cost_inr) > 0.01")),
    ("Store counts: each adjustment is the count minus the book",
     "SELECT * FROM stock_counts WHERE adjustment <> counted - book_before"),
]


def run_generic_tests(con) -> list[dict]:
    out = []
    for name, sql in GENERIC_TESTS:
        bad = rows(con, sql)
        out.append({"name": name, "sql": " ".join(sql.split()), "failing_rows": len(bad), "pass": not bad,
                    "examples": bad[:3]})
    return out


# ---------------------------------------------------------------- 2. corrections, mirror pairs, the trace
CORRECTIONS = """
CREATE OR REPLACE VIEW v_corrections AS
SELECT 'warehouse' AS building, a.adjusted_ts AS ts, a.sku, split_part(a.sku, '-', 1) AS family, a.slot,
       a.units, CAST(a.cases AS DOUBLE) AS cases, a.value_at_cost_inr AS value_inr, a.reason AS why
FROM dc_adjustments a
UNION ALL
SELECT 'store', c.count_ts, c.sku, split_part(c.sku, '-', 1), NULL, c.adjustment,
       c.adjustment / CAST(p.case_units AS DOUBLE), round(c.adjustment * p.cost_inr, 2), c.trigger
FROM stock_counts c JOIN products p USING (sku)
WHERE c.adjustment <> 0 AND c.count_ts > TIMESTAMP '2026-06-01 07:00'
"""

MIRRORS = f"""
CREATE OR REPLACE VIEW v_mirror_pairs AS
SELECT CASE WHEN a.building = b.building THEN 'same building' ELSE 'across buildings' END AS kind,
       a.building AS building_a, a.ts AS ts_a, a.sku AS sku_a, a.slot AS slot_a, a.units AS units_a,
       round(a.cases, 2) AS cases_a, a.value_inr AS value_a,
       b.building AS building_b, b.ts AS ts_b, b.sku AS sku_b, b.slot AS slot_b, b.units AS units_b,
       round(b.cases, 2) AS cases_b, b.value_inr AS value_b
FROM v_corrections a JOIN v_corrections b
  ON a.family = b.family AND sign(a.units) = -sign(b.units)
 AND abs(a.cases) >= 1 AND abs(b.cases) >= 1
 AND abs(abs(a.cases) - abs(b.cases)) <= {TOLERANCE} * greatest(abs(a.cases), abs(b.cases))
 AND abs(epoch(b.ts) - epoch(a.ts)) <= {WINDOW_DAYS} * 86400
 AND (a.ts < b.ts OR (a.ts = b.ts AND a.sku < b.sku))
WHERE (a.building = b.building AND a.sku <> b.sku
       AND (a.building = 'store' OR (split_part(a.slot, '-', 1) = split_part(b.slot, '-', 1)
            AND split_part(a.slot, '-', 2) = split_part(b.slot, '-', 2)
            AND abs(CAST(split_part(a.slot, '-', 3) AS INTEGER) - CAST(split_part(b.slot, '-', 3) AS INTEGER)) = 1)))
   OR (a.building <> b.building AND a.sku = b.sku)
"""


def mirror_pairs(con) -> list[dict]:
    con.execute(CORRECTIONS)
    con.execute(MIRRORS)
    return rows(con, "SELECT * FROM v_mirror_pairs ORDER BY ts_b, ts_a")


def trace(con, pair: dict) -> dict:
    """For a warehouse mirror pair, the picks of the item that came up over, from its slot, in the cases the
    pair moved, in the week before the first correction: the line that went out with the wrong cases."""
    over = pair if pair["units_a"] > 0 else {k.replace("_b", "_a"): v for k, v in pair.items() if k.endswith("_b")}
    sku = pair["sku_a"] if pair["units_a"] > 0 else pair["sku_b"]
    slot = pair["slot_a"] if pair["units_a"] > 0 else pair["slot_b"]
    cases = round(abs(pair["cases_a"]))
    first = min(pair["ts_a"], pair["ts_b"])[:16]
    sql = (f"SELECT p.pick_ts, p.shipment_id, p.line, p.sku, p.slot, p.cases_confirmed, p.confirmed_by, n.sscc, "
           f"n.units FROM picks p JOIN notice_lines n USING (shipment_id, line) "
           f"WHERE p.sku = '{sku}' AND p.slot = '{slot}' AND p.cases_confirmed = {cases} "
           f"AND p.pick_ts BETWEEN TIMESTAMP '{first}' - INTERVAL {WINDOW_DAYS} DAY AND TIMESTAMP '{first}' "
           f"ORDER BY p.pick_ts")
    del over
    return {"sql": " ".join(sql.split()), "candidates": rows(con, sql)}


SURVIVAL = f"""
CREATE OR REPLACE VIEW v_receipt_survival AS
WITH latest AS (
  SELECT c.count_ts, c.sku, c.book_before, c.counted, c.adjustment, max(r.received_ts) AS received_ts
  FROM stock_counts c JOIN goods_receipts r ON r.sku_booked = c.sku AND r.received_ts < c.count_ts
   AND r.received_ts >= c.count_ts - INTERVAL {WINDOW_DAYS} DAY
  WHERE c.adjustment < 0 GROUP BY ALL)
SELECT r.shipment_id, r.sscc, r.line, r.received_ts, r.sku_booked AS sku, r.units_booked,
       l.count_ts, l.book_before, l.counted, l.adjustment
FROM latest l JOIN goods_receipts r ON r.sku_booked = l.sku AND r.received_ts = l.received_ts
WHERE -l.adjustment >= 0.5 * r.units_booked
"""


# ---------------------------------------------------------------- 3. OTIF from the records
def otif(con, failed_receipts: set[tuple[str, int]]) -> dict:
    per = rows(con, """
        WITH lines AS (
          SELECT n.shipment_id, n.line, n.sku, p.cases_ordered * pr.case_units AS ordered, r.units_booked AS received,
                 p.cases_confirmed, p.cases_ordered, s.arrived_ts BETWEEN s.slot_start AND s.slot_end AS in_slot,
                 strftime(s.dispatched_ts, '%H:%M') = '04:30' AS dispatched_on_time
          FROM notice_lines n JOIN shipments s USING (shipment_id)
          JOIN picks p USING (shipment_id, line)
          JOIN products pr ON pr.sku = n.sku
          JOIN goods_receipts r USING (shipment_id, sscc, line))
        SELECT shipment_id, count(*) AS lines, bool_and(in_slot) AS in_slot,
               bool_and(dispatched_on_time AND cases_confirmed = cases_ordered) AS dc_report,
               bool_and(in_slot AND received = ordered) AS scorecard,
               sum(CASE WHEN in_slot AND received = ordered THEN 1 ELSE 0 END) AS lines_ok
        FROM lines GROUP BY shipment_id ORDER BY shipment_id""")
    for p in per:
        lines = rows(con, f"SELECT line FROM notice_lines WHERE shipment_id = '{p['shipment_id']}'")
        p["reconciled"] = bool(p["scorecard"]) and not any((p["shipment_id"], ln["line"]) in failed_receipts for ln in lines)
    n = len(per)
    n_lines = sum(p["lines"] for p in per)
    good = {"dc_report": sum(p["dc_report"] for p in per), "by_line": sum(p["lines_ok"] for p in per),
            "scorecard": sum(p["scorecard"] for p in per), "reconciled": sum(p["reconciled"] for p in per)}
    out_of = {"dc_report": n, "by_line": n_lines, "scorecard": n, "reconciled": n}
    return {"by_delivery": per, "good": good, "out_of": out_of,
            "ways": {k: round(good[k] / out_of[k], 3) for k in good},
            "in_slot": sum(p["in_slot"] for p in per), "shipments": n}


# ---------------------------------------------------------------- 4. the store's gap detector
def gap_detector() -> dict:
    """The retail analysis's hourly gap detector on the till lines, and the censored 5 kg hours of 23-26 June."""
    con = R.connect()
    dc = set(con.execute("SELECT sku FROM products WHERE flow = 'DC'").df().sku)
    sales = {s: a for s, a in R.hourly_sales(con).items() if s in dc}
    daily = {s: a.sum(axis=1) for s, a in sales.items()}
    book, _ = R.hourly_book(con, sales)
    made = R.forecasts_made(daily)
    patterns = R.learn_patterns(sales)
    runs = [r for r in R.detect(sales, book, made, patterns, R.ALPHA) if r["sku"] == HERO]
    stockouts = [s for s in R.stockout_hours(sales, book, made, patterns) if s["sku"] == HERO]
    run = next(r for r in runs if GAP[0] <= r["start"][:10] <= GAP[1])
    hours = [h for h in run["hours"]] + [s for s in stockouts if GAP[0] <= s["date"] <= GAP[1]]
    hours = [h for h in hours if GAP[0] <= h["date"] <= GAP[1]]
    return {
        "flag_ts": run["flag_ts"], "start": run["start"], "book_at_flag": run["book_at_flag"],
        "expected_at_flag": run["expected_at_flag"],
        "censored_open_hours": len(hours),
        "expected": round(sum(h["expected"] for h in hours), 1),
        "recorded": int(sum(h["recorded"] for h in hours)),
        "lost_estimate": round(sum(max(0.0, h["expected"] - h["recorded"]) for h in hours)),
        "hours": hours,
    }


# ---------------------------------------------------------------- 5. the assistant
def assistant(con, pairs, wtrace, survival, ways, gap, key, rkey) -> dict:
    line = key["story"]["line"]
    truth_line = key["story"]["actual"]
    by_del = {d["shipment_id"]: d for d in key["otif_by_delivery"]}
    sid = line["shipment_id"]

    def q(sql):
        return rows(con, sql)

    qa = []

    # Q1: a question about the records. Both should get it right.
    s_slot = ("SELECT count(*) AS deliveries, CAST(sum(CASE WHEN arrived_ts BETWEEN slot_start AND slot_end THEN 1 ELSE 0 END) "
              "AS INTEGER) AS in_slot FROM shipments")
    r1 = q(s_slot)
    gold_slot = sum(d["in_slot"] for d in key["otif_by_delivery"])
    qa.append({"id": "slot", "question": "How many of June's deliveries arrived inside their 06:00–06:30 slot?", "kind": "records",
               "naive": {"plan": [{"sql": s_slot, "result": r1}], "answer": f"{r1[0]['in_slot']} of {r1[0]['deliveries']}.",
                         "value": r1[0]["in_slot"]},
               "domain": {"plan": [{"sql": s_slot, "result": r1}], "answer": f"{r1[0]['in_slot']} of {r1[0]['deliveries']}.",
                          "value": r1[0]["in_slot"]},
               "gold": {"value": gold_slot, "why": "Arrival times are facts the records hold."},
               "check": "the number of deliveries in the slot"})

    # Q2: was the 22 June delivery on time and in full?
    s_ship = f"SELECT arrived_ts, slot_start, slot_end, pallets FROM shipments WHERE shipment_id = '{sid}'"
    rs = q(s_ship)
    s_rcv = (f"SELECT count(*) AS lines, sum(CASE WHEN sku_booked <> asn_sku OR units_booked <> asn_units THEN 1 ELSE 0 END) "
             f"AS discrepancies FROM goods_receipts WHERE shipment_id = '{sid}'")
    rr = q(s_rcv)
    s_pairs = ("SELECT kind, building_a, ts_a, sku_a, slot_a, cases_a, building_b, ts_b, sku_b, slot_b, cases_b "
               "FROM v_mirror_pairs WHERE sku_a LIKE 'ATTA%' ORDER BY ts_b")
    rp = q(s_pairs)
    cand = wtrace["candidates"]
    c0 = cand[0] if len(cand) == 1 else None
    dc_pair = next(p for p in pairs if p["kind"] == "same building" and p["building_a"] == "warehouse")
    st_pair = next(p for p in pairs if p["kind"] == "same building" and p["building_a"] == "store" and p["sku_a"].startswith("ATTA"))
    st5 = st_pair if st_pair["sku_a"] == HERO else {k.replace("_b", "_x").replace("_a", "_b").replace("_x", "_a"): v for k, v in st_pair.items()}
    one = {"units": st5["units_b"], "cases": st5["cases_b"]}
    five = {"units": st5["units_a"], "cases": st5["cases_a"]}
    arrived = rs[0]["arrived_ts"]
    qa.append({"id": "in_full", "question": "Was the 22 June delivery on time and in full?", "kind": "reality",
               "naive": {"plan": [{"sql": s_ship, "result": rs}, {"sql": s_rcv, "result": rr}],
                         "answer": (f"Yes. It arrived at {arrived[11:16]}, inside its {rs[0]['slot_start'][11:16]}–"
                                    f"{rs[0]['slot_end'][11:16]} slot, and all {rr[0]['lines']} lines were booked as the "
                                    f"shipping notice listed them, with no discrepancies."),
                         "in_full": True},
               "domain": {"plan": [{"sql": s_ship, "result": rs}, {"sql": s_rcv, "result": rr}, {"sql": s_pairs, "result": rp},
                                   {"sql": wtrace["sql"], "result": cand}],
                          "answer": (f"On time, at {arrived[11:16]}, but not in full. Line {c0['line']}, {c0['cases_confirmed']} "
                                     f"cases on the notice as 5 kg atta, held 1 kg packs: the warehouse's 1 kg slot came up "
                                     f"{abs(round(dc_pair['cases_a']))} cases short on {day(dc_pair['ts_a'])} and its 5 kg slot "
                                     f"{abs(round(dc_pair['cases_b']))} cases over on {day(dc_pair['ts_b'])}, and the store's "
                                     f"count on {day(st5['ts_a'])} found {abs(five['units'])} bags of 5 kg missing and "
                                     f"{one['units']} more 1 kg packs than the books showed. It was the only {c0['cases_confirmed']}-case "
                                     f"5 kg pick in the week before."),
                          "in_full": False},
               "gold": {"value": "On time, not in full: line 1 held 1 kg packs", "in_full": by_del[sid]["at_the_shelf"],
                        "why": f"The pallet line held {truth_line['units_actual']} packs of {NAME[truth_line['sku_actual']]}."},
               "check": "says whether the delivery was in full"})

    # Q3: OTIF in June.
    sc, rc = ways["ways"]["scorecard"], ways["ways"]["reconciled"]
    s_otif = ("SELECT count(*) AS deliveries, CAST(sum(CAST(scorecard AS INTEGER)) AS INTEGER) AS on_time_in_full "
              "FROM v_otif_by_delivery")
    s_otif_dom = ("SELECT count(*) AS deliveries, CAST(sum(CAST(scorecard AS INTEGER)) AS INTEGER) AS by_receipt, "
                  "CAST(sum(CAST(reconciled AS INTEGER)) AS INTEGER) AS reconciled_with_counts FROM v_otif_by_delivery")
    ro = q(s_otif)
    rod = q(s_otif_dom)
    gold_otif = key["otif_four_ways"]["ways"]["at_the_shelf"]
    qa.append({"id": "otif", "question": "What was Store 014's OTIF from the warehouse in June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_otif, "result": ro}],
                         "answer": f"{sc:.0%}: {ro[0]['on_time_in_full']} of {ro[0]['deliveries']} deliveries arrived in the slot with every line received in full.",
                         "value": sc},
               "domain": {"plan": [{"sql": s_otif_dom, "result": rod}, {"sql": "SELECT * FROM v_receipt_survival", "result": survival}],
                          "answer": (f"{rc:.0%}. The scorecard says {sc:.0%}, but one receipt did not survive the next count: "
                                     f"the 22 June line of 5 kg atta. Counting it as not in full leaves "
                                     f"{rod[0]['reconciled_with_counts']} of {rod[0]['deliveries']}."),
                          "value": rc},
               "gold": {"value": gold_otif, "why": "Deliveries in the slot with every case what the store ordered, from the answer key."},
               "check": "within 2 points of OTIF at the shelf"})

    # Q4: why was 5 kg atta off the shelf?
    s_book = (f"SELECT date, book_on_hand_close FROM inventory_book WHERE sku = '{HERO}' "
              f"AND date BETWEEN '{GAP[0]}' AND '{GAP[1]}' ORDER BY date")
    rb = q(s_book)
    s_sales = (f"SELECT sum(units_sold) AS bags FROM daily_sales WHERE sku = '{HERO}' AND date BETWEEN '{GAP[0]}' AND '2026-06-25'")
    rsl = q(s_sales)
    s_rop = (f"SELECT min(reorder_point) AS low, max(reorder_point) AS high, sum(ordered_units) AS ordered FROM forecasts "
             f"WHERE sku = '{HERO}' AND date BETWEEN '{GAP[0]}' AND '2026-06-25'")
    rop = q(s_rop)
    s_count = (f"SELECT count_ts, book_before, counted FROM stock_counts WHERE sku = '{HERO}' "
               f"AND CAST(count_ts AS DATE) BETWEEN '{GAP[0]}' AND '{GAP[1]}'")
    rcn = q(s_count)
    qa.append({"id": "why", "question": "Why was 5 kg atta off the shelf from 23 to 26 June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_book, "result": rb}, {"sql": s_sales, "result": rsl}, {"sql": s_count, "result": rcn}],
                         "answer": (f"The books showed {rb[0]['book_on_hand_close']} bags from 23 to 25 June while sales stopped, and the "
                                    f"count on {day(rcn[0]['count_ts'])} found none. The stock went missing in the store: theft "
                                    f"or a counting error."),
                         "names_delivery": False},
               "domain": {"plan": [{"sql": s_book, "result": rb}, {"sql": s_rop, "result": rop}, {"sql": s_pairs, "result": rp},
                                   {"sql": wtrace["sql"], "result": cand}],
                          "answer": (f"The {c0['units']} bags of 5 kg booked on 22 June were never on the pallet; line {c0['line']} "
                                     f"held 1 kg packs. The books sat at {rb[0]['book_on_hand_close']}, above the reorder point of "
                                     f"{rop[0]['low']}–{rop[0]['high']}, so nothing was ordered until the 26 June count zeroed them."),
                          "names_delivery": True},
               "gold": {"value": "A mis-pick: 1 kg packs shipped and booked as 5 kg", "names_delivery": True,
                        "why": "The 22 June pallet line held 1 kg packs; the books believed in 5 kg bags that never arrived."},
               "check": "traces the gap to the delivery"})

    # Q5: theft?
    s_loss = (f"SELECT count_ts, sku, adjustment, round(adjustment * cost_inr) AS value_at_cost_inr FROM stock_counts "
              f"JOIN products USING (sku) WHERE sku LIKE 'ATTA%' AND CAST(count_ts AS DATE) = '{GAP[1]}' AND adjustment <> 0")
    rl = q(s_loss)
    loss5 = next(x for x in rl if x["sku"] == HERO)
    qa.append({"id": "theft", "question": "Is the 5 kg atta missing at the store theft?", "kind": "reality",
               "naive": {"plan": [{"sql": s_loss, "result": rl}],
                         "answer": (f"Possibly: {abs(loss5['adjustment'])} bags, ₹{abs(loss5['value_at_cost_inr']):,.0f} at cost, went "
                                    f"missing between counts. Refer it to loss prevention."),
                         "theft": True},
               "domain": {"plan": [{"sql": s_loss, "result": rl}, {"sql": s_pairs, "result": rp}],
                          "answer": (f"No. The same count found {one['units']} more 1 kg packs than the books showed, the mirror image "
                                     f"in cases ({abs(five['cases']):g} against {abs(one['cases']):g}), and the warehouse's 5 kg slot "
                                     f"came up {abs(round(dc_pair['cases_b']))} cases over. The bags never left the warehouse."),
                          "theft": False},
               "gold": {"value": "Not theft: a mis-pick", "theft": False, "why": "No bags were stolen; they were never shipped."},
               "check": "says whether it is theft"})

    # Q6: which delivery to claim against?
    s_disc = "SELECT shipment_id, line, asn_sku, sku_booked FROM goods_receipts WHERE sku_booked <> asn_sku OR units_booked <> asn_units"
    rd = q(s_disc)
    qa.append({"id": "claim", "question": "Which delivery should the store raise a claim against?", "kind": "reality",
               "naive": {"plan": [{"sql": s_disc, "result": rd}],
                         "answer": "None: no receipt in June recorded a discrepancy.", "value": None},
               "domain": {"plan": [{"sql": wtrace["sql"], "result": cand}],
                          "answer": (f"{c0['shipment_id']}, pallet {c0['sscc']}, line {c0['line']}: {c0['cases_confirmed']} cases "
                                     f"noticed as {c0['units']} bags of 5 kg atta, picked at {c0['pick_ts'][11:16]} on "
                                     f"{day(c0['pick_ts'])} with a {c0['confirmed_by']}."),
                          "value": [c0["shipment_id"], c0["sscc"], c0["line"]]},
               "gold": {"value": [line["shipment_id"], line["sscc"], line["line"]],
                        "why": "The pallet line that held the wrong packs, from the answer key."},
               "check": "names the shipment, pallet and line"})

    # Q7: lost sales.
    t5 = [t for t in rkey["truth_daily"] if t["sku"] == HERO and GAP[0] <= t["date"] <= GAP[1]]
    gold_lost = key["story"]["episode"]["lost_units"]
    s_lost_naive = (f"SELECT count(*) AS closes_at_zero FROM inventory_book WHERE sku = '{HERO}' "
                    f"AND date BETWEEN '{GAP[0]}' AND '2026-06-25' AND book_on_hand_close <= 0")
    rln = q(s_lost_naive)
    con.register("v_censored_hours", pd.DataFrame(gap["hours"]))
    s_lost_dom = (f"SELECT count(*) AS censored_open_hours, round(sum(greatest(expected - recorded, 0))) AS bags "
                  f"FROM v_censored_hours WHERE date BETWEEN '{GAP[0]}' AND '{GAP[1]}'")
    rld = q(s_lost_dom)
    qa.append({"id": "lost", "question": "How many bags of 5 kg atta did shoppers want and not find, 23 to 26 June?",
               "kind": "reality",
               "naive": {"plan": [{"sql": s_lost_naive, "result": rln}],
                         "answer": "None recorded: the books showed stock until the count.", "value": 0},
               "domain": {"plan": [{"sql": s_lost_dom, "result": rld}],
                          "answer": (f"About {int(rld[0]['bags'])}: the sales expected in the {rld[0]['censored_open_hours']} open hours "
                                     f"the shelf was empty, from the gap detector and the hours with no stock on the books."),
                          "value": int(rld[0]["bags"])},
               "gold": {"value": gold_lost, "why": "Bags shoppers asked for and could not find, from the answer key."},
               "check": "within 20% of the true number"})
    del t5

    def right(item, side) -> bool:
        a, g = item[side], item["gold"]
        if item["id"] == "slot":
            return a["value"] == g["value"]
        if item["id"] == "in_full":
            return a["in_full"] == g["in_full"]
        if item["id"] == "otif":
            return abs(a["value"] - g["value"]) <= 0.02
        if item["id"] == "why":
            return a["names_delivery"] == g["names_delivery"]
        if item["id"] == "theft":
            return a["theft"] == g["theft"]
        if item["id"] == "claim":
            return a["value"] == g["value"]
        if item["id"] == "lost":
            return abs(a["value"] - g["value"]) / max(1, g["value"]) <= 0.20
        raise KeyError(item["id"])

    for item in qa:
        item["naive"]["right"] = right(item, "naive")
        item["domain"]["right"] = right(item, "domain")
    short = {
        "slot": (f"{r1[0]['in_slot']} of {r1[0]['deliveries']}",) * 3,
        "in_full": ("Yes", "On time, not in full", "On time, not in full"),
        "otif": (f"{sc:.0%}", f"{rc:.0%}", f"{gold_otif:.0%}"),
        "why": ("Theft or a counting error", "The 22 June line held 1 kg packs", "A mis-pick at the warehouse"),
        "theft": ("Possibly", "No", "No"),
        "claim": ("None", f"{c0['shipment_id']}, line {c0['line']}", f"{line['shipment_id']}, line {line['line']}"),
        "lost": ("None", f"About {int(rld[0]['bags'])}", f"{gold_lost}"),
    }
    for item in qa:
        n, d, gl = short[item["id"]]
        item["naive"]["short"], item["domain"]["short"], item["gold"]["short"] = n, d, gl
    return {
        "as_of": AS_OF,
        "questions": qa,
        "score": {"naive": sum(i["naive"]["right"] for i in qa), "domain": sum(i["domain"]["right"] for i in qa),
                  "of": len(qa)},
        "schema_only_tables": ["shipments", "notice_lines", "goods_receipts", "store_orders", "inventory_book",
                               "daily_sales", "forecasts", "stock_counts", "products"],
        "domain_layer": {
            "tables_added": ["picks", "pallets", "dc_adjustments", "pos_lines"],
            "views": {
                "v_corrections": "every count correction in both buildings, in units and in cases",
                "v_mirror_pairs": (f"pairs of corrections in one product family with opposite signs, each at least a case and "
                                   f"within {TOLERANCE:.0%} of each other in cases, within {WINDOW_DAYS} days: neighbouring "
                                   f"slots or one store count, or the same item in both buildings"),
                "v_receipt_survival": "receipt lines whose next count, within a week, took off half or more of what was booked",
                "v_otif_by_delivery": "OTIF per delivery by the warehouse's picks, by the store's receipts, and reconciled with counts",
                "v_censored_hours": "5 kg open hours the gap detector flagged, or with no stock on the books",
            },
            "definitions": {
                "SSCC": "A serial number for a pallet. It identifies the pallet, not what is on it.",
                "pick confirmation": "A scan of the slot's label. It confirms where the picker stood, not what was picked.",
                "goods receipt": "Booked by scanning the pallet label against the shipping notice. A copy of the notice, not an observation of the cases.",
                "in full": "Every case is what was ordered. Only an independent observation can say so: a case scan, a scale, or a later count.",
                "count correction": "Says the book was wrong, not why.",
            },
            "rules": [
                "Pair count corrections before you explain them: equal and opposite in cases, in one family, in neighbouring slots, at one count, or across the two buildings.",
                "Trace a warehouse pair to the picks of the item that came up over, from its slot, in the cases the pair moved, in the week before.",
                "A receipt that does not survive the next count was not what its notice said.",
            ],
        },
    }


# ---------------------------------------------------------------- main
def main() -> None:
    con = connect()
    key = json.loads((DATA / "answer-key-logistics.json").read_text())
    rkey = json.loads((DATA / "answer-key-retail.json").read_text())

    generic = run_generic_tests(con)
    pairs = mirror_pairs(con)
    dc_pair = next(p for p in pairs if p["kind"] == "same building" and p["building_a"] == "warehouse")
    wtrace = trace(con, dc_pair)
    con.execute(SURVIVAL)
    survival = rows(con, "SELECT * FROM v_receipt_survival ORDER BY received_ts")
    failed = {(r["shipment_id"], r["line"]) for r in survival}
    ways = otif(con, failed)
    con.register("v_otif_by_delivery", pd.DataFrame(ways["by_delivery"]))
    unweighed = rows(con, "SELECT sscc, shipment_id, weight_check FROM pallets WHERE weight_check = 'not weighed'")
    case_scanned = rows(con, "SELECT DISTINCT sscc FROM goods_receipts WHERE receipt_method LIKE 'case scan%'")
    gap = gap_detector()

    domain = [
        {"name": "No count correction has a mirror image in the same building",
         "failing": [p for p in pairs if p["kind"] == "same building"]},
        {"name": "No warehouse correction is mirrored at the store",
         "failing": [p for p in pairs if p["kind"] == "across buildings"]},
        {"name": "Every receipt survives the next count", "failing": survival},
        {"name": "Something other than the pick checks what is on each pallet (a scale weight or a case scan)",
         "failing": [u for u in unweighed if u["sscc"] not in {c["sscc"] for c in case_scanned}]},
        {"name": "No item goes longer without a sale than its usual rate allows while the books show stock (5 kg, after 22 June)",
         "failing": [{k: gap[k] for k in ("start", "flag_ts", "book_at_flag", "expected_at_flag")}]},
    ]
    for t in domain:
        t["pass"] = not t["failing"]

    # Score the mirror test and the trace against the answer key.
    contents = {(c["sscc"], c["line"]): c for c in key["pallet_contents_june"]}
    c0 = wtrace["candidates"][0]
    traced = contents[(c0["sscc"], c0["line"])]
    first_found = min(dc_pair["ts_a"], dc_pair["ts_b"])
    found = max(dc_pair["ts_a"], dc_pair["ts_b"])
    arrived = key["story"]["shipment"]["arrived_ts"]

    def days(a: str, b: str) -> float:
        return round((datetime.fromisoformat(b[:16]) - datetime.fromisoformat(a[:16])).total_seconds() / 86400, 2)

    atta_pairs = [p for p in pairs if p["sku_a"].startswith("ATTA")]
    mirror = {
        "pairs": pairs,
        "atta_pairs": len(atta_pairs),
        "other_pairs": [p for p in pairs if not p["sku_a"].startswith("ATTA")],
        "corrections_explained": len({(p[f"building_{s}"], p[f"ts_{s}"], p[f"sku_{s}"]) for p in atta_pairs for s in "ab"}),
        "net_atta_value_inr": round(sum(r["value_inr"] for r in rows(con, "SELECT * FROM v_corrections WHERE family = 'ATTA' "
                                                                          "AND abs(cases) >= 1"))),
        "gross_atta_value_inr": round(sum(abs(r["value_inr"]) for r in rows(con, "SELECT * FROM v_corrections WHERE family = 'ATTA' "
                                                                                 "AND abs(cases) >= 1"))),
        "trace": wtrace,
        "traced_line": {**c0, "actual_sku": traced["sku_actual"], "actual_units": traced["units_actual"]},
        "trace_right": traced["sku_actual"] != c0["sku"],
        "warehouse_pair_complete": found,
        "first_correction": first_found,
        "arrived": arrived,
        "days_to_pair": days(arrived, found),
        "store_count": next(c["count_ts"] for c in rows(con, f"SELECT count_ts FROM stock_counts WHERE sku = '{HERO}' "
                                                               f"AND adjustment < -10")),
    }
    mirror["days_to_store_count"] = days(arrived, mirror["store_count"])
    otif_check = {"answer_key": key["otif_four_ways"]["ways"],
                  "matches": {k: ways["ways"][k] == key["otif_four_ways"]["ways"][k] for k in ("dc_report", "by_line", "scorecard")}
                  | {"reconciled_vs_at_the_shelf": ways["ways"]["reconciled"] == key["otif_four_ways"]["ways"]["at_the_shelf"]}}

    out = {
        "about": ("What a data team can find in the logistics records, scored against the answer key. "
                  "Generated by scripts/analysis/logistics.py from public/data/india-grocery."),
        "tests": {"generic": generic, "domain": domain},
        "mirror": mirror,
        "otif": {**{k: v for k, v in ways.items() if k != "by_delivery"}, "by_delivery": ways["by_delivery"], "check": otif_check},
        "pallets": {"total": len(rows(con, "SELECT sscc FROM pallets")), "weighed": len(rows(con, "SELECT sscc FROM pallets WHERE weight_check <> 'not weighed'")),
                    "case_scanned": len(case_scanned)},
        "gap": {k: v for k, v in gap.items() if k != "hours"},
        "assistant": assistant(con, pairs, wtrace, survival, ways, gap, key, rkey),
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    a = out["assistant"]["score"]
    print(f"generic tests passing: {sum(t['pass'] for t in generic)} of {len(generic)}; domain tests failing: "
          f"{sum(not t['pass'] for t in domain)} of {len(domain)}")
    print(f"mirror pairs: {len(pairs)} ({mirror['atta_pairs']} atta); trace -> {c0['shipment_id']} line {c0['line']} "
          f"(really {traced['units_actual']} x {traced['sku_actual']}); OTIF {ways['ways']}; assistant {a}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
