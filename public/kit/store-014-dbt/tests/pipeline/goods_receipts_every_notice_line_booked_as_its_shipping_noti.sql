-- Goods receipts: every notice line booked, as its shipping notice says
SELECT n.*, r.sku_booked, r.units_booked FROM {{ ref('notice_lines') }} n LEFT JOIN {{ ref('goods_receipts') }} r USING (shipment_id, sscc, line) WHERE r.grn_id IS NULL OR r.asn_sku <> n.sku OR r.asn_units <> n.units OR r.sku_booked <> r.asn_sku OR r.units_booked <> r.asn_units
