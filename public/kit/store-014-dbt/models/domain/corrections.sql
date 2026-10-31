-- Every count correction in both buildings, in units and in cases.
SELECT 'warehouse' AS building, a.adjusted_ts AS ts, a.sku, split_part(a.sku, '-', 1) AS family, a.slot,
       a.units, CAST(a.cases AS DOUBLE) AS cases, a.value_at_cost_inr AS value_inr, a.reason AS why
FROM {{ ref('dc_adjustments') }} a
UNION ALL
SELECT 'store', c.count_ts, c.sku, split_part(c.sku, '-', 1), NULL, c.adjustment,
       c.adjustment / CAST(p.case_units AS DOUBLE), round(c.adjustment * p.cost_inr, 2), c.trigger
FROM {{ ref('stock_counts') }} c JOIN {{ ref('products') }} p USING (sku)
WHERE c.adjustment <> 0 AND c.count_ts > TIMESTAMP '2026-06-01 07:00'
