#!/usr/bin/env python3
"""Rebuild GT's knowledge book (ספר העבודה) as HTML from the knowledge cards.

The repo is the database; this page is a rendering of it. Every figure on the
page is read out of Sales-Machine/knowledge/**.yaml, which reconcile.py has
already joined to the approved sources — so a number cannot reach the page
without surviving that gate.

    python3 scripts/knowledge/build_book.py [-o out.html]
"""
import argparse
import datetime as dt
import html
import os
import subprocess

import yaml

BRAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALES = os.path.join(os.path.dirname(BRAIN), "Sales-Machine")
K = os.path.join(SALES, "knowledge")


def load(rel):
    with open(os.path.join(K, rel), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def sha(repo):
    try:
        return subprocess.check_output(["git", "-C", repo, "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


def e(x):
    return html.escape(str(x), quote=True)


def money(x):
    f = float(x)
    return f"₪{int(f):,}" if f == int(f) else f"₪{f:,.2f}"


# ------------------------------------------------------------------ style
CSS = """
:root{
  --ground:#F1F3EE; --surface:#FBFCF9; --sunk:#E8EBE3;
  --ink:#161A15; --ink-2:#576155; --ink-3:#7C8778;
  --rule:#D9DED2; --rule-2:#C4CBBB;
  --leaf:#2E6B4C;            /* steeped tea — the one bold colour */
  --leaf-soft:#E2EFE7;
  --chill:#3A6B84;           /* the fridge side of the category */
  --chill-soft:#E2EDF2;
  --open:#9E4526; --open-soft:#F6E6DF;
  --hold:#7E6413; --hold-soft:#F4EEDA;
  --shadow:0 1px 2px rgba(22,26,21,.05),0 8px 24px -16px rgba(22,26,21,.28);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0F120E; --surface:#171B15; --sunk:#1E2320;
    --ink:#E9EDE3; --ink-2:#A3AC9C; --ink-3:#7D8878;
    --rule:#2A3027; --rule-2:#3A4235;
    --leaf:#77C79A; --leaf-soft:#1B2C22;
    --chill:#84B8D0; --chill-soft:#17262D;
    --open:#E08A66; --open-soft:#2E1D15;
    --hold:#D9BC63; --hold-soft:#2A2412;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -18px rgba(0,0,0,.8);
    color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --ground:#0F120E; --surface:#171B15; --sunk:#1E2320;
  --ink:#E9EDE3; --ink-2:#A3AC9C; --ink-3:#7D8878;
  --rule:#2A3027; --rule-2:#3A4235;
  --leaf:#77C79A; --leaf-soft:#1B2C22;
  --chill:#84B8D0; --chill-soft:#17262D;
  --open:#E08A66; --open-soft:#2E1D15;
  --hold:#D9BC63; --hold-soft:#2A2412;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -18px rgba(0,0,0,.8);
  color-scheme:dark;
}

*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:76px}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
body{
  margin:0;background:var(--ground);color:var(--ink);
  font-family:"Heebo",-apple-system,"Segoe UI",system-ui,sans-serif;
  font-size:16.5px;line-height:1.62;direction:rtl;
  -webkit-font-smoothing:antialiased;
}
.mono{font-family:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;font-size:.82em;direction:ltr;unicode-bidi:embed}
.wrap{max-width:1080px;margin:0 auto;padding:0 clamp(16px,4vw,40px)}
.prose{max-width:64ch}

/* ---------- top rail ---------- */
.rail{
  position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--ground) 88%,transparent);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--rule);
}
.rail .wrap{display:flex;align-items:center;gap:14px;height:56px;overflow-x:auto;scrollbar-width:none}
.rail .wrap::-webkit-scrollbar{display:none}
.brand{font-weight:800;letter-spacing:.02em;white-space:nowrap;color:var(--ink)}
.brand span{color:var(--leaf)}
.chips{display:flex;gap:2px;margin-inline-start:auto}
.chips a{
  display:flex;align-items:baseline;gap:5px;padding:5px 9px;border-radius:7px;
  text-decoration:none;color:var(--ink-2);font-size:13.5px;white-space:nowrap;
}
.chips a b{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-3);font-weight:500}
.chips a:hover{background:var(--sunk);color:var(--ink)}
.chips a:focus-visible,a:focus-visible,button:focus-visible{outline:2px solid var(--leaf);outline-offset:2px}

/* ---------- hero ---------- */
.hero{padding:clamp(44px,7vw,88px) 0 clamp(28px,4vw,44px)}
.eyebrow{
  font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--leaf);
  font-weight:700;margin:0 0 18px;
}
h1{
  font-family:"Frank Ruhl Libre",Georgia,serif;font-weight:800;
  font-size:clamp(38px,6.4vw,68px);line-height:1.04;letter-spacing:-.015em;
  margin:0 0 20px;text-wrap:balance;
}
.lede{font-size:clamp(17px,2.1vw,20px);color:var(--ink-2);margin:0;max-width:56ch;text-wrap:pretty}

/* ---------- stat strip ---------- */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
  background:var(--rule);border:1px solid var(--rule);border-radius:12px;overflow:hidden;margin:34px 0 0}
.stat{background:var(--surface);padding:18px 20px}
.stat .v{font-family:"Frank Ruhl Libre",Georgia,serif;font-size:clamp(26px,3.6vw,36px);
  font-weight:700;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.stat .k{font-size:12.5px;color:var(--ink-2);margin-top:7px}
.stat .s{font-size:11px;color:var(--ink-3);margin-top:3px}

/* ---------- sections ---------- */
section{padding:clamp(40px,6vw,72px) 0;border-top:1px solid var(--rule)}
.sechead{display:flex;align-items:baseline;gap:14px;margin:0 0 8px}
.num{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--leaf);
  font-weight:600;padding-top:6px}
h2{font-family:"Frank Ruhl Libre",Georgia,serif;font-size:clamp(25px,3.4vw,36px);
  font-weight:700;margin:0;letter-spacing:-.01em;text-wrap:balance}
h3{font-size:16px;font-weight:700;margin:34px 0 12px;letter-spacing:.005em}
h4{font-size:14px;font-weight:700;margin:0 0 6px}
p{margin:0 0 14px;text-wrap:pretty}
section > .wrap > .prose > p:last-child{margin-bottom:0}

/* ---------- cards / callouts ---------- */
.card{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:20px 22px;box-shadow:var(--shadow)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:24px 0 0}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:22px 0 0}
.note{border-inline-start:3px solid var(--leaf);background:var(--leaf-soft);
  padding:14px 18px;border-radius:0 10px 10px 0;margin:22px 0;font-size:15px;color:var(--ink)}
.note.warn{border-color:var(--open);background:var(--open-soft)}
.note.cold{border-color:var(--chill);background:var(--chill-soft)}
.note b{display:block;margin-bottom:4px}

/* ---------- tables ---------- */
.scroller{overflow-x:auto;border:1px solid var(--rule);border-radius:12px;background:var(--surface);margin:22px 0 0}
table{border-collapse:collapse;width:100%;font-size:14.5px;min-width:520px}
th,td{padding:10px 14px;text-align:right;border-bottom:1px solid var(--rule)}
thead th{background:var(--sunk);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink-2);font-weight:700}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover td{background:var(--sunk)}
td.n,th.n{font-variant-numeric:tabular-nums;white-space:nowrap}
td.name{font-weight:500}
caption{caption-side:bottom;padding:11px 14px;font-size:12.5px;color:var(--ink-3);text-align:right;border-top:1px solid var(--rule)}
tr.grp td{background:var(--sunk);font-size:12px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink-2);font-weight:700}

/* ---------- pills ---------- */
.pill{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700;
  padding:2px 9px;border-radius:999px;white-space:nowrap;letter-spacing:.02em}
.pill.ok{background:var(--leaf-soft);color:var(--leaf)}
.pill.draft{background:var(--hold-soft);color:var(--hold)}
.pill.move{background:var(--chill-soft);color:var(--chill)}
.pill.open{background:var(--open-soft);color:var(--open)}

/* ---------- filters ---------- */
.filters{display:flex;flex-wrap:wrap;gap:7px;margin:24px 0 0}
.filters button{
  font:inherit;font-size:13.5px;font-weight:600;padding:6px 14px;border-radius:999px;
  border:1px solid var(--rule-2);background:var(--surface);color:var(--ink-2);cursor:pointer;
  transition:background .12s,color .12s,border-color .12s;
}
.filters button:hover{border-color:var(--leaf);color:var(--ink)}
.filters button[aria-pressed="true"]{background:var(--leaf);border-color:var(--leaf);color:var(--surface)}

/* ---------- q&a ---------- */
.qa{border:1px solid var(--rule);border-radius:12px;background:var(--surface);overflow:hidden;margin:22px 0 0}
.qa details{border-bottom:1px solid var(--rule)}
.qa details:last-child{border-bottom:0}
.qa summary{display:flex;align-items:center;gap:10px;padding:13px 18px;cursor:pointer;
  font-weight:600;font-size:15.5px;list-style:none}
.qa summary::-webkit-details-marker{display:none}
.qa summary::after{content:"+";margin-inline-start:auto;color:var(--ink-3);font-weight:400;font-size:19px;line-height:1}
.qa details[open] summary::after{content:"−"}
.qa summary:hover{background:var(--sunk)}
.qa .body{padding:0 18px 16px;font-size:15px;color:var(--ink)}
.qa .body .src{margin-top:10px;font-size:12px;color:var(--ink-3)}

/* ---------- stages ---------- */
.stage{display:grid;grid-template-columns:auto 1fr;gap:18px;padding:18px 0;border-bottom:1px solid var(--rule)}
.stage:last-child{border-bottom:0}
.stage .idx{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--leaf);font-weight:600;padding-top:3px}
.stage .when{font-size:12px;color:var(--ink-3);margin-bottom:2px}
.script{background:var(--sunk);border-radius:10px;padding:13px 16px;margin-top:10px;font-size:14.5px;
  border-inline-start:2px solid var(--rule-2)}

/* ---------- provenance ---------- */
.stamp{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:20px 22px;margin:30px 0 0}
.stamp dl{display:grid;grid-template-columns:auto 1fr;gap:6px 18px;margin:12px 0 0;font-size:13.5px}
.stamp dt{color:var(--ink-3)}
.stamp dd{margin:0;font-family:"IBM Plex Mono",monospace;font-size:12.5px;direction:ltr;text-align:right;
  unicode-bidi:embed;word-break:break-all}
footer{border-top:1px solid var(--rule);padding:34px 0 60px;color:var(--ink-3);font-size:13.5px}
footer a{color:var(--leaf)}
.small{font-size:13px;color:var(--ink-2)}
ul.tight{margin:8px 0 0;padding-inline-start:20px}
ul.tight li{margin-bottom:5px}
@media(max-width:640px){
  .rail .wrap{height:52px}.chips{display:none}
  .stage{grid-template-columns:1fr;gap:6px}
}
"""

JS = """
document.querySelectorAll('[data-filter]').forEach(function(btn){
  btn.addEventListener('click', function(){
    var want = btn.getAttribute('data-filter');
    document.querySelectorAll('[data-filter]').forEach(function(b){
      b.setAttribute('aria-pressed', String(b === btn));
    });
    document.querySelectorAll('#drinks tbody tr').forEach(function(tr){
      var cat = tr.getAttribute('data-cat');
      tr.hidden = !(want === 'all' || cat === want || tr.classList.contains('grp') === false && false);
    });
    document.querySelectorAll('#drinks tbody tr.grp').forEach(function(tr){
      var cat = tr.getAttribute('data-cat');
      tr.hidden = !(want === 'all' || cat === want);
    });
  });
});
"""


# ------------------------------------------------------------------ build
def build():
    story = {c["id"]: c for c in load("story/chapters.yaml")["chapters"]}
    products = load("products/catalog.yaml")["products"]
    drinks = load("drinks/catalog.yaml")["drinks"]
    answers = load("answers/answer-bank.yaml")["answers"]
    rules = load("boundaries/refusals.yaml")["rules"]
    claims = load("claims/public-claims.yaml")["claims"]
    buyers = load("segments/buyers.yaml")
    motion = load("segments/sales-motion.yaml")

    live = [p for p in products if p.get("customer_facing")]
    held = [p for p in products if not p.get("customer_facing")]
    tom_held = [p for p in held if p.get("open_item") != "UNRESOLVED U-014"]
    teas = [p for p in live if p["family"] == "tea_concentrate"]
    tea_names = sorted({p["name_he"] for p in teas})
    iced = next(d for d in drinks if d["canva_page"] == 8)

    # the prose claims ten concentrates — prove it rather than trust it
    assert len(tea_names) == 10, f"tea concentrate count drifted: {len(tea_names)}"
    assert len(drinks) == 48, len(drinks)

    cats = ["תה", "צ'אי", "אבקות"]
    by_cat = {c: [d for d in drinks if d["category"] == c] for c in cats}

    o = []
    w = o.append

    w('<title>ספר העבודה של GT</title>')
    w('<link rel="preconnect" href="https://fonts.googleapis.com">')
    w('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
      'family=Frank+Ruhl+Libre:wght@500;700;800&family=Heebo:wght@400;500;600;700;800'
      '&family=IBM+Plex+Mono:wght@400;500;600&display=swap">')
    w(f"<style>{CSS}</style>")

    # ---- rail
    nav = [("01", "מה מוכרים", "sell"), ("02", "המספרים", "numbers"), ("03", "מחירון", "pricelist"),
           ("04", "48 משקאות", "drinks"), ("05", "הליד", "lead"), ("06", "מה שולחים", "send"),
           ("07", "בנק תשובות", "answers"), ("08", "הגבולות", "limits"), ("09", "עוד לא סגור", "open")]
    w('<div class="rail"><div class="wrap"><div class="brand">GT <span>everyday</span></div><nav class="chips">')
    for n, label, anchor in nav:
        w(f'<a href="#{anchor}"><b>{n}</b>{e(label)}</a>')
    w('</nav></div></div>')

    # ---- hero
    h = story["hero"]
    w('<header class="hero"><div class="wrap">')
    w(f'<p class="eyebrow">{e(h["eyebrow"])}</p>')
    w(f'<h1>{e(h["title"])}</h1>')
    w(f'<p class="lede">{e(h["lede"])}</p>')
    w('<div class="stats">')
    for v, k, s in (
        (money(iced["cost"]), "עלות תמצית לכוס", "חליטה קרה · 50 מ״ל"),
        (money(iced["price"]), "מחיר מומלץ לצרכן", "כולל מע״מ 18%"),
        (f'{iced["margin_pct"]}%', "רווח על ההכנסה נטו", "נגזר מהנוסחה"),
        (str(len(drinks)), "משקאות", "בשלוש קטגוריות"),
        (str(len(live)), "מוצרים במחירון",
         f"{len(tom_held)} מוחזקים עד הכרעת טום"),
    ):
        w(f'<div class="stat"><div class="v">{e(v)}</div><div class="k">{e(k)}</div><div class="s">{e(s)}</div></div>')
    w('</div>')
    w('<div class="note cold"><b>העמוד הזה הוא תצוגה, לא המקור.</b>'
      'כל מספר כאן נקרא מ-<span class="mono">Sales-Machine/knowledge/</span> ונבדק מול המקור המאושר '
      'לפני שהודפס. מחיר משתנה — מעדכנים במאגר, והעמוד נבנה מחדש.</div>')
    w('</div></header>')

    # ---- 01
    c = story["what_we_sell"]
    lv = story["liquid_vs_powder"]
    w(f'<section id="sell"><div class="wrap"><div class="sechead"><span class="num">{c["number"]}</span>'
      f'<h2>{e(c["title"])}</h2></div><div class="prose">')
    for p in c["paragraphs"]:
        w(f"<p>{e(p)}</p>")
    w('</div>')
    w(f'<h3>{e(lv["title"])}</h3><p class="prose small">{e(lv["lede"])}</p><div class="grid2">')
    for col in lv["columns"]:
        w(f'<div class="card"><h4>{e(col["label"])} <span class="small">· {e(col["sub"])}</span></h4>'
          f'<p class="small" style="margin:0">{e(col["text"])}</p></div>')
    w('</div></div></section>')

    # ---- 02
    n = story["numbers_note"]
    w(f'<section id="numbers"><div class="wrap"><div class="sechead"><span class="num">{n["number"]}</span>'
      f'<h2>{e(n["title"])}</h2></div><p class="prose">{e(n["lede"])}</p>')
    w('<div class="scroller"><table><thead><tr>'
      '<th>מוצר</th><th class="n">מחיר ליחידה</th><th class="n">מנה</th>'
      '<th class="n">מנות ליחידה</th><th class="n">עלות למנה</th></tr></thead><tbody>')
    seen = set()
    for p in live:
        if not p.get("servings_per_unit") or p["name_he"] in seen:
            continue
        key = (p["family"], p.get("pack"))
        if p["family"] == "tea_concentrate" and key in seen:
            continue
        seen.add(key)
        seen.add(p["name_he"] if p["family"] != "tea_concentrate" else key)
        label = ("תמצית תה" if p["family"] == "tea_concentrate"
                 else p["name_he"].split("·")[0].strip())
        w(f'<tr><td class="name">{e(label)} · {e(p["pack"])}</td>'
          f'<td class="n">{money(p["price_exvat"])}</td><td class="n">{e(p["serving"])}</td>'
          f'<td class="n">{p["servings_per_unit"]}</td>'
          f'<td class="n"><b>{money(p["cost_per_serving"])}</b></td></tr>')
    w(f'</tbody><caption>{e(n["footnote"])} · מחירי היחידה ללא מע״מ '
      f'(<span class="mono">knowledge/products/catalog.yaml</span>)</caption></table></div>')

    w('<h3>לפי קטגוריית משקה</h3><div class="scroller"><table><thead><tr>'
      '<th>קטגוריה</th><th class="n">משקאות</th><th class="n">עלות למנה</th>'
      '<th class="n">מחיר</th><th class="n">רווח</th></tr></thead><tbody>')
    for cat in cats:
        g = by_cat[cat]
        w(f'<tr><td class="name">{e(cat)}</td><td class="n">{len(g)}</td>'
          f'<td class="n">{money(min(d["cost"] for d in g))}–{money(max(d["cost"] for d in g))}</td>'
          f'<td class="n">{money(min(d["price"] for d in g))}–{money(max(d["price"] for d in g))}</td>'
          f'<td class="n">{min(d["margin_pct"] for d in g)}–{max(d["margin_pct"] for d in g)}%</td></tr>')
    w('</tbody><caption>מחושב מ-48 המשקאות, לא מוקלד '
      '(<span class="mono">knowledge/drinks/catalog.yaml</span>)</caption></table></div>')
    w(f'<div class="note"><b>הכלל</b>{e(n["callout"])}</div>')
    w('</div></section>')

    # ---- 03
    pl = story["pricelist_note"]
    w(f'<section id="pricelist"><div class="wrap"><div class="sechead"><span class="num">{pl["number"]}</span>'
      f'<h2>{e(pl["title"])}</h2></div><p class="prose">{e(pl["lede"])}</p>')
    w('<div class="scroller"><table><thead><tr><th>תמצית</th><th>רכיבים</th>'
      '<th class="n">500 מ״ל</th><th class="n">1 ליטר</th></tr></thead><tbody>')
    for name in tea_names:
        rows = [p for p in teas if p["name_he"] == name]
        half = next((p for p in rows if p["pack"].startswith("500")), None)
        full = next((p for p in rows if p["pack"].startswith("1")), None)
        ing = next((p.get("ingredients_he", "") for p in rows if p.get("ingredients_he")), "")
        caff = "" if any(not p.get("caffeine_free") for p in rows) else ' <span class="pill ok">נטול קפאין</span>'
        w(f'<tr><td class="name">{e(name)}{caff}</td><td class="small">{e(ing)}</td>'
          f'<td class="n">{money(half["price_exvat"]) if half else "—"}</td>'
          f'<td class="n">{money(full["price_exvat"]) if full else "—"}</td></tr>')
    w('</tbody><caption>ללא מע״מ · מקור: <span class="mono">docs/pricing/2026-08-05_shopify_products_exvat.tsv</span>'
      '</caption></table></div>')

    for title, fams in (("אבקות וערכות", {"powder", "kit"}),
                        ("מחיות פרי", {"puree"}), ("עזרי הכנה", {"accessory"})):
        rows = [p for p in live if p["family"] in fams]
        if not rows:
            continue
        w(f'<h3>{e(title)}</h3><div class="scroller"><table><thead><tr><th>פריט</th>'
          '<th class="mono">SKU</th><th class="n">מחיר</th><th class="n">עלות למנה</th></tr></thead><tbody>')
        for p in sorted(rows, key=lambda r: -float(r["price_exvat"])):
            cps = money(p["cost_per_serving"]) if p.get("cost_per_serving") else "—"
            w(f'<tr><td class="name">{e(p["name_he"])}</td><td class="mono">{e(p["sku"])}</td>'
              f'<td class="n">{money(p["price_exvat"])}</td><td class="n">{cps}</td></tr>')
        w('</tbody></table></div>')

    w(f'<div class="note warn"><b>שש שורות ירדו מהמחירון — {e(pl["changed_from_book"].split("—")[0].strip())}</b>')
    w('<ul class="tight">')
    for p in tom_held:
        why = p.get("why_not_customer_facing", "").split(".")[0].strip()
        w(f'<li><b>{e(p["name_he"])}</b> — {e(why)} <span class="pill open">{e(p.get("open_item", "פתוח"))}</span></li>')
    w('</ul></div>')
    w('</div></section>')

    # ---- 04
    dn = story["drinks_note"]
    w(f'<section id="drinks"><div class="wrap"><div class="sechead"><span class="num">{dn["number"]}</span>'
      f'<h2>{e(dn["title"])}</h2></div><p class="prose">{e(dn["lede"])}</p>')
    w('<div class="filters">')
    w(f'<button type="button" data-filter="all" aria-pressed="true">הכל · {len(drinks)}</button>')
    for cat in cats:
        w(f'<button type="button" data-filter="{e(cat)}" aria-pressed="false">{e(cat)} · {len(by_cat[cat])}</button>')
    w('</div>')
    w('<div class="scroller"><table><thead><tr><th>משקה</th><th class="n">עלות</th>'
      '<th class="n">מחיר</th><th class="n">רווח לכוס</th><th class="n">רווח</th></tr></thead><tbody>')
    for cat in cats:
        fam = None
        for d in by_cat[cat]:
            if d["family"] != fam:
                fam = d["family"]
                w(f'<tr class="grp" data-cat="{e(cat)}"><td colspan="5">{e(cat)} · {e(fam)}</td></tr>')
            w(f'<tr data-cat="{e(cat)}"><td class="name">{e(d["name"])}</td>'
              f'<td class="n">{money(d["cost"])}</td><td class="n">{money(d["price"])}</td>'
              f'<td class="n">{money(d["profit_per_cup"])}</td>'
              f'<td class="n"><b>{d["margin_pct"]}%</b></td></tr>')
    w('</tbody><caption>עלות ורווח לכוס ללא מע״מ · מחיר כולל מע״מ · '
      'רווח = <span class="mono">round((price/1.18 − cost) / (price/1.18) × 100)</span> — נגזר, לא מוקלד'
      '</caption></table></div></div></section>')

    # ---- 05
    ln = story["lead_note"]
    w(f'<section id="lead"><div class="wrap"><div class="sechead"><span class="num">{ln["number"]}</span>'
      f'<h2>{e(ln["title"])}</h2></div><p class="prose">{e(ln["lede"])}</p><div class="grid3">')
    for b in buyers["buyer_types"]:
        w(f'<div class="card"><h4>{e(b["name_he"])}</h4>')
        if b.get("authority_he"):
            w(f'<p class="small" style="margin:0 0 8px">{e(b["authority_he"])}</p>')
        w(f'<p class="small" style="margin:0"><b>מה עובד:</b> {e(b["what_works_he"])}</p></div>')
    w('</div>')
    w('<h3>רצף השיחה</h3><ul class="tight small">')
    for pr in motion["card"]["principles"]:
        w(f"<li>{e(pr)}</li>")
    w('</ul><div style="margin-top:18px">')
    for i, st in enumerate(motion["stages"], 1):
        w(f'<div class="stage"><div class="idx">{i:02d}</div><div>'
          f'<div class="when">{e(st["when"])}</div><h4>{e(st["name_he"])}</h4>')
        for key in ("do_he", "why_he", "shape_he", "also_he"):
            if st.get(key):
                w(f'<p class="small" style="margin:0 0 6px">{e(st[key])}</p>')
        if st.get("script_he"):
            w(f'<div class="script">{e(st["script_he"])}</div>')
        if st.get("blocked_note"):
            w(f'<p class="small" style="margin:8px 0 0"><span class="pill open">{e(st["blocked_by"])}</span> '
              f'{e(st["blocked_note"])}</p>')
        if st.get("changed_from_book"):
            w(f'<p class="small" style="margin:8px 0 0"><span class="pill draft">שונה מהספר</span> '
              f'{e(st["changed_from_book"])}</p>')
        w('</div></div>')
    w('</div><h3>כשאין תשובה</h3><div class="grid3">')
    for f in motion["follow_ups"]:
        head = f'יום {f["day"]}' if isinstance(f["day"], int) else "אחרי כן"
        w(f'<div class="card"><div class="when small">{e(head)}</div><h4>{e(f["name_he"])}</h4>')
        if f.get("rule_he"):
            w(f'<p class="small" style="margin:0 0 6px">{e(f["rule_he"])}</p>')
        if f.get("why_he"):
            w(f'<p class="small" style="margin:0 0 6px">{e(f["why_he"])}</p>')
        if f.get("script_he"):
            w(f'<div class="script">{e(f["script_he"])}</div>')
        w('</div>')
    w('</div></div></section>')

    # ---- 06
    sn = story["send_note"]
    w(f'<section id="send"><div class="wrap"><div class="sechead"><span class="num">{sn["number"]}</span>'
      f'<h2>{e(sn["title"])}</h2></div><p class="prose">{e(sn["lede"])}</p><div class="grid2">')
    for v in buyers["venue_types"]:
        if v.get("status") == "unresolved":
            continue
        w(f'<div class="card"><h4>{e(v["name_he"])}</h4>'
          f'<p class="small" style="margin:0 0 6px"><b>נכנסים עם:</b> {e(v["entry_product"])}</p>'
          f'<p class="small" style="margin:0">{e(v["why_he"])}</p>')
        if v.get("caution"):
            w(f'<p class="small" style="margin:8px 0 0;color:var(--open)">{e(v["caution"])}</p>')
        w('</div>')
    w('</div><h3>לאן מרחיבים אחרי ההזמנה הראשונה</h3><div class="scroller"><table><thead><tr>'
      '<th>מ־</th><th>אל</th><th>מה זה עולה ללקוח</th></tr></thead><tbody>')
    for x in motion["expansion_map"]:
        text = x.get("cost_to_customer_he") or x.get("what_he", "")
        extra = f' <span class="pill open">{e(x["caution"])}</span>' if x.get("caution") else ""
        w(f'<tr><td class="name">{e(x["from"])}</td><td class="name">{e(x["to"])}</td>'
          f'<td class="small">{e(text)}{extra}</td></tr>')
    w('</tbody></table></div></div></section>')

    # ---- 07
    an = story["answers_note"]
    pill = {"מאושר": "ok", "טיוטה": "draft", "העברה": "move"}
    w(f'<section id="answers"><div class="wrap"><div class="sechead"><span class="num">{an["number"]}</span>'
      f'<h2>{e(an["title"])}</h2></div><p class="prose">{e(an["lede"])}</p>')
    counts = {k: sum(1 for a in answers if a["סטטוס"] == k) for k in pill}
    w('<p class="small">'
      f'<span class="pill ok">מאושר · {counts["מאושר"]}</span> '
      f'<span class="pill draft">טיוטה · {counts["טיוטה"]}</span> '
      f'<span class="pill move">העברה · {counts["העברה"]}</span> — '
      'שורת "העברה" היא תשובה תקפה. היא מה שמונע ניחוש.</p>')
    w('<div class="qa">')
    for a in answers:
        st = a["סטטוס"]
        body = a.get("תשובה") or a.get("say_he") or ""
        w(f'<details><summary><span class="pill {pill[st]}">{e(st)}</span>{e(a["שאלה"])}</summary>'
          f'<div class="body"><p style="margin:0">{e(body)}</p>')
        if a.get("caution"):
            w(f'<p class="small" style="margin:8px 0 0;color:var(--open)">⚠ {e(a["caution"])}</p>')
        if a.get("changed_from_book"):
            w(f'<p class="small" style="margin:8px 0 0">שונה מהספר: {e(a["changed_from_book"])}</p>')
        w(f'<div class="src mono">{e(a["source"])}</div></div></details>')
    w('</div></div></section>')

    # ---- 08
    bn = story["boundaries_note"]
    w(f'<section id="limits"><div class="wrap"><div class="sechead"><span class="num">{bn["number"]}</span>'
      f'<h2>{e(bn["title"])}</h2></div><p class="prose">{e(bn["lede"])}</p>')
    w('<div class="scroller"><table><thead><tr><th>מתי זה נדלק</th><th>מה אומרים</th>'
      '<th>למי מעבירים</th></tr></thead><tbody>')
    sev = {"critical": "open", "high": "draft", "medium": "move", "low": "ok"}
    for r in rules:
        if r["id"] == "unmatched_default":
            continue
        keys = "، ".join(str(p) for p in r["patterns"][:6])
        tgt = r.get("escalate_to") or "—"
        w(f'<tr><td class="name">{e(r["id"])} <span class="pill {sev[r["severity"]]}">{e(r["severity"])}</span>'
          f'<div class="small" style="color:var(--ink-3)">{e(keys)}…</div></td>'
          f'<td class="small">{e(r["say_he"])}</td><td class="small">{e(tgt)}</td></tr>')
    d = next(r for r in rules if r["id"] == "unmatched_default")
    w(f'<tr><td class="name">ברירת מחדל <span class="pill open">critical</span>'
      f'<div class="small" style="color:var(--ink-3)">כל מה שלא נתפס למעלה</div></td>'
      f'<td class="small">{e(d["say_he"])}</td><td class="small">alexander</td></tr>')
    w('</tbody><caption>מקור: <span class="mono">knowledge/boundaries/refusals.yaml</span> — '
      'נבדק לפני בנק התשובות. סירוב גובר על תשובה, תמיד.</caption></table></div>')
    w('<div class="grid2">')
    for co in bn["callouts"]:
        w(f'<div class="note warn" style="margin:0"><b>{e(co["title"])}</b>{e(co["text"])}</div>')
    w('</div></div></section>')

    # ---- 09
    on = story["open_note"]
    w(f'<section id="open"><div class="wrap"><div class="sechead"><span class="num">{on["number"]}</span>'
      f'<h2>{e(on["title"])}</h2></div><p class="prose">{e(on["lede"])}</p>')
    w('<h3>ארבע החלטות מסחריות — רק טום סוגר</h3><div class="grid2">')
    for t, txt in (("חבילות ההתחלה", "שם, תוכן מדויק ומחיר לכל אחת משלוש החבילות."),
                   ("זמן אספקה", "בימי עסקים, והאם מרכז ופריפריה שונים. \"פעמיים בשבוע\" היא תדירות, לא תשובה."),
                   ("מדרגות ההנחה", "המספרים עצמם, במסלול התשלום המיידי."),
                   ("התחייבות ובלעדיות", "חוזה? מינימום חודשי? בלעדיות אזורית?")):
        w(f'<div class="card"><h4>{e(t)} <span class="pill open">טום</span></h4>'
          f'<p class="small" style="margin:0">{e(txt)}</p></div>')
    w('</div>')
    w('<h3>שלוש טענות שנאמרו ללקוחות בלי מקור</h3><div class="scroller"><table><thead><tr>'
      '<th>הטענה</th><th>מה נמצא בבדיקה</th></tr></thead><tbody>')
    for cl in claims:
        if cl["authority"] != "unsourced":
            continue
        w(f'<tr><td class="name">{e(cl["text_he"])} <span class="pill open">{e(cl.get("open_item", "פתוח"))}</span></td>'
          f'<td class="small">{e(cl["evidence"])}</td></tr>')
    w('</tbody><caption>עד הכרעת טום — המשפטים האלה ירדו מהעמוד ומהנוסחים. '
      '<span class="mono">knowledge/claims/public-claims.yaml</span></caption></table></div>')
    w('<div class="note cold"><b>פגמי הקטלוג שהספר מנה — לא תוקנו כאן, במכוון.</b>'
      'שלושה מתכונים שמפנים לתמצית שלא קיימת, מתכון וניל/אגבה כפול, "20–25 כוסות", '
      'מספור כפול, וארבעה קטלוגי קנבה שרק אחד מהם בתוקף — כולם בבעלות סשן תפריטי הקטגוריות. '
      'נרשמו והועברו.</div>')
    w('</div></section>')

    # ---- stamp
    w('<section id="build"><div class="wrap"><div class="stamp">')
    w('<h4>מאיפה העמוד הזה נבנה</h4>')
    w('<p class="small" style="margin:0">המאגר הוא האמת. העמוד הזה הוא תצוגה שלו, '
      'שנבנתה מהקבצים למטה אחרי שכולם עברו את הבודק.</p><dl>')
    for k, v in (("build", dt.date.today().isoformat()),
                 ("Sales-Machine", f"{sha(SALES)} · branch claude/gt-specialty-beverages-0p8sbr"),
                 ("production-brain", f"{sha(BRAIN)} · branch claude/gt-specialty-beverages-0p8sbr"),
                 ("generator", "scripts/knowledge/build_book.py"),
                 ("gate", "scripts/knowledge/reconcile.py cards → 0 rows"),
                 ("drinks", ".claude/skills/drinks-pricelist/drinks_final_figures.json (2026-08-27)"),
                 ("prices", "docs/pricing/2026-08-05_shopify_products_exvat.tsv"),
                 ("sellable", "docs/warehouses/catalog-truth.md (Tom 2026-08-06)")):
        w(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>")
    w('</dl></div></div></section>')

    f = story["footer"]
    w(f'<footer><div class="wrap"><p style="margin:0 0 6px"><b>GT everyday</b></p>'
      f'<p style="margin:0 0 14px">{e(f["contact"])}</p>'
      f'<p class="small" style="margin:0">כשמחיר משתנה — מעדכנים במאגר קודם, ורק אחר כך בעיצוב. '
      f'עכשיו זה גם נכון מכנית.</p></div></footer>')
    w(f"<script>{JS}</script>")
    return "\n".join(o)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=os.path.join(
        "/tmp/claude-0/-home-user/f269eb24-76a2-5515-bf81-6a3bfa3dd965/scratchpad", "gt-knowledge-book.html"))
    a = ap.parse_args()
    doc = build()
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"wrote {a.out} — {len(doc):,} bytes")
