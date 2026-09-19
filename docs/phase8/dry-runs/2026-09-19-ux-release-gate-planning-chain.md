# UX release gate — planning → production → procurement → receipt chain (2026-09-19)

> **Invocation:** manual `/ux-release-gate --scope <chain>` inside the planning-chain deep review (`docs/audits/2026-09-19-planning-chain-deep-review.md`).
> **Mode:** render-grade. Dev-shim auth (`NEXT_PUBLIC_ENABLE_DEV_SHIM_AUTH=true`), browser-stubbed APIs via `tests/e2e/ux-shot.spec.ts` + JSON fixtures transcribed from the committed `@mocked` specs. No `X-Fake-Session` / `X-Test-Session`. No portal source touched.
> **Write policy:** read-only gate. Saved here (default). After Tom approval → `gt-factory-os-portal/docs/ux/`.

## Scope

| Route | Role | Fixture | Desktop shot | Mobile shot |
|---|---|---|---|---|
| `/production` | operator | `production-today.json` (TANK planned · PACK planned · PACK done) | `/tmp/ux-shots/production-operator-desktop.png` | `…/production-operator-mobile.png` |
| `/production` (empty API) | operator | — | `…/production-empty-1-operator-desktop.png` | `…/production-empty-1-operator-mobile.png` |
| `/production/runs/RUN1` | operator | `production-run.json` (pick list, PLANNED) | `…/production-runs-RUN1-operator-desktop.png` | `…/production-runs-RUN1-operator-mobile.png` |
| `/production/runs/RUN1/report` | operator | `production-report.json` (IN_PRODUCTION, PACK) | `…/production-runs-RUN1-report-operator-desktop.png` | `…/production-runs-RUN1-report-operator-mobile.png` |
| `/stock/production-actual` (legacy) | operator | empty | `…/stock-production-actual-operator-desktop.png` | `…/stock-production-actual-operator-mobile.png` |
| `/stock/receipts` | operator | `receipts.json` (1 open PO expected today) | `…/stock-receipts-operator-desktop.png` | `…/stock-receipts-operator-mobile.png` |
| `/home` (Today board) | operator | `home.json` | `…/home-operator-desktop.png` | `…/home-operator-mobile.png` |
| `/planning/forecast` | planner | empty | `…/planning-forecast-planner-desktop.png` | `…/planning-forecast-planner-mobile.png` |
| `/planning/meeting` | planner | `meeting.json` | `…/planning-meeting-planner-desktop.png` | `…/planning-meeting-planner-mobile.png` |
| `/planning/production-plan` | planner | `production-plan.json` | `…/planning-production-plan-planner-desktop.png` | `…/planning-production-plan-planner-mobile.png` |
| `/planning/procurement` | planner | `procurement.json` (session, 3 POs) | `…/planning-procurement-planner-desktop.png` | `…/planning-procurement-planner-mobile.png` |
| `/purchase-orders/placement-queue` | planner | `placement-queue.json` | `…/purchase-orders-placement-queue-planner-desktop.png` | `…/purchase-orders-placement-queue-planner-mobile.png` |

