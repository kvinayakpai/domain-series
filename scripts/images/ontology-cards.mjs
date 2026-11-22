// The words and numbers on Season 2's chart pictures ("Ontology is all about domain knowledge").
// Season 2 has no fixed set of pictures: a card names the ones it needs in `only` (open, summary,
// close). The full ontology map and its lit-up parts come from ontology-map.mjs instead.
// The study in "Why does an ontology matter for AI now?" is outside data, quoted from its paper (see
// the post's sources).
import { readFileSync } from 'node:fs';
import { C } from './charts.mjs';

// Six fresh Claude agents and NVIDIA's Nemotron on Store 014 (src/data/auto-ontology-claude-agents.json).
const AGENTS = JSON.parse(readFileSync(new URL('../../src/data/auto-ontology-claude-agents.json', import.meta.url), 'utf8'));
const honest = (model, knowledge) => AGENTS.agents.find((a) => a.model === model && a.knowledge === knowledge).honest;
const NEMO = (knowledge) => AGENTS.nemotron.find((a) => a.knowledge === knowledge).honest;
const row = (label, n, bold) => ({ label, v: n, kind: n === 2 ? 'real' : 'grey', text: `${n} of 2`, bold });

// One run of NVIDIA's Auto-Ontology on Store 014 (src/data/auto-ontology-run.json), and fourteen models read
// answer by answer (src/data/auto-ontology-model-sweep.json, its reviewed block).
const RUN = JSON.parse(readFileSync(new URL('../../src/data/auto-ontology-run.json', import.meta.url), 'utf8'));
const SWEEP = JSON.parse(readFileSync(new URL('../../src/data/auto-ontology-model-sweep.json', import.meta.url), 'utf8'));
const REV = SWEEP.reviewed;
const RIGHT = Object.entries(REV.per_model).filter(([, m]) => m.all_four_right > 0);
const NEVER = Object.keys(REV.per_model).length - RIGHT.length;

const SEASON = 'Why Domain Matters · Ontology';

// Rumiantsau and Fokeev (28 April 2026), arXiv 2604.25149: share of 100 questions answered
// correctly by Claude Opus 4.7, Claude Sonnet 4.6 and GPT-5.4, schema alone and with the note.
const STUDY = { alone: [45.5, 50.5], note: [67.7, 68.7], lift: [17, 23] };

