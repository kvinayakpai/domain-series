// Renders the 1200x630 link-preview images into public/og/ with the site's fonts.
// Run after changing a post's title, record or reality line: npm run og
import { chromium } from '@playwright/test';
import { readFileSync, readdirSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Fonts are inlined as data URIs: a page created with setContent cannot load file:// fonts.
const font = (p) => `data:font/woff2;base64,${readFileSync(path.join(root, 'node_modules', p)).toString('base64')}`;
const outDir = path.join(root, 'public', 'og');
mkdirSync(outDir, { recursive: true });

const fontCss = `
@font-face { font-family: Anek; font-weight: 100 800; font-stretch: 75% 125%;
  src: url(${font('@fontsource-variable/anek-latin/files/anek-latin-latin-standard-normal.woff2')}) format('woff2'); }
@font-face { font-family: Anek; font-weight: 100 800; font-stretch: 75% 125%; unicode-range: U+0100-024F, U+20A0-20C0;
  src: url(${font('@fontsource-variable/anek-latin/files/anek-latin-latin-ext-standard-normal.woff2')}) format('woff2'); }
@font-face { font-family: Literata; font-weight: 200 900;
  src: url(${font('@fontsource-variable/literata/files/literata-latin-opsz-normal.woff2')}) format('woff2'); }
@font-face { font-family: Literata; font-weight: 200 900; unicode-range: U+0100-024F, U+20A0-20C0;
  src: url(${font('@fontsource-variable/literata/files/literata-latin-ext-opsz-normal.woff2')}) format('woff2'); }
@font-face { font-family: PlexMono; font-weight: 400;
  src: url(${font('@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2')}) format('woff2'); }
@font-face { font-family: PlexMono; font-weight: 400; unicode-range: U+0100-024F, U+20A0-20C0;
  src: url(${font('@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-ext-400-normal.woff2')}) format('woff2'); }
`;

const esc = (s = '') => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

function readPosts() {
  const dir = path.join(root, 'src', 'content', 'posts');
  return readdirSync(dir).filter((f) => f.endsWith('.md')).map((f) => {
    const fm = readFileSync(path.join(dir, f), 'utf8').split('---')[1];
    const get = (k) => (fm.match(new RegExp(`^${k}:\\s*"(.*)"\\s*$`, 'm')) || [])[1];
    return { name: get('slug'), title: get('title'), record: get('record'), reality: get('reality') };
  });
}

const cards = [
  { name: 'home', title: 'Why domain matters', lede: 'Every system keeps a record. Domain knowledge is knowing when the record is wrong, and why.' },
  { name: 'demo', title: 'One grocery basket, three domains', lede: 'A supermarket in Bengaluru, its warehouse and its milk route. Synthetic, seeded, and the same for every reader.' },
  ...readPosts(),
];

function html(c) {
  const body = c.record
    ? `<dl>
         <dt>The record says</dt><dd class="rec">${esc(c.record)}</dd>
         <dt>What actually happened</dt><dd class="real"><span>${esc(c.reality)}</span></dd>
       </dl>`
    : `<p class="lede">${esc(c.lede)}</p>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    ${fontCss}
    * { box-sizing: border-box; margin: 0; }
    html, body { width: 1200px; height: 630px; }
    body { background: #f5f6f4; color: #1b2430; font-family: Literata, serif; padding: 64px 72px; display: flex; flex-direction: column; }
    .series { font-family: Anek; font-weight: 700; font-stretch: 75%; font-size: 30px; }
    h1 { font-family: Anek; font-weight: 660; font-stretch: 78%; font-size: 92px; line-height: 0.98; margin-top: 28px; letter-spacing: -0.01em; }
    dl { margin-top: 36px; display: grid; gap: 6px; }
    dt { font-family: Anek; font-size: 24px; color: #59626d; font-weight: 500; }
    dd { margin-bottom: 14px; }
    .rec { font-family: PlexMono; color: #2f55a4; font-size: 34px; letter-spacing: -0.01em; }
    .real span { font-size: 40px; line-height: 1.3; background: #ffe14d; padding: 0 8px; box-decoration-break: clone; }
    .lede { font-size: 38px; line-height: 1.35; margin-top: 30px; max-width: 980px; }
    .url { margin-top: auto; font-family: Anek; font-size: 24px; color: #59626d; }
  </style></head><body>
    ${c.name === 'home' ? '' : '<div class="series">Why Domain Matters</div>'}
    <h1>${esc(c.title)}</h1>
    ${body}
    <div class="url">kvinayakpai.github.io/domain-series</div>
  </body></html>`;
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
for (const c of cards) {
  await page.setContent(html(c), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const file = path.join(outDir, `${c.name}.png`);
  await page.screenshot({ path: file });
  console.log('wrote', path.relative(root, file));
}
await browser.close();
