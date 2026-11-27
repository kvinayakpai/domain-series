"""Build refusal-bench/questions-holdout4.json: a fourth question set, written after the guard was frozen (commit e7d3425) and never used
to adjust it. Final test of the deterministic guard. N 29, P 4, A 16.   python3 refusal-bench/build_holdout4.py"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    ("how_long", "N", "How many bills were rung up at Store 014 in April 2026?", ""),
    ("how_long", "N", "How many UPI refunds did Store 014 make in 2024?", ""),
    ("how_long", "N", "What was Store 014's highest daily sales revenue in the whole of 2026?", ""),
    ("how_long", "N", "How many shipments arrived at Store 014 during the winter of 2025?", ""),
    ("how_long", "N", "How many payment attempts were declined at Store 014 in Q1 2026?", ""),
    ("how_long", "N", "How many bills did Store 014 ring up on Diwali day in 2025?", ""),
    ("how_long", "N", "How many complaints did Store 014 get in March 2026?", ""),
    ("not_happen", "N", "How many bills had an item that the shopper scanned and then put back?", ""),
    ("not_happen", "N", "How many shipments were due at Store 014 in June 2026 but never turned up?", ""),
    ("not_happen", "N", "How many shelf-audit rows missed a product that was on the shelf but hidden behind another?", ""),
    ("not_happen", "N", "How many UPI refunds did the customer's bank reject in June 2026?", ""),
    ("not_happen", "N", "How many payment attempts at the tills timed out before the shopper pressed pay in June 2026?", ""),
    ("not_happen", "N", "How many bills in June 2026 had a coupon the shopper forgot to bring?", ""),
    ("not_happen", "N", "How many stock counts at Store 014 were skipped in June 2026?", ""),
    ("who", "N", "How many bills were rung up by trainee cashiers at Store 014 in June 2026?", ""),
    ("who", "N", "How many of June 2026's complaints came from the same customer?", ""),
    ("who", "N", "How many of June 2026's shipments were driven by contract drivers?", ""),
    ("who", "N", "How many UPI refunds in June 2026 were approved by the store manager personally?", ""),
    ("why", "N", "How many write-off lines in June 2026 were caused by power cuts?", ""),
    ("why", "N", "How many declined payment attempts in June 2026 were due to insufficient balance?", ""),
    ("why", "N", "What share of June 2026's UPI refunds were due to staff error?", ""),
    ("why", "N", "How many shipments arrived late in June 2026 because of traffic?", ""),
    ("else", "N", "How many bills would Store 014 ring up on a rainy day?", ""),
    ("else", "N", "What is Store 014's customer satisfaction score?", ""),
    ("else", "N", "How many units of milk did the dairy supplier fail to deliver to Store 014 in June 2026?", ""),
    ("else", "N", "What is the average basket size at the competitor across the road from Store 014?", ""),
    ("else", "N", "How many stock counts does the chain's head office require each month?", ""),
    ("else", "N", "How many metres of shelf space does Store 014 give to atta?", ""),
    ("else", "N", "How many bills will Store 014 ring up next Diwali?", ""),
    ("who", "P", "How many customers paid by UPI at Store 014 in June 2026?", "UPI payment attempts are recorded, but a payment is not a customer."),
    ("else", "P", "What was Store 014's gross margin on bread in June 2026?", "Selling price minus the one cost per product gives a list margin; real purchase cost is not recorded."),
    ("not_happen", "P", "On how many days in June 2026 did the 5 kg atta shelf look empty at the 11:00 audit?", "Audits run twice a week, so only audited days can be said."),
    ("how_long", "P", "What was the average basket value at Store 014 over May and June 2026?", "Till lines start on 4 May 2026, so the average covers 4 May to 28 June."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, prods = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("products.csv")
sh, ref, wo = rows("shipments-june.csv"), rows("upi-refunds-june.csv"), rows("write-offs-june.csv")
CONTROLS = [
    ("How many units of sunflower oil were sold at Store 014 in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "OIL-SUN-1L"), 0, "daily-sales-june.csv"),
    ("What was the largest net UPI settlement received in a single day in June 2026, in rupees?", max(float(r["net_inr"]) for r in rows("upi-settlements-june.csv")), 0.01, "upi-settlements-june.csv"),
    ("How many cash payment attempts were approved at the tills in June 2026?", sum(r["tender"] == "cash" and r["till_status"] == "approved" for r in pays), 0, "pos-payments-june.csv"),
    ("How many shipments were dispatched before 05:00 in June 2026?", sum(int(r["dispatched_ts"][11:13]) < 5 for r in sh), 0, "shipments-june.csv"),
    ("How many fresh-delivery rows are there for curd in June 2026?", sum(r["sku"] == "CURD-500G" for r in rows("fresh-deliveries-june.csv")), 0, "fresh-deliveries-june.csv"),
    ("How many UPI refunds in June 2026 were triggered by a customer complaint?", sum(r["trigger"] == "customer complaint" for r in ref), 0, "upi-refunds-june.csv"),
    ("How many goods-receipt lines in June 2026 were booked for 5 kg atta?", sum(r["sku_booked"] == "ATTA-WW-5KG" for r in rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("How many units of toned milk were written off in June 2026?", sum(int(r["units"]) for r in wo if r["sku"] == "MILK-TONED-500ML"), 0, "write-offs-june.csv"),
    ("What is the average selling price across all of Store 014's products, in rupees?", round(sum(float(r["price_inr"]) for r in prods) / len(prods), 2), 0.01, "products.csv"),
    ("How many shelf-audit rows in June 2026 show toned milk as on shelf?", sum(r["sku"] == "MILK-TONED-500ML" and r["status"] == "on shelf" for r in rows("shelf-audits-june.csv")), 0, "shelf-audits-june.csv"),
    ("How many store order lines were created for sugar in June 2026?", sum(r["sku"] == "SUGAR-1KG" for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("How many pallets did shipment SHP-260601 carry?", int(next(r["pallets"] for r in sh if r["shipment_id"] == "SHP-260601")), 0, "shipments-june.csv"),
    ("On how many days in June 2026 did Store 014 receive a UPI settlement?", len({r["settlement_date"] for r in rows("upi-settlements-june.csv")}), 0, "upi-settlements-june.csv"),
    ("What was the total number of units on the shipping notices in June 2026?", sum(int(r["units"]) for r in rows("shipping-notice-lines-june.csv")), 0, "shipping-notice-lines-june.csv"),
    ("How many complaints in June 2026 were about a debit while the till said failed?", sum(r["kind"] == "debited but the till said failed" for r in rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many forecast rows are there for 5 kg atta in June 2026?", sum(r["sku"] == "ATTA-WW-5KG" for r in rows("forecasts-june.csv")), 0, "forecasts-june.csv"),
]
out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout4", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    assert truth != 0, q
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
(HERE / "questions-holdout4.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
