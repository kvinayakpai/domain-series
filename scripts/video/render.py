"""Render the captioned videos for each post from the built site.

Each scene is a crisp still of the real site (demo or post) with its caption burned in,
joined with short crossfades. Captions read their numbers from src/data/*.json, so the
videos cannot drift from the world. Captions only: no narration.

    npm run build
    python3 scripts/video/render.py                       # every post, both videos
    python3 scripts/video/render.py logistics             # one post, both videos
    python3 scripts/video/render.py retail short          # 1080x1920, about a minute
    python3 scripts/video/render.py logistics walkthrough # 1920x1080, about two minutes
    python3 scripts/video/render.py payments              # part 3

Writes public/media/<post>-<name>.mp4, .srt and -poster.jpg. Needs Playwright (Python)
with Chromium, and ffmpeg with libx264.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "media"
PORT = 4340
BASE = f"http://127.0.0.1:{PORT}/domain-series/"
FADE = 0.6
FPS = 30

D = json.loads((ROOT / "src" / "data" / "retail.json").read_text())
AI = json.loads((ROOT / "src" / "data" / "retail-ai.json").read_text())
S = {s["key"]: s for s in D["scenarios"]}
ASIS, GAP, BINS = S["off|today"], S["gap|today"], S["off|scanned"]
EP = D["story"]["episode"]
W = D["story"]["kpis"]["weekly"]
REC5 = W["recorded_sales"]["ATTA-WW-5KG"]
SHARE = [REC5[k] / (REC5[k] + W["recorded_sales"]["ATTA-WW-1KG"][k] + W["recorded_sales"]["ATTA-WW-10KG"][k]) for k in range(4)]
OSA = ASIS["kpis"]["osa"]
HERO = AI["forecast"]["by_sku"]["ATTA-WW-5KG"]
FLAG = AI["detector"]["hero_flags"][0]
OPT = {o["label"]: o for o in AI["detector"]["options"]}
SCORE = AI["assistant"]["score"]
AVAIL = AI["availability"]
PASSED = sum(t["pass"] for t in AI["tests"]["generic"])
FALL = round((1 - REC5[1] / REC5[0]) * 100)


def signed(x: float) -> str:
    return f"{'−' if x < 0 else '+'}{round(abs(x) * 100)}%"


L = json.loads((ROOT / "src" / "data" / "logistics.json").read_text())
LS = {s["key"]: s for s in L["scenarios"]}
LA, LPICK, LWEIGH, LCASE = LS["none|label"], LS["pick_scan|label"], LS["check_weigh|label"], LS["none|case_scan"]
LST = L["story"]
LEP = LST["episode"]
LK = LA["kpis"]
LFIVE = next(c for c in LST["corrections"] if c["sku"] == "ATTA-WW-5KG")
LONE = next(c for c in LST["corrections"] if c["sku"] == "ATTA-WW-1KG")

P = json.loads((ROOT / "src" / "data" / "payments.json").read_text())
PS = {s["key"]: s for s in P["scenarios"]}
PA, PCHECK, PREF = PS["retry|manual"], PS["check|manual"], PS["retry|bill_ref"]
PST = P["story"]
PSLOW, PJUNE, PREFUNDS = PST["slowdown"], PST["june"], PST["refunds"]
PHOURS = {x["hour"]: x for x in PST["slowdown_day_by_hour"]}
PDAY = {x["date"]: x for x in PA["daily"]}


def pct(x: float) -> str:
    return f"{round(x * 100)}%"


def inr(x: float) -> str:
    return f"₹{round(x):,}"


# ---------- page helpers (run inside the page) ----------
CAPTION_JS = """([text, fs, bottom, maxw]) => {
  let c = document.getElementById('video-caption');
  if (!text) { if (c) c.remove(); return; }
  if (!c) { c = document.createElement('div'); c.id = 'video-caption'; document.body.append(c); }
  c.textContent = text;
  Object.assign(c.style, { position: 'fixed', left: '50%', transform: 'translateX(-50%)', bottom: bottom + 'px',
    width: 'calc(100% - 32px)', maxWidth: maxw + 'px', zIndex: 9999, background: 'rgba(20,26,33,0.94)', color: '#f5f6f4',
    fontFamily: "'Literata Variable', Georgia, serif", fontSize: fs + 'px', lineHeight: 1.38, padding: '0.7em 0.9em',
    borderRadius: '10px', boxShadow: '0 6px 24px rgba(0,0,0,0.25)', boxSizing: 'border-box' });
}"""

CARD_JS = """([kicker, title, lines, foot, fs]) => {
  let c = document.getElementById('video-card');
  if (!title) { if (c) c.remove(); return; }
  if (!c) { c = document.createElement('div'); c.id = 'video-card'; document.body.append(c); }
  c.replaceChildren();
  Object.assign(c.style, { position: 'fixed', inset: 0, zIndex: 10000, background: '#f5f6f4', color: '#1b2430',
    display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: (fs * (fs < 40 ? 0.7 : 0.9)) + 'px', padding: (fs * (fs < 40 ? 1.3 : 2)) + 'px', boxSizing: 'border-box' });
  const k = document.createElement('p'); k.textContent = kicker;
  Object.assign(k.style, { margin: 0, fontFamily: "'Anek Latin Variable', sans-serif", fontWeight: 600, fontSize: (fs * 0.75) + 'px', color: '#59626d' });
  const h = document.createElement('h1'); h.textContent = title;
  Object.assign(h.style, { margin: 0, fontFamily: "'Anek Latin Variable', sans-serif", fontWeight: 700, fontStretch: '78%', fontSize: (fs * 2.3) + 'px', lineHeight: 1.02 });
  c.append(k, h);
  for (const [label, text, voice] of lines) {
    const box = document.createElement('div');
    const l = document.createElement('p'); l.textContent = label;
    Object.assign(l.style, { margin: '0 0 ' + (fs * 0.2) + 'px', fontFamily: "'Anek Latin Variable', sans-serif", fontSize: (fs * 0.62) + 'px', color: '#59626d' });
    const t = document.createElement('p'); t.textContent = text;
    Object.assign(t.style, voice === 'record'
      ? { margin: 0, fontFamily: "'IBM Plex Mono', monospace", fontSize: (fs * (fs < 40 ? 0.72 : 0.9)) + 'px', lineHeight: 1.3, color: '#2f55a4' }
      : { margin: 0, fontFamily: "'Literata Variable', serif", fontSize: (fs * 1.0) + 'px', lineHeight: 1.3, display: 'inline', background: '#ffe14d', padding: '0 0.2em', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' });
    box.append(l, t); c.append(box);
  }
  const f = document.createElement('p'); f.textContent = foot;
  Object.assign(f.style, { margin: 0, fontFamily: "'Anek Latin Variable', sans-serif", fontSize: (fs * 0.6) + 'px', color: '#59626d' });
  c.append(f);
}"""


class Shot:
    def __init__(self, page: Page, fs: int, bottom: int, maxw: int, card_fs: int):
        self.page, self.fs, self.bottom, self.maxw, self.card_fs = page, fs, bottom, maxw, card_fs

    def goto(self, path: str) -> None:
        self.page.goto(BASE + path)
        self.page.wait_for_load_state("networkidle")
        self.page.evaluate("document.fonts.ready")
        if path.startswith("demo"):
            self.page.wait_for_selector('[data-retail-demo][data-ready="true"]')
            self.page.wait_for_selector('[data-logistics-demo][data-ready="true"]')
            self.page.wait_for_selector('[data-payments-demo][data-ready="true"]')

    def to(self, selector: str, offset: int = 16) -> None:
        self.page.evaluate("""([sel, off]) => { const e = document.querySelector(sel); if (!e) throw new Error('missing ' + sel);
            window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - off); }""", [selector, offset])

    def demo(self, js: str) -> None:
        self.page.evaluate(js)
        self.page.wait_for_timeout(120)

    def caption(self, text: str | None) -> None:
        self.page.evaluate(CAPTION_JS, [text, self.fs, self.bottom, self.maxw])

    def card(self, kicker: str, title: str, lines: list, foot: str) -> None:
        self.page.evaluate(CARD_JS, [kicker, title, lines, foot, self.card_fs])

    def clear(self) -> None:
        self.page.evaluate(CARD_JS, ["", "", [], "", 0])
        self.caption(None)

    def snap(self, path: Path) -> None:
        self.page.wait_for_timeout(150)
        self.page.screenshot(path=str(path))


# ---------- the two videos ----------
TITLE = ("Why Domain Matters, part 1", "Retail and grocery",
         [["The record says", f"5 kg atta: sales −{FALL}% week on week.", "record"],
          ["What actually happened", f"The shelf was empty for {round(EP['empty_open_hours'])} open hours.", "reality"]],
         "A synthetic, seeded world with an answer key. kvinayakpai.github.io/domain-series")
END = ("Why Domain Matters", "Sales are not demand.",
       [["And book stock is", "a belief, not the shelf.", "reality"]],
       "The SQL, the models and a notebook: kvinayakpai.github.io/domain-series/retail/technical")
WHY = "retailDemo.select('assistant'); retailDemo.ask('why')"


def short_scenes() -> list[dict]:
    o = OPT["hourly, 1 in 1,000"]
    return [
        {"card": TITLE, "dur": 4.5, "srt": f"The record says: 5 kg atta sales down {FALL}% week on week. What actually happened: the shelf was empty for {round(EP['empty_open_hours'])} open hours."},
        {"go": "demo/", "to": "#retail", "dur": 6.0,
         "cap": "A supermarket in Bengaluru, June 2026. A synthetic world with an answer key, read the way a data team reads it."},
        {"js": "retailDemo.select('dashboard')", "to": "#persona-panel", "off": 60, "dur": 7.0,
         "cap": f"Monday’s dashboard: 5 kg atta sales down {FALL}%, availability {pct(OSA['system_in_stock'])}. {PASSED} of 12 data tests passed."},
        {"js": WHY, "to": ".run", "off": 60, "dur": 7.0,
         "cap": "Asked why, the AI assistant, given the warehouse schema, blames shoppers switching to other packs."},
        {"js": "retailDemo.select('truth')", "to": "#persona-panel .story", "off": 60, "dur": 7.5,
         "cap": f"What happened: {D['story']['misplaced']['cases']} cases behind the rice. The shelf was empty {round(EP['empty_open_hours'])} open hours while the books showed {EP['book_on_hand_max']}."},
        {"js": "retailDemo.select('detector')", "to": "table.hours tbody tr:nth-child(8)", "off": 120, "dur": 7.5,
         "cap": f"A gap detector on the till lines flags the silence at {FLAG['flag_ts'][11:16]} on Wednesday, three open hours in. {o['true']} of its {o['flags']} alerts were real."},
        {"js": "retailDemo.set('forecast','unconstrained'); retailDemo.select('forecast')", "to": "#persona-panel .tiles", "off": 60, "dur": 7.0,
         "cap": f"Unconstrain demand and the forecast holds: {HERO['month_end']['aware']} bags a day, not {HERO['month_end']['naive']}. Shoppers came for {HERO['month_end']['true_june_mean']}."},
        {"js": "retailDemo.set('grounding','domain'); " + WHY, "to": ".run", "off": 60, "dur": 7.0,
         "cap": f"Give the assistant a domain layer: {SCORE['domain']} of {SCORE['of']} answers right, not {SCORE['naive']}. It finds the empty shelf."},
        {"js": "retailDemo.set('detect','gap')", "to": "[data-outcome]", "off": 150, "dur": 6.5,
         "cap": f"Rerun June with a shelf check at each alert: {GAP['kpis']['lost_units']} bags lost instead of {ASIS['kpis']['lost_units']}."},
        {"card": END, "dur": 5.0, "srt": "Sales are not demand. And book stock is a belief, not the shelf."},
    ]


def walkthrough_scenes() -> list[dict]:
    o1, o100 = OPT["hourly, 1 in 1,000"], OPT["hourly, 1 in 100"]
    return [
        {"card": TITLE, "dur": 5.0, "srt": f"Why Domain Matters, part 1: Retail and grocery. 5 kg atta sales fell {FALL}% in a week; the shelf was empty for {round(EP['empty_open_hours'])} open hours."},
        {"go": "", "to": "table.audit", "off": 140, "dur": 6.5,
         "cap": "Each post takes one failure, shows what the data made of it, and scores it against what really happened."},
        {"go": "retail/", "to": "#monday-9-am-the-weekly-review", "off": 24, "dur": 7.5,
         "cap": f"Monday’s review: sales down {FALL}%. The AI assistant, given the warehouse schema, blames shoppers switching packs."},
        {"to": "table.tests", "off": 60, "dur": 7.0,
         "cap": f"{PASSED} of 12 data tests pass. Four tests about how a store works all fail, on the same records."},
        {"to": "#what-actually-happened", "off": 24, "dur": 7.5,
         "cap": f"What happened: the cases sat behind the rice for {round(EP['empty_open_hours'])} open hours. The books never fell to the reorder point."},
        {"go": "demo/", "to": "#retail .controls", "off": 30, "dur": 7.0,
         "cap": "The demo: change what the data team does with June’s records, or rerun June with the store acting on what it finds."},
        {"js": "retailDemo.select('detector')", "to": "table.hours tbody tr:nth-child(8)", "off": 160, "dur": 8.0,
         "cap": f"The gap detector, hour by hour: blue hours are censored, yellow is the answer key’s empty shelf. It flags 5 kg atta at {FLAG['flag_ts'][11:16]} on Wednesday."},
        {"js": "retailDemo.alpha('0.01'); retailDemo.item('OIL-SUN-1L')", "to": "table.alerts", "off": 120, "dur": 7.5,
         "cap": f"At 1 in 100 it finds {o100['caught']} of {o100['gaps']} gaps, but only {o100['true']} of {o100['flags']} alerts are real. At 1 in 1,000: {o1['caught']} gaps, {o1['true']} of {o1['flags']}. The threshold is a business decision."},
        {"js": "retailDemo.alpha('0.001'); retailDemo.item('ATTA-WW-5KG'); retailDemo.set('forecast','unconstrained'); retailDemo.select('forecast')",
         "to": "#persona-panel .tiles", "off": 60, "dur": 8.0,
         "cap": f"Unconstrained, the forecast holds at {HERO['month_end']['aware']} bags a day. Scored on recorded sales it looks worse: {signed(HERO['aware_vs_recorded']['bias'])} against {signed(HERO['naive_vs_recorded']['bias'])}."},
        {"js": "retailDemo.set('grounding','domain'); " + WHY, "to": ".run", "off": 60, "dur": 8.0,
         "cap": f"With a domain layer the assistant answers {SCORE['domain']} of {SCORE['of']}, and finds the silence, the audit that saw the empty bay, and no delivery."},
        {"js": "retailDemo.set('detect','gap'); retailDemo.select('truth')", "to": "#persona-panel .story", "off": 60, "dur": 7.5,
         "cap": f"Rerun June with a check at every alert: the gap ends the same evening, and {GAP['kpis']['lost_units']} bags are lost instead of {ASIS['kpis']['lost_units']}."},
        {"js": "retailDemo.set('detect','off')", "to": "table.four-ways", "off": 120, "dur": 7.0,
         "cap": f"One name, five numbers: availability of {pct(AVAIL['on_the_books'])}, {pct(AVAIL['shelf_audits'])} or {pct(AVAIL['books_and_tills'])} from the records; {pct(AVAIL['true_open_hours'])} or {pct(AVAIL['true_demand_served'])} from the answer key."},
        {"js": "retailDemo.set('routine','scanned')", "to": "[data-outcome]", "off": 150, "dur": 6.5,
         "cap": f"Or capture the missing event: scan every case into a backroom bin, and {BINS['kpis']['lost_units']} bag is lost instead of {ASIS['kpis']['lost_units']}."},
        {"go": "retail/technical/", "to": "#finding-the-censored-hours", "off": 24, "dur": 7.0,
         "cap": "The technical companion: the tests in SQL, the detector and the forecast in Python, every query the assistant ran, and a notebook."},
        {"go": "retail/", "to": "#for-data-and-ai-leaders-five-questions-to-ask-your-team", "off": 24, "dur": 7.0,
         "cap": "For data and AI leaders: five questions to ask your team."},
        {"card": END, "dur": 5.5, "srt": "Sales are not demand. And book stock is a belief, not the shelf."},
    ]


L_TITLE = ("Why Domain Matters, part 2", "Logistics and supply chain",
           [["The record says", "Delivered on time, in full.", "record"],
            ["What actually happened", "One pallet line held the wrong pack size.", "reality"]],
           "A synthetic, seeded world. kvinayakpai.github.io/domain-series")
L_END = ("Why Domain Matters", "Every record agreed.",
         [["That is exactly why", "nobody checked the pallet.", "reality"]],
         "Run the scenarios and download the records: kvinayakpai.github.io/domain-series")


def logistics_short_scenes() -> list[dict]:
    line = LST["line"]
    return [
        {"card": L_TITLE, "dur": 4.5, "srt": "The record says: delivered on time, in full. What actually happened: one pallet line held the wrong pack size."},
        {"go": "demo/", "to": "#logistics", "dur": 6.0,
         "cap": "Monday 22 June, 6:12 am. The warehouse truck reaches Store 014 inside its 06:00–06:30 slot."},
        {"js": "logisticsDemo.select('dc')", "to": "#logistics .tabs", "off": 8, "dur": 7.0,
         "cap": f"At 03:00 the picker scanned the 5 kg slot’s label, then took {line['cases']} bales from the slot next door: 1 kg packs."},
        {"js": "logisticsDemo.select('transport')", "to": "#logistics .tabs", "off": 8, "dur": 6.0,
         "cap": "The trip log: left at 04:30, arrived at 06:12. On time."},
        {"js": "logisticsDemo.select('receiving')", "to": "#logistics .tabs", "off": 8, "dur": 7.0,
         "cap": f"The clerk scans the pallet label and the notice matches. {line['units']} bags of 5 kg are booked. They do not exist."},
        {"js": "logisticsDemo.select('scorecard')", "to": "#logistics .tabs", "off": 8, "dur": 6.5,
         "cap": f"The OTIF scorecard: {pct(LK['otif']['scorecard'])} for June. The 22 June delivery counts as perfect."},
        {"js": "logisticsDemo.select('stock')", "to": "#logistics .tabs", "off": 8, "dur": 7.0,
         "cap": f"Friday’s count: 5 kg {LFIVE['adjustment']:+d} bags, 1 kg {LONE['adjustment']:+d} packs. Theft? Sloppy counting?".replace("-", "−")},
        {"js": "logisticsDemo.select('truth')", "to": "#lg-panel h4", "off": 40, "dur": 7.5,
         "cap": f"What actually happened: the 5 kg shelf stood empty for {LEP['empty_open_hours']} open hours while the books showed {LEP['book_on_hand_max']}."},
        {"js": "logisticsDemo.select('truth')", "to": "#lg-panel table.ledger", "off": 90, "dur": 7.0,
         "cap": f"Four corrections in two buildings, one mis-pick. Across the company they net to {inr(LST['adjustments_net']['value_at_cost_inr'])}."},
        {"js": "logisticsDemo.set('dc','check_weigh'); logisticsDemo.select('scorecard')", "to": "#logistics [data-outcome]", "off": 240, "dur": 7.0,
         "cap": f"Weigh every pallet: the mistake is caught at dispatch. The shelf stays full, and OTIF falls to {pct(LWEIGH['kpis']['otif']['scorecard'])}."},
        {"card": L_END, "dur": 5.0, "srt": "Every record agreed. That is exactly why nobody checked the pallet."},
    ]


def logistics_walkthrough_scenes() -> list[dict]:
    k = LK["otif"]
    return [
        {"card": L_TITLE, "dur": 5.0, "srt": "Why Domain Matters, part 2: Logistics and supply chain. The record says delivered on time, in full; one pallet line held the wrong pack size."},
        {"go": "", "to": "table.audit", "off": 140, "dur": 6.0,
         "cap": "Part 2 follows one delivery through the people who see it differently."},
        {"go": "logistics/", "to": "article", "off": 90, "dur": 7.0,
         "cap": "The same synthetic world: Store 014 in Jayanagar, and the warehouse in Hoskote that supplies it."},
        {"to": "table.docs", "off": 60, "dur": 8.0,
         "cap": f"Every record of line 1 says 5 kg. The pallet held {LST['actual']['units_actual']} packs of 1 kg. The scan confirmed the slot, not the item."},
        {"to": "figure.figure:has(svg)", "off": 60, "dur": 7.0,
         "cap": f"The books said {LEP['book_on_hand_max']}. The shelf was empty for {LEP['empty_open_hours']} open hours, and nothing was reordered."},
        {"to": "table.ledger", "off": 80, "dur": 7.0,
         "cap": f"Four corrections, two buildings, one mistake. They net to about {inr(LST['adjustments_net']['value_at_cost_inr'])}, so nobody chases them."},
        {"to": "table.four-ways", "off": 120, "dur": 7.0,
         "cap": f"OTIF for June: {pct(k['dc_report'])}, {pct(k['by_line'])}, {pct(k['scorecard'])} or {pct(k['at_the_shelf'])}, depending on whose record decides."},
        {"go": "demo/", "to": "#logistics .controls", "off": 30, "dur": 7.0,
         "cap": "The demo replays June with the same customers and trucks. Change how the warehouse checks, or how the store receives."},
        {"js": "logisticsDemo.select('dc')", "to": "#lg-panel", "off": 70, "dur": 7.0,
         "cap": "The DC shift supervisor sees every line confirmed, and two count variances, both corrected."},
        {"js": "logisticsDemo.select('receiving')", "to": "#lg-panel", "off": 70, "dur": 6.0,
         "cap": "The receiving clerk sees pallet labels that matched the notice. No discrepancies."},
        {"js": "logisticsDemo.select('scorecard')", "to": "#lg-panel", "off": 70, "dur": 7.0,
         "cap": f"The scorecard sees {pct(k['scorecard'])} for June, with 22 June on time and in full."},
        {"js": "logisticsDemo.select('stock')", "to": "#lg-panel", "off": 70, "dur": 7.0,
         "cap": f"The stock controller sees {abs(LFIVE['adjustment'])} bags of 5 kg gone and {LONE['adjustment']} packs of 1 kg from nowhere."},
        {"js": "logisticsDemo.select('truth')", "to": "#lg-panel", "off": 70, "dur": 8.0,
         "cap": f"What actually happened: one mis-pick, {LEP['empty_open_hours']} open hours with an empty shelf, {LEP['lost_units']} bags not sold."},
        {"js": "logisticsDemo.set('dc','pick_scan')", "to": "#logistics [data-outcome]", "off": 200, "dur": 7.0,
         "cap": f"Scan every case at pick: the mistake never happens. OTIF stays {pct(LPICK['kpis']['otif']['scorecard'])}, and now it is true."},
        {"js": "logisticsDemo.set('dc','check_weigh')", "to": "#logistics [data-outcome]", "off": 200, "dur": 7.0,
         "cap": f"Weigh every pallet: caught at dispatch, the truck arrives late. OTIF falls to {pct(LWEIGH['kpis']['otif']['scorecard'])}; the shelf stays full."},
        {"js": "logisticsDemo.set('dc','none'); logisticsDemo.set('receiving','case_scan')", "to": "#logistics [data-outcome]", "off": 200, "dur": 7.0,
         "cap": f"Scan every case at the store: caught on arrival. OTIF falls to {pct(LCASE['kpis']['otif']['scorecard'])} again, because it now counts what arrived."},
        {"js": "logisticsDemo.set('receiving','label'); const d = document.querySelector('#logistics .drawer'); d.open = true; d.querySelector('[data-rec=notice]').click(); d.querySelector('input[name=lg-reveal]').click()",
         "to": "#logistics .drawer", "off": 20, "dur": 8.0,
         "cap": "The records behind it. Nothing says “wrong item”. Download them and find the line yourself."},
        {"go": "logistics/", "to": "#how-to-learn-this-domain", "off": 30, "dur": 7.0,
         "cap": "The post ends with a learning path: warehouse science, GS1 identifiers, India’s e-way bill, and practice on June’s records."},
        {"card": L_END, "dur": 5.5, "srt": "Every record agreed. That is exactly why nobody checked the pallet."},
    ]


P_TITLE = ("Why Domain Matters, part 3", "Payments",
           [["The record says", "Payment failed.", "record"],
            ["What actually happened", "The customer’s account was debited.", "reality"]],
           "A synthetic, seeded world. kvinayakpai.github.io/domain-series")
P_END = ("Why Domain Matters", "Every record was right about what it saw.",
         [["Only the customer", "saw both debits.", "reality"]],
         "Run the scenarios and download the records: kvinayakpai.github.io/domain-series")


def _secs(a: str, b: str) -> int:
    from datetime import datetime
    return round((datetime.fromisoformat(b[:19]) - datetime.fromisoformat(a[:19])).total_seconds())


def _ops() -> str:
    return f"{pct(PHOURS[18]['approved_at_till'] / PHOURS[18]['upi_attempts'])} and {pct(PHOURS[19]['approved_at_till'] / PHOURS[19]['upi_attempts'])}"


def payments_short_scenes() -> list[dict]:
    sc = PST["scene"]
    late = _secs(sc["attempts"][0]["ts"], sc["credited_ts"])
    days = round(_secs(sc["attempts"][0]["ts"], sc["refunded_ts"]) / 86400)
    fw = PSLOW["four_ways"]
    unmatched = PDAY["2026-06-20"]["unmatched"] + PDAY["2026-06-21"]["unmatched"]
    twice = sum(1 for c in PA["complaints"] if c["kind"] == "charged twice")
    refunds = sum(f["amount_inr"] for f in PA["refunds"])
    return [
        {"card": P_TITLE, "dur": 4.5, "srt": "The record says: payment failed. What actually happened: the customer’s account was debited."},
        {"go": "demo/", "to": "#payments", "dur": 6.0,
         "cap": "Saturday 20 June, 6:48 pm. The bank behind Store 014’s tills is slow to answer UPI payments."},
        {"js": "paymentsDemo.select('cashier')", "to": "#payments .tabs", "off": 8, "dur": 7.0,
         "cap": "The till waits 30 seconds, hears nothing, and shows “failed: no response”. The cashier asks for another way to pay."},
        {"js": "paymentsDemo.select('ops')", "to": "#payments .tabs", "off": 8, "dur": 6.5,
         "cap": f"Payments operations sees approvals fall to {_ops()} for two hours, then recover. Incident closed."},
        {"js": "paymentsDemo.select('recon')", "to": "#payments .tabs", "off": 8, "dur": 7.0,
         "cap": f"Reconciliation finds {unmatched} UPI credits with no approved payment at the till, and parks them in suspense."},
        {"js": "paymentsDemo.select('support')", "to": "#payments .tabs", "off": 8, "dur": 6.5,
         "cap": f"Customer support takes {len(PA['complaints'])} payment complaints in June. {twice} say “I was charged twice”."},
        {"js": "paymentsDemo.select('finance')", "to": "#payments .tabs", "off": 8, "dur": 6.5,
         "cap": f"Finance sees no UPI fees in June and {inr(refunds)} of refunds. Nothing looks wrong."},
        {"js": "paymentsDemo.select('truth')", "to": "#py-panel .story", "off": 60, "dur": 7.5,
         "cap": f"What actually happened: her bank had taken the money. The credit came {late} seconds later. She paid twice, and waited {days} days."},
        {"js": "paymentsDemo.select('truth')", "to": "#py-panel table.four-ways", "off": 90, "dur": 7.0,
         "cap": f"Payment success in those 90 minutes: {pct(fw['till'])} at the till, {pct(fw['bank'])} at the bank, {pct(fw['bills_paid'])} of bills paid. {pct(fw['charged_once'])} charged once."},
        {"js": "paymentsDemo.set('recon','bill_ref'); paymentsDemo.select('recon')", "to": "#payments [data-outcome]", "off": 250, "dur": 7.0,
         "cap": f"Put the bill ID on every UPI request: each double charge is found the next morning. Median refund: {PA['kpis']['refunds']['median_days_to_refund']} days → {PREF['kpis']['refunds']['median_days_to_refund']}."},
        {"card": P_END, "dur": 5.0, "srt": "Every record was right about what it saw. Only the customer saw both debits."},
    ]


def payments_walkthrough_scenes() -> list[dict]:
    sc = PST["scene"]
    late = _secs(sc["attempts"][0]["ts"], sc["credited_ts"])
    fw = PSLOW["four_ways"]
    unmatched = PDAY["2026-06-20"]["unmatched"] + PDAY["2026-06-21"]["unmatched"]
    twice = sum(1 for c in PA["complaints"] if c["kind"] == "charged twice")
    gap = sum(PHOURS[h]["credited"] - PHOURS[h]["approved_at_till"] for h in (18, 19))
    a, c, b = PA["kpis"], PCHECK["kpis"], PREF["kpis"]
    return [
        {"card": P_TITLE, "dur": 5.0, "srt": "Why Domain Matters, part 3: Payments. The record says payment failed; the customer’s account was debited."},
        {"go": "", "to": "table.audit", "off": 140, "dur": 6.0,
         "cap": "Part 3 follows one evening’s payments through the people who see them differently."},
        {"go": "payments/", "to": "article", "off": 90, "dur": 7.0,
         "cap": f"The same synthetic world: Store 014 in Jayanagar, now with every one of its {PJUNE['bills']:,} June bills paid at the tills."},
        {"to": "table.docs", "off": 60, "dur": 8.0,
         "cap": f"One basket in every record that holds it. The till says the UPI payment failed; the provider’s report says success, {late} seconds later."},
        {"to": "figure.figure:has(svg)", "off": 60, "dur": 7.0,
         "cap": f"In the 18:00 and 19:00 hours the bank credited {gap} UPI payments that the tills had marked failed."},
        {"to": "table.pay-ways", "off": 120, "dur": 7.0,
         "cap": f"Payment success four ways: {pct(fw['till'])} at the till, {pct(fw['bank'])} at the bank, {pct(fw['bills_paid'])} of bills paid, {pct(fw['charged_once'])} of customers charged once."},
        {"go": "demo/", "to": "#payments .controls", "off": 30, "dur": 7.0,
         "cap": "The demo replays June with the same customers, baskets and banks. Change what the till does, or how the back office matches."},
        {"js": "paymentsDemo.select('cashier')", "to": "#py-panel", "off": 70, "dur": 7.0,
         "cap": f"The tills give up on {PSLOW['upi_timeouts']} UPI payments in 90 minutes. Each time, the cashier asks for another way to pay."},
        {"js": "paymentsDemo.select('ops')", "to": "#py-panel", "off": 70, "dur": 6.0,
         "cap": f"Payments operations sees approvals at {_ops()} for two hours, normal by eight. Incident closed."},
        {"js": "paymentsDemo.select('recon')", "to": "#py-panel", "off": 70, "dur": 7.0,
         "cap": f"Reconciliation sees {unmatched} credits with no approved payment behind them. They sit in suspense until someone calls."},
        {"js": "paymentsDemo.select('support')", "to": "#py-panel", "off": 70, "dur": 6.0,
         "cap": f"Support takes {twice} calls from customers charged twice: a screenshot, a check, and about five days."},
        {"js": "paymentsDemo.select('truth')", "to": "#py-panel", "off": 70, "dur": 8.0,
         "cap": f"What actually happened: {PSLOW['charged_twice']} customers paid twice in 90 minutes, {PSLOW['extra_charges']} extra charges, {inr(PSLOW['charged_twice_inr'])} in all."},
        {"js": "paymentsDemo.set('till','check')", "to": "#payments [data-outcome]", "off": 200, "dur": 7.0,
         "cap": f"Wait for the status check at 90 seconds: double charges in June fall from {a['june']['charged_twice']} to {c['june']['charged_twice']}, and the tills spend {round(c['slowdown']['till_minutes'])} minutes taking payment, not {round(a['slowdown']['till_minutes'])}."},
        {"js": "paymentsDemo.set('till','retry'); paymentsDemo.set('recon','bill_ref')", "to": "#payments [data-outcome]", "off": 200, "dur": 7.0,
         "cap": f"Put the bill ID on every UPI request: double charges still happen, but the median refund falls from {a['refunds']['median_days_to_refund']} days to {b['refunds']['median_days_to_refund']}."},
        {"js": "paymentsDemo.set('recon','manual'); const d = document.querySelector('#payments .drawer'); d.open = true; d.querySelector('[data-rec=psp]').click(); d.querySelector('input[name=py-reveal]').click();"
               " const g = d.querySelector('[data-records] .gap'); const w = g.closest('.table-wrap');"
               " w.scrollTop += g.closest('tr').getBoundingClientRect().top - w.getBoundingClientRect().top - 72;",
         "to": "#payments .drawer", "off": 20, "dur": 8.0,
         "cap": "The records behind it. Nothing says “charged twice”. Download them and find the customers yourself."},
        {"go": "payments/", "to": "#how-to-learn-this-domain", "off": 30, "dur": 7.0,
         "cap": "The post ends with a learning path: how UPI moves money, RBI’s rules for failed payments, reconciliation, and practice on June’s records."},
        {"card": P_END, "dur": 5.5, "srt": "Every record was right about what it saw. Only the customer saw both debits."},
    ]


SHORT = {"viewport": {"width": 360, "height": 640}, "dsf": 3, "mobile": True, "fs": 19, "bottom": 52, "maxw": 340, "card_fs": 26}
WALK = {"viewport": {"width": 1280, "height": 720}, "dsf": 1.5, "mobile": False, "fs": 22, "bottom": 36, "maxw": 920, "card_fs": 44}
POSTS = {
    "retail": {"short": SHORT | {"scenes": short_scenes}, "walkthrough": WALK | {"scenes": walkthrough_scenes}},
    "logistics": {"short": SHORT | {"scenes": logistics_short_scenes}, "walkthrough": WALK | {"scenes": logistics_walkthrough_scenes}},
    "payments": {"short": SHORT | {"scenes": payments_short_scenes}, "walkthrough": WALK | {"scenes": payments_walkthrough_scenes}},
}


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def render(post: str, name: str, page: Page, work: Path) -> None:
    cfg = POSTS[post][name]
    sh = Shot(page, cfg["fs"], cfg["bottom"], cfg["maxw"], cfg["card_fs"])
    scenes = cfg["scenes"]()
    stills = []
    sh.goto("demo/")
    for i, sc in enumerate(scenes):
        sh.clear()
        if "go" in sc:
            sh.goto(sc["go"])
        if "js" in sc:
            sh.demo(sc["js"])
        if "to" in sc:
            sh.to(sc["to"], sc.get("off", 16))
        if "card" in sc:
            sh.card(*sc["card"])
        else:
            sh.caption(sc["cap"])
        path = work / f"{post}-{name}-{i:02d}.png"
        sh.snap(path)
        stills.append(path)
    durs = [sc["dur"] for sc in scenes]
    # ffmpeg: still images joined by crossfades.
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for p, d in zip(stills, durs):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.2f}", "-i", str(p)]
    cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    w = int(cfg["viewport"]["width"] * cfg["dsf"])
    h = int(cfg["viewport"]["height"] * cfg["dsf"])
    parts = [f"[{k}:v]scale={w}:{h},format=yuv420p,fps={FPS},settb=AVTB[s{k}]" for k in range(len(stills))]
    last, offset = "s0", 0.0
    for k in range(1, len(stills)):
        offset += durs[k - 1] - FADE
        parts.append(f"[{last}][s{k}]xfade=transition=fade:duration={FADE}:offset={offset:.2f}[x{k}]")
        last = f"x{k}"
    total = sum(durs) - FADE * (len(durs) - 1)
    out = OUT / f"{post}-{name}.mp4"
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{last}]", "-map", f"{len(stills)}:a",
            "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "48k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    # Captions as SRT, for platforms that take a caption file.
    lines, t = [], 0.0
    for k, sc in enumerate(scenes):
        start = t
        end = t + durs[k] - (FADE if k < len(scenes) - 1 else 0)
        lines += [str(k + 1), f"{srt_time(start)} --> {srt_time(end)}", sc.get("cap") or sc.get("srt", ""), ""]
        t += durs[k] - FADE
    (OUT / f"{post}-{name}.srt").write_text("\n".join(lines))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(stills[0]), "-q:v", "3",
                    str(OUT / f"{post}-{name}-poster.jpg")], check=True)
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB, {total:.1f} s, {len(stills)} scenes)")


def main() -> None:
    args = sys.argv[1:]
    posts = [a for a in args if a in POSTS] or list(POSTS)
    names = [a for a in args if a in ("short", "walkthrough")] or ["short", "walkthrough"]
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found")
    OUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(["node", "node_modules/astro/astro.js", "preview", "--port", str(PORT), "--host", "127.0.0.1"],
                              cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen(BASE, timeout=1)
                break
            except OSError:
                time.sleep(0.5)
        with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
            browser = p.chromium.launch()
            for post in posts:
                for name in names:
                    cfg = POSTS[post][name]
                    ctx = browser.new_context(viewport=cfg["viewport"], device_scale_factor=cfg["dsf"],
                                              is_mobile=cfg["mobile"], has_touch=cfg["mobile"], color_scheme="light",
                                              reduced_motion="reduce")
                    render(post, name, ctx.new_page(), Path(tmp))
                    ctx.close()
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    main()
