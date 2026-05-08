# Exceptions Inbox Cleanup — Design Spec

**Date authored:** 2026-04-27
**Author:** Claude (Opus 4.7) under Tom's direction
**Skill chain:** factory-os-advance → adversarial-system-audit lens → brainstorming
**Status:** DRY-RUN — execution gated on Tom approval after reviewing dry-run output
**Target environment:** Supabase project `rvadsozabmxkkrktwgnv` (eu-central-1, production)

---

## 0. Purpose

Clean the live Exceptions Inbox in `private_core.exceptions` from accumulated noise and historical fixtures, before opening real production traffic. **Stock truth must remain untouched.** Operator-actionable rows must remain visible. Live producers must keep firing on real future data.

This spec was authored after Tom locked decisions D1–D6 (see §8). Execution is gated on dry-run review.

## 0.1 Catalog-safe cleanup rule (Tom 2026-04-27)

**Rule:** any exception referencing a real-looking commercial SKU must never be resolved solely because `item_id` is missing or because the cleanup wants to silence noise. Missing `item_id` means **catalog reconstruction review**, not cleanup.

**Permitted mechanical disposition (DELETE / RESOLVE without evidence):** TEST/dev/timestamp fixtures only — i.e., rows whose dedupe_key, title, or detail makes their non-commercial origin self-evident (e.g., `TEST-SKU-RESOLVER-*`, `TEST-LW-PROBE-*`, `ammc-slice2-*`, `T1REG-*`, `T2DET-*`, `T3BLK-*`, empty SKU, EAN barcode shipped where SKU was expected).

**Required evidence-backed disposition for commercial SKUs (7-condition predicate, Tom-locked 2026-04-27):** before any resolve, the cleanup must produce per-row evidence that ALL seven conditions hold simultaneously:

1. **Canonical item exists** — a row in `private_core.items` whose `item_id` is the proposed canonical mapping target.
2. **Item is active** — `private_core.items.status = 'ACTIVE'`.
3. **Shopify-facing SKU present** — the external SKU appears in `private_core.items.sku` and/or `private_core.items.legacy_sku` for that item.
4. **Barcode matches where available** — if `items.barcode` is populated AND the channel exposes a barcode for the same record, the values must match. (Shopify-side barcode cross-check requires Shopify Admin API and is **out of scope for this cleanup pass per Tom 2026-04-27**; canonical-side `items.barcode` populated is a positive proof; both null is vacuously satisfied.) **v1 implementation in §2.3.1 requires `items.barcode IS NOT NULL` as positive proof — the "both null vacuously satisfied" allowance is reserved for a future relaxation if a no-barcode commercial item ever needs evidence-resolve. Until then, no-canonical-barcode means FAIL.**
5. **Approved alias mapping** — `private_core.integration_sku_map` row exists with `external_sku = <Shopify SKU>`, `source_channel = 'shopify'`, `approval_status = 'approved'`, `item_id = <canonical item_id>`.
6. **Latest Shopify sync succeeded** — `private_core.shopify_fg_sync_history` shows the most recent row for that `(item_id, variant_sku)` pair has `write_status = 'ok'`. **Wording correction (Tom 2026-04-27):** POST 200 OK on `inventory_levels.set` (or equivalent) **does not** prove the product is active or sellable in Shopify; it proves only that the Shopify inventory sync target exists and accepts stock-sync writes for that variant. Commercial sellability is not within this pass; if needed later, validate via Shopify Admin API or a richer Shopify product-state mirror.
7. **No newer exception for the same SKU** — no exception with `dedupe_key` referencing the same Shopify SKU was emitted after the timestamp recorded by the last successful Shopify sync (i.e., the sync evidence has not been invalidated by a regression event).

Only with all seven conditions PASS may the original exception be resolved. The resolution_notes template is fixed:

```
Canonical item exists under <FG item_id>; Shopify-facing SKU <GT...> maps via
approved alias (integration_sku_map.alias_id=<uuid>, approved_at=<ts>);
items.legacy_sku/sku and barcode verified canonical-side (items.barcode=<barcode>);
latest Shopify stock sync write_status='ok' at <cycle_at_ts>; no newer exception
emitted for the same SKU after that sync; exception was stale/orphaned from
pre-alias state.
```

If any of the seven conditions fails, the row stays HOLD and goes to `HOLD_catalog_reconstruction_required` (§2.3.2) — never to a mechanical resolve.

This rule is permanent and applies to all future cleanup tranches.

---

## 1. Exact reconciled counts (live read 2026-04-27)

> **Drift note:** at first read in this session the open count was 414. By the time the deterministic bucket query ran it was **421**. Δ = +7, all in `lionwheel_capped_window_gap` (121 → 128). The category continues to emit at ~1/15min. This validates D5 (suppress required) and proves we must capture a **frozen baseline** before any UPDATE/DELETE.

### 1.1 Status snapshot (full table, all statuses)

| status | n |
|---|---:|
| open | 421 |
| resolved | 77 |
| acknowledged | 4 |
| auto_resolved | 2 |
| **total rows in `private_core.exceptions`** | **504** |

### 1.2 Open rows by deterministic bucket (no overlap, sums to 421)

| bucket | n | action class |
|---|---:|---|
| `ACK_lw_capped_info_only` | 128 | ACKNOWLEDGE |
| `ACK_gi_unmapped_pending_policy` | 78 | ACKNOWLEDGE |
| `RESOLVE_lw_pick_historical_seed` | 71 | RESOLVE |
| `HOLD_active_fg_alias_review_queue` | 54 | HOLD (operator queue) |
| `RESOLVE_historical_burst` | 26 | RESOLVE |
| `HOLD_lw_real_catalog_gap` | 20 | HOLD (operator queue) |
| `DELETE_dev_fixture_with_dependency_check` | 12 | DELETE (with item-table cleanup, gated) |
| `ACK_gtset_archived` | 9 | ACKNOWLEDGE |
| `DELETE_test_fixture` | 5 | DELETE |
| `RESOLVE_evidence_alias_active_and_syncing` | 5 | RESOLVE (orphan dedupe) |
| `RESOLVE_gi_non_ils_by_design` | 4 | RESOLVE |
| `HOLD_operational_approval` | 3 | HOLD (operator approval) |
| `DELETE_lw_test_or_empty` | 2 | DELETE |
| `RESOLVE_item_inactive` | 2 | RESOLVE |
| `HOLD_schedule_rebuild_verifier` | 1 | HOLD (production gate) |
| `HOLD_schedule_export_job` | 1 | HOLD (transitional v1) |
| **total open** | **421** | — |

