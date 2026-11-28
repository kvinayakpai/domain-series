# Store 014 benchmark: the planning panel's answers

## Q001: How many shoppers left Store 014 without buying 5 kg atta in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Shoppers who left without buying are not recorded (absent_event); the stand-in is the number of 11:00 shelf audits in June 2026 that found 5 kg atta empty.)
empty_audits = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report empty_audits = count of *.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]
Stand-ins used (not the real thing): shopper_count (who): a bill is not a shopper: bills are the nearest stand-in

## Q002: What were the lost sales of 5 kg atta in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Lost sales are not recorded (Rule 3); recorded daily units of 5 kg atta in June are the base for an estimate, e.g. normal daily rate times the days the shelf was empty.)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 30.0 | 7950.0
  2026-06-02 | 36.0 | 9540.0
  2026-06-03 | 22.0 | 5830.0
  2026-06-04 | 28.0 | 7420.0
  2026-06-05 | 32.0 | 8480.0
  2026-06-06 | 25.0 | 6625.0
  2026-06-07 | 44.0 | 11660.0
  2026-06-08 | 9.0 | 2385.0
  2026-06-09 | 11.0 | 2915.0
  2026-06-10 | 22.0 | 5830.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf audits of 5 kg atta in June (on-shelf availability) show when the shelf was empty; lost sales themselves are not recorded.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q003: What would June 2026 sales of toned milk 500 ml have been if it had never gone out of stock (true demand)?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Demand is not recorded (Rule 3); recorded daily sales of toned milk 500 ml in June are the base for an estimate of unconstrained sales.)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 265.0 | 6890.0
  2026-06-02 | 395.0 | 10270.0
  2026-06-03 | 313.0 | 8138.0
  2026-06-04 | 224.0 | 5824.0
  2026-06-05 | 292.0 | 7592.0
  2026-06-06 | 340.0 | 8840.0
  2026-06-07 | 265.0 | 6890.0
  2026-06-08 | 289.0 | 7514.0
  2026-06-09 | 389.0 | 10114.0
  2026-06-10 | 280.0 | 7280.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'MILK-TONED-500ML' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf audits of toned milk in June show the stock-out snapshots; sales lost on those days are not recorded and must be estimated.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | on shelf
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | on shelf
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'MILK-TONED-500ML' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q004: When toned milk was empty, what did shoppers buy instead (substitution)?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Days toned milk was seen empty at the 11:00 audit; no record links a shopper to a substitute purchase (absent_event, person_identity).)
No rows matched.
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'MILK-TONED-500ML' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30 and shelf audits.status = 'empty'; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 2: figures from the schema layer. (Plan covers: Daily sales of the other milk pouch (full cream 500 ml) and curd in June, to compare on empty days; substitution by a shopper is not recorded, only these sales.)
56 rows (columns: date, sku, units_sold):
  2026-06-01 | CURD-500G | 112.0
  2026-06-01 | MILK-FC-500ML | 99.0
  2026-06-02 | CURD-500G | 38.0
  2026-06-02 | MILK-FC-500ML | 123.0
  2026-06-03 | CURD-500G | 59.0
  2026-06-03 | MILK-FC-500ML | 81.0
  2026-06-04 | CURD-500G | 88.0
  2026-06-04 | MILK-FC-500ML | 74.0
  2026-06-05 | CURD-500G | 58.0
  2026-06-05 | MILK-FC-500ML | 99.0
  ... and 46 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['MILK-FC-500ML', 'CURD-500G'] and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, sku = daily sales.sku, units_sold = daily sales.units_sold; sorted by date asc, sku asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q005: How many people visited Store 014 each day in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Visitors are not recorded (shopper_count); bills per day in June from approved payments are the nearest stand-in, and a visitor who did not buy is not counted.)
28 rows (columns: day, bills):
  2026-06-01 | 1299
  2026-06-02 | 1089
  2026-06-03 | 997
  2026-06-04 | 974
  2026-06-05 | 978
  2026-06-06 | 1344
  2026-06-07 | 919
  2026-06-08 | 808
  2026-06-09 | 752
  2026-06-10 | 1139
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts); report day = day(pos payments.ts), bills = count distinct of pos payments.bill_id; sorted by day asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]
Stand-ins used (not the real thing): shopper_count (who): a bill is not a shopper: bills are the nearest stand-in

## Q006: How many shoppers abandoned a basket at the till in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Abandoned baskets are not recorded (absent_event); the stand-in is June 2026 payment attempts that were declined or failed, noting every June bill still has one approved payment.)
unsuccessful_attempts = 872; bills_affected = 846
  How it was found: From payment attempt records; keep rows where pos payments.till_status in ['declined', 'failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report unsuccessful_attempts = count of *, bills_affected = count distinct of pos payments.bill_id.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]
Stand-ins used (not the real thing): shopper_count (who): a bill is not a shopper: bills are the nearest stand-in

## Q007: Who are Store 014's best customers by spend in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Customers are not identified (person_identity); the plan lists the highest-value bills in June 2026 as a stand-in (basket_value), not customers.)
10 rows (columns: bill_id, bill_value):
  B260621-140000 | 17558.14
  B260619-140036 | 14543.19
  B260608-090013 | 13677.6
  B260606-000038 | 12886.97
  B260618-110056 | 11136.8
  B260621-070034 | 10215.48
  B260616-130010 | 9809.48
  B260623-100013 | 9500.55
  B260619-120046 | 9292.96
  B260602-100022 | 9211.98
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.bill_id; report bill_id = pos payments.bill_id, bill_value = sum of pos payments.amount_inr; sorted by bill_value desc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q008: How often do Store 014's customers come back (repeat rate and churn)?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q009: Do the same shoppers buy atta, oil and dal together at Store 014?

Answered from the knowledge layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Bills (stand-in for shoppers, no customer identity) whose till lines hold ATTA-WW-5KG, sunflower oil 1 L and toor dal 1 kg together, May-June till lines.)
No rows matched.
  How it was found: From till line records; keep rows where pos lines may.sku_scanned in ['ATTA-WW-5KG', 'OIL-SUN-1L', 'DAL-TOOR-1KG']; group by pos lines may.bill_id; keep groups where items_of_the_three = 3; report bill_id = pos lines may.bill_id, items_of_the_three = count distinct of pos lines may.sku_scanned; sorted by bill_id asc.
Part 2: figures from the schema layer. (Plan covers: Bills (stand-in for shoppers, no customer identity) whose till lines hold ATTA-WW-1KG, sunflower oil 1 L and toor dal 1 kg together, May-June till lines.)
bill_id = B260510-090025; items_of_the_three = 3
  How it was found: From till line records; keep rows where pos lines may.sku_scanned in ['ATTA-WW-1KG', 'OIL-SUN-1L', 'DAL-TOOR-1KG']; group by pos lines may.bill_id; keep groups where items_of_the_three = 3; report bill_id = pos lines may.bill_id, items_of_the_three = count distinct of pos lines may.sku_scanned; sorted by bill_id asc.
Part 3: figures from the schema layer. (Plan covers: Bills (stand-in for shoppers, no customer identity) whose till lines hold ATTA-WW-10KG, sunflower oil 1 L and toor dal 1 kg together, May-June till lines.)
No rows matched.
  How it was found: From till line records; keep rows where pos lines may.sku_scanned in ['ATTA-WW-10KG', 'OIL-SUN-1L', 'DAL-TOOR-1KG']; group by pos lines may.bill_id; keep groups where items_of_the_three = 3; report bill_id = pos lines may.bill_id, items_of_the_three = count distinct of pos lines may.sku_scanned; sorted by bill_id asc.

## Q010: How satisfied are Store 014's customers?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Satisfaction is not recorded; only debit complaints (4 to 26 June 2026) exist as a partial stand-in.)
complaints = 26; first_complaint = 2026-06-04T10:00:00; last_complaint = 2026-06-26T17:00:00
  How it was found: From complaint records; report complaints = count of *, first_complaint = min of customer complaints.complaint_ts, last_complaint = max of customer complaints.complaint_ts.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q011: How is the snacks category doing at Store 014?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: The records hold only the 11 followed products and none is a snacks item, so this lists them to test the category premise; store-wide category sales are not recorded.)
11 rows (columns: sku, name):
  ATTA-WW-10KG | Whole wheat atta 10 kg
  ATTA-WW-1KG | Whole wheat atta 1 kg
  ATTA-WW-5KG | Whole wheat atta 5 kg
  BREAD-WHITE-400G | White bread 400 g
  CURD-500G | Curd 500 g pouch
  DAL-TOOR-1KG | Toor dal 1 kg
  MILK-FC-500ML | Full cream milk 500 ml pouch
  MILK-TONED-500ML | Toned milk 500 ml pouch
  OIL-SUN-1L | Sunflower oil 1 L pouch
  RICE-SM-5KG | Sona masoori rice 5 kg
  ... and 1 more
  How it was found: From product records; report sku = products.sku, name = products.name; sorted by sku asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q012: Did the launch of a new product take sales from an existing one at Store 014?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: No launch date or new-product flag is recorded, so this lists the 11 products to check whether any new one exists; any cause of a sales shift is not recorded.)
11 rows (columns: sku, name):
  ATTA-WW-10KG | Whole wheat atta 10 kg
  ATTA-WW-1KG | Whole wheat atta 1 kg
  ATTA-WW-5KG | Whole wheat atta 5 kg
  BREAD-WHITE-400G | White bread 400 g
  CURD-500G | Curd 500 g pouch
  DAL-TOOR-1KG | Toor dal 1 kg
  MILK-FC-500ML | Full cream milk 500 ml pouch
  MILK-TONED-500ML | Toned milk 500 ml pouch
  OIL-SUN-1L | Sunflower oil 1 L pouch
  RICE-SM-5KG | Sona masoori rice 5 kg
  ... and 1 more
  How it was found: From product records; report sku = products.sku, name = products.name; sorted by sku asc.
Part 2: figures from the schema layer. (Plan covers: June units per product give the sales picture for the 11 followed items only; with no launch date recorded, the month cannot be split before and after a launch.)
11 rows (columns: sku, units):
  ATTA-WW-10KG | 287.0
  ATTA-WW-1KG | 826.0
  ATTA-WW-5KG | 567.0
  BREAD-WHITE-400G | 1674.0
  CURD-500G | 1942.0
  DAL-TOOR-1KG | 539.0
  MILK-FC-500ML | 2916.0
  MILK-TONED-500ML | 8649.0
  OIL-SUN-1L | 747.0
  RICE-SM-5KG | 609.0
  ... and 1 more
  How it was found: From daily sales row records; group by daily sales.sku; report sku = daily sales.sku, units = sum of daily sales.units_sold.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q013: Which products should Store 014 add to or drop from its range?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: A range decision needs demand, shelf space and margin, none of which is recorded; June sales of the 11 followed items are a stand-in.)
11 rows (columns: sku, units, revenue_inr):
  ATTA-WW-10KG | 287.0 | 143213.0
  ATTA-WW-1KG | 826.0 | 47908.0
  ATTA-WW-5KG | 567.0 | 150255.0
  BREAD-WHITE-400G | 1674.0 | 75330.0
  CURD-500G | 1942.0 | 62144.0
  DAL-TOOR-1KG | 539.0 | 90552.0
  MILK-FC-500ML | 2916.0 | 99144.0
  MILK-TONED-500ML | 8649.0 | 224874.0
  OIL-SUN-1L | 747.0 | 113544.0
  RICE-SM-5KG | 609.0 | 212541.0
  ... and 1 more
  How it was found: From daily sales row records; group by daily sales.sku; report sku = daily sales.sku, units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr.
Part 2: figures from the schema layer. (Plan covers: Price minus the single cost per product is a list margin, not a real margin, so this is a proxy and not a basis for a range decision alone.)
11 rows (columns: sku, price_inr, cost_inr):
  ATTA-WW-10KG | 499.0 | 431.0
  ATTA-WW-1KG | 58.0 | 49.5
  ATTA-WW-5KG | 265.0 | 228.0
  BREAD-WHITE-400G | 45.0 | 39.0
  CURD-500G | 32.0 | 29.5
  DAL-TOOR-1KG | 168.0 | 146.0
  MILK-FC-500ML | 34.0 | 32.3
  MILK-TONED-500ML | 26.0 | 24.7
  OIL-SUN-1L | 152.0 | 134.0
  RICE-SM-5KG | 349.0 | 301.0
  ... and 1 more
  How it was found: From product records; report sku = products.sku, price_inr = products.price_inr, cost_inr = products.cost_inr; sorted by sku asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q014: How long do customers queue at the till at Store 014?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q015: What will Store 014's sales be at Diwali 2026?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Diwali demand and festival effects are not recorded and nothing outside these 11 products is held; June revenue of the 11 items is a baseline only, not a Diwali forecast.)
june_revenue_inr = 1243937.0
  How it was found: From daily sales row records; report june_revenue_inr = sum of daily sales.revenue_inr.

## Q016: How many bags of 5 kg atta were sold in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sum of units_sold of 5 kg atta in daily sales for June (data runs 1-28 June).)
units = 567.0; days = 28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold, days = count distinct of daily sales.date.

## Q017: What is the age and gender mix of Store 014's shoppers in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q018: How many shoppers asked a staff member for a product Store 014 does not stock in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q019: Why did sales of toned milk fall on the days they fell in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Daily sales of toned milk in June show the days sales fell; the cause is not recorded (cause).)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 265.0 | 6890.0
  2026-06-02 | 395.0 | 10270.0
  2026-06-03 | 313.0 | 8138.0
  2026-06-04 | 224.0 | 5824.0
  2026-06-05 | 292.0 | 7592.0
  2026-06-06 | 340.0 | 8840.0
  2026-06-07 | 265.0 | 6890.0
  2026-06-08 | 289.0 | 7514.0
  2026-06-09 | 389.0 | 10114.0
  2026-06-10 | 280.0 | 7280.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'MILK-TONED-500ML' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf audits of toned milk in June: an empty shelf is recorded evidence, not a recorded cause.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | on shelf
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | on shelf
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'MILK-TONED-500ML' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 3: figures from the schema layer. (Plan covers: Write-offs of toned milk in June, recorded evidence alongside the sales dips; no record states why sales fell.)
15 rows (columns: date, reason, units):
  2026-06-01 | damaged | 1.0
  2026-06-08 | expired | 4.0
  2026-06-09 | damaged | 1.0
  2026-06-10 | damaged | 1.0
  2026-06-11 | damaged | 1.0
  2026-06-12 | expired | 48.0
  2026-06-13 | expired | 25.0
  2026-06-14 | expired | 42.0
  2026-06-15 | expired | 50.0
  2026-06-16 | expired | 10.0
  ... and 5 more
  How it was found: From write-off records; keep rows where write offs.sku = 'MILK-TONED-500ML' and write offs.date between 2026-06-01 and 2026-06-30; report date = write offs.date, reason = write offs.reason, units = write offs.units; sorted by date asc.
Part 4: figures from the schema layer. (Plan covers: Fresh deliveries of toned milk in June, to set against the low-sales days; the cause itself is not recorded.)
28 rows (columns: delivery_ts, route, units, use_by):
  2026-06-01T05:30 | R-07 | 315.0 | 2026-06-02
  2026-06-02T05:30 | R-07 | 315.0 | 2026-06-03
  2026-06-03T05:30 | R-07 | 315.0 | 2026-06-04
  2026-06-04T05:30 | R-07 | 315.0 | 2026-06-05
  2026-06-05T05:30 | R-07 | 315.0 | 2026-06-06
  2026-06-06T05:30 | R-07 | 338.0 | 2026-06-07
  2026-06-07T05:30 | R-07 | 338.0 | 2026-06-08
  2026-06-08T05:30 | R-07 | 315.0 | 2026-06-09
  2026-06-09T05:30 | R-07 | 315.0 | 2026-06-10
  2026-06-10T05:30 | R-07 | 315.0 | 2026-06-11
  ... and 18 more
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'MILK-TONED-500ML' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report delivery_ts = fresh deliveries.delivery_ts, route = fresh deliveries.route, units = fresh deliveries.units, use_by = fresh deliveries.use_by; sorted by delivery_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q020: How many home-delivery or online orders did Store 014 take in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q021: How did Store 014's daily sales in June 2026 compare with June 2025?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: year outside 2026

## Q022: What were Store 014's total sales in May 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: There are no payments before June, so May store takings are not recorded; this sums May till lines of the eleven followed items only (from 4 May), not the whole store.)
revenue_inr = 1275071.0; units = 19739.0; bills = 13909; first_day = 2026-05-04; last_day = 2026-05-31
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-05-01 and 2026-05-31; report revenue_inr = sum of pos lines may.line_amount, units = sum of pos lines may.qty, bills = count distinct of pos lines may.bill_id, first_day = min of day(pos lines may.bill_ts), last_day = max of day(pos lines may.bill_ts).
Stand-ins used (not the real thing): May is a part month in the till lines (4 May to 28 June)

## Q023: What was the revenue in rupees from 5 kg atta in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sum of revenue_inr of 5 kg atta in daily sales for June (1-28 June).)
revenue_inr = 150255.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report revenue_inr = sum of daily sales.revenue_inr.

## Q024: How many distinct bills were rung up at the tills from 4 May to 31 May 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Distinct bills in till lines 4-31 May; till lines hold only the eleven followed items, so bills without any of them are not counted.)
bills = 13909
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-05-04 and 2026-05-31; report bills = count distinct of pos lines may.bill_id.

## Q025: How many bills were rung up at Store 014 in March 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: march is outside the records

## Q026: What was Store 014's average bill value over May and June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: June average bill value from approved payments (Bills and takings definition: one approved payment per bill).)
avg_bill_inr = 584.1894760115704; bills = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report avg_bill_inr = avg of pos payments.amount_inr, bills = count distinct of pos payments.bill_id.
Part 2: figures from the ontology layer. (Plan covers: May has no payments, so May bill values are not recorded; this is the average per bill of the eleven followed items' till lines (4-31 May), a partial stand-in.)
followed_items_inr_per_bill = 91.67237040764972; bills = 13909
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-05-01 and 2026-05-31; report followed_items_inr_per_bill = sum of pos lines may.line_amount / count distinct of pos lines may.bill_id, bills = count distinct of pos lines may.bill_id.
Stand-ins used (not the real thing): basket_value (who): a bill's total is what one checkout cost: a stand-in for what a shopper spent, since no table links bills to a shopper; May is a part month in the till lines (4 May to 28 June)

## Q027: How many units of all products were sold in June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sum of units_sold in June daily sales; per the Sales definition this covers only the eleven followed items, not the whole store.)
units = 19265.0
  How it was found: From daily sales row records; keep rows where daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold.

## Q028: On how many days in June 2026 did Store 014 sell more than 20 bags of 5 kg atta?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Days in June (1-28) when 5 kg atta units_sold exceeded 20.)
days = 17
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30 and daily sales.units_sold > 20; report days = count distinct of daily sales.date.

## Q029: How many bills did Store 014 ring up on 1 May 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: 1 to 3 May are before the till lines start (4 May)

## Q030: How many bills will Store 014 ring up in July 2026?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: No July records or bill forecast exist; June approved bills are a baseline to start from, not a forecast of July.)
june_bills_baseline = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; report june_bills_baseline = count distinct of pos payments.bill_id.
Not recorded, so not answered: july is outside the records

## Q031: How many bags of 5 kg atta did Store 014 sell per day on average in May and June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: May: 5 kg atta units on till lines (data from 4 May, so 28 days); average per day = units / 28.)
units = 631.0; days_with_sales = 26; first_day = 2026-05-04
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) between 2026-05-01 and 2026-05-31; report units = sum of pos lines may.qty, days_with_sales = count distinct of day(pos lines may.bill_ts), first_day = min of day(pos lines may.bill_ts).
Part 2: figures from the schema layer. (Plan covers: June: average daily units_sold of 5 kg atta in daily sales (1-28 June).)
avg_units_per_day = 20.25; units = 567.0; days = 28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report avg_units_per_day = avg of daily sales.units_sold, units = sum of daily sales.units_sold, days = count distinct of daily sales.date.
Not recorded, so not answered: May is outside this table (June only)

## Q032: How many bills did Store 014 ring up in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June bills counted from approved payments (Bills and takings definition).)
bills = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills = count distinct of pos payments.bill_id.

## Q033: What was the lowest daily revenue in rupees for 1 kg sugar in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Minimum daily revenue of 1 kg sugar in June 2026.)
lowest_daily_revenue_inr = 336.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'SUGAR-1KG' and daily sales.date between 2026-06-01 and 2026-06-30; report lowest_daily_revenue_inr = min of daily sales.revenue_inr.

## Q034: How many units of sugar were sold in June 2026 and why did sales fall in the last week?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Total units of sugar 1 kg sold in June (1-28 June).)
units = 509.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'SUGAR-1KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold.
Part 2: figures from the schema layer. (Plan covers: Daily sugar sales in June, to check the premise that sales fell in the last week; the cause is not recorded (cause).)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 23.0 | 1104.0
  2026-06-02 | 15.0 | 720.0
  2026-06-03 | 21.0 | 1008.0
  2026-06-04 | 31.0 | 1488.0
  2026-06-05 | 19.0 | 912.0
  2026-06-06 | 25.0 | 1200.0
  2026-06-07 | 30.0 | 1440.0
  2026-06-08 | 11.0 | 528.0
  2026-06-09 | 9.0 | 432.0
  2026-06-10 | 20.0 | 960.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'SUGAR-1KG' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 3: figures from the schema layer. (Plan covers: Shelf audits of sugar in June as evidence of an empty shelf; no record states why sales fell.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | empty
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | on shelf
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | on shelf
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'SUGAR-1KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 4: figures from the schema layer. (Plan covers: Closing book stock of sugar in June (a belief, Rule 1) as further evidence; the cause is not recorded.)
28 rows (columns: date, book_on_hand_close):
  2026-06-01 | 21.0
  2026-06-02 | 56.0
  2026-06-03 | 35.0
  2026-06-04 | 4.0
  2026-06-05 | 55.0
  2026-06-06 | 30.0
  2026-06-07 | 0.0
  2026-06-08 | 59.0
  2026-06-09 | 50.0
  2026-06-10 | 30.0
  ... and 18 more
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'SUGAR-1KG' and inventory book.date between 2026-06-01 and 2026-06-30; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.

## Q035: Should Store 014 stock more milk?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Whether to stock more is a decision not recorded; this gives June on-shelf availability of the two milk pouches (share of 11:00 audits 'on shelf').)
2 rows (columns: sku, status, audits):
  MILK-FC-500ML | on shelf | 8
  MILK-TONED-500ML | on shelf | 8
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku in ['MILK-TONED-500ML', 'MILK-FC-500ML'] and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; group by shelf audits.sku, shelf audits.status; report sku = shelf audits.sku, status = shelf audits.status, audits = count of *.
Part 2: figures from the schema layer. (Plan covers: June write-offs of the milk pouches by reason (waste and empty shelf are one decision, Rule 6).)
3 rows (columns: sku, reason, units):
  MILK-FC-500ML | expired | 198.0
  MILK-TONED-500ML | damaged | 5.0
  MILK-TONED-500ML | expired | 291.0
  How it was found: From write-off records; keep rows where write offs.sku in ['MILK-TONED-500ML', 'MILK-FC-500ML'] and write offs.date between 2026-06-01 and 2026-06-30; group by write offs.sku, write offs.reason; report sku = write offs.sku, reason = write offs.reason, units = sum of write offs.units.
Part 3: figures from the schema layer. (Plan covers: June sales of the milk pouches; demand beyond sales is not recorded.)
2 rows (columns: sku, units):
  MILK-FC-500ML | 2916.0
  MILK-TONED-500ML | 8649.0
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['MILK-TONED-500ML', 'MILK-FC-500ML'] and daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.sku; report sku = daily sales.sku, units = sum of daily sales.units_sold.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q036: What was the typical basket size from 4 May to 28 June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Average units, lines and rupees per bill on till lines 4 May-28 June; till lines hold only the eleven followed items, so this is the basket of those items only (basket_value), not the full basket.)
units_per_bill = 1.405043227665706; lines_per_bill = 1.2782780979827089; inr_per_bill = 90.74236311239193; bills = 27760
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-05-04 and 2026-06-28; report units_per_bill = sum of pos lines may.qty / count distinct of pos lines may.bill_id, lines_per_bill = count of * / count distinct of pos lines may.bill_id, inr_per_bill = sum of pos lines may.line_amount / count distinct of pos lines may.bill_id, bills = count distinct of pos lines may.bill_id.
Stand-ins used (not the real thing): basket_value (who): a bill's total is what one checkout cost: a stand-in for what a shopper spent, since no table links bills to a shopper

## Q037: What was the average number of units of bread sold per day in June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Average daily units_sold of white bread 400 g in June daily sales (1-28 June).)
avg_units_per_day = 59.785714285714285; days = 28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'BREAD-WHITE-400G' and daily sales.date between 2026-06-01 and 2026-06-30; report avg_units_per_day = avg of daily sales.units_sold, days = count distinct of daily sales.date.

## Q038: How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: 5 kg atta units sold in June (1-28 June).)
units = 567.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold.
Part 2: figures from the schema layer. (Plan covers: 5 kg atta units sold in the week of 8 June (Mon 8-Sun 14 June).)
units = 88.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-08 and 2026-06-14; report units = sum of daily sales.units_sold.

## Q039: Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Units sold per warehouse-flow (flow = DC) product in week 1 (1-7 June); compare with the other week to find drops of more than half.)
7 rows (columns: sku, name, units):
  ATTA-WW-10KG | Whole wheat atta 10 kg | 87.0
  ATTA-WW-1KG | Whole wheat atta 1 kg | 238.0
  ATTA-WW-5KG | Whole wheat atta 5 kg | 217.0
  DAL-TOOR-1KG | Toor dal 1 kg | 158.0
  OIL-SUN-1L | Sunflower oil 1 L pouch | 210.0
  RICE-SM-5KG | Sona masoori rice 5 kg | 180.0
  SUGAR-1KG | Sugar 1 kg | 164.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where products.flow = 'DC' and daily sales.date between 2026-06-01 and 2026-06-07; group by daily sales.sku, products.name; report sku = daily sales.sku, name = products.name, units = sum of daily sales.units_sold; sorted by sku asc.
Part 2: figures from the ontology layer. (Plan covers: Units sold per warehouse-flow (flow = DC) product in week 2 (8-14 June); compare with the other week to find drops of more than half.)
7 rows (columns: sku, name, units):
  ATTA-WW-10KG | Whole wheat atta 10 kg | 61.0
  ATTA-WW-1KG | Whole wheat atta 1 kg | 207.0
  ATTA-WW-5KG | Whole wheat atta 5 kg | 88.0
  DAL-TOOR-1KG | Toor dal 1 kg | 139.0
  OIL-SUN-1L | Sunflower oil 1 L pouch | 195.0
  RICE-SM-5KG | Sona masoori rice 5 kg | 153.0
  SUGAR-1KG | Sugar 1 kg | 117.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where products.flow = 'DC' and daily sales.date between 2026-06-08 and 2026-06-14; group by daily sales.sku, products.name; report sku = daily sales.sku, name = products.name, units = sum of daily sales.units_sold; sorted by sku asc.

## Q040: Why did 5 kg atta sales fall in the week of 8 June?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Daily 5 kg atta sales 1-14 June, to check the fall in the week of 8 June; the cause is not recorded (cause).)
14 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 30.0 | 7950.0
  2026-06-02 | 36.0 | 9540.0
  2026-06-03 | 22.0 | 5830.0
  2026-06-04 | 28.0 | 7420.0
  2026-06-05 | 32.0 | 8480.0
  2026-06-06 | 25.0 | 6625.0
  2026-06-07 | 44.0 | 11660.0
  2026-06-08 | 9.0 | 2385.0
  2026-06-09 | 11.0 | 2915.0
  2026-06-10 | 22.0 | 5830.0
  ... and 4 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-14; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf audits of 5 kg atta 1-14 June: whether the shelf was seen empty (on-shelf availability).)
4 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-14; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 3: figures from the schema layer. (Plan covers: Closing book stock of 5 kg atta 1-14 June; book stock is a belief, so stock on the books with no sales points to the shelf (Rule 2).)
14 rows (columns: date, book_on_hand_close):
  2026-06-01 | 58.0
  2026-06-02 | 22.0
  2026-06-03 | 64.0
  2026-06-04 | 36.0
  2026-06-05 | 52.0
  2026-06-06 | 27.0
  2026-06-07 | 43.0
  2026-06-08 | 34.0
  2026-06-09 | 78.0
  2026-06-10 | 56.0
  ... and 4 more
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date between 2026-06-01 and 2026-06-14; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 4: figures from the schema layer. (Plan covers: Goods receipts touching 5 kg atta 1-14 June, booked or noticed, as evidence of what arrived; no record states why sales fell.)
6 rows (columns: received_ts, shipment_id, line, asn_sku, sku_booked, units_booked):
  2026-06-01T06:20 | SHP-260601 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 52.0
  2026-06-03T06:16 | SHP-260603 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0
  2026-06-05T06:21 | SHP-260605 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 48.0
  2026-06-07T06:10 | SHP-260607 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 60.0
  2026-06-09T06:17 | SHP-260609 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 56.0
  2026-06-14T06:16 | SHP-260614 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 56.0
  How it was found: From goods-receipt line records; keep rows where (goods receipts.sku_booked = 'ATTA-WW-5KG' or goods receipts.asn_sku = 'ATTA-WW-5KG') and day(goods receipts.received_ts) between 2026-06-01 and 2026-06-14; report received_ts = goods receipts.received_ts, shipment_id = goods receipts.shipment_id, line = goods receipts.line, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, units_booked = goods receipts.units_booked; sorted by received_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q041: Are shoppers switching from 5 kg to 1 kg atta?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Switching by shoppers is not recorded (no identity); the plan shows daily units of both pack sizes so a shift in totals can be seen.)
56 rows (columns: date, sku, units_sold):
  2026-06-01 | ATTA-WW-1KG | 22.0
  2026-06-01 | ATTA-WW-5KG | 30.0
  2026-06-02 | ATTA-WW-1KG | 35.0
  2026-06-02 | ATTA-WW-5KG | 36.0
  2026-06-03 | ATTA-WW-1KG | 41.0
  2026-06-03 | ATTA-WW-5KG | 22.0
  2026-06-04 | ATTA-WW-1KG | 24.0
  2026-06-04 | ATTA-WW-5KG | 28.0
  2026-06-05 | ATTA-WW-1KG | 24.0
  2026-06-05 | ATTA-WW-5KG | 32.0
  ... and 46 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-5KG', 'ATTA-WW-1KG'] and daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.date, daily sales.sku; report date = daily sales.date, sku = daily sales.sku, units_sold = sum of daily sales.units_sold; sorted by date asc.

## Q042: What has daily demand for 5 kg atta been in June so far?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Demand is not recorded (Rule 3); recorded daily sales of 5 kg atta in June are a floor on demand, lower on days the shelf was empty.)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 30.0 | 7950.0
  2026-06-02 | 36.0 | 9540.0
  2026-06-03 | 22.0 | 5830.0
  2026-06-04 | 28.0 | 7420.0
  2026-06-05 | 32.0 | 8480.0
  2026-06-06 | 25.0 | 6625.0
  2026-06-07 | 44.0 | 11660.0
  2026-06-08 | 9.0 | 2385.0
  2026-06-09 | 11.0 | 2915.0
  2026-06-10 | 22.0 | 5830.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf audits of 5 kg atta in June mark the days sales understate demand.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Not recorded, so not answered: needs a longer period than the records cover

## Q043: How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Recorded 5 kg atta sales 23-26 June; lost sales are not recorded (Rule 3) and must be estimated.)
4 rows (columns: date, units_sold, revenue_inr):
  2026-06-23 | 5.0 | 1325.0
  2026-06-24 | 0.0 | 0.0
  2026-06-25 | 0.0 | 0.0
  2026-06-26 | 0.0 | 0.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-23 and 2026-06-26; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf audits of 5 kg atta 23-26 June (11:00 on Tue 23 and Fri 26) confirm when the shelf was empty.)
2 rows (columns: audit_ts, status):
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-23 and 2026-06-26; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 3: figures from the schema layer. (Plan covers: Stand-in demand rate: average daily 5 kg atta sales 1-22 June; times the empty days 23-26 June gives an estimate of bags wanted and not found.)
avg_units_per_day = 22.59090909090909; days = 22
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-22; report avg_units_per_day = avg of daily sales.units_sold, days = count distinct of daily sales.date.
Part 4: figures from the schema layer. (Plan covers: Forecast units per day for 5 kg atta 23-26 June, a second stand-in for demand (forecast is the 28-day mean of sales).)
4 rows (columns: date, forecast_units_per_day):
  2026-06-23 | 21.79
  2026-06-24 | 20.96
  2026-06-25 | 20.14
  2026-06-26 | 19.64
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and forecasts.date between 2026-06-23 and 2026-06-26; report date = forecasts.date, forecast_units_per_day = forecasts.forecast_units_per_day; sorted by date asc.

