# Integration Freshness / Failure-Surface Requirements Spec

**Owner:** W4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Kind:** requirements-only. No schema DDL, no migration SQL, no runtime code, no handler implementations.
**Authored:** 2026-04-23 by executor-w4 (W4 rolling backlog item 4 — final W4 backlog item).
**FR1 migration directory state at write time:** 76 migrations present; latest file `0076_change_log_user_actions.sql` (mtime 2026-04-23 18:04). No migration number is referenced in this spec; the FR1/FR2 bracket applied per EXECUTION_POLICY.md.

**Evidence consumed (all verified from source — no invented field names):**
- `supabase/functions/factory_os_jobs/index.ts` — PRODUCERS array (lines ~315–325): confirmed producer literals, `warn_min`, `crit_min`, `exception_category` per producer; confirmed `emitException` categories per integration; confirmed `checkBreakGlass` query pattern
- `db/migrations/0017_v_integration_freshness.sql` — initial view definition (6 producers); confirmed 8-column contract
- `db/migrations/0027_v_integration_freshness_forecast_publication.sql` — final view definition (7 producers); confirmed all column names: `producer`, `latest_success_at`, `latest_attempt_at`, `latest_failure_at`, `warning_threshold_minutes`, `critical_threshold_minutes`, `current_state`, `age_minutes`; confirmed `current_state` enum: `'fresh'`, `'warning'`, `'critical'`, `'never_ran'`
- `db/migrations/0028_break_glass_function.sql` — confirmed `private_core.is_break_glass()` returns boolean; `private_core.break_glass_reason()` returns text; flags `global_readonly` and `jobs_paused` in `private_core.feature_flags`
- `db/migrations/0006_jobs_runs_integration_runs.sql` — confirmed `job_runs` columns: `run_id`, `job_name`, `started_at`, `ended_at`, `status`, `error`, `output_summary`; confirmed `job_runs.status` values include `'succeeded'`, `'failed'`, `'aborted'`, `'skipped'`, `'running'`; confirmed `integration_runs` columns: `integration_run_id`, `job_run_id`, `integration_name`, `last_http_status`, `last_error`, `cursor_info`, `created_at`
- `db/migrations/0010_exceptions.sql` — confirmed `private_core.exceptions` columns: `exception_id`, `category`, `severity` (CHECK: `info/warning/critical`), `status` (CHECK: `open/acknowledged/resolved/auto_resolved`), `created_at`, `resolved_at`, `dedupe_key`
- `db/migrations/0001_domains_and_schemas.sql` — confirmed `private_core.feature_flags` columns: `flag_key`, `enabled`, `description`; confirmed `updated_at` trigger `trg_feature_flags_touch_updated_at` exists implying an `updated_at` column (exact column name UNRESOLVED-IF-5)
- `CURRENT_STATE.md` — RUNTIME_READY(LionWheel), RUNTIME_READY(Shopify), RUNTIME_READY(GreenInvoice), RUNTIME_READY(freshness_check) emitted; dashboard tile DR-10 pending
- `docs/w4/dashboard-read-model-requirements.md` (Loop 13, W4 backlog item 3) — confirmed `fetchIntegrationFreshness()` returns `pending_tranche_i`; confirmed DR-10 portal type `IntegrationFreshnessRow` uses `last_success_at` and `state`
- `.claude/state/runtime_ready.json` — confirmed integration RUNTIME_READY signals

**Locked upstream decisions honored (CLAUDE.md):**
- Dashboard and Excel consume curated read models only. No direct table access from the browser.
- API is the permission boundary.
- LionWheel is authoritative for open orders / shipments.
- Shopify is a sync target; platform wins on disagreement.
- Green Invoice feeds price evidence only; does not auto-update prices without validation.
- Prefer clear failure over silent drift.
- Break-glass (jobs_paused=true) causes integration crons to skip-not-queue.

---

## 1. Current freshness state

### 1.1 What the freshness_check cron checks

