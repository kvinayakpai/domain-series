// Draws the full Store 014 ontology (src/data/ontology.json) as one picture: the core on top, then the
// truck, the shelf and the money, with the links between things and the rules (circled numbers) on the
// things they govern. It fails if a box or a label overlaps another, or leaves the picture.
//   node scripts/images/ontology-map.mjs [out.png] [--highlight=id,id,...]
import { chromium } from '@playwright/test';
import { mkdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { C } from './charts.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const font = (p) => `data:font/woff2;base64,${readFileSync(path.join(root, 'node_modules', p)).toString('base64')}`;
const O = JSON.parse(readFileSync(path.join(root, 'src', 'data', 'ontology.json'), 'utf8'));
const args = process.argv.slice(2);
const out = args.find((a) => !a.startsWith('--')) ?? path.join(root, 'public', 'images', 'store-014-ontology', 'map.png');
const highlight = (args.find((a) => a.startsWith('--highlight=')) ?? '').replace('--highlight=', '').split(',').filter(Boolean);

const W = 2400;
const H = 1950;
const ROW = (i) => 700 + (i - 1) * 202;
// x, y, width of each thing. Columns: the truck 120–540, the shelf 760–1600 (two sub-columns), the money 1720–2220.
const POS = {
  product: [80, 420, 340], item: [640, 420, 470], place: [1230, 420, 520], customer: [1870, 420, 450],
  order: [120, ROW(1), 420], pick: [120, ROW(2), 420], case: [120, ROW(3), 420], pallet: [120, ROW(4), 420], shipment: [120, ROW(5), 420], receiving: [120, ROW(6), 420],
  stock: [760, ROW(1), 350], 'stock-change': [1250, ROW(1), 350], forecast: [1250, ROW(2), 350], demand: [1250, ROW(3), 350],
  sale: [760, ROW(4), 350], 'lost-sale': [1250, ROW(4), 350], bill: [1250, ROW(5), 350],
  payment: [1720, ROW(1), 500], debit: [1720, ROW(2), 500], settlement: [1720, ROW(3), 500], refund: [1720, ROW(4), 500], complaint: [1720, ROW(5), 500],
};
// How each link leaves and enters its boxes, and where its words sit: side of the line, or above it.
const ROUTE = {
  'product>item': { a: ['right', 0.5], b: ['left', 0.5], label: 'above' },
  'order>pick': {}, 'pick>case': {}, 'case>pallet': {}, 'pallet>shipment': {}, 'shipment>receiving': {},
  'receiving>stock': { a: ['right', 0.5], b: ['left', 0.5], label: 'left', at: 0.78 },
  'stock-change>stock': { a: ['left', 0.5], b: ['right', 0.5], label: 'above' },
  'forecast>demand': {},
  'stock>sale': { at: 0.5 },
  'demand>sale': { a: ['bottom', 0.12], b: ['top', 0.88], label: 'left' },
  'demand>lost-sale': {},
  'sale>bill': { a: ['bottom', 0.88], b: ['top', 0.12], label: 'center' },
  'bill>payment': { a: ['right', 0.5], b: ['left', 0.5], label: 'center', at: 0.5 },
  'payment>debit': {}, 'debit>settlement': {},
  'debit>refund': { elbow: 'right', label: 'right' },
  'complaint>refund': { a: ['top', 0.5], b: ['bottom', 0.5] },
};
const COLS = [
  { x: 120, w: 420, name: 'The truck' },
  { x: 760, w: 840, name: 'The shelf' },
  { x: 1720, w: 500, name: 'The money' },
];

const esc = (s = '') => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const rulesOn = (id) => O.rules.filter((r) => r.on.includes(id)).map((r) => r.n);
const box = (t) => {
  const [x, y, w] = POS[t.id];
  const dim = highlight.length && !highlight.includes(t.id) ? ' dim' : '';
  const key = t.id === 'item' ? ' key' : '';
  const circles = rulesOn(t.id).map((n) => `<span class="rule">${n}</span>`).join('');
  return `<div class="thing${key}${dim}" id="t-${t.id}" style="left:${x}px;top:${y}px;width:${w}px">
    ${circles ? `<div class="rules">${circles}</div>` : ''}<div class="name">${esc(t.name)}</div><div class="says">${esc(t.says)}</div></div>`;
};
const recordsDim = highlight.length && !highlight.includes('records') ? ' dim' : '';

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Anek; font-weight: 100 800; font-stretch: 75% 125%;
  src: url(${font('@fontsource-variable/anek-latin/files/anek-latin-latin-standard-normal.woff2')}) format('woff2'); }