## Q044: Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Premise check: 5 kg atta units in week 1 (1-7 June), to compare with the week of 8 June.)
units = 217.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-07; report units = sum of daily sales.units_sold.
Part 2: figures from the schema layer. (Plan covers: Premise check: 5 kg atta units in the week of 8 June (8-14 June).)
units = 88.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-08 and 2026-06-14; report units = sum of daily sales.units_sold.
Part 3: figures from the schema layer. (Plan covers: Premise check: closing book stock of 5 kg atta 8-14 June; books are a belief (Rule 1), stock with no sales means look at the shelf (Rule 2).)
7 rows (columns: date, book_on_hand_close):
  2026-06-08 | 34.0
  2026-06-09 | 78.0
  2026-06-10 | 56.0
  2026-06-11 | 55.0
  2026-06-12 | 55.0
  2026-06-13 | 33.0
  2026-06-14 | 66.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date between 2026-06-08 and 2026-06-14; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 4: figures from the schema layer. (Plan covers: Shelf audits of 5 kg atta 1-14 June: whether the shelf, not demand, explains the drop; shelf space is not recorded, so no reallocation can be sized from the records.)
4 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-14; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.

## Q045: Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No table records shoppers who walked out; the only evidence is the count of June 2026 audits that found 5 kg atta empty.)
empty_audits = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report empty_audits = count of *.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q046: How many bags of 5 kg atta were sold in June 2023?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: year outside 2026

## Q047: Which products have flow = 'DC' versus flow = 'DSD', and what share of June 2026 revenue came from each flow?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Each product's flow, DC (warehouse) or DSD (direct delivery).)
11 rows (columns: sku, name, flow):
  ATTA-WW-10KG | Whole wheat atta 10 kg | DC
  ATTA-WW-1KG | Whole wheat atta 1 kg | DC
  ATTA-WW-5KG | Whole wheat atta 5 kg | DC
  DAL-TOOR-1KG | Toor dal 1 kg | DC
  OIL-SUN-1L | Sunflower oil 1 L pouch | DC
  RICE-SM-5KG | Sona masoori rice 5 kg | DC
  SUGAR-1KG | Sugar 1 kg | DC
  BREAD-WHITE-400G | White bread 400 g | DSD
  CURD-500G | Curd 500 g pouch | DSD
  MILK-FC-500ML | Full cream milk 500 ml pouch | DSD
  ... and 1 more
  How it was found: From product records; report sku = products.sku, name = products.name, flow = products.flow; sorted by flow asc, sku asc.
Part 2: figures from the ontology layer. (Plan covers: June revenue (eleven followed items, daily sales) by flow; each flow's share = its revenue / the total of both rows.)
2 rows (columns: flow, revenue_inr):
  DC | 782445.0
  DSD | 461492.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.date between 2026-06-01 and 2026-06-30; group by products.flow; report flow = products.flow, revenue_inr = sum of daily sales.revenue_inr.

## Q048: How many bills in store.pos_lines contain both ATTA-WW-5KG and DAL-TOOR-1KG on the same bill_id?

Answered from the schema layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Bills in till lines with 5 kg atta and bills with toor dal 1 kg (each count).)
2 rows (columns: sku, bills):
  ATTA-WW-5KG | 1177
  DAL-TOOR-1KG | 1006
  How it was found: From till line records; keep rows where pos lines may.sku_scanned in ['ATTA-WW-5KG', 'DAL-TOOR-1KG']; group by pos lines may.sku_scanned; report sku = pos lines may.sku_scanned, bills = count distinct of pos lines may.bill_id.
Part 2: figures from the schema layer. (Plan covers: Bills with 5 kg atta or toor dal; bills with both = atta bills + dal bills - bills with either.)
bills_with_either = 2160
  How it was found: From till line records; keep rows where pos lines may.sku_scanned in ['ATTA-WW-5KG', 'DAL-TOOR-1KG']; report bills_with_either = count distinct of pos lines may.bill_id.
Part 3: figures from the schema layer. (Plan covers: List of bills holding both 5 kg atta and toor dal 1 kg on till lines.)
23 rows (columns: bill_id, skus):
  B260504-090041 | 2
  B260506-050009 | 2
  B260506-090024 | 2
  B260512-080025 | 2
  B260512-130049 | 2
  B260520-110068 | 2
  B260520-140049 | 2
  B260521-140051 | 2
  B260522-140007 | 2
  B260523-060019 | 2
  ... and 13 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned in ['ATTA-WW-5KG', 'DAL-TOOR-1KG']; group by pos lines may.bill_id; keep groups where skus = 2; report bill_id = pos lines may.bill_id, skus = count distinct of pos lines may.sku_scanned; sorted by bill_id asc.

## Q049: Which hour of the day (07:00 to 21:00) had the highest average basket value across store.pos_lines in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Average rupees per bill on June till lines by hour of bill_ts (07:00-21:00); till lines hold only the eleven followed items, so this is their basket value, not the full bill.)
15 rows (columns: hour, avg_basket_inr, bills):
  20 | 133.65894465894465 | 777
  21 | 119.59966499162479 | 597
  19 | 112.43422263109476 | 1087
  12 | 101.33333333333333 | 618
  17 | 100.95359848484848 | 1056
  18 | 97.91078669910787 | 1233
  14 | 95.63258785942492 | 626
  16 | 94.35505617977527 | 890
  11 | 90.9778933680104 | 769
  15 | 90.32147742818057 | 731
  ... and 5 more
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30 and hour(pos lines may.bill_ts) between 7 and 21; group by hour(pos lines may.bill_ts); report hour = hour(pos lines may.bill_ts), avg_basket_inr = sum of pos lines may.line_amount / count distinct of pos lines may.bill_id, bills = count distinct of pos lines may.bill_id; sorted by avg_basket_inr desc.
Stand-ins used (not the real thing): basket_value (who): a bill's total is what one checkout cost: a stand-in for what a shopper spent, since no table links bills to a shopper

## Q050: How do Store 014's weekday versus weekend daily unit sales compare for RICE-SM-5KG in May 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Daily units of 5 kg rice in May 2026 from till lines (daily sales cover June only; May starts 4 May); code splits weekday and weekend.)
28 rows (columns: day, units):
  2026-05-04 | 36.0
  2026-05-05 | 30.0
  2026-05-06 | 25.0
  2026-05-07 | 33.0
  2026-05-08 | 25.0
  2026-05-09 | 28.0
  2026-05-10 | 40.0
  2026-05-11 | 23.0
  2026-05-12 | 11.0
  2026-05-13 | 17.0
  ... and 18 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'RICE-SM-5KG' and day(pos lines may.bill_ts) between 2026-05-01 and 2026-05-31; group by day(pos lines may.bill_ts); report day = day(pos lines may.bill_ts), units = sum of pos lines may.qty; sorted by day asc.
Stand-ins used (not the real thing): May is a part month in the till lines (4 May to 28 June)

## Q051: How many distinct gtin_scanned values appear in store.pos_lines, and does every one match store.products.gtin?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Distinct gtin_scanned values on till lines.)
distinct_gtins = 11
  How it was found: From till line records; report distinct_gtins = count distinct of pos lines may.gtin_scanned.
Part 2: figures from the ontology layer. (Plan covers: Each scanned GTIN matched to products.gtin by left join; a blank product_sku means no match.)
11 rows (columns: gtin_scanned, product_sku, lines):
  2900001001014 | ATTA-WW-5KG | 1177
  2900001001021 | ATTA-WW-1KG | 1546
  2900001001038 | ATTA-WW-10KG | 566
  2900001001113 | RICE-SM-5KG | 1234
  2900001001212 | DAL-TOOR-1KG | 1006
  2900001001311 | OIL-SUN-1L | 1502
  2900001001410 | SUGAR-1KG | 1050
  2900001002011 | MILK-TONED-500ML | 14655
  2900001002028 | MILK-FC-500ML | 5728
  2900001002110 | CURD-500G | 3755
  ... and 1 more
  How it was found: From till line records; left-join product records on pos lines may.gtin_scanned = products.gtin; group by pos lines may.gtin_scanned, products.sku; report gtin_scanned = pos lines may.gtin_scanned, product_sku = products.sku, lines = count of *; sorted by gtin_scanned asc.

## Q052: Which bill in June 2026 had the most line items (COUNT(*) in store.pos_lines), and which had the highest total bill amount?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: June bills with the most till lines (eleven followed items only).)
5 rows (columns: bill_id, lines, followed_items_inr):
  B260620-110049 | 5 | 677.0
  B260613-090015 | 5 | 902.0
  B260606-000049 | 5 | 488.0
  B260603-050013 | 5 | 743.0
  B260628-010088 | 4 | 478.0
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; group by pos lines may.bill_id; report bill_id = pos lines may.bill_id, lines = count of *, followed_items_inr = sum of pos lines may.line_amount; sorted by lines desc.
Part 2: figures from the schema layer. (Plan covers: June bill with the highest total, from approved payments (Bills and takings definition: bill totals come from payments).)
5 rows (columns: bill_id, amount_inr, ts):
  B260621-140000 | 17558.14 | 2026-06-21T21:00:36
  B260619-140036 | 14543.19 | 2026-06-19T21:39:54
  B260608-090013 | 13677.6 | 2026-06-08T16:15:08
  B260606-000038 | 12886.97 | 2026-06-06T07:28:22
  B260618-110056 | 11136.8 | 2026-06-18T18:31:21
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bill_id = pos payments.bill_id, amount_inr = pos payments.amount_inr, ts = pos payments.ts; sorted by amount_inr desc.
Part 3: figures from the schema layer. (Plan covers: June bills with the highest till-line total (eleven followed items only), for comparison with the payment total.)
5 rows (columns: bill_id, followed_items_inr):
  B260625-130019 | 1150.0
  B260605-110052 | 1050.0
  B260621-110094 | 950.0
  B260627-090009 | 932.0
  B260605-040036 | 906.0
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; group by pos lines may.bill_id; report bill_id = pos lines may.bill_id, followed_items_inr = sum of pos lines may.line_amount; sorted by followed_items_inr desc.

## Q053: Which SKU in store.daily_sales had the largest single-day percentage drop in units_sold between two consecutive days in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Daily units for the first six products in June 2026; code finds the largest consecutive-day percentage drop.)
168 rows (columns: sku, date, units_sold):
  ATTA-WW-10KG | 2026-06-01 | 10.0
  ATTA-WW-10KG | 2026-06-02 | 13.0
  ATTA-WW-10KG | 2026-06-03 | 12.0
  ATTA-WW-10KG | 2026-06-04 | 7.0
  ATTA-WW-10KG | 2026-06-05 | 17.0
  ATTA-WW-10KG | 2026-06-06 | 11.0
  ATTA-WW-10KG | 2026-06-07 | 17.0
  ATTA-WW-10KG | 2026-06-08 | 4.0
  ATTA-WW-10KG | 2026-06-09 | 5.0
  ATTA-WW-10KG | 2026-06-10 | 7.0
  ... and 158 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG', 'BREAD-WHITE-400G', 'CURD-500G', 'DAL-TOOR-1KG'] and daily sales.date between 2026-06-01 and 2026-06-30; report sku = daily sales.sku, date = daily sales.date, units_sold = daily sales.units_sold; sorted by sku asc, date asc.
Part 2: figures from the schema layer. (Plan covers: Daily units for the remaining five products in June 2026.)
140 rows (columns: sku, date, units_sold):
  MILK-FC-500ML | 2026-06-01 | 99.0
  MILK-FC-500ML | 2026-06-02 | 123.0
  MILK-FC-500ML | 2026-06-03 | 81.0
  MILK-FC-500ML | 2026-06-04 | 74.0
  MILK-FC-500ML | 2026-06-05 | 99.0
  MILK-FC-500ML | 2026-06-06 | 151.0
  MILK-FC-500ML | 2026-06-07 | 101.0
  MILK-FC-500ML | 2026-06-08 | 121.0
  MILK-FC-500ML | 2026-06-09 | 158.0
  MILK-FC-500ML | 2026-06-10 | 87.0
  ... and 130 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['MILK-FC-500ML', 'MILK-TONED-500ML', 'OIL-SUN-1L', 'RICE-SM-5KG', 'SUGAR-1KG'] and daily sales.date between 2026-06-01 and 2026-06-30; report sku = daily sales.sku, date = daily sales.date, units_sold = daily sales.units_sold; sorted by sku asc, date asc.

## Q054: Compare May 2026 and June 2026 total sales using store.daily_sales.

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: June totals from daily sales (eleven followed items, 1-28 June).)
units = 19265.0; revenue_inr = 1243937.0; days = 28
  How it was found: From daily sales row records; keep rows where daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, days = count distinct of daily sales.date.
Part 2: figures from the schema layer. (Plan covers: Daily sales hold no May rows, so May totals come from till lines (eleven followed items, 4-31 May).)
units = 19739.0; revenue_inr = 1275071.0; days = 28
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-05-01 and 2026-05-31; report units = sum of pos lines may.qty, revenue_inr = sum of pos lines may.line_amount, days = count distinct of day(pos lines may.bill_ts).
Stand-ins used (not the real thing): May is a part month in the till lines (4 May to 28 June)

## Q055: How many bags of ATTA-WW-5KG were sold across all 30 days of June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: 5 kg atta units over June; checks the premise of 30 days: daily sales cover only 1-28 June.)
units = 567.0; days_recorded = 28; last_day = 2026-06-28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold, days_recorded = count distinct of daily sales.date, last_day = max of daily sales.date.

## Q056: Join store.pos_lines to store.products on name to compute revenue by product.

Answered from the ontology layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Revenue by product on till lines, joined on the pack code (sku_scanned = products.sku), not on name: Rule 7 forbids matching on product name and till lines have no name column.)
11 rows (columns: sku, name, revenue_inr):
  MILK-TONED-500ML | Toned milk 500 ml pouch | 453570.0
  RICE-SM-5KG | Sona masoori rice 5 kg | 436948.0
  ATTA-WW-5KG | Whole wheat atta 5 kg | 317470.0
  ATTA-WW-10KG | Whole wheat atta 10 kg | 283432.0
  OIL-SUN-1L | Sunflower oil 1 L pouch | 231344.0
  MILK-FC-500ML | Full cream milk 500 ml pouch | 207026.0
  DAL-TOOR-1KG | Toor dal 1 kg | 170016.0
  BREAD-WHITE-400G | White bread 400 g | 152280.0
  CURD-500G | Curd 500 g pouch | 124800.0
  ATTA-WW-1KG | Whole wheat atta 1 kg | 91002.0
  ... and 1 more
  How it was found: From till line records; inner-join product records on pos lines may.sku_scanned = products.sku; group by products.sku, products.name; report sku = products.sku, name = products.name, revenue_inr = sum of pos lines may.line_amount; sorted by revenue_inr desc.

## Q057: How many units of DAL-TOOR-1KG were returned by customers for a refund in June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Product returns are not recorded (UPI refunds answer extra debits, not returned goods); this checks June till lines of toor dal with negative quantity, the only possible trace of a return.)
lines = 0; units = None
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'DAL-TOOR-1KG' and pos lines may.qty < 0 and day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; report lines = count of *, units = sum of pos lines may.qty.

## Q058: What were Store 014's total sales in June 2026, in rupees?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June takings = sum of approved payments (Bills and takings definition).)
takings_inr = 17570666.87; bills = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report takings_inr = sum of pos payments.amount_inr, bills = count distinct of pos payments.bill_id.

## Q059: For how many hours in June 2026 was 5 kg atta off the shelf?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Hours off the shelf are not recorded (shelf_hours); audits are 11:00 snapshots twice a week, so this counts empty audits, not hours.)
empty_audits = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report empty_audits = count of *.
Stand-ins used (not the real thing): shelf_hours (not_happen): shelf audits are 11:00 snapshots twice a week, not hours off the shelf

## Q060: How much stock was stolen in June 2026, as opposed to counted wrong?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: June store count corrections by trigger; no record says whether a shortfall was theft or a counting error (cause).)
2 rows (columns: trigger, counts, net_adjustment_packs, gross_adjustment_packs):
  manager request after complaints | 3 | 93.0 | 221.0
  scheduled full count | 22 | -55.0 | 185.0
  How it was found: From stock count records; keep rows where day(stock counts.count_ts) between 2026-06-01 and 2026-06-30; group by stock counts.trigger; report trigger = stock counts.trigger, counts = count of *, net_adjustment_packs = sum of stock counts.adjustment, gross_adjustment_packs = sum of abs(stock counts.adjustment).
Part 2: figures from the schema layer. (Plan covers: Warehouse stock adjustments by recorded reason (count variances, no theft reason recorded); mirror-image corrections may be one event (Rule 5).)
2 rows (columns: reason, units, value_at_cost_inr):
  cycle count variance | 64.0 | 14592.0
  short pick: slot count variance | -160.0 | -7920.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where day(dc stock adjustments.adjusted_ts) between 2026-06-01 and 2026-06-30; group by dc stock adjustments.reason; report reason = dc stock adjustments.reason, units = sum of dc stock adjustments.units, value_at_cost_inr = sum of dc stock adjustments.value_at_cost_inr.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q061: When was the 5 kg atta shelf restocked in June 2026, and how long did each restock take?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Shelf restock times are not recorded (restock_times); only back-door receipts of 5 kg atta in June 2026 are listed.)
11 rows (columns: received_ts, units_booked, grn_id):
  2026-06-01T06:20 | 52.0 | GRN-260601
  2026-06-03T06:16 | 64.0 | GRN-260603
  2026-06-05T06:21 | 48.0 | GRN-260605
  2026-06-07T06:10 | 60.0 | GRN-260607
  2026-06-09T06:17 | 56.0 | GRN-260609
  2026-06-14T06:16 | 56.0 | GRN-260614
  2026-06-17T06:03 | 60.0 | GRN-260617
  2026-06-20T06:22 | 72.0 | GRN-260620
  2026-06-22T06:12 | 64.0 | GRN-260622
  2026-06-27T06:05 | 84.0 | GRN-260627
  ... and 1 more
  How it was found: From goods-receipt line records; keep rows where goods receipts.sku_booked = 'ATTA-WW-5KG' and day(goods receipts.received_ts) between 2026-06-01 and 2026-06-30; report received_ts = goods receipts.received_ts, units_booked = goods receipts.units_booked, grn_id = goods receipts.grn_id; sorted by received_ts asc.
Not recorded, so not answered: restock_times (not_happen): restock time on the shelf is not recorded (only receipts at the back door) [rule-1]

## Q062: How accurate was the June 2026 forecast for 5 kg atta against real customer demand?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: June forecast units of 5 kg atta; demand is not recorded (forecast_vs_demand), so it can only be scored against recorded sales.)
forecast_units = 637.32; days = 28
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and forecasts.date between 2026-06-01 and 2026-06-30; report forecast_units = sum of forecasts.forecast_units_per_day, days = count distinct of forecasts.date.
Part 2: figures from the schema layer. (Plan covers: June recorded sales of 5 kg atta, the only available score for the forecast (sales understate demand on empty-shelf days).)
units_sold = 567.0; days = 28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units_sold = sum of daily sales.units_sold, days = count distinct of daily sales.date.
Part 3: figures from the schema layer. (Plan covers: June shelf audits of 5 kg atta mark days when sales understate demand.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Not recorded, so not answered: forecast_vs_demand (not_happen): a forecast can only be scored against recorded sales, not demand [rule-4]

## Q063: How many write-off lines in June 2026 had the reason 'expired'?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June write-off rows with reason 'expired'.)
lines = 19
  How it was found: From write-off records; keep rows where write offs.reason = 'expired' and write offs.date between 2026-06-01 and 2026-06-30; report lines = count of *.

## Q064: How many units were written off as expired in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Units written off as expired in June.)
units = 489.0
  How it was found: From write-off records; keep rows where write offs.reason = 'expired' and write offs.date between 2026-06-01 and 2026-06-30; report units = sum of write offs.units.

## Q065: How many shelf-audit rows in June 2026 show a product as empty?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June shelf-audit rows with status 'empty'.)
rows = 3
  How it was found: From shelf-audit row records; keep rows where shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report rows = count of *.

## Q066: What caused the damage on the units written off as damaged in June 2026: rough handling, a faulty fridge or a late delivery?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June write-offs with reason 'damaged'; the cause of damage (handling, fridge, late delivery) is not recorded (cause).)
15 rows (columns: date, sku, units):
  2026-06-01 | MILK-TONED-500ML | 1.0
  2026-06-03 | RICE-SM-5KG | 1.0
  2026-06-09 | ATTA-WW-5KG | 1.0
  2026-06-09 | MILK-TONED-500ML | 1.0
  2026-06-10 | MILK-TONED-500ML | 1.0
  2026-06-11 | MILK-TONED-500ML | 1.0
  2026-06-11 | CURD-500G | 1.0
  2026-06-13 | DAL-TOOR-1KG | 1.0
  2026-06-15 | RICE-SM-5KG | 1.0
  2026-06-18 | CURD-500G | 1.0
  ... and 5 more
  How it was found: From write-off records; keep rows where write offs.reason = 'damaged' and write offs.date between 2026-06-01 and 2026-06-30; report date = write offs.date, sku = write offs.sku, units = write offs.units; sorted by date asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q067: Why was the 28-day mean chosen as the forecast method for Store 014's products?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: The records show which forecast method was used, not why it was chosen (cause).)
method = 28-day mean of recorded sales; rows = 196
  How it was found: From forecast row records; group by forecasts.method; report method = forecasts.method, rows = count of *.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q068: What was the temperature inside Store 014's milk fridge each day in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q069: How many units of 5 kg atta were on the shelf at 3 pm on 10 June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Shelf counts at 3 pm are not recorded; audits are 11:00 snapshots (Tuesday and Friday), so the nearest audits around 10 June are listed.)
2 rows (columns: audit_ts, status):
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-09 and 2026-06-12; report audit_ts = shelf audits.audit_ts, status = shelf audits.status.
Part 2: figures from the schema layer. (Plan covers: Closing book stock on 10 June is a belief, not the shelf count.)
book_on_hand_close = 56.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date = '2026-06-10'; report book_on_hand_close = inventory book.book_on_hand_close.
Stand-ins used (not the real thing): shelf_hours (not_happen): shelf audits are 11:00 snapshots twice a week, not hours off the shelf

## Q070: How many stock counts in June 2026 were triggered by a manager's request after complaints?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June stock counts with trigger 'manager request after complaints'.)
counts = 3
  How it was found: From stock count records; keep rows where stock counts.trigger = 'manager request after complaints' and day(stock counts.count_ts) between 2026-06-01 and 2026-06-30; report counts = count of *.

## Q071: On how many different days in June 2026 was at least one write-off recorded?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Distinct June dates with at least one write-off.)
days = 22
  How it was found: From write-off records; keep rows where write offs.date between 2026-06-01 and 2026-06-30; report days = count distinct of write offs.date.

## Q072: How many stock counts did Store 014 do in the first quarter of 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: needs a longer period than the records cover

## Q073: Why did curd write-offs for expiry happen on the days they did in June 2026: over-ordering, slow sales or a warm fridge?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Days and units of curd written off as expired in June; the cause (over-ordering, slow sales, warm fridge) is not recorded and fridge temperature is not in any table.)
No rows matched.
  How it was found: From write-off records; keep rows where write offs.sku = 'CURD-500G' and write offs.reason = 'expired' and write offs.date between 2026-06-01 and 2026-06-30; report date = write offs.date, units = write offs.units; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: June fresh deliveries of curd with use-by dates, evidence on how much was ordered against shelf life (Rule 6).)
28 rows (columns: delivery_ts, units, use_by, route):
  2026-06-01T05:30 | 69.0 | 2026-06-04 | R-07
  2026-06-02T05:30 | 69.0 | 2026-06-05 | R-07
  2026-06-03T05:30 | 69.0 | 2026-06-06 | R-07
  2026-06-04T05:30 | 70.0 | 2026-06-07 | R-07
  2026-06-05T05:30 | 71.0 | 2026-06-08 | R-07
  2026-06-06T05:30 | 76.0 | 2026-06-09 | R-07
  2026-06-07T05:30 | 75.0 | 2026-06-10 | R-07
  2026-06-08T05:30 | 69.0 | 2026-06-11 | R-07
  2026-06-09T05:30 | 69.0 | 2026-06-12 | R-07
  2026-06-10T05:30 | 69.0 | 2026-06-13 | R-07
  ... and 18 more
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'CURD-500G' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report delivery_ts = fresh deliveries.delivery_ts, units = fresh deliveries.units, use_by = fresh deliveries.use_by, route = fresh deliveries.route; sorted by delivery_ts asc.
Part 3: figures from the schema layer. (Plan covers: June daily curd sales, evidence on whether sales were slow before the expiry days.)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 112.0 | 3584.0
  2026-06-02 | 38.0 | 1216.0
  2026-06-03 | 59.0 | 1888.0
  2026-06-04 | 88.0 | 2816.0
  2026-06-05 | 58.0 | 1856.0
  2026-06-06 | 58.0 | 1856.0
  2026-06-07 | 129.0 | 4128.0
  2026-06-08 | 50.0 | 1600.0
  2026-06-09 | 72.0 | 2304.0
  2026-06-10 | 74.0 | 2368.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'CURD-500G' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 4: figures from the schema layer. (Plan covers: June curd forecast and ordered units, evidence on over-ordering against the 28-day mean.)
No rows matched.
  How it was found: From forecast row records; keep rows where forecasts.sku = 'CURD-500G' and forecasts.date between 2026-06-01 and 2026-06-30; report date = forecasts.date, forecast_units_per_day = forecasts.forecast_units_per_day, ordered_units = forecasts.ordered_units; sorted by date asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q074: How many units did Store 014 lose in June 2026 to damage, expiry, theft and counting errors together?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Units written off as damaged and expired in June 2026; theft is not recorded.)
2 rows (columns: reason, units):
  damaged | 15.0
  expired | 489.0
  How it was found: From write-off records; keep rows where write offs.date between 2026-06-01 and 2026-06-30; group by write offs.reason; report reason = write offs.reason, units = sum of write offs.units.
Part 2: figures from the schema layer. (Plan covers: Count corrections in packs in June 2026; they mix theft and counting errors, which are not told apart.)
net_adjustment_packs = 38.0; gross_adjustment_packs = 406.0
  How it was found: From stock count records; keep rows where day(stock counts.count_ts) between 2026-06-01 and 2026-06-30; report net_adjustment_packs = sum of stock counts.adjustment, gross_adjustment_packs = sum of abs(stock counts.adjustment).
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q075: How many different products were written off in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Distinct products written off in June.)
products = 7
  How it was found: From write-off records; keep rows where write offs.date between 2026-06-01 and 2026-06-30; report products = count distinct of write offs.sku.

## Q076: How many stock counts in June 2026 found a difference between book and counted stock?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June stock counts where counted differs from book_before.)
counts = 21
  How it was found: From stock count records; keep rows where stock counts.counted != stock counts.book_before and day(stock counts.count_ts) between 2026-06-01 and 2026-06-30; report counts = count of *.

## Q077: How many shelf-audit rows missed a product that was on the shelf but hidden behind another?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Whether an empty audit missed a hidden product is not recorded; these are the June audit rows marked empty, to be set against same-day sales (Rule 2).)
3 rows (columns: sku, audit_ts):
  SUGAR-1KG | 2026-06-05T11:00
  ATTA-WW-5KG | 2026-06-12T11:00
  ATTA-WW-5KG | 2026-06-26T11:00
  How it was found: From shelf-audit row records; keep rows where shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report sku = shelf audits.sku, audit_ts = shelf audits.audit_ts; sorted by audit_ts asc.

## Q078: On how many days in June 2026 did the 5 kg atta shelf look empty at the 11:00 audit?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Distinct June days the 5 kg atta audit row says 'empty'.)
days = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report days = count distinct of day(shelf audits.audit_ts).
Stand-ins used (not the real thing): shelf_hours (not_happen): shelf audits are 11:00 snapshots twice a week, not hours off the shelf

## Q079: How many different products had a shelf-audit row marked empty in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Distinct products with an empty audit row in June.)
products = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report products = count distinct of shelf audits.sku.

## Q080: What was the reason for the largest write-off in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Largest June write-off by units, with its recorded reason.)
3 rows (columns: date, sku, reason, units):
  2026-06-26 | MILK-TONED-500ML | expired | 74.0
  2026-06-15 | MILK-TONED-500ML | expired | 50.0
  2026-06-12 | MILK-TONED-500ML | expired | 48.0
  How it was found: From write-off records; keep rows where write offs.date between 2026-06-01 and 2026-06-30; report date = write offs.date, sku = write offs.sku, reason = write offs.reason, units = write offs.units; sorted by units desc.

## Q081: Which shelf audits found an item empty while the hourly book showed stock above zero?

Answered from the ontology layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: There is no hourly book, only a daily close; empty audits matched to the previous day's (the stock believed at the 11:00 audit) closing book stock above zero (Rule 1: book is a belief, the audit is the shelf).)
3 rows (columns: sku, audit_ts, book_date, book_on_hand_close):
  SUGAR-1KG | 2026-06-05T11:00 | 2026-06-04 | 4.0
  ATTA-WW-5KG | 2026-06-12T11:00 | 2026-06-11 | 55.0
  ATTA-WW-5KG | 2026-06-26T11:00 | 2026-06-25 | 63.0
  How it was found: From shelf-audit row records; inner-join book-stock row records on shelf audits.sku = inventory book.sku; keep rows where shelf audits.status = 'empty' and days_between(inventory book.date, day(shelf audits.audit_ts)) = 1 and inventory book.book_on_hand_close > 0; report sku = shelf audits.sku, audit_ts = shelf audits.audit_ts, book_date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by audit_ts asc.
