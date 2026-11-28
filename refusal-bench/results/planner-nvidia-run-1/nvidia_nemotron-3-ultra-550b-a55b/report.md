## S8N01: How many bags of 5 kg atta were sold in June 2026 (or in the week of 8 June)?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N02: Which shelf audits found an item empty while the hourly book showed stock above zero?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).

## S8N03: On which days did any item's closing book stock go below zero?

I can't answer this from Store 014's records: the ontology layer refused the plan (group_by without an aggregate).

## S8N04: Which stock counts disagreed with the book stock by more than 2%?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N05: Which warehouse items saw their weekly sales drop by more than half from week 1 to week 2?

Part 1: answered from the ontology layer. (Plan covers: Week 1 (2026-06-01 to 2026-06-07) total units sold per SKU)
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
  How it was found: From daily sales row records; keep rows where day(daily sales.date) between 2026-06-01 and 2026-06-07; group by daily sales.sku; report sku = daily sales.sku, week1_units = sum of daily sales.units_sold.
Part 2: answered from the ontology layer. (Plan covers: Week 2 (2026-06-08 to 2026-06-14) total units sold per SKU)
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
  How it was found: From daily sales row records; keep rows where day(daily sales.date) between 2026-06-08 and 2026-06-14; group by daily sales.sku; report sku = daily sales.sku, week2_units = sum of daily sales.units_sold.

## S8N06: What time did toned milk record its last sale each day, and how many pouches were written off?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N07: Why did 5 kg atta sales fall in the week of 8 June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N08: Was 5 kg atta in stock on Thursday 11 June?

answered from the ontology layer. (Plan covers: Checks book stock (belief) for 5 kg atta on 2026-06-11; on-shelf availability requires shelf-audits which has no row for that date.)
book_on_hand_close = 55.0
  How it was found: From book-stock row records; keep rows where inventory book.sku = 'ATTA-WW-5KG' and day(inventory book.date) = '2026-06-11'; report book_on_hand_close = inventory book.book_on_hand_close.

## S8N09: Are shoppers switching from 5 kg to 1 kg atta?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N10: What was 5 kg atta's on-shelf availability in June (from book stock vs. shelf audits vs. books and tills)?

Part 1: answered from the ontology layer. (Plan covers: On-shelf availability from shelf audits: share of audits with status 'on shelf' for 5 kg atta (ATTA-WW-5KG) in June.)
2 rows (columns: status, audit_count):
  empty | 2
  on shelf | 6
  How it was found: From shelf-audit row records; inner-join product records on shelf audits.sku = products.sku; keep rows where products.sku = 'ATTA-WW-5KG'; group by shelf audits.status; report status = shelf audits.status, audit_count = count of *.
Part 2: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).
Part 3: answered from the ontology layer. (Plan covers: Daily sales (till lines) for 5 kg atta (ATTA-WW-5KG) in June from pos-lines-may-june.)
24 rows (columns: date, units_sold):
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
  ... and 14 more
  How it was found: From till line records; inner-join product records on pos lines may.sku_scanned = products.sku; keep rows where products.sku = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) >= '2026-06-01' and day(pos lines may.bill_ts) <= '2026-06-28'; group by day(pos lines may.bill_ts); report date = day(pos lines may.bill_ts), units_sold = sum of pos lines may.qty; sorted by date asc.

## S8N11: What has daily demand for 5 kg atta been in June so far?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: needs a longer period than the records cover

## S8N12: How many shoppers left without 5 kg atta, and what were the lost sales in June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8E13: How many of June's deliveries arrived inside their 06:00–06:30 slot?

answered from the schema layer. (Plan covers: Counts June shipments whose arrived_ts falls within the slot_start–slot_end window (06:00–06:30 per ontology).)
on_time_deliveries = 23
  How it was found: From shipment records; keep rows where (shipments.arrived_ts >= shipments.slot_start and shipments.arrived_ts <= shipments.slot_end); report on_time_deliveries = count of *.

## S8N14: How many of June's 30 pallets were weighed at dispatch or case-scanned at receipt?

Part 1: answered from the schema layer. (Plan covers: Count of pallets not weighed at dispatch (weight_check = 'not weighed'))
not_weighed_count = 30
  How it was found: From pallet records; keep rows where pallets.weight_check = 'not weighed'; report not_weighed_count = count of *.
Part 2: answered from the schema layer. (Plan covers: Count of pallet lines case-scanned at receipt (receipt_method = 'pallet label (SSCC) scan against the shipping notice'))
case_scanned_count = 70
  How it was found: From goods-receipt line records; keep rows where goods receipts.receipt_method = 'pallet label (SSCC) scan against the shipping notice'; report case_scanned_count = count of *.

## S8N15: What was the case fill rate across June's store orders according to the shipping notices?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N16: What is the net vs. gross value (at cost) of atta stock corrections across the warehouse and the store?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N17: Which count corrections in the warehouse and store form mirror-image pairs (same product family, opposite signs, within 15% in cases, within 7 days)?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N18: Which goods receipts did not survive the next stock count within a week?