The `freshness_check` cron runs every 10 minutes (`*/10 * * * *`, confirmed migration `0032`). It iterates over every registered producer in the `PRODUCERS` array (confirmed `index.ts` lines ~315–325) and computes per-producer age by reading `private_core.job_runs` for most producers, and `private_core.forecast_versions` for the `forecast.publication` producer.

**Confirmed PRODUCERS array (source: `index.ts`):**

| Producer literal | warn_min | crit_min | exception_category |
|---|---|---|---|
| `integration.lionwheel` | 30 | 120 | `lionwheel_stale` |
| `integration.shopify` | 30 | 120 | `shopify_stale` |
| `integration.green_invoice` | 120 | 240 | `gi_stale` |
| `job.rebuild_verifier` | 1560 | 1800 | `rebuild_stale` |
| `job.export.nightly` | 1560 | 1800 | `export_stale` |
| `forecast.publication` | 10080 | 20160 | `forecast_stale` |
| `freshness.heartbeat` | 10 | 25 | `freshness_heartbeat_stale` |

**Note on `freshness.heartbeat`:** This producer exists in the PRODUCERS array for the self-silence detection path — the freshness_check cron uses it to prove its own liveness. It is NOT included in `api_read.v_integration_freshness` (which has exactly 7 producers: the 6 non-heartbeat integration/job producers plus `forecast.publication`). The heartbeat producer is an internal safety mechanism, not a dashboard-surfaced integration. It MUST NOT appear in the dashboard freshness grid.

### 1.2 Where freshness data is stored

Freshness state for dashboard consumption is held in the view `api_read.v_integration_freshness` (confirmed `db/migrations/0017` and `0027`). This view computes per-producer state from:

- `private_core.job_runs` — for all producers except `forecast.publication`; reads `MAX(started_at) WHERE status='succeeded'` as `latest_success_at`
- `private_core.forecast_versions` — for `forecast.publication` only; reads `MAX(published_at) WHERE status='published' AND site_id='GT-MAIN'`
- `private_core.planning_policy` — thresholds are read parametrically via policy keys `freshness.<producer>.warning_minutes` / `freshness.<producer>.critical_minutes` (per migration `0027` comment §invariants)

The view is the correct and sole source for the dashboard endpoint. The `integration_runs` table (confirmed in migration `0006`) is NOT used by the view; it records per-HTTP-call metadata for audit purposes.

### 1.3 Exception categories emitted by freshness_check

For each producer, the freshness_check cron emits or promotes an exception using the `exception_category` value as the `category` field in `private_core.exceptions`. The `dedupe_key` pattern is `<exception_category>:singleton` (confirmed `index.ts` line ~443). This means at most one open exception per producer exists at any time.

**Severity rules (confirmed from `index.ts`):**
- `current_state = 'never_ran'` → `severity = 'warning'`
- `current_state = 'critical'` → `severity = 'critical'`
- `current_state = 'warning'` → `severity = 'warning'`
- `current_state = 'fresh'` → auto-resolve any existing open exception for that producer

---

## 2. Required backend endpoint

### Endpoint
`GET /api/v1/queries/integration-freshness`

This path is confirmed by the task dispatch and is consistent with the existing `v1/queries/` convention in the API. The portal fetcher `fetchIntegrationFreshness()` in `window2-portal-sandbox/src/features/dashboard/client.ts` currently returns `pending_tranche_i`. Once this endpoint is authored, the client fetcher must be updated to call this path.

### Authentication
Any authenticated role: `operator`, `planner`, `admin`, `viewer`. Unauthenticated requests MUST return HTTP 401.

### Response shape

