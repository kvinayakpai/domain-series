#!/usr/bin/env python3
"""Field 014's other records for KPIs 2 to 6: the plan, the loss log, the monthly totals, the pump
history and the costs.

Reads what scripts/oil-gas/generate.py wrote (src/data/oil-gas/field-014.json: March day by day,
what each well really produced and what the field recorded) and adds the records a field keeps
around it:

- the 2026 business plan's March figure, set in November 2025 (production efficiency, KPI 2)
- the production loss log, which files a loss when a well stops (deferred production, KPI 3)
- the fiscal meter's monthly totals from December 2025 (decline rate, KPI 4)
- every pump's install and pull dates since 2019, with the teardown findings (pump run life, KPI 5)
- the operating costs and the maintenance backlog (lifting cost, KPI 6)

Standard library only and seeded with its own generator, so it never changes Field 014's March.

    python3 scripts/oil-gas/generate.py && python3 scripts/oil-gas/well.py
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
F = json.loads((ROOT / "src" / "data" / "oil-gas" / "field-014.json").read_text())
rng = random.Random(1402)

DAYS = F["meta"]["days"]
WELLS = {w["id"]: w for w in F["meta"]["wells"]}
IDS = list(WELLS)
CASE = F["story"]["case_well"]
D = F["daily"]
W = D["wells"]
S = F["story"]
MARCH_BBL = math.floor(round(sum(D["metered"]), 1) + 0.5)  # the daily record's total, rounded half up
IDX = {d: i for i, d in enumerate(DAYS)}
STOP = S["pump"]["stop"]


def rate_on(wid: str, day: date) -> float:
    """A healthy well's oil rate on any day, from its 1 March rate and its decline."""
    w = WELLS[wid]
    return w["oil_bpd_1mar"] * math.exp(-w["decline_per_year"] * (day - date(2026, 3, 1)).days / 365)


# ---------- KPI 4: the fiscal meter's monthly totals, December 2025 to March 2026 ----------
MONTHS = [("2025-12", date(2025, 12, 1), 31), ("2026-01", date(2026, 1, 1), 31), ("2026-02", date(2026, 2, 1), 28)]


def month_total(start: date, n: int) -> tuple[float, float]:
    """A month before March: every well healthy, a few short stops, the meter within a tenth of a per cent."""
    total, hours = 0.0, 0.0
    for wid in IDS:
        e = 0.0
        for k in range(n):
            e = 0.6 * e + rng.gauss(0, 0.010)
            h = 24.0 - (rng.choice([1, 2, 3, 4, 5]) if rng.random() < 0.035 else 0)
            total += rate_on(wid, start + timedelta(days=k)) * (1 + e) * h / 24
            hours += h
    return total * (1 + rng.gauss(0, 0.001)), hours


monthly = []
for name, start, n in MONTHS:
    bbl, hrs = month_total(start, n)
    monthly.append({"month": name, "days": n, "metered_bbl": round(bbl), "avg_bpd": round(bbl / n), "well_hours": round(hrs)})
monthly.append({"month": "2026-03", "days": 31, "metered_bbl": round(MARCH_BBL), "avg_bpd": round(MARCH_BBL / 31),
                "well_hours": round(sum(sum(W[w]["run_hours"]) for w in IDS))})
feb, mar = monthly[2], monthly[3]
m_reported = mar["avg_bpd"] / feb["avg_bpd"] - 1
annual = lambda m: (1 + m) ** 12 - 1

# The reservoir's own decline: the fifteen other wells, per hour they ran, February to March. In
# February every well was healthy; in March Well 14 is taken out using its pump's own flow estimate.
w14_vfm_mar = sum(W[CASE]["vfm"])
feb_hours_others = feb["well_hours"] - 28 * 24  # Well 14 ran every hour of February
feb_w14 = sum(rate_on(CASE, date(2026, 2, 1) + timedelta(days=k)) for k in range(28))
feb_others_rate = (feb["metered_bbl"] - feb_w14) / feb_hours_others * 24
mar_hours_others = sum(sum(W[w]["run_hours"]) for w in IDS if w != CASE)
mar_others_rate = (MARCH_BBL - w14_vfm_mar) / mar_hours_others * 24
m_reservoir = mar_others_rate / feb_others_rate - 1
# What really happened, from the answer key: the fifteen wells' true production per hour run.
true_others_mar = sum(sum(W[w]["produced"]) for w in IDS if w != CASE) / mar_hours_others * 24
true_decline_per_year = 1 - math.exp(-sum(WELLS[w]["decline_per_year"] * WELLS[w]["oil_bpd_1mar"] for w in IDS) / sum(WELLS[w]["oil_bpd_1mar"] for w in IDS))

