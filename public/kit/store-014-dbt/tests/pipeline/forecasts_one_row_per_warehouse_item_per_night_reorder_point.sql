-- Forecasts: one row per warehouse item per night, reorder point below order-up-to
SELECT date, count(*) AS items, max(CASE WHEN reorder_point > order_up_to THEN 1 ELSE 0 END) AS bad FROM {{ ref('forecasts') }} GROUP BY date HAVING count(*) <> (SELECT count(*) FROM {{ ref('products') }} WHERE flow = 'DC') OR bad = 1
