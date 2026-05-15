# Mobile Input Zoom Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop iOS Safari and other mobile WebKit browsers from auto-zooming whenever the user taps an input, textarea, or select inside the portal — without changing desktop typography, without disabling pinch-to-zoom accessibility, and without touching the 73 form-bearing component files individually.

**Architecture:** The portal's `"Operational Precision"` design system is intentionally 14px-dense (`tailwind.config.ts:131` defines `base = 0.875rem`, `sm = 0.8125rem`). Every `<input>` / `<textarea>` rendered through the `.input` and `.textarea` component classes inherits this sub-16px size (`src/app/globals.css:460-476`). iOS Safari, mobile Chrome on iOS, and any other WebKit-based mobile browser auto-zoom a form field on focus whenever the field's computed `font-size < 16px`. This is hardcoded WebKit behavior — not toggleable via viewport meta. The canonical, browser-standards-compliant fix is to ensure form elements compute to ≥16px on touch devices only, while leaving desktop density untouched. We achieve this with one media-scoped base-layer rule in `globals.css` keyed on `@media (hover: none) and (pointer: coarse)` (the canonical "is a touch device" query — covers iPhone, iPad in finger mode, Android phones, Android tablets, while iPad-with-trackpad correctly reports `hover: hover` and stays on desktop density). The rule applies `font-size: 16px !important` to `input`, `textarea`, `select`, and `[contenteditable]` so it wins against every existing `text-sm` / `text-xs` / `.fc-list-search-input` declaration. We deliberately keep `maximumScale: 5` in the viewport meta so OS pinch-to-zoom remains available — disabling that is the bad-engineer fix and breaks WCAG 1.4.4.

