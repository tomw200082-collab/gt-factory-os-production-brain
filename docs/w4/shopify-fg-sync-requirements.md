# Shopify FG Sync — Contract-Requirements Spec

**Owner:** W4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Kind:** requirements-only. No schema DDL, no migration SQL, no runtime code, no handler implementations.
**Authored:** 2026-04-23 by executor-w4 (W4 rolling backlog item 1).
**Evidence consumed:**
- `CURRENT_STATE.md` (calibrated 2026-04-23) — runtime state, UNRESOLVED items, Shopify signal evidence
- `runtime_ready.json` — `RUNTIME_READY(Shopify)` emitted 2026-04-21T19:05
- `docs/production_endgame_phase_e3_runtime_checkpoint.md` (executor-w1, 2026-04-21) — live smoke evidence, A13 decisions, residuals
- `docs/integrations/shopify_fg_sync_contract.md` (executor-w4, 2026-04-21, commit `71a10cf`) — field-level requirements spec with live API inspection evidence
- `db/migrations/0033_integration_sku_map.sql` — confirmed `integration_sku_map` column names
- `db/migrations/0065_shopify_sync_state.sql` — confirmed `shopify_sync_state` and `shopify_fg_sync_history` column names
- `db/migrations/0062_form_submissions_integration_sku_map_approve.sql` — confirmed `integration_sku_map_approve` form_type

**Locked upstream decisions honored (CLAUDE.md):**
- Shopify is a sync target and commercial boundary only; platform is authoritative on disagreement.
- Shopify is authoritative for nothing operationally critical.
- Platform FG stock is pushed outbound; Shopify is the mirror target.
- Exception-based review for unexplained drift.

---

## Status at time of authoring

`RUNTIME_READY(Shopify)` was emitted 2026-04-21T19:05. The Shopify sync infrastructure is deployed and running on a 15-minute `pg_cron` cadence. **However, all 61 FG items return `write_status='skipped_unmapped'` because there are zero approved `integration_sku_map` rows with `source_channel='shopify'`.** The sync is dormant. This spec defines the full operational requirements the sync must satisfy before it can be declared operationally live.

---

## 1. What stock data is sent to Shopify

### 1.1 Source table

The sync reads `private_core.current_balances` — the synchronously-maintained FG projection table that reflects ledger + anchor state as of the most recent posted event. This is the same table consumed by the planning engine and the nightly export. It is not a materialized view; it is a transactionally maintained projection updated by trigger on every ledger write (confirmed by closed-loop verification 2026-04-23, step 5b).

**Requirement R-S1:** The sync MUST read `private_core.current_balances` and never read `stock_ledger` directly for the per-cycle push quantity. The projection is the authoritative current stock number.

### 1.2 Quantity field and rounding

The quantity field consumed from `current_balances` is `calculated_on_hand` (type `qty_8dp = numeric(24,8)`). Shopify's `inventory_levels/set.json` endpoint requires an integer `available` value.

**Requirement R-S2:** Before pushing to Shopify, the sync MUST apply the zero-clamp floor rule:
```
push_qty = GREATEST(0, FLOOR(calculated_on_hand))
```
This rule is from `shopify_fg_sync_contract.md` §6.3 and was confirmed applied in the deployed runtime (E3 checkpoint §6, decision 6). A negative `calculated_on_hand` produces `push_qty = 0`; the negative on-hand is a platform-side concern and MUST NOT be propagated to Shopify as a negative integer.

**Requirement R-S3:** When `calculated_on_hand < 0` and `push_qty` is therefore clamped to 0, the sync MUST emit a `shopify_negative_on_hand` exception (see §5 for exception definitions). It MUST NOT silently push 0 without surfacing the condition.

### 1.3 Location targeting

GT has exactly one Shopify location. Live-observed `location_id = 54802612384`, `active=true`, `legacy=false`, `country_code=IL` (from `shopify_fg_sync_contract.md` §2.1 probe P4, confirmed in E3 smoke output `shopify_location_id=54802612384`).

**Requirement R-S4:** The sync MUST resolve `location_id` live per cycle from `GET /admin/api/{VERSION}/locations.json` rather than hardcoding the numeric value. The first active location is selected. This is future-proofing against Shopify-side location reconfiguration. (E3 runtime implements this per A13 decision 3, confidence 95%.)

