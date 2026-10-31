-- Shipments: arrival after dispatch, a 30-minute slot
SELECT * FROM {{ ref('shipments') }} WHERE arrived_ts <= dispatched_ts OR slot_end - slot_start <> INTERVAL 30 MINUTE
