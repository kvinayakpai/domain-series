## S8N01: How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N02: Which shelf audits found an item empty while the hourly book showed stock above zero?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N03: On which days did any item's closing book stock go below zero?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).

## S8N04: Which stock counts disagreed with the book stock by more than 2%?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N05: Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N06: What time did toned milk record its last sale each day, and how many pouches were written off?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N07: Why did 5 kg atta sales fall in the week of 8 June?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N08: Was 5 kg atta in stock on Thursday 11 June?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N09: Are shoppers switching from 5 kg to 1 kg atta?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N10: What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N11: What has daily demand for 5 kg atta been in June so far?

Part 1: answered from the schema layer. (Plan covers: Daily demand stand-in for 5 kg atta: units sold per day from till lines in June.)
28 rows (columns: date, units_sold):
  2026-06-01 | 22.0
  2026-06-02 | 19.0
  2026-06-03 | 23.0
  2026-06-04 | 24.0
  2026-06-05 | 24.0
  2026-06-06 | 40.0
  2026-06-07 | 28.0
  2026-06-08 | 24.0
  2026-06-09 | 20.0
  2026-06-10 | 20.0
  ... and 18 more
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'RICE-SM-5KG' and daily sales.date between 2026-06-01 and 2026-06-28; group by daily sales.date; report date = daily sales.date, units_sold = sum of daily sales.units_sold; sorted by date asc.
Part 2: answered from the schema layer. (Plan covers: Daily demand stand-in for 5 kg atta: units sold per day from till lines in June.)
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
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-28; group by daily sales.date; report date = daily sales.date, units_sold = sum of daily sales.units_sold; sorted by date asc.
Not recorded, so not answered: needs a longer period than the records cover

## S8N12: How many shoppers left without 5 kg atta, and what were the lost sales in June?

Part 1: answered from the schema layer. (Plan covers: Shoppers who left without 5 kg atta are not recorded; shelf audits showing ATTA-WW-5KG empty at 11:00 are the only shelf evidence, counted per empty audit.)
empty_audits = 2
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and shelf audits.status = 'empty' and shelf audits.audit_ts between 2026-06-01T00:00 and 2026-06-30T23:59; report empty_audits = count of *.
Part 2: answered from the ontology layer. (Plan covers: Lost sales are not recorded; June till lines for ATTA-WW-5KG give units and revenue as the stand-in for lost sales, with bills as shopper stand-ins.)
lost_sales_units = 567.0; lost_sales_revenue = 150255.0; bills_with_5kg_atta = 560; avg_units_per_bill = 1.0125
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and pos lines may.bill_ts between 2026-06-01T00:00 and 2026-06-30T23:59; report lost_sales_units = sum of pos lines may.qty, lost_sales_revenue = sum of pos lines may.line_amount, bills_with_5kg_atta = count distinct of pos lines may.bill_id, avg_units_per_bill = sum of pos lines may.qty / count distinct of pos lines may.bill_id.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]
Stand-ins used (not the real thing): shopper_count (who): a bill is not a shopper: bills are the nearest stand-in

## S8E13: How many of June's deliveries arrived inside their 06:00–06:30 slot?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N14: How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N15: What was the case fill rate across June's store orders according to the shipping notices?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N16: What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N17: Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N18: Which goods receipts did not survive the next stock count within a week?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N19: Was the 22 June delivery on time and in full?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N20: What was Store 014's OTIF from the warehouse in June?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N21: Why was 5 kg atta off the shelf from 23 to 26 June?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N22: Is the 5 kg atta missing at the store theft?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S8N23: Which delivery, pallet (SSCC), and line should the store raise a claim against?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N24: How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8A25: How many UPI payments did the tills attempt in June?

answered from the schema layer. (Plan covers: Counts all till payment attempts with tender UPI in June 2026.)
upi_payment_attempts = 19166
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.ts between 2026-06-01T00:00 and 2026-06-30T23:59; report upi_payment_attempts = count of *.

