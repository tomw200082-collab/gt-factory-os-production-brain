#!/usr/bin/env python3
"""Build knowledge/drinks/recipes.yaml — what actually goes into each of the 48 drinks.

The drinks card has always carried cost, price and margin and never the recipe, so an
agent could quote ₪3.25 → ₪20 and still not say how the drink is made. This closes that.

Two sources, graded apart on purpose:

  doses  — GT_FOOD_COST_2026-08-27.xlsx, column "פירוט עלות". This is the ingredient
           breakdown the APPROVED cost model is built from (Tom 2026-08-27), so every
           dose is the one that produces the approved cost. Graded system_verified,
           and proved: each drink's parts are summed and checked against the cost in
           knowledge/drinks/catalog.yaml.

  serve  — docs/pricing/canva_workfiles/recipes.json, field "chips". The bar-facing
           method: glass, ice, garnish, order. Dated 2026-08-05 and from the pricing
           generation that was later SUPERSEDED — so its cost and price fields are
           read by nothing here, only the text. Graded doc_confirmed @ 2026-08-05.

The cost basis excludes garnish, ice, water, soda and labour, which is exactly why
both halves are needed: the doses say what you pay for, the chips say what you serve.

    python3 scripts/knowledge/build_recipes_card.py [--check]
"""
import argparse
import json
import os
import re
import subprocess
import sys

import openpyxl
import yaml

BRAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALES = os.path.join(os.path.dirname(BRAIN), "Sales-Machine")
XLSX = os.path.join(BRAIN, "docs/pricing/GT_FOOD_COST_2026-08-27.xlsx")
CHIPS = os.path.join(BRAIN, "docs/pricing/canva_workfiles/recipes.json")
CATALOG = os.path.join(SALES, "knowledge/drinks/catalog.yaml")
OUT = os.path.join(SALES, "knowledge/drinks/recipes.yaml")

DOSE_COST = re.compile(r"₪\s*([0-9]+(?:\.[0-9]+)?)\s*$")

# The workbook prints each part's cost rounded to the agora, so a drink whose parts
# carry a third decimal can miss its own total by ₪0.01. One drink does. It is recorded
# here rather than papered over — the approved cost stands, the parts explain it.
ROUNDING_TOLERANCE = 0.011


def parse_doses(detail):
    """'50 מ"ל GT ₪3.25 + 233 מ"ל חלב ₪1.87' → [{item, cost}, ...]"""
    out = []
    for part in detail.split(" + "):
        part = part.strip()
        m = DOSE_COST.search(part)
        if not m:
            raise ValueError(f"dose without a cost: {part!r}")
        out.append({"item": DOSE_COST.sub("", part).strip(), "cost": float(m.group(1))})
    return out


def load_sources():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    xl = {}
    for r in wb["FOOD COST"].iter_rows(min_row=6, max_row=55, values_only=True):
        if r[0] is None:
            continue
        xl[str(r[2]).strip()] = {
            "n": int(r[0]),
            "cost": float(r[3]),
            "price": float(r[4]),
            "detail": str(r[8]).strip(),
        }
    chips = {c["heb"].strip(): c["chips"] for c in json.load(open(CHIPS, encoding="utf-8"))}
    card = {d["name"].strip(): d for d in yaml.safe_load(open(CATALOG, encoding="utf-8"))["drinks"]}
    return xl, chips, card


