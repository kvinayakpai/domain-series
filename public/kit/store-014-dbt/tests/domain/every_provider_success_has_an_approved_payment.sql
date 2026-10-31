-- Every success in the provider's report has an approved till payment with its RRN
select rrn, initiated_ts, amount_inr, status_ts from {{ ref('psp_upi') }}
where status = 'success' and rrn not in
  (select rrn from {{ ref('till_payments') }} where till_status = 'approved' and rrn is not null)
