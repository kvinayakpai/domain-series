-- Settlements: net is gross minus refunds and fees
SELECT * FROM {{ ref('settlements') }} WHERE abs(net_inr - (gross_inr - refunds_inr - mdr_inr)) > 0.01
