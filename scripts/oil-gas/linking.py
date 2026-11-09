#!/usr/bin/env python3
"""The numbers behind the Oil & Gas season's four linking posts.

1. The well: a scripted production agent, run on forty simulated Marches, with and without one rule
   from KPI 1 (when the pump's own data disagrees with the allocated rate, ask for a well test).
2. The pipe and the ship: when each rule from KPIs 7 to 11 would have fired on March's records.
3. The refinery: the same for KPIs 12 to 18.
4. Who saw what: pairs of records that share a key and how often they agree, and how much sooner
   joining two records shows each of March's problems than the way each was found.

Reads the season's records (field-014, well-kpis, pipe-014 and refinery-014 JSON) and writes
src/data/oil-gas/linking.json and public/data/field-014/agent-forty-marches.csv. Standard library
only, and seeded, so every run gives the same numbers.

    python3 scripts/oil-gas/linking.py
"""
from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src" / "data" / "oil-gas"
F = json.loads((DATA / "field-014.json").read_text())
WK = json.loads((DATA / "well-kpis.json").read_text())
P = json.loads((DATA / "pipe-014.json").read_text())
R = json.loads((DATA / "refinery-014.json").read_text())
DAYS = F["meta"]["days"]
IDX = {d: i for i, d in enumerate(DAYS)}
dnum = lambda iso: int(iso[8:10])
mean = lambda xs: sum(xs) / len(xs)

# ---------- 1. The well: forty simulated Marches ----------
RUNS = 40
HORIZON = 61  # days, 1 March to 30 April
WEAR_LOSS = 0.36  # share of the rate a worn pump has lost by the day it stops (Well 14: 542 of 833 on 18 March)
FLAG_PCT, FLAG_DAYS = 0.10, 2  # the rule: allocated above the pump's estimate by more than 10%, two days running
VFM_ERR = 0.035  # the pump-data estimate's daily error
TEST_DELAY_SEPARATOR, TEST_DELAY_PORTABLE = 1, 2  # days from the flag to a test result
RIG_LEAD = (15, 22)  # days from booking a rig to the rig on site (Field 014: booked 20 March, free 9 April)
WORKOVER_DAYS = 3


def one_march(k: int) -> dict:
    rng = random.Random(1420 + k)
    q0 = rng.gauss(830, 20)
    wear = rng.randint(2, 10)  # the day the pump starts to wear
    stop = wear + rng.randint(12, 17)  # the day it stops for good
    sep = None
    if rng.random() < 0.6:  # the test separator is out of service for part of the month
        a = rng.randint(3, 12)
        sep = (a, a + rng.randint(8, 16))
    lead = rng.randint(*RIG_LEAD)
    noise = [rng.gauss(0, VFM_ERR) for _ in range(HORIZON + 2)]

    def rate(day: int) -> float:
        if day >= stop:
            return 0.0
        if day >= wear:
            return q0 * (1 - WEAR_LOSS * (day - wear + 0.5) / (stop - wear))
        return q0

    def lost(book_day: int) -> tuple[float, int]:
        rig = book_day + lead
        restart = rig + WORKOVER_DAYS
        total = 0.0
        for day in range(1, HORIZON + 1):
            if day >= restart:
                continue
            total += q0 if rig <= day else q0 - rate(day)
        return total, restart

    # Agent A reads the KPIs as reported and books a rig when the pump stops.
    a_lost, a_restart = lost(stop)
    # Agent B has one more rule, and asks for a well test when it fires.
    run, flag = 0, None
    for day in range(1, stop):
        run = run + 1 if q0 > (1 + FLAG_PCT) * rate(day) * (1 + noise[day]) else 0
        if run >= FLAG_DAYS:
            flag = day
            break
    sep_out = flag is not None and sep is not None and sep[0] <= flag <= sep[1]
    test = (flag + (TEST_DELAY_PORTABLE if sep_out else TEST_DELAY_SEPARATOR)) if flag else stop
    b_lost, b_restart = lost(min(test, stop))
    return {"run": k + 1, "seed": 1420 + k, "rate_bpd": round(q0), "wear_from": wear, "stopped": stop,
            "separator_out": f"{sep[0]}-{sep[1]}" if sep else "", "rig_lead_days": lead, "rule_fired": flag or "",
            "separator_out_at_flag": sep_out, "test_result": test, "a_booked": stop, "b_booked": min(test, stop),
            "a_restart": a_restart, "b_restart": b_restart, "a_lost_bbl": round(a_lost), "b_lost_bbl": round(b_lost)}


