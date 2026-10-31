-- Stock counts agree with the books within 2%
select count_ts, sku, book_before, counted, adjustment, trigger from {{ ref('stock_counts') }}
where abs(adjustment) > greatest(1, 0.02 * book_before)
