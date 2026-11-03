import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The finale quotes finale.json (scripts/analysis/finale.py), which is computed from the records.
// Every number checked here is read from the data files, so a change in the world fails here first.
const read = (f: string) => JSON.parse(readFileSync(new URL(`../../src/data/${f}`, import.meta.url), 'utf8'));
const f = read('finale.json');
const pai = read('payments-ai.json');
const J = Object.fromEntries(f.joins.map((j: { id: string }) => [j.id, j]));
const num = (n: number) => n.toLocaleString('en-IN');
const [shelf, truck, money] = f.incidents;
const flat = (s: string) => s.replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');

test('the finale quotes the map correctly', async ({ page }) => {
  await page.goto('who-saw-what/');
  const text = flat(await page.locator('article').innerText());
  const copies = f.joins.filter((j: { kind: string }) => j.kind === 'copy');
  const obs = f.joins.filter((j: { kind: string }) => j.kind === 'observation');
  expect([copies.length, obs.length]).toEqual([8, 4]);
  const bench = read('bench.json').baselines;
  const off = (id: string) => J[id].compared - J[id].agree;
  const expected = [
    'twelve joins in all, and counted how often each pair agrees',
    'Eight of the twelve agree on every row.',
    `The shipping notice matches the pick confirmations on all ${J['picks-notice'].compared} lines, the book stock matches its own ledger on all ${J['book-ledger'].compared} item-days, and all ${num(J['payments-provider'].compared)} UPI payments the tills approved are successes in the provider's report`,
    `The book stock disagrees with ${off('book-counts')} of ${J['book-counts'].compared} stock counts and with two of ${J['book-audits'].compared} shelf checks`,
    'One goods receipt in ten did not survive the next count',
    `And ${off('timeouts-provider')} of ${J['timeouts-provider'].compared} timeouts disagree with the provider's report`,
    'The headline KPIs read copies. On-shelf availability reads the book stock, OTIF reads the goods receipts, and payment success reads the till.',
    `none of the ${f.evidence.pallets.n} pallets was weighed or case-scanned`,
    'The empty atta shelf shows three open hours after it emptied',
    'The wrong pallet line shows four and a half hours after the 5 kg shelf emptied',
    `Each double charge shows a median ${Math.round(money.hours_joined)} hours after the debit`,
    `Staff found the atta bags ${Math.round(shelf.hours_found)} hours after the shelf emptied, the manager's count found the missing 5 kg bags ${Math.round(truck.hours_found)} hours after, and complaints took a median ${Math.round(money.hours_found)} hours, while three customers never complained at all`,
    `a scripted assistant answers ${bench.map.of} questions about Store 014. Given only the schema, it gets ${bench['schema-only'].right} right. Given each domain's definitions and rules, it gets ${bench['domain-layers'].right}, and given the map, all ${bench.map.right}`,
    'GPT-4 answered 16% of enterprise questions correctly from the SQL tables, and 54% when the same data came as a knowledge graph of the business',
    'raised accuracy to 72%',
  ];
  for (const e of expected) expect(text, e).toContain(flat(e));
  expect(off('book-audits')).toBe(2);
  expect(J['receipts-counts']).toMatchObject({ agree: 9, compared: 10 });
  expect(Math.round(shelf.hours_joined)).toBe(3);
  expect(truck.hours_joined).toBe(4.5);
  expect(f.evidence.pallets.checked).toBe(0);
  expect(f.map.unseen).toEqual(['pallet']);
  expect(pai.find.never_complained).toBe(3);
  expect(bench.map.right).toBe(bench.map.of);
  expect(J['timeouts-provider'].agree).toBe(pai.matcher.outcomes['never debited']);
});

test('the finale figures render, on any screen', async ({ page }, info) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('who-saw-what/');
  await expect(page.locator('table.joins tbody tr.copy')).toHaveCount(8);
  await expect(page.locator('table.joins tbody tr.observation')).toHaveCount(4);
  await expect(page.locator('table.joins')).toContainText(`${num(J['payments-provider'].agree)} of ${num(J['payments-provider'].compared)}`);
  if (info.project.name === 'mobile') {
    await expect(page.locator('.record-map .map-narrow')).toBeVisible();
    await expect(page.locator('.record-map .map-narrow li')).toHaveCount(13);
    await expect(page.locator('.record-map .map-narrow')).toContainText('Nothing looks at what is on a pallet.');
  } else {
    await expect(page.locator('.record-map .map-wide svg')).toBeVisible();
    await expect(page.locator('.record-map svg g.node')).toHaveCount(13);
    await expect(page.locator('.record-map svg g.thing')).toHaveCount(6);
    await expect(page.locator('.record-map svg g.thing.unseen')).toContainText('What is on a pallet');
    await expect(page.locator('.record-map svg g.pill.observation')).toHaveCount(4);
  }
  await expect(page.locator('figure.picture img')).toHaveCount(3);
  expect(errors).toEqual([]);
});

test('the map downloads as JSON, and the series links to the finale', async ({ page, request }) => {
  const res = await request.get('data/india-grocery/store-014-map.json');
  expect(res.status()).toBe(200);
  const map = await res.json();
  expect(map.records).toHaveLength(14);
  expect(map.joins).toHaveLength(12);
  expect(map.things.find((t: { id: string }) => t.id === 'pallet').looked_at_by).toEqual([]);
  for (const j of map.joins) expect(j.compared, j.id).toBeGreaterThan(0);
  for (const r of map.records) expect((await request.head(`data/india-grocery/${r.file}`)).status(), r.file).toBe(200);

  await page.goto('./');
  await expect(page.locator('.part-posts a[href$="/who-saw-what/"]')).toHaveCount(1);
  // Since 2 November 2026 posts link only to outside sources; the home page and the pager link the finale.
  await page.goto('why-domain/');
  await expect(page.locator('article a[href$="/who-saw-what/"]')).toHaveCount(0);
  await page.goto('data/');
  await expect(page.locator('a[href$="/store-014-map.json"]')).toHaveCount(1);
  await page.goto('payments/');
  await expect(page.locator('nav.pager a[href$="/who-saw-what/"]')).toHaveCount(1);
});
