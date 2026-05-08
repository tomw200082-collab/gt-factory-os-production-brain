# Stage α — Follow-up Live-Push Verification

> Companion to the Stage α SKU mapping cleanup committed at **2026-04-26 09:13:34 UTC**.
> This is a verification protocol, not a new feature. **No code, no schema, no Shopify writes.**

---

## Why this note exists

Stage α corrected 7 mappings in `private_core.integration_sku_map` and the next sync cycle (09:15 UTC) reported `write_status='ok'` for all 7 affected items. However:

- All 7 platform `current_balances.calculated_on_hand` values were `0` at COMMIT time.
- The mapped Shopify variants were already showing inventory `0`.
- A `0 → 0` write is observationally indistinguishable from a no-op, regardless of whether the sync is actually pushing to Shopify or only logging `write_status='ok'`.
- Therefore: **the mapping correction is verified for integrity, but the live push end-to-end is NOT yet verified by evidence.**

This note defines the verification protocol to execute when natural conditions allow real proof. **Do not fabricate movement to satisfy this check.** Wait for a real production event.

---

## What is currently proven (Stage α evidence)

- ✅ `integration_sku_map` row counts and bijection invariants
- ✅ Sync cycle 09:15 UTC: `last_sync_writes_ok=54`, `writes_failed=0`, no `skipped_unmapped`
- ✅ All 7 affected items recorded `write_status='ok'` in `shopify_fg_sync_history`
- ✅ No new `shopify_*` exceptions emitted
- ✅ All 7 target ACTIVE Shopify products read as inventory `0` (matches platform)
- ✅ No item_id, ledger, items.sku, or Shopify variant SKU touched

## What is NOT yet proven

- ❌ That a non-zero platform `current_balances` value is actually being **received by Shopify** as a live inventory update
- ❌ That `write_status='ok'` in history corresponds to a real successful HTTP write, not just a logged result without an actual API call

---

## The 7 items in scope

| item_id | Mapped Shopify SKU | Mapped to Active Product |
|---|---|---|
| `FG-CON-1L` | `GT-JAS-LOW-1L` | CONSCIOUSNESS 1000ml |
| `FG-NM-1L` | `GTCC-NON-SAN-1L` | GT Nonomimi Sangria Cocktail 1000ml |
| `FG-SAN-RED-3850ML` | `GTCC-SAN-RED-3.85L` | Red Sangria 3.85L |
| `FG-SAN-WHI-3850ML` | `GTCC-SAN-WHI-3.85L` | White Sangria 3.85L |
| `FG-MAR-STR-300ML` | `GTEL-MAR-STR-0.3L` | Margarita Strawberry Elita 0.3L |
| `FG-SAN-WHI-750ML` | `GTEL-SAN-WHI-0.75L` | GT Elita White Sangria Cocktail 750ml |
| `FG-SAN-RED-750ML` | `GTEL-SAN-RED-0.75L` | GT Elita Red Sangria Cocktail 750ml |

Any of the 7 will work for verification. The first to receive a natural production event triggers the protocol.

---

## Trigger conditions

Run the protocol when **all** of these are true:

1. A real operational event has produced a non-zero platform stock change for any of the 7 items in scope. Acceptable sources:
   - Production Actual posting (output qty added to ledger)
   - Goods Receipt against PO
   - Inbound stock adjustment via approved form
2. The change is recorded in `private_core.stock_ledger` (so the projection is real, not a manual update).
3. `current_balances.calculated_on_hand` for the item is now `> 0`.

**Do not create fake stock movement just to satisfy this check.** If a month passes with no movement on these items, that is itself a meaningful signal — but the verification simply waits.

---

## Verification protocol — 6 steps

Designate `T` as the moment the trigger condition becomes true. Designate `<ITEM>` as the affected item_id.

### Step 1 — Confirm platform state changed

```sql
SELECT cb.item_id, cb.calculated_on_hand,
       GREATEST(0, FLOOR(cb.calculated_on_hand))::int AS expected_push_qty,
       cb.last_event_at
FROM private_core.current_balances cb
WHERE cb.item_id = '<ITEM>';
```

**Pass criterion:** `calculated_on_hand > 0` and `last_event_at` is recent (≥ T).

