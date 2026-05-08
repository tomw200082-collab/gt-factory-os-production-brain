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

### Phase 8 agents and commands (locations)

| Path | Owner |
|------|-------|
| `PRODUCTION/.claude/agents/factory-os-governor.md` | governance (Run A) |
| `PRODUCTION/.claude/agents/release-verifier.md` | pre-merge gate (Run A) |
| `PRODUCTION/.claude/agents/source-of-truth-auditor.md` | drift detection (Run A) |
| `PRODUCTION/.claude/agents/ux-flow-architect.md` | flow doctrine (Run A) |
| `PRODUCTION/.claude/agents/interaction-design-specialist.md` | buttons/forms (Run A) |
| `PRODUCTION/.claude/agents/visual-system-designer.md` | tokens/layout (Run A) |
| `PRODUCTION/.claude/agents/ux-content-state-designer.md` | copy/register (Run A) |
| `PRODUCTION/.claude/agents/accessibility-usability-auditor.md` | a11y (Run A) |
| `PRODUCTION/.claude/agents/backend-db-executor.md` | backend executor (Run B) |
| `PRODUCTION/.claude/agents/portal-production-executor.md` | portal executor (Run B) |
| `PRODUCTION/.claude/agents/integration-boundary-executor.md` | integration executor (Run B) |
| `PRODUCTION/.claude/agents/ops-docs-curator.md` | docs curator (Run B) |
| `PRODUCTION/.claude/agents/executor-w1.md` | legacy DB executor (active until Wave 6) |
| `PRODUCTION/.claude/agents/executor-w2.md` | legacy portal executor (active until Wave 6) |
| `PRODUCTION/.claude/agents/executor-w4.md` | legacy integration executor (active until Wave 6) |
| `PRODUCTION/.claude/agents/governor.md` | legacy governor (active until Wave 6) |
| `PRODUCTION/.claude/agents/verifier.md` | post-executor verifier (kept indefinitely) |
| `PRODUCTION/.claude/commands/` | 15 commands (Run A: 7 UX + 3 core; Run B: 5 execution) |

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

### UX canon (PRODUCTION) and portal locked register (portal)

UX doctrine and locked register are split by purpose:

- **Doctrine** (PRODUCTION; produced by UX agents):
  - `PRODUCTION/docs/phase8/ux/UX_RELEASE_GATE.md`
  - `PRODUCTION/docs/phase8/ux/OPERATIONAL_FLOW_MAP.md`
  - `PRODUCTION/docs/phase8/ux/BUTTON_AND_ACTION_RULES.md`
  - `PRODUCTION/docs/phase8/ux/CONTENT_AND_MICROCOPY_GUIDE.md`
  - `PRODUCTION/docs/phase8/ux/STATUS_EMPTY_ERROR_STATES.md`
  - `PRODUCTION/docs/phase8/ux/ACCESSIBILITY_CHECKLIST.md`
  - `PRODUCTION/docs/phase8/ux/DESIGN_SYSTEM_RULES.md`
  - `PRODUCTION/docs/phase8/ux/SCREEN_SCORECARDS.md`
  - `PRODUCTION/docs/phase8/ux/USER_ROLES_AND_CONTEXTS.md`
  - `PRODUCTION/docs/phase8/ux/UX_OPERATING_PRINCIPLES.md`

- **Locked register** (portal; only `ux-content-state-designer` writes):
  - `gt-factory-os-portal/docs/portal_ux_standard.md`
  - `gt-factory-os-portal/docs/portal_language_direction_audit.md`
  - `gt-factory-os-portal/docs/ux/**handoff**.md` (per-surface packets)

- **Decisions** (PRODUCTION; Tom-approved decision packets):
  - `PRODUCTION/docs/phase8/decisions/FLOW-003-planning-blockers-p0-decision-packet.md`
  - (additional decision packets as authored)

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
