// SVG charts for the summary cards. Each takes a spec and the plot's width and height in card pixels
// (cards are 2400x1350 and shown about 390 px wide on a phone, so text stays at 40 px or more).
// Colours: blue is what a system records, orange is what really happened, yellow marks the gap.
export const C = {
  ink: '#1b2430',
  muted: '#59626d',
  rule: '#d5d9d4',
  rec: '#2f55a4',
  real: '#d4621c',
  band: '#ffe14d',
  grey: '#a9afa8',
  ok: '#17795a',
};
const FONT = 'Anek';
const esc = (s = '') => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const t = (x, y, s, { size = 42, anchor = 'start', weight = 400, fill = C.muted } = {}) =>
  `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}" fill="${fill}">${esc(s)}</text>`;
const niceMax = (v, step) => Math.max(step, Math.ceil(v / step) * step);
const svg = (w, h, body) => `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" font-family="${FONT}">${body}</svg>`;

/** Paired daily bars (a = what happened, b = what the record shows), with a shaded band for the gap. */
export function pair(s, w, h) {
  const left = 120, right = 20, top = 170, bottom = h - 80;
  const step = s.step ?? 10;
  const max = niceMax(Math.max(...s.days.flatMap((d) => [d.a, d.b])), step);
  const slot = (w - left - right) / s.days.length;
  const bw = slot * 0.36;
  const y = (v) => bottom - (v / max) * (bottom - top);
  const x = (i) => left + i * slot;
  let body = '';
  for (const b of s.bands ?? []) {
    const x0 = x(b.from.i) + b.from.frac * slot, x1 = x(b.to.i) + b.to.frac * slot;
    body += `<rect x="${x0}" y="0" width="${x1 - x0}" height="${bottom}" fill="${C.band}" opacity="0.55" rx="10"/>`;
    body += t((x0 + x1) / 2, 66, b.label, { size: 54, anchor: 'middle', weight: 700, fill: C.ink });
    if (b.sub) body += t((x0 + x1) / 2, 124, b.sub, { size: 46, anchor: 'middle', fill: C.ink });
  }
  for (let v = 0; v <= max; v += step) {
    body += `<line x1="${left}" x2="${w - right}" y1="${y(v)}" y2="${y(v)}" stroke="${C.rule}" stroke-width="2"/>`;
    body += t(left - 24, y(v) + 14, v, { size: 46, anchor: 'end' });
  }
  s.days.forEach((d, i) => {
    body += `<rect x="${x(i) + slot / 2 - bw - 4}" y="${y(d.a)}" width="${bw}" height="${bottom - y(d.a)}" fill="${C.real}" rx="6"/>`;
    body += `<rect x="${x(i) + slot / 2 + 4}" y="${y(d.b)}" width="${bw}" height="${Math.max(bottom - y(d.b), 0)}" fill="${C.rec}" rx="6"/>`;
    if (d.label) body += t(x(i) + slot / 2, bottom + 60, d.label, { size: 44, anchor: 'middle' });
  });
  body += `<line x1="${left}" x2="${w - right}" y1="${bottom}" y2="${bottom}" stroke="${C.muted}" stroke-width="3"/>`;
  return svg(w, h, body);
}

