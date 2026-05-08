# Day-1 Cutover + Forecast Workspace v2 — Design

**Date:** 2026-04-30
**Author:** Claude (autonomous loop run)
**Status:** Draft for Tom review

---

## Executive summary

Two coupled deliverables:

1. **Day-1 cutover (path Y locked):** ship tomorrow with the existing portal + 25 loops of polish already deployed. Tom is the sole user. Excel goes read-only. Forecast goes through the existing MVP plus a "seed-all-active-FG" enhancement; the full Forecast Workspace v2 ships post-Day-1 in a separate cycle.

2. **Forecast Workspace v2 (post-Day-1):** Stripe/Vercel-light, Anaplan-style stacked-measure pivot grid. Tom-locked aesthetic (β) and approach (α) from the brainstorm dialog 2026-04-29.

This document consolidates locked scope, the shipped polish, the open work for tomorrow's cutover, and the Workspace v2 spec.

---

## Part A — Day-1 cutover (path Y)

### A.1 Scope (all locked in earlier brainstorm)

- **Single user:** Tom (admin) only on Day 1.
- **Self-approval:** allowed for `role ∈ {admin, planner}`. Currently the handlers reject `caller == reporter` with 409. The policy change has been spec'd; backend handler edit + pgTAP follow on a separate W1 dispatch after this design lands.
- **LionWheel silent-drop rule:** unmappable SKUs from LionWheel are dropped silently — no exceptions, no blockers, no inbox entries, no auto-add to `items`. The system is the source of truth for products. This is a permanent rule, not just Day-1.
- **Excel disposition:** full cutover the morning of Day 1. After the count, Excel is export-only. Rollback path = paper forms + back-entry, not Excel-as-editor.
- **Forecast UI for Day-1:** existing MVP at `/planning/forecast` + a "seed-all-active-FG" button. Workspace v2 deploys 4–5 days after Day-1.

### A.2 What's shipped (25 loops on `gt-factory-os-portal/main`)

**Login surface:**
- Resend with 30s cooldown countdown ("Resend in 23s").
- "Use a different email" affordance.
- Magic-link expiry note (1 hour, single-use).
- Mail icon + brand mark above the card + page background polish.
- Footer with portal name + sign-out + status links.
- Callback errors mapped to operator-facing copy by code (access_denied / otp_expired / pkce / etc.) instead of raw machine strings.
- Open Gmail deep-link for `@gmail.com` / `@gteveryday.com` addresses.
- aria-live regions on status changes.
- Better focus rings, disabled-button rationale, env-error operator hint.

**Dashboard:**
- Critical-exceptions banner conditionally rendered above the stat strip when `inboxRows.severity === 'critical'` count > 0; lists up to 3 sample summaries with overflow count and primary CTA into `/inbox?view=exceptions&sort=severity_then_age`.
- Quick-Actions block reordered from last position to Block 2 (right after stat strip) — common daily tasks reachable without scrolling.
- Header description tightened; "as of HH:MM" badge added so render-freshness is glanceable.
- All seven existing blocks preserved.

**TopBar:**
- Non-prod env chip ("PREVIEW" / "DEV") rendered when `NEXT_PUBLIC_VERCEL_ENV` is non-production. Hidden in prod and when dev-shim is active (FAKE SESSION pill already covers that case).

**SideNav:**
- Filter input at the top of the sidebar (case-insensitive substring match against label). Esc clears + blurs. Auto-expands collapsible groups when filter is active.
- Theme toggle (Sun/Moon) added to UserCard footer for one-click access.

**Admin list pages (4):** /admin/items · /admin/components · /admin/supplier-items · /admin/suppliers
- 6 skeleton rows on load (vs bare "Loading…").
- Retry-able error callout with explicit message + Retry button bound to `refetch()`.
- 3-variant empty state ("no rows yet" / "no search match" / "no filter match") with Reset-filters and "+ New X" actions.

**Operator forms (4):** /ops/stock/physical-count · /ops/stock/receipts · /ops/stock/waste-adjustments · /ops/stock/production-actual
- SectionCard-wrapped skeleton on master data load.
- Retry-able error callout when masters fail.

**Planning surfaces (1):** /planning/runs
- Skeleton rows + retry pattern on the planning runs list.

