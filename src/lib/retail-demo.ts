// Retail demo: Store 014's June as a data team reads it. The data team's views (data tests,
// forecast, AI assistant, gap detector) are computed from June's records as they happened, by
// scripts/analysis/retail.py. The store's options rerun June in the world on the same shoppers.
// Every result is scored against the answer key.
import data from '../data/retail.json';
import ai from '../data/retail-ai.json';
import { barChart, lineChart, tableView, type Tooltip } from './charts';
import { bands, day, h, inr, num, pct, recordBlock, says, signed, smallTable, tiles, time, when, wireTabs } from './demo-kit';

type Scn = (typeof data)['scenarios'][number];
type Episode = Scn['episodes'][number];
type Question = (typeof ai)['assistant']['questions'][number];
type Answer = Question['naive'];
type Step = { sql: string; result: Record<string, unknown>[] };
interface Run {
  first: number; alert: number; last: number; expected_at_alert: number; expected_total: number;
  recorded: number; book_at_alert: number; resumed: string | null; real: boolean;
}
interface Grid {
  recorded: number[]; expected: number[]; book: number[]; empty: number[];
  censored: Record<string, string>; runs: Record<string, Run[]>; no_stock: string;
}

const GRID = ai.detector.grid as unknown as Record<string, Grid>;
const C = { record: 'var(--c-record)', reality: 'var(--c-reality)', misplaced: 'var(--c-misplaced)' };
const HERO = data.hero.sku;
const HOURS = data.meta.hours as number[];
const DAYS = data.meta.days as string[];
const NH = HOURS.length;
const WEEKS = ['1–7 Jun', '8–14 Jun', '15–21 Jun', '22–28 Jun'];
const ITEMS = ['ATTA-WW-5KG', 'ATTA-WW-1KG', 'ATTA-WW-10KG', 'RICE-SM-5KG', 'DAL-TOOR-1KG', 'OIL-SUN-1L', 'SUGAR-1KG'];
const NAMES: Record<string, string> = {
  'ATTA-WW-5KG': '5 kg atta', 'ATTA-WW-1KG': '1 kg atta', 'ATTA-WW-10KG': '10 kg atta', 'RICE-SM-5KG': 'rice',
  'DAL-TOOR-1KG': 'toor dal', 'OIL-SUN-1L': 'sunflower oil', 'SUGAR-1KG': 'sugar', 'MILK-FC-500ML': 'full-cream milk',
  'MILK-TONED-500ML': 'toned milk', 'CURD-500G': 'curd', 'BREAD-WHITE-400G': 'bread',
};
const ALPHAS = ['0.01', '0.001', '0.0001'];
const QUESTIONS = ai.assistant.questions as Question[];

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const pad2 = (n: number) => String(n).padStart(2, '0');
const oneIn = (a: string | number) => `1 in ${Math.round(1 / Number(a)).toLocaleString('en-IN')}`;
const hrs = (v: number | null | undefined) => (v == null ? '–' : v >= 10 ? String(Math.round(v)) : v.toFixed(1).replace(/\.0$/, ''));
const hourOf = (i: number) => `${day(DAYS[Math.floor(i / NH)])}, ${pad2(HOURS[i % NH])}:00`;
const alertAt = (i: number) => `${day(DAYS[Math.floor(i / NH)])}, ${pad2(HOURS[i % NH] + 1)}:00`;
const isoEnd = (i: number) => `${DAYS[Math.floor(i / NH)]}T${pad2(HOURS[i % NH] + 1)}:00`;
// Events before opening (a 06:17 delivery) sit on the first open hour of that day.
const idxOf = (iso: string) => DAYS.indexOf(iso.slice(0, 10)) * NH + Math.min(NH - 1, Math.max(0, Number(iso.slice(11, 13)) - HOURS[0]));
const weekTick = (i: number) => (i % (7 * NH) === 0 ? day(DAYS[i / NH]) : null);
const dayTick = (i: number) => (i % 7 === 0 ? day(DAYS[i]) : null);
const shortDay = (iso: string) =>
  `${new Date(`${iso}T12:00:00+05:30`).toLocaleDateString('en-IN', { weekday: 'short', timeZone: 'Asia/Kolkata' })} ${Number(iso.slice(8, 10))}`;

// ---------- state ----------
type Lever = 'forecast' | 'grounding' | 'detect' | 'routine';
const LEVERS: Record<Lever, string[]> = {
  forecast: ['recorded', 'unconstrained'],
  grounding: ['schema', 'domain'],
  detect: ['off', '1d', 'gap'],
  routine: ['today', 'scanned'],
};
const state = {
  persona: 'dashboard',
  forecast: 'recorded',
  grounding: 'schema',
  detect: 'off',
  routine: 'today',
  q: 'why',
  item: HERO,
  alpha: '0.001',
  key: true,
  milk: Math.max(0, data.milk.findIndex((m) => m.factor === 1)),
};
const scn = () => data.scenarios.find((s) => s.key === `${state.detect}|${state.routine}`) as Scn;
const asIs = data.scenarios.find((s) => s.key === 'off|today') as Scn;
const rerun = () => state.detect !== 'off' || state.routine !== 'today';
let root: HTMLElement;

const ev = (s: Scn, kind: string, after = '2026-06-01') => s.events.find((e) => e.kind === kind && e.sku === HERO && e.ts >= after);

function storeDoes() {
  const parts: string[] = [];
  if (state.detect === 'gap') parts.push('someone checks the shelf within an open hour of each gap-detector alert');
  if (state.detect === '1d') parts.push('the store counts the next morning after each nightly low-sales alert');
  if (state.routine === 'scanned') parts.push('every case is scanned into a backroom bin');
  return parts.join(', and ');
}