**Requirement R-S5:** If the live-resolved `location_id` changes between cycles, the sync MUST emit a `shopify_location_changed` exception and continue with the newly-resolved value. It MUST NOT silently push to a stale location ID.

### 1.4 Shopify inventory level fields written

The write call targets `POST /admin/api/{VERSION}/inventory_levels/set.json`. Per `shopify_fg_sync_contract.md` §3.4 (live-inspection-evidenced from probe P5 and Shopify Admin API documentation), the body fields are:

| Field | Source | Notes |
|---|---|---|
| `location_id` | Resolved live from `GET /locations.json` per R-S4 | Integer. Single location per GT's configuration. |
| `inventory_item_id` | Resolved from Shopify variant cache per §2 of this spec | Integer. Looked up by matching `integration_sku_map.external_sku` against `variant.sku` in the per-cycle in-memory cache. |
| `available` | `push_qty` computed per R-S2 | Integer. Zero-clamped. Never negative. |

No other fields are written by this sync. Price, variant options, product state, collection membership, and all other Shopify fields are out of scope.

**Requirement R-S6:** A successful sync write for one item means: `POST /admin/api/{VERSION}/inventory_levels/set.json` returned HTTP 2xx with a response body containing `inventory_level.available` equal to the `push_qty` submitted, and the corresponding `shopify_fg_sync_history` row records `write_status='ok'` and the confirmed `shopify_qty_observed` value. A 2xx response without the matching `available` confirmation is treated as a write warning, not a confirmed write.

---

## 2. SKU mapping requirements

### 2.1 Schema facts (verified from migrations)

The mapping table is `private_core.integration_sku_map` (migration 0033). Confirmed column names:

| Column | Type | Notes |
|---|---|---|
| `alias_id` | `uuid` PK | System-generated. |
| `source_channel` | `text` | CHECK: `('lionwheel', 'shopify', 'green_invoice')`. Shopify rows use `source_channel='shopify'`. |
| `external_sku` | `text` | The Shopify `variant.sku` string (e.g., `GT-LUI-FRE-6L`). |
| `item_id` | `text` | FK to `private_core.items(item_id)`. |
| `approval_status` | `text` | CHECK: `('pending', 'approved', 'rejected')`. Only `approved` rows resolve. |
| `created_by_user_id` | `uuid` | FK to `app_users`. Nullable (import-scripted rows). |
| `created_by_snapshot` | `jsonb` | Audit snapshot of creator. |
| `approved_by_user_id` | `uuid` | FK to `app_users`. NULL until approved. |
| `approved_at` | `timestamptz` | NULL until approved. |
| `notes` | `text` | Nullable. |
| `site_id` | `text` | Default `'GT-MAIN'`. |
| `created_at`, `updated_at` | `timestamptz` | Standard audit columns. |

The UNIQUE constraint is on `(source_channel, external_sku)` — one row per (channel, external_sku) pair, ensuring resolver lookups return 0 or 1 row.

The mapping key is `variant.sku` (the human-readable GT-business SKU string). This was Tom-locked 2026-04-21 as default U-MK1. The `inventory_item_id` integer needed for the write call is resolved per cycle from the Shopify variants cache, not stored in this table.

### 2.2 What makes a mapping approved

A mapping row is approved when `approval_status = 'approved'`. The transition from `pending` to `approved` requires:
- A user with `admin` or `planner` role executing the batch-approval action
- The action is submitted via the `integration_sku_map_approve` form_type (migration 0062) through the standard `form_submissions` idempotency envelope
- The approval records `approved_by_user_id` (FK to `app_users`) and `approved_at` timestamp
- The `created_by_snapshot` JSONB captures the approver display name at approval time

The transition from `pending` to `rejected` is also available; `rejected` is terminal and non-resolving.

**Requirement R-M1:** Only rows with `approval_status = 'approved'` resolve in the sync resolver. `pending` rows MUST NOT be silently treated as approved. `rejected` rows MUST NOT be treated as approved.

### 2.3 Behavior for unmapped items

