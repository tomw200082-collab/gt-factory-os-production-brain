# Planning UX Full-Pass Handoff Packet
## All Planning + Dashboard Screens — Consistency + Significant Improvement

**Status:** READY_FOR_IMPLEMENTATION
**Authored by:** ux-flow-architect + visual-system-designer (combined)
**Date:** 2026-05-08
**Tom approval:** Explicit verbal approval 2026-05-08 — "תשפר משמעותית את הUXUI בכל הדפים"
**Masterplan ref:** PRODUCTION/docs/planning/PLANNING_SCREENS_UPGRADE_MASTERPLAN.md
**Portal tip at audit:** 9e2212e (window2-portal-sandbox main)
**Authority hierarchy:** CLAUDE.md > EXECUTION_POLICY.md > CURRENT_STATE.md > this packet

---

## Section 1 — Authority and Scope

**Tom decisions recorded in this packet:**
- DEC-1 (2026-05-08): Blockers page ("חסמים בתכנון") is unified to English/LTR — the Tom-lock from 2026-04-27 is superseded by this explicit 2026-05-08 approval.
- DEC-2 (2026-05-08): Forecast detail default display = 2 months (frontend-only cap, no backend change).
- DEC-3 (2026-05-08): Decorative features on blockers page (mood map, kanban columns, escalation levels = I5–I12) are removed. Core 5-question UX + I1 (category progress) + I2 (due dates) are kept.
- DEC-4 (2026-05-08): Full UX/UI improvement pass on all planning + dashboard screens.

**Screens in scope:**
1. `/dashboard` (graduation + quick-actions — see companion packet `dashboard-graduation-handoff-2026-05-08.md`)
2. `/planning` (planning hub/index)
3. `/planning/runs` (runs list)
4. `/planning/runs/[run_id]` (run detail)
5. `/planning/runs/[run_id]/recommendations/[rec_id]` (rec detail)
6. `/planning/forecast` (forecast versions list)
7. `/planning/forecast/[version_id]` (forecast detail — 2-month cap only)
8. `/planning/inventory-flow` (reference implementation — light touch)
9. `/planning/blockers` (English conversion + simplification)
10. `/planning/production-plan` (icon discipline + consistency)
11. `/planning/weekly-outlook` (read + apply universal rules)

**Out of scope (do not touch):**
- `/planning/production-simulation` — Window B risk (BOM functions coupled)
- `/planning/boms` — admin surface
- `/planning/forecast/new` — already clean from Wave 2
- Any backend file (`api/**`, `db/**`)
- `portal_ux_standard.md`, `portal_language_direction_audit.md`
- `tailwind.config.ts`, `globals.css`
- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`

---

## Section 2 — Universal Rules (apply to EVERY screen in scope)

These rules must be applied uniformly. No exceptions unless a screen has an explicit override noted in Section 3.

### U1 — FreshnessBadge
**Problem:** Five competing freshness vocabularies exist across screens: `<FreshnessBadge>`, inline `fmtRelative()`, `fmtRelativeAndAbsolute()`, static `<Badge>Live</Badge>`, and hardcoded `#22D3A3` pulsing dot.

**Rule:** Every data-freshness signal uses `<FreshnessBadge>` imported from `@/components/badges/FreshnessBadge`. Remove all inline freshness variants. Remove hardcoded hex `#22D3A3` from dashboard v1 freshness header.

**Reference implementation:** `src/app/(planning)/planning/inventory-flow/page.tsx` — this is the gold standard.

### U2 — Icon discipline
**Problem:** Most screens import 30–50 Lucide icons; many are never rendered.

**Rule:** Audit every icon import. Remove any icon that is not directly referenced in a JSX `<IconName />` expression in the same file. Apply to the page file AND every `_components/*.tsx` in the same directory.

### U3 — WorkflowHeader consistency
**Rule:** Every screen uses `<WorkflowHeader eyebrow="..." title="..." description="..." />`. The eyebrow must match the navigation context ("Planning workspace", "Planner workspace", "Factory floor"). No raw `<h1>` outside WorkflowHeader.

