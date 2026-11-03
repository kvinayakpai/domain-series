// The series' six parts, in reading order. A post names its part in frontmatter; its place in the
// series comes from `order` (its post number, 1 to 25). A KPI post's number among the eighteen KPIs
// comes from SERIES_ORDER in src/lib/kpis.ts.
import { kpiNumber, KPI_COUNT } from './kpis';

export const PARTS = [
  { id: 'start', name: 'Start here', short: 'start here', domain: undefined },
  { id: 'shelf', name: 'The 18 KPIs: the shelf', short: 'the shelf', domain: 'retail' },
  { id: 'truck', name: 'The 18 KPIs: the truck', short: 'the truck', domain: 'logistics' },
  { id: 'money', name: 'The 18 KPIs: the money', short: 'the money', domain: 'payments' },
  { id: 'together', name: 'Linking the KPIs', short: 'linking the KPIs', domain: undefined },
  { id: 'practice', name: 'For practitioners', short: 'for practitioners', domain: undefined },
] as const;
export type PartId = (typeof PARTS)[number]['id'];

export const partOf = (id: string | undefined) => PARTS.find((p) => p.id === id);

/** The line above a post's title: "KPI 3 of 18 · the shelf", "Linking the KPIs: 2 of 4", and so on. */
export function partLine(d: { part?: string; kpi?: string; order: number }, inPart: { data: { order: number; kpi?: string } }[]): string | undefined {
  const part = partOf(d.part);
  if (!part) return undefined;
  if (part.id === 'start') return part.name;
  if (part.domain && d.kpi) return `KPI ${kpiNumber(d.kpi)} of ${KPI_COUNT} · ${part.short}`;
  const sorted = [...inPart].sort((a, b) => a.data.order - b.data.order);
  return `${part.name}: ${sorted.findIndex((p) => p.data.order === d.order) + 1} of ${sorted.length}`;
}
