"""Build notebooks/payments.ipynb, the runnable version of the payments technical companion.

    python3 scripts/analysis/make_payments_notebook.py            # write the notebook
    python3 scripts/analysis/make_payments_notebook.py --run      # also run it on the local records and
                                                                  # check its numbers against src/data/payments-ai.json

The notebook reads the records from the site by default, so it runs as is in Colab or Jupyter.
Set STORE014_DATA to a folder or URL to read them from somewhere else.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "notebooks" / "payments.ipynb"
SITE = "https://kvinayakpai.github.io/domain-series/"

cells: list = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text.strip("\n")))


md(f"""
# Failed, but paid: the payment records

The runnable companion to [Failed, but paid]({SITE}payments/) and its [technical companion]({SITE}payments/technical/).
Everything here uses Store 014's downloadable payment records: the till's payments, the payment provider's UPI report,
the settlements, refunds and complaints for June 2026, in a fictional supermarket in Bengaluru. The answer key is read
only at the end of each section, to score what the records gave us.

Runs in a few seconds. Needs `duckdb` and `pandas` (both preinstalled in Colab).
""")

code("""
import json, os, urllib.request

import duckdb
import pandas as pd

DATA = os.environ.get("STORE014_DATA", "https://kvinayakpai.github.io/domain-series/data/india-grocery/")
FILES = {"till_payments": "pos-payments-june.csv", "psp_upi": "psp-upi-report-june.csv",
         "settlements": "upi-settlements-june.csv", "refunds": "upi-refunds-june.csv",
         "complaints": "customer-complaints-june.csv"}
TIMES = {"till_payments": ["ts"], "psp_upi": ["initiated_ts", "status_ts"], "settlements": ["settlement_date"],
         "refunds": ["requested_ts", "completed_ts"], "complaints": ["complaint_ts", "resolved_ts"]}
TEXT = {"rrn": str, "bill_ref": str, "note": str}  # RRNs are identifiers: keep them as text

con = duckdb.connect()
tables = {}
for name, file in FILES.items():
    df = pd.read_csv(DATA + file, parse_dates=TIMES.get(name, []), dtype=TEXT)
    tables[name] = df
    con.register(name, df)

def read_json(path):
    if path.startswith("http"):
        with urllib.request.urlopen(path) as f:
            return json.load(f)
    with open(path) as f:
        return json.load(f)

KEY = read_json(DATA + "answer-key-payments.json")   # for scoring only
AS_OF = "2026-06-29 09:00"                           # the month-end review

def q(sql):
    return con.execute(sql).df()

{k: len(v) for k, v in tables.items()}
""")

md("""
## 1. Tests that pass

Ten data tests on the till's payments and the provider's reports. A test passes when its query returns no rows.
""")

code('''
TESTS = {
 "Till payments: bill and attempt are unique":
   "SELECT bill_id, attempt, count(*) FROM till_payments GROUP BY ALL HAVING count(*) > 1",
 "Till payments: amounts positive, tender and status from the allowed lists": """
   SELECT * FROM till_payments WHERE amount_inr <= 0 OR tender NOT IN ('UPI', 'card', 'cash')
   OR till_status NOT IN ('approved', 'declined', 'failed', 'failed: no response')""",
 "Till payments: every bill ends with exactly one approved payment": """
   SELECT bill_id, sum(CASE WHEN till_status = 'approved' THEN 1 ELSE 0 END) AS approved
   FROM till_payments GROUP BY bill_id HAVING approved <> 1""",
 "Till payments: approved UPI payments carry an RRN; card and cash carry none": """
   SELECT * FROM till_payments WHERE (tender = 'UPI' AND till_status = 'approved' AND rrn IS NULL)
   OR (tender <> 'UPI' AND rrn IS NOT NULL)""",
 "Provider report: RRN unique, amounts positive, status from the allowed list": """
   SELECT rrn, count(*) FROM psp_upi GROUP BY rrn HAVING count(*) > 1
   UNION ALL SELECT rrn, 1 FROM psp_upi WHERE amount_inr <= 0 OR status NOT IN ('success', 'failed', 'returned')""",
 "Every UPI payment the till approved is a success in the provider's report, for the same amount": """
   SELECT t.* FROM till_payments t LEFT JOIN psp_upi p USING (rrn) WHERE t.tender = 'UPI' AND t.till_status = 'approved'
   AND (p.rrn IS NULL OR p.status <> 'success' OR p.amount_inr <> t.amount_inr)""",
 "Settlements: each day's credits and gross are the previous day's successes": """
   WITH s AS (SELECT CAST(status_ts AS DATE) + 1 AS settlement_date, count(*) AS credits, round(sum(amount_inr), 2) AS gross
              FROM psp_upi WHERE status = 'success' GROUP BY ALL)
   SELECT x.* FROM settlements x LEFT JOIN s ON s.settlement_date = CAST(x.settlement_date AS DATE)
   WHERE x.upi_credits <> coalesce(s.credits, 0) OR abs(x.gross_inr - coalesce(s.gross, 0)) > 0.01""",
 "Settlements: net is gross minus refunds and fees":
   "SELECT * FROM settlements WHERE abs(net_inr - (gross_inr - refunds_inr - mdr_inr)) > 0.01",
 "Refunds: each names a success in the provider's report, for the same amount": """
   SELECT r.* FROM refunds r LEFT JOIN psp_upi p USING (rrn)
   WHERE p.rrn IS NULL OR p.status <> 'success' OR p.amount_inr <> r.amount_inr""",
 "Complaints: each names a bill in the till's records":
   "SELECT * FROM complaints WHERE bill_id NOT IN (SELECT bill_id FROM till_payments)",
}
results = {name: len(q(sql)) for name, sql in TESTS.items()}
pd.Series(results, name="failing rows")
''')

md("""
## 2. The key that is not there

