# Dry-Run DR-007 — /operator-task-simulation goods-receipt-with-PO-prefill

**Run date:** 2026-05-08
**Command:** `/operator-task-simulation goods-receipt-with-PO-prefill`
**Run type:** Dry-run (read-only; based on source comments and contract evidence)
**Agent:** ux-flow-architect

---

## operator-task-simulation — Goods Receipt with PO Prefill

### Task definition

- **Operator role:** `operator`
- **Entry point:** Planner sends operator a link `/stock/receipts?po_id=<po_id>` OR operator navigates from PO detail page.
- **Goal:** Record that goods from a specific PO have arrived and been counted.
- **Expected terminal state:** Stock ledger has a GR event for the delivered quantities; PO status updated to PARTIAL or RECEIVED; operator has confirmation of what was posted.

---

### Step-by-step trace (from source comment evidence)

| Step | UI element | Data needed | Data available | Gap |
|---|---|---|---|---|
| 1. Arrive at GR form via `?po_id=` link | Goods Receipt form | PO header + open lines | Fetched on mount per source comment | PASS |
| 2. Supplier picker is locked | Supplier display (read-only) | Supplier name from PO | Locked per source comment | PASS |
| 3. Lines pre-filled from PO | GR line rows | Component/item, open_qty → received_qty | Pre-populated from PO lines (OPEN/PARTIAL) per §3.4.1 | PASS |
| 4. Operator adjusts quantities | Input fields | Actual received quantities | Editable downward or upward per §3.4.3 | PASS |
| 5. Operator submits | Submit button | All line data + PO reference | Posted to `/api/v1/mutations/goods-receipts` | UNKNOWN — post-submit state not confirmed |
| 6. Post-action: What happened? | ??? | Posted quantities, PO status update | NOT CONFIRMED | FLOW-001 (from DR-004) |
| 7. Operator finds the receipt | ??? | Link to PO detail or receipts list | Not confirmed from source analysis | FLOW-001 continuation |

---

### PO status edge cases (from source comments)

| PO status at arrival | Behavior | Operator-visible? |
|---|---|---|
| OPEN | Normal prefill | YES |
| PARTIAL | Normal prefill (remaining open qty) | YES |
| RECEIVED | Empty-state panel + "View receipts" link | YES (good) |
| CANCELLED | Empty-state panel | YES — what's the message? |

**Finding FLOW-007:** Cancelled PO empty state — what does the operator see?
- The source comment says "PO is RECEIVED/CANCELLED shows empty-state panel with a 'View receipts' link." But RECEIVED and CANCELLED are different states. A CANCELLED PO has no receipts to view. "View receipts" link is misleading on a CANCELLED PO.
- **Proposed fix:** For CANCELLED PO: show "This purchase order has been cancelled. No goods receipt can be recorded. Contact your planner if you believe this is an error."
- **Class:** FLOW_COMPLETION (P1).

---

### Manual intervention points

| Step | Manual intervention required? | Note |
|---|---|---|
| Getting the `?po_id=` link | Planner must send or operator must navigate to PO list first | Reasonable — PO list exists |
| Finding the receipt after submit | UNKNOWN | If no clear post-submit link, operator must search |
| Verifying PO status updated | UNKNOWN | Does the operator see PO status change? |

**Gap:** Step 6-7 (post-submit confirmation and audit trail navigation) is the primary gap. The prefill path is well-implemented but the landing zone after a successful submission is unknown from static analysis.

---

### Post-action visibility

| After completing task | Operator sees | Finding |
|---|---|---|
| Success state | NOT CONFIRMED | FLOW-001 |
| Link to posted GR | NOT CONFIRMED | FLOW-001 continuation |
| PO status updated | NOT CONFIRMED | New finding FLOW-007 continuation |
| "Record another receipt" | NOT CONFIRMED | — |

---

### Simulation findings

| ID | Stage | Description | Class |
|----|-------|-------------|-------|
| FLOW-001 | Terminal action / post-action | Post-submit confirmation and navigation destination | FLOW_COMPLETION (P1) |
| FLOW-007 | Entry | Cancelled PO empty state shows "View receipts" link incorrectly | FLOW_COMPLETION (P1) |

---

### Summary

The PO-prefill path is well-designed for the steps that were confirmed in source comments:
- Supplier lock, line prefill, quantity editability. These are correct.
- The PO status guard (RECEIVED/CANCELLED) shows an empty-state — good.

The remaining gap is the post-submission experience (FLOW-001, FLOW-007). These require
a full source read to confirm whether they are actual gaps or already implemented.

---

**DRY-RUN STATUS: PARTIAL (static analysis + source comment evidence)**
**P0 confirmed: 0**
**P1 candidates: 2 (FLOW-001 continuation, FLOW-007)**
**Manual verification required:** full read of GR form submit handler and post-submit state
