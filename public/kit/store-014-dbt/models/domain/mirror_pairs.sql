-- Pairs of corrections in one product family with opposite signs, each at least a case and within
-- 15% of each other in cases, within a week: neighbouring slots, one store count, or one item
-- in both buildings.
SELECT CASE WHEN a.building = b.building THEN 'same building' ELSE 'across buildings' END AS kind,
       a.building AS building_a, a.ts AS ts_a, a.sku AS sku_a, a.slot AS slot_a, a.units AS units_a,
       round(a.cases, 2) AS cases_a, a.value_inr AS value_a,
       b.building AS building_b, b.ts AS ts_b, b.sku AS sku_b, b.slot AS slot_b, b.units AS units_b,
       round(b.cases, 2) AS cases_b, b.value_inr AS value_b
FROM {{ ref('corrections') }} a JOIN {{ ref('corrections') }} b
  ON a.family = b.family AND sign(a.units) = -sign(b.units)
 AND abs(a.cases) >= 1 AND abs(b.cases) >= 1
 AND abs(abs(a.cases) - abs(b.cases)) <= 0.15 * greatest(abs(a.cases), abs(b.cases))
 AND abs(epoch(b.ts) - epoch(a.ts)) <= 7 * 86400
 AND (a.ts < b.ts OR (a.ts = b.ts AND a.sku < b.sku))
WHERE (a.building = b.building AND a.sku <> b.sku
       AND (a.building = 'store' OR (split_part(a.slot, '-', 1) = split_part(b.slot, '-', 1)
            AND split_part(a.slot, '-', 2) = split_part(b.slot, '-', 2)
            AND abs(CAST(split_part(a.slot, '-', 3) AS INTEGER) - CAST(split_part(b.slot, '-', 3) AS INTEGER)) = 1)))
   OR (a.building <> b.building AND a.sku = b.sku)
