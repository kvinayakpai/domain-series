import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The logistics post and demo quote the world. Every number checked here must still match it.
const data = JSON.parse(readFileSync(new URL('../../src/data/logistics.json', import.meta.url), 'utf8'));
type Scn = (typeof data.scenarios)[number];
const scenario = (key: string): Scn => data.scenarios.find((s: Scn) => s.key === key);
const asIs = scenario('none|label');
const pickScan = scenario('pick_scan|label');
const weigh = scenario('check_weigh|label');
const caseScan = scenario('none|case_scan');
const pct = (v: number) => `${Math.round(v * 100)}%`;
const inr = (v: number) => `₹${Math.abs(Math.round(v)).toLocaleString('en-IN')}`;
const hm = (iso: string) => iso.slice(11, 16);
const dayOf = (iso: string) => Number(iso.slice(8, 10));

async function open(page: Page, query = '') {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`demo/${query}`);
  const root = page.locator('[data-logistics-demo]');
  await expect(root).toHaveAttribute('data-ready', 'true');
  return { errors, root };
}

test('the logistics post quotes the world correctly', async ({ page }) => {
  await page.goto('logistics/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  const st = data.story;
  const ep = st.episode;
  const r = ep.responses;
  const k = asIs.kpis;
  const lines = data.records.notice.filter((a: { shipment_id: string }) => a.shipment_id === st.shipment.shipment_id);
  const cases = (sku: string) => lines.find((a: { sku: string }) => a.sku === sku).cases;
  const pick = st.picks.find((p: { sku: string }) => p.sku === st.line.sku);
  const five = st.corrections.find((c: { sku: string }) => c.sku === 'ATTA-WW-5KG');
  const one = st.corrections.find((c: { sku: string }) => c.sku === 'ATTA-WW-1KG');
  const late = asIs.by_shipment.filter((x: { in_slot: boolean }) => !x.in_slot).map((x: { arrived_ts: string }) => dayOf(x.arrived_ts));
  const short = asIs.by_shipment.filter((x: { in_full_notice: boolean }) => !x.in_full_notice).map((x: { arrived_ts: string }) => dayOf(x.arrived_ts));
  const pallet = st.pallets.find((p: { sscc: string }) => p.sscc === st.line.sscc);
  const light = pick.cases_confirmed * (data.case_kg['ATTA-WW-5KG'] - data.case_kg['ATTA-WW-1KG']);
  const expected = [
    `${cases('ATTA-WW-5KG')} cases of 5 kg atta, ${cases('ATTA-WW-1KG')} of 1 kg atta, ${cases('RICE-SM-5KG')} of rice and ${cases('SUGAR-1KG')} of sugar`,
    `including ${st.line.units} bags of 5 kg atta`,
    `the ${st.line.cases} bales on line 1 hold 1 kg packs, ${st.actual.units_actual} of them`,
    `TRK-07 left at ${hm(st.shipment.dispatched_ts)} and arrived at ${hm(st.shipment.arrived_ts)}`,
    `made the slot on ${k.in_slot} of ${k.shipments} mornings in June`,
    `${pct(k.otif.scorecard)} of June’s ${k.shipments} deliveries`,
    `late on ${late[0]} and ${late[1]} June and short on ${short[0]} and ${short[1]} June`,
    `The books said ${five.book_before} bags and the bay held none`,
    `found ${one.adjustment} more 1 kg packs`,
    `${inr(five.adjustment * data.costs['ATTA-WW-5KG'])} of 5 kg atta gone and ${inr(one.adjustment * data.costs['ATTA-WW-1KG'])} of 1 kg`,
    `went to slot ${pick.slot} for ${pick.cases_confirmed} cases of 5 kg atta`,
    `took ${pick.cases_confirmed} bales from ${data.slots['ATTA-WW-1KG']}`,
    `saw ${ep.book_on_hand_max} bags on the books against a reorder point of ${ep.reorder_point[0]} or ${ep.reorder_point[1]}`,
    `empty for ${ep.empty_open_hours} open hours`,
    `Customers wanted ${ep.lost_units} bags of 5 kg during the gap and could not buy them, ${inr(ep.lost_value_inr)} at the shelf price. ${r.elsewhere} of those became trips to another store, ${r.other_pack} a different pack size and ${r.other_brand} another brand. ${r.delay} shoppers came back later, and ${r.skip} bags were never bought.`,
    `net to about ${inr(st.adjustments_net.value_at_cost_inr)}`,
    `shipped ${k.out_of.by_line} order lines to Store 014 in June and got one wrong`,
    `the scorecard and the shelf agree at ${pct(pickScan.kpis.otif.scorecard)}`,
    `weighs about ${Math.round(pallet.notice_kg - light)} kg against the ${Math.round(pallet.notice_kg)} kg its notice implies, ${pct(light / pallet.notice_kg)} light`,
    `leaves at ${hm(weigh.shipment.dispatched_ts)} instead of ${hm(st.shipment.dispatched_ts)} and reaches the store at ${hm(weigh.shipment.arrived_ts)}`,
    `the scorecard falls to ${pct(weigh.kpis.otif.scorecard)}`,
    `books ${st.actual.units_actual} packs of 1 kg instead of ${st.line.units} bags of 5 kg`,
    `The scorecard falls to ${pct(caseScan.kpis.otif.scorecard)} here too`,
    st.line.sscc,
    st.line.gtin,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(ep.start).toBe('2026-06-23T15:30'); // "ran out at 3:30 on Tuesday afternoon"
  expect(text).toContain('ran out at 3:30 on Tuesday afternoon');
  expect(pickScan.kpis.otif.at_the_shelf).toBe(pickScan.kpis.otif.scorecard);
  expect(weigh.kpis.lost_units_after).toBe(1); // "Only one customer all week misses a 5 kg bag"
  expect(caseScan.kpis.lost_units_after).toBe(0); // "no customer finds the 5 kg shelf empty"
  expect(caseScan.kpis.empty_open_hours_after).toBe(0);
  expect(weigh.kpis.otif.scorecard).toBeLessThan(k.otif.scorecard); // "Two of the three fixes make the headline number worse"
  expect(caseScan.kpis.otif.scorecard).toBeLessThan(k.otif.scorecard);
});

test('the logistics post renders its figures without JavaScript', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('logistics/');
  await expect(page.locator('figure svg[role="img"]:visible')).toHaveCount(1);
  await expect(page.locator('table.docs')).toContainText(`${data.story.actual.units_actual} packs`);
  await expect(page.locator('table.four-ways')).toContainText(pct(asIs.kpis.otif.at_the_shelf));
  await expect(page.locator('table.ledger')).toContainText(inr(data.story.adjustments_net.value_at_cost_inr));
  await ctx.close();
});

test('logistics outcome numbers come from the world, and the controls change them', async ({ page }) => {
  const { errors, root } = await open(page);
  const outcome = root.locator('[data-outcome]');
  await expect(outcome).toContainText(pct(asIs.kpis.otif.scorecard));
  await expect(outcome).toContainText(String(asIs.kpis.empty_open_hours_after));
  await expect(outcome).toContainText(String(asIs.kpis.lost_units_after));

  await root.getByRole('radio', { name: 'Weigh every pallet' }).check();
  await expect(outcome).toContainText(pct(weigh.kpis.otif.scorecard));
  await expect(outcome).toContainText(String(weigh.kpis.lost_units_after));

  await root.getByRole('radio', { name: 'As today', exact: true }).check();
  await root.getByRole('radio', { name: 'Scan every case', exact: true }).check();
  await expect(outcome).toContainText(pct(caseScan.kpis.otif.scorecard));
  expect(errors).toEqual([]);
});

test('every logistics persona renders, and the tabs work from the keyboard', async ({ page }) => {
  const { errors, root } = await open(page);
  for (const t of ['dc', 'transport', 'receiving', 'scorecard', 'stock', 'truth']) {
    await root.locator(`[data-persona="${t}"]`).click();
    await expect(root.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(root.locator('[data-panel] .record, [data-panel] .story').first()).toBeVisible();
  }
  await root.locator('[data-persona="dc"]').click();
  await root.locator('[data-persona="dc"]').press('ArrowRight');
  await expect(root.locator('[data-persona="transport"]')).toHaveAttribute('aria-selected', 'true');
  await expect(root.locator('[data-persona="transport"]')).toBeFocused();
  expect(errors).toEqual([]);
});

test('what actually happened shows OTIF four ways and the corrections that net to almost nothing', async ({ page }) => {
  const { root } = await open(page, '?lg=truth');
  const table = root.locator('table.four-ways');
  for (const key of ['dc_report', 'by_line', 'scorecard', 'at_the_shelf']) {
    await expect(table).toContainText(pct(asIs.kpis.otif[key]));
  }
  await expect(root.locator('table.ledger')).toContainText(inr(data.story.adjustments_net.value_at_cost_inr));
  await expect(root.locator('[data-panel]')).toContainText(`${data.story.episode.lost_units} bags they could not buy`);
});

test('the logistics records drawer reveals the wrong line, and the downloads exist', async ({ page, request }) => {
  const { root } = await open(page);
  await root.getByText('The records behind it').click();
  await root.getByRole('button', { name: 'Shipping notices, 20–28 June' }).click();
  await expect(root.locator('[data-records] table')).toBeVisible();
  await root.getByLabel('Show what the records hide').check();
  await expect(root.locator('[data-records] .gap').first()).toContainText(`Really ${data.story.actual.units_actual}`);
  const links = await root.locator('.downloads a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')));
  expect(links.length).toBeGreaterThanOrEqual(10);
  for (const href of links) {
    const res = await request.get(href!.replace('/domain-series/', ''));
    expect(res.status(), href!).toBe(200);
  }
});

test('the logistics post links its videos and slides, and they are served', async ({ page, request }) => {
  await page.goto('logistics/');
  await expect(page.locator('#walkthrough video')).toHaveAttribute('poster', /logistics-walkthrough-poster\.jpg$/);
  await expect(page.locator('.media-links a[href$="logistics-slides.pdf"]')).toHaveCount(1);
  for (const [file, type] of [
    ['media/logistics-short.mp4', 'video/mp4'],
    ['media/logistics-walkthrough.mp4', 'video/mp4'],
    ['media/logistics-slides.pdf', 'application/pdf'],
    ['media/logistics-short-poster.jpg', 'image/jpeg'],
    ['media/logistics-walkthrough-poster.jpg', 'image/jpeg'],
    ['media/logistics-walkthrough.srt', ''],
    ['media/logistics-short.srt', ''],
  ]) {
    const res = await request.head(file);
    expect(res.status(), file).toBe(200);
    if (type) expect(res.headers()['content-type'], file).toContain(type);
  }
});
