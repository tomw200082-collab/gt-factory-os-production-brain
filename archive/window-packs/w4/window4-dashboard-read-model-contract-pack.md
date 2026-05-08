# Window 4 — Dashboard Read-Model Requirements-Spec Contract Pack

**Owner:** Window 4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Status:** CONTRACT-FIRST, requirements-only; runtime NOT built. No schema, no migrations, no handlers, no runtime code authored by this pack.
**Date authored:** 2026-04-21
**Backlog position:** W4 item 3 per `EXECUTION_POLICY.md §W4` — Dashboard read-model requirements spec.
**Relationship to sibling contracts:**
- `Projects/gt-factory-os/docs/integrations/dashboard_freshness_contract.md` — per-panel read-model view contract (what "fresh" means per data source, which `api_read.*` view backs each panel). This pack is the **aggregate single-endpoint** spec that composes those per-panel views into one read.
- `Projects/gt-factory-os/docs/integrations/integration_freshness_and_failure_surface_contract.md` — producer-side emit requirements. Consumed verbatim here.
- `Projects/gt-factory-os/docs/integrations/jobs_contracts.md` — `job_runs` / `integration_runs` shapes. Consumed verbatim here.
- `Projects/gt-factory-os/docs/integrations/exceptions_contract.md` — canonical exception taxonomy. Consumed verbatim here.
- `.claude/state/runtime_ready.json` — signals registry. Consumed verbatim here.

This pack is **not** an implementation. It is a contract specification for a single aggregate read-model endpoint that will populate the portal's control-tower dashboard. No migrations, no sync runtime, no scheduler wiring, no portal code were produced. All referenced tables / views / files already exist and are cited by source.

---

## 1. Purpose

The control-tower landing page in the portal must render a single coherent snapshot of platform health: stock-truth integrity, pending-approvals and exception backlog, integration freshness per producer, job-health over 24h, latest planning-run state, latest published forecast, the RUNTIME_READY signal registry, and break-glass state.

Today, each of those signals is already individually surfaced by a dedicated per-panel `api_read.*` view (per `dashboard_freshness_contract.md`) or by a state file (`runtime_ready.json`). **Rendering the dashboard by calling N per-panel endpoints is the anti-pattern.** It produces:

- N network round-trips per page load
- N independent TanStack Query entries with divergent `staleTime`
- N error boundaries that can show mutually-inconsistent states (e.g., "no stale integration" + "critical freshness exception" at the same timestamp if round-trips interleave across a freshness_check cron cycle)
- No single canonical "dashboard snapshot at T" usable for audit, support triage, or screenshot-replay when an operator reports "I saw X at 09:14"

This pack defines the aggregate endpoint that replaces N-call rendering with one coherent read, and specifies the envelope shape, data-source binding per field, cache / freshness semantics, auth gating, failure modes, versioning posture, and explicit v1 out-of-scope.

Non-goals of this pack (explicit):
- No new DB schema, no new migrations, no new views. Every field binds to an existing table / view / file.
- No runtime handler code. Only endpoint path proposal + envelope shape + binding map.
- No dashboard UI / component design. That is a W2 concern and is downstream of this contract.
- No authentication mechanics. Auth is magic-link email per CLAUDE.md §"Auth and roles"; role gating per field group is specified but wiring mechanics are outside this pack.

---

## 2. Scope and boundaries

### 2.1 In scope

- **Endpoint path** for the single aggregate dashboard read (§3).
- **Response envelope shape** field-by-field (§4).
- **Underlying data source** per field, citing an existing table / view / state file (§5).
- **Cache and freshness semantics** for the aggregate endpoint, including default refresh cadence proposal (§6).
- **Auth and role gating** per field group (§7).
- **Failure modes** — partial-response contract when a subsource is unreachable (§8).
- **Versioning / backward-compat posture** for the envelope shape (§9).
- **Explicit v1 out-of-scope** — trends, drill-down, per-user activity, cost rollup (§10).

### 2.2 Out of scope (explicit)

- **No new DB schema or migrations** — every source is existing.
- **No handler code / route registration / zod schemas** — binding map only.
- **No portal component design** — W2-owned, downstream.
- **No trend / time-series data** — see §10.
- **No drill-down endpoints** — per-exception, per-job, per-integration detail endpoints are out of scope for this aggregate pack (they exist separately where needed; see Phase 7.5 planning endpoints, exceptions GET, etc.).
- **No auth wiring mechanics** — magic-link bootstrap and first-user-admin seeding remain UNRESOLVED in CURRENT_STATE.md and are not addressed here.
- **No write path** — this is a pure read-model contract. The dashboard never writes.
- **No push / websocket / SSE** — client-driven polling only for v1 (CLAUDE.md §non-negotiables: "Prefer the simplest architecture that will not break under daily factory use").

### 2.3 Relationship to existing per-panel contracts

`dashboard_freshness_contract.md` in the gt-factory-os repo defines per-panel `api_read.v_*` views and the per-panel freshness rules. This aggregate pack **composes** those views — it does not replace them. Per-panel views remain individually addressable for (a) drill-down endpoints (out of scope for v1 but structurally possible) and (b) direct-access integration tests that assert one panel in isolation.

---

## 3. Endpoint path

### 3.1 Canonical proposal

`GET /api/v1/queries/signals`

Chosen for the following reasons:

1. **Under `/api/v1/queries/`** — aligns with the existing query-route convention. `/api/v1/queries/me` already exists (per Grep evidence on `api/src/me/route.ts|handler.ts|schemas.ts`). The planning-review endpoints live under `/api/v1/queries/planning/*` per `gate5_phase7_5_planning_review_endpoints_contract.md`. Queries are read-only; mutations live under `/api/v1/mutations/`.
2. **Singular `signals`** — the noun communicates that the response is a composite of heterogeneous signals (stock-truth, integration freshness, jobs, RUNTIME_READY registry, break-glass), not a list of one entity type. A name like `/api/v1/queries/dashboard` would be more UI-coupled; `signals` is surface-agnostic and remains correct even if the same aggregate is consumed by other clients (CLI diagnostic, ops runbook, support-triage tool).
3. **Aggregate semantics** — one request, one response, one snapshot. Subresources (e.g., `/api/v1/queries/signals/exceptions`) are deliberately NOT introduced; drill-down is out of scope for v1 per §10.

### 3.2 Alternatives considered and rejected

- `/api/v1/queries/dashboard` — rejected: UI-coupled noun. Future non-UI consumers would call an endpoint named "dashboard" just to get signals.
- `/api/v1/queries/health` — rejected: collides with the conventional infra health-check endpoint (`GET /health` returns `{ok: true}` for load-balancer probes, per production smoke evidence in `runtime_ready.json` ProductionActual note). Mixing infra liveness with domain signals is confusing.
- `/api/v1/queries/status` — rejected: ambiguous between "HTTP status of the endpoint itself" and "operational status of the platform".
- Multiple endpoints (`/stock-truth`, `/integrations`, `/jobs`, etc.) — rejected: reintroduces N round-trips, defeats the purpose.

### 3.3 HTTP verb and idempotency

- **Verb:** `GET`.
- **Idempotent:** yes. The endpoint reads snapshots; it never writes.
- **Safe:** yes. No side effects permitted.
- **Query parameters:** none for v1. Filtering, paging, and time-windowing are out of scope (§10). The response always represents "now" as of the snapshot timestamp in the envelope (§4.1).

---

## 4. Response envelope shape

### 4.1 Top-level envelope

The response is a single JSON object with a top-level `snapshot_at` timestamp (the time the snapshot was assembled, distinct from any per-field timestamp) and one field per signal group. Field groups are:

- `snapshot_at` — ISO-8601 UTC timestamp of snapshot assembly
- `stock_truth` — §4.2
- `inbox_counts` — §4.3
- `integration_freshness` — §4.4
- `jobs_24h` — §4.5
- `latest_planning_run` — §4.6
- `latest_forecast` — §4.7
- `runtime_ready_registry` — §4.8
- `break_glass` — §4.9
- `errors` — §4.10 (partial-response error metadata; see §8)

**Field-ordering note:** response field order is not load-bearing; clients must not depend on key order. This is a requirements spec, not a wire-format spec.

### 4.2 `stock_truth` — ledger / projection integrity

Fields:
- `rebuild_verifier_drift_count` — integer count of balance keys whose projected quantity diverges from rebuild-from-ledger. Zero = healthy.
- `last_parity_check_at` — ISO-8601 UTC; the `finished_at` of the latest `succeeded` `job.rebuild_verifier` run.
- `anchors_count` — integer count of rows in `private_core.balance_anchors` (the current-anchor snapshot surface).

**Semantics:** `rebuild_verifier_drift_count > 0` is a Gate-3-level trust event. The dashboard renders this tile with critical severity and links operators to the parity panel.

### 4.3 `inbox_counts` — approvals and exceptions by category × severity

Two sub-objects: `approvals` and `exceptions`.

**`approvals` sub-object:** count of pending approvals per form / mutation category. Categories (enumerated from `EXECUTION_POLICY.md`, `waste_adjustment_runtime_contract.md`, `physical_count_runtime_contract.md`, `gate5_phase7_5_planning_review_endpoints_contract.md`, `master_maintenance_spec.md`, and `bom_version_contract` implicit in CLAUDE.md §BOM modeling):
- `waste` — pending Waste / Adjustment approvals
- `physical_count` — pending Physical Count approvals
- `purchase_recommendation` — pending purchase-recommendation approvals (Gate 5 Phase 7.5)
- `production_recommendation` — pending production-recommendation approvals (Gate 5 Phase 7.5)
- `master_data_edit` — pending admin master-data edits awaiting approval (AMMC / Gate 2 admin runtime)
- `bom_version` — pending BOM version activations awaiting approval

Each entry is an integer count. Zero is a valid value.

**`exceptions` sub-object:** count of open+acknowledged exceptions (i.e., `status IN ('open','acknowledged')`) grouped by category and severity. Shape is a map `category → { info, warning, critical }` where each severity value is an integer. Categories enumerated exactly from `exceptions_contract.md §2`:

- `lionwheel_unknown_sku`
- `freshness_stale` — composite across all `<producer>_stale` categories listed in `exceptions_contract.md §2.1` and `integration_freshness_and_failure_surface_contract.md §2`; the aggregate name represents the collapsed count for inbox display. The individual `<producer>_stale` categories remain directly accessible via the per-panel `api_read.v_exception_summary` view for drill-down.
- `count_discrepancy_large` — equivalent to `exceptions_contract.md §2.4 count_large_variance`
- `shopify_drift`
- `shopify_unmapped_item` — equivalent to `exceptions_contract.md §2.1 shopify_missing_mapping`
- `gi_unmapped_supplier` — equivalent to `exceptions_contract.md §2.1 gi_unknown_supplier`
- `gi_non_ils_currency` — emitted by GI runtime per `runtime_ready.json` GreenInvoice note; UNRESOLVED-DR-3 (see §11)
- `job_failed` — composite across `job_failed_<name>` categories
- `count_freeze_conflict` — freeze-guard enforcement exception per `freeze_guard_contract.md` (UNRESOLVED-DR-4 if not yet in `exceptions_contract.md §2.4` — see §11)
- `bom_version_mismatch` — UNRESOLVED-DR-5 if not yet registered (see §11)

