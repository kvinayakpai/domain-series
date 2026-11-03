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
  // The KPI posts in reading order, then the two for practitioners.
  ...['sales', 'on-shelf-availability', 'lost-sales', 'inventory-accuracy', 'shrink', 'forecast-accuracy', 'days-of-supply',
    'fresh-waste', 'pick-accuracy', 'fill-rate', 'on-time-arrival', 'otif', 'net-adjustments', 'payment-success',
    'technical-declines', 'charged-twice', 'match-rate', 'refund-turnaround', 'bench', 'dbt-tests'].map((slug) => ({ path: `${slug}/`, og: slug })),
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
  for (const slug of ['sales', 'retail', 'logistics', 'payments', 'who-saw-what', 'on-shelf-availability', 'technical-declines', 'dbt-tests']) {
    await expect(page.locator(`.part-posts a[href$="/${slug}/"]`)).toHaveCount(1);
  }
  await expect(page.locator('a[href$="/kpis/"]').first()).toBeVisible();
});

// Every link on every post must land: the page must exist, and so must the section it points at.
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

// Since 2 November 2026 a post's prose links only to outside sources, and every post says that it was
// written by AI and engineered by its author. The layout's header, navigation, figures and media links stay.
test('posts link only to outside sources and carry the AI line', async ({ page }) => {
  await page.goto('./');
  const posts = [...new Set(await page.locator('.start a, .part-posts a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).pathname)))];
  expect(posts).toHaveLength(25);
  for (const post of posts) {
    await page.goto(post.replace('/domain-series/', ''));
    const prose = 'article > p a[href], article > ul a[href], article > ol a[href], article > blockquote a[href]';
    const own = await page.locator(prose).evaluateAll((as) =>
      as
        .map((a) => a as HTMLAnchorElement)
        .filter((a) => a.origin === location.origin && !a.pathname.endsWith('/demo/'))
        .map((a) => a.getAttribute('href')),
    );
    expect(own, post).toEqual([]);
    await expect(page.locator('article'), post).toContainText(/written by AI,? (and )?engineered by me/);
  }
});

test('each KPI post has the same shape and gives its agent the KPI page’s rule', async ({ page }) => {
  await page.goto('kpis/');
  const flat = (t: string) => t.replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"').trim();
  const kpis = await page.locator('section.kpi').evaluateAll((els) => els.map((e) => ({
    id: e.id,
    n: (e.querySelector('.kpi-n') as HTMLElement).innerText.trim(),
    rule: (e.querySelector('.kpi-rule') as HTMLElement).innerText,
    path: (e.querySelector('.kpi-post a') as HTMLAnchorElement).pathname,
  })));
  expect(kpis.map((k) => k.n)).toEqual(Array.from({ length: 18 }, (_, i) => `KPI ${i + 1}`));
  for (const k of kpis) {
    await page.goto(k.path.replace('/domain-series/', ''));
    const h2 = await page.locator('article h2').allInnerTexts();
    expect(h2.slice(0, 4), k.path).toEqual(['What is it?', 'What did it say at Store 014?', 'What could it not see?', 'How do you catch it?']);
    const text = flat(await page.locator('article').innerText());
    const esc = flat(k.rule).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    expect(text, k.path).toMatch(new RegExp(`The rule I would give any AI agent that reads (it|sales) – ${esc}`));
    expect(text, k.path).toContain('Curious to know what you think');
    await expect(page.locator('.post-domain'), k.path).toHaveText(new RegExp(`^${k.n} of 18 · the (shelf|truck|money)$`));
    // Every KPI post opens, summarises and closes with a picture.
    await expect(page.locator('article figure.picture img'), k.path).toHaveCount(3);
  }
});

// The pictures that open, summarise and close each post are served, and say what they show.
test('every picture in every post is served and described', async ({ page, request }) => {
  await page.goto('./');
  const posts = [...new Set(await page.locator('.start a, .part-posts a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).pathname)))];
  expect(posts).toHaveLength(25);
  for (const post of posts) {
    await page.goto(post.replace('/domain-series/', ''));
    const imgs = await page.locator('article figure.picture img').evaluateAll((els) => els.map((e) => ({ src: (e as HTMLImageElement).getAttribute('src')!, alt: (e as HTMLImageElement).alt })));
    expect(imgs.length, post).toBe(3);
    for (const img of imgs) {
      expect(img.alt.length, `${post} ${img.src}`).toBeGreaterThan(60);
      const res = await request.head(img.src.replace('/domain-series/', ''));
      expect(res.status(), img.src).toBe(200);
      expect(res.headers()['content-type'], img.src).toContain('image/png');
    }
  }
});

// The old like-for-like post became KPI 1, Sales. Old links still land.
test('the old like-for-like address redirects to the sales post', async ({ page }) => {
  await page.goto('like-for-like/');
  await expect(page).toHaveURL(/\/domain-series\/sales\/$/);
  await expect(page.locator('h1')).toContainText('Sales');
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
