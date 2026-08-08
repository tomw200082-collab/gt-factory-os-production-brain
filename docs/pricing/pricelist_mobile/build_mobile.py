#!/usr/bin/env python3
"""GT Everyday — wholesale pricelist, mobile edition.

Same catalogue, same ex-VAT prices and same brand palette as the A4 sheet in
`../pricelist_pdf/`, rebuilt as a single self-contained HTML page for a buyer
holding a phone behind their bar. Prices, names, sub-lines and section copy are
copied from `../pricelist_pdf/build.py` — this file must never introduce a
figure the print sheet does not carry.

What the phone changes, and why:

  * There are no pages, so the print folios (01 / 02 / 03) carry no information
    and are dropped. The structural device that replaces them is the count:
    every section states how many products it holds and its price range, which
    is what a buyer scanning a catalogue actually wants to know.
  * The price is the reason the page exists, so it stops being a column and
    becomes a filled panel — the one tinted element on an otherwise flat paper
    page. Running down the scroll, those panels are the page's rhythm.
  * Tea is sold in two sizes. On paper a bottle stands above each price column;
    on the phone the two bottles sit inside the row at their true relative
    height, directly above their own prices, so size-to-price is a picture
    before it is a label.
  * Product cutouts were composited onto the paper colour when the print sheet
    was built, so the card surface stays exactly PAPER — the boxes are invisible
    only while nothing tints them. Structure is carried by hairlines, never by
    filled cards.
  * A buyer who has found their price wants to order, so the phone number and
    WhatsApp thread are a fixed bar, not a footer line.

Assets in `assets/` were lifted from the approved print PDF, so the photography
is provably the same set Tom signed off on 2026-08-06.

Build:  python3 build_mobile.py   →  GT_pricelist_mobile.html
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / 'assets'
FONTS = HERE.parent / 'pricelist_pdf' / 'fonts'

# ─── palette ────────────────────────────────────────────────────────────────
# Sampled from the print sheet. Two additions, both forced by the screen:
#   CORAL_INK  the coral at text contrast (FA6E4D on paper is 2.3:1 and fails)
#   TINT       the price panel, the only surface allowed to leave the paper
PAPER, INK, GREEN, CORAL = '#EFE6D6', '#241C15', '#263B18', '#FA6E4D'
CORAL_INK, TINT, RULE, MUTED = '#C6421F', '#E4D7BE', '#D8CCB4', '#6A5D48'

WA = '972543982444'
TEL = '054-398-2444'
SITE_URL = 'https://pricelist.gteveryday.com'

# Wholesale prices are ex-VAT and are not the shelf price. The link is meant to
# be sent to a buyer, not found by a shopper comparing against the Shopify
# store, so the hosted page asks search engines to stay out. Flip both this and
# site/robots.txt together if the sheet should ever be indexed.
INDEXABLE = False

# ─── data — figures identical to ../pricelist_pdf/build.py ──────────────────
TEAS = [
    ("FRESH",           "חליטה תאילנדית · היביסקוס וליים",       "fresh"),
    ("FRESH ללא סוכר",  "חליטה תאילנדית · ללא תוספת סוכר",       "fresh_sf"),
    ("DETOX",           "חליטה ישראלית · תה ירוק, לואיזה ונענע", "detox"),
    ("DETOX ללא סוכר",  "חליטה ישראלית · ללא תוספת סוכר",        "detox_sf"),
    ("ENERGY",          "חליטת שנגחאי · תה ירוק ולמון גראס",     "energy"),
    ("CALM",            "חליטה צרפתית · קמומיל, תפוח וציפורן",   "calm"),
    ("CONSCIOUSNESS",   "חליטה קוריאנית · יסמין וליצ׳י",         "conscious"),
    ("REVIVE",          "חליטה יפנית · סנצ׳ה ופסיפלורה",         "revive"),
    ("DESERTEA",        "חליטה מדברית · חמישה צמחי בר",          "desertea"),
    ("NAMASTEA",        "חליטה הודית · צ׳אי מסאלה",              "namastea"),
    ("AMERICAN",        "חליטה אמריקאית · תה שחור, יוזו והדרים", "american"),
]
TEA_L, TEA_ML = 65, 33

POWDERS = [
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · שקית 500 גרם",    "pw_matcha",  590),
    ("MATCHA שיזואוקה", "מאצ׳ה טקסית יפנית · 22 שקיות 18 גרם", None,         590),
    ("HOJICHA",         "מאצ׳ה שחורה קלויה · 500 גרם",         "pw_hojicha", 375),
    ("UBE",             "אבקת שורש יאם סגול · 1 ק״ג",          "pw_ube",     340),
    ("UBE",             "אבקת שורש יאם סגול · 500 גרם",        "pw_ube",     175),
    ("MATCHA KIT",      "ערכת מאצ׳ה מלאה להכנה",               None,         170),
]

PUREES = [
    ("SMOOTHIE מנגו",  "מחית פרי 50% · 1 ליטר", "pu_mango", 60),
    ("SMOOTHIE תות",   "מחית פרי 50% · 1 ליטר", "pu_straw", 60),
    ("SMOOTHIE אפרסק", "מחית פרי 50% · 1 ליטר", "pu_peach", 60),
]

TOOLS = [
    ("קערת מאצ׳ה קרמית",    "צ׳אוואן מסורתי",     "tl_bowl",    118),
    ("מקציף מאצ׳ה חשמלי",   "מקציף ידני נטען",    "tl_frother", 100),
    ("מטרפת במבוק",         "צ׳אסן · 100 שיניים", "tl_whisk",    37),
    ("כוס זכוכית 600 מ״ל",  "כוס מדידה מחוסמת",   "tl_beaker",   30),
    ("מעמד למטרפה",         "צ׳אסן טאטה",         "tl_stand",    25),
    ("כוס מדידה",           "ג׳יגר מודפס",        "tl_jigger",   20),
    ("כף מדידה במבוק",      "צ׳אשאקו",            "tl_scoop",    11),
    ("בקבוק מאצ׳ה 500 מ״ל", "בקבוק זכוכית כהה",   "tl_bottle",   10),
]


# ─── embedding ──────────────────────────────────────────────────────────────
# Two delivery modes off one source. 'inline' bakes every byte into the file, so
# the page survives being forwarded, saved or opened offline — that is the whole
# point of the sendable edition. 'site' links assets instead, because a hosted
# page wants them cached separately and the HTML parsed in one small chunk.
MODE = 'inline'
FONT_EXT = 'woff'          # site mode subsets to woff2; inline keeps the woff it embeds

FACES = [
    ('Heebo', 400, 'heebo-400.woff'),
    ('Rubik', 500, 'rubik-500.woff'),
    ('Rubik', 600, 'rubik-600.woff'),
    ('Rubik', 700, 'rubik-700.woff'),
]


def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()


def img(name):
    if MODE == 'site':
        return f'assets/{name}'
    mime = 'image/png' if name.endswith('.png') else 'image/jpeg'
    return data_uri(ASSETS / name, mime)


def face(family, weight, file):
    stem = file.rsplit('.', 1)[0]
    if MODE == 'site':
        src, fmt = f'fonts/{stem}.{FONT_EXT}', FONT_EXT
    else:
        src, fmt = data_uri(FONTS / file, 'font/woff'), 'woff'
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url({src}) format('{fmt}')}}")


def font_faces():
    return "".join(face(*f) for f in FACES)


# ─── markup helpers ─────────────────────────────────────────────────────────
def price(v, size_label=None):
    lab = f'<span class="psz">{size_label}</span>' if size_label else ''
    return (f'<span class="pcell">{lab}'
            f'<span class="pval"><span class="cur">₪</span>{v}</span></span>')


def rng(text):
    """A price range is Latin-ordered; RTL would mirror it into nonsense."""
    return f'<span dir="ltr">{text}</span>'


def tea_row(name, sub, key, idx):
    """1 L and 500 ml at true relative height, each standing over its own price."""
    return f"""<article class="row row--tea" style="--i:{min(idx, 5)}">
  <div class="shot shot--pair">
    <img class="s1l" src="{img(f'big_{key}.jpg')}" alt="{name} · 1 ליטר" loading="lazy" decoding="async">
    <img class="s5h" src="{img(f'sml_{key}.jpg')}" alt="{name} · 500 מ״ל" loading="lazy" decoding="async">
  </div>
  <div class="meta"><h3>{name}</h3><p>{sub}</p></div>
  <div class="panel panel--two">{price(TEA_L, '1 ליטר')}{price(TEA_ML, '500 מ״ל')}</div>
