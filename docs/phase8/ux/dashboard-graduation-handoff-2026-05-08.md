# Dashboard Graduation -- UX Flow Handoff Packet
## R0-1 / R0-2 / R1-12 -- Planning Screens T1 Tranche

**Status:** READY_FOR_IMPLEMENTATION
**Authored by:** ux-flow-architect
**Date:** 2026-05-08
**Masterplan ref:** PRODUCTION/docs/planning/PLANNING_SCREENS_UPGRADE_MASTERPLAN.md S8 (T1)
**Portal tip at audit:** 9e2212e (window2-portal-sandbox main)
**Authority hierarchy:** CLAUDE.md > EXECUTION_POLICY.md > CURRENT_STATE.md > this packet

---

## Section 1 -- Status and authority

**Packet ownership:** ux-flow-architect (read-only authoring). Implementation ownership: portal-production-executor.

**Authority hierarchy for this packet:**
1. CLAUDE.md locked decisions win on every conflict.
2. EXECUTION_POLICY.md governs lane permissions and approval gates.
3. CURRENT_STATE.md is sole authority on live gate status and corridor state.
4. PLANNING_SCREENS_UPGRADE_MASTERPLAN.md S8 defines T1 scope -- this packet is downstream of that doc and does not widen or narrow scope without Tom authorization.
5. This packet is advisory to the implementer -- it is not a locked decision.

**Tom approval status:** Tom approved the masterplan including R0-1 graduation direction on 2026-05-08. This packet operationalizes that approval into an implementable specification.

**Expiry / closure rule:** This packet is superseded when portal-production-executor lands the implementation and release-verifier emits a RUNTIME_READY signal for the graduated dashboard.

**Tranche containment:** This packet covers R0-1, R0-2, R1-12 only. R1-1, R1-3, R1-4, R1-5, R1-7 are in the visual-system-designer parallel packet.

---

## Section 2 -- Tom decision recap

Verbatim from dispatch prompt (controlling authority for this packet):

> Graduate /dashboard/v2 content into /dashboard as the canonical planning dashboard, then deprecate /dashboard/v2 via redirect or clearly documented legacy removal path. Do NOT fold v2 backward into the old dashboard model.

Constraints:
- Direction-of-travel: v2 content forward into v1 URL. Not v1 patterns backward into v2.
- Masterplan S8.6 draft recommendation (graduate v2 content into v1 layout, preserve v1 URL, deprecate v2) is confirmed by Tom decision.
- /dashboard/v2 becomes a Next.js permanent redirect to /dashboard OR is removed entirely. Tom has open question on which (Section 15).

---

## Section 3 -- Current-state evidence (disk, 2026-05-08)

### 3.1 /dashboard (v1) -- src/app/(shared)/dashboard/page.tsx

File: 889 lines. use client. Header comment: Merged: Dashboard overview + Control Tower (v2) -- Dark-mode operational command center.

**Block inventory (current v1 on disk):**

| Block | Component | Data source | State |
|---|---|---|---|
| RM Inventory Value | ValueCard | /api/stock/value | LIVE, skeleton on load |
| FG Inventory Value | ValueCard | /api/stock/value | LIVE, skeleton on load |
| Stock Health Donut | StockDonut | useInventoryFlow hook | LIVE, skeleton on load |
| Exceptions count | ExceptionsCard | /api/exceptions?status=OPEN | LIVE, skeleton on load |
| Shortage Risk | ShortageRisk | useInventoryFlow hook | LIVE, top-6 items linked to inventory-flow item detail |
| Planning Run | PlanningCard | /api/planning/runs?status=completed&limit=1 | LIVE -- NO deep-link to the run |
| Production this week | ProductionWeek | /api/production-plan weekly window | LIVE |
| Recent production | RecentProduction | /api/production-actuals/history?limit=5 | LIVE -- NO movement log link |
| Critical Today | CriticalTodaySection | /api/dashboard/critical-today | LIVE -- conditional render (hides on loading/error/no-data) |
| Slipped Plans | SlippedPlansSection | /api/dashboard/slipped-plans | LIVE -- conditional render (hides on loading/error/no rows) |

**CRITICAL FINDING -- Quick Actions launcher ABSENT (FLOW-DG-001):** page.tsx has no import of QUICK_ACTIONS, QuickAction, or any launcher component from quick-actions.ts. The launcher is fully defined but not rendered.

**CRITICAL FINDING -- Break-glass banner ABSENT (FLOW-DG-002):** page.tsx has no /api/system/break-glass call and no banner component.

**Header:** Custom inline header (lines 819-839). Does NOT use WorkflowHeader. All styling via local design token object C with inline style objects.

