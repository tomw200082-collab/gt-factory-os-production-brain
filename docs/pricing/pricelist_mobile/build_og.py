#!/usr/bin/env python3
"""Link-preview card and home-screen icons for the hosted pricelist.

The page will mostly be opened from a WhatsApp message, so the preview card is
the first thing a buyer sees of it — it is built from the same photograph,
palette and faces as the page rather than left to whatever a scraper picks.

Rendered through the bundled Chromium instead of drawn in PIL, because the card
sets Hebrew: the browser already does the bidi and shaping the fonts need.

Build:  python3 build_og.py   →  site/og.jpg, site/icon-180.png, site/icon-32.png
"""
import base64
import pathlib
import subprocess

from PIL import Image

import build_mobile as bm

HERE = pathlib.Path(__file__).parent
SITE = HERE / 'site'
NODE_PW = '/opt/node22/lib/node_modules/playwright/index.mjs'

# Half paper, half photograph, split by a hairline. A scrim over the whole frame
# turned the bottles to mud; giving the type its own clean ground keeps both the
# photograph and the Hebrew at full strength.
CARD = """<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
{faces}
body{{width:1200px;height:630px;display:grid;grid-template-columns:1fr 520px;
  background:{paper};font-family:'Heebo',sans-serif;color:{ink}}}
.t{{position:relative;padding:76px 76px 76px 60px;display:flex;flex-direction:column;
  align-items:flex-start;justify-content:center}}
.t>img{{width:96px}}
h1{{margin-top:30px;font-family:'Rubik',sans-serif;font-weight:700;font-size:70px;letter-spacing:-.012em}}
p{{margin-top:20px;font-size:24px;line-height:1.6;letter-spacing:.02em;color:{muted}}}
.tag{{margin-top:30px;background:{coral};color:{ink};font-family:'Rubik',sans-serif;
  font-weight:600;font-size:21px;letter-spacing:.08em;padding:13px 22px}}
.yr{{position:absolute;top:56px;right:76px;font-family:'Rubik',sans-serif;font-weight:600;
  font-size:20px;letter-spacing:.42em;opacity:.42}}
.ph{{position:relative;border-right:1px solid {rule}}}
.ph img{{width:100%;height:100%;object-fit:cover;object-position:50% 60%}}
</style></head><body>
<div class="t">
  <span class="yr">2026</span>
  <img src="{mark}" alt="">
  <h1>מחירון סיטונאי</h1>
  <p>תמציות תה · מאצ׳ה ואבקות<br>מחיות פרי · מוצרים משלימים</p>
  <span class="tag">כל המחירים ללא מע״מ</span>
</div>
<div class="ph"><img src="{cover}" alt=""></div>
</body></html>"""

SHOT = """
import {{ chromium }} from '%s';
const b = await chromium.launch();
const p = await b.newPage({{ viewport: {{ width: 1200, height: 630 }}, deviceScaleFactor: 1 }});
await p.goto('file://{card}', {{ waitUntil: 'load' }});
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(400);
await p.screenshot({{ path: '{out}' }});
await b.close();
""" % NODE_PW


def bottle_band():
    """The cover photograph is mostly studio wall; the card wants the labels.

    object-position bottoms out before the bottles fill the panel, so the crop
    is taken in advance rather than nudged in CSS."""
    import io
    im = Image.open(HERE / 'assets' / 'cover.jpg').convert('RGB')
    im = im.crop((0, int(im.height * 0.55), im.width, im.height))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=90)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def build():
    SITE.mkdir(exist_ok=True)
    # The card is rendered from a temp file next to this script, so its assets
    # have to travel inside it — force inline mode whatever the caller left set.
    mode, bm.MODE = bm.MODE, 'inline'
    ext, bm.FONT_EXT = bm.FONT_EXT, 'woff'
    html = CARD.format(
        faces=bm.font_faces(),                       # inline mode: faces carry their own bytes
        paper=bm.PAPER, ink=bm.INK, muted=bm.MUTED, coral=bm.CORAL, rule=bm.RULE,
        cover=bottle_band(), mark=bm.img('logo_ink.png'))
    card = HERE / '.og-card.html'
    png = HERE / '.og-card.png'
    bm.MODE, bm.FONT_EXT = mode, ext
    card.write_text(html, encoding='utf-8')
    shot = HERE / '.og-shot.mjs'
    shot.write_text(SHOT.format(card=card, out=png), encoding='utf-8')
    subprocess.run(['node', str(shot)], check=True, capture_output=True)

    Image.open(png).convert('RGB').save(SITE / 'og.jpg', 'JPEG', quality=86,
                                        optimize=True, progressive=True)

    # Home-screen and tab icons: the green mark on the paper it always sits on.
    mark = Image.open(HERE / 'assets' / 'logo_green.png').convert('RGBA')
    for size, pad in ((180, 26), (32, 4)):
        tile = Image.new('RGB', (size, size), bm.PAPER)
        m = mark.copy()
        m.thumbnail((size - pad * 2, size - pad * 2), Image.LANCZOS)
        tile.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
        tile.save(SITE / f'icon-{size}.png', 'PNG', optimize=True)

    for f in (card, png, shot):
        f.unlink()
    print('og.jpg', (SITE / 'og.jpg').stat().st_size // 1024, 'KB  ·  icon-180.png, icon-32.png')


if __name__ == '__main__':
    build()
