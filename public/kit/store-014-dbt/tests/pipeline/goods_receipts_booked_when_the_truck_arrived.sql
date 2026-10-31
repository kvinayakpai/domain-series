-- Goods receipts: booked when the truck arrived
SELECT r.* FROM {{ ref('goods_receipts') }} r JOIN {{ ref('shipments') }} s USING (shipment_id) WHERE r.received_ts <> s.arrived_ts
