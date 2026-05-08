# Dashboard Read-Model Requirements Spec

**Owner:** W4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Kind:** requirements-only. No schema DDL, no migration SQL, no runtime code, no handler implementations.
**Authored:** 2026-04-23 by executor-w4 (W4 rolling backlog item 3).
**FR1 migration directory state at write time:** 75 migrations present; latest file `0075_supplier_items_std_cost.sql` (2026-04-23 16:38). No migration number is referenced in this spec; the FR1/FR2 bracket is applied as a precautionary read per EXECUTION_POLICY.md.

**Evidence consumed:**
- `CURRENT_STATE.md` (calibrated 2026-04-23) — dashboard tile status, UNRESOLVED items, RUNTIME_READY signals
- `EXECUTION_POLICY.md` — W4 rolling-backlog rules
- `window2-portal-sandbox/src/app/(shared)/dashboard/page.tsx` — live dashboard page; exact Signal<T> types, query keys, pending tiles confirmed
- `window2-portal-sandbox/src/features/dashboard/client.ts` — live client fetchers; pending signals identified (fetchBreakGlassState, fetchStockTruth, fetchIntegrationFreshness, fetchRuntimeReadyRegistry)
- `window2-portal-sandbox/src/features/dashboard/types.ts` — TypeScript interface contracts; Signal<T> discriminated union; DR-1 through DR-12 defaults
- `db/migrations/0006_jobs_runs_integration_runs.sql` — confirmed `job_runs` columns: `run_id`, `job_name`, `started_at`, `ended_at`, `status`, `error`, `output_summary`; `integration_runs` columns: `integration_run_id`, `job_run_id`, `integration_name`, `last_http_status`, `last_error`, `cursor_info`, `created_at`
- `db/migrations/0007_ledger.sql` — confirmed `stock_ledger` columns: `movement_id`, `item_id`, `item_type`, `event_at`, `posted_at`, `movement_type`, `qty_delta`, `idempotency_key`, `reported_by_user_id`, `reported_by_snapshot`, `balance_key`, `post_status`
- `db/migrations/0008_anchors.sql` — confirmed `balance_anchors_current` columns: `anchor_at`, `anchor_qty`, `site_id`, `item_type`, `item_id`, `balance_key`
- `db/migrations/0009_current_balances.sql` — confirmed `current_balances` columns: `calculated_on_hand`, `last_refreshed_at`, `last_event_at`, `item_type`, `item_id`; `rebuild_verifier()` function returns `integer` (drift row count)
- `db/migrations/0010_exceptions.sql` — confirmed `exceptions` columns: `exception_id`, `category`, `severity` (CHECK: info/warning/critical), `status` (CHECK: open/acknowledged/resolved/auto_resolved), `created_at`, `resolved_at`, `dedupe_key`
- `db/migrations/0012_form_tables.sql` — confirmed `form_submissions` columns: `submission_id`, `form_type`, `idempotency_key`, `posted_at`, `posted_by`, `status`; form_type CHECK values confirmed
- `db/migrations/0013_rebuild_verifier_wrapper.sql` — confirmed `private_core.run_rebuild_verifier()` returns JSONB including `drift_count`; `private_core.rebuild_verifier()` returns integer
- `db/migrations/0027_v_integration_freshness_forecast_publication.sql` — confirmed `api_read.v_integration_freshness` columns: `producer`, `latest_success_at`, `latest_attempt_at`, `latest_failure_at`, `warning_threshold_minutes`, `critical_threshold_minutes`, `current_state`, `age_minutes`; 7 producers: `integration.lionwheel`, `integration.shopify`, `integration.green_invoice`, `job.rebuild_verifier`, `job.export.nightly`, `job.freshness_check`, `forecast.publication`
- `db/migrations/0028_break_glass_function.sql` — confirmed `private_core.is_break_glass()` returns boolean; `private_core.break_glass_reason()` returns text; state stored in `private_core.feature_flags` (columns: `flag_key`, `enabled`); relevant flags: `global_readonly`, `jobs_paused`
- `db/migrations/0060_production_actual.sql` — confirmed `production_actual_submit` is a valid `form_submissions.form_type` value (added in migration 0060)
- `db/migrations/0001_domains_and_schemas.sql` — confirmed `feature_flags` columns: `flag_key`, `enabled`, `description`

