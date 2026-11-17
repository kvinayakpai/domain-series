import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import yaml from 'js-yaml';

// Season 2, "Ontology is all about domain knowledge": its contents page, its posts and the Store 014
// numbers they quote. The numbers must still match the KPI list the site builds and the logistics
// records (src/data/logistics.json, logistics-ai.json), so a change to the world fails the build
// until the prose is updated.
const logistics = JSON.parse(readFileSync(new URL('../../src/data/logistics.json', import.meta.url), 'utf8'));
const lai = JSON.parse(readFileSync(new URL('../../src/data/logistics-ai.json', import.meta.url), 'utf8'));
const st = logistics.story;
const words: Record<number, string> = { 16: 'sixteen' };
const pct1 = (v: number) => `${(v * 100).toFixed(1)}%`;

// The posts that are out, in reading order: [slug, the line above the title].
const POSTS: [string, string][] = [
  ['every-word', 'Ontology · Start here: 1 of 3'],
  ['glossary-to-graph', 'Ontology · Start here: 2 of 3'],
  ['four-kb-note', 'Ontology · Start here: 3 of 3'],
  ['what-is-an-item', 'Ontology · Word 1 of 12 · the shelf'],
];
// Post 1 is in Vinayak's voice; the others are narrated by his AI assistant.
const NARRATED = ['glossary-to-graph', 'four-kb-note', 'what-is-an-item'];

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  // Typographic quotes in the page compare equal to plain ones in the expectations.
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

for (const p of [{ path: 'ontology/', og: 'ontology' }, ...POSTS.map(([slug]) => ({ path: `${slug}/`, og: slug }))]) {
  test(`${p.path} renders cleanly`, async ({ page, request }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    const res = await page.goto(p.path);
    expect(res?.status()).toBe(200);
    await expect(page.locator('h1')).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', `https://kvinayakpai.github.io/domain-series/og/${p.og}.png`);
    const og = await request.get(`og/${p.og}.png`);
    expect(og.status()).toBe(200);
    expect(errors).toEqual([]);
  });
}

test('home points to Season 2 ahead of Season 3, and the season pages say which is which', async ({ page }) => {
  await page.goto('./');
  await expect(page.locator('.season-next a[href$="/ontology/"]')).toHaveCount(1);
  await expect(page.locator('.season-next a[href$="/every-word/"]')).toHaveCount(1);
  const seasons = await page.locator('.season-next h2').allInnerTexts();
  expect(seasons[0]).toContain('Season 2');
  expect(seasons[1]).toContain('Season 3');
  await expect(page.locator('.site-nav a[href$="/ontology/"]')).toHaveText('Ontology');
  await page.goto('ontology/');
  await expect(page.locator('.season')).toHaveText(/season two/i);
  await page.goto('oil-and-gas/');
  await expect(page.locator('.season')).toHaveText(/season three/i);
});

test('the season page lists all eighteen posts and links the ones that are out', async ({ page }) => {
  await page.goto('ontology/');
  await expect(page.locator('.opener a[href$="/every-word/"]')).toHaveCount(1);
  await expect(page.locator('.on-posts li')).toHaveCount(18);
  await expect(page.locator('.on-posts li.is-out')).toHaveCount(POSTS.length);
  await expect(page.locator('.on-posts li.is-coming')).toHaveCount(18 - POSTS.length);
  for (const [slug] of POSTS) await expect(page.locator(`.on-posts a[href$="/${slug}/"]`)).toHaveCount(1);
  await expect(page.locator('.on-posts a[href$="/what-is-an-item/"]')).toHaveText('Word 1: What is an item?');
});