### U4 — Shared empty/loading/error states
**Rule:** All loading states use `animate-pulse` skeleton or `<Loader2>` spinner from shared components. All empty states use `<EmptyState>` from `@/components/feedback/states`. All error states use the `border-danger/30 bg-danger-softer` card pattern (already established). No one-off inline skeleton divs unless the existing component library genuinely cannot cover the case.

### U5 — Names not IDs
**Rule:** Every row, card, and table cell that references an item, component, supplier, or user shows the human-readable name as the primary label. IDs appear only as `text-fg-faint text-[10px]` secondary text or in `title=` attributes. No raw UUIDs as primary content ever.

### U6 — English/LTR everywhere
**Rule:** All UI copy in planning + dashboard screens is English, LTR. No Hebrew strings in JSX (per Tom DEC-1 above and global portal standard). Hebrew may appear only in data values returned by the API (e.g., item names, notes), never in structural UI labels, buttons, headers, or helper text.

### U7 — Status badge vocabulary
**Rule:** Use the shared `<Badge>` / `<StatusBadge>` component (already imported on most screens). Tone mapping: `success` = completed/published/active, `warning` = running/draft/pending, `danger` = failed/blocked/critical, `muted` = superseded/archived/inactive. No custom inline badge styling.

---

## Section 3 — Per-Screen Specifications

### S1 — `/planning` (Planning Hub / Index)
**File:** `src/app/(planning)/planning/page.tsx`
**Current state:** 43k token hub with 30+ icon imports, live status queries for forecast/jobs/demand coverage/planning runs.
**Goal:** A clean operational "command center" — answer the 5 planner questions at a glance: (1) Is forecast current? (2) Is LionWheel healthy? (3) Is demand coverage resolved? (4) What did the last run produce? (5) What needs attention?

**Required changes:**
- Apply U1–U7
- Simplify the status cards to 4 clear tiles: Forecast freshness, Last run (status + rec count), Blockers count, LionWheel sync health
- Each tile is a link-card to the relevant detail screen
- Remove decorative metric widgets that are not backed by live data (placeholder charts, streaks, medals, etc.)
- Quick-nav section at bottom: 5 link buttons to Forecast / Runs / Production Plan / Inventory / Blockers — matching `PLANNING_SECTIONS` already defined in the file
- WorkflowHeader: eyebrow="Planning workspace", title="Planning", description="Forecast → run → produce. Status at a glance."

### S2 — `/planning/runs` (Runs List)
**File:** `src/app/(planning)/planning/runs/page.tsx`
**Current state:** 47k tokens, 40+ icon imports, heavy decorative stats.
**Goal:** Clean, scannable list. One prominent "Trigger planning run" CTA. Status filter that actually works.

**Required changes:**
- Apply U1–U7
- Table columns: Run date/time | Status (badge) | Recommendations | Exceptions | Triggered by
- "Trigger planning run" = primary CTA button (Type A, top-right) — planner/admin only
- Status filter: tabs or segmented control — draft / running / completed / failed / superseded
- Each row is clickable → `/planning/runs/[run_id]`
- Running state: auto-refreshes every 5s (already likely implemented — verify and keep)
- WorkflowHeader: eyebrow="Planning workspace", title="Planning runs", description="Each run turns the active forecast into purchase and production recommendations."
- Remove any stats widgets, progress bars, charts that are decorative/placeholder
- Remove all unused icon imports

### S3 — `/planning/runs/[run_id]` (Run Detail)
**File:** `src/app/(planning)/planning/runs/[run_id]/page.tsx`
**Goal:** Clear run summary with rec list + exception list. Click-through to each rec.

**Required changes:**
- Apply U1–U7
- Run summary hero: status badge + triggered_at + triggered_by + rec count + exception count
- Two tabs: Recommendations | Exceptions
- Rec rows: item NAME (not ID), rec_type, quantity, priority badge
- Exception rows: item NAME (not ID), exception_type label (human-readable), severity
- Each rec row is clickable → `/planning/runs/[run_id]/recommendations/[rec_id]`
- Exception rows deep-link to the relevant fix route (this is R1-5 from the original T1)

### S4 — `/planning/runs/[run_id]/recommendations/[rec_id]` (Rec Detail)
**File:** `src/app/(planning)/planning/runs/[run_id]/recommendations/[rec_id]/page.tsx`
**Goal:** Full rec context — why this recommendation exists, what to do, what the BOM breakdown looks like.

