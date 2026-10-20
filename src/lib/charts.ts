// Small SVG charts for the demo: line/area with crosshair, bars with per-mark hover.
// Marks follow the dataviz spec: 2px lines, ~10% area wash, hairline solid grid,
// bars <= 24px with 4px rounded ends, 2px surface gaps, legend for 2+ series.

const SVG = 'http://www.w3.org/2000/svg';

export interface Series {
  key: string;
  label: string;
  color: string; // CSS colour, usually var(--c-...)
  values: (number | null)[];
  area?: boolean;
}

export interface TooltipRow { label: string; value: string; color?: string }
export interface Tooltip { title: string; rows: TooltipRow[] }

interface Common {
  height?: number;
  ariaLabel: string;
  xTick: (i: number) => string | null;
  yFormat?: (v: number) => string;
  tooltip: (i: number) => Tooltip;
  yMax?: number;
}

export interface LineOpts extends Common {
  series: Series[];
  bands?: { from: number; to: number }[];
  bandLabel?: string; // legend label for the bands; "Shelf empty" unless given
  refs?: { values: (number | null)[]; label: string }[];
  markers?: { at: number; label: string }[];
}

export interface BarOpts extends Common {
  series: Series[]; // 1 or 2 series, grouped
  refs?: { values: (number | null)[]; label: string }[]; // step lines drawn over the bars
}