Part 2: figures from the ontology layer. (Plan covers: There is no hourly book, only a daily close; empty audits matched to the same day's closing book stock above zero (Rule 1: book is a belief, the audit is the shelf).)
2 rows (columns: sku, audit_ts, book_date, book_on_hand_close):
  SUGAR-1KG | 2026-06-05T11:00 | 2026-06-05 | 55.0
  ATTA-WW-5KG | 2026-06-12T11:00 | 2026-06-12 | 55.0
  How it was found: From shelf-audit row records; inner-join book-stock row records on shelf audits.sku = inventory book.sku; keep rows where shelf audits.status = 'empty' and days_between(inventory book.date, day(shelf audits.audit_ts)) = 0 and inventory book.book_on_hand_close > 0; report sku = shelf audits.sku, audit_ts = shelf audits.audit_ts, book_date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by audit_ts asc.

## Q082: On which days did any item's closing book stock go below zero?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Days and products with closing book stock below zero.)
6 rows (columns: date, sku, book_on_hand_close):
  2026-06-02 | MILK-FC-500ML | -5.0
  2026-06-09 | MILK-FC-500ML | -5.0
  2026-06-11 | MILK-FC-500ML | -15.0
  2026-06-12 | MILK-FC-500ML | -12.0
  2026-06-13 | MILK-FC-500ML | -14.0
  2026-06-20 | MILK-FC-500ML | -13.0
  How it was found: From book-stock row records; keep rows where inventory book.book_on_hand_close < 0; report date = inventory book.date, sku = inventory book.sku, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.

## Q083: Which stock counts disagreed with the book stock by more than 2%?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Stock counts where |counted - book_before| / book_before exceeds 2%.)
19 rows (columns: sku, count_ts, book_before, counted, adjustment, gap_share):
  ATTA-WW-1KG | 2026-06-01T05:45 | 92.0 | 87.0 | -5.0 | 0.05434782608695652
  ATTA-WW-10KG | 2026-06-01T05:45 | 28.0 | 29.0 | 1.0 | 0.03571428571428571
  RICE-SM-5KG | 2026-06-01T05:45 | 66.0 | 64.0 | -2.0 | 0.030303030303030304
  DAL-TOOR-1KG | 2026-06-01T05:45 | 15.0 | 13.0 | -2.0 | 0.13333333333333333
  OIL-SUN-1L | 2026-06-01T05:45 | 82.0 | 77.0 | -5.0 | 0.06097560975609756
  SUGAR-1KG | 2026-06-01T05:45 | 46.0 | 44.0 | -2.0 | 0.043478260869565216
  MILK-TONED-500ML | 2026-06-01T05:45 | 377.0 | 351.0 | -26.0 | 0.06896551724137931
  MILK-FC-500ML | 2026-06-01T05:45 | 94.0 | 109.0 | 15.0 | 0.1595744680851064
  CURD-500G | 2026-06-01T05:45 | 115.0 | 112.0 | -3.0 | 0.02608695652173913
  BREAD-WHITE-400G | 2026-06-01T05:45 | 64.0 | 59.0 | -5.0 | 0.078125
  ... and 9 more
  How it was found: From stock count records; keep rows where abs(stock counts.counted - stock counts.book_before) / stock counts.book_before > 0.02; report sku = stock counts.sku, count_ts = stock counts.count_ts, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment, gap_share = abs(stock counts.counted - stock counts.book_before) / stock counts.book_before; sorted by count_ts asc.

## Q084: What time did toned milk record its last sale each day, and how many pouches were written off?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Time of the last toned milk till line each day in June 2026.)
28 rows (columns: day, last_sale_ts):
  2026-06-01 | 2026-06-01T21:59
  2026-06-02 | 2026-06-02T18:55
  2026-06-03 | 2026-06-03T19:58
  2026-06-04 | 2026-06-04T21:40
  2026-06-05 | 2026-06-05T21:56
  2026-06-06 | 2026-06-06T21:58
  2026-06-07 | 2026-06-07T21:53
  2026-06-08 | 2026-06-08T21:50
  2026-06-09 | 2026-06-09T21:54
  2026-06-10 | 2026-06-10T21:37
  ... and 18 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'MILK-TONED-500ML' and day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; group by day(pos lines may.bill_ts); report day = day(pos lines may.bill_ts), last_sale_ts = max of pos lines may.bill_ts; sorted by day asc.
Part 2: figures from the schema layer. (Plan covers: Toned milk pouches written off in June 2026.)
pouches_written_off = 296.0
  How it was found: From write-off records; keep rows where write offs.sku = 'MILK-TONED-500ML' and write offs.date between 2026-06-01 and 2026-06-30; report pouches_written_off = sum of write offs.units.

## Q085: Was 5 kg atta in stock on Thursday 11 June?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Closing book stock on Thursday 11 June is a belief, not the shelf (Rule 1).)
book_on_hand_close = 55.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date = '2026-06-11'; report book_on_hand_close = inventory book.book_on_hand_close.
Part 2: figures from the schema layer. (Plan covers: No audit is recorded on a Thursday; the Tuesday 9 and Friday 12 June audits are the nearest shelf evidence.)
2 rows (columns: audit_ts, status):
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-09 and 2026-06-12; report audit_ts = shelf audits.audit_ts, status = shelf audits.status.
Part 3: figures from the schema layer. (Plan covers: Sales on 11 June show whether the product moved.)
units_sold = 1.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date = '2026-06-11'; report units_sold = daily sales.units_sold.

## Q086: What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: On-shelf availability of 5 kg atta in June: share of 11:00 audits with status 'on shelf'.)
2 rows (columns: status, audits):
  empty | 2
  on shelf | 6
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; group by shelf audits.status; report status = shelf audits.status, audits = count of *.
Part 2: figures from the schema layer. (Plan covers: Book view: days in June with closing book stock above zero (a belief, Rule 1).)
28 rows (columns: date, book_on_hand_close):
  2026-06-01 | 58.0
  2026-06-02 | 22.0
  2026-06-03 | 64.0
  2026-06-04 | 36.0
  2026-06-05 | 52.0
  2026-06-06 | 27.0
  2026-06-07 | 43.0
  2026-06-08 | 34.0
  2026-06-09 | 78.0
  2026-06-10 | 56.0
  ... and 18 more
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date between 2026-06-01 and 2026-06-30; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 3: figures from the schema layer. (Plan covers: Books-and-tills view: June days with zero sales while the book shows stock are suspect days (Rule 2).)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 30.0 | 7950.0
  2026-06-02 | 36.0 | 9540.0
  2026-06-03 | 22.0 | 5830.0
  2026-06-04 | 28.0 | 7420.0
  2026-06-05 | 32.0 | 8480.0
  2026-06-06 | 25.0 | 6625.0
  2026-06-07 | 44.0 | 11660.0
  2026-06-08 | 9.0 | 2385.0
  2026-06-09 | 11.0 | 2915.0
  2026-06-10 | 22.0 | 5830.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.

## Q087: What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?

Answered from the schema layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Warehouse atta corrections at cost, net: the signed sum of value_at_cost_inr for the three atta sizes, 23 to 25 June only.)
warehouse_net_value_inr = 6672.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; report warehouse_net_value_inr = sum of dc stock adjustments.value_at_cost_inr.
Part 2: figures from the schema layer. (Plan covers: Warehouse atta corrections at cost, gross: the sum of the absolute value of each correction, so corrections of opposite sign do not cancel.)
warehouse_gross_value_inr = 22512.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; report warehouse_gross_value_inr = sum of abs(dc stock adjustments.value_at_cost_inr).
Part 3: not answered: the ontology layer refused the plan (each row of products can match several earlier rows, so sum over products would count rows more than once).
Part 4: not answered: the ontology layer refused the plan (each row of products can match several earlier rows, so sum over products would count rows more than once).

## Q088: Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Warehouse corrections with signs and cases; code pairs them with store counts (Rule 5, mirror-image corrections are one event).)
2 rows (columns: sku, slot, adjusted_ts, cases, reason):
  ATTA-WW-1KG | A-07-04 | 2026-06-23T14:20 | -16.0 | short pick: slot count variance
  ATTA-WW-5KG | A-07-03 | 2026-06-25T10:00 | 16.0 | cycle count variance
  How it was found: From warehouse (DC) stock adjustment records; report sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, adjusted_ts = dc stock adjustments.adjusted_ts, cases = dc stock adjustments.cases, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.
Part 2: figures from the schema layer. (Plan covers: Store count corrections in packs to pair against warehouse ones within 7 days; pack-to-case conversion uses products.case_units.)
21 rows (columns: sku, count_ts, adjustment):
  ATTA-WW-1KG | 2026-06-01T05:45 | -5.0
  ATTA-WW-10KG | 2026-06-01T05:45 | 1.0
  RICE-SM-5KG | 2026-06-01T05:45 | -2.0
  DAL-TOOR-1KG | 2026-06-01T05:45 | -2.0
  OIL-SUN-1L | 2026-06-01T05:45 | -5.0
  SUGAR-1KG | 2026-06-01T05:45 | -2.0
  MILK-TONED-500ML | 2026-06-01T05:45 | -26.0
  MILK-FC-500ML | 2026-06-01T05:45 | 15.0
  CURD-500G | 2026-06-01T05:45 | -3.0
  BREAD-WHITE-400G | 2026-06-01T05:45 | -5.0
  ... and 11 more
  How it was found: From stock count records; keep rows where stock counts.adjustment != 0; report sku = stock counts.sku, count_ts = stock counts.count_ts, adjustment = stock counts.adjustment; sorted by count_ts asc.

## Q089: Which goods receipts did not survive the next stock count within a week?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Receipts followed within 7 days by a store count of the booked product that found less than the book (negative adjustment); the earliest count per receipt is its next count.)
16 rows (columns: grn_id, line, received_ts, sku_booked, asn_sku, units_booked, count_ts, adjustment, days_after):
  GRN-260620 | 1 | 2026-06-20T06:22 | ATTA-WW-5KG | ATTA-WW-5KG | 72.0 | 2026-06-26T09:00 | -63.0 | 6.109722222201526
  GRN-260620 | 2 | 2026-06-20T06:22 | ATTA-WW-10KG | ATTA-WW-10KG | 24.0 | 2026-06-26T09:00 | -1.0 | 6.109722222201526
  GRN-260622 | 1 | 2026-06-22T06:12 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0 | 2026-06-26T09:00 | -63.0 | 4.116666666697711
  GRN-260622 | 1 | 2026-06-22T06:12 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0 | 2026-06-28T22:30 | -1.0 | 6.679166666697711
  GRN-260622 | 3 | 2026-06-22T06:12 | RICE-SM-5KG | RICE-SM-5KG | 56.0 | 2026-06-28T22:30 | -2.0 | 6.679166666697711
  GRN-260622 | 4 | 2026-06-22T06:12 | SUGAR-1KG | SUGAR-1KG | 50.0 | 2026-06-28T22:30 | -1.0 | 6.679166666697711
  GRN-260623 | 1 | 2026-06-23T06:18 | ATTA-WW-10KG | ATTA-WW-10KG | 26.0 | 2026-06-26T09:00 | -1.0 | 3.1124999998137355
  GRN-260623 | 3 | 2026-06-23T06:18 | OIL-SUN-1L | OIL-SUN-1L | 80.0 | 2026-06-28T22:30 | -8.0 | 5.6749999998137355
  GRN-260624 | 1 | 2026-06-24T06:07 | SUGAR-1KG | SUGAR-1KG | 40.0 | 2026-06-28T22:30 | -1.0 | 4.682638888712972
  GRN-260625 | 1 | 2026-06-25T06:13 | ATTA-WW-10KG | ATTA-WW-10KG | 28.0 | 2026-06-26T09:00 | -1.0 | 1.1159722222946584
  ... and 6 more
  How it was found: From goods-receipt line records; inner-join stock count records on goods receipts.sku_booked = stock counts.sku; keep rows where goods receipts.received_ts < stock counts.count_ts and days_between(goods receipts.received_ts, stock counts.count_ts) <= 7 and stock counts.adjustment < 0; report grn_id = goods receipts.grn_id, line = goods receipts.line, received_ts = goods receipts.received_ts, sku_booked = goods receipts.sku_booked, asn_sku = goods receipts.asn_sku, units_booked = goods receipts.units_booked, count_ts = stock counts.count_ts, adjustment = stock counts.adjustment, days_after = days_between(goods receipts.received_ts, stock counts.count_ts); sorted by received_ts asc, count_ts asc.

## Q090: Why was 5 kg atta off the shelf from 23 to 26 June?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Shelf audits of 5 kg atta 19-26 June; the cause is not recorded (cause), only evidence.)
3 rows (columns: audit_ts, status):
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-19 and 2026-06-26; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 2: figures from the schema layer. (Plan covers: Closing book stock of 5 kg atta 19-26 June (a belief, Rule 1).)
8 rows (columns: date, book_on_hand_close):
  2026-06-19 | 17.0
  2026-06-20 | 68.0
  2026-06-21 | 25.0
  2026-06-22 | 68.0
  2026-06-23 | 63.0
  2026-06-24 | 63.0
  2026-06-25 | 63.0
  2026-06-26 | 0.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date between 2026-06-19 and 2026-06-26; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 3: figures from the schema layer. (Plan covers: Goods receipts touching 5 kg atta 15-26 June: what was booked versus what the notice said.)
3 rows (columns: received_ts, shipment_id, line, sscc, asn_sku, sku_booked, units_booked):
  2026-06-17T06:03 | SHP-260617 | 1 | 029000010000010498 | ATTA-WW-5KG | ATTA-WW-5KG | 60.0
  2026-06-20T06:22 | SHP-260620 | 1 | 029000010000010528 | ATTA-WW-5KG | ATTA-WW-5KG | 72.0
  2026-06-22T06:12 | SHP-260622 | 1 | 029000010000010542 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0
  How it was found: From goods-receipt line records; keep rows where (goods receipts.sku_booked = 'ATTA-WW-5KG' or goods receipts.asn_sku = 'ATTA-WW-5KG') and day(goods receipts.received_ts) between 2026-06-15 and 2026-06-26; report received_ts = goods receipts.received_ts, shipment_id = goods receipts.shipment_id, line = goods receipts.line, sscc = goods receipts.sscc, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, units_booked = goods receipts.units_booked; sorted by received_ts asc.
Part 4: figures from the schema layer. (Plan covers: Warehouse atta adjustments 23-25 June (slot count variances) as evidence of a pick or slot mix-up.)
2 rows (columns: sku, slot, adjusted_ts, cases, reason):
  ATTA-WW-1KG | A-07-04 | 2026-06-23T14:20 | -16.0 | short pick: slot count variance
  ATTA-WW-5KG | A-07-03 | 2026-06-25T10:00 | 16.0 | cycle count variance
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] and day(dc stock adjustments.adjusted_ts) between 2026-06-23 and 2026-06-26; report sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, adjusted_ts = dc stock adjustments.adjusted_ts, cases = dc stock adjustments.cases, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q091: Is the 5 kg atta missing at the store theft?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Theft is a cause that is not recorded; store counts of 5 kg atta show the missing stock only.)
3 rows (columns: count_ts, trigger, book_before, counted, adjustment):
  2026-06-01T05:45 | scheduled full count | 36.0 | 36.0 | 0.0
  2026-06-26T09:00 | manager request after complaints | 63.0 | 0.0 | -63.0
  2026-06-28T22:30 | scheduled full count | 63.0 | 62.0 | -1.0
  How it was found: From stock count records; keep rows where stock counts.sku = 'ATTA-WW-5KG'; report count_ts = stock counts.count_ts, trigger = stock counts.trigger, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment.
Part 2: figures from the schema layer. (Plan covers: Warehouse corrections of 5 kg atta that may mirror the store loss (Rule 5).)
adjusted_ts = 2026-06-25T10:00; cases = 16.0; units = 64.0; reason = cycle count variance
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku = 'ATTA-WW-5KG'; report adjusted_ts = dc stock adjustments.adjusted_ts, cases = dc stock adjustments.cases, units = dc stock adjustments.units, reason = dc stock adjustments.reason.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q092: At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Hourly 5 kg atta sales on 23 June show when selling stopped; the cause is not recorded.)
5 rows (columns: hour, units):
  7 | 1.0
  9 | 1.0
  11 | 1.0
  14 | 1.0
  15 | 1.0
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-23'; group by hour(pos lines may.bill_ts); report hour = hour(pos lines may.bill_ts), units = sum of pos lines may.qty; sorted by hour asc.
Part 2: figures from the schema layer. (Plan covers: Which shipment and line brought 5 kg atta, with notice versus booked units.)
2 rows (columns: shipment_id, line, received_ts, asn_sku, asn_units, units_booked):
  SHP-260620 | 1 | 2026-06-20T06:22 | ATTA-WW-5KG | 72.0 | 72.0
  SHP-260622 | 1 | 2026-06-22T06:12 | ATTA-WW-5KG | 64.0 | 64.0
  How it was found: From goods-receipt line records; keep rows where goods receipts.sku_booked = 'ATTA-WW-5KG' and day(goods receipts.received_ts) between 2026-06-20 and 2026-06-23; report shipment_id = goods receipts.shipment_id, line = goods receipts.line, received_ts = goods receipts.received_ts, asn_sku = goods receipts.asn_sku, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked.
Part 3: figures from the schema layer. (Plan covers: What was picked for 5 kg atta shipments before 23 June (what was really on the truck).)
2 rows (columns: shipment_id, line, cases_ordered, cases_confirmed, slot):
  SHP-260620 | 1 | 18.0 | 18.0 | A-07-03
  SHP-260622 | 1 | 16.0 | 16.0 | A-07-03
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.sku = 'ATTA-WW-5KG' and day(dc pick confirmations.pick_ts) between 2026-06-20 and 2026-06-23; report shipment_id = dc pick confirmations.shipment_id, line = dc pick confirmations.line, cases_ordered = dc pick confirmations.cases_ordered, cases_confirmed = dc pick confirmations.cases_confirmed, slot = dc pick confirmations.slot.
Part 4: figures from the schema layer. (Plan covers: Shipping notice lines for 5 kg atta, to compare the notice with what was received (match on gtin, Rule 7).)
11 rows (columns: shipment_id, line, gtin, cases, units):
  SHP-260601 | 1 | 2900001001014 | 13.0 | 52.0
  SHP-260603 | 1 | 2900001001014 | 16.0 | 64.0
  SHP-260605 | 1 | 2900001001014 | 12.0 | 48.0
  SHP-260607 | 1 | 2900001001014 | 15.0 | 60.0
  SHP-260609 | 1 | 2900001001014 | 14.0 | 56.0
  SHP-260614 | 1 | 2900001001014 | 14.0 | 56.0
  SHP-260617 | 1 | 2900001001014 | 15.0 | 60.0
  SHP-260620 | 1 | 2900001001014 | 18.0 | 72.0
  SHP-260622 | 1 | 2900001001014 | 16.0 | 64.0
  SHP-260627 | 1 | 2900001001014 | 21.0 | 84.0
  ... and 1 more
  How it was found: From shipping-notice line records; keep rows where shipping notice lines.sku = 'ATTA-WW-5KG'; report shipment_id = shipping notice lines.shipment_id, line = shipping notice lines.line, gtin = shipping notice lines.gtin, cases = shipping notice lines.cases, units = shipping notice lines.units.

## Q093: Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Premise check: June forecast units of 5 kg atta; demand is not recorded (forecast_vs_demand), so the 13% can only be measured against sales.)
forecast_units = 637.32
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and forecasts.date between 2026-06-01 and 2026-06-30; report forecast_units = sum of forecasts.forecast_units_per_day.
Part 2: figures from the schema layer. (Plan covers: June recorded 5 kg atta sales; sales understate demand on empty-shelf days, so tuning to sales would chase the stock-out (Rule 4).)
units_sold = 567.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units_sold = sum of daily sales.units_sold.
Part 3: figures from the schema layer. (Plan covers: June shelf audits of 5 kg atta: empty days where sales are not demand.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q094: Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the 2.3 days of supply premise on 11 June from book stock and forecast; why no bags sold is not recorded.)
book_on_hand = 55.0; forecast_units_per_day = 23.82
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and forecasts.date = '2026-06-11'; report book_on_hand = forecasts.book_on_hand, forecast_units_per_day = forecasts.forecast_units_per_day.
Part 2: figures from the schema layer. (Plan covers: Checks that no bags sold on 11 June.)
units_sold = 1.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date = '2026-06-11'; report units_sold = daily sales.units_sold.
Part 3: figures from the schema layer. (Plan covers: Till lines by hour on 11 June show when sales of 5 kg atta stopped.)
hour = 9; units = 1.0
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-11'; group by hour(pos lines may.bill_ts); report hour = hour(pos lines may.bill_ts), units = sum of pos lines may.qty.

## Q095: Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Premise check: toned milk stock counts and their adjustments (is 55 missing?); no record identifies a cashier or shoplifter (person_identity, cause).)
2 rows (columns: sku, count_ts, trigger, book_before, counted, adjustment):
  MILK-TONED-500ML | 2026-06-01T05:45 | scheduled full count | 377.0 | 351.0 | -26.0
  MILK-TONED-500ML | 2026-06-28T22:30 | scheduled full count | 95.0 | 40.0 | -55.0
  How it was found: From stock count records; keep rows where stock counts.sku in ['MILK-TONED-500ML']; report sku = stock counts.sku, count_ts = stock counts.count_ts, trigger = stock counts.trigger, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment; sorted by count_ts asc.
Part 2: figures from the schema layer. (Plan covers: Toned milk write-offs in June: recorded losses that can explain a count gap without theft.)
2 rows (columns: reason, units):
  damaged | 5.0
  expired | 291.0
  How it was found: From write-off records; keep rows where write offs.sku = 'MILK-TONED-500ML' and write offs.date between 2026-06-01 and 2026-06-30; group by write offs.reason; report reason = write offs.reason, units = sum of write offs.units.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q096: If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Premise check: June toned milk revenue and cost at the single product cost (list_margin), for margin after waste.)
units_sold = 8649.0; revenue_inr = 224874.0; cost_inr = 24.7; price_inr = 26.0; cost_of_sales_inr = 213630.3
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.sku = 'MILK-TONED-500ML' and daily sales.date between 2026-06-01 and 2026-06-30; group by products.cost_inr, products.price_inr; report units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, cost_inr = products.cost_inr, price_inr = products.price_inr, cost_of_sales_inr = sum of daily sales.units_sold * products.cost_inr.
Part 2: figures from the ontology layer. (Plan covers: June toned milk write-offs valued at cost (waste side of margin after waste, Rule 6).)
units = 296.0; cost_inr = 24.7; waste_at_cost_inr = 7311.2
  How it was found: From write-off records; inner-join product records on write offs.sku = products.sku; keep rows where write offs.sku = 'MILK-TONED-500ML' and write offs.date between 2026-06-01 and 2026-06-30; group by products.cost_inr; report units = sum of write offs.units, cost_inr = products.cost_inr, waste_at_cost_inr = sum of write offs.units * products.cost_inr.
Part 3: figures from the schema layer. (Plan covers: June toned milk shelf audits; shoppers who leave without milk are not in the till records (absent_event), so the extra walk-outs cannot be counted.)
status = on shelf; audits = 8
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'MILK-TONED-500ML' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; group by shelf audits.status; report status = shelf audits.status, audits = count of *.
Part 4: figures from the schema layer. (Plan covers: June toned milk ordered units, the order a 5% cut would apply to.)
ordered_units = None; forecast_units = None
  How it was found: From forecast row records; keep rows where forecasts.sku = 'MILK-TONED-500ML' and forecasts.date between 2026-06-01 and 2026-06-30; report ordered_units = sum of forecasts.ordered_units, forecast_units = sum of forecasts.forecast_units_per_day.
Stand-ins used (not the real thing): list_margin (else): selling price minus the single cost per product is a list margin, not a real margin

## Q097: Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the premise: trucks that arrived on 22 June against their slot times; the timing check is on arrival only.)
shipment_id = SHP-260622; arrived_ts = 2026-06-22T06:12; slot_start = 2026-06-22T06:00; slot_end = 2026-06-22T06:30
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report shipment_id = shipments.shipment_id, arrived_ts = shipments.arrived_ts, slot_start = shipments.slot_start, slot_end = shipments.slot_end.
Part 2: figures from the schema layer. (Plan covers: Checks the premise: 5 kg atta receipts on 22 June, comparing the notice with the booking; a receipt line is not a physical count.)
grn_id = GRN-260622; asn_units = 64.0; units_booked = 64.0
  How it was found: From goods-receipt line records; keep rows where goods receipts.sku_booked = 'ATTA-WW-5KG' and day(goods receipts.received_ts) = '2026-06-22'; report grn_id = goods receipts.grn_id, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked.
Part 3: figures from the schema layer. (Plan covers: Theft is not recorded and no person is recorded; the net count gap in packs is the only loss figure, and it is not a theft figure.)
net_adjustment_packs = -64.0
  How it was found: From stock count records; keep rows where stock counts.sku = 'ATTA-WW-5KG'; report net_adjustment_packs = sum of stock counts.adjustment.
Part 4: figures from the schema layer. (Plan covers: Warehouse corrections for 5 kg atta, 23 to 25 June only; they are signed and their reasons are count variance or short pick, not theft.)
dc_adjustment_units = 64.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku = 'ATTA-WW-5KG'; report dc_adjustment_units = sum of dc stock adjustments.units.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q098: Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the premise that atta adjustments net to Rs 80 by summing value_at_cost_inr per atta SKU in dc-stock-adjustments-june, with the gross absolute value beside the net so offsetting corrections show (Rule 5).)
2 rows (columns: sku, net_value_inr, gross_value_inr, rows):
  ATTA-WW-1KG | -7920.0 | 7920.0 | 1
  ATTA-WW-5KG | 14592.0 | 14592.0 | 1
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; group by dc stock adjustments.sku; report sku = dc stock adjustments.sku, net_value_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_inr = sum of abs(dc stock adjustments.value_at_cost_inr), rows = count of *.
Part 2: figures from the schema layer. (Plan covers: The table records each correction's reason code (cycle count variance, short pick, slot count variance) but no cause or reason to investigate, so only these recorded rows are given as evidence.)
2 rows (columns: adjusted_ts, sku, slot, reason, cases, units, value_at_cost_inr):
  2026-06-23T14:20 | ATTA-WW-1KG | A-07-04 | short pick: slot count variance | -16.0 | -160.0 | -7920.0
  2026-06-25T10:00 | ATTA-WW-5KG | A-07-03 | cycle count variance | 16.0 | 64.0 | 14592.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, reason = dc stock adjustments.reason, cases = dc stock adjustments.cases, units = dc stock adjustments.units, value_at_cost_inr = dc stock adjustments.value_at_cost_inr; sorted by adjusted_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q099: On which dates in June 2026 did store.forecasts trigger an order (ordered_units > 0), and how many times did book_on_hand + on_order equal reorder_point versus fall below it?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Lists the June dates on which forecast rows triggered an order (ordered_units > 0), with how many products and units were ordered on each.)
25 rows (columns: date, products_ordered, ordered_units):
  2026-06-01 | 1 | 50.0
  2026-06-02 | 5 | 308.0
  2026-06-03 | 1 | 70.0
  2026-06-04 | 3 | 178.0
  2026-06-05 | 4 | 254.0
  2026-06-06 | 2 | 140.0
  2026-06-07 | 4 | 236.0
  2026-06-08 | 3 | 176.0
  2026-06-10 | 5 | 294.0
  2026-06-12 | 4 | 202.0
  ... and 15 more
  How it was found: From forecast row records; keep rows where forecasts.ordered_units > 0 and forecasts.date between 2026-06-01 and 2026-06-30; group by forecasts.date; report date = forecasts.date, products_ordered = count distinct of forecasts.sku, ordered_units = sum of forecasts.ordered_units; sorted by date asc.
Part 2: figures from the ontology layer. (Plan covers: Counts the June forecast rows where book_on_hand + on_order (added within each row, never summed across rows) equalled reorder_point, with the units ordered on those rows.)
times_equal_to_reorder_point = 2; units_ordered_on_those_rows = 80.0
  How it was found: From forecast row records; keep rows where forecasts.book_on_hand + forecasts.on_order = forecasts.reorder_point and forecasts.date between 2026-06-01 and 2026-06-30; report times_equal_to_reorder_point = count of *, units_ordered_on_those_rows = sum of forecasts.ordered_units.
Part 3: figures from the ontology layer. (Plan covers: Counts the June forecast rows where book_on_hand + on_order fell below reorder_point, with the units ordered on those rows.)
times_below_reorder_point = 69; units_ordered_on_those_rows = 4050.0
  How it was found: From forecast row records; keep rows where forecasts.book_on_hand + forecasts.on_order < forecasts.reorder_point and forecasts.date between 2026-06-01 and 2026-06-30; report times_below_reorder_point = count of *, units_ordered_on_those_rows = sum of forecasts.ordered_units.

## Q100: What was the longest streak of consecutive days in June 2026 with zero write-offs across all items in store.write_offs?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Lists every June date with at least one write-off across all items (write-offs are recorded 1 to 28 June), so the zero-write-off days are the dates missing from the list and the longest run of consecutive missing dates is the streak.)
22 rows (columns: date, write_off_rows, units_written_off):
  2026-06-01 | 1 | 1.0
  2026-06-03 | 1 | 1.0
  2026-06-05 | 1 | 1.0
  2026-06-08 | 1 | 4.0
  2026-06-09 | 2 | 2.0
  2026-06-10 | 1 | 1.0
  2026-06-11 | 2 | 2.0
  2026-06-12 | 1 | 48.0
  2026-06-13 | 2 | 26.0
  2026-06-14 | 1 | 42.0
  ... and 12 more
  How it was found: From write-off records; keep rows where write offs.date between 2026-06-01 and 2026-06-30; group by write offs.date; report date = write offs.date, write_off_rows = count of *, units_written_off = sum of write offs.units; sorted by date asc.

## Q101: For each fresh SKU in store.fresh_deliveries, what percentage of delivered units in June 2026 were later written off as 'expired' in store.write_offs?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Denominator of the expired share: units delivered on the fresh routes in June for each fresh product (Rule 6: fresh stock expires, so waste is read against what was delivered).)
4 rows (columns: sku, delivered_units):
  BREAD-WHITE-400G | 1708.0
  CURD-500G | 1996.0
  MILK-FC-500ML | 3144.0
  MILK-TONED-500ML | 9004.0
  How it was found: From fresh-delivery row records; keep rows where day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; group by fresh deliveries.sku; report sku = fresh deliveries.sku, delivered_units = sum of fresh deliveries.units; sorted by sku asc.
Part 2: figures from the schema layer. (Plan covers: Numerator: units written off as 'expired' in June for each product, so each fresh product's percentage is these units divided by its delivered units (planned apart because joining the two tables on product alone would repeat rows).)
2 rows (columns: sku, expired_units):
  MILK-FC-500ML | 198.0
  MILK-TONED-500ML | 291.0
  How it was found: From write-off records; keep rows where write offs.reason = 'expired' and write offs.date between 2026-06-01 and 2026-06-30; group by write offs.sku; report sku = write offs.sku, expired_units = sum of write offs.units; sorted by sku asc.

## Q102: On which dates in June 2026 did store.forecasts.book_on_hand differ from the previous day's store.inventory_book.book_on_hand_close?

Sorry, I'm not in a position to answer this from Store 014's records: the ontology layer refused the plan (cannot compare units with packs).

## Q103: Which SKUs in store.products never had a single write_offs row and never had a 'empty' row in store.shelf_audits during June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: All products in the store.)
11 rows (columns: sku, name):
  ATTA-WW-5KG | Whole wheat atta 5 kg
  ATTA-WW-1KG | Whole wheat atta 1 kg
  ATTA-WW-10KG | Whole wheat atta 10 kg
  RICE-SM-5KG | Sona masoori rice 5 kg
  DAL-TOOR-1KG | Toor dal 1 kg
  OIL-SUN-1L | Sunflower oil 1 L pouch
  SUGAR-1KG | Sugar 1 kg
  MILK-TONED-500ML | Toned milk 500 ml pouch
  MILK-FC-500ML | Full cream milk 500 ml pouch
  CURD-500G | Curd 500 g pouch
  ... and 1 more
  How it was found: From product records; report sku = products.sku, name = products.name.
Part 2: figures from the schema layer. (Plan covers: SKUs that did have at least one write-off row in June.)
7 rows (columns: sku, writeoff_rows):
  ATTA-WW-5KG | 3
  CURD-500G | 3
  DAL-TOOR-1KG | 1
  MILK-FC-500ML | 9
  MILK-TONED-500ML | 15
  RICE-SM-5KG | 2
  SUGAR-1KG | 1
  How it was found: From write-off records; group by write offs.sku; report sku = write offs.sku, writeoff_rows = count of *.
Part 3: figures from the schema layer. (Plan covers: SKUs that had at least one 'empty' shelf-audit row (audits 2026-06-02 to 2026-06-26); products missing from both lists are the answer.)
2 rows (columns: sku, empty_audits):
  ATTA-WW-5KG | 2
  SUGAR-1KG | 1
  How it was found: From shelf-audit row records; keep rows where shelf audits.status = 'empty'; group by shelf audits.sku; report sku = shelf audits.sku, empty_audits = count of *.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q104: On 28 June 2026, what was Store 014's total inventory value at cost—and should we trust that number for MILK-TONED-500ML and MILK-FC-500ML before the 22:30 stock count?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Values each product's closing book stock on 28 June at its single cost, so the total inventory value at cost is the sum of these rows, covering only the eleven recorded products and resting on book stock, which is a belief (Rule 1).)
11 rows (columns: sku, name, book_on_hand_close, cost_inr, value_at_cost_inr):
  RICE-SM-5KG | Sona masoori rice 5 kg | 49.0 | 301.0 | 14749.0
  ATTA-WW-5KG | Whole wheat atta 5 kg | 63.0 | 228.0 | 14364.0
  ATTA-WW-10KG | Whole wheat atta 10 kg | 27.0 | 431.0 | 11637.0
  ATTA-WW-1KG | Whole wheat atta 1 kg | 168.0 | 49.5 | 8316.0
  CURD-500G | Curd 500 g pouch | 94.0 | 29.5 | 2773.0
  OIL-SUN-1L | Sunflower oil 1 L pouch | 20.0 | 134.0 | 2680.0
  MILK-TONED-500ML | Toned milk 500 ml pouch | 95.0 | 24.7 | 2346.5
  DAL-TOOR-1KG | Toor dal 1 kg | 13.0 | 146.0 | 1898.0
  BREAD-WHITE-400G | White bread 400 g | 34.0 | 39.0 | 1326.0
  SUGAR-1KG | Sugar 1 kg | 24.0 | 42.0 | 1008.0
  ... and 1 more
  How it was found: From book-stock row records; inner-join product records on inventory book.sku = products.sku; keep rows where inventory book.date = '2026-06-28'; report sku = inventory book.sku, name = products.name, book_on_hand_close = inventory book.book_on_hand_close, cost_inr = products.cost_inr, value_at_cost_inr = inventory book.book_on_hand_close * products.cost_inr; sorted by value_at_cost_inr desc.
