# UX release gate — tranche 147 (report-production flow)

**Date:** 2026-07-24
**Branch:** `claude/production-report-flow-myf5b6` (portal + backend + brain)
**Scope:** `/planning/production-plan` report CTA · `/production` · `/production/runs/[run_id]` · `/production/runs/[run_id]/report`
**Lenses run:** all five (flow, interaction, content/state, accessibility, visual)

## Verdict

**CONDITIONAL_SHIP** — zero P0 findings remain. Two P1 copy findings are held for Tom because they are a genuine conflict between two authorities, not an oversight (see Conditions).

## What the gate caught that mattered

Three of the four most serious findings were **second-order effects of this tranche's own changes** — the reason the gate is worth running rather than assuming a clean diff is a safe one.

| ID | Sev | Finding | Status |
|---|---|---|---|
| INTER-147-01 | P0 | No confirmation on the one action that moves stock. Tranche 146 deferred a confirm here reasoning that the empty output field was itself a pause; tranche 147 pre-fills that field, so the pause went and the guard went with it. A stray tap on arrival could commit stock at the planned quantity. | **Fixed** — two-step confirm naming product + number; editing the number backs out of it. |
| FLOW-013 | P0 | `handlePickList` answered 409 for REPORTED/CANCELLED runs while the portal treats any non-2xx as a network failure. The read-only screens the portal already had for both states were unreachable dead code, and tapping a Done run showed "Could not load the materials" with a Try-again that could never succeed. Secondary: the GET flipped PLANNED → PICKING, so opening a report marked a never-collected run as "Collecting". | **Fixed** — terminal runs answer 200 from `production_run_pick`; `?intent=report` suppresses the flip. |
| FLOW-001 | P0 | `report_stock_note` claimed materials come off stock, which is false for a run nobody collected for — the primary new path in this tranche. | **Fixed** — hedged to "any materials you collected". |
| FLOW-002 | P1 | A TANK run was offered "Report production" from two places in `PickList`, both leading to a 409 with no way out. | **Fixed** — gated on `isRunReportable`, with copy saying where to go. |
| FLOW-003 / INTER-147-02 | P1 | Back-dated reporting bounced to today after every report. A base batch is a tank plus one run per product, so reporting yesterday meant re-picking the date three times. | **Fixed** — `?date=` threads through to the report screen. |
| FLOW-004 | P1 | Success screen ignored `linked_plan_id` — no way back to the plan card the journey started from. | **Fixed** — "See it on the plan" links back with `?focus_plan=`. |
| FLOW-005 | P1 | The new `shortfalls` array was never surfaced. A partial deduction (stale projection) was invisible to the only person who could report it. | **Fixed** — success screen says so plainly. |
| FLOW-010 | P1 | Portal typed `item_id` / `item_name` non-null; the backend has always sent null for TANK runs, so `runDisplayName` could print "null" as a heading. | **Fixed** — nullable + a named fallback. |
| INTER-147-06 | P1 | Plan card said "Report actual" off-today and "Report production" today — one journey, two names, and "actual" is a word the standard avoids. | **Fixed** — one label. |
| COPY-003 | P1 | Same as FLOW-001, found independently. | **Fixed**. |
| A11Y-147-01/02 | P1 | Focus rings at 50% alpha land near 2.1:1 against the card; WCAG asks 3:1 of a focus indicator. | **Fixed** — full-strength ring + offset. |
| A11Y-147-03 | P1 | The pre-filled quantity had no announced provenance — a screen-reader user could commit a number without knowing it came from the plan. | **Fixed** — `aria-describedby` to the hint. |
| A11Y-147-04 | P1 | The stock consequence lived only in a `title`, which keyboard focus does not surface. | **Fixed** — `aria-describedby` on submit. |
| A11Y-147-05 | P1 | Skeletons ignored `prefers-reduced-motion` while the spinner beside them honoured it. | **Fixed**. |
| A11Y-147-06 / 12 | P1/P2 | 28px and 44px controls on a gloved-touch surface. | **Fixed** for the controls this tranche added. |
| A11Y-147-09 | P2 | Live region announced the today subtitle on a past day. | **Fixed**. |
| VISUAL (banner) | P1 | The new timing note stacked above the committed banner and buried its CTA. | **Fixed** — gated on `!committed`. |
| VISUAL (group) | P1 | The card restructure let the footer action drive the body's hover animation. | **Fixed** — named groups. |
| VISUAL / COPY (misc) | P2 | `<p>` styled as a panel; arbitrary spacing brackets; hint alignment; "one planned job" for a multi-run plan; "then" implying collecting is a precondition; the not-reportable error blaming the planner. | **Fixed**. |

