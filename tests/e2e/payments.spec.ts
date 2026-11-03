import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The payments post and demo quote the world. Every number checked here must still match it.
const data = JSON.parse(readFileSync(new URL('../../src/data/payments.json', import.meta.url), 'utf8'));
const pai = JSON.parse(readFileSync(new URL('../../src/data/payments-ai.json', import.meta.url), 'utf8'));
type Scn = (typeof data.scenarios)[number];
const scenario = (key: string): Scn => data.scenarios.find((s: Scn) => s.key === key);
const asIs = scenario('retry|manual');
const check = scenario('check|manual');
const billRef = scenario('retry|bill_ref');
const st = data.story;
const slow = st.slowdown;
const june = st.june;
const ref = st.refunds;
const pct = (v: number) => `${Math.round(v * 100)}%`;
const pct1 = (v: number) => `${(Math.round(v * 1000) / 10).toFixed(1)}%`;
const inr0 = (v: number) => `₹${Math.round(v).toLocaleString('en-IN')}`;
const inr2 = (v: number) => `₹${v.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const secs = (a: string, b: string) => Math.round((Date.parse(`${b}Z`) - Date.parse(`${a}Z`)) / 1000);
const weekday = (iso: string) => new Date(`${iso.slice(0, 10)}T12:00:00Z`).toLocaleDateString('en-GB', { weekday: 'long', timeZone: 'UTC' });

async function open(page: Page, query = '') {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`demo/${query}`);
  const root = page.locator('[data-payments-demo]');
  await expect(root).toHaveAttribute('data-ready', 'true');
  return { errors, root };
}

test('the money linking post quotes the world correctly', async ({ page }) => {
  await page.goto('payments/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
  const sc = st.scene;
  const d = Object.fromEntries(asIs.daily.map((x: { date: string }) => [x.date, x]));
  const parked = d['2026-06-20'].unmatched + d['2026-06-21'].unmatched;
  const m = pai.matcher;
  const f = pai.find;
  const wait = pai.assistant.questions.find((x: { id: string }) => x.id === 'wait');
  const hm = (iso: string) => iso.slice(11, 16);
  const expected = [
    `Saturday 20 June, ${hm(slow.start)}. The bank's UPI switch slows down. Over the next ${secs(slow.start, slow.end) / 60} minutes, ${slow.upi_timeouts} of ${slow.upi_attempts} UPI attempts get no answer within the till's ${secs(sc.attempts[0].ts, sc.attempts[1].ts)} seconds`,
    `${hm(sc.paid_ts)}. A customer's bank takes ${inr2(sc.amount_inr)}. Her till shows "${sc.attempts[0].till_status}", so she pays again by ${sc.attempts[1].tender}`,
    `confirms her first payment ${secs(sc.paid_ts, sc.credited_ts)} seconds later`,
    `${hm(slow.end)}. The switch recovers. Cashiers have asked for another payment ${slow.second_payments} times, and ${slow.charged_twice} customers have paid twice, ${inr0(slow.charged_twice_inr)} in extra charges`,
    `reconciliation has parked ${parked} credits with no approved payment behind them in suspense`,
    `Payment success rate (KPI 14): ${pct(slow.four_ways.till)} at the till`,
    `Technical decline rate (KPI 15): ${((june.upi_technical_failures / june.upi_attempts) * 100).toFixed(2)}% for June`,
    'Double debits (KPI 16): zero, because every bill had exactly one approved payment',
    `Reconciliation (KPI 17): ${parked} items in suspense`,
    `Refund turnaround (KPI 18): a median ${Math.round(wait.naive.value)} days, from the complaint`,
    `Across all of June, ${june.charged_twice} customers paid twice, and four extra charges were still unrefunded when the month closed`,
    `finds every extra charge, with no false alarms, a median ${f.matcher_median_days} days after the debit`,
    `double charges in June fall from ${asIs.kpis.june.charged_twice} customers to ${check.kpis.june.charged_twice}`,
    `${Math.round(check.kpis.slowdown.till_minutes)} minutes in the slowdown instead of ${Math.round(asIs.kpis.slowdown.till_minutes)}`,
    `the median wait for a refund falls from ${asIs.kpis.refunds.median_days_to_refund} days to ${billRef.kpis.refunds.median_days_to_refund}`,
    `complaints fall from ${asIs.kpis.refunds.complaints} to ${billRef.kpis.refunds.complaints}`,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect([m.true_positives, m.false_positives, m.missed]).toEqual([m.answer_key.extra_charges, 0, 0]);
  expect(ref.unrefunded_at_month_end).toBe(4); // "four extra charges were still unrefunded"
  expect(sc.complaint.complaint_ts.slice(0, 10)).toBe('2026-06-23');
  expect(weekday(sc.complaint.complaint_ts)).toBe('Tuesday'); // "Tuesday 23 June. The customer from 18:48 phones support"
  expect(weekday(sc.refunded_ts)).toBe('Sunday'); // "the following Sunday"
  expect(Math.round(secs(sc.attempts[0].ts, sc.refunded_ts) / 86400)).toBe(8); // "eight days after her shopping"
  expect(billRef.kpis.refunds.unrefunded_at_month_end).toBe(0); // "nothing is left in suspense"
});

