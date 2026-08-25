#!/usr/bin/env python3
"""
Render lead-menu.html to PDF with the bundled headless Chromium.

Usage:  python3 build.py && python3 shot.py
Output: lead-menu.pdf
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

D = Path(__file__).parent
SRC = D / "lead-menu.html"
OUT = D / "lead-menu.pdf"

CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
]


def chromium():
    for c in CANDIDATES:
        if Path(c).is_file():
            return c
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("no chromium binary found")


def main():
    if not SRC.is_file():
        raise SystemExit(f"{SRC} missing — run build.py first")

    binary = chromium()
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            binary,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=6000",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={OUT}",
            SRC.as_uri(),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if not OUT.is_file() or OUT.stat().st_size == 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"chromium did not produce a PDF (exit {r.returncode})")

    print(f"wrote {OUT}  ({OUT.stat().st_size:,} bytes)  via {binary}")


if __name__ == "__main__":
    main()
