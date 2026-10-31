-- Pick confirmations: one per notice line, same order, item and cases, confirmed by a scan
SELECT n.*, p.cases_confirmed FROM {{ ref('notice_lines') }} n LEFT JOIN {{ ref('picks') }} p USING (shipment_id, line) WHERE p.sku IS NULL OR p.sku <> n.sku OR p.order_id <> n.order_id OR p.cases_confirmed <> n.cases OR p.confirmed_by IS NULL OR p.cases_confirmed > p.cases_ordered