**Requirement R-M2:** When the sync scans FG-eligible items (the 61 items matching `supply_method IN ('BOUGHT_FINISHED','MANUFACTURED') AND status='ACTIVE'`) and finds an item with no `integration_sku_map` row for `source_channel='shopify'` with `approval_status='approved'`:
1. The item is SKIPPED — no Shopify API call is attempted for it.
2. A `shopify_unmapped_item` exception MUST be emitted with dedupe_key `shopify_unmapped_item:<item_id>` (one per item; re-emission is suppressed while the exception remains open).
3. The skip is logged in the `shopify_fg_sync_history` table with `write_status='skipped_unmapped'`.
4. The per-cycle `shopify_sync_state` counters reflect the skipped item in `last_sync_item_count` but NOT in `last_sync_writes_ok`.

**Requirement R-M3:** Skipped items MUST NOT be logged individually in `job_runs.error` — only as an aggregate count in the cycle summary. Noise in the run log from 61 per-item skip entries would obscure genuine errors.

### 2.4 Approval workflow

**Requirement R-M4:** The approval interface for Shopify SKU mappings is the existing `/admin/sku-aliases` portal surface (already live, per E3 checkpoint §6 A13 decision 4). It filters by `source_channel='shopify'`. No separate dedicated approval screen is required for v1.

**Requirement R-M5:** The approval workflow MUST support batch approval — an admin or planner can select multiple pending aliases and approve them in one idempotency-key-guarded submission. Individual row approval MUST also be supported.

**Requirement R-M6:** The approval audit trail MUST be queryable: given a `shopify_unmapped_item` exception for `item_id=X`, an operator MUST be able to trace from the exception to the `integration_sku_map` row and see the full approval history (`approved_by_user_id`, `approved_at`, `created_by_snapshot`).

### 2.5 Exit criterion: "fully mapped"

**Requirement R-M7:** The Shopify FG sync is considered fully mapped when:
- Zero `shopify_unmapped_item` exceptions are open in the Exceptions Inbox
- Every FG-eligible item (`supply_method IN ('BOUGHT_FINISHED','MANUFACTURED') AND status='ACTIVE'`) has exactly one `integration_sku_map` row with `source_channel='shopify'` and `approval_status='approved'`
- The next sync cycle after full mapping shows `last_sync_writes_ok = 61` (or the then-current FG eligible count) and `last_sync_item_count = last_sync_writes_ok` (no unmapped skips)

This is a SQL-verifiable criterion. The current state is 61 items unmapped (all 61 FG-eligible items produce `shopify_unmapped_item` exceptions as of 2026-04-21 smoke run).

---

## 3. Sync cadence and freshness

### 3.1 Cadence

The current deployed cadence is `*/15 * * * *` (every 15 minutes via `pg_cron`, migration 0066). This was Tom-locked as U-C1 default on 2026-04-21.

**Requirement R-C1:** Maximum acceptable staleness for Shopify stock = **30 minutes**. Rationale: the 15-minute cadence leaves one full missed cycle before the staleness threshold is crossed. This gives a one-cycle grace window for transient infrastructure failures without triggering a false-alarm exception.

**Requirement R-C2:** The freshness threshold for the `integration.shopify` freshness producer is:
- `warn_min = 30` (2x cadence — one missed cycle)
- `critical_min = 120` (8x cadence — 8 consecutive missed cycles)

These were Tom-locked as U-F1 defaults on 2026-04-21 and confirmed in the E3 checkpoint freshness producer evidence (`warn_min=30, crit_min=120`).

### 3.2 What "last successful push" means

**Requirement R-C3:** "Last successful push" is defined as the `shopify_sync_state.last_successful_sync_at` timestamp — the cycle-level completion timestamp updated when a cycle completes without fatal error. Specifically:
- A cycle that pushes 0 items because all items are unmapped but completes without API errors or DB errors still counts as a successful cycle (it advances `last_successful_sync_at`)
- A cycle that fails to authenticate, fails to resolve the location, or encounters a fatal DB error does NOT advance `last_successful_sync_at`
- A cycle that pushes some items and fails others (partial success) DOES advance `last_successful_sync_at` (partial success is not a fatal failure; per-item failures surface as individual exceptions)

