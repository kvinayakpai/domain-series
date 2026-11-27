"""Build refusal-bench/questions-holdout7.json: a seventh question set, written after the ontology and the layered resolver were frozen (the commit before this file)
and never used to adjust them.   python3 refusal-bench/build_holdout7.py"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    ("how_long", "N", "How many bills did Store 014 ring up in March 2026?", ""),
    ("how_long", "N", "What was the average daily revenue for atta over the last year?", ""),
    ("how_long", "N", "How many write-offs were recorded on 30 April 2026?", ""),
    ("how_long", "N", "How many complaints did Store 014 receive in the whole of 2025?", ""),
    ("how_long", "N", "How many shipments arrived in July 2026?", ""),
    ("how_long", "N", "How many UPI settlements were received this year?", ""),
    ("not_happen", "N", "How many bills had an item the shopper decided not to buy at the till in June 2026?", ""),
    ("not_happen", "N", "How many units of curd were never delivered on route R-07 in June 2026?", ""),
    ("not_happen", "N", "How many payment attempts at the tills were never completed in June 2026?", ""),
    ("not_happen", "N", "How many shoppers came in during June 2026 and bought nothing?", ""),
    ("not_happen", "N", "How many times did the till refuse a card in June 2026 because the machine was offline?", ""),
    ("not_happen", "N", "How many shelf-audit rows missed a product because the auditor skipped the aisle?", ""),
    ("who", "N", "Which route driver was late most often in June 2026?", ""),
    ("who", "N", "How many bills in June 2026 were paid by the same shopper twice?", ""),
    ("who", "N", "Which manager requested the stock counts after complaints?", ""),
    ("who", "N", "How many children's snacks were bought by families in June 2026?", ""),
    ("who", "N", "Who complained about being charged twice?", ""),
    ("why", "N", "Why was the sugar shelf empty at an audit in June 2026?", ""),
    ("why", "N", "What was the reason for the largest write-off in June 2026?", ""),
    ("why", "N", "How many UPI payments failed in June 2026 because of poor network?", ""),
    ("why", "N", "How many bills in June 2026 were small because shoppers were saving money?", ""),
    ("else", "N", "How many bills would Store 014 ring up next June?", ""),
    ("else", "N", "What is the average rent per square foot of Store 014?", ""),
    ("else", "N", "How many units of toor dal does the shop across the road sell in a month?", ""),
    ("else", "N", "Should Store 014 stock more milk?", ""),
    ("else", "N", "How much profit did Store 014 make in June 2026?", ""),
    ("else", "N", "How many units of cooking gas were sold in June 2026?", ""),
    ("mixed", "N", "How many shipments arrived in June 2026 and which was the most delayed driver?", ""),
    ("mixed", "N", "How many units of rice were sold in June 2026 versus last June?", ""),
    ("mixed", "N", "How many UPI refunds were made in June 2026 and what was the bank's reason for each?", ""),
    ("ambiguous", "N", "How many units of sugar or rice were sold in June 2026?", "two products in one question"),
    ("ambiguous", "N", "How many write-offs were there?", "the question names no period and no product; the whole records answer would hide the choice"),
    ("who", "P", "How many customers used UPI at the tills in June 2026?", "Payments are recorded, a payment is not a customer."),
    ("else", "P", "What was the gross margin on full cream milk in June 2026?", "Price minus the single cost per product gives a list margin only."),
    ("not_happen", "P", "On how many days in June 2026 was the toned milk shelf empty at the 11:00 audit?", "Audits run twice a week, so only audited days can be said."),
    ("how_long", "P", "What was the typical basket size from 4 May to 28 June 2026?", "Till lines start on 4 May; a bill is a stand-in for a shopper."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, prods = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("products.csv")
sh, ref, wo = rows("shipments-june.csv"), rows("upi-refunds-june.csv"), rows("write-offs-june.csv")
CONTROLS = [
    ("How many units of full cream milk were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "MILK-FC-500ML"), 0, "daily-sales-june.csv"),
    ("What was the total revenue from toned milk in June 2026, in rupees?", round(sum(float(r["revenue_inr"]) for r in ds if r["sku"] == "MILK-TONED-500ML"), 2), 0.01, "daily-sales-june.csv"),
    ("How many units of 10 kg atta were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "ATTA-WW-10KG"), 0, "daily-sales-june.csv"),
    ("What was the lowest number of units of curd sold on a single day in June 2026?", min(int(r["units_sold"]) for r in ds if r["sku"] == "CURD-500G"), 0, "daily-sales-june.csv"),
    ("What was the average number of units of bread sold per day in June 2026?", round(sum(int(r["units_sold"]) for r in ds if r["sku"] == "BREAD-WHITE-400G") / len([r for r in ds if r["sku"] == "BREAD-WHITE-400G"]), 2), 0.01, "daily-sales-june.csv"),
    ("How many card payment attempts were declined at the tills in June 2026?", sum(r["tender"] == "card" and r["till_status"] == "declined" for r in pays), 0, "pos-payments-june.csv"),
    ("How many UPI payment attempts were approved at the tills in June 2026?", sum(r["tender"] == "UPI" and r["till_status"] == "approved" for r in pays), 0, "pos-payments-june.csv"),
    ("What was the total amount of cash payment attempts at the tills in June 2026, in rupees?", round(sum(float(r["amount_inr"]) for r in pays if r["tender"] == "cash"), 2), 0.01, "pos-payments-june.csv"),
    ("How many shipments arrived on or before the end of their slot in June 2026?", sum(r["arrived_ts"] <= r["slot_end"] for r in sh), 0, "shipments-june.csv"),
    ("What was the total number of pallets on all shipments in June 2026?", sum(int(r["pallets"]) for r in sh), 0, "shipments-june.csv"),
    ("How many pallets are there in June 2026?", len(rows("pallets-june.csv")), 0, "pallets-june.csv"),
    ("What was the total weight in kg on the pallet notices in June 2026?", round(sum(float(r["notice_kg"]) for r in rows("pallets-june.csv")), 2), 0.01, "pallets-june.csv"),
    ("How many fresh-delivery rows are there for toned milk in June 2026?", sum(r["sku"] == "MILK-TONED-500ML" for r in rows("fresh-deliveries-june.csv")), 0, "fresh-deliveries-june.csv"),
    ("What was the total number of units of curd delivered in June 2026?", sum(int(r["units"]) for r in rows("fresh-deliveries-june.csv") if r["sku"] == "CURD-500G"), 0, "fresh-deliveries-june.csv"),
    ("How many goods-receipt lines in June 2026 were booked for toor dal?", sum(r["sku_booked"] == "DAL-TOOR-1KG" for r in rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("What was the total number of units booked on goods-receipt lines in June 2026?", sum(int(r["units_booked"]) for r in rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("How many store order lines were created for 1 kg atta in June 2026?", sum(r["sku"] == "ATTA-WW-1KG" for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("What was the total number of cases ordered by Store 014 in June 2026?", sum(int(r["cases"]) for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("How many stock counts in June 2026 were scheduled full counts?", sum(r["trigger"] == "scheduled full count" for r in rows("stock-counts-june.csv")), 0, "stock-counts-june.csv"),
    ("How many UPI refunds in June 2026 had been completed?", sum(r["completed_ts"] != "" for r in ref), 0, "upi-refunds-june.csv"),
    ("What was the total net UPI amount settled in June 2026, in rupees?", round(sum(float(r["net_inr"]) for r in rows("upi-settlements-june.csv")), 2), 0.01, "upi-settlements-june.csv"),
    ("What was the total gross UPI amount settled to Store 014 in June 2026, in rupees?", round(sum(float(r["gross_inr"]) for r in rows("upi-settlements-june.csv")), 2), 0.01, "upi-settlements-june.csv"),
    ("How many complaints in June 2026 were about payments?", len(rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many complaints in June 2026 were about a debit while the till said failed?", sum(r["kind"] == "debited but the till said failed" for r in rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many shelf-audit rows in June 2026 show bread as on shelf?", sum(r["sku"] == "BREAD-WHITE-400G" and r["status"] == "on shelf" for r in rows("shelf-audits-june.csv")), 0, "shelf-audits-june.csv"),
    ("How many write-off lines were there for toned milk in June 2026?", sum(r["sku"] == "MILK-TONED-500ML" for r in wo), 0, "write-offs-june.csv"),
    ("On how many days in June 2026 did Store 014 write off toned milk?", len({r["date"] for r in wo if r["sku"] == "MILK-TONED-500ML"}), 0, "write-offs-june.csv"),
    ("What is the selling price of full cream milk, in rupees?", float(next(r["price_inr"] for r in prods if r["sku"] == "MILK-FC-500ML")), 0.01, "products.csv"),
    ("What is the average cost of Store 014's products, in rupees?", round(sum(float(r["cost_inr"]) for r in prods) / len(prods), 2), 0.01, "products.csv"),
    ("How many UPI transactions in the UPI service provider's report for June 2026 have the status failed?", sum(r["status"] == "failed" for r in rows("psp-upi-report-june.csv")), 0, "psp-upi-report-june.csv"),
    ("How many distinct bills had a UPI payment attempt from 10 June to 14 June 2026?", len({r["bill_id"] for r in pays if r["tender"] == "UPI" and "2026-06-10" <= r["ts"][:10] <= "2026-06-14"}), 0, "pos-payments-june.csv"),
]
out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout7", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    assert truth != 0, q
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
(HERE / "questions-holdout7.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
