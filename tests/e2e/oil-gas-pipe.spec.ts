import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// KPIs 7 to 11, the pipe and the ship. Every number the posts quote must match the records
// (src/data/oil-gas/pipe-014.json from scripts/oil-gas/pipe.py), so changing the generator fails the
// build until the prose is updated.
const field = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/field-014.json', import.meta.url), 'utf8'));
const pipe = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/pipe-014.json', import.meta.url), 'utf8'));
const ps = pipe.story;
const us = (v: number) => Math.round(v).toLocaleString('en-US');
const dayOf = (iso: string) => Number(iso.slice(8, 10));

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

test('throughput quotes the water in the crude correctly', async ({ page }) => {
  const t = ps.throughput;
  const text = await articleText(page, 'throughput/');
  for (const e of [
    `The pipeline's report for March 2026 shows ${us(t.gross_bbl)} barrels moved, about ${us(t.gross_bpd)} a day`,
    `At 16:00 on ${dayOf(t.fault_from)} March, the burner on one of Field 014's two heater-treaters`,
    `until the burner was fixed at 12:00 on ${dayOf(t.fault_to)} March the crude leaving the field carried ${t.fault_avg_bsw_pct}% water on average, against ${t.bsw_base_pct}% normally and a limit of ${t.spec_pct}% at the refinery`,
    `On ${dayOf(t.worst_day)} March, ${t.worst_water_bbl} of the ${us(t.worst_gross_bbl)} barrels the pipe moved were water`,
    `${us(t.net_bbl)} barrels of oil and ${us(t.water_bbl)} of water`,
    `${us(t.gross_bbl)} barrels moved. ${us(t.water_bbl)} of them were water.`,
    `read about ${ps.tank.lab_bsw_avg_pct}% water all month`,
    `${t.fault_avg_bsw_pct}% at the field and ${ps.tank.lab_bsw_avg_pct}% at the refinery`,
    `would have counted ${us(t.water_bbl)} barrels of water as crude`,
  ]) expect(text, e).toContain(e);
  expect(t.fault_from).toBe('2026-03-11T16:00');
  expect(t.fault_to).toBe('2026-03-21T12:00');
  expect(t.net_bbl).toBe(Math.round(Math.round(field.daily.metered.reduce((a: number, b: number) => a + b, 0) * 10) / 10));
  expect(pipe.meta.days.length).toBe(31);
});

test('loss and gain quotes the receipt meter correctly', async ({ page }) => {
  const l = ps.loss_gain;
  const text = await articleText(page, 'loss-and-gain/');
  for (const e of [
    `Its alarm band is ±${l.tolerance_pct.toFixed(2)}% a day. In March 2026 every day was inside it, between +${l.min_pct.toFixed(2)}% and +${l.max_pct.toFixed(2)}%`,
    `But all ${l.days_positive} days were gains. The receipt meter had been proved on 26 February, and since then it had read about ${l.bias_pct}% high`,
    `Its March proving, due on 26 March, waited for the prover, which was away for its own calibration until 6 April`,
    `the refinery's meter counted ${us(l.gain_bbl)} barrels the pipeline never carried`,
    `on this pipeline that rule fires on ${dayOf(l.first_alert_7_days)} March`,
    `${l.days_inside} days inside tolerance, all ${l.days_positive} the same way.`,
  ]) expect(text, e).toContain(e);
  expect(l.days_inside).toBe(31);
  expect(l.days_positive).toBe(31);
  expect([l.last_proving, l.proving_due, l.prover_back]).toEqual(['2026-02-26', '2026-03-26', '2026-04-06']);
  expect(2 ** 31).toBeGreaterThan(2e9); // "about a one in two billion chance"
  expect(2 ** 31).toBeLessThan(2.5e9);
  expect(1 / 2 ** 7).toBeLessThan(0.01); // seven gains in a row: "less than 1%"
});

