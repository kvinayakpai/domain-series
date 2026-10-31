-- No shelf audit finds an item empty while the books show stock
select a.audit_ts, a.sku, b.book from {{ ref('shelf_audits') }} a
join {{ ref('hourly_book') }} b on b.sku = a.sku and b.date = cast(a.audit_ts as date)
  and b.h = greatest(hour(a.audit_ts) - 1, 7)
where a.status = 'empty' and b.book > 0