# ---------- KPI 2: production efficiency against the plan and against the wells' tests ----------
# The plan's March figure was set in November 2025: each well's November test, declined at the
# plan's 12% a year to mid-March, less a 3% allowance for downtime.
PLAN_DECLINE, PLAN_ALLOWANCE = 0.12, 0.03
nov = {w: rate_on(w, date(2025, 11, 14)) * (1 + rng.gauss(0, 0.03)) for w in IDS}
plan_bpd = round(sum(q * math.exp(-PLAN_DECLINE * 121 / 365) for q in nov.values()) * (1 - PLAN_ALLOWANCE), -1)
plan_bbl = plan_bpd * 31
# The wells' own potential: each well at the rate of its test in force, every hour of March.
mpp_bbl = sum(sum(W[w]["test_rate"]) for w in IDS)
pe_plan = MARCH_BBL / plan_bbl
pe_tests = MARCH_BBL / mpp_bbl
w14_potential = sum(W[CASE]["test_rate"])

# ---------- KPI 3: the loss log ----------
CATS = ["Process trip", "ESP trip, restarted"]
log = []
power_day = next(e["ts"][:10] for e in F["events"] if e["event"].startswith("Grid dip"))
for wid in IDS:
    for i, h in enumerate(W[wid]["run_hours"]):
        day, tr = DAYS[i], W[wid]["test_rate"][i]
        if wid == CASE and day >= S["pump"]["trip"][:10]:
            continue
        down = 24 - h - (1.5 if day == power_day else 0)
        if down > 0.01:
            cat = CATS[(IDS.index(wid) + i) % 2]
            log.append({"start": f"{day}T{rng.randint(1, 20):02d}:{rng.choice(['05', '20', '40', '50'])}", "well": wid, "category": cat,
                        "hours": round(down, 2), "deferred_bbl": round(tr * down / 24)})
log.append({"start": f"{power_day}T14:00", "well": "all", "category": "Power supply (grid)", "hours": 1.5,
            "deferred_bbl": round(sum(W[w]["test_rate"][IDX[power_day]] * 1.5 / 24 for w in IDS if w != CASE))})
trip_h = 24 - W[CASE]["run_hours"][IDX[S["pump"]["trip"][:10]]]
log.append({"start": S["pump"]["trip"], "well": CASE, "category": "ESP trip, restarted", "hours": round(trip_h, 2),
            "deferred_bbl": round(W[CASE]["test_rate"][IDX[S["pump"]["trip"][:10]]] * trip_h / 24)})
stop_h = sum(24 - h for h in W[CASE]["run_hours"][IDX[STOP[:10]]:])
log.append({"start": STOP, "well": CASE, "category": "Other: under investigation", "hours": round(stop_h, 2),
            "deferred_bbl": round(W[CASE]["test_rate"][IDX[STOP[:10]]] * stop_h / 24), "note": "restart failed; cause to be confirmed at the teardown after the pull"})
log.sort(key=lambda r: r["start"])
by_cat: dict[str, int] = {}
for r in log:
    by_cat[r["category"]] = by_cat.get(r["category"], 0) + r["deferred_bbl"]
logged = sum(by_cat.values())
# What the log cannot see: the barrels Well 14 lost while its pump ran worn, against its test.
wear = sum(W[CASE]["test_rate"][i] * W[CASE]["run_hours"][i] / 24 - W[CASE]["produced"][i] for i in range(IDX[S["pump"]["wear_from"]], IDX[STOP[:10]] + 1))
esp_logged = by_cat.get("ESP trip, restarted", 0)
w14_logged = sum(r["deferred_bbl"] for r in log if r["well"] == CASE)
pump_real = round(wear) + w14_logged  # every barrel Well 14's pump cost in March, against its test

