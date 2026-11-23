// Whiteboard pictures: a post explained the way someone would draw it on a whiteboard, with marker
// handwriting, sketched boxes, numbered steps, arrows and a legend. Each board is a list of drawing
// commands (scripts/images/boards.mjs) that a page draws with rough.js and the Kalam handwriting font, then
// checks (no text spilling out of its box, nothing off the board) and saves as public/images/<slug>/board.png.
// Run after `npm run build`: node scripts/images/whiteboard.mjs [slug ...]
import { chromium } from '@playwright/test';
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { BOARDS } from './boards.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const nm = (p) => path.join(root, 'node_modules', p);
const font = (p) => `data:font/woff2;base64,${readFileSync(nm(p)).toString('base64')}`;
const ROUGH = readFileSync(nm('roughjs/bundled/rough.js'), 'utf8');

const css = `
@font-face { font-family: Kalam; font-weight: 400; src: url(${font('@fontsource/kalam/files/kalam-latin-400-normal.woff2')}) format('woff2'); }
@font-face { font-family: Kalam; font-weight: 700; src: url(${font('@fontsource/kalam/files/kalam-latin-700-normal.woff2')}) format('woff2'); }
@font-face { font-family: Kalam; font-weight: 400; unicode-range: U+0100-024F, U+20A0-20C0, U+2190-21FF, U+2212;
  src: url(${font('@fontsource/kalam/files/kalam-latin-ext-400-normal.woff2')}) format('woff2'); }
@font-face { font-family: Kalam; font-weight: 700; unicode-range: U+0100-024F, U+20A0-20C0, U+2190-21FF, U+2212;
  src: url(${font('@fontsource/kalam/files/kalam-latin-ext-700-normal.woff2')}) format('woff2'); }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #e9ebe8; }
svg { display: block; }
.t { font-family: Kalam, 'Comic Sans MS', cursive; line-height: 1.22; color: #1b2430; overflow: visible; }
.t b { font-weight: 700; }
.o { color: #c8521a; } .bl { color: #2f55a4; } .g { color: #15745a; } .gr { color: #6f766f; }
.hl { background: linear-gradient(transparent 12%, rgba(255, 225, 77, 0.85) 12%, rgba(255, 225, 77, 0.85) 88%, transparent 88%); padding: 0 0.12em; }
`;

