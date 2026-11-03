// Renders each KPI post's three images (open, summary, close) into public/images/<slug>/.
// Every number on a card is computed from src/data/*.json in cards.mjs, the same files the posts use.
// Run: node scripts/images/render.mjs [slug ...]
import { chromium } from '@playwright/test';
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { CARDS } from './cards.mjs';

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

// The series' palette: blue = what a system records, orange = what really happened, yellow = the lesson.
const css = `
${fontCss}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: ${W}px; height: ${H}px; }
body { background: #f5f6f4; color: #1b2430; font-family: Anek, sans-serif; padding: 96px 120px 88px; display: flex; flex-direction: column; }
.eyebrow { font-weight: 700; font-size: 46px; letter-spacing: 0.14em; text-transform: uppercase; color: #59626d; }
h1 { font-weight: 700; font-size: 124px; line-height: 1.02; letter-spacing: -0.012em; margin-top: 26px; }
.sub { font-weight: 400; font-size: 62px; color: #59626d; margin-top: 26px; line-height: 1.25; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 44px; margin-top: 64px; }
.panel { background: #eceeea; border-radius: 28px; padding: 56px 64px 64px; }
.label { font-weight: 700; font-size: 46px; letter-spacing: 0.12em; text-transform: uppercase; color: #59626d; }
.big { font-size: 280px; line-height: 0.95; margin-top: 18px; letter-spacing: -0.02em; }
.big.rep { color: #2f55a4; font-weight: 350; }
.big.obs { color: #d4621c; font-weight: 700; }
.cap { font-size: 60px; color: #59626d; margin-top: 18px; line-height: 1.25; }
.line { margin-top: auto; font-weight: 700; font-size: 88px; line-height: 1.12; }
.quote { margin-top: 56px; background: #ffe14d; border-radius: 28px; padding: 60px 72px 66px; }
.quote .label { color: #1b2430; opacity: 0.75; }
.quote p { font-family: Literata, serif; font-weight: 600; font-size: 92px; line-height: 1.22; margin-top: 22px; }
.foot { margin-top: auto; display: flex; justify-content: space-between; align-items: baseline; gap: 48px; font-size: 52px; color: #59626d; }
.foot b { color: #1b2430; font-weight: 700; }
.chart { margin-top: 28px; flex: 1; position: relative; }
.checks { display: grid; grid-template-columns: repeat(3, 1fr); gap: 44px; margin-top: 56px; margin-bottom: 48px; }
.check { border-top: 6px solid #1b2430; padding-top: 26px; font-size: 54px; line-height: 1.2; }
.check b { display: block; font-size: 42px; letter-spacing: 0.12em; text-transform: uppercase; color: #59626d; margin-bottom: 14px; }
.legend { display: flex; gap: 64px; font-size: 54px; color: #59626d; margin-top: 30px; align-items: center; }
.key { display: inline-block; width: 48px; height: 48px; border-radius: 8px; vertical-align: -6px; margin-right: 16px; }
`;

const esc = (s = '') => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

