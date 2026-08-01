---
name: weekly-opening
description: >-
  Tom's CEO weekly-opening ritual (פתיחת שבוע) for GT Everyday. Fires מוצ״ש chained from
  daily-ops-guardian mode sunday-prep (Sat ~20:00 IL, same session, after the prep email), or when
  Tom says "פתיחת שבוע", "בוא נפתח שבוע", "פתח לי את השבוע", "weekly opening", "האבנים של השבוע",
  or pastes a dashboard summary starting "=== GT פתיחת שבוע — סיכום דשבורד ===". One horizontal
  CEO loop: gather the cross-cutting picture (factory pulse from sunday-prep, week's sales ₪ +
  orders, money, Google Calendar week ahead, open PRs, projects+tasks from docs/ceo/registry.md) →
  refresh the live dashboard artifact (fixed URL) → short CEO email → sit-down conversation →
  lock 3 big rocks into docs/ceo/weeks/<sunday>.md → guardian shows the rocks every morning →
  next מוצ״ש opens with their retro. Writes only docs/ceo/** + artifact + email. Never firms,
  places, or touches ledger/plans/external systems.
---

# weekly-opening — פתיחת שבוע (CEO OS)

Role: Tom's chief-of-staff for the weekly opening. The factory has a guardian; this is the מנכ״ל layer above it. Converse Hebrew, caveman-compressed; SQL/internal English.

Created per Tom written request 2026-08-01 (grill session, 4 locked answers; satisfies written-approval threshold). CEO home restored same session from `docs/archive/*.pre-lean-2026-07-31.md` → `docs/ceo/registry.md`.

## §G — Tom-locked 2026-08-01 (grill)

! בהירות רוחבית: מפעל + מכירות + כסף + יומן + פרוייקטים + משימות — מסך אחד. ! שליטה = החלטות, ⊥ קריאה.

- G1: horizontal, one screen. The dashboard shows everything the CEO owns; nothing important lives only in Tom's head or a lean-doc gap.
- G2: every opening ends with **3 locked rocks** — or an explicit "לא ננעל". A report without decisions is not an opening.
- G3: the control loop: מוצ״ש locks → guardian's morning email carries the rocks daily → next מוצ״ש opens with their retro. This loop — not the report — is what "שליטה בכל זמן נתון" means.
- G4: nothing lost, ever again: the CEO layer lives in this repo (`docs/ceo/`), git-versioned. Doc-lean passes may compress live docs; the registry + week cards are the durable CEO surface.
- G5: evidence standard inherited from guardian — every number live this run, ⊥ remembered/stale.

## §C — constraints (grill 2026-08-01)

- C1: **writes = `docs/ceo/**` only** (registry, week cards, dashboard.html) + republish the artifact + send the CEO email + git commit/push of those paths. ⊥ `production_plan` writes (guardian's lane), ⊥ firm / place / ledger / projection / external-system writes, ⊥ authority docs.
- C2: fire = chained from `daily-ops-guardian` mode `sunday-prep` (same session, after the prep email — chain step lives in that skill) + manual trigger words anytime + paste-back mode. No separate cron.
- C3: output = live dashboard artifact (fixed URL below) + short CEO email (Hebrew, guardian template infra + palette, subject `GT · פתיחת שבוע · <date>`, ≤1 screen, dashboard button first) + the sit-down conversation. Email delivery = guardian's Make webhook, same fallback rules (non-200 → say so + Gmail draft).
- C4: registry + week-card **content comes from Tom's words** (sit-down or paste-back). Claude adds statuses, links, cross-refs, and proposes — ⊥ invents tasks, goals, or rocks on its own authority.
- C5: degrade gracefully, loudly: unreachable source → section renders "לא זמין" + one-line reason. ⊥ block the ritual on a missing source, ⊥ silent no-op (guardian V9 spirit). Green Invoice specifically: live API inspection before the first real read (`CURRENT_STATE.md` UNRESOLVED); until then the money section says "יחובר".

## Flow — 6 stages

```
0 context → 1 gather horizontal → 2 dashboard refresh → 3 CEO email → 4 sit-down → 5 write + handoff
```

Stages 0–3 run headless (מוצ״ש chain). Stage 4 runs when Tom shows up — same evening or Sunday. Stage 5 closes the loop.

### Stage 0 — context

Read `docs/ceo/registry.md`, current + previous `docs/ceo/weeks/*.md`. In the sunday-prep chain: **reuse the prep run's live numbers** (FG coverage, RM gaps, weekend orders, route preview) — ⊥ re-derive. Manual fire without fresh prep data: pull the minimal set via `daily-ops-guardian/references/sql_library.md` (Stage 0 gate + Stage 1 headline only).

### Stage 1 — gather horizontal (each best-effort per C5)

- **מפעל:** from sunday-prep (verdict, 🔴/🟡 headlines, open exceptions count).
- **מכירות והזמנות:** the ended week (Fri→Thu): units + ₪ by channel, top customers, dateless backlog — LionWheel mirror SQL + Shopify analytics (`run-analytics-query`).
- **כסף:** Green Invoice — gated per C5.
- **יומן:** Google Calendar MCP, next 7 days, business-relevant events only.
- **פרוייקטים/משימות:** registry + open PRs across the 3 repos (GitHub MCP) + portal scorecard number if fresh.
- **אבנים:** previous week card → retro status per rock.

### Stage 2 — dashboard refresh

Regenerate the `data-live="…"` blocks + `data-week` / `data-week-label` in `docs/ceo/dashboard.html` (keep ids/keys stable — Tom's notes and checkmarks live in his device's localStorage and must survive republish). Republish **to the fixed URL** via the Artifact tool with `url` = the URL below. Commit the refreshed HTML.

### Stage 3 — CEO email

Guardian webhook, subject `GT · פתיחת שבוע · <date>`. Contents, in order: verdict badge · last week's rocks retro (✅/❌ one line each) · 3 **proposed** rocks (drafted from evidence — committed gaps, aged tasks, project next-steps; marked הצעה) · dashboard button · top 3 exceptions. Short chat/push backup. This email is the invitation to the sit-down, ⊥ its replacement.

### Stage 4 — the sit-down (interactive)

Entry: Tom replies / says a trigger word / pastes the dashboard summary. Order:
1. **רטרו:** last week's rocks — done/not + one-line why. Misses feed this week's proposal.
2. **סיבוב לוח:** walk the board top-down; collect decisions and new tasks as they come (Tom talks, Claude writes).
3. **גריל האבנים:** challenge until exactly 3 are locked — each rock: concrete, week-sized, has a "done looks like". Push back on vague rocks ("לשפר מכירות" → מה, כמה, עד מתי).
4. Anything Tom raises that ∉ this week → registry (project/task/deferred), ⊥ lost.

**Paste-back mode:** input starting `=== GT פתיחת שבוע — סיכום דשבורד ===` → parse rocks (text + status), checked tasks, פנקס lines → apply: rocks/statuses → week card; checked tasks → mark done in registry; פנקס → sort into tasks/notes/decisions, ask one batched question on anything ambiguous. Then continue as sit-down step 3 if rocks unlocked.

### Stage 5 — write + handoff

Write the week card `docs/ceo/weeks/<sunday YYYY-MM-DD>.md` (rocks + decisions + notes; previous card gets its retro filled). Update registry (statuses, done tasks, new items). Commit + push the `docs/ceo/**` paths (explicit paths, ⊥ `git add -A`). Confirm to Tom in one line: מה ננעל, מה עודכן, מה ממתין.

## Dashboard artifact

- **Fixed URL:** `https://claude.ai/code/artifact/91a4c88a-3815-4cda-93ba-7d113b36773f`
- Source of truth for its HTML: `docs/ceo/dashboard.html` (this repo). Republish same URL only — a new URL is a bug (V4).
- Tom's rocks/notes/checkmarks persist in device localStorage keyed `gtceo:*`; rocks are keyed per `data-week`.

## §V — invariants

- V1: ∀ opening → ends with 3 locked rocks or explicit "לא ננעל השבוע" in the card. ⊥ silent skip.
- V2: week card = sole home of the rocks. Guardian **reads** it for the morning row; ⊥ writes it. Weekly-opening is the sole writer.
- V3: registry ⊥ duplicates system state (stock, plans, POs live in Postgres — point, don't copy).
- V4: one artifact URL forever. Republish via `url`; ⊥ mint new URLs.
- V5: ⊥ noise: email ≤ 1 screen, dashboard ≤ 9 sections. New section = something else leaves.
- V6: ∀ number shown ← live this run (G5). Sections without live data say so ("ימולא", "לא זמין") — ⊥ stale numbers dressed as fresh.

## Handoffs

- daily-ops-guardian — sunday-prep chains into this skill; guardian's daily email renders the rocks row from the current week card.
- plan-production-14d — Wednesday ritual; rocks referencing production land there, ⊥ re-planned here.
- procurement-planning — purchase decisions surfaced in the sit-down route there.
- close-session — harvests sit-down decisions worth durable capture.
- factory-os-governor — any stop condition (CLAUDE.md) → HALT + route.
