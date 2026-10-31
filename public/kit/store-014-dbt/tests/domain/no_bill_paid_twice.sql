-- No bill is paid twice, once timed-out attempts are matched to the provider's report
select * from {{ ref('extra_charges') }}
