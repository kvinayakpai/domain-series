-- Daily sales reconcile with the till lines
WITH t AS (SELECT CAST(bill_ts AS DATE) AS date, sku_scanned AS sku, sum(qty) AS units FROM {{ ref('pos_lines') }} GROUP BY ALL) SELECT d.date, d.sku, d.units_sold, t.units FROM {{ ref('daily_sales') }} d LEFT JOIN t ON t.date = d.date AND t.sku = d.sku WHERE d.units_sold <> coalesce(t.units, 0)
