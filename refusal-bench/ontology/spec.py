"""Source of truth for the data-bound layer of the Store 014 ontology. Written from the schema (CSV headers), the hand pack and the
12 rules, NOT from any benchmark question list. build_bindings.py turns it into public/data/ontology/store-014-data.ttl and
checks every claim in it against the CSV files (columns exist, every code value occurs, coverage dates are read from the data).

Per table:  noun cue-sets (a question is about this table when ALL tokens of one cue-set are present), grain, key, date column,
            kind (observes = looks at the world, copies = derived from another record: rule 12), and its columns.
Per column: kind  id | time | code | number | text ; for numbers: unit and whether summing makes sense (additive).
"""

# measures are numeric columns that a question can total, average or rank. cues: alternative token sets, any one may match.
# agg: default aggregate when a question says "how many"/"total" (sum for additive amounts).
T = {}


def table(stem, label, nouns, grain, key, date, kind, columns, sku=None, window="june", distinct=None, record=None, default=None):
    T[stem] = dict(default=default, stem=stem, label=label, nouns=nouns, grain=grain, key=key, date=date, kind=kind, columns=columns, sku=sku, window=window,
                   distinct=distinct, record=record)


C = dict  # column spec shorthand

table("pos-lines-may-june", "till line", [["till", "lines"], ["bill", "lines"]], "one product line on a bill, for the eleven followed items only (a bill's other items are not in this table)", "bill_id", "bill_ts", "observes",
      dict(bill_id=C(kind="id"), bill_ts=C(kind="time"), line=C(kind="id"), gtin_scanned=C(kind="id"), sku_scanned=C(kind="id"),
           qty=C(kind="number", unit="units", additive=True, cues=[["items", "scanned"]]),
           unit_price=C(kind="number", unit="rupees", additive=False),
           line_amount=C(kind="number", unit="rupees", additive=True, cues=[["bill", "amount"]])),
      sku="sku_scanned", window="till", record="till-lines", default="line_amount")
table("pos-payments-june", "payment attempt", [["payment", "attempts"], ["payment", "attempt"]], "one try to pay a bill, by one tender", "bill_id", "ts", "observes",
      dict(bill_id=C(kind="id"), attempt=C(kind="id"), ts=C(kind="time"), tender=C(kind="code"), amount_inr=C(kind="number", unit="rupees", additive=True, cues=[["amount"]]),
           till_status=C(kind="code"), rrn=C(kind="id"), note=C(kind="text")), record="till-payments", default="amount_inr")
table("psp-upi-report-june", "UPI service provider's transaction", [["transaction", "upi", "provider's", "report"], ["transaction", "upi", "report"], ["upi", "provider's", "report"], ["upi", "provider", "report"], ["upi", "providers", "report"], ["service", "provider's", "report"]],
      "one UPI transaction as the payment provider saw it", "rrn", "initiated_ts", "observes",
      dict(rrn=C(kind="id"), initiated_ts=C(kind="time"), amount_inr=C(kind="number", unit="rupees", additive=True), status=C(kind="code"), status_ts=C(kind="time"), bill_ref=C(kind="id")),
      record="upi-report", default="amount_inr")
table("daily-sales-june", "daily sales row", [["daily", "sales"]], "units and revenue of one product on one day", None, "date", "copies",
      dict(date=C(kind="time"), sku=C(kind="id"), units_sold=C(kind="number", unit="units", additive=True, cues=[["daily", "units", "sold"], ["units", "sold"], ["bags", "sold"], ["units", "sell"], ["bags", "sell"], ["units", "were", "sold"]]),
           revenue_inr=C(kind="number", unit="rupees", additive=True, cues=[["daily", "revenue"], ["revenue"], ["sell", "rupees"], ["sold", "rupees"]])), sku="sku", window="till", record="till-lines")
table("write-offs-june", "write-off", [["write", "off"], ["write-off", "lines"], ["writeoff", "lines"], ["write-offs"], ["write-off"], ["written", "off"]], "one product written off on one day", None, "date", "observes",
      dict(date=C(kind="time"), sku=C(kind="id"), units=C(kind="number", unit="units", additive=True, cues=[["units", "written", "off"], ["units", "write-offs"], ["units", "write-off"]]), reason=C(kind="code")), sku="sku")
