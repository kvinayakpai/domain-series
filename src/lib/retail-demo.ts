// Retail demo: one store, one month, six ways of looking at the same 5 kg atta shelf.
import data from '../data/retail.json';
import { barChart, lineChart, tableView, type Tooltip } from './charts';
import { bands, day, h, inr, num, pct, recordBlock, says, signed, tiles, when } from './demo-kit';

type Data = typeof data;
type Scn = Data['scenarios'][number];
type Episode = Scn['episodes'][number];

const C = { record: 'var(--c-record)', reality: 'var(--c-reality)', misplaced: 'var(--c-misplaced)' };
const HOURS = data.meta.hours as number[];
const DAYS = data.meta.days as string[];
const NH = HOURS.length;

const hourLabel = (i: number) => `${day(DAYS[Math.floor(i / NH)])}, ${String(HOURS[i % NH]).padStart(2, '0')}:00`;
// Events before opening (a 06:17 delivery) sit on the first open hour of that day.
const idxOf = (iso: string) => DAYS.indexOf(iso.slice(0, 10)) * NH + Math.min(NH - 1, Math.max(0, Number(iso.slice(11, 13)) - HOURS[0]));

const weekTick = (i: number) => (i % (7 * NH) === 0 ? day(DAYS[i / NH]) : null);
const dayTick = (i: number) => (i % 7 === 0 ? day(DAYS[i]) : null);

function big(eps: Episode[], from: string, to: string) {
  return eps.filter((e) => e.start >= from && e.start < to && e.empty_open_hours >= 5)
    .sort((a, b) => b.empty_open_hours - a.empty_open_hours)[0];
}

// ---------- state ----------
const state = { alert: 'off', routine: 'today', persona: 'store', milk: 3 };
const scn = () => data.scenarios.find((s) => s.key === `${state.alert}|${state.routine}`) as Scn;
const asIs = data.scenarios.find((s) => s.key === 'off|today') as Scn;

function episodesOf(s: Scn) {
  return { first: big(s.episodes, '2026-06-01', '2026-06-21'), second: big(s.episodes, '2026-06-21', '2026-06-29') };
}

function eventOf(s: Scn, kind: string, after = '2026-06-01') {
  return s.events.find((e) => e.kind === kind && e.sku === data.hero.sku && e.ts >= after);
}

// ---------- outcome strip ----------
function renderOutcome(root: HTMLElement) {
  const s = scn();
  const base = asIs.kpis;
  const k = s.kpis;
  const host = root.querySelector('[data-outcome]') as HTMLElement;
  host.replaceChildren(tiles([
    { label: 'Open hours the 5 kg shelf stood empty in June', value: num(k.empty_open_hours),
      note: s === asIs ? 'the store as it runs today' : `${num(base.empty_open_hours)} as it runs today` },
    { label: 'Bags customers wanted but could not buy', value: num(k.lost_units),
      note: `${inr(k.lost_value_inr)} at the shelf price` },
    { label: 'Share of demand served from the shelf', value: pct(k.osa.demand_served),
      note: `the system said in stock ${pct(k.osa.system_in_stock)} of open hours` },
  ]));
}

// ---------- personas ----------
type Panel = (host: HTMLElement, s: Scn) => void;

