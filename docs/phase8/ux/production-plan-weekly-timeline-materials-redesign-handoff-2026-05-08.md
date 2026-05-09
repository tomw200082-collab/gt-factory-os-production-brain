# Production Plan — Weekly Timeline Command Surface + Materials This Week Drawer

## Handoff Packet — Run PDP-UX-01

**Status:** READY_FOR_TOM_REVIEW
**Authored by:** claude-code (single-author, design-quality lens via `frontend-design` skill)
**Date:** 2026-05-08
**Run ID:** PDP-UX-01
**Portal tip at audit:** `02266b8` (window2-portal-sandbox main)
**Authority hierarchy:** `CLAUDE.md` > `EXECUTION_POLICY.md` > `CURRENT_STATE.md` > `planning-ux-full-pass-handoff-2026-05-08.md` (universal rules U1–U7) > this packet
**Supersedes:** Section S10 (`/planning/production-plan` light-touch instruction) of `planning-ux-full-pass-handoff-2026-05-08.md` only. All other sections of that packet remain authoritative.
**Design-quality lens:** `frontend-design` skill loaded as a craft reference for this packet (premium, distinctive, non-generic industrial-operations aesthetic).

---

## § 0 — Tom decision recap (just confirmed before authoring)

| # | Decision | Reflected in packet |
|---|---|---|
| 1 | Supersede only S10 of existing planning-ux-full-pass packet | Header + § 1 |
| 2 | Materials drawer backend dependency declared in packet, contract deferred to W4 (not authored here) | § 4, § 12 |
| 3 | Visual redesign + drawer trigger + 'Backend pending' shell shippable immediately | § 11, § 12 |
| 4 | Use `frontend-design` skill as craft lens for visual quality | § 4a (Frontend Design Craft Requirements) |
| 5 | § 12 must NOT lock backend contract — UX needs only, illustrative shape | § 12 rewritten as non-authoritative |
| 6 | Drawer trigger label: "Materials this week" (not "Weekly materials") | § 3, § 4 |
| 7 | Dot-grid background must be removed or near-zero opacity behind board | § 5, § 4a |
| 8 | Bar for "implementation complete" is visual outcome, not component existence | § 11, § 14 |

---

## § 1 — Current screen audit (live screenshot, portal tip `02266b8`)

Tagging: `VISUAL-PDP-NNN` (visual-system-designer domain), `FLOW-PDP-NNN` (ux-flow-architect domain), `INTER-PDP-NNN` (interaction-design-specialist domain), `A11Y-PDP-NNN` (accessibility-usability-auditor domain), `COPY-PDP-NNN` (ux-content-state-designer domain).

### Visual hierarchy failures
- **VISUAL-PDP-001** — KPI band (Planned/Completed/Total/Done%) and the day-card grid compete for visual primacy. Neither dominates. The eye has nowhere to land first. KPI cards read as labels of equal weight to the production cards beneath them.
- **VISUAL-PDP-002** — The dot-grid background pattern is visible at full intensity behind the entire board. It adds texture noise, weakens the calm operational feel, and makes the day-card surfaces feel less raised.
- **VISUAL-PDP-003** — Day cards (Sun May 3, Mon May 4, …) all use the same visual treatment regardless of past/today/future status — only a small "Today" label and an "OVERDUE" chip differentiate. The week does not visually feel like time elapsing left to right.
- **VISUAL-PDP-004** — Production job cards inside each day are functionally readable but visually flat. Quantity ("440 BOTTLE") is sized similarly to the MANUAL/IMPACT chip row beneath it. The eye cannot tell at a glance which signal matters most per card.

### Week / time comprehension failures
- **FLOW-PDP-001** — There is no horizontal time rail. The week reads as 7 disconnected vertical columns, not as a continuous Sun-Sat timeline. Time is implicit (column order) instead of explicit (visual rail).
- **FLOW-PDP-002** — Today (Sat May 9) is marked only by a thin cyan accent on the column header and a "TODAY" badge. From a 5-second glance, today is not unmistakable. The eye lands on the OVERDUE columns first because of red noise, not on today.
- **FLOW-PDP-003** — Overdue columns (Sun, Mon, Tue, Wed, Thu) all carry a red OVERDUE badge plus a red top-border. Five out of seven days are flagged red simultaneously. This collapses the urgency signal — the eye habituates and the actual priority (which overdue is most critical) becomes invisible.
- **FLOW-PDP-004** — Future days (Fri May 8, Sat May 9 — Sat is today actually) currently show empty placeholder cards reading "No production / Add". The empty state visually equals a broken card, not an intentional empty day. The brown-tinted placeholder background reads as a missing element rather than a calm "nothing planned here yet" state.

