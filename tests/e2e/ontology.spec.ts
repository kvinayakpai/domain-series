import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import yaml from 'js-yaml';

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
const story = retail.story;
const ep = story.episode;

// The posts that are out, in reading order: [slug, the line above the title].
const POSTS: [string, string][] = [
  ['what-is-an-ontology', 'Ontology · Start here: 1 of 3'],
  ['why-ontology-matters', 'Ontology · Start here: 2 of 3'],
  ['store-014-ontology', 'Ontology · Start here: 3 of 3'],
  ['ontology-in-open-standards', 'Ontology · A technical detour'],
  ['stock-has-a-place', 'Ontology · Retail: 1 of 4'],
];
// Post 1 is in Vinayak's voice; the others are narrated by his AI assistant.
const NARRATED = ['why-ontology-matters', 'store-014-ontology', 'ontology-in-open-standards', 'stock-has-a-place'];
// Posts that end with one rule for an agent. The full ontology post lists all twelve instead.
const ONE_RULE = ['why-ontology-matters', 'ontology-in-open-standards', 'stock-has-a-place'];
// Posts about a Season 1 problem carry its record and reality lines; the opening posts explain instead.
const WITH_PAIR = ['stock-has-a-place'];

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

test('the season page lists all fifteen posts, links the ones that are out, and covers every Season 1 KPI', async ({ page, request }) => {
  await page.goto('ontology/');
  await expect(page.locator('.opener a[href$="/what-is-an-ontology/"]')).toHaveCount(1);
  await expect(page.locator('.on-posts li')).toHaveCount(15);
  await expect(page.locator('.on-posts li.is-out')).toHaveCount(POSTS.length);
  await expect(page.locator('.on-posts li.is-coming')).toHaveCount(15 - POSTS.length);
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
  // Every file it offers is served, and the tool versions it names are the ones used.
  const hrefs = await page.locator('.ontology-files li a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')!));
  expect(hrefs).toHaveLength(9);
  for (const h of hrefs) expect((await request.head(h.replace('/domain-series/', ''))).status(), h).toBe(200);
  for (const [tool, v] of Object.entries(check.tools) as [string, string][]) {
    const name = { rdflib: 'rdflib', pyshacl: 'pySHACL', owlrl: 'owlrl', owlready2: 'Owlready2', pyoxigraph: 'pyoxigraph', pylode: 'pyLODE', n3: 'N3.js', 'rdf-validate-shacl': 'rdf-validate-shacl' }[tool];
    expect(text, tool).toContain(`${name} ${v}`);
  }
});