**Navigation:** /dashboard IS in nav manifest (Overview group, min_role: viewer, viewer:read).

---

### 3.2 /dashboard/v2 -- src/app/(shared)/dashboard/v2/page.tsx

File: 852 lines. use client. Full file comment documents tranche authorization and RUNTIME_READY signals consumed.

**Live blocks:**
- S4.1 Critical Today (CriticalTodayBlock): LIVE. /api/dashboard/critical-today. Full loading/error/empty/loaded states. Error has Retry button. Empty state tone=success All clear. Footer with fmtRelative(asOf, now) freshness. Detail hints extracted from detail_jsonb per trigger_kind. Accessible markup (role=dialog, aria-).
- S4.4 Slipped Plans (SlippedPlansBlock): LIVE. /api/dashboard/slipped-plans. Same full state hygiene. Footer with source view name + window_days + freshness.

**Placeholder blocks (7, collapsed by default since P1-1 closure):**
S4.2 This-week FG stock risk, S4.3 This-week planned production, S4.5 Open POs due this week, S4.6 Blocked production, S4.7 Blocked purchase, S4.8 Integration freshness, S4.9 Top-5 exceptions. All show honest Coming next / Awaiting read-model state. Default-collapsed. Correct pattern.

**Quick Actions (v2 inline, 4 entries only):**
- /planning/runs -- Run planning -- capability: planning:execute
- /planning/production-plan -- Production plan -- capability: planning:read
- /exceptions -- Exceptions -- capability: viewer:read
- /inbox -- Inbox -- capability: viewer:read

This is smaller and different from quick-actions.ts. Does NOT include Inventory Flow, Blockers, Forecast, Goods Receipt, Physical Count, Production Actual, Purchase Orders.

**Break-glass banner:** PRESENT and live. Reads /api/system/break-glass. Correct DCT2-2 dual-surface pattern.

**WorkflowHeader:** eyebrow Control tower v2, title Control tower, description Morning view -- what needs your attention today. Meta badges: v2 - partial coverage and 2 live blocks - 7 awaiting read-model. Actions slot: Back to v1 dashboard link.

**SectionCard:** Used for each block. Consistent pattern.

**Cache keys:** Namespaced as [dashboard-v2, ...] to avoid collision with v1.

**Navigation:** /dashboard/v2 is NOT in nav manifest. Reachable only by direct URL.

---

### 3.3 Quick Actions launcher -- src/features/dashboard/quick-actions.ts

File: 191 lines. QUICK_ACTIONS array (17 entries).

**Full entry inventory:**

| Label | href | category | capability |
|---|---|---|---|
| Open Inbox | /inbox | triage | viewer:read |
| Goods Receipt | /stock/receipts | stock | stock:execute |
| Waste / Adjustment | /stock/waste-adjustments | stock | stock:execute |
| Physical Count | /stock/physical-count | stock | stock:execute |
| Production Actual | /stock/production-actual | stock | stock:execute |
| Forecast | /planning/forecast | planning | planning:read |
| Planning Runs | /planning/runs | planning | planning:read |
| Daily production plan | /planning/production-plan | planning | planning:read |
| Inventory flow | /planning/inventory-flow | planning | planning:read |
| Blockers | /planning/blockers | planning | planning:read |
| BOM Simulation | /planning/boms | planning | planning:read -- WRONG, see FLOW-DG-004 |
| Purchase Orders | /purchase-orders | planning | viewer:read |
| Items | /admin/items | admin | admin:execute |
| Components | /admin/components | admin | admin:execute |
| BOMs | /admin/masters/boms | admin | admin:execute |
| Suppliers | /admin/suppliers | admin | admin:execute |
| Jobs | /admin/jobs | admin | admin:execute |

**Audit P0-B closure verification:** The three audit-missing surfaces (Daily Production Plan line 112, Inventory Flow line 119, Blockers line 126) ARE present. Data-file closure confirmed. BUT: /dashboard/page.tsx does not import or use this file. The rendering gap is the live problem (FLOW-DG-001).

---

### 3.4 Nav manifest -- src/lib/nav/manifest.ts

File: 378 lines. Typed, capability-aware.

**Current Planning group entries:**
- /planning -- Planning Overview -- planning:read
- /planning/forecast -- Forecast -- planning:read
- /planning/runs -- Run History -- planning:read
- /planning/production-plan -- Daily Production Plan -- planning:read
- /planning/production-simulation -- Production Simulation -- admin:execute (correctly gated)
- /planning/inventory-flow -- Inventory Flow -- planning:read
- /planning/blockers -- Blockers -- planning:read