Sum check: 128+78+71+54+26+20+12+9+5+5+4+3+2+2+1+1 = **421** ✓

### 1.3 Action totals

| action | exceptions affected | other side-effects |
|---|---:|---|
| DELETE | 19 | + DELETE 12 fixture rows from `private_core.items` (gated on dependency checks) |
| RESOLVE (status → `resolved`) | 108 | none |
| ACKNOWLEDGE (status → `acknowledged`) | 215 | none |
| HOLD (status unchanged; operator queue derived) | 79 | external decision/work queues created |
| **total touched** | **421** | — |

### 1.4 Status snapshot AFTER cleanup (projection)

| status | n |
|---|---:|
| open / actionable | 79 |
| acknowledged / non-operator-actionable | 4 + 215 = **219** |
| resolved | 77 + 108 = **185** |
| auto_resolved | 2 |
| **total rows in `private_core.exceptions`** | 504 − 19 = **485** |
| **total deleted** | **19** |

### 1.5 Operator-actionable inbox reduction

Before: 421 open. After: 79 operator-actionable.
**Δ −81% operator inbox load.**

The 79 are:
- 54 — active FG without Shopify alias (review queue, D1)
- 20 — real LW catalog gaps (decision table, D2)
- 3 — operational approvals (positive_adjustment ×2, po_line_over_receipt ×1)
- 1 — `rebuild_stale` (must close after pg_cron run, D4)
- 1 — `export_stale` (close after first artifact + freshness, D3)

---

## 2. Action table by deterministic filter

Every open exception is classified by exactly one filter. The same SQL CASE that produced §1.2 drives the action table.

### 2.1 DELETE bucket (19 exception rows + 12 item rows, dependency-gated)

#### 2.1.1 `DELETE_test_fixture` — 5 rows
**Filter:** `status='open' AND category='shopify_unmapped_item' AND dedupe_key LIKE '%TEST-%'`
**Reason:** Resolver test fixtures (`TEST-SKU-RESOLVER-FG-PENDING/APPROVED/REJECTED`, `TEST-LW-PROBE-FG-1`).

#### 2.1.2 `DELETE_lw_test_or_empty` — 2 rows
**Filter:** `status='open' AND category='lionwheel_unknown_sku' AND (REPLACE(dedupe_key,'lw_sku:','') LIKE 'TEST-%' OR REPLACE(dedupe_key,'lw_sku:','')='')`
**Reason:** Test probe + LW data-quality bug (empty SKU). No operator action possible.

#### 2.1.3 `DELETE_dev_fixture_with_dependency_check` — 12 rows + 12 items
**Filter:** `status='open' AND category='shopify_variant_not_found' AND dedupe_key ~ '(ammc-slice2-|T1REG-|T2DET-|T3BLK-).*177(7|8|9|0)[0-9]+'`
**Items implicated** (all currently `status='active'` in items, no business reason to keep):
- `ammc-slice2-1777199392560-ITM-1`
- `ammc-slice2-1777199392560-ITM-2`
- `ammc-slice2-1777199392560-ITM-BOM`
- `T1REG-BF-1777205442687`
- `T1REG-BF-NOSI-1777205442687`
- `T2DET-1777209889185-MFR`
- `T2DET-1777210102536-BF`
- `T2DET-1777210102536-MFR`
- `T2DET-1777210369167-BF`
- `T2DET-1777210369167-MFR`
- `T3BLK-1777276453154-FG`
- `T3BLK-1777276834406-FG`

**Note:** these are timestamp-named dev fixtures (Unix-ms in IDs) left active from AMMC Slices 1–6 and T1/T2/T3 portal-OS testing. The exception fires precisely because they have neither a Shopify variant SKU nor an alias.
**Gate:** every item must pass §5 dependency checks before its DELETE proceeds. Failed checks halt and escalate.

### 2.2 RESOLVE bucket (108 rows)

| filter | n | resolution_notes |
|---|---:|---|
| `status='open' AND category='shopify_network_failure'` | 26 | `historical burst against pre-runtime variants.json cache (size=193) on 2026-04-23 18:34; superseded by Shopify runtime RUNTIME_READY 2026-04-21` |
| `status='open' AND category='lw_pick_data_missing'` | 71 | `historical 2026-04-18 LW seed snapshot lacked picked_quantity per line; not used for production stock decrement; live producer remains active for new ROUNDTRIP_DELIVERED lines (D2 policy: stock decrements by picked_quantity)` |
| `status='open' AND category='gi_non_ils_currency'` | 4 | `by-design U-C2 v1: ILS-only ingest; revisit when multi-currency lands` |
| `status='open' AND category='shopify_unmapped_item' AND dedupe_key NOT LIKE '%TEST-%' AND items.status<>'active'` | 2 | `item moved to status<>'active'; FG no longer sold via Shopify` |
| `status='open' AND category='shopify_variant_not_found' AND <evidence pack passes per §2.3.1>` | 5 | `catalog item exists, integration_sku_map alias is 'approved' for source_channel='shopify', and shopify_fg_sync_history shows write_status='ok' within 24h; exception was sticky from prior bad-match audit corrected 2026-04-23/26 — verified post-correction` |

**Total RESOLVE: 26 + 71 + 4 + 2 + 5 = 108** ✓

### 2.3.1 Evidence pack — `RESOLVE_evidence_alias_active_and_syncing` (5 rows)

Per §0.1 catalog-safe rule, each of the 5 rows must individually pass the **7-condition evidence predicate** before resolution. The query is run as a gating step inside the cleanup transaction (after the dry-run in §3 has been reviewed and approved):