### Production card hierarchy
- **VISUAL-PDP-005** — Each production job card stacks: quantity ("300 BOTTLE") + small Hebrew text below + "MANUAL" chip + "IMPACT" chip. The two chips visually equal the title in weight. The MANUAL chip is repeated on every card; this is operational noise, not signal.
- **VISUAL-PDP-006** — Hebrew text "תה ירוק" (green tea) appears on some cards mid-card despite the locked English/LTR rule (U6 from existing packet). Suggests data passthrough is correctly Hebrew-named (per memory: names not IDs, even Hebrew-named items keep their Hebrew display) but the surrounding chrome should remain English/LTR. Verify treatment is consistent.
- **VISUAL-PDP-007** — Status indicators (status rail, OVERDUE badge, MANUAL chip, IMPACT chip) signal status three or four times per card with no clear single dominant signal.

### Action hierarchy
- **INTER-PDP-001** — Top-right has "Add from recommendations" + "Add production" — both visually equivalent, no primary/secondary differentiation. New "Materials this week" trigger needs to land cleanly without becoming a third equal-weight button.
- **INTER-PDP-002** — Per-card actions are entirely absent at the visual surface. To do anything with a card the operator must hover/click in. No affordance for the next step.

### Plan ↔ inventory relationship
- **FLOW-PDP-005** — Each card has an "IMPACT" chip that opens a per-item BOM impact drawer (`useBomImpact`). This is per-card, single-item, and requires interaction to discover. The aggregate "what materials does this whole week need?" question is invisible at the page level.

### Mobile risk
- **VISUAL-PDP-008** — At <1024px the seven-column grid will compress to unreadable vertical strips. No responsive collapse strategy is currently visible.

### Accessibility / contrast risk
- **A11Y-PDP-001** — Status colors on chips (MANUAL grey-on-grey, IMPACT yellow-on-grey) need contrast verification at WCAG AA. Color is doing semantic work without a paired text/icon distinction in some places.
- **A11Y-PDP-002** — Today and overdue rely on color + tiny text labels. Color-blind users may not differentiate.

### Background / texture
- **VISUAL-PDP-009** — Dot-grid pattern (visible behind the entire board) competes with the day-card surfaces. Removing it (or reducing to <5% opacity, masked away from the board area) will let the day-card surfaces feel raised and the time rail feel like the focal element.

---

## § 2 — Target UX concept

**Name:** Weekly Production Timeline Command Surface.

**Definition:** A premium industrial-operations weekly production board where time, today, daily load, overdue risk, planned jobs, intentional empty days, and weekly material requirements all communicate in under 5 seconds of glance. Calm, dense, refined. Reads as a single command surface, not a kanban grid.

**5-second comprehension contract:**

1. What week am I viewing? → Week range in the header + horizontal Sun-Sat time rail in Layer 2.
2. Where is today? → Cyan glow marker on the rail + raised lane surface + "Today" wordmark.
3. Which days are overdue? → Thin danger underline under the day's notch in the rail + small overdue count chip in lane header. NOT a flooded red lane.
4. What remains later this week? → Future lanes are calm default surface; subtle.
5. How loaded is each day? → Daily load bar above each rail notch encodes total units at a glance.
6. Which days are empty? → Centered intentional empty state with calm Plus action. Reads as "open day" not "broken card."
7. What needs action? → Cards with required action carry a single dominant cue (a one-tap CTA at the card foot) — no chip noise on cards that need nothing.
8. What raw materials are needed for the whole week? → "Materials this week" button in the header (Type B, drawer trigger).

---

## § 3 — Screen architecture (three layers)

### Layer 1 — Week Command Header

| Element | Component | Behavior |
|---|---|---|
| WorkflowHeader | existing `WorkflowHeader` | eyebrow="Planning workspace", title="Production plan", description="Plan production for the week. Inventory updates only when actuals are reported." |
| Freshness | existing `FreshnessBadge` | Inherits canonical thresholds: warnAfterMinutes=60, failAfterMinutes=1440 (Planning run band per `freshness-vocabulary-visual-system-handoff-2026-05-08.md`). Producer label = "production plan". |
| Planned-only caveat | existing pattern | One-line `text-fg-muted text-sm` slot below freshness. Verbatim copy preserved. |
| Primary action | "Add production" | Type A primary CTA, top-right, accent fill |
| Secondary action | "Add from recommendations" | Type A secondary, ghost variant |
| **NEW** drawer trigger | "Materials this week" | Type B drawer trigger, icon=Boxes, positioned to the LEFT of the two Add buttons with subtle separation. Optional small chip "Pending data source" rendered to the right of the label only when drawer state = `unavailable` (initial launch state). |
| Secondary nav pills | existing | Planning runs · Inventory flow · Report production |

### Layer 2 — Week Timeline Summary

| Element | Detail |
|---|---|
| KPI strip | 4 micro-cards (Planned / Completed / Total units / Done %) — keep `kpi-microcard` pattern, semantic accent left-borders |
| **NEW** time rail | Horizontal Sun-Sat rail spanning full width of the board area. 7 evenly-spaced day notches. Day name + date + load bar above the notch. Today notch glows cyan (subtle ring, not blinking). Past notches subtly desaturated. Overdue notches carry a 2px danger-tone underline directly beneath the notch. Future notches default. |
| Daily load bar | Rendered above each notch. Height encodes total planned units that day (linear scaled to max-day in week). Color encodes day status (default=accent-soft, overdue=warning-soft, today=accent, completed=success-soft). |
| Week-completion footer (existing) | Keep at the very bottom of the board. Slimmer rendering. |

