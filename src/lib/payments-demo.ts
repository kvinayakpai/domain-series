// Payments demo: one Saturday evening's slowdown, six ways of looking at the same payments.
import data from '../data/payments.json';
import { barChart, tableView, type Tooltip } from './charts';
import { day, h, inr, num, pct, recordBlock, recordsTable, says, smallTable, tiles, time, when, wireTabs } from './demo-kit';

type Data = typeof data;
type Scn = Data['scenarios'][number];

const C = { record: 'var(--c-record)', reality: 'var(--c-reality)', misplaced: 'var(--c-misplaced)' };
const SLOW = data.meta.slowdown;
const ST = data.story;
const MDR = ST.mdr_on_june_bills;
const pct1 = (x: number) => `${(Math.round(x * 1000) / 10).toFixed(1)}%`;
const days1 = (x: number | null) => (x == null ? '–' : x.toFixed(1));
const mins = (x: number) => `${Math.round(x)} min`;
const tillName: Record<string, string> = { retry: 'take another payment at once', check: 'wait for the status check' };
const KIND: Record<string, string> = { 'debited but the till said failed': 'debited, till failed' };
const hms = (iso: string) => iso.slice(11, 19);
const plusSec = (iso: string, sec: number) => {
  const t = new Date(`${iso.slice(0, 19)}Z`).getTime() + sec * 1000;
  return new Date(t).toISOString().slice(0, 19);
};
const secsBetween = (a: string, b: string) => Math.round((Date.parse(`${b.slice(0, 19)}Z`) - Date.parse(`${a.slice(0, 19)}Z`)) / 1000);
const daysBetween = (a: string, b: string) => secsBetween(a, b) / 86400;

// ---------- state ----------
const state = { till: 'retry', recon: 'manual', persona: 'cashier' };
const scn = () => data.scenarios.find((s) => s.key === `${state.till}|${state.recon}`) as Scn;
const asIs = data.scenarios.find((s) => s.key === 'retry|manual') as Scn;
const scene = (s: Scn) => s.doubles.find((d) => d.bill_id === ST.scene!.bill_id);

// ---------- outcome strip ----------
function renderOutcome(root: HTMLElement) {
  const s = scn();
  const k = s.kpis;
  const extra = k.slowdown.till_minutes - asIs.kpis.slowdown.till_minutes;
  (root.querySelector('[data-outcome]') as HTMLElement).replaceChildren(tiles([
    { label: 'Customers charged twice in June', value: num(k.june.charged_twice),
      note: `${num(k.slowdown.charged_twice)} of them during the 90-minute slowdown` },
    { label: 'Median days until they got the money back', value: days1(k.refunds.median_days_to_refund),
      note: k.refunds.unrefunded_at_month_end ? `${k.refunds.unrefunded_at_month_end} still waiting when June closed` : 'every one refunded by month end' },
    { label: 'Till time taking payment, Saturday 18:20–19:50', value: mins(k.slowdown.till_minutes),
      note: s.till === 'retry' ? 'as the tills run today' : `${Math.round(extra)} minutes more than today, across the tills` },
  ]));
}

// ---------- personas ----------
type Panel = (host: HTMLElement, s: Scn) => void;

const cashier: Panel = (host, s) => {
  const d = scene(s);
  const bill = ST.scene!;
  // What the till says comes before anything else on the line, so it stays in view on a phone.
  const lines = [`Bill ${bill.bill_id}: ${inr(bill.amount_inr)}, ${day(bill.paid_ts)}`];
  if (d) {
    for (const a of d.attempts) lines.push(`${hms(a.ts)}  ${a.tender.padEnd(5)} ${a.till_status}`);
  } else {
    lines.push(`${hms(bill.paid_ts)}  UPI   approved after status check`);
  }
  host.append(recordBlock(lines, 'What the till recorded for one customer’s basket during the slowdown.'));
  const k = s.kpis.slowdown;
  host.append(tiles([
    { label: 'UPI payments the tills gave up on, 18:20–19:50', value: num(k.upi_timeouts), note: `of ${num(k.upi_attempts)} UPI attempts` },
    { label: 'Times a cashier asked for another payment in those 90 minutes', value: num(k.second_payments) },
    { label: 'When a UPI payment hangs, the cashier', value: s.till === 'retry' ? 'Asks again' : 'Waits 90 s', note: tillName[s.till] },
  ]));
  host.append(says(s.till === 'retry'
    ? '“The screen said failed, so I asked for another way to pay. She said the money had left her account. With twenty people waiting, I can’t argue with the screen.”'
    : '“I wait for the status check before I take a second payment. A minute and a half per customer when the system is slow, and the queue goes out of the door.”'));
};

