"""Build the Store 014 dbt project: the series' data tests and domain tests, on the records, in dbt.

    python3 scripts/kit/make_dbt.py            # write public/kit/store-014-dbt/ and its zip
    python3 scripts/kit/make_dbt.py --check    # also run `dbt build` on it (needs dbt-duckdb) and
                                               # compare every test's failing rows with the analyses

The project reads the CSV records with DuckDB. Its pipeline tests are the data tests from the three
technical companions (keys, values, reconciliations): they pass, except one about milk. Its domain
tests are the tests about the world from the same companions: they fail on June's records, on
purpose, as warnings, each storing its failing rows. The SQL is the analyses' SQL with table names
turned into refs; the gap detector, which the retail analysis runs in Python, is written here in SQL.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "public" / "data" / "india-grocery"
OUT = ROOT / "public" / "kit" / "store-014-dbt"
ZIP = ROOT / "public" / "kit" / "store-014-dbt.zip"
SRC = ROOT / "src" / "data"
RAW = "https://raw.githubusercontent.com/kvinayakpai/domain-series/main/public/data/india-grocery/"

# Model name -> (file, columns read as text). Names follow the technical companions' SQL.
RECORDS = {
    "products": ("products.csv", ["gtin"]),
    "pos_lines": ("pos-lines-may-june.csv", ["gtin_scanned"]),
    "daily_sales": ("daily-sales-june.csv", []),
    "inventory_book": ("inventory-book-june.csv", []),
    "forecasts": ("forecasts-june.csv", []),
    "store_orders": ("store-orders-june.csv", []),
    "goods_receipts": ("goods-receipts-june.csv", ["sscc"]),
    "fresh_deliveries": ("fresh-deliveries-june.csv", []),
    "stock_counts": ("stock-counts-june.csv", []),
    "shelf_audits": ("shelf-audits-june.csv", []),
    "write_offs": ("write-offs-june.csv", []),
    "shipments": ("shipments-june.csv", []),
    "notice_lines": ("shipping-notice-lines-june.csv", ["sscc", "gtin"]),
    "picks": ("dc-pick-confirmations-june.csv", []),
    "pallets": ("pallets-june.csv", ["sscc"]),
    "dc_adjustments": ("dc-stock-adjustments-june.csv", []),
    "till_payments": ("pos-payments-june.csv", ["rrn", "note"]),
    "psp_upi": ("psp-upi-report-june.csv", ["rrn", "bill_ref"]),
    "settlements": ("upi-settlements-june.csv", []),
    "refunds": ("upi-refunds-june.csv", ["rrn"]),
    "complaints": ("customer-complaints-june.csv", ["rrn"]),
}
# The map's record ids (store-014-map.json) for the models it describes.
MAP_ID = {"pos_lines": "lines", "inventory_book": "book", "shelf_audits": "audits", "stock_counts": "counts",
          "picks": "picks", "notice_lines": "notice", "pallets": "labels", "goods_receipts": "receipts",
          "dc_adjustments": "corrections", "till_payments": "payments", "psp_upi": "provider",
          "settlements": "settlements", "refunds": "refunds", "complaints": "complaints"}
DOMAIN_MODELS = ["hourly_book", "silent_runs", "corrections", "mirror_pairs", "receipt_survival",
                 "timeouts_matched", "extra_charges", "join_agreement"]


def ref(sql: str, names=None) -> str:
    """Turn the companions' table names into refs, wherever they follow FROM or JOIN."""
    names = names or list(RECORDS) + DOMAIN_MODELS
    for t in sorted(names, key=len, reverse=True):
        sql = re.sub(rf"(?i)(\b(?:from|join)\s+)({t})\b", lambda m: f"{m.group(1)}{{{{ ref('{m.group(2)}') }}}}", sql)
    return sql


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s[:60].rstrip("_")


