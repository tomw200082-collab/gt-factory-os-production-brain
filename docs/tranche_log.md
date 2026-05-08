# GT Factory OS — Tranche Log

> **Purpose:** Record of completed tranches — date, scope, evidence doc, gaps closed, gaps opened.
> **Governance:** A tranche is not complete until the evidence doc is committed and this log is updated.

---

## Format

```
### Tranche [ID]: [Name]
**Date:** YYYY-MM-DD
**Window:** W1 / W2 / W4 / combination
**Scope:** [what was built]
**Evidence doc:** [path]
**Gaps closed:** [GAP-IDs from gap_registry.md]
**Gaps opened:** [GAP-IDs newly discovered]
**Notes:** [anything non-obvious]
```

---

## Log

### Tranche L0-INFRA: Layer 0 Infrastructure Validation
**Date:** 2026-04-23
**Window:** Manual (infrastructure verification, no code changes)
**Scope:** Verified Railway API health, Railway env vars, Vercel portal live status, Vercel env vars, middleware auth gate.
**Evidence doc:** (inline — see gap_registry.md CLOSED-001 through CLOSED-004)
**Gaps closed:** CLOSED-001, CLOSED-002, CLOSED-003, CLOSED-004
**Gaps opened:** GAP-001 through GAP-016 (initial gap registry population)
**Notes:** Railway project is named `accomplished-learning` (not `gt-factory-os` as expected from memory). Portal production URL is `https://gt-factory-os-portal.vercel.app/`. Vercel encrypted vars cannot be decrypted via CLI pull — confirmed present via `vercel env ls`. `NEXT_PUBLIC_API_BASE` shows as empty string in pulled file (Vercel CLI limitation with encrypted vars); `API_BASE` (server-side) correctly shows Railway URL.

### Tranche L0-DOCS: Layer 0 Documentation Artifacts
**Date:** 2026-04-23
**Window:** Manual (doc authoring)
**Scope:** Authored `operational_dataflow_blueprint.md`, `gap_registry.md`, `false_green_registry.md`, `tranche_log.md`, `lessons_learned.md` in `PRODUCTION/docs/`.
**Evidence doc:** (the files themselves are the evidence)
**Gaps closed:** CLOSED-005
**Gaps opened:** None
**Notes:** These are first-class permanent artifacts per the Master Operating Blueprint, section D. The `operational_dataflow_blueprint.md` is the primary lens for all future audits.

### Tranche L0-ALIAS-FIX: LionWheel Alias Portal Bug Fix (idempotency_key)
**Date:** 2026-04-23
**Window:** W2 (Mode B-AMMC, /admin/sku-aliases surface)
**Scope:** Fixed missing `idempotency_key` field in `/admin/sku-aliases` approve mutation POST body. One-line change to `src/app/(admin)/admin/sku-aliases/page.tsx` line 279. Backend requires `idempotency_key` as non-optional Zod field; omission caused every approve attempt to return HTTP 422.
**Evidence doc:** (inline — W2 executor report + commit 8543d2b on window2-portal-sandbox main)
**Gaps closed:** GAP-008 (portal-side unblock of approve button; alias seeding itself remained blocked by second bug)
**Gaps opened:** None (second blocking bug — extractExternalSku — discovered in same session; fixed in next tranche below)
**Notes:** The backend `POST /api/v1/mutations/integration-sku-map/approve` has existed and been correct since migration 0033; only the portal caller was broken.

### Tranche L1-SKU-ALIASES-CONTINUITY: LionWheel Alias Portal Continuity Fix
**Date:** 2026-04-23
**Window:** W2 (Mode B-AMMC amended, /admin/sku-aliases surface only)
**Scope:** Fixed blocking bug in `extractExternalSku()` (page.tsx:114-123) that made unmapped SKU list always empty in production. LionWheel poller sets `detail` as plain text; old function probed `detail` as JSON object and returned null for every row. Fix: read from `title` field via `/Unknown SKU (.+)$/` regex. Also closed 3 continuity gaps: item names in approved aliases table; `resolved_exceptions_count` surfaced in success banner; note explaining why rows remain unresolved after seeding. Single file change.
**Evidence doc:** (inline — W2 executor report + verifier PASS + commit 96516ae on window2-portal-sandbox main)
**Gaps closed:** GAP-003 portal-side unblock (portal can now show and approve unmapped SKUs); GAP-008 fully closed (both portal bugs fixed)
**Gaps opened:** UNRESOLVED-7 — "37 exact legacy_sku matches" sub-label in tranche contract table (line 47) may be off-by-one; verifier counted 36 table rows, 36+3 ODK=39 Bucket A total is correct; needs W1 confirmation before seeding session begins
**Notes:** Mode B entry was governor Q2 option (a) — targeted amendment overriding EXECUTION_POLICY.md line 63 exclusion of sku-aliases alias workflow. Tom must now deploy portal to Vercel (`vercel --prod` from window2-portal-sandbox), then navigate to `/admin/sku-aliases` to seed the 39 Bucket A aliases.

