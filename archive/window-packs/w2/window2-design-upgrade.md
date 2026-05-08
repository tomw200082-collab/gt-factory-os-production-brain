# Window 2 — Design Upgrade Pass

_2026-04-14 · design polish round · no product scope changes_

## Aesthetic direction

**"Operational Precision."** A modern control tower for a factory ops platform. Premium B2B, not consumer. Industrial heritage. Tuned for eight-hour shifts without eye fatigue.

Concrete commitments made up-front and executed consistently:

- **Surface palette:** warm bone paper (`hsl(42 18% 95%)`), not cold white. Soft dot-grid background texture at 3% opacity. Raised card surfaces sit slightly brighter than the page so hierarchy comes from contrast, not from shadow.
- **Ink:** warm graphite near-black (`hsl(30 10% 10%)`) for primary text. A five-step tone ladder — `fg-strong` → `fg` → `fg-muted` → `fg-subtle` → `fg-faint`.
- **Signature accent:** deep petrol teal (`hsl(186 42% 24%)`). Not generic SaaS cornflower blue. Technical, calm, adult.
- **Semantics:** muted moss (success), burnt amber (warning), oxidized red (danger), slate blue (info) — deliberately restrained so state signals don't compete with content.
- **Typography:** `Public Sans` (GSA-grade, serious, uncommon in SaaS admin) for all UI copy, `IBM Plex Mono` for numerics, IDs, codes, and audit trails. Single-family sans discipline — hierarchy from weight + size, not from font mixing. 14px base for operational density (closer to Linear/Retool than to consumer 16px). Tabular numerics everywhere by default.
- **Borders:** hairline 1px at calibrated opacity (`border/70` – `border/40` in the utility layer). No heavy solid rules.
- **Shadows:** minimal. One `shadow-raised` for cards (barely there), one `shadow-pop` for modals/detail pane drop-downs, one `shadow-focus-ring` for focus. Elevation is mostly contrast.
- **Icons:** `lucide-react`, 1.75–2 stroke, 14–16px. One per nav item, one per status, one per action. Never decorative.
- **Motion:** 150ms `ease-out-quart`. One page reveal (`fade-in-up` with staggered delays) so arriving on a screen feels composed rather than instant-and-jarring. No bounces.

## Foundation layer — what was rewritten

### `tailwind.config.ts`

Replaced the generic blue/gray HSL scaffold with the Operational Precision system:

- **Colors:** full `bg`, `fg`, `border`, `accent`, `success`, `warning`, `danger`, `info` scales — each with `DEFAULT`, `soft`, `softer`, `fg`, `border`, `hover`, `ring` where relevant. 40+ named tokens in one coherent set.
- **Typography:** 11-step font-size scale from `3xs` (10px, for uppercase eyebrows) through `4xl` (36px, for page titles). Each size paired with a letter-spacing and line-height calibrated for its use.
- **Letter spacing:** custom `tightish`, `tight`, `tighter`, `ops` (0.08em for uppercase eyebrows), `sops` (0.12em, airier variant).
- **Border radius:** 6px default, not Tailwind's stock 8px — sharper, more operational.
- **Shadows:** three purpose-built shadow tokens (`raised`, `pop`, `focus-ring`) and `hairline` for 1px inset borders.
- **Keyframes + animations:** `fade-in-up`, `fade-in`, `pulse-soft`.
- **Timing functions:** `out-quart`, `out-expo` for refined motion curves.
- **Spacing:** extended half-steps (`4.5`, `5.5`, `6.5`, etc.) for precise rhythm.

### `src/app/globals.css`

Rewrote the base + component layer:

- **Base layer:** dot-grid background, warm selection color, custom scrollbars, tabular numerics globally, stripped Chrome number-input spinners (they scream "admin template").
- **Component classes:** promoted `.card`, `.btn`, `.input`, `.textarea`, `.label`, `.table-base`, `.chip`, `.field-error`, `.field-hint`, `.eyebrow` to a proper, consistent library. Each has refined hover, focus, and disabled states. Btn variants (`-primary`, `-danger`, `-ghost`, `-outline`) and size modifiers (`-sm`, `-xs`, `-lg`) for real composition.
- **Utility layer:** `.bg-grid`, `.bg-grid-fade` (radial fade mask), `.stripe-border` (diagonal ticker texture for dev notes), `.elev-1`, `.dot`, plus the `.reveal` / `reveal-delay-N` utility pair used for first-visit staggered entrance.

### `src/app/layout.tsx`

