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
    slug: 'does-written-down-knowledge-help',
    eyebrow: `${SEASON} · Putting it together · 2 of 4`,
    headline: 'Two answers exist. Two do not.',
    scope: '5 kg atta, June 2026',
    reported: { label: 'In the shop’s records', value: `${AGENTS.truth.sold}`, how: `bags sold, and ${AGENTS.truth.availability_pct}% on the shelf` },
    observed: { label: 'In no record at all', value: 'none', how: 'walk-aways and lost sales' },
    blind: 'A shopper who walks away leaves no row.',
    chart: {
      type: 'hbars',
      title: 'Who said “no record” on both?',
      sub: 'The two questions no record can answer: shoppers who left without, and lost sales',
      legend: [{ name: 'Said “no record” on both', color: C.real }, { name: 'Gave a number on at least one', color: C.grey }],
      labelW: 1000,
      max: 2,
      rows: [
        row('NVIDIA Nemotron, table list only', NEMO(false)),
        row('NVIDIA Nemotron, with our notes', NEMO(true), true),
        row('Haiku, table list only', honest('Haiku', false)),
        row('Haiku, with our notes', honest('Haiku', true)),
        row('Sonnet, table list only', honest('Sonnet', false)),
        row('Sonnet, with our notes', honest('Sonnet', true), true),
        row('Opus, table list only', honest('Opus', false)),
        row('Opus, with our notes', honest('Opus', true)),
      ],
      note: 'One run each. A number that is called an estimate still counts as a number.',
    },
    lesson: 'Say “no record” before you guess',
    ruleLabel: 'Tell your AI agent',
    rule: 'When no record holds the answer, say so, and if you estimate, say how.',
    checkLabel: 'Ask',
    checks: ['Which table does this number come from?', 'Could anyone have written this down at all?', 'How sure is the AI, and why?'],
    next: 'the whole experiment',
  },

  {
    slug: 'the-auto-ontology-experiment-in-full',
    only: ['summary'],
    eyebrow: `${SEASON} · Putting it together · 3 of 4`,
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
];
