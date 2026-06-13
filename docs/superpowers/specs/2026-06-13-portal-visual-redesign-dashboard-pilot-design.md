# Portal Visual Redesign — Dashboard Pilot (Design Spec)

> **Date:** 2026-06-13 · **Owner:** Tom · **Status:** APPROVED for pilot build (direction + approach locked this session) · **Author:** Claude (brainstorming session)
> **Scope:** ONE hero screen (Dashboard) as an isolated, reversible pilot. No global design change until Tom approves the result.

---

## 1. Goal

Dramatically improve the portal's visual design — **vivid, premium, "glowing"** — and prove it on a single hero screen before any system-wide change. This is a deliberate **reversal of the locked "Operational Precision" doctrine** (restrained, not-poster-bright, hairline shadows), made knowingly by Tom, with Tom as the single approval gate for any global token change.

**Success = Tom looks at a real, clickable reskinned Dashboard and says "yes, roll this out"** — with zero risk taken on the other 69 screens to get there.

## 2. Decisions locked (this session)

| Decision | Choice |
|---|---|
| Direction | **Pilot one hero screen first**, then decide rollout breadth |
| Pilot screen | **Dashboard** (`/dashboard`) — first-seen daily, flattest surface (most upside), low legibility risk |
| Approach | **A — isolated `/dashboard/v3` + scoped token override**; zero edits to locked global files until promotion |
| Tool stack | Stitch (wired) + v0 + 21st.dev Magic + tweakcn + chrome-devtools/Playwright (decided by Claude per Tom's "decide for me") |

## 3. Why the portal is already a system (context)

The portal runs a mature, token-driven design system ("Operational Precision"): warm-bone canvas, single petrol-teal accent (`--accent: 186 42% 24%`), muted editorial semantics, 6px radius, **near-invisible 4–8% hairline shadows**, dense 14px Public Sans / IBM Plex Mono, tabular numerals. It is **not** plain shadcn (no shadcn installed). ~90% of 70 screens are repainted by changing `:root` CSS variables + shadow/gradient tokens + ~5 shared primitives (`.btn`, `.card`, `SectionCard`, `WorkflowHeader`, `Badge`).

Locked, Tom-gated files (NOT touched during the pilot):
`src/app/globals.css` · `tailwind.config.ts` · `docs/portal_ux_standard.md` · `docs/portal_language_direction_audit.md`.

## 4. Architecture — the safe pilot (Approach A)

- **New route:** `src/app/(shared)/dashboard/v3/page.tsx` (mirrors existing `dashboard/v2`). Reuses the **real** data components/queries (KPI tiles, stock-health donut, critical-today card) — identical data flow, no backend/contract change.
- **Scoped theme override:** a new file in `src/**` (e.g. `src/app/(shared)/dashboard/v3/_theme/reskin.css`) defining a scope class:
  ```css
  .reskin-scope { --accent: <new>; --accent-hover: <new>; --bg: <new>; /* glow + gradient custom props */ }
  ```
  The route subtree is wrapped in `<div className="reskin-scope">`. Tailwind utilities (`bg-accent`, etc.) and the component classes (`.btn`, `.card`) reference `hsl(var(--…))`, so they **inherit the scoped values within that subtree only**. The global `:root` is untouched.
- **New glow/gradient/glass effects** are authored as new component-level classes / inline styles / new components **inside `src/**`** (executor-allowed) — never added to `globals.css` or `tailwind.config.ts`.
- **Reversibility:** discard = delete the `v3` route + `_theme` file. Nothing global ever changed.

## 5. Visual direction — "Aurora Cockpit" (working name)

Concrete target to react to (concepts shown before build): deep graphite cockpit canvas; vivid **multi-stop accent** (teal → electric blue → violet); **glowing KPI tiles** with soft color bloom; gradient hero band; glassmorphic cards with subtle inner glow; animated count-up numerals; tasteful motion that **respects `prefers-reduced-motion`**. Candidate token values are designed in tweakcn and shown as 2–3 generated concepts for Tom to pick the mood — not chosen in prose here.

## 6. The reusable pipeline ("connect Stitch safely" — the answer)

This is the repeatable loop (later packageable as a `/portal-redesign` skill):

1. **Concept** — Stitch `generate_screen_from_text` (+ v0) → 2–3 moods → **Tom picks**.
2. **Tokens** — tweakcn → candidate `:root` variables → scoped into `reskin.css`.
3. **Build** — author `/dashboard/v3` in `src/**` (apply `frontend-design` skill for non-generic quality; 21st.dev Magic for component polish).
4. **Verify** — Playwright + chrome-devtools: before/after screenshots, Lighthouse (perf + a11y), WCAG-AA contrast, `prefers-reduced-motion`.
5. **UX gate** — `/design-system-check` + `/screen-scorecard` + `/ux-release-gate` (zero-P0 to ship).
6. **Review** — Tom views the live preview (Vercel preview deploy or local dev-shim).
7. **Promote (Tom-gated)** — only after Tom approves: move the validated tokens into `globals.css` / `tailwind.config.ts` (the ONE human checkpoint), then roll out screen-by-screen, each pass repeating steps 3–6.

## 7. Safety / governance

- **No locked-file edits during the pilot** — all overrides scoped in `src/**`. The global doctrine is revised only at step 7, only with Tom's explicit approval (satisfies the token-authorization gate; portal-production-executor cannot author those files).
- **`portal_ux_standard.md` honored:** English/LTR, names-not-IDs, one-primary-state hygiene, status-chip vocabulary, **color/glow is additive — never the sole signal**. If the bold direction conflicts with a standard clause, revising that clause is a separate Tom-gated proposal routed through `ux-content-state-designer`.
- **Git/deploy:** pilot built on a branch, **preview-deployed only** (redesign/* + feat/* are preview on Vercel). Promotion to `main` (production) only after Tom approval. Hard stops respected (no secrets in diffs, no force-push, no unrelated-runtime merges).
- **Data integrity:** pilot touches **zero** data, contracts, or integrations — it is a read-only reskin of existing components.

## 8. Error handling / risk

| Risk | Mitigation |
|---|---|
| Legibility loss from glow/gradient on dense data | Pilot is Dashboard (KPI/cards, low risk); dense grids (Inventory Flow/Forecast) handled later with restraint, separately gated |
| Performance cost of blur/glow/glass | Lighthouse gate in step 4; cap blur layers; prefer box-shadow glow over heavy backdrop-blur where possible |
| Motion accessibility | All animation behind `prefers-reduced-motion`; verified in step 4 |
| Doctrine reversal regret | Pilot is isolated + reversible; global change deferred to step 7 behind Tom approval |

## 9. Testing

- `npm run typecheck` + `lint` + `build` green.
- Playwright visual before/after on `/dashboard` vs `/dashboard/v3`.
- Lighthouse (perf + a11y) and WCAG-AA contrast on the new skin.
- Manual review of all four dashboard states (loading / empty / error / loaded) under the new skin.

## 10. Out of scope (pilot)

- Global token change (deferred to step 7 / promotion).
- The other 69 screens (rolled out only after Tom approves the pilot).
- Any backend / data / contract / integration change (none).

## 11. Open decision points

- **Concept mood** — chosen after Stitch/v0 generation (step 1).
- **API keys** — v0 (needs a paid v0 plan) + 21st.dev (free tier). Pilot can begin without them (Stitch + tweakcn + screenshots) and fold them in on arrival.
- **Rollout breadth** — decided only after Tom sees the pilot.
