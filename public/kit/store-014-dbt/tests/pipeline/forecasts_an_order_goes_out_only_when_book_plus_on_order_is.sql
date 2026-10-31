-- Forecasts: an order goes out only when book plus on-order is at or below the reorder point
SELECT * FROM {{ ref('forecasts') }} WHERE ordered_units > 0 AND book_on_hand + on_order > reorder_point