Part 2: figures from the schema layer. (Plan covers: Checks the 22:30 count on 28 June for the two milks, setting the book just before the count against the packs counted, the observation that can contradict the book figure (Rules 1 and 12).)
2 rows (columns: count_ts, sku, trigger, book_before, counted, adjustment):
  2026-06-28T22:30 | MILK-TONED-500ML | scheduled full count | 95.0 | 40.0 | -55.0
  2026-06-28T22:30 | MILK-FC-500ML | scheduled full count | 30.0 | 78.0 | 48.0
  How it was found: From stock count records; keep rows where stock counts.sku in ['MILK-TONED-500ML', 'MILK-FC-500ML'] and stock counts.count_ts between 2026-06-28T00:00 and 2026-06-28T23:59; report count_ts = stock counts.count_ts, sku = stock counts.sku, trigger = stock counts.trigger, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment; sorted by count_ts asc.
Part 3: figures from the schema layer. (Plan covers: Lists the June days up to 28 June on which either milk's closing book stock was negative, which no shelf can hold, as further evidence on whether the milk book figures can be trusted.)
6 rows (columns: date, sku, book_on_hand_close):
  2026-06-02 | MILK-FC-500ML | -5.0
  2026-06-09 | MILK-FC-500ML | -5.0
  2026-06-11 | MILK-FC-500ML | -15.0
  2026-06-12 | MILK-FC-500ML | -12.0
  2026-06-13 | MILK-FC-500ML | -14.0
  2026-06-20 | MILK-FC-500ML | -13.0
  How it was found: From book-stock row records; keep rows where inventory book.sku in ['MILK-TONED-500ML', 'MILK-FC-500ML'] and inventory book.date between 2026-06-01 and 2026-06-28 and inventory book.book_on_hand_close < 0; report date = inventory book.date, sku = inventory book.sku, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.

## Q105: Which store.shelf_audits rows prove that ATTA-WW-5KG was out of stock on Thursday 11 June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Shelf-audit rows for ATTA-WW-5KG from 9 to 12 June; audits are 11:00 snapshots on Tuesdays and Fridays, so this checks whether any audit exists on Thursday 11 June.)
2 rows (columns: audit_ts, sku, status):
  2026-06-09T11:00 | ATTA-WW-5KG | on shelf
  2026-06-12T11:00 | ATTA-WW-5KG | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.audit_ts between 2026-06-09 and 2026-06-12; report audit_ts = shelf audits.audit_ts, sku = shelf audits.sku, status = shelf audits.status; sorted by audit_ts asc.

## Q106: Why did store.forecasts order 0 units of ATTA-WW-5KG on 10, 11, and 12 June when the shelf was empty?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Checks that 0 units were ordered on 10, 11 and 12 June and shows what the order rule read, book stock plus stock on order against the reorder point, where book stock is a belief (Rule 1) and why it disagreed with the shelf is not recorded.)
3 rows (columns: date, book_on_hand, on_order, inventory_position, reorder_point, order_up_to, forecast_units_per_day, ordered_units):
  2026-06-10 | 56.0 | 0.0 | 56.0 | 39.0 | 89.0 | 24.57 | 0.0
  2026-06-11 | 55.0 | 0.0 | 55.0 | 40.0 | 88.0 | 23.82 | 0.0
  2026-06-12 | 55.0 | 0.0 | 55.0 | 40.0 | 86.0 | 22.96 | 0.0
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and forecasts.date in ['2026-06-10', '2026-06-11', '2026-06-12']; report date = forecasts.date, book_on_hand = forecasts.book_on_hand, on_order = forecasts.on_order, inventory_position = forecasts.book_on_hand + forecasts.on_order, reorder_point = forecasts.reorder_point, order_up_to = forecasts.order_up_to, forecast_units_per_day = forecasts.forecast_units_per_day, ordered_units = forecasts.ordered_units; sorted by date asc.
Part 2: figures from the schema layer. (Plan covers: Checks the empty-shelf premise with the ATTA-WW-5KG audits on Tuesday 9 and Friday 12 June, as audits run only on Tuesdays and Fridays at 11:00 and 10 and 11 June were not audited.)
2 rows (columns: audit_ts, status):
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-09 and 2026-06-12; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 3: figures from the schema layer. (Plan covers: Recorded sales of ATTA-WW-5KG on 10 to 12 June, since no sales while the book shows stock is a sign the shelf was empty (Rule 2).)
3 rows (columns: date, units_sold):
  2026-06-10 | 22.0
  2026-06-11 | 1.0
  2026-06-12 | 0.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-10 and 2026-06-12; report date = daily sales.date, units_sold = daily sales.units_sold; sorted by date asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q107: Which SKU had the highest shrink in June 2026—and does that mean it had the most theft?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Net hand-count adjustment per SKU in stock-counts-june (packs), most negative first, as one shrink measure.)
11 rows (columns: sku, adj_packs):
  MILK-TONED-500ML | -81.0
  ATTA-WW-5KG | -64.0
  OIL-SUN-1L | -13.0
  CURD-500G | -6.0
  BREAD-WHITE-400G | -5.0
  RICE-SM-5KG | -4.0
  SUGAR-1KG | -3.0
  DAL-TOOR-1KG | -2.0
  ATTA-WW-10KG | 0.0
  MILK-FC-500ML | 63.0
  ... and 1 more
  How it was found: From stock count records; group by stock counts.sku; report sku = stock counts.sku, adj_packs = sum of stock counts.adjustment; sorted by adj_packs asc.
Part 2: figures from the schema layer. (Plan covers: Write-off units per SKU and reason (damaged, expired) in write-offs-june, a second shrink measure that shows the damage and expiry part.)
8 rows (columns: sku, reason, units):
  MILK-TONED-500ML | expired | 291.0
  MILK-FC-500ML | expired | 198.0
  MILK-TONED-500ML | damaged | 5.0
  ATTA-WW-5KG | damaged | 3.0
  CURD-500G | damaged | 3.0
  RICE-SM-5KG | damaged | 2.0
  DAL-TOOR-1KG | damaged | 1.0
  SUGAR-1KG | damaged | 1.0
  How it was found: From write-off records; group by write offs.sku, write offs.reason; report sku = write offs.sku, reason = write offs.reason, units = sum of write offs.units; sorted by units desc.
Part 3: figures from the schema layer. (Plan covers: Theft is not recorded: no table holds a theft or cause code, so only the count triggers (manager request after complaints, scheduled full count) are shown beside the adjustments.)
2 rows (columns: trigger, adj_packs):
  manager request after complaints | 93.0
  scheduled full count | -55.0
  How it was found: From stock count records; group by stock counts.trigger; report trigger = stock counts.trigger, adj_packs = sum of stock counts.adjustment.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q108: Sum store.inventory_book.book_on_hand_close across all days in June for ATTA-WW-5KG to get total monthly stock.

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Daily closing book stock for ATTA-WW-5KG; stock levels are not additive, so they are listed per day and never summed.)
28 rows (columns: date, book_on_hand_close):
  2026-06-01 | 58.0
  2026-06-02 | 22.0
  2026-06-03 | 64.0
  2026-06-04 | 36.0
  2026-06-05 | 52.0
  2026-06-06 | 27.0
  2026-06-07 | 43.0
  2026-06-08 | 34.0
  2026-06-09 | 78.0
  2026-06-10 | 56.0
  ... and 18 more
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG'; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.

## Q109: Why did store.stock_counts show a +157 adjustment for ATTA-WW-1KG on 26 June when the warehouse mis-picked 160 packs?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: The 26 June hand count of ATTA-WW-1KG (book before, counted, adjustment, trigger); the reason for the +157 is not recorded and the 160-pack mis-pick premise is checked in the other parts.)
count_ts = 2026-06-26T09:00; book_before = 106.0; counted = 263.0; adjustment = 157.0; trigger = manager request after complaints
  How it was found: From stock count records; keep rows where stock counts.sku = 'ATTA-WW-1KG' and stock counts.count_ts between 2026-06-26T00:00 and 2026-06-26T23:59; report count_ts = stock counts.count_ts, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment, trigger = stock counts.trigger.
Part 2: figures from the schema layer. (Plan covers: Warehouse (DC) stock adjustments for ATTA-WW-1KG (2026-06-23 to 2026-06-25 only), to check the claimed warehouse mis-pick.)
adjusted_ts = 2026-06-23T14:20; slot = A-07-04; units = -160.0; cases = -16.0; reason = short pick: slot count variance
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku = 'ATTA-WW-1KG'; report adjusted_ts = dc stock adjustments.adjusted_ts, slot = dc stock adjustments.slot, units = dc stock adjustments.units, cases = dc stock adjustments.cases, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.
Part 3: figures from the schema layer. (Plan covers: ATTA-WW-1KG pick lines where cases confirmed differ from cases ordered.)
No rows matched.
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.sku = 'ATTA-WW-1KG' and dc pick confirmations.cases_confirmed != dc pick confirmations.cases_ordered; report shipment_id = dc pick confirmations.shipment_id, line = dc pick confirmations.line, pick_ts = dc pick confirmations.pick_ts, cases_ordered = dc pick confirmations.cases_ordered, cases_confirmed = dc pick confirmations.cases_confirmed, slot = dc pick confirmations.slot; sorted by pick_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q110: Why did store.inventory_book show negative closing stock for MILK-FC-500ML on 6 days in June 2026—did Store 014 sell milk it didn't have?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the premise by listing the June days on which MILK-FC-500ML's closing book stock was negative (the question says 6 days).)
6 rows (columns: date, book_on_hand_close):
  2026-06-02 | -5.0
  2026-06-09 | -5.0
  2026-06-11 | -15.0
  2026-06-12 | -12.0
  2026-06-13 | -14.0
  2026-06-20 | -13.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'MILK-FC-500ML' and inventory book.date between 2026-06-01 and 2026-06-30 and inventory book.book_on_hand_close < 0; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 2: figures from the ontology layer. (Plan covers: A store cannot sell packs it does not hold, so a negative book points to a record error whose cause is not recorded, and this checks whether the packs the till sold as MILK-FC-500ML in June carried that product's own pack code (Rule 7: an i)
sku_recorded_by_till = MILK-FC-500ML; sku_of_pack_code = MILK-FC-500ML; units_sold = 2916.0; till_lines = 2756
  How it was found: From till line records; left-join product records on pos lines may.gtin_scanned = products.gtin; keep rows where pos lines may.sku_scanned = 'MILK-FC-500ML' and day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; group by pos lines may.sku_scanned, products.sku; report sku_recorded_by_till = pos lines may.sku_scanned, sku_of_pack_code = products.sku, units_sold = sum of pos lines may.qty, till_lines = count of *.
Part 3: figures from the schema layer. (Plan covers: Units of MILK-FC-500ML delivered on the fresh routes in June, to set against the units the till sold.)
delivery_rows = 28; units_delivered = 3144.0
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'MILK-FC-500ML' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report delivery_rows = count of *, units_delivered = sum of fresh deliveries.units.
Part 4: figures from the schema layer. (Plan covers: June hand counts of MILK-FC-500ML, the physical observation that can contradict the book (Rules 1 and 12).)
2 rows (columns: count_ts, trigger, book_before, counted, adjustment):
  2026-06-01T05:45 | scheduled full count | 94.0 | 109.0 | 15.0
  2026-06-28T22:30 | scheduled full count | 30.0 | 78.0 | 48.0
  How it was found: From stock count records; keep rows where stock counts.sku = 'MILK-FC-500ML' and day(stock counts.count_ts) between 2026-06-01 and 2026-06-30; report count_ts = stock counts.count_ts, trigger = stock counts.trigger, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment; sorted by count_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q111: Which exact fresh delivery batch (use_by date) was each unit of MILK-TONED-500ML in store.pos_lines sold from?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Till lines do not record which delivery batch or use-by date a pack came from, so the batch of each unit sold is not recorded, and this lists the MILK-TONED-500ML fresh deliveries with their use-by dates as the batches that were available.)
28 rows (columns: delivery_ts, route, units, use_by):
  2026-06-01T05:30 | R-07 | 315.0 | 2026-06-02
  2026-06-02T05:30 | R-07 | 315.0 | 2026-06-03
  2026-06-03T05:30 | R-07 | 315.0 | 2026-06-04
  2026-06-04T05:30 | R-07 | 315.0 | 2026-06-05
  2026-06-05T05:30 | R-07 | 315.0 | 2026-06-06
  2026-06-06T05:30 | R-07 | 338.0 | 2026-06-07
  2026-06-07T05:30 | R-07 | 338.0 | 2026-06-08
  2026-06-08T05:30 | R-07 | 315.0 | 2026-06-09
  2026-06-09T05:30 | R-07 | 315.0 | 2026-06-10
  2026-06-10T05:30 | R-07 | 315.0 | 2026-06-11
  ... and 18 more
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'MILK-TONED-500ML'; report delivery_ts = fresh deliveries.delivery_ts, route = fresh deliveries.route, units = fresh deliveries.units, use_by = fresh deliveries.use_by; sorted by delivery_ts asc.
Part 2: figures from the schema layer. (Plan covers: MILK-TONED-500ML units sold at the till per day, to set against those batches, where assigning a sale to a batch (for example first in, first out) would be an assumption, not a record.)
56 rows (columns: sale_date, units_sold):
  2026-05-04 | 253.0
  2026-05-05 | 388.0
  2026-05-06 | 224.0
  2026-05-07 | 395.0
  2026-05-08 | 191.0
  2026-05-09 | 427.0
  2026-05-10 | 286.0
  2026-05-11 | 357.0
  2026-05-12 | 180.0
  2026-05-13 | 296.0
  ... and 46 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'MILK-TONED-500ML'; group by day(pos lines may.bill_ts); report sale_date = day(pos lines may.bill_ts), units_sold = sum of pos lines may.qty; sorted by sale_date asc.

## Q112: Which shift (morning or evening) had more shelf stockouts at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Shifts are not recorded and shelves are audited only at 11:00 on Tuesdays and Fridays, so an evening stockout is never observed, and this counts the June audits that found a shelf 'empty', by audit hour, as the only recorded stockout eviden)
audit_hour = 11; empty_audits = 3; products_found_empty = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.status = 'empty' and day(shelf audits.audit_ts) between 2026-06-01 and 2026-06-30; group by hour(shelf audits.audit_ts); report audit_hour = hour(shelf audits.audit_ts), empty_audits = count of *, products_found_empty = count distinct of shelf audits.sku.

## Q113: Which aisle or shelf bay inside Store 014 holds OIL-SUN-1L?

Answered from the knowledge layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Only the warehouse (DC) slot of OIL-SUN-1L is recorded as a stand-in; the in-store aisle or shelf bay is not recorded.)
sku = OIL-SUN-1L; name = Sunflower oil 1 L pouch; dc_slot = B-05-01
  How it was found: From product records; keep rows where products.sku = 'OIL-SUN-1L'; report sku = products.sku, name = products.name, dc_slot = products.dc_slot.

## Q114: How many days of safety stock is built into Store 014's reorder_point formula?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: The reorder-point formula, its safety-stock term and the lead time are not recorded, so this gives each product's reorder point in days of forecast (reorder_point divided by forecast_units_per_day), a stand-in that bundles lead-time cover a)
7 rows (columns: sku, avg_reorder_point_days, min_reorder_point_days, max_reorder_point_days, avg_sigma, avg_forecast_units_per_day):
  ATTA-WW-10KG | 1.7908407355894995 | 1.6022620169651274 | 1.9313304721030042 | 4.395714285714286 | 9.82642857142857
  ATTA-WW-1KG | 1.717967227449669 | 1.510892480674631 | 1.9836639439906651 | 11.922857142857143 | 28.525357142857143
  ATTA-WW-5KG | 1.7593126831928814 | 1.4735980352026197 | 2.127659574468085 | 10.008928571428571 | 22.761428571428574
  DAL-TOOR-1KG | 1.6982607062368882 | 1.5330188679245282 | 1.7770597738287561 | 7.6450000000000005 | 18.723214285714285
  OIL-SUN-1L | 1.4700303757327031 | 1.4230769230769231 | 1.5233949945593035 | 7.396071428571429 | 26.865000000000002
  RICE-SM-5KG | 1.4935440387555097 | 1.4001806684733513 | 1.5909090909090908 | 6.265357142857143 | 22.221785714285716
  SUGAR-1KG | 1.6662434471030274 | 1.555793991416309 | 1.7603634298693924 | 7.016785714285715 | 18.3
  How it was found: From forecast row records; keep rows where forecasts.forecast_units_per_day > 0; group by forecasts.sku; report sku = forecasts.sku, avg_reorder_point_days = avg of forecasts.reorder_point / forecasts.forecast_units_per_day, min_reorder_point_days = min of forecasts.reorder_point / forecasts.forecast_units_per_day, max_reorder_point_days = max of forecasts.reorder_point / forecasts.forecast_units_per_day, avg_sigma = avg of forecasts.sigma, avg_forecast_units_per_day = avg of forecasts.forecast_units_per_day; sorted by sku asc.

## Q115: Were Store 014's fresh products kept cold in transit in June 2026?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: The only recorded transit facts for fresh products are route, delivery time, crates and use-by; no temperature or cold-chain reading exists, so the cold condition in transit is not recorded.)
112 rows (columns: sku, route, delivery_ts, crates, use_by):
  MILK-TONED-500ML | R-07 | 2026-06-01T05:30 | 14.0 | 2026-06-02
  MILK-FC-500ML | R-07 | 2026-06-01T05:30 | 5.0 | 2026-06-02
  CURD-500G | R-07 | 2026-06-01T05:30 | 3.0 | 2026-06-04
  BREAD-WHITE-400G | R-12 | 2026-06-01T05:30 | 5.0 | 2026-06-04
  MILK-TONED-500ML | R-07 | 2026-06-02T05:30 | 14.0 | 2026-06-03
  MILK-FC-500ML | R-07 | 2026-06-02T05:30 | 5.0 | 2026-06-03
  CURD-500G | R-07 | 2026-06-02T05:30 | 3.0 | 2026-06-05
  BREAD-WHITE-400G | R-12 | 2026-06-02T05:30 | 5.0 | 2026-06-05
  MILK-TONED-500ML | R-07 | 2026-06-03T05:30 | 14.0 | 2026-06-04
  MILK-FC-500ML | R-07 | 2026-06-03T05:30 | 5.0 | 2026-06-04
  ... and 102 more
  How it was found: From fresh-delivery row records; report sku = fresh deliveries.sku, route = fresh deliveries.route, delivery_ts = fresh deliveries.delivery_ts, crates = fresh deliveries.crates, use_by = fresh deliveries.use_by.

## Q116: How much does a delivery cost per case or per pallet?

Sorry, I'm not in a position to answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## Q117: How many truck shipments arrived from the warehouse in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the warehouse (DC) truck shipments with an arrival time in June 2026 (shipments are recorded 1 to 28 June).)
shipments_arrived = 25
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) between 2026-06-01 and 2026-06-30; report shipments_arrived = count distinct of shipments.shipment_id.

## Q118: How many distinct store orders (distinct order ids, each of which can have several lines) were sent to the warehouse in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the distinct store order ids created in June 2026 (orders are recorded 1 to 27 June), with their number of lines.)
distinct_orders = 24; order_lines = 68
  How it was found: From store order line records; keep rows where day(store orders.created_ts) between 2026-06-01 and 2026-06-30; report distinct_orders = count distinct of store orders.order_id, order_lines = count of *.

## Q119: How many shipments arrived from the warehouse in May 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: May is outside this table (June only)

## Q120: How many pallets arrived from the warehouse in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Sums shipments-june pallets (pallets, additive) for trucks that arrived in June.)
pallets_on_trucks = 30.0
  How it was found: From shipment records; keep rows where shipments.arrived_ts between 2026-06-01 and 2026-06-30T23:59; report pallets_on_trucks = sum of shipments.pallets.
Part 2: figures from the schema layer. (Plan covers: Counts distinct pallet labels (sscc) in pallets-june, checking the first count against the pallet rows.)
pallet_labels = 30
  How it was found: From pallet records; report pallet_labels = count distinct of pallets.sscc.

## Q121: How many units in total did Store 014 order from the warehouse in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total units, with cases, on the store's June 2026 orders to the warehouse (DC), which are recorded 1 to 27 June.)
units_ordered = 3940.0; cases_ordered = 689.0
  How it was found: From store order line records; keep rows where day(store orders.created_ts) between 2026-06-01 and 2026-06-30; report units_ordered = sum of store orders.units, cases_ordered = sum of store orders.cases.

## Q122: How many shipments arrived at Store 014 in July 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: july is outside the records

## Q123: What made the shipment on 12 June 2026 arrive late?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Dispatch, slot and arrival times of the 12 June shipment, to check whether it was late; the cause of lateness is not recorded.)
No rows matched.
  How it was found: From shipment records; keep rows where shipments.arrived_ts between 2026-06-12T00:00 and 2026-06-12T23:59; report shipment_id = shipments.shipment_id, dispatched_ts = shipments.dispatched_ts, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts.

## Q124: How many shipments were due at Store 014 in June 2026 but never turned up?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June shipments on record that have no arrival time, while a delivery that was due but never created as a shipment is not recorded at all.)
shipments_without_arrival = 0
  How it was found: From shipment records; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30 and shipments.arrived_ts is empty; report shipments_without_arrival = count of *.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q125: How many shipments arrived late in June 2026 because of traffic?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: The reason for lateness, traffic or anything else, is not recorded, so this counts the June shipments that arrived after their slot end, whatever the cause.)
late_shipments = 2
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) between 2026-06-01 and 2026-06-30 and shipments.arrived_ts > shipments.slot_end; report late_shipments = count of *.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q126: How many shipments were dispatched before 05:00 in June 2026?

Answered from the schema layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June 2026 shipments whose dispatch time was before 05:00.)
dispatched_before_0500 = 25
  How it was found: From shipment records; keep rows where day(shipments.dispatched_ts) between 2026-06-01 and 2026-06-30 and hour(shipments.dispatched_ts) < 5; report dispatched_before_0500 = count of *.

## Q127: How many goods-receipt lines in June 2026 were booked for 5 kg atta?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June goods-receipt lines booked to whole wheat atta 5 kg (ATTA-WW-5KG), which were booked by pallet-label scan against the shipping notice rather than by looking at the packs.)
receipt_lines = 11; units_booked = 660.0
  How it was found: From goods-receipt line records; keep rows where goods receipts.sku_booked = 'ATTA-WW-5KG' and day(goods receipts.received_ts) between 2026-06-01 and 2026-06-30; report receipt_lines = count of *, units_booked = sum of goods receipts.units_booked.

## Q128: How many pallets did shipment SHP-260601 carry?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Reads the pallets field of shipment SHP-260601 in shipments-june.)
pallets = 1.0
  How it was found: From shipment records; keep rows where shipments.shipment_id = 'SHP-260601'; report pallets = shipments.pallets.
Part 2: figures from the schema layer. (Plan covers: Counts pallet labels on SHP-260601 in pallets-june, to check the pallets field against the pallet rows.)
pallet_labels = 1
  How it was found: From pallet records; keep rows where pallets.shipment_id = 'SHP-260601'; report pallet_labels = count distinct of pallets.sscc.

## Q129: What was the total number of units on the shipping notices in June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total units on the June shipping-notice lines.)
notice_units = 4012.0
  How it was found: From shipping-notice line records; report notice_units = sum of shipping notice lines.units.

## Q130: How many pallets were left on the truck instead of being unloaded in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Unloading is not recorded pallet by pallet, so this counts the pallets on shipments that arrived in June whose pallet label (SSCC) has no goods-receipt line, the only recorded sign of a pallet that was not taken in.)
pallets_with_no_receipt = 0
  How it was found: From pallet records; inner-join shipment records on pallets.shipment_id = shipments.shipment_id; left-join goods-receipt line records on pallets.sscc = goods receipts.sscc; keep rows where day(shipments.arrived_ts) between 2026-06-01 and 2026-06-30 and goods receipts.sscc is empty; report pallets_with_no_receipt = count distinct of pallets.sscc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q131: How many shipments arrived on time in June 2026 according to the drivers?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Drivers' own accounts are not recorded and no table identifies a driver, so this counts the June shipments whose recorded arrival time falls inside their slot (on time as in the OTIF per delivery definition).)
on_time_shipments = 23
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) between 2026-06-01 and 2026-06-30 and shipments.arrived_ts >= shipments.slot_start and shipments.arrived_ts <= shipments.slot_end; report on_time_shipments = count of *.

## Q132: What was the total number of crates delivered on route R-12 in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total crates delivered on fresh route R-12 in June 2026.)
total_crates = 152.0
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.route = 'R-12' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report total_crates = sum of fresh deliveries.crates.

## Q133: How many units of curd were never delivered on route R-07 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Units that were due but never delivered are not recorded, as nothing records what a fresh route was meant to bring, so this gives the curd units actually delivered on route R-07 in June and on how many days.)
units_delivered = 1996.0; delivery_rows = 28; delivery_days = 28
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'CURD-500G' and fresh deliveries.route = 'R-07' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report units_delivered = sum of fresh deliveries.units, delivery_rows = count of *, delivery_days = count distinct of day(fresh deliveries.delivery_ts).
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q134: How many shipments arrived in June 2026 and which was the most delayed driver?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts the warehouse shipments with an arrival time in June 2026.)
shipments_arrived = 25
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) between 2026-06-01 and 2026-06-30; report shipments_arrived = count distinct of shipments.shipment_id.
Part 2: figures from the ontology layer. (Plan covers: Drivers are not recorded, only the vehicle, so this ranks June's late shipments by how long after slot end they arrived, with the vehicle as the nearest stand-in.)
2 rows (columns: shipment_id, vehicle, slot_end, arrived_ts, hours_after_slot_end):
  SHP-260611 | TRK-07 | 2026-06-11T06:30 | 2026-06-11T08:21 | 1.8500000014901161
  SHP-260615 | TRK-07 | 2026-06-15T06:30 | 2026-06-15T08:08 | 1.6333333253860474
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) between 2026-06-01 and 2026-06-30 and shipments.arrived_ts > shipments.slot_end; report shipment_id = shipments.shipment_id, vehicle = shipments.vehicle, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts, hours_after_slot_end = hours_between(shipments.slot_end, shipments.arrived_ts); sorted by hours_after_slot_end desc.

## Q135: What was the total weight in kg on the pallet notices in June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total of notice_kg (weight stated on the shipping notice, not weighed) over June pallets.)
notice_kg_total = 12426.0
  How it was found: From pallet records; report notice_kg_total = sum of pallets.notice_kg.

## Q136: What was the total number of units of curd delivered in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total units of curd (CURD-500G) delivered on the fresh routes in June 2026.)
units_delivered = 1996.0
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'CURD-500G' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report units_delivered = sum of fresh deliveries.units.

## Q137: How many of June's deliveries arrived inside their 06:00–06:30 slot?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts June deliveries whose arrived_ts falls between slot_start and slot_end, the on-time test per Rule 8.)
inside_slot = 23
  How it was found: From shipment records; keep rows where shipments.arrived_ts >= shipments.slot_start and shipments.arrived_ts <= shipments.slot_end; report inside_slot = count distinct of shipments.shipment_id.
Part 2: figures from the schema layer. (Plan covers: Groups shipments-june by slot_start and slot_end to check the slot window is 06:00 to 06:30.)
25 rows (columns: slot_start, slot_end, shipments):
  2026-06-01T06:00 | 2026-06-01T06:30 | 1
  2026-06-02T06:00 | 2026-06-02T06:30 | 1
  2026-06-03T06:00 | 2026-06-03T06:30 | 1
  2026-06-04T06:00 | 2026-06-04T06:30 | 1
  2026-06-05T06:00 | 2026-06-05T06:30 | 1
  2026-06-06T06:00 | 2026-06-06T06:30 | 1
  2026-06-07T06:00 | 2026-06-07T06:30 | 1
  2026-06-08T06:00 | 2026-06-08T06:30 | 1
  2026-06-09T06:00 | 2026-06-09T06:30 | 1
  2026-06-11T06:00 | 2026-06-11T06:30 | 1
  ... and 15 more
  How it was found: From shipment records; group by shipments.slot_start, shipments.slot_end; report slot_start = shipments.slot_start, slot_end = shipments.slot_end, shipments = count of *.

## Q138: How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the 30-pallet premise and how many pallets were weighed at dispatch by counting pallets per weight-check status (the pallet table covers 1 to 30 June).)
weight_check = not weighed; pallets = 30
  How it was found: From pallet records; group by pallets.weight_check; report weight_check = pallets.weight_check, pallets = count distinct of pallets.sscc.
Part 2: figures from the schema layer. (Plan covers: How the June pallets were checked at receipt, counting pallets and lines per receipt method, where a case-by-case scan would show as a method of its own.)
receipt_method = pallet label (SSCC) scan against the shipping notice; pallets = 30; receipt_lines = 70
  How it was found: From goods-receipt line records; keep rows where day(goods receipts.received_ts) between 2026-06-01 and 2026-06-30; group by goods receipts.receipt_method; report receipt_method = goods receipts.receipt_method, pallets = count distinct of goods receipts.sscc, receipt_lines = count of *.

## Q139: What was the case fill rate across June's store orders according to the shipping notices?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Fill rate (in full, by cases) per Definitions: this is the denominator, cases ordered on store orders created in June (store-orders-june covers to 27 June); code divides by the numerator in the next part.)
cases_ordered = 689.0
  How it was found: From store order line records; keep rows where store orders.created_ts between 2026-06-01 and 2026-06-30T23:59; report cases_ordered = sum of store orders.cases.
Part 2: figures from the ontology layer. (Plan covers: Numerator of the fill rate: shipping-notice cases for June-created store orders, joined on order_id and sku, so notice lines of orders from another period are excluded.)
cases_on_notice = 686.0
  How it was found: From shipping-notice line records; inner-join store order line records on shipping notice lines.order_id = store orders.order_id and shipping notice lines.sku = store orders.sku; keep rows where store orders.created_ts between 2026-06-01 and 2026-06-30T23:59; report cases_on_notice = sum of shipping notice lines.cases.

## Q140: Was the 22 June delivery on time and in full?

Answered from the ontology layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: OTIF per delivery for the 22 June shipment: arrival against slot (on time) and cases confirmed against cases ordered over its pick lines (in full).)
1 rows (columns: shipment_id, slot_start, slot_end, arrived_ts, pick_lines, cases_ordered, cases_confirmed):
  SHP-260622 | 2026-06-22T06:00 | 2026-06-22T06:30 | 2026-06-22T06:12 | 4 | 44.0 | 44.0
  How it was found: From pick confirmation records; inner-join shipment records on dc pick confirmations.shipment_id = shipments.shipment_id; keep rows where shipments.arrived_ts between 2026-06-22T00:00 and 2026-06-22T23:59; group by shipments.shipment_id, shipments.slot_start, shipments.slot_end, shipments.arrived_ts; report shipment_id = shipments.shipment_id, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts, pick_lines = count of *, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed.

## Q141: What was Store 014's OTIF from the warehouse in June?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: OTIF per delivery, the denominator: every warehouse delivery due in June.)
june_deliveries = 25
  How it was found: From shipment records; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30; report june_deliveries = count of *.
Part 2: figures from the ontology layer. (Plan covers: OTIF per delivery, the failures: June deliveries that arrived outside slot_start to slot_end or have a pick line whose cases_confirmed differs from cases_ordered, so OTIF is deliveries minus these, divided by deliveries, with in full read f)
3 rows (columns: shipment_id, slot_start, slot_end, arrived_ts, largest_short_cases, largest_over_cases):
  SHP-260611 | 2026-06-11T06:00 | 2026-06-11T06:30 | 2026-06-11T08:21 | -1.0 | 0.0
  SHP-260613 | 2026-06-13T06:00 | 2026-06-13T06:30 | 2026-06-13T06:16 | -2.0 | -2.0
  SHP-260615 | 2026-06-15T06:00 | 2026-06-15T06:30 | 2026-06-15T08:08 | 0.0 | 0.0
  How it was found: From shipment records; left-join pick confirmation records on shipments.shipment_id = dc pick confirmations.shipment_id; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30 and (shipments.arrived_ts is empty or shipments.arrived_ts < shipments.slot_start or shipments.arrived_ts > shipments.slot_end or dc pick confirmations.cases_confirmed != dc pick confirmations.cases_ordered); group by shipments.shipment_id, shipments.slot_start, shipments.slot_end, shipments.arrived_ts; report shipment_id = shipments.shipment_id, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts, largest_short_cases = min of dc pick confirmations.cases_confirmed - dc pick confirmations.cases_ordered, largest_over_cases = max of dc pick confirmations.cases_confirmed - dc pick confirmations.cases_ordered; sorted by shipment_id asc.

