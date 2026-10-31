-- Till payments: amounts positive, tender and status from the allowed lists
SELECT * FROM {{ ref('till_payments') }} WHERE amount_inr <= 0 OR tender NOT IN ('UPI', 'card', 'cash') OR till_status NOT IN ('approved', 'declined', 'failed', 'failed: no response')
