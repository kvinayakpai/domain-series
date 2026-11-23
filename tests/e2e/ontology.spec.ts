import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import yaml from 'js-yaml';
import { ON_POSTS } from '../../src/lib/ontology';

// Season 2, "Ontology is all about domain knowledge": its contents page, its posts, the ontology they
// show (src/data/ontology.json) and the Store 014 numbers they quote. The numbers must still match the
// world (retail.json), its analysis (retail-ai.json), the finale's map (finale.json) and the KPI list
// the site builds, so a change to the world fails the build until the prose is updated.
const json = (f: string) => JSON.parse(readFileSync(new URL(`../../src/data/${f}`, import.meta.url), 'utf8'));
const ontology = json('ontology.json');
const check = json('ontology-check.json');
const retail = json('retail.json');
const ai = json('retail-ai.json');
const finale = json('finale.json');
// One run of NVIDIA's Auto-Ontology on Store 014, summarised by auto-ontology-demo/summarize.py.
const machineRun = json('auto-ontology-run.json');
// Six fresh Claude agents and NVIDIA's Nemotron on the same questions, scored against the records.
const claudeAgents = json('auto-ontology-claude-agents.json');
const repeat = json('auto-ontology-repeat-sweep.json');
const owlShacl = json('auto-ontology-owl-shacl.json');
const sweep = json('auto-ontology-model-sweep.json');
const story = retail.story;
const ep = story.episode;

// The posts that are out, in reading order: [slug, the line above the title].
const POSTS: [string, string][] = [
  ['what-is-an-ontology', 'Ontology · Start here: 1 of 3'],
  ['why-ontology-matters', 'Ontology · Start here: 2 of 3'],
  ['store-014-ontology', 'Ontology · Start here: 3 of 3'],
  ['ontology-in-open-standards', 'Ontology · A technical detour'],
  ['stock-has-a-place', 'Ontology · Retail: 1 of 4'],
  ['demand-is-not-sales', 'Ontology · Retail: 2 of 4'],
  ['a-correction-needs-a-reason', 'Ontology · Retail: 3 of 4'],
  ['waste-and-the-empty-shelf', 'Ontology · Retail: 4 of 4'],
  ['an-item-is-the-pack', 'Ontology · Logistics: 1 of 3'],
  ['a-delivery-ends-on-the-shelf', 'Ontology · Logistics: 2 of 3'],
  ['four-corrections-one-mistake', 'Ontology · Logistics: 3 of 3'],
  ['a-payment-has-three-witnesses', 'Ontology · Payments: 1 of 3'],
  ['one-bill-one-payment', 'Ontology · Payments: 2 of 3'],
  ['the-refund-clock', 'Ontology · Payments: 3 of 3'],
  ['what-would-a-machine-draft', 'Ontology · Putting it together: 1 of 5'],
  ['does-written-down-knowledge-help', 'Ontology · Putting it together: 2 of 5'],
  ['the-auto-ontology-experiment-in-full', 'Ontology · Putting it together: 3 of 5'],
  ['ontology-tools-in-the-market', 'Ontology · Putting it together: 4 of 5'],
  ['start-a-domain-ontology', 'Ontology · Putting it together: 5 of 5'],
];
// Posts 6 to 14 take Season 1's problems; post 15 says how to start.
const PROBLEMS = ['demand-is-not-sales', 'a-correction-needs-a-reason', 'waste-and-the-empty-shelf', 'an-item-is-the-pack',
  'a-delivery-ends-on-the-shelf', 'four-corrections-one-mistake', 'a-payment-has-three-witnesses', 'one-bill-one-payment', 'the-refund-clock'];
// Post 1 is in Vinayak's voice; the others are narrated by his AI assistant.
const NARRATED = ['why-ontology-matters', 'store-014-ontology', 'ontology-in-open-standards', 'stock-has-a-place', ...PROBLEMS, 'what-would-a-machine-draft', 'does-written-down-knowledge-help', 'the-auto-ontology-experiment-in-full', 'ontology-tools-in-the-market', 'start-a-domain-ontology'];
// Posts that end with one rule for an agent. The full ontology post lists all twelve instead.
const ONE_RULE = ['why-ontology-matters', 'ontology-in-open-standards', 'stock-has-a-place', ...PROBLEMS, 'what-would-a-machine-draft', 'does-written-down-knowledge-help', 'the-auto-ontology-experiment-in-full', 'ontology-tools-in-the-market', 'start-a-domain-ontology'];
// Posts about a Season 1 problem carry its record and reality lines; the opening posts explain instead.
const WITH_PAIR = ['stock-has-a-place', ...PROBLEMS];

async function articleText(page: import('@playwright/test').Page, path: string) {
  await page.goto(path);
  // Typographic quotes in the page compare equal to plain ones in the expectations.
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}
async function kpiList(request: import('@playwright/test').APIRequestContext) {
  const list = yaml.load(await (await request.get('kpis/domain-kpis.yaml')).text()) as { domains: { kpis: { id: string; name: string; store_014: { reported: { value: string }; observed: { value: string } } }[] }[] };
  return list.domains.flatMap((d) => d.kpis);
}

for (const p of [{ path: 'ontology/', og: 'ontology' }, ...POSTS.map(([slug]) => ({ path: `${slug}/`, og: slug }))]) {
  test(`${p.path} renders cleanly`, async ({ page, request }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    const res = await page.goto(p.path);
    expect(res?.status()).toBe(200);
    await expect(page.locator('h1')).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', `https://kvinayakpai.github.io/domain-series/og/${p.og}.png`);
    const og = await request.get(`og/${p.og}.png`);
    expect(og.status()).toBe(200);
    expect(errors).toEqual([]);
  });
}

test('home points to Season 2 ahead of Season 3, and the season pages say which is which', async ({ page }) => {
  await page.goto('./');
  await expect(page.locator('.season-next a[href$="/ontology/"]')).toHaveCount(1);
  await expect(page.locator('.season-next a[href$="/what-is-an-ontology/"]')).toHaveCount(1);
  const seasons = await page.locator('.season-next h2').allInnerTexts();
  expect(seasons[0]).toContain('Season 2');
  expect(seasons[1]).toContain('Season 3');
  await expect(page.locator('.site-nav a[href$="/ontology/"]')).toHaveText('Ontology');
  await page.goto('ontology/');
  await expect(page.locator('.season')).toHaveText(/season two/i);
  await page.goto('oil-and-gas/');
  await expect(page.locator('.season')).toHaveText(/season three/i);
});

test('the season page lists all nineteen posts, links the ones that are out, and covers every Season 1 KPI', async ({ page, request }) => {
  await page.goto('ontology/');
  await expect(page.locator('.opener a[href$="/what-is-an-ontology/"]')).toHaveCount(1);
  await expect(page.locator('.on-posts li')).toHaveCount(19);
  await expect(page.locator('.on-posts li.is-out')).toHaveCount(POSTS.length);
  await expect(page.locator('.on-posts li.is-coming')).toHaveCount(19 - POSTS.length);
  for (const [slug] of POSTS) await expect(page.locator(`.on-posts a[href$="/${slug}/"]`)).toHaveCount(1);
  await expect(page.locator('.on-part h3')).toHaveText(['Start here', 'A technical detour', 'Retail', 'Logistics', 'Payments', 'Putting it together']);
  // Every one of Season 1's eighteen KPIs is solved by some post of the plan.
  const solves = (await page.locator('.on-posts .note').allInnerTexts()).join(' ').toLowerCase();
  const kpis = await kpiList(request);
  expect(kpis.length).toBe(18);
  for (const k of kpis) expect(solves, k.name).toContain(k.name.toLowerCase());
});

