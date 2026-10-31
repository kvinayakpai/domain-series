-- Till payments: every bill ends with exactly one approved payment
SELECT bill_id, sum(CASE WHEN till_status = 'approved' THEN 1 ELSE 0 END) AS approved FROM {{ ref('till_payments') }} GROUP BY bill_id HAVING approved <> 1
