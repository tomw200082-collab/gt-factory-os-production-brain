# Dashboard & Control Tower Redesign — Implementation Plan

> **For agentic workers:** REQUIRED — Use `superpowers:subagent-driven-development` (preferred, dispatches W2/W1/W4 executors per tranche) or `superpowers:executing-plans` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Converge `/dashboard` (v1, 7 engineering-truth blocks) and `/dashboard/v2` (v2, 2 live + 7 placeholder decision-truth blocks) into a single best-in-class **morning control tower** that answers "what stops production today, and what falls off the rails this week if I do nothing?" in under 10 seconds, zero scrolls. Then redesign `/planning/inventory-flow` (the FG daily control tower) to match the same visual & interaction language.

**Architecture:** Single canonical `/dashboard` route. Three-layer stack (Alerts → Diagnostics → Recommendations) per IBM/Solvoyo control-tower doctrine. Every block sources from a named `api_read` view per W4 contract `dashboard_control_tower_v2_coverage_requirements.md`. Engineering-truth blocks (parity, jobs, runtime_ready) absorbed into `/admin/system-health`. New design system: shadcn `Card`/`Badge`/`Tabs` extended with status-pill primitives, sparkline cells, freshness chips, time-scope chips, and a Cmd-K command palette. SSR-skeleton + TanStack Query SWR (staleTime 30s, refetchOnWindowFocus, refetchInterval 60s). Mobile-first @ 390px with horizontally-scrollable KPI strip and bottom nav.

**Tech Stack:** Next.js 15 App Router · React 18 · TypeScript · Tailwind · shadcn/ui · TanStack Query v5 · `cmdk` · `framer-motion` (counters only) · Lucide icons. Hebrew copy (LTR layout per CLAUDE.md). Backend: Supabase Postgres + Fastify/Kysely (no new endpoints; only `api_read` views and one or two tightening filters per W4 GAP-2 / GAP-4).

---

## Part 0 — Research synthesis (the WHY)

Four parallel research agents reviewed the world's most respected sources. Synthesis below is the only research carried into the plan; full agent outputs preserved in conversation log.

### The five hard rules every world-class operational dashboard follows

1. **Glance, don't read.** Pre-attentive processing is <200ms. Position + size + a single accent color do the talking. (Stephen Few, NN/g)
2. **Length and 2D position encode quantity — never color or area.** No pies, no gauges, no 3D. Bars and lines win. (Tufte)
3. **Color is a scarce resource. Spend it only on exceptions.** Default state grayscale; color earns its place when the eye must locate breaches in a field of normals. (Few, Refactoring UI)
4. **Per-widget freshness, not a global "last refreshed" badge.** Each tile carries its own `updated 12s ago` chip; widgets caveat themselves when their source is stale. (Datadog, Vercel)
5. **One click = root cause. Two clicks = action.** Anything deeper is a buried surface. (Linear, Kinaxis, o9)

### The single question this dashboard must answer

> **"Is stock truth trustworthy right now, and is the next operator/planner action unblocked? What stops production today; what falls off this week if I do nothing?"**

That is *two facts plus two horizons*: parity status of the stock projection (now), unblocked next action (now), today's blockers (today), this-week's risks (7-day forward window). Everything else is secondary and lives one click away.

### Three exemplars to literally study screenshots of

- **Linear "My Issues" view** — inbox-as-control-surface. Keyboard-first (`J`/`K` move, `Enter` act), no modals, `Cmd-K` palette. Template for our **exceptions inbox** and **blockers list**.
- **Stripe Payments overview** — KPI card with sparkline + trend %. `[number] [▲%] [sparkline]` and nothing else. Template for our **status strip** (parity, FG-at-risk, slipped, jobs).
- **Vercel project dashboard** — deployment status as live tab icon + per-card freshness. Stale data never shown without a freshness chip. Template for our **integration freshness** + **per-block staleness** behavior.

### Patterns we deliberately reject