**Tech Stack:** Next.js 15 App Router, Tailwind v3.4, PostCSS, Playwright (Chromium-only project today — we will add a temporary mobile viewport project to verify the rule), Vitest (for a stylesheet-rule presence check that doesn't require a browser).

---

## Files

- **Modify:** `C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/globals.css` — add one `@media (hover: none) and (pointer: coarse)` block inside `@layer base` (immediately after the existing `input[type="number"]` block, around line 357 in the current file). This is the entire functional change.
- **Create:** `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/unit/globals-css-mobile-zoom.test.ts` — a Vitest unit test that reads `globals.css` from disk and asserts the rule exists with the correct selectors, the correct media query, and the correct value. Catches accidental removal during future refactors.
- **Create:** `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/mobile-input-zoom.spec.ts` — a Playwright spec that opens the login route on an iPhone-emulated viewport, focuses the email input, and asserts the computed `font-size` is exactly `16px` (not 13px / 14px). Catches regressions where someone adds a higher-specificity override.
- **Modify:** `C:/Users/tomw2/Projects/window2-portal-sandbox/playwright.config.ts` — add a second project named `mobile-safari` that runs against `devices["iPhone 14"]` so the new e2e spec actually exercises mobile WebKit behavior. Existing `chromium` project stays unchanged.
- **No change:** `src/app/layout.tsx` — the viewport meta is already correct (`initialScale: 1`, `maximumScale: 5`, `viewportFit: "cover"`). Lowering `maximumScale` would mask the symptom on iOS but break WCAG 1.4.4 (resize text accessibility) and is explicitly out of scope.
- **No change:** the 73 form-bearing component files. The base-layer `!important` rule wins against every component-level `text-sm` / `text-xs` declaration without touching any of them.

---

## Task 1: Add the touch-device font-size base rule

**Files:**
- Modify: `C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/globals.css` — insert new block immediately after the existing `input[type="number"] { -moz-appearance: textfield; }` declaration (current line 356) and before the closing `}` of the `@layer base` block (current line 357).

- [ ] **Step 1: Read the current `@layer base` closing region of `globals.css` to confirm exact insertion point**

Run (from any terminal — this is a read-only sanity check, not a code change):

```bash
sed -n '340,360p' "C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/globals.css"
```

Expected output ends with the lines:

```css
  input[type="number"] {
    -moz-appearance: textfield;
  }
}
```

The closing `}` on the last line is the close of `@layer base`. Our new block must be inserted **before** that closing `}`. If the line numbers have drifted, locate `input[type="number"] { -moz-appearance: textfield; }` and insert immediately after the `}` that closes it but still inside `@layer base`.

- [ ] **Step 2: Insert the touch-device font-size rule**

Use the Edit tool to insert the block. Find this exact `old_string`:

```css
  input[type="number"] {
    -moz-appearance: textfield;
  }
}
```

Replace with this exact `new_string`:

```css
  input[type="number"] {
    -moz-appearance: textfield;
  }

  /* ───────────────────────────────────────────────────────────────────────
     Touch-device input font-size floor — kills iOS focus-zoom.

     WebKit (iOS Safari, iOS Chrome, iOS Edge, every iOS browser) auto-zooms
     on focus whenever a form control's computed font-size is below 16px.
     Our "Operational Precision" type scale is intentionally 14px-dense on
     desktop, which means every .input / .textarea / native <select> on the
     portal triggers the zoom on a phone — small but persistent UX friction.

     Fix: on touch devices only, floor input/textarea/select/contenteditable
     font-size at 16px. Desktop density is preserved because hover-capable
     pointers (mouse, trackpad) match (hover: hover) and never enter this
     block. iPad Pro with the Magic Keyboard trackpad reports hover:hover
     and correctly keeps desktop density; iPad in finger-only mode reports
     hover:none and gets the 16px floor — both behaviors are correct.

     The !important is load-bearing: it must beat every component-level
     text-sm / text-xs declaration across the 70+ form files and the
     .fc-list-search-input 12px override in this same file, without
     editing them individually. We do not weaken this with a less-specific
     selector — that would let a future text-xs reintroduce the zoom.

     We do NOT lower viewport maximumScale to 1 — that would mask this
     symptom on iOS but break WCAG 1.4.4 (text resize) by disabling
     pinch-to-zoom for low-vision users. Floor the font-size; never cap
     the user's zoom.
     ─────────────────────────────────────────────────────────────────── */
  @media (hover: none) and (pointer: coarse) {
    input:not([type="checkbox"]):not([type="radio"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="file"]):not([type="hidden"]):not([type="range"]):not([type="color"]),
    textarea,
    select,
    [contenteditable="true"],
    [contenteditable=""],
    [role="textbox"],
    [role="combobox"],
    [role="searchbox"] {
      font-size: 16px !important;
    }
  }
}
```

- [ ] **Step 3: Verify the file parses by running the build**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npm run build
```

Expected: build completes without CSS parse errors. If you see `SyntaxError` from PostCSS pointing at `globals.css`, the insertion is malformed — re-check that the new block lives **inside** `@layer base` (the trailing `}` of `@layer base` must come after our new block).

- [ ] **Step 4: Verify dev server boots and the login form still renders**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx next dev -p 3737
```

In the same terminal session (or a separate one), open `http://127.0.0.1:3737/login` in a desktop browser. The email input should look identical to before (still 13px / `text-sm`). On a desktop browser this rule does not apply because desktop pointers report `hover: hover`.

Kill the dev server when done (`Ctrl+C`).

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git add src/app/globals.css && git commit -m "fix(mobile): floor input font-size at 16px on touch devices to stop iOS focus-zoom"
```

---

## Task 2: Add a unit test that locks the rule in place

**Files:**
- Create: `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/unit/globals-css-mobile-zoom.test.ts`

The risk we are pinning against: someone reformats `globals.css`, runs a Tailwind upgrade, or accepts an autofix that strips the media block. A pure-stylesheet check runs in milliseconds inside Vitest with no browser — cheap insurance.

- [ ] **Step 1: Write the failing test**

Create file `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/unit/globals-css-mobile-zoom.test.ts` with this exact content:

```typescript
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

// Locks in the iOS focus-zoom fix from globals.css. If this test fails,
// the touch-device font-size floor was removed or weakened — restore it
// before merging. See docs/superpowers/plans/2026-05-12-mobile-input-zoom-fix.md
// for the rationale.

const GLOBALS_CSS_PATH = resolve(__dirname, "..", "..", "src", "app", "globals.css");