This definition ensures the freshness watchdog accurately detects true integration outages rather than being triggered by unmapped-item situations or per-item write failures.

### 3.3 Freshness exception

**Requirement R-C4:** When the `freshness_check` job detects `age_minutes > warn_min` for producer `integration.shopify`, it MUST emit a `shopify_stale` exception (severity `warning`). When `age_minutes > critical_min`, the exception MUST escalate to severity `critical`.

**Requirement R-C5:** The freshness exception MUST auto-resolve when the producer emits a new successful cycle heartbeat (`last_successful_sync_at` advances). This was confirmed in E3 smoke evidence (§5.5): pre-existing `shopify_stale` warning auto-resolved on the first successful cycle.

---

## 4. Drift detection

### 4.1 What Shopify drift means

**Requirement R-D1:** Shopify drift for an item is defined as:
```
drift_qty = shopify_qty_observed - platform_qty
drift_pct = drift_qty / platform_qty  (where platform_qty > 0; NULL otherwise)
```
where `shopify_qty_observed` is the value returned by Shopify's `GET /inventory_levels.json` for the item's `inventory_item_id` + `location_id` pair, and `platform_qty` is the `push_qty` that was submitted to Shopify in the immediately preceding write cycle.

These computed columns exist in `private_core.shopify_fg_sync_history` as `drift_qty` and `drift_pct` (GENERATED ALWAYS STORED, confirmed from migration 0065).

### 4.2 Drift thresholds

**Requirement R-D2:** Drift classification:
- `abs(drift_qty) > 0` after rounding: detectable drift — log in history row; no exception unless threshold crossed
- `abs(drift_pct) > 0.20` (20%) OR `abs(drift_qty) > 10 units` (whichever threshold is crossed first): warn-level `shopify_drift` exception
- `abs(drift_pct) > 0.50` (50%) OR `abs(drift_qty) > 50 units`: critical-level `shopify_drift` exception

The 20% warning threshold (`SHOPIFY_DRIFT_CRITICAL_PCT = 0.20`) was Tom-locked as U-R2 default. The absolute-unit thresholds and the critical escalation at 50% are W4 requirements additions for this spec. **These thresholds are UNRESOLVED and require Tom ratification** (see UNRESOLVED section, item DR-1).

### 4.3 How drift is detected

The sync performs a drift-detection pass at the END of each push cycle. The deployed runtime (E3 checkpoint §6, A13 decision 2) implements this as an inline second pass:
1. After the write pass completes, the runtime queries `shopify_fg_sync_history` for rows from the PREVIOUS cycle that have `write_status='ok'` and `shopify_qty_observed IS NULL`
2. For those rows, it reads back `GET /admin/api/{VERSION}/inventory_levels.json?location_ids={loc}&inventory_item_ids={comma-list}&limit=250` chunked by 50 items
3. The returned `available` values are written back to `shopify_fg_sync_history.shopify_qty_observed` on the prior-cycle rows
4. The GENERATED columns `drift_qty` and `drift_pct` are then non-null and queryable for drift analysis

**Requirement R-D3:** Drift detection MUST use the previous cycle's history rows (not the current cycle's) to allow time for Shopify to process the write before comparing. A zero-interval read-back immediately after write would produce false positives on Shopify propagation lag.

**Requirement R-D4:** The drift-detection pass is capped at 500 unobserved rows per cycle (confirmed E3 A13 decision 9). This prevents runaway reads in pathological accumulation scenarios.

### 4.4 Drift exception

**Requirement R-D5:** When drift exceeds threshold (per R-D2), a `shopify_drift` exception MUST be emitted with:
- `category = 'shopify_drift'`
- `dedupe_key = 'shopify_drift:<item_id>:<cycle_date>'` (one per item per day; avoids spam on persistent drift)
- `detail` carrying: `{item_id, inventory_item_id, observed_qty, platform_qty, drift_qty, drift_pct, cycle_at}`
- `severity = 'warning'` for 20%/10-unit threshold; `severity = 'critical'` for 50%/50-unit threshold

### 4.5 Drift resolution