## Q142: Which delivery, pallet (SSCC), and line should the store raise a claim against?

Answered from the schema layer (1 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Goods-receipt lines where the ASN and the booking differ on SKU or units, giving the delivery, pallet and line.)
No rows matched.
  How it was found: From goods-receipt line records; keep rows where (goods receipts.asn_sku != goods receipts.sku_booked or goods receipts.asn_units != goods receipts.units_booked); report shipment_id = goods receipts.shipment_id, sscc = goods receipts.sscc, line = goods receipts.line, grn_id = goods receipts.grn_id, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked.
Part 2: figures from the schema layer. (Plan covers: Short pick lines are only evidence; whether the store should raise a claim is a decision that no record holds.)
2 rows (columns: shipment_id, line, sku, order_id):
  SHP-260611 | 3 | DAL-TOOR-1KG | SO-260610
  SHP-260613 | 4 | SUGAR-1KG | SO-260612
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed < dc pick confirmations.cases_ordered; report shipment_id = dc pick confirmations.shipment_id, line = dc pick confirmations.line, sku = dc pick confirmations.sku, order_id = dc pick confirmations.order_id.

## Q143: Which pallet on the 22 June shipment failed its dispatch weight check?

Answered from the ontology layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Checks the premise by listing the pallets on the 22 June shipment with their dispatch weight-check status, where a pallet marked 'not weighed' had no weight check to fail.)
2 rows (columns: shipment_id, sscc, cases, notice_kg, weight_check):
  SHP-260622 | 029000010000010542 | 39.0 | 723.7 | not weighed
  SHP-260622 | 029000010000010559 | 5.0 | 73.5 | not weighed
  How it was found: From pallet records; inner-join shipment records on pallets.shipment_id = shipments.shipment_id; keep rows where (day(shipments.slot_start) = '2026-06-22' or day(shipments.arrived_ts) = '2026-06-22'); report shipment_id = pallets.shipment_id, sscc = pallets.sscc, cases = pallets.cases, notice_kg = pallets.notice_kg, weight_check = pallets.weight_check; sorted by sscc asc.

## Q144: If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Current dispatch weighing status of pallets; the future effect of weighing or case scanning on OTIF is not recorded and cannot be forecast from records.)
weight_check = not weighed; pallets = 30
  How it was found: From pallet records; group by pallets.weight_check; report weight_check = pallets.weight_check, pallets = count of *.
Part 2: figures from the schema layer. (Plan covers: Short-picked lines by how the pick was confirmed, as the recorded evidence of in-full failures.)
confirmed_by = slot label scan; short_lines = 2
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed < dc pick confirmations.cases_ordered; group by dc pick confirmations.confirmed_by; report confirmed_by = dc pick confirmations.confirmed_by, short_lines = count of *.

## Q145: What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: OTIF per delivery, the denominator: every warehouse delivery due in June, so the result can be checked against the offered 92%, 90%, 88% and 84%.)
june_deliveries = 25
  How it was found: From shipment records; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30; report june_deliveries = count of *.
Part 2: figures from the ontology layer. (Plan covers: OTIF per delivery, the failures: June deliveries that arrived outside slot_start to slot_end or have a pick line whose cases_confirmed differs from cases_ordered, so OTIF is deliveries minus these, divided by deliveries, with in full read f)
3 rows (columns: shipment_id, slot_start, slot_end, arrived_ts, largest_short_cases, largest_over_cases):
  SHP-260611 | 2026-06-11T06:00 | 2026-06-11T06:30 | 2026-06-11T08:21 | -1.0 | 0.0
  SHP-260613 | 2026-06-13T06:00 | 2026-06-13T06:30 | 2026-06-13T06:16 | -2.0 | -2.0
  SHP-260615 | 2026-06-15T06:00 | 2026-06-15T06:30 | 2026-06-15T08:08 | 0.0 | 0.0
  How it was found: From shipment records; left-join pick confirmation records on shipments.shipment_id = dc pick confirmations.shipment_id; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30 and (shipments.arrived_ts is empty or shipments.arrived_ts < shipments.slot_start or shipments.arrived_ts > shipments.slot_end or dc pick confirmations.cases_confirmed != dc pick confirmations.cases_ordered); group by shipments.shipment_id, shipments.slot_start, shipments.slot_end, shipments.arrived_ts; report shipment_id = shipments.shipment_id, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts, largest_short_cases = min of dc pick confirmations.cases_confirmed - dc pick confirmations.cases_ordered, largest_over_cases = max of dc pick confirmations.cases_confirmed - dc pick confirmations.cases_ordered; sorted by shipment_id asc.

## Q146: Which order_ids appear on warehouse.shipping_notice_lines in June 2026 but are missing from store.store_orders?

Answered from the ontology layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: Lists the order ids on June shipping-notice lines (placed in June by their shipment's dispatch time) that have no line at all in the store orders table, noting that store orders are recorded only for 1 to 27 June, so an order created outsid)
order_id = SO-260531; products_on_notice = 2; shipments = 1; first_dispatched_ts = 2026-06-01T04:30
  How it was found: From shipping-notice line records; left-join store order line records on shipping notice lines.order_id = store orders.order_id; left-join shipment records on shipping notice lines.shipment_id = shipments.shipment_id; keep rows where store orders.order_id is empty and (shipments.dispatched_ts is empty or day(shipments.dispatched_ts) between 2026-06-01 and 2026-06-30); group by shipping notice lines.order_id; report order_id = shipping notice lines.order_id, products_on_notice = count distinct of shipping notice lines.sku, shipments = count distinct of shipping notice lines.shipment_id, first_dispatched_ts = min of shipments.dispatched_ts; sorted by order_id asc.

## Q147: What is the implied pallet tare weight (notice_kg minus the sum of cases * case_kg from store.products) for every pallet in warehouse.pallets?

Answered from the schema layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: not answered: the ontology layer refused the plan (each row of products can match several earlier rows, so sum over products would count rows more than once).
Part 2: figures from the schema layer. (Plan covers: Notice weight per pallet from pallets-june, the minuend of the implied tare (notice_kg minus the summed case weight).)
30 rows (columns: sscc, notice_kg):
  029000010000010320 | 337.4
  029000010000010337 | 73.5
  029000010000010344 | 429.2
  029000010000010351 | 738.1
  029000010000010368 | 94.1
  029000010000010375 | 399.5
  029000010000010382 | 732.5
  029000010000010399 | 169.3
  029000010000010405 | 408.9
  029000010000010412 | 717.8
  ... and 20 more
  How it was found: From pallet records; report sscc = pallets.sscc, notice_kg = pallets.notice_kg.

## Q148: Which shipments arrived before their slot_start versus after their slot_end in June 2026?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: The June shipments that arrived before their slot_start, with how many hours early.)
No rows matched.
  How it was found: From shipment records; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30 and shipments.arrived_ts < shipments.slot_start; report shipment_id = shipments.shipment_id, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts, hours_before_slot_start = hours_between(shipments.arrived_ts, shipments.slot_start); sorted by slot_start asc.
Part 2: figures from the ontology layer. (Plan covers: The June shipments that arrived after their slot_end, with how many hours late.)
2 rows (columns: shipment_id, slot_start, slot_end, arrived_ts, hours_after_slot_end):
  SHP-260611 | 2026-06-11T06:00 | 2026-06-11T06:30 | 2026-06-11T08:21 | 1.8500000014901161
  SHP-260615 | 2026-06-15T06:00 | 2026-06-15T06:30 | 2026-06-15T08:08 | 1.6333333253860474
  How it was found: From shipment records; keep rows where day(shipments.slot_start) between 2026-06-01 and 2026-06-30 and shipments.arrived_ts > shipments.slot_end; report shipment_id = shipments.shipment_id, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts, hours_after_slot_end = hours_between(shipments.slot_end, shipments.arrived_ts); sorted by slot_start asc.

## Q149: Which warehouse slots (dc_slot) in store.products are adjacent to A-07-03 (same aisle and bay, position ±1)?

Answered from the schema layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Lists the products in warehouse slots A-07-02 and A-07-04, the positions either side of A-07-03 in the same aisle and bay, with A-07-03 itself shown for reference.)
2 rows (columns: dc_slot, sku, name, pack):
  A-07-03 | ATTA-WW-5KG | Whole wheat atta 5 kg | 5 kg
  A-07-04 | ATTA-WW-1KG | Whole wheat atta 1 kg | 1 kg
  How it was found: From product records; keep rows where products.dc_slot in ['A-07-02', 'A-07-03', 'A-07-04']; report dc_slot = products.dc_slot, sku = products.sku, name = products.name, pack = products.pack; sorted by dc_slot asc.

## Q150: How many pick confirmations in warehouse.pick_confirmations had cases_confirmed < cases_ordered, and which SKUs were short-picked?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts pick lines in dc-pick-confirmations-june where cases_confirmed is below cases_ordered.)
short_pick_lines = 2
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed < dc pick confirmations.cases_ordered; report short_pick_lines = count of *.
Part 2: figures from the schema layer. (Plan covers: Lists the SKUs of those short pick lines, grouped by sku in dc-pick-confirmations-june.)
2 rows (columns: sku, short_pick_lines):
  DAL-TOOR-1KG | 1
  SUGAR-1KG | 1
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed < dc pick confirmations.cases_ordered; group by dc pick confirmations.sku; report sku = dc pick confirmations.sku, short_pick_lines = count of *.

## Q151: In store.fresh_deliveries, how many days of shelf life (use_by - delivery_ts::date) did milk, curd, and bread have on arrival?

Answered from the ontology layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: Days of shelf life on arrival (use_by minus the delivery date) for the two milks, curd and bread on the fresh routes, as the average, shortest and longest per product.)
4 rows (columns: sku, delivery_rows, avg_shelf_life_days, min_shelf_life_days, max_shelf_life_days):
  BREAD-WHITE-400G | 28 | 3.0 | 3.0 | 3.0
  CURD-500G | 28 | 3.0 | 3.0 | 3.0
  MILK-FC-500ML | 28 | 1.0 | 1.0 | 1.0
  MILK-TONED-500ML | 28 | 1.0 | 1.0 | 1.0
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku in ['MILK-FC-500ML', 'MILK-TONED-500ML', 'CURD-500G', 'BREAD-WHITE-400G']; group by fresh deliveries.sku; report sku = fresh deliveries.sku, delivery_rows = count of *, avg_shelf_life_days = avg of days_between(day(fresh deliveries.delivery_ts), fresh deliveries.use_by), min_shelf_life_days = min of days_between(day(fresh deliveries.delivery_ts), fresh deliveries.use_by), max_shelf_life_days = max of days_between(day(fresh deliveries.delivery_ts), fresh deliveries.use_by); sorted by sku asc.

## Q152: How many distinct sscc pallet labels in warehouse.shipping_notice_lines carried more than one SKU on the same pallet?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Lists the pallet labels (SSCC) on the shipping-notice lines that carry more than one product, so the number of rows is the count asked for.)
22 rows (columns: sscc, skus_on_pallet, notice_lines):
  029000010000010320 | 2 | 2
  029000010000010344 | 2 | 2
  029000010000010351 | 3 | 3
  029000010000010375 | 3 | 3
  029000010000010382 | 2 | 2
  029000010000010399 | 2 | 2
  029000010000010405 | 2 | 2
  029000010000010412 | 3 | 3
  029000010000010436 | 3 | 3
  029000010000010443 | 5 | 5
  ... and 12 more
  How it was found: From shipping-notice line records; group by shipping notice lines.sscc; keep groups where skus_on_pallet > 1; report sscc = shipping notice lines.sscc, skus_on_pallet = count distinct of shipping notice lines.sku, notice_lines = count of *; sorted by sscc asc.

## Q153: What was the average lead time in hours from store.store_orders.created_ts to store.goods_receipts.received_ts for June 2026 orders?

Answered from the ontology layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: Average hours from each June store order's created_ts to the received_ts of the goods-receipt lines that carried it, linked through the shipping-notice line on the same shipment, pallet label and product, averaged over received lines.)
avg_lead_time_hours = 8.389705886187798; shortest_lead_time_hours = 8.00000000372529; longest_lead_time_hours = 10.350000008940697; received_lines = 68; orders = 24
  How it was found: From goods-receipt line records; inner-join shipping-notice line records on goods receipts.shipment_id = shipping notice lines.shipment_id and goods receipts.sscc = shipping notice lines.sscc and goods receipts.asn_sku = shipping notice lines.sku; inner-join store order line records on shipping notice lines.order_id = store orders.order_id and shipping notice lines.sku = store orders.sku; keep rows where day(store orders.created_ts) between 2026-06-01 and 2026-06-30; report avg_lead_time_hours = avg of hours_between(store orders.created_ts, goods receipts.received_ts), shortest_lead_time_hours = min of hours_between(store orders.created_ts, goods receipts.received_ts), longest_lead_time_hours = max of hours_between(store orders.created_ts, goods receipts.received_ts), received_lines = count of *, orders = count distinct of store orders.order_id.

## Q154: Since store.goods_receipts shows asn_units = units_booked and asn_sku = sku_booked on all 70 lines, did the warehouse ship 100% of the right items in June?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts goods-receipt lines where the ASN and the booking differ on SKU or units, which is the only check the records hold.)
mismatched_lines = 0
  How it was found: From goods-receipt line records; keep rows where (goods receipts.asn_sku != goods receipts.sku_booked or goods receipts.asn_units != goods receipts.units_booked); report mismatched_lines = count of *.
Part 2: figures from the schema layer. (Plan covers: Counts warehouse pick lines confirmed below cases_ordered, an observation from the picking side that can contradict the receipt check.)
short_pick_lines = 2
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed < dc pick confirmations.cases_ordered; report short_pick_lines = count of *.
Part 3: figures from the schema layer. (Plan covers: The receipt method is a pallet label scan against the shipping notice, so the receipt check copies the ASN and cannot prove the right items were shipped (Rule 12).)
receipt_method = pallet label (SSCC) scan against the shipping notice; lines = 70
  How it was found: From goods-receipt line records; group by goods receipts.receipt_method; report receipt_method = goods receipts.receipt_method, lines = count of *.

## Q155: Using warehouse.pallets.notice_kg, identify which pallet on 22 June was 160 kg underweight.

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the ontology layer. (Plan covers: The pallets on the 22 June shipment with their notice weight and weight-check status, where notice_kg is the weight written on the notice and the pallets were not weighed, so a pallet's actual weight, and any 160 kg shortfall, is not record)
2 rows (columns: shipment_id, sscc, cases, notice_kg, weight_check):
  SHP-260622 | 029000010000010542 | 39.0 | 723.7 | not weighed
  SHP-260622 | 029000010000010559 | 5.0 | 73.5 | not weighed
  How it was found: From pallet records; inner-join shipment records on pallets.shipment_id = shipments.shipment_id; keep rows where (day(shipments.slot_start) = '2026-06-22' or day(shipments.arrived_ts) = '2026-06-22'); report shipment_id = pallets.shipment_id, sscc = pallets.sscc, cases = pallets.cases, notice_kg = pallets.notice_kg, weight_check = pallets.weight_check; sorted by sscc asc.
Part 2: not answered: the ontology layer refused the plan (each row of products can match several earlier rows, so sum over products would count rows more than once).

## Q156: How many times in June 2026 did a warehouse picker confirm a pick by scanning the case barcode?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: June pick confirmations by how they were confirmed, where 'slot label scan' is the only method recorded, so a confirmation by scanning the case barcode would appear as a separate method.)
confirmed_by = slot label scan; confirmations = 70
  How it was found: From pick confirmation records; keep rows where day(dc pick confirmations.pick_ts) between 2026-06-01 and 2026-06-30; group by dc pick confirmations.confirmed_by; report confirmed_by = dc pick confirmations.confirmed_by, confirmations = count of *.

## Q157: Using warehouse.pick_confirmations, how many cases of ATTA-WW-1KG were actually loaded onto the 22 June truck?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Sums the 1 kg atta cases confirmed as picked on the 22 June truck (picks joined to shipments-june on shipment_id); loading onto the truck is not recorded, so picked cases stand in for loaded cases.)
cases_picked = 9.0
  How it was found: From pick confirmation records; inner-join shipment records on dc pick confirmations.shipment_id = shipments.shipment_id; keep rows where dc pick confirmations.sku = 'ATTA-WW-1KG' and day(shipments.arrived_ts) = '2026-06-22'; report cases_picked = sum of dc pick confirmations.cases_confirmed.

## Q158: If warehouse.shipments shows SHP-260622 arrived at 06:12 inside its 06:00–06:30 slot, was the 5 kg atta on that truck available to shoppers when the store opened at 07:00?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the premise that SHP-260622 arrived at 06:12 inside its 06:00 to 06:30 slot.)
shipment_id = SHP-260622; slot_start = 2026-06-22T06:00; slot_end = 2026-06-22T06:30; arrived_ts = 2026-06-22T06:12
  How it was found: From shipment records; keep rows where shipments.shipment_id = 'SHP-260622'; report shipment_id = shipments.shipment_id, slot_start = shipments.slot_start, slot_end = shipments.slot_end, arrived_ts = shipments.arrived_ts.
Part 2: figures from the schema layer. (Plan covers: When stock reached the shelf is not recorded, only receipts at the back door, so ATTA-WW-5KG sold at the till on 22 June by hour from the 07:00 opening on is the nearest evidence that shoppers could find it (available means on the shelf, Ru)
11 rows (columns: sale_hour, units_sold, till_lines):
  8 | 1.0 | 1
  9 | 1.0 | 1
  12 | 2.0 | 2
  13 | 2.0 | 2
  14 | 1.0 | 1
  15 | 2.0 | 2
  17 | 3.0 | 3
  18 | 4.0 | 4
  19 | 2.0 | 2
  20 | 1.0 | 1
  ... and 1 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-22'; group by hour(pos lines may.bill_ts); report sale_hour = hour(pos lines may.bill_ts), units_sold = sum of pos lines may.qty, till_lines = count of *; sorted by sale_hour asc.
Part 3: figures from the schema layer. (Plan covers: The ATTA-WW-5KG shelf audits after the delivery, which run only at 11:00 on Tuesdays and Fridays, so there is no audit at 07:00 and the first look at the shelf after the truck is the next audit.)
2 rows (columns: audit_ts, status):
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-22 and 2026-06-26; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 4: figures from the schema layer. (Plan covers: Hand counts of the 5 kg atta and its 1 kg lookalike after the delivery, which show whether the 5 kg atta booked from that truck was physically there (Rules 1 and 5).)
4 rows (columns: count_ts, sku, trigger, book_before, counted, adjustment):
  2026-06-26T09:00 | ATTA-WW-5KG | manager request after complaints | 63.0 | 0.0 | -63.0
  2026-06-26T09:00 | ATTA-WW-1KG | manager request after complaints | 106.0 | 263.0 | 157.0
  2026-06-28T22:30 | ATTA-WW-5KG | scheduled full count | 63.0 | 62.0 | -1.0
  2026-06-28T22:30 | ATTA-WW-1KG | scheduled full count | 168.0 | 169.0 | 1.0
  How it was found: From stock count records; keep rows where stock counts.sku in ['ATTA-WW-5KG', 'ATTA-WW-1KG'] and day(stock counts.count_ts) between 2026-06-22 and 2026-06-28; report count_ts = stock counts.count_ts, sku = stock counts.sku, trigger = stock counts.trigger, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment; sorted by count_ts asc.

## Q159: How many units of ATTA-WW-1KG were in slot A-07-04 at the warehouse on 21 June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Warehouse stock by slot is not recorded on any day, so the units in slot A-07-04 on 21 June are not recorded, and this checks which warehouse slot ATTA-WW-1KG is assigned to.)
sku = ATTA-WW-1KG; name = Whole wheat atta 1 kg; dc_slot = A-07-04; case_units = 10.0
  How it was found: From product records; keep rows where products.sku = 'ATTA-WW-1KG'; report sku = products.sku, name = products.name, dc_slot = products.dc_slot, case_units = products.case_units.
Part 2: figures from the schema layer. (Plan covers: The only recorded warehouse stock observations for ATTA-WW-1KG in June, its stock corrections with their slot, which give a change and not the quantity in the slot on 21 June.)
adjusted_ts = 2026-06-23T14:20; sku = ATTA-WW-1KG; slot = A-07-04; reason = short pick: slot count variance; cases = -16.0; units = -160.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.sku = 'ATTA-WW-1KG' and day(dc stock adjustments.adjusted_ts) between 2026-06-01 and 2026-06-30; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, reason = dc stock adjustments.reason, cases = dc stock adjustments.cases, units = dc stock adjustments.units; sorted by adjusted_ts asc.

## Q160: What was the expiry date (use_by) of the ATTA-WW-5KG bags delivered on 22 June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Checks whether ATTA-WW-5KG appears on fresh deliveries on 22 June; use_by is held only for fresh deliveries, so no row is expected for atta.)
No rows matched.
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'ATTA-WW-5KG' and fresh deliveries.delivery_ts between 2026-06-22T00:00 and 2026-06-22T23:59; report delivery_ts = fresh deliveries.delivery_ts, use_by = fresh deliveries.use_by.

## Q161: Of the shoppers whose UPI payment declined or failed in June 2026, how many gave up and left without paying?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: not answered: the ontology layer refused the plan (a select item needs 'as' (a lowercase name) and 'expr').
Part 2: figures from the schema layer. (Plan covers: Every June bill has exactly one approved payment, so recorded bills all ended up paid; abandoned shoppers leave no bill.)
bills_with_approved_payment = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; report bills_with_approved_payment = count distinct of pos payments.bill_id.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q162: What does it cost Store 014 to serve a cash payment versus a UPI payment versus a card payment?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Only UPI's merchant fee (MDR) is recorded, shown as total fees against gross UPI settled, while card fees and the cost of handling cash are not recorded.)
gross_inr = 10798593.78; mdr_inr = 0.0; mdr_share_of_gross = 0.0; upi_credits = 18410.0
  How it was found: From UPI settlement records; report gross_inr = sum of upi settlements.gross_inr, mdr_inr = sum of upi settlements.mdr_inr, mdr_share_of_gross = sum of upi settlements.mdr_inr / sum of upi settlements.gross_inr, upi_credits = sum of upi settlements.upi_credits.
Part 2: figures from the schema layer. (Plan covers: Approved payments by tender, so the UPI fee can be read per UPI payment, with no cost recorded for cash or card payments.)
3 rows (columns: tender, approved_payments, amount_inr):
  UPI | 18384 | 10785227.72
  card | 3864 | 2253823.39
  cash | 7829 | 4531615.76
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; group by pos payments.tender; report tender = pos payments.tender, approved_payments = count of *, amount_inr = sum of pos payments.amount_inr.

## Q163: What inside the till or staff behaviour caused the double charges in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Complaint kinds in customer-complaints-june; the cause, whether a till or staff action, is not recorded in any table.)
2 rows (columns: kind, complaints):
  charged twice | 23
  debited but the till said failed | 3
  How it was found: From complaint records; group by customer complaints.kind; report kind = customer complaints.kind, complaints = count of *.
Part 2: figures from the ontology layer. (Plan covers: Extra debits: provider successes whose rrn has no approved till payment (Definitions); these show the pattern only, not the till or staff cause.)
26 rows (columns: rrn, amount_inr, status_ts):
  615521002766 | 143.11 | 2026-06-04T21:33:20
  615619003319 | 224.51 | 2026-06-05T19:59:20
  615908004963 | 1325.54 | 2026-06-08T08:40:21
  615909004985 | 564.24 | 2026-06-08T09:09:15
  616011005544 | 532.71 | 2026-06-09T13:52:31
  616517008996 | 362.94 | 2026-06-14T17:01:54
  616918011772 | 963.27 | 2026-06-18T18:45:00
  617118013318 | 438.73 | 2026-06-20T18:22:57
  617118013325 | 342.13 | 2026-06-21T11:10:52
  617118013326 | 342.13 | 2026-06-20T21:28:32
  ... and 16 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and pos payments.rrn is empty; report rrn = psp upi report.rrn, amount_inr = psp upi report.amount_inr, status_ts = psp upi report.status_ts.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q164: Which customers were double-charged in June 2026, and did they come back to the store?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Bills (stand-in for shoppers) with a charged-twice complaint; no customer identity is recorded and nothing links bills to a shopper, so who they are and whether they returned is not recorded.)
23 rows (columns: bill_id, complaint_ts, amount_inr):
  B260604-140026 | 2026-06-05T12:00:00 | 143.11
  B260605-120088 | 2026-06-06T13:00:00 | 224.51
  B260609-040018 | 2026-06-10T10:00:00 | 532.71
  B260614-100001 | 2026-06-15T19:00:00 | 362.94
  B260618-110082 | 2026-06-20T11:00:00 | 963.27
  B260620-120037 | 2026-06-22T11:00:00 | 398.2
  B260620-120072 | 2026-06-22T12:00:00 | 646.9
  B260620-110032 | 2026-06-22T14:00:00 | 342.13
  B260620-120041 | 2026-06-22T15:00:00 | 1608.98
  B260620-120019 | 2026-06-22T18:00:00 | 592.94
  ... and 13 more
  How it was found: From complaint records; keep rows where customer complaints.kind = 'charged twice'; report bill_id = customer complaints.bill_id, complaint_ts = customer complaints.complaint_ts, amount_inr = customer complaints.amount_inr; sorted by complaint_ts asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q165: How much of Store 014's payment volume in June 2026 was fraud?

Answered from the knowledge layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Fraud is not recorded on any payment, so this gives June's approved payment volume, the base any fraud share would be read against (Bills and takings definition).)
approved_payments = 30077; payment_volume_inr = 17570666.87
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report approved_payments = count of *, payment_volume_inr = sum of pos payments.amount_inr.
Part 2: figures from the schema layer. (Plan covers: The only recorded payment disputes are customer complaints about debits, charged twice or debited while the till said failed, with how each was resolved, and none is labelled fraud.)
2 rows (columns: kind, resolution, complaints, amount_inr):
  charged twice | refunded after the store matched the credit by hand | 23 | 11301.86
  debited but the till said failed | customer's bank returned the money | 3 | 667.3
  How it was found: From complaint records; keep rows where day(customer complaints.complaint_ts) between 2026-06-01 and 2026-06-30; group by customer complaints.kind, customer complaints.resolution; report kind = customer complaints.kind, resolution = customer complaints.resolution, complaints = count of *, amount_inr = sum of customer complaints.amount_inr.

## Q166: Why do shoppers choose cash, card or UPI at Store 014?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Why shoppers choose a tender is not recorded, so this shows what they chose: approved payments, takings and average bill value by tender (bill values come from approved payments).)
3 rows (columns: tender, approved_payments, takings_inr, average_bill_inr):
  UPI | 18384 | 10785227.72 | 586.6638228894691
  card | 3864 | 2253823.39 | 583.2876268115942
  cash | 7829 | 4531615.76 | 578.8243402733427
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; group by pos payments.tender; report tender = pos payments.tender, approved_payments = count of *, takings_inr = sum of pos payments.amount_inr, average_bill_inr = avg of pos payments.amount_inr.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q167: Does the cash in Store 014's tills match the cash banked in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Neither the cash counted in the tills nor the cash banked is recorded, so this gives the approved cash takings recorded at the tills in June, the figure a banking record would be checked against.)
cash_payments = 7829; cash_takings_inr = 4531615.76
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'cash' and pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report cash_payments = count of *, cash_takings_inr = sum of pos payments.amount_inr.

## Q168: What did a customer's bank statement show for a failed UPI payment at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the ontology layer. (Plan covers: A customer's bank statement is not recorded, so the UPI provider's final status for the same rrn is the nearest witness (Rule 9) for UPI attempts that failed at the till, while timeouts carry no rrn and show no provider status.)
2 rows (columns: till_status, provider_status, attempts):
  failed | failed | 145
  failed: no response |  | 48
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status, psp upi report.status; report till_status = pos payments.till_status, provider_status = psp upi report.status, attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: Customers' own reports that their bank debited them although the till said failed, and how each was resolved.)
resolution = customer's bank returned the money; complaints = 3; amount_inr = 667.3
  How it was found: From complaint records; keep rows where customer complaints.kind = 'debited but the till said failed' and day(customer complaints.complaint_ts) between 2026-06-01 and 2026-06-30; group by customer complaints.resolution; report resolution = customer complaints.resolution, complaints = count of *, amount_inr = sum of customer complaints.amount_inr.
Not recorded, so not answered: bank_side (who): the customer's bank side of a payment is not in the records [rule-9]

## Q169: How many UPI refunds did Store 014 make in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the UPI refunds completed in June 2026 (refunds are recorded 5 to 26 June).)
refunds = 23
  How it was found: From UPI refund records; keep rows where day(upi refunds.completed_ts) between 2026-06-01 and 2026-06-30; report refunds = count of *.

## Q170: What was the total net UPI amount settled to Store 014 in June 2026, in rupees?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total net UPI amount credited to the store by settlements dated in June 2026, in rupees.)
net_settled_inr = 10787291.92; settlement_days = 29
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report net_settled_inr = sum of upi settlements.net_inr, settlement_days = count of *.

## Q171: How many payment attempts were recorded at the tills in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts all payment attempts recorded at the tills in June 2026, of every tender and status.)
payment_attempts = 30949
  How it was found: From payment attempt records; keep rows where day(pos payments.ts) between 2026-06-01 and 2026-06-30; report payment_attempts = count of *.

## Q172: How many different customers paid by UPI at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No table identifies a customer, so this counts the distinct June bills paid by approved UPI, the nearest stand-in, as one shopper can have several bills.)
bills_paid_by_upi = 18384
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills_paid_by_upi = count distinct of pos payments.bill_id.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q173: Which customers complained more than once in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No table identifies a customer, so this lists the bills with more than one June complaint, the nearest stand-in, which cannot show one customer complaining about different bills.)
2 rows (columns: bill_id, complaints, first_complaint_ts, last_complaint_ts):
  B260620-110055 | 2 | 2026-06-23T10:00:00 | 2026-06-24T10:00:00
  B260620-110032 | 2 | 2026-06-22T14:00:00 | 2026-06-23T14:00:00
  How it was found: From complaint records; keep rows where day(customer complaints.complaint_ts) between 2026-06-01 and 2026-06-30; group by customer complaints.bill_id; keep groups where complaints > 1; report bill_id = customer complaints.bill_id, complaints = count of *, first_complaint_ts = min of customer complaints.complaint_ts, last_complaint_ts = max of customer complaints.complaint_ts; sorted by complaints desc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q174: What was the main reason UPI payments failed at Store 014's tills in June 2026: the customer's bank, the network or the customer?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Whether the customer's bank, the network or the customer caused a failure is not recorded, and the till's status only separates business declines ('declined') from technical failures ('failed') and timeouts ('failed: no response', not known)
