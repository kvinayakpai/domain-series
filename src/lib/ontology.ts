// Season 2, "Ontology is all about domain knowledge": nineteen short posts. Three start the season
// (what an ontology is, why it matters for AI now, and the full Store 014 ontology on one page), one
// takes a technical detour through the same ontology in open standards, ten take Season 1's problems
// in retail, logistics and payments and show the part of the ontology that solves each, four look at what
// a machine could draft from Store 014's tables, how well AI models used it, and who else sells an ontology, and one says how to start. The plan lists every post in reading order, so the season
// page can show the posts still to come and a post's header can say "Retail: 1 of 4" before the rest
// are out. A post joins the plan by its slug; its front matter names its part (src/lib/series.ts).
// The ontology itself, its things, links, rules and what each record sees, is src/data/ontology.json.

export const ON_SEASON = { number: 2, name: 'Ontology is all about domain knowledge', short: 'Ontology' } as const;

export type OnPartId = 'on-start' | 'on-detour' | 'on-retail' | 'on-logistics' | 'on-payments' | 'on-together';

export interface OnPost {
  /** The post's number in the season, 1 to 15. */
  n: number;
  slug: string;
  title: string;
  part: OnPartId;
  /** One line for the season page. */
  note?: string;
  /** For a problem post: the Season 1 KPIs it solves (ids in src/lib/kpis.ts). */
  solves?: string[];
  /** The ontology's rules the post explains (numbers in src/data/ontology.json). */
  rules?: number[];
}

export const ON_POSTS: OnPost[] = [
  { n: 1, slug: 'what-is-an-ontology', title: 'What is an ontology?', part: 'on-start', note: 'Things, links and rules: the language of a business, written down so a machine can use it.' },
  { n: 2, slug: 'why-ontology-matters', title: 'Why does an ontology matter for AI now?', part: 'on-start', note: 'The 2026 evidence: a page of domain knowledge beat a change of model.' },
  { n: 3, slug: 'store-014-ontology', title: 'The Store 014 ontology, in full', part: 'on-start', note: 'Twenty-two things, their links, twelve rules and what each record sees, on one page.', rules: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] },
  { n: 4, slug: 'ontology-in-open-standards', title: 'The Store 014 ontology in RDF, OWL and SHACL', part: 'on-detour', note: 'For practitioners: the ontology as files in open standards, read by open-source tools in Python, JavaScript, Rust and Java.' },
  { n: 5, slug: 'stock-has-a-place', title: 'Stock has a place', part: 'on-retail', solves: ['osa', 'days-of-supply', 'ira'], rules: [1, 2] },
  { n: 6, slug: 'demand-is-not-sales', title: 'Demand is not sales', part: 'on-retail', solves: ['lfl', 'lost-sales', 'forecast'], rules: [2, 3, 4] },
  { n: 7, slug: 'a-correction-needs-a-reason', title: 'A correction needs a reason', part: 'on-retail', solves: ['shrink'], rules: [5] },
  { n: 8, slug: 'waste-and-the-empty-shelf', title: 'Waste and the empty shelf are one decision', part: 'on-retail', solves: ['fresh-waste'], rules: [6] },
  { n: 9, slug: 'an-item-is-the-pack', title: 'An item is the pack, not the slot', part: 'on-logistics', solves: ['pick-accuracy', 'fill-rate', 'otif'], rules: [7] },
  { n: 10, slug: 'a-delivery-ends-on-the-shelf', title: 'A delivery ends on the shelf', part: 'on-logistics', solves: ['on-time', 'otif'], rules: [8] },
  { n: 11, slug: 'four-corrections-one-mistake', title: 'Four corrections, one mistake', part: 'on-logistics', solves: ['net-adjustments'], rules: [5] },
  { n: 12, slug: 'a-payment-has-three-witnesses', title: 'A payment has three witnesses', part: 'on-payments', solves: ['success-rate', 'technical-declines'], rules: [9] },
  { n: 13, slug: 'one-bill-one-payment', title: 'One bill, one payment', part: 'on-payments', solves: ['charged-twice', 'match-rate'], rules: [10] },
  { n: 14, slug: 'the-refund-clock', title: 'The refund clock starts at the debit', part: 'on-payments', solves: ['refund-tat'], rules: [11] },
  { n: 15, slug: 'what-would-a-machine-draft', title: 'What would a machine draft for Store 014?', part: 'on-together', note: "NVIDIA's open-source Auto-Ontology drafts an ontology from a company's databases. What it could find at Store 014, and what no table holds." },
  { n: 16, slug: 'does-written-down-knowledge-help', title: 'Does written-down knowledge make an AI honest?', part: 'on-together', note: "The same four questions about one packet of atta, put to NVIDIA's model and to Claude's Haiku, Sonnet and Opus, with and without this season's knowledge." },
  { n: 17, slug: 'the-auto-ontology-experiment-in-full', title: 'The Auto-Ontology experiment, in full', part: 'on-together', note: 'Every run on Store 014: a small open model, a 7B model, NVIDIA\'s Nemotron and six fresh Claude agents, with the numbers and what went wrong.' },
  { n: 18, slug: 'ontology-tools-in-the-market', title: 'Who sells an ontology? A map of the tools', part: 'on-together', note: 'Databricks, Microsoft, Snowflake, Palantir and the open-source tools side by side: which are open, which are proprietary, and which write real RDF, OWL and SHACL.' },
  { n: 19, slug: 'start-a-domain-ontology', title: 'How to start your own domain ontology', part: 'on-together', note: 'The twelfth rule, eight steps from your own KPIs to a first ontology, and where to begin on Monday.', rules: [12] },
];

export const ON_POST_COUNT = ON_POSTS.length;

/** A post's place in the plan, by slug. */
export const onPost = (slug: string | undefined) => ON_POSTS.find((p) => p.slug === slug);

/** A post's place within its part, and the part's size in the plan. */
export function onPlaceInPart(slug: string | undefined): { i: number; of: number } | undefined {
  const p = onPost(slug);
  if (!p) return undefined;
  const inPart = ON_POSTS.filter((x) => x.part === p.part);
  return { i: inPart.findIndex((x) => x.slug === p.slug) + 1, of: inPart.length };
}
