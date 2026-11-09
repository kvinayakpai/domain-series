// The Oil & Gas season's eighteen KPIs, in reading order: six from the well, five from the pipe and
// the ship, seven from the refinery. A KPI gets its x-ray (what it drives, how it is computed, what
// the record cannot see, the check, the rule for an agent, and Field 014's two numbers) when its
// post is written. Numbers come from src/data/oil-gas/field-014.json, written by
// scripts/oil-gas/generate.py, so they cannot drift from the posts.
import field from '../data/oil-gas/field-014.json';

export interface Measured { value: string; how: string }
export interface OgKpi {
  id: string;
  name: string;
  part: 'well' | 'pipe' | 'refinery';
  drives?: string;
  computed?: string;
  blind?: string;
  check?: string;
  agent?: string;
  reported?: Measured;
  observed?: Measured;
  /** Field 014 or Refinery 014, in a sentence. */
  example?: string;
}

const s = field.story;
const num = (v: number) => Math.round(v).toLocaleString('en-IN');

export const OG_KPIS: OgKpi[] = [
  {
    id: 'og-production',
    name: 'Production',
    part: 'well',
    drives: 'The morning production meeting, which wells get attention, the reservoir model, and each partner’s and the government’s share.',
    computed: 'The field’s fiscal meter, shared out to the wells pro rata on each well’s last test: test rate times hours run, scaled so the wells add up to the meter.',
    blind: 'Anything that changed at a well since its last test. The change is spread across every well in the field, and the field total stays right.',
    check: 'Show each rate with the date of the test behind it; watch the allocation factor as a trend; compare each allocated rate with the pump’s own flow estimate.',
    agent: 'Never report a well’s rate without the date of the test behind it. When the pump’s own data disagrees with the allocated rate, ask for a well test before acting on either.',
    reported: { value: num(s.w14_18mar.allocated), how: 'barrels allocated to Well 14, 18 March' },
    observed: { value: num(s.w14_18mar.produced), how: 'barrels Well 14 produced' },
    example: `Well 14 on 18 March: ${num(s.w14_18mar.allocated)} barrels by the allocation, ${num(s.w14_18mar.produced)} produced. Its last test was ${s.w14_test.age_days_at_stop} days old when its pump stopped.`,
  },
  { id: 'og-production-efficiency', name: 'Production efficiency', part: 'well' },
  { id: 'og-deferment', name: 'Deferred production', part: 'well' },
  { id: 'og-decline', name: 'Decline rate', part: 'well' },
  { id: 'og-esp-run-life', name: 'Pump run life', part: 'well' },
  { id: 'og-lifting-cost', name: 'Lifting cost', part: 'well' },
  { id: 'og-throughput', name: 'Throughput', part: 'pipe' },
  { id: 'og-loss-gain', name: 'Loss and gain', part: 'pipe' },
  { id: 'og-tank-stock', name: 'Tank stock accuracy', part: 'pipe' },
  { id: 'og-methane', name: 'Methane intensity', part: 'pipe' },
  { id: 'og-ship-waiting', name: 'Ship waiting time', part: 'pipe' },
  { id: 'og-utilization', name: 'Refinery utilization', part: 'refinery' },
  { id: 'og-margin', name: 'Crack spread and refining margin', part: 'refinery' },
  { id: 'og-diesel-yield', name: 'Diesel yield', part: 'refinery' },
  { id: 'og-energy-intensity', name: 'Energy intensity', part: 'refinery' },
  { id: 'og-availability', name: 'Mechanical availability', part: 'refinery' },
  { id: 'og-turnaround', name: 'Turnaround performance', part: 'refinery' },
  { id: 'og-process-safety', name: 'Process safety events', part: 'refinery' },
];

/** A KPI's number in the Oil & Gas season, 1 to 18. */
export const ogKpiNumber = (id: string) => OG_KPIS.findIndex((k) => k.id === id) + 1;
export const OG_KPI_COUNT = OG_KPIS.length;
export const ogKpi = (id: string | undefined) => OG_KPIS.find((k) => k.id === id);
