-- No item goes longer without a sale than its usual rate allows while the books show stock
select * from {{ ref('silent_runs') }}
