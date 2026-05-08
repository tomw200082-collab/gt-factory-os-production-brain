# Freshness Vocabulary Visual System Handoff - T1 Planning Screens Improvement Program

**Packet status:** READY_FOR_IMPLEMENTATION_PARTIAL
**Authored by:** visual-system-designer
**Date:** 2026-05-08
**Masterplan reference:** PRODUCTION/docs/planning/PLANNING_SCREENS_UPGRADE_MASTERPLAN.md §7 (T1 scope), §8 (T1 plan), §6.5 rule 1
**Work items covered:** R1-1 (freshness vocabulary unification), R1-3 (Run sources freshness timestamps)
**Work items NOT covered:** R1-4, R1-5, R1-7 — see §8 (Adjacencies)
**Portal tip at audit time:** 9e2212e (main, clean per masterplan §1)
**Authority:** Advisory handoff only. No portal source changes authorized. Implementation requires portal-production-executor dispatch.

---

## §1 — Status and authority

**Owner agent:** visual-system-designer (this packet), portal-production-executor (implementation).

**Masterplan reference (locked):**
- §6.5 architecture rule 1: Single freshness component (FreshnessBadge) on every surface that shows time-sensitive data.
- §7 T1 scope R1-1: Standardize freshness vocabulary on FreshnessBadge across dashboard, run detail, inventory flow, PO list.
- §7 T1 scope R1-3: Run Detail: add Run sources freshness timestamps.
- Problem register OR-2: Five freshness vocabularies; standardize on FreshnessBadge.

**Expiry / closure rule:** This packet is superseded when portal-production-executor confirms every REPLACE and ADD migration in §5 is implemented and the grep test in §11 returns zero matches on T1-touched surfaces. Status then upgrades to CLOSED.

**Does this packet authorize backend changes?** No. All items are portal-only. Any finding requiring backend DTO extension is flagged as Open Question in §13.

---

## §2 — Tom decision recap

Tom approved (2026-05-08):

> T1 must standardize a single freshness component (FreshnessBadge) across the touched planning surfaces, eliminating the five competing freshness vocabularies currently in use.

Codified in masterplan §6.5 architecture rule 1 and problem register OR-2. System-level change per UX Operating Principle P5, not a one-off fix.

---

## §3 — Current-state freshness inventory

Complete enumeration of every freshness rendering on T1-touched surfaces as of portal tip 9e2212e. Read-only audit: no source modified.

### Surface 1: Inventory Flow — /planning/inventory-flow

**File:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/InventoryFlowClient.tsx
**Lines:** approx. 1513-1530 (WorkflowHeader meta slot)

Current implementation (lines 1522-1530):


Accompanied by Badge tone="success" dotted showing "Live" (or "Refreshing..." / "Error") for fetch-state signaling. Coexistence is intentional and correct: FreshnessBadge owns "how old is this data"; the status badge owns "is the query in flight right now". This pattern must be carried forward.

**Intent level:** fresh / stale / error. Threshold: warn at 5 min, crit at 30 min.
**Verdict:** REFERENCE IMPLEMENTATION. Correct usage. Do not change.

---

### Surface 2: Dashboard v1 — /dashboard

**File:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(shared)/dashboard/page.tsx

**2a — Page header freshness (lines approx. 832-837):**
Inline JSX renders a pulsing teal dot + "Live · 8 May 2026" using hardcoded inline style colors from local constant object C. Values: C.teal = "#22D3A3", C.muted = "rgba(238,238,245,0.50)". No timestamp age. No stale threshold. No FreshnessBadge.

Token status: DRIFT — uses hardcoded hex/rgba, not CSS custom properties.
Verdict for 2a: REPLACE

**2b — No per-block freshness chips:**
All 8 blocks refresh at staleTime=30_000ms but no block shows when it last refreshed. The page-level chip is the only freshness indicator for the entire page and carries no age information.
Verdict for 2b: ADD per-block freshness when dashboard graduation packet (R0-1) lands. This packet covers page-header level only.

---

### Surface 3: Dashboard v2 — /dashboard/v2

**File:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(shared)/dashboard/v2/page.tsx

**3a — CriticalTodayBlock footer (lines approx. 399-406):**
Uses local fmtRelative() function returning strings like "3h ago". Renders in SectionCard footer as plain text. No dot-indicator. No stale coloring. No threshold-based intent escalation.

**3b — SlippedPlansBlock footer (lines approx. 499-504):**
Same fmtRelative() inline pattern as 3a. Both duplicate the age-formatting logic already inside FreshnessBadge.

Verdict for 3a and 3b: REPLACE — migrate to FreshnessBadge in the footer slot of each SectionCard.

---

### Surface 4: Planning Runs list — /planning/runs

**File:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/runs/page.tsx