test('tank stock accuracy quotes T-104 correctly', async ({ page }) => {
  const k = ps.tank;
  const text = await articleText(page, 'tank-stock-accuracy/');
  for (const e of [
    `never more than ${k.max_abs_diff_pct}% apart, inside the refinery's 0.5% limit, and on 31 March they were ${k.diff_pct_31}% apart: ${us(k.book_31)} barrels by the book and ${us(k.gauge_net_31)} by the gauge`,
    `found ${us(k.dip_free_water_31)} barrels of free water at the bottom of T-104. The probe that measures the water had failed on 2 March`,
    `The tank held ${us(k.true_oil_31)} barrels of oil, more than 2,000 fewer than either record`,
    `a receipt meter that read about ${ps.loss_gain.bias_pct}% high, and took its water from a sampler at the top of the line that read ${k.lab_bsw_avg_pct}% while the field was sending up to ${ps.throughput.worst_bsw_pct}%`,
    `believed T-104 held about 2,000 barrels of oil more than it did`,
  ]) expect(text, e).toContain(e);
  expect(k.max_abs_diff_pct).toBeLessThan(0.5);
  expect(Math.min(k.book_over_true_bbl, k.gauge_over_true_bbl)).toBeGreaterThan(2000);
  expect(Math.max(k.book_over_true_bbl, k.gauge_over_true_bbl)).toBeLessThan(2500);
  expect(k.probe_failed).toBe('2026-03-02');
});

test('methane intensity quotes the inventory and the leak correctly', async ({ page }) => {
  const m = ps.methane;
  const text = await articleText(page, 'methane-intensity/');
  for (const e of [
    `produces about ${m.gor} cubic feet of gas with each barrel of oil`,
    `puts the field at ${m.inventory_t} tonnes of methane a month`,
    `that is a methane intensity of ${m.mi_reported_pct.toFixed(2)}%`,
    `At 11:10 on 14 March a satellite passed over and saw a plume at the compressor station, which it estimated at ${m.satellite.kg_h} kilograms an hour, give or take ${m.satellite.uncertainty_pct}%`,
    `since the compressor restarted after maintenance at 15:00 on 6 March. Measured on site at ${m.leak_kg_h} kilograms of methane an hour, the valve was isolated and replaced at 18:30 on 16 March`,
    `In ten days it released ${m.leak_t.toFixed(0)} tonnes of methane, ${m.leak_x_inventory} times the month's estimate, and March's methane intensity was ${m.mi_real_pct.toFixed(1)}%`,
    `${m.mi_reported_pct.toFixed(2)}% on paper, ${m.mi_real_pct.toFixed(1)}% in the air.`,
    `rose from ${m.ua_before_pct}% of production before the leak to ${m.ua_leak_pct}% while it ran`,
    `would have reported ${m.mi_reported_pct.toFixed(2)}%`,
  ]) expect(text, e).toContain(e);
  expect(m.satellite.ts).toBe('2026-03-14T11:10');
  expect([m.leak_from, m.leak_to]).toEqual(['2026-03-06T15:00', '2026-03-16T18:30']);
  expect(m.leak_hours / 24).toBeGreaterThan(9.5);
  expect(m.leak_hours / 24).toBeLessThan(10.5);
});

test('ship waiting time quotes the replacement cargo correctly', async ({ page }) => {
  const s = ps.ship;
  const text = await articleText(page, 'ship-waiting-time/');
  for (const e of [
    `The port's report shows an average waiting time of ${s.port_avg_reported_days} days for the month`,
    `anchored at 05:50 on 24 March and tendered its notice of readiness at 06:00`,
    `The port's schedule gave the cargo a berthing window from 18:00 on 27 March, and it berthed at 09:40 on 28 March. The report counts ${s.reported_wait_days.toFixed(1)} days of waiting, from the window`,
    `From its notice of readiness, the ship waited ${s.real_wait_days.toFixed(1)} days. Laytime ran out at midnight on 25 March, and the refinery owed ${s.demurrage_days.toFixed(2)} days of demurrage at $${us(s.demurrage_usd_day)} a day: $${us(s.demurrage_usd)}`,
    `${s.reported_wait_days.toFixed(1)} days by the port's schedule, ${s.real_wait_days.toFixed(1)} days by the ship's clock.`,
  ]) expect(text, e).toContain(e);
  expect([s.arrived, s.nor, s.window, s.berthed, s.laytime_end]).toEqual(['2026-03-24T05:50', '2026-03-24T06:00', '2026-03-27T18:00', '2026-03-28T09:40', '2026-03-26T00:00']);
  expect(s.notice_h).toBe(6);
});
