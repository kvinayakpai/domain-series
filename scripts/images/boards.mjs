// The whiteboard pictures for Season 2's "Putting it together" posts: what each board says and where it
// sits. Numbers come from the same data files the posts are tested against, so a board cannot drift from
// its post. Drawn by whiteboard.mjs.
// The boards are narrow and tall, read top to bottom, so their words stay readable on a phone: 1200
// pixels wide with body text of 42 to 48 pixels, about 13 to 14 CSS pixels on a phone screen.
import { readFileSync } from 'node:fs';

const json = (f) => JSON.parse(readFileSync(new URL(`../../src/data/${f}`, import.meta.url), 'utf8'));
const RUN = json('auto-ontology-run.json');
const SWEEP = json('auto-ontology-model-sweep.json');
const REV = SWEEP.reviewed;
const AGENTS = json('auto-ontology-claude-agents.json');
const OWL = json('auto-ontology-owl-shacl.json');
const MODELS_RIGHT = Object.entries(REV.per_model).filter(([, m]) => m.all_four_right > 0);

// Markup for board text: [b]bold[/b], [o]orange[/o], [bl]blue[/bl], [g]green[/g], [gr]grey[/gr],
// [hl]highlighter[/hl], and a new line for each \n.
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const m = (s) => esc(s)
  .replace(/\[b\]/g, '<b>').replace(/\[\/b\]/g, '</b>')
  .replace(/\[(o|bl|g|gr|hl)\]/g, '<span class="$1">').replace(/\[\/(o|bl|g|gr|hl)\]/g, '</span>')
  .replace(/\n/g, '<br>');

// Board width, left margin and the width between the margins.
const W = 1200;
const X = 70;
const CW = W - 2 * X;

// A board is laid out top to bottom: each part takes the y below the last one, and end() sets the height.
function board(slug, name) {
  const commands = [{ t: 'board', w: W, h: 0 }];
  const put = (c) => (commands.push(c), api);
  const api = {
    slug, name, w: W, h: 0, commands,
    // A text box is never shorter than one line of its text: Kalam's line box runs about 0.3 of the size
    // past the line height.
    text: (x, y, w2, h2, s, o = {}) => {
      const one = Math.ceil((o.size ?? 56) * ((o.lh ?? 1.22) + 0.3));
      return put({ t: 'text', x, y, w: w2, h: Math.max(h2, one), html: m(s), ...o });
    },
    // The title in up to `lines` lines, and a one-line grey subtitle. Returns the y below them.
    title: (s, lines, sub, size = 84) => {
      const h2 = lines * 102 + 10;
      api.text(X, 56, CW, h2, s, { size, weight: 700, lh: 1.08 });
      if (!sub) return 56 + h2 + 30;
      api.text(X, 56 + h2 + 8, CW, 60, sub, { size: 40, color: 'grey' });
      return 56 + h2 + 8 + 60 + 36;
    },
    rect: (x, y, w2, h2, o = {}) => put({ t: 'rect', x, y, w: w2, h: h2, ...o }),
    hl: (x, y, w2, h2) => put({ t: 'hl', x, y, w: w2, h: h2 }),
    num: (cx, cy, n, o = {}) => put({ t: 'num', cx, cy, n, ...o }),
    arrow: (pts, o = {}) => put({ t: 'arrow', pts, ...o }),
    line: (pts, o = {}) => put({ t: 'line', pts, ...o }),
    icon: (name, x, y, s, o = {}) => put({ t: 'icon', name, x, y, s, ...o }),
    tick: (x, y, s, o = {}) => put({ t: 'tick', x, y, s, ...o }),
    cross: (x, y, s, o = {}) => put({ t: 'cross', x, y, s, ...o }),
    tally: (x, y, n, o = {}) => put({ t: 'tally', x, y, n, gap: 26, h: 70, ...o }),
    bar: (x, y, w2, h2, frac, color) => put({ t: 'bar', x, y, w: w2, h: h2, frac, color }),
    // A down arrow between two parts, with an optional grey note beside it. Returns the y below it.
    down: (y, note, color = 'ink') => {
      api.arrow([[600, y + 4], [588, y + 38], [600, y + 72]], { color, sw: 7, head: 32 });
      if (note) api.text(640, y + 10, R - 640, 56, note, { size: 40, color: 'grey' });
      return y + 86;
    },
    // A legend in a sketched, dashed box, in two columns when every label is short. Returns the y below it.
    legend: (y, items) => {
      const cols = items.every(([, l]) => l.length <= 21) ? 2 : 1;
      const rows = Math.ceil(items.length / cols), h2 = 40 + rows * 68;
      api.rect(X, y, CW, h2, { stroke: 'grey', sw: 4, rough: 0.9, dashed: true });
      api.text(X + 26, y - 32, 220, 60, 'Legend', { size: 42, weight: 700, color: 'grey' });
      items.forEach(([color, label], i) => {
        const cx = X + 36 + (i % cols) * (CW / cols), cy = y + 40 + Math.floor(i / cols) * 68;
        if (color === 'tick') api.tick(cx + 6, cy - 6, 40);
        else if (color === 'cross') api.cross(cx + 8, cy, 34);
        else if (color === 'tally') api.line([[cx + 30, cy - 10], [cx + 32, cy + 44]], { color: 'green', sw: 8, rough: 0.5 });
        else api.line([[cx, cy + 18], [cx + 62, cy + 14]], { color, sw: 16, rough: 0.6 });
        api.text(cx + 90, cy - 10, CW / cols - 140, 60, label, { size: 42 });
      });
      return y + h2;
    },
    // Close the board below y: set its height and sign it.
    end: (y) => {
      api.h = y + 130;
      commands[0].h = api.h;
      api.text(X, api.h - 94, CW, 46, 'Why Domain Matters · Season 2, putting it together', { size: 32, color: 'grey', align: 'right' });
      return api;
    },
  };
  return api;
}
const R = X + CW;

// One step of a path, the width of the board: its number on the corner, an icon, and the title and words
// beside the icon.
function card(b, { y, h, n, kind, icon, title, body }) {
  const people = kind === 'people';
  b.rect(X, y, CW, h, { stroke: people ? 'green' : 'grey', fill: people ? 'noteG' : 'noteGr', sw: 6 });
  b.num(X + 30, y + 12, n, { color: people ? 'green' : 'grey', d: 80, size: 50 });
  b.icon(icon, X + 50, y + 62, 1.0);
  b.text(X + 190, y + 24, CW - 220, 66, title, { size: 52, weight: 700 });
  b.text(X + 190, y + 96, CW - 220, h - 112, body, { size: 46, lh: 1.22 });
}