# ---------------------------------------------------------------- domain models
HOURLY_BOOK = """
-- The books as the store's system holds them at the end of each June open hour, for warehouse items:
-- the night before's close (on 1 June, the morning's count), plus receipts and count corrections as
-- they happen, minus the till's sales hour by hour. The retail companion rebuilds it the same way.
with dc as (select sku from {{ ref('products') }} where flow = 'DC'),
days as (select cast(d as date) as date from range(date '2026-06-01', date '2026-06-29', interval 1 day) t(d)),
hours as (select h from range(7, 22) t(h)),
sold as (
  select sku_scanned as sku, cast(bill_ts as date) as date, hour(bill_ts) as h, sum(qty) as units
  from {{ ref('pos_lines') }} group by all),
starts as (
  select sku, date + 1 as date, book_on_hand_close as book from {{ ref('inventory_book') }}
  union all
  select sku, cast(count_ts as date), counted from {{ ref('stock_counts') }}
  where count_ts = timestamp '2026-06-01 05:45'),
events as (
  select sku_booked as sku, received_ts as ts, units_booked as units from {{ ref('goods_receipts') }}
  union all
  select sku, count_ts, adjustment from {{ ref('stock_counts') }}
  where count_ts > timestamp '2026-06-01 06:00' and hour(count_ts) < 22),
grid as (
  select dc.sku, days.date, hours.h, coalesce(s.units, 0) as units, st.book as start_book
  from dc cross join days cross join hours
  join starts st on st.sku = dc.sku and st.date = days.date
  left join sold s on s.sku = dc.sku and s.date = days.date and s.h = hours.h)
select g.sku, g.date, g.h, g.units,
       g.start_book
       + coalesce((select sum(e.units) from events e where e.sku = g.sku and cast(e.ts as date) = g.date
                   and e.ts < cast(g.date as timestamp) + to_hours(g.h + 1)), 0)
       - sum(g.units) over (partition by g.sku, g.date order by g.h) as book
from grid g
"""

SILENT_RUNS = """
-- The gap detector, in SQL. Each warehouse item's usual rate for an open hour is last night's
-- forecast (the 28-day mean of daily sales), times its weekday or weekend level, times its share of
-- the day in that hour, both learned from May. A run of open hours with no sale while the books show
-- stock is flagged once its expected sales pass ln(1000): no sale that long is less likely than 1 in
-- 1,000. Closing time does not break a run, and once a run is flagged one lone unit does not end it:
-- inside a long silence a single sale is as likely a scan error as a sale.
with dc as (select sku from {{ ref('products') }} where flow = 'DC'),
days as (select cast(d as date) as date from range(date '2026-05-04', date '2026-06-29', interval 1 day) t(d)),
hours as (select h from range(7, 22) t(h)),
sold as (
  select sku_scanned as sku, cast(bill_ts as date) as date, hour(bill_ts) as h, sum(qty) as units
  from {{ ref('pos_lines') }} group by all),
grid as (
  select dc.sku, days.date, hours.h, coalesce(s.units, 0) as units
  from dc cross join days cross join hours
  left join sold s on s.sku = dc.sku and s.date = days.date and s.h = hours.h),
daily as (select sku, date, sum(units) as units from grid group by all),
shape as (
  select sku, h, (sum(units) + 0.5) / (sum(sum(units)) over (partition by sku) + 0.5 * 15) as share
  from grid where date < date '2026-06-01' group by sku, h),
level as (
  select sku,
         avg(case when dayofweek(date) not in (0, 6) then units end) / avg(units) as weekday,
         avg(case when dayofweek(date) in (0, 6) then units end) / avg(units) as weekend
  from daily where date < date '2026-06-01' group by sku),
forecast as (
  select sku, date + 1 as date,
         avg(units) over (partition by sku order by date rows between 27 preceding and current row) as per_day
  from daily),
hours_june as (
  select b.sku, b.date, b.h, b.units, b.book,
         f.per_day * (case when dayofweek(b.date) in (0, 6) then l.weekend else l.weekday end) * s.share as expected,
         case when b.units > 0 or b.book <= 0 then 1 else 0 end as breaks
  from {{ ref('hourly_book') }} b
  join forecast f on f.sku = b.sku and f.date = b.date
  join level l on l.sku = b.sku
  join shape s on s.sku = b.sku and s.h = b.h),
runs as (
  select *, sum(breaks) over (partition by sku order by date, h rows unbounded preceding) as run_id
  from hours_june),
silent as (
  select *, cast(date as timestamp) + to_hours(h) as hour_ts,
         sum(expected) over (partition by sku, run_id order by date, h rows unbounded preceding) as expected_so_far
  from runs where breaks = 0),
first_flag as (
  select sku, run_id, min(hour_ts) as start,
         min(hour_ts) filter (where expected_so_far > ln(1000)) as flag_hour
  from silent group by sku, run_id),
breaker as (select sku, run_id, units, book from runs where breaks = 1),
flagged as (select * from first_flag where flag_hour is not null)
select f.sku, f.start, f.flag_hour + interval 1 hour as flag_ts,
       round(s.expected_so_far, 1) as expected_at_flag, s.book as book_at_flag
from flagged f
join silent s on s.sku = f.sku and s.run_id = f.run_id and s.hour_ts = f.flag_hour
-- A run that begins after one lone unit, right after a flagged run, is the same silence.
where not exists (
  select 1 from breaker b join flagged p on p.sku = b.sku and p.run_id = b.run_id - 1
  where b.sku = f.sku and b.run_id = f.run_id and b.units = 1 and b.book > 0)
"""


