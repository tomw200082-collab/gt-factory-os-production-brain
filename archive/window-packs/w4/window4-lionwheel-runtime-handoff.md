# Window 4 — LionWheel Runtime Handoff Spec (First Slice)

**Owner:** Window 4 (Integrations)
**Audience:** Window 1 (DB / Schema / Migrations), secondary Window 5 (Governance)
**Status:** runtime-ready handoff spec — **NOT a migration**, **NOT runtime code**
**Authored:** 2026-04-17
**Upstream:** [window4-lionwheel-contract-pack.md](window4-lionwheel-contract-pack.md) (accepted for v1 scope)

This document compresses the accepted LionWheel contract pack into the smallest runtime-ready implementation package. It is the brief Window 1 will consume when runtime authoring begins.

**What this document is:** proposed mirror entity shapes, reconciliation rules, freshness semantics, kill-switch behaviour, validation cases, parallel-safe work register.

**What this document is NOT:** DDL. Migration files. Scheduler wiring. Webhook endpoint code. Runtime fetcher implementation. Planning engine work. Portal UI.

---

## Phase A — Smallest runnable v1 slice

### A.1 First runtime slice — chosen

**Slice 1: single-task pull via `GET /tasks/show/:task_id`, driven by CLI, writing to mirror tables, producing one `integration_run` row per invocation.**

### A.2 Why this slice is first

Ranked against every alternative:

| Candidate first slice | Rejected because |
|---|---|
| `/routes?date=today` daily sweep | requires scheduler wiring; more entities per run (route + embedded visits); harder to assert idempotency in isolation |
| Webhook intake | requires public HTTPS endpoint, signature verification, replay protection, organization-settings change in LionWheel; not the smallest starting surface |
| `/tasks/by_order_id/:order_id` loop | requires maintaining a GT-side list of `wp_order_id`s first; introduces two concepts at once |
| Full polling loop | combines scheduler + fetcher + reconciliation — too many failure surfaces for first evidence |
| **`/tasks/show/:task_id` CLI** ✅ | smallest surface that exercises: auth, parse, upsert, embedded-child upsert (visits + order_items), integration_run lifecycle, freshness view population, idempotency. No scheduler. No webhook. No public endpoint. Fully testable against fixtures. |

**Evidence produced by Slice 1:**
- A row exists in `lw_task` matching the inspected LionWheel task
- Matching rows exist in `lw_visit` and `lw_order_item`
- Exactly one `integration_run` row per CLI invocation
- Second invocation with unchanged `updated_at` produces no downstream change (idempotent)
- Invocation with advanced `updated_at` updates the mirror row and advances `mirror_source_watermark`
- `freshness_status_view` reports `fresh` for `lw_task` after a successful run

### A.3 What Slice 1 explicitly does NOT do

- No scheduler. CLI-driven only.
- No webhook. Webhook intake is Slice 3.
- No `/routes` sweep. Routes mirror is Slice 2.
- No driver or company lookup mirror. Deferred.
- No reconciliation pass. Pure per-call upsert.
- No downstream read-model exposure to portal consumers. The views exist; they are not wired to Window 2 in this slice.
- No planning-engine consumption. Blocked by Gate 3 and Gate 5.

### A.4 Later slices (sequence preview, NOT authored in this doc)

- **Slice 2:** `/routes?date=` daily sweep → upsert `lw_route` + nested visits reconciled against existing `lw_visit` rows.
- **Slice 3:** Webhook endpoint → idempotent ingest from push, trace_id'd to replace CLI-driven `/tasks/show` pulls in the steady state.
- **Slice 4:** Reconciliation pass → daily diff between known-open mirror tasks and observed tasks in date-bounded `/routes` sweeps; retires orphans; emits exceptions.
- **Slice 5:** `lw_driver` + `lw_company` lookup mirror (populated on-demand, cached).
- **Slice 6:** `open_orders_view` + `shipment_status_view` exposure to Window 2 (read-only with staleness badge).

Slices 2–6 stay under this same handoff discipline — proposed shapes only, Window 1 authors DDL.

---

## Phase B — Window 1 handoff spec (proposed shapes, NOT DDL)

All shapes below are **proposals** for Window 1 to finalize. Window 1 is the sole authority on final column names, types, constraints, indexes, and migration structure. This document may not be pasted as SQL.

### B.1 Proposed mirror schema location