describe("globals.css — touch-device input font-size floor", () => {
  const css = readFileSync(GLOBALS_CSS_PATH, "utf8");

  it("declares a (hover: none) and (pointer: coarse) media query", () => {
    expect(css).toMatch(/@media\s*\(\s*hover\s*:\s*none\s*\)\s*and\s*\(\s*pointer\s*:\s*coarse\s*\)/);
  });

  it("applies font-size: 16px !important inside that media query", () => {
    const match = css.match(
      /@media\s*\(\s*hover\s*:\s*none\s*\)\s*and\s*\(\s*pointer\s*:\s*coarse\s*\)\s*\{[\s\S]*?font-size\s*:\s*16px\s*!important[\s\S]*?\}\s*\}/
    );
    expect(match, "expected font-size: 16px !important inside the touch media block").not.toBeNull();
  });

  it("targets input, textarea, and select selectors inside the media query", () => {
    const block = css.match(
      /@media\s*\(\s*hover\s*:\s*none\s*\)\s*and\s*\(\s*pointer\s*:\s*coarse\s*\)\s*\{([\s\S]*?)\n\s*\}\s*\n\s*\}/
    );
    expect(block, "expected to find the touch-device media block").not.toBeNull();
    const inner = block![1];
    expect(inner).toMatch(/\binput\b/);
    expect(inner).toMatch(/\btextarea\b/);
    expect(inner).toMatch(/\bselect\b/);
  });

  it("excludes checkbox and radio inputs from the floor (visual buttons, not text)", () => {
    expect(css).toMatch(/input:not\(\[type="checkbox"\]\):not\(\[type="radio"\]\)/);
  });
});
```

- [ ] **Step 2: Run the test to confirm it passes against the Task 1 change**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx vitest run tests/unit/globals-css-mobile-zoom.test.ts
```

Expected: 4 passing tests, 0 failing.

If any test fails, the CSS rule from Task 1 was inserted incorrectly. Re-read `globals.css` around the insertion point and confirm the media query, the selectors, and the `!important` are all present.

- [ ] **Step 3: Confirm the test would fail without the rule (sanity check, DO NOT COMMIT)**

Temporarily edit `globals.css` and delete the entire `@media (hover: none) and (pointer: coarse) { ... }` block you added in Task 1. Re-run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx vitest run tests/unit/globals-css-mobile-zoom.test.ts
```

Expected: 4 tests fail (the regexes can't find the block).

Then **restore the deleted block** (use `git checkout -- src/app/globals.css` from inside the portal repo, since Task 1 already committed). Re-run the test to confirm it's back to 4 pass / 0 fail. This step proves the test is real — it isn't trivially passing because of a regex that always matches.

- [ ] **Step 4: Commit the test**

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git add tests/unit/globals-css-mobile-zoom.test.ts && git commit -m "test(unit): lock in iOS focus-zoom CSS rule via globals.css presence check"
```

---

## Task 3: Add a Playwright project for mobile WebKit emulation

**Files:**
- Modify: `C:/Users/tomw2/Projects/window2-portal-sandbox/playwright.config.ts`

Today the portal's Playwright config has a single `chromium` project running `Desktop Chrome`. To verify mobile behavior we need a mobile project. We add it alongside, not replacing, so the existing admin-routes-smoke / forecast / planner specs keep running unchanged.

- [ ] **Step 1: Read the current playwright.config.ts**

Run:

```bash
cat "C:/Users/tomw2/Projects/window2-portal-sandbox/playwright.config.ts"
```

Expected: matches the content shown in the planning context — single `chromium` project, `Desktop Chrome` device.

- [ ] **Step 2: Add the mobile-safari project**

Use the Edit tool. Find this exact `old_string`:

```typescript
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
```

Replace with this exact `new_string`:

```typescript
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      // Mobile WebKit emulation — used by tests/e2e/mobile-input-zoom.spec.ts
      // to verify the iOS focus-zoom CSS rule from globals.css. Playwright's
      // WebKit engine is the same engine iOS Safari ships with, so font-size
      // and media-query behavior match production iOS.
      name: "mobile-safari",
      use: { ...devices["iPhone 14"] },
      testMatch: /mobile-.*\.spec\.ts$/,
    },
  ],
```

