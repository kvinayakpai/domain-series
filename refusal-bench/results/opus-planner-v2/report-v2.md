# Store 014: answers to sets 8 and 9 (Opus plans, code checks and runs)

Answered (at least in part): 52 of 55.

## S8N01: How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?

Part 1: not answered: ecords: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Part 2: answered from the ontology layer. (Plan covers: Units of 5 kg atta sold in the week of 8 June (8-14 June 2026).)
units_week_of_8_june = 88.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) between 2026-06-08 and 2026-06-14; report units_week_of_8_june = sum of daily sales.units_sold.

## S8N02: Which shelf audits found an item empty while the hourly book showed stock above zero?

answered from the ontology layer. (Plan covers: Shelf audits with status empty on a day whose closing book stock was above zero; no hourly book is recorded, so the daily closing book (a belief, not the shelf) is used.)
2 rows (columns: audit_ts, sku, book_on_hand_close):
  2026-06-05T11:00 | SUGAR-1KG | 55.0
  2026-06-12T11:00 | ATTA-WW-5KG | 55.0
  How it was found: From shelf-audit row records; inner-join book-stock row records on shelf audits.sku = inventory book.sku; keep rows where shelf audits.status = 'empty' and day(shelf audits.audit_ts) = day(inventory book.date) and inventory book.book_on_hand_close > 0; report audit_ts = shelf audits.audit_ts, sku = shelf audits.sku, book_on_hand_close = inventory book.book_on_hand_close; sorted by audit_ts asc.

## S8N03: On which days did any item's closing book stock go below zero?

answered from the ontology layer. (Plan covers: Days and items whose closing book stock (inventory-book) was below zero.)
6 rows (columns: date, sku, book_on_hand_close):
  2026-06-02 | MILK-FC-500ML | -5.0
  2026-06-09 | MILK-FC-500ML | -5.0
  2026-06-11 | MILK-FC-500ML | -15.0
  2026-06-12 | MILK-FC-500ML | -12.0
  2026-06-13 | MILK-FC-500ML | -14.0
  2026-06-20 | MILK-FC-500ML | -13.0
  How it was found: From book-stock row records; keep rows where inventory book.book_on_hand_close < 0; report date = day(inventory book.date), sku = inventory book.sku, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.

## S8N04: Which stock counts disagreed with the book stock by more than 2%?

answered from the ontology layer. (Plan covers: Store stock counts where the adjustment is more than 2% of the book stock before the count.)
19 rows (columns: count_ts, sku, book_before, counted, adjustment, trigger):
  2026-06-01T05:45 | ATTA-WW-1KG | 92.0 | 87.0 | -5.0 | scheduled full count
  2026-06-01T05:45 | ATTA-WW-10KG | 28.0 | 29.0 | 1.0 | scheduled full count
  2026-06-01T05:45 | RICE-SM-5KG | 66.0 | 64.0 | -2.0 | scheduled full count
  2026-06-01T05:45 | DAL-TOOR-1KG | 15.0 | 13.0 | -2.0 | scheduled full count
  2026-06-01T05:45 | OIL-SUN-1L | 82.0 | 77.0 | -5.0 | scheduled full count
  2026-06-01T05:45 | SUGAR-1KG | 46.0 | 44.0 | -2.0 | scheduled full count
  2026-06-01T05:45 | MILK-TONED-500ML | 377.0 | 351.0 | -26.0 | scheduled full count
  2026-06-01T05:45 | MILK-FC-500ML | 94.0 | 109.0 | 15.0 | scheduled full count
  2026-06-01T05:45 | CURD-500G | 115.0 | 112.0 | -3.0 | scheduled full count
  2026-06-01T05:45 | BREAD-WHITE-400G | 64.0 | 59.0 | -5.0 | scheduled full count
  ... and 9 more
  How it was found: From stock count records; keep rows where abs(stock counts.adjustment / stock counts.book_before) > 0.02; report count_ts = stock counts.count_ts, sku = stock counts.sku, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment, trigger = stock counts.trigger; sorted by count_ts asc.

## S8N05: Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?

Part 1: answered from the ontology layer. (Plan covers: Week 1 (1-7 June) units sold per warehouse-supplied (flow DC) item; compare with week 2 for a drop of more than half.)
7 rows (columns: sku, units_week1):
  ATTA-WW-10KG | 87.0
  ATTA-WW-1KG | 238.0
  ATTA-WW-5KG | 217.0
  DAL-TOOR-1KG | 158.0
  OIL-SUN-1L | 210.0
  RICE-SM-5KG | 180.0
  SUGAR-1KG | 164.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where products.flow = 'DC' and day(daily sales.date) between 2026-06-01 and 2026-06-07; group by daily sales.sku; report sku = daily sales.sku, units_week1 = sum of daily sales.units_sold; sorted by sku asc.
Part 2: answered from the ontology layer. (Plan covers: Week 2 (8-14 June) units sold per warehouse-supplied (flow DC) item.)
7 rows (columns: sku, units_week2):
  ATTA-WW-10KG | 61.0
  ATTA-WW-1KG | 207.0
  ATTA-WW-5KG | 88.0
  DAL-TOOR-1KG | 139.0
  OIL-SUN-1L | 195.0
  RICE-SM-5KG | 153.0
  SUGAR-1KG | 117.0
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where products.flow = 'DC' and day(daily sales.date) between 2026-06-08 and 2026-06-14; group by daily sales.sku; report sku = daily sales.sku, units_week2 = sum of daily sales.units_sold; sorted by sku asc.

## S8N06: What time did toned milk record its last sale each day, and how many pouches were written off?

Part 1: answered from the ontology layer. (Plan covers: Time of the last till line for toned milk on each day (sales = till lines).)
56 rows (columns: date, last_sale_ts):
  2026-05-04 | 2026-05-04T21:59
  2026-05-05 | 2026-05-05T21:59
  2026-05-06 | 2026-05-06T21:50
  2026-05-07 | 2026-05-07T21:57
  2026-05-08 | 2026-05-08T21:56
  2026-05-09 | 2026-05-09T21:59
  2026-05-10 | 2026-05-10T21:57
  2026-05-11 | 2026-05-11T21:58
  2026-05-12 | 2026-05-12T21:47
  2026-05-13 | 2026-05-13T21:56
  ... and 46 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'MILK-TONED-500ML'; group by day(pos lines may.bill_ts); report date = day(pos lines may.bill_ts), last_sale_ts = max of pos lines may.bill_ts; sorted by date asc.
Part 2: answered from the schema layer. (Plan covers: Pouches of toned milk written off, by reason.)
2 rows (columns: reason, units_written_off):
  damaged | 5.0
  expired | 291.0
  How it was found: From write-off records; keep rows where write offs.sku = 'MILK-TONED-500ML'; group by write offs.reason; report reason = write offs.reason, units_written_off = sum of write offs.units.

## S8N07: Why did 5 kg atta sales fall in the week of 8 June?

I can't answer this from Store 014's records: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N08: Was 5 kg atta in stock on Thursday 11 June?

Part 1: answered from the ontology layer. (Plan covers: Shelf audit of 5 kg atta on 11 June (available = on the shelf at the 11:00 audit), if one was held that day.)
No rows matched.
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) = '2026-06-11'; report audit_ts = shelf audits.audit_ts, status = shelf audits.status.
Part 2: answered from the ontology layer. (Plan covers: Closing book stock of 5 kg atta on 11 June (a belief, not the shelf).)
book_on_hand_close = 55.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) = '2026-06-11'; report book_on_hand_close = inventory book.book_on_hand_close.
Part 3: answered from the ontology layer. (Plan covers: Till sales of 5 kg atta on 11 June by hour (silence while the book shows stock is a question for the shelf).)
hour = 9; units = 1.0
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-11'; group by hour(pos lines may.bill_ts); report hour = hour(pos lines may.bill_ts), units = sum of pos lines may.qty; sorted by hour asc.

## S8N09: Are shoppers switching from 5 kg to 1 kg atta?

answered from the ontology layer. (Plan covers: Daily units sold of 5 kg and 1 kg atta in June; no table identifies shoppers, so switching itself cannot be seen, only the two sales series.)
56 rows (columns: date, sku, units_sold):
  2026-06-01 | ATTA-WW-5KG | 30.0
  2026-06-01 | ATTA-WW-1KG | 22.0
  2026-06-02 | ATTA-WW-5KG | 36.0
  2026-06-02 | ATTA-WW-1KG | 35.0
  2026-06-03 | ATTA-WW-5KG | 22.0
  2026-06-03 | ATTA-WW-1KG | 41.0
  2026-06-04 | ATTA-WW-5KG | 28.0
  2026-06-04 | ATTA-WW-1KG | 24.0
  2026-06-05 | ATTA-WW-5KG | 32.0
  2026-06-05 | ATTA-WW-1KG | 24.0
  ... and 46 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-5KG', 'ATTA-WW-1KG']; report date = day(daily sales.date), sku = daily sales.sku, units_sold = daily sales.units_sold; sorted by date asc.

## S8N10: What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?

Part 1: answered from the schema layer. (Plan covers: On-shelf availability of 5 kg atta in June = share of 11:00 shelf audits with status on shelf.)
2 rows (columns: status, audits):
  empty | 2
  on shelf | 6
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG'; group by shelf audits.status; report status = shelf audits.status, audits = count of *.
Part 2: answered from the schema layer. (Plan covers: Book-stock view: days in June with closing book stock above zero vs all days (a belief, not the shelf).)
days_book_above_zero = 27
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.book_on_hand_close > 0; report days_book_above_zero = count of *.
Part 3: answered from the ontology layer. (Plan covers: Books-and-tills view: June days where the book showed stock but the tills sold no 5 kg atta (silence is a question).)
3 rows (columns: date, book_on_hand_close):
  2026-06-12 | 55.0
  2026-06-24 | 63.0
  2026-06-25 | 63.0
  How it was found: From daily sales row records; inner-join book-stock row records on daily sales.sku = inventory book.sku; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) = day(inventory book.date) and inventory book.book_on_hand_close > 0 and daily sales.units_sold = 0; report date = day(daily sales.date), book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.

