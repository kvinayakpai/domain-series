import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

const data = JSON.parse(readFileSync(new URL('../../src/data/retail.json', import.meta.url), 'utf8'));
const ai = JSON.parse(readFileSync(new URL('../../src/data/retail-ai.json', import.meta.url), 'utf8'));
const scenario = (key: string) => data.scenarios.find((s: { key: string }) => s.key === key);
const fmt = (n: number) => Math.round(n).toLocaleString('en-IN');
const pct = (v: number) => `${Math.round(v * 100)}%`;
const hero = ai.forecast.by_sku['ATTA-WW-5KG'];
type Question = { id: string; question: string; naive: { answer: string; right: boolean }; domain: { answer: string; right: boolean } };

// The demo page holds more than one demo, so every locator is scoped to the retail one.
async function open(page: Page, query = '') {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`demo/${query}`);
  const root = page.locator('[data-retail-demo]');
  await expect(root).toHaveAttribute('data-ready', 'true');
  return { errors, root };
}

test('the outcome tiles come from the analysis and the world, and each lever moves its own', async ({ page }) => {
  const { errors, root } = await open(page);
  const outcome = root.locator('[data-outcome]');
  await expect(outcome).toContainText(hero.month_end.naive.toFixed(1));
  await expect(outcome).toContainText(`${ai.assistant.score.naive} of ${ai.assistant.score.of}`);
  await expect(outcome).toContainText(fmt(scenario('off|today').kpis.lost_units));

  await root.getByRole('radio', { name: 'Unconstrained demand' }).check();
  await expect(outcome).toContainText(hero.month_end.aware.toFixed(1));
  await root.getByRole('radio', { name: 'The schema and a domain layer' }).check();
  await expect(outcome).toContainText(`${ai.assistant.score.domain} of ${ai.assistant.score.of}`);

  await root.getByRole('radio', { name: 'Hourly gap detector' }).check();
  const gap = scenario('gap|today');
  await expect(outcome).toContainText(fmt(gap.kpis.lost_units));
  await expect(outcome).toContainText(`${gap.dc.checks} alerts across seven items, ${gap.dc.flags_in_real_gaps} at a real gap`);
  await root.getByRole('radio', { name: 'Scan every case into a bin' }).check();
  await expect(outcome).toContainText(fmt(scenario('gap|scanned').kpis.lost_units));
  expect(gap.kpis.lost_units).toBeLessThan(scenario('off|today').kpis.lost_units);
  expect(errors).toEqual([]);
});

