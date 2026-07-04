# DR-019 — /ux-release-gate: Weekly Meeting ↔ Daily Production Plan corridor

- **Date:** 2026-07-04
- **Invoked by:** Tom (interactive), args: improve the workflow of /planning/meeting so it works simply and synergistically with /planning/production-plan; target: perfect flow, maximum precision, no mid-work interruption, no orphaned open drafts.
- **Scope:** `/planning/meeting` + `/planning/production-plan` (+ their `_lib`/`_components`, and the backend contracts they call: `generate-drafts`, `draft-week`, `firm-week`, `production-plan` reads).
- **Agents:** ux-flow-architect, interaction-design-specialist, visual-system-designer, ux-content-state-designer, accessibility-usability-auditor. Verdict issued mechanically per gate thresholds (any P0 → HOLD); no governor arbitration needed.
- **Visual evidence:** render-grade via `tests/e2e/ux-shot.spec.ts` (dev-shim auth, fixture-stubbed APIs — no portal source touched). Screenshots stored alongside this report:
  - `DR-019-shot-planning-meeting-planner-desktop.png` — meeting page on a Saturday: lands on Execute step; Lock/Generate surfaces are entirely absent from view (renders FLOW-G01/INT-04 visible).
  - `DR-019-shot-planning-production-plan-planner-desktop.png` — production-plan on current week: header reads "Engine drafts below are waiting for your review… 6 planned" while every visible lane says "No production planned" (the plan lives 2 weeks ahead) — live render of the state-contradiction Tom reported.
  - Note: the FirmPanel (Lock step) itself is day-gated and was not rendered; VIS-01 remains code-read, render-unverified.
- **Live failure evidence feeding this gate (from the 2026-07-04 planning session):** engine drafts duplicated an already-planned week (engine blind to item-level manual rows); Tom could not see existing TEAEDD drafts ("אני לא רואה אותן בפורטל"); matcha drafts dated outside the firm window linger orphaned; Tom manually added item-level rows on a day already holding a base batch with no warning.

---

## UX release gate

### Scope
`/planning/meeting`, `/planning/production-plan`

### Top-15 ranked actions (the deliverable — one list, all dimensions)

| # | Sev | Effort | Dimension | Route | Finding | Proposed fix | Evidence |
|---|-----|--------|-----------|-------|---------|--------------|----------|
| 1 | P0 | S | Flow | both | Draft dead-zone: production-plan defaults to current week, meeting FirmPanel defaults to week+2 — drafts for week+1 (or any off-screen week) are invisible on both pages; no global "N drafts pending" indicator. Confirmed cause of "I don't see the drafts". | Global draft-horizon count on meeting Execute panel + production-plan header, independent of visible week; week+1 draft count on the incoming-week strip | `cadence.ts:220-221`, `production-plan/page.tsx:1523,2011`; shot: production-plan header vs empty lanes |
| 2 | P0 | S | Interaction | /planning/meeting | Generate-error "Try again" calls `gen.mutate()` directly — bypasses the two-step confirm that protects hand-edited drafts from deletion | Route retry through `setConfirmingGen(true)` + `gen.reset()` instead of direct mutate | `meeting/page.tsx:557-568` |
| 3 | P0 | M | Flow | /planning/production-plan | ManualAddModal has no same-day base-batch overlap check — adding an item-level plan on a day already holding a base batch silently doubles production intent (happened live on 12/7) | Pre-flight scan of `plansQuery` rows for same-date `is_base_batch`; confirm dialog via existing `useConfirm` pattern | `production-plan/page.tsx:1790-1827` |
| 4 | P0 | M | Flow | /planning/meeting | Engine is blind to manual item-level plans (`base_bom_head_id` null) when computing tank capacity/receipts → drafts over already-planned days; confirm copy "Manually added plans are not affected" is true but critically incomplete | Portal: post-generate overlap warning banner. Backend (ARCH_REQUIRED → backend-db-executor): make `fn_plan_tea_production` count item-level planned rows as capacity+supply | `handler.generate_drafts.ts:136-137`, `meeting/page.tsx:489-491` |
| 5 | P0 | M | Visual | /planning/meeting | Thursday primary CTA "Lock week" renders below week nav + KPI tiles + full 5-day board + near-week strip — below the fold at 768px (code-read, render-unverified) | Lead FirmPanel with a compact "Ready to lock?" action strip (Lock Week + batch count + week range); board becomes supporting detail below | `meeting/page.tsx:729-836` |
| 6 | P1 | S | Flow | /planning/meeting | "Fine-tune →" link to production-plan carries no `?week=` — lands on wrong week (page already honors `?week=`) | `href="/planning/production-plan?week=${nearWeek}"` — one line | `meeting/page.tsx:719`, `production-plan/page.tsx:1532-1538` |
| 7 | P1 | S | Interaction | /planning/meeting | Non-Thursday visits land on Execute; Lock step shows no pending-draft badge — unfirmed drafts invisible for days | `pendingDraftCount` chip on the Lock step in CadenceRail | `meeting/page.tsx:69-73,989-991`; shot: meeting page |
| 8 | P1 | S | Copy | both | "firm"/"firmed" and "lock"/"locked" used interchangeably (10+ occurrences) — no canonical term; proposes §1 lexicon entry (Tom approval) | Adopt "Lock/Locked" everywhere; add lexicon row to portal_ux_standard.md §1 | `meeting/page.tsx:463,637,651,655,798-799,816,861,948,1006`, `ProductionJobCard.tsx:268` |
| 9 | P1 | S | Interaction | /planning/meeting | Generate confirm copy lacks batch count + target week anchor — can overwrite the wrong week's work after week-nav | Interpolate `batchCount` + `fmtWeekRange(weekStart)` into confirm sentence | `meeting/page.tsx:489-490` |
| 10 | P1 | S | Flow | /planning/meeting | Generate success says "N batches waiting across the horizon" while the visible board may show 0 — no bridge to the week containing the new drafts | Include earliest-draft week range + navigation hint in success banner (or `earliest_draft_week_start` in API response) | `meeting/page.tsx:543-548`, `handler.generate_drafts.ts:34-36` |
| 11 | P1 | S | Flow | /planning/meeting | Past-dated orphan drafts (e.g. matcha outside the firm window) counted nowhere; persist silently until next generate wipes them | Surface "N draft batches from past dates — won't be firmed, removed on next generate" under the Draft-batches KPI | `handler.generate_drafts.ts:47-53` |
| 12 | P1 | S | Interaction | /planning/meeting | Lock success banner claims "Reversible via the production plan" — no bulk un-lock exists; reversal = N manual cancels | Honest copy + count + week-targeted link; bulk `cancel-firmed-week` endpoint escalated (ARCH_REQUIRED, INT-06) | `meeting/page.tsx:608` |
| 13 | P1 | S | Interaction | /planning/production-plan | Edit modal for a draft is identical to a firmed plan's — no "edits may be overwritten by next Generate" notice | Conditional notice under modal title when `status==='draft'` | `production-plan/page.tsx:893-896` |
| 14 | P1 | S | Copy | /planning/production-plan | Card title "Base batch · N SKUs" + toasts "base batch (N SKUs)" — forbidden §1 term (breakdown list itself was fixed today) | "Base batch — N products" everywhere | `ProductionJobCard.tsx:81`, `production-plan/page.tsx:1596` |
| 15 | P1 | S | A11y | /planning/meeting | Focus lost when inline Generate/Lock confirms collapse (cancel or settle) — keyboard user dropped to document.body | Trigger-button refs + focus restore on `confirming*` → false | `meeting/page.tsx:388-405` |

