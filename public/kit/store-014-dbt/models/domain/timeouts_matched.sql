-- Each UPI attempt the till gave up on, matched to the provider's row for it: same amount, a start
-- within five seconds, one to one, nearest first.
WITH orphans AS (
  SELECT p.* FROM {{ ref('psp_upi') }} p WHERE p.rrn NOT IN (SELECT rrn FROM {{ ref('till_payments') }} WHERE rrn IS NOT NULL)),
pairs AS (
  SELECT t.bill_id, t.attempt, t.ts, t.amount_inr, o.rrn, o.status, o.status_ts,
         abs(epoch(o.initiated_ts) - epoch(t.ts)) AS gap_s,
         row_number() OVER (PARTITION BY t.bill_id, t.attempt ORDER BY abs(epoch(o.initiated_ts) - epoch(t.ts))) AS k,
         row_number() OVER (PARTITION BY o.rrn ORDER BY abs(epoch(o.initiated_ts) - epoch(t.ts))) AS j
  FROM {{ ref('till_payments') }} t JOIN orphans o ON o.amount_inr = t.amount_inr
   AND abs(epoch(o.initiated_ts) - epoch(t.ts)) <= 5
  WHERE t.till_status = 'failed: no response')
SELECT bill_id, attempt, ts, amount_inr, rrn, status AS final_status, status_ts, gap_s,
       CASE WHEN status = 'success' THEN 'late credit' WHEN status = 'returned' THEN 'debited and returned'
            ELSE 'never debited' END AS outcome
FROM pairs WHERE k = 1 AND j = 1