**Required changes:**
- Apply U1–U7
- RecDetailHeader: item NAME prominently, rec_type as human label ("Purchase order recommended" not "PO_REC"), quantity with UOM
- Component breakdown table: component NAME (not ID), required_qty, available_qty, shortage_qty
- Open POs card: PO number + supplier NAME (not ID) + eta + qty
- Exceptions card: clean list with human labels

### S5 — `/planning/forecast` (Forecast Versions List)
**File:** `src/app/(planning)/planning/forecast/page.tsx`
**Goal:** Clear list of forecast versions. Draft at top. Easy to create new.

**Required changes:**
- Apply U1–U7
- "New forecast" = primary CTA (Type A, top-right)
- Version rows: period label (e.g., "May–Jun 2026") | status badge | created by | items count | published_at
- Draft rows: highlighted with a subtle `bg-accent-soft/10` background
- Published row: most recent = "Active" badge in success tone
- WorkflowHeader: eyebrow="Planning workspace", title="Forecasts", description="Monthly demand forecast drives purchase and production recommendations."
- Remove any decorative charts or stats that are not backed by live API data

### S6 — `/planning/forecast/[version_id]` (Forecast Detail)
**File:** `src/app/(planning)/planning/forecast/[version_id]/page.tsx`
**Current state:** Excellent Wave 2 redesign — minimal changes needed.

**Required changes:**
- **2-month cap (DEC-2):** In the `buckets` useMemo (lines ~306–312), change the `computeMonthBuckets` call to cap at 2 months for monthly cadence:
  ```typescript
  const displayCount =
    version.cadence === "monthly"
      ? Math.min(version.horizon_weeks, 2)
      : version.horizon_weeks;
  return computeMonthBuckets(version.cadence, version.horizon_start_at, displayCount);
  ```
  This is the ONLY required change on this file. Do not alter any other logic.

### S7 — `/planning/inventory-flow` (Inventory Flow)
**File:** `src/app/(planning)/planning/inventory-flow/page.tsx`
**Current state:** Reference implementation. Already correctly uses FreshnessBadge.

**Required changes:**
- Apply U2 (icon discipline audit only)
- Apply U5 (verify names not IDs — it should already be correct)
- Apply U7 (verify status badge vocabulary)
- DO NOT restructure the grid or change the week/day navigation — it works well

### S8 — `/planning/blockers` (Blockers Worklist)
**File:** `src/app/(planning)/planning/blockers/page.tsx`
**Current state:** 47k tokens. Hebrew title + labels. I1–I12 improvement features. Core 5-question UX solid but buried.

**Required changes (per DEC-1 + DEC-3):**

**English conversion:**
- Page title: `"חסמים בתכנון"` → `"Planning blockers"`
- Subtitle: `"פריטים עם ביקוש שלא הפכו להמלצת רכש או ייצור שמישה"` → `"Items with demand that could not be turned into a usable purchase or production recommendation"`
- All Hebrew labels in `labelMaps.ts`, `types.ts`, and component files → English
- Hebrew tag presets (`TAG_PRESETS_HE`) → English: `["Urgent", "Waiting", "Blocked", "Partial fix", "Long term"]`
- Escalation levels → English: `["None", "Team", "Management"]`
- Kanban columns → English: `["Open", "In progress", "Resolved"]`
- Blocker category labels → English
- Fix action labels → English
- Severity labels → English

**Feature simplification (DEC-3 — remove I5–I12):**
Remove from the page these localStorage-backed features:
- Mood map (I11) — `MOOD_OPTIONS`, `MoodValue`, per-row mood state
- Mini kanban (I12) — `KANBAN_COLS_HE`, kanban column assignment per row
- Escalation level assignment (any `EscalationLevel` state)
- Message/note tagging per row (any `MessageSquare` / per-row note state)
- The `TAG_PRESETS_HE` tag assignment UI (the tag input per row)

**Keep (DEC-3):**
- I1 — Per-category resolution progress (BarChart2 toggle + progress bars)
- I2 — Blocker due date assignment (CalendarCheck + localStorage-persisted)
- The core 5-question UX (display_name, blocker reason, severity, fix action, fix route)
- Sort by severity / demand / date
- Filter bar