No FreshnessBadge import. No "as of" chip. The list renders executed_at as a per-row column value (when the run happened). This is data metadata, not a page-level freshness signal.

Verdict: No T1 action required at page-header level. The per-row executed_at display is correct as data metadata. The system rule in §7 documents this distinction explicitly.

---

### Surface 5: Planning Run detail — /planning/runs/[run_id]

**File:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/runs/[run_id]/page.tsx

**5a — fmtAgeFromRun() function (lines approx. 373-386):**
Custom freshness formatter returning strings like "as of run — 3h ago". Bespoke vocabulary not using FreshnessBadge.

**5b — fmtRelativeAndAbsolute() function (lines approx. 388-423):**
Used inline in the "Run sources" card for four rows. The developer comment at lines 388-392 explicitly says it "matches the FreshnessBadge tooltip output but uses the inline format" — acknowledging FreshnessBadge existed and choosing a partial replica instead. Lacks threshold-based intent escalation and accessibility labeling.

Five rows in Run sources card (approx. lines 3354-3479):
- Run time: uses fmtRelativeAndAbsolute on detail.executed_at, renders as absolute + relative inline spans
- Demand forecast: uses fmtRelativeAndAbsolute relative portion as inline text-3xs span
- Open orders snapshot: uses fmtRelativeAndAbsolute on detail.executed_at, renders as inline spans
- Stock anchor refreshed: uses fmtRelativeAndAbsolute on detail.stock_snapshot_anchor_refreshed_at with conditional text-warning-fg
- Stock parity drift: numeric field, no timestamp rendering

**5c — Page header:**
No FreshnessBadge import. WorkflowHeader meta slot has no freshness chip. A planner landing on a 2-day-old run detail sees no age signal before reading recommendations.

Verdict for 5a: REMOVE — superseded by FreshnessBadge. Dead code after migration.
Verdict for 5b: REPLACE — each inline call in Run sources card replaced with compact FreshnessBadge.
Verdict for 5c: ADD — FreshnessBadge in WorkflowHeader meta slot using detail.executed_at.

---

### Surface 6: Purchase Orders list — /purchase-orders

**File:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(po)/purchase-orders/page.tsx

**Current implementation (WorkflowHeader meta slot, lines approx. 593-595):**
Static Badge tone="neutral" dotted showing "Live". No timestamp. No age. No stale threshold. Cannot signal staleness. Audit §8 E.P2 flagged this.

Verdict: REPLACE — substitute FreshnessBadge for the static Live badge.

---

## §4 — Canonical FreshnessBadge contract

**Canonical file:** c:/Users/tomw2/Projects/window2-portal-sandbox/src/components/badges/FreshnessBadge.tsx
**Import:** import { FreshnessBadge } from "@/components/badges/FreshnessBadge"

This contract documents the component as it exists at portal tip 9e2212e. The implementer must not diverge from the Inventory Flow reference implementation.

### 4.1 Props interface (as implemented)

    interface FreshnessBadgeProps {
      label?: string;
      lastAt?: string;            // ISO-8601 timestamp. Undefined = never/neutral tone.
      warnAfterMinutes?: number;  // Default: 60. Transitions to warning/stale tone.
      failAfterMinutes?: number;  // Default: 1440. Transitions to danger/critical tone.
      compact?: boolean;          // Removes border/background pill. For inline use.
      producer?: string;          // Source name for tooltip. e.g. "inventory_flow_projection"
    }

### 4.2 Intent levels

| Internal tone | Display state | Condition | Dot color token |
|---|---|---|---|
| success | Fresh | minutesSince(lastAt) <= warnAfterMinutes | bg-success |
| warning | Stale | > warnAfterMinutes AND <= failAfterMinutes | bg-warning |
| danger | Critical | > failAfterMinutes | bg-danger |
| neutral | Never / unknown | lastAt is undefined, null, or unparseable | bg-fg-faint |

### 4.3 Canonical thresholds by surface type

| Surface type | warnAfterMinutes | failAfterMinutes | Rationale |
|---|---|---|---|
| Near-real-time projection (Inventory Flow) | 5 | 30 | 5 min stale is operationally significant |
| Dashboard command center page header | 2 | 15 | Command center; 2 min visible to planner |
| Dashboard block — Critical Today | 5 | 30 | Same cadence as inventory flow |
| Dashboard block — Slipped Plans | 30 | 240 | Less volatile; 30 min stale acceptable |
| Planning run age (immutable run) | 60 | 1440 | Run older than 24h: prompt re-run before approving recs |
| Snapshots captured at run time | 60 | 1440 | Snapshot age equals run age |
| Nightly-job-refreshed stock anchor | 120 | 1440 | 2h stale = nightly job may have failed |
| Purchase orders list | 10 | 120 | PO data changes hourly; 10 min stale acceptable |

