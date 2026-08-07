#!/usr/bin/env python3
"""GT Everyday — tea collection, phone-shaped PDF. No prices.

Not a pricelist — a shop window. Eleven infusions, two to a page, each as a
framed studio photograph with one spoken-Hebrew line that sells it. The
sheet's job is to make someone want the tasting, not to close the numbers;
the numbers live in GT_pricelist_mobile.pdf.

Photography is the original studio set (Dropbox `AI YASTREBOVA/all bottles`,
2026-07-17), cropped to a uniform 3:4 around the bottle and kept on its own
clean backdrop — framed, not cut out (Tom, 2026-08-07). Names and origin lines
come from build_mobile.py. The only text authored here is PITCH below.

AMERICAN is not yet on sale — its page carries a coming-soon badge and closes
the book as a teaser rather than an offer.

Pages: cover · 5 × pairs (base + sugar-free share a page) · AMERICAN solo
finale · order page = 8, at 90 × 160 mm (9:16, the phone's own shape).

Build:  python3 build_tea.py   →  GT_tea_collection.pdf
"""
import pathlib
import subprocess

import build_mobile as bm

HERE = pathlib.Path(__file__).parent
NODE_PW = '/opt/node22/lib/node_modules/playwright/index.mjs'
PAGE_W, PAGE_H = '90mm', '160mm'
TEL_TOM = '053-725-2858'          # Tom's own line — this catalog only (Tom, 2026-08-07)

# One selling line per flavour — spoken Hebrew, keyed by the flavour's display
# name so a rename in build_mobile.py fails the build instead of dropping copy.
PITCH = {
    'FRESH':          'היביסקוס וליים שנפתחים לאדום עמוק בכוס. אצל הלקוחות שלנו זה הבקבוק שנגמר ראשון.',
    'FRESH ללא סוכר': 'אותו ליים, אותו היביסקוס, בלי סוכר. מי שטועם לא מרגיש שחסר משהו.',
    'DETOX':          'לואיזה ונענע על תה ירוק. קליל וצמחי, מהסוג שאפשר לשתות כל היום בלי להתעייף ממנו.',
    'DETOX ללא סוכר': 'למי שרוצה נקי עד הסוף. רק הצמחים והתה, שום דבר מעבר.',
    'ENERGY':         'למון גראס ותה ירוק עם בעיטה. השעה ארבע אחר הצהריים של אנשים שלא שותים קפה.',
    'CALM':           'קמומיל, תפוח וקצת ציפורן. חם בערב, קר בצהריים — הראש יורד הילוך.',
    'CONSCIOUSNESS':  'יסמין וליצ׳י. נשמע מוזר עד הלגימה הראשונה, ואז מבינים למה שואלים עליו כל הזמן.',
    'REVIVE':         'סנצ׳ה יפנית עם פסיפלורה. עדין וחמצמץ, ועל קרח עם עלה נענע — קיץ.',
    'DESERTEA':       'חמישה צמחי בר מהמדבר הישראלי. כוס שאף תפריט אחר בארץ לא מגיש.',
    'NAMASTEA':       'מסאלה צ׳אי עם הל, קינמון וג׳ינג׳ר. עם חלב מוקצף חם — קשה לחזור אחורה.',
    'AMERICAN':       'תה שחור עם יוזו והדרים. אייס טי אמריקאי קלאסי — נוחת אצלנו ממש בקרוב.',
}
_names = {n for n, _, _ in bm.TEAS}
assert set(PITCH) == _names, f'PITCH out of sync with TEAS: {set(PITCH) ^ _names}'

# Page order: each sugar-free beside its base, AMERICAN closes alone.
PAIRS = [bm.TEAS[0:2], bm.TEAS[2:4], bm.TEAS[4:6], bm.TEAS[6:8], bm.TEAS[8:10]]
FINALE = bm.TEAS[10]


