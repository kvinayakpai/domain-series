"""Build refusal-bench/questions-paraphrase.json: a paraphrase set for the thin model layer: typos, filler words, chatty and tempting wording
and never used to adjust them.   python3 refusal-bench/build_paraphrase.py"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    ("N", "How many shoppers came in on 13 June 2026 and left without paying?", ""),
    ("N", "Hey, how many sacks of sugar did customer households buy in June 2026?", ""),
    ("N", "Which supplier sent us the late truck on SHP-260606?", ""),
    ("N", "How many folks complained about double debits twice?", ""),
    ("N", "Why did the cash payments dip in June 2026?", ""),
    ("N", "How many packets of sugar would we have sold with no stockouts in June 2026?", ""),
    ("N", "Roughly how many refunds will we make next month?", ""),
    ("N", "how many bills did we do on diwali", ""),
    ("P", "How many people paid by card at the tills in June 2026?", "Payments are recorded, a payment is not a person."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, prods = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("products.csv")
sh, ref, wo = rows("shipments-june.csv"), rows("upi-refunds-june.csv"), rows("write-offs-june.csv")
CONTROLS = [
    ("Hey, could you tell me how many UPI refudns Store 014 made in June 2026?", sum(r["trigger"] == "customer complaint" for r in ref) if False else len(ref), 0, "upi-refunds-june.csv"),
    ("how many shipmnets were dispatched before 05:00 in June 2026", sum(r["dispatched_ts"][11:13] < "05" for r in sh), 0, "shipments-june.csv"),
    ("What was the total revnue from toned milk in June 2026, in rupees?", round(sum(float(r["revenue_inr"]) for r in ds if r["sku"] == "MILK-TONED-500ML"), 2), 0.01, "daily-sales-june.csv"),
    ("Please can you tell me the number of cash payment attemps that were approved in June 2026?", sum(r["tender"] == "cash" and r["till_status"] == "approved" for r in pays), 0, "pos-payments-june.csv"),
    ("How many units of sunflwer oil were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "OIL-SUN-1L"), 0, "daily-sales-june.csv"),
    ("What was the biggest single UPI refnd in June 2026, in rupees?", max(float(r["amount_inr"]) for r in ref), 0.01, "upi-refunds-june.csv"),
    ("how many pouches of toned milk were sold in June 2026", sum(int(r["units_sold"]) for r in ds if r["sku"] == "MILK-TONED-500ML"), 0, "daily-sales-june.csv"),
    ("How many packets of sugar were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "SUGAR-1KG"), 0, "daily-sales-june.csv"),
    ("Could you tell me how many store order lines were creatd for toor dal in June 2026?", sum(r["sku"] == "DAL-TOOR-1KG" for r in rows("store-orders-june.csv")), 0, "store-orders-june.csv"),
    ("What is the sellng price of 5 kg atta in rupees?", 265.0, 0.01, "products.csv"),
    ("How many complaints in June 2026 were about being charged twce?", sum(r["kind"] == "charged twice" for r in rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many shelf-audit rows in June 2026 show 5 kg atta as empy?", sum(r["sku"] == "ATTA-WW-5KG" and r["status"] == "empty" for r in rows("shelf-audits-june.csv")), 0, "shelf-audits-june.csv"),
    ("hi, what's the total net UPI amount settled in June 2026?", round(sum(float(r["net_inr"]) for r in rows("upi-settlements-june.csv")), 2), 0.01, "upi-settlements-june.csv"),
    ("How many goods-receipt lines in June 2026 were booked for 5 kg atta pelase?", sum(r["sku_booked"] == "ATTA-WW-5KG" for r in rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("On how many days in June 2026 did we recieve a UPI settlement?", len({r["settlement_date"] for r in rows("upi-settlements-june.csv")}), 0, "upi-settlements-june.csv"),
    ("How many fresh-delivery rows are there for curd in June 2026 thanks", sum(r["sku"] == "CURD-500G" for r in rows("fresh-deliveries-june.csv")), 0, "fresh-deliveries-june.csv"),
]
out = []
for i, (label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "paraphrase", "gap": "", "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    assert truth != 0, q
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
(HERE / "questions-paraphrase.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
