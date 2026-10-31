-- The gap detector, in SQL. Each warehouse item's usual rate for an open hour is last night's
-- forecast (the 28-day mean of daily sales), times its weekday or weekend level, times its share of
-- the day in that hour, both learned from May. A run of open hours with no sale while the books show
-- stock is flagged once its expected sales pass ln(1000): no sale that long is less likely than 1 in
-- 1,000. Closing time does not break a run, and once a run is flagged one lone unit does not end it:
-- inside a long silence a single sale is as likely a scan error as a sale.
with dc as (select sku from {{ ref('products') }} where flow = 'DC'),
days as (select cast(d as date) as date from range(date '2026-05-04', date '2026-06-29', interval 1 day) t(d)),
hours as (select h from range(7, 22) t(h)),
sold as (
  select sku_scanned as sku, cast(bill_ts as date) as date, hour(bill_ts) as h, sum(qty) as units
  from {{ ref('pos_lines') }} group by all),
grid as (
  select dc.sku, days.date, hours.h, coalesce(s.units, 0) as units
  from dc cross join days cross join hours
  left join sold s on s.sku = dc.sku and s.date = days.date and s.h = hours.h),
daily as (select sku, date, sum(units) as units from grid group by all),
shape as (
  select sku, h, (sum(units) + 0.5) / (sum(sum(units)) over (partition by sku) + 0.5 * 15) as share
  from grid where date < date '2026-06-01' group by sku, h),
level as (
  select sku,
         avg(case when dayofweek(date) not in (0, 6) then units end) / avg(units) as weekday,
         avg(case when dayofweek(date) in (0, 6) then units end) / avg(units) as weekend
  from daily where date < date '2026-06-01' group by sku),
forecast as (
  select sku, date + 1 as date,
         avg(units) over (partition by sku order by date rows between 27 preceding and current row) as per_day
  from daily),
hours_june as (
  select b.sku, b.date, b.h, b.units, b.book,
         f.per_day * (case when dayofweek(b.date) in (0, 6) then l.weekend else l.weekday end) * s.share as expected,
         case when b.units > 0 or b.book <= 0 then 1 else 0 end as breaks
  from {{ ref('hourly_book') }} b
  join forecast f on f.sku = b.sku and f.date = b.date
  join level l on l.sku = b.sku
  join shape s on s.sku = b.sku and s.h = b.h),
runs as (
  select *, sum(breaks) over (partition by sku order by date, h rows unbounded preceding) as run_id
  from hours_june),
silent as (
  select *, cast(date as timestamp) + to_hours(h) as hour_ts,
         sum(expected) over (partition by sku, run_id order by date, h rows unbounded preceding) as expected_so_far
  from runs where breaks = 0),
first_flag as (
  select sku, run_id, min(hour_ts) as start,
         min(hour_ts) filter (where expected_so_far > ln(1000)) as flag_hour
  from silent group by sku, run_id),
breaker as (select sku, run_id, units, book from runs where breaks = 1),
flagged as (select * from first_flag where flag_hour is not null)
select f.sku, f.start, f.flag_hour + interval 1 hour as flag_ts,
       round(s.expected_so_far, 1) as expected_at_flag, s.book as book_at_flag
from flagged f
join silent s on s.sku = f.sku and s.run_id = f.run_id and s.hour_ts = f.flag_hour
-- A run that begins after one lone unit, right after a flagged run, is the same silence.
where not exists (
  select 1 from breaker b join flagged p on p.sku = b.sku and p.run_id = b.run_id - 1
  where b.sku = f.sku and b.run_id = f.run_id and b.units = 1 and b.book > 0)
