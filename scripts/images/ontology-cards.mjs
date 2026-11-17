// The words and numbers on Season 2's chart pictures ("Ontology is all about domain knowledge").
// Season 2 has no fixed set of pictures: a card names the ones it needs in `only` (open, summary,
// close). The full ontology map and its lit-up parts come from ontology-map.mjs instead.
// The study in "Why does an ontology matter for AI now?" is outside data, quoted from its paper (see
// the post's sources).
import { C } from './charts.mjs';

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
];
