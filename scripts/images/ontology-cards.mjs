// The words and numbers on Season 2's pictures ("Ontology is all about domain knowledge").
// Store 014's numbers come from the KPI list the site builds (dist/kpis/domain-kpis.yaml) and from
// src/data/logistics*.json, so a card cannot drift from its post. The study in post 3 is outside
// data and is quoted from its paper (see the post's sources). Build the site first.
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import yaml from 'js-yaml';
import { C } from './charts.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const yamlFile = path.join(root, 'dist', 'kpis', 'domain-kpis.yaml');
if (!existsSync(yamlFile)) throw new Error('Build the site first (npm run build): cards read dist/kpis/domain-kpis.yaml');
const KPIS = yaml.load(readFileSync(yamlFile, 'utf8')).domains.flatMap((d) => d.kpis);
const kpi = (id) => {
  const k = KPIS.find((x) => x.id === id);
  if (!k) throw new Error(`no KPI ${id}`);
  return k;
};
const data = (f) => JSON.parse(readFileSync(path.join(root, 'src', 'data', f), 'utf8'));
const logistics = data('logistics.json');
const lai = data('logistics-ai.json');

const SEASON = 'Why Domain Matters · Ontology';
const FOOT = 'Store 014 is a simulated supermarket in Bengaluru.';
const num = (v) => parseFloat(String(v).replace('%', ''));

// Season 1's three headline KPIs, each measured twice.
const osa = kpi('osa').store_014;
const otif = kpi('otif').store_014;
const upi = kpi('success-rate').store_014;

// The 22 June line: what the pick, the notice and the receipt said, and what the cases held.
const st = logistics.story;
const kgOf = (sku) => Number(sku.match(/-(\d+)KG$/)[1]);
const recordKg = st.line.units * kgOf(st.line.sku);
const realKg = st.actual.units_actual * kgOf(st.actual.sku_actual);
const pick = st.picks.find((p) => p.line === st.line.line);
const receipt = st.receipt;
if (pick.cases_confirmed !== st.line.cases || receipt.units_booked !== st.line.units) throw new Error('the 22 June records no longer agree with each other');

// Rumiantsau and Fokeev (28 April 2026), arXiv 2604.25149: share of 100 questions answered
// correctly by Claude Opus 4.7, Claude Sonnet 4.6 and GPT-5.4, schema alone and with the note.
const STUDY = { alone: [45.5, 50.5], note: [67.7, 68.7], lift: [17, 23] };

