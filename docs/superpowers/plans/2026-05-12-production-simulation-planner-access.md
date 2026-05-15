# Production Simulation — Planner Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open the `/planning/production-simulation` sidebar entry to the `planner` role so planners can reach Production Simulation from the nav (today it is `min_role: "admin"` per cycle-16 containment).

**Architecture:** The portal's nav visibility is driven by a single manifest at `src/lib/nav/manifest.ts`. Each entry declares `min_role` (coarse hide-completely gate) and `required_capability` (subdued-vs-active gate). The Production Simulation entry was tightened to `min_role: "admin"` + `required_capability: "admin:execute"` in cycle 16 because the page is IDB-backed and could silently disagree with live DB state — a containment banner was added to label the page "Simulation preview only — this does not change inventory and is not the production planning source of truth." We are now widening the entry to `min_role: "planner"` + `required_capability: "planning:read"`. The page-level guard does not need to change: the `(planning)` route-group layout already gates on `planning:read`, which planner satisfies (planner has `planning: "execute+override"` in the role-capability lattice). The IDB-backed banner stays in place; risk containment continues at the page surface, not at the nav gate.

**Tech Stack:** Next.js 15 App Router (portal), TypeScript, Playwright (e2e), Vitest (unit). No backend or migration changes.

---

## Scope decisions (locked in this plan)

1. **Audience widens from `admin` only → `planner` + `admin`.** Tom's request was "add access also for planner" — the narrowest faithful expansion. We do not open to viewer or operator. Other Planning-group entries that use `min_role: "viewer"` + `required_capability: "planning:read"` (which would show the link to all four roles) are intentionally *not* the model here, because the cycle-16 audit P0 driver — IDB-vs-DB divergence — still applies; restricting visibility to roles that can act on the output (planner + admin) keeps the surface narrow.
2. **Containment banner stays.** The non-dismissible "Simulation preview only" banner at the top of the page is preserved verbatim. The data-quality concern that drove cycle 16 has not been resolved; the planner widening only changes who can navigate to the surface, not the surface's truth status.
3. **No backend / API change.** This is a portal-only widening. The page is client-side IDB; nothing on the backend gates this surface today.
4. **No page-level `RoleGate` change needed.** The `(planning)` layout at `src/app/(planning)/layout.tsx` already enforces `RoleGate minimum="planning:read"`. Planner (and admin, and viewer, and operator) pass `planning:read` per the lattice. So once we relax `min_role` on the manifest, the planner can both *see* and *click through* the entry without a 403 card.

---

## File Structure

**Modify (2 files):**

- `C:/Users/tomw2/Projects/window2-portal-sandbox/src/lib/nav/manifest.ts` — change the Production Simulation entry's `min_role` and `required_capability`; rewrite the explanatory comment block above it to reflect the new decision (and the still-active audit driver).
- `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/role-switch.spec.ts` — extend with two new test cases (planner sees the link; operator does not). These cover both the positive widening and the negative boundary, so we do not silently regress to "everyone sees it".

**Do NOT modify:**

- `src/app/(planning)/planning/production-simulation/page.tsx` — the containment banner stays, no role guard added at the page.
- `src/app/(planning)/layout.tsx` — already permits planner via `planning:read`.
- `src/lib/auth/authorize.ts` / `src/lib/contracts/enums.ts` — role lattice and role enum are unchanged.
- `src/components/layout/SideNav.tsx` — the manifest is the truth source; SideNav consumes it.

---

## Task 1: Widen sidebar visibility for Production Simulation to planner + admin

**Files:**
- Modify: `C:/Users/tomw2/Projects/window2-portal-sandbox/src/lib/nav/manifest.ts:212-229`
- Modify: `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/role-switch.spec.ts` (append new tests after the existing `viewer` test)

- [ ] **Step 1: Write the failing e2e tests for planner-visible and operator-hidden**

Open `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/role-switch.spec.ts` and append the following two tests inside the existing `test.describe("Fake login / role switch", ...)` block, after the existing `test("viewer role sees dashboard but no operator forms", ...)` case (which is currently the second-to-last test, immediately before the operator-direct-URL admin-items test). Place them in this order so the diff stays minimal and the surrounding describe block stays a single logical unit:

