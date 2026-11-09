import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// KPIs 2 to 6, the rest of the well. Every number the posts quote must match Field 014's records
// (src/data/oil-gas/well-kpis.json from scripts/oil-gas/well.py, and field-014.json), so changing a
// generator fails the build until the prose is updated.
const field = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/field-014.json', import.meta.url), 'utf8'));
const well = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/well-kpis.json', import.meta.url), 'utf8'));
const ws = well.story;
const us = (v: number) => Math.round(v).toLocaleString('en-US');
const words: Record<number, string> = { 3: 'three', 5: 'five', 11: 'eleven', 15: 'fifteen', 16: 'sixteen' };

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

test('production efficiency quotes the plan and the wells correctly', async ({ page }) => {
  const pe = ws.pe;
  const text = await articleText(page, 'production-efficiency/');
  for (const e of [
    `In March 2026 the meter measured ${us(pe.actual_bbl)} barrels`,
    `had March at ${us(pe.plan_bpd)} barrels a day, ${us(pe.plan_bbl)} for the month, so the monthly report showed a production efficiency of ${pe.pe_plan_pct}%`,
    `That plan was set on 14 November 2025, from November's well tests, with a decline of ${pe.plan_decline_pct}% a year and a ${pe.plan_allowance_pct}% allowance for downtime`,
    `the wells could have produced ${us(pe.mpp_bbl)} barrels in March. Against that, production efficiency was ${pe.pe_tests_pct}%`,
    `the well lost ${us(pe.w14_lost_bbl)} barrels, ${pe.w14_lost_pct_of_mpp}% of the field's potential`,
    `${pe.pe_plan_pct}% of the plan was ${pe.pe_tests_pct}% of the field.`,
    `Well 14's ${us(pe.w14_lost_bbl)} barrels would have started the right conversation`,
  ]) expect(text, e).toContain(e);
  expect(pe.plan_set).toBe('2025-11-14'); // "four months old" in March
  // The month's total is the sum of the fiscal meter's daily record, as a reader of the CSV would add it up.
  expect(pe.actual_bbl).toBe(Math.round(Math.round(field.daily.metered.reduce((a: number, b: number) => a + b, 0) * 10) / 10));
});

test('deferred production quotes the loss log correctly', async ({ page }) => {
  const d = ws.deferment;
  const trip = well.loss_log.find((r: { well: string; start: string }) => r.well === 'W-14' && r.start.startsWith('2026-03-19'));
  const text = await articleText(page, 'deferred-production/');
  for (const e of [
    `Its loss log for March 2026 has ${d.entries} entries and ${us(d.logged_bbl)} barrels`,
    `Pump trips account for ${us(d.by_category['ESP trip, restarted'])} barrels, process trips for ${us(d.by_category['Process trip'])}, and a grid dip on 23 March for ${us(d.by_category['Power supply (grid)'])}`,
    `One entry, ${us(d.other_bbl)} barrels, is filed as "Other: under investigation"`,
    `the pump really cost: ${us(d.pump_real_bbl)} barrels in March. ${us(d.other_bbl)} sat under "other", ${trip.deferred_bbl} were filed against a trip on 19 March, and ${us(d.wear_unlogged_bbl)} were never logged at all`,
    `The log put ${us(d.esp_logged_bbl)} barrels on pump trips. One pump cost ${us(d.pump_real_bbl)}.`,
    `${d.other_pct}% of March's logged losses had no cause, and pump trips looked like ${Math.round((d.esp_logged_bbl / d.logged_bbl) * 100)}% of the problem`,
    `Well 14's ${us(d.wear_unlogged_bbl)} barrels were visible from 5 March`,
  ]) expect(text, e).toContain(e);
  expect(d.other_bbl + trip.deferred_bbl + d.wear_unlogged_bbl).toBe(d.pump_real_bbl);
  expect(well.loss_log.some((r: { start: string; category: string }) => r.start.startsWith('2026-03-23') && r.category === 'Power supply (grid)')).toBe(true);
});

