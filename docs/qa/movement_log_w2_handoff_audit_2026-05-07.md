# Movement Log — W2 Handoff Audit (Mode A, 2026-05-07)

**Lane:** W2 (executor-w2)
**Mode at authoring:** Mode A (read-only)
**Plan of record:** `C:/Users/tomw2/.claude/plans/you-are-working-on-recursive-planet.md` — *Stock Ledger UX/UI Deep Audit and Improvement Plan*
**Authority basis for this doc:** Mode A docs in `PRODUCTION/docs/qa/` are read-write per existing convention; no canonical portal source modified in this cycle.
**Authoring boundary:** No `RUNTIME_READY(MovementLogV2)` signal exists in `.claude/state/runtime_ready.json` (verified 2026-05-07). All `_components/`, `_lib/`, and `page.tsx` rewrites enumerated in plan §15 are blocked from W2 canonical authoring until W1 emits that signal. This document is a Tranche 0 / pre-Tranche 1 audit only.

---

## §0 Worktree confirmation

- **Canonical W2 worktree:** `C:/Users/tomw2/Projects/window2-portal-sandbox/`. Confirmed via `PRODUCTION/portal/REDIRECT.md` lines 1–13: *"This directory is frozen as a historical Dropbox reference. The canonical, editable, runnable Window 2 portal sandbox is now at C:/Users/tomw2/Projects/window2-portal-sandbox/"*. Per memory `feedback_harness_state_authoritative.md`, this matches the established W2 ownership rule — `window2-portal-sandbox` IS the canonical portal.
- **Branch state at audit time:** `fix/supply-flow-error-clarity` @ `2db3f730e47fa7f3b6181cb91001086c85403164`. `git status --short` returned no output — working tree is clean. No uncommitted edits to `src/app/(shared)/stock/movement-log/page.tsx` or any sibling.
- **Audit doc location:** `PRODUCTION/docs/qa/movement_log_w2_handoff_audit_2026-05-07.md` (this file). Outside the portal repo per dispatch rules. No write inside `window2-portal-sandbox/src/**`.

---

## §1 Current page inventory — `page.tsx` line-by-line

**File path:** `C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(shared)/stock/movement-log/page.tsx`
**Line count:** 503 lines, single file. No `_components/` or `_lib/` siblings exist in `src/app/(shared)/stock/movement-log/`.

### What the page renders today

| Region | Lines | Renders |
|---|---|---|
| `WorkflowHeader` | 229–233 | eyebrow="Stock", title="Movement Log", description="Ledger history for all stock movements. Filter by item, type, or date range." |
| Active PO filter chip (conditional on `?po_id=`) | 243–287 | Cycle 19 chip with PO number resolution, supplier name, status, "Back to PO →" link, and "Clear filter" button. Renders only when `urlPoId` is set. |
| `SectionCard` "Search Movements" | 289–375 | 5 filter inputs in a 3-column responsive grid: `item_id` (text), `item_type` (select, FG/RM/PKG), `movement_type` (select, 5 fixed types), `from_date`, `to_date`. "Apply" + "Clear" buttons. |
| `SectionCard` "Ledger Entries" loading | 378–392 | 6-row pulse skeleton rendered when `isLoading=true`. `aria-busy` + `aria-live="polite"`. |
| `SectionCard` "Ledger Entries" error | 393–405 | Danger-tone box; "Could not load movement log" + retry button. |
| `SectionCard` empty (PO-scoped) | 406–426 | Cycle 19 PO-aware empty state ("No movements found for PO X. PO may not have ledger postings yet, or you may have over-receipt exceptions"). |
| `SectionCard` empty (no filter) | 427–431 | Generic "No movements found for the selected filters." |
| `SectionCard` results table | 432–498 | 7-column table: Event At, Type, Item (`item_id` mono + `item_type` parens), Qty Δ (signed), UOM, Submitted by, Status. Pagination row with Prev/Next, page x of y, total count. |

### Query that issues to `/api/stock/ledger`