</article>"""


def row(name, sub, key, value, idx):
    shot = (f'<img src="{img(key + ".jpg")}" alt="{name}" loading="lazy" decoding="async">'
            if key else
            f'<img class="mark" src="{img("logo_green.png")}" alt="" loading="lazy" decoding="async">')
    return f"""<article class="row" style="--i:{min(idx, 5)}">
  <div class="shot{'' if key else ' shot--mark'}">{shot}</div>
  <div class="meta"><h3>{name}</h3><p>{sub}</p></div>
  <div class="panel">{price(value)}</div>
</article>"""


def band(name, kicker, title):
    return f"""<div class="band">
  <img src="{img(name)}" alt="" loading="lazy" decoding="async">
  <div class="band-t"><span class="bk">{kicker}</span><span class="bt">{title}</span></div>
</div>"""


def sec_head(title, kicker, count, span, note=''):
    return (f'<header class="sec"><h2>{title}</h2>'
            f'<span class="sec-k">{kicker}</span>'
            f'<p class="sec-m"><b>{count} מוצרים</b><span class="dot"></span>{rng(span)}</p>'
            + (f'<p class="sec-n">{note}</p>' if note else '') + '</header>')


# ─── stylesheet ─────────────────────────────────────────────────────────────
def css():
    return f"""{font_faces()}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --paper:{PAPER}; --ink:{INK}; --green:{GREEN}; --coral:{CORAL};
  --coral-ink:{CORAL_INK}; --tint:{TINT}; --rule:{RULE}; --muted:{MUTED};
  --gut:20px; --head:56px;
}}
html{{-webkit-text-size-adjust:100%; scroll-behavior:smooth}}
body{{
  background:var(--paper); color:var(--ink);
  font-family:'Heebo',system-ui,sans-serif; font-size:16px; line-height:1.5;
  -webkit-font-smoothing:antialiased; overflow-x:hidden;
  padding-bottom:calc(84px + env(safe-area-inset-bottom,0px));
}}
img{{max-width:100%; display:block}}
a{{color:inherit}}
:focus-visible{{outline:2.5px solid var(--coral-ink); outline-offset:3px; border-radius:2px}}

