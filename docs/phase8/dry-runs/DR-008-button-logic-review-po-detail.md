# Dry-Run DR-008 — /button-logic-review /purchase-orders/[po_id]

**Run date:** 2026-05-08
**Command:** `/button-logic-review /purchase-orders/[po_id]`
**Run type:** Dry-run (read-only; static analysis of portal source header)
**Agent:** interaction-design-specialist

---

## button-logic-review — Purchase Orders Detail (/purchase-orders/[po_id])

### Surface audited
- Route: `/purchase-orders/[po_id]`
- File: `src/app/(po)/purchase-orders/[po_id]/page.tsx`
- RUNTIME_READY signal: `PurchaseOrders` (#8), `PurchaseOrders-manual` (#13)
- Portal tip at audit: `9605553`

### Structure confirmed
- Client component (`"use client"`)
- Uses `useMutation`, `useQueryClient`, `useRouter` — mutations are present
- Tabbed layout: lines, overview, source-recommendation, attached-grs, history
- Status badge: OPEN | PARTIAL | RECEIVED | CANCELLED
- Has source_type and manual_reason fields (manual PO support)

---

### Action completeness matrix (from structural analysis)

Actions on a PO detail page are expected to include:
- Close/Cancel PO
- Record Goods Receipt (link to GR form with PO prefill)
- Edit lines (for OPEN POs)
- View source recommendation (read-only link)
- View attached GRs (read-only tab)

| Action | Disabled state | Loading state | Destructive | Irreversible | Confirmation | Post-action | Error state | Finding |
|---|---|---|---|---|---|---|---|---|
| Close/Cancel PO | ? | ? | YES | YES | ? | ? | ? | INTER-001 — FULL READ REQUIRED |
| Record GR (link) | ? | N/A | NO | NO | N/A | N/A | N/A | INTER-002 (candidate) |
| Edit PO lines | ? | ? | MEDIUM | NO | ? | ? | ? | Needs full read |
| View rec link | N/A | N/A | NO | NO | N/A | N/A | N/A | — |

---

### Findings

#### [INTER-001] Cancel PO — confirmation completeness unknown from header
- **Class:** DECISION_GRADE (P0 candidate — Cancel PO is irreversible per status model)
- **Location:** `src/app/(po)/purchase-orders/[po_id]/page.tsx`
- **Description:** The PO detail page uses `useMutation` (mutations are present). Cancel/Close PO is a consequential or irreversible action (CANCELLED status appears in the status badge type). From the header alone, it is unknown whether:
  (a) a confirmation dialog exists before Cancel PO,
  (b) the dialog names the PO number and states the consequence,
  (c) the cancel button uses `variant="destructive"`.
- **Proposed fix (if confirmation is missing):** Add a confirmation dialog: "Cancel Purchase Order PO-[number]? This will close the order. Any pending lines will not be received. This action cannot be undone."
- **Acceptance criterion:** The Cancel PO action shows a confirmation dialog that names the PO number, states the consequence, and uses `variant="destructive"` on the confirm button.
- **Full source read required:** YES.

#### [INTER-002] Record Goods Receipt link — context injection unclear
- **Class:** FLOW_COMPLETION (P1)
- **Location:** PO detail — action area or attached-grs tab
- **Description:** There should be a prominent "Record Goods Receipt" action on an OPEN or PARTIAL PO. Whether this link injects `?po_id=` into the GR form URL (enabling prefill) is unknown from the header. If the link goes to a blank GR form, the prefill path from DR-004 is never discoverable.
- **Proposed fix:** "Record Goods Receipt" action on OPEN/PARTIAL POs should link to `/stock/receipts?po_id=<po_id>`.
- **Acceptance criterion:** Clicking "Record Goods Receipt" from the PO detail pre-fills the supplier and PO lines in the GR form.

---

### ux-content-state-designer coordination

From the PO detail source:
- `status: string` — raw status from API. Display must map to standard terms (Open, Partial, Received, Cancelled) per CONTENT_AND_MICROCOPY_GUIDE.md.
- `StatusBadge` component used — needs to be verified to use standard display terms.
- `source_type` field: must NOT appear as raw text to operator. Must be mapped to display string or hidden.

---

### Handoff packet

```yaml
handoff_packet:
  surface: /purchase-orders/[po_id]
  audit_date: 2026-05-08
  authored_by: interaction-design-specialist
  status: DRAFT — header analysis only; full read required
  portal_tip: 9605553
  action_review:
    - action: Cancel / Close PO
      destructive: yes
      irreversible: yes
      confirmation: UNKNOWN — full read required
      finding_id: INTER-001
    - action: Record Goods Receipt
      destructive: no
      irreversible: no
      context_injection: UNKNOWN — full read required
      finding_id: INTER-002
  copy_coordination:
    - status field display (must map raw enum to standard terms)
    - source_type field (must not render raw to operator)
  a11y_coordination:
    - StatusBadge — verify text + color (not color-only)
    - useMutation buttons — verify accessible names
  tom_approval_required: no (findings are P0 candidate and P1; full read decides P0 vs P1)
```

---

**DRY-RUN STATUS: HEADER ANALYSIS (full source read required for INTER-001 P0 confirmation)**
**P0 candidates: 1 (INTER-001 — Cancel PO confirmation completeness)**
**P1 candidates: 1 (INTER-002 — GR link context injection)**
