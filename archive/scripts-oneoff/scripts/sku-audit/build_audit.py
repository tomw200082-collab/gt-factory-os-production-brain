#!/usr/bin/env python3
"""SKU audit: cross-reference platform items, Shopify live, integration_sku_map, LionWheel.

Inputs (paste from earlier queries / dumps):
  - shopify-products-full.json (already saved by Playwright)
  - platform_items.json (will be written from a paste)
  - lionwheel_skus.json (will be written from a paste)
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
SHOPIFY = ROOT / 'shopify-products-full.json'
OUT = Path(__file__).resolve().parent / 'audit_report.json'
OUT_MD = Path(__file__).resolve().parent / 'audit_report.md'

PLATFORM_ITEMS_FILE = Path(__file__).resolve().parent / 'platform_items.json'
LIONWHEEL_FILE = Path(__file__).resolve().parent / 'lionwheel_skus.json'


def load_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def norm(s):
    return (s or '').strip()


def main():
    shopify = load_json(SHOPIFY)
    items = load_json(PLATFORM_ITEMS_FILE)
    lw = load_json(LIONWHEEL_FILE)

    # Index Shopify variants by sku and by barcode (only active or draft)
    # also include archived but flag separately
    sku_to_variant = {}        # sku -> [variants]
    barcode_to_variant = {}    # barcode -> [variants]
    all_active_variants = []

    for p in shopify['data']:
        for v in p['variants']:
            entry = {
                'product_id': p['product_id'],
                'product_title': p['title'],
                'product_status': p['status'],
                'variant_id': v['variant_id'],
                'variant_title': v['title'],
                'sku': norm(v['sku']),
                'barcode': norm(v['barcode']),
                'inventory_item_id': v['inventory_item_id'],
            }
            if entry['sku']:
                sku_to_variant.setdefault(entry['sku'], []).append(entry)
            if entry['barcode']:
                barcode_to_variant.setdefault(entry['barcode'], []).append(entry)
            if p['status'] in ('active', 'draft'):
                all_active_variants.append(entry)

    # Audit each platform item
    audit_rows = []
    matched_variant_ids = set()

    for it in items:
        item_id = it['item_id']
        item_name = it['item_name']
        item_status = it['status']
        plat_sku = norm(it['sku'])
        plat_legacy = norm(it['legacy_sku'])
        plat_barcode = norm(it['barcode'])
        mapped = norm(it['mapped_external_sku'])
        notes = it['mapping_notes']

        # candidates from each route
        by_mapped = sku_to_variant.get(mapped, []) if mapped else []
        by_plat_sku = sku_to_variant.get(plat_sku, []) if plat_sku else []
        by_legacy = sku_to_variant.get(plat_legacy, []) if plat_legacy else []
        by_barcode = barcode_to_variant.get(plat_barcode, []) if plat_barcode else []

        # Combine and dedup by variant_id
        seen = {}
        def add(lst, route):
            for v in lst:
                if v['variant_id'] in seen:
                    seen[v['variant_id']]['routes'].add(route)
                else:
                    e = dict(v); e['routes'] = {route}; seen[v['variant_id']] = e
        add(by_barcode, 'barcode')
        add(by_mapped, 'mapping_external_sku')
        add(by_plat_sku, 'platform_sku')
        add(by_legacy, 'legacy_sku')

        candidates = list(seen.values())

        # Verdict logic: pick primary by (active>draft>archived, mapping route, barcode route)
        verdict = []
        primary = None

        if not candidates:
            if item_status == 'ACTIVE':
                verdict.append('MISSING_SHOPIFY_MATCH')
            else:
                verdict.append('inactive_no_match')
        else:
            def rank(c):
                s = c['product_status']
                status_score = 3 if s == 'active' else (2 if s == 'draft' else 1)
                map_route = 'mapping_external_sku' in c['routes']
                bc_route = 'barcode' in c['routes']
                sku_match_mapping = mapped and c['sku'] == mapped
                return (status_score, sku_match_mapping, map_route, bc_route)
            candidates.sort(key=rank, reverse=True)
            primary = candidates[0]

            # Now decide verdict based on primary
            sku_ok = mapped and primary['sku'] == mapped
            barcode_ok = plat_barcode and primary['barcode'] and (
                plat_barcode == primary['barcode'] or
                plat_barcode.lstrip('0') == primary['barcode'].lstrip('0')
            )

            if not mapped:
                if item_status == 'ACTIVE':
                    verdict.append('NO_MAPPING_ROW_BUT_BARCODE_HIT')
                else:
                    verdict.append('inactive_no_mapping')
            elif primary['product_status'] == 'archived':
                verdict.append('MAPPING_TO_ARCHIVED_SHOPIFY')
            elif sku_ok and barcode_ok:
                verdict.append('VERIFIED_OK')
            elif sku_ok and not primary['barcode']:
                verdict.append('SKU_OK_NO_BARCODE_IN_SHOPIFY')
            elif sku_ok and not barcode_ok:
                verdict.append('SKU_OK_BARCODE_DIFFERS')
            elif not sku_ok and barcode_ok:
                verdict.append('BARCODE_OK_BUT_MAPPING_SKU_WRONG')
            else:
                verdict.append('SUSPICIOUS_NO_DIRECT_MATCH')

        if primary:
            matched_variant_ids.add(primary['variant_id'])

        audit_rows.append({
            'item_id': item_id,
            'item_name': item_name,
            'item_status': item_status,
            'platform_sku': plat_sku,
            'legacy_sku': plat_legacy,
            'platform_barcode': plat_barcode,
            'mapped_external_sku': mapped,
            'mapping_notes': notes,
            'shopify_match': {
                'variant_id': primary['variant_id'] if primary else None,
                'product_id': primary['product_id'] if primary else None,
                'product_title': primary['product_title'] if primary else None,
                'product_status': primary['product_status'] if primary else None,
                'sku': primary['sku'] if primary else None,
                'barcode': primary['barcode'] if primary else None,
                'inventory_item_id': primary['inventory_item_id'] if primary else None,
                'routes': sorted(primary['routes']) if primary else [],
            },
            'all_candidates': [
                {k: c[k] for k in ('variant_id', 'product_title', 'product_status', 'sku', 'barcode', 'inventory_item_id')}
                | {'routes': sorted(c['routes'])}
                for c in candidates
            ],
            'verdict': verdict,
        })

    # Unmapped Shopify variants (active or draft) that don't appear in any platform mapping
    unmapped_shopify = []
    for v in all_active_variants:
        if v['variant_id'] in matched_variant_ids:
            continue
        # also skip variants whose sku looks like obvious Shopify-only (e.g., gift sets, packs, internal codes)
        unmapped_shopify.append(v)

    # LionWheel: SKUs that appear in orders but have no resolution
    lw_unresolved = [r for r in lw if not r['has_resolution']]
    lw_resolved = [r for r in lw if r['has_resolution']]

    report = {
        'summary': {
            'platform_items_total': len(items),
            'platform_active': sum(1 for i in items if i['status'] == 'ACTIVE'),
            'platform_pending': sum(1 for i in items if i['status'] == 'PENDING'),
            'platform_inactive': sum(1 for i in items if i['status'] == 'INACTIVE'),
            'shopify_products_total': len(shopify['data']),
            'shopify_products_active': shopify['byStatus'].get('active', 0),
            'shopify_products_draft': shopify['byStatus'].get('draft', 0),
            'shopify_products_archived': shopify['byStatus'].get('archived', 0),
            'unmapped_shopify_active_or_draft': len(unmapped_shopify),
            'lionwheel_unresolved_skus': len(lw_unresolved),
            'lionwheel_resolved_skus': len(lw_resolved),
        },
        'platform_audit': audit_rows,
        'unmapped_shopify': unmapped_shopify,
        'lionwheel_unresolved': lw_unresolved,
    }

    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Wrote {OUT}')

    # Build human MD
    md = []
    s = report['summary']
    md.append(f"# SKU Audit — {len(items)} platform items vs {len(shopify['data'])} Shopify products vs {len(lw)} LionWheel SKUs\n")
    md.append(f"**Platform:** {s['platform_active']} ACTIVE / {s['platform_pending']} PENDING / {s['platform_inactive']} INACTIVE")
    md.append(f"**Shopify:** {s['shopify_products_active']} active / {s['shopify_products_draft']} draft / {s['shopify_products_archived']} archived")
    md.append(f"**LionWheel:** {s['lionwheel_resolved_skus']} resolved / {s['lionwheel_unresolved_skus']} unresolved\n")

    # Bucket by verdict
    by_verdict = defaultdict(list)
    for r in audit_rows:
        for v in r['verdict']:
            by_verdict[v].append(r)

    md.append("## Verdict counts\n")
    for v, lst in sorted(by_verdict.items(), key=lambda x: -len(x[1])):
        md.append(f"- {v}: **{len(lst)}**")
    md.append("")

    OUT_MD.write_text('\n'.join(md), encoding='utf-8')
    print(f'Wrote {OUT_MD}')

    # Print key flags inline so caller sees it
    print('\n=== SUMMARY ===')
    print(json.dumps(s, indent=2, ensure_ascii=False))
    print('\n=== VERDICT BUCKETS ===')
    for v, lst in sorted(by_verdict.items(), key=lambda x: -len(x[1])):
        print(f'  {v}: {len(lst)}')


if __name__ == '__main__':
    main()
