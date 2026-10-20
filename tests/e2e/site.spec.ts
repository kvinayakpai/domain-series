import { test, expect } from '@playwright/test';

const pages = [
  { path: './', og: 'home' },
  { path: 'retail/', og: 'retail' },
  { path: 'retail/technical/', og: 'retail' },
  { path: 'logistics/', og: 'logistics' },
  { path: 'payments/', og: 'payments' },
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

test('home lists every post with its record and reality', async ({ page }) => {
  await page.goto('./');
  const rows = page.locator('table.audit tbody tr');
  await expect(rows).toHaveCount(3);
  for (const slug of ['retail', 'logistics', 'payments']) {
    await expect(page.locator(`table.audit a[href$="/${slug}/"]`)).toHaveCount(1);
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
