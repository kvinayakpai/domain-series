"""What a data team can find in Store 014's records, scored against the answer key.

Reads the downloadable records in public/data/india-grocery and writes src/data/retail-ai.json,
which the retail post, its technical companion and the demo quote:

  1. the pipeline's data tests, which pass, and four domain tests, which do not
  2. an hourly gap detector on the till lines, scored against the true empty-shelf episodes
  3. the store's forecast against one trained on unconstrained demand, scored against true demand
  4. on-shelf availability under four definitions
  5. a scripted assistant answering seven questions with the schema only, then with a domain layer

Everything is built from the records alone. The answer key (answer-key-retail.json) is read only
to score the results, the way a held-out label set would be.

    python3 scripts/analysis/retail.py

Needs duckdb, numpy and pandas. The notebook notebooks/retail.ipynb walks through the same steps.
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public" / "data" / "india-grocery"
OUT = ROOT / "src" / "data" / "retail-ai.json"

HERO = "ATTA-WW-5KG"
OPEN_HOURS = list(range(7, 22))  # the store is open 07:00-22:00; hour h covers h:00 to h+1:00
H = len(OPEN_HOURS)
MAY = [date(2026, 5, 4) + timedelta(days=i) for i in range(28)]
JUNE = [date(2026, 6, 1) + timedelta(days=i) for i in range(28)]
DAYS = MAY + JUNE
ALPHA = 0.001  # the gap detector flags a run of no sales less likely than 1 in 1,000
ALPHAS = [0.01, 0.001, 0.0001]
ALERT_SHARE = 0.25  # the nightly low-sales rule: sales under a quarter of the forecast
AS_OF = date(2026, 6, 14)  # the assistant answers at the Monday review, with data to Sunday 14 June
WEEK1 = (date(2026, 6, 1), date(2026, 6, 7))
WEEK2 = (date(2026, 6, 8), date(2026, 6, 14))

TABLES = {
    "products": "products.csv",
    "pos_lines": "pos-lines-may-june.csv",
    "daily_sales": "daily-sales-june.csv",
    "inventory_book": "inventory-book-june.csv",
    "forecasts": "forecasts-june.csv",
    "store_orders": "store-orders-june.csv",
    "goods_receipts": "goods-receipts-june.csv",
    "stock_counts": "stock-counts-june.csv",
    "shelf_audits": "shelf-audits-june.csv",
    "write_offs": "write-offs-june.csv",
    "fresh_deliveries": "fresh-deliveries-june.csv",
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name, file in TABLES.items():
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('{DATA / file}')")
    return con


def rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict]:
    df = con.execute(sql).df()
    return json.loads(df.to_json(orient="records", date_format="iso"))


# ---------------------------------------------------------------- 1. data tests
GENERIC_TESTS = [
    ("Till lines: bill and line number are unique",
     "SELECT bill_id, line, count(*) AS n FROM pos_lines GROUP BY ALL HAVING count(*) > 1"),
    ("Till lines: keys present, quantities and prices positive",
     ("SELECT * FROM pos_lines WHERE bill_id IS NULL OR bill_ts IS NULL OR sku_scanned IS NULL "
      "OR qty <= 0 OR unit_price <= 0")),
    ("Till lines: every item and barcode is in the product master",
     ("SELECT l.* FROM pos_lines l LEFT JOIN products p ON l.sku_scanned = p.sku AND l.gtin_scanned = p.gtin "
      "WHERE p.sku IS NULL")),
    ("Till lines: line amount is quantity times price",
     "SELECT * FROM pos_lines WHERE abs(line_amount - qty * unit_price) > 0.005"),
    ("Daily sales reconcile with the till lines",
     ("WITH t AS (SELECT CAST(bill_ts AS DATE) AS date, sku_scanned AS sku, sum(qty) AS units FROM pos_lines "
      "GROUP BY ALL) SELECT d.date, d.sku, d.units_sold, t.units FROM daily_sales d "
      "LEFT JOIN t ON t.date = d.date AND t.sku = d.sku WHERE d.units_sold <> coalesce(t.units, 0)")),
    ("Book stock: one row per item per day, never negative",
     ("SELECT date, sku, book_on_hand_close FROM inventory_book WHERE book_on_hand_close < 0 "
      "UNION ALL SELECT date, NULL, count(*) FROM inventory_book GROUP BY date "
      "HAVING count(*) <> (SELECT count(*) FROM products)")),
    ("Book stock: each close is the last close plus receipts, minus sales and write-offs, plus count adjustments",
     """WITH days AS (SELECT DISTINCT date FROM inventory_book),
        rcv AS (SELECT date, sku, sum(u) AS u FROM (
                  SELECT CAST(received_ts AS DATE) AS date, sku_booked AS sku, units_booked AS u FROM goods_receipts
                  UNION ALL SELECT CAST(delivery_ts AS DATE), sku, units FROM fresh_deliveries) GROUP BY ALL),
        sold AS (SELECT CAST(bill_ts AS DATE) AS date, sku_scanned AS sku, sum(qty) AS u FROM pos_lines GROUP BY ALL),
        wo AS (SELECT date, sku, sum(units) AS u FROM write_offs GROUP BY ALL),
        adj AS (SELECT CAST(count_ts AS DATE) AS date, sku, sum(adjustment) AS u FROM stock_counts
                WHERE hour(count_ts) < 22 GROUP BY ALL)
     SELECT b.date, b.sku, b.book_on_hand_close AS book, prev.book_on_hand_close + coalesce(rcv.u, 0)
            - coalesce(sold.u, 0) - coalesce(wo.u, 0) + coalesce(adj.u, 0) AS rebuilt
     FROM inventory_book b
     JOIN inventory_book prev ON prev.sku = b.sku AND prev.date = b.date - 1
     LEFT JOIN rcv ON rcv.date = b.date AND rcv.sku = b.sku LEFT JOIN sold ON sold.date = b.date AND sold.sku = b.sku
     LEFT JOIN wo ON wo.date = b.date AND wo.sku = b.sku LEFT JOIN adj ON adj.date = b.date AND adj.sku = b.sku
     WHERE book <> rebuilt"""),
    ("Forecasts: one row per warehouse item per night, reorder point below order-up-to",
     ("SELECT date, count(*) AS items, max(CASE WHEN reorder_point > order_up_to THEN 1 ELSE 0 END) AS bad "
      "FROM forecasts GROUP BY date HAVING count(*) <> (SELECT count(*) FROM products WHERE flow = 'DC') OR bad = 1")),
    ("Forecasts: an order goes out only when book plus on-order is at or below the reorder point",
     "SELECT * FROM forecasts WHERE ordered_units > 0 AND book_on_hand + on_order > reorder_point"),
    ("Store orders: every automatic order matches that night's forecast row",
     ("SELECT o.* FROM store_orders o LEFT JOIN forecasts f ON f.sku = o.sku AND f.date = CAST(o.created_ts AS DATE) "
      "AND f.ordered_units = o.units WHERE o.reason = 'auto' AND f.sku IS NULL")),
    ("Goods receipts: every pallet line booked as its shipping notice says",
     "SELECT * FROM goods_receipts WHERE sku_booked <> asn_sku OR units_booked <> asn_units"),
    ("Shelf audits: one status per item per audit, on shelf or empty",
     ("SELECT audit_ts, sku, count(*) AS n FROM shelf_audits GROUP BY ALL HAVING count(*) > 1 "
      "UNION ALL SELECT audit_ts, sku, 1 FROM shelf_audits WHERE status NOT IN ('on shelf', 'empty')")),
]


def run_generic_tests(con) -> list[dict]:
    out = []
    for name, sql in GENERIC_TESTS:
        bad = rows(con, sql)
        out.append({"name": name, "sql": " ".join(sql.split()), "failing_rows": len(bad), "pass": not bad,
                    "examples": bad[:3]})
    return out


# ---------------------------------------------------------------- hourly records
def hourly_sales(con) -> dict[str, np.ndarray]:
    """Units the tills recorded per item, per day (4 May to 28 June) and open hour."""
    df = con.execute("SELECT CAST(bill_ts AS DATE) AS d, hour(bill_ts) AS h, sku_scanned AS sku, sum(qty) AS u "
                     "FROM pos_lines GROUP BY ALL").df()
    out = {s: np.zeros((len(DAYS), H)) for s in sorted(df.sku.unique())}
    index = {d: i for i, d in enumerate(DAYS)}
    for r in df.itertuples():
        out[r.sku][index[r.d.date() if hasattr(r.d, "date") else r.d], OPEN_HOURS.index(int(r.h))] += r.u
    return out


def hourly_book(con, sales: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], bool]:
    """The book as the system holds it at the end of each June open hour, rebuilt from the records.

    Starts from the 1 June count, then applies receipts, sales and count adjustments as they happen
    and write-offs at close. Returns the hours and whether every rebuilt close matches the book.
    """
    counts = con.execute("SELECT * FROM stock_counts ORDER BY count_ts").df()
    rcv = con.execute("SELECT received_ts, sku_booked AS sku, units_booked AS u FROM goods_receipts").df()
    wo = con.execute("SELECT date, sku, sum(units) AS u FROM write_offs GROUP BY ALL").df()
    wo["date"] = pd.to_datetime(wo.date).dt.date
    book_csv = con.execute("SELECT * FROM inventory_book").df()
    book_csv["date"] = pd.to_datetime(book_csv.date).dt.date
    first = JUNE[0]
    out, ok = {}, True
    for s in sales:
        start = counts[(counts.sku == s) & (counts.count_ts.dt.date == first)]
        level = float(start.counted.iloc[0])
        arr = np.zeros((len(JUNE), H))
        for j, d in enumerate(JUNE):
            di = DAYS.index(d)
            evs = []
            for r in rcv[(rcv.sku == s) & (rcv.received_ts.dt.date == d)].itertuples():
                evs.append((r.received_ts.hour + r.received_ts.minute / 60, r.u))
            for r in counts[(counts.sku == s) & (counts.count_ts.dt.date == d)].itertuples():
                if not (d == first and r.count_ts.hour < 7) and r.count_ts.hour < 22:
                    evs.append((r.count_ts.hour + r.count_ts.minute / 60, r.adjustment))
            for hi, h in enumerate(OPEN_HOURS):
                end = h + 1
                level += sum(u for t, u in evs if (hi == 0 and t < end) or (hi > 0 and end - 1 <= t < end))
                level -= sales[s][di, hi]
                arr[j, hi] = level
            level -= float(wo[(wo.sku == s) & (wo.date == d)].u.sum())
            close = book_csv[(book_csv.sku == s) & (book_csv.date == d)].book_on_hand_close.iloc[0]
            ok &= abs(level - close) < 1e-9
        out[s] = arr
    return out, ok


def forecasts_made(daily: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """The store's nightly forecast: the 28-day mean of recorded daily sales, made at 22:00 each day."""
    out = {}
    for s, d in daily.items():
        f = np.zeros(len(DAYS))
        for i in range(len(DAYS)):
            f[i] = d[max(0, i - 27):i + 1].mean()
        out[s] = f
    return out


