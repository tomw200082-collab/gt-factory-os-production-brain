#!/usr/bin/env python3
"""GT Everyday — wholesale pricelist, phone-shaped PDF.

A PDF is what a buyer keeps: it survives in a WhatsApp thread, opens without a
signal, and gets forwarded to a partner. The A4 sheet in `../pricelist_pdf/`
does none of that well on a phone — it arrives as a page you pinch and pan.

So the page is the phone: 90 × 160 mm, exactly 9:16. Every page fills the screen
at full width, and a swipe is a whole new screen rather than a scroll position.

Figures, names, sub-lines and photography come from `build_mobile.py`. Nothing
here recomputes a price. One line is derived rather than quoted, and it is
marked in the code where it is set.

Where this differs from the web page, and why:

  * The web page is operated — it answers "what does X cost" in three seconds,
    so every row carries its own price panel. This is read, so it argues
    instead. Eleven teas at one price do not need the price printed eleven
    times: the pair is stated once, at the head of the section, and the rows
    are then free to be what actually sells them — the label art and the
    infusion. Same for the three purées.
  * Only the sections whose prices genuinely differ set a price per row.
  * No tinted panels, no chips, no sticky anything. Hairlines and paper.

Build:  python3 build_pdf.py   →  GT_pricelist_mobile.pdf
"""
import pathlib
import subprocess

import build_mobile as bm

HERE = pathlib.Path(__file__).parent
NODE_PW = '/opt/node22/lib/node_modules/playwright/index.mjs'

PAGE_W, PAGE_H = '90mm', '160mm'

# Cups per bottle is the print sheet's own line. The per-cup figure is the only
# number on this sheet that is not quoted from build_mobile.py: it is ₪65 ÷ 25
# and ₪65 ÷ 20, shown as a range and with its arithmetic printed underneath, so
# nothing is claimed that the two published figures do not already carry.
CUPS_LOW, CUPS_HIGH = 20, 25
CUP_LOW = f'{bm.TEA_L / CUPS_HIGH:.2f}'
CUP_HIGH = f'{bm.TEA_L / CUPS_LOW:.2f}'


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
.in{{padding:0 9mm}}

/* ── cover ────────────────────────────────────────────────────────────── */
.cover>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  object-position:50% 100%}}
.cover::after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(239,230,214,.72) 0%,rgba(239,230,214,.42) 34%,rgba(239,230,214,0) 58%)}}
.cv{{position:absolute;inset:0;z-index:2;padding:17mm 9mm 0;display:flex;
  flex-direction:column;align-items:center;text-align:center}}
.cv .mark{{width:19mm}}
.cv .hair{{width:11mm;height:.4px;background:{bm.INK};opacity:.32;margin:7mm 0 6mm}}
.cv h1{{font-family:'Rubik',sans-serif;font-weight:700;font-size:24pt;line-height:1.08;
  letter-spacing:-.006em}}
.cv .sub{{margin-top:4mm;font-size:8.4pt;line-height:1.85;color:{bm.MUTED};letter-spacing:.03em}}
.cv .tag{{margin-top:6mm;background:{bm.CORAL};color:{bm.INK};font-family:'Rubik',sans-serif;
  font-weight:600;font-size:7.6pt;letter-spacing:.1em;padding:2.6mm 4.6mm}}
.cover .yr{{position:absolute;z-index:3;top:9mm;right:9mm;font-family:'Rubik',sans-serif;
  font-weight:600;font-size:7.4pt;letter-spacing:.42em;opacity:.5}}
.cover .url{{position:absolute;z-index:3;bottom:8mm;left:0;right:0;text-align:center;
  font-family:'Rubik',sans-serif;font-weight:500;font-size:7pt;letter-spacing:.1em;color:#fff;
  opacity:.92}}

/* ── argument page ────────────────────────────────────────────────────── */
.arg{{display:flex;flex-direction:column;justify-content:center;padding:0 11mm}}
.arg .k{{font-family:'Rubik',sans-serif;font-weight:600;font-size:7pt;letter-spacing:.3em;
  color:{bm.MUTED}}}
.arg .big{{margin-top:5mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:34pt;
  line-height:1;letter-spacing:-.02em;direction:ltr;text-align:right;
  font-variant-numeric:tabular-nums}}
.arg .big .cur{{font-size:.46em;font-weight:600;color:{bm.CORAL_INK};margin-right:.06em;
  vertical-align:.14em}}
.arg .lead{{margin-top:4mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:12.5pt;
  line-height:1.35}}
.arg .rule{{width:16mm;height:1.2px;background:{bm.CORAL};margin:8mm 0}}
.arg .maths{{font-size:8.2pt;line-height:2;color:{bm.MUTED}}}
.arg .maths b{{font-family:'Rubik',sans-serif;font-weight:600;color:{bm.INK}}}

