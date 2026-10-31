-- Book stock: one row per item per day, never negative
{{ config(severity='warn') }}
SELECT date, sku, book_on_hand_close FROM {{ ref('inventory_book') }} WHERE book_on_hand_close < 0 UNION ALL SELECT date, NULL, count(*) FROM {{ ref('inventory_book') }} GROUP BY date HAVING count(*) <> (SELECT count(*) FROM {{ ref('products') }})