### 4.4 Typography and token usage

All correct in the current implementation. No changes required:
- Container: rounded-sm border border-border/70 bg-bg-raised px-2 py-1
- Label: text-3xs font-semibold uppercase tracking-sops text-fg-subtle
- Age value: font-mono text-2xs font-semibold tabular-nums text-fg-strong
- Suffix "ago": text-3xs text-fg-subtle
- Dot: dot CSS class + semantic color token (bg-success / bg-warning / bg-danger / bg-fg-faint)
- Icon: Clock from lucide-react, h-3 w-3 text-fg-faint
No hardcoded hex. No arbitrary spacing. All spacing uses Tailwind scale.

### 4.5 Accessibility behavior

The component renders aria-label on the root div:
    "{label}: {toneLabel}, {formatAgo(min)} ago (producer: {producer})"

The title attribute carries the full tooltip for sighted users. Decorative elements use aria-hidden.

Required: every call site must supply a meaningful label prop when more than one FreshnessBadge appears on the same page. Without label, the aria-label begins with tone level ("Fresh, 3m ago"), which is ambiguous when multiple badges appear. On the Run sources card, all five badge instances must have distinct labels.

### 4.6 Placement rules

| Placement | Usage | Format |
|---|---|---|
| WorkflowHeader meta slot | Page-level data currency | Full pill (not compact), label required |
| SectionCard footer slot | Per-block freshness | Full pill or compact; label required |
| Inline in dd (definition list) | Per-source timestamps | compact={true}, label required |
| Table cell | Not used — do not introduce | — |

### 4.7 What FreshnessBadge is NOT responsible for

- Query fetch state (loading / refreshing / error): use Badge component with tone variants.
- Action affordances: no button or link inside FreshnessBadge.
- Surface-specific microcopy: ux-content-state-designer owns tooltip and label copy.

---

## §5 — Migration map

### KEEP_AS_IS

| ID | File | Location | Reason |
|---|---|---|---|
| K-1 | InventoryFlowClient.tsx | FreshnessBadge with label="As of", warnAfterMinutes=5, failAfterMinutes=30, producer="inventory_flow_projection" (lines 1522-1530) | Reference implementation. Correct in all dimensions. |
| K-2 | InventoryFlowClient.tsx | Badge tone="success" dotted showing "Live" / "Refreshing" / "Error" (lines 1505-1520) | Signals query state not data age. Different semantic from FreshnessBadge. Correct coexistence. Keep. |

### REPLACE

**REP-1** — dashboard/page.tsx header (approx. 832-837)
Current: Inline style pulsing dot + "Live · {date}" using C.teal = "#22D3A3" and C.muted = "rgba(238,238,245,0.50)".
Replace with:
    <FreshnessBadge
      label="As of"
      lastAt={pageDataUpdatedAt}
      warnAfterMinutes={2}
      failAfterMinutes={15}
      producer="dashboard"
    />
Note: Derive pageDataUpdatedAt from most-recent dataUpdatedAt across active queries. Remove the pulse-live div and inline span. Remove import of C constants if no other usage remains.

**REP-2** — dashboard/v2/page.tsx CriticalTodayBlock footer (approx. 399-406)
Current: plain text fmtRelative(asOf, now) in a span.
Replace with:
    <FreshnessBadge label="Critical today" lastAt={asOf} warnAfterMinutes={5} failAfterMinutes={30} producer="v_critical_today" compact />
Remove fmtRelative() call and plain text wrapper.

**REP-3** — dashboard/v2/page.tsx SlippedPlansBlock footer (approx. 499-504)
Current: plain text fmtRelative(asOf, now) in a span.
Replace with:
    <FreshnessBadge label="Slipped plans" lastAt={asOf} warnAfterMinutes={30} failAfterMinutes={240} producer="v_production_plan_slippage" compact />
Remove fmtRelative() call.

**REP-4** — purchase-orders/page.tsx WorkflowHeader meta slot (approx. 593-595)
Current: Badge tone="neutral" dotted showing "Live".
Replace with:
    <FreshnessBadge
      label="Purchase orders"
      lastAt={allPosQuery.dataUpdatedAt > 0 ? new Date(allPosQuery.dataUpdatedAt).toISOString() : undefined}
      warnAfterMinutes={10}
      failAfterMinutes={120}
      producer="purchase_orders_query"
    />
Remove static Live badge. See §13 OQ-3 for zero-state handling note.

**REP-5** — runs/[run_id]/page.tsx Run sources "Run time" row (approx. 3360-3370)
Current: fmtRelativeAndAbsolute(detail.executed_at) rendered as absolute + relative inline spans.
Replace with:
    <FreshnessBadge label="Run executed" lastAt={detail.executed_at} warnAfterMinutes={60} failAfterMinutes={1440} compact producer="planning_run_engine" />