# ---------------------------------------------------------------- 2. gap detector
def learn_patterns(sales: dict[str, np.ndarray]) -> dict[str, dict]:
    """Each item's usual hourly shape and weekday/weekend level, learned from May's till lines."""
    weekend = np.array([d.weekday() >= 5 for d in MAY])
    out = {}
    for s, a in sales.items():
        hist = a[:len(MAY)]
        prof = (hist.sum(axis=0) + 0.5) / (hist.sum() + 0.5 * H)
        per_day = hist.sum(axis=1)
        mean = per_day.mean()
        out[s] = {"profile": prof, "weekday": per_day[~weekend].mean() / mean, "weekend": per_day[weekend].mean() / mean}
    return out


def detect(sales, book, made, patterns, alpha: float) -> list[dict]:
    """Runs of open hours with no sales while the books show stock, flagged once less likely than alpha.

    A run starts at the first open hour without a sale and ends when the item sells again (or the
    books reach zero). Overnight closure does not break a run. Once a run is flagged, one lone unit
    does not end it: inside a long silence a single sale is as likely a scan error (another pack
    scanned as this one) as a sale. Returns every flagged run with the hours it covers, so the
    hours can be treated as censored.
    """
    limit = -math.log(alpha)
    runs = []
    for s in sales:
        p = patterns[s]
        cur, exp, flagged, lone = [], 0.0, None, False
        for j, d in enumerate(JUNE):
            di = DAYS.index(d)
            f = made[s][di - 1]  # last night's forecast
            level = p["weekend"] if d.weekday() >= 5 else p["weekday"]
            for hi, h in enumerate(OPEN_HOURS):
                units = sales[s][di, hi]
                e = f * level * p["profile"][hi]
                if flagged and units == 1 and not lone and book[s][j, hi] > 0:
                    lone = True
                    cur.append({"date": d.isoformat(), "hour": h, "expected": round(float(e), 3), "recorded": 1})
                    exp += e
                    continue
                if units > 0 or book[s][j, hi] <= 0:
                    if flagged:
                        runs.append(flagged | {"hours": cur, "resumed": f"{d}T{h:02d}:00" if units > 0 else None,
                                               "expected_total": round(exp, 1)})
                    cur, exp, flagged, lone = [], 0.0, None, False
                    continue
                cur.append({"date": d.isoformat(), "hour": h, "expected": round(float(e), 3), "recorded": 0})
                exp += e
                if flagged is None and exp > limit:
                    flagged = {"sku": s, "start": f"{cur[0]['date']}T{cur[0]['hour']:02d}:00",
                               "flag_ts": (datetime.combine(d, datetime.min.time()) + timedelta(hours=h + 1)).isoformat(timespec="minutes"),
                               "expected_at_flag": round(exp, 1), "book_at_flag": int(book[s][j, hi])}
        if flagged:
            runs.append(flagged | {"hours": cur, "resumed": None, "expected_total": round(exp, 1)})
    return sorted(runs, key=lambda r: r["flag_ts"])


