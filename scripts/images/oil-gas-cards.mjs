// The words and numbers on the Oil & Gas season's pictures. KPI rules and Field 014's two numbers
// come from the KPI list the site builds (dist/oil-and-gas/kpis.yaml, from src/lib/oil-gas.ts);
// chart data comes from src/data/oil-gas/field-014.json. Build the site first.
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import yaml from 'js-yaml';
import { C } from './charts.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const yamlFile = path.join(root, 'dist', 'oil-and-gas', 'kpis.yaml');
if (!existsSync(yamlFile)) throw new Error('Build the site first (npm run build): cards read dist/oil-and-gas/kpis.yaml');
const KPIS = yaml.load(readFileSync(yamlFile, 'utf8')).kpis;
const kpi = (id) => {
  const k = KPIS.find((x) => x.id === id);
  if (!k) throw new Error(`no Oil & Gas KPI ${id}`);
  return k;
};
const field = JSON.parse(readFileSync(path.join(root, 'src', 'data', 'oil-gas', 'field-014.json'), 'utf8'));
const well = JSON.parse(readFileSync(path.join(root, 'src', 'data', 'oil-gas', 'well-kpis.json'), 'utf8'));
const ws = well.story;
const us = (v) => Math.round(v).toLocaleString('en-US');
const pipe = JSON.parse(readFileSync(path.join(root, 'src', 'data', 'oil-gas', 'pipe-014.json'), 'utf8'));
const ps = pipe.story;
const BOTH = 'Field 014 and Refinery 014 exist only in a simulation.';
const refinery = JSON.parse(readFileSync(path.join(root, 'src', 'data', 'oil-gas', 'refinery-014.json'), 'utf8'));
const rs = refinery.story;
const REF = 'Refinery 014 is a simulated refinery on India’s west coast.';
const link = JSON.parse(readFileSync(path.join(root, 'src', 'data', 'oil-gas', 'linking.json'), 'utf8'));
const lw = link.well;
const money = (v) => `${v < 0 ? '−' : ''}$${Math.abs(v).toFixed(2)}`;
const hoursFrom = (iso, from) => (new Date(`${iso}:00Z`) - new Date(`${from}:00Z`)) / 3600000;
const dayTick = (iso, from) => ({ v: hoursFrom(`${iso}T00:00`, from), label: `${Number(iso.slice(8, 10))} Mar` });
const s = field.story;
const days = field.meta.days;
const w14 = field.daily.wells[s.case_well];
const day = (iso) => days.indexOf(iso);
const dayNum = (iso) => Number(iso.slice(8));
const hoursOf = (ts) => Number(ts.slice(11, 13)) / 24 + Number(ts.slice(14, 16)) / 1440;
const n = (v) => Math.round(v).toLocaleString('en-IN');

const SEASON = 'Why Domain Matters · Oil & Gas';
const FOOT = 'Field 014 is a simulated oil field in western India.';
const eyebrowKpi = (k) => `${SEASON} · KPI ${k.n} of 18 · ${k.name}`;
const nextOf = (id) => { const k = kpi(id); return `KPI ${k.n}, ${k.name}`; };
const linkEyebrow = (i) => `${SEASON} · Linking the KPIs · ${i} of 4`;
const chipK = (id, text) => ({ n: `KPI ${kpi(id).n}`, text });
const joinOf = (id) => link.joins.find((j) => j.id === id);
const joinRow = (id, label, kind) => { const j = joinOf(id); return { label, v: (100 * j.agree) / j.rows, kind, text: `${j.agree} of ${j.rows}` }; };

/** A KPI post's card: the KPI list supplies the numbers and the rule; the spec adds the rest. */
function kpiCard(id, spec) {
  const k = kpi(id);
  return {
    eyebrow: eyebrowKpi(k),
    rule: k.agent_rule,
    footLeft: FOOT,
    ...spec,
    reported: { ...k.case.reported, ...(spec.reported ?? {}) },
    observed: { ...k.case.observed, ...(spec.observed ?? {}) },
  };
}

const stopAt = day(s.pump.stop.slice(0, 10)) + hoursOf(s.pump.stop);
const sepFrom = day(s.separator.out_from.slice(0, 10)) + hoursOf(s.separator.out_from);
const sepTo = day(s.separator.out_to.slice(0, 10)) + hoursOf(s.separator.out_to);
const marchTicks = [0, 7, 14, 21, 30].map((d) => ({ i: d, label: `${dayNum(days[d])} Mar`, anchor: d === 30 ? 'end' : d === 0 ? 'start' : 'middle' }));
const upTo20 = days.slice(0, day('2026-03-20') + 1);
const af18 = field.daily.af[day('2026-03-18')];