The `testMatch` is intentional: this project ONLY runs specs whose filename starts with `mobile-`. We do not want existing admin-routes-smoke etc. running on a mobile viewport unintentionally — they would fail because they were written for desktop layouts. The `mobile-` prefix is the opt-in boundary.

- [ ] **Step 3: Verify Playwright accepts the config**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test --list
```

Expected: lists all existing specs under `[chromium] >` (because none match `mobile-*.spec.ts` yet) and reports zero specs under `[mobile-safari]`. No config-parse errors.

- [ ] **Step 4: Install the WebKit browser binary if not already present**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright install webkit
```

Expected: either "webkit already installed" or a fresh download. This is required because mobile-safari emulation uses Playwright's bundled WebKit engine.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git add playwright.config.ts && git commit -m "test(e2e): add mobile-safari Playwright project gated to mobile-* specs"
```

---

## Task 4: Write the failing mobile-zoom e2e spec

**Files:**
- Create: `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/mobile-input-zoom.spec.ts`

We test on the public `/login` route because it has a real `<input type="email">` and a real `<input type="password">`, requires no auth setup, and is the very first surface a mobile user would touch. The assertion is the same one the user reported as broken: when you tap an input on a phone, does the page zoom? If the input's computed font-size is ≥16px, iOS does not zoom.

- [ ] **Step 1: Confirm the login page has the inputs we plan to assert on**

Run:

```bash
sed -n '1,80p' "C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(auth)/login/page.tsx"
```

Expected output contains at least one `<input` element. If the login page does not have a real `<input>` (e.g. it's purely a redirect or a fake-auth picker without inputs), pick a different route: try `/admin/items` (paste search input) or `/inbox` (filter input). Update the route constant in Step 2 accordingly. Do not skip this check — picking a route with no inputs would make the test trivially pass.

- [ ] **Step 2: Write the failing test**

Create file `C:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/mobile-input-zoom.spec.ts` with this exact content:

```typescript
import { expect, test } from "@playwright/test";

// Mobile-only spec — runs under the mobile-safari Playwright project
// (playwright.config.ts). Verifies that input/textarea/select font-size
// computes to ≥16px on a touch viewport, which is what stops iOS from
// auto-zooming on focus.
//
// The route under test must be a public route with a real <input>. If
// the portal login route changes, switch ROUTE to another public input-
// bearing route (e.g. /auth/click-to-signin).

const ROUTE = "/login";

test.describe("mobile WebKit — input font-size floor", () => {
  test("every visible input on the login route computes to ≥16px font-size", async ({ page }) => {
    await page.goto(ROUTE);

    // Wait for at least one input to be in the DOM and visible — defends
    // against the route still being mid-hydration.
    const firstInput = page.locator("input:visible").first();
    await expect(firstInput).toBeVisible({ timeout: 5_000 });

    const fontSizes = await page
      .locator("input:visible, textarea:visible, select:visible")
      .evaluateAll((els) =>
        els.map((el) => {
          const cs = window.getComputedStyle(el as HTMLElement);
          return {
            tag: el.tagName.toLowerCase(),
            type: (el as HTMLInputElement).type ?? null,
            fontSizePx: parseFloat(cs.fontSize),
          };
        })
      );

    expect(fontSizes.length, "expected at least one visible input on the login route").toBeGreaterThan(0);

    for (const f of fontSizes) {
      // Skip controls that are visual buttons, not text-entry — they
      // don't trigger iOS zoom and are excluded from the CSS rule.
      if (f.tag === "input" && (
        f.type === "checkbox" ||
        f.type === "radio" ||
        f.type === "submit" ||
        f.type === "button" ||
        f.type === "reset" ||
        f.type === "file" ||
        f.type === "range" ||
        f.type === "color"
      )) continue;

      expect(
        f.fontSizePx,
        `<${f.tag}${f.type ? ` type="${f.type}"` : ""}> computed font-size ${f.fontSizePx}px is below the 16px iOS-zoom floor — the @media (hover: none) and (pointer: coarse) rule in globals.css was not applied`
      ).toBeGreaterThanOrEqual(16);
    }
  });
});
```

- [ ] **Step 3: Run the test to verify it passes against the Task 1 rule**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test --project=mobile-safari tests/e2e/mobile-input-zoom.spec.ts
```

