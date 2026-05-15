# UX Release Gate — `/me/activity`

**Date:** 2026-05-14
**Scope:** `/me/activity` (post-polish state, commit `3a19c5d` on `feat/my-activity-log`)
**Trigger:** `/ux-release-gate` invoked by Tom after the 4-agent polish pass

---

## Verdict

**HOLD — 3 P0 findings**

Zero-P0 threshold not met. Three release-blocking issues remain after the polish pass — all small in fix size, all citing locked portal standards or WCAG AA.

---

## P0 findings (block ship)

| ID | Dimension | File:line | Issue | Fix |
|---|---|---|---|---|
| **P0-1** | A11Y / Flow / Interaction (3 agents converged) | `ActivityDrawer.tsx:84` | `aria-hidden` on the backdrop `<div>` wrapper hides the dialog and all its interactive children from screen readers (WCAG 2.1.2 / 4.1.2). Polish pass introduced this attribute to mark the overlay decorative — but the dialog is a child of that overlay, so the entire panel becomes invisible to AT. | Remove `aria-hidden` from the backdrop div. `role="dialog" aria-modal="true"` on the inner panel already informs AT to ignore content behind. |
| **P0-2** | Copy | `ActivityDrawer.tsx:159` | Section header reads **"Payload"** in operator-facing drawer. `portal_ux_standard.md:44` explicitly forbids handler / mutation language including the word `payload` in primary UI. | Rename to a plain-English equivalent. Recommended: **"Submitted data"** (forms) or **"Form data"**. |
| **P0-3** | Copy | `ActivityDrawer.tsx:160-167` | Raw `JSON.stringify` of the row's data rendered inside a `<pre>` in operator UI with no "developer / system internals" segregation. `portal_ux_standard.md:41` forbids raw JSON dump in primary UI; `:50` allows it only behind explicit dev-surface labeling. | Wrap the `<pre>` in a `<details>` disclosure titled **"Developer detail (read-only)"** or visually segregate the block on `bg-bg-deep` with an explicit `Internal reference` label per §1 allowance. |

---

## P1 findings (conditional ship items)

| ID | Dimension | File:line | Issue | Fix |
|---|---|---|---|---|
| P1-1 | Copy | `ActivityDrawer.tsx:198` | Drawer Source field uses raw enum `replace(/_/g, " ")` → `form submission`, `credit decision`, `exception acknowledge` — inconsistent with FilterBar labels (`Forms`, `Credit decisions`, `Inbox acknowledged`). | Reuse FilterBar `SOURCE_OPTIONS` label map. |
| P1-2 | Copy | `ActivityDrawer.tsx:200` | Drawer Action field uses raw `action_kind` enum without display map; may produce technical fragments operators cannot interpret. | Add an `ACTION_LABELS` map or omit the field from operator view (segregate with §1 admin allowance). |
| P1-3 | Copy / Flow | `ActivityDrawer.tsx:150` | Cross-link `l.kind` rendered lowercase from underscore-swap (`goods receipt`). | Apply same `statusLabel` capitalization OR provide a kind→label map. |
| P1-4 | Visual | `DayHeader.tsx:47` | Count chip uses `bg-bg-subtle` without `border`, breaking the chip pattern (border + bg) used by status pills and FilterBar pills. | Add `border border-border` to the chip class. |
| P1-5 | Interaction | `ActivityDrawer.tsx:78-85` cross-links | Cross-links are not clickable — flow gap to linked entity. | Map `kind` → portal route and render as `<a>`; ARCH_REQUIRED if `cross_links` contract lacks a URL/route hint. |
| P1-6 | A11Y | `ActivityDrawer.tsx:122` | `aria-live` region rendered conditionally on `detail.data`; `aria-busy` flips false→true→false; completion-of-load may not announce. | Render live-region wrapper unconditionally; include a hidden completion phrase that changes on resolve. |
| P1-7 | A11Y | `ActivityRow.tsx` | Forwarded `ref` is defined but never threaded from the parent `page.tsx` to the row button — dead prop. Focus return still works via `e.currentTarget` capture; this is cleanup, not a behavioural defect. | Either remove `forwardRef` wrapper or thread the ref from a parent ref-array. |

---

## Per-dimension status

| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 1 (shared with A11Y/Inter) | 1 | RED |
| Interaction | 0 (shared with A11Y) | 2 | AMBER |
| Visual | 0 | 1 | AMBER |
| Copy | 2 | 3 | RED |
| Accessibility | 1 | 2 | RED |

> The A11Y / Flow / Interaction P0 are the **same root issue** (`aria-hidden` on backdrop), counted once per dimension that flagged it. The unique P0 set is **3**: one a11y/structural bug + two copy-standard violations.

---

## `portal_ux_standard.md` compliance

| Rule | Status |
|---|---|
| Plain operational English (§1 Tone) | ⚠ `Payload` violates |
| Forbidden in primary UI (§1) — `JSON.stringify` raw dump | ⚠ violated at `ActivityDrawer.tsx:168` |
| Forbidden in primary UI (§1) — handler/mutation language (`payload`) | ⚠ violated at `ActivityDrawer.tsx:159` |
| Admin/dev raw surfaces require visual segregation + label (§1 Allowed-with-conditions) | ⚠ not applied to the JSON block |

---

## Verdict

**HOLD**

Three P0 issues — all small fix size, two cite locked authority docs (`portal_ux_standard.md`), one is a WCAG AA blocker. No path to SHIP or CONDITIONAL_SHIP until the three P0s are closed.

---

## Required for SHIP

1. **Remove `aria-hidden`** from the drawer backdrop wrapper in `ActivityDrawer.tsx:84`.
2. **Rename `Payload` → `Submitted data`** (or another plain-English equivalent) in `ActivityDrawer.tsx:159`.
3. **Segregate the raw JSON block** behind a `<details>` disclosure or visually-segregated `bg-bg-deep` section labeled `Developer detail (read-only)` per `portal_ux_standard.md` §1 admin/dev allowance.

After the three fixes, re-run `/ux-release-gate` to confirm zero P0 and capture the gate signature.

---

## Tom approval required?

**Yes** — copy decisions (P0-2, P0-3) need a Tom sign-off on the proposed strings before they land. The aria-hidden fix (P0-1) is mechanical and does not require approval.

---

## Next action for Tom

Pick a path:

- **A (fastest to SHIP):** approve the proposed strings — "Submitted data" for the section header, "Developer detail (read-only)" for the disclosure label — and let the executor land all three P0 fixes in one commit on `feat/my-activity-log`. Re-run gate. Then merge.
- **B (split):** land P0-1 (a11y) immediately as an isolated fix, defer the two copy P0s for a separate copy-only commit after Tom proposes alternative strings.

Recommended: **A**, because the polish branch is already a self-contained UX pass; bundling the three fixes keeps the commit history coherent and produces one re-gate pass.

---

## Files referenced

- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(ops)\me\activity\page.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(ops)\me\activity\_components\ActivityDrawer.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(ops)\me\activity\_components\ActivityRow.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(ops)\me\activity\_components\FilterBar.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(ops)\me\activity\_components\DayHeader.tsx`
- `C:\Users\tomw2\Projects\window2-portal-sandbox\docs\portal_ux_standard.md` (authority — §1)
