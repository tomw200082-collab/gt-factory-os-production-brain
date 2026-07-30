# UX release gate — `/purchase-orders/placement-queue` (Dorin's PO execution page) — 2026-07-30

**Trigger:** Tom (2026-07-30, in writing): "the procurement timing logic is relatively good, but the page
is not understandable and not clear enough to use. Must improve both the visual design and the user
experience." Full gate, all five UX agents.
**Prior gates on this corridor:** `UX-RELEASE-GATE-procurement-corridor-2026-07-16.md` (HOLD),
`UX-RELEASE-GATE-procurement-corridor-deepen-2026-07-21.md` (HOLD — P0 on `/planning/procurement`),
`DR-018-ux-release-gate-thursday-corridor-2026-07-03.md`.
**Tranches absorbed by this surface since:** 086 (place), 130 (discard+reason), 140 (switch supplier /
click-to-call), 0261 (confirmed ETA), **150 (partial placement — new since the last gate)**.
**Mode:** read-only; render-grade. Auth via sanctioned dev-shim; no `X-Fake-Session` / `X-Test-Session`.

## Scope

- `/purchase-orders/placement-queue` — `page.tsx` (433), `_components/PlacementRow.tsx` (1233),
  `_lib/api.ts` (422), nav manifest entry, `(po)/layout.tsx`.
- Persona: Dorin, office manager / bookkeeper. **Role = planner** (locked: Tom Option A, 2026-07-16,
  FLOW-8 closure — no separate bookkeeper role in the lattice). Hebrew + `dir="rtl"` authorized
  (portal CLAUDE.md, Tom 2026-06-20) — Hebrew is ⊥ (not a finding) on this surface.

## Visual evidence (committed)

`docs/phase8/dry-runs/assets/uxg-2026-07-30/`:
- `purchase-orders-placement-queue-planner-desktop.png` (1440×900, populated 5-PO fixture:
  1 overdue / 1 today / 1 needs-schedule / 2 next-7-days; two schedule panels auto-open)
- `purchase-orders-placement-queue-planner-mobile.png` (390×844, same fixture)
- `purchase-orders-placement-queue-viewer-{desktop,mobile}.png` (RoleGate wall — correct steady-state
  under Option A)
- `fx-placement-queue.json` (the `UX_SHOT_FIXTURE` used)

Shot paths below abbreviate to `shot:planner-desktop` / `shot:planner-mobile`.

## Governor verification notes (P0 adjudication)

1. **VIS-101 CONFIRMED P0.** Supplier name renders twice per row at near-identical weight:
   group `<h2 className="text-sm font-semibold text-fg">` (`page.tsx:385`) and the row header
   `text-sm font-semibold text-fg-strong` (`PlacementRow.tsx:520-521`), ~8-12px apart, on every
   group. Shot-confirmed on all 5 groups. The supplier-group → PO-work-item hierarchy is illegible;
   this is the single most visible cause of Tom's "not understandable."
2. **COPY-101 DOWNGRADED P0→P2 (governor, backend-verified).** The copy auditor claimed the split-PO
   success banner shows a raw UUID (`page.tsx:155` renders `{placed.split_po_id}`). Backend check
   refutes the P0: migration `0298_partial_placement_split.sql` mints the sibling with
   `v_sibling_po_id := private_core.fn_allocate_po_number(v_year)` and inserts it as **both**
   `po_id` and `po_number`; `0049_purchase_orders.sql` locks "po_number — UNIQUE human-facing, v1
   identical to po_id". Dorin therefore sees a friendly PO number today. Residual (P2): the portal
   silently depends on the v1 `po_id == po_number` identity — make the contract explicit
   (add `split_po_number` to `PlaceResult`) or display a static label. Merged: FLOW-113.

## Regression rollup — prior findings on this surface

Verified CLOSED and holding (all five agents cross-checked, no regressions): FLOW-001, FLOW-005,
FLOW-011, INTER-002 (`ApiError` guard), INTER-003, INTER-005, FLOW-105, INT-102, INT-103, A11Y-103
(2026-07-21), DR-019 P0 (confirm itemises split), 2026-07-21 VIS-206 (sort select no longer clips).
Still open from prior gates: 2026-07-21 COPY-205 (→ carried here as COPY-111/P2), 2026-07-21 VIS-101
partial (cancel label `hidden sm:inline` — icon-only at 390px; carried into A11Y-108/USBL-101).