def daily_rule(daily, book_close, made, n_days: int) -> list[dict]:
    """The nightly rule: n days of sales under a quarter of the forecast while the books show stock."""
    flags = []
    for s in daily:
        for j, d in enumerate(JUNE):
            di = DAYS.index(d)
            f = made[s][di - 1]
            recent = daily[s][di - n_days + 1:di + 1]
            if f > 0 and (recent < ALERT_SHARE * f).all() and book_close[s][j] >= f:
                flags.append({"sku": s, "flag_ts": f"{d}T22:00"})
    return sorted(flags, key=lambda r: r["flag_ts"])


def grid(sales, book, made, patterns, runs_by_alpha, episodes) -> dict:
    """June hour by hour for every warehouse item, for the demo's detector view.

    From the records: units the tills recorded, the sales the detector expected, the rebuilt book,
    and, for each threshold, which hours it treats as censored (a string of 0s and 1s, one per open
    hour) and each flagged run, as open-hour indices: first quiet hour, the hour the alert was raised
    in, last hour. The hours with no stock on the books are censored at every threshold. From the answer key, to score them: whether the shelf was empty when each alert
    fired (as in score_flags) and the share of each open hour the shelf stood empty.
    """
    n = len(JUNE) * H

    def at(d: date, hour: int) -> int:
        return JUNE.index(d) * H + OPEN_HOURS.index(hour)

    out = {}
    for s in sorted(sales):
        p = patterns[s]
        rec, exp, bk = [], [], []
        for j, d in enumerate(JUNE):
            di = DAYS.index(d)
            level = p["weekend"] if d.weekday() >= 5 else p["weekday"]
            for hi in range(H):
                rec.append(int(sales[s][di, hi]))
                exp.append(round(float(made[s][di - 1] * level * p["profile"][hi]), 1))
                bk.append(int(book[s][j, hi]))
        censored, flagged = {}, {}
        for a, runs in runs_by_alpha.items():
            mask = ["0"] * n
            flagged[f"{a:g}"] = []
            for r in runs:
                if r["sku"] != s:
                    continue
                for hr in r["hours"]:
                    mask[at(date.fromisoformat(hr["date"]), hr["hour"])] = "1"
                raised = datetime.fromisoformat(r["flag_ts"]) - timedelta(hours=1)
                first, last = r["hours"][0], r["hours"][-1]
                flagged[f"{a:g}"].append({
                    "first": at(date.fromisoformat(first["date"]), first["hour"]),
                    "alert": at(raised.date(), raised.hour),
                    "last": at(date.fromisoformat(last["date"]), last["hour"]),
                    "expected_at_alert": r["expected_at_flag"], "expected_total": r["expected_total"],
                    "recorded": int(sum(hr["recorded"] for hr in r["hours"])), "book_at_alert": r["book_at_flag"],
                    "resumed": r["resumed"],
                    "real": any(e["sku"] == s and e["start"] <= r["flag_ts"] <= e["end"] for e in episodes),
                })
            censored[f"{a:g}"] = "".join(mask)
        empty = [0.0] * n
        for e in episodes:
            if e["sku"] != s:
                continue
            t0, t1 = datetime.fromisoformat(e["start"]), datetime.fromisoformat(e["end"])
            for j, d in enumerate(JUNE):
                for hi, h in enumerate(OPEN_HOURS):
                    h0 = datetime.combine(d, datetime.min.time()) + timedelta(hours=h)
                    overlap = (min(h0 + timedelta(hours=1), t1) - max(h0, t0)).total_seconds() / 3600
                    if overlap > 0:
                        empty[j * H + hi] = min(1.0, empty[j * H + hi] + overlap)
        out[s] = {"recorded": rec, "expected": exp, "book": bk, "censored": censored, "runs": flagged,
                  "no_stock": "".join("1" if b <= 0 else "0" for b in bk), "empty": [round(x, 1) for x in empty]}
    return out


def open_hours_between(a: str, b: str) -> float:
    """Open hours from a to b, skipping the hours the store is closed."""
    ta, tb = datetime.fromisoformat(a), datetime.fromisoformat(b)
    total, t = 0.0, ta
    while t < tb:
        nxt = min(tb, t.replace(minute=0, second=0) + timedelta(hours=1))
        if 7 <= t.hour < 22:
            total += (nxt - t).total_seconds() / 3600
        t = nxt
    return total


def score_flags(flags: list[dict], episodes: list[dict], min_hours: float = 3.0) -> dict:
    """Precision: flags raised while the shelf really was empty. Recall: gaps of min_hours or more that got a flag."""
    hit = []
    for f in flags:
        ep = next((e for e in episodes if e["sku"] == f["sku"] and e["start"] <= f["flag_ts"] <= e["end"]), None)
        hit.append(ep)
    big = [e for e in episodes if e["empty_open_hours"] >= min_hours]
    caught = [e for e in big if any(h is e for h in hit)]
    lat = []
    for e in caught:
        first = min(f["flag_ts"] for f, h in zip(flags, hit) if h is e)
        lat.append(open_hours_between(e["start"], first))
    return {"flags": len(flags), "true": sum(h is not None for h in hit),
            "precision": round(sum(h is not None for h in hit) / len(flags), 3) if flags else None,
            "gaps": len(big), "caught": len(caught), "recall": round(len(caught) / len(big), 3) if big else None,
            "median_open_hours_to_flag": round(float(np.median(lat)), 2) if lat else None}


# ---------------------------------------------------------------- 3. forecasts
def stockout_hours(sales, book, made, patterns) -> list[dict]:
    """Open hours in June when the books show no stock: censored too, and the records know it.

    The detector skips these hours (its runs end when the books reach zero), so they are added
    here, in the same shape as a run's hours, with the sales the item's pattern expected.
    """
    out = []
    for s in sorted(sales):
        p = patterns[s]
        for j, d in enumerate(JUNE):
            di = DAYS.index(d)
            level = p["weekend"] if d.weekday() >= 5 else p["weekday"]
            for hi, h in enumerate(OPEN_HOURS):
                if book[s][j, hi] <= 0:
                    out.append({"sku": s, "date": d.isoformat(), "hour": h,
                                "expected": round(float(made[s][di - 1] * level * p["profile"][hi]), 3),
                                "recorded": int(sales[s][di, hi])})
    return out