marches = [one_march(k) for k in range(RUNS)]
well = {
    "runs": RUNS, "horizon": "1 March to 30 April", "rig_lead_min": RIG_LEAD[0], "rig_lead_max": RIG_LEAD[1],
    "a_lost_mean": round(mean([m["a_lost_bbl"] for m in marches])), "b_lost_mean": round(mean([m["b_lost_bbl"] for m in marches])),
    "days_earlier_mean": round(mean([m["a_booked"] - m["b_booked"] for m in marches]), 1),
    "b_better_runs": sum(1 for m in marches if m["b_lost_bbl"] < m["a_lost_bbl"]),
    "fired_runs": sum(1 for m in marches if m["rule_fired"] != ""),
    "portable_runs": sum(1 for m in marches if m["separator_out_at_flag"]),
}
well["saved_mean"] = well["a_lost_mean"] - well["b_lost_mean"]
well["saved_pct"] = round(well["saved_mean"] / well["a_lost_mean"] * 100)
with (ROOT / "public" / "data" / "field-014" / "agent-forty-marches.csv").open("w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["run", "seed", "rate_bpd", "pump_wear_from_day", "pump_stopped_day", "test_separator_out_days", "rig_lead_days",
                "rule_fired_day", "test_result_day", "agent_a_rig_booked_day", "agent_b_rig_booked_day", "agent_a_restart_day",
                "agent_b_restart_day", "agent_a_lost_bbl", "agent_b_lost_bbl"])
    for m in marches:
        w.writerow([m["run"], m["seed"], m["rate_bpd"], m["wear_from"], m["stopped"], m["separator_out"], m["rig_lead_days"], m["rule_fired"],
                    m["test_result"], m["a_booked"], m["b_booked"], m["a_restart"], m["b_restart"], m["a_lost_bbl"], m["b_lost_bbl"]])

# Field 014's own March: when the rule fires on Well 14, and what a test then would have found.
fs = F["story"]
w14 = F["daily"]["wells"]["W-14"]
flag_day = fs["check"]["first_flag_w14"]
sep_out = fs["separator"]["out_from"][:10] <= flag_day <= fs["separator"]["out_to"][:10]
test_day = (date.fromisoformat(flag_day) + timedelta(days=TEST_DELAY_PORTABLE if sep_out else TEST_DELAY_SEPARATOR)).isoformat()
well["march"] = {
    "flag": flag_day, "flag_allocated": round(w14["allocated"][IDX[flag_day]]), "flag_vfm": round(w14["vfm"][IDX[flag_day]]),
    "separator_out": sep_out, "test_day": test_day, "test_produced": round(w14["produced"][IDX[test_day]]),
    "last_test_bpd": fs["w14_test"]["oil_bpd"], "stop": fs["pump"]["stop"], "days_before_stop": fs["check"]["days_before_stop"],
    "rig_booked": fs["pump"]["stop"][:10], "rig_free": WK["story"]["lifting"]["rig_free"],
    "test_days_before_stop": (date.fromisoformat(fs["pump"]["stop"][:10]) - date.fromisoformat(test_day)).days,
    "other_well_flagged": fs["check"]["other_wells_flagged"][0], "other_flag_days": fs["check"]["other_flag_days"],
}