Mirror tables SHOULD live in a dedicated schema — **proposed name** `integrations_lionwheel` or `mirror_lionwheel` (Window 1's choice). Not in `private_core`, not in `public`. Separation clarifies:
- ownership (Window 4 contract, Window 1 DDL)
- audit posture (mirror tables are regeneratable; `private_core` tables are not)
- RLS policy (mirror reads may have looser policies than core truth tables)

### B.2 Proposed entity — `lw_task`

| Proposed column | Proposed type | Keys / constraints | Source | Notes |
|---|---|---|---|---|
| `id` | `bigint` | **PK** | LionWheel `task.id` | authoritative external key; NOT a surrogate UUID |
| `public_id` | `text` | unique index | LionWheel `task.public_id` | human-friendly; can be shown to operators |
| `organization_id` | `integer` | index | LionWheel `task.organization_id` | observed GT = 2074 |
| `company_id` | `integer` | index | LionWheel `task.company_id` | observed GT = 34859 |
| `status` | `text` | CHECK against known enum values + log novel | `task.status` | enum incomplete (see G.2 in pack) — store as `text`, log novel values as schema drift |
| `pick_status` | `text` | no CHECK | `task.pick_status` | enum unknown; free text for now |
| `roundtrip_status` | `text` | no CHECK | `task.roundtrip_status` | enum unknown |
| `urgency` | `text` | no CHECK | `task.urgency` | enum unknown |
| `is_roundtrip` | `boolean` | | `task.is_roundtrip` | |
| `same_day` | `boolean` | | `task.same_day` | |
| `is_terminal` | `boolean` | computed / trigger-maintained | derived from `status ∈ {COMPLETED, CANCELED, FINAL_FAILED, ROUNDTRIP_DELIVERED}` | used by `open_orders_view` |
| `wp_order_id` | `text` | **NON-UNIQUE index** | `task.wp_order_id` | **must not be unique** — split orders share it |
| `wp_order_key` | `text` | | `task.wp_order_key` | |
| `creation_origin` | `text` | | `task.creation_origin` | observed `"shopify"` |
| `creation_trigger` | `text` | | `task.creation_trigger` | observed `"automatic"` |
| `driver_id` | `integer` | index (FK to future `lw_driver`, not enforced in Slice 1) | `task.driver_id` | |
| `packages_quantity` | `integer` | | `task.packages_quantity` | |
| `pickup_at` | `timestamptz` | | `task.pickup_at` | |
| `completed_at` | `timestamptz` | nullable | `task.completed_at` | |
| `wp_order_at` | `timestamptz` | | `task.wp_order_at` | |
| `created_at_upstream` | `timestamptz` | | `task.created_at` | **rename from `created_at` to avoid clash with mirror own timestamp** |
| `updated_at_upstream` | `timestamptz` | index | `task.updated_at` | primary change-detection watermark |
| `order_total` | `text` | | `task.order_total` | **store as text**; it arrives as string decimal; parse at read time (see §G.1 in pack for quantity precision) |
| `notes` | `text` | | `task.notes` | |
| `org_note` | `text` | nullable | `task.org_note` | |
| `driver_note` | `text` | nullable | `task.driver_note` | **may contain a credentialed GreenInvoice URL** — see §G.12 in pack; mirror as-is, do NOT fetch the URL from the mirror layer |
| `raw_payload` | `jsonb` | | full `/tasks/show` response body | **resilience column** — protects against schema drift and captures fields not yet promoted to structured columns |
| `mirror_ingested_at` | `timestamptz` | default `now()` | runtime | |
| `mirror_source_run_id` | `uuid` | FK to `integration_run(id)` | runtime | |
| `mirror_source_watermark` | `timestamptz` | | copy of `updated_at_upstream` at ingest | used in upsert WHERE-clause to avoid stale writes |

**Indexes proposed:**
- PK on `id`
- unique on `public_id`
- non-unique on `wp_order_id`
- non-unique on `updated_at_upstream`
- non-unique on `(is_terminal, updated_at_upstream)` to accelerate `open_orders_view`
- non-unique on `status` for freshness-and-retirement queries

**Fields NOT promoted to structured columns in Slice 1** (stay in `raw_payload`):
- `signature_url`, `signee_name`, `signature`, `signed_document`, `signed_document` → POD artifacts
- `price`, `fee_cost` → LionWheel cost fields (see §G.7 in pack)
- all `target_partner_*`, `origin_partner_*`, `transferred_at`, `transfer_errors`, `external_line_branch`, `external_distribution_line` → partner-transfer model, out of v1
- all `money_collect`, `payment_method`, `money_transferred`, `money_transferred_at` → COD (see §G.7)
- all `age_verification`, `age_start_date`, `leave_next_to_door`, `is_self_pickup`, `is_free` → delivery modifiers
- all `validation_*`, `delivery_confirmation_*`, `confirmation_*` → confirmation workflow
- `skills`, `failed_count`, `stop_time`, `wait_time`, `scheduled_template_id`, `sms_from_name`, `otp_code`, `extra_barcode`, `task_type`, `customer_user_agent`, `route_code`, `greeting`, `gifter_name`, `gifter_phone`, `source_order_id`, `due_date`, `earliest`, `latest`, `returned_pallets`, `batch_id`, `branch_id`, `warehouse_id`, `client_id`, `user_id`, `other_user`, `payer`, `printed_at`, `ready_to_print`, `document_number`, `document_type`, `invoice_id`, `distribution_id`, `weight`, `volume`, `cartons_quantity`, `surfaces_quantity`

Rationale: promote only what `open_orders_view` and `shipment_status_view` need. Everything else survives in `raw_payload` for later promotion without re-pulling.

### B.3 Proposed entity — `lw_visit`

| Proposed column | Proposed type | Keys / constraints | Source |
|---|---|---|---|
| `id` | `bigint` | **PK** | `visit.id` |
| `task_id` | `bigint` | FK to `lw_task(id)` ON DELETE CASCADE (see B.7) | `visit.task_id` |
| `route_id` | `bigint` | nullable, no FK in Slice 1 (route mirror comes in Slice 2) | `visit.route_id` |
| `organization_id` | `integer` | | `visit.organization_id` |
| `company_id` | `integer` | | `visit.company_id` |
| `driver_id` | `integer` | | `visit.driver_id` |
| `kind` | `text` | CHECK-soft: observed `"DELIVERY"` (expect `"PICKUP"`) | `visit.kind` |
| `is_done` | `boolean` | | `visit.is_done` |
| `visit_at` | `timestamptz` | | `visit.visit_at` |
| `delivered_at` | `timestamptz` | nullable | `visit.delivered_at` |
| `failed_at` | `timestamptz` | nullable | `visit.failed_at` |
| `failure_reason` | `text` | nullable | `visit.failure_reason` |
| `recipient_name` | `text` | | `visit.recipient_name` |
| `phone` | `text` | | `visit.phone` (E.164) |
| `phone2` | `text` | | `visit.phone2` |
| `email` | `text` | | `visit.email` |
| `city` | `text` | | `visit.city` |
| `street` | `text` | | `visit.street` (Hebrew allowed) |
| `number` | `text` | | `visit.number` |
| `apartment` | `text` | | `visit.apartment` |
| `floor` | `text` | | `visit.floor` |
| `zip_code` | `text` | | `visit.zip_code` |
| `latitude` | `numeric(10,7)` | | `visit.latitude` |
| `longitude` | `numeric(10,7)` | | `visit.longitude` |
| `delivery_latitude` | `numeric(10,7)` | nullable | |
| `delivery_longitude` | `numeric(10,7)` | nullable | |
| `packages_quantity` | `integer` | | `visit.packages_quantity` |
| `notes` | `text` | | `visit.notes` |
| `created_at_upstream` | `timestamptz` | | `visit.created_at` |
| `updated_at_upstream` | `timestamptz` | | `visit.updated_at` |
| `raw_payload` | `jsonb` | | full visit object |
| `mirror_ingested_at` | `timestamptz` | default `now()` | |
| `mirror_source_run_id` | `uuid` | FK to `integration_run(id)` | |
| `mirror_source_watermark` | `timestamptz` | | |

**Indexes proposed:** PK on `id`; FK index on `task_id`; non-unique on `updated_at_upstream`; non-unique on `(is_done, delivered_at)`.

**NOT promoted, live in `raw_payload`:** all `eta_*`, `earliest*`, `latest*`, `loaded_at`, `geo_*`, `matches_count`, `partial_match`, `location_cache_id`, `location_id`, `state`, `geo_fence_id`, `is_location_fixed`, `ignore_location_warning`, `salary`, `salary_origin`, `priority`, `group`, `daily_order`, `entrance`, `entrance_code`, `region_str`, custom Hebrew-keyed fields.

### B.4 Proposed entity — `lw_order_item`

| Proposed column | Proposed type | Keys / constraints | Source |
|---|---|---|---|
| `id` | `bigint` | **PK** | `order_item.id` |
| `task_id` | `bigint` | FK to `lw_task(id)` ON DELETE CASCADE | embedded parent |
| `sku` | `text` | index | `order_item.sku` — **join key to GT `items.sku`** |
| `name` | `text` | | `order_item.name` |
| `quantity` | `text` | | `order_item.quantity` — **stored as text pending G.1 resolution**; parse at read time |
| `variant` | `text` | nullable | |
| `price` | `text` | nullable | **stored as text** to mirror upstream string-decimal semantics |
| `weight` | `text` | nullable | |
| `notes` | `text` | nullable | |
| `raw_payload` | `jsonb` | | |
| `mirror_ingested_at` | `timestamptz` | default `now()` | |
| `mirror_source_run_id` | `uuid` | FK to `integration_run(id)` | |

**Indexes proposed:** PK on `id`; FK index on `task_id`; non-unique on `sku` for join-to-items.

**Join-to-items rule (NOT a FK, NOT enforced at DB layer):**
`lw_order_item.sku` matches `items.sku` when an `items` row with that SKU exists. **Never auto-create** an `items` row from a mirrored order item. Unmatched SKUs must route to an exception (Exceptions Inbox, Gate 3 concept). This preserves CLAUDE.md "never auto-create components from integration payloads."

### B.5 Proposed entity — `integration_run`

| Proposed column | Proposed type | Keys / constraints | Notes |
|---|---|---|---|
| `id` | `uuid` | **PK** | generated at insert |
| `integration` | `text` | CHECK: `'lionwheel'` for Slice 1; extensible | |
| `run_kind` | `text` | CHECK: `'task_refresh'` for Slice 1; extensible: `'routes_sweep'`, `'webhook_ingest'`, `'reconciliation_pass'` | |
| `status` | `text` | CHECK: `'pending' | 'running' | 'succeeded' | 'partial' | 'failed' | 'superseded'` | lifecycle per §C.2 in pack |
| `started_at` | `timestamptz` | default `now()` | |
| `finished_at` | `timestamptz` | nullable | |
| `duration_ms` | `integer` | computed or set at finish | |
| `records_attempted` | `integer` | default 0 | |
| `records_upserted` | `integer` | default 0 | |
| `records_skipped_stale` | `integer` | default 0 | incremented when incoming `updated_at` ≤ existing `mirror_source_watermark` |
| `records_retired` | `integer` | default 0 | incremented when a terminal-status transition is observed |
| `records_failed` | `integer` | default 0 | |
| `error_class` | `text` | nullable; CHECK against §C.4 vocabulary from pack | |
| `error_detail` | `jsonb` | nullable | **must not contain raw token**; redact before write |
| `request_watermark_from` | `timestamptz` | nullable | for watermark-driven refreshes (Slice 2+) |
| `request_watermark_to` | `timestamptz` | nullable | |
| `sweep_date` | `date` | nullable | for routes-sweep runs |
| `trigger_source` | `text` | CHECK: `'manual' | 'scheduler' | 'webhook' | 'reconciliation_job' | 'kill_switch'` | |
| `trace_id` | `text` | | correlation id; operators reference this |
| `evidence_sample` | `jsonb` | nullable | small redacted sample ingested; for audit; token + PII must be scrubbed |
| `endpoint` | `text` | | URL path called (e.g. `/api/v1/tasks/show/:task_id`) for audit |
| `upstream_task_ids` | `bigint[]` | nullable | for task_refresh / webhook_ingest runs, lets `integration_run` be queried by affected task |

**Indexes proposed:** PK on `id`; non-unique on `(integration, run_kind, status)`; non-unique on `started_at` descending.

**Retention policy (proposed, Window 1 finalizes):**
- `succeeded` runs older than 90 days → archive or delete
- `failed` / `partial` runs: retain indefinitely until cleared by ops
- `error_detail` jsonb: cap at 32 KB per row; larger payloads go to object storage with a reference

### B.6 Proposed view — `freshness_status_view`

Not a migration. A view contract:

```
-- Conceptual (NOT SQL to paste; Window 1 authors final form)
-- Returns one row per (integration, entity) combination:

freshness_status_view:
  integration         text      -- 'lionwheel'
  entity              text      -- 'lw_task' | 'lw_visit' | 'lw_order_item'
  last_successful_run_at     timestamptz   -- max(finished_at) from integration_run where status = 'succeeded'
  last_upsert_watermark      timestamptz   -- max(mirror_source_watermark) across the entity's rows
  minutes_since_last_success integer       -- now() - last_successful_run_at
  threshold_minutes          integer       -- lookup from a small freshness_policy table or config
  status                     text          -- 'fresh' | 'degraded' | 'stale' | 'broken'
  auth_error_persists_since  timestamptz   -- nullable; set when most recent run has error_class='auth'
```

**Computation rule:**
- `fresh` iff `minutes_since_last_success <= threshold_minutes` AND no recent `partial` or `failed` status
- `degraded` iff most recent run was `partial`
- `stale` iff `minutes_since_last_success > threshold_minutes`
- `broken` iff `auth_error_persists_since` is set and > 5 minutes ago

**Must be cheap to query.** This view is called on every portal page render that shows a LionWheel-sourced read model. It must not join against full `lw_task` / `lw_visit` tables.

### B.7 Cascade rule — the one subtle call

`lw_visit` and `lw_order_item` FK to `lw_task(id)`. Upstream deletion of a LionWheel task is not observed (CANCELED is a status transition, not a deletion), so ON DELETE CASCADE is primarily a housekeeping / rollback safety net, not an operational dependency.

**Proposed:** ON DELETE CASCADE from `lw_task` for both child tables. Rationale: makes mirror rollback / rebuild trivial. If Window 1 prefers RESTRICT for audit strictness, it must provide a manual cascading rollback script in the runbook.

### B.8 Idempotent upsert expectation

For Slice 1, the fetcher-side upsert logic **must**:

1. Fetch `/tasks/show/:task_id`. If 404 → record `records_failed += 1`, `error_class = 'not_found'` on the run (NOT a run-level failure; this is expected for retired tasks).
2. Parse response. Validate with a Zod schema matching §B.2 / §B.3 / §B.4. On schema mismatch (unknown required field missing, type mismatch) → `error_class = 'schema_drift'`, **halt the run for that entity**, emit exception. Do not silently coerce.
3. Compute incoming `updated_at_upstream` from `task.updated_at`.
4. Upsert `lw_task` using ON CONFLICT (id) DO UPDATE WHERE EXCLUDED.updated_at_upstream > lw_task.mirror_source_watermark. If the WHERE fails → `records_skipped_stale += 1`.
5. On upsert success → `records_upserted += 1`; set `mirror_source_watermark = EXCLUDED.updated_at_upstream`; set `mirror_source_run_id = <current run id>`.
6. For each `visits[]` element → same rule keyed on `visit.id` / `visit.updated_at`.
7. For each `order_items[]` element → same rule keyed on `order_item.id`. **Note:** order_items do not have an `updated_at` in inspected responses; treat any difference in `raw_payload` hash as a change (or simply always overwrite on each task refresh — both are defensible; Window 1 chooses).
8. If status transitioned from non-terminal → terminal → `records_retired += 1`.
9. On run completion → set `status = 'succeeded'` iff `records_failed = 0`, else `'partial'` or `'failed'` per the §C.2 rules.

**Critical:** step 4's WHERE clause is what guarantees webhook / manual-pull / routes-sweep convergence is order-independent. A late-arriving older payload cannot overwrite a newer one.

### B.9 Minimal validation cases Window 1 tests must cover

These are the pgTAP / equivalent test cases Window 1 is responsible for:

| # | Case | Expected |
|---|---|---|
| V.1 | Insert task with status `ACTIVE`, then upsert same task with status `COMPLETED` and later `updated_at` | `lw_task.status = 'COMPLETED'`, `is_terminal = true`, `records_retired += 1` |
| V.2 | Upsert with identical `updated_at` as stored `mirror_source_watermark` | `records_upserted = 0`, `records_skipped_stale = 1` |
| V.3 | Upsert with EARLIER `updated_at` than stored watermark | `records_skipped_stale = 1`; existing row unchanged |
| V.4 | Two tasks sharing `wp_order_id` both ingest | both rows present, neither blocks the other, `wp_order_id` index is non-unique |
| V.5 | Task with 3 visits → all 3 `lw_visit` rows created, FK to task | visits queryable by task_id |
| V.6 | Task with 4 order_items → all 4 `lw_order_item` rows created | items queryable by task_id |
| V.7 | Upstream payload with unknown `status` enum value | `error_class = 'schema_drift'`; no partial write of that task |
| V.8 | `integration_run` lifecycle: pending → running → succeeded | transitions recorded; `finished_at` set; `duration_ms` computed |
| V.9 | `integration_run` lifecycle: pending → running → failed (simulated 401) | `error_class = 'auth'`; `status = 'failed'`; freshness view eventually shows `broken` |
| V.10 | `freshness_status_view` computation for a fresh run, a stale run (> threshold), a broken run (auth error > 5 min) | each returns the correct status |
| V.11 | ON DELETE CASCADE from `lw_task` removes `lw_visit` and `lw_order_item` children | confirmed |
| V.12 | `raw_payload` jsonb round-trips full API response | bit-for-bit equivalent except for server-side reformatting |

---

## Phase C — Runtime execution semantics

### C.1 Pull cadence assumption (Slice 1)

- **Slice 1 has NO cadence.** CLI-driven only. One CLI invocation = one `integration_run` row.
- Later Slice 2 (`/routes` sweep) proposed cadence: **once per 15 minutes during operating hours (08:00–20:00 Israel time), once per 2 hours off-hours.** UNRESOLVED until rate-limit confirmation (§G.4 in pack). Window 5 approves final cadence.
- Later Slice 3 (webhook) has no cadence — push-driven.

### C.2 What constitutes a healthy run

- HTTP 2xx from LionWheel
- Zod schema validation passes for every ingested entity
- At least one record observed in the response (or explicit empty-OK for list endpoints)
- `integration_run.status = 'succeeded'` set at finish
- `records_failed = 0`
- Freshness view flips to `fresh` for the entity within 1 minute

### C.3 What constitutes stale

- No successful run for entity within the threshold in §C.6 of the pack (proposed: 60 min non-terminal tasks, 24 h terminal tasks, 30 min for `lw_route` during operating hours)
- `freshness_status_view.status = 'stale'`
- Portal consumers must render a staleness banner; **must not suppress** the read model entirely on stale (that's broken-state behaviour)

### C.4 What constitutes broken

- `error_class = 'auth'` persisting > 5 minutes
- Webhook stream silent > threshold AND `/routes` sweep also failing (dual-path broken)
- Schema drift detected and sync halted for entity

### C.5 Reconciliation rules — duplicate / partial / cancelled / split / merged

| Case | Detection | Mirror behavior | Downstream effect |
|---|---|---|---|
| **Duplicate** — same payload received twice (e.g., webhook retry) | incoming `updated_at` ≤ stored watermark | `records_skipped_stale += 1`; no-op; `integration_run` still records the attempt with `records_attempted=1, records_upserted=0, records_skipped_stale=1` | no change |
| **Partial payload** — response truncated or parse fails mid-array | parse exception | `integration_run.status = 'partial'`; committed records stay; `error_class = 'partial_payload'`; re-fetch scheduled | downstream views see partial state; freshness flips `degraded` |
| **Cancelled** — task status transitions to `CANCELED` | incoming `status = 'CANCELED'` with later `updated_at` | standard upsert; `is_terminal` flips true; `records_retired += 1`; no soft-delete, row stays | `open_orders_view` drops the task (filters `is_terminal = false`); `shipment_status_view` shows cancelled state |
| **Split** — original order produces multiple tasks sharing `wp_order_id` | observed via `/tasks/by_order_id` returning array, or via two separate webhook events with same `wp_order_id` | both `lw_task` rows exist independently; `wp_order_id` index is non-unique; neither row blocks the other | `open_orders_view` returns both tasks as separate open orders; `demand_impact_view` aggregates `order_items` across all tasks for the `wp_order_id` |
| **Merged** — UNRESOLVED (§G.5 in pack) | not yet observed | **FAIL-SAFE:** if a task mysteriously disappears from `/tasks/show/:id` (404) while still referenced in `open_orders_view`, emit an exception and do NOT delete the mirror row. Let reconciliation pass (Slice 4) decide. | orphan exception surfaces in Exceptions Inbox |
| **Retired** — any terminal status | `is_terminal = true` after upsert | mirror row stays; stops propagating to `open_orders_view`; freshness relaxes to 24 h threshold | planning engine (Gate 5) excludes from demand |
| **Schema drift** — unknown enum / new required field | Zod validation fails | run status `failed` for that entity; no partial write of the affected record; alert | freshness flips `broken` for the entity; downstream views may fall back to last-known with banner |

### C.6 Safe-disable / kill-switch

- Runtime flag: `LIONWHEEL_SYNC_ENABLED` (env var or feature-flag table row)
- When `false`:
  - All LionWheel fetchers exit immediately at entry; they record a single `integration_run` row per attempted invocation with `status='superseded'`, `trigger_source='kill_switch'`, and `error_class=null`
  - Webhook endpoint returns HTTP 200 and discards body (acknowledges LionWheel so it doesn't retry forever) but writes no mirror rows and records `integration_run` with `status='superseded'`
  - `freshness_status_view` transitions to `broken` for LionWheel entities within ~1 minute
- When flipped back to `true`:
  - No automatic backfill in Slice 1; operator triggers CLI refresh for any known-important `wp_order_id`s
  - In Slice 2+, scheduled sweeps resume on their natural cadence
  - Webhooks resume but the gap is visible in run history

**Scope of the switch:**
- Halts LionWheel sync only
- Does **not** affect Shopify, Green Invoice, platform operator workflows, or ledger writes
- Does **not** touch `stock_ledger`, `balance_anchors`, or any master table

### C.7 Read-model degradation rules

Per-view behaviour when source is stale or broken:

| View | Fresh | Degraded | Stale | Broken |
|---|---|---|---|---|
| `open_orders_view` | render normally | render with banner | render with staleness badge | **suppress**; show "LionWheel integration unavailable" placeholder |
| `shipment_status_view` | render normally | render with banner | render with badge; suppress `delivered` / `failed` terminal claims (show "last known") | suppress terminal claims entirely |
| `demand_impact_view` | safe to consume | **refuse planning compute** | **refuse planning compute** | **refuse planning compute** |
| `freshness_status_view` | always renders | always renders | always renders | always renders — it's the view that reports the breakage |
| `net_availability_view` (future, post-Gate-3) | n/a for Slice 1 | n/a | n/a | n/a |

**Rule for Window 2 consumers:** the portal reads `freshness_status_view` before rendering any LionWheel-sourced table, and applies the degradation rule above. The portal does NOT infer stale/broken state from the data itself — it reads the view.

---

## Phase D — Parallel-safe next-move register

### D.1 What Window 1 must build FIRST

Before Slice 1 can run:

1. Migration for `integration_run` (shape per §B.5)
2. Migration for `lw_task` (shape per §B.2)
3. Migration for `lw_visit` (shape per §B.3)
4. Migration for `lw_order_item` (shape per §B.4)
5. Migration for `freshness_status_view` (shape per §B.6)
6. pgTAP tests per §B.9 (cases V.1–V.12)
7. Rollback migration(s) — all of the above must be dropppable without touching `stock_ledger` / `balance_anchors` / masters
8. Runbook entry documenting schema ownership boundary (Window 1 author, Window 4 consumer)

Window 1 also MAY:
- Propose a `freshness_policy` lookup table (`entity`, `threshold_minutes`) if preferred over hardcoded thresholds
- Propose alternate schema name to `integrations_lionwheel` if Window 1 has convention constraints

### D.2 What CAN be built in parallel with Gate 3 (NOW)

These are parallel-safe with Gate 3 because they produce zero runtime state and do not touch stock-truth surfaces:

- [x] Contract pack authoring (DONE — [window4-lionwheel-contract-pack.md](window4-lionwheel-contract-pack.md))
- [x] Runtime handoff spec (THIS DOCUMENT)
- [ ] Window 1 authors mirror migrations (D.1 above) — Window 1's queue
- [ ] Window 4 authors Zod schemas matching §B.2 / §B.3 / §B.4 shapes (TypeScript, no runtime calls) — Window 4's queue
- [ ] Window 4 drafts fetcher module interface (typed, unimplemented — just the contract between caller and fetcher) — Window 4's queue
- [ ] Window 4 authors CLI entry-point skeleton that validates args + env and exits before any HTTP call — Window 4's queue
- [ ] Rotate the LionWheel token (§G.11 in pack) — operator action

### D.3 What ABSOLUTELY must wait for Gate 3 exit

- `net_availability_view`
- `demand_impact_view` consumption by planner workspaces
- Any PO recommendation consuming LionWheel-derived demand
- Any Shopify FG sync direction change
- Any planning engine code that reads mirror views

### D.4 What must wait for Gate 5

- `demand_impact_view` surfacing in planner workspaces
- Purchase recommendations consuming the mirror
- Production recommendations consuming the mirror
- Forecast freeze-window interaction with mirror demand

### D.5 What must wait for Slice 1 completion

Before Slice 2 (`/routes` sweep) starts:
- Slice 1 idempotency verified on fixture replay
- Slice 1 evidence produced for every V.1–V.12 test case
- Kill-switch verified
- `freshness_status_view` verified

Before Slice 3 (webhook) starts:
- Slice 1 + Slice 2 stable for at least one full day under real load
- Webhook signature / replay-protection scheme designed and Window-5-approved
- Public HTTPS endpoint available

---

## Phase E — Runtime blocker register

Items that must be resolved before Slice 1 can run, grouped by ownership:

### E.1 Window 1 must complete before Slice 1

| Blocker | Dependency | Resolving evidence |
|---|---|---|
| Migration for `integration_run` | Window 1 authors DDL | migration file present + pgTAP passes |
| Migrations for `lw_task`, `lw_visit`, `lw_order_item` | Window 1 authors DDL | migration files present + pgTAP passes |
| View `freshness_status_view` | Window 1 authors view | view exists + returns expected shape |
| pgTAP V.1–V.12 | Window 1 authors tests | tests exist + pass against clean schema |
| Rollback migrations | Window 1 authors downgrades | rollback runbook documented |

### E.2 Window 4 must complete before Slice 1 (parallel-safe now)

| Blocker | Dependency | Resolving evidence |
|---|---|---|
| Zod schemas matching §B.2 / §B.3 / §B.4 | Window 4 authors types | `.ts` files exist under Window-4-owned path |
| Fetcher module interface | Window 4 authors type-only module | interface file exists, no HTTP yet |
| CLI skeleton (no HTTP) | Window 4 authors | CLI exits gracefully on `--help`, validates required args |
| Secret-store wiring design | Window 4 + ops | documented: where does `LIONWHEEL_API_TOKEN` live, how is it read at runtime |

### E.3 Operator / business blockers (Tom)

| Blocker | Who resolves | Resolving evidence |
|---|---|---|
| Token rotation (§G.11 pack) | Tom | new token generated, old revoked, new token in secret store |
| Freshness threshold lock (§G.9 pack) | Tom | numeric thresholds agreed per entity |
| Multi-visit partial-shipment usage (§G.6 pack) | Tom | operator confirmation; affects `shipment_status_view` semantics |
| COD field usage (§G.7 pack) | Tom | operator confirmation; affects whether to promote COD fields from `raw_payload` |
| Custom Hebrew-keyed fields stability (§G.8 pack) | Tom | admin inspection of LionWheel org settings |
| `driver_note` / Green Invoice URL handling (§G.12 pack) | Tom + Green Invoice contract pack | decision: mirror as-is / redact / cross-link |

### E.4 LionWheel-side blockers (require further inspection)

| Blocker | Dependency | Resolving evidence |
|---|---|---|
| `order_items[].quantity` precise type (§G.1 pack) | additional read-only inspection call capturing full order_items array | single task pull with small order_items observed end-to-end |
| Enum completeness for `route.status`, `task.pick_status`, `task.roundtrip_status`, `task.urgency`, `task.delivery_confirmation_status`, `visit.kind` (§G.2) | either LionWheel support confirmation or ~1 week production observation | documented enum set OR Window 4 accepts text+schema-drift-logging as permanent resilience |
| Rate limit numbers (§G.4) | LionWheel support OR production observation | documented rate limit; Slice 2 cadence lockable |
| Split/merge exact mechanics (§G.5) | observed real event OR support confirmation | documented mechanic; reconciliation rules C.5 verified |
| Webhook payload exact shape (§G.3) | one observed webhook delivery | field-by-field comparison with `/tasks/show` response |
| Sandbox usability (§G.10) | test sandbox credential against real-shape expectation | sandbox confirmed as safe test environment OR rejected as unrealistic |

### E.5 Windows 2 and 5 are NOT runtime blockers for Slice 1

- Window 2 portal is not a consumer in Slice 1. Slice 1 is CLI-driven.
- Window 5 governance sign-off is needed only at scheduler-cadence locks (Slice 2+) and webhook endpoint design (Slice 3+).

---

## F. Final verdict

**STATUS: CONTRACT_READY_BUT_RUNTIME_BLOCKED**

Runtime is NOT ready. This spec is handoff-ready for Window 1 and for Window 4's own parallel-safe prep work. Runtime cannot begin until:

1. Window 1 completes D.1 migrations + pgTAP (authorial work, not external blockers)
2. Window 4 completes E.2 scaffolding (authorial work)
3. Operator resolves E.3 items (Tom)
4. **Slice 1 does not require Gate 3 exit.** Slice 1 only produces mirror rows and freshness-view rows; it does not feed planning. Gate 3 exit is required before Slice 5 (portal view exposure) and before any planning-engine consumption of mirror demand.

### F.1 Completion estimate

Per the user's instruction — **contract packs do not count as runtime completion.**

Overall project runtime completion estimate (Gates 1–5 weighted equally for this estimate):

- **Gate 1 (Alignment / Contracts):** ~85–95% complete — architecture, input-source, schema, portal module, migration phases, validation gates, and rollback logic exist or are in flight
- **Gate 2 (Foundation / Masters / Admin):** ~60–75% complete — schema foundation present, auth scaffolded (dev-shim auth per memory), master-data import in flight, admin CRUD partial, nightly export not yet live
- **Gate 3 (Stock Truth):** ~20–35% complete — Goods Receipt FILE_READY in window2-portal-sandbox per memory, ledger/anchors/projection contracts exist, parity/rebuild-verification gates not yet run
- **Gate 4 (Mirrors / Forecasting):** **0% runtime complete** (contract pack + runtime handoff spec exist but do not count per user rule)
- **Gate 5 (Planning / Recommendations):** 0% runtime complete

**Overall project runtime completion: ~30–40% against the 5-gate model.**

Stage: **still Stage 3 (stock truth).** Gate 4 work visible here is parallel-safe preparation only, not runtime.

### F.2 Why not RUNTIME_HANDOFF_READY

Two independent reasons, either of which individually precludes `RUNTIME_HANDOFF_READY`:

1. **Window 1 has not yet authored the mirror migrations** (D.1). Until those exist, the fetcher has no target to write to.
2. **Operator blockers E.3 are unresolved** — most critically, token rotation. Running Slice 1 with the in-conversation token is an avoidable exposure.

Either of these becomes resolvable independently. Once BOTH are resolved, a subsequent Window 4 pass can flip the verdict to `RUNTIME_HANDOFF_READY` and Slice 1 can run.

---

## G. Self-check against foundation

- [x] No DDL authored — all schema is "proposed shape", Window 1 finalizes
- [x] No migration files created
- [x] No scheduler wiring
- [x] No webhook endpoint code
- [x] No portal touch
- [x] No planning engine work
- [x] No live LionWheel write calls
- [x] No invented LionWheel fields — every field traces to the accepted contract pack (Appendix A of that pack contains the live-inspection evidence)
- [x] `wp_order_id` non-unique preserved (§B.2, §C.5)
- [x] Monetary / quantity string-decimal preservation preserved (§B.2 `order_total text`, §B.4 `quantity/price text`)
- [x] No generic `/tasks` list endpoint assumed — Slice 1 is `/tasks/show/:task_id`, Slice 2 `/routes?date=`
- [x] Gate 3 not regressed — Slice 1 produces zero stock-truth state
- [x] Stock-truth dependency map from pack §D.6 preserved and referenced (C.7, D.3, D.4, E.5)
- [x] Kill-switch scope does NOT touch `stock_ledger` / `balance_anchors` / masters (C.6)
- [x] Contract pack does NOT count as runtime completion in the estimate (F.1)
- [x] Runtime verdict is honest — CONTRACT_READY_BUT_RUNTIME_BLOCKED, not RUNTIME_HANDOFF_READY

---

**END — Window 4 LionWheel runtime handoff spec.**

Next Window 4 pass: parallel-safe E.2 scaffolding (Zod schemas, fetcher interface, CLI skeleton) — authorable now alongside Window 1's D.1 migration work.