Record the value as `EXPECTED_QTY = GREATEST(0, FLOOR(calculated_on_hand))`.

### Step 2 — Wait for the next 15-minute sync cycle

```sql
SELECT last_sync_at, last_successful_sync_at, last_sync_writes_ok, last_sync_writes_failed
FROM private_core.shopify_sync_state;
```

**Pass criterion:** `last_sync_at > T` (cycle has fired since the trigger), and `last_sync_writes_failed = 0` for that cycle.

If the cycle was failed or skipped, troubleshoot the sync runtime (out of scope for this protocol — escalate).

### Step 3 — Verify history row for `<ITEM>`

```sql
SELECT created_at, item_id, write_status, shopify_qty_observed,
       drift_qty, drift_pct
FROM private_core.shopify_fg_sync_history
WHERE item_id = '<ITEM>'
  AND created_at > '<T>'::timestamptz
ORDER BY created_at DESC
LIMIT 5;
```

**Pass criterion:** at least one row with `write_status='ok'` and `created_at > T`.

If `write_status='skipped_unmapped'`: mapping is broken (must not happen post-α — escalate).
If `write_status='network_fail'` or other: sync runtime issue — re-run after one more cycle, then escalate.

### Step 4 — Read Shopify live inventory

Mapped Shopify SKU is one of the 7 listed in the table above. Look it up via the authenticated admin session (no Shopify writes — read only):

```javascript
// Run inside admin.shopify.com session via browser_evaluate or equivalent:
fetch('/store/greenteaeveryday/products.json?limit=250', { credentials: 'include' })
  .then(r => r.json())
  .then(j => j.products.flatMap(p => p.variants
    .filter(v => v.sku === '<MAPPED_SHOPIFY_SKU>')
    .map(v => ({
      product: p.title, status: p.status,
      sku: v.sku, inv: v.inventory_quantity, updated_at: v.updated_at
    }))));
```

Alternative: fetch via the admin REST endpoint by inventory_item_id from `integration_sku_map.notes` if the GraphQL ID is known.

**Record the live inventory value** for the ACTIVE product (ignore archived duplicates).

### Step 5 — Compare

| Variable | Source | Required relationship |
|---|---|---|
| `EXPECTED_QTY` | from Step 1 | platform side |
| `SHOPIFY_INV` | from Step 4 | Shopify side |
| | | `SHOPIFY_INV == EXPECTED_QTY` |

**Pass criterion:** equal. Off-by-one or fractional diffs imply a rounding bug; report and stop.

If `SHOPIFY_INV != EXPECTED_QTY`:
- Confirm Step 4 read was AFTER the cycle in Step 2 finished
- Allow up to 5 minutes for Shopify-side propagation; re-read Step 4 once
- If still mismatched after one re-read: **live push is NOT proven** — escalate. Do not record verification as passing.

### Step 6 — Record the proof

If all five prior steps passed, append a single line to this note under the **Verification log** section below:

```
- 2026-MM-DD HH:MM UTC | <ITEM> | platform=<EXPECTED_QTY> shopify=<SHOPIFY_INV> | ok | sync_at=<last_sync_at>
```

After the first ok line, the claim **"live inventory push proven after Stage α"** is permitted.

Do not delete or rewrite this note after that point. It is the audit trail.

---

## Hard constraints

- Do not write to `stock_ledger` manually to trigger the protocol.
- Do not touch any inventory in Shopify manually.
- Do not modify `integration_sku_map` for the 7 items (Stage α is closed).
- Do not change `item_id` or `items.sku` to "force" a refresh.
- Do not invoke the cron job manually outside its schedule unless a separate troubleshooting task is approved.

If proof requires breaking any of the above, the proof itself is corrupted. Better to wait.

---

## Verification log

(Populated upon first successful run of the protocol.)

```
<empty>
```

---

## Cross-references

- Stage α plan & SQL: `scripts/sku-audit/stage-alpha-mappings.sql` (committed 2026-04-26 09:13:34 UTC)
- Audit data: `scripts/sku-audit/audit_report.json` and `audit_report.md`
- Source-of-truth: `private_core.integration_sku_map` (rows with `approval_status='approved'` and `notes` containing `2026-04-26 audit:`)