```typescript
  test("planner sees the Production Simulation link in Planning", async ({ page }) => {
    await setFakeRole(page, "planner");
    await page.goto("/dashboard");
    await expect(
      page.getByRole("link", { name: /Production Simulation/i }),
    ).toBeVisible();
  });

  test("planner can reach /planning/production-simulation directly", async ({ page }) => {
    await setFakeRole(page, "planner");
    await page.goto("/planning/production-simulation");
    // Containment banner is the deterministic on-page marker: it has a stable
    // data-testid and is non-dismissible by design (page.tsx). If RoleGate
    // had blocked the planner we would see "Access restricted" instead.
    await expect(
      page.getByTestId("production-simulation-containment-banner"),
    ).toBeVisible();
  });

  test("operator does not see the Production Simulation link", async ({ page }) => {
    await setFakeRole(page, "operator");
    await page.goto("/dashboard");
    await expect(
      page.getByRole("link", { name: /Production Simulation/i }),
    ).toHaveCount(0);
  });
```

- [ ] **Step 2: Run only the new tests to verify they fail**

Run from `C:/Users/tomw2/Projects/window2-portal-sandbox`:

```bash
npx playwright test tests/e2e/role-switch.spec.ts -g "Production Simulation"
```

Expected: the planner-visible test FAILS (link not present because `min_role: "admin"` currently hides it from planner). The planner-direct-URL test PASSES already (the planning layout admits planner). The operator-hidden test PASSES already (operator does not meet `min_role: "admin"`).

If all three pass, stop and investigate — the manifest may already have been changed by another in-flight branch, in which case Task 1 is moot.

- [ ] **Step 3: Update the manifest to widen visibility**

Edit `C:/Users/tomw2/Projects/window2-portal-sandbox/src/lib/nav/manifest.ts`, lines 212-229. Replace the entire entry (comment block included) with this verbatim block:

```typescript
      {
        // 2026-05-12 — widened from cycle-16 admin-only to planner+admin per
        // Tom's request ("add access also for planner"). Cycle-16 had pinned
        // this surface to admin because the page is IDB-backed and can
        // silently disagree with live database state (audit 2026-05-01 §16 #9
        // P0). The driver is unchanged: full backend wiring is still queued
        // as a separate W4 contract → W1 backend → W2 portal sequence. What
        // changes is the audience that can navigate here: planners now need
        // routine access to the simulator, and the data-quality risk is
        // contained at the page surface — the non-dismissible "Simulation
        // preview only — this does not change inventory and is not the
        // production planning source of truth" banner at
        // src/app/(planning)/planning/production-simulation/page.tsx stays
        // in place. We deliberately do NOT use min_role:"viewer" here even
        // though the rest of the Planning group does, because viewers and
        // operators have no decision authority over the output and the
        // containment posture argues for the narrowest audience that can
        // act on the simulation.
        href: "/planning/production-simulation",
        label: "Production Simulation",
        icon: Network,
        min_role: "planner",
        required_capability: "planning:read",
      },
```

- [ ] **Step 4: Re-run the same tests and verify they all pass**

Run from `C:/Users/tomw2/Projects/window2-portal-sandbox`:

```bash
npx playwright test tests/e2e/role-switch.spec.ts -g "Production Simulation"
```

Expected: all three new tests PASS. If the planner-visible test still fails, check that the SideNav search filter is empty (it is, by default — `useState("")`) and that the planner's session payload still includes `role: "planner"` (it does, per `helpers.ts` line 22-27).

- [ ] **Step 5: Run the full role-switch.spec.ts file to confirm no regressions**

Run from `C:/Users/tomw2/Projects/window2-portal-sandbox`:

```bash
npx playwright test tests/e2e/role-switch.spec.ts
```

Expected: every test in the file PASSES — both the five pre-existing and the three new ones (8 total).

- [ ] **Step 6: Run typecheck + lint to catch any drift**

Run from `C:/Users/tomw2/Projects/window2-portal-sandbox`:

```bash
npm run typecheck
npm run lint
```