// Post 19: the five steps, and why the last one is done by hand.
function fiveSteps() {
  const b = board('start-a-domain-ontology');
  let y = b.title('Five steps to an AI that [hl]understands your business[/hl]', 2, 'From Store 014, a simulated supermarket in Bengaluru');
  const steps = [
    ['people', 'chart', 'Know your KPIs', 'The few numbers you run on:\n[b]sales · on-shelf · lost sales[/b]'],
    ['people', 'table', 'Find the record behind each KPI', 'On-shelf availability:\n[bl]books 97%[/bl] · [o]shelf 77%[/o]'],
    ['machine', 'robot', 'Let a machine draft', `[bl][b]${RUN.term_count}[/b] things named[/bl] in ${RUN.run.draft_minutes} minutes\n[o][b]2[/b] missed: demand, lost sale[/o]`],
    ['machine', 'gauge', 'Choose a strong-enough model', `${SWEEP.models_run} models, the same 4 questions:\nonly [b]${MODELS_RIGHT.length}[/b] got all 4 right, even once`],
  ];
  steps.forEach(([kind, icon, title, body], i) => {
    card(b, { y, h: 236, n: i + 1, kind, icon, title, body });
    y = b.down(y + 236, null, i === 3 ? 'green' : 'ink');
  });
  // Step 5, the one that decides the answer.
  const top = y + 6;
  b.rect(X, top, CW, 800, { stroke: 'green', fill: 'noteG', sw: 8 });
  b.num(X + 34, top + 14, 5, { color: 'green', d: 96, size: 60 });
  b.text(X + 90, top + 28, CW - 130, 140, 'Write down how the work happens – [g]by hand[/g]', { size: 56, weight: 700, lh: 1.12 });
  b.rect(X + 70, top + 194, 760, 84, { stroke: 'orange', sw: 6, rot: -2, rough: 1.5 });
  b.text(X + 80, top + 198, 740, 76, 'THE STEP THAT DECIDES THE ANSWER', { size: 40, weight: 700, color: 'orange', align: 'center', valign: 'middle', rot: -2 });
  b.icon('notebook', X + 50, top + 330, 1.6);
  b.text(X + 240, top + 316, CW - 280, 220, '– what each record [o]can’t see[/o]\n– what [o]no record holds[/o]\n– the rules, in plain words', { size: 48, lh: 1.42 });
  b.rect(X + 50, top + 570, CW - 100, 196, { stroke: 'ink', fill: 'noteY', sw: 5, rot: 1 });
  b.text(X + 80, top + 580, CW - 160, 180, `[b]What it changed[/b]\nNVIDIA’s model: guesses → “no record”\nOne plain sentence: [g][b]${REV.plain.all_four_right} → ${REV.rule.all_four_right}[/b][/g] of ${REV.rule.runs} runs all right`, { size: 44, lh: 1.24, rot: 1 });
  y = top + 800 + 44;
  b.text(X, y, CW, 150, '[hl]You can buy the model and the tool.[/hl]\n[hl]Not how your business works.[/hl]', { size: 54, weight: 700, align: 'center', valign: 'middle', lh: 1.25 });
  y = b.legend(y + 150 + 70, [['green', 'only your people can do it'], ['grey', 'a machine or a purchase can do it'], ['blue', 'what the records say'], ['orange', 'what no record holds']]);
  return b.end(y);
}

// Post 15: what happened to one bag of atta, and which record saw it.
function recordsAndReality() {
  const b = board('what-would-a-machine-draft');
  let y = b.title('The records saw the sale. [hl]Not the shopper who left.[/hl]', 2, '5 kg atta at Store 014, a simulated supermarket · June 2026');
  b.text(X, y, CW, 60, '[o]WHAT HAPPENED[/o] → [bl]WHAT THE RECORDS SAW[/bl]', { size: 42, weight: 700 });
  y += 70;
  b.line([[X, y], [R, y - 4]], { color: 'grey', sw: 4, rough: 0.6 });
  y += 34;
  const rows = [
    ['truck', '[b]Tue morning:[/b] a truck brings 14 cases', true, '[bl]Goods receipt: +14 cases[/bl]'],
    ['case', 'The cases go behind the rice – wrong bay', false, '[o]No record[/o]'],
    ['shelf', '[b]Wed 3:48 pm:[/b] the atta shelf runs empty', false, '[bl]Books still say 56 bags[/bl]'],
    ['shopper', 'A shopper wants atta, buys rice, walks out', false, '[o]No row for the atta she wanted[/o]'],
    ['eye', '[b]Fri 11 am:[/b] staff look at the shelf', true, '[bl]Shelf check: empty[/bl]'],
  ];
  rows.forEach(([icon, what, seen, rec], i) => {
    b.num(X + 34, y + 54, i + 1, { d: 70, size: 44 });
    b.icon(icon, X + 92, y + 6, 0.95);
    b.text(X + 220, y + 2, CW - 220, 60, what, { size: 46, lh: 1.2 });
    b.arrow([[X + 226, y + 102], [X + 276, y + 96], [X + 326, y + 102]], { color: seen ? 'blue' : 'orange', dashed: !seen, sw: 6, head: 26 });
    if (seen) b.tick(X + 346, y + 72, 46); else b.cross(X + 352, y + 78, 38);
    b.text(X + 420, y + 70, CW - 420, 64, rec, { size: 46 });
    y += 176;
  });
  // The KPI the books gave, and the shelf's.
  y += 14;
  b.rect(X, y, CW, 384, { stroke: 'ink', fill: 'noteY', sw: 5, rot: -0.6 });
  b.text(X + 40, y + 20, CW - 80, 78, 'The KPI: on-shelf availability', { size: 52, weight: 700 });
  b.text(X + 40, y + 114, 190, 70, 'Books', { size: 48, color: 'blue', weight: 700 });
  b.bar(X + 240, y + 120, 560, 60, 0.97, 'blue');
  b.text(X + 826, y + 110, 170, 76, '97%', { size: 52, weight: 700, color: 'blue' });
  b.text(X + 40, y + 206, 190, 70, 'Shelf', { size: 48, color: 'orange', weight: 700 });
  b.bar(X + 240, y + 212, 560, 60, 0.77, 'orange');
  b.text(X + 826, y + 202, 170, 76, '77%', { size: 52, weight: 700, color: 'orange' });
  b.text(X + 40, y + 298, CW - 80, 64, 'Lost sales: [o]no record holds them[/o]', { size: 46 });
  y += 384 + 40;
  // What a machine made of the same tables.
  b.rect(X, y, CW, 330, { stroke: 'grey', fill: 'noteGr', sw: 5, rot: 0.6 });
  b.icon('robot', X + 30, y + 26, 1.1);
  b.text(X + 170, y + 38, CW - 200, 78, `A machine read the ${RUN.run.tables} tables`, { size: 52, weight: 700 });
  b.tick(X + 176, y + 148, 46);
  b.text(X + 250, y + 132, CW - 290, 70, `[bl]named ${RUN.term_count} things[/bl]`, { size: 48 });
  b.cross(X + 182, y + 238, 38);
  b.text(X + 250, y + 218, CW - 290, 70, '[o]never named demand or the lost sale[/o]', { size: 48 });
  y += 330 + 50;
  b.text(X, y, CW, 150, '[hl]Domain knowledge is knowing which record saw what.[/hl]', { size: 56, weight: 700, align: 'center', valign: 'middle', lh: 1.22 });
  y = b.legend(y + 150 + 70, [['tick', 'a record saw it'], ['cross', 'no record saw it, or only a copy did'], ['blue', 'what the records say'], ['orange', 'what really happened']]);
  return b.end(y);
}

