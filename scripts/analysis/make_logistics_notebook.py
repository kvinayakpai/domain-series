"""Build notebooks/logistics.ipynb, the runnable version of the logistics technical companion.

    python3 scripts/analysis/make_logistics_notebook.py            # write the notebook
    python3 scripts/analysis/make_logistics_notebook.py --run      # also run it on the local records and
                                                                   # check its numbers against src/data/logistics-ai.json

The notebook reads the records from the site by default, so it runs as is in Colab or Jupyter.
Set STORE014_DATA to a folder or URL to read them from somewhere else.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "notebooks" / "logistics.ipynb"
SITE = "https://kvinayakpai.github.io/domain-series/"

cells: list = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text.strip("\n")))


md(f"""
# On time, in full, and wrong: the shipping records

The runnable companion to [On time, in full, and wrong]({SITE}logistics/) and its
[technical companion]({SITE}logistics/technical/). Everything here uses the downloadable records of Store 014 and
the warehouse that supplies it: fictional, simulated hour by hour through June 2026. The answer key is read only at
the end of each section, to score what the records gave us.

Runs in a few seconds. Needs `duckdb` and `pandas` (both preinstalled in Colab).
""")

code("""
import json, os, urllib.request

import duckdb
import pandas as pd

DATA = os.environ.get("STORE014_DATA", "https://kvinayakpai.github.io/domain-series/data/india-grocery/")
FILES = {
    "products": "products.csv", "shipments": "shipments-june.csv", "notice_lines": "shipping-notice-lines-june.csv",
    "picks": "dc-pick-confirmations-june.csv", "pallets": "pallets-june.csv", "goods_receipts": "goods-receipts-june.csv",
    "dc_adjustments": "dc-stock-adjustments-june.csv", "stock_counts": "stock-counts-june.csv",
    "store_orders": "store-orders-june.csv", "inventory_book": "inventory-book-june.csv",
    "daily_sales": "daily-sales-june.csv", "forecasts": "forecasts-june.csv",
}
TIMES = {"shipments": ["dispatched_ts", "slot_start", "slot_end", "arrived_ts"], "picks": ["pick_ts"],
         "goods_receipts": ["received_ts"], "dc_adjustments": ["adjusted_ts"], "stock_counts": ["count_ts"],
         "store_orders": ["created_ts"]}
TEXT = {"sscc": str, "gtin": str}  # SSCCs and GTINs are identifiers: keep their leading zeros

con = duckdb.connect()
tables = {}
for name, file in FILES.items():
    df = pd.read_csv(DATA + file, parse_dates=TIMES.get(name, []), dtype=TEXT)
    tables[name] = df
    con.register(name, df)

def read_json(path):
    if path.startswith("http"):
        with urllib.request.urlopen(path) as f:
            return json.load(f)
    with open(path) as f:
        return json.load(f)

KEY = read_json(DATA + "answer-key-logistics.json")   # for scoring only

def q(sql):
    return con.execute(sql).df()

{k: len(v) for k, v in tables.items()}
""")

md("""
## 1. Tests that pass

