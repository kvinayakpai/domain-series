"""Build refusal-bench/questions-holdout8.json: eighth set, supplied by the owner (37 questions), labels fixed BEFORE any run.
Labels: N = must be refused; A = must be answered correctly; E = either is acceptable but any number given must be right.
python3 refusal-bench/build_holdout8.py"""
import json
from pathlib import Path
HERE = Path(__file__).parent
QS = """How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?
Which shelf audits found an item empty while the hourly book showed stock above zero?
On which days did any item's closing book stock go below zero?
Which stock counts disagreed with the book stock by more than 2%?
Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?
What time did toned milk record its last sale each day, and how many pouches were written off?
Why did 5 kg atta sales fall in the week of 8 June?
Was 5 kg atta in stock on Thursday 11 June?
Are shoppers switching from 5 kg to 1 kg atta?
What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?
What has daily demand for 5 kg atta been in June so far?
How many shoppers left without 5 kg atta, and what were the lost sales in June?
How many of June's deliveries arrived inside their 06:00–06:30 slot?
How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?
What was the case fill rate across June's store orders according to the shipping notices?
What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?
Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?
Which goods receipts did not survive the next stock count within a week?
Was the 22 June delivery on time and in full?
What was Store 014's OTIF from the warehouse in June?
Why was 5 kg atta off the shelf from 23 to 26 June?
Is the 5 kg atta missing at the store theft?
Which delivery, pallet (SSCC), and line should the store raise a claim against?
How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?
How many UPI payments did the tills attempt in June?
How many UPI attempts timed out (failed: no response) without receiving an RRN?
Which successes in the provider's UPI report have no matching approved payment at the till?
Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?
How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?
Which customers were charged three times for a single bill?
Did any customer pay twice in June, and how many?
What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?
Why are 17 UPI credits from 20 and 21 June sitting in suspense?
How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?
Was the store's UPI technical decline rate acceptable in June?
Which customers (by RRN) should the store refund now, without waiting for a complaint?
At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?
Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?""".split("\n")
TRUTH = {13: ("E", 23, "shipments-june.csv: arrived between slot_start and slot_end (all slots are 06:00-06:30)"),
         25: ("A", 19166, "pos-payments-june.csv: UPI attempts, all statuses"),
         26: ("E", 48, "pos-payments-june.csv: UPI, till_status 'failed: no response'")}
out = []
for i, q in enumerate(QS, 1):
    lab, truth, src = TRUTH.get(i, ("N", None, ""))
    x = {"id": f"{lab}{i:02d}", "label": lab, "group": "holdout8", "gap": "owner", "question": q, "proxy_note": ""}
    if truth is not None: x.update(truth=truth, tolerance=0, source=src)
    out.append(x)
(HERE / "questions-holdout8.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), {k: sum(x["label"] == k for x in out) for k in "NAE"})
