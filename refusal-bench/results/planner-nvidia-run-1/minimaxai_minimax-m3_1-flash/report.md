## S8N01: How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"fn": "day", "args": [{"col": "daily-sales-june.date"}]} is not in the plan form).

## S8N02: Which shelf audits found an item empty while the hourly book showed stock above zero?

answered from the ontology layer. (Plan covers: Shelf audits with status 'empty' where the same day's hourly book stock (inventory-book closing book_on_hand_close) was above zero, per the rule that book stock is a belief and the shelf audit is the observation.)
81 rows (columns: audit_ts, sku, book_on_hand_close, book_date):
  2026-06-05T11:00 | SUGAR-1KG | 21.0 | 2026-06-01
  2026-06-05T11:00 | SUGAR-1KG | 56.0 | 2026-06-02
  2026-06-05T11:00 | SUGAR-1KG | 35.0 | 2026-06-03
  2026-06-05T11:00 | SUGAR-1KG | 4.0 | 2026-06-04
  2026-06-05T11:00 | SUGAR-1KG | 55.0 | 2026-06-05
  2026-06-05T11:00 | SUGAR-1KG | 30.0 | 2026-06-06
  2026-06-05T11:00 | SUGAR-1KG | 59.0 | 2026-06-08
  2026-06-05T11:00 | SUGAR-1KG | 50.0 | 2026-06-09
  2026-06-05T11:00 | SUGAR-1KG | 30.0 | 2026-06-10
  2026-06-05T11:00 | SUGAR-1KG | 54.0 | 2026-06-11
  ... and 71 more
  How it was found: From shelf-audit row records; inner-join book-stock row records on shelf audits.sku = inventory book.sku; keep rows where shelf audits.status = 'empty' and inventory book.book_on_hand_close > 0; report audit_ts = shelf audits.audit_ts, sku = shelf audits.sku, book_on_hand_close = inventory book.book_on_hand_close, book_date = inventory book.date; sorted by audit_ts asc.

## S8N03: On which days did any item's closing book stock go below zero?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).

## S8N04: Which stock counts disagreed with the book stock by more than 2%?

I can't answer this from Store 014's records: error OperationalError

## S8N05: Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?

Part 1: answered from the schema layer. (Plan covers: Week 1 (2026-06-01 to 2026-06-07) units sold per warehouse item, using daily sales (till lines) as the sales record.)
11 rows (columns: sku, week1_units):
  ATTA-WW-10KG | 87.0
  ATTA-WW-1KG | 238.0
  ATTA-WW-5KG | 217.0
  BREAD-WHITE-400G | 350.0
  CURD-500G | 542.0
  DAL-TOOR-1KG | 158.0
  MILK-FC-500ML | 728.0
  MILK-TONED-500ML | 2094.0
  OIL-SUN-1L | 210.0
  RICE-SM-5KG | 180.0
  ... and 1 more
  How it was found: From daily sales row records; keep rows where daily sales.date between 2026-06-01 and 2026-06-07; group by daily sales.sku; report sku = daily sales.sku, week1_units = sum of daily sales.units_sold; sorted by sku asc.
Part 2: answered from the schema layer. (Plan covers: Week 2 (2026-06-08 to 2026-06-14) units sold per warehouse item, using daily sales (till lines) as the sales record.)
11 rows (columns: sku, week2_units):
  ATTA-WW-10KG | 61.0
  ATTA-WW-1KG | 207.0
  ATTA-WW-5KG | 88.0
  BREAD-WHITE-400G | 441.0
  CURD-500G | 454.0
  DAL-TOOR-1KG | 139.0
  MILK-FC-500ML | 829.0
  MILK-TONED-500ML | 2064.0
  OIL-SUN-1L | 195.0
  RICE-SM-5KG | 153.0
  ... and 1 more
  How it was found: From daily sales row records; keep rows where daily sales.date between 2026-06-08 and 2026-06-14; group by daily sales.sku; report sku = daily sales.sku, week2_units = sum of daily sales.units_sold; sorted by sku asc.

## S8N06: What time did toned milk record its last sale each day, and how many pouches were written off?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N07: Why did 5 kg atta sales fall in the week of 8 June?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N08: Was 5 kg atta in stock on Thursday 11 June?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).

## S8N09: Are shoppers switching from 5 kg to 1 kg atta?

Part 1: not answered: ecords: the ontology layer refused the plan (select 'product_name' must be aggregated or in group_by).
Part 2: answered from the ontology layer. (Plan covers: Daily units and revenue for 5 kg and 1 kg atta from daily-sales, the store's daily sales record, as a second view of the same switching question.)
56 rows (columns: sku, sale_date, units_sold, revenue_inr):
  ATTA-WW-1KG | 2026-06-01 | 22.0 | 1276.0
  ATTA-WW-5KG | 2026-06-01 | 30.0 | 7950.0
  ATTA-WW-1KG | 2026-06-02 | 35.0 | 2030.0
  ATTA-WW-5KG | 2026-06-02 | 36.0 | 9540.0
  ATTA-WW-1KG | 2026-06-03 | 41.0 | 2378.0
  ATTA-WW-5KG | 2026-06-03 | 22.0 | 5830.0
  ATTA-WW-1KG | 2026-06-04 | 24.0 | 1392.0
  ATTA-WW-5KG | 2026-06-04 | 28.0 | 7420.0
  ATTA-WW-1KG | 2026-06-05 | 24.0 | 1392.0
  ATTA-WW-5KG | 2026-06-05 | 32.0 | 8480.0
  ... and 46 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-5KG', 'ATTA-WW-1KG']; group by daily sales.sku, day(daily sales.date); report sku = daily sales.sku, sale_date = day(daily sales.date), units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr; sorted by sale_date asc, sku asc.

## S8N10: What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?

Part 1: not answered: ecords: the schema layer refused the plan (node {"op": "=", "args": [{"col": "shelf-audits-june.status"}, {"lit": "on shelf"}]} is not in the plan form).
Part 2: answered from the schema layer. (Plan covers: Book-stock belief for 5 kg atta in June: daily closing book stock (packs) averaged over its book days, shown as the belief that shelf audits can contradict.)
sku = ATTA-WW-5KG; book_days = 28; book_on_hand_close_avg = 47.892857142857146
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG'; group by inventory book.sku; report sku = inventory book.sku, book_days = count of *, book_on_hand_close_avg = avg of inventory book.book_on_hand_close.
Part 3: answered from the schema layer. (Plan covers: Till evidence for 5 kg atta: count of till lines, units sold and sales value from pos-lines (sales are till lines), to compare against the book-stock belief and the shelf audits.)
sku = ATTA-WW-5KG; till_lines = 1177; units_sold = 1198.0; sales_value_inr = 317470.0
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG'; group by pos lines may.sku_scanned; report sku = pos lines may.sku_scanned, till_lines = count of *, units_sold = sum of pos lines may.qty, sales_value_inr = sum of pos lines may.line_amount.

## S8N11: What has daily demand for 5 kg atta been in June so far?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: needs a longer period than the records cover

## S8N12: How many shoppers left without 5 kg atta, and what were the lost sales in June?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"fn": "day", "args": [{"col": "pos-lines-may-june.bill_ts"}]} is not in the plan form).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8E13: How many of June's deliveries arrived inside their 06:00–06:30 slot?

answered from the schema layer. (Plan covers: Counts June shipments whose arrived_ts falls within their own slot_start–slot_end window (on-time per delivery).)
deliveries_in_slot = 23
  How it was found: From shipment records; keep rows where (shipments.arrived_ts >= '2026-06-01T00:00' and shipments.arrived_ts < '2026-07-01T00:00' and shipments.arrived_ts >= shipments.slot_start and shipments.arrived_ts <= shipments.slot_end); report deliveries_in_slot = count of *.

## S8N14: How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?

Part 1: not answered: ecords: the schema layer refused the plan (node {"op": "=", "args": [{"col": "pallets-june.weight_check"}, {"lit": "not weighed" is not in the plan form).
Part 2: answered from the ontology layer. (Plan covers: Counts goods-receipt lines and distinct pallet labels (SSCC) scanned at receipt, the case-scan witness for pallets received.)
receipt_lines = 70; distinct_sscc_scanned = 30; distinct_pallets_case_scanned = 30
  How it was found: From goods-receipt line records; report receipt_lines = count of *, distinct_sscc_scanned = count distinct of goods receipts.sscc, distinct_pallets_case_scanned = count distinct of goods receipts.sscc.

## S8N15: What was the case fill rate across June's store orders according to the shipping notices?

answered from the ontology layer. (Plan covers: Case fill rate across June's store orders = total cases on shipping notices divided by total cases ordered, per the fill-rate definition (cases delivered per shipping notice over cases ordered).)
fill_rate = 0.9944349315068494
  How it was found: From shipping-notice line records; inner-join store order line records on shipping notice lines.order_id = store orders.order_id; report fill_rate = sum of shipping notice lines.cases / sum of store orders.cases.

## S8N16: What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?

Part 1: answered from the ontology layer. (Plan covers: Warehouse (DC) stock corrections: net value is the sum of value at cost with its sign, gross is the sum of absolute values.)
net_value_at_cost_inr = 6672.0; gross_value_at_cost_inr = 22512.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; report net_value_at_cost_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_at_cost_inr = sum of abs(dc stock adjustments.value_at_cost_inr).
Part 2: answered from the ontology layer. (Plan covers: Store stock corrections: net and gross adjustment in packs from hand counts (no value-at-cost column exists for store counts).)
net_adjustment_packs = 38.0; gross_adjustment_packs = 406.0
  How it was found: From stock count records; report net_adjustment_packs = sum of stock counts.adjustment, gross_adjustment_packs = sum of abs(stock counts.adjustment).

## S8N17: Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?

Part 1: answered from the schema layer. (Plan covers: Warehouse count corrections (dc-stock-adjustments) with their timestamp, product, slot, cases, units, value at cost and reason, as one side of the mirror-image pair test.)
2 rows (columns: adjustment_ts, sku, slot, cases, units, value_at_cost_inr, reason):
  2026-06-23T14:20 | ATTA-WW-1KG | A-07-04 | -16.0 | -160.0 | -7920.0 | short pick: slot count variance
  2026-06-25T10:00 | ATTA-WW-5KG | A-07-03 | 16.0 | 64.0 | 14592.0 | cycle count variance
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; report adjustment_ts = dc stock adjustments.adjusted_ts, sku = dc stock adjustments.sku, slot = dc stock adjustments.slot, cases = dc stock adjustments.cases, units = dc stock adjustments.units, value_at_cost_inr = dc stock adjustments.value_at_cost_inr, reason = dc stock adjustments.reason; sorted by adjustment_ts asc.
Part 2: answered from the schema layer. (Plan covers: Store count corrections (stock-counts) with their timestamp, product, adjustment in packs, book before, counted and trigger, as the other side of the mirror-image pair test.)
25 rows (columns: count_ts, sku, adjustment, book_before, counted, trigger):
  2026-06-01T05:45 | ATTA-WW-5KG | 0.0 | 36.0 | 36.0 | scheduled full count
  2026-06-01T05:45 | ATTA-WW-1KG | -5.0 | 92.0 | 87.0 | scheduled full count
  2026-06-01T05:45 | ATTA-WW-10KG | 1.0 | 28.0 | 29.0 | scheduled full count
  2026-06-01T05:45 | RICE-SM-5KG | -2.0 | 66.0 | 64.0 | scheduled full count
  2026-06-01T05:45 | DAL-TOOR-1KG | -2.0 | 15.0 | 13.0 | scheduled full count
  2026-06-01T05:45 | OIL-SUN-1L | -5.0 | 82.0 | 77.0 | scheduled full count
  2026-06-01T05:45 | SUGAR-1KG | -2.0 | 46.0 | 44.0 | scheduled full count
  2026-06-01T05:45 | MILK-TONED-500ML | -26.0 | 377.0 | 351.0 | scheduled full count
  2026-06-01T05:45 | MILK-FC-500ML | 15.0 | 94.0 | 109.0 | scheduled full count
  2026-06-01T05:45 | CURD-500G | -3.0 | 115.0 | 112.0 | scheduled full count
  ... and 15 more
  How it was found: From stock count records; report count_ts = stock counts.count_ts, sku = stock counts.sku, adjustment = stock counts.adjustment, book_before = stock counts.book_before, counted = stock counts.counted, trigger = stock counts.trigger; sorted by count_ts asc.

## S8N18: Which goods receipts did not survive the next stock count within a week?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).

## S8N19: Was the 22 June delivery on time and in full?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"op": "and", "args": [{"op": ">=", "args": [{"col": "shipments-june.arrived_ts" is not in the plan form).

## S8N20: What was Store 014's OTIF from the warehouse in June?

Part 1: answered from the schema layer. (Plan covers: Per-order-line OTIF for June: cases confirmed against cases ordered from the warehouse pick confirmations (in-full per order line).)
25 rows (columns: order_id, cases_ordered, cases_confirmed):
  SO-260531 | 18.0 | 18.0
  SO-260601 | 5.0 | 5.0
  SO-260602 | 63.0 | 63.0
  SO-260603 | 7.0 | 7.0
  SO-260604 | 25.0 | 25.0
  SO-260605 | 50.0 | 50.0
  SO-260606 | 23.0 | 23.0
  SO-260607 | 45.0 | 45.0
  SO-260608 | 26.0 | 26.0
  SO-260610 | 39.0 | 38.0
  ... and 15 more
  How it was found: From pick confirmation records; group by dc pick confirmations.order_id; report order_id = dc pick confirmations.order_id, cases_ordered = sum of dc pick confirmations.cases_ordered, cases_confirmed = sum of dc pick confirmations.cases_confirmed.
Part 2: not answered: ecords: the schema layer refused the plan (node {"op": "and", "args": [{"op": ">=", "args": [{"col": "shipments-june.arrived_ts" is not in the plan form).

## S8N21: Why was 5 kg atta off the shelf from 23 to 26 June?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N22: Is the 5 kg atta missing at the store theft?

Part 1: answered from the ontology layer. (Plan covers: Warehouse stock corrections for 5 kg atta (ATTA-WW-5KG) by recorded reason, with net and gross value at cost, to check whether any recorded correction is labelled as theft.)
reason = cycle count variance; net_units = 64.0; net_value_at_cost_inr = 14592.0; gross_value_at_cost_inr = 14592.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku = 'ATTA-WW-5KG'; group by dc stock adjustments.reason; report reason = dc stock adjustments.reason, net_units = sum of dc stock adjustments.units, net_value_at_cost_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_at_cost_inr = sum of abs(dc stock adjustments.value_at_cost_inr); sorted by reason asc.
Part 2: answered from the schema layer. (Plan covers: Store hand-count adjustments for 5 kg atta by recorded trigger, to check whether any count is recorded as theft.)
2 rows (columns: trigger, count_rows, net_adjustment_packs):
  manager request after complaints | 1 | -63.0
  scheduled full count | 2 | -1.0
  How it was found: From stock count records; keep rows where stock counts.sku = 'ATTA-WW-5KG'; group by stock counts.trigger; report trigger = stock counts.trigger, count_rows = count of *, net_adjustment_packs = sum of stock counts.adjustment; sorted by trigger asc.
Part 3: answered from the schema layer. (Plan covers: Write-offs for 5 kg atta by recorded reason (damaged or expired), the only recorded non-sale stock loss for this product.)
reason = damaged; units_written_off = 3.0
  How it was found: From write-off records; keep rows where write offs.sku = 'ATTA-WW-5KG'; group by write offs.reason; report reason = write offs.reason, units_written_off = sum of write offs.units; sorted by reason asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S8N23: Which delivery, pallet (SSCC), and line should the store raise a claim against?

Part 1: answered from the ontology layer. (Plan covers: Identifies the warehouse short-pick stock corrections (reason 'short pick: slot count variance') by SKU, product, slot and timestamp, with the cases, units and value at cost that a claim would be based on.)
1 rows (columns: sku, product_name, slot, adjusted_ts, short_pick_cases, short_pick_units, value_at_cost_inr):
  ATTA-WW-1KG | Whole wheat atta 1 kg | A-07-04 | 2026-06-23T14:20 | -16.0 | -160.0 | -7920.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; inner-join product records on dc stock adjustments.sku = products.sku; keep rows where dc stock adjustments.reason = 'short pick: slot count variance'; group by dc stock adjustments.sku, products.name, dc stock adjustments.slot, dc stock adjustments.adjusted_ts; report sku = dc stock adjustments.sku, product_name = products.name, slot = dc stock adjustments.slot, adjusted_ts = dc stock adjustments.adjusted_ts, short_pick_cases = sum of dc stock adjustments.cases, short_pick_units = sum of dc stock adjustments.units, value_at_cost_inr = sum of dc stock adjustments.value_at_cost_inr; sorted by value_at_cost_inr desc.
Part 2: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).

## S8N24: How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8A25: How many UPI payments did the tills attempt in June?

answered from the schema layer. (Plan covers: Counts UPI payment attempts made by the tills in June, where a payment attempt is one try (tender, till_status).)
upi_payment_attempts = 19166
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report upi_payment_attempts = count of *.

## S8E26: How many UPI attempts timed out (failed: no response) without receiving an RRN?

answered from the schema layer. (Plan covers: Counts UPI payment attempts with till_status 'failed: no response' that have no RRN, per the definition that a UPI timeout has no RRN.)
upi_timeouts_without_rrn = 48
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'failed: no response' and pos payments.rrn is empty; report upi_timeouts_without_rrn = count of *.

## S8N27: Which successes in the provider's UPI report have no matching approved payment at the till?

answered from the ontology layer. (Plan covers: Provider UPI transactions with status 'success' that have no till payment attempt with till_status 'approved' for the same RRN, per the definition that a provider success with no approved till payment is an extra debit.)
26 rows (columns: rrn, bill_ref, amount_inr, initiated_ts, status, till_status, till_attempt):
  615521002766 |  | 143.11 | 2026-06-04T21:32:26 | success |  | 
  615619003319 |  | 224.51 | 2026-06-05T19:58:33 | success |  | 
  615908004963 |  | 1325.54 | 2026-06-08T08:39:27 | success |  | 
  615909004985 |  | 564.24 | 2026-06-08T09:08:34 | success |  | 
  616011005544 |  | 532.71 | 2026-06-09T11:22:07 | success |  | 
  616517008996 |  | 362.94 | 2026-06-14T17:00:31 | success |  | 
  616918011772 |  | 963.27 | 2026-06-18T18:43:56 | success |  | 
  617118013318 |  | 438.73 | 2026-06-20T18:22:03 | success |  | 
  617118013325 |  | 342.13 | 2026-06-20T18:32:55 | success |  | 
  617118013326 |  | 342.13 | 2026-06-20T18:33:25 | success |  | 
  ... and 16 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.attempt is empty or pos payments.till_status != 'approved'); report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, initiated_ts = psp upi report.initiated_ts, status = psp upi report.status, till_status = pos payments.till_status, till_attempt = pos payments.attempt; sorted by initiated_ts asc.

## S8N28: Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?

Part 1: answered from the ontology layer. (Plan covers: Counts UPI till timeouts ('failed: no response') per hour of the day in June 2026, the hours with a burst of 3 or more timeouts.)
4 rows (columns: hour, timeouts):
  11 | 3
  16 | 3
  18 | 13
  19 | 17
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'failed: no response' and pos payments.ts between 2026-06-01T00:00 and 2026-06-30T23:59; group by hour(pos payments.ts); keep groups where timeouts >= 3; report hour = hour(pos payments.ts), timeouts = count of pos payments.attempt; sorted by hour asc.
Part 2: answered from the schema layer. (Plan covers: Computes the June 2026 monthly count of UPI timeouts and the 10x monthly-rate threshold used to judge a burst.)
monthly_timeouts = 48
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'failed: no response' and pos payments.ts between 2026-06-01T00:00 and 2026-06-30T23:59; keep groups where monthly_timeouts * 10 > 0; report monthly_timeouts = count of pos payments.attempt.

## S8N29: How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?

Part 1: answered from the ontology layer. (Plan covers: Counts distinct June UPI bills with an approved till payment above ₹2,000, and sums their approved UPI amounts as the base for the fee.)
200 rows (columns: bill_count, bill_amount_inr):
  1 | 2977.01
  1 | 2381.39
  1 | 4599.82
  1 | 2073.68
  1 | 2635.97
  1 | 2789.39
  1 | 4263.67
  1 | 2650.58
  1 | 2709.93
  1 | 2441.74
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 2000; group by pos payments.bill_id; report bill_count = count distinct of pos payments.bill_id, bill_amount_inr = sum of pos payments.amount_inr.
Part 2: answered from the schema layer. (Plan covers: Computes the 0.4% MDR fee on the summed approved UPI amounts of those bills, with the ₹300 cap applied per bill (cap binds above ₹75,000 per bill).)
mdr_fee_inr = 7905.5596399999995; capped_mdr_fee_inr = 7605.5596399999995
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved' and pos payments.amount_inr > 2000; report mdr_fee_inr = 0.004 * sum of pos payments.amount_inr, capped_mdr_fee_inr = 0.004 * sum of pos payments.amount_inr - 75000.

## S8N30: Which customers were charged three times for a single bill?

answered from the ontology layer. (Plan covers: Bills (the stand-in for a shopper) with three or more approved till payment attempts that the UPI provider also reports as success, i.e. bills charged three times.)
No rows matched.
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.till_status = 'approved' and psp upi report.status = 'success'; group by pos payments.bill_id; keep groups where approved_success_attempts >= 3; report bill_id = pos payments.bill_id, approved_success_attempts = count of pos payments.attempt, distinct_rrns = count distinct of pos payments.rrn; sorted by approved_success_attempts desc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N31: Did any customer pay twice in June, and how many?

answered from the ontology layer. (Plan covers: Bills where the till shows more than one approved payment attempt for the same RRN, i.e. a customer charged twice, per Rule 10 (one bill, one payment; a debit with no approved payment is an extra debit) and the provider's final status by RR)
No rows matched.
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.till_status = 'approved' and psp upi report.status = 'success' and pos payments.rrn is not empty; group by pos payments.bill_id, pos payments.rrn; keep groups where approved_till_attempts > 1; report bill_id = pos payments.bill_id, rrn = pos payments.rrn, approved_till_attempts = count of pos payments.attempt, provider_success_amount_inr = sum of psp upi report.amount_inr; sorted by approved_till_attempts desc.

## S8N32: What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8N33: Why are 17 UPI credits from 20 and 21 June sitting in suspense?

Part 1: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 2: answered from the schema layer. (Plan covers: Counts UPI payment attempts by till status on 20 and 21 June 2026 to see which attempts were approved, declined, failed or timed out.)
4 rows (columns: till_status, attempts, amount_inr):
  approved | 597 | 362451.59
  failed: no response | 29 | 14253.82
  declined | 20 | 9647.18
  failed | 7 | 6037.26
  How it was found: From payment attempt records; keep rows where pos payments.ts between 2026-06-20 and 2026-06-21 and pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *, amount_inr = sum of pos payments.amount_inr; sorted by attempts desc.
Part 3: answered from the schema layer. (Plan covers: Counts provider-side UPI transactions by final status (success, failed, returned) initiated on 20 and 21 June 2026, since the provider's final status decides the outcome.)
3 rows (columns: psp_status, transactions, amount_inr):
  success | 614 | 370277.27999999997
  failed | 38 | 21919.46
  returned | 1 | 193.11
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.initiated_ts between 2026-06-20 and 2026-06-21; group by psp upi report.status; report psp_status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr; sorted by transactions desc.
Part 4: answered from the schema layer. (Plan covers: Lists debit complaints raised on 20 and 21 June 2026 by kind and resolution, the recorded evidence for debits that were charged twice or had a failed till debit.)
kind = charged twice; resolution = refunded after the store matched the credit by hand; complaints = 1; amount_inr = 963.27
  How it was found: From complaint records; keep rows where customer complaints.complaint_ts between 2026-06-20 and 2026-06-21; group by customer complaints.kind, customer complaints.resolution; report kind = customer complaints.kind, resolution = customer complaints.resolution, complaints = count of *, amount_inr = sum of customer complaints.amount_inr; sorted by complaints desc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S8N34: How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?

Part 1: answered from the ontology layer. (Plan covers: For each 'charged twice' complaint, the wait for the money from the extra debit (provider success initiated_ts to resolved_ts) and from the complaint (complaint_ts to resolved_ts), per Rule 11 the clock starts at the extra debit.)
54 rows (columns: bill_id, rrn, extra_debit_ts, complaint_ts, wait_from_extra_debit_hours, wait_from_complaint_hours, resolution, resolved_ts):
  B260605-120088 | 615619003319 | 2026-06-05T19:58:33 | 2026-06-06T13:00:00 | -65.02416666224599 | -48.0 | refunded after the store matched the credit by hand | 2026-06-08T13:00:00
  B260605-120088 | 615619003319 | 2026-06-05T19:58:33 | 2026-06-06T13:00:00 | -65.02416666224599 | -48.0 | refunded after the store matched the credit by hand | 2026-06-08T13:00:00
  B260618-110082 | 616918011772 | 2026-06-18T18:43:56 | 2026-06-20T11:00:00 | -88.26777778565884 | -48.0 | refunded after the store matched the credit by hand | 2026-06-22T11:00:00
  B260618-110082 | 616918011772 | 2026-06-18T18:43:56 | 2026-06-20T11:00:00 | -88.26777778565884 | -48.0 | refunded after the store matched the credit by hand | 2026-06-22T11:00:00
  B260620-120019 | 617119013363 | 2026-06-20T19:11:36 | 2026-06-22T18:00:00 | -94.80666666850448 | -48.0 | refunded after the store matched the credit by hand | 2026-06-24T18:00:00
  B260620-120019 | 617119013363 | 2026-06-20T19:11:36 | 2026-06-22T18:00:00 | -94.80666666850448 | -48.0 | refunded after the store matched the credit by hand | 2026-06-24T18:00:00
  B260620-120047 | 617119013379 | 2026-06-20T19:29:31 | 2026-06-22T19:00:00 | -95.50805555284023 | -48.0 | refunded after the store matched the credit by hand | 2026-06-24T19:00:00
  B260620-120047 | 617119013379 | 2026-06-20T19:29:31 | 2026-06-22T19:00:00 | -95.50805555284023 | -48.0 | refunded after the store matched the credit by hand | 2026-06-24T19:00:00
  B260614-100001 | 616517008996 | 2026-06-14T17:00:31 | 2026-06-15T19:00:00 | -97.99138888344169 | -72.0 | refunded after the store matched the credit by hand | 2026-06-18T19:00:00
  B260614-100001 | 616517008996 | 2026-06-14T17:00:31 | 2026-06-15T19:00:00 | -97.99138888344169 | -72.0 | refunded after the store matched the credit by hand | 2026-06-18T19:00:00
  ... and 44 more
  How it was found: From complaint records; inner-join payment attempt records on customer complaints.bill_id = pos payments.bill_id; inner-join UPI service provider's transaction records on customer complaints.rrn = psp upi report.rrn; keep rows where customer complaints.kind = 'charged twice' and psp upi report.status = 'success'; report bill_id = customer complaints.bill_id, rrn = customer complaints.rrn, extra_debit_ts = psp upi report.initiated_ts, complaint_ts = customer complaints.complaint_ts, wait_from_extra_debit_hours = hours_between(psp upi report.initiated_ts, customer complaints.resolved_ts), wait_from_complaint_hours = hours_between(customer complaints.complaint_ts, customer complaints.resolved_ts), resolution = customer complaints.resolution, resolved_ts = customer complaints.resolved_ts; sorted by wait_from_extra_debit_hours desc.
Part 2: answered from the ontology layer. (Plan covers: The 'charged twice' complaints with no resolved_ts, i.e. still unrefunded at month end, counted per complaint row (a bill is the stand-in for a shopper).)
No rows matched.
  How it was found: From complaint records; inner-join payment attempt records on customer complaints.bill_id = pos payments.bill_id; inner-join UPI service provider's transaction records on customer complaints.rrn = psp upi report.rrn; keep rows where customer complaints.kind = 'charged twice' and psp upi report.status = 'success' and customer complaints.resolved_ts is empty; report bill_id = customer complaints.bill_id, rrn = customer complaints.rrn, complaint_ts = customer complaints.complaint_ts, amount_inr = customer complaints.amount_inr; sorted by complaint_ts asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N35: Was the store's UPI technical decline rate acceptable in June?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"op": "=", "args": [{"col": "pos-payments-june.till_status"}, {"lit": "failed:  is not in the plan form).

## S8N36: Which customers (by RRN) should the store refund now, without waiting for a complaint?

Part 1: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 2: answered from the ontology layer. (Plan covers: Flags bills with more than one approved till payment, the 'charged twice' pattern that should be refunded now (one bill, one payment; Rule 10).)
No rows matched.
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.till_status = 'approved' and psp upi report.status = 'success'; group by pos payments.bill_id; keep groups where approved_payment_count > 1; report bill_id = pos payments.bill_id, approved_payment_count = count of pos payments.attempt; sorted by bill_id asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N37: At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?

I can't answer this from Store 014's records: the plan has no valid parts.

## S8N38: Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N01: Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?

Part 1: answered from the ontology layer. (Plan covers: Checks the premise that 5 kg atta sales dropped 59% in the week of 8 June by listing daily units sold and revenue for ATTA-WW-5KG from 2026-06-08 to 2026-06-14.)
7 rows (columns: day, units_sold, revenue_inr):
  2026-06-08 | 9.0 | 2385.0
  2026-06-09 | 11.0 | 2915.0
  2026-06-10 | 22.0 | 5830.0
  2026-06-11 | 1.0 | 265.0
  2026-06-12 | 0.0 | 0.0
  2026-06-13 | 22.0 | 5830.0
  2026-06-14 | 23.0 | 6095.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) between 2026-06-08 and 2026-06-14; group by day(daily sales.date); report day = day(daily sales.date), units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr; sorted by day asc.
Part 2: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 3: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 4: answered from the ontology layer. (Plan covers: Provides the recorded 5 kg versus 1 kg atta sales (units and revenue) for the week of 8 June that a shelf-space reallocation would be sized from; shelf space itself is not recorded, so no reallocation quantity can be derived.)
2 rows (columns: sku, units_sold, revenue_inr):
  ATTA-WW-1KG | 207.0 | 12006.0
  ATTA-WW-5KG | 88.0 | 23320.0
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-5KG', 'ATTA-WW-1KG'] and day(daily sales.date) between 2026-06-08 and 2026-06-14; group by daily sales.sku; report sku = daily sales.sku, units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr; sorted by sku asc.

## S9N02: Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N03: How many bags of 5 kg atta were sold in June 2023?

I can't answer this from Store 014's records: the ontology layer refused the plan (the question names 2023 but the plan has no date in that year and the records are not from that year).
Not recorded: year outside 2026

## S9N04: Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?

Part 1: not answered: ecords: the ontology layer refused the plan (column forecast_units_per_day is not additive and cannot be summed).
Part 2: answered from the schema layer. (Plan covers: Recorded sales units for 5 kg atta in June 2026-06-01 to 2026-06-28, used as the stand-in for demand because demand itself is not recorded.)
recorded_sales_units = 567.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-28; report recorded_sales_units = sum of daily sales.units_sold.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S9N05: Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?

Part 1: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 2: answered from the ontology layer. (Plan covers: Checks whether any 5 kg atta till lines were sold on the afternoon of 2026-06-11 (14:00 hour), using till lines as the record of sales.)
No rows matched.
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-11' and hour(pos lines may.bill_ts) = 14; group by pos lines may.sku_scanned; report units_sold_afternoon = sum of pos lines may.qty, line_count = count of pos lines may.line.
Part 3: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).

## S9N06: Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N07: If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?

Part 1: answered from the ontology layer. (Plan covers: Till records of bills containing toned milk (MILK-TONED-500ML) in June 2026, with units per bill, as the recorded-sales stand-in for demand met by sales.)
200 rows (columns: bill_id, toned_milk_units):
  B260601-000007 | 2.0
  B260601-000011 | 1.0
  B260601-000014 | 1.0
  B260601-000024 | 1.0
  B260601-000038 | 2.0
  B260601-000042 | 1.0
  B260601-000048 | 1.0
  B260601-000049 | 1.0
  B260601-000053 | 1.0
  B260601-000055 | 1.0
  ... and 190 more
  How it was found: From till line records; inner-join product records on pos lines may.sku_scanned = products.sku; keep rows where products.sku = 'MILK-TONED-500ML' and pos lines may.bill_ts between 2026-06-01T00:00 and 2026-06-28T23:59; group by pos lines may.bill_id; keep groups where toned_milk_units > 0; report bill_id = pos lines may.bill_id, toned_milk_units = sum of pos lines may.qty; sorted by bill_id asc.
Part 2: answered from the ontology layer. (Plan covers: Recorded toned-milk write-off units in June 2026, the waste side of the stated margin premise.)
wasted_units = 295.0
  How it was found: From write-off records; inner-join product records on write offs.sku = products.sku; keep rows where products.sku = 'MILK-TONED-500ML' and write offs.date between 2026-06-01T00:00 and 2026-06-28T23:59; group by write offs.sku; report wasted_units = sum of write offs.units; sorted by wasted_units desc.
Part 3: answered from the ontology layer. (Plan covers: Toned-milk forecast and standing-order parameters (forecast units per day, ordered units, on order, order-up-to, reorder point, book on hand, sigma) for June 2026, to size a 5% cut in the standing order.)
No rows matched.
  How it was found: From forecast row records; inner-join product records on forecasts.sku = products.sku; keep rows where products.sku = 'MILK-TONED-500ML' and forecasts.date between 2026-06-01T00:00 and 2026-06-28T23:59; group by forecasts.sku; report forecast_units_per_day = avg of forecasts.forecast_units_per_day, ordered_units = sum of forecasts.ordered_units, on_order = max of forecasts.on_order, order_up_to = max of forecasts.order_up_to, reorder_point = max of forecasts.reorder_point, book_on_hand = max of forecasts.book_on_hand, sigma = max of forecasts.sigma; sorted by forecast_units_per_day desc.
Stand-ins used (not the real thing): list_margin (else): selling price minus the single cost per product is a list margin, not a real margin

## S9N08: Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N09: Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?

Part 1: answered from the ontology layer. (Plan covers: June atta warehouse stock corrections by SKU and reason, showing the net value at cost (sum of value at cost with its sign) alongside the gross value at cost (sum of absolute values) and the units/cases moved, so a small net does not hide l)
2 rows (columns: sku, reason, adjustment_rows, net_value_at_cost_inr, gross_value_at_cost_inr, net_units, net_cases):
  ATTA-WW-5KG | cycle count variance | 1 | 14592.0 | 14592.0 | 64.0 | 16.0
  ATTA-WW-1KG | short pick: slot count variance | 1 | -7920.0 | 7920.0 | -160.0 | -16.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; keep rows where dc stock adjustments.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; group by dc stock adjustments.sku, dc stock adjustments.reason; report sku = dc stock adjustments.sku, reason = dc stock adjustments.reason, adjustment_rows = count of *, net_value_at_cost_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_at_cost_inr = sum of abs(dc stock adjustments.value_at_cost_inr), net_units = sum of dc stock adjustments.units, net_cases = sum of dc stock adjustments.cases; sorted by gross_value_at_cost_inr desc.
Part 2: answered from the schema layer. (Plan covers: June atta store hand-count adjustments by SKU and trigger, showing store-side corrections that accompany the warehouse corrections (store count adjustments are in stock-counts, warehouse corrections in dc-stock-adjustments).)
6 rows (columns: sku, trigger, count_rows, net_adjustment_packs):
  ATTA-WW-1KG | manager request after complaints | 1 | 157.0
  ATTA-WW-10KG | scheduled full count | 2 | 1.0
  ATTA-WW-10KG | manager request after complaints | 1 | -1.0
  ATTA-WW-5KG | scheduled full count | 2 | -1.0
  ATTA-WW-1KG | scheduled full count | 2 | -4.0
  ATTA-WW-5KG | manager request after complaints | 1 | -63.0
  How it was found: From stock count records; keep rows where stock counts.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; group by stock counts.sku, stock counts.trigger; report sku = stock counts.sku, trigger = stock counts.trigger, count_rows = count of *, net_adjustment_packs = sum of stock counts.adjustment; sorted by net_adjustment_packs desc.
Part 3: answered from the schema layer. (Plan covers: June atta write-offs by SKU and reason (damaged/expired), the recorded waste side that accompanies stock corrections.)
sku = ATTA-WW-5KG; reason = damaged; writeoff_rows = 3; units_written_off = 3.0
  How it was found: From write-off records; keep rows where write offs.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; group by write offs.sku, write offs.reason; report sku = write offs.sku, reason = write offs.reason, writeoff_rows = count of *, units_written_off = sum of write offs.units; sorted by units_written_off desc.
Part 4: not answered: ecords: the schema layer refused the plan (node {"op": "=", "args": [{"col": "shelf-audits-june.status"}, {"lit": "on shelf"}]} is not in the plan form).
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N10: Which pallet on the 22 June shipment failed its dispatch weight check?

answered from the ontology layer. (Plan covers: Identifies the pallet(s) on the shipment dispatched on 2026-06-22 whose weight_check is 'not weighed', using the pallet label (SSCC) as the pallet identifier.)
2 rows (columns: sscc, shipment_id, cases, notice_kg, weight_check):
  029000010000010542 | SHP-260622 | 39.0 | 723.7 | not weighed
  029000010000010559 | SHP-260622 | 5.0 | 73.5 | not weighed
  How it was found: From pallet records; inner-join shipment records on pallets.shipment_id = shipments.shipment_id; keep rows where day(shipments.dispatched_ts) = '2026-06-22' and pallets.weight_check = 'not weighed'; report sscc = pallets.sscc, shipment_id = pallets.shipment_id, cases = pallets.cases, notice_kg = pallets.notice_kg, weight_check = pallets.weight_check; sorted by sscc asc.

## S9N11: If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?

I can't answer this from Store 014's records: no usable plan was returned.

## S9N12: What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"op": "and", "args": [{"op": ">=", "args": [{"col": "shipments-june.arrived_ts" is not in the plan form).

## S9N13: Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?

Part 1: not answered: ecords: the schema layer refused the plan (table 'pos-payments-jone' is not in this plan's from or joins).
Part 2: answered from the schema layer. (Plan covers: Counts recorded complaints by kind (including 'charged twice') and their rupee amounts, the only recorded evidence of double charges; a complaint is not proof of a charge and no customer identity exists.)
2 rows (columns: kind, complaints, complaint_amount_inr):
  charged twice | 23 | 11301.86
  debited but the till said failed | 3 | 667.3
  How it was found: From complaint records; group by customer complaints.kind; report kind = customer complaints.kind, complaints = count of *, complaint_amount_inr = sum of customer complaints.amount_inr; sorted by complaints desc.

## S9N14: Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.

answered from the ontology layer. (Plan covers: Reports the provider's final status for each June UPI till timeout, joined to the provider report by RRN (Rule 9: the provider's final status decides).)
No rows matched.
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.till_status = 'failed: no response' and pos payments.tender = 'UPI'; report rrn = pos payments.rrn, bill_id = pos payments.bill_id, attempt_ts = pos payments.ts, amount_inr = pos payments.amount_inr, final_bank_status = psp upi report.status, status_ts = psp upi report.status_ts; sorted by attempt_ts asc.

## S9N15: Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?

Part 1: answered from the schema layer. (Plan covers: Counts June UPI payment attempts by till status (approved, declined, failed, failed: no response) to check the stated 0.76% decline rate and identify reliability incidents at the till.)
4 rows (columns: attempts, amount_inr):
  17604 | 10331142.02
  552 | 281904.11
  139 | 83542.91
  47 | 22178.77
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.ts between 2026-06-01 and 2026-06-28; group by pos payments.till_status; report attempts = count of *, amount_inr = sum of pos payments.amount_inr; sorted by attempts desc.
Part 2: answered from the schema layer. (Plan covers: Counts June UPI transactions by the provider's final status (success, failed, returned), which per Rule 9 decides the outcome of each UPI request.)
3 rows (columns: transactions, amount_inr):
  17630 | 10344508.08
  706 | 372602.9
  6 | 1656.83
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.initiated_ts between 2026-06-01 and 2026-06-28; group by psp upi report.status; report transactions = count of *, amount_inr = sum of psp upi report.amount_inr; sorted by transactions desc.
Part 3: answered from the ontology layer. (Plan covers: Cross-checks each June UPI till attempt against the provider's final status by RRN, showing where the till and the provider disagree (e.g. till 'failed: no response' with no RRN, or provider success with no approved till payment).)
4 rows (columns: attempts, amount_inr):
  17604 | 10331142.02
  552 | 281904.11
  139 | 83542.91
  47 | 22178.77
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and pos payments.ts between 2026-06-01 and 2026-06-28; group by pos payments.till_status, psp upi report.status; report attempts = count of *, amount_inr = sum of pos payments.amount_inr; sorted by attempts desc.

## S9N16: Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?

Part 1: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 2: answered from the schema layer. (Plan covers: Counts the till's UPI payment attempts on 20–21 June 2026 by till_status, the till witness to whether those credits were approved, declined, failed or timed out.)
4 rows (columns: till_status, attempts, amount_inr):
  approved | 597 | 362451.59
  failed: no response | 29 | 14253.82
  declined | 20 | 9647.18
  failed | 7 | 6037.26
  How it was found: From payment attempt records; keep rows where pos payments.ts between 2026-06-20 and 2026-06-21 and pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *, amount_inr = sum of pos payments.amount_inr; sorted by attempts desc.
Part 3: answered from the schema layer. (Plan covers: Counts the provider's final UPI statuses for transactions initiated on 20–21 June 2026, the provider witness that decides whether a till timeout was actually paid.)
3 rows (columns: status, transactions, amount_inr):
  success | 614 | 370277.27999999997
  failed | 38 | 21919.46
  returned | 1 | 193.11
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.initiated_ts between 2026-06-20 and 2026-06-21; group by psp upi report.status; report status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr; sorted by transactions desc.
Part 4: answered from the schema layer. (Plan covers: Lists debit complaints raised on 20–21 June 2026 by kind and resolution, the recorded evidence for debits that may need a refund before the money can be recognized.)
kind = charged twice; resolution = refunded after the store matched the credit by hand; complaints = 1; amount_inr = 963.27
  How it was found: From complaint records; keep rows where customer complaints.complaint_ts between 2026-06-20 and 2026-06-21; group by customer complaints.kind, customer complaints.resolution; report kind = customer complaints.kind, resolution = customer complaints.resolution, complaints = count of *, amount_inr = sum of customer complaints.amount_inr; sorted by complaints desc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N17: Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?

Part 1: answered from the ontology layer. (Plan covers: Each June refund's turnaround in days from requested_ts to completed_ts, so the 5-day RBI turnaround can be checked per refund (the clock starts at the extra debit per Rule 11, approximated here by the refund request time).)
23 rows (columns: refund_id, bill_id, rrn, requested_ts, completed_ts, turnaround_days):
  RF-003319 | B260605-120088 | 615619003319 | 2026-06-06T13:00:00 | 2026-06-08T13:00:00 | -2.0
  RF-011772 | B260618-110082 | 616918011772 | 2026-06-20T11:00:00 | 2026-06-22T11:00:00 | -2.0
  RF-013318 | B260620-110022 | 617118013318 | 2026-06-23T17:00:00 | 2026-06-25T17:00:00 | -2.0
  RF-013342 | B260620-110055 | 617118013342 | 2026-06-23T10:00:00 | 2026-06-25T10:00:00 | -2.0
  RF-013343 | B260620-110055 | 617118013343 | 2026-06-24T10:00:00 | 2026-06-26T10:00:00 | -2.0
  RF-013363 | B260620-120019 | 617119013363 | 2026-06-22T18:00:00 | 2026-06-24T18:00:00 | -2.0
  RF-013379 | B260620-120047 | 617119013379 | 2026-06-22T19:00:00 | 2026-06-24T19:00:00 | -2.0
  RF-008996 | B260614-100001 | 616517008996 | 2026-06-15T19:00:00 | 2026-06-18T19:00:00 | -3.0
  RF-013351 | B260620-120002 | 617119013351 | 2026-06-24T10:00:00 | 2026-06-27T10:00:00 | -3.0
  RF-013361 | B260620-120016 | 617119013361 | 2026-06-23T12:00:00 | 2026-06-26T12:00:00 | -3.0
  ... and 13 more
  How it was found: From UPI refund records; keep rows where upi refunds.requested_ts between 2026-06-01 and 2026-06-30; report refund_id = upi refunds.refund_id, bill_id = upi refunds.bill_id, rrn = upi refunds.rrn, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, turnaround_days = days_between(upi refunds.requested_ts, upi refunds.completed_ts); sorted by turnaround_days desc.
Part 2: answered from the ontology layer. (Plan covers: The recorded median wait across June refunds, computed as the average of the per-refund turnaround days, to check the stated premise of a 3-day median.)
median_turnaround_days = -3.217391304347826
  How it was found: From UPI refund records; keep rows where upi refunds.requested_ts between 2026-06-01 and 2026-06-30; report median_turnaround_days = avg of days_between(upi refunds.requested_ts, upi refunds.completed_ts).
