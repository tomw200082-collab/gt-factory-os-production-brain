# Window 2 — Design Transfer Package

_2026-04-14 · handoff after approved design pass · closes Window 2 design iteration_

This document is written for someone who wants to adopt the Window 2 visual system **inside a different repo** — primarily the canonical `gt-factory-os/portal/` Tranche 1 Step 2 stream — without reading any sandbox TypeScript. It is portable by design.

Precedence:

- The tokens in §1 are the single source of truth. Any Tailwind config in the sandbox is a downstream implementation of them.
- The components in §2 are named by shape, not by implementation. A "SectionCard" can be re-built in shadcn `Card` + `CardHeader` without any contract loss.
- The screens in §3 are named by pattern (e.g. "split-list-with-sticky-detail"), not by sandbox routes.

---

## 1. Design system handoff

Aesthetic direction: **"Operational Precision."** Modern control tower. Premium B2B. Tuned for eight-hour shifts without eye fatigue. Warm bone paper + graphite ink + one petrol-teal accent + muted semantic colors + single-family sans + operational density.

### 1.1 Color tokens

All values are HSL. Use them however your stack prefers (CSS variables, tailwind config, design-token JSON). Names are semantic; opacity suffixes (`/70`, `/40`) express border weight, not new colors.

#### Surfaces (warm bone — not cold white)

| Token            | Value                        | Use case                                                     |
|------------------|------------------------------|--------------------------------------------------------------|
| `bg`             | `hsl(42 18% 95%)`            | Page background. Warm bone paper.                            |
| `bg.subtle`      | `hsl(42 16% 92%)`            | Section tint, table header, section card footer.            |
| `bg.muted`       | `hsl(42 14% 88%)`            | Disabled well, inactive chip background.                     |
| `bg.raised`      | `hsl(42 20% 98%)`            | Card interior — slightly brighter than page.                 |
| `bg.deep`        | `hsl(40 10% 86%)`            | Deepest tint for nested wells (rare).                        |

#### Ink (warm near-black graphite)

| Token            | Value                        | Use case                                                     |
|------------------|------------------------------|--------------------------------------------------------------|
| `fg.strong`      | `hsl(30 14% 6%)`             | Page titles (h1), key numeric values.                        |
| `fg`             | `hsl(30 10% 10%)`            | Primary body text.                                           |
| `fg.muted`       | `hsl(30 6% 38%)`             | Secondary text, row descriptions, hint text above faint.    |
| `fg.subtle`      | `hsl(30 5% 54%)`             | Tertiary text, eyebrow labels.                               |
| `fg.faint`       | `hsl(30 4% 68%)`             | Placeholder, rule text, em-dashes, icon rest state.         |
| `fg.inverted`    | `hsl(42 20% 98%)`            | Text on the petrol accent or dark tones.                     |

#### Borders (hairlines at calibrated opacity)

| Token            | Value                        | Use case                                                     |
|------------------|------------------------------|--------------------------------------------------------------|
| `border`         | `hsl(30 8% 82%)`             | Default 1px rule. Apply at `/70` opacity for card borders.   |
| `border.strong`  | `hsl(30 10% 70%)`            | Hover-state borders. Heavier rules.                          |
| `border.faint`   | `hsl(30 8% 88%)`             | Softest divider (list separators at 40% opacity).            |

> Convention: cards use `border/70`. Row separators use `border/40` or `border/60`. Input hover uses `border-strong`. Solid fully-opaque borders are rare.

#### Signature accent — petrol teal

| Token              | Value                      | Use case                                                     |
|--------------------|----------------------------|--------------------------------------------------------------|
| `accent`           | `hsl(186 42% 24%)`         | Primary button, active nav, focused input ring, links.       |
| `accent.hover`     | `hsl(186 44% 20%)`         | Primary button hover.                                        |
| `accent.soft`      | `hsl(186 38% 94%)`         | Selected row, active chip, primary button soft fill.         |
| `accent.softer`    | `hsl(186 40% 97%)`         | Barest background tint.                                      |
| `accent.border`    | `hsl(186 32% 40%)`         | Outline variants of accent buttons.                          |
| `accent.fg`        | `hsl(42 20% 98%)`          | Text on accent.                                              |
| `accent.ring`      | `hsl(186 42% 24% / 0.3)`   | Focus ring offset color.                                     |

Not "cornflower blue" or "azure" or "stock Tailwind blue-600." Petrol is the signature — swap at your peril.

#### Semantic colors (restrained, muted)

Each semantic has `DEFAULT`, `soft`, `softer`, `fg`, `border`.

| Role       | DEFAULT              | soft              | softer             | fg (on-soft)      | border            |
|------------|----------------------|-------------------|--------------------|-------------------|-------------------|
| `success`  | `hsl(146 34% 30%)`   | `hsl(146 30% 94%)`| `hsl(146 30% 97%)` | `hsl(146 40% 20%)`| `hsl(146 28% 60%)`|
| `warning`  | `hsl(32 78% 42%)`    | `hsl(38 80% 94%)` | `hsl(38 84% 97%)`  | `hsl(28 82% 28%)` | `hsl(34 70% 62%)` |
| `danger`   | `hsl(4 66% 40%)`     | `hsl(4 60% 94%)`  | `hsl(4 60% 97%)`   | `hsl(4 70% 30%)`  | `hsl(4 56% 60%)`  |
| `info`     | `hsl(210 32% 38%)`   | `hsl(210 30% 94%)`| `hsl(210 32% 97%)` | `hsl(210 40% 26%)`| `hsl(210 26% 58%)`|

Use `fg` variants for text on `soft` backgrounds (passes WCAG AA comfortably). Use `DEFAULT` for dots, bars, icon chips. Never use plain red `#ff0000` or cartoon green `#00ff00`.

