-- Every UPI payment the till approved is a success in the provider's report, for the same amount
SELECT t.* FROM {{ ref('till_payments') }} t LEFT JOIN {{ ref('psp_upi') }} p USING (rrn) WHERE t.tender = 'UPI' AND t.till_status = 'approved' AND (p.rrn IS NULL OR p.status <> 'success' OR p.amount_inr <> t.amount_inr)
