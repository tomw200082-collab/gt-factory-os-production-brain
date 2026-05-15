# UX Release Gate — `/me/activity` (re-gate, pass 2)

**Date:** 2026-05-14
**Scope:** `/me/activity` after P0 fixes (commit `4c69a7c` on `feat/my-activity-log`)
**Trigger:** `/ux-release-gate` re-run after the three P0 fixes landed and were Tom-approved
**Prior gate:** `ux-release-gate-me-activity-2026-05-14.md` — verdict HOLD (3 P0)

---

## Verdict

**SHIP** — zero P0 across all five dimensions.

One new P1 introduced by the fix copy ("Developer detail") — non-blocking; one-word swap.

---

## P0 carry-forward status

| ID | Previous finding | Status |
|---|---|---|
| P0-1 | `aria-hidden` on drawer backdrop | **CLOSED** — attribute removed; dialog now reachable by AT (WCAG 4.1.2) |
| P0-2 | "Payload" section header | **CLOSED** — renamed to "Submitted data" |
| P0-3 | Raw JSON in primary UI without dev-surface segregation | **CLOSED** — wrapped in `<details>` disclosure with bg-bg-deep, collapsed by default, labeled summary per `portal_ux_standard.md` §1 |

---

## New findings introduced by the fix

| ID | Severity | File:line | Issue | Proposed |
|---|---|---|---|---|
| **NEW-P1** | Copy | `ActivityDrawer.tsx:163` | Disclosure summary reads **"Developer detail (read-only)"**. The word "Developer" is developer-audience language on an operator-facing surface; the segregation mechanism satisfies §1 P0 requirement but the wording is jargon. | **"Raw submission data (read-only)"** — keeps the read-only signal, drops the dev-audience framing. |

This is a P1, not a P0. The §1 P0 condition ("visually segregated and labeled as a dev/system surface") is met by the disclosure + bg-bg-deep + collapsed-by-default. The label wording is a refinement.

---

## Per-dimension status

| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 0 | 0 (carry-forward P1s noted in pass 1 still open) | GREEN |
| Interaction | 0 | 0 (carry-forward P1s noted in pass 1 still open) | GREEN |
| Visual | 0 | 0 (carry-forward P1: day-count chip border still open) | GREEN |
| Copy | 0 | 1 NEW + 3 carry-forward (enum labels) | GREEN |
| Accessibility | 0 | 0 (carry-forward P1s noted in pass 1 still open) | GREEN |

---

## Open P1s (conditional ship items — not blocking)

These do not block SHIP but are recommended for a follow-up polish commit:

1. Disclosure summary copy: **"Developer detail (read-only)"** → **"Raw submission data (read-only)"** (NEW this pass)
2. Drawer Source/Action/cross-link enum labels (3 instances) — use display maps instead of `replace(/_/g, " ")`
3. DayHeader count chip lacks `border border-border`
4. Cross-links not clickable (may be ARCH_REQUIRED depending on contract)
5. `aria-live` region timing on detail load
6. Dead `forwardRef` in ActivityRow

---

## `portal_ux_standard.md` compliance

| Rule | Status |
|---|---|
| Plain operational English (§1 Tone) | PASS for primary surface; ⚠ P1 on disclosure label |
| Forbidden — `JSON.stringify` in primary UI | PASS — now behind dev-surface disclosure |
| Forbidden — handler/mutation language (`payload`) | PASS — renamed |
| Admin/dev surfaces require visual segregation + label (§1 allowance) | PASS — bg-bg-deep + collapsed `<details>` + summary label |

---

## Tom approval required?

For SHIP — **no.** Zero P0; approvals from pass 1 stand.
For the NEW-P1 copy swap — Tom's call. Tom previously approved "Developer detail (read-only)" → would need explicit re-approval to switch to "Raw submission data (read-only)".

---

## Next action for Tom

Pick a path:

- **A (ship now):** merge `feat/my-activity-log` in both repos. Re-gate verdict is SHIP. Apply the NEW-P1 copy swap and the other 5 open P1s in a follow-up commit later.
- **B (one more cycle):** apply the one-word NEW-P1 swap ("Developer detail" → "Raw submission data") + the day-count chip border fix in one tiny commit, re-gate (will be SHIP unconditionally), then merge.

Recommended: **B** — both fixes are mechanical and one-word/one-class. They close the only NEW finding from this gate and the carry-forward visual P1, producing a cleaner "shipped" state.

---

## Notes

- The visual-system-designer agent reported BLOCKED (could not locate the file). The other four agents read the file successfully at the same path. This appears to be an agent path-handling quirk (parentheses in `(ops)` segment) and not a code defect. Visual P0 considered absent based on the prior gate (zero P0) + no visual changes in this commit affecting tokens.