export const ONTOLOGY_CARDS = [
  {
    slug: 'what-is-an-ontology',
    only: ['summary'],
    eyebrow: `${SEASON} · Start here · 1 of 3`,
    chart: {
      type: 'hbars',
      title: 'Six ways to write down a business’s words',
      sub: 'From a glossary to a knowledge graph, in one kirana',
      legend: [{ name: 'What an AI agent needs', color: C.real }, { name: 'Useful, but not enough', color: C.grey }],
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
  },

  {
    slug: 'why-ontology-matters',
    only: ['summary'],
    eyebrow: `${SEASON} · Start here · 2 of 3`,
    chart: {
      type: 'hbars',
      title: `The note moved every model ${STUDY.lift[0]} to ${STUDY.lift[1]} points`,
      sub: 'Share of 100 retail questions answered correctly (per cent)',
      legend: [{ name: 'Schema alone', color: C.grey }, { name: 'Schema and the 4 KB note', color: C.real }],
      labelW: 1000,
      max: 100,
      rows: [
        { label: 'Schema alone, lowest model', v: STUDY.alone[0], kind: 'grey', text: `${STUDY.alone[0]}%` },
        { label: 'Schema alone, highest model', v: STUDY.alone[1], kind: 'grey', text: `${STUDY.alone[1]}%` },
        { label: 'With the note, lowest model', v: STUDY.note[0], kind: 'real', text: `${STUDY.note[0]}%`, bold: true },
        { label: 'With the note, highest model', v: STUDY.note[1], kind: 'real', text: `${STUDY.note[1]}%`, bold: true },
      ],
      note: 'Claude Opus 4.7, Claude Sonnet 4.6 and GPT-5.4. Rumiantsau and Fokeev, April 2026.',
    },
  },

  {
    slug: 'what-would-a-machine-draft',
    only: ['open', 'close'],
    eyebrow: `${SEASON} · Putting it together · 1 of 5`,
    headline: 'The records knew the sales, not the shopper who left',
    scope: 'Store 014, June 2026',
    reported: { label: 'Named from the records', value: `${RUN.term_count}`, how: `things, in a ${RUN.run.draft_minutes}-minute draft by a machine` },
    observed: { label: 'Never named', value: '2', how: 'demand and the lost sale' },
    blind: 'A shopper who walks away leaves no row.',
    lesson: 'Ask what the records cannot see',
    ruleLabel: 'Tell your AI agent',
    rule: 'Before you trust a number, ask what its records cannot see.',
    checkLabel: 'Ask',
    checks: ['Which record does this KPI read?', 'Does that record look at the world, or copy another?', 'What happens in the business that no record holds?'],
    next: 'the knowledge layer',
  },

  {
    slug: 'does-written-down-knowledge-help',
    eyebrow: `${SEASON} · Putting it together · 2 of 5`,
    headline: 'Two answers exist. Two do not.',
    scope: '5 kg atta, June 2026',
    reported: { label: 'In the shop’s records', value: `${AGENTS.truth.sold}`, how: `bags sold, and ${AGENTS.truth.availability_pct}% on the shelf` },
    observed: { label: 'In no record at all', value: 'none', how: 'walk-aways and lost sales' },
    blind: 'A shopper who walks away leaves no row.',
    layers: {
      title: 'Five parts of a knowledge layer',
      sub: 'And what an AI does with each, at Store 014',
      rows: [
        { name: 'Words', example: 'OSA, RRN and the other codes', does: 'Reads the question as the business means it' },
        { name: 'Records', example: 'Till lines are sales, not demand. Book stock is a belief', does: 'Picks the right record, and spots the copies' },
        { name: 'KPIs', example: 'On-shelf: the share of shelf checks that found it', does: 'Uses the agreed formula, not its own' },
        { name: 'Rules', example: 'Demand is not sales. Say no record holds walk-aways', does: 'Knows when to say “no record”' },
        { name: 'Examples', example: 'Units sold by item and month, checked', does: 'Copies a pattern known to be right' },
      ],
      note: 'Formal OWL and SHACL files are a sixth form, for machines that check the data.',
    },
    lesson: 'Write it in plain words, tied to the records',
    ruleLabel: 'Tell your AI agent',
    rule: 'When no record holds the answer, say so, and if you estimate, say how.',
    checkLabel: 'Ask',
    checks: ['Is each rule tied to the record it is about?', 'Does every KPI have one agreed formula?', 'Can your AI say “no record”?'],
    next: 'the whole experiment',
  },

  {
    slug: 'the-auto-ontology-experiment-in-full',
    only: ['summary'],
    eyebrow: `${SEASON} · Putting it together · 3 of 5`,
    chart: {
      type: 'hbars',
      title: `The draft took ${AGENTS.draft.small_model.minutes} minutes on a small model, ${AGENTS.draft.nvidia.minutes} on NVIDIA’s`,
      sub: 'Minutes to draft the Store 014 ontology from its 21 tables',
      legend: [{ name: 'Small open model, free GitHub machine', color: C.grey }, { name: 'NVIDIA’s own model', color: C.real }],
      labelW: 1000,
      max: 50,
      rows: [
        { label: `${AGENTS.draft.small_model.name}, ${AGENTS.draft.small_model.terms} terms`, v: AGENTS.draft.small_model.minutes, kind: 'grey', text: `${AGENTS.draft.small_model.minutes} minutes` },
        { label: `${AGENTS.draft.nvidia.name}, ${AGENTS.draft.nvidia.terms} terms`, v: AGENTS.draft.nvidia.minutes, kind: 'real', text: `${AGENTS.draft.nvidia.minutes} minutes`, bold: true },
      ],
      note: 'Neither draft had a term for demand or a lost sale.',
    },
  },

  {
    slug: 'ontology-tools-in-the-market',
    eyebrow: `${SEASON} · Putting it together · 4 of 5`,
    headline: `Same four questions, fourteen models, ${SWEEP.runs} runs`,
    scope: '5 kg atta at Store 014, June 2026',
    chips: [
      { text: 'Made up a month without one query' },
      { text: 'Called a forecast 84 shoppers' },
      { text: 'Said “no record” even to 567 bags sold' },
      { text: 'Kept looking until the turns ran out' },
    ],
    blind: `All four right: ${REV.plain.all_four_right} of ${REV.plain.runs} runs. With one plain sentence: ${REV.rule.all_four_right}.`,
    chart: {
      type: 'hbars',
      title: `${RIGHT.length} of ${Object.keys(REV.per_model).length} models got all four answers right at least once`,
      sub: 'Runs with all four answers right, out of six per model',
      legend: [{ name: 'All four right at least once', color: C.real }, { name: 'Never', color: C.grey }],
      labelW: 1000,
      max: 6,
      rows: [
        ...RIGHT.map(([name, m]) => ({ label: name, v: m.all_four_right, kind: 'real', text: `${m.all_four_right}`, bold: m.all_four_right === Math.max(...RIGHT.map(([, x]) => x.all_four_right)) })),
        { label: `The other ${NEVER} models`, v: 0, kind: 'grey', text: '0' },
      ],
      note: `One run per setting, ${SWEEP.runs} runs read by hand.`,
    },
    lesson: 'Test before you trust',
    ruleLabel: 'Tell your AI agent',
    rule: 'When you are not sure, say so, and never fill a gap with a number.',
    checkLabel: 'Check',
    checks: ['Does it get the answers you already know?', 'Does it say “no record” where no record exists?', 'Does it do both every time you run it?'],
    next: 'the last step',
  },

  {
    slug: 'start-a-domain-ontology',
    only: ['open', 'close'],
    eyebrow: `${SEASON} · Putting it together · 5 of 5`,
    headline: 'The last step is yours',
    scope: 'What only people can add to a machine’s draft',
    chips: [
      { n: '1', text: 'What no record holds' },
      { n: '2', text: 'Which records are copies' },
      { n: '3', text: 'How the work really happens' },
    ],
    blind: 'You can buy the model and the tool. Not how your business works.',
    lesson: 'Write down how the work happens',
    ruleLabel: 'Tell your AI agent',
    rule: 'Before you act on a KPI, find the record it reads and an observation that can contradict it.',
    checkLabel: 'Monday',
    checks: ['Pick the KPI your business argues about most', 'Walk the work behind it, step by step', 'Write each disagreement down as a rule in plain words'],
    next: 'Season 3',
  },
];
