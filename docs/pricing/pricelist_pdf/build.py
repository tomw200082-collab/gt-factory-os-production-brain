#!/usr/bin/env python3
"""GT Everyday — wholesale pricelist PDF. Direction ב ("המדף"), ex-VAT."""
import base64, os, json, datetime

D = os.path.dirname(os.path.abspath(__file__))

def b64(p, mime):
    with open(os.path.join(D, p), 'rb') as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

def img(name):
    p = f"assets/{name}.png"
    return b64(p, "image/png") if os.path.exists(os.path.join(D, p)) else None

FONT = {w: b64(f"fonts/heebo-{w}.woff", "font/woff") for w in (400, 500, 700, 900)}
FRANK = {w: b64(f"fonts/frank-{w}.woff", "font/woff") for w in (400, 500, 700)}
LOGO_W = b64("assets/logo-white.png", "image/png")
LOGO_B = b64("assets/logo-black.png", "image/png")

# ── data ─────────────────────────────────────────────────────────────────────
# price = ex-VAT, from the 2026-08-05 Shopify snapshot. AMERICAN + HOJICHA: Tom.
TEAS = [
    ("FRESH",         "חליטה תאילנדית · היביסקוס וליים",        "fresh",         65, 33),
    ("FRESH · ללא סוכר", "חליטה תאילנדית · ללא תוספת סוכר",     "fresh_sf",      65, 33),
    ("DETOX",         "חליטה ישראלית · תה ירוק, לואיזה ונענע",  "detox",         65, 33),
    ("DETOX · ללא סוכר", "חליטה ישראלית · ללא תוספת סוכר",      "detox_sf",      65, 33),
    ("ENERGY",        "חליטת שנגחאי · תה ירוק ולמון גראס",      "energy",        65, 33),
    ("CALM",          "חליטה צרפתית · קמומיל, תפוח וציפורן",    "calm",          65, 33),
    ("CONSCIOUSNESS", "חליטה קוריאנית · יסמין וליצ׳י",          "consciousness", 65, 33),
    ("REVIVE",        "חליטה יפנית · סנצ׳ה ופסיפלורה",          "revive",        65, 33),
    ("DESERTEA",      "חליטה מדברית · חמישה צמחי בר",           "desertea",      65, 33),
    ("NAMASTEA",      "חליטה הודית · צ׳אי מסאלה",               "namastea",      65, 33),
    ("AMERICAN",      "חליטה אמריקאית · תה שחור, יוזו והדרים",  None,            65, 33),
]

POWDERS = [
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · שקית 500 גרם",   "matcha500", 590),
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · 22 שקיות 18 גרם", "matcha22",  590),
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · שקית 50 גרם",     None,        65),
    ("GT ELITA",        "מאצ׳ה בפחית · 30 גרם",                None,        38),
    ("HOJICHA",         "מאצ׳ה שחורה קלויה · 500 גרם",         None,        375),
    ("UBE",             "אבקת שורש יאם סגול · 1 ק״ג",          "ube1kg",    340),
    ("UBE",             "אבקת שורש יאם סגול · 500 גרם",        None,        175),
    ("MATCHA KIT",      "ערכת מאצ׳ה מלאה להכנה",               None,        170),
]

PUREES = [
    ("SMOOTHIE מנגו",   "מחית פרי 50% · 1 ליטר", "odk_man", 60),
    ("SMOOTHIE תות",    "מחית פרי 50% · 1 ליטר", "odk_str", 60),
    ("SMOOTHIE אפרסק",  "מחית פרי 50% · 1 ליטר", "odk_pea", 60),
]