#### Atmosphere

Body has a faint **dot-grid background texture** at ~35% of `bg.muted`, 24px grid pitch, fixed. This gives surfaces weight without interfering with legibility.

```css
body {
  background-image: radial-gradient(
    circle at 1px 1px,
    hsl(30 10% 80% / 0.35) 1px,
    transparent 0
  );
  background-size: 24px 24px;
  background-attachment: fixed;
}
```

### 1.2 Typography scale

Single-family sans + mono pairing. No display serif. No mixing two sans families.

- **Sans:** `Public Sans` (GSA-backed, open source, Google Fonts). Weights 400, 500, 600, 700, 800.
- **Mono:** `IBM Plex Mono` (IBM open source, Google Fonts). Weights 400, 500, 600.

Tabular numerics globally via `font-variant-numeric: tabular-nums` on `html`, `body`, `input[type="number"]`, `.font-mono`, `.tabular-nums`.

**Base size: 14px** (not 16px). Operational density.

#### Scale

| Name   | Size      | Line height | Letter spacing | Use                                      |
|--------|-----------|-------------|----------------|------------------------------------------|
| `3xs`  | 10px      | 14px        | +0.04em        | Uppercase micro-labels, row indices.     |
| `2xs`  | 11px      | 16px        | +0.02em        | Chip text, field labels, eyebrows.       |
| `xs`   | 12px      | 17.6px      | 0              | Secondary body, hint text, timestamps.   |
| `sm`   | 13px      | 19.2px      | 0              | Compact body, section descriptions.      |
| `base` | 14px      | 21.6px      | 0              | Default body, row content, form inputs.  |
| `md`   | 15px      | 23.2px      | 0              | Emphasised row text.                     |
| `lg`   | 17px      | 24.8px      | 0              | Section titles, modal titles.            |
| `xl`   | 20px      | 28px        | 0              | Large numerics in tiles.                 |
| `2xl`  | 24px      | 31.2px      | −0.01em        | Subsection hero.                         |
| `3xl`  | 30px      | 36.8px      | −0.015em       | Page titles (workflow header h1).        |
| `4xl`  | 36px      | 41.6px      | −0.02em        | Dashboard tile values (mono tabular).    |

#### Letter-spacing tokens

| Name       | Value     | Use                                                                |
|------------|-----------|--------------------------------------------------------------------|
| `tightish` | −0.01em   | Section card titles, sidebar active labels.                        |
| `tight`    | −0.015em  | Workflow header titles.                                            |
| `tighter`  | −0.02em   | Page-level tiles with large mono numerics.                         |
| `ops`      | +0.08em   | Small uppercase eyebrow labels.                                    |
| `sops`     | +0.12em   | Thinner uppercase micro-labels (table headers, field labels).      |

#### Font weights — typical composition

| Element                     | Weight |
|-----------------------------|--------|
| Body text                   | 400    |
| Row name / label default    | 500    |
| Section titles, strong text | 600    |
| Page titles, tile values    | 600    |
| Uppercase eyebrows          | 600    |
| Active nav label            | 600    |

> Rule: hierarchy comes from weight + size + tracking, not from a second font family.

### 1.3 Spacing scale

4px grid. Standard Tailwind scale (`1 = 4px, 2 = 8px, …`) plus these half-steps:

| Name | Pixels |
|------|--------|
| `4.5` | 18px |
| `5.5` | 22px |
| `6.5` | 26px |
| `7.5` | 30px |
| `13`  | 52px |
| `15`  | 60px |
| `17`  | 68px |
| `18`  | 72px |
| `22`  | 88px |

> Used for precise shell padding (`py-8 xl:py-10`), sticky nav offsets (`top-[88px]`), and card header rhythm. The half-steps exist so 18px labels don't fall between 16 and 20.

### 1.4 Radius, border, shadow rules

#### Radius

| Token  | Value | Use                                                         |
|--------|-------|-------------------------------------------------------------|
| `xs`   | 3px   | `kbd`, small chips, inset affordances.                      |
| `sm`   | 4px   | Badges, chip buttons, table cell frames.                    |
| `DEFAULT` / `md` | 6px | Cards, inputs, buttons, table containers.              |
| `lg`   | 8px   | Modals, success state cards.                                |
| `xl`   | 12px  | (rarely used — do not adopt for standard surfaces.)         |
| `2xl`  | 16px  | (reserved — not currently used in the sandbox.)             |

> Default = 6px. This is sharper than Tailwind's default 8px and is part of the operational vibe. Match it.

#### Border rules

- 1px hairlines everywhere. No thicker rules.
- Card borders: `border/70` (70% opacity).
- Row separators: `border/40` or `border/60`.
- Input resting: `border/80`. Hover: `border-strong`. Focused: `border.focus` (= accent).
- Group dividers: gradient rule `linear-gradient(to right, border, border/50, transparent)` — used at the bottom of workflow headers for a more editorial close.

#### Shadow tokens

| Token              | Value                                                                                                   | Use                                   |
|--------------------|---------------------------------------------------------------------------------------------------------|---------------------------------------|
| `raised`           | `0 1px 0 0 hsl(30 10% 80% / 0.4), 0 1px 2px 0 hsl(30 12% 10% / 0.04)`                                   | Default card. Barely there.           |
| `pop`              | `0 2px 6px -1px hsl(30 12% 10% / 0.06), 0 8px 24px -4px hsl(30 12% 10% / 0.08), 0 0 0 1px hsl(30 10% 80% / 0.5)` | Dropdowns, modals, select menus.   |
| `focus-ring`       | `0 0 0 3px hsl(186 42% 24% / 0.18)`                                                                     | Focus ring on inputs and buttons.     |
| `danger-ring`      | `0 0 0 3px hsl(4 66% 40% / 0.18)`                                                                       | Focus ring on destructive inputs.     |
| `hairline`         | `0 0 0 1px hsl(30 8% 82%)`                                                                              | Inset hairline (replacement for border on some atoms). |

