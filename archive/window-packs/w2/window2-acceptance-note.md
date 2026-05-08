# Window 2 — Acceptance Note

_Written 2026-04-14 (review round). This is the **current source of truth** for Window 2 sandbox state. Supersedes the pre-review sections called out inline in `window2-review-pack.md` and the frontend-package spec._

Tom's review round locked a specific work order in six numbered items. This note answers all six. Everything below is verified with commands that ran in the space-safe canonical path. No scope expansion happened in this round; the only behavior change was one shell bug fix surfaced by the Playwright tests (noted in §4).

---

## 1. Workspace truth note

### The only three relevant paths

```
Canonical Window 2 sandbox (runnable, editable, single source of truth)
    C:/Users/tomw2/Projects/window2-portal-sandbox/

Frozen Dropbox reference for Window 2 sandbox (historical, not editable)
    c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/portal/
    → contains only REDIRECT.md pointing at the canonical path
    → the historical src/ tree that was here before the move is obsolete;
      do not read it, do not diff against it; it will not receive edits

Canonical gt-factory-os working repo (a different work stream, separate concern)
    C:/Users/tomw2/Projects/gt-factory-os/
    → its own git repo, active development, currently Tranche 1 Step 2 (D2)
    → ALREADY has an active portal/ at C:/Users/tomw2/Projects/gt-factory-os/portal/
      built under a different architecture (shared/ layout, radix+shadcn,
      PermissionGuard + WriteContext, mocked api-client, vitest already set up)
```

### Is there more than one `gt-factory-os` clone on disk?

**Yes. Two.** Exactly two, and they are not equivalent:

1. **Canonical working repo:** `C:/Users/tomw2/Projects/gt-factory-os/` — git-tracked, on `main`, clean working tree, 10+ recent commits, D2 portal work in progress. This is what Window 1 (or whichever Tranche 1 Step 2 window) actually commits to.
2. **Dropbox docs snapshot:** `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Cowork Projects/Production & Finance/gt-factory-os/` — **not a working repo**. Contains only `README.md`, `docs/` (3 supabase-runbook-style files), `supabase/` (config.toml, migrations/, functions/, seed.sql), `.env.example`, `.gitignore`. **No `portal/`. No `.git/`. No `node_modules/`.** It is a curated, manually-synced doc mirror — Dropbox cross-device reviewing only.

### Which clone is canonical?

**`C:/Users/tomw2/Projects/gt-factory-os/`** is canonical for `gt-factory-os`. The Dropbox docs snapshot is a derived view, not a working copy.

### Where would the future `portal/` land when/if porting from the Window 2 sandbox?

**There is no clean "port" target.** The original review pack's recommendation assumed `gt-factory-os/portal/` was empty and could be filled by porting `PRODUCTION/portal/`. That assumption is **factually wrong**. The canonical portal already exists and is being built with a different architecture by a different work stream. Per the committed `gt-factory-os/docs/portal_coordination.md`:

> "Window 2 is treated as a completely separate work stream per the explicit instruction 'treat Window 2 as separate unless/until I explicitly define a merge plan.' ... Any structural similarity between my portal shell and Window 2's portal is a direct consequence of locked decision 2 on the v1 tech stack — not of copying. ... Until that merge plan exists, the two portals are independent islands."

So the port trigger is no longer "one `GET /read/*` endpoint lands." See §6 for the corrected statement.

### File-path collision risk

None. The two portals live in different filesystem subtrees:

- Window 2 sandbox: `C:/Users/tomw2/Projects/window2-portal-sandbox/`
- Canonical `gt-factory-os/portal/`: `C:/Users/tomw2/Projects/gt-factory-os/portal/`

They are siblings under `C:/Users/tomw2/Projects/` but do not share files or git trees.

### Why the move out of Dropbox

The Dropbox path `GTeveryday Dropbox\Data Center\Tom\...` contains spaces that break Windows npm postinstall scripts (they misparse the unquoted path at the first space and look for `C:\Users\tomw2\napi-postinstall\...`). Both `npm install` and `npm run dev` fail in-place. Moving outside Dropbox was a prerequisite for local dev. The move leaves a `REDIRECT.md` stub at the old location explaining where the code now lives.

---

## 2. Patched spec/doc truth note

The three pre-existing Window 2 docs were scanned for test-coverage and scaffolding overclaims, plus the now-wrong port-trigger assumption. Patches applied in place with visible "Superseded 2026-04-14" markers:

