-- No hour has three or more timeouts and a timeout share over 10 times the month's
with h as (select strftime(ts, '%Y-%m-%dT%H:00') as hour, count(*) as upi_attempts,
    sum(case when till_status = 'failed: no response' then 1 else 0 end) as no_answer
  from {{ ref('till_payments') }} where tender = 'UPI' group by all),
m as (select sum(no_answer) / sum(upi_attempts) as share from h)
select h.*, round(h.no_answer / h.upi_attempts, 3) as share from h, m
where h.no_answer >= 3 and h.no_answer / h.upi_attempts > 10 * m.share
