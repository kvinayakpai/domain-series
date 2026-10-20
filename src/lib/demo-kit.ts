// Shared pieces for the demos: formatting in Indian conventions, and the small DOM
// building blocks every persona view is made of.

export const day = (iso: string) =>
  new Date(`${iso.slice(0, 10)}T12:00:00+05:30`).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'Asia/Kolkata' });
export const time = (iso: string) => iso.slice(11, 16);
export const when = (iso: string) => `${day(iso)}, ${time(iso)}`;
export const pct = (x: number) => `${Math.round(x * 100)}%`;
export const num = (x: number) => Math.round(x).toLocaleString('en-IN');
export const inr = (x: number) => `${x < 0 ? '−' : ''}₹${Math.abs(Math.round(x)).toLocaleString('en-IN')}`;
export const signed = (x: number) => `${x > 0 ? '+' : x < 0 ? '−' : ''}${Math.abs(Math.round(x * 100))}%`;
export const plus = (x: number) => `${x > 0 ? '+' : x < 0 ? '−' : ''}${Math.abs(Math.round(x)).toLocaleString('en-IN')}`;

/** Runs of hours with an empty shelf, as index ranges for chart bands. */
export function bands(empty: number[]) {
  const out: { from: number; to: number }[] = [];
  let start = -1;
  empty.forEach((v, i) => {
    if (v > 0 && start < 0) start = i;
    if ((v <= 0 || i === empty.length - 1) && start >= 0) {
      out.push({ from: start, to: v > 0 ? i : i - 1 });
      start = -1;
    }
  });
  return out;
}

export function h<K extends keyof HTMLElementTagNameMap>(tag: K, cls?: string, text?: string): HTMLElementTagNameMap[K] {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

export function tiles(items: { label: string; value: string; note?: string }[]) {
  const wrap = h('div', 'tiles');
  for (const t of items) {
    const d = h('div', 'tile');
    d.append(h('span', 'tile-label', t.label), h('span', 'tile-value', t.value));
    if (t.note) d.append(h('span', 'tile-note', t.note));
    wrap.append(d);
  }
  return wrap;
}

export function recordBlock(lines: string[], caption: string) {
  const fig = h('figure', 'record');
  const pre = h('pre', 'rec');
  pre.textContent = lines.join('\n');
  fig.append(pre, h('figcaption', '', caption));
  return fig;
}

export function says(text: string, voice: 'person' | 'record' = 'person') {
  const p = h('p', voice === 'record' ? 'says rec' : 'says');
  p.textContent = text;
  return p;
}

/** A records table for the drawer: optional "what really happened" column when revealed. */
export function recordsTable(head: string[], rows: { cells: (string | number)[]; flag?: string }[], reveal: boolean) {
  const wrap = h('div', 'table-wrap tall');
  const table = h('table', 'records-table');
  const thead = h('thead');
  const tr = h('tr');
  for (const c of [...head, ...(reveal ? ['What really happened'] : [])]) { const th = h('th', '', c); th.scope = 'col'; tr.append(th); }
  thead.append(tr);
  const tbody = h('tbody');
  for (const row of rows) {
    const t = h('tr');
    row.cells.forEach((c, i) => t.append(h('td', i === 0 ? 'rec' : '', String(c))));
    if (reveal) {
      const cell = h('td');
      if (row.flag) cell.append(h('span', 'gap', row.flag));
      t.append(cell);
    }
    tbody.append(t);
  }
  table.append(thead, tbody);
  wrap.append(table);
  return wrap;
}

/** A small static table (caption, header row, body rows) for panels. Numbers, and the dash that
 * stands in for one, align right, and so does the header of a column that holds only those. */
export function smallTable(cls: string, caption: string, head: string[] | null, rows: (string | number)[][]) {
  const wrap = h('div', 'table-wrap');
  const table = h('table', cls);
  table.append(h('caption', '', caption));
  const numeric = (c: string | number) => typeof c === 'number' || /^[−+₹\d–]/.test(String(c));
  if (head) {
    const thead = h('thead');
    const tr = h('tr');
    head.forEach((c, i) => {
      const th = h('th', i > 0 && rows.length && rows.every((r) => numeric(r[i])) ? 'n' : '', c);
      th.scope = 'col';
      tr.append(th);
    });
    thead.append(tr);
    table.append(thead);
  }
  const tb = h('tbody');
  for (const r of rows) {
    const tr = h('tr');
    r.forEach((c, i) => {
      const cell = h(i === 0 ? 'th' : 'td', i === 0 ? '' : numeric(c) ? 'n' : '', String(c));
      if (i === 0) (cell as HTMLTableCellElement).scope = 'row';
      tr.append(cell);
    });
    tb.append(tr);
  }
  table.append(tb);
  wrap.append(table);
  return wrap;
}

/** Wire an ARIA tablist: click and arrow keys select; returns select(). */
export function wireTabs(root: HTMLElement, onSelect: (key: string) => void) {
  const tabs = [...root.querySelectorAll<HTMLButtonElement>('[role="tab"][data-persona]')];
  const select = (p: string, focus = false) => {
    for (const t of tabs) {
      const on = t.dataset.persona === p;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    }
    onSelect(p);
  };
  tabs.forEach((t, k) => {
    t.addEventListener('click', () => select(t.dataset.persona as string));
    t.addEventListener('keydown', (ev) => {
      if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
      const next = tabs[(k + (ev.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      select(next.dataset.persona as string, true);
    });
  });
  return select;
}