### Layer 3 — Production Week Board

Seven `ProductionDayLane` components in a flex row. Min lane width 200px on desktop. Horizontal scroll if container width <1280px (overflow-x-auto on the lanes container; sticky time rail above remains in view).

Each lane:

| Element | Detail |
|---|---|
| Day header | Day-name (12px uppercase tracking) + date (16px) + small status chip (Today / Overdue×N / Empty / Default) + total units sub-label |
| Capacity bar | OPTIONAL — only render if capacity data is present in DTO; if absent, omit silently (do NOT render an empty bar) |
| Job cards | Stacked vertically. Gap 12px. |
| Empty state | Centered Plus icon (24×24 in muted ring), label "No production planned", subtext "Add from recommendations or manually". Plus button. Reads as intentional. |
| Footer Add | Inline "+ Add" button at lane foot, only when the lane already has at least one card |

Lane surface treatment:
- **Today lane:** `bg-bg-raised` + `ring-1 ring-accent/30` (subtle inner glow effect)
- **Past lane (no overdue):** `bg-bg-subtle`
- **Overdue lane:** `bg-bg` + 2px `border-l-danger/60` (rail), NOT a flooded background
- **Future lane:** `bg-bg`
- **Empty future lane:** `bg-bg` with the calm intentional empty state

---

## § 4 — Materials This Week Drawer

### Component reuse
- `Drawer` (existing) at `src/components/overlays/Drawer.tsx`. Width: `lg` (640px) on desktop. On mobile (<768px): existing slide-in animation acts as a right-side sheet that consumes most of the screen — verify that radix Dialog wrapper supports tap-outside-to-close on mobile and add a sticky bottom Close affordance for thumb reach.

### Trigger
- Header button labeled **"Materials this week"** with `Boxes` icon (lucide). Type B styling (filled neutral surface, accent on hover).
- When drawer state = `unavailable` (initial launch state, see § 12), append a small `info`-toned chip to the right of the label text reading **"Pending data source"**. Chip is `text-2xs`, no border, fg-muted background. Button itself remains fully functional and clickable; it is not disabled.
- Keyboard: Tab-reachable. `Enter` / `Space` opens drawer. Focus returns to the trigger on close.

### Drawer header
- Title: **"Materials this week"** (matches button label, no surprise rename inside).
- Subtitle: week range (e.g., "May 3–9, 2026") in `text-fg-muted text-sm`.
- FreshnessBadge slot for the materials calculation (independent from page freshness). Renders only when state ≥ `ready_*` (i.e., a calculation actually happened). For `unavailable`/`loading`/`error` no FreshnessBadge.
- Calculation basis line: **"Based on planned production for this week"** (`text-xs text-fg-faint`). Hover/title attribute surfaces the longer explanation: "Required materials are computed from each plan's pinned BOM (or active BOM if not pinned), summed across the week, then compared against current on-hand stock."

### Drawer body — 8 states (every state designed)

| # | State | Trigger | Body content | Tone |
|---|---|---|---|---|
| 1 | `loading` | Endpoint in flight | Skeleton list (5 row shimmer placeholders, 14px height each, gap-2). Header text: "Calculating material requirements…" | Neutral |
| 2 | `ready_covered` | Endpoint returned, no shortages | Confidence header chip (success tone, label "All materials covered"). Grouped list by component category if returned, else flat. Each row: name (16px, fg-strong), required + uom (tabular, 14px), available + uom (tabular, 14px), `✓ Covered` chip (success-soft) | Success |
| 3 | `ready_shortages` | Endpoint returned, ≥1 shortage | Confidence header chip (warning or danger tone depending on max shortage severity, label "X of Y materials short"). Shortage rows rendered first with `border-l-2 border-l-danger`, sorted by severity. Each row: name, required, available, **shortage delta**, expandable "Sources" sub-list (which planned jobs require this component, names not IDs). Covered rows shown beneath in muted treatment. | Warning/Danger |
| 4 | `ready_no_plans` | No active production plans in week | Centered icon, header "No production planned for this week", body "Materials are calculated only when production is planned." Single CTA: "Add production" → closes drawer + opens manual-add modal. | Neutral |
| 5 | `ready_missing_bom` | Endpoint returned but ≥1 plan has no active BOM | Confidence header chip (warning, label "Calculation incomplete"). Banner above list: "Some planned products have no active BOM and were excluded. Set up BOMs in Admin." Rows for plans-with-BOM rendered as ready_covered/shortages; excluded plans listed at bottom under "Excluded from calculation" with item names. | Warning |
| 6 | `unavailable` (initial launch state) | Backend endpoint not yet implemented | Centered icon (Database with slash overlay or similar). Header: **"Weekly material calculation requires a verified materials endpoint."** Sub-block listing: <br>• Selected week: `May 3–9, 2026` <br>• Calculation basis: **unavailable** <br>• Source: **pending verified backend data** <br><br>Footnote: "For per-item material impact, open a production card and use *Inventory impact*." (links to existing per-card BOM drawer pattern — already implemented via `useBomImpact`.) <br><br>**No exact quantities. No mock rows. No placeholder shortages.** | Neutral / honest |
| 7 | `stale` | Endpoint returned but `calculated_at` older than failAfterMinutes threshold | Same body as ready_* state but with banner at top: "This calculation is stale. Refresh to recompute." + Refresh CTA. Existing rows shown with reduced opacity (`opacity-70`). | Warning |
| 8 | `error` | Endpoint failed (network / 5xx / timeout) | Centered icon. Header: "Couldn't load materials". Body: "Try again, or contact support if this persists." CTA: "Retry". | Danger |

