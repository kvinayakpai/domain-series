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
function board(slug) {
  const commands = [{ t: 'board', w: W, h: 0 }];
  const put = (c) => (commands.push(c), api);
  const api = {
    slug, w: W, h: 0, commands,
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
  const forecast = REV.runs.filter((r) => /forecast/.test(r.note ?? '') && r.q2_shoppers && r.q2_shoppers !== 'no_record').length;
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
    '• [b]Table descriptions[/b]: [o]0 – did not go in[/o]',
  ].join('\n'), { size: 42, lh: 1.22 });
  b.text(X + 30, y + 410, CW - 60, 64, '[g][b]→ NVIDIA’s model: from guesses to “no record”[/b][/g]', { size: 44 });
  y = b.down(y + 500, 'both, put to three tests');
  // Three tests.
  const [best, bestRuns] = MODELS_RIGHT.slice().sort((p, q) => q[1].all_four_right - p[1].all_four_right)[0];
  const tests = [
    ['Auto-Ontology’s own agent', `Nemotron: 2 shoppers, 3 bags [o]✗[/o] → with the layer, “no record” [g]✓[/g]\n7B: right tables, wrong logic [o]✗[/o]\nIts check: every question “covered”`],
    [`${AGENTS.agents.length} fresh Claude agents`, `All: ${AGENTS.truth.sold} and ${AGENTS.truth.availability_pct}% [g]✓[/g]\nSonnet: “no record”, both times [g]✓[/g]\nOpus: lost sales as a labelled estimate\nHaiku: forecast → 43–84 shoppers [o]✗[/o]`],
    [`${SWEEP.models_run} models, ${SWEEP.runs} tries`, `3 OWL + SHACL packs × with and without one line\nAll 4 right: [b]${REV.plain.all_four_right} → ${REV.rule.all_four_right}[/b] of ${REV.rule.runs}\n[gr]a script had said ${SWEEP.totals.plain.honest} → ${SWEEP.totals.rule.honest} “honest”[/gr]\nBest: ${best}, ${bestRuns.all_four_right} of ${bestRuns.runs} tries`],
  ];
  tests.forEach(([head, body], i) => {
    b.rect(X, y, CW, 360, { stroke: 'ink', fill: i === 2 ? 'noteY' : 'paper', sw: 5, rot: i === 1 ? 0.5 : -0.5 });
    b.num(X + 30, y + 12, i + 1, { d: 76, size: 48 });
    b.text(X + 80, y + 20, CW - 110, 66, `[b]${head}[/b]`, { size: 48 });
    b.text(X + 40, y + 96, CW - 80, 250, body, { size: 44, lh: 1.22 });
    y += 384;
  });
  y += 20;
  b.text(X, y, CW, 150, '[hl]Machines draft what the tables hold.[/hl]\n[hl]People write what they don’t.[/hl]', { size: 56, weight: 700, align: 'center', valign: 'middle', lh: 1.22 });
  y = b.legend(y + 150 + 70, [['blue', 'the records'], ['grey', 'made by a machine'], ['green', 'written by people'], ['orange', 'no record holds it']]);
  return b.end(y);
}

export const BOARDS = [recordsAndReality(), knowledgeLayer(), experiment(), theExam(), fiveSteps()];
