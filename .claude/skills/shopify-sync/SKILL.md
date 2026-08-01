---
name: shopify-sync
description: >
  GT ↔ Shopify inventory sync — live architecture, write contract, traps that cost
  real migrations, canonical queries, monitoring map. Load BEFORE any work touching:
  Shopify inventory/available/on_hand, shopify_available_reconcile, integration_sku_map,
  shopify_* feature flags or Edge Functions, sync exceptions, oversell/negative stock,
  "מלאי בשופיפיי", reconcile. If the task mentions Shopify and stock in the same
  sentence, this loads first.
---

# Shopify sync — domain truth

> Tier-2 knowledge: loaded on demand, ⊥ at boot. Live status = queries below, ⊥ prose here.
> Last distilled 2026-08-01 (session: orphan-writer discovery → 0305–0311 remediation).

## Architecture — who writes what

- **Sole live writer: Edge Fn `shopify_available_reconcile`** · cron job 24 `*/5` · source adopted at `gt-factory-os/supabase/functions/shopify_available_reconcile/index.ts` (0306, byte-identical to deployed; `verify_jwt=true` since 0309, cron sends vault JWT).
- Contract: `available = GREATEST(0, GREATEST(0,on_hand) − committed)` · **SET** (`inventorySetQuantities`, `ignoreCompareQuantity:true`) → converges every cycle, drift structurally impossible.
- `committed` = SUM open LionWheel `orders_mirror_lines.lw_qty_ordered`, `resolution_status='resolved'`, non-terminal `lw_status`. Known under-count: unresolved lines excluded (Tom-accepted).
- Gate: `private_core.feature_flags.shopify_available_reconcile_live` (`enabled` + `value.allowlist`, `*`=all). Pause valve: flag `shopify_available_write_paused` (auto-set on Shopify 401/403 — **halts ALL sync until manually cleared**).
- Zero clamp Tom-locked 2026-08-01: `available` = sellable count; oversell surfaces as **exception** (0308), ⊥ storefront negative.
- Cadence truth: ⊥ real-time. 5-min cycles; Shopify order → our `available` reflects ≤ ~20 min (LionWheel mirror 15m + cycle 5m; U-AW-1 Tom-accepted 2026-05-14).
- **Authority direction (Tom 2026-08-01): we are authoritative; Shopify = sync target.** Shopify owns only its order pipeline (`committed` on its side).
- Retired/dead paths: `factory_os_jobs` v1 inline write (no-op) · `runShopifyAvailableWrite` (shadow; env flag false since 2026-08-01) · v2 `shopify_fg_sync_v2` (crashes on R1 guard by design, sentinel `index.ts:87` false) · `shopify_fg_push` Edge Fn (deployed, unscheduled, flag-disabled by 0307 — **delta semantics; ⊥ ever schedule against the SET reconciler**).

## Traps — each cost a real migration or a refuted claim