### Forbidden behaviors (locked into packet)
- Do NOT compute material requirements client-side by walking BOM lines and scaling.
- Do NOT call the existing single-BOM endpoint repeatedly and aggregate in the portal.
- Do NOT display production-simulation IDB data — that surface is non-trusted per its own audit banner.
- Do NOT render placeholder rows ("vodka — TBD", "bottle — pending") that visually suggest real data exists.
- Do NOT show exact quantities without `source` + `freshness` + `calculation basis` simultaneously visible in the drawer.

---

## § 4a — Frontend Design Craft Requirements

This section is the design-quality lens that a structurally-correct implementation must clear to count as done. Implementer must read this section before starting and before declaring DONE.

### Visual focal point
- The week itself is the focal point of the page. Time rail (Layer 2) + the today lane (Layer 3) form a single axis the eye should land on first.
- KPI strip is supportive context, not the hero. Sized to read but not to dominate.
- Materials drawer trigger is a deliberate accent in the header — it earns attention but does not steal from the title.

### Premium dark-mode surface layering
- Three explicit surface tiers: `bg` (page canvas) → `bg-subtle` (board container) → `bg-raised` (today lane, drawer surface, KPI cards). Each tier differs by ~3–5% luminosity in dark mode. The eye should feel depth without seeing strong shadows.
- Borders: `border-faint` for default separation, `border-strong` only for selected/focused states.
- No box-shadow color drama. If shadow is used, it is a subtle drop with very low opacity (Tailwind `shadow-sm` or smaller), and in dark mode it is replaced by a 1px lift via lighter surface luminosity.

### Professional spacing rhythm
- 8px base unit. Approved gaps: 8 / 12 / 16 / 24 / 32 / 48.
- KPI strip: 16px gap between cards, 24px from header above, 32px from time rail below.
- Time rail: 24px vertical breathing room above and below.
- Day lanes: 16px gap between lanes; 16px lane padding.
- Job cards: 12px gap stacking; 14px card padding.
- Drawer: 24px outer padding, 16px between header and list, 8px between rows.
- No tighter-than-8px gaps anywhere on this page. No looser-than-48px gaps inside the board.

### Card elegance
- Each production job card is a single composition with one clear hero (the quantity + unit), one secondary line (item name), one status rail (left border, single semantic color), and one quiet metadata row at the foot.
- No more than 3 chips per card. If a card has nothing requiring action, it shows zero chips.
- Hover state: subtle ring (`ring-1 ring-accent/20`) + 1px translate-y lift via transform. Not a heavy elevation. Not a color flood.
- Selected/active card: `ring-1 ring-accent` + raised surface. One state at a time.
- Cancelled cards: existing strikethrough + 0.7 opacity. Keep.

### Timeline readability
- Time rail is visually distinct from the board beneath it. It is the only horizontal element on the page that visually says "time."
- Today marker is a precise cyan dot (8px) + 2px ring (`ring-accent/50`) + a subtle vertical guide line that descends from the rail into the today lane (1px, accent at 20% opacity, 80px tall, fades to transparent).
- Past notches: 0.55 opacity. Future notches: 1.0 opacity, neutral.
- Overdue underline: 2px solid `danger/70`, immediately beneath the notch, never wider than the notch itself.

### Restrained glow
- Approved glow surfaces (only):
  - Today notch on the rail
  - Today lane (subtle inner ring)
  - Selected card / day
  - Drawer when open (Radix Dialog overlay backdrop is enough; do not add additional glow)
  - Critical overdue when explicitly focused (keyboard or click)
- Forbidden:
  - Animated pulsing dots anywhere on this page
  - Glow on KPI cards
  - Glow on every overdue lane (only on focused/critical, not at rest)
  - Glow on the materials drawer trigger button

### Reduction of visual noise
- **Dot-grid background:** Remove from the board area. Two acceptable implementations: (a) page-level dot-grid is masked away from the board's bounding rectangle via a CSS mask or a solid `bg-bg` container that sits above the dot pattern; or (b) global dot opacity reduced to ≤4% and the board's `bg-subtle` covers it visually. Option (a) preferred.
- Remove the per-card `MANUAL` chip when source is the only piece of information conveyed and most cards are manual. Move source into a single icon-only indicator at the corner of the card (`Pencil` for manual, `Sparkles` for recommendation), or surface it only when a card is recommendation-sourced (since manual is the baseline default).
- Collapse `IMPACT` chip into a single small icon button in the card foot row. Only visible when the operator hovers/focuses the card, OR always-visible at 0.6 opacity.
- Empty future days: NOT a brown placeholder card. A calm centered icon + label, sitting in a transparent lane area.

