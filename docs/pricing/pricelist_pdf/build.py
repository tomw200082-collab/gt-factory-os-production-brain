#!/usr/bin/env python3
"""GT Everyday — wholesale pricelist, A4, Hebrew RTL, all prices ex-VAT.

Design DNA is taken from Tom's Canva products catalog (DAHQrpThEBE), not
invented: every page there is a full-bleed photograph with white type over it,
the `gt` mark sits at the top, product names are letterspaced Latin caps beside
Hebrew, and a hairline rule does the structural work. This sheet keeps all four
and adds the one thing a pricelist needs and a catalog does not — a price column
you can run your eye down.

Palette is sampled from the catalog and the cover photograph:
  paper  #EFE6D6  the cover photograph's own wall
  ink    #241C15  the bottle cap
  green  #263B18  the logo
  coral  #FA6E4D  the catalog's own accent page
  rule   #D8CCB4  kraft, lightened

Prices: 27 of 31 rows come straight from
docs/pricing/2026-08-05_shopify_products_exvat.tsv (column price_ils_exvat,
matched by SKU). The rest are Tom's, flagged in FIGURES.
"""
import base64, os, pathlib

HERE = pathlib.Path(__file__).parent
CUT = HERE / 'cut'

# ─── palette ────────────────────────────────────────────────────────────────
PAPER, INK, GREEN, CORAL = '#EFE6D6', '#241C15', '#263B18', '#FA6E4D'
RULE, MUTED = '#D8CCB4', '#7C6E58'

# ─── data ───────────────────────────────────────────────────────────────────
# (english, hebrew sub, cutout key, prices…)   price = ex-VAT shekels
TEAS = [
    ("FRESH",           "חליטה תאילנדית · היביסקוס וליים",       "fresh",        65, 33),
    ("FRESH  ללא סוכר", "חליטה תאילנדית · ללא תוספת סוכר",       "fresh_sf",     65, 33),
    ("DETOX",           "חליטה ישראלית · תה ירוק, לואיזה ונענע", "detox",        65, 33),
    ("DETOX  ללא סוכר", "חליטה ישראלית · ללא תוספת סוכר",        "detox_sf",     65, 33),
    ("ENERGY",          "חליטת שנגחאי · תה ירוק ולמון גראס",     "energy",       65, 33),
    ("CALM",            "חליטה צרפתית · קמומיל, תפוח וציפורן",   "calm",         65, 33),
    ("CONSCIOUSNESS",   "חליטה קוריאנית · יסמין וליצ׳י",         "conscious",    65, 33),
    ("REVIVE",          "חליטה יפנית · סנצ׳ה ופסיפלורה",         "revive",       65, 33),
    ("DESERTEA",        "חליטה מדברית · חמישה צמחי בר",          "desertea",     65, 33),
    ("NAMASTEA",        "חליטה הודית · צ׳אי מסאלה",              "namastea",     65, 33),
    ("AMERICAN",        "חליטה אמריקאית · תה שחור, יוזו והדרים", "american",     65, 33),
]

POWDERS = [
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · שקית 500 גרם",     "matcha",   590),
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · 22 שקיות 18 גרם",  None,       590),
    ("HOJICHA",         "מאצ׳ה שחורה קלויה · 500 גרם",          "hojicha",  375),
    ("UBE",             "אבקת שורש יאם סגול · 1 ק״ג",           "ube",      340),
    ("UBE",             "אבקת שורש יאם סגול · 500 גרם",         "ube",      175),
    ("MATCHA KIT",      "ערכת מאצ׳ה מלאה להכנה",                None,       170),
]

PUREES = [
    ("SMOOTHIE מנגו",  "מחית פרי 50% · 1 ליטר", "odk_man", 60),
    ("SMOOTHIE תות",   "מחית פרי 50% · 1 ליטר", "odk_str", 60),
    ("SMOOTHIE אפרסק", "מחית פרי 50% · 1 ליטר", "odk_pea", 60),
]

TOOLS = [
    ("קערת מאצ׳ה קרמית",     "צ׳אוואן מסורתי",      "bowl",    118),
    ("מקציף מאצ׳ה חשמלי",    "מקציף ידני נטען",     "frother", 100),
    ("מטרפת במבוק",          "צ׳אסן · 100 שיניים",  "whisk",    37),
    ("כוס זכוכית 600 מ״ל",   "כוס מדידה מחוסמת",    "beaker",   30),
    ("מעמד למטרפה",          "צ׳אסן טאטה",          "stand",    25),
    ("כוס מדידה",            "ג׳יגר מודפס",         "jigger",   20),
    ("כף מדידה במבוק",       "צ׳אשאקו",             "scoop",    11),
    ("בקבוק מאצ׳ה 500 מ״ל",  "בקבוק זכוכית כהה",    "bottle",   10),
]


