-- Store orders: every automatic order matches that night's forecast row
SELECT o.* FROM {{ ref('store_orders') }} o LEFT JOIN {{ ref('forecasts') }} f ON f.sku = o.sku AND f.date = CAST(o.created_ts AS DATE) AND f.ordered_units = o.units WHERE o.reason = 'auto' AND f.sku IS NULL