3 rows (columns: till_status, attempts):
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['declined', 'failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *; sorted by attempts desc.
Part 2: figures from the ontology layer. (Plan covers: The UPI provider's final status for the same attempts, matched by rrn (UPI's final status decides, Rule 9), while timeouts carry no rrn and cannot be matched.)
3 rows (columns: till_status, provider_status, attempts):
  declined | failed | 589
  failed | failed | 145
  failed: no response |  | 48
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['declined', 'failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status, psp upi report.status; report till_status = pos payments.till_status, provider_status = psp upi report.status, attempts = count of *.
Not recorded, so not answered: bank_side (who): the customer's bank side of a payment is not in the records [rule-9]; cause (why): no table records the reason or cause of an event [rule-5]

## Q175: How has the UPI share of payments at Store 014 trended over 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Payments are recorded only for June 2026, with none before June, so no trend across 2026 is recorded, and this gives the tender mix of approved payments for the whole recorded period.)
3 rows (columns: tender, approved_payments, amount_inr):
  UPI | 18384 | 10785227.72
  card | 3864 | 2253823.39
  cash | 7829 | 4531615.76
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-01-01 and 2026-12-31; group by pos payments.tender; report tender = pos payments.tender, approved_payments = count of *, amount_inr = sum of pos payments.amount_inr.
Part 2: figures from the schema layer. (Plan covers: Approved payments per day by tender within June, the only trend the records can show, where the UPI share on a day is its UPI payments divided by all its payments.)
84 rows (columns: payment_date, tender, approved_payments):
  2026-06-01 | UPI | 789
  2026-06-01 | card | 173
  2026-06-01 | cash | 337
  2026-06-02 | UPI | 686
  2026-06-02 | card | 126
  2026-06-02 | cash | 277
  2026-06-03 | UPI | 624
  2026-06-03 | card | 118
  2026-06-03 | cash | 255
  2026-06-04 | UPI | 605
  ... and 74 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-01-01 and 2026-12-31; group by day(pos payments.ts), pos payments.tender; report payment_date = day(pos payments.ts), tender = pos payments.tender, approved_payments = count of *; sorted by payment_date asc.

## Q176: What was the total amount in rupees of UPI refunds made in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Total rupees of the UPI refunds completed in June 2026.)
refunds_total_inr = 11301.86; refunds = 23
  How it was found: From UPI refund records; keep rows where day(upi refunds.completed_ts) between 2026-06-01 and 2026-06-30; report refunds_total_inr = sum of upi refunds.amount_inr, refunds = count of *.

## Q177: How many payment attempts at the tills in June 2026 had the status declined?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June 2026 till payment attempts with status 'declined', across all tenders.)
declined_attempts = 679
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'declined' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report declined_attempts = count of *.

## Q178: How many transactions in the UPI service provider's report for June 2026 have the status failed?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June 2026 transactions in the UPI service provider's report with status 'failed'.)
failed_transactions = 750
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'failed' and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; report failed_transactions = count of *.

## Q179: How many UPI refunds has Store 014 made so far in 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Refunds are recorded only from 5 to 26 June 2026, so refunds earlier or later in 2026 are not in the records, and this counts the refunds on record for 2026 with the dates they span.)
refunds = 23; first_completed_ts = 2026-06-08T13:00:00; last_completed_ts = 2026-06-29T17:00:00
  How it was found: From UPI refund records; keep rows where day(upi refunds.completed_ts) between 2026-01-01 and 2026-12-31; report refunds = count of *, first_completed_ts = min of upi refunds.completed_ts, last_completed_ts = max of upi refunds.completed_ts.
Not recorded, so not answered: needs a longer period than the records cover

## Q180: Why were some UPI refunds slower than others at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Refund wait per Rule 11 and Definitions: from the extra debit (the provider success status_ts) to completed_ts, not from the complaint; the complaint clock is not used here.)
23 rows (columns: refund_id, amount_inr, wait_hours):
  RF-013344 | 1064.47 | 187.16888889670372
  RF-013378 | 289.86 | 181.58777778223157
  RF-013325 | 342.13 | 170.81888888776302
  RF-013326 | 342.13 | 160.52444444596767
  RF-013351 | 372.15 | 151.35583333298564
  RF-013389 | 167.25 | 142.7569444477558
  RF-013377 | 216.89 | 137.89499999955297
  RF-013361 | 171.7 | 136.82027777284384
  RF-002766 | 143.11 | 134.44444444030523
  RF-015950 | 781.86 | 120.85750000923872
  ... and 13 more
  How it was found: From UPI refund records; inner-join UPI service provider's transaction records on upi refunds.rrn = psp upi report.rrn; keep rows where psp upi report.status = 'success'; report refund_id = upi refunds.refund_id, amount_inr = upi refunds.amount_inr, wait_hours = hours_between(psp upi report.status_ts, upi refunds.completed_ts); sorted by wait_hours desc.
Part 2: figures from the schema layer. (Plan covers: The reason some refunds were slower is not recorded; the only trigger field holds customer complaint, so the cause is not in the records.)
trigger = customer complaint; refunds = 23
  How it was found: From UPI refund records; group by upi refunds.trigger; report trigger = upi refunds.trigger, refunds = count of *.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q181: How many shoppers paid for one bill with two different payment methods at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Bills (stand-in for shoppers) with attempts under more than one tender; this includes a failed attempt followed by another tender, not only split payment of one bill.)
200 rows (columns: bill_id, tenders):
  B260601-010015 | 2
  B260601-010076 | 2
  B260601-010088 | 2
  B260601-030003 | 2
  B260601-030012 | 2
  B260601-040061 | 2
  B260601-040062 | 2
  B260601-060047 | 2
  B260601-080061 | 2
  B260601-090061 | 2
  ... and 190 more
  How it was found: From payment attempt records; group by pos payments.bill_id; keep groups where tenders > 1; report bill_id = pos payments.bill_id, tenders = count distinct of pos payments.tender.
Stand-ins used (not the real thing): shopper_count (who): a bill is not a shopper: bills are the nearest stand-in

## Q182: How many UPI payments did shoppers retry after a decline at Store 014 in June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Bills with more than one UPI attempt, the recorded sign of a retry.)
200 rows (columns: bill_id, upi_attempts):
  B260601-000008 | 2
  B260601-000042 | 2
  B260601-040002 | 2
  B260601-040036 | 2
  B260601-060013 | 2
  B260601-060029 | 2
  B260601-060033 | 2
  B260601-080053 | 2
  B260601-100028 | 2
  B260601-100033 | 2
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; group by pos payments.bill_id; keep groups where upi_attempts > 1; report bill_id = pos payments.bill_id, upi_attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: Bills with a declined UPI attempt (a business decline), to compare with the retry list.)
bills_with_declined_upi = 577
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'declined'; report bills_with_declined_upi = count distinct of pos payments.bill_id.

## Q183: How many distinct bills had at least one UPI payment attempt in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the distinct June bills with at least one UPI payment attempt, whatever its status.)
bills_with_upi_attempt = 18770
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills_with_upi_attempt = count distinct of pos payments.bill_id.

## Q184: How many complaints did customers decide not to file at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: A complaint a customer chose not to file is not recorded, so the nearest stand-in is the June extra debits (provider successes with no approved till payment) that no complaint mentions, which cannot say why those customers stayed silent.)
extra_debits_without_complaint = 3
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join complaint records on psp upi report.rrn = customer complaints.rrn; keep rows where psp upi report.status = 'success' and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30 and (pos payments.rrn is empty or pos payments.till_status != 'approved') and customer complaints.rrn is empty; report extra_debits_without_complaint = count distinct of psp upi report.rrn.

## Q185: Why did the UPI settlement on 9 June 2026 come in lower than the day before?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks that the 9 June settlement came in lower than 8 June's and shows which part moved (number of credits, gross, fee or refunds), as nothing beyond these parts records why.)
2 rows (columns: settlement_date, upi_credits, gross_inr, mdr_inr, refunds_inr, net_inr):
  2026-06-08 | 574.0 | 357236.46 | 0.0 | 0.0 | 357236.46
  2026-06-09 | 485.0 | 287842.03 | 0.0 | 224.51 | 287617.52
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date in ['2026-06-08', '2026-06-09']; report settlement_date = upi settlements.settlement_date, upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr, mdr_inr = upi settlements.mdr_inr, refunds_inr = upi settlements.refunds_inr, net_inr = upi settlements.net_inr; sorted by settlement_date asc.
Part 2: figures from the schema layer. (Plan covers: The UPI provider's transactions by day and final status from 7 to 9 June, the activity those settlements carry, while which days each settlement covers is not recorded.)
6 rows (columns: status_date, status, transactions, amount_inr):
  2026-06-07 | failed | 32 | 18850.06
  2026-06-07 | success | 574 | 357236.46
  2026-06-08 | failed | 29 | 20538.760000000002
  2026-06-08 | success | 485 | 287842.03
  2026-06-09 | failed | 21 | 10839.23
  2026-06-09 | success | 475 | 288474.39
  How it was found: From UPI service provider's transaction records; keep rows where day(psp upi report.status_ts) between 2026-06-07 and 2026-06-09; group by day(psp upi report.status_ts), psp upi report.status; report status_date = day(psp upi report.status_ts), status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr; sorted by status_date asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q186: What was the biggest single UPI refund in June 2026, in rupees?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: The largest single UPI refund completed in June 2026, in rupees.)
biggest_refund_inr = 1608.98
  How it was found: From UPI refund records; keep rows where day(upi refunds.completed_ts) between 2026-06-01 and 2026-06-30; report biggest_refund_inr = max of upi refunds.amount_inr.

## Q187: How many customer complaints in June 2026 were about being charged twice?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June 2026 customer complaints of the kind 'charged twice'.)
complaints = 23
  How it was found: From complaint records; keep rows where customer complaints.kind = 'charged twice' and day(customer complaints.complaint_ts) between 2026-06-01 and 2026-06-30; report complaints = count of *.

## Q188: How many bills had two or more payment attempts in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Bills with two or more payment attempts in June; count the rows listed.)
200 rows (columns: bill_id, attempts):
  B260601-000008 | 2
  B260601-000042 | 2
  B260601-010015 | 2
  B260601-010076 | 2
  B260601-010088 | 2
  B260601-030003 | 2
  B260601-030012 | 2
  B260601-040002 | 2
  B260601-040036 | 2
  B260601-040061 | 2
  ... and 190 more
  How it was found: From payment attempt records; group by pos payments.bill_id; keep groups where attempts >= 2; report bill_id = pos payments.bill_id, attempts = count of *.

## Q189: On how many days in June 2026 did Store 014 receive a UPI settlement?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the distinct June 2026 dates on which a UPI settlement was credited to the store.)
settlement_days = 29
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report settlement_days = count distinct of upi settlements.settlement_date.

## Q190: How many UPI payments did customers start but never finish in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: A UPI payment a customer started and abandoned is not recorded as such, so this shows June UPI attempts at the till by outcome, those not ending approved being the nearest evidence (timeouts are not known yet, Rule 9), while every June bill)
4 rows (columns: till_status, attempts, bills):
  approved | 18384 | 18384
  declined | 589 | 577
  failed | 145 | 145
  failed: no response | 48 | 44
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *, bills = count distinct of pos payments.bill_id.
Part 2: figures from the schema layer. (Plan covers: The UPI provider's final status for June transactions, where no status for an unfinished payment exists.)
3 rows (columns: status, transactions):
  failed | 750
  returned | 6
  success | 18410
  How it was found: From UPI service provider's transaction records; keep rows where day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; group by psp upi report.status; report status = psp upi report.status, transactions = count of *.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q191: How many payment attempts at the tills had the status failed in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the June 2026 till payment attempts with status 'failed', across all tenders, where timeouts ('failed: no response') are a separate status and not included.)
failed_attempts = 145
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'failed' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report failed_attempts = count of *.

## Q192: How many UPI refunds were made in June 2026, and who approved each of them?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts the UPI refunds completed in June 2026.)
refunds = 23
  How it was found: From UPI refund records; keep rows where day(upi refunds.completed_ts) between 2026-06-01 and 2026-06-30; report refunds = count of *.
Part 2: figures from the schema layer. (Plan covers: No table records who approved a refund, as no person is identified, so this shows the only recorded reason for each refund, its trigger.)
trigger = customer complaint; refunds = 23
  How it was found: From UPI refund records; keep rows where day(upi refunds.completed_ts) between 2026-06-01 and 2026-06-30; group by upi refunds.trigger; report trigger = upi refunds.trigger, refunds = count of *.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q193: What was the smallest net UPI settlement received in a single day in June 2026, in rupees?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: The June 2026 settlement day with the smallest net UPI amount credited, in rupees.)
settlement_date = 2026-06-30; net_inr = -781.86
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report settlement_date = upi settlements.settlement_date, net_inr = upi settlements.net_inr; sorted by net_inr asc.

## Q194: How many UPI payment attempts failed at the tills in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts the June UPI attempts that failed at the till, timeouts ('failed: no response') included and business declines excluded, as in the UPI technical failure rate definition.)
failed_upi_attempts = 193
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report failed_upi_attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: The same failures split into 'failed' and timeouts ('failed: no response').)
2 rows (columns: till_status, attempts):
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *.

## Q195: How many card payment attempts were approved from 15 June to 20 June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts card payment attempts with till status 'approved' dated 15 to 20 June 2026, both days included.)
approved_card_attempts = 841
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'card' and pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-15 and 2026-06-20; report approved_card_attempts = count of *.

## Q196: How many UPI refunds in June 2026 were completed?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts UPI refunds whose completed_ts falls in June 2026 (the refund table runs 5 to 26 June), with their rupee total.)
completed_refunds = 23; refunded_inr = 11301.86
  How it was found: From UPI refund records; keep rows where upi refunds.completed_ts is not empty and day(upi refunds.completed_ts) between 2026-06-01 and 2026-06-30; report completed_refunds = count of *, refunded_inr = sum of upi refunds.amount_inr.

## Q197: How many UPI payments did the tills attempt in June?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts UPI payment attempts at the tills in June (till records run 1 to 28 June) and the bills they were made for.)
upi_attempts = 19166; bills_with_upi_attempt = 18770
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report upi_attempts = count of *, bills_with_upi_attempt = count distinct of pos payments.bill_id.

## Q198: How many UPI attempts timed out (failed: no response) without receiving an RRN?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts UPI till attempts with till status 'failed: no response' that carry no RRN.)
timeouts_without_rrn = 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and pos payments.rrn is empty; report timeouts_without_rrn = count of *.

## Q199: Which successes in the provider's UPI report have no matching approved payment at the till?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Lists provider 'success' transactions whose RRN has no approved till payment (definition: Extra debit), with the till attempt carrying that RRN if there is one; a debit behind a till timeout shows no till row because a timeout has no RRN.)
26 rows (columns: rrn, amount_inr, initiated_ts, status_ts, till_bill_id, till_status):
  615521002766 | 143.11 | 2026-06-04T21:32:26 | 2026-06-04T21:33:20 |  | 
  615619003319 | 224.51 | 2026-06-05T19:58:33 | 2026-06-05T19:59:20 |  | 
  615908004963 | 1325.54 | 2026-06-08T08:39:27 | 2026-06-08T08:40:21 |  | 
  615909004985 | 564.24 | 2026-06-08T09:08:34 | 2026-06-08T09:09:15 |  | 
  616011005544 | 532.71 | 2026-06-09T11:22:07 | 2026-06-09T13:52:31 |  | 
  616517008996 | 362.94 | 2026-06-14T17:00:31 | 2026-06-14T17:01:54 |  | 
  616918011772 | 963.27 | 2026-06-18T18:43:56 | 2026-06-18T18:45:00 |  | 
  617118013318 | 438.73 | 2026-06-20T18:22:03 | 2026-06-20T18:22:57 |  | 
  617118013325 | 342.13 | 2026-06-20T18:32:55 | 2026-06-21T11:10:52 |  | 
  617118013326 | 342.13 | 2026-06-20T18:33:25 | 2026-06-20T21:28:32 |  | 
  ... and 16 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.rrn is empty or pos payments.till_status != 'approved'); report rrn = psp upi report.rrn, amount_inr = psp upi report.amount_inr, initiated_ts = psp upi report.initiated_ts, status_ts = psp upi report.status_ts, till_bill_id = pos payments.bill_id, till_status = pos payments.till_status; sorted by initiated_ts asc.

## Q200: Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: June UPI attempts by till status, giving the monthly timeout rate as 'failed: no response' attempts over all UPI attempts.)
4 rows (columns: till_status, upi_attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status; report till_status = pos payments.till_status, upi_attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: Lists the June clock hours with 3 or more UPI timeouts ('failed: no response'), the first test of a burst.)
2 rows (columns: pay_date, clock_hour, timeouts):
  2026-06-20 | 19 | 16
  2026-06-20 | 18 | 12
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts), hour(pos payments.ts); keep groups where timeouts >= 3; report pay_date = day(pos payments.ts), clock_hour = hour(pos payments.ts), timeouts = count of *; sorted by timeouts desc.
Part 3: figures from the schema layer. (Plan covers: UPI attempts per clock hour for 1 to 14 June, so a candidate hour's timeout rate (its timeouts over its attempts) can be tested against more than 10 times the monthly rate.)
200 rows (columns: pay_date, clock_hour, upi_attempts):
  2026-06-01 | 7 | 69
  2026-06-01 | 8 | 52
  2026-06-01 | 9 | 60
  2026-06-01 | 10 | 53
  2026-06-01 | 11 | 42
  2026-06-01 | 12 | 35
  2026-06-01 | 13 | 34
  2026-06-01 | 14 | 49
  2026-06-01 | 15 | 43
  2026-06-01 | 16 | 52
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-14; group by day(pos payments.ts), hour(pos payments.ts); report pay_date = day(pos payments.ts), clock_hour = hour(pos payments.ts), upi_attempts = count of *; sorted by pay_date asc, clock_hour asc.
Part 4: figures from the schema layer. (Plan covers: UPI attempts per clock hour for 15 to 30 June (till records end 28 June), for the same test against more than 10 times the monthly rate.)
200 rows (columns: pay_date, clock_hour, upi_attempts):
  2026-06-15 | 7 | 55
  2026-06-15 | 8 | 50
  2026-06-15 | 9 | 37
  2026-06-15 | 10 | 27
  2026-06-15 | 11 | 34
  2026-06-15 | 12 | 31
  2026-06-15 | 13 | 23
  2026-06-15 | 14 | 30
  2026-06-15 | 15 | 26
  2026-06-15 | 16 | 40
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-15 and 2026-06-30; group by day(pos payments.ts), hour(pos payments.ts); report pay_date = day(pos payments.ts), clock_hour = hour(pos payments.ts), upi_attempts = count of *; sorted by pay_date asc, clock_hour asc.

## Q201: How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts distinct bills paid by approved UPI payments above 2000 rupees in pos-payments-june, one approved payment per bill.)
upi_bills_over_2000 = 653
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 2000; report upi_bills_over_2000 = count distinct of pos payments.bill_id.
Part 2: figures from the ontology layer. (Plan covers: Sums 0.4 percent of amount for approved UPI bills between 2000 and 75000 rupees, where the 300 rupee cap cannot bind.)
uncapped_fee_inr = 7905.5596399999995
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 2000 and pos payments.amount_inr <= 75000; report uncapped_fee_inr = sum of pos payments.amount_inr * 0.004.
Part 3: figures from the schema layer. (Plan covers: Counts approved UPI bills above 75000 rupees, where 0.4 percent exceeds the 300 rupee cap, so each of these pays exactly 300 rupees in code.)
bills_at_cap = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 75000; report bills_at_cap = count of pos payments.bill_id.

## Q202: Which customers were charged three times for a single bill?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: No table identifies customers, so a bill stands in for one: this lists bills with three or more charges (the approved till payment plus provider-success debits tied to the bill by RRN), and a debit behind a till timeout has no RRN so it can)
No rows matched.
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where (pos payments.till_status = 'approved' or psp upi report.status = 'success'); group by pos payments.bill_id; keep groups where charges >= 3; report bill_id = pos payments.bill_id, charges = count of *, charged_inr = sum of pos payments.amount_inr; sorted by charges desc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q203: Did any customer pay twice in June, and how many?

Answered from the ontology layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Counts June provider successes with no approved till payment (definition: Extra debit, which Rule 10 treats as a customer charged twice until proven otherwise), since no customer identity is recorded.)
extra_debits = 26; extra_debit_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.rrn is empty or pos payments.till_status != 'approved') and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; report extra_debits = count of *, extra_debit_inr = sum of psp upi report.amount_inr.

## Q204: What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts the UPI attempts the tills gave up on ('failed: no response') between 18:20 and 19:50 on Saturday 20 June 2026.)
till_timeouts = 28; timeout_inr = 14156.82
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and pos payments.ts between 2026-06-20T18:20 and 2026-06-20T19:50; report till_timeouts = count of *, timeout_inr = sum of pos payments.amount_inr.
Part 2: figures from the ontology layer. (Plan covers: A timeout has no RRN, so the outcome is read from provider transactions started in the same window whose RRN never reached the till, by final status (Rule 9): success is a late credit, returned is debited and returned, failed is never debit)
3 rows (columns: provider_status, transactions, amount_inr):
  failed | 10 | 6138.02
  returned | 1 | 193.11
  success | 17 | 7825.69
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where pos payments.rrn is empty and psp upi report.initiated_ts between 2026-06-20T18:20 and 2026-06-20T19:50; group by psp upi report.status; report provider_status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q205: Why are 17 UPI credits from 20 and 21 June sitting in suspense?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Settlement credits around 20 and 21 June to check the premise of 17 credits; why anything is in suspense is a cause that is not recorded.)
3 rows (columns: settlement_date, upi_credits, gross_inr):
  2026-06-20 | 824.0 | 510195.41
  2026-06-21 | 607.0 | 367003.47
  2026-06-22 | 670.0 | 423309.67
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date >= '2026-06-20' and upi settlements.settlement_date <= '2026-06-22'; report settlement_date = upi settlements.settlement_date, upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr; sorted by settlement_date asc.
Part 2: figures from the ontology layer. (Plan covers: Provider successes on 20 and 21 June with no approved till payment, the recorded candidates for credits with no till match.)
extra_debits = 17
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and psp upi report.status_ts >= '2026-06-20' and psp upi report.status_ts < '2026-06-22' and (pos payments.till_status is empty or pos payments.till_status != 'approved'); report extra_debits = count of *.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q206: How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Refund wait from the extra debit (provider status_ts) to the refund completed_ts, joined on rrn; average and maximum, no median.)
refunds = 23; avg_hours_from_extra_debit = 123.88242753611311; max_hours_from_extra_debit = 187.16888889670372
  How it was found: From UPI service provider's transaction records; inner-join UPI refund records on psp upi report.rrn = upi refunds.rrn; report refunds = count of *, avg_hours_from_extra_debit = avg of hours_between(psp upi report.status_ts, upi refunds.completed_ts), max_hours_from_extra_debit = max of hours_between(psp upi report.status_ts, upi refunds.completed_ts).
Part 2: figures from the ontology layer. (Plan covers: Support clock: from complaint_ts to refund completed_ts for complaints with a refund, joined on rrn.)
refunds = 23; avg_hours_from_complaint = 77.21739130434783; max_hours_from_complaint = 120.0
  How it was found: From complaint records; inner-join UPI refund records on customer complaints.rrn = upi refunds.rrn; report refunds = count of *, avg_hours_from_complaint = avg of hours_between(customer complaints.complaint_ts, upi refunds.completed_ts), max_hours_from_complaint = max of hours_between(customer complaints.complaint_ts, upi refunds.completed_ts).
Part 3: figures from the ontology layer. (Plan covers: Extra debits with no refund record, i.e. still unrefunded at month end (refund records run to 2026-06-26).)
unrefunded_extra_debits = 3; unrefunded_inr = 2064.2
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join UPI refund records on psp upi report.rrn = upi refunds.rrn; keep rows where psp upi report.status = 'success' and (pos payments.till_status is empty or pos payments.till_status != 'approved') and upi refunds.refund_id is empty; report unrefunded_extra_debits = count of *, unrefunded_inr = sum of psp upi report.amount_inr.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q207: Was the store's UPI technical decline rate acceptable in June?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: UPI technical failure rate definition: failed plus failed: no response over all UPI attempts, shown by status so timeouts can be included or not; what is acceptable is not recorded.)
4 rows (columns: till_status, attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *.

## Q208: Which customers (by RRN) should the store refund now, without waiting for a complaint?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Lists by RRN the extra debits (provider success with no approved till payment, a customer charged twice under Rule 10) that have no completed refund, oldest debit first.)
3 rows (columns: rrn, amount_inr, debited_ts, till_status, refund_requested_ts):
  615908004963 | 1325.54 | 2026-06-08T08:40:21 |  | 
  615909004985 | 564.24 | 2026-06-08T09:09:15 |  | 
  617119013392 | 174.42 | 2026-06-20T19:44:43 |  | 
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join UPI refund records on psp upi report.rrn = upi refunds.rrn; keep rows where psp upi report.status = 'success' and (pos payments.rrn is empty or pos payments.till_status != 'approved') and (upi refunds.rrn is empty or upi refunds.completed_ts is empty); report rrn = psp upi report.rrn, amount_inr = psp upi report.amount_inr, debited_ts = psp upi report.status_ts, till_status = pos payments.till_status, refund_requested_ts = upi refunds.requested_ts; sorted by debited_ts asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q209: Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts the June bills on the tills, to check the 30,077.)
bills = 30077; payment_attempts = 30949
  How it was found: From payment attempt records; keep rows where day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills = count distinct of pos payments.bill_id, payment_attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: Checks that each June bill has exactly one approved payment by setting approved payments against the bills that have one.)
approved_payments = 30077; bills_with_approved_payment = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report approved_payments = count of *, bills_with_approved_payment = count distinct of pos payments.bill_id.
Part 3: figures from the ontology layer. (Plan covers: One approved payment per bill cannot rule out a double charge, so this counts June provider successes with no approved till payment (definition: Extra debit; Rule 10).)
extra_debits = 26; extra_debit_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.rrn is empty or pos payments.till_status != 'approved') and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; report extra_debits = count of *, extra_debit_inr = sum of psp upi report.amount_inr.

## Q210: Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.

Answered from the ontology layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the 48 June UPI timeouts and how many carry an RRN; a timeout has no RRN, so a join on RRN cannot reach them.)
upi_timeouts = 48; timeouts_with_rrn = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report upi_timeouts = count of *, timeouts_with_rrn = count of pos payments.rrn.
Part 2: figures from the ontology layer. (Plan covers: Instead of the RRN join, reads the timeouts' final status from June provider transactions whose RRN never reached the till, by status (Rule 9: UPI's final status decides).)
3 rows (columns: provider_status, transactions, amount_inr):
  failed | 16 | 7621.18
  returned | 6 | 1656.83
  success | 26 | 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where pos payments.rrn is empty and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; group by psp upi report.status; report provider_status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr.

## Q211: Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the 0.76% against June UPI attempts by till status (definition: UPI technical failure rate, 'failed' plus 'failed: no response' over all UPI attempts, shown with and without timeouts).)
4 rows (columns: till_status, upi_attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by pos payments.till_status; report till_status = pos payments.till_status, upi_attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: Shows when June's UPI technical failures happened, by day and clock hour, so a burst hidden inside a low monthly rate comes to light (Rule 12).)
139 rows (columns: pay_date, clock_hour, technical_failures):
  2026-06-20 | 19 | 19
  2026-06-20 | 18 | 13
  2026-06-21 | 19 | 3
  2026-06-03 | 16 | 2
  2026-06-04 | 21 | 2
  2026-06-06 | 9 | 2
  2026-06-06 | 11 | 2
  2026-06-07 | 20 | 2
  2026-06-08 | 8 | 2
  2026-06-08 | 18 | 2
  ... and 129 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts), hour(pos payments.ts); report pay_date = day(pos payments.ts), clock_hour = hour(pos payments.ts), technical_failures = count of *; sorted by technical_failures desc.

## Q212: Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Settlement credits around 20 and 21 June; why credits are in suspense and when finance may recognize unclaimed revenue are not recorded.)
3 rows (columns: settlement_date, upi_credits, gross_inr):
  2026-06-20 | 824.0 | 510195.41
  2026-06-21 | 607.0 | 367003.47
  2026-06-22 | 670.0 | 423309.67
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date >= '2026-06-20' and upi settlements.settlement_date <= '2026-06-22'; report settlement_date = upi settlements.settlement_date, upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr; sorted by settlement_date asc.
Part 2: figures from the ontology layer. (Plan covers: Provider successes on 20 and 21 June with no approved till payment.)
extra_debits = 17
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and psp upi report.status_ts >= '2026-06-20' and psp upi report.status_ts < '2026-06-22' and (pos payments.till_status is empty or pos payments.till_status != 'approved'); report extra_debits = count of *.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q213: Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?

Answered from the ontology layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Refund durations from requested to completed; the RBI 5-day rule itself is not recorded and no median function exists.)
refunds = 23; avg_days = 3.217391304347826; max_days = 5.0
  How it was found: From UPI refund records; report refunds = count of *, avg_days = avg of days_between(upi refunds.requested_ts, upi refunds.completed_ts), max_days = max of days_between(upi refunds.requested_ts, upi refunds.completed_ts).
Part 2: figures from the ontology layer. (Plan covers: Refund wait from the extra debit (provider status_ts) to completion, the clock Rule 11 says to use.)
refunds = 23; avg_days = 5.161767814004713; max_days = 7.798703704029322
  How it was found: From UPI service provider's transaction records; inner-join UPI refund records on psp upi report.rrn = upi refunds.rrn; report refunds = count of *, avg_days = avg of days_between(psp upi report.status_ts, upi refunds.completed_ts), max_days = max of days_between(psp upi report.status_ts, upi refunds.completed_ts).

## Q214: For bills in payments.pos_payments that required more than one attempt (attempt > 1), what was the most common tender used on the final approved attempt after a UPI failure?

Answered from the schema layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: not answered: the ontology layer refused the plan ('1' is not a valid id).
Part 2: figures from the schema layer. (Plan covers: Shows the tender and till status of the earlier attempts that were not approved, i.e. how many were UPI failures, because one plan cannot read the table twice to tie each failure to its bill's approval.)
4 rows (columns: tender, till_status, unapproved_attempts):
  UPI | declined | 589
  UPI | failed | 145
  card | declined | 90
  UPI | failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.till_status != 'approved'; group by pos payments.tender, pos payments.till_status; report tender = pos payments.tender, till_status = pos payments.till_status, unapproved_attempts = count of *; sorted by unapproved_attempts desc.

## Q215: In payments.psp_upi_report, how many rows have a non-null bill_ref?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts provider rows and their non-null bill_ref values; bill_ref is EMPTY in every row, so provider rows reach bills only through the RRN.)
provider_rows = 19166; rows_with_bill_ref = 0
  How it was found: From UPI service provider's transaction records; report provider_rows = count of *, rows_with_bill_ref = count of psp upi report.bill_ref.

## Q216: What was the median and maximum confirmation delay (status_ts - initiated_ts, in seconds) for 'success' rows in payments.psp_upi_report on 20 June 2026 versus all other days in June?

Answered from the ontology layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Average and maximum confirmation delay (status_ts minus initiated_ts, hours times 3600 for seconds) of provider successes started on 20 June 2026.)
successes = 614; avg_delay_seconds = 651.1970685558326; max_delay_seconds = 97206.000007689
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'success' and day(psp upi report.initiated_ts) = '2026-06-20'; report successes = count of *, avg_delay_seconds = avg of hours_between(psp upi report.initiated_ts, psp upi report.status_ts) * 3600, max_delay_seconds = max of hours_between(psp upi report.initiated_ts, psp upi report.status_ts) * 3600.
Part 2: figures from the ontology layer. (Plan covers: The same for provider successes started on every other June day.)
successes = 17796; avg_delay_seconds = 0.5350078656435495; max_delay_seconds = 9023.999977111816
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'success' and day(psp upi report.initiated_ts) != '2026-06-20' and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; report successes = count of *, avg_delay_seconds = avg of hours_between(psp upi report.initiated_ts, psp upi report.status_ts) * 3600, max_delay_seconds = max of hours_between(psp upi report.initiated_ts, psp upi report.status_ts) * 3600.
Part 3: not answered: the ontology layer refused the plan (group_by cannot hold a literal).
Part 4: not answered: the ontology layer refused the plan (group_by cannot hold a literal).

## Q217: What is the total mdr_inr paid across all rows in payments.upi_settlements in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sums mdr_inr over the June 2026 settlement rows (2 to 30 June).)
mdr_inr = 0.0; settlement_days = 29
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report mdr_inr = sum of upi settlements.mdr_inr, settlement_days = count of *.

## Q218: For every refund in payments.upi_refunds, what was the median time from requested_ts to completed_ts?

Answered from the ontology layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: Lists every refund's time from requested_ts to completed_ts in order, so the median is the middle row (there is no median function); this is processing time, not the customer's wait from the extra debit (Rule 11).)
23 rows (columns: refund_id, requested_ts, completed_ts, hours_to_complete):
  RF-003319 | 2026-06-06T13:00:00 | 2026-06-08T13:00:00 | 48.0
  RF-011772 | 2026-06-20T11:00:00 | 2026-06-22T11:00:00 | 48.0
  RF-013318 | 2026-06-23T17:00:00 | 2026-06-25T17:00:00 | 48.0
  RF-013342 | 2026-06-23T10:00:00 | 2026-06-25T10:00:00 | 48.0
  RF-013343 | 2026-06-24T10:00:00 | 2026-06-26T10:00:00 | 48.0
  RF-013363 | 2026-06-22T18:00:00 | 2026-06-24T18:00:00 | 48.0
  RF-013379 | 2026-06-22T19:00:00 | 2026-06-24T19:00:00 | 48.0
  RF-008996 | 2026-06-15T19:00:00 | 2026-06-18T19:00:00 | 72.0
  RF-013351 | 2026-06-24T10:00:00 | 2026-06-27T10:00:00 | 72.0
  RF-013361 | 2026-06-23T12:00:00 | 2026-06-26T12:00:00 | 72.0
  ... and 13 more
  How it was found: From UPI refund records; report refund_id = upi refunds.refund_id, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, hours_to_complete = hours_between(upi refunds.requested_ts, upi refunds.completed_ts); sorted by hours_to_complete asc.

