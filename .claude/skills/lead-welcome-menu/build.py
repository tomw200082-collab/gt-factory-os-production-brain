#!/usr/bin/env python3
"""
Render the GT lead-welcome menu to lead-menu.html.

    python3 build.py && python3 shot.py

Reads every figure from drinks_final_figures.json at build time and asserts the
twelve keys resolve to the approved values. On any mismatch it HALTS with
contract_failure — it does not "fix" either side. Derived spans (profit range,
margin range) are recomputed here and never hardcoded.
"""

import json
import re
import sys
from pathlib import Path

D = Path(__file__).parent
FIGURES = D.parent / "drinks-pricelist" / "drinks_final_figures.json"
FONTS = (D.parent.parent.parent / "docs/pricing/pricelist_pdf/fonts").resolve()
OUT = D / "lead-menu.html"

# ---------------------------------------------------------------- the contract
# Human-readable copy of the approved figures, masterprompt §2.2. build.py
# asserts the figures file against this; it is a tripwire, not a source.
EXPECTED = {
    "8":  ("₪3.76", "₪19", "77%", "₪12.34"),
    "23": ("₪3.25", "₪24", "84%", "₪17.09"),
    "27": ("₪3.62", "₪22", "81%", "₪15.02"),
    "12": ("₪3.76*", "₪19", "77%", "₪12.34"),
    "21": ("₪5.41", "₪24", "73%", "₪14.93"),
    "48": ("₪5.00", "₪24", "75%", "₪15.34"),
    "49": ("₪3.80", "₪24", "81%", "₪16.54"),
    "55": ("₪3.95", "₪28", "83%", "₪19.78"),
    "29": ("₪3.77", "₪26", "83%", "₪18.26"),
    "34": ("₪3.35", "₪26", "85%", "₪18.68"),
    "31": ("₪6.17", "₪26", "72%", "₪15.86"),
    "33": ("₪6.37", "₪26", "71%", "₪15.66"),
}

# The drinks catalog DAHPi9gpfts marks eleven of the twelve with the garnish/foam
# asterisk; key 8 is the only one without. Carried exactly as the catalog has it.
NO_ASTERISK = {"8"}

PRODUCTS = [
    dict(key="fresh", latin="FRESH", he="חליטה תאילנדית", hue="--hue-fresh",
         ingredients="פרחי היביסקוס ולײם",
         blurb="משקה מעורר ללא קפאין. צבע אדום עז, בולט ומסקרן. טעם חמצמץ עדין שמחזיר לקוחות שוב ושוב.",
         shot="assets/bottle-fresh.png", glass="assets/glass-fresh.jpg",
         drinks=["8", "23", "27"], hero="23"),
    dict(key="detox", latin="DETOX", he="חליטה ישראלית", hue="--hue-detox",
         ingredients="תה ירוק, לואיזה, נענע ולײם",
         blurb="טעם קליל ומרענן שלקוחות אוהבים בכל גיל. נרטיב בריאות ברור שכולם מתחברים אליו ומבינים.",
         shot="assets/bottle-detox.png", glass="assets/glass-detox.jpg",
         drinks=["12", "21"], hero="21"),
    dict(key="namastea", latin="NAMASTEA", he="חליטה הודית", hue="--hue-namastea",
         ingredients="שני זני תה שחור, קינמון, הל, ג׳ינג׳ר, פלפל שחור, ציפורן",
         blurb="להיט מכירות ענק בקרב הקהל הישראלי. נפלא כמשקה קר — גם עם מי קוקוס. נפלא כמשקה חם — גם כלאטה.",
         shot="assets/bottle-namastea.png", glass="assets/glass-namastea.jpg",
         drinks=["48", "49", "55"], hero="55"),
    dict(key="matcha", latin="MATCHA", he="מאצ׳ה טקסית שיזואוקה", hue="--hue-matcha",
         ingredients="תה ירוק",
         blurb="לא טרנד חולף — המאצ׳ה כאן כדי להישאר. מייבאים היישר מהחקלאים, בהטסה מרגע הקטיפה — כך נשמרות הטריות והאיכות.",
         shot=None, glass=None,
         drinks=["29", "34", "31", "33"], hero="34"),
]