**UX improvement:**
- WorkflowHeader: eyebrow="Planning workspace", title="Planning blockers", description="Items with demand that have no usable recommendation. Fix these before the next planning run."
- Apply U1–U7
- Severity badges: `danger` = critical, `warning` = high, `muted` = medium/low
- Fix action button: Type B secondary, right-aligned per row, label = the human-readable fix action
- Empty/all-clear state: large, calm, "No blockers — the last run covered all demand" message

### S9 — `/planning/production-plan` (Daily Production Plan)
**File:** `src/app/(planning)/planning/production-plan/page.tsx`
**Current state:** 58k tokens. 40+ icon imports. Complex week-nav + add/edit/cancel flows.

**Required changes:**
- Apply U1–U7
- Keep the core functionality: week navigation, add planned production, edit qty/date/notes, cancel with reason, status display (planned / completed / cancelled)
- WorkflowHeader: eyebrow="Planning workspace", title="Production plan", description="Plan production for the week. Inventory updates only when actuals are reported."
- Status badges: `warning`=planned, `success`=completed, `danger`=cancelled
- "Add production" = Type A primary CTA
- Week navigation: simple prev/next with current week label ("Week of May 5–11, 2026")
- Remove decorative features that are not backed by API data (star ratings, heart-pulse widgets, etc.)
- Reduce icon imports to only those actually rendered

### S10 — `/planning/weekly-outlook` (Weekly Outlook)
**File:** `src/app/(planning)/planning/weekly-outlook/page.tsx`
**Current state:** 49k tokens — not yet read in detail.

**Required changes:**
- **First:** Read the full file to understand its current structure and data sources
- Apply U1–U7 after reading
- Ensure the screen answers "what does this week look like for production and supply?" clearly
- Clean navigation if present
- Remove any placeholder/decorative elements
- Consistent WorkflowHeader pattern

---

## Section 4 — Implementation Order (recommended)

The executor should work in this order to maximize coherence:

1. **Forecast detail 2-month cap** (S6) — single-line change, zero risk, quick win
2. **Universal rules audit pass** on inventory-flow (S7) — lightest screen, establishes the reference you'll copy from
3. **Planning hub** (S1) — sets the navigation context for all other screens
4. **Runs list** (S2) — high-value, heavily used
5. **Blockers** (S8) — English conversion + simplification
6. **Production plan** (S9) — largest screen, do after patterns are established
7. **Runs detail** (S3) + **Rec detail** (S4) — pair these (same route tree)
8. **Forecast list** (S5) — companion to forecast detail
9. **Weekly outlook** (S10) — read + apply after all other patterns locked

Dashboard graduation is covered by `dashboard-graduation-handoff-2026-05-08.md` (companion packet). Do that as part of the same run if context allows, or in a second pass.

---

## Section 5 — What success looks like

**Before the run ends, the executor must verify:**

1. Every screen in scope has FreshnessBadge, not inline freshness
2. No screen has `#22D3A3` hardcoded hex in the portal source
3. Blockers page has zero Hebrew strings in structural JSX (data values from API are OK)
4. Forecast detail shows max 2 month columns for monthly cadence
5. Every screen's icon import list contains only icons referenced in JSX
6. No raw UUIDs visible as primary content in any row or card
7. TypeScript compiles without new errors (`npx tsc --noEmit` in window2-portal-sandbox)
8. No new lint errors introduced

**Handoff ends with:** STATUS, files changed list, tsc result, any stop conditions tripped.

---

## Section 6 — Stop conditions

Stop and report (do not proceed) if:
- Any backend file would need to change to implement a finding
- The blockers page has a data contract that requires Hebrew strings (impossible — it's UI only)
- A screen depends on a RUNTIME_READY signal that hasn't been emitted
- TypeScript errors in existing code block the edit (do not suppress — investigate)
- Any change would touch the production-simulation page (Window B risk)

---

**Owner:** ux-flow-architect + visual-system-designer
**Approver:** Tom (verbal approval 2026-05-08)
**Last updated:** 2026-05-08