```typescript
interface IntegrationFreshnessRow {
  integration_name: string;         // maps to v.producer (exact literal from v_integration_freshness)
  last_successful_at: string | null; // maps to v.latest_success_at; ISO-8601 UTC; null if never_ran
  status: "fresh" | "warning" | "critical" | "never_ran"; // maps to v.current_state
  warn_threshold_min: number | null; // maps to v.warning_threshold_minutes; null for forecast.publication when policy not seeded (UNRESOLVED-IF-2)
  crit_threshold_min: number | null; // maps to v.critical_threshold_minutes; same caveat
  open_exception_count: number;     // COUNT of open exceptions for this producer's exception_category
}

interface IntegrationFreshnessResponse {
  rows: IntegrationFreshnessRow[];  // one row per producer in v_integration_freshness (7 rows)
  as_of: string;                    // ISO-8601 UTC timestamp of when the response was computed
}
```

**Field name alignment with portal types.ts:** The prior dashboard spec (Loop 13) used `last_success_at` and `state` in the `IntegrationFreshnessRow` interface (confirmed from `types.ts`). The task dispatch for this spec uses `last_successful_at`, `status`, `warn_threshold_min`, `crit_threshold_min`, and `open_exception_count`. The handler author and W2 portal author must reconcile the portal `types.ts` interface with this response shape before wiring. This is flagged as UNRESOLVED-IF-3 (see §6).

### Source tables and queries

Three sources are required to build this response:

**Source A — `api_read.v_integration_freshness`** (confirmed, migration `0027`):
Provides `producer`, `latest_success_at`, `current_state`, `warning_threshold_minutes`, `critical_threshold_minutes`, `age_minutes`. Query: `SELECT * FROM api_read.v_integration_freshness` (returns exactly 7 rows for the 7 confirmed producers).

**Source B — `private_core.exceptions`** (confirmed, migration `0010`):
Provides `open_exception_count` per integration. For each producer row, count open exceptions whose `category` matches the producer's `exception_category` from the PRODUCERS table above. The query join: `SELECT category, COUNT(*) FROM private_core.exceptions WHERE status = 'open' GROUP BY category`. The handler must map producer literal → exception_category using the confirmed PRODUCERS table in §1.1.

**Source C — `private_core.job_runs`** (confirmed, migration `0006`):
Not needed directly in the response — `api_read.v_integration_freshness` already aggregates from `job_runs` internally. Source C is listed here for completeness to clarify that the endpoint does not need to query `job_runs` separately.

**Source D — `private_core.integration_runs`** (confirmed, migration `0006`):
NOT used by this endpoint. The `integration_runs` table holds per-HTTP-call audit rows. The dashboard freshness endpoint sources from the view only.

### Mapping table: producer → exception_category

The handler must map each `v_integration_freshness.producer` value to the corresponding staleness exception category to count open exceptions. The confirmed mapping (from PRODUCERS array, `index.ts`):

| v_integration_freshness.producer | exception_category for open_exception_count |
|---|---|
| `integration.lionwheel` | `lionwheel_stale` |
| `integration.shopify` | `shopify_stale` |
| `integration.green_invoice` | `gi_stale` |
| `job.rebuild_verifier` | `rebuild_stale` |
| `job.export.nightly` | `export_stale` |
| `job.freshness_check` | UNRESOLVED-IF-4 (see §6): `freshness_check` itself appears as a producer in the view but the freshness_check job does not emit a `freshness_check_stale` exception for its own staleness — it is the self-silence path that detects this via `freshness.heartbeat`. The exception category for `job.freshness_check` staleness in the view context is not explicitly confirmed from source. |
| `forecast.publication` | `forecast_stale` |

### Staleness tolerance
2 minutes (`staleTime: 120_000` ms in TanStack Query). The freshness_check cron fires every 10 minutes; reading the view at 2-minute intervals provides sufficient freshness without redundant polling.

### Role access
All authenticated roles.

---

## 3. Failure surface — what operators and admins must see

### 3.1 Dashboard tile color states

The integration freshness tile (Block 3, Dashboard DR-10) surfaces a grid where each row represents one of the 7 confirmed producers. Each row renders in one of four states:

| State value | Visual color | Label |
|---|---|---|
| `fresh` | Green | "OK" or "Fresh" |
| `warning` | Amber | "Stale" or "Warning" |
| `critical` | Red | "Critical" |
| `never_ran` | Gray (or Amber) | "Never ran" |