## S8N11: What has daily demand for 5 kg atta been in June so far?

Part 1: answered from the ontology layer. (Plan covers: Demand is not recorded; this gives recorded daily sales of 5 kg atta in June, which understate demand on days the shelf was empty.)
28 rows (columns: date, units_sold):
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
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG'; report date = day(daily sales.date), units_sold = daily sales.units_sold; sorted by date asc.
Part 2: answered from the schema layer. (Plan covers: Shelf audits of 5 kg atta in June, to mark days where sales were capped by an empty shelf.)
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
Not recorded, so not answered: needs a longer period than the records cover

## S8N12: How many shoppers left without 5 kg atta, and what were the lost sales in June?

Part 1: answered from the schema layer. (Plan covers: Shoppers who left and lost sales are not recorded; evidence: June shelf audits that found 5 kg atta empty.)
2 rows (columns: audit_ts):
  2026-06-12T11:00
  2026-06-26T11:00
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.status = 'empty'; report audit_ts = shelf audits.audit_ts; sorted by audit_ts asc.
Part 2: answered from the ontology layer. (Plan covers: Daily recorded sales of 5 kg atta in June, the basis for any stated estimate of lost sales on empty-shelf days.)
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
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG'; report date = day(daily sales.date), units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]
Stand-ins used (not the real thing): shopper_count (who): a bill is not a shopper: bills are the nearest stand-in

## S8E13: How many of June's deliveries arrived inside their 06:00–06:30 slot?

Part 1: answered from the schema layer. (Plan covers: June deliveries on time = arrived_ts between slot_start and slot_end (checks the 06:00-06:30 slot from the data).)
on_time_deliveries = 23
  How it was found: From shipment records; keep rows where shipments.arrived_ts >= shipments.slot_start and shipments.arrived_ts <= shipments.slot_end; report on_time_deliveries = count of *.
Part 2: answered from the ontology layer. (Plan covers: All June deliveries with their slots, to check the 06:00-06:30 slot and the total.)
slot_start_hour = 6; deliveries = 25; earliest_slot_start = 2026-06-01T06:00; latest_slot_end = 2026-06-28T06:30
  How it was found: From shipment records; group by hour(shipments.slot_start); report slot_start_hour = hour(shipments.slot_start), deliveries = count of *, earliest_slot_start = min of shipments.slot_start, latest_slot_end = max of shipments.slot_end.

## S8N14: How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?

Part 1: answered from the schema layer. (Plan covers: June pallets by dispatch weight-check status.)
weight_check = not weighed; pallets = 30
  How it was found: From pallet records; group by pallets.weight_check; report weight_check = pallets.weight_check, pallets = count of *.
Part 2: answered from the ontology layer. (Plan covers: How pallets were received at the store: receipt method by distinct pallet label (SSCC).)
receipt_method = pallet label (SSCC) scan against the shipping notice; pallets = 30
  How it was found: From goods-receipt line records; group by goods receipts.receipt_method; report receipt_method = goods receipts.receipt_method, pallets = count distinct of goods receipts.sscc.

## S8N15: What was the case fill rate across June's store orders according to the shipping notices?

Part 1: answered from the schema layer. (Plan covers: Fill rate numerator: cases on June shipping notices.)
notice_cases = 704.0
  How it was found: From shipping-notice line records; report notice_cases = sum of shipping notice lines.cases.
Part 2: answered from the schema layer. (Plan covers: Fill rate denominator: cases on June store orders (fill rate = notice cases / ordered cases).)
ordered_cases = 689.0
  How it was found: From store order line records; report ordered_cases = sum of store orders.cases.

## S8N16: What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?

Part 1: answered from the ontology layer. (Plan covers: Warehouse atta corrections: net = signed sum of value at cost, gross = sum of absolute values.)
net_value_inr = 6672.0; gross_value_inr = 22512.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report net_value_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_inr = sum of abs(dc stock adjustments.value_at_cost_inr).
Part 2: answered from the ontology layer. (Plan covers: Store atta count adjustments valued at product cost: net (signed) and gross (absolute).)
net_value_inr = -7018.5; gross_value_inr = 23522.5
  How it was found: From stock count records; inner-join product records on stock counts.sku = products.sku; keep rows where stock counts.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report net_value_inr = sum of stock counts.adjustment * products.cost_inr, gross_value_inr = sum of abs(stock counts.adjustment * products.cost_inr).

## S8N17: Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?

Part 1: answered from the schema layer. (Plan covers: All warehouse corrections with product, slot, cases and time, to pair against store corrections (mirror image = same family, opposite signs, within 15% in cases, within 7 days).)
2 rows (columns: adjusted_ts, sku, slot, cases, units, value_at_cost_inr, reason):
  2026-06-23T14:20 | ATTA-WW-1KG | A-07-04 | -16.0 | -160.0 | -7920.0 | short pick: slot count variance
  2026-06-25T10:00 | ATTA-WW-5KG | A-07-03 | 16.0 | 64.0 | 14592.0 | cycle count variance
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, cases = dc stock adjustments.cases, units = dc stock adjustments.units, value_at_cost_inr = dc stock adjustments.value_at_cost_inr, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.
Part 2: answered from the ontology layer. (Plan covers: All non-zero store count corrections converted to cases (adjustment / case units), for the same pairing.)
21 rows (columns: count_ts, sku, adjustment_packs, adjustment_cases, trigger):
  2026-06-01T05:45 | ATTA-WW-1KG | -5.0 | -0.5 | scheduled full count
  2026-06-01T05:45 | ATTA-WW-10KG | 1.0 | 0.5 | scheduled full count
  2026-06-01T05:45 | RICE-SM-5KG | -2.0 | -0.5 | scheduled full count
  2026-06-01T05:45 | DAL-TOOR-1KG | -2.0 | -0.2 | scheduled full count
  2026-06-01T05:45 | OIL-SUN-1L | -5.0 | -0.5 | scheduled full count
  2026-06-01T05:45 | SUGAR-1KG | -2.0 | -0.2 | scheduled full count
  2026-06-01T05:45 | MILK-TONED-500ML | -26.0 | -1.0833333333333333 | scheduled full count
  2026-06-01T05:45 | MILK-FC-500ML | 15.0 | 0.625 | scheduled full count
  2026-06-01T05:45 | CURD-500G | -3.0 | -0.125 | scheduled full count
  2026-06-01T05:45 | BREAD-WHITE-400G | -5.0 | -0.4166666666666667 | scheduled full count
  ... and 11 more
  How it was found: From stock count records; inner-join product records on stock counts.sku = products.sku; keep rows where stock counts.adjustment != 0; report count_ts = stock counts.count_ts, sku = stock counts.sku, adjustment_packs = stock counts.adjustment, adjustment_cases = stock counts.adjustment / products.case_units, trigger = stock counts.trigger; sorted by count_ts asc.

## S8N18: Which goods receipts did not survive the next stock count within a week?

answered from the ontology layer. (Plan covers: Goods receipts followed within 7 days by a store count of the same product that cut the book (negative adjustment).)
58 rows (columns: grn_id, line, shipment_id, sku_booked, received_ts, units_booked, count_ts, adjustment):
  GRN-260601 | 1 | SHP-260601 | ATTA-WW-5KG | 2026-06-01T06:20 | 52.0 | 2026-06-26T09:00 | -63.0
  GRN-260601 | 1 | SHP-260601 | ATTA-WW-5KG | 2026-06-01T06:20 | 52.0 | 2026-06-28T22:30 | -1.0
  GRN-260602 | 1 | SHP-260602 | SUGAR-1KG | 2026-06-02T06:00 | 50.0 | 2026-06-28T22:30 | -1.0
  GRN-260603 | 1 | SHP-260603 | ATTA-WW-5KG | 2026-06-03T06:16 | 64.0 | 2026-06-26T09:00 | -63.0
  GRN-260603 | 3 | SHP-260603 | ATTA-WW-10KG | 2026-06-03T06:16 | 34.0 | 2026-06-26T09:00 | -1.0
  GRN-260603 | 1 | SHP-260603 | ATTA-WW-5KG | 2026-06-03T06:16 | 64.0 | 2026-06-28T22:30 | -1.0
  GRN-260603 | 4 | SHP-260603 | RICE-SM-5KG | 2026-06-03T06:16 | 60.0 | 2026-06-28T22:30 | -2.0
  GRN-260603 | 5 | SHP-260603 | OIL-SUN-1L | 2026-06-03T06:16 | 70.0 | 2026-06-28T22:30 | -8.0
  GRN-260605 | 1 | SHP-260605 | ATTA-WW-5KG | 2026-06-05T06:21 | 48.0 | 2026-06-26T09:00 | -63.0
  GRN-260605 | 1 | SHP-260605 | ATTA-WW-5KG | 2026-06-05T06:21 | 48.0 | 2026-06-28T22:30 | -1.0
  ... and 48 more
  How it was found: From goods-receipt line records; inner-join stock count records on goods receipts.sku_booked = stock counts.sku; keep rows where stock counts.count_ts > goods receipts.received_ts and days_between(goods receipts.received_ts, stock counts.count_ts) <= 7 and stock counts.adjustment < 0; report grn_id = goods receipts.grn_id, line = goods receipts.line, shipment_id = goods receipts.shipment_id, sku_booked = goods receipts.sku_booked, received_ts = goods receipts.received_ts, units_booked = goods receipts.units_booked, count_ts = stock counts.count_ts, adjustment = stock counts.adjustment; sorted by received_ts asc.