**Confirmed orphans (live routes absent from manifest):**
1. /dashboard/v2 -- not in manifest (by design, deprecated by graduation)
2. /planning/boms -- not in manifest (confirmed on disk: src/app/(planning)/planning/boms/page.tsx)
3. /planning/weekly-outlook -- not in manifest (confirmed on disk: src/app/(planning)/planning/weekly-outlook/page.tsx; CURRENT_STATE.md references prior add in commit 81d6c7f that did not survive to portal tip 9e2212e)
4. /planning/inventory-flow/supply -- not in manifest (confirmed on disk: src/app/(planning)/planning/inventory-flow/supply/page.tsx)

---

## Section 4 -- Target end-state after T1

### 4.1 /dashboard -- canonical, single source

**Above-the-fold block order (planner-critical):**
1. Header (WorkflowHeader, no partial-coverage badges)
2. Break-glass banner (conditional -- hidden if inactive)
3. Quick Actions launcher (role-filtered from quick-actions.ts)
4. Critical Today block (v2 CriticalTodayBlock implementation)
5. Slipped Plans block (v2 SlippedPlansBlock implementation -- hides if zero rows)

**Below-the-fold blocks (contextual):**
6. RM Inventory Value + FG Inventory Value (ValueCard pair)
7. Stock Health Donut (inventory-flow hook)
8. Exceptions count (ExceptionsCard -- add Open inbox link per FLOW-DG-007)
9. Shortage Risk (items already link to inventory-flow item detail)
10. Planning Run (PlanningCard -- add Open run link per FLOW-DG-005)
11. Production this week (ProductionWeek)
12. Recent production actuals (RecentProduction -- add View movement log link per FLOW-DG-006)
13. Critical Today + Slipped Plans -- both replaced with v2 implementations, not v1

The 7 placeholder blocks from v2 do NOT migrate. Deferred to T2/T3.

**Header spec:**
- Component: WorkflowHeader (matching v2 pattern)
- eyebrow: Control tower
- title: Dashboard
- description: What needs your attention today.
- meta badges: NONE (remove v2 - partial coverage and 2 live blocks - 7 awaiting read-model)
- actions slot: NONE (remove Back to v1 dashboard link)
- Retain Live - date indicator in meta slot

### 4.2 /dashboard/v2 -- deprecated

Route becomes a Next.js permanent redirect to /dashboard. HTTP 308 recommended (see Section 15 Q1). After graduation, /dashboard/v2 navigates transparently to /dashboard.

---

## Section 5 -- Block-by-block migration plan

### v1 blocks -- all KEEP

| v1 Block | Decision | Action required |
|---|---|---|
| RM Inventory Value | KEEP | No change |
| FG Inventory Value | KEEP | No change |
| Stock Health Donut | KEEP | No change |
| Exceptions count | KEEP + ENHANCE | Add Open inbox link (FLOW-DG-007) |
| Shortage Risk | KEEP | No change (already has item deep-links) |
| Planning Run | KEEP + ENHANCE | Add Open run link when run_id present (FLOW-DG-005) |
| Production this week | KEEP | No change |
| Recent production | KEEP + ENHANCE | Add View movement log footer link (FLOW-DG-006) |
| Critical Today (v1 CriticalTodaySection) | REPLACE with v2 CriticalTodayBlock | v2 has superior state hygiene, retry, detail hints, accessible markup, SectionCard |
| Slipped Plans (v1 SlippedPlansSection) | REPLACE with v2 SlippedPlansBlock | Same reasoning |

### v2 blocks -- migration decisions

| v2 Block | Decision | Justification |
|---|---|---|
| Break-glass banner | MERGE-FROM-V2 | v1 lacks this. Required for DCT2-2 dual-surface pattern. |
| Critical Today (CriticalTodayBlock) | MERGE-FROM-V2 replaces v1 version | Full state hygiene, retry, detail hints, a11y |
| Slipped Plans (SlippedPlansBlock) | MERGE-FROM-V2 replaces v1 version | Same |
| Quick Actions (v2 inline 4-entry) | DROP | Canonical source is quick-actions.ts. v2 inline set is a subset. |
| S4.2 to S4.9 placeholder blocks (7) | DEFER to T2/T3 | Read-models do not exist. Graduated dashboard must not show placeholder content. |
| WorkflowHeader | MERGE-FROM-V2 | Graduated dashboard uses WorkflowHeader. |
| SectionCard wrapper | MERGE-FROM-V2 for Critical Today + Slipped Plans | Other v1 blocks may retain existing card styling. |
| dashboard-v2 cache key namespace | DROP | Post-graduation canonical keys are [dashboard, critical-today] and [dashboard, slipped-plans]. |
| v2 - partial coverage meta badges | DROP | False after graduation. |
| Back to v1 dashboard actions link | DROP | v1 IS the dashboard after graduation. |
| eyebrow Control tower v2 | CHANGE to Control tower | Graduation removes v2 label. |

