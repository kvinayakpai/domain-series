-- Till payments: bill and attempt are unique
SELECT bill_id, attempt, count(*) AS n FROM {{ ref('till_payments') }} GROUP BY ALL HAVING count(*) > 1
