# -*- coding: utf-8 -*-
import json, re, html

R = json.load(open("pricing.json"))
FONTS = open("fonts.css").read()

def n(s):
    m = re.search(r'[\d.]+', s); return float(m.group()) if m else 0.0

# --- family identity: accent picked from what the drink actually IS -----------
FAM = [
 ("01","ICED TEA",        "חליטות קרות", "#B0503F"),
 ("02","LEMONADE",        "לימונדות",    "#D2A017"),
 ("03","SIGNATURE",       "סיגנצ׳ר",     "#8E3B52"),
 ("04","GAZOZ",           "גזוז",        "#DD7534"),
 ("05","ICE MATCHA",      "אייס מאצ׳ה",  "#6E8F3A"),
 ("06","MATCHA SPECIALS", "מאצ׳ה ספיישל","#2E7D64"),
 ("07","MATCHA COCONUT",  "מאצ׳ה קוקוס", "#3B8B9B"),
 ("08","CHAI MASSALA",    "צ׳אי מסאלה",  "#A5602A"),
 ("09","COLD FOAM",       "קולד פואם",   "#8A7358"),
 ("10","UBE",             "אובה",        "#6B4A94"),
]
KEY = {f"{a} {b}": (a,b,heb,col) for a,b,heb,col in FAM}

rows = []
for pg, fam, heb, eng, cost, price, marg, prof in R:
    num,name,hebfam,col = KEY[fam]
    rows.append(dict(pg=pg, fam=fam, num=num, famname=name, hebfam=hebfam, col=col,
                     heb=heb, eng=eng, cost=n(cost), star='*' in cost,
                     price=n(price), marg=int(marg.rstrip('%')), prof=n(prof)))

GROUPS = {}
for r in rows: GROUPS.setdefault(r["fam"], []).append(r)

MMIN, MMAX = min(r["marg"] for r in rows), max(r["marg"] for r in rows)
def ribbon(m):                       # normalise 65..90 so bars differ visibly
    return max(6, min(100, (m-64)/(90-64)*100))

# --- page composition --------------------------------------------------------
PAGES = [["01 ICED TEA","02 LEMONADE","03 SIGNATURE","04 GAZOZ"],
         ["05 ICE MATCHA","06 MATCHA SPECIALS","07 MATCHA COCONUT"],
         ["08 CHAI MASSALA","09 COLD FOAM","10 UBE"]]

def money(v, dec=2):
    s = f"{v:,.{dec}f}".rstrip('0').rstrip('.') if dec else f"{v:,.0f}"
    return f'<span class="mny">₪{s}</span>'

def esc(s): return html.escape(s)

def row_html(r):
    return f'''<div class="row">
  <div class="c-name"><span class="heb">{esc(r["heb"])}</span><span class="eng">{esc(r["eng"])}</span></div>
  <div class="c-rib"><i style="--w:{ribbon(r["marg"]):.1f}%;--c:{r["col"]}"></i><b>{r["marg"]}<small>%</small></b></div>
  <div class="c-num c-cost">{money(r["cost"])}{'<sup>*</sup>' if r["star"] else ''}</div>
  <div class="c-num c-price">{money(r["price"],0)}</div>
  <div class="c-num c-prof">{money(r["prof"])}</div>
</div>'''

def group_html(fam):
    g = GROUPS[fam]; r0 = g[0]
    lo, hi = min(x["price"] for x in g), max(x["price"] for x in g)
    span = f"₪{lo:.0f}" if lo==hi else f"₪{lo:.0f}–₪{hi:.0f}"
    avg = sum(x["marg"] for x in g)/len(g)
    return f'''<section class="grp" style="--c:{r0["col"]}">
  <header class="ghead">
    <div class="gid"><span class="gnum">{r0["num"]}</span><span class="gname">{r0["famname"]}</span><span class="gheb">{esc(r0["hebfam"])}</span></div>
    <div class="gmeta"><span>{len(g)} משקאות</span><em>{span}</em><span>ממוצע {avg:.0f}%</span></div>
  </header>
  <div class="rows">{''.join(row_html(r) for r in g)}</div>
</section>'''

def content_page(idx, fams):
    first = KEY[fams[0]][0]; last = KEY[fams[-1]][0]
    return f'''<div class="page sheet">
  <div class="ph">
    <div class="ph-l"><span class="ph-kicker">GT EVERYDAY · SUMMER 2026</span><h2>מחירון משקאות</h2></div>
    <div class="ph-r"><span class="ph-range">{first} — {last}</span></div>
  </div>
  <div class="colhead">
    <div class="c-name">משקה</div>
    <div class="c-rib">רווחיות</div>
    <div class="c-num">עלות</div>
    <div class="c-num">מחיר</div>
    <div class="c-num">רווח לכוס</div>
  </div>
  {''.join(group_html(f) for f in fams)}
  <div class="pfoot"><span>* כולל הערכת עלות גרניש/קצף</span><span class="pn">{idx}</span></div>
</div>'''

# --- cover -------------------------------------------------------------------
spectrum = ''.join(f'<i style="--c:{c};--n:{len(GROUPS[f"{a} {b}"])}"></i>' for a,b,h,c in FAM)
legend = ''.join(
  f'<div class="lg" style="--c:{c}"><u></u><b>{a}</b><span>{esc(h)}</span><em>{len(GROUPS[f"{a} {b}"])}</em></div>'
  for a,b,h,c in FAM)
tiers = {}
for r in rows: tiers.setdefault(int(r["price"]), []).append(r)
tierbar = ''.join(
  f'<div class="tier"><span class="tp">₪{p}</span><span class="tc">{len(v)}</span>'
  f'<span class="tt">{"משקה" if len(v)==1 else "משקאות"}</span></div>'
  for p,v in sorted(tiers.items()))

