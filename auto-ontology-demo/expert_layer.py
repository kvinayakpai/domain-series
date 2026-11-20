"""What Season 2's hand-built ontology knows, entered into Auto-Ontology the way an expert would.

Auto-Ontology's draft is meant to be refined by experts. This module takes the Store 014 ontology
(src/data/ontology.json: its things, links, twelve rules and which records look or copy) and adds
it through the tool's own channels for experts:

- organization instructions (the agent's system prompt): what each table is, the joins, and the
  twelve rules word for word, each with what it means for these tables
- a glossary of the codes the tables use
- table descriptions, certified
- calculations (SQL attributes) on the terms the draft made, certified by being entered by hand
- certified analyses: SQL the agent can reuse

    from expert_layer import apply
    record = apply(call)   # call(method, path, body) -> JSON, as in run_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = json.loads((ROOT / "src" / "data" / "ontology.json").read_text())
RULE = {r["n"]: r["text"] for r in ONTOLOGY["rules"]}

# What each rule means for Store 014's tables.
HERE = {
    1: "On-shelf availability is the share of store.shelf_audits rows with status 'on shelf'. Never compute it from store.inventory_book.",
    2: "Days with no sales in store.pos_lines while store.inventory_book shows stock mean the shelf may be empty: check store.shelf_audits.",
    3: "Units sold come from store.pos_lines (or store.daily_sales). If asked how many shoppers left without an item, or for lost sales, do not count goods receipts, shelf audits, forecasts or write-offs as shoppers or sales. Say that no record holds them, and if you estimate them, say how. Give what the records show: the shelf audits that found the item missing, and its sales by day.",
    4: "store.forecasts predict demand. Do not score them against store.daily_sales alone.",
    5: "store.stock_counts.adjustment and warehouse.stock_adjustments need a reason. Mirror-image corrections on lookalike items or across the two buildings are one event.",
    6: "For fresh items, store.write_offs and the shelf audits that found the shelf empty are one decision.",
    7: "Match items on store.products.gtin or sku (pos_lines.gtin_scanned, shipping_notice_lines.gtin), never on a slot, an sscc or the product name.",
    8: "A delivery is done only when the stock is on the shelf: compare warehouse.shipments.arrived_ts, store.goods_receipts and later shelf audits.",
    9: "A payments.pos_payments.till_status of 'failed: no response' is a timeout: not known yet. payments.psp_upi_report.status ('success', 'failed', 'returned') decides.",
    10: "A UPI 'success' in payments.psp_upi_report with no approved payment for its bill at the till is a customer charged twice until proven otherwise.",
    11: "Refund time runs from the extra debit (payments.psp_upi_report.status_ts) to payments.upi_refunds.completed_ts, not from the complaint.",
    12: "Before trusting a number, name the table it reads and a table that could contradict it, such as store.shelf_audits against store.inventory_book.",
}

TABLES = {
    "store.pos_lines": "Till lines: every sale as scanned (sku_scanned, qty, bill_ts). Looks at the world. Sales, not demand.",
    "store.daily_sales": "The till lines totalled per item per day. Sales, not demand.",
    "store.inventory_book": "Book stock: what the system believes is on hand at close. It copies other records (the last count, plus receipts, minus sales and write-offs) and never looks at the shelf.",
    "store.shelf_audits": "Staff looking at the shelf at 11:00, twice a week: status 'on shelf' or 'empty'. The only record of what was on the shelf.",
    "store.stock_counts": "Physical counts of the stock, and the corrections they made to the book. Looks at the world.",
    "store.goods_receipts": "Pallets received from the warehouse, as booked. Deliveries into the store, not sales. Copies the shipping notice.",
    "store.forecasts": "The nightly forecast of demand, and the order it made, for each warehouse item. Not sales.",
    "store.write_offs": "Stock thrown away or written off, with a reason.",
    "store.store_orders": "Orders the store sent to the warehouse.",
    "store.fresh_deliveries": "Milk, curd and bread delivered each morning by the dairy and bakery routes.",
    "warehouse.pick_confirmations": "The warehouse's pick confirmations for the store's orders.",
    "warehouse.shipping_notice_lines": "What each shipping notice said was on each pallet. Copies the picks.",
    "warehouse.pallets": "One row per pallet label (sscc). Copies the shipping notice.",
    "warehouse.shipments": "Trucks: dispatch, delivery slot and arrival.",
    "warehouse.stock_adjustments": "Corrections the warehouse made to its stock of the store's lines.",
    "payments.pos_payments": "The till's view of each payment attempt: till_status, and the rrn when the till got one.",
    "payments.psp_upi_report": "UPI's report: each UPI payment's final status and when it was known. Looks at the world.",
    "payments.upi_settlements": "The acquirer's daily UPI settlement. Copies UPI's report.",
    "payments.upi_refunds": "Refunds the store made for UPI payments.",
    "payments.customer_complaints": "Customer complaints about payments.",
}

JOINS = [
    "every sku column (sku, sku_scanned, asn_sku, sku_booked) = store.products.sku",
    "store.pos_lines.bill_id = payments.pos_payments.bill_id",
    "payments.pos_payments.rrn = payments.psp_upi_report.rrn",
    "payments.psp_upi_report.bill_ref = payments.pos_payments.bill_id, when bill_ref is set",
    "payments.upi_refunds.rrn = payments.psp_upi_report.rrn",
    "store.goods_receipts.sscc = warehouse.pallets.sscc",
    "store.goods_receipts.shipment_id = warehouse.shipments.shipment_id",
    "warehouse.shipping_notice_lines.sscc = warehouse.pallets.sscc",
    "warehouse.pick_confirmations.order_id = store.store_orders.order_id",
]

GLOSSARY = {
    "OSA": "On-shelf availability: the share of shelf audits that found the item on the shelf.",
    "SKU": "The store's item code, store.products.sku.",
    "GTIN": "The barcode number on the pack.",
    "SSCC": "The number on a pallet label.",
    "RRN": "UPI's reference number for one payment.",
    "UPI": "India's instant payment system. payments.psp_upi_report is its report.",
    "ASN": "Advance shipping notice: warehouse.shipping_notice_lines.",
    "GRN": "Goods receipt note: store.goods_receipts.",
}

# Calculations, each put on the draft's main term for its table.
CALCULATIONS = [
    {
        "table": "store.pos_lines",
        "prefer": ["line", "sale", "bill"],
        "name": "Units sold (till lines)",
        "description": "Units the till sold, as scanned. Filter by sku_scanned and bill_ts. This is sales, not demand (rule 3).",
        "expression": "SELECT SUM(qty) FROM store.pos_lines",
    },
    {
        "table": "store.shelf_audits",
        "prefer": ["audit"],
        "name": "On-shelf availability (shelf audits)",
        "description": "The share of shelf audits that found the item on the shelf. Rule 1: available means on the shelf.",
        "expression": "SELECT AVG(CASE WHEN status = 'on shelf' THEN 1.0 ELSE 0.0 END) FROM store.shelf_audits",
    },
    {
        "table": "store.inventory_book",
        "prefer": ["hand", "inventory", "stock"],
        "name": "Book stock at close (a belief)",
        "description": "What the system believes was on hand at close: the last count, plus receipts, minus sales and write-offs. Not the shelf (rule 1).",
        "expression": "SELECT SUM(book_on_hand_close) FROM store.inventory_book",
    },
    {
        "table": "store.goods_receipts",
        "prefer": ["receipt", "line"],
        "name": "Units received (goods receipts)",
        "description": "Units booked into the store from the warehouse. Deliveries, not sales.",
        "expression": "SELECT SUM(units_booked) FROM store.goods_receipts",
    },
]

ANALYSES = [
    {
        "name": "Units sold by item and month",
        "description": "Sales by item and month, from the till lines. Sales, not demand (rule 3).",
        "sql": "SELECT sku_scanned AS sku, date_trunc('month', bill_ts) AS month, SUM(qty) AS units_sold FROM store.pos_lines GROUP BY sku_scanned, date_trunc('month', bill_ts)",
    },
    {
        "name": "On-shelf availability by item",
        "description": "Rule 1: available means on the shelf. From the shelf audits, never from book stock.",
        "sql": "SELECT sku, COUNT(*) AS audits, SUM(CASE WHEN status = 'on shelf' THEN 1 ELSE 0 END) AS on_shelf, AVG(CASE WHEN status = 'on shelf' THEN 1.0 ELSE 0.0 END) AS on_shelf_availability FROM store.shelf_audits GROUP BY sku",
    },
    {
        "name": "Shelf audits that found an item missing",
        "description": "The evidence the records hold when asked about shoppers who left without an item, or lost sales. These rows are not shoppers: no record holds demand or lost sales (rule 3).",
        "sql": "SELECT audit_ts, sku FROM store.shelf_audits WHERE status = 'empty' ORDER BY audit_ts",
    },
]


def instructions() -> str:
    things = ", ".join(t["name"].lower() for t in ONTOLOGY["things"])
    lines = [
        "STORE 014 ONTOLOGY. Season 2's hand-built ontology of this store. Follow it over table and column names.",
        "",
        f"Its things: {things}. Demand (a customer wants an item) and lost sales (demand that found the shelf empty) are in no table.",
        "",
        "What each table is:",
        *[f"- {table}: {text}" for table, text in TABLES.items()],
        "",
        "Joins:",
        *[f"- {join}" for join in JOINS],
        "",
        "Rules, each with what it means here:",
    ]
    for n in sorted(RULE):
        lines.append(f"{n}. {RULE[n]}")
        lines.append(f"   Here: {HERE[n]}")
    return "\n".join(lines)


def _err(error: Exception) -> str:
    body = ""
    if hasattr(error, "read"):
        try:
            body = " " + error.read().decode()[:500]
        except Exception:
            pass
    return f"{type(error).__name__}: {error}{body}"


def _main_term(terms_by_table: dict[str, list[dict]], table: str, prefer: list[str]) -> dict | None:
    candidates = terms_by_table.get(table) or []
    for word in prefer:
        for term in candidates:
            if word in (term.get("name") or "").lower():
                return term
    return candidates[0] if candidates else None


def apply(call, terms: list[dict], details: dict) -> dict:
    """Enter the knowledge through the API. Returns what was done and what was refused."""
    record: dict = {"instructions_chars": 0, "glossary": [], "tables": {}, "calculations": [], "analyses": []}

    text = instructions()
    try:
        call("POST", "/api/custom-prompts", {"content": text})
        record["instructions_chars"] = len(text)
    except Exception as error:
        record["instructions_error"] = _err(error)

    for name, description in GLOSSARY.items():
        try:
            call("POST", "/api/acronyms", {"name": name, "description": description})
            record["glossary"].append(name)
        except Exception as error:
            record.setdefault("glossary_errors", {})[name] = _err(error)

    # Table descriptions, certified.
    try:
        dbs = (call("GET", "/api/datasources/dbs") or {}).get("data") or []
        db = next(d for d in dbs if d.get("name") == "store014")
        schemas = db.get("schemas") or []
        if not schemas or not isinstance(schemas[0], dict):
            got = call("GET", f"/api/schemas/{db['id']}")
            schemas = got.get("data", got) if isinstance(got, dict) else got
        for schema in schemas or []:
            tables = (call("GET", f"/api/tables/{schema['id']}") or {}).get("data") or []
            for table in tables:
                key = f"{table.get('schema_name') or schema.get('name')}.{table.get('name')}"
                if key in TABLES:
                    try:
                        call("PATCH", f"/api/nodes/{table['id']}", {"description": TABLES[key], "description_certified": True})
                        record["tables"][key] = "certified"
                    except Exception as error:
                        record["tables"][key] = _err(error)
    except Exception as error:
        record["tables_error"] = _err(error)

    # Calculations on the draft's own terms.
    terms_by_table: dict[str, list[dict]] = {}
    for term in terms:
        for table in ((details.get(term["id"]) or {}).get("data") or {}).get("tables") or []:
            terms_by_table.setdefault(f"{table.get('schema_name')}.{table.get('name')}", []).append(term)
    for calc in CALCULATIONS:
        term = _main_term(terms_by_table, calc["table"], calc["prefer"])
        entry = {"name": calc["name"], "table": calc["table"], "term": term and term.get("name")}
        if term:
            try:
                call("POST", "/api/sql-attributes", {
                    "term_id": term["id"], "name": calc["name"], "description": calc["description"],
                    "expression": calc["expression"], "source": "manual",
                })
                entry["status"] = "added"
            except Exception as error:
                entry["status"] = _err(error)
        else:
            entry["status"] = "no term for this table"
        record["calculations"].append(entry)

    for analysis in ANALYSES:
        entry = {"name": analysis["name"]}
        try:
            call("POST", "/api/custom-analyses", analysis)
            entry["status"] = "added"
        except Exception as error:
            entry["status"] = _err(error)
        record["analyses"].append(entry)
    return record


if __name__ == "__main__":
    print(instructions())
