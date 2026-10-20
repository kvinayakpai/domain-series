"""Render the captioned retail videos from the built site.

Each scene is a crisp still of the real site (demo or post) with its caption burned in,
joined with short crossfades. Captions read their numbers from src/data/retail.json, so
the videos cannot drift from the world. Captions only: no narration.

    npm run build
    python3 scripts/video/render.py            # both videos
    python3 scripts/video/render.py short      # 1080x1920, about 70 s
    python3 scripts/video/render.py walkthrough  # 1920x1080, about 2 min

Writes public/media/retail-<name>.mp4, .srt and -poster.jpg. Needs Playwright (Python)
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
S = {s["key"]: s for s in D["scenarios"]}
ASIS, ALERT, BINS = S["off|today"], S["1d|today"], S["off|scanned"]
EP = D["story"]["episode"]
W = D["story"]["kpis"]["weekly"]
REC5 = W["recorded_sales"]["ATTA-WW-5KG"]
SHARE = [REC5[k] / (REC5[k] + W["recorded_sales"]["ATTA-WW-1KG"][k] + W["recorded_sales"]["ATTA-WW-10KG"][k]) for k in range(4)]
OSA = ASIS["kpis"]["osa"]
MILK = {m["factor"]: m for m in D["milk"]}


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
         [["The record says", "On hand: 55 bags. No reorder needed.", "record"],
          ["What actually happened", "The shelf has been empty since Wednesday.", "reality"]],
         "A synthetic, seeded world. kvinayakpai.github.io/domain-series")
END = ("Why Domain Matters", "Every system keeps a record.",
       [["Domain knowledge is", "knowing when the record is wrong.", "reality"]],
       "Run the scenarios and download the records: kvinayakpai.github.io/domain-series")


def short_scenes() -> list[dict]:
    return [
        {"card": TITLE, "dur": 4.5, "srt": "The record says: on hand, 55 bags, no reorder needed. What actually happened: the shelf has been empty since Wednesday."},
        {"go": "demo/", "to": "#retail", "dur": 6.0,
         "cap": "A supermarket in Bengaluru, June 2026. A synthetic world, calibrated against studies of real stores."},
        {"go": "demo/", "js": "retailDemo.select('store')", "to": ".tabs", "off": 8, "dur": 7.0,
         "cap": f"Thursday, 7:40 pm. The 5 kg atta shelf has been empty since Wednesday afternoon. The handheld says {EP['book_on_hand_min']}."},
        {"js": "retailDemo.select('system')", "to": ".tabs", "off": 8, "dur": 7.0,
         "cap": f"Every night the reorder system sees {EP['book_on_hand_min']} bags, above its reorder point of {EP['reorder_point'][-1]}. It orders nothing."},
        {"js": "retailDemo.select('planner')", "to": ".tabs", "off": 8, "dur": 6.5,
         "cap": f"The demand planner sees sales fall {round((1 - REC5[1] / REC5[0]) * 100)}% in a week, and trims the forecast."},
        {"js": "retailDemo.select('category')", "to": ".tabs", "off": 8, "dur": 6.0,
         "cap": f"The category manager sees 5 kg’s share of atta fall from {pct(SHARE[0])} to {pct(SHARE[1])}."},
        {"js": "retailDemo.select('truth')", "to": ".tabs", "off": 8, "dur": 7.5,
         "cap": f"What actually happened: {D['story']['misplaced']['units']} bags were put away behind the rice. The books were right that the stock existed. Nobody could find it."},
        {"js": "retailDemo.select('truth')", "to": "#persona-panel h4", "off": 40, "dur": 7.0,
         "cap": f"{round(EP['empty_open_hours'])} open hours with an empty shelf. {EP['lost_units']} bags customers wanted and could not buy."},
        {"js": "retailDemo.select('truth')", "to": "table.four-ways", "off": 120, "dur": 7.0,
         "cap": f"Availability that month: {pct(OSA['system_in_stock'])}, {pct(OSA['shelf_audit'])}, {pct(OSA['open_hours_on_shelf'])} or {pct(OSA['demand_served'])}. It depends who you ask."},
        {"js": "retailDemo.set('routine','scanned'); retailDemo.select('store')", "to": "[data-outcome]", "off": 210, "dur": 7.0,
         "cap": f"Scan every case into a backroom bin, and June’s lost bags fall from {ASIS['kpis']['lost_units']} to {BINS['kpis']['lost_units']}."},
        {"card": END, "dur": 5.0, "srt": "Every system keeps a record. Domain knowledge is knowing when the record is wrong."},
    ]


def walkthrough_scenes() -> list[dict]:
    m1, m95 = MILK[1.0], MILK[0.95]
    return [
        {"card": TITLE, "dur": 5.0, "srt": "Why Domain Matters, part 1: Retail and grocery. The record says 55 bags on hand; the shelf has been empty since Wednesday."},
        {"go": "", "to": "table.audit", "off": 140, "dur": 7.0,
         "cap": "Each post takes one real failure and follows it through the people who see it differently."},
        {"go": "retail/", "to": "article", "off": 90, "dur": 7.0,
         "cap": "A fictional supermarket in Jayanagar, Bengaluru. Every number comes from a synthetic, seeded world."},
        {"go": "retail/", "to": "figure.figure", "off": 60, "dur": 8.0,
         "cap": "The cases sat behind the rice. The books never fell to the reorder point, so nothing was ordered."},
        {"to": "table.four-ways", "off": 160, "dur": 7.0,
         "cap": f"One name, four numbers: availability of {pct(OSA['system_in_stock'])}, {pct(OSA['shelf_audit'])}, {pct(OSA['open_hours_on_shelf'])} or {pct(OSA['demand_served'])}."},
        {"go": "demo/", "to": "#retail .controls", "off": 30, "dur": 7.0,
         "cap": "The demo runs the same month on the same customers. Change what the store does and every view updates."},
        {"js": "retailDemo.select('store')", "to": "#persona-panel", "off": 70, "dur": 7.0,
         "cap": "The store manager sees an empty bay, and a handheld that says 55."},
        {"js": "retailDemo.select('system')", "to": "#persona-panel", "off": 70, "dur": 7.0,
         "cap": "The reorder system sees 55 bags above its reorder point. In stock, no reorder needed, three nights running."},
        {"js": "retailDemo.select('planner')", "to": "#persona-panel", "off": 70, "dur": 7.0,
         "cap": f"The planner sees sales fall {round((1 - REC5[1] / REC5[0]) * 100)}%, and the forecast slides to {D['story']['forecast']['end_recorded_sales']} bags a day."},
        {"js": "retailDemo.select('supplier')", "to": "#persona-panel", "off": 70, "dur": 6.0,
         "cap": f"The supplier sees orders drop from {W['store_orders_units'][0]} to {W['store_orders_units'][1]} bags a week."},
        {"js": "retailDemo.select('truth')", "to": "#persona-panel", "off": 70, "dur": 8.0,
         "cap": f"What actually happened: {D['story']['misplaced']['cases']} cases behind the rice, {round(EP['empty_open_hours'])} open hours with an empty shelf, {EP['lost_units']} bags not sold."},
        {"js": "retailDemo.set('alert','1d')", "to": "[data-outcome]", "off": 180, "dur": 7.0,
         "cap": f"A low-sales alert, checked next morning: lost bags fall from {ASIS['kpis']['lost_units']} to {ALERT['kpis']['lost_units']}."},
        {"js": "retailDemo.set('alert','off'); retailDemo.set('routine','scanned')", "to": "[data-outcome]", "off": 180, "dur": 7.0,
         "cap": f"Scanned backroom bins prevent it: {ASIS['kpis']['lost_units']} lost bags become {BINS['kpis']['lost_units']}."},
        {"js": "retailDemo.set('routine','today'); document.querySelector('.drawer').open = true; document.querySelector('input[name=reveal]').click()",
         "to": ".drawer", "off": 20, "dur": 8.0,
         "cap": "The records behind it. Nothing says “misplaced”. Download them and find the gap yourself."},
        {"js": "retailDemo.milk(2)", "to": ".milk", "off": 20, "dur": 8.5,
         "cap": f"Milk carries the opposite risk. A 5% leaner order lifts milk’s margin from {inr(m1['net_inr'])} to {inr(m95['net_inr'])}, and {m95['lost'] - m1['lost']} more pouches go unfound."},
        {"go": "retail/", "to": "#how-to-learn-this-domain", "off": 30, "dur": 7.0,
         "cap": "Each post ends with a learning path: real books, real datasets, and practice on the store’s records."},
        {"card": END, "dur": 5.5, "srt": "Every system keeps a record. Domain knowledge is knowing when the record is wrong."},
    ]


VIDEOS = {
    "short": {"viewport": {"width": 360, "height": 640}, "dsf": 3, "mobile": True, "fs": 19, "bottom": 52, "maxw": 340, "card_fs": 26, "scenes": short_scenes},
    "walkthrough": {"viewport": {"width": 1280, "height": 720}, "dsf": 1.5, "mobile": False, "fs": 22, "bottom": 36, "maxw": 920, "card_fs": 44, "scenes": walkthrough_scenes},
}


def srt_time(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def render(name: str, page: Page, work: Path) -> None:
    cfg = VIDEOS[name]
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
        path = work / f"{name}-{i:02d}.png"
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
    out = OUT / f"retail-{name}.mp4"
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
    (OUT / f"retail-{name}.srt").write_text("\n".join(lines))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(stills[0]), "-q:v", "3",
                    str(OUT / f"retail-{name}-poster.jpg")], check=True)
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB, {total:.1f} s, {len(stills)} scenes)")


def main() -> None:
    names = sys.argv[1:] or list(VIDEOS)
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
            for name in names:
                cfg = VIDEOS[name]
                ctx = browser.new_context(viewport=cfg["viewport"], device_scale_factor=cfg["dsf"],
                                          is_mobile=cfg["mobile"], has_touch=cfg["mobile"], color_scheme="light",
                                          reduced_motion="reduce")
                render(name, ctx.new_page(), Path(tmp))
                ctx.close()
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    main()
