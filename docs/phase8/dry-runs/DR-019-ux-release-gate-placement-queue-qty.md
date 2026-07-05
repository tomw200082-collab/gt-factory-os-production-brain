# DR-019 — /ux-release-gate: placement-queue quantity editing

Date: 2026-07-05
Invoked by: Tom (interactive session), following a direct request to review and
improve `/purchase-orders/placement-queue` and make the line quantity editable.
Scope: `/purchase-orders/placement-queue` (office-manager "orders to place"
screen) plus its downstream data-flow touchpoints (`/purchase-orders/[po_id]`
detail page, `/stock/receipts`).
Context: PR `tomw200082-collab/gt-factory-os-portal#164` (draft, unmerged),
branch `claude/accounts-orders-screen-ux-pdpbfc`. The PR adds an editable
per-line quantity input to `PlacementRow.tsx` — previously read-only text —
wired to the existing but previously-unused `line_qty_overrides` API field.

## Method

All five UX agents audited the surface in parallel (code read + one live
render via `tests/e2e/ux-shot.spec.ts` for the visual/accessibility passes).
The orchestrating session independently re-verified the highest-severity
claims against source and a live render before compiling this report —
verification notes are inline below. `factory-os-governor` issued the formal
verdict.

## Top-N ranked actions (the deliverable)

| # | Sev | Effort | Dimension | Route | Finding | Proposed fix | Evidence |
|---|-----|--------|-----------|-------|---------|--------------|----------|
| 1 | P0 | S | Interaction | placement-queue | Confirm dialog before the irreversible "place order" action never discloses that a line quantity was changed from the planner's approved value, or by how much | Add a disclosure line to the confirm description when `line_qty_overrides.length > 0`, naming the changed line(s) and old→new qty | `PlacementRow.tsx:131-146` (verified) |
| 2 | P0 | S | Interaction | placement-queue | Per-line quantity validation error is unreachable dead code (`canPlace` already disables the button first); no inline per-field error; disabled-button tooltip predates the qty field and never mentions it | Add inline per-field qty error (or remove the dead branch) and update the tooltip to mention quantity | `PlacementRow.tsx:85-88,120-130,266-284,429` (verified) |
| 3 | P1 | S | Flow | `/purchase-orders/[po_id]` | `POStatusBadge` has no case for `APPROVED_TO_ORDER` — falls through to rendering the raw enum string as visible badge text | Add an explicit case, same pattern as the other 4 statuses | `page.tsx:224-232` (verified — same violation class as 3 bugs fixed in tranche 127) |
| 4 | P1 | S | Copy + Interaction | placement-queue | Disabled-button tooltip and confirm-dialog qty-change warning are stale/inaccurate: tooltip omits quantity; the "changes require supplier coordination" sentence fires even when no quantity changed | Update tooltip text; gate the warning sentence on `line_qty_overrides.length > 0` | `PlacementRow.tsx:142,429` (2 agents, consistent) |
| 5 | P1 | S | Interaction | placement-queue | Price / payment-terms / ETA-date `onChange` handlers don't clear the error banner; only the new qty field's handler does — inconsistent | Add `setErrorMsg(null)` to the other three `onChange` handlers | `PlacementRow.tsx:296-300,353-354,371-374` |
| 6 | P1 | S | Interaction | placement-queue | Form inputs remain editable while the place mutation is in flight; only the submit button is locked | Add `disabled={placeMut.isPending}` to qty/price/terms/date inputs | `PlacementRow.tsx:266,289,348,367` |
| 7 | P1 | S | Flow | placement-queue | Page-level "order placed" success banner is single-slot state — placing a second PO in the same session silently overwrites the first PO's confirmation | Make `placed` an array/list, or a small toast stack | `page.tsx:38-41,167-169` |
| 8 | P1 | S | Flow | placement-queue | After a network timeout during placement, the generic Hebrew failure message gives no guidance to check whether the order actually went through | Add a hint to refresh/check the PO list on failure | `_lib/api.ts:157-191` |
| 9 | P1 | S | Accessibility | placement-queue | Quantity input gets no `aria-invalid`/`aria-describedby` on error — a screen-reader user gets no field-level indication (the live-region announcement does fire) | Add per-line error state; wire `aria-invalid` + `aria-describedby` | `PlacementRow.tsx:266-283,370-386` |
| 10 | P1 | M | Interaction (escalation, downgraded) | placement-queue | Portal cannot enforce integer-only quantities for count UOMs (UNIT/PCS/BOX/CASE/BOTTLE/TIN) | **Downgraded from the auditing agent's P0/ARCH_REQUIRED call** — verified the UOM name itself is a reliable static heuristic (UNIT/PCS/BOX/CASE/BOTTLE/TIN are inherently countable; KG/L/G/MG/TON/ML/BAG are continuous). Portal-only static lookup map; no backend field needed | `src/lib/contracts/enums.ts:65-78` (verified) |
| 11 | P1 | M | Visual | placement-queue | Line-list layout has no fixed column alignment between qty/price inputs across rows once a line has two numeric inputs instead of one; item-name length can shift the columns | Bounded `flex-1 truncate` name column + `flex-none` fixed-width trailing input group | `PlacementRow.tsx:254-307` |
| 12 | P1 | S | Visual | placement-queue | Two different label-weight recipes inside one expanded card (line-item labels lighter/smaller than ETA/terms labels) | Adopt one label recipe throughout the card | `PlacementRow.tsx:265,287,344-346,363-365` |
| 13 | P2 | S | Visual | placement-queue | Numeric/date inputs inherit `dir="rtl"` without an explicit override; ambiguous cursor/date-picker direction | Add `dir="ltr"` to the three inputs | `PlacementRow.tsx:266-281,288-304,348-356` |
| 14 | P2 | M | Flow | placement-queue | No visibility into who approved a PO / when / from which planning session (ARCH_REQUIRED — no such field exists on the PO type) | Backend field addition — out of portal scope, route to `backend-db-executor` if prioritized | `_lib/api.ts:15-30` (`QueuePo` type) |
| 15 | P2 | S | Flow | placement-queue | A stale pre-loaded ETA (past date, from a PO that sat in the queue a while) shows no warning before placement | Compare `confirmedDate` to today and surface a soft warning if already past | `PlacementRow.tsx:59-61,353` |

