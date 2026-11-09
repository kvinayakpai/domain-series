#!/usr/bin/env python3
"""Field 014, March 2026: the simulated oil field behind the Oil & Gas season.

Sixteen wells on electric submersible pumps (ESPs) feed one processing station, whose fiscal meter
measures the field's oil every day. Each well's share of that oil is allocated from its last well
test, the usual pro-rata method. In March 2026, Well 14's pump wears from 5 March and stops on
20 March, and the test separator is out of service from 7 to 20 March, so Well 14 is never retested.

The script knows what each well really produced (the answer key) and writes what the field's own
systems record: the fiscal meter, the well tests, the allocation report, the pumps' daily data and
the event log. Standard library only, seeded, so every run writes the same files.

    python3 scripts/oil-gas/generate.py

Writes src/data/oil-gas/field-014.json (read by the site, the pictures and the tests) and the
downloadable records in public/data/field-014/.
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = 14
rng = random.Random(SEED)

MARCH = [date(2026, 3, 1) + timedelta(days=i) for i in range(31)]
DAY = {d.isoformat(): i for i, d in enumerate(MARCH)}

# Well, oil rate on 1 March (barrels a day), water cut, decline per year.
WELLS = [
    ("W-01", 612, 0.58, 0.11), ("W-02", 548, 0.66, 0.13), ("W-03", 705, 0.49, 0.10), ("W-04", 431, 0.71, 0.14),
    ("W-05", 389, 0.74, 0.15), ("W-06", 664, 0.55, 0.11), ("W-07", 577, 0.61, 0.12), ("W-08", 498, 0.68, 0.13),
    ("W-09", 726, 0.47, 0.09), ("W-10", 455, 0.70, 0.14), ("W-11", 602, 0.59, 0.12), ("W-12", 517, 0.64, 0.13),
    ("W-13", 683, 0.52, 0.10), ("W-14", 836, 0.44, 0.10), ("W-15", 470, 0.69, 0.14), ("W-16", 541, 0.65, 0.12),
]
IDS = [w[0] for w in WELLS]
CASE = "W-14"

# The test separator's rota: one well every day or two, the same order each month.
ROTA = ["W-10", "W-11", "W-12", "W-13", "W-14", "W-15", "W-16", "W-01", "W-02", "W-03", "W-04", "W-05", "W-06", "W-07", "W-08", "W-09"]
TEST_HOURS = 12
TEST_ERROR = 0.03  # well tests carry a few per cent of error even in good systems
SEPARATOR_OUT = ("2026-03-07T09:00", "2026-03-20T18:00")  # level transmitter failed; part arrived 20 March

# Well 14's pump: wear from 5 March, a trip on 19 March, and a stop on 20 March it cannot restart from.
WEAR_START = 4  # index of 5 March
WEAR_DAYS = 14
WEAR_LOSS = 0.36
TRIP = ("2026-03-19T10:40", "2026-03-19T14:20")
STOP = "2026-03-20T02:15"
POWER_DIP = ("2026-03-23", 1.5)  # a grid dip stops every pump for an hour and a half

METER_ERROR = 0.001  # the fiscal meter is proved monthly and reads within a tenth of a per cent
VFM_ERROR = 0.035  # a pump-data flow estimate (virtual flow meter): a few per cent either way


def hours(ts: str) -> float:
    return int(ts[11:13]) + int(ts[14:16]) / 60


def true_rates() -> dict[str, list[float]]:
    """Each well's real oil rate (barrels a day while running), day by day."""
    out = {}
    for wid, q0, _wc, decl in WELLS:
        e, rates = 0.0, []
        for i in range(31):
            e = 0.6 * e + rng.gauss(0, 0.010)
            q = q0 * math.exp(-decl * i / 365) * (1 + e)
            if wid == CASE and i >= WEAR_START:
                t = min(i - WEAR_START + 0.5, WEAR_DAYS)
                q *= 1 - WEAR_LOSS * t / WEAR_DAYS
            rates.append(q)
        out[wid] = rates
    return out


def run_hours() -> dict[str, list[float]]:
    """Hours each pump ran each day, as SCADA records them."""
    out = {}
    for wid in IDS:
        hrs = []
        for i, d in enumerate(MARCH):
            h = 24.0
            if rng.random() < 0.035:
                h -= rng.choice([1, 2, 3, 4, 5])
            if d.isoformat() == POWER_DIP[0]:
                h -= POWER_DIP[1]
            if wid == CASE:
                if d.isoformat() == TRIP[0][:10]:
                    h = 24 - (hours(TRIP[1]) - hours(TRIP[0]))
                elif d.isoformat() == STOP[:10]:
                    h = hours(STOP)
                elif d.isoformat() > STOP[:10]:
                    h = 0.0
            hrs.append(round(h, 2))
        out[wid] = hrs
    return out