Ten data tests on the shipping records, the kind a dbt project ships on day one. A test passes when its query returns
no rows. Every record here was written from the same pick confirmation, so they agree with each other.
""")

code('''
TESTS = {
 "Shipments: arrival after dispatch, a 30-minute slot":
   "SELECT * FROM shipments WHERE arrived_ts <= dispatched_ts OR slot_end - slot_start <> INTERVAL 30 MINUTE",
 "Shipping notice: shipment, pallet and line are unique":
   "SELECT shipment_id, sscc, line, count(*) FROM notice_lines GROUP BY ALL HAVING count(*) > 1",
 "Shipping notice: items and barcodes in the product master, units are cases times the case size": """
   SELECT n.* FROM notice_lines n LEFT JOIN products p ON p.sku = n.sku AND p.gtin = n.gtin
   WHERE p.sku IS NULL OR n.units <> n.cases * p.case_units""",
 "Pick confirmations: one per notice line, same order, item and cases, confirmed by a scan": """
   SELECT n.* FROM notice_lines n LEFT JOIN picks p USING (shipment_id, line)
   WHERE p.sku IS NULL OR p.sku <> n.sku OR p.order_id <> n.order_id OR p.cases_confirmed <> n.cases
      OR p.confirmed_by IS NULL OR p.cases_confirmed > p.cases_ordered""",
 "Pallets: every pallet on a notice is in the pallet table, with the same tare on every pallet": """
   WITH w AS (SELECT n.sscc, sum(n.cases * p.case_kg) AS cases_kg FROM notice_lines n JOIN products p USING (sku) GROUP BY n.sscc),
        t AS (SELECT round(pl.notice_kg - w.cases_kg, 1) AS tare FROM w LEFT JOIN pallets pl USING (sscc))
   SELECT tare, count(*) FROM t GROUP BY tare HAVING (SELECT count(DISTINCT tare) FROM t) <> 1 OR tare IS NULL""",
 "Goods receipts: every notice line booked, as its shipping notice says": """
   SELECT n.* FROM notice_lines n LEFT JOIN goods_receipts r USING (shipment_id, sscc, line)
   WHERE r.grn_id IS NULL OR r.asn_sku <> n.sku OR r.asn_units <> n.units OR r.sku_booked <> r.asn_sku
      OR r.units_booked <> r.asn_units""",
 "Goods receipts: booked when the truck arrived":
   "SELECT r.* FROM goods_receipts r JOIN shipments s USING (shipment_id) WHERE r.received_ts <> s.arrived_ts",
 "Store orders: every order line is on the next morning's shipping notice": """
   SELECT o.* FROM store_orders o LEFT JOIN notice_lines n ON n.order_id = o.order_id AND n.sku = o.sku
   WHERE n.sku IS NULL AND CAST(o.created_ts AS DATE) < (SELECT max(CAST(arrived_ts AS DATE)) FROM shipments)""",
 "Warehouse adjustments: units are cases times the case size, value is units at cost": """
   SELECT a.* FROM dc_adjustments a JOIN products p USING (sku)
   WHERE a.units <> a.cases * p.case_units OR abs(a.value_at_cost_inr - a.units * p.cost_inr) > 0.01""",
 "Store counts: each adjustment is the count minus the book":
   "SELECT * FROM stock_counts WHERE adjustment <> counted - book_before",
}
results = {name: len(q(sql)) for name, sql in TESTS.items()}
pd.Series(results, name="failing rows")
''')

md("""
## 2. Corrections, in both buildings

The warehouse corrects its slots; the store corrects its books at counts. Put every correction in one view, in units
and in cases, because a mis-pick moves whole cases and the two sizes of atta have different case sizes.
""")

code('''
con.execute("""
CREATE OR REPLACE VIEW v_corrections AS
SELECT 'warehouse' AS building, a.adjusted_ts AS ts, a.sku, split_part(a.sku, '-', 1) AS family, a.slot,
       a.units, CAST(a.cases AS DOUBLE) AS cases, a.value_at_cost_inr AS value_inr, a.reason AS why
FROM dc_adjustments a
UNION ALL
SELECT 'store', c.count_ts, c.sku, split_part(c.sku, '-', 1), NULL, c.adjustment,
       c.adjustment / CAST(p.case_units AS DOUBLE), round(c.adjustment * p.cost_inr, 2), c.trigger
FROM stock_counts c JOIN products p USING (sku)
WHERE c.adjustment <> 0 AND c.count_ts > TIMESTAMP '2026-06-01 07:00'
""")
q("SELECT * FROM v_corrections ORDER BY ts")
''')

md("""
Netted, the atta corrections come to almost nothing. That is why nobody chases them.
""")

code('''
q("""SELECT round(sum(value_inr)) AS net_inr, round(sum(abs(value_inr))) AS gross_inr
     FROM v_corrections WHERE family = 'ATTA' AND abs(cases) >= 1""")
''')

md("""
## 3. Mirror pairs

The domain test: two corrections mirror each other if they are in one product family, have opposite signs, are each
at least a case, are within 15% of each other in cases, and fall within seven days. In one building they must be in
neighbouring slots (warehouse) or two items at the store; across buildings they must be the same item.
""")

code('''
con.execute("""
CREATE OR REPLACE VIEW v_mirror_pairs AS
SELECT CASE WHEN a.building = b.building THEN 'same building' ELSE 'across buildings' END AS kind,
       a.building AS building_a, a.ts AS ts_a, a.sku AS sku_a, a.slot AS slot_a, a.units AS units_a, round(a.cases, 2) AS cases_a,
       b.building AS building_b, b.ts AS ts_b, b.sku AS sku_b, b.slot AS slot_b, b.units AS units_b, round(b.cases, 2) AS cases_b