Wired `Public_Sans` and `IBM_Plex_Mono` via `next/font/google` so both are self-hosted, swap-displayed, and available as CSS variables (`--font-public-sans`, `--font-plex-mono`) referenced by the Tailwind config.

## Shared primitives — what was upgraded

Every primitive under `src/components/` was rewritten to the new aesthetic. The improvements propagate to every screen that uses them; most pages got better for free.

| Primitive | Key improvements |
|---|---|
| **`AppShellChrome`** | Top bar now sticks with backdrop blur. Wider gutters (8/10 rem). Side nav is `sticky top-[88px]`. Page padding breathes. |
| **`TopBar`** | Custom GT factory brand mark (layered cube SVG). Subtle global status strip (Ledger / Jobs / version). Review-mode button with `FORCED` chip when a state is forced. **FAKE SESSION** pill now reads like a premium warning ticket — dot + eyebrow + separator + display name + mono role code — with an invisible native `<select>` overlaid on a chevron so the click target is clean. |
| **`SideNav`** | Lucide icon per item (hand-curated: `PackageOpen` for receipts, `ClipboardCheck` for counts, `LineChart` for forecast, etc.). Active state uses a 2px accent bar on the left rather than a heavy background fill. Group headers are thin all-caps eyebrows with a trailing rule. Blocked items show a compact `Lock` glyph, not a verbose "blocked" label. New "You are" card pinned below the groups. |
| **`WorkflowHeader`** | Eyebrow is a dot + uppercase label. Title is now `text-3xl` (was `text-2xl`), tracked tighter for a more editorial feel. Meta and actions are clearly separated. Header closes with a gradient hairline rule that starts the page content rhythm. Entire header fades in on first visit. |
| **`SectionCard`** | New `eyebrow` slot. Gradient header from raised → muted for a subtle top light. 5 tone variants (`default` / `warning` / `danger` / `info` / `success`) and 2 densities. |
| **`FormActionsBar`** | Now a floating raised card at `bottom-6`, not a bar flush with the viewport. Backdrop blur. Leading slot holds dirty indicators, primary is always on the right. |
| **`FieldGrid` / `Field`** | Eyebrow-style field labels (uppercase, tracked). New `optional` prop for soft affordance. Errors render with an inline `AlertCircle` icon. Hint + error are mutually exclusive at the style level so they don't pile up. |
| **`ValidationSummary`** | Left accent bar (3px). Icon chip in semantic color. Blockers and warnings stack as dotted list items with mono field names. Fades in. |
| **`ApprovalBanner`** | Accent bar + icon chip. "Policy · …" footer line with shield icon. Warning vs info tones. |
| **`DiffNotice`** | Accent bar + icon + reload/dismiss button pair. Tone-aware (info/warning/danger). |
| **`StatusBadge`** + **`Badge`** | Dot-driven semantics — every state has a colored dot + compact uppercase label. Two `Badge` shapes (soft / outline / solid) and an optional `dotted` prop. Pulse animation on live states (`submitting`, `pending_approval`). |
| **`FreshnessBadge`** | New compact variant. Monospace "Xm ago" value with a tiny inline `Clock` glyph and a semantic health dot. |
| **`ReadinessBadge`** | Dot + label left, detail + state code right. Fits a narrow status cluster cleanly. |
| **`EmptyState` / `LoadingState` / `ErrorState` / `SuccessState` / `StaleNotice`** | Icon chip in a framed box. Dot-grid background texture on empty, subtle gradient on success variants. SuccessState has three tones (success/warning/info) with matching accent bars and composed title/description/children/action slots. |
| **`SearchFilterBar`** | Magnifier inside input, clear-X when query is non-empty, chip filters now render as dotted outline pills with a colored dot when active. |
| **`AuditSnippet`** | Four-cell grid inside a muted well. Icon + eyebrow per cell. Mono version number. Status dot. |
| **`QuantityInput`** | Unit renders as a segmented chip with a left hairline divider inside the input's right edge — it reads as part of the field, not as free-floating text. Tabular numerics, tighter font weight. |
| **`DateTimeInput`** | Mono tabular font so dates align in a column. |
| **`NotesBox`** | Reuses the upgraded `.textarea` base. |
| **`EntitySearchSelect`** | Completely new presentation — chevron rotates on open, search magnifier inside the dropdown header, option rows show a checkbox + label + mono sublabel + optional hint. Shadow `pop` for the open menu. |
| **`LineEditorTable`** | Mono row numbers with leading zero. Trash icon on hover replaces the old ✕ glyph. Tighter cells (1.5/2.5 padding). Sticky-safe footer with line count on the left and an outlined `+ Add line` button on the right. |
| **`ReviewModePanel`** | Petrol header bar with an `Eye` icon. Inline `dot`-accented option chips. `Reset` button with `RotateCcw` icon. Slides in with `reveal` animation. |