| File                              | What was patched                                                                                                                                  |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| `window2-portal-spec.md` §10      | Line "does not pick a form library, validation library, styling system, or test runner" now carries a Superseded note — stack + test runners chosen. |
| `window2-frontend-package.md` §9  | Implementation-sequence preamble now points at this acceptance note as the current source of truth for run/test commands.                         |
| `window2-frontend-package.md` §10 | "No unit/e2e/integration tests in this pass" is now marked Superseded; points to the new test layer (§4 below).                                   |
| `window2-review-pack.md` §1       | The "no `portal/` subdirectory anywhere inside `gt-factory-os`" claim is marked Superseded — the original scan missed the canonical Projects clone. |
| `window2-review-pack.md` §7       | Pre-review "no test runner" state is marked Superseded; points to §4 here for current commands + pass results.                                    |
| `window2-review-pack.md` §8       | "Port into `gt-factory-os/portal` once one read endpoint lands" recommendation is marked Superseded — the destination already has different code. Corrected trigger is §6 here. |

The patches are non-destructive: the original text is still readable for historical continuity, preceded by a visible "Superseded 2026-04-14 (review round)" block.

No dates in the review pack's Appendix A (invariants summary) were touched — those claims are still true. The role-tightening work in §5 below actually makes some of them stronger.

---

## 3. Runnable local path

**One canonical path, space-safe, runs without hacks:**

```
C:/Users/tomw2/Projects/window2-portal-sandbox/
```

### Verified commands (run in this review session)

All four commands Tom asked for, plus two test commands, captured from this session:

| Command                     | Result                                                                                       |
|-----------------------------|----------------------------------------------------------------------------------------------|
| `npm install`               | ✓ `added 371 packages in 47s`                                                                |
| `npm install --save-dev …`  | ✓ `added 44 packages in 25s` (vitest, happy-dom, fake-indexeddb, @playwright/test, @vitest/expect) |
| `npx playwright install chromium --with-deps` | ✓ Chrome for Testing 147.0.7727.15 + headless shell downloaded to `%LOCALAPPDATA%\ms-playwright\` |
| `npx tsc --noEmit`          | ✓ exit 0, no output                                                                          |
| `npx next build`            | ✓ 28 static routes prerendered, no blocking errors, bundle sizes unchanged from review pack  |
| `npm run dev`                | ✓ Next.js 15 starts on configured port; Playwright's webServer config boots it at port 3737  |
| `npm test` (= `vitest run`) | ✓ 5 files, 41 tests passed (~2.3s)                                                          |
| `npm run test:e2e`          | ✓ 13 Playwright tests passed (~40s)                                                         |

### First-run instructions for Tom

```bash
cd /c/Users/tomw2/Projects/window2-portal-sandbox
# Dependencies are already installed in this session. To reinstall cleanly:
#   rm -rf node_modules && npm install
npm run dev       # → http://localhost:3000 (default Next dev port)
npm run typecheck # → should exit 0
npm run build     # → 28 routes, static
npm test          # → 41 vitest unit tests
npm run test:e2e  # → 13 Playwright smoke tests (starts its own dev server on 3737)
```

### `.next/` cache note

`node_modules/` and `.next/` are inside the canonical path. The `.gitignore` excludes them. The whole directory is not under version control yet — it's a sandbox. If Tom wants a git init, that's a one-command follow-up.

---

## 4. Test commands + pass results

### 4.1 Minimum credibility test layer — added this round

The review pack's §7 said "no unit test runner, no e2e runner, no `tests/` folder, Playwright does NOT exist." That is no longer true. This round added a minimum test layer focused on review credibility, not on production coverage.

### 4.2 Commands

```bash
npm test           # vitest run  — 41 unit tests, headless, happy-dom + fake-indexeddb
npm run test:watch # vitest      — watch mode for iterative work
npm run test:e2e   # playwright test — 13 smoke tests against a live Next dev server on :3737
```

### 4.3 Vitest layer — 41/41 passing

Structure:

```
tests/
├── setup-vitest.ts                     fake-indexeddb shim + crypto polyfill
└── unit/
    ├── features/
    │   ├── count-variance.test.ts      9 tests  (blind-flow branching helper)
    │   ├── goods-receipt-schema.test.ts 10 tests  (line validation + header)
    │   └── waste-adjustment-schema.test.ts 9 tests (superRefine rules)
    └── repositories/
        ├── generic-repo.test.ts        7 tests  (OC + soft archive)
        └── boms-repo.test.ts           6 tests  (draft-only + activation retire)
