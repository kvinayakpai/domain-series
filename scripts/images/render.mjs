// Renders each post's three images (open, summary, close) into public/images/<slug>/.
// The words and numbers come from cards.mjs, which reads the KPI list the site builds
// (dist/kpis/domain-kpis.yaml) and the downloadable records, so a card cannot drift from its post.
// Run after `npm run build`: node scripts/images/render.mjs [slug ...]
import { chromium } from '@playwright/test';
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { CARDS as STORE_CARDS } from './cards.mjs';
import { OIL_GAS_CARDS } from './oil-gas-cards.mjs';

const CARDS = [...STORE_CARDS, ...OIL_GAS_CARDS];
import { CHARTS, C } from './charts.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const font = (p) => `data:font/woff2;base64,${readFileSync(path.join(root, 'node_modules', p)).toString('base64')}`;

const W = 2400;
const H = 1350;

const fontCss = `
@font-face { font-family: Anek; font-weight: 100 800; font-stretch: 75% 125%;
  src: url(${font('@fontsource-variable/anek-latin/files/anek-latin-latin-standard-normal.woff2')}) format('woff2'); }
@font-face { font-family: Anek; font-weight: 100 800; font-stretch: 75% 125%; unicode-range: U+0100-024F, U+20A0-20C0, U+2212;
  src: url(${font('@fontsource-variable/anek-latin/files/anek-latin-latin-ext-standard-normal.woff2')}) format('woff2'); }
@font-face { font-family: Literata; font-weight: 200 900;
  src: url(${font('@fontsource-variable/literata/files/literata-latin-opsz-normal.woff2')}) format('woff2'); }
@font-face { font-family: Literata; font-weight: 200 900; unicode-range: U+0100-024F, U+20A0-20C0;
  src: url(${font('@fontsource-variable/literata/files/literata-latin-ext-opsz-normal.woff2')}) format('woff2'); }
`;

const css = `
${fontCss}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: ${W}px; height: ${H}px; }
body { background: #f5f6f4; color: ${C.ink}; font-family: Anek, sans-serif; padding: 96px 120px 88px; display: flex; flex-direction: column; }
.eyebrow { font-weight: 700; font-size: 46px; letter-spacing: 0.14em; text-transform: uppercase; color: ${C.muted}; }
h1 { font-weight: 700; font-size: 124px; line-height: 1.02; letter-spacing: -0.012em; margin-top: 26px; }
.sub { font-weight: 400; font-size: 62px; color: ${C.muted}; margin-top: 26px; line-height: 1.25; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 44px; margin-top: 64px; }
.panel { background: #eceeea; border-radius: 28px; padding: 56px 64px 64px; }
.label { font-weight: 700; font-size: 46px; letter-spacing: 0.12em; text-transform: uppercase; color: ${C.muted}; }
.big { font-size: 280px; line-height: 0.95; margin-top: 18px; letter-spacing: -0.02em; white-space: nowrap; }
.big.rep { color: ${C.rec}; font-weight: 350; }
.big.obs { color: ${C.real}; font-weight: 700; }
.cap { font-size: 60px; color: ${C.muted}; margin-top: 18px; line-height: 1.25; }
.line { margin-top: auto; font-weight: 700; font-size: 88px; line-height: 1.12; }
.chips { display: flex; flex-wrap: wrap; gap: 28px; margin-top: 64px; }
.chip { background: #eceeea; border-radius: 22px; padding: 26px 40px; font-size: 58px; font-weight: 600; }
.chip b { color: ${C.real}; font-weight: 700; margin-right: 16px; }
.quote { margin-top: 56px; background: ${C.band}; border-radius: 28px; padding: 60px 72px 66px; }
.quote .label { color: ${C.ink}; opacity: 0.75; }
.quote p { font-family: Literata, serif; font-weight: 600; font-size: 92px; line-height: 1.22; margin-top: 22px; }
.checks { display: grid; grid-template-columns: repeat(3, 1fr); gap: 44px; margin-top: 56px; margin-bottom: 48px; }
.check { border-top: 6px solid ${C.ink}; padding-top: 26px; font-size: 54px; line-height: 1.2; }
.check b { display: block; font-size: 42px; letter-spacing: 0.12em; text-transform: uppercase; color: ${C.muted}; margin-bottom: 14px; }
.foot { margin-top: auto; display: flex; justify-content: space-between; align-items: baseline; gap: 48px; font-size: 52px; color: ${C.muted}; }
.foot b { color: ${C.ink}; font-weight: 700; }
.chart { margin-top: 28px; flex: 1; position: relative; }
.legend { display: flex; gap: 64px; font-size: 54px; color: ${C.muted}; margin-top: 30px; align-items: center; }
.key { display: inline-block; width: 48px; height: 48px; border-radius: 8px; vertical-align: -6px; margin-right: 16px; }
`;