```sql
WITH targets AS (
  SELECT e.exception_id,
         e.created_at AS exception_created_at,
         REPLACE(e.dedupe_key,'shopify_variant_not_found:','') AS variant_sku
  FROM private_core.exceptions e
  WHERE e.status='open' AND e.category='shopify_variant_not_found'
    AND REPLACE(e.dedupe_key,'shopify_variant_not_found:','')
        IN ('GTCC-SAN-WHI-3.85L','GTCC-SAN-RED-3.85L',
            'GTEL-MAR-CLA-0.3L','GTEL-MAR-PEA-0.3L','GTEL-MAR-STR-0.3L')
),
last_sync AS (
  SELECT h.variant_sku,
         MAX(h.cycle_at) FILTER (WHERE h.write_status='ok') AS last_ok_cycle_at
  FROM private_core.shopify_fg_sync_history h
  GROUP BY h.variant_sku
),
newer_exc AS (
  SELECT t.variant_sku,
         COUNT(*) AS n_newer_exceptions
  FROM targets t
  JOIN last_sync ls ON ls.variant_sku = t.variant_sku
  JOIN private_core.exceptions e2
    ON  e2.created_at > ls.last_ok_cycle_at
    AND e2.dedupe_key LIKE '%' || t.variant_sku
  GROUP BY t.variant_sku
)
SELECT
  t.exception_id,
  t.variant_sku,
  m.item_id            AS mapped_item_id,
  m.alias_id           AS alias_id,
  m.approval_status    AS alias_status,
  m.approved_at        AS alias_approved_at,
  i.status             AS items_status,
  i.barcode            AS items_barcode,
  i.legacy_sku         AS items_legacy_sku,
  i.sku                AS items_sku,
  ls.last_ok_cycle_at  AS last_ok_sync_at,
  COALESCE(ne.n_newer_exceptions, 0) AS newer_exceptions_after_sync,
  -- 7-condition evidence verdict
  (i.item_id IS NOT NULL)                                                           AS cond1_item_exists,
  (i.status = 'ACTIVE')                                                             AS cond2_item_active,
  (i.sku = t.variant_sku OR i.legacy_sku = t.variant_sku)                           AS cond3_shopify_sku_present,
  (i.barcode IS NOT NULL)                                                           AS cond4_barcode_canonical_populated,
  (m.approval_status='approved' AND m.source_channel='shopify' AND m.item_id=i.item_id)
                                                                                    AS cond5_alias_approved,
  (ls.last_ok_cycle_at IS NOT NULL)                                                 AS cond6_latest_sync_ok,
  (COALESCE(ne.n_newer_exceptions,0) = 0)                                           AS cond7_no_regression,
  CASE
    WHEN i.item_id IS NOT NULL
     AND i.status = 'ACTIVE'
     AND (i.sku = t.variant_sku OR i.legacy_sku = t.variant_sku)
     AND i.barcode IS NOT NULL
     AND m.approval_status='approved' AND m.source_channel='shopify' AND m.item_id=i.item_id
     AND ls.last_ok_cycle_at IS NOT NULL
     AND COALESCE(ne.n_newer_exceptions,0) = 0
    THEN 'PASS — all 7 conditions hold; eligible for evidence-backed resolve'
    ELSE 'FAIL — at least one condition failed; route to HOLD_catalog_reconstruction_required'
  END AS evidence_verdict
FROM targets t
LEFT JOIN private_core.integration_sku_map m
  ON m.external_sku = t.variant_sku AND m.source_channel = 'shopify'
LEFT JOIN private_core.items i ON i.item_id = m.item_id
LEFT JOIN last_sync  ls ON ls.variant_sku = t.variant_sku
LEFT JOIN newer_exc  ne ON ne.variant_sku = t.variant_sku
ORDER BY t.variant_sku;
```

**Verdict at execution time** is captured row-by-row and attached to the per-row resolution_notes; no resolve happens for any row whose `evidence_verdict` is FAIL.

**Resolution_notes template (Tom-locked 2026-04-27):**

```
Canonical item exists under <FG item_id>; Shopify-facing SKU <GT...> maps via
approved alias (integration_sku_map.alias_id=<uuid>, approved_at=<ts>);
items.legacy_sku/sku and barcode verified canonical-side (items.barcode=<barcode>);
latest Shopify stock sync write_status='ok' at <cycle_at_ts>; no newer exception
emitted for the same SKU after that sync; exception was stale/orphaned from
pre-alias state.
```

**Wording precision (Tom 2026-04-27):** the resolution_notes deliberately says "stock sync write_status='ok'" — not "Shopify reports the product as active/sellable". The two are different. Sellability is not asserted by this pass.

**Live evidence (read 2026-04-27 12:46 UTC from production DB, full 7-condition predicate executed, all 5 rows PASS):**

| variant_sku | mapped item_id | c1 exist | c2 active | c3 sku/legacy | c4 barcode (canonical) | c5 alias_approved | c6 sync_ok | c7 no_regression | verdict |
|---|---|---|---|---|---|---|---|---|---|
| GTCC-SAN-WHI-3.85L | FG-SAN-WHI-3850ML | ✓ | ✓ ACTIVE | ✓ both fields = SKU | ✓ 0726529648034 | ✓ approved 2026-04-26 09:13 | ✓ 2026-04-27 12:45:01 | ✓ 0 newer exceptions | **PASS** |
| GTCC-SAN-RED-3.85L | FG-SAN-RED-3850ML | ✓ | ✓ ACTIVE | ✓ both fields = SKU | ✓ 0726529648027 | ✓ approved 2026-04-26 09:13 | ✓ 2026-04-27 12:45:01 | ✓ 0 newer exceptions | **PASS** |
| GTEL-MAR-CLA-0.3L | FG-MAR-CLA-300ML | ✓ | ✓ ACTIVE | ✓ both fields = SKU | ✓ 0726529648270 | ✓ approved 2026-04-23 18:34 | ✓ 2026-04-27 12:45:01 | ✓ 0 newer exceptions | **PASS** |
| GTEL-MAR-PEA-0.3L | FG-MAR-PEA-300ML | ✓ | ✓ ACTIVE | ✓ both fields = SKU | ✓ 0726529648157 | ✓ approved 2026-04-23 18:34 | ✓ 2026-04-27 12:45:01 | ✓ 0 newer exceptions | **PASS** |
| GTEL-MAR-STR-0.3L | FG-MAR-STR-300ML | ✓ | ✓ ACTIVE | ✓ both fields = SKU | ✓ 0726529648294 | ✓ approved 2026-04-26 09:13 | ✓ 2026-04-27 12:45:01 | ✓ 0 newer exceptions | **PASS** |

