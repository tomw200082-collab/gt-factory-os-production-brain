#!/usr/bin/env python3
# Stage B — strict validation of the 48 drink pages in Canva design DAHPi9gpfts
# Compares the SAVED on-page values (observed.json) against the approved figures
# (drinks_final_figures.json), plus an independent VAT arithmetic re-derivation.

import json, re, sys
from pathlib import Path

D = Path(__file__).parent
ref = json.loads((D / "drinks_final_figures.json").read_text(encoding="utf-8"))
obs = json.loads((D / "observed.json").read_text(encoding="utf-8"))

FC_LABEL = "FOOD COST · ללא מע״מ"
PRICE_LABEL = "מחיר מומלץ · כולל מע״מ"
NO_STAR_PAGES = {8, 16, 17, 18}          # pages that did NOT carry an asterisk pre-edit
LEGAL_PRICES = {"₪19", "₪22", "₪24", "₪26", "₪28"}
VAT = 1.18

R, O = ref["pages"], obs["pages"]
fails = []
def check(cond, msg):
    if not cond:
        fails.append(msg)

# ---- 1. page count -------------------------------------------------------
check(len(O) == 48, f"page count: {len(O)} != 48")
check(set(R) == set(O), f"page-set mismatch: ref-only={sorted(set(R)-set(O))} obs-only={sorted(set(O)-set(R))}")

stars = 0
for k in sorted(O, key=int):
    p, o, r = int(k), O[k], R[k]

    # ---- 2. cost string exact (star-insensitive) ------------------------
    check(o["cost"].rstrip("*") == r["cost"].rstrip("*"),
          f"p{p} cost: on-page {o['cost']!r} != approved {r['cost']!r}")

    # ---- 3. asterisk preserved exactly where it belongs -----------------
    has = o["cost"].endswith("*")
    stars += has
    check(has == (p not in NO_STAR_PAGES),
          f"p{p} asterisk: on-page star={has}, expected star={p not in NO_STAR_PAGES}")

    # ---- 4/5. labels ----------------------------------------------------
    check(obs["fc_label_all"] == FC_LABEL, "FOOD COST label mismatch")
    check(obs["price_label_all"] == PRICE_LABEL, "price label mismatch")

    # ---- 6. margin, 7. profit ------------------------------------------
    check(o["marg"] == r["marg"], f"p{p} margin: on-page {o['marg']!r} != approved {r['marg']!r}")
    check(o["prof"] == r["prof"], f"p{p} profit: on-page {o['prof']!r} != approved {r['prof']!r}")

    # ---- 8. sale price unchanged ---------------------------------------
    check(o["price"] == r["price"], f"p{p} price: on-page {o['price']!r} != approved {r['price']!r}")
    check(o["price"] in LEGAL_PRICES, f"p{p} price {o['price']!r} not in the allowed set")

    # ---- 9. independent VAT arithmetic (catches transcription slips) ----
    cost = float(o["cost"].rstrip("*").lstrip("₪"))
    price = float(o["price"].lstrip("₪"))
    net = price / VAT
    exp_prof = round(net - cost, 2)
    exp_marg = round((net - cost) / net * 100)
    got_prof = float(re.match(r"₪([\d.]+)", o["prof"]).group(1))
    got_marg = int(o["marg"].rstrip("%"))
    check(abs(exp_prof - got_prof) < 0.005,
          f"p{p} profit arithmetic: {price}/1.18-{cost} = {exp_prof:.2f}, page says {got_prof:.2f}")
    check(exp_marg == got_marg,
          f"p{p} margin arithmetic: computed {exp_marg}%, page says {got_marg}%")

check(stars == 44, f"asterisk count: {stars} != 44")

print(f"pages validated      : {len(O)}")
print(f"asterisks on page    : {stars} (expected 44)")
print(f"FOOD COST label 48/48: {obs['fc_label_all'] == FC_LABEL}")
print(f"price label 48/48    : {obs['price_label_all'] == PRICE_LABEL}")
print(f"checks run           : {len(O) * 10 + 2}")
print(f"deviations           : {len(fails)}")
for f in fails:
    print("  FAIL:", f)
sys.exit(1 if fails else 0)
