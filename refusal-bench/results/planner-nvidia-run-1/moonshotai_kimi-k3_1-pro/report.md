## S8N01: How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?

Part 1: not answered: ecords: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Part 2: answered from the schema layer. (Plan covers: Bags of 5 kg atta sold in the week of 8 June 2026 (8-14 June), using recorded till sales (daily-sales) as units sold.)
bags_sold_week_8_june = 79.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-08T00:00 and 2026-06-14T23:59; report bags_sold_week_8_june = sum of daily sales.units_sold.

## S8N02: Which shelf audits found an item empty while the hourly book showed stock above zero?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8N03: On which days did any item's closing book stock go below zero?

answered from the ontology layer. (Plan covers: Days when any item's closing book stock was below zero, using inventory-book closing book stock in packs.)
6 rows (columns: day, items_below_zero, lowest_closing_book_stock_packs):
  2026-06-02 | 1 | -5.0
  2026-06-09 | 1 | -5.0
  2026-06-11 | 1 | -15.0
  2026-06-12 | 1 | -12.0
  2026-06-13 | 1 | -14.0
  2026-06-20 | 1 | -13.0
  How it was found: From book-stock row records; keep rows where inventory book.book_on_hand_close < 0; group by day(inventory book.date); report day = day(inventory book.date), items_below_zero = count distinct of inventory book.sku, lowest_closing_book_stock_packs = min of inventory book.book_on_hand_close; sorted by day asc.

## S8N04: Which stock counts disagreed with the book stock by more than 2%?

answered from the ontology layer. (Plan covers: Store stock counts whose hand count differed from book_before by more than 2% of book stock, using stock-counts-june (store count adjustments) rather than warehouse corrections.)
19 rows (columns: count_ts, sku, book_before, counted, adjustment, trigger, pct_disagreement):
  2026-06-01T05:45 | ATTA-WW-1KG | 92.0 | 87.0 | -5.0 | scheduled full count | -5.434782608695652
  2026-06-01T05:45 | ATTA-WW-10KG | 28.0 | 29.0 | 1.0 | scheduled full count | 3.571428571428571
  2026-06-01T05:45 | RICE-SM-5KG | 66.0 | 64.0 | -2.0 | scheduled full count | -3.0303030303030303
  2026-06-01T05:45 | DAL-TOOR-1KG | 15.0 | 13.0 | -2.0 | scheduled full count | -13.333333333333334
  2026-06-01T05:45 | OIL-SUN-1L | 82.0 | 77.0 | -5.0 | scheduled full count | -6.097560975609756
  2026-06-01T05:45 | SUGAR-1KG | 46.0 | 44.0 | -2.0 | scheduled full count | -4.3478260869565215
  2026-06-01T05:45 | MILK-TONED-500ML | 377.0 | 351.0 | -26.0 | scheduled full count | -6.896551724137931
  2026-06-01T05:45 | MILK-FC-500ML | 94.0 | 109.0 | 15.0 | scheduled full count | 15.957446808510639
  2026-06-01T05:45 | CURD-500G | 115.0 | 112.0 | -3.0 | scheduled full count | -2.608695652173913
  2026-06-01T05:45 | BREAD-WHITE-400G | 64.0 | 59.0 | -5.0 | scheduled full count | -7.8125
  ... and 9 more
  How it was found: From stock count records; keep rows where abs(stock counts.counted - stock counts.book_before) / stock counts.book_before > 0.02; report count_ts = stock counts.count_ts, sku = stock counts.sku, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment, trigger = stock counts.trigger, pct_disagreement = stock counts.counted - stock counts.book_before / stock counts.book_before * 100; sorted by count_ts asc.

## S8N05: Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?

I can't answer this from Store 014's records: the ontology layer refused the plan ('between' needs arg, low, high).

## S8N06: What time did toned milk record its last sale each day, and how many pouches were written off?

Part 1: answered from the ontology layer. (Plan covers: For toned milk (MILK-TONED-500ML), the last recorded sale time each June day, using till lines as sales.)
28 rows (columns: sale_date, last_sale_time):
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
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'MILK-TONED-500ML' and pos lines may.bill_ts >= '2026-06-01T00:00' and pos lines may.bill_ts <= '2026-06-28T23:59'; group by day(pos lines may.bill_ts); report sale_date = day(pos lines may.bill_ts), last_sale_time = max of pos lines may.bill_ts; sorted by sale_date asc.
Part 2: answered from the schema layer. (Plan covers: Total toned milk pouches written off in June, summing write-off units for MILK-TONED-500ML.)
pouches_written_off = 296.0
  How it was found: From write-off records; keep rows where write offs.sku = 'MILK-TONED-500ML'; report pouches_written_off = sum of write offs.units.

## S8N07: Why did 5 kg atta sales fall in the week of 8 June?

I can't answer this from Store 014's records: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N08: Was 5 kg atta in stock on Thursday 11 June?

Part 1: answered from the ontology layer. (Plan covers: On-shelf availability on 2026-06-11 is the 11:00 shelf audit status for ATTA-WW-5KG; book stock is only a belief.)
No rows matched.
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) = '2026-06-11'; report audit_ts = shelf audits.audit_ts, shelf_status = shelf audits.status.
Part 2: answered from the ontology layer. (Plan covers: Closing book stock on 2026-06-11 is supporting evidence only, not proof the product was on the shelf.)
date = 2026-06-11; book_on_hand_close = 55.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) = '2026-06-11'; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close.

