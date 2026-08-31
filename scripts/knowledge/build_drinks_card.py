#!/usr/bin/env python3
"""Regenerate Sales-Machine/knowledge/drinks/catalog.yaml from the approved figures.

The card is a rendering of .claude/skills/drinks-pricelist/drinks_final_figures.json
(2026-08-27). Never hand-edit the card — change the authority and re-run this.
Category/family grouping mirrors chapter 04 of the knowledge book; the base-product
column mirrors chapter 06 ("the line that matters is liquid vs powder").
"""
import io
import json
import os

BRAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALES = os.path.join(os.path.dirname(BRAIN), "Sales-Machine")
AUTH = os.path.join(BRAIN, ".claude/skills/drinks-pricelist/drinks_final_figures.json")
OUT = os.path.join(SALES, "knowledge/drinks/catalog.yaml")

FAMILY = {
    **{p: ("תה", "חליטות קרות ICED TEA") for p in (8, 9, 10, 11, 12, 13, 14)},
    **{p: ("תה", "לימונדות LEMONADE") for p in (16, 17)},
    **{p: ("תה", "סיגנצ'ר FRUITEA") for p in (20, 21, 22, 23)},
    **{p: ("תה", "גזוז GAZOZ") for p in (25, 26, 27)},
    18: ("צ'אי", "לימונדה"),
    **{p: ("צ'אי", "צ'אי מסאלה CHAI MASSALA") for p in (48, 49, 50, 51, 52, 53)},
    **{p: ("צ'אי", "קולד פואם COLD FOAM") for p in (55, 56, 57, 58)},
    **{p: ("אבקות", "אייס מאצ'ה ICE MATCHA") for p in (29, 30, 31, 32, 33, 34)},
    **{p: ("אבקות", "מאצ'ה ספיישל MATCHA SPECIALS") for p in (36, 37, 38, 39, 40)},
    **{p: ("אבקות", "מאצ'ה קוקוס MATCHA COCONUT") for p in (42, 43, 44, 45, 46)},
    **{p: ("אבקות", "אובה UBE") for p in (60, 61, 62, 63, 64)},
}
BASE = {"תה": "tea_concentrate", "צ'אי": "tea_concentrate (NAMASTEA)", "אבקות": "powder"}

HEADER = """# GT — 48 המשקאות. נוצר אוטומטית; ⊥ לערוך ביד.
# מקור יחיד לעלות/מחיר/רווח:
#   gt-factory-os-production-brain/.claude/skills/drinks-pricelist/drinks_final_figures.json (2026-08-27)
# הקובץ docs/pricing/2026-08-05_drinks_final_figures.json הוא גרסה מוחלפת — ⊥ לקרוא ממנו.
# מפתח: canva_page — מספר העמוד ב"קטלוג משקאות סופי 26" (הקטלוג היחיד בתוקף).
card:
  id: drinks/catalog
  title: 48 המשקאות — עלות, מחיר מומלץ, רווח
  type: drinks-catalog
  authority: system_verified
  date: 2026-08-27
  freshness: review_30d
  source: >-
    gt-factory-os-production-brain/.claude/skills/drinks-pricelist/drinks_final_figures.json
    (_meta.date 2026-08-27 — מודל עלות בוטום-אפ מ-GT_Summer_Menu_2026.xls, טום)
  generated_by: gt-factory-os-production-brain/scripts/knowledge/build_drinks_card.py
  formulas:
    profit: price / 1.18 - cost
    margin_pct: round(profit / (price / 1.18) * 100)
  cost_basis: >-
    ex-VAT ingredients only — ⊥ גרניש, ⊥ קרח, ⊥ מים, ⊥ סודה, ⊥ אריזה, ⊥ עבודה
  price_basis: VAT-inclusive (18%)

drinks:
"""


def main():
    with open(AUTH, encoding="utf-8") as fh:
        data = json.load(fh)
    if data["_meta"]["date"] != "2026-08-27":
        raise SystemExit("authority file is not the 2026-08-27 set — refusing to generate")
    pages = {int(k): v for k, v in data["pages"].items()}
    buf = io.StringIO()
    buf.write(HEADER)
    for page in sorted(pages):
        v = pages[page]
        category, family = FAMILY[page]
        cost = float(v["cost"].replace("₪", ""))
        price = float(v["price"].replace("₪", ""))
        margin = int(v["marg"].replace("%", ""))
        derived = round((price / 1.18 - cost) / (price / 1.18) * 100)
        if derived != margin:
            raise SystemExit(f"page {page}: stored margin {margin}% != derived {derived}%")
        buf.write(
            f"  - canva_page: {page}\n"
            f"    name: {v['name']}\n"
            f"    category: {category}\n"
            f"    family: {family}\n"
            f"    cost: {cost:.2f}\n"
            f"    price: {price:.0f}\n"
            f"    margin_pct: {margin}\n"
            f"    profit_per_cup: {price / 1.18 - cost:.2f}\n"
            f"    base: {BASE[category]}\n"
            f"    source: drinks_final_figures.json p.{page}\n"
            f"    date: '2026-08-27'\n"
            f"    authority: system_verified\n"
        )
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
    print(f"wrote {OUT} — {len(pages)} drinks, all margins re-derived")


if __name__ == "__main__":
    main()