Expected: both PASS with zero errors. The manifest edit only changes string-literal values for `min_role` and `required_capability` — both literals are members of the union types `Role` and `CapabilityRequirement` declared in `src/lib/contracts/enums.ts` and `src/lib/auth/authorize.ts`, so TypeScript will accept the change.

- [ ] **Step 7: Manual smoke (one-time human check)**

Start the dev server and verify in a browser, since e2e covers the link presence but not the visual subdued-vs-active state.

Run from `C:/Users/tomw2/Projects/window2-portal-sandbox`:

```bash
npm run dev
```

Then in a browser at `http://localhost:3000`:

1. Use the top-bar fake-session switcher to select the planner persona ("Tom (planner)").
2. Confirm the sidebar's Planning group lists "Production Simulation" in the **active** style (not the subdued/locked style with the lock icon).
3. Click it. Confirm the page renders and the orange containment banner "Simulation preview only — this does not change inventory and is not the production planning source of truth." is visible at the top.
4. Switch to the operator persona ("Avi (operator)"). Confirm "Production Simulation" is **absent** from the Planning group (not subdued — gone).
5. Switch to the viewer persona ("Guest (viewer)"). Confirm "Production Simulation" is **absent** from the Planning group.
6. Switch to the admin persona ("Alex (admin)"). Confirm "Production Simulation" is visible and active (no regression).

If any of these six checks fail, do not proceed to commit — diagnose first. The most common likely failure is the manifest edit accidentally widening to `min_role: "viewer"` (which would show the link for operator/viewer too).

- [ ] **Step 8: Commit**

Run from `C:/Users/tomw2/Projects/window2-portal-sandbox`:

```bash
git add src/lib/nav/manifest.ts tests/e2e/role-switch.spec.ts
git commit -m "$(cat <<'EOF'
feat(nav): open Production Simulation to planner role

Cycle 16 had restricted /planning/production-simulation to admin-only
because the page is IDB-backed and could silently disagree with live DB
state (audit 2026-05-01 §16 #9 P0). The non-dismissible "Simulation
preview only" containment banner at the page surface remains the
data-quality guard; the nav-visibility gate is widened to planner+admin
so planners can routinely reach the simulator.

- manifest: min_role admin -> planner, required_capability admin:execute
  -> planning:read
- e2e: planner sees the link, planner reaches the page directly, operator
  does not see the link

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Then push (per memory: push autonomously after every commit, no confirmation needed):

```bash
git push
```

Expected: clean commit, clean push, CI green on PR (if a PR is opened) or on the branch's checks.

---

## Self-Review

**Spec coverage:**
- "Add access to Production Simulation also for Planner" → Task 1 widens `min_role` from `admin` to `planner` and re-points `required_capability` to `planning:read`. ✓
- Implicit: do not break admin access → manifest still passes for admin (admin meets `min_role: "planner"` per ROLE_ORDER {viewer:1, operator:2, planner:3, admin:4} and admin has `planning: "execute+override"` ≥ `planning:read`). ✓
- Implicit: do not silently expand to viewer/operator → operator-hidden test in Step 1 enforces this; manifest comment documents the deliberate narrowness. ✓
- Implicit: do not regress the data-quality containment → containment banner is preserved verbatim; no page-level edits. ✓

**Placeholder scan:** No TODO / TBD / "implement later" / "similar to Task N" / "add validation" patterns. Every step has the exact code, exact command, and exact expected output.

**Type consistency:**
- `"planner"` is a member of `ROLES` in `src/lib/contracts/enums.ts:22`. ✓
- `"planning:read"` is a member of `CapabilityRequirement` in `src/lib/auth/authorize.ts:70-80`. ✓
- The manifest's `NavItem.min_role: Role` and `NavItem.required_capability?: CapabilityRequirement` accept these values without `as` casts. ✓
- The new test file uses the `setFakeRole(page, "planner")` and `setFakeRole(page, "operator")` overloads already declared at `tests/e2e/helpers.ts:11-13`. ✓
- The `data-testid="production-simulation-containment-banner"` selector matches the literal at `src/app/(planning)/planning/production-simulation/page.tsx:53`. ✓