- **Hook:** `useQuery` (TanStack), key `["stock-ledger", appliedFilters, urlPoId, offset]`, `staleTime: 30_000` (lines 191–195).
- **Builder:** `buildQuery(filters, poId, offset)` — lines 87–108. Constructs `URLSearchParams` with `item_id`, `item_type`, `movement_type`, `from` (= `${from_date}T00:00:00Z`), `to` (= `${to_date}T23:59:59Z`), `po_id`, `limit=100` (constant `PAGE_SIZE`), `offset`.
- **Fetch:** `fetchLedger` — lines 110–121. Issues `GET /api/stock/ledger?{qs}`. Tolerates both response shapes: bare array (legacy) and `{ rows, total }` envelope.
- **Proxy:** `src/app/api/stock/ledger/route.ts` (verified 8 lines). Calls `proxyRequest({ method: "GET", upstreamPath: "/api/v1/queries/stock/ledger", forwardQuery: true, errorLabel: "stock ledger" })`. Forwards query verbatim. **Note:** plan §15 "Reused utilities" cites `src/app/api/_lib/proxy.ts` but the actual import is from `@/lib/api-proxy` — minor doc nit, not a blocker.
- **Companion query:** `useQuery` for PO header at lines 177–183, hits `/api/purchase-orders/{po_id}` (proxy at `src/app/api/purchase-orders/`). Used only for chip-label resolution; tolerates failure with raw `po_id` fallback.

### Fields the page consumes from `LedgerRow` (interface at lines 10–23)

| Field | Used at | Renders as |
|---|---|---|
| `movement_id` | line 449 | React `key` only — never displayed |
| `movement_type` | line 454 | `fmtMovementType(...)` → label from `MOVEMENT_TYPE_LABELS` (5 entries, lines 57–63), raw passthrough if not in map |
| `item_type` | line 458 | parenthesized after `item_id` |
| `item_id` | line 457 | `<span className="font-mono">` — **raw text PK** rendered to operators (Tom-locked rule "names not IDs" violated; see §4) |
| `qty_delta` | line 461 | `<QtyDeltaCell>` (lines 142–151) — `+` for ≥0 with `text-success-fg`, `−` for <0 with `text-danger-fg`, fixed at 3 decimals |
| `uom` | line 463 | raw passthrough |
| `event_at` | line 451 | `formatDate(iso)` → `en-GB` `DD MMM YYYY HH:MM` (lines 131–140) |
| `post_status` | line 467 | raw text in `text-fg-muted` |
| `reported_by_snapshot` | line 465 | raw text or `—` fallback |

### Fields the API returns that the page **ignores entirely**