/** One muted line at the top of a panel: which data it is built on. */
function context(host: HTMLElement, on: 'records' | 'world', extra = '') {
  const text = on === 'world'
    ? rerun() ? `June rerun on the same shoppers: ${storeDoes()}.` : 'June as it ran.'
    : `Computed from June’s records as they happened${rerun() ? ', before anything the store changes' : ''}.`;
  host.append(h('p', 'context', extra ? `${text} ${extra}` : text));
}

// ---------- outcome strip ----------
function renderOutcome() {
  const s = scn();
  const me = ai.forecast.by_sku['ATTA-WW-5KG'].month_end;
  const sc = ai.assistant.score;
  const notes: string[] = [];
  if (s !== asIs) notes.push(`${num(asIs.kpis.lost_units)} as June ran`);
  if (s.dc.checks) notes.push(`${s.dc.checks} alerts across seven items, ${s.dc.flags_in_real_gaps} at a real gap`);
  (root.querySelector('[data-outcome]') as HTMLElement).replaceChildren(tiles([
    { label: '5 kg atta forecast, bags a day',
      value: (state.forecast === 'unconstrained' ? me.aware : me.naive).toFixed(1),
      note: `made 28 June; shoppers came for ${me.true_june_mean.toFixed(1)} a day in June` },
    { label: 'Questions the AI assistant answers right',
      value: `${state.grounding === 'domain' ? sc.domain : sc.naive} of ${sc.of}`,
      note: state.grounding === 'domain' ? 'given the schema and the domain layer' : 'given the schema only' },
    { label: '5 kg bags shoppers could not find in June', value: num(s.kpis.lost_units), note: notes.join('; ') || 'June as it ran' },
  ]));
}

// ---------- panels ----------
type Panel = (host: HTMLElement, s: Scn) => void;

function share5(s: Scn) {
  const w = s.kpis.weekly.recorded_sales;
  return w['ATTA-WW-5KG'].map((v, k) => v / (v + w['ATTA-WW-1KG'][k] + w['ATTA-WW-10KG'][k]));
}

