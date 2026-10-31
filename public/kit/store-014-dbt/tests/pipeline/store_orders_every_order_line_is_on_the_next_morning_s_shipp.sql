-- Store orders: every order line is on the next morning's shipping notice
SELECT o.* FROM {{ ref('store_orders') }} o LEFT JOIN {{ ref('notice_lines') }} n ON n.order_id = o.order_id AND n.sku = o.sku WHERE n.sku IS NULL AND CAST(o.created_ts AS DATE) < (SELECT max(CAST(arrived_ts AS DATE)) FROM {{ ref('shipments') }})