# ─── assets ─────────────────────────────────────────────────────────────────
def b64(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def b64png(path, max_px, q=84):
    """Embed a cutout at print resolution, flattened onto the page colour.

    Two size levers, both invisible on the page: (1) a 24 mm tile at 300 dpi is
    284 px, so nothing above ~600 px survives; (2) every cutout sits on the flat
    paper colour, so its alpha channel buys nothing — compositing onto PAPER and
    saving JPEG replaces a ~350 KB lossless PNG with a ~30 KB JPEG per tile.
    The whole PDF drops from 11 MB to under 3."""
    import io
    from PIL import Image
    im = Image.open(path).convert('RGBA')
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    bg = Image.new('RGB', im.size, PAPER)
    bg.paste(im, (0, 0), im)
    buf = io.BytesIO(); bg.save(buf, 'JPEG', quality=q)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def b64jpg(path, q=88):
    import io
    from PIL import Image
    im = Image.open(path).convert('RGB')
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def font_face(name, weight, file):
    return (f"@font-face{{font-family:'{name}';font-style:normal;font-weight:{weight};"
            f"src:url({b64(HERE / 'fonts' / file, 'font/woff')}) format('woff');}}")


FONTS = "".join([
    font_face('Heebo', 300, 'heebo-400.woff'),
    font_face('Heebo', 500, 'heebo-500.woff'),
    font_face('Rubik', 400, 'rubik-400.woff'),
    font_face('Rubik', 500, 'rubik-500.woff'),
    font_face('Rubik', 600, 'rubik-600.woff'),
    font_face('Rubik', 700, 'rubik-700.woff'),
])

LOGO = b64(HERE / 'logo_b.png', 'image/png')          # gt mark, brand green
LOGO_K = b64(HERE / 'logo_a.png', 'image/png')        # gt mark, black


BAND_RATIO = 210 / 48          # page width : band height


def band_strip(src, y_frac, out, w=1700):
    """Full-width strip out of a photograph, top edge at `y_frac` of its height."""
    from PIL import Image
    im = Image.open(src).convert('RGB')
    W, H = im.size
    sh = int(W / BAND_RATIO)
    y = min(int(H * y_frac), H - sh)
    c = im.crop((0, y, W, y + sh)).resize((w, int(w / BAND_RATIO)), Image.LANCZOS)
    c.save(HERE / out, quality=92)
    return HERE / out


def tile(key):
    if key and (CUT / f't_{key}.png').exists():
        return f'<span class="tile"><img src="{b64png(CUT / f"t_{key}.png", 620)}" alt=""></span>'
    return f'<span class="tile tile--mark"><img src="{LOGO}" alt=""></span>'


def tile_pair(key):
    """1 L bottle with its 500 ml carafe standing beside it, shared baseline."""
    big = b64png(CUT / f't_{key}.png', 560)
    sml = b64png(CUT / f't_sm_{key}.png', 420)
    return (f'<span class="tile tile-pair"><img class="tb" src="{big}" alt="">'
            f'<img class="ts" src="{sml}" alt=""></span>')


def money(v):
    return f'<span class="p"><span class="cur">₪</span>{v}</span>'


def row(name, sub, key, prices, pair=False):
    t = tile_pair(key) if pair else tile(key)
    return (f'<div class="row">{t}'
            f'<span class="nm"><b>{name}</b><i>{sub}</i></span>'
            f'<span class="pp">{"".join(money(p) for p in prices)}</span></div>')


def section(kicker, title, note=''):
    return (f'<div class="sec"><span class="sec-t">{title}</span>'
            f'<span class="sec-k">{kicker}</span>'
            + (f'<span class="sec-n">{note}</span>' if note else '') + '</div>')


def band(img, kicker, title, note=''):
    return (f'<div class="band"><img src="{b64(img, "image/jpeg")}" alt="">'
            f'<div class="band-t"><span class="bk">{kicker}</span>'
            f'<span class="bt">{title}</span>'
            + (f'<span class="bn">{note}</span>' if note else '') + '</div></div>')


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
{FONTS}
@page{{size:A4;margin:0}}
html,body{{background:{PAPER}}}
body{{font-family:'Heebo',sans-serif;color:{INK};-webkit-font-smoothing:antialiased}}

.page{{position:relative;width:210mm;height:297mm;overflow:hidden;background:{PAPER};
       page-break-after:always;direction:rtl}}
.page:last-child{{page-break-after:auto}}

/* ── cover ───────────────────────────────────────────────────────────── */
.cover{{padding:0}}
.cover>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 100%}}
.cv{{position:absolute;inset:0;padding:33mm 22mm;display:flex;flex-direction:column;align-items:center;
     text-align:center}}