### Tranche L0-CLOSED: Layer 0 Final Closure Declaration
**Date:** 2026-04-23
**Window:** Manual (human declaration — Tom)
**Scope:** Layer 0 fully closed. Step 5f (exception/approval path) confirmed from live DB: exception `7283a2d2` (positive_adjustment, RAW-VODKA, qty=50, status=open); form_submission `56c1be71` pending NOT posted; `current_balances` RAW-VODKA=0.00 unchanged. All 7 Layer 0 exit criteria evidenced.
**Evidence doc:** (inline — CURRENT_STATE.md Layer 0 verdict CLOSED 2026-04-23)
**Gaps closed:** CLOSED-009 (step 5f exception path)
**Gaps opened:** None
**Notes:** Layer 0 verdict changed from CONDITIONAL GO to CLOSED. Next tranche: LionWheel alias seeding — blocked on W2 Mode B sku-aliases-continuity-fix (extractExternalSku bug, authorized 2026-04-23 governor Q2 option a).

### Tranche L2-EXCLUDED-DEMAND: Excluded Demand Categorization + Exception Inbox Cleanup
**Date:** 2026-04-23
**Window:** Direct DB (exception cleanup + view creation)
**Scope:** (1) Closed 41 stale `lionwheel_unknown_sku` exceptions — these were historical exceptions for SKUs now resolvable via hybrid resolver. Inbox now shows 25 open (true current failures) vs 41 resolved. (2) Created `api_read.v_excluded_demand` view (ad-hoc, should be formalized in migration 0058+) providing excluded demand summary by reason. (3) Categorized full excluded demand: bundle (9 SKUs/44 lines/47 units), non-catalog (10/22/52), held-alias (2/5/15), fee-deposit/GTMN-PIK-254 Pikadon 36 units, malformed (2/2/2). (4) Identified GTMN-PIK-254 as bottle deposit fee — not a product. (5) Documented bundle policy gap: bundle composition unknown, explosion impossible without bundle BOM definition.
**Evidence doc:** inline — v_excluded_demand query returns correct summary; exception count 25 open after cleanup
**Gaps closed:** none (stale exception cleanup is maintenance, not a gap closure)
**Gaps opened:** GAP-019 (bundle BOM undefined), GAP-020 (non-catalog SKUs need catalog review)
**Notes:** Bundle demand is materially underrepresented: 47 bundle units hides ~140-280 real FG bottle demand depending on composition. Planner must not treat current planning recommendations as reflecting full customer demand until GAP-019 is resolved. Non-catalog Muza variants (APPZ/PSSP/ANBL/SMAR/BLBR/TROJ) are likely real new products awaiting catalog entry — each has active open orders.

### Tranche L1-HYBRID-RESOLVER: LionWheel Hybrid SKU Resolver + Portal Deploy + NM-SAN Alias
**Date:** 2026-04-23
**Window:** W1 (resolver code + backfill) + W2 (portal deploy) + direct DB (alias seed + backfill)
**Scope:** (1) Rewrote `resolveSku()` in `supabase/functions/factory_os_jobs/index.ts` to implement 3-step hybrid resolver: Step 1 `legacy_sku` exact match → Step 2 `integration_sku_map` alias → Step 3 exception (GTSET-* tagged `bundle_sku=true`). Deployed to Supabase production. (2) Deployed portal commit 96516ae to Vercel production (`gt-factory-os-portal.vercel.app`, deployment `dpl_FBYNFt5nvGKQzvVzrey13KMDjFGo`). (3) Seeded GTCC-NM-SAN-3.85L → FG-NM-3850ML alias. (4) Backfilled 2 NM-SAN order lines (item_id + resolution_status). (5) Two-pass backfill of 294 order lines via exact legacy_sku match (Pass 1) + resolution_status repair (critical fix — v_planning_demand filters on resolution_status='resolved'). (6) ODK aliases confirmed: 3 rows seeded. Total resolved: 330/404 lines (81.7%), 41 distinct SKUs.
**Evidence doc:** (inline — runtime verification: `rows_unknown_sku=0` on post-deploy poll; demand flowing for 15+ items; FG-NM-3850ML showing 14 units demand in v_planning_demand; resolution_status distribution: 330 resolved/41 SKUs, 74 unresolved/24 SKUs)
**Gaps closed:** GAP-003 downgraded P1→P2 (resolver live, demand flowing)
**Gaps opened:** None (bundle policy, non-catalog, held aliases tracked in GAP-003 updated description)
**Notes:** UNRESOLVED-7 (37 vs 36 exact matches) resolved by live DB: 41 distinct resolved SKUs - 4 aliases (3 ODK + 1 NM-SAN) = 37 exact legacy_sku direct matches. "37" in tranche contract is correct. Exception count 65 = 41 stale (now-resolvable, historical) + 24 true current failures. Stale exceptions require admin cleanup (P3). JASM/PNMM held for Tom confirmation. GTSET bundles tagged `bundle_sku=true` in resolver, excluded demand = 44 lines pending bundle-policy tranche.

