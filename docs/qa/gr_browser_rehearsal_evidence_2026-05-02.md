# Goods Receipt — Browser Rehearsal Static Evidence Pack (cycle 18, 2026-05-02; cycle 19 + 20 addenda)

> **Cycle 20 status (2026-05-02 late):** STATIC + MANUAL CHECKLIST READY — auth-session walk pending. The pack now carries (a) the cycle-18 static evidence per step (lines 18-197), (b) the cycle-19 Tom Manual Walkthrough Required addendum for steps 7-9 + bonus step 10 (lines 227-323), and (c) the cycle-20 Tom Walkthrough Plan (this addendum, at the bottom) — a 12-step end-to-end manual checklist with concrete deployed-Vercel URLs, action verbs, `data-testid` element identifiers, DOM/network expectations, failure modes, recovery paths, and pre-conditions to verify before starting. **This is NOT a browser-verified verdict.** No portal source under canonical sandbox was modified this cycle. Tom (or any admin with a real Supabase JWT) is the executor of the dynamic half.

> **Cycle 19 status (2026-05-02 evening):** STATIC PASS — auth-session walk pending.
> Steps 1-6, 10-12 statically verified PASS at cycle 18 commit 4234980. Steps 7-9 require Tom auth-session — see `## Tom Manual Walkthrough Required (cycle 19 addendum)` at the bottom of this file for an enumerated checklist with URLs, data-testids, expected DOM/network behavior, failure modes, and recovery paths.
> No portal source under test was modified for the evidence pack itself. Cycle 19 portal source change scope: `/stock/movement-log` po_id filter UI (separate concern; does not affect the GR rehearsal flow except that the cycle 16 success-panel "View movement log →" link now resolves end-to-end instead of routing to the unfiltered ledger).


> **Companion to:** `gr_browser_rehearsal_checklist_2026-05-02.md` (cycle 17, 235 lines, 12 steps).
>
> **Purpose.** The cycle 17 checklist is the operator instrument for capturing real browser-level behavior under a real Supabase JWT. This evidence pack supplies the **static (source-level) verification** for each of the 12 steps — citing exact files and line numbers in the canonical sandbox `window2-portal-sandbox/src/` — and explicitly flags which steps **REQUIRE TOM AUTH-SESSION** to capture true browser evidence (form submit, post-action panel render, runtime status update propagation, mobile viewport behavior at 390px).
>
> **Implementation under test:** `window2-portal-sandbox` commits `223ba83` (cycle 16 GR PO-prefill + simulation containment) and `4234980` (cycle 17 stale-comment fix on `/purchase-orders/[po_id]/page.tsx:1319-1323`). This pack is grounded in the on-disk source as of 2026-05-02; if either commit is rolled back the citations below would need re-validation.
>
> **What this pack does NOT do.** It does not replace the operator browser walk-through. Auth-gated dynamic behavior (TanStack Query refetch, server roundtrip, success-panel render, status flip post-submit, post-mobile-emulation reflow) cannot be statically verified — the React tree is internally consistent at the source level, but does not prove "the operator clicks this button and the next render is X". Tom (or any admin) is required to capture the dynamic half.

---

## Per-step static evidence

For each cycle-17 step: **route**, **action**, **expected**, **ACTUAL static evidence** (file + lines), and a **pass / fail / requires-auth-session** verdict.

---

### Step 1 — PO list shows Receipts summary column

| Field | Value |
|-------|-------|
| Route | `/purchase-orders` |
| Action | Open the PO list. Look at the `Receipts` column (between `Expected` and `Total net`). |
| Expected | Each PO row in its `Receipts` cell shows a received/ordered ratio in monospaced tabular numbers, a 1-line caption with line count, a 1px progress bar with `role="progressbar"` + `aria-valuenow/valuemin/valuemax`, a warning-toned `open` pill when `total_open_qty > 0`, and a neutral em-dash placeholder when `lines_summary` is undefined. |
| ACTUAL static evidence | `window2-portal-sandbox/src/app/(po)/purchase-orders/page.tsx` line 80 declares `lines_summary?: PurchaseOrderLinesSummary` on `PurchaseOrderRow`; line 842 renders the column header `"Receipts"`; lines 932 inserts `<LinesSummaryCell summary={r.lines_summary} />`; the `LinesSummaryCell` function at lines 201-266 implements: line 207 `<span className="text-fg-faint">—</span>` (neutral em-dash when `summary` undefined); lines 215-220 `lineCount === 0 → "No lines"` neutral; lines 223-237 ratio with `font-mono text-xs tabular-nums` (line 227) — `fmtQtyTrim(received)/fmtQtyTrim(ordered)` (lines 231-233) + `lineCount line(s)` caption (line 236); lines 239-258 progress bar with `role="progressbar"` (line 242) + `aria-valuenow={pct}` (line 243) + `aria-valuemin={0}` (line 244) + `aria-valuemax={100}` (line 245); lines 259-263 warning pill `text-warning-fg tabular-nums` rendered only when `open > 0`. Defensive em-dash and zero-line "No lines" both present per checklist requirement. |
| Pass / fail | **PASS (static)** — React tree exactly matches checklist expectation. |
| Requires Tom auth-session for | URL `https://gt-factory-os-portal.vercel.app/purchase-orders` (auth-gated 307 → /login). Tom must (a) sign in as operator/planner/admin; (b) confirm the `Receipts` column is visible; (c) confirm at least one row shows a non-em-dash ratio; (d) screenshot the column. |

---

### Step 2 — PO detail shows "Receive against this PO →" CTA

| Field | Value |
|-------|-------|
| Route | `/purchase-orders/[po_id]` |
| Action | Look at the `WorkflowHeader.actions` cluster (top-right). |
| Expected | A primary `btn-sm btn-primary` Link reading **"Receive against this PO →"**, `data-testid="po-receive-against-cta"`, `aria-label="Receive against PO {po_number}"`, `title` attribute disclosing over-receipt semantics. Visibility iff `po.status IN ('OPEN','PARTIAL')`. On RECEIVED/CANCELLED, the CTA is replaced by a `View receipts →` ghost Link. |
| ACTUAL static evidence | `window2-portal-sandbox/src/app/(po)/purchase-orders/[po_id]/page.tsx` lines 1325-1335: visibility guard `po && (po.status === "OPEN" \|\| po.status === "PARTIAL")` (line 1325); `<Link href={\`/stock/receipts?po_id=${encodeURIComponent(po_id)}\`} className="btn btn-sm btn-primary" data-testid="po-receive-against-cta" aria-label={\`Receive against PO ${po.po_number}\`} title="Receiving against this PO will update line balances atomically. Over-receipt is permitted but emits an exception for review.">Receive against this PO →</Link>` (lines 1326-1334). Lines 1336-1344: terminal-status branch — `po && (po.status === "RECEIVED" \|\| po.status === "CANCELLED")` (line 1336) renders ghost Link `View receipts →` (line 1342) with `data-testid="po-view-receipts-link"` (line 1340). Cycle 17 docblock at lines 1311-1324 cites W4 cycle 8 spec §3.1 (visibility) + POE-A13-1 (route decision, 95% confidence) + cycle 16 commit `223ba83` closure note. |
| Pass / fail | **PASS (static)** — exactly matches checklist expectation. |
| Requires Tom auth-session for | Confirming the CTA actually renders on a live OPEN/PARTIAL PO and is replaced by `View receipts →` on a RECEIVED/CANCELLED PO. Tom should hover over the CTA to verify the title-attribute over-receipt disclosure tooltip appears. |

---

### Step 3 — CTA navigates to `/stock/receipts?po_id=...`

| Field | Value |
|-------|-------|
| Route | `/purchase-orders/[po_id]` → `/stock/receipts?po_id=<uuid>` |
| Action | Click the "Receive against this PO →" CTA. |
| Expected | Browser URL becomes `/stock/receipts?po_id=<uuid>` (URL-encoded). No 404, no 500. |
| ACTUAL static evidence | `(po)/purchase-orders/[po_id]/page.tsx` line 1327: `href={\`/stock/receipts?po_id=${encodeURIComponent(po_id)}\`}`. The target route file `(ops)/stock/receipts/page.tsx` exists on disk (1,157 lines) and is the canonical Goods Receipt form; cycle-16 reconciliation confirmed there is no separate `/ops/stock/goods-receipt` route. Route group `(ops)` resolves to URL `/stock/receipts` per Next 15 App Router conventions. |
| Pass / fail | **PASS (static)** — href construction is correct, target route exists, encoding correct. |
| Requires Tom auth-session for | Confirming the actual click navigates correctly without an interstitial 401 or 5xx. HTTP probe at cycle 17 cycle exit confirmed the route is auth-gated and returns 307 → /login as expected; behind auth Tom must verify the URL bar shows `?po_id=<uuid>` after click. |

---