.cv .mark{{width:27mm;opacity:.94}}
.cv .hair{{width:14mm;height:.5px;background:{INK};opacity:.32;margin:9mm 0 8mm}}
.cv h1{{font-family:'Rubik',sans-serif;font-weight:600;font-size:29pt;line-height:1.14;letter-spacing:.015em}}
.cv .sub{{margin-top:5.5mm;font-weight:300;font-size:9.2pt;letter-spacing:.055em;color:{MUTED};line-height:1.9}}
.cv .tag{{margin-top:7mm;font-family:'Rubik',sans-serif;font-weight:500;font-size:8.2pt;letter-spacing:.20em;color:{CORAL}}}
.cv .yr{{margin-top:9mm;font-family:'Rubik',sans-serif;font-weight:500;font-size:10pt;letter-spacing:.36em;
         color:{INK};opacity:.5}}

/* ── page furniture ──────────────────────────────────────────────────── */
.foot{{position:absolute;bottom:9mm;right:17mm;left:17mm;display:flex;justify-content:space-between;
       align-items:center;font-size:6.8pt;letter-spacing:.14em;color:{MUTED}}}
.foot .mid{{display:flex;flex-direction:column;align-items:center;gap:1.4mm}}
.foot .mid img{{display:block;width:8.5mm;height:auto;opacity:.62}}
.foot .pg{{font-family:'Rubik',sans-serif;font-weight:500;font-size:6.4pt;letter-spacing:.26em;opacity:.85}}

/* ── opening band ────────────────────────────────────────────────────── */
.band{{position:relative;width:210mm;height:45mm;overflow:hidden;margin-bottom:5mm}}
.band img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.band::after{{content:'';position:absolute;inset:0;
  background:linear-gradient(to left,rgba(20,14,8,.68) 0%,rgba(20,14,8,.32) 46%,rgba(20,14,8,0) 78%)}}