FROM v_corrections a JOIN v_corrections b
  ON a.family = b.family AND sign(a.units) = -sign(b.units)
 AND abs(a.cases) >= 1 AND abs(b.cases) >= 1
 AND abs(abs(a.cases) - abs(b.cases)) <= 0.15 * greatest(abs(a.cases), abs(b.cases))
 AND abs(epoch(b.ts) - epoch(a.ts)) <= 7 * 86400
 AND (a.ts < b.ts OR (a.ts = b.ts AND a.sku < b.sku))
WHERE (a.building = b.building AND a.sku <> b.sku
       AND (a.building = 'store' OR (split_part(a.slot, '-', 1) = split_part(b.slot, '-', 1)
            AND split_part(a.slot, '-', 2) = split_part(b.slot, '-', 2)
            AND abs(CAST(split_part(a.slot, '-', 3) AS INTEGER) - CAST(split_part(b.slot, '-', 3) AS INTEGER)) = 1)))
   OR (a.building <> b.building AND a.sku = b.sku)
""")
pairs = q("SELECT * FROM v_mirror_pairs ORDER BY ts_b, ts_a")
pairs
''')

md("""
Four atta corrections, two in each building, make four pairs. The fifth pair is milk at the month-end count: toned
milk scanned as full-cream at the till, the retail post's scan errors.

## 4. The trace

For the warehouse pair, look for picks of the item that came up over (5 kg, slot A-07-03), in the cases the pair moved,
in the week before the first correction. A slot-label scan confirmed each of them.
""")

code('''
dc = pairs[(pairs.kind == "same building") & (pairs.building_a == "warehouse")].iloc[0]
sku, slot, cases = (dc.sku_a, dc.slot_a, round(abs(dc.cases_a))) if dc.units_a > 0 else (dc.sku_b, dc.slot_b, round(abs(dc.cases_b)))
first = min(dc.ts_a, dc.ts_b)
candidates = q(f"""
  SELECT p.pick_ts, p.shipment_id, p.line, p.sku, p.slot, p.cases_confirmed, p.confirmed_by, n.sscc, n.units
  FROM picks p JOIN notice_lines n USING (shipment_id, line)
  WHERE p.sku = '{sku}' AND p.slot = '{slot}' AND p.cases_confirmed = {cases}
    AND p.pick_ts BETWEEN TIMESTAMP '{first}' - INTERVAL 7 DAY AND TIMESTAMP '{first}'
""")
candidates
''')

md("Score it: what was really on that pallet line?")

code('''
c0 = candidates.iloc[0]
truth = [c for c in KEY["pallet_contents_june"] if c["sscc"] == c0.sscc and c["line"] == c0.line][0]
{"noticed": f"{c0.units} x {c0.sku}", "really": f"{truth['units_actual']} x {truth['sku_actual']}"}
''')

md("""
## 5. Receipts that do not survive the next count

A receipt booked by a pallet-label scan copies the shipping notice. A later count is an independent observation. Flag
the latest receipt before a count when the count takes off half or more of what that receipt booked.
""")

code('''
con.execute("""
CREATE OR REPLACE VIEW v_receipt_survival AS
WITH latest AS (
  SELECT c.count_ts, c.sku, c.book_before, c.counted, c.adjustment, max(r.received_ts) AS received_ts
  FROM stock_counts c JOIN goods_receipts r ON r.sku_booked = c.sku AND r.received_ts < c.count_ts
   AND r.received_ts >= c.count_ts - INTERVAL 7 DAY
  WHERE c.adjustment < 0 GROUP BY ALL)
SELECT r.shipment_id, r.sscc, r.line, r.received_ts, r.sku_booked AS sku, r.units_booked,
       l.count_ts, l.book_before, l.counted, l.adjustment
FROM latest l JOIN goods_receipts r ON r.sku_booked = l.sku AND r.received_ts = l.received_ts
WHERE -l.adjustment >= 0.5 * r.units_booked
""")
survival = q("SELECT * FROM v_receipt_survival")
survival
''')

md("""
## 6. OTIF, four ways

