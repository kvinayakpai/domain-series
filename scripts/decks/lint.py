"""Flag styles a Slides deck drops: properties outside the slide subset for the element they sit on.

Usage: python3 scripts/decks/lint.py <deck project dir> [...]
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TEXT = {"h1", "h2", "h3", "p", "ul", "ol", "li"}
# Properties that apply only to some elements (from the type's format.md subset table).
ONLY = {
    "font-family": TEXT | {"table", "section", "div", "body"},
    "font-size": TEXT | {"table", "section", "div", "body"},
    "font-weight": TEXT | {"th", "span", "section", "div", "body"},
    "font-style": TEXT | {"span"},
    "line-height": TEXT | {"section", "div"},
    "letter-spacing": TEXT,
    "white-space": TEXT,
    "text-transform": TEXT,
    "background": {"section", "div", "img", "table", "tr", "x-icon", "x-shape", "hr"} | TEXT,
    "padding": {"section", "div", "table", "td", "th"} | TEXT,
    "border": {"div", "img", "table", "x-icon", "x-shape", "hr", "x-connector"} | TEXT,
    "border-radius": {"div", "img", "table", "x-shape"} | TEXT,
    "display": {"section", "div"},
    "gap": {"section", "div"},
    "text-align": TEXT | {"td", "th", "section", "div"},
    "color": TEXT | {"span", "td", "th", "x-icon", "x-connector", "hr", "section", "div", "table", "a"},
}
SPAN_OK = {"color", "font-weight", "-webkit-text-fill-color"}
UNSUPPORTED = {"margin", "z-index", "float"}


class Lint(HTMLParser):
    def __init__(self):
        super().__init__()
        self.problems = []
        self.stack = []
        self.in_svg = 0
        self.first_row = None
        self.table_padding = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "svg":
            self.in_svg += 1
        if self.in_svg:
            if tag == "text":
                self.problems.append("svg <text>: fonts never load in an svg; use <p> labels over it")
            return
        if "colspan" in a or "rowspan" in a:
            self.problems.append(f"<{tag}> colspan/rowspan: not supported")
        style = a.get("style") or ""
        props = {}
        for decl in style.split(";"):
            if ":" in decl:
                k, v = decl.split(":", 1)
                props[k.strip().lower()] = v.strip()
        for k, v in props.items():
            base = re.sub(r"-(top|right|bottom|left)$", "", k) if k.startswith(("padding", "border")) and k != "border-radius" else k
            if base in UNSUPPORTED:
                self.problems.append(f"<{tag}> {k}: not in the subset")
            if tag == "span" and k not in SPAN_OK:
                self.problems.append(f"<span> {k}: spans take color only")
                continue
            allowed = ONLY.get(base)
            if allowed is not None and tag not in allowed and tag != "span":
                self.problems.append(f"<{tag}> {k}: does not apply to {tag}")
            if base == "padding" and tag in ("td", "th"):
                if re.search(r"(^|\s)0(px)?(\s|$)", v):
                    self.problems.append(f"<{tag}> {k}: {v}: never a 0 padding on a cell")
                self.table_padding.append(v)
            if re.search(r"\d(em|rem|vw|vh)\b", v) and k != "letter-spacing":
                self.problems.append(f"<{tag}> {k}: {v}: px only")
        if tag == "table":
            self.first_row = "pending"
            self.table_padding = []
        if tag == "tr" and self.first_row == "pending":
            self.first_row = []
        elif tag == "tr" and isinstance(self.first_row, list):
            self.check_first_row()
        if tag in ("td", "th") and isinstance(self.first_row, list) and self.first_row is not None:
            self.first_row.append("width" in props)
        if tag in TEXT and "font-size" in props:
            m = re.match(r"(\d+)px", props["font-size"])
            if m and int(m.group(1)) < 24:
                self.problems.append(f"<{tag}> font-size {props['font-size']}: under 24px")

    def check_first_row(self):
        row = self.first_row
        self.first_row = None
        if row and any(row) and not all(row):
            self.problems.append("table: width on some first-row cells only (all equal columns)")
        if row and not any(row) and len(row) > 1:
            self.problems.append("table: no widths on the first row (equal columns)")

    def handle_endtag(self, tag):
        if tag == "svg":
            self.in_svg -= 1
        if tag == "table":
            if isinstance(self.first_row, list):
                self.check_first_row()
            if len(set(self.table_padding)) > 1:
                self.problems.append(f"table: {len(set(self.table_padding))} different cell paddings (one per table)")


bad = 0
for d in sys.argv[1:]:
    for f in sorted(Path(d, "slides").glob("*.html")):
        lint = Lint()
        lint.feed(f.read_text())
        probs = sorted(set(lint.problems))
        if probs:
            bad += 1
            print(f"{Path(d).parent.name}/{f.stem}:")
            for p in probs:
                print("   ", p)
print("slides with problems:", bad)
sys.exit(1 if bad else 0)
