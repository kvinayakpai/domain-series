"""Fetch Store 014's records into ./data, where the project reads them.

    python get_data.py                 # download them from GitHub
    python get_data.py --from DIR      # or copy them from a folder that has them
"""
import shutil
import sys
import urllib.request
from pathlib import Path

FILES = [
    "customer-complaints-june.csv",
    "daily-sales-june.csv",
    "dc-pick-confirmations-june.csv",
    "dc-stock-adjustments-june.csv",
    "forecasts-june.csv",
    "fresh-deliveries-june.csv",
    "goods-receipts-june.csv",
    "inventory-book-june.csv",
    "pallets-june.csv",
    "pos-lines-may-june.csv",
    "pos-payments-june.csv",
    "products.csv",
    "psp-upi-report-june.csv",
    "shelf-audits-june.csv",
    "shipments-june.csv",
    "shipping-notice-lines-june.csv",
    "stock-counts-june.csv",
    "store-orders-june.csv",
    "upi-refunds-june.csv",
    "upi-settlements-june.csv",
    "write-offs-june.csv"
]
RAW = "https://raw.githubusercontent.com/kvinayakpai/domain-series/main/public/data/india-grocery/"
here = Path(__file__).resolve().parent / "data"
here.mkdir(exist_ok=True)
src = Path(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else None
for f in FILES:
    if src:
        shutil.copy(src / f, here / f)
    else:
        urllib.request.urlretrieve(RAW + f, here / f)
    print("data/" + f)