test('season posts link only to outside sources, carry the AI line and three described pictures', async ({ page, request }) => {
  for (const [slug, line] of POSTS) {
    await page.goto(`${slug}/`);
    await expect(page.locator('.post-domain'), slug).toHaveText(line);
    const prose = 'article > p a[href], article > ul a[href], article > ol a[href], article > blockquote a[href]';
    const own = await page.locator(prose).evaluateAll((as) =>
      as.map((a) => a as HTMLAnchorElement).filter((a) => a.origin === location.origin).map((a) => a.getAttribute('href')),
    );
    expect(own, slug).toEqual([]);
    await expect(page.locator('article'), slug).toContainText(/written by AI and engineered by Vinayak/);
    await expect(page.locator('article'), slug).toContainText('Curious to know what you think');
    // Posts 2 onwards end with a rule for an agent; the opener ends with the season's ask instead.
    if (NARRATED.includes(slug)) await expect(page.locator('article'), slug).toContainText('The rule I would give any AI agent –');
    else await expect(page.locator('article'), slug).toContainText('has to agree what our words mean');
    const imgs = await page.locator('article figure.picture img').evaluateAll((els) => els.map((e) => ({ src: (e as HTMLImageElement).getAttribute('src')!, alt: (e as HTMLImageElement).alt })));
    expect(imgs.length, slug).toBe(3);
    for (const img of imgs) {
      expect(img.alt.length, `${slug} ${img.src}`).toBeGreaterThan(60);
      const res = await request.head(img.src.replace('/domain-series/', ''));
      expect(res.status(), img.src).toBe(200);
      expect(res.headers()['content-type'], img.src).toContain('image/png');
    }
    if (NARRATED.includes(slug)) {
      // The narrator is flagged the first time it says I.
      const plain = (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'");
      const flagged = plain.indexOf("I (Vinayak's AI Assistant)");
      expect(flagged, slug).toBeGreaterThan(-1);
      expect(plain.match(/\bI\b(?! \(Vinayak)/)?.index ?? Infinity, slug).toBeGreaterThan(flagged);
    }
  }
});

test('a word post has the season shape', async ({ page }) => {
  await page.goto('what-is-an-item/');
  const h2 = await page.locator('article h2').allInnerTexts();
  expect(h2.slice(0, 4)).toEqual(['What does the word mean to each team?', 'What did it do at Store 014?', 'How does the industry pin it down?', 'What should you tell your agent?']);
});

test('the opener quotes Season 1’s three KPIs from the KPI list', async ({ page, request }) => {
  const list = yaml.load(await (await request.get('kpis/domain-kpis.yaml')).text()) as { domains: { kpis: { id: string; store_014: { reported: { value: string }; observed: { value: string }; example: string } }[] }[] };
  const k = (id: string) => list.domains.flatMap((d) => d.kpis).find((x) => x.id === id)!.store_014;
  const [osa, otif, upi] = [k('osa'), k('otif'), k('success-rate')];
  const text = await articleText(page, 'every-word/');
  const expected = [
    `On-shelf availability for 5 kg atta read ${osa.reported.value}. Observed on the shelf, it was ${osa.observed.value}.`,
    `On time, in full for June's deliveries read ${otif.reported.value}. With every case right, it was ${otif.observed.value}.`,
    `UPI payment success one Saturday evening read ${upi.reported.value} at the till and ${upi.observed.value} at the store's bank.`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  // "one Saturday evening": 20 June 2026, between 18:20 and 19:50.
  expect(upi.example).toContain('20 June');
  expect(new Date('2026-06-20T12:00:00Z').getUTCDay()).toBe(6);
});

test('the item post quotes the 22 June line and June’s fill rate correctly', async ({ page }) => {
  const text = await articleText(page, 'what-is-an-item/');
  const day = Number(st.shipment.arrived_ts.slice(8, 10));
  const pick = st.picks.find((x: { line: number }) => x.line === st.line.line);
  const expected = [
    `On ${day} June, the warehouse picked ${words[st.line.cases]} cases for Store 014's 5 kg atta line.`,
    'It confirmed the pick by scanning the label on the slot, and it had picked from the 1 kg slot next door.',
    `The shipping notice said ${st.line.units} bags of 5 kg. The cases held ${st.actual.units_actual} packs of 1 kg.`,
    `receiving scanned the pallet's label against the notice and booked ${st.receipt.units_booked} bags of 5 kg.`,
    `By the notices, ${lai.fill.shipped} of the ${lai.fill.ordered} cases ordered in June arrived – a fill rate of ${pct1(lai.fill.by_notice)}.`,
    `Counting only cases of the right item, it was ${pct1(lai.fill.right_item)}.`,
    `None of June's ${lai.pallets.total} pallets was weighed or scanned case by case.`,
    `the ${words[lai.fill.wrong_item_cases]} wrong cases stand out the day they arrive`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(st.line.sku).toBe('ATTA-WW-5KG');
  expect(st.actual.sku_actual).toBe('ATTA-WW-1KG');
  expect(st.line.cases).toBe(lai.fill.wrong_item_cases);
  expect(pick.cases_confirmed).toBe(st.line.cases);
  expect(pick.confirmed_by).toBe('slot label scan');
  expect(st.receipt.receipt_method).toContain('pallet label');
  expect(st.receipt.sku_booked).toBe('ATTA-WW-5KG');
  expect(lai.pallets.weighed).toBe(0);
  expect(lai.pallets.case_scanned).toBe(0);
  const wrong = logistics.scenarios[0].events.find((e: { kind: string }) => e.kind === 'wrong_pallet');
  expect(wrong.detail).toContain('adjacent 1 kg slot');
});

test('previous and next stay within Season 2', async ({ page }) => {
  await page.goto('every-word/');
  await expect(page.locator('.pager a')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/glossary-to-graph/"]')).toHaveCount(1);
  await page.goto('what-is-an-item/');
  await expect(page.locator('.pager a[href$="/four-kb-note/"]')).toHaveCount(1);
  await page.goto('who-saw-what/');
  await expect(page.locator('.pager a[href$="/every-word/"]')).toHaveCount(0);
  await page.goto('every-barrel/');
  await expect(page.locator('.pager a[href$="/what-is-an-item/"]')).toHaveCount(0);
});
