-- No warehouse item's weekly sales halve from one week to the next
select sku, sum(case when date between '2026-06-01' and '2026-06-07' then units_sold end) as week1,
  sum(case when date between '2026-06-08' and '2026-06-14' then units_sold end) as week2
from {{ ref('daily_sales') }} join {{ ref('products') }} using (sku) where flow = 'DC' group by sku
having week2 < 0.5 * week1
