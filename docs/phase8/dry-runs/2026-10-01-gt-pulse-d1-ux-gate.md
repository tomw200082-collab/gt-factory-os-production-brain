# GT Pulse D1 — UX release gate, sales profile (2026-10-01)

## Scope

**Corridor:** the Hebrew RTL sales corridor `/sales/*`: today, leads, lead card (drawer), attention, orgs, settings.

**Code:**
- D1 is live at portal `e6d7e7f`.
- The follow-up is on `fix/gt-pulse-d1-review`:
  - `907aad7`: simplify pass.
  - `ea39d8f`: lead card redesign, sideways-scroll fix, correctness-review fixes.
  - `09a0d17`: gate repairs.

**Profile — how the sales corridor differs from the factory gate:**
- **Copy:** Hebrew-first by Tom's exception. Copy is checked against the approved register (`_lib/labels.ts`, tranche 185, B-FLOW-04), not against English-first.
- **Roles:** manager (`planner`) and rep (`sales_rep`).
- **Widths:** 320, 390 and 430 (mobile first), plus 1280.
- **Modes:** light, dark (the user preference `html.dark`) and reduced motion.
- **Fixture:** synthetic data with deliberately long values (email, campaign, org name), not role-scoped.
- **Not re-reported:** the capture artifacts already dispositioned in the Unit A gate.

**Evidence:**
- 96 viewport shots covering 72 states, with measurements: 0 page overflow, 0 lead-card overflow, 0 text under 12px.
- Keyboard and focus were probed in Chromium 1194.
- Shots are in `/tmp/claude-0/uxgate/` in the session container; the measurements are summarised here.

## Ranked findings and dispositions

| # | ID | Sev | Eff | Lens | Finding | Disposition |
|---|---|---|---|---|---|---|
| 1 | FLOW-002 | P1 | S | Flow | On the lead card, note and next touch sat below the details, two scrolls down at 390 | **Fixed** `09a0d17`: actions above details. Shot re-checked |
| 2 | INTER-001 | P1 | S | Interaction | An in-flight save looked identical to a disabled button | **Fixed** `09a0d17`: `aria-busy` plus a turning ring, less fade |
| 3 | VISUAL-002 | P1 | S | Visual | A long org name made a 9-line row in the desktop leads table | **Fixed** `09a0d17`: two-line clamp, full value in `title` |
| 4 | FLOW-001 | P1 | S | Flow | The flow counts all open leads; the queue below shows today's work. Nothing says so | **HOLD — copy**: needs a Tom-approved label |
| 5 | FLOW-003 | P1 | S | Flow | A saved note's only signal is the field clearing | **HOLD — copy**: needs a Tom-approved "saved" string |
| 6 | VISUAL-001 | P1 | M | Visual | leads, attention, orgs and settings have not received the D1 treatment, so there are two quality tiers | **Next tranche**: corridor-wide D1 pass |
| 7 | INTER-002 | P1 | S | Interaction | The quick-add FAB covers mid-list cards while scrolling | **Deferred**: present before D1, in `SalesShell` (outside this tranche); the Unit A gate measured no overlap at scroll end |
| — | Correctness review | — | S | — | Stale date overnight; hover lift never applied; sticky-save fade lost | **Fixed** `ea39d8f` |
| — | Tom report | P1 | S | Flow/Visual | Lead card scrolled sideways on long values (655px in a 320–430 panel) | **Fixed** `ea39d8f`, with a red→green regression e2e at 320/390/430 |
| 8 | INTER-003 | P2 | S | Interaction | Glass close button had no hover state | Fixed |
| 9 | INTER-005 | P2 | S | Interaction | Up to ~920ms before the 7th card was tappable | Fixed: 480ms, stagger capped at 200ms |
| 10 | A11Y-001 | P2 | S | A11y | Tab transitions ran under reduced motion | Fixed |
| 11 | A11Y-003 | P2 | S | A11y | Timeline focus ring was not the accent colour | Fixed |
| 12 | COPY-001 | P2 | S | Copy/A11y | Screen readers could read an intermediate count-up value | Fixed: AT reads the settled value only |
| 13 | FLOW-004 | P2 | S | Flow | Team triage counts sit under a manager's "mine" scope with no label | HOLD — copy |
| 14 | VISUAL-005 | P2 | M | Visual | Attention feed is a flat list at desktop | Next tranche |
| 15 | A11Y-002 | P2 | M | A11y | A live count change is not announced | Deferred; counts are readable on demand |
| 16 | COPY-002 | P2 | S | Copy | Loading orbs have no text for AT | Deferred: needs a string |
| 17 | VISUAL-004 | P2 | S | Visual | One flow label wraps to two lines at 320 | Accepted |
| — | VISUAL-003 | P2 | S | Visual | Clamp long values in the lead card details | **Rejected**: the details panel is where the full value is read |
| — | INTER-004 | P2 | S | Interaction | The icon nudge moves the "wrong" way in RTL | **Rejected**: in RTL, forward is physical left; `-3px` is correct |

## Per-dimension status

| Lens | P0 | Open P1 | Status |
|---|---|---|---|
| Flow | 0 | 2 (copy HOLD) | AMBER |
| Interaction | 0 | 1 (deferred, existed before D1) | GREEN after fixes |
| Visual | 0 | 1 (next tranche) | AMBER |
| Copy | 0 | 0 | GREEN |
| Accessibility | 0 | 0 | GREEN |

## Checks on `09a0d17`

- Vitest 1559/1559.
- Typecheck, lint and build all exit 0.
- Mocked sales e2e: 56 pass. The 4 failures are the known local Chromium-1194 `tel:` artifact; they pass in CI on 1217.
- No new Hebrew string. No backend change. No flag.