def css():
    return f"""
{bm.font_faces()}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
@page{{size:{PAGE_W} {PAGE_H};margin:0}}
html,body{{background:{bm.PAPER}}}
body{{font-family:'Heebo',sans-serif;color:{bm.INK};-webkit-font-smoothing:antialiased}}

.p{{position:relative;width:{PAGE_W};height:{PAGE_H};overflow:hidden;background:{bm.PAPER};
   direction:rtl;page-break-after:always}}
.p:last-child{{page-break-after:auto}}

/* ── cover ────────────────────────────────────────────────────────────── */
.cover>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  object-position:50% 100%}}
.cover::after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(239,230,214,.74) 0%,rgba(239,230,214,.44) 36%,rgba(239,230,214,0) 60%)}}
.cv{{position:absolute;inset:0;z-index:2;padding:17mm 9mm 0;display:flex;
  flex-direction:column;align-items:center;text-align:center}}
.cv .mark{{width:19mm}}
.cv .hair{{width:11mm;height:.4px;background:{bm.INK};opacity:.32;margin:7mm 0 6mm}}
.cv h1{{font-family:'Rubik',sans-serif;font-weight:700;font-size:23pt;line-height:1.12;
  letter-spacing:-.006em}}
.cv .sub{{margin-top:4mm;font-size:8.6pt;line-height:1.85;color:{bm.MUTED};letter-spacing:.02em}}
.cv .tag{{margin-top:6mm;background:{bm.CORAL};color:{bm.INK};font-family:'Rubik',sans-serif;
  font-weight:600;font-size:7.6pt;letter-spacing:.08em;padding:2.6mm 4.6mm}}
.cover .yr{{position:absolute;z-index:3;top:9mm;right:9mm;font-family:'Rubik',sans-serif;
  font-weight:600;font-size:7.4pt;letter-spacing:.42em;opacity:.5}}

/* ── flavour pages: two tall blocks, one hairline between ─────────────── */
.half{{position:absolute;right:9mm;left:9mm;height:69mm;display:flex;align-items:center;
  gap:5.5mm}}
.half.a{{top:7mm}}
.half.b{{top:81mm;border-top:.5px solid {bm.RULE};padding-top:0}}
/* the photograph keeps its own studio backdrop; the frame is a hairline with a
   narrow paper-white matte, like a print in a gallery */
.half .ph{{flex:0 0 34mm;background:#fff;border:.5px solid {bm.RULE};padding:1.3mm;
  box-shadow:0 .8mm 2.4mm rgba(36,28,21,.10)}}
.half .ph img{{display:block;width:100%;height:auto}}
.half .tx{{flex:1 1 auto;min-width:0}}
.half .no{{font-family:'Rubik',sans-serif;font-weight:600;font-size:6.4pt;letter-spacing:.3em;
  color:{bm.CORAL_INK}}}
.half h2{{margin-top:1.6mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:13pt;
  line-height:1.12;letter-spacing:.01em;white-space:nowrap}}
.half .or{{margin-top:1.8mm;font-family:'Rubik',sans-serif;font-weight:500;font-size:6.8pt;
  letter-spacing:.04em;color:{bm.MUTED}}}
.half .say{{margin-top:3mm;font-size:8.6pt;line-height:1.7;color:{bm.INK}}}
.half .sz{{margin-top:3mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:6.6pt;
  letter-spacing:.14em;color:{bm.MUTED};white-space:nowrap}}

/* ── finale: one flavour, full stage ──────────────────────────────────── */
.solo{{position:absolute;inset:0;padding:0 11mm;display:flex;flex-direction:column;
  justify-content:center;align-items:center;text-align:center}}
.solo .ph{{width:52mm;background:#fff;border:.5px solid {bm.RULE};padding:1.6mm;
  box-shadow:0 1mm 3mm rgba(36,28,21,.12);position:relative}}
.solo .ph img{{display:block;width:100%;height:auto}}
.solo .soon{{position:absolute;top:4mm;left:-3mm;background:{bm.CORAL};color:{bm.INK};
  font-family:'Rubik',sans-serif;font-weight:700;font-size:7.6pt;letter-spacing:.16em;
  padding:2mm 4.4mm;box-shadow:0 .6mm 2mm rgba(36,28,21,.18)}}
.solo .no{{margin-top:7mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:7pt;
  letter-spacing:.34em;color:{bm.CORAL_INK}}}
.solo h2{{margin-top:2mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:22pt}}
.solo .or{{margin-top:2mm;font-family:'Rubik',sans-serif;font-weight:500;font-size:7.6pt;
  letter-spacing:.06em;color:{bm.MUTED}}}
.solo .say{{margin-top:4mm;max-width:58mm;font-size:9.4pt;line-height:1.75}}
.solo .sz{{margin-top:4mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:7pt;
  letter-spacing:.14em;color:{bm.MUTED}}}

/* ── order page ───────────────────────────────────────────────────────── */
.order{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center;padding:0 11mm}}
.order .mark{{width:16mm}}
.order h2{{margin-top:8mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:18pt;
  line-height:1.2}}
.order .sub{{margin-top:4mm;font-size:8.6pt;line-height:1.85;color:{bm.MUTED}}}
.order .cta{{margin-top:9mm;width:100%;background:{bm.GREEN};color:{bm.PAPER};padding:4.6mm 0;
  font-family:'Rubik',sans-serif;font-weight:700;font-size:13pt;direction:ltr}}
.order .cta small{{display:block;font-weight:500;font-size:6.6pt;letter-spacing:.22em;
  opacity:.8;margin-bottom:1.4mm;direction:rtl}}
.order .site{{margin-top:6mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:8pt;
  letter-spacing:.06em;color:{bm.CORAL_INK}}}

.foot{{position:absolute;bottom:6mm;right:9mm;left:9mm;display:flex;
  justify-content:space-between;font-size:5.6pt;letter-spacing:.12em;color:{bm.MUTED}}}
.foot .pg{{font-family:'Rubik',sans-serif;font-weight:600;letter-spacing:.24em;opacity:.8}}
"""


