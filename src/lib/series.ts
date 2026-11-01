// The series' five parts, in reading order. A post names its part in frontmatter; its place in the
// part comes from `order` (start 0, shelf 10s, truck 20s, money 30s, together 40s). A KPI post's
// place among its part's KPIs comes from the KPI's position in src/lib/kpis.ts.
import { DOMAINS } from './kpis';

export const PARTS = [
  { id: 'start', name: 'Start here', domain: undefined },
  { id: 'shelf', name: 'The shelf', domain: 'retail' },
  { id: 'truck', name: 'The truck', domain: 'logistics' },
  { id: 'money', name: 'The money', domain: 'payments' },
  { id: 'together', name: 'Putting it together', domain: undefined },
] as const;
export type PartId = (typeof PARTS)[number]['id'];

export const partOf = (id: string | undefined) => PARTS.find((p) => p.id === id);

/** The line above a post's title: its part, and where it sits in it. */
export function partLine(d: { part?: string; kpi?: string; order: number }, inPart: { data: { order: number; kpi?: string } }[]): string | undefined {
  const part = partOf(d.part);
  if (!part) return undefined;
  if (part.id === 'start') return part.name;
  if (part.domain) {
    const kpis = DOMAINS.find((x) => x.id === part.domain)!.kpis;
    const i = d.kpi ? kpis.findIndex((k) => k.id === d.kpi) : -1;
    return i >= 0 ? `${part.name}: KPI ${i + 1} of ${kpis.length}` : `${part.name}: the story`;
  }
  const sorted = [...inPart].sort((a, b) => a.data.order - b.data.order);
  return `${part.name}: ${sorted.findIndex((p) => p.data.order === d.order) + 1} of ${sorted.length}`;
}
