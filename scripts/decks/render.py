"""Check each slide of a deck for overflow and, optionally, print the deck to PDF.

    python3 scripts/decks/render.py decks/payments/project
    python3 scripts/decks/render.py decks/payments/project --pdf public/media/payments-slides.pdf
    python3 scripts/decks/render.py decks/payments/project --png /tmp/slides

Slides are laid out as the Slides artifact lays them out: a 1920x1080 canvas, the deck's fonts
(from node_modules), tables ruled and padded the same way. A slide whose content runs past the
footer band, or whose text overflows its box, is reported and fails the run.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
NM = ROOT / "node_modules"


def font(p: str) -> str:
    return (NM / p).as_uri()


FONTS = f"""
@font-face{{font-family:'Anek Latin';font-weight:100 800;src:url({font('@fontsource-variable/anek-latin/files/anek-latin-latin-wght-normal.woff2')})}}
@font-face{{font-family:'Anek Latin';font-weight:100 800;unicode-range:U+0100-024F,U+20A0-20C0,U+2190-21FF;src:url({font('@fontsource-variable/anek-latin/files/anek-latin-latin-ext-wght-normal.woff2')})}}
@font-face{{font-family:'Literata';font-weight:200 900;src:url({font('@fontsource-variable/literata/files/literata-latin-wght-normal.woff2')})}}
@font-face{{font-family:'Literata';font-weight:200 900;unicode-range:U+0100-024F,U+20A0-20C0;src:url({font('@fontsource-variable/literata/files/literata-latin-ext-wght-normal.woff2')})}}
@font-face{{font-family:'Literata';font-style:italic;font-weight:400;src:url({font('@fontsource-variable/literata/files/literata-latin-wght-italic.woff2')})}}
@font-face{{font-family:'IBM Plex Mono';font-weight:400;src:url({font('@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2')})}}
@font-face{{font-family:'IBM Plex Mono';font-weight:500;src:url({font('@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2')})}}
"""
BASE = """*{margin:0;box-sizing:border-box}
h1{font-size:96px;font-weight:600;line-height:1.1} h2{font-size:64px;font-weight:600;line-height:1.15} h3{font-size:44px;line-height:1.2} p{font-size:32px;line-height:1.4}
table{border-collapse:collapse;width:100%} td,th{padding:0.35em 0.6em;border-bottom:1px solid #c9cec7;vertical-align:top} a{text-decoration:none}"""
CHECK = """() => {
  const s = document.querySelector('section');
  const footer = [...s.children].some(c => getComputedStyle(c).position === 'absolute' && c.tagName === 'P');
  const limit = footer ? 920 : 952; let maxB = 0;
  for (const c of s.children) { if (c.tagName === 'ASIDE') continue; if (getComputedStyle(c).position === 'absolute') continue;
    maxB = Math.max(maxB, c.getBoundingClientRect().bottom); }
  const over = [...s.querySelectorAll('p,h1,h2,h3,td,th')].filter(e => e.scrollWidth > e.clientWidth + 2).map(e => e.textContent.slice(0, 40));
  return { maxBottom: Math.round(maxB), limit, over };
}"""


def page(body: str, title: str = "", extra: str = "") -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{FONTS}{BASE}{extra}'
            f"aside{{display:none}}</style></head><body>{body}</body></html>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("deck", type=Path, help="a deck's project folder, holding deck.json and slides/")
    ap.add_argument("--pdf", type=Path, help="print the deck to this PDF")
    ap.add_argument("--png", type=Path, help="save each slide as <dir>/<slide id>.png")
    a = ap.parse_args()
    index = json.loads((a.deck / "deck.json").read_text())
    order = index["order"]
    bad = 0
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        one = "body{width:1920px;height:1080px;overflow:hidden} section{width:1920px;height:1080px;position:relative;overflow:hidden}"
        for sid in order:
            f = Path(tmp) / "slide.html"
            f.write_text(page((a.deck / "slides" / f"{sid}.html").read_text(), extra=one))
            pg.goto(f.as_uri())
            pg.evaluate("document.fonts.ready")
            if a.png:
                a.png.mkdir(parents=True, exist_ok=True)
                pg.screenshot(path=str(a.png / f"{sid}.png"))
            info = pg.evaluate(CHECK)
            flag = "OVER" if info["maxBottom"] > info["limit"] or info["over"] else "ok"
            bad += flag != "ok"
            print(f"{sid:12s} bottom {info['maxBottom']} / {info['limit']} {flag} {info['over'] or ''}")
        if a.pdf:
            sections = "".join((a.deck / "slides" / f"{s}.html").read_text() for s in order)
            f = Path(tmp) / "deck.html"
            f.write_text(page(sections, index["title"],
                              "@page{size:1920px 1080px;margin:0} section{width:1920px;height:1080px;position:relative;overflow:hidden;break-after:page}"))
            pg2 = b.new_page()
            pg2.goto(f.as_uri())
            pg2.evaluate("document.fonts.ready")
            a.pdf.parent.mkdir(parents=True, exist_ok=True)
            pg2.pdf(path=str(a.pdf), width="1920px", height="1080px", print_background=True)
            print(f"wrote {a.pdf} ({len(order)} pages)")
        b.close()
    print(f"{a.deck}: {bad} slide(s) with problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