alongside absolute datetime in font-mono text-xs span.

**REP-6** — runs/[run_id]/page.tsx Run sources "Demand forecast" row (approx. 3402-3404)
Current: captured {fmtRelativeAndAbsolute(detail.executed_at).relative} as plain text-3xs span.
Replace with:
    <FreshnessBadge label="Forecast snapshot" lastAt={detail.executed_at} warnAfterMinutes={60} failAfterMinutes={1440} compact producer="planning_run_engine" />
Rationale: snapshot is by definition as old as the run; executed_at is the correct timestamp.

**REP-7** — runs/[run_id]/page.tsx Run sources "Open orders snapshot" row (approx. 3421-3433)
Current: "Captured at run time" + absolute + relative inline spans.
Replace with:
    <FreshnessBadge label="Orders snapshot" lastAt={detail.executed_at} warnAfterMinutes={60} failAfterMinutes={1440} compact producer="planning_run_engine" />
Same timestamp source as REP-6.

**REP-8** — runs/[run_id]/page.tsx Run sources "Stock anchor refreshed" row (approx. 3441-3453)
Current: fmtRelativeAndAbsolute(detail.stock_snapshot_anchor_refreshed_at) as absolute + relative inline spans with conditional text-warning-fg.
Replace with:
    <FreshnessBadge label="Stock anchor" lastAt={detail.stock_snapshot_anchor_refreshed_at} warnAfterMinutes={120} failAfterMinutes={1440} compact producer="balance_anchors_job" />
Uses stock_snapshot_anchor_refreshed_at (not executed_at) because the anchor is refreshed independently of the run.

### ADD

**ADD-1** — runs/[run_id]/page.tsx WorkflowHeader meta slot
Add:
    <FreshnessBadge label="Run age" lastAt={detail.executed_at} warnAfterMinutes={60} failAfterMinutes={1440} producer="planning_run_engine" />
Purpose: tells planner at a glance whether this run is recent before they read any recommendation. Full pill (not compact).

**ADD-2** — dashboard/v2/page.tsx WorkflowHeader meta slot (after existing badges)
Add:
    <FreshnessBadge label="As of" lastAt={pageDataUpdatedAt} warnAfterMinutes={5} failAfterMinutes={30} producer="dashboard_v2" />
Where pageDataUpdatedAt = most-recent dataUpdatedAt across CriticalTodayBlock and SlippedPlansBlock queries.

### REMOVE

**REM-1** — runs/[run_id]/page.tsx
Remove: fmtAgeFromRun() function (approx. lines 373-386) and all call sites.
Reason: superseded by FreshnessBadge. No remaining call sites after REP-5/6/7/8 migration.

**REM-2** — runs/[run_id]/page.tsx
Remove: fmtRelativeAndAbsolute() function (approx. lines 388-423) and all call sites in the Run sources card.
Note: Verify no other call sites exist outside the Run sources card before deleting the function definition.

**REM-3** — dashboard/page.tsx
Remove: pulse-live CSS class usage and the pulsing dot div in the header.
Reason: replaced by REP-1. The pulse-live animation is not part of FreshnessBadge.

---

## §6 — Run sources section design (R1-3)

### 6.1 Current state

The "Run sources" card at approx. lines 3348-3480 is English-language (post Cycle 3 rewrite) and uses fmtRelativeAndAbsolute() for four of its five timestamp rows. Masterplan §5.1 DT-5 still flags it: "Lacks freshness timestamps on demand snapshot, orders snapshot, anchor sync."

The developer comment in the file (lines 388-392) acknowledges FreshnessBadge should be used here. The audit §3 E.P0 finding (now English after Cycle 3 but still using the bespoke function) confirms this is the unfinished piece of OR-2.

### 6.2 Target rendering — all rows

**Row 1 — Run time**
dt: "Run executed"
dd: FreshnessBadge with label="Run executed", lastAt=detail.executed_at, warnAfterMinutes=60, failAfterMinutes=1440, compact, producer="planning_run_engine" + absolute datetime in font-mono text-xs span.
Threshold rationale: A run older than 1 hour means stock positions and open orders may have changed. A run older than 24 hours escalates to danger tone to prompt a fresh run before approving recommendations.

**Row 2 — Triggered by**
No freshness badge needed. Categorical field (Manual / Scheduled). Existing rendering is correct.

**Row 3 — Demand forecast**
When demand_snapshot_forecast_version_id is set:
  Existing "Open forecast" link + FreshnessBadge with label="Forecast snapshot", lastAt=detail.executed_at, warnAfterMinutes=60, failAfterMinutes=1440, compact, producer="planning_run_engine".
