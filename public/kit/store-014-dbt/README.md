# Store 014 in dbt

The data tests and the domain tests from the series *Why Domain Matters*
(https://kvinayakpai.github.io/domain-series/), as a dbt project on DuckDB. It reads the
series' records of one month at Store 014, a fictional Bengaluru supermarket in a synthetic
world, as CSV files.

## Run it

```
pip install dbt-duckdb
python get_data.py          # skip if ./data is already there
dbt build --profiles-dir .
```

`dbt build` creates one view per record in `models/records`, the views the domain tests use in
`models/domain`, and runs two sets of tests:

- `tests/pipeline`: the 32 data tests from the technical companions. Keys, values and
  reconciliations. They pass, except one: the full-cream milk book goes below zero on six days,
  from the till's scan errors. It is set to warn.
- `tests/domain`: 13 tests about how a store, a warehouse and UPI work. They fail on
  June's records, as warnings, and store their failing rows: each is one of June's failures,
  found from the records alone.

Then `dbt show --select join_agreement` lists the twelve joins between the records and how often
each pair agrees: eight always agree, because one record is written from the other.

## The domain tests

The shelf:
- `no_silence_with_stock_on_the_books`: No item goes longer without a sale than its usual rate allows while the books show stock
- `no_audit_finds_empty_with_stock`: No shelf audit finds an item empty while the books show stock
- `counts_agree_with_the_books_within_2pct`: Stock counts agree with the books within 2%
- `no_weekly_sales_halve`: No warehouse item's weekly sales halve from one week to the next

The truck:
- `no_mirror_pair_in_one_building`: No count correction has a mirror image in the same building
- `no_warehouse_correction_mirrored_at_the_store`: No warehouse correction is mirrored at the store
- `every_receipt_survives_the_next_count`: Every receipt survives the next count
- `something_checks_each_pallet`: Something other than the pick checks what is on each pallet (a scale weight or a case scan)

The money:
- `every_provider_success_has_an_approved_payment`: Every success in the provider's report has an approved till payment with its RRN
- `every_upi_attempt_joins_by_rrn`: Every UPI attempt at the till joins the provider's final status by RRN
- `no_bill_paid_twice`: No bill is paid twice, once timed-out attempts are matched to the provider's report
- `extra_charges_back_within_5_days`: Every extra charge comes back within 5 days of the debit (refunds as of the review, 29 June 09:00)
- `no_burst_of_timeouts`: No hour has three or more timeouts and a timeout share over 10 times the month's

Each record's model carries what writes it and what it looks at in the world, from the
series' map of the records (`store-014-map.json`), in its description and `meta`.
