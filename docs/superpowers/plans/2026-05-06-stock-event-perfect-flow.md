# Stock Event Perfect Flow Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After today's physical count, every stock-affecting event (LionWheel shipments, Goods Receipts, Waste/Adjustments, Counts, Production Actuals) flows through gt-factory-os correctly and continuously, with daily verification that proves the system is internally consistent. Concretely: raise `stock-event-accuracy-audit` top-line from 32.9% to ≥99%, fold mass-balance into the audit as a 5th layer, and cut over operator workflows + Shopify writes from `daily-inventory-agent`/Excel to gt-factory-os as the single source of truth.

**Today's count is the cutover moment.** Every event before today's count is forgiven (drift accepted). Every event after today must be correct or the audit catches it within 24h. The plan is phased to make the count itself a clean baseline (Phase 0), get LionWheel right (Phase 1), expand to all event classes (Phase 2), then decommission the legacy Excel/agent path (Phase 3).

**Architecture:** Move the LionWheel→ledger trigger from "task terminal" to "pickup_at passed". Enrich each mirror task at pickup time. Post `LIONWHEEL_PICK` movements on first observation, `LIONWHEEL_UNPICK` compensating movements on later cancellation/un-pick, and `LIONWHEEL_PICK_ADJUSTMENT` deltas when picked qty diverges from ordered qty on later enrichment. Govern unmapped/non-stock/legacy-bundle SKUs through explicit `mapping_status` enum so missing master data degrades gracefully into a visible exception rather than chain failure. Keep Shopify writes off until the entire pipeline is shadow-validated and `daily-inventory-agent` is read-only on FG.

**Tech Stack:** Postgres 17 (Supabase) · Node 20 + Fastify + Kysely (gt-factory-os api) · pgTAP for DB-level invariants · node:test for handlers · Python 3.13 for the audit + cleanup scripts · Windows local dev shell.

**Tom-locked decisions (2026-05-06, see Q1–Q6 acceptance reply):**
- Q1 — pickup_at trigger with append-only reversal semantics (no UPDATE/DELETE on existing ledger rows).
- Q2 — `mapping_status` enum on `integration_sku_map`; `is_stock_managed` only for items that should never affect stock; missing internal item must skip + emit a visible exception, never crash.
- Q3 — `internal_units_per_shopify_unit numeric default 1.0` per mapping; legacy bundle SKUs get `mapping_status='excluded_legacy_bundle'`, never throw.
- Q4 — Hard delete strictly limited to 9 `TEST-LW-*` ledger rows + 5 negative-balance entries, with mandatory dry-run + snapshot + maintenance log.
- Q5 — 30-day backfill via admin CLI, idempotent on `source_event_transition_id`, no Shopify writes during backfill.
- Q6 — `ENABLE_SHOPIFY_FG_WRITE` feature flag + active-writer mutex; Factory OS becomes the **only** Shopify FG writer; `daily-inventory-agent` FG writes get stripped after stable cutover.

**Acceptance tests (Tom-locked, must all be green before phase sign-off):**

*Phase 1 — LionWheel chain:*
1. pickup_at posts exactly once.
2. Duplicate pickup does not double-decrement.
3. Not-picked-after-pickup creates a compensating increment.
4. Missing internal item skips posting but creates a visible data-quality exception.
5. True non-stock-managed item skips silently with no exception.
6. Excluded legacy Shopify bundle does not enter FG write scope.
7. 6-pack/simple pack conversion decrements the correct internal units.
8. TEST-LW dry-run refuses to proceed if counts differ from expected.
9. 30-day backfill emits zero Shopify writes.
10. `ENABLE_SHOPIFY_FG_WRITE=false` blocks all outbound FG writes.
11. Factory OS cannot write Shopify FG while another FG writer is active.

*Phase 0 — Count cutover (today):*
12. After count, every counted item has exactly one new `balance_anchors_current` row whose `anchor_qty` equals the count and `anchor_at = cutover_at`; prior anchors are preserved in `balance_anchors_history`.
13. `count_freezes` blocks every other stock-affecting form for the duration of the count, with no half-count drift events.

*Phase 2 — Other event classes + mass-balance:*
14. Goods Receipt via portal posts a `GR_POSTED` row with PO line linkage and increments `current_balances` synchronously.
15. GR for a PO-less receipt also posts correctly (PO link is null, source_event_id deterministic).
16. GR reversal posts a `GR_REVERSAL` row; PO `received_qty` decrements correctly.
17. Waste posted by operator below threshold auto-posts a `WASTE_POSTED` row.
18. Waste above threshold creates a pending `form_submission`; only an admin's approval posts the row.
19. WASTE_REVERSAL is admin-gated; reverses balance exactly.
20. Recurring monthly count via the Physical Count form produces deterministic anchor history rows.
21. Bulk-count importer accepts an Excel sheet without dropping items and rejects malformed rows with named errors.
22. Production Actual posts `PRODUCTION_OUTPUT`, `PRODUCTION_SCRAP`, and PRODUCTION_CONSUMPTION rows that sum correctly per the pinned two-head BOM.
23. Production Actual on a `BOUGHT_FINISHED` item refuses with a named error (no BOM to consume).
24. Production Actual reversal posts the three matching `*_REVERSAL` rows together as a transaction.
25. Cost rollup matches manual reconciliation on a known fixture (production_actual + GR + waste).
26. **Mass-balance:** for every item over a 7-day window, `opening_anchor + Σ(GR) + Σ(PROD_OUT) − Σ(WASTE) − Σ(FG_OUT_PICK / LIONWHEEL_PICK) − Σ(PROD_CONSUMED) + Σ(COUNT_ADJ) = current_balances.calculated_on_hand` within the locked tolerance (0.5 abs OR 1% rel).

*Phase 3 — Decommission:*
27. With ENABLE_SHOPIFY_FG_WRITE=true and the agent's FG-write capability removed, gt-factory-os is the only writer; daily-inventory-agent FG-write code paths are deleted, not just disabled.
28. Audit cron (Railway scheduled) runs nightly and writes one verdict row per run; verdict ≠ PASS triggers an email/notification.

**Plan structure (16 chunks across 3 phases, each chunk independently reviewable + executable):**

| Phase | Chunk | Workstream | Outcome | Acceptance tests covered |
|---|---|---|---|---|
| **0 — Today** | **0** | Count cutover | Today's physical count creates clean balance_anchors for FG+RM, Shopify reset to count truth, cutover_at marker recorded | 12 (count produces anchors), 13 (no mid-count drift) |
| **1 — LionWheel chain (3-7 days)** | 1 | Foundation schema | New movement_types, mapping_status enum, conversion column, transition counter, system_locks | (foundation only) |
| | 2 | Mirror enrichment | pickup_at populated on every task; lw_qty_picked enriched when LW exposes it | — |
| | 3 | Chain posting + reversal | PICK / UNPICK / PICK_ADJUSTMENT wired; fg_out_bridge_enabled lifecycle | 1, 2, 3 |
| | 4 | Master-data governance | mapping_status workflow + missing-item exceptions | 4, 5 |
| | 5 | Shopify map cleanup | 55 stale → inactive; 35 ambiguous → resolved or excluded_legacy_bundle | 6 |
| | 6 | TEST-LW hard delete | 9 ledger rows + 5 negative-balance fixtures, dry-run-guarded | 8 |
| | 7 | 30-day backfill CLI | Admin-only, idempotent on transition_id, no Shopify writes | 9 |
| | 8 | Shopify FG cutover | ENABLE_SHOPIFY_FG_WRITE flag + active-writer mutex + shadow + set-from-projection | 6, 10, 11 |
| | 9 | Phase 1 sign-off | Audit ≥99%, all AT.1-11 green, CURRENT_STATE update | re-verifies 1-11 |
| **2 — All events (1-2 weeks)** | 10 | GR continuous chain | RM + FG GR via portal → ledger; PO matching; supplier dim integration; mass-balance contribution | new AT.14-16 |
| | 11 | Waste / Adjustment continuous chain | Operator portal flow; large-positive approval workflow; reversal pairs | new AT.17-19 |
| | 12 | Physical Count ongoing workflow | Recurring full + spot counts; bulk-import path; anchor history integrity | new AT.20-21 |
| | 13 | Production Actual continuous chain | Two-head BOM consumption verified daily; output/scrap/RM all post correctly | new AT.22-25 |
| | 14 | Mass-balance audit layer 5 | `opening + GR + PROD_OUT − WASTE − FG_OUT − PROD_CONSUMED + COUNT_ADJ = current` per item | new AT.26 |
| | 15 | Phase 2 sign-off | Audit ≥99% across all 5 layers; daily cron green for 7 consecutive days | re-verifies 1-26 |
| **3 — Decommission (1 month)** | 16 | Excel→read-only + daily-inventory-agent strip-down | gt-factory-os single source; Excel becomes nightly export only; agent FG-write removed | new AT.27-28 |

**Phasing — explicit timing:**
```
Phase 0 (TODAY, 4-8 hours):  freeze → count → anchors → Shopify set → cutover marker
Phase 1 (next 3-7 days):     LionWheel chain green; daily audit cron live
Phase 2 (following 1-2 wks): GR/Waste/Count/Production all continuous; mass-balance verified
Phase 3 (within 1 month):    Excel read-only; daily-inventory-agent FG capability removed
```

**Out of scope for this plan (deliberate):** Forecast freshness audit, Green Invoice price ingest accuracy, customer pricing, FEFO/expiry, multi-location/bin tracking. Each is its own audit + plan. Boundaries visible in the *Audit scope vs blueprint* table the audit prints every run.

**Worktree:** This plan was authored without a worktree. Implementation should be done in a dedicated worktree per superpowers:using-git-worktrees:
```
git -C C:/Users/tomw2/Projects/gt-factory-os worktree add ../gt-factory-os-perfect-flow stock-event-perfect-flow
```

**Repo paths used in this plan:**
- `gt-factory-os/db/migrations/` — DDL, next available slot is `0146`
- `gt-factory-os/db/tests/` — pgTAP files
- `gt-factory-os/api/src/integrations/lionwheel/` — chain (`reconciliation.ts`, `poller.ts`, `schemas.ts`, `sku_resolver.ts`)
- `gt-factory-os/api/test/` — node:test
- `gt-factory-os/scripts/` — admin CLI scripts
- `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/` — audit skill (already built; will be re-run as final gate)

---

## Chunk 0: Count Cutover — TODAY

**Context (must be read before dispatching the implementer):** Tom is conducting a physical count today. This count creates the clean baseline anchors from which gt-factory-os will operate going forward. Any in-flight stock event mid-count corrupts the baseline. Defaults locked in this chunk (override at task 0.1 review if Tom changes them):

- **Count input method:** Tom counts in Excel (familiar tool); a small importer reads the Excel and submits one Physical Count `form_submission` per item via the API. Reason: bulk entry of 60+ FG + 145 RM via the per-item portal form is operationally hostile; Excel is what Tom already uses for counts. (Default for Q-A1.)
- **Count scope:** FG + RM (not components). Reason: components are nearly static; FG drives Shopify; RM drives purchase recommendations. (Default for Q-A2.)
- **Pre-count freeze:** Yes — system-wide `count_freezes` row before count entry begins, lifted only after every line is anchored. Reason: blocks any concurrent waste/GR/production form from posting against an in-flight count. (Default for Q-A3.)
- **Shopify reset:** One-time set-from-count write of every counted FG SKU's `current_balances.calculated_on_hand × internal_units_per_shopify_unit` to Shopify on-hand. Read-only ledger does NOT change; just brings Shopify back to truth. Gated behind a per-run flag, **not** the still-disabled `ENABLE_SHOPIFY_FG_WRITE` (this is a one-shot, not the continuous writer of chunk 8).