**PO surface (1):** /purchase-orders
- Skeleton rows + retry pattern on the PO list.

**Jobs monitor (1):** /admin/jobs
- Aggregate health badges in header (X jobs · Y failed/all healthy · Z running).
- Live "next refresh in Xs" countdown.
- "Refresh now" button shows "Refreshing…" while pending.
- Skeleton + retry callout + better empty state.

### A.3 Open work for tomorrow's cutover (NOT shipped here)

These remain to land before Day-1 produces real ledger writes from operator workflows:

1. **Backend self-approval policy change.** W1 must edit `api/src/waste-adjustments/handler.approve.ts` and `api/src/physical-counts/handler.approve.ts` to permit `caller == reporter` when `role ∈ {admin, planner}`. Add pgTAP cases: ✓ admin self-approve 200, ✓ planner self-approve 200, ✓ operator self-approve 409, ✓ viewer self-approve 403. Effort: ~2 hours.

2. **LionWheel resolver silent-drop change.** W1 edits `api/src/integrations/lionwheel/resolver.ts` (~10 lines): when SKU is unmappable, log INFO with `unmappable_count` + `sample_skus[5]`; do NOT emit an exception. Add a unit test confirming 0 exceptions and 0 `v_planning_demand` rows for an unmappable input.

3. **Bulk-close stale exceptions.** Admin action through `/exceptions` inbox. ~41 historical LionWheel-triage entries to retire. UI already supports bulk acknowledge/resolve.

4. **"Seed-all-active-FG" forecast button.** Portal addition at `/planning/forecast/new`: one-click button that pre-populates the draft with all 68 active FG items at qty=0. Saves Tom ~30 min on Day-1 forecast entry.

### A.4 Day-1 timeline (recommended)