# Names, descriptors, preparation and ingredient panels — all verbatim from the
# drink's own page in the Canva drinks catalog DAHPi9gpfts.
DRINKS = {
    "8":  dict(name="חליטת היביסקוס וליים", desc="חליטת היביסקוס וליים קרה או מוגזת, עם סלייס לימון ונענע",
               steps=["מלאו כוס בקרח", "הוסיפו 50 מ״ל תרכיז GT",
                      "השלימו ל־⅔ במים קרים (או סודה למוגז)", "קשטו: סלייס לימון · נענע טריה"],
               panel=["קרח", "50 מ״ל תרכיז GT", "סלייס לימון", "עשבי קישוט"]),
    "23": dict(name="חליטת תפוח היביסקוס", desc="",
               steps=["מלאו כוס בקרח", "הוסיפו 40 מ״ל מיץ תפוחים", "הוסיפו 40 מ״ל תרכיז GT",
                      "השלימו ל־⅔ במים", "קשטו בגרניש לפי טעם"],
               panel=["קרח", "40 מ״ל מיץ תפוחים", "40 מ״ל תרכיז GT", "גרניש"]),
    "27": dict(name="גזוז היביסקוס ותפוח", desc="",
               steps=["מלאו כוס בקרח", "הוסיפו 40 מ״ל מיץ תפוחים", "הוסיפו 40 מ״ל תרכיז GT",
                      "השלימו ל־⅔ בסודה (~150 מ״ל)", "קשטו: גרניש לפי טעם"],
               panel=["קרח", "40 מ״ל מיץ תפוחים", "40 מ״ל תרכיז GT", "~150 מ״ל סודה", "גרניש לפי טעם"]),
    "12": dict(name="חליטת תה ירוק וליים", desc="תה ירוק, לואיזה, נענע וליים",
               steps=["מלאו כוס בקרח", "הוסיפו 50 מ״ל תרכיז GT",
                      "השלימו ל־⅔ במים קרים (או סודה למוגז)", "קשטו: סלייס לימון · נענע טריה"],
               panel=["קרח", "50 מ״ל תרכיז GT", "סלייס לימון", "עשבי קישוט"]),
    "21": dict(name="חליטת תות לואיזה", desc="משקה דגל על בסיס מחית תות",
               steps=["מלאו כוס בקרח", "הוסיפו 40 מ״ל מחית תות", "הוסיפו 40 מ״ל תרכיז GT",
                      "השלימו ל־⅔ במים", "קשטו בגרניש לפי טעם"],
               panel=["קרח", "40 מ״ל מחית תות", "40 מ״ל תרכיז GT", "גרניש"]),
    "48": dict(name="אייס צ׳אי מסאלה קלאסי", desc="צ׳אי מסאלה עשיר עם קצף חלב ואבקת קינמון",
               steps=["מלאו כוס בקרח", "השלימו ל־⅔ בחלב או תחליפי חלב", "יצקו 50 מ״ל תרכיז מסאלה GT",
                      "הוסיפו קצף חלב", "פזרו אבקת קינמון מלמעלה"],
               panel=["קרח", "⅔ כוס חלב", "50 מ״ל מסאלה GT", "70 מ״ל קצף חלב", "קינמון"]),
    "49": dict(name="צ׳אי מסאלה על הקרח", desc="צ׳אי מסאלה קליל, על בסיס מים ומרענן",
               steps=["מלאו כוס בקרח", "השלימו ל־⅔ במים", "יצקו 50 מ״ל תרכיז מסאלה GT",
                      "הוסיפו הרבה קצף חלב"],
               panel=["קרח", "⅔ כוס מים", "50 מ״ל מסאלה GT", "70 מ״ל קצף חלב"]),
    "55": dict(name="צ׳אי מסאלה קולד פואם וניל", desc="צ׳אי מסאלה עם קצף קר חלבי בטעם וניל",
               steps=["מלאו כוס בקרח", "השלימו ל־⅔ במים", "יצקו 50 מ״ל תרכיז מסאלה GT",
                      "הכתירו בקצף קר חלבי עם תמצית וניל", "קשטו במקל וניל"],
               panel=["קרח", "⅔ כוס מים", "50 מ״ל מסאלה GT", "70 מ״ל קצף קר חלבי", "תמצית וניל"]),
    "29": dict(name="אייס מאצ׳ה קלאסי", desc="קלאסי מאצ׳ה אייס",
               steps=["מלאו כוס בקרח", "השלימו ל־⅔ בחלב או תחליפי חלב",
                      "יצקו 50 מ״ל תרכיז מאצ׳ה (1.8 גר׳)", "הוסיפו קצף חלב מלמעלה"],
               panel=["קרח", "⅔ כוס חלב", "50 מ״ל מאצ׳ה (1.8 גר׳)", "70 מ״ל קצף חלב"]),
    "34": dict(name="מאצ׳ה אגבה על הקרח", desc="אגבה מאצ׳ה אייס, קליל על הקרח",
               steps=["מלאו כוס בקרח", "הוסיפו 15 מ״ל סירופ אגבה", "השלימו ל־⅔ במים",
                      "יצקו 50 מ״ל תרכיז מאצ׳ה (1.8 גר׳)", "הוסיפו קצף חלב מלמעלה"],
               panel=["קרח", "⅔ כוס מים", "15 מ״ל סירופ אגבה", "50 מ״ל מאצ׳ה (1.8 גר׳)", "70 מ״ל קצף חלב"]),
    "31": dict(name="אייס מאצ׳ה תות", desc="אייס מאצ׳ה מחית תות",
               steps=["מלאו כוס בקרח", "הוסיפו 40 מ״ל מחית תות", "השלימו ל־⅔ בחלב או תחליפי חלב",
                      "יצקו 50 מ״ל תרכיז מאצ׳ה (1.8 גר׳)", "הוסיפו קצף חלב מלמעלה"],
               panel=["קרח", "40 מ״ל מחית תות", "⅔ כוס חלב", "50 מ״ל מאצ׳ה (1.8 גר׳)", "70 מ״ל קצף חלב"]),
    "33": dict(name="אייס מאצ׳ה מסאלה", desc="מאצ׳ה אייס תמצית מסאלה GT",
               steps=["מלאו כוס בקרח", "הוסיפו 40 מ״ל תמצית מסאלה GT", "השלימו ל־⅔ בחלב או תחליפי חלב",
                      "יצקו 50 מ״ל תרכיז מאצ׳ה (1.8 גר׳)", "הוסיפו קצף חלב מלמעלה"],
               panel=["קרח", "40 מ״ל תמצית מסאלה GT", "⅔ כוס חלב", "50 מ״ל מאצ׳ה (1.8 גר׳)", "70 מ״ל קצף חלב"]),
}