All 5 rows PASS at spec authoring time. The verdict is **re-verified inside the cleanup transaction** immediately before each UPDATE — execution-time drift (e.g., a fresh exception emitted post-sync) will flip a row to FAIL and route it to `HOLD_catalog_reconstruction_required`. The re-verification is non-optional.

**Why this is not "mechanical resolve based on missing item_id":** the predicate requires seven positive proofs that the underlying business state is correct. It tests for presence and consistency, not absence. A row that fails any condition drops to `HOLD_catalog_reconstruction_required` (§2.3.2).

### 2.3.2 Reconstruction queue — `HOLD_catalog_reconstruction_required` (currently 0 rows)

The 5 candidate rows enumerated in §2.3.1 currently all PASS the evidence predicate, so this bucket is empty in the current snapshot. The bucket exists as a permanent landing zone: any future `shopify_variant_not_found` row referencing a real-looking commercial SKU that fails the §2.3.1 predicate goes here, with a per-row reconstruction worksheet:

| field | source |
|---|---|
| Shopify SKU | `dedupe_key` (post-prefix-strip) |
| Shopify title | live Shopify admin lookup (manual or API) |
| barcode | live Shopify variant + cross-check to `private_core.items.barcode` |
| current Shopify status | live Shopify admin (active / draft / archived) |
| proposed canonical item_id | derived per `FG-{family}-{variant}-{size_in_ML}` convention; if ambiguous → return proposal table to Tom |
| proposed item name | from existing item if equivalent found; else from Shopify product title |
| family / category | from `items.family` if existing equivalent; else manual classification |
| size / unit | from variant + `items.pack_size`/`sales_uom` |
| equivalent item exists under another key? | YES/NO + justification (legacy_sku/barcode/sku match) |
| recommended action | `create_alias` (item exists) / `create_item` (no equivalent) / `restore_item` (was deactivated) / `hold_for_tom` (ambiguous) |
| confidence reason | match-level evidence string |

Recommended actions are subject to the rule "If equivalent item exists, create alias — never duplicate the item."

### 2.3 ACKNOWLEDGE bucket (215 rows)

| filter | n | acknowledged_notes |
|---|---:|---|
| `status='open' AND category='lionwheel_capped_window_gap'` | 128 | `info-only diagnostic from LW 100-row poll cap; pending D5 job-side suppress / move to integration_diagnostics; not operator-actionable; do not auto-resolve — historical artifact for LW corridor audit` |
| `status='open' AND category='gi_unmapped_supplier'` | 78 | `GI ingest noise pending D6 v1 mapping policy; admin expenses (utilities/fuel/parking/telecom) need ignore lane; ~15 real GT suppliers (טמפו, אסי את אור, פרופק, אומגה, קיטהקאטה, סוד היין, רוזנפלד אריזות, מיקי מדבקות, נ.ענבי, צבר, ארגל פוד סרוויס, ויירדוז, פייקול, שריווד, דנירן) need manual map via /admin/suppliers` |
| `status='open' AND category='lionwheel_unknown_sku' AND REPLACE(dedupe_key,'lw_sku:','') LIKE 'GTSET-%'` | 9 | `archived/not-currently-sold bundle SKU per Tom 2026-04-27; do not alias to Shopify; reopen if any GTSET reappears in orders_mirror with captured_at > 2026-04-18 17:30:48` |

**Total ACK: 128 + 78 + 9 = 215** ✓

### 2.4 HOLD bucket (79 rows — no-op now; operator queues created)

| filter | n | downstream queue |
|---|---:|---|
| `status='open' AND category='shopify_unmapped_item' AND dedupe_key NOT LIKE '%TEST-%' AND items.status='active'` | 54 | **D1 alias review queue** — heuristic resolver (Shopify cache + variant SKU + barcode + legacy_sku) → review per product family → explicit approval per row |
| `status='open' AND category='lionwheel_unknown_sku' AND NOT (sku LIKE 'GTSET-%' OR sku LIKE 'TEST-%' OR sku='')` | 20 | **D2 catalog decision table** — TEA_FLAVOR_NEW(9) / ACCESSORY(5) / GLASSWARE(2) / OTHER(3) / EAN(1) |
| `status='open' AND category IN ('positive_adjustment','po_line_over_receipt')` | 3 | **operational approval queue** — `/exceptions` planner action |
| `status='open' AND category='rebuild_stale'` | 1 | **D4 — schedule pg_cron `rebuild_verifier()` daily 03:00 IL** |
| `status='open' AND category='export_stale'` | 1 | **D3 — schedule nightly read-only values-only export** |

**Total HOLD: 54 + 20 + 3 + 1 + 1 = 79** ✓

---

## 3. Dry-run SQL

All cleanup SQL is read-only at dry-run stage. No writes. Output reviewed before execution stage.

### 3.1 Bucket dry-run (full id-level dump)