When null: existing "No forecast attached" copy. No badge needed.
Rationale: The forecast snapshot is captured at run time. executed_at is the correct clock for planning trust, not the forecast creation date.

**Row 4 — Open orders snapshot**
When demand_snapshot_orders_snapshot_run_id is set:
  "Captured at run time" text + FreshnessBadge with label="Orders snapshot", lastAt=detail.executed_at, warnAfterMinutes=60, failAfterMinutes=1440, compact, producer="planning_run_engine".
When null: existing "No open-orders snapshot attached" copy.

**Row 5 — Stock anchor refreshed**
FreshnessBadge with label="Stock anchor", lastAt=detail.stock_snapshot_anchor_refreshed_at, warnAfterMinutes=120, failAfterMinutes=1440, compact, producer="balance_anchors_job" + absolute datetime in font-mono text-xs span.
When stock_snapshot_anchor_refreshed_at is null: FreshnessBadge with lastAt={undefined} renders in neutral/never tone automatically. Do not guard with a conditional null check — the never state is informative.
Threshold rationale: balance_anchors rebuild runs nightly. An anchor older than 2 hours during a workday may indicate the job failed. An anchor older than 24 hours means quantity projections may be wrong.

**Row 6 — Stock parity drift at run time**
Numeric field. No badge.

### 6.3 DTO verification — no backend change required

Fields confirmed present in PlanningRunDetail type in runs/[run_id]/page.tsx:
- detail.executed_at — line 77, type string (always present)
- detail.stock_snapshot_anchor_refreshed_at — line 83, type string | null
- detail.demand_snapshot_forecast_version_id — line 84, type string | null
- detail.demand_snapshot_orders_snapshot_run_id — line 85, type string | null

All required timestamps are already in the detail payload. T1 is portal-only rendering. No backend change, no DTO extension.

### 6.4 What the planner reads after T1

A planner landing on a run detail will see, before reading any recommendation:

Run age badge in WorkflowHeader meta: "4h ago [warning dot]"

In Run sources card:
- Run executed: 4h ago [warning dot] — May 08, 2026 10:23
- Demand forecast: Open forecast link + badge "Forecast snapshot: 4h ago [warning dot]"
- Orders snapshot: "Captured at run time" + badge "Orders snapshot: 4h ago [warning dot]"
- Stock anchor: badge "Stock anchor: 6h ago [danger dot — over 120-min threshold]" — May 08, 2026 08:15

This is a complete, standardized, threshold-aware freshness picture for all four inputs to the run. Before T1, the same planner sees bespoke monospace text with conditional CSS color — technically accurate but not standardized, not accessible as a badge system, and not using threshold intent escalation.

---

## §7 — System rule proposal for DESIGN_SYSTEM_RULES.md

The following text is proposed for addition to PRODUCTION/docs/phase8/ux/DESIGN_SYSTEM_RULES.md as a new top-level section after "Component variant registry". This is within the visual-system-designer write authority (additions by visual-system-designer; token changes require Tom authorization — this is a documentation addition, not a token change).

---

**Proposed addition text (insert verbatim after "Component variant registry" section):**

---

### Freshness component rule (SYSTEM_RULE — OR-2 closure, 2026-05-08)

Every portal surface that displays time-sensitive data must use FreshnessBadge from
src/components/badges/FreshnessBadge.tsx as its sole freshness vocabulary.
No surface may render "Live", "as of time", "updated time", "as of run — ...",
or any other freshness phrase as a substitute.

Reference implementation: src/app/(planning)/planning/inventory-flow/InventoryFlowClient.tsx
lines approx. 1522-1530. Do not change this implementation.

Canonical import: import { FreshnessBadge } from "@/components/badges/FreshnessBadge"

Permitted co-occurrence: A Badge component with tone="success"/"info"/"danger" dotted may
appear alongside FreshnessBadge in the same meta slot to signal query fetch state
(Loading / Refreshing / Error). These are separate signals and must not be merged.

Forbidden patterns:
- Badge tone="neutral" dotted showing "Live" as a freshness signal — use FreshnessBadge instead.
- Inline style color values for freshness indicators — all color via CSS custom properties.
- Local fmtRelative(), fmtAgeFromRun(), fmtRelativeAndAbsolute() for freshness display — superseded.
- pulse-live CSS class on freshness indicators.
- FreshnessBadge inside a table cell.

Canonical thresholds by surface type:

| Surface type | warnAfterMinutes | failAfterMinutes |
|---|---|---|
| Near-real-time projection (Inventory Flow) | 5 | 30 |
| Dashboard command center page header | 2 | 15 |
| Dashboard block Critical Today type | 5 | 30 |
| Dashboard block Slipped Plans type | 30 | 240 |
| Planning run age | 60 | 1440 |
| Snapshot captured at run time | 60 | 1440 |
| Nightly-job-refreshed stock anchor | 120 | 1440 |
| Purchase orders list | 10 | 120 |

