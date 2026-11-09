// The Oil & Gas season's eighteen KPIs, in reading order: six from the well, five from the pipe and
// the ship, seven from the refinery. A KPI gets its x-ray (what it drives, how it is computed, what
// the record cannot see, the check, the rule for an agent, and Field 014's two numbers) when its
// post is written. Numbers come from src/data/oil-gas/field-014.json, written by
// scripts/oil-gas/generate.py, so they cannot drift from the posts.
import field from '../data/oil-gas/field-014.json';
import well from '../data/oil-gas/well-kpis.json';
import pipe from '../data/oil-gas/pipe-014.json';
import refinery from '../data/oil-gas/refinery-014.json';

export interface Measured { value: string; how: string }
export interface OgKpi {
  id: string;
  name: string;
  part: 'well' | 'pipe' | 'refinery';
  drives?: string;
  computed?: string;
  blind?: string;
  check?: string;
  agent?: string;
  reported?: Measured;
  observed?: Measured;
  /** Field 014 or Refinery 014, in a sentence. */
  example?: string;
}

const s = field.story;
const ws = well.story;
const ps = pipe.story;
const rs = refinery.story;
const num = (v: number) => Math.round(v).toLocaleString('en-US');
const usd = (v: number) => `$${v.toFixed(2)}`;