```

Coverage of Tom's explicit vitest list:

| Tom's item                                                        | Where                                                   | Cases |
|-------------------------------------------------------------------|---------------------------------------------------------|-------|
| Optimistic concurrency in `generic-repo`                          | `generic-repo.test.ts` describe 1                       | 3     |
| Soft archive behavior                                             | `generic-repo.test.ts` describe 2                       | 4     |
| BOM draft-only edit rule                                          | `boms-repo.test.ts` describe 1                          | 3     |
| BOM activation retires prior active version                      | `boms-repo.test.ts` describe 2                          | 3     |
| Waste-adjustment validation refine                                | `waste-adjustment-schema.test.ts`                       | 9     |
| Receipts line validation                                          | `goods-receipt-schema.test.ts`                          | 10    |
| Count blind-flow branching helper (extracted for testability)     | `count-variance.test.ts`                                | 9     |

Last-run summary:

```
Test Files  5 passed (5)
     Tests  41 passed (41)
  Duration  1.60s
```

**Two small refactors were required to make the form schemas testable without mounting React:**

1. Extracted `wasteAdjustmentSchema` to `src/features/ops/waste-adjustment-schema.ts`. The page file re-imports it. No behavior change.
2. Extracted `goodsReceiptSchema` + `goodsReceiptLineSchema` to `src/features/ops/goods-receipt-schema.ts`. Same pattern.
3. Extracted `classifyCountVariance` to `src/features/ops/count-variance.ts` (this is the "if extracted" bullet Tom explicitly permitted). The page file uses it via a single import; the in-page decision code is gone. A small doc header explains the rule.

### 4.4 Playwright layer — 13/13 passing

Structure:

```
tests/e2e/
├── helpers.ts                          setFakeRole / setReviewForcedState / resetIdb
├── role-switch.spec.ts                 5 cases
├── admin-items-crud.spec.ts            2 cases
├── goods-receipt-success.spec.ts       1 case
├── forecast-dirty.spec.ts              2 cases
└── review-mode-forced-state.spec.ts    3 cases
```

Coverage of Tom's Playwright list:

| Tom's item                                              | Where                                        |
|---------------------------------------------------------|----------------------------------------------|
| Fake login / role switch                                | `role-switch.spec.ts` (5 cases, all roles)  |
| Admin item create/edit happy path                       | `admin-items-crud.spec.ts` case 1            |
| Goods receipt shell success-state path                  | `goods-receipt-success.spec.ts`              |
| Forecast cell edit dirty-state path                     | `forecast-dirty.spec.ts` case 1              |
| Review-mode forced-state rendering on one operator form | `review-mode-forced-state.spec.ts` (3 cases covering success / approval_required / stale_conflict on Goods Receipt) |

Bonus cases (free reinforcement of §5 role-tightening):

- `role-switch.spec.ts`: operator cannot reach `/admin/items` even by direct URL — expects the "Not available for your role" card.
- `role-switch.spec.ts`: viewer role sees dashboard but not operator forms.
- `admin-items-crud.spec.ts` case 2: planner sees `/admin/items` but the `+ New item` button is not rendered and the "read-only for planner" badge shows.
- `forecast-dirty.spec.ts` case 2: viewer sees forecast read-only, no numeric input cells render.

Last-run summary:

```
Running 13 tests using 1 worker
  ok  1 [chromium] › admin-items-crud.spec.ts:5 admin create happy path        2.8s
  ok  2 [chromium] › admin-items-crud.spec.ts:38 planner read-only             919ms
  ok  3 [chromium] › forecast-dirty.spec.ts:5  planner dirty counter           2.1s
  ok  4 [chromium] › forecast-dirty.spec.ts:28 viewer read-only                1.1s
  ok  5 [chromium] › goods-receipt-success.spec.ts:5 success state             2.4s
  ok  6 [chromium] › review-mode-forced-state.spec.ts:5 forced success         1.0s
  ok  7 [chromium] › review-mode-forced-state.spec.ts:24 forced approval       1.0s
  ok  8 [chromium] › review-mode-forced-state.spec.ts:35 forced stale          1.0s
  ok  9 [chromium] › role-switch.spec.ts:5  default planner                    881ms
  ok 10 [chromium] › role-switch.spec.ts:11 operator hides planner nav         844ms
  ok 11 [chromium] › role-switch.spec.ts:24 admin reveals master-data nav      818ms
  ok 12 [chromium] › role-switch.spec.ts:32 viewer no operator forms           946ms
  ok 13 [chromium] › role-switch.spec.ts:40 operator blocked from admin        899ms
  13 passed (39.9s)