## Dedupe map (cross-dimension merges → one canonical row each)

| Canonical | Merged duplicates | Note |
|---|---|---|
| VIS-108 | FLOW-114, INTER-109, USBL-104, COPY-113 | "התחל עבודה מול הספק · N" accent pill — non-interactive CTA-styled span; 5 dimensions flagged it independently |
| FLOW-112 | USBL-102 | collapsed row gives no action orientation / no expand affordance |
| FLOW-111 | COPY-112 | scope-tab semantics invisible before selection |
| COPY-111 | INTER-107, prior COPY-205 | confirm overstates irreversibility |
| COPY-101 (↓P2) | FLOW-113 | split-PO id contract explicitness (see adjudication #2) |

Canonical totals: **1 P0 · 32 P1 · 12 P2**.

## Top-ranked actions (the deliverable — one list, all dimensions; sev first, then ascending effort)

| # | Sev | Effort | Dimension | Finding | Proposed fix | Evidence |
|---|-----|--------|-----------|---------|--------------|----------|
| 1 | **P0** | S | Visual | VIS-101 — supplier name printed twice per row at identical weight; group-vs-row hierarchy collapses; page reads as duplicated rows | Remove `supplier_name` from the collapsed row header inside supplier groups; row leads with PO number + amount + status chip; group `<h2>` owns supplier identity (pair with VIS-106 eyebrow rule) | `page.tsx:385`, `PlacementRow.tsx:520-521`, shot:planner-desktop |
| 2 | P1 | S | Flow | FLOW-112 (+USBL-102) — collapsed row offers three equal-weight buttons with zero orientation; a needs-schedule row looks identical to a ready-to-place row; users discover the prerequisite only after entering data | State-dependent inline hint next to the actions: "← נדרש תזמון" on needs-schedule rows; "פתחי להזנת מחיר ותנאים" on ready rows | `PlacementRow.tsx:519-552,241-246` |
| 3 | P1 | S | Flow | FLOW-111 (+COPY-112) — "עכשיו" definition sits *after* the tabs in muted text-xs; with only future orders the default tab shows 0 rows → false "nothing to do" | Move scope semantics above/into the tabs (or `title` per tab); helper copy for "7 ימים" and "הכול" | `page.tsx:280-307` |
| 4 | P1 | S | Visual | VIS-102 — native date inputs render `mm/dd/yyyy` / `07/30/2026` (US) inside the Hebrew page; no `lang` on the RTL root | Add `lang="he"` to the `dir="rtl"` root div — all descendant date inputs flip to DD/MM/YYYY | `page.tsx:111`, `PlacementRow.tsx:613,629`, shot:planner-desktop |
| 5 | P1 | S | Copy | COPY-103 — displayed dates are ISO `YYYY-MM-DD`; ambiguous for a bookkeeper reading RTL; Israeli convention is DD/MM/YYYY | `formatIsraeliDate()` at the 5 render sites | `PlacementRow.tsx:536,540,545,462,664` |
| 6 | P1 | S | Interaction | INTER-102 — "שמור מועד" succeeds silently; indistinguishable from "חזרה" (discard) | Toast "מועד עודכן" on `onSuccess` per §9 | `PlacementRow.tsx:206-213` |
| 7 | P1 | S | Interaction | INTER-104 — schedule submit stays enabled when the required risk note is empty; validation fires post-click, contradicting the page's own preemptive-disable pattern | Extend `disabled` + tooltip to cover `scheduleDateAfterSafe && !scheduleNote.trim()` | `PlacementRow.tsx:726,192-195` |
| 8 | P1 | S | Interaction | INTER-103 — place-order confirm names the PO number but not the supplier — a terminal money action | Add `po.supplier_name` to the confirm title | `PlacementRow.tsx:457-460` |
| 9 | P1 | S | Interaction | INTER-105 — "שנה מועד" / cancel toggles not locked while placement is in flight | `disabled={placeMut.isPending}` on both (pattern already on supply toggles) | `PlacementRow.tsx:555-592` vs `:968` |
| 10 | P1 | S | Visual | VIS-108 (merged ×5) — "התחל עבודה מול הספק · N" is a non-interactive span in full CTA styling; every dimension flagged the false affordance | Remove the pill (count already in sub-label); rule: accent pill styling = interactive only | `page.tsx:390-392`, shot:planner-desktop |
| 11 | P1 | S | Copy | COPY-102/104/106/107 — schedule-panel jargon batch: "מידע נעול מהשרת", "הגעה מתוכננת פנימית", "סיבת סיכון", "סיבת חריגה מתאריך בטוח" — planner/dev vocabulary at the highest-stress moment | Plain-Hebrew rewrite (exact strings in the copy packet): "מועד אחרון לפי תכנון:", "הגעה צפויה (לפי תכנון)", "מדוע מבצעים אחרי המועד האחרון?", "הסבר לביצוע מאוחר (חובה)" | `PlacementRow.tsx:661,626,670,688` |
| 12 | P1 | S | Copy | COPY-105 — supply toggle "לא הוזמן" contradicts its own frame "מה סופק" (the order WAS placed) | Rename to "לא יסופק" (+ alert copy at `:1017,1090`) | `PlacementRow.tsx:957` |
| 13 | P1 | S | Copy | COPY-108 — UOM leaks English ("KG", "L") into Hebrew lines and confirm text | UOM display map (ק"ג / ל' / ג' / מ"ל / יח') at all render sites | `PlacementRow.tsx:921,1005,330-332` |
| 14 | P1 | S | Copy | COPY-109 — `lineName()` falls back to internal IDs in confirm-dialog text when names are null (carried from DR-018 COPY-008) | Drop `component_id`/`item_id` from the display chain | `PlacementRow.tsx:88-89` |
| 15 | P1 | S | Visual | VIS-103 — scope tabs use `btn-primary` for selection; design system has `.segmented` for exactly this | Replace with `.segmented` / `.segmented-option` (globals.css:893-927) | `page.tsx:283-303`, shot:planner-desktop |
| 16 | P1 | S | Visual | VIS-109 — schedule panels auto-expand on mount; on mobile two open panels push rows 3-5 below the fold — queue can't be scanned | No auto-expand in list context; urgency chip on the collapsed header instead (see also INTER-106) | `PlacementRow.tsx:227-229`, shot:planner-mobile |
| 17 | P1 | S | Visual | VIS-106 — group `<h2>` and row header share size/weight; hierarchy rests on background alone | Group headings → `.eyebrow` scale; 3-step ladder: eyebrow group → semibold PO → xs-muted meta | `page.tsx:385-391` |
| 18 | P1 | S | A11y | A11Y-101 — disabled "בצע הזמנה" hides its blocked reason in a `title` on a non-focusable element; keyboard/SR users can't learn what's missing | `aria-disabled` + click-guard + `blockedReason` as adjacent visible text | `PlacementRow.tsx:1213-1215` |
| 19 | P1 | S | A11y | USBL-103 — `required` on price/ETA/terms drives no visible marker; users discover requirements by trial | "(חובה)" on the three labels | `PlacementRow.tsx:926-928,1128-1131,1148-1150` |
| 20 | P1 | S | A11y | A11Y-103 — partial-qty error text not associated (`aria-describedby` missing) | Stable error `id` + `aria-describedby` when invalid | `PlacementRow.tsx:1002-1019` |
| 21 | P1 | S | A11y | A11Y-104 — lines skeleton `aria-busy` on a bare div announces nothing | `role="status"` + sr-only "טוען שורות הזמנה…" | `PlacementRow.tsx:839-846` |
| 22 | P1 | M | Flow | FLOW-110 — supplier grouping fragments urgency order; most-overdue and second-most-overdue sit in different sections. **Counter-view (interaction agent): grouping enables one-call-per-supplier batching — genuinely good.** → **Tom decision** (see below) | Option: flat urgency list when sort=date (supplier as inline label), grouping as opt-in; or keep grouping but order groups by most-urgent member with an urgency strip | `page.tsx:70-90,376-419` |
| 23 | P1 | M | Interaction | INTER-101 — the paste-ready order document (the call opener) renders *below* the price inputs (the call's answers); sequence inverted vs a real supplier call | Move `order_document_text` block above the lines list | `PlacementRow.tsx:871-1123` |
| 24 | P1 | M | Interaction | INTER-106 — after saving a schedule the panel closes with no bridge to the pricing step | `setOpen(true)` on schedule success, or a next-step hint | `PlacementRow.tsx:206-213,227-229` |
| 25 | P1 | M | Visual | VIS-104 — six data points concatenated by `·` at uniform weight; urgency buried mid-string | Three-zone row: status chip (RTL start) / PO+amount mono / dates | `PlacementRow.tsx:523-547`, shot:planner-desktop |
| 26 | P1 | M | Visual | VIS-105 — schedule form mixes preset buttons and fields in one flex-wrap; no field↔preset grouping in RTL | Two labeled fieldsets (order date / arrival date), presets co-located with their field | `PlacementRow.tsx:600-656`, shot:planner-desktop+mobile |
| 27 | P1 | M | A11y | A11Y-102 — supply-state trio announced as independent toggles (`aria-pressed`), not a mutually-exclusive choice | `role="radiogroup"` + `role="radio"` + `aria-checked` | `PlacementRow.tsx:950-983` |
| 28 | P1 | M | A11y | A11Y-105 — RTL tab order lands on secondary "חזרה" before the primary action in both panel footers | Primary first in DOM (review safe-first intent with interaction) | `PlacementRow.tsx:712-734,803-833` |
| 29 | P1 | M | A11y | USBL-101 — expand / schedule / cancel presented as equal peers; destructive path undifferentiated | Danger-tone or overflow placement for the cancel trigger | shot:planner-desktop, `PlacementRow.tsx:555-592` |
| 30 | P1 | S* | Copy | COPY-110 — cancel-reason catalogues diverge between PlacementRow and FocusCard; incoherent audit vocabulary (*S after **Tom decision** on the shared set) | Shared `CANCEL_REASONS` const; Tom picks per-role subset | `PlacementRow.tsx:39-45` vs `FocusCard.tsx:60-65` |
| 31 | P1 | S | Flow | FLOW-116 — supplier-confirmed ETA pre-filled from planner estimate; the forcing function ("confirm with the supplier") is bypassed silently | Sub-label naming the pre-fill source + prompt to update per supplier confirmation | `PlacementRow.tsx:222-224,1125-1143` |

### P2 (audit trail — fix opportunistically)

| ID | Dimension | Finding | Evidence |
|---|---|---|---|
| COPY-101↓ | Copy/Flow | Make `split_po_id`/`po_number` identity explicit in `PlaceResult` (add `split_po_number`) or show a static label — robustness, not a live defect | `page.tsx:148-158`, `api.ts:117-124`, backend 0298 |
| COPY-111 | Copy | Confirm claims placed orders can't be cancelled — false (OPEN cancel exists); carried P2 since 2026-07-21 | `PlacementRow.tsx:460-463` |
| COPY-114 | Copy | "דורש תזמון" → "חסר תאריך ביצוע" | `PlacementRow.tsx:95` |
| FLOW-115 | Flow | Scope-tab counts stay full-queue while a supplier filter is active | `page.tsx:283-304` |
| INTER-108 | Interaction | No `<form>` wrapper — Enter never submits; expert path missing | `PlacementRow.tsx:838` |
| VIS-107 | Visual | Two stacked bordered control bars; should be one `.filter-bar-sticky` | `page.tsx:279-353` |
| VIS-110 | Visual | Overdue banner uses danger tokens (= system error); business urgency should use warning tokens | `page.tsx:267-277` |
| A11Y-106 | A11y | "אין טלפון" at `--fg-subtle` = 3.09:1 (WCAG 1.4.3 fail); token ladder audit is L, spot fix S | `SupplierCallLink.tsx:42`, `globals.css:67-68` |
| A11Y-107 | A11y | Pending spinners aria-hidden with no sr-only "מבצע…" | `PlacementRow.tsx:729-730,1219-1224` |
| A11Y-108 | A11y | Icon-only cancel at 390px ~40px wide (< 44px target) | `PlacementRow.tsx:583`, shot:planner-mobile |
| A11Y-109 | A11y | `aria-expanded` without `aria-controls`/panel id | `PlacementRow.tsx:515-516,838` |

## P0 findings (all dimensions) — block ship

| ID | Dimension | Route | Description |
|---|---|---|---|
| VIS-101 | Visual | /purchase-orders/placement-queue | Supplier name printed twice per row (group `<h2>` + row header) at near-identical `text-sm font-semibold` weight — the page's two-level hierarchy is unreadable; primary confirmed cause of Tom's "not understandable" |

## Per-dimension status

| Dimension | P0 | P1 | P2 | Status |
|---|---|---|---|---|
| Flow | 0 | 4 | 2 | AMBER |
| Interaction | 0 | 6 | 1 | AMBER |
| Visual | 1 | 7 | 2 | RED |
| Copy | 0 | 9 | 3 | AMBER |
| Accessibility | 0 | 7 | 4 | AMBER |
| **Canonical total** | **1** | **32** | **12** | |

## portal_ux_standard.md compliance

**PASS with noted violations** (post-governor-verification):
- §1 forbidden patterns: PASS — the claimed raw-ID exposure (COPY-101) is refuted by backend evidence;
  no raw enums / API paths / HTTP codes reach the operator (`ApiError` guard holding).
- §6 plain copy: VIOLATION — "מידע נעול מהשרת" (COPY-102, P1 #11).
- §7 mobile: partial — icon-only cancel at 390px (accepted-partial since 2026-07-21; now A11Y-108).
- §3 state hygiene, §4 status semantics, §8 button naming, §9 banners: PASS.

## Verdict

**HOLD**

## Blockers (HOLD)

1. **VIS-101** — `page.tsx:385` + `PlacementRow.tsx:520-521`. Fix: drop `supplier_name` from the row
   header inside supplier groups; row leads with PO number + amount + status chip; group heading moves
   to eyebrow scale (VIS-106). Effort S. This single fix changes what every row on the page reads like.

Practical note: the blocker is S-effort. A tranche bundling #1 with ranked items #2–#21 (all S) is
one focused work batch and would flip Visual RED→GREEN and resolve the bulk of Tom's complaint.

## Conditions

n/a (HOLD, not CONDITIONAL_SHIP).

## Tom approval required?

**yes** —
1. HOLD acknowledgment + authorization of a fix tranche (suggest: tranche 154, manifest = the four
   placement-queue files + tests; no backend, no tokens).
2. **Design decision FLOW-110 (#22):** flat urgency-first list vs supplier grouping. The flow agent
   found grouping fights triage; the interaction agent found grouping enables one-call-per-supplier
   batching. Governor recommendation: keep supplier grouping, order groups by their most-urgent
   member, and rely on the #25 status chips for in-group urgency — revisit flat list only if Dorin
   still struggles.
3. **COPY-110 (#30):** pick the shared cancel-reason catalogue (per-role subset).

## Next action for Tom

Reply "מאשר טראנץ' 154" (approve fix tranche) — I will draft the tranche manifest from ranked items
#1–#21 (all S-effort, portal-only, four files) and route it through `/portal-tranche-plan` for
execution; decisions on #22 (grouping) and #30 (reason catalogue) can ride along or wait.

---

# Addendum — tranche 154 executed (same day)

Tom approved the fix tranche in-session ("מאשר טראנץ' 154") and agreed with the governor
recommendations on the two open design questions. Implemented in
`gt-factory-os-portal` PR **#198** (branch `claude/procurement-execution-ux-x3p14w`); manifest at
`docs/portal-os/tranches/154-placement-queue-clarity.md`.

## Verdict movement

**HOLD → cleared pending merge.** The single P0 (VIS-101) is fixed, plus 31 of 32 P1 and 9 of 12 P2.

| Dimension | P0 before | P0 after | P1 before | P1 after |
|---|---|---|---|---|
| Flow | 0 | 0 | 4 | 0 |
| Interaction | 0 | 0 | 6 | 0 |
| Visual | 1 | **0** | 7 | 0 |
| Copy | 0 | 0 | 9 | 1 (COPY-110) |
| Accessibility | 0 | 0 | 7 | 0 |

Deliberately not closed, with reasons:
- **COPY-110** (shared cancel-reason catalogue) — still blocked on Tom picking the per-role subset.
  Not invented.
- **INTER-108** (`<form>` wrapper for Enter-to-submit) — deferred; interacts with the confirm-dialog
  flow and is a P2 convenience.
- **A11Y-106** (`--fg-subtle` at 3.09:1) — token-level, and tokens are frozen. Needs its own tranche.

## Design decisions taken (Tom-delegated, governor-recommended)

1. **FLOW-110 grouping** — supplier grouping kept; groups ordered by their most urgent member, with
   that state on the group header. Both auditors' concerns satisfied without a flat list.
2. **Hierarchy by promotion, not demotion** — the gate proposed shrinking the group heading to
   `.eyebrow`. Since the supplier name now appears exactly once, it is the call target and stays
   prominent; the *row* was demoted instead (status chip + mono PO number). Same ladder, correct
   direction.
3. **A11Y-105 split** — primary-first DOM order applied to the schedule footer, deliberately **not**
   to the cancel footer: landing on "חזרה" first before a destructive action is the guard.

## Correction to a gate finding

**VIS-102 was right about the defect and wrong about the fix.** The proposed `lang="he"` on the RTL
root does not make `<input type="date">` render DD/MM/YYYY — Chromium formats date inputs from the
**browser's** locale and ignores the document language. Verified against a render: the widget still
showed `08/09/2026` for the 9th of August. `lang="he"` stays (correct for other reasons), and the
guarantee now comes from a `DateEcho` printing the Israeli format beside every date input.
Recorded so the next gate does not re-propose the same non-fix.

## Evidence

`assets/uxg-2026-07-30/after/`:
- `purchase-orders-placement-queue-planner-desktop.png` / `-mobile.png` — same fixture, same
  viewports as the before-shots one directory up. Mobile now shows all five orders in the first
  viewport; previously two auto-opened panels pushed rows 3–5 below the fold.
- `expanded-desktop.png` — the expanded row as a numbered call script (1 · send the order,
  2 · record what the supplier confirmed, then arrival date and payment terms).
- `expanded-split-desktop.png` — partial-supply state with the split panel and the per-line
  validation message.
- `schedule-desktop.png` — the schedule panel as two labelled fieldsets, with the date echo visible
  beside the native widget.

Rail placement and tone verified by pixel probe rather than by eye: danger `rgb(193,105,98)`,
warning `rgb(209,154,90)`, accent `rgb(99,132,135)` at the row's inline-start (right) edge.

## Verification

`tsc --noEmit` 0 · `eslint` 0 · `vitest` **1130/1130** · `playwright --grep @mocked` **56/56**.
New unit cases pin the behaviours that changed: supplier name absent from the collapsed row, no
auto-open, schedule blocked before the click while a required late-reason is empty, native
radiogroup semantics, Israeli date rendering, and the `aria-disabled` click guard.

## Next action for Tom

Review and merge `gt-factory-os-portal#198` once its checks are green. Two decisions still open and
unblocked by this work: the shared cancel-reason catalogue (COPY-110), and whether the
`--fg-subtle` contrast fix warrants its own token tranche (A11Y-106).

---

**Gate run:** 2026-07-30, session `claude/procurement-execution-ux-x3p14w`.
**Agents:** ux-flow-architect, interaction-design-specialist, visual-system-designer,
ux-content-state-designer, accessibility-usability-auditor; verdict by governor pass with two P0
adjudications (1 confirmed, 1 downgraded on backend evidence).
**Write policy:** saved to `PRODUCTION/docs/phase8/dry-runs/` per gate default; copy to
`gt-factory-os-portal/docs/ux/` only after Tom approval.