### Tranche LOOP3-DECISION-GRADE-UX: Decision-Grade Approval Context + Success Screen Enrichment
**Date:** 2026-04-23
**Window:** W1 (API backend) + W2 (portal pages + proxy routes)
**Scope:** (1) Backend — `handleWasteAdjustmentDetail` + `GET /api/v1/queries/waste-adjustments/:submission_id` (joins form_submissions + waste_adjustments + items/components + app_users + exceptions; returns item name, direction, qty, unit, reason_code, notes, submitter, timestamps, exception_category). Same pattern for `handlePhysicalCountDetail` + `GET /api/v1/queries/physical-counts/:submission_id`. Deployed to Railway (commit c29d354, `railway up --detach`). (2) Portal — Waste and Physical Count submission success/pending banners enriched with item-level context (item summary displayed above monospace detail). Both `/inbox/approvals/waste/[submission_id]` and `/inbox/approvals/physical-count/[submission_id]` pages fully rewritten: useQuery-driven detail card with item name/ID, direction (color-coded), amount, reason, notes, event time, submitted+by, exception category, current status; graceful error fallback. Portal proxy routes added: `/api/waste-adjustments/[submission_id]/route.ts` and `/api/physical-count/[id]/route.ts`. Deployed to Vercel (commit 70cc491, `dpl_9Uaq5iZic2fYansc9ZGnojBQA6aG`).
**Evidence doc:** inline — live DB query for `56c1be71` returned `{item_display_name: "Vodka", direction: "positive", quantity: "50.00000000", unit: "L", submitted_by_display_name: "Tom", exception_category: "positive_adjustment"}`. Railway GET → HTTP 401 (route registered, not 404). Portal TypeScript clean, 63 pages built.
**Gaps closed:** GAP-017 (approval review surface now shows full decision-grade context)
**Gaps opened:** None
**Notes:** Key implementation detail — in Physical Count form, item data must be captured from `snapshot` before `resetFlow()` clears state; local const capture before `setDone()`+`resetFlow()` calls. `DetailRow` typed with `ReactNode` (not `React.ReactNode`) since React is not imported as namespace. Pre-existing API typecheck errors in `planning/handler.ts` are pre-existing, not introduced by this tranche.

### Tranche LOOP4-OPERATOR-FEEDBACK: Operator Self-Sufficiency — GR Context + Movement Log Correctness
**Date:** 2026-04-23
**Window:** W1 (API ledger handler) + W2 (portal GR form + movement log)
**Scope:** (1) Backend — `api/src/stock/ledger-handler.ts`: added `reported_by_snapshot` to ledger SELECT. `api/src/stock/schemas.ts`: added field to `LedgerRow` interface. Deployed to Railway (`0189630`, `railway up --detach`, health 200). (2) Portal — `src/app/(ops)/stock/receipts/page.tsx`: GR success banner now captures supplier name + per-line item label/qty/unit from form state before reset, builds `itemSummary` displayed above the monospace `submission_id` detail. `src/app/(shared)/stock/movement-log/page.tsx`: fixed three bugs: (a) movement type dropdown had `WASTE_LOSS/WASTE_GAIN/COUNT_ADJUST` which don't exist — corrected to `GR_POSTED/WASTE_POSTED/production_output/production_consumption/production_scrap`; (b) date range params `from_date`/`to_date` were silently ignored by API Zod schema — renamed to `from`/`to` with `T00:00:00Z`/`T23:59:59Z` suffix; (c) added "Submitted by" column showing `reported_by_snapshot` (display name) with UUID-truncated fallback. Deployed to Vercel (commit `adfb4d2`, deployment `5h9habzw7`).
**Evidence doc:** inline — Railway health 200; ledger route → 401 (registered); portal build 63 pages clean; portal pushed `96516ae..adfb4d2` to origin.
**Gaps closed:** (movement log bugs were not formally registered; added as new gaps and immediately closed in this tranche)
**Gaps opened:** None
**Notes:** Physical count does NOT write to stock_ledger directly — uses `replace_anchor()` instead. So `COUNT_ADJUST` was not just wrong in the dropdown, it doesn't exist as a movement type at all. Production types are lowercase (`production_output` not `PRODUCTION_OUTPUT`) — this is a known inconsistency in the API that should be normalized eventually (P3, not touched here). `reported_by_snapshot` is null for the one live event before fix `9633ebc` (2026-04-23); all future writes have it populated.

### Tranche LOOP5-PLANNING-TRUST: Planning Decision Context + Jobs Dashboard Visibility
**Date:** 2026-04-23
**Window:** W1 (API planning + jobs handlers) + W2 (portal planning run detail + dashboard)
**Scope:** (1) Backend — `api/src/planning/handler.reads.ts`: extended `handleListRecommendations` SQL to join `components.inventory_uom` / `items.sales_uom` as `uom` and scalar-subquery `current_balances.calculated_on_hand` as `current_stock_bal` per recommendation row. `api/src/planning/schemas.ts`: added `uom: string | null` + `current_stock_bal: string | null` to `PlanningRecommendationRow`. `api/src/admin/jobs/handler.ts`: relaxed role gate from admin-only to `planner|admin|viewer`; added `skipped_count_24h` SQL bucket (status='skipped'). Deployed to Railway (commit `fd959d8`, `railway up --detach`, health 200). (2) Portal — `src/app/(planning)/planning/runs/[run_id]/page.tsx`: added `uom` + `current_stock_bal` to `RecommendationRow` interface; added three new table columns: "On hand" (current_stock_bal + uom inline), "Order by" (order_by_date — already in API response), "Shortage by" (shortage_date — already in API response). `src/features/dashboard/client.ts`: replaced `fetchJobsHealth24h` pending stub with real fetch to `/api/admin/jobs`; aggregates `run_count_24h` / `failed_count_24h` / `skipped_count_24h` to `{successes, failures, skipped}`; `last_failure_reason` sourced from first job with last_status='failed'. Portal proxy `/api/admin/jobs/route.ts` already existed. Deployed to Vercel (commit `70a0850`, `dpl_E1xGr4wFxoXy2Jm6bQEaxVEd8cNK`).
**Evidence doc:** inline — Railway health 200; portal build 63 pages clean; Vercel aliased to `gt-factory-os-portal.vercel.app`; portal typecheck 0 errors.
**Gaps closed:** GAP-004 partial (jobs health tile now live; KPI aggregation tiles still pending). Dashboard jobs tile upgraded from `pending_tranche_i` to live.
**Gaps opened:** None
**Notes:** `current_stock_bal` uses a scalar subquery with `ORDER BY item_type LIMIT 1` as a safety net for the rare case where an item_id appears across multiple item_types — deterministic but may return RM instead of PKG if such a collision existed. In practice, component_id and item_id are separate namespaces so this is not a live risk. `order_by_date` and `shortage_date` columns were already returned by the backend since Phase 7.5 — they were just not rendered in the portal table.

