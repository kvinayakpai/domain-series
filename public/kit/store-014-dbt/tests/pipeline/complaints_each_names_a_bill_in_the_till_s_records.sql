-- Complaints: each names a bill in the till's records
SELECT c.* FROM {{ ref('complaints') }} c WHERE c.bill_id NOT IN (SELECT bill_id FROM {{ ref('till_payments') }})
