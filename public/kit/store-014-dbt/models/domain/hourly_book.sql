-- The books as the store's system holds them at the end of each June open hour, for warehouse items:
-- the night before's close (on 1 June, the morning's count), plus receipts and count corrections as
-- they happen, minus the till's sales hour by hour. The retail companion rebuilds it the same way.
with dc as (select sku from {{ ref('products') }} where flow = 'DC'),
days as (select cast(d as date) as date from range(date '2026-06-01', date '2026-06-29', interval 1 day) t(d)),
hours as (select h from range(7, 22) t(h)),
sold as (
  select sku_scanned as sku, cast(bill_ts as date) as date, hour(bill_ts) as h, sum(qty) as units
  from {{ ref('pos_lines') }} group by all),
starts as (
  select sku, date + 1 as date, book_on_hand_close as book from {{ ref('inventory_book') }}
  union all
  select sku, cast(count_ts as date), counted from {{ ref('stock_counts') }}
  where count_ts = timestamp '2026-06-01 05:45'),
events as (
  select sku_booked as sku, received_ts as ts, units_booked as units from {{ ref('goods_receipts') }}
  union all
  select sku, count_ts, adjustment from {{ ref('stock_counts') }}
  where count_ts > timestamp '2026-06-01 06:00' and hour(count_ts) < 22),
grid as (
  select dc.sku, days.date, hours.h, coalesce(s.units, 0) as units, st.book as start_book
  from dc cross join days cross join hours
  join starts st on st.sku = dc.sku and st.date = days.date
  left join sold s on s.sku = dc.sku and s.date = days.date and s.h = hours.h)
select g.sku, g.date, g.h, g.units,
       g.start_book
       + coalesce((select sum(e.units) from events e where e.sku = g.sku and cast(e.ts as date) = g.date
                   and e.ts < cast(g.date as timestamp) + to_hours(g.h + 1)), 0)
       - sum(g.units) over (partition by g.sku, g.date order by g.h) as book
from grid g