# ------------------------------------------------------------------ the gate
def load_figures():
    if not FIGURES.is_file():
        sys.exit(f"contract_failure: {FIGURES} missing")
    pages = json.load(FIGURES.open())["pages"]
    out, bad = {}, []
    for k, exp in EXPECTED.items():
        if k not in pages:
            bad.append(f"  key {k}: absent from the figures file")
            continue
        v = pages[k]
        got = (v["cost"], v["price"], v["marg"], v["prof"].replace(" לכוס", ""))
        if got != exp:
            bad.append(f"  key {k}: figures file {got} != approved {exp}")
        cost = v["cost"].rstrip("*")
        out[k] = dict(cost=cost, price=v["price"], marg=v["marg"],
                      prof=v["prof"].replace(" לכוס", ""),
                      star="" if k in NO_ASTERISK else "*")
    if bad:
        sys.exit("contract_failure: the approved figures changed. HALT — do not adapt.\n"
                 + "\n".join(bad))
    return out


def derived(fig):
    """Recomputed every build. Never hardcoded — masterprompt §2.2."""
    profs = [float(f["prof"].lstrip("₪")) for f in fig.values()]
    margs = [int(f["marg"].rstrip("%")) for f in fig.values()]
    return dict(prof_lo=f"₪{min(profs):.2f}", prof_hi=f"₪{max(profs):.2f}",
                marg_lo=f"{min(margs)}%", marg_hi=f"{max(margs)}%",
                n_products=len(PRODUCTS), n_drinks=len(EXPECTED))


# ------------------------------------------------------------------- helpers
def num(s):
    """Latin/figure token. Landmine 11: without the isolate, ₪12.34 can render
    12.34₪ or reorder its digits, which ships a wrong number."""
    return f'<span class="num">{s}</span>'


def figures_row(f):
    """Hero screens only. Profit is absent here on purpose — it is the 180px figure
    directly above, and printing it twice crowded the number and said nothing."""
    return f'''<div class="figs">
      <div class="fig"><div class="cap">FOOD COST</div><div class="val cost">{num(f["cost"] + f["star"])}</div></div>
      <div class="fig"><div class="cap">מחיר מומלץ</div><div class="val">{num(f["price"])}</div></div>
      <div class="fig"><div class="cap">שוליים</div><div class="val">{num(f["marg"])}</div></div>
    </div>'''


def drink_block(k, fig):
    d, f = DRINKS[k], fig[k]
    panel = " · ".join(re.sub(r"(\d[\d.,]*)", r'<span class="num">\1</span>', x) for x in d["panel"])
    return f'''<div class="drink">
      <div class="drow">
        <div class="dname">{d["name"]}</div>
        <div class="dprofit"><div class="cap">רווח לכוס</div>
          <div class="val profit">{num(f["prof"])}</div></div>
      </div>
      <div class="mini">
        <span><i>FOOD COST</i>{num(f["cost"] + f["star"])}</span>
        <span><i>מחיר מומלץ</i>{num(f["price"])}</span>
        <span><i>שוליים</i>{num(f["marg"])}</span>
      </div>
      <div class="panel">{panel}</div>
    </div>'''


