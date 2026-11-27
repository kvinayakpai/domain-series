"""Capability registry for Store 014: what the records cover and which business terms they can and cannot define.

Coverage is read from the CSV files (not typed in). Terms are written from the schema and the hand pack
(refusal-bench/packs), not from any question list. Statuses:
  not_recorded  nothing in the records defines it: any question that needs it is 'no record'
  proxy         only a stand-in exists: answer as a labelled proxy or 'no record', never as the answer
Gap kinds: who, not_happen, why, else, how_long.
"""
import csv
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "public" / "data" / "india-grocery"
DATE_COLS = {"pos-lines-may-june.csv": "bill_ts", "pos-payments-june.csv": "ts", "psp-upi-report-june.csv": "initiated_ts",
             "daily-sales-june.csv": "date", "write-offs-june.csv": "date", "upi-refunds-june.csv": "requested_ts",
             "upi-settlements-june.csv": "settlement_date", "shipments-june.csv": "dispatched_ts", "stock-counts-june.csv": "count_ts",
             "shelf-audits-june.csv": "audit_ts", "customer-complaints-june.csv": "complaint_ts", "fresh-deliveries-june.csv": "delivery_ts",
             "goods-receipts-june.csv": "received_ts", "store-orders-june.csv": "created_ts", "forecasts-june.csv": "date"}


def coverage():
    out = {}
    for f, col in DATE_COLS.items():
        vals = sorted(r[col][:10] for r in csv.DictReader(open(DATA / f)) if r[col])
        out[f] = [vals[0], vals[-1]]
    return out


# Columns that could identify a person. None of the 21 tables has one: bill ids, rrn (a bank reference per transaction),
# vehicle and slot codes identify things, not people.
PERSON_COLUMNS = []

TERMS = [
    # who: nobody is identified
    dict(id="person_identity", gap="who", status="not_recorded", note="no table identifies a customer, cashier, supplier, driver or household",
         patterns=[r"\bwho\b", r"\bwhich (customers?|shoppers?|staff|cashiers?|suppliers?|households?|drivers?|delivery drivers?|segments?)\b",
                   r"\b(different|distinct|unique) (customers|shoppers|people)\b", r"\b(repeat (rate|customers)|churn|lifetime value|age and gender|best customers)\b",
                   r"\bhouseholds?\b", r"\b(cashier|staff member|delivery driver|supplier'?s?)\b", r"\bbuy .* every week\b", r"\bmore than once\b.*\b(shoppers?|customers?)\b",
                   r"\b(shoppers?|customers?) .* more than once\b", r"\bapproved\b.*\bwrite-?offs\b"]),
    dict(id="shopper_count", gap="who", status="proxy", note="a bill is not a shopper: bills are the nearest stand-in",
         patterns=[r"\bhow many (shoppers|customers|people)\b(?! complaints)"]),
    # why: no reason or cause codes
    dict(id="cause", gap="why", status="not_recorded", note="no table records the reason or cause of an event",
         patterns=[r"^\s*why\b", r"\bwhat caused\b", r"\b(main|real|root) reason\b", r"\bcause of\b", r"\bwhat inside the till\b", r"\bbecause of\b", r"\bwhat explains\b"]),
    # what did not happen
    dict(id="absent_event", gap="not_happen", status="not_recorded", note="nothing records a shopper who did not buy, a product not on the shelf, a payment not retried",
         patterns=[r"\babandon", r"\bvoid", r"\bcancel", r"\brefus(ed|al)\b", r"\bwalked out\b", r"\bleft (the )?(store|shop)?\s*without\b", r"\bleft without\b", r"\bwithout (buying|a bill|paying)\b",
                   r"\bput (it |them )?back\b", r"\bwould have been\b", r"\btrue demand\b", r"\blost sales?\b", r"\bnever\b", r"\bnot done\b", r"\bnot accept", r"\bwere told there\b",
                   r"\bentered .* and left\b", r"\bgave up\b", r"\bsubstitut", r"\bremov\w*\b.*\bfrom a bill\b", r"\bbefore an item was scanned\b", r"\bstockouts? cost\b",
                   r"\basked (a staff member )?for\b", r"\btried to pay\b", r"\bscheduled .* (were )?not\b", r"\bconversion\b", r"\bfootfall\b", r"\b(people|shoppers) visited\b", r"\bvisitors\b",
                   r"\bpicked up\b", r"\bqueue\b", r"\bunpaid\b", r"\bleft\b"]),
    # what else: outside the records
    dict(id="external", gap="else", status="not_recorded", note="nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products",
         patterns=[r"\bcompetitors?\b", r"\b(weather|rainfall|rain|temperature)\b", r"\b(rent|staff costs?|electricity)\b", r"\bfestival\b", r"\bmarket share\b", r"\bsatisf",
                   r"\belasticity\b", r"\bother stores?\b", r"\bwholesale price\b", r"\b(by car|by bike|on foot)\b", r"\b(home-delivery|online) orders?\b", r"\bprefer\b", r"\bprofitable\b",
                   r"\bmaximi[sz]e profit\b", r"\bworking capital\b", r"\bpayment terms\b", r"\bper square foot\b", r"\badd to or drop\b", r"\bcheap or expensive\b", r"\bpromotion\b", r"\bdiscount\b",
                   r"\bhow should\b", r"\bshould store\b", r"\bmark(ed)? ?down\b", r"\bcategory\b.*\bdoing\b", r"\bnew product\b", r"\bheld for other stores\b", r"\bfor other stores\b",
                   r"\bhow much should\b", r"\bstolen\b", r"\btheft\b"]),
    dict(id="list_margin", gap="else", status="proxy", note="selling price minus the single cost per product is a list margin, not a real margin",
         patterns=[r"\bgross margin\b", r"\bmargin\b"]),
    dict(id="basket_value", gap="who", status="proxy", note="a bill's total is what one checkout cost: a stand-in for what a shopper spent, since no table links bills to a shopper",
         patterns=[r"\b(average|mean|typical)\b.*\b(bill|basket)\b.*\b(value|size|amount)\b", r"\b(bill|basket) (value|size)\b"]),
    dict(id="shelf_hours", gap="not_happen", status="proxy", note="shelf audits are 11:00 snapshots twice a week, not hours off the shelf",
         patterns=[r"\bhours\b.*\boff the shelf\b", r"\bat 3 pm\b", r"\bshelf look empty\b", r"\bon the shelf at\b"]),
    dict(id="forecast_vs_demand", gap="not_happen", status="not_recorded", note="a forecast can only be scored against recorded sales, not demand",
         patterns=[r"\bforecast\b.*\b(accura|real|true|against)", r"\baccurate\b.*\bforecast\b"]),
    dict(id="bank_side", gap="who", status="not_recorded", note="the customer's bank side of a payment is not in the records",
         patterns=[r"\bbank statement\b", r"\bcustomer's bank\b", r"\bbank'?s? (view|side)\b"]),
    dict(id="restock_times", gap="not_happen", status="not_recorded", note="restock time on the shelf is not recorded (only receipts at the back door)",
         patterns=[r"\brestock", r"\bshelf was (restocked|empty for)\b"]),
]
# Certified measures: the only things the records answer exactly. A question passes only if it asks for a count, total, average or
# price (intent) of a thing these tables hold (entity). Anything else is 'no record': the list of what is NOT recorded is open-ended,
# the list of what IS recorded is the 21 tables. Nouns come from the table and column names in the schema.
INTENT = [r"\bhow many\b", r"\bwhat (was|is|were) the (total|average|number|selling price|revenue|highest|lowest)\b", r"\bwhat is the selling price\b",
          r"\bon how many (different )?days\b", r"\bhow much (revenue|money)\b", r"\bhow much .* (sell|sold|revenue)\b", r"\bwhat (was|is|were) the (biggest|largest|smallest|highest|lowest|maximum|minimum)\b"]
