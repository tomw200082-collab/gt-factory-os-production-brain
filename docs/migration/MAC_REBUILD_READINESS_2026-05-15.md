# GT Factory OS — Mac Rebuild Readiness

> **Date:** 2026-05-15
> **Purpose:** Everything needed to rebuild the full GT Factory OS working environment on a new MacBook from GitHub + documented steps + manually-restored secrets.
> **Verdict:** **Mac-ready — CONDITIONAL** (the only conditions are human steps: install tooling, restore `.env` files, run one real work session). No code blockers.

This document is the authoritative rebuild reference. Its companion, `MACBOOK_FIRST_DAY_CHECKLIST_2026-05-15.md`, is a plain-language step list for Tom.

---

## 0. Summary

| Repo | GitHub | First-Mac branch | Rebuildable from GitHub today? | Readiness |
|---|---|---|---|---|
| PRODUCTION brain | `gt-factory-os-production-brain` | `planning-masterplan-2026-05-08` | Yes | 9 / 10 |
| Backend | `gt-factory-os` | `main` | Yes | 8 / 10 |
| Portal | `gt-factory-os-portal` | `main` | Yes | 9 / 10 |
| LionWheel route agent | `gt-lionwheel-daily-route-agent` | `main` | Yes | 10 / 10 |

All four repos are fully pushed. All local WIP was committed and pushed during the 2026-05-15 migration session. **Nothing important remains only on the Windows machine** except the secret `.env` files (by design — see §6) and one re-downloadable PDF cache.

---

## 1. PRODUCTION brain

- **GitHub:** https://github.com/tomw200082-collab/gt-factory-os-production-brain
- **Clone:**
  ```
  git clone https://github.com/tomw200082-collab/gt-factory-os-production-brain.git
  ```
- **Branch to check out first:** `planning-masterplan-2026-05-08`
  ```
  git checkout planning-masterplan-2026-05-08
  ```
  > This is the live working branch. `main` is intentionally far behind (`258ac3c`) and must **not** be used as the working branch. Do not merge `planning-masterplan-2026-05-08` into `main` without a deliberate decision.
- **Important extra branches:** `main` (historical baseline), `run-g-final-brain-closure` (historical). The `worktree-agent-*` local branches are throwaway agent artifacts — ignore them; they will not exist after a fresh clone.
- **Install / build / test:** none. This repo is pure governance/docs/state (Markdown + JSON + a few helper scripts). No Node, no Python, no build step.
- **First run:** open the folder in Claude Code / VS Code. `CLAUDE.md` is the boot kernel.
- **Env / secrets:** none.
- **Lives outside git:** nothing critical. Note this repo currently sits **inside Dropbox** (`GTeveryday Dropbox/.../PRODUCTION`). On the Mac you can either keep it in Dropbox or clone it fresh to `~/Projects/`. GitHub is now the source of truth either way — a fresh clone is cleaner and avoids the spaces-in-path friction.
- **Open PRs / WIP:** none open. All session WIP committed + pushed.
- **Safe to ignore:** `worktree-agent-*` branches, `archive/**` (historical only).
- **Not safe to lose:** the whole repo — it is the system's brain. Fully on GitHub now.
- **Readiness:** 9 / 10.

---

## 2. Backend — `gt-factory-os`

- **GitHub:** https://github.com/tomw200082-collab/gt-factory-os
- **Clone:**
  ```
  git clone https://github.com/tomw200082-collab/gt-factory-os.git
  ```
- **Branch to check out first:** `main`
- **This repo has TWO npm projects:**
  - **root** — database tooling: migrations, imports, pgTAP tests.
  - **`api/`** — the Fastify HTTP server (the actual backend service).
- **Install:**
  ```
  npm install            # in repo root
  cd api && npm install  # in api/
  ```
- **Tooling required:** Node 20+, PostgreSQL 16 client tools (`psql`), and `pg_prove` (pgTAP test runner) if you intend to run DB tests.
- **Typecheck:**
  ```
  npm run typecheck          # root
  cd api && npm run typecheck # api/
  ```
- **Build:** none — both projects run via `tsx` (no compile step).
- **Run the API server:**
  ```
  cd api && npm start        # tsx start-server.ts ; health check at /health
  ```
- **Tests:**
  - `cd api && npm test` — Node test runner (`tsx --test`).
  - `npm run db:test:all` — pgTAP tests; **needs a live database** and is not part of routine rebuild verification.