test('every view renders, and the tabs work from the keyboard', async ({ page }) => {
  const { errors, root } = await open(page);
  const panel = root.locator('[data-panel]');
  const views: [string, string][] = [
    ['dashboard', '[data-panel] svg'], ['tests', 'table.tests'], ['forecast', '[data-panel] svg'],
    ['assistant', '.run code.sql'], ['detector', 'table.hours'], ['truth', '[data-panel] svg'],
  ];
  for (const [t, sel] of views) {
    await root.locator(`[data-persona="${t}"]`).click();
    await expect(root.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(root.locator(sel).first()).toBeVisible();
    await expect(panel.locator('p.context')).toBeVisible();
  }
  await root.locator('[data-persona="dashboard"]').click();
  await root.locator('[data-persona="dashboard"]').press('ArrowRight');
  await expect(root.locator('[data-persona="tests"]')).toHaveAttribute('aria-selected', 'true');
  await expect(root.locator('[data-persona="tests"]')).toBeFocused();
  expect(errors).toEqual([]);
});

test('the data tests pass and the tests about the world fail, as the analysis found', async ({ page }) => {
  const { root } = await open(page, '?persona=tests');
  const passed = ai.tests.generic.filter((t: { pass: boolean }) => t.pass).length;
  const panel = root.locator('[data-panel]');
  await expect(panel).toContainText(`${passed} of ${ai.tests.generic.length}`);
  await expect(panel).toContainText(`0 of ${ai.tests.domain.length}`);
  await expect(panel.locator('table.tests td.no')).toHaveCount(ai.tests.generic.length - passed + ai.tests.domain.length);
  await expect(panel).toContainText(`Fails: ${ai.tests.domain[0].failing.length} runs, among them 5 kg atta, 39 open hours`);
});

test('the forecast is scored two ways, and the unconstrained one looks worse on recorded sales', async ({ page }) => {
  const { root } = await open(page, '?persona=forecast');
  const panel = root.locator('[data-panel]');
  const signed = (x: number) => `${x > 0 ? '+' : '−'}${Math.abs(Math.round(x * 100))}%`;
  await expect(panel).toContainText(signed(hero.naive_vs_recorded.bias));
  await expect(panel).toContainText(signed(hero.naive_vs_true.bias));
  await root.getByRole('radio', { name: 'Unconstrained demand' }).check();
  await expect(panel).toContainText(signed(hero.aware_vs_recorded.bias));
  await expect(panel).toContainText(signed(hero.aware_vs_true.bias));
  await expect(panel).toContainText(`${ai.forecast.order_up_to_month_end.aware[1]} bags`);
  expect(hero.aware_vs_recorded.bias).toBeGreaterThan(hero.naive_vs_recorded.bias);
  expect(Math.abs(hero.aware_vs_true.bias)).toBeLessThan(Math.abs(hero.naive_vs_true.bias));
});

test('the assistant answers each question from its plan, and the domain layer changes the verdicts', async ({ page }) => {
  const { root } = await open(page, '?persona=assistant');
  const run = root.locator('.run');
  for (const q of ai.assistant.questions as Question[]) {
    await root.locator(`.questions [data-q="${q.id}"]`).click();
    await expect(root.locator(`.questions [data-q="${q.id}"]`)).toHaveAttribute('aria-pressed', 'true');
    await expect(run.locator('.answer-text')).toHaveText(q.naive.answer);
    await expect(run.locator('.verdict strong')).toHaveText(q.naive.right ? 'Right.' : 'Wrong.');
  }
  await root.getByRole('radio', { name: 'The schema and a domain layer' }).check();
  await root.locator('.questions [data-q="why"]').click();
  const why = (ai.assistant.questions as Question[]).find((q) => q.id === 'why')!;
  await expect(run.locator('.answer-text')).toHaveText(why.domain.answer);
  await expect(run.locator('.verdict strong')).toHaveText('Right.');
  await expect(root.locator('.questions .mark.ok')).toHaveCount(ai.assistant.score.domain);
  await root.getByText('What the domain layer adds to the schema').click();
  await expect(root.locator('pre.yaml')).toContainText('v_censored_hours');
});

test('the gap detector grid matches the analysis, by item and threshold', async ({ page }) => {
  const { root } = await open(page, '?persona=detector');
  const grid = root.locator('table.hours');
  await expect(grid.locator('tbody tr')).toHaveCount(28);
  await expect(grid.locator('tbody td')).toHaveCount(28 * 15);
  const g = ai.detector.grid['ATTA-WW-5KG'];
  const count = (s: string) => [...s].filter((c) => c === '1').length;
  await expect(grid.locator('td.c')).toHaveCount(count(g.censored['0.001']));
  await expect(grid.locator('td.a')).toHaveCount(g.runs['0.001'].length);
  await expect(grid.locator('td.k')).toHaveCount(count(g.no_stock));
  await root.locator('[data-alpha="0.01"]').click();
  const oil = ai.detector.grid['OIL-SUN-1L'];
  await root.locator('[data-item="OIL-SUN-1L"]').click();
  await expect(root.locator('table.hours td.a')).toHaveCount(oil.runs['0.01'].length);
  const opt = ai.detector.options.find((o: { alpha?: number }) => o.alpha === 0.01);
  await expect(root.locator('[data-panel] .tiles')).toContainText(`${opt.true} of ${opt.flags}`);
  await expect(root.locator('table.alerts')).toContainText('Stocked: a false alarm');
  await root.getByLabel('Show the answer key').uncheck();
  await expect(root.locator('table.hours td.e')).toHaveCount(0);
  await expect(root.locator('table.alerts')).not.toContainText('false alarm');
});

test('what actually happened tells the story and shows availability five ways', async ({ page }) => {
  const { root } = await open(page, '?persona=truth');
  const osa = scenario('off|today').kpis.osa;
  const table = root.locator('table.four-ways');
  for (const v of [osa.system_in_stock, osa.shelf_audit, ai.availability.books_and_tills, osa.open_hours_on_shelf, osa.demand_served]) {
    await expect(table).toContainText(pct(v));
  }
  const ep = data.story.episode;
  await expect(root.locator('[data-panel]')).toContainText(`Shoppers asked for ${ep.lost_units} bags they could not find`);
  // Rerun June with the gap detector: the check finds the cases the same evening.
  await root.getByRole('radio', { name: 'Hourly gap detector' }).check();
  await expect(root.locator('[data-panel]')).toContainText('the gap detector raises an alert');
  await expect(root.locator('[data-panel] p.context')).toContainText('June rerun on the same shoppers');
});

test('deep links set the levers and the question', async ({ page }) => {
  const { root } = await open(page, '?persona=assistant&grounding=domain&detect=gap&q=lost');
  await expect(root.locator('input[name="grounding"][value="domain"]')).toBeChecked();
  await expect(root.locator('input[name="detect"][value="gap"]')).toBeChecked();
  await expect(root.locator('.questions [data-q="lost"]')).toHaveAttribute('aria-pressed', 'true');
  const lost = (ai.assistant.questions as Question[]).find((q) => q.id === 'lost')!;
  await expect(root.locator('.run .answer-text')).toHaveText(lost.domain.answer);
});

test('the milk slider trades waste for empty shelves', async ({ page }) => {
  const { root } = await open(page);
  const out = root.locator('[data-milk-out]');
  const lean = data.milk[0];
  await root.locator('input[name="milk"]').fill('0');
  await expect(out).toContainText(fmt(lean.lost));
  await expect(out).toContainText(fmt(lean.expired));
});

test('the records drawer reveals scan errors, and the downloads and notebook exist', async ({ page, request }) => {
  const { root } = await open(page);
  await root.getByText('The records behind it').click();
  await expect(root.locator('[data-records] table')).toBeVisible();
  const errors = data.records.pos_lines.filter((l: { scan_error: string | null }) => l.scan_error).length;
  await root.getByLabel('Show what the records hide').check();
  if (errors) await expect(root.locator('[data-records] .gap').first()).toContainText('Really');
  const links = await root.locator('.downloads a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')));
  expect(links.length).toBeGreaterThanOrEqual(12);
  for (const href of links.filter((h) => h!.startsWith('/domain-series/'))) {
    const res = await request.get(href!.replace('/domain-series/', ''));
    expect(res.status(), href!).toBe(200);
  }
  expect(links).toContain('https://colab.research.google.com/github/kvinayakpai/domain-series/blob/main/public/notebooks/retail.ipynb');
  const nb = await request.get('notebooks/retail.ipynb');
  expect(nb.status()).toBe(200);
  expect((await nb.json()).cells.length).toBeGreaterThan(20);
});