// Post 16: the knowledge layer, its five parts and what the AI does with each.
function knowledgeLayer() {
  const b = board('does-written-down-knowledge-help');
  let y = b.title('What is a knowledge layer?', 1, null, 80);
  b.text(X, y - 14, CW, 80, '[hl]The business, written down for the AI[/hl]', { size: 56, weight: 700 });
  y += 100;
  // The records the layer explains.
  b.rect(X, y, CW, 190, { stroke: 'blue', fill: 'noteB', sw: 6 });
  b.icon('table', X + 26, y + 44, 1.0);
  b.text(X + 160, y + 20, CW - 190, 150, `[b]THE RECORDS[/b] – ${RUN.run.tables} tables: till lines, book stock, shelf checks, deliveries, payments`, { size: 44, valign: 'middle', lh: 1.2 });
  y = b.down(y + 190, null, 'green');
  b.text(X, y, CW, 64, '[b]THE KNOWLEDGE LAYER[/b] – [g]written by people[/g]', { size: 48 });
  y += 78;
  const notes = [
    ['noteY', 'Words', 'OSA, RRN, GTIN: what the codes mean', 'reads the question as the business does'],
    ['noteB', 'Records', 'Till = sales, not demand · books = a belief', 'picks the right table, spots the copies'],
    ['noteG', 'KPIs', 'On-shelf = the shelf checks that found the bag', 'uses the agreed formula, not its own'],
    ['noteO', 'Rules', 'Demand is not sales · no record? say so', 'knows when to say “no record”'],
    ['noteY', 'Examples', 'Units sold by item and month, checked', 'copies a pattern known to be right'],
  ];
  notes.forEach(([fill, name, example, does], i) => {
    b.rect(X, y, CW, 212, { stroke: 'ink', fill, sw: 5, rot: i % 2 ? 0.5 : -0.5 });
    b.text(X + 34, y + 12, CW - 68, 62, `[b]${i + 1}. ${name}[/b]`, { size: 48 });
    b.text(X + 34, y + 78, CW - 68, 58, example, { size: 44 });
    b.text(X + 34, y + 136, CW - 68, 58, `→ the AI [g]${does}[/g]`, { size: 44 });
    y += 226;
  });
  // The AI, reading the layer before the tables.
  b.arrow([[420, y + 4], [408, y + 52], [420, y + 100]], { color: 'green', sw: 8, head: 36 });
  b.icon('robot', 470, y + 14, 1.4);
  b.text(640, y + 24, R - 640, 120, '[b]THE AI[/b]\n[gr]reads this layer first[/gr]', { size: 44, lh: 1.2 });
  y += 186;
  // What changed when it did.
  b.rect(X, y, CW, 340, { stroke: 'orange', fill: 'noteO', sw: 5, rot: 0.6 });
  b.cross(X + 30, y + 30, 36);
  b.text(X + 84, y + 14, CW - 120, 64, '[b]Without it[/b]', { size: 48 });
  b.text(X + 34, y + 90, CW - 68, 230, '“2 shoppers walked away”\n[o]really: 2 empty shelf checks[/o]\n“3 lost bags”\n[o]really: 3 damaged bags[/o]', { size: 44, lh: 1.22 });
  y += 340 + 24;
  b.rect(X, y, CW, 290, { stroke: 'green', fill: 'noteG', sw: 6, rot: -0.6 });
  b.tick(X + 24, y + 24, 46);
  b.text(X + 84, y + 14, CW - 120, 64, '[b]With it[/b]', { size: 48 });
  b.text(X + 34, y + 90, CW - 68, 180, `“No record holds this.”\n[bl]The records show: 2 empty shelf checks,\n${AGENTS.truth.sold} bags sold[/bl]`, { size: 44, lh: 1.22 });
  y += 290 + 50;
  b.text(X, y, CW, 150, '[hl]Plain words, tied to the real records, worked best.[/hl]', { size: 56, weight: 700, align: 'center', valign: 'middle', lh: 1.22 });
  y += 160;
  b.text(X, y, CW, 150, 'Formal OWL and SHACL files are a sixth form – for machines that check the data, not for an AI that answers questions', { size: 40, color: 'grey', align: 'center', lh: 1.2 });
  y = b.legend(y + 150 + 60, [['green', 'written by people'], ['blue', 'the records'], ['tick', 'a right answer'], ['cross', 'a wrong answer']]);
  return b.end(y);
}

// Post 18: the same four questions as an exam, who passed and the ways to fail.
function theExam() {
  const forecast = REV.runs.filter((r) => /forecast/.test(r.note ?? '') && r.q2_shoppers && r.q2_shoppers !== 'no_record').length;
  const b = board('ontology-tools-in-the-market');
  let y = b.title(`Same 4 questions.\n${SWEEP.models_run} AI models. [hl]Who passed?[/hl]`, 2, `5 kg atta, Store 014 · ${SWEEP.runs} tries, every answer read by hand`);
  // The answer key.
  b.rect(X, y, CW, 452, { stroke: 'ink', fill: 'paper', sw: 5, rot: -0.6 });
  b.text(X + 40, y + 20, CW - 80, 66, '[b]THE ANSWER KEY[/b]', { size: 48 });
  const qs = [['Bags sold?', `[bl][b]${AGENTS.truth.sold}[/b][/bl]`], ['Shoppers who walked away?', '[o][b]“no record”[/b][/o]'],
    ['How often on the shelf?', `[bl][b]${AGENTS.truth.availability_pct}%[/b][/bl]`], ['Sales lost?', '[o][b]“no record”[/b][/o]']];
  qs.forEach(([q, ans], i) => b.text(X + 40, y + 96 + i * 66, CW - 80, 62, `Q${i + 1}. ${q} → ${ans}`, { size: 46 }));
  b.text(X + 40, y + 368, CW - 80, 62, '[b]Pass = all 4 right[/b]', { size: 46, color: 'green' });
  y += 452 + 50;
  // Before and after the one plain sentence.
  b.text(X, y, 440, 60, 'Without the sentence', { size: 44, color: 'grey' });
  b.text(X, y + 78, 440, 130, `[b]${REV.plain.all_four_right}[/b] of ${REV.plain.runs}`, { size: 100, color: 'grey', lh: 1 });
  b.arrow([[X + 400, y + 144], [X + 520, y + 124], [X + 640, y + 144]], { color: 'green', sw: 9, head: 44 });
  b.text(X + 690, y, CW - 690, 60, 'With it', { size: 44 });
  b.text(X + 690, y + 78, CW - 690, 130, `[b]${REV.rule.all_four_right}[/b] of ${REV.rule.runs}`, { size: 100, color: 'green', lh: 1 });
  y += 230;
  b.rect(X + 40, y, CW - 80, 196, { stroke: 'ink', fill: 'noteY', sw: 5, rot: 1.2 });
  b.text(X + 70, y + 12, CW - 140, 176, '[b]One plain sentence added:[/b]\n“When no record holds the answer, say ‘no record’ and give no number.”', { size: 44, lh: 1.22, rot: 1.2 });
  y += 196 + 60;
  // Four ways to fail.
  const blanket = REV.runs.filter((r) => r.q1_sold === 'refused' && r.q3_on_shelf === 'refused' && r.no_record_on_both).length;
  b.text(X, y, CW, 66, '4 WAYS TO FAIL', { size: 50, weight: 700, color: 'orange' });
  y += 82;
  const fails = [
    ['robot', `${REV.plain.gave_a_number + REV.rule.gave_a_number}`, 'Made up a number', '1,840 bags sold – without one query'],
    ['chart', `${forecast}`, 'Called a forecast “shoppers”', '“84 shoppers” – really a forecast'],
    ['exam', `${blanket}`, 'Said “no record” to everything', `even to the ${AGENTS.truth.sold} bags sold`],
    ['gauge', `${REV.plain.no_final_answer + REV.rule.no_final_answer}`, 'Never finished', 'ran out of turns, or went silent'],
  ];
  const fw = (CW - 30) / 2;
  fails.forEach(([icon, count, title, eg], i) => {
    const x = X + (i % 2) * (fw + 30), yy = y + Math.floor(i / 2) * 400;
    b.rect(x, yy, fw, 376, { stroke: 'orange', fill: 'noteO', sw: 5, rot: i % 2 ? 1 : -1 });
    b.icon(icon, x + 22, yy + 22, 0.9);
    b.text(x + 150, yy + 14, fw - 180, 110, `[b]${count}[/b]`, { size: 80, color: 'orange', align: 'right', valign: 'middle' });
    b.text(x + 26, yy + 128, fw - 52, 120, `[b]${title}[/b]`, { size: 44, lh: 1.15 });
    b.text(x + 26, yy + 252, fw - 52, 110, eg, { size: 42, lh: 1.18 });
  });
  y += 776 + 12;
  b.text(X, y, CW, 54, `Counts are tries, out of ${SWEEP.runs} – one try is in two boxes`, { size: 38, color: 'grey', align: 'right' });
  y += 54 + 56;
  // Who passed, as tally marks.
  b.text(X, y, CW, 64, '[b]WHO PASSED[/b] – tries with all 4 right, out of 6', { size: 46 });
  y += 82;
  MODELS_RIGHT.forEach(([name, mm], i) => {
    b.text(X, y + i * 72, 620, 64, name, { size: 46 });
    b.tally(X + 660, y + i * 72 + 2, mm.all_four_right, { h: 56 });
  });
  y += MODELS_RIGHT.length * 72 + 8;
  b.text(X, y, CW, 60, `[gr]${Object.keys(REV.per_model).length - MODELS_RIGHT.length} other models: never[/gr]`, { size: 44 });
  y += 60 + 50;
  b.text(X, y, CW, 150, '[hl]Test before you trust – and test more than once.[/hl]', { size: 56, weight: 700, align: 'center', valign: 'middle', lh: 1.22 });
  y = b.legend(y + 150 + 70, [['tally', 'one try, all 4 right'], ['orange', 'a way to fail'], ['blue', 'in the records'], ['grey', 'without the sentence']]);
  return b.end(y);
}

