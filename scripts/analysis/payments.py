"""What a data team can find in the payment records, scored against the answer key.

Reads the downloadable records in public/data/india-grocery and writes src/data/payments-ai.json,
which the payments post, its technical companion and the demo quote:

  1. the pipeline's data tests on the till's payments and the provider's reports, which pass, and
     five domain tests, which do not
  2. a matcher that joins each timed-out UPI attempt to the provider's final status by amount and
     time, and finds every extra charge, scored against the answer key
  3. payment success measured from the records, and how long each extra charge took to find
  4. a scripted assistant answering seven questions at the month-end review, with the schema only and
     with a domain layer

Everything is built from the records alone. The answer key (answer-key-payments.json) is read only
to score the results.

    python3 scripts/analysis/payments.py

Needs duckdb and pandas. The notebook notebooks/payments.ipynb walks through the same steps.
"""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public" / "data" / "india-grocery"
OUT = ROOT / "src" / "data" / "payments-ai.json"

AS_OF = "2026-06-29T09:00"  # the month-end review, with June's records
SLOW = ("2026-06-20T18:20", "2026-06-20T19:50")  # Saturday evening, when the acquirer's switch was slow
MATCH_SECONDS = 5  # a timed-out attempt and the provider's row for it start within five seconds
TAT_DAYS = 5  # RBI's turnaround for failed payments to a merchant: T+5
BURST = 10  # an hour whose timeout share is ten times the month's is a burst