- **Env / secrets:** root `.env` — see §6 for the full required variable list. The `api/` server reads the same root `.env`.
- **Important extra branches to fetch (all pushed to GitHub):**
  - `backup/gi-supplier-price-analysis-2026-05-15` — preserved Green Invoice price-analysis WIP.
  - `backup/master-data-fix-wave-1-wip-2026-05-15` — preserved master-data reconciliation WIP.
  - `backup/perfect-flow-wip-2026-05-15` — preserved stock-event test snapshots.
  - `backup/chore-structure-consolidation-2026-05-15` — preserved orphaned branch (remote was deleted).
  - `backup/run-d-b3-bom-shadow-verification-2026-05-15` — preserved orphaned branch.
  - `feat/production-plan-notes` and other active feature branches — all pushed.
- **Lives outside git (must restore / decide manually):**
  - **`.env`** — real integration secrets. Restore from password manager. See §6.
  - **`scripts/gi_pdfs/`** — 122 supplier-invoice PDFs (~17.5 MB). **Intentionally not committed.** Re-downloadable on the Mac via `npx tsx scripts/gi_download_pdfs.ts`, or copy the folder manually from Windows before wiping it if you want the exact files.
  - Git **worktrees** (`gt-factory-os.worktrees/*`) do not transfer. Recreate with `git worktree add` only if needed; every worktree branch is already on GitHub.
- **Open PRs:** none.
- **Known non-blocking issues (pre-existing, not migration regressions):**
  - Root typecheck: 1 error in `scripts/archive/_w1_lw_live_exercise.ts` (stale module path in an archived one-off script).
  - `api/` typecheck: 6 errors, all in `api/test/shopify_adapter.test.ts` (test-file type-argument mismatches). The `api/` source itself compiles; the server runs.
- **Not safe to lose:** all branches (now on GitHub), `.env` (local only — restore manually).
- **Readiness:** 8 / 10 (−1 pre-existing typecheck noise; −1 needs `psql`/`pg_prove` tooling installed for DB work).

---

## 3. Portal — `gt-factory-os-portal`

- **GitHub:** https://github.com/tomw200082-collab/gt-factory-os-portal
- **Clone:**
  ```
  git clone https://github.com/tomw200082-collab/gt-factory-os-portal.git
  ```
  > The Windows working folder is named `window2-portal-sandbox` — that name is historical. This repo **is** the canonical production portal. On the Mac, clone it as `gt-factory-os-portal` (its real name).
- **Branch to check out first:** `main` (now at `1faf657`).
  > The Windows working branch was `redesign/production-simulation`; that is just `main` + one committed tsconfig cleanup and is preserved on GitHub. Start clean on `main`.
- **Install:**
  ```
  npm install
  ```
- **Tooling required:** Node 20+ (22 is fine).
- **Commands:**
  ```
  npm run typecheck   # tsc --noEmit — verified clean
  npm run build       # next build — verified clean (89 routes)
  npm run test        # vitest
  npm run lint:urls   # route-group leak guard
  npm run dev         # local dev server
  ```
- **Env / secrets:** `.env.local` — see §6.
- **Important extra branches:** many feature branches, all pushed. Notably `fix/inventory-flow-display-2026-05-14` (the open PR branch — see below).
- **Lives outside git:** `.env.local` (restore manually — see §6). Git worktrees do not transfer.
- **Open PRs:** **PR #21** — "feat(inventory-flow): DayPopover without-production row + chip tooltip clarity" (branch `fix/inventory-flow-display-2026-05-14`). **Left OPEN intentionally** — it is a product UX change, out of scope for the migration. Review and merge it normally after the move.
- **Known non-blocking issues:** `npm run test` (vitest) reports 240 passed / 275 (35 pre-existing baseline failures, zero regression — matches the documented baseline). Build and typecheck are clean.
- **Not safe to lose:** all branches (on GitHub), `.env.local` (local only).
- **Readiness:** 9 / 10.

---

## 4. LionWheel daily route agent — `gt-lionwheel-daily-route-agent`

- **GitHub:** https://github.com/tomw200082-collab/gt-lionwheel-daily-route-agent
- **Clone:**
  ```
  git clone https://github.com/tomw200082-collab/gt-lionwheel-daily-route-agent.git
  ```