def build():
    xl, chips, card = load_sources()
    problems = []

    for label, missing in (
        ("in the workbook, not in the approved card", set(xl) - set(card)),
        ("in the approved card, not in the workbook", set(card) - set(xl)),
        ("in the approved card, no serve method", set(card) - set(chips)),
    ):
        for name in sorted(missing):
            problems.append(f"{label}: {name}")

    recipes = []
    for name, d in sorted(card.items(), key=lambda kv: kv[1]["canva_page"]):
        x = xl.get(name)
        if not x:
            continue
        doses = parse_doses(x["detail"])
        parts = round(sum(p["cost"] for p in doses), 2)
        approved = float(d["cost"])
        delta = round(parts - approved, 2)
        if abs(delta) > ROUNDING_TOLERANCE:
            problems.append(f"cost does not reconcile: {name} parts={parts} approved={approved}")
        if abs(x["price"] - float(d["price"])) > 0.005:
            problems.append(f"price disagrees: {name} workbook={x['price']} card={d['price']}")

        entry = {
            "name": name,
            "canva_page": d["canva_page"],
            "category": d["category"],
            "family": d["family"],
            "doses": doses,
            "doses_total": parts,
            "approved_cost": approved,
            "doses_source": "GT_FOOD_COST_2026-08-27.xlsx · FOOD COST · פירוט עלות",
            "doses_date": "2026-08-27",
            "doses_authority": "system_verified",
            "serve": list(chips.get(name, [])),
            "serve_source": "docs/pricing/canva_workfiles/recipes.json (טקסט בלבד — המחירים בקובץ ההוא מוחלפים)",
            "serve_date": "2026-08-05",
            "serve_authority": "doc_confirmed",
        }
        if delta:
            entry["rounding_note"] = (
                f"סכום המנות ₪{parts} מול עלות מאושרת ₪{approved} — פער {delta:+.2f} "
                "מעיגול אגורה בגיליון. העלות המאושרת גוברת."
            )
        recipes.append(entry)

    if problems:
        print("HALT — recipes do not reconcile against the approved sources:", file=sys.stderr)
        for p in problems:
            print("  ·", p, file=sys.stderr)
        return None, problems

    commit = subprocess.run(
        ["git", "-C", BRAIN, "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()

    doc = {
        "card": {
            "id": "drinks/recipes",
            "title": "מתכוני 48 המשקאות — מנות ושיטת הכנה",
            "type": "recipes",
            "authority": "per-entry",
            "date": "2026-08-31",
            "freshness": "stable",
            "source": (
                "מנות: GT_FOOD_COST_2026-08-27.xlsx (מודל העלות המאושר, טום 2026-08-27) · "
                "שיטת הגשה: canva_workfiles/recipes.json 2026-08-05, טקסט בלבד"
            ),
            "generated_by": f"scripts/knowledge/build_recipes_card.py @ {commit}",
            # the entry's own grade is the DOSES grade — that is the entry's substance.
            # `serve` is an attachment and carries its own, lower, grade inline.
            "entry_keys": {
                "authority": "doses_authority",
                "date": "doses_date",
                "source": "doses_source",
            },
            "note": (
                "המנות הן מה שמודל העלות המאושר מתמחר — ולכן הן מתאימות בדיוק לעלות שבכרטיס. "
                "בסיס העלות ⊥ כולל גרניש, קרח, מים, סודה, אריזה ועבודה, ולכן שיטת ההגשה "
                "מופיעה בנפרד ובדרגה נמוכה יותר."
            ),
        },
        "recipes": recipes,
    }
    return doc, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = ap.parse_args()

    doc, problems = build()
    if problems:
        sys.exit(1)

    n = len(doc["recipes"])
    rounded = sum(1 for r in doc["recipes"] if "rounding_note" in r)
    print(f"{n}/48 drinks — every dose breakdown reconciles to the approved cost "
          f"({rounded} within the agora-rounding tolerance)")
    print(f"{sum(1 for r in doc['recipes'] if r['serve'])}/{n} carry a serve method")

    if args.check:
        return
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# נוצר אוטומטית ע\"י scripts/knowledge/build_recipes_card.py — ⊥ לערוך ביד.\n")
        f.write("# מנות: מודל העלות המאושר 2026-08-27. שיטת הגשה: קבצי הקנבה 2026-08-05.\n")
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100)
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(BRAIN))}")


if __name__ == "__main__":
    main()