// Drawing in the page. Every shape is rough.js with a fixed seed, so a board draws the same every time.
const RUNTIME = `
const INK = '#1b2430', C = { ink: INK, blue: '#2f55a4', orange: '#c8521a', green: '#15745a', grey: '#7d847d',
  yellow: '#ffe14d', paper: '#fdfdfa', noteY: '#fff3a3', noteB: '#dde8ff', noteG: '#d9f1e3', noteO: '#ffe0cc', noteGr: '#ebedea' };
const col = (c) => C[c] || c;
const svg = document.getElementById('board');
const rc = rough.svg(svg);
const NS = 'http://www.w3.org/2000/svg';
let seed = 7;
const o = (x = {}) => ({ roughness: 1.3, bowing: 1, strokeWidth: 5, stroke: INK, seed: seed++, ...x,
  ...(x.stroke ? { stroke: col(x.stroke) } : {}), ...(x.fill ? { fill: col(x.fill) } : {}) });
const add = (n) => { svg.appendChild(n); return n; };
const g = (rot, cx, cy) => { const e = document.createElementNS(NS, 'g'); if (rot) e.setAttribute('transform', 'rotate(' + rot + ' ' + cx + ' ' + cy + ')'); return add(e); };
function text(c) {
  const f = document.createElementNS(NS, 'foreignObject');
  f.setAttribute('x', c.x); f.setAttribute('y', c.y); f.setAttribute('width', c.w); f.setAttribute('height', c.h || 400);
  const d = document.createElement('div');
  d.className = 't'; d.dataset.check = c.check === false ? '' : '1';
  d.style.cssText = 'width:' + c.w + 'px;height:' + (c.h || 400) + 'px;font-size:' + (c.size || 56) + 'px;font-weight:' + (c.weight || 400) +
    ';color:' + col(c.color || 'ink') + ';text-align:' + (c.align || 'left') + ';display:flex;flex-direction:column;justify-content:' +
    ({ top: 'flex-start', middle: 'center', bottom: 'flex-end' }[c.valign || 'top']) + ';' + (c.lh ? 'line-height:' + c.lh + ';' : '');
  d.innerHTML = '<div class="in">' + c.html + '</div>';
  f.appendChild(d);
  (c.rot ? g(c.rot, c.x + c.w / 2, c.y + (c.h || 400) / 2) : svg).appendChild(f);
}
function arrowHead(p, q, color, sw, size) {
  const a = Math.atan2(q[1] - p[1], q[0] - p[0]), s = size || 38;
  for (const d of [0.5, -0.5]) add(rc.line(q[0], q[1], q[0] - s * Math.cos(a + d), q[1] - s * Math.sin(a + d), o({ stroke: color, strokeWidth: sw, roughness: 0.8 })));
}
const ICONS = {
  robot(x, y, s, c) {
    add(rc.rectangle(x + 15 * s, y + 30 * s, 70 * s, 55 * s, o({ stroke: c, fill: 'noteGr', fillStyle: 'solid' })));
    add(rc.circle(x + 35 * s, y + 55 * s, 14 * s, o({ stroke: c, fill: c, fillStyle: 'solid', strokeWidth: 3 })));
    add(rc.circle(x + 65 * s, y + 55 * s, 14 * s, o({ stroke: c, fill: c, fillStyle: 'solid', strokeWidth: 3 })));
    add(rc.line(x + 38 * s, y + 73 * s, x + 62 * s, y + 73 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 50 * s, y + 30 * s, x + 50 * s, y + 12 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.circle(x + 50 * s, y + 9 * s, 10 * s, o({ stroke: c, fill: 'orange', fillStyle: 'solid', strokeWidth: 3 })));
    add(rc.line(x + 8 * s, y + 50 * s, x + 15 * s, y + 50 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 85 * s, y + 50 * s, x + 92 * s, y + 50 * s, o({ stroke: c, strokeWidth: 4 })));
  },
  table(x, y, s, c) {
    add(rc.rectangle(x + 8 * s, y + 15 * s, 84 * s, 70 * s, o({ stroke: c, fill: 'noteB', fillStyle: 'solid' })));
    add(rc.rectangle(x + 8 * s, y + 15 * s, 84 * s, 17 * s, o({ stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 3 })));
    for (const yy of [49, 67]) add(rc.line(x + 8 * s, y + yy * s, x + 92 * s, y + yy * s, o({ stroke: c, strokeWidth: 3 })));
    for (const xx of [36, 64]) add(rc.line(x + xx * s, y + 15 * s, x + xx * s, y + 85 * s, o({ stroke: c, strokeWidth: 3 })));
  },
  chart(x, y, s, c) {
    add(rc.line(x + 10 * s, y + 88 * s, x + 92 * s, y + 88 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 10 * s, y + 88 * s, x + 10 * s, y + 10 * s, o({ stroke: c, strokeWidth: 4 })));
    [[22, 55], [44, 35], [66, 62]].forEach(([xx, h], i) => add(rc.rectangle(x + xx * s, y + (88 - h) * s, 16 * s, h * s,
      o({ stroke: c, fill: ['blue', 'orange', 'green'][i], fillStyle: 'hachure', hachureGap: 7, strokeWidth: 3 }))));
  },
  gauge(x, y, s, c) {
    add(rc.arc(x + 50 * s, y + 70 * s, 84 * s, 84 * s, Math.PI, Math.PI * 1.45, false, o({ stroke: 'orange', strokeWidth: 9 })));
    add(rc.arc(x + 50 * s, y + 70 * s, 84 * s, 84 * s, Math.PI * 1.45, Math.PI * 1.7, false, o({ stroke: 'yellow', strokeWidth: 9 })));
    add(rc.arc(x + 50 * s, y + 70 * s, 84 * s, 84 * s, Math.PI * 1.7, Math.PI * 2, false, o({ stroke: 'green', strokeWidth: 9 })));
    add(rc.line(x + 50 * s, y + 70 * s, x + 80 * s, y + 42 * s, o({ stroke: c, strokeWidth: 5 })));
    add(rc.circle(x + 50 * s, y + 70 * s, 12 * s, o({ stroke: c, fill: c, fillStyle: 'solid' })));
  },
  notebook(x, y, s, c) {
    add(rc.rectangle(x + 12 * s, y + 8 * s, 62 * s, 84 * s, o({ stroke: c, fill: 'noteG', fillStyle: 'solid' })));
    for (const yy of [28, 42, 56, 70]) add(rc.line(x + 22 * s, y + yy * s, x + 64 * s, y + yy * s, o({ stroke: c, strokeWidth: 3 })));
    add(rc.line(x + 60 * s, y + 88 * s, x + 94 * s, y + 30 * s, o({ stroke: 'orange', strokeWidth: 9 })));
    add(rc.line(x + 60 * s, y + 88 * s, x + 66 * s, y + 77 * s, o({ stroke: c, strokeWidth: 5 })));
  },
  shopper(x, y, s, c) {
    add(rc.circle(x + 50 * s, y + 16 * s, 24 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 50 * s, y + 28 * s, x + 50 * s, y + 62 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 50 * s, y + 38 * s, x + 30 * s, y + 52 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 50 * s, y + 38 * s, x + 72 * s, y + 50 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 50 * s, y + 62 * s, x + 36 * s, y + 92 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 50 * s, y + 62 * s, x + 66 * s, y + 92 * s, o({ stroke: c, strokeWidth: 4 })));
  },
  truck(x, y, s, c) {
    add(rc.rectangle(x + 4 * s, y + 25 * s, 58 * s, 45 * s, o({ stroke: c, fill: 'noteY', fillStyle: 'solid' })));
    add(rc.polygon([[x + 62 * s, y + 40 * s], [x + 84 * s, y + 40 * s], [x + 96 * s, y + 55 * s], [x + 96 * s, y + 70 * s], [x + 62 * s, y + 70 * s]], o({ stroke: c, fill: 'noteGr', fillStyle: 'solid' })));
    add(rc.circle(x + 22 * s, y + 76 * s, 18 * s, o({ stroke: c, fill: c, fillStyle: 'solid' })));
    add(rc.circle(x + 80 * s, y + 76 * s, 18 * s, o({ stroke: c, fill: c, fillStyle: 'solid' })));
  },
  shelf(x, y, s, c, full) {
    add(rc.rectangle(x + 8 * s, y + 10 * s, 84 * s, 80 * s, o({ stroke: c })));
    add(rc.line(x + 8 * s, y + 50 * s, x + 92 * s, y + 50 * s, o({ stroke: c, strokeWidth: 4 })));
    if (full) for (const xx of [16, 40, 64]) add(rc.rectangle(x + xx * s, y + 24 * s, 18 * s, 25 * s, o({ stroke: c, fill: 'noteO', fillStyle: 'solid', strokeWidth: 3 })));
  },
  bag(x, y, s, c) {
    add(rc.polygon([[x + 22 * s, y + 18 * s], [x + 78 * s, y + 18 * s], [x + 84 * s, y + 92 * s], [x + 16 * s, y + 92 * s]], o({ stroke: c, fill: 'noteO', fillStyle: 'solid' })));
    add(rc.line(x + 22 * s, y + 18 * s, x + 30 * s, y + 6 * s, o({ stroke: c, strokeWidth: 4 })));
    add(rc.line(x + 78 * s, y + 18 * s, x + 70 * s, y + 6 * s, o({ stroke: c, strokeWidth: 4 })));
  },
  exam(x, y, s, c) {
    add(rc.rectangle(x + 14 * s, y + 6 * s, 72 * s, 88 * s, o({ stroke: c, fill: 'paper', fillStyle: 'solid' })));
    for (const [yy, ok] of [[24, 1], [44, 0], [64, 1]]) {
      add(rc.rectangle(x + 22 * s, y + (yy - 6) * s, 12 * s, 12 * s, o({ stroke: c, strokeWidth: 3 })));
      add(rc.line(x + 42 * s, y + yy * s, x + 76 * s, y + yy * s, o({ stroke: c, strokeWidth: 3 })));
      if (ok) add(rc.linearPath([[x + 23 * s, y + yy * s], [x + 28 * s, y + (yy + 5) * s], [x + 36 * s, y + (yy - 9) * s]], o({ stroke: 'green', strokeWidth: 5 })));
      else { add(rc.line(x + 22 * s, y + (yy - 6) * s, x + 34 * s, y + (yy + 6) * s, o({ stroke: 'orange', strokeWidth: 5 }))); add(rc.line(x + 34 * s, y + (yy - 6) * s, x + 22 * s, y + (yy + 6) * s, o({ stroke: 'orange', strokeWidth: 5 }))); }
    }
  },
  case(x, y, s, c) {
    add(rc.rectangle(x + 10 * s, y + 28 * s, 80 * s, 58 * s, o({ stroke: c, fill: 'noteO', fillStyle: 'solid' })));
    add(rc.line(x + 10 * s, y + 28 * s, x + 90 * s, y + 86 * s, o({ stroke: c, strokeWidth: 3 })));
    add(rc.line(x + 90 * s, y + 28 * s, x + 10 * s, y + 86 * s, o({ stroke: c, strokeWidth: 3 })));
    add(rc.rectangle(x + 30 * s, y + 12 * s, 40 * s, 16 * s, o({ stroke: c, fill: 'noteO', fillStyle: 'solid', strokeWidth: 3 })));
  },
  eye(x, y, s, c) {
    add(rc.path('M ' + (x + 4 * s) + ' ' + (y + 50 * s) + ' Q ' + (x + 50 * s) + ' ' + (y + 4 * s) + ' ' + (x + 96 * s) + ' ' + (y + 50 * s) +
      ' Q ' + (x + 50 * s) + ' ' + (y + 96 * s) + ' ' + (x + 4 * s) + ' ' + (y + 50 * s) + ' Z', o({ stroke: c, fill: 'paper', fillStyle: 'solid' })));
    add(rc.circle(x + 50 * s, y + 50 * s, 30 * s, o({ stroke: c, fill: 'blue', fillStyle: 'solid', strokeWidth: 3 })));
    add(rc.circle(x + 50 * s, y + 50 * s, 11 * s, o({ stroke: c, fill: c, fillStyle: 'solid', strokeWidth: 2 })));
  },
  shop(x, y, s, c) {
    add(rc.rectangle(x + 10 * s, y + 38 * s, 80 * s, 56 * s, o({ stroke: c, fill: 'noteY', fillStyle: 'solid' })));
    const zz = [[x + 4 * s, y + 38 * s]]; for (let i = 0; i <= 8; i++) zz.push([x + (4 + i * 11.5) * s, y + (i % 2 ? 26 : 38) * s]);
    add(rc.linearPath([[x + 4 * s, y + 38 * s], [x + 14 * s, y + 14 * s], [x + 86 * s, y + 14 * s], [x + 96 * s, y + 38 * s]], o({ stroke: c })));
    add(rc.linearPath(zz, o({ stroke: 'orange', strokeWidth: 4 })));
    add(rc.rectangle(x + 40 * s, y + 62 * s, 20 * s, 32 * s, o({ stroke: c, strokeWidth: 3 })));
  },
};
const DRAW = {
  board(c) {
    add(rc.rectangle(14, 14, c.w - 28, c.h - 28, { roughness: 0.4, strokeWidth: 22, stroke: '#c5c9c4', fill: C.paper, fillStyle: 'solid', seed: 1 }));
  },
  text,
  rect(c) {
    const n = rc.rectangle(c.x, c.y, c.w, c.h, o({ stroke: c.stroke || 'ink', fill: c.fill, fillStyle: c.fillStyle || 'solid', strokeWidth: c.sw || 5,
      roughness: c.rough ?? 1.3, hachureGap: c.gap || 14, strokeLineDash: c.dashed ? [22, 16] : undefined }));
    (c.rot ? g(c.rot, c.x + c.w / 2, c.y + c.h / 2) : svg).appendChild(n);
  },
  hl(c) { const n = rc.rectangle(c.x, c.y, c.w, c.h, { stroke: 'none', fill: 'rgba(255,225,77,0.7)', fillStyle: 'solid', roughness: 1.6, seed: seed++ }); svg.appendChild(n); },
  circle(c) { add(rc.circle(c.cx, c.cy, c.d, o({ stroke: c.stroke || 'ink', fill: c.fill, fillStyle: c.fillStyle || 'solid', strokeWidth: c.sw || 5 }))); },
  num(c) {
    add(rc.circle(c.cx, c.cy, c.d || 104, o({ stroke: c.color || 'ink', fill: c.color || 'ink', fillStyle: 'solid', strokeWidth: 4 })));
    text({ x: c.cx - 60, y: c.cy - 62, w: 120, h: 120, size: c.size || 70, weight: 700, color: '#ffffff', align: 'center', valign: 'middle', html: String(c.n), check: false });
  },
  line(c) { add((c.curve ? rc.curve : rc.linearPath).call(rc, c.pts, o({ stroke: c.color || 'ink', strokeWidth: c.sw || 5, strokeLineDash: c.dashed ? [24, 18] : undefined, roughness: c.rough ?? 1 }))); },
  arrow(c) {
    const pts = c.pts, color = c.color || 'ink', sw = c.sw || 6;
    add((pts.length > 2 && c.curve !== false ? rc.curve : rc.linearPath).call(rc, pts, o({ stroke: color, strokeWidth: sw, roughness: c.rough ?? 0.9, strokeLineDash: c.dashed ? [26, 18] : undefined })));
    arrowHead(pts[pts.length - 2], pts[pts.length - 1], color, sw, c.head);
    if (c.both) arrowHead(pts[1], pts[0], color, sw, c.head);
  },
  tick(c) { add(rc.linearPath([[c.x, c.y + 0.5 * c.s], [c.x + 0.35 * c.s, c.y + 0.85 * c.s], [c.x + c.s, c.y]], o({ stroke: c.color || 'green', strokeWidth: c.sw || 9 }))); },
  cross(c) { for (const [a, b] of [[[c.x, c.y], [c.x + c.s, c.y + c.s]], [[c.x + c.s, c.y], [c.x, c.y + c.s]]]) add(rc.line(a[0], a[1], b[0], b[1], o({ stroke: c.color || 'orange', strokeWidth: c.sw || 9 }))); },
  icon(c) { ICONS[c.name](c.x, c.y, c.s || 1, col(c.color || 'ink'), c.full); },
  tally(c) {
    for (let i = 0; i < c.n; i++) {
      const five = i % 5 === 4, base = c.x + Math.floor(i / 5) * (c.gap * 5 + 30) + (i % 5) * c.gap;
      if (five) add(rc.line(base - c.gap * 4 - 10, c.y + c.h * 0.75, base + 6, c.y + c.h * 0.2, o({ stroke: c.color || 'green', strokeWidth: 7 })));
      else add(rc.line(base, c.y, base, c.y + c.h, o({ stroke: c.color || 'green', strokeWidth: 7 })));
    }
  },
  bar(c) {
    add(rc.rectangle(c.x, c.y, c.w, c.h, o({ stroke: 'ink', strokeWidth: 4, roughness: 0.8 })));
    if (c.frac > 0) add(rc.rectangle(c.x, c.y, c.w * c.frac, c.h, o({ stroke: c.color, fill: c.color, fillStyle: 'hachure', hachureGap: 11, fillWeight: 4, strokeWidth: 4 })));
  },
};
for (const c of window.COMMANDS) DRAW[c.t](c);
`;

