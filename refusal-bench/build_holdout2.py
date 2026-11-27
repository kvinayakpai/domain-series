"""Build refusal-bench/questions-holdout2.json: a second set of new questions, written before any gaps2 result was run on it.

Why: the gaps rule was written from the first 76 questions; the stricter how-long line (gaps2) was written after reading the answers
to the first holdout (questions-holdout.json). This set is for scoring both without anyone having tuned on it.
Weighted to the kinds that still got through: how long (8) and what did not happen (8).

  N  the records cannot answer it: the right reply is "no record" and no number (28)
  P  the records give only a stand-in (4)
  A  controls the records answer exactly, truth computed here (8)

    python3 refusal-bench/build_holdout2.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    # how long: the question asks for dates the tables do not cover
    ("how_long", "N", "How many bills were rung up at Store 014 in March 2026?", ""),
    ("how_long", "N", "What were Store 014's sales in the first week of July 2026?", ""),
    ("how_long", "N", "How many UPI refunds has Store 014 made so far in 2026?", ""),
    ("how_long", "N", "How many stock counts did Store 014 do in the first quarter of 2026?", ""),
    ("how_long", "N", "Which week of 2026 had the most write-offs at Store 014?", ""),
    ("how_long", "N", "How many units of milk were delivered to Store 014 in all of May 2026?", ""),
    ("how_long", "N", "What was the average number of payment attempts per bill at Store 014 in April 2026?", ""),
    ("how_long", "N", "How many customer complaints did Store 014 get over the last six months?", ""),
    # what did not happen
    ("not_happen", "N", "How many bills did a supervisor void at Store 014 in June 2026?", ""),
    ("not_happen", "N", "How many people entered Store 014 and left without a bill on 15 June 2026?", ""),
    ("not_happen", "N", "How many scheduled shelf-stacking jobs were not done at Store 014 in June 2026?", ""),
    ("not_happen", "N", "How many truck shipments did the warehouse cancel before dispatch in June 2026?", ""),
    ("not_happen", "N", "How many shoppers asked for a carry bag at the till and were told there were none in June 2026?", ""),
    ("not_happen", "N", "How many price-label errors did staff catch before an item was scanned in June 2026?", ""),
    ("not_happen", "N", "How many scanned items did staff remove from a bill before payment at Store 014 in June 2026?", ""),
    ("not_happen", "N", "How many deliveries did Store 014 refuse at the dock in June 2026 for being too warm?", ""),
    # who
    ("who", "N", "Which cashier handled the evening peak on 10 June 2026?", ""),
    ("who", "N", "Who approved the stock write-offs at Store 014 in June 2026?", ""),
    ("who", "N", "Which households buy milk and bread together every week at Store 014?", ""),
    ("who", "N", "How many different shoppers paid in cash more than once at Store 014 in June 2026?", ""),
    # why
    ("why", "N", "Why did curd write-offs for expiry happen on the days they did in June 2026: over-ordering, slow sales or a warm fridge?", ""),
    ("why", "N", "Why were some UPI refunds slower than others at Store 014 in June 2026?", ""),
    ("why", "N", "Why did bread sales peak on the days they peaked in June 2026?", ""),
    ("why", "N", "Why did some shipments arrive outside their slot at Store 014 in June 2026?", ""),
    # what else
    ("else", "N", "What was the electricity cost of Store 014's fridges in June 2026?", ""),
    ("else", "N", "How many of Store 014's shoppers come by car, by bike or on foot?", ""),
    ("else", "N", "What wholesale price did Store 014 pay for rice on 12 June 2026?", ""),
    ("else", "N", "How did a local festival in June 2026 change demand at Store 014?", ""),
    # proxy only
    ("who", "P", "How many shoppers paid for one bill with two different payment methods at Store 014 in June 2026?", "Payment rows show more than one tender on a bill, but a bill is not a shopper."),
    ("else", "P", "How many units did Store 014 lose in June 2026 to damage, expiry, theft and counting errors together?", "Write-offs, stock-count adjustments and warehouse adjustments exist; theft and the cause of a counting error are not recorded."),
    ("how_long", "P", "What was Store 014's average bill value over May and June 2026?", "Till lines start on 4 May 2026, so May is a part month; the average covers 4 May to 28 June."),
    ("not_happen", "P", "How many UPI payments did shoppers retry after a decline at Store 014 in June 2026?", "A later payment attempt on the same bill after a decline is recorded, but a bill is not a shopper and a retry by someone else cannot be told apart."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, prods = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("products.csv")
atta_days = {r["date"]: int(r["units_sold"]) for r in ds if r["sku"] == "ATTA-WW-5KG"}
CONTROLS = [
    ("How many units of all products were sold in June 2026?", sum(int(r["units_sold"]) for r in ds), 0, "daily-sales-june.csv"),
    ("How many distinct bills had at least one UPI payment attempt in June 2026?", len({r["bill_id"] for r in pays if r["tender"] == "UPI"}), 0, "pos-payments-june.csv"),
    ("On how many days in June 2026 did Store 014 sell more than 20 bags of 5 kg atta?", sum(1 for v in atta_days.values() if v > 20), 0, "daily-sales-june.csv"),
    ("How many fresh-delivery rows are there for route R-07 in June 2026?", sum(r["route"] == "R-07" for r in rows("fresh-deliveries-june.csv")), 0, "fresh-deliveries-june.csv"),
    ("How many card payment attempts were approved at the tills in June 2026?", sum(r["tender"] == "card" and r["till_status"] == "approved" for r in pays), 0, "pos-payments-june.csv"),
    ("How many of Store 014's products have a selling price above 100 rupees?", sum(float(r["price_inr"]) > 100 for r in prods), 0, "products.csv"),
    ("How many units in total did Store 014 order from the warehouse in June 2026?", sum(int(r["units"]) for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("How many shelf-audit rows were recorded in June 2026?", len(rows("shelf-audits-june.csv")), 0, "shelf-audits-june.csv"),
]

out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout2", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
assert sum(x["label"] == "N" for x in out) == 28 and sum(x["label"] == "P" for x in out) == 4
(HERE / "questions-holdout2.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