> Elevation is mostly contrast. Cards sit above the page because they are **brighter than the page**, not because they throw a shadow.

### 1.5 Motion rules

- **Base timing:** `150ms` for all hover, focus, press, row-tint, chip-toggle.
- **Enter curve:** `cubic-bezier(0.165, 0.84, 0.44, 1)` (sandbox name: `ease-out-quart`).
- **Alt curve:** `cubic-bezier(0.19, 1, 0.22, 1)` (`ease-out-expo`) for longer reveals.
- **Page reveal:** workflow headers fade-in-up 320ms on first mount. Tiles can stagger with 40ms delay per item up to 6 items. Never stagger more than 6.
- **Live status pulse:** `pulse-soft 2.4s ease-in-out infinite` — opacity `1 → 0.55 → 1`. Used for pending states and live dots.
- **Forbidden:** spring bounces, elastic overshoots, page-level parallax, skeleton shimmer, typed-in-cursor, rainbow accents.

### 1.6 Icon rules

- **Library:** `lucide-react`. No other icon library. No emoji as UI.
- **Stroke:** `1.75` default, `2` for active/bold states, `2.5` for check/close micro-icons inside tight chips.
- **Size:** `12px` (inside 10–11px chips), `14px` (inside buttons, next to 13px text), `16px` (section headers, feedback state chips).
- **Never decorative.** One icon per nav item, per status, per button. Icons always paired with text OR carry an `aria-label`.
- **One atmospheric exception:** dashboard tiles may include a single faint watermark icon at ~4% opacity (the `Zap` on Window 2's dashboard tile shell). Use sparingly.

#### Canonical icon mapping

This is the sandbox's assignment list. Keep it consistent when porting:

| Function             | Icon              |
|----------------------|-------------------|
| Dashboard            | `LayoutDashboard` |
| Exceptions           | `TriangleAlert`   |
| Home (operator)      | `Home`            |
| Goods Receipt        | `PackageOpen`     |
| Waste / Adjustment   | `Sliders`         |
| Physical Count       | `ClipboardCheck`  |
| Production Actual    | `Factory`         |
| My Submissions       | `Inbox`           |
| Forecast             | `LineChart`       |
| Purchase Recs        | `ShoppingCart`    |
| Production Recs      | `Hammer`          |
| Approvals            | `CheckSquare`     |
| PO                   | `FileText`        |
| Items                | `Package`         |
| Components           | `Cog`             |
| BOMs                 | `Network`         |
| Suppliers            | `Building2`       |
| Supplier items       | `Link2`           |
| Planning policy      | `Sliders`         |
| Users                | `Users`           |
| Jobs                 | `Activity`        |
| Integrations         | `Plug`            |

Status icons: `AlertCircle` (critical/error), `AlertTriangle` (warning), `Info` (info), `CheckCircle2` (success), `XOctagon` (blocker), `ShieldCheck` (policy), `Clock` (time), `RefreshCw` (stale/reload), `Lock` (blocked).

### 1.7 Density rules

- **Base font:** 14px. Tables, inputs, buttons, and row text default to `sm` (13px) or `base` (14px) — never larger for body.
- **Row height:** 36–40px for data rows. Dense tables can drop to 32px with `table-dense` modifier.
- **Input height:** 36px (`h-9`). Small inputs: 28px (`h-7`). Mini: 24px (`h-6`). Large: 40px (`h-10`).
- **Card body padding:** 20px comfortable, 16px compact.
- **Card header padding:** 20px horizontal, 16px vertical.
- **Table cell padding:** `px-3 py-2.5` comfortable, `px-3 py-1.5` compact.
- **Page padding:** 32px horizontal, 32px vertical (xl: 40/40).
- **Section gap:** 20–24px between stacked sections.
- **Field gap:** 20px between form fields in a grid.

> Density is load-bearing. A 16px base will visibly break the rhythm; do not upscale for "accessibility" — legibility comes from weight/contrast calibration, not from inflating the base.

### 1.8 Page-shell rules

- **Max width:** 1440px centered.
- **Top bar:** 64px tall, sticky top, `bg/85` + `backdrop-blur-md`, border-bottom `border/70`, z-index 40. Contains: brand mark, app title + eyebrow, optional global status strip (live dots), review button, separator rule, fake-session pill (or real session pill in production).
- **Side nav:** 232px wide, sticky at `top-[88px]` (top bar + 24px), flex column, no scroll container (scroll with page).
- **Main:** `flex-1`, `min-w-0`, bottom padding 64px (for sticky form action bars not to cover content).
- **Gap between nav and main:** 40px.
- **Reveal:** root page content (workflow header) fades in-up 320ms on mount.

### 1.9 Card / surface rules

- **Card:** `bg-raised` background, `border/70` border, `shadow-raised`, radius 6px, overflow-hidden when it has a bordered header.
- **Header:** 20px horizontal, 16px vertical, bottom-border `border/70`, subtle `bg-gradient-to-b from-bg-raised to-bg/40` to catch light.
  - Eyebrow row (optional, `3xs` uppercase `ops` tracking, `fg-subtle`).
  - Title row (`base` weight 600 tracking `tightish`, `fg-strong`).
  - Description row (optional, `xs` `fg-muted`).
  - Right-aligned actions (button row).
- **Body:** `p-5` comfortable, `p-4` compact, override with `contentClassName="p-0"` for table content.
- **Footer** (optional): `bg-subtle/60`, top-border `border/70`, `px-5 py-3`, `xs` text `fg-muted`.
- **Tone variants:** `default` / `warning` / `danger` / `info` / `success`. Each swaps the border color to the matching semantic at 50% opacity. Body stays neutral.

> Cards never stack shadows. A card inside a card has no extra shadow — only a border.

### 1.10 Table / list rules

- **Base:** `border-collapse`, `text-sm`, `text-left`.
- **Thead row:** `bg-subtle/60`, `border-b border`. `th` cells: `px-3 py-2`, `text-3xs` uppercase `sops` tracked `text-fg-subtle`, no bold weight increase beyond 600.
- **Tbody row:** `border-b border/40` or `border/60`. `py-2.5` comfortable, `py-1.5` compact. Hover `bg-subtle/60`. Selected (via `data-selected="true"`) `bg-accent-soft/70`.
- **td:** `px-3 py-2.5` align-middle, `text-sm` for values, `font-mono tabular-nums` for numerics.
- **First column:** can be sticky-left with `sticky left-0 z-[1] bg-raised` for wide grids.
- **Row numbers (line editors):** `font-mono text-3xs tabular-nums text-fg-faint`, zero-padded (`01`, `02`).

### 1.11 Form rules

- **Labels:** `mb-1.5 flex items-center justify-between`, inner text `text-2xs font-semibold uppercase tracking-sops text-fg-muted`. Required marker: `<span class="text-danger">*</span>`. Optional marker: right-aligned `text-3xs text-fg-faint` lowercase "optional".
- **Input (`h-9`):** radius 6px, `border border/80`, `bg-raised`, `px-3 text-sm`, placeholder `fg-faint`. Hover → `border-strong`. Focus → `border.focus` (= accent) + focus ring (shadow `0 0 0 2px bg, 0 0 0 4px accent/0.4`). Disabled → `bg-subtle text-fg-muted cursor-not-allowed`.
- **Textarea:** `min-h-[80px]` otherwise identical to input. Line-height `relaxed`.
- **Error state:** `border-danger/80 bg-danger-softer/40`. Error message line under the field: `mt-1 flex items-center gap-1 text-xs text-danger-fg` with inline `AlertCircle` icon.
- **Hint line:** `mt-1 text-xs text-fg-subtle`.
- **Field grid:** `grid gap-x-5 gap-y-5` with column count 1/2/3/4 by breakpoint. Span modifiers for wide fields (`sm:col-span-2`).
- **Number inputs:** always tabular font, Chrome spinner arrows stripped (`-webkit-appearance: none`).
- **Number input with unit:** right-side segmented chip with a left hairline separator inside the input's padding area — unit reads as part of the field.

### 1.12 Badge / state rules

- **Shape:** rounded-sm (4px), 1px border, `px-1.5 py-0.5`, `text-3xs` uppercase tracked `sops`.
- **Composition:** dot + label. `<span class="dot bg-<semantic>" /> Label`. The dot is the signal; the pill is low-chrome.
- **Three variants:**
  - `soft` — background at `soft` (94% L), text at `fg`, border at `30%` opacity. Default.
  - `outline` — transparent background, text at `fg`, border at `40%` opacity.
  - `solid` — `DEFAULT` background, white text, `DEFAULT` border. Used for high-emphasis (critical urgency flame).
- **Semantic tones:** `neutral` / `accent` / `success` / `warning` / `danger` / `info`.
- **Status badge (submission states):** always dot + label. Live states (`submitting`, `pending_approval`) pulse the dot softly. Terminal states (`committed`, `approved`, `rejected`) are static. `discarded` strikes through the label.
- **Freshness badge:** clock icon + eyebrow label + hairline separator + tabular "Xm ago" + semantic dot (green <warn, amber warn-fail, red fail). Compact variant drops the outer border.
- **Readiness badge:** dot + label + right-aligned status code (`OK` / `WARN` / `FAIL` / `?`).

### 1.13 Eyebrow / micro-label

Used pervasively for hierarchy:

```css
.eyebrow {
  font-size: 11px;          /* 2xs */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;   /* sops */
  color: var(--fg-subtle);
}
```

An eyebrow often pairs with a small dot or an icon to catch the eye: `<span class="dot bg-accent" /> Planning workspace`.

### 1.14 Dev affordances (carry-over rules)

- Review mode, fake session pill, and the operator "FAKE SESSION" warning chip all use the `warning` palette + a pulsing dot — deliberately loud so they cannot be confused with real auth or real production states.
- Dev notes use a striped border accent (diagonal `repeating-linear-gradient`) + `bg-subtle/40` + dashed border. Clearly "not product."

---

## 2. Component mapping

For each upgraded primitive: what it is, where it's used, whether it's portable as-is, what (if any) sandbox logic it depends on, and the adoption recommendation.

**Legend — adoption recommendation:**
- **Copy** — take the component whole, swap tokens, use it.
- **Adapt** — keep the visual shape, rewrite the implementation on top of the canonical portal's existing primitive conventions (Radix/shadcn, `PermissionGuard`, `WriteContext`).
- **Reimplement** — the concept transfers but the component is too sandbox-coupled; build fresh under the canonical's conventions.
- **Do not transfer** — sandbox-only concept; deliberately leave behind.

| Component            | Purpose                                                                 | Used on                                                                 | Portable as-is? | Sandbox-only deps                                            | Recommendation    |
|----------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|-----------------|--------------------------------------------------------------|-------------------|
| `AppShellChrome`     | Top bar + left nav + main frame wrapper                                 | All authenticated routes                                                | Yes (layout only) | None — pure layout                                         | **Copy**          |
| `TopBar`             | Brand mark + global status strip + review button + session pill         | All routes                                                              | Partial         | `useSession`→fake-auth, `useReviewMode`, FAKE SESSION pill   | **Adapt** — keep brand/status/pill shape; swap session source for the canonical `AuthProvider`; drop review button outside sandbox |
| `SideNav`            | Role-aware nav with icons, active accent bar, blocked markers, "You are" footer | All authenticated routes                                         | Partial         | `useSession`→fake-auth, hard-coded 28-route list, "blocked" concept | **Adapt** — keep icon+accent-bar pattern and group rhythm; rebuild the nav list against the canonical routes; drop "blocked" if the canonical doesn't have that concept |
| `WorkflowHeader`     | Eyebrow + title + description + meta + actions + hairline rule          | Every screen                                                            | **Yes**         | None                                                         | **Copy**          |
| `SectionCard`        | Titled content card with gradient header, tones, densities              | Every non-trivial screen                                                | **Yes**         | None                                                         | **Copy**          |
| `FormActionsBar`     | Sticky floating action footer                                           | All forms + forecast workspace                                          | **Yes**         | None                                                         | **Copy**          |
| `FieldGrid` + `Field`| Form field layout grid with uppercase labels + errors + hints           | Every form                                                              | **Yes**         | None                                                         | **Copy**          |
| `ValidationSummary`  | Stacked blocker/warning list with semantic accent bar                   | Operator forms, admin detail forms                                      | **Yes**         | Depends on a `ValidationIssue` shape (trivial type)          | **Copy**          |
| `ApprovalBanner`     | Policy-trigger callout with title + reason + policy key                 | Operator forms, forecast, BOM panels                                    | **Yes**         | None                                                         | **Copy**          |
| `DiffNotice`         | Stale/diff banner with reload + dismiss                                 | Forecast workspace, purchase recs                                       | **Yes**         | None                                                         | **Copy**          |
| `StatusBadge`        | Submission-state dot + label                                            | My submissions, operator home                                           | Partial         | `SubmissionState` enum — sandbox-defined                     | **Adapt** — copy the visual; swap the state enum to whatever the canonical submission model lands on |
| `Badge` (generic)    | Generic semantic badge (soft/outline/solid + dotted)                    | Everywhere                                                              | **Yes**         | None                                                         | **Copy**          |
| `FreshnessBadge`     | Time-since + semantic health dot                                        | Dashboard, forecast meta, jobs monitor                                  | **Yes**         | None — takes any ISO timestamp                               | **Copy**          |
| `ReadinessBadge`     | OK/WARN/FAIL status with label + detail                                 | Dashboard readiness tile                                                | **Yes**         | None                                                         | **Copy**          |
| `EmptyState`         | Framed placeholder with icon chip + dot-grid texture                    | Lists, inboxes                                                          | **Yes**         | None                                                         | **Copy**          |
| `LoadingState`       | Centered spinner card                                                   | Loading branches                                                        | **Yes**         | None                                                         | **Copy**          |
| `ErrorState`         | Danger-bordered card with icon chip                                     | Error branches                                                          | **Yes**         | None                                                         | **Copy**          |
| `SuccessState`       | Success/warning/info framed card with icon chip + slot for children    | Form success, variance card wrap                                        | **Yes**         | None                                                         | **Copy**          |
| `StaleNotice`        | Inline stale/conflict banner                                            | Receipts stale branch                                                   | **Yes**         | None                                                         | **Copy**          |
| `SearchFilterBar`    | Search input with clear-X + dot-accented filter chips                   | Every list view                                                         | **Yes**         | None                                                         | **Copy**          |
| `AuditSnippet`       | Four-cell audit metadata grid (created/updated/version/status)          | Admin detail panels                                                     | Partial         | `AuditMeta` shape — sandbox-defined but trivial              | **Copy** (rename the type if canonical differs) |
| `QuantityInput`      | Number input with right-side unit chip                                  | Operator forms, BOM line editor                                         | Partial         | `Uom` enum — sandbox-defined                                 | **Copy** (swap the Uom type) |
| `DateTimeInput`      | `datetime-local` wrapper with mono tabular font                         | Operator forms                                                          | **Yes**         | None                                                         | **Copy**          |
| `NotesBox`           | Styled textarea wrapper                                                 | Operator forms, admin                                                   | **Yes**         | None                                                         | **Copy**          |
| `EntitySearchSelect` | Search-and-pick dropdown with label + sublabel + optional hint          | Admin BOM component picker (designed for wide use)                      | **Yes**         | None — takes generic `EntityOption`                          | **Copy**          |
| `LineEditorTable`    | Generic repeating-row editor with add/remove + row numbers              | Receipts, BOM editor, PO form                                           | **Yes**         | None — generic on `T`                                        | **Copy**          |
| `ReviewModePanel`    | Dev panel to force screen states and swap fixture sets                  | Global (dev only)                                                       | No              | Entirely sandbox — `useReviewMode`, `ScreenState` enum       | **Do not transfer** |
| `StatePreviewChip`   | Chip shown when review mode is forcing a state                          | Operator forms                                                          | No              | Sandbox only                                                 | **Do not transfer** |

### Shared-logic primitives (for completeness)

These are not visual primitives but are referenced by components. They have their own portability story:

| Utility           | Portable? | Recommendation                                                                 |
|-------------------|-----------|--------------------------------------------------------------------------------|
| `cn()` (classname merge) | Yes | Copy. Standard `clsx` + `tailwind-merge` combo.                          |
| `useHasRole()`    | Adapt     | The canonical portal has `PermissionGuard` + `WriteContext`. Don't port the hook; use the canonical's equivalent at the same call sites. |
| `useSession()`    | Adapt     | Sandbox uses fake auth. Canonical uses `AuthProvider`. Same interface in spirit — rename if helpful. |
| `useForcedOr()`   | No        | Review-mode only. Do not transfer.                                             |

---

## 3. Screen transfer priority

Ranked by **cost-to-transfer vs. visual payoff**, assuming the canonical portal already has its D2 shared primitives layer.

### Tier A — transfer first (high value, low friction)

These are the screens where the design language most obviously lifts the product, and they transfer cleanly because their underlying contract is pure master-data CRUD (which the canonical portal is already building in Tranche 1).

| Screen pattern                          | Sandbox reference               | Why first                                                                                         |
|-----------------------------------------|---------------------------------|---------------------------------------------------------------------------------------------------|
| **Admin master-maintenance split view** | `/admin/items` (template)       | Split list + detail pane is the core of master maintenance. Upgraded `SectionCard` + `SearchFilterBar` + `AuditSnippet` carry 90% of the visual lift for free. All admin pages are the same pattern so one port spreads across six screens. |
| **Admin table/list chrome**             | `/admin/items` list view        | Upgraded `.table-base` class. Once adopted, every admin list screen looks right.                   |
| **Admin form detail pane**              | `ItemDetailPanel` shape         | `FieldGrid` + `Field` + `FormActionsBar` + `ValidationSummary` + `AuditSnippet` drop straight in. |
| **Dashboard tile + hero row**           | `/dashboard` tile set           | Even without the exact metrics, the tile composition (eyebrow + mono value + accent pct bar + dotted badges + atmosphere watermark) is a template the canonical can reuse the day it has any read model to display. |
| **Freshness + readiness cluster**       | `/dashboard` right rail         | Boundary-system health is universal. Component set ports directly. |

### Tier B — transfer after Tier A (medium value, some adaptation)

These need more adaptation but are worth doing once the tokens and primitives are in place.

| Screen pattern                          | Sandbox reference                           | Why second                                                                                           |
|-----------------------------------------|---------------------------------------------|------------------------------------------------------------------------------------------------------|
| **Grouped decision queue**              | `/planning/purchase-recommendations`        | The supplier-grouped selection-with-indeterminate-master-checkbox pattern is genuinely novel and operationally sharp. Transfer after the planning engine at least proposes data.     |
| **Forecast grid with sticky columns**   | `/planning/forecast`                        | High value but visually complex. Transfer after the forecast API exists — the grid's sticky-column + focus-glow + family-group pattern is worth the effort. |
| **Split-severity expand list (inbox)**  | `/exceptions`                               | Row-expand + left-accent-bar + icon-chip + recommended-action card is a clean pattern. Transfers once the canonical has an exceptions source. |
| **Grouped approval cards**              | `/approvals`                                | Kind-grouped approvals with payload disclosure. Transfer once the canonical has an approvals source. |

### Tier C — transfer only when backend contract is live

| Screen pattern                          | Reason to wait                                                                                          |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------|
| **Operator form shells** (receipt, waste, count) | The form layout is Tier A quality, but the operator surface is meaningful only once Window 1's ledger contracts exist. Transferring the shell prematurely creates a false "we have receipts" signal. |
| **Physical count variance card**        | The three-cell counted/system/delta card is great, but it ties directly to the server-side variance decision (auto-post vs approval). Port only after the decision model is locked. |
| **PO Form**                             | Downstream of approved recommendations. No point porting until the planning→PO stage model exists.     |
| **My submissions / outbox**             | Depends on a real outbox reconciler and real submission state machine. Port after outbox envelope is wired. |

### Tier D — do not transfer

| Screen / component                      | Why                                                                                                     |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------|
| `ReviewModePanel`, `StatePreviewChip`   | Entirely sandbox review tooling. No reason to exist in the canonical portal.                           |
| `FAKE SESSION` pill                     | Sandbox auth affordance. Canonical has real auth.                                                      |
| "blocked" nav chips                     | Sandbox-only concept for shell readiness. Canonical doesn't model "blocked routes" the same way.       |
| Dev notes (`DevNote` helper in receipts)| Sandbox-only. Strip on port.                                                                            |
| Hard-coded fixture data                 | Obviously.                                                                                              |

---

## 4. Canonical-portal fit note

The canonical `gt-factory-os/portal/` is a different work stream at D2 (shared primitives) stage. It uses a different architecture (Radix + shadcn primitives, `shared/` layout, `AuthProvider` + `PermissionGuard` + `WriteContext`, mocked `api-client` + `read-model-hooks`). This section explains which parts of the Window 2 design upgrade will cross that boundary cleanly and which will not.

### 4.1 Architecture-agnostic (transfers to any React/Tailwind stack)

These are token-level decisions and component shapes that don't care about the surrounding architecture. You could port these into Next.js + Radix, into Remix + Ark, into Vite + anything:

- **The full color token system** (§1.1) — just CSS variables or a design-token JSON.
- **Typography pair** (Public Sans + IBM Plex Mono) and the 11-step scale.
- **Spacing scale** (4px grid + half-steps).
- **Radius / border / shadow rules.**
- **Motion system** (timings, curves, reveal animation).
- **Icon library choice** (`lucide-react`) and the canonical icon mapping.
- **Density rules** (14px base, row heights, input heights, padding rhythm).
- **Card shape rules**, **table shape rules**, **form shape rules**, **badge shape rules** — as visual contracts, not as specific components.
- **Dot-grid body background**.
- **"Eyebrow" micro-label pattern**.
- **Dot-driven status semantics** (`<dot /> Label` composition).
- **Tabular numerics everywhere** discipline.
- **Focus-ring style** (accent at 0.4 opacity, 3px).

These are the cheapest to port and the highest-leverage. **Adopt these first, in any order.**

### 4.2 Tightly coupled to the sandbox route/layout structure

These depend on the sandbox's specific routes, auth, or layout groups, and will need real adaptation even when the component itself is visually reusable:

- **`TopBar`** — the FAKE SESSION pill, the review-mode button, and the live status strip (`Ledger OK · Jobs 2 warn · v0.1.0`) are sandbox affordances. The brand mark + global status pattern + slot on the right transfers; the specific slots do not.
- **`SideNav`** — the 28-route nav list, the "blocked" chip pattern, and the "You are" footer card are sandbox-specific. The group-header + icon + accent-bar active state pattern is portable.
- **Review-mode plumbing** — `useForcedOr`, `StatePreviewChip`, any component that reads from `ReviewModeProvider`. Strip entirely on port.
- **Operator `(operator)/layout.tsx` with strict role gating** — the gating pattern transfers to `PermissionGuard`, but the specific role strings come from sandbox fake-auth. Rewrite at the boundary.
- **`useHasRole`** — call sites transfer, the hook does not. Replace with the canonical portal's equivalent.
- **`SplitListLayout`** — this is a simple grid wrapper but it assumes the sandbox's detail-panel state machine (`{ kind: "closed" | "create" | "edit" }`). Copy the layout, rewrite the state to fit the canonical's patterns.

### 4.3 Likely conflicts with the canonical portal

Things that the canonical portal already has and will almost certainly clash with:

- **Primitive philosophy.** The canonical portal uses Radix + shadcn. The Window 2 primitives are hand-rolled on custom CSS classes (`.btn`, `.input`, `.card`, `.table-base`). These two approaches are not directly composable — `<Dialog>` from Radix has a different API than a custom modal. **Adoption strategy:** port the **tokens** into the canonical's Tailwind config and restyle the canonical's existing Radix/shadcn components using those tokens. Do not copy the Window 2 components whole; their .btn/.input class-based shape will fight the canonical's `Button` / `Input` Radix components.
- **Permission model.** The canonical uses `PermissionGuard` + `WriteContext`. Window 2 uses `RoleGate` + `useHasRole`. Same shape, different API. Whichever the canonical has is authoritative — do not introduce `useHasRole` into the canonical repo.
- **Session model.** The canonical has `AuthProvider` + `RoleSwitcher` (its own dev-time affordance). Window 2 has `SessionProvider` + fake-auth pill. Use the canonical's.
- **Form stack.** Both repos picked `react-hook-form` + `zod`. No conflict here — the only thing to port is the **visual composition** of `FieldGrid` / `Field` / `ValidationSummary` on top of whatever form primitives the canonical already has.
- **Test runner.** Both use Vitest. No conflict.
- **Layout folder shape.** The canonical has `src/shared/layout/` (AppShell, TopBar, Sidebar, MaintenanceBanner). Window 2 has `src/components/layout/`. Use the canonical's placement.

### 4.4 Safest adoption sequence

**Step 1 — Tokens only, zero components (1 day).**  
Drop §1.1–§1.5 into the canonical portal's `tailwind.config.ts` and `globals.css`. No component edits. The existing shadcn primitives now render in warm bone / petrol / Public Sans + IBM Plex Mono. This alone delivers 60% of the visual lift. Run the canonical's existing tests to verify nothing regresses.

**Step 2 — Typography wiring (1 hour).**  
Install Google Fonts via `next/font` in the canonical layout. Add `--font-public-sans` and `--font-plex-mono` variables. Update the canonical's body font to Public Sans.

**Step 3 — Restyle the canonical's Radix primitives (1 day).**  
`Button`, `Input`, `Label`, `Card`, `Dialog`, `Select`, `Tabs` — adjust class bindings to match §1.4, §1.9, §1.11. Do not replace the components, just update their styling to match the token system. The canonical's existing tests for those components continue to pass.

**Step 4 — Adopt Tier A screen patterns (2–3 days).**  
Apply the dashboard tile composition, the admin split-view layout, the filter-bar chip pattern, the audit snippet grid. No new components — just compose the canonical's Radix primitives into these patterns.

**Step 5 — Adopt Tier B patterns (deferred, 3–5 days when their backends exist).**  
Forecast grid, purchase recs queue, exceptions list, approvals cards.

**Step 6 — Tier C shelved until backend contracts land.**  
Operator forms, variance card, PO form, outbox surface.

**Step 7 — Never adopted.**  
Review-mode panel, fake-session pill, dev-note helper, "blocked" nav concept.

### 4.5 Merge-plan inputs (unresolved, to be decided by Tom)

These are decisions the canonical portal and the Window 2 sandbox cannot resolve on their own. They require an explicit coordination note:

1. **Is Window 2 the design lead for both portals?** (If yes, the tokens and patterns are authoritative; the canonical portal's existing design decisions yield to Window 2's.)
2. **Does the canonical portal want to replace its Radix/shadcn primitives with Window 2's hand-rolled ones?** (Recommended: **no**. Keep Radix, restyle. Hand-rolled primitives were an optimization for sandbox-scope, not a superior approach for production.)
3. **Which dev affordance system wins?** Canonical has `RoleSwitcher` (its own); Window 2 has `FAKE SESSION` + `ReviewModePanel`. They cannot coexist in one top bar.
4. **Dark theme support.** Window 2 didn't add it. Canonical may want to. The token system is dark-compatible if you define a `[data-theme="dark"]` branch, but the Window 2 sandbox never exercised this.

Until these are resolved, the adoption strategy in §4.4 stays at steps 1–3 (tokens + restyling, no new components). Past that, a merge plan is required.

---

## 5. Before / after summary

In product terms. Short.

### What changed visually

- **Surface temperature.** Stark white → warm bone paper. The whole product feels less clinical and easier on the eye for long reads.
- **Accent color.** Stock SaaS blue → petrol teal. The product has a distinct color memory now — you can pick a screenshot of it out of a lineup.
- **Typography.** System font stack → Public Sans + IBM Plex Mono. Headlines read editorial-serious. Numerics align in columns. Codes and IDs are monospace by default.
- **Hierarchy.** Flat "plain box" cards → cards with gradient headers, eyebrows, titles, descriptions, right-actions, and semantic-tone borders.
- **Navigation.** Text-only nav items → icon + label + active-bar pattern. Role-aware, with tight eyebrow group headers and a "You are" card.
- **Icons.** Sporadic dot glyphs → consistent Lucide throughout, one per nav/status/action.
- **Status language.** Various ad-hoc pills → dot-driven semantic badges that read at a glance in a row of many.
- **Atmosphere.** Plain flat background → subtle dot-grid body texture that adds weight without noise.

### What changed operationally (readability)

- **Tabular numerics everywhere.** Quantities, deltas, percents, versions, timestamps, SKUs — all align by column. Scannable.
- **Dense row heights.** Tables fit more data per viewport without feeling cramped.
- **Sticky top bar + sticky side nav + sticky form action bar.** Less UI thrashing as you move between sections of a long page. The primary submit is always within reach.
- **Clearer separators.** Hairline borders at calibrated opacity replace heavier default rules — data reads cleaner.
- **Inline clear-X on searches.** Faster iteration on filters.

### What changed in trust / decision clarity

- **Approval-trigger is named explicitly.** Waste adjustments and forecast publishes now surface the exact policy key that will route them to approval, before submit. No operator is ever surprised by an approval step.
- **Live status pulses.** `Pending approval` and `Submitting` states have a soft pulsing dot — operators can tell at a glance what's in motion.
- **FAKE SESSION is impossible to confuse with real auth.** The warning-bordered pill with a pulsing dot in the top bar is loud in the right way — it reads as a ticket, not as a quiet label.
- **Data freshness is visible as a whole cluster.** Every integration boundary (Ledger / LionWheel / Shopify / Green Invoice) has its age + health dot in one place on the dashboard.
- **Variance is a side-by-side card.** Counted vs system vs delta, each with its own column, mono numerics, semantic color on delta. Operators read the decision in < 1 second.
- **Dirty state is explicit on the forecast.** A pulsing warning dot + count of unsaved edits, always visible in the bottom action bar. Nothing ever silently hangs off-screen.

### What intentionally did not change

- **Product scope.** 28 routes, same 28 routes. No feature drift.
- **Business logic.** Forms still submit as mock view-swaps. IndexedDB repositories are unchanged. BOM draft-only rule, optimistic concurrency, blind UX on counts — all untouched.
- **Route structure.** Same layout groups (`(auth)`, `(shared)`, `(operator)`, `(planner)`, `(admin)`), same per-route permissions.
- **Backend assumptions.** Still no `fetch`. Still no `@supabase/supabase-js`. Still no ledger contact.
- **Test coverage depth.** Still 41 Vitest + 13 Playwright. No new tests added in the design round.
- **Dark theme.** Deferred. Light-only.
- **i18n.** English-first. Hebrew only in data values. No RTL.
- **Accessibility baseline.** Focus-visible, semantic HTML, ARIA labels on icon-only buttons — unchanged.

---

## 6. Freeze line

Window 2 is frozen again.

### Explicit freeze terms

1. **No more design iteration** unless Tom requests a specific, targeted pass with scoped deliverables.
2. **No more route expansion.** The 28 routes are the permanent v1 surface.
3. **No more product-scope drift.** No new feature slices, no new forms, no deeper workflow logic.
4. **No backend wiring.** No `fetch`, no `@supabase/supabase-js`, no direct API calls — even "just as a scaffold."
5. **No auth integration.** Fake session stays. `useHasRole` stays.
6. **No Supabase SDK in browser code** — the rule from foundation doc §17 continues to hold.
7. **Sandbox remains sandbox.** The canonical portal is a separate work stream. Window 2 does not port into the canonical repo without an explicit merge plan from Tom.

### What is allowed without breaking the freeze

- **Bug fixes** surfaced by the test layer (following the pattern from the earlier `viewToState` fix).
- **Adding more tests** to guard existing behavior.
- **Responding to targeted Tom-requested polish passes** on specific named screens.
- **Answering questions about the design system** (this document is the reference for that).
- **Re-running the four gates** on demand: `tsc --noEmit`, `next build`, `vitest run`, `playwright test`.

### What breaks the freeze (never do without explicit approval)

- Adding a new route.
- Adding a new lucide icon to a nav item not in the current mapping.
- Adding a new `.btn-*` or `.input-*` variant without a Tom-approved use case.
- Touching `tailwind.config.ts` color or typography tokens.
- Importing Supabase SDK anywhere.
- Wiring any form submission to a real network call.
- Copying Window 2 files into `gt-factory-os/portal/`.
- Starting a dark-theme pass.

---

## Appendix — Quick reference card

For someone reading this at 2am and needing to adopt the system fast:

```
Font: Public Sans + IBM Plex Mono
Base: 14px, tabular-nums everywhere
Background: hsl(42 18% 95%) (warm bone)
Ink: hsl(30 10% 10%) (warm graphite)
Accent: hsl(186 42% 24%) (petrol teal)
Radius: 6px default, 8px large, 4px small
Border: hsl(30 8% 82%) at 70% opacity on cards, 40% on dividers
Shadow: barely there — elevation from bg contrast
Motion: 150ms, cubic-bezier(0.165, 0.84, 0.44, 1)
Icons: lucide-react, stroke 1.75, 14–16px, never decorative
Density: 14px base, 36–40px row, 20px card padding
Eyebrow: 11px uppercase +0.12em tracked, fg-subtle
Status: dot + uppercase label, soft/outline/solid
Numbers: always tabular, mono for codes/IDs/timestamps
Pulse: soft 2.4s on live states only
No: purple gradients, consumer fonts, skeleton shimmer, bounces
```

Treat this card as the elevator pitch. Everything else in this document is detail.

---

_End of Window 2 design transfer package. Window 2 is now frozen._
