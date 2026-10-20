import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

// The payments post and demo quote the world. Every number checked here must still match it.
const data = JSON.parse(readFileSync(new URL('../../src/data/payments.json', import.meta.url), 'utf8'));
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

test('the payments post quotes the world correctly', async ({ page }) => {
  await page.goto('payments/');
  const text = (await page.locator('article').innerText()).replace(/\s+/g, ' ');
  const sc = st.scene;
  const hours = Object.fromEntries(st.slowdown_day_by_hour.map((h: { hour: number }) => [h.hour, h]));
  const d = Object.fromEntries(asIs.daily.map((x: { date: string }) => [x.date, x]));
  const twice = asIs.complaints.filter((c: { kind: string }) => c.kind === 'charged twice').length;
  const refunds = asIs.refunds.reduce((a: number, f: { amount_inr: number }) => a + f.amount_inr, 0);
  const longestReturn = Math.max(...asIs.returns.map((r: { days: number }) => r.days));
  const expected = [
    `basket comes to ${inr2(sc.amount_inr)}`,
    `${secs(sc.attempts[0].ts, sc.credited_ts)} seconds after she approved the UPI payment`,
    `the tills gave up on ${slow.upi_timeouts} UPI payments, and cashiers asked for another payment ${slow.second_payments} times`,
    `fell to ${pct(hours[18].approved_at_till / hours[18].upi_attempts)} and ${pct(hours[19].approved_at_till / hours[19].upi_attempts)} of UPI attempts in the 18:00 and 19:00 hours`,
    `there were ${d['2026-06-20'].provider_credits} credits against ${d['2026-06-20'].till_approved} approvals, and on Sunday ${d['2026-06-21'].provider_credits} against ${d['2026-06-21'].till_approved}. The ${d['2026-06-20'].unmatched + d['2026-06-21'].unmatched} credits`,
    `takes ${asIs.complaints.length} complaints about payments in June, ${twice} of them`,
    `${inr0(refunds)} of refunds`,
    `${pct(data.params.upi_slowdown.value.timeout)} of UPI attempts at Store 014 got no answer`,
    `Store 014 took ${slow.bills} bills. Of ${slow.upi_attempts} UPI attempts, the tills gave up on ${slow.upi_timeouts}. ${slow.charged_twice} customers paid twice, two of them three times: ${slow.extra_charges} extra charges, ${inr2(slow.charged_twice_inr)} in all.`,
    `Across June, ${june.charged_twice} customers paid twice, ${june.extra_charges} extra charges worth ${inr2(june.charged_twice_inr)}; ${june.charged_twice - slow.charged_twice} of them outside the Saturday slowdown`,
    `The median wait was ${ref.median_days_to_refund} days, the longest ${ref.max_days_to_refund}, and when June closed four extra charges, ${inr2(ref.unrefunded_inr)}`,
    `double charges in June fall from ${asIs.kpis.june.charged_twice} customers to ${check.kpis.june.charged_twice}`,
    `the tills spend ${Math.round(check.kpis.slowdown.till_minutes)} minutes taking payment instead of ${Math.round(asIs.kpis.slowdown.till_minutes)}`,
    `The median wait for a refund falls from ${asIs.kpis.refunds.median_days_to_refund} days to ${billRef.kpis.refunds.median_days_to_refund}`,
    `complaints fall from ${asIs.kpis.refunds.complaints} to ${billRef.kpis.refunds.complaints}`,
    pct(slow.four_ways.till), pct(slow.four_ways.bank), pct(slow.four_ways.charged_once), pct1(june.four_ways.till),
    sc.rrn, sc.bill_id,
  ];
  for (const e of expected) expect(text, e).toContain(e);
  expect(slow.extra_charges - slow.charged_twice).toBe(2); // "two of them three times"
  expect(ref.unrefunded_at_month_end).toBe(4); // "four extra charges"
  expect(june.debited_and_returned).toBe(6); // "Six customers were debited"
  expect(longestReturn).toBeLessThanOrEqual(3); // "within three days"
  expect(weekday(sc.complaint.complaint_ts)).toBe('Tuesday'); // "On Tuesday she phones the store"
  expect(weekday(sc.refunded_ts)).toBe('Sunday'); // "on the following Sunday"
  expect(Math.round(secs(sc.attempts[0].ts, sc.refunded_ts) / 86400)).toBe(8); // "eight days after her shopping"
  expect(st.mdr_on_june_bills.fee_inr).toBeGreaterThan(7500); // "about ₹8,000 a month"
  expect(st.mdr_on_june_bills.fee_inr).toBeLessThan(8500);
  expect(billRef.kpis.refunds.unrefunded_at_month_end).toBe(0); // "nothing is left in suspense"
});

test('the payments post renders its figures without JavaScript', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('payments/');
  await expect(page.locator('figure svg[role="img"]:visible')).toHaveCount(1);
  await expect(page.locator('table.docs')).toContainText(st.scene.rrn);
  await expect(page.locator('table.pay-ways')).toContainText(pct(slow.four_ways.charged_once));
  await expect(page.locator('table.policy-table tbody tr')).toHaveCount(4);
  await ctx.close();
});

test('payments outcome numbers come from the world, and the controls change them', async ({ page }) => {
  const { errors, root } = await open(page);
  const outcome = root.locator('[data-outcome]');
  await expect(outcome).toContainText(String(asIs.kpis.june.charged_twice));
  await expect(outcome).toContainText(String(asIs.kpis.refunds.median_days_to_refund));
  await expect(outcome).toContainText(`${Math.round(asIs.kpis.slowdown.till_minutes)} min`);

  await root.getByRole('radio', { name: 'Wait for the status check' }).check();
  await expect(outcome).toContainText(String(check.kpis.june.charged_twice));
  await expect(outcome).toContainText(`${Math.round(check.kpis.slowdown.till_minutes)} min`);

  await root.getByRole('radio', { name: 'As today: ask for another payment' }).check();
  await root.getByRole('radio', { name: 'Put the bill ID on every UPI request' }).check();
  await expect(outcome).toContainText(String(billRef.kpis.refunds.median_days_to_refund));
  expect(errors).toEqual([]);
});

test('every payments persona renders, and the tabs work from the keyboard', async ({ page }) => {
  const { errors, root } = await open(page);
  for (const t of ['cashier', 'ops', 'recon', 'support', 'finance', 'truth']) {
    await root.locator(`[data-persona="${t}"]`).click();
    await expect(root.locator(`[data-persona="${t}"]`)).toHaveAttribute('aria-selected', 'true');
    await expect(root.locator('[data-panel] .record, [data-panel] .story').first()).toBeVisible();
  }
  await root.locator('[data-persona="cashier"]').click();
  await root.locator('[data-persona="cashier"]').press('ArrowRight');
  await expect(root.locator('[data-persona="ops"]')).toHaveAttribute('aria-selected', 'true');
  await expect(root.locator('[data-persona="ops"]')).toBeFocused();
  expect(errors).toEqual([]);
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