Remaining findings (9 more P1, 17 P2) are in the per-dimension audit trail below.

### P0 findings (all dimensions) — block ship
| ID | Dimension | Route | Description |
|---|---|---|---|
| FLOW-G01 | Flow | both | Week-window dead-zone hides drafts from both pages; no cross-page pending-drafts signal |
| INT-01 | Interaction | /planning/meeting | Error-retry path bypasses the destructive-action confirmation on generate-drafts |
| FLOW-G02 | Flow | /planning/meeting | Engine blind to manual item-level plans → duplicate drafts over planned days (portal warning + backend ARCH fix) |
| FLOW-G03 | Flow | /planning/production-plan | Manual add has no same-day base-batch overlap guard |
| VIS-01 | Visual | /planning/meeting | Primary "Lock week" CTA below the fold at standard viewport (render-unverified for the day-gated FirmPanel) |

### P1 findings — conditional-ship items (summary)
FLOW-G04..G08 (edited-badge on meeting chips + draft-week API field; success-banner week bridge; orphan count; deep-link with step+week), INT-02..INT-06 (confirm anchors; honest reversal copy; pending badge; draft-edit notice; ARCH: bulk un-lock endpoint), VIS-02..VIS-05 (draft vs in-production chip tones; cancelled chip; CadenceRail stepper states; overdue lane surface), COPY-01..COPY-06 (lock lexicon; at-risk SKUs→products; SKU in titles/toasts; generate trigger consequence label; draft-chip link phrasing; firm-error template+retry), A11Y-01..A11Y-04 (focus restore; day-lane group labels; motion-reduce on skeletons; aria-pressed+live on recommendation picker).

### Per-dimension status
| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 3 | 5 | RED |
| Interaction | 1 | 5 | RED |
| Visual | 1 | 4 | RED |
| Copy | 0 | 6 | AMBER |
| Accessibility | 0 | 4 | AMBER |

### portal_ux_standard.md compliance
Violations noted: §1 lexicon ("SKU" in operator copy ×3 surfaces; firm/lock dual vocabulary — standard has no entry, lexicon update proposed and requires Tom approval), §3 state hygiene (meeting-page result banners lack dismiss/auto-clear; firm-error shows raw `error.message` with no retry), §4 status semantics (planned cards carry no chip; cancelled cards carry no chip; draft and in-production share one chip tone), §9 banner pattern (planned-only bar uses neutral surface instead of info tokens).

### Verdict
**HOLD** — 5 P0 findings present (threshold: any P0 → HOLD).

