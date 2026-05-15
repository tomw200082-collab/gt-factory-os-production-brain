# ux-flow-architect audit — /inventory

**Audit date:** 2026-05-14
**Trigger:** Tom screenshot 2026-05-14 morning — (a) qty column blank on every row, every TIER showed `? Unknown` — root cause was portal-shipped-before-Railway version skew; hotfixed via `gt-factory-os-portal` PR #17 (`dc8f514` on main) with `resolveDisplay(row)` defensive fallback. (b) `—` persists in VALUE (ILS) column for many FG items despite trust strip claim "Cost rolled-up nightly for manufactured FG".

**Surface audited:** `/inventory` (`src/app/(shared)/inventory/page.tsx`)
**Portal tip at time of audit:** `dc8f514` (main, post-PR #17 hotfix)
**Backend:** `gt-factory-os` Railway; stock list handler `api/src/stock/handler.ts`; value handler `api/src/stock/value-handler.ts`; ledger handler `api/src/stock/ledger-handler.ts`
**Design spec:** `PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md`

**RUNTIME_READY signals inspected:** No discrete `RUNTIME_READY(StockTruthChange1)` signal found. The Change 1 overlay (Reconcile badge, StockTruthDrawer, display fields) was delivered without its own signal — flagged as governance concern only, not a flow gap.

---

## Contracts inspected

- `api/src/stock/handler.ts` — live SQL confirms `on_hand_raw`, `on_hand_display`, `is_below_floor`, `floor_gap` are all returned (read: yes)
- `api/src/stock/value-handler.ts` — live SQL confirms cost source is `supplier_items.std_cost_per_inv_uom` where `is_primary = true`; **no manufactured-FG rollup column exists** (read: yes)
- `api/src/stock/schemas.ts` — `StockValueRow` confirms `supply_method` returned for FG; `unit_cost_ils` is nullable (read: yes)
- `PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md` — complete spec (read: yes)
- `PRODUCTION/docs/phase8/ux/UX_OPERATING_PRINCIPLES.md` — DRAFT principles (read: yes)
- `PRODUCTION/docs/phase8/ux/CONTENT_AND_MICROCOPY_GUIDE.md` — copy standards (read: yes)
- `PRODUCTION/docs/phase8/ux/STATUS_EMPTY_ERROR_STATES.md` — state hygiene standards (read: yes)

---

## Flow coverage

| Flow stage | Status | Finding |
|---|---|---|
| Entry / context | PARTIAL | Header copy is technically accurate but uses internal jargon (`private_core.current_balances`) in the trust strip — a developer path visible to operators. |
| Processing / state | PASS | Skeleton matches table layout; `aria-busy` set; no "0 items" during load; `Refreshing` indicator on background re-fetch. One gap: value data and list data have separate stale times — operator can see total value update while list is stale (or vice versa). |
| Review / decision | **FAIL** | The "Cost rolled-up nightly for manufactured FG" claim is a promise the system does not fulfil. The value handler computes cost from `supplier_items` only — no nightly rollup mechanism exists. MANUFACTURED FG items with no primary supplier-items row show `—` forever, not "pending rollup." The `pending_rollup` badge is derived in the portal but the backend never emits a separate "rolled-up" cost. The trust strip is making a nightly-job promise with no job behind it. |
| Terminal action | PARTIAL | "Post corrective Goods Receipt" CTA opens in a new tab. Works but breaks the corrective workflow: after posting, the drawer in the original tab does not refresh. Operator must manually Refresh and reopen the drawer. |
| Post-action visibility | **FAIL** | After posting a corrective GR in the new tab, there is no signal back to the drawer or the list. Drawer TanStack query has `staleTime: 30_000`; will not re-fetch. Warning alert count will not decrement. Reconcile chip count will not drop. Operator has no confidence the action worked. |
| Auditability | PARTIAL | Drawer shows the 10 most recent ledger events. The corrective GR, once posted, is visible on the next drawer open. However `total_matching` from the ledger API is not surfaced — operator cannot know whether 10 shown are complete. |
| Recovery / error | PARTIAL | Page error state is well-formed with Retry. Drawer error state is well-formed with "Try again." However ledger error state inside the drawer still shows the CTA — operator could post a duplicate GR without having seen the existing ledger. |

---

## Findings

### [FLOW-001] Trust strip exposes a developer table path to operators
- **Class:** FLOW_COMPLETION
- **Location:** `page.tsx` line 927 — `"Source: private_core.current_balances"`
- **Description:** Trust strip shows the literal Postgres schema-qualified table name. Forbidden pattern per `CONTENT_AND_MICROCOPY_GUIDE.md`. An operator who calls support will quote this string; it sets a false technical register for a non-technical audience.
- **Proposed fix:** Replace with "Source: Stock ledger" (ux-content-state-designer confirms exact label).
- **Acceptance criterion:** Trust strip shows no DB object names, schema names, or SQL path fragments.

### [FLOW-002] "Cost rolled-up nightly for manufactured FG" is a promise the system does not keep — **HIGHEST IMPACT**
- **Class:** DECISION_GRADE
- **Location:** `page.tsx` line 940 (trust strip secondary); line 952 (KPI card secondary `"Manufactured FG rolled up nightly."`)
- **Description:** Tom's direct complaint. The trust strip and Total Inventory Value KPI both state manufactured FG cost is "rolled up nightly." The backend value handler computes cost exclusively from `supplier_items.std_cost_per_inv_uom` where `is_primary = true`. **There is no nightly rollup job. There is no BOM-based cost accumulation.** For a MANUFACTURED FG item with no primary supplier-items row, `unit_cost_ils` is always null, `total_value_ils` is always null, and the portal `deriveCostStatus` returns `pending_rollup` (displayed as "Rolled-up cost pending"). This label implies a pending job will eventually fill the value. **In reality, the value will remain "—" unless a `supplier_items` row with `is_primary = true` is created manually for that FG item.** Operator looking at `—` after hours of operation is correct to be confused: system promised a cost would appear, and it never will.
- **Proposed fix (portal only, no backend change):** Remove both instances of "nightly" rollup language. Replace with honest, state-describing copy that does not promise an automated process. The `CostBadge` label "Rolled-up cost pending" must also be revised — since no rollup will happen, this label is actively misleading. Replace with a factual label such as "Cost not set." ux-content-state-designer owns replacement copy.
- **Acceptance criterion:** No copy on `/inventory` references "nightly," "rolled-up nightly," "rollup," or automation-implying language. The `pending_rollup` CostBadge label is updated. `—` in VALUE for MANUFACTURED FG items is accompanied by copy that honestly describes the state.

### [FLOW-003] `pending_rollup` CostBadge label actively misleads daily users
- **Class:** DECISION_GRADE
- **Location:** `page.tsx` line 349 (`CostBadge`); `deriveCostStatus` line 247
- **Description:** `deriveCostStatus` returns `"pending_rollup"` for any FG item with `supply_method === "MANUFACTURED"` and no `unit_cost`. The badge renders "Rolled-up cost pending" with info tone. This tells the operator "wait, something is running." **Nothing is running.** Dozens of rows on a daily shift can carry this badge with no path to act. Combined with FLOW-002, operators told "it will roll up tonight" will wait night after night with nothing changing.
- **Proposed fix:** Change label to "Cost not set" (matching `missing_cost` treatment, or with a subtle distinction like "BOM cost not configured"). Remove implied wait-state tone. Add secondary note in MISSING COST DATA KPI card that includes MANUFACTURED items so the count is understood to cover both bought-finished + manufactured-without-cost cases.
- **Acceptance criterion:** The `pending_rollup` badge contains no "pending," "rollup," or automation-implying language. Operator understands manual action is required. Badge tone is `warning` not `info` (or merged with `missing_cost`).

### [FLOW-004] "MISSING COST DATA: 67" diverges from the chip-filtered count
- **Class:** FLOW_COMPLETION
- **Location:** `page.tsx` lines 970–980 (KPI card)
- **Description:** KPI count comes from `valueData.items_without_cost` — counts items with `unit_cost_ils = null` including BOTH `missing_cost` and `pending_rollup` cases. But the "Missing cost" chip filter activates only `missing_cost` items. So card might say `67` but chip shows `12`. No explanation. Operator clicks "Missing cost" and wonders where the other 55 went.
- **Proposed fix:** Update `missingCostOnly` filter logic to also match `pending_rollup` (so chip count matches KPI). Portal-only change, no backend contract impact.
- **Acceptance criterion:** When "Missing cost" chip is active, number of rows shown equals (or is explained relative to) the KPI card count.

### [FLOW-005] Warning alert is not dismissable and has no per-visit persistence
- **Class:** FLOW_COMPLETION
- **Location:** `page.tsx` lines 983–1003
- **Description:** Floor-breach warning renders on every visit, persists entire session with no dismiss path. If operator is mid-investigation, has drawer open, or already submitted a corrective GR and is waiting, the banner continues to shout. Could persist for days.
- **Proposed fix:** Add dismiss button (X) that suppresses for current session via `useState`. Auto-suppress when `tierFilter === "reconcile"` is active (operator is already in corrective workflow view).
- **Acceptance criterion:** Operator can dismiss. Alert doesn't reappear same session. Absent when Reconcile chip active.

### [FLOW-006] "Show only these →" link and "Reconcile" chip are disconnected in copy
- **Class:** FLOW_COMPLETION
- **Location:** `page.tsx` line 998 (alert button); line 1124 (chip label)
- **Description:** Alert says "click the badge for the offending ledger events" and "Show only these →" links to the Reconcile chip. Two elements reference the same concept with different names. For a first-time operator the mapping is not self-evident.
- **Proposed fix:** Change alert link to "Filter to Reconcile items →" or similar. After click, scroll chip row into view + focus the activated chip.
- **Acceptance criterion:** After clicking the alert link, operator can see which chip was activated. Labels match or alert names the chip explicitly.

### [FLOW-007] "below physical floor" phrasing will not land for factory operators
- **Class:** FLOW_COMPLETION
- **Location:** `page.tsx` line 990 (alert); `StockTruthDrawer.tsx` line 91 (drawer header)
- **Description:** Stock-management term of art from the spec. A factory operator pouring drinks at GT Everyday will not parse "below physical floor" as "we have recorded more outflows than inflows." Not in the standard term lexicon.
- **Proposed fix:** Replace with plain-language equivalent: "More stock recorded as leaving than arriving" or "Outflows exceed recorded receipts by X units." Technical "floor" may be retained inside the drawer's math block (planner/admin-only) but not in operator-visible alert or badge tooltip.
- **Acceptance criterion:** "Floor" does not appear in operator-visible alert copy, badge label, or drawer top-level header.

### [FLOW-008] Drawer CTA opens GR form in a new tab — corrective action breaks drawer context
- **Class:** FLOW_COMPLETION
- **Location:** `StockTruthDrawer.tsx` lines 173–181 (`Link target="_blank"`)
- **Description:** Spec §4.2 point 4 says CTA opens in the same drawer (or new page if form doesn't support drawer mode). Implementation uses new tab. After posting GR in new tab, drawer in original tab has no way to know. Operator must remember to return, close drawer, click Refresh, reopen drawer. Success is silent in original tab.
- **Proposed fix:** Add "I posted the receipt — refresh" button inside drawer that calls `refetch()`. Pure portal change.
- **Acceptance criterion:** After posting corrective GR, operator has clear path to see whether Reconcile badge cleared, without developer knowledge of TanStack cache TTLs.

### [FLOW-009] "Post corrective count (coming soon)" disabled CTA is unacceptable on a daily-use surface
- **Class:** DECISION_GRADE
- **Location:** `StockTruthDrawer.tsx` lines 185–190
- **Description:** When item has no ledger events since anchor, drawer shows disabled button "Post corrective count (coming soon)" with `title="Physical-count form route pending — see follow-up plan."` Developer's internal placeholder visible to operators. Tells the daily operator a feature they need exists but is not ready, with no timeline, no alternative, no actionable next step. `CONTENT_AND_MICROCOPY_GUIDE.md` explicitly forbids empty-action states. MANUFACTURED FG item gone negative with no ledger events leaves operator with zero options.
- **Proposed fix:** Remove disabled "coming soon" button entirely. Replace with prose: "To correct this balance, post a physical count from the Counts section." Include link to `/stock/counts` (or equivalent route).
- **Acceptance criterion:** No "coming soon" text appears on `/inventory` or in the drawer. When corrective-count path is unavailable, surface gives named alternative path.

### [FLOW-010] Ledger event horizon of 10 is insufficient for diagnosing a floor breach
- **Class:** FLOW_COMPLETION
- **Location:** `StockTruthDrawer.tsx` line 29 (`limit=10`)
- **Description:** Spec specifies 10 as default. For a breach accumulated over many events, 10 may not reveal root cause. Backend `LedgerQuerySchema` supports up to 500. `total_matching` is returned but not shown. Operator sees 10 rows with no indication of whether there are 11 or 400 more.
- **Proposed fix:** Show `total_matching` below the ledger table: "Showing 10 of 47 events." Add "View full ledger for this item →" link.
- **Acceptance criterion:** Drawer displays total event count for the item. If >10, navigation link to full ledger is present.

### [FLOW-011] Ledger error state does not gate the CTA
- **Class:** FLOW_COMPLETION
- **Location:** `StockTruthDrawer.tsx` lines 119–130 (error); 172–191 (CTA)
- **Description:** CTA visibility depends on `hasEvents` (data content) rather than load state. If API returns empty rows on error, wrong CTA variant could be shown.
- **Proposed fix:** Gate CTA on `!isError && data !== undefined` in addition to `hasEvents`. When `isError`, hide all CTA variants and show only error block + retry button.
- **Acceptance criterion:** When `isError` is true, no CTA is rendered.

### [FLOW-012] Sort default (alphabetical by name) is suboptimal for daily shift use
- **Class:** POLISH_ACCELERATION
- **Location:** `page.tsx` line 693 — `useState<SortKey>("name")`
- **Description:** Default sort is alphabetical ascending. For a shift operator opening the page at start of day, the most useful default is "lowest stock first" (`on_hand` ascending) or "most recent movement first." Alphabetical is a reference sort, not operational.
- **Proposed fix:** Change default to `on_hand` ascending. Consult Tom first.
- **Acceptance criterion:** On page load, actionable items (lowest stock or most recent) appear at the top.

### [FLOW-013] Sort/filter does not reset on tab switch
- **Class:** POLISH_ACCELERATION
- **Location:** `page.tsx` line 686 — shared state across tabs
- **Description:** Sort state and UOM/family filters persist across FG → RM/PKG switch. A UOM valid for FG may produce zero results in RM/PKG.
- **Proposed fix:** Reset UOM and family filters on tab change; optionally reset sort.
- **Acceptance criterion:** Switching tabs resets UOM and family filter to "All."

### [FLOW-014] Mobile ReconcileBadge touch target risk
- **Class:** FLOW_COMPLETION
- **Location:** `InventoryCardMobile` (lines 491–549)
- **Description:** Badge is ~24px tall (`text-2xs` with `py-0.5`). WCAG/spec minimum 44px. On 390px viewport, badge sits right-adjacent to the item Link. Fat-finger risk: navigation instead of opening drawer.
- **Proposed fix:** Increase badge touch target to 44px minimum via padding. Add ≥8px separation between Link `div` and `OnHandCell` `div`.
- **Acceptance criterion:** Reconcile badge button height ≥44px on mobile. Badge click opens drawer without navigating.

### [FLOW-015] KPI strip loads independently from list — visible state mismatch
- **Class:** POLISH_ACCELERATION
- **Location:** `page.tsx` lines 721–739 (queries); staleTime list=60s, value=300s
- **Description:** Different stale times. On background re-fetch, list refetches while value remains stale up to 5 minutes. Operator sees updated list but KPI value lagging. `as_of` timestamp comes from `valueData.as_of` — can be 5 minutes stale while list is fresh.
- **Proposed fix:** Normalize both to 60s, or derive both from a shared query key.
- **Acceptance criterion:** After refresh or background re-fetch, `as_of` timestamp and list data are synchronized.

### [FLOW-016] Reconcile chip has no count — operator cannot gauge scale before clicking
- **Class:** POLISH_ACCELERATION
- **Location:** `page.tsx` lines 1121–1145
- **Description:** Chips have no counts. `negativeCount` is computed already for the alert. Showing the count on the Reconcile chip (`Reconcile (4)`) lets the operator know the scale without clicking.
- **Proposed fix:** Add count bubble to Reconcile chip using `negativeCount`.
- **Acceptance criterion:** Reconcile chip shows live count of below-floor items when count > 0.

### [FLOW-017] Deploy-time qty blank (trust erosion) — process gap to document
- **Class:** FLOW_COMPLETION
- **Location:** Process, not code — the PR #17 hotfix (`resolveDisplay()`) addresses the rendering, not the deploy coordination
- **Description:** No deploy notification, no maintenance mode, no "data loading" overlay bridged the window between portal deploy and backend deploy. The `? Unknown` tier badge gave no indication that the state was transient. `resolveDisplay()` fallback mitigates future version skew but the process gap remains.
- **Proposed fix:** No code change for the rendering. Operational runbook entry required: "Portal deploys introducing new required backend fields must coordinate with backend deploy within the same maintenance window, or the portal fallback must be clearly labeled as temporary." Route to `factory-os-governor`.
- **Acceptance criterion:** Tom + governor acknowledge the process gap in writing. Deploy runbook entry exists.

### [FLOW-018] `as_of` timestamp is response time, not data freshness
- **Class:** FLOW_COMPLETION (portal-only fix); **ARCH_REQUIRED** (backend-aware variant)
- **Location:** `page.tsx` lines 929–935 (trust strip render); `value-handler.ts` line 100 — `as_of: new Date().toISOString()`
- **Description:** `as_of` is generated at handler call time — it's the API response timestamp, not the last ledger event timestamp. `current_balances` may have last updated hours ago; `as_of` still shows current minute. On cached responses (`staleTime: 300s`) the displayed `as_of` is up to 5 minutes stale while showing the minute of the original fetch.
- **Proposed fix (portal-only):** Rename label from "As of:" to "Fetched at:" — honest about what the timestamp means.
- **ARCH_REQUIRED variant:** Add `max_event_at: string` to `/api/v1/queries/stock/value` response (using `MAX(cb.last_event_at)`). Portal then displays actual data freshness.
- **Acceptance criterion (portal):** Trust strip label does not claim timestamp represents data age unless it actually does. Label reads "Fetched at:" or equivalent.

---

## Summary of class distribution

| Class | Count | IDs |
|---|---|---|
| **DECISION_GRADE_NOW** | 3 | FLOW-002, FLOW-003, FLOW-009 |
| FLOW_COMPLETION_NEXT | 10 | FLOW-001, FLOW-004, FLOW-005, FLOW-006, FLOW-007, FLOW-008, FLOW-010, FLOW-011, FLOW-014, FLOW-017, FLOW-018 (portal-only) |
| POLISH_ACCELERATION_LATER | 4 | FLOW-012, FLOW-013, FLOW-015, FLOW-016 |
| ARCH_REQUIRED | 1 (escalated) | FLOW-018 variant B |

---

## Handoff packet (to portal-production-executor + ux-content-state-designer)

```yaml
handoff_packet:
  surface: /inventory
  audit_date: 2026-05-14
  authored_by: ux-flow-architect
  portal_tip: dc8f514

  decision_grade_now:
    - FLOW-002: Remove "rolled-up nightly" promise from trust strip + Total Inventory Value KPI secondary
    - FLOW-003: Replace "Rolled-up cost pending" badge label with "Cost not set"; change tone info → warning
    - FLOW-009: Remove "Post corrective count (coming soon)" disabled button; replace with prose + link to /stock/counts

  flow_completion_next:
    - FLOW-001: Replace "Source: private_core.current_balances" with plain-English label
    - FLOW-004: Make "Missing cost" chip include pending_rollup items so chip count matches KPI count
    - FLOW-005: Dismissable warning alert (session-level)
    - FLOW-006: Alert link text names the activated chip
    - FLOW-007: Replace "below physical floor" with plain factory-operational language
    - FLOW-008: "Refresh now" button inside drawer after corrective GR
    - FLOW-010: Show total_matching count + "View full ledger →" link in drawer
    - FLOW-011: Gate drawer CTA on !isError && data !== undefined
    - FLOW-014: Reconcile badge mobile touch target ≥ 44px
    - FLOW-017: Deploy coordination runbook (governance, not code)
    - FLOW-018 portal-only: Rename "As of:" → "Fetched at:"

  polish_acceleration_later:
    - FLOW-012: Default sort = on_hand ascending (consult Tom)
    - FLOW-013: Reset filter/sort on tab switch
    - FLOW-015: Normalize list + value staleTime
    - FLOW-016: Add count bubble to Reconcile chip

  arch_required_escalations:
    - FLOW-018 variant B: Add max_event_at to /api/v1/queries/stock/value response
      route_to: factory-os-governor → backend-db-executor

  accessibility_handoff_to: accessibility-usability-auditor
  copy_handoff_to: ux-content-state-designer
  visual_handoff_to: visual-system-designer

  tom_approval_required: yes
  tom_approval_notes: >
    FLOW-002 / FLOW-003 copy changes remove a promise from the trust strip and
    rename a badge. Tom must approve replacement copy before
    portal-production-executor acts.
    FLOW-009 substitute navigation link requires Tom to confirm /stock/counts
    is the correct referral path.
    FLOW-012 sort default change requires Tom preference.

  rollback_plan: >
    All proposed fixes are portal-only React/copy changes with no backend
    contract dependencies (except FLOW-018 variant B which is escalated).
    Each change is independently revertable. No DB migration. No API contract
    change.
```

---

## Escalations

**ARCH_REQUIRED — FLOW-018 variant B — route to `factory-os-governor`:**

The "As of" timestamp could be made honest by returning `MAX(cb.last_event_at)` from the stock value handler. Requires adding `max_event_at: string` to `StockValueResponse` and the `value-handler.ts` query (additive field, no migration). Crosses portal-production-executor allowed-paths boundary.

Governor should evaluate whether this fits in the current sprint. Portal can immediately consume it in the trust strip by replacing `as_of` display with `max_event_at`. Until backend lands, the portal-only fix (relabel "As of:" → "Fetched at:") is the correct interim.

---

## Key findings for Tom, ordered by operational impact

1. **FLOW-002 (DECISION_GRADE):** "Cost rolled-up nightly" is a lie the system tells every operator every day. VALUE (ILS) shows `—` for many FG items not because a job is pending but because no cost has ever been configured. **This is the direct answer to Tom's morning complaint.** Must be corrected before next factory shift.

2. **FLOW-003 (DECISION_GRADE):** Every MANUFACTURED FG row without a supplier cost shows a badge saying "Rolled-up cost pending" — implying the system is working on it. It is not. Every operator who reads this badge will wait. Nothing will happen.

3. **FLOW-009 (DECISION_GRADE):** For items with no ledger events since anchor, the drawer's only CTA is a disabled button saying "coming soon." Worst possible state for a daily-use diagnostic surface. Operator dead-end with no exit.

4. **FLOW-005 + FLOW-008 (FLOW_COMPLETION):** The corrective workflow (open drawer → see ledger → post GR → badge clears) is broken at the post-action step. After posting the GR in a new tab, nothing in the original tab confirms success.

---

## Files read

- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(shared)\inventory\page.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\stock\ReconcileBadge.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\stock\StockTruthDrawer.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\overlays\Drawer.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\lib\stock-display.ts`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\api\stock\value\route.ts`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\api\stock\route.ts`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\api\stock\ledger\route.ts`
- `C:\Users\tomw2\Projects\gt-factory-os\api\src\stock\value-handler.ts`
- `C:\Users\tomw2\Projects\gt-factory-os\api\src\stock\handler.ts`
- `C:\Users\tomw2\Projects\gt-factory-os\api\src\stock\ledger-handler.ts`
- `C:\Users\tomw2\Projects\gt-factory-os\api\src\stock\schemas.ts`
- `PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md`
- `PRODUCTION/docs/phase8/ux/UX_OPERATING_PRINCIPLES.md`
- `PRODUCTION/docs/phase8/ux/CONTENT_AND_MICROCOPY_GUIDE.md`
- `PRODUCTION/docs/phase8/ux/STATUS_EMPTY_ERROR_STATES.md`
