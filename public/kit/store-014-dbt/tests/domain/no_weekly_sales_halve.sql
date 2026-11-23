-- No warehouse item's weekly sales halve from one week to the next
select sku, sum(case when date between '{{ var('window_start') }}' and '{{ var('week1_end') }}' then units_sold end) as week1,
  sum(case when date between '{{ var('week2_start') }}' and '{{ var('week2_end') }}' then units_sold end) as week2
from {{ ref('daily_sales') }} join {{ ref('products') }} using (sku) where flow = 'DC' group by sku
having week2 < 0.5 * week1