---

## Section 6 -- Quick Actions launcher (R0-2) plan

### 6.1 Audit finding verification

Original P0-B (audit 2026-05-01 S11-B): Quick Actions missing Daily Production Plan, Inventory Flow, Blockers.
Cycle 4 closure claimed in CURRENT_STATE.md line 133.

Disk verification 2026-05-08:
- quick-actions.ts DOES contain Daily Production Plan (line 112), Inventory Flow (line 119), Blockers (line 126). Data-file closure confirmed.
- /dashboard/page.tsx does NOT import or render any component consuming QUICK_ACTIONS. No import of QuickAction, QUICK_ACTIONS, or any launcher component anywhere in the file.

Conclusion: Cycle 4 closed the data-file gap. The rendering gap was introduced when the dark-mode rewrite replaced the prior page that did render the launcher. P0-B/P0-F is NOT fully closed. R0-2 is the rendering gap fix.

### 6.2 Target Quick Actions configuration

Render QUICK_ACTIONS from src/features/dashboard/quick-actions.ts, filtered by authorizeCapability(role, entry.required). No new entries needed for T1.

The 6 planning surfaces required by masterplan S8.1 are already present:

| Surface | In quick-actions.ts? |
|---|---|
| Daily Production Plan | YES (line 112) |
| Inventory Flow | YES (line 119) |
| Blockers | YES (line 126) |
| Forecast | YES (line 97) |
| Planning Runs | YES (line 104) |
| Purchase Orders | YES (line 144 via viewer:read) |

### 6.3 BOM Simulation capability fix (FLOW-DG-004)

Required single-entry change in quick-actions.ts (lines 136-141):

BEFORE:
  href: /planning/boms
  label: BOM Simulation
  required: planning:read
  category: planning

AFTER:
  href: /planning/boms
  label: BOM Simulation
  required: admin:execute
  category: admin

Both required AND category must change. The category field controls tile grouping if the launcher renders by category.

Rationale: BOM Simulator is IDB-backed (masterplan S5.1 DT-3). A planner using it for material coverage decisions may make incorrect purchasing or production decisions. Same rationale as the admin:execute gate already on /planning/production-simulation in the manifest (lines 218-229 of manifest.ts).

### 6.4 Out of scope for R0-2

- Do NOT add /planning/weekly-outlook to quick-actions.ts (long-horizon overview, not daily action).
- Do NOT add /planning/inventory-flow/supply to quick-actions.ts (diagnosis surface, nav fate in Section 7).
- Do NOT add new entries not already in the array.

---

## Section 7 -- Sidebar nav rationalization (R1-12) plan

### 7.1 /dashboard/v2 -- disposition

Not in manifest. Deprecated by graduation. No manifest entry needed.
Action: none required in manifest.

### 7.2 /planning/boms (BOM Simulator)

Current state: not in manifest. Reachable by direct URL and (incorrectly) via Quick Actions at planning:read.
Disposition: add to Admin group with admin:execute gate.

Entry to add (Admin group, after /admin/masters/boms):

  href: /planning/boms
  label: BOM Simulator
  icon: Network (already imported -- same icon as /planning/production-simulation for simulation tool family)
  min_role: admin
  required_capability: admin:execute

### 7.3 /planning/weekly-outlook (Weekly Outlook)

Current state: route exists on disk. Not in manifest at portal tip 9e2212e. CURRENT_STATE.md references prior add in commit 81d6c7f that did not survive to current tip.
Nature: long-horizon planner overview surface per masterplan S6.2 Out of scope of daily decision loop.
Disposition: add to Planning group at planning:read, placed after /planning/blockers. Subject to Tom Q2 confirmation (Section 15).

Entry to add (Planning group, after /planning/blockers, before /planning/production-simulation):

  href: /planning/weekly-outlook
  label: Weekly Outlook
  icon: CalendarDays (already imported)
  min_role: viewer
  required_capability: planning:read

Prerequisite: implementer spot-checks /planning/weekly-outlook/page.tsx before adding. If content is an EmptyState or coming-soon stub, use min_role: admin until content lands.

### 7.4 /planning/inventory-flow/supply (Supply Flow)

Current state: route exists on disk. Not in manifest.
Nature: component/RM view of the inventory-flow model. FG inventory flow is in nav; its RM counterpart is not. These are companion views.
Disposition: add to Planning group immediately after /planning/inventory-flow.