```

### 4.5 What Playwright caught during authoring (credit to the test layer)

While wiring the smoke tests, Playwright surfaced a real shell bug I had not caught during the build round or the review round:

**Goods Receipt's `viewToState` helper mapped `view: "form"` → `"empty"`**, which meant the page's early-return `if (effective === "empty") return <EmptyState/>` fired on initial mount, and the form **never actually rendered in its natural state** — only when review mode forced a different screen state. This is exactly the kind of bug that structured visual summaries cannot catch. The fix was one edit to the `effective` computation (pass `null` when `view === "form"` and no forcedScreenState) and is the only behavior change in this round. Typecheck + build + Playwright + Vitest all confirm the fix.

This is a concrete payoff for the minimum test layer — it paid for its own cost during its first run.

### 4.6 What is still missing (deliberately)

No accessibility audit. No visual regression. No component-tree snapshot tests. No contract tests (nothing to contract against yet). No per-screen Playwright state-matrix across all 7 states × all operator forms — only one form × 3 states. Adding more Playwright coverage is cheap once a merge plan exists.

---

## 5. Explicit statement of what remains mock-only

The role tightening landed in the sandbox. Here is the current surface, with explicit mock-only calls so reviewers don't confuse real behavior with shell behavior:

### 5.1 What tightened in this round

- `(operator)/layout.tsx` — was `["operator", "planner", "admin"]`, now **`["operator"]`**. Operator-only URLs (`/home`, `/ops/receipts`, `/ops/waste-adjustments`, `/ops/counts`, `/ops/production-actual`, `/my-submissions`) render the "Not available for your role" card for non-operator roles. Reviewers use the FAKE SESSION chip to switch.
- Admin maintenance pages (`/admin/items`, `/admin/components`, `/admin/boms`, `/admin/suppliers`, `/admin/supplier-items`, `/admin/planning-policy`, `/admin/users`) now read `canWrite = useHasRole("admin")` and gate every mutation button behind it. Planner can enter each page, browse the list, open the detail panel to inspect, but **cannot see** `+ New …`, `Save`, `Archive/Reactivate`, or BOM-specific `New draft` / `Save draft lines` / `Activate version` / `+ Add BOM line` controls. The BOM editor's `isDraft` flag is `ANDed` with `canWrite`, so planner sees draft line rows as read-only strings, not editable selects.
- `/admin/users` — role dropdown and Deactivate/Reactivate button are hidden for planner; they see a neutral `Badge` with the current role.
- Planning surfaces (`/planning/forecast`, `/planning/purchase-recommendations`) already gated writes behind `useHasRole("planner", "admin")` in the build round; no change needed. Verified by the viewer-read-only Playwright test.

The Playwright role-switch specs (5 cases) plus the `admin-items-crud.spec.ts#2` planner-read-only spec verify all of this in one browser run.

### 5.2 What is still mock-only (unchanged, restated for clarity)

All of the following are mock in the sandbox and must remain mock until the explicit port/merge plan exists:

1. **Authentication.** No `@supabase/supabase-js` imported anywhere. `FakeSession` + `gt.fakeauth.v1` localStorage chip + `RoleGate` + `useHasRole` is the entire auth surface. The FAKE SESSION chip in the top bar is the only way to "log in".

2. **All stock-affecting writes** — Goods Receipt / Waste / Adjustment / Physical Count / Production Actual / PO Form. The submit handler is a `setView("success")` or confirm-then-`setView("success")` no-op. No `fetch`. No outbox replay. No ledger posting. No idempotency-key dedup at a server.

3. **Planning workspace saves.** Forecast grid edits mutate local React state only; save/publish/discard buttons render but do nothing. Purchase recommendation approve/reject/hold only mutate local React state.

4. **Inbox actions.** Exceptions acknowledge/resolve and approvals approve/reject mutate local React state only.

5. **Jobs Monitor Run now / Disable.** Disabled at the button level.

6. **Integrations Admin.** Three static tiles, buttons disabled.

7. **All backend contracts.** Everything in `window2-portal-spec.md` §5 is still a Window 2 proposal, not a locked API shape.

8. **Outbox/retry reconciler loop.** Envelope is defined in the DTO layer; no replay runs.

9. **Attachments.** No upload. No file handling. Storage model is `TODO-WINDOW1`.

10. **Real-time concurrency, websockets, Supabase realtime.** Not wired.

