# GT Factory OS — DB Operations Log

> **Append-only log** of manually-executed DB operations on production / staging / dev environments.
> Most recent on top. Never edit prior entries; corrections go in a new entry referencing the prior one.
>
> **Author:** `backend-db-executor` (or Tom for direct ops; in transitional period also legacy `executor-w1` until Wave 6 deprecation).
> **Cross-reference:** for migration semantics see `docs/contracts/SCHEMA_GUIDANCE.md`. For CURRENT_STATE gate impact, see `CURRENT_STATE.md` §Gate-by-gate runtime status.
>
> **Origin:** entries below 2026-05-09 were migrated verbatim from `CURRENT_STATE.md` §"DB ops log — manually-executed operations" during Phase 8 Run F Wave 4 Hole 2 cleanup (2026-05-09). The original section in CURRENT_STATE.md was removed; pre-migration text preserved at `archive/historical-state-snapshots/2026-05-08-phase8-ai-brain-rewrite-snapshot.md`.

---

## Schema (per-entry)

Each entry uses this skeleton:

```
### YYYY-MM-DD — <slug> [APPLIED | PENDING | ROLLED_BACK]
- **Migration / op:** <file path or SQL summary>
- **Environment:** prod | staging | dev
- **Executed by:** <Tom (admin) | backend-db-executor commit hash | executor-w1 commit hash>
- **Method:** <psql / Node pg client / Supabase SQL editor / portal-driven>
- **Verification:** <pgTAP / parity / smoke / manual>
- **Rollback:** <path or "none — additive">
- **Reference:** <issue / PR / commit / runbook>
- **Schema semantics changed:** YES | NO
- **RLS changed:** YES | NO
- **Data changed:** YES | NO
- **PO corridor touched:** YES | NO
```

---

## Entries (most recent on top)

### 2026-05-07 — 0152_shopify_fg_sync_history_disabled_status — APPLIED
- **Migration / op:** `gt-factory-os/db/migrations/0152_shopify_fg_sync_history_disabled_status.sql`
- **Environment:** prod
- **Applied at:** 2026-05-07 ~11:52Z via `gt-factory-os/scripts/apply_0152.mjs` (operational tooling, same pattern as `apply_0150.mjs` 2026-05-02)
- **What:** additive CHECK expansion on `private_core.shopify_fg_sync_history.write_status` to admit `disabled_pending_v2` (Phase 0 kill-switch audit row). Original 5 values (`ok`, `429`, `auth_fail`, `network_fail`, `skipped_unmapped`) preserved verbatim.
- **Before:** `CHECK ((write_status = ANY (ARRAY['ok','429','auth_fail','network_fail','skipped_unmapped'])))`
- **After:** `CHECK ((write_status = ANY (ARRAY['ok','429','auth_fail','network_fail','skipped_unmapped','disabled_pending_v2'])))`
- **Verification:** `db/tests/0152_shopify_fg_sync_history_disabled_status.test.sql` written (4 assertions). NOT YET RUN by backend-db; runtime correctness verified empirically by Phase 0 smoke (110 `disabled_pending_v2` rows inserted successfully + `pg_get_constraintdef` round-trip).
- **Rollback:** none — additive
- **Reference:** Shopify External Boundary v2 Phase 0 corridor; PRs #6/#7/#8.
- **backend-db review status:** REQUIRED. The migration was applied as a Phase-0 unblocking exception (integration corridor needed the new status value to write its kill-switch audit row). Going forward, all schema deltas are backend-db-spec-only per Tom 2026-05-07 governance lock.
- **Schema semantics changed:** NO (additive only)
- **RLS changed:** NO
- **Data changed:** NO
- **PO corridor touched:** NO

---

