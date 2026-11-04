// The words and numbers on each post's three images. KPI values and agent rules come from the KPI
// list the site builds (dist/kpis/domain-kpis.yaml, from src/lib/kpis.ts); chart data comes from
// src/data/*.json and the downloadable records in public/data/india-grocery/. Build the site first.
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import yaml from 'js-yaml';
import { C } from './charts.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const data = (f) => JSON.parse(readFileSync(path.join(root, 'src', 'data', f), 'utf8'));
const csv = (f) => {
  const [head, ...rows] = readFileSync(path.join(root, 'public', 'data', 'india-grocery', f), 'utf8').trim().split(/\r?\n/);
  const keys = head.split(',');
  return rows.map((r) => Object.fromEntries(r.split(',').map((v, i) => [keys[i], v])));
};
const yamlFile = path.join(root, 'dist', 'kpis', 'domain-kpis.yaml');
if (!existsSync(yamlFile)) throw new Error('Build the site first (npm run build): cards read dist/kpis/domain-kpis.yaml');
const KPIS = yaml.load(readFileSync(yamlFile, 'utf8')).domains.flatMap((d) => d.kpis);
const kpi = (id) => {
  const i = KPIS.findIndex((k) => k.id === id);
  if (i < 0) throw new Error(`no KPI ${id}`);
  return { ...KPIS[i], n: i + 1 };
};

const ai = data('retail-ai.json');
const retail = data('retail.json');
const logistics = data('logistics.json');
const payments = data('payments.json');
const pai = data('payments-ai.json');
const finale = data('finale.json');
const bench = data('bench.json');
const dbt = data('dbt-kit.json');

const pct = (v) => `${Math.round(Math.abs(v) * 100)}%`;
const signed = (v) => `${v < 0 ? '−' : '+'}${pct(v)}`;
const inr = (v) => `₹${Math.round(v).toLocaleString('en-IN')}`;
const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const dayLabel = (iso) => `${DOW[new Date(`${iso}T12:00:00Z`).getUTCDay()]} ${Number(iso.slice(8))}`;

// ---------- the simulated June: 28 days of 15 open hours, 07:00 to 22:00 ----------
const DAYS = retail.meta.days;
const HOURS = retail.meta.hours;
const asIs = retail.scenarios.find((s) => s.key === 'off|today');
const daily = asIs.daily;
const hourly = asIs.hourly;
const dayIdx = (ts) => DAYS.indexOf(ts.slice(0, 10));
const hourIdx = (ts) => dayIdx(ts) * HOURS.length + (Number(ts.slice(11, 13)) - HOURS[0]) + Number(ts.slice(14, 16)) / 60;
const frac = (ts) => (Number(ts.slice(11, 13)) + Number(ts.slice(14, 16)) / 60 - HOURS[0]) / HOURS.length;
const gap1 = retail.story.episode; // 5 kg atta behind the rice
const gap2 = logistics.story.episode; // the wrong pallet line
const weekTicks = (per = 1) => [0, 7, 14, 21, 27].map((d) => ({ i: d === 27 ? (d + 1) * per - 1 : d * per, label: `${Number(DAYS[d].slice(8))} Jun`, anchor: d === 27 ? 'end' : 'middle' }));
const dayBand = (ep, label, sub) => ({ from: dayIdx(ep.start) + frac(ep.start), to: dayIdx(ep.end) + frac(ep.end), label, sub });

const eyebrowKpi = (k) => `Why Domain Matters · KPI ${k.n} of 18 · ${k.name}`;
const nextOf = (id) => { const k = kpi(id); return `KPI ${k.n}, ${k.name}`; };

/** A KPI post's card: the KPI list supplies the numbers and the rule; the spec adds the rest. */
function kpiCard(id, spec) {
  const k = kpi(id);
  const s14 = k.store_014;
  return {
    eyebrow: eyebrowKpi(k),
    rule: k.agent_rule,
    ...spec,
    reported: { ...s14.reported, ...(spec.reported ?? {}) },
    observed: { ...s14.observed, ...(spec.observed ?? {}) },
    kpi: k,
    reportedRaw: s14.reported,
    observedRaw: s14.observed,
  };
}

// ---------- KPI 1: sales ----------
const s5 = ai.forecast.series_5kg;
const week = (w, key) => s5.slice(w * 7, w * 7 + 7).reduce((a, d) => a + d[key], 0);
const sold = [week(0, 'recorded'), week(1, 'recorded')];
const want = [week(0, 'true'), week(1, 'true')];
const shareStocked = ai.assistant.questions.find((q) => q.id === 'switching').domain.plan[0].result.map((r) => r.share_5kg);
const shareAll = ai.assistant.questions.find((q) => q.id === 'why').naive.plan[2].result[0];

// ---------- KPI 4 and 5: the month-end count ----------
const products = Object.fromEntries(csv('products.csv').map((p) => [p.sku, p]));
const counts = csv('stock-counts-june.csv');
const monthEnd = counts.filter((c) => c.count_ts.startsWith('2026-06-28')).map((c) => ({ sku: c.sku, adj: Number(c.adjustment), book: Number(c.book_before), counted: Number(c.counted) }));
const disagreeing = counts.filter((c) => Number(c.adjustment) !== 0).length;
const shortName = (sku) => products[sku].name.replace('Whole wheat atta', 'Atta').replace('Sona masoori rice', 'Rice').replace(' pouch', '');
const book = csv('inventory-book-june.csv');
const fcBelowZero = book.filter((r) => r.sku === 'MILK-FC-500ML' && Number(r.book_on_hand_close) < 0).length;
const milkCount = (sku) => monthEnd.find((m) => m.sku === sku);