## Screens polished on top of the primitives

### Dashboard (`/dashboard`)

Rebuilt from plain "tiles + list" into a proper control tower:

- **Four hero tiles** — Stock Health, Planning Run, Exceptions, Readiness. Each has an eyebrow, a large mono-numeric value (`text-4xl` tabular), an optional percentage bar (health tile), a bottom strip of dotted badges, and a faint `Zap` watermark in the corner (4% opacity — atmosphere without noise).
- **Stockout watch** list — each row shows a framed `Nd days` tile with semantic urgency color, item name, on-hand quantity, and a rank glyph.
- **Data freshness cluster** — every boundary system (Ledger / LionWheel / Shopify / Green Invoice) with its compact `FreshnessBadge` and a short sub-label explaining its role.

### Forecast workspace (`/planning/forecast`)

Rebuilt as a serious working surface:

- New top bar with version badge, horizon badge, bucket granularity, and compact freshness badge — so the planner always knows what they're looking at.
- Header actions: History / Export / Publish version triplet with the publish button as primary.
- Grid now has a sticky-left item column (with gradient fade into transparent), mono bucket headers (e.g. `W17`), and cell inputs that glow petrol on focus with an inset focus ring. Zero cells render as em-dashes in faint gray so active edits pop visually.
- **New grand-total row** at the bottom with an accent-tinted total cell.
- **Family group headers** are sticky-styled with a dot + uppercase family name + SKU count chip.
- Approval banner is always visible ("Publishing requires a secondary planner review") with the exact `planning_policy` key that triggered it.
- Form actions bar now shows a live dirty-count with a pulsing dot when unsaved, and three distinct buttons (Revert / Discard / Save N).

### Purchase recommendations (`/planning/purchase-recommendations`)

Rebuilt as a decision queue, not a list:

- Grouped by supplier with indeterminate-state master checkboxes per group.
- Urgency rendered as `Badge variant="solid"` in danger for critical (with a `Flame` glyph). Row selection tints the row with `data-selected="true"` → accent-soft background.
- Stronger secondary info: mono component ID under the name, mono `target_receive_date` with `Clock` glyph, reason in muted italic.
- Action footer groups reject/hold as ghost buttons and keeps approve as primary with a `Check` glyph. Selection count shows "N selected for action".

### Exceptions inbox (`/exceptions`)

Rebuilt with severity emphasis and a refined expand pattern:

- Left 3px accent bar keyed to severity.
- Icon chip box in semantic tone (Critical = `AlertCircle`, Warning = `AlertTriangle`, Info = `Info`).
- Row header gets the severity badge + source chip + status pill + right-aligned timestamp in one clean strip.
- Expand opens a `fade-in` panel with detail text, recommended-action info card (`ShieldCheck` icon, info-softer background, info border), and two distinct action buttons.

### Approvals inbox (`/approvals`)

Rebuilt as grouped approval cards:

- Kinds are now human-labeled (`waste_adjustment` → "Waste / Adjustment").
- Each row has a `ClipboardList` icon chip + role badge + submitter + timestamp + summary + trigger-reason line (with `ShieldCheck` glyph).
- Payload preview is a collapsible `ChevronRight → ChevronDown` disclosure over a mono code block.
- Approve / reject stacked on the right as primary (check) + ghost danger (X).
- Hero meta badges show session-local tallies ("N approved this session", "N rejected this session").

### Operator home (`/home`)

Rebuilt:

- Three quick-action cards with hover gradient tints (`from-accent/10`, `from-warning/10`, `from-info/10`), icon chip, title, description, and an "Open form →" caret that translates on hover.
- Recent submissions list with form-type chip + mono timestamp + summary + `StatusBadge`.

### My submissions (`/my-submissions`)

Refined:

- Filter chips via upgraded `SearchFilterBar` with active dots.
- Each submission row has a form-type chip + mono idempotency key eyebrow + larger title + mono timestamp pair. Retry / Discard appear inline for `queued` and `failed_retriable` rows with `RotateCcw` and `Trash2` icons.
- Empty state uses the new empty-state primitive.

### Goods Receipt (`/ops/receipts`)

Beyond the primitive cascade:

- `DevNote` is now a refined dev ticket with a stripe-border accent on the left and dot-list body. Still clearly flagged as "TODO — Window 1".

### Waste / Adjustment (`/ops/waste-adjustments`)

The most visible form-level polish:

- **Direction picker** rebuilt from plain card radios into a strict asymmetric pair:
  - Active loss card → accent left bar + accent-soft background + accent-colored custom radio dot.
  - Active positive card → **warning** left bar + warning-soft background + warning-colored radio dot + a prominent "Approval required" pill in the corner.
  - Inactive cards use neutral hover tints.
  - Native `<input type="radio">` is `sr-only` behind a custom-drawn circle so the visual matches the rest of the design system while keeping accessibility.
- The old flat emoji-style layout is gone.

### Physical Count (`/ops/counts`)

Success and variance rendering polished:

- **New `VarianceCard`** — a three-cell grid showing Counted / System / Delta side-by-side. Each cell has an eyebrow, a large mono tabular number, and a unit below. The Delta cell color-codes by sign (success for matched, info for positive delta, danger for negative). Inserted into the `SuccessState` children slot when variance is auto-posted or held.
- `SuccessState` tone now correctly switches between success (matched) and warning (auto / held).

### Admin maintenance screens

These benefited most from the primitive cascade — no per-page rewrite needed. The upgraded `SectionCard`, `SplitListLayout`, `SearchFilterBar`, field primitives, `AuditSnippet`, `LineEditorTable`, and status/badge primitives carry across:

- `/admin/items`, `/admin/components`, `/admin/suppliers`, `/admin/supplier-items`, `/admin/planning-policy`, `/admin/boms`, `/admin/users`, `/admin/jobs`, `/admin/integrations`.
- Lists now use `table-base` with refined header (uppercase eyebrow columns, tabular numerics, hover tint, bordered rows at 40% opacity).
- Detail panels use the new SectionCard with eyebrow + title + description + actions header.
- "read-only for planner" badge and disabled secondary actions from the prior role-tightening round now look intentional, not stubbed.

## Verification gates — all green after the upgrade

| Gate                     | Result                                                       |
|--------------------------|--------------------------------------------------------------|
| `npx tsc --noEmit`       | exit 0                                                       |
| `npx next build`         | 28 static routes prerendered, bundle shared JS 100 kB        |
| `npm test` (Vitest)      | **41 tests, 5 files, all passing** in ~1.6s                  |
| `npm run test:e2e`       | **13 Playwright tests, all passing** in ~32s                 |

Two Playwright tests needed a one-line text-selector update because the top bar's FAKE SESSION label was uppercased and the forecast zero-state text was rewritten — both are legitimate design polish, not behavior regressions. The tests were updated, not the polish reverted.

## Files changed

### New primitives / infra
- `src/app/layout.tsx` — next/font wiring
- `tailwind.config.ts` — full design system
- `src/app/globals.css` — base layer + component classes

### Primitives rewritten
- `src/components/layout/AppShellChrome.tsx`
- `src/components/layout/TopBar.tsx`
- `src/components/layout/SideNav.tsx`
- `src/components/workflow/WorkflowHeader.tsx`
- `src/components/workflow/SectionCard.tsx`
- `src/components/workflow/FormActionsBar.tsx`
- `src/components/workflow/FieldGrid.tsx`
- `src/components/workflow/ValidationSummary.tsx`
- `src/components/workflow/ApprovalBanner.tsx`
- `src/components/workflow/DiffNotice.tsx`
- `src/components/badges/StatusBadge.tsx`
- `src/components/badges/FreshnessBadge.tsx`
- `src/components/badges/ReadinessBadge.tsx`
- `src/components/feedback/states.tsx`
- `src/components/data/SearchFilterBar.tsx`
- `src/components/data/AuditSnippet.tsx`
- `src/components/fields/QuantityInput.tsx`
- `src/components/fields/DateTimeInput.tsx`
- `src/components/fields/NotesBox.tsx`
- `src/components/fields/EntitySearchSelect.tsx`
- `src/components/line-editor/LineEditorTable.tsx`
- `src/components/review/ReviewModePanel.tsx`

### Screens polished on top of primitives
- `src/app/(shared)/dashboard/page.tsx`
- `src/app/(operator)/home/page.tsx`
- `src/app/(operator)/my-submissions/page.tsx`
- `src/app/(operator)/ops/receipts/page.tsx`
- `src/app/(operator)/ops/waste-adjustments/page.tsx`
- `src/app/(operator)/ops/counts/page.tsx`
- `src/app/(planner)/planning/forecast/page.tsx`
- `src/app/(planner)/planning/purchase-recommendations/page.tsx`
- `src/app/(planner)/exceptions/page.tsx`
- `src/app/(planner)/approvals/page.tsx`

