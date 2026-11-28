"""Build refusal-bench/questions-holdout9.json: ninth set, supplied by the owner (17 questions, each carrying a false or unanswerable premise).
Every one must be refused (label N). Labels fixed before any run.   python3 refusal-bench/build_holdout9.py"""
import json
from pathlib import Path
QS = """Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?
Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?
How many bags of 5 kg atta were sold in June 2023?
Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?
Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?
Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?
If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?
Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?
Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?
Which pallet on the 22 June shipment failed its dispatch weight check?
If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?
What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?
Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?
Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.
Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?
Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?
Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?""".split("\n")
out = [{"id": f"N{i:02d}", "label": "N", "group": "holdout9", "gap": "owner", "question": q, "proxy_note": ""} for i, q in enumerate(QS, 1)]
(Path(__file__).parent / "questions-holdout9.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out))