## S8E26: How many UPI attempts timed out (failed: no response) without receiving an RRN?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N27: Which successes in the provider's UPI report have no matching approved payment at the till?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N28: Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N29: How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N30: Which customers were charged three times for a single bill?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N31: Did any customer pay twice in June, and how many?

I can't answer this from Store 014's records: the ontology layer refused the plan (a condition needs an op).

## S8N32: What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8N33: Why are 17 UPI credits from 20 and 21 June sitting in suspense?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N34: How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N35: Was the store's UPI technical decline rate acceptable in June?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N36: Which customers (by RRN) should the store refund now, without waiting for a complaint?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N37: At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?

I can't answer this from Store 014's records: no usable plan was returned.

## S8N38: Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?

I can't answer this from Store 014's records: the plan has no valid parts.

## S9N01: Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?

Part 1: not answered: ecords: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Part 2: answered from the schema layer. (Plan covers: 5 kg atta units sold in the week of 8 June)
units_week2 = 88.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-08 and 2026-06-14; report units_week2 = sum of daily sales.units_sold.
Part 3: answered from the schema layer. (Plan covers: book stock for 5 kg atta during the week of 8 June)
min_book_on_hand = 33.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and inventory book.date between 2026-06-08 and 2026-06-14; report min_book_on_hand = min of inventory book.book_on_hand_close.
Part 4: answered from the schema layer. (Plan covers: 1 kg atta units sold in the week of 8 June)
units_1kg_week2 = 207.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-1KG' and daily sales.date between 2026-06-08 and 2026-06-14; report units_1kg_week2 = sum of daily sales.units_sold.

## S9N02: Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N03: How many bags of 5 kg atta were sold in June 2023?

I can't answer this from Store 014's records: the ontology layer refused the plan (2023-06-01, 2023-06-30 is outside the records of 'daily-sales-june' (2026-06-01 to 2026-06-28)).
Not recorded: year outside 2026

## S9N04: Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?

Part 1: answered from the ontology layer. (Plan covers: Forecast units for 5 kg atta across June (forecast stands in for demand per Rule 4))
forecast_units = 608.0; forecast_days = 28
  How it was found: From forecast row records; keep rows where forecasts.sku = 'ATTA-WW-5KG' and forecasts.date between 2026-06-01 and 2026-06-28; report forecast_units = sum of forecasts.ordered_units, forecast_days = count distinct of forecasts.date.
Part 2: answered from the ontology layer. (Plan covers: Recorded sales units for 5 kg atta across June (sales stand in for demand per Rule 4))
sales_units = 567.0; sales_days = 28
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and daily sales.date between 2026-06-01 and 2026-06-28; report sales_units = sum of daily sales.units_sold, sales_days = count distinct of daily sales.date.
Not recorded, so not answered: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S9N05: Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?

Part 1: answered from the ontology layer. (Plan covers: Checks whether any 5 kg atta bags were sold on Thursday 11 June afternoon (12:00-17:59) using till lines as the sales record.)
afternoon_units = None; afternoon_bills = 0
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-11' and hour(pos lines may.bill_ts) >= 12 and hour(pos lines may.bill_ts) < 18; report afternoon_units = sum of pos lines may.qty, afternoon_bills = count distinct of pos lines may.bill_id.
Part 2: answered from the ontology layer. (Plan covers: Checks the book stock belief for 5 kg atta on 11 June, noting book stock is not shelf availability.)
book_on_hand_close = 55.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) = '2026-06-11'; report book_on_hand_close = inventory book.book_on_hand_close.
Part 3: answered from the ontology layer. (Plan covers: Checks the 11:00 shelf audit status for 5 kg atta on 11 June as the on-shelf availability evidence.)
No rows matched.
  How it was found: From shelf-audit row records; keep rows where shelf audits.sku = 'ATTA-WW-5KG' and day(shelf audits.audit_ts) = '2026-06-11'; report audit_status = shelf audits.status.