def domain_models() -> dict[str, str]:
    sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
    import logistics as LG
    import payments as PY

    def body(view_sql: str) -> str:
        return ref(re.sub(r"(?is)^\s*CREATE OR REPLACE VIEW \w+ AS\s*", "", view_sql).strip())

    finale = json.loads((SRC / "finale.json").read_text())
    alias = {"notice": "notice_lines", "receipts": "goods_receipts", "book": "inventory_book", "fresh": "fresh_deliveries",
             "till_lines": "pos_lines", "provider": "psp_upi", "dc_corrections": "dc_adjustments", "labels": "pallets"}
    parts = []
    for j in finale["joins"]:
        if j["sql"] is None:
            sql = ("select count(*) as compared, sum(case when outcome = 'never debited' then 1 else 0 end) as agree "
                   "from {{ ref('timeouts_matched') }}")
        else:
            sql = j["sql"]
            for a, b in alias.items():
                sql = re.sub(rf"(?i)(\b(?:FROM|JOIN)\s+){a}\b", rf"\1{b}", sql)
            sql = ref(sql, list(RECORDS))
        parts.append(f"select '{j['id']}' as join_id, '{j['a']}' as record_a, '{j['b']}' as record_b, compared, agree from ({sql})")
    joins = ("-- The finale's twelve joins between June's records, and how often each pair agrees. Eight always\n"
             "-- agree: one record is written from the other. Four sometimes disagree: one side looks at the world.\n"
             + "\nunion all\n".join(parts) + "\n")
    return {
        "hourly_book": HOURLY_BOOK.strip() + "\n",
        "silent_runs": SILENT_RUNS.strip() + "\n",
        "corrections": "-- Every count correction in both buildings, in units and in cases.\n" + body(LG.CORRECTIONS) + "\n",
        "mirror_pairs": ("-- Pairs of corrections in one product family with opposite signs, each at least a case and within\n"
                         "-- 15% of each other in cases, within a week: neighbouring slots, one store count, or one item\n"
                         "-- in both buildings.\n" + body(LG.MIRRORS).replace("v_corrections", "{{ ref('corrections') }}") + "\n"),
        "receipt_survival": "-- Receipt lines whose next count, within a week, took off half or more of what was booked.\n" + body(LG.SURVIVAL) + "\n",
        "timeouts_matched": ("-- Each UPI attempt the till gave up on, matched to the provider's row for it: same amount, a start\n"
                             "-- within five seconds, one to one, nearest first.\n" + body(PY.MATCH) + "\n"),
        "extra_charges": ("-- Late credits on bills the customer then paid again.\n"
                          + body(PY.EXTRA).replace("v_timeouts_matched", "{{ ref('timeouts_matched') }}") + "\n"),
        "join_agreement": joins,
    }


