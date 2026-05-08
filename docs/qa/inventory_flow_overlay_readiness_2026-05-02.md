# Inventory Flow — Planned-Inflow Overlay Readiness Check (cycle 17, 2026-05-02; cycle 18 re-check; cycle 20 re-check)

> **Status (cycle 20 re-check, 2026-05-02T18:00Z): VIEW-ready, ENDPOINT-pending. Branch A3 binds.** Cycle 20 dispatch instructed W2 to re-check `runtime_ready.json` for a `RUNTIME_READY` signal carrying the planned-inflow HTTP endpoint (`GET /api/v1/queries/inventory/planned-inflow`). Re-check evidence:
>
> - **VIEW layer (signal #29, `PlannedInflowByDay`):** EMITTED at 2026-05-02T13:30:00Z by executor-w1; evidence_path `Projects/gt-factory-os/docs/cycle18_w1_three_tasks_checkpoint.md`. Migration 0125 applied live to Supabase PG17. Contains `api_read.v_planned_inflow_by_day` with the 11-column shape (`plan_date`, `item_id`, `planned_qty_total`, `completed_qty_total`, `planned_remaining_qty` HEADLINE, `cancelled_qty_total`, `plan_count`, `plan_count_completed`, `plan_count_cancelled`, `plan_count_remaining`, `latest_created_at`). pgTAP 21/21 PASS. **The view is consumable today via direct DB access.**
> - **HTTP ENDPOINT layer (anticipated signal #31, `RUNTIME_READY(PlannedInflowEndpoint)` or sibling):** **NOT EMITTED** as of cycle 20 entry. The runtime_ready.json signal at index 31 is `ProductionActual-TwoHead` (Two-Head BOM Explosion Repair, governor-emitted 2026-05-02T15:30:00Z) — unrelated to inventory-flow planned-inflow. Signal #32 absent; #33 is `Forecast-Monthly`. **No HTTP-endpoint shape signal carrying the planned-inflow API** exists in any of signals #29..#33.
> - **Live API probe (Railway production, 2026-05-02 cycle 20):** `GET https://gt-factory-os-api-production.up.railway.app/api/v1/queries/inventory/planned-inflow` (no auth) returns **HTTP 404** — route not registered. Control: same host's `/health` returns 200 and `/api/v1/queries/inventory/flow` returns 401, both confirming the API container is alive and the existing inventory-flow route is correctly auth-gated. The 404 is not a routing or auth artifact — it is the canonical signal that **W1 cycle 20 has NOT shipped the HTTP endpoint** that consumes the view.
>
> **Branch A3 binds this cycle.** Per cycle 20 dispatch hard rule: "Branch A3 — W1 signal #31 NOT EMITTED at end of your run: Skip overlay implementation. Update cycle 17 readiness doc with cycle 20 status. Focus all your effort on Task B." Skipped: portal proxy, DTO mirror, day-card chip rendering, toggle, footer caveat, stale warning, error state, click-through to `/planning/production-plan`. Effort redirected to `gr_browser_rehearsal_evidence_2026-05-02.md` cycle 20 Tom Walkthrough Plan addendum. Tom-locked deferral *"do NOT build overlay until W1 read-model is safe"* still honored — and now extended: the read-model is half-safe (view live + tested) but the HTTP endpoint is still missing, so portal cannot reach the data without a backend handler. The two layers must be split conceptually: signal #29 unlocks ad-hoc planner SQL queries against the view; the still-unemitted endpoint signal will unlock the portal overlay. The cycle-N+1 W1 work described in §6 below remains the prerequisite — its scope is now narrower (handler + route registration only; the view is already live).

> **Status (cycle 18 re-check, 2026-05-02T22:00Z): Pending W1 read-model.** Cycle 18 dispatch instructed W2 to re-check `runtime_ready.json` for a `RUNTIME_READY(PlannedInflowByDay)` signal (anticipated as signal #28). Re-check result: signal #28 is `LionWheelCreditDecisionBackend` (W1 Wave 2 §Chunk C.2 closure, emitted 2026-05-02T10:39:11Z); **no `PlannedInflowByDay` / `v_planned_inflow_by_day` / `inventory-flow-overlay` signal has been emitted by W1 in cycle 18**. Glob `Projects/gt-factory-os/api/migrations/*planned_inflow*` returned 0 matches at re-check. Glob `Projects/gt-factory-os/api/src/inventory/handler.flow.ts` content for `planned_inflow` returned 0 references. **Branch B3 (skip overlay implementation) is the binding W2 path this cycle.** Tom-locked deferral *"do NOT build overlay until W1 read-model is safe"* honored. The cycle-N+1 W1 work described in §6 below remains the prerequisite; the cycle 18 dispatch did not unblock it. **Superseded by cycle 20 re-check above** — the view layer (migration 0125) landed in cycle 18 itself per signal #29; the HTTP endpoint is the remaining gap as of cycle 20.

> **Purpose.** Tom's cycle 17 dispatch rule: *"Inventory Flow planned overlay readiness — do NOT build overlay until W1 read-model is safe. Prepare UI if read-model exists."* This doc enumerates **what currently exists** on `/planning/inventory-flow`, **what is missing** for the planned-inflow overlay per W4 cycle 4 contract, and **the recommended cycle order** for shipping the overlay safely. It is a readiness audit, not an implementation plan.
>
> **W4 contract under audit:** `Projects/gt-factory-os/docs/integrations/inventory_flow_planned_inflow_overlay_contract.md` (533 lines, authored 2026-05-01, document-only — no DB migration / no API endpoint / no portal route or component changed).

---

## §1 Current /planning/inventory-flow page state

### 1.1 Files in the canonical portal tree

```
window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/
├── page.tsx                          (20 lines — server component, exports metadata + InventoryFlowClient)
├── InventoryFlowClient.tsx           (246 lines — client component with the full grid + filter + skeleton states)
├── _components/
│   ├── DayCell.tsx                   (per-day cell on the desktop grid)
│   ├── DayHeaderRow.tsx              (column-header row above the grid)
│   ├── DayPopover.tsx                (hover/click popover for a day cell)
│   ├── FilterBar.tsx                 (family + search + at_risk_only filters)
│   ├── FlowGridDesktop.tsx           (desktop grid layout)
│   ├── HeroBar.tsx                   (top summary tiles: at_risk_count, earliest_stockout, etc.)
│   ├── MobileCardStream.tsx          (mobile vertical stream; one card per item)
│   ├── MobileItemCard.tsx            (single item card on mobile)
│   ├── StickyItemPanel.tsx           (left-side sticky panel listing items)
│   ├── UnmappedSkusBanner.tsx        (hard-gate banner when unknown_sku_pct_of_demand >= 10%)
│   └── WeekCell.tsx                  (per-week cell on the desktop grid for weeks 3..8)
├── _lib/
│   ├── format.ts                     (number formatters — 0-2 decimal places per inventory_flow_contract.md §6.3)
│   ├── risk.ts                       (risk-tier predicates: isAtRisk, etc.)
│   ├── types.ts                      (TypeScript mirrors of FlowResponseSchema; 117 lines)
│   └── useInventoryFlow.ts           (TanStack Query hook hitting GET /api/v1/queries/inventory/flow)
├── [itemId]/                         (per-item drill-down sub-route)
└── …
```

### 1.2 What the page currently shows (per signal #14 evidence)

Per the live RUNTIME_READY(InventoryFlow) signal #14 (emitted 2026-04-26T10:55:00Z; evidence_path `Projects/gt-factory-os/docs/inventory_flow_runtime_ready_checkpoint.md`; backend handler stack confirmed live at cycle 6.5 commit `9ae6683` with 7/7 node:test green against live pooled Supabase PG17 + Railway production probes 401/200 verified):

1. **Header band:**
   - `WorkflowHeader` with title `"Inventory Flow"`, description `"Daily projection of finished-goods stock over the next 14 days, then weekly through 8 weeks. Stockouts surface at the top; healthy items recede."`
   - Status badge (Loading / Refreshing / Live / Error) tracking the TanStack Query state.
   - `FreshnessBadge` displaying `as_of` timestamp from the API (`label="As of"`, warn after 5 min, fail after 30 min, producer `inventory_flow_projection`).
   - `Refresh now` button forcing `flowQuery.refetch()`.

2. **Hero bar (HeroBar.tsx):**
   - Tiles for `at_risk_count`, `earliest_stockout`, `open_orders_count`, `exceptions_count`, `unknown_sku_pct_of_demand`.
   - Loading skeleton when first paint.

3. **Filter bar (FilterBar.tsx):**
   - `family` filter (URL-driven via `?family=`).
   - `q` search filter (URL-driven via `?q=`; client-side substring match on item_name + item_id + family).
   - `at_risk_only` toggle (URL-driven via `?at_risk_only=`; defaults to `true` unless explicitly `false`).

4. **Grid (desktop) — FlowGridDesktop.tsx:**
   - **14-day daily band** (current_date through current_date + 14 days). One column per day with: `is_working_day`, `holiday_name_he` (if any), `demand_lionwheel`, `demand_forecast`, `incoming_supply` (open POs), `projected_on_hand_eod`, `tier` (`healthy | watch | critical | stockout | non_working`).
   - **Weeks 3..8 weekly band** (six weeks beyond the 14-day daily band). One column per week with: `week_start`, `min_on_hand`, `stockout_day` (if any), `tier`.
   - Item rows aggregate the above per (item_id × {day | week}). Sticky left panel lists items.

5. **Mobile (< 1024px) — MobileCardStream.tsx + MobileItemCard.tsx:**
   - Vertical card stream; one card per item with the same per-day fields displayed horizontally inside each card.

6. **Empty / loading / error states:**
   - Cold-load explainer banner: "Calculating projection… Daily inventory flow runs a heavy SQL pass over forecast + open orders + BOM + on-hand for every active FG. First-time loads can take ~20 seconds."
   - Skeleton grid until isMounted (SSR-safe hydration guard).
   - `ErrorState` banner on `flowQuery.isError`.
   - `EmptyState` banner when filtered items array is empty (with copy variant for at-risk-only true vs false).

7. **Hard-gate `UnmappedSkusBanner`:**
   - When `summary.unknown_sku_pct_of_demand >= 0.10`, the banner replaces the grid entirely. Per `inventory_flow_contract.md` §5.

8. **Per-item drill-down:**
   - `/planning/inventory-flow/[itemId]` — shows LionWheel orders + open POs over the 14-day horizon for the selected item, joined to suppliers (per `inventory_flow_contract.md` §6.1 endpoint `GET /api/v1/queries/inventory/flow/item/:item_id`).

**Verdict:** the page is fully wired against `api_read.v_daily_inventory_flow` (migration 0098) + `fn_compute_daily_fg_projection` (migration 0097) + the cycle 6.5 API handler stack. The base inventory-flow corridor is **CLOSED**. Tom's daily-use need ("see actual stock projection over 14 days + weeks 3-8 weekly aggregation") is met.

---

## §2 What is MISSING for the planned-inflow overlay

Per W4 cycle 4 contract `inventory_flow_planned_inflow_overlay_contract.md` §4 (read-model requirements) + §5 (UI display requirements), every layer below is **NOT YET PRESENT** on the page or in the backend:

### 2.1 Read-model layer (W1 owns)

| Item | Status | Notes |
|------|--------|-------|
| `api_read.v_planned_inflow_by_day` view (or equivalent shape per contract §4.1) | **NOT AUTHORED.** Glob check `Projects/gt-factory-os/api/migrations/*planned_inflow*` returns zero matches. | W4 contract §9 GAP-IFPI-1. W1 must author a future migration slot at migration time. Not blocking this readiness check; blocking eventual UI consumption. |
| `production_plan.rendered_state` derivation embedded in view's CASE expression | **NOT EMBEDDED** (no view exists yet). | W4 contract §9 GAP-IFPI-2. The derivation lives only in the API handler today; needs porting into the view's WHERE/CASE clauses. |
| New API endpoint (Option A: `GET /api/v1/queries/inventory/planned-inflow`; Option B: additive field on `/inventory/flow`) | **NOT AUTHORED.** Glob check `Projects/gt-factory-os/api/src/inventory/handler.flow.ts` confirms no `planned_inflow` reference. | W4 contract §9 GAP-IFPI-3. W1 picks Option A or B per §4.5 at endpoint-authoring time. |
| Auth — viewer + operator + planner + admin (same as base) | **N/A** — no endpoint to gate yet. | W4 contract §4.6. |
| `Cache-Control: no-store` + 60s coupled refresh cadence | **N/A** — no endpoint. | W4 contract §4.8. |

### 2.2 Portal UI layer (W2 owns)

| Item | Status | Notes |
|------|--------|-------|
| Day-card overlay primitive (chip / dotted-bar / icon + count) | **NOT IMPLEMENTED.** `_components/DayCell.tsx` does not currently render a planned overlay. | W4 contract §5.1 + §10 row 6 default = (a) dotted/dashed chip in corner. UNRESOLVED-IFPI-1 — Tom may pick (a)/(b)/(c). |
| `data-testid="planned-inflow-chip"` (or equivalent) on each chip | **NOT PRESENT** | For E2E test wiring. |
| Tooltip "Planned production · not yet posted to stock" section | **NOT IMPLEMENTED** in `DayPopover.tsx`. | W4 contract §5.1 tooltip requirements. |
| Per-day drilldown "Planned production this day" mini-section | **NOT IMPLEMENTED** in `[itemId]/page.tsx`. | W4 contract §5.2. Required fields: plan date, item name, planned qty, UoM, source (`'recommendation' | 'manual'`), source detail (link to rec or "Manual entry by..."), created at, created by, pinned BOM, "Open production form" deep link, "View plan in production-plan board" deep link. |
| Toggle "Show planned production overlay" checkbox | **NOT IMPLEMENTED.** `FilterBar.tsx` has no overlay toggle. | W4 contract §5.1 toggle requirements + §10 row 4 default = ON (UNRESOLVED-IFPI-5; Tom may flip to OFF). |
| Toggle persistence in `localStorage` (key `gtfos.inventoryFlow.plannedOverlayEnabled` recommended) | **NOT IMPLEMENTED** | W4 contract §10 row 3. |
| Footer board-level caveat: **"Stock changes only when production is reported. Planned production shows what is scheduled; it does not affect inventory until posted."** (mandatory, non-dismissible) | **NOT IMPLEMENTED.** No footer caveat element on the page. | W4 contract §7.2 — non-negotiable. |
| Visual hard rules V1–V7 (posted-stock visually dominant, info-tone color, literal "Planned" / "מתוכנן" textually visible, cancelled / done plans never rendered, etc.) | **N/A** — chip not implemented. | W4 contract §5.1. |
| Mobile @ 390px requirements (chip ≥ 24px tall, microcopy not truncated, toggle moves to page header, tap-to-expand drilldown inline) | **N/A** | W4 contract §8. |

### 2.3 Empty / loading / error states for the overlay layer

| State | Required behavior | Status |
|-------|------------------|--------|
| Empty (no plans for `(plan_date, item_id)`) | NO overlay element rendered. Empty days render exactly as today. | **N/A — overlay not implemented.** |
| Loading (overlay data in-flight) | Skeleton matching chip footprint; truth elements render normally (independent fetch). | **N/A** |
| Error (overlay endpoint non-200) | Posted-stock elements render normally; NO overlay chips render; small inline caveat: "Planned production data unavailable — showing posted stock only." | **N/A** |
| Stale plan (plan_date < CURRENT_DATE, still planned) | Overdue plans NOT shown on inventory-flow board; surface on Dashboard §4.4 Slipped Plans + `/planning/production-plan` board. | **N/A — overdue handling out of v1 scope per contract §6.4.** |

---

## §3 Read-model gap — GAP-IFPI-1 verification

**Glob check 2026-05-02:**

```
Projects/gt-factory-os/api/migrations/*planned_inflow*  → 0 matches
Projects/gt-factory-os/api/src/inventory/*planned*      → 0 matches
Projects/gt-factory-os/api/src/inventory/handler.flow.ts → no `planned_inflow` reference
```

**Conclusion: GAP-IFPI-1 is OPEN.** No view, no endpoint, no schema authored as of cycle 17.

**Per cycle 17 W1 dispatch scope** (LionWheel diagnostics, not view authoring): the planned-inflow read-model is **NOT** scheduled to land in cycle 17. The earliest possible W1 land is cycle 18+, contingent on Tom's prioritization.

**Tom's cycle 17 W2 dispatch rule applies:** *"do NOT build overlay until W1 read-model is safe."* Therefore W2 stays in audit-only mode this cycle for the overlay surface. The base inventory-flow page remains untouched.

---

## §4 IFPI-1..11 status — UNRESOLVED items

Per W4 contract §12, eleven UNRESOLVED items pend Tom's first-dispatch decision. Status as of 2026-05-02:

| ID | Question | W4 default | Tom's decision (2026-05-02) | Status |
|----|----------|-----------|------------------------------|--------|
| **IFPI-1** | Visual primitive: (a) dotted/dashed chip in corner; (b) pattern-fill secondary bar; (c) faint icon + count. | (a) dotted chip — smallest footprint. | **NOT YET DECIDED.** | Open. W2 may pick at implementation time within "info tone, never success/warning/error" lock. |
| **IFPI-2** | Localization register: Hebrew (`מתוכנן · לא דווח`) vs English (`Planned · not posted`)? | Hebrew on this surface. | **DECIDED 2026-05-02 (cycle 16 dispatch context):** **English** (per "safe default language register: Actual / Planned / Forecast / Stale"). All overlay microcopy (chip text, tooltip header, footer caveat) renders in English. | **Closed → English.** |
| **IFPI-3** | Should the overlay extend to `/admin/products/[item_id]` (Product 360) in v1? | DEFER to v1.1. | **NOT YET DECIDED — accept default.** | Open (default sticky: defer). |
| **IFPI-4** | Should the overlay cover weeks 3..8 (weekly-aggregated band) in v1? | 14-day daily band only in v1. | **NOT YET DECIDED — accept default.** | Open (default sticky: 14-day only). |
| **IFPI-5** | Toggle default state: ON or OFF? | ON. | **NOT YET DECIDED.** | Open. W4 default: ON. Tom may flip to OFF at first dispatch if first impressions show distraction. |
| **IFPI-6** | Color scheme exact tokens: which info-tone tokens? | W2 picks at implementation time; "info tone, never success/warning/error" is locked. | **N/A — W2 picks within constraint.** | Open (token-level only; semantic locked). |
| **IFPI-7** | Empty-day tooltip: mention "No production scheduled for this day" or stay silent? | Default silent. | **NOT YET DECIDED — accept default.** | Open (default sticky: silent). |
| **IFPI-8** | Should overdue plans (plan_date < today, still planned) appear on inventory-flow board? | NO in v1. Surface on Dashboard §4.4 Slipped Plans only. | **NOT YET DECIDED — accept default.** | Open (default sticky: NO). |
| **IFPI-9** | Should overlay endpoint allow `viewer` role to see planned production, or only `operator | planner | admin`? | Same as base = viewer + operator + planner + admin. | **NOT YET DECIDED — accept default.** | Open (default sticky: same as base). |
| **IFPI-10** | `completed_qty_total` semantic: planned quantity of completed rows OR actually-produced quantity? | Planned quantity. Variance via per-day drilldown. | **NOT YET DECIDED — accept default.** | Open (default sticky: planned qty). |
| **IFPI-11** | Telemetry/analytics — log overlay-toggle events? | DEFER to v1.1. | **NOT YET DECIDED — accept default.** | Open (default sticky: defer). |

**Summary:** 1 of 11 is Tom-locked (IFPI-2 = English). 10 of 11 are at W4 defaults. Only IFPI-2 was a hard blocker per W4 contract §14 stop-condition #10 ("Localization register conflicts unresolved → STOP and request decision before authoring strings"). With IFPI-2 resolved, the overlay can be **built** once the read-model lands; the remaining 10 unresolved items are W2-callable within their default-resolution scope.

---

## §5 Locked invariants & boundaries (must hold across the build)

Per W4 contract §10 + §13 + §14:

| # | Locked invariant | Source | Enforcement |
|---|------------------|--------|-------------|
| L1 | A4 LOCKED — FG netting inbound = 0; overlay does NOT feed engine. | CLAUDE.md, CURRENT_STATE.md, `production_plan_contract.md` §5 rows 4-5 | Non-negotiable. Stop condition #1. |
| L2 | Plans never write `stock_ledger` / `current_balances`. | `production_plan_contract.md` §1, §5 | Non-negotiable. |
| L3 | Overlay color = info-tone, NEVER success/warning/error. | `production_plan_contract.md` §9 | Non-negotiable. V3 enforcement. |
| L4 | Overlay carries literal word "Planned" textually (per IFPI-2 = English). | `production_plan_contract.md` §9 | Non-negotiable. V4 enforcement + §7.1 + §7.3. |
| L5 | Cancelled plans NEVER on overlay (filtered at read-model, not UI). | `production_plan_contract.md` §9 | Non-negotiable. V5 enforcement + A13 #7. |
| L6 | Done plans NEVER on overlay (filtered at read-model). | `production_plan_contract.md` §9 | Non-negotiable. V6 enforcement + A13 #8. |
| L7 | Posted-stock element MUST remain visually dominant; planned overlay is secondary in size, weight, saturation. | W4 contract §5.1 V1 | Non-negotiable. |
| L8 | Posted-stock element MUST NOT be re-colored or re-sized by overlay introduction. | W4 contract §5.1 V2 | Non-negotiable. Stop condition #3. |
| L9 | Overlay never alters `projected_on_hand_eod` number rendered in cell. | W4 contract §5.1 V7 | Non-negotiable. |
| L10 | Footer board-level caveat MUST render at footer always-visible non-dismissible. | W4 contract §7.2 | Non-negotiable. Stop condition #6. |
| L11 | Posted-stock fetch MUST be independent from overlay fetch (no shared loading/error state). | W4 contract §6.3 | Non-negotiable. Stop condition #7. |
| L12 | Overlay is read-only display. Hovering / tapping / toggling never triggers a write. | W4 contract §14 stop #9 | Non-negotiable. |

---

## §6 Recommended cycle order for overlay shipment

This is W2's recommendation to the governor for sequencing the overlay build. Each cycle is one atomic land with its own evidence pack.

### Cycle N (W4) — _NOT NEEDED_
W4 has already authored the contract (cycle 4, 533 lines). No further W4 work required unless Tom changes any of §1, §2, §7, §11, §12, §14 (§15 boundaries).

### Cycle N+1 (W1) — author read-model + endpoint

**Scope:**
1. Author `api_read.v_planned_inflow_by_day` (or equivalent) per W4 contract §4.1 + §4.2.
2. Author endpoint Option A (`GET /api/v1/queries/inventory/planned-inflow?from=&to=`) OR Option B (additive field on `/inventory/flow`). W1 picks at implementation time per §4.5.
3. Zod schema + Fastify handler + auth gate (viewer + operator + planner + admin per §4.6).
4. pgTAP for view (cancelled-rows-zero, done-rows-zero, aggregation correctness).
5. node:test for endpoint (auth gates, happy path, idempotency).
6. Apply migration to live Supabase PG17.
7. Deploy via `railway up` from `api/` subdirectory.
8. Production probes (200 with auth, 401 without).
9. Emit `RUNTIME_READY(InventoryFlowPlannedInflowOverlay)` (or W1's chosen signal name) with `evidence_path` pointing at the checkpoint doc.

**Closes:** GAP-IFPI-1, GAP-IFPI-2, GAP-IFPI-3.

**Authority required from Tom:** none beyond existing W4 contract acceptance. W1 owns the implementation shape decisions (Option A/B, view name, endpoint path).

### Cycle N+2 (W2) — portal overlay consumption

**Scope (after W1 cycle N+1 emits RUNTIME_READY):**
1. Add new TanStack Query hook `usePlannedInflow(params)` mirroring `useInventoryFlow`.
2. Add `PlannedInflowChip` primitive to `_components/DayCell.tsx` (default = (a) dotted chip per IFPI-1 default).
3. Extend `DayPopover.tsx` with "Planned production · not yet posted to stock" tooltip section.
4. Add overlay toggle to `FilterBar.tsx` with `localStorage` persistence on key `gtfos.inventoryFlow.plannedOverlayEnabled` (default ON per IFPI-5 default).
5. Add board-level footer caveat (non-dismissible, English per IFPI-2 = "Stock changes only when production is reported. Planned production shows what is scheduled; it does not affect inventory until posted.").
6. Extend `[itemId]/page.tsx` with "Planned production this day" mini-section.
7. Mobile @ 390px: toggle moves to page header; tap-to-expand drilldown inline.
8. Empty / loading / error states per W4 contract §6.
9. Author Playwright spec covering the W4 §11.1 walk-through.
10. Validation gates 4/4 (typecheck, build, lint:urls, Hebrew/RTL grep).
11. Atomic commit, push, Vercel auto-deploy probe.

**Closes:** GAP-IFPI-4.

**Authority required from Tom:** none if W4 defaults apply. If Tom wants different visual primitive (IFPI-1) or default toggle state (IFPI-5) or unmoved Hebrew (IFPI-2 already locked English), Tom dispatches the change.

### Cycle N+3 (W2, optional) — Product 360 history-chart overlay extension

Defer to v1.1 per IFPI-3 default. Out of scope for the corridor closure cycle.

---

## §7 Dependencies + sequencing

```
Tom: "build the overlay"
  └─ Tom decides IFPI-1 (visual primitive) + IFPI-5 (default toggle state) + accepts other defaults
       └─ governor dispatches W1 cycle N+1 (read-model + endpoint)
            └─ W1 emits RUNTIME_READY(InventoryFlowPlannedInflowOverlay)
                 └─ governor dispatches W2 cycle N+2 (portal overlay)
                      └─ W2 atomic commit + push + Vercel deploy + browser rehearsal
                           └─ Tom executes browser rehearsal → corridor CLOSED
```

**Hard sequencing rule:** W2 cycle N+2 cannot start until W1 cycle N+1 is on disk and the signal is in `runtime_ready.json`. This is the standard EXECUTION_POLICY.md Mode B-FILE_READY-vs-RUNTIME_READY guardrail. **Premature W2 build without read-model would either (a) compile-fail (no endpoint to call) or (b) ship dead UI (overlay always empty). Both are harmful — they create the impression of progress without it.**

---

## §8 Verification this cycle was audit-only

| Check | Result |
|-------|--------|
| Portal source files modified for overlay-related code | **0** files |
| Portal source files modified at all | **1** file — comment-only fix at `(po)/purchase-orders/[po_id]/page.tsx:1319-1321` removing stale W2-FOLLOWUP-RECEIPTS-PO-PREFILL claim (cycle 16 closed it). Documented in cycle 17 hardening pass section of `runtime_dead_end_audit.md`. NOT related to overlay. |
| Backend source files modified | **0** files |
| Migrations authored | **0** files |
| New RUNTIME_READY signal emitted | **0** signals |
| `runtime_ready.json` modified | **NO** (W1-owned) |
| `inventory_flow_contract.md` or `inventory_flow_planned_inflow_overlay_contract.md` modified | **NO** (W4-owned) |
| New contract values invented | **NO** |
| Sandbox-to-canonical promotion | **NO** |
| `.env` / credentials / secrets touched | **NO** |
| Tom-locked surfaces (`/planning/blockers` Hebrew page-title) touched | **NO** |

**Verdict:** cycle 17 W2 work on the overlay surface is audit-only as Tom's dispatch required. The build is correctly deferred until W1 ships the read-model.

---

## §9 Authorization basis

- EXECUTION_POLICY.md Mode B-Planning-Corridor 2026-05-02 amendment + cycle 17 dispatch carve-out enumerates `/planning/inventory-flow` under Allowed surfaces for **audit work** only (overlay build is Tom-locked deferred per dispatch rule).
- Signal #14 RUNTIME_READY(InventoryFlow) emitted 2026-04-26T10:55:00Z by executor-w1 (evidence_path `Projects/gt-factory-os/docs/inventory_flow_runtime_ready_checkpoint.md`) verified readable on disk before audit authoring.
- W4 cycle 4 contract `Projects/gt-factory-os/docs/integrations/inventory_flow_planned_inflow_overlay_contract.md` (533 lines) verified readable on disk before audit authoring.
- Tom's cycle 16 dispatch resolution of IFPI-2 = English ("safe default language register: Actual / Planned / Forecast / Stale") is the only Tom-locked closure on the IFPI-1..11 list.
- Tom's cycle 17 dispatch rule "do NOT build overlay until W1 read-model is safe; prepare UI if read-model exists" is binding on this readiness check.

This is an audit document. No portal source files were modified during overlay-readiness analysis (the unrelated cycle 16 stale-comment fix on `(po)/purchase-orders/[po_id]/page.tsx` is documented in `runtime_dead_end_audit.md` under "Cycle 17 hardening pass").

---

## §10 Cycle 18 re-check — Status: Pending W1 read-model

**Re-check timestamp:** 2026-05-02T22:00Z (executor-w2, cycle 18 tranche `gr-browser-evidence-and-inventoryflow-overlay-readiness`).

**Cycle 18 dispatch instruction:** W1 cycle 18 was anticipated to author `api_read.v_planned_inflow_by_day` and emit `RUNTIME_READY(PlannedInflowByDay)` (or equivalent) as signal #28, parallel to the cycle 18 W2 dispatch. If that signal landed mid-cycle, W2 would switch to **Branch B1** and begin the overlay UI build per W4 cycle 4 contract `inventory_flow_planned_inflow_overlay_contract.md` §5.1.

**Re-check evidence:**

| Check | Result |
|-------|--------|
| `.claude/state/runtime_ready.json` signal #28 | `LionWheelCreditDecisionBackend` (W1 Wave 2 §Chunk C.2, emitted 2026-05-02T10:39:11Z) — **NOT** `PlannedInflowByDay` |
| `.claude/state/runtime_ready.json` grep `PlannedInflowByDay\|planned_inflow\|v_planned_inflow_by_day` | **0 matches** |
| `Projects/gt-factory-os/api/migrations/*planned_inflow*` glob | **0 files** |
| `Projects/gt-factory-os/api/src/inventory/handler.flow.ts` content `planned_inflow` grep | **0 references** |
| `Projects/gt-factory-os/api/src/inventory/*planned*` glob | **0 files** |

**Branch decision: B3 — skip overlay implementation entirely this cycle.**

Per cycle-18 dispatch instructions, Branch B3 actions: (a) skip overlay implementation; (b) update this readiness doc with `Status: Pending W1 read-model` (done above); (c) record in commit message: "Inventory Flow overlay UI deferred — W1 read-model signal #28 not yet live this cycle."

**No portal source files modified in cycle 18 for the overlay surface.** Validation gates not run for portal source (no portal source modified). The cycle 18 deliverables this cycle are documentation-only:

- `gr_browser_rehearsal_evidence_2026-05-02.md` (NEW, ~330 lines, Task A static evidence pack for the cycle-17 12-step browser checklist).
- `inventory_flow_overlay_readiness_2026-05-02.md` (this file, +§10 cycle 18 re-check section, Task B Branch B3 outcome).

**Recommended next dispatch:** governor commissions W1 to author `api_read.v_planned_inflow_by_day` + endpoint per W4 cycle 4 contract §4.1 + §4.2 + §4.5 (Option A or B), emit `RUNTIME_READY(InventoryFlowPlannedInflowOverlay)` (or W1's chosen signal name), and only THEN dispatch W2 to consume the read-model and ship the overlay UI per §6 Cycle N+2 scope. The hard sequencing rule from §7 stands: premature W2 build without read-model would compile-fail or ship dead UI.

**Authorization basis (cycle 18 re-check):** EXECUTION_POLICY.md Mode B-Planning-Corridor 2026-05-02 amendment + cycle 18 dispatch carve-out for `/planning/inventory-flow` audit + `PRODUCTION/docs/qa/`. Re-check itself is an audit-only mode-B activity (no portal source touched).
