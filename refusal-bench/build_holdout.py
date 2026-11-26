"""Build refusal-bench/questions-holdout.json: new questions for testing the 'gaps' rule fairly.

The gaps rule (run.py, GAPS) was written from the five kinds of gap seen in the first 76 questions, so its scores on those
are an upper bound. These questions were written afterwards, one per new topic, and none repeats a topic in questions.json.
Each N question was checked against the CSV files in public/data/india-grocery to confirm they cannot answer it.

  N  the records cannot answer it: the right reply is "no record" and no number (29)
  P  the records give only a stand-in (4)
  A  controls the records answer exactly, truth computed here (10)

    python3 refusal-bench/build_holdout.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    # who
    ("who", "N", "Which staff member rang up the most bills at Store 014 in June 2026?", ""),
    ("who", "N", "Which supplier's goods were on the shipments that arrived from the warehouse in June 2026?", ""),
    ("who", "N", "How many different customers paid by UPI at Store 014 in June 2026?", ""),
    ("who", "N", "Which customers complained more than once in June 2026?", ""),
    ("who", "N", "What is the age and gender mix of Store 014's shoppers in June 2026?", ""),
    ("who", "N", "Which delivery driver was on milk route R-07 on 10 June 2026?", ""),
    # what did not happen
    ("not_happen", "N", "How many shoppers asked a staff member for a product Store 014 does not stock in June 2026?", ""),
    ("not_happen", "N", "How many bills were started at a till and cancelled before payment in June 2026?", ""),
    ("not_happen", "N", "How many shoppers walked out of Store 014 in June 2026 because the queue at the till was too long?", ""),
    ("not_happen", "N", "How many products did shoppers pick up and then put back on the shelf in June 2026?", ""),
    ("not_happen", "N", "How many shoppers asked for a cash refund and were refused in June 2026?", ""),
    ("not_happen", "N", "How many shoppers tried to pay with a card type Store 014's tills do not accept in June 2026?", ""),
    # why
    ("why", "N", "Why did shoppers return items to Store 014 in June 2026?", ""),
    ("why", "N", "What caused the damage on the units written off as damaged in June 2026: rough handling, a faulty fridge or a late delivery?", ""),
    ("why", "N", "Why did sales of toned milk fall on the days they fell in June 2026?", ""),
    ("why", "N", "What was the main reason UPI payments failed at Store 014's tills in June 2026: the customer's bank, the network or the customer?", ""),
    ("why", "N", "Why did shoppers choose the 1 kg atta pack over the 5 kg pack in June 2026?", ""),
    ("why", "N", "Why was the 28-day mean chosen as the forecast method for Store 014's products?", ""),
    # what else
    ("else", "N", "What was the temperature inside Store 014's milk fridge each day in June 2026?", ""),
    ("else", "N", "How did rainfall in June 2026 change the number of shoppers at Store 014?", ""),
    ("else", "N", "What did the nearest competitor charge for 5 kg atta in June 2026?", ""),
    ("else", "N", "What are Store 014's monthly rent and staff costs?", ""),
    ("else", "N", "How many units of 5 kg atta did the warehouse hold for other stores in June 2026?", ""),
    ("else", "N", "How many home-delivery or online orders did Store 014 take in June 2026?", ""),
    # how long
    ("how_long", "N", "How did Store 014's daily sales in June 2026 compare with June 2025?", ""),
    ("how_long", "N", "What were the average daily sales of toned milk at Store 014 over the last twelve months?", ""),
    ("how_long", "N", "How has the UPI share of payments at Store 014 trended over 2026?", ""),
    ("how_long", "N", "How many shipments arrived from the warehouse in May 2026?", ""),
    ("how_long", "N", "What was Store 014's best sales day of 2026?", ""),
    # proxy only
    ("how_long", "P", "What were Store 014's total sales in May 2026?", "Till lines start on 4 May 2026, so 4 to 31 May is a part month; 1 to 3 May are not recorded."),
    ("who", "P", "How many different people complained about being charged twice in June 2026?", "The complaints file has one row per complaint and no customer id, so rows are an upper bound on people."),
    ("how_long", "P", "On how many days of 2026 did Store 014's 5 kg atta shelf look empty at the 11:00 audit?", "Shelf audits cover June only (twice a week at 11:00), so this can only be answered for June."),
    ("else", "P", "How many units of 5 kg atta were on the shelf at 3 pm on 10 June 2026?", "Only 11:00 shelf audits (on shelf or empty) and end-of-day book stock exist; no shelf count at 3 pm."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pl = rows("daily-sales-june.csv"), rows("pos-lines-may-june.csv")
CONTROLS = [
    ("How many units of toned milk 500 ml were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "MILK-TONED-500ML"), 0, "daily-sales-june.csv"),
    ("What was the revenue in rupees from 5 kg atta in June 2026?", round(sum(float(r["revenue_inr"]) for r in ds if r["sku"] == "ATTA-WW-5KG"), 2), 1, "daily-sales-june.csv"),
    ("How many distinct bills were rung up at the tills from 4 May to 31 May 2026?", len({r["bill_id"] for r in pl if r["bill_ts"] < "2026-06-01"}), 0, "pos-lines-may-june.csv"),
    ("What was the total amount in rupees of UPI refunds made in June 2026?", round(sum(float(r["amount_inr"]) for r in rows("upi-refunds-june.csv")), 2), 1, "upi-refunds-june.csv"),
    ("How many goods-receipt lines were booked in June 2026?", len(rows("goods-receipts-june.csv")), 0, "goods-receipts-june.csv"),
    ("How many pallets arrived from the warehouse in June 2026?", len(rows("pallets-june.csv")), 0, "pallets-june.csv"),
    ("How many stock counts in June 2026 were triggered by a manager's request after complaints?", sum(r["trigger"] == "manager request after complaints" for r in rows("stock-counts-june.csv")), 0, "stock-counts-june.csv"),
    ("How many payment attempts at the tills in June 2026 had the status declined?", sum(r["till_status"] == "declined" for r in rows("pos-payments-june.csv")), 0, "pos-payments-june.csv"),
    ("On how many different days in June 2026 was at least one write-off recorded?", len({r["date"] for r in rows("write-offs-june.csv")}), 0, "write-offs-june.csv"),
    ("How many transactions in the UPI service provider's report for June 2026 have the status failed?", sum(r["status"] == "failed" for r in rows("psp-upi-report-june.csv")), 0, "psp-upi-report-june.csv"),
]

out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
assert sum(x["label"] == "N" for x in out) == 29 and sum(x["label"] == "P" for x in out) == 4
(HERE / "questions-holdout.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