**Locked upstream decisions honored (CLAUDE.md):**
- Dashboard and Excel consume curated read models only. No direct table access from the browser.
- Database is authoritative for master data, stock events, stock projections, exceptions, audit trails.
- API is the permission boundary.
- Portal does not talk directly to core operational tables.
- Prefer clear failure over silent drift.

---

## 1. Purpose and authority

This spec defines the read-model contracts that the dashboard control tower (`/dashboard`) must consume for its seven signal panels. The dashboard is a read-only surface; it authors no state. Its purpose is to surface operational health — stock truth, integration freshness, jobs status, planning run state, forecast state, break-glass state, and form authorization state — to any authenticated operator, planner, admin, or viewer. This spec exists because four of the seven dashboard panels currently render `pending_tranche_i` placeholders (as confirmed in `client.ts` and the live portal page), meaning their backend endpoints have not been authored. The two KPI fields (runs-today and last-movement) are also backend-blocked. This document specifies the read-model shape, data source, staleness rules, and caching behavior required before each pending tile can be wired and those placeholder states retired.

---

## 2. Tile inventory

The following table covers all seven signal blocks rendered by the dashboard page, plus the two sub-KPIs that are backend-blocked. The "current status" reflects the state confirmed in `client.ts` at time of authoring.

| # | Tile / Signal | Block name in page.tsx | Current status | Data source | Staleness tolerance | Notes |
|---|---|---|---|---|---|---|
| 1 | Inbox total + critical exceptions | Block 1 (top row) | **LIVE** — reads `["inbox","all_rows"]` cache (Tranche B); renders unavailable if cache cold | `private_core.exceptions` via `/api/exceptions` (Tranche B) | 30 s per DR-1; stale if cache cold | Reuses Tranche B cache; no duplicate fetch |
| 2 | Latest planning run | Block 1 (top row) | **LIVE** — reads `/api/planning/runs?status=completed&limit=1` | `private_core.planning_runs` | 30 s | Fields: `run_id`, `executed_at`, `status`, `summary.exceptions_count` |
| 3 | Break-glass state | Block 1 (top row) | **PENDING** — `fetchBreakGlassState()` returns `pending_tranche_i` | `private_core.feature_flags` via `private_core.is_break_glass()` + `private_core.break_glass_reason()` | 30 s | See §8 for full contract |
| 4 | Rebuild verifier + anchors | Block 2 (stock truth) | **PENDING** — `fetchStockTruth()` returns `pending_tranche_i` | `private_core.rebuild_verifier()`, `private_core.balance_anchors_current` | 5 min acceptable (nightly job; on-demand refresh not required) | See §7 for full contract |
| 5 | Integration freshness grid | Block 3 (integrations) | **PENDING** — `fetchIntegrationFreshness()` returns `pending_tranche_i` | `api_read.v_integration_freshness` | 2 min | See §6 for full contract |
| 6 | Jobs 24h health | Block 4 (jobs) | **LIVE** — reads `/api/admin/jobs` (Loop 5 tile) | `private_core.job_runs` via `/api/admin/jobs` | 30 s per DR-1 | Aggregates `run_count_24h`, `failed_count_24h`, `skipped_count_24h` |
| 7 | Latest published forecast | Block 5 (forecast) | **LIVE** — reads `/api/forecasts/versions?status=published` | `private_core.forecast_versions` | 30 s | Fields: `version_id`, `cadence`, `horizon_weeks`, `horizon_start_at`, `published_at`, `status` |
| 8 | RUNTIME_READY registry | Block 6 (authorization) | **PENDING** — `fetchRuntimeReadyRegistry()` returns `pending_tranche_i` | UNRESOLVED-DR-1: no DB-backed registry exists; harness file `.claude/state/runtime_ready.json` is the current authoritative source; that file MUST NOT be read at portal runtime | See §5 | See §5 for full contract |
| KPI-A | Runs-today (stock events posted today) | Not yet a tile — backend-blocked | **BLOCKED** | `private_core.form_submissions` (posted_at >= today midnight) | 60 s | See §4 for full contract |
| KPI-B | Last movement timestamp + item | Not yet a tile — backend-blocked | **BLOCKED** | `private_core.stock_ledger` (most recent `event_at`) | 60 s | See §5-last-movement for full contract |