A UPI attempt the till gave up on, "failed: no response", never learned its RRN. So the obvious join cannot work:
""")

code('''
q("""SELECT count(*) AS timeouts, count(rrn) AS with_an_rrn FROM till_payments WHERE till_status = 'failed: no response'""")
''')

md("""
The provider's report still has a row for each of them. Match the timeouts to the provider rows no till payment claims,
by amount and a start within five seconds, one to one, nearest first. Then read the provider's final status.
""")

code('''
con.execute("""
CREATE OR REPLACE VIEW v_timeouts_matched AS
WITH orphans AS (SELECT * FROM psp_upi WHERE rrn NOT IN (SELECT rrn FROM till_payments WHERE rrn IS NOT NULL)),
pairs AS (
  SELECT t.bill_id, t.attempt, t.ts, t.amount_inr, o.rrn, o.status, o.status_ts,
         abs(epoch(o.initiated_ts) - epoch(t.ts)) AS gap_s,
         row_number() OVER (PARTITION BY t.bill_id, t.attempt ORDER BY abs(epoch(o.initiated_ts) - epoch(t.ts))) AS k,
         row_number() OVER (PARTITION BY o.rrn ORDER BY abs(epoch(o.initiated_ts) - epoch(t.ts))) AS j
  FROM till_payments t JOIN orphans o ON o.amount_inr = t.amount_inr AND abs(epoch(o.initiated_ts) - epoch(t.ts)) <= 5
  WHERE t.till_status = 'failed: no response')
SELECT bill_id, attempt, ts, amount_inr, rrn, status AS final_status, status_ts, gap_s,
       CASE WHEN status = 'success' THEN 'late credit' WHEN status = 'returned' THEN 'debited and returned'
            ELSE 'never debited' END AS outcome
FROM pairs WHERE k = 1 AND j = 1
""")
matched = q("SELECT * FROM v_timeouts_matched ORDER BY ts")
matched.outcome.value_counts()
''')

md("""
## 3. The extra charges

A late credit on a bill the customer then paid again is an extra charge. Nothing in the till's records says so.
""")

code('''
con.execute("""
CREATE OR REPLACE VIEW v_extra_charges AS
SELECT m.bill_id, m.rrn, m.amount_inr, m.ts AS debited_ts, m.status_ts AS credited_ts, a.tender AS paid_again_by
FROM v_timeouts_matched m JOIN till_payments a ON a.bill_id = m.bill_id AND a.till_status = 'approved'
WHERE m.outcome = 'late credit'
""")
extra = q("SELECT * FROM v_extra_charges ORDER BY debited_ts")
extra.agg(customers=("bill_id", "nunique"), extra_charges=("rrn", "count"), amount_inr=("amount_inr", "sum"))
''')

md("Score it against the answer key:")

code('''
truth = {c["rrn"] for c in KEY["charged_twice"]}
found = set(extra.rrn)
{"found": len(found), "right": len(found & truth), "false alarms": len(found - truth), "missed": len(truth - found)}
''')

md("""
## 4. How long it took, and what was never found