const store: Panel = (host, s) => {
  const { first } = episodesOf(s);
  const probe = first ? DAYS.find((d) => d > first.start.slice(0, 10) && d < first.end.slice(0, 10)) ?? first.start.slice(0, 10) : '2026-06-11';
  const i = DAYS.indexOf(probe) * NH + (19 - HOURS[0]);
  const shelf = s.hourly.shelf[i];
  const book = s.hourly.book[i];
  host.append(recordBlock([
    `Shelf walk, ${day(probe)} 19:40`,
    `Atta 5 kg bay:      ${shelf === 0 ? 'empty' : `${shelf} bags`}`,
    `Handheld on hand:   ${book}`,
  ], 'What the store manager sees on the floor, and what the handheld says.'));
  const long = s.episodes.filter((e) => e.empty_open_hours >= 5);
  host.append(tiles([
    { label: 'Open hours with an empty shelf in June', value: num(s.kpis.empty_open_hours) },
    { label: 'Gaps longer than five open hours', value: String(long.length),
      note: long.length ? long.map((e) => `${num(e.empty_open_hours)} h from ${when(e.start)}`).join('; ') : undefined },
    { label: 'Bags customers could not buy', value: num(s.kpis.lost_units) },
  ]));
  const alertCount = eventOf(s, 'alert_count');
  const quote = !first
    ? '“Every case has a bin now. When the shelf runs low, we know where the stock is.”'
    : alertCount && alertCount.ts < first.end
      ? `“The low-sales alert sent someone to count on ${day(alertCount.ts)} morning. The cases were behind the rice.”`
      : `“The handheld says we have ${book}. We looked in the backroom and couldn't find any. It must be on the next truck.”`;
  host.append(says(quote));
  const chart = h('div');
  host.append(h('h4', '', 'Bags on the 5 kg shelf, every open hour in June'), chart);
  lineChart(chart, {
    ariaLabel: 'Bags on the 5 kg shelf by hour, June 2026',
    series: [{ key: 'shelf', label: 'On the shelf', color: C.reality, values: s.hourly.shelf, area: true }],
    bands: bands(s.hourly.empty),
    xTick: weekTick,
    tooltip: (j): Tooltip => ({ title: hourLabel(j), rows: [{ label: 'bags on the shelf', value: num(s.hourly.shelf[j]), color: C.reality }] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'Bags on the shelf at 19:00 each day', ['Day', 'On the shelf at 19:00', 'Open hours empty'],
    DAYS.map((d, k) => [day(d), s.hourly.shelf[k * NH + 12], s.hourly.empty.slice(k * NH, k * NH + NH).reduce((a, b) => a + b, 0).toFixed(1)]));
};

const system: Panel = (host, s) => {
  const { first } = episodesOf(s);
  const d0 = first ? Math.max(0, DAYS.indexOf(first.start.slice(0, 10))) : 9;
  const lines = ['Night   On hand  Reorder at  Order'];
  for (let d = d0; d < Math.min(DAYS.length - 1, d0 + 3); d++) {
    lines.push(`${DAYS[d].slice(8)} Jun  ${String(s.daily.book_close[d]).padStart(7)}  ${String(s.daily.reorder_point[d + 1]).padStart(10)}  ${String(s.daily.ordered[d]).padStart(5)}`);
  }
  host.append(recordBlock(lines, 'The nightly reorder run at 22:00, as the system logs it (bags).'));
  const nightsNoOrder = first
    ? DAYS.filter((d, k) => d >= first.start.slice(0, 10) && d < first.end.slice(0, 10) && s.daily.ordered[k] === 0).length
    : 0;
  host.append(tiles([
    { label: 'Open hours the system showed stock', value: pct(s.kpis.osa.system_in_stock) },
    { label: 'Nights it ordered nothing while the shelf was empty', value: first ? String(nightsNoOrder) : '0' },
    { label: first ? `Stock on the books while the shelf was empty, ${day(first.start)} to ${day(first.end)}` : 'Stock on the books during a long gap',
      value: first ? `${first.book_on_hand_min}–${first.book_on_hand_max}` : 'none',
      note: first ? `reorder point ${first.reorder_point.join('–')}` : undefined },
  ]));
  const alerted = s.events.find((e) => e.kind === 'low_sales_alert' && e.sku === data.hero.sku);
  host.append(says(alerted ? `Low sales against the books on ${day(alerted.ts)}. Count requested for next morning.` : 'In stock. No reorder needed.', 'record'));
  const chart = h('div');
  host.append(h('h4', '', 'Stock on the books at closing time, and the reorder point'), chart);
  barChart(chart, {
    ariaLabel: 'Book stock at close and reorder point by day, June 2026',
    series: [{ key: 'book', label: 'On the books at close', color: C.record, values: s.daily.book_close }],
    refs: [{ values: s.daily.reorder_point, label: 'Reorder point' }],
    xTick: dayTick,
    tooltip: (j) => ({ title: day(DAYS[j]), rows: [
      { label: 'on the books at close', value: num(s.daily.book_close[j]), color: C.record },
      { label: 'reorder point', value: num(s.daily.reorder_point[j]) },
      { label: 'ordered that night', value: num(s.daily.ordered[j]) },
    ] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'Nightly reorder run', ['Day', 'On the books at close', 'Reorder point', 'Ordered'],
    DAYS.map((d, k) => [day(d), s.daily.book_close[k], s.daily.reorder_point[k], s.daily.ordered[k]]));
};

const planner: Panel = (host, s) => {
  const w = s.kpis.weekly;
  const rec = w.recorded_sales['ATTA-WW-5KG' as keyof typeof w.recorded_sales] as number[];
  host.append(recordBlock([
    'Weekly sales report, atta 5 kg (bags)',
    ...w.weeks.map((wk, k) => `${wk.padEnd(15)} ${String(rec[k]).padStart(4)}${k ? `  ${signed(rec[k] / rec[k - 1] - 1)}` : ''}`),
  ], 'What the demand planner sees: sales as the tills recorded them.'));
  host.append(tiles([
    { label: 'Recorded sales, week 2 against week 1', value: signed(rec[1] / rec[0] - 1) },
    { label: 'Forecast, start to end of June', value: `${s.kpis.forecast.start} → ${s.kpis.forecast.end}`, note: 'bags a day' },
    { label: 'Forecast error against recorded sales', value: pct(s.kpis.forecast.wmape_vs_recorded_sales), note: 'weighted MAPE' },
  ]));
  host.append(says(s.kpis.forecast.end < s.kpis.forecast.start - 1
    ? '“5 kg demand is falling and getting erratic. Trim the forecast and the order.”'
    : '“5 kg is steady. The forecast is tracking.”'));
  const chart = h('div');
  host.append(h('h4', '', 'Recorded sales of 5 kg atta each day, and the forecast'), chart);
  barChart(chart, {
    ariaLabel: 'Recorded daily sales and forecast, June 2026',
    series: [{ key: 'sales', label: 'Recorded sales', color: C.record, values: s.daily.recorded['5kg'] }],
    refs: [{ values: s.daily.forecast, label: 'Forecast' }],
    xTick: dayTick,
    tooltip: (j) => ({ title: day(DAYS[j]), rows: [
      { label: 'recorded sales', value: num(s.daily.recorded['5kg'][j]), color: C.record },
      { label: 'forecast', value: s.daily.forecast[j].toFixed(1) },
    ] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'Recorded sales and forecast', ['Day', 'Recorded sales', 'Forecast'],
    DAYS.map((d, k) => [day(d), s.daily.recorded['5kg'][k], s.daily.forecast[k].toFixed(1)]));
};

const category: Panel = (host, s) => {
  const w = s.kpis.weekly.recorded_sales as Record<string, number[]>;
  const share = w['ATTA-WW-5KG'].map((v, k) => v / (v + w['ATTA-WW-1KG'][k] + w['ATTA-WW-10KG'][k]));
  host.append(recordBlock([
    'Atta sales by pack, share of units',
    ...s.kpis.weekly.weeks.map((wk, k) => `${wk.padEnd(15)} 5 kg ${pct(share[k]).padStart(4)}   1 kg ${String(w['ATTA-WW-1KG'][k]).padStart(3)}   10 kg ${String(w['ATTA-WW-10KG'][k]).padStart(3)}`),
  ], 'What the category manager sees: the pack mix, as the tills recorded it.'));
  host.append(tiles([
    { label: '5 kg share of atta units, week 1', value: pct(share[0]) },
    { label: '5 kg share, week 2', value: pct(share[1]) },
    { label: '5 kg share, week 4', value: pct(share[3]) },
  ]));
  host.append(says(share[1] < share[0] - 0.08
    ? '“Shoppers are moving away from the 5 kg pack. Give some of its shelf space to 1 kg.”'
    : '“The pack mix is stable.”'));
  const chart = h('div');
  host.append(h('h4', '', '5 kg share of atta units sold, by week'), chart);
  barChart(chart, {
    ariaLabel: '5 kg share of atta units by week',
    series: [{ key: 'share', label: '5 kg share', color: C.record, values: share.map((x) => Math.round(x * 100)) }],
    yMax: 50,
    yFormat: (v) => `${Math.round(v)}%`,
    xTick: (j) => s.kpis.weekly.weeks[j].split('-')[0],
    tooltip: (j) => ({ title: `Week of ${s.kpis.weekly.weeks[j].split('-')[0]}`, rows: [{ label: '5 kg share of units', value: pct(share[j]), color: C.record }] }),
  });
};

const supplier: Panel = (host, s) => {
  const o = s.kpis.weekly.store_orders_units;
  host.append(recordBlock([
    'Orders from Store 014, atta 5 kg (bags)',
    ...s.kpis.weekly.weeks.map((wk, k) => `${wk.padEnd(15)} ${String(o[k]).padStart(4)}`),
  ], "What the atta supplier's sales rep sees: orders, nothing else."));
  host.append(tiles([
    { label: 'Orders, week 2 against week 1', value: signed(o[1] / o[0] - 1) },
    { label: 'Bags ordered in June', value: num(o.reduce((a, b) => a + b, 0)) },
  ]));
  host.append(says(o[1] < o[0] * 0.8
    ? '“Store 014 is ordering less of our 5 kg. Is a competitor’s brand getting the space?”'
    : '“Store 014 orders are steady.”'));
  const chart = h('div');
  host.append(h('h4', '', 'Bags of 5 kg atta ordered by the store, by week'), chart);
  barChart(chart, {
    ariaLabel: 'Store orders of 5 kg atta by week',
    series: [{ key: 'orders', label: 'Ordered', color: C.record, values: o }],
    xTick: (j) => s.kpis.weekly.weeks[j].split('-')[0],
    tooltip: (j) => ({ title: `Week of ${s.kpis.weekly.weeks[j].split('-')[0]}`, rows: [{ label: 'bags ordered', value: num(o[j]), color: C.record }] }),
  });
};

const truth: Panel = (host, s) => {
  const { first, second } = episodesOf(s);
  const mis = eventOf(s, 'misplaced_putaway');
  const found = eventOf(s, 'found_in_backroom') ?? eventOf(s, 'alert_count');
  const caught = eventOf(s, 'put_away_scan_caught_mismatch');
  const story = h('div', 'story');
  if (first && mis) {
    const r = first.responses as Record<string, number>;
    story.append(
      h('p', '', `${when(mis.ts)}: ${mis.units / data.hero.case_units} cases (${mis.units} bags) are put away behind the rice stack, in the wrong bay.`),
      h('p', '', `${when(first.start)}: the shelf runs out. The books still show ${first.book_on_hand_max} bags, above the reorder point of ${first.reorder_point[first.reorder_point.length - 1]}, so nothing is ordered.`),
      h('p', '', `${found ? when(found.ts) : when(first.end)}: ${found?.kind === 'alert_count' ? 'the low-sales alert sends someone to count, and they find the cases' : 'staff restacking the rice find the cases'}. The shelf was empty for ${first.empty_open_hours} open hours.`),
      h('p', '', `Customers wanted ${first.lost_units} bags they could not buy: ${r.other_brand} bought another brand, ${r.other_pack} took a different pack size, ${r.elsewhere} went elsewhere, ${r.delay} came back later and ${r.skip} gave up.`),
    );
  } else {
    story.append(h('p', '', 'With every case scanned into a bin, nothing goes missing in the backroom, and refill rounds keep the shelf stocked.'));
  }
  if (caught) {
    story.append(h('p', '', `${when(caught.ts)}: the put-away scan finds 1 kg cases on a line booked as 5 kg, and the receipt is corrected before it can mislead anyone.`));
  } else if (second) {
    story.append(h('p', 'aside', `On ${day(second.start)} the shelf empties again for ${second.empty_open_hours} open hours, for a different reason that starts at the warehouse. That's the logistics post.`));
  }
  host.append(story);
  const chart = h('div');
  host.append(h('h4', '', 'What the books said, what was on the shelf, and what was lost in the backroom'), chart);
  const kinds = ['misplaced_putaway', 'found_in_backroom', 'alert_count', 'wrong_pallet', 'complaint_count', 'put_away_scan_caught_mismatch'];
  const markers = s.events
    .filter((e) => e.sku === data.hero.sku && kinds.includes(e.kind))
    .map((e) => ({ at: idxOf(e.ts), label: e.kind }))
    .filter((m) => m.at >= 0);
  lineChart(chart, {
    ariaLabel: 'Book stock, shelf stock and misplaced stock by hour, June 2026',
    height: 240,
    series: [
      { key: 'book', label: 'On the books', color: C.record, values: s.hourly.book },
      { key: 'shelf', label: 'On the shelf', color: C.reality, values: s.hourly.shelf },
      { key: 'misplaced', label: 'In the wrong bay', color: C.misplaced, values: s.hourly.misplaced },
    ],
    bands: bands(s.hourly.empty),
    markers,
    xTick: weekTick,
    tooltip: (j) => ({ title: hourLabel(j), rows: [
      { label: 'on the books', value: num(s.hourly.book[j]), color: C.record },
      { label: 'on the shelf', value: num(s.hourly.shelf[j]), color: C.reality },
      { label: 'in the wrong bay', value: num(s.hourly.misplaced[j]), color: C.misplaced },
      { label: 'customers wanted', value: num(s.hourly.demand[j]) },
    ] }),
  });
  const o = s.kpis.osa;
  const table = h('table', 'four-ways');
  table.append(h('caption', '', 'On-shelf availability for June, measured four ways'));
  const tb = h('tbody');
  for (const [label, value, how] of [
    ['The system showed stock', pct(o.system_in_stock), 'open hours with stock on the books'],
    ['Shelf audits found it', pct(o.shelf_audit), `${o.audits.length} audits, Tuesdays and Fridays at 11:00`],
    ['It was on the shelf', pct(o.open_hours_on_shelf), 'open hours with at least one bag on the shelf'],
    ['Customers found it', pct(o.demand_served), 'bags wanted that were on the shelf'],
  ]) {
    const tr = h('tr');
    tr.append(h('th', '', label), h('td', 'n', value), h('td', 'how', how));
    tb.append(tr);
  }
  table.append(tb);
  host.append(table);
};

const PANELS: Record<string, Panel> = { store, system, planner, category, supplier, truth };

function renderPersona(root: HTMLElement) {
  const host = root.querySelector('[data-panel]') as HTMLElement;
  host.replaceChildren();
  PANELS[state.persona](host, scn());
  host.setAttribute('aria-labelledby', `tab-${state.persona}`);
}

// ---------- milk ----------
function renderMilk(root: HTMLElement) {
  const m = data.milk[state.milk];
  const out = root.querySelector('[data-milk-out]') as HTMLElement;
  const std = data.milk_product.standing_order as { weekday: number; weekend: number };
  (root.querySelector('[data-milk-label]') as HTMLElement).textContent =
    `${Math.round(std.weekday * m.factor)} pouches on weekdays, ${Math.round(std.weekend * m.factor)} at weekends (${signed(m.factor - 1)} on today's order)`;
  out.replaceChildren(tiles([
    { label: 'Pouches thrown away after their date', value: num(m.expired), note: `${pct(m.waste_share)} of deliveries` },
    { label: 'Pouches customers wanted and could not find', value: num(m.lost), note: `${pct(m.unmet_share)} of demand` },
    { label: 'Milk margin after waste', value: inr(m.net_inr), note: `${inr(m.gross_margin_inr)} earned, ${inr(m.waste_cost_inr)} thrown away` },
  ]));
  const chart = root.querySelector('[data-milk-chart]') as HTMLElement;
  lineChart(chart, {
    ariaLabel: 'Pouches thrown away and pouches short, by standing order',
    height: 200,
    series: [
      { key: 'expired', label: 'Thrown away', color: C.record, values: data.milk.map((x) => x.expired) },
      { key: 'lost', label: 'Wanted but not found', color: C.reality, values: data.milk.map((x) => x.lost) },
    ],
    markers: [{ at: state.milk, label: 'selected' }],
    xTick: (j) => signed(data.milk[j].factor - 1),
    tooltip: (j) => ({ title: `Standing order ${signed(data.milk[j].factor - 1)}`, rows: [
      { label: 'thrown away', value: num(data.milk[j].expired), color: C.record },
      { label: 'wanted but not found', value: num(data.milk[j].lost), color: C.reality },
      { label: 'margin after waste', value: inr(data.milk[j].net_inr) },
    ] }),
  });
}

// ---------- records drawer ----------
function renderRecords(root: HTMLElement, which: string, reveal: boolean) {
  const host = root.querySelector('[data-records]') as HTMLElement;
  host.replaceChildren();
  const r = data.records;
  let head: string[] = [];
  let rows: { cells: (string | number)[]; flag?: string }[] = [];
  if (which === 'till') {
    head = ['Bill', 'Time', 'Item scanned', 'Qty', 'Amount'];
    rows = r.pos_lines.map((l) => ({ cells: [l.bill_id, when(l.bill_ts), l.sku_scanned, l.qty, inr(l.line_amount)],
      flag: l.scan_error ? `Really ${l.scan_error}` : undefined }));
  } else if (which === 'book') {
    head = ['Day', 'On the books at close', 'Shelf audit', 'Count'];
    const audits = Object.fromEntries(r.audits.map((a) => [a.audit_ts.slice(0, 10), a.status]));
    const counts = Object.fromEntries(asIs.counts.filter((c) => c.sku === data.hero.sku).map((c) => [c.count_ts.slice(0, 10), `${c.book_before} → ${c.counted}`]));
    rows = DAYS.map((d, k) => ({ cells: [day(d), asIs.daily.book_close[k], audits[d] ?? '', counts[d] ?? ''],
      flag: reveal && asIs.daily.physical_close[k] !== asIs.daily.book_close[k] ? `Really ${asIs.daily.physical_close[k]} in the building` : undefined }));
  } else if (which === 'reorder') {
    head = ['Night', 'Forecast a day', 'On hand', 'Reorder point', 'Ordered'];
    rows = r.forecasts.map((f) => ({ cells: [day(f.date), f.forecast_units_per_day.toFixed(1), f.book_on_hand, f.reorder_point, f.ordered_units] }));
  } else {
    head = ['Received', 'Pallet (SSCC)', 'Booked as', 'Bags', 'How'];
    rows = r.receipts.map((x) => ({ cells: [when(x.received_ts), x.sscc, x.sku_booked, x.units_booked, x.receipt_method.startsWith('pallet') ? 'pallet label' : 'case scan'] }));
  }
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
  host.append(wrap);
}

// ---------- wiring ----------
export function mountRetailDemo(root: HTMLElement) {
  const tabs = [...root.querySelectorAll<HTMLButtonElement>('[role="tab"][data-persona]')];
  const select = (p: string, focus = false) => {
    state.persona = p;
    for (const t of tabs) {
      const on = t.dataset.persona === p;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    }
    renderPersona(root);
  };
  tabs.forEach((t, k) => {
    t.addEventListener('click', () => select(t.dataset.persona as string));
    t.addEventListener('keydown', (ev) => {
      if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
      const next = tabs[(k + (ev.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      select(next.dataset.persona as string, true);
    });
  });
  root.querySelectorAll<HTMLInputElement>('input[name="alert"], input[name="routine"]').forEach((inp) => {
    inp.addEventListener('change', () => {
      state[inp.name as 'alert' | 'routine'] = inp.value;
      renderOutcome(root);
      renderPersona(root);
    });
  });
  const slider = root.querySelector<HTMLInputElement>('input[name="milk"]');
  slider?.addEventListener('input', () => { state.milk = Number(slider.value); renderMilk(root); });
  let recTab = 'till';
  const reveal = root.querySelector<HTMLInputElement>('input[name="reveal"]');
  root.querySelectorAll<HTMLButtonElement>('[data-rec]').forEach((b) => {
    b.addEventListener('click', () => {
      recTab = b.dataset.rec as string;
      root.querySelectorAll('[data-rec]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      renderRecords(root, recTab, !!reveal?.checked);
    });
  });
  reveal?.addEventListener('change', () => renderRecords(root, recTab, reveal.checked));

  // Deep links: #retail?persona=truth&alert=1d&routine=scanned
  const q = new URLSearchParams(location.search);
  if (q.get('alert') && ['off', '2d', '1d'].includes(q.get('alert') as string)) state.alert = q.get('alert') as string;
  if (q.get('routine') && ['today', 'scanned'].includes(q.get('routine') as string)) state.routine = q.get('routine') as string;
  root.querySelectorAll<HTMLInputElement>('input[name="alert"], input[name="routine"]').forEach((inp) => {
    inp.checked = inp.value === state[inp.name as 'alert' | 'routine'];
  });
  renderOutcome(root);
  select(q.get('persona') && PANELS[q.get('persona') as string] ? (q.get('persona') as string) : 'store');
  renderMilk(root);
  renderRecords(root, recTab, false);
  root.dataset.ready = 'true';
  (window as unknown as { retailDemo: unknown }).retailDemo = {
    state,
    select,
    set(name: 'alert' | 'routine', value: string) {
      const inp = root.querySelector<HTMLInputElement>(`input[name="${name}"][value="${value}"]`);
      if (inp) { inp.checked = true; inp.dispatchEvent(new Event('change')); }
    },
    milk(i: number) { if (slider) { slider.value = String(i); slider.dispatchEvent(new Event('input')); } },
  };
}
