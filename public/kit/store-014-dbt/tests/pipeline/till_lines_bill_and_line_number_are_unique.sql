-- Till lines: bill and line number are unique
SELECT bill_id, line, count(*) AS n FROM {{ ref('pos_lines') }} GROUP BY ALL HAVING count(*) > 1