Placement rules:
- WorkflowHeader meta slot: full pill (not compact), label prop required.
- SectionCard footer slot: full pill or compact; label prop required.
- Inline dd in a definition list: compact={true}, label prop required.
- Not in table cells.

Accessibility requirement: Every FreshnessBadge call site must supply a label prop when the
badge appears alongside other signals (any page with more than one FreshnessBadge). Label must
be a short, meaningful noun phrase: "As of", "Demand snapshot", "Orders snapshot", "Stock anchor".

When adding a new surface: implementer must add a row to the threshold table in the same PR.
visual-system-designer sign-off required on new threshold values.

---

## §8 — Adjacencies (R1-4, R1-5, R1-7)

These three T1 work items are NOT covered in this packet. Listed here so the implementer knows this packet alone does not complete T1.

### R1-4 — Run Detail: render item_name/component_name on exception rows

Not in this packet because: information-hierarchy and content-state problem. Exception rows currently show raw item_id / component_id values (regression vs lock 0997398 "show names not IDs"). The fix requires verifying whether the exception DTO carries name fields and replacing raw ID rendering. This is interaction-design-specialist and ux-content-state-designer domain.

Follow-up: Dispatch interaction-design-specialist for R1-4. Verify exception DTO payload carries item_name / component_name fields; if not, a small backend DTO extension is needed.

### R1-5 — Run Detail: fix exception deep-links

Not in this packet because: routing / navigation problem. missing_supplier_mapping routes to /admin/masters/items/{componentId} (wrong; should be /admin/masters/components/{componentId}). missing_bom lands on overview tab instead of appending ?tab=bom. Pure routing logic in ExceptionActionLink. No visual system rule involved.

Follow-up: Dispatch interaction-design-specialist for R1-5. Surgical routing corrections. Can be batched with R1-4.

### R1-7 — Recommendation drill-down: hide approve/reject when status is not pending

Not in this packet because: state-aware action button visibility rule. Approve/reject buttons stay rendered when rec.status !== "pending", leading to a 409 server error on click. The fix is a conditional render gate. This is interaction-design-specialist domain per BUTTON_AND_ACTION_RULES.md.

Follow-up: Dispatch interaction-design-specialist for R1-7. 0.25-day fix per masterplan. Can be bundled with R1-4 and R1-5 in a single packet.

**Recommendation to orchestrator:** Before T1 implementation begins, dispatch interaction-design-specialist for a single packet covering R1-4, R1-5, and R1-7. These three items share a surface and a domain. A single packet is more efficient than three separate dispatches.

---

## §9 — Forbidden patterns (implementer must-not-do list)

1. Do not introduce a second freshness primitive. There must be exactly one freshness component after T1: FreshnessBadge at src/components/badges/FreshnessBadge.tsx. Do not create a FreshnessChip, StaleIndicator, DataAge, or any other variant. If FreshnessBadge needs a new rendering mode, add a prop to the existing component.

2. Do not inline-style freshness colors. Dashboard v1's C.teal / C.muted pattern is a design token drift violation. Do not replicate the C.{} pattern for any freshness-related color.

3. Do not remove freshness rendering from any surface that currently has it. The migration action is REPLACE, not REMOVE. The only REMOVE actions in this packet are helper functions that become dead code after the REPLACE migrations.

4. Do not change Inventory Flow's freshness behavior. InventoryFlowClient.tsx is the reference implementation. Its FreshnessBadge props, threshold values, and co-occurrence with the status badge are canonical.

5. Do not use FreshnessBadge inside a table cell. Use a date-column pattern for table freshness values.

6. Do not hard-code threshold values as magic numbers without a comment explaining the rationale.

7. Do not suppress the never state. When lastAt is undefined or null, FreshnessBadge renders "never" in neutral tone. This is correct and informative. Do not guard with conditional null unless the field is guaranteed populated another way.

8. Do not omit the label prop when multiple badges appear on the same page. On the Run sources card, all five FreshnessBadge instances must have a distinct label.

9. Do not use the pulse-live CSS animation on the new badges. FreshnessBadge uses a static dot.

10. Do not add FreshnessBadge to a surface not on the T1 list without visual-system-designer review. The migration map in §5 is exhaustive for T1.

---

## §10 — Files expected to be touched

### COMPONENT (likely no changes needed)
- c:/Users/tomw2/Projects/window2-portal-sandbox/src/components/badges/FreshnessBadge.tsx
  No props changes required for T1. Existing interface supports all T1 call sites. The compact prop is implemented. Open only if a bug is discovered. Any prop additions require visual-system-designer review.