/* ── hero ─────────────────────────────────────────────────────────────── */
.hero{{position:relative; min-height:86svh; display:grid; place-items:start center;
  padding:clamp(64px,11svh,104px) var(--gut) 40px; overflow:hidden}}
.hero>img{{position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
  object-position:50% 100%}}
.hero::after{{content:''; position:absolute; inset:0;
  background:linear-gradient(180deg,rgba(239,230,214,.62) 0%,rgba(239,230,214,.34) 34%,
    rgba(239,230,214,0) 56%)}}
.hv{{position:relative; z-index:2; text-align:center; display:grid; justify-items:center}}
.hv>*{{animation:rise .8s cubic-bezier(.2,.7,.2,1) both; animation-delay:calc(var(--d,0)*90ms)}}
.hv .mark{{width:76px; --d:0}}
.hv .hair{{width:52px; height:1px; background:var(--ink); opacity:.3; margin:22px 0 20px; --d:1}}
.hv h1{{font-family:'Rubik',sans-serif; font-weight:700; font-size:clamp(38px,11.5vw,54px);
  line-height:1.06; letter-spacing:-.005em; --d:2}}
.hv .sub{{margin-top:16px; font-size:15px; line-height:1.85; color:var(--muted);
  letter-spacing:.02em; --d:3}}
