# Window 4 — LionWheel Contract-First Integration Pack

**Owner:** Window 4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Status:** contract-complete, runtime NOT built, pre-Gate 4 precursor
**Date authored:** 2026-04-17
**Inspection basis:** live read-only LionWheel API calls performed during this session, see Appendix A

This pack is **not** an implementation. It is a contract specification. No migrations, no sync runtime, no scheduler wiring, no portal code were produced. Mirror table DDL is explicitly deferred to Window 1. Planning-engine consumption is explicitly deferred to Gate 5.

---

## Phase A — Source boundary truth (foundation restatement)

LionWheel is the operational source for **open orders and shipment state**. It is **mirrored internally**, not queried live for every computation. It is **not the planning engine**. It is **not stock truth**. Split, merge, and cancel are first-class reconciliation concerns.

The GT platform database remains authoritative for master data, stock events, stock projections, planning runs, and audit trails. LionWheel does not override any of those. On any conflict between a LionWheel value and a platform value for a field the platform owns, the platform wins. On conflicts about open-order and shipment state, LionWheel wins and the mirror reconciles.

### A.1 What LionWheel IS authoritative for

- existence and identity of a delivery task (LionWheel `task_id`, `public_id`)
- operational delivery status transitions (the `status` enum, see §B.8)
- visit-level delivery execution state (`is_done`, `delivered_at`, `failed_at`)
- driver / route assignment
- pickup and dispatch timestamps (`pickup_at`, `completed_at`, `created_at`, `updated_at`)
- the `order_items` line-item set **as LionWheel received it at task creation time** (this is a *snapshot*, not a live line-item source)

### A.2 What LionWheel is NOT authoritative for