### Step 4 — PO context strip renders above the form

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Wait for form to load. Look at strip immediately above the form, below WorkflowHeader. |
| Expected | A horizontal context strip (`data-testid="receipts-po-context-strip"`) showing PO number in monospaced font, supplier name, expected delivery date if present, and a `← Back to PO` Link (`data-testid="receipts-po-back-to-po"`) routing to `/purchase-orders/[po_id]`. WorkflowHeader.eyebrow reads `Receiving against PO {po_number}`; description reads `From {supplier_name} · expected {date}.` (or just `From {supplier}.` if no date). |
| ACTUAL static evidence | `(ops)/stock/receipts/page.tsx` lines 685-713: render guard `urlPoLocked && !urlPoTerminal && urlPoHeader` (line 685); strip element with `className="mb-4 flex flex-wrap items-center gap-3 rounded-md border border-info/30 bg-info-softer/30 px-4 py-3 text-sm" role="note" data-testid="receipts-po-context-strip"` (lines 687-689); inside: `Receiving against PO <span className="font-mono">{urlPoHeader.po_number}</span>` (lines 691-694); supplier name `{urlPoHeader.supplier_name ?? urlPoHeader.supplier_id}` (line 696); conditional expected date (lines 698-702); back link `<Link href={\`/purchase-orders/${encodeURIComponent(urlPoHeader.po_id)}\`} className="btn btn-ghost btn-sm" data-testid="receipts-po-back-to-po">← Back to PO</Link>` (lines 704-710). WorkflowHeader.eyebrow conditional at line 593: `urlPoLocked && urlPoHeader ? \`Receiving against PO ${urlPoHeader.po_number}\` : "Operator form"`; description conditional at lines 595-599: `urlPoLocked && urlPoHeader ? \`From ${urlPoHeader.supplier_name ?? urlPoHeader.supplier_id}${urlPoHeader.expected_receive_date ? \` · expected ${urlPoHeader.expected_receive_date}\` : ""}.\` : "Record physical goods arrival. Partial receipts are supported."`. `urlPoId` derivation: line 248 `const urlPoId = searchParams?.get("po_id") ?? "";`; `urlPoLocked` flag: line 341 `const urlPoLocked = Boolean(urlPoId);`. |
| Pass / fail | **PASS (static)** — strip + eyebrow + description all match checklist. Info-tone `border-info/30 bg-info-softer/30` is visually distinct from posted-stock and matches the secondary-overlay convention. |
| Requires Tom auth-session for | Confirming the strip actually renders post-fetch (not stuck in `poHeaderQuery.isLoading` skeleton at lines 651-655 or `poHeaderQuery.isError` panel at lines 656-684). Tom should also verify the WorkflowHeader.eyebrow and description text are correct for the chosen PO. |

---

### Step 5 — Supplier picker is locked with caption

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Scroll to form. Inspect supplier `<select>`. |
| Expected | Supplier `<select>` is **disabled** with current value matching the PO's supplier; below it a caption reads `From PO {po_number} — supplier locked.`; caption has `id="receipt-supplier-locked-caption"`; select has `aria-describedby="receipt-supplier-locked-caption"`. Reference-PO picker is also disabled with a synthetic option for the URL-supplied PO if outside the OPEN/PARTIAL filter. |
| ACTUAL static evidence | Supplier select at `(ops)/stock/receipts/page.tsx` lines 836-851: `<select className="input" value={supplierId} onChange={...} required disabled={urlPoLocked} data-testid="receipt-supplier-select" aria-describedby={urlPoLocked && urlPoHeader ? "receipt-supplier-locked-caption" : undefined}>` (lines 836-844). Locked caption rendered conditionally at lines 852-859: `urlPoLocked && urlPoHeader ? <span id="receipt-supplier-locked-caption" className="mt-1 block text-3xs text-fg-muted">From PO {urlPoHeader.po_number} — supplier locked.</span> : null`. Supplier prefill effect at lines 384-434 sets `setSupplierId(urlPoHeader.supplier_id)` on line 392. Reference-PO select (lines 865-891): `disabled={urlPoLocked}` (line 870); synthetic option block at lines 884-890 — when `urlPoLocked && urlPoHeader && !(openPosQuery.data?.rows ?? []).some(p => p.po_id === urlPoHeader.po_id)`, renders one synthetic `<option key={urlPoHeader.po_id} value={urlPoHeader.po_id}>{po_number} · {supplier_id} · {status}</option>`. |
| Pass / fail | **PASS (static)** — disabled state, caption text, ARIA wiring, and synthetic option logic all match checklist. |
| Requires Tom auth-session for | Confirming the supplier `<select>` is visually greyed out at the live URL and that clicking it does not open a dropdown. Confirming the caption renders below the select. Confirming the Reference PO picker shows the URL-supplied PO as selected. |

---

### Step 6 — PO lines pre-loaded with received_qty = open_qty

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Look at `Lines` SectionCard. Count pre-rendered draft rows. |
| Expected | One `LineDraft` row per OPEN/PARTIAL PO line; CLOSED + CANCELLED filtered. Each draft's `quantity` = corresponding line's `open_qty`; `unit` = PO line's `uom`; `po_line_id` wired (verifiable via linked-PO-line `<select>`); `receivable_key` = `component:{component_id}` then fallback `item:{item_id}` then empty. |
| ACTUAL static evidence | Prefill effect at `(ops)/stock/receipts/page.tsx` lines 384-434, gated by `urlPoLocked && !prefillApplied && !urlPoTerminal && urlPoHeader && !poDetailQuery.isLoading` (lines 385-389). Filter: `poLines.filter(pl => pl.line_status === "OPEN" \|\| pl.line_status === "PARTIAL")` (lines 398-400) — explicitly excludes CLOSED + CANCELLED. Empty-eligible short-circuit at lines 401-406 sets `setPrefillApplied(true)` and returns. Draft mapping at lines 407-423: `receivable_key = pl.component_id ? \`component:${pl.component_id}\` : pl.item_id ? \`item:${pl.item_id}\` : ""` (lines 408-412); `unit = (UOMS as readonly string[]).includes(pl.uom) ? (pl.uom as Uom) : "UNIT"` (lines 413-415); each draft: `{ receivable_key: key, quantity: pl.open_qty, unit, notes: "", po_line_id: pl.po_line_id }` (lines 416-422). `setLines(drafts)` (line 424) replaces the initial empty draft. `setPrefillApplied(true)` guards re-runs. |
| Pass / fail | **PASS (static)** — receivable_key fallback chain, quantity = open_qty, unit from PO line, po_line_id wired, status filter, and prefill-once guard all match checklist. |
| Requires Tom auth-session for | Confirming the actual count of pre-rendered drafts matches the count of OPEN/PARTIAL PO lines on the chosen PO; confirming each draft's quantity input is pre-filled with the line's open_qty value (not blank); confirming the linked-PO-line `<select>` shows the matching PO line metadata. |

---