```sql
-- 3.1 — print every open exception_id with its assigned bucket
WITH classified AS (
  SELECT
    e.exception_id,
    e.category,
    e.dedupe_key,
    e.title,
    e.created_at,
    REPLACE(e.dedupe_key,'shopify_unmapped_item:','')   AS shopify_key,
    REPLACE(e.dedupe_key,'shopify_variant_not_found:','') AS variant_key,
    REPLACE(e.dedupe_key,'lw_sku:','')                  AS lw_key
  FROM private_core.exceptions e
  WHERE e.status = 'open'
)
SELECT
  c.exception_id,
  c.category,
  c.dedupe_key,
  CASE
    WHEN c.category='shopify_unmapped_item' AND c.dedupe_key LIKE '%TEST-%'
      THEN 'DELETE_test_fixture'
    WHEN c.category='shopify_unmapped_item' AND i.item_id IS NULL
      THEN 'HOLD_catalog_reconstruction_required'  -- defensive (none expected); per §0.1 never resolve mechanically on missing item_id
    WHEN c.category='shopify_unmapped_item' AND i.status='active'
      THEN 'HOLD_active_fg_alias_review_queue'
    WHEN c.category='shopify_unmapped_item'
      THEN 'RESOLVE_item_inactive'
    WHEN c.category='shopify_variant_not_found' AND i.item_id IS NULL
      THEN 'RESOLVE_evidence_alias_active_and_syncing'
    WHEN c.category='shopify_variant_not_found' AND c.variant_key ~ '(ammc-slice2-|T1REG-|T2DET-|T3BLK-).*177[789][0-9]+'
      THEN 'DELETE_dev_fixture_with_dependency_check'
    WHEN c.category='shopify_variant_not_found'
      THEN 'HOLD_catalog_reconstruction_required'  -- defensive (none expected); never resolve mechanically
    WHEN c.category='shopify_network_failure'
      THEN 'RESOLVE_historical_burst'
    WHEN c.category='lionwheel_unknown_sku' AND (c.lw_key LIKE 'TEST-%' OR c.lw_key='')
      THEN 'DELETE_lw_test_or_empty'
    WHEN c.category='lionwheel_unknown_sku' AND c.lw_key LIKE 'GTSET-%'
      THEN 'ACK_gtset_archived'
    WHEN c.category='lionwheel_unknown_sku'
      THEN 'HOLD_lw_real_catalog_gap'
    WHEN c.category='lw_pick_data_missing'
      THEN 'RESOLVE_lw_pick_historical_seed'
    WHEN c.category='gi_unmapped_supplier'
      THEN 'ACK_gi_unmapped_pending_policy'
    WHEN c.category='gi_non_ils_currency'
      THEN 'RESOLVE_gi_non_ils_by_design'
    WHEN c.category='lionwheel_capped_window_gap'
      THEN 'ACK_lw_capped_info_only'
    WHEN c.category IN ('positive_adjustment','po_line_over_receipt')
      THEN 'HOLD_operational_approval'
    WHEN c.category='export_stale'
      THEN 'HOLD_schedule_export_job'
    WHEN c.category='rebuild_stale'
      THEN 'HOLD_schedule_rebuild_verifier'
    ELSE 'UNCLASSIFIED'
  END AS bucket
FROM classified c
LEFT JOIN private_core.items i
  ON  (c.category='shopify_unmapped_item'      AND i.item_id = c.shopify_key)
   OR (c.category='shopify_variant_not_found'  AND i.item_id = c.variant_key)
ORDER BY bucket, c.category, c.created_at;
```

**Validation invariants** (run alongside):
1. `SUM(bucket COUNT) = 421` (live count — re-read at execution time; drift expected).
2. `bucket='UNCLASSIFIED' COUNT = 0`.
3. Every bucket count matches §1.2 exactly (within drift only on `ACK_lw_capped_info_only`).

### 3.2 DELETE dry-run (no execution)

```sql
-- exceptions slated for DELETE (19)
SELECT e.exception_id, e.category, e.dedupe_key, e.title, e.created_at
FROM private_core.exceptions e
WHERE e.status='open' AND (
  (e.category='shopify_unmapped_item' AND e.dedupe_key LIKE '%TEST-%')
  OR (e.category='lionwheel_unknown_sku' AND (REPLACE(e.dedupe_key,'lw_sku:','') LIKE 'TEST-%' OR REPLACE(e.dedupe_key,'lw_sku:','')=''))
  OR (e.category='shopify_variant_not_found' AND REPLACE(e.dedupe_key,'shopify_variant_not_found:','') ~ '(ammc-slice2-|T1REG-|T2DET-|T3BLK-).*177[789][0-9]+')
)
ORDER BY e.category, e.dedupe_key;

-- items slated for DELETE (12, dependency-gated by §5)
SELECT i.item_id, i.status, i.supply_method, i.created_at
FROM private_core.items i
WHERE i.item_id IN (
  'ammc-slice2-1777199392560-ITM-1','ammc-slice2-1777199392560-ITM-2','ammc-slice2-1777199392560-ITM-BOM',
  'T1REG-BF-1777205442687','T1REG-BF-NOSI-1777205442687',
  'T2DET-1777209889185-MFR','T2DET-1777210102536-BF','T2DET-1777210102536-MFR',
  'T2DET-1777210369167-BF','T2DET-1777210369167-MFR',
  'T3BLK-1777276453154-FG','T3BLK-1777276834406-FG'
)
ORDER BY i.item_id;
```

### 3.3 UPDATE dry-run

```sql
-- RESOLVE counts preview
SELECT
  CASE
    WHEN category='shopify_network_failure' THEN 'RESOLVE_historical_burst'
    WHEN category='lw_pick_data_missing' THEN 'RESOLVE_lw_pick_historical_seed'
    WHEN category='gi_non_ils_currency' THEN 'RESOLVE_gi_non_ils_by_design'
  END AS bucket,
  COUNT(*) AS n
FROM private_core.exceptions
WHERE status='open' AND category IN ('shopify_network_failure','lw_pick_data_missing','gi_non_ils_currency')
GROUP BY bucket;

-- (analogous queries for RESOLVE_item_inactive, RESOLVE_evidence_alias_active_and_syncing, ACKNOWLEDGE buckets)
```

---

## 4. Rollback SQL

### 4.1 Snapshots (taken first, in single transaction, before any cleanup writes)

```sql
BEGIN;
CREATE TABLE private_core._exceptions_pre_cleanup_2026_04_27
  AS SELECT * FROM private_core.exceptions;
CREATE TABLE private_core._items_pre_cleanup_2026_04_27
  AS SELECT * FROM private_core.items WHERE item_id IN (
    'ammc-slice2-1777199392560-ITM-1','ammc-slice2-1777199392560-ITM-2','ammc-slice2-1777199392560-ITM-BOM',
    'T1REG-BF-1777205442687','T1REG-BF-NOSI-1777205442687',
    'T2DET-1777209889185-MFR','T2DET-1777210102536-BF','T2DET-1777210102536-MFR',
    'T2DET-1777210369167-BF','T2DET-1777210369167-MFR',
    'T3BLK-1777276453154-FG','T3BLK-1777276834406-FG'
  );
COMMIT;

-- Verify snapshot integrity
SELECT COUNT(*) AS exc_snapshot_rows FROM private_core._exceptions_pre_cleanup_2026_04_27;
SELECT COUNT(*) AS items_snapshot_rows FROM private_core._items_pre_cleanup_2026_04_27;
-- expect: 504 (or live drift), 12
```

### 4.2 Per-action transaction wrapping

Each action class runs in its own transaction. `rebuild_verifier()` is invoked inside the transaction; non-zero result rolls back.

```sql
BEGIN;
-- DELETE step
DELETE FROM private_core.exceptions WHERE exception_id IN (...);
DELETE FROM private_core.items     WHERE item_id      IN (...);
SELECT private_core.rebuild_verifier() AS drift;
-- if drift <> 0, ROLLBACK;
COMMIT;
```