**Severity enum:** `{info, warning, critical}` per `exceptions_contract.md §1` CHECK constraint. Zero-count buckets MAY be omitted OR MAY be present with zero; the dashboard must tolerate both.

### 4.4 `integration_freshness` — per-producer freshness state

An array of entries, one per registered producer. Producer list enumerated exactly from `integration_freshness_and_failure_surface_contract.md §2`:

- `integration.lionwheel`
- `integration.shopify`
- `integration.green_invoice`
- `job.rebuild_verifier`
- `job.export.nightly`
- `job.freshness_check` (self)
- `forecast.publication`

Additional producers MAY appear if registered; the dashboard must tolerate new producers without client-side schema changes.

Per-producer fields:
- `producer` — string, exactly the producer key above.
- `last_success_at` — ISO-8601 UTC or null. Null = never-ran (cold start).
- `age_minutes` — integer minutes since `last_success_at`, or null if never-ran.
- `state` — enum `{ok, warn, crit, never_ran}`. Computed from `age_minutes` against `warn_min` / `crit_min`. `never_ran` is a distinct state from `crit` to allow cold-start rendering without alarm fatigue.
- `warn_min` — integer minutes threshold for `warn` state, sourced from `planning_policy` rows keyed `freshness.<producer>.warning_minutes` per the locked invariant in `integration_freshness_and_failure_surface_contract.md §2`.
- `crit_min` — integer minutes threshold for `crit` state, same source mechanism.

### 4.5 `jobs_24h` — per-job 24-hour health rollup

An array of entries, one per known job. Jobs include at minimum (sourced from `jobs_contracts.md` + `runtime_ready.json` evidence):
- `rebuild_verifier` (nightly)
- `excel_snapshot_export` (nightly)
- `lionwheel_poll` (cron, per `runtime_ready.json` LionWheel note)
- `shopify_fg_sync` (cron `*/15 * * * *`, per `runtime_ready.json` Shopify note)
- `green_invoice_poll` (cron `0 * * * *`, per `runtime_ready.json` GreenInvoice note)
- `freshness_check` (cron `*/10 * * * *`, per `runtime_ready.json` freshness_check note)
- Any future planning recompute / forecast-related scheduled jobs as they land

Per-job fields:
- `job_name` — string, exactly the `job_runs.job_name` value per `jobs_contracts.md §Table shapes`.
- `last_run_at` — ISO-8601 UTC of the most recent `job_runs.started_at` for this `job_name`, or null.
- `last_status` — enum `{running, succeeded, failed, aborted, skipped}` per `jobs_contracts.md §Table shapes` CHECK constraint.
- `successes_24h` — integer count of `job_runs` rows for this `job_name` in the last 24h with `status='succeeded'`.
- `failures_24h` — integer count of `job_runs` rows for this `job_name` in the last 24h with `status IN ('failed','aborted')`.
- `last_error` — nullable string. Populated from `job_runs.error` of the most recent non-succeeded run (if any in the 24h window). Truncated to 500 characters; full error available via drill-down (out of scope for v1).

**Skipped runs:** rows with `status='skipped'` (e.g., break-glass-active invocations per `runtime_ready.json` LionWheel note) count toward neither `successes_24h` nor `failures_24h`. They are operationally normal during a break-glass window. UNRESOLVED-DR-6 if Tom prefers them separately surfaced (see §11).

### 4.6 `latest_planning_run` — most recent planning run summary

Fields:
- `run_id` — UUID, the `planning_runs.run_id` of the most recent run regardless of status, or null if no runs exist yet.
- `status` — enum per `gate5_phase3_run_substrate_checkpoint.md` / `0037` planning_runs status lifecycle. Typical values include `running`, `succeeded`, `failed`.
- `executed_at` — ISO-8601 UTC; the `executed_at` column of the run row.
- `exceptions_count` — integer count of exceptions emitted by this run (rows in the planning-run exceptions projection per `gate5_phase7_orchestration_checkpoint.md`).
- `fg_coverage_count` — integer count of FG items covered by this run (i.e., rows in the FG netting output for this `run_id`).

**Empty-state semantics:** if no planning run exists yet (pre-first-run state), the entire `latest_planning_run` object is null. The dashboard renders a "no planning run yet" placeholder. This is not a failure mode.

### 4.7 `latest_forecast` — most recent published forecast summary

Fields:
- `version_id` — UUID, the `forecast_versions.version_id` of the most recent `published` row for `site_id='GT-MAIN'`, per `forecast_planning_contract.md §B.3 + §D.4`, or null if none exists yet (cold start).
- `cadence` — enum `{monthly, weekly, daily}` per CLAUDE.md §Forecast ("Monthly first, then weekly, then daily operationally"). UNRESOLVED-DR-7 if the `forecast_versions` substrate does not yet carry an explicit cadence column vs deriving cadence from horizon bucket granularity — see §11.
- `horizon_weeks` — integer; the `horizon_weeks` of the version, per `forecast_planning_contract.md §B.4`.
- `horizon_start_at` — ISO-8601 UTC (date-resolution acceptable); the ISO week start of the first forecasted week.
- `published_at` — ISO-8601 UTC; the `forecast_versions.published_at` value. This is the field consumed by the `forecast.publication` freshness producer per `integration_freshness_and_failure_surface_contract.md §2`.