// Post 17, for practitioners: every route and every test on one board.
function experiment() {
  const b = board('the-auto-ontology-experiment-in-full');
  const [opus, sonnet] = OWL.agents, n = RUN.with_nvidia_models;
  let y = b.title('The experiment\n[hl]on one board[/hl]', 2, 'For practitioners · every route and every test');
  // The data, and the true answers.
  b.rect(X, y, CW, 292, { stroke: 'blue', fill: 'noteB', sw: 6 });
  b.icon('table', X + 26, y + 34, 1.0);
  b.text(X + 160, y + 20, CW - 190, 170, `[b]THE DATA[/b] – Store 014, June 2026: ${RUN.run.tables} tables in Postgres (store, warehouse, payments), no foreign keys, no descriptions`, { size: 44, lh: 1.2 });
  b.text(X + 30, y + 204, CW - 60, 62, `[b]True answers:[/b] [bl]${AGENTS.truth.sold}[/bl] · [bl]${AGENTS.truth.availability_pct}%[/bl] · [o]no record[/o] · [o]no record[/o]`, { size: 44 });
  y = b.down(y + 292, 'described two ways');
  // What machines drafted from the tables.
  const ind = '\u00a0\u00a0\u00a0';
  b.rect(X, y, CW, 664, { stroke: 'grey', fill: 'noteGr', sw: 6 });
  b.icon('robot', X + 22, y + 18, 0.9);
  b.text(X + 140, y + 26, CW - 170, 70, '[b]A · MACHINE DRAFTS[/b]', { size: 48 });
  b.text(X + 30, y + 116, CW - 60, 430, [
    '• [b]Auto-Ontology + Qwen3 4B[/b]', `${ind}${RUN.term_count} terms · ${RUN.run.draft_minutes} min · 4 joins`,
    '• [b]Auto-Ontology + Nemotron 3.5 Lightning[/b]', `${ind}${n.term_count} terms · ${n.draft_minutes} min · 3 joins`,
    '• [b]Ontop[/b]', `${ind}${OWL.ontop.classes} classes · ${OWL.ontop.datatype_properties} data properties · 0 links`,
    '• [b]Claude Opus / Sonnet[/b], OWL + SHACL', `${ind}${opus.classes} / ${sonnet.classes} classes · ${opus.node_shapes} / ${sonnet.node_shapes} shapes`,
  ].join('\n'), { size: 42, lh: 1.2 });
  b.rect(X + 130, y + 556, 800, 84, { stroke: 'orange', sw: 6, rot: -1.5, rough: 1.5 });
  b.text(X + 140, y + 560, 780, 76, '[b]none named demand or a lost sale[/b]', { size: 44, color: 'orange', align: 'center', valign: 'middle', rot: -1.5 });
  y += 664 + 30;
  // What people wrote down.
  b.rect(X, y, CW, 500, { stroke: 'green', fill: 'noteG', sw: 6 });
  b.icon('notebook', X + 22, y + 18, 0.9);
  b.text(X + 140, y + 26, CW - 170, 70, '[b]B · KNOWLEDGE BY HAND[/b]', { size: 48 });
  b.text(X + 30, y + 120, CW - 60, 270, [
    '• [b]Instructions[/b], nearly 1,000 words: 12 rules, each with a “Here:” line tying it to a table',
    '• [b]Glossary[/b]: 8 codes',
    '• [b]Calculations[/b]: 4 · [b]certified queries[/b]: 3',
    '• [b]Table descriptions[/b]: 20 of 21 (first try: [o]0[/o])',
  ].join('\n'), { size: 42, lh: 1.22 });
  b.text(X + 30, y + 410, CW - 60, 64, '[g][b]→ NVIDIA’s model: from guesses to “no record”[/b][/g]', { size: 44 });
  y = b.down(y + 500, 'both, put to three tests');
  // Three tests.
  const [best, bestRuns] = MODELS_RIGHT.slice().sort((p, q) => q[1].all_four_right - p[1].all_four_right)[0];
  const tests = [
    ['Auto-Ontology’s own agent', `Nemotron: 2 shoppers, 3 bags [o]✗[/o] → with the layer, “no record” [g]✓[/g]\nRerun with table descriptions: shoppers “no record” [g]✓[/g], lost sales “142” [o]✗[/o]\n7B: right tables, wrong logic [o]✗[/o]\nIts check: every question “covered”`],
    [`${AGENTS.agents.length} fresh Claude agents`, `All: ${AGENTS.truth.sold} and ${AGENTS.truth.availability_pct}% [g]✓[/g]\nSonnet: “no record”, both times [g]✓[/g]\nOpus: lost sales as a labelled estimate\nHaiku: forecast → 43–84 shoppers [o]✗[/o]\nWith Sonnet and Opus’s notes: Haiku, shoppers “no record” 4 of 4 [g]✓[/g]`],
    [`${SWEEP.models_run} models, ${SWEEP.runs} tries`, `3 OWL + SHACL packs × with and without one line\nAll 4 right: [b]${REV.plain.all_four_right} → ${REV.rule.all_four_right}[/b] of ${REV.rule.runs}\n[gr]a script had said ${SWEEP.totals.plain.honest} → ${SWEEP.totals.rule.honest} “honest”[/gr]\nBest: ${best}, ${bestRuns.all_four_right} of ${bestRuns.runs} tries`],
  ];
  tests.forEach(([head, body], i) => {
    const h = i === 0 ? 480 : i === 1 ? 480 : 360;
    b.rect(X, y, CW, h, { stroke: 'ink', fill: i === 2 ? 'noteY' : 'paper', sw: 5, rot: i === 1 ? 0.5 : -0.5 });
    b.num(X + 30, y + 12, i + 1, { d: 76, size: 48 });
    b.text(X + 80, y + 20, CW - 110, 66, `[b]${head}[/b]`, { size: 48 });
    b.text(X + 40, y + 96, CW - 80, h - 110, body, { size: 44, lh: 1.22 });
    y += h + 24;
  });
  y += 20;
  b.text(X, y, CW, 150, '[hl]Machines draft what the tables hold.[/hl]\n[hl]People write what they don’t.[/hl]', { size: 56, weight: 700, align: 'center', valign: 'middle', lh: 1.22 });
  y = b.legend(y + 150 + 70, [['blue', 'the records'], ['grey', 'made by a machine'], ['green', 'written by people'], ['orange', 'no record holds it']]);
  return b.end(y);
}

