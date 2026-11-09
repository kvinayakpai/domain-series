#!/usr/bin/env python3
"""Refinery 014, March 2026: a 240,000 barrel-a-day refinery on India's west coast, built for
medium sour Gulf crude, in the month that crude stopped.

Units: a crude and vacuum unit; a hydrocracker that turns vacuum gasoil (VGO) into diesel, jet and
naphtha, fed from the crude unit and a VGO tank; a naphtha reformer, in its turnaround until
15 March; and crude charge pumps P-101A and B. Prices are the simulation's own monthly averages,
as differentials to Dubai crude.

In March 2026:
- Gulf crude runs out on 9 March; light crude from Fujairah replaces it, then Arab Light from
  Yanbu and West African crude arrive late in the month (utilization, KPI 12)
- the screen margin for the planned slate is high; the realised margin carries the premiums,
  freight and the lighter slate (crack spread and margin, KPI 13)
- the hydrocracker keeps running full on the VGO tank, which hits its minimum on 21 March
  (diesel yield, KPI 14)
- the refinery runs harder than in February, while its preheat train fouls after a desalter
  upset (energy intensity, KPI 15)
- P-101A trips three times; P-101B carries the crude unit each time (availability, KPI 16)
- the reformer turnaround restarts on schedule with part of its scope deferred (turnaround, KPI 17)
- no process safety event, while overdue safety-critical inspections grow (process safety, KPI 18)

Standard library only and seeded, so every run writes the same files.

    python3 scripts/oil-gas/refinery.py
"""
from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rng = random.Random(1412)
DAYS = [(date(2026, 3, 1) + timedelta(days=i)).isoformat() for i in range(31)]
N = 31
CAPACITY = 240_000  # nameplate crude capacity, barrels a day

# ---------- the crude slate ----------
# Shares of medium sour (Gulf), light (Murban from Fujairah, West African) and domestic (Field 014) crude.
def slate(i: int) -> dict[str, float]:
    d = i + 1
    if d <= 9:
        return {"medium": 0.96, "light": 0.0, "domestic": 0.04}
    if d <= 21:
        return {"medium": 0.0, "light": 0.96, "domestic": 0.04}
    if d <= 27:
        return {"medium": 0.60, "light": 0.36, "domestic": 0.04}
    return {"medium": 0.50, "light": 0.46, "domestic": 0.04}


PLAN_SLATE = {"medium": 0.92, "light": 0.04, "domestic": 0.04}
PLAN_RUN = 235_000
# Straight-run yields, share of each crude's volume.
CUT = {
    "medium": {"lpg": 0.02, "naphtha": 0.17, "kero": 0.12, "diesel": 0.24, "vgo": 0.28, "residue": 0.17},
    "light": {"lpg": 0.03, "naphtha": 0.27, "kero": 0.15, "diesel": 0.25, "vgo": 0.18, "residue": 0.12},
    "domestic": {"lpg": 0.02, "naphtha": 0.20, "kero": 0.12, "diesel": 0.26, "vgo": 0.26, "residue": 0.14},
}
HCU_CAP = 65_000
HCU_YIELD = {"diesel": 0.55, "kero": 0.18, "naphtha": 0.19, "lpg": 0.08}
VGO_START, VGO_MIN, VGO_MAX = 300_000, 30_000, 340_000
REF_CAP = 35_000  # reformer naphtha feed
REF_RESTART = "2026-03-15T18:00"
REF_YIELD = {"gasoline": 0.85, "lpg": 0.10}  # reformate to the gasoline pool; the rest is gas and hydrogen