/* ── section head ─────────────────────────────────────────────────────── */
.band{{position:relative;width:{PAGE_W};height:26mm;overflow:hidden}}
.band img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.band::after{{content:'';position:absolute;inset:0;background:linear-gradient(to left,
  rgba(20,14,8,.72) 0%,rgba(20,14,8,.3) 52%,rgba(20,14,8,0) 84%)}}
.band-t{{position:absolute;z-index:2;right:9mm;bottom:4.4mm;color:#fff}}
.band-t .bk{{display:block;font-family:'Rubik',sans-serif;font-weight:500;font-size:5.4pt;
  letter-spacing:.34em;opacity:.88}}
.band-t .bt{{display:block;font-family:'Rubik',sans-serif;font-weight:700;font-size:14pt;
  margin-top:.8mm}}

.sec{{margin:5.4mm 0 0;position:relative;padding-right:3.4mm}}
.sec::before{{content:'';position:absolute;right:0;top:.6mm;bottom:.6mm;width:1.3px;
  background:{bm.CORAL}}}
.sec h2{{font-family:'Rubik',sans-serif;font-weight:700;font-size:14pt;color:{bm.GREEN}}}
.sec .k{{display:block;font-family:'Rubik',sans-serif;font-weight:500;font-size:5.4pt;
  letter-spacing:.32em;color:{bm.MUTED};margin-top:.9mm}}
.cont{{margin-top:6mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:8pt;
  letter-spacing:.24em;color:{bm.MUTED}}}

/* One price for the whole section, stated once instead of eleven times. */
.oneprice{{margin-top:4mm;border-top:.5px solid {bm.RULE};border-bottom:.5px solid {bm.RULE};
  padding:3.4mm 0;display:flex;align-items:baseline;gap:5mm}}
.oneprice .u{{display:flex;align-items:baseline;gap:1.6mm}}
.oneprice .sz{{font-family:'Rubik',sans-serif;font-weight:600;font-size:7pt;color:{bm.MUTED}}}
.oneprice .v{{font-family:'Rubik',sans-serif;font-weight:700;font-size:15pt;line-height:1;
  direction:ltr;font-variant-numeric:tabular-nums}}
.oneprice .v .cur{{font-size:.55em;font-weight:600;color:{bm.CORAL_INK};margin-right:.08em;
  vertical-align:.12em}}

/* ── rows ─────────────────────────────────────────────────────────────── */
.list{{margin-top:1mm}}
.r{{display:flex;align-items:center;gap:4mm;padding:2.6mm 0;border-bottom:.5px solid {bm.RULE}}}
.r:last-child{{border-bottom:0}}
.r .sh{{flex:0 0 13mm;height:13mm;display:flex;align-items:center;justify-content:center}}
.r .sh img{{max-width:100%;max-height:100%;object-fit:contain}}
.r .sh--mark img{{width:6mm;opacity:.16}}
.r .m{{flex:1 1 auto;min-width:0}}
.r .m b{{display:block;font-family:'Rubik',sans-serif;font-weight:600;font-size:9.6pt;
  line-height:1.2;letter-spacing:.02em}}
.r .m i{{display:block;font-style:normal;font-size:6.8pt;line-height:1.4;color:{bm.MUTED};
  margin-top:.7mm}}
.r .v{{flex:0 0 auto;font-family:'Rubik',sans-serif;font-weight:700;font-size:13pt;
  line-height:1;direction:ltr;font-variant-numeric:tabular-nums;white-space:nowrap}}
.r .v .cur{{font-size:.55em;font-weight:600;color:{bm.CORAL_INK};margin-right:.1em;
  vertical-align:.12em}}
.roomy .r{{padding:5mm 0}}
.roomy .r .sh{{flex-basis:19mm;height:19mm}}
.dense .r{{padding:2.2mm 0}}
.dense .r .sh{{flex-basis:11.5mm;height:11.5mm}}

/* ── order page ───────────────────────────────────────────────────────── */
.order{{display:flex;flex-direction:column;justify-content:center;padding:0 11mm;text-align:center;
  align-items:center}}
.order .mark{{width:16mm}}
.order h2{{margin-top:8mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:19pt;
  line-height:1.15}}
.order .sub{{margin-top:4mm;font-size:8.4pt;line-height:1.8;color:{bm.MUTED}}}
.order .cta{{margin-top:9mm;width:100%;background:{bm.GREEN};color:{bm.PAPER};padding:4.6mm 0;
  font-family:'Rubik',sans-serif;font-weight:700;font-size:13pt;letter-spacing:.02em;
  direction:ltr}}
.order .cta small{{display:block;font-weight:500;font-size:6.6pt;letter-spacing:.22em;
  opacity:.8;margin-bottom:1.4mm;direction:rtl}}
.order .site{{margin-top:6mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:8pt;
  letter-spacing:.06em;color:{bm.CORAL_INK}}}
.order .fine{{position:absolute;bottom:9mm;left:9mm;right:9mm;font-size:6.4pt;
  letter-spacing:.1em;color:{bm.MUTED}}}

.foot{{position:absolute;bottom:6mm;right:9mm;left:9mm;display:flex;
  justify-content:space-between;align-items:center;font-size:5.6pt;letter-spacing:.12em;
  color:{bm.MUTED}}}
.foot .pg{{font-family:'Rubik',sans-serif;font-weight:600;letter-spacing:.24em;opacity:.8}}
"""


def money(v, cls='v'):
    return f'<span class="{cls}"><span class="cur">₪</span>{v}</span>'


def foot(n):
    return (f'<div class="foot"><span>כל המחירים ללא מע״מ</span>'
            f'<span class="pg">{n:02d}</span></div>')


def band(img, kicker, title):
    return (f'<div class="band"><img src="{bm.img(img)}" alt="">'
            f'<div class="band-t"><span class="bk">{kicker}</span>'
            f'<span class="bt">{title}</span></div></div>')


def sec(title, kicker):
    return f'<div class="sec"><h2>{title}</h2><span class="k">{kicker}</span></div>'


def flavour(name, sub, key):
    """Tea row — no price. The pair is stated once, above the list."""
    return (f'<div class="r"><span class="sh"><img src="{bm.img(f"big_{key}.jpg")}" alt=""></span>'
            f'<span class="m"><b>{name}</b><i>{sub}</i></span></div>')


def priced(name, sub, key, value):
    sh = (f'<span class="sh"><img src="{bm.img(key + ".jpg")}" alt=""></span>' if key
          else f'<span class="sh sh--mark"><img src="{bm.img("logo_green.png")}" alt=""></span>')
    return (f'<div class="r">{sh}<span class="m"><b>{name}</b><i>{sub}</i></span>'
            f'{money(value)}</div>')


def build():
    bm.MODE, bm.FONT_EXT = 'inline', 'woff'

    cover = f"""<div class="p cover">
  <img src="{bm.img('cover.jpg')}" alt="">
  <span class="yr">2026</span>
  <div class="cv">
    <img class="mark" src="{bm.img('logo_ink.png')}" alt="GT EVERYDAY">
    <span class="hair"></span>
    <h1>מחירון סיטונאי</h1>
    <p class="sub">תמציות תה · מאצ׳ה ואבקות<br>מחיות פרי · מוצרים משלימים</p>
    <span class="tag">כל המחירים ללא מע״מ</span>
  </div>
  <span class="url">{bm.SITE_URL.replace('https://', '')}</span>
</div>"""

    argument = f"""<div class="p arg">
  <span class="k">COST&nbsp;&nbsp;PER&nbsp;&nbsp;CUP</span>
  <div class="big">{money(f'{CUP_LOW}–{CUP_HIGH}', 'x')}</div>
  <p class="lead">זו עלות התמצית<br>בכוס משקה אחת.</p>
  <span class="rule"></span>
  <p class="maths">
    בקבוק <b>1 ליטר</b> = <b>{CUPS_LOW}–{CUPS_HIGH} כוסות</b><br>
    {money(bm.TEA_L, 'x2')} ÷ {CUPS_HIGH} כוסות = {money(CUP_LOW, 'x2')} לכוס<br>
    {money(bm.TEA_L, 'x2')} ÷ {CUPS_LOW} כוסות = {money(CUP_HIGH, 'x2')} לכוס
  </p>
  {foot(2)}
</div>"""

    tea_bar = (f'<div class="oneprice">'
               f'<span class="u"><span class="sz">1 ליטר</span>{money(bm.TEA_L, "v")}</span>'
               f'<span class="u"><span class="sz">500 מ״ל</span>{money(bm.TEA_ML, "v")}</span>'
               f'</div>')

    # Splits are set by the page, not by the catalogue: five flavours clear the
    # band on the opening page, six fit where there is no band. The guard below
    # fails the build if either number stops being true.
    tea_a = "".join(flavour(n, s, k) for n, s, k in bm.TEAS[:5])
    tea_b = "".join(flavour(n, s, k) for n, s, k in bm.TEAS[5:])

    p3 = f"""<div class="p">
  {band('band_tea.jpg', 'TEA&nbsp;&nbsp;EXTRACTS', 'תמציות תה')}
  <div class="in">{sec('תמציות תה', 'כל הטעמים · אותו מחיר')}
    {tea_bar}<div class="list">{tea_a}</div></div>
  {foot(3)}
</div>"""

    p4 = f"""<div class="p">
  <div class="in" style="padding-top:12mm">
    <span class="cont">תמציות תה · המשך</span>
    {tea_bar}<div class="list">{tea_b}</div></div>
  {foot(4)}
</div>"""

    p5 = f"""<div class="p">
  {band('band_powder.jpg', 'MATCHA&nbsp;&nbsp;·&nbsp;&nbsp;POWDERS', 'מאצ׳ה ואבקות')}
  <div class="in">{sec('מאצ׳ה ואבקות', 'MATCHA&nbsp;&nbsp;·&nbsp;&nbsp;POWDERS')}
    <div class="list dense" style="margin-top:4mm">
      {"".join(priced(n, s, k, v) for n, s, k, v in bm.POWDERS)}</div></div>
  {foot(5)}
</div>"""

    puree_bar = (f'<div class="oneprice"><span class="u">'
                 f'<span class="sz">1 ליטר · כל הטעמים</span>{money(60, "v")}</span></div>')

    p6 = f"""<div class="p">
  <div class="in" style="padding-top:14mm">{sec('מחיות פרי', 'FRUIT&nbsp;&nbsp;PURÉES')}
    {puree_bar}
    <div class="list roomy">
      {"".join(f'<div class="r"><span class="sh"><img src="{bm.img(k + ".jpg")}" alt=""></span>'
               f'<span class="m"><b>{n}</b><i>{s}</i></span></div>'
               for n, s, k, _ in bm.PUREES)}</div></div>
  {foot(6)}
</div>"""

    p7 = f"""<div class="p">
  {band('band_tools.jpg', 'TOOLS&nbsp;&nbsp;·&nbsp;&nbsp;SERVEWARE', 'מוצרים משלימים')}
  <div class="in">{sec('מוצרים משלימים', 'TOOLS&nbsp;&nbsp;·&nbsp;&nbsp;SERVEWARE')}
    <div class="list" style="margin-top:3mm">
      {"".join(priced(n, s, k, v) for n, s, k, v in bm.TOOLS[:5])}</div></div>
  {foot(7)}
</div>"""

    p8 = f"""<div class="p">
  <div class="in" style="padding-top:12mm">
    <span class="cont">מוצרים משלימים · המשך</span>
    <div class="list roomy" style="margin-top:4mm">
      {"".join(priced(n, s, k, v) for n, s, k, v in bm.TOOLS[5:])}</div></div>
  {foot(8)}
</div>"""

    order = f"""<div class="p order">
  <img class="mark" src="{bm.img('logo_green.png')}" alt="GT EVERYDAY">
  <h2>נשמח לקבל<br>את ההזמנה שלכם</h2>
  <p class="sub">אספקה שבועית · הזמנה בוואטסאפ או בטלפון</p>
  <div class="cta"><small>להזמנות</small>{bm.TEL}</div>
  <span class="site">{bm.SITE_URL.replace('https://', '')}</span>
  <p class="fine">כל המחירים בשקלים, ללא מע״מ · המחירון בתוקף לשנת 2026</p>
</div>"""

    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>GT Everyday — מחירון סיטונאי</title><style>{css()}</style></head>'
            f'<body>{cover}{argument}{p3}{p4}{p5}{p6}{p7}{p8}{order}</body></html>')

    src = HERE / '.pdf-src.html'
    src.write_text(html, encoding='utf-8')
    out = HERE / 'GT_pricelist_mobile.pdf'
    shot = HERE / '.pdf-shot.mjs'
    shot.write_text(f"""
import {{ chromium }} from '{NODE_PW}';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('file://{src}', {{ waitUntil: 'load' }});
await p.evaluate(() => document.fonts.ready);
const over = await p.evaluate(() => {{
  const RESERVE = 34;                       // the footer band, in CSS px
  return [...document.querySelectorAll('.p')].map((pg, i) => {{
    const top = pg.getBoundingClientRect().top, lim = pg.clientHeight - RESERVE;
    let worst = 0;
    for (const el of pg.querySelectorAll('.list > *, .oneprice, .cta, .fine'))
      worst = Math.max(worst, el.getBoundingClientRect().bottom - top);
    return {{ page: i + 1, over: Math.round(worst - lim) }};
  }}).filter(r => r.over > 0);
}});
if (over.length) {{
  console.error('OVERFLOW ' + JSON.stringify(over));
  process.exit(3);
}}
await p.pdf({{ path: '{out}', width: '{PAGE_W}', height: '{PAGE_H}',
  printBackground: true, margin: {{ top: 0, right: 0, bottom: 0, left: 0 }} }});
await b.close();
""", encoding='utf-8')
    r = subprocess.run(['node', str(shot)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'{r.stderr.strip()}\n(source kept at {src} for inspection)')
    src.unlink()
    shot.unlink()
    print(f'{out.name}  {out.stat().st_size / 1e6:.2f} MB  ·  9 pages  ·  {PAGE_W}×{PAGE_H}'
          f'  ·  overflow guard clean')


if __name__ == '__main__':
    build()