**Tiles 1, 2, 6, 7 are live.** Tiles 3, 4, 5, 8 and KPI-A, KPI-B are the deliverable of Tranche I backend work. This spec defines the contracts for all pending items.

---

## 3. Global read-model conventions

The following conventions apply to all pending endpoints.

**3.1 Endpoint path convention.** Suggested path: `GET /api/v1/queries/dashboard/<tile-name>`. This is a suggestion; the actual path is determined by the API handler author (W1). The portal proxy path is determined by W2. W4 is specifying the logical read contract, not the URL string.

**3.2 Authentication.** All dashboard reads are accessible to any authenticated role: `operator`, `planner`, `admin`, `viewer`. No role restriction on reads. The API handler MUST still verify that the session is authenticated (reject 401 on missing/invalid token).

**3.3 Response envelope.** Consistent with existing dashboard endpoints: a flat JSON object containing the fields specified per-tile. No pagination is required for any dashboard endpoint. Error responses follow the existing API error shape.

**3.4 Caching.** Per DR-1 (Tom-locked 2026-04-21): client-side `staleTime = 30_000 ms` for all dashboard signals. No server-side cache layer is required. The endpoint may be called on every 30-second refocus event. Exceptions: the stock truth endpoint (§7) has a 5-minute suggested staleTime given the nightly job cadence; the freshness grid (§6) has a 2-minute suggested staleTime.

**3.5 The Signal<T> discriminated union.** The portal's `client.ts` returns `Signal<T>` from every fetcher. The "ok" path is populated when the endpoint returns a well-formed response. The "unavailable" path fires on HTTP errors. The "pending_tranche_i" path fires when no endpoint exists. Once Tranche I endpoints are authored, the `pending_tranche_i` return in the client fetchers should be replaced with live GET calls; the "ok"/"unavailable" branches already handle rendering.

---

## 4. Runs-today contract (KPI-A)

### Endpoint
`GET /api/v1/queries/dashboard/runs-today` (suggested)

### Purpose
Count of stock events successfully posted today — specifically, `form_submissions` rows where `posted_at >= midnight of the current day in the site timezone` and `status = 'posted'`. This KPI answers the question "how many stock operations have been recorded today?"

### Included form_types
The count MUST include all stock-affecting form types. From confirmed migration evidence, the stock-affecting types in `form_submissions.form_type` are:

- `goods_receipt`
- `waste_adjustment`
- `physical_count`
- `production_actual_submit`

Non-stock form types (`forecast_save`, `forecast_publish`, `forecast_revise`, `forecast_discard`, `forecast_open_draft`, `planning_run_execute`, `planning_rec_approve`, `planning_rec_dismiss`, `planning_rec_convert_to_po`) MUST NOT be counted.

### Filter semantics
- `status = 'posted'` — only posted submissions count. Pending, rejected, or cancelled submissions are excluded.
- `posted_at >= <today_midnight_site_tz>` — the `posted_at` column on `form_submissions` is confirmed in migration 0012. "Today midnight in site timezone" is UNRESOLVED-DR-2 (see §9).

### Response shape

```typescript
interface RunsTodayResponse {
  count: number;          // total posted stock-affecting form submissions today
  as_of: string;          // ISO-8601 UTC timestamp of when the count was computed
  today_start_utc: string; // ISO-8601 UTC equivalent of midnight in site timezone (UNRESOLVED-DR-2)
}
```