.band-t{{position:absolute;right:17mm;bottom:8mm;z-index:2;text-align:right;color:#fff}}
.band-t .bk{{display:block;font-family:'Rubik',sans-serif;font-size:7pt;font-weight:500;letter-spacing:.30em;opacity:.85}}
.band-t .bt{{display:block;font-family:'Rubik',sans-serif;font-weight:600;font-size:18.5pt;letter-spacing:.02em;margin-top:1.5mm}}
.band-t .bn{{display:block;font-size:7.4pt;font-weight:300;letter-spacing:.05em;opacity:.8;margin-top:1.5mm}}

/* ── section head (in-page) ──────────────────────────────────────────── */
.body{{padding:0 17mm}}
.sec{{position:relative;padding-right:5mm;margin:6.5mm 0 3mm}}
.sec::before{{content:'';position:absolute;right:0;top:.8mm;bottom:.8mm;width:1.4px;background:{CORAL}}}
.sec-t{{display:block;font-family:'Rubik',sans-serif;font-weight:600;font-size:14pt;letter-spacing:.02em;color:{GREEN}}}
.sec-k{{display:block;font-family:'Rubik',sans-serif;font-size:6.6pt;font-weight:500;letter-spacing:.30em;color:{MUTED};margin-top:1mm}}

/* ── rows ────────────────────────────────────────────────────────────── */
.cols{{display:flex;align-items:flex-end;padding:0 0 1.6mm 0;border-bottom:.6px solid {RULE}}}
.cols .tile{{height:0}}
.cols .ch{{width:26mm;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;
           gap:1.1mm;font-family:'Rubik',sans-serif;font-size:6.6pt;font-weight:500;letter-spacing:.16em;color:{MUTED}}}
.row{{display:flex;align-items:center;gap:0;padding:1.05mm 0;border-bottom:.6px solid {RULE}}}
.row:last-child{{border-bottom:0}}

.tile{{flex:0 0 24mm;height:16.6mm;display:flex;align-items:flex-end;justify-content:center}}
.tile img{{max-width:100%;max-height:100%;object-fit:contain}}
.tile--mark{{align-items:center}}
.tile--mark img{{width:8.5mm;opacity:.16}}
.tile-pair{{gap:1mm}}
.tile-pair .tb{{height:100%;width:auto}}
.tile-pair .ts{{height:64%;width:auto}}

.nm{{flex:1 1 auto;padding-right:5mm;min-width:0}}
.nm b{{display:block;font-family:'Rubik',sans-serif;font-weight:500;font-size:10pt;letter-spacing:.04em;line-height:1.22}}
.nm i{{display:block;font-style:normal;font-weight:300;font-size:7.8pt;color:{MUTED};
       letter-spacing:.02em;margin-top:.7mm}}

.pp{{flex:0 0 auto;display:flex;direction:ltr}}
.p{{width:26mm;text-align:center;font-family:'Rubik',sans-serif;font-weight:600;font-size:13.5pt;line-height:1;
    font-variant-numeric:tabular-nums;white-space:nowrap}}
.p .cur{{font-size:8.5pt;font-weight:500;color:{CORAL};margin-right:.7mm;vertical-align:.1em}}

.note{{margin-top:6mm;font-size:7.2pt;font-weight:300;color:{MUTED};letter-spacing:.04em}}
.roomy .row{{padding:2.3mm 0}}
.roomy .tile{{flex-basis:26mm;height:18.5mm}}
"""


def page_cover():
    return f"""<div class="page cover">
  <img src="{b64jpg(HERE / 'src' / 'cover.png', 88)}" alt="">
  <div class="cv">
    <img class="mark" src="{LOGO_K}" alt="GT EVERYDAY">
    <span class="hair"></span>
    <h1>מחירון סיטונאי</h1>
    <span class="sub">תמציות תה · מאצ׳ה ואבקות<br>מחיות פרי · מוצרים משלימים</span>
    <span class="tag">כל המחירים ללא מע״מ</span>
    <span class="yr">2026</span>
  </div>
</div>"""


def furniture(n):
    return (f'<div class="foot"><span>כל המחירים ללא מע״מ</span>'
            f'<span class="mid"><img src="{LOGO}" alt="GT EVERYDAY">'
            f'<span class="pg">{n}</span></span>'
            f'<span>gteveryday.com · 054-398-2444</span></div>')


def build():
    # Page-top photographs — Tom's picks, folder CATALOG/2 slide (2026-08-06).
    b1 = band_strip(HERE / 'hd' / 'h14.png', 0.56, 'band1.jpg')   # bottles + drinks, terrace
    b2 = band_strip(HERE / 'pw' / 'p23.png', 0.42, 'band2.jpg')   # whisks · iced matcha · MATCHA bag
    b3 = band_strip(HERE / 'hd' / 'h12.png', 0.52, 'band3.jpg')   # travertine shelf

    # RTL flips flex order, so the price block reads [500 ml, 1 L] left to right
    # inside its own direction:ltr context — the headers must be built the same
    # way or they land over the wrong column. Above each label stands the bottle
    # it prices, so the size→price mapping is visible before any text is read.
    kb = b64png(CUT / 't_fresh.png', 200)
    ks = b64png(CUT / 't_sm_fresh.png', 160)
    hdr = ('<div class="cols"><span class="tile"></span><span class="nm"></span>'
           f'<span class="pp"><span class="ch"><img src="{ks}" style="height:5.4mm" alt="">'
           '<span>500 מ״ל</span></span>'
           f'<span class="ch"><img src="{kb}" style="height:8mm" alt="">'
           '<span>1 ליטר</span></span></span></div>')

    p1 = f"""<div class="page">{furniture('01')}
  {band(b1, 'TEA  EXTRACTS', 'תמציות תה', 'בקבוק אחד = 20–25 כוסות משקה')}
  <div class="body">
    {hdr}
    {''.join(row(n, s, k, [p5, p1_], pair=True) for n, s, k, p1_, p5 in TEAS)}
  </div></div>"""

    p2 = f"""<div class="page">{furniture('02')}
  {band(b2, 'MATCHA  ·  POWDERS', 'מאצ׳ה ואבקות')}
  <div class="body roomy">
    <div style="margin-top:-2mm"></div>
    {''.join(row(n, s, k, [p]) for n, s, k, p in POWDERS)}
    {section('FRUIT  PURÉES', 'מחיות פרי')}
    {''.join(row(n, s, k, [p]) for n, s, k, p in PUREES)}
  </div></div>"""

    p3 = f"""<div class="page">{furniture('03')}
  {band(b3, 'TOOLS  ·  SERVEWARE', 'מוצרים משלימים')}
  <div class="body roomy">
    {''.join(row(n, s, k, [p]) for n, s, k, p in TOOLS)}
  </div></div>"""

    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>GT Everyday — מחירון סיטונאי</title><style>{CSS}</style></head>'
            f'<body>{page_cover()}{p1}{p2}{p3}</body></html>')
    (HERE / 'pricelist.html').write_text(html, encoding='utf-8')
    print('pricelist.html', round((HERE / 'pricelist.html').stat().st_size / 1e6, 2), 'MB')
    print('rows', len(TEAS) + len(POWDERS) + len(PUREES) + len(TOOLS))


if __name__ == '__main__':
    build()