// ---- Post 17, for the technical reader: one picture for each idea. ----
const TECH = 'the-auto-ontology-experiment-in-full';
const FILL = { green: 'noteG', grey: 'noteGr', blue: 'noteB', orange: 'noteO', ink: 'paper', yellow: 'noteY' };

// A panel the width of the board, or of a column: a coloured box with an optional icon, a title and words.
function panel(b, { x = X, y, w = CW, h, color = 'grey', icon, title, body, tsize = 50, bsize = 44, n, rot = 0 }) {
  b.rect(x, y, w, h, { stroke: color, fill: FILL[color], sw: 6, rot });
  const ix = icon ? 150 : n ? 130 : 40;
  if (icon) b.icon(icon, x + 26, y + 30, 0.95);
  if (n) b.num(x + 30, y + 12, n, { color, d: 76, size: 46 });
  b.text(x + ix, y + 22, w - ix - 24, 64, title, { size: tsize, weight: 700 });
  if (body) b.text(x + ix, y + 22 + Math.ceil(tsize * 1.52) + 6, w - ix - 24, h - Math.ceil(tsize * 1.52) - 44, body, { size: bsize, lh: 1.22 });
}

// 1. Where it all ran.
function techMachine() {
  const b = board(TECH, 'machine');
  let y = b.title('Where did this [hl]actually run?[/hl]', 2, 'No GPU of mine. The GPUs are NVIDIA’s.');
  panel(b, { y, h: 300, color: 'green', icon: 'notebook', title: 'YOU · a GitHub repository', body: '[b]Files you write:[/b] the workflow, run-config.env, the seed script\n[b]One secret:[/b] a free NVIDIA key' });
  y = b.down(y + 300, '1 · a push starts the run');
  // GitHub's machine.
  const top = y;
  const inner = [
    ['blue', 'table', 'Postgres', `Store 014’s ${RUN.run.tables} tables of June records`],
    ['grey', 'robot', 'Auto-Ontology', 'NVIDIA’s open-source tool, in Docker'],
    ['grey', 'gauge', 'Model adapter', 'Sits between the tool and the models. Makes embeddings and reranks'],
    ['grey', 'chart', 'Ollama', 'A small open model on the CPU: Qwen3 4B'],
  ];
  const ih = 330, gw = (CW - 70) / 2;
  b.rect(X, top, CW, 220 + 2 * (ih + 24) + 24, { stroke: 'ink', fill: 'paper', sw: 7, rot: -0.3 });
  b.text(X + 30, top + 22, CW - 60, 66, '[b]GITHUB’S FREE MACHINE[/b]', { size: 54 });
  b.text(X + 30, top + 96, CW - 60, 112, 'A rented Linux computer, wiped after each run:\n4 CPUs · 16 GB · [o]no GPU[/o]', { size: 42, color: 'grey', lh: 1.2 });
  inner.forEach(([color, icon, title, body], i) => {
    const cx = X + 24 + (i % 2) * (gw + 22), cy = top + 234 + Math.floor(i / 2) * (ih + 24);
    b.rect(cx, cy, gw, ih, { stroke: color, fill: FILL[color], sw: 5 });
    b.icon(icon, cx + 20, cy + 18, 0.8);
    b.text(cx + 130, cy + 26, gw - 150, 60, title, { size: 46, weight: 700 });
    b.text(cx + 22, cy + 130, gw - 44, ih - 144, body, { size: 40, lh: 1.2 });
  });
  y = top + 220 + 2 * (ih + 24) + 24;
  // Text goes out, the answer comes back.
  b.arrow([[X + 260, y + 10], [X + 250, y + 70], [X + 260, y + 130]], { color: 'ink', sw: 7, head: 30 });
  b.text(X + 20, y + 140, 470, 120, '2 · a prompt goes out as text', { size: 40, color: 'grey' });
  b.arrow([[X + 800, y + 130], [X + 810, y + 70], [X + 800, y + 10]], { color: 'ink', sw: 7, head: 30 });
  b.text(X + 560, y + 140, 470, 120, '3 · the answer comes back as text', { size: 40, color: 'grey' });
  y += 290;
  panel(b, { y, h: 520, color: 'grey', icon: 'robot', title: 'NVIDIA’S HOSTED API', body: '[b]A free key[/b] from build.nvidia.com\nThe models (Nemotron, Kimi, GLM and more) run on [b]NVIDIA’s GPUs[/b]\nThe 14 models took turns on the same free service\n[o]It slowed down: 503 and 504 for over an hour once[/o]' });
  y = b.down(y + 520, '4 · save and commit');
  panel(b, { y, h: 240, color: 'green', icon: 'notebook', title: 'RESULTS · on your branch', body: 'Every answer, every SQL, the logs: files you can read' });
  y += 240 + 44;
  b.text(X, y, CW, 150, 'GitHub’s machine [hl]only sends text[/hl].\nThe GPU work happens at NVIDIA.', { size: 54, weight: 700, align: 'center', valign: 'middle', lh: 1.25 });
  y = b.legend(y + 150 + 70, [['green', 'files you write'], ['blue', 'the records'], ['grey', 'computers: GitHub’s, NVIDIA’s'], ['orange', 'what is missing or slow']]);
  return b.end(y);
}

