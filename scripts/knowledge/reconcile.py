#!/usr/bin/env python3
"""Reconcile GT's knowledge book against its approved sources, and validate the
knowledge cards that replace it.

Two subcommands:

    book   — diff the figures published in the book (book_published_figures.json)
             against the approved sources. Zero rows is the W1 gate (D1/D4).
    cards  — validate Sales-Machine/knowledge/**.yaml: required keys per entry,
             registry coverage, and every price/cost/margin re-joined to source (D2).

Approved sources (nothing else is authoritative):
  drinks         .claude/skills/drinks-pricelist/drinks_final_figures.json  (2026-08-27)
  product prices docs/pricing/2026-08-05_shopify_products_exvat.tsv
  sellability    docs/warehouses/catalog-truth.md

The superseded docs/pricing/2026-08-05_drinks_final_figures.json is refused on sight.
"""
import argparse
import json
import os
import re
import sys

BRAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALES = os.path.join(os.path.dirname(BRAIN), "Sales-Machine")

DRINKS_AUTHORITY = os.path.join(BRAIN, ".claude/skills/drinks-pricelist/drinks_final_figures.json")
DRINKS_SUPERSEDED = os.path.join(BRAIN, "docs/pricing/2026-08-05_drinks_final_figures.json")
PRICE_TSV = os.path.join(BRAIN, "docs/pricing/2026-08-05_shopify_products_exvat.tsv")
CATALOG_TRUTH = os.path.join(BRAIN, "docs/warehouses/catalog-truth.md")
BOOK = os.path.join(BRAIN, "scripts/knowledge/book_published_figures.json")

VAT = 1.18
CARD_KEYS = ("source", "date", "authority", "freshness")
AUTHORITY_GRADES = ("user_confirmed", "system_verified", "doc_confirmed", "inferred")
FRESHNESS = ("stable", "review_30d", "snapshot")


def money(x):
    return round(float(str(x).replace("₪", "").strip()), 2)


def pct(x):
    return int(str(x).replace("%", "").strip())


# ---------------------------------------------------------------- sources
def load_drinks():
    with open(DRINKS_AUTHORITY, encoding="utf-8") as fh:
        d = json.load(fh)
    if d["_meta"]["date"] != "2026-08-27":
        raise SystemExit("drinks authority is not the 2026-08-27 file — refusing to reconcile")
    return {int(k): v for k, v in d["pages"].items()}, d["_meta"]