### Before/after visual intent

| Aspect | Before (current `02266b8`) | After (PDP-UX-01) |
|---|---|---|
| Where the eye lands first | KPI strip and OVERDUE chips compete | Time rail with today marker |
| What the week feels like | 7 disconnected vertical columns | A continuous Sun→Sat timeline |
| How today reads | A small "TODAY" label among other badges | An unmistakable cyan accent on the rail + raised lane |
| How overdue reads | 5 simultaneously red columns, signal collapses | Thin danger underline beneath each overdue notch + small overdue chip in lane; lane background calm |
| How empty days read | Placeholder card that looks broken | Calm intentional empty state; lane breathes |
| How a card reads | 4 competing signals (qty, status, manual chip, impact chip) | Quantity dominates; one status rail; metadata recedes |
| How materials are surfaced | Hidden per-card behind hover | "Materials this week" trigger in the header (visible always) |
| Background | Dot-grid noise behind everything | Dot-grid masked away from the board; board has clean depth via surface layering |
| Overall feel | Functional kanban grid | Premium industrial command surface |

### Why the result should feel better than the current screen
- The week communicates as time, not as 7 columns. A planner glances and instantly knows where they are in the week.
- Overdue reads as a real priority signal, not as background red noise.
- Empty days feel like decisions, not gaps.
- Cards reward fast scanning — quantity dominates because that is what the planner is looking for.
- Materials are surfaced at the page level via one deliberate button. Operators do not have to inspect every card to feel weekly material risk.
- The whole page reads as one calm, premium operations surface — not as a collection of disconnected widgets.
- Even the "unavailable" materials drawer state communicates honesty: it tells the operator what is missing without pretending to have data.

---

## § 5 — Visual direction (token usage)

**All tokens are reused from existing portal design system.** No new tokens added in this run. If a critical visual outcome cannot be achieved with current tokens, a `design-system delta` is documented in § 13 (Tom open questions) — global tokens are NOT modified by the implementer in this run.

| Role | Token | Source |
|---|---|---|
| Page canvas | `bg` | `globals.css` existing |
| Board container surface | `bg-subtle` | existing |
| Lane surface (default future) | `bg` | existing |
| Lane surface (today) | `bg-raised` + `ring-1 ring-accent/30` | composition |
| Lane surface (past, no overdue) | `bg-subtle` (slightly muted further with `opacity-95`) | composition |
| Lane surface (overdue) | `bg` + `border-l-2 border-l-danger/60` | composition |
| Card surface | `bg-raised` | existing |
| Drawer surface | Radix overlay + `bg-raised` | existing Drawer |
| Border subtle | `border-faint` | existing |
| Border strong | `border-strong` | existing |
| Border focus | `border-focus` | existing |
| Text strong | `fg-strong` | existing |
| Text default | `fg` | existing |
| Text muted | `fg-muted` | existing |
| Text subtle / faint | `fg-subtle` / `fg-faint` | existing |
| Planned amber | `warning` family | existing |
| Completed green | `success` family | existing |
| Overdue red | `danger` family | existing |
| Today / accent (petrol teal) | `accent` family | existing |
| Inventory / materials | `info` family | existing |
| Neutral | `fg-muted` + `bg-muted` | existing |

**Dark-mode surface layering:** rely on the three `bg` / `bg-subtle` / `bg-raised` tiers as defined. Implementer must verify each tier is visually distinguishable in both light and dark mode — if not, document as a design-system delta in § 13, do NOT modify `globals.css`.

**Dot-grid background:** Remove from the board area. See § 4a for two acceptable implementations.

**Glow rules:** see § 4a "Restrained glow".

---

## § 6 — Typography specification

Inherits Public Sans + IBM Plex Mono from `tailwind.config.ts`. 14px base operational density.

| Role | Size class | Weight | Notes |
|---|---|---|---|
| Page title | `text-3xl` (≈30px) | 700 | WorkflowHeader title slot |
| Subtitle / caveat | `text-sm` | 500 | `text-fg-muted` |
| KPI numbers | `text-3xl` | 700 | tabular-nums |
| KPI labels | `text-2xs` | 600 | uppercase, tracking-wider |
| Day name (lane header) | `text-xs` | 700 | uppercase, tracking-wide |
| Date | `text-sm` | 600 | tabular-nums |
| Card quantity | `text-2xl` | 700 | tabular-nums, dominant |
| Card unit | `text-sm` | 600 | secondary to quantity |
| Card item name | `text-base` | 700 | secondary to qty/unit |
| Metadata chips | `text-2xs` | 600 | grouped at card foot |
| Drawer material qty | `text-base` | 700 | tabular-nums |
| Drawer material name | `text-base` | 700 | fg-strong |
| Drawer caveat | `text-xs` | 500 | fg-faint |

