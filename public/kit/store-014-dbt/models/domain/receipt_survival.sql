-- Receipt lines whose next count, within a week, took off half or more of what was booked.
WITH latest AS (
  SELECT c.count_ts, c.sku, c.book_before, c.counted, c.adjustment, max(r.received_ts) AS received_ts
  FROM {{ ref('stock_counts') }} c JOIN {{ ref('goods_receipts') }} r ON r.sku_booked = c.sku AND r.received_ts < c.count_ts
   AND r.received_ts >= c.count_ts - INTERVAL 7 DAY
  WHERE c.adjustment < 0 GROUP BY ALL)
SELECT r.shipment_id, r.sscc, r.line, r.received_ts, r.sku_booked AS sku, r.units_booked,
       l.count_ts, l.book_before, l.counted, l.adjustment
FROM latest l JOIN {{ ref('goods_receipts') }} r ON r.sku_booked = l.sku AND r.received_ts = l.received_ts
WHERE -l.adjustment >= 0.5 * r.units_booked
