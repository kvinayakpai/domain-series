// Logistics demo: one truck, one wrong pallet line, six ways of looking at the same delivery.
import data from '../data/logistics.json';
import { barChart, lineChart, tableView, type Tooltip } from './charts';
import { bands, day, h, inr, num, pct, plus, recordBlock, recordsTable, says, smallTable, tiles, time, when, wireTabs } from './demo-kit';

type Data = typeof data;
type Scn = Data['scenarios'][number];

const C = { record: 'var(--c-record)', reality: 'var(--c-reality)', misplaced: 'var(--c-misplaced)' };
const HOURS = data.meta.hours as number[];
const DAYS = data.meta.days as string[];
const NH = HOURS.length;
const HERO = data.hero.sku;
const ONE = data.one_kg.sku;
const NAMES: Record<string, string> = {
  'ATTA-WW-5KG': 'Atta 5 kg', 'ATTA-WW-1KG': 'Atta 1 kg', 'ATTA-WW-10KG': 'Atta 10 kg', 'RICE-SM-5KG': 'Rice 5 kg',
  'DAL-TOOR-1KG': 'Toor dal 1 kg', 'OIL-SUN-1L': 'Oil 1 L', 'SUGAR-1KG': 'Sugar 1 kg',
};
const name = (sku: string) => NAMES[sku] ?? sku;
const COST = data.costs as Record<string, number>;
const CASE_KG = data.case_kg as Record<string, number>;
const SLOT = data.slots as Record<string, string>;
const short = (sscc: string) => `…${sscc.slice(-4)}`;
const hrs = (x: number) => (x === 0 ? '0' : x < 1 ? 'under 1' : x.toFixed(1).replace(/\.0$/, ''));
const dd = (iso: string) => new Date(`${iso.slice(0, 10)}T12:00:00+05:30`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', timeZone: 'Asia/Kolkata' });
const hourLabel = (i: number) => `${day(DAYS[Math.floor(i / NH)])}, ${String(HOURS[i % NH]).padStart(2, '0')}:00`;
const idxOf = (iso: string) => DAYS.indexOf(iso.slice(0, 10)) * NH + Math.min(NH - 1, Math.max(0, Number(iso.slice(11, 13)) - HOURS[0]));
const twoDayTick = (i: number) => (i % (2 * NH) === 0 ? dd(DAYS[i / NH]) : null);
const clock = (hoursAfterSix: number) => {
  const m = Math.round(hoursAfterSix * 60) + 360;
  return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
};

// ---------- state ----------
const state = { dc: 'none', receiving: 'label', persona: 'dc' };
const scn = () => data.scenarios.find((s) => s.key === `${state.dc}|${state.receiving}`) as Scn;
const asIs = data.scenarios.find((s) => s.key === 'none|label') as Scn;
const ev = (s: Scn, kind: string) => s.events.find((e) => e.kind === kind);
// How much lighter the pallet is with 1 kg bales on the 5 kg line.
const lightKg = (s: Scn) => (s.picks.find((p) => p.sku === HERO)?.cases_confirmed ?? 0) * (CASE_KG[HERO] - CASE_KG[ONE]);
const row22 = (s: Scn) => s.by_shipment.find((r) => r.shipment_id === s.shipment.shipment_id)!;

function weeks(s: Scn) {
  const starts = ['2026-06-01', '2026-06-08', '2026-06-15', '2026-06-22'];
  return starts.map((a, k) => {
    const b = k < 3 ? starts[k + 1] : '2026-06-29';
    const rows = s.by_shipment.filter((r) => r.arrived_ts >= a && r.arrived_ts < b);
    return { label: dd(a), n: rows.length, slot: rows.filter((r) => r.in_slot).length,
      full: rows.filter((r) => r.in_full_receipt).length, good: rows.filter((r) => r.scorecard).length,
      shelf: rows.filter((r) => r.at_the_shelf).length };
  });
}

// ---------- outcome strip ----------
function renderOutcome(root: HTMLElement) {
  const s = scn();
  const k = s.kpis;
  (root.querySelector('[data-outcome]') as HTMLElement).replaceChildren(tiles([
    { label: 'OTIF on the scorecard for June', value: pct(k.otif.scorecard),
      note: `${pct(k.otif.at_the_shelf)} counting what was really on the pallets` },
    { label: 'Open hours the 5 kg shelf stood empty, 22–28 June', value: hrs(k.empty_open_hours_after),
      note: s === asIs ? 'the chain as it runs today' : `${hrs(asIs.kpis.empty_open_hours_after)} as it runs today` },
    { label: 'Bags of 5 kg customers could not buy, 22–28 June', value: num(k.lost_units_after),
      note: `${inr(k.lost_value_after_inr)} at the shelf price` },
  ]));
}

// ---------- personas ----------
type Panel = (host: HTMLElement, s: Scn) => void;

const dc: Panel = (host, s) => {
  host.append(recordBlock([
    `Pick confirmations, order ${s.picks[0].order_id}, Store 014`,
    'Time  Slot     Item        Cases  Scanned',
    ...s.picks.map((p) => `${time(p.pick_ts)} ${p.slot}  ${name(p.sku).padEnd(11)} ${String(p.cases_confirmed).padStart(5)}  ${p.confirmed_by.replace(' scan', '').replace('case barcode', 'each case')}`),
  ], `What the warehouse system recorded for the truck to Store 014 on ${day(s.shipment.arrived_ts)}.`));
  const lines = s.by_shipment.reduce((a, r) => a + r.lines, 0);
  const onSchedule = s.by_shipment.filter((r) => r.dispatched_on_time).length;
  const claim = s.claims[0];
  const caught = ev(s, 'pick_scan_caught_wrong_item') ?? ev(s, 'check_weigh_caught_wrong_item');
  host.append(tiles([
    { label: 'Order lines picked for Store 014 in June', value: num(lines) },
    { label: 'Picking errors on record', value: claim ? '1' : '0',
      note: claim ? `reported by the store, ${when(claim.claim_ts)}` : caught ? 'one caught before the truck left' : 'none reported' },
    { label: 'Deliveries dispatched on schedule', value: `${onSchedule} of ${s.by_shipment.length}` },
  ]));
  const weigh = ev(s, 'check_weigh_caught_wrong_item');
  const quote = ev(s, 'pick_scan_caught_wrong_item')
    ? '“The scanner rejected a 1 kg bale on the 5 kg line at three in the morning, and the picker took the right cases. Nothing to report.”'
    : weigh
      ? `“The scale flagged a pallet ${Math.round(lightKg(s))} kg light. We re-picked the 5 kg line, and the truck left ${data.check_weigh.repick_minutes} minutes late.”`
      : claim
        ? '“Store 014 reported 1 kg bales on a 5 kg line. We counted both slots, corrected them, and had a word with the picker.”'
        : '“Every line on that truck was picked and confirmed. The atta bay had two count variances this week, and both are corrected.”';
  host.append(says(quote));
  if (s.dc_adjustments.length) {
    host.append(smallTable('ledger', 'Stock corrections in the atta bay, 22 to 28 June', ['When', 'Slot', 'Item', 'Cases', 'Reason'],
      s.dc_adjustments.map((a) => [when(a.adjusted_ts), a.slot, name(a.sku), plus(a.cases), a.reason])));
  } else {
    host.append(h('p', 'muted', 'No stock corrections in the atta bay between 22 and 28 June.'));
  }
};

const transport: Panel = (host, s) => {
  const sh = s.shipment;
  const r = row22(s);
  host.append(recordBlock([
    `Trip log, ${sh.vehicle}, ${day(sh.arrived_ts)}`,
    `Left the DC      ${time(sh.dispatched_ts)}`,
    `Delivery slot    ${time(sh.slot_start)}–${time(sh.slot_end)}`,
    `Arrived          ${time(sh.arrived_ts)}`,
    `Status           ${r.in_slot ? 'on time' : 'late'}`,
  ], 'What the transport system logs for the truck: times, nothing about what it carried.'));
  const late = s.by_shipment.filter((x) => !x.in_slot);
  host.append(tiles([
    { label: 'Deliveries in the 06:00–06:30 slot in June', value: `${s.kpis.in_slot} of ${s.kpis.shipments}`, note: pct(s.kpis.in_slot / s.kpis.shipments) },
    { label: 'Late arrivals', value: String(late.length), note: late.map((x) => `${dd(x.arrived_ts)} at ${time(x.arrived_ts)}`).join('; ') },
    { label: `${dd(sh.arrived_ts)} delivery`, value: r.in_slot ? 'On time' : 'Late', note: `arrived ${time(sh.arrived_ts)}` },
  ]));
  host.append(says(r.in_slot
    ? `“${sh.vehicle} made its slot on 22 June. ${late.length} late mornings this month.”`
    : `“The DC held ${sh.vehicle} for ${data.check_weigh.repick_minutes} minutes on 22 June, so it reached the store at ${time(sh.arrived_ts)}. That’s a late delivery on my report.”`));
  const chart = h('div');
  host.append(h('h4', '', 'When the truck reached Store 014 each morning in June'), chart);
  const after6 = s.by_shipment.map((x) => {
    const [hh, mm] = x.arrived_ts.slice(11, 16).split(':').map(Number);
    return Math.max(0.02, (hh * 60 + mm - 360) / 60);
  });
  barChart(chart, {
    ariaLabel: 'Truck arrival time at Store 014 for each delivery in June 2026, against the 06:30 end of the slot',
    series: [{ key: 'arrival', label: 'Arrival', color: C.record, values: after6 }],
    refs: [{ values: after6.map(() => 0.5), label: 'Slot ends at 06:30' }],
    yFormat: clock,
    xTick: (j) => (j % 6 === 0 ? dd(s.by_shipment[j].arrived_ts) : null),
    tooltip: (j): Tooltip => ({ title: day(s.by_shipment[j].arrived_ts), rows: [
      { label: 'arrived', value: time(s.by_shipment[j].arrived_ts), color: C.record },
      { label: s.by_shipment[j].in_slot ? 'in the slot' : 'late', value: '' },
    ] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'Arrival times in June', ['Delivery', 'Arrived', 'In the slot'],
    s.by_shipment.map((x) => [day(x.arrived_ts), time(x.arrived_ts), x.in_slot ? 'yes' : 'no']));
};

const receiving: Panel = (host, s) => {
  const claim = s.claims.find((c) => c.shipment_id === s.shipment.shipment_id);
  host.append(recordBlock([
    `Goods receipt ${s.receipts[0].grn_id}, ${when(s.receipts[0].received_ts)}`,
    `Method: ${s.receipts[0].receipt_method}`,
    'Pallet  Line  Item booked     Units',
    ...s.receipts.map((r) => `${short(r.sscc)}  ${String(r.line).padStart(4)}  ${name(r.sku_booked).padEnd(14)} ${String(r.units_booked).padStart(5)}`),
    claim ? `Discrepancy: notice ${claim.notice_units} × ${name(claim.notice_sku)}, found ${claim.received_units} × ${name(claim.received_sku)}. Claim ${claim.claim_id}.`
      : 'Discrepancies: none',
  ], 'What the store’s receiving screen shows once the pallets are booked.'));
  const pallets = data.records.shipments.reduce((a, x) => a + x.pallets, 0);
  const caseScan = s.receiving === 'case_scan';
  host.append(tiles([
    { label: 'Pallets received in June', value: num(pallets) },
    { label: 'Receiving discrepancies reported in June', value: String(s.claims.length) },
    { label: 'How each pallet is checked', value: caseScan ? 'Every case' : 'Pallet label', note: caseScan ? 'each case barcode scanned' : 'SSCC scanned against the shipping notice' },
  ]));
  host.append(says(claim
    ? '“Line 1 says 5 kg. It’s sixteen bales of 1 kg. I booked what’s here and raised a claim with the DC.”'
    : caseScan
      ? '“Every case scanned, and everything matched the notice.”'
      : '“Pallet labels scanned, notice matched, no discrepancies. Booked and put away before we opened.”'));
};

const scorecard: Panel = (host, s) => {
  const w = weeks(s);
  host.append(recordBlock([
    'OTIF scorecard, DC-BLR-01 to Store 014, by goods receipt',
    'Week of   Deliveries  On time  In full  OTIF',
    ...w.map((x) => `${x.label.padEnd(9)} ${String(x.n).padStart(10)}  ${String(x.slot).padStart(7)}  ${String(x.full).padStart(7)}  ${pct(x.good / x.n).padStart(4)}`),
  ], 'What the supply chain performance team publishes every week.'));
  const r = row22(s);
  const k = s.kpis;
  host.append(tiles([
    { label: 'OTIF for June, per delivery', value: pct(k.otif.scorecard), note: `${k.good.scorecard} of ${k.out_of.scorecard} deliveries` },
    { label: 'OTIF for June, per order line', value: pct(k.otif.by_line), note: `${k.good.by_line} of ${k.out_of.by_line} lines` },
    { label: `The ${dd(s.shipment.arrived_ts)} delivery`, value: r.scorecard ? 'On time, in full' : r.in_slot ? 'Not in full' : 'Late' },
  ]));
  const missed = s.by_shipment.filter((x) => !x.scorecard);
  const why = (x: typeof missed[number]) => `${dd(x.arrived_ts)} ${[!x.in_slot ? 'late' : '', !x.in_full_receipt ? 'short' : ''].filter(Boolean).join(' and ')}`;
  host.append(says(`“${pct(k.otif.scorecard)} for June. ${missed.length} deliveries missed: ${missed.map(why).join(', ')}. ${r.scorecard ? 'The 22 June delivery was perfect.' : 'The 22 June delivery missed.'}”`));
  const chart = h('div');
  host.append(h('h4', '', 'OTIF by week, as the scorecard measures it'), chart);
  barChart(chart, {
    ariaLabel: 'OTIF by week from the store’s goods receipts, June 2026',
    series: [{ key: 'otif', label: 'OTIF', color: C.record, values: w.map((x) => Math.round((x.good / x.n) * 100)) }],
    yMax: 100,
    yFormat: (v) => `${Math.round(v)}%`,
    xTick: (j) => w[j].label,
    tooltip: (j) => ({ title: `Week of ${w[j].label}`, rows: [
      { label: 'OTIF', value: pct(w[j].good / w[j].n), color: C.record },
      { label: 'deliveries', value: String(w[j].n) },
    ] }),
  });
};

const stock: Panel = (host, s) => {
  const counts = s.store_counts;
  if (!counts.length) {
    host.append(recordBlock(['Count adjustments, Store 014, 22–28 June', 'Atta: none'], 'What the stock controller sees: counts and the adjustments they made.'));
    host.append(says('“Atta counts are clean this week.”'));
    return;
  }
  const cost = COST;
  host.append(recordBlock([
    `Count adjustments, Store 014, ${when(counts[0].count_ts)}`,
    `Trigger: ${counts[0].trigger}`,
    'Item        On the books  Counted  Adjustment  At cost',
    ...counts.map((c) => `${name(c.sku).padEnd(11)} ${String(c.book_before).padStart(12)}  ${String(c.counted).padStart(7)}  ${plus(c.adjustment).padStart(10)}  ${inr(c.adjustment * cost[c.sku]).padStart(8)}`),
  ], 'What the stock controller sees: counts and the adjustments they made.'));
  const five = counts.find((c) => c.sku === HERO);
  const one = counts.find((c) => c.sku === ONE);
  const net = counts.reduce((a, c) => a + c.adjustment * cost[c.sku], 0);
  host.append(tiles([
    { label: '5 kg atta adjusted', value: five ? plus(five.adjustment) : '0', note: five ? `${inr(five.adjustment * cost[HERO])} at cost` : undefined },
    { label: '1 kg atta adjusted', value: one ? plus(one.adjustment) : '0', note: one ? `${inr(one.adjustment * cost[ONE])} at cost` : undefined },
    { label: 'Net adjustment at cost', value: inr(net) },
  ]));
  host.append(says(`“${five ? Math.abs(five.adjustment) : 0} bags of 5 kg atta gone, and ${one ? one.adjustment : 0} packs of 1 kg from nowhere. Either the counting is sloppy or 5 kg bags are walking out. Recount next week and watch the aisle.”`));
};

const truth: Panel = (host, s) => {
  const story = h('div', 'story');
  const wrong = ev(s, 'wrong_pallet');
  const pickScan = ev(s, 'pick_scan_caught_wrong_item');
  const weigh = ev(s, 'check_weigh_caught_wrong_item');
  const claim = s.claims[0];
  const ep = s.episodes.find((e) => e.empty_open_hours >= 5);
  const pick = s.picks.find((p) => p.sku === HERO)!;
  const line = s.notice.find((a) => a.sku === HERO)!;
  if (pickScan) {
    story.append(h('p', '', `${when(pickScan.ts)}: the picker reaches into slot ${SLOT[ONE]}, next to the 5 kg slot. The case scan rejects the 1 kg bale, and the right ${pick.cases_confirmed} cases of 5 kg go on the pallet. Every record downstream is true.`));
  } else if (weigh) {
    story.append(
      h('p', '', `${time(pick.pick_ts)}: the picker scans the label of slot ${pick.slot} and takes ${pick.cases_confirmed} bales from the next slot, the same brand’s 1 kg packs.`),
      h('p', '', `${when(weigh.ts)}: the dispatch scale finds pallet ${short(line.sscc)} ${Math.round(lightKg(s))} kg lighter than its shipping notice says it should be. The line is re-picked; the truck leaves at ${time(s.shipment.dispatched_ts)} and reaches the store at ${time(s.shipment.arrived_ts)}, outside its slot. Every record downstream is true, and the scorecard counts the delivery as late.`),
    );
  } else if (wrong) {
    story.append(
      h('p', '', `${time(pick.pick_ts)} on ${day(pick.pick_ts)}: the picker scans the label of slot ${pick.slot} (5 kg) and takes ${pick.cases_confirmed} bales from slot ${SLOT[ONE]} next to it, the same brand’s 1 kg packs. The scan confirms the slot, not the item.`),
      h('p', '', `From that confirmation the DC prints the pallet label (${line.sscc}) and sends the shipping notice: ${line.cases} cases of 5 kg, ${line.units} bags.`),
      h('p', '', `${when(s.shipment.arrived_ts)}: the truck arrives in its slot.${claim ? ' The clerk scans every case, finds 1 kg bales on line 1, books what arrived and raises a claim. The DC corrects both slots that morning, and the store’s reorder system orders 5 kg that night.' : ` The clerk scans the label, and the store books ${line.units} bags of 5 kg it does not have. The 160 packs of 1 kg go into the backroom, off the books.`}`),
    );
    if (!claim && ep) {
      story.append(h('p', '', `${when(ep.start)}: the 5 kg shelf runs out. The books show ${ep.book_on_hand_max} bags, above the reorder point of ${ep.reorder_point[ep.reorder_point.length - 1]}, so nothing is ordered.`));
      const [a1, a2] = s.dc_adjustments;
      if (a1 && a2) story.append(h('p', '', `${day(a1.adjusted_ts)} and ${day(a2.adjusted_ts)}: the DC corrects its two slots one at a time, ${plus(a1.cases)} and ${plus(a2.cases)} cases, as count variances. Nothing connects them to the truck.`));
      const c = s.store_counts[0];
      if (c) story.append(h('p', '', `${when(c.count_ts)}: after complaints, the store counts the atta bay. The shelf was empty for ${ep.empty_open_hours} open hours, and customers wanted ${ep.lost_units} bags they could not buy.`));
    }
  }
  host.append(story);

  const chart = h('div');
  host.append(h('h4', '', '5 kg atta: on the books and on the shelf, 20 to 28 June'), chart);
  const kinds = ['wrong_pallet', 'complaint_count', 'receiving_scan_caught_mismatch', 'check_weigh_caught_wrong_item', 'pick_scan_caught_wrong_item'];
  lineChart(chart, {
    ariaLabel: 'Book stock and shelf stock of 5 kg atta by hour, 20 to 28 June 2026',
    height: 230,
    series: [
      { key: 'book', label: 'On the books', color: C.record, values: s.hourly.book_5kg },
      { key: 'shelf', label: 'On the shelf', color: C.reality, values: s.hourly.shelf_5kg },
    ],
    bands: bands(s.hourly.empty_5kg),
    markers: s.events.filter((e) => kinds.includes(e.kind) && e.ts >= DAYS[0]).map((e) => ({ at: idxOf(e.ts), label: e.kind })),
    xTick: twoDayTick,
    tooltip: (j) => ({ title: hourLabel(j), rows: [
      { label: 'on the books', value: num(s.hourly.book_5kg[j]), color: C.record },
      { label: 'on the shelf', value: num(s.hourly.shelf_5kg[j]), color: C.reality },
      { label: 'customers wanted', value: num(s.hourly.demand_5kg[j]) },
    ] }),
  });
  const chart2 = h('div');
  host.append(h('h4', '', '1 kg atta: on the books and in the building'), chart2);
  lineChart(chart2, {
    ariaLabel: 'Book stock and physical stock of 1 kg atta by hour, 20 to 28 June 2026',
    height: 200,
    series: [
      { key: 'book', label: 'On the books', color: C.record, values: s.hourly.book_1kg },
      { key: 'physical', label: 'In the building', color: C.reality, values: s.hourly.physical_1kg },
    ],
    xTick: twoDayTick,
    tooltip: (j) => ({ title: hourLabel(j), rows: [
      { label: 'on the books', value: num(s.hourly.book_1kg[j]), color: C.record },
      { label: 'in the building', value: num(s.hourly.physical_1kg[j]), color: C.reality },
    ] }),
  });

  const k = s.kpis;
  const table = h('table', 'four-ways');
  table.append(h('caption', '', 'OTIF for June, measured four ways'));
  const tb = h('tbody');
  for (const [label, key, how] of [
    ['The DC’s report', 'dc_report', 'deliveries dispatched on schedule, every line shipped as ordered, by its pick confirmations'],
    ['The scorecard, per line', 'by_line', 'order lines that arrived in the slot and in full, by the store’s goods receipt'],
    ['The scorecard, per delivery', 'scorecard', 'deliveries in the slot with every line in full, by the goods receipt'],
    ['What the shelf got', 'at_the_shelf', 'deliveries in the slot with every case what the store ordered'],
  ] as const) {
    const tr = h('tr');
    tr.append(h('th', '', label), h('td', 'n', pct(k.otif[key])), h('td', 'how', `${how} (${k.good[key]} of ${k.out_of[key]})`));
    tb.append(tr);
  }
  table.append(tb);
  host.append(table);

  // Only the two packs the mis-pick swapped; the same count also caught a stray 10 kg bag.
  const swapped = s.store_counts.filter((c) => c.sku === HERO || c.sku === ONE);
  if (s.dc_adjustments.length || swapped.length) {
    const cost = COST;
    const rows: (string | number)[][] = [
      ...s.dc_adjustments.map((a) => [`DC, ${when(a.adjusted_ts)}`, name(a.sku), plus(a.units), inr(a.value_at_cost_inr)]),
      ...swapped.map((c) => [`Store, ${when(c.count_ts)}`, name(c.sku), plus(c.adjustment), inr(c.adjustment * cost[c.sku])]),
    ];
    const net = s.dc_adjustments.reduce((a, x) => a + x.value_at_cost_inr, 0) + swapped.reduce((a, c) => a + c.adjustment * cost[c.sku], 0);
    rows.push(['Net, across the company', '', '', inr(net)]);
    host.append(smallTable('ledger net', 'The stock corrections this one pallet line caused', ['Where and when', 'Item', 'Units', 'At cost'], rows));
  }
};

const PANELS: Record<string, Panel> = { dc, transport, receiving, scorecard, stock, truth };

function renderPersona(root: HTMLElement) {
  const host = root.querySelector('[data-panel]') as HTMLElement;
  host.replaceChildren();
  PANELS[state.persona](host, scn());
  host.setAttribute('aria-labelledby', `lg-tab-${state.persona}`);
}

// ---------- records drawer (the chain as it runs today) ----------
function renderRecords(root: HTMLElement, which: string, reveal: boolean) {
  const host = root.querySelector('[data-records]') as HTMLElement;
  const r = data.records;
  let head: string[] = [];
  let rows: { cells: (string | number)[]; flag?: string }[] = [];
  if (which === 'deliveries') {
    head = ['Delivery', 'Arrived', 'In the slot', 'Lines', 'Scorecard'];
    rows = asIs.by_shipment.map((x) => ({ cells: [x.shipment_id, when(x.arrived_ts), x.in_slot ? 'yes' : 'no', x.lines, x.scorecard ? 'on time, in full' : 'missed'],
      flag: x.scorecard && !x.at_the_shelf ? 'A line held the wrong item' : undefined }));
  } else if (which === 'notice') {
    head = ['Delivery', 'Pallet', 'Line', 'Notice says', 'Cases', 'Booked as', 'Units'];
    rows = r.notice.filter((a) => a.shipment_id >= 'SHP-260620').map((a) => ({
      cells: [a.shipment_id, short(a.sscc), a.line, name(a.sku), a.cases, name(a.booked_sku), a.booked_units],
      flag: a.really ? `Really ${a.really.units} × ${name(a.really.sku)}` : undefined }));
  } else if (which === 'picks') {
    const wrongPick = !!ev(asIs, 'wrong_pallet');
    head = ['Picked', 'Order', 'Slot', 'Item', 'Cases', 'Confirmed by'];
    rows = r.picks.filter((p) => p.pick_ts >= '2026-06-20').map((p) => ({
      cells: [when(p.pick_ts), p.order_id, p.slot, name(p.sku), p.cases_confirmed, p.confirmed_by],
      flag: wrongPick && p.shipment_id === asIs.shipment.shipment_id && p.sku === HERO
        ? `Taken from slot ${SLOT[ONE]}: ${name(ONE)}` : undefined }));
  } else {
    const cost = COST;
    head = ['Where', 'When', 'Item', 'Adjustment', 'Reason'];
    rows = [
      ...asIs.dc_adjustments.map((a) => ({ cells: ['DC', when(a.adjusted_ts), name(a.sku), `${plus(a.cases)} cases`, a.reason], flag: 'The 22 June mis-pick' })),
      ...asIs.store_counts.map((c) => ({ cells: ['Store', when(c.count_ts), name(c.sku), `${plus(c.adjustment)} (${inr(c.adjustment * cost[c.sku])})`, c.trigger], flag: 'The 22 June mis-pick' })),
    ];
  }
  host.replaceChildren(recordsTable(head, rows, reveal));
}

// ---------- wiring ----------
export function mountLogisticsDemo(root: HTMLElement) {
  const select = wireTabs(root, (p) => { state.persona = p; renderPersona(root); });
  const inputs = root.querySelectorAll<HTMLInputElement>('input[name="dc"], input[name="receiving"]');
  inputs.forEach((inp) => {
    inp.addEventListener('change', () => {
      state[inp.name as 'dc' | 'receiving'] = inp.value;
      renderOutcome(root);
      renderPersona(root);
    });
  });
  let recTab = 'deliveries';
  const reveal = root.querySelector<HTMLInputElement>('input[name="lg-reveal"]');
  root.querySelectorAll<HTMLButtonElement>('[data-rec]').forEach((b) => {
    b.addEventListener('click', () => {
      recTab = b.dataset.rec as string;
      root.querySelectorAll('[data-rec]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      renderRecords(root, recTab, !!reveal?.checked);
    });
  });
  reveal?.addEventListener('change', () => renderRecords(root, recTab, reveal.checked));

  // Deep links: /demo/?lg=truth&dc=pick_scan&recv=case_scan#logistics
  const q = new URLSearchParams(location.search);
  if (['none', 'pick_scan', 'check_weigh'].includes(q.get('dc') ?? '')) state.dc = q.get('dc') as string;
  if (['label', 'case_scan'].includes(q.get('recv') ?? '')) state.receiving = q.get('recv') as string;
  inputs.forEach((inp) => { inp.checked = inp.value === state[inp.name as 'dc' | 'receiving']; });
  renderOutcome(root);
  select(q.get('lg') && PANELS[q.get('lg') as string] ? (q.get('lg') as string) : 'dc');
  renderRecords(root, recTab, false);
  root.dataset.ready = 'true';
  (window as unknown as { logisticsDemo: unknown }).logisticsDemo = {
    state,
    select,
    set(nameOf: 'dc' | 'receiving', value: string) {
      const inp = root.querySelector<HTMLInputElement>(`input[name="${nameOf}"][value="${value}"]`);
      if (inp) { inp.checked = true; inp.dispatchEvent(new Event('change')); }
    },
  };
}