### SURFACE (portal page and client files)
- c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(shared)/dashboard/page.tsx
  Replace header freshness pattern (REP-1). Add FreshnessBadge import.
- c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(shared)/dashboard/v2/page.tsx
  Replace CriticalTodayBlock and SlippedPlansBlock footer patterns (REP-2, REP-3). Add page-header badge (ADD-2). Add FreshnessBadge import.
- c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(po)/purchase-orders/page.tsx
  Replace static Live badge (REP-4). Add FreshnessBadge import.
- c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/runs/[run_id]/page.tsx
  Replace five inline freshness renderings (REP-5 through REP-8). Add run-header badge (ADD-1). Remove dead helper functions (REM-1, REM-2). Add FreshnessBadge import.

### TOKEN (no changes)
- tailwind.config.ts: No changes. All required tokens already defined.
- globals.css: No changes.

### DOCS
- c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/docs/phase8/ux/DESIGN_SYSTEM_RULES.md
  Add freshness component rule section (see §7 proposed text). Documentation addition within visual-system-designer write authority. No Tom authorization required.

---
## §11 — Verification gates

### Gate 1 — grep test (zero matches required on T1-touched surfaces)

After implementation, search for the following patterns across the four touched files.
Any match = regression. Zero matches = PASS.

Search for in dashboard/page.tsx, dashboard/v2/page.tsx, purchase-orders/page.tsx, runs/[run_id]/page.tsx:
- Static "Live" string as a Badge child (not in a comment)
- fmtAgeFromRun (function name anywhere in file)
- fmtRelativeAndAbsolute (function name anywhere in file)
- pulse-live (CSS class string)
- C.teal or C.muted or C.gold in freshness-related sections (hardcoded hex constants)

Exclude from this check: InventoryFlowClient.tsx — it legitimately uses Badge dotted "Live" as a query-state signal alongside FreshnessBadge, which is the correct pattern.

### Gate 2 — FreshnessBadge import presence

All four touched surface files must contain:
    import { FreshnessBadge } from "@/components/badges/FreshnessBadge"

### Gate 3 — /design-system-check on T1 surfaces

Run /design-system-check against each T1-touched surface. No TOKEN_DRIFT findings for color values in freshness rendering.

### Gate 4 — /screen-scorecard per surface

Each touched surface must score SHIP on the freshness-vocabulary dimension:
- /dashboard: SHIP on freshness dimension.
- /dashboard/v2: SHIP on freshness dimension.
- /purchase-orders: SHIP on freshness dimension.
- /planning/runs/[run_id]: SHIP on freshness dimension (R1-3 closure). Other open items (R1-4, R1-5, R1-7) may keep the surface at CONDITIONAL_SHIP until their packets are implemented.
- /planning/inventory-flow: no change expected; verify no regression.

### Gate 5 — /ux-release-gate aggregate

Aggregate gate verdict for T1 must include a note confirming OR-2 (five freshness vocabularies reduced to one) is closed. T1 cannot ship complete until R1-4, R1-5, and R1-7 companion packets are also implemented (see §8).

---

## §12 — Collision risk

### Window B (backend BOM verification)
No collision. Portal-only. No BOM-walking functions, no migrations, no schema changes. The balance_anchors refreshed_at timestamp is a stable backend asset already exposed in the detail DTO.

### Portal main branch
Inventory Flow FreshnessBadge usage is not being changed. The migration is additive or substitutive on other surfaces. No regression risk to the most-used planning surface.

### Parallel packet from ux-flow-architect (dashboard graduation R0-1)
The ux-flow-architect packet for dashboard graduation may restructure /dashboard and /dashboard/v2 layouts. If implemented concurrently, there is a merge risk on dashboard/page.tsx and dashboard/v2/page.tsx.

Recommended sequencing: dashboard graduation (R0-1) first, then freshness vocabulary (R1-1/R1-3). Freshness changes are isolated to WorkflowHeader meta slots and SectionCard footer slots. If graduation changes those slot structures, apply freshness changes to the post-graduation versions.

If both must ship in parallel, portal-production-executor must reconcile both packets in a single branch.

### R1-4 / R1-5 / R1-7 companion packet
No collision. Those items touch exception row rendering, routing logic, and button visibility in runs/[run_id]/page.tsx — distinct zones from the WorkflowHeader meta slot and Run sources card. Can be implemented in either order.

---
## §13 — Open questions for Tom

### OQ-1 — FreshnessBadge component location
FreshnessBadge lives at src/components/badges/FreshnessBadge.tsx. After T1 it will be imported by at least 5 files. Should it be promoted to src/components/feedback/FreshnessBadge.tsx (alongside states.tsx) for discoverability? No action required for T1. Flag for a future housekeeping pass.

