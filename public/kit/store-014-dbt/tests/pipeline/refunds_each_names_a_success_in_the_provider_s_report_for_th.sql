-- Refunds: each names a success in the provider's report, for the same amount
SELECT r.* FROM {{ ref('refunds') }} r LEFT JOIN {{ ref('psp_upi') }} p USING (rrn) WHERE p.rrn IS NULL OR p.status <> 'success' OR p.amount_inr <> r.amount_inr