| Pattern | Why we reject it for this scale |
|---|---|
| OEE / MTBF / cycle-time KPIs (Siemens, GE, Rockwell) | Wrong vocabulary — beverage plant is recipe-driven, not machine-paced |
| Multiple persona dashboards (Tulip's 6) | One factory, four roles, role-aware sections within one page |
| Risk × node heatmap (Blue Yonder, IBM SCIS) | Pointless with one factory and one planner |
| Scenario / what-if sandbox on the landing page | `/planning/runs` already serves this; don't duplicate |
| Multi-tier collaboration threads / @mentions on exceptions | Tom is the planner; WhatsApp suffices |
| Pies, gauges, 3D, donut charts | Banned by Tufte/Few; no exceptions |
| Reports-disguised-as-dashboard (Katana Insights) | Dashboard answers "now"; reports answer "trend" — they live in a separate `/reports` surface |

---

## Part 1 — Vision & strategy

### 1.1 Converge to a single canonical `/dashboard`

**Decision:** Drop the v1/v2 split. The single `/dashboard` route becomes Tom's morning control tower. The current v1's seven engineering-truth blocks (parity, jobs, runtime_ready, etc.) move to `/admin/system-health` where they already belong cognitively (system audits, not daily decisions).

**Rationale:** W4 contract §1 explicitly authorizes "Replace the existing 7-block `/dashboard` with an operator-truth-first morning control tower." DCT2-8 default at portal-author time was "ship at `/dashboard/v2`" because v1 was load-bearing; once v2 reaches feature parity, the split costs muscle memory more than it earns.

**Migration path:**
- `/dashboard/v2` → 308 redirect to `/dashboard` once T-E (all 9 blocks live) lands.
- Archive v1's `/dashboard/page.tsx` content to `/admin/system-health/page.tsx` (new route under `(admin)` group).
- Sidebar nav: rename "Dashboard" entry to "מגדל פיקוח" / "Control Tower"; existing `/admin/jobs` and `/admin/integrations` remain as drill-downs from `/admin/system-health`.

### 1.2 The control tower lives at `/dashboard`. The FG daily projection lives at `/planning/inventory-flow`.

**Two surfaces, one design language.** `/dashboard` is the morning glance ("am I OK across all corridors?"). `/planning/inventory-flow` is the deep daily FG projection ("which SKU runs out which day?"). Both adopt the same color palette, status pill system, freshness chips, time-scope chips, and Cmd-K palette. They differ in density (dashboard: dense status strip + lists; inventory-flow: full grid with timeline) but share primitives.

### 1.3 Three-layer stack as the canonical layout

| Layer | Purpose | Visual weight | Blocks |
|---|---|---|---|
| **Layer 1 — Alerts** | "What stops me right now?" | Largest. Top of page. Red-tinted on breach. | §4.1 Critical Today + status strip (KPI tiles) |
| **Layer 2 — Diagnostics** | "What's the picture this week?" | Medium. Two-column grid on desktop, stacked on mobile. | §4.2 Stock Risk · §4.3 Planned Production · §4.4 Slipped Plans · §4.5 Open POs |
| **Layer 3 — Recommendations & Health** | "What needs review or maintenance?" | Smallest. Bottom of page. | §4.6 Blocked Production · §4.7 Blocked Purchase · §4.8 Integration Freshness · §4.9 Top-5 Exceptions |

Cross-cutting: persistent **break-glass banner** (top, when active), **freshness band** (above Layer 3), **quick-action row** (top-right on desktop, top-scroll on mobile), **Cmd-K palette** (global).

---

## Part 2 — Information architecture

### 2.1 Canonical block map (replaces both v1 and v2)

| # | Block | Source view (per W4 §3) | Layer | Desktop position | Mobile order |
|---|---|---|---|---|---|
| **A** | Status strip — 4 KPI tiles | mixed (v_critical_today count, v_inventory_flow_summary, v_planning_run_latest, v_integration_freshness count) | 1 | row 1, full-width 4-col grid | row 1 horizontal scroll |
| **B** | §4.1 Critical Today | `api_read.v_critical_today` ✓ existing | 1 | row 2, full-width red-tinted | row 2 |
| **C** | §4.2 This-Week FG Stock Risk | `GET /api/v1/queries/inventory/flow?at_risk_only=true&horizon_weeks=2` ✓ | 2 | row 3, left half | row 3 |
| **D** | §4.3 This-Week Planned Production | `GET /api/v1/queries/production-plan` ✓ (date filter — GAP-2) | 2 | row 3, right half | row 4 horizontal scroll |
| **E** | §4.4 Slipped Plans | `api_read.v_production_plan_slippage` ✓ existing (signal #22) | 2 | row 4, left half | row 5 |
| **F** | §4.5 Open POs Due This Week | `GET /api/v1/queries/purchase-orders` ✓ (client-filter v1; GAP-4 optional) | 2 | row 4, right half | row 6 |
| **G** | §4.6 Blocked Production | `GET /api/v1/queries/planning/blockers?category=missing_bom` ✓ | 3 | row 5, left third | row 7 |
| **H** | §4.7 Blocked Purchase | `GET .../blockers?category=missing_supplier_mapping&...&...` ✓ | 3 | row 5, middle third | row 8 |
| **I** | §4.9 Top-5 Exceptions | `api_read.v_exception_summary` ✓ | 3 | row 5, right third | row 9 |
| **J** | §4.8 Integration Freshness | `api_read.v_integration_freshness` ✓ | 3 | row 6, full-width 7-col | row 10 |

### 2.2 Status strip (Layer 1 KPI tiles) — the four numbers above the fold

Per Stripe pattern: `[number] [▲%/sparkline] [muted source citation]`. Click → drill into the corresponding view.

| Tile | Headline | Sub | Tone trigger | Click target |
|---|---|---|---|---|
| **1. Stock truth** | `parity_ok ? "תקין" : `${drift_count} שורות סטייה`` | "פרציה אחרונה: לפני 2 שעות" | red if `!parity_ok`; amber if last check >24h | `/admin/system-health` |
| **2. Critical today** | count of `v_critical_today` rows | top trigger_kind label | red if count>0; green-soft if 0 | scrolls to §4.1 anchor |
| **3. Stock at risk (14d)** | count of inventory_flow at-risk items | "${earliest_stockout} הוא הראשון" | red if any stockout date ≤ today; amber if ≤ 7d | `/planning/inventory-flow?at_risk_only=true` |
| **4. Open exceptions** | count of `v_exception_summary` rows | "X חמורות, Y בינוניות" | red if any critical; amber if any warning | `/exceptions` |

Sparkline: 14-day daily count for tiles 2/3/4 (when read-models expose it; v1 ships without sparklines and adds in T-H). Tile 1's sparkline is the daily parity check pass/fail strip — render the last 14 dots, green/red.

### 2.3 Quick-action row (top-right on desktop, top-scroll on mobile)

Per W4 §7. Hidden (not disabled) when role gate excludes user. Renders as `<Link>` (no `onClick`) per W4 §7.5.

| Action | Hebrew | Destination | Roles |
|---|---|---|---|
| הרץ תכנון | RUN_PLANNING | `/planning/runs` | planner, admin |
| תכנון ייצור | OPEN_PRODUCTION_PLAN | `/planning/production-plan` | operator, planner, admin |
| חריגות | OPEN_EXCEPTIONS | `/exceptions` | all four |
| תיבת דואר | OPEN_INBOX | `/inbox` | all four |
| **+ דיווח קליטה** (new) | OPEN_GR | `/ops/receipts` | operator, planner, admin |
| **+ ספירה חדשה** (new) | OPEN_COUNT | `/ops/stock/physical-count` | operator, planner, admin |

Two new actions added beyond W4 §7.1 because operator daily flow needs them at one click. W4 contract is base requirement; this is additive and non-conflicting.

### 2.4 Cmd-K command palette (global)

Triggers: `Cmd+K` / `Ctrl+K`. Searchable across:
- Every navigable route in the sidebar (with role gate)
- Every item by `item_name` / SKU (deep-link to `/inventory?item_id=…` or `/admin/items/[item_id]`)
- Every supplier (deep-link to `/admin/suppliers/[supplier_id]`)
- Every open exception by category (deep-link to filtered `/exceptions`)
- Time-scope verbs ("עבור ל-7 ימים", "עבור ל-14 ימים")

Default top hits when palette empty: today's primary actions for the user's role.

---

## Part 3 — Visual design system (the colors, the type, the spacing)

### 3.1 Color tokens (extends shadcn theme)

**Status palette (semantic, not branded):**

| Token | Light hex | Dark hex | Use |
|---|---|---|---|
| `status-ok` | `#15803D` (green-700) | `#86EFAC` (green-300) | parity OK, fresh integration, "all clear" empty state |
| `status-ok-soft` | `#DCFCE7` (green-100) | `#14532D/40` | tile background when state=OK |
| `status-warn` | `#B45309` (amber-700) | `#FCD34D` (amber-300) | freshness=warning, slipped <3d, near-stockout |
| `status-warn-soft` | `#FEF3C7` (amber-100) | `#78350F/40` | tile background when state=WARN |
| `status-danger` | `#B91C1C` (red-700) | `#FCA5A5` (red-300) | parity drift, critical_today fired, stockout today, fail_hard exception |
| `status-danger-soft` | `#FEE2E2` (red-100) | `#7F1D1D/40` | tile background when state=DANGER |
| `status-stale` | `#475569` (slate-600) | `#94A3B8` (slate-400) | dashed-ring chip; never_ran, no-data-yet |
| `status-info` | `#1D4ED8` (blue-700) | `#93C5FD` (blue-300) | informational pills (run status: "completed", "running", "draft") |
| `status-accent` | (existing accent) | (existing accent) | role badges, drill-down hover |

**Hard rules:**
- Default tile/card background: `bg-bg-raised` (existing). No status color unless tone is set.
- Soft fills (`-soft` tokens) only for KPI tiles in Layer 1 and the §4.1 banner. Layer 2/3 cards stay neutral; status conveyed by per-row badges + dot indicators.
- Body text never uses raw status colors — only `*-fg` variants paired with appropriate background contrast (WCAG AAA: 7:1 minimum).
- Amber (`#B45309`) only at >=14px text; never thin body type.
- Diverging quantitative scales (over/under target) use blue↔orange (`#1D4ED8` ↔ `#C2410C`), NOT red/green. Reserve red/green for binary status only.

**Colorblind safety:** every color encoding pairs with a shape/icon:
- OK → solid filled circle
- Warn → triangle (filled when severe)
- Danger → filled square / stop sign
- Stale → dashed ring
- Info → "i" circle

### 3.2 Typography scale (Inter or system; existing portal stack)

| Level | Size | Weight | Use |
|---|---|---|---|
| Display | 32–40px | 600 | KPI numbers (status strip values) |
| H1 | 24px | 600 | page title (`מגדל פיקוח`) |
| H2 | 18px | 600 | section card titles (block headers) |
| H3 | 14px | 600 | sub-section labels inside a block |
| Body | 14px | 400 | row text, descriptions |
| Small | 12px | 400 | row meta (timestamps, source citations) |
| Eyebrow | 11px | 600 uppercase tracking-wide | block eyebrow ("§4.1 Layer 1", or just "Layer 1") |
| Mono | 12px | 500 monospace | timestamps, IDs in tooltips |

**Hierarchy rule (Knaflic/Linear):** typography hierarchy does most of the work. Bold + size + position. Color earns its place only on status. Never bold "everything important" — when everything is bold, nothing is.

### 3.3 Spacing & density

- **Card padding:** `p-4` desktop, `p-3` mobile internal padding. `gap-4` between cards.
- **Above-the-fold target (1440×900 desktop):** Status strip + §4.1 Critical Today fully visible without scroll. ≤6 KPI tiles in the strip (we ship 4).
- **Above-the-fold target (390×844 mobile):** Quick-action row + Status strip horizontal scroll + §4.1 Critical Today header all visible. The body of §4.1 may extend below fold; the count badge is enough.
- **Line height:** `leading-relaxed` (1.625) for descriptions; `leading-normal` (1.5) for table rows; `leading-tight` (1.25) for KPI values.
- **One screen, no scroll, for the role landing.** Drill-downs live one click away.

### 3.4 Status pill system (the 3-tone discipline)

**Don't use 5 colors.** Use 3 tones + shape + position + modifier:

```tsx
<StatusPill tone="ok|warn|danger" variant="solid|outline|dotted" icon={<IconForKind/>}>
  {label}
</StatusPill>
```

- `tone="ok"` `variant="solid"` → fresh, posted, completed
- `tone="warn"` `variant="solid"` → stale, slipped, near-stockout
- `tone="danger"` `variant="solid"` → critical, stockout, fail_hard
- `tone` + `variant="outline"` → milder shade of same state
- `tone` + `variant="dotted"` → indeterminate / pending state (NEVER mock data, only honest "we're checking")

**Stale and Unknown ride on the warn/neutral pill** with a `Clock` or `?` icon modifier — they aren't separate colors.

Existing portal already has `Badge` with `tone={ok|warn|danger|info|neutral|accent}` and `variant={solid|outline|soft|...}`. We extend `dotted` and add canonical `StatusPill` wrapper that enforces the 3-tone discipline (info/neutral/accent stay available but are only for non-status uses).

### 3.5 Sparkline conventions (Tufte, Stripe)

- **Inline only.** Never standalone charts on the dashboard.
- **Width 80–120px, height 24–32px.** Inside KPI tile, right of the number.
- **No axes, no labels, no gridlines.** A sparkline is a typographic glyph, not a chart.
- **End point dot** (Tufte rule) — last point gets a 4px dot, colored by current tone.
- **Hover tooltip** — date + value. No legend.
- Library: lightweight inline SVG component, ~30 lines. No `recharts` for sparklines (overkill).

Used for: status strip tiles 2/3/4 (14-day count), §4.4 slipped-plans block header (last-30-day slip count), §4.8 freshness producers (24-hour freshness pulse).

### 3.6 Animation discipline (motion = signal, not decoration)

- **Counters.** When a KPI value changes during refresh, animate from old → new over 400ms (`framer-motion` or `react-countup`). Subtle.
- **Pulse on data change.** When a row appears or status flips, brief 200ms background flash on that row only. (`framer-motion` `animate` + `transitionEnd`.)
- **Skeleton shimmer.** During initial load, shimmer the skeleton. After first response, never shimmer.
- **Banned.** No spinning loaders, no bouncing icons, no infinite ambient animations, no auto-rotating tiles. Motion destroys glanceability.
- `prefers-reduced-motion` respected — counters and pulse become instant.

---

## Part 4 — Interaction model

### 4.1 Time-scope chips (top of page, sticky)

```
[Today] [7 days] [14 days] [30 days]    ← URL-encoded (?scope=14d)
```

- One click changes every time-scoped block on the page (§4.2 horizon, §4.4 slip window, §4.5 PO horizon, §4.9 exception age cutoff).
- Default: `7d`. Persists in URL.
- Mobile: same row as quick actions, horizontally scrollable.

### 4.2 URL-encoded filter state

Every filter (scope, severity, source) lives in the URL. Tom can copy-paste a URL and another role sees the same view. Pattern from Linear/Stripe.

```
/dashboard?scope=14d&severity=critical&from=lionwheel
```

- `useSearchParams` + `useRouter().replace` for non-blocking updates
- Filter bar is sticky at top (z-40, backdrop blur, border-b)

### 4.3 Per-row interactions

- **Hover** → subtle background highlight + side-popover preview (200ms delay) showing the row's full detail. No navigation cost.
- **Click** → navigate to the action surface (one click = root cause; the action surface owns the mutation per W4 §7.5).
- **Keyboard** (Linear pattern): `J`/`K` (or `↓`/`↑`) move focus through rows; `Enter` opens; `Esc` clears focus.

### 4.4 Per-widget freshness chip

Top-right corner of each block:

```
[Clock-icon] עודכן לפני 12 שניות   ← green
[Clock-icon] עודכן לפני 6 דקות      ← amber when >5min
[Clock-icon] עודכן לפני 32 דקות     ← red when >30min
```

- Sourced from W4-locked `current_state` column on `v_integration_freshness` for blocks whose source is producer-tracked.
- For blocks whose source is a curated `api_read` view (e.g., `v_critical_today`), use the response's `as_of` field (already returned per inventory_flow §6.5).
- **Never** compute freshness from raw timestamps client-side (W4 §8.3 — no-derived-staleness rule).

### 4.5 Optimistic UI (where applicable)

The dashboard itself is read-only per W4 §7.5. But quick-action targets (`/exceptions`, `/inbox`, future inline acknowledge) get optimistic-UI treatment via TanStack Query `onMutate` + rollback on error. Pattern: instant local update, server confirmation in background, rollback on failure with a toast.

This is not a v1 dashboard requirement — it's a primitive used by destination surfaces. Mentioned here for design-system completeness.

### 4.6 Cmd-K command palette

Library: `cmdk` (4kb gzipped). Keyboard shortcut: `Cmd+K` / `Ctrl+K`. See §2.4 for hit list. Modal: full-page `Dialog` with backdrop blur, autofocused input.

---

## Part 5 — Freshness, trust & disclosure (the W4 §8 contract — non-negotiable)

Every numeric or state value rendered on the dashboard MUST surface its source and freshness. This is the operator-trust principle: a number without provenance is a guess.

### 5.1 The three required disclosures per number (W4 §8.1)

1. **Source view / endpoint name** — e.g., `api_read.v_integration_freshness`. Rendered in tooltip-on-hover (desktop) or tap-popover (mobile).
2. **As-of timestamp** — relative time at block footer; absolute timestamp on hover.
3. **Freshness state** — `fresh | warning | critical | never_ran` (verbatim from `v_integration_freshness`). Rendered as small dot icon next to block title.

### 5.2 No-stale-rendering rule (W4 §8.2)

If a block's source is in `critical` or `never_ran` state, the block renders with a red banner: `"מקור הנתונים מיושן ב-N שעות. החלטות שמסתמכות על הבלוק הזה אינן אמינות."` The block STILL renders the data (per inventory_flow_contract.md UNRESOLVED-IF-6 default — staleness is surfaced, not hidden).

### 5.3 No-derived-staleness rule (W4 §8.3)

The dashboard MUST NOT compute "fresh / warning / critical" from raw timestamps. It consumes `current_state` from `v_integration_freshness` verbatim. Any per-block staleness banner is keyed on the producer's `current_state`, not on age math performed on the dashboard side.

### 5.4 Source-citation footers

Each block's footer renders a `ⓘ source: api_read.v_critical_today · עודכן לפני 14 שניות` line in muted small text. Click → opens an "About this block" modal showing the contract reference (`docs/integrations/dashboard_control_tower_v2_coverage_requirements.md#§4.1`) — Tom can audit.

---

## Part 6 — Mobile-first @ 390px

Tom checks the dashboard from his phone at 07:30 IDT before the factory opens. Mobile is the primary morning surface, not an afterthought.

### 6.1 Block visibility @ 390px (priority top → bottom)

1. **Quick-action row** (horizontal scroll) — always visible, never collapsed
2. **Status strip** — 4 KPI tiles in horizontal scroll
3. **§4.1 Critical Today** — full-width, ALWAYS visible at top, never collapsed (W4 §6.3)
4. **§4.2 This-Week FG Stock Risk** — max 5 rows + "View all (N) →"
5. **§4.3 Planned Production** — collapsed to horizontal day-strip (7 columns scrollable, the only authorized horizontal scroll per W4 §6.5)
6. **§4.4 Slipped Plans** — max 5 rows
7. **§4.5 Open POs Due** — two sub-sections (overdue / due) stacked
8. **§4.6/§4.7 Blockers** — max 3 rows each
9. **§4.8 Integration Freshness** — abbreviated columns (state badge + producer label + relative age)
10. **§4.9 Top-5 Exceptions** — max 5 rows

### 6.2 Bottom nav (new)

Three destinations always reachable on mobile:

```
[בית]  [מלאי]  [משימות]
```

- בית → `/dashboard`
- מלאי → `/inventory` (or `/planning/inventory-flow` for planner+)
- משימות → `/inbox`

Implemented as a `fixed bottom-0` nav. Hides on scroll-down; reveals on scroll-up.

### 6.3 Hard rules

- No horizontal scroll except §4.3 day-strip (W4 §6.5)
- All other blocks reflow to single column
- `min-h-screen` on root — never a stunted layout
- Tap targets ≥44×44px (Apple HIG)
- Sidebar collapses to drawer (existing portal behavior)

---

## Part 7 — Implementation tranches

> **Execution model:** This plan is implemented under Mode B-Planning-Corridor (per `EXECUTION_POLICY.md` 2026-05-02 amendment scoping pan-portal authoring on planning corridor surfaces). `/dashboard` is on the allowed-surfaces list per DCT2-8 default. **Tranches are dispatched sequentially**; each tranche has its own validation gate and commit. No tranche begins before the prior tranche's success-evidence is recorded. **W4 contract compliance is non-negotiable** at every gate.
>
> **Owner mapping:**
> - **W2** (window2-portal-sandbox): T-A, T-B, T-C portal, T-D portal, T-E portal, T-F, T-G, T-H
> - **W1** (gt-factory-os): T-C backend (status strip aggregation view), T-D backend (only if GAP-2 PO date filter not yet exposed), T-E backend (no new endpoints — verifies existing read-models)
> - **W4**: contract mirroring; §11 acceptance verification per tranche
>
> **Verifier:** every tranche ends with `verifier` agent run before merge. PASS evidence required (live HTTP 200, real JWT, mobile @ 390px Playwright snapshot, Network panel zero-write check per W4 §11.7).

### Chunk 1: Foundation primitives (T-A)

Goal: ship the design-system primitives every later tranche consumes. No user-visible change yet.

**File map (W2 portal):**
- Create: `src/components/control-tower/StatusPill.tsx`
- Create: `src/components/control-tower/KPITile.tsx`
- Create: `src/components/control-tower/Sparkline.tsx`
- Create: `src/components/control-tower/FreshnessChip.tsx`
- Create: `src/components/control-tower/TimeScopeChips.tsx`
- Create: `src/components/control-tower/SourceCitation.tsx`
- Create: `src/lib/control-tower/tokens.ts` (status palette tokens; extends existing theme)
- Modify: `tailwind.config.ts` — add `status-ok / status-warn / status-danger / status-stale` color tokens (light + dark)
- Test: `src/components/control-tower/__tests__/StatusPill.test.tsx`, `KPITile.test.tsx`, etc. (Vitest + RTL)

#### Task 1: Status palette tokens

- [ ] Step 1: Extend `tailwind.config.ts` `theme.extend.colors` with the §3.1 palette. Tokens: `status-ok / status-ok-soft / status-warn / status-warn-soft / status-danger / status-danger-soft / status-stale / status-info`. Light + dark variants via existing CSS-vars pattern.
- [ ] Step 2: Build `src/lib/control-tower/tokens.ts` exporting `STATUS_TONES = ['ok', 'warn', 'danger', 'stale', 'info'] as const` and `type StatusTone = (typeof STATUS_TONES)[number]`.
- [ ] Step 3: Run `pnpm typecheck`. Expected: `EXIT=0`.
- [ ] Step 4: Verify dark-mode contrast WCAG AAA on every token via axe-core in Storybook (or skip Storybook, run `axe` against a temporary fixture page).
- [ ] Step 5: Commit `feat(control-tower): add status palette tokens (T-A.1)`.

#### Task 2: `<StatusPill>` primitive

- [ ] Step 1: Write failing test `StatusPill.test.tsx` — assert tone={'ok'|'warn'|'danger'|'stale'|'info'} renders correct bg/fg classes; variant={'solid'|'outline'|'dotted'} renders correct border treatment; `icon` slot renders the passed icon; colorblind invariant: every tone pairs with a default shape (solid circle / triangle / square / dashed ring / i-circle) when no icon is passed.
- [ ] Step 2: Run test, expect FAIL ("StatusPill not defined").
- [ ] Step 3: Implement `StatusPill.tsx`. Props: `tone`, `variant`, `icon?`, `dotted?` (alias for `variant="dotted"`), `children`, `aria-label?`.
- [ ] Step 4: Run test, expect PASS.
- [ ] Step 5: Commit `feat(control-tower): StatusPill primitive (T-A.2)`.

#### Task 3: `<KPITile>` primitive

- [ ] Step 1: Write failing test `KPITile.test.tsx` — props: `label`, `value`, `tone`, `sub?`, `sparkline?`, `href?`, `icon?`. Asserts: value renders display-size; clicking when `href` set navigates; sparkline renders inline beside value when passed; tone={ok|warn|danger} sets correct soft background.
- [ ] Step 2: Run test, expect FAIL.
- [ ] Step 3: Implement `KPITile.tsx`. Wraps `<Link>` when `href`, plain `<div>` otherwise. Internal layout: `flex flex-col gap-2 rounded border p-4`. Value uses `text-3xl font-semibold tracking-tight`. Background per tone soft.
- [ ] Step 4: Run test, expect PASS.
- [ ] Step 5: Commit `feat(control-tower): KPITile primitive (T-A.3)`.

#### Task 4: `<Sparkline>` primitive

- [ ] Step 1: Write failing test `Sparkline.test.tsx` — input `data: number[]` length 14; asserts SVG renders 14 points, last point gets dot, tone classes applied; renders nothing if length<2 (degraded gracefully).
- [ ] Step 2: Run test, expect FAIL.
- [ ] Step 3: Implement `Sparkline.tsx` as a 30-line inline-SVG component. Computes min/max, normalizes to viewBox, renders `<polyline>` + final `<circle r=2>`. Width/height props with sensible defaults (96×24).
- [ ] Step 4: Run test, expect PASS.
- [ ] Step 5: Commit `feat(control-tower): Sparkline primitive (T-A.4)`.

#### Task 5: `<FreshnessChip>` primitive

- [ ] Step 1: Write failing test `FreshnessChip.test.tsx` — props: `currentState: 'fresh'|'warning'|'critical'|'never_ran'`, `lastSuccessAt: string|null`, `now: Date`. Asserts: tone derives from `currentState` ONLY (never from age math) — invariant test: when `lastSuccessAt` is 30s ago but `currentState='critical'`, chip renders red. When `lastSuccessAt` is 3h ago but `currentState='fresh'`, chip renders green. (Per W4 §8.3 no-derived-staleness rule.)
- [ ] Step 2: Run test, expect FAIL.
- [ ] Step 3: Implement `FreshnessChip.tsx`. Renders `<StatusPill>` with tone from `currentState` and label `"עודכן לפני {ageHumanized}"`.
- [ ] Step 4: Run test, expect PASS.
- [ ] Step 5: Commit `feat(control-tower): FreshnessChip respecting W4 §8.3 (T-A.5)`.

#### Task 6: `<TimeScopeChips>` primitive

- [ ] Step 1: Write failing test `TimeScopeChips.test.tsx` — renders 4 chips (Today/7d/14d/30d), reads `?scope=` from `useSearchParams`, click triggers `router.replace` with new param without page reload, defaults to `7d` when absent.
- [ ] Step 2: Run test (mock `next/navigation`), expect FAIL.
- [ ] Step 3: Implement `TimeScopeChips.tsx` using `useSearchParams` + `useRouter`. Chip is a `<button>` with `aria-pressed`.
- [ ] Step 4: Run test, expect PASS.
- [ ] Step 5: Commit `feat(control-tower): TimeScopeChips with URL state (T-A.6)`.

#### Task 7: `<SourceCitation>` primitive

- [ ] Step 1: Write failing test — renders muted-small footer text with `ⓘ source: {viewName} · עודכן {relativeTime}`. Tooltip on hover shows `{absoluteTime}`. Click opens an "About this block" `<Dialog>` linking to W4 contract section.
- [ ] Step 2: Run test, expect FAIL.
- [ ] Step 3: Implement `SourceCitation.tsx`.
- [ ] Step 4: Run test, expect PASS.
- [ ] Step 5: Commit `feat(control-tower): SourceCitation footer (T-A.7)`.

#### Task 8: T-A acceptance gate

- [ ] Step 1: Run full portal `pnpm typecheck`. Expected: `EXIT=0`.
- [ ] Step 2: Run `pnpm build`. Expected: `EXIT=0`.
- [ ] Step 3: Run new vitest suite `pnpm test src/components/control-tower`. Expected: all PASS.
- [ ] Step 4: Run axe-core against a Storybook fixture (or a `/dev/control-tower-fixture` route gated by `NODE_ENV !== 'production'`). Expected: zero AAA violations.
- [ ] Step 5: Verifier: dispatch `verifier` subagent with prompt "Verify T-A primitives compile, tests pass, axe AAA clean, and no usage of raw color hex outside `tailwind.config.ts`." Expected verdict: **PASS**.
- [ ] Step 6: Commit `chore(control-tower): T-A acceptance gate passed`. Push.

---

### Chunk 2: Route convergence (T-B)

Goal: collapse `/dashboard/v2` into `/dashboard` and archive engineering blocks to `/admin/system-health`. No new functionality; pure consolidation.

**File map:**
- Modify: `src/app/(shared)/dashboard/page.tsx` — replace contents with v2's layout (Critical Today + Slipped Plans + 7 placeholders + quick actions)
- Modify: `src/app/(shared)/dashboard/v2/page.tsx` — replace with `redirect('/dashboard')` server component
- Create: `src/app/(admin)/admin/system-health/page.tsx` — moves the v1 7 engineering-truth blocks here, gated to `admin` only
- Modify: `src/components/SideNav/manifest.ts` (or equivalent nav source) — KEEP "Dashboard" label English per Q-2 decision (do NOT rename); add "System Health" entry under Admin
- Test: existing `/dashboard` E2E that asserts `/dashboard` HTTP 200 still passes; new test asserts `/dashboard/v2 → 308 → /dashboard`; new test asserts `/admin/system-health` HTTP 200 for admin role only

#### Task 9: Move v2 layout to `/dashboard`, redirect `/dashboard/v2`

- [ ] Step 1: Backup current `/dashboard/page.tsx` content into `src/app/(admin)/admin/system-health/_legacy-dashboard.tsx` (preserve as starting point for T-B.10).
- [ ] Step 2: Replace `/dashboard/page.tsx` with the contents of `/dashboard/v2/page.tsx` (verbatim) plus updated route comments noting the convergence.
- [ ] Step 3: Replace `/dashboard/v2/page.tsx` with `import { redirect } from 'next/navigation'; export default function() { redirect('/dashboard'); }`. Add `export const dynamic = 'force-dynamic'` so the redirect always runs.
- [ ] Step 4: Run `pnpm typecheck` + `pnpm build`. Expected: both `EXIT=0`.
- [ ] Step 5: Smoke test in dev: `/dashboard` renders the v2 layout; `/dashboard/v2` redirects.
- [ ] Step 6: Commit `feat(dashboard): converge v1+v2 to single canonical /dashboard route (T-B.9)`.

#### Task 10: Archive engineering blocks to `/admin/system-health`

- [ ] Step 1: Create `src/app/(admin)/admin/system-health/page.tsx` using `_legacy-dashboard.tsx` as starting point. Strip the user-greeting header; replace eyebrow with "System health" / "מצב מערכת".
- [ ] Step 2: Add role gate — only `admin` role passes; `planner | operator | viewer` get redirected to `/dashboard`.
- [ ] Step 3: Update sidebar nav manifest: add `"System Health"` entry under Admin section, route `/admin/system-health`. Remove the original `/dashboard` engineering-blocks reference if any.
- [ ] Step 4: Run `pnpm typecheck` + `pnpm build` + `pnpm test`. Expected: all `EXIT=0`.
- [ ] Step 5: E2E test: as `admin`, visit `/admin/system-health` → renders Stock Truth + Parity + Jobs 24h + Forecast + RUNTIME_READY blocks; as `planner`, visit → 307 redirect to `/dashboard`.
- [ ] Step 6: Commit `feat(admin): /admin/system-health archives engineering-truth blocks (T-B.10)`. Push.

#### Task 11: T-B acceptance gate

- [ ] Step 1: Deploy to Vercel preview. Confirm: `/dashboard` renders v2 layout; `/dashboard/v2` 308→`/dashboard`; `/admin/system-health` HTTP 200 for admin, 307→`/dashboard` for non-admin.
- [ ] Step 2: Verifier: dispatch with prompt "Verify T-B route convergence: single canonical /dashboard, /dashboard/v2 redirects, engineering blocks archived to /admin/system-health behind admin role gate, no broken sidebar links."
- [ ] Step 3: Tom checkpoint: brief Tom that the convergence has landed. Sidebar label stays "Dashboard" per Q-2 decision; no rename.

---

### Chunk 3: Layer 1 — Status strip + Critical Today (T-C)

Goal: ship the four KPI tiles + the Critical Today block with full design-system treatment. This is the morning glance.

**Backend prereqs (W1):** confirm `api_read.v_critical_today` is exposed via `GET /api/dashboard/critical-today` (already live per signal #19). One new aggregation: `GET /api/dashboard/status-strip` returning the four numbers in one response (avoids 4 round-trips from the dashboard).

**File map (W2):**
- Create: `src/features/control-tower/use-status-strip.ts` (TanStack Query hook → `/api/dashboard/status-strip`)
- Create: `src/features/control-tower/StatusStrip.tsx` (4 `<KPITile>` in a grid)
- Create: `src/features/control-tower/CriticalTodayBlock.tsx` (refactored from existing inline component; uses new primitives)
- Create: `src/app/api/dashboard/status-strip/route.ts` (Next proxy → `/api/v1/queries/dashboard/status-strip`)
- Modify: `src/app/(shared)/dashboard/page.tsx` — replace the existing critical-today inline component with imported one; add `<StatusStrip />` above it

**File map (W1) — only if status-strip aggregation read-model needs to be authored:**
- Create: `db/migrations/0132_v_dashboard_status_strip.sql` — view aggregating: `(SELECT COUNT(*) FROM api_read.v_critical_today)`, `(SELECT COUNT(*) FROM api_read.v_inventory_flow_summary WHERE risk_tier IN ('stockout','near_stockout'))`, `(SELECT parity_ok, drift_count, last_check_at FROM api_read.v_parity_status)`, `(SELECT COUNT(*) FROM api_read.v_exception_summary WHERE status='open')`.
- Create: `db/tests/0132_v_dashboard_status_strip.test.sql` — pgTAP, 4 assertions.
- Create: `api/src/dashboard/status-strip-route.ts` — Fastify route + Zod schema.
- Test: `api/test/dashboard-status-strip.test.ts` — node:test against live pooled PG17.

**Decision needed:** Does Tom want a single aggregation read-model (one round-trip, less flexibility) OR four parallel TanStack Queries (4 round-trips, each tile has independent stale state)? Default per dashboard performance research: **single aggregation** — because mobile cellular latency dominates 4 round-trips. Reversible. See open question Q-1.

#### Task 12: W1 — `v_dashboard_status_strip` view (parallel-safe)

- [ ] Step 1: Author `db/migrations/0132_v_dashboard_status_strip.sql` per file map. View body: SELECT four scalar columns from existing api_read views.
- [ ] Step 2: Author pgTAP test asserting view exists, returns exactly 1 row, columns match contract.
- [ ] Step 3: Apply to live Supabase via existing migration runner. Confirm `pg_prove` 4/4.
- [ ] Step 4: Author Fastify route `api/src/dashboard/status-strip-route.ts`. Zod response schema: `{critical_count: number, at_risk_count: number, parity_ok: boolean, parity_drift_count: number, parity_checked_at: string, open_exceptions_count: number, as_of: string}`.
- [ ] Step 5: Author node:test asserting HTTP 200 against live pooled PG17 with real JWT.
- [ ] Step 6: Deploy to Railway. Confirm `GET /api/v1/queries/dashboard/status-strip` HTTP 200 with JWT, 401 without.
- [ ] Step 7: Emit harness signal `RUNTIME_READY(DashboardStatusStrip)`.
- [ ] Step 8: Commit + push.

#### Task 13: W2 — `<StatusStrip>` component

- [ ] Step 1: Create `src/app/api/dashboard/status-strip/route.ts` Next proxy.
- [ ] Step 2: Create `src/features/control-tower/use-status-strip.ts` TanStack hook with `staleTime: 30_000` and `refetchOnWindowFocus: true`.
- [ ] Step 3: Write failing test for `StatusStrip.tsx` — renders 4 tiles, each KPITile with correct `tone` derived from data (parity_ok=false → tone="danger"; critical_count>0 → tone="danger"; at_risk_count>0 → tone="warn"; open_exceptions_count=0 → tone="ok").
- [ ] Step 4: Run test, expect FAIL.
- [ ] Step 5: Implement `StatusStrip.tsx`. Layout: `grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4`.
- [ ] Step 6: Run test, expect PASS.
- [ ] Step 7: Add to `/dashboard/page.tsx` above the existing Critical Today block.
- [ ] Step 8: Commit `feat(control-tower): StatusStrip with W4-compliant freshness (T-C.13)`.

#### Task 14: W2 — refactor `CriticalTodayBlock` to use new primitives

- [ ] Step 1: Extract existing inline Critical Today component into `src/features/control-tower/CriticalTodayBlock.tsx`.
- [ ] Step 2: Replace inline `<div>` rows with `<StatusPill tone="danger" variant="solid">` for trigger_kind labels.
- [ ] Step 3: Add `<FreshnessChip>` to top-right corner reading `as_of` from response.
- [ ] Step 4: Add `<SourceCitation>` to footer.
- [ ] Step 5: Re-import in `/dashboard/page.tsx`.
- [ ] Step 6: Run E2E: `/dashboard` HTTP 200; Critical Today block renders identically to before, with refined visual treatment.
- [ ] Step 7: Commit `refactor(control-tower): CriticalTodayBlock uses primitives (T-C.14)`. Push.

#### Task 15: T-C acceptance gate

- [ ] Step 1: Verifier: "Verify T-C status strip + Critical Today block render against live data; tile tones derive from response data verbatim (no client-side math); freshness chip uses server-computed `current_state` per W4 §8.3."
- [ ] Step 2: Mobile Playwright snapshot @ 390px — status strip horizontally scrollable; Critical Today fully visible above the fold.
- [ ] Step 3: Tom morning-glance test: Tom opens `/dashboard` on phone; reports "I can see what's broken in <5 seconds" or kicks back. **CONDITIONAL GO** until Tom confirms verbally.

---

### Chunk 4: Layer 2 — Diagnostics (T-D)

Goal: ship the four mid-layer blocks (§4.2 Stock Risk, §4.3 Planned Production, §4.4 Slipped Plans, §4.5 Open POs) with full design-system treatment.

**Per-block subtasks** (similar shape — fetch hook → block component → refactor placeholder to live block → mobile reflow → freshness chip + source citation → test → commit). Each block gets its own task with files listed below. Bite-sized tasks within each block follow the same TDD cadence as T-C.

**File map (W2):**
- Create: `src/features/control-tower/blocks/StockRiskBlock.tsx` (consumes existing `/api/v1/queries/inventory/flow?at_risk_only=true&horizon_weeks=2`)
- Create: `src/features/control-tower/blocks/PlannedProductionBlock.tsx` (consumes `/api/v1/queries/production-plan` with date filter — see GAP-2 below)
- Create: `src/features/control-tower/blocks/SlippedPlansBlock.tsx` (refactored from existing inline; uses new primitives)
- Create: `src/features/control-tower/blocks/OpenPOsBlock.tsx` (consumes `/api/v1/queries/purchase-orders` with client-side filter; GAP-4 server-side filter optional)
- Modify: `src/app/(shared)/dashboard/page.tsx` — wires Layer 2 blocks; removes corresponding placeholders

**Backend (W1) — only if needed:**
- GAP-2 (production-plan date-range filter): inspect existing endpoint shape; if `date_from`/`date_to` params don't exist, add them. No schema change needed (table has `plan_date`).
- GAP-4 (PO date filter): defer to v1.1 unless typical PO row count >200.

#### Tasks 16–19 (one per block, 6 steps each)

Detailed steps in `docs/plans/2026-05-02-dashboard-T-D-tasks.md` (will be authored at tranche start). Skeleton:

- [ ] **T-D.16 §4.2 Stock Risk:** consume `at_risk_only=true&horizon_weeks=2`; render compact list (max 10 desktop / 5 mobile); `risk_tier` badge per inventory_flow §3.4 (do NOT re-derive); deep-links per W4 §4.2; "Plan run →" badge on each row; "Blocker →" badge if item appears in §4.6/§4.7.
- [ ] **T-D.17 §4.3 Planned Production:** 7-column day grid (`Sun..Sat` from today's day-of-week, rolling 7d per W4 §13 DCT2-1); `BOM mismatch dot icon` deferred to v1.1 per W4 §13 DCT2-6.
- [ ] **T-D.18 §4.4 Slipped Plans:** refactor existing inline; 7-day backward window; explicit footer copy per W4 §4.4; source-correct (`from_plan_id` per signal #18).
- [ ] **T-D.19 §4.5 Open POs:** two sub-sections (overdue / due); `total_value_net` OMITTED per W4 §13 DCT2-5 unless W1 confirms field exposure during this tranche; client-side date filter; deep-link per W4 §4.5.

Each task ends with: typecheck + build + test + verifier + commit + push.

#### Task 20: T-D acceptance gate

- [ ] Step 1: Verifier: all four blocks render against live data; deep-links HTTP 200; mobile @ 390px reflows correctly; only §4.3 horizontal-scrolls (W4 §6.5 invariant); each block has freshness chip + source citation.
- [ ] Step 2: Tom morning-glance test on Layer 1 + Layer 2 combined.

---

### Chunk 5: Layer 3 — Recommendations & Health (T-E)

Goal: ship the bottom-layer blocks (§4.6 Blocked Production, §4.7 Blocked Purchase, §4.8 Integration Freshness, §4.9 Top-5 Exceptions).

**File map (W2):**
- Create: `src/features/control-tower/blocks/BlockedProductionBlock.tsx`
- Create: `src/features/control-tower/blocks/BlockedPurchaseBlock.tsx`
- Create: `src/features/control-tower/blocks/IntegrationFreshnessBlock.tsx` (verbatim mirror of producer-side contract — 7 producers, 4 states, no derivation)
- Create: `src/features/control-tower/blocks/TopExceptionsBlock.tsx` (uses existing `resolveExceptionDeepLink()` helper per W4 §10 row 10)

#### Tasks 21–24

- [ ] **T-E.21 §4.6 Blocked Production:** per W4 §4.6, max 5 desktop / 3 mobile; demand_qty + earliest_shortage_at; "Fix this →" links to `/admin/boms`; uses Hebrew label map verbatim from `planning_unresolved_demand_blockers_contract.md`.
- [ ] **T-E.22 §4.7 Blocked Purchase:** per W4 §4.7; identical shape; three category filters; uses PBR-4 normalized `display_id/display_name/display_kind`.
- [ ] **T-E.23 §4.8 Integration Freshness:** 7-row table, columns per W4 §4.8; consumes `current_state` verbatim; renders "5 fresh · 1 warning · 0 critical · 1 never_ran" header. NO derived staleness.
- [ ] **T-E.24 §4.9 Top-5 Exceptions:** client-side LIMIT 5; uses existing `resolveExceptionDeepLink()` helper.

Each ends with: typecheck + build + test + verifier + commit + push.

#### Task 25: T-E acceptance gate (full block coverage)

- [ ] Step 1: Verifier: 9 blocks of W4 §4 all live; W4 §11 acceptance criteria all PASS (block presence and order, empty-state coverage, role-gate verification, deep-link verification, freshness-banner verification, mobile @ 390px verification, no-write verification, loading-state verification, error-state independence verification, caveat-footer verification, gap-closure precondition verification).
- [ ] Step 2: Emit `RUNTIME_READY(DashboardControlTowerV2-Complete)` (W4 §13 DCT2-7 suggested name; W2 may rename).
- [ ] Step 3: Tom **FULL-GO** checkpoint: visual acceptance on real device (desktop + mobile).

---

### Chunk 6: Interaction layer (T-F)

Goal: layer Cmd-K palette, time-scope chips (sticky), URL filter state, hover-preview popovers, J/K keyboard nav. This is what makes the surface feel "smart" and "interactive" — Tom's words.

**File map:**
- Create: `src/features/control-tower/CommandPalette.tsx` (uses `cmdk` library)
- Create: `src/features/control-tower/StickyFilterBar.tsx` (wraps `<TimeScopeChips>` + `<SeverityChips>` + `<SourceChips>`)
- Create: `src/features/control-tower/RowHoverPreview.tsx` (Radix popover; reusable across blocks)
- Create: `src/lib/control-tower/use-keyboard-nav.ts` (J/K/Enter row navigation)
- Modify: `src/app/(shared)/dashboard/page.tsx` — wraps page in `<CommandPalette>` provider; adds `<StickyFilterBar>` to top
- Modify: every Layer 2/3 block — accepts `?scope=` from filter bar; adds `RowHoverPreview` to its rows

#### Tasks 26–30

- [ ] **T-F.26 Cmd-K Command Palette:** install `cmdk`; build provider; route + item + supplier + exception search; default-empty hits = role's primary actions; Cmd+K / Ctrl+K hotkey.
- [ ] **T-F.27 Sticky Filter Bar:** wraps TimeScopeChips + SeverityChips + SourceChips; URL state via `useSearchParams`; `position: sticky; top: 0; z-40`.
- [ ] **T-F.28 Row Hover Preview:** Radix popover triggered on row hover (200ms delay); shows full row detail; same content shown on tap on mobile (different trigger).
- [ ] **T-F.29 Keyboard Navigation:** J/K (or arrows) move focus; Enter activates; Esc clears. Respect `prefers-reduced-motion` and `display: contents`.
- [ ] **T-F.30 URL Filter Plumbing:** every block reads `?scope=` and re-renders; add `?severity=` to §4.9 and §4.6/§4.7.

Each ends with: typecheck + build + test + verifier + commit + push.

#### Task 31: T-F acceptance gate

- [ ] Step 1: Verifier: Cmd-K opens via shortcut; finds "FG-COC-1L" returns deep-link; sticky filter bar updates URL without page reload; J/K navigates; hover preview opens within 200ms.
- [ ] Step 2: Accessibility audit: every interactive element has `aria-label`; Cmd-K dialog traps focus; keyboard nav announces row content via screen reader.

---

### Chunk 7: Mobile pass + bottom nav (T-G)

Goal: mobile-first treatment for the consolidated dashboard. Bottom nav, horizontal-scroll status strip, day-strip §4.3, tap-target audit.

**File map:**
- Create: `src/components/MobileBottomNav.tsx` (3-tab fixed-bottom navigation)
- Modify: `src/app/(shared)/layout.tsx` (or root layout) — render `<MobileBottomNav>` on mobile breakpoints
- Modify: every Layer 2/3 block — apply mobile row caps (max 5 desktop, 3 mobile per W4 §6.1)
- Modify: `<StatusStrip>` — `overflow-x-auto` on mobile

#### Tasks 32–35

- [ ] **T-G.32 Bottom nav:** 3 tabs (בית / מלאי / משימות); hides on scroll-down, shows on scroll-up; tap targets ≥44×44px.
- [ ] **T-G.33 Status strip mobile:** `flex flex-row overflow-x-auto snap-x` with `snap-start` per tile.
- [ ] **T-G.34 §4.3 day-strip:** 7 columns scrollable horizontally (the only authorized horizontal scroll per W4 §6.5); each cell tap → `/planning/production-plan?date=…`.
- [ ] **T-G.35 Tap target audit:** every clickable element ≥44×44px. Run via Playwright @ 390×844 viewport, assert via `bbox.width >= 44 && bbox.height >= 44` for every `<a>` / `<button>` / `[role=button]`.

#### Task 36: T-G acceptance gate

- [ ] Step 1: Mobile Playwright snapshot. Confirm: above-the-fold = quick-action row + status strip + Critical Today block visible; bottom nav fixed at viewport-bottom.
- [ ] Step 2: Real-device test (iPhone Safari + Android Chrome).
- [ ] Step 3: Tom mobile morning-glance test: "Can you tell me what needs attention in <5 seconds without scrolling?"

---

### Chunk 8: Polish + animation + a11y + `/planning/inventory-flow` parity (T-H)

Goal: final polish layer. Counter animations on KPI changes, 200ms pulse on row state flip, sparklines populated where read-models support, axe AAA audit, design-system applied to `/planning/inventory-flow` for consistency.

#### Tasks 37–42

- [ ] **T-H.37 Counter animations:** `framer-motion` or `react-countup` on KPI tile values; respect `prefers-reduced-motion`.
- [ ] **T-H.38 Row pulse:** 200ms background flash on rows whose status changed in last refresh.
- [ ] **T-H.39 Sparklines populated:** add 14-day history sub-fields to `v_dashboard_status_strip` (W1 backend extension; harness signal #N+1); render in tiles 2/3/4.
- [ ] **T-H.40 axe AAA audit:** zero violations across `/dashboard` and `/admin/system-health`. Color contrast ≥7:1 every body text. Every interactive element has `aria-label` or visible label.
- [ ] **T-H.41 `/planning/inventory-flow` parity:** apply same StatusPill, KPITile, FreshnessChip, SourceCitation, sticky filter bar, Cmd-K trigger to this surface. Visual consistency with the dashboard.
- [ ] **T-H.42 Reduced-motion + RTL audit:** `prefers-reduced-motion: reduce` disables counters and pulse; LTR layout preserved (per CLAUDE.md "No full RTL layout in v1") but Hebrew text rendering verified via Playwright text-content snapshot tests.

#### Task 43: T-H acceptance gate (final ship)

- [ ] Step 1: Full E2E suite (Playwright) green: all 9 blocks render; deep-links HTTP 200; mobile + desktop snapshots match approved baselines.
- [ ] Step 2: axe-core: zero AAA violations.
- [ ] Step 3: Lighthouse score ≥90 on Performance, Accessibility, Best Practices, SEO (for `/dashboard` route).
- [ ] Step 4: Tom **FULL-GO** acceptance: morning-glance test on real desktop + real phone.

---

## Part 8 — Tom Tax checklist (daily-friction items per `feedback_tom_lens_audit_calibration.md`)

Every item below MUST be answered "no friction" for the dashboard to ship FULL-GO.

- [ ] Can Tom tell within 5 seconds, on his phone, that the system is or isn't OK this morning?
- [ ] Can Tom tell which item runs out first this week without opening another page?
- [ ] Can Tom tell which planning recommendations are blocked, and what to fix, in one click?
- [ ] Can Tom run a planning run from the dashboard quick-action without opening 3 menus?
- [ ] Can Tom see when LionWheel last successfully synced, without going to /admin/integrations?
- [ ] When break-glass is active, does the dashboard refuse to render anything stale silently? (Per W4 §8.2 — staleness is surfaced, never hidden.)
- [ ] When freshness=critical for a producer, do dependent blocks display the staleness banner? (Per W4 §8.2 + §8.3.)
- [ ] Can a viewer role open the dashboard and not see hidden actions they could fail to call? (Per W4 §11.3.)
- [ ] Can Tom paste a `/dashboard?scope=14d&severity=critical` URL into another planner's chat and they see exactly the same view?
- [ ] When zero exceptions are open, does the dashboard explicitly say "כל המערכת תקינה" — not just hide the block? (Per W4 §10 row 6 operator-trust principle.)

---

## Part 9 — Small things that will hurt later (per `feedback_tom_lens_audit_calibration.md`)

These are the things that aren't blockers today but will rot the dashboard if not fixed at this build.

1. **Time-scope state surviving across navigation.** When Tom clicks `7d → 14d` then drills into an exception, then comes back, does `?scope=14d` survive? It must, or the daily flow breaks. Fix at T-F.30 by reading from URL on mount.
2. **`as_of` on every response.** Every `api_read.*` view used by the dashboard must return `as_of` (response generation timestamp). Inventory-flow already does. Confirm during T-D for `production-plan` and `purchase-orders`.
3. **No "loading forever" failure mode.** TanStack Query default retry on error = 3. After 3 retries, `isError=true`. Each block MUST render `<ErrorState>` with retry button per W4 §5.11. Don't let any block hang on a perpetual skeleton.
4. **No silent role downgrade.** If Tom's session expires mid-page, every refetch fails with 401. The page MUST show a "session expired — log in" toast and redirect, not silently render empty blocks. Wire at T-A via auth middleware integration.
5. **No mock/placeholder data ever.** Per W4 §10 row 6 + `planning_unresolved_demand_blockers_contract.md` §10. Every empty state is honest. Every `Coming next` placeholder reveals "awaiting read-model" badge.
6. **Sparklines must NOT render fake history.** If 14-day history is null, render the KPI tile WITHOUT a sparkline. Don't generate fake data points.
7. **Sidebar nav label** stays English "Dashboard" per Q-2 decision (2026-05-02). DO NOT rename to Hebrew. Page H1 inside the route may still read "Dashboard" or the existing greeting text — keep English in nav.
8. **Cmd-K must NOT find unauthorized routes.** Role gate applied at the search index level, not just at render time. Otherwise a viewer types "פתח admin" and sees admin entries that fail on click.
9. **Animation respect for `prefers-reduced-motion`.** Tom is fine; some users will have motion-sensitive disorders. Audit at T-H.42.
10. **`/dashboard/v2` → `/dashboard` redirect must be 308, not 307.** 308 is permanent and cacheable; 307 is temporary. We're permanently moving the route.
11. **The "Awaiting read-model" placeholder can NEVER ship in production for >2 weeks.** Each placeholder is a gap. T-D and T-E close them all. If T-D ships and T-E is delayed, the placeholders disappear (block hidden) rather than render — never let an empty placeholder linger as "we're working on it" while it goes stale.

---

## Part 10 — Decisions locked by Tom on 2026-05-02

All 7 questions resolved. Defaults adopted except Q-2 (sidebar label kept English for muscle memory). No item blocks T-A.

| # | Decision | Resolution |
|---|---|---|
| Q-1 | Status strip aggregation | **Single `v_dashboard_status_strip` read-model** (default). One round-trip; better on cellular. T-C.12 authors the W1 view. |
| Q-2 | Sidebar nav label | **"Dashboard"** (English, **NOT** "מגדל פיקוח"). Tom: preserve muscle memory. T-B.10 keeps existing English label; do NOT rename. |
| Q-3 | Quick-action row count | **6 actions** (default): RUN_PLANNING, OPEN_PRODUCTION_PLAN, OPEN_EXCEPTIONS, OPEN_INBOX, OPEN_GR, OPEN_COUNT. Goods Receipt + Physical Count one click from morning view per operator daily flow. Diverges additively from W4 §7.1 (4 actions); non-conflicting since W4's 4 are a subset. |
| Q-4 | `/planning/inventory-flow` scope | **Same primitives, layout preserved** (default). T-H.41 applies StatusPill, KPITile, FreshnessChip, SourceCitation, sticky filter bar, Cmd-K trigger. Existing timeline + per-item-row layout preserved. No separate redesign plan. |
| Q-5 | Forecast accuracy tile | **Defer to v1.1** (default). Status strip ships with 4 tiles. W1 does NOT author `v_forecast_accuracy_last_week` in this plan. |
| Q-6 | Cmd-K search index | **Full search** (default): routes + items + suppliers + exceptions. Linear-style. Role-gate applied at index level (per Part 9 small-things item #8). |
| Q-7 | Mobile bottom nav | **3 tabs** (default): בית / מלאי / משימות. T-G.32 implements as specified. |

**Open authorization to start T-A:** None remaining. T-A is parallel-safe with all current corridors (no schema, no runtime, primitives only). Awaiting Tom's "go" to dispatch T-A.

---

## Part 11 — Acceptance criteria summary

This plan is "implemented correctly" when ALL of the following pass against the live production deployment:

### 11.1 W4 contract compliance
- All 11 W4 §11 acceptance gates PASS (block presence and order, empty-state coverage, role-gate verification, deep-link verification, freshness-banner verification, mobile @ 390px verification, no-write verification, loading-state verification, error-state independence verification, caveat-footer verification, gap-closure precondition verification).

### 11.2 Research-grounded design rules satisfied
- 5 hard rules of dashboard design (Few/Tufte/NN/g) all upheld — verifiable by visual inspection.
- 3-tone status pill discipline enforced (no 5-color palette anywhere).
- Per-widget freshness present on every block.
- One click = root cause; two clicks = action — verifiable by counting clicks on every "Open →" / "Fix this →" link.

### 11.3 Tom Tax (Part 8) zero friction
- Every checklist item answered "no friction".

### 11.4 Small-things-hurt-later (Part 9) all closed
- Every item in Part 9 either fixed at this build or explicitly deferred with reason.

### 11.5 FULL-GO criteria
- Tom morning-glance test PASS on real desktop AND real mobile.
- axe-core AAA: zero violations.
- Lighthouse Performance/Accessibility/Best Practices ≥90.
- All 43 implementation tasks committed and pushed; verifier PASS on each tranche acceptance gate.

---

## Part 12 — Out of scope (not v1)

- Reports tab (trends, historical analytics) — separate `/reports` surface; v1.1 or later
- Scenario / what-if sandbox — `/planning/runs` already serves this
- @mention / collaboration threads on exceptions
- Cycle-counting dashboard widgets (CLAUDE.md "Do not overbuild cycle counting in v1")
- FEFO / expiry / location / bin tracking (CLAUDE.md "No expiry logic in v1")
- Customer pricing widgets (CLAUDE.md)
- AI-prescriptive layer (Kinaxis-style) — system already has `/planning/runs` recommendation engine; do not bolt on AI
- Multi-site control tower — one factory only
- Heatmap / risk-grid widgets — pointless at this scale
- OEE / MTBF / cycle-time KPIs — wrong vocabulary for recipe-driven plant

---

## Notes for the executor

- This plan is **research-grounded** but **flexible at the edges.** Tom's open questions (Part 10) shift specific tasks. Do not author T-C.12 backend until Q-1 answered. Do not author T-G.32 until Q-7 answered. Halt and request decision on `assumption_failure` or `data_failure` per `EXECUTION_POLICY.md`.
- Every commit ends with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` per repo convention.
- Push autonomously after each commit per `feedback_push_autonomously.md`.
- Mark each task `- [x]` as soon as it's done, not in batches.
- Use `superpowers:verification-before-completion` skill before claiming any tranche acceptance gate PASS.
- Use `superpowers:test-driven-development` skill at every task that touches code.
- This plan supersedes any inline "TODO" comments in `/dashboard/page.tsx` or `/dashboard/v2/page.tsx`.

---

**Plan authored:** 2026-05-02 by Claude Opus 4.7 (1M context) for Tom Wallach.
**Research basis:** 4 parallel research agents synthesizing Stephen Few, Edward Tufte, Nielsen Norman Group, Cole Knaflic, Refactoring UI, IBM Carbon, Atlassian Design, Tulip, Siemens Opcenter, Rockwell FactoryTalk, GE Proficy, Katana MRP, Cin7, Kinaxis, o9, Blue Yonder, IBM SCIS, FourKites, Linear, Vercel, Stripe, Datadog, Grafana, Sentry. Full agent transcripts preserved in conversation log.
**Authority:** W4 contract `dashboard_control_tower_v2_coverage_requirements.md` (existing) + Tom's directive 2026-05-02 ("really really accessible, smart, beautiful, practical, interactive, colorful, simple").