# ---------- KPI 5: every pump since the field went on ESPs ----------
# (well, installed, pulled or None while running, reason pulled, teardown finding)
H = [
    ("W-01", "2019-02-11", "2022-08-30", "failed", "motor: insulation breakdown"), ("W-01", "2022-09-04", None, "", ""),
    ("W-02", "2019-03-05", "2023-01-18", "failed", "cable: splice failure"), ("W-02", "2023-01-23", None, "", ""),
    ("W-03", "2019-01-22", "2021-11-09", "failed", "pump: scale deposits"), ("W-03", "2021-11-14", "2025-04-02", "failed", "motor: insulation breakdown"), ("W-03", "2025-04-07", None, "", ""),
    ("W-04", "2019-04-16", "2023-06-27", "failed", "seal section: fluid ingress"), ("W-04", "2023-07-02", None, "", ""),
    ("W-05", "2019-05-07", "2022-03-15", "pulled", "upsized for higher water cut"), ("W-05", "2022-03-19", None, "", ""),
    ("W-06", "2019-02-26", "2022-12-06", "failed", "cable: insulation damage"), ("W-06", "2022-12-11", "2025-11-03", "failed", "seal section: fluid ingress"), ("W-06", "2025-11-08", None, "", ""),
    ("W-07", "2019-06-18", "2023-09-12", "failed", "motor: insulation breakdown"), ("W-07", "2023-09-17", None, "", ""),
    ("W-08", "2019-07-09", "2022-05-24", "failed", "pump: scale deposits"), ("W-08", "2022-05-29", None, "", ""),
    ("W-09", "2019-01-15", "2023-03-28", "failed", "seal section: fluid ingress"), ("W-09", "2023-04-02", None, "", ""),
    ("W-10", "2019-08-13", "2022-10-11", "failed", "cable: splice failure"), ("W-10", "2022-10-16", None, "", ""),
    ("W-11", "2019-09-03", "2023-11-21", "failed", "motor: insulation breakdown"), ("W-11", "2023-11-26", None, "", ""),
    ("W-12", "2019-10-08", "2024-02-13", "failed", "pump: scale deposits"), ("W-12", "2024-02-18", None, "", ""),
    ("W-13", "2019-03-19", "2022-07-05", "failed", "seal section: fluid ingress"), ("W-13", "2022-07-10", "2025-09-16", "failed", "cable: splice failure"), ("W-13", "2025-09-21", None, "", ""),
    ("W-14", "2019-03-11", "2022-09-04", "pulled", "upsized for a higher rate"), ("W-14", "2022-09-09", "2023-10-26", "failed", "pump: abrasive wear, sand"),
    ("W-14", "2023-11-01", "2024-10-23", "failed", "pump: abrasive wear, sand"), ("W-14", "2024-10-29", "2025-07-26", "failed", "pump: abrasive wear, sand"),
    ("W-14", "2025-07-31", None, "", ""),
    ("W-15", "2019-11-12", "2023-05-09", "failed", "motor: insulation breakdown"), ("W-15", "2023-05-14", None, "", ""),
    ("W-16", "2019-12-03", "2024-06-25", "failed", "seal section: fluid ingress"), ("W-16", "2024-06-30", None, "", ""),
]
END = date(2026, 3, 31)
runs = []
for wid, inst, pulled, why, finding in H:
    d0 = date.fromisoformat(inst)
    if wid == CASE and pulled is None:  # stopped on 20 March, still in the hole at the end of March
        d1, status, why, finding = date.fromisoformat(STOP[:10]), "failed, awaiting pull", "failed", "teardown after the pull (April)"
    elif pulled is None:
        d1, status = END, "running"
    else:
        d1, status = date.fromisoformat(pulled), why
    runs.append({"well": wid, "installed": inst, "ended": d1.isoformat() if status != "running" else "", "days": (d1 - d0).days,
                 "status": status, "teardown": finding})
pulled_failed = [r for r in runs if r["status"] == "failed"]  # what the monthly report averages: pumps pulled after a failure
avg_reported = sum(r["days"] for r in pulled_failed) / len(pulled_failed)
w14_runs = [r for r in runs if r["well"] == CASE]
w14_sand = [r for r in w14_runs if "sand" in r["teardown"]]
running = [r for r in runs if r["status"] == "running"]