## Q219: How many complaints in payments.customer_complaints were resolved (resolved_ts IS NOT NULL), and what was the median resolution time (resolved_ts - complaint_ts)?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts complaints whose resolved_ts is not null.)
resolved_complaints = 26
  How it was found: From complaint records; keep rows where customer complaints.resolved_ts is not empty; report resolved_complaints = count of *.
Part 2: figures from the ontology layer. (Plan covers: Lists each resolved complaint's resolution time (resolved_ts minus complaint_ts) in order, so the median is the middle row (there is no median function).)
26 rows (columns: bill_id, kind, resolution, resolution_hours):
  B260610-050041 | debited but the till said failed | customer's bank returned the money | 1.0000000074505806
  B260625-060004 | debited but the till said failed | customer's bank returned the money | 25.00000000745058
  B260605-120088 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260618-110082 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260620-120019 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260620-120047 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260620-110055 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260620-110022 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260620-110055 | charged twice | refunded after the store matched the credit by hand | 48.0
  B260603-090023 | debited but the till said failed | customer's bank returned the money | 49.00000000745058
  ... and 16 more
  How it was found: From complaint records; keep rows where customer complaints.resolved_ts is not empty; report bill_id = customer complaints.bill_id, kind = customer complaints.kind, resolution = customer complaints.resolution, resolution_hours = hours_between(customer complaints.complaint_ts, customer complaints.resolved_ts); sorted by resolution_hours asc.

## Q220: Which complaints in payments.customer_complaints have an rrn that does not appear in payments.upi_refunds?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Lists complaints whose RRN has no row in the UPI refunds table.)
3 rows (columns: bill_id, rrn, kind, resolution, complaint_ts, amount_inr):
  B260603-090023 | 615416001875 | debited but the till said failed | customer's bank returned the money | 2026-06-04T10:00:00 | 73.65
  B260610-050041 | 616112006197 | debited but the till said failed | customer's bank returned the money | 2026-06-11T10:00:00 | 378.31
  B260625-060004 | 617613016497 | debited but the till said failed | customer's bank returned the money | 2026-06-26T10:00:00 | 215.34
  How it was found: From complaint records; left-join UPI refund records on customer complaints.rrn = upi refunds.rrn; keep rows where customer complaints.rrn is not empty and upi refunds.rrn is empty; report bill_id = customer complaints.bill_id, rrn = customer complaints.rrn, kind = customer complaints.kind, resolution = customer complaints.resolution, complaint_ts = customer complaints.complaint_ts, amount_inr = customer complaints.amount_inr; sorted by complaint_ts asc.

## Q221: On which settlement dates in payments.upi_settlements did refunds_inr exceed zero, and does the sum of refunds_inr across settlements match the sum of amount_inr in payments.upi_refunds?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Lists the settlement dates whose refunds_inr is above zero.)
11 rows (columns: settlement_date, refunds_inr):
  2026-06-09 | 224.51
  2026-06-11 | 143.11
  2026-06-15 | 532.71
  2026-06-19 | 362.94
  2026-06-23 | 963.27
  2026-06-25 | 1255.46
  2026-06-26 | 3261.02
  2026-06-27 | 556.8
  2026-06-28 | 1523.72
  2026-06-29 | 1696.46
  ... and 1 more
  How it was found: From UPI settlement records; keep rows where upi settlements.refunds_inr > 0; report settlement_date = upi settlements.settlement_date, refunds_inr = upi settlements.refunds_inr; sorted by settlement_date asc.
Part 2: figures from the schema layer. (Plan covers: Sums refunds_inr across all settlement rows, for comparison with the refund table.)
settlement_refunds_inr = 11301.86
  How it was found: From UPI settlement records; report settlement_refunds_inr = sum of upi settlements.refunds_inr.
Part 3: figures from the schema layer. (Plan covers: Sums amount_inr over all rows of the UPI refunds table, with how many completed, for comparison with the settlement total.)
refund_rows = 23; completed_refunds = 23; refund_amount_inr = 11301.86
  How it was found: From UPI refund records; report refund_rows = count of *, completed_refunds = count of upi refunds.completed_ts, refund_amount_inr = sum of upi refunds.amount_inr.

## Q222: For each day in June 2026, what share of total revenue in store.pos_lines was paid by UPI, card, and cash (joining on bill_id to approved rows in payments.pos_payments)?

Answered from the schema layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Daily takings by tender from approved payments (the bills and takings definition), with shares computed in code; pos-lines-may-june is not used for total revenue because it holds only the eleven followed items.)
84 rows (columns: day, tender, takings_inr):
  2026-06-01 | UPI | 450061.0
  2026-06-01 | card | 100846.73
  2026-06-01 | cash | 208842.24
  2026-06-02 | UPI | 401860.81
  2026-06-02 | card | 62253.18
  2026-06-02 | cash | 170621.8
  2026-06-03 | UPI | 382500.8
  2026-06-03 | card | 76673.01
  2026-06-03 | cash | 152490.89
  2026-06-04 | UPI | 346755.83
  ... and 74 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; group by day(pos payments.ts), pos payments.tender; report day = day(pos payments.ts), tender = pos payments.tender, takings_inr = sum of pos payments.amount_inr; sorted by day asc.

## Q223: Which bills in payments.pos_payments had an approved amount that did not equal the sum of line_amount for that bill_id in store.pos_lines?

Answered from the schema layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: not answered: the ontology layer refused the plan (the join to pos-payments-june repeats rows of pos-lines-may-june, so sum over them would count rows more than once).
Part 2: figures from the schema layer. (Plan covers: Counts June bills with an approved payment.)
approved_bills = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report approved_bills = count distinct of pos payments.bill_id.
Part 3: figures from the schema layer. (Plan covers: Counts June bills with any till line for the eleven followed items; bills without one have nothing to compare.)
bills_with_lines = 13851
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; report bills_with_lines = count distinct of pos lines may.bill_id.

## Q224: In payments.pos_payments, what was the average time in seconds between attempt = 1 and attempt = 2 on bills where attempt 1 had till_status = 'failed: no response' versus till_status = 'declined'?

Sorry, I'm not in a position to answer this from Store 014's records: the ontology layer refused the plan ('1' is not a valid id).

## Q225: Which bills in payments.pos_payments had three or more payment attempts, and what was the sequence of tender and till_status for each?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Finds bills with three or more payment attempts in pos-payments-june.)
25 rows (columns: bill_id, attempts):
  B260620-110032 | 4
  B260625-060004 | 3
  B260620-120072 | 3
  B260620-120041 | 3
  B260620-120034 | 3
  B260620-110055 | 3
  B260620-110016 | 3
  B260620-030007 | 3
  B260620-010048 | 3
  B260619-110143 | 3
  ... and 15 more
  How it was found: From payment attempt records; group by pos payments.bill_id; keep groups where count of * >= 3; report bill_id = pos payments.bill_id, attempts = count of pos payments.attempt; sorted by attempts desc.
Part 2: figures from the schema layer. (Plan covers: Lists the tender and till_status sequence per bill and attempt, to be filtered in code to the bills from the first plan; the 200-row limit may truncate.)
200 rows (columns: bill_id, attempt, tender, till_status):
  B260601-000000 | 1 | cash | approved
  B260601-000001 | 1 | cash | approved
  B260601-000002 | 1 | card | approved
  B260601-000003 | 1 | UPI | approved
  B260601-000004 | 1 | cash | approved
  B260601-000005 | 1 | UPI | approved
  B260601-000006 | 1 | UPI | approved
  B260601-000007 | 1 | UPI | approved
  B260601-000008 | 1 | UPI | declined
  B260601-000008 | 2 | UPI | approved
  ... and 190 more
  How it was found: From payment attempt records; report bill_id = pos payments.bill_id, attempt = pos payments.attempt, tender = pos payments.tender, till_status = pos payments.till_status; sorted by bill_id asc, attempt asc.

## Q226: Join payments.pos_payments to payments.psp_upi_report on bill_id = bill_ref to reconcile all June UPI transactions.

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: bill_ref is EMPTY in every row, so the reconciliation joins on RRN instead: June provider transactions by provider status against the till status for the same RRN, empty where the till never saw it (Rule 9).)
6 rows (columns: provider_status, till_status, transactions, provider_inr):
  success | approved | 18384 | 10785227.72
  failed | declined | 589 | 313033.23
  failed | failed | 145 | 86750.06
  success |  | 26 | 13366.06
  failed |  | 16 | 7621.18
  returned |  | 6 | 1656.83
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; group by psp upi report.status, pos payments.till_status; report provider_status = psp upi report.status, till_status = pos payments.till_status, transactions = count of *, provider_inr = sum of psp upi report.amount_inr; sorted by transactions desc.
Part 2: figures from the schema layer. (Plan covers: Counts June UPI till attempts with no RRN by till status (the timeouts), which cannot be matched to the provider report.)
till_status = failed: no response; upi_attempts_without_rrn = 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30 and pos payments.rrn is empty; group by pos payments.till_status; report till_status = pos payments.till_status, upi_attempts_without_rrn = count of *.
Part 3: figures from the ontology layer. (Plan covers: Counts June UPI till attempts whose RRN is missing from the provider report, by till status.)
No rows matched.
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-01 and 2026-06-30 and pos payments.rrn is not empty and psp upi report.rrn is empty; group by pos payments.till_status; report till_status = pos payments.till_status, till_rrns_missing_at_provider = count of *.

## Q227: How much did Store 014 pay in UPI merchant fees (mdr_inr) in June 2026, and why was it ₹8,082?

Answered from the ontology layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Sums June 2026 mdr_inr to check the ₹8,082, with the gross value and credits it was charged on.)
mdr_inr = 0.0; gross_inr = 10798593.78; upi_credits = 18410.0
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report mdr_inr = sum of upi settlements.mdr_inr, gross_inr = sum of upi settlements.gross_inr, upi_credits = sum of upi settlements.upi_credits.
Part 2: figures from the ontology layer. (Plan covers: The fee terms behind the ₹8,082 are not recorded (cause not recorded), so each day's MDR is set against its gross UPI value and credits to show the rate it implies.)
28 rows (columns: settlement_date, upi_credits, gross_inr, mdr_inr, mdr_share_of_gross):
  2026-06-02 | 789.0 | 450061.0 | 0.0 | 0.0
  2026-06-03 | 686.0 | 401860.81 | 0.0 | 0.0
  2026-06-04 | 624.0 | 382500.8 | 0.0 | 0.0
  2026-06-05 | 606.0 | 346898.94 | 0.0 | 0.0
  2026-06-06 | 610.0 | 366430.23 | 0.0 | 0.0
  2026-06-07 | 842.0 | 489252.16 | 0.0 | 0.0
  2026-06-08 | 574.0 | 357236.46 | 0.0 | 0.0
  2026-06-09 | 485.0 | 287842.03 | 0.0 | 0.0
  2026-06-10 | 475.0 | 288474.39 | 0.0 | 0.0
  2026-06-11 | 711.0 | 422706.24 | 0.0 | 0.0
  ... and 18 more
  How it was found: From UPI settlement records; keep rows where upi settlements.settlement_date between 2026-06-01 and 2026-06-30 and upi settlements.gross_inr > 0; report settlement_date = upi settlements.settlement_date, upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr, mdr_inr = upi settlements.mdr_inr, mdr_share_of_gross = upi settlements.mdr_inr / upi settlements.gross_inr; sorted by settlement_date asc.

## Q228: Match payments.pos_payments timeouts to payments.psp_upi_report using a 60-second window on amount_inr—does every timeout still match cleanly one-to-one?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Lists timeouts with time and amount; amount_inr is in no joinable group and timeouts have no rrn, so the 60-second amount match is a stand-in done in code, not a join, and it is not one-to-one proof.)
48 rows (columns: bill_id, ts, amount_inr):
  B260603-090023 | 2026-06-03T16:25:16 | 73.65
  B260604-140026 | 2026-06-04T21:32:26 | 143.11
  B260605-040030 | 2026-06-05T11:46:46 | 154.82
  B260605-120088 | 2026-06-05T19:58:33 | 224.51
  B260606-040056 | 2026-06-06T11:43:27 | 206.2
  B260608-010027 | 2026-06-08T08:39:27 | 1325.54
  B260608-020011 | 2026-06-08T09:08:34 | 564.24
  B260609-030032 | 2026-06-09T10:33:17 | 359.59
  B260609-040018 | 2026-06-09T11:22:07 | 532.71
  B260610-050041 | 2026-06-10T12:49:48 | 378.31
  ... and 38 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; report bill_id = pos payments.bill_id, ts = pos payments.ts, amount_inr = pos payments.amount_inr; sorted by ts asc.
Part 2: figures from the schema layer. (Plan covers: Provider rows with time and amount, for the same stand-in window match in code; the provider has no bill ref to tie a row to a bill.)
200 rows (columns: rrn, initiated_ts, amount_inr, status):
  615207000001 | 2026-06-01T07:01:03 | 161.31 | success
  615207000002 | 2026-06-01T07:01:36 | 1404.32 | success
  615207000003 | 2026-06-01T07:01:39 | 120.45 | success
  615207000007 | 2026-06-01T07:02:22 | 275.07 | success
  615207000005 | 2026-06-01T07:02:37 | 344.92 | failed
  615207000004 | 2026-06-01T07:02:41 | 955.86 | success
  615207000006 | 2026-06-01T07:02:52 | 344.92 | success
  615207000008 | 2026-06-01T07:04:57 | 1577.15 | success
  615207000009 | 2026-06-01T07:05:20 | 731.38 | success
  615207000010 | 2026-06-01T07:06:16 | 55.22 | success
  ... and 190 more
  How it was found: From UPI service provider's transaction records; report rrn = psp upi report.rrn, initiated_ts = psp upi report.initiated_ts, amount_inr = psp upi report.amount_inr, status = psp upi report.status; sorted by initiated_ts asc.

## Q229: Did any customer complain about being charged twice when they were actually refunded by their own bank (status = 'returned')?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Lists 'charged twice' complaints whose RRN the provider reports as 'returned', meaning the customer's own bank had sent the money back.)
No rows matched.
  How it was found: From complaint records; inner-join UPI service provider's transaction records on customer complaints.rrn = psp upi report.rrn; keep rows where customer complaints.kind = 'charged twice' and psp upi report.status = 'returned'; report bill_id = customer complaints.bill_id, rrn = customer complaints.rrn, amount_inr = customer complaints.amount_inr, complaint_ts = customer complaints.complaint_ts, resolution = customer complaints.resolution, provider_status_ts = psp upi report.status_ts; sorted by complaint_ts asc.

## Q230: Since payments.upi_settlements.net_inr equals gross_inr - refunds_inr - mdr_inr on every day, does the store's bank account reconcile cleanly with the tills?

Answered from the schema layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Per-day UPI money approved at the till (one of the three witnesses in rule 9); the day is compared with settlement_date in code because no join key links them.)
28 rows (columns: day, till_upi_approved_inr):
  2026-06-01 | 450061.0
  2026-06-02 | 401860.81
  2026-06-03 | 382500.8
  2026-06-04 | 346755.83
  2026-06-05 | 366205.72
  2026-06-06 | 489252.16
  2026-06-07 | 357236.46
  2026-06-08 | 285952.25
  2026-06-09 | 287941.68
  2026-06-10 | 422706.24
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved'; group by day(pos payments.ts); report day = day(pos payments.ts), till_upi_approved_inr = sum of pos payments.amount_inr; sorted by day asc.
Part 2: figures from the schema layer. (Plan covers: Per-day bank settlement rows, to test net equals gross minus refunds minus mdr and gross against the till figure in code.)
29 rows (columns: settlement_date, gross_inr, refunds_inr, mdr_inr, net_inr):
  2026-06-02 | 450061.0 | 0.0 | 0.0 | 450061.0
  2026-06-03 | 401860.81 | 0.0 | 0.0 | 401860.81
  2026-06-04 | 382500.8 | 0.0 | 0.0 | 382500.8
  2026-06-05 | 346898.94 | 0.0 | 0.0 | 346898.94
  2026-06-06 | 366430.23 | 0.0 | 0.0 | 366430.23
  2026-06-07 | 489252.16 | 0.0 | 0.0 | 489252.16
  2026-06-08 | 357236.46 | 0.0 | 0.0 | 357236.46
  2026-06-09 | 287842.03 | 224.51 | 0.0 | 287617.52
  2026-06-10 | 288474.39 | 0.0 | 0.0 | 288474.39
  2026-06-11 | 422706.24 | 143.11 | 0.0 | 422563.13
  ... and 19 more
  How it was found: From UPI settlement records; report settlement_date = upi settlements.settlement_date, gross_inr = upi settlements.gross_inr, refunds_inr = upi settlements.refunds_inr, mdr_inr = upi settlements.mdr_inr, net_inr = upi settlements.net_inr; sorted by settlement_date asc.

## Q231: List every rrn in payments.psp_upi_report that failed to settle in payments.upi_settlements.

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Settlement is recorded only as daily totals with no RRN, so which RRN failed to settle is not recorded; provider successes per day are the side to compare with the settlement days.)
28 rows (columns: success_date, provider_successes, success_inr):
  2026-06-01 | 789 | 450061.0
  2026-06-02 | 686 | 401860.81
  2026-06-03 | 624 | 382500.8
  2026-06-04 | 606 | 346898.94
  2026-06-05 | 610 | 366430.23
  2026-06-06 | 842 | 489252.16
  2026-06-07 | 574 | 357236.46
  2026-06-08 | 485 | 287842.03
  2026-06-09 | 475 | 288474.39
  2026-06-10 | 711 | 422706.24
  ... and 18 more
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'success'; group by day(psp upi report.status_ts); report success_date = day(psp upi report.status_ts), provider_successes = count of *, success_inr = sum of psp upi report.amount_inr; sorted by success_date asc.
Part 2: figures from the schema layer. (Plan covers: Daily settlement credits and gross value, where a shortfall against the provider's successes shows when unsettled transactions would sit, without naming their RRNs.)
29 rows (columns: settlement_date, upi_credits, gross_inr):
  2026-06-02 | 789.0 | 450061.0
  2026-06-03 | 686.0 | 401860.81
  2026-06-04 | 624.0 | 382500.8
  2026-06-05 | 606.0 | 346898.94
  2026-06-06 | 610.0 | 366430.23
  2026-06-07 | 842.0 | 489252.16
  2026-06-08 | 574.0 | 357236.46
  2026-06-09 | 485.0 | 287842.03
  2026-06-10 | 475.0 | 288474.39
  2026-06-11 | 711.0 | 422706.24
  ... and 19 more
  How it was found: From UPI settlement records; report settlement_date = upi settlements.settlement_date, upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr; sorted by settlement_date asc.

## Q232: Which payment app (Google Pay, PhonePe, Paytm) had the highest timeout rate at Store 014 on 20 June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No record holds the customer's payment app (tender is only 'UPI'), so this gives the UPI timeout rate on 20 June 2026 across all apps, by till status.)
4 rows (columns: till_status, upi_attempts):
  approved | 597
  declined | 20
  failed | 7
  failed: no response | 29
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) = '2026-06-20'; group by pos payments.till_status; report till_status = pos payments.till_status, upi_attempts = count of *.

## Q233: What was the customer's phone number or UPI VPA (@okaxis, @ybl) for the 24 double-charged bills?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: No table records a customer's phone number or UPI VPA (person identity), so this only checks the 24 against extra debits (definition: Extra debit) and how many tie to a bill through the till's RRN.)
extra_debits = 26; bills_tied_by_rrn = 0
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.rrn is empty or pos payments.till_status != 'approved'); report extra_debits = count of *, bills_tied_by_rrn = count distinct of pos payments.bill_id.

## Q234: How much does a price change move demand for 5 kg atta (price elasticity)?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Daily sales units and revenue of 5 kg atta as a stand-in; demand is not recorded and price changes are not logged, so elasticity cannot be measured.)
28 rows (columns: date, units_sold, revenue_inr):
  2026-06-01 | 30.0 | 7950.0
  2026-06-02 | 36.0 | 9540.0
  2026-06-03 | 22.0 | 5830.0
  2026-06-04 | 28.0 | 7420.0
  2026-06-05 | 32.0 | 8480.0
  2026-06-06 | 25.0 | 6625.0
  2026-06-07 | 44.0 | 11660.0
  2026-06-08 | 9.0 | 2385.0
  2026-06-09 | 11.0 | 2915.0
  2026-06-10 | 22.0 | 5830.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG'; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q235: Which promotion or discount worked best at Store 014 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Units sold at each till price per item as a stand-in; promotions and discounts are not recorded.)
11 rows (columns: sku, unit_price, units):
  ATTA-WW-10KG | 499.0 | 568.0
  ATTA-WW-1KG | 58.0 | 1569.0
  ATTA-WW-5KG | 265.0 | 1198.0
  BREAD-WHITE-400G | 45.0 | 3384.0
  CURD-500G | 32.0 | 3900.0
  DAL-TOOR-1KG | 168.0 | 1012.0
  MILK-FC-500ML | 34.0 | 6089.0
  MILK-TONED-500ML | 26.0 | 17445.0
  OIL-SUN-1L | 152.0 | 1522.0
  RICE-SM-5KG | 349.0 | 1252.0
  ... and 1 more
  How it was found: From till line records; group by pos lines may.sku_scanned, pos lines may.unit_price; report sku = pos lines may.sku_scanned, unit_price = pos lines may.unit_price, units = sum of pos lines may.qty; sorted by sku asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q236: Is Store 014 profitable overall in June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Profit needs costs the records do not hold (rent, staff and other overheads; only one cost per product), so this gives the recorded side, June takings from approved payments (definition: Bills and takings).)
bills = 30077; takings_inr = 17570666.87
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills = count of *, takings_inr = sum of pos payments.amount_inr.
Part 2: figures from the ontology layer. (Plan covers: List margin on the eleven followed items in June, revenue minus units times the single cost per product, a stand-in rather than a real margin.)
11 rows (columns: sku, units, revenue_inr, list_cost_inr, list_margin_inr):
  RICE-SM-5KG | 609.0 | 212541.0 | 183309.0 | 29232.0
  ATTA-WW-5KG | 567.0 | 150255.0 | 129276.0 | 20979.0
  ATTA-WW-10KG | 287.0 | 143213.0 | 123697.0 | 19516.0
  OIL-SUN-1L | 747.0 | 113544.0 | 100098.0 | 13446.0
  DAL-TOOR-1KG | 539.0 | 90552.0 | 78694.0 | 11858.0
  MILK-TONED-500ML | 8649.0 | 224874.0 | 213630.3 | 11243.700000000012
  BREAD-WHITE-400G | 1674.0 | 75330.0 | 65286.0 | 10044.0
  ATTA-WW-1KG | 826.0 | 47908.0 | 40887.0 | 7021.0
  MILK-FC-500ML | 2916.0 | 99144.0 | 94186.79999999999 | 4957.200000000012
  CURD-500G | 1942.0 | 62144.0 | 57289.0 | 4855.0
  ... and 1 more
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.sku; report sku = daily sales.sku, units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, list_cost_inr = sum of daily sales.units_sold * max of products.cost_inr, list_margin_inr = sum of daily sales.revenue_inr - sum of daily sales.units_sold * max of products.cost_inr; sorted by list_margin_inr desc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q237: What was Store 014's gross margin on 5 kg atta in June 2026, using real purchase costs, rebates and freight?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: Real purchase costs, rebates and freight are not recorded (only one cost per product), so this gives the June list margin on 5 kg atta, revenue minus units times that single cost.)
units = 567.0; revenue_inr = 150255.0; list_cost_inr = 129276.0; list_margin_inr = 20979.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, list_cost_inr = sum of daily sales.units_sold * max of products.cost_inr, list_margin_inr = sum of daily sales.revenue_inr - sum of daily sales.units_sold * max of products.cost_inr.
Stand-ins used (not the real thing): list_margin (else): selling price minus the single cost per product is a list margin, not a real margin

## Q238: Which product earns the most per square foot of shelf at Store 014?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Shelf space is not recorded, so earnings per square foot cannot be worked out; this ranks the eleven followed products by recorded revenue and list margin (selling price minus the single cost per product).)
11 rows (columns: sku, revenue_inr, units, list_margin_inr):
  RICE-SM-5KG | 212541.0 | 609.0 | 29232.0
  ATTA-WW-5KG | 150255.0 | 567.0 | 20979.0
  ATTA-WW-10KG | 143213.0 | 287.0 | 19516.0
  OIL-SUN-1L | 113544.0 | 747.0 | 13446.0
  DAL-TOOR-1KG | 90552.0 | 539.0 | 11858.0
  MILK-TONED-500ML | 224874.0 | 8649.0 | 11243.700000000012
  BREAD-WHITE-400G | 75330.0 | 1674.0 | 10044.0
  ATTA-WW-1KG | 47908.0 | 826.0 | 7021.0
  MILK-FC-500ML | 99144.0 | 2916.0 | 4957.200000000012
  CURD-500G | 62144.0 | 1942.0 | 4855.0
  ... and 1 more
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; group by daily sales.sku; report sku = daily sales.sku, revenue_inr = sum of daily sales.revenue_inr, units = sum of daily sales.units_sold, list_margin_inr = sum of daily sales.revenue_inr - sum of daily sales.units_sold * max of products.cost_inr; sorted by list_margin_inr desc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q239: Will a shelf camera at Store 014 pay for itself?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: On-shelf versus empty audit rows (11:00 snapshots) as the only evidence; camera cost, lost sales and payback are not recorded.)
2 rows (columns: status, audits):
  empty | 3
  on shelf | 85
  How it was found: From shelf-audit row records; group by shelf audits.status; report status = shelf audits.status, audits = count of *.

## Q240: What is the selling price in rupees of 5 kg atta?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Gives the recorded selling price of 5 kg atta (ATTA-WW-5KG) from the product list.)
sku = ATTA-WW-5KG; name = Whole wheat atta 5 kg; pack = 5 kg; price_inr = 265.0
  How it was found: From product records; keep rows where products.sku = 'ATTA-WW-5KG'; report sku = products.sku, name = products.name, pack = products.pack, price_inr = products.price_inr.

## Q241: What are Store 014's monthly rent and staff costs?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q242: What wholesale price did Store 014 pay for rice on 12 June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: No dated purchase or wholesale price is recorded (only one cost per product), so this gives the rice's single recorded cost as a stand-in for what was paid on 12 June.)
sku = RICE-SM-5KG; name = Sona masoori rice 5 kg; pack = 5 kg; cost_inr = 301.0
  How it was found: From product records; keep rows where products.sku = 'RICE-SM-5KG'; report sku = products.sku, name = products.name, pack = products.pack, cost_inr = products.cost_inr.
Part 2: figures from the schema layer. (Plan covers: Checks whether any rice was received at the back door on 12 June 2026.)
No rows matched.
  How it was found: From goods-receipt line records; keep rows where goods receipts.sku_booked = 'RICE-SM-5KG' and day(goods receipts.received_ts) = '2026-06-12'; report grn_id = goods receipts.grn_id, received_ts = goods receipts.received_ts, units_booked = goods receipts.units_booked; sorted by received_ts asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q243: How many of Store 014's products have a selling price above 100 rupees?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts products in the product list (the eleven recorded items) whose selling price is above ₹100.)
products_over_100_inr = 5
  How it was found: From product records; keep rows where products.price_inr > 100; report products_over_100_inr = count of *.

## Q244: What was the profit on Store 014's June 2026 sales of rice?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the ontology layer. (Plan covers: Real profit is not recorded (one cost per product and no other costs), so this gives the June list margin on Sona masoori rice 5 kg, revenue minus units times its single cost.)
units = 609.0; revenue_inr = 212541.0; list_cost_inr = 183309.0; list_margin_inr = 29232.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.sku = 'RICE-SM-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, list_cost_inr = sum of daily sales.units_sold * max of products.cost_inr, list_margin_inr = sum of daily sales.revenue_inr - sum of daily sales.units_sold * max of products.cost_inr.

## Q245: What is the cost of 1 kg sugar, in rupees?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Gives the single recorded cost price of 1 kg sugar (SUGAR-1KG) from the product list.)
sku = SUGAR-1KG; name = Sugar 1 kg; cost_inr = 42.0
  How it was found: From product records; keep rows where products.sku = 'SUGAR-1KG'; report sku = products.sku, name = products.name, cost_inr = products.cost_inr.

## Q246: What is the gross margin percentage ((price_inr - cost_inr) / price_inr) for every SKU in store.products, ranked highest to lowest?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Computes (price_inr - cost_inr) / price_inr as a percentage for every product, highest first; with one cost per product it is a list margin, not a real margin.)
11 rows (columns: sku, name, price_inr, cost_inr, gross_margin_pct):
  ATTA-WW-1KG | Whole wheat atta 1 kg | 58.0 | 49.5 | 14.655172413793101
  ATTA-WW-5KG | Whole wheat atta 5 kg | 265.0 | 228.0 | 13.962264150943396
  RICE-SM-5KG | Sona masoori rice 5 kg | 349.0 | 301.0 | 13.753581661891118
  ATTA-WW-10KG | Whole wheat atta 10 kg | 499.0 | 431.0 | 13.627254509018035
  BREAD-WHITE-400G | White bread 400 g | 45.0 | 39.0 | 13.333333333333334
  DAL-TOOR-1KG | Toor dal 1 kg | 168.0 | 146.0 | 13.095238095238097
  SUGAR-1KG | Sugar 1 kg | 48.0 | 42.0 | 12.5
  OIL-SUN-1L | Sunflower oil 1 L pouch | 152.0 | 134.0 | 11.842105263157894
  CURD-500G | Curd 500 g pouch | 32.0 | 29.5 | 7.8125
  MILK-FC-500ML | Full cream milk 500 ml pouch | 34.0 | 32.3 | 5.000000000000009
  ... and 1 more
  How it was found: From product records; report sku = products.sku, name = products.name, price_inr = products.price_inr, cost_inr = products.cost_inr, gross_margin_pct = products.price_inr - products.cost_inr / products.price_inr * 100; sorted by gross_margin_pct desc.
Stand-ins used (not the real thing): list_margin (else): selling price minus the single cost per product is a list margin, not a real margin

## Q247: Since store.pos_lines.line_amount equals qty * unit_price on every row, did Store 014 offer any discounts in June 2026?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: Checks the premise by counting June till lines where line_amount is not qty times unit_price.)
lines_not_qty_times_price = 0
  How it was found: From till line records; keep rows where day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30 and pos lines may.line_amount != pos lines may.qty * pos lines may.unit_price; report lines_not_qty_times_price = count of *.
Part 2: figures from the ontology layer. (Plan covers: Discounts are not recorded as such and qty times unit price cannot reveal a cut unit price, so this finds June lines sold below the product's list price, matched on the GTIN on the pack (Rule 7).)
No rows matched.
  How it was found: From till line records; inner-join product records on pos lines may.gtin_scanned = products.gtin; keep rows where day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30 and pos lines may.unit_price < products.price_inr; group by products.sku; report sku = products.sku, lines = count of *, units = sum of pos lines may.qty, lowest_till_price = min of pos lines may.unit_price, list_price = max of products.price_inr; sorted by lines desc.

## Q248: Which brand of 5 kg atta does Store 014 sell, and who is its manufacturer?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No table records brand or manufacturer (supplier identity is not recorded); the product list holds only the name, pack and GTIN of 5 kg atta.)
sku = ATTA-WW-5KG; name = Whole wheat atta 5 kg; pack = 5 kg; gtin = 2900001001014
  How it was found: From product records; keep rows where products.sku = 'ATTA-WW-5KG'; report sku = products.sku, name = products.name, pack = products.pack, gtin = products.gtin.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q249: How many units of BREAD-WHITE-400G were sold at a markdown before expiring in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Expired bread write-offs in June as the expiry evidence; a markdown is not recorded anywhere, so units sold at a markdown cannot be counted.)
expired_units_written_off = None
  How it was found: From write-off records; keep rows where write offs.sku = 'BREAD-WHITE-400G' and write offs.reason = 'expired'; report expired_units_written_off = sum of write offs.units.
Part 2: figures from the ontology layer. (Plan covers: Units of bread on till lines priced below list price, a markdown stand-in for the eleven followed items; the expiry link is not recorded.)
units_below_list = None
  How it was found: From till line records; inner-join product records on pos lines may.sku_scanned = products.sku; keep rows where pos lines may.sku_scanned = 'BREAD-WHITE-400G' and pos lines may.unit_price < products.price_inr; report units_below_list = sum of pos lines may.qty.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q250: What was the GST rate or tax amount collected on each bill in store.pos_lines?