## S9N06: Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N07: If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S9N08: Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N09: Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S9N10: Which pallet on the 22 June shipment failed its dispatch weight check?

I can't answer this from Store 014's records: no usable plan was returned.

## S9N11: If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?

I can't answer this from Store 014's records: the schema layer refused the plan (plan keys not defined: ['plans']).

## S9N12: What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?

I can't answer this from Store 014's records: no usable plan was returned.

## S9N13: Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?

Part 1: answered from the schema layer. (Plan covers: Checks whether any bill has more than one approved UPI payment attempt, which would indicate a customer charged twice.)
No rows matched.
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and pos payments.tender = 'UPI'; group by pos payments.bill_id; keep groups where count of * > 1; report bill_id = pos payments.bill_id, approved_count = count of *.
Part 2: answered from the schema layer. (Plan covers: Counts complaints explicitly recorded as charged twice, which would be direct evidence of double charging.)
complaint_count = 23
  How it was found: From complaint records; keep rows where customer complaints.kind = 'charged twice'; report complaint_count = count of *.

## S9N14: Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.

Part 1: not answered: ecords: the ontology layer refused the plan (an 'on' pair has two nodes).
Part 2: answered from the schema layer. (Plan covers: Lists UPI timeouts with no RRN so the reader can see which timeouts cannot be joined to the provider report.)
48 rows (columns: attempt, bill_id, rrn, till_status):
  1 | B260603-090023 |  | failed: no response
  1 | B260604-140026 |  | failed: no response
  1 | B260605-040030 |  | failed: no response
  1 | B260605-120088 |  | failed: no response
  1 | B260606-040056 |  | failed: no response
  1 | B260608-010027 |  | failed: no response
  1 | B260608-020011 |  | failed: no response
  1 | B260609-040018 |  | failed: no response
  1 | B260610-050041 |  | failed: no response
  1 | B260614-100001 |  | failed: no response
  ... and 38 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and pos payments.rrn is empty; report attempt = pos payments.attempt, bill_id = pos payments.bill_id, rrn = pos payments.rrn, till_status = pos payments.till_status; sorted by attempt asc.

## S9N15: Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?

I can't answer this from Store 014's records: the ontology layer refused the plan ('between' needs arg, low, high).

## S9N16: Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?

I can't answer this from Store 014's records: no usable plan was returned.
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S9N17: Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?

Part 1: answered from the ontology layer. (Plan covers: June refund turnaround days from request to completion)
23 rows (columns: turnaround_days):
  -5.0
  -5.0
  -5.0
  -5.0
  -5.0
  -4.0
  -4.0
  -3.0
  -3.0
  -3.0
  ... and 13 more
  How it was found: From UPI refund records; keep rows where upi refunds.requested_ts between 2026-06-01T00:00 and 2026-06-30T23:59; report turnaround_days = days_between(upi refunds.requested_ts, upi refunds.completed_ts); sorted by turnaround_days asc.
Part 2: answered from the schema layer. (Plan covers: June complaints count to check the median-wait premise)
complaint_count = 26
  How it was found: From complaint records; keep rows where customer complaints.complaint_ts between 2026-06-01T00:00 and 2026-06-30T23:59; report complaint_count = count of *.
Part 3: answered from the ontology layer. (Plan covers: June complaint resolution wait to test the stated median of 3 days)
26 rows (columns: median_wait_days):
  -2.0416666669771075
  -5.0
  -2.0
  -4.0
  -0.041666666977107525
  -3.0
  -2.0
  -3.0
  -3.0
  -5.0
  ... and 16 more
  How it was found: From complaint records; keep rows where customer complaints.complaint_ts between 2026-06-01T00:00 and 2026-06-30T23:59; report median_wait_days = days_between(customer complaints.complaint_ts, customer complaints.resolved_ts).