const ops: Panel = (host, s) => {
  const hours = s.hourly;
  const worst = hours.reduce((a, b) => (b.upi_attempts && b.approved_at_till / b.upi_attempts < a.approved_at_till / Math.max(1, a.upi_attempts) ? b : a));
  host.append(recordBlock([
    `UPI success at the tills, ${day(SLOW.start)}`,
    'Hour   Attempts  Approved  Success',
    ...hours.filter((x) => x.hour >= 16).map((x) => `${String(x.hour).padStart(2, '0')}:00  ${String(x.upi_attempts).padStart(8)}  ${String(x.approved_at_till).padStart(8)}  ${pct(x.approved_at_till / Math.max(1, x.upi_attempts)).padStart(7)}`),
  ], 'What the payments operations dashboard shows: approvals at the till, hour by hour.'));
  host.append(tiles([
    { label: 'UPI success at the tills in June', value: pct1(s.kpis.june.four_ways.till) },
    { label: `Worst hour, ${day(SLOW.start)}`, value: pct(worst.approved_at_till / Math.max(1, worst.upi_attempts)), note: `${String(worst.hour).padStart(2, '0')}:00–${String(worst.hour + 1).padStart(2, '0')}:00` },
    { label: 'Technical failures, rest of June', value: pct1(s.kpis.june.upi_technical_failures / s.kpis.june.upi_attempts) },
  ]));
  host.append(says('“Our acquirer’s UPI switch slowed down for ninety minutes on Saturday evening. Success was back to normal by eight. Incident closed; nothing for the stores to do.”'));
  const chart = h('div');
  host.append(h('h4', '', `UPI payments approved at the tills, each hour on ${day(SLOW.start)}`), chart);
  barChart(chart, {
    ariaLabel: `UPI attempts and approvals at the tills by hour, ${day(SLOW.start)}`,
    series: [
      { key: 'attempts', label: 'Attempts', color: C.misplaced, values: hours.map((x) => x.upi_attempts) },
      { key: 'approved', label: 'Approved at the till', color: C.record, values: hours.map((x) => x.approved_at_till) },
    ],
    xTick: (j) => (j % 2 === 0 ? `${String(hours[j].hour).padStart(2, '0')}:00` : null),
    tooltip: (j): Tooltip => ({ title: `${String(hours[j].hour).padStart(2, '0')}:00–${String(hours[j].hour + 1).padStart(2, '0')}:00`, rows: [
      { label: 'UPI attempts', value: num(hours[j].upi_attempts), color: C.misplaced },
      { label: 'approved at the till', value: num(hours[j].approved_at_till), color: C.record },
    ] }),
  });
  const t = h('div');
  host.append(t);
  tableView(t, 'UPI attempts and approvals by hour', ['Hour', 'Attempts', 'Approved at the till'], hours.map((x) => [`${String(x.hour).padStart(2, '0')}:00`, x.upi_attempts, x.approved_at_till]));
};