**Outcome of Chunk 0:** every counted FG + RM item has a fresh row in `balance_anchors_current` with `anchor_at = <cutover_at>` and `anchor_source = 'physical_count_2026-05-06'`. `current_balances.calculated_on_hand` matches the count (rebuild_verifier=0 against the new anchors). Shopify on-hand for every mapped FG SKU equals the count after conversion. A `private_core.system_state` row records `cutover_at` for downstream reference.

### Task 0.1 — Pre-count freeze + system_state migration

**Files:**
- Create: `gt-factory-os/db/migrations/0149_phase0_cutover.sql`
- Create: `gt-factory-os/db/tests/0149_phase0_cutover.test.sql`

- [ ] **Step 1: Write failing pgTAP test**

```sql
BEGIN;
SELECT plan(8);

SELECT has_table('private_core', 'system_state');
SELECT has_column('private_core', 'system_state', 'key');
SELECT has_column('private_core', 'system_state', 'value_jsonb');
SELECT has_column('private_core', 'system_state', 'set_at');
SELECT has_column('private_core', 'system_state', 'set_by_user_id');

-- system_state.key is unique
SELECT col_is_pk('private_core', 'system_state', ARRAY['key']);

-- A maintenance_log table exists (chunk 6 prerequisite landed earlier OR here)
SELECT has_table('private_core', 'maintenance_log');
SELECT has_column('private_core', 'maintenance_log', 'action');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run, verify failure**

```bash
psql "$DATABASE_URL_POOLED" -f gt-factory-os/db/tests/0149_phase0_cutover.test.sql
```

Expected: `has_table('private_core', 'system_state')` fails.

- [ ] **Step 3: Write the migration**

```sql
BEGIN;

-- Phase 0 — Count cutover prerequisites
--   • system_state: durable record of cutover_at + cutover scope
--   • maintenance_log: audit trail for one-shot data operations
--     (count import, TEST-LW cleanup, Shopify-reset, etc.)

CREATE TABLE IF NOT EXISTS private_core.system_state (
  key text PRIMARY KEY,
  value_jsonb jsonb NOT NULL,
  set_at timestamptz NOT NULL DEFAULT now(),
  set_by_user_id uuid REFERENCES private_core.app_users(user_id)
);

COMMENT ON TABLE private_core.system_state IS
  'Durable system-wide singleton state. Used for cutover_at, feature gates, and any other one-row-many-keys metadata that must survive deploys.';

