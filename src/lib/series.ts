// The series' seasons and parts, in reading order. A post names its part in frontmatter, and its
// season follows from the part. Store 014 (retail, logistics, payments) is posts 1 to 23; the Oil &
// Gas season, on Field 014 and Refinery 014, numbers its posts from 101. A KPI post's number among
// its season's eighteen KPIs comes from SERIES_ORDER in src/lib/kpis.ts or OG_KPIS in src/lib/oil-gas.ts.
import { kpiNumber, KPI_COUNT } from './kpis';
import { ogKpiNumber, OG_KPI_COUNT } from './oil-gas';

export const SEASONS = [
  { id: 'store-014', name: 'Store 014', home: '' },
  { id: 'oil-gas', name: 'Oil & Gas', home: 'oil-and-gas/' },
] as const;
export type SeasonId = (typeof SEASONS)[number]['id'];

export const PARTS = [
  { id: 'start', name: 'Start here', short: 'start here', domain: undefined, season: 'store-014', start: true },
  { id: 'shelf', name: 'The 18 KPIs: the shelf', short: 'the shelf', domain: 'retail', season: 'store-014', start: false },
  { id: 'truck', name: 'The 18 KPIs: the truck', short: 'the truck', domain: 'logistics', season: 'store-014', start: false },
  { id: 'money', name: 'The 18 KPIs: the money', short: 'the money', domain: 'payments', season: 'store-014', start: false },
  { id: 'together', name: 'Linking the KPIs', short: 'linking the KPIs', domain: undefined, season: 'store-014', start: false },
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

/** The line above a post's title: "KPI 3 of 18 · the shelf", "Oil & Gas · KPI 1 of 18 · the well", "Linking the KPIs: 2 of 4". */
export function partLine(d: { part?: string; kpi?: string; order: number }, inPart: { data: { order: number; kpi?: string } }[]): string | undefined {
  const part = partOf(d.part);
  if (!part) return undefined;
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