Entry to add (Planning group, immediately after /planning/inventory-flow):

  href: /planning/inventory-flow/supply
  label: Supply Flow
  icon: Package (already imported -- represents components/RM)
  min_role: viewer
  required_capability: planning:read

Note on icon: Package is also used in Admin group for /admin/items. The visual collision is acceptable because the groups are visually separated and planner-role users do not see Admin group entries. Visual-system-designer can address icon cross-group consistency in their parallel packet.

Prerequisite: implementer spot-checks /planning/inventory-flow/supply/page.tsx before adding.

### 7.5 Target Planning group after T1

Full Planning group after R1-12 changes (additions marked):

  /planning                          -- Planning Overview       -- viewer  planning:read
  /planning/forecast                 -- Forecast               -- viewer  planning:read
  /planning/runs                     -- Run History             -- viewer  planning:read
  /planning/production-plan          -- Daily Production Plan   -- viewer  planning:read
  /planning/inventory-flow           -- Inventory Flow          -- viewer  planning:read
  [ADD] /planning/inventory-flow/supply -- Supply Flow          -- viewer  planning:read
  /planning/blockers                 -- Blockers               -- viewer  planning:read
  [ADD] /planning/weekly-outlook     -- Weekly Outlook          -- viewer  planning:read
  /planning/production-simulation    -- Production Simulation   -- admin   admin:execute (unchanged)

Admin group additions (after /admin/masters/boms):
  [ADD] /planning/boms               -- BOM Simulator           -- admin   admin:execute

No entries removed. No groups restructured.

### 7.6 Consistent rule (embed as manifest comment)

Add this comment block to manifest.ts above the production-simulation entry in Planning group:

// Daily-decision surfaces (Forecast, Run History, Daily Production Plan, Inventory Flow,
// Supply Flow, Blockers) use min_role: viewer + planning:read. Long-horizon overview
// surfaces (Weekly Outlook) also use planning:read but are positioned after the
// daily-critical surfaces. Scratch / simulation tools with false-data risk (Production
// Simulation, BOM Simulator) use min_role: admin + admin:execute and live in Admin group.

---

## Section 8 -- Operational flow checks (jobs-to-be-done)

Per masterplan S6.1, seven jobs-to-be-done must be supportable from the graduated dashboard.

| JTB | Description | Status after T1 | Gap |
|---|---|---|---|
| JTB-1 First-glance scan | Critical Today (stockout/fail-hard/integration-stale/break-glass), Slipped Plans, break-glass banner | SUPPORTED | v1 CriticalTodaySection weaker than v2 -- replace per Section 5 |
| JTB-2 Triage | Quick Actions (Blockers, Inbox), ExceptionsCard with inbox link | SUPPORTED once FLOW-DG-001 and FLOW-DG-007 fixed | Rendering gap is T1 deliverable |
| JTB-3 Diagnose | ShortageRisk links to inventory-flow item detail; PlanningCard needs run deep-link | PARTIAL | PlanningCard missing run deep-link (FLOW-DG-005) |
| JTB-4 Decide | Quick Actions (Planning Runs, Blockers, Inbox) | SUPPORTED once FLOW-DG-001 fixed | Same rendering gap |
| JTB-5 Execute | Quick Actions (Daily Production Plan, Planning Runs) | SUPPORTED once FLOW-DG-001 fixed | Same |
| JTB-6 Confirm | RecentProduction shows last 5 actuals; add movement log link | PARTIAL | No movement log link (FLOW-DG-006) |
| JTB-7 Plan ahead | Quick Actions (Forecast, Planning Runs) | SUPPORTED once FLOW-DG-001 fixed | Same |

All 7 JTBs are fully supportable after T1 findings are fixed.

---

## Section 9 -- Mobile / responsive notes

Visual-system-designer owns token standardization. These are structural observations only.

9.1 Block order on mobile: The above-the-fold blocks (break-glass, quick-actions, Critical Today, Slipped Plans) must appear ABOVE the KPI stat strip in DOM order. The stat strip (4 ValueCard/StockDonut/ExceptionsCard) stacks vertically at 390px with current grid-cols-4. Do not place the stat strip above Critical Today. The 2x2 grid improvement (R2-6) is P2 deferred.

9.2 Quick Actions at mobile: Use horizontal-scroll overflow-x-auto row at <640px, wrapping grid at >=640px. Matching v2 pattern (v2/page.tsx line 715). Prevents tile-wall problem noted in masterplan S5.5 IH-2.

9.3 Freshness in SectionCard footer: v2 uses fmtRelative(asOf, now) in the SectionCard footer slot. This is the correct pattern. Do NOT introduce FreshnessBadge component imports in this T1 pass -- FreshnessBadge standardization (R1-1) is owned by the visual-system-designer parallel packet. Use the existing footer text pattern from v2 verbatim.