### Tranche LOOP6-FORECAST-LINE-ADD: Forecast Draft Authoring — Add-Item UI + Bucket Generation
**Date:** 2026-04-23
**Window:** W2 (portal — planning/forecast/[version_id] page only)
**Scope:** Closed the P1 planner-blocking gap where fresh forecast drafts were completely unusable from the portal. Three changes: (1) `generateBucketsFromMetadata(horizonStartAt, horizonWeeks, cadence)` — generates ISO period columns for monthly/weekly/daily drafts with no existing lines, so a blank draft immediately shows a writable grid. (2) Add-item control — a select+button panel below the forecast grid; fetches active items from `/api/items?status=ACTIVE&limit=1000`; filters out already-in-forecast items; appends new items to bottom of grid with highlight (`bg-accent-soft/10`); after save the items become server-backed and the local tracking set clears. (3) Item name display — sticky left column now shows item_name as primary text + item_id as secondary monospace code (planners recognize products by name). Also updated empty state copy to direct planners to the add-item control. Also closed GAP-007 as false green: `production-actual/page.tsx` was already fully wired (two-step BOM snapshot flow, consumption preview, pinned bom_version_id); gap registry was stale.
**Evidence doc:** (inline — typecheck exit 0, build exit 0, 63 pages clean, `window2-portal-sandbox` commit pushed)
**Gaps closed:** GAP-007 (false green — Production Actual form was already wired; gap registry stale); partial progress on planner self-sufficiency (fresh draft now populatable without developer API call)
**Gaps opened:** None
**Notes:** `dirtyEntries` only includes cells the planner has touched, so newly added rows with no quantities filled don't pollute the save payload. `addedItemIds` uses a `Set<string>` appended after sorted existing items so new rows visually appear at the bottom. Pre-existing TypeScript errors in `planning/handler.ts` (lines 117/173) are not introduced by this tranche. Bucket generation caps: monthly ≤24 buckets, weekly ≤horizonWeeks+2, daily ≤62 days — prevents unbounded arrays on malformed metadata.

### Tranche LOOP7-PLANNER-DEMAND-CONTEXT: Pre-Run Demand Context Card
**Date:** 2026-04-23
**Window:** W2 (portal — planning/runs/page.tsx only)
**Scope:** Closed the pre-run demand visibility gap on `/planning/runs`. Added a 3-tile context panel above the runs list: (1) Forecast tile — shows latest published forecast version, cadence, horizon, and published_at; warns "No published forecast — planning uses open orders only" if absent; fetches from existing `/api/forecasts/versions?status=published` proxy. (2) Order sync tile — shows LionWheel last sync time (timeAgo) and last_status; warns on failure or 24h failure count; matches `integration.lionwheel` or `lionwheel_poll` job name in `/api/admin/jobs` response. (3) Demand coverage caveat — static amber tile: "Partial — bundle SKUs and unresolved LionWheel mappings are excluded. Recommendations reflect resolved demand only." No new backend endpoints needed — both queries reuse existing proxies. Also runtime-verified all 4 planning routes via HTTP probe: `GET /api/v1/queries/planning/runs` → 401, `POST /api/v1/mutations/planning/run` → 401, `POST /recommendations/:id/approve` → 401, `POST /recommendations/:id/convert-to-po` → 401. Routes confirmed registered on Railway with auth enforced.
**Evidence doc:** (inline — typecheck exit 0, build exit 0, 63 pages clean, commit 27ec31a, deployment dpl_9EFqbteSiW9ptAFXLeUwXp8rTmjJ, Railway HTTP probes all 401)
**Gaps closed:** None formally registered — addresses the pre-run demand visibility gap noted in Loop 6 checkpoint
**Gaps opened:** None
**Notes:** The demand caveat tile is static (hardcoded "Partial") because runtime-dynamic excluded demand count requires a new backend endpoint (scoped to Loop 8). The LionWheel job name probe is defensive — matches both `integration.lionwheel` and `lionwheel_poll`. The `last_ended_at` field is returned by the Railway API but was not in the portal's `AdminJobRow` interface; a new `JobContextRow` interface was added locally to the runs page (not shared to avoid over-coupling). Planning routes are runtime-verified via Railway HTTP probe (401 = route registered + auth enforced), confirming the trigger-approve-convert-to-PO chain is accessible from the portal. Full end-to-end browser verification (trigger → approve → PO creation) remains Tom's checkpoint step.

