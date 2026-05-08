# Goods Receipt — Browser Rehearsal Checklist (cycle 17, 2026-05-02)

> **Purpose.** Cycle 16 commit `223ba83` shipped the `/stock/receipts?po_id=` URL-driven prefill flow + the PO list `Receipts` summary column + the PO detail "Receive against this PO →" header CTA. Validation gates 4/4 PASSED at commit time (typecheck, build, lint:urls, Hebrew/RTL grep), and HTTP probes confirmed the route is auth-gated and alive. **What is NOT yet evidenced is browser-level operator behavior** — that the prefill actually fires under a real Supabase JWT against a real OPEN PO with at least 2 lines, that the success panel renders, that the back-link navigation produces an updated PO detail view, and that the terminal-status guard reroutes correctly on RECEIVED/CANCELLED POs.
>
> Tom (or any admin) follows this checklist against the deployed Vercel portal to fill in the **Actual** column and flip each step to PASS or FAIL. The result becomes the browser-level evidence pack for the GR/PO corridor.

---

## Pre-conditions

Before starting, verify these state items. **STOP** if any pre-condition is FAIL — gather the missing artifact first.

| # | Pre-condition | Verification step | Required value |
|---|---------------|-------------------|----------------|
| P1 | Portal commit deployed | Visit `gt-factory-os-portal.vercel.app/purchase-orders` (auth-gated) → click "Settings" or check footer / view-source for build SHA | `≥ 223ba83` (cycle 16 GR PO-prefill + simulation containment) |
| P2 | Backend Railway commit deployed | Visit `gt-factory-os-api.up.railway.app/health` | `200 OK` with `ok:true`; deploy SHA `≥ 010d09f` (cycle 16 backend tip) |
| P3 | Auth role | Sign in with magic link as a user whose `app_users.role IN ('operator','planner','admin')` | Bearer JWT from Supabase active in browser session |
| P4 | Test data — at least one OPEN PO with ≥ 2 lines | Either: (a) `/purchase-orders` list shows at least one row in OPEN status with `Receipts` column showing ratio `0 / N` for N ≥ 2; OR (b) create one via `/purchase-orders/new` (planner+admin only) | One OPEN PO with `lines_summary.line_count >= 2` |
| P5 | Test data — at least one RECEIVED or CANCELLED PO (for terminal-status step) | Filter `/purchase-orders?status=RECEIVED` or `status=CANCELLED` | Optional — needed only for Step 11 |
| P6 | Mobile test capability | Browser dev-tools → toggle device emulation to a 390px-wide viewport (e.g., iPhone 12 Pro) | Enabled before Step 12 |

---

## Step-by-step rehearsal

For each step, fill in **Actual** and **Pass/Fail**. A screenshot placeholder is provided for visual evidence.

---

### Step 1 — PO list shows Receipts summary column

| Field | Value |
|-------|-------|
| Route | `/purchase-orders` |
| Action | Open the PO list. Look at the `Receipts` column (between `Expected` and `Total net`). |
| Expected | Each PO row in its `Receipts` cell shows: a received/ordered ratio in monospaced tabular numbers (e.g., `0 / 24`); a 1-line caption with line count (`2 lines`); a 1px progress bar with `role="progressbar"` + `aria-valuenow/valuemin/valuemax`; a warning-toned `open` pill when `total_open_qty > 0`; success tone when fully received. Empty `lines_summary` (older API or transient rollback) shows neutral `No lines` caption. |
| Actual | _(Tom fills)_ |
| Screenshot | `[placeholder — capture full PO list with Receipts column visible]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If `Receipts` column missing entirely → check parent `PurchaseOrderRow` import has `lines_summary?: PurchaseOrderLinesSummary` (page.tsx:80). If column shows `—` everywhere → backend `lines_summary` rollup not populated; W1 cycle 9 verification needed. |

---

### Step 2 — PO detail shows "Receive against this PO →" CTA

| Field | Value |
|-------|-------|
| Route | `/purchase-orders/[po_id]` (click into one OPEN PO from Step 1) |
| Action | Look at the `WorkflowHeader.actions` cluster (top-right of the page). |
| Expected | A primary `btn-sm btn-primary` Link visible with text **"Receive against this PO →"**. `data-testid="po-receive-against-cta"`. `aria-label="Receive against PO {po_number}"`. `title` attribute discloses: "Receiving against this PO will update line balances atomically. Over-receipt is permitted but emits an exception for review." Visibility rule: rendered iff `po.status IN ('OPEN','PARTIAL')`. |
| Actual | _(Tom fills)_ |
| Screenshot | `[placeholder — capture PO detail header with CTA visible]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If CTA missing on OPEN/PARTIAL PO → check `(po)/purchase-orders/[po_id]/page.tsx:1323-1333` — visibility guard `po && (po.status === "OPEN" || po.status === "PARTIAL")`. If CTA visible on RECEIVED/CANCELLED PO → that's a regression; the guard at line 1334 should render the "View receipts →" Link instead. |

