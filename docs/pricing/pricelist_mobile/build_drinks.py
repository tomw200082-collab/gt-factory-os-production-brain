#!/usr/bin/env python3
"""GT Everyday — what to make at home, phone-shaped PDF. No prices, no margins.

The companion to GT_tea_collection.pdf: that one says what is in the bottle,
this one says what to do with it. One drink per page, thirteen pages.

Scope — Tom, 2026-08-07: "רק הדפים שאפשר להכין אך ורק את המוצרים האלו". A
recipe qualifies only if a person at home can make it with a GT tea extract
plus things any kitchen or supermarket already has: ice, water, soda,
lemonade, apple juice, lychee, a lemon slice, herbs. The Canva catalog's other
31 drinks need matcha, hojicha, ube, GT fruit purées or a batched cold foam,
and are out.

Everything commercial is stripped. The source pages carry FOOD COST, a
recommended consumer price and a margin percentage; none of that belongs in a
sheet for someone's kitchen, so none of it is read.

Concentrate is 30 ml throughout (Tom, 2026-08-07). The source says 50 ml for
the iced teas and lemonades and 40 ml for the signature and gazoz pours — a
café measure. Everything else in a recipe is quoted from the source page.

Source: Canva design DAHPi9gpfts, "קטלוג משקאות מעודכן", pages 8-14, 16-18, 23,
25, 27. Photography is those pages' own, cropped to the catalog's 3:4 frame.

Design follows GT_tea_collection.pdf exactly: paper, one hue per page, a
white-matted photograph on a colour card, the mark and a live WhatsApp link on
every page. The hue is the *extract's* colour, not the drink's, so a page
visibly belongs to a bottle in the other catalog.

Build:  python3 build_drinks.py   →  GT_drinks_at_home.pdf
"""
import base64
import pathlib
import subprocess

import build_mobile as bm
import build_tea as tea

HERE = pathlib.Path(__file__).parent
NODE_PW = '/opt/node22/lib/node_modules/playwright/index.mjs'
PAGE_W, PAGE_H = '90mm', '160mm'

ML = 30                                        # concentrate per glass (Tom, 2026-08-07)

# (key, family, hebrew, latin, description, extract-key, extract-name, steps, chips)
# `extract` keys into build_tea.PALETTE, so the page wears its bottle's colour.
ICED = 'חליטה קרה'
LEMO = 'לימונדה'
SIGN = 'משקה דגל'
GAZO = 'גזוז'


def iced(key, heb, latin, desc, ext, ext_name, garnish):
    return (key, ICED, heb, latin, desc, ext, ext_name,
            ['מלאו כוס בקרח',
             f'הוסיפו {ML} מ״ל תרכיז {ext_name}',
             'השלימו ל־⅔ במים קרים (או סודה למוגז)',
             f'קשטו: {garnish}'],
            ['קרח', f'{ML} מ״ל תרכיז {ext_name}', 'סלייס לימון', 'עשבי קישוט'])


def lemonade(key, heb, latin, desc, ext, ext_name):
    return (key, LEMO, heb, latin, desc, ext, ext_name,
            ['מלאו כוס בקרח',
             f'הוסיפו {ML} מ״ל תרכיז {ext_name}',
             'מלאו עד למעלה בלימונדה',
             'ערבבו קלות והגישו'],
            ['קרח', f'{ML} מ״ל תרכיז {ext_name}', '~250 מ״ל לימונדה'])


