import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The Oil & Gas season's four linking posts. Every number they quote must match the records and
// the linking experiment (src/data/oil-gas/linking.json from scripts/oil-gas/linking.py), so a
// change to any generator fails the build until the prose is updated.
const read = (f: string) => JSON.parse(readFileSync(new URL(`../../src/data/oil-gas/${f}`, import.meta.url), 'utf8'));
const field = read('field-014.json');
const ws = read('well-kpis.json').story;
const pipe = read('pipe-014.json');
const ps = pipe.story;
const refinery = read('refinery-014.json');
const rs = refinery.story;
const link = read('linking.json');
const s = field.story;
const us = (v: number) => Math.round(v).toLocaleString('en-US');
const dayOf = (iso: string) => Number(iso.slice(8, 10));
const joinOf = (id: string) => link.joins.find((j: { id: string }) => j.id === id);
const foundOf = (id: string) => link.found.find((f: { id: string }) => f.id === id);

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

test('the well linking post quotes Field 014 and the forty Marches correctly', async ({ page }) => {
  const w = link.well;
  const m = w.march;
  const text = await articleText(page, 'upstream/');
  for (const e of [
    `Well 14, the field's best well, is tested at ${s.w14_test.oil_bpd} barrels a day`,
    `**Thursday ${dayOf(s.pump.wear_from)} March.** Well 14's pump starts to wear`.replace(/\*\*/g, ''),
    `The test separator goes out of service until ${dayOf(s.separator.out_to)} March`,
    `${us(m.flag_allocated)} barrels against ${us(m.flag_vfm)}`,
    `The morning report shows Well 14 at ${us(s.w14_18mar.allocated)} barrels. It produced ${us(s.w14_18mar.produced)}.`,
    `no rig is free until ${dayOf(ws.lifting.rig_free)} April`,
    `Well 14 at ${us(s.w14_18mar.allocated)} barrels on 18 March`,
    `${ws.pe.pe_plan_pct}% of the plan`,
    `Against what the wells could produce, ${ws.pe.pe_tests_pct}%`,
    `${us(ws.deferment.esp_logged_bbl)} barrels lost to pump trips, and ${us(ws.deferment.other_bbl)} under "other". The pump cost ${us(ws.deferment.pump_real_bbl)}, and ${us(ws.deferment.wear_unlogged_bbl)} of them were never logged`,
    `${Math.abs(ws.decline.reported_monthly_pct).toFixed(1)}% in a month, ${ws.decline.reported_annual_pct}% a year`,
    `The reservoir declined ${Math.abs(ws.decline.reservoir_monthly_pct)}%`,
    `${ws.run_life.avg_reported_years} years on average, while Well 14's last four pumps averaged ${ws.run_life.w14_sand_avg_days} days`,
    `$${ws.lifting.usd_per_bbl['2026-03'].toFixed(2)} a barrel, a little cheaper than February`,
    `the $${us(ws.lifting.workover_usd)} workover waited for April`,
    `Joining the two would have flagged the pump on ${dayOf(m.flag)} March, nine days before it stopped`,
    `after ${ws.run_life.w14_sand_days.join(', ').replace(/, (\d+)$/, ' and $1')} days, and the fourth had run ${ws.run_life.w14_last_days}`,
    `the rule fired on ${dayOf(m.flag)} March`,
    `about ${Math.round(m.test_produced / 50) * 50} barrels a day on ${dayOf(m.test_day)} March, against the ${m.last_test_bpd} on the report`,
    `The rule also flagged Well 02 for three days`,
    `a rig arrives ${w.rig_lead_min} to ${w.rig_lead_max} days after it is booked`,
    `the first agent lost ${us(w.a_lost_mean)} barrels of Well 14's oil on average between 1 March and 30 April. The second lost ${us(w.b_lost_mean)}, about a third less, because it booked its rig ${w.days_earlier_mean} days sooner`,
    `It did better in all forty runs`,
  ]) expect(text, e).toContain(e);
  expect(m.days_before_stop).toBe(9);
  expect(m.test_days_before_stop).toBe(7); // "a week before the pump stopped"
  expect(m.separator_out).toBe(true);
  expect(m.other_well_flagged).toBe('W-02');
  expect(m.other_flag_days).toBe(3);
  expect(w.runs).toBe(40);
  expect(w.b_better_runs).toBe(40);
  expect(w.fired_runs).toBe(40); // one extra well test a month
  expect(w.saved_pct).toBeGreaterThanOrEqual(30); // "about a third"
  expect(w.saved_pct).toBeLessThanOrEqual(37);
  // Well 02: "about 8% below its last test" on the days the rule flagged it.
  const w2 = field.daily.wells['W-02'];
  const gap = 1 - w2.produced[4] / w2.test_rate[4];
  expect(Math.round(gap * 100)).toBe(8);
  // The forty Marches are published, one row a run.
  const csv = readFileSync(new URL('../../public/data/field-014/agent-forty-marches.csv', import.meta.url), 'utf8').trim().split('\n');
  expect(csv.length).toBe(41);
  const rows = csv.slice(1).map((r) => r.split(','));
  const mean = (k: number) => rows.reduce((a, r) => a + Number(r[k]), 0) / rows.length;
  expect(Math.round(mean(13))).toBe(w.a_lost_mean);
  expect(Math.round(mean(14))).toBe(w.b_lost_mean);
});