def unconstrain(daily, runs, stockouts) -> dict[str, np.ndarray]:
    """Recorded sales plus the expected sales in every censored hour: the runs the detector
    flagged, and the hours the books show no stock."""
    out = {s: a.copy() for s, a in daily.items()}
    hours = [{"sku": r["sku"], **hr} for r in runs for hr in r["hours"]] + stockouts
    for hr in hours:
        out[hr["sku"]][DAYS.index(date.fromisoformat(hr["date"]))] += max(0.0, hr["expected"] - hr["recorded"])
    return out


def errors(forecast: np.ndarray, actual: np.ndarray) -> dict:
    return {"bias": round(float((forecast - actual).sum() / actual.sum()), 3),
            "wape": round(float(np.abs(forecast - actual).sum() / actual.sum()), 3)}


# ---------------------------------------------------------------- 5. the assistant
def assistant(con, sales, book, made, made_unc, runs, stockouts, key) -> dict:
    """Seven questions at the Monday review, answered from the schema alone and with a domain layer."""
    upto = AS_OF.isoformat()
    w1, w2 = (f"'{a}' AND '{b}'" for a, b in (WEEK1, WEEK2))
    truth = pd.DataFrame(key["truth_daily"])
    truth["date"] = pd.to_datetime(truth.date).dt.date
    t5 = truth[truth.sku == HERO]
    hero_eps = [e for e in key["episodes"] if e["sku"] == HERO]
    hero_runs = [r for r in runs if r["sku"] == HERO and r["flag_ts"] <= "2026-06-15T09:00"]

    # The domain layer: derived views and the observations the schema-only assistant never joins.
    # Censored hours: runs the detector had flagged by the Monday review, and hours with no stock on the books.
    flagged = [r for r in runs if r["flag_ts"] <= "2026-06-15T09:00"]
    cens = pd.DataFrame([{"sku": r["sku"], "run_start": r["start"], "reason": "gap detector", **hr}
                         for r in flagged for hr in r["hours"]]
                        + [{"run_start": None, "reason": "no stock on the books", **hr} for hr in stockouts])
    cens = cens[cens.date <= upto]
    con.register("v_censored_hours", cens)
    est = pd.DataFrame([{"date": d.isoformat(), "sku": s, "recorded": float(sales[s][DAYS.index(d)].sum()),
                         "imputed": float((cens[(cens.sku == s) & (cens.date == d.isoformat())].expected
                                           - cens[(cens.sku == s) & (cens.date == d.isoformat())].recorded).clip(lower=0).sum())}
                        for s in sales for d in JUNE if d <= AS_OF])
    est["demand_estimate"] = est.recorded + est.imputed
    con.register("v_demand_estimate", est)
    hb = pd.DataFrame([{"date": d.isoformat(), "hour": h, "sku": s, "book": float(book[s][j, hi])}
                       for s in book for j, d in enumerate(JUNE) if d <= AS_OF for hi, h in enumerate(OPEN_HOURS)])
    con.register("v_hourly_book", hb)

    def q(sql):
        return rows(con, sql)

    qa = []

    # Q1: a question about the records. Both assistants should get it right.
    sql = f"SELECT sum(units_sold) AS bags FROM daily_sales WHERE sku = '{HERO}' AND date BETWEEN {w2}"
    r = q(sql)
    bags = int(r[0]["bags"])
    qa.append({"id": "sold", "question": "How many bags of 5 kg atta did we sell in the week of 8 June?",
               "kind": "records",
               "naive": {"plan": [{"sql": sql, "result": r}], "answer": f"{bags} bags.", "value": bags},
               "domain": {"plan": [{"sql": sql, "result": r}],
                          "answer": f"The tills scanned {bags} bags. That is what sold, not what shoppers wanted.",
                          "value": bags},
               "gold": {"value": bags, "why": "The tills' count is right: it is a fact about the records."},
               "check": "the number of bags the tills scanned"})

    # Q2: why did sales fall?
    s_weeks = (f"SELECT sum(CASE WHEN date BETWEEN {w1} THEN units_sold END) AS week1, "
               f"sum(CASE WHEN date BETWEEN {w2} THEN units_sold END) AS week2 FROM daily_sales WHERE sku = '{{sku}}'")
    r5 = q(s_weeks.format(sku=HERO))
    s_book = f"SELECT min(book_on_hand_close) AS low, max(book_on_hand_close) AS high FROM inventory_book WHERE sku = '{HERO}' AND date BETWEEN {w2}"
    rb = q(s_book)
    fall = 1 - r5[0]["week2"] / r5[0]["week1"]
    s_share = (f"SELECT round(sum(CASE WHEN sku = '{HERO}' AND date BETWEEN {w1} THEN units_sold END) / "
               f"sum(CASE WHEN date BETWEEN {w1} THEN units_sold END), 3) AS week1, "
               f"round(sum(CASE WHEN sku = '{HERO}' AND date BETWEEN {w2} THEN units_sold END) / "
               f"sum(CASE WHEN date BETWEEN {w2} THEN units_sold END), 3) AS week2 FROM daily_sales WHERE sku LIKE 'ATTA%'")
    rs = q(s_share)
    s_gap = (f"SELECT run_start, max(date || 'T' || lpad(CAST(hour AS VARCHAR), 2, '0')) AS last_hour, count(*) AS open_hours, "
             f"round(sum(expected), 1) AS expected_sales FROM v_censored_hours WHERE sku = '{HERO}' "
             f"AND date BETWEEN {w2} GROUP BY run_start ORDER BY open_hours DESC LIMIT 1")
    rg = q(s_gap)
    s_audit = (f"SELECT a.audit_ts, a.status, b.book_on_hand_close AS book_last_close FROM shelf_audits a "
               f"JOIN inventory_book b ON b.sku = a.sku AND b.date = CAST(a.audit_ts AS DATE) - 1 "
               f"WHERE a.sku = '{HERO}' AND CAST(a.audit_ts AS DATE) BETWEEN {w2}")
    ra = q(s_audit)
    gap = rg[0]
    run = next(r for r in hero_runs if r["start"] == gap["run_start"])
    s_rcv = (f"SELECT count(*) AS deliveries FROM goods_receipts WHERE sku_booked = '{HERO}' "
             f"AND received_ts BETWEEN TIMESTAMP '{gap['run_start']}' AND TIMESTAMP '{run['resumed']}'")
    rr = q(s_rcv)
    s_split = (f"SELECT CASE WHEN date <= '{WEEK1[1]}' THEN 'week1' ELSE 'week2' END AS week, "
               f"CAST(sum(recorded) AS INTEGER) AS recorded, CAST(round(sum(demand_estimate)) AS INTEGER) AS with_gaps_filled "
               f"FROM v_demand_estimate WHERE sku = '{HERO}' GROUP BY ALL ORDER BY week")
    rsp = q(s_split)
    w1e, w2e = rsp[0]["with_gaps_filled"], rsp[1]["with_gaps_filled"]
    shelf_share = (w2e - rsp[1]["recorded"]) / (rsp[0]["recorded"] - rsp[1]["recorded"])
    share_words = "about half" if 0.4 <= shelf_share <= 0.6 else f"about {shelf_share:.0%}"
    empty_audit = next((a for a in ra if a["status"] == "empty"), None)
    ep = next(e for e in hero_eps if e["start"][:10] >= WEEK2[0].isoformat() and e["empty_open_hours"] >= 24)
    true_w1 = int(t5[(t5.date >= WEEK1[0]) & (t5.date <= WEEK1[1])].base_demand.sum())
    true_w2 = int(t5[(t5.date >= WEEK2[0]) & (t5.date <= WEEK2[1])].base_demand.sum())
    lost_w2 = int(t5[(t5.date >= WEEK2[0]) & (t5.date <= WEEK2[1])].lost.sum())
    last_sale = q(f"SELECT max(bill_ts) AS t FROM pos_lines WHERE sku_scanned = '{HERO}' AND bill_ts < TIMESTAMP '{gap['run_start']}'")[0]["t"]
    next_sale = q(f"SELECT min(bill_ts) AS t FROM pos_lines WHERE sku_scanned = '{HERO}' AND bill_ts >= TIMESTAMP '{run['resumed']}'")[0]["t"]
    def fmt(t: str) -> str:
        return datetime.fromisoformat(t[:16]).strftime("%a %-d %b, %H:%M")

    s_book_gap = (f"SELECT CAST(min(b.book) AS INTEGER) AS low, CAST(max(b.book) AS INTEGER) AS high FROM v_hourly_book b "
                  f"JOIN v_censored_hours c USING (sku, date, hour) WHERE c.sku = '{HERO}' AND c.run_start = '{gap['run_start']}'")
    rbg = q(s_book_gap)
    s_gap_rec = (f"SELECT CAST(sum(recorded) AS INTEGER) AS recorded FROM v_censored_hours WHERE sku = '{HERO}' "
                 f"AND run_start = '{gap['run_start']}'")
    rgr = q(s_gap_rec)
    rec_gap = rgr[0]["recorded"]
    rec_words = "nothing" if rec_gap == 0 else ("one bag" if rec_gap == 1 else f"{rec_gap} bags")
    qa.append({"id": "why", "question": "Why did 5 kg atta sales fall in the week of 8 June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_weeks.format(sku=HERO), "result": r5}, {"sql": s_book, "result": rb},
                                  {"sql": s_share, "result": rs}],
                         "answer": (f"Sales fell {fall:.0%}, from {int(r5[0]['week1'])} bags to {int(r5[0]['week2'])}. The books showed "
                                    f"{rb[0]['low']} to {rb[0]['high']} bags on hand all week, so stock was available and this "
                                    f"is not a supply problem. 5 kg's share of atta fell from {rs[0]['week1']:.0%} to "
                                    f"{rs[0]['week2']:.0%}, which suggests shoppers are moving to other pack sizes."),
                         "says_shelf_empty": False, "says_demand_fell": True},
               "domain": {"plan": [{"sql": s_weeks.format(sku=HERO), "result": r5}, {"sql": s_gap, "result": rg},
                                   {"sql": s_gap_rec, "result": rgr}, {"sql": s_book_gap, "result": rbg},
                                   {"sql": s_audit, "result": ra}, {"sql": s_rcv, "result": rr},
                                   {"sql": s_split, "result": rsp}],
                          "answer": (f"From {fmt(last_sale)} to {fmt(next_sale)} the tills recorded {rec_words} in "
                                     f"{gap['open_hours']} open hours, against {round(gap['expected_sales'])} expected, while the "
                                     f"books showed {rbg[0]['low']}–{rbg[0]['high']} bags. "
                                     + (f"The shelf audit at {fmt(empty_audit['audit_ts'])} found the bay empty. " if empty_audit else "")
                                     + ("No delivery arrived before sales resumed, so the bags were in the store but not on the "
                                        "shelf: misplaced or not refilled. ")
                                     + (f"With those hours filled in, the week comes to about {w2e} bags against {w1e}: the empty "
                                        f"shelf explains {share_words} of the fall, and the rest is demand easing after a "
                                        f"strong first week. Nothing says shoppers changed packs.")),
                          "says_shelf_empty": True, "says_demand_fell": False},
               "gold": {"value": f"Shelf empty {ep['start']} to {ep['end']} ({ep['empty_open_hours']} open hours), "
                                 f"{lost_w2} bags not found; shoppers came for {true_w1} bags, then {true_w2}",
                        "why": ("The cases were in the backroom, in the wrong bay. Demand also eased after the month's "
                                "first week; nobody switched packs.")},
               "check": "names the empty shelf as the cause and does not blame shoppers switching packs"})

    # Q3: was it in stock on Thursday?
    thu = date(2026, 6, 11)
    s_book_thu = f"SELECT book_on_hand_close FROM inventory_book WHERE sku = '{HERO}' AND date = '{thu}'"
    rbt = q(s_book_thu)
    s_cens_thu = (f"SELECT count(*) AS censored_open_hours, CAST(sum(recorded) AS INTEGER) AS recorded, "
                  f"round(sum(expected), 1) AS expected_sales FROM v_censored_hours WHERE sku = '{HERO}' AND date = '{thu}'")
    rct = q(s_cens_thu)
    thu_rec = rct[0]["recorded"]
    true_thu = float(t5[t5.date == thu].empty_open_hours.iloc[0])
    qa.append({"id": "in_stock", "question": "Was 5 kg atta in stock on Thursday 11 June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_book_thu, "result": rbt}],
                         "answer": f"Yes: {rbt[0]['book_on_hand_close']} bags on hand at close.", "on_shelf": True},
               "domain": {"plan": [{"sql": s_book_thu, "result": rbt}, {"sql": s_cens_thu, "result": rct}],
                          "answer": (f"On the books, yes: {rbt[0]['book_on_hand_close']} bags. On the shelf, no: the tills "
                                     f"recorded {'nothing' if thu_rec == 0 else ('one bag' if thu_rec == 1 else f'{thu_rec} bags')} "
                                     f"in its {rct[0]['censored_open_hours']} open hours, against {round(rct[0]['expected_sales'])} "
                                     f"expected."),
                          "on_shelf": False},
               "gold": {"value": f"Empty for {true_thu:g} of {H} open hours", "on_shelf": true_thu < H / 2,
                        "why": "Nothing was on the shelf all day."},
               "check": "says whether the bags were on the shelf"})

    # Q4: what is demand?
    s_fc = (f"SELECT round(avg(units_sold), 1) AS bags_per_day FROM daily_sales WHERE sku = '{HERO}' "
            f"AND date <= '{upto}'")
    rf = q(s_fc)
    s_est = (f"SELECT round(avg(demand_estimate), 1) AS bags_per_day, round(avg(recorded), 1) AS recorded_per_day "
             f"FROM v_demand_estimate WHERE sku = '{HERO}'")
    re_ = q(s_est)
    true_dem = round(float(t5[t5.date <= AS_OF].base_demand.mean()), 1)
    qa.append({"id": "demand", "question": "What has daily demand for 5 kg atta been in June so far?", "kind": "reality",
               "naive": {"plan": [{"sql": s_fc, "result": rf}],
                         "answer": f"{rf[0]['bags_per_day']:.1f} bags a day, from daily sales.",
                         "value": rf[0]["bags_per_day"]},
               "domain": {"plan": [{"sql": s_est, "result": re_}],
                          "answer": (f"About {re_[0]['bags_per_day']} bags a day in June so far: {re_[0]['recorded_per_day']} "
                                     f"recorded, plus the sales expected in the hours the shelf was empty."),
                          "value": re_[0]["bags_per_day"]},
               "gold": {"value": true_dem, "why": "Shoppers who came for 5 kg atta, 1 to 14 June, from the answer key."},
               "check": "within 10% of true demand"})

    # Q5: are shoppers switching packs?
    hs = pd.DataFrame([{"date": d.isoformat(), "hour": h, "sku": s, "units": float(sales[s][DAYS.index(d), hi])}
                       for s in sales if s.startswith("ATTA") for d in JUNE if d <= AS_OF for hi, h in enumerate(OPEN_HOURS)])
    con.register("v_hourly_sales", hs)
    s_share_open = (f"SELECT CASE WHEN date <= '{WEEK1[1]}' THEN 'week1' ELSE 'week2' END AS week, "
                    f"round(sum(CASE WHEN sku = '{HERO}' THEN units END) / sum(units), 3) AS share_5kg FROM v_hourly_sales h "
                    f"WHERE NOT EXISTS (SELECT 1 FROM v_censored_hours c WHERE c.sku = '{HERO}' AND c.date = h.date AND c.hour = h.hour) "
                    f"GROUP BY ALL ORDER BY week")
    rso = q(s_share_open)
    td = truth[truth.sku.str.startswith("ATTA")]
    tshare = [float(td[(td.date >= a) & (td.date <= b) & (td.sku == HERO)].base_demand.sum()
                    / td[(td.date >= a) & (td.date <= b)].base_demand.sum()) for a, b in (WEEK1, WEEK2)]
    qa.append({"id": "switching", "question": "Are shoppers switching from 5 kg to 1 kg atta?", "kind": "reality",
               "naive": {"plan": [{"sql": s_share, "result": rs}],
                         "answer": f"Yes: 5 kg's share of atta units fell from {rs[0]['week1']:.0%} to {rs[0]['week2']:.0%} in a week.",
                         "switching": True},
               "domain": {"plan": [{"sql": s_share_open, "result": rso}],
                          "answer": (f"No. In the hours the 5 kg shelf was stocked, its share was {rso[0]['share_5kg']:.0%} in the "
                                     f"first week and {rso[1]['share_5kg']:.0%} in the second. The share fell only in the hours "
                                     f"there was no 5 kg to buy."),
                          "switching": False},
               "gold": {"value": f"Share of atta shoppers {tshare[0]:.0%} then {tshare[1]:.0%}", "switching": False,
                        "why": "Nobody changed packs on purpose; some took 1 kg because 5 kg was not there."},
               "check": "says whether shoppers are switching"})

    # Q6: availability.
    s_osa_book = (f"SELECT round(avg(CASE WHEN book_on_hand_close > 0 THEN 1.0 ELSE 0 END), 3) AS days_in_stock "
                  f"FROM inventory_book WHERE sku = '{HERO}' AND date <= '{upto}'")
    ro = q(s_osa_book)
    open_hours = sum(1 for d in JUNE if d <= AS_OF) * H
    s_osa_dom = (f"SELECT round(1 - count(*) / {open_hours}.0, 3) AS open_hours_on_shelf FROM v_censored_hours WHERE sku = '{HERO}'")
    rod = q(s_osa_dom)
    true_osa = round(1 - float(t5[t5.date <= AS_OF].empty_open_hours.sum()) / open_hours, 3)
    qa.append({"id": "availability", "question": "What was 5 kg atta's on-shelf availability, 1 to 14 June?", "kind": "reality",
               "naive": {"plan": [{"sql": s_osa_book, "result": ro}],
                         "answer": f"{ro[0]['days_in_stock']:.0%}: the books showed stock at every close.",
                         "value": ro[0]["days_in_stock"]},
               "domain": {"plan": [{"sql": s_osa_dom, "result": rod}],
                          "answer": f"About {rod[0]['open_hours_on_shelf']:.0%} of open hours, leaving out the hours the tills show as a gap.",
                          "value": rod[0]["open_hours_on_shelf"]},
               "gold": {"value": true_osa, "why": "Share of open hours with bags on the shelf, from the answer key."},
               "check": "within 5 points of the true share of open hours"})

    # Q7: lost sales.
    s_lost_naive = (f"SELECT count(*) AS days_out_of_stock FROM inventory_book WHERE sku = '{HERO}' "
                    f"AND date BETWEEN {w2} AND book_on_hand_close <= 0")
    rl = q(s_lost_naive)
    s_lost_dom = f"SELECT round(sum(expected)) AS bags FROM v_censored_hours WHERE sku = '{HERO}' AND date BETWEEN {w2}"
    rld = q(s_lost_dom)
    true_lost = int(t5[(t5.date >= WEEK2[0]) & (t5.date <= WEEK2[1])].lost.sum())
    qa.append({"id": "lost", "question": "How many bags of 5 kg atta did shoppers want but not get, 8 to 14 June?",
               "kind": "reality",
               "naive": {"plan": [{"sql": s_lost_naive, "result": rl}],
                         "answer": "None recorded: the item was never out of stock on the books.", "value": 0},
               "domain": {"plan": [{"sql": s_lost_dom, "result": rld}],
                          "answer": f"About {int(rld[0]['bags'])}: the sales expected in the hours the shelf was empty.",
                          "value": int(rld[0]["bags"])},
               "gold": {"value": true_lost, "why": "Bags shoppers asked for and could not find, from the answer key."},
               "check": "within 20% of the true number"})

    # Score each answer against the answer key.
    def right(item, side) -> bool:
        a, g = item[side], item["gold"]
        if item["id"] == "sold":
            return a["value"] == g["value"]
        if item["id"] == "why":
            return a["says_shelf_empty"] and not a["says_demand_fell"]
        if item["id"] == "in_stock":
            return a["on_shelf"] == g["on_shelf"]
        if item["id"] == "demand":
            return abs(a["value"] - g["value"]) / g["value"] <= 0.10
        if item["id"] == "switching":
            return a["switching"] == g["switching"]
        if item["id"] == "availability":
            return abs(a["value"] - g["value"]) <= 0.05
        if item["id"] == "lost":
            return abs(a["value"] - g["value"]) / max(1, g["value"]) <= 0.20
        raise KeyError(item["id"])

    for item in qa:
        item["naive"]["right"] = right(item, "naive")
        item["domain"]["right"] = right(item, "domain")
    # One-line versions for tables.
    short = {
        "sold": (f"{bags} bags", f"{bags} bags", f"{bags} bags"),
        "why": ("Shoppers moving to other packs", "The empty shelf, about half the fall",
                f"Shelf empty {ep['empty_open_hours']:g} open hours"),
        "in_stock": (f"Yes, {rbt[0]['book_on_hand_close']} bags", "Not on the shelf", "Empty all day"),
        "demand": (f"{rf[0]['bags_per_day']:.1f} a day", f"{re_[0]['bags_per_day']} a day", f"{true_dem} a day"),
        "switching": ("Yes", "No", "No"),
        "availability": (f"{ro[0]['days_in_stock']:.0%}", f"{rod[0]['open_hours_on_shelf']:.0%}", f"{true_osa:.0%}"),
        "lost": ("None", f"About {int(rld[0]['bags'])}", f"{true_lost}"),
    }
    for item in qa:
        n, d, g = short[item["id"]]
        item["naive"]["short"], item["domain"]["short"], item["gold"]["short"] = n, d, g
    return {
        "as_of": "2026-06-15T09:00",
        "questions": qa,
        "score": {"naive": sum(i["naive"]["right"] for i in qa), "domain": sum(i["domain"]["right"] for i in qa),
                  "of": len(qa)},
        "schema_only_tables": ["daily_sales", "inventory_book", "forecasts", "store_orders", "products"],
        "domain_layer": {
            "tables_added": ["pos_lines", "shelf_audits", "goods_receipts", "stock_counts"],
            "views": {"v_hourly_sales": "units the tills recorded per item, day and open hour",
                      "v_hourly_book": "the book at the end of each open hour, rebuilt from receipts, sales, counts and write-offs",
                      "v_censored_hours": f"open hours the gap detector flagged (1 in {round(1 / ALPHA):,}), or with no stock on the books",
                      "v_demand_estimate": "recorded sales plus the sales expected in censored hours"},
            "definitions": {
                "sales": "Units the tills scanned. Sales measure demand only while the item is on the shelf.",
                "book stock": "What the system believes is on hand: the last count plus receipts, minus sales and recorded write-offs. A belief, not an observation.",
                "shelf audit": "A person looked at the shelf. An observation.",
                "demand": "What shoppers wanted: sales plus the sales expected in censored hours.",
                "in stock": "On the shelf, not on the books. Use audits and censored hours, never the book alone.",
            },
            "rules": [
                "Treat as censored every open hour with no stock on the books, and every run of no sales longer than the item's usual rate allows while the books show stock.",
                "If sales resume without a delivery, the stock was in the store all along.",
                "Never compare sales across periods without removing censored hours.",
            ],
        },
    }


