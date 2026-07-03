# DR-018 — UX Release Gate: Thursday→Sunday Production-Planning Corridor

Date: 2026-07-03 · Invoked by: Tom (`/ux-release-gate`) · Mode: manual, corridor-scoped
Evidence mode: **code-read** (remote sandbox — render harness unavailable; visual/layout findings
marked CONFIRM-BY-RENDER except where structurally verified by grep). All five UX agents dispatched.

## Scope
`/planning/meeting` · `/planning/production-plan` · `/planning/procurement` · `/purchase-orders/placement-queue`
· `/planning` (overview) · `/planning/inventory-flow` · `/planning/production-simulation` · `/planning/forecast`
+ the `plan-production-14d` skill flow contract.

## Top-12 ranked actions (the deliverable)

| # | Sev | Effort | Dimension | Route | Finding | Proposed fix | Evidence |
|---|-----|--------|-----------|-------|---------|--------------|----------|
| 1 | P0 | S | Flow | sidebar | Firm cockpit `/planning/meeting` absent from nav manifest — Thursday's most critical action is undiscoverable | Add "Weekly Meeting" entry to Planning nav group | `src/lib/nav/manifest.ts:216-318` |
| 2 | P0 | S | Visual | /planning/procurement + PO family | `.btn-accent` used on 10+ primary CTAs but **never defined** in globals.css → primary actions render as neutral buttons. Scope verified by grep: procurement FocusCard/ActionList/AddLineForm + purchase-orders new/list/[po_id] | Alias `.btn-accent` → `.btn-primary` in globals.css (token decision: Tom) or replace class at call sites | `ActionList.tsx:261,269` + grep: zero definition in `globals.css`/`tailwind.config.ts` |
| 3 | P0 | M | Interaction | /planning/meeting | "Generate / refresh drafts" fires with **zero confirmation** yet wipes all `TEAEDD:%` drafts incl. Tom's hand-edits (the exact trap the skill forbids for itself — portal leaves it one click away) | Two-step inline confirm (same pattern as Firm week) naming the destructive scope | `meeting/page.tsx:470` |
| 4 | P0 | M | A11y | /planning/procurement | FocusMode dialog: no focus-in on open, no focus-restore on close — keyboard/AT operator loses position every session | Capture activeElement on mount, focus container, restore on unmount (pattern exists in `useDialogA11y`) | `FocusMode.tsx:139-205` |
| 5 | P0 | M | A11y | /planning/inventory-flow | `role="gridcell"` orphaned — no `role="grid"`/`role="row"` ancestors; AT grid navigation non-functional | Add `role="grid"` to scroll container + `role="row"` per item row + row/colcount | `DayCell.tsx:107`, `FlowGridDesktop.tsx:194,209` |
| 6 | P1 | S | Copy | /planning/meeting | "Firm week" is lexicon-absent jargon; overview says "lock the week" — same concept, two words, one click apart | Rename all 6 occurrences to "Lock week"/"Confirm lock"/"Locking…"/"locked" | `meeting/page.tsx:479,533-539,691,717,733,738` |
| 7 | P1 | S | Interaction | /purchase-orders/placement-queue | "בצע הזמנה" (terminal, irreversible) reachable with missing prices/terms — validation only fires post-click | Disable until `canPlace` (all prices >0 + term selected) + tooltip | `PlacementRow.tsx:372-387` |
| 8 | P1 | S | Interaction | /purchase-orders/placement-queue | Empty `confirmedDate` silently omitted from confirm dialog — re-opens the documented no-ETA double-order trap at the human step | Append missing-ETA warning sentence to confirm description when date blank | `PlacementRow.tsx:111-113` |
| 9 | P1 | S | Flow+Copy | /purchase-orders/placement-queue | Empty state indistinguishable from upstream-bug state (masked the live trigger bug until 2026-07-03) + no overdue/aging page banner | Add "if you know orders were approved and nothing appears — contact planning" line + overdue-count alert banner | `placement-queue/page.tsx:119-130` |
| 10 | P1 | S | Flow+Interaction | /planning/production-plan | Stage-4 "סיימתי" handshake is chat-only; no portal affordance; drafts can sit indefinitely | Persistent info banner when draft rows exist: "done editing → return to planning chat / Weekly Meeting to lock" | `production-plan/page.tsx:1848-1880`, SKILL.md stage 4 |
| 11 | P1 | S | Interaction+Copy | /planning/meeting | 403/503 render raw API strings ("break-glass" jargon); no retry on generate-drafts error | Map status→operator copy + "Try again" button | `meeting/page.tsx:496-499,558-563`, `cadence.ts:326` |
| 12 | P1 | M | Flow | /planning (overview) | Pipeline block (Demand→Run→Recommendations) implies the ordering path; real path is Forecast→Meeting→Procurement — wrong-turn risk | Retitle "Engine diagnostic" + one-line disclaimer pointing to the real corridor | `planning/page.tsx:677-684,745-771` |