const recon: Panel = (host, s) => {
  const d21 = s.daily.find((x) => x.date === '2026-06-21')!;
  const d20 = s.daily.find((x) => x.date === '2026-06-20')!;
  host.append(recordBlock([
    'UPI reconciliation, Store 014',
    `${'Day'.padEnd(11)} Approved  Credits  Unmatched`,
    ...[d20, d21].map((x) => `${day(x.date).padEnd(11)} ${String(x.till_approved).padStart(8)}  ${String(x.provider_credits).padStart(7)}  ${String(x.unmatched).padStart(9)}`),
    `Matched by: ${s.recon === 'manual' ? 'amount and time, by hand' : 'bill ID on every UPI request'}`,
  ], 'What the reconciliation analyst sees: the provider’s credits against the till’s approvals.'));
  const r = s.kpis.refunds;
  host.append(tiles([
    { label: 'UPI credits in June with no approved payment at the till', value: num(r.extra_charges) },
    { label: 'Still unmatched when June closed', value: num(r.unrefunded_at_month_end), note: r.unrefunded_at_month_end ? `${inr(r.unrefunded_inr)}, held in suspense` : 'none' },
    { label: 'Refunded within two days of the payment', value: num(s.doubles.filter((x) => x.refunded_ts && daysBetween(x.paid_ts, x.refunded_ts) <= 2).length) },
  ]));
  host.append(says(s.recon === 'manual'
    ? '“The provider shows credits with no approved payment behind them at the till. Until a customer claims one, it sits in suspense.”'
    : '“Every UPI credit names its bill. If a bill is already paid, the match flags it the next morning and the refund goes out.”'));
  const chart = h('div');
  host.append(h('h4', '', 'UPI credits with no approved payment at the till, by day in June'), chart);
  barChart(chart, {
    ariaLabel: 'Unmatched UPI credits by day, June 2026',
    series: [{ key: 'unmatched', label: 'Unmatched credits', color: C.reality, values: s.daily.map((x) => x.unmatched) }],
    xTick: (j) => (j % 7 === 0 ? day(s.daily[j].date) : null),
    tooltip: (j) => ({ title: day(s.daily[j].date), rows: [
      { label: 'unmatched credits', value: num(s.daily[j].unmatched), color: C.reality },
      { label: 'refunds paid', value: num(s.daily[j].refunds) },
    ] }),
  });
};

const support: Panel = (host, s) => {
  const twice = s.complaints.filter((c) => c.kind === 'charged twice');
  host.append(recordBlock([
    'Customer complaints about payments, June',
    ...s.complaints.slice(0, 7).map((c) => `${when(c.complaint_ts)}  ${(KIND[c.kind] ?? c.kind).padEnd(20)}  ${inr(c.amount_inr)}`),
    s.complaints.length > 7 ? `… ${s.complaints.length - 7} more` : '',
  ].filter(Boolean), 'What customer support logs: who called, when, and what they said happened.'));
  host.append(tiles([
    { label: 'Payment complaints in June', value: num(s.complaints.length) },
    { label: '“I was charged twice”', value: num(twice.length) },
    { label: 'Median days from paying to the refund', value: days1(s.kpis.refunds.median_days_to_refund) },
  ]));
  host.append(says(s.recon === 'manual'
    ? '“Every caller says we took their money twice. We ask for a screenshot, check it with the provider, and the refund takes about five days.”'
    : '“Most customers have their refund before they think of calling. The ones who call, we can tell when it went out.”'));
};

const finance: Panel = (host, s) => {
  const refunded = s.refunds.reduce((a, f) => a + f.amount_inr, 0);
  const settled = data.records.settlements;
  const credits = settled.reduce((a, x) => a + x.upi_credits, 0);
  const gross = settled.reduce((a, x) => a + x.gross_inr, 0);
  host.append(recordBlock([
    'UPI settlements for June’s payments',
    `Credits settled   ${num(credits).padStart(19)}`,
    `Gross             ${inr(gross).padStart(19)}`,
    `UPI fees (MDR)    ${inr(0).padStart(19)}`,
    `Refunds paid out  ${inr(refunded).padStart(19)}`,
  ], 'What the finance controller sees in June’s settlement statements.'));
  host.append(tiles([
    { label: 'UPI fees in June', value: inr(0), note: 'no merchant fee on UPI before 15 October 2026' },
    { label: 'The same bills under the fee that began on 15 October', value: inr(MDR.fee_inr), note: `0.4% on ${num(MDR.bills_above)} UPI bills above ₹2,000` },
    { label: 'Refunds paid for double charges', value: inr(refunded) },
  ]));
  host.append(says(`“UPI was free in June. From October it costs us about ${inr(Math.round(MDR.fee_inr / 100) * 100)} a month on big baskets, and nobody budgeted for refunds.”`));
};

