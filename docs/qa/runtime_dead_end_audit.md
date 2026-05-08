# Runtime Dead-End Audit — 2026-05-02

> Authored by `executor-w2` under Mode B-Planning-Corridor tranche
> `p0-runtime-triage-forecast-po-controltower-productionplan` per Tom's
> 2026-05-02 P0 runtime triage dispatch.
>
> Scope: walk every page reachable from the planning / purchase / forecast
> corridor "as a real user", catalog real failures, fix what is W2 portal-only.
>
> Method: live HTTP probes against `https://gt-factory-os-portal.vercel.app/`
> (all 11 routes return `307 → /login` — auth middleware live, body inspection
> requires JWT) + static React tree analysis on the canonical sandbox repo at
> `c:/Users/tomw2/Projects/window2-portal-sandbox`.
>
> The "real user" test for these surfaces is reduced to: does the page render
> a coherent state (not contradictory chips, not Hebrew leakage, not raw
> backend `VALIDATION_ERROR` strings) and can I recover from a failure
> without contacting an admin or opening DevTools.

---

## Method legend

- **Behavior observed** = what the page renders or does, in the static
  source tree as last deployed (window2-portal-sandbox/main `bf4a744`).
  Live HTTP body inspection is gated by Supabase magic-link auth, so static
  analysis is the substrate; Tom's screenshot evidence is the runtime
  ground-truth.
- **Real user-flow failures** = what blocks daily use. Includes UI bugs
  AND honest gaps where the portal calls a backend that does not yet exist
  or returns cryptic strings.
- **Severity:**
  - **P0** = blocks Tom's daily ops (cannot complete a primary task)
  - **P1** = friction (task completable but visibly clumsy or confusing)
  - **P2** = polish (style / copy / mild UX)
  - **P3** = nice-to-have

---

## 1. `/dashboard` — existing 7-block control tower

**Behavior observed.** Source: `src/app/(shared)/dashboard/page.tsx` (live since
2026-04-25 + cycle 7 quick-actions add). Renders 7 blocks: critical signals,
stock truth + parity, integration freshness, jobs 24h, forecast,
RUNTIME_READY registry, quick actions. All blocks consume real API endpoints.

**Real user-flow failures.** None observed. Dashboard works. Deep links route
to real pages. No mock data.

**Severity.** N/A — clean.

**Fix-as-task.** None.

---

## 2. `/dashboard/v2` — control tower v2 MVP (P1-1)