// 2. One run, step by step, and how long each part took.
function techRun() {
  const b = board(TECH, 'run');
  let y = b.title('One run, [hl]step by step[/hl]', 2, 'What the demo workflow does on GitHub’s machine');
  const steps = [
    ['Pick the models', 'run-config.env: nvidia or ollama'],
    ['Fetch Auto-Ontology', 'NVIDIA’s code at one fixed commit'],
    ['Start Postgres, the adapter, Ollama', 'a small embedding model is pulled'],
    ['Load Store 014', `${RUN.run.tables} tables, no foreign keys`],
    ['Build and start Auto-Ontology', 'then wait until the web app answers'],
    ['Draft, check coverage, ask the 4 questions', 'the part where the model works'],
    ['Enter the knowledge by hand', 'then check coverage and ask again'],
    ['Save, scrub, commit', 'passwords and key removed first'],
  ];
  steps.forEach(([t, s], i) => {
    const hot = i === 5;
    b.rect(X, y, CW, 190, { stroke: hot ? 'orange' : 'grey', fill: hot ? 'noteO' : 'noteGr', sw: 5 });
    b.num(X + 30, y + 14, i + 1, { color: hot ? 'orange' : 'grey', d: 76, size: 46 });
    b.text(X + 130, y + 16, CW - 160, 120, t, { size: 46, weight: 700, lh: 1.1 });
    b.text(X + 130, y + 124, CW - 160, 56, s, { size: 38, color: 'grey' });
    y += 190;
    if (i < steps.length - 1) { b.arrow([[600, y + 2], [592, y + 22], [600, y + 42]], { color: 'ink', sw: 6, head: 24 }); y += 46; }
  });
  y += 50;
  // How long step 6 took with two kinds of model.
  const q = RUN.run.phases, n = RUN.with_nvidia_models.phases;
  b.text(X, y, CW, 70, '[b]Step 6, in minutes[/b]', { size: 52 });
  y += 84;
  const rows = [
    ['Draft the ontology', q.compile.minutes, n.compile.minutes],
    ['Check coverage', q.coverage.minutes, n.coverage.minutes],
    ['Ask the 4 questions', q.ask.minutes, n.ask.minutes],
  ];
  const max = 46;
  rows.forEach(([label, a, c]) => {
    b.text(X, y, CW, 60, label, { size: 44, weight: 700 });
    b.text(X, y + 64, 120, 56, 'CPU', { size: 38, color: 'grey' });
    b.bar(X + 130, y + 72, 700, 46, Math.max(a / max, 0.012), 'grey');
    b.text(X + 850, y + 62, 200, 60, `${a}`, { size: 46, weight: 700 });
    b.text(X, y + 130, 120, 56, 'GPU', { size: 38, color: 'orange' });
    b.bar(X + 130, y + 138, 700, 46, Math.max(c / max, 0.012), 'orange');
    b.text(X + 850, y + 128, 200, 60, `${c}`, { size: 46, weight: 700, color: 'orange' });
    y += 214;
  });
  b.text(X, y, CW, 120, `[gr]CPU: Qwen3 4B on GitHub’s 4 CPUs (run 6). GPU: Nemotron 3.5 Lightning on NVIDIA’s servers (run 10)[/gr]`, { size: 38, lh: 1.2 });
  y += 130;
  y = b.legend(y + 60, [['grey', 'a small model on the CPU'], ['orange', 'NVIDIA’s model on its GPUs']]);
  return b.end(y);
}

// 3. The sweep: one job per model, a loop of SQL.
function techSweep() {
  const b = board(TECH, 'sweep');
  let y = b.title('The sweep: [hl]one job per model[/hl]', 2, `${SWEEP.models_run} models · ${SWEEP.runs} runs · the same 4 questions`);
  panel(b, { y, h: 330, color: 'grey', n: 1, title: 'One GitHub job for each model', body: 'Each job is its own machine with its own Postgres and Store 014’s tables. Up to 10 at a time.' });
  y = b.down(y + 330);
  panel(b, { y, h: 400, color: 'green', n: 2, title: 'The prompt', body: 'The 4 questions\n+ one pack of OWL and SHACL, pasted as text\n+ sometimes one line: [b]say “no record”, no number[/b]' });
  y += 400;
  // The loop.
  y = b.down(y);
  const lt = y;
  b.rect(X, lt, CW, 1010, { stroke: 'ink', fill: 'paper', sw: 6, rough: 1.1, rot: 0.2 });
  b.text(X + 30, lt + 18, CW - 60, 66, `[b]3 · The loop: up to 30 turns[/b]`, { size: 50 });
  const loop = [
    ['grey', 'The model replies with ONE ```sql block', 'These models take no tool calls, so the SQL is plain text'],
    ['blue', 'The job runs it on Postgres', 'read-only, 30 seconds at most, first 60 rows'],
    ['blue', 'The rows go back as the next message', 'or the error, as a text-to-SQL agent would see it'],
  ];
  let ly = lt + 106;
  loop.forEach(([c, t, s], i) => {
    b.rect(X + 30, ly, CW - 60, 220, { stroke: c, fill: FILL[c], sw: 5 });
    b.text(X + 56, ly + 14, CW - 112, 130, t, { size: 44, weight: 700, lh: 1.1 });
    b.text(X + 56, ly + 132, CW - 112, 80, s, { size: 38, color: 'grey', lh: 1.15 });
    ly += 220;
    if (i < loop.length - 1) { b.arrow([[600, ly + 2], [592, ly + 20], [600, ly + 38]], { color: 'ink', sw: 6, head: 22 }); ly += 42; }
  });
  // Return arrow.
  b.arrow([[X + 8, ly - 120], [X - 6, ly - 430], [X + 20, lt + 220]], { color: 'orange', sw: 7, head: 26, dashed: true });
  b.text(X + 40, ly + 10, CW - 80, 70, '[o]↻ repeat until a final answer[/o]', { size: 42, weight: 700 });
  y = lt + 1010;
  y = b.down(y);
  panel(b, { y, h: 380, color: 'green', n: 4, title: 'Save, scrub the key, commit', body: 'The final answer, every SQL it ran, its results: one file per run, committed to the branch' });
  y += 380 + 36;
  b.rect(X, y, CW, 290, { stroke: 'orange', fill: 'noteO', sw: 5 });
  b.text(X + 30, y + 18, CW - 60, 60, '[b]When the free service stumbled[/b]', { size: 48 });
  b.text(X + 30, y + 90, CW - 60, 190, '• Each call is retried 6 times, 30 seconds apart\n• 504 errors, prompts too long, a time limit,\n  and Gemma 3 answering 404', { size: 40, lh: 1.25 });
  y += 290 + 50;
  y = b.legend(y + 30, [['grey', 'the model and the job'], ['blue', 'the records'], ['green', 'what you write or keep'], ['orange', 'what went wrong']]);
  return b.end(y);
}

// 4. How the Claude agents were run, twice.
function techAgents() {
  const b = board(TECH, 'agents');
  const W2 = AGENTS.with_sonnet_and_opus_packs;
  let y = b.title('How the Claude agents were [hl]tested[/hl]', 2, 'Claude’s own agents, on my computer, not on GitHub');
  panel(b, { y, h: 360, color: 'green', n: 1, title: 'I launch an agent', body: 'Haiku, Sonnet or Opus. It has never seen this work. It gets the 4 questions, some notes, and one tool.' });
  y = b.down(y + 360);
  b.text(X, y, CW, 70, '[b]The notes it is given[/b]', { size: 50 });
  y += 84;
  const cw2 = (CW - 24) / 2;
  b.rect(X, y, cw2, 470, { stroke: 'grey', fill: FILL.grey, sw: 5 });
  b.text(X + 20, y + 16, cw2 - 40, 130, '[b]Test 1 · 21 Nov[/b]\n6 agents', { size: 44, lh: 1.15 });
  b.text(X + 20, y + 160, cw2 - 40, 300, 'Nemotron’s 21-term draft,\nalone, or with the\nknowledge layer I wrote', { size: 40, lh: 1.2 });
  b.rect(X + cw2 + 24, y, cw2, 470, { stroke: 'grey', fill: FILL.yellow, sw: 5 });
  b.text(X + cw2 + 44, y + 16, cw2 - 40, 130, `[b]Test 2 · 23 Nov[/b]\n${W2.runs.length} agents`, { size: 44, lh: 1.15 });
  b.text(X + cw2 + 44, y + 160, cw2 - 40, 300, 'The Opus pack or the Sonnet pack, with or without the “no record” line', { size: 40, lh: 1.2 });
  y += 470;
  y = b.down(y, 'the agent works alone');
  panel(b, { y, h: 380, color: 'blue', icon: 'table', n: 2, title: 'It queries Store 014', body: 'A read-only login to Postgres: it can read the 21 tables and change nothing' });
  y = b.down(y + 380);
  panel(b, { y, h: 340, color: 'grey', n: 3, title: 'It hands back an answer and its SQL', body: 'Four answers, the queries behind them, and how sure it is' });
  y = b.down(y + 340);
  panel(b, { y, h: 340, color: 'green', n: 4, title: 'I re-run its SQL on the records', body: 'Then score: 567 bags, 75%, and no record twice' });
  y += 340 + 50;
  // Result: honest answers out of 8, per model, test 2.
  b.text(X, y, CW, 120, '[b]Test 2: “no record” where it should be[/b]\nout of 8 answers on the 2 questions no table can answer', { size: 42, lh: 1.2 });
  y += 140;
  Object.entries(W2.honest_of_8).forEach(([model, k]) => {
    b.text(X, y, 260, 64, model, { size: 46, weight: 700 });
    b.bar(X + 270, y + 8, 560, 52, k / 8, k === 8 ? 'green' : 'orange');
    b.text(X + 860, y, 200, 64, `${k} of 8`, { size: 46, weight: 700, color: k === 8 ? 'green' : 'orange' });
    y += 90;
  });
  b.text(X, y + 6, CW, 120, '[gr]Haiku kept “no record” for the shoppers every time. Without the line, it gave a lost-sales estimate.[/gr]', { size: 38, lh: 1.2 });
  y += 140;
  y = b.legend(y + 40, [['green', 'what I write or check'], ['grey', 'what the agent is given'], ['blue', 'the records'], ['orange', 'a number where there should be none']]);
  return b.end(y);
}