# ---------------------------------------------------------------- tests
PIPELINE_WARN = {"Book stock: one row per item per day, never negative"}  # fails on milk: the till's scan errors


def pipeline_tests() -> dict[str, tuple[str, str]]:
    out = {}
    for f in ("retail-ai.json", "logistics-ai.json", "payments-ai.json"):
        for t in json.loads((SRC / f).read_text())["tests"]["generic"]:
            out[slug(t["name"])] = (t["name"], ref(t["sql"], list(RECORDS)))
    return out


DOMAIN_TESTS = {
    # Retail
    "no_silence_with_stock_on_the_books": (
        "No item goes longer without a sale than its usual rate allows while the books show stock",
        "select * from {{ ref('silent_runs') }}"),
    "no_audit_finds_empty_with_stock": (
        "No shelf audit finds an item empty while the books show stock",
        ("select a.audit_ts, a.sku, b.book from {{ ref('shelf_audits') }} a\n"
         "join {{ ref('hourly_book') }} b on b.sku = a.sku and b.date = cast(a.audit_ts as date)\n"
         "  and b.h = greatest(hour(a.audit_ts) - 1, 7)\n"
         "where a.status = 'empty' and b.book > 0")),
    "counts_agree_with_the_books_within_2pct": (
        "Stock counts agree with the books within 2%",
        ("select count_ts, sku, book_before, counted, adjustment, trigger from {{ ref('stock_counts') }}\n"
         "where abs(adjustment) > greatest(1, 0.02 * book_before)")),
    "no_weekly_sales_halve": (
        "No warehouse item's weekly sales halve from one week to the next",
        ("select sku, sum(case when date between '2026-06-01' and '2026-06-07' then units_sold end) as week1,\n"
         "  sum(case when date between '2026-06-08' and '2026-06-14' then units_sold end) as week2\n"
         "from {{ ref('daily_sales') }} join {{ ref('products') }} using (sku) where flow = 'DC' group by sku\n"
         "having week2 < 0.5 * week1")),
    # Logistics
    "no_mirror_pair_in_one_building": (
        "No count correction has a mirror image in the same building",
        "select * from {{ ref('mirror_pairs') }} where kind = 'same building'"),
    "no_warehouse_correction_mirrored_at_the_store": (
        "No warehouse correction is mirrored at the store",
        "select * from {{ ref('mirror_pairs') }} where kind = 'across buildings'"),
    "every_receipt_survives_the_next_count": (
        "Every receipt survives the next count",
        "select * from {{ ref('receipt_survival') }}"),
    "something_checks_each_pallet": (
        "Something other than the pick checks what is on each pallet (a scale weight or a case scan)",
        ("select sscc, shipment_id, weight_check from {{ ref('pallets') }}\n"
         "where weight_check = 'not weighed'\n"
         "  and sscc not in (select sscc from {{ ref('goods_receipts') }} where receipt_method like 'case scan%')")),
    # Payments
    "every_provider_success_has_an_approved_payment": (
        "Every success in the provider's report has an approved till payment with its RRN",
        ("select rrn, initiated_ts, amount_inr, status_ts from {{ ref('psp_upi') }}\n"
         "where status = 'success' and rrn not in\n"
         "  (select rrn from {{ ref('till_payments') }} where till_status = 'approved' and rrn is not null)")),
    "every_upi_attempt_joins_by_rrn": (
        "Every UPI attempt at the till joins the provider's final status by RRN",
        "select bill_id, attempt, ts, amount_inr from {{ ref('till_payments') }} where till_status = 'failed: no response'"),
    "no_bill_paid_twice": (
        "No bill is paid twice, once timed-out attempts are matched to the provider's report",
        "select * from {{ ref('extra_charges') }}"),
    "extra_charges_back_within_5_days": (
        "Every extra charge comes back within 5 days of the debit (refunds as of the review, 29 June 09:00)",
        ("select e.*, r.completed_ts from {{ ref('extra_charges') }} e\n"
         "left join {{ ref('refunds') }} r on r.rrn = e.rrn and r.completed_ts <= timestamp '2026-06-29 09:00'\n"
         "where r.rrn is null or r.completed_ts > e.debited_ts + interval 5 day")),
    "no_burst_of_timeouts": (
        "No hour has three or more timeouts and a timeout share over 10 times the month's",
        ("with h as (select strftime(ts, '%Y-%m-%dT%H:00') as hour, count(*) as upi_attempts,\n"
         "    sum(case when till_status = 'failed: no response' then 1 else 0 end) as no_answer\n"
         "  from {{ ref('till_payments') }} where tender = 'UPI' group by all),\n"
         "m as (select sum(no_answer) / sum(upi_attempts) as share from h)\n"
         "select h.*, round(h.no_answer / h.upi_attempts, 3) as share from h, m\n"
         "where h.no_answer >= 3 and h.no_answer / h.upi_attempts > 10 * m.share")),
}
# What the analyses found for each domain test: the dbt run must find the same number of rows.
EXPECTED = {
    "no_silence_with_stock_on_the_books": ("retail-ai.json", "No item goes longer without a sale than its usual rate allows while the books show stock"),
    "no_audit_finds_empty_with_stock": ("retail-ai.json", "No shelf audit finds an item empty while the books show stock"),
    "counts_agree_with_the_books_within_2pct": ("retail-ai.json", "Stock counts agree with the books within 2%"),
    "no_weekly_sales_halve": ("retail-ai.json", "No warehouse item's weekly sales halve from one week to the next"),
    "no_mirror_pair_in_one_building": ("logistics-ai.json", "No count correction has a mirror image in the same building"),
    "no_warehouse_correction_mirrored_at_the_store": ("logistics-ai.json", "No warehouse correction is mirrored at the store"),
    "every_receipt_survives_the_next_count": ("logistics-ai.json", "Every receipt survives the next count"),
    "something_checks_each_pallet": ("logistics-ai.json", "Something other than the pick checks what is on each pallet (a scale weight or a case scan)"),
    "every_provider_success_has_an_approved_payment": ("payments-ai.json", "Every success in the provider's report has an approved till payment with its RRN"),
    "every_upi_attempt_joins_by_rrn": ("payments-ai.json", "Every UPI attempt at the till joins the provider's final status by RRN"),
    "no_bill_paid_twice": ("payments-ai.json", "No bill is paid twice, once timed-out attempts are matched to the provider's report"),
    "extra_charges_back_within_5_days": ("payments-ai.json", "Every extra charge comes back within 5 days of the debit"),
    "no_burst_of_timeouts": ("payments-ai.json", "No hour has three or more timeouts and a timeout share over 10 times the month's"),
}