@font-face { font-family: Anek; font-weight: 100 800; font-stretch: 75% 125%; unicode-range: U+0100-024F, U+20A0-20C0, U+2212;
  src: url(${font('@fontsource-variable/anek-latin/files/anek-latin-latin-ext-standard-normal.woff2')}) format('woff2'); }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: ${W}px; height: ${H}px; }
body { position: relative; background: #f5f6f4; color: ${C.ink}; font-family: Anek, sans-serif; }
.eyebrow { position: absolute; left: 80px; top: 76px; font-weight: 700; font-size: 44px; letter-spacing: 0.14em; text-transform: uppercase; color: ${C.muted}; }
h1 { position: absolute; left: 80px; top: 136px; font-weight: 700; font-size: 104px; line-height: 1; letter-spacing: -0.012em; }
.sub { position: absolute; left: 80px; top: 262px; font-size: 46px; color: ${C.muted}; }
.band { position: absolute; font-weight: 700; font-size: 30px; letter-spacing: 0.14em; text-transform: uppercase; color: ${C.muted}; }
.col { position: absolute; top: 622px; font-weight: 700; font-size: 34px; letter-spacing: 0.12em; text-transform: uppercase; color: ${C.ink}; border-bottom: 3px solid ${C.ink}; padding-bottom: 6px; }
.thing { position: absolute; background: #fff; border: 2px solid #c3c8c2; border-radius: 18px; padding: 13px 20px 15px; }
.thing.key { background: ${C.band}; border-color: #d9bd2f; }
.thing.dim { opacity: 0.32; }
.name { font-weight: 700; font-size: 41px; line-height: 1.08; }
.says { font-size: 28px; line-height: 1.2; color: ${C.muted}; margin-top: 5px; }
.rules { position: absolute; top: -22px; right: 14px; display: flex; gap: 8px; }
.rule { width: 46px; height: 46px; border-radius: 50%; background: ${C.real}; color: #fff; font-weight: 700; font-size: 27px; display: flex; align-items: center; justify-content: center; }
.records { position: absolute; left: 760px; top: ${ROW(6)}px; width: 1460px; background: #fff; border: 2px solid #c3c8c2; border-radius: 18px; padding: 16px 22px 18px; }
.records.dim { opacity: 0.32; }
.records .rules { right: 14px; }
.records .row { font-size: 29px; line-height: 1.3; color: ${C.ink}; margin-top: 6px; }
.records .row b { font-weight: 700; }
.records .obs b { color: ${C.real}; }
.records .copy b { color: ${C.rec}; }
.foot { position: absolute; left: 80px; top: ${H - 62}px; font-size: 28px; color: ${C.muted}; }
svg { position: absolute; left: 0; top: 0; }
</style></head><body>
<div class="eyebrow">Why Domain Matters · Ontology</div>
<h1>The Store 014 ontology</h1>
<div class="sub">${O.things.length} things, how they link, and ${O.rules.length} rules (the circled numbers)</div>
<div class="band" style="left:80px;top:372px">The core</div>
${COLS.map((c) => `<div class="col" style="left:${c.x}px;width:${c.w}px">${c.name}</div>`).join('')}
${O.things.map(box).join('\n')}
<div class="records${recordsDim}" id="t-records"><div class="rules"><span class="rule">12</span></div>
  <div class="name">Records: who saw what</div>
  <div class="row obs"><b>Look at the world:</b> ${esc(O.records.observe.join(', '))}</div>
  <div class="row copy"><b>Copy another record:</b> ${esc(O.records.copy.join(', '))}</div></div>
<div class="foot">Store 014 is a simulated supermarket in Bengaluru, with its warehouse, trucks, tills and bank.</div>
</body></html>`;

// Playwright's own browser in CI; a system Chrome where that is not installed.
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath: process.env.CHROME ?? '/usr/bin/google-chrome' });
}
const page = await browser.newPage({ viewport: { width: W, height: H } });
await page.setContent(html);
await page.evaluate(() => document.fonts.ready);
const problems = await page.evaluate(({ links, ROUTE, highlight, C }) => {
  const rect = (id) => document.getElementById(`t-${id}`).getBoundingClientRect();
  const pt = (r, [side, t]) => ({
    top: [r.left + r.width * t, r.top], bottom: [r.left + r.width * t, r.bottom],
    left: [r.left, r.top + r.height * t], right: [r.right, r.top + r.height * t],
  })[side];
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', innerWidth); svg.setAttribute('height', innerHeight);
  svg.innerHTML = `<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="${C.muted}"/></marker>
    <marker id="arrow-dim" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c3c8c2"/></marker></defs>`;
  document.body.appendChild(svg);
  const labels = [];
  for (const l of links) {
    const key = `${l.from}>${l.to}`;
    const r = ROUTE[key];
    if (!r) return [`no route for ${key}`];
    const A = rect(l.from), B = rect(l.to);
    const on = !highlight.length || (highlight.includes(l.from) && highlight.includes(l.to));
    const stroke = on ? C.muted : '#c3c8c2';
    let d, lx, ly, anchor = 'start';
    if (r.elbow === 'right') {
      const [x1, y1] = pt(A, ['right', 0.5]); const [x2, y2] = pt(B, ['right', 0.5]); const xe = Math.max(x1, x2) + 46;
      d = `M${x1},${y1} H${xe} V${y2} H${x2 + 4}`; lx = xe + 12; ly = (y1 + y2) / 2 + 9;
    } else {
      const [x1, y1] = pt(A, r.a ?? ['bottom', 0.5]); const [x2, y2] = pt(B, r.b ?? ['top', 0.5]);
      const len = Math.hypot(x2 - x1, y2 - y1); const ux = (x2 - x1) / len, uy = (y2 - y1) / len;
      d = `M${x1},${y1} L${x2 - ux * 4},${y2 - uy * 4}`;
      const at = r.at ?? 0.5; const mx = x1 + (x2 - x1) * at, my = y1 + (y2 - y1) * at;
      const side = r.label ?? 'right';
      if (side === 'right') { lx = mx + 14; ly = my + 9; }
      if (side === 'left') { lx = mx - 14; ly = my + 9; anchor = 'end'; }
      if (side === 'above') { lx = mx; ly = my - 12; anchor = 'middle'; }
      if (side === 'center') { lx = mx; ly = my + 9; anchor = 'middle'; }
    }
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', d); p.setAttribute('fill', 'none'); p.setAttribute('stroke', stroke); p.setAttribute('stroke-width', '3.5');
    p.setAttribute('marker-end', `url(#${on ? 'arrow' : 'arrow-dim'})`);
    svg.appendChild(p);
    const t = document.createElementNS(NS, 'text');
    t.textContent = l.says; t.setAttribute('x', lx); t.setAttribute('y', ly); t.setAttribute('text-anchor', anchor);
    t.setAttribute('font-family', 'Anek'); t.setAttribute('font-size', '27'); t.setAttribute('font-style', 'italic');
    t.setAttribute('fill', on ? C.ink : '#b5bab4'); t.setAttribute('stroke', '#f5f6f4'); t.setAttribute('stroke-width', '9');
    t.setAttribute('paint-order', 'stroke'); t.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(t);
    labels.push({ key, el: t });
  }
  // Checks: boxes inside the picture and apart; labels clear of boxes and of each other.
  const out = [];
  const boxes = [...document.querySelectorAll('.thing, .records, .col, .band, h1, .sub, .eyebrow, .foot')].map((el) => ({ id: el.id || el.className, r: el.getBoundingClientRect() }));
  const hit = (a, b, pad = 0) => a.left < b.right + pad && b.left < a.right + pad && a.top < b.bottom + pad && b.top < a.bottom + pad;
  for (const b of boxes) if (b.r.left < 0 || b.r.top < 0 || b.r.right > innerWidth || b.r.bottom > innerHeight) out.push(`${b.id} leaves the picture`);
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) if (hit(boxes[i].r, boxes[j].r, 6)) out.push(`${boxes[i].id} overlaps ${boxes[j].id}`);
  const lb = labels.map((l) => ({ key: l.key, r: l.el.getBoundingClientRect() }));
  for (const l of lb) {
    if (l.r.right > innerWidth - 10 || l.r.left < 10) out.push(`label ${l.key} leaves the picture`);
    for (const b of boxes) if (hit(l.r, b.r, 2)) out.push(`label ${l.key} overlaps ${b.id}`);
  }
  for (let i = 0; i < lb.length; i++) for (let j = i + 1; j < lb.length; j++) if (hit(lb[i].r, lb[j].r, 2)) out.push(`label ${lb[i].key} overlaps label ${lb[j].key}`);
  // The thing boxes must be shorter than a row, so the links between rows have room.
  for (const el of document.querySelectorAll('.thing')) if (el.getBoundingClientRect().height > 152) out.push(`${el.id} is ${Math.round(el.getBoundingClientRect().height)}px tall`);
  return out;
}, { links: O.links, ROUTE, highlight, C });
if (problems.length) { await browser.close(); throw new Error(`ontology map:\n  ${problems.join('\n  ')}`); }
mkdirSync(path.dirname(out), { recursive: true });
await page.screenshot({ path: out });
await browser.close();
console.log(`wrote ${path.relative(process.cwd(), out)}`);
