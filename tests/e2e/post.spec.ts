import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The retail post quotes numbers in prose. Each one must still match the world.
const data = JSON.parse(readFileSync(new URL('../../src/data/retail.json', import.meta.url), 'utf8'));
const asIs = data.scenarios.find((s: { key: string }) => s.key === 'off|today');
const alert = data.scenarios.find((s: { key: string }) => s.key === '1d|today');
const routine = data.scenarios.find((s: { key: string }) => s.key === 'off|scanned');
const story = data.story;
const ep = story.episode;
const milk = (f: number) => data.milk.find((m: { factor: number }) => Math.abs(m.factor - f) < 1e-9);
const inr = (v: number) => `₹${Math.round(v).toLocaleString('en-IN')}`;
const pct = (v: number) => `${Math.round(v * 100)}%`;

test('the retail post quotes the world correctly', async ({ page }) => {
  await page.goto('retail/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  const weekly = story.kpis.weekly;
  const rec5 = weekly.recorded_sales['ATTA-WW-5KG'];
  const share = (k: number) => rec5[k] / (rec5[k] + weekly.recorded_sales['ATTA-WW-1KG'][k] + weekly.recorded_sales['ATTA-WW-10KG'][k]);
  const r = ep.responses;
  const expected = [
    `${ep.book_on_hand_min} bags on hand`,
    `${ep.book_on_hand_max} bags against a reorder point of ${ep.reorder_point[0]} or ${ep.reorder_point[1]}`,
    `${story.misplaced.cases} cases of 5 kg atta, ${story.misplaced.units} bags`,
    `empty for ${Math.round(ep.empty_open_hours)} open hours`,
    `sold ${rec5[0]} bags in the first week of June and ${rec5[1]} in the second, down ${Math.round((1 - rec5[1] / rec5[0]) * 100)}%`,
    `from ${story.forecast.before} bags a day before the gap to ${story.forecast.end_recorded_sales}`,
    `${pct(share(0))} of atta units sold in the first week and ${pct(share(1))} in the second`,
    `from ${weekly.store_orders_units[0]} bags to ${weekly.store_orders_units[1]}`,
    `Customers wanted about ${weekly.true_demand[1]} bags that week. The tills recorded ${rec5[1]}.`,
    `Of the ${ep.lost_units} bags customers wanted during the gap and could not buy, ${r.other_brand} became sales of another brand and ${r.other_pack} a different pack size. ${r.elsewhere} became trips to another store, ${r.delay} shoppers came back later, and ${r.skip} bags`,
    `${story.true_demand_per_day.may} bags a day on average in May and ${story.true_demand_per_day.june} in June`,
    `off by ${pct(story.kpis.forecast.wmape_vs_recorded_sales)} in June`,
    `off by ${pct(story.kpis.forecast.wmape_vs_true_demand)}`,
    `forecast at ${story.forecast.end_corrected} bags a day at the end of June, not ${story.forecast.end_recorded_sales}`,
    `${milk(1).expired} pouches expired in June, eating ${inr(milk(1).waste_cost_inr)} of the ${inr(milk(1).gross_margin_inr)}`,
    `more than doubles, to ${inr(milk(0.95).net_inr)}`,
    `rise from ${milk(1).lost} to ${milk(0.95).lost}`,
    `fall from ${Math.round(asIs.kpis.empty_open_hours)} to ${Math.round(alert.kpis.empty_open_hours)}`,
    `fall from ${asIs.kpis.lost_units} to ${alert.kpis.lost_units}`,
    `${pct(data.causes.groups_share['shelf and backroom'] + data.causes.groups_share['store ordering and stock records'])} of those hours started in the store`,
    `${data.record_accuracy.wrong} of ${data.record_accuracy.items} items had wrong records`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(routine.kpis.lost_units).toBe(1); // "Unmet demand for the month falls to a single bag."
  expect(milk(0.95).net_inr / milk(1).net_inr).toBeGreaterThan(2); // "more than doubles"
});

test('the post renders its figures without JavaScript', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('retail/');
  await expect(page.locator('figure svg[role="img"]:visible')).toHaveCount(1);
  await expect(page.locator('table.four-ways')).toContainText(pct(asIs.kpis.osa.system_in_stock));
  await expect(page.locator('table.milk-table tbody tr')).toHaveCount(data.milk.length);
  await ctx.close();
});

test('the post links its videos and slides, and they are served', async ({ page, request }) => {
  await page.goto('retail/');
  await expect(page.locator('#walkthrough video')).toHaveAttribute('poster', /retail-walkthrough-poster\.jpg$/);
  for (const [file, type] of [
    ['media/retail-short.mp4', 'video/mp4'],
    ['media/retail-walkthrough.mp4', 'video/mp4'],
    ['media/retail-slides.pdf', 'application/pdf'],
    ['media/retail-short-poster.jpg', 'image/jpeg'],
    ['media/retail-walkthrough.srt', ''],
  ]) {
    const res = await request.head(file);
    expect(res.status(), file).toBe(200);
    if (type) expect(res.headers()['content-type'], file).toContain(type);
  }
});