### 4.3 Restore commands

```sql
-- Restore deleted exceptions
INSERT INTO private_core.exceptions
SELECT * FROM private_core._exceptions_pre_cleanup_2026_04_27 s
WHERE s.exception_id NOT IN (SELECT exception_id FROM private_core.exceptions);

-- Restore deleted items
INSERT INTO private_core.items
SELECT * FROM private_core._items_pre_cleanup_2026_04_27 s
WHERE s.item_id NOT IN (SELECT item_id FROM private_core.items);

-- Restore status / resolution_notes for RESOLVE / ACKNOWLEDGE
UPDATE private_core.exceptions e
SET status = s.status,
    acknowledged_at = s.acknowledged_at,
    acknowledged_by = s.acknowledged_by,
    resolved_at = s.resolved_at,
    resolved_by = s.resolved_by,
    resolution_notes = s.resolution_notes,
    updated_at = NOW()
FROM private_core._exceptions_pre_cleanup_2026_04_27 s
WHERE e.exception_id = s.exception_id;
```

### 4.3.1 Restore caveat (advisory)

Items restore via §4.3 assumes §5 dependency checks were clean before the original DELETE. Because §5 halts on any dependency hit, the items DELETE only proceeds if no child rows reference the item_id at the time of DELETE. The restore therefore re-INSERTs the item itself but does not need to recreate child rows (none existed at delete-time). If somehow a child row was deleted via cascade *despite* clean §5 (a logic bug or schema drift), the restore is partial and a manual reconciliation tranche is required — flag immediately to Tom.

### 4.4 Snapshot retention

Snapshots persist for **30 days**. After 30 days clean drop:

```sql
DROP TABLE private_core._exceptions_pre_cleanup_2026_04_27;
DROP TABLE private_core._items_pre_cleanup_2026_04_27;
```

Rollback time budget: **< 60 seconds** for full restore.

---

## 5. Pre-delete dependency checks

Before deleting **any** of the 12 items, every check below must return **zero rows** for that item. Any non-zero result halts the cleanup and escalates to Tom.

### 5.1 Stock truth

```sql
-- 5.1.a — stock_ledger
SELECT item_id, COUNT(*) AS n FROM private_core.stock_ledger
WHERE item_id IN (<12 ids>) GROUP BY item_id;

-- 5.1.b — current_balances and shadow
SELECT item_id, calculated_on_hand FROM private_core.current_balances WHERE item_id IN (<12 ids>);
SELECT item_id, calculated_on_hand FROM private_core.current_balances_shadow WHERE item_id IN (<12 ids>);

-- 5.1.c — anchors
SELECT item_id, COUNT(*) AS n FROM private_core.balance_anchors_current WHERE item_id IN (<12 ids>) GROUP BY item_id;
SELECT item_id, COUNT(*) AS n FROM private_core.balance_anchors_history WHERE item_id IN (<12 ids>) GROUP BY item_id;
```

### 5.2 Forms / receipts / production

```sql
-- 5.2.a — goods receipts
SELECT gr.gr_id, grl.item_id FROM private_core.goods_receipt_lines grl
JOIN private_core.goods_receipts gr USING (gr_id) WHERE grl.item_id IN (<12 ids>);

-- 5.2.b — purchase order lines
SELECT po_line_id, item_id FROM private_core.purchase_order_lines WHERE item_id IN (<12 ids>);

-- 5.2.c — production_actual
SELECT * FROM private_core.production_actual WHERE item_id IN (<12 ids>);

-- 5.2.d — physical counts
SELECT * FROM private_core.physical_counts WHERE item_id IN (<12 ids>);

-- 5.2.e — waste / adjustments
SELECT * FROM private_core.waste_adjustments WHERE item_id IN (<12 ids>);
```

### 5.3 Planning / forecast / BOM / mappings

```sql
-- 5.3.a — forecast lines
SELECT COUNT(*) AS n, item_id FROM private_core.forecast_lines WHERE item_id IN (<12 ids>) GROUP BY item_id;

-- 5.3.b — planning_run_recommendations
SELECT * FROM private_core.planning_run_recommendations WHERE item_id IN (<12 ids>);

-- 5.3.c — planning_run_fg_coverage / component_demand / component_netting
SELECT 'fg_coverage' AS t, COUNT(*) FROM private_core.planning_run_fg_coverage WHERE item_id IN (<12 ids>);
SELECT 'comp_demand' AS t, COUNT(*) FROM private_core.planning_run_component_demand WHERE item_id IN (<12 ids>);
SELECT 'comp_netting' AS t, COUNT(*) FROM private_core.planning_run_component_netting WHERE item_id IN (<12 ids>);

-- 5.3.d — BOM head/version/lines (item as parent or as child)
SELECT 'bom_head_primary' AS t, item_id FROM private_core.items WHERE item_id IN (<12 ids>) AND primary_bom_head_id IS NOT NULL;
SELECT 'bom_lines_as_child' AS t, COUNT(*) FROM private_core.bom_lines bl
  JOIN private_core.bom_version bv ON bv.bom_version_id = bl.bom_version_id
  JOIN private_core.bom_head bh ON bh.bom_head_id = bv.bom_head_id
  WHERE bl.final_component_id IN (<12 ids>);

-- 5.3.e — integration_sku_map (alias references)
SELECT * FROM private_core.integration_sku_map WHERE item_id IN (<12 ids>);

-- 5.3.f — supplier_items
SELECT * FROM private_core.supplier_items WHERE item_id IN (<12 ids>);

-- 5.3.g — orders_mirror_lines
SELECT lw_sku, item_id, COUNT(*) FROM private_core.orders_mirror_lines WHERE item_id IN (<12 ids>) GROUP BY lw_sku, item_id;

-- 5.3.h — shopify_fg_sync_history
SELECT * FROM private_core.shopify_fg_sync_history WHERE item_id IN (<12 ids>);

-- 5.3.i — change_log (audit trail)
SELECT entity_id, COUNT(*) AS n FROM private_core.change_log
WHERE entity_type='item' AND entity_id::text IN (<12 ids>) GROUP BY entity_id;
```

### 5.4 Halt rule

If **any** check above returns ≥1 row for a given item, the DELETE for that specific item halts. Other items proceed individually. The halted item is escalated to Tom with a copy of the dependency hits. Items are deleted **one at a time** within the transaction, each guarded by its own dependency check.