TOOLS = [
    ("קערת מאצ׳ה קרמית",     "צ׳אוואן מסורתי",             "bowl",     118),
    ("מקציף מאצ׳ה חשמלי",    "מקציף ידני נטען",            None,       100),
    ("מקציף קוקטיילים",      "מקציף מקצועי",               None,       75),
    ("מטרפת במבוק",          "צ׳אסן · 100 שיניים",         "whisk",    37),
    ("קנקן זכוכית עם מסננת", "קנקן נפוליטן",               None,       36),
    ("כוס זכוכית 600 מ״ל",   "כוס מדידה מחוסמת",           "glasspot", 30),
    ("מעמד למטרפה",          "צ׳אסן טאטה",                 "stand",    25),
    ("כוס מדידה",            "כוס מדידה מזכוכית",          None,       20),
    ("כף מדידה במבוק",       "צ׳אשאקו",                    "scoop",    11),
    ("בקבוק מאצ׳ה 500 מ״ל",  "בקבוק זכוכית כהה",           None,       10),
]

TODAY = "06.08.2026"

# ── helpers ──────────────────────────────────────────────────────────────────
def tile(key):
    src = img(key) if key else None
    if src:
        return f'<div class="tile"><img src="{src}" alt=""></div>'
    return f'<div class="tile tile--mark"><img src="{LOGO_B}" alt=""></div>'


def row(name, sub, key, prices):
    cells = "".join(f'<div class="p"><span class="cur">₪</span>{p}</div>' for p in prices)
    return f"""<div class="row">
      {tile(key)}
      <div class="nm"><h4>{name}</h4><p>{sub}</p></div>
      <div class="lead"></div>
      <div class="prices">{cells}</div>
    </div>"""


def section(num, title, kicker, rows_html, heads=None):
    h = ""
    if heads:
        h = '<div class="colhead">' + "".join(f"<span>{x}</span>" for x in heads) + "</div>"
    return f"""<section class="sec">
      <div class="sechead">
        <div class="sectitle"><span class="num">{num}</span><h3>{title}</h3></div>
        <span class="kicker">{kicker}</span>
      </div>
      {h}
      <div class="rows">{rows_html}</div>
    </section>"""


tea_rows = "".join(row(n, s, k, [a, b]) for n, s, k, a, b in TEAS)
pow_rows = "".join(row(n, s, k, [p]) for n, s, k, p in POWDERS)
pur_rows = "".join(row(n, s, k, [p]) for n, s, k, p in PUREES)
tool_rows = "".join(row(n, s, k, [p]) for n, s, k, p in TOOLS)

lineup = "".join(
    f'<img src="{img("cv_"+k)}" alt="">'
    for k in ["fresh", "detox", "energy", "calm", "consciousness", "revive"]
)

HTML = f"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<title>GT Everyday · מחירון סיטונאי</title>
<style>
@font-face{{font-family:Heebo;src:url({FONT[400]}) format('woff');font-weight:400}}
@font-face{{font-family:Heebo;src:url({FONT[500]}) format('woff');font-weight:500}}
@font-face{{font-family:Heebo;src:url({FONT[700]}) format('woff');font-weight:700}}
@font-face{{font-family:Heebo;src:url({FONT[900]}) format('woff');font-weight:900}}
@font-face{{font-family:Frank;src:url({FRANK[400]}) format('woff');font-weight:400}}
@font-face{{font-family:Frank;src:url({FRANK[500]}) format('woff');font-weight:500}}
@font-face{{font-family:Frank;src:url({FRANK[700]}) format('woff');font-weight:700}}

