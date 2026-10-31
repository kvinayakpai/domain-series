-- Till lines: line amount is quantity times price
SELECT * FROM {{ ref('pos_lines') }} WHERE abs(line_amount - qty * unit_price) > 0.005