The exact label strings are a W2 portal concern (W4 specifies state values, not UI copy). The color-to-state mapping above is the contract.

### 3.2 Stale vs. errored: different failure modes

"Stale" and "errored" are distinct failure modes that must be visually distinguishable:

**Stale** — the integration has not produced a successful run within the threshold window. Cause may be: cron skipped (break-glass), provider API unavailable, network failure, or configuration issue. The `current_state` field in the view captures this. Stale means the last successful run was too long ago — the run may have completed without error but the data is old.

**Errored** — the integration's most recent run attempt failed (HTTP error, auth failure, schema drift). This is derivable from `v_integration_freshness.latest_failure_at > latest_success_at` (i.e., the last attempt failed). If this condition is true, the tile should surface an "errored" indicator (distinct from merely stale). This distinction matters because:
- A stale-but-not-errored state may resolve on the next cron cycle.
- An errored state requires operator investigation.

The `api_read.v_integration_freshness` view exposes `latest_attempt_at` and `latest_failure_at` columns (confirmed). The endpoint MAY include these in the response as optional fields to enable this distinction in the portal. Whether to include them is a handler-author decision. W4 requires that the portal not conflate "stale" and "errored" as a single state. If the handler does not include `latest_failure_at`, this distinction is UNRESOLVED-IF-6 (see §6).

### 3.3 Action available from the tile

The freshness tile MUST NOT contain a fix button. The only action available from the tile is a deep-link to `/admin/integrations`. This is a navigation affordance, not an operational control. The tile must not expose any mutation from the dashboard surface.

The portal's existing exception links on the tile (if any) also route to `/inbox` (the exceptions inbox) rather than performing any action inline.

---

## 4. Exception categories per integration

### 4.1 LionWheel (`integration.lionwheel`)

The following exception categories are confirmed from the Edge Function source (`index.ts`):

| Category | Severity | Trigger | Dedupe key pattern |
|---|---|---|---|
| `lionwheel_stale` | warning or critical | freshness_check: producer not updated within threshold | `lionwheel_stale:singleton` |
| `lionwheel_unknown_sku` | warning | Order line contains SKU not resolvable via `integration_sku_map` | `lionwheel_unknown_sku:<sku>` |
| `lionwheel_auth_failure` | critical | LionWheel API returns 401/403 | UNRESOLVED-IF-7: dedupe key pattern not grep-confirmed for this category |
| `lionwheel_rate_limit_stuck` | critical | Persistent 429 after 3 retries | UNRESOLVED-IF-7: dedupe key pattern not confirmed |
| `lionwheel_capped_window_gap` | info | Poll window capped; coverage gap detected | UNRESOLVED-IF-7: dedupe key pattern not confirmed |
| `lionwheel_schema_drift` | warning | LionWheel response row fails Zod schema validation | UNRESOLVED-IF-7: dedupe key pattern not confirmed |
| `lionwheel_auth_expired` | critical | Auth expired mid-cycle | UNRESOLVED-IF-7: dedupe key pattern not confirmed |

**Portal inbox surface:** The exceptions inbox filters by `category`. Operators can filter to `lionwheel_*` categories. The `/admin/integrations` deep-link is the primary operator action when LionWheel exceptions are open.

### 4.2 Shopify (`integration.shopify`)

The following exception categories are confirmed from `index.ts` (comments at line ~1523–1526 plus `emitException` calls):