**Requirement R-D6:** Drift MUST NOT trigger an autonomous out-of-cycle push. The normal 15-minute cadence overwrites Shopify on the next cycle. The platform wins; the next write is the correction. (Per `shopify_fg_sync_contract.md` §6.2 R-D1.)

**Requirement R-D7:** Drift exception resolution is performed by the operator acknowledging and resolving via the Exceptions Inbox after the next cycle confirms convergence (i.e., `shopify_qty_observed` on the next drift-detection pass equals `platform_qty`).

**Requirement R-D8:** If drift persists across 3 consecutive cycles (defined as: 3 sequential `shopify_fg_sync_history` rows for the same `item_id` each have `abs(drift_qty) > threshold`), the exception severity MUST escalate from `warning` to `critical`. This indicates the normal push is not converging, which is a structural problem (mapping broken, Shopify override, or push failure).

---

## 5. Error handling and visibility

### 5.1 Per-item error behavior

| Error type | Behavior |
|---|---|
| `write_status='skipped_unmapped'` | No API call. Emit `shopify_unmapped_item` exception (dedupe per item). Log in history. Count in cycle summary as skipped. |
| HTTP 429 (rate limit) | Retry up to 3 times with exponential backoff (`2s, 4s, 8s`). Read `Retry-After` header. On 3rd failure: emit `shopify_rate_limit_stuck` (critical), mark item `write_status='429'`, pause job via feature flag. |
| HTTP 401 / 403 (auth failure) | Emit `shopify_auth_failure` (critical). Pause entire job via feature flag. Do NOT retry. Mark `write_status='auth_fail'`. |
| HTTP 5xx / network timeout | Retry with backoff `1s, 4s, 16s, 60s`. After 4 failures: emit `shopify_network_failure`. Mark `write_status='network_fail'`. Log `x-request-id` response header in exception detail. |
| HTTP 404 / 422 on POST | Shopify-side variant deleted or `inventory_management != 'shopify'`. Emit `shopify_mapping_broken`. Mark `write_status='network_fail'` (v1 per E3 A13 decision 8). Do NOT retry. |
| API version mismatch | `x-shopify-api-version` in response != pinned `2025-07`. Emit `shopify_api_version_drift` (info). Continue with the response. |

**Requirement R-E1:** A per-item failure MUST NOT abort the cycle for other items. The cycle continues and pushes all remaining mapped items. The failed item is recorded in `shopify_fg_sync_history` with its specific `write_status`.

**Requirement R-E2:** A complete cycle failure (auth failure or total network outage preventing ANY item from being pushed) MUST halt the cycle immediately, mark `integration_runs.status='failed'`, and NOT advance `shopify_sync_state.last_successful_sync_at`.

### 5.2 Jobs run table requirements

**Requirement R-E3:** Each sync cycle MUST produce one `job_runs` row with:
- `job_type = 'integration.shopify'`
- `status`: `'succeeded'` | `'failed'` | `'skipped'` (if break-glass or feature flag pause)
- `error`: null on success; error message on failure; `'break_glass_active:jobs_paused'` or `'shopify_push_paused'` on skip
- `started_at`, `completed_at` (wall-clock duration of the full cycle)

**Requirement R-E4:** Each sync cycle MUST produce one `integration_runs` row and update the `shopify_sync_state` singleton with:

| Field | Value |
|---|---|
| `last_sync_at` | Cycle start timestamp (every cycle, regardless of outcome) |
| `last_successful_sync_at` | Cycle completion timestamp (successful cycles only) |
| `last_sync_item_count` | Total FG-eligible items scanned (61 currently) |
| `last_sync_writes_ok` | Items successfully pushed to Shopify this cycle |
| `last_sync_writes_failed` | Items that returned a write error this cycle |
| `lifetime_writes_ok` | Monotonically increasing total successful writes across all cycles |
| `lifetime_writes_failed` | Monotonically increasing total write failures across all cycles |

Note: `last_sync_item_count - last_sync_writes_ok - last_sync_writes_failed` = items skipped (unmapped). This arithmetic identity enables portal display without a dedicated skipped-count column.