# ------------------------------------------------- Movement 4: the one diagram
def mapping_svg(fig):
    """Four coloured spine segments on one axis, twelve drinks hanging off it,
    and exactly one curve that leaves the axis and re-enters it higher up.

    Not a link diagram. Eleven of the twelve drinks belong to a single product,
    so eleven parallel lines would be noise pretending to be information. Drawn
    this way the single crossing — אייס מאצ׳ה מסאלה reaching back to NAMASTEA —
    is the only thing on the right of the axis, so it reads as intent.
    Hand-authored. No chart library."""
    X, W = 838, 904
    y, secs, parts = 24, {}, []
    for p in PRODUCTS:
        top = y
        parts.append(f'<text x="812" y="{y+50}" class="m-prod" fill="var({p["hue"]})">{p["latin"]}</text>')
        y += 50 + 30
        for k in p["drinks"]:
            parts.append(f'<line x1="792" y1="{y-13}" x2="{X}" y2="{y-13}" class="m-tick"/>')
            parts.append(f'<circle cx="{X}" cy="{y-13}" r="7" fill="var({p["hue"]})"/>')
            parts.append(f'<text x="778" y="{y}" class="m-drink">{DRINKS[k]["name"]}</text>')
            secs[k] = y - 13
            y += 62
        parts.insert(0, f'<line x1="{X}" y1="{top+14}" x2="{X}" y2="{y-52}" '
                        f'stroke="var({p["hue"]})" stroke-width="5"/>')
        secs[p["key"]] = ((top + 14) + (y - 52)) / 2
        y += 46
    cross = (f'<path d="M {X},{secs["33"]} C 902,{secs["33"]} 902,{secs["namastea"]} '
             f'{X},{secs["namastea"]}" class="m-cross"/>'
             f'<circle cx="{X}" cy="{secs["namastea"]}" r="7" fill="var(--hue-namastea)"/>')
    return (f'<svg viewBox="0 0 {W} {y}" width="{W}" class="mapsvg" direction="ltr" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}{cross}</svg>')


DOWN = ('<svg class="down" viewBox="0 0 26 76" width="26" height="76" aria-hidden="true">'
        '<path d="M13 0 V68 M3 55 L13 68 L23 55" fill="none" stroke="var(--coral)" '
        'stroke-width="3.5" stroke-linecap="square"/></svg>')


