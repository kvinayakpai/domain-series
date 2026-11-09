import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// KPIs 12 to 18, Refinery 014. Every number the posts quote must match the refinery's records
// (src/data/oil-gas/refinery-014.json from scripts/oil-gas/refinery.py).
const ref = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/refinery-014.json', import.meta.url), 'utf8'));
const pipe = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/pipe-014.json', import.meta.url), 'utf8'));
const rs = ref.story;
const us = (v: number) => Math.round(v).toLocaleString('en-US');
const d2 = (v: number) => Math.abs(v).toFixed(2);

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

test('refinery utilization quotes the runs and the slate correctly', async ({ page }) => {
  const u = rs.utilization;
  const text = await articleText(page, 'refinery-utilization/');
  for (const e of [
    `can process ${us(rs.refinery.capacity_bpd)} barrels a day`,
    `In March 2026 it ran at ${u.pct}% of capacity, against ${u.feb_pct}% in February`,
    `Its Gulf crude ran out on 9 March. From 10 March it ran light crude loaded at Fujairah`,
    `Arab Light from Yanbu from 22 March and West African crude from 28 March`,
    `Over the month, ${u.light_share_pct}% of the crude it ran was light, against ${u.plan_light_pct}% in its plan`,
    `until the tank reached its minimum on 24 March. After that it ran at ${rs.diesel.hcu_after_min_pct}% to ${rs.diesel.hcu_after_max_pct}% of capacity`,
    `realised margin for March was $${d2(rs.margin.realised)} a barrel, against $${d2(rs.margin.plan)} in the plan`,
    `${u.pct}% full, half of it on the wrong crude.`,
  ]) expect(text, e).toContain(e);
  expect([u.gulf_out_day, u.yanbu_from, u.waf_from, u.tank_min_day]).toEqual(['2026-03-09', '2026-03-22', '2026-03-28', '2026-03-24']);
  expect(Math.abs(u.light_share_pct - 50)).toBeLessThanOrEqual(2); // "half"
  // The West African crude is the replacement cargo that berthed on 28 March (pipe-014.json).
  expect(pipe.story.ship.berthed.slice(0, 10)).toBe(u.waf_from);
});

test('refining margin walks from the screen to the realised margin correctly', async ({ page }) => {
  const m = rs.margin;
  const prem = -(m.steps.plan_premium + m.steps.crude_premium);
  const text = await articleText(page, 'refining-margin/');
  for (const e of [
    `For March 2026 it averaged $${d2(m.screen)} a barrel`,
    `The realised margin was $${d2(m.realised)}`,
    `Crude premiums: −$${prem.toFixed(2)} a barrel. Light crude bought at short notice cost $${ref.meta.premium_vs_dubai.light.toFixed(2)} over Dubai, against $${ref.meta.premium_vs_dubai.medium.toFixed(2)} for the Gulf crude in the plan`,
    `Freight and war-risk insurance: −$${d2(m.steps.freight)}`,
    `The slate: −$${d2(m.steps.slate)}`,
    `Demurrage on the replacement cargo: −$${d2(m.steps.demurrage)}`,
    `would have earned $${d2(m.plan)}, not $${d2(m.screen)}`,
    `$${d2(m.screen)} on the screen, $${d2(m.realised)} in the refinery.`,
  ]) expect(text, e).toContain(e);
  const walked = m.screen + m.steps.plan_premium + m.steps.crude_premium + m.steps.freight + m.steps.slate + m.steps.demurrage;
  expect(Math.abs(walked - m.realised)).toBeLessThan(0.015);
  expect(m.screen / m.realised).toBeGreaterThan(1.8); // "about twice"
  expect(m.screen / m.realised).toBeLessThan(2.2);
});

test('diesel yield quotes the tank and the yields correctly', async ({ page }) => {
  const d = rs.diesel;
  const text = await articleText(page, 'diesel-yield/');
  for (const e of [
    `made diesel at ${d.yield_pct}% of its crude in March 2026, against a plan of ${d.plan_pct}%`,
    `the yield even rose, to ${d.light_pct}%`,
    `${us(d.vgo_start)} barrels at the start of March`,
    `until the tank reached its minimum of ${us(d.vgo_end)} barrels on 24 March`,
    `ran at ${d.hcu_after_min_pct}% to ${d.hcu_after_max_pct}% of capacity, and the yield was ${d.after_pct}%`,
    `${us(d.vgo_drawn)} barrels of VGO came out of the tank, enough to make ${us(d.diesel_from_tank)} barrels of diesel`,
    `the yield from March's own crude was ${d.own_pct}%`,
    `${d.yield_pct}% on plan, ${d.own_pct}% from March's crude.`,
  ]) expect(text, e).toContain(e);
  expect(d.low_day).toBe('2026-03-24');
});

