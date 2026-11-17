// Season 2, "Ontology is all about domain knowledge": eighteen short posts, one everyday word each.
// Three posts start the season, twelve words come from the shelf, the truck, the money and a first
// look at the oil field, and three put it together. The plan lists every post in reading order, so
// the season page can show the posts still to come and a post's header can say "Word 1 of 12".
// A post joins the plan by its slug; its front matter names its part (src/lib/series.ts) and, for a
// word post, its word.

export const ON_SEASON = { number: 2, name: 'Ontology is all about domain knowledge', short: 'Ontology' } as const;

export type OnPartId = 'on-start' | 'on-shelf' | 'on-truck' | 'on-money' | 'on-field' | 'on-together';

export interface OnPost {
  /** The post's number in the season, 1 to 18. */
  n: number;
  slug: string;
  title: string;
  part: OnPartId;
  /** For a word post: the word's id. */
  word?: string;
}

export const ON_POSTS: OnPost[] = [
  { n: 1, slug: 'every-word', title: 'Every word has a blind spot', part: 'on-start' },
  { n: 2, slug: 'glossary-to-graph', title: 'From a glossary to a knowledge graph, in one kirana', part: 'on-start' },
  { n: 3, slug: 'four-kb-note', title: 'A 4 KB note beat a better model', part: 'on-start' },
  { n: 4, slug: 'what-is-an-item', title: 'What is an item?', part: 'on-shelf', word: 'item' },
  { n: 5, slug: 'what-is-a-sale', title: 'What is a sale?', part: 'on-shelf', word: 'sale' },
  { n: 6, slug: 'in-stock', title: 'What does “in stock” mean?', part: 'on-shelf', word: 'in-stock' },
  { n: 7, slug: 'delivered', title: 'What does “delivered” mean?', part: 'on-truck', word: 'delivered' },
  { n: 8, slug: 'what-is-a-shipment', title: 'What is a shipment?', part: 'on-truck', word: 'shipment' },
  { n: 9, slug: 'on-time', title: 'What is “on time”?', part: 'on-truck', word: 'on-time' },
  { n: 10, slug: 'failed', title: 'What does “failed” mean?', part: 'on-money', word: 'failed' },
  { n: 11, slug: 'one-payment', title: 'What is one payment?', part: 'on-money', word: 'payment' },
  { n: 12, slug: 'settled', title: 'When is money really settled?', part: 'on-money', word: 'settled' },
  { n: 13, slug: 'what-is-a-well', title: 'What is a well?', part: 'on-field', word: 'well' },
  { n: 14, slug: 'what-is-a-barrel', title: 'What is a barrel?', part: 'on-field', word: 'barrel' },
  { n: 15, slug: 'what-is-a-pump', title: 'What is a pump?', part: 'on-field', word: 'pump' },
  { n: 16, slug: 'who-decides', title: 'Who decides what a word means?', part: 'on-together' },
  { n: 17, slug: 'one-map', title: 'One map from the shelf to the refinery', part: 'on-together' },
  { n: 18, slug: 'start-an-ontology', title: 'How to start a domain ontology', part: 'on-together' },
];

export const ON_POST_COUNT = ON_POSTS.length;
export const ON_WORDS = ON_POSTS.filter((p) => p.word);
export const ON_WORD_COUNT = ON_WORDS.length;

/** A word's number among the season's twelve words, in reading order. */
export const onWordNumber = (word: string) => ON_WORDS.findIndex((p) => p.word === word) + 1;

/** A post's place in the plan, by slug. */
export const onPost = (slug: string | undefined) => ON_POSTS.find((p) => p.slug === slug);

/** A start or together post's place within its part, and the part's size in the plan. */
export function onPlaceInPart(slug: string | undefined): { i: number; of: number } | undefined {
  const p = onPost(slug);
  if (!p) return undefined;
  const inPart = ON_POSTS.filter((x) => x.part === p.part);
  return { i: inPart.findIndex((x) => x.slug === p.slug) + 1, of: inPart.length };
}
