// The series' seasons and parts, in reading order. A post names its part in frontmatter, and its
// season follows from the part. Season 1, Store 014 (retail, logistics, payments), is posts 1 to 23.
// Season 2, "Ontology is all about domain knowledge", numbers its posts from 201 and follows the plan
// in src/lib/ontology.ts. Season 3, Oil & Gas on Field 014 and Refinery 014, keeps the numbers from
// 101 it had when it was published as the second season. A KPI post's number among its season's
// eighteen KPIs comes from SERIES_ORDER in src/lib/kpis.ts or OG_KPIS in src/lib/oil-gas.ts.
import { kpiNumber, KPI_COUNT } from './kpis';
import { ogKpiNumber, OG_KPI_COUNT } from './oil-gas';
import { onWordNumber, ON_WORD_COUNT, onPlaceInPart } from './ontology';

export const SEASONS = [
  { id: 'store-014', number: 1, name: 'Store 014', home: '' },
  { id: 'ontology', number: 2, name: 'Ontology', home: 'ontology/' },
  { id: 'oil-gas', number: 3, name: 'Oil & Gas', home: 'oil-and-gas/' },
] as const;
export type SeasonId = (typeof SEASONS)[number]['id'];

export const PARTS = [
  { id: 'start', name: 'Start here', short: 'start here', domain: undefined, season: 'store-014', start: true },
  { id: 'shelf', name: 'The 18 KPIs: the shelf', short: 'the shelf', domain: 'retail', season: 'store-014', start: false },
  { id: 'truck', name: 'The 18 KPIs: the truck', short: 'the truck', domain: 'logistics', season: 'store-014', start: false },
  { id: 'money', name: 'The 18 KPIs: the money', short: 'the money', domain: 'payments', season: 'store-014', start: false },
  { id: 'together', name: 'Linking the KPIs', short: 'linking the KPIs', domain: undefined, season: 'store-014', start: false },
  { id: 'on-start', name: 'Start here', short: 'start here', domain: undefined, season: 'ontology', start: true },
  { id: 'on-shelf', name: 'Words from the shelf', short: 'the shelf', domain: undefined, season: 'ontology', start: false },
  { id: 'on-truck', name: 'Words from the truck', short: 'the truck', domain: undefined, season: 'ontology', start: false },
  { id: 'on-money', name: 'Words from the money', short: 'the money', domain: undefined, season: 'ontology', start: false },
  { id: 'on-field', name: 'A first look at the oil field', short: 'the oil field', domain: undefined, season: 'ontology', start: false },
  { id: 'on-together', name: 'Putting it together', short: 'putting it together', domain: undefined, season: 'ontology', start: false },
  { id: 'og-start', name: 'Oil & Gas: start here', short: 'start here', domain: undefined, season: 'oil-gas', start: true },
  { id: 'well', name: 'The 18 KPIs: the well', short: 'the well', domain: 'upstream', season: 'oil-gas', start: false },
  { id: 'pipe', name: 'The 18 KPIs: the pipe & ship', short: 'the pipe & ship', domain: 'midstream', season: 'oil-gas', start: false },
  { id: 'refinery', name: 'The 18 KPIs: the refinery', short: 'the refinery', domain: 'downstream', season: 'oil-gas', start: false },
  { id: 'og-together', name: 'Linking the KPIs', short: 'linking the KPIs', domain: undefined, season: 'oil-gas', start: false },
] as const;
export type PartId = (typeof PARTS)[number]['id'];

export const partOf = (id: string | undefined) => PARTS.find((p) => p.id === id);
/** The season a post belongs to, from its part. Posts without a part belong to Store 014. */
export const seasonOf = (part: string | undefined): SeasonId => partOf(part)?.season ?? 'store-014';

/**
 * The line above a post's title: "KPI 3 of 18 · the shelf", "Ontology · Word 1 of 12 · the shelf",
 * "Ontology · Start here: 2 of 3", "Oil & Gas · KPI 1 of 18 · the well", "Linking the KPIs: 2 of 4".
 */
export function partLine(
  d: { part?: string; kpi?: string; order: number; slug?: string; word?: string },
  inPart: { data: { order: number; kpi?: string } }[],
): string | undefined {
  const part = partOf(d.part);
  if (!part) return undefined;
  if (part.season === 'ontology') {
    // Season 2 numbers its posts from the plan, so a header reads the same before every post is out.
    if (d.word) return `Ontology · Word ${onWordNumber(d.word)} of ${ON_WORD_COUNT} · ${part.short}`;
    const place = onPlaceInPart(d.slug);
    return place ? `Ontology · ${part.name}: ${place.i} of ${place.of}` : `Ontology · ${part.name}`;
  }
  if (part.start) return part.name;
  if (part.domain && d.kpi) {
    return part.season === 'oil-gas'
      ? `Oil & Gas · KPI ${ogKpiNumber(d.kpi)} of ${OG_KPI_COUNT} · ${part.short}`
      : `KPI ${kpiNumber(d.kpi)} of ${KPI_COUNT} · ${part.short}`;
  }
  const sorted = [...inPart].sort((a, b) => a.data.order - b.data.order);
  const prefix = part.season === 'oil-gas' ? 'Oil & Gas · ' : '';
  return `${prefix}${part.name}: ${sorted.findIndex((p) => p.data.order === d.order) + 1} of ${sorted.length}`;
}