// ---------- KPI 7: days of supply ----------
const lastHour = (d) => d * HOURS.length + HOURS.length - 1;
const dosBooks = daily.book_close.map((b, d) => b / daily.forecast[d]);
const dosFound = daily.book_close.map((_, d) => (hourly.shelf[lastHour(d)] + hourly.backroom[lastHour(d)]) / daily.forecast[d]);

// ---------- KPI 8: milk ----------
const milk = Object.fromEntries(retail.milk.map((m) => [m.factor, m]));
const sellOutDays = (f) => milk[f].daily_lost.filter((x) => x > 0).length;

// ---------- truck ----------
const ls = logistics.story;
const lk = logistics.scenarios.find((s) => s.key === 'none|label').kpis;
const lai = data('logistics-ai.json');
const shipments = csv('shipments-june.csv');
const minute = (ts) => Number(ts.slice(11, 13)) * 60 + Number(ts.slice(14, 16));
const costOf = (sku) => Number(products[sku].cost_inr);
const adj = [
  { v: ls.dc_adjustments[0].value_at_cost_inr, label: ['Warehouse, 1 kg', '23 Jun'] },
  { v: ls.dc_adjustments[1].value_at_cost_inr, label: ['Warehouse, 5 kg', '25 Jun'] },
  { v: ls.corrections[0].adjustment * costOf('ATTA-WW-5KG'), label: ['Store, 5 kg', '26 Jun'] },
  { v: ls.corrections[1].adjustment * costOf('ATTA-WW-1KG'), label: ['Store, 1 kg', '26 Jun'] },
];
const gross = adj.reduce((a, x) => a + Math.abs(x.v), 0);
const net = adj.reduce((a, x) => a + x.v, 0);
const hoursFrom = (ts, t0) => (Date.parse(`${ts}:00Z`) - Date.parse(`${t0}:00Z`)) / 3_600_000;

// ---------- money ----------
const slow = payments.story.slowdown;
const june = payments.story.june;
const byHour = payments.story.slowdown_day_by_hour;
const perCharge = pai.find.per_charge;
const recon = payments.scenarios.find((s) => s.key === 'retry|manual').daily;
const juneDays = DAYS;
const chargesByDay = juneDays.map((d) => perCharge.filter((c) => c.debited_ts.startsWith(d)).length);
const fromComplaint = perCharge.filter((c) => c.refund_days != null && c.complaint_days != null).map((c) => c.refund_days - c.complaint_days);
const fromDebit = perCharge.filter((c) => c.refund_days != null).map((c) => c.refund_days);
const median = (xs) => { const a = [...xs].sort((x, y) => x - y); const m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; };


// ---------- linking and practitioner posts ----------
const scen = (key) => payments.scenarios.find((s) => s.key === key).kpis;
const incident = (id) => finale.incidents.find((i) => i.id === id);
const joinOf = (id) => finale.joins.find((j) => j.id === id);
const chipK = (id, text) => ({ n: `KPI ${kpi(id).n}`, text });
const agentsMean = finale.agents.replenishment.lost_bags_mean;
const linkEyebrow = (i) => `Why Domain Matters · Linking the KPIs · ${i} of 4`;
const SHORT_TESTS = {
  every_upi_attempt_joins_by_rrn: 'UPI attempts join by reference',
  something_checks_each_pallet: 'Something checks each pallet',
  every_provider_success_has_an_approved_payment: 'Every credit has a payment',
  no_bill_paid_twice: 'No bill paid twice',
  counts_agree_with_the_books_within_2pct: 'Counts agree with the books',
  extra_charges_back_within_5_days: 'Extra charges back in 5 days',
  no_silence_with_stock_on_the_books: 'No silence with stock on the books',
};
const domainTests = Object.entries(dbt.domain).sort((a, b) => b[1] - a[1]);