def feb_rate(wid: str, day: int) -> float:
    """Back-cast a well's rate to a February day from its 1 March rate and decline."""
    _id, q0, _wc, decl = next(w for w in WELLS if w[0] == wid)
    days_before = (date(2026, 3, 1) - date(2026, 2, day)).days
    return q0 * math.exp(decl * days_before / 365)


def well_tests(rates):
    """February's tests, then March's: the rota until the separator fails, a catch-up queue after it."""
    tests = []
    for p, wid in enumerate(ROTA):
        day = 1 + math.floor(p * 28 / 16)
        tests.append({"well": wid, "date": f"2026-02-{day:02d}", "oil_bpd": round(feb_rate(wid, day) * (1 + rng.gauss(0, TEST_ERROR))), "hours": TEST_HOURS, "note": ""})
    out_from, out_to = SEPARATOR_OUT[0][:10], SEPARATOR_OUT[1][:10]
    deferred, cancelled = [], []
    for p, wid in enumerate(ROTA):
        due = MARCH[math.floor(p * 30 / 16)].isoformat()
        if out_from <= due <= out_to:
            deferred.append((wid, due))
            continue
        if due > out_to:
            deferred.append((wid, due))  # the queue after the repair takes the rest of the rota too
            continue
        q = rates[wid][DAY[due]]
        tests.append({"well": wid, "date": due, "oil_bpd": round(q * (1 + rng.gauss(0, TEST_ERROR))), "hours": TEST_HOURS, "note": ""})
    day = DAY["2026-03-21"]
    for wid, due in deferred:
        if wid == CASE:
            cancelled.append({"well": wid, "due": due, "reason": "test separator out of service, then the well was down"})
            continue
        d = MARCH[day].isoformat()
        note = f"due {due}, deferred: separator out of service" if due <= out_to else f"due {due}, after the catch-up"
        tests.append({"well": wid, "date": d, "oil_bpd": round(rates[wid][day] * (1 + rng.gauss(0, TEST_ERROR))), "hours": TEST_HOURS, "note": note})
        day += 1
    tests.sort(key=lambda t: (t["date"], t["well"]))
    return tests, cancelled


def latest_test(tests, wid: str, iso: str):
    """The test in force on a day: the latest one on or before it (a test counts from its own day)."""
    return max((t for t in tests if t["well"] == wid and t["date"] <= iso), key=lambda t: t["date"])


def telemetry(rates, hrs):
    """Daily averages from each pump: motor temperature, motor current, pump intake pressure."""
    base = {wid: (round(rng.uniform(102, 114), 1), round(rng.uniform(38, 52), 1), round(rng.uniform(52, 70), 1)) for wid in IDS}
    out = {}
    for wid in IDS:
        temp, amps, intake = [], [], []
        t0, a0, p0 = base[wid]
        for i in range(31):
            if hrs[wid][i] == 0:
                temp.append(None); amps.append(None); intake.append(None)
                continue
            dt = da = dp = 0.0
            if wid == CASE and i >= WEAR_START:
                x = min(i - WEAR_START + 0.5, WEAR_DAYS) / WEAR_DAYS
                dt, da, dp = 22 * x ** 1.3, 4.8 * x ** 1.4, 13 * x ** 1.2
            temp.append(round(t0 + dt + rng.gauss(0, 0.6), 1))
            amps.append(round(a0 + da + rng.gauss(0, 0.4), 1))
            intake.append(round(p0 + dp + rng.gauss(0, 0.5), 1))
        out[wid] = {"motor_c": temp, "current_a": amps, "intake_bar": intake, "base": {"motor_c": t0, "current_a": a0, "intake_bar": p0}}
    return out