### Data source
`private_core.form_submissions` — confirmed table from migration 0012. Columns used: `form_type`, `status`, `posted_at`.

### Staleness tolerance
60 seconds. The KPI is informational and does not drive any operational decision.

### Cache behavior
`staleTime: 60_000` ms in TanStack Query.

### Role access
All authenticated roles.

---

## 5. Last-movement contract (KPI-B) and RUNTIME_READY registry contract

### 5a. Last-movement contract (KPI-B)

#### Endpoint
`GET /api/v1/queries/dashboard/last-movement` (suggested)

#### Purpose
The most recent stock ledger event — the `event_at` timestamp and `item_id` of the latest posted movement. This tells the operator "when was the last time stock moved?"

#### Response shape

```typescript
interface LastMovementResponse {
  event_at: string | null;         // ISO-8601 UTC of the most recent stock_ledger row; null if no movements exist
  item_id: string | null;          // item_id of that row; null if no movements
  movement_type: string | null;    // movement_type of that row (free text, confirmed in migration 0007); null if no movements
  movement_id: string | null;      // UUID of the row; null if no movements
}
```

#### Data source
`private_core.stock_ledger` — confirmed table from migration 0007. Query: most recent row by `event_at` DESC, where `post_status = 'POSTED'`. Columns used: `event_at`, `item_id`, `movement_type`, `movement_id`, `post_status`.

**Note on `post_status`:** migration 0007 confirms the `post_status` column exists and that `'POSTED'` is a valid status value (referenced in the current_balances trigger logic in 0009 and the projection filter). The full `post_status` CHECK constraint values are UNRESOLVED-DR-3 (see §9) — the spec requires `post_status = 'POSTED'` filter based on confirmed operational semantics.

#### Staleness tolerance
60 seconds. Informational KPI.

#### Cache behavior
`staleTime: 60_000` ms.

#### Role access
All authenticated roles.

---

### 5b. RUNTIME_READY registry contract

#### Endpoint
`GET /api/v1/queries/dashboard/runtime-ready-registry` (suggested)

#### Purpose
Surface which operational forms have backend closure. This tile replaces the current `pending_tranche_i` placeholder in Block 6. The authoritative source of `RUNTIME_READY` signals is the harness file `.claude/state/runtime_ready.json`. The portal MUST NOT read that file at runtime. Therefore, this endpoint requires a DB-backed registry.

#### Architecture note (UNRESOLVED-DR-1)
No DB-backed `runtime_ready` registry table exists in the confirmed migration set (0001–0075). The harness file `.claude/state/runtime_ready.json` is the sole authoritative source at this time. Options for a DB-backed registry:
- W1 authors a migration that creates a `private_core.runtime_ready_signals` table and seeds it from the harness file.
- W1 authors a seeded read-only view in `api_read` that hardcodes the known signals.

Neither option may be chosen by W4 (both are W1 schema work). Until W1 authors a migration, this endpoint cannot be authoritatively implemented. **This item is UNRESOLVED-DR-1 and is marked as such in §9.**

#### Response shape (provisional — depends on UNRESOLVED-DR-1 resolution)

```typescript
interface RuntimeReadyRegistryRow {
  signal_name: string;   // e.g. "WasteAdjustment", "GoodsReceipt", etc.
  emitted_at: string;    // ISO-8601 UTC
}

interface RuntimeReadyRegistryResponse {
  rows: RuntimeReadyRegistryRow[];
  source: string;  // e.g. "db_registry" or "harness_file_snapshot"
}
```

#### Data source
UNRESOLVED-DR-1: pending W1 DB-backed registry table or seeded view. The portal page's `RuntimeReadyBlock` component already handles the `rows: Array<{ signal_name: string; emitted_at: string }>` shape (confirmed in `types.ts`).

#### Staleness tolerance
5 minutes. The registry changes only when W1 emits a new signal — infrequently.

#### Cache behavior
`staleTime: 300_000` ms (5 minutes).

#### Role access
All authenticated roles.

---

## 6. Integration freshness grid contract