const truth: Panel = (host, s) => {
  const story = h('div', 'story');
  const bill = ST.scene!;
  const d = scene(s);
  const att = ST.scene!.attempts;
  const first = att[0];
  const second = att[1];
  story.append(h('p', '', `${when(first.ts)}: a customer with a basket of ${inr(bill.amount_inr)} pays by UPI. Her bank debits her account. The answer back to the till is stuck in the acquirer’s slow switch.`));
  if (d) {
    story.append(
      h('p', '', `${hms(plusSec(first.ts, 30))}: the till gives up and shows “failed: no response”. The cashier asks for another way to pay, and she pays by ${second.tender}.`),
      h('p', '', `${hms(bill.credited_ts)}: the store’s bank confirms the UPI credit, ${secsBetween(first.ts, bill.credited_ts)} seconds after she paid. Nobody at the till sees it. She has now paid twice.`),
      h('p', '', d.refunded_ts ? `${when(d.refunded_ts)}: ${s.recon === 'manual' ? 'after she calls and the store matches the credit by hand' : 'the next morning’s match on the bill ID'}, she gets ${inr(bill.amount_inr)} back.` : 'June ends before she gets her money back.'),
    );
  } else {
    story.append(h('p', '', `The till waits for the status check NPCI allows at 90 seconds. The credit has arrived by then, ${secsBetween(first.ts, bill.credited_ts)} seconds after she paid, so the till shows it approved. She pays once.`));
  }
  const k = s.kpis.slowdown;
  const ret = k.debited_and_returned === 1 ? 'one customer was' : `${k.debited_and_returned} customers were`;
  story.append(h('p', 'aside', `Across the 90 minutes, ${k.charged_twice} customers paid twice (${k.extra_charges} extra charges, ${inr(k.charged_twice_inr)}), and ${ret} debited and later refunded by their bank.`));
  host.append(story);

  const fw = k.four_ways;
  const table = h('table', 'four-ways');
  table.append(h('caption', '', `Payment success during the slowdown, ${day(SLOW.start)} 18:20–19:50, measured four ways`));
  const tb = h('tbody');
  for (const [label, v, how] of [
    ['The till', fw.till, 'UPI attempts the till marked approved'],
    ['The bank', fw.bank, 'UPI attempts that ended as a credit to the store, including late ones'],
    ['Bills paid', fw.bills_paid, 'bills the store was paid for, one way or another'],
    ['Customers charged once', fw.charged_once, 'bills where no customer money moved twice'],
  ] as const) {
    const tr = h('tr');
    tr.append(h('th', '', label), h('td', 'n', pct(v)), h('td', 'how', how));
    tb.append(tr);
  }
  table.append(tb);
  host.append(table);

  const rows = s.doubles.filter((x) => x.paid_ts.slice(0, 16) >= SLOW.start && x.paid_ts.slice(0, 16) < SLOW.end)
    .sort((a, b) => a.paid_ts.localeCompare(b.paid_ts))
    .map((x) => {
      const late = secsBetween(x.paid_ts, x.credited_ts);
      return [hms(x.paid_ts), inr(x.amount_inr), late < 120 ? `${late} s later` : late < 7200 ? `${Math.round(late / 60)} min later` : `${(late / 3600).toFixed(1)} h later`,
        x.refunded_ts ? `${daysBetween(x.paid_ts, x.refunded_ts).toFixed(1)} days` : 'not by month end'];
    });
  if (rows.length) host.append(smallTable('ledger', 'Every extra charge in the slowdown, and when it came back', ['Paid', 'Amount', 'Credited', 'Refunded after'], rows));
};

const PANELS: Record<string, Panel> = { cashier, ops, recon, support, finance, truth };

