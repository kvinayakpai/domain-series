-- Shipping notice: every item and barcode is in the product master, units are cases times the case size
SELECT n.* FROM {{ ref('notice_lines') }} n LEFT JOIN {{ ref('products') }} p ON p.sku = n.sku AND p.gtin = n.gtin WHERE p.sku IS NULL OR n.units <> n.cases * p.case_units
