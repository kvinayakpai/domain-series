-- Every receipt survives the next count
select * from {{ ref('receipt_survival') }}
