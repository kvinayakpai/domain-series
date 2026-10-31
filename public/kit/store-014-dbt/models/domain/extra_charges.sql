-- Late credits on bills the customer then paid again.
SELECT m.bill_id, m.rrn, m.amount_inr, m.ts AS debited_ts, m.status_ts AS credited_ts,
       a.tender AS paid_again_by, a.ts AS paid_again_ts
FROM {{ ref('timeouts_matched') }} m
JOIN {{ ref('till_payments') }} a ON a.bill_id = m.bill_id AND a.till_status = 'approved'
WHERE m.outcome = 'late credit'