`change_log` rows are tolerated only as historical audit (item creation/update). Any row implying ledger or stock-truth touch of the item halts.

---

## 6. Before/after status counts (with proof of stock-truth integrity)

### 6.1 Before (live read 2026-04-27)

```sql
-- exceptions table status
SELECT status, COUNT(*) FROM private_core.exceptions GROUP BY status;
-- expected: open=421 (drift), resolved=77, acknowledged=4, auto_resolved=2, total=504

-- stock truth probes
SELECT private_core.rebuild_verifier() AS drift_before;
SELECT COUNT(*) AS ledger_rows_before FROM private_core.stock_ledger;
SELECT COUNT(*) AS balances_rows_before FROM private_core.current_balances;
SELECT COUNT(*) AS anchors_curr_before FROM private_core.balance_anchors_current;
SELECT COUNT(*) AS anchors_hist_before FROM private_core.balance_anchors_history;
SELECT MAX(posted_at) AS latest_ledger_post_before FROM private_core.stock_ledger;
```

### 6.2 After (must hold post-cleanup)

```sql
-- exceptions table status
SELECT status, COUNT(*) FROM private_core.exceptions GROUP BY status;
-- expected: open=79 (steady-state; drift on lionwheel_capped_window_gap allowed)
--           acknowledged=219, resolved=185, auto_resolved=2, total=485

-- stock truth probes (must equal §6.1 outputs exactly)
SELECT private_core.rebuild_verifier() AS drift_after;
SELECT COUNT(*) AS ledger_rows_after FROM private_core.stock_ledger;
SELECT COUNT(*) AS balances_rows_after FROM private_core.current_balances;
SELECT COUNT(*) AS anchors_curr_after FROM private_core.balance_anchors_current;
SELECT COUNT(*) AS anchors_hist_after FROM private_core.balance_anchors_history;
SELECT MAX(posted_at) AS latest_ledger_post_after FROM private_core.stock_ledger;
```

### 6.3 Stock-truth integrity invariants

The cleanup is rejected if any of these fails:

| invariant | expected |
|---|---|
| `drift_after = 0` | always |
| `drift_after = drift_before` | must be equal (both 0) |
| `ledger_rows_after = ledger_rows_before` | exact equality |
| `balances_rows_after = balances_rows_before` | exact equality |
| `anchors_curr_after = anchors_curr_before` | exact equality |
| `anchors_hist_after = anchors_hist_before` | exact equality |
| `latest_ledger_post_after = latest_ledger_post_before` | exact equality |

If any invariant fails, `ROLLBACK` and abort.

### 6.4 Tolerance on `lionwheel_capped_window_gap` drift

Producer-driven drift is expected on this category. The expected open count after the cleanup transaction commits is:

```
open_after_target = 79
open_after_observed = open_after_target + N_capped_drift
where N_capped_drift = COUNT(*) FROM private_core.exceptions
                       WHERE category='lionwheel_capped_window_gap'
                         AND status='open'
                         AND created_at > <snapshot_taken_at>
```

§6.3 invariants are **not** evaluated against this category drift. The status-count check is reformulated as:

```
open_after_observed - N_capped_drift = 79  -- must hold
```

All other invariants must hold exactly. If `acknowledged`, `resolved`, `auto_resolved`, or stock-truth probes drift, the cleanup is rejected and rolled back.

---

## 7. rebuild_verifier proof-of-zero

### 7.1 Pre-cleanup baseline

```sql
SELECT private_core.rebuild_verifier() AS drift;  -- expect 0
```

If non-zero before cleanup begins → halt; this is a pre-existing parity defect that must be resolved first.

### 7.2 Per-transaction guard (re-run after every action class)

```sql
BEGIN;
  -- ... cleanup writes ...
  SELECT private_core.rebuild_verifier() AS drift;
  -- if drift <> 0 → ROLLBACK and escalate
COMMIT;
```

### 7.3 Post-cleanup confirmation

```sql
SELECT private_core.rebuild_verifier() AS drift_final;  -- must be 0
```

### 7.4 D4 follow-up — `rebuild_stale` exception closure

`rebuild_stale` exception must remain `open` until `rebuild_verifier()` runs successfully under pg_cron schedule (D4 — daily 03:00 Asia/Jerusalem). Closure script (post-D4):

```sql
UPDATE private_core.exceptions
SET status='resolved', resolved_at=NOW(),
    resolution_notes='rebuild_verifier scheduled in pg_cron; first scheduled run completed; freshness producer registered'
WHERE status='open' AND category='rebuild_stale';
```

Same pattern for `export_stale` after D3 first successful artifact + freshness visible.

---

## 8. Remaining decision queues

This spec **does not** consume Tom's locked decisions D1–D6 — those will be acted on in subsequent specs/tranches. After this cleanup completes:

### 8.1 D1 — bulk alias review queue (54 active FG)

**Output produced by post-cleanup query:**

```sql
WITH active_unmapped AS (
  SELECT REPLACE(e.dedupe_key,'shopify_unmapped_item:','') AS sku, e.exception_id
  FROM private_core.exceptions e
  JOIN private_core.items i ON i.item_id = REPLACE(e.dedupe_key,'shopify_unmapped_item:','')
  WHERE e.status='open' AND e.category='shopify_unmapped_item'
    AND e.dedupe_key NOT LIKE '%TEST-%' AND i.status='active'
)
SELECT
  i.item_id,
  i.family,
  i.item_name,
  i.legacy_sku,
  i.barcode,
  i.sku AS items_sku_field,
  -- candidate Shopify variant via legacy_sku
  ssv.shopify_variant_sku AS candidate_via_legacy_sku,
  -- candidate via barcode
  ssv2.shopify_variant_sku AS candidate_via_barcode,
  -- confidence reason
  CASE
    WHEN ssv.shopify_variant_sku IS NOT NULL AND ssv2.shopify_variant_sku IS NOT NULL
         AND ssv.shopify_variant_sku = ssv2.shopify_variant_sku THEN 'HIGH: legacy_sku=barcode match'
    WHEN ssv.shopify_variant_sku IS NOT NULL THEN 'MEDIUM: legacy_sku match only'
    WHEN ssv2.shopify_variant_sku IS NOT NULL THEN 'MEDIUM: barcode match only'
    ELSE 'LOW: requires manual mapping'
  END AS confidence
FROM active_unmapped au
JOIN private_core.items i ON i.item_id = au.sku
LEFT JOIN private_core.shopify_sync_state ssv  ON ssv.shopify_variant_sku = i.legacy_sku
LEFT JOIN private_core.shopify_sync_state ssv2 ON ssv2.shopify_variant_sku = i.barcode
ORDER BY i.family, confidence DESC, i.item_id;
```

