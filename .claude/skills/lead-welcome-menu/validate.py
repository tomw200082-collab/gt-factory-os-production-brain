#!/usr/bin/env python3
"""
D3 — prove every drink figure on the page is the approved figure.

Compares all four fields of all twelve drinks against drinks_final_figures.json
AND independently re-derives profit and margin from cost and price under the
VAT rule, so a figure that is merely self-consistent with a wrong source still
fails. Then confirms each figure actually appears in the built page.

    python3 validate.py          -> "deviations 0" when clean
"""
import json, re, sys
from pathlib import Path

D = Path(__file__).parent
FIGURES = D.parent / "drinks-pricelist" / "drinks_final_figures.json"
PAGE = D / "lead-menu.html"
KEYS = ["8", "23", "27", "12", "21", "48", "49", "55", "29", "34", "31", "33"]
VAT = 1.18


def text_of(html):
    body = html.split("</style>", 1)[1]
    return re.sub(r"<[^>]+>", " ", body)


def main():
    figs = json.load(FIGURES.open())["pages"]
    page = text_of(PAGE.read_text(encoding="utf-8"))
    dev = []

    for k in KEYS:
        if k not in figs:
            dev.append(f"key {k}: absent from {FIGURES.name}")
            continue
        v = figs[k]
        cost_s, price_s = v["cost"].rstrip("*"), v["price"]
        marg_s, prof_s = v["marg"], v["prof"].replace(" לכוס", "")

        # independent re-derivation — never trust the file's own arithmetic
        c, p = float(cost_s.lstrip("₪")), float(price_s.lstrip("₪"))
        ex = p / VAT
        prof_calc, marg_calc = round(ex - c, 2), round((ex - c) / ex * 100)
        if f"₪{prof_calc:.2f}" != prof_s:
            dev.append(f"key {k}: profit {prof_s} but price/{VAT}-cost = ₪{prof_calc:.2f}")
        if f"{marg_calc}%" != marg_s:
            dev.append(f"key {k}: margin {marg_s} but profit/ex-VAT revenue = {marg_calc}%")

        # every field must actually reach the page
        for label, val in (("cost", cost_s), ("price", price_s),
                           ("margin", marg_s), ("profit", prof_s)):
            if val not in page:
                dev.append(f"key {k}: {label} {val} does not appear in {PAGE.name}")

    # ---- the closed check ----------------------------------------------------
    # Presence alone is not enough: ₪17.09 appears on both the FRESH product screen
    # and its hero, so corrupting one occurrence still leaves the value "present".
    # Every money and percentage token on the page must therefore also BE an
    # approved one. Anything figure-shaped and unrecognised is a deviation.
    approved_money, approved_pct = set(), set()
    for k in KEYS:
        v = figs[k]
        approved_money |= {v["cost"].rstrip("*"), v["price"],
                           v["prof"].replace(" לכוס", "")}
        approved_pct.add(v["marg"])
    # non-drink figures that legitimately appear, each with its source
    approved_pct |= {"50%"}          # מחית תות: 50% פרי — products catalog DAHQrpThEBE
    for tok in set(re.findall(r"₪\s?\d+(?:\.\d+)?", page)):
        if tok.replace(" ", "") not in approved_money:
            dev.append(f"unapproved money token on the page: {tok!r}")
    for tok in set(re.findall(r"\d+%", page)):
        if tok not in approved_pct:
            dev.append(f"unapproved percentage token on the page: {tok!r}")

    # the two derived spans quoted on S02 must match the twelve rows
    profs = [float(figs[k]["prof"].replace(" לכוס", "").lstrip("₪")) for k in KEYS]
    margs = [int(figs[k]["marg"].rstrip("%")) for k in KEYS]
    for span, lo, hi in ((("profit"), f"₪{min(profs):.2f}", f"₪{max(profs):.2f}"),
                         (("margin"), f"{min(margs)}%", f"{max(margs)}%")):
        if lo not in page or hi not in page:
            dev.append(f"derived {span} span {lo}–{hi} does not appear in {PAGE.name}")

    for d in dev:
        print("  DEVIATION:", d)
    print(f"drinks checked {len(KEYS)} · fields checked {len(KEYS) * 4}")
    money_toks = set(re.findall(r"₪\s?\d+(?:\.\d+)?", page))
    pct_toks = set(re.findall(r"\d+%", page))
    print(f"figure-shaped tokens on the page: {len(money_toks)} money, "
          f"{len(pct_toks)} percentage — every one matched against the approved set")
    print(f"deviations {len(dev)}")
    return 1 if dev else 0


if __name__ == "__main__":
    sys.exit(main())