DRINKS = [
    iced('fresh', 'חליטת היביסקוס וליים', 'fresh',
         'חליטת היביסקוס וליים — קרה או מוגזת, עם סלייס לימון ונענע',
         'fresh', 'FRESH', 'סלייס לימון · נענע טריה'),
    iced('calm', 'חליטת קמומיל ותפוח', 'calm',
         'קמומיל, תפוח וציפורן · נטול קפאין ומרגיע',
         'calm', 'CALM', 'סלייס לימון · אורגנו/נענע'),
    iced('desertea', 'חליטה מדברית', 'desertea',
         'לואיזה, נענע, אורגנו, מרווה וזוטה לבנה · נטול קפאין',
         'desertea', 'DESERTEA', 'סלייס לימון · מגוון תבלינים'),
    iced('revive', 'חליטת סנצ׳ה ופסיפלורה', 'revive',
         'סנצ׳ה יפני ופסיפלורה · מכיל קפאין, מרענן',
         'revive', 'REVIVE', 'סלייס לימון · רוזמרין'),
    iced('detox', 'חליטת תה ירוק וליים', 'detox',
         'תה ירוק, לואיזה, נענע וליים',
         'detox', 'DETOX', 'סלייס לימון · נענע טריה'),
    iced('energy', 'חליטת תה ירוק ולמון גראס', 'energy',
         'תה ירוק, למון גראס, נענע ולימון',
         'energy', 'ENERGY', 'סלייס לימון · בזיליקום'),
    iced('conscious', 'חליטת יסמין וליצ׳י', 'consciousness',
         'תה יסמין וליצ׳י — קר או מוגז, ארומטי ועדין',
         'conscious', 'CONSCIOUSNESS', 'סלייס לימון · נענע טריה'),

    lemonade('fresh_lemonade', 'לימונדת היביסקוס וליים', 'fresh lemonade',
             'לימונדה מרעננת על בסיס היביסקוס וליים', 'fresh', 'FRESH'),
    lemonade('desertea_lemonade', 'לימונדה מדברית', 'desertea lemonade',
             'לימונדה על בסיס צמחי בר ישראליים', 'desertea', 'DESERTEA'),
    lemonade('namastea_lemonade', 'לימונדת צ׳אי מסאלה', 'namastea lemonade',
             'לימונדה על בסיס צ׳אי מסאלה', 'namastea', 'NAMASTEA'),

    ('fresh_apple', SIGN, 'חליטת תפוח היביסקוס', 'fresh apple',
     'משקה דגל על בסיס מיץ תפוחים', 'fresh', 'FRESH',
     ['מלאו כוס בקרח', 'הוסיפו 40 מ״ל מיץ תפוחים', f'הוסיפו {ML} מ״ל תרכיז FRESH',
      'השלימו ל־⅔ במים', 'קשטו בגרניש לפי טעם'],
     ['קרח', '40 מ״ל מיץ תפוחים', f'{ML} מ״ל תרכיז FRESH', 'גרניש']),

    ('conscious_lychee', GAZO, 'גזוז יסמין וליצ׳י', 'consciousness lychee',
     'גזוז תה יסמין וליצ׳י עם ליצ׳י טרי', 'conscious', 'CONSCIOUSNESS',
     ['מלאו כוס בקרח', 'הוסיפו 40 מ״ל מי ליצ׳י',
      f'הוסיפו {ML} מ״ל תרכיז CONSCIOUSNESS',
      'השלימו ל־⅔ בסודה (~150 מ״ל)', 'קשטו: 2 ליצ׳י'],
     ['קרח', '40 מ״ל מי ליצ׳י', f'{ML} מ״ל תרכיז CONSCIOUSNESS',
      '~150 מ״ל סודה', '2 ליצ׳י']),

    ('fresh_apple_gazoz', GAZO, 'גזוז היביסקוס ותפוח', 'fresh apple',
     'גזוז על בסיס מיץ תפוחים', 'fresh', 'FRESH',
     ['מלאו כוס בקרח', 'הוסיפו 40 מ״ל מיץ תפוחים', f'הוסיפו {ML} מ״ל תרכיז FRESH',
      'השלימו ל־⅔ בסודה (~150 מ״ל)', 'קשטו: גרניש לפי טעם'],
     ['קרח', '40 מ״ל מיץ תפוחים', f'{ML} מ״ל תרכיז FRESH',
      '~150 מ״ל סודה', 'גרניש לפי טעם']),
]