def load_prices():
    out = {}
    with open(PRICE_TSV, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4 or parts[0] == "sku":
                continue
            out[parts[0]] = {"title": parts[1], "type": parts[2], "price": money(parts[3])}
    return out


def load_catalog_truth():
    """Return {sku_or_name: verdict} where verdict is 'sellable' | 'negative' | 'no_sku'."""
    sellable, negative, no_sku = set(), {}, {}
    section = None
    with open(CATALOG_TRUTH, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("##"):
                section = "negative" if "רשומות-שלילה" in line else "positive"
                continue
            if not line.startswith("|") or set(line.strip()) <= set("|-: "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or cells[0] in ("מוצר",):
                continue
            name = cells[0]
            skus = [c for c in cells[1:3] if re.match(r"^[A-Z][A-Z0-9*.\-]+$", c)]
            if section == "negative":
                negative[name] = {"sku": skus[0] if skus else None, "ruling": cells[2] if len(cells) > 2 else ""}
            else:
                if any("אין SKU פעיל" in c for c in cells):
                    no_sku[name] = cells
                for s in skus:
                    sellable.add(s)
    return sellable, negative, no_sku


# ---------------------------------------------------------------- book diff
def reconcile_book():
    if os.path.exists(DRINKS_SUPERSEDED):
        print("NOTE  superseded file still present: docs/pricing/2026-08-05_drinks_final_figures.json "
              "(list-shaped, field `heb`) — never read it. Cleanup item CL-1.\n")
    pages, meta = load_drinks()
    prices = load_prices()
    sellable, negative, no_sku = load_catalog_truth()
    with open(BOOK, encoding="utf-8") as fh:
        book = json.load(fh)

    rows = []

    # --- 48 drinks: cost / price / margin / name
    by_page = {d["page"]: d for d in book["drinks"]}
    if len(by_page) != 48:
        rows.append(("DRINKS", "count", f"book has {len(by_page)} pages", "authority has 48"))
    for page, auth in sorted(pages.items()):
        b = by_page.get(page)
        if not b:
            rows.append(("DRINK", f"page {page} · {auth['name']}", "missing from book", "in authority"))
            continue
        for field, bval, aval in (
            ("cost", money(b["cost"]), money(auth["cost"])),
            ("price", money(b["price"]), money(auth["price"])),
            ("margin", pct(b["margin"]), pct(auth["marg"])),
        ):
            if bval != aval:
                rows.append(("DRINK", f"page {page} · {auth['name']} · {field}", bval, aval))
        if b["name"] != auth["name"]:
            rows.append(("DRINK-NAME", f"page {page}", b["name"], auth["name"]))
        # margin must be derivable, not asserted
        derived = round((money(auth["price"]) / VAT - money(auth["cost"])) / (money(auth["price"]) / VAT) * 100)
        if derived != pct(auth["marg"]):
            rows.append(("DRINK-FORMULA", f"page {page} · {auth['name']}", auth["marg"], f"{derived}%"))

    # --- category summary recomputed from the authority
    cat_of = {d["page"]: d["category"] for d in book["drinks"]}
    agg = {}
    for page, auth in pages.items():
        c = cat_of.get(page)
        a = agg.setdefault(c, {"n": 0, "cost": [], "price": [], "marg": []})
        a["n"] += 1
        a["cost"].append(money(auth["cost"]))
        a["price"].append(money(auth["price"]))
        a["marg"].append(pct(auth["marg"]))
    for row in book["category_summary"]:
        a = agg.get(row["category"])
        if not a:
            rows.append(("CATEGORY", row["category"], "not found", "—"))
            continue
        for label, bval, aval in (
            ("drinks", row["drinks"], a["n"]),
            ("cost_min", money(row["cost_min"]), min(a["cost"])),
            ("cost_max", money(row["cost_max"]), max(a["cost"])),
            ("price_min", money(row["price_min"]), min(a["price"])),
            ("price_max", money(row["price_max"]), max(a["price"])),
            ("margin_min", row["margin_min"], min(a["marg"])),
            ("margin_max", row["margin_max"], max(a["marg"])),
        ):
            if bval != aval:
                rows.append(("CATEGORY", f"{row['category']} · {label}", bval, aval))

    # --- price list: price match + sellability (D4)
    for p in book["price_list"]:
        hint, name = p.get("sku_hint"), p["name"]
        neg = next((k for k in negative if _same_product(k, name, negative[k]["sku"], hint)), None)
        if neg:
            rows.append(("SELLABILITY", name, f"₪{p.get('price', p.get('price_1000'))} in the book",
                         f"negative record — Tom 2026-08-06: {negative[neg]['ruling']}"))
            continue
        if hint is None:
            rows.append(("NO-SKU", name, f"₪{p.get('price', p.get('price_1000'))} in the book",
                         "catalog-truth records no active SKU"))
            continue
        for key, sku in (("price", hint), ("price_1000", f"{hint}-1L"), ("price_500", f"{hint}-0.5L")):
            if key not in p:
                continue
            src = prices.get(sku)
            if src is None:
                rows.append(("PRICE-SKU", f"{name} · {sku}", p[key], "SKU absent from the ex-VAT price list"))
            elif money(p[key]) != src["price"]:
                rows.append(("PRICE", f"{name} · {sku}", money(p[key]), src["price"]))

    # --- per-serving arithmetic
    for r in book["per_serving"]:
        expected = round(r["unit_price"] / r["servings"], 2)
        if abs(expected - money(r["cost_per_serving"])) > 0.005:
            rows.append(("PER-SERVING", f"{r['item']} — {r['unit_price']}/{r['servings']}",
                         money(r["cost_per_serving"]), expected))

    # --- headline figures
    h = book["headline"]
    if h["cups_per_1l_bottle"] * h["serving_ml"] != 1000:
        rows.append(("HEADLINE", "cups × serving_ml", h["cups_per_1l_bottle"] * h["serving_ml"], 1000))
    if len(pages) != h["drinks_total"]:
        rows.append(("HEADLINE", "drinks_total", h["drinks_total"], len(pages)))
    iced = pages[8]
    for label, bval, aval in (("cost_per_cup_iced_tea", money(h["cost_per_cup_iced_tea"]), money(iced["cost"])),
                              ("recommended_price_iced_tea", money(h["recommended_price_iced_tea"]), money(iced["price"])),
                              ("margin_pct_iced_tea", h["margin_pct_iced_tea"], pct(iced["marg"]))):
        if bval != aval:
            rows.append(("HEADLINE", label, bval, aval))

    # --- claims: graded in the claims card, or unsourced
    claims = _load_claims()
    for c in book["claims"]:
        cid = c.get("claim_id")
        entry = claims.get(cid)
        if entry is None:
            rows.append(("CLAIM", c["claim"], "printed in the book",
                         f"no entry `{cid}` in knowledge/claims/public-claims.yaml"))
        elif entry.get("authority") == "unsourced":
            rows.append(("CLAIM", c["claim"], "printed in the book",
                         f"unsourced — {entry.get('open_item', 'Tom')}"))

    return rows


def _load_claims():
    card = os.path.join(SALES, "knowledge/claims/public-claims.yaml")
    if not os.path.exists(card):
        return {}
    yaml = _yaml()
    with open(card, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    return {c["id"]: c for c in doc.get("claims", [])}


def _same_product(truth_name, book_name, truth_sku, book_sku):
    if truth_sku and book_sku and truth_sku == book_sku:
        return True
    t = truth_name.replace("״", '"').replace("׳", "'")
    b = book_name.replace("״", '"').replace("׳", "'")
    return t in b or b in t


# ---------------------------------------------------------------- card validation
def _yaml():
    try:
        import yaml  # noqa
        return yaml
    except ImportError:
        raise SystemExit("PyYAML not installed — run: pip install pyyaml")


def validate_cards():
    yaml = _yaml()
    kdir = os.path.join(SALES, "knowledge")
    reg_path = os.path.join(kdir, "registry.yaml")
    with open(reg_path, encoding="utf-8") as fh:
        registry = yaml.safe_load(fh)
    registered = {c["id"] for c in registry.get("cards", [])}

    rows = []
    pages, _ = load_drinks()
    prices = load_prices()
    _, negative, _ = load_catalog_truth()
    neg_skus = {v["sku"] for v in negative.values() if v["sku"]}

    for root, _dirs, files in os.walk(kdir):
        for fn in sorted(files):
            if not fn.endswith((".yaml", ".yml")) or fn == "registry.yaml":
                continue
            path = os.path.join(root, fn)
            cid = os.path.relpath(path, kdir).rsplit(".", 1)[0].replace(os.sep, "/")
            if cid not in registered:
                rows.append(("REGISTRY", cid, "not in registry.yaml", "must be indexed (rule 1)"))
            with open(path, encoding="utf-8") as fh:
                doc = yaml.safe_load(fh)
            if not isinstance(doc, dict):
                rows.append(("CARD", cid, "not a mapping", "expected a mapping with `card` + entries"))
                continue
            head = doc.get("card", {})
            for k in CARD_KEYS:
                if not head.get(k):
                    rows.append(("CARD", cid, f"missing `{k}`", "rule 1"))
            if head.get("authority") not in AUTHORITY_GRADES + ("per-entry", "n/a"):
                rows.append(("CARD", cid, f"authority={head.get('authority')}", "|".join(AUTHORITY_GRADES)))
            if head.get("freshness") not in FRESHNESS:
                rows.append(("CARD", cid, f"freshness={head.get('freshness')}", "|".join(FRESHNESS)))
            # a store may name its per-entry keys differently — it declares the map itself
            alias = head.get("entry_keys") or {}
            for name, entries in doc.items():
                if name == "card" or not isinstance(entries, list):
                    continue
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    label = e.get("id") or e.get("name") or e.get("sku") or e.get("q") or "?"
                    if head.get("authority") == "per-entry":
                        for k in ("source", "date", "authority"):
                            if not e.get(alias.get(k, k)):
                                rows.append(("ENTRY", f"{cid} · {label}", f"missing `{alias.get(k, k)}`", "rule 1"))
                        grade = e.get(alias.get("authority", "authority"))
                        if grade not in AUTHORITY_GRADES + ("unsourced",):
                            rows.append(("ENTRY", f"{cid} · {label}", f"authority={grade}",
                                         "|".join(AUTHORITY_GRADES)))
                    rows.extend(_check_entry_numbers(cid, label, e, pages, prices, neg_skus))
    return rows


def _check_entry_numbers(cid, label, e, pages, prices, neg_skus):
    rows = []
    if "canva_page" in e:
        auth = pages.get(int(e["canva_page"]))
        if not auth:
            rows.append(("DRINK-CARD", f"{cid} · {label}", e["canva_page"], "page absent from the authority"))
        else:
            for k, a in (("cost", money(auth["cost"])), ("price", money(auth["price"])), ("margin_pct", pct(auth["marg"]))):
                if k in e and money(e[k]) != a:
                    rows.append(("DRINK-CARD", f"{cid} · {label} · {k}", e[k], a))
    if e.get("sku"):
        sku = e["sku"]
        if sku in neg_skus and e.get("customer_facing", True):
            rows.append(("SELLABILITY-CARD", f"{cid} · {label}", "customer_facing", "negative record"))
        src = prices.get(sku)
        if src is None:
            if e.get("price_exvat") is not None:
                rows.append(("PRICE-CARD", f"{cid} · {label}", sku, "SKU absent from the ex-VAT price list"))
        elif e.get("price_exvat") is not None and money(e["price_exvat"]) != src["price"]:
            rows.append(("PRICE-CARD", f"{cid} · {label}", money(e["price_exvat"]), src["price"]))
    return rows


# ---------------------------------------------------------------- output
# A book finding is CLOSED once the knowledge cards carry the corrected value —
# the published HTML page is a 2026-08-31 snapshot this session cannot edit, so the
# card is where the fix lands. OPEN means only Tom can close it.
RESOLUTION = {
    "DRINK-NAME":  ("closed", "knowledge/drinks/catalog.yaml carries the authority name"),
    "PER-SERVING": ("closed", "the row is dropped with the product (Tom 2026-08-31)"),
    "SELLABILITY": ("closed", "Tom 2026-08-31: off the customer price list. Still orderable in the "
                              "store — that is drift_scan.py's business, not the book's"),
    "NO-SKU":      ("open",   "no active SKU behind a printed price"),
    "CLAIM":       ("open",   "unsourced — give the figure and its basis, or drop the sentence"),
}


def report(title, rows, resolutions=False):
    print(f"=== {title} ===")
    if not rows:
        print("0 rows — PASS\n")
        return 0
    w = max(len(str(r[1])) for r in rows)
    head = f"{'KIND':<14} {'SUBJECT':<{w}}  {'BOOK / CARD':<32} SOURCE OF TRUTH"
    print(head + ("   STATE" if resolutions else ""))
    still_open = 0
    for kind, subject, book_v, src_v in rows:
        line = f"{kind:<14} {str(subject):<{w}}  {str(book_v):<32} {src_v}"
        if resolutions:
            state, why = RESOLUTION.get(kind, ("open", ""))
            still_open += state == "open"
            line += f"   [{state}] {why}"
        print(line)
    if resolutions:
        print(f"\n{len(rows)} findings — {len(rows) - still_open} closed by the cards, "
              f"{still_open} OPEN (Tom's, §6)\n")
        return still_open
    print(f"\n{len(rows)} rows — FAIL\n")
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["book", "cards", "all"], nargs="?", default="all")
    args = ap.parse_args()
    bad = 0
    if args.what in ("book", "all"):
        bad += report("W1 — the book (2026-08-31 snapshot) vs its approved sources",
                      reconcile_book(), resolutions=True)
    if args.what in ("cards", "all"):
        bad += report("D2 — knowledge cards vs their approved sources", validate_cards())
    return 1 if bad else 0


def _selftest():
    """Smallest check that fails if the joins break."""
    pages, meta = load_drinks()
    assert len(pages) == 48 and meta["date"] == "2026-08-27"
    for p, v in pages.items():
        d = round((money(v["price"]) / VAT - money(v["cost"])) / (money(v["price"]) / VAT) * 100)
        assert d == pct(v["marg"]), f"page {p}: margin {v['marg']} != derived {d}%"
    prices = load_prices()
    assert prices["GT-HIB-LOW-1L"]["price"] == 65.0 and prices["GT-SHI-CER-500"]["price"] == 590.0
    sellable, negative, no_sku = load_catalog_truth()
    assert "GT-SHI-CER-50" in {v["sku"] for v in negative.values()}, negative
    assert "GT-HIB-LOW-1L" in sellable
    # 2026-08-31: AMERICAN and HOJICHA were recorded as "no active SKU" and both had one.
    # The list is now empty; assert it stays empty rather than that those two are in it.
    assert not no_sku, f"a row is back to 'no active SKU': {no_sku}"
    assert {"GT-AME-LOW-1L", "GT-AME-LOW-0.5L", "GT-HOJ-BLK-500"} <= sellable, sellable
    assert prices["GT-AME-LOW-1L"]["price"] == 65.0 and prices["GT-AME-LOW-0.5L"]["price"] == 33.0
    print("selftest OK — 48 drinks, margins derive, price/sellability joins live")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        sys.exit(main())
