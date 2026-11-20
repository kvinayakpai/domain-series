"""Write Store 014's records as one Postgres database, for Auto-Ontology to read.

The tables are Season 1's downloadable June records (public/data/india-grocery), loaded
as they are: one schema per part of the business (the store, the warehouse,
payments), column names unchanged, types read from the values, and a primary key
only where the file's rows are unique on it. There are no foreign keys and no
descriptions, as with most systems' tables, so the joins are left for Auto-Ontology
to find. The answer keys are not loaded: they hold what really happened, which no
system recorded.

    python3 auto-ontology-demo/seed_store014.py > store014.sql
    psql -d store014 -v ON_ERROR_STOP=1 -f store014.sql
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data" / "india-grocery"

# file -> (schema, table)
TABLES = {
    "products.csv": ("store", "products"),
    "pos-lines-may-june.csv": ("store", "pos_lines"),
    "daily-sales-june.csv": ("store", "daily_sales"),
    "inventory-book-june.csv": ("store", "inventory_book"),
    "forecasts-june.csv": ("store", "forecasts"),
    "store-orders-june.csv": ("store", "store_orders"),
    "goods-receipts-june.csv": ("store", "goods_receipts"),
    "fresh-deliveries-june.csv": ("store", "fresh_deliveries"),
    "stock-counts-june.csv": ("store", "stock_counts"),
    "shelf-audits-june.csv": ("store", "shelf_audits"),
    "write-offs-june.csv": ("store", "write_offs"),
    "dc-pick-confirmations-june.csv": ("warehouse", "pick_confirmations"),
    "dc-stock-adjustments-june.csv": ("warehouse", "stock_adjustments"),
    "shipments-june.csv": ("warehouse", "shipments"),
    "shipping-notice-lines-june.csv": ("warehouse", "shipping_notice_lines"),
    "pallets-june.csv": ("warehouse", "pallets"),
    "pos-payments-june.csv": ("payments", "pos_payments"),
    "psp-upi-report-june.csv": ("payments", "psp_upi_report"),
    "upi-settlements-june.csv": ("payments", "upi_settlements"),
    "upi-refunds-june.csv": ("payments", "upi_refunds"),
    "customer-complaints-june.csv": ("payments", "customer_complaints"),
}

# Candidate primary keys, tried in order; the first the rows are unique on is declared.
KEYS = {
    "products": [("sku",)],
    "pos_lines": [("bill_id", "line")],
    "daily_sales": [("date", "sku")],
    "inventory_book": [("date", "sku")],
    "forecasts": [("date", "sku")],
    "store_orders": [("order_id",), ("order_id", "sku")],
    "goods_receipts": [("grn_id", "line"), ("grn_id",)],
    "fresh_deliveries": [("delivery_ts", "route", "sku"), ("delivery_ts", "sku")],
    "stock_counts": [("count_ts", "sku")],
    "shelf_audits": [("audit_ts", "sku")],
    "write_offs": [("date", "sku", "reason"), ("date", "sku")],
    "pick_confirmations": [("order_id", "line"), ("shipment_id", "line")],
    "stock_adjustments": [("adjusted_ts", "sku")],
    "shipments": [("shipment_id",)],
    "shipping_notice_lines": [("shipment_id", "line"), ("shipment_id", "sscc", "line")],
    "pallets": [("sscc",)],
    "pos_payments": [("bill_id", "attempt")],
    "psp_upi_report": [("rrn",)],
    "upi_settlements": [("settlement_date",)],
    "upi_refunds": [("refund_id",)],
    "customer_complaints": [],
}

# Codes stay text even when they are all digits: barcodes, pallet labels, references.
CODE = re.compile(r"(_id|gtin|sscc|rrn|_ref|sku|^slot|dc_slot|vehicle|route)$|^(gtin|sku)_")
INT = re.compile(r"^-?\d+$")
DEC = re.compile(r"^-?\d+\.\d+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?$")


def column_type(name: str, values: list[str]) -> str:
    seen = [v for v in values if v != ""]
    if CODE.search(name) or not seen:
        return "text"
    if all(TS.match(v) for v in seen):
        return "timestamp"
    if all(DATE.match(v) for v in seen):
        return "date"
    if all(INT.match(v) for v in seen):
        return "bigint" if any(abs(int(v)) > 2_000_000_000 for v in seen) else "integer"
    if all(INT.match(v) or DEC.match(v) for v in seen):
        return "numeric"
    if all(v in ("true", "false") for v in seen):
        return "boolean"
    return "text"


def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def copy_value(value: str) -> str:
    if value == "":
        return r"\N"
    return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def main() -> None:
    out = sys.stdout
    out.write("-- Store 014's June records, from public/data/india-grocery\n")
    out.write("SET client_encoding = 'UTF8';\nSET client_min_messages = warning;\n")
    for schema in sorted({s for s, _ in TABLES.values()}):
        out.write(f"CREATE SCHEMA IF NOT EXISTS {quote(schema)};\n")
    for file, (schema, table) in TABLES.items():
        with open(DATA / file, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        header, body = rows[0], rows[1:]
        columns = list(zip(*body)) if body else [[] for _ in header]
        types = [column_type(name, list(col)) for name, col in zip(header, columns)]
        key = None
        for candidate in KEYS[table]:
            idx = [header.index(c) for c in candidate]
            seen = {tuple(r[i] for i in idx) for r in body}
            if len(seen) == len(body) and all(r[i] != "" for r in body for i in idx):
                key = candidate
                break
        qualified = f"{quote(schema)}.{quote(table)}"
        cols = ",\n  ".join(f"{quote(n)} {t}" for n, t in zip(header, types))
        pk = f",\n  PRIMARY KEY ({', '.join(quote(c) for c in key)})" if key else ""
        out.write(f"\nDROP TABLE IF EXISTS {qualified};\n")
        out.write(f"CREATE TABLE {qualified} (\n  {cols}{pk}\n);\n")
        out.write(f"COPY {qualified} ({', '.join(quote(n) for n in header)}) FROM stdin;\n")
        for r in body:
            out.write("\t".join(copy_value(v) for v in r) + "\n")
        out.write("\\.\n")
        print(f"{qualified}: {len(body)} rows, key {key}", file=sys.stderr)
    out.write("\nANALYZE;\n")


if __name__ == "__main__":
    main()
