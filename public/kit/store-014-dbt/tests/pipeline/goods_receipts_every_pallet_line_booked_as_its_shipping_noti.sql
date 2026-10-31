-- Goods receipts: every pallet line booked as its shipping notice says
SELECT * FROM {{ ref('goods_receipts') }} WHERE sku_booked <> asn_sku OR units_booked <> asn_units
