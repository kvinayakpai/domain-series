import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The Oil & Gas season: its contents page, its posts, and the Field 014 numbers they quote. Every
// number must still match the simulation's output (src/data/oil-gas/field-014.json), so changing
// the generator fails the build until the prose is updated.
const field = JSON.parse(readFileSync(new URL('../../src/data/oil-gas/field-014.json', import.meta.url), 'utf8'));
const s = field.story;
const days = field.meta.days as string[];
const n = (v: number) => Math.round(v).toLocaleString('en-IN');
const dayOf = (iso: string) => Number(iso.slice(8, 10));
const words: Record<number, string> = { 2: 'two', 3: 'three', 9: 'nine', 15: 'fifteen', 16: 'sixteen' };
const SEASON_POSTS = ['every-barrel/', 'production/'];

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  // Typographic quotes in the page compare equal to plain ones in the expectations.
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}

for (const p of [{ path: 'oil-and-gas/', og: 'oil-and-gas' }, { path: 'every-barrel/', og: 'every-barrel' }, { path: 'production/', og: 'production' }]) {
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

test('home points to the season, and the season page lists its KPIs and records', async ({ page, request }) => {
  await page.goto('./');
  await expect(page.locator('.season-next a[href$="/oil-and-gas/"]')).toHaveCount(1);
  await expect(page.locator('.season-next a[href$="/every-barrel/"]')).toHaveCount(1);
  await page.goto('oil-and-gas/');
  await expect(page.locator('.opener a[href$="/every-barrel/"]')).toHaveCount(1);
  await expect(page.locator('.og-posts li')).toHaveCount(18);
  await expect(page.locator('.og-posts a[href$="/production/"]')).toHaveText('KPI 1: Production');
  const files = await page.locator('.files a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')!));
  expect(files).toHaveLength(6);
  for (const f of files) {
    const res = await request.head(f.replace('/domain-series/', ''));
    expect(res.status(), f).toBe(200);
  }
});

test('season posts link only to outside sources, carry the AI line and three described pictures', async ({ page, request }) => {
  for (const post of SEASON_POSTS) {
    await page.goto(post);
    const prose = 'article > p a[href], article > ul a[href], article > ol a[href], article > blockquote a[href]';
    const own = await page.locator(prose).evaluateAll((as) =>
      as.map((a) => a as HTMLAnchorElement).filter((a) => a.origin === location.origin).map((a) => a.getAttribute('href')),
    );
    expect(own, post).toEqual([]);
    await expect(page.locator('article'), post).toContainText(/written by AI and engineered by Vinayak/);
    await expect(page.locator('article'), post).toContainText('Curious to know what you think');
    const imgs = await page.locator('article figure.picture img').evaluateAll((els) => els.map((e) => ({ src: (e as HTMLImageElement).getAttribute('src')!, alt: (e as HTMLImageElement).alt })));
    expect(imgs.length, post).toBe(3);
    for (const img of imgs) {
      expect(img.alt.length, `${post} ${img.src}`).toBeGreaterThan(60);
      const res = await request.head(img.src.replace('/domain-series/', ''));
      expect(res.status(), img.src).toBe(200);
    }
  }
});

test('the KPI post has the series shape and gives its agent the KPI list’s rule', async ({ page, request }) => {
  const yaml = await (await request.get('oil-and-gas/kpis.yaml')).text();
  const rule = JSON.parse(yaml.match(/id: og-production[\s\S]*?agent_rule: (".*")/)![1]);
  await page.goto('production/');
  const h2 = await page.locator('article h2').allInnerTexts();
  expect(h2.slice(0, 4)).toEqual(['What is it?', 'What did it say at Field 014?', 'What could it not see?', 'How do you catch it?']);
  await expect(page.locator('.post-domain')).toHaveText('Oil & Gas · KPI 1 of 18 · the well');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  expect(text).toContain(`The rule I would give any AI agent that reads it – ${rule}`);
});

test('the production post quotes Field 014 correctly', async ({ page }) => {
  const text = await articleText(page, 'production/');
  const af18 = field.daily.af[days.indexOf('2026-03-18')];
  const expected = [
    `It has ${words[s.field.wells]} wells, each lifted by an electric submersible pump`,
    `the morning report shows Well 14, the field's best well, at ${n(s.w14_18mar.allocated)} barrels, close to the ${s.w14_test.oil_bpd} of its last test`,
    `The allocation factor reads ${af18.toFixed(2)}`,
    `It produced ${n(s.w14_18mar.produced)} barrels that day`,
    `Its pump had been wearing since ${dayOf(s.pump.wear_from)} March, and its last test was on ${dayOf(s.w14_test.date)} February`,
    `the test separator was out of service from ${dayOf(s.separator.out_from)} to ${dayOf(s.separator.out_to)} March`,
    `On ${dayOf(s.pump.trip)} March the pump tripped, and early on ${dayOf(s.pump.stop)} March it stopped for good`,
    `The allocation said ${n(s.w14_18mar.allocated)} barrels. The well produced ${n(s.w14_18mar.produced)}.`,
    `From ${dayOf(s.overstated.from)} to ${dayOf(s.overstated.to)} March the report gave Well 14 ${n(s.overstated.extra_bbl)} barrels it never produced, and took them from the other ${words[s.field.wells - 1]} wells, each about ${s.overstated.others_understated_pct}% low`,
    `The meter was never more than ${s.meter.max_daily_error_pct}% out on any day`,
    `from ${s.af.first_week_mean.toFixed(2)} in the first days of March to ${s.af.on_18mar.toFixed(2)}`,
    `Well 14's test was ${s.w14_test.age_days_at_stop} days old when its pump stopped`,
    `Well 14's allocated rate ran more than 10% above its pump-data estimate from ${dayOf(s.check.first_flag_w14)} March, ${words[s.check.days_before_stop]} days before the pump stopped`,
    `The same check also flagged Well 2 for ${words[s.check.other_flag_days]} days`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(s.check.other_wells_flagged).toEqual(['W-02']);
  expect(s.pump.stop.startsWith('2026-03-20T0')).toBe(true); // "early on 20 March"
  // "the field is a little down": the meter on 18 March against 1 March.
  const drop = 1 - field.daily.metered[days.indexOf('2026-03-18')] / field.daily.metered[0];
  expect(drop).toBeGreaterThan(0);
  expect(drop).toBeLessThan(0.05);
});

test('the start post quotes Field 014 correctly and pages within the season', async ({ page }) => {
  const text = await articleText(page, 'every-barrel/');
  const expected = [
    `with ${words[s.field.wells]} wells, each lifted by an electric submersible pump`,
    `the production report credited Well 14, the field's best well, with ${n(s.w14_18mar.allocated)} barrels. It produced ${n(s.w14_18mar.produced)}`,
    `Its last test was ${s.w14_test.age_days_at_stop} days old when the pump stopped on ${dayOf(s.pump.stop)} March`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  // "its pump had been wearing for two weeks" on 18 March
  const wearDays = dayOf('2026-03-18') - dayOf(s.pump.wear_from);
  expect(wearDays).toBeGreaterThanOrEqual(12);
  expect(wearDays).toBeLessThanOrEqual(15);
  // Previous and next stay within the season.
  await expect(page.locator('.pager a')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/production/"]')).toHaveCount(1);
  await page.goto('who-saw-what/');
  await expect(page.locator('.pager a[href$="/every-barrel/"]')).toHaveCount(0);
});
