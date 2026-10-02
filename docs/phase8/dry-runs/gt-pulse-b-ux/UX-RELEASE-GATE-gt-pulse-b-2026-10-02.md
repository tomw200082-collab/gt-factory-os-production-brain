# UX release gate: GT Pulse Unit B portal (sales profile, strict)

**Date:** 2026-10-02
**Scope:**
- `/sales/orgs` (list, filters, search, bulk owners)
- `/sales/orgs/[id]` (workspace, circle, orders timeline, sheets, contacts)
- `/sales/orgs/review` (identity review)
- the command palette
- the lead-drawer link

Roles: manager (admin, planner) and rep (`sales_rep`). Widths 320 to 1440px; light, dark and reduced motion; a touch phone.
**Portal:** `gt-factory-os-portal` branch `claude/gt-pulse-b-portal`, release PR #244, final tip `550e04c` (tranches 189 to 196).
**Backend:** gt-factory-os #339 (`held_by` on identity candidates), merged as `e9855e8`.
**Rule:** Unit B passes only with P0 = 0 and P1 = 0. Fixtures are synthetic; there are no real customers and no production sessions.

## Rounds

| Round | Tip | Flow | Interaction | Visual | Content | Accessibility | Total P0 / P1 |
|---|---|---|---|---|---|---|---|
| 1 | 2263955 | 1 / 4 | 1 / 6 | 0 / 3 | 0 / 7 | 0 / 3 | **2 / 23** |
| 2 (after tranche 193) | 6e43849 | 0 / 0 | 0 / 1 | 0 / 1* | 0 / 1 | 0 / 1 | **0 / 4** |
| 3 (after the timeline redesign, tranche 194) | bd34575 | — | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 1 | **0 / 2** |
| 4 (final, after tranches 195 and 196) | 3310d29 | — | 0 / 0 | — | — | 0 / 0 | **0 / 0** |

\* VIS-B-008 (merge sheet light in dark mode) was not a product defect. The screenshot script emulated the colour scheme without the portal's `dark` class. Re-rendered with the class, the sheet is dark; the visual lens closed it.

Round 4 re-audited only the lenses that still had open items. Flow, visual and content had passed at P0 0 / P1 0 in the round before. The one change after round 4 (`550e04c`) is the list's address-sync fix found by the full e2e run. It has its own red-first unit test, and journeys A and K passed 16/16 over 8 repetitions.

## The findings that mattered

- **FLOW-B-001 (P0).** A business moved to a distributor showed days of silence (T5). Fixed.
- **INTER-B-001 (P0).** An irreversible merge did not name the business it merges into.
  - Fixed end to end with a backend field (#339, `held_by`).
  - The candidate card says "כבר שייך לעסק …".
  - The confirm names both businesses, says the record closes for good, and asks "כן, לאחד".
  - The toast links to the destination and stays until it is closed.
- **COPY-B-012 (P1).** The merge copy promised that every contact moves. The API moves only those the destination lacks, and the copy now says so.
- **A11Y-194-001 (P1).** Timeline month columns are about 15px wide on a phone. Tom's ask (two years at a glance) is kept:
  - a finger drawn along the chart chooses a month;
  - 44px previous/next buttons reach every month (the WCAG 2.5.8 equivalent-control exception).
- **INTER-NEW-001 (P1).** The two years disappeared when their read failed. They now keep their place, say what failed and offer a retry.

The full lists, fixes and rejected or deferred items are in the tranche manifests `docs/portal-os/tranches/193` to `196` in the portal repo.

## Evidence

- vitest 1737/1737 · typecheck 0 · eslint 0 errors · `next build` green.
- Playwright `@mocked` (chromium) 150/150, including `sales-orgs.spec` 21/21: journeys A to K, Tom's timeline, the moved branch, a 320 to 1440 matrix with no sideways scroll, 44px targets, dark mode with reduced motion, sheet layering, bulk owners, and a touch-phone run with a finger scrub.
- Rendered evidence was in the session's scratch space and is not committed (synthetic data only).

## Verdict

**SHIP** (strict: P0 0, P1 0).

## Residuals (not blocking)

- **No WebKit or real iPhone run.** The environment has no WebKit, so touch was tested with Chromium touch emulation.
- **8 review orgs (`customer_not_verified`) cannot be resolved from the portal.** The held customer is not in the mirror, and resolving them needs a backend change.
- **Deferred P2s**, named in the tranches:
  - a shared panel shell;
  - `<bdi>` value components;
  - the toast timer inside `Toast`;
  - a single gesture model;
  - the month sheet's paging progress;
  - reopening the lead drawer on return.

## Tom approval required?

No, for the UI. Design, UX and copy were delegated on 2026-10-02. The 26 identity decisions and Ice Dream (U-055) stay Tom's, and this release decides none of them.