## S8N19: Was the 22 June delivery on time and in full?

Part 1: answered from the ontology layer. (Plan covers: On time for the 22 June delivery: arrived_ts vs slot_start and slot_end.)
shipment_id = SHP-260622; arrived_ts = 2026-06-22T06:12; slot_start = 2026-06-22T06:00; slot_end = 2026-06-22T06:30; pallets = 2.0
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report shipment_id = shipments.shipment_id, arrived_ts = shipments.arrived_ts, slot_start = shipments.slot_start, slot_end = shipments.slot_end, pallets = shipments.pallets.
Part 2: answered from the ontology layer. (Plan covers: In full for the 22 June delivery: cases confirmed vs cases ordered per line, with pick slot vs the product's slot.)
4 rows (columns: line, sku, slot_picked, product_slot, cases_ordered, cases_confirmed):
  1 | ATTA-WW-5KG | A-07-03 | A-07-03 | 16.0 | 16.0
  2 | ATTA-WW-1KG | A-07-04 | A-07-04 | 9.0 | 9.0
  3 | RICE-SM-5KG | A-09-01 | A-09-01 | 14.0 | 14.0
  4 | SUGAR-1KG | B-03-04 | B-03-04 | 5.0 | 5.0
  How it was found: From pick confirmation records; inner-join shipment records on dc pick confirmations.shipment_id = shipments.shipment_id; inner-join product records on dc pick confirmations.sku = products.sku; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report line = dc pick confirmations.line, sku = dc pick confirmations.sku, slot_picked = dc pick confirmations.slot, product_slot = products.dc_slot, cases_ordered = dc pick confirmations.cases_ordered, cases_confirmed = dc pick confirmations.cases_confirmed.
Part 3: answered from the ontology layer. (Plan covers: What the store booked from the 22 June delivery: notice SKU/units vs booked SKU/units per pallet line (received by pallet-label scan, not case by case).)
4 rows (columns: sscc, line, asn_sku, sku_booked, asn_units, units_booked, receipt_method):
  029000010000010542 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0 | 64.0 | pallet label (SSCC) scan against the shipping notice
  029000010000010542 | 2 | ATTA-WW-1KG | ATTA-WW-1KG | 90.0 | 90.0 | pallet label (SSCC) scan against the shipping notice
  029000010000010542 | 3 | RICE-SM-5KG | RICE-SM-5KG | 56.0 | 56.0 | pallet label (SSCC) scan against the shipping notice
  029000010000010559 | 4 | SUGAR-1KG | SUGAR-1KG | 50.0 | 50.0 | pallet label (SSCC) scan against the shipping notice
  How it was found: From goods-receipt line records; inner-join shipment records on goods receipts.shipment_id = shipments.shipment_id; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report sscc = goods receipts.sscc, line = goods receipts.line, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked, receipt_method = goods receipts.receipt_method.

## S8N20: What was Store 014's OTIF from the warehouse in June?

Part 1: answered from the ontology layer. (Plan covers: OTIF per delivery: each June shipment's arrival vs slot and its cases confirmed vs ordered (on time = arrived within slot; in full = confirmed >= ordered).)
25 rows (columns: shipment_id, arrived_ts, slot_start, slot_end, cases_ordered, cases_confirmed):
  SHP-260601 | 2026-06-01T06:20 | 2026-06-01T06:00 | 2026-06-01T06:30 | 18.0 | 18.0
  SHP-260602 | 2026-06-02T06:00 | 2026-06-02T06:00 | 2026-06-02T06:30 | 5.0 | 5.0
  SHP-260603 | 2026-06-03T06:16 | 2026-06-03T06:00 | 2026-06-03T06:30 | 63.0 | 63.0
  SHP-260604 | 2026-06-04T06:00 | 2026-06-04T06:00 | 2026-06-04T06:30 | 7.0 | 7.0
  SHP-260605 | 2026-06-05T06:21 | 2026-06-05T06:00 | 2026-06-05T06:30 | 25.0 | 25.0
  SHP-260606 | 2026-06-06T06:12 | 2026-06-06T06:00 | 2026-06-06T06:30 | 50.0 | 50.0
  SHP-260607 | 2026-06-07T06:10 | 2026-06-07T06:00 | 2026-06-07T06:30 | 23.0 | 23.0
  SHP-260608 | 2026-06-08T06:06 | 2026-06-08T06:00 | 2026-06-08T06:30 | 45.0 | 45.0
  SHP-260609 | 2026-06-09T06:17 | 2026-06-09T06:00 | 2026-06-09T06:30 | 26.0 | 26.0
  SHP-260611 | 2026-06-11T08:21 | 2026-06-11T06:00 | 2026-06-11T06:30 | 39.0 | 38.0
  ... and 15 more
  How it was found: From shipment records; inner-join pick confirmation records on shipments.shipment_id = dc pick confirmations.shipment_id; group by shipments.shipment_id; report shipment_id = shipments.shipment_id, arrived_ts = min of shipments.arrived_ts, slot_start = min of shipments.slot_start, slot_end = max of shipments.slot_end, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed; sorted by arrived_ts asc.
Part 2: answered from the schema layer. (Plan covers: Per order line in full: pick lines whose confirmed cases met ordered cases.)
lines_in_full = 68
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed >= dc pick confirmations.cases_ordered; report lines_in_full = count of *.
Part 3: answered from the schema layer. (Plan covers: Per line and per case totals: all pick lines, cases ordered and cases confirmed (note: picks are confirmed by slot label scan, a copy, not a check at the door).)
lines = 70; cases_ordered = 707.0; cases_confirmed = 704.0
  How it was found: From pick confirmation records; report lines = count of *, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed.

## S8N21: Why was 5 kg atta off the shelf from 23 to 26 June?

Part 1: answered from the ontology layer. (Plan covers: The cause is not recorded; evidence: shelf audits of 5 kg atta 20-26 June.)
2 rows (columns: audit_ts, status):
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-20 and 2026-06-26; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 2: not answered: ecords: the ontology layer refused the plan (the question names day 26 of month 6 but the plan has no such date).
Part 3: not answered: ecords: the ontology layer refused the plan (the question names day 26 of month 6 but the plan has no such date).
Part 4: not answered: ecords: the ontology layer refused the plan (the question names day 26 of month 6 but the plan has no such date).
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S8N22: Is the 5 kg atta missing at the store theft?

Part 1: answered from the schema layer. (Plan covers: Whether it is theft is a cause and is not recorded; evidence: store counts of 5 kg atta (book vs counted).)
3 rows (columns: count_ts, book_before, counted, adjustment, trigger):
  2026-06-01T05:45 | 36.0 | 36.0 | 0.0 | scheduled full count
  2026-06-26T09:00 | 63.0 | 0.0 | -63.0 | manager request after complaints
  2026-06-28T22:30 | 63.0 | 62.0 | -1.0 | scheduled full count
  How it was found: From stock count records; keep rows where stock counts.sku = 'ATTA-WW-5KG'; report count_ts = stock counts.count_ts, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment, trigger = stock counts.trigger; sorted by count_ts asc.
Part 2: answered from the schema layer. (Plan covers: Warehouse corrections on atta items (a mirror-image correction would point upstream rather than at the store).)
2 rows (columns: adjusted_ts, sku, slot, cases, units, reason):
  2026-06-23T14:20 | ATTA-WW-1KG | A-07-04 | -16.0 | -160.0 | short pick: slot count variance
  2026-06-25T10:00 | ATTA-WW-5KG | A-07-03 | 16.0 | 64.0 | cycle count variance
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, cases = dc stock adjustments.cases, units = dc stock adjustments.units, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.
Part 3: answered from the ontology layer. (Plan covers: Atta pick lines where the slot picked differs from the product's own slot (item matched on slot, not pack code).)
No rows matched.
  How it was found: From pick confirmation records; inner-join product records on dc pick confirmations.sku = products.sku; keep rows where dc pick confirmations.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] and dc pick confirmations.slot != products.dc_slot; report pick_ts = dc pick confirmations.pick_ts, shipment_id = dc pick confirmations.shipment_id, line = dc pick confirmations.line, sku = dc pick confirmations.sku, slot_picked = dc pick confirmations.slot, product_slot = products.dc_slot, cases_confirmed = dc pick confirmations.cases_confirmed; sorted by pick_ts asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S8N23: Which delivery, pallet (SSCC), and line should the store raise a claim against?

Part 1: answered from the ontology layer. (Plan covers: Shipping-notice lines whose pack code (GTIN) is not the GTIN of the product they name: delivery, SSCC and line (match on pack code).)
No rows matched.
  How it was found: From shipping-notice line records; inner-join product records on shipping notice lines.sku = products.sku; keep rows where shipping notice lines.gtin != products.gtin; report shipment_id = shipping notice lines.shipment_id, sscc = shipping notice lines.sscc, line = shipping notice lines.line, sku = shipping notice lines.sku, notice_gtin = shipping notice lines.gtin, product_gtin = products.gtin, cases = shipping notice lines.cases.
Part 2: answered from the ontology layer. (Plan covers: Pick lines confirmed from a slot other than the product's own slot (confirmed by slot label scan), with their shipment and line.)
No rows matched.
  How it was found: From pick confirmation records; inner-join product records on dc pick confirmations.sku = products.sku; keep rows where dc pick confirmations.slot != products.dc_slot; report shipment_id = dc pick confirmations.shipment_id, line = dc pick confirmations.line, sku = dc pick confirmations.sku, slot_picked = dc pick confirmations.slot, product_slot = products.dc_slot, cases_confirmed = dc pick confirmations.cases_confirmed.
Part 3: answered from the schema layer. (Plan covers: Goods-receipt lines where the booked SKU or units differ from the shipping notice, by delivery, SSCC and line.)
No rows matched.
  How it was found: From goods-receipt line records; keep rows where (goods receipts.asn_sku != goods receipts.sku_booked or goods receipts.asn_units != goods receipts.units_booked); report shipment_id = goods receipts.shipment_id, sscc = goods receipts.sscc, line = goods receipts.line, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked.
Part 4: answered from the schema layer. (Plan covers: Warehouse corrections with reason short pick: slot count variance, which point at a mispicked line.)
adjusted_ts = 2026-06-23T14:20; sku = ATTA-WW-1KG; slot = A-07-04; cases = -16.0; value_at_cost_inr = -7920.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.reason = 'short pick: slot count variance'; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, cases = dc stock adjustments.cases, value_at_cost_inr = dc stock adjustments.value_at_cost_inr.

## S8N24: How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?

Part 1: answered from the ontology layer. (Plan covers: Demand and shoppers who did not find the item are not recorded; evidence: shelf audits of 5 kg atta 23-26 June.)
2 rows (columns: audit_ts, status):
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-23 and 2026-06-26; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 2: answered from the ontology layer. (Plan covers: Recorded sales of 5 kg atta 23-26 June.)
4 rows (columns: date, units_sold):
  2026-06-23 | 5.0
  2026-06-24 | 0.0
  2026-06-25 | 0.0
  2026-06-26 | 0.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) between 2026-06-23 and 2026-06-26; report date = day(daily sales.date), units_sold = daily sales.units_sold; sorted by date asc.
Part 3: not answered: ecords: the ontology layer refused the plan (the question names day 26 of month 6 but the plan has no such date).

## S8A25: How many UPI payments did the tills attempt in June?

answered from the ontology layer. (Plan covers: UPI payment attempts at the tills in June (one attempt = one try), and the bills they were for.)
upi_attempts = 19166; upi_bills = 18770
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report upi_attempts = count of *, upi_bills = count distinct of pos payments.bill_id.

## S8E26: How many UPI attempts timed out (failed: no response) without receiving an RRN?

answered from the schema layer. (Plan covers: UPI attempts with till status 'failed: no response' (timeouts), and how many of them carry an RRN.)
timeouts = 48; timeouts_with_rrn = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; report timeouts = count of *, timeouts_with_rrn = count of pos payments.rrn.

## S8N27: Which successes in the provider's UPI report have no matching approved payment at the till?

answered from the ontology layer. (Plan covers: Provider successes whose RRN has no approved till payment (an extra debit by definition).)
26 rows (columns: rrn, bill_ref, amount_inr, initiated_ts, status_ts, till_status):
  615521002766 |  | 143.11 | 2026-06-04T21:32:26 | 2026-06-04T21:33:20 | 
  615619003319 |  | 224.51 | 2026-06-05T19:58:33 | 2026-06-05T19:59:20 | 
  615908004963 |  | 1325.54 | 2026-06-08T08:39:27 | 2026-06-08T08:40:21 | 
  615909004985 |  | 564.24 | 2026-06-08T09:08:34 | 2026-06-08T09:09:15 | 
  616011005544 |  | 532.71 | 2026-06-09T11:22:07 | 2026-06-09T13:52:31 | 
  616517008996 |  | 362.94 | 2026-06-14T17:00:31 | 2026-06-14T17:01:54 | 
  616918011772 |  | 963.27 | 2026-06-18T18:43:56 | 2026-06-18T18:45:00 | 
  617118013318 |  | 438.73 | 2026-06-20T18:22:03 | 2026-06-20T18:22:57 | 
  617118013325 |  | 342.13 | 2026-06-20T18:32:55 | 2026-06-21T11:10:52 | 
  617118013326 |  | 342.13 | 2026-06-20T18:33:25 | 2026-06-20T21:28:32 | 
  ... and 16 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, initiated_ts = psp upi report.initiated_ts, status_ts = psp upi report.status_ts, till_status = pos payments.till_status; sorted by initiated_ts asc.

## S8N28: Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?

Part 1: answered from the ontology layer. (Plan covers: Hours (date and hour) in June with 3 or more UPI timeouts ('failed: no response').)
2 rows (columns: date, hour, timeouts):
  2026-06-20 | 18 | 12
  2026-06-20 | 19 | 16
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by day(pos payments.ts), hour(pos payments.ts); keep groups where timeouts >= 3; report date = day(pos payments.ts), hour = hour(pos payments.ts), timeouts = count of *; sorted by date asc.
Part 2: answered from the ontology layer. (Plan covers: Monthly baseline: all June UPI timeouts and the trading hours they fall across, to compare each burst hour against more than 10 times the monthly hourly rate.)
june_timeouts = 48; days_with_timeouts = 17
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; report june_timeouts = count of *, days_with_timeouts = count distinct of day(pos payments.ts).
Part 3: answered from the ontology layer. (Plan covers: Monthly baseline denominator: all June UPI attempts and the days they span.)
june_upi_attempts = 19166; trading_days = 28
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report june_upi_attempts = count of *, trading_days = count distinct of day(pos payments.ts).

## S8N29: How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?

Part 1: answered from the ontology layer. (Plan covers: Approved UPI bills above Rs 2,000 and up to Rs 75,000, where 0.4% stays under the Rs 300 cap: count and fee at 0.4%.)
bills = 653; amount_inr = 1976389.91; mdr_fee_inr = 7905.55964
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 2000 and pos payments.amount_inr <= 75000; report bills = count distinct of pos payments.bill_id, amount_inr = sum of pos payments.amount_inr, mdr_fee_inr = sum of pos payments.amount_inr * 0.004.
Part 2: answered from the ontology layer. (Plan covers: Approved UPI bills above Rs 75,000, where the fee is capped at Rs 300 each.)
bills_capped = 0; capped_fee_inr = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 75000; report bills_capped = count distinct of pos payments.bill_id, capped_fee_inr = count of * * 300.

## S8N30: Which customers were charged three times for a single bill?

answered from the schema layer. (Plan covers: No customer identity is recorded; a bill is the stand-in: bills with three or more provider UPI successes.)
bill_ref = None; successes = 18410; amount_inr = 10798593.78
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'success'; group by psp upi report.bill_ref; keep groups where successes >= 3; report bill_ref = psp upi report.bill_ref, successes = count of *, amount_inr = sum of psp upi report.amount_inr; sorted by successes desc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N31: Did any customer pay twice in June, and how many?

Part 1: answered from the schema layer. (Plan covers: Bills (the stand-in for customers) with two or more provider UPI successes in June.)
bill_ref = None; successes = 18410; amount_inr = 10798593.78
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'success'; group by psp upi report.bill_ref; keep groups where successes >= 2; report bill_ref = psp upi report.bill_ref, successes = count of *, amount_inr = sum of psp upi report.amount_inr; sorted by successes desc.
Part 2: answered from the ontology layer. (Plan covers: Count of extra debits: provider successes with no approved till payment on their RRN, and the bills they hit.)
extra_debits = 26; bills = 0; amount_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report extra_debits = count of *, bills = count distinct of psp upi report.bill_ref, amount_inr = sum of psp upi report.amount_inr.

## S8N32: What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?

Part 1: answered from the ontology layer. (Plan covers: UPI attempts the tills gave up on (failed or 'failed: no response') between 18:20 and 19:50 on 20 June, with the provider's final status for the same bill.)
31 rows (columns: bill_id, attempt, till_ts, till_status, psp_rrn, psp_status, psp_status_ts):
  B260620-110022 | 1 | 2026-06-20T18:22:03 | failed: no response |  |  | 
  B260620-110024 | 1 | 2026-06-20T18:25:41 | failed: no response |  |  | 
  B260620-110027 | 1 | 2026-06-20T18:27:56 | failed: no response |  |  | 
  B260620-110029 | 1 | 2026-06-20T18:28:25 | failed: no response |  |  | 
  B260620-110032 | 1 | 2026-06-20T18:32:55 | failed: no response |  |  | 
  B260620-110032 | 2 | 2026-06-20T18:33:25 | failed: no response |  |  | 
  B260620-110032 | 3 | 2026-06-20T18:33:55 | failed: no response |  |  | 
  B260620-110035 | 1 | 2026-06-20T18:34:10 | failed: no response |  |  | 
  B260620-110048 | 1 | 2026-06-20T18:45:34 | failed: no response |  |  | 
  B260620-110056 | 1 | 2026-06-20T18:48:25 | failed: no response |  |  | 
  ... and 21 more
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.bill_id = psp upi report.bill_ref; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and pos payments.ts between 2026-06-20T18:20 and 2026-06-20T19:50; report bill_id = pos payments.bill_id, attempt = pos payments.attempt, till_ts = pos payments.ts, till_status = pos payments.till_status, psp_rrn = psp upi report.rrn, psp_status = psp upi report.status, psp_status_ts = psp upi report.status_ts; sorted by till_ts asc.
Part 2: answered from the ontology layer. (Plan covers: Summary for the same window: given-up attempts by provider final status (success = late credit, returned = debited and returned, failed or none = never debited).)
psp_status = None; attempts = 31; amount_inr = None
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.bill_id = psp upi report.bill_ref; keep rows where pos payments.tender = 'UPI' and pos payments.till_status in ['failed', 'failed: no response'] and pos payments.ts between 2026-06-20T18:20 and 2026-06-20T19:50; group by psp upi report.status; report psp_status = psp upi report.status, attempts = count of *, amount_inr = sum of psp upi report.amount_inr.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8N33: Why are 17 UPI credits from 20 and 21 June sitting in suspense?

Part 1: answered from the ontology layer. (Plan covers: Why is not recorded; checks the 17: provider UPI successes initiated on 20-21 June with no approved till payment on their RRN (credits with no bill to match).)
17 rows (columns: rrn, bill_ref, amount_inr, initiated_ts, till_status, till_note):
  617118013318 |  | 438.73 | 2026-06-20T18:22:03 |  | 
  617118013325 |  | 342.13 | 2026-06-20T18:32:55 |  | 
  617118013326 |  | 342.13 | 2026-06-20T18:33:25 |  | 
  617118013344 |  | 1064.47 | 2026-06-20T18:48:25 |  | 
  617118013342 |  | 168.21 | 2026-06-20T18:48:34 |  | 
  617118013343 |  | 168.21 | 2026-06-20T18:49:04 |  | 
  617119013351 |  | 372.15 | 2026-06-20T19:01:34 |  | 
  617119013361 |  | 171.7 | 2026-06-20T19:09:24 |  | 
  617119013363 |  | 592.94 | 2026-06-20T19:11:36 |  | 
  617119013372 |  | 398.2 | 2026-06-20T19:21:36 |  | 
  ... and 7 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and day(psp upi report.initiated_ts) between 2026-06-20 and 2026-06-21 and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, initiated_ts = psp upi report.initiated_ts, till_status = pos payments.till_status, till_note = pos payments.note; sorted by initiated_ts asc.
Part 2: not answered: ecords: the ontology layer refused the plan (the question names day 21 of month 6 but the plan has no such date).
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S8N34: How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?

Part 1: answered from the ontology layer. (Plan covers: Refund wait measured from the extra debit (provider success time) and from the complaint, to refund completion.)
refunds = 23; avg_days_from_debit = -5.161767814004713; max_days_from_debit = -2.7087962962687016; avg_days_from_complaint = -3.217391304347826; max_days_from_complaint = -2.0
  How it was found: From UPI refund records; inner-join UPI service provider's transaction records on upi refunds.rrn = psp upi report.rrn; left-join complaint records on upi refunds.rrn = customer complaints.rrn; keep rows where psp upi report.status = 'success'; report refunds = count of *, avg_days_from_debit = avg of days_between(psp upi report.status_ts, upi refunds.completed_ts), max_days_from_debit = max of days_between(psp upi report.status_ts, upi refunds.completed_ts), avg_days_from_complaint = avg of days_between(customer complaints.complaint_ts, upi refunds.completed_ts), max_days_from_complaint = max of days_between(customer complaints.complaint_ts, upi refunds.completed_ts).
Part 2: answered from the ontology layer. (Plan covers: Extra debits (provider success with no approved till payment) with no refund on record by month end.)
unrefunded = 3; amount_inr = 2064.2
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join UPI refund records on psp upi report.rrn = upi refunds.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved') and upi refunds.refund_id is empty; report unrefunded = count of *, amount_inr = sum of psp upi report.amount_inr.
Part 3: answered from the ontology layer. (Plan covers: Complaints by kind and resolution, including those settled by the customer's bank returning the money rather than a store refund.)
2 rows (columns: kind, resolution, complaints, avg_days_complaint_to_resolved):
  charged twice | refunded after the store matched the credit by hand | 23 | -3.217391304347826
  debited but the till said failed | customer's bank returned the money | 3 | -1.0416666669771075
  How it was found: From complaint records; group by customer complaints.kind, customer complaints.resolution; report kind = customer complaints.kind, resolution = customer complaints.resolution, complaints = count of *, avg_days_complaint_to_resolved = avg of days_between(customer complaints.complaint_ts, customer complaints.resolved_ts).
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N35: Was the store's UPI technical decline rate acceptable in June?

Part 1: answered from the schema layer. (Plan covers: June UPI till attempts by till status; no acceptable threshold is recorded, so this gives the rates to judge.)
4 rows (columns: till_status, attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *.
Part 2: answered from the ontology layer. (Plan covers: Hours with 3 or more UPI timeouts, showing whether failures were spread or clustered.)
2 rows (columns: date, hour, timeouts):
  2026-06-20 | 18 | 12
  2026-06-20 | 19 | 16
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by day(pos payments.ts), hour(pos payments.ts); keep groups where timeouts >= 3; report date = day(pos payments.ts), hour = hour(pos payments.ts), timeouts = count of *; sorted by date asc.
Part 3: answered from the schema layer. (Plan covers: Provider-side final statuses of June UPI transactions.)
3 rows (columns: status, transactions):
  failed | 750
  returned | 6
  success | 18410
  How it was found: From UPI service provider's transaction records; group by psp upi report.status; report status = psp upi report.status, transactions = count of *.

## S8N36: Which customers (by RRN) should the store refund now, without waiting for a complaint?

answered from the ontology layer. (Plan covers: Extra debits (provider success with no approved till payment) that have no refund on record, by RRN, with any complaint and its resolution; bills stand in for customers.)
3 rows (columns: rrn, bill_ref, amount_inr, debit_ts, complaint_ts, complaint_resolution):
  615908004963 |  | 1325.54 | 2026-06-08T08:40:21 |  | 
  615909004985 |  | 564.24 | 2026-06-08T09:09:15 |  | 
  617119013392 |  | 174.42 | 2026-06-20T19:44:43 |  | 
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join UPI refund records on psp upi report.rrn = upi refunds.rrn; left-join complaint records on psp upi report.rrn = customer complaints.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved') and upi refunds.refund_id is empty; report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, debit_ts = psp upi report.status_ts, complaint_ts = customer complaints.complaint_ts, complaint_resolution = customer complaints.resolution; sorted by debit_ts asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N37: At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?

Part 1: answered from the ontology layer. (Plan covers: Till sales of 5 kg atta on Tuesday 23 June by hour up to 20:00, to show when selling stopped; the cause itself is not recorded.)
5 rows (columns: hour, units, last_sale_ts):
  7 | 1.0 | 2026-06-23T07:35
  9 | 1.0 | 2026-06-23T09:51
  11 | 1.0 | 2026-06-23T11:41
  14 | 1.0 | 2026-06-23T14:46
  15 | 1.0 | 2026-06-23T15:10
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and pos lines may.bill_ts between 2026-06-23T00:00 and 2026-06-23T20:00; group by hour(pos lines may.bill_ts); report hour = hour(pos lines may.bill_ts), units = sum of pos lines may.qty, last_sale_ts = max of pos lines may.bill_ts; sorted by hour asc.
Part 2: answered from the ontology layer. (Plan covers: Goods-receipt lines naming atta on the notice or as booked, 20-23 June: shipment, SSCC, line, notice vs booked SKU and units.)
5 rows (columns: received_ts, shipment_id, sscc, line, asn_sku, sku_booked, asn_units, units_booked):
  2026-06-20T06:22 | SHP-260620 | 029000010000010528 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 72.0 | 72.0
  2026-06-20T06:22 | SHP-260620 | 029000010000010528 | 2 | ATTA-WW-10KG | ATTA-WW-10KG | 24.0 | 24.0
  2026-06-22T06:12 | SHP-260622 | 029000010000010542 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0 | 64.0
  2026-06-22T06:12 | SHP-260622 | 029000010000010542 | 2 | ATTA-WW-1KG | ATTA-WW-1KG | 90.0 | 90.0
  2026-06-23T06:18 | SHP-260623 | 029000010000010566 | 1 | ATTA-WW-10KG | ATTA-WW-10KG | 26.0 | 26.0
  How it was found: From goods-receipt line records; keep rows where (goods receipts.asn_sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] or goods receipts.sku_booked in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']) and day(goods receipts.received_ts) between 2026-06-20 and 2026-06-23; report received_ts = goods receipts.received_ts, shipment_id = goods receipts.shipment_id, sscc = goods receipts.sscc, line = goods receipts.line, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked; sorted by received_ts asc.
Part 3: answered from the ontology layer. (Plan covers: What was really picked: atta pick lines 20-23 June with slot picked vs the product's own slot (pack code vs slot label).)
5 rows (columns: pick_ts, shipment_id, line, sku, slot_picked, product_slot, cases_confirmed):
  2026-06-20T03:00 | SHP-260620 | 1 | ATTA-WW-5KG | A-07-03 | A-07-03 | 18.0
  2026-06-20T03:08 | SHP-260620 | 2 | ATTA-WW-10KG | A-07-05 | A-07-05 | 12.0
  2026-06-22T03:00 | SHP-260622 | 1 | ATTA-WW-5KG | A-07-03 | A-07-03 | 16.0
  2026-06-22T03:08 | SHP-260622 | 2 | ATTA-WW-1KG | A-07-04 | A-07-04 | 9.0
  2026-06-23T03:00 | SHP-260623 | 1 | ATTA-WW-10KG | A-07-05 | A-07-05 | 13.0
  How it was found: From pick confirmation records; inner-join product records on dc pick confirmations.sku = products.sku; keep rows where dc pick confirmations.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] and day(dc pick confirmations.pick_ts) between 2026-06-20 and 2026-06-23; report pick_ts = dc pick confirmations.pick_ts, shipment_id = dc pick confirmations.shipment_id, line = dc pick confirmations.line, sku = dc pick confirmations.sku, slot_picked = dc pick confirmations.slot, product_slot = products.dc_slot, cases_confirmed = dc pick confirmations.cases_confirmed; sorted by pick_ts asc.
Part 4: answered from the ontology layer. (Plan covers: Warehouse corrections on atta items from 23 June (mirror-image slot corrections show what left on the truck).)
2 rows (columns: adjusted_ts, sku, slot, cases, reason):
  2026-06-23T14:20 | ATTA-WW-1KG | A-07-04 | -16.0 | short pick: slot count variance
  2026-06-25T10:00 | ATTA-WW-5KG | A-07-03 | 16.0 | cycle count variance
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG'] and day(dc stock adjustments.adjusted_ts) >= '2026-06-23'; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, cases = dc stock adjustments.cases, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.

## S8N38: Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?

Part 1: answered from the schema layer. (Plan covers: One of the joins only (the full set of 12 is not listed): shipping notice vs goods receipt - lines where booked SKU or units disagree with the notice copy, against all lines.)
disagreeing_lines = 0
  How it was found: From goods-receipt line records; keep rows where (goods receipts.asn_sku != goods receipts.sku_booked or goods receipts.asn_units != goods receipts.units_booked); report disagreeing_lines = count of *.
Part 2: answered from the ontology layer. (Plan covers: Pick confirmations vs shipping-notice lines joined on order and SKU: rows and total case difference (zero means a copy).)
joined_rows = 70; abs_case_difference = 0.0
  How it was found: From pick confirmation records; inner-join shipping-notice line records on dc pick confirmations.order_id = shipping notice lines.order_id and dc pick confirmations.sku = shipping notice lines.sku; report joined_rows = count of *, abs_case_difference = sum of abs(dc pick confirmations.cases_confirmed - shipping notice lines.cases).
Part 3: answered from the ontology layer. (Plan covers: Till payments vs the provider report joined on RRN: rows and total amount difference, plus rows where till and provider status disagree are visible by status.)
3 rows (columns: till_status, psp_status, joined_rows, abs_amount_difference):
  approved | success | 18384 | 0.0
  declined | failed | 589 | 0.0
  failed | failed | 145 | 0.0
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; group by pos payments.till_status, psp upi report.status; report till_status = pos payments.till_status, psp_status = psp upi report.status, joined_rows = count of *, abs_amount_difference = sum of abs(pos payments.amount_inr - psp upi report.amount_inr).
Part 4: answered from the ontology layer. (Plan covers: Pallets vs shipping-notice lines joined on SSCC: rows and total case difference between the pallet label and the notice lines.)
30 rows (columns: sscc, pallet_cases, notice_cases):
  029000010000010320 | 18.0 | 18.0
  029000010000010337 | 5.0 | 5.0
  029000010000010344 | 24.0 | 24.0
  029000010000010351 | 39.0 | 39.0
  029000010000010368 | 7.0 | 7.0
  029000010000010375 | 25.0 | 25.0
  029000010000010382 | 35.0 | 35.0
  029000010000010399 | 15.0 | 15.0
  029000010000010405 | 23.0 | 23.0
  029000010000010412 | 38.0 | 38.0
  ... and 20 more
  How it was found: From shipping-notice line records; inner-join pallet records on shipping notice lines.sscc = pallets.sscc; group by pallets.sscc; report sscc = pallets.sscc, pallet_cases = max of pallets.cases, notice_cases = sum of shipping notice lines.cases.

## S9N01: Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?

Part 1: not answered: ecords: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Part 2: answered from the ontology layer. (Plan covers: Checks the 59% premise: 5 kg atta units sold in the week of 8 June (8-14 June).)
units_week_of_8_june = 88.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) between 2026-06-08 and 2026-06-14; report units_week_of_8_june = sum of daily sales.units_sold.
Part 3: answered from the ontology layer. (Plan covers: Book stock of 5 kg atta in the week of 8 June (a belief, not the shelf).)
7 rows (columns: date, book_on_hand_close):
  2026-06-08 | 34.0
  2026-06-09 | 78.0
  2026-06-10 | 56.0
  2026-06-11 | 55.0
  2026-06-12 | 55.0
  2026-06-13 | 33.0
  2026-06-14 | 66.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) between 2026-06-08 and 2026-06-14; report date = day(inventory book.date), book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 4: answered from the ontology layer. (Plan covers: Shelf audits of 5 kg atta in the week of 8 June: whether it was on the shelf at all (shelf space itself is not recorded).)
2 rows (columns: audit_ts, status):
  2026-06-09T11:00 | on shelf
  2026-06-12T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-08 and 2026-06-14; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.

## S9N02: Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N03: How many bags of 5 kg atta were sold in June 2023?

I can't answer this from Store 014's records: the ontology layer refused the plan (2023-06-01, 2023-06-30 is outside the records of 'daily-sales-june' (2026-06-01 to 2026-06-28)).
Not recorded: year outside 2026

## S9N04: Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?

Part 1: answered from the schema layer. (Plan covers: Demand is not recorded, so the forecast can only be scored against sales: average daily forecast for 5 kg atta in June (28-day mean of recorded sales).)
method = 28-day mean of recorded sales; avg_forecast_units_per_day = 22.761428571428574; days = 28
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG'; group by forecasts.method; report method = forecasts.method, avg_forecast_units_per_day = avg of forecasts.forecast_units_per_day, days = count of *.
Part 2: answered from the schema layer. (Plan covers: Average recorded daily sales of 5 kg atta in June, to check the 13% claim against sales (not demand).)
avg_units_sold_per_day = 20.25; days = 28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG'; report avg_units_sold_per_day = avg of daily sales.units_sold, days = count of *.
Part 3: answered from the schema layer. (Plan covers: Shelf audits of 5 kg atta that found it empty: days where sales were capped, so sales understate demand.)
2 rows (columns: status, audits):
  empty | 2
  on shelf | 6
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG'; group by shelf audits.status; report status = shelf audits.status, audits = count of *.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S9N05: Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?

Part 1: answered from the ontology layer. (Plan covers: Checks the 2.3 days-of-supply premise: book on hand and forecast per day for 5 kg atta on 11 June.)
book_on_hand = 55.0; forecast_units_per_day = 23.82; days_of_supply = 2.3089840470193113
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and day(forecasts.date) = '2026-06-11'; report book_on_hand = forecasts.book_on_hand, forecast_units_per_day = forecasts.forecast_units_per_day, days_of_supply = forecasts.book_on_hand / forecasts.forecast_units_per_day.
Part 2: answered from the ontology layer. (Plan covers: Till sales of 5 kg atta on 11 June by hour, to check the afternoon silence; the cause is not recorded.)
hour = 9; units = 1.0
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-11'; group by hour(pos lines may.bill_ts); report hour = hour(pos lines may.bill_ts), units = sum of pos lines may.qty; sorted by hour asc.
Part 3: not answered: ecords: the ontology layer refused the plan (the question names day 11 of month 6 but the plan has no such date).
Part 4: not answered: ecords: the ontology layer refused the plan (the question names day 11 of month 6 but the plan has no such date).

## S9N06: Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?

Part 1: answered from the schema layer. (Plan covers: No cashier or shoplifter is recorded; checks the 55 premise: store counts of toned milk (book before, counted, adjustment).)
2 rows (columns: count_ts, book_before, counted, adjustment, trigger):
  2026-06-01T05:45 | 377.0 | 351.0 | -26.0 | scheduled full count
  2026-06-28T22:30 | 95.0 | 40.0 | -55.0 | scheduled full count
  How it was found: From stock count records; keep rows where stock counts.sku = 'MILK-TONED-500ML'; report count_ts = stock counts.count_ts, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment, trigger = stock counts.trigger; sorted by count_ts asc.
Part 2: answered from the schema layer. (Plan covers: Toned milk written off in June by reason (waste that may not have been booked is part of the gap).)
2 rows (columns: reason, units):
  damaged | 5.0
  expired | 291.0
  How it was found: From write-off records; keep rows where write offs.sku = 'MILK-TONED-500ML'; group by write offs.reason; report reason = write offs.reason, units = sum of write offs.units.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N07: If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?

Part 1: answered from the ontology layer. (Plan covers: Shoppers who leave without milk are not recorded; checks the margin premise: toned milk revenue and list cost of units sold in June (list margin).)
units_sold = 8649.0; revenue_inr = 224874.0; cost_of_sales_inr = 213630.3
  How it was found: From daily sales row records; inner-join product records on daily sales.sku = products.sku; keep rows where daily sales.sku = 'MILK-TONED-500ML'; report units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr, cost_of_sales_inr = sum of daily sales.units_sold * products.cost_inr.
Part 2: answered from the ontology layer. (Plan covers: Toned milk written off in June at list cost (waste side of margin after waste).)
units_written_off = 296.0; waste_cost_inr = 7311.2
  How it was found: From write-off records; inner-join product records on write offs.sku = products.sku; keep rows where write offs.sku = 'MILK-TONED-500ML'; report units_written_off = sum of write offs.units, waste_cost_inr = sum of write offs.units * products.cost_inr.
Part 3: answered from the schema layer. (Plan covers: Toned milk fresh deliveries in June (the standing order) in units.)
deliveries = 28; units_delivered = 9004.0
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'MILK-TONED-500ML'; report deliveries = count of *, units_delivered = sum of fresh deliveries.units.
Part 4: answered from the schema layer. (Plan covers: Shelf audits of toned milk by status: how often it was already empty (waste and the empty shelf are one decision).)
status = on shelf; audits = 8
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'MILK-TONED-500ML'; group by shelf audits.status; report status = shelf audits.status, audits = count of *.
Stand-ins used (not the real thing): list_margin (else): selling price minus the single cost per product is a list margin, not a real margin

## S9N08: Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?

Part 1: answered from the ontology layer. (Plan covers: No person is recorded; checks the on-time premise for the 22 June delivery (arrived_ts vs slot).)
shipment_id = SHP-260622; arrived_ts = 2026-06-22T06:12; slot_start = 2026-06-22T06:00; slot_end = 2026-06-22T06:30
  How it was found: From shipment records; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report shipment_id = shipments.shipment_id, arrived_ts = shipments.arrived_ts, slot_start = shipments.slot_start, slot_end = shipments.slot_end.
Part 2: answered from the ontology layer. (Plan covers: Goods receipt of the 22 June delivery: notice vs booked SKU and units per pallet line (booked by pallet-label scan, which copies the notice).)
4 rows (columns: sscc, line, asn_sku, sku_booked, asn_units, units_booked, receipt_method):
  029000010000010542 | 1 | ATTA-WW-5KG | ATTA-WW-5KG | 64.0 | 64.0 | pallet label (SSCC) scan against the shipping notice
  029000010000010542 | 2 | ATTA-WW-1KG | ATTA-WW-1KG | 90.0 | 90.0 | pallet label (SSCC) scan against the shipping notice
  029000010000010542 | 3 | RICE-SM-5KG | RICE-SM-5KG | 56.0 | 56.0 | pallet label (SSCC) scan against the shipping notice
  029000010000010559 | 4 | SUGAR-1KG | SUGAR-1KG | 50.0 | 50.0 | pallet label (SSCC) scan against the shipping notice
  How it was found: From goods-receipt line records; inner-join shipment records on goods receipts.shipment_id = shipments.shipment_id; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report sscc = goods receipts.sscc, line = goods receipts.line, asn_sku = goods receipts.asn_sku, sku_booked = goods receipts.sku_booked, asn_units = goods receipts.asn_units, units_booked = goods receipts.units_booked, receipt_method = goods receipts.receipt_method.
Part 3: answered from the ontology layer. (Plan covers: Pick lines on the 22 June delivery with slot picked vs the product's own slot (what was really loaded).)
4 rows (columns: line, sku, slot_picked, product_slot, cases_ordered, cases_confirmed):
  1 | ATTA-WW-5KG | A-07-03 | A-07-03 | 16.0 | 16.0
  2 | ATTA-WW-1KG | A-07-04 | A-07-04 | 9.0 | 9.0
  3 | RICE-SM-5KG | A-09-01 | A-09-01 | 14.0 | 14.0
  4 | SUGAR-1KG | B-03-04 | B-03-04 | 5.0 | 5.0
  How it was found: From pick confirmation records; inner-join shipment records on dc pick confirmations.shipment_id = shipments.shipment_id; inner-join product records on dc pick confirmations.sku = products.sku; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report line = dc pick confirmations.line, sku = dc pick confirmations.sku, slot_picked = dc pick confirmations.slot, product_slot = products.dc_slot, cases_ordered = dc pick confirmations.cases_ordered, cases_confirmed = dc pick confirmations.cases_confirmed.
Part 4: not answered: ecords: the ontology layer refused the plan (the question names day 22 of month 6 but the plan has no such date).
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N09: Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?

Part 1: answered from the ontology layer. (Plan covers: Checks the Rs 80 premise for the warehouse: atta corrections net (signed sum at cost) vs gross (sum of absolute values).)
net_value_inr = 6672.0; gross_value_inr = 22512.0; corrections = 2
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report net_value_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_inr = sum of abs(dc stock adjustments.value_at_cost_inr), corrections = count of *.
Part 2: answered from the ontology layer. (Plan covers: Store atta count adjustments at product cost: net vs gross.)
net_value_inr = -7018.5; gross_value_inr = 23522.5
  How it was found: From stock count records; inner-join product records on stock counts.sku = products.sku; keep rows where stock counts.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report net_value_inr = sum of stock counts.adjustment * products.cost_inr, gross_value_inr = sum of abs(stock counts.adjustment * products.cost_inr).
Part 3: answered from the schema layer. (Plan covers: Each warehouse atta correction with slot and reason, to see mirror-image pairs that net to nearly zero but are one event.)
2 rows (columns: adjusted_ts, sku, slot, cases, value_at_cost_inr, reason):
  2026-06-23T14:20 | ATTA-WW-1KG | A-07-04 | -16.0 | -7920.0 | short pick: slot count variance
  2026-06-25T10:00 | ATTA-WW-5KG | A-07-03 | 16.0 | 14592.0 | cycle count variance
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-1KG', 'ATTA-WW-5KG', 'ATTA-WW-10KG']; report adjusted_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, cases = dc stock adjustments.cases, value_at_cost_inr = dc stock adjustments.value_at_cost_inr, reason = dc stock adjustments.reason; sorted by adjusted_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N10: Which pallet on the 22 June shipment failed its dispatch weight check?

answered from the ontology layer. (Plan covers: Checks the premise: weight-check status of each pallet on the shipment that arrived on 22 June.)
2 rows (columns: shipment_id, sscc, cases, notice_kg, weight_check):
  SHP-260622 | 029000010000010542 | 39.0 | 723.7 | not weighed
  SHP-260622 | 029000010000010559 | 5.0 | 73.5 | not weighed
  How it was found: From pallet records; inner-join shipment records on pallets.shipment_id = shipments.shipment_id; keep rows where day(shipments.arrived_ts) = '2026-06-22'; report shipment_id = pallets.shipment_id, sscc = pallets.sscc, cases = pallets.cases, notice_kg = pallets.notice_kg, weight_check = pallets.weight_check.

## S9N11: If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?

Part 1: answered from the schema layer. (Plan covers: The future change in the scorecard is not recorded; this shows today's dispatch weight checks on June pallets.)
weight_check = not weighed; pallets = 30
  How it was found: From pallet records; group by pallets.weight_check; report weight_check = pallets.weight_check, pallets = count of *.
Part 2: answered from the schema layer. (Plan covers: Today's receipt method at the store (pallet-label scan, not case scan).)
receipt_method = pallet label (SSCC) scan against the shipping notice; lines = 70
  How it was found: From goods-receipt line records; group by goods receipts.receipt_method; report receipt_method = goods receipts.receipt_method, lines = count of *.
Part 3: answered from the ontology layer. (Plan covers: Current OTIF inputs per delivery (on time = arrived within slot; in full = confirmed vs ordered cases), which the scorecard copies from picks.)
25 rows (columns: shipment_id, arrived_ts, slot_start, slot_end, cases_ordered, cases_confirmed):
  SHP-260601 | 2026-06-01T06:20 | 2026-06-01T06:00 | 2026-06-01T06:30 | 18.0 | 18.0
  SHP-260602 | 2026-06-02T06:00 | 2026-06-02T06:00 | 2026-06-02T06:30 | 5.0 | 5.0
  SHP-260603 | 2026-06-03T06:16 | 2026-06-03T06:00 | 2026-06-03T06:30 | 63.0 | 63.0
  SHP-260604 | 2026-06-04T06:00 | 2026-06-04T06:00 | 2026-06-04T06:30 | 7.0 | 7.0
  SHP-260605 | 2026-06-05T06:21 | 2026-06-05T06:00 | 2026-06-05T06:30 | 25.0 | 25.0
  SHP-260606 | 2026-06-06T06:12 | 2026-06-06T06:00 | 2026-06-06T06:30 | 50.0 | 50.0
  SHP-260607 | 2026-06-07T06:10 | 2026-06-07T06:00 | 2026-06-07T06:30 | 23.0 | 23.0
  SHP-260608 | 2026-06-08T06:06 | 2026-06-08T06:00 | 2026-06-08T06:30 | 45.0 | 45.0
  SHP-260609 | 2026-06-09T06:17 | 2026-06-09T06:00 | 2026-06-09T06:30 | 26.0 | 26.0
  SHP-260611 | 2026-06-11T08:21 | 2026-06-11T06:00 | 2026-06-11T06:30 | 39.0 | 38.0
  ... and 15 more
  How it was found: From shipment records; inner-join pick confirmation records on shipments.shipment_id = dc pick confirmations.shipment_id; group by shipments.shipment_id; report shipment_id = shipments.shipment_id, arrived_ts = min of shipments.arrived_ts, slot_start = min of shipments.slot_start, slot_end = max of shipments.slot_end, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed; sorted by arrived_ts asc.

## S9N12: What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?

Part 1: answered from the ontology layer. (Plan covers: OTIF per delivery in June: each shipment's arrival vs slot and cases confirmed vs ordered, to compare with the offered 92/90/88/84%.)
25 rows (columns: shipment_id, arrived_ts, slot_start, slot_end, cases_ordered, cases_confirmed):
  SHP-260601 | 2026-06-01T06:20 | 2026-06-01T06:00 | 2026-06-01T06:30 | 18.0 | 18.0
  SHP-260602 | 2026-06-02T06:00 | 2026-06-02T06:00 | 2026-06-02T06:30 | 5.0 | 5.0
  SHP-260603 | 2026-06-03T06:16 | 2026-06-03T06:00 | 2026-06-03T06:30 | 63.0 | 63.0
  SHP-260604 | 2026-06-04T06:00 | 2026-06-04T06:00 | 2026-06-04T06:30 | 7.0 | 7.0
  SHP-260605 | 2026-06-05T06:21 | 2026-06-05T06:00 | 2026-06-05T06:30 | 25.0 | 25.0
  SHP-260606 | 2026-06-06T06:12 | 2026-06-06T06:00 | 2026-06-06T06:30 | 50.0 | 50.0
  SHP-260607 | 2026-06-07T06:10 | 2026-06-07T06:00 | 2026-06-07T06:30 | 23.0 | 23.0
  SHP-260608 | 2026-06-08T06:06 | 2026-06-08T06:00 | 2026-06-08T06:30 | 45.0 | 45.0
  SHP-260609 | 2026-06-09T06:17 | 2026-06-09T06:00 | 2026-06-09T06:30 | 26.0 | 26.0
  SHP-260611 | 2026-06-11T08:21 | 2026-06-11T06:00 | 2026-06-11T06:30 | 39.0 | 38.0
  ... and 15 more
  How it was found: From shipment records; inner-join pick confirmation records on shipments.shipment_id = dc pick confirmations.shipment_id; group by shipments.shipment_id; report shipment_id = shipments.shipment_id, arrived_ts = min of shipments.arrived_ts, slot_start = min of shipments.slot_start, slot_end = max of shipments.slot_end, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed; sorted by arrived_ts asc.
Part 2: answered from the schema layer. (Plan covers: In full per order line: pick lines whose confirmed cases met ordered cases.)
lines_in_full = 68
  How it was found: From pick confirmation records; keep rows where dc pick confirmations.cases_confirmed >= dc pick confirmations.cases_ordered; report lines_in_full = count of *.
Part 3: answered from the schema layer. (Plan covers: Per line and per case totals: all pick lines, cases ordered and confirmed.)
lines = 70; cases_ordered = 707.0; cases_confirmed = 704.0
  How it was found: From pick confirmation records; report lines = count of *, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed.

## S9N13: Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?

Part 1: answered from the ontology layer. (Plan covers: Checks the premise: approved till payments in June vs distinct bills they cover.)
approved_payments = 30077; bills = 30077
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; report approved_payments = count of *, bills = count distinct of pos payments.bill_id.
Part 2: answered from the ontology layer. (Plan covers: Extra debits: provider UPI successes whose RRN has no approved till payment (charged twice until proven otherwise); bills stand in for customers.)
extra_debits = 26; bills = 0; amount_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report extra_debits = count of *, bills = count distinct of psp upi report.bill_ref, amount_inr = sum of psp upi report.amount_inr.
Part 3: answered from the schema layer. (Plan covers: June complaints by kind (charged twice, debited but the till said failed).)
2 rows (columns: kind, complaints):
  charged twice | 23
  debited but the till said failed | 3
  How it was found: From complaint records; group by customer complaints.kind; report kind = customer complaints.kind, complaints = count of *.

## S9N14: Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.

Part 1: answered from the schema layer. (Plan covers: Checks the premise: UPI timeouts ('failed: no response') in June and how many carry an RRN to join on (a timeout has no RRN).)
timeouts = 48; timeouts_with_rrn = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; report timeouts = count of *, timeouts_with_rrn = count of pos payments.rrn.
Part 2: answered from the ontology layer. (Plan covers: Final provider status of the timeouts, joined on bill ID (bill_id = bill_ref) since the RRN is missing.)
psp_status = None; rows = 48; timeouts = 3
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.bill_id = psp upi report.bill_ref; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by psp upi report.status; report psp_status = psp upi report.status, rows = count of *, timeouts = count distinct of pos payments.attempt.

## S9N15: Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?

Part 1: answered from the schema layer. (Plan covers: Checks the 0.76% premise: June UPI till attempts by status.)
4 rows (columns: till_status, attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *.
Part 2: answered from the ontology layer. (Plan covers: Hours with 3 or more UPI timeouts: bursts a monthly average hides.)
2 rows (columns: date, hour, timeouts):
  2026-06-20 | 18 | 12
  2026-06-20 | 19 | 16
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by day(pos payments.ts), hour(pos payments.ts); keep groups where timeouts >= 3; report date = day(pos payments.ts), hour = hour(pos payments.ts), timeouts = count of *; sorted by date asc.
Part 3: answered from the ontology layer. (Plan covers: Customer harm: extra debits (provider success with no approved till payment).)
extra_debits = 26; amount_inr = 13366.06
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report extra_debits = count of *, amount_inr = sum of psp upi report.amount_inr.

## S9N16: Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?

Part 1: answered from the ontology layer. (Plan covers: The reason and any accounting rule for recognizing revenue are not recorded; checks the 17: provider successes initiated 20-21 June with no approved till payment, with refund and complaint status.)
17 rows (columns: rrn, bill_ref, amount_inr, initiated_ts, till_status, refund_completed_ts, complaint_resolution):
  617118013318 |  | 438.73 | 2026-06-20T18:22:03 |  | 2026-06-25T17:00:00 | refunded after the store matched the credit by hand
  617118013325 |  | 342.13 | 2026-06-20T18:32:55 |  | 2026-06-28T14:00:00 | refunded after the store matched the credit by hand
  617118013326 |  | 342.13 | 2026-06-20T18:33:25 |  | 2026-06-27T14:00:00 | refunded after the store matched the credit by hand
  617118013344 |  | 1064.47 | 2026-06-20T18:48:25 |  | 2026-06-28T14:00:00 | refunded after the store matched the credit by hand
  617118013342 |  | 168.21 | 2026-06-20T18:48:34 |  | 2026-06-25T10:00:00 | refunded after the store matched the credit by hand
  617118013343 |  | 168.21 | 2026-06-20T18:49:04 |  | 2026-06-26T10:00:00 | refunded after the store matched the credit by hand
  617119013351 |  | 372.15 | 2026-06-20T19:01:34 |  | 2026-06-27T10:00:00 | refunded after the store matched the credit by hand
  617119013361 |  | 171.7 | 2026-06-20T19:09:24 |  | 2026-06-26T12:00:00 | refunded after the store matched the credit by hand
  617119013363 |  | 592.94 | 2026-06-20T19:11:36 |  | 2026-06-24T18:00:00 | refunded after the store matched the credit by hand
  617119013372 |  | 398.2 | 2026-06-20T19:21:36 |  | 2026-06-25T11:00:00 | refunded after the store matched the credit by hand
  ... and 7 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join UPI refund records on psp upi report.rrn = upi refunds.rrn; left-join complaint records on psp upi report.rrn = customer complaints.rrn; keep rows where psp upi report.status = 'success' and day(psp upi report.initiated_ts) between 2026-06-20 and 2026-06-21 and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, initiated_ts = psp upi report.initiated_ts, till_status = pos payments.till_status, refund_completed_ts = upi refunds.completed_ts, complaint_resolution = customer complaints.resolution; sorted by initiated_ts asc.
Part 2: answered from the ontology layer. (Plan covers: Same extra debits on 20-21 June summarised: count and amount (these are customers' money owed back, not unclaimed revenue).)
credits = 17; amount_inr = 7825.69
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and day(psp upi report.initiated_ts) between 2026-06-20 and 2026-06-21 and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report credits = count of *, amount_inr = sum of psp upi report.amount_inr.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N17: Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?

Part 1: answered from the ontology layer. (Plan covers: Refund wait from the extra debit (provider success) to refund completion, which is when the clock starts; checks the 3-day median premise.)
23 rows (columns: rrn, debit_ts, requested_ts, completed_ts, days_from_debit):
  615619003319 | 2026-06-05T19:59:20 | 2026-06-06T13:00:00 | 2026-06-08T13:00:00 | -2.7087962962687016
  617119013372 | 2026-06-21T22:21:42 | 2026-06-22T11:00:00 | 2026-06-25T11:00:00 | -3.526597222313285
  616918011772 | 2026-06-18T18:45:00 | 2026-06-20T11:00:00 | 2026-06-22T11:00:00 | -3.6770833334885538
  617119013363 | 2026-06-20T19:12:47 | 2026-06-22T18:00:00 | 2026-06-24T18:00:00 | -3.949456018395722
  617119013379 | 2026-06-20T19:30:18 | 2026-06-22T19:00:00 | 2026-06-24T19:00:00 | -3.978958333376795
  616517008996 | 2026-06-14T17:01:54 | 2026-06-15T19:00:00 | 2026-06-18T19:00:00 | -4.082013888750225
  617119013375 | 2026-06-21T02:02:13 | 2026-06-22T15:00:00 | 2026-06-25T15:00:00 | -4.540127314627171
  617119013400 | 2026-06-20T20:50:48 | 2026-06-22T12:00:00 | 2026-06-25T12:00:00 | -4.631388888694346
  617118013342 | 2026-06-20T18:49:47 | 2026-06-23T10:00:00 | 2026-06-25T10:00:00 | -4.632094907108694
  616011005544 | 2026-06-09T13:52:31 | 2026-06-10T10:00:00 | 2026-06-14T10:00:00 | -4.83853009250015
  ... and 13 more
  How it was found: From UPI refund records; inner-join UPI service provider's transaction records on upi refunds.rrn = psp upi report.rrn; keep rows where psp upi report.status = 'success'; report rrn = upi refunds.rrn, debit_ts = psp upi report.status_ts, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, days_from_debit = days_between(psp upi report.status_ts, upi refunds.completed_ts); sorted by days_from_debit desc.
Part 2: answered from the ontology layer. (Plan covers: Refunds that took more than 5 days from the extra debit.)
refunds_over_5_days = 0
  How it was found: From UPI refund records; inner-join UPI service provider's transaction records on upi refunds.rrn = psp upi report.rrn; keep rows where psp upi report.status = 'success' and days_between(psp upi report.status_ts, upi refunds.completed_ts) > 5; report refunds_over_5_days = count of *.
Part 3: answered from the ontology layer. (Plan covers: Extra debits with no refund on record at all (never refunded, so they cannot have met any turnaround).)
unrefunded_extra_debits = 3; amount_inr = 2064.2
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; left-join UPI refund records on psp upi report.rrn = upi refunds.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved') and upi refunds.refund_id is empty; report unrefunded_extra_debits = count of *, amount_inr = sum of psp upi report.amount_inr.