---

## Section 10 -- Forbidden patterns and hard constraints

1. Do NOT remove or change break-glass banner copy. Preserve verbatim from v2.
2. Do NOT change /planning/blockers route, page content, or nav entry. Hebrew Tom-locked.
3. Do NOT change permission gating on any route except BOM Simulation required field in quick-actions.ts.
4. Do NOT touch BOM Simulation page internals (/planning/boms/page.tsx). Deferred to T5.
5. Do NOT add new backend endpoints. All dashboard endpoints are already live.
6. Do NOT invent new API fields. All fields consumed are in existing contracts.
7. Do NOT delete src/features/dashboard/quick-actions.ts.
8. Do NOT touch frozen flags (LIONWHEEL_FG_OUT_BRIDGE_ENABLED, SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED).
9. Do NOT git push. Commit only. Tom pushes per EXECUTION_POLICY.md.
10. Do NOT change portal_ux_standard.md.
11. Do NOT add Hebrew copy. All new labels must be English. ux-content-state-designer owns copy.
12. Do NOT migrate the 7 placeholder blocks (S4.2-S4.9) from v2. Deferred.
13. FLOW-003 closure must be preserved. Do not alter /planning/blockers nav entry or quick-actions entry.
14. Do NOT use v1 CriticalTodaySection or SlippedPlansSection in the graduated dashboard. Replace with v2 versions.
15. Do NOT use the v2 inline QUICK_ACTIONS (4-entry array in v2/page.tsx). Use quick-actions.ts as canonical source.

---

## Section 11 -- Files expected to be touched

### Primary changes

| File | Change type | What changes |
|---|---|---|
| src/app/(shared)/dashboard/page.tsx | MAJOR REWRITE | Graduated dashboard. Adds break-glass, Quick Actions, v2 CriticalTodayBlock and SlippedPlansBlock, WorkflowHeader, SectionCard. Retains 9 v1 data blocks. Adds Open run link on PlanningCard, View movement log on RecentProduction, Open inbox link on ExceptionsCard. |
| src/app/(shared)/dashboard/v2/page.tsx | REPLACE with redirect | Replace entire content with Next.js server component redirect(/dashboard) permanent 308. |
| src/features/dashboard/quick-actions.ts | SINGLE ENTRY EDIT | BOM Simulation: required from planning:read to admin:execute, category from planning to admin. |
| src/lib/nav/manifest.ts | ADD 3 ENTRIES + COMMENT | Add Supply Flow (after /planning/inventory-flow), Weekly Outlook (after /planning/blockers), BOM Simulator (Admin group after /admin/masters/boms). Add consistency comment above production-simulation entry. |

### Secondary / conditional

| File | Change type | Condition |
|---|---|---|
| src/app/(shared)/dashboard/v2/layout.tsx | CHECK | If exists, verify it does not need cleanup after redirect. |
| Any component used ONLY by v2/page.tsx | OPTIONAL DELETE | If orphaned after redirect. Do not delete shared components (SectionCard, WorkflowHeader). |

### No changes expected

Any file under src/app/(planning)/, src/app/(ops)/, src/app/(po)/. Any API route. Any backend file. portal_ux_standard.md. Any auth file.

---

## Section 12 -- Out of scope (explicit)

### Covered by visual-system-designer parallel packet
R1-1 (FreshnessBadge standardization), R1-3 (Run Detail sources timestamps), R1-4 (Run Detail exception row names), R1-5 (Run Detail exception deep-link fixes), R1-7 (Rec drill-down status-aware buttons).

### Deferred to later tranches
R0-3 Dashboard Last 24h activity tile (T2/T3 -- needs new read-model). P0-D PO detail Hebrew banner (Tom decision POGR-2). P0-G production-simulation IDB false-green (Tom decisions PSDP-1..4). S4.2-S4.9 placeholder blocks (T2/T3). Mobile 2x2 stat strip R2-6 (T4). Mobile inventory-flow day popover R1-11 (T4). BOM Simulator page internals (T5). Planning overview replacement (T3). Production-actual cache invalidation R2-7 (T2). Run Detail bulk-approve R1-9 (T2 verification needed).

### Separate corridors
R1-13 Receive against this PO CTA (PO corridor). R1-14 View posted movement link (Production Actual corridor). R1-2 Role badge rendering (system-wide pass).
---

---

## Section 13 -- Verification gates

### 13.1 Automated checks

