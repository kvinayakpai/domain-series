// The series' domain KPIs, x-rayed: what each one drives, how it is usually computed, what the
// record behind it cannot see, the check that exposes the gap, the rule an agent needs, and Store
// 014's two numbers (as its systems report the KPI, and as the answer key observed it).
// Numbers come from the world's export and the retail analysis, so they cannot drift from the posts.
import retail from '../data/retail.json';
import ai from '../data/retail-ai.json';
import logistics from '../data/logistics.json';
import payments from '../data/payments.json';
import lai from '../data/logistics-ai.json';
import pai from '../data/payments-ai.json';

export interface Measured { value: string; how: string }
export interface Kpi {
  id: string;
  name: string;
  /** The decisions the KPI drives. */
  drives: string;
  /** How it is usually computed, and from which record. */
  computed: string;
  /** What that record cannot see. */
  blind: string;
  /** The test or independent observation that exposes the gap. */
  check: string;
  /** The rule an agent needs before it acts on the KPI. */
  agent: string;
  reported?: Measured;
  observed?: Measured;
  /** Store 014, in a sentence. */
  example: string;
  /** For the KPI a post is built around: the cost of the gap and how long it took to find. */
  hero?: { scope: string; cost: string; found: string };
}
export interface Domain { id: string; name: string; post: string; kpis: Kpi[] }

const pct = (v: number) => `${Math.round(Math.abs(v) * 100)}%`;
const signed = (v: number) => `${v < 0 ? '−' : '+'}${pct(v)}`;
const inr = (v: number) => `₹${Math.round(v).toLocaleString('en-IN')}`;
const num = (v: number) => Math.round(v).toLocaleString('en-IN');

// ---------- retail ----------
const asIs = retail.scenarios.find((s) => s.key === 'off|today')!;
const ep = retail.story.episode!;
const hero5 = ai.forecast.by_sku['ATTA-WW-5KG'];
const flag = ai.detector.hero_flags[0];
const rec5 = retail.story.kpis.weekly.recorded_sales['ATTA-WW-5KG'];
const base = ai.forecast.series_5kg.map((x) => x.true);
const week = (k: number) => base.slice(k * 7, k * 7 + 7).reduce((a, b) => a + b, 0);
const made = Object.fromEntries(ai.forecast.made_5kg.map((m) => [m.date, m.naive]));
const daysOfSupply = ep.book_on_hand_max / made['2026-06-10'];
const accuracy = retail.record_accuracy;
const countDetail = retail.meta.realism.find((r) => r.check.startsWith('Most item records'))!.detail;
const adj = (sku: string) => Number((countDetail.match(new RegExp(`${sku} ([+-]\\d+)`)) ?? [])[1] ?? 0);
const minus = (v: number) => `${v < 0 ? '−' : '+'}${Math.abs(v)}`;
const milk = Object.fromEntries(retail.milk.map((m) => [m.factor, m]));
const evenings = (f: number) => milk[f].daily_lost.filter((x: number) => x > 0).length;

// ---------- logistics ----------
const lk = logistics.scenarios.find((s) => s.key === 'none|label')!.kpis;
const ls = logistics.story;
const hm = (ts: string) => ts.slice(11, 16);
const foundAfterDays = Math.floor((Date.parse(`${ls.corrections[0].count_ts}:00+05:30`) - Date.parse(`${ls.shipment.arrived_ts}:00+05:30`)) / 86_400_000);

// ---------- payments ----------
const pk = payments.scenarios.find((s) => s.key === 'retry|manual')!;
const slow = payments.story.slowdown;
const june = payments.story.june;
const refunds = payments.story.refunds;
const unmatched = pk.daily.filter((d) => d.date === '2026-06-20' || d.date === '2026-06-21').reduce((a, d) => a + d.unmatched, 0);
// Refund wait as support measures it: from the complaint (the assistant's schema-only answer).
const fromComplaint = Math.round((pai.assistant.questions.find((q) => q.id === 'wait')!.naive as unknown as { value: number }).value);