def km_median(rs):
    """Kaplan-Meier median run life: failures count as events, pumps still running are censored."""
    pts = sorted((r["days"], r["status"] in ("failed", "failed, awaiting pull")) for r in rs)
    s, n = 1.0, len(pts)
    for t, event in pts:
        if event:
            s *= 1 - 1 / n
            if s <= 0.5:
                return t
        n -= 1
    return None  # more than half still running


others = [r for r in runs if r["well"] != CASE and r["status"] != "pulled"]
km_others = km_median(others)
by_cause: dict[str, list[int]] = {}
for r in pulled_failed + [r for r in runs if r["status"] == "failed, awaiting pull"]:
    key = r["teardown"].split(":")[0] if "sand" not in r["teardown"] else "sand wear"
    by_cause.setdefault(key, []).append(r["days"])

# ---------- KPI 6: the operating costs and the maintenance backlog (US dollars) ----------
pump_hours = {"2026-01": monthly[1]["well_hours"], "2026-02": feb["well_hours"], "2026-03": mar["well_hours"]}
POWER_PER_PUMP_HOUR = 55.0  # electricity for one ESP for an hour
COSTS = {
    "2026-01": {"staff and contracts": 820_000, "chemicals and water treatment": 384_000, "maintenance and repairs": 452_000, "well services and workovers": 0, "transport and other": 296_000},
    "2026-02": {"staff and contracts": 820_000, "chemicals and water treatment": 352_000, "maintenance and repairs": 446_000, "well services and workovers": 0, "transport and other": 288_000},
    "2026-03": {"staff and contracts": 820_000, "chemicals and water treatment": 381_000, "maintenance and repairs": 441_000, "well services and workovers": 0, "transport and other": 298_000},
}
for m in COSTS:
    COSTS[m] = {"electricity": round(pump_hours[m] * POWER_PER_PUMP_HOUR, -3), **COSTS[m]}
WORKOVER = 342_000  # Well 14: rig, new pump and cable; no rig free until 9 April
bbl = {"2026-01": monthly[1]["metered_bbl"], "2026-02": feb["metered_bbl"], "2026-03": mar["metered_bbl"]}
lift = {m: sum(c.values()) / bbl[m] for m, c in COSTS.items()}
lift_with_workover = (sum(COSTS["2026-03"].values()) + WORKOVER) / bbl["2026-03"]
BACKLOG = [
    {"month_end": "2026-01-31", "overdue_orders": 12, "est_cost_usd": 88_000},
    {"month_end": "2026-02-28", "overdue_orders": 14, "est_cost_usd": 96_000},
    {"month_end": "2026-03-31", "overdue_orders": 23, "est_cost_usd": 96_000 + WORKOVER + 61_000},
]

