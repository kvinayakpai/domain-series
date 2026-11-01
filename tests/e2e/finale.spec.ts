import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The finale quotes finale.json (scripts/analysis/finale.py), which is computed from the records.
// Every number checked here is read from the data files, so a change in the world fails here first.
const read = (f: string) => JSON.parse(readFileSync(new URL(`../../src/data/${f}`, import.meta.url), 'utf8'));
const f = read('finale.json');
const pai = read('payments-ai.json');
const key = JSON.parse(readFileSync(new URL('../../public/data/india-grocery/answer-key-logistics.json', import.meta.url), 'utf8'));
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
  const t = f.trace;
  const expected = [
    'Eight of twelve joins compare a record with its own copy.',
    `the wrong pallet line four and a half hours after the 5 kg shelf emptied`,
    `each double charge a median ${Math.round(money.hours_joined)} hours after the debit`,
    `staff found the atta bags ${Math.round(shelf.hours_found)} hours after the shelf emptied`,
    `the manager's count found the missing bags ${Math.round(truck.hours_found)} hours after`,
    `complaints took a median ${Math.round(money.hours_found)} hours, while three customers never complained at all`,
    `Eight of the twelve joins agree on every row`,
    `The shipping notice matches the pick confirmations on all ${J['picks-notice'].compared} lines, the book stock equals its own ledger on all ${J['book-ledger'].compared} item-days, and all ${num(J['payments-provider'].compared)} UPI payments the tills approved are successes`,
    `The book stock disagrees with ${J['book-counts'].compared - J['book-counts'].agree} of ${J['book-counts'].compared} stock counts`,
    `the count on 26 June found ${t.silence.book_at_flag} bags of 5 kg atta that were not there`,
    `It disagrees with two of ${J['book-audits'].compared} shelf audits`,
    `found the 5 kg shelf empty with ${f.audits_disagreeing.find((a: { sku: string }) => a.sku === 'ATTA-WW-5KG').book_at_audit} bags on the books`,
    `One goods receipt in ten did not survive the next count`,
    `${J['timeouts-provider'].compared - J['timeouts-provider'].agree} of ${J['timeouts-provider'].compared} timeouts disagree with the provider's report`,
    `none of June's ${f.evidence.pallets.n} pallets was weighed or case-scanned, all ${f.evidence.picks_by_slot_scan.n} picks were confirmed by scanning the slot, and all ${f.evidence.receipts_by_label.n} receipts by scanning the label`,
    `show 5 kg atta silent since 4 pm, with ${t.silence.book_at_flag} bags on the books`,
    `names line ${t.names.line} of the 22 June shipment, and the answer key agrees: it held ${t.answer_key.units} packs of 1 kg`,
    `${Math.round(t.hours_before_pair)} hours before the warehouse's own corrections pair up, and ${Math.round(t.hours_before_count)} hours before the store's count`,
    'answered one question in seven from the schema, and seven in seven with that domain\'s layer',
    'GPT-4 answered 16% of enterprise questions correctly from the SQL tables, and 54% when the same data was given to it as a knowledge graph',
    'raised accuracy to 72%',
  ];
  for (const e of expected) expect(text, e).toContain(flat(e));
  expect(t.right).toBe(true);
  expect(text).toContain('the empty atta shelf three open hours after it emptied');
  expect(Math.round(shelf.hours_joined)).toBe(3);
  expect(truck.hours_joined).toBe(4.5);
  expect(t.names.shipment_id).toBe('SHP-260622');
  expect(J['receipts-counts']).toMatchObject({ agree: 9, compared: 10 });
  const truth = key.pallet_contents_june.find((p: { sscc: string; line: number }) => p.sscc === t.hit.sscc && p.line === t.hit.line);
  expect([truth.sku_actual, truth.units_actual]).toEqual([t.names.sku, -t.names.units]);
  expect(f.map.unseen).toEqual(['pallet']);
  expect(f.agents.assistants).toMatchObject({ naive: 3, domain: 21, of: 21 });
  expect(J['timeouts-provider'].agree).toBe(pai.matcher.outcomes['never debited']);
});

test('the finale figures render, on any screen', async ({ page }, info) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('who-saw-what/');
  await expect(page.locator('.ttf-row')).toHaveCount(3);
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
  await expect(page.locator('.trace .hops li')).toHaveCount(5);
  await expect(page.locator('.trace .verdict')).toContainText('Right.');
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
  await page.goto('why-domain/');
  await expect(page.locator('article a[href$="/who-saw-what/"]')).toHaveCount(1);
  await page.goto('data/');
  await expect(page.locator('a[href$="/store-014-map.json"]')).toHaveCount(1);
  await page.goto('technical-declines/');
  await expect(page.locator('nav.pager a[href$="/who-saw-what/"]')).toHaveCount(1);
});