// 5. Three automatic routes from the same tables.
function techRoutes() {
  const b = board(TECH, 'routes');
  const [opus, sonnet] = OWL.agents, n = RUN.with_nvidia_models;
  let y = b.title('Three machine routes from [hl]the same 21 tables[/hl]', 2, 'And what each one wrote');
  panel(b, { y, h: 230, color: 'blue', icon: 'table', title: `Store 014 · ${RUN.run.tables} tables`, body: 'No foreign keys, no descriptions' });
  y += 230;
  const routes = [
    ['grey', 'robot', 'A · Auto-Ontology', `A semantic layer: terms, joins, calculations\n${n.term_count} terms with Nemotron, ${RUN.term_count} with Qwen3 4B\nNot RDF, OWL or SHACL`],
    ['grey', 'table', 'B · Ontop', `An OWL file and a mapping\n${OWL.ontop.classes} classes · ${OWL.ontop.datatype_properties} data properties\n[o]0 links[/o]: no foreign keys to follow`],
    ['grey', 'robot', 'C · Opus and Sonnet agents', `OWL and SHACL, written from the database alone\n${opus.classes} / ${sonnet.classes} classes · ${opus.node_shapes} / ${sonnet.node_shapes} shapes\n[g]They found the joins the database never declared[/g]`],
  ];
  routes.forEach(([c, icon, t, body]) => {
    y = b.down(y);
    panel(b, { y, h: 440, color: c, icon, title: t, body, tsize: 48, bsize: 42 });
    y += 440;
  });
  y = b.down(y, 'then, the same test for all');
  b.rect(X, y, CW, 330, { stroke: 'orange', fill: FILL.orange, sw: 7, rot: -0.5 });
  b.icon('shopper', X + 26, y + 36, 1.0);
  b.text(X + 170, y + 30, CW - 200, 90, '[b]None of the three[/b]', { size: 54 });
  b.text(X + 170, y + 130, CW - 200, 180, 'named demand or a lost sale.\nA strong model finds what the data shows.\nNot what it never held.', { size: 44, lh: 1.22 });
  y += 330 + 60;
  b.text(X, y, CW, 160, '[hl]Same tables, three outputs,[/hl]\n[hl]the same blind spot[/hl]', { size: 54, weight: 700, align: 'center', valign: 'middle', lh: 1.25 });
  y = b.legend(y + 160 + 70, [['blue', 'the records'], ['grey', 'made by a machine'], ['orange', 'no record holds it']]);
  return b.end(y);
}

// 6. The sweep's results.
function techResults() {
  const b = board(TECH, 'results');
  const per = Object.entries(REV.per_model);
  let y = b.title('Who got [hl]all four right?[/hl]', 2, `Tries with all four right · ${SWEEP.models_run} models · ${SWEEP.runs} tries`);
  per.forEach(([name, m2]) => {
    const free = m2.all_four_right;
    b.text(X, y, 450, 64, name, { size: 40, weight: free ? 700 : 400, color: free ? 'ink' : 'grey' });
    b.bar(X + 460, y + 10, 440, 48, free / m2.runs, free ? 'green' : 'grey');
    b.text(X + 930, y, 140, 64, `${free}`, { size: 46, weight: 700, color: free ? 'green' : 'grey' });
    y += 84;
  });
  y += 20;
  b.rect(X, y, CW, 300, { stroke: 'ink', fill: FILL.yellow, sw: 5, rot: 0.4 });
  b.text(X + 30, y + 14, CW - 60, 66, '[b]The same line, in everyone’s prompt[/b]', { size: 46 });
  b.text(X + 30, y + 90, CW - 60, 200, `Without it: [o]${REV.plain.all_four_right} of ${REV.plain.runs}[/o] tries right\nWith it: [g]${REV.rule.all_four_right} of ${REV.rule.runs}[/g] tries right`, { size: 52, lh: 1.25, weight: 700 });
  y += 300 + 50;
  b.text(X, y, CW, 70, '[b]How a try fails[/b]', { size: 52 });
  y += 84;
  const fails = [
    [`${REV.plain.gave_a_number + REV.rule.gave_a_number}`, 'gave a number for what no record holds'],
    [`${REV.plain.no_record_but_q1_or_q3_wrong + REV.rule.no_record_but_q1_or_q3_wrong}`, 'said “no record” but got 567 or 75% wrong'],
    [`${REV.plain.no_final_answer + REV.rule.no_final_answer}`, 'never finished: no final answer'],
  ];
  fails.forEach(([k, t]) => {
    b.rect(X, y, CW, 170, { stroke: 'orange', fill: FILL.orange, sw: 5 });
    b.text(X + 20, y + 20, 200, 130, k, { size: 84, weight: 700, color: 'orange', align: 'center', valign: 'middle' });
    b.text(X + 240, y + 20, CW - 270, 130, t, { size: 46, valign: 'middle', lh: 1.15 });
    y += 190;
  });
  y += 30;
  y = b.legend(y + 30, [['green', 'tries with all 4 right'], ['grey', 'models that never did'], ['orange', 'ways to fail']]);
  return b.end(y);
}

