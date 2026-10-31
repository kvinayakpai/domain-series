// The scripted assistant, as a demo view: pick a question, see the queries it ran with what it was given,
// its answer scored against the answer key, every question's score, and the domain layer it was given.
// Shared by the demos whose analysis exports an `assistant` block (logistics, and later payments).
import { h } from './demo-kit';

export interface Step { sql: string; result: Record<string, unknown>[] }
export interface Answer { answer: string; right: boolean; short: string; plan: Step[] }
export interface Question {
  id: string; question: string; check: string;
  naive: Answer; domain: Answer; gold: { short: string; why: string };
}
export interface Assistant {
  as_of: string;
  questions: Question[];
  score: { naive: number; domain: number; of: number };
  schema_only_tables: string[];
  domain_layer: { definitions: Record<string, string>; rules: string[]; views: Record<string, string>; tables_added: string[] };
}
export interface AssistantOptions {
  grounding: 'schema' | 'domain';
  q: string;
  onAsk: (id: string) => void;
  /** One muted line above the questions: when they were asked, of which records. */
  context: string;
  /** Names the schema in the domain layer's header, e.g. 'shipping'. */
  schema: string;
  /** Labels the question list for screen readers, e.g. 'Questions at the supplier review'. */
  listLabel: string;
}

const WORDS: Record<number, string> = { 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight' };

const fmtCell = (v: unknown) => {
  if (v == null) return '–';
  if (typeof v === 'boolean') return v ? 'true' : 'false';
  if (typeof v === 'number') return Number.isInteger(v) ? v.toLocaleString('en-IN') : String(Math.round(v * 1000) / 1000);
  const t = String(v);
  return /^\d{4}-\d\d-\d\dT/.test(t) ? t.slice(0, 16).replace('T', ' ') : t;
};

function resultTable(rows: Record<string, unknown>[]) {
  const wrap = h('div', 'res');
  const t = h('table');
  const thead = h('thead');
  const tr = h('tr');
  for (const c of Object.keys(rows[0])) { const th = h('th', '', c); th.scope = 'col'; tr.append(th); }
  thead.append(tr);
  const tb = h('tbody');
  for (const r of rows.slice(0, 4)) {
    const row = h('tr');
    for (const v of Object.values(r)) row.append(h('td', '', fmtCell(v)));
    tb.append(row);
  }
  t.append(thead, tb);
  wrap.append(t);
  return wrap;
}

function renderRun(box: HTMLElement, a: Assistant, o: AssistantOptions, id: string) {
  const q = a.questions.find((x) => x.id === id) ?? a.questions[0];
  const side = o.grounding === 'domain' ? q.domain : q.naive;
  box.className = `run ${o.grounding}`;
  box.replaceChildren(
    h('p', 'who', o.grounding === 'domain' ? 'AI assistant, given the schema and the domain layer' : 'AI assistant, given the schema'),
    h('p', 'asked', q.question),
    h('p', 'steps-head', `It ran ${side.plan.length === 1 ? 'one query' : `${side.plan.length} queries`}:`),
  );
  const ol = h('ol', 'steps');
  for (const step of side.plan) {
    const li = h('li');
    li.append(h('code', 'sql', step.sql));
    if (step.result.length) li.append(resultTable(step.result));
    ol.append(li);
  }
  const answer = h('blockquote', 'answer-text');
  answer.append(h('p', '', side.answer));
  const verdict = h('p', 'verdict');
  verdict.append(h('strong', side.right ? 'ok' : 'no', side.right ? 'Right.' : 'Wrong.'),
    document.createTextNode(` Answer key: ${q.gold.short}. ${q.gold.why}`));
  box.append(ol, answer, verdict, h('p', 'rule', `Scoring rule: ${q.check}.`));
}

function layerYaml(a: Assistant, schema: string) {
  const d = a.domain_layer;
  const quote = (s: string) => `"${s.replace(/"/g, '\\"')}"`;
  return [
    `# Given to the assistant with the ${schema} schema`,
    'definitions:',
    ...Object.entries(d.definitions).map(([k, v]) => `  ${k.replace(/ /g, '_')}: ${quote(String(v))}`),
    'rules:',
    ...d.rules.map((r) => `  - ${quote(r)}`),
    'views:',
    ...Object.entries(d.views).map(([k, v]) => `  ${k}: ${quote(String(v))}`),
    `tables_added: [${d.tables_added.join(', ')}]`,
  ].join('\n');
}

export function assistantView(host: HTMLElement, a: Assistant, o: AssistantOptions) {
  host.append(h('p', 'context', o.context));
  const ask = h('div', 'ask');
  const list = h('div', 'questions');
  list.setAttribute('role', 'group');
  list.setAttribute('aria-label', o.listLabel);
  const run = h('div', 'run');
  run.setAttribute('aria-live', 'polite');
  for (const q of a.questions) {
    const right = (o.grounding === 'domain' ? q.domain : q.naive).right;
    const b = h('button');
    b.type = 'button';
    b.dataset.q = q.id;
    b.setAttribute('aria-pressed', String(q.id === o.q));
    b.append(h('span', 'q', q.question), h('span', `mark ${right ? 'ok' : 'no'}`, right ? 'Right' : 'Wrong'));
    b.addEventListener('click', () => {
      o.onAsk(q.id);
      list.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      renderRun(run, a, o, q.id);
    });
    list.append(b);
  }
  ask.append(list, run);
  host.append(ask);
  renderRun(run, a, o, o.q);

  const sc = a.score;
  const wrap = h('div', 'table-wrap');
  const table = h('table', 'ledger scores');
  table.append(h('caption', '', `${WORDS[sc.of] ?? sc.of} questions: ${sc.naive} of ${sc.of} right with the schema only, ${sc.domain} of ${sc.of} with the domain layer`));
  const thead = h('thead');
  const hr = h('tr');
  ['Question', 'Schema only', 'With the domain layer', 'Answer key'].forEach((c, i) => {
    const on = (i === 1 && o.grounding === 'schema') || (i === 2 && o.grounding === 'domain');
    const th = h('th', on ? 'on' : '', c);
    th.scope = 'col';
    hr.append(th);
  });
  thead.append(hr);
  const tb = h('tbody');
  for (const q of a.questions) {
    const tr = h('tr');
    const th = h('th', '', q.question);
    th.scope = 'row';
    tr.append(th);
    for (const [side, on] of [[q.naive, o.grounding === 'schema'], [q.domain, o.grounding === 'domain']] as [Answer, boolean][]) {
      const td = h('td', on ? 'on' : '');
      td.append(h('span', side.right ? 'ok' : 'no', side.right ? 'Right' : 'Wrong'), document.createTextNode(` ${side.short}`));
      tr.append(td);
    }
    tr.append(h('td', 'key', q.gold.short));
    tb.append(tr);
  }
  table.append(thead, tb);
  wrap.append(table);
  host.append(wrap);

  const det = h('details', 'layer');
  det.append(h('summary', '', 'What the domain layer adds to the schema'));
  const pre = h('pre', 'yaml');
  pre.textContent = layerYaml(a, o.schema);
  det.append(pre, h('p', 'note', `The schema alone has ${a.schema_only_tables.join(', ')}. The assistant is scripted so the run can be repeated: for each question it runs the queries the question calls for, with what it was given, and composes the answer from what they return.`));
  host.append(det);
}
