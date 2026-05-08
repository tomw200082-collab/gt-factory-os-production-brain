# Planning Screens Upgrade — Masterplan

**Owner:** Tom (sole approver)
**Authored by:** governance routing (master audit + architecture + roadmap run)
**Branch:** `planning-masterplan-2026-05-08`
**Status:** PROPOSAL — awaiting Tom approval before any execution tranche
**Authority weight:** advisory. Does not override `CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, or any locked decision. Does not authorize any portal source change. Implementation requires per-tranche dispatch.

---

## 0 — Why this document exists

GT Factory OS now has **19 planning-related portal surfaces** plus a dashboard pair (v1 / v2). They were built corridor-by-corridor over months of cycles. Each surface ships individually correct. Together they are not yet a coherent planning system.

The user (Tom) called for a Planning Screens Improvement Program — but explicitly asked for a master audit + architecture + roadmap **before** any broad redesign run. This document is that artifact.

It answers four questions:

1. What planning surfaces exist today, who reads them, what decisions they are supposed to support.
2. What is broken, what is fragile, what is blocked by Window B (BOM verification still in flight).
3. What should the planning system look like architecturally — not as 19 isolated screens, but as a single decision system supporting one operator's daily rhythm.
4. What should the **first execution tranche** be, and what should *follow* it.

This document does not implement anything. No portal source changed in this run. No backend changed. No frozen flag flipped. No deploy.

---

## 1 — State of the world (2026-05-08)

| Layer | State |
|---|---|
| PRODUCTION brain | clean, `main` @ `258ac3c`, Run G in flight on a separate branch |
| Portal (`window2-portal-sandbox`) | clean, `main` @ `9e2212e` (FLOW-003 closed via Run C) |
| Backend (`gt-factory-os`) | dirty on `run-d-b3-4-supabase-branch-bom-verification` — **Window B still open** |
| Active corridors | Shopify External Boundary v2 (Phase 4 in flight, Gate E pending) · Planning Corridor v1 (Tranches 1-3 closed; cycles 7-8 closed) · Sunday cutover 2026-05-10 |
| Aggregate UX gate | `CONDITIONAL_SHIP` — was HOLD pre-Run-C |
| Audit P0 status | 8 of 11 closed via cycles 2-8; **2 still open** (P0-D PO Hebrew banner, P0-G production-simulation IDB false green) |
| RUNTIME_READY count | 35 |
| Frozen flags | `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false` — both must remain false during this program |

### Constraints (non-negotiable)

- No edits to product runtime in this run.
- No edits to BOM-verification migrations 0156–0174 (Window B owns those).
- No edits to authority docs (`CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, `WORKSPACE_MAP.md`).
- No edits to `portal_ux_standard.md` or `portal_language_direction_audit.md` (UX-content-state-designer is sole writer).
- No new modules. No CRM / lead intake / sales / marketing / finance.
- No `git push` to main on any repo. Branch + commit only; Tom pushes when ready.

---

## 2 — Planning surface inventory (19 surfaces)

Compact map. Full per-surface detail (data entities, top-level imports, primary actions, deep-links) lives in the discovery scan output of this run. Surface type legend: `O` = overview, `T` = triage, `D` = decision, `E` = execution, `A` = admin/config, `S` = simulation.

| # | Route | Surface name | Primary user | Type | Sidebar nav | Status |
|---|---|---|---|---|---|---|
| 1 | `/dashboard` | Dashboard v1 (Control Tower) | planner+admin | O+T | yes | **Live, fragmented** — 8-block layout, missing planning quick-actions |
| 2 | `/dashboard/v2` | Dashboard v2 (Control Tower MVP) | planner+admin | O+T | **no** | Live MVP, 7 of 8 sub-blocks render placeholder cards |
| 3 | `/planning` | Planning Overview | planner | O | yes | Bare links page; no decision content |
| 4 | `/planning/forecast` | Forecast list | planner | A | yes | Live, English, clean |
| 5 | `/planning/forecast/[version_id]` | Forecast detail (edit/publish) | planner | A | (deep-link only) | Live; one Hebrew Active-callout was P1 (cycle 3 sweep) |
| 6 | `/planning/forecast/new` | New forecast draft | planner | A | (deep-link only) | Live, clean |
| 7 | `/planning/runs` | Planning runs list | planner | T | yes | Live, English (post-cycle-3 closure) |
| 8 | `/planning/runs/[run_id]` | Run detail + recommendations summary | planner | D | (deep-link only) | Live, English (post-cycle-3 closure) — **decision surface** |
| 9 | `/planning/runs/[run_id]/recommendations/[rec_id]` | Recommendation drill-down | planner | D | (deep-link only) | Live, English (post-cycle-3 closure) — **decision surface** |
| 10 | `/planning/production-plan` | Daily Production Plan | planner | E | yes | Live, English, Gate-4.2-clean |
| 11 | `/planning/production-simulation` | Production Simulator (IDB) | admin | S | yes | **P0-G open** — IDB-backed, false-green risk |
| 12 | `/planning/blockers` | Blockers worklist | planner | T | yes | Live (Hebrew Tom-locked); FLOW-003 closed |
| 13 | `/planning/boms` | BOM Simulator | admin | S | **no** | Orphan; BOM Simulation UX correction queued (project memory) |
| 14 | `/planning/weekly-outlook` | Weekly outlook | planner | O | **no (was added 2026-04-25, manifest verify needed)** | Live |
| 15 | `/planning/inventory-flow` | Inventory Flow (FG, 14d/6w) | planner | O+T | yes | Live, FreshnessBadge-clean — **most-used surface** |
| 16 | `/planning/inventory-flow/[itemId]` | Inventory Flow item detail | planner | T | (deep-link only) | Live |
| 17 | `/planning/inventory-flow/supply` | Supply Flow (components, 14d/6w) | planner | O+T | **no** | Live but not in primary nav |
| 18 | `/admin/planning-policy` | Planning policy parameters | admin | A | yes | Live |
| 19 | `/admin/holidays` | Israeli holidays calendar | admin | A | yes | Live (cycle 8 closure 2026-05-08) |