# ------------------------------------------------------------------------ CSS
def css():
    faces = "".join(
        f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;"
        f"src:url('{(FONTS / f'{fam.lower()}-{w}.woff').as_uri()}') format('woff');}}"
        for fam, w in [("Rubik", 400), ("Rubik", 500), ("Rubik", 600), ("Rubik", 700),
                       ("Heebo", 400), ("Heebo", 500), ("Heebo", 700), ("Heebo", 900)])
    return faces + """
@page { size: 1080px 1920px; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
html { direction: rtl; }
body { background: var(--paper); color: var(--ink);
       font-family:'Heebo',sans-serif; font-weight:400;
       -webkit-font-smoothing:antialiased; }

.screen { position:relative; width:1080px; height:1920px; overflow:hidden;
          background:var(--paper); page-break-after:always; break-after:page;
          padding:96px 88px 168px 88px; }
.screen:last-child { page-break-after:auto; break-after:auto; }

/* the running footer — the deck's name and screen number do the job a repeated
   logo would do badly */
.foot { position:absolute; inset:auto 88px 56px 88px; display:flex;
        justify-content:space-between; font-size:36px; color:var(--muted);
        letter-spacing:.04em; }
.foot .num { color:var(--muted); }

.num { direction:ltr; unicode-bidi:isolate; font-variant-numeric:tabular-nums; }

h1,h2,.dname,.prod,.figbig,.cover-h { font-family:'Rubik',sans-serif; line-height:1.08; }
.kick { font-family:'Rubik',sans-serif; font-weight:600; font-size:40px;
        letter-spacing:.18em; color:var(--muted); }
h2 { font-size:88px; font-weight:700; margin-bottom:40px; }
.lead { font-size:48px; line-height:1.5; color:var(--ink); max-width:904px; }
.body { font-size:42px; line-height:1.5; }
.rule { height:1px; background:var(--line); border:0; margin:20px 0; }

/* ---- cover ---- */
.cover { display:flex; flex-direction:column; justify-content:space-between; }
.cover-logo { width:190px; }
.cover-h { font-size:150px; font-weight:700; letter-spacing:-.02em; }
.cover-h em { font-style:normal; color:var(--coral); }
.cover-vision { font-size:48px; color:var(--muted); margin-top:40px; }
.cover-bottles { display:flex; align-items:flex-end; justify-content:space-between; gap:0;
                 flex:0 0 560px; height:560px; padding:0 10px; }
.cover-bottles img { height:100%; width:auto; max-width:31%; object-fit:contain; }
.prow { display:flex; justify-content:space-between; font-family:'Rubik',sans-serif;
        font-weight:600; font-size:40px; letter-spacing:.14em; }
.prow span { display:flex; align-items:center; gap:16px; }
.prow i { width:22px; height:22px; border-radius:50%; display:inline-block; }

/* ---- promise ---- */
.big { font-family:'Rubik',sans-serif; font-weight:700; font-size:130px; line-height:1.02;
       white-space:nowrap; }
.claim { display:flex; gap:56px; font-size:36px; color:var(--muted); flex-wrap:wrap; }

/* ---- mapping ---- */
.mapsvg { display:block; margin:0 auto; }
.arw { vertical-align:-2px; margin:0 12px; }
.m-prod { font-family:'Rubik',sans-serif; font-weight:700; font-size:56px;
          letter-spacing:.14em; text-anchor:end; }
.m-drink { font-family:'Heebo',sans-serif; font-size:42px; fill:var(--ink); text-anchor:end; }
.m-tick { stroke:var(--line); stroke-width:2; }
.m-cross { fill:none; stroke:var(--hue-matcha); stroke-width:3; }

/* ---- product screens ---- */
.prod { font-size:130px; font-weight:700; letter-spacing:.06em; line-height:1; }
.prodsub { font-size:42px; color:var(--muted); margin-top:16px; }
.shot { position:absolute; left:-56px; top:108px; height:560px; }
.prodhead { max-width:600px; min-height:510px; }
.prodhead.wide { max-width:904px; min-height:0; }
.dense .prod { font-size:110px; }
.dense .blurb { font-size:38px; line-height:1.3; margin-top:12px; }
.dense .drink { padding:0; }
.dense .mini { margin-top:2px; }
.dense .panel { margin-top:2px; }
.dense .dprofit .val { font-size:64px; margin-top:0; }
.dense .rule { margin:12px 0; }
.dense .dprofit .val { font-size:64px; }

.drink { padding:9px 0; border-bottom:1px solid var(--line); }
.drink:last-of-type { border-bottom:0; }
.drow { display:flex; align-items:baseline; justify-content:space-between; gap:32px; }

.dname { font-size:52px; font-weight:600; flex:1 1 auto; }
.dprofit { text-align:left; flex:0 0 auto; }
.dprofit .cap { font-family:'Rubik',sans-serif; font-weight:600; font-size:36px;
                letter-spacing:.1em; color:var(--muted); }
.dprofit .val { font-family:'Rubik',sans-serif; font-weight:700; font-size:70px;
                line-height:1; margin-top:4px; }
.dprofit .val.profit { color:var(--profit); }
.panel { font-size:36px; color:var(--muted); line-height:1.26; margin-top:6px; }
.mini { display:flex; gap:52px; margin-top:8px; }
.mini span { display:flex; flex-direction:column; align-items:flex-start;
             font-family:'Rubik',sans-serif; font-weight:700; font-size:44px; }
.mini i { font-style:normal; font-weight:600; font-size:36px; letter-spacing:.08em;
          color:var(--muted); margin-bottom:2px; }
.mini span:first-child { color:var(--cost); }
.figs { display:flex; gap:56px; margin-top:28px; }
.fig .cap { font-family:'Rubik',sans-serif; font-weight:600; font-size:36px;
            letter-spacing:.1em; color:var(--muted); }
.fig .val { font-family:'Rubik',sans-serif; font-weight:700; font-size:72px; margin-top:8px; }
.fig .val.cost { color:var(--cost); }
.blurb { font-size:42px; line-height:1.4; color:var(--ink); margin-top:22px; max-width:600px; }
.prodhead.wide .blurb { max-width:904px; }
.flow { display:flex; flex-direction:column; align-items:flex-start; gap:12px; }
.down { display:block; margin-right:40px; }
.legal { font-size:30px; color:var(--muted); }

/* ---- hero screens ---- */
.hero { padding:0; color:var(--paper); }
.hero .bg { position:absolute; top:0; left:0; width:1080px; height:1920px;
            background-size:cover; background-position:center; }
.hero .scrim { position:absolute; top:0; left:0; width:1080px; height:1920px;
   background:linear-gradient(180deg, rgba(20,14,10,.72) 0%, rgba(20,14,10,.30) 34%,
                              rgba(20,14,10,.62) 66%, rgba(20,14,10,.92) 100%); }
.hero .inner { position:absolute; top:96px; right:88px; bottom:168px; left:88px;
               display:flex; flex-direction:column; justify-content:space-between; }
.hero .plate { margin:0 -88px; padding:56px 88px 64px;
   background:linear-gradient(180deg, rgba(16,11,7,0) 0%, rgba(16,11,7,.74) 22%,
                              rgba(16,11,7,.74) 78%, rgba(16,11,7,0) 100%); }
.hero .kick, .hero .fig .cap { color:rgba(239,230,214,.72); }
.hero .dname { font-size:88px; }
.hero .ddesc { color:rgba(239,230,214,.80); }
.hero .fig .val { color:var(--paper); }
.hero .fig .val.cost, .hero .fig .val.profit { color:var(--paper); }
.hero .steps { font-size:42px; line-height:1.5; }
.hero .steps li { list-style:none; display:flex; gap:24px; padding:10px 0; }
.hero .steps b { font-family:'Rubik',sans-serif; font-weight:700;
                 color:var(--coral); min-width:44px; }
.herofig { font-family:'Rubik',sans-serif; font-weight:700; font-size:180px; line-height:1; }
.hero .foot { color:rgba(239,230,214,.62); }
.hero .foot .num { color:rgba(239,230,214,.62); }

/* matcha hero — no photograph exists, so typography and the hue carry it */
.hero.typo .bg { background:var(--hue-matcha); }
.hero.typo .scrim { background:linear-gradient(180deg, rgba(28,34,12,.55) 0%,
                    rgba(28,34,12,.20) 40%, rgba(28,34,12,.80) 100%); }

/* ---- lists ---- */
.olist { margin-top:16px; }
.olist li { list-style:none; padding:28px 0; border-bottom:1px solid var(--line);
            display:flex; gap:28px; align-items:baseline; }
.olist li:last-child { border-bottom:0; }
.olist .nm { font-family:'Rubik',sans-serif; font-weight:700; font-size:52px;
             letter-spacing:.08em; min-width:290px; }
.olist .role { font-size:38px; color:var(--muted); }
.have { display:flex; flex-wrap:wrap; gap:20px 28px; margin-top:40px; }
.have span { font-size:48px; padding:14px 30px; border:1px solid var(--line); border-radius:999px; }

/* ---- closing ---- */
.close { display:flex; flex-direction:column; justify-content:center; }
.promise { font-family:'Rubik',sans-serif; font-weight:700; font-size:150px;
           line-height:1.05; letter-spacing:-.01em; }
.promise-sub { font-size:48px; color:var(--muted); margin-top:40px; max-width:820px; line-height:1.5; }
.contact { margin-top:96px; font-size:42px; line-height:1.7; }
.contact a { color:var(--ink); text-decoration:none; }
.signoff { margin-top:96px; font-size:42px; color:var(--muted); }
.close-logo { width:170px; margin-top:64px; }
"""


