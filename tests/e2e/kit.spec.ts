import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { load } from 'js-yaml';

// The kit page quotes what scripts/kit/*.py built and checked. Every number here is read from those
// outputs, and every file the page offers must be served.
const read = (f: string) => JSON.parse(readFileSync(new URL(`../../src/data/${f}`, import.meta.url), 'utf8'));
const bench = read('bench.json');
const dbt = read('dbt-kit.json');
const finale = read('finale.json');

test('the kit page shows the bench, the dbt tests and the domain layer', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('kit/');
  await expect(page.locator('h1')).toHaveText('Take it to work');
  const rows = page.locator('table.bench-scores tbody tr');
  await expect(rows).toHaveCount(3);
  for (const [i, k] of ['schema-only', 'domain-layers', 'map'].entries()) {
    await expect(rows.nth(i).locator('td.all')).toHaveText(`${bench.baselines[k].right} of ${bench.baselines[k].of}`);
  }
  expect([bench.baselines['schema-only'].right, bench.baselines['domain-layers'].right, bench.baselines.map.right]).toEqual([3, 21, 22]);
  await expect(page.locator('.qs > div')).toHaveCount(bench.sample.length);
  const tests = page.locator('table.dbt-tests tbody tr:not(.group)');
  await expect(tests).toHaveCount(Object.keys(dbt.domain).length);
  for (const [id, n] of Object.entries(dbt.domain)) {
    await expect(page.locator('table.dbt-tests tbody tr', { has: page.locator(`code:text-is("${id}")`) }).locator('td.n')).toHaveText(String(n));
  }
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  expect(text).toContain(`${dbt.pipeline.pass} pass, and the other warns about one milk book`);
  expect(finale.joins.filter((j: { kind: string }) => j.kind === 'copy').length).toBe(8);
  expect(text).toContain('eight always do');
  expect(errors).toEqual([]);
});

test('every file the kit offers is served, and the YAML and JSON parse', async ({ page, request }) => {
  await page.goto('kit/');
  const hrefs = await page.locator('article a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')!));
  const local = [...new Set(hrefs.filter((h) => h.startsWith('/domain-series/') && !h.endsWith('/') && !h.includes('#')))];
  expect(local.length).toBeGreaterThanOrEqual(12);
  for (const h of local) expect((await request.get(h.replace('/domain-series/', ''))).status(), h).toBe(200);

  const q = await (await request.get('kit/bench/questions.json')).json();
  expect(q.questions).toHaveLength(bench.questions);
  const key = await (await request.get('kit/bench/answer-key.json')).json();
  expect(Object.keys(key.answers)).toEqual(q.questions.map((x: { id: string }) => x.id));
  const layer = load(await (await request.get('kit/store-014-domain-layer.yaml')).text()) as Record<string, unknown>;
  expect(Object.keys(layer)).toEqual(expect.arrayContaining(['records', 'joins', 'kpis', 'definitions', 'rules', 'views']));
  expect((layer.joins as unknown[]).length).toBe(finale.joins.length);
  const template = load(await (await request.get('kit/domain-layer-template.yaml')).text()) as Record<string, unknown>;
  expect(Object.keys(template)).toEqual(['records', 'unseen', 'joins', 'kpis', 'definitions', 'rules', 'views']);
  const zip = await request.get('kit/store-014-dbt.zip');
  expect(zip.status()).toBe(200);
  expect((await zip.body()).subarray(0, 2).toString()).toBe('PK');
});