Expected: 1 passed.

If it fails with `<input type="email"> computed font-size 13px is below the 16px iOS-zoom floor`, the CSS rule from Task 1 is not actually firing. Re-open `globals.css`, confirm the media block is inside `@layer base`, confirm there is no typo in `(hover: none) and (pointer: coarse)`, and rerun. If Playwright reports "device descriptor not found: iPhone 14", upgrade to a current iPhone device name from `npx playwright devices` output and retry.

- [ ] **Step 4: Confirm the test would fail without the rule (sanity check, DO NOT COMMIT)**

Temporarily delete the `@media (hover: none) and (pointer: coarse) { ... }` block from `globals.css`. Re-run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test --project=mobile-safari tests/e2e/mobile-input-zoom.spec.ts
```

Expected: 1 failed, with the error message naming the offending input and its sub-16px font-size.

Then restore the deleted block:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git checkout -- src/app/globals.css
```

Re-run the test to confirm it's back to 1 pass.

- [ ] **Step 5: Confirm the chromium project still passes (no regression)**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test --project=chromium
```

Expected: every existing spec still passes. The new mobile-only spec does not run here (its filename starts with `mobile-`, so `testMatch: /mobile-.*\.spec\.ts$/` on the mobile project excludes it from chromium via `testMatch` not being set on chromium — Playwright runs all specs by default on a project unless overridden). If chromium picks up the mobile spec and fails because it runs on desktop viewport, add `testIgnore: /mobile-.*\.spec\.ts$/` to the chromium project definition.

- [ ] **Step 6: Commit**

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git add tests/e2e/mobile-input-zoom.spec.ts && git commit -m "test(e2e): verify input font-size ≥16px on mobile WebKit to prove iOS focus-zoom is killed"
```

---

## Task 5: Guard chromium project from picking up mobile specs

**Files:**
- Modify: `C:/Users/tomw2/Projects/window2-portal-sandbox/playwright.config.ts`

This is a small belt-and-braces step: even though the `mobile-safari` project has `testMatch` to opt in to mobile specs, the default `chromium` project still scans `tests/e2e/**` and would run the mobile spec on desktop Chrome, where it'd fail (`mobile-` specs are written for mobile viewports). Add a matching `testIgnore` to chromium.

- [ ] **Step 1: Add testIgnore to the chromium project**

Use the Edit tool. Find this exact `old_string`:

```typescript
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
```

Replace with this exact `new_string`:

```typescript
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      testIgnore: /mobile-.*\.spec\.ts$/,
    },
```

- [ ] **Step 2: Verify chromium no longer lists mobile specs**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test --project=chromium --list
```

Expected: `tests/e2e/mobile-input-zoom.spec.ts` does NOT appear in the list. All other specs do.

- [ ] **Step 3: Verify mobile-safari still lists only mobile specs**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test --project=mobile-safari --list
```

Expected: only `tests/e2e/mobile-input-zoom.spec.ts` appears.

- [ ] **Step 4: Run the full Playwright suite end-to-end as the final regression check**

Run:

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && npx playwright test
```

Expected: all specs pass under both `chromium` and `mobile-safari` projects. If anything fails that was passing before, stop and investigate — do not paper over it.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git add playwright.config.ts && git commit -m "test(e2e): exclude mobile-*.spec.ts from chromium project to keep desktop runs clean"
```

---

## Task 6: Final acceptance — manual mobile verification

This is the gate the user explicitly cares about: "תיבות וחלונות לכתיבה או מילוי [...] עושה זום קטן". The automated tests prove the CSS rule is in the bundle and applies on emulated mobile WebKit. They do not prove how iOS Safari on Tom's actual phone behaves in practice — only Tom's phone can do that. This task is non-skippable.

- [ ] **Step 1: Deploy the change to the staging environment Tom uses on his phone**