### Endpoint
`GET /api/v1/queries/dashboard/integration-freshness` (suggested)

### Purpose
Show the freshness health of all 7 integration producers. A stale producer emits its own exception; this tile shows the grid at a glance.

### Data source
`api_read.v_integration_freshness` — confirmed view from migration 0027. The view's full column set is confirmed:

| Column | Type | Description |
|---|---|---|
| `producer` | text | Producer name literal (7 confirmed values below) |
| `latest_success_at` | timestamptz or null | Timestamp of most recent successful run |
| `latest_attempt_at` | timestamptz or null | Timestamp of most recent run attempt (null for `forecast.publication`) |
| `latest_failure_at` | timestamptz or null | Timestamp of most recent failed run (null for `forecast.publication`) |
| `warning_threshold_minutes` | integer or null | Threshold for "warning" state (from `planning_policy`) |
| `critical_threshold_minutes` | integer or null | Threshold for "critical" state (from `planning_policy`) |
| `current_state` | text | One of: `'fresh'`, `'warning'`, `'critical'`, `'never_ran'` |
| `age_minutes` | integer or null | Minutes since last success; null if never_ran |

**Confirmed producer literals (7 total):**
1. `integration.lionwheel`
2. `integration.shopify`
3. `integration.green_invoice`
4. `job.rebuild_verifier`
5. `job.export.nightly`
6. `job.freshness_check`
7. `forecast.publication`

### Response shape

```typescript
interface IntegrationFreshnessRow {
  producer: string;
  last_success_at: string | null;  // ISO-8601 UTC; maps to v.latest_success_at
  state: "fresh" | "warning" | "critical" | "never_ran" | string;  // maps to v.current_state
  age_minutes: number | null;      // maps to v.age_minutes
  // Optional extended fields for tooltip / detail:
  warning_threshold_minutes?: number | null;
  critical_threshold_minutes?: number | null;
}

interface IntegrationFreshnessResponse {
  rows: IntegrationFreshnessRow[];
  as_of: string;  // ISO-8601 UTC timestamp of when this was computed
}
```

**Mapping note:** The portal's `IntegrationFreshnessRow` type in `types.ts` (confirmed) uses `last_success_at` and `state`. The DB view uses `latest_success_at` and `current_state`. The handler MUST rename these fields for the response: `latest_success_at` → `last_success_at`, `current_state` → `state`. The portal renderer matches on `r.state === "fresh"` / `"warning"` / `"critical"` / `"never_ran"` (confirmed in `page.tsx` line ~861).

### Staleness tolerance
2 minutes. The freshness view is cheap to query and producers update on their own schedules (the shortest being 15-minute Shopify and 60-minute GI).

### Cache behavior
`staleTime: 120_000` ms (2 minutes) — override of DR-1 default of 30 s.

### Role access
All authenticated roles.

---

## 7. Rebuild verifier contract (stock truth block)

### Endpoint
`GET /api/v1/queries/dashboard/stock-truth` (suggested)

### Purpose
Surface the `rebuild_verifier()` parity result, the anchor count, and the timestamp of the last nightly verifier run. Zero drift is the only operationally safe state. Non-zero drift should show as a danger signal.

### Data sources
Three confirmed DB objects:

1. `private_core.rebuild_verifier()` — confirmed in migration 0009; returns `integer` (drift row count; 0 = no drift).
2. `private_core.balance_anchors_current` — confirmed in migration 0008; the count of rows in this table is the anchor count.
3. `private_core.job_runs` — confirmed in migration 0006; query the most recent row where `job_name = 'rebuild_verifier'` and `status IN ('succeeded', 'failed', 'skipped', 'aborted')` to find `started_at` (last run timestamp) and `ended_at`.

