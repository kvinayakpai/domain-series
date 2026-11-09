#!/usr/bin/env python3
"""Between the field and the refinery, March 2026: the pipe, the tank, the gas and the ship.

Field 014's oil leaves through its fiscal meter (the net oil in field-014.json) into a 140 km
pipeline to Refinery 014, where a receipt meter measures it into crude tank T-104. Field 014's
associated gas is compressed and sold. Refinery 014's imported crude arrives by tanker at a single
point mooring off the coast. In March 2026:

- the field's heater-treater HT-1 loses its burner on 11 March, so the crude carries more water
  until 21 March (throughput, KPI 7)
- the refinery's receipt meter reads about 0.18% high after its February proving, and the March
  proving waits for the prover (loss and gain, KPI 8)
- T-104's free-water probe fails on 2 March, so neither the book nor the gauge sees the water that
  settles (tank stock accuracy, KPI 9)
- compressor K-2's blowdown valve passes gas from 6 to 16 March; a satellite sees the plume on
  14 March (methane intensity, KPI 10)
- a replacement cargo for the Gulf crude arrives on 24 March and waits at anchor (ship waiting, KPI 11)

Standard library only and seeded, so every run writes the same files.

    python3 scripts/oil-gas/generate.py && python3 scripts/oil-gas/pipe.py
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
F = json.loads((ROOT / "src" / "data" / "oil-gas" / "field-014.json").read_text())
rng = random.Random(1407)
DAYS = F["meta"]["days"]
N = len(DAYS)
NET = F["daily"]["metered"]  # barrels of oil a day through the field's fiscal meter


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s)


def frac_of_day(day: str, start: str, end: str) -> float:
    """The share of a day that falls between start and end."""
    d0, d1 = ts(f"{day}T00:00"), ts(f"{day}T00:00") + timedelta(days=1)
    a, b = max(d0, ts(start)), min(d1, ts(end))
    return max((b - a).total_seconds(), 0) / 86400


# ---------- KPI 7: water in the crude ----------
HT_FAULT = ("2026-03-11T16:00", "2026-03-21T12:00")  # HT-1 burner flame failure until the igniter was replaced
BSW_BASE, BSW_FAULT = 0.0025, 0.0185
bsw = []
for d in DAYS:
    f = frac_of_day(d, *HT_FAULT)
    level = BSW_BASE + f * (BSW_FAULT - BSW_BASE) + (rng.gauss(0, 0.0018) if f > 0.5 else 0)
    bsw.append(max(level + rng.gauss(0, 0.0003), 0.0015))
gross = [NET[i] / (1 - bsw[i]) for i in range(N)]
water = [gross[i] - NET[i] for i in range(N)]

# ---------- KPI 8: the receipt meter reads high ----------
RECEIPT_BIAS = 0.0018
TOL = 0.30  # the pipeline's daily loss and gain alarm band, per cent
receipt = [gross[i] * (1 + RECEIPT_BIAS + rng.gauss(0, 0.0005)) for i in range(N)]
lg_pct = [(receipt[i] - gross[i]) / gross[i] * 100 for i in range(N)]
run, first_alert = 0, None
for i in range(N):
    run = run + 1 if lg_pct[i] > 0 else 0
    if run == 7 and first_alert is None:
        first_alert = DAYS[i]
PROVINGS = [
    {"meter": "Refinery 014 receipt meter FT-104", "date": "2026-01-27", "meter_factor": 0.9994, "result": "accepted"},
    {"meter": "Refinery 014 receipt meter FT-104", "date": "2026-02-26", "meter_factor": 0.9991, "result": "accepted"},
    {"meter": "Refinery 014 receipt meter FT-104", "date": "2026-03-26", "meter_factor": None, "result": "postponed: prover away for calibration until 6 April"},
]

# ---------- KPI 9: tank T-104 ----------
LAB_BSW = [round(0.0030 + rng.gauss(0, 0.0003), 4) for _ in range(N)]  # the receipt sampler draws from the top of the line
SETTLE = 0.85  # share of the water that settles to the bottom as free water
PROBE_FAIL = "2026-03-02"
oil, free, susp = 58_000.0, 420.0, 60.0  # opening: oil, free water and suspended water (barrels)
book = 58_000.0
t104 = []
for i, d in enumerate(DAYS):
    oil_in, water_in = NET[i], water[i]
    free += SETTLE * water_in
    susp += (1 - SETTLE) * water_in
    # The crude unit draws about the day's receipt; what it draws carries the suspended water with it.
    draw_total = gross[i] * (1 + rng.gauss(0, 0.02))
    susp_share = susp / (oil + susp)
    oil_out, susp_out = draw_total * (1 - susp_share), draw_total * susp_share
    oil += oil_in - oil_out
    susp -= susp_out
    issued_gross = draw_total  # the outlet meter measures what leaves
    book += receipt[i] * (1 - LAB_BSW[i]) - issued_gross * (1 - LAB_BSW[i])
    total_liquid = oil + free + susp
    free_seen = free if d < PROBE_FAIL else 0.0
    gauge_net = (total_liquid - free_seen) * (1 - LAB_BSW[i])
    t104.append({"date": d, "book_net": book, "gauge_total": total_liquid, "free_water_probe": free_seen, "gauge_net": gauge_net,
                 "diff_pct": (book - gauge_net) / gauge_net * 100, "true_oil": oil, "true_free": free})
end = t104[-1]
dip_free = round(end["true_free"] / 10) * 10  # the 31 March manual dip, to the nearest ten barrels

# ---------- KPI 10: methane ----------
GOR = 360  # standard cubic feet of gas per barrel of oil
CH4_SHARE = 0.82  # methane, mole fraction of the gas
M3_PER_MMSCF = 28_317
KG_PER_M3 = 0.678  # methane at standard conditions
INVENTORY_T = 2.1  # the field's monthly estimate from emission factors, the same since January
LEAK = ("2026-03-06T15:00", "2026-03-16T18:30")  # K-2 blowdown valve passing after its restart
LEAK_KG_H = 230  # measured on site with a high-flow sampler, 15 March
SAT = {"ts": "2026-03-14T11:10", "kg_h": 260, "uncertainty_pct": 50}
gas = []
for i, d in enumerate(DAYS):
    produced = NET[i] * GOR / 1e6  # MMscf
    fuel, flare = 0.55 * (1 + rng.gauss(0, 0.02)), 0.08 * (1 + rng.gauss(0, 0.1))
    leak_h = frac_of_day(d, *LEAK) * 24
    leak_mmscf = LEAK_KG_H * leak_h / KG_PER_M3 / CH4_SHARE / M3_PER_MMSCF
    normal_ua = produced * (0.015 + rng.gauss(0, 0.002))
    sold = produced - fuel - flare - normal_ua - leak_mmscf
    gas.append({"date": d, "produced": produced, "fuel": fuel, "flare": flare, "sold": sold, "unaccounted": normal_ua + leak_mmscf, "leak_kg": LEAK_KG_H * leak_h})
leak_t = sum(g["leak_kg"] for g in gas) / 1000
sold_m3 = sum(g["sold"] for g in gas) * M3_PER_MMSCF
mi_reported = INVENTORY_T * 1000 / KG_PER_M3 / sold_m3
mi_real = (INVENTORY_T + leak_t) * 1000 / KG_PER_M3 / sold_m3
ua_before = sum(g["unaccounted"] for g in gas[:5]) / sum(g["produced"] for g in gas[:5])
leak_days = [i for i, g in enumerate(gas) if g["leak_kg"] > LEAK_KG_H * 20]
ua_leak = sum(gas[i]["unaccounted"] for i in leak_days) / sum(gas[i]["produced"] for i in leak_days)

# ---------- KPI 11: the replacement cargo ----------
CARGO = {
    "cargo": "replacement cargo, West African crude, about 2 million barrels",
    "arrived": "2026-03-24T05:50", "nor": "2026-03-24T06:00", "notice_h": 6, "laytime_h": 36,
    "window": "2026-03-27T18:00",  # the berthing window the port's schedule gave it, after the tanker at the mooring and a hose change
    "berthed": "2026-03-28T09:40", "hoses_off": "2026-03-30T05:00", "demurrage_usd_day": 165_000,
}
reported_wait_d = (ts(CARGO["berthed"]) - ts(CARGO["window"])).total_seconds() / 86400
real_wait_d = (ts(CARGO["berthed"]) - ts(CARGO["nor"])).total_seconds() / 86400
laytime_end = ts(CARGO["nor"]) + timedelta(hours=CARGO["notice_h"] + CARGO["laytime_h"])
dem_days = (ts(CARGO["hoses_off"]) - laytime_end).total_seconds() / 86400
VESSELS = [
    {"vessel": "Tanker A (Arab Light, loaded at Yanbu)", "arrived": "2026-03-21T14:20", "nor": "2026-03-21T14:30", "window": "2026-03-22T06:00",
     "berthed": "2026-03-22T07:10", "hoses_off": "2026-03-26T22:00", "note": "discharge slowed by a hose leak, 24 to 25 March"},
    {"vessel": "Replacement cargo (West African crude)", "arrived": CARGO["arrived"], "nor": CARGO["nor"], "window": CARGO["window"],
     "berthed": CARGO["berthed"], "hoses_off": CARGO["hoses_off"], "note": "hose change on the mooring, 27 March"},
]
for v in VESSELS:
    v["reported_wait_days"] = round((ts(v["berthed"]) - ts(v["window"])).total_seconds() / 86400, 2)
    v["wait_from_nor_days"] = round((ts(v["berthed"]) - ts(v["nor"])).total_seconds() / 86400, 2)
port_avg_reported = sum(v["reported_wait_days"] for v in VESSELS) / len(VESSELS)

fault_days = [i for i, d in enumerate(DAYS) if frac_of_day(d, *HT_FAULT) > 0.9]
worst = max(range(N), key=lambda i: bsw[i])
story = {
    "pipeline_km": 140,
    "throughput": {
        "gross_bbl": round(sum(gross)), "net_bbl": round(sum(NET)), "water_bbl": round(sum(water)),
        "water_pct": round(sum(water) / sum(gross) * 100, 2), "gross_bpd": round(sum(gross) / N),
        "bsw_base_pct": round(BSW_BASE * 100, 2), "worst_day": DAYS[worst], "worst_bsw_pct": round(bsw[worst] * 100, 1),
        "worst_water_bbl": round(water[worst]), "worst_gross_bbl": round(gross[worst]),
        "fault_from": HT_FAULT[0], "fault_to": HT_FAULT[1],
        "fault_water_bbl": round(sum(water[i] for i in fault_days)), "fault_days": len(fault_days),
        "fault_avg_bsw_pct": round(sum(bsw[i] for i in fault_days) / len(fault_days) * 100, 1),
        "spec_pct": 1.0,
    },
    "loss_gain": {
        "bias_pct": round(RECEIPT_BIAS * 100, 2), "tolerance_pct": TOL, "days_positive": sum(1 for x in lg_pct if x > 0),
        "days_inside": sum(1 for x in lg_pct if abs(x) <= TOL), "max_pct": round(max(lg_pct), 2), "min_pct": round(min(lg_pct), 2),
        "gain_bbl": round(sum(receipt) - sum(gross)), "first_alert_7_days": first_alert,
        "last_proving": "2026-02-26", "proving_due": "2026-03-26", "prover_back": "2026-04-06",
    },
    "tank": {
        "name": "T-104", "probe_failed": PROBE_FAIL, "opening_free_water_bbl": 420,
        "book_31": round(end["book_net"]), "gauge_net_31": round(end["gauge_net"]), "diff_pct_31": round(end["diff_pct"], 2),
        "max_abs_diff_pct": round(max(abs(r["diff_pct"]) for r in t104), 2),
        "true_oil_31": round(end["true_oil"]), "dip_free_water_31": dip_free,
        "book_over_true_bbl": round(end["book_net"] - end["true_oil"]), "gauge_over_true_bbl": round(end["gauge_net"] - end["true_oil"]),
        "lab_bsw_avg_pct": round(sum(LAB_BSW) / N * 100, 2),
    },
    "methane": {
        "inventory_t": INVENTORY_T, "leak_t": round(leak_t, 1), "leak_kg_h": LEAK_KG_H, "leak_from": LEAK[0], "leak_to": LEAK[1],
        "leak_hours": round((ts(LEAK[1]) - ts(LEAK[0])).total_seconds() / 3600, 1), "satellite": SAT,
        "sold_mm3": round(sold_m3 / 1e6, 2), "mi_reported_pct": round(mi_reported * 100, 2), "mi_real_pct": round(mi_real * 100, 1),
        "leak_x_inventory": round(leak_t / INVENTORY_T), "ua_before_pct": round(ua_before * 100, 1), "ua_leak_pct": round(ua_leak * 100, 1),
        "benchmark_pct": 0.20, "gor": GOR,
    },
    "ship": {
        **CARGO, "reported_wait_days": round(reported_wait_d, 1), "real_wait_days": round(real_wait_d, 1),
        "laytime_end": laytime_end.isoformat(timespec="minutes"), "demurrage_days": round(dem_days, 2),
        "demurrage_usd": round(dem_days * CARGO["demurrage_usd_day"], -3), "port_avg_reported_days": round(port_avg_reported, 1),
        "port_avg_from_nor_days": round(sum(v["wait_from_nor_days"] for v in VESSELS) / len(VESSELS), 1),
    },
}

r1 = lambda xs: [round(x, 1) for x in xs]
data = {
    "meta": {"about": "Field 014's pipeline to Refinery 014, tank T-104, the field's gas and the refinery's crude tankers, March 2026.", "seed": 1407, "days": DAYS},
    "daily": {
        "net": r1(NET), "gross": r1(gross), "water": r1(water), "bsw_pct": [round(x * 100, 2) for x in bsw], "lab_bsw_pct": [round(x * 100, 2) for x in LAB_BSW],
        "receipt": r1(receipt), "lg_pct": [round(x, 3) for x in lg_pct],
        "t104": [{k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()} for r in t104],
        "gas": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in g.items()} for g in gas],
    },
    "provings": PROVINGS, "vessels": VESSELS, "story": story,
}
(ROOT / "src" / "data" / "oil-gas" / "pipe-014.json").write_text(json.dumps(data, indent=1) + "\n")

rec = ROOT / "public" / "data" / "pipe-014"
rec.mkdir(parents=True, exist_ok=True)


def write(name, head, rows):
    with open(rec / name, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        w.writerows(rows)


write("field-dispatch-march-2026.csv", ["date", "gross_standard_bbl", "bsw_pct", "net_oil_bbl"],
      [[DAYS[i], round(gross[i], 1), round(bsw[i] * 100, 2), round(NET[i], 1)] for i in range(N)])
write("pipeline-throughput-march-2026.csv", ["date", "throughput_bbl"], [[DAYS[i], round(gross[i], 1)] for i in range(N)])
write("receipt-meter-march-2026.csv", ["date", "gross_standard_bbl", "lab_bsw_pct", "net_oil_booked_bbl"],
      [[DAYS[i], round(receipt[i], 1), round(LAB_BSW[i] * 100, 2), round(receipt[i] * (1 - LAB_BSW[i]), 1)] for i in range(N)])
write("loss-gain-march-2026.csv", ["date", "dispatched_bbl", "received_bbl", "gain_bbl", "gain_pct", "alarm_band_pct"],
      [[DAYS[i], round(gross[i], 1), round(receipt[i], 1), round(receipt[i] - gross[i], 1), round(lg_pct[i], 3), TOL] for i in range(N)])
write("meter-provings-2026.csv", ["meter", "date", "meter_factor", "result"], [[p["meter"], p["date"], p["meter_factor"] or "", p["result"]] for p in PROVINGS])
write("tank-t104-march-2026.csv", ["date", "book_net_bbl", "gauge_total_bbl", "free_water_probe_bbl", "gauge_net_bbl", "book_minus_gauge_pct"],
      [[r["date"], round(r["book_net"], 1), round(r["gauge_total"], 1), round(r["free_water_probe"], 1), round(r["gauge_net"], 1), round(r["diff_pct"], 3)] for r in t104])
write("tank-t104-dips-2026.csv", ["date", "method", "free_water_bbl"], [["2026-02-28", "manual dip, water-finding paste", 420], ["2026-03-31", "manual dip, water-finding paste", dip_free]])
write("gas-balance-march-2026.csv", ["date", "produced_mmscf", "fuel_mmscf", "flare_mmscf", "sold_mmscf", "unaccounted_mmscf"],
      [[g["date"], round(g["produced"], 3), round(g["fuel"], 3), round(g["flare"], 3), round(g["sold"], 3), round(g["unaccounted"], 3)] for g in gas])
write("methane-march-2026.csv", ["date", "source", "record", "methane"],
      [["2026-03", "inventory", "monthly estimate from emission factors", f"{INVENTORY_T} t"],
       [SAT["ts"], "satellite", "plume over compressor station, K-2 area", f"{SAT['kg_h']} kg/h, plus or minus {SAT['uncertainty_pct']}%"],
       ["2026-03-15T10:30", "site survey", "optical gas imaging: K-2 blowdown valve passing; high-flow sampler", f"{LEAK_KG_H} kg/h"],
       [LEAK[1], "maintenance", "K-2 blowdown valve isolated and replaced", "0 kg/h"]])
write("vessel-log-march-2026.csv", ["vessel", "arrived", "notice_of_readiness", "berthing_window", "berthed", "hoses_off", "waiting_days_reported", "note"],
      [[v["vessel"], v["arrived"], v["nor"], v["window"], v["berthed"], v["hoses_off"], v["reported_wait_days"], v["note"]] for v in VESSELS])
write("answer-key-pipe-march-2026.csv", ["date", "water_in_crude_bbl", "t104_true_oil_bbl", "t104_free_water_bbl", "k2_methane_kg"],
      [[DAYS[i], round(water[i], 1), round(t104[i]["true_oil"], 1), round(t104[i]["true_free"], 1), round(gas[i]["leak_kg"], 1)] for i in range(N)])

print(json.dumps(story, indent=1))