cover = f'''<div class="page cover">
  <div class="cov-top"><span>GT EVERYDAY</span><span>SUMMER 2026</span></div>
  <div class="cov-mid">
    <div class="cov-eyebrow">קטלוג משקאות · נספח מסחרי</div>
    <h1 class="cov-h">מחירון</h1>
    <div class="cov-sub">PRICE&nbsp;LIST</div>
    <div class="cov-rule"></div>
    <p class="cov-lede">כל 48 המשקאות בקטלוג — עלות חומרי גלם, מחיר מכירה ורווח גולמי לכוס.<br>מסודר לפי משפחה, בקוד צבע זהה לקטלוג.</p>
  </div>
  <div class="legend">
    <div class="lg-lab">משפחות המשקאות</div>
    <div class="spectrum">{spectrum}</div>
    <div class="lg-grid">{legend}</div>
  </div>
  <div class="cov-stats">
    <div class="st"><b>48</b><span>משקאות</span></div>
    <div class="st"><b>10</b><span>משפחות</span></div>
    <div class="st"><b class="sm">₪19<i>–</i>₪28</b><span>טווח מחיר</span></div>
    <div class="st"><b>{MMIN}<i>–</i>{MMAX}<small>%</small></b><span>רווח גולמי</span></div>
  </div>
  <div class="cov-tiers"><div class="ct-lab">מדרגות מחיר</div><div class="ct-row">{tierbar}</div></div>
  <div class="cov-foot">מחיר מומלץ · ללא מע״מ · כפי שמופיע בקטלוג המשקאות</div>
</div>'''

# --- summary -----------------------------------------------------------------
famstats = []
for a,b,heb,col in FAM:
    g = GROUPS[f"{a} {b}"]
    famstats.append(dict(num=a, name=b, heb=heb, col=col, k=len(g),
        cost=sum(x["cost"] for x in g)/len(g),
        price=sum(x["price"] for x in g)/len(g),
        prof=sum(x["prof"] for x in g)/len(g),
        marg=sum(x["marg"] for x in g)/len(g)))
top = sorted(rows, key=lambda r:-r["marg"])[:5]
bot = sorted(rows, key=lambda r: r["marg"])[:5]
maxprof = max(f["prof"] for f in famstats)

fs_rows = ''.join(f'''<div class="fs" style="--c:{f["col"]}">
  <div class="fs-id"><span class="fs-n">{f["num"]}</span><span class="fs-h">{esc(f["heb"])}</span><span class="fs-e">{f["name"]}</span></div>
  <div class="fs-bar"><i style="--w:{f["prof"]/maxprof*100:.1f}%"></i></div>
  <div class="fs-v">{money(f["cost"])}</div>
  <div class="fs-v">{money(f["price"])}</div>
  <div class="fs-v strong">{money(f["prof"])}</div>
  <div class="fs-v">{f["marg"]:.0f}<small>%</small></div>
</div>''' for f in famstats)

def mini(r, rank):
    return f'''<div class="mini" style="--c:{r["col"]}">
      <span class="mk">{rank}</span>
      <span class="mn">{esc(r["heb"])}</span>
      <span class="mm">{r["marg"]}<small>%</small></span>
      <span class="mp">{money(r["prof"])}</span></div>'''

summary = f'''<div class="page sheet">
  <div class="ph">
    <div class="ph-l"><span class="ph-kicker">GT EVERYDAY · SUMMER 2026</span><h2>תמונת רווחיות</h2></div>
    <div class="ph-r"><span class="ph-range">סיכום</span></div>
  </div>
  <div class="sec-lab">ממוצע לפי משפחה</div>
  <div class="fs-head"><div class="fs-id">משפחה</div><div class="fs-bar">רווח יחסי</div>
    <div class="fs-v">עלות</div><div class="fs-v">מחיר</div><div class="fs-v">רווח</div><div class="fs-v">%</div></div>
  <div class="fs-wrap">{fs_rows}</div>
  <div class="two">
    <div class="col">
      <div class="sec-lab">חמשת הרווחיים ביותר</div>
      {''.join(mini(r,i+1) for i,r in enumerate(top))}
    </div>
    <div class="col">
      <div class="sec-lab">חמשת הנמוכים ביותר</div>
      {''.join(mini(r,i+1) for i,r in enumerate(bot))}
    </div>
  </div>
  <div class="callout">
    <div class="co-k">מה שהמספרים אומרים</div>
    <p>כל 48 המשקאות יושבים בין <b>{MMIN}%</b> ל־<b>{MMAX}%</b> רווח גולמי — פער של 16 נקודות בלבד. התמחור אחיד ובריא לרוחב הקטלוג.
    המנוף האמיתי הוא <b>מדרגת המחיר</b>, לא העלות: מעבר מ־₪19 ל־₪28 מוסיף כ־<b>₪9</b> רווח לכוס בעוד פער העלות בין המשקה הזול ליקר הוא ₪3.94 בלבד.</p>
  </div>
  <div class="pfoot"><span>מחירים ללא מע״מ · ממוצעים אריתמטיים לא משוקללים</span><span class="pn">5</span></div>
</div>'''

BODY = cover + ''.join(content_page(i+2, f) for i, f in enumerate(PAGES)) + summary
CSS = open("style.css").read()
open("pricelist.html","w").write(
f'''<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="UTF-8">
<title>GT מחירון משקאות · SUMMER 2026</title>
<style>{FONTS}</style><style>{CSS}</style></head><body>{BODY}</body></html>''')
print("pages:", 5, "| rows:", len(rows), "| families:", len(FAM))
