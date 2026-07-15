# UX release gate — /admin/decision-board (tranche 128, true-gross-margin rebuild)

Run: 2026-07-15, via `/ux-release-gate` (Tom-directed, this session) against
`gt-factory-os-portal` branch `claude/decision-board-dashboard-i4qxs9` (PR #169).
Render evidence: `tests/e2e/ux-shot.spec.ts` + dev-shim, fixture-stubbed
`/api/unit-economics` (all decision states + stale + anomaly exercised), desktop
1440 + mobile 390 shots, pre- and post-fix. All five UX agents ran read-only.

## Scope

`/admin/decision-board` (page.tsx rebuild + new OperatingCostsDrawer.tsx) — the
CM2 corridor surface (gt-factory-os SPEC.md §T4). English-first route; no Hebrew
labels found (confirmed against the authorized-Hebrew list).

## Verdict history

1. **First pass: HOLD** — 3 × P0 (flow, visual, a11y), 12 × P1, 5 × P2.
2. **Fastfollow applied in-tranche** (precedent: tranches 126/127), commits
   `62529e0`, `e0cdee4`, `7a8652c`.
3. **Re-render + oracles green** → **re-issued verdict: CONDITIONAL_SHIP.**

## P0 findings — all FIXED and re-verified

| ID | Dimension | Finding | Fix (landed) |
|---|---|---|---|
| P0-1 | Flow | Inspector next-move ("Act now"/"Fix price") rendered as a clickable-looking but inert arrow-span — no path to act | Real controls: copy-target-price button (loss/workhorse/drag), Link to `/admin/masters/items/[id]` (needs_data), plain text otherwise |
| P0-2 | Visual | 8-column table horizontally scrolled at 390px (UX standard §7 violation) — margin/target invisible | Mobile keeps Product / Decision / True margin % / Target price (`hidden md:table-cell` on the rest) + name truncation; no horizontal scroll |
| P0-3 | A11y | Drawer `role="dialog" aria-modal` без focus trap or initial focus | Initial focus → close button; Tab cycle trapped in panel; focus restored to trigger on close |

Also fixed while in the file (P1/P2): dirty-close guard + inline discard confirm
(Esc/backdrop), disabled-save `title` tooltip, add-line Discard, "Recalculating…"
indicator (isFetching), `aria-sort`, inspector `aria-live`, anomaly icon
`aria-describedby` (keyboard-reachable text), stale banner icon → AlertTriangle +
single-signal (SourcePill neutral), quadrant target label right-anchored above
halos, "(CM2)" jargon removed outside the rules popover, judge-reason copy in
plain English, "below water" idiom replaced, `cost_key` no longer rendered in the
drawer, odd segment card spans full row on mobile, verdict-band grammar.

## Remaining P1 conditions (next sprint — none block a draft-PR merge decision)

| # | Dimension | Item | Effort |
|---|---|---|---|
| C1 | Interaction | Success confirmation after cost-save (currently only the Recalculating indicator) | S |
| C2 | Flow | Mobile: Inspector below the fold after bubble tap — reorder or `scrollIntoView` | M |
| C3 | Visual | Decision palette hardcodes hex — map to `--decision-*` tokens for dark-mode (needs Tom authorization for new tokens) | M |
| C4 | Interaction | `target_pct` (the one knob) has no edit affordance — product decision: expose in drawer vs admin-only | M |
| C5 | A11y | `prefers-reduced-motion` does not yet gate CSS/SVG transitions (count-ups are gated) | S |

## Per-dimension status (post-fix)

| Dimension | P0 | P1 open | Status |
|---|---|---|---|
| Flow | 0 | 1 (C2) | GREEN |
| Interaction | 0 | 2 (C1, C4) | GREEN |
| Visual | 0 | 1 (C3) | GREEN |
| Copy | 0 | 0 | GREEN |
| Accessibility | 0 | 1 (C5) | GREEN |

## portal_ux_standard.md compliance

PASS post-fix (§7 no-horizontal-scroll, §8 disabled-explains-why, §9 warning-banner
icon all remediated; §9 toast pattern pending as C1).

## Evidence

- tsc 0 · eslint 0 · vitest 886/886 · decision-board e2e 1/1 (tap + keyboard paths)
- Shots: /tmp/ux-shots (pre-fix), /tmp/ux-shots-v2, /tmp/ux-shots-v3 (post-fix mobile)
- Commits: gt-factory-os-portal `4728f20 → 7a8652c` (PR #169)

## Verdict

**CONDITIONAL_SHIP** — zero P0 across all five dimensions after the fastfollow;
five named P1 conditions above.

## Tom approval required?

**Yes** — CONDITIONAL_SHIP always requires Tom approval; C3/C4 additionally need
his product/token decisions. Note: this gate covers UX only. The surface goes
live only after the backend corridor applies (migrations 0282/0283 + API deploy,
gt-factory-os PR #166) — production deploy + prod-DB migration apply remain
deliberate, explicitly-flagged steps per CLAUDE.md.

## Next action for Tom

Approve CONDITIONAL_SHIP (and answer C4: should the margin target be editable
from the board?), then schedule the backend apply sequence.