### Blockers
1. **FLOW-G01** — `cadence.ts:220-221` + `production-plan/page.tsx:1523,2011`: add horizon-wide draft counters on both pages + week+1 draft count on the incoming strip.
2. **INT-01** — `meeting/page.tsx:557-568`: retry must re-enter the confirm step, never call `gen.mutate()` directly.
3. **FLOW-G02** — portal overlap-warning after generate (`meeting/page.tsx` success path) + backend `fn_plan_tea_production` capacity fix (route to backend-db-executor; migration touching 0216-era function).
4. **FLOW-G03** — `production-plan/page.tsx:1790-1827`: same-day base-batch guard in `handleManualAdd` with confirm dialog.
5. **VIS-01** — `meeting/page.tsx:729-836`: action-first FirmPanel layout ("Ready to lock?" strip above the board).

### Conditions
n/a (HOLD).

### Tom approval required?
yes — (a) approve the P0 fix batch, (b) approve the §1 lexicon update ("Lock/Locked" canonical; "firm" retired from operator copy), (c) approve routing two ARCH_REQUIRED items to the backend lane: engine capacity awareness of manual plans (FLOW-G02) and a bulk `cancel-firmed-week` endpoint (INT-06).

### Next action for Tom
Say "תקן את החוסמים" to execute the five P0 fixes now (4 portal-side + the FLOW-G02 portal warning; the two backend ARCH items get routed separately), or name which subset to start with.

---

## Audit trail — full per-dimension findings

The complete agent reports (findings tables + handoff packets) are preserved verbatim in the session transcript of 2026-07-04. Condensed registers:

### Flow (ux-flow-architect) — 3 P0 / 5 P1 / 2 P2
G01 draft dead-zone (P0/S) · G02 engine blind to manual rows (P0/M, ARCH) · G03 no manual-add overlap guard (P0/M) · G04 edited-drafts invisible on meeting chips, draft-week API lacks `is_user_modified` (P1/M) · G05 generate-success lacks week bridge (P1/S) · G06 Fine-tune link missing `?week=` (P1/S) · G07 orphaned past-dated drafts uncounted (P1/S) · G08 draft-banner deep-link lacks step+week (P1/S) · G09 tank-days KPI ignores manual plans — disclosure footnote (P2/S) · G10 manual-add success toast lacks week-state hint (P2/S).

### Interaction (interaction-design-specialist) — 1 P0 / 5 P1 / 4 P2
INT-01 retry bypasses confirm (P0/S) · INT-02 confirm lacks count+week anchor (P1/S) · INT-03 "Reversible" copy inaccurate (P1/S) · INT-04 no pending-draft badge on Lock step (P1/S) · INT-05 draft edit modal lacks overwrite notice (P1/S) · INT-06 no bulk un-lock — backend endpoint required (P1/L, ARCH) · INT-07 "Keep current drafts" enabled mid-mutation (P2/S) · INT-08 result banners lack dismiss/auto-clear (P2/S) · INT-09 draft banner leads with Planning Overview detour (P2/S) · INT-10 cancel modal lacks draft-regeneration notice (P2/S).

### Visual (visual-system-designer) — 1 P0 / 4 P1 / 3 P2
VIS-01 Lock CTA below fold (P0/M) · VIS-02 draft + in-production share chip-info (P1/S) · VIS-03 cancelled cards have no chip (P1/S) · VIS-04 CadenceRail lacks stepper numbers/done states (P1/M) · VIS-05 overdue lane surface = future lane surface (P1/S) · VIS-06 pack-breakdown needs separator/eyebrow (P2/S) · VIS-07 planned-only bar not on info tokens (P2/S) · VIS-08 pack breakdown drops uom — `fmtQty(line.qty, line.uom)` (P2/S).

### Copy (ux-content-state-designer) — 0 P0 / 6 P1 / 4 P2
COPY-01 firm/lock unify (P1/S, + §1 lexicon update, Tom approval) · COPY-02 "at-risk SKUs"→products (P1/S) · COPY-03 "N SKUs" in title/toasts→products (P1/S) · COPY-04 generate trigger consequence label (P1/S) · COPY-05 draft-chip link phrasing (P1/S) · COPY-06 firm-error template + retry (P1/S) · COPY-07..10 polish (firm/lock stragglers, "horizon" jargon, tooltip jargon) (P2/S). Hebrew/EN check: both routes clean English-first (not in exception list).

### Accessibility (accessibility-usability-auditor) — 0 P0 / 4 P1 / 4 P2
A11Y-01 focus restore after inline confirms (P1/S) · A11Y-02 day-lane `role="group"`+label (P1/S) · A11Y-03 motion-reduce on skeletons/progress (P1/S) · A11Y-04 aria-pressed + live region in recommendations picker (P1/S) · A11Y-05 CadenceRail tablist semantics (P2/S) · A11Y-06 BatchChip aria-label on generic div (P2/S) · A11Y-07 persistent live-region containers (P2/M) · A11Y-08 per-route document titles via server shells (P2/M).

---

**Write policy:** saved to `PRODUCTION/docs/phase8/dry-runs/` (default, pre-approval). After Tom approval this gate record may be copied to `gt-factory-os-portal/docs/ux/`.