.hv .tag{{margin-top:24px; background:var(--coral); color:var(--ink);
  font-family:'Rubik',sans-serif; font-weight:600; font-size:13px; letter-spacing:.1em;
  padding:10px 18px; --d:4}}
.hero .yr{{position:absolute; z-index:3; top:calc(20px + env(safe-area-inset-top,0px));
  right:var(--gut); font-family:'Rubik',sans-serif; font-weight:600; font-size:12.5px;
  letter-spacing:.42em; opacity:.5; animation:rise .8s cubic-bezier(.2,.7,.2,1) both .5s}}
.cue{{position:absolute; bottom:18px; left:50%; translate:-50% 0; z-index:2; width:15px;
  opacity:.78; animation:nudge 2.4s ease-in-out infinite 1.4s}}
@keyframes rise{{from{{opacity:0; transform:translateY(18px)}}}}
@keyframes nudge{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(6px)}}}}

/* ── sticky header ────────────────────────────────────────────────────── */
.top{{position:sticky; top:0; z-index:40; background:rgba(239,230,214,.94);
  -webkit-backdrop-filter:saturate(1.4) blur(14px); backdrop-filter:saturate(1.4) blur(14px);
  border-bottom:1px solid var(--rule)}}
.top-b{{height:var(--head); display:flex; align-items:center; gap:12px;
  padding:0 var(--gut)}}
.top-b img{{width:26px}}
.top-b .ttl{{font-family:'Rubik',sans-serif; font-weight:600; font-size:16px;
  letter-spacing:.01em; flex:1 1 auto}}
.top-b .vat{{background:var(--coral); color:var(--ink); font-family:'Rubik',sans-serif;
  font-weight:600; font-size:11px; letter-spacing:.06em; padding:6px 10px; white-space:nowrap}}
.chips{{display:flex; gap:7px; overflow-x:auto; padding:0 var(--gut) 10px;
  scrollbar-width:none; -webkit-overflow-scrolling:touch}}
.chips::-webkit-scrollbar{{display:none}}
.chips a{{flex:0 0 auto; min-height:38px; display:inline-flex; align-items:center;
  padding:0 13px; border:1px solid var(--rule); color:var(--muted); text-decoration:none;
  font-family:'Rubik',sans-serif; font-weight:600; font-size:13.5px; letter-spacing:.01em;
  transition:background .18s, color .18s, border-color .18s}}
.chips a[aria-current="true"]{{background:var(--green); border-color:var(--green); color:var(--paper)}}

/* ── section band ─────────────────────────────────────────────────────── */
section{{scroll-margin-top:calc(var(--head) + 50px)}}
.band{{position:relative; aspect-ratio:16/6.4; overflow:hidden; margin-top:34px}}
.band img{{position:absolute; inset:0; width:100%; height:100%; object-fit:cover}}
.band::after{{content:''; position:absolute; inset:0;
  background:linear-gradient(to left,rgba(20,14,8,.74) 0%,rgba(20,14,8,.3) 52%,rgba(20,14,8,0) 84%)}}