Also fixed while in-file: three stale code comments still describing stock moving at pick time, and three pre-existing type errors in `production-runs/handler.ts` (`floor_name` missing from an `Omit`) that made the module fail to typecheck on `main`.

## Conditions (Tom's call — held deliberately, not overlooked)

**COPY-001 / COPY-002 — status words.** The content lens flags `run_status_done: "Done"` → `"Completed"` and `run_status_todo: "To do"` → `"Planned"` per the `portal_ux_standard.md` §1 lexicon, where "done" is explicitly in the avoid column.

Held, because two authorities disagree and the tie is Tom's to break:

- The lexicon was written for planner-facing surfaces.
- `/production` has an explicit, documented mandate to use simple English for Denis, who reads English poorly. "Done" and "To do" are the simpler words, and they shipped through Gates 145 and 146 with Tom's Gate-5 sign-off.

Changing them would regress the reading level this surface was deliberately tuned to. Applying the lexicon silently, or ignoring it silently, both seemed worse than asking. **COPY-004** is the same shape: the content lens itself proposed amending the standard to accept the short form "Report production" rather than treating it as a violation.

## Deferred, with reasons

| ID | Why not now |
|---|---|
| FLOW-012 | Needs a new `report_submission_id` field on the pick-list response to link the audit trail. Real, but a backend contract addition on a rare path (re-opening an already-reported run). |
| A11Y-147-07 | `--fg-subtle` at 3.09:1 is a design-token fix; `globals.css` is frozen for this OS. Token-level escalation, not a corridor tranche. |
| A11Y-147-08 | QC `aria-controls` persistence needs the panel always rendered. Pre-existing, unchanged by this tranche. |
| A11Y-147-10 / 11 | Stepper labels and a link-destination suffix need lexicon coordination — same open question as COPY-001/002. |
| A11Y-147-13 / INTER-147-03 (steppers) | Stepper heights are pre-existing sizes from Gates 145/146. |
| INTER-147-04 | No affordance to restore the pre-fill after clearing. The planned quantity is already on screen in the header ("Making 200 L"), so recovery is reading it off the same view. |
| FLOW-006 | Rendering the actual date in the past-day title. The date sits in the picker directly below it. |

## Per-dimension status

| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 0 | 0 | GREEN |
| Interaction | 0 | 0 | GREEN |
| Content / state | 0 | 2 (held for Tom) | AMBER |
| Accessibility | 0 | 0 | GREEN |
| Visual | 0 | 0 | GREEN |

## Evidence

- Portal: `tsc --noEmit` clean · `eslint` clean · `vitest run` **1080/1080**, 129 files.
- Backend: `cd api && tsc --noEmit` → **0 errors in `production-runs`** (3 on `main`) · `npm run test:production-runs` **18/18**.
- **Not evidenced:** render-grade screenshots. The gate asks visual findings to cite a screenshot; the harness could not launch in this container (the installed Playwright wants a Chromium build that is not present, and `playwright install` is not permitted here). The visual lens produced two P1s from a partial render plus code reading; the rest of its findings cite `file:line`. Worth a re-run with screenshots before this ships.
- **Not evidenced:** the pgTAP suite. `db/tests/0295_production_run_picking.test.sql` is updated for the new ordering but pgTAP is not installed here and no Postgres is reachable.

## Tom approval required?

**Yes** — for the COPY-001/002/004 lexicon question above. Nothing else is blocked.

## Next action for Tom

Decide whether `/production` keeps Denis's words ("Done", "To do", "Report production") or moves to the standard lexicon ("Completed", "Planned", "Open Production Report"). Either answer is one small commit; the surface should not be left with the two authorities disagreeing.
