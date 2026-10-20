import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

const data = JSON.parse(readFileSync(new URL('../../src/data/retail.json', import.meta.url), 'utf8'));
const scenario = (key: string) => data.scenarios.find((s: { key: string }) => s.key === key);
const fmt = (n: number) => Math.round(n).toLocaleString('en-IN');

async function open(page: Page, query = '') {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`demo/${query}`);
  await expect(page.locator('[data-retail-demo]')).toHaveAttribute('data-ready', 'true');
  return errors;
}

test('outcome numbers come from the world, and the controls change them', async ({ page }) => {
  const errors = await open(page);
  const outcome = page.locator('[data-outcome]');
  const asIs = scenario('off|today');
  await expect(outcome).toContainText(fmt(asIs.kpis.empty_open_hours));
  await expect(outcome).toContainText(fmt(asIs.kpis.lost_units));

  await page.getByRole('radio', { name: 'Next morning' }).check();
  const alert = scenario('1d|today');
  await expect(outcome).toContainText(fmt(alert.kpis.lost_units));

  await page.getByRole('radio', { name: 'Scan every case into a bin' }).check();
  const both = scenario('1d|scanned');
  await expect(outcome).toContainText(fmt(both.kpis.lost_units));
  expect(both.kpis.lost_units).toBeLessThan(alert.kpis.lost_units);
  expect(errors).toEqual([]);
});

test('every persona renders a chart, and the tabs work from the keyboard', async ({ page }) => {
  const errors = await open(page);
  const tabs = ['store', 'system', 'planner', 'category', 'supplier', 'truth'];
  for (const t of tabs) {
    await page.locator(`[data-persona="${t}"]`).click();
    await expect(page.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(page.locator('[data-panel] svg').first()).toBeVisible();
  }
  await page.locator('[data-persona="store"]').click();
  await page.locator('[data-persona="store"]').press('ArrowRight');
  await expect(page.locator('[data-persona="system"]')).toHaveAttribute('aria-selected', 'true');
  await expect(page.locator('[data-persona="system"]')).toBeFocused();
  expect(errors).toEqual([]);
});

test('what actually happened shows availability measured four ways', async ({ page }) => {
  await open(page, '?persona=truth');
  const osa = scenario('off|today').kpis.osa;
  const table = page.locator('table.four-ways');
  for (const v of [osa.system_in_stock, osa.shelf_audit, osa.open_hours_on_shelf, osa.demand_served]) {
    await expect(table).toContainText(`${Math.round(v * 100)}%`);
  }
  const ep = data.story.episode;
  await expect(page.locator('[data-panel]')).toContainText(`${ep.lost_units} bags they could not buy`);
});

test('the milk slider trades waste for empty shelves', async ({ page }) => {
  await open(page);
  const out = page.locator('[data-milk-out]');
  const lean = data.milk[0];
  await page.locator('input[name="milk"]').fill('0');
  await expect(out).toContainText(fmt(lean.lost));
  await expect(out).toContainText(fmt(lean.expired));
});

test('the records drawer reveals scan errors, and the downloads exist', async ({ page, request }) => {
  await open(page);
  await page.getByText('The records behind it').click();
  await expect(page.locator('[data-records] table')).toBeVisible();
  const errors = data.records.pos_lines.filter((l: { scan_error: string | null }) => l.scan_error).length;
  await page.getByLabel('Show what the records hide').check();
  if (errors) await expect(page.locator('[data-records] .gap').first()).toContainText('Really');
  const links = await page.locator('.downloads a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')));
  expect(links.length).toBeGreaterThanOrEqual(10);
  for (const href of links) {
    const res = await request.get(href!.replace('/domain-series/', ''));
    expect(res.status(), href!).toBe(200);
  }
});