DOMAIN_OF = {k: v[0].split("-")[0] for k, v in EXPECTED.items()}

GET_DATA = f'''"""Fetch Store 014's records into ./data, where the project reads them.

    python get_data.py                 # download them from GitHub
    python get_data.py --from DIR      # or copy them from a folder that has them
"""
import shutil
import sys
import urllib.request
from pathlib import Path

FILES = {json.dumps(sorted(f for f, _ in RECORDS.values()), indent=4)}
RAW = "{RAW}"
here = Path(__file__).resolve().parent / "data"
here.mkdir(exist_ok=True)
src = Path(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else None
for f in FILES:
    if src:
        shutil.copy(src / f, here / f)
    else:
        urllib.request.urlretrieve(RAW + f, here / f)
    print("data/" + f)
'''


def readme(tests: dict, domain: dict) -> str:
    groups = {"retail": "The shelf", "logistics": "The truck", "payments": "The money"}
    lines = ["# Store 014 in dbt", "",
             "The data tests and the domain tests from the series *Why Domain Matters*",
             "(https://kvinayakpai.github.io/domain-series/), as a dbt project on DuckDB. It reads the",
             "series' records of one month at Store 014, a fictional Bengaluru supermarket in a synthetic",
             "world, as CSV files.", "",
             "## Run it", "",
             "```", "pip install dbt-duckdb", "python get_data.py          # skip if ./data is already there",
             "dbt build --profiles-dir .", "```", "",
             "`dbt build` creates one view per record in `models/records`, the views the domain tests use in",
             "`models/domain`, and runs two sets of tests:", "",
             f"- `tests/pipeline`: the {len(tests)} data tests from the technical companions. Keys, values and",
             "  reconciliations. They pass, except one: the full-cream milk book goes below zero on six days,",
             "  from the till's scan errors. It is set to warn.",
             f"- `tests/domain`: {len(domain)} tests about how a store, a warehouse and UPI work. They fail on",
             "  June's records, as warnings, and store their failing rows: each is one of June's failures,",
             "  found from the records alone.", "",
             "Then `dbt show --select join_agreement` lists the twelve joins between the records and how often",
             "each pair agrees: eight always agree, because one record is written from the other.", "",
             "## The domain tests", ""]
    for d, name in groups.items():
        lines.append(f"{name}:")
        lines += [f"- `{k}`: {v[0]}" for k, v in domain.items() if DOMAIN_OF[k] == d]
        lines.append("")
    lines += ["Each record's model carries what writes it and what it looks at in the world, from the",
              "series' map of the records (`store-014-map.json`), in its description and `meta`.", ""]
    return "\n".join(lines)