test('decline rate quotes the monthly totals correctly', async ({ page }) => {
  const d = ws.decline;
  const text = await articleText(page, 'decline-rate/');
  for (const e of [
    `The meter averaged ${us(d.feb_avg_bpd)} barrels a day in February 2026 and ${us(d.mar_avg_bpd)} in March, a fall of ${Math.abs(d.reported_monthly_pct).toFixed(1)}% in one month`,
    `Annualized, that is a decline of ${d.reported_annual_pct}% a year, against about ${Math.abs(d.usual_monthly_pct).toFixed(0)}% a month from December to February`,
    `the field declined ${Math.abs(d.reservoir_monthly_pct).toFixed(1)}% from February to March, close to its usual pace`,
    `${Math.abs(d.reported_monthly_pct).toFixed(1)}% by the meter, ${Math.abs(d.reservoir_monthly_pct).toFixed(1)}% by the reservoir.`,
    `a field declining at ${d.reported_annual_pct}% a year`,
  ]) expect(text, e).toContain(e);
  const zeroDays = field.daily.wells['W-14'].produced.filter((v: number) => v === 0).length;
  expect(text).toContain(`the well produced nothing for the last ${words[zeroDays]} days of the month`);
});

test('pump run life quotes the pump history correctly', async ({ page }) => {
  const r = ws.run_life;
  const text = await articleText(page, 'pump-run-life/');
  for (const e of [
    `has put ${r.pumps_since_2019} pumps into its sixteen wells since it went on pumps in 2019. ${r.failed_pulled} have failed and been pulled, and they ran ${us(r.avg_reported_days)} days on average, ${r.avg_reported_years} years`,
    `the next three ran ${r.w14_sand_days[0]}, ${r.w14_sand_days[1]} and ${r.w14_sand_days[2]} days`,
    `The fourth went in on 31 July 2025 and stopped on 20 March 2026, after ${r.w14_last_days} days`,
    `${r.avg_reported_years} years on average, ${r.w14_sand_avg_days} days in Well 14.`,
    `Well 14's short runs are 3 of the ${r.failed_pulled} failures`,
    `leaves out the ${r.running} pumps still running, ${words[r.running_over_3y]} of them for more than three years`,
    `the typical pump in the other fifteen wells runs about ${us(r.km_median_others_days)} days`,
    `runs that ended in sand wear averaged ${r.by_cause['sand wear'].avg_days} days, and every other cause averaged more than 1,200`,
  ]) expect(text, e).toContain(e);
  expect(r.w14_last_installed).toBe('2025-07-31');
  for (const [cause, v] of Object.entries(r.by_cause) as [string, { avg_days: number }][]) {
    if (cause !== 'sand wear' && !cause.startsWith('teardown')) expect(v.avg_days, cause).toBeGreaterThan(1200);
  }
});

test('lifting cost quotes the costs and the backlog correctly', async ({ page }) => {
  const l = ws.lifting;
  const m = (v: number) => (Math.round(v / 10000) / 100).toFixed(2);
  const months = well.monthly as { month: string; metered_bbl: number }[];
  const bbl = (k: string) => months.find((x) => x.month === k)!.metered_bbl;
  const text = await articleText(page, 'lifting-cost/');
  for (const e of [
    `spent $${m(l.opex_usd['2026-02'])} million to produce ${us(bbl('2026-02'))} barrels in February 2026 and $${m(l.opex_usd['2026-03'])} million to produce ${us(bbl('2026-03'))} in March`,
    `Its lifting cost went from $${l.usd_per_bbl['2026-02'].toFixed(2)} a barrel to $${l.usd_per_bbl['2026-03'].toFixed(2)}`,
    `would cost $${us(l.workover_usd)}. No rig was free until 9 April`,
    `Add it back and March cost $${l.mar_with_workover.toFixed(2)} a barrel, the dearest month of the year`,
    `overdue maintenance grew from ${l.backlog[1].overdue_orders} work orders, worth about $${us(l.backlog[1].est_cost_usd)}, at the end of February to ${l.backlog[2].overdue_orders}, worth about $${us(l.backlog[2].est_cost_usd)}, at the end of March`,
    `$${l.usd_per_bbl['2026-03'].toFixed(2)} a barrel, with $${us(l.backlog[2].est_cost_usd)} of work waiting.`,
    `Well 14 lost ${us(ws.pe.w14_lost_bbl)} barrels in March`,
  ]) expect(text, e).toContain(e);
  expect(l.rig_free).toBe('2026-04-09');
  expect(l.mar_with_workover).toBeGreaterThan(Math.max(l.usd_per_bbl['2026-01'], l.usd_per_bbl['2026-02']));
  expect(l.usd_per_bbl['2026-03']).toBeLessThan(l.usd_per_bbl['2026-02']);
});