**Requirement R-E5:** The per-cycle `shopify_fg_sync_history` table MUST receive one row per FG-eligible item per cycle, regardless of write outcome (including `skipped_unmapped`). These rows are the raw audit trail for drift analysis and exception diagnosis.

### 5.3 Portal admin/integrations view requirements

**Requirement R-V1:** The portal's admin/integrations view (or equivalent integration status surface) MUST display for the Shopify FG sync:

| Display element | Source | Staleness rule |
|---|---|---|
| Last successful sync timestamp | `shopify_sync_state.last_successful_sync_at` | Flag as stale if > 30 minutes ago |
| Items pushed count (last cycle) | `shopify_sync_state.last_sync_writes_ok` | Shown alongside timestamp |
| Items skipped (unmapped) count (last cycle) | `last_sync_item_count - last_sync_writes_ok - last_sync_writes_failed` | If > 0, show link to Exceptions Inbox filtered by `shopify_unmapped_item` |
| Items failed count (last cycle) | `shopify_sync_state.last_sync_writes_failed` | If > 0, show link to Exceptions Inbox filtered by `shopify_*` |
| Integration status badge | Derived: `fresh` / `stale` / `broken` based on `last_successful_sync_at` and open `shopify_auth_failure` exceptions | `broken` if any `shopify_auth_failure` exception is open; `stale` if `last_successful_sync_at` > 30 min; `fresh` otherwise |
| Link to exceptions inbox | Filter: `category LIKE 'shopify_%'` and `status IN ('open','acknowledged')` | Always visible |

**Requirement R-V2:** The staleness state MUST be derived from `shopify_sync_state.last_successful_sync_at` using wall-clock comparison at render time. The portal MUST NOT cache this value for more than 30 seconds (TanStack Query `staleTime` <= 30,000ms for this endpoint).

**Requirement R-V3:** The portal MUST NOT show a "healthy" green badge when `last_successful_sync_at` is null or when any `shopify_auth_failure` exception is open. A null `last_successful_sync_at` means the sync has never completed a successful cycle and MUST surface as `unknown` / `not started`, not as `fresh`.

---

## 6. Production Actual to Shopify propagation chain

### 6.1 The chain

When a Production Actual form is submitted by an operator, the FG stock update reaches Shopify through this chain:

```
PA form submit
  → POST /api/v1/mutations/production-actuals
  → handler: stock_ledger INSERT (production_output row, qty_delta = +output_qty)
  → DB trigger: current_balances UPDATE (synchronous, same transaction)
  → current_balances.calculated_on_hand updated
  → next shopify_fg_sync cron fires (within 0–15 minutes)
  → sync reads current_balances, resolves mapping, pushes to Shopify
  → Shopify inventory_levels.available updated
```

### 6.2 End-to-end latency SLA

**Requirement R-P1:** Maximum end-to-end latency from Production Actual submission to Shopify reflecting the updated FG stock = **30 minutes** (one cron cycle at worst). This is a soft SLA — the cron fires every 15 minutes, so in the median case the update reaches Shopify within 15 minutes. The 30-minute bound accounts for one full cron interval after the PA is submitted.

**Requirement R-P2:** The trigger chain from PA submission to `current_balances` update is synchronous (same DB transaction). There is no async lag in the platform side of the chain — as soon as the PA form handler commits, `current_balances` reflects the update.

### 6.3 What can break this chain

**Requirement R-P3:** The following conditions break or degrade the chain. Each has a detectable signal:

| Failure | Detection signal |
|---|---|
| PA handler fails to commit | 5xx response to the operator; no ledger write; Exceptions Inbox shows exception if the form_submission stays in pending without posting |
| `current_balances` trigger not firing | `rebuild_verifier()` returns non-zero; nightly verifier job detects drift; rebuild_verifier_drift exception fires |
| Shopify cron not firing | `shopify_stale` exception from `freshness_check` (warn at 30 min, critical at 120 min) |
| Shopify push failing per-item | `write_status != 'ok'` in `shopify_fg_sync_history`; `shopify_network_failure` or `shopify_auth_failure` exception |
| Item has no approved mapping | `shopify_unmapped_item` exception; zero writes for that item |
| Break-glass active | `job_runs.error = 'break_glass_active:jobs_paused'`; no write; freshness watchdog will eventually trigger |
| Feature flag `shopify_push_paused=true` | `job_runs.error = 'shopify_push_paused'`; no write; freshness watchdog will eventually trigger |

