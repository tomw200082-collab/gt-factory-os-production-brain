# Dry-Run DR-006 — /ux-flow-audit /(ops)/waste-adjustment + physical-count

**Run date:** 2026-05-08
**Command:** `/ux-flow-audit /(ops)/stock/waste-adjustments` and `/(ops)/stock/physical-count`
**Run type:** Dry-run (read-only; structural inspection)
**Agent:** ux-flow-architect

---

## ux-flow-architect audit — Waste Adjustment + Physical Count (combined)

### Surfaces audited
- `/(ops)/stock/waste-adjustments` (RUNTIME_READY #1, 2026-04-17T16:54:13Z)
- `/(ops)/stock/physical-count` (RUNTIME_READY #2, 2026-04-17T19:21:41Z)

Both are among the earliest RUNTIME_READY signals and may have the most drift vs. current portal standards.

### Contracts inspected
- `portal_ux_standard.md` §3 (state hygiene) — read
- Signal evidence notes from `runtime_ready.json` — read

---

## Waste Adjustment

### Flow coverage

| Flow stage | Status | Finding |
|---|---|---|
| Entry / context | UNKNOWN | Route exists (`waste-adjustments/`). Entry context unknown from header read. |
| Processing / state | UNKNOWN | TanStack Query expected. State coverage not confirmed. |
| Review / decision | CRITICAL QUESTION | Positive adjustments require stronger control per CLAUDE.md. Is the "positive adjustment" path visually distinct from waste? |
| Terminal action | UNKNOWN | Submit destination not confirmed. |
| Post-action visibility | UNKNOWN | — |
| Auditability | PARTIAL | Submissions list exists at `/(ops)/stock/submissions`. |
| Recovery | UNKNOWN | Approval flow for large discrepancies exists per CLAUDE.md. Visible in UI? |

### Findings

#### [FLOW-005] Positive adjustment approval path visibility unclear
- **Class:** DECISION_GRADE (P0 candidate)
- **Location:** `/(ops)/stock/waste-adjustments`
- **Description:** CLAUDE.md §Waste/Adjustment states "Positive 'found stock' adjustments require stronger control." It is unknown from structural analysis whether the operator-facing form makes this distinction visually and contextually clear. If a positive adjustment silently goes to an approval queue without telling the operator, this is a flow gap.
- **Proposed fix:** Positive adjustments must explicitly tell the operator: (a) this goes for approval, (b) what happens next, (c) who approves it.
- **Acceptance criterion:** Operator submitting a positive adjustment sees a clear message that their adjustment is pending approval and knows who will approve it.
- **Full source read required:** yes.

---

## Physical Count

### Flow coverage

| Flow stage | Status | Finding |
|---|---|---|
| Entry / context | STRONG (by contract) | Blind count — snapshot quantity hidden. Known good design per RUNTIME_READY #2 evidence. |
| Processing / state | KNOWN GOOD (by contract) | 31/31 pgTAP green; 18 HTTP cases verified. State coverage extensive. |
| Review / decision | STRONG | Operator submits count; delta computed; auto-post for small discrepancies; approval required for large. |
| Terminal action | STRONG | Auto-post path and approval-pending path both exist per signal evidence. |
| Post-action visibility | UNKNOWN | After approval or auto-post, does the operator see what was posted? |
| Auditability | PARTIAL | Count history expected. Confirmed by anchor history reference in signal evidence. |
| Recovery | GOOD (by contract) | Count freeze prevents concurrent counts. |

### Findings

#### [FLOW-006] Post-count visibility — operator does not know if approved
- **Class:** FLOW_COMPLETION (P1)
- **Location:** `/(ops)/stock/physical-count`
- **Description:** After submitting a count that goes to approval, the operator likely sees a "pending" status. But do they know when it is approved? Is there a notification or a status update they can check without asking a planner?
- **Proposed fix:** Count submission result should show: "Your count has been submitted. [If auto-posted: posted to stock — view result. If pending: awaiting approval by your planner — check back here.]" A status page showing all pending counts would serve this need.
- **Acceptance criterion:** Operator who submitted a count-for-approval can check its status in the portal without asking a planner.

---

### Combined handoff packet

```yaml
handoff_packet:
  surfaces: [/(ops)/stock/waste-adjustments, /(ops)/stock/physical-count]
  audit_date: 2026-05-08
  authored_by: ux-flow-architect
  status: DRAFT — structural analysis only
  portal_tip: 9605553
  findings:
    - id: FLOW-005
      class: DECISION_GRADE (P0 candidate)
      surface: waste-adjustments
      description: Positive adjustment approval path visibility unclear
      full_read_required: yes
    - id: FLOW-006
      class: FLOW_COMPLETION (P1)
      surface: physical-count
      description: Post-count status visibility for operator after pending-approval submission
```

---

**DRY-RUN STATUS: STRUCTURAL ANALYSIS (full source read needed for both surfaces)**
**P0 candidates: 1 (FLOW-005 — waste adjustment positive path)**
**P1 findings: 1 (FLOW-006 — count approval visibility)**
