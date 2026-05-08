# Dry-Run DR-005 — /ux-flow-audit /planning/blockers

**Run date:** 2026-05-08
**Command:** `/ux-flow-audit /planning/blockers`
**Run type:** Dry-run (read-only; static analysis of portal source)
**Agent:** ux-flow-architect + ux-content-state-designer (Hebrew audit)

---

## ux-flow-architect audit — Planning Blockers

### Surface audited
- Route: `/planning/blockers` (portal: `src/app/(planning)/planning/blockers/page.tsx`)
- RUNTIME_READY signal: `Planning-Tranche3-Blockers` (#17), emitted 2026-04-27
- Portal tip at audit: `9605553`

### Contracts inspected
- `portal_ux_standard.md` §1 (language), §3 (state hygiene) — read
- Page source header — read

---

### CRITICAL FINDING — Hebrew register confirmed as Tom-locked

The `/planning/blockers` page has a Tom-locked Hebrew register explicitly documented in the source:

```
// Tom-locked 2026-04-27:
//   route        = /planning/blockers
//   page title   = "חסמים בתכנון"
//   subtitle     = "פריטים עם ביקוש שלא הפכו להמלצת רכש או ייצור שמישה"
//
// 5-question UX (Tom verbatim) — every row answers:
//   1. מה חסום?         (display_name; never UUID)
//   2. למה זה חסום?      (Hebrew blocker_label)
//   3. מה הסיכון?       (severity tone + demand_qty + earliest_shortage_at)
//   4. מה עושים עכשיו?  (Hebrew fix_action_label)
//   5. איפה מתקנים?     (fix_route link OR "פנה למפתח" when null)
```

**Assessment:** This is NOT a P0 Hebrew violation. Tom has explicitly pinned a Hebrew register for this surface. The copy is authoritative per Tom's direct instruction (2026-04-27). The `ux-content-state-designer` should record this register in the copy guide and `portal_language_direction_audit.md` if not already there.

---

### Flow coverage

| Flow stage | Status | Finding |
|---|---|---|
| Entry / context | PASS | The 5-question UX framework provides strong context: what is blocked, why, risk, fix action, fix location. |
| Processing / state | CONFIRMED (partial) | Code references `BlockersEmptyAllClear`, `BlockersEmptyNoRunYet`, `BlockersErrorBanner`, `BlockersFilteredEmpty`, `BlockersLoadingSkeleton` — all five state variants exist. This is exemplary. |
| Review / decision | PASS | Severity tone + demand_qty + earliest_shortage_at gives decision context. |
| Terminal action | FLOW_COMPLETION | Fix action routes to `fix_route` link or shows "פנה למפתח" (contact developer). The "contact developer" path is an operator-visible dead-end — a planner/admin should be the contact, not a developer. |
| Post-action visibility | NOT_CONFIRMED | After following a fix link, does the planner return to the blockers list? Is the blocker resolved automatically or manually? |
| Auditability | NOT_CONFIRMED | Is there a resolved-blockers history? Not confirmed from header. |
| Recovery / error | CONFIRMED | `BlockersErrorBanner` component exists. |

---

### Findings

#### [FLOW-003] "Contact developer" as a terminal action for a planner
- **Class:** DECISION_GRADE (P0 candidate)
- **Location:** `/planning/blockers` page — `fix_action_label` "פנה למפתח" when `fix_route` is null
- **Description:** When a blocker has no automated fix route, the system tells the planner to "contact the developer." This is a dead-end: the planner cannot act, and developers are not the right party. The planner or admin should be directed to contact Tom or perform the master-data fix manually.
- **Proposed fix:** Replace "פנה למפתח" with "עדכן נתוני אב" (Update master data) with a link to the relevant admin screen, or "פנה למנהל" (Contact administrator) with a named contact or admin route. The developer path should not be visible to planners.
- **Acceptance criterion:** No operator or planner sees "contact developer" in the portal. If no fix route exists, the fix guidance names an admin action or contact.
- **Architecture note:** If the `fix_route` field on the blocker DTO cannot be populated for some blocker types, this may require backend contract extension (ARCH_REQUIRED). Check blocker DTO.
- **Tom review required:** yes — Hebrew copy change.

#### [FLOW-004] Post-fix state unclear: does the blocker disappear after fix?
- **Class:** FLOW_COMPLETION (P1)
- **Location:** `/planning/blockers` page — post-fix flow
- **Description:** After a planner navigates to the fix route and resolves the issue, does the blocker list update automatically? Or must the planner re-run planning to see the blocker disappear? The current UX does not make this clear.
- **Proposed fix:** After returning from a fix route, the blockers list should refresh. If a planning re-run is required before the blocker clears, display a notice: "Re-run planning to confirm this blocker is resolved."
- **Acceptance criterion:** Planner knows whether the blocker is cleared after a fix action without having to ask.

---

### ux-content-state-designer note

The Hebrew copy on this surface is Tom-locked and correct per the source comment. However:
1. This register should be formally recorded in `portal_language_direction_audit.md` if not already present.
2. The "פנה למפתח" copy is the only item that needs review (FLOW-003 above).
3. The 5-question UX framework in Hebrew is exemplary and should be referenced in the `OPERATIONAL_FLOW_MAP.md` as a positive pattern.

---

### Handoff packet

```yaml
handoff_packet:
  surface: /planning/blockers
  audit_date: 2026-05-08
  authored_by: ux-flow-architect
  status: DRAFT — partial (static analysis only)
  portal_tip: 9605553
  hebrew_register: Tom-locked 2026-04-27 — confirmed in source comment
  findings:
    - id: FLOW-003
      class: DECISION_GRADE
      severity: P0 candidate
      description: '"Contact developer" terminal action visible to planner'
      proposed_fix: Replace with admin action or planner contact guidance
      tom_approval_required: yes (Hebrew copy change)
    - id: FLOW-004
      class: FLOW_COMPLETION
      severity: P1
      description: Post-fix state ambiguous; planner does not know if re-run needed
  copy_handoff_to: ux-content-state-designer (FLOW-003 Hebrew copy)
  arch_required: FLOW-003 may need DTO extension if fix_route is always null for some blocker types
```

### Escalations

- FLOW-003 may be ARCH_REQUIRED if the blocker DTO cannot carry a fix_route for certain types. Route to `factory-os-governor` after blocker DTO is read.

---

**DRY-RUN STATUS: PARTIAL (static analysis)**
**P0 candidates: 1 (FLOW-003 — needs full read to confirm; Tom approval required for Hebrew copy change)**
**P1 findings: 1 (FLOW-004)**