## S8N09: Are shoppers switching from 5 kg to 1 kg atta?

Part 1: answered from the ontology layer. (Plan covers: Daily recorded sales of 5 kg and 1 kg atta, to check whether their sales trends are consistent with switching; sales are till lines/daily sales, not shopper behaviour.)
56 rows (columns: sku, day, units_sold, revenue_inr):
  ATTA-WW-1KG | 2026-06-01 | 22.0 | 1276.0
  ATTA-WW-1KG | 2026-06-02 | 35.0 | 2030.0
  ATTA-WW-1KG | 2026-06-03 | 41.0 | 2378.0
  ATTA-WW-1KG | 2026-06-04 | 24.0 | 1392.0
  ATTA-WW-1KG | 2026-06-05 | 24.0 | 1392.0
  ATTA-WW-1KG | 2026-06-06 | 52.0 | 3016.0
  ATTA-WW-1KG | 2026-06-07 | 40.0 | 2320.0
  ATTA-WW-1KG | 2026-06-08 | 27.0 | 1566.0
  ATTA-WW-1KG | 2026-06-09 | 24.0 | 1392.0
  ATTA-WW-1KG | 2026-06-10 | 41.0 | 2378.0
  ... and 46 more
  How it was found: From daily sales row records; keep rows where daily sales.sku in ['ATTA-WW-5KG', 'ATTA-WW-1KG']; group by daily sales.sku, day(daily sales.date); report sku = daily sales.sku, day = day(daily sales.date), units_sold = sum of daily sales.units_sold, revenue_inr = sum of daily sales.revenue_inr; sorted by sku asc, day asc.
Part 2: not answered: ecords: the schema layer refused the plan (node {"op": "=", "args": [{"col": "shelf-audits-june.status"}, {"lit": "on shelf"}]} is not in the plan form).

## S8N10: What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?

Part 1: not answered: ecords: the schema layer refused the plan (node {"op": "=", "args": [{"col": "shelf-audits-june.status"}, {"lit": "on shelf"}]} is not in the plan form).
Part 2: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 3: answered from the ontology layer. (Plan covers: Daily June till-line sales for ATTA-WW-5KG provide the sales evidence to compare with book stock and shelf audits; sales are not demand or availability.)
24 rows (columns: day, units_sold, sales_value_inr):
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
  ... and 14 more
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and pos lines may.bill_ts between 2026-06-01T00:00 and 2026-06-30T23:59; group by day(pos lines may.bill_ts); report day = day(pos lines may.bill_ts), units_sold = sum of pos lines may.qty, sales_value_inr = sum of pos lines may.line_amount; sorted by day asc.

## S8N11: What has daily demand for 5 kg atta been in June so far?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: needs a longer period than the records cover

## S8N12: How many shoppers left without 5 kg atta, and what were the lost sales in June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8E13: How many of June's deliveries arrived inside their 06:00–06:30 slot?

answered from the ontology layer. (Plan covers: Counts June shipments whose booked slot is 06:00–06:30 and that arrived on time, using the definition arrived_ts between slot_start and slot_end.)
deliveries_in_slot = 23
  How it was found: From shipment records; keep rows where shipments.arrived_ts between 2026-06-01T00:00 and 2026-06-28T23:59 and hour(shipments.slot_start) = 6 and hour(shipments.slot_end) = 6 and shipments.arrived_ts >= shipments.slot_start and shipments.arrived_ts <= shipments.slot_end; report deliveries_in_slot = count of *.

## S8N14: How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8N15: What was the case fill rate across June's store orders according to the shipping notices?