run = [round(236_000 + rng.gauss(0, 1_200)) for _ in range(N)]
vgo_tank = VGO_START
rows = []
for i in range(N):
    sl = slate(i)
    cut = {k: sum(run[i] * sl[c] * CUT[c][k] for c in sl) for k in CUT["medium"]}
    hcu_feed = min(HCU_CAP, cut["vgo"] + (vgo_tank - VGO_MIN))
    vgo_tank += cut["vgo"] - hcu_feed
    vgo_sold = max(vgo_tank - VGO_MAX, 0)
    vgo_tank -= vgo_sold
    ref_frac = 0.0 if DAYS[i] < REF_RESTART[:10] else (0.25 if DAYS[i] == REF_RESTART[:10] else 1.0)
    ref_feed = min(REF_CAP * ref_frac, cut["naphtha"] + HCU_YIELD["naphtha"] * hcu_feed)
    prod = {
        "lpg": cut["lpg"] + HCU_YIELD["lpg"] * hcu_feed + REF_YIELD["lpg"] * ref_feed,
        "naphtha": cut["naphtha"] + HCU_YIELD["naphtha"] * hcu_feed - ref_feed,
        "gasoline": REF_YIELD["gasoline"] * ref_feed,
        "kero": cut["kero"] + HCU_YIELD["kero"] * hcu_feed,
        "diesel": cut["diesel"] + HCU_YIELD["diesel"] * hcu_feed,
        "vgo_sold": vgo_sold,
        "residue": cut["residue"],
    }
    rows.append({"date": DAYS[i], "run": run[i], "slate": sl, "vgo_made": cut["vgo"], "hcu_feed": hcu_feed, "vgo_tank": vgo_tank,
                 "ref_feed": ref_feed, "prod": prod})

total_run = sum(run)
util = total_run / (CAPACITY * N)
light_share = sum(r["run"] * r["slate"]["light"] for r in rows) / total_run
medium_share = sum(r["run"] * r["slate"]["medium"] for r in rows) / total_run
hcu_util = [r["hcu_feed"] / HCU_CAP for r in rows]
tank_min_day = next(r["date"] for r in rows if r["vgo_tank"] <= VGO_MIN + 1)
diesel = sum(r["prod"]["diesel"] for r in rows)
diesel_yield = diesel / total_run
vgo_drawn = VGO_START - rows[-1]["vgo_tank"]
diesel_from_tank = HCU_YIELD["diesel"] * vgo_drawn
diesel_yield_own = (diesel - diesel_from_tank) / total_run


def plan_day():
    """The plan's barrel: the planned slate and run, hydrocracker full, reformer running."""
    cut = {k: sum(PLAN_RUN * PLAN_SLATE[c] * CUT[c][k] for c in PLAN_SLATE) for k in CUT["medium"]}
    hcu = min(HCU_CAP, cut["vgo"])
    ref = REF_CAP
    return {
        "lpg": cut["lpg"] + HCU_YIELD["lpg"] * hcu + REF_YIELD["lpg"] * ref,
        "naphtha": cut["naphtha"] + HCU_YIELD["naphtha"] * hcu - ref,
        "gasoline": REF_YIELD["gasoline"] * ref,
        "kero": cut["kero"] + HCU_YIELD["kero"] * hcu,
        "diesel": cut["diesel"] + HCU_YIELD["diesel"] * hcu,
        "vgo_sold": cut["vgo"] - hcu,
        "residue": cut["residue"],
    }


plan = plan_day()
plan_diesel_yield = plan["diesel"] / PLAN_RUN
# The week the stored feed ran out: same crude run, less diesel.
week = [r for r in rows if "2026-03-21" <= r["date"] <= "2026-03-21"]
first_week = [r for r in rows if r["date"] <= "2026-03-09"]
low = [r for r in rows if r["date"] == tank_min_day][0]

# ---------- KPI 13: margins, US dollars a barrel ----------
CRACK = {"lpg": -16.0, "naphtha": -8.0, "gasoline": 17.0, "kero": 58.0, "diesel": 48.0, "vgo_sold": 5.0, "residue": -12.0}
PREMIUM = {"medium": 2.0, "light": 14.5, "domestic": 3.0}  # each crude's price over Dubai, delivered terms aside
FREIGHT = {"medium": 1.6, "light": 5.8, "domestic": 0.4}  # freight, war-risk insurance and pipeline tariff
PLAN_PREMIUM = sum(PLAN_SLATE[c] * PREMIUM["medium" if c == "medium" else c] for c in PLAN_SLATE)
FUEL_AND_LOSS = 2.2  # own fuel and losses, a barrel of crude, at plan
DEMURRAGE_USD = 694_000  # the replacement cargo's demurrage (pipe-014.json)