// 7. How to repeat it.
function techReplicate() {
  const b = board(TECH, 'replicate');
  let y = b.title('Want to repeat it? [hl]Seven steps[/hl]', 2, 'You need a GitHub account and a free NVIDIA key');
  const steps = [
    ['green', 'notebook', 'Copy the repository', 'Take the branches auto-ontology-demo and owl-packs-nim from kvinayakpai/domain-series'],
    ['green', 'gauge', 'Get a free key', 'Make one at build.nvidia.com. Add it as the repository secret NVIDIA_API_KEY'],
    ['green', 'table', 'Choose what to run', 'Demo: edit auto-ontology-demo/run-config.env (MODELS, EMBEDDINGS). Sweep: edit the model list in the workflow'],
    ['grey', 'robot', 'Start it', 'Push to the branch, or press Run workflow in the Actions tab'],
    ['grey', 'chart', 'Wait', 'The demo with NVIDIA’s model took about 30 minutes. With Qwen3 4B on the CPU it took hours. The sweep runs its jobs side by side'],
    ['blue', 'notebook', 'Read the results', 'Committed to the branch: auto-ontology-demo/results/run-N and owl-packs-test/results/nim-run-N'],
    ['blue', 'eye', 'Score by reading', 'Read every answer. Re-run its SQL on your own copy of the records (seed_store014.py makes it)'],
  ];
  steps.forEach(([c, icon, t, body], i) => {
    const h = 330;
    panel(b, { y, h, color: c, icon, n: i + 1, title: t, body, tsize: 48, bsize: 40 });
    y += h;
    if (i < steps.length - 1) y = b.down(y);
  });
  y += 50;
  b.rect(X, y, CW, 250, { stroke: 'orange', fill: FILL.orange, sw: 6, rot: -0.4 });
  b.text(X + 30, y + 16, CW - 60, 66, '[b]Watch for[/b]', { size: 48 });
  b.text(X + 30, y + 90, CW - 60, 150, 'The free service rate-limits and sometimes fails.\nA model that is listed may still answer 404.', { size: 42, lh: 1.22 });
  y += 250 + 50;
  y = b.legend(y + 30, [['green', 'set up by you'], ['grey', 'runs by itself'], ['blue', 'what you read'], ['orange', 'what can go wrong']]);
  return b.end(y);
}

// 8. Who offers what.
function techMarket() {
  const b = board(TECH, 'market');
  let y = b.title('Who offers the tools, and [hl]what do they write?[/hl]', 2, 'Placed by what each product’s own documents say');
  b.text(X, y, CW, 60, '[b]↓ who writes the meaning[/b]   [b]→ the file it ends in[/b]', { size: 40, color: 'grey' });
  y += 76;
  const cw2 = (CW - 24) / 2;
  b.text(X, y, cw2, 112, '[b]OWL / RDF[/b]\nthe open standard', { size: 38, lh: 1.15, align: 'center' });
  b.text(X + cw2 + 24, y, cw2, 112, '[b]Their own format[/b]\nYAML or a product', { size: 38, lh: 1.15, align: 'center' });
  y += 110;
  const cells = [
    ['grey', 'A MACHINE DRAFTS', [['Ontop', 'from the tables'], ['Fabric IQ', 'from Power BI models; imports OWL']], [['NVIDIA Auto-Ontology', 'exports Ossie YAML'], ['Snowflake', 'drafts from past queries'], ['Databricks Genie', 'learns; people certify']]],
    ['green', 'PEOPLE MODEL IT', [['Protégé', 'you build by hand'], ['Stardog', 'RDF graph database'], ['Timbr', 'in SQL; imports OWL']], [['Palantir Foundry', 'objects, links, actions'], ['Apache Ossie', 'a YAML format, not RDF']]],
  ];
  cells.forEach(([c, label, left, right]) => {
    b.text(X, y, CW, 60, `[b]${label}[/b]`, { size: 42, color: c === 'green' ? 'green' : 'grey' });
    y += 66;
    const rows = Math.max(left.length, right.length), h = 36 + rows * 170;
    [left, right].forEach((col, ci) => {
      const x0 = X + ci * (cw2 + 24);
      b.rect(x0, y, cw2, h, { stroke: c, fill: FILL[c], sw: 5 });
      col.forEach(([t, s], i) => {
        b.text(x0 + 18, y + 18 + i * 170, cw2 - 36, 64, t, { size: 42, weight: 700 });
        b.text(x0 + 18, y + 82 + i * 170, cw2 - 36, 80, s, { size: 34, color: 'grey', lh: 1.1 });
      });
    });
    y += h + 40;
  });
  b.text(X, y, CW, 150, '[hl]None can draft what no table holds[/hl]\n[hl]– so people still write it[/hl]', { size: 52, weight: 700, align: 'center', valign: 'middle', lh: 1.25 });
  y = b.legend(y + 150 + 70, [['grey', 'machine-drafted'], ['green', 'modeled by people']]);
  return b.end(y);
}


// 9. The repeat of the Opus and Sonnet packs.
const REP = json('auto-ontology-repeat-sweep.json');
function techRepeat() {
  const b = board(TECH, 'repeat');
  let y = b.title('Same model, [hl]different luck[/hl]', 2, `Each pack tried six times · ${REP.tries_saved} of ${REP.tries_planned} tries saved`);
  b.text(X, y, CW, 70, '[b]Tries with all four right, out of 6[/b]', { size: 48 });
  y += 90;
  ['Nemotron 3 Ultra', 'Nemotron 3.5 Lightning', 'Gemma 4 31B', 'Nemotron 3.5 Super', 'Step 5 Preview'].forEach((name) => {
    const m = REP.per_model[name];
    b.text(X, y, CW, 60, name, { size: 44, weight: 700 });
    b.text(X, y + 66, 150, 56, 'Opus', { size: 38, color: 'grey' });
    b.bar(X + 160, y + 74, 640, 44, Math.max(m.opus[1] / 6, 0.012), 'blue');
    b.text(X + 830, y + 62, 200, 60, `${m.opus[1]}`, { size: 46, weight: 700, color: 'blue' });
    b.text(X, y + 126, 150, 56, 'Sonnet', { size: 38, color: 'grey' });
    b.bar(X + 160, y + 134, 640, 44, Math.max(m.sonnet[1] / 6, 0.012), 'orange');
    b.text(X + 830, y + 122, 200, 60, `${m.sonnet[1]}`, { size: 46, weight: 700, color: 'orange' });
    y += 214;
  });
  y += 20;
  b.rect(X, y, CW, 340, { stroke: 'ink', fill: FILL.yellow, sw: 5, rot: 0.4 });
  b.text(X + 30, y + 16, CW - 60, 66, '[b]Across every model[/b]', { size: 48 });
  b.text(X + 30, y + 96, CW - 60, 230, `Opus pack: [b]${REP.totals.opus.all_four_right} of ${REP.totals.opus.tries}[/b] tries\nSonnet pack: [b]${REP.totals.sonnet.all_four_right} of ${REP.totals.sonnet.tries}[/b] tries\n[hl]The packs came out level[/hl]`, { size: 50, lh: 1.25 });
  y += 340 + 50;
  b.rect(X, y, CW, 330, { stroke: 'orange', fill: FILL.orange, sw: 5 });
  b.text(X + 30, y + 16, CW - 60, 66, '[b]Not every job finished[/b]', { size: 48 });
  b.text(X + 30, y + 96, CW - 60, 220, `GLM 5.3 Flash saved nothing.\nKimi K3.1 Pro saved 6 tries, none finished.\nBoth hit the job’s time limit.`, { size: 42, lh: 1.25 });
  y += 330 + 50;
  b.text(X, y, CW, 150, '[hl]One model, two packs:[/hl]\n[hl]Ultra 5 of 6 on one, 0 of 6 on the other[/hl]', { size: 50, weight: 700, align: 'center', valign: 'middle', lh: 1.25 });
  y = b.legend(y + 150 + 70, [['blue', 'with the Opus pack'], ['orange', 'with the Sonnet pack']]);
  return b.end(y);
}

export const BOARDS = [recordsAndReality(), knowledgeLayer(), experiment(), theExam(), fiveSteps(), techMachine(), techRun(), techSweep(), techAgents(), techRoutes(), techResults(), techReplicate(), techMarket(), techRepeat()];