1. pnpm typecheck exits 0 on all changed files.
2. CI lint guard scripts/check-no-persona-in-urls.mjs passes.
3. src/app/(shared)/dashboard/v2/page.tsx is a server component with redirect() only.
4. quick-actions.ts BOM Simulation entry has required: admin:execute and category: admin.
5. Nav manifest Planning group contains /planning/inventory-flow/supply and /planning/weekly-outlook.
6. Nav manifest Admin group contains /planning/boms with required_capability: admin:execute.
7. Nav manifest does NOT contain entry for /dashboard/v2.

### 13.2 Manual browser walkthrough (planner session)

Check 1 -- Graduated dashboard renders at /dashboard: Header shows eyebrow Control tower, title Dashboard. No partial-coverage or N-live-blocks badges. Break-glass banner absent (inactive env). Quick Actions row visible with: Open Inbox, Forecast, Planning Runs, Daily production plan, Inventory flow, Blockers, Purchase Orders. BOM Simulation tile NOT visible. Critical Today renders (skeleton then All clear or alert rows). Slipped Plans renders (skeleton then empty or slip rows). All 9 data blocks render without errors. ExceptionsCard has Open inbox link. PlanningCard has Open run link when completed run exists. RecentProduction has View movement log footer link.

Check 2 -- No partial-coverage badges on /dashboard.

Check 3 -- v2 redirect: navigate to /dashboard/v2. Browser redirects to /dashboard. URL shows /dashboard. No 404.

Check 4 -- FLOW-003 regression: click Blockers in Quick Actions. Navigates to /planning/blockers. Page renders. Hebrew content expected (Tom-locked).

Check 5 -- Nav entries: Planning group contains Supply Flow and Weekly Outlook. Admin group (expand) contains BOM Simulator. BOM Simulator NOT visible to planner session.

Check 6 -- Admin session Quick Actions: BOM Simulation tile present. Planner session: absent.

Check 7 -- Break-glass active (if testable): warning banner appears above Quick Actions. Links to /admin/integrations#break-glass.

### 13.3 /ux-release-gate inputs

Route scope: /dashboard (full 7-dimension audit), /dashboard/v2 (redirect verify only), /planning/blockers (regression check only).
Target verdict: SHIP or CONDITIONAL_SHIP with named P1 items. Any remaining DECISION_GRADE finding = HOLD.

---

## Section 14 -- Collision risk

14.1 Window B: NONE. Dashboard consumes only stable views (v_critical_today migration 0117, v_production_plan_slippage migration 0118). No contact with BOM-walking migrations 0156-0174.

14.2 FLOW-003: LOW risk. FLOW-003 fix (9e2212e) changed files under planning/blockers/. This packet touches (shared)/dashboard/, features/dashboard/, lib/nav/manifest.ts. No file overlap. Check 4 in Section 13.2 is explicit regression gate.

14.3 Sunday 2026-05-10 cutover: TIMING RISK. T1 should land BEFORE Sunday (Thu/Fri 2026-05-08/09) OR AFTER (Mon 2026-05-11). Do NOT land on Sunday during active cutover window. Tom confirms timing.

14.4 Shopify External Boundary v2: NONE. Dashboard does not call Shopify endpoints.