test('the pipe and ship linking post quotes the records and the replay correctly', async ({ page }) => {
  const L = link.pipe;
  const text = await articleText(page, 'midstream/');
  for (const e of [
    `The day before it read ${us(pipe.daily.t104[0].free_water_probe)} barrels of free water`,
    `It leaks about ${ps.methane.leak_kg_h} kilograms of methane an hour`,
    `every one inside the ±${ps.loss_gain.tolerance_pct.toFixed(2)}% band. It has read about ${ps.loss_gain.bias_pct}% high`,
    `Until it is fixed at 12:00 on ${dayOf(ps.throughput.fault_to)} March, the crude leaving the field carries ${ps.throughput.fault_avg_bsw_pct}% water on average`,
    `keeps reading about ${ps.tank.lab_bsw_avg_pct}%`,
    `The valve is replaced at 18:30 on ${dayOf(ps.methane.leak_to)} March, after ${Math.round(ps.methane.leak_t)} tonnes of methane`,
    `the ship berths at 09:40 on ${dayOf(ps.ship.berthed)} March`,
    `The prover is away for its own calibration until ${dayOf(ps.loss_gain.prover_back)} April`,
    `The month-end dip finds ${us(ps.tank.dip_free_water_31)} barrels of free water in T-104`,
    `${us(ps.throughput.gross_bbl)} barrels, a steady month. ${us(ps.throughput.water_bbl)} of them were water`,
    `All 31 were gains: ${us(ps.loss_gain.gain_bbl)} barrels the pipeline never carried`,
    `${ps.methane.mi_reported_pct}%, from emission factors. With the leak, ${ps.methane.mi_real_pct}%`,
    `${ps.ship.reported_wait_days} days for the replacement cargo, by the port's schedule. From its notice, ${ps.ship.real_wait_days} days and $${us(ps.ship.demurrage_usd)} of demurrage`,
    `The two were apart for ten days`,
    `from ${ps.methane.ua_before_pct}% of production to ${L.methane.ua_pct}% on ${dayOf(L.methane.ua_day)} March`,
    `The rules would have flagged the dead probe on ${dayOf(L.tank.probe_flag)} March, the leak on ${dayOf(L.methane.ua_day)} March and the meter on ${dayOf(L.loss_gain.alert)} March`,
    `the crew would have replaced the valve on ${dayOf(L.methane.fixed_with_rule)} March, and K-2 would have released about ${Math.round(L.methane.leak_t_with_rule)} tonnes of methane instead of ${Math.round(L.methane.leak_t)}`,
    `from ${dayOf(L.loss_gain.alert) + 1} March would have kept ${us(L.loss_gain.phantom_kept_out_bbl)} of the ${us(L.loss_gain.phantom_bbl)} phantom barrels`,
  ]) expect(text, e).toContain(e);
  expect(L.water.days).toBe(10);
  expect(L.water.from).toBe('2026-03-12');
  expect(L.tank.probe_flag).toBe(ps.tank.probe_failed);
  expect(ps.loss_gain.days_positive).toBe(31);
  expect(0.5 ** 7).toBeLessThan(0.01); // seven gains in a row, by chance
  expect(refinery.tier3.filter((t: { event: string }) => t.event.includes('desalter')).length).toBe(2); // "upset the desalter twice"
  // The replay list: five rules, each with a date.
  await expect(page.locator('.replay-row')).toHaveCount(5);
  await expect(page.locator('.replay-row').first()).toContainText(`KPI 7, Throughput`);
});