function el<K extends keyof SVGElementTagNameMap>(name: K, attrs: Record<string, string | number>): SVGElementTagNameMap[K] {
  const node = document.createElementNS(SVG, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
  return node;
}

// Round tick steps (1, 2, 2.5, 5 x 10^n) with at most five intervals.
function yScale(maxV: number, fixed?: number): { yMax: number; step: number } {
  const top = fixed ?? Math.max(1, maxV);
  const raw = top / 5;
  const p = Math.pow(10, Math.floor(Math.log10(raw)));
  let step = 10 * p;
  for (const m of [1, 2, 2.5, 5, 10]) if (m * p >= raw) { step = m * p; break; }
  return { yMax: fixed ?? Math.ceil(top / step - 1e-9) * step, step };
}

function legend(host: HTMLElement, series: Series[], kind: 'line' | 'bar', extra: { label: string; swatch: string }[] = []) {
  if (series.length + extra.length < 2) return;
  const ul = document.createElement('ul');
  ul.className = 'chart-legend';
  for (const s of series) {
    const li = document.createElement('li');
    const key = document.createElement('span');
    key.className = kind === 'line' ? 'key-line' : 'key-rect';
    key.style.background = s.color;
    li.append(key, document.createTextNode(s.label));
    ul.append(li);
  }
  for (const x of extra) {
    const li = document.createElement('li');
    const key = document.createElement('span');
    key.className = x.swatch;
    li.append(key, document.createTextNode(x.label));
    ul.append(li);
  }
  host.append(ul);
}

function tooltipBox(host: HTMLElement) {
  const tip = document.createElement('div');
  tip.className = 'chart-tip';
  tip.setAttribute('role', 'status');
  tip.hidden = true;
  host.append(tip);
  return (t: Tooltip | null, x = 0, y = 0, width = 0) => {
    if (!t) { tip.hidden = true; return; }
    tip.replaceChildren();
    const h = document.createElement('div');
    h.className = 'tip-title';
    h.textContent = t.title;
    tip.append(h);
    for (const r of t.rows) {
      const row = document.createElement('div');
      row.className = 'tip-row';
      const k = document.createElement('span');
      k.className = 'key-line';
      if (r.color) k.style.background = r.color; else k.style.visibility = 'hidden';
      const v = document.createElement('strong');
      v.textContent = r.value;
      const l = document.createElement('span');
      l.textContent = r.label;
      row.append(k, v, l);
      tip.append(row);
    }
    tip.hidden = false;
    const w = tip.offsetWidth;
    const left = Math.min(Math.max(0, x + 12), Math.max(0, width - w));
    tip.style.left = `${x + 12 + w > width ? Math.max(0, x - w - 12) : left}px`;
    tip.style.top = `${y}px`;
  };
}

function frame(host: HTMLElement, o: Common, n: number, maxV: number) {
  host.replaceChildren();
  host.classList.add('chart');
  const width = Math.max(280, host.clientWidth);
  const height = o.height ?? 220;
  const m = { l: 40, r: 12, t: 10, b: 26 };
  const W = width - m.l - m.r;
  const Hh = height - m.t - m.b;
  const { yMax, step } = yScale(maxV, o.yMax);
  const svg = el('svg', { viewBox: `0 0 ${width} ${height}`, width, height, role: 'img', 'aria-label': o.ariaLabel });
  const g = el('g', { transform: `translate(${m.l},${m.t})` });
  svg.append(g);
  const x = (i: number) => (n <= 1 ? W / 2 : (i / (n - 1)) * W);
  const y = (v: number) => Hh - (v / yMax) * Hh;
  const fmt = o.yFormat ?? ((v: number) => String(Math.round(v)));
  for (let v = 0; v <= yMax + 1e-9; v += step) {
    g.append(el('line', { x1: 0, x2: W, y1: y(v), y2: y(v), class: 'grid' }));
    const t = el('text', { x: -8, y: y(v) + 4, 'text-anchor': 'end', class: 'tick' });
    t.textContent = fmt(v);
    g.append(t);
  }
  return { svg, g, width, height, m, W, Hh, x, y, yMax };
}

export function lineChart(host: HTMLElement, o: LineOpts): void {
  const draw = () => {
    const n = o.series[0].values.length;
    const all = [...o.series.flatMap((s) => s.values), ...(o.refs ?? []).flatMap((r) => r.values)];
    const maxV = Math.max(1, ...all.filter((v): v is number => v != null));
    const f = frame(host, o, n, maxV);
    const { g, x, y, W, Hh } = f;
    const step = n > 1 ? W / (n - 1) : W;
    for (const b of o.bands ?? []) {
      g.append(el('rect', { x: x(b.from) - step / 2, y: 0, width: Math.max(2, x(b.to) - x(b.from) + step), height: Hh, class: 'band' }));
    }
    for (let i = 0; i < n; i++) {
      const t = o.xTick(i);
      if (t == null) continue;
      g.append(el('line', { x1: x(i), x2: x(i), y1: Hh, y2: Hh + 4, class: 'axis' }));
      const tx = el('text', { x: x(i), y: Hh + 18, 'text-anchor': 'middle', class: 'tick' });
      tx.textContent = t;
      g.append(tx);
    }
    g.append(el('line', { x1: 0, x2: W, y1: Hh, y2: Hh, class: 'axis' }));
    for (const r of o.refs ?? []) {
      let d = '';
      r.values.forEach((v, i) => {
        if (v == null) return;
        const px = x(i) - (i > 0 ? step / 2 : 0);
        d += `${d ? 'L' : 'M'}${px},${y(v)}H${x(i) + (i < n - 1 ? step / 2 : 0)}`;
      });
      g.append(el('path', { d, class: 'ref' }));
    }
    for (const s of o.series) {
      let d = '';
      let started = false;
      s.values.forEach((v, i) => {
        if (v == null) { started = false; return; }
        d += `${started ? 'L' : 'M'}${x(i)},${y(v)}`;
        started = true;
      });
      if (s.area) {
        const first = s.values.findIndex((v) => v != null);
        const last = s.values.length - 1 - [...s.values].reverse().findIndex((v) => v != null);
        const area = el('path', { d: `${d}L${x(last)},${Hh}L${x(first)},${Hh}Z`, class: 'area' });
        area.style.fill = s.color;
        g.append(area);
      }
      const p = el('path', { d, class: 'line' });
      p.style.stroke = s.color;
      g.append(p);
    }
    for (const mk of o.markers ?? []) {
      g.append(el('line', { x1: x(mk.at), x2: x(mk.at), y1: 0, y2: Hh, class: 'marker' }));
    }
    const cross = el('line', { x1: 0, x2: 0, y1: 0, y2: Hh, class: 'cross' });
    cross.style.visibility = 'hidden';
    g.append(cross);
    const dots = o.series.map((s) => {
      const c = el('circle', { r: 4, class: 'dot' });
      c.style.fill = s.color;
      c.style.visibility = 'hidden';
      g.append(c);
      return c;
    });
    const hit = el('rect', { x: 0, y: 0, width: W, height: Hh, class: 'hit' });
    g.append(hit);
    host.append(f.svg);
    const show = tooltipBox(host);
    let idx = -1;
    const place = (i: number) => {
      idx = Math.max(0, Math.min(n - 1, i));
      cross.setAttribute('x1', String(x(idx)));
      cross.setAttribute('x2', String(x(idx)));
      cross.style.visibility = 'visible';
      o.series.forEach((s, k) => {
        const v = s.values[idx];
        dots[k].style.visibility = v == null ? 'hidden' : 'visible';
        if (v != null) { dots[k].setAttribute('cx', String(x(idx))); dots[k].setAttribute('cy', String(y(v))); }
      });
      show(o.tooltip(idx), x(idx) + f.m.l, f.m.t, f.width);
    };
    const hide = () => {
      cross.style.visibility = 'hidden';
      dots.forEach((d) => (d.style.visibility = 'hidden'));
      show(null);
    };
    hit.addEventListener('pointermove', (ev) => {
      const r = (f.svg as SVGSVGElement).getBoundingClientRect();
      const px = ((ev.clientX - r.left) * f.width) / r.width - f.m.l;
      place(Math.round((px / W) * (n - 1)));
    });
    hit.addEventListener('pointerleave', hide);
    host.tabIndex = 0;
    host.setAttribute('aria-label', `${o.ariaLabel}. Use the left and right arrow keys to read values.`);
    host.onkeydown = (ev) => {
      const jump = ev.shiftKey ? 15 : 1;
      if (ev.key === 'ArrowRight') { place(idx < 0 ? 0 : idx + jump); ev.preventDefault(); }
      if (ev.key === 'ArrowLeft') { place(idx < 0 ? n - 1 : idx - jump); ev.preventDefault(); }
      if (ev.key === 'Escape') hide();
    };
    host.onblur = hide;
    legend(host, o.series, 'line', [
      ...(o.refs ?? []).map((r) => ({ label: r.label, swatch: 'key-ref' })),
      ...((o.bands ?? []).length ? [{ label: o.bandLabel ?? 'Shelf empty', swatch: 'key-band' }] : []),
    ]);
  };
  draw();
  observe(host, draw);
}

export function barChart(host: HTMLElement, o: BarOpts): void {
  const draw = () => {
    const n = o.series[0].values.length;
    const all = [...o.series.flatMap((s) => s.values), ...(o.refs ?? []).flatMap((r) => r.values)];
    const maxV = Math.max(1, ...all.filter((v): v is number => v != null));
    const f = frame(host, o, n, maxV);
    const { g, Hh, W, y } = f;
    const band = W / n;
    const groups = o.series.length;
    const barW = Math.min(24, (band - 4) / groups - 2);
    const xb = (i: number, k: number) => i * band + band / 2 - (groups * barW + (groups - 1) * 2) / 2 + k * (barW + 2);
    for (let i = 0; i < n; i++) {
      const t = o.xTick(i);
      if (t == null) continue;
      const tx = el('text', { x: i * band + band / 2, y: Hh + 18, 'text-anchor': 'middle', class: 'tick' });
      tx.textContent = t;
      g.append(tx);
    }
    g.append(el('line', { x1: 0, x2: W, y1: Hh, y2: Hh, class: 'axis' }));
    const show = tooltipBox(host);
    const hits: SVGRectElement[] = [];
    for (let i = 0; i < n; i++) {
      o.series.forEach((s, k) => {
        const v = s.values[i];
        if (v == null || v <= 0) return;
        const x0 = xb(i, k);
        const top = y(v);
        const r = Math.min(4, barW / 2, Hh - top);
        const d = `M${x0},${Hh}V${top + r}Q${x0},${top} ${x0 + r},${top}H${x0 + barW - r}Q${x0 + barW},${top} ${x0 + barW},${top + r}V${Hh}Z`;
        const p = el('path', { d, class: 'bar' });
        p.style.fill = s.color;
        g.append(p);
      });
      const hit = el('rect', { x: i * band, y: 0, width: band, height: Hh, class: 'hit' });
      hit.setAttribute('data-i', String(i));
      hit.addEventListener('pointerenter', () => { hit.classList.add('on'); show(o.tooltip(i), i * band + band / 2 + f.m.l, f.m.t, f.width); });
      hit.addEventListener('pointerleave', () => { hit.classList.remove('on'); show(null); });
      g.append(hit);
      hits.push(hit);
    }
    for (const r of o.refs ?? []) {
      let d = '';
      r.values.forEach((v, i) => {
        if (v == null) return;
        d += `${d ? 'L' : 'M'}${i * band},${y(v)}H${(i + 1) * band}`;
      });
      const path = el('path', { d, class: 'ref' });
      g.insertBefore(path, hits[0] ?? null);
    }
    host.append(f.svg);
    let idx = -1;
    host.tabIndex = 0;
    host.setAttribute('aria-label', `${o.ariaLabel}. Use the left and right arrow keys to read values.`);
    host.onkeydown = (ev) => {
      if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
      ev.preventDefault();
      hits[idx]?.classList.remove('on');
      idx = ev.key === 'ArrowRight' ? Math.min(n - 1, idx + 1) : Math.max(0, idx < 0 ? n - 1 : idx - 1);
      hits[idx].classList.add('on');
      show(o.tooltip(idx), idx * band + band / 2 + f.m.l, f.m.t, f.width);
    };
    host.onblur = () => { hits[idx]?.classList.remove('on'); show(null); };
    legend(host, o.series, 'bar', (o.refs ?? []).map((r) => ({ label: r.label, swatch: 'key-ref' })));
  };
  draw();
  observe(host, draw);
}

const observed = new WeakMap<HTMLElement, ResizeObserver>();
function observe(host: HTMLElement, draw: () => void) {
  observed.get(host)?.disconnect();
  let last = host.clientWidth;
  const ro = new ResizeObserver(() => {
    if (Math.abs(host.clientWidth - last) < 8) return;
    last = host.clientWidth;
    draw();
  });
  ro.observe(host);
  observed.set(host, ro);
}

/** A plain table twin for a chart, for screen readers and anyone who prefers numbers. */
export function tableView(host: HTMLElement, caption: string, head: string[], rows: (string | number)[][]): void {
  host.replaceChildren();
  const details = document.createElement('details');
  details.className = 'table-view';
  const summary = document.createElement('summary');
  summary.textContent = 'Show the numbers';
  const wrap = document.createElement('div');
  wrap.className = 'table-wrap';
  const table = document.createElement('table');
  const cap = document.createElement('caption');
  cap.textContent = caption;
  table.append(cap);
  const thead = document.createElement('thead');
  const tr = document.createElement('tr');
  for (const h of head) { const th = document.createElement('th'); th.scope = 'col'; th.textContent = h; tr.append(th); }
  thead.append(tr);
  const tbody = document.createElement('tbody');
  for (const r of rows) {
    const row = document.createElement('tr');
    r.forEach((c, i) => {
      const cell = document.createElement(i === 0 ? 'th' : 'td');
      if (i === 0) (cell as HTMLTableCellElement).scope = 'row';
      cell.textContent = String(c);
      row.append(cell);
    });
    tbody.append(row);
  }
  table.append(thead, tbody);
  wrap.append(table);
  details.append(summary, wrap);
  host.append(details);
}
