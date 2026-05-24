# GT Factory OS — Inventory / Production Operator Form UX Audit
**Date:** 2026-05-24
**Branch:** `claude/inventory-forms-audit-ux-JFRdj` (portal + backend + brain)
**Scope:** every operator/planner/admin form and surface that touches inventory truth, purchasing, receipts, waste/adjustments, physical counts, and production actuals — plus shared approval / inbox / form-system surfaces.
**Method:** read-only multi-agent audit (8 parallel tracks) → master report → safe surgical implementation loops.
**Authority:** working audit doc following the `overnight_audit_*.md` / `cleanup_audit_*.md` pattern. Not an authority doc. Does not relax any locked decision.

---

## 1. Executive summary

### Safe today
- **Contract grounding is solid.** All five operator forms (PO manual create + cancel, Goods Receipt, Waste/Adjustment, Physical Count, Production Actual) consume real, frozen backend contracts. No invented enums, fields, statuses, or reason codes were found. Conflict reasons in UI match `api/src/*/schemas.ts` verbatim (Agent 1).
- **Sanctioned write paths are in place.** All four stock-affecting flows route through `private_core.stock_ledger` inserts inside single backend transactions, with `form_submissions.idempotency_key` UNIQUE enforcement and replay markers. Physical Count is anchor-first via `replace_anchor()`; no ledger row is written for counts (Agent 3).
- **Pending vs posted is enforced at the data layer.** Pending waste/count submissions do NOT insert ledger rows; trigger `trg_fs_posted_replays_*` writes ledger only on pending→posted flip. The danger is purely UI: data layer is correct (Agent 3).
- **PO→GR rollup is atomic.** Trigger `0055_gr_po_rollup_trigger.sql` §A fires synchronously inside the same transaction; UOM mismatch rolls the whole tx back. Idempotent replay handled by §B (Agent 3).
- **Existing test coverage for Physical Count is real** — auto-post, pending, approve, reject, idempotent replay, concurrent race all green (`physical_counts_idempotent.test.ts`, Agent 6).

### Risky today (P0 / P1, see §4)
- **Physical Count Step 1 → Step 2 has no snapshot-open confirmation.** If the `openSnapshot` call silently fails, the operator advances to Step 2, counts the item, submits, and only discovers the failure at submit — having lost the count (Agent 2B P0).
- **Approval Inline Card on the inbox allows BLIND APPROVE/REJECT when the detail fetch fails.** Hebrew copy at `approval-inline-card.tsx:458` says "cannot load details, can still approve/reject" — operator can post stock changes without ever seeing what they're approving (Agent 2C, **escalated to P0**).
- **Physical Count approval page has a comment claiming self-approval prevention exists, but the UI does not enforce it** (line 325). Backend 403 is the only barrier (Agent 2C P1).
- **Pending vs posted is distinguished only by tone color** in waste, physical count, and goods receipt success banners. No icon or text-only signal. A11y + comprehension risk on the single most dangerous semantic in the system (Agent 2B / Agent 3 / Agent 1 cross-cite, P1).
- **`idempotent_replay: true` from server is rendered identically to a first-time post** across GR + Waste + Count + Production. Operator can't tell "this was already posted" from "this was just posted now" (Agent 2A / Agent 1 contract evidence, P1).

### Confusing but not dangerous (P2)
- Production Actual submit button is labeled **"Approve"** — wrong word for the operator's own posting action.
- Waste reason-code dropdown shows raw codes (`SPOILAGE_LOSS`) with underscores swapped for spaces; no human-readable labels.
- Physical Count Step 2 collects unit AFTER quantity — backwards entry order.
- Waste-adjustment stepper buttons are `h-9 w-9` (36 px) — below WCAG AA 44 px touch minimum.
- "Large variance detected" pending banner does not define what "large" is.
- `Cmd/Ctrl+Enter` submit shortcut on Production Actual has zero on-screen affordance.
- PO list falls back to monospace `supplier_id` if supplier name is missing.
- Attached GR card on PO detail shows `item_id` in monospace as primary label.
- PO detail history tab does NOT surface GR-triggered PO state changes (operator sees PO move OPEN→PARTIAL with no causal trail).

### Must not be touched without backend / contract / read-model clarification
- **GR reversal does not decrement PO `received_qty`** (GAP-006, Layer 2 backend gap, not a UI gap).
- **Production Actual variance vs plan is informational only** — do not invent stock-affecting variance UI.
- **Scrap reduces FG only, not RM consumption** (GAP-011, locked decision, operator-training problem not UI problem). The two-head BOM preview rendering can be made clearer but cannot change semantics.
- **Self-approval rules differ by form** (waste: forbidden; physical count: admin/planner self-approval permitted per design 2026-04-30 §A.3). UI must not unify these.
- **Count discrepancy threshold is a proposed default** (GAP-010). Do not surface a specific percentage in operator copy until calibrated.
- **Manual PO source_type='manual'** with NULL recommendation/run links. UI must not synthesize source attribution.

---

## 2. Full route / file matrix

Canonical portal = `/home/user/gt-factory-os-portal`.
Stale duplicate to **not** edit = `/home/user/gt-factory-os/portal` (admin master-data only; no operator flows).
Backend = `/home/user/gt-factory-os/api/src`.
Migrations = `/home/user/gt-factory-os/db/migrations`.