def product_value(prod: dict, crude: float) -> float:
    return sum(prod[k] * CRACK[k] for k in prod) / crude


screen = product_value(plan, PLAN_RUN) - FUEL_AND_LOSS  # the benchmark: published cracks on the planned barrel, before crude premiums
plan_margin = screen - PLAN_PREMIUM - sum(PLAN_SLATE[c] * FREIGHT[c] for c in PLAN_SLATE)
actual_value = sum(sum(r["prod"][k] * CRACK[k] for k in r["prod"]) for r in rows) / total_run
prem = sum(r["run"] * sum(r["slate"][c] * PREMIUM[c] for c in r["slate"]) for r in rows) / total_run
frt = sum(r["run"] * sum(r["slate"][c] * FREIGHT[c] for c in r["slate"]) for r in rows) / total_run
dem = DEMURRAGE_USD / total_run

# ---------- KPI 15: energy ----------
FIXED_GJ = 52_000
VAR_GJ = 0.30  # per barrel of crude
HCU_GJ, REF_GJ = 0.12, 0.25  # per barrel of feed
FOUL_FROM = "2026-03-12"  # desalter upset from the wet crude, preheat train fouling from here
FOUL_PCT = 0.06
STARTUP_GJ = {"2026-03-15": 4_000, "2026-03-16": 3_000}
FEB_DAYS = 28
feb_run = [round(218_400 + rng.gauss(0, 1_500)) for _ in range(FEB_DAYS)]
feb_ref = [REF_CAP if k + 1 < 23 else 0 for k in range(FEB_DAYS)]  # reformer turnaround from 23 February


def expected(run_bbl, hcu, ref):
    return FIXED_GJ + VAR_GJ * run_bbl + HCU_GJ * hcu + REF_GJ * ref


feb_energy = [expected(feb_run[k], HCU_CAP, feb_ref[k]) * (1 + rng.gauss(0, 0.004)) for k in range(FEB_DAYS)]
mar_energy = []
for r in rows:
    e = expected(r["run"], r["hcu_feed"], r["ref_feed"])
    if r["date"] >= FOUL_FROM:
        e += FOUL_PCT * VAR_GJ * r["run"]
    e += STARTUP_GJ.get(r["date"], 0)
    mar_energy.append(e * (1 + rng.gauss(0, 0.004)))
ei_feb = sum(feb_energy) / sum(feb_run)
ei_mar = sum(mar_energy) / total_run
idx_feb = sum(feb_energy) / sum(expected(feb_run[k], HCU_CAP, feb_ref[k]) for k in range(FEB_DAYS)) * 100
idx_mar = sum(mar_energy) / sum(expected(r["run"], r["hcu_feed"], r["ref_feed"]) for r in rows) * 100
util_feb = sum(feb_run) / (CAPACITY * FEB_DAYS)

# ---------- KPI 16: the crude charge pumps ----------
TRIPS = [
    {"tag": "P-101A", "trip": "2026-03-08T04:12", "cause": "high vibration, drive-end bearing", "back": "2026-03-10T06:30"},
    {"tag": "P-101A", "trip": "2026-03-17T22:40", "cause": "mechanical seal leak", "back": "2026-03-20T08:10"},
    {"tag": "P-101A", "trip": "2026-03-29T13:05", "cause": "high vibration, drive-end bearing", "back": None},
]
SPARE_START_S = [7, 9, 6]
spare_hours = 0.0
for t in TRIPS:
    end = datetime.fromisoformat(t["back"]) if t["back"] else datetime(2026, 4, 1)
    spare_hours += (end - datetime.fromisoformat(t["trip"])).total_seconds() / 3600