export const CARDS = [
  kpiCard('lfl', {
    slug: 'sales',
    headline: 'An empty shelf looks like falling demand',
    scope: 'Store 014, 5 kg atta, the week of 8 June 2026 against the week before',
    reported: { value: signed(sold[1] / sold[0] - 1), how: `bags sold, ${sold[0]} → ${sold[1]}` },
    observed: { value: signed(want[1] / want[0] - 1), how: `bags shoppers came for, ${want[0]} → ${want[1]}` },
    blind: 'A till records a sale, not a shopper.',
    chart: {
      type: 'pair',
      title: 'The shoppers kept coming. The sales stopped.',
      sub: '5 kg atta at Store 014, 1 to 14 June 2026, bags each day',
      legend: [{ name: 'Bags shoppers came for', color: C.real }, { name: 'Bags sold', color: C.rec }],
      days: s5.slice(0, 14).map((d) => ({ label: dayLabel(d.date), a: d.true, b: d.recorded })),
      bands: [{ from: { i: dayIdx(gap1.start), frac: frac(gap1.start) }, to: { i: dayIdx(gap1.end), frac: frac(gap1.end) }, label: 'Shelf empty', sub: `${gap1.book_on_hand_max} bags on the books` }],
      note: `5 kg share of atta sales while on the shelf: ${pct(shareStocked[0])} → ${pct(shareStocked[1])}. Over all hours: ${pct(shareAll.week1)} → ${pct(shareAll.week2)}.`,
    },
    lesson: 'Sales measure the shelf, not the shopper',
    checks: ['Look for silent hours while the books show stock.', 'Compare the weeks again without those hours.', 'Read the pack mix only when every pack was on the shelf.'],
    next: nextOf('osa'),
  }),

  kpiCard('osa', {
    slug: 'on-shelf-availability',
    headline: 'In stock is not on the shelf',
    scope: 'Store 014, 5 kg atta, open hours in June 2026',
    reported: { how: 'of open hours with stock on the books' },
    observed: { how: 'of open hours with a bag on the shelf' },
    blind: 'Book stock cannot see the shelf.',
    chart: {
      type: 'lines',
      title: 'The books never ran out. The shelf did, twice.',
      sub: '5 kg atta at Store 014, bags at every open hour of June 2026',
      legend: [{ name: 'Bags on the books', color: C.rec }, { name: 'Bags on the shelf', color: C.real }],
      length: hourly.book.length,
      step: 20,
      ticks: weekTicks(HOURS.length),
      bands: [
        { from: hourIdx(gap1.start), to: hourIdx(gap1.end), label: 'Empty', sub: `${gap1.book_on_hand_max} on the books` },
        { from: hourIdx(gap2.start), to: hourIdx(gap2.end), label: 'Empty', sub: `${gap2.book_on_hand_max} on the books` },
      ],
      series: [
        { name: 'books', values: hourly.book, color: C.rec, width: 5 },
        { name: 'shelf', values: hourly.shelf, color: C.real, width: 5 },
      ],
      note: `By the books, available ${kpi('osa').store_014.reported.value} of open hours. On the shelf, ${kpi('osa').store_014.observed.value}.`,
    },
    lesson: 'Availability is a fact about the shelf',
    checks: ['Join every shelf check to the dashboard.', 'Flag long runs with no sales while the books show stock.', 'Walk the shelf before trusting the number.'],
    next: nextOf('lost-sales'),
  }),

  kpiCard('lost-sales', {
    slug: 'lost-sales',
    headline: 'The number no system records',
    scope: 'Store 014, 5 kg atta, June 2026',
    reported: { how: 'lost sales in any report' },
    observed: { how: 'bags shoppers came for and could not find' },
    blind: 'A shopper who leaves leaves no row anywhere.',
    chart: {
      type: 'bars',
      title: `${retail.story.kpis.lost_units} bags lost in June, and not one row in any table`,
      sub: '5 kg atta at Store 014: bags shoppers came for and could not find, each day',
      step: 10,
      ticks: weekTicks(1),
      values: daily.lost.map((v, d) => ({ v, hot: (d >= dayIdx(gap1.start) && d <= dayIdx(gap1.end)) || (d >= dayIdx(gap2.start) && d <= dayIdx(gap2.end)), label: v >= 10 ? String(v) : '' })),
      note: `${inr(retail.story.kpis.lost_value_inr)} of sales on one item in one store, most of it in two gaps.`,
    },
    lesson: 'A loss nobody records is still a loss',
    checks: ['Fill silent hours with the usual sales.', 'Report the estimate with its method.', 'Check it against shelf checks.'],
    next: nextOf('ira'),
  }),

  kpiCard('ira', {
    slug: 'inventory-accuracy',
    headline: 'The books are a belief',
    scope: 'Store 014, the eleven items followed, June 2026',
    observed: { how: '3 of 11 records right at the month-end count' },
    blind: 'Between counts, the book is assumed right.',
    chart: {
      type: 'diverging',
      title: `At the month-end count, ${monthEnd.filter((m) => m.adj !== 0).length} of ${monthEnd.length} records were wrong`,
      sub: 'Store 014, 28 June 2026: units counted minus units on the books',
      labelW: 700,
      rows: [...monthEnd].sort((a, b) => a.adj - b.adj).map((m) => ({ label: shortName(m.sku), v: m.adj })),
      note: `Across June, the books disagreed with ${disagreeing} of the store's ${counts.length} stock counts.`,
    },
    lesson: 'Treat book stock as an estimate',
    checks: ['Test the book against shelf checks between counts.', 'Count when a test fails, not only by the calendar.', 'Record why each difference happened.'],
    next: nextOf('shrink'),
  }),

  kpiCard('shrink', {
    slug: 'shrink',
    headline: 'A correction says the book was wrong, not why',
    scope: 'Store 014, the month-end count, 28 June 2026',
    reported: { value: `${milkCount('MILK-TONED-500ML').adj}`.replace('-', '−'), how: `toned milk pouches (full-cream ${milkCount('MILK-FC-500ML').adj > 0 ? '+' : ''}${milkCount('MILK-FC-500ML').adj})` },
    observed: { value: 'Not theft', how: 'mostly one pouch scanned as the other' },
    blind: 'Theft, damage and scan errors look alike.',
    chart: {
      type: 'diverging',
      title: `One milk lost ${Math.abs(milkCount('MILK-TONED-500ML').adj)} pouches. The other gained ${milkCount('MILK-FC-500ML').adj}.`,
      sub: 'Store 014, the month-end count on 28 June 2026, pouches counted minus the books',
      labelW: 1080,
      rows: [['MILK-TONED-500ML', 'Toned milk'], ['MILK-FC-500ML', 'Full-cream milk']].map(([sku, name]) => { const m = milkCount(sku); return { label: `${name}: books ${m.book}, counted ${m.counted}`, v: m.adj, hot: true }; }),
      note: `The full-cream book went below zero on ${fcBelowZero} days in June: it was selling pouches it did not have.`,
    },
    lesson: 'Look for the mirror image before blaming theft',
    checks: ['Pair a loss with a gain on its sibling.', 'Watch for books that go below zero.', 'Fix the process the pair points to.'],
    next: nextOf('forecast'),
  }),

  kpiCard('forecast', {
    slug: 'forecast-accuracy',
    headline: 'The better forecast can look worse',
    scope: 'Store 014, 5 kg atta, the 28-day average forecast, June 2026',
    reported: { how: 'bias, scored against recorded sales' },
    observed: { how: 'bias, scored against shoppers' },
    blind: 'The target is censored too.',
    chart: {
      type: 'lines',
      title: 'The forecast learnt the empty shelf',
      sub: '5 kg atta at Store 014, bags a day, June 2026',
      legend: [{ name: 'Bags shoppers came for', color: C.real }, { name: 'Bags sold', color: C.rec }, { name: 'Forecast', color: C.ink }],
      length: s5.length,
      step: 10,
      ticks: weekTicks(1),
      bands: [dayBand(gap1, 'Empty'), dayBand(gap2, 'Empty')],
      series: [
        { name: 'came for', values: s5.map((d) => d.true), color: C.real, width: 5 },
        { name: 'sold', values: s5.map((d) => d.recorded), color: C.rec, width: 5 },
        { name: 'forecast', values: s5.map((d) => d.naive), color: C.ink, width: 7, dash: '16 12' },
      ],
      note: `Scored on sales the forecast runs ${kpi('forecast').store_014.reported.value.replace('+', '')} high. Scored on shoppers, ${kpi('forecast').store_014.observed.value.replace('−', '')} low.`,
    },
    lesson: 'Score the forecast on demand, not on sales',
    checks: ['Fill empty hours before scoring.', 'Split bias by weeks with silent runs.', 'Keep the forecast that wins on demand.'],
    next: nextOf('days-of-supply'),
  }),

  kpiCard('days-of-supply', {
    slug: 'days-of-supply',
    headline: '2.3 days on the books, none on the shelf',
    scope: 'Store 014, 5 kg atta, mid-June 2026',
    blind: 'Phantom stock counts as supply.',
    chart: {
      type: 'lines',
      title: 'Days of supply on the books, and days staff could find',
      sub: '5 kg atta at Store 014: stock at closing divided by the store\'s forecast, June 2026',
      legend: [{ name: 'On the books', color: C.rec }, { name: 'Stock staff could find', color: C.real }],
      length: dosBooks.length,
      step: 1,
      ticks: weekTicks(1),
      bands: [dayBand(gap1, 'Empty'), dayBand(gap2, 'Empty')],
      series: [
        { name: 'books', values: dosBooks, color: C.rec, width: 6 },
        { name: 'found', values: dosFound, color: C.real, width: 6 },
      ],
      note: `With ${gap1.book_on_hand_max} bags on the books, above the reorder point of 40, the store ordered nothing.`,
    },
    lesson: 'Days of supply is only as good as the stock under it',
    checks: ['Recompute on stock someone has seen.', 'Treat a silent item’s supply as unknown.', 'Walk shelves with a week of supply and no sales.'],
    next: nextOf('fresh-waste'),
  }),

  kpiCard('fresh-waste', {
    slug: 'fresh-waste',
    headline: 'Cutting the order always looks free',
    scope: 'Store 014, toned milk, a standing order 5% leaner than today’s, June 2026',
    reported: { how: `margin after waste, up from ${inr(milk[1].net_inr)}` },
    observed: { value: String(milk[0.95].lost), how: `pouches not found, up from ${milk[1].lost}` },
    blind: 'Demand above the sell-out is never recorded.',
    chart: {
      type: 'hbars',
      title: 'The waste report improves. The empty shelves double.',
      sub: 'Toned milk at Store 014, June 2026: today’s standing order against one 5% leaner',
      labelW: 980,
      rows: [
        { label: 'Margin after waste, today', v: milk[1].net_inr, max: milk[0.95].net_inr * 1.15, kind: 'grey', text: inr(milk[1].net_inr) },
        { label: 'Margin after waste, 5% leaner', v: milk[0.95].net_inr, max: milk[0.95].net_inr * 1.15, kind: 'rec', text: inr(milk[0.95].net_inr) },
        { label: 'Pouches not found, today', v: milk[1].lost, max: milk[0.95].lost * 1.15, kind: 'grey', text: String(milk[1].lost) },
        { label: 'Pouches not found, 5% leaner', v: milk[0.95].lost, max: milk[0.95].lost * 1.15, kind: 'real', text: String(milk[0.95].lost) },
      ],
      note: `With the leaner order the milk sells out on ${sellOutDays(0.95)} days instead of ${sellOutDays(1)}.`,
    },
    lesson: 'Put waste and empty shelves in one table',
    checks: ['Record the time of each day’s last sale.', 'Estimate demand after the sell-out.', 'Choose the order on both numbers.'],
    next: nextOf('pick-accuracy'),
  }),

  kpiCard('pick-accuracy', {
    slug: 'pick-accuracy',
    headline: 'A slot scan confirms the place, not the product',
    scope: 'Store 014’s warehouse, June 2026',
    reported: { how: 'of June’s picks confirmed by slot scan' },
    observed: { how: `${ls.actual.units_actual} packs of 1 kg sent as ${ls.line.units} bags of 5 kg` },
    blind: 'The scan confirmed where the picker stood.',
    chart: {
      type: 'events',
      title: 'One mis-pick, seen twice, never joined',
      sub: 'The warehouse and Store 014, 22 to 26 June 2026',
      from: 0,
      to: hoursFrom('2026-06-26T12:00', '2026-06-22T00:00'),
      ticks: ['2026-06-22', '2026-06-23', '2026-06-24', '2026-06-25', '2026-06-26'].map((d) => ({ v: hoursFrom(`${d}T00:00`, '2026-06-22T00:00'), label: `${Number(d.slice(8))} Jun` })),
      events: [
        { v: hoursFrom(ls.picks[0].pick_ts, '2026-06-22T00:00'), up: true, hot: true, anchor: 'start', lines: [`${ls.picks[0].pick_ts.slice(11)} pick confirmed`, 'wrong slot, right label'] },
        { v: hoursFrom(ls.shipment.arrived_ts, '2026-06-22T00:00'), up: false, anchor: 'start', lines: [`${ls.shipment.arrived_ts.slice(11)} truck on time`, 'notice says 5 kg'] },
        { v: hoursFrom(ls.dc_adjustments[0].adjusted_ts, '2026-06-22T00:00'), up: true, anchor: 'start', lines: ['1 kg slot −16 cases', 'booked as a short pick'] },
        { v: hoursFrom(ls.dc_adjustments[1].adjusted_ts, '2026-06-22T00:00'), up: false, lines: ['5 kg slot +16 cases', 'booked as a count variance'] },
        { v: hoursFrom(ls.corrections[0].count_ts, '2026-06-22T00:00'), up: true, anchor: 'end', lines: ['Store count', `${Math.abs(ls.corrections[0].adjustment)} bags of 5 kg missing`] },
      ],
      note: 'The −16 and the +16 in neighboring slots are mirror images of one mis-pick.',
    },
    lesson: 'Scan the product, not the place',
    checks: ['Scan each case’s barcode at pick.', 'Pair mirror-image slot corrections.', 'Follow the pair back to the pick.'],
    next: nextOf('fill-rate'),
  }),

  kpiCard('fill-rate', {
    slug: 'fill-rate',
    headline: 'The right quantity of the wrong item',
    scope: `Store 014’s June orders from the warehouse, ${lai.fill.ordered} cases`,
    reported: { how: 'of ordered cases shipped, by the notices' },
    observed: { how: 'counting only cases of the right item' },
    blind: 'The notice counted cases, not what was in them.',
    chart: {
      type: 'hbars',
      title: 'The notice counted cases. It could not see inside them.',
      sub: `Store 014’s June orders: ${lai.fill.ordered} cases ordered (axis from 95%)`,
      labelW: 900,
      min: 95,
      max: 100,
      rows: [
        { label: `By the notices: ${lai.fill.shipped} of ${lai.fill.ordered}`, v: lai.fill.by_notice * 100, kind: 'rec', text: `${(lai.fill.by_notice * 100).toFixed(1)}%` },
        { label: `The right item: ${lai.fill.shipped - lai.fill.wrong_item_cases} of ${lai.fill.ordered}`, v: lai.fill.right_item * 100, kind: 'real', text: `${(lai.fill.right_item * 100).toFixed(1)}%` },
      ],
      note: `${lai.fill.wrong_item_cases} cases on the 22 June line held 1 kg packs instead of 5 kg bags.`,
    },
    lesson: 'A filled line is not a right line',
    checks: ['Scan the case, not the slot.', 'Weigh the pallet against the notice.', 'Compute fill rate by the item.'],
    next: nextOf('on-time'),
  }),

  kpiCard('on-time', {
    slug: 'on-time-arrival',
    headline: 'A punctual truck with the wrong pallet',
    scope: 'Store 014, deliveries from the warehouse, June 2026',
    blind: 'Arrival time says nothing about the pallet.',
    chart: {
      type: 'dots',
      title: `${lk.in_slot} of ${lk.shipments} trucks on time, one with the wrong pallet`,
      sub: 'Arrival times at Store 014, each delivery in June 2026',
      days: DAYS.length,
      min: 5 * 60 + 50,
      max: 8 * 60 + 35,
      band: { from: 6 * 60, to: 6 * 60 + 30, label: 'Delivery slot' },
      yTicks: [{ v: 360, label: '06:00' }, { v: 390, label: '06:30' }, { v: 420, label: '07:00' }, { v: 450, label: '07:30' }, { v: 480, label: '08:00' }, { v: 510, label: '08:30' }],
      ticks: weekTicks(1),
      points: shipments.map((s) => ({ i: dayIdx(s.arrived_ts), m: minute(s.arrived_ts), hot: s.shipment_id === ls.shipment.shipment_id, label: s.shipment_id === ls.shipment.shipment_id ? `${ls.shipment.arrived_ts.slice(11)}, the wrong pallet` : minute(s.arrived_ts) > 390 ? `late, ${s.arrived_ts.slice(11)}` : '', labelDy: s.shipment_id === ls.shipment.shipment_id ? -170 : -40 })),
    },
    lesson: 'On time is half a delivery',
    checks: ['Judge arrival with what was on the pallet.', 'Measure when stock reaches the shelf.', 'Rank suppliers on both.'],
    next: nextOf('otif'),
  }),

  kpiCard('otif', {
    slug: 'otif',
    headline: 'In full means the label said so',
    scope: `Store 014, ${lk.shipments} deliveries from the warehouse, June 2026`,
    blind: 'A shipping notice cannot see inside a pallet.',
    chart: {
      type: 'hbars',
      title: 'OTIF four ways. Only one looked inside the pallets.',
      sub: `Store 014’s ${lk.shipments} deliveries from the warehouse, June 2026`,
      labelW: 760,
      max: 100,
      rows: [
        { label: 'Warehouse report', v: lk.otif.dc_report * 100, kind: 'rec', text: pct(lk.otif.dc_report) },
        { label: 'By order line', v: lk.otif.by_line * 100, kind: 'rec', text: pct(lk.otif.by_line) },
        { label: 'Store scorecard', v: lk.otif.scorecard * 100, kind: 'rec', text: pct(lk.otif.scorecard) },
        { label: 'Every case right', v: lk.otif.at_the_shelf * 100, kind: 'real', text: pct(lk.otif.at_the_shelf) },
      ],
      note: 'The first three judge “in full” from records copied from the pick.',
    },
    lesson: 'Ask how “in full” was checked',
    checks: ['Scan cases at receipt.', 'Compare receipts with the next count.', 'Keep one record the pick did not write.'],
    next: nextOf('net-adjustments'),
  }),

  kpiCard('net-adjustments', {
    slug: 'net-adjustments',
    headline: 'Four corrections, one mistake',
    scope: 'Atta corrections at cost, the warehouse and Store 014, June 2026',
    observed: { value: inr(gross), how: 'the same four corrections, gross' },
    blind: 'Offsetting errors cancel.',
    chart: {
      type: 'waterfall',
      title: `${inr(gross)} of corrections net to ${inr(net)}`,
      sub: 'Four atta corrections at cost in two buildings, 23 to 26 June 2026',
      steps: adj.map((a) => ({ v: a.v, text: `${a.v < 0 ? '−' : '+'}${inr(Math.abs(a.v))}`, label: a.label })),
      netText: inr(net),
      netLabel: ['Net', 'June'],
      note: 'One mis-pick caused all four, and each building closed its own two.',
    },
    lesson: 'A small net can hide a large mistake',
    checks: ['Report gross beside net.', 'Pair corrections across items.', 'Pair them across buildings.'],
    next: nextOf('success-rate'),
  }),

  kpiCard('success-rate', {
    slug: 'payment-success',
    headline: 'Failed at the till, paid at the bank',
    scope: 'Store 014, UPI at the tills, Saturday 20 June 2026, 18:20 to 19:50',
    blind: 'A till cannot see the customer’s bank.',
    chart: {
      type: 'hbars',
      title: 'Same 90 minutes, four success rates',
      sub: 'UPI at Store 014’s tills, Saturday 20 June 2026, 18:20 to 19:50',
      labelW: 860,
      max: 100,
      rows: [
        { label: 'Approved at the till', v: slow.four_ways.till * 100, kind: 'rec', text: pct(slow.four_ways.till) },
        { label: 'Credited at the bank', v: slow.four_ways.bank * 100, kind: 'real', text: pct(slow.four_ways.bank) },
        { label: 'Customers charged once', v: slow.four_ways.charged_once * 100, kind: 'grey', text: pct(slow.four_ways.charged_once) },
        { label: 'Bills paid', v: slow.four_ways.bills_paid * 100, kind: 'grey', text: pct(slow.four_ways.bills_paid) },
      ],
      note: `Over all of June the till and the bank agree within a point: ${(june.four_ways.till * 100).toFixed(1)}% and ${(june.four_ways.bank * 100).toFixed(1)}%.`,
    },
    lesson: 'A timeout is a question, not a failure',
    checks: ['Match each timeout to the final status.', 'Wait for the status check before asking again.', 'Count late credits as paid.'],
    next: nextOf('technical-declines'),
  }),

  kpiCard('technical-declines', {
    slug: 'technical-declines',
    headline: 'A good month can hide a bad hour',
    scope: 'Store 014, UPI attempts, June 2026',
    blind: 'Averages hide bursts, and timeouts are not counted.',
    chart: {
      type: 'bars',
      title: `A month at ${kpi('technical-declines').store_014.reported.value}, an evening at a quarter`,
      sub: 'UPI attempts with no answer within 30 seconds, Store 014, Saturday 20 June 2026, by hour',
      step: 10,
      ticks: byHour.filter((h) => h.hour % 2 === 1).map((h) => ({ i: byHour.indexOf(h), label: `${String(h.hour).padStart(2, '0')}:00` })),
      values: byHour.map((h) => { const v = (100 * h.no_response) / h.upi_attempts; return { v, hot: v > 10, label: v > 10 ? `${Math.round(v)}%` : '' }; }),
      note: `None of the ${slow.upi_timeouts} timeouts in the slowdown counts as a technical decline.`,
    },
    lesson: 'Read the rate by the hour',
    checks: ['Count timeouts as failures.', 'Watch the worst hour, not the month.', 'Track the switch’s response time.'],
    next: nextOf('charged-twice'),
  }),

  kpiCard('charged-twice', {
    slug: 'charged-twice',
    headline: 'No report has a column for them',
    scope: 'Store 014, all June bills, 2026',
    observed: { value: String(june.charged_twice), how: `customers, ${june.extra_charges} extra charges, ${inr(june.charged_twice_inr)}` },
    blind: 'A timed-out payment has no reference to join on.',
    chart: {
      type: 'bars',
      title: `${june.charged_twice} customers paid twice. No report counted one.`,
      sub: 'Extra charges at Store 014 by the day of the debit, June 2026',
      step: 5,
      ticks: weekTicks(1),
      values: chargesByDay.map((v, d) => ({ v, hot: DAYS[d] === '2026-06-20', label: v >= 3 ? String(v) : '' })),
      note: `${slow.charged_twice} of the ${june.charged_twice} paid twice in 90 minutes on Saturday 20 June.`,
    },
    lesson: 'Zero in the records is not zero',
    checks: ['Match timeouts to the provider by amount and time.', 'Look for bills paid again.', 'Run it every morning.'],
    next: nextOf('match-rate'),
  }),

  kpiCard('match-rate', {
    slug: 'match-rate',
    headline: 'The unmatched pile is where the customers are',
    scope: 'Store 014, UPI credits, 20 and 21 June 2026',
    observed: { value: String(slow.charged_twice), how: `customers owed ${inr(slow.charged_twice_inr)} for ${slow.extra_charges} extra charges` },
    blind: 'The missing key makes a match impossible.',
    chart: {
      type: 'bars',
      title: 'The suspense pile spiked the night the switch slowed',
      sub: 'UPI credits with no approved payment behind them, Store 014, each day of June 2026',
      step: 5,
      ticks: weekTicks(1),
      values: recon.map((d) => ({ v: d.unmatched, hot: d.unmatched > 0, label: d.unmatched > 0 ? String(d.unmatched) : '' })),
      note: `The ${slow.extra_charges} on 20 and 21 June were extra charges on customers who had already paid again.`,
    },
    lesson: 'Unmatched credits are customers’ money',
    checks: ['Match on amount and time when the key is missing.', 'Put the bill ID on every request.', 'Age every item in suspense.'],
    next: nextOf('refund-tat'),
  }),

  kpiCard('refund-tat', {
    slug: 'refund-turnaround',
    headline: 'Start the clock at the debit',
    scope: 'Store 014, refunds of extra charges, June 2026',
    observed: { how: 'median, from the extra debit' },
    blind: 'The clock started at the complaint.',
    chart: {
      type: 'strip',
      title: `Support measured ${median(fromComplaint)} days. Customers waited ${median(fromDebit).toFixed(1)}.`,
      sub: 'Days to a refund for each extra charge at Store 014, June 2026',
      max: 8,
      step: 1,
      labelW: 600,
      yard: { v: 5, label: 'RBI’s five days' },
      rows: [
        { label: 'From the complaint', sub: `median ${median(fromComplaint)} days`, values: fromComplaint, kind: 'rec', median: median(fromComplaint) },
        { label: 'From the debit', sub: `median ${median(fromDebit).toFixed(1)} days`, values: fromDebit, kind: 'real', median: median(fromDebit) },
      ],
      note: `${pai.find.not_refunded} extra charges were still unrefunded when June closed. ${pai.find.never_complained} of those customers never complained.`,
    },
    lesson: 'Measure the wait from the customer’s side',
    checks: ['Start the clock at the debit.', 'Count refunds made without a complaint.', 'Find extra charges before customers do.'],
    next: 'Linking the KPIs',
  }),
  {
    slug: 'retail',
    eyebrow: linkEyebrow(1),
    headline: 'One empty shelf moved six KPIs',
    scope: 'Store 014, 5 kg atta, 9 to 15 June 2026',
    chips: [chipK('lfl', `Sales ${signed(sold[1] / sold[0] - 1)}`), chipK('osa', `Availability ${kpi('osa').store_014.reported.value}`), chipK('lost-sales', 'Lost sales 0'), chipK('ira', 'Inventory accuracy 100%'), chipK('forecast', 'Forecast eased'), chipK('days-of-supply', `Days of supply ${kpi('days-of-supply').store_014.reported.value}`)],
    blind: 'Six desks, six numbers, one cause.',
    chart: {
      type: 'events',
      title: 'One week, and the answer was in the store’s own records',
      sub: '5 kg atta at Store 014, 9 to 15 June 2026',
      from: 0,
      to: hoursFrom('2026-06-15T12:00', '2026-06-09T00:00'),
      ticks: ['2026-06-09', '2026-06-10', '2026-06-11', '2026-06-12', '2026-06-13', '2026-06-14', '2026-06-15'].map((d) => ({ v: hoursFrom(`${d}T00:00`, '2026-06-09T00:00'), label: `${Number(d.slice(8))} Jun` })),
      events: [
        { v: hoursFrom(retail.story.misplaced.ts, '2026-06-09T00:00'), up: true, hot: true, anchor: 'start', lines: [`${retail.story.misplaced.ts.slice(11)} cases put away`, 'behind the rice'] },
        { v: hoursFrom(gap1.start, '2026-06-09T00:00'), up: false, anchor: 'start', lines: [`${gap1.start.slice(11)} shelf empty`, `${gap1.book_on_hand_max} bags on the books`] },
        { v: hoursFrom('2026-06-12T11:00', '2026-06-09T00:00'), up: true, lines: ['11:00 shelf check: empty', `${gap1.book_on_hand_min} on the books, joined to nothing`] },
        { v: hoursFrom(gap1.end, '2026-06-09T00:00'), up: false, lines: [`${gap1.end.slice(11)} cases found`, `${gap1.lost_units} bags not sold`] },
        { v: hoursFrom('2026-06-15T09:00', '2026-06-09T00:00'), up: true, anchor: 'end', lines: ['Monday review', `sales ${signed(sold[1] / sold[0] - 1)}`] },
      ],
      note: `The tills went silent on 5 kg atta by ${incident('shelf').joined.ts.slice(11)} on Wednesday, three open hours after the shelf emptied.`,
    },
    lesson: 'The shelf was assumed, not measured',
    ruleLabel: 'What one rule did',
    rule: `Across forty simulated Junes, an agent told that in stock means on the shelf lost ${Math.round(agentsMean.domain)} bags instead of ${Math.round(agentsMean.naive)}, with no extra stock.`,
    checkLabel: 'Do this',
    checks: ['Join every shelf check to the dashboard.', 'Listen to the tills for silent hours.', 'Give your agent the rule.'],
    next: 'Linking 2 of 4, the truck',
  },
  {
    slug: 'logistics',
    eyebrow: linkEyebrow(2),
    headline: 'On time, in full, and wrong',
    scope: 'Store 014 and its warehouse, 22 to 26 June 2026',
    chips: [chipK('pick-accuracy', 'Pick accuracy 100%'), chipK('fill-rate', `Fill rate ${kpi('fill-rate').store_014.reported.value}`), chipK('on-time', `On time ${lk.in_slot} of ${lk.shipments}`), chipK('otif', `OTIF ${kpi('otif').store_014.reported.value}`), chipK('net-adjustments', `Net adjustments ${inr(net)}`)],
    blind: 'Every record agreed, because each copied the one before.',
    chart: {
      type: 'hbars',
      title: 'Every shipping record agreed. Only the count did not.',
      sub: 'Pairs of Store 014’s June records, and how often they agree',
      labelW: 980,
      max: 100,
      rows: [
        ['picks-notice', 'Picks and the notice', 'rec'],
        ['notice-labels', 'Notice and pallet labels', 'rec'],
        ['notice-receipts', 'Notice and receipts', 'rec'],
        ['receipts-counts', 'Receipts and the next count', 'real'],
      ].map(([id, label, kind]) => { const j = joinOf(id); return { label, v: (100 * j.agree) / j.compared, kind, text: `${j.agree} of ${j.compared}` }; }),
      note: 'The first three are copies of the pick. Only the count looks at what was on the pallet.',
    },
    lesson: 'Agreement between copies proves nothing',
    ruleLabel: 'The trace',
    rule: `Joining the store’s silence to the warehouse’s records names the pallet line ${finale.trace.hours_before_pair} hours before the warehouse’s own pair and ${finale.trace.hours_before_count} before the store’s count.`,
    checkLabel: 'Do this',
    checks: ['Scan cases or weigh pallets.', 'Pair corrections across buildings.', 'Follow a silent item back to its pick.'],
    next: 'Linking 3 of 4, the money',
  },
  {
    slug: 'payments',
    eyebrow: linkEyebrow(3),
    headline: 'Failed, but paid',
    scope: 'Store 014, UPI at the tills, Saturday 20 June 2026, 18:20 to 19:50',
    chips: [chipK('success-rate', `Success ${pct(slow.four_ways.till)}`), chipK('technical-declines', `Technical declines ${kpi('technical-declines').store_014.reported.value}`), chipK('charged-twice', 'Double debits 0'), chipK('match-rate', `Suspense ${slow.extra_charges} items`), chipK('refund-tat', `Refunds ${kpi('refund-tat').store_014.reported.value}`)],
    blind: `Five healthy-looking numbers, ${slow.charged_twice} customers charged twice.`,
    chart: {
      type: 'pair',
      title: 'At 18:00 and 19:00 the bank received more than the till approved',
      sub: 'UPI at Store 014, Saturday 20 June 2026, payments each hour',
      legend: [{ name: 'Credited at the bank', color: C.real }, { name: 'Approved at the till', color: C.rec }],
      step: 10,
      days: byHour.map((h) => ({ label: String(h.hour).padStart(2, '0'), a: h.credited, b: h.approved_at_till })),
      bands: [{ from: { i: 11, frac: 20 / 60 }, to: { i: 12, frac: 50 / 60 }, label: 'Slowdown' }],
      note: `Cashiers asked for another payment ${slow.second_payments} times, and ${slow.charged_twice} customers paid twice.`,
    },
    lesson: 'The bank had the final word',
    ruleLabel: 'Two small changes',
    rule: `Waiting for the 90-second status check cuts double charges from ${june.charged_twice} customers to ${scen('check|manual').june.charged_twice}. A bill ID on every request cuts the median refund wait from ${scen('retry|manual').refunds.median_days_to_refund} days to ${scen('retry|bill_ref').refunds.median_days_to_refund}.`,
    checkLabel: 'Do this',
    checks: ['Match timeouts to the provider every morning.', 'Put a key on every request.', 'Start the refund clock at the debit.'],
    next: 'Linking 4 of 4, who saw what',
  },
  {
    slug: 'who-saw-what',
    eyebrow: linkEyebrow(4),
    headline: 'Who saw what: eighteen KPIs on one map',
    scope: 'Store 014, June 2026, three incidents',
    chips: [{ text: '5 kg atta in the wrong bay' }, { text: '1 kg packs on a 5 kg line' }, { text: 'Customers charged twice' }],
    blind: 'The headline KPIs read copies.',
    chart: {
      type: 'hbars',
      title: 'Hours by joining, days by waiting',
      sub: 'How long each June failure took to find at Store 014',
      labelW: 1000,
      max: 70,
      rows: [
        { label: 'Empty shelf, by joining', v: incident('shelf').hours_joined, kind: 'real', text: `${incident('shelf').hours_joined} h` },
        { label: 'Empty shelf, by waiting', v: incident('shelf').hours_found, kind: 'grey', text: `${Math.round(incident('shelf').hours_found)} h` },
        { label: 'Wrong pallet, by joining', v: incident('truck').hours_joined, kind: 'real', text: `${incident('truck').hours_joined} h` },
        { label: 'Wrong pallet, by waiting', v: incident('truck').hours_found, kind: 'grey', text: `${Math.round(incident('truck').hours_found)} h` },
        { label: 'Double debit, by joining', v: incident('money').hours_joined, kind: 'real', text: `${Math.round(incident('money').hours_joined)} h, median` },
        { label: 'Double debit, by waiting', v: incident('money').hours_found, kind: 'grey', text: `${Math.round(incident('money').hours_found)} h, median` },
      ],
      note: 'Joining two of the store’s own records found each failure in hours. Waiting took days.',
    },
    lesson: 'Give your agent the map',
    ruleLabel: 'On the Store 014 Bench',
    rule: `A scripted assistant answers ${bench.baselines['schema-only'].right} of ${bench.baselines['schema-only'].of} questions from the schema, ${bench.baselines['domain-layers'].right} with each domain’s rules and ${bench.baselines.map.right} with the map.`,
    checkLabel: 'Do this',
    checks: ['List which records are copies.', 'Join the ones that look at the world.', 'Give the agent what each record can see.'],
    footLeft: 'The end of the series. Thank you for reading.',
  },
];