| Flow | Portal route | Portal page/component (path:line where known) | Portal hook/proxy | Backend handler | Migration / contract | Tests | Owner | Confidence |
|---|---|---|---|---|---|---|---|---|
| PO list | `/purchase-orders` | `(po)/purchase-orders/page.tsx` (StatusBadge, LinesSummaryCell, stats tiles 513-542) | `/api/purchase-orders` proxy | `api/src/purchase-orders/route.ts` + `handler.ts` | 0007 ledger; 0025 change_log | `api/test/purchase_order_manual_create.test.ts` (create only) | W2 portal | clear |
| PO detail | `/purchase-orders/[po_id]` | `(po)/purchase-orders/[po_id]/page.tsx` (AttachedGrCard 283-343, History 372-443) | `/api/purchase-orders/[po_id]` | `purchase-orders/handler.ts` + `cancel_handler.ts` + `line_cancel_handler.ts` | 0007, 0025 | partial | W2 portal | clear |
| PO manual create | `/purchase-orders/new` | `(po)/purchase-orders/new/page.tsx` | `/api/purchase-orders` POST | `create_manual_po_handler.ts:1-304` + DB `fn_create_manual_po` | LOCKED_DECISIONS §"Receipts and POs"; schemas.ts:93-196 | `purchase_order_manual_create.test.ts` (happy path + validation + 409 supplier mapping) | W2 portal | clear |
| PO cancel | `(po)/purchase-orders/[po_id]` action | inline | `/api/purchase-orders/[po_id]` mutation | `cancel_handler.ts:1-132` (status DRAFT/OPEN only; defends against partial receipts) | 0007, 0025 | missing | W2 portal | clear |
| PO line cancel | inline on detail | inline | `/api/purchase-order-lines/[id]` | `line_cancel_handler.ts:1-140` | 0007 | missing | W2 portal | clear |
| Goods Receipt form | `/ops/stock/receipts` (also `?po_id=` prefill) | `(ops)/stock/receipts/page.tsx:1-2024` (LandingPicker 1389-1491; POLineMatchCard; FormActionsBar) | proxy via `/api/goods-receipts` | `goods-receipts/handler.ts:1-300+` (auto-post; UOM/item-class checks; UNIQUE replay) | 0007 ledger + 0055 GR→PO rollup; goods-receipts/schemas.ts:1-63 | `goods_receipts.test.ts` (I1-I7; reversal partial) | W2 portal | clear |
| GR list / history | (missing) | — | — | `goods-receipts/list_handler.ts` (backend present) | 0012 form_tables | none | W4 read-model gap | drift |
| Waste/Adjustment form | `/ops/stock/waste-adjustments` | `(ops)/stock/waste-adjustments/page.tsx:1-1089` (inline reason-code mirror 35-72; sticky bar 1053-1083; positive confirm 1003-1048) | `/api/waste-adjustments` proxy | `waste-adjustments/handler.ts` (auto-post loss ≤ threshold; 202 pending else) | waste-adjustments/schemas.ts:1-182; portal mirror `src/lib/contracts/waste-adjustments.ts` | `tests/unit/features/waste-adjustment-schema.test.ts` (**schema only — zero API tests**) | W2 portal (UI), W1 backend (API tests) | clear (UI) + missing (tests) |
| Waste approval | `/inbox/approvals/waste/[submission_id]` | `(inbox)/inbox/approvals/waste/[submission_id]/page.tsx:1-358` | `/api/waste-adjustments/:id/approve` + `/reject` | `waste-adjustments/handler.ts` approve/reject endpoints | schemas.ts:75-78 (approve), 142-152 (conflict reasons incl. `SELF_APPROVAL_FORBIDDEN`) | missing | W2 portal | clear |
| Physical Count form | `/ops/stock/physical-count` | `(ops)/stock/physical-count/page.tsx:1-1358` (BlindCountBanner 232-258; step indicator 167-229; snapshot card 1107-1161; cancel inline 1281-1308) | `/api/physical-count/open` + `/api/physical-count` POST | `physical-counts/handler.ts` (anchor-first; `replace_anchor()`; ratio algorithm) | physical-counts/schemas.ts:1-159; design doc 2026-04-30 §A.3 self-approval | `physical_counts_idempotent.test.ts` (full incl. approve/reject/race) | W2 portal | clear |
| Physical Count approval | `/inbox/approvals/physical-count/[submission_id]` | `(inbox)/inbox/approvals/physical-count/[submission_id]/page.tsx:1-375` (comment line 325 about self-approval) | `/api/physical-count/:id/approve` + `/reject` | physical-counts handler approve/reject; admin/planner self-approval permitted | schemas.ts:76-104 (approve response includes `anchor_source='COUNT_APPROVAL'`) | covered in idempotent suite | W2 portal | clear |
| Production Actual form | `/ops/stock/production-actual` | `(ops)/stock/production-actual/page.tsx:1-2518` (step indicator; BOM preview 1178-1234; success 1465-1635; variance 1600-1621) | `/api/production-actuals/open` + POST | `production-actuals/handler.ts:1-100+` (two-head BOM; PRODUCTION_CONSUMPTION + OUTPUT + SCRAP rows; from_plan link validation) | production-actuals/schemas.ts:1-206; LOCKED_DECISIONS §"Production reporting v1"; blueprint §"BOM/Recipe Semantics" | `production_actual.test.ts` (T4-T7); `tests/e2e/production-actual-real.spec.ts` (load only, **no submit assertion**) | W2 portal | clear |
| Approval inline card | `/inbox` (embedded) | `src/features/inbox/approval-inline-card.tsx:1-500+` (LoadError 458 — **blind-approve risk**) | `/api/waste-adjustments/:id/approve` + `/api/physical-count/:id/approve` | shared with detail-page approvals | shared | missing | W2 portal | clear |
| Exceptions inbox | `/inbox` | `src/app/(inbox)/inbox/page.tsx` + `src/features/inbox/*` | `/api/exceptions` | shared queries | 0010 exceptions | missing | W2 portal | clear |
| Credit decision | `/inbox/credit/[exception_id]` | `(inbox)/inbox/credit/[exception_id]/page.tsx:1-610` (Hebrew labels; isTerminal 482-485) | `/api/inbox/credit/:id/approve` + `/reject` + `/acknowledge` | inbox credit handlers | doc B §3.2 / §3.4 lifecycle | missing | W2 portal | clear |
| My submissions | `/ops/me/activity` | `(ops)/me/activity/page.tsx` | `/api/submissions/recent` | recent_submissions handler | GAP-005 CLOSED 2026-04-23 | partial | W2 portal | clear |
| Shared form widgets | n/a | `src/features/ops/*` (WorkflowHeader, SectionCard, ValidationSummary, FormActionsBar, StepIndicator, BlindCountBanner) | varies | — | — | unit (partial) | W2 portal | clear |