answered from the ontology layer. (Plan covers: Goods receipt lines and the first stock count for the same SKU within 7 days after receipt)
20 rows (columns: grn_id, line, sku, received_ts, units_booked, next_count_ts, days_to_count):
  GRN-260620 | 1 | ATTA-WW-5KG | 2026-06-20T06:22 | 72.0 | 2026-06-26T09:00 | 6.109722222201526
  GRN-260620 | 2 | ATTA-WW-10KG | 2026-06-20T06:22 | 24.0 | 2026-06-26T09:00 | 6.109722222201526
  GRN-260622 | 1 | ATTA-WW-5KG | 2026-06-22T06:12 | 64.0 | 2026-06-26T09:00 | 4.116666666697711
  GRN-260622 | 2 | ATTA-WW-1KG | 2026-06-22T06:12 | 90.0 | 2026-06-26T09:00 | 4.116666666697711
  GRN-260622 | 3 | RICE-SM-5KG | 2026-06-22T06:12 | 56.0 | 2026-06-28T22:30 | 6.679166666697711
  GRN-260622 | 4 | SUGAR-1KG | 2026-06-22T06:12 | 50.0 | 2026-06-28T22:30 | 6.679166666697711
  GRN-260623 | 1 | ATTA-WW-10KG | 2026-06-23T06:18 | 26.0 | 2026-06-26T09:00 | 3.1124999998137355
  GRN-260623 | 2 | DAL-TOOR-1KG | 2026-06-23T06:18 | 60.0 | 2026-06-28T22:30 | 5.6749999998137355
  GRN-260623 | 3 | OIL-SUN-1L | 2026-06-23T06:18 | 80.0 | 2026-06-28T22:30 | 5.6749999998137355
  GRN-260624 | 1 | SUGAR-1KG | 2026-06-24T06:07 | 40.0 | 2026-06-28T22:30 | 4.682638888712972
  ... and 10 more
  How it was found: From goods-receipt line records; left-join stock count records on goods receipts.sku_booked = stock counts.sku; keep rows where (goods receipts.received_ts is not empty and stock counts.count_ts is not empty and stock counts.count_ts > goods receipts.received_ts and days_between(stock counts.count_ts, goods receipts.received_ts) <= 7); group by goods receipts.grn_id, goods receipts.line, goods receipts.sku_booked, goods receipts.received_ts, goods receipts.units_booked; report grn_id = goods receipts.grn_id, line = goods receipts.line, sku = goods receipts.sku_booked, received_ts = goods receipts.received_ts, units_booked = goods receipts.units_booked, next_count_ts = min of stock counts.count_ts, days_to_count = days_between(min of stock counts.count_ts, goods receipts.received_ts).

## S8N19: Was the 22 June delivery on time and in full?