| Slot | Action | Surface | Approver |
|---|---|---|---|
| 08:00 | Open count snapshot for first item | `/ops/stock/physical-count` | n/a |
| 08:00–11:00 | Count physically across the catalog | (offline) | n/a |
| 11:00 | Submit each count + self-approve as admin (after §A.3 #1 lands) | physical-count form | Tom (self) |
| 11:00 | Bulk-close 41 stale LionWheel exceptions | `/exceptions` | Tom (admin) |
| 11:30 | Open new forecast draft + click "Seed all active FG" | `/planning/forecast/new` | n/a |
| 11:30–13:00 | Enter 8-week forecast monthly buckets across 68 items | forecast detail | n/a |
| 13:00 | Publish forecast version | publish button | atomic |
| 13:30 | Trigger planning run | `/planning/runs/new` | n/a |
| 14:00–15:00 | Review purchase recommendations + approve | `/planning/runs/[id]` | Tom (idem-by-idem) |
| 15:00 | Convert approved recs → POs (auto on approval per Phase 9) | server-side | atomic |
| Evening | Sanity scan of dashboard + exceptions + freshness | `/dashboard` | Tom (visual) |

**Failure-mode rule:** if any step blocks, paper forms + back-entry until resolved. **Never** edit Excel as a workaround.

### A.5 Risk log + rollback

| Risk | Tripwire | Rollback |
|---|---|---|
| Self-approval handler change introduces 500 | E2E approve test red | revert 2 handlers + 2 tests |
| LionWheel resolver drops legitimate demand | demand drops to 0 vs prior run | revert resolver to exception-emit path |
| Forecast seed button mis-fires | button shows error / no rows added | manual single-item add still works (existing) |
| Physical count freeze stuck | freeze not auto-releasing after auto-post | admin release through API/SQL |
| autosave conflict on forecast | edits lost on refresh | existing MVP unchanged; v2 not yet live so no regression |
| Vercel deploy breaks | live URL returns 5xx | revert to commit `b7278fb` |

---

## Part B — Forecast Workspace v2 (post-Day-1)

### B.1 Locked decisions

- **Layout pattern:** Anaplan-style stacked-measure pivot grid (option α from brainstorm dialog 2026-04-29).
- **Aesthetic:** Stripe/Vercel-light (option β). White surfaces · subtle borders · single accent color · tabular numerals · 8px baseline grid · subtle shadows · Inter + Heebo font stack.
- **Horizon:** 8 weeks (CLAUDE.md non-negotiable).
- **Granularity:** monthly first, then weekly toggle.
- **Versioning + freeze:** backend already supports; surface freeze in-cell as 🔒 icon.
- **Hebrew labels:** `תחזית` / `הזמנות פתוחות` / `סה״כ ביקוש` / `פרסם גרסה` / `טיוטה` / `פורסם` / `שונה מאז פרסום אחרון` / `מוקפא` / `סקור / בטל / פרסם` / `העתק מאשתקד` / `חלק שווה` / `+10% צמיחה`. Numbers stay LTR within RTL layout.

### B.2 Layout (single screen at `/planning/forecast/[version_id]/v2`)

- **Header:** version dropdown · monthly/weekly toggle · horizon picker · LionWheel freshness chip · primary "פרסם גרסה" button.
- **Left rail:** 68 SKUs · search · sort (alpha / category / volume / variance) · click → grid scrolls to that SKU.
- **Main grid:** 68 rows × 8 cols. Each SKU has 3 stacked sub-rows:
  - `תחזית` — editable. Baseline = grey-faint italic. Override = blue-bold. ⭐ = changed since last publish. 🔒 = freeze.
  - `הזמנות פתוחות` — read-only from LionWheel mirror. Click → drill to order list.
  - `⊕ סה״כ ביקוש` — computed. Click → inline popover: `1,200 = 800 forecast + 400 orders (3 orders)`.
- **Right side panel (collapsible):** sparkline (last 12 weeks) · last-year same-period comparison · notes · quick actions (`העתק מאשתקד` / `חלק שווה` / `+10% צמיחה` / `אפס שורה`).
- **Bottom bar:** `12 תאים שונו מאז פרסום אחרון. [סקור] [בטל] [פרסם]`

### B.3 Interaction model

- **Keyboard-first:** ← → ↑ ↓ Tab Enter for nav · Esc undo · Ctrl+Z · shift-drag for range fill · Ctrl+V from Excel block-paste.
- **Autosave:** debounced 800ms to `Working` version; `Publish` is one-click atomic snapshot.
- **Filter pills:** "רק עם הזמנות" · "רק שונו השבוע" · "רק קוקטיילים" · "רק שורות עם ⭐".
- **Decomposition popover:** click `סה״כ ביקוש` cell → tooltip inline; Esc closes.
- **Compare overlay:** dropdown "השווה ל-..." → previous published version overlays as delta column / cell-bg color.

### B.4 Technical contract

- **Routes (new):** `/planning/forecast/[version_id]/v2` — does not replace MVP; both coexist.
- **Endpoints:** reuse existing `/api/forecasts/save-lines` + `/api/forecasts/publish` + new `/api/v1/queries/orders/by-item-and-period?from=…&to=…&items=…` for the open-orders sub-row. The new endpoint is read-only and pulls from the existing LionWheel mirror.
- **Virtualization:** tanstack-virtual for the grid. 68 × 3 × 8 = 1,632 cells; without virtualization the browser will judder during edit.
- **State:** TanStack Query for reads; `useReducer` for local edit state; debounced `save-lines` mutation for autosave.
- **Layout:** RTL on `<html dir="rtl">` for the workspace (or `dir="rtl"` on a top wrapper if RTL-only-on-this-page); numbers and dates render LTR inside `<bdi>` wrappers per the Hebrew/RTL gotchas in S1 research §E.

### B.5 Tests required before merge

1. Playwright E2E real-HTTP: open new draft → seed 68 items → edit cells → keyboard nav → publish → verify DB rows match.
2. Visual regression: baseline screenshot of grid 68×8 light + dark themes.
3. a11y pass: tab order through all cells; aria-labels; focus rings visible.
4. RTL pass: layout RTL; input direction LTR per cell.
5. Idempotency: replay-publish on same version returns same response code (already covered by backend; surface in UI).
6. Conflict path: edit a frozen cell → server returns 409 → UI shows the freeze tooltip + rollback the local edit.

### B.6 Effort estimate

- New endpoint `/api/v1/queries/orders/by-item-and-period`: W1, ~3 hours including tests.
- Grid component + virtualization + RTL layer: W2, ~14 hours.
- Side panel + quick actions (incl. "copy from last year" — needs historical sales endpoint or skip if absent): W2, ~6 hours.
- Decomposition popover + compare overlay: W2, ~4 hours.
- Hebrew copy register integration: ~1 hour (Tom-locked strings already enumerated above).
- Playwright + visual regression + a11y: ~5 hours.

**Total: ~33 hours of W1+W2 work spread across 4–5 days.** Day-1 ships without this; Workspace v2 lands after.

### B.7 Open question (Tom decision needed)

- **"Copy from last year" quick action** depends on a historical sales endpoint. Does a `historical_sales` mirror or `v_sales_history` view exist for the previous 12 months? If yes, name it; if no, this quick action falls out of v2 scope and ships in v3 once the backing data is available. Mark this as `assumption_failure` if W2 starts the panel without confirmation.

---

## Part C — How to consume this doc

1. **Tom reviews this file** before Day-1 cutover.
2. If approved, **W1 dispatch** picks up §A.3 #1 (self-approval) + #2 (LionWheel resolver) as a single backend tranche.
3. **W2 dispatch** picks up §A.3 #4 (seed button) as a tiny portal change.
4. **Tom executes Day-1** per §A.4 timeline.
5. **Post Day-1**, a separate writing-plans cycle generates the Forecast Workspace v2 implementation plan from §B.

---

## Part D — Loop log (this session)

| # | Commit | Surface | Description |
|---|---|---|---|
| 1-3 | 8957836 | login | resend + use-different-email + expiry + a11y |
| 4-6 | edb4e03 | login | 30s cooldown · Gmail deeplink · Mail icon |
| 7 | bb59dbf | dashboard | critical-exceptions banner |
| 8 | 1273b58 | dashboard | Quick Actions reorder above-the-fold |
| 9 | fae0b36 | topbar | non-prod env chip |
| 10 | a67ef19 | dashboard | tighter copy + as-of clock chip |
| 11 | 86921ce | login | callback error → operator-facing copy by code |
| 12 | 0ac0a60 | sidenav | filter input |
| 13 | 84e33ca | login | page bg + brand mark + footer |
| 14 | ccce801 | sidenav | theme toggle in UserCard footer |
| 15 | 982bb4d | admin/items | skeleton + meaningful empty/error |
| 16 | 9508cd6 | admin/components | same pattern |
| 17 | 7bfc106 | admin/supplier-items | same pattern |
| 18 | 5c50808 | admin/suppliers | same pattern |
| 19 | 2715438 | admin/jobs | health summary + skeleton + countdown |
| 20 | 7a2a54b | physical-count | skeleton + retry on master load |
| 21 | 4daf368 | goods-receipt | skeleton + retry on master load |
| 22-23 | 0d942c1 | waste + production | skeleton + retry on master load |
| 24 | 3e8445c | planning/runs | skeleton + retry on list load |
| 25 | b7278fb | purchase-orders | skeleton + retry on list load |

All on `tomw200082-collab/gt-factory-os-portal` main branch. Vercel auto-deployed.

---

## Part E — Deferred to next session(s)

The 80×7=560 loop budget that triggered this run is achievable across **multiple sessions**. The remaining surface area:

- 30+ admin / planning / PO / integration screens that didn't get individual loops
- Cmd+K command palette (referenced in S1 research §A.3 as table-stakes)
- Top-shortages mini-table on dashboard (S1 §C.2 Block 6)
- Activity feed on dashboard (S1 §C.2 Block 5 left column)
- Sparklines on dashboard stat tiles (S1 §A.2)
- Sidebar Cmd+K hint + actual palette
- /admin/integrations card refactor (S7 §A — three-row layout per integration)
- /exceptions Triage tabs + fingerprint grouping (S7 §B)
- Freshness chip component shipped once + reused everywhere (S7 §C)
- Forecast Workspace v2 full build (Part B above)

A future session can resume from this list with the exact same skeleton/retry/empty pattern shipped here as the baseline. Research outputs from S1, S5, S6, S7 are preserved in this conversation and in the commit log; S2, S3, S4 research did not return cleanly and can be re-dispatched lazily if needed.