test('energy intensity quotes the energy figures correctly', async ({ page }) => {
  const e0 = rs.energy;
  const text = await articleText(page, 'energy-intensity/');
  for (const e of [
    `used ${e0.ei_feb.toFixed(3)} gigajoules of energy a barrel in February 2026, when it ran at ${e0.feb_util_pct}% of capacity, and ${e0.ei_mar.toFixed(3)} in March at ${e0.mar_util_pct}%: ${Math.abs(e0.ei_change_pct)}% less`,
    `February used ${Math.abs(e0.feb_vs_expected_pct).toFixed(1)}% less than expected and March ${e0.mar_over_expected_pct.toFixed(1)}% more`,
    `From 12 March the crude unit's preheat train fouled`,
    `Over the month that came to ${us(e0.extra_gj)} gigajoules`,
    `${Math.abs(e0.ei_change_pct)}% less a barrel, ${e0.mar_over_expected_pct.toFixed(1)}% more than it should have used.`,
  ]) expect(text, e).toContain(e);
  expect(e0.feb_vs_expected_pct).toBeLessThan(0);
  expect(e0.foul_from).toBe('2026-03-12');
});

test('mechanical availability quotes the pump trips correctly', async ({ page }) => {
  const a = rs.availability;
  const t = ref.trips;
  const text = await articleText(page, 'mechanical-availability/');
  for (const e of [
    `reported a mechanical availability of ${a.pct}% for March 2026`,
    `four hours on the diesel hydrotreater on 25 March`,
    `at 04:12 on 8 March on high vibration at a bearing, at 22:40 on 17 March with a leaking mechanical seal, and at 13:05 on 29 March on high vibration at the same bearing`,
    `Each time P-101B started within nine seconds`,
    `P-101B carried the crude unit alone for ${a.spare_hours} hours, about seven days`,
    `At 06:00 on 31 March, with P-101A still under repair, P-101B raised its own vibration alarm`,
    `${a.pct}% available, on a spare that ran alone for seven days.`,
  ]) expect(text, e).toContain(e);
  expect(t.map((x: { trip: string }) => x.trip)).toEqual(['2026-03-08T04:12', '2026-03-17T22:40', '2026-03-29T13:05']);
  expect(t[2].back).toBeNull();
  expect(Math.round(a.spare_days)).toBe(7);
  const dht = ref.unplanned[0];
  expect((new Date(`${dht.to}:00Z`).getTime() - new Date(`${dht.from}:00Z`).getTime()) / 3600000).toBeCloseTo(4.25, 2);
});

test('turnaround quotes the reformer turnaround correctly', async ({ page }) => {
  const t = rs.turnaround;
  const text = await articleText(page, 'turnaround/');
  for (const e of [
    `at 06:00 on 23 February, planned to restart at 18:00 on 15 March with ${us(t.planned_orders)} work orders`,
    `The war began five days in`,
    `management decided on 3 March to hold the restart date`,
    `The reformer restarted on schedule after ${t.days} days, at $${(t.actual_usd / 1e6).toFixed(1)} million against a budget of $${(t.budget_usd / 1e6).toFixed(1)} million`,
    `Opening the unit had found ${t.found_orders} more jobs. Of the ${us(t.planned_orders + t.found_orders)} in all, ${t.deferred_orders} were deferred to a later date, ${t.deferred_pct_of_scope}% of the scope`,
    `They included ${t.deferred_sce} of the ${t.planned_sce} safety-critical inspections in the plan`,
    `On time, with ${t.deferred_orders} jobs left undone.`,
  ]) expect(text, e).toContain(e);
  expect([t.start, t.planned_end, t.actual_end]).toEqual(['2026-02-23T06:00', '2026-03-15T18:00', '2026-03-15T18:00']);
});

test('process safety quotes the events and the backlog correctly', async ({ page }) => {
  const s = rs.safety;
  const text = await articleText(page, 'process-safety/');
  for (const e of [
    `had no Tier 1 or Tier 2 process safety event in March 2026, and none since 4 November 2025`,
    `Overdue safety-critical inspections rose from ${s.overdue_feb} at the end of February to ${s.overdue_mar} at the end of March: ${rs.turnaround.deferred_sce} deferred from the reformer turnaround, and ${s.overdue_mar - s.overdue_feb - rs.turnaround.deferred_sce} more that fell due`,
    `rose from ${s.tier3_feb} to ${s.tier3_mar}`,
    `Zero events, ${s.overdue_mar} overdue inspections.`,
  ]) expect(text, e).toContain(e);
  expect(s.last_tier2).toBe('2025-11-04');
  const kinds = (ref.tier3 as { event: string }[]).map((x) => x.event.split(':')[0]);
  expect(kinds.filter((k) => k.startsWith('desalter')).length).toBe(2);
  expect(kinds.filter((k) => k.startsWith('overhead water pH')).length).toBe(2);
  expect(ref.tier3.length).toBe(s.tier3_mar);
});