I can't answer this from Store 014's records: the schema layer refused the plan (node {"op": "and", "args": [{"op": ">=", "args": [{"col": "shipments-june.arrived_ts" is not in the plan form).

## S8N20: What was Store 014's OTIF from the warehouse in June?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N21: Why was 5 kg atta off the shelf from 23 to 26 June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N22: Is the 5 kg atta missing at the store theft?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S8N23: Which delivery, pallet (SSCC), and line should the store raise a claim against?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8N24: How many bags of 5 kg atta did shoppers want and not find between 23 and 26 June?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S8A25: How many UPI payments did the tills attempt in June?

answered from the schema layer. (Plan covers: Count of UPI payment attempts recorded at the tills in June.)
upi_attempts = 19166
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report upi_attempts = count of *.

## S8E26: How many UPI attempts timed out (failed: no response) without receiving an RRN?

answered from the schema layer. (Plan covers: Counts UPI payment attempts that timed out at the till (failed: no response) and have no RRN recorded.)
timeout_count = 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and pos payments.rrn is empty; report timeout_count = count of *.

## S8N27: Which successes in the provider's UPI report have no matching approved payment at the till?

answered from the ontology layer. (Plan covers: Provider UPI successes (status=success) with no approved till payment (till_status != approved or missing), per Rule 9 and Rule 10.)
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
  How it was found: From UPI service provider's transaction records; left-join payment attempt records on psp upi report.rrn = pos payments.rrn; keep rows where psp upi report.status = 'success' and (pos payments.till_status is empty or pos payments.till_status != 'approved'); report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, amount_inr = psp upi report.amount_inr, initiated_ts = psp upi report.initiated_ts, status_ts = psp upi report.status_ts, till_status = pos payments.till_status.

## S8N28: Which hours in June had a burst of UPI timeouts (3+ timeouts and >10× the monthly rate)?

Part 1: answered from the ontology layer. (Plan covers: Count UPI timeouts per hour in June)
12 rows (columns: hour, timeout_count):
  8 | 1
  9 | 1
  10 | 2
  11 | 3
  12 | 2
  13 | 2
  16 | 3
  17 | 1
  18 | 13
  19 | 17
  ... and 2 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; group by hour(pos payments.ts); report hour = hour(pos payments.ts), timeout_count = count of *; sorted by hour asc.
Part 2: answered from the schema layer. (Plan covers: Total UPI attempts in June for monthly rate)
total_upi = 19166
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; report total_upi = count of *.

## S8N29: How many UPI bills in June were above ₹2,000, and what would a 0.4% MDR fee (capped at ₹300) cost?

Part 1: answered from the schema layer. (Plan covers: Count UPI bills in June with approved payments above ₹2,000)
200 rows (columns: bill_id, bill_amount):
  B260601-000089 | 2977.01
  B260601-010043 | 2381.39
  B260601-020073 | 4599.82
  B260601-030030 | 2073.68
  B260601-040003 | 2635.97
  B260601-040035 | 2789.39
  B260601-040046 | 4263.67
  B260601-050005 | 2650.58
  B260601-060000 | 2709.93
  B260601-070025 | 2441.74
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved'; group by pos payments.bill_id; keep groups where bill_amount > 2000; report bill_id = pos payments.bill_id, bill_amount = sum of pos payments.amount_inr.
Part 2: answered from the schema layer. (Plan covers: Calculate 0.4% MDR fee capped at ₹300 for each UPI bill above ₹2,000)
200 rows (columns: bill_id, bill_amount):
  B260601-000089 | 2977.01
  B260601-010043 | 2381.39
  B260601-020073 | 4599.82
  B260601-030030 | 2073.68
  B260601-040003 | 2635.97
  B260601-040035 | 2789.39
  B260601-040046 | 4263.67
  B260601-050005 | 2650.58
  B260601-060000 | 2709.93
  B260601-070025 | 2441.74
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'approved'; group by pos payments.bill_id; keep groups where bill_amount > 2000; report bill_id = pos payments.bill_id, bill_amount = sum of pos payments.amount_inr.

## S8N30: Which customers were charged three times for a single bill?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N31: Did any customer pay twice in June, and how many?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S8N32: What happened to the UPI payments the tills gave up on between 18:20 and 19:50 on Saturday 20 June (late credit vs. debited and returned vs. never debited)?

Part 1: answered from the ontology layer. (Plan covers: UPI payment attempts the till marked 'failed: no response' between 18:20 and 19:50 on 2026-06-20 (the till gave up on these).)
28 rows (columns: bill_id, attempt, till_ts, amount_inr, rrn):
  B260620-110022 | 1 | 2026-06-20T18:22:03 | 438.73 | 
  B260620-110024 | 1 | 2026-06-20T18:25:41 | 126.67 | 
  B260620-110027 | 1 | 2026-06-20T18:27:56 | 346.5 | 
  B260620-110029 | 1 | 2026-06-20T18:28:25 | 1977.43 | 
  B260620-110032 | 1 | 2026-06-20T18:32:55 | 342.13 | 
  B260620-110032 | 2 | 2026-06-20T18:33:25 | 342.13 | 
  B260620-110032 | 3 | 2026-06-20T18:33:55 | 342.13 | 
  B260620-110035 | 1 | 2026-06-20T18:34:10 | 602.95 | 
  B260620-110048 | 1 | 2026-06-20T18:45:34 | 276.24 | 
  B260620-110056 | 1 | 2026-06-20T18:48:25 | 1064.47 | 
  ... and 18 more
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and day(pos payments.ts) = '2026-06-20' and hour(pos payments.ts) >= 18 and hour(pos payments.ts) <= 19; report bill_id = pos payments.bill_id, attempt = pos payments.attempt, till_ts = pos payments.ts, amount_inr = pos payments.amount_inr, rrn = pos payments.rrn; sorted by till_ts asc.
Part 2: answered from the ontology layer. (Plan covers: UPI provider transactions initiated between 18:00 and 19:59 on 2026-06-20, showing final status (success, failed, returned) and timestamps.)
109 rows (columns: bill_ref, rrn, initiated_ts, amount_inr, status, status_ts):
   | 617118013301 | 2026-06-20T18:00:18 | 303.2 | success | 2026-06-20T18:00:18
   | 617118013302 | 2026-06-20T18:01:13 | 453.95 | success | 2026-06-20T18:01:13
   | 617118013303 | 2026-06-20T18:02:16 | 296.41 | failed | 2026-06-20T18:02:16
   | 617118013304 | 2026-06-20T18:02:31 | 296.41 | success | 2026-06-20T18:02:31
   | 617118013305 | 2026-06-20T18:05:41 | 359.64 | success | 2026-06-20T18:05:41
   | 617118013306 | 2026-06-20T18:08:08 | 317.88 | success | 2026-06-20T18:08:08
   | 617118013307 | 2026-06-20T18:09:48 | 277.13 | success | 2026-06-20T18:09:48
   | 617118013308 | 2026-06-20T18:11:33 | 342.39 | success | 2026-06-20T18:11:33
   | 617118013309 | 2026-06-20T18:12:35 | 383.98 | success | 2026-06-20T18:12:35
   | 617118013310 | 2026-06-20T18:12:58 | 266.88 | success | 2026-06-20T18:12:58
  ... and 99 more
  How it was found: From UPI service provider's transaction records; keep rows where day(psp upi report.initiated_ts) = '2026-06-20' and hour(psp upi report.initiated_ts) >= 18 and hour(psp upi report.initiated_ts) <= 19; report bill_ref = psp upi report.bill_ref, rrn = psp upi report.rrn, initiated_ts = psp upi report.initiated_ts, amount_inr = psp upi report.amount_inr, status = psp upi report.status, status_ts = psp upi report.status_ts; sorted by initiated_ts asc.
Part 3: answered from the ontology layer. (Plan covers: UPI refunds requested on 2026-06-20 (debited and returned to customer's bank).)
bill_id = B260618-110082; rrn = 616918011772; amount_inr = 963.27; requested_ts = 2026-06-20T11:00:00; completed_ts = 2026-06-22T11:00:00
  How it was found: From UPI refund records; keep rows where day(upi refunds.requested_ts) = '2026-06-20'; report bill_id = upi refunds.bill_id, rrn = upi refunds.rrn, amount_inr = upi refunds.amount_inr, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts; sorted by requested_ts asc.
Part 4: answered from the ontology layer. (Plan covers: Customer complaints on 2026-06-20 (charged twice or debited but till said failed) and their resolutions.)
1 rows (columns: bill_id, rrn, kind, amount_inr, complaint_ts, resolution, resolved_ts):
  B260618-110082 | 616918011772 | charged twice | 963.27 | 2026-06-20T11:00:00 | refunded after the store matched the credit by hand | 2026-06-22T11:00:00
  How it was found: From complaint records; keep rows where day(customer complaints.complaint_ts) = '2026-06-20'; report bill_id = customer complaints.bill_id, rrn = customer complaints.rrn, kind = customer complaints.kind, amount_inr = customer complaints.amount_inr, complaint_ts = customer complaints.complaint_ts, resolution = customer complaints.resolution, resolved_ts = customer complaints.resolved_ts; sorted by complaint_ts asc.
Not recorded, so not answered: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]

## S8N33: Why are 17 UPI credits from 20 and 21 June sitting in suspense?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: cause (why): no table records the reason or cause of an event [rule-5]

## S8N34: How long did customers who paid twice wait for their money (from the extra debit vs. from the complaint), and how many were still unrefunded at month end?

Part 1: answered from the schema layer. (Plan covers: Complaints for 'charged twice' with timestamps and RRN to link to debit and refund)
23 rows (columns: complaint_ts, resolved_ts, rrn, bill_id):
  2026-06-05T12:00:00 | 2026-06-10T12:00:00 | 615521002766 | B260604-140026
  2026-06-06T13:00:00 | 2026-06-08T13:00:00 | 615619003319 | B260605-120088
  2026-06-10T10:00:00 | 2026-06-14T10:00:00 | 616011005544 | B260609-040018
  2026-06-15T19:00:00 | 2026-06-18T19:00:00 | 616517008996 | B260614-100001
  2026-06-20T11:00:00 | 2026-06-22T11:00:00 | 616918011772 | B260618-110082
  2026-06-22T11:00:00 | 2026-06-25T11:00:00 | 617119013372 | B260620-120037
  2026-06-22T12:00:00 | 2026-06-25T12:00:00 | 617119013400 | B260620-120072
  2026-06-22T14:00:00 | 2026-06-27T14:00:00 | 617118013326 | B260620-110032
  2026-06-22T15:00:00 | 2026-06-25T15:00:00 | 617119013375 | B260620-120041
  2026-06-22T18:00:00 | 2026-06-24T18:00:00 | 617119013363 | B260620-120019
  ... and 13 more
  How it was found: From complaint records; keep rows where customer complaints.kind = 'charged twice'; report complaint_ts = customer complaints.complaint_ts, resolved_ts = customer complaints.resolved_ts, rrn = customer complaints.rrn, bill_id = customer complaints.bill_id.
Part 2: answered from the schema layer. (Plan covers: Approved UPI payments per bill and RRN to identify the first successful debit)
200 rows (columns: bill_id, rrn, ts):
  B260601-000003 | 615207000001 | 2026-06-01T07:01:03
  B260601-000005 | 615207000002 | 2026-06-01T07:01:36
  B260601-000006 | 615207000003 | 2026-06-01T07:01:39
  B260601-000007 | 615207000004 | 2026-06-01T07:02:41
  B260601-000008 | 615207000006 | 2026-06-01T07:02:52
  B260601-000010 | 615207000007 | 2026-06-01T07:02:22
  B260601-000012 | 615207000008 | 2026-06-01T07:04:57
  B260601-000013 | 615207000009 | 2026-06-01T07:05:20
  B260601-000015 | 615207000010 | 2026-06-01T07:06:16
  B260601-000016 | 615207000011 | 2026-06-01T07:07:23
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved' and pos payments.tender = 'UPI'; report bill_id = pos payments.bill_id, rrn = pos payments.rrn, ts = pos payments.ts.
Part 3: answered from the schema layer. (Plan covers: Successful UPI transactions from provider with initiation and settlement timestamps)
200 rows (columns: rrn, bill_ref, initiated_ts, status_ts):
  615207000001 |  | 2026-06-01T07:01:03 | 2026-06-01T07:01:03
  615207000002 |  | 2026-06-01T07:01:36 | 2026-06-01T07:01:36
  615207000003 |  | 2026-06-01T07:01:39 | 2026-06-01T07:01:39
  615207000004 |  | 2026-06-01T07:02:41 | 2026-06-01T07:02:41
  615207000006 |  | 2026-06-01T07:02:52 | 2026-06-01T07:02:52
  615207000007 |  | 2026-06-01T07:02:22 | 2026-06-01T07:02:22
  615207000008 |  | 2026-06-01T07:04:57 | 2026-06-01T07:04:57
  615207000009 |  | 2026-06-01T07:05:20 | 2026-06-01T07:05:20
  615207000010 |  | 2026-06-01T07:06:16 | 2026-06-01T07:06:16
  615207000011 |  | 2026-06-01T07:07:23 | 2026-06-01T07:07:23
  ... and 190 more
  How it was found: From UPI service provider's transaction records; keep rows where psp upi report.status = 'success'; report rrn = psp upi report.rrn, bill_ref = psp upi report.bill_ref, initiated_ts = psp upi report.initiated_ts, status_ts = psp upi report.status_ts.
Part 4: answered from the schema layer. (Plan covers: Refunds triggered by customer complaint with request and completion timestamps)
23 rows (columns: bill_id, rrn, requested_ts, completed_ts):
  B260604-140026 | 615521002766 | 2026-06-05T12:00:00 | 2026-06-10T12:00:00
  B260605-120088 | 615619003319 | 2026-06-06T13:00:00 | 2026-06-08T13:00:00
  B260609-040018 | 616011005544 | 2026-06-10T10:00:00 | 2026-06-14T10:00:00
  B260614-100001 | 616517008996 | 2026-06-15T19:00:00 | 2026-06-18T19:00:00
  B260618-110082 | 616918011772 | 2026-06-20T11:00:00 | 2026-06-22T11:00:00
  B260620-110022 | 617118013318 | 2026-06-23T17:00:00 | 2026-06-25T17:00:00
  B260620-110032 | 617118013325 | 2026-06-23T14:00:00 | 2026-06-28T14:00:00
  B260620-110032 | 617118013326 | 2026-06-22T14:00:00 | 2026-06-27T14:00:00
  B260620-110055 | 617118013342 | 2026-06-23T10:00:00 | 2026-06-25T10:00:00
  B260620-110055 | 617118013343 | 2026-06-24T10:00:00 | 2026-06-26T10:00:00
  ... and 13 more
  How it was found: From UPI refund records; keep rows where upi refunds.trigger = 'customer complaint'; report bill_id = upi refunds.bill_id, rrn = upi refunds.rrn, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N35: Was the store's UPI technical decline rate acceptable in June?

answered from the schema layer. (Plan covers: Counts UPI payment attempts by till status to compute the technical decline rate (failed + failed: no response) / total UPI attempts for June.)
4 rows (columns: till_status, attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *.

## S8N36: Which customers (by RRN) should the store refund now, without waiting for a complaint?

answered from the ontology layer. (Plan covers: Identifies UPI payments that timed out at the till (failed: no response) but succeeded per the PSP report, indicating extra debits that should be refunded per Rule 9 and Rule 10.)
No rows matched.
  How it was found: From payment attempt records; inner-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response' and psp upi report.status = 'success'; report rrn = pos payments.rrn, bill_id = pos payments.bill_id, amount_inr = pos payments.amount_inr, payment_ts = pos payments.ts, psp_status_ts = psp upi report.status_ts; sorted by rrn asc.
Not recorded, so not answered: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S8N37: At 20:00 on Tuesday 23 June, why has 5 kg atta stopped selling at Store 014 this evening—and if a delivery is to blame, which shipment and line, and what was really on it?

Part 1: answered from the ontology layer. (Plan covers: Part 1: Check if 5 kg atta had zero sales on 23 June (the Tuesday in question).)
date = 2026-06-23; units_sold = 5.0; revenue_inr = 1325.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) = '2026-06-23'; report date = day(daily sales.date), units_sold = daily sales.units_sold, revenue_inr = daily sales.revenue_inr.
Part 2: answered from the ontology layer. (Plan covers: Part 2: Check for any 5 kg atta sales after 20:00 on 23 June at the till level.)
No rows matched.
  How it was found: From till line records; keep rows where pos lines may.sku_scanned = 'ATTA-WW-5KG' and day(pos lines may.bill_ts) = '2026-06-23' and hour(pos lines may.bill_ts) >= 20; report bill_ts = pos lines may.bill_ts, qty = pos lines may.qty, line_amount = pos lines may.line_amount; sorted by bill_ts asc.
Part 3: answered from the ontology layer. (Plan covers: Part 3: Check fresh deliveries of 5 kg atta on 23 June (DSD flow) that could affect evening availability.)
No rows matched.
  How it was found: From fresh-delivery row records; keep rows where fresh deliveries.sku = 'ATTA-WW-5KG' and day(fresh deliveries.delivery_ts) = '2026-06-23'; report delivery_ts = fresh deliveries.delivery_ts, route = fresh deliveries.route, units = fresh deliveries.units, crates = fresh deliveries.crates, use_by = fresh deliveries.use_by; sorted by delivery_ts asc.
Part 4: answered from the ontology layer. (Plan covers: Part 4: Check DC receipts of 5 kg atta on 23 June with shipment arrival times to identify late/short deliveries.)
No rows matched.
  How it was found: From goods-receipt line records; inner-join shipment records on goods receipts.shipment_id = shipments.shipment_id; keep rows where goods receipts.sku_booked = 'ATTA-WW-5KG' and day(goods receipts.received_ts) = '2026-06-23'; report shipment_id = goods receipts.shipment_id, received_ts = goods receipts.received_ts, units_booked = goods receipts.units_booked, asn_units = goods receipts.asn_units, arrived_ts = shipments.arrived_ts, slot_start = shipments.slot_start, slot_end = shipments.slot_end; sorted by received_ts asc.

## S8N38: Across all 12 joins between Store 014's tables, which pairs agree on 100% of rows (copies) and which ones disagree (observations)?

I can't answer this from Store 014's records: no usable plan was returned.

## S9N01: Since 5 kg atta sales dropped 59% in the week of 8 June while the books showed stock on hand all week, how much shelf space should we reallocate from 5 kg to 1 kg atta?

Part 1: answered from the ontology layer. (Plan covers: Daily units sold of 5 kg atta (ATTA-WW-5KG) for the week of 8 June 2026.)
7 rows (columns: day, units_sold_5kg):
  2026-06-08 | 9.0
  2026-06-09 | 11.0
  2026-06-10 | 22.0
  2026-06-11 | 1.0
  2026-06-12 | 0.0
  2026-06-13 | 22.0
  2026-06-14 | 23.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-5KG' and day(daily sales.date) between 2026-06-08 and 2026-06-14; group by day(daily sales.date); report day = day(daily sales.date), units_sold_5kg = sum of daily sales.units_sold; sorted by day asc.
Part 2: not answered: ecords: the ontology layer refused the plan (the question names day 8 of month 6 but the plan has no such date).
Part 3: answered from the ontology layer. (Plan covers: Daily units sold of 1 kg atta (ATTA-WW-1KG) for the week of 8 June 2026.)
7 rows (columns: day, units_sold_1kg):
  2026-06-08 | 27.0
  2026-06-09 | 24.0
  2026-06-10 | 41.0
  2026-06-11 | 31.0
  2026-06-12 | 24.0
  2026-06-13 | 28.0
  2026-06-14 | 32.0
  How it was found: From daily sales row records; keep rows where daily sales.sku = 'ATTA-WW-1KG' and day(daily sales.date) between 2026-06-08 and 2026-06-14; group by day(daily sales.date); report day = day(daily sales.date), units_sold_1kg = sum of daily sales.units_sold; sorted by day asc.
Part 4: not answered: ecords: the ontology layer refused the plan (group_by without an aggregate).

## S9N02: Which table records the exact number of shoppers who walked out without 5 kg atta in June 2026, and how many were there?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: absent_event (not_happen): nothing records a shopper who did not buy, a product not on the shelf, a payment not retried [rule-3]; person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N03: How many bags of 5 kg atta were sold in June 2023?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: year outside 2026

## S9N04: Our 28-day forecast for 5 kg atta ran 13% too high in June—by how much should we tune it down to match shopper demand?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: external (else): nothing about competitors, weather, other stores, costs beyond one per product, or anything outside these 11 products

## S9N05: Given that we had 2.3 days of supply of 5 kg atta on Thursday 11 June, why did the store fail to sell any bags that afternoon?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N06: Which cashier or shoplifter caused the 55 missing pouches of toned milk at the month-end count?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N07: If we cut our toned milk standing order by 5% to lift margin after waste from ₹4,121 to ₹10,810, how many extra shoppers will leave without milk according to the till records?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N08: Since the 22 June delivery arrived inside its slot with zero discrepancies on the goods receipt, who in the store stole the 63 missing bags of 5 kg atta?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).
Not recorded: person_identity (who): no table identifies a customer, cashier, supplier, driver or household

## S9N09: Why should we investigate June's atta stock adjustments if they only net out to ₹80 across the company?

Part 1: not answered: ecords: the schema layer refused the plan (node {"op": "abs", "args": [{"col": "dc-stock-adjustments-june.value_at_cost_inr"}]} is not in the plan form).
Part 2: answered from the schema layer. (Plan covers: Shows store-level stock count adjustments for atta SKUs by trigger type, which may reveal manager-requested counts after complaints that warehouse adjustments alone would miss.)
6 rows (columns: sku, trigger, total_adjustment_packs, count_events):
  ATTA-WW-10KG | manager request after complaints | -1.0 | 1
  ATTA-WW-10KG | scheduled full count | 1.0 | 2
  ATTA-WW-1KG | manager request after complaints | 157.0 | 1
  ATTA-WW-1KG | scheduled full count | -4.0 | 2
  ATTA-WW-5KG | manager request after complaints | -63.0 | 1
  ATTA-WW-5KG | scheduled full count | -1.0 | 2
  How it was found: From stock count records; keep rows where stock counts.sku in ['ATTA-WW-10KG', 'ATTA-WW-1KG', 'ATTA-WW-5KG']; group by stock counts.sku, stock counts.trigger; report sku = stock counts.sku, trigger = stock counts.trigger, total_adjustment_packs = sum of stock counts.adjustment, count_events = count of *.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N10: Which pallet on the 22 June shipment failed its dispatch weight check?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S9N11: If we start weighing every pallet at dispatch or scanning every case at the store, how much will our OTIF scorecard improve?

I can't answer this from Store 014's records: the schema layer found no way to answer it (no valid query plan exists).

## S9N12: What was Store 014's OTIF in June—92%, 90%, 88%, or 84%?

I can't answer this from Store 014's records: the ontology layer refused the plan (an 'on' pair has two nodes).

## S9N13: Since all 30,077 bills in June have exactly one approved payment, can we confirm that zero customers were charged twice?

Part 1: answered from the schema layer. (Plan covers: Find bills with more than one approved payment attempt in June.)
No rows matched.
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; group by pos payments.bill_id; keep groups where approved_count > 1; report bill_id = pos payments.bill_id, approved_count = count of *.
Part 2: answered from the schema layer. (Plan covers: Find bills with exactly one approved payment attempt in June.)
200 rows (columns: bill_id, approved_count):
  B260601-000000 | 1
  B260601-000001 | 1
  B260601-000002 | 1
  B260601-000003 | 1
  B260601-000004 | 1
  B260601-000005 | 1
  B260601-000006 | 1
  B260601-000007 | 1
  B260601-000008 | 1
  B260601-000009 | 1
  ... and 190 more
  How it was found: From payment attempt records; keep rows where pos payments.till_status = 'approved'; group by pos payments.bill_id; keep groups where approved_count = 1; report bill_id = pos payments.bill_id, approved_count = count of *.
Part 3: answered from the schema layer. (Plan covers: List complaints that indicate possible double charging in June.)
26 rows (columns: bill_id, kind, complaint_ts):
  B260603-090023 | debited but the till said failed | 2026-06-04T10:00:00
  B260604-140026 | charged twice | 2026-06-05T12:00:00
  B260605-120088 | charged twice | 2026-06-06T13:00:00
  B260609-040018 | charged twice | 2026-06-10T10:00:00
  B260610-050041 | debited but the till said failed | 2026-06-11T10:00:00
  B260614-100001 | charged twice | 2026-06-15T19:00:00
  B260618-110082 | charged twice | 2026-06-20T11:00:00
  B260620-120037 | charged twice | 2026-06-22T11:00:00
  B260620-120072 | charged twice | 2026-06-22T12:00:00
  B260620-110032 | charged twice | 2026-06-22T14:00:00
  ... and 16 more
  How it was found: From complaint records; keep rows where customer complaints.kind in ['charged twice', 'debited but the till said failed']; report bill_id = customer complaints.bill_id, kind = customer complaints.kind, complaint_ts = customer complaints.complaint_ts.

## S9N14: Join pos_payments to psp_upi_report on rrn to report the final bank status of all 48 UPI timeouts in June.

answered from the ontology layer. (Plan covers: Final bank status from PSP report for all UPI payment attempts that timed out at the till (till_status = 'failed: no response') in June, joined on RRN.)
48 rows (columns: bill_id, attempt, rrn, till_status, psp_status, psp_status_ts):
  B260603-090023 | 1 |  | failed: no response |  | 
  B260604-140026 | 1 |  | failed: no response |  | 
  B260605-040030 | 1 |  | failed: no response |  | 
  B260605-120088 | 1 |  | failed: no response |  | 
  B260606-040056 | 1 |  | failed: no response |  | 
  B260608-010027 | 1 |  | failed: no response |  | 
  B260608-020011 | 1 |  | failed: no response |  | 
  B260609-030032 | 2 |  | failed: no response |  | 
  B260609-040018 | 1 |  | failed: no response |  | 
  B260610-050041 | 1 |  | failed: no response |  | 
  ... and 38 more
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and pos payments.till_status = 'failed: no response'; report bill_id = pos payments.bill_id, attempt = pos payments.attempt, rrn = pos payments.rrn, till_status = pos payments.till_status, psp_status = psp upi report.status, psp_status_ts = psp upi report.status_ts; sorted by bill_id asc.

## S9N15: Our UPI technical decline rate in June was 0.76%, well under 1%—so did we have any UPI reliability incidents?

Part 1: answered from the schema layer. (Plan covers: Count of UPI payment attempts by till status (approved, declined, failed, failed: no response) to compute technical decline rate from till perspective.)
4 rows (columns: till_status, attempts):
  approved | 18384
  declined | 589
  failed | 145
  failed: no response | 48
  How it was found: From payment attempt records; keep rows where pos payments.tender = 'UPI'; group by pos payments.till_status; report till_status = pos payments.till_status, attempts = count of *.
Part 2: answered from the schema layer. (Plan covers: Count of UPI transactions by PSP final status (success, failed, returned) to cross-check technical decline rate from provider perspective.)
3 rows (columns: psp_status, transactions):
  failed | 750
  returned | 6
  success | 18410
  How it was found: From UPI service provider's transaction records; group by psp upi report.status; report psp_status = psp upi report.status, transactions = count of *.
Part 3: answered from the ontology layer. (Plan covers: Joint view of till status and PSP status by RRN to identify discrepancies (e.g., till timeout but PSP success = extra debit; till approved but PSP failed = reliability incident).)
4 rows (columns: till_status, psp_status, count):
  approved | success | 18384
  declined | failed | 589
  failed | failed | 145
  failed: no response |  | 48
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI'; group by pos payments.till_status, psp upi report.status; report till_status = pos payments.till_status, psp_status = psp upi report.status, count = count of *.
Part 4: answered from the schema layer. (Plan covers: Count of UPI-related customer complaints (charged twice, debited but till said failed) as indicator of reliability incidents experienced by customers.)
2 rows (columns: complaint_kind, count):
  charged twice | 23
  debited but the till said failed | 3
  How it was found: From complaint records; keep rows where customer complaints.kind in ['charged twice', 'debited but the till said failed']; group by customer complaints.kind; report complaint_kind = customer complaints.kind, count = count of *.

## S9N16: Why are 17 UPI credits from 20–21 June sitting in suspense, and when can finance recognize them as unclaimed store revenue?

Part 1: answered from the ontology layer. (Plan covers: Shows UPI settlement rows for 20–21 June with credits, gross, net, refunds, MDR to see the 17 credits in context.)
2 rows (columns: settlement_date, upi_credits, gross_inr, net_inr, refunds_inr, mdr_inr):
  2026-06-20 | 824.0 | 510195.41 | 510195.41 | 0.0 | 0.0
  2026-06-21 | 607.0 | 367003.47 | 367003.47 | 0.0 | 0.0
  How it was found: From UPI settlement records; keep rows where day(upi settlements.settlement_date) between 2026-06-20 and 2026-06-21; report settlement_date = day(upi settlements.settlement_date), upi_credits = upi settlements.upi_credits, gross_inr = upi settlements.gross_inr, net_inr = upi settlements.net_inr, refunds_inr = upi settlements.refunds_inr, mdr_inr = upi settlements.mdr_inr; sorted by settlement_date asc.
Part 2: answered from the ontology layer. (Plan covers: Lists UPI payment attempts on 20–21 June with till and PSP statuses by RRN to identify credits not matched to approved payments.)
200 rows (columns: bill_id, rrn, amount_inr, till_status, psp_status, psp_status_ts, payment_day):
  B260620-000001 | 617107012837 | 287.1 | approved | success | 2026-06-20T07:01:28 | 2026-06-20
  B260620-000002 | 617107012838 | 575.17 | approved | success | 2026-06-20T07:03:35 | 2026-06-20
  B260620-000005 | 617107012839 | 136.2 | approved | success | 2026-06-20T07:05:37 | 2026-06-20
  B260620-000006 | 617107012840 | 723.7 | approved | success | 2026-06-20T07:05:33 | 2026-06-20
  B260620-000007 | 617107012841 | 935.03 | approved | success | 2026-06-20T07:06:54 | 2026-06-20
  B260620-000010 | 617107012842 | 142.04 | approved | success | 2026-06-20T07:09:46 | 2026-06-20
  B260620-000011 | 617107012843 | 165.17 | approved | success | 2026-06-20T07:09:09 | 2026-06-20
  B260620-000012 | 617107012844 | 723.52 | approved | success | 2026-06-20T07:10:38 | 2026-06-20
  B260620-000014 | 617107012845 | 322.77 | approved | success | 2026-06-20T07:11:20 | 2026-06-20
  B260620-000015 | 617107012846 | 789.41 | approved | success | 2026-06-20T07:11:47 | 2026-06-20
  ... and 190 more
  How it was found: From payment attempt records; left-join UPI service provider's transaction records on pos payments.rrn = psp upi report.rrn; keep rows where pos payments.tender = 'UPI' and day(pos payments.ts) between 2026-06-20 and 2026-06-21; report bill_id = pos payments.bill_id, rrn = pos payments.rrn, amount_inr = pos payments.amount_inr, till_status = pos payments.till_status, psp_status = psp upi report.status, psp_status_ts = psp upi report.status_ts, payment_day = day(pos payments.ts); sorted by payment_day asc.
Part 3: answered from the ontology layer. (Plan covers: Shows complaints on 20–21 June that may relate to the 17 UPI credits (e.g., double debits awaiting refund).)
bill_id = B260618-110082; rrn = 616918011772; amount_inr = 963.27; kind = charged twice; resolution = refunded after the store matched the credit by hand; complaint_day = 2026-06-20
  How it was found: From complaint records; keep rows where day(customer complaints.complaint_ts) between 2026-06-20 and 2026-06-21; report bill_id = customer complaints.bill_id, rrn = customer complaints.rrn, amount_inr = customer complaints.amount_inr, kind = customer complaints.kind, resolution = customer complaints.resolution, complaint_day = day(customer complaints.complaint_ts); sorted by complaint_day asc.
Part 4: answered from the ontology layer. (Plan covers: Shows UPI refunds requested on 20–21 June to see which credits have already been refunded vs. still in suspense.)
bill_id = B260618-110082; rrn = 616918011772; amount_inr = 963.27; requested_ts = 2026-06-20T11:00:00; completed_ts = 2026-06-22T11:00:00; trigger = customer complaint
  How it was found: From UPI refund records; keep rows where day(upi refunds.requested_ts) between 2026-06-20 and 2026-06-21; report bill_id = upi refunds.bill_id, rrn = upi refunds.rrn, amount_inr = upi refunds.amount_inr, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, trigger = upi refunds.trigger; sorted by requested_ts asc.
Not recorded, so not answered: cause (why): no table records the reason or cause of an event [rule-5]

## S9N17: Did Store 014 meet RBI's 5-day turnaround on all June refunds, given that the median wait was 3 days?

answered from the ontology layer. (Plan covers: List each June UPI refund with its request and completion timestamps and the turnaround in days, to check if all are within the 5-day RBI limit and to verify the median wait.)
23 rows (columns: bill_id, requested_ts, completed_ts, turnaround_days):
  B260605-120088 | 2026-06-06T13:00:00 | 2026-06-08T13:00:00 | 2.0
  B260618-110082 | 2026-06-20T11:00:00 | 2026-06-22T11:00:00 | 2.0
  B260620-110022 | 2026-06-23T17:00:00 | 2026-06-25T17:00:00 | 2.0
  B260620-110055 | 2026-06-23T10:00:00 | 2026-06-25T10:00:00 | 2.0
  B260620-110055 | 2026-06-24T10:00:00 | 2026-06-26T10:00:00 | 2.0
  B260620-120019 | 2026-06-22T18:00:00 | 2026-06-24T18:00:00 | 2.0
  B260620-120047 | 2026-06-22T19:00:00 | 2026-06-24T19:00:00 | 2.0
  B260614-100001 | 2026-06-15T19:00:00 | 2026-06-18T19:00:00 | 3.0
  B260620-120002 | 2026-06-24T10:00:00 | 2026-06-27T10:00:00 | 3.0
  B260620-120016 | 2026-06-23T12:00:00 | 2026-06-26T12:00:00 | 3.0
  ... and 13 more
  How it was found: From UPI refund records; keep rows where upi refunds.requested_ts between 2026-06-01 and 2026-06-30 and upi refunds.completed_ts is not empty; report bill_id = upi refunds.bill_id, requested_ts = upi refunds.requested_ts, completed_ts = upi refunds.completed_ts, turnaround_days = days_between(upi refunds.completed_ts, upi refunds.requested_ts); sorted by turnaround_days asc.