### 2026-04-30 — Day-1 prep stale-exception bulk-close — PENDING (Tom execution)
- **Migration / op:** `UPDATE` on `private_core.exceptions`
- **Environment:** prod
- **Scope:** `category='lionwheel_unknown_sku' AND status='open' AND created_at < now() - interval '14 days'`
- **Expected rows affected:** ~41 (per CURRENT_STATE.md figure as of 2026-04-29)
- **Executed by:** Tom (admin) — pending execution
- **Why now:** companion to design 2026-04-30 §A.3 #2 silent-drop change (commit `1202d5c`). The historical 41 stale rows predate the silent-drop change; bulk-closing them clears the inbox so Day-1 starts with a clean exceptions tab.
- **Method (preferred — portal):** open `https://gt-factory-os-portal.vercel.app/exceptions?view=exceptions&category=lionwheel_unknown_sku`, multi-select all rows older than 14 days, click "Resolve" with reason note "Stale historical lionwheel_unknown_sku predating §A.3 #2 silent-drop change. Bulk-closed during Day-1 prep."
- **Method (fallback — direct SQL via psql or Supabase SQL editor):**
  ```sql
  UPDATE private_core.exceptions
     SET status = 'resolved',
         resolved_at = now(),
         resolved_by_snapshot = 'admin (Day-1 prep bulk-close per design §A.3 #3)',
         resolution_notes = 'Stale lionwheel_unknown_sku exception predating §A.3 #2 silent-drop change. Closed in bulk on Day-1 prep.'
   WHERE category = 'lionwheel_unknown_sku'
     AND status = 'open'
     AND created_at < now() - interval '14 days';
  ```
- **Preflight verification:**
  ```sql
  SELECT count(*) FROM private_core.exceptions
   WHERE category='lionwheel_unknown_sku' AND status='open' AND created_at < now() - interval '14 days';
  ```
  Expected: ~41 before; 0 after.
- **Post verification:**
  ```sql
  SELECT count(*) FROM private_core.exceptions
   WHERE category='lionwheel_unknown_sku' AND status='open';
  ```
  Expected: 0 (or near-0 if any new exceptions arrived between Chunk 2 deploy and now — but per Chunk 2 silent-drop, no new ones should appear).
- **Rollback:** reversible via `UPDATE … SET status='open' WHERE exception_id IN (…specific list…)`.
- **Reference:** design 2026-04-30 §A.3 #3.
- **Schema semantics changed:** NO
- **RLS changed:** NO
- **Data changed:** YES (status field on ~41 rows)
- **PO corridor touched:** NO

---

### 2026-04-24 — 0082_gr_reversal_po_decrement_trigger — APPLIED (pre-existing, confirmed)
- **Migration / op:** `db/migrations/0082_gr_reversal_po_decrement_trigger.sql`
- **Environment:** prod
- **Status:** Already applied prior to this session. Confirmed via `information_schema.triggers` query: `trg_stock_ledger_gr_reversal_po_decrement` exists on `private_core.stock_ledger`. UNRESOLVED-GP-1 CLOSED.
- **Verification:** trigger presence confirmed via `information_schema.triggers`.
- **Rollback:** would require dropping the trigger; not planned.
- **Reference:** UNRESOLVED-GP-1 (CURRENT_STATE.md history); GR reversal → PO `received_qty` decrement path.
- **Schema semantics changed:** YES — new trigger on stock_ledger for GR_REVERSAL events; decrements `purchase_order_lines.received_qty`
- **RLS changed:** NO
- **Data changed:** NO
- **PO corridor touched:** YES

---

### 2026-04-24 — 0081_fk_hygiene_indexes — APPLIED
- **Migration / op:** `db/migrations/0081_fk_hygiene_indexes.sql`
- **Environment:** production Supabase — project ref `rvadsozabmxkkrktwgnv` (eu-central-1)
- **Connection:** direct host, SSL, autocommit (no transaction wrapper)
- **Executed by:** Claude Sonnet 4.6 / Tom session 2026-04-24
- **Method:** Node.js `pg` client in autocommit mode (equivalent to `psql -v ON_ERROR_STOP=1 -f`; psql not in bash PATH on this machine)
- **Preflight:** 0 invalid indexes found — clean
- **Execution:** 9/9 statements OK, no errors
- **Verification (pg_index):** 9 rows returned; `indisready=true`, `indisvalid=true` for all
- **Indexes created:**
  - `idx_stock_ledger_reported_by_user` (partial, stock_ledger)
  - `idx_stock_ledger_posted_by_user` (partial, stock_ledger)
  - `idx_exceptions_acknowledged_by` (partial, exceptions)
  - `idx_exceptions_resolved_by` (partial, exceptions)
  - `idx_exceptions_related_job_run` (partial, exceptions)
  - `idx_integration_sku_map_item_id` (full, integration_sku_map)
  - `idx_planning_runs_forecast_version` (partial, planning_runs)
  - `idx_planning_runs_orders_snapshot_run` (partial, planning_runs)
  - `idx_planning_runs_supersedes` (partial, planning_runs)
- **Rollback:** none planned — pure performance hygiene.
- **Reference:** FK hygiene tranche 2026-04-24.
- **Schema semantics changed:** NO
- **RLS changed:** NO
- **Data changed:** NO
- **PO corridor touched:** NO
