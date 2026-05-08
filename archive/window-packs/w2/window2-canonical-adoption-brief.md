# Canonical Portal — Window 2 Design Adoption Brief

_2026-04-14 · planning-only · references `window2-design-transfer.md` as the token source of truth_

**Audience:** whoever is building `C:/Users/tomw2/Projects/gt-factory-os/portal/` (the canonical portal, currently at Tranche 1 Step 2, D2 shared primitives stage). This brief tells you how to adopt the Window 2 visual system without rewriting your architecture.

**This is a plan, not a PR.** Nothing gets copied or edited in the canonical repo as a result of this document. The brief exists so that when adoption work is approved, the sequence, the guardrails, and the acceptance criteria are already settled.

---

## 1. Adoption objective

Apply the Window 2 design system to the canonical portal **with minimum architectural disruption**.

Specifically:

- The canonical portal gains the Operational Precision visual language: warm bone paper, petrol-teal accent, Public Sans + IBM Plex Mono, 14px operational density, hairline borders, dot-driven status semantics, tabular numerics.
- The canonical portal keeps its own primitive architecture intact. No Radix/shadcn components are replaced. No `<Button>` becomes a class-based `.btn`. No `<Dialog>` gets swapped for a custom modal.
- The canonical portal keeps its own auth, permission, and dev-affordance systems (`AuthProvider`, `PermissionGuard`, `WriteContext`, `RoleSwitcher`).
- The canonical portal keeps its own routing, layout structure, and read-model-hooks API surface.
- Adoption happens **at the token and pattern layer only**, composed on top of the canonical's existing primitives.

The deliverable, at the end of adoption, is: a canonical portal that **looks like Window 2** to a reviewer but **is structured like the canonical** to an engineer. No reviewer would confuse screenshots of the two. No engineer reading the code would find Window 2 files.

---

## 2. Locked decisions

These four decisions are now the default. They govern any adoption work going forward, unless Tom explicitly overrides.

### D1 — Window 2 is the design language lead

The tokens, visual hierarchy, density rules, and pattern language in `window2-design-transfer.md` §1 are the **authoritative design direction** for the canonical portal. Where the canonical portal's current design differs from the Window 2 system, the canonical yields to the Window 2 system.

Concretely: the canonical portal's Tailwind config, typography, palette, spacing scale, radius, shadow, motion, icon library, and density rules are reconciled to match Window 2. Any pre-existing design-level decision in the canonical (cool-white backgrounds, stock Tailwind blue, system fonts, 16px base) is overridden.

### D2 — The canonical portal keeps its existing primitive architecture

The canonical portal uses Radix + shadcn (`src/components/ui/{button,input,label,card,dialog,select,tabs,badge,sonner}.tsx`). **Do not replace these with Window 2's hand-rolled primitives.** Hand-rolled classes (`.btn`, `.input`, `.card`, `.table-base`) were optimal for the sandbox's scope — not for a production repo that already has a more rigorous primitive foundation.

Adoption happens by:

- **Tokens** — shared colors, typography, spacing, radius, shadow, motion.
- **Typography** — Google Font wiring in the canonical's `layout.tsx`.
- **Restyling** — the canonical's `ui/*.tsx` Radix wrappers get updated class bindings that reference the new tokens, but keep their Radix structure.
- **Pattern composition** — new screens in the canonical use the canonical's primitives composed into the Window 2 patterns (dashboard tile shape, admin split view, eyebrow + title + description card header, dot-driven status badges).

### D3 — Canonical dev/runtime conventions win inside the canonical repo

The following **are not ported** into the canonical portal under any circumstances:

| Do not port                             | Canonical already has                                    |
|-----------------------------------------|----------------------------------------------------------|
| `ReviewModePanel`, `StatePreviewChip`   | N/A — dev affordance out of scope for the canonical.    |
| `FAKE SESSION` pill (yellow warning)    | `RoleSwitcher` + `AuthProvider` handle dev role swapping.|
| "blocked" nav chip concept              | Canonical doesn't model blocked-route status this way.   |
| `useHasRole`, `useSession` hooks        | `PermissionGuard` + `WriteContext` handle this.          |
| `SessionProvider` from sandbox          | `AuthProvider` already exists.                           |
| `GenericIdbRepo` / IndexedDB repositories| Canonical has `shared/api-client/` + `read-model-hooks`.|
| `SplitListLayout` component             | Canonical will build its own layout primitives.          |
| Sandbox route assumptions (28 routes)   | Canonical builds its own route tree Tranche-by-Tranche. |
| Any `src/lib/fixtures/*.ts` fixture files | Canonical has `fixtures/masters/*.json` with its own contract. |
| Any `src/lib/review-mode/*` file        | N/A.                                                     |