---

### Step 3 — CTA navigates to /stock/receipts?po_id=...

| Field | Value |
|-------|-------|
| Route | `/purchase-orders/[po_id]` (continue from Step 2) |
| Action | Click the "Receive against this PO →" CTA. |
| Expected | Browser URL becomes `/stock/receipts?po_id=<uuid>` where `<uuid>` is the PO's `po_id` (URL-encoded). Page begins loading the GR form. No 404, no 500. |
| Actual | _(Tom fills — capture the URL bar)_ |
| Screenshot | `[placeholder — capture URL bar showing /stock/receipts?po_id=<uuid>]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If URL missing `?po_id=` → check CTA href at `(po)/purchase-orders/[po_id]/page.tsx:1325`. If 404 → route group `(ops)` may have shifted; canonical URL is `/stock/receipts` per cycle 16 reconciliation. |

---

### Step 4 — PO context strip renders above the form

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` (continue from Step 3) |
| Action | Wait for the form to finish loading. Look at the strip immediately above the form, below the WorkflowHeader. |
| Expected | A horizontal context strip (`data-testid="receipts-po-context-strip"`) shows: PO number in monospaced font (e.g., `PO-2026-0001`); supplier name; expected delivery date if present; a Link `data-testid="receipts-po-back-to-po"` reading **"← Back to PO"** routing to `/purchase-orders/[po_id]`. The WorkflowHeader.eyebrow reads **"Receiving against PO {po_number}"**. The WorkflowHeader.description reads **"From {supplier_name} · expected {date}."** (or just `From {supplier}.` if no date). |
| Actual | _(Tom fills)_ |
| Screenshot | `[placeholder — capture WorkflowHeader + PO context strip]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If strip missing entirely → check `urlPoLocked && !urlPoTerminal && urlPoHeader` guard at `(ops)/stock/receipts/page.tsx`. If header eyebrow / description don't change from defaults → check WorkflowHeader.eyebrow / description conditional at receipts/page.tsx:592-600. |

---

### Step 5 — Supplier picker is locked with caption

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Scroll to the form. Look at the supplier `<select>` element. |
| Expected | The supplier `<select>` is **disabled** (greyed out, no dropdown opens on click). Its currently-selected value matches the PO's supplier. Below the supplier picker, a small caption reads **"From PO {po_number} — supplier locked."** The caption has `id="receipt-supplier-locked-caption"` and the select has `aria-describedby="receipt-supplier-locked-caption"`. Reference-PO picker (separate field) is also disabled with a synthetic option for the URL-supplied PO if it's outside the OPEN/PARTIAL filter set. |
| Actual | _(Tom fills)_ |
| Screenshot | `[placeholder — capture form with disabled supplier + locked caption]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If supplier still editable → check `disabled={urlPoLocked}` on supplier `<select>` element. If caption missing → check `urlPoLocked && urlPoHeader` guard around the `<span id="receipt-supplier-locked-caption">` element. |