## P0 findings (block ship)

| ID | Dimension | Route | Description |
|---|---|---|---|
| FLOW-001 | Flow | sidebar | /planning/meeting not in nav manifest — firm cockpit undiscoverable |
| VISUAL-001 | Visual | procurement + PO family | `.btn-accent` undefined; 10+ primary CTAs render unstyled |
| INTER-001 | Interaction | /planning/meeting | Generate-drafts destructive, zero confirmation |
| A11Y-001 | A11y | /planning/procurement | FocusMode no focus-in/restore |
| A11Y-002 | A11y | /planning/inventory-flow | Orphaned gridcell roles; AT grid model broken |

## P1 findings (conditional-ship items)
Interaction: INTER-002 (expose `is_user_modified` in plan DTO — **column already exists in `production_plan`**, verified live 2026-07-03; effort is DTO+badge, not schema), INTER-003, INTER-004, INTER-005 (supersede confirm lacks PO count), INTER-006.
Flow: FLOW-003 (overview wrong-turn), FLOW-004 (queue empty-state honesty), FLOW-005 (procurement lacks firmed-week context header), FLOW-006 (no overdue banner).
Copy: COPY-001 (firm→lock), COPY-002 (break-glass), COPY-003 ("Report Production"→"Open Production Report"), COPY-004 (simulation banner negative framing deters legitimate use — replace with "Use this to check material needs before committing…"), COPY-006, COPY-007 (done state color-only, add "Completed" chip), COPY-008 (raw `item_id` fallback in destructive confirms).
Visual: VISUAL-002 (commitment panel visually detached from firm CTA), VISUAL-003 (4 card dialects for same entity), VISUAL-004 (2 badge sources), VISUAL-005 (mobile board strategy).
A11y: A11Y-003..008 (focus rings ×2, tablist arrows via existing `useRovingTabList`, unicode arrows, enum aria-labels, dead tab stops).

## P2 (polish)
INTER-008/009/010, COPY-009/010, VISUAL-006/007/008, A11Y-009/010, FLOW-007..010 (chip→meeting link, inventory-flow/simulation corridor-role captions, forecast Hebrew normalization ref).

## Per-dimension status
| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 1 | 4 | RED |
| Interaction | 1 | 5 | RED |
| Visual | 1 | 4 | RED |
| Copy | 0 | 7 | AMBER |
| Accessibility | 2 | 6 | RED |

## portal_ux_standard.md compliance
Violations noted: §1 lexicon ("Firm week", "Report Production", raw `item_id` fallback, enum tier names
in aria-labels), §4 color-alone status (done state, draft state single-signal), §3 empty-state honesty
(placement queue). Hebrew surfaces (procurement, placement-queue) fully compliant — zero English leakage.

## Verdict
**HOLD** — 5 P0 findings present.

## Blockers (exact locations in Top-12 rows 1–5)
All five are portal-layer; none requires schema change. Estimated total effort: 2 S + 3 M.

## Conditions
n/a (HOLD). On P0 closure, re-gate; P1 list above becomes the conditional-ship register.

## Tom approval required?
yes — (a) `.btn-accent` token decision (alias vs call-site replacement), (b) tranche authorization for
the P0 batch, (c) INTER-007 long-term design (portal "done editing" flag vs chat-only convention).

## Next action for Tom
Approve a P0-fix tranche (5 items, rows 1–5) — then re-run `/ux-release-gate` for CONDITIONAL_SHIP.

---
Session corrections applied to agent findings: VISUAL-001 scope widened (grep: PO family included);
INTER-002 effort downgraded (DB column exists — live-verified). Render-dependent items
(contrast, touch targets, mobile board) flagged CONFIRM-BY-RENDER for a harness pass on CI/local.