**Empty-state semantics:** if no published forecast exists (cold start), the entire `latest_forecast` object is null. `forecast.publication` freshness state will independently reflect `never_ran` in §4.4.

### 4.8 `runtime_ready_registry` — RUNTIME_READY signal registry projection

An array of entries, one per signal in `.claude/state/runtime_ready.json`. Per-entry fields:
- `form` — string, the `form` field from the signal entry (e.g., `"WasteAdjustment"`, `"LionWheel"`, `"PurchaseOrders"`, `"Shopify"`).
- `emitted_at` — ISO-8601 UTC, the `emitted_at` field.
- `evidence_path` — string, the `evidence_path` field (relative path to backend contract doc or test output).

Fields deliberately omitted from the projection:
- `emitted_by` — always `executor-w1` per `.claude/SIGNALS.md`; not interesting to the dashboard.
- `note` — verbose checkpoint prose; not useful for dashboard rendering. Operators wanting the note open the `evidence_path` directly.

**Ordering:** most recent `emitted_at` first. The dashboard renders this as a "what came online and when" timeline tile.

**Schema drift:** the stale repo-local file at `gt-factory-os/.claude/state/runtime_ready.json` (3-signal schema, per CURRENT_STATE.md 2026-04-19 governance reconciliation) is NOT a source for this endpoint. Only the governance-path file under `PRODUCTION/.claude/state/runtime_ready.json` is authoritative.

### 4.9 `break_glass` — platform read-only / jobs-paused state

