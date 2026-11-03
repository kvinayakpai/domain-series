import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The retail post and its companion quote numbers in prose. Each one must still match the world
// (retail.json) and the analysis of its records (retail-ai.json).
const data = JSON.parse(readFileSync(new URL('../../src/data/retail.json', import.meta.url), 'utf8'));
const ai = JSON.parse(readFileSync(new URL('../../src/data/retail-ai.json', import.meta.url), 'utf8'));
const scenario = (key: string) => data.scenarios.find((s: { key: string }) => s.key === key);
const asIs = scenario('off|today');
const story = data.story;
const ep = story.episode;
const hero = ai.forecast.by_sku['ATTA-WW-5KG'];
const pct = (v: number) => `${Math.round(Math.abs(v) * 100)}%`;
const signed = (v: number) => `${v < 0 ? '−' : '+'}${pct(v)}`;
const made = (d: string) => ai.forecast.made_5kg.find((m: { date: string }) => m.date === d);
const week = (k: number) => ai.forecast.series_5kg.slice(k * 7, k * 7 + 7).reduce((a: number, x: { true: number }) => a + x.true, 0);
const option = (label: string) => ai.detector.options.find((o: { label: string }) => o.label === label);
const rerun = (label: string) => data.detectors.find((o: { label: string }) => o.label === label);

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  // Typographic quotes in the page compare equal to plain ones in the expectations.
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