assert {d[5] for d in DRINKS} <= set(tea.PALETTE), 'a drink names an unknown extract'
for d in DRINKS:
    assert (HERE / 'assets' / 'drinks' / f'dr_{d[0]}.jpg').exists(), f'no photo for {d[0]}'
    joined = ' '.join(d[7] + d[8])
    assert '50 מ״ל תרכיז' not in joined and '40 מ״ל תרכיז' not in joined, \
        f'{d[0]} still carries a café pour'


def photo(key):
    return 'data:image/jpeg;base64,' + base64.b64encode(
        (HERE / 'assets' / 'drinks' / f'dr_{key}.jpg').read_bytes()).decode()


def cover_photo():
    return 'data:image/jpeg;base64,' + base64.b64encode(
        (HERE / 'assets' / 'drinks' / 'cover_drink.jpg').read_bytes()).decode()


def css():
    return f"""
{bm.font_faces()}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
@page{{size:{PAGE_W} {PAGE_H};margin:0}}
html,body{{background:{bm.PAPER}}}
body{{font-family:'Heebo',sans-serif;color:{bm.INK};-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}

.p{{position:relative;width:{PAGE_W};height:{PAGE_H};overflow:hidden;background:{bm.PAPER};
   direction:rtl;page-break-after:always}}
.p:last-child{{page-break-after:auto}}

/* ── cover ────────────────────────────────────────────────────────────── */
.cover>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  object-position:50% 100%}}
.cover::after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(239,230,214,.95) 0%,rgba(239,230,214,.72) 30%,rgba(239,230,214,.14) 52%,
  rgba(239,230,214,0) 66%)}}
.cv{{position:absolute;inset:0;z-index:2;padding:15mm 9mm 0;display:flex;
  flex-direction:column;align-items:center;text-align:center}}
.cv .mark{{width:27mm}}
.cv .hair{{width:14mm;height:.5px;background:{bm.INK};opacity:.3;margin:7mm 0 6mm}}
.cv h1{{font-family:'Rubik',sans-serif;font-weight:700;font-size:33pt;line-height:1.06;
  letter-spacing:-.012em}}
.cv .sub{{margin-top:4mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:8pt;
  letter-spacing:.22em;color:{tea.rgba(bm.CORAL_INK, 1)}}}
.cv .lede{{margin-top:7mm;padding-top:6mm;border-top:.5px solid {tea.rgba(bm.INK, .16)};
  max-width:64mm;font-size:8.6pt;line-height:1.95;color:{bm.MUTED};letter-spacing:.01em}}
.cover .yr{{position:absolute;z-index:3;top:9mm;right:9mm;font-family:'Rubik',sans-serif;
  font-weight:600;font-size:7.4pt;letter-spacing:.42em;opacity:.5}}

/* ── recipe page ──────────────────────────────────────────────────────── */
.card{{position:absolute;top:0;left:0;right:0;height:60mm;overflow:hidden;
  background:linear-gradient(165deg,var(--card1),var(--card2))}}
.card .wm{{position:absolute;bottom:-12mm;left:-10mm;width:36mm;height:36mm;
  color:var(--c);opacity:.16;transform:rotate(-8deg)}}
.ph{{position:absolute;z-index:2;top:5mm;left:50%;transform:translateX(-50%);
  width:37mm;background:#fff;border:.5px solid var(--frame);padding:1.5mm;
  box-shadow:0 1mm 3.4mm rgba(36,28,21,.18)}}
.ph img{{display:block;width:100%;height:auto}}

.tx{{position:absolute;top:62mm;right:9mm;left:9mm;color:var(--c)}}
.no{{font-family:'Rubik',sans-serif;font-weight:700;font-size:6.4pt;letter-spacing:.28em}}
.tx h2{{margin-top:1.8mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:14.5pt;
  line-height:1.14;color:{bm.INK}}}
.lat{{margin-top:1.4mm;font-family:'Rubik',sans-serif;font-weight:500;font-size:8pt;
  letter-spacing:.12em}}
.desc{{margin-top:2.6mm;font-size:7.8pt;line-height:1.55;color:{bm.MUTED}}}

.how{{margin-top:4mm;padding-top:3.2mm;border-top:.5px solid {bm.RULE}}}
.how .lb{{font-family:'Rubik',sans-serif;font-weight:700;font-size:6.4pt;
  letter-spacing:.24em;color:{bm.MUTED}}}
.how ol{{margin-top:2.6mm;list-style:none}}
.how li{{display:flex;gap:2.8mm;align-items:baseline;padding:.55mm 0;font-size:8pt;
  line-height:1.45;color:{bm.INK}}}
.how li b{{flex:0 0 4mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:7pt;
  color:var(--c)}}

.chips{{margin-top:3.4mm;display:flex;flex-wrap:wrap;gap:1.4mm}}
.chips span{{border:.5px solid var(--frame);color:{bm.MUTED};font-size:6pt;
  letter-spacing:.01em;padding:.9mm 2mm;border-radius:6mm}}

/* ── order page ───────────────────────────────────────────────────────── */
.order{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center;padding:0 11mm}}
.order .mark{{width:30mm}}
.order h2{{margin-top:11mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:27pt;
  line-height:1.14}}
.order h2 span{{display:block;font-size:.74em;margin-top:1.6mm}}
.order .cta{{margin-top:11mm;width:100%;background:{bm.GREEN};color:{bm.PAPER};
  padding:4.4mm 0 5mm;display:block;box-shadow:0 1mm 3mm rgba(38,59,24,.22)}}
.order .cta small{{display:flex;align-items:center;justify-content:center;gap:1.8mm;
  font-family:'Rubik',sans-serif;font-weight:600;font-size:7pt;letter-spacing:.14em;
  opacity:.92;margin-bottom:2.4mm}}
.order .cta small svg{{width:4.2mm;height:4.2mm;display:block}}
.order .cta b{{display:block;font-family:'Rubik',sans-serif;font-weight:700;font-size:15pt;
  direction:ltr;text-decoration:underline;text-underline-offset:1.4mm;
  text-decoration-thickness:.4mm;text-decoration-color:{tea.rgba(bm.PAPER, .55)}}}
.band{{position:absolute;z-index:2;left:0;right:0;bottom:0;height:6mm;display:flex;
  direction:ltr}}
.band i{{flex:1 1 0}}

/* ── page furniture ───────────────────────────────────────────────────── */
.foot{{position:absolute;bottom:5.4mm;right:9mm;left:9mm;z-index:3;display:flex;
  align-items:center;justify-content:space-between;font-size:5.6pt;letter-spacing:.12em;
  color:{bm.MUTED}}}
.foot .id{{display:flex;align-items:center;gap:2mm}}
.foot .id img{{width:8.4mm;height:auto;opacity:.88}}
.foot .end{{display:flex;align-items:center;gap:2.6mm}}
.foot .wa{{display:inline-flex;align-items:center;gap:1.4mm;padding:1.2mm 2.8mm 1.2mm 2mm;
  border-radius:9mm;background:{bm.GREEN};color:{bm.PAPER};
  font-family:'Rubik',sans-serif;font-weight:600;font-size:5.4pt;letter-spacing:.06em}}
.foot .wa svg{{width:3.4mm;height:3.4mm;display:block}}
.foot .pg{{font-family:'Rubik',sans-serif;font-weight:600;letter-spacing:.24em;opacity:.85}}
"""