Measure from the extra debit, not from the complaint. A refund counts once it is done by the month-end review.
""")

code('''
waits = q(f"""
  SELECT e.rrn, e.bill_id, e.amount_inr, e.debited_ts, c.complaint_ts, r.completed_ts,
         (epoch(c.complaint_ts) - epoch(e.debited_ts)) / 86400 AS days_to_complaint,
         (epoch(r.completed_ts) - epoch(e.debited_ts)) / 86400 AS days_to_refund
  FROM v_extra_charges e LEFT JOIN complaints c USING (rrn)
  LEFT JOIN (SELECT * FROM refunds WHERE completed_ts <= TIMESTAMP '{AS_OF}') r USING (rrn)""")
{"median days to refund, from the debit": round(waits.days_to_refund.median(), 1),
 "not refunded at the review": int(waits.completed_ts.isna().sum()),
 "of which never complained": int((waits.completed_ts.isna() & waits.complaint_ts.isna()).sum())}
''')

md("""
## 5. The hour a monthly rate hides
""")

code('''
hours = q("""SELECT strftime(ts, '%Y-%m-%d %H:00') AS hour, count(*) AS upi_attempts,
                    sum(CASE WHEN till_status = 'failed: no response' THEN 1 ELSE 0 END) AS no_answer
             FROM till_payments WHERE tender = 'UPI' GROUP BY ALL""")
month = hours.no_answer.sum() / hours.upi_attempts.sum()
hours["share"] = hours.no_answer / hours.upi_attempts
bursts = hours[(hours.no_answer >= 3) & (hours.share > 10 * month)].sort_values("hour")
print(f"timeouts over June: {month:.2%}")
bursts
''')

md("""
## Exercises

1. Relax the matcher to 60 seconds. Which timeouts now match two provider rows, and why?
2. Find the customers who paid three times. What did the cashier do differently?
3. Put a ₹100-a-day compensation clock on every extra charge from the fifth day after the debit, as RBI does for failed
   payments to a merchant. What would June have cost?
4. Compute payment success for 18:20 to 19:50 on 20 June four ways: at the till, at the bank, bills paid, and customers
   charged once.

The answer key (`answer-key-payments.json`) scores each one.
""")

code('''
# The numbers the post quotes, in one place.
summary = {
    "generic_tests_passed": int(sum(v == 0 for v in results.values())),
    "timeouts": int(len(matched)), "outcomes": {k: int(v) for k, v in matched.outcome.value_counts().items()},
    "extra_charges": int(len(extra)), "customers": int(extra.bill_id.nunique()),
    "right": len(found & truth), "false": len(found - truth), "missed": len(truth - found),
    "refund_median_days_from_debit": round(float(waits.days_to_refund.median()), 1),
    "not_refunded": int(waits.completed_ts.isna().sum()),
    "bursts": list(bursts.hour.str.replace(" ", "T")),
}
print(json.dumps(summary))
''')


def build() -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                      "language_info": {"name": "python"}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, OUT)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(cells)} cells)")


def run_and_check() -> None:
    from nbconvert.preprocessors import ExecutePreprocessor

    nb = nbf.read(OUT, as_version=4)
    os.environ["STORE014_DATA"] = str(ROOT / "public" / "data" / "india-grocery") + "/"
    ExecutePreprocessor(timeout=300, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(OUT.parent)}})
    out = "".join(o.get("text", "") for o in nb.cells[-1].get("outputs", []))
    got = json.loads(out.strip().splitlines()[-1])
    ai = json.loads((ROOT / "src" / "data" / "payments-ai.json").read_text())
    m, f = ai["matcher"], ai["find"]
    want = {
        "generic_tests_passed": sum(t["pass"] for t in ai["tests"]["generic"]),
        "timeouts": m["matched"], "outcomes": m["outcomes"],
        "extra_charges": m["extra_charges"], "customers": m["customers"],
        "right": m["true_positives"], "false": m["false_positives"], "missed": m["missed"],
        "refund_median_days_from_debit": f["refund_median_days_from_debit"], "not_refunded": f["not_refunded"],
        "bursts": [b["hour"] for b in ai["hours"]["bursts"]],
    }
    bad = {k: (got.get(k), want[k]) for k in want if got.get(k) != want[k]}
    if bad:
        sys.exit(f"notebook disagrees with payments-ai.json: {bad}")
    nbf.write(nb, OUT)
    print("notebook ran and matches payments-ai.json:", got)


if __name__ == "__main__":
    build()
    if "--run" in sys.argv:
        run_and_check()