table("upi-refunds-june", "UPI refund", [["upi", "refunds"], ["upi", "refund"]], "one refund sent back to a customer's bank", "refund_id", "requested_ts", "observes",
      dict(refund_id=C(kind="id"), rrn=C(kind="id"), bill_id=C(kind="id"), amount_inr=C(kind="number", unit="rupees", additive=True, cues=[["amount"]]), trigger=C(kind="code"),
           requested_ts=C(kind="time"), completed_ts=C(kind="time")), record="settlements", default="amount_inr")
table("upi-settlements-june", "UPI settlement", [["upi", "settlements"], ["upi", "settlement"], ["upi", "amount", "settled"], ["upi", "settled"]], "one day's UPI money credited to the store", "settlement_date", "settlement_date", "copies",
      dict(settlement_date=C(kind="time"), upi_credits=C(kind="number", unit="credits", additive=True), gross_inr=C(kind="number", unit="rupees", additive=True, cues=[["gross"]]),
           refunds_inr=C(kind="number", unit="rupees", additive=True), mdr_inr=C(kind="number", unit="rupees", additive=True, cues=[["mdr"]]),
           net_inr=C(kind="number", unit="rupees", additive=True, cues=[["net", "upi", "amount"], ["net"]])), record="settlements", default="net_inr")
table("shipments-june", "shipment", [["shipments"], ["shipment"], ["trucks"], ["truck"]], "one truck from the warehouse (DC)", "shipment_id", "dispatched_ts", "observes",
      dict(shipment_id=C(kind="id"), vehicle=C(kind="id"), dispatched_ts=C(kind="time"), slot_start=C(kind="time"), slot_end=C(kind="time"), arrived_ts=C(kind="time"),
           pallets=C(kind="number", unit="pallets", additive=True, cues=[["pallets"]])))
table("stock-counts-june", "stock count", [["stock", "counts"], ["stock", "count"]], "one product counted by hand", None, "count_ts", "observes",
      dict(count_ts=C(kind="time"), sku=C(kind="id"), book_before=C(kind="number", unit="packs", additive=False), counted=C(kind="number", unit="packs", additive=False),
           adjustment=C(kind="number", unit="packs", additive=True), trigger=C(kind="code")), sku="sku", record="stock-counts")
table("shelf-audits-june", "shelf-audit row", [["shelf-audit", "rows"], ["shelf", "audit", "rows"], ["shelf-audit", "row"], ["shelf", "audits"]], "one product seen or not seen at an 11:00 audit", None, "audit_ts", "observes",
      dict(audit_ts=C(kind="time"), sku=C(kind="id"), status=C(kind="code")), sku="sku", record="shelf-audits")
table("customer-complaints-june", "complaint", [["complaints", "about", "payments"], ["customer", "complaints", "about", "payments"], ["complaints"], ["complaint"], ["customer", "complaints"]], "one complaint about a debit", None, "complaint_ts", "observes",
      dict(complaint_ts=C(kind="time"), kind=C(kind="code"), amount_inr=C(kind="number", unit="rupees", additive=True), bill_id=C(kind="id"), rrn=C(kind="id"),
           resolved_ts=C(kind="time"), resolution=C(kind="code")), default="amount_inr")
table("fresh-deliveries-june", "fresh-delivery row", [["fresh-delivery", "rows"], ["fresh", "delivery", "rows"], ["fresh-delivery", "row"], ["fresh", "deliveries"]], "one product on one fresh route delivery", None, "delivery_ts", "observes",
      dict(delivery_ts=C(kind="time"), route=C(kind="code"), sku=C(kind="id"), units=C(kind="number", unit="units", additive=True, cues=[["units", "delivered"], ["units"]]),
           crates=C(kind="number", unit="crates", additive=True, cues=[["crates", "delivered"], ["crates"]]), use_by=C(kind="time")), sku="sku")