UNPLANNED = [{"unit": "diesel hydrotreater", "from": "2026-03-25T11:20", "to": "2026-03-25T15:35", "cause": "recycle gas compressor trip"}]
UNITS = ["crude and vacuum unit", "hydrocracker", "diesel hydrotreater", "sulphur recovery", "hydrogen unit"]
unit_hours = len(UNITS) * N * 24
down_hours = sum((datetime.fromisoformat(u["to"]) - datetime.fromisoformat(u["from"])).total_seconds() / 3600 for u in UNPLANNED)
mech_avail = 1 - down_hours / unit_hours
B_ALARM = "2026-03-31T06:00"

# ---------- KPI 17: the reformer turnaround ----------
TA = {"unit": "naphtha hydrotreater and reformer", "start": "2026-02-23T06:00", "planned_end": "2026-03-15T18:00", "actual_end": "2026-03-15T18:00",
      "planned_orders": 1240, "found_orders": 182, "completed_orders": 1038, "planned_sce": 96, "completed_sce": 55,
      "budget_usd": 14_200_000, "actual_usd": 13_900_000, "decided": "2026-03-03"}
TA["deferred_orders"] = TA["planned_orders"] + TA["found_orders"] - TA["completed_orders"]
TA["deferred_sce"] = TA["planned_sce"] - TA["completed_sce"]
TA["deferred_pct_of_scope"] = round(TA["deferred_orders"] / (TA["planned_orders"] + TA["found_orders"]) * 100)
TA["days"] = round((datetime.fromisoformat(TA["actual_end"]) - datetime.fromisoformat(TA["start"])).total_seconds() / 86400, 1)

# ---------- KPI 18: process safety ----------
PSE = [
    {"month": "2026-01", "tier1": 0, "tier2": 0, "tier3": 2, "overdue_sce_inspections": 16},
    {"month": "2026-02", "tier1": 0, "tier2": 0, "tier3": 2, "overdue_sce_inspections": 18},
    {"month": "2026-03", "tier1": 0, "tier2": 0, "tier3": 7, "overdue_sce_inspections": 18 + TA["deferred_sce"] + 2},
]
TIER3 = [
    {"ts": "2026-03-12T09:40", "unit": "crude unit", "event": "desalter level high-high: wet crude"},
    {"ts": "2026-03-13T02:15", "unit": "crude unit", "event": "desalter level high-high: wet crude"},
    {"ts": "2026-03-14T18:30", "unit": "crude unit", "event": "overhead water pH below its safe operating limit"},
    {"ts": "2026-03-16T07:05", "unit": "reformer", "event": "heater tube skin temperature above limit during restart"},
    {"ts": "2026-03-19T23:50", "unit": "crude unit", "event": "overhead water pH below its safe operating limit"},
    {"ts": "2026-03-24T03:30", "unit": "hydrocracker", "event": "feed surge drum low-low level: VGO tank at minimum"},
    {"ts": "2026-03-29T13:05", "unit": "crude unit", "event": "charge flow low: P-101A trip, spare started"},
]
assert len(TIER3) == PSE[2]["tier3"]
LAST_TIER2 = "2025-11-04"