story = {
    "pe": {
        "plan_bpd": int(plan_bpd), "plan_set": "2025-11-14", "plan_decline_pct": round(PLAN_DECLINE * 100), "plan_allowance_pct": round(PLAN_ALLOWANCE * 100),
        "plan_bbl": int(plan_bbl), "mpp_bbl": round(mpp_bbl), "mpp_bpd": round(mpp_bbl / 31), "actual_bbl": round(MARCH_BBL),
        "pe_plan_pct": round(pe_plan * 100, 1), "pe_tests_pct": round(pe_tests * 100, 1),
        "w14_potential_bbl": round(w14_potential), # What Well 14 lost to its pump, the same figure KPI 3 and the linking posts use.
        "w14_lost_bbl": pump_real, "w14_lost_pct_of_mpp": round(pump_real / mpp_bbl * 100, 1),
    },
    "deferment": {
        "logged_bbl": logged, "by_category": by_cat, "other_bbl": by_cat["Other: under investigation"],
        "other_pct": round(by_cat["Other: under investigation"] / logged * 100), "esp_logged_bbl": esp_logged,
        "entries": len(log), "wear_unlogged_bbl": round(wear), "pump_real_bbl": pump_real,
        "w14_stop_hours": round(stop_h, 1), "w14_stop_bbl": round(W[CASE]["test_rate"][IDX[STOP[:10]]] * stop_h / 24),
        "esp_share_real_pct": round(pump_real / (logged + round(wear)) * 100),
    },
    "decline": {
        "feb_avg_bpd": feb["avg_bpd"], "mar_avg_bpd": mar["avg_bpd"], "reported_monthly_pct": round(m_reported * 100, 1),
        "reported_annual_pct": round(-annual(m_reported) * 100), "reservoir_monthly_pct": round(m_reservoir * 100, 1),
        "reservoir_annual_pct": round(-annual(m_reservoir) * 100), "true_annual_pct": round(true_decline_per_year * 100),
        "feb_others_rate": round(feb_others_rate), "mar_others_rate": round(mar_others_rate), "true_others_mar_rate": round(true_others_mar),
        "dec_avg_bpd": monthly[0]["avg_bpd"], "jan_avg_bpd": monthly[1]["avg_bpd"],
        "usual_monthly_pct": round(((feb["avg_bpd"] / monthly[0]["avg_bpd"]) ** 0.5 - 1) * 100, 1),
    },
    "run_life": {
        "pumps_since_2019": len(runs), "failed_pulled": len(pulled_failed), "running": len(running),
        "avg_reported_days": round(avg_reported), "avg_reported_years": round(avg_reported / 365.25, 1),
        "w14_sand_days": [r["days"] for r in w14_sand], "w14_last_days": w14_runs[-1]["days"], "w14_last_installed": w14_runs[-1]["installed"],
        "w14_sand_avg_days": round((sum(r["days"] for r in w14_sand) + w14_runs[-1]["days"]) / (len(w14_sand) + 1)),
        "km_median_others_days": km_others, "running_median_age_days": sorted(r["days"] for r in running)[len(running) // 2],
        "running_over_3y": sum(1 for r in running if r["days"] > 3 * 365),
        "by_cause": {k: {"n": len(v), "avg_days": round(sum(v) / len(v))} for k, v in sorted(by_cause.items())},
    },
    "lifting": {
        "usd_per_bbl": {m: round(v, 2) for m, v in lift.items()}, "opex_usd": {m: sum(c.values()) for m, c in COSTS.items()},
        "mar_with_workover": round(lift_with_workover, 2), "workover_usd": WORKOVER, "rig_free": "2026-04-09",
        "backlog": BACKLOG, "electricity_mar": COSTS["2026-03"]["electricity"], "electricity_feb": COSTS["2026-02"]["electricity"],
    },
}

out = ROOT / "src" / "data" / "oil-gas" / "well-kpis.json"
out.write_text(json.dumps({"meta": {"about": "Field 014's plan, loss log, monthly totals, pump history and costs, around March 2026.", "seed": 1402},
                           "monthly": monthly, "loss_log": log, "esp_runs": runs, "costs": COSTS, "story": story}, indent=1) + "\n")

rec = ROOT / "public" / "data" / "field-014"


def write(name, head, rows):
    with open(rec / name, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        w.writerows(rows)


write("production-plan-march-2026.csv", ["month", "basis", "set_on", "plan_bpd", "plan_bbl"],
      [["2026-03", f"2026 business plan: November 2025 tests, declined {round(PLAN_DECLINE * 100)}% a year, less {round(PLAN_ALLOWANCE * 100)}% for downtime", "2025-11-14", int(plan_bpd), int(plan_bbl)]])
write("loss-log-march-2026.csv", ["start", "well_id", "category", "hours", "deferred_bbl", "note"],
      [[r["start"], r["well"], r["category"], r["hours"], r["deferred_bbl"], r.get("note", "")] for r in log])
write("monthly-production-dec-2025-mar-2026.csv", ["month", "days", "metered_oil_bbl", "average_bpd", "well_hours"],
      [[m["month"], m["days"], m["metered_bbl"], m["avg_bpd"], m["well_hours"]] for m in monthly])
write("esp-run-history-2019-2026.csv", ["well_id", "installed", "ended", "run_days", "status", "teardown_finding"],
      [[r["well"], r["installed"], r["ended"], r["days"], r["status"], r["teardown"]] for r in runs])
write("operating-costs-jan-mar-2026.csv", ["month", "category", "usd"], [[m, k, v] for m, c in COSTS.items() for k, v in c.items()])
write("maintenance-backlog-2026.csv", ["month_end", "overdue_work_orders", "estimated_cost_usd"], [[b["month_end"], b["overdue_orders"], b["est_cost_usd"]] for b in BACKLOG])

print(json.dumps(story, indent=1))