> Note: `shopify_sync_state` may need adaptation if it does not expose variant SKU directly — alternate: `shopify_fg_sync_history` projected to distinct variant SKUs. Confirmed structure check in the alias-tranche spec.

**Output fields per row** (per Tom D1):
- `item_id` (target)
- `proposed_mapping` (Shopify variant SKU)
- `confidence_reason` (HIGH / MEDIUM / LOW + justification)
- `source_fields` (legacy_sku / barcode / both)
- `action` (approve / edit / mark_problem)

Only HIGH-confidence rows are eligible for bulk-approval (still requires explicit operator confirmation per row). MEDIUM/LOW stay manual.

### 8.2 D2 — LW catalog decision table (20 real)

| group | n | example skus | proposed lane |
|---|---:|---|---|
| TEA_FLAVOR_NEW | 9 | GTCC-MUZ-{ANBL,APPZ,BLBR,CHRBL,JASM,PNMM,PSSP,SMAR,TROJ}-1L | catalog/alias decision pending Tom + Alex |
| ACCESSORY | 5 | AP-{DRI-ORA, DRI-PIN, DRI-ROS, FRO-MAT, TAP-PIN} | catalog-managed / non-catalog / ignore — only ignore if never stock-managed |
| GLASSWARE | 2 | GT-GLA-CUP, GT-GLA-MAT-PRINT | catalog-managed / non-catalog / ignore — same rule |
| OTHER | 3 | GT-PUE-FRE-1L, GTEL-BAB-RED-0.75L, GTMN-PIK-254 | per-SKU |
| EAN_AS_SKU | 1 | 7290003803217 | add `items.barcode → item_id` resolver path; do NOT treat as SKU |

### 8.3 D3 — `export_stale` schedule (transitional v1)

- **Owner:** Tom (operations).
- **Implementation choice (preferred):** Supabase Edge Function `factory_os_jobs` extension OR pg_cron — must produce a values-only Excel/CSV artifact, never round-trip into the platform.
- **Failure visibility:** must register as a `freshness_check` producer with warn/crit thresholds.
- **Closure:** `export_stale` resolves only after first successful run + artifact + freshness visibility.
- **If Tom decides to drop:** remove producer + dashboard expectation + docs contract + exception rule together.

### 8.4 D4 — `rebuild_verifier` schedule (production gate)

- **pg_cron, daily 03:00 Asia/Jerusalem.**
- Writes a `job_runs` row.
- Failure surfaces as production blocker.
- `rebuild_stale` resolves only after first successful scheduled run.

### 8.5 D5 — `lionwheel_capped_window_gap` suppression

- Short-term: remove from operator inbox via downgrade rule (e.g., default Inbox view filter excludes `category='lionwheel_capped_window_gap'`).
- Medium-term: move category to a new `private_core.integration_diagnostics` table.
- History preserved either way.

### 8.6 D6 — `gi_unmapped_supplier` two-lane policy

- **Lane A — admin expense ignore/suppress:** maintain a list of GI supplier_ids that are admin-only (utilities/fuel/parking/telecom) and skip exception emission for them. Do not insert into `suppliers`.
- **Lane B — operational supplier mapping queue:** queue real GT operational suppliers for manual mapping via `/admin/suppliers`. Mapping written to `suppliers.green_invoice_supplier_id`.

---

## 9. UI / operator impact — what stays visible

### 9.1 Visible after cleanup

The default Exceptions Inbox shows **79 operator-actionable rows**:

| group | n | next step for operator |
|---|---:|---|
| Active FG without Shopify alias (D1) | 54 | review queue, family-grouped, with proposed mapping |
| Real LW catalog gaps (D2) | 20 | decision table grouped by class |
| Operational approvals | 3 | planner approve/reject |
| `rebuild_stale` (D4) | 1 | wait for first pg_cron run |
| `export_stale` (D3) | 1 | wait for first nightly artifact |

### 9.2 Hidden but preserved

| group | n | where it lives | why hidden |
|---|---:|---|---|
| `acknowledged` historical | 219 | `private_core.exceptions` filtered out of default Inbox view | not operator-actionable; auditable via exception detail |
| `resolved` | 185 | same | settled, auditable |
| `auto_resolved` | 2 | same | system-closed |

### 9.3 Operator contract

After cleanup, the Inbox satisfies:
- **No false-action items.** Every row in default view has a real next step.
- **Full audit retained.** Acknowledged/resolved still queryable via `/exceptions?status=all` or admin DB view.
- **Live producers active.** New `lw_pick_data_missing` (real ROUNDTRIP_DELIVERED + missing pick), new `positive_adjustment`, new `po_line_over_receipt`, new `shopify_unmapped_item` (real new FG), new `lionwheel_unknown_sku` (real new SKU) all continue to surface.
- **Suppressed producers controlled.** `lionwheel_capped_window_gap` continues to write but is hidden from default view; moved to `integration_diagnostics` in D5 follow-up.
- **Bundle/archive policy enforced.** GTSET reappearance in `orders_mirror_lines` with `captured_at > 2026-04-18 17:30:48` re-opens the corresponding ack'd exception (manual step pending D5/D6 tooling).

---

## 10. Execution gating

This spec is **not yet approved for execution.**

Required next steps (in order):
1. Tom reviews this spec.
2. spec-document-reviewer subagent runs over it (per brainstorming process).
3. Dry-run §3 SQL is executed and output is reviewed (read-only).
4. Tom approves execution per action class (DELETE / RESOLVE / ACKNOWLEDGE).
5. §5 dependency checks run; any failure halts that item's DELETE.
6. §4 snapshots taken first.
7. Each action class wrapped in transaction with §7 `rebuild_verifier()` guard.
8. Post-cleanup invariants in §6.3 verified.
9. D3/D4 scheduling executed in their own specs.
10. Spec checked into git after Tom approval.

End of design spec.