**Calling rebuild_verifier() directly vs reading from job_runs:**
Calling `rebuild_verifier()` on every dashboard load is O(N) over all balance keys and MUST NOT be done per dashboard request. The dashboard endpoint SHOULD instead read the last `job_runs.output_summary` for `job_name = 'rebuild_verifier'` which contains `drift_count` (confirmed in the `run_rebuild_verifier()` wrapper from migration 0013). The `run_rebuild_verifier()` wrapper stores `drift_count` in `output_summary` JSONB. The endpoint reads the most recent succeeded run's `output_summary->>'drift_count'` — do not re-execute the verifier on each request.

**UNRESOLVED-DR-4:** The `output_summary` JSONB key for drift is confirmed as `'drift_count'` from migration 0013 line: `'drift_count', v_drift_count`. However, the exact full JSONB shape of `output_summary` (all keys present) has not been confirmed by a live DB inspection. Only `drift_count` key is confirmed from migration source. Mark as UNRESOLVED-DR-4 for full JSONB shape verification.

### Response shape

```typescript
interface StockTruthResponse {
  rebuild_verifier_drift: number | null;  // drift row count from latest job run's output_summary; null if no completed run exists
  anchors_count: number;                  // COUNT(*) from private_core.balance_anchors_current
  last_parity_check_at: string | null;    // started_at of the most recent job_runs row for job_name='rebuild_verifier'; null if never ran
  last_parity_status: string | null;      // status of that job run ('succeeded'/'failed'/'skipped'/'aborted'); null if never ran
}
```

**Mapping to portal types.ts:** The portal `StockTruthSummary` (confirmed in `types.ts`) uses: `rebuild_verifier_drift: number | null`, `anchors_count?: number`, `last_parity_check_at?: string`. The response shape above is a superset — `last_parity_status` is additional context. The handler author should include it; the portal will ignore extra fields.

### Staleness tolerance
5 minutes. The rebuild verifier runs nightly (confirmed `0061_rebuild_verifier_nightly_cron.sql`). An older drift count is still operationally valid within a 5-minute window.

### Cache behavior
`staleTime: 300_000` ms (5 minutes) — override of DR-1 default.

### Role access
All authenticated roles.

---

## 8. Break-glass contract

### Endpoint
`GET /api/v1/queries/dashboard/break-glass` (suggested)

### Purpose
Surface whether break-glass mode is currently active and which flags are set. When active, the system is read-only and jobs are paused; operators need to see this prominently on the dashboard.

### Data source
Two confirmed DB objects from migration 0028:

1. `private_core.is_break_glass()` — returns `boolean`. `TRUE` iff either `global_readonly` OR `jobs_paused` is enabled in `private_core.feature_flags`.
2. `private_core.break_glass_reason()` — returns `text`. Comma-separated list of enabled flags (`global_readonly`, `jobs_paused`). `NULL` when `is_break_glass()` is false.

The `private_core.feature_flags` table is confirmed (migration 0001); columns used: `flag_key`, `enabled`. The timestamp when a flag was set is UNRESOLVED-DR-5 (see §9).

### Response shape

```typescript
interface BreakGlassResponse {
  active: boolean;          // result of private_core.is_break_glass()
  reason: string | null;    // result of private_core.break_glass_reason(); null when not active
  set_at: string | null;    // UNRESOLVED-DR-5: feature_flags has no confirmed updated_at column; null until resolved
  set_by: string | null;    // UNRESOLVED-DR-5: no confirmed auditor column on feature_flags; null until resolved
}
```

**Mapping to portal types.ts:** The portal `BreakGlassState` (confirmed in `types.ts`) uses: `active: boolean`, `set_at?: string`, `set_by?: string`. The response includes `reason` as a new field; the portal will ignore it. The portal page (`page.tsx` lines ~714–732) renders `set_at` and `set_by` when present, with a fallback "v1 metadata: state only" label when both are null — this fallback handles the UNRESOLVED-DR-5 case gracefully.

### Staleness tolerance
30 seconds. Break-glass state is operationally critical; when activated it should appear on the dashboard promptly.

### Cache behavior
`staleTime: 30_000` ms per DR-1 default.

### Role access
All authenticated roles.

---

## 9. UNRESOLVED items