11. **Master-data mutations going to the real backend.** Admin CRUD writes go to `fake-indexeddb` (in tests) or browser IndexedDB (in dev). They never leave the browser. Optimistic concurrency is enforced on the client and by the in-browser store, not by any server.

12. **Planning policy values flowing into operator forms.** The operator form shells still read hardcoded mock thresholds (`LARGE_THRESHOLD = 25`, count auto-post `5%` / `2` abs). The admin Planning Policy page persists edits to IndexedDB but no form reads from it. Rewire is a `TODO` in the freeze list of the review pack.

### 5.3 What is NOT mock but also not yet final

- `GenericIdbRepo` and `IdbBomsRepo` are real code with real behavior — optimistic concurrency, audit bump, soft delete, BOM versioning, draft-only edits, activation retiring prior active. They are just bound to IndexedDB instead of a real API. When the real API lands, an `ApiRepo<T>` implementation against the same `Repository<T>` interface replaces them. The 41 unit tests guard the contract of the `Repository<T>` interface and the BOM rules.

---

## 6. Explicit port trigger statement

### 6.1 The corrected trigger

**Do not port `window2-portal-sandbox/` into `gt-factory-os/portal/` at any point without an explicit merge plan from Tom.** There is no automatic trigger.

The review pack's original recommendation — "port once Window 1 lands one `GET /read/*` endpoint" — was written under the assumption that the destination was empty. The destination is not empty: `C:/Users/tomw2/Projects/gt-factory-os/portal/` is being built as "Tranche 1 Step 2, D1–D7 deliverable sequence" by a separate work stream, with a different architecture (`shared/` layout vs my `components/` + `features/`, radix/shadcn primitives vs my hand-rolled primitives, `PermissionGuard` + `WriteContext` vs my `RoleGate` + `useHasRole`, mocked `api-client` + `read-model-hooks` vs my `Repository<T>` + IndexedDB). The committed `docs/portal_coordination.md` in that repo **explicitly forbids touching `PRODUCTION/portal/` and forbids reading Window 2 code** until a merge plan exists.

### 6.2 What would have to happen for a port to make sense

Two independent preconditions, both required:

1. **Tom writes and locks a merge plan** — this is a coordination document explicitly naming which of the two parallel implementations is the keeper per concern: auth context, permission-guard semantics, form primitive placement, API-client shape, layout scaffolding, master-maintenance page pattern. Until that plan exists, there is nothing to port *into*. It is explicitly a Tom decision, not a window-level decision.
2. **Window 1 has landed at least one concrete API read model** that both portals could target. Without that, there is no forcing function to reconcile the two — each can keep drifting in parallel forever.

### 6.3 What to do before the merge plan exists

Per Tom's constraint "**no more new routes, no more deeper Tier 2/Tier 3 features, no Supabase integration, no auth integration, no backend assumptions added silently**":

- **Keep the Window 2 sandbox frozen as a review-only artefact.** Changes are allowed only for:
  - Bug fixes surfaced by the test layer (like the `viewToState` bug fixed this round).
  - Tightening role/permission semantics in the mock (already done in §5).
  - Polishing master maintenance per the review pack §6A list, if and when Tom asks.
  - Adding tests to existing behavior.
- **Do not edit the canonical `gt-factory-os/portal/`** — that belongs to the other work stream. Window 2 has zero business in that repo.
- **Do not import Window 2 code into the canonical repo and do not import canonical repo code into Window 2.** This is the coordination-note rule; honor it in both directions.
- **Do not write a "just in case" unified shared-types package.** That is a merge-plan-level decision.

### 6.4 What `npm run dev` on each side shows today

For reviewers who want to see both:

| Path                                                 | What it boots                                                                      |
|------------------------------------------------------|-------------------------------------------------------------------------------------|
| `C:/Users/tomw2/Projects/window2-portal-sandbox/`    | Full Window 2 shell — 28 routes, master-data CRUD, operator forms, planning workspaces, dashboard, inboxes. |
| `C:/Users/tomw2/Projects/gt-factory-os/portal/`      | Tranche 1 Step 2 D2 scaffold — shared primitives + tests, no feature pages yet. |

They are deliberately separate. Opening both in parallel is the current review surface.

---

## Appendix A — Full list of files added/changed this round

### Added

