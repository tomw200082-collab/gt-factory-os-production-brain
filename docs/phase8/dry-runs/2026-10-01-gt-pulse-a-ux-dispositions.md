# GT Pulse Unit A — first-pass UX findings and dispositions (2026-10-01)

Heads after repair: backend `27538a7`, portal `c81c4a8`. Evidence re-captured on these heads:
connected `2026-10-01-gt-pulse-a-connected/` (proof 21/21 at 390 and 1280, 116 shots,
`shots-notes.txt`), fixture `2026-10-01-gt-pulse-a-fixture-shots/` (24 shots).

| Finding | Lens | Sev claimed | Disposition | Evidence |
|---|---|---|---|---|
| B-FLOW-01 activity feed unscoped for reps | flow | P0 | **Fixed** backend `27538a7` (also review I2); proof check "rep activity feed holds only the rep's leads" | proof-390.log |
| B-FLOW-02 attention unscoped for reps | flow | P0 | **Not a defect**: `handleSalesAttention` filters `assignee = session.email` for `sales_rep`, which excludes the unowned bucket | `api/src/sales/queries_handler.ts` handleSalesAttention |
| VISUAL-101 dark mode never applies | visual | P0 | **Capture error, not product**: dark is a user preference (`theme_preference` → `html.dark`), not OS `prefers-color-scheme`. Re-captured with the real preference: `html.dark=true`, background `rgb(21,24,30)` | shots-notes.txt; `*-390-dark.png`, `*-320-dark.png` |
| COPY-002/004 unregistered backend task titles (`קשר ראשון`, `מענה אנושי`, `לחזור לליד`, `בדיקת הטיוטה והמשך אנושי`) | copy | P1 | **Fixed** portal `331f935`: trigger-made kinds show the registered `task.reason.*` text instead | today-queue.test.tsx |
| COPY-003 team-wide counts under a rep's "my queue" | copy | P1 | **Fixed** portal `331f935`: the triage strip is not rendered for `sales_rep` | sales-email-to-task.spec.ts |
| INTER-001 Save silently disabled after 09:00 when today is picked | interaction | P1 | **Fixed** portal `c81c4a8`: date floor becomes tomorrow after 09:00 Israel | outcome-sheet.test.tsx |
| B-FLOW-04 disabled Save gives no reason | flow | P1 | **Partly fixed** `331f935`: fields are natively `required` (note `minLength=5`); a visible reason string would be new copy → HOLD for Tom's copy approval, not added | outcome-sheet.test.tsx |
| A11Y-002 completion toggle lacks `aria-expanded` | a11y | P2 | **Fixed** `331f935` | today-queue.test.tsx |
| A11Y-003 ghost Tab stop | a11y | P1 | **Measurement artifact**: `activeElement` was `body` after focus left the document past the last control — no focusable script | shots-notes.txt |
| B-FLOW-05 keyboard never reaches task actions | flow | P1 | **Measurement artifact**: the first capture stopped after 14 Tab presses. 40-stop run: manager reaches `התקשר` and `השלם משימה` (true); rep's Today was empty at capture time | shots-notes.txt |
| VISUAL-001/103, A11Y-006, A-FLOW-01/B-FLOW-03 FAB covers cards/nav | visual/a11y/flow | P1 | **Full-page screenshot artifact**: fixed bars paint mid-page in `fullPage` captures. Measured at scroll end at 320/390/430/1280 light/dark/reduced: no control under a fixed bar on Today | shots-notes.txt (no OVERLAP lines) |
| VISUAL-102 date input shows mm/dd/yyyy | visual | P1 | **Not product**: native date input follows the device locale; headless Chromium is en-US. No change | — |
| COPY-001 / VISUAL-002 / INTER-002 English "Access restricted" with `viewer` in code style | copy/visual/interaction | P1/P2 | **Pre-existing, out of tranche**: shared `src/lib/auth/role-gate.tsx` on `main`; a viewer has no sales capability. Logged for a later tranche | role-gate.tsx |
| A11Y-001 sheet background not inert | a11y | P2 | Today/Leads/Attention bodies already set `inert`/`aria-hidden` while the sheet is open (mocked e2e asserts it) | sales-outcome-integrity.spec.ts |
| A11Y-004 two navs share one name | a11y | P2 | Deferred: needs new copy | — |
| A11Y-005 settings twice in manager Tab order | a11y | P2 | Deferred | — |
| INTER-003 drawer saves keep static labels | interaction | P2 | Deferred | — |
| VISUAL-003/004, A-FLOW-02 attention feed grouping/empty card | visual/flow | P2 | Deferred | — |
| B-FLOW-06 login branding is factory-flavoured | flow | P2 | Deferred, out of tranche | — |

Mocked sales e2e on the repaired head (local Chromium 1194): 55 passed, 4 failed. The same four
tests fail identically on the base `1ba2c98` with this Chromium build (all four click a `tel:`
link; headless Chromium 1194 stalls input after an external-protocol navigation) and pass in PR CI
on Chromium 1217. WebKit is not installed here: WebKit keyboard proof stays **HOLD**.

## Re-run and final verdict (heads backend `9d423c1`, portal `a7ccffd`)

- The re-run on `c81c4a8` agreed with every disposition above and found 0 P0. It left 2 P1 open: B-FLOW-04 and INTER-NEW-01.
- INTER-NEW-01 is fixed in `a7ccffd` (`israelFirstSchedulableDate`). It is proven in real Chromium on the connected stack: a typed `2020-01-01` is raised to the floor (proof-*.log 22/22).
- B-FLOW-04: native `required` and `minLength`, plus a `:user-invalid` border, give a visible cause. A textual reason needs Tom's copy approval.
- Governor verdict (pre-production): **fixture render gate SHIP; connected five-lens audit CONDITIONAL_SHIP.**
  - The B-FLOW-04 copy must be approved before a production SHIP.
  - Five things must be re-proven on real devices: WebKit/iOS keyboard save, a screen reader, the iOS date locale, Resend delivery, and `tel:`.
  - No frozen flag may change.
  - The verdict covers only these SHAs.