story = {
    "refinery": {"capacity_bpd": CAPACITY, "march_run_bbl": total_run, "avg_run_bpd": round(total_run / N)},
    "utilization": {
        "pct": round(util * 100, 1), "light_share_pct": round(light_share * 100), "plan_light_pct": round(PLAN_SLATE["light"] * 100),
        "medium_share_pct": round(medium_share * 100), "gulf_out_day": "2026-03-09", "yanbu_from": "2026-03-22", "waf_from": "2026-03-28",
        "hcu_min_util_pct": round(min(hcu_util) * 100), "tank_min_day": tank_min_day, "feb_pct": round(util_feb * 100),
    },
    "margin": {
        "screen": round(screen, 2), "plan": round(plan_margin, 2), "realised": round(actual_value - FUEL_AND_LOSS - prem - frt - dem, 2),
        "steps": {"crude_premium": round(-(prem - PLAN_PREMIUM), 2), "plan_premium": round(-PLAN_PREMIUM, 2),
                  "freight": round(-frt, 2), "demurrage": round(-dem, 2), "slate": round(actual_value - product_value(plan, PLAN_RUN), 2)},
        "diesel_crack": CRACK["diesel"], "jet_crack": CRACK["kero"],
    },
    "diesel": {
        "yield_pct": round(diesel_yield * 100, 1), "plan_pct": round(plan_diesel_yield * 100, 1), "own_pct": round(diesel_yield_own * 100, 1),
        "vgo_start": VGO_START, "vgo_end": round(rows[-1]["vgo_tank"]), "vgo_drawn": round(vgo_drawn), "diesel_from_tank": round(diesel_from_tank),
        "first_week_yield_pct": round(sum(r["prod"]["diesel"] for r in first_week) / sum(r["run"] for r in first_week) * 100, 1),
        "low_day": tank_min_day, "low_day_yield_pct": round(low["prod"]["diesel"] / low["run"] * 100, 1),
        "low_day_run": low["run"], "low_day_diesel": round(low["prod"]["diesel"]), "plan_diesel_bpd": round(plan["diesel"]),
        "after_pct": round(sum(r["prod"]["diesel"] for r in rows if r["date"] >= tank_min_day) / sum(r["run"] for r in rows if r["date"] >= tank_min_day) * 100, 1),
        "light_pct": round(sum(r["prod"]["diesel"] for r in rows if "2026-03-10" <= r["date"] <= "2026-03-21") / sum(r["run"] for r in rows if "2026-03-10" <= r["date"] <= "2026-03-21") * 100, 1),
        "hcu_after_min_pct": round(min(r["hcu_feed"] for r in rows if r["date"] >= tank_min_day) / HCU_CAP * 100), "hcu_after_max_pct": round(max(r["hcu_feed"] for r in rows if r["date"] >= tank_min_day) / HCU_CAP * 100),
    },
    "energy": {
        "feb_util_pct": round(util_feb * 100), "mar_util_pct": round(util * 100), "ei_feb": round(ei_feb, 3), "ei_mar": round(ei_mar, 3),
        "ei_change_pct": round((ei_mar / ei_feb - 1) * 100, 1), "idx_feb": round(idx_feb, 1), "idx_mar": round(idx_mar, 1),
        "idx_change_pct": round((idx_mar / idx_feb - 1) * 100, 1), "mar_over_expected_pct": round(idx_mar - 100, 1), "feb_vs_expected_pct": round(idx_feb - 100, 1),
        "foul_from": FOUL_FROM, "extra_gj": round(sum(mar_energy) - sum(expected(r["run"], r["hcu_feed"], r["ref_feed"]) for r in rows)),
    },
    "availability": {
        "pct": round(mech_avail * 100, 1), "trips": len(TRIPS), "spare_hours": round(spare_hours), "spare_days": round(spare_hours / 24, 1),
        "b_alarm": B_ALARM, "crude_unit_avail_pct": 100.0,
    },
    "turnaround": TA,
    "safety": {"tier1": 0, "tier2": 0, "last_tier2": LAST_TIER2, "overdue_feb": PSE[1]["overdue_sce_inspections"],
               "overdue_mar": PSE[2]["overdue_sce_inspections"], "tier3_feb": PSE[1]["tier3"], "tier3_mar": PSE[2]["tier3"]},
}

r1 = lambda x: round(x, 1)
data = {
    "meta": {"about": "Refinery 014, a simulated 240,000 b/d refinery on India's west coast, March 2026.", "seed": 1412, "days": DAYS,
             "cracks_vs_dubai": CRACK, "premium_vs_dubai": PREMIUM, "freight": FREIGHT},
    "daily": [{"date": r["date"], "run": r["run"], "slate": r["slate"], "vgo_made": r1(r["vgo_made"]), "hcu_feed": r1(r["hcu_feed"]),
               "vgo_tank": r1(r["vgo_tank"]), "ref_feed": r1(r["ref_feed"]), "prod": {k: r1(v) for k, v in r["prod"].items()},
               "diesel_yield_pct": round(r["prod"]["diesel"] / r["run"] * 100, 2), "energy_gj": round(mar_energy[i])} for i, r in enumerate(rows)],
    "feb": {"run": feb_run, "energy_gj": [round(x) for x in feb_energy]},
    "trips": TRIPS, "unplanned": UNPLANNED, "tier3": TIER3, "pse": PSE, "plan": {k: r1(v) for k, v in plan.items()}, "story": story,
}
(ROOT / "src" / "data" / "oil-gas" / "refinery-014.json").write_text(json.dumps(data, indent=1) + "\n")

