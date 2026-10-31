-- Shelf audits: one status per item per audit, on shelf or empty
SELECT audit_ts, sku, count(*) AS n FROM {{ ref('shelf_audits') }} GROUP BY ALL HAVING count(*) > 1 UNION ALL SELECT audit_ts, sku, 1 FROM {{ ref('shelf_audits') }} WHERE status NOT IN ('on shelf', 'empty')