If a sandbox file is visually compelling, **take the markup shape and rebuild it on the canonical's primitives** — do not Ctrl-C/Ctrl-V the file.

### D4 — No dark-theme work now

Light-only remains the correct scope for v1. The token system is dark-compatible in theory (define a `[data-theme="dark"]` branch against the same semantic token names) but that work is explicitly **out of scope** for this adoption round. Tom will flag it separately if/when dark mode becomes a goal.

---

## 3. Step-by-step adoption sequence

Five work packages, in order. Each is a single reviewable unit. Do not interleave.

### Step 1 — Tokens (1 day)

Drop the Window 2 token system into the canonical portal's Tailwind config and base CSS. No component changes.

**Files likely touched**

- `portal/tailwind.config.ts` — full color palette (`bg`, `fg`, `border`, `accent`, `success`, `warning`, `danger`, `info`), font-size scale, letter-spacing tokens, radius scale, shadow tokens, spacing half-steps, keyframes, animations, timing functions. Replaces whatever is currently there.
- `portal/src/app/globals.css` — base layer (`html`/`body` background, dot-grid texture, selection color, scrollbar, tabular numerics, stripped Chrome spinners, focus-visible style) plus utility layer (`.eyebrow`, `.dot`, `.bg-grid`, `.bg-grid-fade`, `.reveal`, stripe border). **Do not** add `.btn`/`.input`/`.card` component classes here — those fight Radix.

**Expected visual gain**

All existing canonical primitives (Button, Input, Card, Dialog, Select, Tabs, Badge) immediately render in warm bone / petrol / graphite even though their component code is untouched. This delivers **~60% of the total visual lift** on day one.

**What must not be changed**

