// One dairy item (1 L milk) through DC -> store -> till, for one week.
// Seeded and deterministic: the same inputs always give the same numbers.
// Parameters are chosen for the story; this does not read Domain Explorer tables.

export interface Controls {
  safetyStock: number;   // units held above forecast cover
  forecastWindow: number; // days of history averaged for the forecast
  delayDays: number;      // extra days added to the shipment on day 3
}

export interface DayRow {
  day: string;
  demand: number;
  sold: number;
  lostSales: number;
  onHandEnd: number;
  shrink: number;
  ordered: number;
  received: number;
  deliveryOk: boolean | null; // null when nothing was received that day
}

export interface PayRow { rail: 'UPI' | 'Card'; attempts: number; approved: number; declines: Record<string, number>; }

export interface Result {
  days: DayRow[];
  onShelf: number;        // share of demand served from shelf
  otif: number;           // share of shipments on time and in full
  dockToStockHours: number;
  shrinkUnits: number;
  pay: PayRow[];
  approvalRate: number;
  takeRate: number;       // net merchant fees / gross volume
  settledIn: string;
}

// mulberry32: small, fast, seedable PRNG
function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const WEEKDAY = [0.9, 0.9, 0.95, 1.0, 1.15, 1.35, 1.1];
const BASE = 120;          // units per day
const DC_CAPACITY_SHORT = 0.03; // chance the DC ships short
const LT = 1;             // normal DC -> store lead time, days
const SHRINK_RATE = 0.005; // share of on-hand lost per day
const PRICE = 68;          // INR per unit
const BASKET_OTHER = 350;  // INR, rest of the basket
const MDR = { UPI: 0, Card: 0.018 }; // merchant discount rate

export function simulate(c: Controls, seed = 42): Result {
  const r = rng(seed);
  const noise = () => 1 + (r() - 0.5) * 0.16;

  // 14 days of history before the week, to seed the forecast
  const history: number[] = [];
  for (let i = 0; i < 14; i++) history.push(Math.round(BASE * noise()));

  const window = Math.min(c.forecastWindow, history.length);
  const forecast = () => history.slice(-window).reduce((a, b) => a + b, 0) / window;

  let onHand = 120;
  const pipeline: { arrive: number; qty: number; promised: number; inFull: boolean; onTime: boolean }[] = [];
  const days: DayRow[] = [];
  let demandTotal = 0, servedTotal = 0, shrinkUnits = 0;
  let shipments = 0, good = 0;
  const pay: Record<'UPI' | 'Card', PayRow> = {
    UPI: { rail: 'UPI', attempts: 0, approved: 0, declines: {} },
    Card: { rail: 'Card', attempts: 0, approved: 0, declines: {} },
  };
  let gross = 0, fees = 0;

  for (let d = 0; d < 7; d++) {
    // receipts due today
    let received = 0;
    const arriving = pipeline.filter((p) => p.arrive === d);
    for (const p of arriving) {
      received += p.qty;
      shipments++;
      if (p.onTime && p.inFull) good++;
    }
    onHand += received;

    // demand, sales, lost sales
    const demand = Math.round(BASE * WEEKDAY[d] * noise());
    const sold = Math.min(demand, onHand);
    onHand -= sold;
    demandTotal += demand;
    servedTotal += sold;

    // shrink (theft, waste, admin error)
    const shrink = Math.round(onHand * SHRINK_RATE);
    onHand -= shrink;
    shrinkUnits += shrink;

    // replenishment at 18:00 for delivery later
    history.push(demand);
    const target = forecast() * (LT + 1) + c.safetyStock;
    const ordered = Math.max(0, Math.round(target - onHand - pipeline.filter((p) => p.arrive > d).reduce((a, p) => a + p.qty, 0)));
    if (ordered > 0) {
      const short = r() < DC_CAPACITY_SHORT;
      const qty = short ? Math.round(ordered * 0.9) : ordered;
      const delay = d === 2 ? c.delayDays : 0;
      const arrive = d + LT + delay;
      pipeline.push({ arrive, qty, promised: d + LT, inFull: !short, onTime: delay === 0 });
    }

    // till transactions: a share of the day's sold units
    const txns = Math.max(1, Math.round(sold / 2.2));
    for (let t = 0; t < txns; t++) {
      const rail: 'UPI' | 'Card' = r() < 0.58 ? 'UPI' : 'Card';
      const amount = PRICE * (1 + Math.floor(r() * 3)) + BASKET_OTHER * r();
      const row = pay[rail];
      row.attempts++;
      const declineP = rail === 'UPI' ? 0.025 : 0.04;
      if (r() >= declineP) {
        row.approved++;
        gross += amount;
        fees += amount * MDR[rail];
      } else {
        const pick = r();
        const reason = rail === 'UPI'
          ? (pick < 0.4 ? 'Insufficient funds' : pick < 0.75 ? 'Bank timeout' : 'Velocity limit')
          : (pick < 0.5 ? 'Do not honour' : pick < 0.8 ? 'Issuer timeout' : 'Expired card');
        row.declines[reason] = (row.declines[reason] || 0) + 1;
      }
    }

    days.push({
      day: DAYS[d], demand, sold, lostSales: demand - sold, onHandEnd: onHand, shrink,
      ordered, received,
      deliveryOk: arriving.length ? arriving.every((p) => p.onTime && p.inFull) : null,
    });
  }

  const totalAttempts = pay.UPI.attempts + pay.Card.attempts;
  const totalApproved = pay.UPI.approved + pay.Card.approved;

  return {
    days,
    onShelf: servedTotal / demandTotal,
    otif: shipments ? good / shipments : 1,
    dockToStockHours: 3.5 + (c.delayDays > 0 ? 0.5 : 0),
    shrinkUnits,
    pay: [pay.UPI, pay.Card],
    approvalRate: totalApproved / totalAttempts,
    takeRate: gross ? fees / gross : 0,
    settledIn: 'UPI settles same day; card settles T+1',
  };
}
