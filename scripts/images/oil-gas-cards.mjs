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
];