answered from the ontology layer. (Plan covers: Case fill rate across June's store orders: total shipping-notice cases divided by total ordered cases, matched by order and SKU.)
cases_ordered = 689.0; cases_shipped = 686.0; case_fill_rate = 0.9956458635703919
  How it was found: From store order line records; left-join shipping-notice line records on store orders.order_id = shipping notice lines.order_id and store orders.sku = shipping notice lines.sku; keep rows where store orders.created_ts between 2026-06-01T00:00 and 2026-06-30T23:59; report cases_ordered = sum of store orders.cases, cases_shipped = sum of shipping notice lines.cases, case_fill_rate = sum of shipping notice lines.cases / sum of store orders.cases.

## S8N16: What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?

Part 1: answered from the ontology layer. (Plan covers: Warehouse atta corrections: net is the sum of signed value at cost and gross is the sum of absolute values.)
net_value_at_cost_inr = 6672.0; gross_value_at_cost_inr = 22512.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; inner-join product records on dc stock adjustments.sku = products.sku; keep rows where dc stock adjustments.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; report net_value_at_cost_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_at_cost_inr = sum of abs(dc stock adjustments.value_at_cost_inr).
Part 2: answered from the ontology layer. (Plan covers: Store atta count adjustments: net is the sum of signed adjustments times product cost and gross is the sum of absolute adjustments times product cost.)
net_value_at_cost_inr = -7018.5; gross_value_at_cost_inr = 23522.5
  How it was found: From stock count records; inner-join product records on stock counts.sku = products.sku; keep rows where stock counts.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; report net_value_at_cost_inr = sum of stock counts.adjustment * products.cost_inr, gross_value_at_cost_inr = sum of abs(stock counts.adjustment) * products.cost_inr.

## S8N17: Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8N18: Which goods receipts did not survive the next stock count within a week?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8N19: Was the 22 June delivery on time and in full?

Part 1: not answered: ecords: the schema layer refused the plan (node {"op": "between", "arg": {"col": "shipments-june.arrived_ts"}, "low": {"col": "s is not in the plan form).
Part 2: answered from the ontology layer. (Plan covers: In full per delivery: shipping-notice cases against ordered cases for the 22 June 2026 shipment, using the notice-to-order fill-rate definition.)
shipment_id = SHP-260622; notice_cases = 44.0; ordered_cases = 44.0
  How it was found: From shipping-notice line records; inner-join shipment records on shipping notice lines.shipment_id = shipments.shipment_id; left-join store order line records on shipping notice lines.order_id = store orders.order_id and shipping notice lines.sku = store orders.sku; keep rows where day(shipments.arrived_ts) = '2026-06-22'; group by shipments.shipment_id; report shipment_id = shipments.shipment_id, notice_cases = sum of shipping notice lines.cases, ordered_cases = sum of store orders.cases.

## S8N20: What was Store 014's OTIF from the warehouse in June?

answered from the ontology layer. (Plan covers: Per-delivery OTIF for June warehouse shipments: on time means arrived_ts between slot_start and slot_end, and in full means shipping-notice cases equal ordered cases; each shipment's evidence is returned for the OTIF share.)
25 rows (columns: shipment_id, arrived_ts, slot_start, slot_end, notice_cases, ordered_cases):
  SHP-260601 | 2026-06-01T06:20 | 2026-06-01T06:00 | 2026-06-01T06:30 | 18.0 | 
  SHP-260602 | 2026-06-02T06:00 | 2026-06-02T06:00 | 2026-06-02T06:30 | 5.0 | 5.0
  SHP-260603 | 2026-06-03T06:16 | 2026-06-03T06:00 | 2026-06-03T06:30 | 63.0 | 63.0
  SHP-260604 | 2026-06-04T06:00 | 2026-06-04T06:00 | 2026-06-04T06:30 | 7.0 | 7.0
  SHP-260605 | 2026-06-05T06:21 | 2026-06-05T06:00 | 2026-06-05T06:30 | 25.0 | 25.0
  SHP-260606 | 2026-06-06T06:12 | 2026-06-06T06:00 | 2026-06-06T06:30 | 50.0 | 50.0
  SHP-260607 | 2026-06-07T06:10 | 2026-06-07T06:00 | 2026-06-07T06:30 | 23.0 | 23.0
  SHP-260608 | 2026-06-08T06:06 | 2026-06-08T06:00 | 2026-06-08T06:30 | 45.0 | 45.0
  SHP-260609 | 2026-06-09T06:17 | 2026-06-09T06:00 | 2026-06-09T06:30 | 26.0 | 26.0
  SHP-260611 | 2026-06-11T08:21 | 2026-06-11T06:00 | 2026-06-11T06:30 | 38.0 | 39.0
  ... and 15 more
  How it was found: From shipment records; left-join shipping-notice line records on shipments.shipment_id = shipping notice lines.shipment_id; left-join store order line records on shipping notice lines.order_id = store orders.order_id and shipping notice lines.sku = store orders.sku; keep rows where shipments.arrived_ts between 2026-06-01T00:00 and 2026-06-28T23:59; group by shipments.shipment_id, shipments.arrived_ts, shipments.slot_start, shipments.slot_end; report shipment_id = shipments.shipment_id, arrived_ts = shipments.arrived_ts, slot_start = shipments.slot_start, slot_end = shipments.slot_end, notice_cases = sum of shipping notice lines.cases, ordered_cases = sum of store orders.cases; sorted by shipment_id asc.

## S8N21: Why was 5 kg atta off the shelf from 23 to 26 June?

Part 1: answered from the ontology layer. (Plan covers: Checks the 11:00 shelf audits for 5 kg atta on 23–26 June; on-shelf availability is the share of audits with status 'on shelf'.)
2 rows (columns: audit_ts, status):
  2026-06-23T11:00 | on shelf
  2026-06-26T11:00 | empty
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) between 2026-06-23 and 2026-06-26; report audit_ts = shelf audits.audit_ts, status = shelf audits.status; sorted by audit_ts asc.
Part 2: answered from the ontology layer. (Plan covers: Shows the book stock belief for 5 kg atta on 23–26 June, since book stock is not the shelf and silence with stock on the books means the shelf should be checked.)
4 rows (columns: date, book_on_hand_close):
  2026-06-23 | 63.0
  2026-06-24 | 63.0
  2026-06-25 | 63.0
  2026-06-26 | 0.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) between 2026-06-23 and 2026-06-26; report date = inventory book.date, book_on_hand_close = inventory book.book_on_hand_close; sorted by date asc.
Part 3: answered from the ontology layer. (Plan covers: Shows recorded till sales of 5 kg atta on 23–26 June; sales are not demand and no-sales silence is a question, not a cause.)
4 rows (columns: date, units_sold, revenue_inr):
  2026-06-23 | 5.0 | 1325.0
  2026-06-24 | 0.0 | 0.0
  2026-06-25 | 0.0 | 0.0
  2026-06-26 | 0.0 | 0.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) between 2026-06-23 and 2026-06-26; report date = daily sales.date, units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr; sorted by date asc.
Part 4: answered from the ontology layer. (Plan covers: Lists back-door receipts of 5 kg atta on 23–26 June as the nearest recorded supply evidence; shelf restock times and the actual cause of the empty shelf are not recorded.)
No rows matched.
  How it was found: From goods-receipt line records; keep rows where goods receipts.sku_booked = 'ATTA-WW-5KG' and day(goods receipts.received_ts) between 2026-06-23 and 2026-06-26; report received_ts = goods receipts.received_ts, units_booked = goods receipts.units_booked, shipment_id = goods receipts.shipment_id; sorted by received_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S8N22: Is the 5 kg atta missing at the store theft?

Part 1: answered from the schema layer. (Plan covers: Physical stock counts for 5 kg atta show book-versus-counted gaps, but no table records the cause of a gap, so theft cannot be established.)
3 rows (columns: count_ts, trigger, book_before, counted, adjustment):
  2026-06-01T05:45 | scheduled full count | 36.0 | 36.0 | 0.0
  2026-06-26T09:00 | manager request after complaints | 63.0 | 0.0 | -63.0
  2026-06-28T22:30 | scheduled full count | 63.0 | 62.0 | -1.0
  How it was found: From stock count records; keep rows where stock counts.sku = 'ATTA-WW-5KG'; report count_ts = stock counts.count_ts, trigger = stock counts.trigger, book_before = stock counts.book_before, counted = stock counts.counted, adjustment = stock counts.adjustment; sorted by count_ts asc.
Part 2: answered from the schema layer. (Plan covers: Shelf audits show when 5 kg atta was recorded empty versus on shelf, which is the recorded evidence of it missing at the store.)
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
Part 3: answered from the schema layer. (Plan covers: Recorded write-offs for 5 kg atta show stock removed for damaged or expired reasons, which are recorded reasons rather than theft.)
3 rows (columns: date, reason, units):
  2026-06-09 | damaged | 1.0
  2026-06-19 | damaged | 1.0
  2026-06-22 | damaged | 1.0
  How it was found: From write-off records; keep rows where write offs.sku = 'ATTA-WW-5KG'; report date = write offs.date, reason = write offs.reason, units = write offs.units; sorted by date asc.
Part 4: answered from the ontology layer. (Plan covers: Warehouse corrections for 5 kg atta show recorded cycle-count or slot-count variances, which are evidence of corrections but not proof of theft.)
adjusted_ts = 2026-06-25T10:00; slot = A-07-03; reason = cycle count variance; units = 64.0; value_at_cost_inr = 14592.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; inner-join product records on dc stock adjustments.sku = products.sku; keep rows where dc stock adjustments.sku = 'ATTA-WW-5KG'; report adjusted_ts = dc stock adjustments.adjusted_ts, slot = dc stock adjustments.slot, reason = dc stock adjustments.reason, units = dc stock adjustments.units, value_at_cost_inr = dc stock adjustments.value_at_cost_inr; sorted by adjusted_ts asc.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S8N23: Which delivery, pallet (SSCC), and line should the store raise a claim against?

Part 1: not answered: ecords: the ontology layer refused the plan (cannot join {"col": "goods-receipts-june.line"} to {"col": "shipping-notice-lines-june.line"}: not the same kind of key).
Part 2: answered from the ontology layer. (Plan covers: Flags labelled pallets missing from shipping-notice or goods-receipt records as additional claim candidates; no line exists when the pallet itself is absent.)
No rows matched.
  How it was found: From pallet records; left-join shipping-notice line records on pallets.sscc = shipping notice lines.sscc; left-join goods-receipt line records on pallets.sscc = goods receipts.sscc; keep rows where (shipping notice lines.sscc is empty or goods receipts.sscc is empty); group by pallets.shipment_id, pallets.sscc, pallets.cases, pallets.notice_kg, pallets.weight_check; report shipment_id = pallets.shipment_id, sscc = pallets.sscc, cases = pallets.cases, notice_kg = pallets.notice_kg, weight_check = pallets.weight_check, notice_lines = count of shipping notice lines.line, receipt_lines = count of goods receipts.line; sorted by shipment_id asc, sscc asc.

## S8N24: How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8A25: How many UPI payments did the tills attempt in June?

answered from the schema layer. (Plan covers: Counts every UPI payment attempt recorded at the tills in June 2026 (one row = one try).)
upi_attempts = 19166
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report upi_attempts = count of *.

## S8E26: How many UPI attempts timed out (failed: no response) without receiving an RRN?

I can't answer this from Store 014's records: the ontology layer refused the plan (a select item needs 'as' (a lowercase name) and 'expr').

## S8N27: Which successes in the provider's UPI report have no matching approved payment at the till?

I can't answer this from Store 014's records: the ontology layer refused the plan (cannot join {"col": "pos-payments-june.till_status"} to {"lit": "approved"}: not the same kind of key).

## S8N28: Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?

Part 1: answered from the ontology layer. (Plan covers: Hours with 3+ UPI timeouts ('failed: no response'), the first burst condition; the monthly-rate comparison needs the monthly total.)
2 rows (columns: day, hour, timeouts):
  2026-06-20 | 18 | 12
  2026-06-20 | 19 | 16
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by day(pos payments.ts), hour(pos payments.ts); keep groups where count of * >= 3; report day = day(pos payments.ts), hour = hour(pos payments.ts), timeouts = count of *; sorted by day asc, hour asc.
Part 2: answered from the schema layer. (Plan covers: Monthly UPI timeout total and observed time span, to derive the monthly hourly rate for the >10× test.)
monthly_timeouts = 48; first_ts = 2026-06-03T16:25:16; last_ts = 2026-06-28T10:44:29
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; report monthly_timeouts = count of *, first_ts = min of pos payments.ts, last_ts = max of pos payments.ts.

## S8N29: How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"sum": "amount_inr", "arg": {"col": "pos-payments-june.amount_inr"}} is not in the plan form).

## S8N30: Which customers were charged three times for a single bill?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N31: Did any customer pay twice in June, and how many?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"op": "=", "args": [{"col": "pos-payments-june.till_status"}, {"lit": "approved is not in the plan form).

## S8N32: What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?

I can't answer this from Store 014's records: the ontology layer refused the plan ('between' needs arg, low, high).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8N33: Why are 17 UPI credits from 20 and 21 June sitting in suspense?

Part 1: answered from the ontology layer. (Plan covers: Checks the stated 17 credits on 20 and 21 June and shows the settlement rows; the reason money is in suspense is not recorded.)
2 rows (columns: settlement_day, credits, gross, refunds, mdr, net):
  2026-06-20 | 824.0 | 510195.41 | 0.0 | 0.0 | 510195.41
  2026-06-21 | 607.0 | 367003.47 | 0.0 | 0.0 | 367003.47
  How it was found: From UPI settlement records; keep rows where day(upi settlements.settlement_date) in ['2026-06-20', '2026-06-21']; report settlement_day = day(upi settlements.settlement_date), credits = upi settlements.upi_credits, gross = upi settlements.gross_inr, refunds = upi settlements.refunds_inr, mdr = upi settlements.mdr_inr, net = upi settlements.net_inr.
Part 2: answered from the ontology layer. (Plan covers: Shows the provider's final UPI statuses for 20 and 21 June, the recorded evidence behind the settlement figures.)
5 rows (columns: payment_day, provider_status, transactions, amount):
  2026-06-20 | failed | 38 | 21919.46
  2026-06-20 | returned | 1 | 193.11
  2026-06-20 | success | 614 | 370277.27999999997
  2026-06-21 | failed | 34 | 18340.16
  2026-06-21 | success | 663 | 420035.86
  How it was found: From UPI service provider's transaction records; keep rows where day(psp upi report.initiated_ts) in ['2026-06-20', '2026-06-21']; group by day(psp upi report.initiated_ts), psp upi report.status; report payment_day = day(psp upi report.initiated_ts), provider_status = psp upi report.status, transactions = count of *, amount = sum of psp upi report.amount_inr.
Part 3: answered from the ontology layer. (Plan covers: Shows the till's UPI attempt outcomes on those dates so approved, failed and not-known-yet attempts can be compared with the provider report.)
7 rows (columns: till_day, till_status, attempts, amount):
  2026-06-20 | approved | 597 | 362451.59
  2026-06-20 | declined | 20 | 9647.18
  2026-06-20 | failed | 7 | 6037.26
  2026-06-20 | failed: no response | 29 | 14253.82
  2026-06-21 | approved | 663 | 420035.86
  2026-06-21 | declined | 22 | 11535.96
  2026-06-21 | failed | 12 | 6804.2
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) in ['2026-06-20', '2026-06-21']; group by day(pos payments.ts), pos payments.till_status; report till_day = day(pos payments.ts), till_status = pos payments.till_status, attempts = count of *, amount = sum of pos payments.amount_inr.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S8N34: How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?

Part 1: not answered: ecords: the schema layer refused the plan (column 'complaint' is not in table 'customer-complaints-june').
Part 2: answered from the ontology layer. (Plan covers: This identifies bills with more than one provider-successful UPI debit and bounds the extra-debit time using the provider's final success timestamps, per the three-witness payment definition.)
No rows matched.
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and psp upi report.status = 'success'; group by pos payments.bill_id; keep groups where provider_successes > 1; report bill_id = pos payments.bill_id, provider_successes = count distinct of psp upi report.rrn, approved_till_payments = count distinct of pos payments.attempt, first_success_ts = min of psp upi report.status_ts, last_success_ts = max of psp upi report.status_ts; sorted by bill_id asc.
Part 3: not answered: ecords: the schema layer refused the plan (column 'complaint' is not in table 'customer-complaints-june').
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N35: Was the store's UPI technical decline rate acceptable in June?

Part 1: answered from the schema layer. (Plan covers: Counts June UPI attempts and technical declines at the till, where technical decline means till_status 'failed: no response' (a timeout, not a bank decline).)
upi_attempts = 19166; technical_declines = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report upi_attempts = count of *, technical_declines = sum of 0 + 0.
Part 2: answered from the schema layer. (Plan covers: Checks the provider's final UPI statuses for June as the deciding witness on failures, since a till timeout means not known yet.)
provider_transactions = 750; provider_failed = 750
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'failed'; report provider_transactions = count of *, provider_failed = count of *.

## S8N36: Which customers (by RRN) should the store refund now, without waiting for a complaint?

I can't answer this from Store 014's records: the ontology layer refused the plan (cannot join {"col": "pos-payments-june.till_status"} to {"lit": "approved"}: not the same kind of key).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N37: At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?

I can't answer this from Store 014's records: the ontology layer refused the plan ('between' needs arg, low, high).

## S8N38: Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N01: Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?

I can't answer this from Store 014's records: the ontology layer refused the plan ('between' needs arg, low, high).

## S9N02: Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N03: How many bags of 5 kg atta were sold in June 2023?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: year outside 2026

## S9N04: Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S9N05: Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?

Part 1: answered from the ontology layer. (Plan covers: Checks the premise of zero sales on 11 June using recorded daily sales for 5 kg atta; sales are till lines/daily sales, not demand.)
units_sold = 1.0; revenue_inr = 265.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) = '2026-06-11'; report units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr.
Part 2: answered from the ontology layer. (Plan covers: Checks recorded till lines for 5 kg atta specifically on the afternoon of 2026-06-11.)
afternoon_lines = 0; afternoon_units = None; afternoon_revenue_inr = None
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-11' and hour(pos lines may.bill_ts) >= 12; report afternoon_lines = count of *, afternoon_units = sum of pos lines may.qty, afternoon_revenue_inr = sum of pos lines may.line_amount.
Part 3: answered from the ontology layer. (Plan covers: Shows the nearest recorded shelf observation; on-shelf availability is the 11:00 audit status, not book stock.)
No rows matched.
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) = '2026-06-11'; report audit_ts = shelf audits.audit_ts, status = shelf audits.status.
Part 4: answered from the ontology layer. (Plan covers: Shows the recorded closing book stock behind the supply premise; book stock is a belief, not proof of shelf availability or a cause.)
book_on_hand_close = 55.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) = '2026-06-11'; report book_on_hand_close = inventory book.book_on_hand_close.

## S9N06: Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N07: If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N08: Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N09: Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?

Part 1: answered from the ontology layer. (Plan covers: June atta warehouse corrections by product, slot and reason, showing net and gross value; mirror-image corrections on lookalike items or neighboring slots are one event, so a small net can hide large opposite errors.)
2 rows (columns: sku, product, slot, reason, corrections, units, net_value_inr, gross_value_inr):
  ATTA-WW-5KG | Whole wheat atta 5 kg | A-07-03 | cycle count variance | 1 | 64.0 | 14592.0 | 14592.0
  ATTA-WW-1KG | Whole wheat atta 1 kg | A-07-04 | short pick: slot count variance | 1 | -160.0 | -7920.0 | 7920.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; inner-join product records on dc stock adjustments.sku = products.sku; keep rows where dc stock adjustments.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; group by dc stock adjustments.sku, products.name, dc stock adjustments.slot, dc stock adjustments.reason; report sku = dc stock adjustments.sku, product = products.name, slot = dc stock adjustments.slot, reason = dc stock adjustments.reason, corrections = count of *, units = sum of dc stock adjustments.units, net_value_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_inr = sum of abs(dc stock adjustments.value_at_cost_inr); sorted by gross_value_inr desc.
Part 2: answered from the ontology layer. (Plan covers: June atta store count adjustments by product and trigger, separating store count adjustments from warehouse corrections and showing the gross movement behind any small net.)
6 rows (columns: sku, product, trigger, counts, net_adjustment_packs, gross_adjustment_packs):
  ATTA-WW-1KG | Whole wheat atta 1 kg | manager request after complaints | 1 | 157.0 | 157.0
  ATTA-WW-5KG | Whole wheat atta 5 kg | manager request after complaints | 1 | -63.0 | 63.0
  ATTA-WW-1KG | Whole wheat atta 1 kg | scheduled full count | 2 | -4.0 | 6.0
  ATTA-WW-10KG | Whole wheat atta 10 kg | manager request after complaints | 1 | -1.0 | 1.0
  ATTA-WW-10KG | Whole wheat atta 10 kg | scheduled full count | 2 | 1.0 | 1.0
  ATTA-WW-5KG | Whole wheat atta 5 kg | scheduled full count | 2 | -1.0 | 1.0
  How it was found: From stock count records; inner-join product records on stock counts.sku = products.sku; keep rows where stock counts.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG'] and stock counts.count_ts >= '2026-06-01T00:00' and stock counts.count_ts < '2026-07-01T00:00'; group by stock counts.sku, products.name, stock counts.trigger; report sku = stock counts.sku, product = products.name, trigger = stock counts.trigger, counts = count of *, net_adjustment_packs = sum of stock counts.adjustment, gross_adjustment_packs = sum of abs(stock counts.adjustment); sorted by gross_adjustment_packs desc.
Part 3: answered from the ontology layer. (Plan covers: Checks the ₹80 premise for June atta warehouse corrections only, since the records cover Store 014 and its warehouse rather than the whole company, and contrasts net value with gross value.)
first_adjustment = 2026-06-23T14:20; last_adjustment = 2026-06-25T10:00; skus_affected = 2; slots_affected = 2; net_value_inr = 6672.0; gross_value_inr = 22512.0
  How it was found: From warehouse carry carried marked across settled one stock adjustment records; inner-join product records on dc stock adjustments.sku = products.sku; keep rows where dc stock adjustments.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; report first_adjustment = min of dc stock adjustments.adjusted_ts, last_adjustment = max of dc stock adjustments.adjusted_ts, skus_affected = count distinct of dc stock adjustments.sku, slots_affected = count distinct of dc stock adjustments.slot, net_value_inr = sum of dc stock adjustments.value_at_cost_inr, gross_value_inr = sum of abs(dc stock adjustments.value_at_cost_inr).
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N10: Which pallet on the 22 June shipment failed its dispatch weight check?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N11: If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N12: What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?

Part 1: not answered: ecords: the schema layer refused the plan (node {"op": ">=", "args": [{"col": "shipments-june.arrived_ts"}, {"col": "shipments-j is not in the plan form).
Part 2: answered from the ontology layer. (Plan covers: Checks the in-full part per case in June: shipping-notice cases against order cases, so OTIF can be computed per delivery and stated with that definition.)
ordered_cases = 689.0; notice_cases = 686.0
  How it was found: From shipping-notice line records; inner-join store order line records on shipping notice lines.order_id = store orders.order_id and shipping notice lines.sku = store orders.sku; inner-join shipment records on shipping notice lines.shipment_id = shipments.shipment_id; keep rows where shipments.arrived_ts between 2026-06-01T00:00 and 2026-06-28T23:59; report ordered_cases = sum of store orders.cases, notice_cases = sum of shipping notice lines.cases.

## S9N13: Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?

I can't answer this from Store 014's records: no usable plan was returned.

## S9N14: Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N15: Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?

Part 1: answered from the schema layer. (Plan covers: Checks the stated 0.76% UPI technical decline rate against June till attempts rather than accepting the premise.)
attempts = 19166; technical_declines = 0
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report attempts = count of *, technical_declines = sum of 0 + 0.
Part 2: answered from the ontology layer. (Plan covers: Finds June UPI timeout incidents, which are reliability failures even when the overall decline rate is below 1%.)
17 rows (columns: day, timeouts):
  2026-06-20 | 29
  2026-06-09 | 2
  2026-06-08 | 2
  2026-06-05 | 2
  2026-06-28 | 1
  2026-06-26 | 1
  2026-06-25 | 1
  2026-06-24 | 1
  2026-06-22 | 1
  2026-06-19 | 1
  ... and 7 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by day(pos payments.ts); report day = day(pos payments.ts), timeouts = count of *; sorted by timeouts desc.
Part 3: answered from the ontology layer. (Plan covers: Uses the provider's final UPI status to identify failed transactions by day in June.)
28 rows (columns: day, provider_failures):
  2026-06-28 | 44
  2026-06-19 | 43
  2026-06-10 | 43
  2026-06-20 | 38
  2026-06-21 | 34
  2026-06-06 | 33
  2026-06-07 | 32
  2026-06-13 | 31
  2026-06-24 | 30
  2026-06-08 | 29
  ... and 18 more
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'failed'; group by day(psp upi report.status_ts); report day = day(psp upi report.status_ts), provider_failures = count of *; sorted by provider_failures desc.
Part 4: answered from the ontology layer. (Plan covers: Identifies provider successes without an approved till payment, the records' definition of an extra UPI debit and a reliability incident.)
No rows matched.
  How it was found: From UPI service provider's transaction records; inner-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and pos payments.tender = 'UPI' and pos payments.till_status != 'approved'; report rrn = psp upi report.rrn, bill_id = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, provider_status_ts = psp upi report.status_ts, till_status = pos payments.till_status.

## S9N16: Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?

Part 1: answered from the ontology layer. (Plan covers: Checks the stated 17 UPI credits on 20–21 June and shows the recorded settlement amounts; the records do not identify a suspense balance or a revenue-recognition date.)
2 rows (columns: settlement_day, upi_credits, gross_inr, refunds_inr, mdr_inr, net_inr):
  2026-06-20 | 824.0 | 510195.41 | 0.0 | 0.0 | 510195.41
  2026-06-21 | 607.0 | 367003.47 | 0.0 | 0.0 | 367003.47
  How it was found: From UPI settlement records; keep rows where day(upi settlements.settlement_date) between 2026-06-20 and 2026-06-21; report settlement_day = day(upi settlements.settlement_date), upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr, refunds_inr = upi settlements.refunds_inr, mdr_inr = upi settlements.mdr_inr, net_inr = upi settlements.net_inr.
Part 2: answered from the ontology layer. (Plan covers: Shows the provider's final UPI statuses for 20–21 June as evidence around the credits, without treating them as proof of a cause.)
3 rows (columns: provider_status, transactions, amount_inr):
  failed | 72 | 40259.62
  returned | 1 | 193.11
  success | 1277 | 790313.14
  How it was found: From UPI service provider's transaction records; keep rows where day(psp upi report.initiated_ts) between 2026-06-20 and 2026-06-21; group by psp upi report.status; report provider_status = psp upi report.status, transactions = count of *, amount_inr = sum of psp upi report.amount_inr.
Part 3: answered from the ontology layer. (Plan covers: Lists provider successes on 20–21 June with no till payment sharing the RRN, the recorded stand-in for unmatched debits rather than established unclaimed revenue.)
17 rows (columns: rrn, bill_ref, amount_inr, status_ts, till_attempts, approved_till_attempts):
  617118013318 |  | 438.73 | 2026-06-20T18:22:57 | 0 | 
  617118013325 |  | 342.13 | 2026-06-21T11:10:52 | 0 | 
  617118013326 |  | 342.13 | 2026-06-20T21:28:32 | 0 | 
  617118013342 |  | 168.21 | 2026-06-20T18:49:47 | 0 | 
  617118013343 |  | 168.21 | 2026-06-21T13:44:37 | 0 | 
  617118013344 |  | 1064.47 | 2026-06-20T18:49:52 | 0 | 
  617119013351 |  | 372.15 | 2026-06-21T02:38:39 | 0 | 
  617119013361 |  | 171.7 | 2026-06-20T19:10:47 | 0 | 
  617119013363 |  | 592.94 | 2026-06-20T19:12:47 | 0 | 
  617119013372 |  | 398.2 | 2026-06-21T22:21:42 | 0 | 
  ... and 7 more
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where day(psp upi report.initiated_ts) between 2026-06-20 and 2026-06-21 and psp upi report.status = 'success'; group by psp upi report.rrn, psp upi report.bill_ref, psp upi report.amount_inr, psp upi report.status_ts; keep groups where pos payments.rrn is empty; report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, status_ts = psp upi report.status_ts, till_attempts = count of pos payments.attempt, approved_till_attempts = sum of 0 * pos payments.amount_inr.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N17: Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?

Part 1: answered from the ontology layer. (Plan covers: Checks every June refund's request-to-completion turnaround against the 5-day limit and exposes the waits behind the claimed 3-day median; the refund clock here starts at the refund request because the extra debit timestamp is not held in t)
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
  How it was found: From UPI refund records; keep rows where upi refunds.requested_ts >= '2026-06-01T00:00' and upi refunds.requested_ts < '2026-07-01T00:00'; report refund_id = upi refunds.refund_id, bill_id = upi refunds.bill_id, rrn = upi refunds.rrn, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, turnaround_days = days_between(upi refunds.requested_ts, upi refunds.completed_ts); sorted by turnaround_days desc.
Part 2: answered from the ontology layer. (Plan covers: Uses the complaint timestamp as the nearest recorded start of the debit/refund clock to test the 5-day turnaround under Rule 11, since the original extra debit time is not directly recorded.)
23 rows (columns: refund_id, rrn, complaint_ts, requested_ts, completed_ts, days_complaint_to_completion):
  RF-003319 | 615619003319 | 2026-06-06T13:00:00 | 2026-06-06T13:00:00 | 2026-06-08T13:00:00 | -2.0
  RF-011772 | 616918011772 | 2026-06-20T11:00:00 | 2026-06-20T11:00:00 | 2026-06-22T11:00:00 | -2.0
  RF-013318 | 617118013318 | 2026-06-23T17:00:00 | 2026-06-23T17:00:00 | 2026-06-25T17:00:00 | -2.0
  RF-013342 | 617118013342 | 2026-06-23T10:00:00 | 2026-06-23T10:00:00 | 2026-06-25T10:00:00 | -2.0
  RF-013343 | 617118013343 | 2026-06-24T10:00:00 | 2026-06-24T10:00:00 | 2026-06-26T10:00:00 | -2.0
  RF-013363 | 617119013363 | 2026-06-22T18:00:00 | 2026-06-22T18:00:00 | 2026-06-24T18:00:00 | -2.0
  RF-013379 | 617119013379 | 2026-06-22T19:00:00 | 2026-06-22T19:00:00 | 2026-06-24T19:00:00 | -2.0
  RF-008996 | 616517008996 | 2026-06-15T19:00:00 | 2026-06-15T19:00:00 | 2026-06-18T19:00:00 | -3.0
  RF-013351 | 617119013351 | 2026-06-24T10:00:00 | 2026-06-24T10:00:00 | 2026-06-27T10:00:00 | -3.0
  RF-013361 | 617119013361 | 2026-06-23T12:00:00 | 2026-06-23T12:00:00 | 2026-06-26T12:00:00 | -3.0
  ... and 13 more
  How it was found: From UPI refund records; left-join complaint records on upi refunds.rrn = customer complaints.rrn; keep rows where upi refunds.requested_ts >= '2026-06-01T00:00' and upi refunds.requested_ts < '2026-07-01T00:00'; report refund_id = upi refunds.refund_id, rrn = upi refunds.rrn, complaint_ts = customer complaints.complaint_ts, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, days_complaint_to_completion = days_between(customer complaints.complaint_ts, upi refunds.completed_ts); sorted by days_complaint_to_completion desc.