| Category | Severity | Trigger | Dedupe key pattern |
|---|---|---|---|
| `shopify_stale` | warning or critical | freshness_check: producer not updated within threshold | `shopify_stale:singleton` |
| `shopify_unmapped_item` | warning | FG item has no approved `integration_sku_map` alias for `source_channel='shopify'` | `shopify_unmapped_item:<item_id>` |
| `shopify_rate_limit_stuck` | critical | Shopify API returns 429 | UNRESOLVED-IF-7: dedupe key not confirmed |
| `shopify_auth_failure` | critical | Shopify API returns 401/403 | UNRESOLVED-IF-7: dedupe key not confirmed |
| `shopify_network_failure` | warning | Non-auth, non-429 HTTP error during push | UNRESOLVED-IF-7: dedupe key not confirmed |
| `shopify_api_version_drift` | info | Shopify response indicates API version changed from `2025-07` | UNRESOLVED-IF-7: dedupe key not confirmed |
| `shopify_drift` | warning or critical | Detected drift between platform stock and Shopify inventory level | UNRESOLVED-IF-7: dedupe key not confirmed |

**Portal inbox surface:** Operators resolve `shopify_unmapped_item` exceptions by approving the corresponding SKU alias via `/admin/sku-aliases` with `source_channel='shopify'` filter. Once approved, the next sync cycle will push that item and auto-resolve the exception.

### 4.3 Green Invoice (`integration.green_invoice`)

The following exception categories are confirmed from `index.ts`:

| Category | Severity | Trigger | Dedupe key pattern |
|---|---|---|---|
| `gi_stale` | warning or critical | freshness_check: producer not updated within threshold | `gi_stale:singleton` |
| `gi_unmapped_supplier` | warning | GI expense row has a `gi_supplier_id` not resolvable to a `suppliers` row via `suppliers.green_invoice_supplier_id` | `gi_unmapped_supplier:<gi_supplier_id>` |
| `gi_non_ils_currency` | warning | GI expense row is in a currency other than ILS | UNRESOLVED-IF-7: dedupe key not confirmed |
| `gi_auth_failure` | critical | GI JWT exchange or API call returns 401/403 | UNRESOLVED-IF-7: dedupe key not confirmed |
| `gi_rate_limit_stuck` | critical | GI API returns 429 persistently | UNRESOLVED-IF-7: dedupe key not confirmed |
| `gi_api_failure` | warning | Non-auth, non-429 error mid-cycle | UNRESOLVED-IF-7: dedupe key not confirmed |

**Portal inbox surface:** Operators resolve `gi_unmapped_supplier` exceptions by mapping the GI supplier ID to a `suppliers` row. The mapping mechanism requires `suppliers.green_invoice_supplier_id` column (migration `0071` confirmed this column exists). The `/admin/integrations` deep-link routes operators to the supplier mapping surface.

### 4.4 Exception categories and the `open_exception_count` field

The `open_exception_count` in the endpoint response (§2) counts **all** open exceptions whose `category` starts with the integration's prefix (`lionwheel_*`, `shopify_*`, `gi_*`). This is a broader count than staleness alone — it captures auth failures, unmapped items, and other operational categories. The handler author must decide whether to count only the staleness exception category or all categories for a given integration. W4 recommendation: count all open exceptions across all categories for the integration (i.e., use `LIKE 'lionwheel_%'` pattern), as this gives operators the most useful operational signal. This is not a locked requirement — the handler author may narrow to staleness-only with a comment.

---

## 5. Break-glass interaction

### 5.1 What happens when jobs_paused=true

When `private_core.feature_flags` has `jobs_paused=true` (or `global_readonly=true`), `private_core.is_break_glass()` returns `true`. The Edge Function checks this at the start of every job dispatch (confirmed `checkBreakGlass()` call in `index.ts`). On a positive result, the job logs an `aborted` row to `private_core.job_runs` with `error = 'break_glass_active:<reason>'` and returns `{skipped: true, reason: 'break_glass'}`.

Consequence for freshness: if all integration crons are skipping due to break-glass, `latest_success_at` values in `api_read.v_integration_freshness` will become stale. Over time, the freshness_check cron would emit staleness exceptions. HOWEVER: the freshness_check cron itself also respects break-glass. When `jobs_paused=true`, the freshness_check cron also returns `{skipped: true}` and logs an `aborted` row. This means **no new staleness exceptions are emitted during break-glass** — the freshness_check is also paused.

### 5.2 The distinction: skipped-due-to-break-glass vs. genuinely failed