ENTITIES = {
    "pos_lines / pos_payments": [r"\bbills?\b", r"\bpayment attempts?\b", r"\bapproved\b.*\battempts?\b", r"\bupi payment attempt\b", r"\bcard payment attempts?\b"],
    "psp_upi_report": [r"\btransactions? in the upi service provider'?s? report\b", r"\bupi service provider'?s? report\b"],
    "upi_refunds": [r"\bupi refunds?\b"], "upi_settlements": [r"\bsettled\b", r"\bsettlements?\b", r"\bnet upi amount\b"],
    "customer_complaints": [r"\bcomplaints?\b(?! .*\bwho\b)"], "write_offs": [r"\bwrite-?off", r"\bwritten off\b"],
    "shipments / pallets / goods_receipts": [r"\bshipments?\b", r"\bpallets?\b", r"\bgoods-receipt lines?\b"],
    "shelf_audits": [r"\bshelf-audit rows?\b", r"\bshelf audits?\b"], "stock_counts": [r"\bstock counts?\b"],
    "store_orders": [r"\bstore orders?\b", r"\bunits in total did store 014 order\b", r"\border from the warehouse\b"],
    "products": [r"\bhow many products\b", r"\bselling price\b", r"\bproducts? .* price\b"],
    "daily_sales": [r"\bunits? (of .* )?(were )?sold\b", r"\bbags? of\b.*\bsold\b", r"\brevenue\b.*\b(atta|milk|rice|oil|dal|sugar|bread|curd)\b", r"\bsell (more|zero)\b", r"\bsold\b", r"\bsell\b"],
    "fresh_deliveries": [r"\bfresh-delivery rows?\b", r"\bfresh deliver"],
    "shipping_notice_lines": [r"\bshipping notices?\b"], "forecasts": [r"\bforecast rows?\b"],
}
# till lines (bills, sales, revenue) run 4 May to 28 June; every other table is June only
TILL_PATTERNS = [r"\bbills?\b", r"\bsales\b", r"\brevenue\b", r"\baverage bill\b", r"\bbasket\b"]


def build():
    return {"coverage": coverage(), "person_columns": PERSON_COLUMNS, "terms": TERMS, "till_patterns": TILL_PATTERNS,
            "intent": INTENT, "entities": ENTITIES, "till_window": ["2026-05-04", "2026-06-28"], "other_window": ["2026-06-01", "2026-06-30"]}


if __name__ == "__main__":
    reg = build()
    (Path(__file__).parent / "registry.json").write_text(json.dumps(reg, indent=1))
    print({k: (len(v) if hasattr(v, "__len__") else v) for k, v in reg.items()})
