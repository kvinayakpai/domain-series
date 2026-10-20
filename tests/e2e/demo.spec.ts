import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

const data = JSON.parse(readFileSync(new URL('../../src/data/retail.json', import.meta.url), 'utf8'));
const scenario = (key: string) => data.scenarios.find((s: { key: string }) => s.key === key);
const fmt = (n: number) => Math.round(n).toLocaleString('en-IN');

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

test('outcome numbers come from the world, and the controls change them', async ({ page }) => {
  const { errors, root } = await open(page);
  const outcome = root.locator('[data-outcome]');
  const asIs = scenario('off|today');
  await expect(outcome).toContainText(fmt(asIs.kpis.empty_open_hours));
  await expect(outcome).toContainText(fmt(asIs.kpis.lost_units));

  await root.getByRole('radio', { name: 'Next morning' }).check();
  const alert = scenario('1d|today');
  await expect(outcome).toContainText(fmt(alert.kpis.lost_units));

  await root.getByRole('radio', { name: 'Scan every case into a bin' }).check();
  const both = scenario('1d|scanned');
  await expect(outcome).toContainText(fmt(both.kpis.lost_units));
  expect(both.kpis.lost_units).toBeLessThan(alert.kpis.lost_units);
  expect(errors).toEqual([]);
});

test('every persona renders a chart, and the tabs work from the keyboard', async ({ page }) => {
  const { errors, root } = await open(page);
  const tabs = ['store', 'system', 'planner', 'category', 'supplier', 'truth'];
  for (const t of tabs) {
    await root.locator(`[data-persona="${t}"]`).click();
    await expect(root.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(root.locator('[data-panel] svg').first()).toBeVisible();
  }
  await root.locator('[data-persona="store"]').click();
  await root.locator('[data-persona="store"]').press('ArrowRight');
  await expect(root.locator('[data-persona="system"]')).toHaveAttribute('aria-selected', 'true');
  await expect(root.locator('[data-persona="system"]')).toBeFocused();
  expect(errors).toEqual([]);
});

test('what actually happened shows availability measured four ways', async ({ page }) => {
  const { root } = await open(page, '?persona=truth');
  const osa = scenario('off|today').kpis.osa;
  const table = root.locator('table.four-ways');
  for (const v of [osa.system_in_stock, osa.shelf_audit, osa.open_hours_on_shelf, osa.demand_served]) {
    await expect(table).toContainText(`${Math.round(v * 100)}%`);
  }
  const ep = data.story.episode;
  await expect(root.locator('[data-panel]')).toContainText(`${ep.lost_units} bags they could not buy`);
});

test('the milk slider trades waste for empty shelves', async ({ page }) => {
  const { root } = await open(page);
  const out = root.locator('[data-milk-out]');
  const lean = data.milk[0];
  await root.locator('input[name="milk"]').fill('0');
  await expect(out).toContainText(fmt(lean.lost));
  await expect(out).toContainText(fmt(lean.expired));
});

test('the records drawer reveals scan errors, and the downloads exist', async ({ page, request }) => {
  const { root } = await open(page);
  await root.getByText('The records behind it').click();
  await expect(root.locator('[data-records] table')).toBeVisible();
  const errors = data.records.pos_lines.filter((l: { scan_error: string | null }) => l.scan_error).length;
  await root.getByLabel('Show what the records hide').check();
  if (errors) await expect(root.locator('[data-records] .gap').first()).toContainText('Really');
  const links = await root.locator('.downloads a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')));
  expect(links.length).toBeGreaterThanOrEqual(10);
  for (const href of links) {
    const res = await request.get(href!.replace('/domain-series/', ''));
    expect(res.status(), href!).toBe(200);
  }
});