# --------------------------------------------------------------- the screens
def foot(n, dark=False):
    return (f'<div class="foot"><span>תפריט הפתיחה · GT</span>'
            f'<span class="num">{n:02d} / 15</span></div>')


def screen(n, body, cls=""):
    return f'<section class="screen {cls}">{body}{foot(n)}</section>\n'


def product_screen(n, p, fig):
    dense = " dense" if len(p["drinks"]) > 3 else ""
    if p["shot"]:
        art = f'<img class="shot" src="{p["shot"]}" alt="">'
    else:
        # No Tom-approved MATCHA packshot exists (masterprompt §2.4, §6.A).
        # A typographic placeholder, never a borrowed or stock image.
        art = ""
    blocks = "".join(drink_block(k, fig) for k in p["drinks"])
    star = ('<div class="legal">* כולל הערכת עלות גרניש/קצף</div>'
            if any(fig[k]["star"] for k in p["drinks"]) else "")
    return screen(n, f'''{art}
      <div class="prodhead{"" if p["shot"] else " wide"}">
        <div class="prod" style="color:var({p["hue"]})">{p["latin"]}</div>
        <div class="prodsub">{p["he"]} · {p["ingredients"]}</div>
        <p class="blurb">{p["blurb"]}</p>
      </div>
      <hr class="rule" style="background:var({p["hue"]});height:3px">
      {blocks}
      {star}''', dense.strip())


def hero_screen(n, p, fig):
    k = p["hero"]; d, f = DRINKS[k], fig[k]
    bg = (f'<div class="bg" style="background-image:url({p["glass"]})"></div>'
          if p["glass"] else '<div class="bg"></div>')
    steps = "".join(f'<li><b>{i}</b><span>{s}</span></li>' for i, s in enumerate(d["steps"], 1))
    desc = f'<div class="ddesc" style="margin-top:16px">{d["desc"]}</div>' if d["desc"] else ""
    cls = "hero" + ("" if p["glass"] else " typo")
    return screen(n, f'''{bg}<div class="scrim"></div>
      <div class="inner">
        <div>
          <div class="kick">{p["latin"]}</div>
          <div class="dname" style="margin-top:24px">{d["name"]}</div>{desc}
        </div>
        <div class="plate">
          <div class="kick">רווח לכוס</div>
          <div class="herofig">{num(f["prof"])}</div>
          {figures_row(f)}
          <div class="legal" style="color:rgba(239,230,214,.62);margin-top:16px">
            {"* כולל הערכת עלות גרניש/קצף" if f["star"] else "&nbsp;"}</div>
        </div>
        <ul class="steps">{steps}</ul>
      </div>''', cls)


