import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { load } from 'js-yaml';

// The opener, the KPI page, the home table and the KPI x-ray in each post header all quote the
// world. Every number checked here is derived from the world's exports directly, not from
// src/lib/kpis.ts, so a change in the world that the prose has not caught up with fails here.
const read = (f: string) => JSON.parse(readFileSync(new URL(`../../src/data/${f}`, import.meta.url), 'utf8'));
const retail = read('retail.json');
const ai = read('retail-ai.json');
const logistics = read('logistics.json');
const payments = read('payments.json');
const pai = read('payments-ai.json');
const lai = read('logistics-ai.json');

const pct = (v: number) => `${Math.round(Math.abs(v) * 100)}%`;
const inr = (v: number) => `₹${Math.round(v).toLocaleString('en-IN')}`;

const ep = retail.story.episode;
const asIs = retail.scenarios.find((s: { key: string }) => s.key === 'off|today');
const flag = ai.detector.hero_flags[0];
const lk = logistics.scenarios.find((s: { key: string }) => s.key === 'none|label').kpis;
const ls = logistics.story;
const foundAfterDays = Math.floor((Date.parse(`${ls.corrections[0].count_ts}:00+05:30`) - Date.parse(`${ls.shipment.arrived_ts}:00+05:30`)) / 86_400_000);
const slow = payments.story.slowdown;
const june = payments.story.june;
const refunds = payments.story.refunds;

// The KPI each domain post is built around, measured twice, with what the gap cost.
const heroes = [
  {
    post: 'retail', id: 'osa',
    reported: pct(ai.availability.on_the_books), observed: pct(ai.availability.true_open_hours),
    cost: `${asIs.kpis.lost_units} bags shoppers could not find: ${inr(asIs.kpis.lost_value_inr)} of sales`,
    found: `After ${Math.round(ep.empty_open_hours)} open hours`,
  },
  {
    post: 'logistics', id: 'otif',
    reported: pct(lk.otif.dc_report), observed: pct(lk.otif.at_the_shelf),
    cost: `${ls.episode.lost_units} bags (${inr(ls.episode.lost_value_inr)}) not sold`,
    found: `${foundAfterDays} days after delivery`,
  },
  {
    post: 'payments', id: 'success-rate',
    reported: pct(slow.four_ways.till), observed: pct(slow.four_ways.bank),
    cost: `${slow.charged_twice} customers charged twice: ${slow.extra_charges} extra charges, ${inr(slow.charged_twice_inr)}`,
    found: `median ${refunds.median_days_to_refund} days`,
  },
];