def foot(n):
    return f"""<div class="foot">
  <span class="id"><img src="{bm.img('logo_green.png')}" alt="GT EVERYDAY">gteveryday.com</span>
  <span class="end"><a class="wa" href="{tea.WA_TOM}">{tea.WA_MARK}הזמנה בוואטסאפ</a>
    <span class="pg">{n:02d}</span></span>
</div>"""


def page(idx, drink):
    key, fam, heb, latin, desc, ext, ext_name, steps, chips = drink
    accent, deep = tea.PALETTE[ext]
    style = (f'--c:{accent};--card1:{tea.rgba(accent, .26)};'
             f'--card2:{tea.rgba(accent, .10)};--frame:{tea.rgba(deep, .28)}')
    wm = tea.MARK[tea.GLYPHS[ext_name][0]]
    return f"""<div class="p" style="{style}">
  <div class="card"><svg class="wm" viewBox="0 0 24 24" fill="currentColor">{wm}</svg></div>
  <span class="ph"><img src="{photo(key)}" alt="{heb}"></span>
  <div class="tx">
    <span class="no">N°{idx:02d} · {fam}</span>
    <h2>{heb}</h2>
    <div class="lat">{latin}</div>
    <p class="desc">{desc}</p>
    <div class="how">
      <span class="lb">אופן הכנה</span>
      <ol>{''.join(f'<li><b>{i + 1}</b><span>{s}</span></li>' for i, s in enumerate(steps))}</ol>
      <div class="chips">{''.join(f'<span>{c}</span>' for c in chips)}</div>
    </div>
  </div>
  {foot(idx + 1)}
</div>"""


