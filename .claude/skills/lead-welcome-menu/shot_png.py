#!/usr/bin/env python3
"""Render each screen to PNG so the deck is judged from pixels, never from source.
Writes full-size 1080x1920 PNGs plus 390px-wide phone-scale versions — the 0.361x
collapse is the whole point, so the phone-scale ones are the ones to look at."""
import re, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

D = Path(__file__).parent
OUT = D / "shots"; OUT.mkdir(exist_ok=True)
CANDIDATES = ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
              "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"]

def chromium():
    for c in CANDIDATES:
        if Path(c).is_file(): return c
    for n in ("chromium","chromium-browser","google-chrome"):
        if shutil.which(n): return shutil.which(n)
    raise SystemExit("no chromium binary found")

html = (D / "lead-menu.html").read_text()
head, body = html.split("<body>", 1)
screens = re.findall(r'<section class="screen.*?</section>', body, re.S)
assert len(screens) == 15, f"expected 15 screens, found {len(screens)}"

binary = chromium()
only = [int(a) for a in sys.argv[1:]] or range(1, 16)
for i, sc in enumerate(screens, 1):
    if i not in only: continue
    tmp = D / f".screen{i:02d}.html"
    tmp.write_text(head + "<style>html,body{margin:0;padding:0;width:1080px;height:1920px;"
                   "}</style><body>" + sc + "</body></html>", encoding="utf-8")
    png = OUT / f"s{i:02d}.png"
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([binary, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--virtual-time-budget=5000", f"--user-data-dir={prof}",
                        "--window-size=1080,2200", f"--screenshot={png}", tmp.as_uri()],
                       capture_output=True, timeout=180)
    tmp.unlink()
    # Render taller than the page and crop: when the viewport equals the content
    # height Chromium fits the page to it and every measurement comes back ~4.5% short.
    im = Image.open(png); im.load()
    im = im.crop((0, 0, 1080, 1920)); im.save(png)
    im.resize((390, 693), Image.LANCZOS).save(OUT / f"phone{i:02d}.png")
    print(f"s{i:02d} {im.size} -> phone 390x693")
