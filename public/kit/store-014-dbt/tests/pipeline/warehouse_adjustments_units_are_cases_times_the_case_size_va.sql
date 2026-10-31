-- Warehouse adjustments: units are cases times the case size, value is units at cost
SELECT a.* FROM {{ ref('dc_adjustments') }} a JOIN {{ ref('products') }} p USING (sku) WHERE a.units <> a.cases * p.case_units OR abs(a.value_at_cost_inr - a.units * p.cost_inr) > 0.01