const dashboard: Panel = (host, s) => {
  context(host, 'world');
  const rec = s.kpis.weekly.recorded_sales['ATTA-WW-5KG'];
  const share = share5(s);
  const change = rec[1] / rec[0] - 1;
  host.append(recordBlock([
    'Atta 5 kg, June      Bags  On week',
    ...WEEKS.map((wk, k) => `${wk.padEnd(18)} ${String(rec[k]).padStart(5)}  ${k ? signed(rec[k] / rec[k - 1] - 1).padStart(6) : ''}`.trimEnd()),
    '',
    `Availability, books  ${pct(s.kpis.osa.system_in_stock).padStart(5)}`,
    `5 kg share of atta   ${pct(share[0])} → ${pct(share[1])}`,
  ], 'What the sales dashboard shows: bags as the tills recorded them, and availability computed from book stock.'));
  host.append(tiles([
    { label: 'Sales, 8–14 June against the week before', value: signed(change) },
    { label: 'On-shelf availability on the dashboard', value: pct(s.kpis.osa.system_in_stock), note: 'open hours with stock on the books' },
    { label: '5 kg share of atta units, 8–14 June', value: pct(share[1]), note: `${pct(share[0])} the week before` },
  ]));
  host.append(says(change < -0.4
    ? `“5 kg atta sales fell ${pct(-change)} with stock on hand. Shoppers are moving to the 1 kg pack.”`
    : '“5 kg atta eased after the month-start shop, as it does.”'));
  const chart = h('div');
  host.append(h('h4', '', 'Bags of 5 kg atta sold each day, as the tills recorded them'), chart);
  barChart(chart, {
    ariaLabel: 'Recorded daily sales of 5 kg atta, June 2026',
    series: [{ key: 'sales', label: 'Recorded sales', color: C.record, values: s.daily.recorded['5kg'] }],
    xTick: dayTick,
    tooltip: (j): Tooltip => ({ title: day(DAYS[j]), rows: [{ label: 'bags recorded', value: num(s.daily.recorded['5kg'][j]), color: C.record }] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'Recorded sales of 5 kg atta by day', ['Day', 'Bags recorded'], DAYS.map((d, k) => [day(d), s.daily.recorded['5kg'][k]]));
};

// The world tests' results and evidence, written from their failing rows.
type Row = Record<string, string | number | null>;
function worldResult(i: number, failing: Row[]) {
  const hero = failing.filter((r) => r.sku === HERO);
  if (i === 0) {
    const g = [...hero].sort((a, b) => Number(b.open_hours) - Number(a.open_hours))[0];
    return `Fails: ${failing.length} runs, among them 5 kg atta, ${g.open_hours} open hours from ${when(String(g.start))}`;
  }
  if (i === 1) return `Fails: ${failing.length} audits, among them 5 kg atta at ${when(String(hero[0].audit_ts))} with ${hero[0].book} on the books`;
  if (i === 2) return `Fails: ${failing.length} count lines`;
  return `Fails: ${NAMES[String(failing[0].sku)]}, ${num(Number(failing[0].week1))} bags then ${num(Number(failing[0].week2))}`;
}
function worldEvidence(i: number, failing: Row[]) {
  const name = (r: Row) => cap(NAMES[String(r.sku)] ?? String(r.sku));
  return failing.map((r) => {
    if (i === 0) return `${name(r)}: ${r.open_hours} open hours with no sale from ${when(String(r.start))}, ${r.expected_total} sales expected`;
    if (i === 1) return `${name(r)}: empty at ${when(String(r.audit_ts))}, ${r.book} on the books`;
    if (i === 2) return `${name(r)}: ${when(String(r.count_ts))}, books ${r.book_before}, counted ${r.counted} (${r.trigger})`;
    return `${name(r)}: ${num(Number(r.week1))} bags, then ${num(Number(r.week2))}`;
  });
}

const testsPanel: Panel = (host) => {
  context(host, 'records');
  const g = ai.tests.generic;
  const d = ai.tests.domain;
  const passed = g.filter((t) => t.pass).length;
  host.append(tiles([
    { label: 'The pipeline’s data tests passing', value: `${passed} of ${g.length}`, note: 'keys, values and reconciliations' },
    { label: 'Tests about how a store works, passing', value: `${d.filter((t) => t.pass).length} of ${d.length}`, note: 'each one uses only the records' },
  ]));
  host.append(says('“The pipeline is green, apart from the usual milk scan errors.”'));
  const wrap = h('div', 'table-wrap');
  const table = h('table', 'ledger tests');
  table.append(h('caption', '', 'June’s records, tested two ways'));
  const tb = h('tbody');
  const group = (text: string) => {
    const tr = h('tr', 'group');
    const th = h('th', '', text);
    th.colSpan = 2;
    th.scope = 'colgroup';
    tr.append(th);
    tb.append(tr);
  };
  const row = (name: string, more: { summary: string; body: HTMLElement }, result: string, ok: boolean) => {
    const tr = h('tr');
    const th = h('th', '', name);
    th.scope = 'row';
    const det = h('details', 'more');
    det.append(h('summary', '', more.summary), more.body);
    th.append(det);
    tr.append(th, h('td', ok ? 'ok' : 'no', result));
    tb.append(tr);
  };
  group(`The pipeline’s data tests: ${passed} of ${g.length} pass`);
  for (const t of g) {
    let result = 'Pass';
    if (!t.pass) {
      const items = [...new Set((t.examples as Row[]).map((e) => String(e.sku ?? '')).filter(Boolean))];
      result = `Fails: ${t.failing_rows} rows${items.length ? `, all ${items.map((x) => NAMES[x] ?? x).join(', ')} below zero` : ''}`;
    }
    row(t.name, { summary: 'SQL', body: h('code', 'sql', t.sql) }, result, t.pass);
  }
  group(`Tests about how a store works: 0 of ${d.length} pass`);
  d.forEach((t, i) => {
    const failing = t.failing as unknown as Row[];
    const ul = h('ul', 'evidence');
    for (const line of worldEvidence(i, failing)) ul.append(h('li', '', line));
    row(t.name, { summary: `The ${failing.length} failing ${failing.length === 1 ? 'row' : 'rows'}`, body: ul }, worldResult(i, failing), t.pass);
  });
  table.append(tb);
  wrap.append(table);
  host.append(wrap);
  host.append(h('p', 'note', 'The pipeline’s tests check that the records agree with each other. The other four check the records against how a store works: an item in stock does not go far longer than usual without a sale, an audit does not find an empty shelf while the books show stock, counts agree with the books, and weekly sales of a staple do not halve.'));
};

/** Day indices with at least one censored hour (flagged, or no stock on the books), as chart bands. */
function censoredDays(sku: string, alpha = '0.001') {
  const g = GRID[sku];
  const hit = (j: number) => g.censored[alpha].slice(j * NH, (j + 1) * NH).includes('1') || g.no_stock.slice(j * NH, (j + 1) * NH).includes('1');
  return bands(DAYS.map((_, j) => (hit(j) ? 1 : 0)));
}

const forecastPanel: Panel = (host, s) => {
  context(host, 'records');
  const aware = state.forecast === 'unconstrained';
  const k = aware ? 'aware' : 'naive';
  const f = ai.forecast.by_sku['ATTA-WW-5KG'];
  const made = Object.fromEntries(ai.forecast.made_5kg.map((m) => [m.date, m]));
  host.append(recordBlock([
    'Nightly forecast, atta 5 kg',
    `28-day mean of ${aware ? 'unconstrained demand' : 'recorded sales'}`,
    '',
    'Made at 22:00       Bags a day',
    ...['2026-06-09', '2026-06-14', '2026-06-21', '2026-06-28'].map((d) => `${day(d).padEnd(18)} ${made[d][k].toFixed(1).padStart(6)}`),
  ], aware
    ? 'Unconstrained demand: recorded sales, plus, in every censored hour, the sales expected beyond those recorded. Censored hours are the ones the gap detector flagged and the ones with no stock on the books.'
    : 'The store’s forecast, rebuilt from the till lines.'));
  const vr = aware ? f.aware_vs_recorded : f.naive_vs_recorded;
  const vt = aware ? f.aware_vs_true : f.naive_vs_true;
  const up = ai.forecast.order_up_to_month_end[k];
  host.append(tiles([
    { label: 'Forecast made on 28 June, bags a day', value: f.month_end[k].toFixed(1), note: `shoppers came for ${f.month_end.true_june_mean.toFixed(1)} a day in June` },
    { label: 'Bias over June, against recorded sales', value: signed(vr.bias), note: 'the score the team can compute' },
    { label: 'Bias over June, against what shoppers wanted', value: signed(vt.bias), note: 'the score from the answer key' },
    { label: 'Order-up-to level it sets at month end', value: `${up[1]} bags`, note: `reorder point ${up[0]}` },
  ]));
  host.append(says(aware
    ? `“Scored on recorded sales, the new forecast looks worse: ${pct(vr.bias)} high. Scored on what shoppers wanted, its bias is ${signed(vt.bias)}, not ${signed(f.naive_vs_true.bias)}.”`
    : `“The forecast runs ${pct(vr.bias)} above sales. Tune it down.”`));
  const ser = ai.forecast.series_5kg;
  const chart = h('div');
  host.append(h('h4', '', 'Bags of 5 kg atta each day in June, and the forecast in use'), chart);
  lineChart(chart, {
    ariaLabel: 'Recorded sales, demand and forecast of 5 kg atta by day, June 2026',
    height: 240,
    series: [
      { key: 'recorded', label: 'Recorded sales', color: C.record, values: ser.map((x) => x.recorded) },
      ...(aware ? [{ key: 'unc', label: 'Recorded plus imputed', color: C.misplaced, values: ser.map((x) => Math.round((x.recorded + x.imputed) * 10) / 10) }] : []),
      { key: 'true', label: 'Shoppers came for (answer key)', color: C.reality, values: ser.map((x) => x.true) },
    ],
    refs: [{ values: ser.map((x) => x[k]), label: aware ? 'Forecast from unconstrained demand' : 'Forecast from recorded sales' }],
    bands: censoredDays(HERO),
    bandLabel: 'Days with censored hours',
    xTick: dayTick,
    tooltip: (j): Tooltip => ({ title: day(ser[j].date), rows: [
      { label: 'recorded sales', value: num(ser[j].recorded), color: C.record },
      ...(aware ? [{ label: 'imputed in censored hours', value: ser[j].imputed.toFixed(1), color: C.misplaced }] : []),
      { label: 'shoppers came for', value: num(ser[j].true), color: C.reality },
      { label: 'forecast in use', value: ser[j][k].toFixed(1) },
    ] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'Recorded sales, imputed demand, shoppers and forecast, 5 kg atta', ['Day', 'Recorded', 'Imputed', 'Shoppers came for', 'Forecast in use'],
    ser.map((x) => [day(x.date), x.recorded, x.imputed.toFixed(1), x.true, x[k].toFixed(1)]));
  if (rerun()) {
    host.append(h('p', 'note', `In the rerun, the store’s own forecast learns from the new records: it ends June at ${s.kpis.forecast.end.toFixed(1)} bags a day, against ${asIs.kpis.forecast.end.toFixed(1)} as June ran. Acting on the gaps also cleans the data the next model trains on.`));
  }
};

// ---------- the assistant ----------
const fmtCell = (v: unknown) => {
  if (v == null) return '–';
  if (typeof v === 'number') return Number.isInteger(v) ? v.toLocaleString('en-IN') : String(Math.round(v * 1000) / 1000);
  const t = String(v);
  return /^\d{4}-\d\d-\d\dT/.test(t) ? t.slice(0, 16).replace('T', ' ') : t;
};

function resultTable(rows: Record<string, unknown>[]) {
  const wrap = h('div', 'res');
  const t = h('table');
  const thead = h('thead');
  const tr = h('tr');
  for (const c of Object.keys(rows[0])) { const th = h('th', '', c); th.scope = 'col'; tr.append(th); }
  thead.append(tr);
  const tb = h('tbody');
  for (const r of rows.slice(0, 4)) {
    const row = h('tr');
    for (const v of Object.values(r)) row.append(h('td', '', fmtCell(v)));
    tb.append(row);
  }
  t.append(thead, tb);
  wrap.append(t);
  return wrap;
}

const sideOf = (q: Question): Answer => (state.grounding === 'domain' ? q.domain : q.naive) as Answer;

function renderRun(box: HTMLElement) {
  const q = QUESTIONS.find((x) => x.id === state.q) ?? QUESTIONS[0];
  const side = sideOf(q);
  const plan = side.plan as Step[];
  box.className = `run ${state.grounding}`;
  box.replaceChildren(
    h('p', 'who', state.grounding === 'domain' ? 'AI assistant, given the schema and the domain layer' : 'AI assistant, given the schema'),
    h('p', 'asked', q.question),
    h('p', 'steps-head', `It ran ${plan.length === 1 ? 'one query' : `${plan.length} queries`}:`),
  );
  const ol = h('ol', 'steps');
  for (const step of plan) {
    const li = h('li');
    li.append(h('code', 'sql', step.sql));
    if (step.result.length) li.append(resultTable(step.result));
    ol.append(li);
  }
  const answer = h('blockquote', 'answer-text');
  answer.append(h('p', '', side.answer));
  const verdict = h('p', 'verdict');
  verdict.append(h('strong', side.right ? 'ok' : 'no', side.right ? 'Right.' : 'Wrong.'), document.createTextNode(` Answer key: ${q.gold.short}. ${q.gold.why}`));
  box.append(ol, answer, verdict, h('p', 'rule', `Scoring rule: ${q.check}.`));
}

function domainLayerYaml() {
  const d = ai.assistant.domain_layer;
  const quote = (s: string) => `"${s.replace(/"/g, '\\"')}"`;
  return [
    '# Given to the assistant with the warehouse schema',
    'definitions:',
    ...Object.entries(d.definitions).map(([k, v]) => `  ${k.replace(/ /g, '_')}: ${quote(String(v))}`),
    'rules:',
    ...d.rules.map((r) => `  - ${quote(r)}`),
    'views:',
    ...Object.entries(d.views).map(([k, v]) => `  ${k}: ${quote(String(v))}`),
    `tables_added: [${d.tables_added.join(', ')}]`,
  ].join('\n');
}

const assistantPanel: Panel = (host) => {
  host.append(h('p', 'context', `Asked at the Monday review on 15 June, of the records to Sunday night${rerun() ? ', as they happened' : ''}.`));
  const ask = h('div', 'ask');
  const list = h('div', 'questions');
  list.setAttribute('role', 'group');
  list.setAttribute('aria-label', 'Questions at the Monday review');
  const run = h('div', 'run');
  run.setAttribute('aria-live', 'polite');
  for (const q of QUESTIONS) {
    const right = sideOf(q).right;
    const b = h('button');
    b.type = 'button';
    b.dataset.q = q.id;
    b.setAttribute('aria-pressed', String(q.id === state.q));
    b.append(h('span', 'q', q.question), h('span', `mark ${right ? 'ok' : 'no'}`, right ? 'Right' : 'Wrong'));
    b.addEventListener('click', () => {
      state.q = q.id;
      list.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      renderRun(run);
    });
    list.append(b);
  }
  ask.append(list, run);
  host.append(ask);
  renderRun(run);

  const sc = ai.assistant.score;
  const wrap = h('div', 'table-wrap');
  const table = h('table', 'ledger scores');
  table.append(h('caption', '', `Seven questions: ${sc.naive} of ${sc.of} right with the schema only, ${sc.domain} of ${sc.of} with the domain layer`));
  const thead = h('thead');
  const hr = h('tr');
  ['Question', 'Schema only', 'With the domain layer', 'Answer key'].forEach((c, i) => {
    const th = h('th', i === 1 && state.grounding === 'schema' ? 'on' : i === 2 && state.grounding === 'domain' ? 'on' : '', c);
    th.scope = 'col';
    hr.append(th);
  });
  thead.append(hr);
  const tb = h('tbody');
  for (const q of QUESTIONS) {
    const tr = h('tr');
    const th = h('th', '', q.question);
    th.scope = 'row';
    tr.append(th);
    for (const [side, on] of [[q.naive, state.grounding === 'schema'], [q.domain, state.grounding === 'domain']] as [Answer, boolean][]) {
      const td = h('td', on ? 'on' : '');
      td.append(h('span', side.right ? 'ok' : 'no', side.right ? 'Right' : 'Wrong'), document.createTextNode(` ${side.short}`));
      tr.append(td);
    }
    tr.append(h('td', 'key', q.gold.short));
    tb.append(tr);
  }
  table.append(thead, tb);
  wrap.append(table);
  host.append(wrap);

  const det = h('details', 'layer');
  det.append(h('summary', '', 'What the domain layer adds to the schema'));
  const pre = h('pre', 'yaml');
  pre.textContent = domainLayerYaml();
  det.append(pre, h('p', 'note', `The schema alone has ${ai.assistant.schema_only_tables.join(', ')}. The assistant is scripted so the run can be repeated: for each question it runs the queries the question calls for, with what it was given, and composes the answer from what they return.`));
  host.append(det);
};

// ---------- the gap detector ----------
function segButtons(label: string, name: string, options: [string, string][], current: string) {
  const wrap = h('div', 'local');
  const lab = h('span', 'local-label', label);
  lab.id = `retail-local-${name}`;
  const group = h('div', 'seg buttons');
  group.setAttribute('role', 'group');
  group.setAttribute('aria-labelledby', lab.id);
  for (const [value, text] of options) {
    const b = h('button', '', text);
    b.type = 'button';
    b.dataset[name] = value;
    b.setAttribute('aria-pressed', String(value === current));
    group.append(b);
  }
  wrap.append(lab, group);
  return wrap;
}

function hoursGrid(sku: string, alpha: string, key: boolean) {
  const g = GRID[sku];
  const cens = g.censored[alpha];
  const alerts = new Set(g.runs[alpha].map((r) => r.alert));
  const wrap = h('div', 'hours-wrap');
  wrap.tabIndex = 0;
  const table = h('table', 'hours');
  table.append(h('caption', '', `${cap(NAMES[sku])}, June: units the tills recorded in each open hour. The alerts are listed below the table.`));
  const thead = h('thead');
  const top = h('tr');
  const corner = h('th', '', 'Day');
  corner.scope = 'col';
  top.append(corner);
  for (const hour of HOURS) { const th = h('th', '', String(hour)); th.scope = 'col'; top.append(th); }
  thead.append(top);
  const tb = h('tbody');
  DAYS.forEach((d, j) => {
    const tr = h('tr', j > 0 && j % 7 === 0 ? 'wk' : '');
    const th = h('th', '', shortDay(d));
    th.scope = 'row';
    tr.append(th);
    for (let k = 0; k < NH; k++) {
      const i = j * NH + k;
      const v = g.recorded[i];
      const e = g.empty[i];
      const none = g.no_stock[i] === '1';
      const cls = [v === 0 ? 'z' : '', cens[i] === '1' ? 'c' : '', none ? 'k' : '', alerts.has(i) ? 'a' : '',
        key && e >= 0.5 ? 'e' : key && e > 0 ? 'e part' : ''];
      const td = h('td', cls.filter(Boolean).join(' '), String(v));
      td.title = `${hourOf(i)}: ${v} recorded, ${g.expected[i].toFixed(1)} expected, ${g.book[i]} on the books`
        + `${cens[i] === '1' ? '; censored' : ''}${none ? '; censored, no stock on the books' : ''}${alerts.has(i) ? '; alert raised' : ''}`
        + `${key && e > 0 ? `; shelf empty ${Math.round(e * 60)} min` : ''}`;
      tr.append(td);
    }
    tb.append(tr);
  });
  table.append(thead, tb);
  wrap.append(table);
  return wrap;
}

function gridLegend(key: boolean) {
  const ul = h('ul', 'chart-legend hours-key');
  const item = (cls: string, text: string) => { const li = h('li'); li.append(h('span', `sw ${cls}`), document.createTextNode(text)); ul.append(li); };
  item('c', 'Hour the detector treats as censored');
  item('a', 'Alert raised in this hour');
  item('k', 'No stock on the books: censored, and the records know it');
  if (key) item('e', 'Shelf empty for the hour, from the answer key');
  return ul;
}

function alertsBlock(sku: string, alpha: string, key: boolean) {
  const g = GRID[sku];
  const runs = g.runs[alpha];
  const box = h('div');
  box.append(h('h4', '', `Alerts on ${NAMES[sku]} at ${oneIn(alpha)}`));
  if (!runs.length) box.append(h('p', 'note', `None: no silence on ${NAMES[sku]} in June was less likely than ${oneIn(alpha)}.`));
  else {
    box.append(smallTable('ledger alerts', `${runs.length} ${runs.length === 1 ? 'alert' : 'alerts'}, scored against the answer key`,
      ['Alert raised', 'Quiet since', 'Run, open hours', 'Sales expected by the alert', 'Books showed', ...(key ? ['The shelf, from the answer key'] : [])],
      runs.map((r) => [alertAt(r.alert), hourOf(r.first), String(r.last - r.first + 1), r.expected_at_alert.toFixed(1), String(r.book_at_alert),
        ...(key ? [r.real ? 'Empty: a real gap' : 'Stocked: a false alarm'] : [])])));
  }
  if (key) {
    const gaps = ai.detector.episodes_3h.filter((e) => e.sku === sku);
    const found = (e: (typeof gaps)[number]) => runs.some((r) => e.start <= isoEnd(r.alert) && isoEnd(r.alert) <= e.end);
    const missed = gaps.filter((e) => !found(e));
    const text = !gaps.length
      ? `The answer key has no gap of three open hours or more on ${NAMES[sku]} in June.`
      : `The answer key has ${gaps.length} ${gaps.length === 1 ? 'gap' : 'gaps'} of three open hours or more on ${NAMES[sku]}; the detector found ${gaps.length - missed.length}.`
        + (missed.length ? ` Missed: ${missed.map((e) => `${hrs(e.empty_open_hours)} open hours from ${when(e.start)}`).join('; ')}.` : '');
    box.append(h('p', 'note', text));
  }
  return box;
}

function comparison(alpha: string) {
  const off = ai.detector.options;
  const by = Object.fromEntries(off.map((o) => [o.label, o]));
  const rr = Object.fromEntries(data.detectors.map((o) => [o.label, o]));
  const bins = data.scenarios.find((s) => s.key === 'off|scanned') as Scn;
  const row = (label: string, k: string) => {
    const o = by[k];
    return [label, String(o.flags), String(o.true), `${o.caught} of ${o.gaps}`, hrs(o.median_open_hours_to_flag), String(rr[k].hero_lost_units)];
  };
  const rows = [
    ['Not at all, as today', '–', '–', `0 of ${off[0].gaps}`, '–', String(asIs.kpis.lost_units)],
    row('Nightly rule, after two days', 'daily rule, 2 days'),
    row('Nightly rule, after one day', 'daily rule, 1 day'),
    ...ALPHAS.map((a) => row(`Hourly detector, ${oneIn(a)}`, `hourly, ${oneIn(a)}`)),
    ['Scan every case into a backroom bin', '–', '–', '–', '–', String(bins.kpis.lost_units)],
  ];
  const tbl = smallTable('ledger detectors', 'Seven warehouse items, June: ways of finding empty shelves, scored',
    ['How the store looks for gaps', 'Alerts', 'At an empty shelf', 'Gaps found', 'Open hours to alert', '5 kg bags lost in the rerun'], rows);
  const chosen = 3 + ALPHAS.indexOf(alpha);
  tbl.querySelectorAll('tbody tr')[chosen]?.classList.add('chosen');
  const box = h('div');
  box.append(tbl, h('p', 'note', 'Alerts are scored on June’s records as they happened; gaps found counts the answer key’s gaps of three open hours or more. Bags lost come from rerunning June on the same shoppers with the store acting on every alert: a check within an open hour for the hourly detector, a count next morning for the nightly rule.'));
  return box;
}

const detectorPanel: Panel = (host) => {
  context(host, 'records', 'Each item’s usual pattern is learned from May’s till lines.');
  host.append(h('p', 'panel-intro', 'For each warehouse item, the detector adds up the sales it expects over every run of open hours with no sales while the books show stock, and raises an alert once a silence that long is less likely than the threshold. The hours of a flagged run count as censored: the forecast and the assistant’s domain layer both use them.'));
  const bar = h('div', 'local-controls');
  const items = segButtons('Item', 'item', ITEMS.map((x) => [x, cap(NAMES[x])]), state.item);
  const alphas = segButtons('Alert when a silence is less likely than', 'alpha', ALPHAS.map((a) => [a, oneIn(a)]), state.alpha);
  const keyLabel = h('label', 'reveal');
  const cb = h('input');
  cb.type = 'checkbox';
  cb.name = 'key';
  cb.checked = state.key;
  keyLabel.append(cb, document.createTextNode(' Show the answer key'));
  bar.append(items, alphas, keyLabel);
  const out = h('div', 'detector-out');
  host.append(bar, out);
  const draw = () => {
    const o = ai.detector.options.find((x) => x.kind === 'hourly' && String(x.alpha) === state.alpha)!;
    out.replaceChildren(
      tiles([
        { label: `Alerts in June across seven items, at ${oneIn(state.alpha)}`, value: String(o.flags) },
        { label: 'Raised while the shelf was empty', value: `${o.true} of ${o.flags}`, note: 'precision, from the answer key' },
        { label: 'Gaps of three open hours or more found', value: `${o.caught} of ${o.gaps}`, note: 'recall, from the answer key' },
        { label: 'Median open hours from empty shelf to alert', value: hrs(o.median_open_hours_to_flag) },
      ]),
      h('h4', '', `${cap(NAMES[state.item])}, every open hour in June`),
      hoursGrid(state.item, state.alpha, state.key),
      gridLegend(state.key),
      alertsBlock(state.item, state.alpha, state.key),
      h('h4', '', 'Every way of looking for gaps, scored'),
      comparison(state.alpha),
    );
  };
  const wire = (group: HTMLElement, name: 'item' | 'alpha') => {
    group.addEventListener('click', (e) => {
      const b = (e.target as HTMLElement).closest<HTMLButtonElement>('button');
      if (!b) return;
      state[name] = b.dataset[name] as string;
      group.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      draw();
    });
  };
  wire(items, 'item');
  wire(alphas, 'alpha');
  cb.addEventListener('change', () => { state.key = cb.checked; draw(); });
  draw();
};

// ---------- what actually happened ----------
const truth: Panel = (host, s) => {
  context(host, 'world');
  const eps = s.episodes as Episode[];
  const base = ai.forecast.series_5kg.map((x) => x.true);
  const week = (k: number) => base.slice(k * 7, k * 7 + 7).reduce((a, b) => a + b, 0);
  const rec = s.kpis.weekly.recorded_sales['ATTA-WW-5KG'];
  host.append(tiles([
    { label: 'Open hours the 5 kg shelf stood empty in June', value: hrs(s.kpis.empty_open_hours) },
    { label: 'Bags shoppers asked for and could not find', value: num(s.kpis.lost_units), note: `${inr(s.kpis.lost_value_inr)} at the shelf price` },
    { label: 'Shoppers who came for 5 kg atta, 8–14 June', value: num(week(1)), note: `the tills recorded ${num(rec[1])}; ${num(week(0))} came the week before` },
  ]));
  const story = h('div', 'story');
  const say = (t: string, cls = '') => story.append(h('p', cls, t));
  const mis = ev(s, 'misplaced_putaway');
  const ep1 = eps.find((e) => e.causes.includes('misplaced'));
  const ep2 = eps.find((e) => e.causes.includes('wrong_pallet'));
  if (mis && ep1) {
    say(`${when(mis.ts)}: ${mis.units / data.hero.case_units} cases (${mis.units} bags) from the morning truck are put away behind the rice stack, in the wrong bay.`);
    say(`${when(ep1.start)}: the shelf runs out. The books still show ${ep1.book_on_hand_max} bags, above the reorder point of ${ep1.reorder_point[ep1.reorder_point.length - 1]}, so nothing is ordered.`);
    const flag = ev(s, 'gap_flag');
    const check = ev(s, 'gap_check');
    const alert = ev(s, 'low_sales_alert');
    const count = ev(s, 'alert_count');
    if (flag && check && check.ts <= ep1.end) {
      say(`${when(flag.ts)}: the gap detector raises an alert. “${flag.detail}” At ${time(check.ts)} someone checks the bay and the backroom and finds the cases. The shelf was empty for ${hrs(ep1.empty_open_hours)} open hours.`);
    } else if (alert && count && count.ts <= ep1.end) {
      say(`${when(alert.ts)}: the nightly rule flags a day of sales under a quarter of the forecast. The count at ${when(count.ts)} finds the cases. The shelf was empty for ${hrs(ep1.empty_open_hours)} open hours.`);
    } else {
      say(`${when(ep1.end)}: staff restacking the rice find the cases. The shelf was empty for ${hrs(ep1.empty_open_hours)} open hours while the system showed stock.`);
    }
    const r = ep1.responses as Record<string, number>;
    say(`Shoppers asked for ${ep1.lost_units} bags they could not find: ${r.other_brand} bought another brand, ${r.other_pack} took a different pack size, ${r.elsewhere} went elsewhere, ${r.delay} came back later and ${r.skip} left without.`);
  } else {
    say('Every case is scanned into a numbered backroom bin at put-away, so the cases that arrive on 9 June are where the record says, and the refill rounds find them.');
  }
  const caught = ev(s, 'put_away_scan_caught_mismatch');
  if (caught) say(`${when(caught.ts)}: the put-away scan finds 1 kg cases on a line booked as 5 kg, and the receipt is corrected before it can mislead anyone.`);
  else if (ep2) say(`${when(ep2.start)}: the shelf empties again, for ${hrs(ep2.empty_open_hours)} open hours, for a reason that starts at the warehouse. That is the logistics post.`, 'aside');
  host.append(story);

  const chart = h('div');
  host.append(h('h4', '', 'What the books said, what was on the shelf, and what was lost in the backroom'), chart);
  const kinds = ['misplaced_putaway', 'found_in_backroom', 'alert_count', 'gap_check', 'wrong_pallet', 'complaint_count', 'put_away_scan_caught_mismatch'];
  const markers = s.events
    .filter((e) => e.sku === HERO && kinds.includes(e.kind))
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
    tooltip: (j): Tooltip => ({ title: hourOf(j), rows: [
      { label: 'on the books', value: num(s.hourly.book[j]), color: C.record },
      { label: 'on the shelf', value: num(s.hourly.shelf[j]), color: C.reality },
      { label: 'in the wrong bay', value: num(s.hourly.misplaced[j]), color: C.misplaced },
      { label: 'shoppers wanted', value: num(s.hourly.demand[j]) },
    ] }),
  });

  const o = s.kpis.osa;
  const rows: [string, string, string][] = [
    ['On the books', pct(o.system_in_stock), 'open hours with stock on the books'],
    ['Shelf audits', pct(o.shelf_audit), `${o.audits.length} audits, Tuesdays and Fridays at 11:00`],
  ];
  if (s === asIs) rows.push(['Books and tills', pct(ai.availability.books_and_tills), 'open hours with stock on the books, outside the gaps the tills show']);
  rows.push(
    ['On the shelf', pct(o.open_hours_on_shelf), 'open hours with at least one bag on the shelf (answer key)'],
    ['Demand served', pct(o.demand_served), 'bags shoppers wanted that they found (answer key)'],
  );
  const table = h('table', 'four-ways');
  table.append(h('caption', '', `On-shelf availability of 5 kg atta in June, ${rows.length === 5 ? 'five' : 'four'} ways`));
  const tb = h('tbody');
  for (const [label, value, how] of rows) {
    const tr = h('tr');
    const th = h('th', '', label);
    th.scope = 'row';
    tr.append(th, h('td', 'n', value), h('td', 'how', how));
    tb.append(tr);
  }
  table.append(tb);
  host.append(table);
};

const PANELS: Record<string, Panel> = {
  dashboard, tests: testsPanel, forecast: forecastPanel, assistant: assistantPanel, detector: detectorPanel, truth,
};

function renderPersona() {
  const host = root.querySelector('[data-panel]') as HTMLElement;
  host.replaceChildren();
  PANELS[state.persona](host, scn());
  host.setAttribute('aria-labelledby', `tab-${state.persona}`);
}

// ---------- milk ----------
function renderMilk() {
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
    tooltip: (j): Tooltip => ({ title: `Standing order ${signed(data.milk[j].factor - 1)}`, rows: [
      { label: 'thrown away', value: num(data.milk[j].expired), color: C.record },
      { label: 'wanted but not found', value: num(data.milk[j].lost), color: C.reality },
      { label: 'margin after waste', value: inr(data.milk[j].net_inr) },
    ] }),
  });
}

// ---------- records drawer ----------
function renderRecords(which: string, reveal: boolean) {
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
    const counts = Object.fromEntries(asIs.counts.filter((c) => c.sku === HERO).map((c) => [c.count_ts.slice(0, 10), `${c.book_before} → ${c.counted}`]));
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
export function mountRetailDemo(el: HTMLElement) {
  root = el;
  // Deep links: /demo/?persona=forecast&forecast=unconstrained&grounding=domain&detect=gap&routine=scanned&q=why#retail
  const q = new URLSearchParams(location.search);
  for (const [name, values] of Object.entries(LEVERS) as [Lever, string[]][]) {
    const v = q.get(name) ?? (name === 'detect' ? q.get('alert') : null);
    if (v && values.includes(v)) state[name] = v;
  }
  const qid = q.get('q');
  if (qid && QUESTIONS.some((x) => x.id === qid)) state.q = qid;
  const item = q.get('item');
  if (item && ITEMS.includes(item)) state.item = item;
  const alpha = q.get('alpha');
  if (alpha && ALPHAS.includes(alpha)) state.alpha = alpha;

  const radios = [...root.querySelectorAll<HTMLInputElement>('form.controls input[type="radio"]')];
  for (const inp of radios) {
    inp.checked = inp.value === state[inp.name as Lever];
    inp.addEventListener('change', () => {
      if (!inp.checked) return;
      state[inp.name as Lever] = inp.value;
      renderOutcome();
      renderPersona();
    });
  }
  const select = wireTabs(root, (p) => { state.persona = p; renderPersona(); });
  renderOutcome();
  const persona = q.get('persona');
  select(persona && PANELS[persona] ? persona : 'dashboard');

  const slider = root.querySelector<HTMLInputElement>('input[name="milk"]');
  if (slider) slider.value = String(state.milk);
  slider?.addEventListener('input', () => { state.milk = Number(slider.value); renderMilk(); });
  renderMilk();

  let recTab = 'till';
  const reveal = root.querySelector<HTMLInputElement>('input[name="reveal"]');
  root.querySelectorAll<HTMLButtonElement>('[data-rec]').forEach((b) => {
    b.addEventListener('click', () => {
      recTab = b.dataset.rec as string;
      root.querySelectorAll('[data-rec]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      renderRecords(recTab, !!reveal?.checked);
    });
  });
  reveal?.addEventListener('change', () => renderRecords(recTab, reveal.checked));
  renderRecords(recTab, false);

  root.dataset.ready = 'true';
  const click = (sel: string) => root.querySelector<HTMLElement>(sel)?.click();
  (window as unknown as { retailDemo: unknown }).retailDemo = {
    state,
    select,
    set(name: Lever, value: string) {
      const inp = root.querySelector<HTMLInputElement>(`form.controls input[name="${name}"][value="${value}"]`);
      if (inp) { inp.checked = true; inp.dispatchEvent(new Event('change')); }
    },
    ask(id: string) { state.q = id; click(`[data-q="${id}"]`); },
    item(sku: string) { click(`[data-item="${sku}"]`); },
    alpha(a: string) { click(`[data-alpha="${a}"]`); },
    key(on: boolean) {
      const cb = root.querySelector<HTMLInputElement>('input[name="key"]');
      if (cb && cb.checked !== on) { cb.checked = on; cb.dispatchEvent(new Event('change')); }
    },
    milk(i: number) { if (slider) { slider.value = String(i); slider.dispatchEvent(new Event('input')); } },
  };
}