Sorry, I'm not in a position to answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## Q251: How many staff does Store 014 need in each hour of the day?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Staff numbers and staffing standards are not recorded, so approved June bills by hour of day are only the workload a staffing plan would start from.)
15 rows (columns: clock_hour, bills, trading_days):
  7 | 2397 | 28
  8 | 2455 | 28
  9 | 2033 | 28
  10 | 1774 | 28
  11 | 1652 | 28
  12 | 1470 | 28
  13 | 1439 | 28
  14 | 1362 | 28
  15 | 1664 | 28
  16 | 1895 | 28
  ... and 5 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by hour(pos payments.ts); report clock_hour = hour(pos payments.ts), bills = count of *, trading_days = count distinct of day(pos payments.ts); sorted by clock_hour asc.

## Q252: Which delivery driver was on milk route R-07 on 10 June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Deliveries on route R-07 on 2026-06-10 with their products; drivers are not identified in the records.)
3 rows (columns: delivery_ts, sku, units):
  2026-06-10T05:30 | MILK-TONED-500ML | 315.0
  2026-06-10T05:30 | MILK-FC-500ML | 109.0
  2026-06-10T05:30 | CURD-500G | 69.0
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.route = 'R-07' and fresh deliveries.delivery_ts >= '2026-06-10' and fresh deliveries.delivery_ts < '2026-06-11'; report delivery_ts = fresh deliveries.delivery_ts, sku = fresh deliveries.sku, units = fresh deliveries.units.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q253: Which cashier rang up the 5,000th bill of June 2026?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: No table records cashiers (person identity), so counting approved June bills by day only places the 5,000th bill on a date, not who rang it up.)
28 rows (columns: pay_date, bills):
  2026-06-01 | 1299
  2026-06-02 | 1089
  2026-06-03 | 997
  2026-06-04 | 974
  2026-06-05 | 978
  2026-06-06 | 1344
  2026-06-07 | 919
  2026-06-08 | 808
  2026-06-09 | 752
  2026-06-10 | 1139
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts); report pay_date = day(pos payments.ts), bills = count of *; sorted by pay_date asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q254: Which cashier rang up the most bills at Store 014 in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q255: Which supplier delivered the curd on route R-12 in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No table identifies suppliers (person identity), so this only shows the curd deliveries on route R-12 in June 2026.)
deliveries = 0; units = None; crates = None; first_delivery = None; last_delivery = None
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'CURD-500G' and fresh deliveries.route = 'R-12' and day(fresh deliveries.delivery_ts) between 2026-06-01 and 2026-06-30; report deliveries = count of *, units = sum of fresh deliveries.units, crates = sum of fresh deliveries.crates, first_delivery = min of fresh deliveries.delivery_ts, last_delivery = max of fresh deliveries.delivery_ts.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## Q256: Which manager requested the stock counts after complaints?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: No table names the manager (person identity), so this lists the stock counts recorded as a manager request after complaints.)
3 rows (columns: sku, count_ts, book_before, counted, adjustment):
  ATTA-WW-5KG | 2026-06-26T09:00 | 63.0 | 0.0 | -63.0
  ATTA-WW-1KG | 2026-06-26T09:00 | 106.0 | 263.0 | 157.0
  ATTA-WW-10KG | 2026-06-26T09:00 | 24.0 | 23.0 | -1.0
  How it was found: From stock count records; keep rows where stock counts.trigger = 'manager request after complaints'; report sku = stock counts.sku, count_ts = stock counts.count_ts, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment; sorted by count_ts asc.

## Q257: Which individual warehouse picker made the mis-pick at slot A-07-03 on 22 June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: No table identifies pickers (person identity; picks are confirmed by slot label scan), so this lists the picks from slot A-07-03 on 22 June 2026.)
1 rows (columns: pick_ts, order_id, shipment_id, sku, cases_ordered, cases_confirmed, confirmed_by):
  2026-06-22T03:00 | SO-260621 | SHP-260622 | ATTA-WW-5KG | 16.0 | 16.0 | slot label scan
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.slot = 'A-07-03' and day(dc pick confirmations.pick_ts) = '2026-06-22'; report pick_ts = dc pick confirmations.pick_ts, order_id = dc pick confirmations.order_id, shipment_id = dc pick confirmations.shipment_id, sku = dc pick confirmations.sku, cases_ordered = dc pick confirmations.cases_ordered, cases_confirmed = dc pick confirmations.cases_confirmed, confirmed_by = dc pick confirmations.confirmed_by; sorted by pick_ts asc.
Part 2: figures from the schema layer. (Plan covers: Lists the warehouse stock corrections at slot A-07-03, the recorded trace of the mis-pick (Rule 5: mirror-image corrections are one event).)
adjusted_ts = 2026-06-25T10:00; sku = ATTA-WW-5KG; reason = cycle count variance; cases = 16.0; units = 64.0; value_at_cost_inr = 14592.0
  How it was found: From warehouse (DC) stock adjustment records; keep rows where dc stock adjustments.slot = 'A-07-03'; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, reason = dc stock adjustments.reason, cases = dc stock adjustments.cases, units = dc stock adjustments.units, value_at_cost_inr = dc stock adjustments.value_at_cost_inr; sorted by adjusted_ts asc.

## Q258: Why did shoppers choose another store instead of Store 014 in June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Nothing records shoppers who went to another store or why (absent event, cause), so approved bills per day, the stand-in for shoppers, only show whether visits fell.)
28 rows (columns: pay_date, bills, takings_inr):
  2026-06-01 | 1299 | 759749.97
  2026-06-02 | 1089 | 634735.79
  2026-06-03 | 997 | 611664.7
  2026-06-04 | 974 | 572639.82
  2026-06-05 | 978 | 568176.8
  2026-06-06 | 1344 | 788949.61
  2026-06-07 | 919 | 540699.36
  2026-06-08 | 808 | 486541.3
  2026-06-09 | 752 | 432491.33
  2026-06-10 | 1139 | 672193.94
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts); report pay_date = day(pos payments.ts), bills = count of *, takings_inr = sum of pos payments.amount_inr; sorted by pay_date asc.
Part 2: figures from the schema layer. (Plan covers: Shelf-audit results by product show when shoppers met an empty shelf at 11:00 (Rule 3), without saying that anyone left because of it.)
13 rows (columns: sku, status, audits):
  ATTA-WW-10KG | on shelf | 8
  ATTA-WW-1KG | on shelf | 8
  ATTA-WW-5KG | empty | 2
  ATTA-WW-5KG | on shelf | 6
  BREAD-WHITE-400G | on shelf | 8
  CURD-500G | on shelf | 8
  DAL-TOOR-1KG | on shelf | 8
  MILK-FC-500ML | on shelf | 8
  MILK-TONED-500ML | on shelf | 8
  OIL-SUN-1L | on shelf | 8
  ... and 3 more
  How it was found: From shelf-audit row records; group by shelf audits.sku, shelf audits.status; report sku = shelf audits.sku, status = shelf audits.status, audits = count of *; sorted by sku asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## Q259: What is Store 014's market share in its area?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: The area's market and competitors are not recorded (external), so market share cannot be worked out; this gives only Store 014's own side, its bills and takings in the June records.)
bills = 30077; takings_inr = 17570666.87
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; report bills = count of *, takings_inr = sum of pos payments.amount_inr.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q260: How did weather, festivals or local events change Store 014's sales in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Daily sales of the eleven followed items in June; weather, festivals and local events are not recorded.)
28 rows (columns: date, units, revenue_inr):
  2026-06-01 | 685.0 | 46285.0
  2026-06-02 | 768.0 | 49259.0
  2026-06-03 | 666.0 | 47526.0
  2026-06-04 | 587.0 | 40931.0
  2026-06-05 | 672.0 | 54183.0
  2026-06-06 | 846.0 | 60629.0
  2026-06-07 | 744.0 | 57355.0
  2026-06-08 | 605.0 | 34615.0
  2026-06-09 | 763.0 | 39685.0
  2026-06-10 | 691.0 | 46180.0
  ... and 18 more
  How it was found: From daily sales row records; group by daily sales.date; report date = daily sales.date, units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr; sorted by date asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q261: How does Store 014 compare with the chain's other stores?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Nothing about the chain's other stores is recorded (external), so this gives only Store 014's own June bills and takings, its side of any comparison.)
bills = 30077; takings_inr = 17570666.87; trading_days = 28
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; report bills = count of *, takings_inr = sum of pos payments.amount_inr, trading_days = count distinct of day(pos payments.ts).
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q262: Does Store 014 comply with food-safety and labelling rules?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Food-safety and labelling rules and inspections are not recorded (external), so write-offs by product and reason, including expired stock, are the recorded trace of expiry control.)
8 rows (columns: sku, reason, units_written_off):
  ATTA-WW-5KG | damaged | 3.0
  CURD-500G | damaged | 3.0
  DAL-TOOR-1KG | damaged | 1.0
  MILK-FC-500ML | expired | 198.0
  MILK-TONED-500ML | damaged | 5.0
  MILK-TONED-500ML | expired | 291.0
  RICE-SM-5KG | damaged | 2.0
  SUGAR-1KG | damaged | 1.0
  How it was found: From write-off records; group by write offs.sku, write offs.reason; report sku = write offs.sku, reason = write offs.reason, units_written_off = sum of write offs.units; sorted by sku asc.
Part 2: figures from the schema layer. (Plan covers: Lists fresh deliveries that arrived on or after their use-by date, the one food-safety check the records allow, while nothing records labelling.)
No rows matched.
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.use_by <= day(fresh deliveries.delivery_ts); report delivery_ts = fresh deliveries.delivery_ts, sku = fresh deliveries.sku, route = fresh deliveries.route, use_by = fresh deliveries.use_by, units = fresh deliveries.units; sorted by delivery_ts asc.

## Q263: What did the nearest competitor charge for 5 kg atta in June 2026?

Answered from the knowledge layer (1 of 1 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Competitor prices are not recorded (external), so this gives only Store 014's own June till prices for 5 kg atta.)
unit_price = 265.0; bags = 567.0; lines = 560
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; group by pos lines may.unit_price; report unit_price = pos lines may.unit_price, bags = sum of pos lines may.qty, lines = count of *; sorted by unit_price asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q264: How many sales did Store 014 lose to the road closure on 14 June 2026?

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Recorded sales on 14 June for the eleven followed items; the road closure is not recorded (cause), and lost sales are not recorded, so this is the sales side only.)
units_sold = 660.0; revenue_inr = 46233.0
  How it was found: From daily sales row records; keep rows where daily sales.date = '2026-06-14'; report units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr.
Part 2: figures from the schema layer. (Plan covers: Forecast units for 14 June as a demand stand-in, to be set against recorded sales; by rule 3 the lost sales are an estimate (forecast minus sales) with the method stated, not a record.)
forecast_demand_units = 151.05
  How it was found: From forecast row records; keep rows where forecasts.date = '2026-06-14'; report forecast_demand_units = sum of forecasts.forecast_units_per_day.

## Q265: Which festival caused the sales spike in June 2026?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Figures from the schema layer. (Plan covers: Festivals are not recorded (external, cause), so approved bills and takings per day in June only show whether and when a spike happened.)
28 rows (columns: pay_date, bills, takings_inr):
  2026-06-01 | 1299 | 759749.97
  2026-06-02 | 1089 | 634735.79
  2026-06-03 | 997 | 611664.7
  2026-06-04 | 974 | 572639.82
  2026-06-05 | 978 | 568176.8
  2026-06-06 | 1344 | 788949.61
  2026-06-07 | 919 | 540699.36
  2026-06-08 | 808 | 486541.3
  2026-06-09 | 752 | 432491.33
  2026-06-10 | 1139 | 672193.94
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts); report pay_date = day(pos payments.ts), bills = count of *, takings_inr = sum of pos payments.amount_inr; sorted by pay_date asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q266: Which days in June 2026 had a power outage or internet disruption at Store 014?

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Power and internet outages are not recorded, so UPI technical failures per day are only the payment-side trace a connectivity problem would leave, not proof of one.)
28 rows (columns: pay_date, technical_failures):
  2026-06-01 | 5
  2026-06-02 | 3
  2026-06-03 | 6
  2026-06-04 | 4
  2026-06-05 | 7
  2026-06-06 | 4
  2026-06-07 | 4
  2026-06-08 | 8
  2026-06-09 | 5
  2026-06-10 | 11
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts); report pay_date = day(pos payments.ts), technical_failures = count of *; sorted by pay_date asc.
Part 2: figures from the schema layer. (Plan covers: Approved bills per day with the first and last bill time, where a power cut would show as a short or quiet trading day.)
28 rows (columns: pay_date, bills, first_bill_ts, last_bill_ts):
  2026-06-01 | 1299 | 2026-06-01T07:00:07 | 2026-06-01T21:59:15
  2026-06-02 | 1089 | 2026-06-02T07:00:10 | 2026-06-02T21:58:41
  2026-06-03 | 997 | 2026-06-03T07:00:14 | 2026-06-03T21:59:46
  2026-06-04 | 974 | 2026-06-04T07:00:48 | 2026-06-04T21:57:40
  2026-06-05 | 978 | 2026-06-05T07:00:14 | 2026-06-05T21:57:35
  2026-06-06 | 1344 | 2026-06-06T07:01:12 | 2026-06-06T21:59:35
  2026-06-07 | 919 | 2026-06-07T07:02:19 | 2026-06-07T21:59:49
  2026-06-08 | 808 | 2026-06-08T07:01:20 | 2026-06-08T21:59:39
  2026-06-09 | 752 | 2026-06-09T07:01:55 | 2026-06-09T21:58:47
  2026-06-10 | 1139 | 2026-06-10T07:00:19 | 2026-06-10T21:58:19
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; group by day(pos payments.ts); report pay_date = day(pos payments.ts), bills = count of *, first_bill_ts = min of pos payments.ts, last_bill_ts = max of pos payments.ts; sorted by pay_date asc.

## Q267: How many products does Store 014 sell in these records?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts the rows of the product list, one per product sold.)
products = 11
  How it was found: From product records; report products = count of *.

## Q268: Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?

Answered from the ontology layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the ontology layer. (Plan covers: The records do not list 12 joins, so four key ones are checked, starting with receipts against shipping notices on pallet label and SKU, where a zero unit gap means the receipt copies the notice rather than observing the pallet (Rule 12).)
joined_lines = 70; asn_vs_notice_unit_gap = 0.0; booked_vs_notice_unit_gap = 0.0
  How it was found: From goods-receipt line records; inner-join shipping-notice line records on goods receipts.sscc = shipping notice lines.sscc and goods receipts.asn_sku = shipping notice lines.sku; report joined_lines = count of *, asn_vs_notice_unit_gap = sum of abs(goods receipts.asn_units - shipping notice lines.units), booked_vs_notice_unit_gap = sum of abs(goods receipts.units_booked - shipping notice lines.units).
Part 2: figures from the ontology layer. (Plan covers: Pick confirmations against shipping-notice lines on order and SKU, which, being confirmed by slot label scan, copy the order unless the case counts disagree (Rule 7, Rule 12).)
joined_lines = 70; confirmed_vs_notice_case_gap = 0.0
  How it was found: From pick confirmation records; inner-join shipping-notice line records on dc pick confirmations.order_id = shipping notice lines.order_id and dc pick confirmations.sku = shipping notice lines.sku; report joined_lines = count of *, confirmed_vs_notice_case_gap = sum of abs(dc pick confirmations.cases_confirmed - shipping notice lines.cases).
Part 3: figures from the ontology layer. (Plan covers: Till payments against the provider report on RRN, where a till status that disagrees with the provider's is two independent witnesses disagreeing (Rule 9, Rule 12).)
3 rows (columns: till_status, provider_status, rows, amount_gap_inr):
  approved | success | 18384 | 0.0
  declined | failed | 589 | 0.0
  failed | failed | 145 | 0.0
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; group by pos payments.till_status, psp upi report.status; report till_status = pos payments.till_status, provider_status = psp upi report.status, rows = count of *, amount_gap_inr = sum of abs(pos payments.amount_inr - psp upi report.amount_inr); sorted by rows desc.
Part 4: figures from the ontology layer. (Plan covers: Till lines against the product list on the GTIN on the pack, where a scanned SKU that differs from the GTIN's SKU is a disagreement (Rule 7).)
11 rows (columns: sku_scanned, sku_of_gtin, lines):
  MILK-TONED-500ML | MILK-TONED-500ML | 14655
  MILK-FC-500ML | MILK-FC-500ML | 5728
  CURD-500G | CURD-500G | 3755
  BREAD-WHITE-400G | BREAD-WHITE-400G | 3266
  ATTA-WW-1KG | ATTA-WW-1KG | 1546
  OIL-SUN-1L | OIL-SUN-1L | 1502
  RICE-SM-5KG | RICE-SM-5KG | 1234
  ATTA-WW-5KG | ATTA-WW-5KG | 1177
  SUGAR-1KG | SUGAR-1KG | 1050
  DAL-TOOR-1KG | DAL-TOOR-1KG | 1006
  ... and 1 more
  How it was found: From till line records; inner-join product records on pos lines may.gtin_scanned = products.gtin; group by pos lines may.sku_scanned, products.sku; report sku_scanned = pos lines may.sku_scanned, sku_of_gtin = products.sku, lines = count of *; sorted by lines desc.

## Q269: How many days in June 2026 did Store 014 stay open—30 or 28?

Answered from the knowledge layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Opening days are not recorded, so days with approved bills stand in, and the till records stop at 28 June, so 29 and 30 June are unrecorded rather than shown closed.)
days_with_bills = 28; first_bill_ts = 2026-06-01T07:00:07; last_bill_ts = 2026-06-28T21:56:21
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report days_with_bills = count distinct of day(pos payments.ts), first_bill_ts = min of pos payments.ts, last_bill_ts = max of pos payments.ts.
Part 2: figures from the schema layer. (Plan covers: Settlement dates with UPI credits, which run to 30 June and credit earlier days' sales, are a second witness on which days the store traded.)
settlement_days_with_credits = 28; first_date = 2026-06-02; last_date = 2026-06-29
  How it was found: From UPI settlement records; keep rows where upi settlements.upi_credits > 0 and upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report settlement_days_with_credits = count of *, first_date = min of upi settlements.settlement_date, last_date = max of upi settlements.settlement_date.

## Q270: How many units of ghee were sold at Store 014 in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the ontology layer refused the plan (the question names 2026 but the plan has no date in that year and the records are not from that year).

## Q271: How many units of atta were sold in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sums June 2026 units sold of each atta pack (1 kg, 5 kg and 10 kg), whose total is all atta units.)
3 rows (columns: sku, units_sold):
  ATTA-WW-10KG | 287.0
  ATTA-WW-1KG | 826.0
  ATTA-WW-5KG | 567.0
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] and daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.sku; report sku = daily sales.sku, units_sold = sum of daily sales.units_sold; sorted by sku asc.

## Q272: How many write-offs were there?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts write-off rows (one product written off on one day, 1 to 28 June) and the units they removed.)
write_offs = 34; units_written_off = 504.0
  How it was found: From write-off records; report write_offs = count of *, units_written_off = sum of write offs.units.

## Q273: How many bags of 5 kg atta did Store 015 sell in June 2026?

Sorry, I'm not in a position to answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## Q274: How many 1-litre pouches of toned milk were sold in June 2026?

Answered from the schema layer (2 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Toned milk is recorded only as 500 ml pouches; no 1-litre pouch exists, so this gives the 500 ml units for June.)
units_sold_500ml = 8649.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'MILK-TONED-500ML'; report units_sold_500ml = sum of daily sales.units_sold.

## Q275: How many kilograms of atta did Store 014 sell in June 2026?

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: June 2026 atta units by pack, so kilograms are units times the pack size in products.pack (definition: Weight; case_kg includes packaging and is not used).)
3 rows (columns: sku, pack, units_sold):
  ATTA-WW-10KG | 10 kg | 287.0
  ATTA-WW-1KG | 1 kg | 826.0
  ATTA-WW-5KG | 5 kg | 567.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] and daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.sku, products.pack; report sku = daily sales.sku, pack = products.pack, units_sold = sum of daily sales.units_sold; sorted by sku asc.

## Q276: On how many days in June 2026 was the net UPI settlement above ₹4 lakh?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts June 2026 settlement days whose net_inr is above ₹4 lakh (₹400,000).)
days_net_over_4_lakh = 10
  How it was found: From UPI settlement records; keep rows where upi settlements.net_inr > 400000 and upi settlements.settlement_date between 2026-06-01 and 2026-06-30; report days_net_over_4_lakh = count of *.

## Q277: How many bags of 5 kg atta were sold on 06/05/2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Reads 06/05/2026 day first, as 6 May 2026, and sums 5 kg atta bags on the till lines that day.)
bags = 46.0; bills = 43
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-05-06'; report bags = sum of pos lines may.qty, bills = count distinct of pos lines may.bill_id.
Part 2: figures from the schema layer. (Plan covers: Reads 06/05/2026 month first, as 5 June 2026, and gives 5 kg atta units sold that day.)
bags = 32.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date = '2026-06-05'; report bags = sum of daily sales.units_sold.

## Q278: How many bags of 5 kg atta were sold on Friday 11 June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Units on 2026-06-11, which is a Thursday, so the 'Friday' premise is wrong.)
units_sold = 1.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date = '2026-06-11'; report units_sold = sum of daily sales.units_sold.
Part 2: figures from the schema layer. (Plan covers: Units on Friday 2026-06-12, in case that day was meant.)
units_sold = 0.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date = '2026-06-12'; report units_sold = sum of daily sales.units_sold.

## Q279: How many pallets did shipment SHP-260612 carry?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Reads the pallets figure recorded for shipment SHP-260612 in shipments-june.)
No rows matched.
  How it was found: From shipment records; keep rows where shipments.shipment_id = 'SHP-260612'; report pallets = shipments.pallets.
Part 2: figures from the schema layer. (Plan covers: Counts pallet label rows for SHP-260612 in pallets-june, to check the shipment figure.)
pallet_rows = 0
  How it was found: From pallet records; keep rows where pallets.shipment_id = 'SHP-260612'; report pallet_rows = count of pallets.sscc.

## Q280: dont tell me it's not recorded—just give me a ballpark of how many shopers walked out without 5kg atta in jun 2026

Answered from the knowledge layer (3 of 3 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Shoppers who left without 5 kg atta are not recorded (lost sales, Rule 3), so the ballpark is a labelled estimate built from bills buying it per day, which give the normal daily rate and the dips.)
24 rows (columns: bill_date, bills_buying, bags):
  2026-06-01 | 30 | 30.0
  2026-06-02 | 36 | 36.0
  2026-06-03 | 22 | 22.0
  2026-06-04 | 28 | 28.0
  2026-06-05 | 32 | 32.0
  2026-06-06 | 25 | 25.0
  2026-06-07 | 43 | 44.0
  2026-06-08 | 9 | 9.0
  2026-06-09 | 11 | 11.0
  2026-06-10 | 21 | 22.0
  ... and 14 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) between 2026-06-01 and 2026-06-30; group by day(pos lines may.bill_ts); report bill_date = day(pos lines may.bill_ts), bills_buying = count distinct of pos lines may.bill_id, bags = sum of pos lines may.qty; sorted by bill_date asc.
Part 2: figures from the schema layer. (Plan covers: The 11:00 shelf audits of 5 kg atta show when the shelf was empty, so normal daily buyers times the empty days gives the estimate, bearing in mind audits are twice-weekly snapshots, not hours off the shelf.)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG'; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q281: Refund the 26 UPI payments that the provider marked successful but the tills never approved.

Answered from the knowledge layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Figures from the ontology layer. (Plan covers: Checks the 26 figure by counting provider successes with no approved till payment; this only counts, it cannot issue refunds.)
extra_debits = 26; extra_debit_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.till_status is empty or pos payments.till_status != 'approved'); report extra_debits = count of *, extra_debit_inr = sum of psp upi report.amount_inr.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## Q282: hey quick one - how many bags of 5kg aata did we actually sell in jun 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sums June 2026 units sold of 5 kg atta (ATTA-WW-5KG).)
bags = 567.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report bags = sum of daily sales.units_sold.

## Q283: Hey, could you tell me how many UPI refudns Store 014 made in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts UPI refunds requested in June 2026, how many completed, and their rupee total.)
refunds = 23; completed_refunds = 23; refund_inr = 11301.86
  How it was found: From UPI refund records; keep rows where day(upi refunds.requested_ts) between 2026-06-01 and 2026-06-30; report refunds = count of *, completed_refunds = count of upi refunds.completed_ts, refund_inr = sum of upi refunds.amount_inr.

## Q284: How many packets of sugar were sold in June 2026?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sums June 2026 units sold of 1 kg sugar packets (SUGAR-1KG).)
packets = 509.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'SUGAR-1KG' and daily sales.date between 2026-06-01 and 2026-06-30; report packets = sum of daily sales.units_sold.

## Q285: hw many upi payments timed out (no response) at the tills in june 2026 without an rrn

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Counts June 2026 UPI till attempts with till status 'failed: no response' that carry no RRN.)
timeouts_without_rrn = 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and pos payments.rrn is empty and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report timeouts_without_rrn = count of *.

## Q286: 5kg atta sales tanked 59% in week 2 even tho book stock was fine - how much shelf space shld we move to 1kg?

Answered from the schema layer (3 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Daily 5 kg atta sales in June, to check the 59% fall in week 2 (8 to 14 June) against week 1.)
28 rows (columns: sale_date, bags):
  2026-06-01 | 30.0
  2026-06-02 | 36.0
  2026-06-03 | 22.0
  2026-06-04 | 28.0
  2026-06-05 | 32.0
  2026-06-06 | 25.0
  2026-06-07 | 44.0
  2026-06-08 | 9.0
  2026-06-09 | 11.0
  2026-06-10 | 22.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.date; report sale_date = daily sales.date, bags = sum of daily sales.units_sold; sorted by sale_date asc.
Part 2: figures from the schema layer. (Plan covers: Daily closing book stock of 5 kg atta, to check that the books looked fine, remembering that book stock is a belief and not the shelf (Rule 1).)
28 rows (columns: book_date, book_on_hand_close):
  2026-06-01 | 58.0
  2026-06-02 | 22.0
  2026-06-03 | 64.0
  2026-06-04 | 36.0
  2026-06-05 | 52.0
  2026-06-06 | 27.0
  2026-06-07 | 43.0
  2026-06-08 | 34.0
  2026-06-09 | 78.0
  2026-06-10 | 56.0
  ... and 18 more
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG'; report book_date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by book_date asc.
Part 3: figures from the schema layer. (Plan covers: The 11:00 shelf audits of 5 kg atta (definition: On-shelf availability), because falling sales while the books show stock means look at the shelf (Rule 2), and demand that met an empty shelf is lost sales, not a shift in demand (Rule 3).)
8 rows (columns: audit_ts, status):
  2026-06-02T11:00 | on shelf
  2026-06-05T11:00 | on shelf
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  2026-06-16T11:00 | on shelf
  2026-06-19T11:00 | on shelf
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG'; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 4: figures from the schema layer. (Plan covers: Shelf space is not recorded, so no move can be sized; daily 1 kg atta sales only show whether shoppers switched to 1 kg when 5 kg fell.)
28 rows (columns: sale_date, packs_1kg):
  2026-06-01 | 22.0
  2026-06-02 | 35.0
  2026-06-03 | 41.0
  2026-06-04 | 24.0
  2026-06-05 | 24.0
  2026-06-06 | 52.0
  2026-06-07 | 40.0
  2026-06-08 | 27.0
  2026-06-09 | 24.0
  2026-06-10 | 41.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-1KG' and daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.date; report sale_date = daily sales.date, packs_1kg = sum of daily sales.units_sold; sorted by sale_date asc.

## Q287: join pos_payments to psp_upi_report on rrn n give me the final status of all 48 upi timeouts in june

Answered from the ontology layer (2 of 3 valid plans reached it). 2 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Checks the 48 June UPI timeouts and how many carry an RRN; a timeout has no RRN, so a join on RRN cannot reach them.)
upi_timeouts = 48; timeouts_with_rrn = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report upi_timeouts = count of *, timeouts_with_rrn = count of pos payments.rrn.
Part 2: figures from the ontology layer. (Plan covers: Instead of the RRN join, reads the timeouts' final status from June provider transactions whose RRN never reached the till, by status (Rule 9: UPI's final status decides).)
3 rows (columns: provider_status, transactions, amount_inr):
  failed | 16 | 7621.18
  returned | 6 | 1656.83
  success | 26 | 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where pos payments.rrn is empty and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; group by psp upi report.status; report provider_status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr.

## Q288: all 30077 bills have 1 approved payment so nobody got double charged right?? confirm pls

Answered from the ontology layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Part 1: figures from the schema layer. (Plan covers: Counts the June bills on the tills, to check the 30077.)
bills = 30077; payment_attempts = 30949
  How it was found: From payment attempt records; keep rows where day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills = count distinct of pos payments.bill_id, payment_attempts = count of *.
Part 2: figures from the schema layer. (Plan covers: Checks that each bill has exactly 1 approved payment by setting approved payments against the bills that have one.)
approved_payments = 30077; bills_with_approved_payment = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report approved_payments = count of *, bills_with_approved_payment = count distinct of pos payments.bill_id.
Part 3: figures from the ontology layer. (Plan covers: One approved payment per bill cannot rule out a double charge, so this counts provider successes with no approved till payment (definition: Extra debit; Rule 10).)
extra_debits = 26; extra_debit_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.rrn is empty or pos payments.till_status != 'approved') and day(psp upi report.initiated_ts) between 2026-06-01 and 2026-06-30; report extra_debits = count of *, extra_debit_inr = sum of psp upi report.amount_inr.

## Q289: how many bags of 5kg atta did we sell in june 2023??

Sorry, I'm not in a position to answer this from Store 014's records: the knowledge layer says this is not recorded: year outside 2026

## Q290: how much net proft did store 014 make in june 2026 after rent n staff salaries

Answered from the knowledge layer (2 of 2 valid plans reached it). The planners' results differ; this is the plan ranked first at that layer.
Part 1: figures from the schema layer. (Plan covers: Rent and staff salaries are not recorded (external), so net profit cannot be worked out; this gives the recorded side, June takings from approved payments (definition: Bills and takings).)
bills = 30077; takings_inr = 17570666.87
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and day(pos payments.ts) between 2026-06-01 and 2026-06-30; report bills = count of *, takings_inr = sum of pos payments.amount_inr.
Part 2: figures from the ontology layer. (Plan covers: List margin on the eleven followed items in June, revenue minus units times the single cost per product, a stand-in that is neither net profit nor a real margin.)
11 rows (columns: sku, units, revenue_inr, list_cost_inr, list_margin_inr):
  RICE-SM-5KG | 609.0 | 212541.0 | 183309.0 | 29232.0
  ATTA-WW-5KG | 567.0 | 150255.0 | 129276.0 | 20979.0
  ATTA-WW-10KG | 287.0 | 143213.0 | 123697.0 | 19516.0
  OIL-SUN-1L | 747.0 | 113544.0 | 100098.0 | 13446.0
  DAL-TOOR-1KG | 539.0 | 90552.0 | 78694.0 | 11858.0
  MILK-TONED-500ML | 8649.0 | 224874.0 | 213630.3 | 11243.700000000012
  BREAD-WHITE-400G | 1674.0 | 75330.0 | 65286.0 | 10044.0
  ATTA-WW-1KG | 826.0 | 47908.0 | 40887.0 | 7021.0
  MILK-FC-500ML | 2916.0 | 99144.0 | 94186.79999999999 | 4957.200000000012
  CURD-500G | 1942.0 | 62144.0 | 57289.0 | 4855.0
  ... and 1 more
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.date between 2026-06-01 and 2026-06-30; group by daily sales.sku; report sku = daily sales.sku, units = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, list_cost_inr = sum of daily sales.units_sold * max of products.cost_inr, list_margin_inr = sum of daily sales.revenue_inr - sum of daily sales.units_sold * max of products.cost_inr; sorted by list_margin_inr desc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## Q291: June 2026 mein 5 kilo atta ke kitne bag bike?

Answered from the schema layer (3 of 3 valid plans reached it). 3 of 3 planners reached this result.
Figures from the schema layer. (Plan covers: Sums June 2026 units sold of 5 kg atta (ATTA-WW-5KG), one unit per bag.)
bags = 567.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-30; report bags = sum of daily sales.units_sold.