def main():
    rates = true_rates()
    hrs = run_hours()
    tests, cancelled = well_tests(rates)
    tele = telemetry(rates, hrs)

    produced = {w: [rates[w][i] * hrs[w][i] / 24 for i in range(31)] for w in IDS}
    vfm = {w: [produced[w][i] * (1 + rng.gauss(0, VFM_ERROR)) for i in range(31)] for w in IDS}
    true_total = [sum(produced[w][i] for w in IDS) for i in range(31)]
    metered = [true_total[i] * (1 + rng.gauss(0, METER_ERROR)) for i in range(31)]

    in_force = {w: [latest_test(tests, w, d.isoformat()) for d in MARCH] for w in IDS}
    theo = {w: [in_force[w][i]["oil_bpd"] * hrs[w][i] / 24 for i in range(31)] for w in IDS}
    af = [metered[i] / sum(theo[w][i] for w in IDS) for i in range(31)]
    alloc = {w: [theo[w][i] * af[i] for i in range(31)] for w in IDS}

    # ---------- the story, in the numbers the posts quote ----------
    i18, i5, i20 = DAY["2026-03-18"], DAY["2026-03-05"], DAY["2026-03-20"]
    span = range(i5, i20 + 1)
    w14_alloc = sum(alloc[CASE][i] for i in span)
    w14_prod = sum(produced[CASE][i] for i in span)
    others_alloc = sum(alloc[w][i] for w in IDS if w != CASE for i in span)
    others_prod = sum(produced[w][i] for w in IDS if w != CASE for i in span)
    t14 = latest_test(tests, CASE, "2026-03-20")
    test_age = (date.fromisoformat(STOP[:10]) - date.fromisoformat(t14["date"])).days

    # The check: a well's allocated oil above its pump-data estimate by more than 10%, two days running.
    def flags(w):
        hits = []
        for i in range(1, 31):
            ok = lambda k: alloc[w][k] > 0 and vfm[w][k] > 0 and alloc[w][k] > 1.10 * vfm[w][k]
            if ok(i) and ok(i - 1):
                hits.append(MARCH[i].isoformat())
        return hits
    all_flags = {w: flags(w) for w in IDS}
    first14 = all_flags[CASE][0]
    other_flag_days = {w: f for w, f in all_flags.items() if w != CASE and f}

    # When the pump's own data parted from its base: motor temperature 5 degrees C above its February level.
    base_t = tele[CASE]["base"]["motor_c"]
    warm = next(MARCH[i].isoformat() for i in range(31) if tele[CASE]["motor_c"][i] is not None and tele[CASE]["motor_c"][i] > base_t + 5)

    meter_err = [abs(metered[i] / true_total[i] - 1) for i in range(31)]
    story = {
        "field": {
            "wells": len(IDS),
            "oil_bpd_1mar": round(sum(w[1] for w in WELLS)),
            "march_metered_bbl": round(sum(metered)),
            "march_produced_bbl": round(sum(true_total)),
        },
        "case_well": CASE,
        "w14_test": {"date": t14["date"], "oil_bpd": t14["oil_bpd"], "age_days_at_stop": test_age},
        "w14_18mar": {"allocated": round(alloc[CASE][i18]), "produced": round(produced[CASE][i18]), "vfm": round(vfm[CASE][i18])},
        "w14_1mar": {"allocated": round(alloc[CASE][0]), "produced": round(produced[CASE][0])},
        "overstated": {
            "from": MARCH[i5].isoformat(), "to": MARCH[i20].isoformat(),
            "allocated_bbl": round(w14_alloc), "produced_bbl": round(w14_prod), "extra_bbl": round(w14_alloc - w14_prod),
            "others_understated_pct": round((others_prod - others_alloc) / others_prod * 100, 1),
        },
        "af": {"first_week_mean": round(sum(af[:4]) / 4, 3), "on_18mar": round(af[i18], 3), "min": round(min(af[:i20]), 3), "max": round(max(af), 3)},
        "meter": {"max_daily_error_pct": round(max(meter_err) * 100, 2), "month_error_pct": round(abs(sum(metered) / sum(true_total) - 1) * 100, 3)},
        "pump": {
            "wear_from": MARCH[WEAR_START].isoformat(), "trip": TRIP[0], "restart": TRIP[1], "stop": STOP,
            "warm_day": warm, "motor_c_base": base_t, "motor_c_18mar": tele[CASE]["motor_c"][i18],
            "current_a_base": tele[CASE]["base"]["current_a"], "current_a_18mar": tele[CASE]["current_a"][i18],
            "intake_bar_base": tele[CASE]["base"]["intake_bar"], "intake_bar_18mar": tele[CASE]["intake_bar"][i18],
        },
        "check": {
            "rule": "allocated oil above the pump-data estimate by more than 10%, two days running",
            "first_flag_w14": first14,
            "days_before_stop": (date.fromisoformat(STOP[:10]) - date.fromisoformat(first14)).days,
            "other_wells_flagged": sorted(other_flag_days),
            "other_flag_days": sum(len(f) for f in other_flag_days.values()),
        },
        "separator": {"out_from": SEPARATOR_OUT[0], "out_to": SEPARATOR_OUT[1], "cancelled": cancelled},
    }

    def r1(xs):
        return [None if x is None else round(x, 1) for x in xs]

    data = {
        "meta": {
            "name": "Field 014",
            "about": "A simulated onshore oil field in western India: sixteen wells on electric submersible pumps, one processing station, March 2026.",
            "seed": SEED,
            "days": [d.isoformat() for d in MARCH],
            "wells": [{"id": w, "oil_bpd_1mar": q, "water_cut": wc, "decline_per_year": dc, "lift": "ESP"} for w, q, wc, dc in WELLS],
            "allocation": "pro rata on the last well test: each well's test rate times its run hours, scaled so the wells add up to the fiscal meter",
        },
        "tests": tests,
        "daily": {
            "metered": r1(metered),
            "produced_total": r1(true_total),
            "af": [round(x, 4) for x in af],
            "wells": {
                w: {
                    "run_hours": hrs[w],
                    "test_rate": [in_force[w][i]["oil_bpd"] for i in range(31)],
                    "test_date": [in_force[w][i]["date"] for i in range(31)],
                    "allocated": r1(alloc[w]),
                    "produced": r1(produced[w]),
                    "vfm": r1(vfm[w]),
                    "motor_c": tele[w]["motor_c"],
                    "current_a": tele[w]["current_a"],
                    "intake_bar": tele[w]["intake_bar"],
                }
                for w in IDS
            },
        },
        "events": [
            {"ts": SEPARATOR_OUT[0], "well": "", "system": "maintenance", "event": "Test separator out of service: level transmitter failed"},
            {"ts": TRIP[0], "well": CASE, "system": "SCADA", "event": "ESP trip: motor overload"},
            {"ts": TRIP[1], "well": CASE, "system": "SCADA", "event": "ESP restarted"},
            {"ts": STOP, "well": CASE, "system": "SCADA", "event": "ESP trip: motor overload; restart failed (phase imbalance)"},
            {"ts": SEPARATOR_OUT[1], "well": "", "system": "maintenance", "event": "Test separator back in service"},
            {"ts": f"{POWER_DIP[0]}T14:00", "well": "", "system": "SCADA", "event": "Grid dip: all pumps stopped for 1.5 hours"},
        ],
        "story": story,
    }
    out = ROOT / "src" / "data" / "oil-gas" / "field-014.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1) + "\n")

    rec = ROOT / "public" / "data" / "field-014"
    rec.mkdir(parents=True, exist_ok=True)

    def write(name, head, rows):
        with open(rec / name, "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(head)
            w.writerows(rows)

    write("well-tests-feb-mar-2026.csv", ["well_id", "test_date", "duration_h", "oil_bpd", "note"],
          [[t["well"], t["date"], t["hours"], t["oil_bpd"], t["note"]] for t in tests])
    write("fiscal-meter-march-2026.csv", ["date", "oil_bbl"], [[MARCH[i].isoformat(), round(metered[i], 1)] for i in range(31)])
    write("production-allocation-march-2026.csv",
          ["date", "well_id", "run_hours", "test_date", "test_rate_bpd", "theoretical_bbl", "allocation_factor", "allocated_bbl"],
          [[MARCH[i].isoformat(), w, hrs[w][i], in_force[w][i]["date"], in_force[w][i]["oil_bpd"], round(theo[w][i], 1), round(af[i], 4), round(alloc[w][i], 1)]
           for i in range(31) for w in IDS])
    write("esp-daily-march-2026.csv", ["date", "well_id", "run_hours", "motor_temp_c", "motor_current_a", "intake_pressure_bar", "flow_estimate_oil_bbl"],
          [[MARCH[i].isoformat(), w, hrs[w][i], tele[w]["motor_c"][i] if tele[w]["motor_c"][i] is not None else "", tele[w]["current_a"][i] if tele[w]["current_a"][i] is not None else "",
            tele[w]["intake_bar"][i] if tele[w]["intake_bar"][i] is not None else "", round(vfm[w][i], 1)] for i in range(31) for w in IDS])
    write("events-march-2026.csv", ["ts", "well_id", "system", "event"], [[e["ts"], e["well"], e["system"], e["event"]] for e in sorted(data["events"], key=lambda e: e["ts"])])
    write("answer-key-produced-march-2026.csv", ["date", "well_id", "produced_oil_bbl"], [[MARCH[i].isoformat(), w, round(produced[w][i], 1)] for i in range(31) for w in IDS])

    print(json.dumps(story, indent=1))


if __name__ == "__main__":
    main()
