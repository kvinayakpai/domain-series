-- Every extra charge comes back within 5 days of the debit (refunds as of the review, 29 June 09:00)
select e.*, r.completed_ts from {{ ref('extra_charges') }} e
left join {{ ref('refunds') }} r on r.rrn = e.rrn and r.completed_ts <= timestamp '2026-06-29 09:00'
where r.rrn is null or r.completed_ts > e.debited_ts + interval 5 day