test('the refinery linking post quotes Refinery 014 and the replay correctly', async ({ page }) => {
  const L = link.refinery;
  const text = await articleText(page, 'downstream/');
  for (const e of [
    `It can process ${us(rs.refinery.capacity_bpd)} barrels a day`,
    `which holds about ${L.tank.cover_days} days of feed at that rate`,
    `${rs.turnaround.deferred_orders} jobs are deferred, ${rs.turnaround.deferred_sce} of them safety-critical inspections`,
    `the hydrocracker drops to ${rs.diesel.hcu_after_min_pct}% to ${rs.diesel.hcu_after_max_pct}% of capacity`,
    `${rs.utilization.pct}%, the best month of the year`,
    `$${rs.margin.screen.toFixed(2)} a barrel on the screen. Refinery 014 earned $${rs.margin.realised.toFixed(2)}`,
    `${rs.diesel.yield_pct}%, on plan. From March's own crude, ${rs.diesel.own_pct}%`,
    `${Math.abs(rs.energy.ei_change_pct)}% less energy a barrel. Against what the same runs should use, ${rs.energy.mar_over_expected_pct.toFixed(1)}% more`,
    `${rs.availability.pct}%. P-101A tripped three times, and P-101B ran alone for ${rs.availability.spare_hours} hours`,
    `with ${rs.turnaround.deferred_orders} jobs deferred`,
    `Overdue safety-critical inspections rose from ${rs.safety.overdue_feb} to ${rs.safety.overdue_mar}`,
    `leaving ${rs.turnaround.deferred_sce} safety-critical inspections for later`,
    `with ${rs.safety.overdue_mar} inspections overdue`,
    `On ${dayOf(L.tank.flag)} March, the VGO tank's level said the hydrocracker had about ${L.tank.cover_days} days of feed left`,
    `On ${dayOf(L.energy.flag)} March, a model of what the same runs should use`,
    `On 17 March, the trip log, read by equipment tag, showed P-101A failing twice in ten days`,
  ]) expect(text, e).toContain(e);
  expect(refinery.trips.length).toBe(3);
  expect(L.pump.flag).toBe('2026-03-17T22:40');
  expect((new Date(`${L.pump.flag}:00Z`).getTime() - new Date(`${L.pump.first}:00Z`).getTime()) / 86400000).toBeLessThan(10);
  expect(rs.utilization.light_share_pct).toBe(50); // "Half the crude"
  expect(rs.turnaround.deferred_sce / rs.safety.overdue_mar).toBeGreaterThan(0.5); // "most of the backlog"
  expect(L.slate.flag).toBe('2026-03-10');
  expect(rs.utilization.gulf_out_day).toBe('2026-03-09');
  await expect(page.locator('.replay-row')).toHaveCount(7);
  await expect(page.locator('.replay')).toContainText(`$${refinery.meta.premium_vs_dubai.light.toFixed(2)} over Dubai`);
});

test('the finale quotes the joins, the map and the days correctly', async ({ page }) => {
  const text = await articleText(page, 'well-to-refinery/');
  const apart = (id: string) => joinOf(id).rows - joinOf(id).agree;
  for (const e of [
    `eleven joins in all`,
    `Three of the eleven agree on every row`,
    `Well 14's pump data parted from its allocation for twelve days`,
    `were apart for ten`,
    `The probe and the dip disagreed by ${us(ps.tank.dip_free_water_31)} barrels`,
    `The gas balance showed K-2's leak for eleven days`,
    `the trip log showed three trips that never reached the downtime log`,
    `Well 14's pump shows ${foundOf('pump').days_sooner} days before it stopped, and K-2's leak ${foundOf('leak').days_sooner} days before the satellite saw it`,
    `The VGO tank shows ${foundOf('vgo').days_sooner} days before the hydrocracker's feed drum alarmed, and P-101A ${foundOf('p101').days_sooner} days before its spare's own alarm`,
    `The dead probe shows ${foundOf('probe').days_sooner} days before the month-end dip, and the meter reading high ${foundOf('meter').days_sooner} days before the next proving`,
    `cut Well 14's lost barrels by about a third across forty simulated Marches`,
    `about 65% of 11 business questions`,
  ]) expect(text, e).toContain(e);
  expect(link.joins.length).toBe(11);
  expect(link.summary.always).toBe(3);
  expect(link.summary.always_agree).toBe(true);
  expect(link.summary.worlds_disagree).toBe(true);
  expect(apart('alloc-vfm')).toBe(12);
  expect(apart('water')).toBe(10);
  expect(apart('gas')).toBe(11);
  expect(joinOf('downtime-trips').rows).toBe(3);
  expect(joinOf('downtime-trips').agree).toBe(0);
  expect(joinOf('fiscal-receipt').same_way).toBe(31);
  expect(link.summary.days_sooner_min).toBe(8);
  expect(link.summary.days_sooner_max).toBe(30);
  // The join table and the map.
  await expect(page.locator('.og-joins tbody tr:not(.group)')).toHaveCount(11);
  await expect(page.locator('.og-map tr.kpi-row')).toHaveCount(18);
  await expect(page.locator('.og-map')).toContainText('the pump’s own data, every day');
});

test('the linking posts have their part line, flag the narrator, and page within the season', async ({ page }) => {
  for (const [i, slug] of ['upstream', 'midstream', 'downstream', 'well-to-refinery'].entries()) {
    await page.goto(`${slug}/`);
    await expect(page.locator('.post-domain'), slug).toHaveText(`Oil & Gas · Linking the KPIs: ${i + 1} of 4`);
    const plain = (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'");
    const flagged = plain.indexOf("I (Vinayak's AI Assistant)");
    expect(flagged, slug).toBeGreaterThan(-1);
    expect(plain.match(/\bI\b(?! \(Vinayak)/)?.index ?? Infinity, slug).toBeGreaterThan(flagged);
  }
  await page.goto('upstream/');
  await expect(page.locator('.pager a[href$="/process-safety/"]')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/midstream/"]')).toHaveCount(1);
  await page.goto('well-to-refinery/');
  await expect(page.locator('.pager a')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/downstream/"]')).toHaveCount(1);
});