### Inventory observations

- **Two dashboards exist.** v1 and v2 are both live; v2 not in nav. Either v2 graduates and v1 is deprecated, or v2 is folded into v1. The split is the single biggest source of fragmentation.
- **Two simulators exist.** `/planning/production-simulation` and `/planning/boms` are both IDB-backed simulation surfaces with overlapping responsibility. P0-G flags one as false-green. The BOM Simulation UX correction is queued (project memory, post-PO-corridor).
- **Three planning surfaces are not in primary sidebar nav.** Supply Flow, Weekly Outlook, BOM Simulator — these are reachable only via deep-link or direct URL.
- **`/planning` overview is content-bare.** It is a hub-page of links to other planning surfaces with no embedded operational content.

---

## 3 — Backend asset map and Window B exposure

### Stable / production-ready (LOW Window B risk)

| Asset | Type | Migration | Consumed by |
|---|---|---|---|
| `v_critical_today` | view | 0117 | `/dashboard` block 1 + `/dashboard/v2` |
| `v_production_plan_slippage` | view | 0118 | `/dashboard` + `/dashboard/v2` |
| `v_planned_inflow_by_day` | view | 0125 | inventory-flow planned-inflow overlay |
| `v_daily_inventory_flow` | view | 0098 | `/planning/inventory-flow` |
| `v_daily_supply_side_flow` | view | 0146 | `/planning/inventory-flow/supply` |
| `production_plan` | table | 0115 | `/planning/production-plan` + slippage view |
| `planning_runs` + recommendations + exceptions | tables | 0037 | `/planning/runs` chain |

### BOM-walking core (HIGH Window B risk)

| Asset | Type | Migration | Why high risk |
|---|---|---|---|
| `fn_explode_bom_to_components` | function | 0041 (v2 0126 two-head) | Recursive BOM walker; output materially shifts if a BOM line flips active/inactive |
| `fn_compute_fg_net_requirements` | function | 0040 | Gates `missing_bom` exception emission |
| `fn_compute_component_net_purchase` | function | 0042 | Component-level demand |
| `fn_execute_planning_run` | function | 0045 | Orchestrator; emits `planning_run_recommendations` and `planning_run_exceptions` |
| `planning_run_exceptions` (data) | data | n/a | Existing `missing_bom` rows may become stale or require re-emission post-Window-B |

### What this means for the planning UX program

- **Surfaces backed by stable views** (Dashboard, Production Plan, Inventory Flow, Blockers worklist) can be improved **now** with low coupling to Window B.
- **Surfaces backed by the BOM-walking engine** (Run Detail recommendations, Recommendation Drill-Down, exception deep-links) carry an implicit invariant: the recommendations a planner approves today reflect the BOM truth at run time. If Window B shifts BOM truth, *historical* recommendations remain immutable evidence; *new* runs after BOM verification will produce different output.
- **Production Simulation and BOM Simulator** depend on BOM correctness end-to-end — these are the highest Window B-blocked surfaces.

---

## 4 — Audit synthesis (where we actually are after cycles 2-8)

Source: `PRODUCTION/docs/overnight_audit_2026-05-01.md` (16 P0 / 38 P1 / 50 P2 / 29 P3 across 12 corridors). Cycles 2-8 closed 8 of 11 P0s. Freshness check on disk 2026-05-08 confirms.

### Closed P0s (cycles 2-8, verified on disk)

| Corridor | What was P0 | Closure |
|---|---|---|
| Production Actual form | Hebrew throughout | Cycle 2 — English re-write landed |
| Run detail (`/planning/runs/[run_id]`) | Hebrew sources + Hebrew rec summary | Cycle 3 — full English re-write |
| Recommendation drill-down | Hebrew everywhere | Cycle 3 — full English re-write |
| Run list (`/planning/runs`) | Hebrew title + CTA | Cycle 3 — English |
| Run freshness | `(לפי הריצה — ...)` everywhere | Cycle 3 — `as of run` standardized |
| Forecast active-callout | Hebrew P1 banner | Cycle 3 sweep |
| Dashboard quick-actions | Missing planning surfaces | Cycle 4 — Daily Production Plan / Inventory Flow / Blockers added |
| Forecast active callout | Hebrew | Cycle 4 |