By the warehouse's picks, by the store's receipts per line and per delivery, and once more with the receipts that did
not survive a count taken out. Then compare with the answer key, which knows what was on the pallets.
""")

code('''
per = q("""
  WITH lines AS (
    SELECT n.shipment_id, n.line, p.cases_ordered * pr.case_units AS ordered, r.units_booked AS received,
           p.cases_confirmed, p.cases_ordered, s.arrived_ts BETWEEN s.slot_start AND s.slot_end AS in_slot,
           strftime(s.dispatched_ts, '%H:%M') = '04:30' AS dispatched_on_time
    FROM notice_lines n JOIN shipments s USING (shipment_id) JOIN picks p USING (shipment_id, line)
    JOIN products pr ON pr.sku = n.sku JOIN goods_receipts r USING (shipment_id, sscc, line))
  SELECT shipment_id, count(*) AS lines, bool_and(in_slot) AS in_slot,
         bool_and(dispatched_on_time AND cases_confirmed = cases_ordered) AS dc_report,
         bool_and(in_slot AND received = ordered) AS scorecard,
         sum(CASE WHEN in_slot AND received = ordered THEN 1 ELSE 0 END) AS lines_ok
  FROM lines GROUP BY shipment_id ORDER BY shipment_id""")
bad = set(survival.shipment_id)
per["reconciled"] = per.scorecard & ~per.shipment_id.isin(bad)
ways = {"dc_report": per.dc_report.mean(), "by_line": per.lines_ok.sum() / per.lines.sum(),
        "scorecard": per.scorecard.mean(), "reconciled": per.reconciled.mean()}
pd.DataFrame({"from the records": pd.Series(ways).round(3),
              "answer key": pd.Series(KEY["otif_four_ways"]["ways"]).rename({"at_the_shelf": "reconciled"})})
''')

md("""
## Exercises

1. Find the 22 June line from the pallet weights alone. The pallet table holds the weight each pallet's notice implies;
   what would a scale have read?
2. Loosen the mirror rule to 25% and to 30 days. What else pairs up, and is any of it real?
3. Build the pair rule for the store alone: which store counts could have told the store, on their own, that a
   delivery was wrong?
4. Compute OTIF per line and per delivery for a 15-minute slot instead of 30. Which deliveries move?

The answer key (`answer-key-logistics.json`) scores each one.
""")

code('''
# The numbers the post quotes, in one place.
summary = {
    "generic_tests_passed": int(sum(v == 0 for v in results.values())),
    "pairs": len(pairs), "atta_pairs": int(pairs.sku_a.str.startswith("ATTA").sum()),
    "trace": [c0.shipment_id, c0.sscc, int(c0.line)],
    "receipts_failing": len(survival),
    "otif": {k: round(float(v), 3) for k, v in ways.items()},
}
print(json.dumps(summary))
''')


def build() -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                      "language_info": {"name": "python"}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, OUT)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(cells)} cells)")


def run_and_check() -> None:
    from nbconvert.preprocessors import ExecutePreprocessor

    nb = nbf.read(OUT, as_version=4)
    os.environ["STORE014_DATA"] = str(ROOT / "public" / "data" / "india-grocery") + "/"
    ExecutePreprocessor(timeout=300, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(OUT.parent)}})
    out = "".join(o.get("text", "") for o in nb.cells[-1].get("outputs", []))
    got = json.loads(out.strip().splitlines()[-1])
    ai = json.loads((ROOT / "src" / "data" / "logistics-ai.json").read_text())
    t = ai["mirror"]["traced_line"]
    want = {
        "generic_tests_passed": sum(x["pass"] for x in ai["tests"]["generic"]),
        "pairs": len(ai["mirror"]["pairs"]), "atta_pairs": ai["mirror"]["atta_pairs"],
        "trace": [t["shipment_id"], t["sscc"], t["line"]],
        "receipts_failing": len(ai["tests"]["domain"][2]["failing"]),
        "otif": ai["otif"]["ways"],
    }
    bad = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    if bad:
        sys.exit(f"notebook disagrees with logistics-ai.json: {bad}")
    nbf.write(nb, OUT)
    print("notebook ran and matches logistics-ai.json:", got)


if __name__ == "__main__":
    build()
    if "--run" in sys.argv:
        run_and_check()