Fields:
- `jobs_paused` — boolean; true when the global break-glass flag is set (per `jobs_contracts.md §Binding decisions referenced` #67 "Kill switch lives in `feature_flags`, not an env var").
- `set_at` — ISO-8601 UTC or null; timestamp of the most recent flip into `jobs_paused=true`.
- `set_by` — string user identifier or null; operator who set it.

**Source row:** the `feature_flags` row named `global_readonly` per `jobs_contracts.md §Kill switch`. UNRESOLVED-DR-8 if `set_by` and `set_at` are columns on that row today vs derived from an audit trail — see §11.

### 4.10 `errors` — partial-response error metadata

When the endpoint succeeds at assembling *part* of the response but a subsource was unreachable or errored (see §8 failure modes), the corresponding field group MAY be null and an entry MAY appear in `errors`:

- `errors` is an array; empty `[]` means full success.
- Per-entry: `{ field_group, error_class, message }` where `field_group` names the top-level key that could not be populated (e.g., `"latest_planning_run"`) and `error_class` is one of `{unreachable, empty, schema_drift, unknown}`.
- A populated `errors` array does NOT cause HTTP non-2xx. The HTTP response stays `200 OK` with the partial envelope. HTTP non-2xx is reserved for auth, role-gate, and total-failure cases (§8.4).

---

## 5. Underlying data sources per field

### 5.1 Binding map

Every field in §4 binds to an existing data source. This section cites the source table / view / file for each. **No new DB objects are proposed.** Where a source does not yet exist, the gap is flagged as UNRESOLVED in §11.

| Envelope path | Source | Reference |
|---|---|---|
| `snapshot_at` | computed at response-assembly time | N/A |
| `stock_truth.rebuild_verifier_drift_count` | `api_read.v_rebuild_verifier_status` (latest drift count) | `dashboard_freshness_contract.md` "What 'fresh' means" row for `current_balances` |
| `stock_truth.last_parity_check_at` | `api_read.v_rebuild_verifier_status` (latest wrapper `finished_at`) | same |
| `stock_truth.anchors_count` | `count(*) FROM private_core.balance_anchors` | migration `0007` / `0008` per CURRENT_STATE.md Gate 3 DB layer |
| `inbox_counts.approvals.waste` | `count(*) FROM private_core.waste_adjustment WHERE status='pending'` | `waste_adjustment_runtime_contract.md` |
| `inbox_counts.approvals.physical_count` | `count(*) FROM private_core.physical_counts WHERE status='pending'` | `physical_count_runtime_contract.md` |
| `inbox_counts.approvals.purchase_recommendation` | `count(*) FROM private_core.planning_run_purchase_recs WHERE approval_status='pending'` | `gate5_phase7_5_planning_review_endpoints_contract.md` |
| `inbox_counts.approvals.production_recommendation` | `count(*) FROM private_core.planning_run_production_recs WHERE approval_status='pending'` | same |
| `inbox_counts.approvals.master_data_edit` | per AMMC admin-runtime pending-approval surface | UNRESOLVED-DR-2 — no source view named yet (see §11) |
| `inbox_counts.approvals.bom_version` | per BOM-version activation approval surface | UNRESOLVED-DR-5 (see §11) |
| `inbox_counts.exceptions.*` | `api_read.v_exception_summary` grouped by `category, severity` | `exceptions_contract.md §5` |
| `integration_freshness[]` | `api_read.v_integration_freshness` per producer | `integration_freshness_and_failure_surface_contract.md §5.1` (referenced; view to be authored by W1) |
| `jobs_24h[].last_run_at` | `MAX(started_at) FROM private_core.job_runs GROUP BY job_name` | `jobs_contracts.md §Table shapes` |
| `jobs_24h[].last_status` | `job_runs.status` joined on that max | same |
| `jobs_24h[].successes_24h` | `count(*) FROM private_core.job_runs WHERE job_name=X AND status='succeeded' AND started_at > now() - interval '24 hours'` | same |
| `jobs_24h[].failures_24h` | `count(*) FROM private_core.job_runs WHERE job_name=X AND status IN ('failed','aborted') AND started_at > now() - interval '24 hours'` | same |
| `jobs_24h[].last_error` | `job_runs.error` from most recent non-succeeded run | same |
| `latest_planning_run.run_id` | `private_core.planning_runs` ORDER BY executed_at DESC LIMIT 1 | `gate5_phase3_run_substrate_checkpoint.md` |
| `latest_planning_run.exceptions_count` | per-run exception projection | `gate5_phase7_orchestration_checkpoint.md` |
| `latest_planning_run.fg_coverage_count` | per-run FG netting row count | `gate5_phase4_net_requirements_checkpoint.md` |
| `latest_forecast.*` | `private_core.forecast_versions WHERE site_id='GT-MAIN' AND status='published' ORDER BY published_at DESC LIMIT 1` | `forecast_planning_contract.md §B.3` + migration `0018` |
| `runtime_ready_registry[]` | `.claude/state/runtime_ready.json` (governance path) | `.claude/SIGNALS.md` |
| `break_glass.jobs_paused` | `private_core.feature_flags` row `global_readonly` | `jobs_contracts.md §Kill switch` |

### 5.2 Explicit non-use of LionWheel / Shopify / GI provider field names

This endpoint never surfaces LionWheel, Shopify, or Green Invoice provider-side field names (e.g., `task.wp_order_id`, Shopify `inventory_item_id`, GI `documentType`). All integration surfaces in the envelope are **mirror-table / run-table / state-file projections**:

- Integration freshness reads `private_core.integration_runs` + the producers registered in `api_read.v_integration_freshness`.
- Shopify / GI health beyond freshness is accessible via drill-down endpoints outside this aggregate pack.
- LionWheel-specific SKU-alias backlog is surfaced via the `lionwheel_unknown_sku` exception category in `inbox_counts.exceptions` — this is mirror-side metadata, not LionWheel-side field names.

No invented provider field names appear in this pack.

### 5.3 Identity panel

The portal's top-right identity panel is **not** part of this aggregate endpoint. It reads `GET /api/v1/queries/me` (existing per `api/src/me/{route,handler,schemas}.ts`). Separation rationale:

1. `queries/me` is per-session, per-user, cache-private. The aggregate signals response is per-tenant, not per-user (other than role-gated field redaction per §7), so mixing them would force the cache key to include user identity and would defeat shared caching.
2. `queries/me` is called on every portal page (not just the dashboard). Duplicating its fields into the aggregate response would create two sources of truth for identity state.
3. Identity payload includes RLS-equivalent information that must not be cached in any shared layer.

---

## 6. Cache and freshness semantics

### 6.1 Endpoint-level freshness model — proposal

Two options were considered:

**Option A: Live-read every time.** Every call recomputes every field against live tables / views / state file. Simplest; no cache layer. Worst case is one call per dashboard render per user per refetch.

**Option B: Cached projection refreshed by cron.** A dedicated projection table / materialized view is refreshed every N seconds; the endpoint serves the projection.

### 6.2 Proposed default — **Option A with per-route TTL cache**

Default proposal: Option A (live-read) with a 30-second server-side TTL cache on the route handler, mirroring the pattern established in `dashboard_freshness_contract.md §Caching` ("Server-side: 60-second TTL via Next.js route handler cache"). Rationale:

- Every underlying source is already O(1) or O(small-N) — no query is expensive at GT's data scale (the largest joined row set, `job_runs` in the last 24h × ~6 jobs, is bounded at ~thousands).
- Option A is simpler to reason about: the dashboard always reflects the underlying sources as of ≤30s ago.
- Option B introduces a new state surface (the projection) that must itself have a freshness signal, leading to a recursive "who watches the projection refresher" question already answered for `freshness_check` but undesirable to duplicate.
- A 30-second TTL is half of the 60-second client-side TanStack `staleTime` already locked in `dashboard_freshness_contract.md §Caching`, leaving headroom for edge-cache coordination.

**Hard-refresh bypass:** a `?bypass_cache=1` query parameter MAY be introduced in a future revision to force live read. Not in v1.

### 6.3 Per-subsource freshness

Since each field reads from its own source, per-subsource freshness continues to apply. The aggregate envelope's `integration_freshness[]` array and the `freshness_check` job continue to be the operator-facing freshness signal. The 30-second TTL on the aggregate endpoint is purely a serving-layer optimization and does NOT delay propagation of freshness state by more than 30 seconds.

### 6.4 UNRESOLVED — cache cadence default is a governance call

Marked UNRESOLVED-DR-1: the 30-second TTL default is a proposal, not a locked value. Tom may prefer a different cadence (e.g., 60s aligned with `dashboard_freshness_contract.md`, or 10s for faster response under break-glass incidents). Governance decision, not a W4 call. Listed in §11.

---

## 7. Auth and role gating

### 7.1 Role model

Per CLAUDE.md §"Auth and roles" locked decision: roles are `operator`, `planner`, `admin`, `viewer`. Magic-link email auth. No passwords, no 2FA in v1. Auth wiring mechanics remain UNRESOLVED in CURRENT_STATE.md.

### 7.2 Per-field-group role requirements

| Field group | Minimum role | Rationale |
|---|---|---|
| `snapshot_at` | `viewer` | metadata only |
| `stock_truth` | `viewer` | all roles need to see ledger integrity; critical drift must be platform-wide visible |
| `inbox_counts.approvals.*` | `viewer` | counts only, not row detail; drill-down to individual approvals requires the per-form role (e.g., planner or admin for Waste approval) |
| `inbox_counts.exceptions.*` | `viewer` | counts only, not row detail |
| `integration_freshness[]` | `viewer` | platform health is visible to all authenticated users |
| `jobs_24h[]` | `viewer` | same |
| `jobs_24h[].last_error` | `admin` | error messages can leak provider payload fragments; redacted to `null` for non-admin; admin sees full truncated string |
| `latest_planning_run` | `viewer` | run summary is visible; drill-down uses Phase 7.5 endpoints with their own gates |
| `latest_forecast` | `viewer` | forecast is operationally public within the org |
| `runtime_ready_registry[]` | `viewer` | signal existence is not confidential |
| `runtime_ready_registry[].evidence_path` | `admin` | file paths inside the repo are admin-visible; redacted to `null` for non-admin |
| `break_glass.jobs_paused` | `viewer` | all roles need to know when the platform is in read-only mode |
| `break_glass.set_at` | `admin` | operator identity and timing details are admin-scope |
| `break_glass.set_by` | `admin` | same |
| `errors[]` | `viewer` | error metadata (field_group + class + message) is visible to all; the underlying sources are role-gated per above so non-admins will simply see fields they cannot access as `null`, not as errors |

### 7.3 Redaction vs omission

When a field is role-gated and the caller lacks the role, the field is **present in the envelope with value `null`**, not omitted. Rationale:

1. Omission would require the client to know the full field set to distinguish "missing because not populated" from "missing because role-gated". Null makes the distinction explicit.
2. A future `_meta.redacted_fields[]` list MAY be added to the envelope so clients can display "this field is hidden for your role" without guessing. UNRESOLVED-DR-9 — listed in §11.

### 7.4 Unauthenticated calls

`GET /api/v1/queries/signals` without a valid session returns `401` per the established auth convention (see `runtime_ready.json` ProductionActual note: "POST /api/v1/mutations/production-actuals + GET /api/v1/queries/production-actuals/open both return 401 Missing Authorization header without Bearer"). This endpoint follows the same convention.

### 7.5 Viewer role as minimum

No field group is unauthenticated-public. A `viewer`-role session is the minimum for any data. This aligns with `dashboard_freshness_contract.md` binding decision #25: "Dashboard access: logged-in only, role-gated. No public URLs, no share tokens."

---

## 8. Failure modes

### 8.1 Core principle — partial response preferred over full-endpoint 500

When one subsource is unreachable, the aggregate endpoint MUST prefer returning a partial envelope with `null` in the affected field group and an entry in the top-level `errors` array, rather than returning HTTP 500.

Rationale: the dashboard's purpose is to be the operator's single pane when something is wrong. A full-endpoint 500 when, e.g., the `cron.job_run_details` view is empty on a freshly-bootstrapped environment would blind the operator at exactly the moment they need visibility.

### 8.2 Subsource failure classes

| Failure | Treatment | HTTP status |
|---|---|---|
| Subsource table / view missing (schema not yet deployed) | Field group → `null`, `errors[]` entry `error_class='schema_drift'` | 200 |
| Subsource view exists but returns zero rows (empty state, e.g., no planning runs yet) | Field group → `null`, `errors[]` entry `error_class='empty'` | 200 |
| Subsource query times out (>2s per subsource budget) | Field group → `null`, `errors[]` entry `error_class='unreachable'` | 200 |
| Subsource query errors for unknown reason | Field group → `null`, `errors[]` entry `error_class='unknown'` | 200 |
| `runtime_ready.json` file missing or unreadable | `runtime_ready_registry[]` → empty array `[]` + `errors[]` entry `error_class='unreachable'` | 200 |
| Database totally unreachable | see §8.4 | 503 |
| Caller unauthenticated | see §7.4 | 401 |
| Caller lacks viewer role | (rare — implies malformed role claim) | 403 |

### 8.3 Empty-state vs schema-drift distinction

`empty` and `schema_drift` are distinct error classes:
- `empty` — the source exists and was queried successfully; the natural result is "no rows". Example: brand-new environment with no planning runs yet. This is not an alert condition; dashboard renders "no data yet" placeholder.
- `schema_drift` — the source could not be queried because the expected table / view / column shape is not present. This IS an alert condition; operator should investigate a missing migration.

The dashboard MUST render these differently: `empty` as a soft placeholder, `schema_drift` as a visible problem.

### 8.4 Total-failure case

When the database connection itself is down (no subsource can be queried), the endpoint SHOULD return `503 Service Unavailable` with a minimal envelope containing only `snapshot_at` and an `errors[]` entry `error_class='unreachable'` with `field_group='(all)'`. This is the one case where HTTP non-2xx is preferred over partial response, because there is no partial response to give.

### 8.5 Timeout budget

Per-subsource query timeout: 2 seconds (aligns with `dashboard_freshness_contract.md §Failure modes` "Next.js route handler timeout (5s)" at the aggregate level). Per-endpoint total timeout: 5 seconds. Subsources that exceed 2s are treated as `unreachable` per §8.2 and do NOT block sibling subsources.

---

## 9. Versioning and backward-compat posture

### 9.1 Versioning principle

The endpoint path is `/api/v1/queries/signals`. The `v1` in the path is the API-version anchor. The response envelope SHAPE within v1 follows the following rules:

### 9.2 Rules for v1 envelope evolution

- **Adding new top-level field groups** — allowed and non-breaking. Clients MUST tolerate unknown top-level keys.
- **Adding new fields inside an existing field group** — allowed and non-breaking. Same tolerance rule.
- **Adding new entries to an array** (e.g., new producer in `integration_freshness[]`, new job in `jobs_24h[]`) — allowed and non-breaking. Clients MUST iterate, not key-by-index.
- **Renaming a field** — **breaking change**. Requires a new `/api/v2/` path or a deprecation window where both old and new names appear simultaneously.
- **Removing a field** — **breaking change**. Same treatment.
- **Changing a field's type** (e.g., integer to string) — **breaking change**. Same treatment.
- **Changing an enum's value set by adding values** — non-breaking if documented in `EXECUTION_POLICY.md` or the corresponding per-contract spec; clients MUST tolerate unknown enum values by rendering them in a fallback "unknown" bucket.
- **Changing an enum's value set by removing values** — **breaking change**.

### 9.3 Requirements-only qualification

This is a requirements-only document. The rules above become enforceable once the endpoint is implemented. Until then, this section is forward-looking guidance. No current field is "live".

### 9.4 Deprecation protocol

When a v2 path is introduced, v1 must continue to serve for at least one operational cycle (CURRENT_STATE.md "gate-by-gate" cadence granularity) before removal. Clients should log a warning on receipt of a deprecation header (e.g., `Deprecation: true` per the RFC) but continue to function.

---

## 10. Out of scope for v1 (explicit)

The following are deliberately NOT in the v1 aggregate endpoint. Each is listed so that consumer teams do not assume availability.

### 10.1 Trends over time

No time-series fields. No `rebuild_verifier_drift_count_last_7_days[]`. No `jobs_failures_per_hour_last_24h[]`. Trends require a separate time-series substrate and a longer retention window than the current `job_runs` / `integration_runs` tables guarantee. V1 renders point-in-time state only.

### 10.2 Drill-down per exception

No exception-row payloads, no exception-detail navigation. The endpoint returns only **counts** by category × severity. Drill-down uses the existing exceptions list endpoint (per `exceptions_contract.md §5` / `api_read.v_exception_summary` and the `api/test/exceptions.test.ts` E1–E16 coverage referenced in `runtime_ready.json` ExceptionsInbox note).

### 10.3 Per-user activity

No `my_pending_approvals` field keyed to the calling user. No "things waiting for me" subsetting. The dashboard surfaces org-wide counts; per-user surfacing is a future enhancement outside this pack.

### 10.4 Cost rollup

No cost / margin / financial summary. Gate 5 Phase 10 cost rollup is a post-closure stretch per CURRENT_STATE.md Gate 5 A11 amendment. Until that lands, the dashboard carries no cost information.

### 10.5 Operator / driver / supplier activity feeds

No per-operator form-submission feed. No per-driver delivery feed. No per-supplier PO feed. These are separate drill-down surfaces if ever needed.

### 10.6 Push / SSE / WebSocket

No server-push. Client polls at its own cadence, honoring the server-side TTL per §6.2.

### 10.7 Multi-site / multi-tenant selection

GT runs single-site (`site_id='GT-MAIN'`) per forecast and planning contracts. No site-picker logic in the envelope; all fields are implicitly scoped to `GT-MAIN`.

### 10.8 Differentiated operator-rollout evidence

The "first live production stock event" milestone (CURRENT_STATE.md §Gate 3 post-exit tracking) is NOT surfaced in this endpoint as a distinct field. It would be derivable from `stock_ledger` inspection, but is out of scope: dashboard surfaces platform health, not operator-rollout progress.

---

## 11. UNRESOLVED items (explicit, do not silently heal)

Each entry below identifies a gap that must not be silently filled by the executor building the runtime handler. Resolution must be an explicit governance or W1 decision.

- **UNRESOLVED-DR-1 — Cache refresh cadence default.** §6 proposes 30-second TTL; a different cadence (15s / 60s / configurable via `planning_policy`) is a governance call, not a W4 call. Why it cannot be silently filled: serving-layer cadence has operator-UX and incident-response implications that are Tom-authoritative.

- **UNRESOLVED-DR-2 — Pending master-data-edit approval source view.** §5.1 binding for `inbox_counts.approvals.master_data_edit` currently has no named view. The AMMC v1 admin-runtime surfaces pending-approval rows per `master_maintenance_spec.md`, but the aggregate-facing view name is not yet defined in any contract. Why it cannot be silently filled: inventing a view name would collide with W1 AMMC-runtime conventions.

- **UNRESOLVED-DR-3 — `gi_non_ils_currency` exception category registration.** §4.3 lists this as a dashboard-visible exception category; it is emitted by GI runtime per `runtime_ready.json` GreenInvoice note but is NOT in `exceptions_contract.md §2.1`. Why it cannot be silently filled: adding a category requires a W4 edit to `exceptions_contract.md`, not a silent binding decision in this aggregate pack. Flagged for a future W4 rolling-backlog cycle.

- **UNRESOLVED-DR-4 — `count_freeze_conflict` exception category registration.** Same pattern as DR-3; `freeze_guard_contract.md` governs count-freeze semantics but the exception category is not yet formally in `exceptions_contract.md §2.4`. Why it cannot be silently filled: same as DR-3.

- **UNRESOLVED-DR-5 — `bom_version_mismatch` exception and BOM-version approval source.** Covers both (a) the exception category name (not in §2.x of `exceptions_contract.md` today) and (b) the pending-BOM-version approval source view. Why it cannot be silently filled: BOM-version lifecycle contracts (CLAUDE.md §BOM modeling) lock the `bom_head / bom_version / bom_lines` structure but have not yet defined an approval-queue surface.

- **UNRESOLVED-DR-6 — Treatment of `skipped` job runs in 24h health.** §4.5 proposes that `status='skipped'` rows count toward neither successes nor failures. Tom may prefer them separately surfaced (e.g., `skipped_24h` field) to make break-glass activity visible. Why it cannot be silently filled: affects operator interpretation of "was the job healthy" during break-glass windows.

- **UNRESOLVED-DR-7 — Forecast cadence source column.** §4.7 surfaces `cadence` as `{monthly, weekly, daily}` per CLAUDE.md §Forecast. It is unknown whether `forecast_versions` carries an explicit cadence column or whether cadence is derived from horizon bucket granularity. Why it cannot be silently filled: binding to a non-existent column is `assumption_failure`; deriving cadence here risks divergence from any future explicit column.

- **UNRESOLVED-DR-8 — `break_glass.set_at` / `set_by` source columns.** §4.9 binds to `private_core.feature_flags` row `global_readonly` but the existence of `set_at` / `set_by` columns on `feature_flags` is not confirmed in any W4 contract read during authoring. Jobs contract §Binding decisions references feature_flags with "short cache and expiry timestamp" but does not enumerate audit columns. Why it cannot be silently filled: binding to non-existent columns is `assumption_failure`.

- **UNRESOLVED-DR-9 — `_meta.redacted_fields[]` inclusion.** §7.3 proposes a future `_meta.redacted_fields[]` array to surface role-gated-redaction explicitly to clients. Not in v1 envelope. Why it cannot be silently filled: adding a meta-field to v1 requires governance on the "null means redacted vs null means empty" ambiguity.

- **UNRESOLVED-DR-10 — `api_read.v_integration_freshness` view existence.** `integration_freshness_and_failure_surface_contract.md §5.1` references this view as the freshness-check read surface, but whether W1 has authored it against the producer registry enumerated in that document's §2 is not confirmed at the time of this pack. Why it cannot be silently filled: if the view does not yet exist, the aggregate endpoint cannot implement §4.4 without a W1 handoff.

- **UNRESOLVED-DR-11 — Per-run exceptions_count source for `latest_planning_run`.** §4.6 binds `exceptions_count` to "the per-run exception projection" per Gate 5 Phase 7. The exact view / column name is not enumerated here because the Gate 5 Phase 7 checkpoint carries the authoritative projection shape but this aggregate pack did not re-verify the column spelling. Why it cannot be silently filled: W1 must confirm the exact column.

- **UNRESOLVED-DR-12 — Role-gated `jobs_24h[].last_error` truncation length.** §4.5 proposes 500 characters. Tom may prefer a different limit (256 / 1024 / none for admin). Why it cannot be silently filled: leakage-risk decision.

---

## 12. Self-check against foundation

- [x] Requirements-only — no DDL, no handler code, no migrations, no runtime authored. §§1, 2.
- [x] Single aggregate endpoint proposed at canonical path `/api/v1/queries/signals`. §3.
- [x] Response envelope fully enumerated field-by-field. §4.
- [x] Data source cited per field — every binding is to an existing table / view / file; none invent provider field names. §5.1, §5.2.
- [x] Identity panel deliberately separated from aggregate to preserve `/api/v1/queries/me` contract. §5.3.
- [x] Cache and freshness semantics explicit; default cadence is a proposal, cadence-default listed UNRESOLVED. §6, §11 (DR-1).
- [x] Role gating per field group enumerated; viewer is the minimum. §7.
- [x] Failure modes prefer partial response over full-endpoint 500; schema-drift vs empty distinguished. §8.
- [x] Versioning rules for v1 envelope evolution laid out. §9.
- [x] Explicit v1 out-of-scope list covers trends, drill-down, per-user, cost rollup. §10.
- [x] UNRESOLVED items registered with reasons. §11.
- [x] No reopening of locked decisions in CLAUDE.md / CURRENT_STATE.md / EXECUTION_POLICY.md. Verified.
- [x] No migration-number claim — this is a read-model over existing tables; FR1→write→FR2 bracket not required per EXECUTION_POLICY.md §W4 pre-write-fresh-read scope. Verified.
- [x] No invented LionWheel / Shopify / GI provider field names — all integration surfaces read through mirror tables, run tables, or the state file. §5.2.

---

**END — Window 4 Dashboard Read-Model requirements-spec contract pack.**

Runtime is **not built**. This pack is **contract-complete** for v1 scope, with the UNRESOLVED register in §11. Runtime implementation is blocked until the §11 items are resolved by the governor / W1 handoff, and even then is downstream of the priorities in CURRENT_STATE.md §Current critical path.