test('the shelf linking post quotes the world and the agents correctly', async ({ page }) => {
  const text = await articleText(page, 'retail/');
  const rec5 = story.kpis.weekly.recorded_sales['ATTA-WW-5KG'];
  const audit = ai.tests.domain[1].failing.find((a: { sku: string }) => a.sku === 'ATTA-WW-5KG');
  const finale = JSON.parse(readFileSync(new URL('../../src/data/finale.json', import.meta.url), 'utf8'));
  const shelf = finale.incidents.find((i: { id: string }) => i.id === 'shelf');
  const runs = data.agents.runs;
  const heroLog = (k: string) => runs[k].log.filter((x: { sku: string }) => x.sku === 'ATTA-WW-5KG');
  const cut = heroLog('naive')[0];
  const [ask1, checked1] = heroLog('domain');
  const ep0 = (k: string) => runs[k].episodes.find((e: { start: string }) => e.start.startsWith('2026-06-10'));
  const seeds = data.agents.seeds.runs;
  const dos = (ep.book_on_hand_max / made('2026-06-10').naive).toFixed(1);
  const expected = [
    `Tuesday 9 June, ${story.misplaced.ts.slice(11, 16)}. Fourteen cases of 5 kg atta from the morning truck are put away behind the rice`,
    `Wednesday 10 June, ${ep.start.slice(11, 16)}. The shelf runs out. The books show ${ep.book_on_hand_max} bags, above the reorder point of ${ep.reorder_point[1]}`,
    `A routine shelf check finds the 5 kg bay empty with ${audit.book} bags on the books`,
    `Shoppers had come for ${ep.lost_units} bags they could not find`,
    `The weekly review opens on 5 kg atta, down ${pct(1 - rec5[1] / rec5[0])}`,
    `On-shelf availability (KPI 2): ${pct(asIs.kpis.osa.system_in_stock)} for June`,
    `with ${ep.book_on_hand_max} bags on the books and none on the shelf`,
    `Days of supply (KPI 7): ${dos} days`,
    `would have flagged it at ${shelf.joined.ts.slice(11, 16)} that day, three open hours after the shelf emptied`,
    `cut the forecast from ${cut.forecast_from.toFixed(1)} bags a day to ${cut.forecast_to.toFixed(1)}`,
    `the shelf was empty for ${Math.round(ep0('domain').empty_open_hours)} open hours instead of ${Math.round(ep0('none').empty_open_hours)}`,
    `5 kg atta lost ${Math.round(seeds.none.mean.hero_lost_units)} bags on average with no agent, ${Math.round(seeds.naive.mean.hero_lost_units)} with the first agent and ${Math.round(seeds.domain.mean.hero_lost_units)} with the second, which held no extra stock and asked for about six shelf checks a month`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(story.misplaced.cases).toBe(14);
  expect(Math.round(ai.detector.hero_flags[0].open_hours_to_flag)).toBe(3);
  expect(ask1.ts).toBe('2026-06-10T22:00'); // "asked for a shelf check at 22:00 on Wednesday"
  expect(checked1.ts).toBe('2026-06-11T08:00'); // "staff found the bags at 08:00 on Thursday"
  expect(runs.naive.checks).toBe(0); // "It checked no shelves"
  expect(data.agents.seeds.n).toBe(40);
  expect(Math.round(seeds.domain.mean.checks)).toBe(6);
  expect(seeds.domain.mean.stock_at_cost_inr).toBeLessThanOrEqual(seeds.none.mean.stock_at_cost_inr);
});

test('the technical companion quotes the analysis correctly and links the notebook', async ({ page, request }) => {
  const text = await articleText(page, 'retail/technical/');
  const hourly = option('hourly, 1 in 1,000');
  const all = ai.forecast.all_items;
  const series = ai.forecast.series_5kg;
  const unconstrained = series.reduce((a: number, x: { recorded: number; imputed: number }) => a + x.recorded + x.imputed, 0);
  const key = JSON.parse(readFileSync(new URL('../../public/data/india-grocery/answer-key-retail.json', import.meta.url), 'utf8'));
  const truth5 = key.truth_daily.filter((t: { sku: string }) => t.sku === 'ATTA-WW-5KG');
  const sum = (k: string) => truth5.reduce((a: number, t: Record<string, number>) => a + t[k], 0);
  const falseAlarms = ai.detector.flags.filter((f: { in_real_gap: boolean }) => !f.in_real_gap).length;
  const expected = [
    `At 1 in 1,000 the detector raises ${hourly.flags} alerts in June and ${hourly.true} are real. The ${falseAlarms} that are not`,
    `looks ${pct(hero.naive_vs_recorded.bias)} too high`,
    `the unconstrained forecast looks worse still, ${pct(hero.aware_vs_recorded.bias)} high`,
    `the store's forecast is ${pct(hero.naive_vs_true.bias)} too low, and the unconstrained version is ${pct(hero.aware_vs_true.bias)} low`,
    `On 28 June the unconstrained forecast stands at ${hero.month_end.aware} bags a day, a little above the ${hero.month_end.true_june_mean}`,
    `comes to ${Math.round(unconstrained)} bags. The answer key has ${sum('true_demand')} bags asked for, counting every visit, and ${sum('base_demand')} counting each shopper once`,
    `osa_books_tills # ${pct(ai.availability.books_and_tills)}`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(text).toContain(`${(all.naive_vs_true.bias * 100).toFixed(1).replace('-', '−')}% to ${(all.aware_vs_true.bias * 100).toFixed(1).replace('-', '−')}%`);
  const colab = page.locator('a[href="https://colab.research.google.com/github/kvinayakpai/domain-series/blob/main/public/notebooks/retail.ipynb"]');
  await expect(colab).toHaveCount(1);
  const nb = await request.get('notebooks/retail.ipynb');
  expect(nb.status()).toBe(200);
  // The post links its companion, and the companion links back.
  await page.goto('retail/');
  await expect(page.locator('a[href$="/retail/technical/"]').first()).toBeVisible();
});

test('the companion renders its tables without JavaScript', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('retail/technical/');
  await expect(page.locator('table.four-ways')).toContainText(pct(asIs.kpis.osa.system_in_stock));
  await expect(page.locator('table.four-ways')).toContainText(pct(ai.availability.books_and_tills));
  await expect(page.locator('table.tests tbody tr:not(.group)')).toHaveCount(ai.tests.generic.length + ai.tests.domain.length);
  await expect(page.locator('table.detectors tbody tr')).toHaveCount(7);
  await expect(page.locator('table.assistant tbody tr')).toHaveCount(ai.assistant.questions.length);
  await expect(page.locator('.assistant-full dt')).toHaveCount(ai.assistant.questions.length);
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
