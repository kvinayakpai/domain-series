import { test, expect } from '@playwright/test';

const pages = [
  { path: './', og: 'home' },
  { path: 'why-domain/', og: 'why-domain' },
  { path: 'kpis/', og: 'kpis' },
  { path: 'retail/', og: 'retail' },
  { path: 'retail/technical/', og: 'retail' },
  { path: 'logistics/', og: 'logistics' },
  { path: 'logistics/technical/', og: 'logistics' },
  { path: 'payments/', og: 'payments' },
  { path: 'payments/technical/', og: 'payments' },
  { path: 'who-saw-what/', og: 'who-saw-what' },
  ...['on-shelf-availability', 'lost-sales', 'like-for-like', 'forecast-accuracy', 'inventory-accuracy', 'days-of-supply', 'shrink',
    'fresh-waste', 'otif', 'fill-rate', 'pick-accuracy', 'net-adjustments', 'on-time-arrival', 'payment-success', 'charged-twice',
    'match-rate', 'refund-turnaround', 'technical-declines', 'bench', 'dbt-tests'].map((slug) => ({ path: `${slug}/`, og: slug })),
  { path: 'kit/', og: 'kit' },
  { path: 'demo/', og: 'demo' },
  { path: 'data/', og: 'home' },
];

for (const p of pages) {
  test(`${p.path} renders cleanly`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });

    const res = await page.goto(p.path);
    expect(res?.status()).toBe(200);
    await expect(page.locator('h1')).toBeVisible();

    // No sideways scrolling on any screen size.
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);

    // Link previews point at an absolute image URL for this page.
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute(
      'content',
      `https://kvinayakpai.github.io/domain-series/og/${p.og}.png`,
    );
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', /^https:\/\/kvinayakpai\.github\.io\/domain-series\//);

    expect(errors).toEqual([]);
  });
}

test('link-preview images are served', async ({ request }) => {
  for (const p of pages.filter((x) => x.path !== 'data/' && !x.path.endsWith('technical/'))) {
    const res = await request.get(`og/${p.og}.png`);
    expect(res.status(), p.og).toBe(200);
    expect(res.headers()['content-type']).toContain('image/png');
  }
});

test('home leads with the opener and lists every post by part', async ({ page }) => {
  await page.goto('./');
  await expect(page.locator('.start a[href$="/why-domain/"]')).toHaveCount(1);
  for (const slug of ['retail', 'logistics', 'payments', 'who-saw-what', 'on-shelf-availability', 'technical-declines', 'dbt-tests']) {
    await expect(page.locator(`.part-posts a[href$="/${slug}/"]`)).toHaveCount(1);
  }
  await expect(page.locator('a[href$="/kpis/"]').first()).toBeVisible();
});

// Every claim in the series links to its evidence, so every link on every post must land: the page
// must exist, and so must the section it points at.
test('every link on every post lands on a page and a section that exist', async ({ page, request }) => {
  test.setTimeout(120_000);
  await page.goto('./');
  const posts = [...new Set(await page.locator('.start a, .part-posts a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).pathname)))];
  expect(posts).toHaveLength(25);
  const ids = new Map<string, Set<string>>();
  const idsOf = async (path: string) => {
    if (!ids.has(path)) {
      const res = await request.get(path.replace('/domain-series/', ''));
      expect(res.status(), path).toBe(200);
      const html = await res.text();
      ids.set(path, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
    }
    return ids.get(path)!;
  };
  for (const post of posts) {
    await page.goto(post.replace('/domain-series/', ''));
    const hrefs = await page.locator('article a[href]').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).href));
    for (const href of hrefs) {
      const u = new URL(href);
      if (u.origin !== new URL(page.url()).origin) continue;
      if (/\.[a-z0-9]+$/i.test(u.pathname)) {
        expect((await request.head(u.pathname.replace('/domain-series/', ''))).status(), `${post} -> ${href}`).toBe(200);
        continue;
      }
      const found = await idsOf(u.pathname);
      if (u.hash) expect(found.has(decodeURIComponent(u.hash.slice(1))), `${post} -> ${href}`).toBe(true);
    }
  }
});

test('each KPI post has the same shape and gives its agent the KPI page’s rule', async ({ page }) => {
  await page.goto('kpis/');
  const rules = Object.fromEntries(await page.locator('section.kpi').evaluateAll((els) => els.map((e) => [e.id, (e.querySelector('.kpi-rule') as HTMLElement).innerText.trim()])));
  const links = await page.locator('section.kpi .kpi-post a').evaluateAll((as) => as.map((a) => [(a.closest('section.kpi') as HTMLElement).id, (a as HTMLAnchorElement).pathname]));
  expect(links).toHaveLength(18);
  for (const [id, path] of links) {
    await page.goto(path.replace('/domain-series/', ''));
    const h2 = await page.locator('article h2').allInnerTexts();
    for (const section of ['Why the number missed it', 'How to catch it', 'If an AI agent reads it', 'Try it on your own data']) expect(h2, `${path}: ${section}`).toContain(section);
    await expect(page.locator('.agent-rule-text')).toHaveText(rules[id]);
    await expect(page.locator('.post-domain')).toHaveText(/^The (shelf|truck|money): KPI \d of [58]$/);
    await expect(page.locator('dl.pair .rec')).not.toBeEmpty();
  }
});

test('posts show a byline and link to their demo scenario', async ({ page }) => {
  for (const slug of ['retail', 'logistics', 'payments']) {
    await page.goto(`${slug}/`);
    await expect(page.locator('.byline')).toContainText('Vinayak');
    const demo = page.locator(`a[href$="/demo/#${slug}"]`);
    expect(await demo.count()).toBeGreaterThanOrEqual(1);
  }
  await page.goto('demo/');
  for (const slug of ['retail', 'logistics', 'payments']) {
    await expect(page.locator(`#${slug}`)).toHaveCount(1);
  }
});

test('the records page lists every retail file, and each is served', async ({ page, request }) => {
  await page.goto('data/');
  const links = await page.locator('#retail-records + .table-wrap a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')));
  expect(links).toContain('/domain-series/data/india-grocery/pos-lines-may-june.csv');
  expect(links).toContain('/domain-series/data/india-grocery/fresh-deliveries-june.csv');
  for (const href of links) {
    const res = await request.head(href!.replace('/domain-series/', ''));
    expect(res.status(), href!).toBe(200);
  }
  await expect(page.locator('a[href$="/retail/technical/"]')).toHaveCount(1);
});

test('RSS feed and sitemap are served', async ({ request }) => {
  const rss = await request.get('rss.xml');
  expect(rss.status()).toBe(200);
  expect(await rss.text()).toContain('<title>Why Domain Matters</title>');
  const sitemap = await request.get('sitemap-index.xml');
  expect(sitemap.status()).toBe(200);
});