# ---------- 2. The pipe and the ship: each rule replayed on March ----------
ps = P["story"]
pd = P["daily"]
bsw, lab = pd["bsw_pct"], pd["lab_bsw_pct"]
water_days = [DAYS[i] for i in range(len(DAYS)) if bsw[i] - lab[i] > 0.5]
probe = pd["t104"]
probe_day = next(r["date"] for k, r in enumerate(probe) if k and r["free_water_probe"] == 0 and probe[k - 1]["free_water_probe"] > 100)
gas = pd["gas"]
ua_day = next(g["date"] for g in gas if g["unaccounted"] / g["produced"] > 0.05)
ua_pct = round(next(g for g in gas if g["date"] == ua_day)["unaccounted"] / next(g for g in gas if g["date"] == ua_day)["produced"] * 100, 1)
# The same response as in March, started from the gas balance instead of the satellite: the balance for a day is read the
# next morning, a crew with a camera finds the source the morning after, and the valve is replaced by 18:30 the day after that.
leak_from = datetime.fromisoformat(ps["methane"]["leak_from"])
fixed = datetime.fromisoformat(f"{ua_day}T18:30") + timedelta(days=3)
leak_rule_t = ps["methane"]["leak_kg_h"] * (fixed - leak_from).total_seconds() / 3600 / 1000
lg_alert = ps["loss_gain"]["first_alert_7_days"]
# From the day after the alert, receipts are booked on the field's proved fiscal meter until the prover is back.
phantom_after = sum(pd["receipt"][i] - pd["gross"][i] for i in range(IDX[lg_alert] + 1, len(DAYS)))
pipe = {
    "water": {"from": water_days[0], "to": water_days[-1], "days": len(water_days), "fault_water_bbl": ps["throughput"]["fault_water_bbl"],
              "dip": "2026-03-31"},
    "loss_gain": {"alert": lg_alert, "proving": ps["loss_gain"]["prover_back"], "phantom_bbl": ps["loss_gain"]["gain_bbl"],
                  "phantom_kept_out_bbl": round(phantom_after)},
    "tank": {"probe_flag": probe_day, "probe_failed": ps["tank"]["probe_failed"], "dip": "2026-03-31", "free_water_bbl": ps["tank"]["dip_free_water_31"],
             "free_water_at_flag": round(probe[IDX[probe_day]]["true_free"])},
    "methane": {"ua_day": ua_day, "ua_pct": ua_pct, "ua_before_pct": ps["methane"]["ua_before_pct"], "satellite": ps["methane"]["satellite"]["ts"],
                "fixed": ps["methane"]["leak_to"], "fixed_with_rule": fixed.isoformat(timespec="minutes"), "leak_t": ps["methane"]["leak_t"],
                "leak_t_with_rule": round(leak_rule_t, 1)},
    "ship": {"nor": ps["ship"]["nor"], "laytime_end": ps["ship"]["laytime_end"], "berthed": ps["ship"]["berthed"],
             "reported_days": ps["ship"]["reported_wait_days"], "real_days": ps["ship"]["real_wait_days"], "demurrage_usd": ps["ship"]["demurrage_usd"]},
}

# ---------- 3. The refinery: each rule replayed on March ----------
rs = R["story"]
daily = R["daily"]
MIN_TANK = 30_000
draw = [0.0] + [max(0.0, daily[i - 1]["vgo_tank"] - daily[i]["vgo_tank"]) for i in range(1, len(daily))]
first_draw = next(k for k in range(len(daily)) if draw[k] > 0)
cover_days = round((daily[first_draw]["vgo_tank"] - MIN_TANK) / draw[first_draw])
# Energy against what the same runs should use (the model in refinery.py), two days running above it by more than 2%.
FIXED_GJ, VAR_GJ, HCU_GJ, REF_GJ = 52_000, 0.30, 0.12, 0.25
expected = [FIXED_GJ + VAR_GJ * d["run"] + HCU_GJ * d["hcu_feed"] + REF_GJ * d["ref_feed"] for d in daily]
over = [d["energy_gj"] / e - 1 for d, e in zip(daily, expected)]
energy_flag = next(daily[k]["date"] for k in range(1, len(daily)) if over[k] > 0.02 and over[k - 1] > 0.02)
light_day = next(d["date"] for d in daily if d["slate"]["light"] > 0.5)
trips = R["trips"]
refinery = {
    "slate": {"flag": light_day, "light_pct": round(daily[IDX[light_day]]["slate"]["light"] * 100), "plan_light_pct": rs["utilization"]["plan_light_pct"],
              "util_pct": rs["utilization"]["pct"], "screen": rs["margin"]["screen"], "plan": rs["margin"]["plan"], "realised": rs["margin"]["realised"]},
    "tank": {"flag": daily[first_draw]["date"], "cover_days": cover_days, "draw_bbl": round(draw[first_draw]), "tank_bbl": round(daily[first_draw]["vgo_tank"]),
             "empty": rs["utilization"]["tank_min_day"], "yield": rs["diesel"]["yield_pct"], "own": rs["diesel"]["own_pct"]},
    "energy": {"flag": energy_flag, "foul_from": rs["energy"]["foul_from"], "over_pct_at_flag": round(over[IDX[energy_flag]] * 100, 1),
               "ei_change_pct": rs["energy"]["ei_change_pct"], "mar_over_expected_pct": rs["energy"]["mar_over_expected_pct"], "extra_gj": rs["energy"]["extra_gj"]},
    "pump": {"flag": trips[1]["trip"], "first": trips[0]["trip"], "third": trips[2]["trip"], "b_alarm": rs["availability"]["b_alarm"],
             "spare_hours": rs["availability"]["spare_hours"]},
    "turnaround": {"flag": rs["turnaround"]["actual_end"], "decided": rs["turnaround"]["decided"], "deferred": rs["turnaround"]["deferred_orders"],
                   "deferred_sce": rs["turnaround"]["deferred_sce"]},
    "safety": {"tier3_feb": rs["safety"]["tier3_feb"], "tier3_mar": rs["safety"]["tier3_mar"], "overdue_feb": rs["safety"]["overdue_feb"],
               "overdue_mar": rs["safety"]["overdue_mar"], "tier3_second": R["tier3"][1]["ts"]},
}

