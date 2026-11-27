"""Take secrets out of the files a run commits.

Removes the run's throwaway passwords (SCRUB, separated by |), the NVIDIA key
(NVIDIA_API_KEY), anything shaped like an NVIDIA key, Bearer tokens and
key/token/password assignments from every text file
under a folder (non-UTF-8 bytes are kept as they are), in place.

    python3 auto-ontology-demo/scrub.py <folder>

Standard library only.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

NVIDIA_KEY_SHAPE = re.compile(r"nvapi-[A-Za-z0-9_\-]{8,}")
GEMINI_KEY_SHAPE = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")
# Authorization headers and key/token/password assignments, in logs, tracebacks and JSON.
BEARER = re.compile(r"(?i)(Bearer\s+)[A-Za-z0-9\-._~+/]+=*")
ASSIGNED = re.compile(
    r"""(?i)(["']?(?:api[_-]?key|secret|token|password)["']?\s*[:=]\s*["']?)[A-Za-z0-9_\-.]{12,}(["']?)"""
)


def secrets() -> list[str]:
    found = [s for s in os.environ.get("SCRUB", "").split("|") if s]
    found.append(os.environ.get("NVIDIA_API_KEY", ""))
    found.append(os.environ.get("GEMINI_KEY", ""))
    return [s for s in found if len(s) >= 8]


def clean(text: str) -> str:
    for secret in secrets():
        text = text.replace(secret, "[redacted]")
    text = NVIDIA_KEY_SHAPE.sub("[redacted]", text)
    text = GEMINI_KEY_SHAPE.sub("[redacted]", text)
    text = BEARER.sub(r"\1[redacted]", text)
    return ASSIGNED.sub(r"\1[redacted]\2", text)


def clean_tree(root: str | Path) -> int:
    changed = 0
    for path in Path(root).rglob("*"):
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\0" in raw:  # binary files, such as the Ossie zip
            continue
        # surrogateescape keeps any non-UTF-8 byte as it was, so a log with a stray byte is still
        # scrubbed (it used to be skipped on UnicodeDecodeError) and is written back unchanged elsewhere.
        text = raw.decode("utf-8", errors="surrogateescape")
        cleaned = clean(text)
        if cleaned != text:
            path.write_bytes(cleaned.encode("utf-8", errors="surrogateescape"))
            changed += 1
    return changed


if __name__ == "__main__":
    print("scrubbed", clean_tree(sys.argv[1] if len(sys.argv) > 1 else "."), "files")