function page(body) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${body}</body></html>`;
}

/** Opening card: the KPI, the question it answers, and its two numbers. */
function openCard(c) {
  return page(`
    <div class="eyebrow">Why Domain Matters · KPI ${c.n} of 18 · ${esc(c.kpi)}</div>
    <h1>${esc(c.headline)}</h1>
    <div class="sub">${esc(c.scope)}</div>
    <div class="pair">
      <div class="panel"><div class="label">Reported</div><div class="big rep">${esc(c.reported.value)}</div><div class="cap">${esc(c.reported.how)}</div></div>
      <div class="panel"><div class="label">Observed</div><div class="big obs">${esc(c.observed.value)}</div><div class="cap">${esc(c.observed.how)}</div></div>
    </div>
    <div class="line">${esc(c.blind)}</div>`);
}

/** Summary card: a daily bar chart of what was wanted against what the record shows, with the gap shaded. */
function chartCard(c) {
  const ch = c.chart;
  const cw = W - 240;
  const chH = 640;
  const left = 120;
  const bottom = chH - 80;
  const max = Math.ceil(Math.max(...ch.days.flatMap((d) => [d.a, d.b])) / 10) * 10;
  const slot = (cw - left - 20) / ch.days.length;
  const bw = slot * 0.36;
  const plotTop = 170;
  const y = (v) => bottom - (v / max) * (bottom - plotTop);
  const x = (i) => left + i * slot;
  const ticks = Array.from({ length: max / 10 + 1 }, (_, i) => i * 10); // top tick sits at plotTop, below the band label
  const band = ch.band;
  const bx0 = x(band.from.i) + band.from.frac * slot;
  const bx1 = x(band.to.i) + band.to.frac * slot;
  const svg = `<svg width="${cw}" height="${chH}" viewBox="0 0 ${cw} ${chH}" font-family="Anek">
    <rect x="${bx0}" y="0" width="${bx1 - bx0}" height="${bottom}" fill="#ffe14d" opacity="0.55" rx="10"/>
    <text x="${(bx0 + bx1) / 2}" y="66" text-anchor="middle" font-size="54" font-weight="700" fill="#1b2430">${esc(band.label)}</text>
    <text x="${(bx0 + bx1) / 2}" y="124" text-anchor="middle" font-size="46" fill="#1b2430">${esc(band.sub)}</text>
    ${ticks.map((t) => `<line x1="${left}" x2="${cw - 20}" y1="${y(t)}" y2="${y(t)}" stroke="#d5d9d4" stroke-width="2"/>
      <text x="${left - 24}" y="${y(t) + 13}" text-anchor="end" font-size="46" fill="#59626d">${t}</text>`).join('')}
    ${ch.days.map((d, i) => `
      <rect x="${x(i) + slot / 2 - bw - 4}" y="${y(d.a)}" width="${bw}" height="${bottom - y(d.a)}" fill="#d4621c" rx="6"/>
      <rect x="${x(i) + slot / 2 + 4}" y="${y(d.b)}" width="${bw}" height="${Math.max(bottom - y(d.b), 0)}" fill="#2f55a4" rx="6"/>
      <text x="${x(i) + slot / 2}" y="${bottom + 60}" text-anchor="middle" font-size="44" fill="#59626d">${esc(d.label)}</text>`).join('')}
    <line x1="${left}" x2="${cw - 20}" y1="${bottom}" y2="${bottom}" stroke="#59626d" stroke-width="3"/>
  </svg>`;
  return page(`
    <div class="eyebrow">Why Domain Matters · KPI ${c.n} of 18 · ${esc(c.kpi)}</div>
    <h1 style="font-size:104px">${esc(ch.title)}</h1>
    <div class="sub" style="font-size:56px;margin-top:18px">${esc(ch.sub)}</div>
    <div class="legend"><span><span class="key" style="background:#d4621c"></span>${esc(ch.aName)}</span><span><span class="key" style="background:#2f55a4"></span>${esc(ch.bName)}</span></div>
    <div class="chart">${svg}</div>
    <div class="foot" style="margin-top:16px;font-size:50px;color:#1b2430"><span>${esc(ch.note)}</span></div>`);
}

/** Closing card: the lesson, the rule to give an AI agent, and three checks to run on your own data. */
function ruleCard(c) {
  return page(`
    <div class="eyebrow">Why Domain Matters · KPI ${c.n} of 18 · ${esc(c.kpi)}</div>
    <h1 style="font-size:${c.lesson.length > 34 ? 104 : 124}px">${esc(c.lesson)}</h1>
    <div class="quote"><div class="label">Tell your AI agent</div><p>${esc(c.rule)}</p></div>
    <div class="checks">${c.checks.map((t, i) => `<div class="check"><b>Check ${i + 1}</b>${esc(t)}</div>`).join('')}</div>
    <div class="foot"><span>Store 014 is a simulated supermarket in Bengaluru.</span><span>Next: <b>${esc(c.next)}</b></span></div>`);
}

const wanted = process.argv.slice(2);
const cards = wanted.length ? CARDS.filter((c) => wanted.includes(c.slug)) : CARDS;
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
  for (const [name, html] of [['open', openCard(c)], ['summary', chartCard(c)], ['close', ruleCard(c)]]) {
    await tab.setContent(html, { waitUntil: 'load' });
    await tab.evaluate(() => document.fonts.ready);
    const overflow = await tab.evaluate(() => document.documentElement.scrollHeight > window.innerHeight || document.documentElement.scrollWidth > window.innerWidth);
    if (overflow) throw new Error(`${c.slug}/${name}: content overflows the ${W}x${H} card`);
    const file = path.join(dir, `${name}.png`);
    await tab.screenshot({ path: file });
    console.log('wrote', path.relative(root, file));
  }
}
await browser.close();