14.5 Simultaneous portal lanes: NONE expected. Visual-system-designer parallel packet touches planning/runs/** -- no file overlap with this packet. Use separate commits if both packets land in same session.

---

## Section 15 -- Open questions for Tom

### Q1 -- HTTP redirect type for /dashboard/v2

Option A (recommended): 308 permanent redirect. Correct semantic for a graduation decision. Browser and CDN cache it. Rollback requires restoring v2/page.tsx from git history.
Option B: 307 temporary redirect. Keeps rollback simpler without git history. Semantically incorrect. Browsers do not cache 307.
Option C: Delete route entirely. Clean but creates 404 for bookmarked /dashboard/v2 URLs. Harder to rollback.

Recommendation: Option A (308). Tom confirms or overrides before implementation.

### Q2 -- Weekly Outlook nav entry prerequisite

Route exists on disk: src/app/(planning)/planning/weekly-outlook/page.tsx. Not in manifest at portal tip 9e2212e. CURRENT_STATE.md references prior nav add in commit 81d6c7f that did not survive to current tip. Masterplan classifies it as long-horizon planner overview (not daily-critical).

Question: is /planning/weekly-outlook production-ready for planner access today (planning:read), or should it be admin-only for now?

Implementer adds with planning:read if Tom confirms production-ready, or admin:execute if uncertain. Tom must confirm before implementer touches the manifest.

---

## Section 16 -- Handoff signature

packet_status: READY_FOR_IMPLEMENTATION
packet_authored_by: ux-flow-architect
packet_date: 2026-05-08
masterplan_ref: PRODUCTION/docs/planning/PLANNING_SCREENS_UPGRADE_MASTERPLAN.md S8.1
portal_tip_at_audit: 9e2212e

tom_approval_required: yes
tom_approval_items:
  Q1: Confirm 308 permanent redirect (vs 307 or route deletion) for /dashboard/v2.
  Q2: Confirm Weekly Outlook is production-ready for planners (planning:read) or admin-only for now.

acceptance_criteria:
  - Exactly one dashboard route at /dashboard; /dashboard/v2 redirects to it.
  - Quick Actions launcher visible and role-filtered on /dashboard; BOM Simulation absent for planners.
  - Break-glass banner appears on /dashboard when break-glass is active.
  - Critical Today block with full loading/error/empty/loaded states on /dashboard.
  - Slipped Plans block with full loading/error/empty/loaded states on /dashboard.
  - ExceptionsCard has Open inbox link.
  - PlanningCard has Open run link when run exists.
  - RecentProduction has View movement log footer link.
  - Planning group nav contains Supply Flow and Weekly Outlook (pending Q2 for gate level).
  - Admin group nav contains BOM Simulator at admin:execute.
  - FLOW-003 preserved -- Blockers nav entry and quick-action unchanged.
  - No partial-coverage or awaiting-read-model badges on graduated /dashboard.
  - /ux-release-gate on /dashboard returns SHIP or CONDITIONAL_SHIP.

rollback_plan: Four files changed, all independently revertible via git revert or single-file restore. No backend changes. No migration to reverse. Rollback: (1) restore src/app/(shared)/dashboard/v2/page.tsx from 9e2212e; (2) revert src/app/(shared)/dashboard/page.tsx; (3) revert BOM Simulation entry in quick-actions.ts to planning:read; (4) remove 3 added manifest entries. Each step independent.

accessibility_handoff_to: accessibility-usability-auditor
copy_handoff_to: ux-content-state-designer
visual_handoff_to: visual-system-designer

---

## Appendix A -- Finding quick-reference

| ID | Class | Location | Fix priority |
|---|---|---|---|
| FLOW-DG-001 | DECISION_GRADE | dashboard/page.tsx -- no quick-actions render | P0 -- must fix before ship |
| FLOW-DG-002 | DECISION_GRADE | dashboard/page.tsx -- no break-glass banner | P0 -- must fix before ship |
| FLOW-DG-003 | FLOW_COMPLETION | v2 WorkflowHeader partial-coverage badges | P1 -- fix in graduation pass |
| FLOW-DG-004 | DECISION_GRADE | quick-actions.ts BOM Simulation gate wrong | P0 -- must fix before ship |
| FLOW-DG-005 | FLOW_COMPLETION | PlanningCard -- no deep-link to run | P1 -- fix in graduation pass |
| FLOW-DG-006 | FLOW_COMPLETION | RecentProduction -- no movement log link | P1 -- fix in graduation pass |
| FLOW-DG-007 | FLOW_COMPLETION | ExceptionsCard -- no inbox link | P1 -- fix in graduation pass |

Three P0 (DECISION_GRADE) findings -- FLOW-DG-001, FLOW-DG-002, FLOW-DG-004 -- must resolve before the graduated dashboard can receive a SHIP verdict from /ux-release-gate. Four P1 (FLOW_COMPLETION) findings can fix in the same implementation pass or be named as conditionals in a CONDITIONAL_SHIP verdict.

---

## Appendix B -- RUNTIME_READY signal coverage

| Signal | Number | Endpoint | Status |
|---|---|---|---|
| CriticalToday | 19 | /api/dashboard/critical-today via v_critical_today | confirmed emitted |
| ProductionPlanSlippage | 22 | /api/dashboard/slipped-plans via v_production_plan_slippage | confirmed emitted |
| DashboardCriticalToday | 23 | portal proxy for critical-today endpoint | confirmed emitted |
| DashboardSlippedPlans | 24 | portal proxy for slipped-plans endpoint | confirmed emitted |

Break-glass endpoint /api/system/break-glass is live (confirmed via v2 page.tsx consumption) but not tracked as a RUNTIME_READY signal. No new signals required for T1.

---

## Appendix C -- Escalations required

None. No findings require backend contract changes, schema migrations, or new API endpoints. No stop conditions tripped. No frozen flags involved.

FLOW-DG-004 (BOM Simulation capability fix) is a portal-only single-field change in quick-actions.ts. No backend involved.

If the implementer discovers /planning/weekly-outlook is a content stub, gate the nav entry at admin:execute and flag to factory-os-governor for routing to appropriate execution lane. That is a conditional implementation decision, not an escalation now.