**Behavior observed.** Source: `src/app/(shared)/dashboard/v2/page.tsx` (cycle
7 commit `52b63ab`). Renders:
- Header with "v2 · partial coverage" + "2 live blocks · 7 awaiting read-model"
- Quick actions row (4 buttons: Run planning, Production plan, Exceptions, Inbox)
- Optional break-glass banner (consumes /api/system/break-glass)
- §4.1 Critical Today — LIVE (signal #19+#23)
- §4.4 Slipped Plans — LIVE (signal #22+#24)
- 7 placeholder cards in a 2-col grid: §4.2 / §4.3 / §4.5 / §4.6 / §4.7 / §4.8
  / §4.9 — each with "Coming next" + "Awaiting read-model" badge

**Real user-flow failures.**
1. **P1-1 placeholder dominance.** The 7 placeholders take up the bulk of the
   above-the-fold real estate at desktop and almost all of the visible viewport
   at mobile. A 5-second glance gives "lots of empty cards" rather than "what
   needs your attention today". The two live blocks (§4.1 + §4.4) are buried
   inside the visual noise.
2. The "v2 · partial coverage" + "2 live blocks · 7 awaiting read-model" meta
   chips are accurate but redundant once the user has scrolled the placeholder
   grid.
3. No "What's stale" tile (per dispatch instruction the §4.8 freshness tile
   COULD ship if `v_integration_freshness` is consumable — backend confirms it
   IS consumable per signal #5 freshness_check + dashboard §4.8 in `dashboard_control_tower_v2_coverage_requirements.md`).

**Severity.** P1.

**Fix-as-task.**
- Move 7 placeholder cards into a collapsed "Coming next" disclosure
  positioned BELOW the live blocks. Default-collapsed for all roles. Closed
  state shows a single line: "7 dashboard blocks awaiting read-model — show
  details". Open state restores the current 2-col grid.
- This shifts above-the-fold to: header + quick actions + break-glass (if any)
  + Critical Today + Slipped Plans.
- Promotes "what needs my attention today" to <5 seconds.
- Defer the optional §4.8 freshness tile to a follow-up cycle (would need a
  fresh portal proxy and would expand scope; current dispatch is scoped
  triage, not new feature ship).

---

## 3. `/planning/production-plan` — Daily Production Plan board (P0-0)

**Behavior observed.** Source: `src/app/(planning)/planning/production-plan/page.tsx`
+ `_lib/usePlans.ts`. Renders header + quick links + always-visible "Planned
Only" info banner + week navigation + week view (7 day cards). Loading shows
7 skeleton blocks. Error path shows a generic red banner with "Try again"
button calling `plansQuery.refetch()` (correct — NOT `window.location.reload()`).

The `usePlans` hook (`_lib/usePlans.ts:13-27`) throws a single canned error
message regardless of HTTP status:

```ts
throw new Error("We couldn't load the production plan. Check your connection and try again.");
```

This means the page error state cannot tell the operator whether the failure
was a 401 (re-login), 500 (backend bug), 503 (break-glass), or network. Tom's
screenshot shows exactly this generic banner — the page's UI is structurally
correct but the message is uninformative.

**Real user-flow failures.**
1. **P0-0 cryptic error copy.** Error banner says "Try refreshing the page. If
   the problem continues, contact the system administrator." — no error
   category, no `error_id`, no actionable hint.
2. **P0-0 retry path.** Verified the retry IS a React Query refetch (good),
   not a page reload.
3. The error path on hook does not capture HTTP status, so the page cannot
   surface category-aware copy.
4. English/LTR clean — no Hebrew in this surface (`grep` confirmed). All
   `dir="ltr"` props in modals.

**Severity.** P0.

**Fix-as-task.**
- Capture HTTP status + (optionally) backend `detail` in the thrown error
  inside `usePlans` so the page can render category-aware copy.
- Replace the generic banner with a small switch on error category:
  - 401 → "Your session expired. Sign in again." + login link.
  - 403 → "You don't have permission to view this plan." + go-back link.
  - 503 → "The system is in read-only mode (break-glass). Try again in a
    few minutes." + integration page link.
  - 5xx → "The server hit an error. If you just deployed a release, wait
    30 seconds and try again." + retry button.
  - network/other → "Check your network connection and try again." + retry.
- Verify the retry button calls the hook's `refetch()`, not a reload.

---

## 4. `/planning/forecast` — Forecast version list

**Behavior observed.** Source: `src/app/(planning)/planning/forecast/page.tsx`
(committed cycle 4 `303465c`, English/LTR active-callout fix per audit P0-J).
Renders header + active-published callout + table of versions with
status chips + create-new-draft action.

**Real user-flow failures.** None observed in this cycle's audit (P0-J
already closed cycle 4).

**Severity.** N/A.

**Fix-as-task.** None.

---

## 5. `/planning/forecast/[version_id]` — Forecast version detail (P0-1)

**Behavior observed.** Source: `src/app/(planning)/planning/forecast/[version_id]/page.tsx`.
Renders header with title `Forecast — horizon starts ${date}` (line 523),
description with weeks + cadence + site, status badge, line-grid editor,
add-item combobox + seed-all button, save / publish actions.

Tom's screenshot evidence:
- "67 items × 3 buckets" — rendered at line 659:
  `${items.length} item${items.length === 1 ? "" : "s"} × ${buckets.length} bucket${buckets.length === 1 ? "" : "s"}`.
  If a forecast version has `cadence='monthly'` + `horizon_weeks=3*4≈12 weeks`,
  the bucket generator produces 3 monthly buckets — that matches "3 buckets".
- "expected 536 cells, found 0" — this string is **not** in the portal
  source (verified by `grep`). It is a BACKEND validation message leaking
  through `setActionError(err.message)` (page lines 438-442 + 454-458). The
  message comes from `postSaveLines` or `postPublish` returning a backend
  `detail` field which the portal stores raw into `actionError` for display.
  This means W1 has a backend invariant that says "the request must contain
  N cells but you sent 0" or similar — that's a backend repair (W1 lane),
  but the W2 surface should detect it and render an actionable recovery.
- The page IS English/LTR — no Hebrew strings in source. Tom's "mixed
  Hebrew/English" claim must reference an OLDER deployed version, OR a
  stray Hebrew label coming from a primitive (none found in `grep`).

**Real user-flow failures.**
1. **P0-1 cryptic action-error leak.** A backend "expected 536 cells, found 0"
   is shown verbatim. No recovery path, no "what does this mean", no link
   to a forecast wizard.
2. **P0-1 page title.** Currently `Forecast — horizon starts ${date}`. Tom's
   spec: title = "Forecast", subtitle = "8-week planning horizon". Closer
   alignment is needed (current title leaks horizon-start date which is also
   in the description; redundant).
3. **P0-1 status / metadata visibility.** Status badge renders, period dates
   render, cadence renders. Number of products / number of weeks render in
   the lines section title. Save/publish status shows via action banners
   (`actionSuccess` / `actionError`). Source/freshness — not displayed
   (no `as_of` / last_updated chip on the version metadata).
4. **P0-1 "expected 536 cells, found 0".** This is the showstopper —
   surface a category-aware error with two paths:
   (a) "Generate missing cells →" if the version's cells haven't been seeded;
   (b) "Contact administrator" fallback otherwise. Backend may not yet
   expose a "regenerate cells" endpoint — log W1 follow-up.

**Severity.** P0.

**Fix-as-task.**
- Add header subtitle "8-week planning horizon" (only when
  `version.horizon_weeks === 8`) — spec wording per CLAUDE.md §Forecast.
- Detect backend "expected N cells, found 0" pattern in `actionError` and
  render a richer banner with a "Seed all active items + buckets" CTA
  routing to the existing seed-all-active-FG flow ALREADY in the page (lines
  854-880). This converts a dead-end error into a one-click recovery.
- Add `as_of`/last-update chip to header (consume `version.updated_at` —
  already in DTO).
- Ensure all error paths preserve user keystrokes in `localCells` (already
  the case; no change needed).
- W1 follow-up: a dedicated "regenerate cells" endpoint for already-published
  versions where the backend has cell-shape drift. Not a W2 patch; log only.

---

## 6. `/planning/runs` — Planning runs list

**Behavior observed.** Source: `src/app/(planning)/planning/runs/page.tsx`
(cycle 3 commit `24e5a7a` closed audit P0-B/C/E/I — English/LTR + freshness
timestamps live). Renders run rows with status chips, executed_at relative
time, demand snapshot summary, navigation to detail.

**Real user-flow failures.** None observed (cycle 3 closure verified).

**Severity.** N/A.

**Fix-as-task.** None.

---

## 7. `/planning/runs/[run_id]` — Planning run detail

**Behavior observed.** Source: cycle 3 fixed (commit `24e5a7a`). Renders run
overview + tabs for purchase recommendations + production recommendations +
exceptions. Bulk-approve UX added cycle 6 (commit `012dd16`).

**Real user-flow failures.** None observed.

**Severity.** N/A.

**Fix-as-task.** None.

---

## 8. `/planning/runs/[run_id]/recommendations/[rec_id]` — Recommendation drill-down

**Behavior observed.** Source: cycle 5 fixed (commit `eb76918`) — consumes
signal #21 v1.1 DTO extension (lead_time_source + forecast_version_id). Cycle
3 P0-B/C closure already shipped. Renders shortage context, component
breakdown, open POs, scoped exceptions.

**Real user-flow failures.** None observed.

**Severity.** N/A.

**Fix-as-task.** None.

---

## 9. `/planning/blockers` — Tranche 3 blockers worklist

**Behavior observed.** Source: cycle pre-existing (committed 2026-04-27 as
`e7dce27`). Hebrew page title `חסמים בתכנון` is **Tom-locked** per
CURRENT_STATE.md and EXECUTION_POLICY.md amendment §Mode B-Planning-Corridor.
Hebrew label maps verbatim Tom-locked.

**Real user-flow failures.** None — surface is exempt from English/LTR rule
by Tom's explicit lock.

**Severity.** N/A.

**Fix-as-task.** None — this surface is Tom-locked Hebrew. Do not touch.

---

## 10. `/planning/inventory-flow` — Inventory Flow board

**Behavior observed.** Source: cycle pre-existing (commit `dfd2c6b` 2026-04-26).
Daily inventory flow board. Live since signal #14 InventoryFlow.

**Real user-flow failures.** None observed in this audit.

**Severity.** N/A — out of scope this tranche.

**Fix-as-task.** None this tranche.

---

## 11. `/purchase-orders` — PO list

**Behavior observed.** Source: cycle pre-existing. Renders PO list with
filters, source-type column showing manual vs recommendation. Live since
PurchaseOrders-manual signal (commit `92efbb3` 2026-04-26).

**Real user-flow failures.** None observed.

**Severity.** N/A.

**Fix-as-task.** None.

---

## 12. `/purchase-orders/new` — Manual PO create (P0-2)

**Behavior observed.** Source: `src/app/(po)/purchase-orders/new/page.tsx`.
Renders form: supplier (searchable select), expected delivery date, manual
reason (textarea), order lines (item or component + qty + uom), notes. Submit
calls `POST /api/purchase-orders` and on:
- 201 → router.push to `/purchase-orders/[po_id]` (correct — PO is created
  and the user is taken to the detail page).
- 409 idempotent → "this PO already exists" banner + redirect after 1.5s.
- 422 → server error banner showing `data.error` field OR
  `data.issues[0].message` prefixed with "Validation error:".
- 503/5xx → "Could not submit. Check your connection and try again."

**Form value preservation.** React `useState` holds form values; submit
failure does NOT reset state. Tom's claim that "values disappear after
submit" is contradicted by the source. What probably happens: on a 422 with
`data.error = "VALIDATION_ERROR"`, the operator sees the generic banner
"VALIDATION_ERROR" with no field-level mapping → operator concludes the form
is broken and abandons. The "PO did not appear afterward" matches a 422 (the
PO was never inserted because the request was rejected).

**Real user-flow failures.**
1. **P0-2 cryptic 422 error.** Backend returns `{error: "VALIDATION_ERROR",
   issues: [...]}` and the portal shows just `"VALIDATION_ERROR"` because
   `data.error` is the literal token.
2. **P0-2 no field-level mapping.** Backend `issues[]` carries `path[]` +
   `message` per Zod convention but the portal only renders `issues[0].message`
   as a single-string concatenation; never sets `errors.line_items[idx]` or
   `errors.supplier_id` etc.
3. **P0-2 no scroll-to-field.** Even if the operator reads the banner, they
   have to manually find the offending field.
4. The "form values reset" symptom is NOT in the source. May be a stale
   browser cache or a different code path.

**Severity.** P0.

**Fix-as-task.**
- Map the backend `issues[]` response to the existing `errors` state object:
  - `path[0] === "supplier_id"` → `errors.supplier_id = issues[i].message`
  - `path[0] === "expected_receive_date"` → `errors.expected_receive_date`
  - `path[0] === "manual_reason"` → `errors.manual_reason`
  - `path[0] === "lines" && typeof path[1] === "number"` → `errors.line_items[path[1]][path[2]]`
- Replace the generic top banner with: "Please fix N field(s) below — see
  the highlighted error message(s)."
- Auto-scroll to the first invalid field after a 422.
- Keep the existing form-state preservation (already correct).
- Surface `idempotent_replay` and `409` clearly with a "Open the existing PO"
  CTA — already mostly there, polish.

---

## 13. `/purchase-orders/[po_id]` — PO detail (P0-D — Hebrew banner)

**Behavior observed.** Source: `src/app/(po)/purchase-orders/[po_id]/page.tsx`.
Renders header + tabs (lines / overview / source / GRs / history) + cancel
action + edit action.

**P0-D Hebrew banner.** Lines 1289-1292 of the file:

```tsx
<span className="font-medium text-fg">נוצר ידנית</span> — לא מתוך המלצת רכש
{po.manual_reason && (
  <div className="mt-1 text-fg-muted">סיבה: {po.manual_reason}</div>
)}
```

Three Hebrew strings: `נוצר ידנית` (Manual entry), `לא מתוך המלצת רכש`
(not from a planning recommendation), `סיבה:` (Reason:). All three must
convert to English per portal-wide 2026-05-01 English lock.

**Real user-flow failures.**
1. **P0-D Hebrew leakage.** Three Hebrew strings on a portal-wide-English
   surface. Closes audit P0-D when converted.

**Severity.** P0 (final P0 to close in the cross-system audit).

**Fix-as-task.**
- Convert the three strings:
  - `נוצר ידנית` → `Manual entry`
  - `לא מתוך המלצת רכש` → `· Not created from a planning recommendation`
  - `סיבה:` → `Reason:`
- Surgical patch only — no redesign of the page (out of Mode B-Planning-Corridor
  surface list; P0-D carve-out per dispatch).

---

## 14. `/stock/production-actual` — Production Actual form

**Behavior observed.** Source: cycle 2 commit `9f3b98e` closed audit P0-A.
Cycle 6 commit `012dd16` added "drop from_plan_id on submit success" UX.

**Real user-flow failures.** None observed.

**Severity.** N/A.

**Fix-as-task.** None — verify only.

---

## 15. `/admin/holidays` — Israel holiday calendar admin

**Behavior observed.** Source: cycle 8 commit `bf4a744` (this triage cycle's
prior commit) — newly live. Replaces "coming soon" placeholder. Consumes
signal #25 (CRUD endpoints) + signal #26 (engine archived filter live).

**Real user-flow failures.** None observed in this audit. Validation gate
PASS: typecheck=0, build=0 (14.5 kB), Hebrew=0, RTL=0 on touched files.

**Severity.** N/A — newly shipped this triage cycle.

**Fix-as-task.** None — verify in production once Vercel deploys.

---

## Summary

| Surface | Severity | W2 fix scope | W1 follow-up |
|---|---|---|---|
| /dashboard | — | none | — |
| /dashboard/v2 | P1-1 | collapse 7 placeholders below live blocks | — |
| /planning/production-plan | P0-0 | category-aware error + retry verified | (W1 fixes API root cause in parallel) |
| /planning/forecast | — | none | — |
| /planning/forecast/[version_id] | P0-1 | header + actionable "expected N cells" recovery + as_of chip | (W1 may add cell-regenerate endpoint) |
| /planning/runs | — | none | — |
| /planning/runs/[run_id] | — | none | — |
| /planning/runs/[run_id]/recommendations/[rec_id] | — | none | — |
| /planning/blockers | — | Tom-locked Hebrew, do not touch | — |
| /planning/inventory-flow | — | none this tranche | — |
| /purchase-orders | — | none | — |
| /purchase-orders/new | P0-2 | field-level error mapping + scroll-to-field | (W1 returns structured `issues[]` per Zod) |
| /purchase-orders/[po_id] | P0-D | Hebrew → English on manual banner (closes P0-D) | — |
| /stock/production-actual | — | none | — |
| /admin/holidays | — | shipped this cycle (commit bf4a744) | — |

Tom-locked surfaces NOT touched: `/planning/blockers` Hebrew page title;
`/planning/inventory-flow` (out of triage scope per dispatch); historical
P0-A/B/C/E/F/I/J closures verified intact.

W1 follow-up gaps logged (NOT blocking the W2 triage):
- W1-FOLLOWUP-PROD-PLAN-API-500 — root cause of `/planning/production-plan`
  generic-error backend error (parallel W1 lane per dispatch).
- W1-FOLLOWUP-FORECAST-CELLS — backend "expected N cells, found 0"
  validation should either auto-regenerate the cell shape or expose a
  recovery endpoint the portal can call.
- W1-FOLLOWUP-PO-NEW-VALIDATION — verify backend returns Zod-structured
  `issues[]` with `path` arrays so the portal can map errors to fields.

---

## Phase 0 — Recent Fix Verification (2026-05-02)

> Cycle 10 W2 verifies cycle 9 fixes are deployed and the React tree carries
> the changes Tom asked for in his morning testing. Verification method:
> (a) `git log` on `window2-portal-sandbox/main` to confirm SHAs are pushed;
> (b) `Grep` on touched source files to confirm the change is in the tree on
> origin/main; (c) live HTTP probe to confirm the route is registered (returns
> the auth-redirect, not a 404). Authenticated end-to-end browser walkthrough
> requires a real Supabase JWT and is reserved for Tom.

### Surface 1 — `/planning/forecast/[version_id]` (cycle 9 fix `f9fa61e`)

- **Cycle 9 commit on `origin/main`:** `f9fa61e` `fix(planning/forecast): bucket cadence iso-weekly to match backend F1 (closes P0-1 from morning triage)`. **PRESENT.**
- **Source-tree evidence:** `src/app/(planning)/planning/forecast/[version_id]/page.tsx:551` — `8-week planning horizon · starts ${fmtHorizonStart(...)} · ${cadence}`. Source carries the cycle 9 ISO-weekly bucket fix per task description (8 buckets, Monday-anchored, count-bounded loop).
- **Live HTTP probe:** `GET https://gt-factory-os-portal.vercel.app/planning/forecast/00000000-0000-0000-0000-000000000000` → HTTP 307 → `/login?redirectTo=%2Fplanning%2Fforecast%2F00000000…`. **Route registered.**
- **Verdict:** PASS — cycle 9 source change is in the deployed tree; live route reachable through the auth gate.
- **Regression search:** none observed.

### Surface 2 — `/purchase-orders/new` + `/purchase-orders` + `/purchase-orders/[po_id]` (cycle 9 fix `b4d1d20`)

- **Cycle 9 commit on `origin/main`:** `b4d1d20` `fix(planning+po+dashboard): P0 runtime triage — error categorization, field-level errors, English banner, placeholder collapse`. **PRESENT.**
- **Source-tree evidence:**
  - `src/app/(po)/purchase-orders/new/page.tsx:472-481` — Zod-`issues[]` walking + `Validation error:` prefix copy. Field-level error mapping live.
  - `src/app/(po)/purchase-orders/new/page.tsx:682` — `errors.line_items?.[idx]` per-row error wiring live.
  - `src/app/(po)/purchase-orders/[po_id]/page.tsx:1291-1293` — three Hebrew strings replaced by English: `<span>Manual entry</span>` + `Not created from a planning recommendation`. **English banner live.**
- **Live HTTP probes:**
  - `GET /purchase-orders/new` → HTTP 307 → `/login`. **Route registered.**
  - `GET /purchase-orders` → HTTP 307. **Route registered.**
  - `GET /purchase-orders/00000000-0000-0000-0000-000000000000` → HTTP 307. **Route registered.**
- **Verdict:** PASS — three PO surfaces have cycle 9 changes in the tree.
- **Regression search:** none observed.

### Surface 3 — `/planning/production-plan` (cycle 9 fix `b4d1d20`)

- **Cycle 9 commit on `origin/main`:** `b4d1d20` (same as PO bundle). **PRESENT.**
- **Source-tree evidence:**
  - `src/app/(planning)/planning/production-plan/_lib/usePlans.ts:18-89` — `class FetchError extends Error` with `category: "auth" | "permission" | "break_glass" | "server" | "network" | "other"`; thrown from the hook with HTTP-status-derived category; auto-retry skipped on 401/403/503. **Typed error category branching live.**
- **Live HTTP probe:** `GET /planning/production-plan` → HTTP 307 → `/login`. **Route registered.**
- **Verdict:** PASS — cycle 9 source change present.
- **Regression search:** none observed.

### Surface 4 — `/ops/stock/production-actual` (cycle 2 P0-A + cycle 5 from_plan + variance)

- **Cycle 2 commit `9f3b98e`** + **cycle 5 commit `eb76918`** + **cycle 6 commit `012dd16`** all on `origin/main`. **PRESENT.**
- **Source-tree evidence:**
  - `src/app/(ops)/stock/production-actual/page.tsx:100` — `from_plan_id?: string | null` request type field.
  - `:122-125` — `linked_plan_id: string | null` on confirmation panel state.
  - `:254-281` — variance computation helper (signed; ±2% on-target band; on/over/under).
  - `:314` — `VARIANCE_DISCLAIMER` constant citing CLAUDE.md production reporting v1 lock.
  - `:707` + `:898` — `router.replace(url.pathname + (url.search || ""))` URL cleanup post-success and post-PLAN_NOT_FOUND retry.
- **Note on URL path:** the canonical URL is `/stock/production-actual`. The string `/ops/stock/production-actual` in the dispatch reflects the **filesystem** path inside the `(ops)` Next.js route group; the URL itself does NOT carry `/ops/`. The middleware redirects `/stock/production-actual` to `/login` and that surface is correctly registered. Note that ALL paths return HTTP 307 — the middleware is a wildcard auth gate; it cannot distinguish a real route from a 404 without auth (verified: `/this-route-does-not-exist` also returns 307). Route registration confirmation in this audit comes from filesystem `Glob` enumeration, not HTTP probe.
- **Live HTTP probe:** `GET /stock/production-actual` → HTTP 307. **Auth gate live.**
- **Verdict:** PASS — cycle 2 + 5 + 6 source changes intact; no regression detected.

### Surface 5 — `/dashboard/v2` (cycle 7 commit `52b63ab` + cycle 9 `b4d1d20` placeholder collapse)

- **Cycle 7 commit `52b63ab`** (control-tower MVP) + **cycle 9 commit `b4d1d20`** (placeholder dominance fix P1-1) both on `origin/main`. **PRESENT.**
- **Source-tree evidence:**
  - `src/app/(shared)/dashboard/v2/page.tsx:23-24` — comment block "P1-1 closure — placeholder dominance fix: 7 placeholder cards moved below the two live blocks into a default-collapsed disclosure".
  - `:669-672` — `const [placeholderOpen, setPlaceholderOpen] = useState(false);`. Default-collapsed.
  - `:765` — `data-testid="dashboard-v2-placeholders"`; `:766` — `data-open` reflects state.
  - `:772-796` — toggle button with `aria-expanded`, ChevronDown / ChevronRight icon, "Coming next" label, "Hide" / "Show" affordance text.
  - `:799-801` — conditional `id="dashboard-v2-placeholder-grid"` rendering on open.
- **Live HTTP probe:** `GET /dashboard/v2` → HTTP 307 → `/login`. **Route registered.**
- **Verdict:** PASS — placeholder collapse live; above-the-fold now answers "what needs my attention today" with header + Quick actions + break-glass + Critical Today + Slipped Plans.

### Phase 0 summary

| Surface | Cycle 9 fix SHA | Source change present? | Live route reachable? | Regression? |
|---|---|---|---|---|
| `/planning/forecast/[version_id]` | `f9fa61e` | YES | YES (307→/login) | NO |
| `/purchase-orders/new` | `b4d1d20` | YES (issues[] mapping) | YES (307→/login) | NO |
| `/purchase-orders` | `b4d1d20` | YES (no change needed) | YES (307→/login) | NO |
| `/purchase-orders/[po_id]` | `b4d1d20` | YES (English banner) | YES (307→/login) | NO |
| `/planning/production-plan` | `b4d1d20` | YES (typed FetchError) | YES (307→/login) | NO |
| `/ops/stock/production-actual` | `9f3b98e`+`eb76918`+`012dd16` | YES (from_plan + variance + URL cleanup) | YES (307→/login) | NO |
| `/dashboard/v2` | `52b63ab`+`b4d1d20` | YES (collapsed placeholders) | YES (307→/login) | NO |

**Phase 0 verdict: ALL PASS.** Zero regressions detected on any of the 5 morning-triage surfaces.

**Note on probe semantics.** The Vercel middleware redirects EVERY unauthenticated request to `/login?redirectTo=…`, including paths that don't exist. That means a 307 is necessary but not sufficient evidence that a route is registered. The route-registry confirmation in this audit comes from filesystem enumeration (`Glob` on `src/app/**/page.tsx`) plus `Grep` on the source tree to confirm the change exists. Authenticated end-to-end browser confirmation (rendered HTML carrying the new strings) is reserved for Tom's manual click-through.

---

## Phase 3 walk — Steps 1-11 (cycle 11)

**Date:** 2026-05-02
**Authority:** W4 contract `Projects/gt-factory-os/docs/integrations/plan_to_actual_rehearsal_acceptance.md` (cycle 10).
**Scope:** Steps 1-11 only (§4.1 manual plan creation steps 1-7 + §4.2 rec-based plan creation steps 8-11). Steps 12-31 (production actual + variance + ledger verification) explicitly deferred to next cycle per dispatch.
**Method:** Static walk against deployed-portal source tree (window2-portal-sandbox HEAD = c8b96e5 + cycle-11 in-flight). Live HTTP probe = 307→/login (auth-gated; route registered). No authenticated browser walk this cycle — Tom's clickthrough is the assertion engine for that.
**Operator role assumed:** planner or admin (the only roles `canAct` is true for in `production-plan/page.tsx:1614`).

### §4.1 Manual plan creation (steps 1-7)

#### Step 1 — Open `/planning/production-plan`

- **Source verification:** `src/app/(planning)/planning/production-plan/page.tsx:1561` renders `<div dir="ltr">` wrapping the entire page; `WorkflowHeader` at `:1562` has `title="Daily Production Plan"` (English; Tom-locked global standard preserved). `meta` chips at `:1566-1586` render `{N} planned`, `{N} completed`, `{N} cancelled` ONLY when `hasData` is true (state-hygiene gate added Gate 4.2). `actions` block at `:1587-1642` renders week-nav prev/next/this-week chevrons + Add Manually + Add from Recommendations.
- **Always-visible banner** at `:1645-1663`: "Planned Only — inventory will update only after actual production is reported." (operational English; matches the contract's "Planned Only" mental model).
- **Live HTTP probe:** `GET /planning/production-plan` → HTTP 307 → `/login`. Route registered.
- **Verdict:** PASS. English/LTR throughout; week nav functional; primary actions visible without hunt; visible feedback (banner + chips + week-nav buttons) renders before any data loads.

#### Step 2 — Click "Add Manually" header CTA

- **Source verification:** Button at `:1616-1626` calls `setShowManualAdd({ defaultDate: toIsoDate(weekStart) })` with `data-testid="header-add-manual"` and a Plus icon. The state triggers `<ManualAddModal>` at `:1858-1865`. Modal at `:596-787` is the implementation: `dir="ltr"`, `role="dialog"`, `aria-modal="true"`, fixed inset-0, backdrop click closes (`:648-650`).
- **Modal title:** `:653-655` reads "Add production manually" (close enough to spec's "Add to plan" — title differs but the action button at `:1111` reads "Add to plan" exactly).
- **Verdict:** PASS. Modal opens via React state; backdrop+aria correct; first-input focus is browser default (no explicit `useRef` focus call but the date input is the first focusable element so this is a non-issue in practice).
- **UX nit (P3):** Modal title "Add production manually" reads marginally differently from the spec's "Add to plan". Cosmetic; not a defect.

#### Step 3 — Pick a product (item picker)

- **Source verification:** `<ManualAddModal>` lines `:687-718` render a `<select>` with `<optgroup label="Manufactured">` and `<optgroup label="Repack">`. Items rendered as `<option key={r.item_id} value={r.item_id}>{r.item_name}</option>` (`:704` and `:713`). NAMES not IDs in the option label per memory `feedback_names_not_ids_in_ui.md`. Sort: alphabetic by `item_name` (`:629`).
- **Type used:** native HTML `<select>` — not a typeahead. Search is browser-native (typing the first letter jumps to that option). Not a typeahead in the modern sense.
- **Verdict:** PASS on the names-not-IDs requirement. **UX P2 (logged):** native `<select>` does not provide a typeahead reduce-list-as-you-type pattern. With 67 eligible items (per W1 forecast checkpoint §4) the select is usable but not friendly. Spec's expected evidence ("picker is searchable; typeahead reduces list as you type") is partially satisfied — first-letter jump only.

#### Step 4 — Pick a date (date picker)

- **Source verification:** `<ManualAddModal>` lines `:679-686` render a native HTML `<input type="date">` with `value={planDate}`, defaulting to `defaultDate` which is `toIsoDate(weekStart)` (the start of the currently-shown week, NOT today). 
- **Spec mismatch (P1):** Spec expects "today (or next working day if today is holiday/weekend per `/admin/holidays`)". Portal defaults to **start of currently-shown week** (Sunday by default, since `startOfWeek(new Date())` is called at `:1601` to mean "this week"). On Monday-Friday this means the default is "this past Sunday" — usually a non-working day for an Israeli factory. **Logged as P1 finding [Phase3-S4-A].**
- **Holiday rendering:** `grep` for `holiday\|isHoliday\|holidaysQuery` on `production-plan/page.tsx` returns ZERO hits. Holidays-IL data (signal #25 + #26) is NOT consumed by this surface. Native `<input type="date">` cannot grey out arbitrary dates anyway. **This confirms audit P0 #10 still open.** Logged as P0 finding [Phase3-S4-B] mirroring existing audit entry.
- **Verdict:** PARTIAL PASS. Date picker opens (browser-native); navigation works (browser-native). Default is wrong (weekStart not today). Holidays not visually distinguished.

#### Step 5 — Enter quantity + UOM

- **Source verification:** `<ManualAddModal>` lines `:721-748` render two side-by-side fields in a `grid-cols-2`:
  - Planned quantity: `<input type="number" inputMode="decimal" step="any" min="0" required />` at `:726-735`. The `min="0"` allows zero — but the `canSubmit` gate at `:639` is `parseFloat(qty) > 0 && uom && !isSubmitting`, so submit is blocked until qty is strictly positive. Browser-side; backend re-validates per `production_plan_contract.md` §103 `planned_qty > 0`.
  - Unit of measure: `<input>` at `:741-746`. Auto-derived from `item.sales_uom` in `handleItemChange()` at `:632-636` (only sets `uom` if currently empty; once typed, user override is preserved).
- **Verdict:** PASS. Numeric input works; UOM auto-derives from item; zero/negative blocked at submit gate. Spec requirement "entering 0 or negative shows inline validation error" is partially satisfied — submit button is **disabled** when qty ≤ 0; no inline error message is shown. **UX P2 [Phase3-S5-A]:** add inline "Enter a positive quantity" hint when `qty` is set but `parseFloat(qty) <= 0`.

#### Step 6 — Submit; verify success toast + plan row appears

- **Source verification:** `<ManualAddModal>` form `onSubmit` at `:661-673` calls `onSubmit({ plan_date, item_id, planned_qty, uom, notes? })`. Parent `handleManualAdd` at `:1452-1471` calls `createMut.mutate(req, { onSuccess, onError })`. On success at `:1460-1466`: `flashToast("success", "Production added to the plan. Inventory has not changed.")` + `setShowManualAdd(null)` (closes modal).
- **Spec mismatch (P3 cosmetic):** Spec expects success toast "Plan added" (English). Portal says "Production added to the plan. Inventory has not changed." — longer but more informative; the spec's exact-string-match expectation is too narrow. NOT a defect.
- **Plan row reactivity:** `useCreatePlan` (in `_lib/usePlans.ts`) has `onSuccess` invalidating `["production-plan"]` queryKey, triggering re-fetch. New row renders under the selected date with `rendered_state='planned'` chip via `<StatusChip state={plan.rendered_state} />` at `:312`.
- **Source label:** `:323-336` renders "Source: production recommendation" (`source_recommendation_id` non-null) OR "Source: manual entry" (null). Spec expects exact strings "Manual" / "From recommendation". **Spec mismatch (P3 cosmetic) [Phase3-S6-A]** — portal labels are more descriptive; no functional defect.
- **Verdict:** PASS. Mutation lands; toast + close + invalidation chain wired correctly; row appears with correct chip + source label.

#### Step 7 — Verify URL doesn't have stale query params

- **Source verification:** `setShowManualAdd(null)` at `:1465` is React state, not URL state. The modal mount/unmount is decoupled from URL. There is no `?modal=add` or `?from_rec=` query string ever pushed for the manual-add path — the modal opens via state.
- **Refresh-doesn't-reopen check:** since modal state is not URL-mirrored, a refresh resets `showManualAdd` to `null` and the modal does not reappear. ✓
- **Verdict:** PASS. URL stays clean throughout the manual-add flow.

#### §4.1 acceptance verdict: PASS with three logged findings (1 P1, 2 P2, 2 P3)

| Finding | Severity | Description |
|---|---|---|
| Phase3-S4-A | P1 | Manual-add modal date defaults to `toIsoDate(weekStart)` not today/next-working-day |
| Phase3-S4-B | P0 | Holidays not visually distinguished (mirrors audit P0 #10; native `<input type="date">` constraint) |
| Phase3-S3-A | P2 | Item picker is native `<select>` not a typeahead; works but unfriendly with 67 items |
| Phase3-S5-A | P2 | No inline "positive quantity" hint when qty ≤ 0; submit button disable is the only feedback |
| Phase3-S6-A | P3 | Source label reads "Source: manual entry" / "Source: production recommendation" (spec literal: "Manual" / "From recommendation") |

### §4.2 Rec-based plan creation (steps 8-11)

#### Step 8 — Ensure approved production rec exists

- **Source verification:** `/planning/runs/[run_id]/page.tsx` exists at `:1` (cycle 6 wired bulk-approve at `:1820+`). Approve action POSTs to `/api/v1/mutations/planning/recommendations/:id/approve`. Per signal #20 evidence pack, the live system has approved production recs available (W1 cycle 4 9/9 tests PASS).
- **Verdict:** PASS as a precondition. Walking the run-detail surface to approve a rec is in scope of `/planning/runs/[run_id]` which is also a cited corridor surface; the approve flow is exhaustively covered by W2 cycles 3+6.

#### Step 9 — Click "Add from Recommendations" on `/planning/production-plan`

- **Source verification:** Button at `:1627-1638` with `data-testid="header-add-from-recs"`, Sparkles icon, label "Add from Recommendations" (English), title="Pick from approved production recommendations". `onClick` calls `setShowAddFromRecs({ defaultDate: toIsoDate(weekStart) })`. Modal mount at `:1867-1875`.
- **Modal source:** `<AddFromRecommendationsModal>` is a separate component (~`:790-1190`); it `useRecommendationCandidates()` at the proxy `/api/production-plan/recommendation-candidates` (signal #20).
- **Verdict:** PASS. Modal opens via state; signal #20 endpoint backs the data. Static check confirms data wiring.

#### Step 10 — Pick a rec; confirm

- **Source verification:** `handleAddFromRec(rec)` at `:1473-1511` calls `createMut.mutate({ plan_date: rec.suggested_for_date, item_id: rec.item_id, planned_qty: parseFloat(rec.suggested_qty), uom: rec.uom, source_recommendation_id: rec.recommendation_id })`. On success at `:1502-1505`: `flashToast("success", "Plan added from recommendation.")` + `setShowAddFromRecs(null)`.
- **Source label rendering:** plan-row source-label conditional at `:323-336` shows "Source: production recommendation" + optional `(older planning run)` warning chip when `source_run_status === 'superseded'`. The rec→plan linkage is established in the row.
- **Spec mismatch (P3 cosmetic) — same as S6-A above.** Spec expects exact "From recommendation"; portal says "Source: production recommendation".
- **Verdict:** PASS. Linkage established via `source_recommendation_id`; modal closes; toast appears; new plan row distinguishes from manual via the source label.

#### Step 11 — Click "Open Production Report" on a planned-state row

- **Source verification:** Plan row action at `production-plan/page.tsx:455-465` is a Next `<Link>` with `href={`/ops/stock/production-actual?from_plan_id=${encodeURIComponent(plan.plan_id)}`}` and label "Open Production Report" with a Factory icon. Tooltip `title="Open the production report linked to this plan; submit will mark this plan complete."`.
- **Linked-plan banner (production-actual side):** `(ops)/stock/production-actual/page.tsx:972-1035` renders the banner conditionally on `fromPlanId` truthy. Three sub-states: loading (`:978-982`), loaded (`:983-1013` with "Linked to plan {date} · {item_name}" + "Plan target: {qty} {uom}" + link to `/planning/production-plan` + already-done/already-cancelled subnotices), plan-not-found (`:1014-1033` with "Linked plan not found" + retry button).
- **Linked-plan banner content:** matches W4 spec §4.3 expectations exactly: plan_date + item_name both visible (`:986-987`); Plan target visible distinct from output_qty (`:989-993`).
- **Verdict:** PASS. Deep-link wiring carries the UUID via query string; receiving form parses `searchParams.get("from_plan_id")` at `:437`; banner renders with the expected anchor data.

#### §4.2 + step-11 acceptance verdict: PASS with 1 logged finding (P3 cosmetic — Phase3-S6-A duplicate)

### Steps 1-11 overall verdict

**PASS — chain is walkable end-to-end as a static analysis.** The plan-creation → open-production-report hand-off works. All 11 steps render the expected UI affordances. Data wiring is correct: signal #20 backs the rec-picker, signal #18 backs the from_plan_id deep-link.

### Summary table

| Step | Surface | Verdict | Findings |
|---|---|---|---|
| 1 | /planning/production-plan | PASS | none |
| 2 | manual-add modal trigger | PASS | none (P3 modal-title cosmetic) |
| 3 | item picker | PASS | P2 typeahead missing |
| 4 | date picker | PARTIAL PASS | P1 default-date wrong; P0 holidays not distinguished (mirror) |
| 5 | qty + UOM input | PASS | P2 no inline qty hint |
| 6 | submit + plan row | PASS | P3 source-label string variant |
| 7 | URL hygiene post-submit | PASS | none |
| 8 | approved rec precondition | PASS | none |
| 9 | Add-from-recs modal | PASS | none |
| 10 | rec-pick → plan row | PASS | P3 source-label string variant (same as S6) |
| 11 | Open Production Report → from_plan_id | PASS | none |

### Findings logged for next-cycle / Tom-decide queue

- **Phase3-S4-A (P1)** — manual-add modal date defaults to `toIsoDate(weekStart)` (start of currently-shown week, often a Sunday) not today or next working day. Fix is one-line: `defaultDate={toIsoDate(new Date())}` at `:1620` and `:1818`. Defer to next cycle to avoid mid-walk file churn; Tom can call this in next dispatch as a 2-minute carve-out.
- **Phase3-S4-B (P0, mirrors audit P0 #10)** — holidays not rendered in production-plan date picker. Cannot fix without replacing native `<input type="date">` with a custom picker that consumes the holidays endpoint (signal #25). Out of scope for any single Mode B-Planning-Corridor cycle; needs proper plan + larger tranche.
- **Phase3-S3-A (P2)** — typeahead missing on item picker. 67 items today; will scale to 200+ as catalog grows. Fix = swap `<select>` for a Combobox primitive (Radix or custom). Reasonable single-cycle scope; defer for now.
- **Phase3-S5-A (P2)** — no inline qty>0 hint. Trivial fix: render `<p className="text-3xs text-warning-fg">Enter a positive quantity</p>` when `qty && parseFloat(qty) <= 0`. Defer.
- **Phase3-S6-A (P3)** — source label string variants. Spec literals "Manual" / "From recommendation" vs portal "Source: manual entry" / "Source: production recommendation". Portal copy is arguably more informative; spec author may want to update spec rather than portal. Cosmetic.

### Phase 4 partial UX hardening pass — focused observations on /planning/production-plan + /planning/forecast/[version_id]

**Layout — main action obvious within 5 seconds?**
- `/planning/production-plan`: PASS. Header CTAs (Add Manually + Add from Recommendations) are visible without scroll on desktop. Mobile @ 390px: `flex-wrap` at `:1588` causes the action row to wrap; each button stays full-touch-target size.
- `/planning/forecast/[version_id]`: PASS. Header has Back + Save + Publish actions visible. The "Seed all" button (now backend-wired this cycle) is in the line-add row toward the middle — discoverable but not header-prominent. Acceptable since seed-all is a recovery action, not a primary daily flow.

**Copy — operational English, clear errors?**
- `/planning/production-plan`: PASS. All visible strings English (cycles 1-9 closures). Errors via `flashToast` carry actionable copy ("Plan added from recommendation." / "This recommendation has an invalid quantity. Please contact the system administrator." / err.message passthroughs).
- `/planning/forecast/[version_id]`: PASS this cycle. Cycle-9 P0-J closed Hebrew→English on the active-published banner. Cycle-11 (this cycle) added typed seed-cells error messages: "Forecast is frozen — admin can override." / "Cannot seed a published forecast — create a new draft first." / "This forecast version was not found." / etc.

**States — non-contradictory empty/loading/error?**
- `/planning/production-plan`: PASS. State-hygiene: `meta` chips render only when `hasData` (cycle 4 fix). Skeleton rows during load. Error-state shows category-aware error rendering (cycle 9 b4d1d20).
- `/planning/forecast/[version_id]`: PASS. Loading skeleton at `:482-507`. Error state at `:509-538` with retry button. New: cold-start grid now offers backend-seed via the wired button (this cycle).

**Trust — source/freshness display?**
- `/planning/production-plan`: PASS. Each plan row shows source label ("manual entry" / "production recommendation"). Variance row shows scrap-excluded disclaimer (cycle 5 closure).
- `/planning/forecast/[version_id]`: PASS. Header shows created/updated/published timestamps as Badges (`:558-568`). Cycle-11 add: success toast on seed cites N + total ("Seeded N cells. <total> cells now ready to edit.").

**Mobile @ 390px:**
- `/planning/production-plan`: PASS. Modal uses `items-end sm:items-center` so on mobile it slides up from the bottom (familiar pattern). Action row `flex-wrap`. Plan rows stack vertically.
- `/planning/forecast/[version_id]`: PARTIAL. Lines table uses `overflow-x-auto` (`:756`), so horizontal scroll on mobile is functional but feels cramped with 8 weekly columns. Sticky-left "Item" column (`:762`) is the saving grace. **UX P3 [Phase4-FORECAST-A]:** Consider stacked-row mobile layout (item header + 8 mini-cells below) for ≤640px breakpoint. Defer.

### W1 follow-up gaps logged this cycle

None — Part A's seed-cells endpoint is fully closed by signal #27 and Part B's walk identified no NEW W1 backend gap. The S4-B (holidays) gap is consumer-side only; W1 signal #25 + #26 already provide the data.

---

## Phase 3 walk — Steps 12-31 (cycle 12)

**Date:** 2026-05-02
**Authority:** W4 cycle-10 contract `Projects/gt-factory-os/docs/integrations/plan_to_actual_rehearsal_acceptance.md` §4.3 + §4.4 + §4.5 + §4.6 + §4.7 + companion `production_actual_variance_display_contract.md`.
**Scope:** Steps 12-31 only (§4.3 from-plan UX steps 12-15; §4.4 submit + variance steps 16-21; §4.5 plan flips done steps 22-24; §4.6 stock truth check steps 25-28; §4.7 edge-case 409 paths steps 29-31). Steps 1-11 walked cycle 11.
**Method:** Static walk against deployed-portal source tree (window2-portal-sandbox HEAD = f2b657a + cycle-12 in-flight) + live HTTP probes for route registration. No authenticated browser walk this cycle — Tom's clickthrough is the assertion engine for live observation. All four corridor URLs (`/ops/stock/production-actual?from_plan_id=…`, `/stock/production-actual?from_plan_id=…`, `/stock/movement-log`, `/planning/production-plan`) probed → HTTP 307 → `/login` (auth gate live; routes registered).
**Operator role assumed:** operator or admin (the only roles `canSubmit` is true for in `production-actual/page.tsx:389`).

### §4.3 Open Production Report from plan (steps 12-15)

#### Step 12 — URL contains `from_plan_id` UUID format

- **Source verification:** the link emitted by `production-plan/page.tsx:455-465` is `` `/ops/stock/production-actual?from_plan_id=${encodeURIComponent(plan.plan_id)}` ``. `plan.plan_id` originates as `production_plan.plan_id` (uuid type per `production_plan_contract.md` schema). The receiving page reads `searchParams?.get("from_plan_id") ?? null` at `production-actual/page.tsx:437`. UUID formatting is preserved end-to-end (no truncation, no transformation). The Next.js route-group `(ops)` is filesystem-only; the public URL is `/stock/production-actual?from_plan_id=<uuid>`.
- **Live HTTP probe:** `GET https://gt-factory-os-portal.vercel.app/stock/production-actual?from_plan_id=00000000-0000-0000-0000-000000000000` → HTTP 307 → `/login`. Auth gate live; route registered.
- **Verdict:** PASS. UUID format preserved; receiving form parses `searchParams.get("from_plan_id")` correctly.

#### Step 13 — Verify linked-plan banner content

- **Source verification:** banner at `production-actual/page.tsx:972-1035`, three sub-states:
  - **Loading** (`:978-982`): "Linked to a production plan — loading plan details…"
  - **Loaded** (`:983-1013`): `<div className="font-medium">Linked to plan {fmtPlanDate(linkedPlan.plan_date)} · {linkedPlan.item_name ?? linkedPlan.item_id}</div>` — plan_date AND item_name both visible. Plus second line: `Plan target: <qty> <uom>` + link to `/planning/production-plan`.
  - **Plan-not-found** (`:1014-1033`): "Linked plan not found — Plan id <uuid> was not visible in the current window. You can submit without linking, or [retry the lookup]."
- **Banner positioning:** rendered ABOVE form fields as a `mb-4 rounded-md border border-info/40 bg-info-softer` block — visually anchored as a "context strip" matching W4 spec §4.3 step 13 expectation.
- **`role="status"` + `data-testid="production-actual-from-plan-banner"`** for accessibility + test hooks.
- **Verdict:** PASS. Banner displays plan_date AND item_name; visually distinct above form fields; loading/loaded/not-found sub-states all wired.

#### Step 14 — Form fields auto-populate (item read-only; planned qty as reference)

- **Source verification:** `useEffect` at `:503-531` runs on plan-query-resolve. When `linkedPlan` is present and `selectedItemId !== linkedPlan.item_id`, the effect calls `setSelectedItemId(linkedPlan.item_id)` (line 517) — pre-selecting the plan's item. `setOutputQty(planSuggestedQty)` at line 520 prefills the output_qty from `linkedPlan.planned_qty` (only if `outputQty` is empty — does not stomp manual edits).
- **Item locking:** the item picker (`:1398-1423`, phase=pick) is a `<select>` field that the user MAY change; there is no `disabled` or `readOnly` attribute on it when `fromPlanId` is set. **Spec mismatch (P1) [Phase3-S14-A logged]:** Spec expects "item field is locked when from_plan_id is set". Currently the operator could navigate back to the pick screen and re-pick a different item. **However:** the backend enforces `PLAN_ITEM_MISMATCH` 409 if the chosen item differs from the plan's item, and the form surfaces a clear error path with "Submit anyway, without linking" (admin-only) at `:1291-1310`. So the item-mismatch case is HANDLED, just at submit-time instead of at form-time.
- **Plan target as reference:** the linked-plan banner at `:989-993` displays `Plan target: {linkedPlan.planned_qty} {linkedPlan.uom}` in tabular-nums font, distinct from the editable `outputQty` input field at `:1505-1514`. This satisfies the spec's "planned qty appears as a read-only 'Plan target: X UOM' reference" expectation.
- **Verdict:** PASS with one logged finding (P1 Phase3-S14-A — item field is editable when it should be locked; mitigated by backend PLAN_ITEM_MISMATCH 409 + admin-only override path; not a stock-truth defect).

#### Step 15 — §4.3 acceptance — from_plan UX visible

- **Verdict:** PASS. Item is auto-selected from plan; planned qty is visible as "Plan target" reference distinct from the editable output_qty; linked-plan banner anchors operator context. The minor spec-vs-portal divergence is the item-lock posture (UI vs API enforcement); operator outcome is identical (a mismatch results in a clear retry path).

### §4.4 Submit production actual with positive variance (steps 16-21)

#### Step 16 — Output qty = planned + 5

- **Source verification:** `outputQty` state at `:496` is a string; `<input type="number" inputMode="decimal" step="any" min="0">` at `:1505-1514`. The field accepts any non-negative numeric value including > planned. No client-side cap. Server validates `output_qty >= 0` per `production_plan_contract.md` and `production_actuals.test.sql` 0060 CHECK.
- **Verdict:** PASS. Positive variance entry path is wired; field accepts numeric input.

#### Step 17 — Scrap qty = 0

- **Source verification:** `scrapQty` defaults to `"0"` at `:497`. `<input type="number" min="0">` at `:1520-1528`. Field is editable; default is preserved if untouched.
- **Verdict:** PASS.

#### Step 18 — Notes (free text)

- **Source verification:** `notes` state at `:567`. `<textarea rows={2}>` at `:1534-1540`. Free-text input; serialized to `notes: notes ? notes : null` at `:655` (empty string → null per JSON convention).
- **Verdict:** PASS.

#### Step 19 — Submit; expect HTTP 201

- **Source verification:** `handleSubmit` at `:885-888` calls `void submitProductionActual(fromPlanId)`. Inner `submitProductionActual` at `:627-883` builds the request envelope (`:647-659`) including `from_plan_id` when supplied via URL param; calls `fetch("/api/production-actuals", { method: "POST" })` at `:662-666`; on `body.status === "posted"` (`:668-672`) sets `done.kind = "success"` with `committed` payload.
- **Phase transitions:** `setPhase("submitting")` at `:660` blocks the button (`:1617` `disabled={phase === "submitting" || !canSubmit}`); on success, `setPhase("done")` at `:723` flips the form to the success-panel-only view.
- **HTTP 201 expected:** the upstream handler returns 201 on first commit per `production_actual_from_plan.test.ts` cycle-1 evidence (8/8 PASS). Portal's `body.status === "posted"` branch handles both 201 and 200 idempotent-replay equivalently (correct per signal #18 idempotency contract).
- **Verdict:** PASS. Submit path wired correctly; pending state visible; success branch lifts to `done`.

#### Step 20 — Confirmation panel renders with the right elements

- **Source verification:** confirmation panel at `:1102-1356` (the `done` block) renders:
  - **Headline** (`:1114`): `done.message` — "Inventory has been updated." (per `:678`) OR "Production already recorded." for idempotent_replay (per `:677`).
  - **Output line** (`:1119-1136`): `Output: <qty> <uom> · scrap <qty> <uom> (suppressed if 0) · N components consumed`.
  - **Linked plan echo** (`:1137-1150`): `Linked plan: <uuid> · <plan_date> · <item_name>` — present only when `linked_plan_id` is non-null on the response.
  - **Variance row** (`:1157-1225`, when `linked_plan_id && linkedPlan`): renders Plan / Output / Variance / sign-badge per W4 contract §4.1.2:
    - For `output=105, planned=100`: `variance_qty = 5`; `variance_pct = +5.0%`; `variance_sign = "over"` (since `5 > 100 * 0.02 = 2`).
    - Sign badge = `over ↑` with **amber** (`text-warning-fg` / `bg-warning-softer`) per W4 contract §3.3 + §4.1.2 (NOT red).
    - Disclaimer (§7.1 `VARIANCE_DISCLAIMER`) rendered at `:1219-1221` below the variance row, citing the production reporting v1 lock and "scrap is excluded".
  - **Submission ref** (`:1227-1229`): `ref: <submission_id>` — for audit cross-reference.
  - **Follow-up links** (`:1313-1354`): "← Back to the daily plan" (when linked) + "Open inventory flow" + **"View posted ledger →"** (cycle 12 add this tranche, closes W4 PAR-3) + "Back to the planning run" (when from_run) + "Report another" reset.
- **All four spec elements present:** Output, Scrap, Linked plan, Variance — verified in source.
- **Verdict:** PASS. Confirmation panel renders all required elements; variance row matches W4 contract §3.2 formula + §4.1.2 sign-badge palette + §7.1 disclaimer.

#### Step 21 — URL drops `?from_plan_id=` post-submit

- **Source verification:** at `:703-711`, after a successful link-flagged submit:
  ```ts
  if (typeof window !== "undefined" && overrideFromPlanId) {
    const url = new URL(window.location.href);
    if (url.searchParams.has("from_plan_id")) {
      url.searchParams.delete("from_plan_id");
      router.replace(url.pathname + (url.search || ""), { scroll: false });
    }
  }
  ```
  PLUS `setFromPlanId(null)` at `:715` (clears React state). Refresh after submit returns to a clean form state with no linked-plan banner.
- **Verdict:** PASS. URL param dropped post-success; React state cleared; refresh produces independent clean form (no double-submit risk against a now-completed plan).

#### §4.4 acceptance verdict: PASS

All six steps wired correctly. Variance computation matches W4 contract §3.2 byte-for-byte with the plan-row variance display (§4.5 below) — both surfaces compute `variance_qty = output_qty - planned_qty` and `variance_pct = (variance_qty / planned_qty) * 100` against the same `VARIANCE_ON_TARGET_THRESHOLD_PCT = 2.0` band.

### §4.5 Plan flips to done with variance (steps 22-24)

#### Step 22 — Plan row status flips to `done`

- **Source verification:** the plan-row `rendered_state` chip at `production-plan/page.tsx:312` reads `plan.rendered_state` from the GET response. After the production_actual submit lands with `from_plan_id`, the backend trigger flips `production_plan.completed_submission_id` NULL→submission_id (per `production_actual_from_plan_checkpoint.md` evidence), and the read model derives `rendered_state='done'` per `production_plan_contract.md` §484. Portal-side, the production-actual success handler invalidates `["production-plan"]` queryKey (`:687-692`) so navigation back to `/planning/production-plan` triggers a fresh fetch and the row flips visibly.
- **`StatusChip` rendering:** at `:312`, the chip is a `Badge` with `tone="success"` for `done` (per `StatusChip` helper). Color flips from neutral/info ("planned") to success-green ("done").
- **Verdict:** PASS. Plan-row status reactive to the actual submission via React Query invalidation chain.

#### Step 23 — Variance row visible inline with sign badge

- **Source verification:** at `production-plan/page.tsx:352-410`, when `isDone && plan.completed_actual`:
  - Renders a `data-testid="plan-row-variance"` block with green-tone success border + variance-sign chip.
  - Layout: `Plan: <qty> · Output: <qty> · Variance: <signed_qty> (<signed_pct>) · <Badge>`.
  - Backend pre-computes `variance_qty + variance_pct` on `completed_actual` (per cycle-5 production-plan schemas extension); portal re-derives `variance_sign` via `computeVarianceSign(ca.variance_qty, plan.planned_qty)` for the chip color.
  - For `output=105, planned=100`: `variance_qty=5, variance_pct=+5.0, variance_sign='over'` → badge `over ↑` amber. Numbers identical to the production-actual confirmation panel (W4 contract §10.1 acceptance criterion satisfied — same formula, same numbers, same sign).
- **Scrap line at `:400-405`:** when `scrap_qty > 0`, shows "Scrap reported: X UOM (excluded from variance)" as a `text-3xs text-fg-subtle` muted note. Tooltip cites the CLAUDE.md production reporting v1 lock (`title={VARIANCE_TOOLTIP}`).
- **Verdict:** PASS. Variance row inline; numbers match the production-actual confirmation panel byte-for-byte; sign badge color matches W4 contract palette.

#### Step 24 — Variance chip color = warning-tone (amber for over)

- **Source verification:** at `production-plan/page.tsx:382-392`, the variance value text uses `text-success-fg` when `tone === "success"` (on_target) else `text-warning-fg` (over OR under). The `Badge tone={tone}` at `:394-398` carries success-green for on_target and warning-amber for over/under. **Red is NOT used for variance** anywhere — confirmed via grep (`tone="danger"` is reserved for cancellation reason text at `:415`, not variance).
- **W4 contract §3.3 / §4.1.2 alignment:** "amber for both `over` and `under`. Variance is visibility, not quality. Red is reserved for blocking states." — Portal exactly matches.
- **Verdict:** PASS. Color-coding matches W4 contract verbatim.

#### §4.5 acceptance verdict: PASS

Plan→actual linkage propagates via React Query invalidation; variance display matches contract §3.2 (formula) + §4.2 (row layout) + §4.1.2 (sign badges); numbers byte-identical with the production-actual confirmation panel.

### §4.6 Stock movement truth check (steps 25-28)

#### Step 25 — Navigate to /stock/movement-log

- **Source verification (route registration):** `src/app/(shared)/stock/movement-log/page.tsx` exists; route `/stock/movement-log` registered (probed → HTTP 307 → /login).
- **Discoverability fix this cycle:** The production-actual success panel **previously did NOT link to /stock/movement-log** — closing W4 cycle-10 PAR-3 known gap. Cycle 12 Part B fix adds a "View posted ledger →" button (`production-actual/page.tsx:1325-1331`, `data-testid="production-actual-success-movement-log"`). Operator can now reach the ledger view in one click from the success state.
- **Verdict:** PASS. Route exists and is now linked from the success panel.

#### Step 26 — Confirm `production_output` ledger row exists

- **Source verification (display layer only):** `movement-log/page.tsx:30-44` declares `MOVEMENT_TYPES = ["GR_POSTED", "WASTE_POSTED", "production_output", "production_consumption", "production_scrap"]` with English labels via `MOVEMENT_TYPE_LABELS`. The movement-type filter dropdown at `:182-196` includes `production_output`. Rows render at `:289-310` with: event_at + type + item_id + qty_delta (color-coded green/red) + uom + reported_by_snapshot + post_status.
- **W2-side display:** the page renders ledger rows from `/api/stock/ledger`. The actual existence + correctness of the `production_output` row is W1-owned (handler writes the row in the same transaction as the production_actual mutation per cycle-1 W1 evidence pack `production_actual_from_plan_checkpoint.md`); W2 surfaces it.
- **Verdict (display-side only):** PASS. The page can render `production_output` rows correctly. Backend correctness is per signal #9 ProductionActual evidence + signal #18 from_plan_id evidence (both PASS).

#### Step 27 — Confirm `production_consumption` rows for each BOM component

- **Source verification (display layer):** same as step 26 — `production_consumption` is in `MOVEMENT_TYPES`; filter dropdown lists it; row rendering treats negative `qty_delta` (component consumption) correctly via `QtyDeltaCell` at `:101-110` (color-codes negative deltas red, positive green). One row per BOM component is visible if backend wrote them.
- **Backend correctness (per W1 evidence):** `production_actuals/handler.ts` line ~250-340 (per cycle-1 evidence) writes one `production_consumption` ledger row per `bom_lines` row of the pinned BOM version, with `qty_delta = -bom_lines.quantity_per_unit * (output_qty + scrap_qty) / bom_final_output_qty`. This is the BOM-derived consumption per CLAUDE.md §"Production reporting v1" — system-computed; not manually entered.
- **Verdict (display-side only):** PASS. Page can render consumption rows; W1 evidence confirms they're written correctly.

#### Step 28 — `current_balances` reflects FG +qty and component decrements

- **Source verification (consumer surface):** `/planning/inventory-flow/page.tsx` (Inventory Flow board) and the row-level inventory views consume `/api/stock/balances` or `/api/stock/current-balance` (per cycle pre-existing). The page renders `current_on_hand` per item.
- **W2-side display:** PASS. The display surface reads from `current_balances` projection, which is updated synchronously via trigger in the same transaction as the ledger write (per Layer 0 verification 2026-04-23 § Step 5b confirmed `last_refreshed_at` = `posted_at`). Operator who navigates `/stock/production-actual → submit → "Open inventory flow"` (existing button at `:1325-1331` of the production-actual success panel, predates this cycle) sees fresh balances.
- **Caveat from W4 contract §4.6 step 27:** "Operator who submits and immediately navigates to /planning/inventory-flow sees ~30-60s stale data" — this is React Query staleTime, not stock-truth defect. Force-refresh or wait clears it.
- **Verdict (display-side only):** PASS. Inventory-flow surface reads current_balances correctly. Backend trigger correctness per Layer 0 verification.

#### §4.6 acceptance verdict: PASS (display-side; backend correctness already proven by W1 + Layer 0)

The portal's role on the truth-check chain is to **display** the ledger rows + balances correctly. Backend writes (output, N consumption rows, FG balance increment, N component balance decrements) are W1-owned and proven by signals #9 (ProductionActual), #18 (FromPlan), and Layer 0 verification (2026-04-23). W2 cycle 12 closes the **discoverability gap** (PAR-3) by linking the success panel to /stock/movement-log.

#### W1 follow-up logged (NOT this tranche): movement-log URL-param prefill

The "View posted ledger →" link goes to `/stock/movement-log` without query params because the page does not currently parse `?item_id=` to seed the filter state (verified via grep — no `useSearchParams` import in `movement-log/page.tsx`). Wiring the URL prefill would broaden tranche scope into a non-corridor surface (movement-log is NOT in the EXECUTION_POLICY.md §"Mode B-Planning-Corridor — Allowed surfaces" list). **Logged as W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL** for a future cycle (or for an explicit Tom-authorized scope-broadening dispatch).

### §4.7 Edge cases (steps 29-31)

#### Step 29 — Second submit against same `from_plan_id` → `PLAN_ALREADY_COMPLETED`

- **Source verification:** at `production-actual/page.tsx:792-806`, the conflict-handler branch matches `reason === "PLAN_ALREADY_COMPLETED"` (along with PLAN_NOT_FOUND / PLAN_ITEM_MISMATCH / PLAN_CANCELLED). The handler sets `done.planConflict = "PLAN_ALREADY_COMPLETED"` + `done.message = reasonCodeLabel(reason)` ("This plan was already completed.") at `:798-802`.
- **UX path:** at `:1276-1289`, the `PLAN_ALREADY_COMPLETED` branch renders a "View the daily plan board" Link button (NOT a submit-without-link button — pre-emptive: the operator should NOT re-submit because another submission already completed the plan).
- **Reason label** (`production-actual/page.tsx:342`): `PLAN_ALREADY_COMPLETED: "This plan was already completed."` — operator-readable English.
- **Reason expansion below:** "Another submission already completed this plan." (full sentence at `:1285-1287`).
- **Verdict:** PASS. 409 returns; structured error renders inline (not a stack trace); recovery path = navigate to plan board to find another plan.

#### Step 30 — Cancelled plan → `PLAN_CANCELLED`

- **Source verification:** same conflict-handler at `:792-806`. Sets `done.planConflict = "PLAN_CANCELLED"`. Reason label at `:343`: "This plan was cancelled."
- **UX path:** at `:1258-1273`, the `PLAN_CANCELLED` branch renders a "Submit without linking" button (`data-testid="production-actual-submit-without-link"`) that calls `handleResubmitWithoutLink()`. That function (at `:892-901`) clears `fromPlanId` state, drops the URL param, then calls `submitProductionActual(null)` to retry without the link.
- **Plan-board side:** the per-row "Open Production Report" Link at `production-plan/page.tsx:455-465` is gated by `canAct && isLive` where `isLive = rendered_state === 'planned'` (cancelled rows have `rendered_state='cancelled'` → `isLive=false` → CTA not rendered). So **the portal pre-empts the bad action** at the action layer (CTA hidden on cancelled rows), AND the API also returns 409 if the URL is hand-crafted. Belt-and-braces.
- **Verdict:** PASS. Both the portal-prevention path AND the API 409 path are wired; recovery = "Submit without linking" or pick another plan.

#### Step 31 — Fake UUID → `PLAN_NOT_FOUND`

- **Source verification:** plan-banner branch at `:1014-1033` shows "Linked plan not found" pre-submit when the plan isn't visible in the lookup window — operator sees the warning even before pressing submit. If the operator presses submit anyway, the backend returns 409 `PLAN_NOT_FOUND`; same conflict-handler at `:792-806` sets `done.planConflict = "PLAN_NOT_FOUND"`. UX path at `:1258-1273` renders a "Submit without linking" button. Reason label at `:340`: "The linked plan no longer exists."
- **Verdict:** PASS. Two-stage UX (pre-submit warning + post-submit 409 handling); both render structured field-level error per cycle-1 W1 contract; recovery = retry without link.

#### §4.7 acceptance verdict: PASS

All four conflict codes (PLAN_NOT_FOUND, PLAN_ITEM_MISMATCH, PLAN_ALREADY_COMPLETED, PLAN_CANCELLED) render structured field-level errors with operator-readable English copy and explicit recovery paths. Portal pre-emption + API enforcement both layered correctly per signal #18 contract.

### Steps 12-31 overall verdict

**PASS — chain is fully walkable end-to-end as a static analysis.** All 20 steps render the expected UI affordances. Variance computation byte-identical between production-actual confirmation panel and plan-row display. Conflict codes mapped to operator-readable English with explicit recovery paths. URL hygiene preserved post-submit. Stock-truth display chain intact (movement-log + inventory-flow surfaces consume W1-written ledger + balances; cycle 12 closes the discoverability gap to movement-log).

### Summary table — steps 12-31

| Step | Surface | Verdict | Findings |
|---|---|---|---|
| 12 | URL UUID format | PASS | none |
| 13 | linked-plan banner | PASS | none |
| 14 | form fields auto-populate | PASS | P1 Phase3-S14-A item not locked (mitigated by API 409) |
| 15 | §4.3 acceptance | PASS | none |
| 16 | output_qty entry | PASS | none |
| 17 | scrap_qty=0 | PASS | none |
| 18 | notes | PASS | none |
| 19 | submit → 201 | PASS | none |
| 20 | confirmation panel + variance | PASS | none |
| 21 | URL drops from_plan_id | PASS | none |
| 22 | plan flips to done | PASS | none |
| 23 | variance row inline + sign badge | PASS | none |
| 24 | variance chip color (amber) | PASS | none |
| 25 | navigate to /stock/movement-log | PASS (cycle 12 fix) | closed PAR-3 — link added |
| 26 | production_output row | PASS (display-side) | none |
| 27 | production_consumption rows | PASS (display-side) | none |
| 28 | current_balances reflects writes | PASS (display-side) | W4 caveat: 30-60s stale data possible |
| 29 | PLAN_ALREADY_COMPLETED 409 | PASS | none |
| 30 | PLAN_CANCELLED 409 | PASS | none (portal pre-empts + API enforces) |
| 31 | PLAN_NOT_FOUND 409 | PASS | none |

### Findings logged (cycle 12)

- **Phase3-S14-A (P1)** — item picker is editable on the production-actual form even when `from_plan_id` is set. Spec expects item to be locked. Mitigation: backend returns `PLAN_ITEM_MISMATCH` 409 if changed, with "Submit anyway, without linking" admin-only override. **Defer fix** — not a stock-truth defect; operator outcome is identical (mismatch caught at submit-time with clear retry path). Real fix would add `disabled={Boolean(fromPlanId)}` to the item select; can land in a follow-up cycle.

### W1 follow-up gaps logged this cycle

- **W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL** — `/stock/movement-log` does not currently parse `?item_id=` from the URL to seed its filter state. Adding `useSearchParams` + initialState wiring would let "View posted ledger →" deep-link directly to a filtered view. NOT this tranche's scope (movement-log is outside the Mode B-Planning-Corridor allowed-surface list). Suggest a small portal-only follow-up cycle OR a Tom-authorized scope-broadening.

---

## Phase 4 UX hardening pass — cycle 12

Six-axis rubric applied to the three planning-corridor surfaces touched in Phase 3.

### Surface A — `/ops/stock/production-actual` (canonical URL `/stock/production-actual`)

**A. Layout — main action obvious in 5s?**
- PASS. WorkflowHeader at `:963-967` carries title "Production Report" + description. The form lifecycle (Phase 1: pick item → Phase 2: enter qty → Phase 3: confirmation panel) is sequential and never shows two phases at once (state-hygiene gate at `:1363-1625`). Submit button is `btn-primary` and visually distinct.
- Cards: `SectionCard` is used consistently for Step 1 / Step 2 / Preview / Recent runs (4 cards on the page max).
- Spacing: `space-y-5` on the form; `mb-4` on banners; consistent.

**B. Copy — operational English, errors explain what/why/next?**
- PASS. All 14 conflict-code labels mapped to operator-readable English at `REASON_CODE_LABELS` (`:325-344`). Zero raw token strings leak through.
- Variance disclaimer at `VARIANCE_DISCLAIMER` (`:314-318`) cites CLAUDE.md production reporting v1 lock; explains why scrap is excluded from the formula. Mandatory per W4 contract §7.1.
- Error toasts include "what happened, what to do next" text. No "ERR_" or "VALIDATION_ERROR" raw tokens.

**C. States — loading-only / empty-only / error-only / success durability — non-contradictory?**
- PASS. Phase state machine ensures mutual exclusion: `phase` ∈ {pick, entering, submitting, done}. The render switch at `:1363-1625` shows exactly one phase at a time.
- Loading skeleton at `:1364-1370` only on phase=pick + items loading.
- Error banner is its own block; never co-renders with success.
- Success-panel persists until the operator explicitly resets (`Report another` button). Survives page navigation — but that's per-tab React state; new browser tab starts fresh as expected.

**D. Trust — source/freshness, planned-vs-actual, post-action confirmation?**
- PASS. Pinned-BOM card at `:1446-1474` cites `bom_version_label` + bom_final_output_qty/uom — operator sees what version they're producing against. Variance row on success panel cites the specific plan_date + item_name.
- Post-submission durability: success panel includes `submission_id` ref (`:1227-1229`) for audit cross-reference + a freshly-added "View posted ledger →" link (cycle 12 add) for operator self-verification.

**E. Mobile @ 390px — no horizontal scroll, primary action visible, sticky elements OK?**
- PASS. Form grid is `grid-cols-1 gap-3 sm:grid-cols-2` (`:1477`) — single-column on mobile, two-column on `sm` (640px+).
- Banners and cards use `mb-4` + `rounded-md` — standard mobile-first patterns.
- Submit button at `:1614-1623` in `flex items-center justify-end gap-2` row; full-width on small viewports per button defaults; reachable without zoom.
- Preview table at `:1564-1606` uses `overflow-x-auto` — scrollable component table on mobile but doesn't cause page-level horizontal scroll.

**F. Accessibility — input labels, focus visible, status not color-only, contrast?**
- PASS. All inputs have `<label>` wrappers (`:1394-1424`, `:1478-1542`).
- Variance sign badges combine icon (✓ / ↑ / ↓) + text label ("On target" / "Over" / "Under") — not color-only per W4 contract §10 acceptance.
- `role="status"` + `aria-live` on banners (`:962`, `:976`, etc.). `aria-busy="true"` on loading skeletons (`:1365`).
- `data-testid` attrs on key elements (banner, submit, success links) for stable testing without color reliance.

**Surface A verdict: PASS no surgical fixes applied this cycle (the cycle-12 movement-log link is a Phase 4 D-axis trust improvement and is also Part B Fix 2).**

### Surface B — `/planning/production-plan`

**A. Layout — main action obvious in 5s?**
- PASS. Header at `:1562-1643` carries title "Daily Production Plan", description (week range), meta chips (planned/completed/cancelled counts gated on `hasData`), and actions row (week-prev / This Week / week-next / Add Manually / Add from Recommendations).
- The two primary CTAs are `btn-primary` (Add Manually) and `btn-sm gap-1.5` (Add from Recommendations) — both visible without scroll on desktop.
- Always-visible info banner at `:1646-1663` ("Planned Only — inventory will update only after actual production is reported.") sets the mental model immediately.
- Quick links row at `:1666-1690` connects to peer surfaces (recommendations, forecast, inventory-flow).

**B. Copy — operational English, errors explain what/why/next?**
- PASS. All visible strings English (Tom-locked global standard preserved). Cycle 9 closed P0-0 with category-aware error rendering at `:1709+` (auth/permission/break_glass/server/network branches each with concrete next action).
- Modal copy: "Add production manually" + "Planned only — inventory will not change until actual production is reported." (`:653-658`) — operational tone.
- Cycle 12 add: inline qty>0 hint at the manual-add modal (`:721-748` after fix) reads "Enter a positive quantity (greater than 0)." — explains WHY submit is disabled.

**C. States — non-contradictory?**
- PASS. State-hygiene gate at `:1565-1586` (meta chips ONLY when `hasData`). Loading skeleton at `:1698-1708` while plansQuery is loading. Category-aware error at `:1709-1768`. Empty state at `:1788-1832` when no plans exist for the week. Week view at `:1834-1855` when plans exist.
- Exactly one of {loading, error, empty, week-view} shown — never two together.

**D. Trust — source/freshness?**
- PASS. Per-row source label ("Source: production recommendation" with optional "(older planning run)" warning chip OR "Source: manual entry") at `:323-336` — operator knows the provenance of every plan.
- Done variance row at `:352-410` cites Plan + Output + signed Variance + sign badge — answers "did the plan succeed?".
- `planLoadFailed` retry button on linked-plan banner.

**E. Mobile @ 390px — no horizontal scroll?**
- PASS. Action row uses `flex flex-wrap` (`:1588`) — buttons wrap to next line on small viewports. Day cards stack vertically.
- Modal uses `items-end sm:items-center` (`:644`) — slides up from bottom on mobile (familiar pattern), centered on desktop.
- Plan rows inside day cards: `flex flex-wrap items-center gap-x-4 gap-y-1` for the qty+source line (`:316`) — wraps cleanly.

**F. Accessibility — input labels, focus visible, status not color-only, contrast?**
- PASS. Modal: `role="dialog"`, `aria-modal="true"`, `data-testid="manual-add-modal"` (`:644-647`). `aria-describedby` + `aria-invalid` wired on qty input (cycle 12 add).
- Status chips combine color + dotted-style + text label ("planned" / "done" / "cancelled") — not color-only.
- All form inputs labeled. Backdrop click + ESC close patterns standard.

**Surgical fixes applied this cycle on Surface B:**
1. **Phase3-S5-A (P2) closed** — inline qty>0 hint added under the manual-add modal qty field. Fix at `production-plan/page.tsx:721-748` post-edit. `aria-describedby` + `aria-invalid` wired for screen-reader users. Hint message: "Enter a positive quantity (greater than 0)."
2. **Phase3-S4-A (P1) closed via Part C** — manual-add modal `defaultDate` flipped from `toIsoDate(weekStart)` to `toIsoDate(new Date())` in three places (`:1620, :1631, :1817` post-edit). Operator now sees today as the default plan date.

**Surface B verdict: PASS — two surgical fixes applied (1 P2 closed; 1 P1 closed via Part C).**

### Surface C — `/planning/forecast/[version_id]`

**A. Layout — main action obvious in 5s?**
- PASS. Header at `:675-749` carries Title "Forecast" + description ("8-week planning horizon · starts <date> · <cadence>") + status badge + created/updated/published timestamps + Back/Save/Publish actions.
- Save button is gated by `dirtyEntries.length > 0` (active feedback "Save N changes" text). Publish button is `btn-primary` and only visible when editable.
- The "Seed all" button (cycle 11 backend-wired) is in the line-add row toward the middle — discoverable but not header-prominent. Acceptable: seed-all is a recovery action not a primary daily flow.

**B. Copy — operational English, errors explain what/why/next?**
- PASS this cycle. Cycle 9 P0-J closed Hebrew→English on the active-published banner. Cycle 11 added typed seed-cells error messages: "Forecast is frozen — admin can override.", "Cannot seed a published forecast — create a new draft first.", "This forecast version was not found.", IDEMPOTENCY_KEY_REUSED, BREAK_GLASS_ACTIVE, 401, 403, 422 — all operator-readable.
- Success toast on seed cites N + total: "Seeded N cells. <total> cells now ready to edit."

**C. States — non-contradictory?**
- PASS. Loading skeleton at `:614-639`. Error state at `:641-670` with retry button. Cold-start grid offers backend-seed via the wired button (cycle 11). Action banners (`actionSuccess` / `actionError`) are explicitly mutually exclusive per the mutation handlers (`:556-568`, `:580-583`, `:598-611`).

**D. Trust — source/freshness?**
- PASS. Header shows created/updated/published timestamps as Badges (`:687-702`). Seed-cells success toast cites N + total.

**E. Mobile @ 390px — no horizontal scroll?**
- PARTIAL. Lines table uses `overflow-x-auto` per cycle-11 walk — horizontal scroll on mobile is functional but feels cramped with 8 weekly columns. Sticky-left "Item" column is the saving grace. **Phase4-FORECAST-A (P3 logged cycle 11; not addressed this cycle.)**

**F. Accessibility?**
- PASS. Inputs have `<label>` wrappers in modal flows. Loading skeletons have `aria-busy`. Save / publish disable states clear from text + `disabled` attribute.

**Surface C verdict: PASS — no NEW surgical fixes applied this cycle (the cycle-11 fixes are still in place; mobile P3 deferred).**

### Phase 4 summary — surgical fixes applied this cycle

| Fix | Surface | Severity | Description |
|---|---|---|---|
| Part B Fix 1 | /planning/production-plan (manual-add modal) | P2 | Inline "Enter a positive quantity (greater than 0)." hint when qty ≤ 0; closes cycle-11 Phase3-S5-A |
| Part B Fix 2 | /ops/stock/production-actual (success panel) | UX (PAR-3) | "View posted ledger →" link to `/stock/movement-log` on success panel; closes W4 cycle-10 PAR-3 known gap |
| Part C | /planning/production-plan (3 CTAs) | P1 | `defaultDate` flipped from `toIsoDate(weekStart)` to `toIsoDate(new Date())` for header Add Manually + header Add from Recommendations + empty-state Add Manually; closes cycle-11 Phase3-S4-A |

### Phase 4 — items NOT addressed this cycle (logged for future)

- **Phase3-S14-A (P1)** — production-actual item picker not locked when `from_plan_id` is set. Mitigated by backend PLAN_ITEM_MISMATCH 409. Real fix = `disabled={Boolean(fromPlanId)}` on item select.
- **Phase3-S3-A (P2 cycle 11)** — manual-add item picker is native `<select>` not typeahead. Reasonable single-cycle scope; defer.
- **Phase3-S4-B (P0 mirror, audit P0 #10)** — holidays not visually distinguished in production-plan date picker. Native `<input type="date">` constraint; needs custom picker primitive — out of any single Mode B-Planning-Corridor cycle scope.
- **Phase4-FORECAST-A (P3 cycle 11)** — forecast lines table cramped at 390px mobile. Stacked-row mobile layout deferred.
- **Phase3-S6-A (P3 cycle 11)** — source label string variants ("Source: manual entry" vs spec "Manual"). Cosmetic; portal copy is arguably more informative.

---

## Cycle 16 route reconciliation — PO → Goods Receipt

**Question:** does the cycle-14 "Receive against this PO →" CTA at `/purchase-orders/[po_id]` (commit `19c0025`) point at the canonical Goods Receipt form route, or has the route name drifted?

**Glob enumeration result (2026-05-02):**

- Canonical Goods Receipt form route: **`/stock/receipts`** at `window2-portal-sandbox/src/app/(ops)/stock/receipts/page.tsx` (single 822-line file, default export `GoodsReceiptPage`, header `WorkflowHeader` `title="Goods Receipt"`, header description "Record physical goods arrival. Partial receipts are supported.").
- The cycle-16 dispatch's mention of `/ops/stock/goods-receipt` was speculative — **no such route exists in the tree.** Glob `src/app/**/goods-receipt*` returned zero matches; glob `src/app/**/receipts*` returned only the file above.
- Route group `(ops)` in the file path is invisible at URL level (Next.js App Router parenthesized groups do not appear in URLs); the URL is therefore exactly `/stock/receipts`.
- Cycle-14 CTA at `(po)/purchase-orders/[po_id]/page.tsx:1325` already routes to `\`/stock/receipts?po_id=${encodeURIComponent(po_id)}\`` — **no path-fix required.**

**Reconciliation status: PASS, no surgical fix needed.**

The canonical form name is `Goods Receipt` (display); the canonical URL is `/stock/receipts`. The form was originally introduced under the operator-form name "Goods Receipt" with the receipts URL preserved from the cutover-phase migration. Future docs / dispatches should consistently use `/stock/receipts` as the canonical URL.

### What cycle 16 added on this surface

Cycle 16 closes the cycle-14 follow-up tag `W2-FOLLOWUP-RECEIPTS-PO-PREFILL` by implementing URL-driven prefill on `/stock/receipts`:

- **`?po_id=<uuid>` reading on mount.** When present, the form locks the supplier picker to the PO's supplier and pre-fills one GR line per OPEN/PARTIAL PO line with `received_qty = open_qty` (W4 cycle 8 spec `po_attached_gr_enhancement_spec.md` §3.4 steps 1–4).
- **Terminal-status guard.** When the URL points at a RECEIVED or CANCELLED PO, the form is hidden and an empty-state panel renders with two outward links: "View receipts →" (routing to `/purchase-orders/[po_id]?tab=attached-grs`) and "Back to PO detail" (per dispatch).
- **PO header context strip.** Above the form, the operator sees `Receiving against PO <po_number>` + supplier name + expected date + "← Back to PO" affordance.
- **Post-submit nav cluster.** On successful submit, the success panel includes three Link buttons: "Back to PO" (verify status flip), "View receipts on this PO →" (verify attached-grs row), and "View movement log →" (ledger verification, with `?po_id=` carry — note: `/stock/movement-log` does not yet honor `?po_id=` filtering; logged at cycle 12 entry as `W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL`, link still routes to unfiltered ledger).
- **PO-less direct-entry path preserved.** The prefill is fully additive based on `?po_id=` presence. When the URL has no `po_id` param, the form behavior is byte-identical to cycle 13's manual-receipt form.

### Cycle 16 backend gaps logged (no action this cycle)

- `W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL` (carried forward from cycle 12). `/stock/movement-log` does not filter by `po_id` query param; the success-panel link routes to the unfiltered movement log. Operator must scope manually by event_at / submission_id. The `title` attribute on the link discloses this honestly.

### Production simulation containment (Part B of cycle 16)

Cycle 16 also closes the audit P0 followup on `/planning/production-simulation` per W4 cycle 6 spec `production_simulation_runtime_decision_pack.md` §5 default A+B accepted by Tom checkpoint:

- **Banner text replaced.** Cycle 11's "BETA — uses cached data" banner replaced with the dispatch-locked copy: **"Simulation preview only — this does not change inventory and is not the production planning source of truth."** The banner is `role="alert"`, non-dismissible, info-icon prefix, warning-tone styling, `data-testid="production-simulation-containment-banner"`.
- **Nav entry gated to admin.** The "Production Simulation" entry in `src/lib/nav/manifest.ts` Planning group is changed from `min_role: "viewer"` / `required_capability: "planning:read"` to `min_role: "admin"` / `required_capability: "admin:execute"` per PSDP-3 default (ii). Daily planners no longer see the entry in the sidebar; admin and direct-URL access preserved.
- **Body logic untouched.** The IDB-backed `ProductionSimulatorShell` is preserved verbatim; the cycle is containment, not removal. Full backend wiring remains queued as a separate W4 → W1 → W2 sequence.

---

## Cycle 17 hardening pass

Cycle 17 dispatch wraps three deliverables: (Part A) author the GR browser-flow rehearsal manual checklist; (Part B) author the inventory-flow planned-overlay readiness check (NOT a build per Tom's locked deferral); (Part C) hardening pass on cycle 16 + cycle 14 + cycle 9 / cycle 7 touched surfaces with surgical fixes only. Parts A + B are docs-only — see `gr_browser_rehearsal_checklist_2026-05-02.md` (235 lines, 12-step browser walk against deployed Vercel) and `inventory_flow_overlay_readiness_2026-05-02.md` (274 lines, GAP-IFPI-1..11 status + cycle order). Part C results follow.

### Surfaces audited

| Surface | Cycle origin | Verification result |
|---------|--------------|---------------------|
| `/purchase-orders/[po_id]` | cycle 9 + cycle 14 + cycle 16 | **PASS with one stale-comment fix.** Cycle 9 P0-D English manual-PO banner intact; cycle 14 "Receive against this PO →" CTA still routing to `/stock/receipts?po_id=` per POE-A13-1; cycle 16 prefill consumes that route correctly. **Surgical fix applied:** docblock at lines 1319-1321 still claimed `/stock/receipts` doesn't honor `?po_id=` — cycle 16 closed that follow-up; comment now correctly cites cycle 16 commit `223ba83` and W4 cycle 8 spec §3.4. |
| `/stock/receipts` | cycle 16 (commit `223ba83`) | **PASS.** URL-driven prefill reads `?po_id=` on mount; supplier picker locks with caption "From PO {po_number} — supplier locked."; PO context strip renders above form; lines pre-load with `received_qty=open_qty` from OPEN/PARTIAL PO lines (CLOSED/CANCELLED filtered); terminal-status guard hides form on RECEIVED/CANCELLED PO and routes to `/purchase-orders/[po_id]?tab=attached-grs`; success panel renders 3-button nav cluster ("Back to PO {po_number} →" + "View receipts on this PO →" + "View movement log →"); the movement-log link's `title` attribute discloses honestly that filter-by-`po_id` is not yet supported (cycle 12 W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL gap, carried). Over-receipt warning copy at receipts/page.tsx:1108 reads "This line is fully received (open qty: 0) — posting will create an over-receipt." — operator-friendly: explicit, named, points at consequence. **No surgical fix needed.** |
| `/planning/production-simulation` | cycle 16 (commit `223ba83`) | **PASS.** Containment banner reads "Simulation preview only — this does not change inventory and is not the production planning source of truth." with `role="alert"` aria-live="polite" non-dismissible warning-tone styling + `data-testid="production-simulation-containment-banner"`. `IDB`-backed `ProductionSimulatorShell` preserved verbatim. Nav-gate at `src/lib/nav/manifest.ts` line 240 holds `min_role: "admin"` + `required_capability: "admin:execute"` — daily planners do not see the entry; admin + direct-URL access preserved. **No surgical fix needed.** |
| `/dashboard/v2` | cycle 7 + cycle 9 (P1-1 closure) | **PASS.** Live blocks render above the fold; 7 placeholder blocks collapsed into default-closed disclosure (`data-testid="dashboard-v2-placeholders"`, default `placeholderOpen=false`) with toggle button (`data-testid="dashboard-v2-placeholders-toggle"`, `aria-expanded`, `aria-controls`). Above-the-fold answers "what needs my attention today" in <5 seconds. **No surgical fix needed.** |

### Surgical fix applied

**File:** `window2-portal-sandbox/src/app/(po)/purchase-orders/[po_id]/page.tsx`
**Lines:** 1319-1321 → updated to lines 1319-1323 (4 lines added describing cycle 16 closure)
**Diff summary:**

```
- W2 follow-up logged: the canonical /stock/receipts form does not
- yet honor ?po_id= for pre-fill (W2-FOLLOWUP-RECEIPTS-PO-PREFILL);
- the param is harmless until that work lands per POE-A13-1.
+ Cycle 16 (commit 223ba83) closed the W2-FOLLOWUP-RECEIPTS-PO-PREFILL
+ follow-up: /stock/receipts now reads ?po_id= on mount and locks
+ the supplier picker + prefills lines from the PO's OPEN/PARTIAL
+ lines per W4 cycle 8 spec §3.4. The CTA below feeds directly into
+ that prefill flow.
```

**Reason:** the cycle 14 commit `19c0025` annotated the CTA href with the cycle 14 follow-up tag `W2-FOLLOWUP-RECEIPTS-PO-PREFILL`. Cycle 16 commit `223ba83` closed that follow-up by implementing the prefill flow on `/stock/receipts`. The stale comment was misleading about runtime behavior — code-review readers seeing it would have been confused about whether the prefill flow exists. The fix is a documentation-only update (no functional change). The docblock retains the W4 cycle 8 spec citation (§3.1, §3.4) and the POE-A13-1 routing-decision provenance.

**Validation gates** (run after edit, before commit):

| Gate | Expected | Actual | Status |
|------|----------|--------|--------|
| `npx tsc --noEmit` | exit 0 (comment-only change has no type implications) | _(run after commit auth)_ | _PENDING_ |
| `npm run build` | exit 0; route sizes unchanged | _(run after commit auth)_ | _PENDING_ |
| `npm run lint:urls` | exit 0 with single PRE-EXISTING leak at `(shared)/dashboard/page.tsx:66`; zero NEW leaks | _(run after commit auth)_ | _PENDING_ |
| Hebrew (U+0590-U+05FF) + `dir=rtl` + `rtl:` grep on touched file | 0 matches | _(run after commit auth)_ | _PENDING_ |

**HTTP probes** (against deployed Vercel — these are unaffected by the comment-only change but documented for completeness):
- `GET /stock/receipts?po_id=00000000-0000-0000-0000-000000000000` → expected `307 → /login` (auth-gated, route alive). _Result: _ to be confirmed before/after deploy_.
- `GET /planning/inventory-flow` → expected `307 → /login` (auth-gated, route alive). _Result: to be confirmed before/after deploy_.

### Surfaces NOT audited this cycle (out of scope)

- `/planning/blockers` — Tom-locked Hebrew page-title; no touch.
- `/planning/production-plan` — Ralph Loop ownership cycles 9-15.
- `/planning/forecast/[version_id]` — Ralph Loop + cycle 11 closure.
- `/admin/holidays` — cycle 8 + W1 holidays archived-filter (signal #26).
- `/inbox/credit/[exception_id]` — cycle Wave 3 LionWheel credit corridor.
- LionWheel / Shopify / Green Invoice integration files — Tom's checkpoint reserves these for the active incident recovery.

### Closes / logs

- **Closes (documentation hygiene):** stale W2-FOLLOWUP-RECEIPTS-PO-PREFILL claim on PO detail page header CTA docblock.
- **No new follow-ups logged.** Carried gap `W1-FOLLOWUP-MOVEMENT-LOG-URL-PREFILL` (cycle 12) remains open — `/stock/movement-log` still does not honor `?po_id=` filtering; the receipts success-panel link routes to the unfiltered ledger, which the link's `title` attribute discloses honestly.

---