def html(fig):
    D_ = derived(fig)
    s = []
    # S01 cover
    s.append(screen(1, f'''
      <div style="display:flex;flex-direction:column;height:100%;justify-content:space-between">
        <div>
          <img class="cover-logo" src="assets/gt-logo-black.png" alt="GT">
          <div class="kick" style="margin-top:96px">תפריט הפתיחה</div>
          <h1 class="cover-h" style="margin-top:24px">ארבע תמציות.<br>
            <span class="num">{D_["n_drinks"]}</span> משקאות.<br><em>תפריט רווחי.</em></h1>
          <div class="cover-vision">המשקה הטוב יותר, הבחירה הקלה, לכולם.</div>
        </div>
        <div class="cover-bottles">
          <img src="assets/bottle-namastea.png" alt=""><img src="assets/bottle-detox.png" alt=""><img src="assets/bottle-fresh.png" alt="">
        </div>
        <div class="prow">''' + "".join(
            f'<span><i style="background:var({p["hue"]})"></i>{p["latin"]}</span>' for p in PRODUCTS
        ) + '</div></div>', "cover"))

    # S02 the promise
    s.append(screen(2, f'''
      <div class="kick">ההבטחה</div>
      <h2 style="margin-top:24px">מארבעה מוצרים,<br>תפריט שלם.</h2>
      <div class="flow" style="margin-top:48px">
        <div class="big"><span class="num">{D_["n_products"]}</span> מוצרים</div>
        {DOWN}
        <div class="big" style="color:var(--green)"><span class="num">{D_["n_drinks"]}</span> משקאות</div>
      </div>
      <hr class="rule" style="margin-top:56px">
      <div style="margin-top:32px">
        <div class="kick">רווח לכוס</div>
        <div class="figbig" style="font-size:96px;font-weight:700;color:var(--profit);margin-top:8px">
          {num(D_["prof_lo"])}–{num(D_["prof_hi"])}</div>
        <div class="kick" style="margin-top:32px">שוליים</div>
        <div class="figbig" style="font-size:96px;font-weight:700;margin-top:8px">
          {num(D_["marg_lo"])}–{num(D_["marg_hi"])}</div>
      </div>
      <hr class="rule" style="margin-top:64px">
      <div class="lead" style="margin-top:24px"><span class="num">20–25</span> כוסות מכל בקבוק.</div>
      <div class="claim" style="margin-top:64px">
        <span>ללא חומרים משמרים</span><span>ללא צבעי מאכל</span><span>ללא תמציות טעם</span></div>
      <div class="body" style="margin-top:28px;color:var(--muted)">
        <span class="num">17</span> קק״ל ל־<span class="num">100</span> מ״ל מוכן</div>'''))

    # S03 the mapping — the screen the deck is built around
    s.append(screen(3, f'''
      <div class="kick">המיפוי</div>
      <h2 style="margin-top:24px">מאיזה מוצר<br>מיוצר כל משקה</h2>
      {mapping_svg(fig)}
      <div class="body" style="color:var(--muted);margin-top:24px">
        משקה אחד בלבד מחבר שני מוצרים.</div>'''))

    # S04 how it is made
    s.append(screen(4, '''
      <div class="kick">פשוט להגיש</div>
      <h2 style="margin-top:24px">כוס מושלמת<br>בשלוש תנועות</h2>
      <ul class="olist" style="margin-top:64px">
        <li><span class="nm" style="min-width:110px;color:var(--coral)"><span class="num">1</span></span>
            <span class="lead">מלאו כוס בקרח.</span></li>
        <li><span class="nm" style="min-width:110px;color:var(--coral)"><span class="num">2</span></span>
            <span class="lead">השלימו במים קרים.</span></li>
        <li><span class="nm" style="min-width:110px;color:var(--coral)"><span class="num">3</span></span>
            <span class="lead">הוסיפו את תרכיז GT, ערבבו קלות, סיימו בפרוסת לימון או נענע טרייה — והגישו.</span></li>
      </ul>
      <hr class="rule" style="margin-top:64px">
      <div style="display:flex;gap:64px;align-items:baseline;margin-top:24px">
        <div class="big" style="font-size:150px;color:var(--coral)"><span class="num">5:1</span></div>
        <div class="body" style="max-width:560px"><span class="num">250</span> מ״ל נוזל ל־<span class="num">50</span> מ״ל תרכיז.
          התרכיז תמיד נכנס אחרון.</div>
      </div>
      <hr class="rule" style="margin-top:64px">
      <div class="kick">אחסון</div>
      <div class="body" style="margin-top:24px">באחסון סגור — מקום קריר ויבש, לא דורש קירור.<br>
        לאחר הפתיחה — לשמור בקירור; מומלץ עד <span class="num">3</span> חודשים.</div>
      <div class="body" style="margin-top:40px;color:var(--muted)">
        GT נבנה לצוותים עמוסים — קל להכניס, קל לתפעל, בכל משמרת.</div>'''))

    # S05-S12 — a dense product screen, then a hero that breathes. Hold the alternation.
    n = 5
    for p in PRODUCTS:
        s.append(product_screen(n, p, fig)); n += 1
        s.append(hero_screen(n, p, fig)); n += 1

    # S13 what to order
    roles = {"fresh": "היביסקוס ולײם. הבסיס לשלושה משקאות בתפריט.",
             "detox": "תה ירוק, לואיזה, נענע ולײם. הבסיס לשני משקאות.",
             "namastea": "מסאלה צ׳אי. הבסיס לשלושה משקאות — וגם לאייס מאצ׳ה מסאלה.",
             "matcha": "מאצ׳ה טקסית שיזואוקה. הבסיס לארבעה משקאות."}
    items = "".join(
        f'<li><span class="nm" style="color:var({p["hue"]})">{p["latin"]}</span>'
        f'<span class="role">{roles[p["key"]]}</span></li>' for p in PRODUCTS)
    s.append(screen(13, f'''
      <div class="kick">הזמנה</div>
      <h2 style="margin-top:24px">מה מזמינים<br>מ־GT</h2>
      <ul class="olist" style="margin-top:64px">{items}
        <li><span class="nm" style="color:var(--cost)">SMOOTHIE</span>
          <span class="role">מחית תות, <span class="num">50%</span> פרי. נדרשת לשני משקאות:
            חליטת תות לואיזה ואייס מאצ׳ה תות.</span></li>
      </ul>
      <hr class="rule" style="margin-top:64px">
      <div class="body" style="color:var(--muted)">בקבוק תמצית: <span class="num">20–25</span> כוסות.
        באחסון סגור — ללא קירור.</div>'''))

    # S14 what you already have
    have = ["קרח", "מים קרים", "סודה", "חלב או תחליפי חלב", "קצף חלב", "מיץ תפוחים",
            "סירופ אגבה", "אבקת קינמון", "תמצית וניל", "לימון", "נענע טרייה", "גרניש לפי טעם"]
    s.append(screen(14, f'''
      <div class="kick">המטבח שלכם</div>
      <h2 style="margin-top:24px">מה שכבר יש<br>לכם במטבח</h2>
      <p class="lead" style="margin-top:40px">כל <span class="num">{D_["n_drinks"]}</span> המשקאות נבנים
        מהתרכיזים של GT ומהמצרכים שכבר עומדים אצלכם על השיש.</p>
      <div class="have">{"".join(f"<span>{h}</span>" for h in have)}</div>
      <hr class="rule" style="margin-top:56px">
      <div class="lead">כל השאר כבר אצלכם. מ־GT מגיעים רק התרכיזים.</div>'''))

    # S15 closing — leads with the promise. Tom explicit; D8.
    s.append(screen(15, '''
      <div class="promise">נחזור אליכם<br>בהקדם.</div>
      <div class="promise-sub">נשמח להתאים לכם את התפריט — לפי מה שאתם מוכרים היום.</div>
      <div class="contact">
        <div><span class="num">gteveryday.com</span></div>
        <div><span class="num">info@gteveryday.com</span></div>
        <div><span class="num">054-398-2444</span></div>
        <div><span class="num">@gteveryday</span></div>
      </div>
      <div class="signoff">המשקה הטוב יותר, הבחירה הקלה, לכולם.</div>
      <img class="close-logo" src="assets/gt-logo-black.png" alt="GT">''', "close"))

    doc = "".join(s).replace("⅔", '<span class="num">2/3</span>')
    tokens = (D / "tokens.css").read_text()
    return ('<!DOCTYPE html>\n<html lang="he" dir="rtl"><head><meta charset="utf-8">'
            '<title>GT — תפריט הפתיחה</title><style>\n' + tokens + css()
            + '\n</style></head><body>\n' + doc + '</body></html>\n')


def main():
    fig = load_figures()
    OUT.write_text(html(fig), encoding="utf-8")
    d = derived(fig)
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
    print(f"  {d['n_products']} products, {d['n_drinks']} drinks, 15 screens")
    print(f"  derived: profit {d['prof_lo']}–{d['prof_hi']} · margin {d['marg_lo']}–{d['marg_hi']}")


if __name__ == "__main__":
    main()