/** Lines over an index (hours or days), with shaded bands, a few dated ticks and optional end labels. */
export function lines(s, w, h) {
  const left = 120, right = s.endLabels ? 330 : 30, top = s.bands?.length ? 170 : 40, bottom = h - 80;
  const n = s.length;
  const step = s.step ?? 10;
  const max = s.max ?? niceMax(Math.max(...s.series.flatMap((x) => x.values.filter((v) => v != null))), step);
  const x = (i) => left + (i / (n - 1)) * (w - left - right);
  const y = (v) => bottom - (v / max) * (bottom - top);
  let body = '';
  for (const b of s.bands ?? []) {
    body += `<rect x="${x(b.from)}" y="0" width="${x(b.to) - x(b.from)}" height="${bottom}" fill="${C.band}" opacity="0.55" rx="10"/>`;
    body += t((x(b.from) + x(b.to)) / 2, 66, b.label, { size: 50, anchor: 'middle', weight: 700, fill: C.ink });
    if (b.sub) body += t((x(b.from) + x(b.to)) / 2, 120, b.sub, { size: 42, anchor: 'middle', fill: C.ink });
  }
  for (let k = 0; k * step <= max + 1e-9; k++) {
    const v = +(k * step).toFixed(6);
    body += `<line x1="${left}" x2="${w - right}" y1="${y(v)}" y2="${y(v)}" stroke="${C.rule}" stroke-width="2"/>`;
    body += t(left - 24, y(v) + 14, v, { size: 44, anchor: 'end' });
  }
  for (const r of s.refs ?? []) {
    body += `<line x1="${left}" x2="${w - right}" y1="${y(r.value)}" y2="${y(r.value)}" stroke="${C.ink}" stroke-width="3" stroke-dasharray="14 10"/>`;
    body += t(w - right - 8, y(r.value) - 16, r.label, { size: 42, anchor: 'end', fill: C.ink });
  }
  for (const tk of s.ticks ?? []) body += t(x(tk.i), bottom + 60, tk.label, { size: 44, anchor: tk.anchor ?? 'middle' });
  for (const ser of s.series) {
    const pts = ser.values.map((v, i) => (v == null ? null : `${x(i).toFixed(1)},${y(v).toFixed(1)}`));
    let d = '', pen = false;
    for (const p of pts) { if (p == null) { pen = false; continue; } d += `${pen ? 'L' : 'M'}${p} `; pen = true; }
    body += `<path d="${d}" fill="none" stroke="${ser.color}" stroke-width="${ser.width ?? 7}" stroke-linejoin="round" stroke-linecap="round" ${ser.dash ? `stroke-dasharray="${ser.dash}"` : ''}/>`;
    if (s.endLabels) {
      const last = ser.values.length - 1 - [...ser.values].reverse().findIndex((v) => v != null);
      body += t(x(last) + 24, y(ser.values[last]) + 16 + (ser.labelDy ?? 0), ser.name, { size: 44, weight: 700, fill: ser.color });
    }
  }
  body += `<line x1="${left}" x2="${w - right}" y1="${bottom}" y2="${bottom}" stroke="${C.muted}" stroke-width="3"/>`;
  return svg(w, h, body);
}

/** One series of bars per day, with optional highlighted bars and value labels on the tallest. */
export function bars(s, w, h) {
  const left = 120, right = 20, top = 60, bottom = h - 80;
  const step = s.step ?? 10;
  const max = niceMax(Math.max(...s.values.map((v) => v.v)), step);
  const slot = (w - left - right) / s.values.length;
  const bw = slot * 0.7;
  const y = (v) => bottom - (v / max) * (bottom - top);
  let body = '';
  for (let k = 0; k * step <= max + 1e-9; k++) {
    const v = +(k * step).toFixed(6);
    body += `<line x1="${left}" x2="${w - right}" y1="${y(v)}" y2="${y(v)}" stroke="${C.rule}" stroke-width="2"/>`;
    body += t(left - 24, y(v) + 14, v, { size: 44, anchor: 'end' });
  }
  for (const r of s.refs ?? []) {
    body += `<line x1="${left}" x2="${w - right}" y1="${y(r.value)}" y2="${y(r.value)}" stroke="${C.ink}" stroke-width="3" stroke-dasharray="14 10"/>`;
    body += t(w - right - 8, y(r.value) - 16, r.label, { size: 42, anchor: 'end', fill: C.ink });
  }
  s.values.forEach((d, i) => {
    const x0 = left + i * slot + (slot - bw) / 2;
    if (d.v > 0) body += `<rect x="${x0}" y="${y(d.v)}" width="${bw}" height="${bottom - y(d.v)}" fill="${d.hot ? C.real : C.grey}" rx="5"/>`;
    if (d.label) body += t(x0 + bw / 2, d.v > 0 ? y(d.v) - 18 : bottom - 18, d.label, { size: 42, anchor: 'middle', weight: 700, fill: C.ink });
  });
  for (const tk of s.ticks ?? []) body += t(left + tk.i * slot + slot / 2, bottom + 60, tk.label, { size: 44, anchor: tk.anchor ?? 'middle' });
  body += `<line x1="${left}" x2="${w - right}" y1="${bottom}" y2="${bottom}" stroke="${C.muted}" stroke-width="3"/>`;
  return svg(w, h, body);
}