def records_yml() -> str:
    m = json.loads((DATA / "store-014-map.json").read_text())
    recs = {r["id"]: r for r in m["records"]}
    things = {t["id"]: t["name"] for t in m["things"]}
    out = ["version: 2", "", "models:"]
    for name, (file, _) in RECORDS.items():
        r = recs.get(MAP_ID.get(name, ""))
        desc = f"{file}."
        meta = {"file": file}
        if r:
            looks = ", ".join(f"{things[x['thing']].lower()}{' (in part)' if x['how'] == 'part' else ''}" for x in r["looks_at"])
            desc = f"{r['name']}: written by {r['written_by']}. " + (f"Looks at {looks}." if looks else "Looks at nothing itself; it is written from other records.")
            meta |= {"written_by": r["written_by"], "looks_at": [x["thing"] for x in r["looks_at"]], "map_id": r["id"]}
        out += [f"  - name: {name}", f"    description: {json.dumps(desc, ensure_ascii=False)}",
                f"    meta: {json.dumps(meta, ensure_ascii=False)}"]
    return "\n".join(out) + "\n"


def write() -> tuple[dict, dict]:
    if OUT.exists():
        data = OUT / "data"
        keep = data.exists()
        if keep:
            shutil.move(str(data), str(OUT.parent / ".dbt-data"))
        shutil.rmtree(OUT)
        OUT.mkdir(parents=True)
        if keep:
            shutil.move(str(OUT.parent / ".dbt-data"), str(data))
    for p in ("models/records", "models/domain", "tests/pipeline", "tests/domain"):
        (OUT / p).mkdir(parents=True, exist_ok=True)
    (OUT / "dbt_project.yml").write_text(
        "name: store_014\nversion: \"1.0.0\"\nconfig-version: 2\nprofile: store_014\n\n"
        "model-paths: [\"models\"]\ntest-paths: [\"tests\"]\n\n"
        "flags:\n  send_anonymous_usage_stats: false\n\n"
        "vars:\n  data_dir: data  # the folder holding the CSV records; get_data.py fills it\n\n"
        "models:\n  store_014:\n    +materialized: view\n\n"
        "data_tests:\n  store_014:\n    domain:\n      +severity: warn\n      +store_failures: true\n")
    (OUT / "profiles.yml").write_text("store_014:\n  target: dev\n  outputs:\n    dev:\n      type: duckdb\n      path: store_014.duckdb\n      threads: 4\n")
    (OUT / ".gitignore").write_text("target/\nlogs/\ndbt_packages/\n*.duckdb\n*.duckdb.wal\n")
    for name, (file, text) in RECORDS.items():
        types = "{" + ", ".join(f"'{c}': 'VARCHAR'" for c in text) + "}"
        opt = f", types={types}" if text else ""
        (OUT / "models" / "records" / f"{name}.sql").write_text(
            f"select * from read_csv_auto('{{{{ var(\"data_dir\") }}}}/{file}'{opt})\n")
    (OUT / "models" / "records" / "_records.yml").write_text(records_yml())
    for name, sql in domain_models().items():
        (OUT / "models" / "domain" / f"{name}.sql").write_text(sql)
    tests = pipeline_tests()
    for k, (title, sql) in tests.items():
        cfg = "{{ config(severity='warn') }}\n" if title in PIPELINE_WARN else ""
        (OUT / "tests" / "pipeline" / f"{k}.sql").write_text(f"-- {title}\n{cfg}{sql}\n")
    for k, (title, sql) in DOMAIN_TESTS.items():
        (OUT / "tests" / "domain" / f"{k}.sql").write_text(f"-- {title}\n{sql}\n")
    (OUT / "get_data.py").write_text(GET_DATA)
    (OUT / "README.md").write_text(readme(tests, DOMAIN_TESTS))
    return tests, DOMAIN_TESTS