The portal's deploy mechanism is owned by Tom (per CLAUDE.md: "git push, merge, deploy — Tom only"). Push the branch and ask Tom to deploy / merge / promote per the existing workflow. Do not autonomously deploy.

```bash
cd "C:/Users/tomw2/Projects/window2-portal-sandbox" && git push
```

Stop here and prompt Tom: "Please pull this to your mobile-accessible environment (staging or main) and confirm the next step."

- [ ] **Step 2: Tom verifies on iPhone Safari**

Acceptance script — Tom runs this on his own phone in Safari, after the deploy:

  1. Open the portal in iPhone Safari.
  2. Navigate to `/login`. Tap the email field. **Expected:** the page does not zoom in. The field gains focus, the keyboard slides up, the rest of the page does not change scale.
  3. Sign in (or use the dev-shim if staging) and navigate to a form-heavy route — try `/admin/items` (search bar), `/stock/receipts` (quantity inputs), and `/admin/products/new` (text + textarea fields).
  4. Tap each kind of field — text, number, search, textarea, select. **Expected:** none of them trigger a zoom on focus.
  5. Pinch-to-zoom anywhere on the page. **Expected:** the page does zoom — accessibility pinch-to-zoom still works (this is the WCAG 1.4.4 requirement we deliberately preserved).
  6. Reply with PASS or FAIL.

- [ ] **Step 3: If PASS, the fix is done**

No further code changes. The CSS rule, the unit test, and the e2e test are all in place to prevent regression.

- [ ] **Step 4: If FAIL, diagnose and iterate**

The most likely causes of a FAIL after Task 1-5 all passed automatically:

  - **CDN / browser cached the old CSS.** Ask Tom to hard-reload (long-press the reload icon in Safari → "Request Desktop Website" then back, or close-and-reopen the tab). If hard-reload fixes it, the CSS rule is correct and the issue was stale-cache only — note this in the commit log but no code change is needed.
  - **A specific form field uses inline `style={{ fontSize: ... }}` with a sub-16px value.** Inline style normally loses to `!important`, but if the inline style itself has `!important` (rare but possible via `style={{ fontSize: '13px !important' }}` — React 19+ supports this), it would beat the CSS rule. Search the codebase: `grep -r "fontSize" src/ | grep -i "important"`. If a match exists, remove the `!important` from the inline style — the CSS rule is the correct owner of this concern.
  - **A specific page renders inputs in a Shadow DOM.** The CSS rule does not pierce shadow boundaries. The portal does not currently use Shadow DOM, but if any future component (e.g. a third-party embedded widget) does, the rule must be repeated inside the shadow root. Diagnose by opening Safari Web Inspector → Computed pane → check the font-size source.

In all three cases, the resolution is small and local — do not weaken the base rule.

---

## Self-Review

**Spec coverage:**

- "iOS Safari zooms on input focus" → killed by Task 1 (CSS font-size floor on touch devices).
- "Don't break desktop density" → preserved by media-query scoping (`hover: none` / `pointer: coarse`).
- "Don't break pinch-to-zoom accessibility" → preserved (we floor font-size, not cap `maximumScale`).
- "Don't touch 73 files individually" → preserved (single base-layer rule with `!important`).
- "Lock the fix in place against future regressions" → Task 2 (unit), Task 4 (e2e).
- "Tom-actually-tries-it gate" → Task 6.

**Placeholder scan:** No `TBD`, no "implement later", no "add appropriate handling". Every step has either exact code or an exact command.

**Type consistency:** No TypeScript types introduced. The Playwright spec uses Playwright's built-in `expect` / `test` only. The Vitest spec uses `readFileSync` / `resolve` / Vitest's built-in `expect` / `it` / `describe` only. No cross-task type references.

**One subtle thing I want to flag explicitly:** the Playwright project name is `mobile-safari` and uses `devices["iPhone 14"]` (which is WebKit-backed in Playwright). If Playwright deprecates `iPhone 14` in a future release, the device name needs to roll forward. The Task 3 Step 4 install command tolerates this — but a future executor running this plan after a Playwright major upgrade may need to substitute `iPhone 15` or similar. The acceptance criterion is "device descriptor exists and uses WebKit"; the specific iPhone model number is incidental.
