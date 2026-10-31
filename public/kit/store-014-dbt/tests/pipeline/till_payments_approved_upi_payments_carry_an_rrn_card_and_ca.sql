-- Till payments: approved UPI payments carry an RRN; card and cash carry none
SELECT * FROM {{ ref('till_payments') }} WHERE (tender = 'UPI' AND till_status = 'approved' AND rrn IS NULL) OR (tender <> 'UPI' AND rrn IS NOT NULL)