# ---------- 4. Who saw what: joins, and how soon each problem shows ----------
alloc, vfm = w14["allocated"], w14["vfm"]
w14_rows = [i for i in range(len(DAYS)) if alloc[i] and vfm[i] and alloc[i] > 0 and vfm[i] > 0]
lg = pd["lg_pct"]
vessels = P["vessels"]
dips = [(r[0], r[2]) for r in [("2026-02-28", "manual dip", ps["tank"]["opening_free_water_bbl"]), ("2026-03-31", "manual dip", ps["tank"]["dip_free_water_31"])]]
probe_at = {"2026-02-28": ps["tank"]["opening_free_water_bbl"], "2026-03-31": probe[-1]["free_water_probe"]}  # the probe agreed with February's dip
model_days = sum(1 for x in over if abs(x) <= 0.02)
over_from = next(daily[k]["date"] for k in range(len(daily)) if over[k] > 0.02)
joins = [
    {"id": "alloc-meter", "kind": "always", "a": "The allocation report", "b": "the fiscal meter", "unit": "days", "rows": len(DAYS),
     "agree": sum(1 for i in range(len(DAYS)) if abs(sum(F["daily"]["wells"][x]["allocated"][i] for x in F["daily"]["wells"]) - F["daily"]["metered"][i]) < 1),
     "how": "The allocation shares out the meter, so the wells always add up to it"},
    {"id": "book-gauge", "kind": "always", "a": "T-104\u2019s book stock", "b": "its gauge", "unit": "days", "rows": len(probe),
     "agree": sum(1 for r in probe if abs(r["diff_pct"]) <= 0.5), "how": "Within 0.5%, because both counted the water as oil"},
    {"id": "fiscal-receipt", "kind": "always", "a": "The field\u2019s fiscal meter", "b": "the refinery\u2019s receipt meter", "unit": "days", "rows": len(DAYS),
     "agree": sum(1 for x in lg if abs(x) <= ps["loss_gain"]["tolerance_pct"]), "same_way": sum(1 for x in lg if x > 0),
     "how": "Inside the \u00b10.30% band, and a gain on every one of those days"},
    {"id": "alloc-vfm", "kind": "world", "a": "Well 14\u2019s allocated rate", "b": "its pump\u2019s own flow estimate", "unit": "days", "rows": len(w14_rows),
     "agree": sum(1 for i in w14_rows if alloc[i] <= 1.1 * vfm[i]), "how": "Within 10% until the pump wore. Apart on 8 March and every day from 10 March"},
    {"id": "water", "kind": "world", "a": "The field\u2019s water reading", "b": "the refinery\u2019s sampler", "unit": "days", "rows": len(DAYS),
     "agree": len(DAYS) - len(water_days), "how": f"Within half a point, apart from {dnum(water_days[0])} to {dnum(water_days[-1])} March, while the heater-treater was down"},
    {"id": "probe-dips", "kind": "world", "a": "T-104\u2019s water probe", "b": "the manual dips", "unit": "dips", "rows": len(dips),
     "agree": sum(1 for d, v in dips if abs(probe_at[d] - v) <= 0.1 * v),
     "how": f"Both about {ps['tank']['opening_free_water_bbl']} barrels on 28 February. On 31 March the dip found {ps['tank']['dip_free_water_31']:,} and the probe read zero"},
    {"id": "gas", "kind": "world", "a": "The methane inventory", "b": "the field\u2019s gas balance", "unit": "days", "rows": len(gas),
     "agree": sum(1 for g in gas if g["unaccounted"] / g["produced"] <= 0.03),
     "how": f"Unaccounted gas at its usual level, apart from {dnum(ua_day)} to {dnum(ps['methane']['leak_to'])} March, while K-2 leaked"},
    {"id": "schedule-nor", "kind": "world", "a": "The port\u2019s schedule", "b": "the ships\u2019 notices of readiness", "unit": "ships", "rows": len(vessels),
     "agree": sum(1 for v in vessels if abs(v["wait_from_nor_days"] - v["reported_wait_days"]) < 1),
     "how": "Within a day. The replacement cargo waited 0.7 days by the schedule and 4.2 from its notice"},
    {"id": "yield-tank", "kind": "world", "a": "The diesel yield", "b": "the VGO tank behind the hydrocracker", "unit": "days", "rows": len(daily),
     "agree": sum(1 for k in range(len(daily)) if draw[k] < 1), "how": f"The tank held steady, apart from {dnum(daily[first_draw]['date'])} to {dnum(rs['utilization']['tank_min_day'])} March, while it fed the hydrocracker"},
    {"id": "energy-model", "kind": "world", "a": "The refinery\u2019s energy use", "b": "a model of what the same runs should use", "unit": "days", "rows": len(daily),
     "agree": model_days, "how": f"Within 2% until {dnum(over_from)} March, then above it every day while the preheat train fouled"},
    {"id": "downtime-trips", "kind": "world", "a": "The crude unit\u2019s downtime log", "b": "the trip log, by equipment tag", "unit": "trips", "rows": len(trips),
     "agree": 0, "how": "None of P-101A\u2019s three trips cost the unit an hour, so none reached the downtime log"},
]
for j in joins:
    j["share"] = round(j["agree"] / j["rows"], 3)

