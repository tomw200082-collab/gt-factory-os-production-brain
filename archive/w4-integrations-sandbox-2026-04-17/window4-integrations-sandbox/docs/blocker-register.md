# Window 4 canonical blocker register — LionWheel

**Owner:** Window 4
**Last updated:** 2026-04-17 (Window 4 third pass — scaffolding)
**Supersedes:** blockers listed in §E of `window4-lionwheel-runtime-handoff.md` and §G of `window4-lionwheel-contract-pack.md`. This is now the single canonical place.

## How to read this

Each blocker names:
- **Owner** — who must act (Tom / Window 1 / Window 4 / LionWheel inspection)
- **Blocks** — the next runtime step that cannot proceed until resolved
- **Resolving evidence** — what marks it done
- **Status** — open / in-progress / resolved

Do not broaden this list without deleting something else. Ambiguity is the enemy.

---

## A. Tom (operator) blockers

### T.1 — Rotate the LionWheel API token
- **Status:** open
- **Blocks:** Slice 1 runtime (token in prior conversation history is burned for production use)
- **Resolving evidence:** new token generated in LionWheel settings, old token revoked, new token stored in secret store per `secret-store-wiring.md`, new token **not** pasted into any chat or ticket
- **Notes:** this is the single most important blocker; Slice 1 should not run with the prior token under any circumstance

### T.2 — Lock freshness thresholds per entity
- **Status:** open
- **Blocks:** `freshness_status_view` final rule wiring (Window 1 authors view with placeholder thresholds until Tom locks)
- **Resolving evidence:** numeric minutes for each of:
  - non-terminal task fresh-window (proposed 60 min)
  - terminal task fresh-window (proposed 24 h)
  - `/routes` sweep fresh-window during operating hours (proposed 30 min)
  - off-hours fresh-window (proposed 2 h)
  - webhook-stream silence threshold (proposed 4 h during operating hours)

### T.3 — Confirm multi-visit partial-shipment usage
- **Status:** open
- **Blocks:** `shipment_status_view` semantics; whether per-visit partial-completion state is a first-class operator surface
- **Resolving evidence:** Tom confirms whether GT's workflow uses multi-visit tasks to model partial shipments, or whether all shipments are single-visit

### T.4 — Confirm COD / money_collect field usage
- **Status:** open
- **Blocks:** decision to promote `money_collect`, `payment_method`, `money_transferred`, `money_transferred_at`, `cod_type` from `raw_payload` into structured `lw_task` columns
- **Resolving evidence:** Tom confirms whether GT uses cash-on-delivery in operations; if no, these stay in `raw_payload` permanently

### T.5 — Decide handling for `driver_note` Green Invoice signed URL
- **Status:** open
- **Blocks:** whether the mirror stores the signed URL verbatim, parses it for reconciliation with Green Invoice, or redacts it on ingest
- **Resolving evidence:** decision recorded; ties into the future Green Invoice contract pack

### T.6 — Stabilize custom Hebrew-keyed task fields
- **Status:** open
- **Blocks:** decision whether to mirror `"להוציא באישור"`, `"לא שולם"`, etc. as structured columns or leave inside `raw_payload`
- **Resolving evidence:** Tom confirms whether these are org-configured custom fields or ad-hoc; if configured, their definitions are surfaced

---

## B. Window 1 (DB / Schema / Migrations) blockers

Window 1's queue before Slice 1 can run. All items derive from `window4-lionwheel-runtime-handoff.md` §D.1.

### W1.1 — Migration for `integration_run` table
- **Status:** not started
- **Blocks:** every slice
- **Resolving evidence:** migration file exists under `gt-factory-os/db/migrations/`, runs cleanly against a fresh DB, pgTAP covers the CHECK constraints on `status` / `run_kind` / `trigger_source` / `error_class`
- **Shape reference:** runtime handoff §B.5, type reference `src/lionwheel/mirror-shapes.ts` → `IntegrationRunRecordSchema`