---

### Step 6 — PO lines pre-loaded with received_qty = open_qty

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Look at the `Lines` SectionCard. Count how many line draft rows are pre-rendered. |
| Expected | One `LineDraft` row per OPEN/PARTIAL PO line (CLOSED + CANCELLED lines are filtered out). Each draft row's `quantity` input is pre-filled with the corresponding PO line's `open_qty`. Each draft's `unit` matches the PO line's `uom`. The `po_line_id` is wired (verifiable by inspecting the linked-PO-line `<select>` — it shows the matching PO line `#{line_number} · {component_or_item_name} · {open_qty} open / {ordered_qty} ordered {uom}`). The receivable_key is resolved by trying `component_id` then `item_id`. |
| Actual | _(Tom fills — note the count of draft rows + the qty / unit on each)_ |
| Screenshot | `[placeholder — capture lines section with prefilled drafts]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If no drafts pre-fill → check the `useEffect` prefill block in receipts/page.tsx (gated on `urlPoLocked && urlPoHeader && poDetailQuery.data && !prefillApplied`). If wrong qty / unit → check the `LineDraft` build inside that effect (received_qty=open_qty; uom from PO line). If 409 PO_LINE_PARENT_MISMATCH on submit later → receivable_key resolution failed; manually pick item from picker. |

---

### Step 7 — Edit one line's qty downward (partial), submit

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Pick one line. Edit its `quantity` input downward (e.g., from `24` to `10`). Optionally edit `notes`. Click **Submit receipt**. |
| Expected | Submit button changes to **"Submitting…"** (disabled). Form posts to `/api/goods-receipts` proxy (forwards to `POST /api/v1/mutations/goods-receipts`). On success: page transitions out of `submitting` phase; success panel renders (next step). |
| Actual | _(Tom fills — note any console errors)_ |
| Screenshot | `[placeholder — capture moment of clicking submit]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If form refuses to submit → check the network tab for the `POST /api/goods-receipts` request. 401 → JWT expired (re-login). 403 → role gate; user lacks `operator|admin`. 422 → validation error (qty must be > 0; idempotency_key invalid). 409 → reason_code (DUPLICATE_IDEMPOTENCY_KEY, PO_LINE_PARENT_MISMATCH, ITEM_TYPE_MISMATCH). 503 → break-glass mode active. |

---