def foot(n):
    return (f'<div class="foot"><span>gteveryday.com</span>'
            f'<span class="pg">{n:02d}</span></div>')


def show(name):
    """'FRESH ללא סוכר' stacks badly at display size — the qualifier drops a line.
    CONSCIOUSNESS is one unbreakable word — long names take a smaller size."""
    qual = ''
    if name.endswith(' ללא סוכר'):
        name = name[:-len(' ללא סוכר')]
        qual = '<span style="display:block;font-size:.62em;margin-top:.8mm">ללא סוכר</span>'
    size = '' if len(name) <= 9 else ' style="font-size:10pt;letter-spacing:.04em"'
    return f'<span{size}>{name}</span>{qual}'


def ph(key):
    return f'data:image/jpeg;base64,' + __import__('base64').b64encode(
        (HERE / 'assets' / 'tea' / f'ph_{key}.jpg').read_bytes()).decode()


def block(pos, idx, name, origin, key):
    return f"""<div class="half {pos}">
  <span class="ph"><img src="{ph(key)}" alt="{name}"></span>
  <span class="tx">
    <span class="no">N°{idx:02d}</span>
    <h2>{show(name)}</h2>
    <span class="or">{origin}</span>
    <p class="say">{PITCH[name]}</p>
    <span class="sz">1 ליטר · 500 מ״ל</span>
  </span>
</div>"""


def build():
    bm.MODE, bm.FONT_EXT = 'inline', 'woff'

    cover = f"""<div class="p cover">
  <img src="{bm.img('cover.jpg')}" alt="">
  <span class="yr">2026</span>
  <div class="cv">
    <img class="mark" src="{bm.img('logo_ink.png')}" alt="GT EVERYDAY">
    <span class="hair"></span>
    <h1>אחד עשר טעמים.<br>עולם שלם בבקבוק.</h1>
    <p class="sub">תמציות תה טבעיות להכנה קרה או חמה<br>מוזגים, מוסיפים מים וקרח — מוכן</p>
    <span class="tag">בקבוק אחד = 20–25 כוסות משקה</span>
  </div>
</div>"""

    pages, n = [], 0
    for pi, pair in enumerate(PAIRS):
        halves = []
        for hi, (name, origin, key) in enumerate(pair):
            n += 1
            halves.append(block('a' if hi == 0 else 'b', n, name, origin, key))
        pages.append(f'<div class="p">{"".join(halves)}{foot(pi + 2)}</div>')

    name, origin, key = FINALE
    finale = f"""<div class="p">
  <div class="solo">
    <span class="ph"><img src="{ph(key)}" alt="{name}">
      <span class="soon">בקרוב</span></span>
    <span class="no">N°11 · COMING&nbsp;SOON</span>
    <h2>{name}</h2>
    <span class="or">{origin}</span>
    <p class="say">{PITCH[name]}</p>
  </div>
  {foot(7)}
</div>"""

    order = f"""<div class="p">
  <div class="order">
    <img class="mark" src="{bm.img('logo_green.png')}" alt="GT EVERYDAY">
    <h2>רוצים לטעום?</h2>
    <p class="sub">כל טעם מגיע בבקבוק ליטר או חצי ליטר<br>מדברים עם תום — ומרכיבים יחד את התפריט שלכם</p>
    <div class="cta"><small>תום · בוואטסאפ או בטלפון</small>{TEL_TOM}</div>
    <span class="site">{bm.SITE_URL.replace('https://', '')}</span>
  </div>
</div>"""

    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>GT Everyday — תמציות תה</title><style>{css()}</style></head>'
            f'<body>{cover}{"".join(pages)}{finale}{order}</body></html>')

    src = HERE / '.tea-src.html'
    src.write_text(html, encoding='utf-8')
    out = HERE / 'GT_tea_collection.pdf'
    shot = HERE / '.tea-shot.mjs'
    shot.write_text(f"""
import {{ chromium }} from '{NODE_PW}';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('file://{src}', {{ waitUntil: 'load' }});
await p.evaluate(() => document.fonts.ready);
await p.pdf({{ path: '{out}', width: '{PAGE_W}', height: '{PAGE_H}',
  printBackground: true, margin: {{ top: 0, right: 0, bottom: 0, left: 0 }} }});
await b.close();
""", encoding='utf-8')
    subprocess.run(['node', str(shot)], check=True, capture_output=True)
    src.unlink()
    shot.unlink()
    print(f'{out.name}  {out.stat().st_size / 1e6:.2f} MB  ·  8 pages  ·  {PAGE_W}×{PAGE_H}')


if __name__ == '__main__':
    build()