test('the payments companion renders its tables without JavaScript', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('payments/technical/');
  await expect(page.locator('table.pay-ways')).toContainText(pct(slow.four_ways.charged_once));
  await expect(page.locator('table.tests tbody tr:not(.group)')).toHaveCount(pai.tests.generic.length + pai.tests.domain.length);
  await expect(page.locator('table.match').first()).toContainText(String(pai.matcher.outcomes['late credit']));
  await expect(page.locator('table.assistant tbody tr')).toHaveCount(pai.assistant.questions.length);
  await ctx.close();
});

test('payments outcome numbers come from the world, and the controls change them', async ({ page }) => {
  const { errors, root } = await open(page);
  const outcome = root.locator('[data-outcome]');
  await expect(outcome).toContainText(String(asIs.kpis.june.charged_twice));
  await expect(outcome).toContainText(String(asIs.kpis.refunds.median_days_to_refund));

  await root.getByRole('radio', { name: 'Wait for the status check' }).check();
  await expect(outcome).toContainText(String(check.kpis.june.charged_twice));
  await expect(outcome).toContainText(`till time ${Math.round(check.kpis.slowdown.till_minutes - asIs.kpis.slowdown.till_minutes)} minutes longer`);

  await root.getByRole('radio', { name: 'As today: ask for another payment' }).check();
  await root.getByRole('radio', { name: 'Put the bill ID on every UPI request' }).check();
  await expect(outcome).toContainText(String(billRef.kpis.refunds.median_days_to_refund));

  // The data team's levers.
  await expect(outcome).toContainText(`${pai.matcher.late_credits} credits wait in suspense`);
  await root.getByRole('radio', { name: 'Matched to the provider’s report' }).check();
  await expect(outcome).toContainText(`on ${pai.matcher.customers} customers`);
  const sc = pai.assistant.score;
  await expect(outcome).toContainText(`${sc.naive} of ${sc.of}`);
  await root.getByRole('radio', { name: 'The schema and a domain layer' }).check();
  await expect(outcome).toContainText(`${sc.domain} of ${sc.of}`);
  expect(errors).toEqual([]);
});

