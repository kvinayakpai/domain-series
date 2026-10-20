"""Regenerate the decks from the world data, lint them against the slide format, and check their layout.

    python3 scripts/decks/build.py          # regenerate, lint and check every deck
    python3 scripts/decks/build.py --pdf    # also print public/media/<post>-slides.pdf

Each deck's source is decks/<post>/project: the Slides artifact's own files (deck.json and one
HTML file per slide, speaker notes included). Every deck is generated from src/data/*.json by
make_<post>.py, so its numbers follow the world and the analysis. After a change, publish the
changed files to the deck's Slides artifact.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "scripts" / "decks"
POSTS = ["retail", "logistics", "payments"]
GENERATED = ["retail", "logistics", "payments"]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> None:
    for post in GENERATED:
        run(str(HERE / f"make_{post}.py"))
    run(str(HERE / "lint.py"), *[str(ROOT / "decks" / p / "project") for p in POSTS])
    for post in POSTS:
        args = [str(HERE / "render.py"), str(ROOT / "decks" / post / "project")]
        if "--pdf" in sys.argv:
            args += ["--pdf", str(ROOT / "public" / "media" / f"{post}-slides.pdf")]
        run(*args)


if __name__ == "__main__":
    main()