### Step 8 — Success panel renders with posted ledger movement count + nav cluster

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | After Step 7 submit succeeds, look at the success panel. |
| Expected | A green-toned panel (`data-testid="receipt-success-panel"`) shows: the message **"Receipt posted successfully."** (or "Receipt already recorded." on idempotent replay); the itemSummary line (supplier · line item · qty · unit, repeated for each line); the detail line **"ref: {submission_id} · N line(s)"** where N = the count of posted ledger movements (one per `committed.lines[]` row, equivalent to the GR line count). Below those, a 3-button nav cluster: **"Back to PO {po_number} →"** (`data-testid="receipt-success-back-to-po"`) routing to `/purchase-orders/[po_id]`; **"View receipts on this PO →"** (`data-testid="receipt-success-view-attached-grs"`) routing to `/purchase-orders/[po_id]?tab=attached-grs`; **"View movement log →"** (`data-testid="receipt-success-view-movement-log"`) routing to `/stock/movement-log?po_id=<uuid>` with a `title` attribute disclosing **"Filter by po_id is not yet supported on the movement log; the link routes to the unfiltered ledger."** **Note:** the success panel does NOT explicitly print the new PO status text (e.g., "PO is now PARTIAL") — the user verifies via Step 9 by clicking Back to PO. The "posted ledger movement count" is the `N line(s)` figure on the detail line. |
| Actual | _(Tom fills)_ |
| Screenshot | `[placeholder — capture success panel + nav cluster]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If panel renders but missing nav cluster → check `done.kind === "success" && done.poId` guard at receipts/page.tsx:746. If `done.poId` missing → check `committed.po_id` in the success branch at receipts/page.tsx:561. If panel doesn't render at all → re-check Step 7 (submit phase didn't complete). |

---

### Step 9 — Click "Back to PO {po_number} →"; PO detail shows updated received_qty + line_status

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` → `/purchase-orders/[po_id]` |
| Action | Click the "Back to PO {po_number} →" button in the success-panel nav cluster. |
| Expected | Browser navigates to `/purchase-orders/[po_id]`. PO detail page renders. Header shows updated PO `status` (likely now `PARTIAL` if Step 7 was a partial receive — i.e., remaining open_qty > 0 — or `RECEIVED` if everything fully closed). Lines section shows updated `received_qty` matching the GR posted in Step 7 (e.g., the line that was edited to `10` now shows `received: 10 / 24` or similar in its line summary). The "Receive against this PO →" CTA is still visible if status is `PARTIAL`; replaced by "View receipts →" if status is now `RECEIVED`. |
| Actual | _(Tom fills — note the status badge + the affected line's received_qty)_ |
| Screenshot | `[placeholder — capture PO detail with updated status + received_qty]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If PO status didn't flip → backend `fn_post_goods_receipt` line balance update logic gap; W1 escalation (NOT a W2 fix). If received_qty unchanged → page may be serving stale TanStack Query cache; force-refresh (Ctrl+Shift+R) or check QueryClient invalidation post-mutation. |

---

### Step 10 — "View movement log →" link works (unfiltered)

| Field | Value |
|-------|-------|
| Route | (return to `/stock/receipts?po_id=<uuid>` if needed by replaying Step 7, or use the success panel from Step 8 if still in scope) |
| Action | Click the "View movement log →" link in the success-panel nav cluster. |
| Expected | Browser navigates to `/stock/movement-log?po_id=<uuid>` (URL carries `?po_id=` param). Movement log page renders; the page is currently agnostic to the `po_id` query param, so it shows the unfiltered ledger view (NOT scoped to this specific PO). The link's hover-tooltip (`title` attribute) discloses this honestly: **"Filter by po_id is not yet supported on the movement log; the link routes to the unfiltered ledger."** |
| Actual | _(Tom fills — confirm both: navigation succeeds AND tooltip is honest)_ |
| Screenshot | `[placeholder — hover state showing tooltip + landing page on movement log]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If link 404s → `/stock/movement-log` route doesn't exist; cycle 16 dispatch assumed it does. If tooltip missing → check `title=` attr at receipts/page.tsx:774. If link silently filters by `po_id` → that means W1 closed the W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL gap; update the tooltip to remove the disclosure. **Logged gap:** `W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL` (carried from cycle 12). |

---

### Step 11 — Terminal PO via direct URL → "View receipts →" empty-state guard

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid-of-RECEIVED-or-CANCELLED-PO>` |
| Action | Manually paste a URL pointing at a RECEIVED or CANCELLED PO (find one via `/purchase-orders?status=RECEIVED`). Hit enter. |
| Expected | Form is **NOT** rendered. Instead, a SectionCard renders with title **"PO {po_number} cannot accept further receipts"** (`data-testid="receipts-po-terminal-guard"`). Body text: **"This PO is in {Received|Cancelled} state. No additional goods receipts may be posted against PO {po_number} ({supplier_name})."** Three affordances below the body: **"View receipts →"** (`data-testid="receipts-po-terminal-view-receipts"`) routing to `/purchase-orders/[po_id]?tab=attached-grs`; **"Back to PO detail"** routing to `/purchase-orders/[po_id]`; **"Start a manual receipt"** (`data-testid="receipts-po-terminal-clear-link"`) routing to `/stock/receipts` with no query params (clears the lock). |
| Actual | _(Tom fills)_ |
| Screenshot | `[placeholder — capture terminal-status guard panel]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If form still renders → check `urlPoLocked && urlPoTerminal && urlPoHeader` guard around the SectionCard at receipts/page.tsx:606. If `urlPoTerminal` flag wrong → check `urlPoHeader.status === "RECEIVED" || === "CANCELLED"` flag derivation. If wrong copy → check SectionCard contents at receipts/page.tsx:607-619. |

---

### Step 12 — Mobile @ 390px — sticky elements, line cards, submit button reachable

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` (use OPEN PO from Step 6) |
| Action | Browser dev-tools → toggle device emulation to 390px width. Reload the page. |
| Expected | (a) PO context strip from Step 4 remains visible without horizontal scroll (the strip's `flex flex-wrap items-center gap-2` allows wrapping); (b) line cards are stacked vertically (no horizontal table); each line card is readable in full at 390px width; (c) supplier picker + Reference PO picker stack vertically; (d) Submit receipt button is reachable without horizontal scroll (the form's parent SectionCard wraps to viewport width); (e) success panel from Step 8 wraps gracefully — the 3-button nav cluster wraps to multiple lines on narrow screens via `flex-wrap`. |
| Actual | _(Tom fills — note any horizontal scrollbar appearing or any element clipped)_ |
| Screenshot | `[placeholder — capture full mobile view at 390px width]` |
| Pass / Fail | _(Tom fills)_ |
| Next-fix if FAIL | If horizontal scroll on context strip → check the strip's flex wrap classes at receipts/page.tsx (look for the strip block around line 690). If submit button overflows → the form's outer container needs `max-w-full` or `min-w-0`. If line cards too wide → check Tailwind responsive prefixes (sm:, md:) on the LineDraft container. |

---

## Summary template (Tom fills after walk)

| Step | Pass / Fail | Notes |
|------|-------------|-------|
| 1 — PO list Receipts column | _ | _ |
| 2 — PO detail CTA | _ | _ |
| 3 — CTA navigates to /stock/receipts?po_id= | _ | _ |
| 4 — PO context strip | _ | _ |
| 5 — Supplier picker locked + caption | _ | _ |
| 6 — Lines pre-loaded with open_qty | _ | _ |
| 7 — Edit qty downward + submit | _ | _ |
| 8 — Success panel + nav cluster | _ | _ |
| 9 — Back to PO shows updated status + qty | _ | _ |
| 10 — Movement log link works | _ | _ |
| 11 — Terminal PO empty-state guard | _ | _ |
| 12 — Mobile @ 390px | _ | _ |

**Overall verdict:** _(PASS / FAIL / PARTIAL — Tom fills)_

**Cycles to file as follow-up if any FAIL:** _(executor-w2 next dispatch will pick these up)_

---

## Known gaps (carried, not blocking this rehearsal)

- **W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL** (carried from cycle 12). The `/stock/movement-log` surface does not yet honor `?po_id=` filtering. The Step 10 link routes to the unfiltered ledger; the link's `title` attribute discloses this honestly. Closure of this gap is W1's call (a separate dispatch); when it lands, update Step 10's expected behavior + drop the tooltip disclosure.
- **Authenticated end-to-end smoke** — this checklist itself IS the closure for that. Once Tom executes it and fills in PASS for ≥ 10 of 12 steps, the GR/PO browser-flow corridor is browser-evidenced.

---

## Authorization basis

- EXECUTION_POLICY.md Mode B-Planning-Corridor 2026-05-02 amendment + cycle 16/17 dispatch carve-out enumerates `/stock/receipts` + `/purchase-orders/[po_id]` under Allowed surfaces.
- Signal #2 RUNTIME_READY(GoodsReceipt) (GR-era + Gate 3 closure pack) provides backend GR contract.
- W4 cycle 8 spec `Projects/gt-factory-os/docs/integrations/po_attached_gr_enhancement_spec.md` §3 + §4 verified readable on disk before authoring.
- Cycle 16 commit `223ba83` (window2-portal-sandbox/main) is the implementation under test.

This is an audit document. No portal source files were modified during its authoring.