**Drift flag:** `/home/user/gt-factory-os/portal/src/app/admin/*` exists but contains only admin master-data routes, no operator flows. All operator-flow audits in this report target the canonical `/home/user/gt-factory-os-portal` repo. The duplicate is not edited.

---

## 3. Per-form process-continuity map

Each form is mapped: entry → required context → validation → submit → server behavior → terminal UI state → stock/PO/plan effect → visibility after action → audit/history → approval/correction/reversal path → gaps.

### 3.1 Manual Purchase Order create
- **Entry**: `/purchase-orders/new`. Reached from list (planner/admin role gate). No deep-link source.
- **Required context**: supplier, expected_receive_date, manual_reason, ≥1 line with item_id XOR component_id and ordered_qty>0. Idempotency key minted client-side.
- **Validation**: client-side none visible; relies on server. Server 422 returns field-keyed `ValidationErrors`.
- **Submit**: `POST /api/v1/mutations/purchase-orders` via portal proxy. Handler: `create_manual_po_handler.ts`.
- **Server behavior**: calls `fn_create_manual_po` (returns po_id, po_number, status, source_type='manual'). Idempotent replay returns 201 with `idempotent_replay: true`. 409 conflict reasons (verbatim): `EMPTY_REASON`, `EMPTY_LINES`, `INVALID_QTY`, `LINE_POLYMORPHISM_VIOLATION`, `SUPPLIER_NOT_FOUND`, `ACTOR_NOT_FOUND`, `SUPPLIER_ITEM_MAPPING_MISSING`.
- **Terminal state**: redirect to PO detail page. **Gap**: no success confirmation rendered before redirect; on slow networks the operator can't tell whether the submit went through.
- **Stock effect**: none on create. PO is supply signal only.
- **Visibility**: PO appears in `/purchase-orders` list immediately (cache invalidation TBD; verify in implementation phase).
- **Audit**: history tab on detail shows `PO_CREATE` row.
- **Approval/correction**: cancel via detail page (planner/admin); status DRAFT or OPEN only.
- **Gaps to register**: P2 silent-success on redirect; P2 no client-side validation surface before submit; P2 multi-line table likely overflows on 390 px (unverified).

### 3.2 Goods Receipt
- **Entry**: `/ops/stock/receipts` direct or `?po_id=<id>` prefill from PO detail.
- **Required context** (prefill path): PO header + OPEN/PARTIAL lines; supplier locked; lines seeded with `received_qty = open_qty`. Manual path: operator picks supplier + adds lines.
- **Validation**: client-side none visible for over-receipt or wrong-item; server enforces UOM consistency, supplier active, item active, item-type match.
- **Submit**: 3-step (Header → Lines → Review). `POST /api/v1/mutations/goods-receipts`.
- **Server behavior**: single transaction inserts `form_submissions` (UNIQUE idempotency_key), `goods_receipts` header, `goods_receipt_lines`, `stock_ledger` rows (`movement_type='GR_POSTED'`, composite idempotency key `GR:{idem}:{line_id}`). Trigger 0055 §A rolls up `received_qty` on `purchase_order_lines` synchronously; UOM mismatch raises and rolls entire tx back. Over-receipt is **non-blocking** — emits exception row, commits receipt.
- **Terminal state**: full-page success banner with bulleted posted-lines list and post-action nav cluster (Back to PO / View receipts / View movement log / Post another receipt).
- **Stock effect**: per-line `+received_qty` to `current_balances` via projection trigger (0009).
- **PO effect**: `received_qty` increments synchronously; PO status flips OPEN→PARTIAL or →RECEIVED via separate logic.
- **Visibility**: stock list shows new on-hand immediately. PO detail Attached-GRs tab shows the receipt.
- **Audit**: PO history tab shows PO-level mutations but **does not** surface GR-triggered changes (P2 gap).
- **Approval/correction**: no operator reversal. GR reversal endpoint exists at backend; portal has no operator surface and **PO `received_qty` is NOT decremented on reversal** (GAP-006, blocked).
- **Gaps to register**: P1 `idempotent_replay` shown identically to first-time post (line 865-871); P1 raw `item_id` font-mono primary on AttachedGrCard (line 326); P1 raw `po_line_id` in posted-lines summary (line 1224-1233); P2 PO detail History missing GR rollups; P2 supplier fallback to monospace ID on PO list (line 937); P2 over-receipt no inline guard before submit (verify); P2 wrong-item on manual path no guard (verify).

### 3.3 Waste / Adjustment
- **Entry**: `/ops/stock/waste-adjustments`. Operator/planner/admin can submit. No deep-link.
- **Required context**: direction (loss | positive), item_type, item_id, quantity, unit, reason_code. Notes required if direction=positive OR reason_code in {theft_loss, found_stock, correction, other}. Idempotency key.
- **Validation**: inline — reason-code dropdown filters by direction (lines 769-836); notes asterisk + character count; sticky submit bar.
- **Submit**: `POST /api/v1/mutations/waste-adjustments`.
- **Server behavior**: direction=loss & qty ≤ threshold → 201 posted, ledger `WASTE_POSTED` row inserted in same tx. Direction=loss & qty > threshold → 202 pending, exception emitted. Direction=positive → 202 pending always, exception emitted with `approval_reason='positive_direction'`. Conflict reasons include `COUNT_FREEZE_ACTIVE`, `REASON_CODE_NOT_ALLOWED`, `IDEMPOTENCY_KEY_REUSED`.
- **Terminal state**: result banner with tone=success (posted) or tone=warning (pending). Shows idempotency_key (P3 noise) and submission_id.
- **Stock effect**: posted → `WASTE_POSTED` ledger row, balance updates immediately. Pending → no ledger row, balance unchanged until approval.
- **Visibility**: posted → stock list reflects change. Pending → no stock change; row appears in inbox `/inbox/approvals/waste/[submission_id]`.
- **Audit**: form_submissions row + (if posted) ledger row + (if pending) exception row.
- **Approval/correction**: planner/admin approves or rejects from inbox. Self-approval forbidden (handler-enforced 409 `SELF_APPROVAL_FORBIDDEN`); **NOT enforced in UI** (P1 gap).
- **Gaps to register**: P1 pending vs posted distinguished by tone only (no icon/text); P1 pending result has no link to inbox; P2 reason codes shown as `SPOILAGE_LOSS` not "Spoilage / Loss" labels; P2 character-count shown but max-length not enforced client-side; P2 stepper buttons 36 px (below WCAG); P3 idempotency_key visible to user (noise); P0 missing API integration tests entirely (Agent 6).