/** Horizontal bars, one per label, coloured by kind ('rec', 'real', 'grey'), with the value printed. */
export function hbars(s, w, h) {
  const labelW = s.labelW ?? 820, right = 260, gap = 28;
  const n = s.rows.length;
  const bh = Math.min(n <= 2 ? 150 : 118, (h - gap * (n - 1)) / n);
  const max = s.max ?? Math.max(...s.rows.map((r) => r.max ?? r.v));
  const min = s.min ?? 0;
  let body = '';
  s.rows.forEach((r, i) => {
    // A row may carry its own scale, for rows in different units.
    const x = (v) => labelW + ((v - min) / ((r.max ?? max) - min)) * (w - labelW - right);
    const y0 = i * (bh + gap) + (h - (n * bh + (n - 1) * gap)) / 2;
    body += t(labelW - 32, y0 + bh / 2 + 15, r.label, { size: 48, anchor: 'end', fill: C.ink, weight: r.bold ? 700 : 400 });
    body += `<rect x="${labelW}" y="${y0}" width="${Math.max(x(r.v) - labelW, 4)}" height="${bh}" fill="${C[r.kind ?? 'grey']}" rx="10"/>`;
    body += t(x(r.v) + 24, y0 + bh / 2 + 17, r.text ?? r.v, { size: 54, weight: 700, fill: C.ink });
  });
  return svg(w, h, body);
}

/** Bars either side of zero, one per label: count corrections, adjustments. */
export function diverging(s, w, h) {
  const labelW = s.labelW ?? 640, pad = 230, gap = 16;
  const n = s.rows.length;
  const bh = Math.min(96, (h - gap * (n - 1)) / n);
  const m = Math.max(...s.rows.map((r) => Math.abs(r.v)));
  const zero = labelW + pad + (w - labelW - 2 * pad) / 2;
  const half = (w - labelW - 2 * pad) / 2;
  const x = (v) => zero + (v / m) * half;
  let body = `<line x1="${zero}" x2="${zero}" y1="0" y2="${h}" stroke="${C.muted}" stroke-width="3"/>`;
  s.rows.forEach((r, i) => {
    const y0 = i * (bh + gap) + (h - (n * bh + (n - 1) * gap)) / 2;
    const color = r.v === 0 ? C.rule : r.hot ? C.real : C.grey;
    body += t(labelW - 24, y0 + bh / 2 + 15, r.label, { size: 44, anchor: 'end', fill: C.ink, weight: r.hot ? 700 : 400 });
    if (r.v !== 0) body += `<rect x="${Math.min(zero, x(r.v))}" y="${y0}" width="${Math.abs(x(r.v) - zero)}" height="${bh}" fill="${color}" rx="8"/>`;
    const tx = r.v < 0 ? x(r.v) - 20 : r.v > 0 ? x(r.v) + 20 : zero + 20;
    body += t(tx, y0 + bh / 2 + 16, r.text ?? (r.v > 0 ? `+${r.v}` : r.v === 0 ? '0' : `−${Math.abs(r.v)}`), { size: 48, weight: 700, anchor: r.v < 0 ? 'end' : 'start', fill: C.ink });
  });
  return svg(w, h, body);
}