### Still-open P0s (per `CURRENT_STATE.md`)

| ID | Surface | What | Blocking |
|---|---|---|---|
| P0-D | `/(po)/purchase-orders/[po_id]` | Hebrew manual-PO banner inside English page | Tom decision POGR-2 |
| P0-G | `/planning/production-simulation` | IDB false green — operator can simulate without live data, mistake it for live planning | Tom decision PSDP-1..4 |

### Open P1 backlog (planning corridor only — most relevant to this program)

Categorized for later consumption:

**A. Decision-context completeness**
- Recommendation drill-down: `lead_time_days` source unknown (component? supplier override? policy default?). Audit said: stamp source.
- Run detail: `Run sources` section misses freshness timestamps on `demand_snapshot_orders_snapshot_run_id`.
- Run detail: when `purchase_recs_count + production_recs_count === 0`, no "what this means" explainer above the recs section.
- Inventory Flow: legend does not state "Planned production NOT included" (per A4 lock).

**B. Action surface friction**
- No bulk-approve for ready production recs (cycle 6 partially landed; verify).
- No "→ PO 1234" chip on rec row when `converted_to_po_id` is set.
- Run detail exception rows render raw `item_id` / `component_id` instead of names (regression vs `0997398` lock).
- Recommendation drill-down still shows approve/reject buttons when `rec.status !== 'pending'`.

**C. Navigation / dead ends**
- Exception action `missing_supplier_mapping` routes to `/admin/masters/items/<componentId>` (wrong; should go to `/admin/masters/components/<componentId>`).
- Exception `missing_bom` deep-link lands on overview tab instead of `?tab=bom`.
- No "← Back to Dashboard" on `/admin/sku-map` permission-denied state.
- Recommendation drill-down "rec missing" state has only `Back to recommendations`, not a path to current run.

**D. State hygiene**
- Run detail has no skeleton on the recommendations card while purchaseQuery/productionQuery load — brief misleading "0 total".
- Forecast empty-state mentions "Try clearing the filter" but offers no inline `Clear filter` button.

**E. Mobile @ 390px**
- Inventory-flow day popover modal centered, not slide-up (violates Tom-locked global pattern).
- Run detail mobile per-rec card wraps action row to three lines.
- Inbox filter chips wrap to 3 lines.
- Dashboard block-1 stat-strip pushes content below fold on mobile.

**F. Freshness vocabulary**
- Five different freshness components in use across the chain: `FreshnessBadge`, `as of <time>` chip, `(לפי הריצה — ...)`, `Live` badge, plain `at <iso>`. Standardize on `FreshnessBadge`.

**G. Tom-tax (daily friction)**
- No "Receive against this PO →" CTA on PO detail.
- No "View posted movement" inline link after production-actual submit.
- No "Open recipe →" link on inventory-flow item detail.
- No "What changed in last 24h" block on dashboard.
- Forecast publish path is List → Detail → Edit → Publish; no inline `Resume draft` action.

**H. False-green risks (still latent)**
- Production Simulation false-green (P0-G).
- BOM Simulator overlap (project memory: queued).
- Dashboard `BreakGlassCard` "All systems operational" tone too cheerful.
- Production-tab "Ready if purchase executes" chip relies on backend feasibility flag without UI cross-check.
- `/admin/sku-health` `shopify_variant_match` always "unknown" but column rendered as complete.

### Net picture

The planning corridor is no longer in a P0 emergency. It is in a P1-polish + architectural-fragmentation phase. The remaining open P0s (P0-D, P0-G) are isolated and tractable. The real work now is:

1. Architectural — close the dashboard split, decide simulator fate, normalize freshness vocabulary, add missing nav entries.
2. Decision-context — close the "show source / show freshness / show what this means" gaps on the run-detail and rec-drill-down surfaces.
3. Operating-rhythm — add the surfaces a planner needs *between* the existing surfaces (last-24h activity, today's plan-vs-actual delta, what-needs-my-attention-now).

---

## 5 — Planning problem register

Categorized for triage. Severity: P0 = blocks ship; P1 = high impact, high frequency; P2 = nice-to-have polish; Def = deferred (Window B or product decision).

### 5.1 Data truth / dependency issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| DT-1 | Run Detail recommendations | Recommendations from runs prior to BOM verification may not match new-run output | Def | yes | no — re-run after Window B |
| DT-2 | Production Simulation | IDB-backed; not source-of-truth-aligned (P0-G) | P0 | partial | needs Tom decision PSDP-1..4 |
| DT-3 | BOM Simulator (`/planning/boms`) | Same IDB false-green risk as DT-2 | P1 | partial | queued post-PO corridor (project memory) |
| DT-4 | Inventory Flow | A4 lock — does not include planned production as inflow; legend silent on this | P1 | no | yes (UX-only — add legend note) |
| DT-5 | Run sources card | Lacks freshness timestamps on demand snapshot, orders snapshot, anchor sync | P1 | no | yes (UX-only) |

### 5.2 Decision framing issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| DF-1 | Dashboard v1 vs v2 | Two dashboards exist; planner doesn't know which is canonical | P1 | no | yes — graduate v2 or fold into v1 |
| DF-2 | `/planning` overview | No decision content; hub of links only | P1 | no | yes — replace with "Today" view |
| DF-3 | Recommendation drill-down | Lead time source not stamped | P1 | no | yes |
| DF-4 | Run Detail | When 0 recs + N exceptions, no "what this means" explainer | P1 | no | yes |
| DF-5 | Dashboard | No "What changed in last 24h" surface | P1 | no | yes (needs new read-model) |
| DF-6 | Inventory Flow | No planned-production overlay (A4 lock means engineering decision, not just UX) | Def | no | needs A4 lock revisit |

### 5.3 Actionability issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| AC-1 | Run Detail production tab | No bulk-approve for ready production recs (partial cycle 6) | P1 | no | yes — verify cycle 6 closure on disk |
| AC-2 | Run Detail rec rows | No "→ PO 1234" chip after convert-to-PO | P1 | no | yes |
| AC-3 | Recommendation drill-down | Approve/reject buttons stay enabled after rec.status moves off `pending` | P1 | no | yes |
| AC-4 | PO detail | No "Receive against this PO →" CTA | P1 | no | yes (PO corridor — adjacent) |
| AC-5 | Production Actual success | No "View posted movement" inline link | P1 | no | yes |
| AC-6 | Inbox | No "snooze / dismiss without resolving" path | P1 | no | yes |

### 5.4 Navigation / flow issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| NV-1 | Run Detail exception rows | `missing_supplier_mapping` routes to `/admin/masters/items/...` instead of `/admin/masters/components/...` | P1 | no | yes |
| NV-2 | Run Detail exception rows | `missing_bom` lands on overview tab; should append `?tab=bom` | P1 | no | yes |
| NV-3 | Sidebar nav | Supply Flow, Weekly Outlook, BOM Simulator, Dashboard v2 not in primary nav | P1 | no | yes |
| NV-4 | Recommendation drill-down | "rec missing" state has only `Back to recommendations`, no path to current run | P2 | no | yes |
| NV-5 | Inventory Flow item detail | No "Open recipe →" link | P2 | no | yes |
| NV-6 | Forecast | Publish path requires List → Detail → Edit → Publish; no inline `Resume draft` | P2 | no | yes |

### 5.5 Information hierarchy issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| IH-1 | Run Detail | `Run sources` section dense, hard to scan; no `FreshnessBadge` | P1 | no | yes |
| IH-2 | Dashboard v1 | Block 1 stat strip pushes content below fold on mobile; 9 quick-action cards stack | P1 | no | yes |
| IH-3 | Run Detail | Exception rows render raw IDs instead of names (regression vs `0997398`) | P1 | no | yes |
| IH-4 | Run Detail | Policy snapshot accordion shows 50+ keys at default monospace; unhelpful | P2 | no | yes |
| IH-5 | Inventory Flow legend | Risk-tier chips lack color-blind variant | P2 | no | yes |

### 5.6 Visual clarity / density issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| VC-1 | Mobile day popover (Inventory Flow) | Centered modal not slide-up — violates Tom-locked global pattern | P1 | no | yes |
| VC-2 | Run Detail mobile | Per-rec card wraps action row to 3 lines | P1 | no | yes |
| VC-3 | PO list mobile | KPI tile strip horizontally scrolls at 390px | P1 | no | yes |
| VC-4 | Inbox mobile | 8 view chips wrap to 3 lines | P2 | no | yes |
| VC-5 | Forecast detail mobile | 8 weekly buckets force horizontal scroll | P2 | no | yes |

### 5.7 State handling issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| SH-1 | Run Detail | Rec card shows "0 total" briefly while secondary queries load | P1 | no | yes |
| SH-2 | Dashboard | Inconsistent loading-shell pattern across blocks | P1 | no | yes |
| SH-3 | Dashboard `InboxTotalCard` | Cold-cache shows "—" with `pending_tranche_i` signal — looks like backend issue | P2 | no | yes |
| SH-4 | Production Actual | `done.kind === "error"` and `itemsQuery.isLoading` can render simultaneously | P2 | no | yes |
| SH-5 | Inbox | When all 4 source streams loading, brief pre-merge state | P3 | no | yes |

### 5.8 Ownership / operating-rhythm issues

| ID | Surface(s) | Problem | Severity | Window B blocked? | Solvable now? |
|---|---|---|---|---|---|
| OR-1 | Cross-system | No "Today" surface aggregating critical-today + ready recs + plan + open blockers + last-24h | P1 | no | yes (needs new read-model) |
| OR-2 | Cross-system | Five freshness vocabularies; standardize on `FreshnessBadge` | P1 | no | yes (UX-only) |
| OR-3 | Production Plan ↔ Production Actual | If operator opens form but doesn't submit, plan stays `Planned` forever; no in-flight status | P1 | no | needs backend signal |
| OR-4 | Cross-system | After production-actual success, inventory-flow shows ~30-60s stale data | P2 | no | yes (cache invalidation) |
| OR-5 | Cross-system | Role badge renders raw enum across all surfaces | P2 | no | yes (single util) |

---

## 6 — Target planning architecture

The current 19-surface set was built corridor-by-corridor. The target is a planning *system* organized around the planner's actual decision cycle.

### 6.1 Jobs to be done (planner)

1. **First-glance scan.** "Is anything urgent? Did anything break overnight? What needs my attention right now?"
2. **Triage.** "Of the open exceptions / blockers / approvals, which ones must I resolve today, this week, later?"
3. **Diagnose.** "Why is this item flagged? What does the recommendation depend on? Can I trust it?"
4. **Decide.** "Approve, dismiss, escalate, or wait."
5. **Execute.** "Convert this approval into a downstream artifact (PO, production plan entry, exception resolution)."
6. **Confirm.** "Did the action take effect? Where is the audit trail?"
7. **Plan ahead.** "What is forecast saying for next month? Are policy parameters still right?"

### 6.2 Surface taxonomy

The 19 surfaces map cleanly into **five operational layers**:

| Layer | Job | Current surfaces | Target |
|---|---|---|---|
| 1. Command center | Decision (1) — "What needs me now?" | `/dashboard`, `/dashboard/v2` (split) | Single graduated dashboard with planning quick-actions, last-24h activity tile, freshness-standardized blocks |
| 2. Triage queues | Decision (2) — "Triage" | `/planning/blockers`, `/inbox`, `/planning/runs` (list) | Keep three; ensure they share a freshness/severity/age vocabulary |
| 3. Diagnosis | Decision (3) — "Diagnose" | `/planning/runs/[run_id]`, `/planning/runs/[run_id]/recommendations/[rec_id]`, `/planning/inventory-flow`, `/planning/inventory-flow/[itemId]`, `/planning/inventory-flow/supply` | Keep all; harden decision-context (lead-time source, freshness, exception deep-links) |
| 4. Decision + Execution | Decisions (4)+(5) — "Decide + Execute" | `/planning/production-plan`, `/planning/runs/[run_id]/recommendations/[rec_id]` (approve/dismiss/convert) | Keep; add bulk-approve, conversion-trail chips, "Receive against this PO" |
| 5. Configuration | Decision (7) — "Plan ahead" | `/planning/forecast/*`, `/admin/planning-policy`, `/admin/holidays` | Keep; minor polish |

**Out of scope of the daily decision loop:**

- `/planning/production-simulation` — admin-scoped scratch tool.
- `/planning/boms` — admin-scoped BOM scratch tool.
- `/planning/weekly-outlook` — long-horizon view, not daily.

These should either:
1. Be moved under `/admin/` (clear operator separation), OR
2. Stay under `/planning/` but be visually de-emphasized in nav (collapsed group).

### 6.3 Ideal progression

```
visibility (command center)
    ↓
diagnosis (run detail / inventory flow)
    ↓
prioritization (triage queues / blockers / inbox)
    ↓
action (approve / convert / plan / receive)
    ↓
confirmation (post-action toast → audit trail link → freshness chip)
```

Every surface should support exactly one of these phases as its primary job, and link forward to the next phase. Today, this chain is broken in three places:

- **visibility → diagnosis:** Dashboard does not deep-link into the *specific* run or item that drove the alert; it shows aggregate counts.
- **diagnosis → prioritization:** Run-detail exceptions deep-link into wrong admin pages (NV-1, NV-2). Inventory-flow item detail does not surface the recipe.
- **action → confirmation:** Production-actual submit does not deep-link to the posted movement (G-1 in the audit). Convert-to-PO does not deep-link back to the rec row.

### 6.4 What does NOT yet exist (and probably should)

- **A "Today" surface** — what was the last planning run? what plans are in flight today? what was actually produced yesterday vs the plan? what changed in the last 24h? Currently this is split across 4 surfaces.
- **A planning audit trail** — the `change_log` table exists but no surface renders "what did the planning system decide and why" in a planner-readable form.
- **A purchase recommendations digest surface** — runs detail shows recs grouped by ready/blocked but there is no day-of-week purchasing rhythm view.

### 6.5 Architecture rules (to embed in handoff packets)

1. **Single freshness component** (`FreshnessBadge`) on every surface that shows time-sensitive data.
2. **Single role badge component** rendering friendly labels (no raw enum).
3. **Single status-chip vocabulary** for `Planned / Completed / Cancelled / Pending / Approved / Dismissed / Converted / Superseded`.
4. **Mobile-first dialog rule:** modals slide up at <640px (Tom-locked global standard).
5. **Decision-grade info standard:** every decision surface (rec drill-down, run detail, blockers) must show *source + freshness + last-action* for every fact rendered.
6. **No false greens:** if a column / chip / banner depends on data not yet wired, hide it; do not render an "unknown" placeholder that could be mistaken for a true value.
7. **Names not IDs** (already locked in user memory; verify on every surface during handoff).

---

## 7 — Roadmap

Prioritization rule: P0 = decision-grade gap, blocks daily use; P1 = high-frequency friction or architectural fragmentation; P2 = polish; Def = blocked by Window B or product decision.

### P0 — Highest leverage, safest now

| ID | Work item | Surface(s) | Effort | Backend? | Window B? | Owner lane | First-tranche candidate |
|---|---|---|---|---|---|---|---|
| **R0-1** | Graduate Dashboard v2; deprecate v1 OR fold v2 into v1 | `/dashboard*` | 2-3 days | no (uses live read-models) | no | portal | **YES** |
| **R0-2** | Add planning quick-actions to dashboard (was P0-B in audit; cycle 4 partial — verify) | `/dashboard` | 0.5 day | no | no | portal | **YES** |
| **R0-3** | Add "Last 24h activity" tile to dashboard | `/dashboard` | 1 day portal + 1-2 days backend | yes (new read-model) | no | backend-db + portal | **YES** |
| **R0-4** | Decide P0-D PO-detail Hebrew banner (Tom decision POGR-2) | `/(po)/purchase-orders/[po_id]` | 0.5 day after Tom decision | no | no | portal | yes if Tom decides this run |
| **R0-5** | Decide P0-G production-simulation IDB false-green (Tom decisions PSDP-1..4) | `/planning/production-simulation` | depends on Tom decision | depends | partial | portal + maybe backend | yes if Tom decides this run |

### P1 — Important next

| ID | Work item | Surface(s) | Effort | Backend? | Window B? | Owner lane |
|---|---|---|---|---|---|---|
| R1-1 | Standardize freshness vocabulary on `FreshnessBadge` everywhere | all | 1 day | no | no | portal |
| R1-2 | Standardize role-badge rendering (friendly enum → label) | all | 0.5 day | no | no | portal |
| R1-3 | Run Detail: add `Run sources` freshness timestamps + skeleton on rec card | `/planning/runs/[run_id]` | 0.5 day | no | no | portal |
| R1-4 | Run Detail: render `item_name`/`component_name` on exception rows (regression fix) | `/planning/runs/[run_id]` | 0.5 day | no | no | portal |
| R1-5 | Run Detail: fix exception deep-links (NV-1 components, NV-2 ?tab=bom) | `/planning/runs/[run_id]` | 0.5 day | no | no | portal |
| R1-6 | Recommendation drill-down: stamp lead-time source | `/planning/runs/[run_id]/recommendations/[rec_id]` | 0.5 day | maybe (read-model field) | no | portal (+ maybe backend-db) |
| R1-7 | Recommendation drill-down: hide approve/reject when status ≠ `pending` | same | 0.25 day | no | no | portal |
| R1-8 | Run Detail: render "→ PO 1234" chip on rec row when `converted_to_po_id` set | same | 0.5 day | no | no | portal |
| R1-9 | Bulk-approve "ready_now" production recs (verify cycle 6 closure first) | `/planning/runs/[run_id]` | 0.5-1 day | maybe | no | portal |
| R1-10 | Inventory Flow: legend "Planned production NOT included" (A4 lock honesty) | `/planning/inventory-flow` | 0.25 day | no | no | portal |
| R1-11 | Mobile day-popover: slide-up modal | `/planning/inventory-flow` | 0.25 day | no | no | portal |
| R1-12 | Sidebar nav: add Supply Flow, Weekly Outlook, Dashboard v2 (or fix v2 vs v1) | nav manifest | 0.25 day | no | no | portal |
| R1-13 | "Receive against this PO →" CTA on PO detail | `/(po)/purchase-orders/[po_id]` | 0.5 day | no | no | portal (PO corridor — adjacent) |
| R1-14 | "View posted movement" inline on Production Actual success | `/(ops)/stock/production-actual` | 0.5 day | no | no | portal |
| R1-15 | Dashboard `BreakGlassCard` tone-match | `/dashboard` | 0.25 day | no | no | portal |

### P2 — Later

| ID | Work item | Surface(s) | Owner lane |
|---|---|---|---|
| R2-1 | "Open recipe →" link on inventory-flow item detail | `/planning/inventory-flow/[itemId]` | portal |
| R2-2 | Forecast list: inline `Resume draft` action on draft rows | `/planning/forecast` | portal |
| R2-3 | Inbox: collapse 8 view chips into `<select>` at <640px | `/inbox` | portal |
| R2-4 | Run Detail policy-snapshot accordion: friendly group-by | `/planning/runs/[run_id]` | portal |
| R2-5 | Inventory-flow risk chips: add color-blind variant | `/planning/inventory-flow` | portal |
| R2-6 | Mobile dashboard block-1 stat strip 2x2 grid | `/dashboard` | portal |
| R2-7 | After production-actual: invalidate `["inventory","flow"]` cache | (cross-cache) | portal |
| R2-8 | Forecast list: status-filter friendly labels (instead of raw enum) | `/planning/forecast` | portal |

### Deferred — blocked by Window B or product decision

| ID | Work item | Why deferred |
|---|---|---|
| RD-1 | Re-run planning runs after Window B closes; reconcile open recommendations | Window B BOM verification still in flight |
| RD-2 | Production Simulation graduation (real BOM-walking simulation, not IDB) | Tom decisions PSDP-1..4 + Window B alignment |
| RD-3 | BOM Simulator graduation | project memory: queued post-PO corridor |
| RD-4 | A4 lock revisit — should Inventory Flow include planned production as inflow? | engineering decision; tied to planning-engine v2 |
| RD-5 | Production-Plan in-flight status (operator opened form but didn't submit) | needs backend signal not currently emitted |
| RD-6 | Planning audit trail surface | needs read-model + product decision on what to expose |
| RD-7 | Purchase recommendations digest / weekly purchasing rhythm view | needs design + product decision |
| RD-8 | Forecast → Run → Plan → Actual delta visualization | needs cross-surface read-model |

---

## 8 — Recommended first execution tranche

### 8.1 Tranche T1 — Dashboard graduation + Decision-loop polish

**Scope (1 sprint, ~5-7 working days):**

1. **R0-1** Graduate Dashboard v2 OR fold v2 into v1. Pick one. The split is the single highest-fragmentation issue in the planning corridor.
2. **R0-2** Verify and complete planning quick-actions on the graduated dashboard (`Daily Production Plan`, `Inventory Flow`, `Blockers`, `Production Plan`, `Forecast`, `Runs`). Cycle 4 closed P0-B partially; verify on disk.
3. **R1-1** Standardize freshness vocabulary on `FreshnessBadge` across dashboard + run detail + inventory flow + PO list.
4. **R1-3** Run Detail: add `Run sources` freshness timestamps + skeleton on rec card.
5. **R1-4** Run Detail: render `item_name`/`component_name` on exception rows.
6. **R1-5** Run Detail: fix exception deep-links (NV-1 components, NV-2 ?tab=bom).
7. **R1-7** Recommendation drill-down: hide approve/reject when status ≠ `pending`.
8. **R1-12** Sidebar nav: rationalize entries; surface or hide v2 / Supply Flow / Weekly Outlook / BOM Simulator with consistent rules.

### 8.2 Why this tranche

- **Visible user value:** Dashboard is the planner's first-glance surface every morning. Decision-loop polish removes the rough edges on *exactly* the surfaces a planner walks every day.
- **Operational clarity:** standardizing freshness vocabulary and rec status disabling alone removes a large fraction of "is this true right now?" friction.
- **Safety:** all items in this tranche use already-stable read-models. Window B risk = LOW. Frozen flags = untouched. Backend = touched only if R1-6 (lead-time source) is added (deferred to T2).
- **Low dependency risk:** every item is portal-only or portal + small DTO extension. No schema migration, no integration boundary.
- **Proof of new brain:** this tranche will exercise the Phase 8 Run B agent stack — `ux-flow-architect` (handoff), `interaction-design-specialist` (button rules), `ux-content-state-designer` (microcopy register), `accessibility-usability-auditor` (a11y), and `portal-production-executor` (implementation). Five UX agents → one portal-production-executor. Clean dispatch chain.

### 8.3 What this tranche does NOT touch

- Backend schema changes.
- Frozen flags.
- BOM verification work (Window B).
- Authority docs.
- Production Simulation false-green (P0-G needs Tom decision PSDP-1..4 first — separate tranche).
- PO detail Hebrew banner (P0-D needs Tom decision POGR-2 first — separate tranche).
- New surfaces (no "Today" view, no last-24h tile yet — that comes in T2 or T3 once T1 ships).

### 8.4 Success criteria

T1 ships when:

1. There is exactly **one** dashboard route (`/dashboard`); `/dashboard/v2` either deprecated or merged.
2. `FreshnessBadge` is the only freshness component used on T1-touched surfaces.
3. Audit P1 items A.* (decision-context) for Run Detail and Recommendation drill-down close.
4. Audit P1 items C.* (NV-1, NV-2) close.
5. UX release-gate verdict on touched surfaces is `SHIP` (not `CONDITIONAL_SHIP`).
6. No regression on Inventory Flow, Production Plan, Blockers (FLOW-003 closure preserved).
7. Sidebar nav contains exactly the surfaces a planner is supposed to use; the rest are either under `/admin/` or hidden.

### 8.5 Dependencies

- Tom approval of this masterplan (this run produces the proposal).
- Tom decision on R0-1: graduate v2 vs fold into v1. **This is the single most important decision in T1.** A draft recommendation is below.
- All 5 UX agents available for handoff packet authoring.
- `portal-production-executor` available with Tom-approved Hebrew register entries (none expected in T1 — all surfaces are English-locked except Blockers which is already Tom-locked).
- No collision with Window B (Window B is backend; this tranche is portal-only).
- No collision with Sunday 2026-05-10 cutover (T1 should land **before or after**, not during).

### 8.6 Draft recommendation on R0-1 (graduate v2 vs fold)

**Recommendation: graduate `/dashboard/v2` content into `/dashboard`, then deprecate `/dashboard/v2`.**

Rationale:

- v2 was authored as MVP; per `CURRENT_STATE.md` 7 of 8 sub-blocks render placeholder cards.
- v1 has the established URL, the existing Quick Actions launcher, and existing operator habit.
- Folding v2 *content* (Critical Today block, Slipped Plans block) into the v1 layout preserves operator memory and fixes both surfaces in one move.
- The alternative (graduate v2, redirect v1 → v2) would require Tom-approved nav reshuffling and likely surfaces stale links across docs.

This is a draft recommendation. **Tom decides.**

---

## 9 — Tranches that follow T1

### Tranche T2 — Decision-context completeness

Closes the "show source / show freshness / show what this means" gaps. Surfaces touched: Run Detail (more), Recommendation drill-down, Inventory Flow, Production Actual.

Scope (~5-7 days):
- R1-6 lead-time source stamp (small backend extension).
- R1-8 "→ PO 1234" chip after convert-to-PO.
- R1-9 bulk-approve verification + completion.
- R1-10 Inventory Flow A4-lock legend honesty.
- R1-13 "Receive against this PO →" CTA.
- R1-14 "View posted movement" inline link on Production Actual success.
- DF-4 "what this means" explainer when 0 recs + N exceptions.

Window B risk: LOW (no BOM-walking changes). Backend touched: minimal (one DTO extension for lead-time source).

### Tranche T3 — Operating-rhythm surface ("Today" view)

After T1 + T2 ship and Window B closes (or its impact is bounded), introduce a single new operational-rhythm surface aggregating:

- Critical Today (already wired)
- Slipped Plans (already wired)
- Open Blockers count
- Latest Planning Run summary (recs + exceptions)
- Last 24h activity (R0-3)
- Today's plan vs actual delta

This is the OR-1 problem and the "What does NOT yet exist" gap from §6.4. It would replace the current bare `/planning` overview page with operational content, OR live as a new `/today` route, OR be the new home dashboard. Tom decides between those three placements before T3 starts.

Window B risk: LOW. Backend: 1-2 new read-model views.

### Tranche T4 — Mobile + a11y polish

All mobile + a11y P1/P2 items in §5.5–5.7. One coordinated polish pass.

Window B risk: NONE. Backend: NONE.

### Tranche T5 — Simulator surface fate

After T1-T4 ship and Window B closes, address Production Simulation (P0-G) and BOM Simulator (DT-3). Either graduate to live BOM-walking or move under `/admin/` with explicit "scratch tool" labeling.

Window B risk: HIGH (these surfaces are the most BOM-coupled).

---

## 10 — What this run did NOT do

- Did not change any portal source.
- Did not change any backend.
- Did not change any authority doc.
- Did not change `portal_ux_standard.md` or `portal_language_direction_audit.md`.
- Did not push any branch.
- Did not flip any frozen flag.
- Did not run any pgTAP, did not connect to any DB.
- Did not run any UX agent (existing audits were sufficient).
- Did not attempt to resolve P0-D (Tom decision POGR-2 required).
- Did not attempt to resolve P0-G (Tom decisions PSDP-1..4 required).
- Did not produce the second optional doc (`PLANNING_PROBLEM_REGISTER.md`); the register is embedded in §5 of this masterplan because keeping a single source-of-truth simplifies handoff and there is no operational benefit to splitting.

---

## 11 — Handoff

### 11.1 If Tom approves this masterplan as-is

Next dispatch (T1 kickoff): handoff packets for the 8 work items in §8.1, in order:

1. `ux-flow-architect` produces flow-handoff for the dashboard graduation (R0-1).
2. `visual-system-designer` produces visual-handoff for the freshness vocabulary standardization (R1-1).
3. `interaction-design-specialist` produces interaction-handoff for sidebar nav rationalization (R1-12) and exception-row deep-link fixes (R1-5).
4. `ux-content-state-designer` produces copy-handoff for any new microcopy needed.
5. `accessibility-usability-auditor` produces a11y-handoff for the touched surfaces.
6. `portal-production-executor` (or legacy `executor-w2`) implements per the packets.
7. `release-verifier` runs `/ux-release-gate` on touched surfaces; emits `SHIP` verdict for T1 close.

### 11.2 If Tom wants changes

Reply with the change. The masterplan is intentionally a **branch** + a single doc — nothing else changed in this run. Iterating is cheap.

### 11.3 If Tom wants a different first tranche

The candidates that did NOT win the recommendation but are tractable alternatives:

- **T1-alt-A**: Decision-context completeness (T2 above) — start with the Run Detail / Recommendation drill-down hardening instead of dashboard. Pro: directly attacks the planner's decision moment. Con: dashboard fragmentation persists.
- **T1-alt-B**: Mobile + a11y polish (T4 above). Pro: lowest risk, broadest coverage. Con: lowest visible operational value.
- **T1-alt-C**: New "Today" surface (T3 above). Pro: highest visible operational value. Con: highest risk; requires new read-model + Window B closure for full credibility.

---

## 12 — Closing notes

The planning corridor is in solid shape after Phase 8 Run C. Most P0 audit findings are closed. The remaining work is a P1-polish + architectural-consolidation phase, not a rebuild.

The single highest-leverage move right now is **graduating the dashboard split** — because it is the one surface every planner reads first, every day. Everything else in T1 is the polish chain that connects the dashboard to the surfaces it points to.

After T1, the system has earned the right to invest in T3's "Today" surface — a new operational-rhythm view. Before T1, that investment would just add a 20th planning surface to a system that already has 19.

**Branch:** `planning-masterplan-2026-05-08`
**Commit (this run):** to follow this file write
**Push:** **NO — Tom only**
**Authority:** advisory; awaiting Tom approval for T1 execution.
