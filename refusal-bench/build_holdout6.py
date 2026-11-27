"""Build refusal-bench/questions-holdout6.json: a sixth question set, written after the ontology and the layered resolver were frozen (commit a838eb5)
and never used to adjust them.   python3 refusal-bench/build_holdout6.py"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    ("how_long", "N", "How many bills did Store 014 ring up in January 2026?", ""),
    ("how_long", "N", "What was the total value of UPI settlements in the second half of 2025?", ""),
    ("how_long", "N", "How many shipments arrived in the last week of May 2026?", ""),
    ("how_long", "N", "How many UPI refunds has Store 014 made over the past three years?", ""),
    ("how_long", "N", "What was the highest daily revenue for milk in 2024?", ""),
    ("how_long", "N", "How many bills were rung up on 1 May 2026?", ""),
    ("how_long", "N", "How many cash payment attempts were approved in April 2026?", ""),
    ("not_happen", "N", "How many bills were abandoned at the till in June 2026?", ""),
    ("not_happen", "N", "How many units of sugar would Store 014 have sold in June 2026 if it had never run out?", ""),
    ("not_happen", "N", "How many shoppers asked for ghee and went away empty-handed in June 2026?", ""),
    ("not_happen", "N", "How many UPI payments were started and then cancelled by the shopper in June 2026?", ""),
    ("not_happen", "N", "How many shipments were scheduled for June 2026 but cancelled by the warehouse?", ""),
    ("not_happen", "N", "How many store orders did the warehouse refuse to fill in June 2026?", ""),
    ("not_happen", "N", "How many bills in June 2026 had an item that was scanned twice by mistake?", ""),
    ("who", "N", "Which cashier had the most declined payment attempts in June 2026?", ""),
    ("who", "N", "How many different customers complained in June 2026?", ""),
    ("who", "N", "Who drove the truck for shipment SHP-260612?", ""),
    ("who", "N", "How many of June 2026's bills were paid by regular shoppers?", ""),
    ("who", "N", "Which supplier delivered the curd on route R-12 in June 2026?", ""),
    ("why", "N", "Why were so many units of toned milk written off in June 2026?", ""),
    ("why", "N", "What was the main reason UPI payments failed in June 2026?", ""),
    ("why", "N", "How many shipments were late in June 2026 due to the road works?", ""),
    ("why", "N", "How many stock counts in June 2026 found a difference because of theft?", ""),
    ("else", "N", "What is the monthly electricity bill of Store 014?", ""),
    ("else", "N", "How many units of atta did the competitor sell in June 2026?", ""),
    ("else", "N", "What is the cost of a shelf in Store 014?", ""),
    ("else", "N", "How many units of biscuits were sold in June 2026?", ""),
    ("else", "N", "Which festival caused the sales spike in June 2026?", ""),
    ("else", "N", "How many people live within one kilometre of Store 014?", ""),
    ("mixed", "N", "How many UPI refunds were made in June 2026, and who approved each of them?", ""),
    ("mixed", "N", "How many units of sugar were sold in June 2026 and why did sales fall in the last week?", ""),
    ("mixed", "N", "How many shipments arrived on time in June 2026 according to the drivers?", ""),
    ("ambiguous", "N", "How many units of atta were sold in June 2026?", "atta comes in three sizes: the question does not say which"),
    ("ambiguous", "N", "How many units of milk were sold in June 2026?", "toned and full cream milk are different products"),
    ("who", "P", "How many people paid by cash at Store 014 in June 2026?", "Payments are recorded, a payment is not a person."),
    ("else", "P", "What was the margin on curd at Store 014 in June 2026?", "Price minus the single cost per product gives a list margin only."),
    ("not_happen", "P", "On how many days in June 2026 did the sugar shelf look empty at the 11:00 audit?", "Audits run twice a week, so only audited days can be said."),
    ("how_long", "P", "What was the average bill value at Store 014 from 4 May to 28 June 2026?", "Till lines start on 4 May; a bill's value is a stand-in for what a shopper spent."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, prods = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("products.csv")
sh, ref, wo = rows("shipments-june.csv"), rows("upi-refunds-june.csv"), rows("write-offs-june.csv")
CONTROLS = [
    ("How many units of toor dal were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "DAL-TOOR-1KG"), 0, "daily-sales-june.csv"),
    ("What was the total revenue from sugar in June 2026, in rupees?", round(sum(float(r["revenue_inr"]) for r in ds if r["sku"] == "SUGAR-1KG"), 2), 0.01, "daily-sales-june.csv"),
    ("How many units were written off as damaged in June 2026?", sum(int(r["units"]) for r in wo if r["reason"] == "damaged"), 0, "write-offs-june.csv"),
    ("What was the average UPI refund amount in June 2026, in rupees?", round(sum(float(r["amount_inr"]) for r in ref) / len(ref), 2), 0.01, "upi-refunds-june.csv"),
    ("What was the smallest net UPI settlement received in a single day in June 2026, in rupees?", min(float(r["net_inr"]) for r in rows("upi-settlements-june.csv")), 0.01, "upi-settlements-june.csv"),
    ("How many UPI payment attempts failed at the tills in June 2026?", sum(r["tender"] == "UPI" and r["till_status"] == "failed" for r in pays), 0, "pos-payments-june.csv"),
    ("How many UPI payment attempts had the status failed: no response in June 2026?", sum(r["tender"] == "UPI" and r["till_status"] == "failed: no response" for r in pays), 0, "pos-payments-june.csv"),
    ("How many shipments arrived after the end of their slot in June 2026?", sum(r["arrived_ts"] > r["slot_end"] for r in sh), 0, "shipments-june.csv"),
    ("How many shipments were dispatched before 04:31 in June 2026?", sum(r["dispatched_ts"][11:16] < "04:31" for r in sh), 0, "shipments-june.csv"),
    ("What was the total number of cases on the shipping notices in June 2026?", sum(int(r["cases"]) for r in rows("shipping-notice-lines-june.csv")), 0, "shipping-notice-lines-june.csv"),
    ("What was the total number of crates delivered on route R-12 in June 2026?", sum(int(r["crates"]) for r in rows("fresh-deliveries-june.csv") if r["route"] == "R-12"), 0, "fresh-deliveries-june.csv"),
    ("How many fresh-delivery rows are there for route R-12 in June 2026?", sum(r["route"] == "R-12" for r in rows("fresh-deliveries-june.csv")), 0, "fresh-deliveries-june.csv"),
    ("What is the cost of 1 kg sugar, in rupees?", float(next(r["cost_inr"] for r in prods if r["sku"] == "SUGAR-1KG")), 0.01, "products.csv"),
    ("How many store order lines were created for toor dal in June 2026?", sum(r["sku"] == "DAL-TOOR-1KG" for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("How many goods-receipt lines in June 2026 were booked for rice?", sum(r["sku_booked"] == "RICE-SM-5KG" for r in rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("On how many days in June 2026 were curd units written off?", len({r["date"] for r in wo if r["sku"] == "CURD-500G"}), 0, "write-offs-june.csv"),
    ("How many forecast rows are there for sunflower oil in June 2026?", sum(r["sku"] == "OIL-SUN-1L" for r in rows("forecasts-june.csv")), 0, "forecasts-june.csv"),
    ("What was the highest number of units of sunflower oil sold on a single day in June 2026?", max(int(r["units_sold"]) for r in ds if r["sku"] == "OIL-SUN-1L"), 0, "daily-sales-june.csv"),
    ("How many complaints in June 2026 were refunded after the store matched the credit by hand?", sum(r["resolution"] == "refunded after the store matched the credit by hand" for r in rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many pick confirmations were recorded in June 2026?", len(rows("dc-pick-confirmations-june.csv")), 0, "dc-pick-confirmations-june.csv"),
    ("How many pallets did shipment SHP-260603 carry?", int(next(r["pallets"] for r in sh if r["shipment_id"] == "SHP-260603")), 0, "shipments-june.csv"),
    ("How many distinct bills had a cash payment attempt in June 2026?", len({r["bill_id"] for r in pays if r["tender"] == "cash"}), 0, "pos-payments-june.csv"),
    ("How many distinct bills were rung up from 4 May to 10 May 2026?", len({r["bill_id"] for r in rows("pos-lines-may-june.csv") if "2026-05-04" <= r["bill_ts"][:10] <= "2026-05-10"}), 0, "pos-lines-may-june.csv"),
    ("How many products have a cost above 100 rupees?", sum(float(r["cost_inr"]) > 100 for r in prods), 0, "products.csv"),
    ("How many card payment attempts were approved from 15 June to 20 June 2026?", sum(r["tender"] == "card" and r["till_status"] == "approved" and "2026-06-15" <= r["ts"][:10] <= "2026-06-20" for r in pays), 0, "pos-payments-june.csv"),
    ("How many units of curd were written off in June 2026?", sum(int(r["units"]) for r in wo if r["sku"] == "CURD-500G"), 0, "write-offs-june.csv"),
    ("How many shelf-audit rows in June 2026 show rice as on shelf?", sum(r["sku"] == "RICE-SM-5KG" and r["status"] == "on shelf" for r in rows("shelf-audits-june.csv")), 0, "shelf-audits-june.csv"),
    ("What is the selling price of toor dal, in rupees?", float(next(r["price_inr"] for r in prods if r["sku"] == "DAL-TOOR-1KG")), 0.01, "products.csv"),
    ("How many UPI refunds in June 2026 were completed? ", sum(r["completed_ts"] != "" for r in ref), 0, "upi-refunds-june.csv"),
    ("How many transactions in the UPI service provider's report for June 2026 have the status returned?", sum(r["status"] == "returned" for r in rows("psp-upi-report-june.csv")), 0, "psp-upi-report-june.csv"),
]
out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout6", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    assert truth != 0, q
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
(HERE / "questions-holdout6.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
