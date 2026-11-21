"""Take secrets out of the files a run commits.

Removes the run's throwaway passwords (SCRUB, separated by |), the NVIDIA key
(NVIDIA_API_KEY), anything shaped like an NVIDIA key, Bearer tokens and
key/token/password assignments from every text file
under a folder, in place.

    python3 auto-ontology-demo/scrub.py <folder>

Standard library only.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

NVIDIA_KEY_SHAPE = re.compile(r"nvapi-[A-Za-z0-9_\-]{8,}")
# Authorization headers and key/token/password assignments, in logs, tracebacks and JSON.
BEARER = re.compile(r"(?i)(Bearer\s+)[A-Za-z0-9\-._~+/]+=*")
ASSIGNED = re.compile(
    r"""(?i)(["']?(?:api[_-]?key|secret|token|password)["']?\s*[:=]\s*["']?)[A-Za-z0-9_\-.]{12,}(["']?)"""
)


def secrets() -> list[str]:
    found = [s for s in os.environ.get("SCRUB", "").split("|") if s]
    found.append(os.environ.get("NVIDIA_API_KEY", ""))
    return [s for s in found if len(s) >= 8]


def clean(text: str) -> str:
    for secret in secrets():
        text = text.replace(secret, "[redacted]")
    text = NVIDIA_KEY_SHAPE.sub("[redacted]", text)
    text = BEARER.sub(r"\1[redacted]", text)
    return ASSIGNED.sub(r"\1[redacted]\2", text)


def clean_tree(root: str | Path) -> int:
    changed = 0
    for path in Path(root).rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):  # binary files, such as the Ossie zip
            continue
        cleaned = clean(text)
        if cleaned != text:
            path.write_text(cleaned)
            changed += 1
    return changed


if __name__ == "__main__":
    print("scrubbed", clean_tree(sys.argv[1] if len(sys.argv) > 1 else "."), "files")