### 3.4 Physical Count
- **Entry**: `/ops/stock/physical-count`. Two-step (Step 1 = item pick; Step 2 = blind-count + submit). Operator/planner/admin can submit; planner/admin can approve.
- **Required context Step 1**: item selection via combobox. Side-effect: server opens snapshot (`POST /api/physical-count/open` returns snapshot_id, opened_at, idempotent_open). **Gap**: snapshot-open failure is silent — Step 2 still renders. **P0**.
- **Required context Step 2**: counted_quantity (≥0), unit. Snapshot context card shows snapshot_id + opened_at. BlindCountBanner enforces no on-screen system qty.
- **Validation**: unit required to enable submit; quantity has no min=0 in code, allows negative until server 422 (P2).
- **Submit**: `POST /api/v1/mutations/physical-count` with snapshot_id + counted_quantity + unit.
- **Server behavior**: ratio algorithm `abs(delta)/snapshot > threshold` → 202 pending (auto-anchor blocked). Else → 201 posted, calls `replace_anchor()` (anchor-first; **no `stock_ledger` row**). Zero-snapshot edge case: counted>0 vs snapshot=0 → always pending. Conflict reasons include `SNAPSHOT_NOT_FOUND`, `SNAPSHOT_EXPIRED`, `SNAPSHOT_OWNER_MISMATCH`, `SNAPSHOT_ALREADY_CONSUMED`, `COUNT_ALREADY_OPEN`, `THRESHOLD_NOT_CONFIGURED`.
- **Terminal state**: result banner. Auto-posted shows "Count posted" with delta colored by sign; pending shows "Large variance detected…awaiting planner approval" without defining what "large" means (P2).
- **Stock effect**: posted → anchor replaced (snapshot becomes new baseline). Pending → no anchor change, `count_freezes.state='holding'` blocks concurrent waste/GR on that key.
- **Visibility**: posted → stock list reflects new on-hand from anchor. Pending → no change; row appears in `/inbox/approvals/physical-count/[submission_id]`.
- **Audit**: form_submissions + (if posted) anchor row.
- **Approval/correction**: planner/admin approves (admin/planner self-approval **permitted** per design 2026-04-30 §A.3 — distinct from waste). Approval inserts `replace_anchor()` and resolves exception. Rejection leaves anchor unchanged. Cancel snapshot released via `POST /api/physical-count/:snapshot_id/cancel`.
- **Gaps to register**: **P0** silent snapshot-open failure; P1 snapshot_id not echoed in result banner (audit-trail opacity); P1 pending uses "large variance" without definition; P1 self-approval prevention claimed in code comment (line 325) but UI does not enforce — see also P2 backend allows admin/planner self-approval, so the comment is misleading not buggy: the actual rule is "operator/viewer cannot self-approve" and UI should disable buttons for those roles; P2 unit-after-quantity entry order; P2 negative qty accepted; P2 approval success shows `anchor_source='COUNT_APPROVAL'` enum but not anchor value or delta.