**What still blocks planner self-sufficiency after Loop 7:**
1. No excluded demand count in the context panel (the "Partial" caveat is static — Loop 8 closes this)
2. No demand breakdown before triggering (what items, what quantities — Loop 8)
3. Full browser-side end-to-end verification (trigger → complete run → approve recommendation → convert to PO → see PO) is Tom's verification step — all infrastructure is in place

### Tranche LOOP8-DEMAND-COVERAGE: Live Demand Coverage Endpoint + Dynamic Planner Tile
**Date:** 2026-04-23
**Window:** W1 (Railway API) + W2 (portal planning/runs page + proxy route)
**Scope:** Replaced the static "Partial" demand caveat tile in `/planning/runs` with live data from a new backend endpoint. (1) Backend — `api/src/planning/schemas.ts`: added `DemandCoverageResponse` interface. `api/src/planning/handler.reads.ts`: added `handleListDemandCoverage()` — queries `orders_mirror_lines` JOIN `orders_mirror` (WHERE `retired_at IS NULL`) grouped by resolution category: resolved (item_id set + resolution_status='resolved'), bundle (lw_sku LIKE 'GTSET%'), and unresolved-non-bundle. Returns line counts, distinct SKU counts, and `is_partial` flag per category. `api/src/planning/route.ts`: registered `GET /api/v1/queries/planning/demand-coverage`. Deployed to Railway (commit `47f22ff`). (2) Portal — `src/app/api/planning/demand-coverage/route.ts`: new proxy to Railway. `src/app/(planning)/planning/runs/page.tsx`: added `DemandCoverageRow` interface, `demandCoverageQuery` (staleTime 3m), replaced static tile with live tile: amber + counts if any exclusions, green + "All active order lines resolved" if fully covered. Deployed to Vercel (commit `40a358e`, pushed to `tomw200082-collab/gt-factory-os-portal` main). Railway endpoint verified live: `GET /api/v1/queries/planning/demand-coverage` → 401 (route registered, auth enforced).
**Evidence doc:** (inline — Railway HTTP probe 401 confirmed; portal typecheck exit 0; build 63 pages clean; portal pushed to GitHub origin)
**Gaps closed:** None formally — Loop 8 closes the planner-visibility sub-gap within GAP-003 (static → dynamic tile); the underlying exclusion causes (bundles, non-catalog, held aliases) remain open
**Gaps opened:** None
**Notes:** The query mirrors `v_planning_demand` inclusion logic exactly (same `retired_at IS NULL` + `lw_qty_ordered > 0` filters). Bundle detection uses `lw_sku LIKE 'GTSET%'` — covers all current bundle SKU patterns. The tile color switches automatically: green when `is_partial=false`, amber when any exclusions exist. `v_excluded_demand` view (created ad-hoc in Tranche L2-EXCLUDED-DEMAND) is NOT referenced by the endpoint — query runs directly against `orders_mirror_lines` for production robustness. Pre-existing API typecheck errors in `planning/handler.ts` (lines 117/173) are not introduced by this tranche.

### Tranche LOOP9-RECENT-SUBMISSIONS: Operator Self-Check — My Submissions Surface (GAP-005)
**Date:** 2026-04-23
**Window:** W1 (Railway API new module) + W2 (portal page + proxy + nav)
**Scope:** Built the missing "recent submissions" surface that operators need to answer "did my form get posted?" without developer involvement. (1) Backend — new `api/src/submissions/` module: `schemas.ts` (RecentSubmissionsResponse interface), `handler.ts` (handleListRecentSubmissions — queries `form_submissions WHERE submitted_by = session.user_id ORDER BY submitted_at DESC LIMIT 20`), `route.ts` (registers `GET /api/v1/queries/submissions/recent`). Registered in `server.ts`. Deployed to Railway (commit `061cda5`). (2) Portal — `src/app/api/submissions/recent/route.ts` (proxy). `src/app/(ops)/stock/submissions/page.tsx` (new page: shows last 20 submissions with status badges: `posted` = stock changed (green), `pending` = awaiting approval (amber), `rejected` = rejected with reason (red), `cancelled` (neutral); auto-refreshes every 60s). `src/lib/nav/manifest.ts` — added "My Submissions" entry (Clock icon, `stock:execute` capability, href `/stock/submissions`, replacing the previously omitted TODO comment). Deployed to Vercel (commit `4a9bc00`, pushed to origin).
**Evidence doc:** (inline — typecheck exit 0; build 64 pages including `/stock/submissions`; Railway endpoint probed at deploy time)
**Gaps closed:** GAP-005 (recent-submissions backend endpoint + portal surface)
**Gaps opened:** None
**Notes:** The nav manifest previously had a comment noting `/stock/submissions` was a "Tranche A target URL" awaiting a dedicated cycle — this tranche delivers it. The `submitted_by` column in `form_submissions` stores the `app_users.user_id` (same as `session.user_id`), confirmed from the waste-adjustments handler pattern. `rejection_reason` is shown inline under the badge when non-null. The page polls every 60s so pending→posted transitions are visible without manual refresh. Admin/planner also see their own submissions here (planning_run_execute, planning_rec_approve, etc. all show up with correct form_type labels).