FOUND = [
    {"id": "pump", "problem": "Well 14's worn pump", "join": "the allocated rate and the pump's own estimate", "shows": flag_day,
     "found": fs["pump"]["stop"][:10], "found_by": "the pump stopped"},
    {"id": "probe", "problem": "T-104's failed water probe", "join": "the probe and its own last reading", "shows": probe_day,
     "found": "2026-03-31", "found_by": "the month-end dip"},
    {"id": "meter", "problem": "The receipt meter reading high", "join": "the sign of each day's gain", "shows": lg_alert,
     "found": ps["loss_gain"]["prover_back"], "found_by": "the next proving"},
    {"id": "leak", "problem": "Compressor K-2's leak", "join": "the gas balance and the inventory", "shows": ua_day,
     "found": ps["methane"]["satellite"]["ts"][:10], "found_by": "a satellite"},
    {"id": "vgo", "problem": "The VGO tank running down", "join": "the diesel yield and the tank", "shows": daily[first_draw]["date"],
     "found": rs["utilization"]["tank_min_day"], "found_by": "the feed drum's low-level alarm"},
    {"id": "p101", "problem": "P-101A failing again", "join": "trips by equipment tag", "shows": trips[1]["trip"][:10],
     "found": rs["availability"]["b_alarm"][:10], "found_by": "the spare's own alarm"},
]
for f in FOUND:
    f["days_sooner"] = (date.fromisoformat(f["found"]) - date.fromisoformat(f["shows"])).days
summary = {
    "always": sum(1 for j in joins if j["kind"] == "always"), "worlds": sum(1 for j in joins if j["kind"] == "world"),
    "always_rows": sum(j["rows"] for j in joins if j["kind"] == "always"),
    "always_agree": all(j["agree"] == j["rows"] for j in joins if j["kind"] == "always"),
    "worlds_disagree": all(j["agree"] < j["rows"] for j in joins if j["kind"] == "world"),
    "joins": len(joins),
    "days_sooner_min": min(f["days_sooner"] for f in FOUND), "days_sooner_max": max(f["days_sooner"] for f in FOUND),
    "days_sooner_median": sorted(f["days_sooner"] for f in FOUND)[len(FOUND) // 2 - 1: len(FOUND) // 2 + 1],
}

out = {"well": well, "pipe": pipe, "refinery": refinery, "joins": joins, "found": FOUND, "summary": summary}
(DATA / "linking.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
