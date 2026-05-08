# GT Factory OS — Workspace Map

**Two active boxes. One home for everything.**

---

## BOX 1 — PRODUCTION/ (this folder)
**AI brain: governance, state, execution policy.**

| File | Purpose | Authoritative on |
|------|---------|-----------------|
| `CLAUDE.md` | Durable contract | Locked decisions, architecture, non-negotiables |
| `CURRENT_STATE.md` | Live runtime status | Gate status, completion %, critical path, open gaps |
| `EXECUTION_POLICY.md` | Operational governance | Window ownership, lane policy, mode amendments |
| `ACTIVE_NOW.md` | Ephemeral operator context | Nothing — defers to CURRENT_STATE.md if stale |
| `.claude/state/runtime_ready.json` | Harness signals | RUNTIME_READY events (authoritative) |
| `.claude/state/active_mode.json` | W2 mode | Mode A / Mode B (authoritative) |

**Never in Box 1:** source code, npm packages, contract specs, runbooks, active logic of any kind.

---

## BOX 2 — Canonical Runtime (two repos, one box)

### Backend — `C:/Users/tomw2/Projects/gt-factory-os/`
Fastify API · Postgres migrations · pgTAP tests · docs · scripts  
Railway deploy. Branches tracked at `github.com/[canonical-backend-remote]`.

### Frontend (portal) — `github.com/tomw200082-collab/gt-factory-os-portal`
Local working copy: `C:/Users/tomw2/Projects/window2-portal-sandbox/`  
*(folder name is historical — "sandbox" is a misnomer; this is the live production portal)*  
68 pages · Next.js 15 · Supabase live · Vercel deploy at `gt-factory-os-portal.vercel.app`  
`@claude` on GitHub → targets `tomw200082-collab/gt-factory-os-portal`  
Local Claude Code work → `window2-portal-sandbox/` — must push/pull with GitHub remote.

**Pre-execution portal sync checks (run before any portal work):**
```bash
git fetch --all --prune && git status --short && git log --oneline --decorate -5
git branch -vv && git worktree list && git remote -v
```

**Note:** `gt-factory-os/portal/` is a D1–D4 reference scaffold only — not the production portal.  
**Note:** `PRODUCTION/portal/` is archived — do not use.

---

## Other active project (separate, not part of this system)
`C:/Users/tomw2/Projects/gt-lionwheel-daily-route-agent/` — LionWheel route builder agent.

---

## Archive
`PRODUCTION/archive/` — completed window deliverables, frozen sandboxes, one-off scripts, and migrated originals.  
Archive contents are read-only historical reference. Do not import, execute, or promote code from archive.

Original supplier invoice folder and migrated spec shells were archived after verified migration (2026-05-08). Active operational invoice files now live under `PRODUCTION/data/invoices/suppliers/`. Canonical specs now live under `gt-factory-os/docs/`.

---

## Operational Reference Files
Operational reference files live under `PRODUCTION/data/`. They are not canonical runtime code. Runtime truth remains in `gt-factory-os` and `gt-factory-os-portal`.  
Supplier invoice scans live under `PRODUCTION/data/invoices/suppliers/` (`unprocessed/` = awaiting entry; `processed/` = confirmed in system).