The dashboard tile must distinguish these two cases:

| Scenario | `v_integration_freshness.current_state` | `job_runs.status` for most recent row |
|---|---|---|
| Integration ran successfully, data is fresh | `fresh` | `succeeded` |
| Integration has not run recently (stale, no break-glass) | `warning` or `critical` | `succeeded` (but old) or `failed` |
| Integration skipped due to break-glass (jobs_paused) | `warning` or `critical` (because time has passed) | `aborted` |
| Integration never ran | `never_ran` | no rows |

The `current_state` value alone cannot distinguish "stale because break-glass" from "stale because genuine failure". To surface this distinction, the endpoint SHOULD include a `break_glass_active` boolean field:

```typescript
interface IntegrationFreshnessResponse {
  rows: IntegrationFreshnessRow[];
  as_of: string;
  break_glass_active: boolean;  // result of private_core.is_break_glass()
  break_glass_reason: string | null; // result of private_core.break_glass_reason(); null if not active
}
```

When `break_glass_active = true`, the portal tile renders a global "break-glass active — jobs paused" banner above the grid. Individual rows showing `warning` or `critical` state are understood by the operator to be stale because jobs are paused, not because of a genuine failure. This prevents false-alarm escalation.

### 5.3 How to detect break-glass from the endpoint

The break-glass state is queryable from the API via the two confirmed DB functions (migration `0028`):

- `SELECT private_core.is_break_glass() AS active, private_core.break_glass_reason() AS reason`