def check(tests: dict) -> dict:
    dbt = shutil.which("dbt") or sys.exit("dbt not found: pip install dbt-duckdb")
    data = OUT / "data"
    data.mkdir(exist_ok=True)
    for f, _ in RECORDS.values():
        shutil.copy(DATA / f, data / f)
    res = subprocess.run([dbt, "build", "--profiles-dir", "."], cwd=OUT, capture_output=True, text=True, check=False)
    run = json.loads((OUT / "target" / "run_results.json").read_text())
    found = {}
    for r in run["results"]:
        uid = r["unique_id"]
        if uid.startswith("test."):
            found[uid.split(".")[2]] = (r["status"], r.get("failures") or 0)
    bad = [(k, v) for k, v in found.items() if (k in tests and v[0] != "pass" and k != slug(next(iter(PIPELINE_WARN))))]
    if bad or res.returncode:
        print(res.stdout[-3000:])
        sys.exit(f"pipeline tests that did not pass: {bad}")
    for k, (f, name) in EXPECTED.items():
        want = len(next(t for t in json.loads((SRC / f).read_text())["tests"]["domain"] if t["name"] == name)["failing"])
        status, n = found[k]
        assert status == "warn" and n == want, (k, status, n, want)
    agree = subprocess.run([dbt, "show", "--profiles-dir", ".", "--select", "join_agreement", "--limit", "20", "--output", "json"],
                           cwd=OUT, capture_output=True, text=True, check=False)
    out = agree.stdout
    rows = json.loads(out[out.index("\n{") + 1:])["show"] if "\n{" in out else []
    fin = {j["id"]: (j["compared"], j["agree"]) for j in json.loads((SRC / "finale.json").read_text())["joins"]}
    assert {r["join_id"]: (r["compared"], r["agree"]) for r in rows} == fin, rows
    summary = {"pipeline": {"tests": len(tests), "pass": sum(found[k][0] == "pass" for k in tests), "warn": sum(found[k][0] == "warn" for k in tests)},
               "domain": {k: found[k][1] for k in EXPECTED}}
    for p in (OUT / "target", OUT / "logs", data):
        shutil.rmtree(p, ignore_errors=True)
    for p in OUT.glob("*.duckdb*"):
        p.unlink()
    return summary


def main() -> None:
    tests, domain = write()
    if "--check" in sys.argv:
        s = check(tests)
        print(json.dumps(s, indent=1))
        (SRC / "dbt-kit.json").write_text(json.dumps(s | {"domain_titles": {k: v[0] for k, v in domain.items()},
                                                          "domain_of": DOMAIN_OF}, indent=1) + "\n")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, Path("store-014-dbt") / p.relative_to(OUT))
        for f, _ in RECORDS.values():
            z.write(DATA / f, Path("store-014-dbt") / "data" / f)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(tests)} pipeline tests, {len(domain)} domain tests) and {ZIP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