/** Steps that add up to a net: each correction as a floating bar, then the net. */
export function waterfall(s, w, h) {
  const left = 40, right = 40, top = 90, bottom = h - 150;
  const n = s.steps.length + 1;
  const slot = (w - left - right) / n;
  const bw = slot * 0.62;
  let run = 0;
  const levels = s.steps.map((st) => { const from = run; run += st.v; return { ...st, from, to: run }; });
  const all = levels.flatMap((l) => [l.from, l.to]).concat([0]);
  const hi = Math.max(...all), lo = Math.min(...all);
  const y = (v) => top + ((hi - v) / (hi - lo)) * (bottom - top);
  let body = `<line x1="${left}" x2="${w - right}" y1="${y(0)}" y2="${y(0)}" stroke="${C.muted}" stroke-width="3"/>`;
  levels.forEach((l, i) => {
    const x0 = left + i * slot + (slot - bw) / 2;
    const yTop = y(Math.max(l.from, l.to)), yBot = y(Math.min(l.from, l.to));
    body += `<rect x="${x0}" y="${yTop}" width="${bw}" height="${Math.max(yBot - yTop, 4)}" fill="${l.v < 0 ? C.grey : '#6f7a86'}" rx="8"/>`;
    body += t(x0 + bw / 2, yTop - 20, l.text, { size: 46, weight: 700, anchor: 'middle', fill: C.ink });
    l.label.forEach((line, k) => { body += t(x0 + bw / 2, h - 96 + k * 50, line, { size: 42, anchor: 'middle' }); });
    if (i < levels.length - 1) body += `<line x1="${x0 + bw}" x2="${x0 + slot}" y1="${y(l.to)}" y2="${y(l.to)}" stroke="${C.muted}" stroke-width="2" stroke-dasharray="8 8"/>`;
  });
  const xn = left + levels.length * slot + (slot - bw) / 2;
  body += `<rect x="${xn}" y="${y(Math.max(run, 0)) - 3}" width="${bw}" height="6" fill="${C.ink}"/>`;
  body += t(xn + bw / 2, y(Math.max(run, 0)) - 26, s.netText, { size: 54, weight: 700, anchor: 'middle', fill: C.ink });
  s.netLabel.forEach((line, k) => { body += t(xn + bw / 2, h - 96 + k * 50, line, { size: 42, anchor: 'middle', weight: 700, fill: C.ink }); });
  return svg(w, h, body);
}

/** Dots on a time-of-day axis, one per day, with a shaded slot band and one highlighted dot. */
export function dots(s, w, h) {
  const left = 200, right = 40, top = 20, bottom = h - 80;
  const x = (i) => left + (i / (s.days - 1)) * (w - left - right);
  const y = (m) => bottom - ((m - s.min) / (s.max - s.min)) * (bottom - top);
  let body = `<rect x="${left}" y="${y(s.band.to)}" width="${w - left - right}" height="${y(s.band.from) - y(s.band.to)}" fill="${C.band}" opacity="0.55" rx="10"/>`;
  body += t(w - right - 20, y(s.band.to) - 20, s.band.label, { size: 46, weight: 700, anchor: 'end', fill: C.ink });
  for (const m of s.yTicks) {
    body += `<line x1="${left}" x2="${w - right}" y1="${y(m.v)}" y2="${y(m.v)}" stroke="${C.rule}" stroke-width="2"/>`;
    body += t(left - 24, y(m.v) + 14, m.label, { size: 44, anchor: 'end' });
  }
  for (const tk of s.ticks) body += t(x(tk.i), bottom + 60, tk.label, { size: 44, anchor: tk.anchor ?? 'middle' });
  for (const p of s.points) {
    body += `<circle cx="${x(p.i)}" cy="${y(p.m)}" r="${p.hot ? 26 : 18}" fill="${p.hot ? C.real : C.rec}" stroke="#f5f6f4" stroke-width="4"/>`;
    if (p.label) {
      const ly = y(p.m) + (p.labelDy ?? -46);
      if (p.labelDy && p.labelDy < -60) body += `<line x1="${x(p.i)}" x2="${x(p.i)}" y1="${y(p.m) - 28}" y2="${ly + 14}" stroke="${C.real}" stroke-width="4"/>`;
      body += t(x(p.i), ly, p.label, { size: 46, weight: 700, anchor: 'middle', fill: p.hot ? C.real : C.ink });
    }
  }
  return svg(w, h, body);
}

