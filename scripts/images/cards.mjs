// The words and numbers on each KPI post's three images. Numbers are computed here from the same
// data files the posts read (src/data/*.json), so a card cannot drift from its post.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const data = (f) => JSON.parse(readFileSync(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'src', 'data', f), 'utf8'));
const ai = data('retail-ai.json');
const retail = data('retail.json');

const pct = (v) => `${Math.round(Math.abs(v) * 100)}%`;
const signed = (v) => `${v < 0 ? '−' : '+'}${pct(v)}`;
const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const dayLabel = (iso) => `${DOW[new Date(`${iso}T12:00:00Z`).getUTCDay()]} ${Number(iso.slice(8))}`;

// ---------- KPI 1: sales ----------
const s5 = ai.forecast.series_5kg;
const week = (k, key) => s5.slice(k * 7, k * 7 + 7).reduce((a, d) => a + d[key], 0);
const sold = [week(0, 'recorded'), week(1, 'recorded')];
const want = [week(0, 'true'), week(1, 'true')];
const ep = retail.story.episode;
const openHours = retail.meta.hours; // the hours the store is open, e.g. 7..21
const frac = (ts) => (Number(ts.slice(11, 13)) + Number(ts.slice(14, 16)) / 60 - openHours[0]) / openHours.length;
const dayIndex = (ts) => s5.findIndex((d) => d.date === ts.slice(0, 10));
const switching = ai.assistant.questions.find((q) => q.id === 'switching').domain.plan[0].result;
const shareStocked = switching.map((r) => r.share_5kg);
const shareAll = ai.assistant.questions.find((q) => q.id === 'why').naive.plan[2].result[0];

export const CARDS = [
  {
    slug: 'sales',
    n: 1,
    kpi: 'Sales',
    headline: 'An empty shelf looks like falling demand',
    scope: 'Store 014, 5 kg atta, the week of 8 June 2026 against the week before',
    reported: { value: signed(sold[1] / sold[0] - 1), how: `bags sold, ${sold[0]} → ${sold[1]}` },
    observed: { value: signed(want[1] / want[0] - 1), how: `bags shoppers came for, ${want[0]} → ${want[1]}` },
    blind: 'A till records a sale, not a shopper.',
    chart: {
      title: 'The shoppers kept coming. The sales stopped.',
      sub: '5 kg atta at Store 014, 1 to 14 June 2026, bags each day',
      aName: 'Bags shoppers came for',
      bName: 'Bags sold',
      days: s5.slice(0, 14).map((d) => ({ label: dayLabel(d.date), a: d.true, b: d.recorded })),
      band: {
        from: { i: dayIndex(ep.start), frac: frac(ep.start) },
        to: { i: dayIndex(ep.end), frac: frac(ep.end) },
        label: 'Shelf empty',
        sub: `${ep.book_on_hand_max} bags on the books`,
      },
      note: `5 kg share of atta sales while on the shelf: ${pct(shareStocked[0])} → ${pct(shareStocked[1])}. Over all hours: ${pct(shareAll.week1)} → ${pct(shareAll.week2)}.`,
    },
    lesson: 'Sales measure the shelf, not the shopper',
    rule: 'Before you compare sales across periods, take out the hours the shelf was empty.',
    checks: [
      'Look for silent hours while the books show stock.',
      'Compare the weeks again without those hours.',
      'Read the pack mix only when every pack was on the shelf.',
    ],
    next: 'On-shelf availability',
  },
];
