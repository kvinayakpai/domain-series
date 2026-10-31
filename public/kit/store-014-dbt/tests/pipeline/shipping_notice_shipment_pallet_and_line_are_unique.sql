-- Shipping notice: shipment, pallet and line are unique
SELECT shipment_id, sscc, line, count(*) AS n FROM {{ ref('notice_lines') }} GROUP BY ALL HAVING count(*) > 1