table("goods-receipts-june", "goods-receipt line", [["goods-receipt", "lines"], ["goods-receipt", "line"], ["goods", "receipt", "lines"]], "one pallet line received at the back door", "grn_id", "received_ts", "observes",
      dict(grn_id=C(kind="id"), shipment_id=C(kind="id"), sscc=C(kind="id"), line=C(kind="id"), received_ts=C(kind="time"), asn_sku=C(kind="id"),
           asn_units=C(kind="number", unit="units", additive=True), sku_booked=C(kind="id"), units_booked=C(kind="number", unit="units", additive=True, cues=[["units", "booked"], ["units", "received"]]),
           receipt_method=C(kind="code")), sku="sku_booked", record="goods-receipts")
table("store-orders-june", "store order line", [["store", "order", "lines"], ["store", "order", "line"], ["order", "lines"]], "one product on an order to the warehouse (DC)", "order_id", "created_ts", "observes",
      dict(order_id=C(kind="id"), sku=C(kind="id"), units=C(kind="number", unit="units", additive=True, cues=[["units", "order"], ["units", "ordered"], ["units", "in", "total", "order"]]),
           cases=C(kind="number", unit="cases", additive=True, cues=[["cases", "order"], ["cases", "ordered"]]), created_ts=C(kind="time"), reason=C(kind="code")), sku="sku",
      distinct=dict(label="store order", nouns=[["store", "orders"], ["store", "order"]], column="order_id"))
table("forecasts-june", "forecast row", [["forecast", "rows"], ["forecast", "row"], ["forecasts"]], "one product's forecast for one day", None, "date", "copies",
      dict(date=C(kind="time"), sku=C(kind="id"), forecast_units_per_day=C(kind="number", unit="units", additive=True), sigma=C(kind="number", unit="units", additive=False),
           reorder_point=C(kind="number", unit="units", additive=False), order_up_to=C(kind="number", unit="units", additive=False), book_on_hand=C(kind="number", unit="units", additive=False),
           on_order=C(kind="number", unit="units", additive=False), ordered_units=C(kind="number", unit="units", additive=True), method=C(kind="code")), sku="sku", record="forecasts")
table("pallets-june", "pallet", [["pallets"], ["pallet"]], "one pallet with its label", "sscc", None, "copies",
      dict(sscc=C(kind="id"), shipment_id=C(kind="id"), cases=C(kind="number", unit="cases", additive=True, cues=[["cases"]]), notice_kg=C(kind="number", unit="kg", additive=True, cues=[["kg"], ["kilos"]]),
           weight_check=C(kind="code")), record="pallet-labels")
table("shipping-notice-lines-june", "shipping-notice line", [["shipping", "notice", "lines"], ["shipping", "notices"], ["shipping", "notice"]], "one product line on a shipping notice", None, None, "copies",
      dict(shipment_id=C(kind="id"), sscc=C(kind="id"), line=C(kind="id"), order_id=C(kind="id"), sku=C(kind="id"), gtin=C(kind="id"),
           cases=C(kind="number", unit="cases", additive=True, cues=[["cases"]]), units=C(kind="number", unit="units", additive=True, cues=[["units"]])), sku="sku", record="shipping-notice")
table("dc-pick-confirmations-june", "pick confirmation", [["pick", "confirmations"], ["pick", "confirmation"], ["pick", "lines"]], "one product line confirmed by a picker", None, "pick_ts", "observes",
      dict(pick_ts=C(kind="time"), order_id=C(kind="id"), shipment_id=C(kind="id"), line=C(kind="id"), sku=C(kind="id"), slot=C(kind="id"),
           cases_ordered=C(kind="number", unit="cases", additive=True, cues=[["cases", "ordered"]]), cases_confirmed=C(kind="number", unit="cases", additive=True, cues=[["cases", "confirmed"]]),
           confirmed_by=C(kind="code")), sku="sku", record="pick-confirmations")
table("dc-stock-adjustments-june", "warehouse (DC) stock adjustment", [["warehouse", "stock", "adjustments"], ["warehouse", "adjustments"], ["dc", "stock", "adjustments"]], "one correction to warehouse (DC) stock", None, "adjusted_ts", "observes",
      dict(adjusted_ts=C(kind="time"), sku=C(kind="id"), slot=C(kind="id"), cases=C(kind="number", unit="cases", additive=True), units=C(kind="number", unit="units", additive=True),
           value_at_cost_inr=C(kind="number", unit="rupees", additive=True), reason=C(kind="code")), sku="sku")