export const DOMAINS: Domain[] = [
  {
    id: 'retail',
    name: 'Retail and grocery',
    post: 'retail',
    kpis: [
      {
        id: 'osa',
        name: 'On-shelf availability',
        drives: 'Replenishment priorities, store and category reviews, supplier scorecards.',
        computed: 'Book stock: the share of open hours, or days, with stock on hand above zero.',
        blind: 'Stock that is on the books but not on the shelf: in the wrong bay, in the backroom, stolen, or scanned as something else.',
        check: 'Shelf audits, an independent observation. Runs of no sales that the item’s usual rate cannot explain while the books show stock.',
        agent: 'In stock means on the shelf, not on the books. When an item stops selling while the books show stock, ask someone to check the shelf.',
        reported: { value: pct(ai.availability.on_the_books), how: 'from book stock' },
        observed: { value: pct(ai.availability.true_open_hours), how: 'bags on the shelf' },
        example: `5 kg atta in June: the books showed stock ${pct(ai.availability.on_the_books)} of open hours; the shelf had a bag ${pct(ai.availability.true_open_hours)} of them.`,
        hero: {
          scope: '5 kg atta at Store 014, June',
          cost: `${num(asIs.kpis.lost_units)} bags shoppers could not find: ${inr(asIs.kpis.lost_value_inr)} of sales, on one item in one store`,
          found: `After ${Math.round(ep.empty_open_hours)} open hours, by staff restacking the rice. A gap detector on the till lines flags it in ${Math.round(flag.open_hours_to_flag)}.`,
        },
      },
      {
        id: 'lost-sales',
        name: 'Lost sales',
        drives: 'Estimates of what empty shelves cost, and so the business case for every availability fix.',
        computed: 'Nothing records it. It is taken as zero, or estimated as out-of-stock days times average sales.',
        blind: 'The whole number: a shopper who leaves without buying leaves no row anywhere.',
        check: 'Estimate it from censored hours: the sales the item’s pattern expected while the shelf was empty, checked against audits.',
        agent: 'Lost sales are estimated, never recorded. Report them with the method and the hours they cover.',
        reported: { value: '0', how: 'no system records them' },
        observed: { value: `${num(asIs.kpis.lost_units)} bags`, how: inr(asIs.kpis.lost_value_inr) },
        example: `5 kg atta in June: no record shows a lost sale; shoppers asked for ${num(asIs.kpis.lost_units)} bags they could not find.`,
      },
      {
        id: 'lfl',
        name: 'Like-for-like sales growth',
        drives: 'Trading reviews, range and space decisions, conversations with suppliers.',
        computed: 'Recorded sales, week on week or year on year.',
        blind: 'An empty shelf looks like falling demand, and the recovery afterwards looks like growth.',
        check: 'Compare periods outside censored hours, or compare demand estimates instead of sales.',
        agent: 'Before you compare sales across periods, take out the hours the shelf was empty.',
        reported: { value: signed(rec5[1] / rec5[0] - 1), how: 'recorded sales, week of 8 June' },
        observed: { value: signed(week(1) / week(0) - 1), how: 'shoppers who came for it' },
        example: `5 kg atta: sales fell from ${rec5[0]} bags to ${rec5[1]}; shoppers who came for it fell from ${week(0)} to ${week(1)}, after the month-start shop.`,
      },
      {
        id: 'forecast',
        name: 'Forecast accuracy and bias',
        drives: 'Orders, safety stock, staffing, and the trust anyone places in a forecast.',
        computed: 'Forecasts scored against recorded sales: WAPE, MAPE and bias.',
        blind: 'The target is censored too. A forecast that learns the gaps scores well against sales and badly against demand.',
        check: 'Score against unconstrained demand, and look at bias in the weeks with censored hours.',
        agent: 'Score forecasts against estimated demand, not raw sales, wherever the shelf was empty.',
        reported: { value: signed(hero5.naive_vs_recorded.bias), how: 'bias against recorded sales' },
        observed: { value: signed(hero5.naive_vs_true.bias), how: 'bias against shoppers' },
        example: `The store’s 5 kg forecast looks ${pct(hero5.naive_vs_recorded.bias)} too high against sales and is ${pct(hero5.naive_vs_true.bias)} too low against demand. Scored on sales, the better forecast looks worse.`,
      },
      {
        id: 'ira',
        name: 'Inventory record accuracy',
        drives: 'Trust in every number computed from book stock: availability, turns, reorders.',
        computed: 'Counts against the book, at count time only. Between counts it is assumed to be perfect.',
        blind: 'The days between counts, and the reason behind each difference.',
        check: 'Tests that the book agrees with audits and with how the item sells; counts triggered by anomalies, not only the calendar.',
        agent: 'Book stock is a belief: the last count plus transactions. Treat it as an estimate with an error.',
        reported: { value: '100%', how: 'assumed between counts' },
        observed: { value: pct((accuracy.items - accuracy.wrong) / accuracy.items), how: `${accuracy.items - accuracy.wrong} of ${accuracy.items} records right` },
        example: `At the month-end count, ${accuracy.wrong} of Store 014’s ${accuracy.items} item records were wrong. Published studies find most store records wrong.`,
      },
      {
        id: 'days-of-supply',
        name: 'Days of supply and inventory turns',
        drives: 'Working capital, order quantities, markdowns.',
        computed: 'Book stock divided by the forecast (days of supply); cost of sales over average book inventory (turns).',
        blind: 'Phantom stock counts as supply, and a censored forecast stretches it further.',
        check: 'Recompute on observed stock and demand estimates for items with censored hours.',
        agent: 'Days of supply on book stock can be days of nothing on the shelf. Before you hold back an order, check that shoppers can find the stock.',
        reported: { value: `${daysOfSupply.toFixed(1)} days`, how: `${ep.book_on_hand_max} bags on the books` },
        observed: { value: '0 days', how: 'on the shelf' },
        example: `During the gap the books showed ${ep.book_on_hand_max} bags of 5 kg atta, ${daysOfSupply.toFixed(1)} days of supply at ${made['2026-06-10']} a day. The shelf had none.`,
      },
      {
        id: 'shrink',
        name: 'Shrink and count adjustments',
        drives: 'Loss prevention, audit, margin.',
        computed: 'Count adjustments and write-offs, at cost, per item and period.',
        blind: 'An adjustment says the book was wrong, not why. Theft, damage and scan errors look alike.',
        check: 'Pair adjustments: a loss on one item and a gain on its sibling is a scan error, not theft. Pair them across buildings too.',
        agent: 'Explain an adjustment before you act on it. Look for its mirror image.',
        reported: { value: `${minus(adj('MILK-TONED-500ML'))} and ${minus(adj('MILK-FC-500ML'))}`, how: 'toned and full-cream milk' },
        observed: { value: 'one scan error', how: 'mostly one pouch scanned as the other' },
        example: `The month-end count took ${Math.abs(adj('MILK-TONED-500ML'))} pouches off toned milk and added ${Math.abs(adj('MILK-FC-500ML'))} to full-cream: mostly one pouch scanned as the other, not theft.`,
      },
      {
        id: 'fresh-waste',
        name: 'Fresh waste against availability',
        drives: 'Standing orders for milk, bread and produce.',
        computed: 'Write-offs (waste) and sales. Availability is rarely measured for fresh at all.',
        blind: 'Demand above the sell-out is never recorded, so cutting the order always looks free.',
        check: 'The time of each day’s last sale, and an estimate of demand above the sell-out.',
        agent: 'Waste and empty shelves trade off. Never optimise one without estimating the other.',
        reported: { value: inr(milk[0.95].net_inr), how: `margin after waste, up from ${inr(milk[1].net_inr)}` },
        observed: { value: num(milk[0.95].lost), how: `pouches not found, up from ${num(milk[1].lost)}` },
        example: `A 5% leaner toned-milk order lifts the margin after waste from ${inr(milk[1].net_inr)} to ${inr(milk[0.95].net_inr)}, and the milk sells out on ${evenings(0.95)} days in June instead of ${evenings(1)}. Only the answer key sees the shoppers who left without it.`,
      },
    ],
  },
  {
    id: 'logistics',
    name: 'Logistics and supply chain',
    post: 'logistics',
    kpis: [
      {
        id: 'otif',
        name: 'On time, in full (OTIF)',
        drives: 'Supplier and carrier scorecards, fines, warehouse staffing.',
        computed: 'The warehouse’s pick confirmations, or the store’s goods receipts against shipping notices.',
        blind: '“In full” means the label said so. A wrong pack under the right label counts as perfect.',
        check: 'Case-level scans at receipt; warehouse slot counts reconciled with store counts.',
        agent: 'OTIF from documents measures paperwork. Ask how “in full” was verified before you act on it.',
        reported: { value: pct(lk.otif.dc_report), how: 'the warehouse’s report' },
        observed: { value: pct(lk.otif.at_the_shelf), how: 'on time, every case right' },
        example: `June’s ${lk.shipments} deliveries: ${pct(lk.otif.dc_report)} on time and in full by the warehouse’s report, ${pct(lk.otif.scorecard)} on the store’s scorecard, ${pct(lk.otif.at_the_shelf)} with every case what the store ordered.`,
        hero: {
          scope: 'Deliveries to Store 014, June',
          cost: `One pallet line of 1 kg packs booked as 5 kg: the 5 kg shelf empty for ${ls.episode.empty_open_hours} open hours, ${num(ls.episode.lost_units)} bags (${inr(ls.episode.lost_value_inr)}) not sold`,
          found: `${foundAfterDays} days after delivery, when complaints led the manager to count the bay. Pairing the warehouse’s two corrections names the pallet line ${Math.round(lai.mirror.days_to_store_count - lai.mirror.days_to_pair) === 1 ? 'a day' : `${Math.round(lai.mirror.days_to_store_count - lai.mirror.days_to_pair)} days`} sooner.`,
        },
      },
      {
        id: 'fill-rate',
        name: 'Fill rate',
        drives: 'Availability upstream, supplier performance, order planning.',
        computed: 'Cases shipped over cases ordered, from the shipping notice.',
        blind: 'The right quantity of the wrong item.',
        check: 'Item-level verification: scan the case’s barcode, not the slot’s label, or weigh the pallet.',
        agent: 'A filled line is right only if the item is right.',
        reported: { value: `${(lai.fill.by_notice * 100).toFixed(1)}%`, how: 'by the shipping notice' },
        observed: { value: `${(lai.fill.right_item * 100).toFixed(1)}%`, how: 'counting only the right item' },
        example: `Of the ${num(lai.fill.ordered)} cases on June’s store orders, the notices show ${num(lai.fill.shipped)} shipped, ${(lai.fill.by_notice * 100).toFixed(1)}%; ${lai.fill.wrong_item_cases} of those held the wrong item, so ${(lai.fill.right_item * 100).toFixed(1)}% were the item ordered.`,
      },
      {
        id: 'pick-accuracy',
        name: 'Pick accuracy',
        drives: 'Warehouse process design, labour, the cost of errors downstream.',
        computed: 'Pick confirmations, usually a scan of the slot’s label, and later claims.',
        blind: 'A slot scan confirms the place, not the product.',
        check: 'Mirror-image count variances in adjacent slots; store counts on the same days.',
        agent: 'A slot scan is not a product scan. Mirror-image variances in neighbouring slots are one mis-pick.',
        reported: { value: '100%', how: 'every pick confirmed by slot scan' },
        observed: { value: '1 mis-pick', how: `${ls.actual.units_actual} packs of 1 kg as ${ls.line.units} of 5 kg` },
        example: `On 22 June a line was picked from the neighbouring 1 kg slot: ${ls.actual.units_actual} packs of 1 kg shipped as ${ls.line.units} bags of 5 kg. The next day the warehouse wrote off ${Math.abs(ls.dc_adjustments[0].cases)} cases of 1 kg as a “short pick”.`,
      },
      {
        id: 'net-adjustments',
        name: 'Net inventory adjustments',
        drives: 'Inventory accuracy reporting, finance sign-off, loss investigations.',
        computed: 'Count corrections at cost, netted per period and building.',
        blind: 'Offsetting errors cancel. A large mistake can net to almost nothing.',
        check: 'Look at gross corrections, and pair them across items and buildings.',
        agent: 'Pair corrections before you call inventory accurate. Small nets can hide large errors.',
        reported: { value: inr(ls.adjustments_net.value_at_cost_inr), how: 'four corrections, netted' },
        observed: { value: '1 mistake', how: 'behind all four' },
        example: `Four corrections in two buildings, two in the warehouse and two in the store, net to about ${inr(ls.adjustments_net.value_at_cost_inr)} at cost. One mis-pick caused all four.`,
      },
      {
        id: 'on-time',
        name: 'On-time arrival',
        drives: 'Receiving labour, shelf-refill timing, carrier scorecards.',
        computed: 'Trip logs and receipt timestamps against the delivery slot.',
        blind: 'A punctual truck can bring the wrong goods. Arrival time says nothing about the shelf.',
        check: 'Measure shelf-ready time, and pair on-time with in-full checked at case level.',
        agent: 'On time is half a delivery. Judge it with what was on the pallet.',
        reported: { value: `${lk.in_slot} of ${lk.shipments}`, how: 'deliveries in the slot' },
        observed: { value: hm(ls.shipment.arrived_ts), how: 'the wrong pallet, on time' },
        example: `The truck with the wrong pallet arrived at ${hm(ls.shipment.arrived_ts)}, inside its ${hm(ls.shipment.slot_start)}–${hm(ls.shipment.slot_end)} slot. ${lk.in_slot} of June’s ${lk.shipments} deliveries made the slot.`,
      },
    ],
  },
  {
    id: 'payments',
    name: 'Payments',
    post: 'payments',
    kpis: [
      {
        id: 'success-rate',
        name: 'Payment success rate',
        drives: 'Provider choice, incident response, checkout design.',
        computed: 'The till’s or gateway’s approvals over attempts.',
        blind: '“Failed” at the till can mean “not answered in time”. The money may already have moved.',
        check: 'Match each attempt to the provider’s final status by reference, and count late credits.',
        agent: 'A UPI timeout is a question, not a failure. Check the final status before asking for another payment.',
        reported: { value: pct(slow.four_ways.till), how: 'approved at the till' },
        observed: { value: pct(slow.four_ways.bank), how: 'credited at the bank' },
        example: `Between 18:20 and 19:50 on 20 June the till approved ${pct(slow.four_ways.till)} of UPI attempts; ${pct(slow.four_ways.bank)} ended as a credit at the bank. Over all of June the two sit within a point.`,
        hero: {
          scope: 'UPI at Store 014’s tills, Saturday 20 June, 18:20–19:50',
          cost: `${slow.charged_twice} customers charged twice: ${slow.extra_charges} extra charges, ${inr(slow.charged_twice_inr)}`,
          found: `By no system. Each surfaced when a customer complained, and June’s refunds took a median ${refunds.median_days_to_refund} days. Matching each timeout to the provider’s report finds all ${pai.matcher.extra_charges} the next morning.`,
        },
      },
      {
        id: 'charged-twice',
        name: 'Customers charged twice',
        drives: 'Refunds, complaints, trust in the store.',
        computed: 'Complaints, after the fact.',
        blind: 'No record says “charged twice”. A payment that timed out has no reference to join on.',
        check: 'Credits with no approved payment, matched to bills by amount and time.',
        agent: 'A credit with no approved payment is a customer charged twice until proven otherwise.',
        reported: { value: '0', how: 'in any system' },
        observed: { value: `${june.charged_twice} customers`, how: `${june.extra_charges} extra charges, ${inr(june.charged_twice_inr)}` },
        example: `${june.charged_twice} customers paid twice in June, ${slow.charged_twice} of them in the 90-minute slowdown. No table in the store’s records has a column for it.`,
      },
      {
        id: 'match-rate',
        name: 'Reconciliation match rate',
        drives: 'Finance close, suspense balances, refund queues.',
        computed: 'Settlement lines matched automatically over all lines.',
        blind: 'A missing key makes a match impossible, not just unlikely. The unmatched pile is where the customers are.',
        check: 'Carry the bill ID on every UPI request, and age every item in suspense.',
        agent: 'Unmatched credits are customers’ money. Match them by bill, amount and time, then refund.',
        reported: { value: `${unmatched} items`, how: 'parked in suspense, 20–21 June' },
        observed: { value: `${unmatched} extra charges`, how: 'on customers who had paid again' },
        example: `${unmatched} UPI credits on 20 and 21 June had no approved payment behind them. Each was an extra charge on a customer who had already paid again.`,
      },
      {
        id: 'refund-tat',
        name: 'Refund turnaround',
        drives: 'Complaints, customer trust, compliance with the RBI’s turnaround rules.',
        computed: 'Refund date minus complaint date.',
        blind: 'The clock starts at the complaint, not at the extra debit. Customers who never complain never appear.',
        check: 'Measure from the debit, and count refunds made without a complaint.',
        agent: 'Start the clock at the debit, not the complaint.',
        reported: { value: `${fromComplaint} days`, how: 'median, from the complaint' },
        observed: { value: `${pai.find.refund_median_days_from_debit} days`, how: `median, from the extra debit; ${pai.find.not_refunded} not refunded in June` },
        example: `From the complaint, refunds took a median ${fromComplaint} days. From the extra debit, when the customer lost the money, they took ${pai.find.refund_median_days_from_debit}, and ${pai.find.over_tat} of the ${pai.matcher.extra_charges - pai.find.not_refunded} refunds came later than the five days RBI gives banks. When June closed, ${pai.find.not_refunded} extra charges, ${inr(pai.find.not_refunded_inr)}, were still unrefunded; ${pai.find.never_complained} of those customers never complained.`,
      },
      {
        id: 'technical-declines',
        name: 'Technical decline rate',
        drives: 'Provider service levels, routing, incident alerts.',
        computed: 'Declines with technical reason codes over attempts, usually per month.',
        blind: 'Averages hide bursts. A good month can contain a bad hour, and timeouts are often not counted as declines at all.',
        check: 'Watch it by the hour, with timeouts counted, against the switch’s response time.',
        agent: 'Read failure rates by the hour, with timeouts counted, before you trust a monthly rate.',
        reported: { value: `${((june.upi_technical_failures / june.upi_attempts) * 100).toFixed(2)}%`, how: 'technical failures, June' },
        observed: { value: pct(slow.upi_timeouts / slow.upi_attempts), how: 'no answer in 30 s, Saturday evening' },
        example: `Over June, ${((june.upi_technical_failures / june.upi_attempts) * 100).toFixed(2)}% of UPI attempts failed for technical reasons. Between 18:20 and 19:50 on 20 June, ${slow.upi_timeouts} of ${slow.upi_attempts} got no answer within the till’s 30 seconds, and none of them counts as a technical decline.`,
      },
    ],
  },
];

export const KPI_COUNT = DOMAINS.reduce((a, d) => a + d.kpis.length, 0);

/** The KPI a post is built around. */
export function heroKpi(post: string): { domain: Domain; kpi: Kpi } | undefined {
  const domain = DOMAINS.find((d) => d.post === post);
  const kpi = domain?.kpis.find((k) => k.hero);
  return domain && kpi ? { domain, kpi } : undefined;
}
