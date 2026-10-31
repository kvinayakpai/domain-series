-- Till lines: keys present, quantities and prices positive
SELECT * FROM {{ ref('pos_lines') }} WHERE bill_id IS NULL OR bill_ts IS NULL OR sku_scanned IS NULL OR qty <= 0 OR unit_price <= 0