table("inventory-book-june", "book-stock row", [["book", "stock", "rows"], ["book-stock", "rows"], ["book", "stock"]], "one product's closing book stock for a day", None, "date", "copies",
      dict(date=C(kind="time"), sku=C(kind="id"), book_on_hand_close=C(kind="number", unit="packs", additive=False)), sku="sku", record="book-stock")
table("products", "product", [["products"], ["product"]], "one product sold in the store", "sku", None, "observes",
      dict(sku=C(kind="id"), gtin=C(kind="id"), name=C(kind="text"), pack=C(kind="text"), case_units=C(kind="number", unit="units", additive=False),
           case_kg=C(kind="number", unit="kg", additive=False), flow=C(kind="code"), dc_slot=C(kind="id"),
           price_inr=C(kind="number", unit="rupees", additive=False, cues=[["selling", "price"], ["price"]]), cost_inr=C(kind="number", unit="rupees", additive=False, cues=[["cost"]])), sku="sku", window="none", default="price_inr")

# A bill is a distinct bill_id on the till lines (rule: one checkout, its lines and total).
BILL = dict(label="bill", nouns=[["bills"], ["bill"]], table="pos-lines-may-june", column="bill_id")

# synonyms for code values: (table, column, value) -> phrases a question may use. The value itself is always a phrase.
VALUE_ALT = {
    ("pos-payments-june", "tender", "UPI"): ["upi"],
    ("customer-complaints-june", "kind", "debited but the till said failed"): ["debit while the till said failed", "debited while the till said failed", "debit but the till said failed",
                                                                              "debited when the till said failed", "debited but till said failed"],
    ("customer-complaints-june", "kind", "charged twice"): ["being charged twice", "double debit", "double charge", "debited twice", "charged two times"],
    ("upi-refunds-june", "trigger", "customer complaint"): ["complaint"],
    ("shelf-audits-june", "status", "on shelf"): ["on the shelf", "on-shelf", "present"],
    ("stock-counts-june", "trigger", "scheduled full count"): ["scheduled count", "scheduled full counts", "scheduled"],
    ("stock-counts-june", "trigger", "manager request after complaints"): ["manager's request after complaints", "managers request after complaints", "requested by the manager after complaints"],
    ("psp-upi-report-june", "status", "success"): ["successful", "succeeded"],
}

# words that only join a question together and carry no business meaning
GLUE = """a an the of in on at to for from by with and or is are was were be been do does did done has have had it its this that these those there their they them we you your
i my me our what which how many much store 014 s t than then as per each every any all some into over about up out between during while when where
rupees rupee inr warehouse dc total number count counts sum average mean highest lowest biggest largest smallest maximum minimum single most least days day
rung ring made make log logged recorded record recorded receive received arrive arrived show shows showed were being get got give gave sent send include included
tills till records these row rows line lines different distinct unique amount amounts""".split()

# aggregate cues (token sets) -> function
AGG = {
    "count": [["how", "many"], ["number", "of"], ["count"], ["how", "much"]],
    "sum": [["total"], ["sum"], ["altogether"], ["in", "total"]],
    "avg": [["average"], ["mean"], ["typical"]],
    "max": [["highest"], ["largest"], ["biggest"], ["maximum"], ["most"], ["peak"]],
    "min": [["lowest"], ["smallest"], ["minimum"], ["least"]],
}
DISTINCT_CUES = [["distinct"], ["different"], ["unique"]]

# things the records cannot define. The question guard's registry terms (who, why, absent event, outside factor, stand-ins) are added
# from registry.TERMS by the builder, so there is one list.

# identifier shapes: a token that looks like one of these names a single record of the column
ID_PATTERNS = {"shipment_id": r"shp-\d{6}", "order_id": r"so-\d{6}", "refund_id": r"rf-\d{6}", "grn_id": r"grn-\d{6}", "bill_id": r"b\d{6}-\d{6}"}