test('the ontology has twenty-two things and twelve rules, and the rules cover every Season 1 KPI', async ({ request }) => {
  expect(ontology.things.length).toBe(22);
  expect(ontology.rules.map((r: { n: number }) => r.n)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  const ids = new Set(ontology.things.map((t: { id: string }) => t.id));
  for (const l of ontology.links) {
    expect(ids.has(l.from), `${l.from} > ${l.to}`).toBe(true);
    expect(ids.has(l.to), `${l.from} > ${l.to}`).toBe(true);
  }
  for (const r of ontology.rules) for (const on of r.on) expect(ids.has(on) || on === 'records', `rule ${r.n} on ${on}`).toBe(true);
  const kpis = (await kpiList(request)).map((k) => k.id);
  const solved = new Set(ontology.rules.flatMap((r: { solves: string[] }) => r.solves));
  for (const s of solved) expect(kpis, `rule names ${s}`).toContain(s);
  for (const k of kpis) expect(solved.has(k), `no rule solves ${k}`).toBe(true);
});

test('season posts link only to outside sources, carry the AI line and described pictures', async ({ page, request }) => {
  for (const [slug, line] of POSTS) {
    await page.goto(`${slug}/`);
    await expect(page.locator('.post-domain'), slug).toHaveText(line);
    const prose = 'article > p a[href], article > ul a[href], article > ol a[href], article > blockquote a[href]';
    const own = await page.locator(prose).evaluateAll((as) =>
      as.map((a) => a as HTMLAnchorElement).filter((a) => a.origin === location.origin).map((a) => a.getAttribute('href')),
    );
    expect(own, slug).toEqual([]);
    await expect(page.locator('article'), slug).toContainText(/written by AI and engineered by Vinayak/);
    await expect(page.locator('article'), slug).toContainText('Curious to know what you think');
    if (ONE_RULE.includes(slug)) await expect(page.locator('article'), slug).toContainText('The rule I would give any AI agent –');
    await expect(page.locator('dl.pair'), slug).toHaveCount(WITH_PAIR.includes(slug) ? 1 : 0);
    const imgs = await page.locator('article figure.picture img').evaluateAll((els) => els.map((e) => ({ src: (e as HTMLImageElement).getAttribute('src')!, alt: (e as HTMLImageElement).alt })));
    expect(imgs.length, slug).toBeGreaterThanOrEqual(1);
    for (const img of imgs) {
      expect(img.alt.length, `${slug} ${img.src}`).toBeGreaterThan(60);
      const res = await request.head(img.src.replace('/domain-series/', ''));
      expect(res.status(), img.src).toBe(200);
      expect(res.headers()['content-type'], img.src).toContain('image/png');
    }
    if (NARRATED.includes(slug)) {
      // The narrator is flagged the first time it says I.
      const plain = (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'");
      const flagged = plain.indexOf("I (Vinayak's AI Assistant)");
      expect(flagged, slug).toBeGreaterThan(-1);
      expect(plain.match(/\bI\b(?! \(Vinayak)/)?.index ?? Infinity, slug).toBeGreaterThan(flagged);
    }
  }
});

test('the full ontology post shows the map, opens it at full size and lists the twelve rules from the ontology', async ({ page, request }) => {
  await page.goto('store-014-ontology/');
  const zoom = page.locator('figure.picture a.zoom');
  await expect(zoom).toHaveCount(1);
  const href = (await zoom.getAttribute('href'))!;
  expect(href).toMatch(/images\/store-014-ontology\/map\.png$/);
  expect((await request.head(href.replace('/domain-series/', ''))).status()).toBe(200);
  const items = page.locator('ol.ontology-rules li');
  await expect(items).toHaveCount(12);
  const texts = (await page.locator('ol.ontology-rules .text').allInnerTexts()).map((t) => t.replace(/[“”]/g, '"'));
  expect(texts).toEqual(ontology.rules.map((r: { text: string }) => r.text.replace(/[“”]/g, '"')));
  const names = new Map((await kpiList(request)).map((k) => [k.id, k.name.toLowerCase()]));
  const fixes = await page.locator('ol.ontology-rules .fixes').allInnerTexts();
  ontology.rules.forEach((r: { n: number; solves: string[] }, i: number) => {
    if (!r.solves.length) expect(fixes[i]).toContain('All eighteen');
    for (const id of r.solves) expect(fixes[i].toLowerCase(), `rule ${r.n}`).toContain(names.get(id)!);
  });
  const text = await articleText(page, 'store-014-ontology/');
  expect(text).toContain('Twenty-two things, in four groups.');
  expect(text).toContain('Twelve rules. Each one is a fix from Season 1, written down.');
  // The records paragraph names the same records as the map, in the same order.
  const said = (list: string[]) => list.map((r) => (r.includes("'s ") ? r : `the ${r}`)).join(', ').replace(/, ([^,]+)$/, ' and $1');
  expect(text).toContain(`Some records look at the world – ${said(ontology.records.observe)} of every payment.`);
  expect(text).toContain(`Others copy another record – ${said(ontology.records.copy)}.`);
});

test('the posts quote Store 014 correctly', async ({ page, request }) => {
  const kpis = await kpiList(request);
  const k = (id: string) => kpis.find((x) => x.id === id)!.store_014;
  const shelf = finale.incidents.find((i: { id: string }) => i.id === 'shelf');
  const audit = ai.tests.domain[1].failing.find((a: { sku: string }) => a.sku === 'ATTA-WW-5KG');
  const runs = retail.agents.runs;
  const heroLog = (key: string) => runs[key].log.filter((x: { sku: string }) => x.sku === 'ATTA-WW-5KG');
  const [ask1, checked1] = heroLog('domain');
  const ep0 = (key: string) => runs[key].episodes.find((e: { start: string }) => e.start.startsWith('2026-06-10'));
  const seeds = retail.agents.seeds.runs;
  const made = ai.forecast.made_5kg.find((m: { date: string }) => m.date === '2026-06-10');
  const words: Record<number, string> = { 14: 'fourteen' };
  const at = (ts: string) => ts.slice(11, 16);

  const three = await articleText(page, 'store-014-ontology/');
  for (const e of [
    `On Tuesday 9 June, ${words[story.misplaced.cases]} cases of 5 kg atta were put away behind the rice, in the wrong bay.`,
    `On Wednesday at ${at(ep.start)} the shelf ran out, while the books showed ${ep.book_on_hand_max} bags.`,
    `after shoppers had come for ${ep.lost_units} bags they could not find`,
    `flags the empty shelf at ${at(shelf.joined.ts)}, three open hours after it emptied`,
  ]) expect(three, e).toContain(e);

  const four = await articleText(page, 'stock-has-a-place/');
  for (const e of [
    `Ask the books on Wednesday 10 June, and they say ${ep.book_on_hand_max} bags.`,
    `On Tuesday 9 June at ${at(story.misplaced.ts)}, ${words[story.misplaced.cases]} cases of 5 kg atta from the morning truck were put away behind the rice`,
    `On Wednesday at ${at(ep.start)} the shelf ran out. The books still showed ${ep.book_on_hand_max} bags.`,
    `On-shelf availability read ${k('osa').reported.value} for June, because the books showed stock in ${k('osa').reported.value} of open hours. The shelf had a bag in ${k('osa').observed.value} of them.`,
    `Days of supply read ${(ep.book_on_hand_max / made.naive).toFixed(1)} days – ${ep.book_on_hand_max} bags at ${made.naive.toFixed(1)} a day.`,
    `Since ${ep.book_on_hand_max} was above the reorder point of ${ep.reorder_point[1]}, nothing was ordered.`,
    `At the month-end count, ${retail.record_accuracy.wrong} of the ${retail.record_accuracy.items} items followed were wrong.`,
    `For 5 kg atta in June, that is ${k('osa').observed.value}, not ${k('osa').reported.value}.`,
    `found the 5 kg bay empty with ${audit.book} bags on the books`,
    `asked for a shelf check at ${at(ask1.ts)} on Wednesday. Staff found the bags at ${at(checked1.ts)} on Thursday, and the shelf was empty for ${Math.round(ep0('domain').empty_open_hours)} open hours instead of ${Math.round(ep0('none').empty_open_hours)}.`,
    `5 kg atta lost ${Math.round(seeds.none.mean.hero_lost_units)} bags on average with no agent and ${Math.round(seeds.domain.mean.hero_lost_units)} with the agent that knew where stock has to be`,
  ]) expect(four, e).toContain(e);
  expect(new Date(story.misplaced.ts).getUTCDay()).toBe(2); // a Tuesday
  expect(ask1.ts.startsWith('2026-06-10')).toBe(true); // Wednesday
  expect(checked1.ts.startsWith('2026-06-11')).toBe(true); // Thursday
  expect(retail.agents.seeds.n).toBe(40); // "forty simulated Junes"
  // "empty for nearly three days": Wednesday 15:48 to Saturday 10:00.
  const hours = (Date.parse(story.found.ts) - Date.parse(ep.start)) / 3.6e6;
  expect(hours).toBeGreaterThan(60);
  expect(hours).toBeLessThan(72);
});

test('the four addresses of the first plan still land', async ({ page }) => {
  for (const [from, to] of [['every-word/', 'what-is-an-ontology/'], ['glossary-to-graph/', 'what-is-an-ontology/'], ['four-kb-note/', 'why-ontology-matters/'], ['what-is-an-item/', 'ontology/']]) {
    await page.goto(from);
    await expect(page, from).toHaveURL(new RegExp(`/domain-series/${to}$`));
  }
});

test('previous and next stay within Season 2', async ({ page }) => {
  await page.goto('what-is-an-ontology/');
  await expect(page.locator('.pager a')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/why-ontology-matters/"]')).toHaveCount(1);
  await page.goto('store-014-ontology/');
  await expect(page.locator('.pager a[href$="/ontology-in-open-standards/"]')).toHaveCount(1);
  await page.goto('stock-has-a-place/');
  await expect(page.locator('.pager a[href$="/ontology-in-open-standards/"]')).toHaveCount(1);
  await page.goto('start-a-domain-ontology/');
  await expect(page.locator('.pager a')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/ontology-tools-in-the-market/"]')).toHaveCount(1);
  await page.goto('does-written-down-knowledge-help/');
  await expect(page.locator('.pager a[href$="/what-would-a-machine-draft/"]')).toHaveCount(1);
  await expect(page.locator('.pager a[href$="/the-auto-ontology-experiment-in-full/"]')).toHaveCount(1);
  await page.goto('who-saw-what/');
  await expect(page.locator('.pager a[href$="/what-is-an-ontology/"]')).toHaveCount(0);
  await page.goto('every-barrel/');
  await expect(page.locator('.pager a[href$="/stock-has-a-place/"]')).toHaveCount(0);
});

// The technical detour: the ontology in open standards. Its numbers come from the tools' own output
// (src/data/ontology-check.json, written by scripts/ontology/check.py and check.mjs), its code excerpts
// from the published files, and every file it offers is served.
test('the technical detour quotes the files and the tools correctly', async ({ page, request }) => {
  const text = await articleText(page, 'ontology-in-open-standards/');
  const c = check.counts;
  const py = check.shacl.python;
  const js = check.shacl.javascript;
  expect(c.things).toBe(ontology.things.length);
  expect(ontology.links.length).toBe(18);
  const props = c.object_properties + c.datatype_properties;
  for (const e of [
    `The ${c.things} things become OWL classes and the ${ontology.links.length} links become properties.`,
    `In all, ${c.classes} classes, ${props} properties and ${check.triples.ontology} triples.`,
    `That is ${check.triples.june} triples.`,
    `pySHACL found ${py.count} violations`,
    `Each one reads back to the same ${check.triples.ontology} triples.`,
    `found the same ${js.count} violations`,
  ]) expect(text, e).toContain(e);
  // Both validators agree, the formats round-trip, the reasoners did what the post says.
  expect(js.same_as_python).toBe(true);
  expect(js.count).toBe(py.count);
  for (const f of Object.values(check.formats) as { same_graph: boolean; triples: number }[]) {
    expect(f.same_graph).toBe(true);
    expect(f.triples).toBe(check.triples.ontology);
  }
  expect(check.hermit.consistent).toBe(true);
  expect(check.hermit.catches_sale_and_lost_sale).toBe(true);
  expect(check.owlrl.debit_returned_by_refund).toBe(true);
  // The list of violations is the tools' list, rule by rule.
  const byRule = new Map<number, number>();
  for (const v of py.violations) byRule.set(v.rule, (byRule.get(v.rule) ?? 0) + 1);
  expect([...byRule.keys()]).toEqual([1, 4, 5, 7, 8, 9, 10]);
  const items = await page.locator('article > ul').nth(1).locator('li').allInnerTexts();
  expect(items.map((t) => Number(t.match(/^Rule (\d+)/)![1]))).toEqual([...byRule.keys()]);
  expect(byRule.get(5)).toBe(2); // "the store's two count corrections"
  expect(byRule.get(8)).toBe(2); // "both deliveries"
  expect(byRule.get(10)).toBe(2); // "no bill number, and its debit has no approved payment"
  // The SPARQL answers.
  const [debit] = check.sparql.debit_without_approval.rows;
  const [clock] = check.sparql.refund_clock.rows;
  const [empty] = check.sparql.book_but_empty.rows;
  const inr = (v: string) => `₹${Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  expect(text).toContain(`It finds one debit – RRN ${debit.rrn}, ${inr(debit.amount)}, on bill ${debit.bill}.`);
  expect(check.sparql.debit_without_approval.rows).toHaveLength(1);
  expect(clock.fromDebit).toMatch(/^P7DT19H/);
  expect(clock.fromComplaint).toBe('P5D');
  expect(text).toContain('The refund came 7 days and 19 hours after the debit, and 5 days after the complaint.');
  expect(text).toContain(`the books showed ${empty.book} bags of 5 kg atta while a shelf check at ${empty.checked.slice(11, 16)} on 12 June saw none`);
  expect(empty.checked.startsWith('2026-06-12')).toBe(true);
  expect(empty.seen).toBe('0');
  // The code excerpts are the published files, give or take line breaks.
  const flat = (s: string) => s.replace(/\s+/g, ' ').trim();
  const files: Record<string, string> = {};
  const file = async (f: string) => (files[f] ??= flat(await (await request.get(`data/ontology/${f}`)).text()));
  const blocks = await page.locator('article pre').allInnerTexts();
  expect(blocks).toHaveLength(3);
  for (const stmt of flat(blocks[0]).split(/(?<=\.) (?=s14:)/)) expect(await file('store-014.ttl'), stmt).toContain(stmt);
  for (const stmt of flat(blocks[1]).split(/(?<=\.) (?=s14:)/)) expect(await file('store-014-shapes.ttl'), stmt).toContain(stmt);
  expect(await file('store-014-queries.rq')).toContain(flat(blocks[2]));
  // The network picture's description gives the graph page's own numbers.
  const g = check.graph;
  expect(g.classes).toBe(c.classes);
  expect(g.links).toBe(c.object_properties);
  expect([g.borrowed, g.things]).toEqual([2, 5]); // "Two dark blue circles", "five dashed circles"
  expect(g.circles).toBe(g.classes + g.borrowed + g.things);
  expect(g.arrows).toBe(g.links + g.subclass);
  const alt = await page.locator('article figure.picture img[src$="network-graph.png"]').getAttribute('alt');
  for (const e of [`${g.classes} classes are circles`, 'Two dark blue circles', 'five dashed circles mark Thing',
    `${g.arrows} arrows join them: ${g.links} links and ${g.subclass} subclass arrows.`]) expect(alt, e).toContain(e);
  // Every file it offers is served, and the tool versions it names are the ones used.
  const hrefs = await page.locator('.ontology-files li a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')!));
  expect(hrefs).toHaveLength(10);
  for (const h of hrefs) expect((await request.head(h.replace('/domain-series/', ''))).status(), h).toBe(200);
  for (const [tool, v] of Object.entries(check.tools) as [string, string][]) {
    const name = { rdflib: 'rdflib', pyshacl: 'pySHACL', owlrl: 'owlrl', owlready2: 'Owlready2', pyoxigraph: 'pyoxigraph', pylode: 'pyLODE', n3: 'N3.js', 'rdf-validate-shacl': 'rdf-validate-shacl', 'vis-network': 'vis-network' }[tool];
    expect(text, tool).toContain(`${name} ${v}`);
  }
});

test('the interactive graph draws every class and link in the file, and says what each one is', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('data/ontology/store-014-graph.html');
  await expect(page.locator('body')).toHaveAttribute('data-ready', '1', { timeout: 60_000 });
  const g = check.graph;
  const c = check.counts;
  expect(await page.evaluate('[network.body.data.nodes.length, network.body.data.edges.length]')).toEqual([g.circles, g.arrows]);
  await expect(page.locator('#footer')).toContainText(
    `Drawn by vis-network ${check.tools['vis-network']} from store-014.ttl: ${c.classes} classes, ${c.object_properties} object properties, `
    + `${c.datatype_properties} data fields and ${check.triples.ontology} triples.`);
  // Click the Item circle: its description, key and links come from the file.
  const at = (await page.evaluate("network.canvasToDOM(network.getPositions(['s14:Item'])['s14:Item'])")) as { x: number; y: number };
  const box = (await page.locator('#graph').boundingBox())!;
  await page.mouse.click(box.x + at.x, box.y + at.y);
  const details = page.locator('#details');
  await expect(details.locator('h2')).toHaveText('Item');
  await expect(details).toContainText('GTIN: string – the key: two with the same value are the same thing');
  await expect(details).toContainText('Case → holds item');
  expect(errors).toEqual([]);
});

// Posts 6 to 15 quote their rules word for word from the ontology, and every number they give can be found
// in the Season 1 posts they draw on (which their own tests pin to the world's data), in the KPI list, or in
// the tools' output for the technical detour. A number typed wrong, or one with no source, fails here.
const DRAWS_ON: Record<string, string[]> = {
  'demand-is-not-sales': ['sales', 'lost-sales', 'forecast-accuracy', 'retail'],
  'a-correction-needs-a-reason': ['shrink'],
  'waste-and-the-empty-shelf': ['fresh-waste'],
  'an-item-is-the-pack': ['pick-accuracy', 'fill-rate', 'otif', 'logistics'],
  'a-delivery-ends-on-the-shelf': ['on-time-arrival', 'otif', 'logistics'],
  'four-corrections-one-mistake': ['net-adjustments', 'pick-accuracy', 'logistics'],
  'a-payment-has-three-witnesses': ['payment-success', 'technical-declines', 'payments'],
  'one-bill-one-payment': ['charged-twice', 'match-rate', 'payments'],
  'the-refund-clock': ['refund-turnaround', 'payments'],
  'what-would-a-machine-draft': ['store-014-ontology', 'who-saw-what'],
  'does-written-down-knowledge-help': ['what-would-a-machine-draft'],
  'the-auto-ontology-experiment-in-full': ['what-would-a-machine-draft'],
  'ontology-tools-in-the-market': ['what-would-a-machine-draft'],
  'start-a-domain-ontology': ['who-saw-what', 'store-014-ontology'],
};
// Not data: rule numbers and pack sizes, the year, the store's name and the date under the title. Post 15
// also gives the similarity range, issue and acceptance date of the study it cites.
const NOT_DATA = new Set([...Array.from({ length: 13 }, (_, i) => String(i)), '2026', '014', '18']);
const OUTSIDE: Record<string, string[]> = {
  'what-would-a-machine-draft': ['21', '19', '2.0'], // NVIDIA's announcement date, the repository's read date, its licence
  'ontology-tools-in-the-market': ['2.0', '2604.25149'], // the Apache licence version, the study's arXiv number
  'start-a-domain-ontology': ['0.5', '0.8', '17', '30', '2.0'],
};

test('posts 6 to 19 quote their rules from the ontology and their numbers from Season 1', async ({ page, request }) => {
  const numbers = (s: string) => new Set((s.replace(/[₹+−]/g, '').match(/\d[\d,]*(?:\.\d+)?%?/g) ?? []).map((n) => n.replace(/,+$/, '')));
  const known = await (await request.get('kpis/domain-kpis.yaml')).text() + JSON.stringify(check);
  const later = ON_POSTS.filter((x) => x.n >= 6);
  expect(later.map((x) => x.slug)).toEqual(Object.keys(DRAWS_ON));
  for (const p of later) {
    const text = await articleText(page, `${p.slug}/`);
    for (const n of p.rules ?? []) {
      const rule = ontology.rules.find((r: { n: number }) => r.n === n);
      expect(text, `${p.slug} rule ${n}`).toContain(`Rule ${n} – ${rule.text.replace(/[“”]/g, '"')}`);
    }
    const runs = ['does-written-down-knowledge-help', 'the-auto-ontology-experiment-in-full', 'ontology-tools-in-the-market'];
    let sources = known + (p.slug === 'what-would-a-machine-draft' ? JSON.stringify(machineRun) : '') + (runs.includes(p.slug) ? JSON.stringify(claudeAgents) + JSON.stringify(machineRun) + JSON.stringify(owlShacl) + JSON.stringify(sweep) + JSON.stringify(repeat) : '');
    for (const s of DRAWS_ON[p.slug]) sources += ` ${await articleText(page, `${s}/`)}`;
    const found = numbers(sources);
    for (const n of numbers(text)) {
      if (NOT_DATA.has(n) || OUTSIDE[p.slug]?.includes(n)) continue;
      expect(found.has(n) || found.has(n.replace('%', '')), `${p.slug}: ${n}`).toBe(true);
    }
  }
  // The two answers the payments posts take from the detour's SPARQL questions.
  const [debit] = check.sparql.debit_without_approval.rows;
  const inr = (v: string) => `₹${Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  expect(await articleText(page, 'one-bill-one-payment/')).toContain(`It found her: RRN ${debit.rrn}, ${inr(debit.amount)}, on bill ${debit.bill}.`);
  expect(await articleText(page, 'the-refund-clock/')).toContain('The refund came 7 days and 19 hours after the debit, and 5 days after the complaint.');
  expect(check.sparql.refund_clock.rows[0].fromDebit).toMatch(/^P7DT19H/);
  expect(check.sparql.refund_clock.rows[0].fromComplaint).toBe('P5D');
});

// Post 15, for everyone: the KPIs it quotes come from the KPI list, the drafts from the run's record, and the
// book stock's description from the draft the machine wrote.
test('post 15 quotes the KPIs, the drafts and the answers as recorded', async ({ page, request }) => {
  const text = await articleText(page, 'what-would-a-machine-draft/');
  const kpis = await kpiList(request);
  const osa = kpis.find((k) => k.id === 'osa')!.store_014;
  const lost = kpis.find((k) => k.id === 'lost-sales')!.store_014;
  expect(text).toContain(`The books said ${osa.reported.value}. The shelf had a bag ${osa.observed.value} of the time.`);
  expect(text).toContain(`on-shelf availability came to read ${osa.reported.value}.`);
  expect(lost.observed.value).toBe('157 bags');
  expect(text).toContain('we could count the lost bags – 157 of them – only because Store 014 is a simulation');
  expect(text).toContain(`I ran it on Store 014's ${machineRun.run.tables} tables of June records.`);
  expect(text).toContain(`On a small free AI model, the draft took ${machineRun.run.draft_minutes} minutes and named ${machineRun.term_count} things`);
  const n = machineRun.with_nvidia_models;
  expect(text).toContain(`On NVIDIA's own model, it took ${n.draft_minutes} minutes and named ${n.term_count}, one for each table.`);
  // The small model's draft called the book stock a count.
  const terms = JSON.parse(readFileSync(new URL('../../public/data/auto-ontology/store014-draft-terms.json', import.meta.url), 'utf8')) as { name: string; description?: string }[];
  expect(terms.some((t) => /final count of stock/.test(t.description ?? ''))).toBe(true);
  expect(text).toContain('described the book stock as "the final count of stock" for the day.');
  // Neither draft named the two things no table holds.
  expect(machineRun.terms_naming_the_gap).toEqual([]);
  expect(n.terms_naming_the_gap).toEqual([]);
  expect(text).toContain('Two things, in both drafts.');
  // The answers: 660 on the draft alone, then Nemotron's 567, 2 and 3.
  type A = { id: string; rerun_on_store014: string[][] | null };
  const by = (list: A[], id: string) => list.find((a) => a.id === id)!;
  expect(by(machineRun.with_a_7b_model.draft_alone, 'sold').rerun_on_store014).toEqual([['660']]);
  expect(text).toContain('A small model said 660 bags were sold – the bags the warehouse delivered, not the bags shoppers bought.');
  expect(by(n.before, 'sold').rerun_on_store014).toEqual([[`${retailSoldJune()}`]]);
  expect(by(n.before, 'left-without').rerun_on_store014).toEqual([['2']]);
  expect(by(n.before, 'lost-sales').rerun_on_store014).toEqual([['3']]);
  expect(text).toContain(`NVIDIA's model got the bags sold right, ${retailSoldJune()}, and then said 2 shoppers walked away`);
  expect(n.coverage_before.every((c: { coverage: number }) => c.coverage === 1)).toBe(true);
  expect(text).toContain("The tool's own check said every question was covered.");
});

// Post 17 reports every run of Auto-Ontology on Store 014. Each claim in its runs sections is pinned to the run's
// record (src/data/auto-ontology-run.json), and the record's answers are pinned to the data.
test('post 17 reports the Store 014 run on the small model as recorded', async ({ page, request }) => {
  const text = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  const run = machineRun.run;
  expect(run.chat_model).toMatch(/^qwen3:4b/);
  expect(text).toContain('Run 6 used Qwen3 4B, at 4 bits, for drafting and answering.');
  expect(text).toContain(`Store 014's ${run.tables} tables of June records`);
  expect(text).toContain(`The draft took ${run.draft_minutes} minutes and named ${machineRun.term_count} terms`);
  // Ten product terms, one per table that holds a SKU.
  expect(machineRun.product_terms).toHaveLength(10);
  expect(text).toContain('It named the product ten times');
  // Four joins, all from the goods receipts, a fifth thrown out, and none between the till and UPI.
  expect(run.compile.joins_inferred).toEqual(['0', '4']);
  expect(run.compile.joins.every((j: string) => j.startsWith('goods_receipts.'))).toBe(true);
  expect(run.compile.joins.map((j: string) => j.split(' -> ')[1].split('.')[0]).sort()).toEqual(['pallets', 'products', 'shipments']);
  expect(run.compile.joins_rejected).toEqual(['goods_receipts.units_booked']);
  expect(text).toContain('It found four joins, all from the goods receipts – to the shipment, the pallet and the product.');
  expect(text).toContain('A fifth, from units_booked, was thrown out by its own check against the data.');
  expect(run.compile.sql_attributes_from_history).toBe('0');
  expect(text).toContain('It suggested no calculations');
  expect(run.ossie_export_refused).toContain('candidates: goods_receipt_line, goods_receipt_note');
  expect(text).toContain('Apache Ossie refused the export, because goods_receipts.asn_sku mapped to two terms, Goods Receipt Line and Goods Receipt Note.');
  // No term named for demand or a lost sale; demand only inside two descriptions.
  expect(machineRun.terms_naming_the_gap).toEqual([]);
  expect(machineRun.descriptions_mentioning_the_gap).toEqual(['Forecast Variability', 'Reorder Point']);
  expect(text).toContain('No term was named for demand or a lost sale. Demand came up only inside two descriptions');
  // The coverage check said every question was covered.
  expect(machineRun.coverage.length).toBeGreaterThan(0);
  expect(machineRun.coverage.every((c: { coverage: number }) => c.coverage === 1)).toBe(true);
  expect(text).toContain('The coverage check said every question was covered, including the two no table can answer.');
  // The agent answered none, though its query for the bags sold was right.
  const asked = machineRun.answers as { id: string; answer: string; sql: string | null; truth: string[][] | null }[];
  expect(asked).toHaveLength(4);
  expect(asked.every((a) => a.answer.startsWith("I couldn't write a query"))).toBe(true);
  const sold = asked.find((a) => a.id === 'sold')!;
  expect(sold.truth).toEqual([[`${retailSoldJune()}`]]);
  expect(text).toContain(`For the bags sold it ran the right query – ${retailSoldJune()} from the daily sales – but answered in plain text and never called submit`);
  // The files box links to files that are there.
  for (const f of ['store014-draft-terms.json', 'store014-run.json']) {
    expect((await request.get(`data/auto-ontology/${f}`)).status()).toBe(200);
  }
});

// Runs 7 and 8: the 7B model on the draft alone, then before and after the knowledge layer went in. Each claim
// is pinned to the record, and each number to the answer's own query re-run on the records.
test('post 17 reports the 7B runs and the knowledge layer as recorded', async ({ page, request }) => {
  const text = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  const w = machineRun.with_a_7b_model;
  type A = { id: string; answer: string | null; sql: string | null; rerun_on_store014: string[][] | null };
  const by = (list: A[], id: string) => list.find((a) => a.id === id)!;
  expect(w.answer_model).toMatch(/^qwen2\.5:7b/);
  expect(text).toContain('Runs 7 and 8 kept the 4B draft and put Qwen2.5 7B on the answers.');
  // On the draft alone.
  const alone = by(w.draft_alone, 'sold');
  expect(alone.sql).toContain('units_booked');
  expect(alone.sql).toContain('store.goods_receipts');
  expect(alone.rerun_on_store014).toEqual([['660']]);
  const aloneShelf = by(w.draft_alone, 'on-shelf');
  expect(aloneShelf.sql).toContain('store.goods_receipts');
  expect(aloneShelf.rerun_on_store014?.[0][1]).toBe('11');
  expect(text).toContain('one run said 660 bags sold – SUM(units_booked) from the goods receipts – and gave on-shelf availability as "11 units received", which was 11 receipt rows.');
  expect(by(w.before, 'sold').rerun_on_store014).toEqual([[`${retailSoldJune()}`]]);
  const left = by(w.before, 'left-without');
  expect(left.sql).toContain('store.inventory_book');
  expect(left.rerun_on_store014).toEqual([['28']]);
  const osa = by(w.before, 'on-shelf');
  expect(osa.sql).toContain('warehouse.pick_confirmations');
  expect(osa.sql).toContain('AVG(');
  expect(osa.sql).toContain('cases_confirmed');
  expect(w.before_on_shelf_percent).toBe('1.43%');
  expect(text).toContain("gave 28 shoppers who left without – COUNT(*) of the book-stock rows, one a day – and on-shelf availability of 1.43%, AVG(cases_confirmed) over SUM(cases_ordered) from the warehouse's picks.");
  // What went in.
  expect(w.entered.rules_quoted).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  expect(w.entered.glossary.length).toBe(8);
  expect(w.entered.calculations.map((c: { status: string }) => c.status)).toEqual(['added', 'added', 'added', 'added']);
  expect(w.entered.analyses.map((c: { status: string }) => c.status)).toEqual(['added', 'added', 'added']);
  expect(w.entered.tables_certified).toEqual([]);
  expect(text).toContain('Eight codes: OSA, SKU, GTIN, SSCC, RRN, UPI, ASN and GRN');
  expect(text).toContain('None went in on the earlier runs. The API answered in a shape the code did not expect.');
  expect(machineRun.table_descriptions_rerun.certified).toBe(20);
  expect(text).toContain('After the fix, 20 of the 21 tables went in on run 13');
  // After.
  const sold = by(w.after, 'sold');
  expect(sold.sql).toContain('store.pos_lines');
  expect(sold.sql).toContain('gtin');
  expect(sold.rerun_on_store014).toEqual([[`${retailSoldJune()}`]]);
  expect(text).toContain(`${retailSoldJune()} from pos_lines joined to products on the GTIN.`);
  const shelf = by(w.after, 'on-shelf');
  expect(shelf.sql).toBeFalsy();
  expect(shelf.answer).toContain("'on shelf'");
  expect(text).toContain("On-shelf availability as the share of shelf audits with status 'on shelf', but with no SQL and no number.");
  expect(by(w.after, 'left-without').rerun_on_store014).toEqual([[`${retailSoldJune()}`]]);
  expect(text).toContain(`The shoppers who left without were answered with the ${retailSoldJune()} bags sold.`);
  const lost = by(w.after, 'lost-sales');
  expect(lost.sql).toContain('no_sales_days');
  expect(lost.rerun_on_store014).toEqual(w.days_with_sales);
  expect(w.days_with_sales).toEqual([['24']]);
  expect(text).toContain('"Estimated lost sales 24" came from a CTE named no_sales_days that in fact listed the days with sales – 24 of the 28.');
  expect(w.coverage_after.every((c: { coverage: number }) => c.coverage === 1)).toBe(true);
  expect(text).toContain('every question covered, before and after. After, it at least matched the right things.');
  // The knowledge layer as entered is the published file, rule 3 quoted from it.
  const instructions = readFileSync(new URL('../../public/data/auto-ontology/store014-expert-instructions.txt', import.meta.url), 'utf8');
  expect(instructions).toContain('If asked how many shoppers left without an item, or for lost sales, do not count goods receipts, shelf audits, forecasts or write-offs as shoppers or sales. Say that no record holds them, and if you estimate them, say how.');
  expect(text).toContain('If asked how many shoppers left without an item, or for lost sales, do not count goods receipts, shelf audits, forecasts or write-offs as shoppers or sales. Say that no record holds them, and if you estimate them, say how.');
  expect((await request.get('data/auto-ontology/store014-expert-instructions.txt')).status()).toBe(200);
});

// Run 10: Nemotron drafting and answering, with the local embeddings the other runs used.
test('post 17 reports the run on NVIDIA\'s own model as recorded', async ({ page, request }) => {
  const text = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  const n = machineRun.with_nvidia_models;
  type A = { id: string; answer: string | null; sql: string | null; rerun_on_store014: string[][] | null; truth: string[][] | null };
  const by = (list: A[], id: string) => list.find((a) => a.id === id)!;
  expect(n.chat_model).toBe('nvidia/nemotron-3.5-lightning-30b-a3b');
  expect(n.embedding_model).toMatch(/^nomic-embed-text/);
  expect(machineRun.run.embedding_model).toMatch(/^nomic-embed-text/);
  expect(text).toContain(`Run 10 used Nemotron 3.5 Lightning (${n.chat_model}) for drafting and answering, with the same local embeddings as before`);
  // The draft: one term per table, none for the gap, three joins to the shipments, none for the till and UPI.
  expect(n.draft_minutes).toBe(10);
  expect(n.term_count).toBe(machineRun.run.tables);
  expect(n.terms.every((t: { tables: string[] }) => t.tables.length === 1 || t.tables.includes('warehouse.shipments'))).toBe(true);
  expect(text).toContain(`It drafted in ${n.draft_minutes} minutes and named ${n.term_count} terms, one for each table`);
  expect(n.terms_naming_the_gap).toEqual([]);
  expect(n.descriptions_mentioning_the_gap).toEqual([]);
  expect(text).toContain('No term or description named demand or a lost sale.');
  expect(n.compile.joins_inferred).toEqual(['0', '3']);
  expect(n.compile.joins.map((j: string) => j.split(' -> ')[1])).toEqual(['shipments.shipment_id', 'shipments.shipment_id', 'shipments.shipment_id']);
  expect(n.compile.joins.map((j: string) => j.split('.')[0]).sort()).toEqual(['goods_receipts', 'pallets', 'pick_confirmations']);
  expect(n.compile.joins_rejected).toEqual(['customer_complaints.bill_id', 'upi_refunds.bill_id']);
  expect(n.compile.joins_considered.some((j: string) => /pos_payments|psp_upi_report/.test(j))).toBe(false);
  expect(text).toContain("It found three joins, all to warehouse.shipments.shipment_id – from goods_receipts, pallets and pick_confirmations – rejected customer_complaints.bill_id and upi_refunds.bill_id, and never considered a join between the till's payments and UPI's report.");
  expect(n.ossie_export_refused).toBeNull();
  expect(text).toContain('The Ossie export went through.');
  // On the draft alone: the two the records can answer, right; the two they cannot, answered anyway.
  expect(by(n.before, 'sold').rerun_on_store014).toEqual([[`${retailSoldJune()}`]]);
  const shelf = by(n.before, 'on-shelf');
  expect(shelf.rerun_on_store014).toEqual([['8', '6', '75.00']]);
  expect(shelf.truth).toEqual([['6 of 8']]);
  const left = by(n.before, 'left-without');
  expect(left.sql).toContain('store.shelf_audits');
  expect(left.sql).toContain("status = 'empty'");
  expect(left.rerun_on_store014).toEqual([['2']]);
  const lost = by(n.before, 'lost-sales');
  expect(lost.sql).toContain('store.write_offs');
  expect(lost.rerun_on_store014).toEqual([['3']]);
  const writeOffs = readFileSync(new URL('../../public/data/india-grocery/write-offs-june.csv', import.meta.url), 'utf8')
    .trim().split(/\r?\n/).slice(1).map((l) => l.split(',')).filter((r) => r[1] === 'ATTA-WW-5KG');
  expect(writeOffs.reduce((s, r) => s + Number(r[2]), 0)).toBe(3);
  expect(writeOffs.every((r) => r[3] === 'damaged')).toBe(true);
  expect(text).toContain(`${retailSoldJune()} from the daily sales and 75% from the shelf audits, both right. The shoppers who left without became 2 – the shelf audits with status 'empty' – and the lost sales became 3, the bags written off as damaged.`);
  // After the knowledge layer: the same two right, and the two gaps named as gaps.
  expect(n.entered.rules_quoted).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  expect(by(n.after, 'sold').rerun_on_store014).toEqual([[`${retailSoldJune()}`]]);
  expect(by(n.after, 'on-shelf').rerun_on_store014?.[0].slice(0, 2)).toEqual(['8', '6']);
  const leftAfter = by(n.after, 'left-without');
  expect(leftAfter.answer).toContain('No table records shoppers who left without the item');
  expect(leftAfter.rerun_on_store014).toEqual([['2', `${retailSoldJune()}`]]);
  const lostAfter = by(n.after, 'lost-sales');
  expect(lostAfter.answer).toContain("are not stored in any table per the organization's rules");
  expect(lostAfter.rerun_on_store014).toEqual([['empty_shelf_audits', '2'], ['units_sold', `${retailSoldJune()}`]]);
  expect(text).toContain('For the shoppers: "No table records shoppers who left without the item", with the two empty audits and the 567 bags sold.');
  expect(text).toContain(`For the lost sales: "not stored in any table per the organization's rules", with the same two figures.`);
  expect(n.coverage_before.every((c: { coverage: number }) => c.coverage === 1)).toBe(true);
  expect(n.coverage_after.every((c: { coverage: number }) => c.coverage === 1)).toBe(true);
  expect((await request.get('data/auto-ontology/store014-nemotron-draft-terms.json')).status()).toBe(200);
});

// Bags of 5 kg atta the till lines show sold, 1 to 28 June, from the published records.
function retailSoldJune() {
  const lines = readFileSync(new URL('../../public/data/india-grocery/pos-lines-may-june.csv', import.meta.url), 'utf8').trim().split('\n');
  const head = lines[0].split(',');
  const [ts, sku, qty] = ['bill_ts', 'sku_scanned', 'qty'].map((c) => head.indexOf(c));
  return lines.slice(1).map((l) => l.split(',')).filter((r) => r[sku] === 'ATTA-WW-5KG' && r[ts] >= '2026-06-01' && r[ts] < '2026-07-01').reduce((n, r) => n + Number(r[qty]), 0);
}

// Posts 16 and 17: the same four questions put to NVIDIA's model and six fresh Claude agents. The answers
// the agents gave are pinned to the file, and what they were checked against to the records.
test('posts 16 and 17 report the Claude agents and Nemotron as recorded', async ({ page }) => {
  const a = claudeAgents;
  expect(a.truth.sold).toBe(retailSoldJune());
  expect(a.truth.on_shelf / a.truth.audits * 100).toBe(a.truth.availability_pct);
  expect(a.agents.map((x: { model: string; knowledge: boolean }) => `${x.model} ${x.knowledge}`)).toEqual(
    ['Haiku false', 'Haiku true', 'Sonnet false', 'Sonnet true', 'Opus false', 'Opus true']);
  for (const x of a.agents) {
    expect(x.sold, `${x.model} sold`).toBe(a.truth.sold);
    expect(x.availability_pct, `${x.model} availability`).toBe(a.truth.availability_pct);
  }
  // "Honest" means the answer starts with "no record" for both unanswerable questions, or for one of them.
  for (const x of a.agents) {
    const said = [x.shoppers, x.lost].filter((t: string) => t.startsWith('no record') && !/\d/.test(t.replace(/two|29 and 30 June/g, '')));
    expect(said.length, `${x.model} ${x.knowledge}`).toBe(x.honest);
  }
  expect(a.nemotron.map((x: { honest: number }) => x.honest)).toEqual([0, 2]);
  const sonnet = a.agents.filter((x: { model: string }) => x.model === 'Sonnet');
  expect(sonnet.every((x: { honest: number }) => x.honest === 2)).toBe(true);
  const haiku = a.agents.find((x: { model: string; knowledge: boolean }) => x.model === 'Haiku' && x.knowledge)!;
  expect(haiku.shoppers).toContain('43 to 84 shoppers, from forecasts');

  const simple = await articleText(page, 'does-written-down-knowledge-help/');
  expect(simple).toContain('Two have answers in the records: 567 bags were sold, and staff found the atta on the shelf in six of eight checks – 75%.');
  expect(simple).toContain("Without the knowledge layer, NVIDIA's model gave real numbers from the wrong records: 2 shoppers, which were really the two empty-shelf checks, and 3 lost bags, which were really bags thrown away as damaged.");
  expect(simple).toContain('With it, the same model said no record holds them, and gave what the records do show – the two empty checks and the 567 bags sold.');
  expect(simple).toContain('Asked how many shoppers walked away, it gave the 567 bags sold.');
  expect(simple).toContain('Sonnet said "no record" with or without the knowledge layer.');
  expect(simple).toContain('took a sales forecast and called it 43 to 84 shoppers, even with the knowledge layer in front of it.');
  expect(simple).toContain(`I also gave ${sweep.models_run} AI models the knowledge as formal OWL and SHACL files instead of plain words.`);
  expect(simple).toContain('When no record holds the answer, say so, and if you estimate, say how.');

  const full = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  expect(full).toContain(`The draft took ${a.draft.small_model.minutes} minutes and named ${a.draft.small_model.terms} terms`);
  expect(full).toContain(`drafted in ${a.draft.nvidia.minutes} minutes and named ${a.draft.nvidia.terms} terms, one for each table`);
  expect(full).toContain('answered 503 and 504 for over an hour');
  expect(full).toContain('The till data ends on 28 June, so 29 and 30 June are not in the database.');
  expect(a.truth.data_ends).toBe('28 June');
  expect(full).toContain('Sonnet said no record holds the shoppers or the lost sales, both times.');
  expect(full).toContain('a model of 90 to 110 bags from the draft alone, and an estimate of 160 to 170 with the knowledge layer');
});

// Post 17 also reports two automatic routes to OWL and SHACL, pinned to src/data/auto-ontology-owl-shacl.json,
// and what Opus noticed, pinned to the file it wrote.
test('post 17 reports Ontop and the two Claude agents writing OWL and SHACL as recorded', async ({ page, request }) => {
  const text = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  const o = owlShacl.ontop;
  expect(text).toContain(`It wrote ${o.classes} classes, one for each table, and ${o.datatype_properties} data properties, one for each column. It wrote ${o.object_properties} object properties`);
  expect(text).toContain(`${o.triples} triples`);
  const [opus, sonnet] = owlShacl.agents;
  expect(text).toContain(`Opus wrote ${opus.classes} classes, ${opus.object_properties} object properties, ${opus.datatype_properties} data properties, ${opus.node_shapes} SHACL node shapes and ${opus.sparql_rules} rules`);
  expect(text).toContain(`Sonnet wrote ${sonnet.classes} classes, ${sonnet.object_properties} object properties, ${sonnet.datatype_properties} data properties and ${sonnet.node_shapes} node shapes`);
  expect(text).toContain('Neither listed demand or a lost sale.');
  expect(opus.lists_demand_or_lost_sale_as_missing || sonnet.lists_demand_or_lost_sale_as_missing).toBe(false);
  // What Opus noticed, read from its own file.
  const ttl = readFileSync(new URL('../../public/data/auto-ontology/store014-opus-ontology.ttl', import.meta.url), 'utf8');
  const seen = owlShacl.opus_noticed;
  expect(ttl).toContain('book (computed) stock');
  expect(ttl).toContain(`for ${seen.timeouts_matched_to_upi_report} 'failed: no response' attempts with no RRN`);
  expect(ttl).toContain(seen.forecast_method_seen);
  expect(text).toContain(`It described the book stock as "${seen.book_stock}", it matched the ${seen.timeouts_matched_to_upi_report} till attempts that ended in 'failed: no response' to UPI's report`);
  expect(readFileSync(new URL('../../public/data/auto-ontology/store014-sonnet-ontology.ttl', import.meta.url), 'utf8')).toContain(`:${owlShacl.sonnet_named_till_lines} a owl:Class`);
  // The five files are served.
  for (const f of ['ontop-ontology.owl', 'opus-ontology.ttl', 'opus-shapes.ttl', 'sonnet-ontology.ttl', 'sonnet-shapes.ttl']) {
    expect((await request.get(`data/auto-ontology/store014-${f}`)).status(), f).toBe(200);
  }
  // Post 19 says the same about the book stock.
  expect(await articleText(page, 'start-a-domain-ontology/')).toContain('Opus noticed that the book stock is computed, not counted.');
});

// Posts 17 and 18 report the same questions put to fourteen models: the automated score as it was recorded, and
// the score from reading every answer (src/data/auto-ontology-model-sweep.json, reviewed), whose totals must
// follow from its per-run records.
test('posts 17 and 18 report the model sweep as recorded, and as read answer by answer', async ({ page, request }) => {
  const text = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  const t = sweep.totals;
  expect(t.plain.honest + t.plain.invented + t.plain.no_answer + t.plain.error + t.rule.honest + t.rule.invented + t.rule.no_answer + t.rule.error).toBe(sweep.runs);
  expect(sweep.models.length).toBe(sweep.models_run);
  expect(text).toContain(`That made ${sweep.runs} runs.`);
  expect(text).toContain(`to ${sweep.models_run} models.`);
  expect(text).toContain(`It found ${t.plain.honest} honest runs as they were, and ${t.rule.honest} with the line.`);
  expect(text).toContain(sweep.prompt.base_line);

  type R = { model: string; pack: string; rule_line: boolean; automated: string; queries: number; turn_cap: number; answered?: boolean; why_not?: string;
    q1_sold?: string; q2_shoppers?: string; q3_on_shelf?: string; q4_lost_sales?: string; all_four_right: boolean; no_record_on_both: boolean; answers: Record<string, string | null> };
  const rev = sweep.reviewed;
  const runs = rev.runs as R[];
  expect(runs).toHaveLength(sweep.runs);
  for (const [cond, rule] of [['plain', false], ['rule', true]] as const) {
    const rows = runs.filter((r) => r.rule_line === rule);
    const answered = rows.filter((r) => r.answered !== false);
    expect(rows.length).toBe(rev[cond].runs);
    expect(rows.filter((r) => r.all_four_right).length, cond).toBe(rev[cond].all_four_right);
    expect(rows.filter((r) => r.no_record_on_both).length, cond).toBe(rev[cond].no_record_on_both);
    expect(rows.filter((r) => r.answered === false).length, cond).toBe(rev[cond].no_final_answer);
    for (const r of answered) {
      expect(r.all_four_right, `${r.model} ${r.pack} ${rule}`).toBe(r.q1_sold === 'right' && r.q3_on_shelf === 'right' && r.q2_shoppers === 'no_record' && r.q4_lost_sales === 'no_record');
      // An answer read as right says 567 or 75%.
      if (r.q1_sold === 'right') expect(r.answers['1'], `${r.model} ${r.pack}`).toContain(`${retailSoldJune()}`);
      if (r.q3_on_shelf === 'right') expect(r.answers['3'], `${r.model} ${r.pack}`).toMatch(/\b75(\.0+)?%/);
    }
    // The automated score's runs line up with the reviewed ones, model by model.
    const auto = sweep.models.map((m: { model: string; plain: Record<string, number>; rule: Record<string, number> }) => [m.model, m[cond]] as const);
    for (const [model, counts] of auto) {
      const mine = rows.filter((r) => r.model === model);
      expect(mine.length, model).toBe(counts.honest + counts.invented + counts.no_answer + counts.error);
      expect(mine.filter((r) => r.automated === 'honest').length, model).toBe(counts.honest);
    }
  }
  for (const [name, m] of Object.entries(rev.per_model) as [string, { runs: number; all_four_right: number; plain: number; rule: number }][]) {
    const rows = runs.filter((r) => r.model === name);
    expect(rows.length, name).toBe(m.runs);
    expect(rows.filter((r) => r.all_four_right && !r.rule_line).length, name).toBe(m.plain);
    expect(rows.filter((r) => r.all_four_right && r.rule_line).length, name).toBe(m.rule);
  }
  expect(rev.rule.all_four_right).toBeGreaterThan(rev.plain.all_four_right);
  expect(text).toContain(`The line still did the work: ${rev.plain.all_four_right} runs all four right as it was, ${rev.rule.all_four_right} with the line.`);
  // Where reading changed the automated score: a refusal in other words, and runs that refused every question.
  const run = (model: string, pack: string, rule: boolean) => runs.find((r) => r.model === model && r.pack === pack && r.rule_line === rule)!;
  const ultra = run('Nemotron 3 Ultra', 'auto-opus', false);
  expect(ultra.automated).toBe('invented');
  expect(ultra.all_four_right).toBe(true);
  expect(ultra.answers['2']).toBe('Cannot be determined from available data.');
  expect(text).toContain(`Nemotron 3 Ultra's "${ultra.answers['2']!.replace(/\.$/, '')}"`);
  const qwen = runs.filter((r) => r.model.startsWith('Qwen') && r.rule_line);
  expect(qwen.every((r) => r.automated === 'honest' && r.q1_sold === 'refused' && !r.all_four_right)).toBe(true);
  // Super with the Sonnet pack ran no query and made up a month.
  const superSonnet = runs.filter((r) => r.model === 'Nemotron 3.5 Super' && r.pack === 'auto-sonnet');
  expect(superSonnet.every((r) => r.queries === 0 && r.q1_sold === 'wrong')).toBe(true);
  expect(superSonnet.map((r) => r.answers['1']).join(' ')).toContain('1,840');
  expect(text).toContain('1,840 bags sold, 2,360 shoppers');
  // Why runs gave no final answer, and the turn caps.
  const why = rev.why_no_final_answer as Record<string, number>;
  expect(Object.values(why).reduce((s, n) => s + n, 0)).toBe(rev.plain.no_final_answer + rev.rule.no_final_answer);
  expect(runs.filter((r) => r.model === 'Mistral Large 4').every((r) => r.why_not === 'stopped with an empty reply')).toBe(true);
  expect(text).toContain(`${why['stopped with an empty reply']} stopped with an empty reply – including all six of Mistral Large 4's`);
  expect(runs.filter((r) => r.turn_cap === 16).length).toBe(rev.turn_caps['16']);
  expect(text).toContain(`which covers ${rev.turn_caps['16']} of the ${sweep.runs} runs.`);
  // The CSV: one row per run, with what the review read.
  const csv = await (await request.get('data/auto-ontology/store014-model-sweep.csv')).text();
  const lines = csv.trim().split('\n');
  expect(lines.length - 1).toBe(sweep.runs);
  expect(lines[0]).toContain('reviewed_all_four_right');

  // Post 18 says the same in plain words.
  const choose = await articleText(page, 'ontology-tools-in-the-market/');
  expect(choose).toContain(`That made ${sweep.runs} runs, most of them on NVIDIA's free service.`);
  expect(choose).toContain(`Only ${rev.plain.all_four_right} of the ${rev.plain.runs} runs without the extra sentence got all four answers right`);
  expect(choose).toContain(`With the sentence, ${rev.rule.all_four_right} of ${rev.rule.runs} did.`);
  const right = (Object.entries(rev.per_model) as [string, { runs: number; all_four_right: number }][]).filter(([, m]) => m.all_four_right > 0);
  expect(right).toHaveLength(6);
  expect(choose).toContain(`Six of the ${sweep.models_run} models got all four right at least once.`);
  const [best, bestRuns] = right.sort((x, y) => y[1].all_four_right - x[1].all_four_right)[0];
  expect(best).toBe('Nemotron 3 Ultra');
  expect(choose).toContain(`The steadiest, Nemotron 3 Ultra, did so in ${bestRuns.all_four_right} of its ${bestRuns.runs} runs.`);
  expect(rev.per_model['Nemotron 3.5 Super'].all_four_right).toBe(3);
  expect(choose).toContain('Nemotron 3.5 Super got all four right three times, and twice invented a month without looking at the records.');
  const gemma = runs.find((r) => r.model === 'Gemma 4 31B' && r.pack === 'auto-opus' && !r.rule_line)!;
  expect(gemma.answers['4']).toBe('37.8');
  expect(choose).toContain('such as 37.8');
});

// Post 17 and post 18: the repeat of the Opus and Sonnet packs, as recorded.
test('posts 17 and 18 report the repeat of the packs as recorded', async ({ page }) => {
  const t17 = await articleText(page, 'the-auto-ontology-experiment-in-full/');
  const t18 = await articleText(page, 'ontology-tools-in-the-market/');
  const a = repeat;
  expect(t17).toContain('Did repeating the Opus and Sonnet packs change the story?');
  expect(t17).toContain(`${a.tries_saved} of the ${a.tries_planned} tries were saved.`);
  expect(t17).toContain(`${a.totals.opus.all_four_right} of ${a.totals.opus.tries} tries all four right with the Opus pack, ${a.totals.sonnet.all_four_right} of ${a.totals.sonnet.tries} with the Sonnet pack`);
  expect(a.per_model['Nemotron 3 Ultra'].opus).toEqual([6, 5]);
  expect(a.per_model['Nemotron 3 Ultra'].sonnet).toEqual([6, 0]);
  expect(t17).toContain('five of six on the Opus pack and none of six on the Sonnet pack');
  expect(t18).toContain('Nemotron 3 Ultra got all four right in 5 of 6 tries with the Opus pack and in none of 6 with the Sonnet pack');
  expect(t18).toContain(`${a.totals.opus.all_four_right} of ${a.totals.opus.tries} tries right against ${a.totals.sonnet.all_four_right} of ${a.totals.sonnet.tries}`);
});
