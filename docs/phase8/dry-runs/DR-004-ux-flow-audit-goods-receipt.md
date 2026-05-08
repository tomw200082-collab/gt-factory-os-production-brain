# Dry-Run DR-004 — /ux-flow-audit /(ops)/stock/receipts

**Run date:** 2026-05-08
**Command:** `/ux-flow-audit /(ops)/stock/receipts`
**Run type:** Dry-run (read-only; static analysis of portal source)
**Agent:** ux-flow-architect

---

## ux-flow-architect audit — Goods Receipt

### Surface audited
- Route: `/(ops)/stock/receipts` (portal: `src/app/(ops)/stock/receipts/page.tsx`)
- RUNTIME_READY signal: `GoodsReceipt-FromPO` (#35), emitted 2026-05-02T19:30:00Z
- Portal tip at audit: `9605553`

### Contracts inspected
- `GoodsReceipt-FromPO` signal evidence: `Projects/gt-factory-os/docs/goods_receipt_frompo_checkpoint.md` — referenced, not read in this dry-run
- `portal_ux_standard.md` — §1, §3, §4 read

### Static analysis basis
Read: `src/app/(ops)/stock/receipts/page.tsx` (first 100 lines).
Component is `"use client"`, uses TanStack Query, WorkflowHeader, SectionCard components.
Supports PO prefill via `?po_id=` URL param. PO-less entry preserved.

---

### Flow coverage

| Flow stage | Status | Finding |
|---|---|---|
| Entry / context | PARTIAL | PO prefill path provides context (supplier locked, lines pre-filled). Direct-entry path has no "why are you here" context — just an empty form. |
| Processing / state | PASS | Client component with TanStack Query. Loading/empty states referenced in code comments (PO RECEIVED/CANCELLED shows empty-state panel). Needs verification of chip gating. |
| Review / decision | UNKNOWN | Cannot confirm from header alone whether a review step exists before submit. Full read of submit flow needed. |
| Terminal action | PARTIAL | Submit posts to `/api/v1/mutations/goods-receipts`. Post-action confirmation behavior not confirmed from header. |
| Post-action visibility | NOT_CONFIRMED | Where does the operator go after a successful receipt? Receipts list? PO detail? Not visible from header. |
| Auditability | NOT_CONFIRMED | Is the submitted GR accessible from the PO detail or a receipts list? Code comments reference a "View receipts" link on closed PO — this suggests auditability exists but needs full audit. |
| Recovery / error | PARTIAL | PO status guard exists (RECEIVED/CANCELLED shows message). General submit error recovery not confirmed. |

---

### Findings

#### [FLOW-001] Post-action destination unclear from static analysis
- **Class:** FLOW_COMPLETION (P1 candidate — needs full read to confirm P0 vs P1)
- **Location:** `src/app/(ops)/stock/receipts/page.tsx`
- **Description:** After a successful GR submission, the destination is not clear from the header. The operator may be left at a blank or reset form without confirmation of what was posted and where to find it.
- **Proposed fix:** After successful submit, show a success banner with: (a) what was posted — "X units of [Product] posted to stock", (b) a link to the receipts list or PO detail, (c) a "Record another receipt" CTA.
- **Acceptance criterion:** After a successful GR, operator sees a success state naming the product/quantity posted and can navigate to the audit trail without using the back button.
- **Full read required:** yes — this is a PARTIAL finding pending full source read.

#### [FLOW-002] Direct-entry path has no entry context
- **Class:** FLOW_COMPLETION (P1)
- **Location:** `src/app/(ops)/stock/receipts/page.tsx`
- **Description:** When no `?po_id=` param is present, the operator arrives at a blank goods receipt form. There is no context about what they are receiving, no date pre-filled, and no indication of open deliveries expected.
- **Proposed fix:** On direct entry, consider showing a "Expected deliveries today" sidebar or a note linking to the PO list for context. At minimum, pre-fill the date field with today.
- **Acceptance criterion:** Direct-entry GR shows today's date pre-filled and a prompt pointing the operator to the PO list if they have a related PO.
- **Architecture note:** If "expected deliveries" requires a backend endpoint not yet in the contract, this is ARCH_REQUIRED.

---

### Handoff packet (draft — pending full source audit)

```yaml
handoff_packet:
  surface: /(ops)/stock/receipts
  audit_date: 2026-05-08
  authored_by: ux-flow-architect
  status: DRAFT — partial (static analysis only; full read pending)
  portal_tip: 9605553
  contracts_inspected:
    - runtime_ready.json signal GoodsReceipt-FromPO (#35)
    - portal_ux_standard.md §1, §3, §4
  findings:
    - id: FLOW-001
      class: FLOW_COMPLETION
      description: Post-action destination after GR submit unclear
      proposed_fix: Success banner with product/quantity + link to audit trail
      acceptance_criterion: Operator sees what was posted and can navigate to it
    - id: FLOW-002
      class: FLOW_COMPLETION
      description: Direct-entry path has no contextual entry frame
      proposed_fix: Pre-fill date; suggest PO list for context
  states_covered: [loading (assumed), error (assumed), empty (PO status guard confirmed)]
  full_read_required: yes
  tom_approval_required: no (P1 findings only pending full audit)
```

### Escalations
None from this dry-run. FLOW-002 may become ARCH_REQUIRED if "expected deliveries" endpoint does not exist — needs contract check.

---

**DRY-RUN STATUS: PARTIAL (static analysis; full source read needed for complete audit)**
**P0 findings confirmed: 0** (no P0 confirmed from header; full read required)
**P1 findings: 2 (FLOW-001, FLOW-002 — both pending confirmation)**