async function articleText(page: Page, path: string) {
  await page.goto(path);
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

test('the opener quotes the world correctly', async ({ page }) => {
  const text = await articleText(page, 'why-domain/');
  const dbt = read('dbt-kit.json');
  const seeds = retail.agents.seeds.runs;
  // The three KPIs, each measured twice and named in plain text: since 2 November 2026 posts link
  // only to outside sources.
  const rows = page.locator('.kpi-pairs li');
  await expect(rows).toHaveCount(3);
  for (const [i, h] of [heroes[0], heroes[1], heroes[2]].entries()) {
    await expect(rows.nth(i).locator('.kp-v.rec')).toHaveText((h as { reported: string }).reported);
    await expect(rows.nth(i).locator('.kp-v.gap')).toHaveText((h as { observed: string }).observed);
    await expect(rows.nth(i).locator('a')).toHaveCount(0);
  }
  const expected = [
    `In those 90 minutes on Saturday evening, ${slow.charged_twice} customers paid twice`,
    `${dbt.pipeline.pass} of the store's ${dbt.pipeline.tests} data tests passed, and the other one warned about milk`,
    'book stock cannot see the shelf, a shipping notice cannot see inside a pallet, and a till cannot see the customer\'s bank',
    'across forty simulated Junes 5 kg atta lost half as many sales',
    'does this for all eighteen of the series\' KPIs',
    'The series has 25 short posts, one idea each, in five parts.',
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(dbt.pipeline.tests - dbt.pipeline.pass).toBe(1);
  expect(retail.agents.seeds.n).toBe(40);
  const half = seeds.domain.mean.hero_lost_units / seeds.naive.mean.hero_lost_units;
  expect(half).toBeGreaterThan(0.45);
  expect(half).toBeLessThan(0.55);
  expect(seeds.domain.mean.stock_at_cost_inr).toBeLessThanOrEqual(seeds.none.mean.stock_at_cost_inr);
  // The opener has no x-ray of its own, and every other post is one of the twenty-five.
  await expect(page.locator('.xray')).toHaveCount(0);
  await expect(page.locator('.post-domain')).toHaveText('Start here');
});

test('the KPI page x-rays eighteen KPIs, each measured twice', async ({ page }) => {
  await page.goto('kpis/');
  await expect(page.locator('section.kpi')).toHaveCount(18);
  for (const [domain, n, word] of [['retail', 8, 'eight'], ['logistics', 5, 'five'], ['payments', 5, 'five']] as const) {
    await expect(page.locator(`#${domain} section.kpi`)).toHaveCount(n);
    await expect(page.locator(`.kpi-jump a[href="#${domain}"]`).locator('..')).toContainText(`${word} KPIs`);
    await expect(page.locator(`#${domain} .kpi-from a[href$="/${domain}/"]`)).toHaveCount(1);
  }

  // Every KPI carries both numbers, the four facets and a Store 014 example.
  const kpis = page.locator('section.kpi');
  for (let i = 0; i < 18; i++) {
    const k = kpis.nth(i);
    await expect(k.locator('.kpi-twice .kpi-num')).toHaveCount(2);
    await expect(k.locator('.kpi-facets dt')).toHaveText(['Usually computed from', 'Blind spot', 'Domain check', 'Tell your agent']);
    await expect(k.locator('.kpi-example')).toContainText('Store 014');
    await expect(k.locator('.kpi-drives')).toHaveText(/^It drives [a-z]/);
  }

  // The numbers, from the world.
  const twice = async (id: string, reported: string, observed: string) => {
    await expect(page.locator(`#${id} .kpi-num.rec`), id).toHaveText(reported);
    await expect(page.locator(`#${id} .kpi-num.gap`), id).toHaveText(observed);
  };
  for (const h of heroes) await twice(h.id, h.reported, h.observed);
  const acc = retail.record_accuracy;
  await twice('lost-sales', '0', `${asIs.kpis.lost_units} bags`);
  await twice('ira', '100%', pct((acc.items - acc.wrong) / acc.items));
  await twice('fill-rate', `${(lai.fill.by_notice * 100).toFixed(1)}%`, `${(lai.fill.right_item * 100).toFixed(1)}%`);
  // Every KPI links to its own post.
  await expect(page.locator('section.kpi .kpi-post a')).toHaveCount(18);
  await twice('on-time', `${lk.in_slot} of ${lk.shipments}`, ls.shipment.arrived_ts.slice(11, 16));
  await twice('charged-twice', '0', `${june.charged_twice} customers`);
  const fromComplaint = pai.assistant.questions.find((q: { id: string }) => q.id === 'wait').naive.value;
  await twice('refund-tat', `${Math.round(fromComplaint)} days`, `${pai.find.refund_median_days_from_debit} days`);
  await twice('technical-declines', `${((june.upi_technical_failures / june.upi_attempts) * 100).toFixed(2)}%`, pct(slow.upi_timeouts / slow.upi_attempts));
});

test('the KPI list downloads as YAML with the same eighteen entries', async ({ page, request }) => {
  const res = await request.get('kpis/domain-kpis.yaml');
  expect(res.status()).toBe(200);
  expect(res.headers()['content-type']).toContain('yaml');
  const doc = load(await res.text()) as { domains: { id: string; kpis: Record<string, unknown>[] }[] };
  expect(doc.domains.map((d) => d.id)).toEqual(['retail', 'logistics', 'payments']);
  const all = doc.domains.flatMap((d) => d.kpis);
  expect(all).toHaveLength(18);
  for (const k of all) {
    for (const field of ['id', 'name', 'drives', 'usually_computed_from', 'blind_spot', 'domain_check', 'agent_rule', 'store_014']) {
      expect(k[field], `${k.id}: ${field}`).toBeTruthy();
    }
  }
  const osa = all.find((k) => k.id === 'osa') as { store_014: { reported: { value: string }; observed: { value: string } } };
  expect(osa.store_014.reported.value).toBe(heroes[0].reported);
  expect(osa.store_014.observed.value).toBe(heroes[0].observed);

  // The page and the file list the same KPIs, in the same order.
  await page.goto('kpis/');
  const ids = await page.locator('section.kpi').evaluateAll((els) => els.map((e) => e.id));
  expect(ids).toEqual(all.map((k) => k.id));
  await expect(page.locator('a[href$="/kpis/domain-kpis.yaml"]')).toHaveAttribute('download', '');
});

test('each domain post opens with its KPI x-rayed, linked to the KPI page', async ({ page }) => {
  for (const h of heroes) {
    await page.goto(`${h.post}/`);
    const x = page.locator('.xray');
    await expect(x).toBeVisible();
    await expect(x).toContainText(h.reported);
    await expect(x).toContainText(h.observed);
    await expect(x).toContainText(h.cost);
    await expect(x).toContainText(h.found);
    await expect(page.locator('.post-domain')).toBeVisible();
    const link = x.locator(`a[href$="/kpis/#${h.id}"]`);
    await expect(link).toContainText('17 more');
    await link.click();
    await expect(page).toHaveURL(new RegExp(`/kpis/#${h.id}$`));
    await expect(page.locator(`section.kpi#${h.id}`)).toBeInViewport();
  }
});

test('the home page lists the twenty-five posts by part, each with what actually happened', async ({ page }) => {
  await page.goto('./');
  await expect(page.locator('.part')).toHaveCount(4);
  const counts = { shelf: 9, truck: 6, money: 6, together: 3 } as const;
  for (const [part, n] of Object.entries(counts)) await expect(page.locator(`#part-${part} + .part-blurb + .part-posts li`)).toHaveCount(n);
  await expect(page.locator('.part-posts li')).toHaveCount(24);
  for (const [h, slug] of [[heroes[0], 'on-shelf-availability'], [heroes[1], 'otif'], [heroes[2], 'payment-success']] as const) {
    const row = page.locator('.part-posts li', { has: page.locator(`a[href$="/${slug}/"]`) });
    await expect(row.locator('.note')).toContainText(h.observed);
  }
  for (const slug of ['retail', 'logistics', 'payments']) await expect(page.locator(`.part-posts .is-story a[href$="/${slug}/"]`)).toHaveCount(1);
  await expect(page.locator('#contents-title')).toHaveText('The series, in 25 short posts');
  // Every page leads readers to the opener and the KPI page.
  await expect(page.locator('header nav a[href$="/why-domain/"]')).toHaveText('Start here');
  await expect(page.locator('header nav a[href$="/kpis/"]')).toHaveText('KPIs');
});