TABLES = {
    "till_payments": ("pos-payments-june.csv", {"rrn": "VARCHAR", "note": "VARCHAR"}),
    "psp_upi": ("psp-upi-report-june.csv", {"rrn": "VARCHAR", "bill_ref": "VARCHAR"}),
    "settlements": ("upi-settlements-june.csv", {}),
    "refunds": ("upi-refunds-june.csv", {"rrn": "VARCHAR"}),
    "complaints": ("customer-complaints-june.csv", {"rrn": "VARCHAR"}),
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name, (file, types) in TABLES.items():
        opt = f", types={json.dumps(types).replace(chr(34), chr(39))}" if types else ""
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('{DATA / file}'{opt})")
    return con


def rows(con, sql: str) -> list[dict]:
    return json.loads(con.execute(sql).df().to_json(orient="records", date_format="iso"))


def days(a: str, b: str) -> float:
    return (datetime.fromisoformat(b[:19]) - datetime.fromisoformat(a[:19])).total_seconds() / 86400


def inr(v: float) -> str:
    return f"₹{v:,.2f}"


# ---------------------------------------------------------------- 1. data tests
GENERIC_TESTS = [
    ("Till payments: bill and attempt are unique",
     "SELECT bill_id, attempt, count(*) AS n FROM till_payments GROUP BY ALL HAVING count(*) > 1"),
    ("Till payments: amounts positive, tender and status from the allowed lists",
     ("SELECT * FROM till_payments WHERE amount_inr <= 0 OR tender NOT IN ('UPI', 'card', 'cash') "
      "OR till_status NOT IN ('approved', 'declined', 'failed', 'failed: no response')")),
    ("Till payments: every bill ends with exactly one approved payment",
     ("SELECT bill_id, sum(CASE WHEN till_status = 'approved' THEN 1 ELSE 0 END) AS approved FROM till_payments "
      "GROUP BY bill_id HAVING approved <> 1")),
    ("Till payments: approved UPI payments carry an RRN; card and cash carry none",
     ("SELECT * FROM till_payments WHERE (tender = 'UPI' AND till_status = 'approved' AND rrn IS NULL) "
      "OR (tender <> 'UPI' AND rrn IS NOT NULL)")),
    ("Provider report: RRN unique, amounts positive, status from the allowed list",
     ("SELECT rrn, count(*) AS n FROM psp_upi GROUP BY rrn HAVING count(*) > 1 "
      "UNION ALL SELECT rrn, 1 FROM psp_upi WHERE amount_inr <= 0 OR status NOT IN ('success', 'failed', 'returned')")),
    ("Every UPI payment the till approved is a success in the provider's report, for the same amount",
     ("SELECT t.* FROM till_payments t LEFT JOIN psp_upi p USING (rrn) WHERE t.tender = 'UPI' AND t.till_status = 'approved' "
      "AND (p.rrn IS NULL OR p.status <> 'success' OR p.amount_inr <> t.amount_inr)")),
    ("Settlements: each day's credits and gross are the previous day's successes",
     ("WITH s AS (SELECT CAST(status_ts AS DATE) + 1 AS settlement_date, count(*) AS credits, round(sum(amount_inr), 2) AS gross "
      "FROM psp_upi WHERE status = 'success' GROUP BY ALL) "
      "SELECT x.settlement_date, x.upi_credits, s.credits, x.gross_inr, s.gross FROM settlements x "
      "LEFT JOIN s USING (settlement_date) WHERE x.upi_credits <> coalesce(s.credits, 0) "
      "OR abs(x.gross_inr - coalesce(s.gross, 0)) > 0.01")),
    ("Settlements: net is gross minus refunds and fees",
     "SELECT * FROM settlements WHERE abs(net_inr - (gross_inr - refunds_inr - mdr_inr)) > 0.01"),
    ("Refunds: each names a success in the provider's report, for the same amount",
     ("SELECT r.* FROM refunds r LEFT JOIN psp_upi p USING (rrn) WHERE p.rrn IS NULL OR p.status <> 'success' "
      "OR p.amount_inr <> r.amount_inr")),
    ("Complaints: each names a bill in the till's records",
     "SELECT c.* FROM complaints c WHERE c.bill_id NOT IN (SELECT bill_id FROM till_payments)"),
]


def run_generic_tests(con) -> list[dict]:
    out = []
    for name, sql in GENERIC_TESTS:
        bad = rows(con, sql)
        out.append({"name": name, "sql": " ".join(sql.split()), "failing_rows": len(bad), "pass": not bad,
                    "examples": bad[:3]})
    return out


# ---------------------------------------------------------------- 2. the matcher
# A UPI attempt the till gave up on never learned its RRN, so it cannot be joined to the provider's
# report by key. The provider's report has a row for it all the same: same amount, started in the
# same second. Match the till's timeouts to the provider rows no till payment claims, one to one,
# nearest in time first.
MATCH = f"""
CREATE OR REPLACE VIEW v_timeouts_matched AS
WITH orphans AS (
  SELECT p.* FROM psp_upi p WHERE p.rrn NOT IN (SELECT rrn FROM till_payments WHERE rrn IS NOT NULL)),
pairs AS (
  SELECT t.bill_id, t.attempt, t.ts, t.amount_inr, o.rrn, o.status, o.status_ts,
         abs(epoch(o.initiated_ts) - epoch(t.ts)) AS gap_s,
         row_number() OVER (PARTITION BY t.bill_id, t.attempt ORDER BY abs(epoch(o.initiated_ts) - epoch(t.ts))) AS k,
         row_number() OVER (PARTITION BY o.rrn ORDER BY abs(epoch(o.initiated_ts) - epoch(t.ts))) AS j
  FROM till_payments t JOIN orphans o ON o.amount_inr = t.amount_inr
   AND abs(epoch(o.initiated_ts) - epoch(t.ts)) <= {MATCH_SECONDS}
  WHERE t.till_status = 'failed: no response')
SELECT bill_id, attempt, ts, amount_inr, rrn, status AS final_status, status_ts, gap_s,
       CASE WHEN status = 'success' THEN 'late credit' WHEN status = 'returned' THEN 'debited and returned'
            ELSE 'never debited' END AS outcome
FROM pairs WHERE k = 1 AND j = 1
"""

EXTRA = """
CREATE OR REPLACE VIEW v_extra_charges AS
SELECT m.bill_id, m.rrn, m.amount_inr, m.ts AS debited_ts, m.status_ts AS credited_ts,
       a.tender AS paid_again_by, a.ts AS paid_again_ts
FROM v_timeouts_matched m
JOIN till_payments a ON a.bill_id = m.bill_id AND a.till_status = 'approved'
WHERE m.outcome = 'late credit'
"""


# ---------------------------------------------------------------- 3. the assistant
def assistant(con, matched, extra, key, refunds_view) -> dict:
    s0, s1 = SLOW
    ct = key["charged_twice"]
    gold_customers = len({c["bill_id"] for c in ct})
    gold_extra = len(ct)
    gold_inr = round(sum(c["amount_inr"] for c in ct), 2)

    def q(sql):
        return rows(con, sql)

    qa = []

    # Q1: a question about the records.
    s_att = "SELECT count(*) AS upi_attempts FROM till_payments WHERE tender = 'UPI'"
    r1 = q(s_att)
    gold_att = key["story"]["june"]["upi_attempts"]
    qa.append({"id": "attempts", "question": "How many UPI payments did the tills attempt in June?", "kind": "records",
               "naive": {"plan": [{"sql": s_att, "result": r1}], "answer": f"{r1[0]['upi_attempts']:,}.", "value": r1[0]["upi_attempts"]},
               "domain": {"plan": [{"sql": s_att, "result": r1}], "answer": f"{r1[0]['upi_attempts']:,}.", "value": r1[0]["upi_attempts"]},
               "gold": {"value": gold_att, "why": "Attempts are facts the till records."},
               "check": "the number of attempts"})

    # Q2: did anyone pay twice?
    s_twice = ("SELECT count(*) AS bills, sum(CASE WHEN approved > 1 THEN 1 ELSE 0 END) AS paid_twice FROM "
               "(SELECT bill_id, sum(CASE WHEN till_status = 'approved' THEN 1 ELSE 0 END) AS approved FROM till_payments GROUP BY bill_id)")
    r2 = q(s_twice)
    s_extra = ("SELECT count(DISTINCT bill_id) AS customers, count(*) AS extra_charges, round(sum(amount_inr), 2) AS amount_inr "
               "FROM v_extra_charges")
    r2d = q(s_extra)
    qa.append({"id": "twice", "question": "Did any customer pay twice in June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_twice, "result": r2}],
                         "answer": f"No. All {r2[0]['bills']:,} bills have exactly one approved payment.", "value": 0},
               "domain": {"plan": [{"sql": "SELECT outcome, count(*) AS attempts FROM v_timeouts_matched GROUP BY outcome",
                                    "result": q("SELECT outcome, count(*) AS attempts FROM v_timeouts_matched GROUP BY outcome ORDER BY attempts DESC")},
                                   {"sql": s_extra, "result": r2d}],
                          "answer": (f"Yes: {r2d[0]['customers']} customers, {r2d[0]['extra_charges']} extra charges, "
                                     f"{inr(r2d[0]['amount_inr'])}. Each is a UPI payment the till gave up on and the store's bank "
                                     f"credited later, on a bill the customer then paid again."),
                          "value": r2d[0]["customers"]},
               "gold": {"value": gold_customers, "why": f"{gold_customers} customers, {gold_extra} extra charges, {inr(gold_inr)}, from the answer key."},
               "check": "the number of customers charged twice"})

    # Q3: the 28 timeouts on Saturday evening.
    s_slow_naive = (f"SELECT till_status, count(*) AS attempts FROM till_payments WHERE tender = 'UPI' "
                    f"AND ts BETWEEN TIMESTAMP '{s0}' AND TIMESTAMP '{s1}' GROUP BY till_status ORDER BY attempts DESC")
    r3 = q(s_slow_naive)
    timeouts = next(x["attempts"] for x in r3 if x["till_status"] == "failed: no response")
    s_slow = (f"SELECT outcome, count(*) AS attempts FROM v_timeouts_matched WHERE ts BETWEEN TIMESTAMP '{s0}' "
              f"AND TIMESTAMP '{s1}' GROUP BY outcome ORDER BY attempts DESC")
    r3d = q(s_slow)
    out3 = {x["outcome"]: x["attempts"] for x in r3d}
    gold3 = {}
    for a in key["upi_attempts_not_simply_approved"]:
        if a["till_status"] == "failed: no response" and s0 <= a["ts"][:16] <= s1:
            o = {"late credit": "late credit", "returned": "debited and returned", "failed": "never debited"}[a["final"]]
            gold3[o] = gold3.get(o, 0) + 1
    qa.append({"id": "timeouts", "question": "What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June?",
               "kind": "reality",
               "naive": {"plan": [{"sql": s_slow_naive, "result": r3}],
                         "answer": f"They failed: the tills got no response on {timeouts} payments, and the customers paid another way.",
                         "value": {"never debited": timeouts}},
               "domain": {"plan": [{"sql": s_slow, "result": r3d}],
                          "answer": (f"Of the {timeouts}, {out3.get('late credit', 0)} were credited to the store late, so those "
                                     f"customers paid twice; {out3.get('debited and returned', 0)} was debited and returned by the "
                                     f"customer's bank; {out3.get('never debited', 0)} never left the customer's account."),
                          "value": out3},
               "gold": {"value": gold3, "why": "What became of each payment, from the answer key."},
               "check": "the outcome of every timed-out payment"})

    # Q4: the suspense items.
    s_susp = ("SELECT count(*) AS credits_without_an_approved_payment, round(sum(amount_inr), 2) AS amount_inr FROM psp_upi p "
              "WHERE status = 'success' AND CAST(status_ts AS DATE) BETWEEN '2026-06-20' AND '2026-06-21' "
              "AND rrn NOT IN (SELECT rrn FROM till_payments WHERE till_status = 'approved' AND rrn IS NOT NULL)")
    r4 = q(s_susp)
    s_susp_dom = ("SELECT count(*) AS extra_charges, count(DISTINCT bill_id) AS customers, round(sum(amount_inr), 2) AS amount_inr "
                  "FROM v_extra_charges WHERE CAST(credited_ts AS DATE) BETWEEN '2026-06-20' AND '2026-06-21'")
    r4d = q(s_susp_dom)
    n_susp = r4[0]["credits_without_an_approved_payment"]
    qa.append({"id": "suspense", "question": f"Why are {n_susp} UPI credits from 20 and 21 June sitting in suspense?", "kind": "reality",
               "naive": {"plan": [{"sql": s_susp, "result": r4}],
                         "answer": (f"No approved payment at the tills matches them, so they wait in suspense until someone "
                                    f"claims them: {inr(r4[0]['amount_inr'])}."),
                         "names_customers": False},
               "domain": {"plan": [{"sql": s_susp, "result": r4}, {"sql": s_susp_dom, "result": r4d}],
                          "answer": (f"They are extra charges. Each matches, by amount and time, a UPI payment the till gave up on, "
                                     f"on a bill that was paid again: {r4d[0]['customers']} customers are owed "
                                     f"{inr(r4d[0]['amount_inr'])}."),
                          "names_customers": True},
               "gold": {"value": "Extra charges on customers who paid again", "names_customers": True,
                        "why": "Every one is a customer's money, from the answer key."},
               "check": "says whose money it is"})

    # Q5: how long did they wait?
    s_wait = ("SELECT round(median(epoch(r.completed_ts) - epoch(c.complaint_ts)) / 86400, 1) AS median_days, "
              "round(max(epoch(r.completed_ts) - epoch(c.complaint_ts)) / 86400, 1) AS longest_days "
              f"FROM refunds r JOIN complaints c USING (rrn) WHERE r.completed_ts <= TIMESTAMP '{AS_OF}'")
    r5 = q(s_wait)
    s_wait_dom = ("SELECT count(*) AS extra_charges, count(r.rrn) AS refunded, "
                  "round(median(epoch(r.completed_ts) - epoch(e.debited_ts)) / 86400, 1) AS median_days_from_debit, "
                  "CAST(sum(CASE WHEN r.rrn IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS not_refunded, "
                  "round(sum(CASE WHEN r.rrn IS NULL THEN e.amount_inr ELSE 0 END), 2) AS not_refunded_inr, "
                  "CAST(sum(CASE WHEN r.rrn IS NULL AND c.rrn IS NULL THEN 1 ELSE 0 END) AS INTEGER) AS never_complained "
                  f"FROM v_extra_charges e LEFT JOIN (SELECT * FROM refunds WHERE completed_ts <= TIMESTAMP '{AS_OF}') r USING (rrn) "
                  "LEFT JOIN complaints c USING (rrn)")
    r5d = q(s_wait_dom)
    gold_wait = round(statistics.median([days(c["paid_ts"], c["refunded_ts"]) for c in ct if c["refunded_by_month_end"]]), 1)
    gold_unref = sum(1 for c in ct if not c["refunded_by_month_end"])
    qa.append({"id": "wait", "question": "How long did customers who paid twice wait for their money?", "kind": "reality",
               "naive": {"plan": [{"sql": s_wait, "result": r5}],
                         "answer": f"A median {r5[0]['median_days']} days from complaint to refund; the longest {r5[0]['longest_days']}.",
                         "value": r5[0]["median_days"], "unrefunded": None},
               "domain": {"plan": [{"sql": s_wait_dom, "result": r5d}],
                          "answer": (f"A median {r5d[0]['median_days_from_debit']} days from the extra debit to the refund. And "
                                     f"{r5d[0]['not_refunded']} extra charges, {inr(r5d[0]['not_refunded_inr'])}, had not been "
                                     f"refunded when June closed; {r5d[0]['never_complained']} of those customers never complained."),
                          "value": r5d[0]["median_days_from_debit"], "unrefunded": r5d[0]["not_refunded"]},
               "gold": {"value": gold_wait, "unrefunded": gold_unref,
                        "why": f"A median {gold_wait} days from the debit, and {gold_unref} never refunded in June, from the answer key."},
               "check": "within half a day of the median from the debit, and counts the unrefunded"})

    # Q6: technical declines.
    s_tech = ("SELECT count(*) AS upi_attempts, sum(CASE WHEN till_status = 'failed' THEN 1 ELSE 0 END) AS technical_failures, "
              "round(100.0 * sum(CASE WHEN till_status = 'failed' THEN 1 ELSE 0 END) / count(*), 2) AS pct "
              "FROM till_payments WHERE tender = 'UPI'")
    r6 = q(s_tech)
    s_hours = ("SELECT strftime(ts, '%Y-%m-%d %H:00') AS hour, count(*) AS upi_attempts, "
               "sum(CASE WHEN till_status = 'failed: no response' THEN 1 ELSE 0 END) AS no_answer, "
               "round(100.0 * sum(CASE WHEN till_status = 'failed: no response' THEN 1 ELSE 0 END) / count(*), 1) AS pct "
               "FROM till_payments WHERE tender = 'UPI' GROUP BY ALL ORDER BY pct DESC LIMIT 3")
    r6d = q(s_hours)
    top2 = sorted(r6d[:2], key=lambda x: x["hour"])
    sl = key["story"]["slowdown"]
    qa.append({"id": "declines", "question": "Was the store's UPI technical decline rate acceptable in June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_tech, "result": r6}],
                         "answer": (f"Yes: {r6[0]['pct']}% of UPI attempts failed for technical reasons, in line with the "
                                    f"0.7–0.8% NPCI reports for UPI as a whole."),
                         "says_burst": False},
               "domain": {"plan": [{"sql": s_tech, "result": r6}, {"sql": s_hours, "result": r6d}],
                          "answer": (f"Over the month, yes: {r6[0]['pct']}%. But timeouts are not counted as technical declines, "
                                     f"and in the {top2[0]['hour'][11:16]} and {top2[1]['hour'][11:16]} hours on 20 June the tills got "
                                     f"no answer on {top2[0]['pct']:g}% and {top2[1]['pct']:g}% of attempts. A monthly rate hides the "
                                     f"hours that charged customers twice."),
                          "says_burst": True},
               "gold": {"value": f"No answer on {sl['upi_timeouts']} of {sl['upi_attempts']} attempts, 18:20–19:50 on 20 June",
                        "says_burst": True, "why": "The slowdown, from the answer key."},
               "check": "finds the hour the monthly rate hides"})

    # Q7: who to refund now.
    s_open = "SELECT count(*) AS open_complaints FROM complaints WHERE resolved_ts IS NULL OR resolved_ts > TIMESTAMP '2026-06-29 09:00'"
    r7 = q(s_open)
    s_refund = ("SELECT e.bill_id, e.rrn, e.amount_inr, e.credited_ts FROM v_extra_charges e LEFT JOIN refunds r USING (rrn) "
                "WHERE r.rrn IS NULL ORDER BY e.credited_ts")  # no refund done or under way
    r7d = q(s_refund)
    gold7 = sorted(c["rrn"] for c in ct if c["refunded_ts"] is None)
    qa.append({"id": "refund_now", "question": "Which customers should the store refund now, without waiting for a complaint?",
               "kind": "reality",
               "naive": {"plan": [{"sql": s_open, "result": r7}],
                         "answer": "None: no complaint is open.", "value": []},
               "domain": {"plan": [{"sql": s_refund, "result": r7d}],
                          "answer": (f"{len(r7d)}: bills " + ", ".join(x["bill_id"] for x in r7d)
                                     + f", {inr(sum(x['amount_inr'] for x in r7d))} in all. Their extra charges are in the "
                                       f"provider's report and nobody has claimed them."),
                          "value": sorted(x["rrn"] for x in r7d)},
               "gold": {"value": gold7, "why": "The extra charges nobody ever refunded, from the answer key."},
               "check": "names every unrefunded extra charge"})

    def right(item, side) -> bool:
        a, g = item[side], item["gold"]
        i = item["id"]
        if i in ("attempts", "twice"):
            return a["value"] == g["value"]
        if i == "timeouts":
            return a["value"] == g["value"]
        if i == "suspense":
            return a["names_customers"] == g["names_customers"]
        if i == "wait":
            return a["unrefunded"] == g["unrefunded"] and abs(a["value"] - g["value"]) <= 0.5
        if i == "declines":
            return a["says_burst"] == g["says_burst"]
        if i == "refund_now":
            return a["value"] == g["value"]
        raise KeyError(i)

    for item in qa:
        item["naive"]["right"] = right(item, "naive")
        item["domain"]["right"] = right(item, "domain")
    gl3 = gold3
    short = {
        "attempts": (f"{r1[0]['upi_attempts']:,}",) * 3,
        "twice": ("No", f"{r2d[0]['customers']} customers", f"{gold_customers} customers"),
        "timeouts": (f"All {timeouts} failed", f"{out3.get('late credit', 0)} credited late",
                     f"{gl3.get('late credit', 0)} credited late, {gl3.get('debited and returned', 0)} returned, {gl3.get('never debited', 0)} never debited"),
        "suspense": ("Unclaimed credits", "Extra charges on customers", "Extra charges on customers"),
        "wait": (f"{r5[0]['median_days']} days, from complaint", f"{r5d[0]['median_days_from_debit']} days from the debit; {r5d[0]['not_refunded']} never",
                 f"{gold_wait} days; {gold_unref} never"),
        "declines": (f"Yes, {r6[0]['pct']}%", "Not in the hour that mattered", "No answer on a third, one evening"),
        "refund_now": ("None", f"{len(r7d)} bills", f"{len(gold7)} bills"),
    }
    for item in qa:
        n, d, gl = short[item["id"]]
        item["naive"]["short"], item["domain"]["short"], item["gold"]["short"] = n, d, gl
    del refunds_view, matched, extra
    return {
        "as_of": AS_OF,
        "questions": qa,
        "score": {"naive": sum(i["naive"]["right"] for i in qa), "domain": sum(i["domain"]["right"] for i in qa),
                  "of": len(qa)},
        "schema_only_tables": ["till_payments", "settlements", "refunds", "complaints"],
        "domain_layer": {
            "tables_added": ["psp_upi"],
            "views": {
                "v_timeouts_matched": (f"each UPI attempt the till gave up on, matched to the provider's row for it by amount and "
                                       f"a start within {MATCH_SECONDS} seconds, one to one, with its final status"),
                "v_extra_charges": "late credits on bills the customer then paid again",
            },
            "definitions": {
                "failed: no response": "The till stopped waiting. A question, not an answer: the money may already have moved.",
                "RRN": "The payment's reference number. A till that hears nothing back never learns it.",
                "late credit": "A success in the provider's report after the till gave up. If the bill was paid again, an extra charge.",
                "refund wait": "Measured from the extra debit, not from the complaint.",
                "technical decline rate": "Counts failures the switch reported. Timeouts are not in it; read it by the hour.",
            },
            "rules": [
                "Match every timed-out UPI attempt to the provider's final status by amount and time before calling it failed.",
                "A provider success with no approved till payment is a customer's money until proven otherwise.",
                "Read payment rates by the hour, with timeouts counted, before trusting a monthly rate.",
            ],
        },
    }