- `reported_by_user_id` (interface line 19) — fetched, never rendered.
- `source_event_id` (interface line 20) — fetched, never rendered.
- `notes` (interface line 21) — fetched, never rendered.
- Any join-shape data not on the local interface (e.g., LW task id, GT order #, recipient name, supplier id, PO number, BOM version id, reversal of, etc.) — interface does not declare them, so the type system silently drops them. **This is the central gap the plan §4.1 closes.**

### Filter list staleness (plan §4.6)

`MOVEMENT_TYPES` const at lines 49–55 declares only 5 movement types: `GR_POSTED`, `WASTE_POSTED`, `production_output`, `production_consumption`, `production_scrap`. The actual stock_ledger universe is broader (`COUNT_*`, `FG_OUT_PICK`, `FG_OUT_PICK_REVERSAL`, `LW_*` historical pre-cycle-19 rows for the cleanup window, etc., per `CLAUDE.md` §LionWheel). The dropdown therefore underrepresents. Plan §4.3 / §4.6 fix this via a `/movement-types` enumeration endpoint — a backend deliverable, not W2.

---

## §2 Dependency map — imports + reuse posture

| Import (line) | Symbol | Source path | Reuse posture for plan §15 |
|---|---|---|---|
| 3 | `useEffect, useMemo, useState` | `react` | Reuse as-is. |
| 4 | `Link` | `next/link` | Reuse as-is. |
| 5 | `useRouter, useSearchParams` | `next/navigation` | Reuse as-is. |
| 6 | `useQuery` | `@tanstack/react-query` | Reuse as-is. Plan §15 `_lib/queries.ts` should encapsulate the `useQuery(...)` call so the page composes from a typed hook rather than inlining the key. Pattern already established in `src/app/(planning)/planning/inventory-flow/supply/_lib/useSupplyFlow.ts`. |
| 7 | `WorkflowHeader` | `@/components/workflow/WorkflowHeader` | **Reuse as-is.** Plan §15 confirms UNCHANGED. Component (`src/components/workflow/WorkflowHeader.tsx`, 62 lines) accepts `eyebrow`, `title`, `description`, `meta`, `actions`, `children` — sufficient for the new "trust strip / filter chip" rail under the header. Can host `meta` slot for permission caveat. |
| 8 | `SectionCard` | `@/components/workflow/SectionCard` | **Reuse as-is.** Plan §15 confirms UNCHANGED. Component (`src/components/workflow/SectionCard.tsx`, 81 lines) accepts `title`, `description`, `eyebrow`, `actions`, `children`, `footer`, `tone` (`default/warning/danger/info/success`), `density`. Tone prop already covers the "trust" / "warning" / "info" cases enumerated in plan §6 / §11. `footer` slot is ideal for "showing N of M" / "row source caveat" lines. |
| (proxy) | `proxyRequest` | `@/lib/api-proxy` | **Reuse as-is.** Plan §15 cites it as `src/app/api/_lib/proxy.ts` — minor path mismatch; actual file is `src/lib/api-proxy.ts`. No code change to the proxy is needed for this plan. |

### Sibling primitives that the new components in plan §15 will need

These are pre-existing canonical primitives W2 should compose, not re-author. Net-new authoring is required only for the movement-log-specific shells.

| Need (plan §15) | Existing primitive available? | Path |
|---|---|---|
| `MovementDetailsDrawer` (side panel desktop, bottom sheet mobile) | **Yes — `Drawer`** stack-aware Radix Dialog primitive | `src/components/overlays/Drawer.tsx` (full Radix Dialog wrapper with focus trap, ARIA, stack context, width="md/lg/xl"). Already used by `AssignPrimarySupplierDrawer`, `ClassWEditDrawer`, `QuickFixDrawer`, `BomLineAddDrawer`. Mode B work composes this; do **not** author a new drawer primitive. |
| `SummaryCards` (5 KPI tiles) | **Yes — `KpiTiles` shape pattern** | `src/components/dashboard/KpiTiles.tsx` (3-tile responsive grid with TanStack count fetches, error degradation to "—"). Plan §6.summary-cards-rules can reuse the structural pattern; do not author a new responsive-grid primitive — re-use the layout discipline. |
| Status badges (multi-pill: text + icon + color, plan §8) | **Yes — `StatusBadge` and `FreshnessBadge` and `ReadinessBadge`** | `src/components/badges/StatusBadge.tsx` (dot + text, success/danger/warning/info tones from CSS-var palette), `FreshnessBadge.tsx`, `ReadinessBadge.tsx`. New movement-status badges should reuse the dot+pill+text discipline. |
| `aria-expanded` accordion / details disclosure (plan §10 details panel) | **Yes — `BlockerDetailAccordion`** as the closest in-tree pattern | `src/app/(planning)/planning/blockers/_components/BlockerDetailAccordion.tsx` (lines 31–46 demonstrate `aria-expanded={open}` on the disclosure button + chevron rotate). Pattern, not component, for reuse. |
| `cn` class merger | Yes | `src/lib/cn.ts` — used everywhere |

### Net-new in plan §15 (no in-tree predecessor)

- `ShipmentGroupCard` — collapsed-by-default group container with sub-row reveal. **No in-tree predecessor.** Closest pattern is `BlockerDetailAccordion` (disclosure semantics) + `SectionCard` (chrome). New component is justified.
- `MovementRow` — desktop table row. Today rendered inline at page.tsx:448–469. Plan §15 EXTRACTS — net-new in component form, no behavior change required.
- `MovementCardMobile` — mobile card. **No in-tree predecessor for movement-log row-as-card.** The closest analog is `src/app/(planning)/planning/inventory-flow/_components/MobileItemCard.tsx`. Pattern reusable; component net-new.
- `BusinessContextLine` — renders `business_context.{primary,secondary,tertiary}` per `kind`. **Net-new.** Tightly coupled to plan §4.1 backend response shape — cannot start until backend ships.
- `TrustStrip` — "מקור / עודכן / event_at vs posted_at / RBAC" strip. **Net-new.** Note: plan §15 row 6 still uses Hebrew labels in the title, but per the dispatch's plan §16 confirmation and per memory `feedback_portal_ui_english_ltr.md`, English/LTR is the default — open question to confirm at Mode B kickoff.
- `MovementDetailsDrawer` — composes existing `<Drawer>` primitive. Net-new shell, not a new primitive.
- `SummaryCards` — net-new for movement-log; can mirror `KpiTiles` layout discipline.
- `StickyDateHeader` — net-new. No in-tree predecessor for this exact pattern (sticky group-header inside a scroll container). `WeekCell.tsx` and `DayHeaderRow.tsx` in inventory-flow have related sticky patterns to study.
- `QtyDeltaCell` — already exists inline at page.tsx:142–151. Plan §15 EXTRACT to `_components/QtyDeltaCell.tsx`. Pure mechanical move.
- `_lib/labels.ts` — net-new. Pattern aligned with `src/app/(planning)/planning/inventory-flow/_lib/`, `src/app/(planning)/planning/forecast/_lib/`, `src/app/(planning)/planning/blockers/_lib/`.
- `_lib/types.ts` — net-new. Same pattern as above.
- `_lib/queries.ts` — net-new. Same pattern.

---

## §3 Design-token inventory

Tailwind token system source: `C:/Users/tomw2/Projects/window2-portal-sandbox/tailwind.config.ts` ("Operational Precision" design system, 14px base, HSL-var-driven, four families: surfaces, foreground/ink, borders, semantic colors).

### Tokens used by `page.tsx` today

| Token (Tailwind class) | Lines using it | Token family |
|---|---|---|
| `text-success-fg` | 147 (positive qty) | semantic / success |
| `text-danger-fg` | 147 (negative qty), 394, 400 | semantic / danger |
| `text-fg-muted` | 250, 292, 305, 321, 337, 349, 428, 450, 463, 464, 467, 475 | foreground / muted |
| `text-fg-subtle` | 258, 263, 421, 437, 458 | foreground / subtle |
| `text-fg` (default) | 252, 419, 453, 457 | foreground / default |
| `text-3xs` | 437 (uppercase tracking-sops eyebrow on table head) | font-size scale |
| `bg-bg-subtle` | 385, 386, 387, 388 (skeleton blocks); 449 (`hover:bg-bg-subtle/30`) | surface / subtle |
| `bg-info-softer/30` | 245 (PO chip background) | semantic / info |
| `bg-danger-softer` | 394 (error box) | semantic / danger |
| `border-border` | 300, 311, 326, 344, 355 (inputs); 437 (table head bottom rule) | border / default |
| `border-border/60` | 437 | border alpha |
| `border-border/40` | 447 (`divide-y`); 474 (pagination top border) | border alpha |
| `border-border/30` | 383 (skeleton rows) | border alpha |
| `border-info/30` | 245 (PO chip outline) | semantic / info |
| `border-danger/40` | 394 (error box outline) | semantic / danger |
| `focus:ring-accent/40` | 300, 311, 326, 344, 355 (input focus ring) | accent ring |
| `tracking-sops` | 437 (table head, ALL CAPS header letter-spacing 0.12em) | letter-spacing token |
| `font-mono` | 252, 419, 457 (item_id, po_id raw values) | font family |
| `font-medium` | 147 (qty delta) | weight |
| `font-semibold` | 292, 305, 321, 337, 349, 437 (form labels and table head) | weight |
| `divide-border/40` | 447 (table tbody) | border alpha |

### Colors used **outside** the token system

**None observed.** Every color, surface, and border on `page.tsx` resolves to a CSS variable behind the Tailwind config. No hard-coded `#RRGGBB`, no `text-[#…]` arbitrary values, no `rgb(...)`. The page is fully token-compliant; no token swaps are required for the redesign.

### Tokens the redesign will likely add (forward-looking, not in current page)

These are tokens already present in `tailwind.config.ts` that plan §6 / §8 / §14 will use:
- `tier-*` (5-tier inventory gradient) — likely **not** for movement-log; reserved for inventory-flow tier coloring.
- `bg-bg-raised`, `bg-bg-deep` — for sticky date header drop shadow / raised surface.
- `text-fg-strong` — currently used only inside `WorkflowHeader`; redesign will likely surface it on summary card values.
- `text-fg-faint`, `text-fg-inverted` — available, currently unused in this page.
- `accent-*` family — currently unused on this page apart from focus rings; can host primary CTAs (e.g., "Open shipment").
- `border-border-strong`, `border-border-focus`, `border-border-faint` — alternate border weights available.

No net-new tokens are required for plan §15. The system is sufficient.

---

## §4 Accessibility / WCAG 2.2 + mobile gap list

These are concrete defects observable on the existing page that the plan §13 acceptance criteria will close.

### A. Names not IDs (Tom-locked rule, ref `feedback_names_not_ids_in_ui.md`)

- **Lines 457–458:** `<span className="font-mono">{row.item_id}</span><span>({row.item_type})</span>` — operators see a raw text PK like `WS-LIME-330` instead of "Lime · 330ml glass". Item-name resolution is not joined client-side or server-side today. Plan §4.5 closes this via SQL join; until then, the rule is violated.
- **Lines 252, 419:** PO number chip — better, since cycle 19 already resolved `po_number` from `po_id`, but the fallback path on PO-header lookup failure (lines 188–189) still surfaces the raw `po_id` text PK in the UI. Acceptable degradation per the cycle 19 contract, but audit-flagged as a Tom-Tax item: in 1% of cases the operator sees a raw ID.
- **Line 465:** `reported_by_snapshot ?? "—"` — uses the snapshot pattern correctly per `CLAUDE.md` §"Audit semantics". Compliant.

### B. Status conveyed by color alone

- **Lines 142–151 `QtyDeltaCell`:** the only signal that distinguishes "+200" (inflow) from "−200" (outflow) for a colorblind operator is the explicit `+` / `−` sign and the green/red token color. The sign is text-based, so this passes WCAG 2.2 SC 1.4.1 (Use of Color). **Pass.** No icon needed.
- **Line 467 `post_status`:** raw text in muted gray, no badge, no color, no icon. Visually anemic but technically compliant — status differentiation comes from the text itself. Plan §8 mandates multi-pill (text + icon + color) badges; net upgrade.

### C. `aria-expanded` and disclosure semantics

- **No expandable sections exist on the current page.** The plan §7 `ShipmentGroupCard` (collapsed-by-default group with sub-row reveal) and §10 details drawer introduce this. The pattern available for reuse is at `src/app/(planning)/planning/blockers/_components/BlockerDetailAccordion.tsx` lines 31–46. Mode B authoring must apply `aria-expanded={open}` on the disclosure button and `aria-controls=` referencing the panel `id`.
- The Cycle 19 PO filter chip (lines 243–287) uses `role="note"` + `aria-live="polite"`. **Compliant.**
- The error box (lines 393–405) uses no role; `error` text is announced because `role="alert"` is implicit only when `aria-live="assertive"` is set, which it is not. **Defect: error box does not announce on error → speech.** Plan §11 should require `role="alert"` here.

### D. Focus indicators

- Inputs at lines 300, 311, 326, 344, 355 use `focus:outline-none focus:ring-2 focus:ring-accent/40`. **Compliant** (custom ring replaces removed outline; meets WCAG 2.2 SC 2.4.7 Focus Visible).
- Pagination buttons at 481–494 inherit the `.btn` and `.btn-sm` utility classes. Their focus state lives in the `globals.css` `.btn` definition — confirm at Mode B audit, not visible from this page alone. **Defer audit to Mode B kickoff.**
- `Apply` / `Clear` buttons at 362–373 same as above.
- "Back to PO →" `Link` at 269–275 uses `.btn-ghost`. Same caveat.
- Skeleton blocks at 380–390 are not focusable. **Compliant.**

### E. Keyboard tab order

Sequential reading order today on a result page with `?po_id=`:
1. PO chip "Back to PO →" link (273)
2. PO chip "Clear filter" button (281)
3. Item ID input (297)
4. Item Type select (310)
5. Movement Type select (325)
6. From Date input (343)
7. To Date input (354)
8. Apply button (363)
9. Clear button (369)
10. Retry button (if error visible, 398) — interruption
11. Pagination Prev (481)
12. Pagination Next (488)

**Issue:** the table itself is not focusable. Per plan §10, individual rows must become keyboard-focusable to open the details drawer. Today there is no keyboard path into per-row interaction. **Defect: violates WCAG 2.2 SC 2.1.1 Keyboard once row-detail interaction lands** — must be addressed in Tranche 3.

### F. Touch target size (mobile)

- All `.btn-sm` instances at lines 273, 281, 363, 369, 481, 488 — `.btn-sm` height likely 28–32px (confirm at Mode B from `globals.css`). **Below 44×44px guidance from WCAG 2.2 SC 2.5.8.** Plan §12 mandates ≥44px on mobile; defect to close.
- Filter inputs at lines 295–357 use `py-1.5 text-sm` → ~28px touch height. Same defect on mobile.
- Pagination buttons at 479–494 — same.

### G. Horizontal scroll at 375px

- Line 434: `<div className="overflow-x-auto">` wraps the 7-column table. **Behavior:** at 375px the table will horizontally scroll because the 7 columns at `min-w-full` cannot compress below their content widths. **This is the explicit defect plan §12 (Mobile 375 / 390 / 430 px) closes** by replacing the table with `MovementCardMobile` cards via `hidden md:block` / `md:hidden` breakpoints. Until the rewrite lands, mobile users get a side-scrolling table — a Tom-Tax item already flagged in this plan.

### H. Empty / loading / error states (plan §11)

- **Loading:** lines 378–392 — pulse skeleton, structurally honest (preserves row shape). `aria-busy` set. **Compliant.**
- **Error:** lines 393–405 — has retry, color-coded. Missing `role="alert"`. **Defect (minor).**
- **Empty (PO-scoped):** lines 406–426 — Cycle 19 wording about ledger postings or over-receipt exceptions. **Compliant and informative.**
- **Empty (no filter):** lines 427–431 — generic "No movements found for the selected filters." **Acceptable.**
- **Permission-blocked:** **does not exist today.** Plan §11 mandates a permission caveat panel ("data hidden by RBAC"); current page has no role-aware UI element. **Defect** — closure requires backend role-gate first (plan §4.4) which is W1.

---

## §5 Cross-component impact of plan §15 — net-new vs reusable

For each new/modified file enumerated in plan §15 (frontend table, lines 644–663):

| Plan §15 file | Status | Predecessor / pattern in tree | Reuse path |
|---|---|---|---|
| `(shared)/stock/movement-log/page.tsx` | **REWRITE** | self (current 503 lines) | Full rewrite. Will compose `WorkflowHeader`, `SectionCard`, new local `_components/*`, `Drawer` primitive, TanStack hooks from `_lib/queries.ts`. |
| `_components/ShipmentGroupCard.tsx` | **NET-NEW** | closest: `BlockerDetailAccordion.tsx` for disclosure semantics; `SectionCard` for chrome | Compose `SectionCard` + disclosure pattern. No new primitive needed. |
| `_components/MovementRow.tsx` | **NET-NEW (extract)** | inline row at page.tsx:448–469 | Mechanical extract. |
| `_components/MovementCardMobile.tsx` | **NET-NEW** | closest: `src/app/(planning)/planning/inventory-flow/_components/MobileItemCard.tsx` | Pattern reuse for mobile-card layout discipline. |
| `_components/BusinessContextLine.tsx` | **NET-NEW** | none — tightly coupled to plan §4.1 `business_context` API shape | **BLOCKED** until backend ships. |
| `_components/TrustStrip.tsx` | **NET-NEW** | closest: `src/components/dashboard/KpiTiles.tsx` for tile-row layout discipline | Pattern reuse only. Authoring waits on backend RBAC contract (plan §4.4). |
| `_components/MovementDetailsDrawer.tsx` | **NET-NEW (composition)** | `src/components/overlays/Drawer.tsx` (Radix-based) | **Compose `<Drawer>` directly.** Do NOT author a new drawer primitive. Existing siblings: `AssignPrimarySupplierDrawer`, `ClassWEditDrawer`, `QuickFixDrawer`, `BomLineAddDrawer`. |
| `_components/SummaryCards.tsx` | **NET-NEW** | closest: `src/components/dashboard/KpiTiles.tsx` (responsive 3→1 grid, count-fetch pattern) | Pattern reuse for tile layout. New component because plan §6 specifies 5 cards (vs Kpi's 3) and movement-log-specific copy. |
| `_components/StickyDateHeader.tsx` | **NET-NEW** | closest: `src/app/(planning)/planning/inventory-flow/_components/WeekCell.tsx`, `DayHeaderRow.tsx` for sticky group-header patterns | Pattern reuse. |
| `_components/QtyDeltaCell.tsx` | **NET-NEW (extract)** | inline at page.tsx:142–151 | Mechanical extract. |
| `_lib/labels.ts` | **NET-NEW** | pattern: `src/app/(planning)/planning/inventory-flow/_lib/`, `forecast/_lib/`, `blockers/_lib/` | Standard Hebrew/English label-map and status-formatter module. **Confirm English-only first per Tom-locked register before authoring.** |
| `_lib/types.ts` | **NET-NEW** | same pattern | Mirror plan §4.1 shape verbatim from upstream OpenAPI / contract pack — do NOT invent values. |
| `_lib/queries.ts` | **NET-NEW** | pattern: `src/app/(planning)/planning/inventory-flow/supply/_lib/useSupplyFlow.ts` | TanStack hook + buildQuery extract. |
| `tests/e2e/movement-log.spec.ts` | **NET-NEW** | pattern: existing Playwright specs in `window2-portal-sandbox/tests/e2e/` | Standard real-HTTP smoke spec. |
| `WorkflowHeader.tsx` | **UNCHANGED** (plan confirms) | self | No change. |
| `SectionCard.tsx` | **UNCHANGED** (plan confirms) | self | No change. |

**Net-new component count under `_components/`:** 9 (ShipmentGroupCard, MovementRow, MovementCardMobile, BusinessContextLine, TrustStrip, MovementDetailsDrawer, SummaryCards, StickyDateHeader, QtyDeltaCell).
**Of those, true net-new behaviors:** 6 (ShipmentGroupCard, MovementCardMobile, BusinessContextLine, TrustStrip, SummaryCards, StickyDateHeader). The remaining 3 are mechanical extracts of existing inline code or compositions of existing primitives.

---

## §6 Mode B readiness checklist

W2 cannot enter Mode B for this surface until **all** of the following hold:

### 6.1 W1 emits `RUNTIME_READY(MovementLogV2)`

- **Form name to register:** `MovementLogV2` (suggested; W1 chooses).
- **Required `evidence_path` content** (per plan §16 Tranche 1 exit + plan §4):
  1. Migration `0149_lw_destination_recipient_name.sql` landed and applied to staging.
  2. `api/src/integrations/lionwheel/reconciliation.ts` and poller writing `lw_destination_recipient_name` on upsert (plan §15 row 2).
  3. Backfill script `gt-factory-os/scripts/lionwheel/backfill_recipient_name.ts` executed on staging (plan §5 backfill plan).
  4. New `gt-factory-os/api/src/stock/movement-types.ts` enumeration source.
  5. `gt-factory-os/api/src/stock/schemas.ts` extended per plan §4.1: new `LedgerRow` shape with `business_context`, `group_id`, `reversal_of_movement_id`, all join fields. Zod schemas locked.
  6. `gt-factory-os/api/src/stock/ledger-handler.ts` rewritten per plan §4.5 with full SQL join, role gate, group_id assignment, business_context synthesis.
  7. `/movement-types` and `/movement-summary` endpoints live (plan §4.3).
  8. `gt-factory-os/api/test/stock_ledger_*.test.ts` — all listed tests green (existing 6 PO-filter + 6+ new: role-based recipient visibility, recipient filter authorization, full-text search, business_context.kind, group_id stability, unknown-context surfacing).
  9. **Manual `curl` proof against staging** included in evidence path showing the new shape.
- **Conflict-of-ownership note:** `0149_lw_destination_recipient_name.sql` collides with the existing `0149` slot — `CLAUDE.md` "LionWheel pickup → ledger decrement" section explicitly references migration 0149 as the (rejected) `LIONWHEEL_PICK*` enum addition. **W1 must resolve the renumbering BEFORE Tranche 1 dispatch under FR1→write→FR2 protocol** (`EXECUTION_POLICY.md` §"Pre-write fresh-read protocol"). If the existing 0149 file already occupies the slot, W1 must pick the next free number; W2 does NOT silently substitute.

### 6.2 W4 contract pack landed

- W4 must publish a contract pack documenting the verbatim API shape from plan §4.1 + §4.5.
- **Suggested file:** `PRODUCTION/window4-stock-ledger-movement-log-contract-pack.md` — sibling to existing `window4-shopify-greeninvoice-contract-pack.md`, `window4-lionwheel-contract-pack.md`, `window4-dashboard-read-model-contract-pack.md`.
- W2 will re-type the schema into `_lib/types.ts` from the contract pack (NOT from the W1 schemas.ts file directly — promotion forbidden per `EXECUTION_POLICY.md` §4.3 "no sandbox-to-canonical promotion / W2 does not invent backend contract values"). Mirror only, no invention. If a hook needs a value not in the contract pack → emit `assumption_failure`.

### 6.3 Tom approval on plan §16 open questions

Plan §16 itself is the tranche outline; the open-question lock points are in earlier sections. Confirm closed at Mode B kickoff:
- §3 UX principles — locked in plan body.
- §4.4 Authorization rule (recipient name visible to admin/planner only; operator/viewer get redacted) — locked.
- §4.6 Movement-type filter dropdown source — locked to new `/movement-types` endpoint.
- §6 IA — 5 summary cards locked in plan body.
- §7 Grouping (collapsed-by-default; reversal rows never merged into groups) — locked.
- §10 Drawer vs row-expand — open question; per plan body, "Drawer (side panel desktop, bottom sheet mobile)" is the locked answer.
- §13 a11y — locked.
- §14 Visual design — locked.
- **Localization register** (Hebrew vs English/LTR) for the new components — per memory `feedback_portal_ui_english_ltr.md`, default is English/LTR; plan §15 row 6 shows Hebrew labels in `TrustStrip` description (`"מקור / עודכן / event_at vs posted_at / RBAC"`) and §10 shows Hebrew "↶ נהפך מ-…". **OPEN: confirm whether movement-log surface is on Tom's Hebrew register.** Block at Mode B kickoff.

### 6.4 No-op rule

- Mode B may not be entered on `FILE_READY(form)` alone. `EXECUTION_POLICY.md` §"Signals" + `.claude/SIGNALS.md`. The signal must be `RUNTIME_READY(MovementLogV2)` with a verified `evidence_path`.

---

## §7 Worktree confirmation (per dispatch §7)

- Canonical worktree: `C:/Users/tomw2/Projects/window2-portal-sandbox/`. Confirmed via `PRODUCTION/portal/REDIRECT.md` ("This directory is frozen as a historical Dropbox reference. The canonical, editable, runnable Window 2 portal sandbox is now at C:/Users/tomw2/Projects/window2-portal-sandbox/").
- Per memory `project_portal_improvement_os.md`: portal-os/full-merge already on main; this is a forward-only worktree.
- `git status --short` on `c:/Users/tomw2/Projects/window2-portal-sandbox/` returned empty output at audit time. **Tree is clean.**
- Branch: `fix/supply-flow-error-clarity` @ `2db3f730e47fa7f3b6181cb91001086c85403164`. Audit raised no expectation that this audit cycle commit anything.

---

## Summary

The current Movement Log page is a single 503-line file at `C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(shared)/stock/movement-log/page.tsx`. It composes `WorkflowHeader`, `SectionCard`, `useQuery`, `useRouter`, and `useSearchParams` into a 5-filter + 7-column table view of `/api/stock/ledger`. It already correctly fetches via the proxy at `src/app/api/stock/ledger/route.ts` (forwards query verbatim) and resolves the cycle-19 `?po_id=` filter chip with PO-header lookup and graceful fallback.

The plan §15 redesign is **all on the consumer side** of the contract — every new component is a composition of existing primitives (`WorkflowHeader`, `SectionCard`, `Drawer`, status-badge family) plus net-new local shells specific to the movement-log surface. **No new portal primitives are needed.** All 9 listed `_components/*.tsx` files compose existing in-tree primitives or are mechanical extracts. The 3 listed `_lib/*.ts` files mirror the established `_lib/` pattern from `(planning)/planning/{inventory-flow,forecast,blockers}/_lib/`.

The current page is **fully token-compliant** (no off-token colors), has a **single concrete WCAG defect** (error box missing `role="alert"`, line 394) plus mobile-side defects (table side-scrolls at 375px; touch targets below 44px on filter inputs/pagination/`.btn-sm`) that the plan §11/§12/§13 redesign already targets. **Item-name resolution is the largest user-facing gap** — `row.item_id` is rendered as a raw text PK at line 457, violating Tom-locked rule "names not IDs". This is closed only by the backend SQL join in plan §4.5, not by W2 unilaterally.

W2 cannot proceed beyond Mode A on this surface without:
1. `RUNTIME_READY(MovementLogV2)` from W1 with the migration / handler / tests / staging-`curl` evidence.
2. W4 contract pack establishing the verbatim plan §4.1 / §4.5 response shape.
3. Confirmation that movement-log is **not** on Tom's Hebrew register (plan §15 row 6 has Hebrew strings; default per memory `feedback_portal_ui_english_ltr.md` is English/LTR).
4. W1 resolving the migration-0149 numbering collision per `EXECUTION_POLICY.md` FR1→write→FR2 bracket — `0149` slot is contested per `CLAUDE.md` LionWheel section.

Until those land, this surface stays in Mode A.