.band-t{{position:absolute; z-index:2; right:var(--gut); bottom:16px; color:#fff}}
.band-t .bk{{display:block; font-family:'Rubik',sans-serif; font-weight:500; font-size:10px;
  letter-spacing:.34em; opacity:.88}}
.band-t .bt{{display:block; font-family:'Rubik',sans-serif; font-weight:700;
  font-size:clamp(24px,7vw,32px); letter-spacing:.005em; margin-top:5px}}

/* ── section head ─────────────────────────────────────────────────────── */
.sec{{position:relative; margin:26px var(--gut) 6px; padding-right:14px}}
.sec::before{{content:''; position:absolute; right:0; top:5px; bottom:5px; width:3px;
  background:var(--coral)}}
.sec h2{{font-family:'Rubik',sans-serif; font-weight:700; font-size:26px; color:var(--green);
  letter-spacing:.005em}}
.sec-k{{display:block; font-family:'Rubik',sans-serif; font-weight:500; font-size:10px;
  letter-spacing:.32em; color:var(--muted); margin-top:5px}}
.sec-m{{display:flex; align-items:center; gap:9px; margin-top:11px; font-size:13.5px;
  color:var(--muted); letter-spacing:.01em}}
.sec-m b{{font-family:'Rubik',sans-serif; font-weight:600; color:var(--ink)}}
.sec-m [dir=ltr]{{font-family:'Rubik',sans-serif; font-weight:600; color:var(--ink);
  font-variant-numeric:tabular-nums}}
.sec-m .dot{{width:3px; height:3px; background:var(--rule); border-radius:50%}}
.sec-n{{margin-top:7px; font-size:13.5px; color:var(--muted)}}

/* ── rows ─────────────────────────────────────────────────────────────── */
.list{{margin:14px var(--gut) 0; border-top:1px solid var(--rule)}}
.row{{display:grid; grid-template-columns:96px 1fr; grid-template-areas:'shot meta' 'shot panel';
  align-items:center; gap:2px 14px; padding:16px 0; border-bottom:1px solid var(--rule)}}
.row--tea{{grid-template-columns:104px 1fr}}
.shot{{grid-area:shot; height:96px; display:flex; align-items:flex-end; justify-content:center; gap:5px}}
.shot img{{max-height:100%; width:auto; object-fit:contain}}
.shot--pair .s1l{{height:100%}}
.shot--pair .s5h{{height:64%}}
.shot--mark{{align-items:center}}
.shot--mark .mark{{width:38px; opacity:.17}}
.meta{{grid-area:meta; align-self:end; min-width:0}}
.meta h3{{font-family:'Rubik',sans-serif; font-weight:600; font-size:20px; line-height:1.2;
  letter-spacing:.012em}}
.meta p{{margin-top:5px; font-size:14px; line-height:1.45; color:var(--muted)}}

/* the one tinted surface on the page — a price you can hit with a thumb */
.panel{{grid-area:panel; align-self:start; justify-self:start; margin-top:12px;
  background:var(--tint); display:flex; min-height:58px}}
.panel--two{{width:100%}}
.pcell{{flex:1 1 0; display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:3px; padding:9px 12px}}
.panel--two .pcell+.pcell{{border-right:1px solid rgba(36,28,21,.15)}}
.panel:not(.panel--two) .pcell{{padding:9px 22px}}
.psz{{font-family:'Rubik',sans-serif; font-weight:600; font-size:11.5px; letter-spacing:.03em;
  color:var(--muted)}}
.pval{{direction:ltr; font-family:'Rubik',sans-serif; font-weight:700; font-size:31px;
  line-height:1; font-variant-numeric:tabular-nums; letter-spacing:-.015em; white-space:nowrap}}
.panel:not(.panel--two) .pval{{font-size:35px}}
.cur{{font-size:.53em; font-weight:600; color:var(--coral-ink); margin-right:.09em;
  vertical-align:.12em}}

/* ── footer + call bar ────────────────────────────────────────────────── */
.foot{{margin:8px var(--gut) 0; padding:40px 0 30px; text-align:center; color:var(--muted); font-size:13px; letter-spacing:.02em}}
.foot img{{width:40px; margin:0 auto 16px; opacity:.62}}
.foot .l{{margin-top:7px}}
.foot .dl{{margin-top:16px}}
.foot .dl a{{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;
  border:1px solid var(--rule); text-decoration:none; color:var(--ink);
  font-family:'Rubik',sans-serif; font-weight:600; font-size:13.5px; letter-spacing:.01em}}
.foot .yr{{margin-top:16px; font-family:'Rubik',sans-serif; font-weight:600; font-size:12px;
  letter-spacing:.36em; opacity:.55}}

.bar{{position:fixed; z-index:50; inset:auto 0 0 0; display:flex; gap:10px;
  padding:10px var(--gut) calc(10px + env(safe-area-inset-bottom,0px));
  background:rgba(239,230,214,.95);
  -webkit-backdrop-filter:blur(14px); backdrop-filter:blur(14px);
  border-top:1px solid var(--rule);
  transform:translateY(110%); transition:transform .34s cubic-bezier(.2,.7,.2,1)}}
.bar.on{{transform:none}}
.bar a{{flex:1 1 0; min-height:52px; display:flex; align-items:center; justify-content:center;
  gap:9px; text-decoration:none; font-family:'Rubik',sans-serif; font-weight:600; font-size:15.5px;
  letter-spacing:.02em}}
.bar .wa{{background:var(--green); color:var(--paper)}}
.bar .tel{{background:transparent; color:var(--ink); border:1.5px solid var(--ink)}}
.bar svg{{width:19px; height:19px; flex:0 0 auto}}

/* ── reveal ───────────────────────────────────────────────────────────── */
.row{{opacity:0; transform:translateY(14px);
  transition:opacity .5s ease, transform .5s cubic-bezier(.2,.7,.2,1);
  transition-delay:calc(var(--i,0)*34ms)}}
.row.in{{opacity:1; transform:none}}

@media (min-width:600px){{
  :root{{--gut:32px}}
  body{{max-width:720px; margin:0 auto; border-inline:1px solid var(--rule)}}
  .row{{grid-template-columns:120px 1fr auto;
        grid-template-areas:'shot meta panel'; align-items:center; gap:0 18px; padding:18px 0}}
  .row--tea{{grid-template-columns:130px minmax(0,1fr) 250px}}
  .meta{{align-self:center}}
  .panel{{margin-top:0; justify-self:end}}
  .shot{{height:110px}}
}}
@media (prefers-reduced-motion:reduce){{
  html{{scroll-behavior:auto}}
  *,*::before,*::after{{animation-duration:.001ms !important; animation-iteration-count:1 !important;
    transition-duration:.001ms !important}}
  .row{{opacity:1; transform:none}}
}}
"""


JS = """
(function(){
  var rows=document.querySelectorAll('.row');
  if('IntersectionObserver' in window){
    var ro=new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); ro.unobserve(e.target); } });
    },{rootMargin:'0px 0px -8% 0px',threshold:.05});
    rows.forEach(function(r){ ro.observe(r); });
  } else { rows.forEach(function(r){ r.classList.add('in'); }); }

  var bar=document.querySelector('.bar'), hero=document.querySelector('.hero');
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      bar.classList.toggle('on', !es[0].isIntersecting);
    },{threshold:.12}).observe(hero);
  } else { bar.classList.add('on'); }

  var chips=[].slice.call(document.querySelectorAll('.chips a')),
      secs=chips.map(function(c){ return document.querySelector(c.getAttribute('href')); });
  function mark(el){
    chips.forEach(function(c,i){ c.setAttribute('aria-current', secs[i]===el ? 'true':'false'); });
    var a=chips[secs.indexOf(el)];
    if(a && a.parentNode.scrollWidth>a.parentNode.clientWidth){
      a.parentNode.scrollTo({left:a.offsetLeft-40,behavior:'smooth'});
    }
  }
  var spy=new IntersectionObserver(function(es){
    var vis=es.filter(function(e){ return e.isIntersecting; });
    if(vis.length){ mark(vis.sort(function(a,b){ return a.boundingClientRect.top-b.boundingClientRect.top; })[0].target); }
  },{rootMargin:'-30% 0px -60% 0px'});
  secs.forEach(function(s){ if(s) spy.observe(s); });
})();
"""

WA_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.6 2 2.2 6.4 2.2 '
          '11.84c0 1.74.46 3.44 1.32 4.94L2 22l5.36-1.4a9.8 9.8 0 0 0 4.68 1.19h.01c5.43 0 9.84-4.4 '
          '9.84-9.84 0-2.63-1.02-5.1-2.88-6.96A9.78 9.78 0 0 0 12.04 2Zm0 17.94h-.01a8.2 8.2 0 0 '
          '1-4.16-1.14l-.3-.18-3.1.81.83-3.02-.2-.31a8.13 8.13 0 0 1-1.25-4.36c0-4.51 3.68-8.18 '
          '8.2-8.18 2.19 0 4.24.85 5.79 2.4a8.13 8.13 0 0 1 2.4 5.79c0 4.51-3.68 8.19-8.2 '
          '8.19Zm4.5-6.13c-.25-.12-1.46-.72-1.68-.8-.23-.09-.39-.13-.56.12-.16.25-.63.8-.78.96-.14.17-.29.19-.53.07-.25-.13-1.04-.39-1.98-1.23-.73-.65-1.23-1.46-1.37-1.7-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.44.12-.14.16-.25.25-.41.08-.17.04-.31-.02-.44-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.42l-.47-.01c-.16 '
          '0-.43.06-.65.31-.23.25-.86.84-.86 2.05s.88 2.38 1 2.54c.13.17 1.74 2.65 4.2 3.72.59.25 '
          '1.05.4 1.4.52.59.18 1.13.16 1.55.1.47-.07 1.46-.6 1.66-1.18.21-.57.21-1.07.15-1.17-.06-.11-.23-.17-.47-.29Z"/></svg>')

TEL_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 '
           '6.6 6.6l2.2-2.2c.28-.28.68-.36 1.03-.25 1.13.37 2.34.57 3.57.57.55 0 1 .45 1 '
           '1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.5c0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 '
           '1.24.2 2.44.57 3.57.11.35.03.75-.25 1.03l-2.22 2.2Z"/></svg>')


def head_extra():
    """Link-preview and indexing tags — only meaningful for the hosted edition."""
    if MODE != 'site':
        return ''
    robots = '' if INDEXABLE else '<meta name="robots" content="noindex,nofollow">\n'
    return (robots +
            f'<link rel="canonical" href="{SITE_URL}/">\n'
            f'<link rel="icon" href="icon-32.png" sizes="32x32">\n'
            f'<link rel="apple-touch-icon" href="icon-180.png">\n'
            f'<meta property="og:type" content="website">\n'
            f'<meta property="og:locale" content="he_IL">\n'
            f'<meta property="og:site_name" content="GT Everyday">\n'
            f'<meta property="og:title" content="GT Everyday · מחירון סיטונאי 2026">\n'
            f'<meta property="og:description" content="תמציות תה, מאצ׳ה ואבקות, מחיות פרי ומוצרים משלימים. כל המחירים ללא מע״מ.">\n'
            f'<meta property="og:url" content="{SITE_URL}/">\n'
            f'<meta property="og:image" content="{SITE_URL}/og.jpg">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n')


def render():
    teas = "".join(tea_row(n, s, k, i) for i, (n, s, k) in enumerate(TEAS))
    powders = "".join(row(n, s, k, v, i) for i, (n, s, k, v) in enumerate(POWDERS))
    purees = "".join(row(n, s, k, v, i) for i, (n, s, k, v) in enumerate(PUREES))
    tools = "".join(row(n, s, k, v, i) for i, (n, s, k, v) in enumerate(TOOLS))

    html = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{PAPER}">
<meta name="description" content="GT Everyday — מחירון סיטונאי 2026. תמציות תה, מאצ׳ה ואבקות, מחיות פרי ומוצרים משלימים. כל המחירים ללא מע״מ.">
<title>GT Everyday · מחירון סיטונאי 2026</title>
{head_extra()}<style>{css()}</style>
</head>
<body>

<header class="hero">
  <img src="{img('cover.jpg')}" alt="בקבוקי GT Everyday" fetchpriority="high" decoding="async">
  <div class="hv">
    <img class="mark" src="{img('logo_ink.png')}" alt="GT Everyday">
    <span class="hair"></span>
    <h1>מחירון סיטונאי</h1>
    <p class="sub">תמציות תה · מאצ׳ה ואבקות<br>מחיות פרי · מוצרים משלימים</p>
    <span class="tag">כל המחירים ללא מע״מ</span>
  </div>
  <span class="yr">2026</span>
  <svg class="cue" viewBox="0 0 24 40" fill="none" stroke="{PAPER}" stroke-width="2.4"
       stroke-linecap="round" aria-hidden="true"><path d="M4 26l8 9 8-9"/></svg>
</header>

<div class="top">
  <div class="top-b">
    <img src="{img('logo_green.png')}" alt="">
    <span class="ttl">מחירון סיטונאי</span>
    <span class="vat">ללא מע״מ</span>
  </div>
  <nav class="chips" aria-label="קטגוריות">
    <a href="#tea" aria-current="true">תמציות תה</a>
    <a href="#powders" aria-current="false">מאצ׳ה</a>
    <a href="#purees" aria-current="false">מחיות פרי</a>
    <a href="#tools" aria-current="false">ציוד</a>
  </nav>
</div>

<main>
  <section id="tea">
    {band('band_tea.jpg', 'TEA&nbsp;&nbsp;EXTRACTS', 'תמציות תה')}
    {sec_head('תמציות תה', 'TEA&nbsp;&nbsp;EXTRACTS', 11, '₪33 – ₪65', 'בקבוק אחד = 20–25 כוסות משקה')}
    <div class="list">{teas}</div>
  </section>

  <section id="powders">
    {band('band_powder.jpg', 'MATCHA&nbsp;&nbsp;·&nbsp;&nbsp;POWDERS', 'מאצ׳ה ואבקות')}
    {sec_head('מאצ׳ה ואבקות', 'MATCHA&nbsp;&nbsp;·&nbsp;&nbsp;POWDERS', 6, '₪170 – ₪590')}
    <div class="list">{powders}</div>
  </section>

  <section id="purees">
    {sec_head('מחיות פרי', 'FRUIT&nbsp;&nbsp;PURÉES', 3, '₪60')}
    <div class="list">{purees}</div>
  </section>

  <section id="tools">
    {band('band_tools.jpg', 'TOOLS&nbsp;&nbsp;·&nbsp;&nbsp;SERVEWARE', 'מוצרים משלימים')}
    {sec_head('מוצרים משלימים', 'TOOLS&nbsp;&nbsp;·&nbsp;&nbsp;SERVEWARE', 8, '₪10 – ₪118')}
    <div class="list">{tools}</div>
  </section>
</main>

<footer class="foot">
  <img src="{img('logo_green.png')}" alt="GT Everyday">
  <p>כל המחירים ללא מע״מ</p>
  <p class="l">gteveryday.com · {TEL}</p>
  {'<p class="dl"><a href="GT_pricelist_mobile.pdf" download>הורדת המחירון · PDF</a></p>' if MODE == 'site' else ''}
  <p class="yr">2026</p>
</footer>

<nav class="bar" aria-label="הזמנות">
  <a class="wa" href="https://wa.me/{WA}">{WA_SVG}הזמנה בוואטסאפ</a>
  <a class="tel" href="tel:+{WA}">{TEL_SVG}{TEL}</a>
</nav>

<script>{JS}</script>
</body>
</html>"""

    return html


def build():
    html = render()
    out = HERE / 'GT_pricelist_mobile.html'
    out.write_text(html, encoding='utf-8')

    # The hosted-artifact host supplies its own <!doctype>/<head>/<body> shell and
    # takes only page content, so the document wrapper is stripped and the RTL
    # direction the <html dir> carried is restated in the stylesheet instead.
    body = html.split('<body>', 1)[1].rsplit('</body>', 1)[0]
    (HERE / 'artifact.html').write_text(
        '<title>GT Everyday · מחירון סיטונאי 2026</title>\n'
        f'<style>html,body{{direction:rtl}}{css()}</style>\n{body}',
        encoding='utf-8')
    rows = len(TEAS) + len(POWDERS) + len(PUREES) + len(TOOLS)
    figures = len(TEAS) * 2 + len(POWDERS) + len(PUREES) + len(TOOLS)
    print(f'{out.name}  {out.stat().st_size / 1e6:.2f} MB  ·  {rows} rows  ·  {figures} figures')


if __name__ == '__main__':
    build()