```
window2-portal-sandbox/
├── playwright.config.ts
├── vitest.config.ts
├── src/features/ops/count-variance.ts            (new, extracted helper)
├── src/features/ops/waste-adjustment-schema.ts   (new, extracted schema)
├── src/features/ops/goods-receipt-schema.ts      (new, extracted schema)
└── tests/
    ├── setup-vitest.ts
    ├── unit/
    │   ├── features/
    │   │   ├── count-variance.test.ts
    │   │   ├── waste-adjustment-schema.test.ts
    │   │   └── goods-receipt-schema.test.ts
    │   └── repositories/
    │       ├── generic-repo.test.ts
    │       └── boms-repo.test.ts
    └── e2e/
        ├── helpers.ts
        ├── role-switch.spec.ts
        ├── admin-items-crud.spec.ts
        ├── goods-receipt-success.spec.ts
        ├── forecast-dirty.spec.ts
        └── review-mode-forced-state.spec.ts
```

Also added at the old Dropbox location:

```
PRODUCTION/portal/REDIRECT.md   (stub pointing at the canonical path)
```

### Changed in existing sandbox files

- `src/app/(operator)/layout.tsx` — `RoleGate` allow list from `["operator","planner","admin"]` → `["operator"]`.
- `src/app/(admin)/admin/items/page.tsx` — `useHasRole("admin")` gate on `+ New item`, Save, Archive. `data-testid`s added on SKU input, Name input, Save button, New-item button for Playwright hooks.
- `src/app/(admin)/admin/components/page.tsx` — same gate pattern.
- `src/app/(admin)/admin/suppliers/page.tsx` — same gate pattern.
- `src/app/(admin)/admin/supplier-items/page.tsx` — same gate pattern.
- `src/app/(admin)/admin/planning-policy/page.tsx` — same gate pattern.
- `src/app/(admin)/admin/boms/page.tsx` — same gate pattern + `isDraft = isDraft && canWrite` for the line editor + gated `+ New draft from latest`, Activate, Save draft lines, Start new draft.
- `src/app/(admin)/admin/users/page.tsx` — role dropdown and Deactivate button gated.
- `src/app/(operator)/ops/receipts/page.tsx` — **bug fix** for `viewToState` making the form never render in its natural state. Schema import switched to the extracted `goodsReceiptSchema`. `data-testid`s added on supplier select, line-item select, line-qty input.
- `src/app/(operator)/ops/waste-adjustments/page.tsx` — schema import switched to extracted `wasteAdjustmentSchema`.
- `src/app/(operator)/ops/counts/page.tsx` — uses extracted `classifyCountVariance` helper instead of inline branching logic.
- `src/lib/repositories/generic-repo.ts` — `WithIdAudit` interface tightened (removed over-broad `[k: string]: unknown` index signature) for the tests to compile cleanly.
- `tsconfig.json` — `exclude` now adds `tests`, `playwright-report`, `test-results`.
- `package.json` — scripts added: `test`, `test:watch`, `test:e2e`. Devdeps added: vitest, @vitest/expect, fake-indexeddb, happy-dom, @playwright/test.

### Changed in existing Dropbox spec files

- `window2-portal-spec.md` — §10 test-runner bullet marked Superseded.
- `window2-frontend-package.md` — §9 preamble + §10 tests bullet marked Superseded.
- `window2-review-pack.md` — §1, §7, §8 Superseded blocks added. Body text unchanged below the supersession markers.

---

## Appendix B — Constraint compliance check

Tom's explicit prohibitions on this round:

| Constraint                                                          | Status                                                                                    |
|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| No more new routes                                                  | ✓ — zero new routes. 28 total, unchanged from review pack.                                |
| No more deeper Tier 2/Tier 3 features                               | ✓ — only test hooks (`data-testid`), role gates on existing buttons, and one shell bug fix. |
| No Supabase integration                                             | ✓ — zero `@supabase/*` imports anywhere in `src/`. Can be verified with `grep -r`.       |
| No auth integration                                                 | ✓ — fake auth unchanged.                                                                  |
| No backend assumptions added silently                               | ✓ — no new API-shape assumptions in shell code. Test assumptions live entirely in pure-function helpers and the swappable `Repository<T>` interface. |
| Connected UI for stock-affecting workflows                          | ✗ prohibited → ✓ still mock                                                               |
| Browser → core tables directly                                      | ✗ prohibited → ✓ all master-data IO goes through the `Repository<T>` interface           |
| Silent drift from route/readiness matrix                            | ✗ prohibited → ✓ route list unchanged; readiness matrix honored                           |
| Expanding scope before the review package is accepted               | ✗ prohibited → ✓ only the items Tom explicitly asked for were built                       |

---

_End of Window 2 acceptance note._
