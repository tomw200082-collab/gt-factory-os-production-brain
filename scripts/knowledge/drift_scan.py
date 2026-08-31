#!/usr/bin/env python3
"""Check the curated catalog against live Shopify. Scoped, on purpose.

docs/warehouses/catalog-truth.md is the curated list of what GT actually sells.
It is deliberately NOT a mirror of the Shopify store — the store also carries
cocktails, mixers, packaging, garnish and retired lines that have no business in
a customer catalog. So this script asks only the three questions that can make
the catalog wrong, and stays silent about everything else:

  1. PRICE      a catalogued SKU's live price != the approved price list
  2. GONE       a catalogued SKU is no longer ACTIVE in Shopify
  3. SELLABLE   a negative record (Tom: "we don't sell this") is still orderable

An earlier version of this script diffed the whole store both ways. It returned
31 rows of which 4 mattered, and buried the real findings. A scan that can't tell
signal from noise is not a scan.

    python3 scripts/knowledge/drift_scan.py [snapshot.json]
"""
import json
import os
import re
import sys

BRAIN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TSV = os.path.join(BRAIN, "docs/pricing/2026-08-05_shopify_products_exvat.tsv")
TRUTH = os.path.join(BRAIN, "docs/warehouses/catalog-truth.md")
DEFAULT_SNAP = os.path.join(BRAIN, "data/shopify/2026-08-31_active_snapshot.json")


def load_snapshot(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return {sku: {"price": float(p), "title": t} for sku, p, t in d["variants"]}, d["_meta"]


def load_tsv():
    out = {}
    with open(TSV, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            c = line.rstrip("\n").split("\t")
            if len(c) >= 4 and c[0] != "sku":
                out[c[0]] = {"title": c[1], "price": float(c[3])}
    return out


def load_truth():
    """The curated catalog: {sku: (kind, product name)}, kind = sellable | negative."""
    skus, section = {}, None
    with open(TRUTH, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("##"):
                section = "negative" if "רשומות-שלילה" in line else "positive"
                continue
            if not line.startswith("|") or set(line.strip()) <= set("|-: "):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or cells[0] == "מוצר":
                continue
            for s in [c for c in cells[1:3] if re.match(r"^[A-Z][A-Z0-9*.\-]+$", c)]:
                skus[s] = ("negative" if section == "negative" else "sellable", cells[0])
    return skus


def main():
    live, meta = load_snapshot(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SNAP)
    tsv, truth = load_tsv(), load_truth()
    catalogued = sum(1 for k in truth.values() if k[0] == "sellable")

    print(f"live snapshot {meta['date']} — {len(live)} ACTIVE variants in the store")
    print(f"curated catalog — {catalogued} sellable SKUs, "
          f"{len(truth) - catalogued} negative records\n")
    print("Out of scope by design: every Shopify product that is not in catalog-truth.md.\n")

    rows = []
    for sku, (kind, name) in sorted(truth.items()):
        if kind == "sellable":
            if sku not in live:
                rows.append(("GONE", sku, name, "in the catalog, not ACTIVE in Shopify"))
                continue
            listed = tsv.get(sku)
            if listed is None:
                rows.append(("NO-PRICE", sku, name,
                             f"live at ₪{live[sku]['price']:g}, absent from the approved price list"))
            elif abs(live[sku]["price"] - listed["price"]) > 0.005:
                rows.append(("PRICE", sku, name,
                             f"live ₪{live[sku]['price']:g} vs price list ₪{listed['price']:g}"))
        elif sku in live:
            rows.append(("SELLABLE", sku, name,
                         f"negative record, still orderable at ₪{live[sku]['price']:g}"))

    if not rows:
        print("0 rows — catalog and store agree")
        return 0
    w1 = max(len(r[1]) for r in rows)
    w2 = max(len(r[2]) for r in rows)
    print(f"{'KIND':<10} {'SKU':<{w1}}  {'PRODUCT':<{w2}}  FINDING")
    for k, s, n, f in rows:
        print(f"{k:<10} {s:<{w1}}  {n:<{w2}}  {f}")
    print(f"\n{len(rows)} rows")
    return len(rows)


def _selftest():
    live, _ = load_snapshot(DEFAULT_SNAP)
    truth, tsv = load_truth(), load_tsv()
    assert truth["GT-AME-LOW-1L"] == ("sellable", "AMERICAN"), truth.get("GT-AME-LOW-1L")
    assert truth["GT-SHI-CER-50"][0] == "negative"
    assert live["GT-AME-LOW-1L"]["price"] == 65.0 and tsv["GT-AME-LOW-1L"]["price"] == 65.0
    assert "GTCC-MUZ-ANBL-1L" not in truth, "a cocktail SKU leaked into the curated catalog"
    print("selftest OK — catalog scoped, cocktails excluded, AMERICAN price agrees")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        sys.exit(0 if main() == 0 else 1)