### 3.5 Production Actual
- **Entry**: `/ops/stock/production-actual` direct or `?item_id=&from_plan_id=&suggested_qty=` deep-link. Operator/admin only (planner forbidden — distinct from other forms).
- **Required context**: item_id (MANUFACTURED or REPACK supply_method), pinned bom_version_id (and base_bom_version_id if two-head), output_qty, scrap_qty, output_uom, optional notes, optional from_plan_id.
- **Validation**: client-side qty ≥0; variance vs plan computed at 2% threshold (line 357-361, hardcoded), informational only.
- **Submit**: `POST /api/v1/mutations/production-actuals`. **Submit button labeled "Approve"** (P2 — wrong word for operator's own action).
- **Server behavior**: single tx inserts `production_actual` row + ledger rows: `PRODUCTION_CONSUMPTION` per BOM line (`qty_delta = -output_qty × qty_per_unit`); `PRODUCTION_OUTPUT` (`+output_qty`); `PRODUCTION_SCRAP` (`qty_delta=0`, audit-only per A13 §1 — scrap reduces FG via OUTPUT-SCRAP NET, not via SCRAP delta). If from_plan_id provided: plan validated (item match, status='planned', not already completed) and `production_plan.completed_submission_id` updated; on any plan mismatch entire tx rolls back. Conflict reasons include `STALE_BOM_VERSION`, `STALE_BASE_BOM_VERSION`, `WRONG_SUPPLY_METHOD`, `NO_ACTIVE_BOM_VERSION`, `UOM_MISMATCH`, `PLAN_NOT_FOUND`, `PLAN_ITEM_MISMATCH`, `PLAN_ALREADY_COMPLETED`, `PLAN_CANCELLED`.
- **Terminal state**: success panel (lines 1465-1635) with large output qty, scrap if >0, consumption breakdown table (component_id in font-mono — P1 raw ID risk), linked plan context, variance row.
- **Stock effect**: FG +output_qty, FG -scrap_qty (via separate PRODUCTION_SCRAP audit row that does NOT change balance; only PRODUCTION_OUTPUT does), each RM/PKG component -consumption_qty.
- **Visibility**: stock list reflects FG and component balances immediately.
- **Audit**: form_submissions + ledger rows + (if plan-linked) production_plan.completed_submission_id.
- **Approval/correction**: none — production actual auto-posts. No reversal in v1.
- **Gaps to register**: P2 submit button labeled "Approve" (semantically wrong); P2 `Cmd/Ctrl+Enter` shortcut no on-screen affordance; P1 success panel shows component_id without name (raw ID); P1 success panel shows no before/after stock balance per component; P2 two-head BOM split (PACK vs BASE) labeled in Hebrew without explanation of why scrap does not reduce RM (GAP-011 operator-training note).

### 3.6 Waste approval (inbox)
- **Entry**: `/inbox/approvals/waste/[submission_id]`. Planner/admin.
- **Required context**: detail fetch from `GET /api/waste-adjustments/:submission_id` (item, direction, quantity, reason_code, notes, event_at, submitted_at, submitted_by_display_name, status, exception).
- **Validation**: rejection_reason required (button disabled until non-empty); approval_notes optional.
- **Submit**: `POST .../approve` or `.../reject` with idempotency key.
- **Server behavior**: on approve → form_submissions pending→posted triggers replay → ledger `WASTE_POSTED` row inserted, exception resolved. On reject → form_submissions pending→rejected, exception resolved, no ledger row. 409 `SELF_APPROVAL_FORBIDDEN` if submitter == approver.
- **Terminal state**: SuccessState shows `stock_ledger_movement_id` (raw) and `exception_id` (raw). **Gap**: no human-readable "Item X stock changed from A to B" (P1).
- **Stock effect**: approval posts the deferred ledger row; rejection does not.
- **Audit**: visible via inbox row history.
- **Approval/correction**: none — terminal.
- **Gaps to register**: P1 raw IDs in success message; P1 no stock before/after; P2 conflict banner generic ("refresh the page and try again") rather than echoing 409 reason; P2 no audit history shown after action (no "Approved by X at HH:MM"); P2 self-approval enforcement only server-side (UI should preemptively disable buttons when current user id == submitter id).

### 3.7 Physical Count approval (inbox)
- **Entry**: `/inbox/approvals/physical-count/[submission_id]`. Planner/admin (and per design 2026-04-30 §A.3, admin/planner may self-approve their own counts).
- **Required context**: detail fetch (item, counted_quantity, snapshot_quantity, delta, event_at, submitted_at, submitted_by, status).
- **Validation**: rejection_reason required.
- **Submit**: `POST .../approve` or `.../reject`.
- **Server behavior**: approve → form_submissions pending→posted, `replace_anchor()` invoked, exception resolved. Reject → pending→rejected, anchor unchanged, exception resolved.
- **Terminal state**: SuccessState shows `anchor_source='COUNT_APPROVAL'` enum (P1 — should also show new anchor value + delta).
- **Stock effect**: approval replaces the anchor (this is THE event that updates stock truth for a count). Rejection: anchor unchanged.
- **Audit**: anchor row.
- **Gaps to register**: P1 self-approval comment at line 325 documents policy but UI does not enforce role check (admin/planner OK, operator/viewer not allowed); P1 success message shows enum not value; P2 no anchor before/after surfaced.

### 3.8 Approval inline card (`/inbox` embedded)
- **Entry**: rendered on `/inbox` for `approval:waste` and `approval:physical_count` rows.
- **Required context**: lazy detail fetch on mount.
- **Validation**: rejection_reason required.
- **Submit**: same endpoints as the detail pages.
- **Server behavior**: identical to detail-page approval.
- **Terminal state**: inline outcome card in Hebrew ("אושר — הפעולה הועברה למחסן" / "נדחה — הפעולה לא בוצעה").
- **Gap (escalated to P0)**: `approval-inline-card.tsx:458` `LoadError` state shows "לא ניתן לטעון פרטים. ניתן לאשר או לדחות בכל זאת." (cannot load details, can approve/reject anyway) — operator can post stock-affecting approvals **without ever seeing the detail**. This is a correctness risk, not a UX risk.
- Other gaps: P2 no submission_id / actor / timestamp echoed in terminal state.

### 3.9 Credit decision (inbox)
- **Entry**: `/inbox/credit/[exception_id]`. Planner/admin (capability `planning:execute`).
- See Agent 2C report for full process map. Out of scope for inventory-truth implementation in this pass; documented for completeness. Severity P2 for ID/context echo gaps.

### 3.10 Shared form system
- WorkflowHeader, SectionCard, StepIndicator, BlindCountBanner, ValidationSummary, FormActionsBar, useCapability, idempotency-key utility.
- Idempotency: minted at form open; reused on retry; reset on "record another" or success.
- Session: real Supabase SSR auth via `@supabase/ssr`; tests use `X-Test-Session` dev-shim (`ENABLE_DEV_SHIM_AUTH=true` in test env only).
- Portal API proxy at `src/app/api/*` forwards Authorization header to backend `/api/v1/mutations/*`.

---

## 4. Gap register

P0 = correctness/trust blocker. P1 = daily-use blocker. P2 = friction / Tom Tax. P3 = polish.

| ID | Pri | Form / surface | Title | Evidence (file:line) | Why it matters operationally | Owner | Safe to implement now? | Proposed next action |
|---|---|---|---|---|---|---|---|---|
| AUD-001 | **P0** | Approval inline card | Inline card allows blind approve/reject when detail fetch fails | `src/features/inbox/approval-inline-card.tsx:458` | Operator approves a waste/count submission they have not actually seen — direct stock effect from an uninformed decision. Worst-case false-green. | W2 portal | YES (UI-only) | Block approve+reject buttons when detail fetch errors; require deep-link to detail page; keep "Retry detail" affordance. |
| AUD-002 | **P0** | Physical Count form | Snapshot-open failure on Step 1 is silent; Step 2 renders anyway | `src/app/(ops)/stock/physical-count/page.tsx:1052-1110` (open useEffect); `src/features/ops/physical-count-submit.ts:200-204` | Operator counts, submits, then loses the count to a conflict; trust damaged, time wasted. | W2 portal | YES (UI-only) | Surface snapshot-open error before Step 2; block advance if snapshot didn't open. |
| AUD-003 | **P1** | Waste, GR, Count, Production | `idempotent_replay: true` rendered identically to first-time post | GR `receipts/page.tsx:865-871`; Waste `waste-adjustments/page.tsx:615-617`; contract evidence: schemas.ts response shapes include `idempotent_replay` boolean | Operator submits, network glitches, they hit submit again, success banner says "Posted!" — operator thinks they double-posted and either panics or stops trusting confirmation. | W2 portal | YES (UI-only; contract already returns the flag) | When `idempotent_replay=true`, add explicit "Already posted — replay returned existing record" badge + show original `posted_at`. |
| AUD-004 | **P1** | Waste + Count + GR + Production | Pending vs posted distinguished by tone color only (no icon, no text-only flag) | waste `waste-adjustments/page.tsx:607-684`; count `physical-count/page.tsx:509-640` | The single most dangerous semantic in the system (blueprint §"most dangerous semantic trap"). Color-blind users and grayscale viewers cannot tell. | W2 portal | YES | Add icon (CheckCircle vs ClockArrow) + explicit text ("POSTED — stock updated" vs "PENDING APPROVAL — stock NOT yet changed") in addition to tone. |
| AUD-005 | **P1** | Waste + Count approval | Self-approval prevention is server-only; UI lets operator click approve on own submission | waste `(inbox)/inbox/approvals/waste/[submission_id]/page.tsx:278` (submitter shown, no check); count `(inbox)/inbox/approvals/physical-count/[submission_id]/page.tsx:301,325` (comment lies about UI enforcement) | Operator clicks approve, hits 409, sees generic "Action refused" banner. Wastes time and is confusing. | W2 portal | YES (UI-only) | Compare `submitted_by_user_id` to current user; disable Approve+Reject (or hide) when self; show inline "You cannot approve your own submission" notice. For physical count, allow admin/planner self-approval per design 2026-04-30 §A.3 — only block operator/viewer. |
| AUD-006 | **P1** | Waste approval | Success banner shows raw `stock_ledger_movement_id` and `exception_id`, no "Item X stock changed from A to B" | `(inbox)/inbox/approvals/waste/[submission_id]/page.tsx:154-179` | Approver cannot verify the stock effect was correct without leaving page. | W2 portal | YES if detail endpoint returns item display + balance after; verify in code | Use existing detail fields to render "Approved. {Item display} adjusted by {±qty}{unit}. Ledger ref: {short id}." Defer "from A to B" if read-model doesn't carry it. |
| AUD-007 | **P1** | Physical Count approval | Success banner shows `anchor_source='COUNT_APPROVAL'` enum and nothing about the new anchor value or delta | `(inbox)/inbox/approvals/physical-count/[submission_id]/page.tsx:168-179` | Same as above: approver cannot verify what they just made canonical. | W2 portal | YES | Render "Approved. New anchor: {counted_quantity}{unit} (delta {±delta}). Snapshot replaced." Use values already on the page. |
| AUD-008 | **P1** | Physical Count form | snapshot_id not echoed in submit result banner | `physical-count/page.tsx:509-640`; `physical-count-submit.ts:260-280` | Operator cannot correlate their submission with the snapshot they opened. | W2 portal | YES (UI-only) | Show `snapshot_id` (short form) + `opened_at` in the result card. |
| AUD-009 | **P1** | Waste + Count pending | Pending result has no link to inbox / no clear "what happens next" | waste `waste-adjustments/page.tsx:628-641`; count similar | Operator has no idea where to follow up; perception that the submission is "lost". | W2 portal | YES (UI-only) | Add explicit "Awaiting approval" panel with link to `/inbox` (and to the specific approval page where possible). |
| AUD-010 | **P1** | Production Actual | Submit button labeled "Approve" (semantically wrong for operator's own posting) | `(ops)/stock/production-actual/page.tsx:783` | "Approve" implies approving someone else's work; this is the operator's own posting. | W2 portal | YES (UI-only) | Re-label to "Post production actual" (or Tom-pinned Hebrew equivalent if register entry exists; otherwise English). |
| AUD-011 | **P1** | GR success | `idempotent_replay` indistinguishable from first-time post | `receipts/page.tsx:865-871` | Same as AUD-003 but GR-specific. Could cause an operator to keep retrying a successful submit. | W2 portal | YES | Folded into AUD-003 implementation. |
| AUD-012 | **P1** | PO detail | AttachedGrCard uses font-mono `item_id` as primary label | `(po)/purchase-orders/[po_id]/page.tsx:326` | Operator/admin cannot verify which physical item was received without separate lookup. | W2 portal | YES if backend returns item display name in attached GR payload; verify | Show item display name primary, `item_id` short hash secondary. |
| AUD-013 | **P1** | Goods Receipt success | Posted-lines summary shows `po_line_id` rather than human reference | `receipts/page.tsx:1224-1233` | Operator can't tell which PO line they just received against without leaving the page. | W2 portal | YES if response includes line ref; verify | Show "Line {n}: {item display} +{qty}{unit}" instead of raw `po_line_id`. |
| AUD-014 | **P1** | Production Actual success | Consumption table shows `component_id` (font-mono) without component display name | `production-actual/page.tsx:1465-1635` | Operator can't verify they consumed the right components. | W2 portal | YES if BOM-open response carries names (likely does); verify | Render component display name primary, ID secondary. |
| AUD-015 | **P2** | Waste form | Reason codes shown as raw underscored strings (`SPOILAGE_LOSS` → "SPOILAGE LOSS"), not human labels | `waste-adjustments/page.tsx:35-72` (mirror); approval pages show raw too | Operator picks the wrong reason because labels are unclear. | W2 portal | YES (contract already locks the codes; map to labels client-side) | Add a labels map `WASTE_REASON_LABELS_EN` (and `_HE` if Tom-pinned register exists) for display only. Do NOT change the code values. |
| AUD-016 | **P2** | Waste form | Stepper buttons `h-9 w-9` = 36 px below WCAG 44 px touch minimum | `waste-adjustments/page.tsx:857-897` | Mobile operators mis-tap. | W2 portal | YES (CSS-only) | Bump to `h-11 w-11` (44 px) or `h-12 w-12` on touch screens. |
| AUD-017 | **P2** | Physical Count Step 2 | Unit selected AFTER quantity (backwards entry order) | `physical-count/page.tsx:1174-1235` | Mobile operators enter "47" then hunt for unit chip; submit disabled with no clear reason. | W2 portal | YES (UI re-order only) | Move unit chips above the quantity input OR pre-select unit_default from open response. |
| AUD-018 | **P2** | Physical Count Step 2 | Negative qty accepted until server 422 | `physical-count/page.tsx:1174-1210` | Late feedback, frustrating. | W2 portal | YES (HTML attr) | Add `min="0"` and inline error before submit. |
| AUD-019 | **P2** | Physical Count pending | "Large variance detected" never defines what "large" is | `physical-count/page.tsx:509` | Operator wonders if they entered something wrong. | W2 portal | YES (copy only) | Re-word to "Variance is large enough to require planner approval before the count is applied." Do NOT cite a specific percentage (GAP-010 threshold not calibrated). |
| AUD-020 | **P2** | Production Actual | `Cmd/Ctrl+Enter` submit shortcut has no on-screen affordance | `production-actual/page.tsx:781-800` | Desktop users may submit accidentally while typing notes. | W2 portal | YES | Add a small hint under the submit button "Tip: Ctrl+Enter to submit" OR remove the shortcut. |
| AUD-021 | **P2** | PO list | Supplier falls back to monospace `supplier_id` when name missing | `(po)/purchase-orders/page.tsx:937` | Operator cannot read who the supplier is. | W2 portal | partial (contract returns name; ID fallback should be last resort and visually de-emphasized) | Show "Unknown supplier ({short id})" rather than raw monospace UUID. |
| AUD-022 | **P2** | PO detail history | History tab does not surface GR-triggered PO state changes | `(po)/purchase-orders/[po_id]/page.tsx:372-443` | Audit cannot trace why a PO moved OPEN→PARTIAL. | W4 read-model | NO (requires backend history endpoint to include GR rollup events) | Defer; file W4 gap. |
| AUD-023 | **P2** | All approvals | Conflict 409 banner is generic ("refresh and try again") rather than echoing `reason_code` | waste + count approval pages | Approver doesn't know whether to retry, re-fetch, or hand off. | W2 portal | YES (contract returns reason_code) | Echo human-readable mapping per known reason codes (SUBMISSION_NOT_PENDING, SELF_APPROVAL_FORBIDDEN, etc.). |
| AUD-024 | **P2** | Approval inline card terminal | No submission_id / actor / timestamp in success state | `approval-inline-card.tsx:414-443` | No audit trail context if user wants to confirm what they just did. | W2 portal | YES (UI-only) | Show short submission ref + "approved just now" timestamp. |
| AUD-025 | **P2** | Production Actual | Two-head BOM preview labels (Hebrew pack/base section headers) don't explain scrap does NOT reduce RM | `production-actual/page.tsx:1178-1234` | Operator believes scrap reduces consumption (GAP-011 operator-training note). | W2 portal | YES (copy only) | Add small disclaimer "Scrap reduces finished-goods output only; raw-material consumption is based on planned output." |
| AUD-026 | **P3** | Waste / all forms | `idempotency_key` shown in success banner is operator noise | `waste-adjustments/page.tsx:615-617` and elsewhere | Operator doesn't know what it is. | W2 portal | YES | Hide behind "Details" disclosure or remove from operator success copy; keep in dev console / logs. |
| AUD-027 | **P3** | Waste form | Character count shown but max not enforced client-side | `waste-adjustments/page.tsx:992-994` | Operator types long notes then gets 422. | W2 portal | YES if max length is in contract; verify | Add `maxLength` attr matching contract. |
| AUD-028 | **P1 (TESTS)** | Waste/Adjustment | Zero API integration tests | `api/test/*` — none for waste-adjustments | High-risk surface with no test coverage. | W1 backend | NO (out of W2 lane; flag for backend tranche) | Defer; file W1 gap. |
| AUD-029 | **P1 (TESTS)** | All operator forms | Zero mobile-viewport (390 px) E2E tests | `tests/e2e/*` — only `mobile-input-zoom.spec.ts` | Daily-driver operators are on phones/tablets. | W2 portal | YES (can be added in this pass for at least one form) | Add a 390 px Playwright smoke for waste-adjustments and physical-count. |
| AUD-030 | **P1 (TESTS)** | All operator forms | Zero post-action visibility tests (verify next page reflects new event) | `tests/e2e/*` | False-green risk: API says posted, UI may not reflect it. | W2 portal | partial | Defer to a follow-up; not in this pass. |

---

## 5. Cross-flow findings

### 5.1 PO → GR → Inventory → PO status
- Atomic at backend: GR insert + `goods_receipt_lines` insert + `stock_ledger` insert + trigger 0055 §A `received_qty` rollup all in one transaction. UOM mismatch raises and rolls everything back. **UI risk**: handler responds with 400 on the rollback, but the GR form's error rendering for trigger-raised UOM mismatches is not verified — verify in implementation phase before claiming closed. Over-receipt commits the receipt AND emits an exception (non-blocking); UI does not warn before submit (potential P2 to add an inline guard, but verify there's no contractual reason to permit silent over-receipt first).

### 5.2 GR / Waste / Count freeze interaction
- `count_freezes.state='holding'` while a count is pending blocks concurrent waste/GR via advisory lock + state check. Conflict response uses `COUNT_FREEZE_ACTIVE` (waste) / equivalent (GR — verify name in implementation phase). **UI risk**: conflict banner copy must tell the operator "a count is in progress for {item}; wait for approval/recount" not a generic "conflict".

### 5.3 Physical Count anchor vs Waste ledger movement
- Anchor replacement (Physical Count) and ledger movement (Waste) are different events. UI must say "anchor replaced" for count and "ledger movement posted" for waste. Currently approval success messages blur this — count success says "Anchor source: COUNT_APPROVAL" (right concept, wrong words for an operator); waste success says "Ledger movement {id}" (also opaque). Both should use plain operator copy. Tracked in AUD-006 / AUD-007.

### 5.4 Production plan → Production Actual → FG/RM movement → variance display
- Plan link validated and consumed atomically (`production_plan.completed_submission_id` set on submit; rolled back if any plan mismatch). Variance is informational and does not affect stock. UI variance disclaimer (line 357-361) is correct per contract. Idempotent replay does NOT re-link the plan (correct by design). **UI risk**: success panel does not show "stock changed: FG +X, RM −Y, PKG −Z" in human terms (tracked in AUD-014).

### 5.5 Pending approvals → inbox → approval/reject → stock effect visibility
- Inbox unifies waste + count approvals (inline cards) and credit decisions + planning recs (deep-link). Inline-card fast path has a P0 blind-approve risk on detail-fetch failure (AUD-001). Stock effect visibility post-approval is opaque (AUD-006, AUD-007).

### 5.6 Dashboard / read-model visibility after operator event
- Stock list (`/stock`) reads `current_balances` via curated read model — should reflect changes immediately for posted/approved events. For pending events the balance is unchanged (by design — most dangerous semantic). UI does not currently link from the operator success banner directly to the relevant stock-list row (would require querying the read model with balance_key) — defer as P3 polish unless trivial.

### 5.7 Manual PO vs recommendation PO
- Contract distinguishes `source_type` = `'manual'` vs (from recommendation, with `source_recommendation_id` + `source_run_id`). UI presence of source attribution on PO list / detail not verified. Out of scope for this pass; flag P2 in route matrix if absent on verification.

---

## 6. Implementation plan

### Tranche A — Decision-grade UX now (this overnight pass)
**Goal**: close every P0 + the highest-leverage P1s that are UI-only, contract-grounded, and verifiable without backend changes.

Surfaces & actions:
1. **AUD-001 — Block blind approve/reject in inline card** (`approval-inline-card.tsx:458`).
2. **AUD-002 — Surface snapshot-open failure in Physical Count** (`physical-count/page.tsx` open useEffect).
3. **AUD-003 — Render `idempotent_replay` distinctly** in GR + Waste + Count + Production success banners.
4. **AUD-004 — Pending vs posted: icon + text, not tone-only** across waste + count + GR + production.
5. **AUD-005 — Self-approval UI guard** in waste + count approval pages (allowing admin/planner self-approve for count per design 2026-04-30 §A.3).
6. **AUD-009 — Pending result → link to inbox** in waste + count.
7. **AUD-010 — Production Actual submit label fix** (`"Approve"` → `"Post production actual"` or per Hebrew register).
8. **AUD-006 / AUD-007 — Approval success copy: human-readable stock/anchor effect** (using fields already on the page).

**Why now**: each one is contract-grounded, UI-only, verifiable by reading the existing handler responses, and addresses a documented correctness or trust risk.

**Risk**: low. No schema change. No new endpoint. No new contract value. Idempotency, role rules, and stock-effect routing are unchanged.

**Test plan**: type-check (`tsc --noEmit`) + unit tests where present; manual code review for each affected page. Mobile smoke at 390 px is in Tranche B.

**Stop conditions**: if any change requires inventing a backend field, halt and log as W4 gap.

### Tranche B — Flow-completion UX next (queued, run if time permits in same pass)
9. **AUD-008 — Echo snapshot_id in PC result banner**.
10. **AUD-011 — GR replay disambiguation** (folded into AUD-003).
11. **AUD-012, AUD-013, AUD-014 — Raw IDs → display names** on AttachedGrCard, GR success line summary, production-actual consumption table. Verify backend responses include names first.
12. **AUD-015 — Waste reason-code labels map** (English; Hebrew only if Tom register entry exists).
13. **AUD-019 — "Large variance" copy without quoting threshold**.
14. **AUD-023 — Conflict 409 banner echoes reason_code mapping**.
15. **AUD-025 — Two-head BOM scrap disclaimer**.

### Tranche C — Polish / acceleration later (NOT in this pass)
- AUD-016 stepper touch targets (CSS-only but coordinate with shared form widget).
- AUD-017 unit-before-qty re-order (touches form state).
- AUD-018 negative-qty client guard.
- AUD-020 Cmd+Enter affordance.
- AUD-021 supplier-name fallback copy.
- AUD-024 inline-card terminal state metadata.
- AUD-026 idempotency_key noise removal.
- AUD-027 maxLength enforcement.
- AUD-029 mobile-viewport Playwright smoke (one form per pass).

### Tranches deferred to other lanes
- AUD-022 PO history GR rollup — W4 read-model.
- AUD-028 Waste API integration tests — W1 backend.
- AUD-030 Post-action visibility tests — W2 + W1 coordination.
- GAP-006 GR reversal PO `received_qty` decrement — W1.
- GAP-010 Count discrepancy threshold calibration — Tom.
- GAP-011 Scrap-vs-RM operator training — Tom.

---

## 7. Implementation log

Populated by the implementation loops below. Each entry: gap id, files changed, before/after behavior, tests run, screenshots if available, remaining risks.

*(Tranche A loops appended below as they complete.)*