test('every payments view renders, and the tabs work from the keyboard', async ({ page }) => {
  const { errors, root } = await open(page);
  for (const t of ['ops', 'tests', 'recon', 'assistant', 'store', 'truth']) {
    await root.locator(`[data-persona="${t}"]`).click();
    await expect(root.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(root.locator('[data-panel] .record, [data-panel] .story, [data-panel] table, [data-panel] .run').first()).toBeVisible();
  }
  await root.locator('[data-persona="ops"]').click();
  await root.locator('[data-persona="ops"]').press('ArrowRight');
  await expect(root.locator('[data-persona="tests"]')).toHaveAttribute('aria-selected', 'true');
  await expect(root.locator('[data-persona="tests"]')).toBeFocused();
  expect(errors).toEqual([]);
});

test('the reconciliation view holds the credits in suspense, then matches them to customers', async ({ page }) => {
  const { root } = await open(page, '?py=recon');
  const panel = root.locator('[data-panel]');
  await expect(panel).toContainText('Credits held in suspense in June');
  await root.getByRole('radio', { name: 'Matched to the provider’s report' }).check();
  const m = pai.matcher;
  await expect(panel).toContainText(`${m.matched} of ${m.timeouts}`);
  await expect(panel.locator('table tbody tr')).toHaveCount(m.extra_charges);
  await expect(panel).toContainText(`${m.true_positives} found, ${m.false_positives} false alarms`);
  // Scored: the matcher's extra charges are the answer key's.
  const key = JSON.parse(readFileSync(new URL('../../public/data/india-grocery/answer-key-payments.json', import.meta.url), 'utf8'));
  const found = pai.find.per_charge.map((x: { rrn: string }) => x.rrn).sort();
  expect(found).toEqual(key.charged_twice.map((c: { rrn: string }) => c.rrn).sort());
});

test('the payments assistant answers each question from its plan', async ({ page }) => {
  const { root } = await open(page, '?py=assistant');
  const q = pai.assistant.questions.find((x: { id: string }) => x.id === 'twice');
  await expect(root.locator('.run')).toContainText(q.naive.answer);
  await root.getByRole('radio', { name: 'The schema and a domain layer' }).check();
  for (const item of pai.assistant.questions) {
    await root.locator(`[data-q="${item.id}"]`).click();
    await expect(root.locator('.run')).toContainText(item.domain.answer);
    await expect(root.locator('.run code.sql')).toHaveCount(item.domain.plan.length);
  }
});

test('the payments companion quotes the analysis and links its notebook', async ({ page, request }) => {
  await page.goto('payments/technical/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  const m = pai.matcher;
  const f = pai.find;
  for (const e of [
    `All ${m.timeouts} of June's timeouts have a blank reference`,
    `${m.outcomes['late credit']} late credits, ${m.outcomes['debited and returned']} debited and returned, ${m.outcomes['never debited']} never debited`,
    `It returns ${m.extra_charges} rows on ${m.customers} bills`,
    `${m.true_positives} right, ${m.false_positives} false alarms, ${m.missed} missed`,
    `the median wait is ${f.refund_median_days_from_debit} days, ${f.not_refunded} extra charges were still unrefunded, and ${f.over_tat} of the refunds`,
  ]) expect(text.replace(/[’‘]/g, "'"), e).toContain(e);
  await expect(page.locator('figure.plan')).toHaveCount(2);
  await expect(page.locator('a[href="https://colab.research.google.com/github/kvinayakpai/domain-series/blob/main/public/notebooks/payments.ipynb"]')).toHaveCount(1);
  expect((await request.get('notebooks/payments.ipynb')).status()).toBe(200);
});

test('what actually happened shows payment success four ways and every extra charge', async ({ page }) => {
  const { root } = await open(page, '?py=truth');
  const table = root.locator('table.four-ways');
  for (const v of [slow.four_ways.till, slow.four_ways.bank, slow.four_ways.charged_once]) await expect(table).toContainText(pct(v));
  await expect(root.locator('table.ledger tbody tr')).toHaveCount(slow.extra_charges);
  await expect(root.locator('[data-panel]')).toContainText(`${slow.charged_twice} customers paid twice`);
});

test('the payments post links its videos and slides, and they are served', async ({ page, request }) => {
  await page.goto('payments/');
  await expect(page.locator('#walkthrough video')).toHaveAttribute('poster', /payments-walkthrough-poster\.jpg$/);
  await expect(page.locator('.media-links a[href$="payments-slides.pdf"]')).toHaveCount(1);
  for (const [file, type] of [
    ['media/payments-short.mp4', 'video/mp4'],
    ['media/payments-walkthrough.mp4', 'video/mp4'],
    ['media/payments-slides.pdf', 'application/pdf'],
    ['media/payments-short-poster.jpg', 'image/jpeg'],
    ['media/payments-walkthrough-poster.jpg', 'image/jpeg'],
    ['media/payments-walkthrough.srt', ''],
    ['media/payments-short.srt', ''],
  ]) {
    const res = await request.head(file);
    expect(res.status(), file).toBe(200);
    if (type) expect(res.headers()['content-type'], file).toContain(type);
  }
  // The page count the post quotes is the PDF's.
  const pdf = (await (await request.get('media/payments-slides.pdf')).body()).toString('latin1');
  const pages = (pdf.match(/\/Type\s*\/Page\b(?!s)/g) ?? []).length;
  await expect(page.locator('.media-links')).toContainText(`${pages} pages`);
});

test('the payments records drawer reveals the late credits, and the downloads exist', async ({ page, request }) => {
  const { root } = await open(page);
  await root.getByText('The records behind it').click();
  await expect(root.locator('[data-records] table')).toBeVisible();
  await root.getByLabel('Show what the records hide').check();
  await expect(root.locator('[data-records] .gap').first()).toContainText('credited later');
  await root.getByRole('button', { name: 'Provider’s UPI report' }).click();
  await expect(root.locator('[data-records] .gap').first()).toContainText('No approved payment at the till');
  const links = await root.locator('.downloads a').evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute('href')));
  expect(links.length).toBeGreaterThanOrEqual(7);
  for (const href of links) {
    const res = await request.get(href!.replace('/domain-series/', ''));
    expect(res.status(), href!).toBe(200);
  }
});