### Tranche LOOP10-INVENTORY-VALUE: Inventory Value Visibility — Cost × On-Hand Per Item
**Date:** 2026-04-23
**Window:** W1 (Railway API — stock/value-handler) + W2 (portal inventory page + proxy route)
**Scope:** Added economics visibility to the inventory page. (1) Backend — `api/src/stock/schemas.ts`: added `StockValueRow` and `StockValueResponse` interfaces. `api/src/stock/value-handler.ts`: new handler `handleStockValue()` — uses a lateral join `current_balances × items/components × supplier_items (is_primary=true)` to return per-item `unit_cost_ils` (std_cost_per_inv_uom) and `total_value_ils` (on_hand × unit_cost), plus aggregate `total_value_ils`, `items_with_cost`, `items_without_cost`. Items with no primary supplier return null cost. `api/src/stock/route.ts`: registered `GET /api/v1/queries/stock/value`. Deployed to Railway (commit `26ade10`). (2) Portal — `src/app/api/stock/value/route.ts` (new proxy). `src/app/(shared)/inventory/page.tsx`: added `valueQuery` (staleTime 5min), builds `valueMap: Map<"item_type:item_id", {unit_cost, total_value}>`, adds "Unit Cost" and "Value (ILS)" columns to stock table, adds total inventory value banner above the table (shows total + items_with_cost + items_without_cost count). Currency formatted via `Intl.NumberFormat` with ILS locale. Deployed to Vercel (commit `7ab166d`, pushed to origin).
**Evidence doc:** (inline — Railway endpoint `GET /api/v1/queries/stock/value` → HTTP 401 confirmed live (deploy 29bd49eb from api/ subdirectory); portal typecheck exit 0; build clean; portal pushed to GitHub origin)
**Gaps closed:** None formally registered — addresses Loop 10 economics/control-readiness goal
**Gaps opened:** None
**Notes:** Railway deploy must always be run from `api/` subdirectory (where `railway.toml` and the Railway service link live). Deploying from the monorepo root uploads the root `package.json` (which has no API start script) and does not find the `railway.toml` — builds queue and fail silently, leaving the old container running. The lateral join picks only the `is_primary=true` supplier_items row per item. MANUFACTURED FG items typically have no supplier_items row (they're produced, not purchased) — these correctly return null cost/value. For RM/PKG components, std_cost_per_inv_uom should be populated from the seeded supplier_items data. Items with negative on_hand will show negative value (not clamped to zero) — intentional, as it surfaces a real data quality issue. Total value shown in ILS (₪). The `valueMap` key uses `"item_type:item_id"` composite to avoid collisions between FG item_ids and component_ids (different namespaces but not schema-enforced to be disjoint).

### Tranche LOOP11-ECONOMICS-FOUNDATION: Value-Handler P0 Fix (Path B) + Admin Cost Edit
**Date:** 2026-04-23
**Window:** W1 (gt-factory-os: migration + handler) + W2 (portal: inventory display + admin form) + W4 (Green Invoice requirements spec)
**Scope:** (1) W1 — Committed pending 0074 changes (commit 5e65e31: supplier-items delete CRUD + change_log action). Migration 0075: added `std_cost_per_inv_uom money_4dp` to `private_core.supplier_items`; seeded 165/198 rows from `components.std_cost_per_inv_uom` where component_id matches. Fixed `api/src/stock/value-handler.ts` P0: lateral join now valid (column exists post-0075); added `supply_method` to SELECT and response. Updated `StockValueRow` schema to include `supply_method: string | null`. Extended `SupplierItemUpdateSchema` to accept `std_cost_per_inv_uom`. pgTAP 4/4 green. Applied to live Supabase DB. Deployed to Railway (commit 71c58c5). (2) W2 — Updated `/inventory` page: `supply_method`-aware null cost display (MANUFACTURED FG → "Computed (Phase 2)" italic gray; BOUGHT_FINISHED/RM/PKG without cost → "Cost not set" amber); total inventory value banner subtitle added. Added `CostEditCell` to admin supplier detail (`/admin/masters/suppliers/[id]`) supplier-items tab — inline number input + Save + cancel, PATCHes `/api/supplier-items/:id` with `if_match_updated_at` + `idempotency_key`. Commit 1f98e7b on window2-portal-sandbox main. (3) W4 — Authored Green Invoice supplier-price requirements spec at `docs/w4/green-invoice-supplier-price-requirements.md`. FR2 race documented (0075 landed during write window; citation corrected to 0075 — factually accurate).
**Evidence doc:** W1 evidence at `C:/Users/tomw2/Projects/gt-factory-os/docs/0075_std_cost_migration_evidence.md`; verifier PASS on W1 file evidence; W2 typecheck exit 0 + build green (67 static pages); W4 spec at `docs/w4/green-invoice-supplier-price-requirements.md`
**Gaps closed:** GAP-024 (P0 value-handler SQL column error — CLOSED by migration 0075 + handler fix)
**Gaps opened:** GAP-022 (supplier-items GET doesn't return std_cost, edit cell starts blank), GAP-023 (7 BOUGHT_FINISHED items have no cost — Tom manual entry needed)
**Notes:** (1) gt-factory-os has no `origin` remote configured — W1 commits are on local main only; Tom must push manually. (2) 33 supplier_items rows still have no cost after seeding (RM/PKG items with component_id but the corresponding component had no cost). (3) BOUGHT_FINISHED items (7 rows with item_id) were not seeded by the migration — requires admin entry via the new cost edit cell. (4) The end-to-end verification (authenticated GET /stock/value returning non-zero total_value_ils) requires Tom's JWT — 401 confirmed on unauthenticated probe, SQL error eliminated. (5) W4 FR2 race: migration 0075 landed during W4 write window; spec corrected to cite 0075 correctly; under Tom's autonomous-5-loops authorization this is not a hard stop (factually correct correction, not an invented value).

### Tranche LOOP15-DASHBOARD-HEALTH-TILES: Dashboard Parity + Break-Glass Tiles + Cost Edit Fix + W4 Final Spec
**Date:** 2026-04-23
**Window:** W1 (Railway API — parity-check + break-glass endpoints) + W2 (portal dashboard + cost edit) + W4 (integration freshness spec)
**Scope:** (1) W1 — New `api/src/stock/parity-handler.ts`: `handleStockParityCheck()` runs `SELECT private_core.rebuild_verifier() AS drift_count`, returns `{parity_ok, drift_count, checked_at}`. Registered `GET /api/v1/queries/stock/parity-check` in stock route. New `api/src/system/` module (handler.ts + route.ts + schemas.ts): `handleBreakGlassState()` queries `private_core.feature_flags` for `global_readonly` + `jobs_paused` flags, returns `{break_glass_active, jobs_paused, set_at}`. Registered `GET /api/v1/queries/system/break-glass` in server.ts. 2/2 tests green for each endpoint. Railway commit `8a32a0a`, both probes → 401 confirmed. (2) W2 — New proxy routes: `src/app/api/stock/parity-check/route.ts` + `src/app/api/system/break-glass/route.ts`. Dashboard: `fetchParityCheck()` + `fetchBreakGlassState()` fetchers added to client.ts; `ParityCheckBlock` component (green "Parity OK" / red "Parity Drift" + drift count + timestamp, staleTime=60s); `BreakGlassCard` rewritten (green "Normal" / amber "Jobs Paused" / red "Read-Only Mode"). CostEditCell fix: `std_cost_per_inv_uom: string | null` added to `SupplierItemRow`; input now initializes with current cost value; stale "backend gap" comment removed. Build: 71 pages (was 69, +2 new API dynamic routes), 0 TS errors. Commit `a91eb72` pushed to origin/main. (3) W4 — Integration freshness/failure-surface requirements spec authored at `docs/w4/integration-freshness-failure-surface-requirements.md`. W4 rolling backlog now fully exhausted (all 4 items complete). 7 UNRESOLVED items (IF-1 through IF-7). Field names verified from Edge Function PRODUCERS array and migrations.
**Evidence doc:** (inline — verifier PASS W1+W4; W2 build 71 pages clean; Railway probes 401; active_mode.json Loop 15 exit)
**Gaps closed:** GAP-004 partially — rebuild_verifier and break-glass tiles now live; integration freshness and RUNTIME_READY registry still pending
**Gaps opened:** None (UNRESOLVED-IF-1 through IF-7 from W4 spec are requirements gaps, not new code gaps)
**Notes:** Verifier flagged: W1 break-glass handler reads `private_core.feature_flags` directly rather than calling `private_core.is_break_glass()` (the canonical function per migration 0028). Functionally identical but not canonical. W4 spec §5.3 correctly notes this requirement for the integration-freshness handler. Low-priority patch for a future loop. CostEditCell fix was a 1-line change enabled by the Loop 13 W1 GAP-022 fix — the portal was holding a stale "not available from backend" assumption that needed clearing.

### Tranche LOOP14-ADMIN-USER-MANAGEMENT: Admin User Role + Status Management
**Date:** 2026-04-23
**Window:** W1 (Railway API — admin users PATCH endpoint + migration) + W2 (portal admin users page wiring)
**Scope:** (1) W1 — Migration 0076: extended `change_log.action` CHECK from 51 to 53 values, adding `USER_ROLE_CHANGED` and `USER_STATUS_CHANGED`. Applied live to Supabase PG17. New handler `api/src/users/update_handler.ts`: `handleAdminUserUpdate` — admin-only gate (403), 404 not-found branch, 409 `CANNOT_SELF_DEMOTE` guard (admin cannot change own role to non-admin), UPDATE `app_users` SET role/status with `emitChangeLog` calls in transaction. Extended `api/src/users/schemas.ts` with `AdminUserUpdateSchema` + `AdminUserUpdate` type. Registered `PATCH /api/v1/mutations/admin/users/:user_id` in `api/src/users/route.ts`. 4/4 node:test green (T1 401, T2 403 non-admin, T3 200 happy + change_log verified, T4 409 CANNOT_SELF_DEMOTE). Railway commit `dfe1bc9`, HTTP probe 401 confirmed. (2) W2 — New proxy `src/app/api/users/[user_id]/route.ts` (PATCH, proxyRequest pattern). `/admin/users/page.tsx` rewritten: inline role `<select>` per row with `roleMutation`; Deactivate/Activate status button per row with `statusMutation`; self-demote 409 guard ("You cannot change your own admin role."); `useQueryClient` + `invalidateQueries` on both mutations; "manually insert DB row" footer removed, replaced with "New users appear here automatically after their first sign-in." Portal commit `f8292f5`, pushed to origin/main. `active_mode.json` Loop 14 exit appended, mode returned to A.
**Evidence doc:** (inline — verifier PASS on both W1 and W2; W1 4/4 tests; W2 69 static pages clean; Railway 401 probe; active_mode.json confirmed)
**Gaps closed:** GAP-009 partially closed (users surface now wired; jobs/integrations still pending)
**Gaps opened:** None
**Notes:** Migration 0076 was required because `USER_ROLE_CHANGED`/`USER_STATUS_CHANGED` were not pre-existing in the `change_log.action` CHECK constraint. W1 correctly identified the constraint and extended it before adding the handler (rather than using a pre-existing action name that didn't fit). Admin cannot self-demote as a safety invariant — requires another admin to make that change. gt-factory-os still has no origin remote; commit `dfe1bc9` is on local `main` only.

### Tranche LOOP13-PA-HISTORY-AND-CHAIN-CLOSE: Production Actual History + Shopify Chain Audit + GI Fix
**Date:** 2026-04-23
**Window:** W1 (Railway API — PA list endpoint + GAP-022 + GI Edge Function fix) + W2 (portal PA page enrichment) + W4 (dashboard read-model requirements spec)
**Scope:** (1) W1 — Closed GAP-022: added `std_cost_per_inv_uom::text` to `handleSupplierItemsList` SELECT + `SupplierItemRow` interface (2-line fix). Built new `GET /api/v1/queries/production-actuals` endpoint: `list-handler.ts` + schema additions (`ProductionActualListQuerySchema`, `ProductionActualListRow`, `ProductionActualListResponse`) + route registration. Handler joins `production_actual` + `items` + `bom_version` + `form_submissions`; subquery for `consumption_count` (production_consumption ledger rows per submission); parameterized `item_id` filter + `limit` (default 50, max 200); ORDER BY `event_at DESC`. pgTAP 1/1 green (column existence). 4/4 node:test green (401 unauth, 200 viewer envelope, row shape, limit ceiling). Railway deployed commit `3b787a0`, health 200, 401 on unauthenticated probe confirmed. Bonus fix: GI Edge Function `giResolveSupplier()` `$1::uuid` → `$1::text` cast correction (commit `ec7b600`); GI poll restored. (2) W2 — New proxy route `src/app/api/production-actuals/history/route.ts` forwarding to `/api/v1/queries/production-actuals`. Production Actual page `(ops)/stock/production-actual/page.tsx` enriched: "Recent production runs" section (10-row history table, shows Item/Output/Scrap/BOM version/Event time/Consumed count); `queryClient.invalidateQueries` on successful submission; scrap semantics clarification note ("Output = good units produced. FG stock increases by output qty only."); INSUFFICIENT_STOCK error handler fixed (was showing "Submit failed (409)" without shortfall detail — now formats each shortfall as `component_id: need X, have Y`). Portal build: 69 static pages, 0 TS errors, commit `171e4bf` pushed to origin/main. (3) W4 — Dashboard read-model requirements spec authored (`docs/w4/dashboard-read-model-requirements.md`). Contracts for 6 pending tiles: rebuild_verifier drift, break-glass state, integration freshness, RUNTIME_READY registry, runs-today KPI, last-movement. 6 UNRESOLVED items (DR-1 through DR-6, DR-6 closed within spec). Key UNRESOLVED-DR-1: no `private_core.runtime_ready_signals` table — portal cannot read `.claude/state/runtime_ready.json` at runtime; W1 migration needed to seed 11 known signals.
**Evidence doc:** (inline — Railway health 200 + 401 probe confirmed; portal build 69 pages clean; W4 spec at `docs/w4/dashboard-read-model-requirements.md`)
**Gaps closed:** GAP-022 (supplier-items `std_cost_per_inv_uom` missing from response — fixed W1 commit 3b787a0)
**Gaps opened:** UNRESOLVED-DR-1 (no DB-backed runtime_ready_signals table — noted in W4 spec; W1 migration needed)
**Notes:** Deep audit confirmed the full Production Actual → stock_ledger → current_balances → Shopify FG sync chain is code-correct. The Shopify Edge Function reads `current_balances` via JOIN on every 15-min cycle. Chain is BLOCKED only by 0 approved `integration_sku_map` aliases for `source_channel='shopify'` — seeding 61 Shopify aliases is the sole remaining blocker for first real Shopify FG write. False green corrected: operational dataflow blueprint "FG net = output − scrap" is misleading — actual implementation posts +output_qty only, scrap is informational 0-delta row (documented A13 §1 decision in RUNTIME_READY(ProductionActual) checkpoint). Blueprint wording should be updated in a future doc pass. gt-factory-os still has no origin remote — commits 5e65e31, 71c58c5, 74be764, 3b787a0, ec7b600 are on local main only; Tom must push manually.

---

*Log initiated: 2026-04-23.*