1. **Grep ⊥ proves a flag has no reader.** Deployed Edge Functions ∉ git. `list_edge_functions` first. Cost: 0302 (narrowed a flag that gated the then-live writer's sibling; inert by luck).
2. **`items.sku` ≠ the sync key.** Reconciler resolves `integration_sku_map.external_sku` ONLY. Fixing `items.sku` changes nothing. Cost: 0303→0305 (matcha bowl months at −4 while we held 20).
3. **Coverage direction: system→Shopify** (Tom 2026-08-01). ∀ item sold in system ! mapped. Reverse ⊥ holds — Shopify carries retired/merch junk; counting from Shopify side inflated 3 real misses into "62 gaps".
4. **Every `integration_sku_map` query !** `source_channel='shopify' AND approval_status='approved' AND mapping_status='active'` — else fan-out double-counts (items carry lionwheel/GI/inactive rows). Fix = WHERE, ⊥ GROUP BY.
5. **⊥ map 2 items to 1 external_sku** — reconciler would write 2 answers per cycle for the same variant.
6. **Empty/quiet ≠ green.** 4 claims refuted by one query each in one session (audit_runs "never verified" — 83/83 green existed · 2× drift · dup SKUs · shadow-path "maintaining Shopify"). Query before claiming; `cron.job_run_details` "succeeded" = POST fired, ⊥ function succeeded — check the function's own log/`job_runs`.
7. **A crashing job can be load-bearing.** v2's 96 fails/day were the only interlock holding a 2nd unclamped writer in shadow. "Fixing" a red job can arm a hazard — check what its failure gates before repairing. (Now guarded by 0310 tripwire regardless.)

## Canonical queries (copy, ⊥ re-derive)

```sql
-- Health now (opens/auto-resolves exceptions as side effect)
select private_core.run_shopify_sync_health('manual');

-- Last cycle breakdown
with c as (select max(cycle_at) m from private_core.shopify_reconcile_log)
select c.m, l.status, count(*) from private_core.shopify_reconcile_log l, c
where l.cycle_at=c.m group by 1,2;

-- Coverage (THE check; direction system→Shopify)
select i.item_id from private_core.items i
where i.status='ACTIVE' and i.supply_method in ('BOUGHT_FINISHED','MANUFACTURED','REPACK')
  and not exists (select 1 from private_core.integration_sku_map m
    where m.item_id=i.item_id and m.source_channel='shopify'
      and m.approval_status='approved' and m.mapping_status='active');
-- expected: EXCLUDED-NONSTOCK (sentinel) + currently ADD-ORANGE-100G (see OPEN)

-- Item deep-dive before touching any mapping
select l.cycle_at, l.status, l.sku, l.on_hand, l.committed, l.available, l.http_status
from private_core.shopify_reconcile_log l where l.item_id=$1 order by cycle_at desc limit 5;
```

Shopify side: `productVariants(query:"sku:X")` → `inventoryQuantity`, `product{status}`. ACTIVE products only enter the reconciler's cache.

## Monitoring — what watches, what it catches

- cron 26 `*/15`: `run_shopify_sync_health()` (0308) — stale >30m · `skip_no_active_variant` (trap-2 class) · `set_fail*` · **oversell** (`on_hand−committed<0`; clamp hides it from storefront ∴ inbox is the only surface). All dedupe-keyed, auto-resolve when clear.
- Same cron: `run_shopify_second_writer_tripwire()` (0310) — fires on `live_*` rows in `shopify_available_write_attempts` OR handler notes `v2_healthy=true`. If it fires: set `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false` (factory_os_jobs secrets). ⊥ "fix" via `shopify_available_write_paused` — that kills the good reconciler too.
- Blind spot by design: an item with NO mapping row appears in NO log — only the coverage query above sees it. Run it whenever items are added/changed.

## Frozen / needs-Tom

- Env flags `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` (false since 2026-08-01, Tom) + `SHOPIFY_GRAPHQL_SYNC_ENABLED` (still true, inert while sentinel false) + code sentinels — brain `CLAUDE.md` frozen list. ⊥ flip without Tom written approval.
- Deleting deployed `shopify_fg_push` Edge Fn — flag-disabled instead; deletion = Tom call.
- brain `CLAUDE.md` §Source-of-truth still carries "platform wins on disagreement" — stale vs live behavior + Tom 2026-08-01 ruling; Tom-sole-writer ∴ pending his edit.

## OPEN

- **`ADD-ORANGE-100G`**: 29 units anchor-only, **0 ledger movements ever**, no mappings. Twin `ADD-GAR-ORA-DRY` is the live item (35 movements, mapped shopify:`AP-DRI-ORA`, syncing). Stock-truth question, ⊥ mapping: physical count → reversal/re-post onto twin, or retire item. ⊥ map both to one SKU (trap 5).
- ~60 unmapped ACTIVE Shopify variants (stale negatives like `GTMN-PIK-254` −2675) = storefront cleanup for Tom, ⊥ sync gap.

## LEARNED — append-only log (close-session routes here)

> Format: `- YYYY-MM-DD: <one-line fact> (evidence: <query/migration/PR>)`
> Self-compaction: when this section exceeds 30 lines → distill into the sections above, clear the log, stamp "Last distilled" in the header. No approval needed — this file ∉ authority docs.

(empty — created 2026-08-01)
