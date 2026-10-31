-- Till lines: every item and barcode is in the product master
SELECT l.* FROM {{ ref('pos_lines') }} l LEFT JOIN {{ ref('products') }} p ON l.sku_scanned = p.sku AND l.gtin_scanned = p.gtin WHERE p.sku IS NULL