Constraint: no more than 2–3 dominant type sizes per visible region. Quantities and dates must use tabular-nums. Body and metadata never exceed 14px.

---

## § 7 — Layout rules

8px spacing rhythm. Approved gap scale: 8 / 12 / 16 / 24 / 32 / 48 (already mapped in § 4a).

**Desktop ≥1440px:** 7 day lanes side-by-side, lane min-width 200px; comfortable. Board can be wider than viewport — outer container scrolls horizontally.

**Desktop 1280–1439px:** 7 lanes still side-by-side at min-width; horizontal scroll if needed. Time rail above stays visible and sticky.

**Tablet 768–1279px:** Approach: keep the rail full-width sticky at top; collapse the board to a "today + next 2 days" focused view with a smaller rail-strip selector that lets the operator nudge the focus window.

**Mobile <768px:** Vertical day list. Time rail becomes a horizontal sticky strip at the top. Selected day expands inline with its cards. Materials drawer renders as a near-full-screen sheet from the right (Radix Dialog default behavior — verify it consumes ≥85% of viewport width on mobile).

Constraint: no unreadable seven-column squeeze on small screens. If responsive collapse cannot be cleanly implemented in this run, mobile is explicitly deferred and called out in § 11 verification gates as "Mobile collapse strategy deferred — single-column fallback acceptable for v1."

---

## § 8 — Production card redesign

**Hierarchy (top → bottom):**

1. Quantity + Unit row — dominant, tabular-nums, qty in `text-2xl/700`, unit in `text-sm/600` to its right.
2. Item name — `text-base/700`, single line, truncate with title attribute on overflow.
3. Single status rail — left border, 2px, semantic color (planned=`warning`, done=`success`, cancelled=`fg-muted`).
4. Conditional metadata foot row — only renders if there is meaningful metadata. Source icon (only for recommendation-sourced cards: `Sparkles` icon at `text-2xs`); inventory-impact icon button (small, `Boxes`); overdue indicator (only for overdue cards: small `Clock` icon with `text-danger` at the start of the row).
5. Conditional next-action button — appears only when card explicitly needs an operator action (e.g., "Open report" for a card whose plan_date has passed and is still planned, not cancelled, not completed).

**Removals vs current:**
- Remove the `MANUAL` chip from manually-sourced cards (manual is baseline; surface only deviation = `Sparkles` for recommendation source).
- Collapse `IMPACT` chip into a small icon button.
- Remove duplicate status signaling (currently border + bg tint + chip + badge all signal the same status).

**State combinations:**

| Plan state | Visible cues |
|---|---|
| Planned (not overdue) | Status rail (warning), qty/unit/name, optional source icon |
| Planned (overdue) | Status rail (danger), qty/unit/name, source icon, `Clock` icon at foot |
| Completed | Status rail (success), qty/unit/name shown with output_qty + variance summary block (existing `completed_actual` block — keep as today, restyled to fit the smaller card aesthetic) |
| Cancelled | strikethrough qty + name, opacity 0.7, no chips |

**Hover / selected states:** subtle ring + lift per § 4a. One state at a time.

---

## § 9 — Week-time readability

Already specified in § 3 Layer 2 + § 4a "Timeline readability". Cross-check:

- Time rail across the top of the board: ✅ § 3 Layer 2
- Today unmistakable: ✅ § 3, § 4a
- Past visually distinct: ✅ § 3 (lane surface tier), § 4a (notch desaturation)
- Future calmer: ✅ § 3
- Overdue urgency without flooding: ✅ § 3 (lane border-l), § 4a (rail underline)
- Empty days intentional: ✅ § 3 + § 4a
- Daily load visible before reading individual cards: ✅ § 3 (load bar above each notch)

---

## § 10 — Implementation plan (file scope)

**Approved files for this run.** No file outside this list may be modified. No global tokens, no `globals.css`, no `tailwind.config.ts`, no backend, no DB, no other planning screens.

| File | Change kind | Detail |
|---|---|---|
| `src/app/(planning)/planning/production-plan/page.tsx` | major edit | Restructure into 3-layer architecture (Layer 1 header / Layer 2 KPI+rail / Layer 3 day lanes). Extract local components below. Mount Materials this week drawer trigger + drawer instance. |
| `src/app/(planning)/planning/production-plan/_components/WeekTimelineRail.tsx` | NEW (local) | Sun-Sat horizontal rail with daily load bar + today marker + overdue underline + past/future treatment. |
| `src/app/(planning)/planning/production-plan/_components/ProductionDayLane.tsx` | NEW (local) | Single day lane composition (header + capacity bar if data + cards + empty state + footer Add). |
| `src/app/(planning)/planning/production-plan/_components/ProductionJobCard.tsx` | NEW (local) | Redesigned card per § 8. |
| `src/app/(planning)/planning/production-plan/_components/MaterialsThisWeekDrawer.tsx` | NEW (local) | Composes existing `Drawer` + 8-state machine per § 4. Initial launch state = `unavailable`. |
| `src/app/(planning)/planning/production-plan/_lib/types.ts` | minor edit | Add `MaterialsDrawerState` union + `MaterialsThisWeekDTO` type stub (returns `unavailable` for now). |