*(Full per-dimension finding sets, including additional P2 polish items — VISUAL-005/006/007/008, COPY-003, INTER-007, A11Y-203/204 — are in the per-dimension audit trail below; omitted from the Top-15 for brevity, none are blocking.)*

## Findings excluded after verification

- **VISUAL-002** (agent claim: primary "place order" button's `justify-end` placement is an RTL-convention violation). **NOT CONFIRMED.** Checked the sibling `FocusCard.tsx` in the same procurement domain (also Hebrew/RTL): it uses the identical convention (`justify-between`, primary actions group landing on the physical left). This is an established, deliberate pattern in this codebase, not a bug. Excluded from the ranked list.

## P0 findings (all dimensions) — block ship

| ID | Dimension | Route | Description |
|---|---|---|---|
| INTER-001 | Interaction | placement-queue | Confirm dialog doesn't disclose quantity overrides before an irreversible place action |
| INTER-002 | Interaction | placement-queue | Per-field qty validation unreachable; no inline error; stale tooltip |

## P1 findings — conditional-ship items

FLOW-PQ-01, COPY-001/002, INTER-003/004/005, FLOW-PQ-04, FLOW-PQ-05, A11Y-202, INTER-006 (downgraded, portal-only), VISUAL-001, VISUAL-003 — see ranked list above.

## Per-dimension status

| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 0 | 4 | AMBER |
| Interaction | 2 | 4 | RED |
| Visual | 0 | 2 | AMBER |
| Copy | 0 | 2 | AMBER |
| Accessibility | 0 | 1 | AMBER |

## portal_ux_standard.md compliance

PASS. `ux-content-state-designer` confirmed the two copy findings (COPY-001/002)
are applications of the existing §3 rules (actionable error copy, accurate
confirmation copy) to the new quantity field — not gaps in the standard
itself. No standard updates proposed.

## Verdict

**HOLD** (factory-os-governor, 2026-07-05)

Rule applied: any P0 finding → HOLD. Both confirmed P0s live in the
newly-added quantity-editing code path on an unmerged draft PR. The action
gated (placing a real order with a possibly-silently-changed quantity) is
irreversible-adjacent and touches a Hebrew/RTL bookkeeper surface explicitly
authorized in CLAUDE.md — extra care is warranted here, not less. No
frozen-flag risk, no locked-decision violation, correct lane (portal-only).

## Blockers

- **INTER-001**: `PlacementRow.tsx` confirm dialog — add a disclosure line
  naming the changed line(s) and old→new quantity when `line_qty_overrides`
  is non-empty.
- **INTER-002**: Either add inline per-field qty error + update the
  disabled-button tooltip to mention quantity, or remove the now-dead
  validation branch in `handlePlace` and rely solely on `canPlace` + inline
  error — do not ship both a dead code path and a missing UI signal.

## Tom approval required?

No, for the fix itself — a portal-only follow-up commit on this same
unmerged draft PR, within `portal-production-executor`'s lane; no frozen
flags, no schema, no external writes. Tom approval **would** be needed to
override this HOLD and request review as-is.

## Next action for Tom

Authorize a follow-up commit on PR #164 that closes INTER-001 and INTER-002
(and, opportunistically, the P1 duplicates in the same file — COPY-001/002,
INTER-003/004/005, FLOW-PQ-01) before flipping the PR from draft to
review-ready. The remaining P1/P2 items (visual column alignment, the
integer-UOM heuristic, the multi-PO banner, ARCH_REQUIRED approval audit
trail, etc.) are recommended for a dedicated follow-on visual + UX pass, as
originally requested — not blocking this PR.
