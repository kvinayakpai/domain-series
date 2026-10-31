-- Store counts: each adjustment is the count minus the book
SELECT * FROM {{ ref('stock_counts') }} WHERE adjustment <> counted - book_before