### Tests updated to match refined labels
- `tests/e2e/forecast-dirty.spec.ts`

### Dependencies added
- `lucide-react`

## Design decisions worth flagging

1. **Light theme only.** Dark-mode support was not added. For eight-hour operator shifts in a warm bone palette, light is easier on the eyes than a dark theme, and dark theming is a large additional contract (token aliases, two-theme review cycle, printed-export parity). Deferred.

2. **Single-family sans.** I pair Public Sans (UI) with IBM Plex Mono (numerics), not two sans families. Mixing display + body sans is a consumer move; single-family hierarchy reads more operational. Distinctive via the uncommon font choice, not via a clash.

3. **No shadcn CLI.** The primitives layer is hand-rolled on top of custom component classes in `globals.css`. This keeps bundle size and styling surface under Window 2's own control, and the upgraded classes (`.btn`, `.input`, `.chip`, `.card`, `.table-base`) work uniformly without pulling in Radix everywhere. When the canonical `gt-factory-os/portal/` portal eventually needs to reconcile with this, the token layer (Tailwind tokens + classes) is the interoperable surface — not the components themselves.

4. **Tabular numerics globally.** `font-variant-numeric: tabular-nums` is applied at the body level and reinforced on every numeric class. Every quantity, delta, threshold, SKU, timestamp, and version number aligns by column. Non-negotiable for operational trust.

5. **Icons are semantic, not decorative.** Every lucide icon in the shell maps to a specific function (nav item, status, action). No decorative icons in section headers, no "cute" empty-state mascots. One conceptual exception: the faint `Zap` watermark on dashboard tiles (4% opacity — atmosphere).

6. **FAKE SESSION is impossible to miss.** The warning-bordered pill in the top bar pulses a dot and uses uppercase tracked type. The PR explicitly called for visible review-mode and fake-session labels "without making the UI ugly" — the refined pill reads as intentional, not as a sticky note.

7. **Warmer bone background over stark white.** The `hsl(42 18% 95%)` page color tests better for long reads than cold gray, and the subtle dot grid background texture gives the surface weight without interfering with legibility. Turn it off by removing one rule from `globals.css` body if anyone hates it.

## What was intentionally NOT touched

- **Route structure.** Zero changes. Same 28 routes, same layout groups.
- **Business logic.** Forms still submit as mock view-swaps. Repositories still hit IndexedDB. No behavior change except one bug fix surfaced by tests last round.
- **Test coverage depth.** Still 41 vitest + 13 Playwright. No new tests added in this round.
- **Dark theme.** Deferred.
- **i18n infrastructure.** Still English-first; Hebrew appears only in fixture values per CLAUDE.md.
- **Accessibility overhaul.** Kept the existing focus-visible story, respect semantics, no color-only meaning. But did not run an axe audit or add ARIA beyond what was already there.
- **RTL.** Explicitly disallowed. Not touched.
- **Canonical `gt-factory-os/portal/`** — remains a separate, untouched work stream per the committed coordination note in that repo.
- **Dropbox reference copy** (`PRODUCTION/portal/`) — still points at `C:/Users/tomw2/Projects/window2-portal-sandbox/` via REDIRECT.md and is not receiving edits.

## How to see the upgrade

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox
npm install             # if not already installed in the sandbox path
npm run dev             # → http://localhost:3000
```

First-run path to feel the difference:

1. Land on `/dashboard`. Notice the dot-grid background, the petrol accent, the reveal animation on the header, the tile composition, the shortage-risk list.
2. Click `Forecast` in the side nav. The grid has sticky left column, gradient family headers, glow-on-focus cell editors, and the raised form action bar at the bottom.
3. Click `Purchase recs`. Grouped supplier panels, urgency flame, row-selection tint.
4. Switch the FAKE SESSION role to `operator` via the top-bar chip. Watch the nav flip entirely.
5. Open `Waste / Adjustment`. Click the "Positive correction" card — the warning accent bar snaps in, the "Approval required" pill appears, and the approval banner updates at the bottom of the form as you change quantity.
6. Open `Physical Count`. Submit any value against an item. The success state renders a three-cell variance card with colored delta.
7. Open the Review-mode button in the top bar. Force the receipts page into every state — empty, validation error, success, approval required, stale conflict — and feel that the state transitions look intentional.

_End of design upgrade pass._
