"""Build refusal-bench/questions-holdout5.json: a fifth question set, written after the guard and the certified query catalogue were frozen (commit dd39b48)
and never used to adjust them.   python3 refusal-bench/build_holdout5.py"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    ("how_long", "N", "How many bills did Store 014 ring up in July 2026?", ""),
    ("how_long", "N", "What were Store 014's total UPI settlements in the first quarter of 2026?", ""),
    ("how_long", "N", "How many complaints has Store 014 received since it opened?", ""),
    ("how_long", "N", "How many units of curd were sold in 2025?", ""),
    ("how_long", "N", "What was the busiest day for bills at Store 014 last December?", ""),
    ("how_long", "N", "How many write-off lines were recorded in the week of 20 April 2026?", ""),
    ("how_long", "N", "How many shipments arrived at Store 014 on 2 May 2026?", ""),
    ("not_happen", "N", "How many shoppers came to Store 014 in June 2026 and left because the queue was long?", ""),
    ("not_happen", "N", "How many units of milk would Store 014 have sold if it had never run out?", ""),
    ("not_happen", "N", "How many bills in June 2026 had a product the shopper asked for that was not stocked?", ""),
    ("not_happen", "N", "How many UPI payments did customers start but never finish in June 2026?", ""),
    ("not_happen", "N", "How many pallets were left on the truck instead of being unloaded in June 2026?", ""),
    ("not_happen", "N", "How many stock counts were missed by the night staff in June 2026?", ""),
    ("not_happen", "N", "How many times did a shopper return a product after buying it in June 2026?", ""),
    ("who", "N", "Which cashier rang up the most bills at Store 014 in June 2026?", ""),
    ("who", "N", "How many shoppers made more than ten visits to Store 014 in June 2026?", ""),
    ("who", "N", "Which driver was on the truck for shipment SHP-260605?", ""),
    ("who", "N", "How many complaints in June 2026 came from senior citizens?", ""),
    ("who", "N", "Who authorised the UPI refunds in June 2026?", ""),
    ("why", "N", "Why did sales of sunflower oil fall on 14 June 2026?", ""),
    ("why", "N", "What was the main reason shipments arrived after their slot in June 2026?", ""),
    ("why", "N", "How many declined card payments in June 2026 happened because the card had expired?", ""),
    ("why", "N", "How many write-offs in June 2026 were due to a fridge breakdown?", ""),
    ("else", "N", "How much did Store 014 pay in rent in June 2026?", ""),
    ("else", "N", "How many bills would Store 014 ring up if it stayed open 24 hours?", ""),
    ("else", "N", "What price does the shop next door charge for 1 kg sugar?", ""),
    ("else", "N", "How many units of ghee were sold at Store 014 in June 2026?", ""),
    ("else", "N", "What is the temperature inside the milk fridge at Store 014?", ""),
    ("else", "N", "How many employees work at Store 014?", ""),
    ("who", "P", "How many people shopped at Store 014 in June 2026?", "Bills are recorded, but a bill is not a person."),
    ("else", "P", "What was the margin on toned milk at Store 014 in June 2026?", "Price minus the single cost per product gives a list margin only."),
    ("not_happen", "P", "On how many days in June 2026 was the curd shelf empty at the 11:00 audit?", "Audits run twice a week, so only audited days can be said."),
    ("how_long", "P", "What was the average bill value at Store 014 across May and June 2026?", "Till lines start on 4 May 2026."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, prods = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("products.csv")
sh, ref, wo = rows("shipments-june.csv"), rows("upi-refunds-june.csv"), rows("write-offs-june.csv")
CONTROLS = [
    ("How many units of full cream milk were sold at Store 014 in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "MILK-FC-500ML"), 0, "daily-sales-june.csv"),
    ("How many units of 1 kg atta were sold at Store 014 in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "ATTA-WW-1KG"), 0, "daily-sales-june.csv"),
    ("What was the total revenue from white bread at Store 014 in June 2026, in rupees?", round(sum(float(r["revenue_inr"]) for r in ds if r["sku"] == "BREAD-WHITE-400G"), 2), 0.01, "daily-sales-june.csv"),
    ("How many card payment attempts were approved at the tills in June 2026?", sum(r["tender"] == "card" and r["till_status"] == "approved" for r in pays), 0, "pos-payments-june.csv"),
    ("How many UPI payment attempts were declined at the tills in June 2026?", sum(r["tender"] == "UPI" and r["till_status"] == "declined" for r in pays), 0, "pos-payments-june.csv"),
    ("How many payment attempts at the tills had the status failed in June 2026?", sum(r["till_status"] == "failed" for r in pays), 0, "pos-payments-june.csv"),
    ("How many shipments were dispatched before 04:45 in June 2026?", sum(r["dispatched_ts"][11:16] < "04:45" for r in sh), 0, "shipments-june.csv"),
    ("How many pallets did shipment SHP-260606 carry?", int(next(r["pallets"] for r in sh if r["shipment_id"] == "SHP-260606")), 0, "shipments-june.csv"),
    ("How many fresh-delivery rows are there for white bread in June 2026?", sum(r["sku"] == "BREAD-WHITE-400G" for r in rows("fresh-deliveries-june.csv")), 0, "fresh-deliveries-june.csv"),
    ("How many units of sugar were written off in June 2026?", sum(int(r["units"]) for r in wo if r["sku"] == "SUGAR-1KG"), 0, "write-offs-june.csv"),
    ("How many write-off lines in June 2026 had the reason 'damaged'?", sum(r["reason"] == "damaged" for r in wo), 0, "write-offs-june.csv"),
    ("How many store order lines were created for rice in June 2026?", sum(r["sku"] == "RICE-SM-5KG" for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("How many goods-receipt lines in June 2026 were booked for sugar?", sum(r["sku_booked"] == "SUGAR-1KG" for r in rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("How many forecast rows are there for toor dal in June 2026?", sum(r["sku"] == "DAL-TOOR-1KG" for r in rows("forecasts-june.csv")), 0, "forecasts-june.csv"),
    ("How many shelf-audit rows in June 2026 show sugar as on shelf?", sum(r["sku"] == "SUGAR-1KG" and r["status"] == "on shelf" for r in rows("shelf-audits-june.csv")), 0, "shelf-audits-june.csv"),
    ("What was the total net UPI amount settled to Store 014 in June 2026, in rupees?", round(sum(float(r["net_inr"]) for r in rows("upi-settlements-june.csv")), 2), 0.01, "upi-settlements-june.csv"),
    ("What was the biggest single UPI refund in June 2026, in rupees?", max(float(r["amount_inr"]) for r in ref), 0.01, "upi-refunds-june.csv"),
    ("What is the selling price of 1 kg sugar, in rupees?", float(next(r["price_inr"] for r in prods if r["sku"] == "SUGAR-1KG")), 0.01, "products.csv"),
    ("How many complaints in June 2026 were about being charged twice?", sum(r["kind"] == "charged twice" for r in rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many transactions in the UPI service provider's report for June 2026 have the status success?", sum(r["status"] == "success" for r in rows("psp-upi-report-june.csv")), 0, "psp-upi-report-june.csv"),
    ("How many stock counts in June 2026 were scheduled full counts?", sum(r["trigger"] == "scheduled full count" for r in rows("stock-counts-june.csv")), 0, "stock-counts-june.csv"),
    ("How many bills had a payment attempt by card in June 2026?", len({r["bill_id"] for r in pays if r["tender"] == "card"}), 0, "pos-payments-june.csv"),
    ("What was the highest daily revenue for curd in June 2026, in rupees?", max(float(r["revenue_inr"]) for r in ds if r["sku"] == "CURD-500G"), 0.01, "daily-sales-june.csv"),
    ("How many different products had a shelf-audit row marked empty in June 2026?", len({r["sku"] for r in rows("shelf-audits-june.csv") if r["status"] == "empty"}), 0, "shelf-audits-june.csv"),
]
out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout5", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    assert truth != 0, q
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
(HERE / "questions-holdout5.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
