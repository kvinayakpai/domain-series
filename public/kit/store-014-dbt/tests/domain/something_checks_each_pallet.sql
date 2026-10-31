-- Something other than the pick checks what is on each pallet (a scale weight or a case scan)
select sscc, shipment_id, weight_check from {{ ref('pallets') }}
where weight_check = 'not weighed'
  and sscc not in (select sscc from {{ ref('goods_receipts') }} where receipt_method like 'case scan%')
