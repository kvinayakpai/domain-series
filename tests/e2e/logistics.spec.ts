import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The logistics post and demo quote the world. Every number checked here must still match it.
const data = JSON.parse(readFileSync(new URL('../../src/data/logistics.json', import.meta.url), 'utf8'));
const lai = JSON.parse(readFileSync(new URL('../../src/data/logistics-ai.json', import.meta.url), 'utf8'));
type Scn = (typeof data.scenarios)[number];
const scenario = (key: string): Scn => data.scenarios.find((s: Scn) => s.key === key);
const asIs = scenario('none|label');
const pickScan = scenario('pick_scan|label');
const weigh = scenario('check_weigh|label');
const caseScan = scenario('none|case_scan');
const pct = (v: number) => `${Math.round(v * 100)}%`;
const inr = (v: number) => `₹${Math.abs(Math.round(v)).toLocaleString('en-IN')}`;
const hm = (iso: string) => iso.slice(11, 16);

async function open(page: Page, query = '') {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`demo/${query}`);
  const root = page.locator('[data-logistics-demo]');
  await expect(root).toHaveAttribute('data-ready', 'true');
  return { errors, root };
}

test('the logistics story quotes the world correctly', async ({ page }) => {
  await page.goto('logistics/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'");
  const st = data.story;
  const ep = st.episode;
  const r = ep.responses;
  const k = asIs.kpis;
  const lines = data.records.notice.filter((a: { shipment_id: string }) => a.shipment_id === st.shipment.shipment_id);
  const cases = (sku: string) => lines.find((a: { sku: string }) => a.sku === sku).cases;
  const pick = st.picks.find((p: { sku: string }) => p.sku === st.line.sku);
  const five = st.corrections.find((c: { sku: string }) => c.sku === 'ATTA-WW-5KG');
  const one = st.corrections.find((c: { sku: string }) => c.sku === 'ATTA-WW-1KG');
  const pallet = st.pallets.find((p: { sscc: string }) => p.sscc === st.line.sscc);
  const light = pick.cases_confirmed * (data.case_kg['ATTA-WW-5KG'] - data.case_kg['ATTA-WW-1KG']);
  const m = lai.mirror;
  const expected = [
    `at ${Number(hm(st.shipment.arrived_ts).slice(0, 2))}:${hm(st.shipment.arrived_ts).slice(3)}, twelve minutes into its 06:00–06:30 slot`,
    `${cases('ATTA-WW-5KG')} cases of 5 kg atta, ${cases('ATTA-WW-1KG')} of 1 kg atta, ${cases('RICE-SM-5KG')} of rice and ${cases('SUGAR-1KG')} of sugar`,
    `including ${st.line.units} bags of 5 kg atta`,
    `the ${st.line.cases} bales on line 1 hold 1 kg packs, ${st.actual.units_actual} of them`,
    `says ${pct(k.otif.scorecard)} of June's ${k.shipments} deliveries arrived in the slot and in full, and the warehouse's own report says ${pct(k.otif.dc_report)}`,
    `the truck made the slot on ${k.in_slot} of ${k.shipments} mornings`,
    `found the books at ${five.book_before} bags of 5 kg and the bay empty, and ${one.adjustment} more 1 kg packs than the books showed`,
    `went to slot ${pick.slot} for ${pick.cases_confirmed} cases of 5 kg atta, scanned the slot's label, and took ${pick.cases_confirmed} bales from ${data.slots['ATTA-WW-1KG']}`,
    `held ${st.line.units} bags of 5 kg that did not exist, while ${st.actual.units_actual} packs of 1 kg sat in the backroom`,
    `saw ${ep.book_on_hand_max} bags on the books against a reorder point of ${ep.reorder_point[0]} or ${ep.reorder_point[1]}`,
    `stayed empty for ${ep.empty_open_hours} open hours`,
    `Customers wanted ${ep.lost_units} bags of 5 kg during the gap and could not buy them: ${r.elsewhere} of those became trips to another store, ${r.other_pack} a different pack size and ${r.other_brand} another brand, ${r.delay} shoppers came back later, and ${r.skip} bags were never bought.`,
    `none of June's ${lai.pallets.total} pallets was weighed or case-scanned`,
    `net to about ${inr(st.adjustments_net.value_at_cost_inr)} at cost, against ${inr(m.gross_atta_value_inr)} gross`,
    `fails for all ${lai.tests.domain[3].failing.length} of June's pallets`,
    `returns one row, line ${m.traced_line.line} of the 22 June shipment`,
    `brings OTIF from the records to ${pct(lai.otif.ways.reconciled)}`,
    `the scorecard and the shelf agree at ${pct(pickScan.kpis.otif.scorecard)}`,
    `weighs about ${Math.round(pallet.notice_kg - light)} kg against the ${Math.round(pallet.notice_kg)} kg its notice implies, ${pct(light / pallet.notice_kg)} light`,
    `reaches the store at ${hm(weigh.shipment.arrived_ts)}, outside its slot`,
    `the scorecard falls to ${pct(weigh.kpis.otif.scorecard)}`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(text).toContain('All ten pass');
  expect(lai.tests.generic).toHaveLength(10);
  expect(text).toContain('16 cases short in its 1 kg atta slot on Tuesday and 16 cases over in its 5 kg slot on Thursday');
  expect(st.dc_adjustments.map((a: { cases: number }) => Math.abs(a.cases))).toEqual([16, 16]);
  expect(text).toContain('five mirror pairs');
  expect(m.pairs).toHaveLength(5);
  expect(text).toContain('answers seven questions of seven, against one with the schema alone');
  expect([lai.assistant.score.naive, lai.assistant.score.domain, lai.assistant.score.of]).toEqual([1, 7, 7]);
  expect(text).toContain('ran out at 3:30 on Tuesday afternoon');
  expect(ep.start).toBe('2026-06-23T15:30');
  expect(text).toContain('a day before the store');
  expect(Math.round(m.days_to_store_count - m.days_to_pair)).toBe(1);
  expect(text).toContain('only one customer all week misses a 5 kg bag');
  expect(weigh.kpis.lost_units_after).toBe(1);
  expect(text).toContain(`no customer finds the 5 kg shelf empty, and the scorecard falls to ${pct(caseScan.kpis.otif.scorecard)}`);
  expect(caseScan.kpis.lost_units_after).toBe(0);
  expect(lai.otif.ways.reconciled).toBe(asIs.kpis.otif.at_the_shelf);
  expect(pickScan.kpis.otif.at_the_shelf).toBe(pickScan.kpis.otif.scorecard);
  expect(weigh.kpis.otif.scorecard).toBeLessThan(k.otif.scorecard); // "Two of the three fixes make the headline number worse"
  expect(caseScan.kpis.otif.scorecard).toBeLessThan(k.otif.scorecard);
});

test('the logistics post renders its figures without JavaScript', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('logistics/');
  await expect(page.locator('figure svg[role="img"]:visible')).toHaveCount(1);
  await expect(page.locator('table.docs')).toContainText(`${data.story.actual.units_actual} packs`);
  await expect(page.locator('table.ledger.net')).toContainText(inr(data.story.adjustments_net.value_at_cost_inr));
  await page.goto('logistics/technical/');
  await expect(page.locator('table.four-ways')).toContainText(pct(asIs.kpis.otif.at_the_shelf));
  await expect(page.locator('table.tests tbody tr:not(.group)')).toHaveCount(lai.tests.generic.length + lai.tests.domain.length);
  await expect(page.locator('table.mirror tbody tr')).toHaveCount(lai.mirror.pairs.length);
  await expect(page.locator('table.assistant tbody tr')).toHaveCount(lai.assistant.questions.length);
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

  // The data team's levers.
  await expect(outcome).toContainText(inr(lai.mirror.net_atta_value_inr));
  await root.getByRole('radio', { name: 'Paired' }).check();
  await expect(outcome).toContainText('One mis-pick');
  await expect(outcome).toContainText(`${lai.mirror.traced_line.shipment_id}, line ${lai.mirror.traced_line.line}`);
  const sc = lai.assistant.score;
  await expect(outcome).toContainText(`${sc.naive} of ${sc.of}`);
  await root.getByRole('radio', { name: 'The schema and a domain layer' }).check();
  await expect(outcome).toContainText(`${sc.domain} of ${sc.of}`);
  expect(errors).toEqual([]);
});

test('every logistics view renders, and the tabs work from the keyboard', async ({ page }) => {
  const { errors, root } = await open(page);
  for (const t of ['scorecard', 'tests', 'corrections', 'assistant', 'ops', 'truth']) {
    await root.locator(`[data-persona="${t}"]`).click();
    await expect(root.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(root.locator('[data-panel] .record, [data-panel] .story, [data-panel] table, [data-panel] .run').first()).toBeVisible();
  }
  await root.locator('[data-persona="scorecard"]').click();
  await root.locator('[data-persona="scorecard"]').press('ArrowRight');
  await expect(root.locator('[data-persona="tests"]')).toHaveAttribute('aria-selected', 'true');
  await expect(root.locator('[data-persona="tests"]')).toBeFocused();
  expect(errors).toEqual([]);
});

test('the data tests pass and the tests about the world do not, as the analysis found', async ({ page }) => {
  const { root } = await open(page, '?lg=tests');
  const g = lai.tests.generic;
  await expect(root.locator('[data-outcome]')).toBeVisible();
  await expect(root.locator('[data-panel]')).toContainText(`${g.filter((t: { pass: boolean }) => t.pass).length} of ${g.length}`);
  await expect(root.locator('[data-panel]')).toContainText(`${lai.tests.domain[3].failing.length} of ${lai.pallets.total} pallets`);
  expect(g.every((t: { pass: boolean }) => t.pass)).toBe(true);
  expect(lai.tests.domain.every((t: { pass: boolean }) => !t.pass)).toBe(true);
});

test('the corrections view nets them, then pairs them and traces the pallet line', async ({ page }) => {
  const { root } = await open(page, '?lg=corrections');
  const panel = root.locator('[data-panel]');
  await expect(panel).toContainText(inr(lai.mirror.net_atta_value_inr));
  await expect(panel).toContainText('Investigations opened');
  await root.getByRole('radio', { name: 'Paired' }).check();
  const t = lai.mirror.traced_line;
  await expect(panel).toContainText(`${t.shipment_id}, line ${t.line}`);
  await expect(panel).toContainText(t.sscc);
  await expect(panel).toContainText(`that line held ${t.actual_units} packs`);
  await expect(panel.locator('table tbody tr')).toHaveCount(lai.mirror.pairs.length);
  // Scored: the traced line is the one the answer key says held the wrong packs.
  const key = JSON.parse(readFileSync(new URL('../../public/data/india-grocery/answer-key-logistics.json', import.meta.url), 'utf8'));
  expect([t.shipment_id, t.sscc, t.line]).toEqual([key.story.line.shipment_id, key.story.line.sscc, key.story.line.line]);
  expect(lai.mirror.trace.candidates).toHaveLength(1);
  expect(lai.otif.check.matches).toEqual({ dc_report: true, by_line: true, scorecard: true, reconciled_vs_at_the_shelf: true });
});

test('the assistant answers each question from its plan, and the domain layer changes the verdicts', async ({ page }) => {
  const { root } = await open(page, '?lg=assistant');
  const run = root.locator('.run');
  const q = lai.assistant.questions.find((x: { id: string }) => x.id === 'in_full');
  await expect(run).toContainText(q.naive.answer);
  await root.getByRole('radio', { name: 'The schema and a domain layer' }).check();
  await expect(root.locator('.run')).toContainText(q.domain.answer);
  for (const item of lai.assistant.questions) {
    await root.locator(`[data-q="${item.id}"]`).click();
    await expect(root.locator('.run')).toContainText(item.domain.answer);
    await expect(root.locator('.run code.sql')).toHaveCount(item.domain.plan.length);
  }
  await expect(root.locator('table.scores tbody tr')).toHaveCount(lai.assistant.questions.length);
});

test('what actually happened shows OTIF four ways and the corrections that net to almost nothing', async ({ page }) => {
  const { root } = await open(page, '?lg=truth');
  const table = root.locator('table.four-ways');
  for (const key of ['dc_report', 'by_line', 'scorecard', 'at_the_shelf']) {
    await expect(table).toContainText(pct(asIs.kpis.otif[key]));
  }
  await expect(root.locator('table.ledger.net')).toContainText(inr(data.story.adjustments_net.value_at_cost_inr));
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

test('the logistics companion quotes the analysis and links its notebook', async ({ page, request }) => {
  await page.goto('logistics/technical/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  const m = lai.mirror;
  const t = m.traced_line;
  for (const e of [
    `Netted, the atta corrections come to ₹${m.net_atta_value_inr} at cost`,
    `gross, they come to ₹${m.gross_atta_value_inr.toLocaleString('en-IN')}`,
    `It returns one row: ${t.shipment_id}, pallet ${t.sscc}, line ${t.line}`,
    `The answer key says that line held ${t.actual_units} packs of 1 kg`,
    `${m.days_to_pair.toFixed(1)} days after the truck arrived`,
    `OTIF from the records is ${pct(lai.otif.ways.reconciled)}: ${lai.otif.good.reconciled} of ${lai.otif.out_of.reconciled}`,
    `about ${lai.gap.lost_estimate} bags shoppers could not find`,
    `It returns ${lai.fill.shipped} cases shipped of ${lai.fill.ordered} ordered, ${(lai.fill.by_notice * 100).toFixed(1)}%`,
    `${lai.fill.wrong_item_cases} of the cases shipped on 22 June held 1 kg packs on a 5 kg line. Counting only cases of the right item, the fill rate is ${(lai.fill.right_item * 100).toFixed(1)}%`,
  ]) expect(text, e).toContain(e);
  await expect(page.locator('table.tests tbody tr:not(.group)')).toHaveCount(lai.tests.generic.length + lai.tests.domain.length);
  await expect(page.locator('figure.plan')).toHaveCount(2);
  const colab = page.locator('a[href="https://colab.research.google.com/github/kvinayakpai/domain-series/blob/main/public/notebooks/logistics.ipynb"]');
  await expect(colab).toHaveCount(1);
  expect((await request.get('notebooks/logistics.ipynb')).status()).toBe(200);
  await page.goto('logistics/');
  await expect(page.locator('a[href$="/logistics/technical/"]').first()).toBeVisible();
});