/** Events on a time line, labels alternating above and below. */
export function events(s, w, h) {
  const left = 120, right = 120, mid = h / 2;
  const x = (v) => left + ((v - s.from) / (s.to - s.from)) * (w - left - right);
  let body = `<line x1="${left - 40}" x2="${w - right + 40}" y1="${mid}" y2="${mid}" stroke="${C.muted}" stroke-width="4"/>`;
  for (const tk of s.ticks) {
    body += `<line x1="${x(tk.v)}" x2="${x(tk.v)}" y1="${mid - 14}" y2="${mid + 14}" stroke="${C.muted}" stroke-width="3"/>`;
    body += t(x(tk.v), mid + 64, tk.label, { size: 40, anchor: 'middle' });
  }
  s.events.forEach((e, i) => {
    const up = e.up ?? i % 2 === 0;
    const ex = x(e.v);
    const y1 = up ? mid - 70 : mid + 110;
    body += `<line x1="${ex}" x2="${ex}" y1="${mid}" y2="${up ? mid - 60 : mid + 100}" stroke="${e.hot ? C.real : C.rec}" stroke-width="4"/>`;
    body += `<circle cx="${ex}" cy="${mid}" r="20" fill="${e.hot ? C.real : C.rec}" stroke="#f5f6f4" stroke-width="4"/>`;
    const anchor = e.anchor ?? 'middle';
    e.lines.forEach((line, k) => {
      const yy = up ? y1 - (e.lines.length - 1 - k) * 54 - 10 : y1 + 40 + k * 54;
      body += t(ex, yy, line, { size: k === 0 ? 46 : 42, weight: k === 0 ? 700 : 400, anchor, fill: k === 0 ? C.ink : C.muted });
    });
  });
  return svg(w, h, body);
}

/** Dots along a days axis in labelled rows, with a dashed yardstick. */
export function strip(s, w, h) {
  const labelW = s.labelW ?? 560, right = 60, top = 40, bottom = h - 90;
  const x = (v) => labelW + (v / s.max) * (w - labelW - right);
  const n = s.rows.length;
  const rowH = (bottom - top) / n;
  let body = '';
  for (let v = 0; v <= s.max; v += s.step ?? 1) {
    body += `<line x1="${x(v)}" x2="${x(v)}" y1="${top}" y2="${bottom}" stroke="${C.rule}" stroke-width="2"/>`;
    body += t(x(v), bottom + 60, v, { size: 44, anchor: 'middle' });
  }
  if (s.yard) {
    body += `<line x1="${x(s.yard.v)}" x2="${x(s.yard.v)}" y1="${top - 20}" y2="${bottom}" stroke="${C.ink}" stroke-width="4" stroke-dasharray="14 10"/>`;
  }
  s.rows.forEach((r, i) => {
    const cy = top + rowH * i + rowH / 2;
    body += t(labelW - 32, cy - 6, r.label, { size: 48, anchor: 'end', weight: 700, fill: C.ink });
    if (r.sub) body += t(labelW - 32, cy + 46, r.sub, { size: 42, anchor: 'end' });
    const seen = new Map();
    for (const v of r.values) {
      const k = Math.round(v * 4) / 4;
      const c = seen.get(k) ?? 0;
      seen.set(k, c + 1);
      body += `<circle cx="${x(v)}" cy="${cy + (c % 2 ? 1 : -1) * Math.ceil(c / 2) * 30}" r="17" fill="${C[r.kind]}" opacity="0.9"/>`;
    }
    if (r.median != null) {
      body += `<line x1="${x(r.median)}" x2="${x(r.median)}" y1="${cy - rowH / 2 + 30}" y2="${cy + rowH / 2 - 30}" stroke="${C.ink}" stroke-width="6"/>`;
    }
  });
  if (s.yard) body += t(x(s.yard.v) + 16, top + 6, s.yard.label, { size: 42, weight: 700, fill: C.ink });
  return svg(w, h, body);
}

export const CHARTS = { pair, lines, bars, hbars, diverging, waterfall, dots, events, strip };