**Requirement R-P4:** The portal's admin/integrations view MUST surface break-glass and feature-flag pause state so operators can immediately see if the Shopify sync is intentionally paused, rather than diagnosing it as a system failure.

---

## 7. Exit criteria for "Shopify FG sync is operationally live"

The following criteria are observable by Tom without running SQL. All must pass concurrently to declare the Shopify FG sync operationally live.

**EC-1 — Zero unmapped items:** The Exceptions Inbox shows zero open `shopify_unmapped_item` exceptions. (Current state: 61 open. These are the worklist for alias seeding via `/admin/sku-aliases` with `source_channel='shopify'` filter.)

**EC-2 — Recent successful sync:** The `/admin/integrations` view shows `last_successful_sync_at` within the past 30 minutes AND the status badge reads `fresh`.

**EC-3 — Writes confirmed:** The portal shows `last_sync_writes_ok > 0` after the first post-mapping sync cycle. `last_sync_writes_ok` should equal the number of FG-eligible items with approved mappings.

**EC-4 — Test round-trip:** After a test FG stock adjustment (e.g., a Waste/Adjustment or Physical Count on a single FG item), the Shopify `available` value for the corresponding variant updates to the new quantity within 30 minutes (one cron fire).

**EC-5 — No blocking exceptions:** Zero open `shopify_auth_failure`, `shopify_rate_limit_stuck`, or `shopify_mapping_broken` exceptions.

**EC-6 — History audit trail:** The `shopify_fg_sync_history` table shows rows with `write_status='ok'` for all mapped items from at least one completed cycle.

These criteria form a sufficient but not exhaustive definition of operational live-ness. Drift detection (§4) and freshness monitoring (§3) are ongoing operational concerns, not one-time exit gates.

---

## 8. Exception category summary

All exceptions emit via `private_core.exceptions`. The `category` column has no CHECK constraint on live DB (confirmed 2026-04-21 via `pg_constraint` inspection — 0010 invariant E4 leaves `category` free-text). These strings are authored at application layer.

| Category string | Severity | Dedupe key | Trigger |
|---|---|---|---|
| `shopify_unmapped_item` | `warning` | `shopify_unmapped_item:<item_id>` | FG-eligible item has no approved `integration_sku_map` row for `source_channel='shopify'` |
| `shopify_drift` | `warning` / `critical` | `shopify_drift:<item_id>:<cycle_date>` | Drift exceeds threshold (§4.2) |
| `shopify_negative_on_hand` | `warning` | `shopify_negative_on_hand:<item_id>:<cycle_date>` | `current_balances.calculated_on_hand < 0`; push clamped to 0 |
| `shopify_rate_limit_stuck` | `critical` | `shopify_rate_limit_stuck:<cycle_id>` | 3 consecutive 429s on the same POST |
| `shopify_auth_failure` | `critical` | `shopify_auth_failure:<cycle_date>` | HTTP 401 / 403 from Shopify API |
| `shopify_network_failure` | `warning` | `shopify_network_failure:<cycle_id>` | 4 consecutive 5xx on the same POST |
| `shopify_mapping_broken` | `warning` | `shopify_mapping_broken:<inventory_item_id>` | HTTP 404 / 422 on a previously-mapped item's POST |
| `shopify_api_version_drift` | `info` | `shopify_api_version_drift:<cycle_date>` | Response `x-shopify-api-version != '2025-07'` |
| `shopify_stale` | `warning` / `critical` | `integration.shopify.stale` | Freshness watchdog: age > warn_min=30 / crit_min=120 |
| `shopify_location_changed` | `warning` | `shopify_location_changed:<cycle_date>` | Live-resolved `location_id` differs from prior cycle |

---

## 9. Break-glass and pause behavior

**Requirement R-BG1:** The sync MUST check the global break-glass switch before any Shopify API call. If active: write `job_runs` row with `error='break_glass_active:jobs_paused'`; return immediately; do not advance `last_successful_sync_at`.