- **Branch to check out first:** `main`
- **Install (Python 3.10+; 3.13 verified):**
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]"     # ".[dev]" includes pytest + reportlab; plain ".[" for runtime only
  ```
- **Test:**
  ```
  python -m pytest            # verified: 117 passed
  ```
- **Run:**
  ```
  python -m src.run --date YYYY-MM-DD --validate-inputs-only --strict
  python -m src.run --date YYYY-MM-DD
  ```
- **Env / secrets:** **optional.** The agent runs file-based — Tom drops LionWheel export JSON into `data/inputs/`. A `.env` with `LIONWHEEL_API_KEY` (or `LIONWHEEL_GT`) is only needed for the optional live-fetch path. There is no `.env` on the Windows machine today, confirming normal operation needs none.
- **Lives outside git:** `data/runs/`, `data/inbox/*`, `data/debug/` are gitignored — these are operational run history, local-only, not critical. The important config (`data/sku_map.json`, `data/area_map.yaml`, sample inputs) **is** tracked in git.
- **Open PRs:** none.
- **Not safe to lose:** the repo (on GitHub). Run history in `data/runs/` is nice-to-keep but not essential.
- **Readiness:** 10 / 10.

---

## 5. Tooling to install on the new Mac

| Tool | Why | Install |
|---|---|---|
| Homebrew | macOS package manager | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Git | version control | `brew install git` |
| Node 20+ | backend `api/`, portal | `brew install node` |
| Python 3.11+ | LionWheel agent | `brew install python` |
| PostgreSQL 16 client | backend DB work (`psql`) | `brew install postgresql@16` |
| pgTAP / `pg_prove` | backend DB tests (optional) | `brew install pgtap` then `cpan TAP::Harness` if needed |
| VS Code | editor | `brew install --cask visual-studio-code` |
| Claude Code | the agent CLI | per Anthropic install docs |
| GitHub CLI (`gh`) | PR/branch operations | `brew install gh` then `gh auth login` |

---

## 6. Secrets / env files — restore manually (NEVER in git)

These files contain real credentials. They are correctly gitignored and were **not** committed. Recreate them on the Mac by copying values from your password manager. The variable **names** below are the complete required set; **values** must be restored by hand.

### Backend — `gt-factory-os/.env`
```
SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_REGION
DATABASE_URL, DATABASE_URL_POOLED, DATABASE_URL_SHADOW
FIXTURES_DIR, IMPORT_BATCH_SIZE          (config, not secret)
LIONWHEEL_ENV, LIONWHEEL_BASE_URL, LIONWHEEL_API_KEY, LIONWHEEL_COMPANY_ID
GREENINVOICE_ENV, GREENINVOICE_API_BASE_URL, GREENINVOICE_KEY_ID, GREENINVOICE_SECRET
SHOPIFY_ENV, SHOPIFY_STORE_DOMAIN, SHOPIFY_ADMIN_API_TOKEN
RESEND_API_KEY
SUPABASE_MGMT_PAT, RAILWAY_TOKEN, VERCEL_TOKEN   (deploy/management tokens — optional locally)
```
> The committed `gt-factory-os/.env.example` is **stale** — it documents only the Supabase/Postgres block. The list above is authoritative. (The `.env.example` file could not be updated automatically because a safety hook blocks all `.env*` writes; update it by hand if desired.)

### Portal — `gt-factory-os-portal/.env.local`
```
NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
NEXT_PUBLIC_API_BASE, API_BASE
NEXT_PUBLIC_ENABLE_DEV_SHIM_AUTH
```

### LionWheel agent — `gt-lionwheel-daily-route-agent/.env` (optional)
```
LIONWHEEL_API_KEY        (or LIONWHEEL_GT — only for the optional live-fetch path)
```

### PRODUCTION brain
No secrets.

**Tip:** before wiping Windows, copy all three `.env` files to a secure location (password manager attachment or encrypted drive) — they are the one thing GitHub does not hold.

---

## 7. What is NOT on GitHub (manual-copy or accept-loss list)

| Item | Location | Action |
|---|---|---|
| Backend `.env` | `gt-factory-os/.env` | **Restore manually** (secrets) |
| Portal `.env.local` | `gt-factory-os-portal/.env.local` | **Restore manually** (secrets) |
| LionWheel `.env` | `gt-lionwheel-daily-route-agent/.env` | Only if live-fetch is used; optional |
| `scripts/gi_pdfs/` | backend | Re-downloadable; copy manually only if exact files wanted |
| LionWheel `data/runs/` history | LionWheel agent | Operational history; copy if you want it, otherwise accept loss |
| Git worktrees | both Node repos | Do not transfer; recreate on demand — all branches are on GitHub |
| Local Claude Code session state | machine-level | Not needed; sessions are stateless across machines |

---

## 8. Migration readiness verdict

**Mac-ready: CONDITIONAL.** There are no code or repository blockers. Every repo clones, installs, and verifies. The remaining work is purely human:

1. Install the tooling in §5.
2. Restore the three `.env` files in §6.
3. Clone the four repos and check out the branches in §0.
4. Run the verification commands and confirm them green.
5. Complete one real work session before retiring the Windows machine.

See `MACBOOK_FIRST_DAY_CHECKLIST_2026-05-15.md` for the step-by-step version.
