#!/usr/bin/env python3
"""
GT Everyday — build the drinks cost sheet from the approved final figures.

Source of truth : drinks_final_figures.json — the file Stage B validated the
                  Canva catalog against. No figure is recomputed here; the only
                  derived value is the bar geometry (cost as a share of net
                  revenue), which is a drawing instruction, not a number shown.
Output          : pricelist.html   (render to PDF with shot.py)

Two structural facts drive the layout, both read off the live catalog:

  1. Every family has exactly one recommended price. In a flat table that means
     48 repeated price cells; here the price sits on the family band once, which
     is how the business actually prices.
  2. The family codes (01…10) are the deck's own running headers, so they are
     wayfinding a reader can act on, not decoration. Same for the page refs.
"""

import html
import json
from pathlib import Path

D = Path(__file__).parent
FIG = D / "drinks_final_figures.json"
CSS = D / "style.css"
OUT = D / "pricelist.html"

VAT = 1.18
NO_STAR = {8, 16, 17, 18}

# (code, hebrew name, latin name, page numbers) — mirrors the catalog's own bands
FAMILIES = [
    ("01", "חליטות קרות",     "iced tea",        [8, 9, 10, 11, 12, 13, 14]),
    ("02", "לימונדות",         "lemonade",        [16, 17, 18]),
    ("03", "משקאות דגל",       "signature",       [20, 21, 22, 23]),
    ("04", "גזוז",             "gazoz",           [25, 26, 27]),
    ("05", "אייס מאצ'ה",       "ice matcha",      [29, 30, 31, 32, 33, 34]),
    ("06", "מאצ'ה ספיישלס",    "matcha specials", [36, 37, 38, 39, 40]),
    ("07", "מאצ'ה קוקוס",      "matcha coconut",  [42, 43, 44, 45, 46]),
    ("08", "צ'אי מסאלה",       "chai massala",    [48, 49, 50, 51, 52, 53]),
    ("09", "צ'אי קולד פואם",   "chai cold foam",  [55, 56, 57, 58]),
    ("10", "אייס אובה",        "ice ube",         [60, 61, 62, 63, 64]),
]


def e(s):
    return html.escape(str(s))


def money(s):
    """₪4.73* → (4.73, '*')"""
    body = s.lstrip("₪")
    star = "*" if body.endswith("*") else ""
    return float(body.rstrip("*")), star


def main():
    fig = json.loads(FIG.read_text(encoding="utf-8"))
    meta, pages = fig["_meta"], fig["pages"]

    mapped = [p for *_, ps in FAMILIES for p in ps]
    if sorted(mapped) != sorted(int(k) for k in pages):
        raise SystemExit("family map out of sync with the figures file")

    costs, nets = [], []
    blocks = []
    for code, he, latin, page_nums in FAMILIES:
        prices = {pages[str(p)]["price"] for p in page_nums}
        if len(prices) != 1:
            raise SystemExit(f"family {code} has mixed prices {prices} — price cannot sit on the band")
        price_txt = prices.pop()
        price = float(price_txt.lstrip("₪"))
        net = price / VAT

        rows = []
        for p in page_nums:
            d = pages[str(p)]
            cost, _ = money(d["cost"])
            star = "" if p in NO_STAR else "*"
            keep, _ = money(d["prof"].replace(" לכוס", ""))
            share = cost / net * 100
            costs.append(cost)
            nets.append(net)
            rows.append(
                "<tr>"
                f'<td class="cell-name"><span class="page-ref">{p}</span>'
                f'<span class="drink">{e(d["name"])}</span></td>'
                f'<td class="cell-bar"><div class="bar">'
                f'<div class="bar-cost" style="width:{share:.1f}%"></div>'
                f'<span class="bar-pct">{e(d["marg"])}</span></div></td>'
                f'<td class="cell-cost"><span class="cost">₪{cost:.2f}'
                f'<span class="star">{star}</span></span></td>'
                f'<td class="cell-keep"><span class="keep">₪{keep:.2f}</span></td>'
                "</tr>"
            )

        blocks.append(
            '<section class="family">'
            '<div class="family-head">'
            f'<span class="family-code latin">{code}</span>'
            f'<span class="family-name">{e(he)}</span>'
            f'<span class="family-latin latin">{e(latin)}</span>'
            f'<span class="family-price">מחיר מומלץ <b>{e(price_txt)}</b></span>'
            "</div>"
            f'<table class="rows">{"".join(rows)}</table>'
            "</section>"
        )

    avg_cost = sum(costs) / len(costs)
    avg_net = sum(nets) / len(nets)
    avg_share = avg_cost / avg_net * 100
    vat_pct = round(meta["vat_rate"] * 100)

    doc = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>GT Everyday — מה נשאר לך מכל כוס · SUMMER 2026</title>
<style>{CSS.read_text(encoding="utf-8")}</style>
</head>
<body>

<header class="masthead">
  <p class="masthead-brand latin">GT EVERYDAY</p>
  <h1 class="masthead-title">מה נשאר לך מכל כוס</h1>
  <p class="masthead-sub latin">cost per cup · summer 2026</p>

  <div class="hero">
    <p class="hero-label">כוס ממוצעת בקטלוג, לפי גודל:</p>
    <div class="hero-bar">
      <div class="hero-bar-cost" style="width:{avg_share:.1f}%"></div>
      <span class="hero-tag hero-tag-cost">עלות רכיבים ₪{avg_cost:.2f}</span>
      <span class="hero-tag hero-tag-keep">נשאר לך ₪{avg_net - avg_cost:.2f}</span>
    </div>
    <div class="hero-foot">
      <span class="hero-foot-facts">
        <span><b>{len(pages)}</b> משקאות</span>
        <span><b>{len(FAMILIES)}</b> משפחות</span>
        <span>הזולה <b>₪{min(costs):.2f}</b>, היקרה <b>₪{max(costs):.2f}</b></span>
      </span>
      <span>כל פס באורך אחיד = כוס אחת. החלק הכתום הוא מה שהיא עולה לך.</span>
    </div>
  </div>

  <div class="colkey">
    <span class="colkey-name"></span>
    <span class="colkey-bar">אחוז הרווח</span>
    <span class="colkey-cost">עלות</span>
    <span class="colkey-keep">נשאר לך</span>
  </div>
</header>

{''.join(blocks)}

<div class="notes">
  <p><b>הבסיס.</b> עלות הרכיבים היא ללא מע״מ. המחיר המומלץ הוא לצרכן, כולל מע״מ {vat_pct}%.
     "נשאר לך" = המחיר פחות מע״מ, פחות עלות הרכיבים. גם האחוז שליד כל פס מחושב כך.</p>
  <p><b>* כולל הערכת עלות גרניש/קצף.</b> מופיע ב־44 מתוך {len(pages)} המשקאות.</p>
  <p>המספרים זהים אחד לאחד לקטלוג המשקאות. המספר האפור לפני כל שם הוא העמוד המקביל בו.</p>
</div>

</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT}  ({len(pages)} drinks, {len(FAMILIES)} families, avg cost share {avg_share:.1f}%)")


if __name__ == "__main__":
    main()