def build():
    bm.MODE, bm.FONT_EXT = 'inline', 'woff'

    cover = f"""<div class="p cover">
  <img src="{cover_photo()}" alt="">
  <span class="yr">2026</span>
  <div class="cv">
    <img class="mark" src="{bm.img('logo_ink.png')}" alt="GT EVERYDAY">
    <span class="hair"></span>
    <h1>משקאות</h1>
    <p class="sub">{len(DRINKS)} מתכונים</p>
    <p class="lede">כל המשקאות כאן מוכנים מתמציות התה שבקטלוג —
      כוס, קרח, {ML} מ״ל תרכיז ומה שיש במקרר.</p>
  </div>
</div>"""

    pages = "".join(page(i + 1, d) for i, d in enumerate(DRINKS))

    order = f"""<div class="p">
  <div class="order">
    <img class="mark" src="{bm.img('logo_green.png')}" alt="GT EVERYDAY">
    <h2>להזמנות<span>תום</span></h2>
    <a class="cta" href="{tea.WA_TOM}"><small>{tea.WA_MARK}לחצו לשיחת וואטסאפ</small>
      <b>{tea.TEL_TOM}</b></a>
  </div>
  <span class="band">{''.join(f'<i style="background:{c}"></i>' for c in tea.SPECTRUM)}</span>
</div>"""

    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>GT Everyday — משקאות להכנה בבית</title><style>{css()}</style></head>'
            f'<body>{cover}{pages}{order}</body></html>')

    src = HERE / '.drinks-src.html'
    src.write_text(html, encoding='utf-8')
    out = HERE / 'GT_drinks_at_home.pdf'
    shot = HERE / '.drinks-shot.mjs'
    shot.write_text(f"""
import {{ chromium }} from '{NODE_PW}';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('file://{src}', {{ waitUntil: 'load' }});
await p.evaluate(() => document.fonts.ready);
const over = await p.evaluate(() => {{
  const RESERVE = 48;
  return [...document.querySelectorAll('.p')].map((pg, i) => {{
    const top = pg.getBoundingClientRect().top, lim = pg.clientHeight - RESERVE;
    let worst = 0;
    for (const el of pg.querySelectorAll('.chips, .how li, .lede, .cta'))
      worst = Math.max(worst, el.getBoundingClientRect().bottom - top);
    return {{ page: i + 1, over: Math.round(worst - lim) }};
  }}).filter(r => r.over > 0);
}});
if (over.length) {{ console.error('OVERFLOW ' + JSON.stringify(over)); process.exit(3); }}
await p.pdf({{ path: '{out}', width: '{PAGE_W}', height: '{PAGE_H}',
  printBackground: true, margin: {{ top: 0, right: 0, bottom: 0, left: 0 }} }});
await b.close();
""", encoding='utf-8')
    r = subprocess.run(['node', str(shot)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'{r.stderr.strip()}\n(source kept at {src})')
    src.unlink()
    shot.unlink()
    print(f'{out.name}  {out.stat().st_size / 1e6:.2f} MB  ·  {len(DRINKS) + 2} pages'
          f'  ·  {PAGE_W}×{PAGE_H}  ·  overflow guard clean')


if __name__ == '__main__':
    build()