**Requirement R-BG2:** The sync MUST check `feature_flags.shopify_push_paused` before any Shopify API call. If `true`: write `job_runs` row with `error='shopify_push_paused'`; return immediately; do not advance `last_successful_sync_at`.

**Requirement R-BG3:** Both pause conditions MUST be visible in the portal's admin/integrations view (see §5.3 R-P4). An operator MUST be able to distinguish intentional pause from staleness from broken auth by inspecting the portal alone, without querying the DB directly.

---

## UNRESOLVED items

These items cannot be silently filled. Each is explicitly open.

**DR-1 — Drift escalation thresholds (absolute-unit bounds).** This spec proposes `abs(drift_qty) > 10 units` for warning and `abs(drift_qty) > 50 units` for critical, alongside the Tom-locked 20% percentage threshold. The percentage threshold is locked (U-R2, 2026-04-21). The absolute-unit bounds are W4 additions not yet Tom-ratified. Reason cannot be filled: GT's per-SKU quantity ranges are not known to W4 (a batch-product SKU may have "50 units" as a trivial daily variance; a concentrate SKU may have "1 unit" as a critical signal). Tom must set these bounds based on operational experience with specific SKUs.

**DR-2 — Drift critical escalation on 3 consecutive misses.** Requirement R-D8 specifies that 3 consecutive cycles of above-threshold drift escalate the exception severity to critical. The "3 consecutive cycles" count is a W4 proposal, not Tom-ratified. Reason cannot be filled: this depends on GT's tolerance for unresolved drift before escalation.

**DR-3 — Portal display endpoint for shopify_sync_state.** Requirement R-V1 specifies that the portal reads `shopify_sync_state` fields. The specific API endpoint path that exposes this data (e.g., `/api/v1/queries/admin/integrations/shopify-status`) does not exist in the currently deployed API and has not been observed in a live inspection artifact. The requirement is stated; the implementation endpoint is W1-owned and currently absent. This is flagged as a portal display gap, not an integration gap.

**DR-4 — Shopify cancellation/refund path (inherited UNRESOLVED).** Per `CURRENT_STATE.md` §"Open UNRESOLVED items": "Shopify cancellation / refund path in GT's specific order flow" remains unresolved. The v1 behavior (next push overwrites; `shopify_drift` exception fires) is specified in this document as the default. The UNRESOLVED item is whether a more nuanced reconciliation is needed. Reason cannot be filled: requires sampling cancelled/refunded orders in GT's Shopify tenant (per `shopify_connectivity_probe_evidence.md` §"Next inspection steps").

**DR-5 — `shopify_location_changed` exception handling.** Requirement R-S5 states that a changed `location_id` must emit an exception and continue with the new value. The specific handling after exception emission (whether the cycle continues or halts) is not confirmed by inspection evidence. The E3 runtime does not appear to implement this check explicitly (A13 decision 3 resolves the location live but does not specify behavior on change). Reason cannot be filled: this edge case was not exercised in the E3 smoke run (GT has one location and it has not changed).

---

## Cross-references

- `docs/integrations/shopify_fg_sync_contract.md` (2026-04-21) — field-level contract with live API inspection evidence. This spec extends that contract at the operational-requirements layer.
- `docs/integrations/shopify_boundary_contract.md` (2026-04-16) — higher-level business boundary; locked source-of-truth rule.
- `docs/production_endgame_phase_e3_runtime_checkpoint.md` (2026-04-21) — W1 runtime smoke evidence; A13 decisions; confirmed column names and deployed behavior.
- `db/migrations/0033_integration_sku_map.sql` — `integration_sku_map` table schema (confirmed column names used above).
- `db/migrations/0065_shopify_sync_state.sql` — `shopify_sync_state` + `shopify_fg_sync_history` table schema (confirmed column names used above).
- `db/migrations/0062_form_submissions_integration_sku_map_approve.sql` — `integration_sku_map_approve` form_type.
- `CLAUDE.md` §"Locked decisions — Orders and integrations" + §"Source-of-truth map" — binding upstream rules.
- `CURRENT_STATE.md` §"Open UNRESOLVED items" — cancellation/refund path carried forward as DR-4.

---

**End of spec.**