### OQ-2 — Dashboard v1 freshness migration vs graduation sequencing
If v1 is deprecated under R0-1, REP-1 may be unnecessary. Recommendation: implement REP-1 regardless. Until v1 is formally removed from the route tree it continues to render, and a freshness violation on a live route violates OR-2.

### OQ-3 — Purchase Orders dataUpdatedAt zero-state handling
REP-4 proposes using allPosQuery.dataUpdatedAt (TanStack Query built-in) as the lastAt source. Before the first fetch completes, dataUpdatedAt is 0 (epoch). Converting 0 to ISO string gives 1970-01-01T00:00:00.000Z, triggering danger tone immediately — which is correct (data not yet loaded = not fresh). If this is confusing, the implementer may guard: allPosQuery.dataUpdatedAt > 0 ? new Date(allPosQuery.dataUpdatedAt).toISOString() : undefined. The undefined case renders neutral/never tone. Document the choice with an inline comment.

### OQ-4 — Per-block freshness on dashboard v1 beyond page header
This packet covers page-header level only for dashboard v1. Per-block freshness on all 8 blocks (audit §11 E.P1) is deferred until the dashboard graduation decision (R0-1) is resolved. If v1 and v2 merge, the merged layout will need a per-block freshness audit — flag for the dashboard graduation packet.

---

## §14 — Handoff signature

Packet status: READY_FOR_IMPLEMENTATION_PARTIAL
Agent: visual-system-designer
Date: 2026-05-08
Portal tip: 9e2212e
Design system: Operational Precision — tokens confirmed present in tailwind.config.ts

Work items covered:
- R1-1: Unified freshness vocabulary — DESIGNED, ready for portal-production-executor
- R1-3: Run sources freshness timestamps — DESIGNED, ready for portal-production-executor

Work items NOT covered (adjacencies requiring separate handoff):
- R1-4: interaction-design-specialist domain — see §8
- R1-5: interaction-design-specialist domain — see §8
- R1-7: interaction-design-specialist domain — see §8

Findings:
- VISUAL-001 (SYSTEM_RULE): FreshnessBadge is canonical. Enforce via system rule in DESIGN_SYSTEM_RULES.md.
- VISUAL-002 (TOKEN_DRIFT): Hardcoded hex in dashboard v1 header freshness section. Fix: REP-1.
- VISUAL-003 (COMPONENT_INCONSISTENCY): Local fmtRelative() in dashboard v2 footers. Fix: REP-2, REP-3.
- VISUAL-004 (COMPONENT_INCONSISTENCY): Static Live badge on PO list. Fix: REP-4.
- VISUAL-005 (COMPONENT_INCONSISTENCY): Bespoke helper functions in run detail. Fix: REP-5 through REP-8, REM-1, REM-2, ADD-1.
- VISUAL-006 (ONE_OFF_FIX): No freshness signal in run detail header. Fix: ADD-1.

Token changes required: none
Component changes required: none
Copy handoff to: ux-content-state-designer
A11y handoff to: accessibility-usability-auditor

Next dispatch recommended:
- interaction-design-specialist: R1-4, R1-5, R1-7 (single packet, same surface and domain)
- portal-production-executor: R1-1, R1-3 (this packet is ready)

---

## Audit summary

Design system reference:
- tailwind.config.ts: read yes
- globals.css: read no (tokens confirmed present via tailwind.config.ts)
- Operational Precision tokens: confirmed present

Hierarchy review:
- PASS: FreshnessBadge has clear visual hierarchy
- FAIL dashboard v1 header: TOKEN_DRIFT (VISUAL-002)
- FAIL dashboard v2 block footers: plain text, no hierarchy or intent escalation (VISUAL-003)
- PASS Inventory Flow reference implementation

Component consistency review:

| Component | Correct variant | Finding |
|---|---|---|
| FreshnessBadge in Inventory Flow | Reference implementation | KEEP_AS_IS |
| Badge neutral dotted Live in PO list | Incorrect freshness signal | VISUAL-004 REPLACE |
| Inline fmtRelative() in dashboard v2 footers | Not a component | VISUAL-003 REPLACE |
| Inline style pulsing dot in dashboard v1 header | TOKEN_DRIFT | VISUAL-002 REPLACE |
| fmtRelativeAndAbsolute() + fmtAgeFromRun() in run detail | Bespoke helpers | VISUAL-005 REPLACE + REMOVE |

Token hygiene:

| Issue | Location | Finding |
|---|---|---|
| C.teal = #22D3A3 in freshness header | dashboard/page.tsx | TOKEN_DRIFT |
| C.muted = rgba in freshness header | dashboard/page.tsx | TOKEN_DRIFT |
| Inline conditional text-warning-fg in Run sources | runs/[run_id]/page.tsx | Non-standard; superseded by FreshnessBadge |