The handler executes this single query (same pattern used by the Edge Function's `checkBreakGlass()` call). This is a read-only query accessible to any authenticated role.

**The handler must NOT read `private_core.feature_flags` directly** — it must use the canonical `is_break_glass()` function per the migration `0028` comment: "Integration code and job code MUST use this function — never read the flags directly — so a later flag addition only needs to update this function."

### 5.4 Break-glass and the freshness grid rendering

When `break_glass_active = true`:
- The tile renders a prominent amber or red banner: "Break-glass active — jobs paused"
- Individual producer rows with `warning` or `critical` state are displayed with a "paused" indicator rather than an alarm indicator
- The deep-link to `/admin/integrations` is still available (read-only; no fix button)
- The tile does NOT suppress the grid — operators may still want to see which producers are stale and by how much

When `break_glass_active = false`:
- `warning` or `critical` rows indicate genuine staleness or failure
- The operator should investigate via `/admin/integrations` and the exceptions inbox

---

## 6. UNRESOLVED items

Each item below cannot be silently filled without live inspection, schema verification, or a W1 decision. No UNRESOLVED item has been silently defaulted.

- **UNRESOLVED-IF-1: `planning_policy` key naming for freshness thresholds.** The `api_read.v_integration_freshness` view reads thresholds from `private_core.planning_policy` using parametric keys `freshness.<producer>.warning_minutes` / `freshness.<producer>.critical_minutes` (confirmed from migration `0027` comment). The exact key name format (e.g., `freshness.integration.lionwheel.warning_minutes`) has not been confirmed by a live `SELECT policy_key, policy_value FROM private_core.planning_policy WHERE policy_key LIKE 'freshness%'` query. The PRODUCERS array in `index.ts` defines the hardcoded thresholds used by the cron; the view thresholds come from the policy table. Whether the view thresholds match the cron constants, and whether all 7 producers have policy rows seeded, cannot be confirmed without live DB inspection. This label `UNRESOLVED-IF-1` follows the migration `0027` comment naming convention: "UNRESOLVED-IF-1 convention resolved 2026-04-18 in contract §7" — meaning the original naming issue was resolved, but the live seeded values are not confirmed here.

- **UNRESOLVED-IF-2: `warning_threshold_minutes` / `critical_threshold_minutes` null behavior.** If a producer has no corresponding row in `private_core.planning_policy`, the `v_integration_freshness` view may return null for these threshold columns. The response spec above marks these as `number | null`. The handler must handle null thresholds gracefully (do not crash; treat as "threshold unknown").

- **UNRESOLVED-IF-3: Portal `types.ts` field name mismatch.** The existing portal `IntegrationFreshnessRow` interface in `window2-portal-sandbox/src/features/dashboard/types.ts` (confirmed in Loop 13 dashboard spec) uses `last_success_at` and `state`. The endpoint specified here uses `last_successful_at`, `status`, `warn_threshold_min`, `crit_threshold_min`, and `open_exception_count`. Before the portal fetcher can be wired, either: (a) the handler returns `last_success_at` / `state` (matching the existing portal types), or (b) W2 updates `types.ts` to match the richer response shape. This reconciliation is W2 + W1 work; W4 flags the mismatch and does not resolve it.

- **UNRESOLVED-IF-4: Exception category for `job.freshness_check` staleness.** The producer `job.freshness_check` appears in `api_read.v_integration_freshness` as one of the 7 rows. The freshness_check job is the cron that monitors other producers. If the freshness_check cron itself becomes stale, it is detected via the `freshness.heartbeat` producer (which is NOT in the view). The staleness exception category for `job.freshness_check` as a view row is not confirmed in the PRODUCERS array — the PRODUCERS array entry for `job.freshness_check` does not appear (only `freshness.heartbeat` with `exception_category: 'freshness_heartbeat_stale'`). The `open_exception_count` for the `job.freshness_check` view row cannot be determined without confirming whether any exception is emitted with a `job_freshness_check_stale` or similar category. Until confirmed: set `open_exception_count = 0` for the `job.freshness_check` row, and surface this as a known gap.

- **UNRESOLVED-IF-5: `private_core.feature_flags.updated_at` column name.** Migration `0001` confirms a trigger `trg_feature_flags_touch_updated_at` exists, implying an `updated_at` column. However, the exact column name was not grep-confirmed in the migration DDL text. If the dashboard break-glass tile (from the sibling Loop 13 spec, §8) needs `set_at`, it should map to `feature_flags.updated_at`. Until confirmed via `\d private_core.feature_flags` or equivalent, `set_at` in break-glass responses must return null (consistent with UNRESOLVED-DR-5 in the sibling spec).

- **UNRESOLVED-IF-6: `latest_failure_at` inclusion in endpoint response.** The spec recommends the handler include `latest_failure_at` and `latest_attempt_at` from the view to enable the portal to distinguish "stale" from "errored." This is a recommendation, not a lock. If the handler author omits these fields, the portal cannot surface the stale-vs-errored distinction per §3.2. W4 flags this as a gap for the handler author to decide; it does not block the endpoint from functioning.

- **UNRESOLVED-IF-7: Dedupe key patterns for non-staleness exception categories.** The PRODUCERS array confirms the `dedupe_key` pattern for staleness exceptions (`<exception_category>:singleton`). For operational exception categories (`lionwheel_auth_failure`, `shopify_unmapped_item`, `gi_unmapped_supplier`, etc.), the dedupe key patterns vary. `shopify_unmapped_item:<item_id>` and `gi_unmapped_supplier:<gi_supplier_id>` were confirmed in `index.ts`. All other non-staleness dedupe key patterns were not grep-confirmed from source. This does not affect the endpoint response shape but affects the portal inbox's ability to link to specific exception detail pages. W4 marks this for the portal inbox author (W2) to verify from source before building exception deep-links.

---

## 7. FR1/FR2 migration directory bracket

**FR1 (pre-write scan):** Performed immediately before writing this artifact.
- Total migrations: 76
- Latest file: `0076_change_log_user_actions.sql` (mtime 2026-04-23 18:04)
- No migration number is referenced in this spec. No collision risk.

**FR2 (post-write scan):** To be performed immediately after this file is written. If `0077_*.sql` or later appears between FR1 and the write completion, emit `contract_failure` per EXECUTION_POLICY.md §FR1→write→FR2 bracket.

This spec does not name any migration file as a target. The FR1/FR2 bracket is applied as a precaution per policy.