:root{{
  --ink:#14342F; --paper:#F7F4ED; --rule:#DDD6C7; --muted:#756E5D;
  --gold:#A8823C; --deep:#0E2622;
}}
*{{margin:0;padding:0;box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
@page{{size:A4;margin:0}}
html{{font-family:Heebo,sans-serif}}
body{{background:var(--paper);color:var(--ink)}}
.page{{width:210mm;height:297mm;position:relative;overflow:hidden;background:var(--paper);
  page-break-after:always;padding:16mm 15mm 14mm}}
.page:last-child{{page-break-after:auto}}

/* ── cover ── */
.cover{{background:var(--deep);color:#F7F4ED;padding:0;display:flex;flex-direction:column}}
.cover .frame{{position:absolute;inset:9mm;border:1px solid rgba(247,244,237,.16)}}
.cover .top{{padding:40mm 18mm 0;text-align:center;position:relative;z-index:2}}
.cover img.logo{{width:26mm;opacity:.97}}
.cover .eyebrow{{margin-top:11mm;font:500 8.5pt/1 Heebo;letter-spacing:.42em;
  color:rgba(247,244,237,.62)}}
.cover h1{{font:700 41pt/1.06 Frank;margin-top:6mm;letter-spacing:-.01em}}
.cover .sub{{margin-top:5mm;font:400 11pt/1.7 Heebo;color:rgba(247,244,237,.72);max-width:118mm;
  margin-inline:auto}}
.cover .vat{{margin-top:10mm;display:inline-block;border:1px solid rgba(168,130,60,.55);
  color:#D9B570;border-radius:999px;padding:2.6mm 7mm;font:700 10pt/1 Heebo;letter-spacing:.06em}}
.cover .shelf{{position:absolute;bottom:0;left:0;right:0;height:118mm;z-index:1}}
.cover .shelf .line{{position:absolute;bottom:29mm;left:9mm;right:9mm;height:1px;
  background:rgba(247,244,237,.22)}}
.cover .shelf .bottles{{position:absolute;bottom:29mm;left:0;right:0;display:flex;
  justify-content:center;align-items:flex-end;gap:1.5mm;padding:0 12mm}}
.cover .shelf img{{width:28.5mm;height:auto;object-fit:contain;object-position:bottom;
  filter:drop-shadow(0 2mm 3.5mm rgba(0,0,0,.5))}}
.cover .foot{{position:absolute;bottom:12mm;left:0;right:0;text-align:center;
  font:400 8pt/1 Heebo;letter-spacing:.28em;color:rgba(247,244,237,.5);z-index:2}}

/* ── content ── */
.masthead{{display:flex;align-items:baseline;justify-content:space-between;
  border-bottom:1.6px solid var(--ink);padding-bottom:3mm;margin-bottom:7mm}}
.masthead .mh-r{{font:700 13pt/1 Frank;letter-spacing:.01em}}
.masthead .mh-l{{font:500 7.6pt/1 Heebo;letter-spacing:.24em;color:var(--muted)}}

.sec{{margin-bottom:7mm}}
.sec:last-child{{margin-bottom:0}}
.sechead{{display:flex;align-items:baseline;justify-content:space-between;
  border-bottom:1px solid var(--ink);padding-bottom:1.8mm;margin-bottom:1mm}}
.sectitle{{display:flex;align-items:baseline;gap:3mm}}
.sectitle .num{{font:700 8pt/1 Heebo;color:var(--gold);letter-spacing:.1em}}
.sectitle h3{{font:700 14pt/1 Frank;letter-spacing:0}}
.kicker{{font:400 8pt/1 Heebo;color:var(--muted);letter-spacing:.14em}}

.colhead{{display:flex;justify-content:flex-end;gap:0;margin:1.6mm 0 .4mm}}
.colhead span{{width:23mm;text-align:center;font:500 7pt/1 Heebo;letter-spacing:.16em;
  color:var(--muted)}}

.row{{display:flex;align-items:center;gap:4.5mm;padding:2.45mm 0;
  border-bottom:.6px solid var(--rule)}}
.row:last-child{{border-bottom:none}}
.tile{{width:16mm;height:16mm;flex:0 0 16mm;display:flex;align-items:center;
  justify-content:center;background:#FFFDF8;border:.6px solid var(--rule);border-radius:50%;
  overflow:hidden}}
.tile img{{width:86%;height:86%;object-fit:contain}}
.tile--mark{{background:#F0EBE0;border-color:#E4DDCD}}
.tile--mark img{{width:46%;height:46%;opacity:.2}}
.nm{{min-width:0}}
.nm h4{{font:700 11pt/1.25 Heebo;letter-spacing:-.005em}}
.nm p{{font:400 8.4pt/1.35 Heebo;color:var(--muted);margin-top:.4mm}}
.lead{{flex:1;height:1px;border-bottom:.6px dotted #CFC7B4;margin:0 2mm;
  transform:translateY(3px)}}
.prices{{display:flex;gap:0}}
.p{{direction:ltr;width:23mm;text-align:center;font:700 15pt/1 Heebo;color:var(--ink);
  font-variant-numeric:tabular-nums;white-space:nowrap}}
.cur{{font-size:9.5pt;font-weight:500;color:var(--gold);margin-left:.7mm}}

.pagefoot{{position:absolute;bottom:9mm;left:15mm;right:15mm;display:flex;
  justify-content:space-between;align-items:center;border-top:.6px solid var(--rule);
  padding-top:2.2mm;font:400 7.4pt/1.5 Heebo;color:var(--muted)}}
.pagefoot b{{font-weight:700;color:var(--ink)}}
.pagefoot .pg{{font:500 7.4pt/1 Heebo;letter-spacing:.14em}}
</style></head><body>

<div class="page cover">
  <div class="frame"></div>
  <div class="top">
    <img class="logo" src="{LOGO_W}" alt="GT Everyday">
    <div class="eyebrow">מחירון סיטונאי</div>
    <h1>תמציות, מאצ׳ה<br>ומוצרים משלימים</h1>
    <div class="sub">בקבוק אחד של תמצית GT הוא 20–25 כוסות משקה.<br>
      כל המחירים בעמודים הבאים הם מחירי סיטונאות לבית עסק.</div>
    <div class="vat">כל המחירים ללא מע״מ</div>
  </div>
  <div class="shelf">
    <div class="bottles">{lineup}</div>
    <div class="line"></div>
  </div>
  <div class="foot">GTEVERYDAY.COM · {TODAY}</div>
</div>

<div class="page">
  <div class="masthead">
    <div class="mh-r">מחירון סיטונאי · GT Everyday</div>
    <div class="mh-l">כל המחירים בש״ח, ללא מע״מ</div>
  </div>
  {section("01", "תמציות תה", "בקבוק = 20–25 כוסות", tea_rows, ["1 ליטר", "500 מ״ל"])}
  <div class="pagefoot">
    <div>מחירי סיטונאות לבית עסק · <b>ללא מע״מ</b> · נכון ל־{TODAY}</div>
    <div class="pg">1 / 3</div>
  </div>
</div>

<div class="page">
  <div class="masthead">
    <div class="mh-r">מחירון סיטונאי · GT Everyday</div>
    <div class="mh-l">כל המחירים בש״ח, ללא מע״מ</div>
  </div>
  {section("02", "מאצ׳ה ואבקות", "יבוא ישיר", pow_rows)}
  {section("03", "מחיות פרי", "50% פרי", pur_rows)}
  <div class="pagefoot">
    <div>מחירי סיטונאות לבית עסק · <b>ללא מע״מ</b> · נכון ל־{TODAY}</div>
    <div class="pg">2 / 3</div>
  </div>
</div>

<div class="page">
  <div class="masthead">
    <div class="mh-r">מחירון סיטונאי · GT Everyday</div>
    <div class="mh-l">כל המחירים בש״ח, ללא מע״מ</div>
  </div>
  {section("04", "מוצרים משלימים", "כלי הכנה והגשה", tool_rows)}
  <div class="pagefoot">
    <div>להזמנות: <b>054-398-2444</b> · info@gteveryday.com · gteveryday.com</div>
    <div class="pg">3 / 3</div>
  </div>
</div>

</body></html>"""

open(os.path.join(D, "pricelist.html"), "w", encoding="utf-8").write(HTML)
n = len(TEAS) + len(POWDERS) + len(PUREES) + len(TOOLS)
missing = [r[0] + " · " + r[1] for r in TEAS if r[2] is None]
missing += [r[0] + " · " + r[1] for r in POWDERS if r[2] is None]
missing += [r[0] + " · " + r[1] for r in TOOLS if r[2] is None]
print(f"rows={n}  with-photo={n-len(missing)}  no-photo={len(missing)}")
for m in missing:
    print("   no photo:", m)