# ---------------------------------------------------------------- main
def main() -> None:
    con = connect()
    key = json.loads((DATA / "answer-key-payments.json").read_text())

    generic = run_generic_tests(con)
    con.execute(MATCH)
    con.execute(EXTRA)
    matched = rows(con, "SELECT * FROM v_timeouts_matched ORDER BY ts")
    extra = rows(con, "SELECT * FROM v_extra_charges ORDER BY debited_ts")
    timeouts = rows(con, "SELECT bill_id, attempt, ts, amount_inr FROM till_payments WHERE till_status = 'failed: no response'")
    orphans = rows(con, ("SELECT rrn, initiated_ts, amount_inr, status_ts FROM psp_upi WHERE status = 'success' AND rrn NOT IN "
                         "(SELECT rrn FROM till_payments WHERE till_status = 'approved' AND rrn IS NOT NULL)"))
    refunds = {r["rrn"]: r for r in rows(con, f"SELECT * FROM refunds WHERE completed_ts <= TIMESTAMP '{AS_OF}'")}
    complaints = {r["rrn"]: r for r in rows(con, "SELECT * FROM complaints")}

    # Score the matcher against the answer key.
    ct = {c["rrn"]: c for c in key["charged_twice"]}
    found = {e["rrn"] for e in extra}
    true_pos = found & set(ct)
    outcomes = {(a["bill_id"], a["attempt"]): a["final"] for a in key["upi_attempts_not_simply_approved"]
                if a["till_status"] == "failed: no response"}
    name = {"success": "late credit", "returned": "returned", "failed": "failed"}
    outcome_right = sum(outcomes.get((m["bill_id"], m["attempt"])) == name[m["final_status"]] for m in matched)

    # How long each extra charge took to find: the matcher runs after the next morning's settlement file
    # (09:00 the day after the credit); a complaint finds it when the customer calls.
    finds = []
    for e in extra:
        settled = (datetime.fromisoformat(e["credited_ts"][:10] + "T09:00") + timedelta(days=1)).isoformat()
        c = complaints.get(e["rrn"])
        r = refunds.get(e["rrn"])
        finds.append({"rrn": e["rrn"], "bill_id": e["bill_id"], "amount_inr": e["amount_inr"], "debited_ts": e["debited_ts"],
                      "matcher_days": round(days(e["debited_ts"], settled), 2),
                      "complaint_days": round(days(e["debited_ts"], c["complaint_ts"]), 2) if c else None,
                      "refund_days": round(days(e["debited_ts"], r["completed_ts"]), 2) if r else None})

    def med(xs: list[float]) -> float | None:
        return round(statistics.median(xs), 1) if xs else None

    # Hourly timeout shares, and the bursts the monthly rate hides.
    hours = rows(con, ("SELECT strftime(ts, '%Y-%m-%dT%H:00') AS hour, count(*) AS upi_attempts, "
                       "sum(CASE WHEN till_status = 'failed: no response' THEN 1 ELSE 0 END) AS no_answer "
                       "FROM till_payments WHERE tender = 'UPI' GROUP BY ALL ORDER BY hour"))
    month = sum(h["no_answer"] for h in hours) / sum(h["upi_attempts"] for h in hours)
    bursts = [h | {"share": round(h["no_answer"] / h["upi_attempts"], 3)} for h in hours
              if h["no_answer"] >= 3 and h["no_answer"] / h["upi_attempts"] > BURST * month]

    # Success in the slowdown, from the records once the timeouts are matched.
    s0, s1 = SLOW
    slow = rows(con, (f"SELECT count(*) AS upi_attempts, sum(CASE WHEN till_status = 'approved' THEN 1 ELSE 0 END) AS approved_at_till "
                      f"FROM till_payments WHERE tender = 'UPI' AND ts BETWEEN TIMESTAMP '{s0}' AND TIMESTAMP '{s1}'"))[0]
    slow_late = rows(con, (f"SELECT count(*) AS n FROM v_timeouts_matched WHERE outcome = 'late credit' "
                           f"AND ts BETWEEN TIMESTAMP '{s0}' AND TIMESTAMP '{s1}'"))[0]["n"]
    success = {"till": round(slow["approved_at_till"] / slow["upi_attempts"], 4),
               "bank": round((slow["approved_at_till"] + slow_late) / slow["upi_attempts"], 4),
               "answer_key": key["story"]["slowdown"]["four_ways"]}

    late_unmatched = [e for e in rows(con, "SELECT * FROM v_timeouts_matched") if e["outcome"] == "late credit"]
    domain = [
        {"name": "Every success in the provider's report has an approved till payment with its RRN", "failing": orphans},
        {"name": "Every UPI attempt at the till joins the provider's final status by RRN",
         "failing": timeouts},
        {"name": "No bill is paid twice, once timed-out attempts are matched to the provider's report", "failing": extra},
        {"name": f"Every extra charge comes back within {TAT_DAYS} days of the debit",
         "failing": [f for f in finds if f["refund_days"] is None or f["refund_days"] > TAT_DAYS]},
        {"name": f"No hour has three or more timeouts and a timeout share over {BURST} times the month's", "failing": bursts},
    ]
    for t in domain:
        t["pass"] = not t["failing"]

    out = {
        "about": ("What a data team can find in the payment records, scored against the answer key. "
                  "Generated by scripts/analysis/payments.py from public/data/india-grocery."),
        "tests": {"generic": generic, "domain": domain},
        "matcher": {
            "timeouts": len(timeouts), "matched": len(matched),
            "outcomes": {o: sum(1 for m in matched if m["outcome"] == o) for o in ("late credit", "debited and returned", "never debited")},
            "outcomes_right": outcome_right,
            "extra_charges": len(extra), "customers": len({e["bill_id"] for e in extra}),
            "extra_inr": round(sum(e["amount_inr"] for e in extra), 2),
            "true_positives": len(true_pos), "false_positives": len(found - set(ct)), "missed": len(set(ct) - found),
            "answer_key": {"extra_charges": len(ct), "customers": len({c["bill_id"] for c in ct.values()})},
            "late_credits": len(late_unmatched),
            "max_gap_s": max(m["gap_s"] for m in matched),
        },
        "find": {
            "per_charge": finds,
            "matcher_median_days": med([f["matcher_days"] for f in finds]),
            "complaint_median_days": med([f["complaint_days"] for f in finds if f["complaint_days"] is not None]),
            "never_complained": sum(1 for f in finds if f["complaint_days"] is None),
            "refund_median_days_from_debit": med([f["refund_days"] for f in finds if f["refund_days"] is not None]),
            "not_refunded": sum(1 for f in finds if f["refund_days"] is None),
            "not_refunded_inr": round(sum(f["amount_inr"] for f in finds if f["refund_days"] is None), 2),
            "over_tat": sum(1 for f in finds if f["refund_days"] is not None and f["refund_days"] > TAT_DAYS),
        },
        "hours": {"month_share": round(month, 5), "bursts": bursts},
        "success": success,
        "assistant": assistant(con, matched, extra, key, refunds),
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    m = out["matcher"]
    print(f"generic tests passing: {sum(t['pass'] for t in generic)} of {len(generic)}; domain tests failing: "
          f"{sum(not t['pass'] for t in domain)} of {len(domain)}")
    print(f"matcher: {m['matched']} of {m['timeouts']} timeouts matched ({m['outcomes']}), {m['outcomes_right']} outcomes right; "
          f"extra charges {m['extra_charges']} ({m['true_positives']} true, {m['false_positives']} false, {m['missed']} missed)")
    print(f"find: {out['find']}".replace(str(out['find']['per_charge']), '...'))
    print(f"success {success}; bursts {[b['hour'] for b in bursts]}; assistant {out['assistant']['score']}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