### Step 7 — Edit one line's qty downward (partial), submit

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | Edit one line's quantity downward + click Submit receipt. |
| Expected | Submit button changes to `Submitting…` (disabled). Form posts to `/api/goods-receipts` proxy. On success: page transitions out of `submitting` phase. |
| ACTUAL static evidence | This step is **dynamic** — it requires (a) operator interaction (mutating the qty input) and (b) a real backend roundtrip. Static evidence: the LineDraft rows render editable `<input>` elements (the prefill seeds `quantity` to the PO line's `open_qty`, and the operator can decrease this freely). Submit handler at `(ops)/stock/receipts/page.tsx` exists in the same file (the cycle-16 implementation routes through a `/api/goods-receipts` proxy → `POST /api/v1/mutations/goods-receipts`). The submit button transitions through `phase: "idle" \| "submitting" \| "done"` and renders `Submitting…` (disabled) during the in-flight request. Network-error fallback at lines 580-587 sets `done = { kind: "error", message: "Network error submitting receipt.", detail: ... }`. |
| Pass / fail | **REQUIRES TOM AUTH-SESSION** — static reading confirms the submit code path exists and the network-error fallback is wired, but the actual 200/4xx/5xx response handling and ledger-write side effects can only be observed under live auth. |
| Requires Tom auth-session for | (a) Confirming Submit triggers a network call; (b) confirming the proxy forwards correctly; (c) confirming the response is 200 (success) and not 401/403/422/409/503 with operator-friendly error rendering; (d) confirming the page transitions to the success state with a real `committed.po_id` from the backend. |

---

### Step 8 — Success panel renders with posted ledger movement count + nav cluster

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | After Step 7 success, inspect success panel. |
| Expected | Green-toned panel (`data-testid="receipt-success-panel"`) with success message, itemSummary line, detail line `ref: {submission_id} · N line(s)`, and a 3-button nav cluster: `Back to PO {po_number} →` (`data-testid="receipt-success-back-to-po"`), `View receipts on this PO →` (`data-testid="receipt-success-view-attached-grs"`), and `View movement log →` (`data-testid="receipt-success-view-movement-log"`) with honest title-attribute disclosure. |
| ACTUAL static evidence | Success panel at `(ops)/stock/receipts/page.tsx` lines 715-781. Outer wrapper (lines 716-729): `done.kind === "success" → border-success/40 bg-success-softer text-success-fg` (lines 719-722); `data-testid="receipt-success-panel"` (line 727 conditional). Message + itemSummary + detail rendered at lines 730-740. Nav cluster guard at line 746: `done.kind === "success" && done.poId`. Cluster wrapper: `<div className="mt-3 flex flex-wrap items-center gap-2">` (line 747). Three Links: (1) `<Link href={\`/purchase-orders/${encodeURIComponent(done.poId)}\`} ... data-testid="receipt-success-back-to-po">Back to PO{done.poNumber ? \` ${done.poNumber}\` : ""} →</Link>` (lines 748-754); (2) `<Link href={\`/purchase-orders/${encodeURIComponent(done.poId)}?tab=attached-grs\`} ... data-testid="receipt-success-view-attached-grs">View receipts on this PO →</Link>` (lines 755-761); (3) movement-log link at lines 770-777 — `href={\`/stock/movement-log?po_id=${encodeURIComponent(done.poId)}\`} ... data-testid="receipt-success-view-movement-log" title="Filter by po_id is not yet supported on the movement log; the link routes to the unfiltered ledger."`. The disclosure docblock at lines 762-769 explains the W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL gap. The success branch sets `poId = committed.po_id` and `poNumber = urlPoHeader?.po_number ?? undefined` (line 562). |
| Pass / fail | **REQUIRES TOM AUTH-SESSION** — the panel JSX is correctly wired and all three nav links are present in source, but rendering depends on a successful Step-7 submit reaching `done.kind === "success" && done.poId`. |
| Requires Tom auth-session for | Confirming the success panel renders post-submit; confirming the 3-button nav cluster is visible; confirming the title-attribute disclosure on the movement-log link is present (hover state); confirming `done.poId` is populated from the backend response. |

---

### Step 9 — "Back to PO {po_number} →" navigation shows updated received_qty + line_status

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` → `/purchase-orders/[po_id]` |
| Action | Click `Back to PO {po_number} →` button. |
| Expected | Browser navigates to `/purchase-orders/[po_id]`. PO detail renders with updated status (`PARTIAL` if remaining > 0; `RECEIVED` if zero) + lines section reflects new received_qty. CTA flips from `Receive against this PO →` to `View receipts →` if status is now `RECEIVED`. |
| ACTUAL static evidence | The link at `(ops)/stock/receipts/page.tsx` lines 748-754 routes correctly to `/purchase-orders/${encodeURIComponent(done.poId)}`. The back-link target route is the same `(po)/purchase-orders/[po_id]/page.tsx` page that was the entry point in Step 2; that page's status-rollup logic (lines 1325 OPEN/PARTIAL guard, lines 1336 RECEIVED/CANCELLED guard) automatically reads from the PO header response and renders the appropriate CTA. The status flip itself is a backend concern: GR posts trigger `fn_post_goods_receipt` which updates `purchase_order_lines.received_qty` (cycle 9 W1 cycle, migration 0085). |
| Pass / fail | **REQUIRES TOM AUTH-SESSION** — link target and CTA flip logic are statically correct, but verifying the actual updated `received_qty` value rendered in the lines section and the actual status badge transition requires live data + TanStack Query refetch + backend rollup. |
| Requires Tom auth-session for | (a) Verify navigation succeeds; (b) verify the PO detail header shows updated status (likely `PARTIAL` for downward-edit, `RECEIVED` for full); (c) verify the affected line's received_qty matches the GR posted in Step 7; (d) verify the CTA at line 1325 either still renders (status still OPEN/PARTIAL) or is replaced by `View receipts →` (status now RECEIVED). If TanStack Query cache is stale, force-refresh (Ctrl+Shift+R). |

---

### Step 10 — "View movement log →" link works (unfiltered)

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` (success panel) |
| Action | Click "View movement log →" link. |
| Expected | Browser navigates to `/stock/movement-log?po_id=<uuid>`. Movement log page renders unfiltered (`po_id` not yet honored). Link's `title` attribute discloses honestly. |
| ACTUAL static evidence | Movement-log link at `(ops)/stock/receipts/page.tsx` lines 770-777: `href={\`/stock/movement-log?po_id=${encodeURIComponent(done.poId)}\`}` (line 771); `data-testid="receipt-success-view-movement-log"` (line 773); `title="Filter by po_id is not yet supported on the movement log; the link routes to the unfiltered ledger."` (line 774). The disclosure docblock at lines 762-769 explicitly cites the W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL gap (carried from cycle 12). The target route `/stock/movement-log` is documented as agnostic to `po_id` — verifying the route exists is a separate audit (cycle 17 active_mode confirmed it as a known carried gap). |
| Pass / fail | **PASS (static)** for the link construction + honest disclosure. The unfiltered behavior is the documented expected behavior per the cited W1 follow-up. |
| Requires Tom auth-session for | (a) Hover over the link to confirm the `title` tooltip appears with the disclosure copy; (b) click the link to confirm navigation succeeds (no 404); (c) observe that the movement log page shows the unfiltered ledger (this is the documented behavior pending W1 cycle to add `?po_id=` filtering). |

---

### Step 11 — Terminal PO direct-URL → "View receipts →" empty-state guard

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid-of-RECEIVED-or-CANCELLED-PO>` |
| Action | Paste URL pointing at terminal PO. Hit enter. |
| Expected | Form NOT rendered. Instead, a SectionCard with title `PO {po_number} cannot accept further receipts` (`data-testid="receipts-po-terminal-guard"`) and three affordances: `View receipts →` (`data-testid="receipts-po-terminal-view-receipts"`), `Back to PO detail`, `Start a manual receipt` (`data-testid="receipts-po-terminal-clear-link"`). |
| ACTUAL static evidence | Terminal guard at `(ops)/stock/receipts/page.tsx` lines 606-644. Render guard: `urlPoLocked && urlPoTerminal && urlPoHeader` (line 606). `urlPoTerminal` derivation: lines 372-374 `const urlPoTerminal = urlPoHeader !== null && (urlPoHeader.status === "RECEIVED" \|\| urlPoHeader.status === "CANCELLED");`. SectionCard title: `PO {urlPoHeader.po_number} cannot accept further receipts` (line 607). Inner panel: `<div className="rounded-md border border-border/60 bg-bg-raised p-4 text-sm" role="status" data-testid="receipts-po-terminal-guard">` (lines 608-612). Body lines 613-619: status-aware text `This PO is in {RECEIVED → "Received" : "Cancelled"} state.` + `No additional goods receipts may be posted against PO {po_number} ({supplier_name}).`. Three affordances at lines 620-641: (1) `<Link href={...?tab=attached-grs} className="btn btn-sm btn-primary" data-testid="receipts-po-terminal-view-receipts">View receipts →</Link>` (lines 621-627); (2) `<Link href={\`/purchase-orders/${encodeURIComponent(urlPoHeader.po_id)}\`} className="btn btn-ghost btn-sm">Back to PO detail</Link>` (lines 628-633); (3) `<Link href="/stock/receipts" className="btn btn-ghost btn-sm" data-testid="receipts-po-terminal-clear-link">Start a manual receipt</Link>` (lines 634-640). The form rendering itself (line 783 onward) is structurally untouched — but is hidden whenever the guard renders, since the guard panel is the first conditional element at line 606. |
| Pass / fail | **PASS (static)** — guard logic, copy, and three affordances all match checklist. |
| Requires Tom auth-session for | Tom must (a) find a real RECEIVED or CANCELLED PO (e.g. via `/purchase-orders?status=RECEIVED` filter); (b) construct the URL `/stock/receipts?po_id=<that-po-uuid>` directly; (c) confirm the form does NOT render and the terminal guard panel does. |

---

### Step 12 — Mobile @ 390px — sticky elements, line cards, submit button reachable

| Field | Value |
|-------|-------|
| Route | `/stock/receipts?po_id=<uuid>` |
| Action | DevTools → 390px width emulation. Reload. |
| Expected | (a) PO context strip remains visible without horizontal scroll; (b) line cards stack vertically; (c) supplier + reference-PO pickers stack vertically; (d) Submit button reachable; (e) success-panel nav cluster wraps to multiple lines. |
| ACTUAL static evidence (CSS-class analysis) | `(ops)/stock/receipts/page.tsx` mobile-relevant Tailwind class signatures: (a) **PO context strip** at line 687 uses `className="mb-4 flex flex-wrap items-center gap-3 rounded-md border border-info/30 bg-info-softer/30 px-4 py-3 text-sm"` — `flex-wrap` ensures the strip's items (PO label, supplier, expected date, back-link) wrap to multiple lines on narrow viewports without horizontal scroll. (b) **Form field grids** at lines 786-819: lines 786 + 791 + 819 all use `grid grid-cols-1 gap-3 sm:grid-cols-2` or `sm:grid-cols-3` — at viewports below the `sm` breakpoint (640px in default Tailwind), the grid collapses to a single column, stacking fields vertically. The 390px viewport is below 640px, so single-column layout applies. (c) **Supplier + Reference PO selects** at lines 836-851 + 865-891: each is wrapped in a `<label className="block min-w-0">` (line 832) or `block min-w-0 sm:col-span-2` (line 861, 910); the `min-w-0` ensures the label container can shrink below its content's intrinsic width, preventing horizontal overflow on narrow screens. (d) **Submit button** + form container: the form is wrapped in `<SectionCard>` which is a flex/block container that takes the parent width; no fixed-width or `min-w-[…]` is imposed at the form-level wrapper. (e) **Success-panel nav cluster** at line 747: `<div className="mt-3 flex flex-wrap items-center gap-2">` — `flex-wrap` makes the three Link buttons reflow to multiple rows when their combined width exceeds the panel's parent width, which is guaranteed at 390px. (f) **Terminal-guard affordances** at line 620: `<div className="mt-3 flex flex-wrap items-center gap-2">` — same reflow guarantee. |
| Pass / fail | **PASS (static, CSS-class level)** — every region cited in the mobile checklist uses `flex-wrap`, `grid-cols-1` (mobile) → `sm:grid-cols-N` (tablet+), or `min-w-0` to enable native reflow at 390px. There is no fixed-width container, no `overflow-x-scroll`, and no horizontal table on this page. |
| Requires Tom auth-session for | (a) Toggle DevTools device emulation to a 390px-wide viewport (e.g. iPhone 12 Pro); (b) reload; (c) confirm visual reflow matches the static prediction — no horizontal scrollbar, no clipped element, all interactive elements tap-friendly. CSS-class analysis cannot prove there is no overflow at runtime (e.g. due to a long PO number wrapping awkwardly), only that the class soup is correctly biased toward reflow. |

---

## Auth-required-step summary

| Step | Static verdict | Auth-required for |
|------|---------------|-------------------|
| 1 — PO list Receipts column | PASS (static) | Visual confirmation under operator/planner/admin role |
| 2 — PO detail CTA | PASS (static) | Visual + tooltip hover |
| 3 — CTA navigation | PASS (static) | Click navigation + URL bar verify |
| 4 — PO context strip | PASS (static) | Strip render post-fetch + eyebrow text |
| 5 — Supplier picker locked | PASS (static) | Disabled state + caption render |
| 6 — Lines pre-loaded | PASS (static) | Per-draft qty/unit/po_line_id verify |
| 7 — Edit + submit | **REQUIRES TOM AUTH-SESSION** | Backend roundtrip + response handling |
| 8 — Success panel + nav cluster | **REQUIRES TOM AUTH-SESSION** | Panel render + 3-button cluster + tooltip |
| 9 — Back to PO + updated status | **REQUIRES TOM AUTH-SESSION** | Status flip + received_qty update |
| 10 — Movement log link | PASS (static) | Hover tooltip + click navigation |
| 11 — Terminal PO guard | PASS (static) | Direct-URL load with terminal PO |
| 12 — Mobile @ 390px | PASS (static, CSS-class) | DevTools emulation reflow verify |

**Static verdict.** Steps 1, 2, 3, 4, 5, 6, 10, 11, and 12 are statically verified PASS — the React tree, ARIA wiring, link construction, conditional render guards, and Tailwind CSS classes all correctly match the cycle-17 checklist's expected behavior. Steps 7, 8, and 9 require Tom auth-session walk-through to capture true browser evidence — they depend on a real Supabase JWT, a backend roundtrip, and post-mutation TanStack Query cache propagation that cannot be statically simulated.

---

## Surgical fix attempted during static inspection

**None applied this cycle.** Static inspection identified zero defects: every cited element exists at the cited line numbers, ARIA attributes are correct, conditional render guards are correctly composed, and Tailwind classes are correctly biased toward mobile reflow. The cycle 17 commit `4234980` already closed the only stale-comment defect identified in cycle 17 (the W2-FOLLOWUP-RECEIPTS-PO-PREFILL claim at `(po)/purchase-orders/[po_id]/page.tsx:1319-1323` now correctly cites cycle 16 closure). No additional small surgical fix is warranted — the implementation is internally consistent.

---

## Verdict

**Steps 1, 2, 3, 4, 5, 6, 10, 11, and 12 statically verified PASS** against canonical sandbox source as of cycle 17 commit `4234980` (parent `223ba83`). **Steps 7, 8, and 9 require Tom auth-session walk-through** to capture true browser evidence — they depend on a real backend roundtrip and post-mutation state propagation that cannot be inspected statically.

The `gr_browser_rehearsal_checklist_2026-05-02.md` cycle-17 checklist remains the operator instrument for capturing the dynamic half. This evidence pack is the static prerequisite — it confirms the React tree is correctly wired before Tom invests in the auth-gated walk-through.

---

## Authorization basis

- EXECUTION_POLICY.md Mode B-Planning-Corridor 2026-05-02 amendment + cycle 18 dispatch carve-out enumerates `/stock/receipts` + `/purchase-orders/[po_id]` static audit + `PRODUCTION/docs/qa/` under Allowed surfaces.
- Signal #2 RUNTIME_READY(GoodsReceipt) (Gate 3 closure pack) provides backend GR contract.
- Cycle 16 commit `223ba83` (`window2-portal-sandbox/main`) is the implementation under test.
- Cycle 17 commit `4234980` (`window2-portal-sandbox/main`) is the stale-comment fix on `(po)/purchase-orders/[po_id]/page.tsx`.
- W4 cycle 8 spec `Projects/gt-factory-os/docs/integrations/po_attached_gr_enhancement_spec.md` §3 + §4 verified as the contract under which the cycle 16 implementation was authored.

This is an audit document. No portal source files were modified during its authoring.

---

## Tom Manual Walkthrough Required (cycle 19 addendum)

Cycle 19 dispatch directive: "If browser is available: execute steps 7-9 of the checklist. ... If browser is not available: provide exact manual checklist and do not call it browser-verified."

The agent does not have an authenticated browser session against the deployed Vercel portal. This addendum supplies a structured checklist Tom (or any admin with a real Supabase JWT) can follow to capture the dynamic evidence the static pack above cannot produce.

**Pre-conditions** (must hold before walking these steps):
- P-1. Portal commit on `window2-portal-sandbox/main` ≥ 4234980 (cycle 17). Cycle 19 commit will add a movement-log filter; not strictly required for steps 7-9 but useful for step 10 retest.
- P-2. Backend on `gt-factory-os-api` Railway deploy ≥ cycle 18 commit on `main` (handler-level po_id filter on `/api/v1/queries/stock/ledger`; for steps 7-9 themselves the backend `goods_receipts` mutations endpoint is what matters — that has been live since Gate 3 closure).
- P-3. Auth role: operator, planner, or admin (NOT viewer — viewer is read-only and cannot submit). Tom signs in via `/login` magic-link.
- P-4. At least one OPEN PO with at least 1 OPEN/PARTIAL line, ideally 2+ lines so step 7's "edit one line downward" is a meaningful partial-receipt test.
- P-5. (Optional, for terminal-guard regression at step 11) at least one RECEIVED or CANCELLED PO; Tom can construct a URL `/stock/receipts?po_id=<that-po-id>` directly to exercise that branch.

For each step below: URL → action → element to look for (with `data-testid` + visible text) → DOM/network expectation → failure modes → recovery path.

---

### Step 7 (manual) — Edit one line's qty downward (partial), submit

| Field | Value |
|-------|-------|
| URL | `https://gt-factory-os-portal.vercel.app/stock/receipts?po_id=<your-OPEN-PO-id>` |
| Action | Wait for prefill. Pick one LineDraft row. Decrease its quantity input by any value > 0 (e.g. if `open_qty = 100`, set quantity to `60`). Click `Submit receipt`. |
| Element to look for (pre-submit) | `<button type="submit">` reading `Submit receipt`. After click, button text flips to `Submitting…` and is `disabled`. |
| DOM/network expectation | (a) Network tab shows `POST /api/goods-receipts` (portal proxy) → upstream `POST /api/v1/mutations/goods-receipts`. (b) Request body JSON includes top-level `po_id` (the URL-supplied uuid), `supplier_id` (auto-prefilled from PO header), `lines[]` array with one entry per draft row, each carrying `po_line_id`, `quantity`, `unit`, `notes`. (c) Response status 200 with body `{ submission_id, po_id, po_number?, lines: [{...}] }`. (d) On success, the page leaves `phase: "submitting"` and renders the green success panel (verified at step 8). |
| Failure modes | **401** = auth expired → Tom signs in again. **403** = role insufficient → use operator/planner/admin. **422** = Zod validation fail → check the request body shape against schema; usually means a draft has `quantity = 0` or non-numeric. **409 ITEM_TYPE_MISMATCH / PO_LINE_PARENT_MISMATCH** = receivable_key resolution picked a wrong row (rare; usually points to a master-data issue on the PO line). **5xx** = backend down → check Railway logs. **Network error** = portal alone shows `done.kind === "error"` with `Network error submitting receipt.` red panel + Retry-friendly state. |
| Recovery path | If the submit fails, the form does NOT clear — operator can correct fields and re-submit. The PO context strip + supplier lock remain intact. If TanStack Query somehow desynced, `Ctrl+Shift+R` reloads `?po_id=<uuid>` and re-prefills cleanly. |
| Pass criteria | (i) `Submitting…` rendered between click and response; (ii) on 200, the green success panel appears at step 8; (iii) on 4xx/5xx, the red error panel appears with parsable `detail`; (iv) NO unhandled exception in browser console. |
| Screenshot to capture | (a) Pre-submit form with the edited quantity highlighted; (b) post-submit success panel OR error panel. |

---

### Step 8 (manual) — Success panel renders with posted ledger movement count + nav cluster

| Field | Value |
|-------|-------|
| URL | Same `/stock/receipts?po_id=<uuid>` after step 7 success — page does not navigate; the success panel replaces (or is rendered alongside) the form region. |
| Action | After step 7 returns 200, scroll to (or stay on) the panel that just appeared. |
| Element to look for | Outer wrapper has `data-testid="receipt-success-panel"`. Inside it: a green-toned heading line (success message), an itemSummary line (count of posted lines), a detail line `ref: {submission_id} · N line(s)`, and a 3-button nav cluster. Cluster buttons by data-testid: `receipt-success-back-to-po`, `receipt-success-view-attached-grs`, `receipt-success-view-movement-log`. Visible text on each: `Back to PO {po_number} →`, `View receipts on this PO →`, `View movement log →`. |
| DOM/network expectation | (a) `done.poId` populated from the backend response (`committed.po_id`). If empty, the nav cluster does not render — that is a backend response issue, not a portal bug. (b) Hovering over the `View movement log →` link shows the cycle 19 title attribute `View ledger movements scoped to this PO.` (replaced the cycle 16 honest-disclosure copy). (c) No flicker / no "stuck spinner" overlay. |
| Failure modes | **No panel appears** = the response branched to error or `done.poId` is missing → check network tab for the response body. **Wrong text on movement-log title** = browser cached cycle 16 build → hard reload or check Vercel deployment SHA. **Nav cluster shows but Back-to-PO link is dead** = `done.poId` empty → same root cause. |
| Recovery path | If the success panel fails to render after a 200 response, file as a separate W2 cycle defect (DTO contract drift between W1 GR mutation handler and portal `done.poId` extraction). If the title attribute still says "Filter by po_id is not yet supported", the cycle 19 commit has not yet deployed to Vercel — wait for the auto-deploy. |
| Pass criteria | (i) `data-testid="receipt-success-panel"` visible; (ii) all 3 nav-cluster buttons present and clickable; (iii) hover tooltip on movement-log link shows the cycle 19 copy; (iv) Submit button no longer says `Submitting…`. |
| Screenshot to capture | The full success panel including all 3 buttons. |

---

### Step 9 (manual) — "Back to PO {po_number} →" navigation shows updated received_qty + line_status

| Field | Value |
|-------|-------|
| URL | Click `receipt-success-back-to-po` → browser navigates to `/purchase-orders/<po-id>`. |
| Action | After step 8, click the leftmost button. |
| Element to look for | (a) URL bar shows `/purchase-orders/<po-id>` (no `?po_id=` query string). (b) PO detail page header eyebrow text reads the canonical `PO {po_number}`. (c) Status badge near the top now reads either `PARTIAL` (if step 7 was a partial-qty edit and ≥1 line still has `open_qty > 0`) or `RECEIVED` (if step 7 fully closed every line on this PO). (d) Lines section table renders updated `received_qty` and `line_status` for the line edited in step 7. (e) The CTA at the top of the page (`po-receive-against-cta`) either still renders (if status is still OPEN/PARTIAL) or is replaced by the ghost `View receipts →` link (`po-view-receipts-link`) if status is now RECEIVED. |
| DOM/network expectation | (a) On navigation, `GET /api/purchase-orders/<po-id>` fires; response carries the rolled-up `received_qty` and `line_status` per line. (b) TanStack Query may serve a stale cache on first paint — if the values look unchanged, force-refresh (Ctrl+Shift+R). (c) The header status badge uses the same status enum the CTA visibility branches on. |
| Failure modes | **Stale received_qty / line_status** = TanStack Query cache hit before backend rollup completed → hard reload. **Status badge reads `OPEN` after a full receipt** = `fn_post_goods_receipt` rollup did not fire (W1 backend defect — check `received_qty`-by-line; if all lines closed but PO header still OPEN, this is a W1 cycle defect to log). **CTA still says `Receive against this PO →` after a full receipt** = same root cause (PO status didn't flip). |
| Recovery path | If status flip is wrong, capture: (a) the values in the lines table; (b) the status badge text; (c) hard-reload result. If hard-reload fixes it → portal cache issue; if hard-reload still wrong → backend rollup defect (W1). |
| Pass criteria | (i) URL changes to `/purchase-orders/<po-id>`; (ii) lines table reflects step 7's edit (the affected line's `received_qty` increased by the qty submitted); (iii) status badge correctly reads `PARTIAL` or `RECEIVED` per the math; (iv) CTA visibility correct per status. |
| Screenshot to capture | The PO detail header (status + CTA region) plus the affected line row in the lines table. |

---

### Bonus: Step 10 retest under cycle 19 (movement log filter)

The cycle 18 evidence pack had Step 10 as PASS-static for the link existing and routing to the unfiltered ledger. **Cycle 19 changes this**: the `/stock/movement-log` page now consumes `?po_id=` from the URL and shows an active filter chip.

| Field | Value |
|-------|-------|
| URL | After step 8 success, click `receipt-success-view-movement-log`. |
| Action | Observe the resulting page. |
| Element to look for | (a) URL bar shows `/stock/movement-log?po_id=<uuid>`. (b) New element with `data-testid="movement-log-po-filter-chip"`: info-tone bordered strip at the top of the page, before the `Search Movements` filter card. Visible text: `Filtered by PO:` followed by the human-readable po_number (e.g. `PO-2026-00112`) in monospace, optionally followed by `· {supplier_name}` and `· {status}`. (c) On the right of the chip: a `Back to PO →` link (`movement-log-po-filter-back-link`) and a `Clear filter` button (`movement-log-po-filter-clear`). (d) The ledger table below the chip shows ONLY movements whose `related_po_line_id` belongs to a PO line under that PO (typically GR_POSTED rows from the just-submitted receipt). |
| DOM/network expectation | (a) `GET /api/stock/ledger?po_id=<uuid>&limit=100&offset=0` fires and returns rows scoped to that PO. (b) `GET /api/purchase-orders/<uuid>` fires in parallel for the chip's po_number resolution; if it errors, the chip falls back to displaying the raw uuid (graceful degradation). (c) Clicking `Clear filter` calls `router.replace("/stock/movement-log")` — URL updates, chip disappears, and the table re-fetches unfiltered. |
| Failure modes | **Chip does not render** = `?po_id=` not on URL (dead-link regression on the success-panel `<Link>`) → check `done.poId` extraction. **Chip shows raw uuid not po_number** = the PO header lookup failed (auth, network, or PO truly missing) → graceful fallback expected. **Empty ledger after a successful step 7** = backend GR write succeeded but ledger postings haven't propagated yet (timing) → empty-state copy says "No movements found for PO {x}. The PO may not have ledger postings yet, or you may have over-receipt exceptions."; refresh in 2-3 seconds. **`Clear filter` button doesn't drop the param** = `router.replace` failure (rare) → manually edit the URL to remove `?po_id=`. |
| Recovery path | If the chip is broken, the page still functions: the per-field filters in the SectionCard work independently. If the empty state shows but you expected rows, hard-reload after a few seconds; if still empty, the GR may have failed at the ledger-write step (W1 defect). |
| Pass criteria | (i) Chip renders with resolved po_number when PO header endpoint is reachable; (ii) ledger table shows only PO-scoped movements; (iii) `Clear filter` cleanly returns to the unfiltered view; (iv) empty state copy reads correctly when 0 rows match. |
| Screenshot to capture | The chip + the first few ledger rows below it. |

---

### Auth-required-step summary (cycle 19 update)

| Step | Cycle 18 verdict | Cycle 19 status |
|------|-----------------|-----------------|
| 1 — PO list Receipts column | PASS (static) | unchanged — still PASS-static; auth-session walk pending |
| 2 — PO detail CTA | PASS (static) | unchanged |
| 3 — CTA navigation | PASS (static) | unchanged |
| 4 — PO context strip | PASS (static) | unchanged |
| 5 — Supplier picker locked | PASS (static) | unchanged |
| 6 — Lines pre-loaded | PASS (static) | unchanged |
| **7 — Edit + submit** | **REQUIRES AUTH-SESSION** | **STILL REQUIRES AUTH-SESSION** — see manual checklist above |
| **8 — Success panel + nav cluster** | **REQUIRES AUTH-SESSION** | **STILL REQUIRES AUTH-SESSION** — note title-attribute copy refresh under cycle 19 |
| **9 — Back to PO + updated status** | **REQUIRES AUTH-SESSION** | **STILL REQUIRES AUTH-SESSION** — see manual checklist above |
| 10 — Movement log link | PASS (static) | **CHANGED behavior under cycle 19** — link now drives a filtered ledger view; see Bonus section above |
| 11 — Terminal PO guard | PASS (static) | unchanged |
| 12 — Mobile @ 390px | PASS (static, CSS-class) | unchanged; cycle 19 movement-log chip added — `flex flex-wrap` on the chip element ensures clean reflow at 390px |

**Cycle 19 verdict on this evidence pack: STATIC PASS — auth-session walk pending.** This is NOT a browser-verified verdict. Tom (or any admin with a real Supabase JWT) executes the manual checklist above to convert this to a fully browser-verified PASS.

---

## Cycle 20 Tom Walkthrough Plan

> **Mode B-Planning-Corridor cycle 20 dispatch directive:** "Tom continues to require browser-level evidence. You don't have an authenticated browser. So produce a structured manual checklist Tom can execute and capture evidence from."
>
> **The agent does not have an authenticated browser session.** This addendum is the cycle 20 reformulation of the Tom-walk for **all 12 steps** of the original cycle 17 checklist plus the cycle 19 bonus step 10 retest. Each step gives: concrete URL, action verb (click / type / submit), specific element identification (`data-testid` + visible text), DOM/network expectation, failure modes, and recovery if it fails.
>
> This is a **manual-checklist-ready** instrument, not browser-verified evidence. Verdict on this cycle 20 addendum: **STATIC + MANUAL CHECKLIST READY — auth-session walk pending.**

### Pre-conditions (verify before starting)

Tom must verify all five pre-conditions before walking the 12 steps. If any fails, do not walk — report and halt.

| # | Pre-condition | How to verify | Failure recovery |
|---|---------------|---------------|------------------|
| P-1 | Portal commit on Vercel ≥ `bfebdfc` (cycle 19 movement-log po_id filter UI) | (a) Visit `https://gt-factory-os-portal.vercel.app/`. (b) Open browser devtools → Network tab → reload → click any HTML response → inspect `x-vercel-deployment-url` or `x-vercel-id` header. (c) Cross-reference with the Vercel deployment list at https://vercel.com/<team>/gt-factory-os-portal/deployments — the live deployment must point at a `window2-portal-sandbox` commit on `main` ≥ `bfebdfc` (cycle 19) | If older: trigger a re-deploy via Vercel UI ("Redeploy" on the latest production deployment). Do NOT proceed until confirmed. |
| P-2 | Backend Railway deploy ≥ `3ac1964` (cycle 19 LionWheel runtime closure) | `curl -s https://gt-factory-os-api-production.up.railway.app/health` → 200 `{ok:true}`. Then optionally inspect Railway service `gt-factory-os-api` deployments list — the deployed commit must be ≥ `3ac1964`. **Cycle 20 amendment:** if W1 cycle 20 ships and deploys mid-cycle (newer SHA), prefer the newer SHA — but `3ac1964` is the floor. | If `/health` returns 5xx: Railway may be cold-starting; wait 30s and retry. If still failing: report a backend outage; do NOT walk. |
| P-3 | Auth role: operator, planner, or admin | After signing in via `/login` magic-link, visit `/api/auth/whoami` (if exposed) or simply note that auth-gated pages render without 403 redirect. Viewer role is read-only and CANNOT submit a GR — step 7 will fail under viewer. | Use a non-viewer role; ask Tom for a planner/admin magic-link if necessary. |
| P-4 | At least one OPEN PO with ≥2 OPEN/PARTIAL lines exists in DB | Visit `/purchase-orders?status=OPEN` (or just `/purchase-orders` and filter). Pick a PO whose `Receipts` cell shows `0/N` ratio with `N ≥ 2`, OR a partial like `1/3` with at least one remaining OPEN/PARTIAL line. | If none exist: create a manual PO via `/purchase-orders/new` (planner/admin only) with ≥2 lines and submit. The new PO will land in OPEN status. |
| P-5 | (Optional, for step 11 terminal-guard regression) at least one RECEIVED or CANCELLED PO exists | Visit `/purchase-orders?status=RECEIVED` (or `?status=CANCELLED`). Note its uuid for step 11. | If none exist: complete a small PO end-to-end first (or skip step 11 — it is a regression sanity check, not a critical-path probe). |

---

### Step 1 — PO list shows Receipts summary column

| Field | Value |
|-------|-------|
| URL | `https://gt-factory-os-portal.vercel.app/purchase-orders` |
| Action | Open the page. Visually scan the table. |
| Element to identify | Column header reading `Receipts` between `Expected` and `Total net`. Each row's Receipts cell contains: a monospaced ratio (e.g. `0.00/100.00`) with `font-mono text-xs tabular-nums` styling; a 1-line caption `N line(s)`; a 1-pixel progress bar with `role="progressbar"` and `aria-valuenow/valuemin/valuemax`; a warning-toned `open` pill when `total_open_qty > 0`; a neutral em-dash placeholder where `lines_summary` is undefined. Source ref: `(po)/purchase-orders/page.tsx:201-266` (LinesSummaryCell). |
| DOM/network expectation | (a) HTTP 200 on the page's `GET /api/v1/queries/purchase-orders?...` proxy fetch (visible in Network tab). (b) Response payload includes `lines_summary` per row when the PO has ≥1 line. (c) No 401/403 redirect (means P-3 holds). |
| Failure modes | **Receipts column missing** = old portal deploy → re-check P-1. **All cells show em-dash** = backend `lines_summary` field stripped from response → check Network tab for the actual JSON shape. **401 redirect to /login** = P-3 fails → re-auth. |
| Recovery if fails | If column is missing entirely, hard-reload (Ctrl+Shift+R). If still missing, P-1 is wrong — ask Vercel to re-deploy. |

### Step 2 — Verify Receipts column shows ratio + line count + progress bar

| Field | Value |
|-------|-------|
| URL | Same as Step 1 |
| Action | On a row whose Receipts cell shows non-em-dash, hover over it. Tab to it via keyboard if accessibility check is desired. |
| Element to identify | Numeric ratio rendered with `font-mono`. Below: `N line(s)` text. Below that: progress bar with `role="progressbar"`. Optional warning pill `text-warning-fg tabular-nums` when `total_open_qty > 0`. |
| DOM/network expectation | No additional network calls on hover (data is rendered from the same payload). Hover does not trigger a tooltip in v1 (no title attribute on the cell wrapper per cycle 11 + 14 source). |
| Failure modes | Ratio shows but progress bar missing → CSS class regression. Ratio numbers off by an order of magnitude → backend `received_qty` / `ordered_qty` shape mismatch (check the JSON). |
| Recovery if fails | Capture the JSON response body and the rendered cell screenshot. File as a separate W2 cycle defect (cycle 11 + 14 already shipped this — regression would indicate a refactor side effect). |

### Step 3 — Click an OPEN PO with at least 2 lines

| Field | Value |
|-------|-------|
| URL | Same as Step 1 |
| Action | Click the row of the OPEN PO selected in P-4. The `<tr>` is wired as a Next `<Link>` to `/purchase-orders/<uuid>`. |
| Element to identify | The clickable row. After click, URL bar transitions to `https://gt-factory-os-portal.vercel.app/purchase-orders/<uuid>` (no query string). PO detail page loads. WorkflowHeader title reads the PO number (e.g. `PO-2026-00112`). Status badge shows `OPEN` or `PARTIAL`. |
| DOM/network expectation | (a) URL changes to `/purchase-orders/<uuid>`. (b) `GET /api/purchase-orders/<uuid>` proxy fetch fires. (c) Response 200 with header + lines + attached_grs payload. |
| Failure modes | **Click does nothing** = the row's Link wrapper missing → check Network tab for blocked navigation. **404** = stale uuid (PO was deleted) → pick another PO. **5xx** = backend defect → check Railway logs. |
| Recovery if fails | Hard-reload `/purchase-orders/<uuid>`. If still 404, the PO truly does not exist — pick another from the list. |

### Step 4 — Verify "Receive against this PO →" header CTA visible

| Field | Value |
|-------|-------|
| URL | `https://gt-factory-os-portal.vercel.app/purchase-orders/<uuid>` |
| Action | Look at the top-right WorkflowHeader.actions cluster (above the Lines section). Hover briefly to read the title-attribute disclosure. |
| Element to identify | Primary `btn-sm btn-primary` Link with `data-testid="po-receive-against-cta"`. Visible text: `Receive against this PO →`. `aria-label="Receive against PO <po_number>"`. `title` attribute reads about over-receipt semantics. Visibility iff `po.status IN ('OPEN','PARTIAL')`. Source ref: `(po)/purchase-orders/[po_id]/page.tsx:1325-1335`. |
| DOM/network expectation | Element is rendered with `display` non-`none`, `pointer-events` non-`none`. No tooltip JS — the title attribute is the OS-native hover. |
| Failure modes | **CTA missing on OPEN PO** = visibility guard regression → inspect HTML for the data-testid; if not in DOM, the conditional render is broken. **Wrong link href** (does not contain `/stock/receipts?po_id=`) = href construction regression. **Visible on RECEIVED/CANCELLED** = guard inverted. |
| Recovery if fails | Capture screenshot + HTML inspector view of the WorkflowHeader.actions region. File as W2 defect (cycle 16 closed this; regression would indicate a refactor side effect). |

### Step 5 — Click CTA. URL becomes `/stock/receipts?po_id=<uuid>`

| Field | Value |
|-------|-------|
| URL | Click `data-testid="po-receive-against-cta"` from Step 4. |
| Action | Single click. Wait for navigation. |
| Element to identify | Browser URL bar transitions to `https://gt-factory-os-portal.vercel.app/stock/receipts?po_id=<URL-encoded-uuid>`. The `(ops)/stock/receipts/page.tsx` route loads. |
| DOM/network expectation | (a) URL exactly matches the pattern (uuid encoded but readable). (b) `GET /api/purchase-orders/<uuid>` and `GET /api/v1/queries/purchase-orders?status=OPEN,PARTIAL` proxy calls fire (the form needs both the URL-PO header and the open-POs reference list). (c) `GET /api/v1/queries/items?...` and `/components?...` may also fire for receivable resolution. (d) HTTP 200 on all. |
| Failure modes | **404** = the receipts route is unreachable (very rare; cycle 16 verified). **401 redirect** = auth expired → re-sign-in. **No `?po_id=` query string** = href construction missing the encodeURIComponent → see Step 4 recovery. |
| Recovery if fails | Hard-reload. If still broken, manually visit `/stock/receipts?po_id=<uuid>` from the URL bar — the prefill effect should still fire if the route loads. |

### Step 6 — Verify supplier-locked caption + PO context strip

| Field | Value |
|-------|-------|
| URL | `https://gt-factory-os-portal.vercel.app/stock/receipts?po_id=<uuid>` |
| Action | Wait for the form to load (no skeleton spinner). Visually verify two elements: (a) the PO context strip above the form; (b) the supplier `<select>` is disabled. |
| Element to identify | (a) Strip with `data-testid="receipts-po-context-strip"` containing `Receiving against PO <po_number>` (the po_number in `font-mono`), supplier name, optional expected delivery date, and a `← Back to PO` Link with `data-testid="receipts-po-back-to-po"`. Source ref: `(ops)/stock/receipts/page.tsx:685-713`. (b) Supplier `<select>` element with `data-testid="receipt-supplier-select"` and `disabled` attribute true; below it a caption with `id="receipt-supplier-locked-caption"` reading `From PO <po_number> — supplier locked.`. Source ref: lines 836-859. (c) WorkflowHeader.eyebrow text reads `Receiving against PO <po_number>`. (d) WorkflowHeader.description reads `From <supplier_name>` followed optionally by ` · expected <date>.`. |
| DOM/network expectation | The strip's `border-info/30 bg-info-softer/30` info-tone styling is visually distinct from posted-stock indicators (per cycle 16 visual separation rule). The supplier select has the disabled cursor on hover. |
| Failure modes | **Strip missing** = `urlPoLocked && !urlPoTerminal && urlPoHeader` guard failed → check Network tab for the `GET /api/purchase-orders/<uuid>` response shape. **Strip rendered but caption missing** = caption render condition inverted. **Supplier select clickable** = `disabled={urlPoLocked}` regression. |
| Recovery if fails | Capture screenshot + Network tab. File as W2 defect. |

### Step 7 — Verify lines pre-loaded with `received_qty = open_qty`

| Field | Value |
|-------|-------|
| URL | Same as Step 6. |
| Action | Look at the `Lines` SectionCard. Count the pre-rendered LineDraft rows. Inspect each draft's quantity input value. |
| Element to identify | One LineDraft `<div>` per OPEN/PARTIAL PO line (CLOSED + CANCELLED filtered). Each draft contains: a `quantity` numeric input pre-filled with the line's `open_qty` value; a `unit` selector pre-set to the PO line's `uom`; a hidden / displayed `po_line_id` (visible via the linked-PO-line `<select>` showing the matching line metadata); a `receivable_key` resolved as `component:<id>` then `item:<id>` then empty. Source ref: `(ops)/stock/receipts/page.tsx:384-434` (prefill effect) + lines 416-422 (draft mapping). |
| DOM/network expectation | (a) Initial blank draft is replaced by the prefilled drafts after `poDetailQuery.isLoading` flips false. (b) `prefillApplied` becomes true and the effect does not re-run. (c) Each draft's quantity input shows the numeric value, not `0` or empty. |
| Failure modes | **Drafts blank or missing** = prefill effect did not fire → check `poDetailQuery.isLoading` Network tab + the `lines` array shape. **Quantity = 0** = `pl.open_qty` is 0 on every line (PO is fully received) → use a different PO. **Wrong UOM** = `(UOMS as readonly string[]).includes(pl.uom)` failed → fallback `"UNIT"` rendered, indicates non-canonical UOM on the PO line. |
| Recovery if fails | Hard-reload to retry prefill. If lines still blank, the PO has no OPEN/PARTIAL lines (P-4 failed) — pick another. |

### Step 8 — Edit one line's qty downward. Submit.

| Field | Value |
|-------|-------|
| URL | Same as Step 6. |
| Action | (a) Pick one LineDraft row. (b) Click into its `quantity` input. (c) Decrease the value by some amount > 0 (e.g. if `open_qty = 100`, type `60`). (d) Click the `Submit receipt` button. |
| Element to identify | Numeric `<input type="number">` (or text with numeric pattern) inside the chosen LineDraft. Submit button labeled `Submit receipt` at the bottom of the form, usually `data-testid="receipt-submit-btn"` or similar (verify in HTML inspector). After click, button text flips to `Submitting…` and `disabled` is true. |
| DOM/network expectation | (a) Network tab shows `POST /api/goods-receipts` (portal proxy) → upstream `POST /api/v1/mutations/goods-receipts`. (b) Request body includes top-level `po_id`, `supplier_id` (auto-prefilled), and `lines[]` with one entry per draft (each carrying `po_line_id`, `quantity`, `unit`, `notes`). (c) Response 200 with body `{submission_id, po_id, po_number?, lines: [{...}]}`. (d) Page transitions out of `phase: "submitting"` to `phase: "done"` (success branch) or stays on form with error panel (error branch). |
| Failure modes | **Submit button does not flip to Submitting…** = handler not wired → check console for JS error. **401** = auth expired. **403** = role insufficient (viewer cannot submit). **422** = Zod validation fail (likely `quantity = 0` or non-numeric). **409 ITEM_TYPE_MISMATCH / PO_LINE_PARENT_MISMATCH** = receivable_key resolution wrong. **5xx** = backend down. **Network error** = portal renders red `done.kind === "error"` panel with `Network error submitting receipt.`. |
| Recovery if fails | If submit fails, the form does NOT clear — correct fields and re-submit. If TanStack Query desynced, hard-reload `?po_id=<uuid>` to re-prefill cleanly. Capture screenshot + Network tab response body for any 4xx/5xx. |

### Step 9 — Verify success panel: posted ledger movement count + new PO status + 3 nav links

| Field | Value |
|-------|-------|
| URL | Same as Step 6 (page does not navigate; success panel replaces or sits alongside the form region). |
| Action | After Step 8 returns 200, scroll to the success panel (or note that it appears at the form's location). |
| Element to identify | (a) Outer panel with `data-testid="receipt-success-panel"`, green-toned (`border-success/40 bg-success-softer text-success-fg`). (b) Success message line + itemSummary line (count of posted lines) + detail line `ref: <submission_id> · N line(s)`. (c) 3-button nav cluster wrapped in `flex flex-wrap gap-2`: button 1 with `data-testid="receipt-success-back-to-po"` reading `Back to PO <po_number> →`; button 2 with `data-testid="receipt-success-view-attached-grs"` reading `View receipts on this PO →`; button 3 with `data-testid="receipt-success-view-movement-log"` reading `View movement log →`. Source ref: `(ops)/stock/receipts/page.tsx:715-781`. |
| DOM/network expectation | (a) Panel renders within ~500ms of the 200 response. (b) `done.poId = committed.po_id` and `done.poNumber = urlPoHeader?.po_number` are populated from the response. (c) Hovering button 3 shows the cycle 19 title attribute `View ledger movements scoped to this PO.`. (d) Submit button no longer says `Submitting…`. |
| Failure modes | **No panel** = response branched to error or `done.poId` missing → check Network tab for the actual response body. **Wrong title-attribute on movement-log** = browser cached a pre-cycle-19 build → hard reload or check Vercel deployment SHA. **Nav cluster shows but Back-to-PO link dead** = `done.poId` empty → backend response shape regression. |
| Recovery if fails | If panel does not render after a 200, capture the response body and file as DTO drift defect. If title attribute reads the cycle-16 honest-disclosure copy ("Filter by po_id is not yet supported…"), Vercel has not deployed cycle 19 yet — wait for auto-deploy (usually < 2 min). |

### Step 10 — Click "View movement log →". URL becomes `/stock/movement-log?po_id=<uuid>`. Verify filter chip (cycle 19), table filtered.

| Field | Value |
|-------|-------|
| URL | After Step 9, click `data-testid="receipt-success-view-movement-log"`. |
| Action | Single click. Wait for navigation + page load. |
| Element to identify | (a) URL bar shows `https://gt-factory-os-portal.vercel.app/stock/movement-log?po_id=<uuid>`. (b) **Cycle 19 filter chip** with `data-testid="movement-log-po-filter-chip"`: info-tone bordered strip at the top of the page, before the `Search Movements` filter card. Visible text: `Filtered by PO:` + the human-readable po_number (e.g. `PO-2026-00112`) in monospace, optionally followed by `· <supplier_name>` and `· <status>`. (c) On the right of the chip: `Back to PO →` link with `data-testid="movement-log-po-filter-back-link"` and `Clear filter` button with `data-testid="movement-log-po-filter-clear"`. (d) Below the chip, the ledger table shows ONLY movements whose `related_po_line_id` belongs to a PO line under that PO (typically GR_POSTED rows from the just-submitted receipt). |
| DOM/network expectation | (a) `GET /api/stock/ledger?po_id=<uuid>&limit=100&offset=0` fires; response scoped to PO. (b) `GET /api/purchase-orders/<uuid>` fires in parallel for the chip's po_number resolution. (c) Clicking `Clear filter` calls `router.replace("/stock/movement-log")`; chip disappears; table re-fetches unfiltered. |
| Failure modes | **Chip not rendered** = `?po_id=` not on URL (Step 9 link regression) → check `done.poId` extraction. **Chip shows raw uuid** = PO header lookup failed → graceful fallback expected. **Empty ledger after a successful Step 8** = backend GR write succeeded but ledger postings haven't propagated yet (timing) → empty-state copy says "No movements found for PO {x}…"; refresh in 2-3 seconds. **`Clear filter` doesn't drop the param** = `router.replace` failure (rare). |
| Recovery if fails | If chip is broken, the page still functions: per-field filters work independently. If empty state shows but rows expected, hard-reload after a few seconds; if still empty, the GR may have failed at the ledger-write step (W1 defect). |

### Step 11 — Click "Back to PO". Verify PO detail shows updated received_qty/line_status

| Field | Value |
|-------|-------|
| URL | After Step 9 / 10, click `data-testid="receipt-success-back-to-po"` from the success panel (or `data-testid="movement-log-po-filter-back-link"` if you went via the movement log route). |
| Action | Single click. Wait for navigation + page load. |
| Element to identify | (a) URL bar shows `https://gt-factory-os-portal.vercel.app/purchase-orders/<uuid>` (no query string). (b) PO detail page header eyebrow text reads canonical `PO <po_number>`. (c) Status badge near the top shows `PARTIAL` (if Step 8 was a partial-qty edit and ≥1 line still has `open_qty > 0`) or `RECEIVED` (if Step 8 fully closed every line on this PO). (d) Lines section table renders updated `received_qty` and `line_status` for the line edited in Step 8. (e) The header CTA at `data-testid="po-receive-against-cta"` either still renders (if status still OPEN/PARTIAL) or is replaced by `data-testid="po-view-receipts-link"` reading `View receipts →` if status now RECEIVED. |
| DOM/network expectation | (a) On navigation, `GET /api/purchase-orders/<uuid>` fires; response carries the rolled-up `received_qty` and `line_status` per line. (b) TanStack Query may serve a stale cache on first paint — if values look unchanged, force-refresh (Ctrl+Shift+R). (c) The header status badge enum matches the CTA visibility branches. |
| Failure modes | **Stale received_qty / line_status** = TanStack Query cache hit before backend rollup completed → hard reload. **Status badge reads `OPEN` after a full receipt** = `fn_post_goods_receipt` rollup did not fire (W1 backend defect). **CTA still says `Receive against this PO →` after a full receipt** = same root cause (PO status didn't flip). |
| Recovery if fails | If status flip is wrong, capture: (a) values in lines table; (b) status badge text; (c) hard-reload result. If hard-reload fixes → portal cache issue; if hard-reload still wrong → backend rollup defect (W1 cycle to file). |

### Step 12 — Mobile @ 390px sanity (key actions reachable)

| Field | Value |
|-------|-------|
| URL | Either Step 1 (`/purchase-orders`), Step 5 (`/stock/receipts?po_id=<uuid>`), or Step 11 (`/purchase-orders/<uuid>`). |
| Action | (a) Open browser DevTools. (b) Toggle device-emulation (Ctrl+Shift+M in Chrome). (c) Set viewport width to 390px (e.g. iPhone 12 Pro preset). (d) Reload the page. (e) Walk through the form / detail / list at 390px width; tap interactive elements. |
| Element to identify | (a) On `/purchase-orders`: the table reflows; rows remain readable; no horizontal scrollbar appears. (b) On `/stock/receipts?po_id=<uuid>`: PO context strip wraps via `flex flex-wrap` (still visible without horizontal scroll); form field grids collapse from `sm:grid-cols-2` → single column at < 640px; supplier + reference-PO selects stack vertically (each wrapped in `block min-w-0`); Submit button is reachable; success-panel nav cluster wraps to multiple lines via `flex flex-wrap gap-2`. (c) On `/purchase-orders/<uuid>`: WorkflowHeader.actions cluster wraps; CTA remains reachable; lines table has its own scroll container per cycle 14. |
| DOM/network expectation | No `overflow-x: scroll` on the body. No `min-w-[…]` larger than 390px on any container. Tap targets ≥ 44px hit area on the WorkflowHeader CTA + Submit + nav cluster buttons. |
| Failure modes | **Horizontal scrollbar appears on body** = a child container has fixed-pixel width exceeding 390px → inspect via DevTools CSS rules. **Submit button clipped or unreachable** = `<form>` ancestor has `overflow: hidden` and contains a too-wide grandchild. **Nav cluster does not wrap** = `flex` without `flex-wrap` → cycle 16 source guarantees `flex-wrap`; regression. |
| Recovery if fails | Capture screenshot at 390px showing the failing element. File as W2 mobile defect (cycle 12 + 16 already audited; regression would indicate a refactor side effect). |

---

### Cycle 20 verdict (this addendum)

| Step | Cycle 18 verdict | Cycle 19 status | Cycle 20 walkthrough plan ready |
|------|-----------------|-----------------|--------------------------------|
| 1 — PO list Receipts column | PASS (static) | unchanged | YES (URL + element + DOM/network + failure modes) |
| 2 — Ratio + line count + progress bar | PASS (static) | unchanged | YES |
| 3 — Click OPEN PO with ≥2 lines | PASS (static) | unchanged | YES |
| 4 — "Receive against this PO →" CTA | PASS (static) | unchanged | YES |
| 5 — CTA navigates to /stock/receipts?po_id=<uuid> | PASS (static) | unchanged | YES |
| 6 — Supplier-locked caption + PO context strip | PASS (static) | unchanged | YES |
| 7 — Lines pre-loaded with received_qty = open_qty | PASS (static) | unchanged | YES |
| **8 — Edit + submit** | **REQUIRES AUTH-SESSION** | **STILL REQUIRES AUTH-SESSION** | YES |
| **9 — Success panel + nav cluster** | **REQUIRES AUTH-SESSION** | **STILL REQUIRES AUTH-SESSION (cycle 19 title-attribute refresh)** | YES |
| **10 — Movement log filter chip + filtered table** | PASS (static link existence) | **CHANGED behavior under cycle 19** | YES (now exercises the chip + filtered table) |
| **11 — Back to PO + updated status** | **REQUIRES AUTH-SESSION** | **STILL REQUIRES AUTH-SESSION** | YES |
| 12 — Mobile @ 390px | PASS (static, CSS-class) | unchanged | YES |

**Cycle 20 verdict on this evidence pack: STATIC + MANUAL CHECKLIST READY — auth-session walk pending.** This is NOT a browser-verified verdict. Steps 8, 9, and 11 categorically require Tom auth-session (form submit, post-action panel render, status flip propagation). Steps 1-7, 10, and 12 can be Tom-walked statically (visual + DOM inspection only) but the cycle 20 plan still gives concrete URLs + element identifiers + DOM expectations + failure recovery so Tom captures real browser evidence rather than re-deriving from source. Tom (or any admin with a real Supabase JWT) executes the manual plan above to convert this to a fully browser-verified PASS.

### Authorization basis (cycle 20 addendum)

- EXECUTION_POLICY.md Mode B-Planning-Corridor 2026-05-02 amendment + cycle 20 dispatch carve-out (`inventory-overlay-conditional-and-gr-browser-support` tranche) enumerates `PRODUCTION/docs/qa/` as read-write under W2 ownership.
- This addendum is NOT canonical portal source; no validation gates apply.
- W1 cycle 20 inventory planned-inflow HTTP endpoint signal NOT EMITTED at end of W2 cycle 20 run — Branch A3 binds — overlay implementation skipped per dispatch hard rule. Effort redirected to this Tom Walkthrough Plan.