Each item below cannot be silently filled because it requires either a live DB inspection session, a W1 migration decision, or Tom's operational confirmation. No UNRESOLVED item has been silently defaulted in this spec.

- **UNRESOLVED-DR-1 — RUNTIME_READY DB registry:** No `private_core.runtime_ready_signals` table or equivalent DB-backed registry exists in migrations 0001–0075. The harness file `.claude/state/runtime_ready.json` is the sole current authority. Before the Block 6 tile can be wired, W1 must author a migration creating a DB registry table (or seeded view) and seed it with the 11 known signals. W4 cannot specify the table structure — that is W1 schema work.

- **UNRESOLVED-DR-2 — Site timezone for runs-today midnight boundary:** The "today midnight in site timezone" filter for the runs-today KPI requires a canonical site timezone value. No `site_timezone` or equivalent setting has been confirmed in migrations 0001–0075 (the `planning_policy` table may carry this value under an unconfirmed key). Until confirmed, the handler author must decide between UTC midnight and a hardcoded timezone, or add a site-config key. This affects the `today_start_utc` field in the response.

- **UNRESOLVED-DR-3 — Full `post_status` CHECK constraint values on `stock_ledger`:** Migration 0007 confirms `'POSTED'` as an operational value used in projection triggers. The full CHECK constraint for `post_status` was not directly confirmed (no `check (post_status in (...))` line was found in the migration grep). The last-movement query filter `post_status = 'POSTED'` is based on confirmed operational semantics. The handler author should verify the full CHECK constraint before adding defensive filtering logic.

- **UNRESOLVED-DR-4 — Full `output_summary` JSONB shape for rebuild_verifier job runs:** Migration 0013 confirms `drift_count` as a key in `job_runs.output_summary` for the `rebuild_verifier` job. The complete JSONB structure (all keys and their types) has not been confirmed by a live `SELECT output_summary FROM job_runs WHERE job_name='rebuild_verifier' ORDER BY started_at DESC LIMIT 1` query. The handler should read `output_summary->>'drift_count'` with a null-safe cast; other JSONB keys should not be assumed.

- **UNRESOLVED-DR-5 — Break-glass activation timestamp and actor:** `private_core.feature_flags` columns are confirmed as `flag_key`, `enabled`, `description` (migration 0001). The table has an `updated_at` trigger (`trg_feature_flags_touch_updated_at` confirmed in migration 0001), which means an `updated_at` column likely exists — but the exact column name was not grep-confirmed in the migration text. Until a live inspection confirms `feature_flags.updated_at` exists and is a `timestamptz`, `set_at` in the break-glass response MUST return `null`. There is no `set_by` column confirmed; `set_by` MUST also return `null` in v1.

- **UNRESOLVED-DR-6 — `integration_runs` usage for freshness grid:** The freshness grid spec sources from `api_read.v_integration_freshness` (confirmed view, confirmed columns). The task brief cites `integration_runs` as a source alongside the exceptions table. The confirmed view reads from `private_core.job_runs` (not `integration_runs`) for job-backed producers. The `integration_runs` table is confirmed (migration 0006) but is not used by `v_integration_freshness`. W4 confirms the view is the correct source; `integration_runs` is not needed for the dashboard freshness grid.

---

## 10. FR1/FR2 migration directory bracket

**FR1 (pre-write scan):** Performed immediately before writing this artifact. Migration directory state at scan time:
- Total migrations: 75
- Latest file: `0075_supplier_items_std_cost.sql` (mtime 2026-04-23 16:38)
- No migration number is referenced in this spec. No collision risk.

**FR2 (post-write scan):** To be performed immediately after this file is written. If `0076_*.sql` or later appears between FR1 and FR2, emit `contract_failure` per EXECUTION_POLICY.md §FR1→write→FR2 bracket. The W4 executor will perform FR2 as the next action after this Write call.

**Note:** This spec does not reference any migration number as a target (no "target migration 00NN" claim). The FR1/FR2 bracket is applied as a precaution per policy. A collision would only matter if this spec named a specific migration path, which it does not.
