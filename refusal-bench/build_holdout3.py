"""Build refusal-bench/questions-holdout3.json: a third question set, written after the guard (refusal-bench/guards) was frozen.

Purpose: a fair test of the deterministic guard and its certified-measure allowlist. Written to stress it: unanswerable questions that
name countable things the tables hold (bills, refunds, shipments) and answerable controls phrased in ways the allowlist may not expect.
  N 29, P 3, A 12.   python3 refusal-bench/build_holdout3.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "public" / "data" / "india-grocery"

Q = [
    ("how_long", "N", "How many bills did Store 014 ring up in the week of 20 April 2026?", ""),
    ("how_long", "N", "What was the total of Store 014's UPI refunds in the first half of 2026?", ""),
    ("how_long", "N", "How many shipments arrived at Store 014 in July 2026?", ""),
    ("how_long", "N", "How many write-off lines were recorded at Store 014 in 2025?", ""),
    ("how_long", "N", "What was the net UPI amount settled to Store 014 in May 2026?", ""),
    ("how_long", "N", "How many payment attempts were declined at Store 014 over the last three months?", ""),
    ("how_long", "N", "How many bills did Store 014 ring up on 1 May 2026?", ""),
    ("not_happen", "N", "How many bills would Store 014 have rung up in June 2026 if the milk had never run out?", ""),
    ("not_happen", "N", "How many shoppers left a bill unpaid at the till in June 2026?", ""),
    ("not_happen", "N", "How many complaints did customers decide not to file at Store 014 in June 2026?", ""),
    ("not_happen", "N", "How many shelf-audit rows would have shown empty if the audit had been done every hour?", ""),
    ("not_happen", "N", "How many write-off lines in June 2026 were later reversed after a recount?", ""),
    ("not_happen", "N", "How many UPI refunds in June 2026 did the customer request and then withdraw?", ""),
    ("not_happen", "N", "How many bills in June 2026 did a customer start paying for with a wallet that Store 014 does not take?", ""),
    ("who", "N", "Which cashier rang up the 5,000th bill of June 2026?", ""),
    ("who", "N", "How many of June's UPI refunds went to customers who had complained before?", ""),
    ("who", "N", "How many bills in June 2026 were paid by regulars?", ""),
    ("who", "N", "Name the supplier behind each June shipment.", ""),
    ("why", "N", "Why did the UPI settlement on 9 June 2026 come in lower than the day before?", ""),
    ("why", "N", "What made the shipment on 12 June 2026 arrive late?", ""),
    ("why", "N", "How many payment attempts in June 2026 failed because the till froze?", ""),
    ("else", "N", "How many bills would a competitor's store nearby have rung up in June 2026?", ""),
    ("else", "N", "What does a shelf-stacker at Store 014 earn per hour?", ""),
    ("else", "N", "How full was the car park at Store 014 on weekends in June 2026?", ""),
    ("else", "N", "Is the milk fridge at Store 014 energy efficient?", ""),
    ("else", "N", "How many sales did Store 014 lose to the road closure on 14 June 2026?", ""),
    ("else", "N", "What is the carbon cost of the June 2026 shipments?", ""),
    ("else", "N", "How many units of rice did Store 014's rivals sell in June 2026?", ""),
    ("else", "N", "How many bills will Store 014 ring up in July 2026?", ""),
    ("who", "P", "How many shoppers paid in cash at Store 014 in June 2026?", "Cash payment attempts are recorded, but a payment is not a shopper."),
    ("else", "P", "What was the profit on Store 014's June 2026 sales of rice?", "Selling price minus the one cost value per product gives a list margin; real purchase cost is not recorded."),
    ("how_long", "P", "How many bags of 5 kg atta did Store 014 sell per day on average in May and June 2026?", "Till lines start on 4 May, so the average covers 4 May to 28 June; daily sales cover June only."),
]


def rows(name):
    return list(csv.DictReader(open(DATA / name)))


ds, pays, pl = rows("daily-sales-june.csv"), rows("pos-payments-june.csv"), rows("pos-lines-may-june.csv")
sh, sc = rows("shipments-june.csv"), rows("stock-counts-june.csv")
per_bill = Counter(r["bill_id"] for r in pays)
CONTROLS = [
    ("How many bills did Store 014 ring up in June 2026?", len({r["bill_id"] for r in pl if r["bill_ts"] >= "2026-06-01"}), 0, "pos-lines-may-june.csv"),
    ("How much did Store 014 sell of white bread in June 2026, in rupees?", round(sum(float(r["revenue_inr"]) for r in ds if r["sku"] == "BREAD-WHITE-400G"), 2), 1, "daily-sales-june.csv"),
    ("What was the biggest single UPI refund in June 2026, in rupees?", max(float(r["amount_inr"]) for r in rows("upi-refunds-june.csv")), 0.01, "upi-refunds-june.csv"),
    ("How many customer complaints in June 2026 were about being charged twice?", sum(r["kind"] == "charged twice" for r in rows("customer-complaints-june.csv")), 0, "customer-complaints-june.csv"),
    ("How many shipments arrived on or before the end of their slot in June 2026?", sum(r["arrived_ts"] <= r["slot_end"] for r in sh), 0, "shipments-june.csv"),
    ("How many different products were written off in June 2026?", len({r["sku"] for r in rows("write-offs-june.csv")}), 0, "write-offs-june.csv"),
    ("How many card payment attempts were declined at the tills in June 2026?", sum(r["tender"] == "card" and r["till_status"] == "declined" for r in pays), 0, "pos-payments-june.csv"),
    ("What was the lowest daily revenue in rupees for 1 kg sugar in June 2026?", min(float(r["revenue_inr"]) for r in ds if r["sku"] == "SUGAR-1KG"), 0.01, "daily-sales-june.csv"),
    ("How many stock counts in June 2026 found a difference between book and counted stock?", sum(int(r["adjustment"]) != 0 for r in sc), 0, "stock-counts-june.csv"),
    ("How many UPI settlements did Store 014 receive in June 2026?", len(rows("upi-settlements-june.csv")), 0, "upi-settlements-june.csv"),
    ("How many units of 5 kg rice were sold in June 2026?", sum(int(r["units_sold"]) for r in ds if r["sku"] == "RICE-SM-5KG"), 0, "daily-sales-june.csv"),
    ("How many bills had two or more payment attempts in June 2026?", sum(v >= 2 for v in per_bill.values()), 0, "pos-payments-june.csv"),
]
out = []
for i, (gap, label, q, proxy) in enumerate(Q, 1):
    out.append({"id": f"{label}{i:02d}", "label": label, "group": "holdout3", "gap": gap, "question": q, "proxy_note": proxy})
for j, (q, truth, tol, src) in enumerate(CONTROLS, 1):
    assert truth != 0, q
    out.append({"id": f"A{j:02d}", "label": "A", "group": "control", "gap": "", "question": q, "truth": truth, "tolerance": tol, "source": src})
(HERE / "questions-holdout3.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "questions;", {k: sum(x["label"] == k for x in out) for k in "NPA"}, [c["truth"] for c in out if c["label"] == "A"])
