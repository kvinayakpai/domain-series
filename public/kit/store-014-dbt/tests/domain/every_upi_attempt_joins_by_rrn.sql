-- Every UPI attempt at the till joins the provider's final status by RRN
select bill_id, attempt, ts, amount_inr from {{ ref('till_payments') }} where till_status = 'failed: no response'