export const ONTOLOGY_CARDS = [
  {
    slug: 'every-word',
    eyebrow: `${SEASON} · Start here`,
    headline: 'Every word has a blind spot',
    scope: 'Season 2: Ontology is all about domain knowledge',
    chips: [{ n: 'Available', text: 'books or shelf?' }, { n: 'In full', text: 'cases or the right item?' }, { n: 'Success', text: 'till or bank?' }],
    blind: 'Under every blind spot in Season 1 sat a word.',
    chart: {
      type: 'hbars',
      title: 'One word, two meanings, two numbers',
      sub: 'Store 014, June 2026: three KPIs, each measured twice (per cent)',
      legend: [{ name: 'As the system reports it', color: C.rec }, { name: 'As it really was', color: C.real }],
      labelW: 1000,
      max: 100,
      rows: [
        { label: 'Available, on the books', v: num(osa.reported.value), kind: 'rec', text: osa.reported.value },
        { label: 'Available, on the shelf', v: num(osa.observed.value), kind: 'real', text: osa.observed.value, bold: true },
        { label: 'In full, by the report', v: num(otif.reported.value), kind: 'rec', text: otif.reported.value },
        { label: 'In full, every case right', v: num(otif.observed.value), kind: 'real', text: otif.observed.value, bold: true },
        { label: 'Success, at the till', v: num(upi.reported.value), kind: 'rec', text: upi.reported.value },
        { label: 'Success, at the bank', v: num(upi.observed.value), kind: 'real', text: upi.observed.value, bold: true },
      ],
      note: 'On-shelf availability, OTIF and UPI payment success at Store 014.',
    },
    lesson: 'Every word has a blind spot',
    ruleLabel: 'Before an AI agent uses our numbers',
    rule: 'Agree what our words mean, and write it down.',
    checkLabel: 'Part',
    checks: ['Start here: three posts on why words matter.', 'Twelve words: the shelf, the truck, the money and the oil field.', 'Putting it together: who decides, one map, how to start.'],
    footLeft: FOOT,
    next: 'From a glossary to a knowledge graph',
  },

  {
    slug: 'glossary-to-graph',
    eyebrow: `${SEASON} · Start here · 2 of 3`,
    headline: 'From a glossary to a knowledge graph',
    scope: 'Six steps, explained with one kirana shop',
    chips: [{ n: '1', text: 'Glossary' }, { n: '2', text: 'Taxonomy' }, { n: '3', text: 'Data model' }, { n: '4', text: 'Semantic layer' }, { n: '5', text: 'Ontology' }, { n: '6', text: 'Knowledge graph' }],
    blind: 'Each step adds one thing. Agents need the top two.',
    chart: {
      type: 'hbars',
      title: 'Agents need the top two steps',
      sub: 'From a glossary to a knowledge graph, in one kirana',
      legend: [{ name: 'What an agent needs', color: C.real }, { name: 'Useful, but not enough', color: C.grey }],
      labelW: 760,
      max: 14,
      rows: [
        { label: '6 Knowledge graph', v: 6, kind: 'real', text: 'flat 302’s real account', bold: true },
        { label: '5 Ontology', v: 5, kind: 'real', text: 'family, bill, pack, rules', bold: true },
        { label: '4 Semantic layer', v: 4, kind: 'grey', text: 'monthly sales, one formula' },
        { label: '3 Data model', v: 3, kind: 'grey', text: 'the billing tables' },
        { label: '2 Taxonomy', v: 2, kind: 'grey', text: 'atta is a kind of flour' },
        { label: '1 Glossary', v: 1, kind: 'grey', text: 'udhaar: pay at month end' },
      ],
      note: 'Tables say where the data is. The top two say what it means.',
    },
    lesson: 'Agents need the top two steps',
    rule: 'Read the ontology before you read the tables.',
    checks: ['Write down the words your teams argue about.', 'Link each word to the records it points to.', 'Add the rules that must always hold.'],
    footLeft: 'A kirana is a neighbourhood grocery shop.',
    next: 'A 4 KB note beat a better model',
  },

  {
    slug: 'four-kb-note',
    eyebrow: `${SEASON} · Start here · 3 of 3`,
    headline: 'A 4 KB note beat a better model',
    scope: 'Three frontier models, 100 retail questions, April 2026',
    reported: { label: 'Schema alone', value: `${STUDY.alone[0]}–${STUDY.alone[1]}%`, how: 'answered correctly' },
    observed: { label: 'With a 4 KB note', value: `${STUDY.note[0]}–${STUDY.note[1]}%`, how: 'answered correctly' },
    blind: 'The note, not the model, explained the difference.',
    chart: {
      type: 'hbars',
      title: `The note moved every model ${STUDY.lift[0]} to ${STUDY.lift[1]} points`,
      sub: 'Share of 100 retail questions answered correctly (per cent)',
      legend: [{ name: 'Schema alone', color: C.grey }, { name: 'Schema and the note', color: C.real }],
      labelW: 1000,
      max: 100,
      rows: [
        { label: 'Schema alone, lowest model', v: STUDY.alone[0], kind: 'grey', text: `${STUDY.alone[0]}%` },
        { label: 'Schema alone, highest model', v: STUDY.alone[1], kind: 'grey', text: `${STUDY.alone[1]}%` },
        { label: 'With the note, lowest model', v: STUDY.note[0], kind: 'real', text: `${STUDY.note[0]}%`, bold: true },
        { label: 'With the note, highest model', v: STUDY.note[1], kind: 'real', text: `${STUDY.note[1]}%`, bold: true },
      ],
      note: 'Claude Opus 4.7, Claude Sonnet 4.6 and GPT-5.4.',
    },
    lesson: 'Meaning beats model choice',
    rule: 'Read the note on measures and rules before you write any query.',
    checks: ['Write one page on your measures and rules.', 'Test your agent with and without it.', 'Prefer an honest refusal to a confident guess.'],
    footLeft: 'Rumiantsau and Fokeev, arXiv, 28 April 2026.',
    next: 'Word 1, Item',
  },

  {
    slug: 'what-is-an-item',
    eyebrow: `${SEASON} · Word 1 of 12 · Item`,
    headline: 'What is an item?',
    scope: `Store 014’s 5 kg atta line, ${Number(st.shipment.arrived_ts.slice(8, 10))} June 2026`,
    chips: [{ n: 'Family', text: 'the atta' }, { n: 'Shelf', text: 'one 5 kg bag' }, { n: 'Warehouse', text: 'a case' }, { n: 'Billing', text: 'a code' }],
    blind: 'Four teams, one word, four different things.',
    chart: {
      type: 'hbars',
      title: `Three records said ${recordKg} kg of atta. The cases held ${realKg}.`,
      sub: `Store 014’s 5 kg atta line, ${Number(st.shipment.arrived_ts.slice(8, 10))} June 2026, ${st.line.cases} cases, in kilograms of atta`,
      labelW: 1100,
      max: recordKg * 1.15,
      rows: [
        { label: 'The pick, by the slot label', v: recordKg, kind: 'rec', text: `${recordKg} kg` },
        { label: 'The shipping notice', v: recordKg, kind: 'rec', text: `${recordKg} kg` },
        { label: 'The receipt, by the pallet label', v: recordKg, kind: 'rec', text: `${recordKg} kg` },
        { label: 'Inside the cases', v: realKg, kind: 'real', text: `${realKg} kg`, bold: true },
      ],
      note: `${st.line.units} bags of 5 kg on paper, ${st.actual.units_actual} packs of 1 kg in the cases.`,
    },
    lesson: 'An item is the pack, not the name',
    rule: 'An item is the pack the customer asked for, known by the code on the pack. Match on that code, never on the slot, the pallet label or the product name.',
    checks: ['Scan each case at receiving.', 'Match on the pack’s code.', 'Count fill rate by the item as well as by the case.'],
    footLeft: FOOT,
    next: 'Word 2, Sale',
  },
];

// The numbers the item post quotes, for anyone checking the card against the post.
export const ITEM_FACTS = { recordKg, realKg, shipped: lai.fill.shipped, ordered: lai.fill.ordered, pallets: lai.pallets.total };