# ---------------------------------------------------------------- main
def main() -> None:
    con = connect()
    key = json.loads((DATA / "answer-key-retail.json").read_text())
    episodes = [e for e in key["episodes"]]
    truth = pd.DataFrame(key["truth_daily"])
    truth["date"] = pd.to_datetime(truth.date).dt.date

    generic = run_generic_tests(con)
    dc = set(con.execute("SELECT sku FROM products WHERE flow = 'DC'").df().sku)
    sales = {s: a for s, a in hourly_sales(con).items() if s in dc}
    daily = {s: a.sum(axis=1) for s, a in sales.items()}
    book, book_ok = hourly_book(con, sales)
    made = forecasts_made(daily)
    fc_csv = con.execute("SELECT date, sku, forecast_units_per_day FROM forecasts").df()
    fc_csv["date"] = pd.to_datetime(fc_csv.date).dt.date
    fc_ok = all(abs(round(made[r.sku][DAYS.index(r.date)], 2) - r.forecast_units_per_day) < 0.006
                for r in fc_csv.itertuples())
    patterns = learn_patterns(sales)
    bc = con.execute("SELECT date, sku, book_on_hand_close FROM inventory_book").df()
    bc["date"] = pd.to_datetime(bc.date).dt.date
    book_close = {s: bc[bc.sku == s].set_index("date").loc[JUNE].book_on_hand_close.to_numpy(float) for s in book}

    runs_by_alpha = {a: detect(sales, book, made, patterns, a) for a in ALPHAS}
    runs = runs_by_alpha[ALPHA]
    detectors = []
    for n in (2, 1):
        fl = daily_rule(daily, book_close, made, n)
        detectors.append({"label": f"daily rule, {n} day{'s' if n > 1 else ''}", "kind": "daily", "days": n,
                          **score_flags(fl, episodes)})
    for a in ALPHAS:
        detectors.append({"label": f"hourly, 1 in {round(1 / a):,}", "kind": "hourly", "alpha": a,
                          **score_flags(runs_by_alpha[a], episodes)})
    def end_of(r):
        last = r["hours"][-1]
        return f"{last['date']}T{last['hour'] + 1:02d}:00"

    hero_flags = [{k: r[k] for k in ("sku", "start", "flag_ts", "expected_at_flag", "book_at_flag", "resumed")}
                  | {"open_hours_to_flag": round(open_hours_between(r["start"], r["flag_ts"]), 2), "end": end_of(r),
                     "open_hours": len(r["hours"]), "recorded": int(sum(h["recorded"] for h in r["hours"])),
                     "expected_total": r["expected_total"]}
                  for r in runs if r["sku"] == HERO]

    # Domain tests: what the world would contradict.
    audits = con.execute("SELECT * FROM shelf_audits").df()
    empty_with_stock = []
    for a in audits[audits.status == "empty"].itertuples():
        if a.sku in book and a.audit_ts.date() in JUNE:
            j, hi = JUNE.index(a.audit_ts.date()), OPEN_HOURS.index(a.audit_ts.hour)
            level = book[a.sku][j, hi - 1] if hi > 0 else book[a.sku][j, 0]
            if level > 0:
                empty_with_stock.append({"audit_ts": a.audit_ts.isoformat(timespec="minutes"), "sku": a.sku,
                                         "book": int(level)})
    counts = rows(con, "SELECT count_ts, sku, book_before, counted, adjustment, trigger FROM stock_counts "
                       "WHERE abs(adjustment) > greatest(1, 0.02 * book_before)")
    wk = rows(con, f"""SELECT sku, sum(CASE WHEN date BETWEEN '{WEEK1[0]}' AND '{WEEK1[1]}' THEN units_sold END) AS week1,
                       sum(CASE WHEN date BETWEEN '{WEEK2[0]}' AND '{WEEK2[1]}' THEN units_sold END) AS week2
                       FROM daily_sales JOIN products USING (sku) WHERE flow = 'DC' GROUP BY sku
                       HAVING week2 < 0.5 * week1""")
    domain = [
        {"name": "No item goes longer without a sale than its usual rate allows while the books show stock",
         "failing": [{k: r[k] for k in ("sku", "start", "flag_ts", "resumed", "expected_total")}
                     | {"open_hours": len(r["hours"])} for r in runs]},
        {"name": "No shelf audit finds an item empty while the books show stock", "failing": empty_with_stock},
        {"name": "Stock counts agree with the books within 2%", "failing": counts},
        {"name": "No warehouse item's weekly sales halve from one week to the next", "failing": wk},
    ]
    for t in domain:
        t["pass"] = not t["failing"]

    # Forecasts, scored against true demand. The forecast for day d is the one made the night before.
    stockouts = stockout_hours(sales, book, made, patterns)
    unc = unconstrain(daily, runs, stockouts)
    made_unc = forecasts_made(unc)
    jdx = [DAYS.index(d) for d in JUNE]
    fc = {}
    for s in sorted(sales):
        true = truth[truth.sku == s].sort_values("date").base_demand.to_numpy(float)
        naive = np.array([made[s][i - 1] for i in jdx])
        aware = np.array([made_unc[s][i - 1] for i in jdx])
        fc[s] = {"naive_vs_recorded": errors(naive, daily[s][jdx]), "naive_vs_true": errors(naive, true),
                 "aware_vs_true": errors(aware, true), "aware_vs_recorded": errors(aware, daily[s][jdx]),
                 "month_end": {"naive": round(float(made[s][-1]), 1), "aware": round(float(made_unc[s][-1]), 1),
                               "true_june_mean": round(float(true.mean()), 1)}}
    h = fc[HERO]
    tot = {k: errors(np.concatenate([np.array([(made if k.startswith("naive") else made_unc)[s][i - 1] for i in jdx])
                                     for s in sorted(sales)]),
                     np.concatenate([truth[truth.sku == s].sort_values("date").base_demand.to_numpy(float)
                                     for s in sorted(sales)]))
           for k in ("naive_vs_true", "aware_vs_true")}
    rp = {"z": 1.65, "lead": 1, "cover": 2}

    def upto(f, sig):
        rop = math.ceil(f * rp["lead"] + rp["z"] * sig * math.sqrt(rp["lead"]))
        return rop, rop + math.ceil(f * rp["cover"])

    sig_n = float(daily[HERO][-28:].std())
    sig_a = float(unc[HERO][-28:].std())
    series = [{"date": d.isoformat(), "recorded": int(daily[HERO][i]), "true": int(truth[(truth.sku == HERO) & (truth.date == d)].base_demand.iloc[0]),
               "naive": round(float(made[HERO][i - 1]), 1), "aware": round(float(made_unc[HERO][i - 1]), 1),
               "imputed": round(float(unc[HERO][i] - daily[HERO][i]), 1)} for d, i in zip(JUNE, jdx)]

    # Availability, four ways (5 kg, June).
    hero_t = truth[truth.sku == HERO]
    open_june = len(JUNE) * H
    hero_cens = sum(len(r["hours"]) for r in runs if r["sku"] == HERO) + sum(hr["sku"] == HERO for hr in stockouts)
    a5 = audits[audits.sku == HERO]
    availability = {
        "on_the_books": round(float((book[HERO] > 0).mean()), 3),
        "shelf_audits": round(float((a5.status == "on shelf").mean()), 3),
        "books_and_tills": round(1 - hero_cens / open_june, 3),
        "true_open_hours": round(1 - float(hero_t.empty_open_hours.sum()) / open_june, 3),
        "true_demand_served": round(1 - float(hero_t.lost.sum()) / float(hero_t.true_demand.sum()), 3),
        "audits": len(a5),
    }

    out = {
        "about": "What a data team can find in Store 014's records, scored against the answer key.",
        "alpha": ALPHA,
        "tests": {"generic": generic, "domain": domain,
                  "self_checks": {"hourly_book_rebuilds_every_close": bool(book_ok),
                                  "forecast_rebuilt_from_till_lines": bool(fc_ok)}},
        "patterns": {s: {"profile": [round(float(x), 4) for x in p["profile"]], "weekday": round(float(p["weekday"]), 3),
                         "weekend": round(float(p["weekend"]), 3)} for s, p in patterns.items()},
        "detector": {"options": detectors, "hero_flags": hero_flags,
                     "flags": [{k: r[k] for k in ("sku", "start", "flag_ts", "resumed", "expected_at_flag")}
                               | {"open_hours": len(r["hours"]), "end": end_of(r),
                                  "in_real_gap": any(e["sku"] == r["sku"] and e["start"] <= r["flag_ts"] <= e["end"]
                                                     for e in episodes)} for r in runs],
                     "episodes_3h": [e for e in episodes if e["empty_open_hours"] >= 3],
                     "grid": grid(sales, book, made, patterns, runs_by_alpha, episodes)},
        "forecast": {"by_sku": fc, "all_items": tot, "series_5kg": series,
                     "made_5kg": [{"date": d.isoformat(), "naive": round(float(made[HERO][i]), 1),
                                   "aware": round(float(made_unc[HERO][i]), 1)} for d, i in zip(JUNE, jdx)],
                     "order_up_to_month_end": {"naive": upto(h["month_end"]["naive"], sig_n),
                                               "aware": upto(h["month_end"]["aware"], sig_a)},
                     "imputed_bags_june": round(float(unc[HERO][jdx].sum() - daily[HERO][jdx].sum()), 1)},
        "availability": availability,
        "assistant": assistant(con, sales, book, made, made_unc, runs, stockouts, key),
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    a = out["assistant"]["score"]
    print(f"wrote {OUT.relative_to(ROOT)}: generic tests {sum(t['pass'] for t in generic)}/{len(generic)} pass, "
          f"domain tests {sum(t['pass'] for t in domain)}/{len(domain)} pass; book rebuilt {book_ok}, forecast rebuilt {fc_ok}; "
          f"assistant {a['naive']}/{a['of']} vs {a['domain']}/{a['of']}")


if __name__ == "__main__":
    main()
