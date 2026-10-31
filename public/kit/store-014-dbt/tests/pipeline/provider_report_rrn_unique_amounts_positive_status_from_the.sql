-- Provider report: RRN unique, amounts positive, status from the allowed list
SELECT rrn, count(*) AS n FROM {{ ref('psp_upi') }} GROUP BY rrn HAVING count(*) > 1 UNION ALL SELECT rrn, 1 FROM {{ ref('psp_upi') }} WHERE amount_inr <= 0 OR status NOT IN ('success', 'failed', 'returned')