### W1.2 — Migrations for `lw_task`, `lw_visit`, `lw_order_item`
- **Status:** not started
- **Blocks:** every slice
- **Resolving evidence:** three migration files exist, schema (proposed name `integrations_lionwheel` or `mirror_lionwheel`, Window 1's call) isolated from `private_core`, `wp_order_id` index is explicitly NOT unique, string-decimal columns typed as `text`
- **Shape reference:** runtime handoff §B.2 / §B.3 / §B.4

### W1.3 — `freshness_status_view`
- **Status:** not started
- **Blocks:** read-model degradation contract (runtime handoff §C.7)
- **Resolving evidence:** view exists, returns one row per `(integration, entity)`, status computed from `integration_run` history + per-entity watermarks, query cost is O(1) or O(log n) — never O(n) over mirror tables
- **Shape reference:** runtime handoff §B.6

### W1.4 — pgTAP tests V.1 through V.12
- **Status:** not started
- **Blocks:** Slice 1 acceptance
- **Resolving evidence:** twelve pgTAP tests present, all passing against a clean schema; covers idempotent upsert (V.2, V.3), status retirement (V.1), split-order non-unique wp_order_id (V.4), embedded-child upsert (V.5, V.6), schema drift halt (V.7), `integration_run` lifecycle (V.8, V.9), freshness view computation (V.10), cascade (V.11), raw_payload round-trip (V.12)

### W1.5 — Rollback migrations + runbook
- **Status:** not started
- **Blocks:** operational readiness
- **Resolving evidence:** each forward migration has a paired downgrade; dropping the entire LionWheel mirror schema leaves `stock_ledger` / `balance_anchors` / masters / audit tables untouched; runbook documents the rollback order

---

## C. Window 4 (this directory) blockers

Work Window 4 itself owes before Slice 1 runtime.

### W4.1 — Zod API schemas
- **Status:** ✅ resolved (this pass)
- **Evidence:** `src/lionwheel/api-schemas.ts` exists, matches inspected shapes, uses `.passthrough()` for raw_payload resilience, no invented field names

### W4.2 — Mirror upsert shapes
- **Status:** ✅ resolved (this pass)
- **Evidence:** `src/lionwheel/mirror-shapes.ts` exists, matches runtime handoff §B.2–§B.5, string-decimals preserved as `z.string()`

### W4.3 — Fetcher interface
- **Status:** ✅ resolved (this pass) — interface only, no implementation
- **Evidence:** `src/lionwheel/fetcher.ts` declares `LionWheelFetcher` + `FetchResult` + `LionWheelFetcherConfig` + error-class mapping

### W4.4 — CLI skeleton
- **Status:** ✅ resolved (this pass) — does not perform HTTP
- **Evidence:** `src/lionwheel/cli.ts` parses args, validates env, reports planned run, exits with well-defined codes

### W4.5 — Secret-store wiring design note
- **Status:** ✅ resolved (this pass)
- **Evidence:** `docs/secret-store-wiring.md` exists, documents env var names, rotation posture, kill-switch coupling

### W4.6 — Fetcher implementation
- **Status:** ⛔ blocked on W1.1 + W1.2 + T.1
- **Blocks:** Slice 1 runtime execution
- **Resolving evidence:** fetcher module implements `LionWheelFetcher` against `members.lionwheel.com`, passes fixture-replay idempotency tests, redacts token in all error paths, respects kill-switch
- **Do not start** before W1.1 + W1.2 + T.1 are done; without a mirror target or rotated token, implementation is either untestable or unsafe

### W4.7 — Runtime wrapper (integration_run row lifecycle)
- **Status:** ⛔ blocked on W1.1 + W4.6
- **Blocks:** Slice 1 acceptance
- **Resolving evidence:** wrapper opens a `pending` run row, transitions to `running`, calls fetcher, upserts, transitions to `succeeded`/`partial`/`failed` per runtime handoff §C.2, redacts token in `error_detail`

### W4.8 — Fixture replay harness
- **Status:** resolved
- **Evidence:** `fixtures/lionwheel/*.json` (7 fixtures: 2 task-show, 1 split-order, 2 routes, 2 errors); `src/lionwheel/__tests__/mapper.spec.ts` (schema parse + isTerminalStatus + mapper invariants + split-order assertion + order_item normalization edges); `src/lionwheel/__tests__/replay.ts` (one-command fixture smoke check)
- **Note:** Window 1's pgTAP tests and Window 4's fixture replay harness serve different purposes — don't merge them. Window 4 tests verify the pure mapper and the Zod parse contract; Window 1 pgTAP tests verify upsert semantics, watermark monotonicity, cascade, and freshness-view computation against a real schema.

### W4.9 — Pure API -> mirror mapper
- **Status:** resolved
- **Evidence:** `src/lionwheel/mapper.ts` — `mapTaskToFetchResult`, `mapTaskToUpsert`, `mapVisitToUpsert`, `mapOrderItemToUpsert`, `normalizeQuantity`; exhaustively tested in mapper.spec.ts
- **Consumer:** the future fetcher implementation (W4.6) will delegate all shape-mapping to this module; having it isolated and pure means runtime authoring reduces to transport + error classification + integration_run lifecycle, with zero mapping logic to write-and-re-write under pressure

---

## E. Window 4 Shopify scaffolding (this pass)

Shopify-side counterparts to the LionWheel scaffolding in §C. Same rules: no DDL, no HTTP, no scheduler, no portal. Window 1 remains focused on Gate 3 closure; Shopify migrations (W1.SG.*) are NOT queued this cycle.

### W4.SG.1 — Zod schemas for Shopify Admin GraphQL
- **Status:** resolved
- **Evidence:** `src/shopify/api-schemas.ts` — `InventorySetQuantitiesInputSchema`, `InventoryQuantityInputSchema`, `InventoryLevelSchema`, `InventoryItemSchema`, `LocationSchema`, `InventoryQuantitySchema`, `ShopifyUserErrorSchema`, `InventorySetQuantityNameSchema`. Every field traces to a cited shopify.dev page; UNRESOLVED items (reason enum beyond "correction", scheduledChanges inner fields, UserError exact shape) are explicitly commented and preserved via `.passthrough()`.

### W4.SG.2 — Mirror/push shapes
- **Status:** resolved
- **Evidence:** `src/shopify/mirror-shapes.ts` — `PushQuantityRequestSchema`, `ShopifyPushPlanSchema`, `ShopifyReconciliationRowSchema`, `ShopifyDriftVerdictSchema` (discriminated union), plus `ShopifyRunKindSchema` and `ShopifyErrorClassSchema` for Window 1's eventual CHECK-constraint extension of `integration_run`.

### W4.SG.3 — Pure Shopify mappers
- **Status:** resolved
- **Evidence:** `src/shopify/mapper.ts` — `mapPushRequestToPlan`, `deriveIdempotencyKey`, `mapInventoryLevelToReconciliationRow`, `classifyDrift`, `ShopifyMapperError`. All pure, no I/O. Invariants enforced: platformProjectedQty >= 0, first-push compareQuantity refusal, `ignoreCompareQuantity=false` in v1, deterministic idempotency key.

### W4.SG.4 — Typed fetcher interface (no implementation)
- **Status:** resolved
- **Evidence:** `src/shopify/fetcher.ts` — `ShopifyFetcher` interface (`pushInventorySet`, `readInventoryLevelsForLocation`, `resolveInventoryItemIdBySku`), `FetchResult<T>` discriminated union (8 variants + `disabled_by_kill_switch`), `errorClassOf`, `ShopifyFetcherConfig`. Zero implementation.

### W4.SG.5 — Env parser
- **Status:** resolved
- **Evidence:** `src/shopify/env.ts` — `parseRuntimeEnv`, `ENV_VAR_NAMES` (`SHOPIFY_ADMIN_API_TOKEN`, `SHOPIFY_SHOP_DOMAIN`, `SHOPIFY_ADMIN_API_VERSION`, `SHOPIFY_SYNC_ENABLED`, `SHOPIFY_REQUEST_TIMEOUT_MS`), `redactToken`, default API version 2026-04 (the `@idempotent` minimum).

### W4.SG.6 — CLI skeleton
- **Status:** resolved
- **Evidence:** `src/shopify/cli.ts` — parses `--push`/`--reconcile` subcommands, validates env, prints what a real run would do, exits. Fetcher module not imported; no HTTP path possible.

### W4.SG.7 — Fixture corpus + unit tests + replay harness
- **Status:** resolved
- **Evidence:** `fixtures/shopify/inventory-set-quantities-input--happy.json`, `fixtures/shopify/inventory-level-read--single-location.json`, `src/shopify/__tests__/mapper.spec.ts` (schema parse, deriveIdempotencyKey, mapper happy/error paths, read mapper, drift classification — 25+ assertions), `src/shopify/__tests__/replay.ts` (fixture smoke-check with drift classification on read samples).

### W4.SG.8 — Fetcher implementation
- **Status:** **blocked on Gate 3 closure AND W1.SG.* Window-1 migrations AND Shopify Admin API token provisioning**. Do not start.
- **Resolving evidence path:** Gate 3 exits + Window 1 authors Shopify migrations (W1.SG.1, W1.SG.2) + Shopify Admin API token stored per secret-store-wiring pattern + operator confirmations T.SG.1, T.SG.2.

### W4.SG.9 — Runtime wrapper (integration_run lifecycle for Shopify)
- **Status:** blocked on W1.SG.1 + W4.SG.8. Do not start.

---

## F. Green Invoice — status update after 2026-04-17 read-only inspection

See `window4-greeninvoice-inspection-report.md` for the full evidence trail. This section supersedes the Green Invoice entries in `window4-shopify-greeninvoice-contract-pack.md` §F.4 where the two conflict.

### Resolved this pass (from public source inspection — no token used)

- **L.GI.1 — JWT auth flow.** Resolved: `POST /v1/account/token` with body `{id, secret}`; JWT in header `X-Authorization-Bearer` and body field `token`; TTL 1 hour.
- **L.GI.4 — 13-code document type enum.** Resolved: all codes 10, 100, 200, 210, 300, 305, 320, 330, 400, 405, 500, 600, 610 confirmed across three independent sources.
- Partial L.GI.2 — document/client endpoint paths resolved verbatim (`/v1/documents`, `/v1/documents/search`, `/v1/clients`, `/v1/clients/search`, `/v1/items`); expense/supplier paths remain unresolved (narrowed).
- Partial L.GI.3 — outbound document + income-line field sets resolved verbatim (including key correction: `price: float` and `quantity: int`, not string-decimal; update Zod accordingly when authoring); expense-line shape still unresolved.
- Partial L.GI.5 — client object shape resolved verbatim as template; supplier object remains unresolved.
- L.GI.8 — sandbox URL identified as `https://sandbox.d.greeninvoice.co.il/api`; usability of GT-realistic demo data still UNRESOLVED.

### Remaining — narrowly scoped to expense/supplier surface only

| # | Item | Unblock path |
|---|---|---|
| U.GI.1 | exact `/v1/expenses/*` path | one authenticated call |
| U.GI.2 | expense object field set | one authenticated `GET /v1/expenses/{id}` |
| U.GI.3 | exact `/v1/suppliers/*` path | one authenticated call |
| U.GI.4 | supplier object field set | one authenticated `GET /v1/suppliers/{id}` |
| U.GI.5 | expense line-item field set (`catalogNum` vs `sku` asymmetry observed on outbound; inbound shape unresolved) | one authenticated `GET /v1/expenses/{id}` |
| U.GI.6 | expense updated_at-equivalent + mutability | observation of an edited expense via auth |
| U.GI.7 | webhook availability for expense events | operator inspection of GI Settings → Developer Tools |
| U.GI.8 | full error-class vocabulary | live observation of error cases |

### Policy

Do **not** author Green Invoice Zod schemas for the expense/supplier surface this cycle — that would require guessing field names. Outbound-document + client surface could now be authored verbatim if the lane is ever reopened for it; this cycle's directive does not reopen the lane. Green Invoice remains PARKED pending one authenticated inspection pass to close U.GI.1 through U.GI.5.

---

## D. LionWheel inspection blockers

Items that cannot be resolved from the accepted contract pack without further live observation or LionWheel support confirmation.

### L.1 — `order_items[].quantity` precise type (contract pack G.1)
- **Status:** open
- **Blocks:** `LwOrderItemUpsert.quantity` type can be narrowed from `string` to a more precise form only after resolution
- **Resolving evidence:** one `/tasks/show` response with a small `order_items` array observed end-to-end (prior inspection was truncated at 4 KB); OR LionWheel support confirmation

### L.2 — Enum completeness (G.2)
- **Status:** open (low priority — Zod schemas accept strings)
- **Blocks:** whether mirror `status`/`pick_status`/`urgency`/`roundtrip_status`/`route.status`/`visit.kind` columns can switch from `text` with log-on-novel-value to `CHECK` constraints
- **Resolving evidence:** ~1 week of production observation OR LionWheel support confirmation

### L.3 — Rate-limit values (G.4)
- **Status:** open
- **Blocks:** Slice 2 scheduler cadence lock (currently proposed at 15 min during operating hours)
- **Resolving evidence:** LionWheel support confirmation OR one week of production observation with no 429s and no latency spikes

### L.4 — Split / merge / cancel exact mechanics (G.5)
- **Status:** open
- **Blocks:** reconciliation pass (Slice 4) final design
- **Resolving evidence:** observed real event OR LionWheel support confirmation; confirms whether merge exists at all

### L.5 — Webhook payload exact shape (G.3)
- **Status:** open
- **Blocks:** Slice 3 (webhook intake)
- **Resolving evidence:** one observed webhook delivery captured with full payload, field-by-field compared against `/tasks/show`; signature / replay-protection scheme validated

### L.6 — Sandbox credential usability (G.10)
- **Status:** open
- **Blocks:** CI test environment setup; validation sequence (runtime handoff §E.5)
- **Resolving evidence:** sandbox credential tested against API, shape confirmed realistic, documented as safe for test use; OR sandbox rejected and GT needs its own non-production tenant

---

## Exit criterion for this register

When every item above is either ✅ resolved, ⛔ blocked on a named dependency, or explicitly deferred to a later slice, the register is healthy.

When T.1 + W1.1 + W1.2 resolve, Window 4 can start W4.6 (fetcher implementation). That is the handoff moment to go from parallel-safe scaffolding to runtime-in-progress.