function renderPersona(root: HTMLElement) {
  const host = root.querySelector('[data-panel]') as HTMLElement;
  host.replaceChildren();
  PANELS[state.persona](host, scn());
  host.setAttribute('aria-labelledby', `py-tab-${state.persona}`);
}

// ---------- records drawer (the store as it runs today) ----------
function renderRecords(root: HTMLElement, which: string, reveal: boolean) {
  const host = root.querySelector('[data-records]') as HTMLElement;
  const r = data.records;
  let head: string[] = [];
  let rows: { cells: (string | number)[]; flag?: string }[] = [];
  if (which === 'till') {
    head = ['Bill', 'Try', 'Time', 'Tender', 'Amount', 'Till says', 'UPI reference'];
    rows = r.pos.map((a) => ({ cells: [a.bill_id, a.attempt, hms(a.ts), a.tender, inr(a.amount_inr), a.till_status, a.rrn ?? ''],
      flag: a.really === 'late credit' ? 'The store was credited later' : a.really === 'returned' ? 'Debited, returned by the bank later' : undefined }));
  } else if (which === 'psp') {
    const approved = new Set(r.pos.filter((a) => a.till_status === 'approved' && a.rrn).map((a) => a.rrn));
    head = ['UPI reference', 'Started', 'Amount', 'Provider says', 'Known at'];
    rows = r.psp.map((p) => ({ cells: [p.rrn, hms(p.initiated_ts), inr(p.amount_inr), p.status, when(p.status_ts)],
      flag: p.status === 'success' && !approved.has(p.rrn) ? 'No approved payment at the till' : undefined }));
  } else {
    head = ['Settled', 'UPI credits', 'Gross', 'Refunds', 'Net'];
    rows = r.settlements.map((x) => ({ cells: [day(x.settlement_date), num(x.upi_credits), inr(x.gross_inr), inr(x.refunds_inr), inr(x.net_inr)] }));
  }
  host.replaceChildren(recordsTable(head, rows, reveal));
}

// ---------- wiring ----------
export function mountPaymentsDemo(root: HTMLElement) {
  const select = wireTabs(root, (p) => { state.persona = p; renderPersona(root); });
  const inputs = root.querySelectorAll<HTMLInputElement>('input[name="till"], input[name="recon"]');
  inputs.forEach((inp) => {
    inp.addEventListener('change', () => {
      state[inp.name as 'till' | 'recon'] = inp.value;
      renderOutcome(root);
      renderPersona(root);
    });
  });
  let recTab = 'till';
  const reveal = root.querySelector<HTMLInputElement>('input[name="py-reveal"]');
  root.querySelectorAll<HTMLButtonElement>('[data-rec]').forEach((b) => {
    b.addEventListener('click', () => {
      recTab = b.dataset.rec as string;
      root.querySelectorAll('[data-rec]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      renderRecords(root, recTab, !!reveal?.checked);
    });
  });
  reveal?.addEventListener('change', () => renderRecords(root, recTab, reveal.checked));

  // Deep links: /demo/?py=truth&till=check&recon=bill_ref#payments
  const q = new URLSearchParams(location.search);
  if (['retry', 'check'].includes(q.get('till') ?? '')) state.till = q.get('till') as string;
  if (['manual', 'bill_ref'].includes(q.get('recon') ?? '')) state.recon = q.get('recon') as string;
  inputs.forEach((inp) => { inp.checked = inp.value === state[inp.name as 'till' | 'recon']; });
  renderOutcome(root);
  select(q.get('py') && PANELS[q.get('py') as string] ? (q.get('py') as string) : 'cashier');
  renderRecords(root, recTab, false);
  root.dataset.ready = 'true';
  (window as unknown as { paymentsDemo: unknown }).paymentsDemo = {
    state,
    select,
    set(nameOf: 'till' | 'recon', value: string) {
      const inp = root.querySelector<HTMLInputElement>(`input[name="${nameOf}"][value="${value}"]`);
      if (inp) { inp.checked = true; inp.dispatchEvent(new Event('change')); }
    },
  };
}