export const OG_KPIS: OgKpi[] = [
  {
    id: 'og-production',
    name: 'Production',
    part: 'well',
    drives: 'The morning production meeting, which wells get attention, the reservoir model, and each partner’s and the government’s share.',
    computed: 'The field’s fiscal meter, shared out to the wells pro rata on each well’s last test: test rate times hours run, scaled so the wells add up to the meter.',
    blind: 'Anything that changed at a well since its last test. The change is spread across every well in the field, and the field total stays right.',
    check: 'Show each rate with the date of the test behind it; watch the allocation factor as a trend; compare each allocated rate with the pump’s own flow estimate.',
    agent: 'Never report a well’s rate without the date of the test behind it. When the pump’s own data disagrees with the allocated rate, ask for a well test before acting on either.',
    reported: { value: num(s.w14_18mar.allocated), how: 'barrels allocated to Well 14, 18 March' },
    observed: { value: num(s.w14_18mar.produced), how: 'barrels Well 14 produced' },
    example: `Well 14 on 18 March: ${num(s.w14_18mar.allocated)} barrels by the allocation, ${num(s.w14_18mar.produced)} produced. Its last test was ${s.w14_test.age_days_at_stop} days old when its pump stopped.`,
  },
  {
    id: 'og-production-efficiency',
    name: 'Production efficiency',
    part: 'well',
    drives: 'How a field is judged against its potential, where engineers look for lost barrels, and the targets operators and regulators set.',
    computed: 'Oil produced in a period divided by the potential for that period. The potential is often taken from the business plan or an old register.',
    blind: 'A potential set months earlier, or one already net of expected downtime. Losses that fit inside the plan’s allowance never show.',
    check: 'Recompute against what the wells can produce now, from their latest tests; state the potential’s date and basis; list the biggest loss in barrels beside the percentage.',
    agent: 'Report production efficiency against what the wells can produce now, and state the potential’s date and basis. A plan net of expected losses is not a potential.',
    reported: { value: `${ws.pe.pe_plan_pct}%`, how: 'production efficiency, March, against the plan' },
    observed: { value: `${ws.pe.pe_tests_pct}%`, how: 'against what the wells could produce' },
    example: `March at Field 014: ${ws.pe.pe_plan_pct}% against the November plan, ${ws.pe.pe_tests_pct}% against the wells’ own tests. Well 14 alone lost ${num(ws.pe.w14_lost_bbl)} barrels.`,
  },
  {
    id: 'og-deferment',
    name: 'Deferred production',
    part: 'well',
    drives: 'Which losses get engineering time and budget, the reliability programme, and the explanation for any gap to plan.',
    computed: 'A loss log: each time a well or a plant stops, someone files the hours, an estimate of the barrels and a cause from a pick list.',
    blind: 'Losses with no stop, such as a pump producing less while it runs, and the cause of a stop nobody has diagnosed yet, which lands in ‘other’.',
    check: 'Treat a large ‘other’ as a data problem; compare each well’s rate with its potential every day, not only its hours; update the cause after the teardown.',
    agent: 'Treat a large ‘other’ in the loss log as a data problem, not a cause. Find the cause, and count the barrels lost by wells that kept running.',
    reported: { value: num(ws.deferment.esp_logged_bbl), how: 'barrels the loss log put down to pump trips, March' },
    observed: { value: num(ws.deferment.pump_real_bbl), how: 'barrels Well 14’s pump cost' },
    example: `Field 014’s March loss log: ${num(ws.deferment.logged_bbl)} barrels, ${ws.deferment.other_pct}% under ‘other’. Well 14’s pump cost ${num(ws.deferment.pump_real_bbl)}, and ${num(ws.deferment.wear_unlogged_bbl)} of them were never logged.`,
  },
  {
    id: 'og-decline',
    name: 'Decline rate',
    part: 'well',
    drives: 'The reserves estimate, the production forecast, and how much drilling and workover money a field needs to hold its output.',
    computed: 'The fall in a field’s production from one period to the next, often annualized: this month’s daily average against last month’s.',
    blind: 'Why production fell. A pump that stops looks the same as a reservoir that is running out.',
    check: 'Compute decline per producing hour; take wells with mechanical events out; compare with the field’s usual pace before changing a forecast.',
    agent: 'Compute decline on producing hours, with mechanical events taken out, before calling it the reservoir.',
    reported: { value: `${Math.abs(ws.decline.reported_monthly_pct).toFixed(1)}%`, how: 'fall in Field 014’s oil, February to March' },
    observed: { value: `${Math.abs(ws.decline.reservoir_monthly_pct).toFixed(1)}%`, how: 'fall for the reservoir, on the hours the wells ran' },
    example: `March’s fall of ${Math.abs(ws.decline.reported_monthly_pct)}% annualizes to ${ws.decline.reported_annual_pct}% a year. On producing hours, with Well 14 taken out, the field fell ${Math.abs(ws.decline.reservoir_monthly_pct)}%.`,
  },
  {
    id: 'og-esp-run-life',
    name: 'Pump run life',
    part: 'well',
    drives: 'Which pumps are bought, the workover budget, and whether a well’s design gets changed.',
    computed: 'The average number of days the field’s pumps ran before they failed and were pulled.',
    blind: 'Pumps still running, which have not failed yet, and the reason each pump failed. One well’s repeated failures disappear into the average.',
    check: 'Count running pumps as censored in a survival curve; split run life by well and by teardown cause; flag any well whose pumps fail the same way twice.',
    agent: 'Read pump run life by well and by teardown cause, counting pumps still running. A well whose pumps keep failing the same way needs the cause fixed, not another pump.',
    reported: { value: `${ws.run_life.avg_reported_years} years`, how: 'average run life of Field 014’s failed pumps' },
    observed: { value: `${ws.run_life.w14_sand_avg_days} days`, how: 'average run of Well 14’s last four pumps' },
    example: `Field 014’s failed pumps ran ${num(ws.run_life.avg_reported_days)} days on average. Well 14’s last four ran ${ws.run_life.w14_sand_days.join(', ')} and ${ws.run_life.w14_last_days} days, and three teardowns found sand wear.`,
  },
  {
    id: 'og-lifting-cost',
    name: 'Lifting cost',
    part: 'well',
    drives: 'A field’s place in the portfolio, its budget, and when it is judged too costly to keep producing.',
    computed: 'The month’s operating costs divided by the barrels produced, in dollars a barrel.',
    blind: 'Work that was due but not done. A repair that waits for a rig lowers the cost a barrel, and the lost barrels never appear as a cost.',
    check: 'Show the maintenance backlog and its cost beside the KPI; compare costs over a quarter, not a month; add the deferred work back before comparing months.',
    agent: 'Never report a lower lifting cost without the maintenance backlog beside it. Work that waited is a cost moved, not a cost saved.',
    reported: { value: usd(ws.lifting.usd_per_bbl['2026-03']), how: 'lifting cost a barrel, March' },
    observed: { value: usd(ws.lifting.mar_with_workover), how: 'with the workover that waited for a rig' },
    example: `Field 014’s lifting cost fell from ${usd(ws.lifting.usd_per_bbl['2026-02'])} in February to ${usd(ws.lifting.usd_per_bbl['2026-03'])} in March, while Well 14’s $${num(ws.lifting.workover_usd)} workover waited for a rig.`,
  },
  {
    id: 'og-throughput',
    name: 'Throughput',
    part: 'pipe',
    drives: 'Pipeline tariffs and schedules, and how much crude a refinery plans to receive.',
    computed: 'The volume the pipeline moved in a day, from its meters, in gross barrels: oil plus whatever water and sediment travel with it.',
    blind: 'What the barrels were. Water moves through a pipe as easily as oil, so a rise in water reads as steady throughput.',
    check: 'Report net barrels of oil beside the gross, with the water; alert when water crosses the crude limit; compare the water readings at both ends.',
    agent: 'Count throughput in net barrels of oil, with the water reported beside it. A barrel moved is not a barrel of oil.',
    reported: { value: num(ps.throughput.gross_bbl), how: 'barrels the pipeline moved, March' },
    observed: { value: num(ps.throughput.water_bbl), how: 'of them were water' },
    example: `The pipeline moved ${num(ps.throughput.gross_bbl)} barrels in March. ${num(ps.throughput.water_bbl)} were water, most of it while a heater-treater at Field 014 was down.`,
  },
  {
    id: 'og-loss-gain',
    name: 'Loss and gain',
    part: 'pipe',
    drives: 'Whether a pipeline’s meters are trusted, who pays for missing oil, and when someone looks for a leak.',
    computed: 'Barrels received minus barrels sent, each day, as a percentage, checked against a tolerance band.',
    blind: 'Which way the gap points. A meter that is off the same way every day stays inside the band.',
    check: 'Alert on the sign and the trend, such as seven days in a row the same way; track meter factors between provings; never let a proving slip without a check.',
    agent: 'Alert on the sign and the trend of loss and gain, not only on its size. A meter that is off the same way every day is wrong, even inside tolerance.',
    reported: { value: `${ps.loss_gain.days_inside} of 31`, how: 'days inside the tolerance band, March' },
    observed: { value: `${ps.loss_gain.days_positive} of 31`, how: 'days the receipt meter read high' },
    example: `Every day of March was inside ±${ps.loss_gain.tolerance_pct.toFixed(2)}%, and every day was a gain: Refinery 014’s receipt meter counted ${num(ps.loss_gain.gain_bbl)} barrels the pipeline never carried.`,
  },
  {
    id: 'og-tank-stock',
    name: 'Tank stock accuracy',
    part: 'pipe',
    drives: 'Crude scheduling, how long a refinery can run, and month-end stock in the accounts.',
    computed: 'The book stock, a running sum of metered receipts and issues, against the gauged stock from the tank’s level, with free water taken off.',
    blind: 'Errors both records share. A meter that reads high, a sampler that misses water and a failed water probe can all point the same way.',
    check: 'Decide on gauged stock with free water removed; treat a failed water probe as an open measurement; dip by hand when it is out; reconcile against an independent record.',
    agent: 'Decide on gauged stock with the free water removed, and never read a failed water probe as zero. When the book and the gauge agree, check what they could both be missing.',
    reported: { value: `${ps.tank.diff_pct_31.toFixed(2)}%`, how: 'book against gauge, tank T-104, 31 March' },
    observed: { value: num(ps.tank.dip_free_water_31), how: 'barrels of water both counted as crude' },
    example: `T-104’s book and gauge were ${ps.tank.diff_pct_31.toFixed(2)}% apart on 31 March. The month-end dip found ${num(ps.tank.dip_free_water_31)} barrels of free water, and the probe that should have seen it had read zero since 2 March.`,
  },
  {
    id: 'og-methane',
    name: 'Methane intensity',
    part: 'pipe',
    drives: 'A company’s climate targets and reports, regulators’ attention, and buyers’ choice of gas.',
    computed: 'Methane emitted as a share of the gas sold, with the methane usually estimated from emission factors for each piece of equipment.',
    blind: 'A leak. Emission factors describe what equipment usually emits, so an inventory built from them stays the same until someone measures.',
    check: 'Put confirmed measurements from satellites, aircraft or surveys into the KPI; treat a jump in unaccounted gas as a leak; survey after maintenance.',
    agent: 'A confirmed plume overrides the estimate. Report methane from measurements when you have them, and treat a jump in unaccounted gas as a leak until a survey says otherwise.',
    reported: { value: `${ps.methane.mi_reported_pct.toFixed(2)}%`, how: 'methane intensity, March, by the inventory' },
    observed: { value: `${ps.methane.mi_real_pct.toFixed(1)}%`, how: 'with the leak a satellite saw' },
    example: `Field 014’s inventory put March at ${ps.methane.inventory_t} tonnes of methane. Compressor K-2’s blowdown valve released ${ps.methane.leak_t.toFixed(0)} tonnes in ten days, and a satellite saw the plume on 14 March.`,
  },
  {
    id: 'og-ship-waiting',
    name: 'Ship waiting time',
    part: 'pipe',
    drives: 'Demurrage bills, berth planning, and when a refinery can count on its crude.',
    computed: 'The time between a ship’s scheduled berthing window and its berthing, from the port’s own schedule.',
    blind: 'Waiting before the schedule was written. A window set after the delay was known makes a long wait look short.',
    check: 'Measure from the notice of readiness; show demurrage owed beside waiting time; compare the schedule with each ship’s statement of facts.',
    agent: 'Measure ship waiting from the notice of readiness, and show the demurrage beside it. A schedule written after the delay cannot measure the delay.',
    reported: { value: `${ps.ship.reported_wait_days.toFixed(1)} days`, how: 'the replacement cargo’s wait, by the port’s schedule' },
    observed: { value: `${ps.ship.real_wait_days.toFixed(1)} days`, how: 'from its notice of readiness' },
    example: `Refinery 014’s replacement cargo waited ${ps.ship.real_wait_days.toFixed(1)} days at anchor from its notice of readiness, ${ps.ship.reported_wait_days.toFixed(1)} by the port’s schedule, and ran up $${num(ps.ship.demurrage_usd)} of demurrage.`,
  },
  {
    id: 'og-utilization',
    name: 'Refinery utilization',
    part: 'refinery',
    drives: 'How a refinery is judged on any given day, crude buying, and what a country’s fuel supply looks like.',
    computed: 'Crude processed divided by the crude unit’s nameplate capacity.',
    blind: 'Which crude went in and what it made. A crude unit can run full on a crude the rest of the refinery was not built for.',
    check: 'Show the crude slate and the margin beside utilization; watch the units that make the money, not only the crude unit; flag a slate far from the plan.',
    agent: 'Report utilization with the crude slate and the margin beside it. A full crude unit says nothing about what the barrels are worth.',
    reported: { value: `${rs.utilization.pct}%`, how: 'crude unit utilization, March' },
    observed: { value: `${rs.utilization.light_share_pct}%`, how: `of the crude was light, against ${rs.utilization.plan_light_pct}% in the plan` },
    example: `Refinery 014 ran at ${rs.utilization.pct}% in March. Half its crude was light crude it was not built for, and its realised margin was $${rs.margin.realised.toFixed(2)} a barrel against $${rs.margin.plan.toFixed(2)} in the plan.`,
  },
  {
    id: 'og-margin',
    name: 'Refining margin',
    part: 'refinery',
    drives: 'Run rates, crude buying, which products to make, and what investors and governments think a refiner earns.',
    computed: 'Product prices minus crude prices from price screens, as a crack spread or a benchmark margin for a typical refinery.',
    blind: 'What this refinery paid and made: its crude premiums, freight, demurrage and its own yields on the crude it actually ran.',
    check: 'Report the realised margin beside the benchmark; walk the gap step by step; value the slate the refinery actually ran.',
    agent: 'Never report the benchmark crack or screen margin as our margin. Show the realised margin with the crude premiums, freight and yields that separate them.',
    reported: { value: `$${rs.margin.screen.toFixed(2)}`, how: 'benchmark margin a barrel, March' },
    observed: { value: `$${rs.margin.realised.toFixed(2)}`, how: 'Refinery 014’s realised margin' },
    example: `Refinery 014’s screen margin for March was $${rs.margin.screen.toFixed(2)} a barrel. After crude premiums, freight, demurrage and its own slate it earned $${rs.margin.realised.toFixed(2)}.`,
  },
  {
    id: 'og-diesel-yield',
    name: 'Diesel yield',
    part: 'refinery',
    drives: 'How much of the most valuable product a refinery sells, and how the planners judge the crude they buy.',
    computed: 'Diesel produced divided by crude processed, for the month, against the plan.',
    blind: 'Diesel made from feed drawn out of intermediate tanks. A yield can stay on plan for weeks on stock made from last month’s crude.',
    check: 'Compute yields from a balance that includes intermediate tank changes; read them by week; watch the feed tanks of the units that make diesel.',
    agent: 'Compute yields from a balance that includes changes in intermediate tanks. A yield drawn from stock is borrowed, not made.',
    reported: { value: `${rs.diesel.yield_pct}%`, how: `diesel yield, March, plan ${rs.diesel.plan_pct}%` },
    observed: { value: `${rs.diesel.own_pct}%`, how: 'from March’s own crude' },
    example: `Refinery 014’s diesel yield was ${rs.diesel.yield_pct}% in March, on plan, while its VGO tank fell from ${num(rs.diesel.vgo_start)} barrels to its minimum. From March’s own crude it was ${rs.diesel.own_pct}%.`,
  },
  {
    id: 'og-energy-intensity',
    name: 'Energy intensity',
    part: 'refinery',
    drives: 'Fuel costs, carbon reporting, and the case for energy-saving projects.',
    computed: 'Energy used, as fuel, steam and power, divided by crude processed, compared month on month.',
    blind: 'How busy the refinery was. Much of a refinery’s energy is fixed, so a fuller month uses less energy a barrel without being more efficient.',
    check: 'Compare energy with what the same runs should use; compare months at like throughput and crude; watch furnace fuel and fouling directly.',
    agent: 'Compare energy intensity at like throughput and crude. A busier month uses less energy a barrel without being more efficient.',
    reported: { value: `${rs.energy.ei_change_pct}%`, how: 'energy a barrel, February to March' },
    observed: { value: `+${rs.energy.mar_over_expected_pct.toFixed(1)}%`, how: 'energy above what the same runs should use, March' },
    example: `Refinery 014 used ${Math.abs(rs.energy.ei_change_pct)}% less energy a barrel in March than in February, because it ran fuller. Against what the same runs should use, it used ${rs.energy.mar_over_expected_pct.toFixed(1)}% more.`,
  },
  {
    id: 'og-availability',
    name: 'Mechanical availability',
    part: 'refinery',
    drives: 'Maintenance budgets, reliability rankings, and how hard a refinery can be run.',
    computed: 'The share of time process units were not down for unplanned repairs.',
    blind: 'Failures that cost no downtime. A spared pump can trip again and again while its spare carries the unit.',
    check: 'Count trips per equipment tag, spared or not; track how long a spare runs alone; treat a repeat cause as an open failure.',
    agent: 'Count trips per equipment tag, including pumps with a running spare. A spare that keeps saving the unit is a failure waiting for a second one.',
    reported: { value: `${rs.availability.pct}%`, how: 'mechanical availability, March' },
    observed: { value: `${rs.availability.trips}`, how: 'trips of crude charge pump P-101A' },
    example: `Refinery 014’s mechanical availability was ${rs.availability.pct}% in March. Its crude charge pump P-101A tripped ${rs.availability.trips} times, and the spare ran alone for ${rs.availability.spare_days} days.`,
  },
  {
    id: 'og-turnaround',
    name: 'Turnaround performance',
    part: 'refinery',
    drives: 'How a refinery’s maintenance teams are judged, when units restart, and the next turnaround’s scope.',
    computed: 'A turnaround’s days and cost against its plan: on time, on budget.',
    blind: 'The work that was left undone to stay on time, including safety-critical inspections moved to a later date.',
    check: 'Report deferred work orders and deferred safety-critical inspections beside the schedule; track the deferred list to closure.',
    agent: 'Report a turnaround’s deferred scope beside its schedule, especially safety-critical inspections. On time with work left undone is a schedule kept, not a job done.',
    reported: { value: 'On time', how: 'reformer turnaround, restarted as planned' },
    observed: { value: `${rs.turnaround.deferred_orders}`, how: `work orders deferred, ${rs.turnaround.deferred_sce} of them safety-critical inspections` },
    example: `Refinery 014’s reformer turnaround finished on schedule and under budget, with ${rs.turnaround.deferred_orders} work orders deferred, ${rs.turnaround.deferred_sce} of them safety-critical inspections.`,
  },
  {
    id: 'og-process-safety',
    name: 'Process safety events',
    part: 'refinery',
    drives: 'Safety reports to the board, regulators and the public, and how a refinery’s safety is judged.',
    computed: 'The number of Tier 1 and Tier 2 process safety events, releases of hazardous material above set thresholds.',
    blind: 'Risk that has not yet released anything: overdue safety-critical inspections and the challenges to safety systems counted in Tiers 3 and 4.',
    check: 'Report overdue safety-critical work and Tier 3 challenges beside the event count; trend them monthly; tie every deferral to a risk review.',
    agent: 'Report overdue safety-critical work and Tier 3 challenges beside the event count. Zero events on a growing backlog is not zero risk.',
    reported: { value: '0', how: 'Tier 1 and Tier 2 process safety events, March' },
    observed: { value: `${rs.safety.overdue_mar}`, how: `safety-critical inspections overdue, up from ${rs.safety.overdue_feb}` },
    example: `Refinery 014 had no Tier 1 or Tier 2 event in March, while overdue safety-critical inspections rose from ${rs.safety.overdue_feb} to ${rs.safety.overdue_mar} and Tier 3 challenges from ${rs.safety.tier3_feb} to ${rs.safety.tier3_mar}.`,
  },
];

/** A KPI's number in the Oil & Gas season, 1 to 18. */
export const ogKpiNumber = (id: string) => OG_KPIS.findIndex((k) => k.id === id) + 1;
export const OG_KPI_COUNT = OG_KPIS.length;
export const ogKpi = (id: string | undefined) => OG_KPIS.find((k) => k.id === id);