rec = ROOT / "public" / "data" / "refinery-014"
rec.mkdir(parents=True, exist_ok=True)


def write(name, head, rws):
    with open(rec / name, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        w.writerows(rws)


write("crude-runs-march-2026.csv", ["date", "crude_run_bbl", "medium_sour_pct", "light_pct", "domestic_pct"],
      [[r["date"], r["run"], round(r["slate"]["medium"] * 100), round(r["slate"]["light"] * 100), round(r["slate"]["domestic"] * 100)] for r in rows])
write("hydrocracker-and-vgo-tank-march-2026.csv", ["date", "vgo_from_crude_bbl", "hydrocracker_feed_bbl", "vgo_tank_end_bbl"],
      [[r["date"], round(r["vgo_made"]), round(r["hcu_feed"]), round(r["vgo_tank"])] for r in rows])
write("products-march-2026.csv", ["date", "lpg_bbl", "naphtha_bbl", "gasoline_bbl", "jet_kero_bbl", "diesel_bbl", "vgo_sold_bbl", "fuel_oil_bbl"],
      [[r["date"]] + [round(r["prod"][k]) for k in ("lpg", "naphtha", "gasoline", "kero", "diesel", "vgo_sold", "residue")] for r in rows])
write("lp-plan-march-2026.csv", ["item", "value"], [["crude run, bbl/d", PLAN_RUN], ["medium sour share", PLAN_SLATE["medium"]], ["light share", PLAN_SLATE["light"]],
      ["domestic share", PLAN_SLATE["domestic"]]] + [[f"{k}, bbl/d", round(v)] for k, v in plan.items()])
write("prices-march-2026.csv", ["item", "usd_per_bbl_vs_dubai"], [[f"crack: {k}", v] for k, v in CRACK.items()] + [[f"premium: {k} crude", v] for k, v in PREMIUM.items()]
      + [[f"freight and insurance: {k} crude", v] for k, v in FREIGHT.items()])
write("energy-feb-mar-2026.csv", ["date", "crude_run_bbl", "energy_gj"],
      [[f"2026-02-{k + 1:02d}", feb_run[k], round(feb_energy[k])] for k in range(FEB_DAYS)] + [[r["date"], r["run"], round(mar_energy[i])] for i, r in enumerate(rows)])
write("pump-trips-march-2026.csv", ["tag", "tripped", "cause", "spare_started_s", "back_in_service"],
      [[t["tag"], t["trip"], t["cause"], SPARE_START_S[k], t["back"] or "still under repair on 31 March"] for k, t in enumerate(TRIPS)]
      + [["P-101B", B_ALARM, "vibration alarm while running as the only charge pump", "", ""]])
write("unplanned-downtime-march-2026.csv", ["unit", "from", "to", "cause"], [[u["unit"], u["from"], u["to"], u["cause"]] for u in UNPLANNED])
write("turnaround-reformer-2026.csv", ["item", "value"], [[k, v] for k, v in TA.items()])
write("process-safety-2026.csv", ["month", "tier1_pse", "tier2_pse", "tier3_challenges", "overdue_safety_critical_inspections"],
      [[p["month"], p["tier1"], p["tier2"], p["tier3"], p["overdue_sce_inspections"]] for p in PSE])
write("tier3-march-2026.csv", ["ts", "unit", "event"], [[t["ts"], t["unit"], t["event"]] for t in TIER3])

print(json.dumps(story, indent=1))