- stock truth, in any form
- FG stock levels (Shopify is the sync target; platform is authoritative on disagreement)
- BOM explosion or planning demand
- component-level consumption (BOM-derived on GT side)
- master-data SKU catalog (GT item master is authoritative; `order_items.sku` is matched, not trusted as a catalog source)
- pricing truth (LionWheel carries `order_total` and `order_items[].price` as-received from the originating commerce channel; active supplier/customer pricing is not LionWheel's domain)
- customer/company master (LionWheel `company_id` is scoped to LionWheel's own customer model; see §B.9)

### A.3 Concrete implications for integration design

1. **Mirror-first, not live-call.** Planning demand must never be computed by calling LionWheel inside a computation path. The mirror is read.
2. **No generic list-tasks endpoint exists.** See §B.1. The mirror cannot "SELECT *" from LionWheel. Push-based (webhook) is the primary freshness path; `/routes?date=` is the reconciliation sweep.
3. **Tasks carry `creation_origin` metadata.** Observed value for GT: `"shopify"`. This means the commerce channel is upstream of LionWheel. The mirror must preserve this field for provenance; it must **not** use it to re-source stock or master data.
4. **`order_items` is a snapshot taken at task creation, not a live commerce feed.** Edits in Shopify after task creation may not reflect on the LionWheel task. The mirror must treat `order_items` as LionWheel-frozen.
5. **Split / merge / cancel is observed through status transitions and new task creation, not through explicit split/merge events.** §B.10 defines the reconciliation rules.

---

## Phase B — Inbound data contract pack

Entities in scope for v1. Anything marked **(inspected)** was observed in a live response during this session; **(docs)** was observed only in official docs; **UNRESOLVED** requires further inspection or operator input before runtime.

### B.1 Endpoint inventory (authoritative for this pack)

| HTTP | Path | Purpose | Evidence |
|---|---|---|---|
| GET | `/api/v1/routes?date=YYYY-MM-DD&format=json` | list routes for a date, each embedding its visits array (inspected) | live call returned array of routes; see Appendix A |
| GET | `/api/v1/tasks/show/:task_id` | full task detail (inspected) | live call returned `{task:{...}}` |
| GET | `/api/v1/tasks/by_order_id/:order_id` | all tasks matching an external order id (inspected) | live call returned `{tasks:[...]}` — **array, supports multiple tasks per order** |
| GET | `/api/v1/tasks/by_phone/:phone` | search by recipient phone (docs) | not inspected in this session |
| GET | `/api/v1/drivers/:driver_id/daily_route` | driver daily route (docs) | not inspected |
| GET | `/api/v1/visits/:visit_id` | single visit (docs) | not inspected |
| GET | `/api/v1/companies/:company_id` | company detail (docs) | not inspected |

**No generic `GET /tasks` listing endpoint exists.** This is the single most important design constraint. See §C for the freshness model implication.

### B.2 Authentication contract

- **Method:** query parameter `key=<token>` on every request. Not a header.
- **Token types:**
  - **shipping-company key** — organization-scoped; no `c_key` prefix. GT's token is of this type (confirmed by absence of prefix and by successful `/routes` response listing GT tasks).
  - **customer key** — prefix `c_key_...`; customer-scoped (docs).
- **Error shapes (inspected):**
  - HTTP 401 → `{"error":"API Key is wrong"}`
  - HTTP 404 → `{"error":"Not found"}`
- **Transport:** HTTPS. Base URL: `https://members.lionwheel.com/api/v1`.

### B.3 Answer to the COMPANY_ID question

`company_id` is **NOT required** for read-only calls with a shipping-company key. The key itself scopes access to the organization. However:

- Observed on GT tasks: `organization_id: 2074`, `company_id: 34859`. The `company_id` identifies GT as a customer-record inside LionWheel's tenancy model.
- The mirror **must persist** `organization_id` and `company_id` for every mirrored task for provenance and future multi-tenant reconciliation, even though they do not need to be sent as request parameters.
- `company_id` is only needed as a **request parameter** on **write** calls (delivery creation) to associate a new task with a specific customer record — and Window 4 is not doing writes in this pack.

### B.4 Entity — `route` (inspected)

**Purpose in GT:** the day-indexed driver plan that embeds visits. Primary vehicle for the reconciliation sweep.

| Field | Type observed | Notes |
|---|---|---|
| `id` | integer | route id; mirror-side internal FK source |
| `date` | string `"DD/MM/YYYY"` | **note Hebrew date format**, not ISO; must parse explicitly |
| `name` | string | display name, e.g. `"דורין 16/04/2026"` |
| `driver_id` | integer | driver reference |
| `driver_str` | string | driver display name (Hebrew allowed) |
| `status` | string | observed value: `"planned"` — **enum not fully known** (UNRESOLVED) |
| `is_locked` | boolean | |
| `start_time` | string `"HH:MM"` | |
| `end_eta_at` | string `"HH:MM"` \| null | |
| `distance` | string `"225.74 KMs"` | **string with units**; `int_distance` carries meters |
| `int_distance` | integer \| null | meters |
| `polyline` | string \| null | encoded polyline; not operationally required |
| `color` | string | hex color for UI |
| `vehicle_id` / `vehicle_str` | nullable | vehicle assignment |
| `external_driver_id` | string | may be empty |
| `notes` | nullable string | |
| `assistant_driver_str`, `code`, `max_packages_quantity`, `max_surfaces_quantity`, `max_volume`, `max_weight`, `finish_location_id`, `finish_point_address`, `finish_visit_id`, `start_location_id`, `start_point_address`, `start_visit_id`, `weight`, `wait_time` | nullable / default values | low operational signal for v1; mirror-persist but don't consume |
| `visits` | array of `visit` (see B.5) | **embedded inline** in `/routes` response |

**Required for v1:** `id`, `date`, `driver_id`, `driver_str`, `status`, `visits[]`.
**Nice-to-have:** `distance`/`int_distance`, `start_time`/`end_eta_at`, `polyline`.

### B.5 Entity — `visit` (inspected — union of fields from `/routes` and `/tasks/show`)

**Purpose in GT:** one physical stop (pickup or delivery). Tasks can have multiple visits when roundtrip or multi-stop.

| Field | Type observed | Notes |
|---|---|---|
| `id` | integer | visit id |
| `task_id` | integer | FK to task |
| `route_id` | integer | FK to route |
| `organization_id` | integer | LionWheel organization |
| `company_id` | integer | LionWheel customer record |
| `driver_id` | integer | |
| `kind` | string | observed: `"DELIVERY"`. Other values UNRESOLVED (likely `"PICKUP"` exists but not inspected) |
| `is_done` | boolean | |
| `visit_at` | ISO8601 timestamp with TZ `+03:00` | |
| `delivered_at` | ISO8601 \| null | inspected on COMPLETED visit |
| `failed_at` | ISO8601 \| null | |
| `eta_at` / `early_eta_at` / `late_eta_at` / `eta_at_formatted` / `eta_window` | nullable | |
| `earliest_at` / `latest_at` / `earliest` / `latest` / `earliest_latest_time` | nullable | time-window fields |
| `loaded_at` | ISO8601 \| null | pickup-side timestamp |
| `created_at` / `updated_at` | ISO8601 | |
| `recipient_name` | string | **Hebrew allowed**, observed Hebrew values |
| `phone` | string `"+972..."` | E.164 format observed |
| `phone2` | string | may be empty |
| `email` | string | may be empty |
| `city` / `street` / `number` / `apartment` / `floor` / `zip_code` / `entrance` / `entrance_code` | strings / nullable | **Hebrew allowed** in `street`, e.g. `"שמשון זליג"` |
| `latitude` / `longitude` | number | WGS84 |
| `delivery_latitude` / `delivery_longitude` | nullable number | delivery-confirmed geo |
| `region_str` | string | |
| `state` | nullable string | |
| `geo_provider` | string | observed: `"shopify"` |
| `geo_type` | nullable | |
| `is_location_fixed` | boolean | |
| `ignore_location_warning` | boolean | |
| `geo_fence_id` / `location_id` / `location_cache_id` | nullable integer | |
| `matches_count` / `partial_match` | nullable | geo-match diagnostics |
| `notes` | string | may be empty |
| `packages_quantity` | integer | per-visit package count |
| `surfaces_quantity` / `volume_number` | nullable / number | |
| `priority` | nullable | |
| `group` / `daily_order` | nullable | sort/grouping within route |
| `failure_reason` | nullable string | free-text failure note |
| `salary` / `salary_origin` | nullable | driver compensation; **not for GT operational use** |
| `route_locked` | boolean (from /routes response) | |
| `route_name` | string (from /routes response) | |
| `task_status` | string (from /routes response) | **duplicate of task.status for convenience** — see B.8 |
| `wp_order_id` | string (from /routes response) | **duplicate of task.wp_order_id** — see B.7 |
| **(custom fields)** | Hebrew-keyed strings observed in one response: `"להוציא באישור"`, `"לא שולם"` | UNRESOLVED — these appear to be org-configured custom fields; their schema and stability is unknown |

**Required for v1:** `id`, `task_id`, `route_id`, `kind`, `is_done`, `visit_at`, `delivered_at`, `failed_at`, `recipient_name`, `phone`, city/street/number, `packages_quantity`, `notes`, `failure_reason`.
**Nice-to-have:** full geo set, eta fields, loaded_at.
**Out of v1:** salary fields, polyline metadata, custom Hebrew-keyed fields until their stability is confirmed.

### B.6 Entity — `task` (inspected — GT's "delivery order")

**Purpose in GT:** the unit of outbound commitment. The operational open-order object. One task = one shipment event from GT's perspective.

| Field | Type observed | Notes |
|---|---|---|
| `id` | integer | internal LionWheel task id |
| `public_id` | string | e.g. `"M93TRM2PZZ"` — human-friendly id |
| `organization_id` | integer | observed GT value: 2074 |
| `company_id` | integer | observed GT value: 34859 |
| `status` | string | see §B.8 |
| `pick_status` | string | observed: `"NEW"` — enum UNRESOLVED |
| `roundtrip_status` | string | observed: `"UNRETURNED"` — enum UNRESOLVED |
| `urgency` | string | observed: `"REGULAR"` — enum UNRESOLVED |
| `is_roundtrip` | boolean | |
| `same_day` | boolean | |
| `notes` / `org_note` / `driver_note` | string / nullable | free text; **note:** `driver_note` observed to contain a Green Invoice signed document URL — cross-system link (see §D.3) |
| `packages_quantity` | integer | |
| `cartons_quantity` / `surfaces_quantity` / `weight` / `volume` | nullable | |
| `pickup_at` | ISO8601 | authoritative dispatch target |
| `created_at` | ISO8601 | mirror ingest watermark source |
| `updated_at` | ISO8601 | **primary change-detection watermark** |
| `completed_at` | ISO8601 \| null | terminal timestamp |
| `wp_order_at` | ISO8601 | original commerce order timestamp |
| `wp_order_id` | string | observed format `"#GT12519"` — **commerce order external id, primary GT-side reconciliation key** |
| `wp_order_key` | string | observed `"7066461536497"` — **numeric, aligns with Shopify order id semantics when `creation_origin="shopify"`** |
| `creation_origin` | string | observed: `"shopify"` — provenance |
| `creation_trigger` | string | observed: `"automatic"` |
| `driver_id` | integer | |
| `vehicle_kind` | nullable | |
| `delivery_method` | string | may be empty |
| `money_collect` / `payment_method` / `money_transferred` / `money_transferred_at` / `cod_type` (docs) | nullable | COD-related; **not operationally used by GT** in v1 (assumption — confirm with Tom) UNRESOLVED |
| `order_total` | string decimal, e.g. `"370.50"` | **string, not number** — parse carefully |
| `signature_url` / `signature` / `signee_name` / `signed_document` | nullable | proof-of-delivery artifacts |
| `is_photo_attached` / `is_document_attached` / `photos` / `documents` (docs) | boolean / array | artifact presence flags |
| `price` / `fee_cost` | nullable | LionWheel-side cost fields; **not GT revenue** — UNRESOLVED whether these are operator-visible |
| `document_number` / `document_type` / `invoice_id` / `distribution_id` | nullable | cross-system references |
| `batch_id` / `branch_id` / `warehouse_id` / `client_id` / `user_id` / `other_user` / `payer` | nullable | LionWheel org-scoped FKs; mirror-persist for provenance only |
| `target_partner_task_id` / `origin_partner_task_id` / `target_partner_bridge_id` / `origin_partner_bridge_id` / `target_partner_task_status` / `target_partner_transfer_type` / `origin_partner_transfer_type` / `origin_partner_company` / `transferred_at` / `transfer_errors` / `external_line_branch` / `external_distribution_line` | nullable | **partner-transfer model** — out of v1 scope until GT confirms use |
| `printed_at` / `ready_to_print` | timestamp / boolean | print workflow state |
| `age_verification` / `age_start_date` / `leave_next_to_door` / `is_self_pickup` / `is_free` | boolean / date | delivery modifiers |
| `validation_status` / `validation_link_sent_at` / `delivery_confirmation_status` / `confirmation_link_sent_at` / `confirmation_updated_at` / `delivery_decline_reason_id` | nullable / string | **customer-confirmation workflow** — observed `delivery_confirmation_status: "NOT_SENT"`; enum UNRESOLVED |
| `returned_pallets` | nullable | |
| `scheduled_template_id` / `stop_time` / `wait_time` | nullable | |
| `skills` | array | observed empty `[]`; purpose UNRESOLVED |
| `failed_count` | integer | retry tracking |
| `sms_from_name` / `otp_code` / `extra_barcode` / `task_type` / `customer_user_agent` / `route_code` / `greeting` / `gifter_name` / `gifter_phone` / `source_order_id` / `due_date` / `earliest` / `latest` | nullable / various | low operational signal for v1 |
| `visits` | array of `visit` (see B.5) | **embedded inline** |
| `photos` | array | POD photos |
| `order_items` | array of `order_item` (see B.7) | **embedded inline** |

**Required for v1:** `id`, `public_id`, `organization_id`, `company_id`, `status`, `pick_status`, `urgency`, `is_roundtrip`, `pickup_at`, `created_at`, `updated_at`, `completed_at`, `wp_order_id`, `wp_order_key`, `creation_origin`, `creation_trigger`, `driver_id`, `order_total`, `packages_quantity`, `visits[]`, `order_items[]`.

**Nice-to-have:** notes fields, POD artifacts, confirmation-workflow fields.

**Out of v1:** partner-transfer fields, COD fields, salary/price fields (unless Tom confirms need), custom Hebrew-keyed fields.

### B.7 Entity — `order_item` (inspected — embedded in task)

**Purpose in GT:** the line-item set as received by LionWheel at task creation. The primary bridge from a LionWheel task to GT's FG item master.

| Field | Type observed | Notes |
|---|---|---|
| `id` | integer | LionWheel-side line id |
| `sku` | string | **observed real GT SKU** `"GT-HIB-LOW-1L"` — matches GT item master SKU shape. **This is the join key to GT `items.id` / `items.sku`.** |
| `name` | string | observed `"FRESH 1000ml"` — human-readable product name |
| `variant` | nullable | |
| `quantity` | UNRESOLVED (response truncated at 4000 chars during inspection; docs declare `quantity` as a standard field) |
| `price` / `weight` / `notes` | docs-declared | not live-verified in this session |

**Required for v1:** `id`, `sku`, `name`, `quantity`.
**Nice-to-have:** `price`, `weight`, `variant`, `notes`.

**UNRESOLVED — critical:** confirm `quantity` is numeric (integer vs decimal) and whether `price` is string-decimal (mirroring `order_total`) or numeric. Live sample was truncated; needs a second inspection call fetching a task with small `order_items` entirely within a 2–4 KB response window, or jq-based precise capture.

### B.8 Status enum — `task.status` (authoritative)

From docs; one value (`COMPLETED`) live-confirmed:

| Integer | String |
|---|---|
| 0 | `UNASSIGNED` |
| 1 | `ASSIGNED` |
| 2 | `ACTIVE` |
| 3 | `COMPLETED` **(live-confirmed)** |
| 4 | `CANCELED` |
| 5 | `ROUNDTRIP_DELIVERED` |
| 6 | `IN_INVENTORY` |
| 7 | `OUT_INVENTORY` |
| 8 | `FAILED` |
| 9 | `FINAL_FAILED` |
| 10 | `IN_TRANSFER` |

**Mirror contract:** store status as the string form. Integer form exists for compatibility but is not the canonical persistence shape.

**Enums UNRESOLVED:**
- `route.status` — observed `"planned"` only
- `task.pick_status` — observed `"NEW"` only
- `task.roundtrip_status` — observed `"UNRETURNED"` only
- `task.urgency` — observed `"REGULAR"` only
- `task.delivery_confirmation_status` — observed `"NOT_SENT"` only
- `visit.kind` — observed `"DELIVERY"` only (expect `"PICKUP"` but not confirmed)

### B.9 Key catalogue — reconciliation identifiers

| Key name (LionWheel) | Scope | Stable? | Proposed mirror role |
|---|---|---|---|
| `task.id` (integer) | LionWheel-global | yes | **primary authoritative external key** for a task |
| `task.public_id` (string) | LionWheel-global | yes | human-friendly secondary key; operator-visible |
| `task.wp_order_id` (string `"#GT12519"`) | commerce-channel | **primary GT-side business key** | join key to GT commerce-order concept |
| `task.wp_order_key` (string numeric) | commerce-channel | aligns with Shopify order id when `creation_origin="shopify"` | secondary commerce reconciliation |
| `task.organization_id` (integer) | LionWheel-tenant | static for GT (`2074`) | store for provenance; not a join key |
| `task.company_id` (integer) | LionWheel-tenant | static for GT (`34859`) | store for provenance; not a join key |
| `visit.id` (integer) | LionWheel-global | yes | primary key for visit mirror |
| `route.id` (integer) | LionWheel-global | yes | primary key for route mirror |
| `driver_id` (integer) | LionWheel-org | yes | FK within mirror |

**Rule:** `task.id` is the authoritative external key. `wp_order_id` is the **business** reconciliation key GT consumes. Multiple tasks can share a `wp_order_id` — confirmed by `/tasks/by_order_id/` returning an array — so `wp_order_id` is **not unique** in the mirror and must not be a primary key.

### B.10 Cancellation / partial shipment / split / merge semantics

**Observed behavior:** none of these produced explicit events during the inspection session. Inferred model, to be verified:

- **Cancellation:** `task.status` transitions to `"CANCELED"` (enum value 4). Task is not deleted. `updated_at` advances. Mirror must treat `CANCELED` as a terminal retirement state and emit a reconciliation event downstream.
- **Partial shipment:** not directly modeled on the task object. Partial-completion state expressed via per-visit `is_done`/`delivered_at`/`failed_at` fields when a task has multiple visits. **UNRESOLVED** — whether GT's workflow uses multi-visit tasks for partial shipment needs operator confirmation.
- **Split:** when an order is split into multiple tasks, multiple tasks share `wp_order_id`. `/tasks/by_order_id/:order_id` returns the full set. **UNRESOLVED** — whether a split happens by cancelling-and-recreating or by adding tasks with the same `wp_order_id`.
- **Merge:** no observed mechanism. **UNRESOLVED** — whether LionWheel supports merging two tasks.
- **Retirement:** any task in `COMPLETED`, `CANCELED`, `FINAL_FAILED`, or `ROUNDTRIP_DELIVERED` is terminal. Mirror should mark the snapshot-run `retirement` flag on next sight and stop propagating changes downstream even if `updated_at` continues to advance for metadata reasons.

**Reconciliation rule for the mirror:** on any status transition into a terminal value, emit a `task_retirement` reconciliation signal. Downstream read models (see §D) must treat `CANCELED` tasks as **removed from demand** for planning purposes.

---

## Phase C — Integration run / freshness model (contract only, no DDL)

### C.1 `integration_run` contract shape

Purpose: one record per discrete sync attempt. Not a DDL spec; Window 1 will author the table.

| Field | Proposed type | Purpose |
|---|---|---|
| `id` | UUID | mirror-side primary key |
| `integration` | string enum | `"lionwheel"` for this pack; future: `"shopify"`, `"green_invoice"` |
| `run_kind` | string enum | `"webhook_ingest"` \| `"routes_sweep"` \| `"task_refresh"` \| `"reconciliation_pass"` |
| `status` | string enum | see C.2 lifecycle |
| `started_at` | timestamptz | |
| `finished_at` | timestamptz \| null | |
| `duration_ms` | integer \| null | |
| `records_attempted` | integer | |
| `records_upserted` | integer | |
| `records_retired` | integer | |
| `records_failed` | integer | |
| `error_class` | string \| null | controlled vocabulary, see C.4 |
| `error_detail` | jsonb \| null | redacted payload sample on failure; must not store tokens |
| `request_watermark_from` | timestamptz \| null | for `task_refresh` runs using `updated_at` |
| `request_watermark_to` | timestamptz \| null | |
| `sweep_date` | date \| null | for `routes_sweep` runs |
| `trigger_source` | string | `"scheduler"` \| `"webhook"` \| `"manual"` \| `"reconciliation_job"` |
| `trace_id` | string | correlation id for logs |
| `evidence_sample` | jsonb \| null | small redacted sample of what was ingested, for audit |

### C.2 Run status lifecycle

```
pending --> running --> succeeded
                   \--> failed
                   \--> partial  (some records upserted, some failed)
                   \--> superseded (newer run overtook this one)
```

**Rules:**
- `succeeded` requires `records_failed == 0` and `finished_at != null`.
- `partial` is the honest state for a run that ingested some but not all records; downstream freshness views must treat `partial` as degraded.
- `superseded` lets a long-running reconciliation yield to a fresher run without being marked failed.

### C.3 Success / failure evidence recorded per run

- **Per run:** status, counts, duration, watermarks, error class, trace id.
- **Per ingested entity (not in `integration_run` itself — belongs in mirror tables Window 1 authors):** `mirror_ingested_at`, `mirror_source_run_id` (FK to `integration_run.id`), `mirror_source_watermark` (the `updated_at` observed at ingest).

### C.4 Error class controlled vocabulary

| Class | Meaning | Retry posture |
|---|---|---|
| `auth` | 401 from LionWheel | **stop all sync, page operator**; never retry blindly |
| `not_found` | 404 on a specific entity fetch | **record and continue** — not a run-level failure |
| `rate_limit` | HTTP 429 if ever observed | exponential backoff; UNRESOLVED whether LionWheel emits 429 (no rate-limit info in docs) |
| `network_timeout` | connect/read timeout | bounded retry, then fail |
| `schema_drift` | unexpected field shape or new enum value | **stop ingest for that entity**, emit exception, do not silently coerce |
| `partial_payload` | response truncated / parse failure | record, re-fetch |
| `unknown` | anything else | fail the run; operator inspects |

### C.5 Rate-limit assumptions

**UNRESOLVED.** LionWheel public docs do not state rate limits. Runtime must:
- self-throttle `/routes?date=` sweeps to one per date per minute at most
- treat any non-200, non-401, non-404 response as a potential rate-limit signal
- observe in production for one week before committing to a bounded retry budget

### C.6 Freshness indicators (what "fresh" means, per entity)

| Entity | Freshness rule | Stale threshold (proposed, not locked) |
|---|---|---|
| `task` (non-terminal status) | last-seen `updated_at` from any of: webhook, `/tasks/show` refresh, `/routes` sweep, `/tasks/by_order_id` lookup | **stale if no confirmation within 60 min** for non-terminal; **stale if no confirmation within 24 h** for terminal |
| `route` | `/routes?date=today` call succeeded within threshold | **stale if no successful sweep of today's date within 30 min during operating hours** |
| `visit` | inherits from its parent task | same as task |
| `company` / `driver` | refreshed on demand | **stale if last refresh > 7 days** |
| `webhook stream` | last webhook received | **stale if no webhook received for any status within 4 h during operating hours** (assuming GT has non-zero daily volume) |

**Proposed-not-locked:** every threshold above needs operator confirmation from Tom before runtime lock. Marked UNRESOLVED in §G.

### C.7 Stale-data detection rule

The mirror maintains a per-entity `freshness_status` view (see §D.4). A downstream read is:
- **trustable** if the source is `fresh`
- **degraded** if `partial` (last run ingested some not all)
- **stale** if the freshness threshold is breached
- **broken** if `auth` class error has been in effect for > 5 minutes

### C.8 Alert conditions (what emits, where it goes conceptually)

- `auth` error persisting > 5 min → **immediate operator alert** (delivery mechanism deferred to Window 5 / ops)
- Webhook stream silent > threshold during operating hours → **ops alert**
- `/routes` sweep failed for today's date > 30 min → **ops alert**
- Schema drift detected (unknown enum value, new required field) → **developer alert + sync halt for affected entity**
- Reconciliation pass found tasks in the mirror with no upstream match (orphans) → **reconciliation exception** routed to the Exceptions Inbox (Gate 3 concept)

### C.9 Minimum observability for operator / admin

1. "Last successful run" timestamp per integration + run_kind
2. Current freshness status per entity
3. Last 24 h of run outcomes (succeeded / failed / partial counts)
4. Open reconciliation exceptions
5. Webhook-stream heartbeat

None of these need runtime code in this pack; they are contract requirements that constrain the eventual dashboard implementation (Window 4 dashboard contracts domain).

---

## Phase D — Downstream read models + stock-truth dependency map

### D.1 Read model — `open_orders_view`

- **Name (proposed):** `open_orders_view`
- **Consumer:** Window 2 portal (planner screens), eventual Window 4 dashboard, future Gate 5 planning engine
- **Source entities:** `task` (mirror), filtered by `status NOT IN ('COMPLETED','CANCELED','FINAL_FAILED','ROUNDTRIP_DELIVERED')`
- **Update dependency:** `task` mirror fresh within task freshness threshold (§C.6)
- **Required now | later:** **later** — planner consumption waits until Gate 3 exits
- **What cannot be trusted if freshness is broken:** the entire "what is still outstanding" signal — if webhook stream is stale and no sweep ran, outstanding orders shown may already be completed upstream
- **Stale rendering policy:** safe to render with a **staleness badge** when degraded; **suppress entirely** if broken (auth error)

### D.2 Read model — `shipment_status_view`

- **Name (proposed):** `shipment_status_view`
- **Consumer:** Window 2 portal (operator shipment-status lookups), eventual dashboard
- **Source entities:** `task` + `visit` (mirror); surfaces per-task status and per-visit execution state
- **Update dependency:** `task` + `visit` fresh
- **Required now | later:** **later**
- **What cannot be trusted if freshness is broken:** delivered/failed status claims for any visit with `updated_at` older than threshold
- **Stale rendering policy:** badge when degraded; suppress terminal-state claims (delivered vs failed) when broken

### D.3 Read model — `demand_impact_view`

- **Name (proposed):** `demand_impact_view`
- **Consumer:** **Gate 5 planning engine only.** Not for v1 portal rendering.
- **Source entities:** `open_orders_view` aggregated by GT `items.id` via join on `order_items.sku` → `items.sku`. Group by item; sum `order_items.quantity` for all non-terminal tasks.
- **Update dependency:** `task` + `order_items` fresh; **also** depends on GT `items` master being authoritative (handled by Gate 2 master-data load).
- **Required now | later:** **later** — blocked until Gate 3 stock-truth exits and Gate 5 planning engine begins.
- **What cannot be trusted if freshness is broken:** planning input becomes fiction. **Planning must refuse to run** if this view's source is `stale` or `broken`.
- **Join-safety note:** `order_items.sku` matching to `items.sku` requires GT item master to hold every SKU that LionWheel can deliver; unmatched SKUs must route to an exception, **not** be silently dropped or create pseudo-items. Enforces CLAUDE.md "never auto-create components from integration payloads."

### D.4 Read model — `freshness_status_view`

- **Name (proposed):** `freshness_status_view`
- **Consumer:** dashboard + operator banner + planner gate
- **Source entities:** `integration_run` + per-mirror-entity `mirror_source_watermark` watermarks
- **Update dependency:** self (computed from the mirror's own run history)
- **Required now | later:** **needed concurrent with the mirror going live** — the freshness view must exist before any mirror-dependent read model is exposed to planners
- **What cannot be trusted if freshness is broken:** nothing; this view describes the brokenness
- **Special rule:** this view must be **cheap to query** and **never blocked** by the same failures it is reporting on

### D.5 Read model — `shopify_fg_sync_reconciliation_view` (optional for this pack, flagged)

- **Name (proposed):** `shopify_fg_sync_reconciliation_view`
- **Consumer:** ops / admin
- **Source entities:** LionWheel `order_items` snapshots + Shopify FG stock deltas + platform FG projection
- **Required now | later:** **later** — touches Shopify integration which is a separate contract pack; **out of scope** for this Window 4 LionWheel-only pass but noted here because LionWheel `creation_origin="shopify"` links the two domains.

### D.6 Stock-truth dependency map (required, separate section)

This is the honest dependency register. **Do not collapse softer dependencies into stronger ones, and do not mark Gate-3-dependent views as "ready now" to look further along.**

| Read model | Depends on Gate 3 stock truth? | Type of dependency |
|---|---|---|
| `open_orders_view` | **No** | pure LionWheel mirror; independent of stock truth |
| `shipment_status_view` | **No** | pure LionWheel mirror |
| `freshness_status_view` | **No** | self-describing mirror state |
| `demand_impact_view` | **No for correctness of demand signal itself; YES for operational safety** | demand can be computed without stock truth, but it is **dangerous to feed into planning** before stock truth is trusted — planning with bad stock + good demand still produces bad POs |
| `net_availability_view` *(not yet defined; will combine demand and stock)* | **YES, hard dependency** | cannot exist until Gate 3 exits; cannot be rendered for planners until then |
| `shopify_fg_sync_reconciliation_view` | **YES, hard dependency** | platform FG projection must be trusted before it can be declared authoritative against Shopify |

**Consumer-side blocking rule for Window 2 (portal) and Gate 5 (planning):**
- `open_orders_view`, `shipment_status_view`, `freshness_status_view` — may render with the staleness-badge contract even before Gate 3 exits, **as operator-visibility-only surfaces**; they must not be used to drive stock decisions
- `demand_impact_view` — do not expose to planners until Gate 3 has exited and a `net_availability_view` wraps it with stock context
- `net_availability_view` — do not build until Gate 3 has exited

### D.7 Inter-window consumer map

| Read model | Window consuming | When |
|---|---|---|
| `open_orders_view` | Window 2 portal (read-only), Window 4 dashboard | after mirror runtime lights up, post-Gate-3-exit recommended |
| `shipment_status_view` | Window 2 portal, Window 4 dashboard | same |
| `demand_impact_view` | Gate 5 planning engine (computed server-side) | Gate 5 only |
| `freshness_status_view` | every consumer surface | concurrent with mirror go-live |

---

## Phase E — Future runtime implementation sequence (plan, not implementation)

### E.1 Prerequisites from Window 1

Before the mirror runtime lights up:

1. Window 1 authors migrations for:
   - `integration_run` table matching the contract in §C.1
   - LionWheel mirror tables: `lw_task`, `lw_visit`, `lw_route`, `lw_order_item`, and `lw_driver` / `lw_company` lookup mirrors
   - Watermark columns on each mirror table (`mirror_ingested_at`, `mirror_source_run_id`, `mirror_source_watermark`)
   - `freshness_status_view` as a database view over `integration_run` + mirror watermarks
2. Window 1 authors pgTAP tests for: idempotent upsert, watermark monotonicity, terminal-status retirement.
3. Window 1 authors rollback migration(s) — mirror schema can be dropped without touching `stock_ledger`, `balance_anchors`, or any master table.

### E.2 Prerequisites from Gate 3 (stock truth)

The mirror can ingest and the operator-visible views can render **before Gate 3 exits**, with banners. However:

- `demand_impact_view` must **not** be consumed by anything that feeds planning until Gate 3 exits.
- The mirror runtime should **not** publish FG-sync deltas back to Shopify until Gate 3 exits (Shopify reconciliation is a separate pack, flagged not authored).

### E.3 Prerequisites from auth / secrets / config

1. Token storage: **environment-based secret store** (Supabase secrets or equivalent), never inline in repo, never in memory beyond the runtime process boundary.
2. Token rotation posture: rotate the current token after this pack is reviewed (it is in conversation history). Store new token in secrets and reference by name only.
3. Environment separation: one token for production, a separate token for staging/sandbox — LionWheel provides a sandbox credential (`c_key_7afa4a75-...` per help center, username `api_sandbox`). **UNRESOLVED** whether the sandbox carries GT-realistic data for integration testing; confirm before depending on it.
4. Webhook endpoint: runtime must provide a public HTTPS endpoint configured in LionWheel's organization settings. Endpoint path, secret, and replay-protection strategy are runtime concerns not specified in this pack.

### E.4 First runtime slice to implement (smallest evidence-producing slice)

The smallest slice that produces verifiable evidence without lighting up demand-impact:

1. **Single entity:** `lw_task` upsert from `GET /tasks/show/:task_id` triggered manually (CLI).
2. **Idempotent:** second call with same `updated_at` produces zero downstream change.
3. **One `integration_run` row per invocation.** Status transitions observable.
4. **One `freshness_status_view` row computed from the run.**
5. **No webhook yet. No scheduler yet. No routes sweep yet.**

Evidence produced: `lw_task` rows exist, `integration_run` rows exist, freshness view reports `fresh`, re-run yields no duplicate deltas.

### E.5 Validation sequence

Before each slice is considered trusted:

1. **Fixture replay test:** a canned LionWheel response ingested N times produces one row and one run per invocation, no drift.
2. **Split/merge test:** fixture with two tasks sharing a `wp_order_id` ingests to two separate `lw_task` rows; `wp_order_id` is a non-unique column.
3. **Cancel test:** fixture transitioning a task from `ACTIVE` to `CANCELED` retires the mirror row (a retirement flag or terminal-status marker is set) and downstream views drop the task from `open_orders_view`.
4. **Freshness breach test:** simulate no runs for 2× threshold; `freshness_status_view` flips to `stale`.
5. **Schema-drift test:** fixture with an unknown `status` enum value causes `schema_drift` error class, halts ingest for `lw_task`, does **not** silently coerce.
6. **Duplicate-webhook test:** same webhook payload received twice; second occurrence is idempotent.
7. **Auth-failure test:** invalid token triggers `auth` error class, run status `failed`, alert emission observable.

### E.6 Rollback / safe-disable approach

1. **Kill-switch:** a single runtime flag (env var or feature flag) `LIONWHEEL_SYNC_ENABLED=false` halts all outbound calls and webhook ingest immediately.
2. **Effect when disabled:**
   - `freshness_status_view` flips to `broken` for LionWheel entities within 1 minute.
   - `open_orders_view` and `shipment_status_view` render with `broken` banner; portal consumers are expected to degrade gracefully (show last known + banner; do not error out).
   - `demand_impact_view` refuses to compute; planning gate (when Gate 5 exists) blocks recompute.
3. **Mirror table rollback:** mirror schema can be dropped and rebuilt from webhook backfill + `/tasks/by_order_id/` lookups for known GT `wp_order_id`s. Rebuild does **not** touch the ledger.
4. **Data rollback:** mirror tables never feed `stock_ledger` directly. There is no rollback concern on the audit boundary.

### E.7 What can be built in parallel vs what must wait

**Parallel-safe with Gate 3 (can proceed now or anytime):**
- Window 1 authoring of `integration_run` + mirror table migrations (Window 1 ownership)
- Runtime scaffolding for the `/tasks/show` fetcher (Window 4 ownership)
- Webhook-endpoint scaffolding with replay-protection signature check (Window 4)
- `freshness_status_view` as a view (Window 1 + Window 4 contract alignment)
- Operator-visibility rendering of `open_orders_view` and `shipment_status_view` as **read-only info surfaces with staleness banner** (Window 2 when ready; not blocking)

**Must wait for Gate 3 exit:**
- `net_availability_view`
- Any planning-engine consumption of `demand_impact_view`
- Any Shopify FG sync bidirectional write
- Any PO recommendation that depends on demand+stock

**Must wait for Gate 5:**
- `demand_impact_view` surfacing in planner workspaces
- Purchase recommendations consuming the mirror
- Production recommendations consuming the mirror

---

## F. Final required outputs checklist

- [x] **Phase A — LionWheel boundary contract pack** (§A)
- [x] **Mirror entity list** (§B.1, B.4–B.7, B.9)
- [x] **`integration_runs` / freshness model (contract)** (§C)
- [x] **Downstream read-model pack** (§D.1–D.5, D.7)
- [x] **Stock-truth dependency map** (§D.6)
- [x] **Future runtime implementation sequence** (§E)
- [x] **Blocking open-questions register** (§G)

---

## G. Blocking open questions

Each entry names the question, which phase / runtime step it blocks, and what evidence would resolve it.

| # | Question | Blocks | Resolving evidence |
|---|---|---|---|
| G.1 | Exact shape of `/tasks/show` `order_items[]` — specifically `quantity` numeric type and whether `price` is string-decimal | Phase B completeness; `demand_impact_view` numeric correctness | one live inspection call on a task with small `order_items` captured fully (not truncated) |
| G.2 | Enum completeness for `route.status`, `task.pick_status`, `task.roundtrip_status`, `task.urgency`, `task.delivery_confirmation_status`, `visit.kind` | mirror schema (Window 1 enum constraints); schema-drift detection logic | live observation over ~1 week OR LionWheel support confirmation; until then, mirror must store as free string and log any novel value |
| G.3 | Webhook payload exact field set — is it the full `/tasks/show` response, only creation-like fields, or a compact subset? | webhook-ingest code; idempotency logic | one observed webhook delivery captured and compared to `/tasks/show` response for the same task |
| G.4 | LionWheel rate limits — numeric thresholds | retry/backoff policy (§C.5); sweep cadence | LionWheel support confirmation OR one week of production observation |
| G.5 | Split/merge/cancel exact mechanics — does split happen by cancel-and-recreate or by adding a task with shared `wp_order_id`? Does merge exist at all? | `open_orders_view` retirement rules; Gate 5 demand rollup correctness | observed real split/merge/cancel in production OR LionWheel support confirmation |
| G.6 | Whether GT operationally uses multi-visit tasks for partial shipment | `shipment_status_view` semantics; partial-shipment UI | operator confirmation from Tom |
| G.7 | Whether `task.money_collect` / COD fields are operationally used by GT | whether to surface COD fields in operator views | operator confirmation from Tom |
| G.8 | Whether the custom Hebrew-keyed fields observed (`להוציא באישור`, `לא שולם`) are stable org-configured fields or ad-hoc | whether to mirror them as structured columns or as a `custom_fields` jsonb | admin inspection of LionWheel organization settings by Tom |
| G.9 | Freshness threshold values per entity — the §C.6 proposals need operator lock | alert wiring; `freshness_status_view` output | Tom confirms numeric thresholds |
| G.10 | Sandbox credential (`c_key_7afa4a75-...` per help center) — does it carry GT-realistic data, and is it safe to use for integration tests? | validation sequence (§E.5) depends on a test environment | try the sandbox credential in a subsequent inspection pass and compare to production shape |
| G.11 | Token rotation — current production token is in conversation history; when will it be rotated and where will the new token be stored? | E.3 auth prerequisite | Tom rotates and stores new token in Supabase secrets |
| G.12 | Whether `task.driver_note` (observed to carry a Green Invoice signed document URL) should be mirrored as-is, parsed to link to Green Invoice artifacts, or redacted | cross-system integration contract between LionWheel mirror and Green Invoice pack | decision from Tom + Green Invoice contract pack (not in this session) |

---

## Appendix A — Endpoints inspected (this session)

| Endpoint | Method | Observed response | Evidence |
|---|---|---|---|
| `/api/v1/routes?date=2026-04-17&format=json` | GET | HTTP 200 `[]` (empty, no routes today yet) | confirms auth works, confirms top-level shape is array |
| `/api/v1/routes?date=2026-04-16&format=json` | GET | HTTP 200 populated array of route objects with embedded visits | **primary route + visit field inspection** |
| `/api/v1/routes?date=2026-04-15&format=json` | GET | HTTP 200 populated with polyline data | secondary confirmation |
| `/api/v1/routes?date=2026-04-14&format=json` | GET | HTTP 200 populated | secondary confirmation |
| `/api/v1/routes?date=2026-04-10&format=json` | GET | HTTP 200 `[]` | no routes that date |
| `/api/v1/routes?date=2026-04-07&format=json` | GET | HTTP 200 `[]` | no routes that date |
| `/api/v1/routes?date=2026-03-30&format=json` | GET | HTTP 200 populated | secondary confirmation |
| `/api/v1/tasks/show/23936538` | GET | HTTP 200 `{task:{...}}` wrapper | **primary task field inspection** |
| `/api/v1/tasks/by_order_id/%23GT12519` | GET | HTTP 200 `{tasks:[...]}` wrapper (array, even for single match) | **confirms array shape and supports multi-task-per-order** |
| `/api/v1/tasks/show/1?key=invalid-token` | GET | HTTP 401 `{"error":"API Key is wrong"}` | auth error shape |
| `/api/v1/tasks/show/999999999999` | GET | HTTP 404 `{"error":"Not found"}` | not-found error shape |

### A.1 Redacted sample response shapes

**`/routes?date=2026-04-16` — top-level element (route) — redacted sample:**

```json
[{
  "id": 1434554,
  "assistant_driver_str": null,
  "code": null,
  "color": "#C673CF",
  "date": "16/04/2026",
  "distance": "0 KMs",
  "driver_id": <REDACTED_INT>,
  "driver_str": "<REDACTED_HEBREW_NAME>",
  "end_eta_at": null,
  "external_driver_id": "",
  "finish_location_id": null,
  "finish_point_address": null,
  "finish_visit_id": null,
  "int_distance": null,
  "is_locked": false,
  "max_packages_quantity": 0,
  "max_surfaces_quantity": 0,
  "max_volume": 0,
  "max_weight": 0,
  "name": "<REDACTED_HEBREW_NAME> 16/04/2026",
  "notes": null,
  "polyline": null,
  "start_location_id": null,
  "start_point_address": null,
  "start_time": "08:30",
  "start_visit_id": null,
  "status": "planned",
  "vehicle_id": null,
  "vehicle_str": null,
  "visits": [ { /* see visit sample below */ } ],
  "wait_time": null,
  "weight": 0.0
}]
```

**Embedded `visit` inside `/routes` response — redacted:**

```json
{
  "id": 30077437,
  "apartment": "",
  "city": "<REDACTED_CITY>",
  "color": "#C673CF",
  "company_name": "Online",
  "delivery_latitude": null,
  "delivery_longitude": null,
  "earliest": null,
  "earliest_latest_time": null,
  "eta_at": null,
  "eta_at_formatted": null,
  "eta_window": null,
  "failure_reason": null,
  "floor": "",
  "group": null,
  "is_done": true,
  "kind": "DELIVERY",
  "latitude": <REDACTED_LAT>,
  "location_name": null,
  "longitude": <REDACTED_LON>,
  "packages_quantity": 2,
  "partial_address": "<REDACTED_ADDRESS>",
  "partial_address_no_city": "<REDACTED_STREET>",
  "phone": "<REDACTED_E164>",
  "priority": null,
  "recipient_name": "<REDACTED_RECIPIENT>",
  "route_id": 1434554,
  "route_locked": false,
  "route_name": "<REDACTED_ROUTE_NAME>",
  "surfaces_quantity": null,
  "task_id": 23936538,
  "task_status": "COMPLETED",
  "visit_at": "2026-04-16T00:00:00.000+03:00",
  "visit_at_formatted": "16/04/2026",
  "volume_number": 0.0,
  "wp_order_id": "#GT12519",
  "להוציא באישור": "",
  "לא שולם": ""
}
```

**`/tasks/show/:task_id` — redacted sample:**

```json
{"task":{
  "id": 23936538,
  "public_id": "M93TRM2PZZ",
  "notes": "PICK UP",
  "organization_id": 2074,
  "company_id": 34859,
  "created_at": "2026-04-13T14:07:08.598+03:00",
  "updated_at": "2026-04-15T16:56:06.532+03:00",
  "pickup_at": "2026-04-16T00:00:00.000+03:00",
  "same_day": false,
  "is_roundtrip": false,
  "packages_quantity": 2,
  "driver_id": <REDACTED_INT>,
  "vehicle_kind": null,
  "status": "COMPLETED",
  "urgency": "REGULAR",
  "signature_url": null,
  "surfaces_quantity": null,
  "org_note": null,
  "price": null,
  "wait_time": null,
  "signee_name": null,
  "driver_note": "<REDACTED_GREEN_INVOICE_SIGNED_URL>",
  "user_id": null,
  "document_number": null,
  "fee_cost": null,
  "invoice_id": null,
  "distribution_id": null,
  "other_user": null,
  "wp_order_id": "#GT12519",
  "wp_order_key": "7066461536497",
  "delivery_method": "",
  "wp_order_at": "2026-04-13T14:06:02.000+03:00",
  "batch_id": null,
  "cartons_quantity": null,
  "money_collect": null,
  "creation_origin": "shopify",
  "completed_at": "2026-04-15T16:56:06.575+03:00",
  "greeting": null,
  "payment_method": null,
  "gifter_name": null,
  "gifter_phone": null,
  "target_partner_task_id": null,
  "origin_partner_task_id": null,
  "target_partner_bridge_id": null,
  "printed_at": null,
  "order_total": "370.50",
  "warehouse_id": null,
  "money_transferred": false,
  "earliest": null,
  "latest": null,
  "validation_status": null,
  "is_self_pickup": false,
  "stop_time": null,
  "is_free": false,
  "origin_partner_bridge_id": null,
  "money_transferred_at": null,
  "customer_user_agent": null,
  "pick_status": "NEW",
  "branch_id": null,
  "age_verification": false,
  "leave_next_to_door": false,
  "is_photo_attached": false,
  "scheduled_template_id": null,
  "weight": null,
  "route_code": null,
  "signature": null,
  "signed_document": false,
  "returned_pallets": null,
  "sms_from_name": null,
  "client_id": null,
  "volume": null,
  "extra_barcode": null,
  "task_type": null,
  "payer": null,
  "otp_code": null,
  "is_document_attached": false,
  "origin_partner_company": null,
  "ready_to_print": true,
  "age_start_date": "2026-04-16T00:00:00.000+03:00",
  "target_partner_task_status": null,
  "target_partner_transfer_type": null,
  "origin_partner_transfer_type": null,
  "transferred_at": null,
  "external_line_branch": null,
  "external_distribution_line": null,
  "creation_trigger": "automatic",
  "roundtrip_status": "UNRETURNED",
  "source_order_id": null,
  "validation_link_sent_at": null,
  "skills": [],
  "due_date": null,
  "failed_count": 0,
  "delivery_confirmation_status": "NOT_SENT",
  "delivery_decline_reason_id": null,
  "confirmation_link_sent_at": null,
  "confirmation_updated_at": null,
  "document_type": null,
  "transfer_errors": null,
  "visits": [ { /* expanded visit — see below */ } ],
  "photos": [],
  "order_items": [
    {
      "id": 210665463,
      "sku": "GT-HIB-LOW-1L",
      "name": "FRESH 1000ml",
      "variant": null,
      "quantity": "<TRUNCATED_AT_INSPECTION — see G.1>"
    }
  ]
}}
```

**Expanded `visit` from `/tasks/show` (superset of `/routes` visit) — redacted:**

```json
{
  "id": 30077437,
  "organization_id": 2074,
  "company_id": 34859,
  "task_id": 23936538,
  "driver_id": <REDACTED_INT>,
  "kind": "DELIVERY",
  "visit_at": "2026-04-16T00:00:00.000+03:00",
  "is_done": true,
  "created_at": "2026-04-13T14:07:08.621+03:00",
  "updated_at": "2026-04-15T16:56:06.600+03:00",
  "delivered_at": "2026-04-15T16:56:06.599+03:00",
  "eta_at": null,
  "delivery_latitude": null,
  "delivery_longitude": null,
  "failed_at": null,
  "daily_order": null,
  "group": null,
  "route_id": 1434554,
  "apartment": "",
  "city": "<REDACTED_CITY>",
  "email": "",
  "floor": "",
  "geo_provider": "shopify",
  "geo_type": null,
  "latitude": <REDACTED_LAT>,
  "longitude": <REDACTED_LON>,
  "matches_count": null,
  "name": null,
  "notes": "",
  "number": "7",
  "partial_match": null,
  "phone": "<REDACTED_E164>",
  "phone2": "",
  "recipient_name": "<REDACTED_RECIPIENT>",
  "region_str": "<REDACTED_REGION>",
  "street": "<REDACTED_HEBREW_STREET>",
  "zip_code": null,
  "entrance_code": null,
  "entrance": null,
  "location_cache_id": null,
  "salary": null,
  "location_id": null,
  "state": null,
  "earliest_at": null,
  "latest_at": null,
  "loaded_at": null,
  "is_location_fixed": true,
  "ignore_location_warning": false,
  "geo_fence_id": null,
  "early_eta_at": null,
  "late_eta_at": null,
  "salary_origin": null,
  "priority": null,
  "driver_str": "<REDACTED_HEBREW_NAME>"
}
```

**Error samples:**

```json
// HTTP 401
{"error":"API Key is wrong"}

// HTTP 404
{"error":"Not found"}
```

### A.2 Fields NOT verified in live inspection this session

- `order_items[].quantity` (truncation at 4000 chars)
- `order_items[].price`, `order_items[].weight`, `order_items[].notes`, `order_items[].variant` when populated
- All enum values beyond the single values observed (see G.2)
- Webhook payload shape (G.3)
- Pagination behavior on `/tasks/by_order_id` when an order has many tasks
- `/drivers/:driver_id/daily_route` response shape
- `/visits/:visit_id` response shape
- `/companies/:company_id` response shape

### A.3 Not called in this session (read-only-scope discipline)

- any POST / PUT / PATCH / DELETE
- any `/api/v1/tasks/create`
- any `/api/v1/tasks/:id/update`
- any `/api/v1/visits/:id` update
- any `/api/v1/drivers/:id/optimize_daily_route`
- any write to Window 1 schema, Window 2 portal, or any migration file
- no runtime sync code was authored; no scheduler wiring; no mirror DDL

---

## H. Self-check against foundation

- [x] LionWheel = open orders + shipment state only; not planning; not stock truth — §A verbatim
- [x] Mirror-internally rule preserved — §A.3, §C, §D
- [x] Never compute planning from live API — §A.3, §D.3, §D.6
- [x] Split/merge/cancel first-class — §B.10
- [x] No invented field names — every field is either (inspected) / (docs) / UNRESOLVED (§G)
- [x] No Window 1 DDL authored — §E.1 defers all migrations to Window 1
- [x] No Window 2 portal touch — Window 2 is a consumer of read models, not modified here
- [x] No runtime integration code authored — §E is plan-only
- [x] Stock-truth dependency map is honest and not collapsed — §D.6
- [x] Blocking open questions register surfaced — §G
- [x] Token will be rotated per §E.3 / G.11 — operator action required, flagged

---

**END — Window 4 LionWheel contract-first integration pack.**

Integration is **not ready**. This pack is **contract-complete for v1 scope**, with the explicit UNRESOLVED register above. Runtime implementation is blocked until §G items are resolved and Window 1 authors the mirror schema migrations per §E.1.