export const OIL_GAS_CARDS = [
  {
    slug: 'every-barrel',
    eyebrow: `${SEASON} · Start here`,
    headline: 'Every barrel has a blind spot',
    scope: 'Field 014 and Refinery 014, simulated through March 2026',
    chips: [{ n: '6', text: 'KPIs from the well' }, { n: '5', text: 'from the pipe & ship' }, { n: '7', text: 'from the refinery' }],
    blind: 'Knowing what a record cannot see is domain knowledge.',
    chart: {
      type: 'lines',
      title: 'Steady on paper, failing in the ground',
      sub: 'Well 14 at Field 014, March 2026, barrels of oil a day',
      legend: [{ name: 'Allocated to Well 14', color: C.rec }, { name: 'Produced by Well 14', color: C.real }],
      length: days.length,
      step: 200,
      max: 1000,
      ticks: marchTicks,
      bands: [{ from: day(s.pump.wear_from), to: stopAt, label: 'Pump wearing', sub: `last test ${dayNum(s.w14_test.date)} Feb` }],
      series: [
        { name: 'allocated', values: w14.allocated, color: C.rec, width: 7 },
        { name: 'produced', values: w14.produced, color: C.real, width: 7 },
      ],
      note: `18 March: ${n(s.w14_18mar.allocated)} barrels allocated, ${n(s.w14_18mar.produced)} produced. The field meter was right every day.`,
    },
    lesson: 'Every barrel has a blind spot',
    ruleLabel: 'Before an agent acts on a KPI',
    rule: 'Ask which record the number came from, and what that record cannot see.',
    checkLabel: 'Part',
    checks: ['The well: six KPIs from Field 014’s pumps.', 'The pipe & ship: five KPIs between the field and the refinery.', 'The refinery: seven KPIs from Refinery 014.'],
    footLeft: 'Field 014 and Refinery 014 exist only in a simulation.',
    next: nextOf('og-production'),
  },

  kpiCard('og-production', {
    slug: 'production',
    headline: 'The field total was right. Well 14 was not.',
    scope: 'Field 014, Well 14, Wednesday 18 March 2026',
    reported: { how: 'barrels allocated to Well 14' },
    observed: { how: 'barrels Well 14 produced' },
    blind: 'Allocation shares the field’s oil by each well’s last test.',
    chart: {
      type: 'pair',
      title: 'The pump wore. The report stayed near 800.',
      sub: 'Well 14 at Field 014, 1 to 20 March 2026, barrels of oil each day',
      legend: [{ name: 'Barrels Well 14 produced', color: C.real }, { name: 'Barrels allocated to it', color: C.rec }],
      step: 200,
      days: upTo20.map((iso, i) => ({ label: i % 3 === 0 || i === upTo20.length - 1 ? `${dayNum(iso)}` : '', a: w14.produced[i], b: w14.allocated[i] })),
      bands: [{ from: { i: Math.floor(sepFrom), frac: sepFrom % 1 }, to: { i: Math.min(Math.floor(sepTo), upTo20.length - 1), frac: Math.floor(sepTo) > upTo20.length - 1 ? 1 : sepTo % 1 }, label: 'Test separator out', sub: 'no well test possible' }],
      note: `Allocation factor: ${s.af.first_week_mean.toFixed(2)} → ${af18.toFixed(2)}. Last test of Well 14: ${dayNum(s.w14_test.date)} February, ${s.w14_test.oil_bpd} barrels.`,
    },
    lesson: 'A well’s number is only as fresh as its last test',
    checks: ['Show the test date beside every allocated rate.', 'Read the allocation factor as a trend.', 'Compare each allocated rate with the pump’s own estimate.'],
    next: nextOf('og-production-efficiency'),
  }),

  kpiCard('og-production-efficiency', {
    slug: 'production-efficiency',
    headline: '99% of the plan, 95% of the field',
    scope: 'Field 014, March 2026',
    reported: { how: 'production efficiency against the plan' },
    observed: { how: 'against what the wells could produce' },
    blind: 'The plan had already taken the losses out.',
    chart: {
      type: 'hbars',
      title: 'The plan had already budgeted the losses',
      sub: 'Field 014, March 2026, thousands of barrels of oil (axis from 240)',
      labelW: 1060,
      min: 240,
      max: 292,
      rows: [
        { label: 'The business plan, set in November', v: ws.pe.plan_bbl / 1000, kind: 'grey', text: (ws.pe.plan_bbl / 1000).toFixed(1) },
        { label: 'What the wells could produce', v: ws.pe.mpp_bbl / 1000, kind: 'real', text: (ws.pe.mpp_bbl / 1000).toFixed(1), bold: true },
        { label: 'What the meter measured', v: ws.pe.actual_bbl / 1000, kind: 'rec', text: (ws.pe.actual_bbl / 1000).toFixed(1) },
      ],
      note: `Production efficiency: ${ws.pe.pe_plan_pct}% of the plan, ${ws.pe.pe_tests_pct}% of the wells. Well 14 lost ${us(ws.pe.w14_lost_bbl)} barrels.`,
    },
    lesson: 'A plan is not a potential',
    checks: ['Recompute against the wells’ latest tests.', 'Print the potential’s date and basis.', 'Show the biggest loss in barrels.'],
    next: nextOf('og-deferment'),
  }),

  kpiCard('og-deferment', {
    slug: 'deferred-production',
    headline: 'The pump’s barrels were filed under ‘other’',
    scope: 'Field 014, loss log, March 2026',
    reported: { how: 'barrels lost to pump trips, by the log' },
    observed: { how: 'barrels Well 14’s pump cost' },
    blind: 'A loss log sees stops, and only the causes known at the time.',
    chart: {
      type: 'hbars',
      title: 'Most of the pump’s barrels had no cause',
      sub: 'Field 014, barrels of oil lost in March 2026',
      legend: [{ name: 'The loss log', color: C.rec }, { name: 'What Well 14’s pump really cost', color: C.real }],
      labelW: 900,
      rows: [
        { label: 'Other: under investigation', v: ws.deferment.by_category['Other: under investigation'], kind: 'rec', text: us(ws.deferment.by_category['Other: under investigation']) },
        { label: 'Pump trips', v: ws.deferment.by_category['ESP trip, restarted'], kind: 'rec', text: us(ws.deferment.by_category['ESP trip, restarted']) },
        { label: 'Grid dip, 23 March', v: ws.deferment.by_category['Power supply (grid)'], kind: 'rec', text: us(ws.deferment.by_category['Power supply (grid)']) },
        { label: 'Process trips', v: ws.deferment.by_category['Process trip'], kind: 'rec', text: us(ws.deferment.by_category['Process trip']) },
        { label: 'Well 14’s pump', v: ws.deferment.pump_real_bbl, kind: 'real', text: us(ws.deferment.pump_real_bbl), bold: true },
      ],
      note: `${us(ws.deferment.wear_unlogged_bbl)} of Well 14’s barrels were never logged: the well kept running while its pump wore.`,
    },
    lesson: 'A big ‘other’ is a data problem',
    checks: ['Chase every ‘other’ until it has a cause.', 'Compare each well’s rate with its potential daily.', 'Update the log after the teardown.'],
    next: nextOf('og-decline'),
  }),

  kpiCard('og-decline', {
    slug: 'decline-rate',
    headline: 'Was it the reservoir or the pump?',
    scope: 'Field 014, February to March 2026',
    reported: { how: 'fall in Field 014’s oil' },
    observed: { how: 'fall for the reservoir, on producing hours' },
    blind: 'A monthly total cannot tell a stopped pump from a tired reservoir.',
    chart: {
      type: 'hbars',
      title: 'One pump, not the reservoir',
      sub: 'Fall in Field 014’s oil production, per cent in a month',
      labelW: 1180,
      max: 5.4,
      rows: [
        { label: 'February to March, by the meter', v: Math.abs(ws.decline.reported_monthly_pct), kind: 'rec', text: `${Math.abs(ws.decline.reported_monthly_pct).toFixed(1)}%` },
        { label: 'Usual pace, December to February', v: Math.abs(ws.decline.usual_monthly_pct), kind: 'grey', text: `${Math.abs(ws.decline.usual_monthly_pct).toFixed(1)}%` },
        { label: 'The reservoir, Well 14 taken out', v: Math.abs(ws.decline.reservoir_monthly_pct), kind: 'real', text: `${Math.abs(ws.decline.reservoir_monthly_pct).toFixed(1)}%`, bold: true },
      ],
      note: `Annualized, March’s fall is ${ws.decline.reported_annual_pct}% a year. Well 14 was down for the last eleven days.`,
    },
    lesson: 'A stopped pump is not a tired reservoir',
    checks: ['Compute decline per producing hour.', 'Take wells with mechanical events out.', 'Compare with the field’s usual pace.'],
    next: nextOf('og-esp-run-life'),
  }),

  kpiCard('og-esp-run-life', {
    slug: 'pump-run-life',
    headline: 'The average pump lives long. Well 14’s don’t.',
    scope: 'Field 014, every pump since 2019',
    reported: { how: 'average run of the failed pumps' },
    observed: { how: 'average run of Well 14’s last four' },
    blind: 'An average mixes every well and every cause.',
    chart: {
      type: 'hbars',
      title: 'Well 14’s pumps fail sooner each time',
      sub: 'Pump runs at Field 014, in days',
      labelW: 1080,
      rows: [
        { label: 'Average of the 20 failed pumps', v: ws.run_life.avg_reported_days, kind: 'rec', text: us(ws.run_life.avg_reported_days) },
        { label: 'Typical run, the other 15 wells', v: ws.run_life.km_median_others_days, kind: 'grey', text: us(ws.run_life.km_median_others_days) },
        ...['2022', '2023', '2024'].map((y, i) => ({ label: `Well 14, pump of ${y}`, v: ws.run_life.w14_sand_days[i], kind: 'real', text: `${ws.run_life.w14_sand_days[i]}` })),
        { label: 'Well 14, pump of 2025', v: ws.run_life.w14_last_days, kind: 'real', text: `${ws.run_life.w14_last_days}`, bold: true },
      ],
      note: 'Three of Well 14’s teardowns found sand wear. The 2025 pump is still in the hole.',
    },
    lesson: 'Fix the cause, not the pump',
    checks: ['Count running pumps in a survival curve.', 'Split run life by well and cause.', 'Flag repeat failures in one well.'],
    next: nextOf('og-lifting-cost'),
  }),

  kpiCard('og-lifting-cost', {
    slug: 'lifting-cost',
    headline: 'Cheaper per barrel, because the repair waited',
    scope: 'Field 014, March 2026',
    reported: { how: 'lifting cost a barrel, March' },
    observed: { how: 'with the workover that waited for a rig' },
    blind: 'A cost a barrel cannot see work that was due and not done.',
    chart: {
      type: 'bars',
      title: 'March looked cheaper because the repair waited',
      sub: 'Field 014, lifting cost in 2026, dollars a barrel',
      step: 2,
      values: [
        { v: ws.lifting.usd_per_bbl['2026-01'], label: `$${ws.lifting.usd_per_bbl['2026-01'].toFixed(2)}` },
        { v: ws.lifting.usd_per_bbl['2026-02'], label: `$${ws.lifting.usd_per_bbl['2026-02'].toFixed(2)}` },
        { v: ws.lifting.usd_per_bbl['2026-03'], label: `$${ws.lifting.usd_per_bbl['2026-03'].toFixed(2)}` },
        { v: ws.lifting.mar_with_workover, label: `$${ws.lifting.mar_with_workover.toFixed(2)}`, hot: true },
      ],
      ticks: [{ i: 0, label: 'January' }, { i: 1, label: 'February' }, { i: 2, label: 'March' }, { i: 3, label: 'March + workover' }],
      note: `Overdue maintenance: about $${us(ws.lifting.backlog[1].est_cost_usd)} in February, $${us(ws.lifting.backlog[2].est_cost_usd)} in March.`,
    },
    lesson: 'Work that waited is a cost moved',
    checks: ['Show the backlog and its cost.', 'Add deferred work back before comparing.', 'Put lost barrels beside the cost.'],
    next: nextOf('og-throughput'),
  }),

  kpiCard('og-throughput', {
    slug: 'throughput',
    headline: 'The pipe moved its barrels, and some were water',
    scope: 'Field 014’s pipeline to Refinery 014, March 2026',
    reported: { how: 'barrels the pipeline moved' },
    observed: { how: 'of them were water' },
    blind: 'A barrel moved is not a barrel of oil.',
    chart: {
      type: 'lines',
      title: 'The field saw the water. The refinery’s sampler did not.',
      sub: 'Water in the crude from Field 014, March 2026, per cent',
      legend: [{ name: 'Field’s sampler', color: C.real }, { name: 'Refinery’s sampler', color: C.rec }],
      length: days.length,
      step: 0.5,
      max: 2.5,
      ticks: marchTicks,
      bands: [{ from: day(ps.throughput.fault_from.slice(0, 10)) + hoursOf(ps.throughput.fault_from), to: day(ps.throughput.fault_to.slice(0, 10)) + hoursOf(ps.throughput.fault_to), label: 'Heater-treater down' }],
      refs: [{ value: ps.throughput.spec_pct, label: 'Limit at the refinery, 1%' }],
      series: [
        { name: 'field', values: pipe.daily.bsw_pct, color: C.real, width: 7 },
        { name: 'refinery', values: pipe.daily.lab_bsw_pct, color: C.rec, width: 7 },
      ],
      note: `${us(ps.throughput.water_bbl)} of the ${us(ps.throughput.gross_bbl)} barrels the pipe moved in March were water.`,
    },
    lesson: 'A barrel moved is not a barrel of oil',
    checks: ['Report net oil beside gross.', 'Alert on water above the limit.', 'Compare the water readings at both ends.'],
    footLeft: BOTH,
    next: nextOf('og-loss-gain'),
  }),

  kpiCard('og-loss-gain', {
    slug: 'loss-and-gain',
    headline: 'Inside tolerance every day, and wrong the same way',
    scope: 'Field 014’s pipeline to Refinery 014, March 2026',
    reported: { how: 'days inside the tolerance band' },
    observed: { how: 'days the receipt meter read high' },
    blind: 'A tolerance band asks how big, not which way.',
    chart: {
      type: 'bars',
      title: 'A gain every day, inside the band every day',
      sub: 'Daily loss and gain, Field 014 to Refinery 014, March 2026, per cent',
      step: 0.1,
      refs: [{ value: ps.loss_gain.tolerance_pct, label: `Alarm band, ±${ps.loss_gain.tolerance_pct.toFixed(2)}%` }],
      values: pipe.daily.lg_pct.map((v, i) => ({ v, hot: days[i] === ps.loss_gain.first_alert_7_days })),
      ticks: [0, 6, 13, 20, 30].map((i) => ({ i, label: `${dayNum(days[i])} Mar`, anchor: i === 30 ? 'end' : i === 0 ? 'start' : 'middle' })),
      note: `Seventh gain in a row on ${dayNum(ps.loss_gain.first_alert_7_days)} March. The receipt meter counted ${us(ps.loss_gain.gain_bbl)} barrels that never came.`,
    },
    lesson: 'Inside tolerance is not the same as right',
    checks: ['Alert on seven days the same way.', 'Track meter factors between provings.', 'Check the meter when a proving slips.'],
    footLeft: BOTH,
    next: nextOf('og-tank-stock'),
  }),

  kpiCard('og-tank-stock', {
    slug: 'tank-stock-accuracy',
    headline: 'The book and the gauge agreed. Both counted the water.',
    scope: 'Refinery 014, crude tank T-104, 31 March 2026',
    reported: { how: 'between the book and the gauge' },
    observed: { how: 'barrels of water both counted as crude' },
    blind: 'Two records can agree and share the same mistake.',
    chart: {
      type: 'hbars',
      title: 'Two records agreed. The tank held less.',
      sub: 'Tank T-104 at Refinery 014, 31 March 2026, barrels of crude (axis from 50,000)',
      labelW: 960,
      min: 50000,
      max: 60000,
      rows: [
        { label: 'The book', v: ps.tank.book_31, kind: 'rec', text: us(ps.tank.book_31) },
        { label: 'The gauge', v: ps.tank.gauge_net_31, kind: 'rec', text: us(ps.tank.gauge_net_31) },
        { label: 'Oil in the tank', v: ps.tank.true_oil_31, kind: 'real', text: us(ps.tank.true_oil_31), bold: true },
      ],
      note: `The month-end dip found ${us(ps.tank.dip_free_water_31)} barrels of free water. The water probe had read zero since 2 March.`,
    },
    lesson: 'Agreement is not accuracy',
    checks: ['Take free water off the gauge.', 'Dip by hand while the probe is out.', 'Reconcile against an independent record.'],
    footLeft: BOTH,
    next: nextOf('og-methane'),
  }),

  kpiCard('og-methane', {
    slug: 'methane-intensity',
    headline: 'Low on paper, visible from space',
    scope: 'Field 014, March 2026',
    reported: { how: 'methane intensity, by the inventory' },
    observed: { how: 'with the leak a satellite saw' },
    blind: 'An estimate built from emission factors cannot see a leak.',
    chart: (() => {
      const from = '2026-03-05T00:00';
      return {
        type: 'events',
        title: 'A satellite saw what the inventory could not',
        sub: 'Compressor K-2 at Field 014, March 2026',
        from: 0,
        to: hoursFrom('2026-03-18T00:00', from),
        ticks: ['2026-03-06', '2026-03-09', '2026-03-12', '2026-03-15', '2026-03-17'].map((d) => dayTick(d, from)),
        events: [
          { v: hoursFrom(ps.methane.leak_from, from), up: true, hot: true, anchor: 'start', lines: ['15:00 K-2 restarts', 'blowdown valve passing'] },
          { v: hoursFrom(ps.methane.satellite.ts, from), up: false, anchor: 'end', lines: ['11:10 satellite sees it', `about ${ps.methane.satellite.kg_h} kg/h, ±${ps.methane.satellite.uncertainty_pct}%`] },
          { v: hoursFrom('2026-03-15T10:30', from), up: true, anchor: 'end', lines: ['Crew finds the valve', `${ps.methane.leak_kg_h} kg/h; replaced 16 Mar`] },
        ],
        note: `${ps.methane.leak_t.toFixed(0)} tonnes of methane in ten days. The inventory: ${ps.methane.inventory_t} tonnes for the month.`,
      };
    })(),
    lesson: 'A measurement beats an estimate',
    checks: ['Put confirmed measurements in the KPI.', 'Watch the gas balance for jumps.', 'Survey after maintenance.'],
    next: nextOf('og-ship-waiting'),
  }),

  kpiCard('og-ship-waiting', {
    slug: 'ship-waiting-time',
    headline: 'Ready on time, waiting at anchor',
    scope: 'Refinery 014’s mooring, replacement crude cargo, March 2026',
    reported: { how: 'waiting, by the port’s schedule' },
    observed: { how: 'waiting, from its notice of readiness' },
    blind: 'A schedule written after the delay cannot measure it.',
    chart: (() => {
      const from = '2026-03-24T00:00';
      return {
        type: 'events',
        title: `${ps.ship.real_wait_days.toFixed(1)} days at anchor, ${ps.ship.reported_wait_days.toFixed(1)} by the schedule`,
        sub: 'The replacement cargo at Refinery 014’s mooring, March 2026',
        from: 0,
        to: hoursFrom('2026-03-30T12:00', from),
        ticks: ['2026-03-24', '2026-03-25', '2026-03-27', '2026-03-28', '2026-03-29', '2026-03-30'].map((d) => dayTick(d, from)),
        events: [
          { v: hoursFrom(ps.ship.nor, from), up: true, hot: true, anchor: 'start', lines: ['06:00 ready', 'notice of readiness'] },
          { v: hoursFrom(ps.ship.laytime_end, from), up: false, anchor: 'start', lines: ['26 Mar 00:00 laytime ends', 'demurrage starts'] },
          { v: hoursFrom(ps.ship.window, from), up: true, anchor: 'end', lines: ['18:00 port’s window', 'opens'] },
          { v: hoursFrom(ps.ship.berthed, from), up: false, anchor: 'middle', lines: ['09:40 berthed'] },
          { v: hoursFrom(ps.ship.hoses_off, from), up: true, anchor: 'end', lines: ['05:00 discharge', 'ends'] },
        ],
        note: `Demurrage: ${ps.ship.demurrage_days.toFixed(2)} days at $${us(ps.ship.demurrage_usd_day)} a day, $${us(ps.ship.demurrage_usd)}.`,
      };
    })(),
    lesson: 'Start the clock when the ship is ready',
    checks: ['Measure from the notice of readiness.', 'Show demurrage ship by ship.', 'Compare the schedule with the statement of facts.'],
    footLeft: BOTH,
    next: nextOf('og-utilization'),
  }),

  kpiCard('og-utilization', {
    slug: 'refinery-utilization',
    headline: 'Running at 98%, on the wrong crude',
    scope: 'Refinery 014, March 2026',
    reported: { how: 'crude unit utilization' },
    observed: { how: 'of the crude was light; the plan had 4%' },
    blind: 'A full crude unit says nothing about what the barrels are worth.',
    chart: {
      type: 'lines',
      title: 'The crude unit ran full. The hydrocracker lived on its tank.',
      sub: 'Refinery 014, March 2026, per cent',
      legend: [{ name: 'Crude unit', color: C.rec }, { name: 'Hydrocracker', color: C.real }, { name: 'Its feed tank, full', color: C.grey }],
      length: days.length,
      step: 20,
      max: 100,
      ticks: marchTicks,
      bands: [{ from: 9, to: 20.99, label: 'Light crude only' }],
      series: [
        { name: 'cdu', values: refinery.daily.map((d) => (d.run / rs.refinery.capacity_bpd) * 100), color: C.rec, width: 7 },
        { name: 'hcu', values: refinery.daily.map((d) => (d.hcu_feed / 65000) * 100), color: C.real, width: 7 },
        { name: 'tank', values: refinery.daily.map((d) => (d.vgo_tank / 340000) * 100), color: C.grey, width: 7, dash: '16 12' },
      ],
      note: `Half the crude was light, against ${rs.utilization.plan_light_pct}% in the plan. Margin ${money(rs.margin.realised)} a barrel; plan ${money(rs.margin.plan)}.`,
    },
    lesson: 'Full is not the same as earning',
    checks: ['Show the slate and margin beside utilization.', 'Watch the units that make the money.', 'Flag a slate far from the plan.'],
    footLeft: REF,
    next: nextOf('og-margin'),
  }),

  kpiCard('og-margin', {
    slug: 'refining-margin',
    headline: 'Record cracks, ordinary margin',
    scope: 'Refinery 014, March 2026',
    reported: { how: 'benchmark margin a barrel, from price screens' },
    observed: { how: 'the margin Refinery 014 realised' },
    blind: 'A screen does not pay this refinery’s crude premiums or freight.',
    chart: {
      type: 'waterfall',
      title: 'Record cracks, ordinary margin',
      sub: 'Refinery 014, March 2026, US dollars a barrel',
      steps: [
        { v: rs.margin.screen, text: money(rs.margin.screen), label: ['Screen', 'margin'] },
        { v: rs.margin.steps.plan_premium + rs.margin.steps.crude_premium, text: money(rs.margin.steps.plan_premium + rs.margin.steps.crude_premium), label: ['Crude', 'premiums'] },
        { v: rs.margin.steps.freight, text: money(rs.margin.steps.freight), label: ['Freight and', 'insurance'] },
        { v: rs.margin.steps.slate, text: money(rs.margin.steps.slate), label: ['The light', 'slate'] },
        { v: rs.margin.steps.demurrage, text: money(rs.margin.steps.demurrage), label: ['Demurrage'] },
      ],
      netText: money(rs.margin.realised),
      netLabel: ['Realised', 'margin'],
      note: `At normal premiums and freight, the plan would have earned ${money(rs.margin.plan)}.`,
    },
    lesson: 'A screen is not a refinery',
    checks: ['Report realised beside benchmark.', 'Walk the gap step by step.', 'Price the crude actually run.'],
    footLeft: REF,
    next: nextOf('og-diesel-yield'),
  }),

  kpiCard('og-diesel-yield', {
    slug: 'diesel-yield',
    headline: 'On plan, while the feed tank emptied',
    scope: 'Refinery 014, March 2026',
    reported: { how: `diesel yield; the plan was ${rs.diesel.plan_pct}%` },
    observed: { how: 'from March’s own crude' },
    blind: 'A yield drawn from stock is borrowed, not made.',
    chart: {
      type: 'hbars',
      title: 'On plan, with the tank paying for it',
      sub: 'Refinery 014’s diesel yield, March 2026, per cent of crude (axis from 30)',
      labelW: 1080,
      min: 30,
      max: 42,
      rows: [
        { label: 'The plan', v: rs.diesel.plan_pct, kind: 'grey', text: rs.diesel.plan_pct.toFixed(1) },
        { label: 'March, as reported', v: rs.diesel.yield_pct, kind: 'rec', text: rs.diesel.yield_pct.toFixed(1) },
        { label: 'Light crude on the tank, 10–21 Mar', v: rs.diesel.light_pct, kind: 'rec', text: rs.diesel.light_pct.toFixed(1) },
        { label: 'After the tank ran out, 24–31 Mar', v: rs.diesel.after_pct, kind: 'real', text: rs.diesel.after_pct.toFixed(1) },
        { label: 'March’s own crude', v: rs.diesel.own_pct, kind: 'real', text: rs.diesel.own_pct.toFixed(1), bold: true },
      ],
      note: `The feed tank: ${us(rs.diesel.vgo_start)} barrels at the start of March, ${us(rs.diesel.vgo_end)} by 24 March.`,
    },
    lesson: 'A yield drawn from stock is borrowed',
    checks: ['Include intermediate tank changes.', 'Read yields by week.', 'Watch the feed tanks.'],
    footLeft: REF,
    next: nextOf('og-energy-intensity'),
  }),

  kpiCard('og-energy-intensity', {
    slug: 'energy-intensity',
    headline: 'More efficient, because it was busier',
    scope: 'Refinery 014, February to March 2026',
    reported: { how: 'energy a barrel, February to March' },
    observed: { how: 'above what the same runs should use' },
    blind: 'A fuller refinery spreads its fixed energy over more barrels.',
    chart: {
      type: 'diverging',
      title: 'Less a barrel, more than it should have used',
      sub: 'Refinery 014, March 2026, per cent',
      labelW: 1000,
      rows: [
        { label: 'Energy a barrel, against February', v: rs.energy.ei_change_pct, text: `${rs.energy.ei_change_pct.toFixed(1).replace('-', '−')}%` },
        { label: 'Against what the runs should use', v: rs.energy.mar_over_expected_pct, hot: true, text: `+${rs.energy.mar_over_expected_pct.toFixed(1)}%` },
      ],
      note: `From 12 March the preheat train fouled; the furnaces burned ${us(rs.energy.extra_gj)} GJ more than expected.`,
    },
    lesson: 'Busier is not better',
    checks: ['Compare with what the runs should use.', 'Compare at like throughput and crude.', 'Watch furnace fuel and fouling.'],
    footLeft: REF,
    next: nextOf('og-availability'),
  }),

  kpiCard('og-availability', {
    slug: 'mechanical-availability',
    headline: '99.9% available, and one pump tripped three times',
    scope: 'Refinery 014, crude charge pumps, March 2026',
    reported: { how: 'mechanical availability' },
    observed: { how: 'trips of crude charge pump P-101A' },
    blind: 'A trip a spare absorbs costs no hours, so it does not count.',
    chart: (() => {
      const from = '2026-03-07T00:00';
      return {
        type: 'events',
        title: 'Three trips, no lost hours',
        sub: 'Crude charge pumps P-101A and B at Refinery 014, March 2026',
        from: 0,
        to: hoursFrom('2026-03-31T18:00', from),
        ticks: ['2026-03-08', '2026-03-15', '2026-03-22', '2026-03-29'].map((d) => dayTick(d, from)),
        events: [
          { v: hoursFrom(refinery.trips[0].trip, from), up: true, hot: true, anchor: 'start', lines: ['8 Mar P-101A trips', 'bearing vibration'] },
          { v: hoursFrom(refinery.trips[1].trip, from), up: false, hot: true, anchor: 'middle', lines: ['17 Mar trips again', 'seal leak'] },
          { v: hoursFrom(refinery.trips[2].trip, from), up: true, hot: true, anchor: 'end', lines: ['29 Mar trips again', 'the same bearing'] },
          { v: hoursFrom(rs.availability.b_alarm, from), up: false, anchor: 'end', lines: ['31 Mar the spare alarms', 'P-101B vibration'] },
        ],
        note: `The spare ran alone for ${rs.availability.spare_hours} hours. Mechanical availability: ${rs.availability.pct}%.`,
      };
    })(),
    lesson: 'A spare hides the failures',
    checks: ['Count trips per tag.', 'Track how long a spare runs alone.', 'Treat a repeat cause as open.'],
    footLeft: REF,
    next: nextOf('og-turnaround'),
  }),

  kpiCard('og-turnaround', {
    slug: 'turnaround',
    headline: 'On time, because the scope shrank',
    scope: 'Refinery 014, reformer turnaround, 23 February to 15 March 2026',
    reported: { how: 'restarted as planned' },
    observed: { how: `jobs deferred, ${rs.turnaround.deferred_sce} of them safety-critical inspections` },
    blind: 'A date can be kept by moving work.',
    chart: {
      type: 'hbars',
      title: 'On time, because the scope shrank',
      sub: 'Refinery 014’s reformer turnaround, work orders',
      labelW: 1160,
      rows: [
        { label: 'Planned', v: rs.turnaround.planned_orders, kind: 'grey', text: us(rs.turnaround.planned_orders) },
        { label: 'Found when the unit was opened', v: rs.turnaround.found_orders, kind: 'grey', text: us(rs.turnaround.found_orders) },
        { label: 'Completed', v: rs.turnaround.completed_orders, kind: 'rec', text: us(rs.turnaround.completed_orders) },
        { label: 'Deferred', v: rs.turnaround.deferred_orders, kind: 'real', text: us(rs.turnaround.deferred_orders), bold: true },
        { label: 'Safety-critical inspections deferred', v: rs.turnaround.deferred_sce, kind: 'real', text: `${rs.turnaround.deferred_sce} of ${rs.turnaround.planned_sce}` },
      ],
      note: `Restarted on schedule after ${rs.turnaround.days} days: $13.9 million, against a budget of $14.2 million.`,
    },
    lesson: 'A date kept is not a job done',
    checks: ['Report deferred work beside the schedule.', 'Risk-review every deferred inspection.', 'Track the deferred list to closure.'],
    footLeft: REF,
    next: nextOf('og-process-safety'),
  }),

  kpiCard('og-process-safety', {
    slug: 'process-safety',
    headline: 'Zero incidents, growing backlog',
    scope: 'Refinery 014, March 2026',
    reported: { how: 'Tier 1 and Tier 2 process safety events' },
    observed: { how: `safety-critical inspections overdue, up from ${rs.safety.overdue_feb}` },
    blind: 'A count of releases cannot see risk that has not released anything yet.',
    chart: {
      type: 'hbars',
      title: 'Zero events, growing backlog',
      sub: 'Refinery 014, process safety indicators, 2026',
      labelW: 1160,
      rows: [
        { label: 'Tier 1 and 2 events, March', v: 0, kind: 'rec', text: '0' },
        { label: 'Tier 3 challenges, February', v: rs.safety.tier3_feb, kind: 'grey', text: `${rs.safety.tier3_feb}` },
        { label: 'Tier 3 challenges, March', v: rs.safety.tier3_mar, kind: 'real', text: `${rs.safety.tier3_mar}` },
        { label: 'Overdue inspections, end of February', v: rs.safety.overdue_feb, kind: 'grey', text: `${rs.safety.overdue_feb}` },
        { label: 'Overdue inspections, end of March', v: rs.safety.overdue_mar, kind: 'real', text: `${rs.safety.overdue_mar}`, bold: true },
      ],
      note: `${rs.turnaround.deferred_sce} of the ${rs.safety.overdue_mar} overdue inspections were deferred from the reformer turnaround.`,
    },
    lesson: 'Zero events is not zero risk',
    checks: ['Report the backlog beside the count.', 'Trend both monthly.', 'Risk-review every deferral.'],
    footLeft: REF,
    next: 'Linking 1 of 4, the well',
  }),

  {
    slug: 'upstream',
    eyebrow: linkEyebrow(1),
    headline: 'One worn pump moved six KPIs',
    scope: 'Field 014, Well 14, March 2026',
    chips: [
      chipK('og-production', `Well 14: ${us(s.w14_18mar.allocated)} barrels`),
      chipK('og-production-efficiency', `Efficiency ${ws.pe.pe_plan_pct}%`),
      chipK('og-deferment', `Pump trips ${us(ws.deferment.esp_logged_bbl)} barrels`),
      chipK('og-decline', `Decline ${ws.decline.reported_annual_pct}% a year`),
      chipK('og-esp-run-life', `Run life ${ws.run_life.avg_reported_years} years`),
      chipK('og-lifting-cost', `Lifting cost $${ws.lifting.usd_per_bbl['2026-03'].toFixed(2)}`),
    ],
    blind: 'Six desks, six numbers, one pump.',
    chart: (() => {
      const from = '2026-03-01T00:00';
      return {
        type: 'events',
        title: 'Nine days of warning in the field’s own records',
        sub: 'Well 14 at Field 014, March and April 2026',
        from: 0,
        to: hoursFrom('2026-04-11T00:00', from),
        ticks: [['2026-03-01', '1 Mar'], ['2026-03-08', '8 Mar'], ['2026-03-15', '15 Mar'], ['2026-03-22', '22 Mar'], ['2026-03-29', '29 Mar'], ['2026-04-05', '5 Apr']].map(([d, label]) => ({ v: hoursFrom(`${d}T00:00`, from), label })),
        events: [
          { v: hoursFrom(`${s.pump.wear_from}T12:00`, from), up: true, anchor: 'start', lines: [`${dayNum(s.pump.wear_from)} Mar pump wears`, `allocated at its ${s.w14_test.oil_bpd} test`] },
          { v: hoursFrom(`${lw.march.flag}T12:00`, from), up: false, hot: true, lines: [`${dayNum(lw.march.flag)} Mar pump data parts`, `${us(lw.march.flag_allocated)} allocated, ${us(lw.march.flag_vfm)} estimated`] },
          { v: hoursFrom('2026-03-18T12:00', from), up: true, anchor: 'start', lines: [`18 Mar ${us(s.w14_18mar.allocated)} allocated`, `${us(s.w14_18mar.produced)} produced`] },
          { v: hoursFrom(s.pump.stop, from), up: false, anchor: 'start', lines: ['20 Mar pump stops', 'filed under other'] },
          { v: hoursFrom(`${ws.lifting.rig_free}T00:00`, from), up: true, anchor: 'end', lines: ['9 Apr rig free', `$${Math.round(ws.lifting.workover_usd / 1000)}k workover`] },
        ],
        note: `Well 14’s pump data parted from its allocated rate on ${dayNum(lw.march.flag)} March, ${{ 9: 'nine' }[lw.march.days_before_stop] ?? lw.march.days_before_stop} days before the pump stopped.`,
      };
    })(),
    lesson: 'The pump’s own data was the answer',
    ruleLabel: 'What one rule did',
    rule: `Across forty simulated Marches, an agent told to test a well when its pump’s data and its allocation part lost ${us(lw.b_lost_mean)} barrels instead of ${us(lw.a_lost_mean)}.`,
    checkLabel: 'Do this',
    checks: ['Join pump data to the allocation.', 'Test the well when they part.', 'Give your agent the rule.'],
    footLeft: FOOT,
    next: 'Linking 2 of 4, the pipe & ship',
  },

  {
    slug: 'midstream',
    eyebrow: linkEyebrow(2),
    headline: 'Inside tolerance, on schedule, and wrong',
    scope: 'Field 014 to Refinery 014, March 2026',
    chips: [
      chipK('og-throughput', `Throughput ${us(ps.throughput.gross_bbl)}`),
      chipK('og-loss-gain', `Loss and gain inside ${ps.loss_gain.days_inside} of 31 days`),
      chipK('og-tank-stock', 'T-104 within 0.5%'),
      chipK('og-methane', `Methane ${ps.methane.mi_reported_pct}%`),
      chipK('og-ship-waiting', `Waiting ${ps.ship.reported_wait_days} days`),
    ],
    blind: 'Every record agreed with the record beside it.',
    chart: {
      type: 'hbars',
      title: 'The pairs that always agreed missed the problems',
      sub: 'Pairs of March’s records from the field to the refinery, % that agree',
      labelW: 1060,
      max: 100,
      rows: [
        joinRow('fiscal-receipt', 'Fiscal and receipt meters', 'rec'),
        joinRow('book-gauge', 'T-104’s book and gauge', 'rec'),
        joinRow('water', 'Field water and refinery sampler', 'real'),
        joinRow('probe-dips', 'T-104’s probe and manual dips', 'real'),
        joinRow('gas', 'Gas balance and methane inventory', 'real'),
        joinRow('schedule-nor', 'Port schedule and notices', 'real'),
      ],
      note: 'The first two pairs agreed every day, and missed a meter reading high and 2,200 barrels of water. Each of the other four shows a problem.',
    },
    lesson: 'Agreement is not accuracy',
    ruleLabel: 'Five rules, replayed on March',
    rule: `They flag the dead probe on ${dayNum(link.pipe.tank.probe_flag)} March, the leak on ${dayNum(link.pipe.methane.ua_day)} March and the meter on ${dayNum(link.pipe.loss_gain.alert)} March, days or weeks before the dip, the satellite and the proving.`,
    checkLabel: 'Do this',
    checks: ['Alert on the sign, not only the size.', 'Treat a dead probe as a failure.', 'Join the gas balance to the inventory.'],
    footLeft: BOTH,
    next: 'Linking 3 of 4, the refinery',
  },

  {
    slug: 'downstream',
    eyebrow: linkEyebrow(3),
    headline: 'The best month, borrowed from April',
    scope: 'Refinery 014, March 2026',
    chips: [
      chipK('og-utilization', `Utilization ${rs.utilization.pct}%`),
      chipK('og-margin', `Margin ${money(rs.margin.screen)}`),
      chipK('og-diesel-yield', `Diesel yield ${rs.diesel.yield_pct}%`),
      chipK('og-energy-intensity', `Energy ${rs.energy.ei_change_pct}% a barrel`.replace('-', '−')),
      chipK('og-availability', `Availability ${rs.availability.pct}%`),
      chipK('og-turnaround', 'Turnaround on time'),
      chipK('og-process-safety', 'Zero events'),
    ],
    blind: 'Seven good numbers. April pays for four of them.',
    chart: (() => {
      const from = '2026-03-01T00:00';
      return {
        type: 'events',
        title: 'Two weeks of warning, each in a record no KPI read',
        sub: 'Refinery 014, March 2026',
        from: 0,
        to: hoursFrom('2026-04-01T00:00', from),
        ticks: ['2026-03-01', '2026-03-08', '2026-03-15', '2026-03-22', '2026-03-29'].map((d) => dayTick(d, from)),
        events: [
          { v: hoursFrom(`${link.refinery.tank.flag}T12:00`, from), up: false, anchor: 'end', lines: [`${dayNum(link.refinery.tank.flag)} Mar light crude`, `${link.refinery.tank.cover_days} days of VGO left`] },
          { v: hoursFrom(rs.turnaround.actual_end, from), up: true, anchor: 'end', lines: ['15 Mar reformer restarts', `${rs.turnaround.deferred_sce} inspections deferred`] },
          { v: hoursFrom(link.refinery.pump.flag, from), up: false, hot: true, anchor: 'end', lines: ['17 Mar P-101A trips', 'again, in ten days'] },
          { v: hoursFrom(`${rs.utilization.tank_min_day}T12:00`, from), up: false, hot: true, anchor: 'start', lines: ['24 Mar VGO at minimum', `hydrocracker ${rs.diesel.hcu_after_min_pct}–${rs.diesel.hcu_after_max_pct}%`] },
          { v: hoursFrom(rs.availability.b_alarm, from), up: true, anchor: 'end', lines: ['31 Mar the spare alarms', `${rs.safety.overdue_mar} inspections overdue`] },
        ],
        note: 'The tank, the trip log and the deferral list each warned two weeks ahead. No KPI read them.',
      };
    })(),
    lesson: 'A good month can be borrowed',
    ruleLabel: 'Seven rules, replayed on March',
    rule: `They flag the VGO tank on ${dayNum(link.refinery.tank.flag)} March and P-101A on 17 March, two weeks before the feed drum’s alarm and the spare’s.`,
    checkLabel: 'Do this',
    checks: ['Compute yields with tank changes.', 'Count trips per tag.', 'Report deferred work beside the date.'],
    footLeft: REF,
    next: 'Linking 4 of 4, who saw what',
  },

  {
    slug: 'well-to-refinery',
    eyebrow: linkEyebrow(4),
    headline: 'Who saw what, from the well to the refinery',
    scope: 'Field 014 and Refinery 014, March 2026, six problems',
    chips: [{ text: 'A worn pump' }, { text: 'A dead water probe' }, { text: 'A meter reading high' }, { text: 'A leaking valve' }, { text: 'A tank running down' }, { text: 'A pump failing again' }],
    blind: 'Every KPI read a record that could not see its problem.',
    chart: {
      type: 'hbars',
      title: 'Days by joining, weeks by waiting',
      sub: 'How many days sooner two joined records show each March problem',
      labelW: 1060,
      max: 32,
      rows: link.found.map((f) => ({ label: { pump: 'Well 14’s worn pump', probe: 'T-104’s dead probe', meter: 'The receipt meter', leak: 'K-2’s leaking valve', vgo: 'The VGO tank', p101: 'P-101A failing again' }[f.id], v: f.days_sooner, kind: 'real', text: `${f.days_sooner} days` })),
      note: `Two of the field’s or refinery’s own records, joined, showed each problem ${link.summary.days_sooner_min} to ${link.summary.days_sooner_max} days sooner.`,
    },
    lesson: 'Give your agent the map',
    ruleLabel: 'Forty simulated Marches',
    rule: `One rule from the map, test a well when its pump’s data and its allocation part, cut Well 14’s lost barrels by ${lw.saved_pct}%.`,
    checkLabel: 'Do this',
    checks: ['List the record each KPI reads.', 'Name the record that sees its problem.', 'Give the agent both.'],
    footLeft: 'The end of the Oil & Gas season. Thank you for reading.',
  },
];