Empty-API variants were also rendered for `/production/runs/RUN1`, `/production/runs/RUN1/report`, `/stock/receipts`, `/planning/procurement` (`*-empty-1-*`). Fixtures live in `/tmp/ux-fixtures/` (session-scoped; regenerate from the specs named in each file's header).

**Audit lens (from the deep review):** production has not been reported since 2026-09-07 (15 finished goods negative, Shopify shows them sold out); the last purchase session was 2026-08-23; September receipts are mostly PO-less. The gate therefore weighs the operator end-of-day report path and the door receipt path above everything else.

## Method and severity notes

Five read-only UX agents ran in parallel on the same screenshot set: `ux-flow-architect`, `interaction-design-specialist`, `visual-system-designer`, `ux-content-state-designer`, `accessibility-usability-auditor`. Their per-dimension tables are reproduced beneath the ranked list. Two cross-dimension duplicates were merged, and one severity was changed after verification by the gate author:

- **VISUAL-001 / INTER-001 → merged, P1.** The crash on the `*-empty-1-*` render (`runStatusMeta(data.status)` with `status` undefined, `src/app/(production)/production/_lib/runs.ts:126`) only occurs when the pick-list API answers **200 with an empty body**. The real API is Zod-typed and answers 404/500 on a bad run, which `PickList.tsx:70` turns into the plain-English error state. Not reachable in production; still worth a fallback, and the error boundary must never show raw JavaScript text to an operator.
- **INTER-002 / A11Y-002 → merged, P0.** Same root (every primary control in the `/production` corridor is 48–56 px; two are 28 px) against the Tom-locked ≥60 px rule for production order cycle v2 (`LOCKED_DECISIONS.md` §Production order cycle v2).
- **INTER-006 → answered by the backend audit.** The run report does not auto-close a base-batch plan (`report-handler.ts:276-278, 294-309`); `close-batch` is planner/admin only (`handler.close_batch.ts:63`). This is finding F5 / action A5 of the deep review, not a portal-only fix.

## Top-N ranked actions (one list, all dimensions)

| # | Sev | Effort | Dimension | Route | Finding | Proposed fix | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | P0 | S | Flow | `/home` (Today board, Yesterday tab) | "Needs a report" renders as a danger `<span>` with no link — the exact state behind the September reporting blackout is visible but not actionable | Make it `<Link href={`/production?date=${yesterdayIso}`}>` (date already in the panel's query) | `src/app/(shared)/home/_components/TodayBoard.tsx:164` |
| 2 | P0 | S | Flow | `/home` (Today board, Today tab) | Planned rows are plain `<li>`; the operator cannot start a run from the board | Wrap each row in `<Link href="/production">` | `TodayBoard.tsx:239-259` |
| 3 | P0 | S | Copy | `/stock/production-actual` (legacy) | Raw enum `PRODUCTION_CONSUMPTION_REVERSAL` in an operator-visible section description | "Stock quantities returned from reversed run." — or retire the surface (row 20) | `src/app/(ops)/stock/production-actual/page.tsx:1483` |
| 4 | P0 | M | Interaction + A11y | `/production`, `/production/runs/[id]`, `…/report` | Every primary control 48–56 px; "Extra job" ×2 = 28 px; PickRow edit ≈ 40 px — below the locked ≥60 px floor (two below WCAG 44 px) | One `btn-touch` variant (`min-height: 3.75rem`) applied across RunList, RunCard, PickRow, DoneBar, ReportForm, UnplannedRunDialog | `RunList.tsx:95,247`; `ReportForm.tsx:482,553,606`; `globals.css:533`; shot `production-runs-RUN1-report-operator-mobile.png` |
| 5 | P1 | S | A11y | `/stock/receipts` | "Confirm & receive all" and "Review lines instead" are `btn-sm` = 28 px — the most time-saving control on the door surface is the smallest | `btn-lg` (48 px), stacked full-width on mobile | `src/app/(ops)/stock/receipts/page.tsx:1824,1838` |
| 6 | P1 | S | Flow | `…/report` | Report `onSuccess` invalidates run queries but not `["today-board"]` — the danger badge on `/home` survives a successful report until reload | Add `invalidateQueries({ queryKey: ["today-board"] })` | `ReportForm.tsx` onSuccess; `TodayBoard.tsx:428-429` |
| 7 | P1 | S | Flow | `/purchase-orders/placement-queue` | Success banner links to `/stock/receipts` without `?po_id=` — Dorin re-selects the PO she just placed | `/stock/receipts?po_id=${placed.po_id}` | `placement-queue/page.tsx:307` |
| 8 | P1 | S | Flow | `/stock/receipts` (success) | Only a PO-detail link; no way back to the queue | Add "Back to orders queue" → `/purchase-orders/placement-queue` | `receipts/page.tsx:1019-1037` |
| 9 | P1 | S | Flow | `/production/runs/[id]` (TANK) | Success copy "Report the filling jobs for it." is plain text — no path to the fill runs | Link to `/production` | `PickList.tsx:244-248`; `copy.ts` `pick_tank_no_report` |
| 10 | P1 | S | Visual + Interaction | `/production/runs/[id]`, `…/report` | Unguarded status map + error boundary that prints the JS exception in a `<code>` block | `STATUS_META[status] ?? STATUS_META.PLANNED`; error boundary renders plain English + retry only | `runs.ts:126`; shot `production-runs-RUN1-empty-1-operator-mobile.png` |
| 11 | P1 | S | Interaction | `…/report` | Idempotency key regenerated inside `mutationFn` on every retry | `useRef(newKey())` outside the mutation; reset only on re-opening the confirm step | `ReportForm.tsx:50-55,172` |
| 12 | P1 | S | Interaction | `…/report` | QC toggle `btn-xs` = 24 px | `h-10` minimum | `ReportForm.tsx:603-610` |
| 13 | P1 | S | Visual | `/home` (operator) | Developer backlog text "no portal read model (gap G3)" shown to the operator | Plain "Route tracking not available yet." or suppress for operator role | `TodayBoard.tsx:302-305`; shot `home-operator-mobile.png` |
| 14 | P1 | S | Visual | `/home` vs `…/report` | "in production" is grey on the board and amber on the run form — one concept, two signals | One "executing" tone in the status-chip table; apply to both | `TodayBoard.tsx:253`; `runs.ts:121` |
| 15 | P1 | S | Interaction | `/planning/production-plan` | Cancel and Delete are adjacent, same size, both `text-danger` | Cancel → muted; Delete stays danger or moves behind overflow | `ProductionJobCard.tsx:476-509` |
| 16 | P1 | S | Visual | `/stock/receipts`, `/planning/procurement`, `/stock/physical-count` | `min-h-[44px]` / `min-h-[64px]` as raw brackets in 5+ files | `.min-h-touch` utility in `globals.css` (token change → Tom) | `ReceiptLandingPicker.tsx:185,346`; `POLineMatchCard.tsx:360,398`; `ProcurementWorkQueue.tsx:222`; `CalendarView.tsx:255` |
| 17 | P1 | M | A11y | `/stock/receipts` | Supplier combobox has no `aria-activedescendant` and options have no `id` | Stable option ids + `aria-activedescendant` on the input | `receipts/page.tsx:404-462` |
| 18 | P1 | M | Flow | `/planning/forecast` | No UI to revise / roll forward a published version although `/api/forecasts/open-draft` is deployed | "Start new draft from this version" on each published row | `forecast/page.tsx`; `src/app/api/forecasts/open-draft/route.ts` |
| 19 | P1 | S (backend) | Interaction | `/production` | "Close batch" unreachable from the operator corridor; backend does not auto-close | Auto-complete the base-batch plan when every manifest member is reported (deep review A5) | `report-handler.ts:276-278,294-309`; `handler.close_batch.ts:63` |
| 20 | P1 | L | Visual + Copy | `/stock/production-actual` (legacy) | Second production-report surface with a divergent template and 12 jargon strings ("pinned BOM", "stock ledger", "break-glass", raw UUIDs, "SKU", supply-method enums) | Retire: redirect to the `/production` corridor (deep review B1 / delete list). If it must stay, apply COPY-001…013 | `production-actual/page.tsx:506,536,544,1142,1218,1400,1408,1484`; shot `stock-production-actual-operator-mobile.png` |
| 21 | P1 | M | Visual | `/planning/inventory-flow` | `text-[9px]`/`[10px]`/`[12px]`/`[13px]` brackets bypass the type scale | Map to `text-3xs/xs/sm`; `text-[9px]` → `text-3xs` or a new `4xs` token (Tom) | `DayCell.tsx:228,238`; `StickyItemPanel.tsx:135,140,183,220`; `DayHeaderRow.tsx:192,198,211`; `MobileItemCard.tsx:417,429,509` |
| 22 | P1 | S | Copy | `/stock/receipts` | Eyebrow "Operator form"; raw `submission_id` in the success detail; PO badge "OPEN" verbatim | "Stock Receipt"; "Receipt saved. Check stock balances."; "Open" | `receipts/page.tsx:1277,1003,1484`; shot `stock-receipts-operator-desktop.png` |
| 23 | P2 | S | Flow | `/purchase-orders/placement-queue` | Placement does not invalidate `["ops","receipts","open-pos"]` | Add to the invalidation list | `placement-queue/_lib/api.ts:334-342` |
| 24 | P2 | S | A11y | global | `page-enter` and `.sparkline-path` animations ignore `prefers-reduced-motion` | Extend the existing reduced-motion block | `globals.css:423-425,697-703` |
| 25 | P2 | S | A11y | `/stock/receipts` | StepIndicator on mobile is colour-only, no `aria-current="step"` | `aria-current` + `sr-only` step names | `receipts/page.tsx:468-513` |
| 26 | P2 | S | A11y | `/planning/procurement`, `/purchase-orders/placement-queue` | Hebrew strings without `lang="he"` on the innermost element | `<span lang="he">` | `FocusCard.tsx:56-60`; `placement-queue/page.tsx:59-63` |
| 27 | P2 | S | A11y | `…/report`, `/production/runs/[id]` | QC toggle drops `aria-controls` when collapsed; PickRow focus ring at 50 % alpha | Stable `aria-controls` + explicit `aria-expanded`; `ring-accent` full opacity | `ReportForm.tsx:607-610`; `PickRow.tsx:180` |
| 28 | P2 | S | Copy | `/planning/production-plan`, `/planning/meeting`, `/production/runs/[id]` | "planned"/"completed" lowercase; "Blocked — missing BOM"; empty state without CTA; "Save what you took?" | Title Case; "recipe"; §3 template; "Save your picks for {product}?" | `production-plan/page.tsx:142-145,2359,2368`; `meeting/page.tsx:464`; `DoneBar.tsx:175` |
| 29 | P2 | L | Visual + A11y | global (light theme) | `--fg-subtle` ≈ 3.09:1 on eyebrows, `<th>`, chip text | Token change `30 5% 54%` → `~47%`, verify both themes (Tom) | `globals.css:59` |
| 30 | P2 | M | Interaction | `/stock/receipts` | "Receive all in full" confirm names the line count, not the items | List up to 3 items + quantities from the cached PO lines | `receipts/page.tsx:1794-1845` |

## P0 findings (all dimensions) — block ship

| ID | Dimension | Route | Description |
|---|---|---|---|
| FLOW-002 | Flow | `/home` | "Needs a report" danger state has no affordance (`TodayBoard.tsx:164`) |
| FLOW-001 | Flow | `/home` | Today's plan rows are not links (`TodayBoard.tsx:239-259`) |
| COPY-004 | Copy | `/stock/production-actual` | Raw enum `PRODUCTION_CONSUMPTION_REVERSAL` in operator copy (`page.tsx:1483`) |
| INTER-002 / A11Y-002 | Interaction + A11y | `/production` corridor | Touch targets 28–56 px against the locked ≥60 px floor (`RunList.tsx:95,247`; `ReportForm.tsx:482,553,606`; `globals.css:533`) |

## P1 findings — conditional-ship items

Rows 5–22 of the ranked list (18 items): five flow seams (report → board, TANK → fill runs, placement → receipt, receipt → queue, forecast roll-forward), three form/interaction hardening items on the report surface, the receipts express buttons, the combobox ARIA gap, the two token/utility items, the `in_production` tone split, and the legacy-surface retirement.

## Per-dimension status

| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 2 | 5 | RED |
| Interaction | 1 | 6 | RED |
| Visual | 0 | 5 | AMBER |
| Copy | 1 | 12 (11 on the legacy surface) | RED |
| Accessibility | 0 | 3 | AMBER |

## portal_ux_standard.md compliance

Violations: §1 (system-internal terms "gap G3", "pinned BOM", "stock ledger", "break-glass", "SKU", raw enums and UUIDs), §3 (actionable-state hygiene on the Today board; loaded-empty chips on the legacy form; confirm without record name), §4 (status tone split), §5 (raw reason-code fallback), §6 (post-action context lost placement → receipt), §7 (touch targets below the 32 px portal floor: "Extra job" 28 px, receipts express 28 px), §8 ("Operator form" eyebrow). PASS: language rule on every audited surface (English-first; Hebrew only on `/planning/procurement`, `/purchase-orders/placement-queue`, viewer cockpit), two-step confirm on every stock-moving action, planned/actual separation, loading and error states present, dialog focus management (`useDialogA11y`), `/production` copy dictionary.

## Verdict

**HOLD** — four P0 findings.

Reading: per-screen quality is good (the report form, the door receipt and the empty states are composed and readable — see `production-runs-RUN1-report-operator-mobile.png`, `stock-receipts-operator-mobile.png`, `production-empty-1-operator-mobile.png`). The failures sit at the **seams** — board → run, tank → fill, placement → receipt, report → board — and on the **legacy** surface that was never retired. That is the same shape the deep review found in the backend: the steps between "produce" and "report" are where the chain breaks.

## Blockers (HOLD)

1. `TodayBoard.tsx:164` — link "Needs a report" to `/production?date=<yesterday>`.
2. `TodayBoard.tsx:239-259` — link each plan row to `/production`.
3. `production-actual/page.tsx:1483` — replace the raw enum string (or redirect the legacy route to `/production`, which also clears rows 20 and 22).
4. `/production` corridor — `btn-touch` (≥60 px) on every interactive control listed in row 4; "Extra job" and PickRow edit first.

All four are portal-source only; no backend, schema, Hebrew register, or token change is needed for the blockers. One bounded tranche, effort S+S+S+M.

## Tom approval required?

**No** for the four blockers. **Yes** for three P1 token changes (`.min-h-touch` utility, `text-4xs` or consolidation to `text-3xs`, `--fg-subtle` value) and for retiring `/stock/production-actual` (its 30-day retirement window expired 2026-08-23; the deep review recommends the redirect as part of report-first).

## Next action for Tom

Approve one portal tranche "gate P0 batch (4 items)" so it can be dispatched independently of the planning-chain decisions — it unblocks the operator's daily entry point regardless of which direction §4 of the deep review takes.