const W = 2000;
const H = 2500;
const page = (board) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
<svg id="board" xmlns="http://www.w3.org/2000/svg" width="${board.w ?? W}" height="${board.h ?? H}" viewBox="0 0 ${board.w ?? W} ${board.h ?? H}"></svg>
<script>${ROUGH}</script><script>window.COMMANDS = ${JSON.stringify(board.commands)};</script><script>${RUNTIME}</script></body></html>`;

const wanted = process.argv.slice(2);
const boards = wanted.length ? BOARDS.filter((b) => wanted.includes(b.slug)) : BOARDS;
if (wanted.length && wanted.some((w) => !BOARDS.some((b) => b.slug === w))) throw new Error(`no board for: ${wanted.filter((w) => !BOARDS.some((b) => b.slug === w)).join(', ')}`);
const executablePath = process.env.CHROME ?? (existsSync('/usr/bin/google-chrome') ? '/usr/bin/google-chrome' : undefined);
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath });
}
for (const b of boards) {
  const tab = await browser.newPage({ viewport: { width: b.w ?? W, height: b.h ?? H }, deviceScaleFactor: 1 });
  const errors = [];
  tab.on('pageerror', (e) => errors.push(e.message));
  await tab.setContent(page(b), { waitUntil: 'load' });
  await tab.evaluate(() => document.fonts.ready);
  if (errors.length) throw new Error(`${b.slug}: ${errors.join('; ')}`);
  const problems = await tab.evaluate(() => {
    const out = [];
    const box = document.getElementById('board').getBoundingClientRect();
    const texts = [...document.querySelectorAll('.t')];
    for (const t of texts) {
      const inner = t.firstElementChild;
      if (t.dataset.check && (inner.scrollHeight > t.clientHeight + 2 || inner.scrollWidth > t.clientWidth + 2)) out.push(`text spills out of its box (${inner.scrollHeight}x${inner.scrollWidth} in ${t.clientHeight}x${t.clientWidth}): ${t.textContent.slice(0, 50)}`);
      const r = inner.getBoundingClientRect();
      if (r.left < box.left + 30 || r.right > box.right - 30 || r.top < box.top + 30 || r.bottom > box.bottom - 30) out.push(`text off the board: ${t.textContent.slice(0, 50)}`);
    }
    // Words must not sit on top of each other.
    const rects = texts.filter((t) => t.dataset.check).map((t) => [t.textContent.slice(0, 30), (() => {
      const range = document.createRange(); range.selectNodeContents(t.firstElementChild); return range.getBoundingClientRect();
    })()]);
    for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
      const [a, ra] = rects[i], [bb, rb] = rects[j];
      // A font's line box runs a little above and below its letters, so lines stacked close may touch by a few pixels.
      if (ra.left < rb.right - 4 && rb.left < ra.right - 4 && ra.top < rb.bottom - 14 && rb.top < ra.bottom - 14) out.push(`"${a}" overlaps "${bb}"`);
    }
    return out;
  });
  if (problems.length && !process.env.WB_LOOSE) throw new Error(`${b.slug}: ${problems.join('; ')}`);
  if (problems.length) console.warn(`${b.slug}: ${problems.join('\n  ')}`);
  const dir = path.join(root, 'public', 'images', b.slug);
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${b.name ?? 'board'}.png`);
  await tab.screenshot({ path: file, clip: { x: 0, y: 0, width: b.w ?? W, height: b.h ?? H } });
  console.log('wrote', path.relative(root, file));
  await tab.close();
}
await browser.close();