const esc = (s = '') => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const page = (body) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${body}</body></html>`;
const eyebrow = (c) => `<div class="eyebrow">${esc(c.eyebrow)}</div>`;
const fit = (s, sizes) => sizes.find(([n]) => s.length <= n)?.[1] ?? sizes.at(-1)[1];

/** Opening card: the KPI and its two numbers, or for other posts, what the post links. */
function openCard(c) {
  const h1 = `<h1 style="font-size:${fit(c.headline, [[36, 124], [48, 108], [999, 96]])}px">${esc(c.headline)}</h1>`;
  const sub = c.scope ? `<div class="sub">${esc(c.scope)}</div>` : '';
  const pair = c.reported
    ? `<div class="pair">
        <div class="panel"><div class="label">${esc(c.reported.label ?? 'Reported')}</div><div class="big rep" style="font-size:${fit(c.reported.value, [[5, 280], [8, 210], [99, 160]])}px">${esc(c.reported.value)}</div><div class="cap">${esc(c.reported.how)}</div></div>
        <div class="panel"><div class="label">${esc(c.observed.label ?? 'Observed')}</div><div class="big obs" style="font-size:${fit(c.observed.value, [[5, 280], [8, 210], [99, 160]])}px">${esc(c.observed.value)}</div><div class="cap">${esc(c.observed.how)}</div></div>
      </div>`
    : '';
  const chips = c.chips ? `<div class="chips">${c.chips.map((x) => `<span class="chip">${x.n ? `<b>${esc(x.n)}</b>` : ''}${esc(x.text)}</span>`).join('')}</div>` : '';
  return page(`${eyebrow(c)}${h1}${sub}${pair}${chips}<div class="line">${esc(c.blind)}</div>`);
}

/** Summary card: the chart that shows the whole post at a glance. */
function chartCard(c) {
  const ch = c.chart;
  const legend = ch.legend ? `<div class="legend">${ch.legend.map((l) => `<span><span class="key" style="background:${l.color}"></span>${esc(l.name)}</span>`).join('')}</div>` : '';
  const chartH = 1350 - 96 - 88 - 46 - 26 - 110 - 18 - 70 - (ch.legend ? 84 : 0) - (ch.note ? 92 : 0) - 28;
  const body = CHARTS[ch.type](ch, W - 240, chartH);
  return page(`${eyebrow(c)}
    <h1 style="font-size:${fit(ch.title, [[40, 104], [52, 92], [999, 84]])}px">${esc(ch.title)}</h1>
    <div class="sub" style="font-size:56px;margin-top:18px">${esc(ch.sub)}</div>
    ${legend}
    <div class="chart">${body}</div>
    ${ch.note ? `<div class="foot" style="margin-top:16px;font-size:50px;color:${C.ink}"><span>${esc(ch.note)}</span></div>` : ''}`);
}

/** Closing card: the lesson, the rule to give an AI agent, and three checks to run on your own data. */
function ruleCard(c) {
  const ruleSize = fit(c.rule, [[90, 92], [130, 80], [999, 68]]);
  return page(`${eyebrow(c)}
    <h1 style="font-size:${fit(c.lesson, [[34, 124], [44, 104], [999, 92]])}px">${esc(c.lesson)}</h1>
    <div class="quote"><div class="label">${esc(c.ruleLabel ?? 'Tell your AI agent')}</div><p style="font-size:${ruleSize}px">${esc(c.rule)}</p></div>
    <div class="checks">${c.checks.map((x, i) => `<div class="check"><b>${esc(c.checkLabel ?? 'Check')} ${i + 1}</b>${esc(x)}</div>`).join('')}</div>
    <div class="foot"><span>${esc(c.footLeft ?? 'Store 014 is a simulated supermarket in Bengaluru.')}</span>${c.next ? `<span>Next: <b>${esc(c.next)}</b></span>` : ''}</div>`);
}

const wanted = process.argv.slice(2);
const cards = wanted.length ? CARDS.filter((c) => wanted.includes(c.slug)) : CARDS;
if (wanted.length && cards.length !== wanted.length) throw new Error(`no card for: ${wanted.filter((w) => !CARDS.some((c) => c.slug === w)).join(', ')}`);
const executablePath = process.env.CHROME ?? (existsSync('/usr/bin/google-chrome') ? '/usr/bin/google-chrome' : undefined);
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath });
}
const tab = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
for (const c of cards) {
  const dir = path.join(root, 'public', 'images', c.slug);
  mkdirSync(dir, { recursive: true });
  for (const [name, make] of [['open', openCard], ['summary', chartCard], ['close', ruleCard]]) {
    await tab.setContent(make(c), { waitUntil: 'load' });
    await tab.evaluate(() => document.fonts.ready);
    const problems = await tab.evaluate(() => {
      const out = [];
      if (document.documentElement.scrollHeight > window.innerHeight || document.documentElement.scrollWidth > window.innerWidth) out.push('content overflows the card');
      // Text blocks must not run into each other.
      const boxes = [...document.querySelectorAll('h1, .sub, .pair, .chips, .line, .quote, .checks, .foot, .legend, .chart')].map((e) => [e.className || e.tagName, e.getBoundingClientRect()]);
      for (let i = 1; i < boxes.length; i++) if (boxes[i][1].top < boxes[i - 1][1].bottom - 2) out.push(`${boxes[i][0]} overlaps ${boxes[i - 1][0]}`);
      for (const e of document.querySelectorAll('svg text')) { const r = e.getBoundingClientRect(); const box = e.ownerSVGElement.getBoundingClientRect(); if (r.left < box.left - 1 || r.right > box.right + 1 || r.top < box.top - 1 || r.bottom > box.bottom + 1) out.push(`chart text cut: ${e.textContent}`); }
      for (const e of document.querySelectorAll('.big, .cap, .chip, h1')) if (e.scrollWidth > e.clientWidth + 2) out.push(`text too wide: ${e.textContent.slice(0, 40)}`);
      return out;
    });
    if (problems.length) throw new Error(`${c.slug}/${name}: ${problems.join('; ')}`);
    const file = path.join(dir, `${name}.png`);
    await tab.screenshot({ path: file });
    console.log('wrote', path.relative(root, file));
  }
}
await browser.close();