**Out-of-scope (must not be touched):**
- `tailwind.config.ts` — global tokens locked
- `src/app/globals.css` — global tokens locked
- `portal_ux_standard.md`, `portal_language_direction_audit.md`
- `api/**`, `db/**` — no backend/schema changes
- All other planning screens (governed by existing planning-ux-full-pass packet)
- Frozen flags (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`)

**Local extraction is approved** — moving today's page-local components (DayCard, ProductionItemChip, WeekLoadSegment) into the new local component files is permitted and encouraged. Existing modal components (ManualAddModal, AddFromRecommendationsModal, EditModal, CancelModal) stay in `page.tsx` for this run; no rewrite needed.

---

## § 11 — Verification gates

Implementer cannot declare DONE without all of these.

### Visual gates
- Three screenshots produced and committed to `PRODUCTION/docs/phase8/ux/screens/PDP-UX-01/`:
  - `after-1440x900.png`
  - `after-1280x800.png`
  - `after-390-mobile.png`
- One **before** screenshot reference at `before-1440x900-from-portal-tip-02266b8.png` (already implicitly captured in this packet's audit; implementer adds a copy alongside the after shots for direct comparison).
- No text clipping at any width.
- Time rail visually present and readable at 1440 and 1280; collapses correctly at 390.
- Today is unmistakable at all three widths from a 5-second glance.
- Overdue is visible but not overwhelming — no fully-red lane backgrounds.
- Empty future days look intentional.
- Materials this week button renders in header, opens drawer on click and `Enter`.
- Drawer renders in `unavailable` state with: selected week, calculation basis = unavailable, source = pending verified backend data. **No fake quantities. No placeholder material rows.**
- Dot-grid background is removed from the board area or reduced to ≤4% opacity behind it.

### A11y gates
- WCAG AA contrast for all meaningful text against its surface (verify with browser tooling).
- Status indicators paired with text or shape (no color-only signaling).
- Drawer trigger reachable via Tab; drawer closes via Esc; focus returns to trigger on close.
- Touch targets ≥44px on mobile.
- Reduced-motion preference respected (no glow animation on today notch when `prefers-reduced-motion: reduce`).

### Code-hygiene gates
- No edits outside the files listed in § 10.
- No DB / BOM / backend edits.
- No `tailwind.config.ts` or `globals.css` edits.
- Portal `npm run build` passes.
- Portal `npm run lint` passes.
- Portal `npm run typecheck` passes.

### Implementer self-critique gate
- Implementer must produce a markdown file at `PRODUCTION/docs/phase8/ux/screens/PDP-UX-01/self-critique.md` listing **5 remaining visual weaknesses after implementation**. This forces honest assessment. Empty list = automatic FAIL of this gate (every implementation has weaknesses; admitting them is the gate).

### Verifier dispatch
- After all of the above, dispatch `verifier` agent with: this packet path + portal git diff + screenshots + self-critique. Verifier returns PASS / FAIL.

---

## § 12 — Backend dependency declaration (NON-AUTHORITATIVE)

**This section does not author the backend contract.** It declares only what the drawer's UX needs to display in order to graduate from `unavailable` → `ready_*` states.

W4 (`integration-boundary-executor` / `executor-w4`) owns the actual contract: endpoint path, response shape, calculation basis, freshness model, error semantics, backend verification, and the contract requirements specification document. This packet may neither lock nor preempt that work.

### UX data needs (illustrative shape only — NOT a contract)

When backend is ready, the drawer needs to display per material row:
- material name (names not IDs per `feedback_names_not_ids_in_ui.md`)
- required quantity + uom
- available quantity + uom (if trusted)
- shortage delta (if trusted)
- list of source plans / products that require this material (names, plan dates, contributing qty per plan)
- caveats (an array of strings describing what the calculation does not include — e.g., "Open POs not netted")

And per drawer-level metadata:
- selected week (from page state)
- calculation timestamp
- confidence label (verified / estimated / missing source)
- list of plans excluded from calculation (with reason — e.g., "no active BOM")
- aggregated counts (total materials, total shortages)

### Initial launch behavior (until W4 contract + backend land)
- Drawer state hard-coded to `unavailable`.
- Body shows the exact copy locked in § 4 state #6:
  - Header: "Weekly material calculation requires a verified materials endpoint."
  - Body: selected week + calculation basis: unavailable + source: pending verified backend data
  - Footnote: "For per-item material impact, open a production card and use Inventory impact."
- No exact quantities. No mock rows. No placeholder shortages.
- Trigger button shows "Pending data source" chip beside its label.

### Hand-off recipient (separate dispatch)
- W4 must author a contract requirements specification document (not in this packet's scope).
- Once W4 contract lands, backend-db-executor implements the endpoint per W4 spec.
- Once backend endpoint is verified live, this packet's drawer is upgraded from `unavailable` to live states 1–5/7/8 in a follow-on portal cycle (PDP-UX-01b). The state machine in `MaterialsThisWeekDrawer.tsx` is built upfront so this graduation requires only the data-fetch wiring.

---

## § 13 — Tom open questions (post-packet review)

Items that may still need Tom decision after he reviews the packet:

1. **Today marker treatment on the time rail** — cyan dot + ring + descending guide line vs. just dot + ring (no guide line).
2. **Capacity bar in lane header** — proposed as conditional render only when capacity data is in the DTO. No capacity data exists today. Two paths: (a) omit silently if absent (current proposal); or (b) defer the entire capacity-bar concept to a future cycle once a capacity model is locked.
3. **Dot-grid background removal vs reduction** — preferred is full mask away from the board area; alternative is global opacity reduction to ≤4%. Either is acceptable for this run; implementer picks one and documents.
4. **Materials this week chip on trigger button** — "Pending data source" chip when state is unavailable, vs. no chip at all (button only). Current proposal: chip. Alternative: no chip, drawer body alone communicates the unavailable state.
5. **Mobile collapse strategy** — full responsive collapse (vertical day list + sticky rail strip) within this run, or defer mobile to a follow-on cycle and ship desktop-first only. If deferred: implementation lists "Mobile collapse strategy deferred" in § 11.
6. **Design-system deltas (if surfaced during implementation)** — if implementer finds that current tokens cannot achieve the premium dark-mode surface layering required by § 4a, the delta is documented in a follow-up file at `PRODUCTION/docs/phase8/ux/design-system-deltas/PDP-UX-01-deltas.md` rather than being applied to global tokens. Tom decides whether to dispatch a follow-on visual-system-designer cycle to land the deltas.

---

## § 14 — Summary report (maps to Tom's 9 reporting items)

1. **Current screen weaknesses** → § 1 (10+ tagged findings across visual, flow, interaction, a11y, copy domains).
2. **Target visual architecture** → § 2 + § 3 (three-layer architecture: Week Command Header / Week Timeline Summary / Production Week Board).
3. **Proposed component structure** → § 10 (one major edit + four new local components + one types edit).
4. **Exact token proposal** → § 5 (reuse-only — zero new global tokens; design-system deltas documented separately if needed per § 13.6).
5. **Weekly materials drawer data dependency assessment** → § 4 (forbidden behaviors box) + § 12 (non-authoritative dependency declaration).
6. **Files expected to change** → § 10 (six files total, all under `src/app/(planning)/planning/production-plan/`).
7. **What can be implemented immediately** → Visual redesign per § 1–§ 11 + Materials this week drawer trigger button + drawer shell with `unavailable` state per § 4 state #6.
8. **What remains blocked by BOM/data truth** → Drawer states 2, 3, 5, 7 (any state requiring real material data) — blocked until W4 authors backend contract + backend implements endpoint.
9. **Verification plan** → § 11 (visual gates / a11y gates / code-hygiene gates / implementer self-critique gate / verifier dispatch).

---

## § 15 — Handoff signature

- **Acceptance criteria for packet approval:** Tom replies with explicit approval of this packet path. No changes to portal or backend until that happens.
- **Implementation owner after approval:** `portal-production-executor` (only after Tom dispatches it; not auto-triggered by approval alone).
- **Backend dependency owner:** `executor-w4` / `integration-boundary-executor` (separate dispatch by Tom; does not block visual redesign).
- **Design-system delta owner (if surfaced):** `visual-system-designer` (separate cycle after implementation surfaces a real need).
- **Rollback plan:** revert the six files listed in § 10 via git. No schema, no state, no flags involved. Portal-only change is safely reversible.
- **Next handoff:** Tom approval → portal-production-executor dispatch with this packet as input → verifier dispatch on PASS claim → if PASS, separate W4 contract cycle for materials endpoint → if W4 + backend deliver, follow-on cycle PDP-UX-01b graduates the drawer from `unavailable` to live data.

---

## Appendix — Critical files (read-only references)

| Purpose | Path |
|---|---|
| Live page source (read for audit) | `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(planning)\planning\production-plan\page.tsx` |
| Reusable Drawer | `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\overlays\Drawer.tsx` |
| FreshnessBadge spec | `PRODUCTION/docs/phase8/ux/freshness-vocabulary-visual-system-handoff-2026-05-08.md` |
| Universal rules U1–U7 (inherited) | `PRODUCTION/docs/phase8/ux/planning-ux-full-pass-handoff-2026-05-08.md` § 2 |
| Tailwind config (read-only) | `C:\Users\tomw2\Projects\window2-portal-sandbox\tailwind.config.ts` |
| globals.css (read-only) | `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\globals.css` |
| Existing per-card BOM impact (referenced in drawer footnote) | `useBomImpact` hook in `src/app/(planning)/planning/production-plan/_lib/usePlans.ts` |
| Frontend Design craft skill (lens used for § 4a) | `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md` |

---

**End of packet.**
