#!/usr/bin/env python3
"""Show every unmatched SKU with: Excel row, Hebrew product name, qty,
notes, and a proposed match candidate from the items master if there is
a plausible one (fuzzy on flavor codes)."""
import json, re, sys
from pathlib import Path

ROOT = Path(r"c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION")
report = json.load(open(ROOT / "scripts" / "_analyze_may_forecast_v2.json", encoding="utf-8"))

# Load items master from the V2 report's row data (we have it embedded as resolved.item_id keys)
# Actually let's just fetch live from DB for the master list
import psycopg
ENV = Path(r"c:/Users/tomw2/Projects/gt-factory-os/.env").read_text(encoding="utf-8")
DB_URL = next(l[len("DATABASE_URL_POOLED="):].strip()
              for l in ENV.splitlines() if l.startswith("DATABASE_URL_POOLED="))
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

conn = psycopg.connect(DB_URL, sslmode="require")
cur = conn.cursor()
cur.execute("SELECT item_id, item_name, supply_method, status FROM private_core.items ORDER BY item_id")
items = [{"item_id": r[0], "item_name": r[1], "supply_method": r[2], "status": r[3]} for r in cur.fetchall()]
items_by_id = {it["item_id"]: it for it in items}

print("=" * 120)
print("UNMATCHED SKUs — full per-row breakdown")
print("=" * 120)

groups = {
    "MUZA-1L":       [],   # GTCC-MUZ-*-1L
    "SANGRIA-0.15L": [],
    "SANGRIA-OTHER": [],
    "ARAK":          [],
    "BABKA":         [],
    "TROPICAL":      [],
    "ODK":           [],
    "OTHER":         [],
}

for row in report["rows"]:
    unmatched = [r for r in row["resolved"] if not r["item_id"]]
    if not unmatched:
        continue
    for r in unmatched:
        sku = r["sku_excel"]
        rec = {
            "excel_row": row["excel_row"],
            "name":     row["name"],
            "flavor":   row["flavor"],
            "qty_total": row["qty_total"],
            "weekly":   row["weekly"],
            "notes":    row["notes"],
            "sku":      sku,
            "all_skus_in_row": row["skus_raw"],
        }
        if sku.startswith("GTCC-MUZ-") and sku.endswith("-1L"):
            groups["MUZA-1L"].append(rec)
        elif sku.startswith("GTCC-") and "-SAN-" in sku and "0.15" in sku:
            groups["SANGRIA-0.15L"].append(rec)
        elif sku.startswith("GTCC-NM-SAN-") or "SAN-" in sku:
            groups["SANGRIA-OTHER"].append(rec)
        elif "ARA" in sku:
            groups["ARAK"].append(rec)
        elif "BAB" in sku:
            groups["BABKA"].append(rec)
        elif "TRO" in sku:
            groups["TROPICAL"].append(rec)
        elif sku.startswith("GT-ODK"):
            groups["ODK"].append(rec)
        else:
            groups["OTHER"].append(rec)

# Helper: search items master for plausible candidates
def candidates_for(sku, name):
    out = []
    sku_u = sku.upper()
    name_u = (name or "").upper()
    # Look for any item whose name contains substring or item_id has matching tokens
    for it in items:
        nm = (it["item_name"] or "").upper()
        iid = it["item_id"].upper()
        # Strong: same flavor token in id
        # MUZA cocktails — the 200ML variants might be alternatives
        if "MUZ" in sku_u and ("MUZ" in iid or "MUZ" in nm):
            out.append(it)
        elif "SAN" in sku_u and "RED" in sku_u and ("SAN" in iid and "RED" in iid):
            out.append(it)
        elif "SAN" in sku_u and "WHI" in sku_u and ("SAN" in iid and "WHI" in iid):
            out.append(it)
        elif "SAN" in sku_u and "PIN" in sku_u and ("SAN" in iid and "PIN" in iid):
            out.append(it)
        elif "ARA" in sku_u and "ARA" in iid:
            out.append(it)
        elif "ODK" in sku_u and "ODK" in iid:
            out.append(it)
    return out[:8]

for group_name, recs in groups.items():
    if not recs: continue
    print(f"\n--- GROUP: {group_name} ({len(recs)} SKUs, total qty = {sum(r['qty_total'] for r in recs)}) ---")
    for rec in recs:
        print(f"\n  Row {rec['excel_row']:2d}  SKU: {rec['sku']}")
        print(f"    Name (HE): {rec['name']}  | flavor: {rec['flavor']}")
        print(f"    Qty total: {rec['qty_total']}   Weekly: {rec['weekly']}")
        print(f"    Notes: {rec['notes']}")
        print(f"    All SKUs in this row: {rec['all_skus_in_row']}")
        cands = candidates_for(rec["sku"], rec["name"])
        if cands:
            print(f"    Possible matches in items master:")
            for c in cands:
                print(f"      {c['item_id']:30s}  {c['item_name']}   ({c['supply_method']}, {c['status']})")
        else:
            print(f"    No plausible candidate in items master")

cur.close(); conn.close()