- Do not touch any `src/components/ui/*.tsx` file.
- Do not touch any `src/shared/*` file.
- Do not add or remove any route.
- Do not introduce `clsx` / `tailwind-merge` / icon library dependencies (if not already installed — check canonical's package.json first).
- Do not add `.btn`, `.input`, `.card`, `.table-base`, `.chip` component classes.

**Validation gate**

1. `npm run typecheck` (canonical repo) exits 0.
2. `npm run test` (canonical repo Vitest) passes unchanged.
3. `npm run build` (canonical repo Next.js) succeeds.
4. Manual visual smoke: load the canonical portal in dev, verify no broken layout or unreadable contrast. Five minutes, eyeball only.

**Rollback approach**

Single commit. Revert the commit to restore the previous palette. No state migration. No data migration. The token change is pure CSS. Canonical's tests give immediate regression signal if something breaks.

---

### Step 2 — Typography wiring (1 hour)

Add Public Sans + IBM Plex Mono to the canonical portal and wire them globally.

**Files likely touched**

- `portal/src/app/layout.tsx` — import `Public_Sans` and `IBM_Plex_Mono` from `next/font/google`, add to the `<html>` className as CSS variables (`--font-public-sans`, `--font-plex-mono`).
- `portal/tailwind.config.ts` — `fontFamily.sans` and `fontFamily.mono` arrays reference the CSS variables.
- `portal/src/app/globals.css` — `html`/`body` get `font-sans`. `font-variant-numeric: tabular-nums` is global.

**Expected visual gain**

All text in the canonical portal switches from system fonts to Public Sans. Numerics align by column. The product gains the operational tone Window 2 has.

**What must not be changed**

- Do not change any component's explicit font className.
- Do not add a second sans family for display text. Single-family discipline is part of the design contract.
- Do not change font weights in any component yet.

**Validation gate**

1. Canonical typecheck + build + tests pass unchanged.
2. Visual smoke: open the canonical portal in dev. Confirm Public Sans is loaded (DevTools → Computed → font-family). Confirm `input[type=number]` renders tabular digits.

**Rollback approach**

Revert the single commit. `next/font` is stateless.

---

### Step 3 — Restyle canonical primitives (1 day)

Update the class bindings inside `src/components/ui/*.tsx` so each Radix-wrapped primitive renders against the new token system. The component API stays unchanged; only the visual expression changes.

**Files likely touched**

- `portal/src/components/ui/button.tsx` — update variants (`default`/`destructive`/`outline`/`secondary`/`ghost`/`link`) to match §1.4 + §1.9 conventions. Heights, padding, radius, focus ring. Match the Window 2 button rhythm (`h-9` default, `rounded-md`, `text-sm font-medium`, hairline border with `inset 0 0 0 1px rgba(255,255,255,0.6)` highlight for the default variant).
- `portal/src/components/ui/input.tsx` — 36px height, 6px radius, hairline border at 80% opacity, petrol focus ring, warm bone raised background.
- `portal/src/components/ui/label.tsx` — uppercase eyebrow style (`text-2xs font-semibold uppercase tracking-sops text-fg-muted`).
- `portal/src/components/ui/card.tsx` — bg-raised, `border/70`, `shadow-raised`, gradient header from `bg-raised` to `bg/40`.
- `portal/src/components/ui/dialog.tsx` — `shadow-pop` for the modal, `bg-raised` content surface, warm backdrop overlay instead of stock black.
- `portal/src/components/ui/select.tsx` — chevron rotates on open, option rows on hover use `bg-subtle/60`, selected option uses `bg-accent-soft text-accent`.
- `portal/src/components/ui/tabs.tsx` — active tab uses an accent bottom border (2px) instead of a background fill; inactive tabs muted.
- `portal/src/components/ui/badge.tsx` — rounded-sm (4px), `text-3xs` uppercase tracked `sops`, four tones (`default`/`secondary`/`destructive`/`outline`) re-mapped to the Window 2 semantics. Add support for a dot prefix.
- `portal/src/components/ui/sonner.tsx` — toast styling to match the warm bone aesthetic (rounded-md, shadow-pop, hairline border).

**Expected visual gain**

Every existing canonical screen (even the minimal D1/D2 scaffold pages) now looks fully polished. Buttons, forms, cards, modals, selects — all look like Window 2 even though they remain Radix underneath. The remaining 30% of the visual lift lands here.

**What must not be changed**

- Do not change the component's exported API. `<Button variant="default" size="sm">` keeps its contract.
- Do not remove Radix slots or `asChild` support.
- Do not import `lucide-react` inside `ui/*.tsx` unless the component already uses an icon (many don't — leave them alone).
- Do not add new variants beyond what already exists. New variants are a feature creep risk.

**Validation gate**

1. `npm run typecheck` exits 0.
2. `npm run test` — the canonical already has tests for `StatusBadge`, `TextInput`, `Field`, `ConfirmDialog`, `PermissionGuard`, etc. All must still pass. If a test is asserting a specific class (e.g. `expect(button).toHaveClass("bg-blue-600")`), update the assertion — not the component.
3. `npm run build` exits 0.
4. Visual diff review. Open the canonical portal in dev, walk every route that renders one of the touched primitives, compare against a before-screenshot set.

**Rollback approach**

Single commit per primitive file, OR one squash commit for all 9 files if the team prefers. Revert cleanly. No state migration. If a specific primitive restyle breaks, revert just that file.

---

### Step 4 — Tier A pattern composition (2–3 days, only as Tier A screens are being built)

Apply Tier A patterns **as the canonical portal's D4 work (the 5 Master Maintenance screens) lands**, not as a retroactive rewrite.

This is the most important timing point in the brief: the canonical portal is at D2 (shared primitives). D3 is mocked API. D4 is the 5 master-maintenance screens. **Adoption of Tier A patterns must happen in lockstep with D4 — the screens should be built with the Window 2 patterns from the first file commit, not retrofitted after.**

**Files likely touched**

- `portal/src/shared/layout/AppShell.tsx` — page frame (max-width 1440px, padding rhythm, 232px side nav, 40px gap). Adopt the Window 2 shell rules (§1.8). Keep the canonical's `AppShell` component contract; only the internal layout and spacing changes.
- `portal/src/shared/layout/TopBar.tsx` — brand mark on the left, optional status strip, right-aligned action area that holds `RoleSwitcher` (the canonical's dev affordance). Apply Window 2 style to the brand + height + sticky backdrop, but keep `RoleSwitcher` as the session-switching element — **not** the FAKE SESSION pill.
- `portal/src/shared/layout/Sidebar.tsx` — icon + label + active accent-bar pattern. Icons from `lucide-react` using the canonical icon mapping from `window2-design-transfer.md` §1.6. Group headers as eyebrows with trailing hairline.
- `portal/src/shared/layout/MaintenanceBanner.tsx` — adopt Window 2 banner visual (left accent bar, icon chip, semantic tone) even though its purpose is canonical-specific.
- `portal/src/shared/form-primitives/Field.tsx` — update label to eyebrow style. Error message with inline icon. Hint line.
- `portal/src/shared/form-primitives/TextInput.tsx`, `NumberInput.tsx`, `StatusBadge.tsx`, `ConfirmDialog.tsx`, `ConflictDialog.tsx` — restyled where their visuals differ from the Window 2 system.
- `portal/src/shared/form-primitives/EditableCell.tsx` (if it exists) — apply focus-glow pattern for cell editors.
- New files under `portal/src/app/...` as the D4 Master Maintenance screens are built. Each screen composes the above primitives into Window 2 patterns.

**Tier A patterns to apply** (see §4 for the detailed map):

1. **Admin master-maintenance split view** — list + detail pane grid. Match the Window 2 `SplitListLayout` shape without copying the file.
2. **Admin table / list chrome** — match `.table-base` behavior using the canonical's Tailwind classes on a plain `<table>`.
3. **Admin detail pane** — `Card` with `CardHeader` eyebrow/title/description/actions, `CardContent` form grid, sticky action footer at the bottom.
4. **Dashboard tile composition** — eyebrow + mono numeric hero + optional accent-pct bar + dotted badges footer + faint atmosphere watermark.
5. **Freshness + readiness cluster** — vertical list of boundary systems with `FreshnessBadge`-shape compact chips.

**Expected visual gain**

The canonical portal's Tranche 1 Master Maintenance screens look production-grade from the moment they are first committed. Zero retrofit debt.

**What must not be changed**

- Do not introduce a parallel `SplitListLayout` component from Window 2. Rebuild the layout pattern inline in the canonical screen.
- Do not add any sandbox route. The canonical's route tree is the canonical's route tree.
- Do not create a `components/layout/AppShellChrome.tsx` in the canonical. The canonical uses `shared/layout/AppShell.tsx`.
- Do not import any `@/` path that resolves to a sandbox source file.
- Do not copy any fixture data from the sandbox. The canonical has its own `fixtures/masters/*.json`.

**Validation gate**

1. All canonical tests still pass.
2. Each new D4 screen has at least one Playwright smoke test in the canonical's own test suite (not Window 2's). Tests may reference elements by testid or role/name — do **not** port Window 2's test spec files.
3. Visual review by Tom: compare the canonical's new Tranche 1 screens to the Window 2 sandbox admin screens. The layout, the eyebrows, the card headers, the table rhythm, the audit snippet should be visually interchangeable. The underlying code is not.

**Rollback approach**

Per-screen commit granularity. If an adoption decision ages badly, revert that screen's commit and re-implement on the canonical's own previous conventions. The underlying Step 1–3 work is not rolled back.

---

### Step 5 — Pause and review gate (hard stop)

After Step 4 completes: **stop**. Do not proceed to Tier B or Tier C patterns.

**Why the stop exists**

Tier B (forecast grid, purchase recs queue, exceptions list, approvals cards) and Tier C (operator forms, variance card, PO form, outbox) depend on backend contracts that do not exist yet in Tranche 1. Attempting to apply those patterns before the contracts exist creates a false "we have planning" or "we have receipts" signal — exactly what the Window 2 review round warned against.

**What this gate checks**

1. Token adoption matches §1.1–§1.5 values exactly (palette, typography, radius, shadow, motion).
2. Typography is Public Sans for UI, IBM Plex Mono for numerics, tabular numerics global.
3. Every Radix primitive in `src/components/ui/` uses the new tokens.
4. The D4 Master Maintenance screens use Tier A patterns end-to-end.
5. No Window 2 file has been copied into the canonical. (grep check: zero imports from `@/lib/fixtures/`, `@/lib/auth/fake-auth`, `@/lib/review-mode/`, or equivalent sandbox paths.)
6. Canonical's existing tests all pass.
7. New tests exist for D4 screens in the canonical's own test suite.
8. Tom confirms the visual gate with a single review session.

**Only after this gate** does adoption work resume — and only when the next Tranche's backend contracts are confirmed.

**Rollback approach**

None required — the gate is a review checkpoint, not a code change.

---

## 4. Tier A adoption map

Five patterns. For each: where it lands in the canonical, what it depends on, how hard it is, and whether it's safe to adopt before real backend contracts are live.

### 4.1 Admin master-maintenance split view

**Target canonical surface:** the D4 Master Maintenance screens — 5 screens under `portal/src/app/admin/...` (exact routes TBD by the canonical's Tranche 1 Step 2 planner). Each screen renders a list of master records + a detail pane for create/edit.

**Dependencies:**

- Step 1–3 complete (tokens + primitives restyled).
- Canonical's `api-client` layer provides mocked list/get/create/update for master-data domains. (Already true at D3.)
- Canonical's `PermissionGuard` / `WriteContext` gates write operations.

**Expected complexity:** medium. 5 screens × ~4 hours each = ~2.5 days once the primitives are ready. Most of the weight is in the detail pane form composition; the list is a straightforward table.

**Safe before backend contracts are live?** Yes. The canonical's mocked api-client is the shim. Tier A is explicitly about master maintenance, which doesn't touch the stock ledger or the planning engine. This is the safest possible adoption target.

### 4.2 Admin table / list chrome

**Target canonical surface:** the table component used inside every admin master-maintenance screen. Not a standalone shared component — each screen renders its own `<table>` using the canonical's Tailwind conventions against a reusable row/cell class style.

**Dependencies:**

- Step 1 tokens (for the header + row + border colors).
- Step 3 primitive restyle (for any `<Button size="sm">` inside row actions).

**Expected complexity:** low. ~2 hours. The table visual is pure CSS.

**Safe before backend contracts are live?** Yes. Pure presentation.

### 4.3 Admin detail pane

**Target canonical surface:** the right-hand detail pane component inside each master-maintenance screen. Composed from `Card` + `CardHeader` (Window 2 eyebrow/title/description/actions pattern) + `CardContent` (form grid with Window 2 `Field` rhythm) + a sticky action footer (new pattern on top of existing Radix primitives).

**Dependencies:**

- Steps 1–3 complete.
- Canonical's `Field` + `TextInput` + `NumberInput` + `ConfirmDialog` + `ConflictDialog` primitives already exist at D2.
- Canonical's `WriteContext` gates the form's submit handler.

**Expected complexity:** medium. ~4 hours per unique detail pane shape. Most detail panes share structure, so the first one costs more and the rest are cheap.

**Safe before backend contracts are live?** Yes. Form submit goes through the mocked api-client layer already in place.

### 4.4 Dashboard tile composition

**Target canonical surface:** whatever dashboard page the canonical eventually builds (Tranche 5 or later per `docs/portal_coordination.md`). Until then, this pattern is **documented but not implemented** in the canonical.

**Dependencies:**

- Steps 1–3 complete.
- Canonical has at least one read-model hook that returns a scalar (e.g. `useHealth` already exists in `src/shared/read-model-hooks/`).
- Dashboard surface is intentionally deferred until Tranche 5.

**Expected complexity:** low once it's the right time. ~2 hours to compose the tile shell on top of the canonical's `Card` primitive.

**Safe before backend contracts are live?** **With caveat.** The tile *shape* is safe to adopt the day the canonical has any dashboard page at all. The *specific metrics* (stock health, planning run, exceptions summary, readiness) require the matching read models, which belong to later Tranches. Recommendation: build a single "system health" tile from `useHealth` as soon as the canonical has a dashboard, using the Window 2 tile shape. Add more tiles per Tranche as read models land.

### 4.5 Freshness / readiness cluster

**Target canonical surface:** a subsection of the canonical dashboard (once a dashboard exists). Renders a vertical list of boundary systems (LionWheel, Shopify, Green Invoice, ledger) each with a time-since stamp + semantic health dot.

**Dependencies:**

- Step 1 tokens.
- Canonical `read-model-hooks` for boundary-system health. Only `useHealth` exists today; more will come as integrations land in later Tranches.

**Expected complexity:** low. ~2 hours once a dashboard page exists.

**Safe before backend contracts are live?** With caveat. Same as 4.4 — the shape is safe, but the content depends on read models that don't all exist yet. Start with one integration (the first one that has a health endpoint) and add more as they land.

---

## 5. Canonical conflict watchlist

Six failure modes, ranked by likelihood and severity. For each: what it looks like, why it happens, how to avoid it.

### 5.1 Token drift

**Symptom:** pockets of the canonical portal still render in cool white / stock Tailwind blue / system fonts / rounded-8px cards, mixed with newly token-correct surfaces. The UI feels inconsistent — not broken, but visibly stitched.

**Likely cause:** Step 1 (tokens) was committed but one of these happened:

- A component inside `src/components/ui/*.tsx` hard-codes a Tailwind color class like `bg-blue-600` or `text-slate-500` that the token switch didn't cover.
- A component inside `src/shared/*.tsx` uses a non-token color inline.
- A new commit lands after Step 1 that introduces stock Tailwind colors by habit.

**Mitigation:**

- Before committing Step 1, grep the canonical for default Tailwind color classes: `bg-blue-`, `bg-gray-`, `bg-slate-`, `bg-stone-`, `bg-zinc-`, `text-blue-`, `text-gray-`, `text-slate-`, `border-gray-`, `border-slate-`. Every match is a token-drift risk. Replace with the token-system equivalents before the gate.
- Add a lint rule or a Vitest test that scans `src/**/*.tsx` for stock Tailwind color prefixes. Fail the build on any match outside whitelisted exceptions.
- PR review rule: no commit after Step 1 may introduce a stock Tailwind color class without explicit design sign-off.

### 5.2 Over-copying sandbox code

**Symptom:** a file appears in the canonical repo with the header comment "Extracted from the Physical Count form page…" or imports from `@/lib/review-mode/*` or `@/lib/auth/fake-auth`. PR diff includes files named `useHasRole.ts`, `SessionProvider.tsx`, `fake-auth.ts`, `ReviewModePanel.tsx`, or similar.

**Likely cause:** someone read `window2-design-transfer.md`, found the component mapping table, and interpreted "Copy" as "Ctrl-C / Ctrl-V the .tsx file from the sandbox." The recommendation meant **copy the visual contract**, not the file.

**Mitigation:**

- Hard PR rule: zero file imports from `PRODUCTION/portal/`, `window2-portal-sandbox/`, or any path containing "window2". Enforce in CI with a simple grep.
- For every "Copy" recommendation in §2 of the transfer doc, the implementation approach is: read the sandbox component as a reference in a different window, **type** the canonical version from scratch, using the canonical's primitives. The visual match is the goal; the code is not shared.
- No symlinks, no shared npm packages, no cross-repo imports.
- If an engineer insists on literal reuse, that is a merge-plan conversation, not a Step 4 action.

### 5.3 Primitive mismatch

**Symptom:** two button styles coexist in one screen. Or a new class-based `.btn` button sits next to an existing `<Button variant="default">`. Or a custom `<div className="card">…</div>` is rendered inside a Radix `<Card>`.

**Likely cause:** someone ported Window 2 `.btn`/`.input`/`.card` component classes into the canonical's `globals.css` alongside the existing Radix primitives. Both now exist. Developers pick whichever they remember.

**Mitigation:**

- Step 1's rule: **only add tokens and utility classes** to `globals.css`. Never add `.btn`, `.input`, `.card`, `.table-base`, `.chip` as component classes in the canonical. These belong exclusively to Window 2.
- Code review check: any new CSS component class in the canonical's `globals.css` is a red flag. Push back unless it's a well-argued canonical-specific addition.
- If the canonical's Radix primitives are insufficient for a pattern, the answer is "add a new Radix variant," not "add a class-based primitive."

### 5.4 Auth / dev-affordance leakage

**Symptom:** a FAKE SESSION pill appears in the canonical top bar. Or a "Review mode" button appears. Or the code imports `useHasRole` from any non-canonical module. Or a `gt.fakeauth.v1` localStorage key exists.

**Likely cause:** someone adapted `TopBar.tsx` from the sandbox verbatim instead of rebuilding it on the canonical's `AuthProvider` + `RoleSwitcher`.

**Mitigation:**

- PR rule: the canonical's `src/shared/layout/TopBar.tsx` may **only** use `useAuth()` from `src/shared/auth-context/` and render `RoleSwitcher` from the same path for session affordances.
- No string `"FAKE SESSION"` allowed in canonical source. Fail the build.
- No import from `src/lib/auth/fake-auth` or `src/lib/review-mode/*`. These paths do not exist in the canonical and must not be created.
- Sandbox's "warning-bordered ticket" visual style is safe to borrow for other warnings (maintenance banner, integration failure state), but the label "FAKE SESSION" and the review-mode button never land.

### 5.5 False "feature readiness" signal

**Symptom:** the canonical portal's dashboard looks polished with real tiles and real numbers. A stakeholder sees it and concludes Tranche 3 ("Core Forms") or Tranche 5 ("Planning Engine") is complete. Actual backend work has not progressed. Expectations drift.

**Likely cause:** visual lift outran backend contract. The design system is powerful enough to make an empty shell look production-grade. Someone populates it with fixture data that feels real, and no one adds a clear "Tranche N Step M · Dk scaffold" marker.

**Mitigation:**

- Keep a stage indicator visible in the canonical's top bar at all times — in the spot where the Window 2 sandbox has its "shell build" chip. For the canonical this reads `Tranche 1 · Step 2 · D3 — shared primitives + mocked API` (or the current value). Update it on every Tranche step commit.
- On any fixture-driven tile or list, add a muted "fixture" chip in the corner that disappears once real read models are wired. This is cheap and immunizes stakeholders against visual illusion.
- Never apply Tier B or Tier C patterns to screens whose backend contracts are not yet accepted. The Step 5 gate enforces this.

### 5.6 Layout mismatch

**Symptom:** the canonical's `AppShell` uses different max-width / side nav width / sticky offsets / page padding than Window 2 specifies. A new Tier A pattern composed under Window 2 rules looks off inside the canonical's shell — elements don't align, the grid breathes differently, sticky offsets fight each other.

**Likely cause:** the canonical has its own `AppShell`, `TopBar`, `Sidebar` with pre-existing layout decisions that predate this adoption brief. Step 4 patterns assume §1.8 page-shell rules (1440px max, 232px side nav, top-[88px] sticky offset, 40px gap). If the canonical doesn't match, patterns break.

**Mitigation:**

- Step 4's first action on `AppShell.tsx` is to **reconcile layout to §1.8 exactly**. Audit: max-width, side nav width, top bar height, sticky offsets, page padding. Align.
- If the canonical has a legitimate reason to deviate (e.g. a requirement for a different max-width), document the deviation in a `canonical-layout-deviations.md` file in the canonical repo. Every pattern that assumes the shell dimensions must account for the deviation explicitly — not silently.
- Test: composite a known Tier A pattern (admin master-maintenance split view) inside the new shell and visually verify the rhythm works. If it doesn't, you have layout drift and it must be fixed before more patterns land.

---

## 6. Acceptance gate

The exact review checklist for declaring: **"The canonical portal has successfully adopted the Window 2 design language."**

This is a **design-adoption gate**. It does **not** imply feature completeness, backend contracts, workflow readiness, or merge resolution.

### 6.1 Token compliance

- [ ] `portal/tailwind.config.ts` contains the Window 2 color palette with HSL values within 1% of §1.1 specifications.
- [ ] `portal/tailwind.config.ts` contains the 11-step font-size scale from §1.2 with matching sizes, line-heights, and letter-spacings.
- [ ] `portal/tailwind.config.ts` contains the 5 radius tokens from §1.4 with `md`/default = 6px.
- [ ] `portal/tailwind.config.ts` contains the 5 shadow tokens from §1.4.
- [ ] `portal/src/app/globals.css` applies the dot-grid body background from §1.1.
- [ ] `portal/src/app/globals.css` sets tabular numerics globally.
- [ ] Grep check: `rg "bg-blue-|bg-slate-|text-blue-|text-slate-|border-gray-" portal/src/` returns zero matches outside of documented exceptions.

### 6.2 Typography compliance

- [ ] `portal/src/app/layout.tsx` imports `Public_Sans` and `IBM_Plex_Mono` from `next/font/google`.
- [ ] Both fonts are applied as CSS variables on `<html>`.
- [ ] Body font-family resolves to Public Sans in DevTools.
- [ ] Inputs of type number render with tabular digits.
- [ ] No other sans or mono font families are imported.

### 6.3 Primitive compliance

- [ ] Every file in `portal/src/components/ui/` has been updated to render against the new tokens.
- [ ] The canonical's existing test suite for primitives (`StatusBadge.test`, `TextInput.test`, `ConfirmDialog.test`, `Field.test`, `PermissionGuard.test`, `AuthProvider.test`, `useHealth.test`, `errors.test`, `stub.test`, etc.) all pass unchanged or with only class-string assertions updated.
- [ ] No primitive file imports `lucide-react` unless it already did at D2.
- [ ] No primitive file gains a new variant.

### 6.4 Tier A pattern adoption

- [ ] D4 Master Maintenance screens exist in the canonical and compose the admin split-view + table chrome + detail pane patterns from §4 of this brief.
- [ ] The admin table chrome matches Window 2's rhythm: uppercase `sops`-tracked headers, 2.5py row padding, `border/40` separators, `bg-subtle/60` hover, `bg-accent-soft/70` selected.
- [ ] The admin detail pane composes `Card` + `CardHeader` with eyebrow/title/description/actions.
- [ ] The admin detail pane uses a sticky form action footer at the bottom.

### 6.5 Contamination check

- [ ] `rg "from.*window2|from.*PRODUCTION/portal|from.*fake-auth|from.*review-mode|FAKE SESSION|ReviewModePanel|useHasRole|SessionProvider|GenericIdbRepo" portal/src/` returns **zero** matches.
- [ ] No file under `portal/src/` has the name `fake-auth.ts`, `session-provider.tsx`, `role-gate.tsx`, `review-mode-panel.tsx`, `state-preview-chip.tsx`, or any obvious sandbox copy.
- [ ] No file in `portal/src/lib/fixtures/`. (The canonical uses `portal/fixtures/masters/*.json`, a different convention.)

### 6.6 Gate meta

- [ ] Canonical `npm run typecheck` exits 0.
- [ ] Canonical `npm run test` passes.
- [ ] Canonical `npm run build` exits 0.
- [ ] Canonical's own Playwright tests (if any exist by this point) pass.
- [ ] Tom does a visual walkthrough: dashboard (or placeholder), one admin screen, one form screen. Side-by-side with screenshots of the Window 2 sandbox. **Visual parity is the success criterion.**
- [ ] A stage chip in the canonical top bar still reads the current Tranche/Step state (e.g., `Tranche 1 · Step 2 · D4`), not "production" or "ready."

### 6.7 What the gate does NOT check

- ❌ Feature completeness (Tranche 3 forms, Tranche 4 planning, Tranche 5 engine).
- ❌ Real backend contracts wired.
- ❌ Supabase session integration.
- ❌ Ledger posting or projection reads.
- ❌ LionWheel, Shopify, or Green Invoice integration live.
- ❌ Dark-theme parity.
- ❌ A merge between the Window 2 sandbox and the canonical portal.
- ❌ Retirement of the Window 2 sandbox.

Passing this gate means the canonical portal **looks right**. It does not mean it **is done**.

---

## 7. Freeze reminder

Window 2 stays frozen after this brief.

- No more sandbox design work without a specific Tom-requested pass.
- No code transfer from `PRODUCTION/portal/` or `window2-portal-sandbox/` into the canonical repo.
- No canonical edits yet as a result of this brief. **This brief is planning-only.** The first canonical commit based on this brief happens only when Tom explicitly approves adoption work.
- The Window 2 sandbox continues to pass the four gates on demand (`tsc --noEmit`, `next build`, `vitest run`, `playwright test`). That's the only work that may happen in Window 2 without breaking the freeze.
- The design transfer package (`window2-design-transfer.md`) and this adoption brief are both living reference documents. Update them if their underlying assumptions drift — but they are not themselves code, and updating them does not break the freeze.

---

_End of canonical adoption brief. No code written. No canonical edits made. Ready for Tom's decision on when — and whether — Step 1 begins._