CREATE TABLE IF NOT EXISTS private_core.maintenance_log (
  log_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  action text NOT NULL,
  performed_by_user_id uuid REFERENCES private_core.app_users(user_id),
  performed_at timestamptz NOT NULL DEFAULT now(),
  details jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS maintenance_log_action_idx
  ON private_core.maintenance_log (action, performed_at DESC);

COMMENT ON TABLE private_core.maintenance_log IS
  'Append-only audit trail for one-shot data operations: count cutover, synthetic-data cleanup, schema repairs. Never UPDATE/DELETE.';

COMMIT;
```

- [ ] **Step 4: Apply, re-run test, verify pass**

```bash
psql "$DATABASE_URL_POOLED" -f gt-factory-os/db/migrations/0149_phase0_cutover.sql
psql "$DATABASE_URL_POOLED" -f gt-factory-os/db/tests/0149_phase0_cutover.test.sql
```

Expected: 8/8 PASS.

- [ ] **Step 5: Insert system-wide count_freeze row**

This is a manual operator action **performed at the moment Tom is ready to start counting**. The implementer creates a small CLI script `gt-factory-os/scripts/start_count_cutover.mjs`:

```javascript
// Inserts a private_core.count_freezes row spanning ALL items, all sites,
// covering the count window. Tom calls release_count_cutover.mjs once
// the import completes.
import 'dotenv/config';
import pg from 'pg';
const { Pool } = pg;
const pool = new Pool({ connectionString: process.env.DATABASE_URL_POOLED, ssl: { rejectUnauthorized: false } });

const userId = process.env.CUTOVER_OPERATOR_USER_ID;
if (!userId) throw new Error('CUTOVER_OPERATOR_USER_ID env var required');

const { rows: [freeze] } = await pool.query(`
  INSERT INTO private_core.count_freezes (
    freeze_kind, scope, opened_by_user_id, opened_at, expected_close_within
  ) VALUES (
    'system_wide_count_cutover', 'all_items', $1, now(), interval '12 hours'
  ) RETURNING freeze_id, opened_at
`, [userId]);
console.log(JSON.stringify({ freeze_id: freeze.freeze_id, opened_at: freeze.opened_at }, null, 2));

await pool.query(`
  INSERT INTO private_core.maintenance_log (action, performed_by_user_id, details)
  VALUES ('count_cutover_freeze_opened', $1, $2)
`, [userId, JSON.stringify({ freeze_id: freeze.freeze_id })]);

await pool.end();
```

(If `count_freezes.scope` is not nullable or has a different column shape, the implementer reads `private_core.count_freezes` schema first and adapts. The intent is system-wide, not per-item.)

- [ ] **Step 6: Commit**

```bash
git add gt-factory-os/db/migrations/0149_phase0_cutover.sql \
        gt-factory-os/db/tests/0149_phase0_cutover.test.sql \
        gt-factory-os/scripts/start_count_cutover.mjs
git commit -m "phase0(cutover): system_state + maintenance_log + freeze script

Establishes the durable record of cutover_at (chunk 9 references it as
the line between forgiven historical drift and enforced forward
correctness) and an append-only audit trail for one-shot data
operations.

Plan chunk 0 task 0.1."
```

### Task 0.2 — Excel-to-PhysicalCount importer

**Files:**
- Create: `gt-factory-os/scripts/import_count_from_excel.py`
- Create: `gt-factory-os/api/test/physical_count_bulk_import.test.ts`

The importer reads an Excel file with columns `[item_id, count_qty, notes]`. For each row it submits a `POST /api/v1/mutations/physical-counts` call (same handler the portal uses), under one shared `idempotency_key` prefix `count_cutover_2026-05-06:<item_id>`.

- [ ] **Step 1: Write failing test (covers AT.21)**

```typescript
import { test } from 'node:test';
import assert from 'node:assert/strict';

test('AT.21: bulk-count importer rejects malformed rows with named errors', async () => {
  // Excel rows: [{item_id: 'FG-CAL-1L', count_qty: 12}, {item_id: '', count_qty: 5}, {item_id: 'BAD-ITEM', count_qty: -1}]
  // Expect: row 1 imported; row 2 rejected with reason='missing_item_id'; row 3 rejected with reason='non_positive_qty'
});

test('AT.21: bulk-count importer is idempotent on re-run', async () => {
  // Run twice with the same input; expect exactly one form_submission per item.
});

test('AT.12: every counted item has exactly one new balance_anchors_current row', async () => {
  // Run import; query balance_anchors_current for each item_id; expect anchor_qty=count_qty and anchor_at near cutover_at.
});
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement the importer**

```python
# gt-factory-os/scripts/import_count_from_excel.py
"""
Excel → Physical Count importer for the count cutover.

Inputs:
  --excel <path>       Path to .xlsx with columns: item_id, count_qty, notes (optional)
  --site-id <id>       e.g. 'GT-MAIN'
  --user-id <uuid>     Operator submitting the count
  --dry-run            Validate + summarize, do not POST

Behavior:
  - Validates every row before any POST. If any row is malformed, prints all
    errors and refuses to proceed (no half-imports).
  - For each valid row: POST /api/v1/mutations/physical-counts with
    idempotency_key='count_cutover_2026-05-06:<item_id>'.
  - Logs every result to maintenance_log (action='count_cutover_row',
    details={item_id, count_qty, submission_id, status}).
  - Final summary: imported, rejected, anchored_count.
"""
# … implementation
```

The Python script uses `openpyxl` for the Excel read and `requests` for the POST. Auth via `X-Test-Session` shim or a Supabase JWT.

- [ ] **Step 4: Tom-driven test run on real count data**

Tom places the count Excel at `PRODUCTION/.cutover/2026-05-06_count.xlsx`. Implementer runs:

```bash
python gt-factory-os/scripts/import_count_from_excel.py \
  --excel "PRODUCTION/.cutover/2026-05-06_count.xlsx" \
  --site-id GT-MAIN --user-id <Tom's app_users uuid> --dry-run
```

Expected: summary shows `valid_rows=N, malformed=0` (or, if malformed, named errors). If malformed, Tom edits the Excel and re-runs.

- [ ] **Step 5: Apply for real**

```bash
python gt-factory-os/scripts/import_count_from_excel.py \
  --excel "PRODUCTION/.cutover/2026-05-06_count.xlsx" \
  --site-id GT-MAIN --user-id <Tom's app_users uuid>
```

Expected: every row produces a `form_submissions` row with `status='posted'`, a matching `stock_ledger COUNT_ADJUST` row, and a new `balance_anchors_current` row.

- [ ] **Step 6: Commit**

### Task 0.3 — Anchor & projection verification

**Files:**
- Create: `gt-factory-os/scripts/verify_count_cutover.py`

After import, the verifier queries:

```sql
SELECT count(*)::int AS items_with_anchor
FROM private_core.balance_anchors_current
WHERE anchor_source = 'physical_count_2026-05-06';

SELECT bool_and(
  abs(cb.calculated_on_hand - bac.anchor_qty) < 0.001
)::boolean AS projection_matches_anchor
FROM private_core.current_balances cb
JOIN private_core.balance_anchors_current bac USING (site_id, item_type, item_id, batch_id_or_empty)
WHERE bac.anchor_source = 'physical_count_2026-05-06';

SELECT private_core.rebuild_verifier();  -- expect 0
```

- [ ] **Step 1-3: Write + run + verify**

Expected: items_with_anchor matches the imported count, projection_matches_anchor=true, rebuild_verifier=0.

If any check fails, **STOP** — do not proceed to Shopify reset. Investigate before continuing.

### Task 0.4 — One-shot Shopify set-from-count

**Files:**
- Create: `gt-factory-os/scripts/shopify_reset_from_count.mjs`

Reads `current_balances` for every FG with `mapping_status='active'` and live Shopify variant. Writes Shopify on-hand = `calculated_on_hand × internal_units_per_shopify_unit` (rounded to int).

**This script bypasses the ENABLE_SHOPIFY_FG_WRITE gate by design** — it's a one-shot reset, not the continuous writer. The implementer marks this clearly in code and in `maintenance_log`.

```javascript
// gt-factory-os/scripts/shopify_reset_from_count.mjs
//
// One-shot: writes Shopify on-hand FROM the count anchors created by
// task 0.2. Does NOT use the chunk-8 continuous writer. Does NOT take
// the system_locks mutex (no other writer should be active during
// cutover; chunk 8 mutex covers ongoing operations).
//
// Refuses to run unless:
//   1. balance_anchors_current has rows with anchor_source='physical_count_2026-05-06'
//   2. system_state.key='cutover_at' is NOT YET set (this is the moment we set it)
//   3. system_locks has no active 'shopify_fg_writer' row
//
// On success:
//   - Sets system_state[cutover_at] = now()
//   - Logs to maintenance_log
//   - Releases the count_freezes row (transitions freeze status to 'consumed_cutover')
```

- [ ] **Step 1: Dry-run**

Expected: prints a table of `(item_id, name, count_qty, conversion, target_shopify_qty, current_shopify_qty, delta)` for every mapped FG.

- [ ] **Step 2: Tom reviews the dry-run output**. Critical: every delta should be EXPLAINABLE — anything wildly off (e.g., conversion of 100 vs expected 6) flags a Shopify mapping bug. Tom fixes mapping if needed; re-runs dry-run; only proceeds when output looks right.

- [ ] **Step 3: Apply for real**

- [ ] **Step 4: Confirm**

Re-run the audit:

```bash
python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" --days 1 --quiet
```

Expected: layer 4 (shopify_parity) reports ≥99% match (≤0.5 unit divergence per mapped item). If not, the Shopify reset didn't take effect on some SKUs — investigate before lifting freeze.

### Task 0.5 — Lift freeze + close out

- [ ] **Step 1: Mark cutover complete**

```javascript
// gt-factory-os/scripts/release_count_cutover.mjs
import 'dotenv/config';
import pg from 'pg';
const { Pool } = pg;
const pool = new Pool({ connectionString: process.env.DATABASE_URL_POOLED, ssl: { rejectUnauthorized: false } });

await pool.query('BEGIN');
await pool.query(`
  INSERT INTO private_core.system_state (key, value_jsonb)
  VALUES ('cutover_at', jsonb_build_object('timestamp', now(), 'phase', 0, 'reason', 'physical_count_2026-05-06'))
  ON CONFLICT (key) DO UPDATE SET value_jsonb = excluded.value_jsonb, set_at = now()
`);
await pool.query(`
  UPDATE private_core.count_freezes
  SET freeze_status = 'consumed_cutover', closed_at = now()
  WHERE freeze_kind = 'system_wide_count_cutover' AND closed_at IS NULL
`);
await pool.query(`
  INSERT INTO private_core.maintenance_log (action, details)
  VALUES ('count_cutover_complete', $1)
`, [JSON.stringify({ counted_items: '<from task 0.3>', shopify_reset_at: '<from task 0.4>' })]);
await pool.query('COMMIT');
console.log('cutover complete');
await pool.end();
```

- [ ] **Step 2: Final audit run**

```bash
python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" --days 1
```

Expected: top-line ≥95%; layer 4 (shopify_parity) at ≥99%; data quality section now shows `cutover_at = <timestamp>` (the audit will need a small update to read this — see chunk 14).

- [ ] **Step 3: Commit + tag**

```bash
git tag -a phase0-cutover -m "Count cutover complete 2026-05-06; gt-factory-os is now stock-truth"
git push --tags
```

**Phase 0 sign-off criteria (block Phase 1 from starting until all checked):**
- [ ] Every counted item has a `balance_anchors_current` row with `anchor_source='physical_count_2026-05-06'`.
- [ ] `rebuild_verifier()` returns 0 against the new anchors.
- [ ] Shopify on-hand for every mapped FG equals (count × conversion) within 0.5 units.
- [ ] `system_state[cutover_at]` is set.
- [ ] `count_freezes` row is `consumed_cutover` with no half-count drift events.
- [ ] AT.12 + AT.13 verified by automated tests.

---

## Chunk 1: Foundation Schema

**Outcome:** All structural prerequisites for the new chain logic exist in the live DB before any handler code touches them. Pure additive — no existing column types or rows change.

### Task 1.1 — Migration `0146_stock_event_perfect_flow_foundation.sql`

**Files:**
- Create: `gt-factory-os/db/migrations/0146_stock_event_perfect_flow_foundation.sql`
- Create: `gt-factory-os/db/tests/0146_stock_event_perfect_flow_foundation.test.sql`

- [ ] **Step 1: Write failing pgTAP test (test before DDL)**

Create `gt-factory-os/db/tests/0146_stock_event_perfect_flow_foundation.test.sql`:

```sql
BEGIN;
SELECT plan(15);

-- Movement types
SELECT has_column('private_core', 'stock_ledger', 'movement_type');
SELECT col_type_is('private_core', 'stock_ledger', 'movement_type', 'text');

-- New movement_type values are accepted
PREPARE insert_pick AS
  INSERT INTO private_core.stock_ledger
    (movement_id, movement_type, item_id, qty_delta, event_at, posted_at,
     source_channel, source_event_id, post_status)
  VALUES
    (gen_random_uuid(), 'LIONWHEEL_PICK', 'FG-CAL-1L', -1, now(), now(),
     'LIONWHEEL', 'lw_pick_test:1:1:t1', 'POSTED');
SELECT lives_ok('insert_pick', 'LIONWHEEL_PICK movement_type accepted');

-- Roll back so test data does not leak.
ROLLBACK TO SAVEPOINT pgtap_test_savepoint;

-- integration_sku_map.mapping_status exists with the locked enum domain
SELECT has_column('private_core', 'integration_sku_map', 'mapping_status');
SELECT col_default_is('private_core', 'integration_sku_map', 'mapping_status', 'active');

-- internal_units_per_shopify_unit
SELECT has_column('private_core', 'integration_sku_map', 'internal_units_per_shopify_unit');
SELECT col_type_is('private_core', 'integration_sku_map', 'internal_units_per_shopify_unit', 'numeric');
SELECT col_default_is('private_core', 'integration_sku_map', 'internal_units_per_shopify_unit', '1.0');

-- items.is_stock_managed
SELECT has_column('private_core', 'items', 'is_stock_managed');
SELECT col_type_is('private_core', 'items', 'is_stock_managed', 'boolean');
SELECT col_default_is('private_core', 'items', 'is_stock_managed', 'true');

-- orders_mirror_lines.posted_pick_transition_seq tracks the highest
-- transition counter posted to the ledger for this line
SELECT has_column('private_core', 'orders_mirror_lines', 'posted_pick_transition_seq');
SELECT col_type_is('private_core', 'orders_mirror_lines', 'posted_pick_transition_seq', 'integer');
SELECT col_default_is('private_core', 'orders_mirror_lines', 'posted_pick_transition_seq', '0');

-- system_locks table for active-writer mutex (Q6)
SELECT has_table('private_core', 'system_locks');
SELECT has_column('private_core', 'system_locks', 'lock_name');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test, verify it fails**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os
psql "$DATABASE_URL_POOLED" -f db/tests/0146_stock_event_perfect_flow_foundation.test.sql
```

Expected: assertion failures for `has_column ... mapping_status`, `has_column ... internal_units_per_shopify_unit`, `has_column ... is_stock_managed`, `has_column ... posted_pick_transition_seq`, `has_table ... system_locks`. The `LIONWHEEL_PICK` insert may also fail if a CHECK constraint excludes the value — capture the exact error to inform the migration.

- [ ] **Step 3: Write the migration**

Create `gt-factory-os/db/migrations/0146_stock_event_perfect_flow_foundation.sql`:

```sql
BEGIN;

-- ──────────────────────────────────────────────────────────────────────────
-- 0146 — Stock Event Perfect Flow: foundation
--
-- Adds ALL structural prerequisites for the pickup_at-triggered chain:
--   • new movement_types (LIONWHEEL_PICK / LIONWHEEL_UNPICK / LIONWHEEL_PICK_ADJUSTMENT)
--   • mapping_status enum on integration_sku_map
--   • internal_units_per_shopify_unit on integration_sku_map
--   • is_stock_managed on items
--   • posted_pick_transition_seq on orders_mirror_lines
--   • system_locks table for active-writer mutex
--
-- Pure additive. Safe to roll forward; existing columns are untouched.
-- See PRODUCTION/docs/superpowers/plans/2026-05-06-stock-event-perfect-flow.md
-- chunk 1 task 1.1.
-- ──────────────────────────────────────────────────────────────────────────

-- 1) Movement types — relax the CHECK constraint if one exists.
DO $$
DECLARE
  con_name text;
BEGIN
  SELECT conname INTO con_name
  FROM pg_constraint
  WHERE conrelid = 'private_core.stock_ledger'::regclass
    AND contype = 'c'
    AND pg_get_constraintdef(oid) LIKE '%movement_type%';
  IF con_name IS NOT NULL THEN
    EXECUTE format('ALTER TABLE private_core.stock_ledger DROP CONSTRAINT %I', con_name);
  END IF;
END $$;

ALTER TABLE private_core.stock_ledger
  ADD CONSTRAINT stock_ledger_movement_type_chk
  CHECK (movement_type IN (
    -- existing values, do NOT remove any
    'GR_POSTED','GR_REVERSAL','WASTE_POSTED','WASTE_REVERSAL',
    'COUNT_ADJUST','COUNT_ADJUST_REVERSAL',
    'PRODUCTION_OUTPUT','PRODUCTION_SCRAP','PRODUCTION_CONSUMPTION',
    'PRODUCTION_OUTPUT_REVERSAL','PRODUCTION_SCRAP_REVERSAL','PRODUCTION_CONSUMPTION_REVERSAL',
    'FG_OUT_PICK','FG_OUT_PICK_REVERSAL',
    -- new values introduced by 0146
    'LIONWHEEL_PICK','LIONWHEEL_UNPICK','LIONWHEEL_PICK_ADJUSTMENT'
  ));

COMMENT ON CONSTRAINT stock_ledger_movement_type_chk ON private_core.stock_ledger IS
  'Locked enumeration. Update by writing a new migration that recreates the constraint with a superset; never drop without a replacement in the same transaction.';

-- 2) integration_sku_map.mapping_status
DO $$ BEGIN
  CREATE TYPE private_core.sku_mapping_status AS ENUM (
    'active',
    'pending_item_creation',     -- mapped externally; internal item not yet created
    'missing_internal_item',     -- mapped but item_id is NULL — requires master data
    'excluded_non_stock',        -- explicitly not stock-tracked (merchandise, glassware)
    'excluded_legacy_bundle',    -- legacy Shopify composed/bundle SKU; out of scope for FG sync
    'inactive'                   -- soft-deleted alias
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

ALTER TABLE private_core.integration_sku_map
  ADD COLUMN IF NOT EXISTS mapping_status private_core.sku_mapping_status
    NOT NULL DEFAULT 'active';

CREATE INDEX IF NOT EXISTS integration_sku_map_status_idx
  ON private_core.integration_sku_map (source_channel, mapping_status);

-- 3) Per-mapping packaging conversion (Tom Q3 — internal_units_per_shopify_unit,
--    NOT shopify_units_per_internal_unit, because the latter inverts to fractions
--    on multi-pack SKUs.)
ALTER TABLE private_core.integration_sku_map
  ADD COLUMN IF NOT EXISTS internal_units_per_shopify_unit numeric(20,8)
    NOT NULL DEFAULT 1.0;

ALTER TABLE private_core.integration_sku_map
  ADD CONSTRAINT integration_sku_map_units_positive
    CHECK (internal_units_per_shopify_unit > 0);

-- 4) items.is_stock_managed (Tom Q2 — only for items that truly never affect stock)
ALTER TABLE private_core.items
  ADD COLUMN IF NOT EXISTS is_stock_managed boolean NOT NULL DEFAULT true;

COMMENT ON COLUMN private_core.items.is_stock_managed IS
  'False only for items that should never affect stock truth (e.g. promo glassware, kits we ship but do not stock). Default true preserves existing behavior. Per Tom Q2 2026-05-06.';

-- 5) Per-line transition counter on the mirror — the chain reads this to decide
--    whether the next observed pick state warrants a new ledger event.
ALTER TABLE private_core.orders_mirror_lines
  ADD COLUMN IF NOT EXISTS posted_pick_transition_seq integer NOT NULL DEFAULT 0;

ALTER TABLE private_core.orders_mirror_lines
  ADD CONSTRAINT orders_mirror_lines_pick_seq_nonneg
    CHECK (posted_pick_transition_seq >= 0);

-- 6) Active-writer mutex table (Tom Q6).
--    A FG-Shopify writer takes a row before writing; releases on success/failure.
CREATE TABLE IF NOT EXISTS private_core.system_locks (
  lock_name text PRIMARY KEY,
  holder_name text NOT NULL,
  acquired_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  notes text
);

COMMENT ON TABLE private_core.system_locks IS
  'Cooperative mutex for system-wide singletons (e.g. shopify_fg_writer). A holder writes a row with expires_at; concurrent acquirers wait or fail.';

COMMIT;
```

- [ ] **Step 4: Apply migration**

```bash
psql "$DATABASE_URL_POOLED" -f gt-factory-os/db/migrations/0146_stock_event_perfect_flow_foundation.sql
```

Expected: `BEGIN`, multiple `ALTER TABLE` / `CREATE TYPE` / `CREATE TABLE`, `COMMIT` with no errors.

- [ ] **Step 5: Re-run pgTAP test, verify it passes**

```bash
psql "$DATABASE_URL_POOLED" -f gt-factory-os/db/tests/0146_stock_event_perfect_flow_foundation.test.sql
```

Expected: `# Looks like you have run 15 tests`, `ok 1` … `ok 15`, `# All 15 tests passed`.

- [ ] **Step 6: Commit**

```bash
git add gt-factory-os/db/migrations/0146_stock_event_perfect_flow_foundation.sql \
        gt-factory-os/db/tests/0146_stock_event_perfect_flow_foundation.test.sql
git commit -m "db(0146): foundation for stock-event perfect flow

Adds the schema prerequisites for chunk 3 (LionWheel pickup_at trigger):
- LIONWHEEL_PICK / LIONWHEEL_UNPICK / LIONWHEEL_PICK_ADJUSTMENT movement_types
- integration_sku_map.mapping_status enum + .internal_units_per_shopify_unit
- items.is_stock_managed
- orders_mirror_lines.posted_pick_transition_seq
- system_locks table

Pure additive. 15/15 pgTAP green.

Plan: PRODUCTION/docs/superpowers/plans/2026-05-06-stock-event-perfect-flow.md"
```

---

## Chunk 2: Mirror Enrichment — pickup_at populated, qty enriched at pickup time

**Outcome:** Every new `orders_mirror` row has its `pickup_at` populated. The poller's enrichment pass runs at pickup time (not only at terminal). `lw_qty_picked` is captured whenever LionWheel exposes it, even pre-terminal.

### Task 2.1 — Refactor poller to two-stage pull

**Files:**
- Modify: `gt-factory-os/api/src/integrations/lionwheel/poller.ts`
- Test: `gt-factory-os/api/test/lionwheel_poller_pickup_at.test.ts` (new)

The current poller calls `/tasks?limit=200` (summary only). The summary does NOT include `pickup_at`. We add a per-task `/tasks/show/<id>` enrichment pass that runs on ANY new mirror row, not just terminal. The result: `pickup_at`, `lw_qty_picked` (when available), `lw_line_status` populated.

- [ ] **Step 1: Write the failing test**

Create `gt-factory-os/api/test/lionwheel_poller_pickup_at.test.ts`:

```typescript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { enrichMirrorWithDetail, type MirrorRow } from '../src/integrations/lionwheel/poller.js';

test('enrichMirrorWithDetail populates pickup_at on first observation', async () => {
  const mirror: MirrorRow = { lw_task_id: 24008294, pickup_at: null };
  const fakeFetcher = async (id: number) => ({
    id, pickup_at: '2026-05-04T08:00:00.000+03:00',
    status: 'ASSIGNED',
    order_items: [{ id: 933253784, sku: 'GT-SEN-LOW-1L', quantity: 6 }]
  });
  const result = await enrichMirrorWithDetail([mirror], fakeFetcher);
  assert.equal(result[0].pickup_at, '2026-05-04T08:00:00.000+03:00');
  assert.equal(result[0].enriched, true);
});

test('enrichMirrorWithDetail does not overwrite existing pickup_at', async () => {
  const mirror: MirrorRow = {
    lw_task_id: 1, pickup_at: '2026-05-01T10:00:00.000+03:00'
  };
  const fakeFetcher = async () => ({
    id: 1, pickup_at: '2099-01-01T00:00:00.000+03:00', status: 'ASSIGNED',
    order_items: []
  });
  const result = await enrichMirrorWithDetail([mirror], fakeFetcher);
  // Existing pickup_at preserved — LionWheel may rarely change pickup_at,
  // and we want a stable single source of truth per task.
  assert.equal(result[0].pickup_at, '2026-05-01T10:00:00.000+03:00');
});

test('enrichMirrorWithDetail tolerates LionWheel detail-fetch failure', async () => {
  const mirror: MirrorRow = { lw_task_id: 99, pickup_at: null };
  const fakeFetcher = async () => { throw new Error('CF 1010'); };
  const result = await enrichMirrorWithDetail([mirror], fakeFetcher);
  assert.equal(result[0].pickup_at, null);
  assert.equal(result[0].enriched, false);
  assert.equal(result[0].enrichment_error, 'CF 1010');
});
```

- [ ] **Step 2: Run, verify it fails**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os/api && npx node --test test/lionwheel_poller_pickup_at.test.ts
```

Expected: `enrichMirrorWithDetail` not exported.

- [ ] **Step 3: Implement enrichment**

In `gt-factory-os/api/src/integrations/lionwheel/poller.ts` add a new exported function. Sketch:

```typescript
export interface MirrorRow {
  lw_task_id: number;
  pickup_at: string | null;
  enriched?: boolean;
  enrichment_error?: string;
  // … existing fields preserved
}

export type DetailFetcher = (id: number) => Promise<{
  id: number;
  pickup_at: string;
  status: string;
  order_items: Array<{ id: number; sku: string; quantity: number; picked_quantity?: number }>;
}>;

export async function enrichMirrorWithDetail(
  rows: MirrorRow[],
  fetcher: DetailFetcher
): Promise<MirrorRow[]> {
  const out: MirrorRow[] = [];
  for (const row of rows) {
    try {
      const detail = await fetcher(row.lw_task_id);
      out.push({
        ...row,
        pickup_at: row.pickup_at ?? detail.pickup_at, // never overwrite an existing value
        enriched: true,
      });
    } catch (e: any) {
      out.push({ ...row, enriched: false, enrichment_error: e?.message ?? String(e) });
    }
  }
  return out;
}
```

The trigger inside the existing poller's main loop changes from "newly terminal → enrich" to "any row with `pickup_at IS NULL` OR `lw_pick_enrichment_status IS NULL` → enrich". This pulls forward the enrichment pass to as soon as we see the task.

- [ ] **Step 4: Run tests, verify they pass**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os/api && npx node --test test/lionwheel_poller_pickup_at.test.ts
```

Expected: 3/3 PASS.

- [ ] **Step 5: Commit**

```bash
git add gt-factory-os/api/src/integrations/lionwheel/poller.ts \
        gt-factory-os/api/test/lionwheel_poller_pickup_at.test.ts
git commit -m "feat(lionwheel): enrich mirror with pickup_at at first observation

Move the detail-fetch enrichment from the terminal-status branch to any
row with NULL pickup_at. This is the prerequisite for chunk 3's
pickup_at-triggered chain — without populated pickup_at, the chain
cannot decide WHEN to post.

Existing pickup_at values are preserved (LionWheel rarely changes
pickup_at; we choose first-observation as authoritative). Detail
failures are tolerated (recorded as enrichment_error, mirror row stays
NULL — chain will retry on next pass).

3/3 node:test PASS.

Plan: PRODUCTION/docs/superpowers/plans/2026-05-06-stock-event-perfect-flow.md
chunk 2."
```

### Task 2.2 — Backfill pickup_at for existing 364 NULL rows

**Files:**
- Create: `gt-factory-os/scripts/backfill_mirror_pickup_at.mjs`

- [ ] **Step 1: Write the script**

```javascript
// gt-factory-os/scripts/backfill_mirror_pickup_at.mjs
//
// One-shot: pull /tasks/show/<id> for every orders_mirror row whose pickup_at
// IS NULL, write the value back. No mirror rows are deleted or reshaped.
// Per Tom 2026-05-06 (chunk 2 task 2.2).
import 'dotenv/config';
import pg from 'pg';

const { Pool } = pg;
const pool = new Pool({ connectionString: process.env.DATABASE_URL_POOLED, ssl: { rejectUnauthorized: false } });
const KEY = process.env.LIONWHEEL_API_KEY;
const BASE = 'https://members.lionwheel.com/api/v1';
const UA = 'GT-FactoryOS-MirrorBackfill/1.0';

async function fetchDetail(id) {
  const r = await fetch(`${BASE}/tasks/show/${id}?key=${KEY}`, { headers: { 'User-Agent': UA } });
  if (!r.ok) return null;
  const j = await r.json();
  return j?.task ?? null;
}

const dryRun = process.argv.includes('--dry-run');

const { rows } = await pool.query(`
  SELECT mirror_id, lw_task_id FROM private_core.orders_mirror
  WHERE pickup_at IS NULL AND retired_at IS NULL
  ORDER BY captured_at DESC LIMIT 1000
`);
console.log(`pending: ${rows.length}`);

let updated = 0, skipped = 0, failed = 0;
for (const row of rows) {
  const detail = await fetchDetail(row.lw_task_id);
  if (!detail?.pickup_at) { skipped++; continue; }
  if (dryRun) {
    console.log(`[dry] ${row.lw_task_id} -> ${detail.pickup_at}`);
    updated++;
    continue;
  }
  try {
    await pool.query(
      `UPDATE private_core.orders_mirror SET pickup_at = $1 WHERE mirror_id = $2 AND pickup_at IS NULL`,
      [detail.pickup_at, row.mirror_id]
    );
    updated++;
  } catch (e) { failed++; }
  await new Promise(r => setTimeout(r, 150));
}
console.log({ updated, skipped, failed, dryRun });
await pool.end();
```

- [ ] **Step 2: Dry-run**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os && node scripts/backfill_mirror_pickup_at.mjs --dry-run
```

Expected: prints `pending: 364`, then 364 `[dry] <task_id> -> <iso>` lines, finally `{ updated: 364, skipped: 0, failed: 0, dryRun: true }`.

- [ ] **Step 3: Run for real**

```bash
node scripts/backfill_mirror_pickup_at.mjs
```

Expected: `{ updated: ~364, ... }` and a follow-up audit run shows `pickup_at IS NULL on N/364` where N is much smaller (only failures).

- [ ] **Step 4: Verify via audit skill**

```bash
python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" --days 7 --quiet
```

Expected: top-line still <95% (chunk 3 hasn't landed) but the Data Quality section's pickup_at-NULL line drops near zero.

- [ ] **Step 5: Commit**

```bash
git add gt-factory-os/scripts/backfill_mirror_pickup_at.mjs
git commit -m "chore(lionwheel): one-shot backfill of pickup_at on 364 mirror rows

Pulls /tasks/show/<id> for every orders_mirror row with pickup_at=NULL
and writes the value. Read-only on every other column. Idempotent
(WHERE pickup_at IS NULL guard).

This is part of chunk 2 of the perfect-flow plan: chain in chunk 3
needs populated pickup_at to fire."
```

---

## Chunk 3: Chain Posting + Reversal — the heart of the plan

**Outcome:** For every shipped LionWheel line, a correct `stock_ledger` row exists. PICK posts at pickup_at. UNPICK reverts on cancellation. PICK_ADJUSTMENT compensates when picked qty diverges from ordered qty on later enrichment. All idempotent on `source_event_transition_id`.

### §3.0 Quantity-handling design (decision point flagged for review)

At pickup_at, LionWheel exposes `order_items[].quantity` (ordered) but not always `lw_qty_picked`. The chain must decide:

- **Option A (chosen for this plan):** Decrement `quantity` at pickup_at. On later enrichment, if `picked_quantity` is reported AND differs from `quantity`, post a `LIONWHEEL_PICK_ADJUSTMENT` delta of `(picked - quantity)` (negative if short-pick, positive if over-pick).
- **Option B (alternative):** Wait for `picked_quantity` enrichment before posting. Trades up to a few hours of stock-truth lag for exact-on-first-post quantities.

The plan implements Option A. Option B = same code path with the trigger condition flipped. Reviewer should confirm A vs B before chunk 3 lands.

Either way, Tom's "Never use lw_qty_ordered for stock deduction" rule from the legacy reconciliation header **is replaced** in this plan — the new contract uses `quantity` provisionally, with `LIONWHEEL_PICK_ADJUSTMENT` ensuring eventual exactness. Note this in the file comment.

### Task 3.1 — Transition state machine (pure module)

**Files:**
- Create: `gt-factory-os/api/src/integrations/lionwheel/pick_state.ts`
- Test: `gt-factory-os/api/test/lionwheel_pick_state.test.ts`

A small pure module that, given (mirror line current state) + (last posted transition) returns a list of zero or more `Transition` records to emit. No DB I/O. Trivially unit-testable.

- [ ] **Step 1: Write failing test (covers acceptance tests #1, #2, #3, #7)**

Create `gt-factory-os/api/test/lionwheel_pick_state.test.ts`:

```typescript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { computeTransitions, type MirrorLineState, type PostedState } from '../src/integrations/lionwheel/pick_state.js';

const baseLine: MirrorLineState = {
  lw_task_id: '1', lw_order_item_id: '1',
  pickup_at: '2026-05-04T08:00:00+03:00',
  status: 'ASSIGNED',
  retired_at: null,
  resolution_status: 'resolved',
  item_id: 'FG-CAL-1L',
  qty_ordered: 6,
  qty_picked: null,
  is_stock_managed: true,
  mapping_status: 'active',
};
const noPosted: PostedState = { last_posted_seq: 0, net_qty_delta: 0 };

test('AT.1: pickup_at posts exactly once', () => {
  const ts = computeTransitions(baseLine, noPosted, new Date('2026-05-04T09:00:00+03:00'));
  assert.equal(ts.length, 1);
  assert.equal(ts[0].kind, 'PICK');
  assert.equal(ts[0].qty_delta, -6);
  assert.equal(ts[0].seq, 1);
});

test('AT.2: duplicate pickup does not double-decrement', () => {
  const posted: PostedState = { last_posted_seq: 1, net_qty_delta: -6 };
  const ts = computeTransitions(baseLine, posted, new Date('2026-05-04T10:00:00+03:00'));
  assert.deepEqual(ts, []);
});

test('AT.3: not-picked-after-pickup creates a compensating increment', () => {
  const posted: PostedState = { last_posted_seq: 1, net_qty_delta: -6 };
  const cancelled = { ...baseLine, status: 'CANCELED' as const };
  const ts = computeTransitions(cancelled, posted, new Date('2026-05-04T11:00:00+03:00'));
  assert.equal(ts.length, 1);
  assert.equal(ts[0].kind, 'UNPICK');
  assert.equal(ts[0].qty_delta, +6);
  assert.equal(ts[0].seq, 2);
});

test('AT.7: PICK_ADJUSTMENT on later qty enrichment', () => {
  const posted: PostedState = { last_posted_seq: 1, net_qty_delta: -6 };
  const enriched = { ...baseLine, qty_picked: 4 }; // operator only picked 4 of 6
  const ts = computeTransitions(enriched, posted, new Date('2026-05-04T12:00:00+03:00'));
  assert.equal(ts.length, 1);
  assert.equal(ts[0].kind, 'PICK_ADJUSTMENT');
  // Posted -6, real should be -4 → adjustment = +2
  assert.equal(ts[0].qty_delta, +2);
  assert.equal(ts[0].seq, 2);
});

test('skips items with mapping_status=missing_internal_item', () => {
  const missing = { ...baseLine, item_id: null, mapping_status: 'missing_internal_item' as const };
  const ts = computeTransitions(missing, noPosted, new Date());
  assert.deepEqual(ts, []);
});

test('skips items with is_stock_managed=false (AT.5: silent)', () => {
  const nonStock = { ...baseLine, is_stock_managed: false };
  const ts = computeTransitions(nonStock, noPosted, new Date());
  assert.deepEqual(ts, []);
});

test('skips when pickup_at is in the future', () => {
  const future = { ...baseLine, pickup_at: '2099-01-01T00:00:00+03:00' };
  const ts = computeTransitions(future, noPosted, new Date('2026-05-06T00:00:00+03:00'));
  assert.deepEqual(ts, []);
});

test('skips retired (split/merge) lines', () => {
  const retired = { ...baseLine, retired_at: '2026-05-05T00:00:00+03:00' };
  const ts = computeTransitions(retired, noPosted, new Date());
  assert.deepEqual(ts, []);
});
```

- [ ] **Step 2: Run, verify it fails (module does not yet exist)**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os/api && npx node --test test/lionwheel_pick_state.test.ts
```

Expected: import error.

- [ ] **Step 3: Implement `pick_state.ts`**

```typescript
// gt-factory-os/api/src/integrations/lionwheel/pick_state.ts
//
// Pure transition-state machine. Decides what (if any) ledger transitions to
// emit for a single mirror line, given its currently observed state + the
// chain's already-posted state. No DB I/O.

export type Status = 'UNASSIGNED'|'ASSIGNED'|'ACTIVE'|'IN_TRANSFER'|'COMPLETED'|'ROUNDTRIP_DELIVERED'|'CANCELED'|'CANCELLED'|'FAILED'|'FINAL_FAILED';
export type MappingStatus = 'active'|'pending_item_creation'|'missing_internal_item'|'excluded_non_stock'|'excluded_legacy_bundle'|'inactive';

export interface MirrorLineState {
  lw_task_id: string;
  lw_order_item_id: string;
  pickup_at: string | null;
  status: Status;
  retired_at: string | null;
  resolution_status: 'resolved'|'unresolved'|null;
  item_id: string | null;
  qty_ordered: number;
  qty_picked: number | null;
  is_stock_managed: boolean;
  mapping_status: MappingStatus;
}

export interface PostedState {
  last_posted_seq: number;
  net_qty_delta: number;  // sum of all qty_delta posted for this line so far
}

export type TransitionKind = 'PICK' | 'UNPICK' | 'PICK_ADJUSTMENT';

export interface Transition {
  kind: TransitionKind;
  qty_delta: number;
  seq: number;
  reason: string;
}

const NON_PICKABLE: ReadonlySet<Status> = new Set(['UNASSIGNED','CANCELED','CANCELLED','FAILED','FINAL_FAILED']);

export function computeTransitions(
  line: MirrorLineState,
  posted: PostedState,
  now: Date
): Transition[] {
  // Skip rules — silent (AT.5)
  if (line.retired_at) return [];
  if (!line.is_stock_managed) return [];
  if (line.mapping_status === 'inactive') return [];
  if (line.mapping_status === 'excluded_non_stock') return [];
  if (line.mapping_status === 'excluded_legacy_bundle') return [];

  // Skip rules — emit exception elsewhere (chunk 4) but no transition here
  if (line.mapping_status === 'pending_item_creation') return [];
  if (line.mapping_status === 'missing_internal_item') return [];
  if (line.resolution_status !== 'resolved') return [];
  if (!line.item_id) return [];

  // pickup_at must exist and be ≤ now
  if (!line.pickup_at) return [];
  const pa = new Date(line.pickup_at);
  if (Number.isNaN(pa.getTime())) return [];
  if (pa > now) return [];

  // Branch on observed state + posted state
  const cancelled = NON_PICKABLE.has(line.status);
  const expectedQty = -1 * (line.qty_picked ?? line.qty_ordered);

  if (posted.last_posted_seq === 0) {
    // Never posted before. Only post if not cancelled.
    if (cancelled) return [];
    return [{
      kind: 'PICK',
      qty_delta: -line.qty_ordered,
      seq: 1,
      reason: 'pickup_at_passed_first_observation',
    }];
  }

  // We have posted before — decide if reality has diverged.
  if (cancelled) {
    // Compensating increment. Only one UNPICK per posted PICK chain.
    if (posted.net_qty_delta === 0) return []; // already balanced
    return [{
      kind: 'UNPICK',
      qty_delta: -posted.net_qty_delta, // restore what was decremented
      seq: posted.last_posted_seq + 1,
      reason: 'cancelled_or_failed_after_pickup',
    }];
  }

  // Same observed pick state, possibly with a more accurate qty_picked enrichment.
  const drift = expectedQty - posted.net_qty_delta;
  if (Math.abs(drift) < 1e-6) return [];
  return [{
    kind: 'PICK_ADJUSTMENT',
    qty_delta: drift,
    seq: posted.last_posted_seq + 1,
    reason: 'qty_picked_enrichment_revealed_drift',
  }];
}
```

- [ ] **Step 4: Run tests, verify all pass**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os/api && npx node --test test/lionwheel_pick_state.test.ts
```

Expected: 8/8 PASS.

- [ ] **Step 5: Commit**

```bash
git add gt-factory-os/api/src/integrations/lionwheel/pick_state.ts \
        gt-factory-os/api/test/lionwheel_pick_state.test.ts
git commit -m "feat(lionwheel): pure transition state machine for pickup_at chain

Decides PICK / UNPICK / PICK_ADJUSTMENT transitions given mirror line
state + posted state. No DB I/O. Acceptance tests AT.1, AT.2, AT.3,
AT.7 covered as unit tests; non-stock and missing-item skip paths
covered as well.

8/8 node:test PASS.

Plan chunk 3 task 3.1."
```

### Task 3.2 — Wire the state machine into the existing reconciler

**Files:**
- Modify: `gt-factory-os/api/src/integrations/lionwheel/reconciliation.ts`
- Test: `gt-factory-os/api/test/lionwheel_chain_post_pickup.test.ts` (new)

- [ ] **Step 1: Write failing integration test**

Create `gt-factory-os/api/test/lionwheel_chain_post_pickup.test.ts` — sets up a temp pool, seeds one mirror task with pickup_at in the past, runs the chain, asserts:
1. exactly one row in `stock_ledger` with `movement_type='LIONWHEEL_PICK'`, `source_event_id='lw_pick:<task>:<line>:t1'`, `qty_delta=-6`.
2. `orders_mirror_lines.posted_pick_transition_seq=1`.
3. running the chain again with no state change posts no new rows (idempotency).

- [ ] **Step 2: Run, verify it fails**

Expected: chain still uses the legacy enrichPickedQuantities/reconcileAfterPoll terminal-only logic.

- [ ] **Step 3: Refactor the chain**

In `reconciliation.ts`, add a new exported function `reconcilePickupAt(pool, config)` that:
1. Selects every `orders_mirror_lines` row for tasks where `pickup_at <= now()` and the row has not been retired.
2. For each, calls `computeTransitions(line, postedState, now)`.
3. For each transition, INSERTs a `stock_ledger` row inside a transaction with `source_event_id = 'lw_pick:<task>:<line>:t<seq>' | 'lw_unpick:...' | 'lw_pick_adj:...'` and increments `orders_mirror_lines.posted_pick_transition_seq`.
4. Uses `ON CONFLICT (source_event_id) DO NOTHING` (or unique index — see step 3a) for hard idempotency.

- [ ] **Step 3a: Add unique index on source_event_id** (one-time migration `0147_stock_ledger_source_event_id_unique.sql`)

```sql
BEGIN;
-- Strict idempotency for LionWheel-driven chain. Every posted ledger row from
-- the chain has a deterministic source_event_id; uniqueness prevents any race
-- or replay from double-posting.
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS stock_ledger_lw_source_event_id_uniq
  ON private_core.stock_ledger (source_event_id)
  WHERE source_channel = 'LIONWHEEL';
COMMIT;
```

(`CONCURRENTLY` is safe in production; the partial WHERE keeps the index lean.)

- [ ] **Step 4: Run integration test, verify it passes**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os/api && npx node --test test/lionwheel_chain_post_pickup.test.ts
```

Expected: 3/3 PASS.

- [ ] **Step 5: Add fg_out_bridge_enabled lifecycle**

The existing `DEFAULT_RECONCILER_CONFIG.fg_out_bridge_enabled = false`. We KEEP that default, but introduce `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` env var that the API reads on boot. Production config (Railway) flips to `true` only after Tom's review passes chunks 3 + 4.

Add a startup log line:

```
[lionwheel] fg_out_bridge_enabled=true|false (from env LIONWHEEL_FG_OUT_BRIDGE_ENABLED)
```

- [ ] **Step 6: Commit**

```bash
git add gt-factory-os/api/src/integrations/lionwheel/reconciliation.ts \
        gt-factory-os/api/test/lionwheel_chain_post_pickup.test.ts \
        gt-factory-os/db/migrations/0147_stock_ledger_source_event_id_unique.sql
git commit -m "feat(lionwheel): pickup_at-triggered reconcile with PICK/UNPICK/ADJ

Implements reconcilePickupAt(): walks every mirror line whose pickup_at
has passed, calls computeTransitions() (chunk 3 task 3.1), writes the
resulting transitions to stock_ledger inside a transaction. Per-line
posted_pick_transition_seq is advanced atomically with the ledger
insert.

Strict idempotency via partial unique index on
stock_ledger.source_event_id WHERE source_channel='LIONWHEEL'
(migration 0147).

fg_out_bridge_enabled remains false-by-default; flip via
LIONWHEEL_FG_OUT_BRIDGE_ENABLED env on Railway after chunk 4 lands and
the audit shows ≥99% top-line in shadow mode (chunk 9).

3/3 integration node:test PASS. AT.1, AT.2, AT.3 covered.

Plan chunk 3 tasks 3.2 + 3.2a."
```

---

## Chunk 4: Master-data Governance + Missing-Item Exceptions

**Outcome:** Every unmapped or pending-master-data SKU in `integration_sku_map` has an explicit `mapping_status` other than `active`. The chain reads this status and either skips silently (excluded categories) or skips + emits a `lionwheel_missing_internal_item` exception (pending categories). Operators see the queue at `/admin/sku-aliases`.

### Task 4.1 — Backfill `mapping_status` from current rows

**Files:**
- Create: `gt-factory-os/scripts/backfill_mapping_status.mjs`

Walks `integration_sku_map` and assigns status based on observed shape:
- `item_id IS NULL` AND `external_sku` is recognized as glassware/kit → `excluded_non_stock`
- `item_id IS NULL` otherwise → `missing_internal_item`
- `item_id IS NOT NULL` → leave `active`
- Existing alias-not-yet-approved rows → `pending_item_creation`

- [ ] **Step 1: Build the classifier**

```javascript
// gt-factory-os/scripts/backfill_mapping_status.mjs
import 'dotenv/config';
import pg from 'pg';
const { Pool } = pg;
const pool = new Pool({ connectionString: process.env.DATABASE_URL_POOLED, ssl: { rejectUnauthorized: false } });

const NON_STOCK_PATTERNS = [/GT-GLA-/, /GT-MAT-KIT/, /AP-FRO-/, /-CUP$/];

function classify(row) {
  if (row.item_id) return 'active';
  if (row.approval_status !== 'approved') return 'pending_item_creation';
  if (NON_STOCK_PATTERNS.some(re => re.test(row.external_sku))) return 'excluded_non_stock';
  return 'missing_internal_item';
}

const dryRun = process.argv.includes('--dry-run');
const { rows } = await pool.query(`SELECT * FROM private_core.integration_sku_map`);
const counts = {};
for (const row of rows) {
  const ms = classify(row);
  counts[ms] = (counts[ms] ?? 0) + 1;
  if (!dryRun) {
    await pool.query(
      `UPDATE private_core.integration_sku_map SET mapping_status = $1 WHERE alias_id = $2`,
      [ms, row.alias_id]
    );
  }
}
console.log({ dryRun, total: rows.length, counts });
await pool.end();
```

- [ ] **Step 2: Dry-run + commit on green numbers**

```bash
cd c:/Users/tomw2/Projects/gt-factory-os && node scripts/backfill_mapping_status.mjs --dry-run
```

Expected `counts` shape: `{ active: ~115, pending_item_creation: ~5, excluded_non_stock: ~10, missing_internal_item: ~1 }`. If shape differs significantly, surface to Tom.

```bash
node scripts/backfill_mapping_status.mjs
```

- [ ] **Step 3: Commit**

```bash
git add gt-factory-os/scripts/backfill_mapping_status.mjs
git commit -m "chore(lionwheel): backfill integration_sku_map.mapping_status

Classifies every existing alias: active / pending_item_creation /
excluded_non_stock / missing_internal_item. Idempotent. Dry-run by
default.

Plan chunk 4 task 4.1."
```

### Task 4.2 — Emit `lionwheel_missing_internal_item` exceptions from the chain

**Files:**
- Modify: `gt-factory-os/api/src/integrations/lionwheel/reconciliation.ts`
- Test: `gt-factory-os/api/test/lionwheel_missing_item_exception.test.ts` (new, covers AT.4)

- [ ] **Step 1: Write the failing test**

```typescript
import { test } from 'node:test';
import assert from 'node:assert/strict';
// … set up a mirror line with mapping_status='missing_internal_item' and run the chain

test('AT.4: missing internal item emits exception, no ledger row', async () => {
  // Arrange: seed an integration_sku_map row with mapping_status='missing_internal_item'
  // and an orders_mirror_lines row referencing that external_sku.
  // Act: run reconcilePickupAt.
  // Assert: zero stock_ledger rows for that line; exactly one open exception
  //         with category='lionwheel_missing_internal_item' and
  //         related_entity_id matching the lw_task_id.
});
```

- [ ] **Step 2: Run, verify failure**

- [ ] **Step 3: Implement emission inside reconcilePickupAt**

Inside `reconcilePickupAt`, when `computeTransitions` returns `[]` because of `pending_item_creation` or `missing_internal_item`, write to `private_core.exceptions` with:

```sql
INSERT INTO private_core.exceptions (
  category, severity, title, detail,
  related_entity_type, related_entity_id, dedupe_key, status
) VALUES (
  'lionwheel_missing_internal_item', 'high',
  'Missing internal item for LionWheel SKU ' || $external_sku,
  jsonb_build_object('lw_sku', $sku, 'lw_task_id', $tid, 'lw_order_item_id', $oid),
  'orders_mirror_lines', $line_mirror_id,
  'lwmissing:' || $tid || ':' || $oid, 'open'
) ON CONFLICT (dedupe_key) DO NOTHING;
```

The `dedupe_key` ensures one exception per line — re-running the chain doesn't multiply exceptions.

- [ ] **Step 4: Run test, verify pass**

- [ ] **Step 5: Commit**

```bash
git add gt-factory-os/api/src/integrations/lionwheel/reconciliation.ts \
        gt-factory-os/api/test/lionwheel_missing_item_exception.test.ts
git commit -m "feat(lionwheel): emit visible exception on missing internal item

When the chain encounters a mirror line whose mapping_status indicates
master data is missing/pending, the chain skips the ledger post AND
writes a deduped exception so the operator sees it in the inbox + the
audit. AT.4 covered.

Plan chunk 4 task 4.2."
```

### Task 4.3 — Manual review queue surfaces

**Files:**
- Modify: `portal/src/app/admin/sku-aliases/page.tsx` (or wherever the existing alias review UI lives — verify path)

Add a filter chip for `mapping_status` so the planner can scan `pending_item_creation` and `missing_internal_item` rows separately. UX detail; no behavior change.

- [ ] Steps 1-5 follow the same TDD shape; a Playwright + manual smoke test on a staging Vercel preview is enough here.

### Task 4.4 — Audit skill awareness of new statuses

**Files:**
- Modify: `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py`

The audit's reason rollup currently knows `unmapped_sku`. After chunk 4 there are richer reasons. Update the categorization to read `mapping_status` directly instead of inferring from `item_id IS NULL`. Add a new bucket in the data-quality section: "K mapped SKUs in mapping_status='pending_item_creation' awaiting master data."

- [ ] Re-run the eval set (`evals/grade.py 19`) → expect 30/30 still pass; visual report shows the new bucket.

---

## Chunk 5: Shopify Map Cleanup + Bundle Exclusion

**Outcome:** All 55 stale Shopify map entries are flipped to `mapping_status='inactive'`; all 35 conversion-ambiguous entries get an explicit `internal_units_per_shopify_unit` value if Tom can resolve them, OR `mapping_status='excluded_legacy_bundle'` if not.

### Task 5.1 — Flag stale Shopify variants

**Files:**
- Create: `gt-factory-os/scripts/cleanup_shopify_sku_map.mjs`

Walks every `integration_sku_map` row with `source_channel='shopify'`. For each, calls Shopify `/products.json` to see if the variant exists. If not → mark `mapping_status='inactive'`. Idempotent. Dry-run first.

- [ ] Steps 1-5 mirror chunk 4 task 4.1.

### Task 5.2 — Conversion-ratio resolution worksheet

**Files:**
- Create: `PRODUCTION/.audit-tmp/shopify_conversion_resolution_worksheet.csv` (one-time)

Generated CSV with: `external_sku, item_id, item_name, items.pack_size, suggested_internal_units_per_shopify_unit, decision`. Tom fills `decision` with the integer or `bundle_exclude`. A second script reads the CSV and applies.

- [ ] Tom must look at the worksheet and decide; no automation here. Mark this task as "human-in-the-loop required" in the executor's queue.

### Task 5.3 — Apply the worksheet

**Files:**
- Create: `gt-factory-os/scripts/apply_shopify_conversion_worksheet.mjs`

Reads `decision` column. For numeric → set `internal_units_per_shopify_unit`. For `bundle_exclude` → set `mapping_status='excluded_legacy_bundle'`. Dry-run first. Idempotent.

- [ ] Acceptance test #6 covered: re-run the audit; layer 4 should now compute on the full 121 mappings minus the explicitly excluded ones, with the conversion correctly applied for 6-pack SKUs.

---

## Chunk 6: TEST-LW Hard Delete

**Outcome:** Exactly 9 `TEST-LW-*` ledger rows + 5 negative-balance fixtures are deleted. The audit's negative-balance section becomes empty. Phantom-events count drops to 0. Nothing else is touched.

### Task 6.1 — Dry-run + count guard

**Files:**
- Create: `gt-factory-os/scripts/cleanup_test_lw_synthetic.mjs`

```javascript
// Tom-locked invariants (Q4):
//   exactly 9 stock_ledger rows where item_id LIKE 'TEST-LW-%'
//   exactly 5 current_balances rows where item_id LIKE 'TEST-LW-%' AND calculated_on_hand < 0
//
// Refuses to proceed if either count drifts.

const EXPECTED_LEDGER = 9;
const EXPECTED_NEG_BALANCES = 5;

const dryRun = !process.argv.includes('--apply');

const ledgerCount = (await pool.query(
  `SELECT count(*)::int n FROM private_core.stock_ledger WHERE item_id LIKE 'TEST-LW-%'`
)).rows[0].n;
const negCount = (await pool.query(
  `SELECT count(*)::int n FROM private_core.current_balances
   WHERE item_id LIKE 'TEST-LW-%' AND calculated_on_hand < 0`
)).rows[0].n;

if (ledgerCount !== EXPECTED_LEDGER || negCount !== EXPECTED_NEG_BALANCES) {
  console.error(`REFUSING: expected ledger=${EXPECTED_LEDGER}, neg=${EXPECTED_NEG_BALANCES}; got ledger=${ledgerCount}, neg=${negCount}`);
  process.exit(2);
}
console.log(`shape verified: ${ledgerCount} ledger rows + ${negCount} neg balances`);

if (dryRun) { console.log('dry-run, exiting'); process.exit(0); }

// Snapshot
const snap = `gt-factory-os/.snapshots/test_lw_cleanup_${new Date().toISOString().replace(/[:.]/g,'-')}`;
fs.mkdirSync(snap, { recursive: true });
fs.writeFileSync(`${snap}/ledger.json`, JSON.stringify(
  (await pool.query(`SELECT * FROM private_core.stock_ledger WHERE item_id LIKE 'TEST-LW-%'`)).rows, null, 2));
fs.writeFileSync(`${snap}/balances.json`, JSON.stringify(
  (await pool.query(`SELECT * FROM private_core.current_balances WHERE item_id LIKE 'TEST-LW-%'`)).rows, null, 2));

await pool.query('BEGIN');
await pool.query(`DELETE FROM private_core.stock_ledger WHERE item_id LIKE 'TEST-LW-%'`);
await pool.query(`DELETE FROM private_core.current_balances WHERE item_id LIKE 'TEST-LW-%' AND calculated_on_hand < 0`);
// Maintenance log
await pool.query(`
  INSERT INTO private_core.maintenance_log (action, performed_at, details)
  VALUES ('test_lw_synthetic_cleanup', now(), $1)
`, [JSON.stringify({ ledger_deleted: ledgerCount, balances_deleted: negCount, snapshot_path: snap })]);
await pool.query('COMMIT');

// Rebuild projection
await pool.query(`SELECT private_core.rebuild_verifier()`);
console.log('cleanup committed; rebuild_verifier() called');
```

(If `private_core.maintenance_log` does not yet exist, this task includes a small migration adding it — `0148_maintenance_log.sql`.)

- [ ] **Step 1: Run dry-run, confirm shape**

```bash
node gt-factory-os/scripts/cleanup_test_lw_synthetic.mjs
```

Expected: `shape verified: 9 ledger rows + 5 neg balances` then `dry-run, exiting`.

- [ ] **Step 2: Apply**

```bash
node gt-factory-os/scripts/cleanup_test_lw_synthetic.mjs --apply
```

Expected: `cleanup committed; rebuild_verifier() called`.

- [ ] **Step 3: Verify via audit**

```bash
python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" --quiet
```

Expected: phantoms=0, negative-balance=0 in the JSON sidecar; the negative-balance section in the markdown shows the ✅ line.

- [ ] **Step 4: AT.8 explicit test — synthetic count drift**

Manually insert one extra `TEST-LW-*` row before the script. Run it. Expected: exits 2 with `REFUSING:` message; nothing touched. Remove the synthetic row afterwards.

- [ ] **Step 5: Commit**

```bash
git add gt-factory-os/scripts/cleanup_test_lw_synthetic.mjs \
        gt-factory-os/db/migrations/0148_maintenance_log.sql
git commit -m "chore(stock): hard-delete 9 TEST-LW synthetic ledger rows + 5 neg balances

Strict scope per Tom Q4 2026-05-06: exactly 9 stock_ledger + 5
negative-balance current_balances rows, all TEST-LW-* prefixed.
Pre-flight count guard refuses to proceed if shape drifts. Snapshot
written to .snapshots/. Maintenance log row added. rebuild_verifier()
called immediately after.

AT.8 verified manually (synthetic count drift refused).

Plan chunk 6 task 6.1."
```

---

## Chunk 7: 30-Day Backfill CLI

**Outcome:** A standalone admin script replays the chain over the last 30 days of mirror history, producing the ledger rows that should have been posted while the bridge was off. Idempotent on `source_event_id`. Internal-only — no Shopify writes.

### Task 7.1 — Backfill script

**Files:**
- Create: `gt-factory-os/scripts/backfill_lionwheel_pickup_chain.mjs`

The script:
1. Calls the same `reconcilePickupAt()` function from chunk 3 with a `windowStart = now - 30d`.
2. Sets a script-local config `{ shopify_writes_enabled: false }`.
3. Writes a reconciliation report `gt-factory-os/.audits/backfill_<ts>/report.md` showing rows posted, exceptions emitted, and counts by movement_type.

Key code:

```javascript
// gt-factory-os/scripts/backfill_lionwheel_pickup_chain.mjs
import 'dotenv/config';
import { reconcilePickupAt } from '../api/src/integrations/lionwheel/reconciliation.js';

const dryRun = !process.argv.includes('--apply');
const result = await reconcilePickupAt(pool, {
  fg_out_bridge_enabled: true, // backfill explicitly opens the gate locally
  windowStart: new Date(Date.now() - 30 * 24 * 3600 * 1000),
  windowEnd: new Date(),
  dryRun,
  shopifyWritesEnabled: false,
});
console.log(JSON.stringify(result, null, 2));
```

- [ ] **AT.9 verification step:** in the test run, snoop `result.shopify_writes` and assert it's empty/zero. Acceptance test #9 covered.

- [ ] After running for real: re-run the audit, expect coverage > 80% (some early-window tasks may have been retired before pickup_at populated).

---

## Chunk 8: Shopify FG Cutover (flag + mutex + shadow)

**Outcome:** A single, gated, mutex-protected Shopify FG writer in Factory OS. Default OFF. Shadow-mode for 2-3 days produces a divergence report against current Shopify truth; cutover lifts the flag only after divergence ≤0.5%.

### Task 8.1 — `ENABLE_SHOPIFY_FG_WRITE` env flag

**Files:**
- Modify: `gt-factory-os/api/src/server.ts` (or wherever the Shopify writer is instantiated)
- Test: `gt-factory-os/api/test/shopify_fg_write_gate.test.ts` (covers AT.10)

Single read of `process.env.ENABLE_SHOPIFY_FG_WRITE === 'true'` at boot. Every write call checks the gate first. False → log + skip + emit a `shopify_fg_write_blocked_by_gate` exception (rate-limited).

- [ ] AT.10 test: set env to `false`, attempt write, assert no HTTP request to Shopify and one exception logged.

### Task 8.2 — Active-writer mutex via `system_locks`

**Files:**
- Create: `gt-factory-os/api/src/integrations/shopify/writer_lock.ts`
- Test: `gt-factory-os/api/test/shopify_fg_writer_lock.test.ts` (covers AT.11)

Before each batch of Shopify writes, the writer:
1. INSERTs a row into `private_core.system_locks` with `lock_name='shopify_fg_writer'`, `holder_name=process.env.RAILWAY_DEPLOYMENT_ID`, `expires_at=now()+5min`. ON CONFLICT — fail with explicit message.
2. Performs writes.
3. DELETEs its row in a `finally` block.

If `system_locks` already has a non-expired `shopify_fg_writer` row owned by anyone else (e.g. a `daily-inventory-agent` instance), the writer refuses. AT.11 covered.

### Task 8.3 — Shadow-mode divergence report

**Files:**
- Create: `gt-factory-os/scripts/shopify_fg_shadow_report.mjs`

For each FG item with `mapping_status='active'` AND `is_stock_managed=true`: read `current_balances.calculated_on_hand`, multiply by `internal_units_per_shopify_unit`, compare to live Shopify on-hand. Output a CSV. Run twice a day for 2-3 operating days. Cutover only when median absolute divergence ≤ 0.5 units AND no item with abs divergence > 5.

### Task 8.4 — Set-from-projection writer (not event-by-event)

**Files:**
- Create: `gt-factory-os/api/src/integrations/shopify/fg_set_from_projection.ts`

Tom Q6 #5: prefer absolute set, not delta. The writer:
1. Reads `current_balances` for every Shopify-mapped item.
2. Computes Shopify-units = `calculated_on_hand × internal_units_per_shopify_unit` (rounded to integer).
3. Calls `POST /inventory_levels/set.json` once per item with the computed value.
4. Logs to `shopify_fg_sync_history` with reconciliation metadata.

Rollback path: setting `ENABLE_SHOPIFY_FG_WRITE=false` immediately stops new writes; Shopify retains last-set values.

### Task 8.5 — Strip FG writes from daily-inventory-agent

**Files:**
- Modify: `C:/Users/tomw2/.claude/skills/daily-inventory-agent/SKILL.md`
- Modify: `C:/Users/tomw2/.claude/skills/daily-inventory-agent/scripts/...` (FG-writing functions)

After Factory OS runs cleanly for 7 days with `ENABLE_SHOPIFY_FG_WRITE=true`, **strip** the Shopify FG-write capability from `daily-inventory-agent`. Replace with read-only verification calls. Document in the skill description: "FG inventory writes are owned by gt-factory-os; this skill no longer writes Shopify FG."

---

## Chunk 9: End-to-end audit verification + sign-off

**Outcome:** A single audit run shows ≥99% top-line, zero phantoms, zero unmatched-shipments-on-negative-balance, and PASS verdict. Documented as `PRODUCTION/docs/superpowers/specs/2026-05-06-stock-event-perfect-flow-signoff.md`.

### Task 9.1 — Full audit run

```bash
python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" \
  --days 7 --include-raw --threshold 99
```

Expected exit code: 0. Top-line ≥99.0%. Verdict: `PASS`.

If verdict is anything else, capture the gap, file an issue, and DO NOT mark the plan complete. Return to the failing chunk.

### Task 9.2 — Sign-off document

**Files:**
- Create: `PRODUCTION/docs/superpowers/specs/2026-05-06-stock-event-perfect-flow-signoff.md`

Records:
1. Final audit run path + top-line + verdict.
2. All 11 acceptance tests with the test path + commit SHA where each one is verified.
3. Cutover-state checklist (ENABLE_SHOPIFY_FG_WRITE timestamp, daily-inventory-agent strip-down date).
4. Rollback procedure (set flag false; revert chunk 3 if pickup-trigger turns out wrong).
5. Open follow-ups (if any): items in `mapping_status='pending_item_creation'` awaiting Tom; items in `missing_internal_item` awaiting master data.

### Task 9.3 — Update CURRENT_STATE.md

Mark the "LionWheel pick-reconciliation chain repair corridor" as **CLOSED** with date and audit-evidence link. Per CLAUDE.md authority rules, this is the only place runtime status is restated.

### Task 9.4 — Final commit + PR

```bash
git add PRODUCTION/docs/superpowers/specs/2026-05-06-stock-event-perfect-flow-signoff.md \
        PRODUCTION/CURRENT_STATE.md
git commit -m "docs(plan): close stock-event-perfect-flow with audit ≥99%

Audit run: <path>, top-line=<X>%, verdict=PASS.
Acceptance tests 1-11: all green. See sign-off for evidence map.

Cutover:
  ENABLE_SHOPIFY_FG_WRITE=true on Railway since <ts>
  daily-inventory-agent FG-write capability removed in commit <sha>

Rollback: flip ENABLE_SHOPIFY_FG_WRITE=false; behavior reverts to
Postgres-internal-only with no Shopify writes. Chain itself remains
green.

CURRENT_STATE.md: LionWheel pick-reconciliation chain repair corridor
CLOSED <date>."
```

---

## Plan Review Checklist (before execution starts)

- [ ] Chunk-3 §3.0 quantity-handling decision (Option A vs B) reviewed and confirmed by Tom.
- [ ] Chunk 5 worksheet has Tom's `decision` column filled before Task 5.3 runs.
- [ ] Chunk 8 cutover is gated on Chunk 9 task 9.1's PASS verdict — never run 8.4 (`ENABLE_SHOPIFY_FG_WRITE=true`) before 9.1 succeeds.
- [ ] All commits go to a feature branch / worktree, not directly to `main`. PR review before merge.
- [ ] After each chunk, re-run `python evals/grade.py <iter>` of the audit skill to confirm no regression on the eval set.

## Rollback procedure (per chunk)

| Chunk | Rollback |
|---|---|
| 1 | `BEGIN; ALTER TABLE … DROP COLUMN …; DROP TYPE …; DROP TABLE system_locks; COMMIT;` — pure additive, safe. |
| 2 | Revert poller commit; mirror's pickup_at column stays populated (no harm). |
| 3 | Set `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false`. Posted ledger rows from this branch remain (append-only ledger by design); manual reversal via WASTE_REVERSAL pattern if rows are unwanted. |
| 4 | Revert script + chain commits; mapping_status backfill rows can stay (no harm) or be reset to `'active'` for affected aliases. |
| 5 | Revert worksheet application; the `internal_units_per_shopify_unit` column defaults to 1.0 again. |
| 6 | Restore from `.snapshots/test_lw_cleanup_*` directory. |
| 7 | Backfill produced only ledger rows; same as chunk 3 rollback. |
| 8 | `ENABLE_SHOPIFY_FG_WRITE=false`; daily-inventory-agent's FG-write capability is reinstated only by reverting its commit. |
| 9 | Sign-off doc deletion; CURRENT_STATE entry reverts. |

---

---

## Phase 2 — All event classes continuous (chunks 10-15, stubs)

> **Stubs only.** Full TDD writeup lands after Tom answers Q-A4 (operator portal readiness) and Q-A5 (priority order). Every chunk below has its outcome locked, but task-level steps wait on those answers.

### Chunk 10: Goods Receipt continuous chain

**Outcome:** Every supplier delivery — RM or FG (BOUGHT_FINISHED) — flows from operator → portal GR form → `goods_receipts` record → `stock_ledger GR_POSTED` → `current_balances`. Both PO-linked and PO-less paths covered. GR_REVERSAL works. Source PO's `received_qty` increments correctly.

**Acceptance:** AT.14, AT.15, AT.16.

**Key open questions before detail:**
- How does Tom currently log GR (paper, Excel, supplier email)? The portal needs the lowest-friction path.
- Supplier identity normalization — `suppliers` table is the source of truth; importer for GR form should auto-fill from PO when linked.
- PO matching tolerance — exact qty? ±1 unit? ±5%?

**Pre-existing artifacts (from CURRENT_STATE.md):** GR handler runtime exists at `gt-factory-os/api/src/goods-receipts/handler.ts`; node:test passes; preflight script `verify_gr_preflight.ts` 14/14 probes pass. Chunk 10 wires this into daily ops, not building new runtime.

### Chunk 11: Waste / Adjustment continuous chain

**Outcome:** Operator-reported waste (RM/FG) and corrective adjustments flow through the portal's Waste/Adjustment form. Auto-post for small deltas; admin-approved post for large. WASTE_REVERSAL is admin-gated.

**Acceptance:** AT.17, AT.18, AT.19.

**Pre-existing artifacts:** Waste/Adjustment runtime is `RUNTIME_READY` per CURRENT_STATE (signal emitted 2026-04-17). 33/33 pgTAP green; HTTP smoke matrix already covers auth + auto-post + idempotent replay + 2 pending categories + role-gate + freeze-guard. Chunk 11 = operator workflow handoff + audit cross-check, not new runtime.

### Chunk 12: Physical Count ongoing workflow

**Outcome:** Recurring monthly counts produce deterministic `balance_anchors_history` rows. Spot counts (per-item, between full counts) are first-class. Bulk-import path from chunk 0 is reused for monthly counts.

**Acceptance:** AT.20, AT.21.

**Pre-existing artifacts:** Physical Count runtime is `RUNTIME_READY` per CURRENT_STATE (signal emitted 2026-04-17). 31/31 pgTAP + 18+1 HTTP matrix green. Chunk 12 = monthly cadence + audit visibility, not new runtime.

### Chunk 13: Production Actual continuous chain

**Outcome:** Daily production reports produce correct `PRODUCTION_OUTPUT + PRODUCTION_SCRAP + PRODUCTION_CONSUMPTION` rows from the pinned two-head BOM. Cost rollup matches manual reconciliation on a known fixture.

**Acceptance:** AT.22, AT.23, AT.24, AT.25.

**Pre-existing artifacts:** Production Actual + two-head BOM repair landed 2026-05-02 per CURRENT_STATE (signal #31). 6 tranches landed in one day; 42/50 post-deploy submissions exhibited two-head explosion signature; rebuild_verifier=0. Chunk 13 = daily-cadence audit + drift alerting on top of the existing runtime.

### Chunk 14: Mass-balance Layer 5 in the audit

**Outcome:** The `stock-event-accuracy-audit` skill grows a 5th layer that solves the mass-balance equation per item over the audit window. Top-line accuracy formula updates to weight all 5 layers. Mass-balance failure surfaces named items + signed deltas.

**Acceptance:** AT.26.

**Implementation sketch:**
- New module `compute_layer5_mass_balance.py` in the skill's `scripts/` dir.
- Per item over [window_start, window_end]:
  - `opening = balance_anchors_current.anchor_qty WHERE anchor_at <= window_start ORDER BY anchor_at DESC LIMIT 1`
  - `Σ(GR) = sum of qty_delta where movement_type IN ('GR_POSTED','GR_REVERSAL')`
  - `Σ(WASTE) = sum where movement_type IN ('WASTE_POSTED','WASTE_REVERSAL')`
  - `Σ(FG_OUT) = sum where movement_type IN ('FG_OUT_PICK','LIONWHEEL_PICK','LIONWHEEL_UNPICK','LIONWHEEL_PICK_ADJUSTMENT')`
  - `Σ(PROD_OUT) = sum where movement_type IN ('PRODUCTION_OUTPUT','PRODUCTION_OUTPUT_REVERSAL')`
  - `Σ(PROD_SCRAP) = sum where movement_type IN ('PRODUCTION_SCRAP','PRODUCTION_SCRAP_REVERSAL')`
  - `Σ(PROD_CONS) = sum where movement_type IN ('PRODUCTION_CONSUMPTION','PRODUCTION_CONSUMPTION_REVERSAL')`
  - `Σ(COUNT_ADJ) = sum where movement_type IN ('COUNT_ADJUST','COUNT_ADJUST_REVERSAL')`
  - `expected = opening + Σ(GR) + Σ(PROD_OUT) + Σ(PROD_SCRAP) + Σ(FG_OUT) + Σ(WASTE) + Σ(PROD_CONS) + Σ(COUNT_ADJ)`
    (signs already encoded in qty_delta convention; sum is straightforward)
  - `actual = current_balances.calculated_on_hand`
  - Match if `|expected − actual| ≤ max(0.5, 0.01 × |expected|)`
- Weight: `w5 = 4` (heaviest single layer — this is the holistic invariant).
- New top-line: `(3·L1 + 3·L2 + 1·L3 + 2·L4 + 4·L5) / 13`.

### Chunk 15: Phase 2 sign-off

**Outcome:** Audit ≥99% across all 5 layers. Daily Railway-cron audit run for 7 consecutive days, all PASS. Document at `PRODUCTION/docs/superpowers/specs/2026-05-XX-phase2-signoff.md`.

**Pre-conditions:** chunks 10-14 all merged + verified. Daily audit cron live (chunk 14 task includes setup).

---

## Phase 3 — Decommission (chunk 16, stub)

### Chunk 16: Excel→read-only + daily-inventory-agent strip-down

**Outcome:** gt-factory-os is the single source of stock truth. Excel master is exported nightly (read-only artifact). The `daily-inventory-agent` skill's FG-write code paths are deleted, not just disabled. Audit cron has been stable for 7+ days.

**Acceptance:** AT.27, AT.28.

**Tasks (high-level):**
- Strip `daily-inventory-agent/scripts/sync_shopify.py` (or equivalent) of any POST/PUT to Shopify inventory endpoints. Replace with read-only verification mode that compares Shopify on-hand to gt-factory-os projection and emits a divergence report.
- Update `daily-inventory-agent/SKILL.md` description: "FG inventory writes are owned by gt-factory-os; this skill verifies and reports divergence only."
- Convert Excel master writes to a nightly read-only export from gt-factory-os (`scripts/export_excel_master.py`).
- Final cutover: set `ENABLE_SHOPIFY_FG_WRITE=true` on Railway. Document the date in `system_state[shopify_writer_cutover_at]`.

---

**End of plan.** Total: 16 chunks across 3 phases · 28 acceptance tests · all six workstreams covered (LionWheel + Shopify + GR + Waste + Count + Production) · daily-cron audit closes the loop · Phase 0 starts TODAY.
