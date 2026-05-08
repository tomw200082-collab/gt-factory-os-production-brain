"""
One-off: create 3 matcha-accessory drafts in the GreenTeaEveryday Shopify store.

Reads SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_API_TOKEN from env (loaded by caller).
Idempotency: each product is checked by SKU first; if a variant with that SKU already
exists, that product is skipped (no duplicate creation).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error

SHOP = os.environ["SHOPIFY_STORE_DOMAIN"]
TOKEN = os.environ["SHOPIFY_ADMIN_API_TOKEN"]
API = f"https://{SHOP}/admin/api/2024-01"

DRAFTS = [
    {
        "title": "מעמד קרמיקה למקציף מאצ'ה",
        "sku": "AP-STA-MAT",
        "barcode": "8901",
        "price": "25.00",
    },
    {
        "title": "כפית במבוק למאצ'ה",
        "sku": "AP-SCO-MAT",
        "barcode": "8902",
        "price": "11.00",
    },
    {
        "title": "בוחש מקציף במבוק למאצ'ה",
        "sku": "AP-WHK-MAT",
        "barcode": "8903",
        "price": "37.00",
    },
]


def req(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "X-Shopify-Access-Token": TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} {method} {path}: {body_text}") from e


def sku_taken(sku: str) -> tuple[bool, dict | None]:
    q = {
        "query": (
            "query($q:String!){ productVariants(first:1, query:$q){ edges{ node{ "
            "id sku product{ id title status }}}}}"
        ),
        "variables": {"q": f"sku:{sku}"},
    }
    res = req("POST", "/graphql.json", q)
    edges = ((res.get("data") or {}).get("productVariants") or {}).get("edges", [])
    if not edges:
        return False, None
    return True, edges[0]["node"]


def barcode_taken(bc: str) -> bool:
    q = {
        "query": "query($q:String!){ productVariants(first:1, query:$q){ edges{ node{ id sku barcode }}}}",
        "variables": {"q": f"barcode:{bc}"},
    }
    res = req("POST", "/graphql.json", q)
    edges = ((res.get("data") or {}).get("productVariants") or {}).get("edges", [])
    return bool(edges)


def create_draft(d: dict) -> dict:
    body = {
        "product": {
            "title": d["title"],
            "vendor": "GreenTeaEveryday",
            "product_type": "Accessories",
            "status": "draft",
            "tags": "Matcha, Accessories",
            "variants": [
                {
                    "price": d["price"],
                    "sku": d["sku"],
                    "barcode": d["barcode"],
                    "taxable": True,
                    "requires_shipping": True,
                    "inventory_management": "shopify",
                    "inventory_policy": "deny",
                }
            ],
        }
    }
    return req("POST", "/products.json", body)


def main() -> int:
    results = []
    for d in DRAFTS:
        taken, existing = sku_taken(d["sku"])
        if taken:
            results.append({"sku": d["sku"], "skipped": True, "existing": existing})
            print(f"SKIP {d['sku']}: already exists -> {existing}")
            continue
        if barcode_taken(d["barcode"]):
            results.append({"sku": d["sku"], "skipped": True, "reason": "barcode-collision"})
            print(f"SKIP {d['sku']}: barcode {d['barcode']} already taken")
            continue
        resp = create_draft(d)
        prod = resp.get("product", {})
        v = (prod.get("variants") or [{}])[0]
        admin_url = f"https://{SHOP.replace('.myshopify.com','')}.myshopify.com/admin/products/{prod.get('id')}"
        results.append(
            {
                "sku": d["sku"],
                "product_id": prod.get("id"),
                "variant_id": v.get("id"),
                "handle": prod.get("handle"),
                "status": prod.get("status"),
                "barcode": v.get("barcode"),
                "price": v.get("price"),
                "admin_url": admin_url,
            }
        )
        print(f"CREATED {d['sku']} -> product_id={prod.get('id')} status={prod.get('status')}")
    print()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
