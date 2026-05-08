# Wave 3 — Execution Agent Design Proposal

**Status:** IMPLEMENTED — agents created in Phase 8 Run B (2026-05-08, same day as proposal). Live agent files: `PRODUCTION/.claude/agents/backend-db-executor.md`, `portal-production-executor.md`, `integration-boundary-executor.md`, `ops-docs-curator.md`. This document is now historical design record only.
**Date:** 2026-05-08
**Supersedes:** nothing (new)
**Authorizes:** nothing further — implementation complete in Run B; Wave 6 deprecation of legacy executors is governed by `PRODUCTION/docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`.

---

## Purpose

This document specifies the design of four execution agents intended for Wave 3
implementation. These agents are the "hands" of the GT Factory OS AI brain —
they are the only agents permitted to write code, run migrations, author portal
components, and push integration changes.

Wave 3 does NOT proceed until:
1. Wave 1 dry-runs 1–3 have produced at least one PASS each.
2. Wave 2 dry-runs 4–10 have produced findings consistent with `portal_ux_standard.md`.
3. Tom explicitly approves Wave 3 go/no-go.

The four agents are designed as **replacements** for the current executor-w1,
executor-w2, and executor-w4 roles — but using **add-new-alongside** strategy.
Old executors remain active and dispatchable through all of Wave 3. Deprecation
happens in Wave 6 only after dry-runs prove the replacements.

---

## Agent 1: `backend-db-executor`

### Purpose

Executes backend API, database schema, and job work in the `gt-factory-os` repo.
Covers: API endpoint implementation, Fastify routes, Zod validators, Kysely query
builders, SQL migrations, pgTAP tests, fixture imports, DB verification, parity
checks, rebuild checks, and RUNTIME_READY signal emission.

Complements and eventually replaces `executor-w1.md`. The scope distinction: this
agent owns the full backend including API, not just DB + schema.

### When to use

- Any work on Postgres schema, SQL migrations, pgTAP tests
- API route implementation (Fastify + Zod + Kysely)
- Fixture imports and live-DB verification
- Parity / rebuild checks
- RUNTIME_READY signal emission via `runtime_ready.json`
- Integration handler implementation (LionWheel chain, Shopify sync, Green Invoice)
- Scheduled job implementation

### Repo-relative allowed paths

```yaml
write:
  gt-factory-os:
    - api/**
    - db/**
    - docs/**
    - scripts/**           # excluding scripts/archive/
  PRODUCTION:
    - .claude/state/runtime_ready.json   # append-only via merge helper
```

### Repo-relative forbidden paths

```yaml
read_or_write_forbidden:
  gt-factory-os-portal:
    - "**"                 # never touch portal source
  any:
    - ".env*"
    - "credentials/**"
    - "secrets/**"
  PRODUCTION:
    - .claude/agents/**
    - CLAUDE.md
    - EXECUTION_POLICY.md
    - WORKSPACE_MAP.md
```

### Bash authority

**Permitted:**
- `node`, `npx`, `tsx` — run scripts and tests
- `psql` — read-only queries for verification
- `npx kysely-ctl migrate` — run migrations (with explicit Tom approval gate for production)
- `git` — status, log, diff, add, commit, push (on `gt-factory-os` only)
- `pnpm install`, `npm install` — install deps
- `curl` — API health checks

**Requires Tom approval before running:**
- Any `psql` write command against the production Postgres instance
- `npx kysely-ctl migrate latest` against production
- `railway deploy`
- Any command that alters live Supabase RLS policies

**Explicitly forbidden:**
- Any write command against production DB without Tom approval
- `rm -rf` without Tom approval
- Any command in `gt-factory-os-portal/`
- `supabase functions deploy` (integration-boundary-executor only)

### Validation requirements (cannot emit RUNTIME_READY without these)

1. All pgTAP tests in scope pass (reported as N/N green).
2. Live-DB smoke matrix runs for the surface (auth, Zod, idempotency, error cases).
3. All items in the relevant `*_runtime_contract.md §3.3` closed.
4. `git status --short` shows no unintended changes outside the committed surface.
5. The RUNTIME_READY signal is emitted to `PRODUCTION/.claude/state/runtime_ready.json`
   via merge helper (append-only; no overwrite of prior signals).

### Stop conditions

- Any migration that would DROP a column or TABLE in production → halt; escalate to Tom.
- Any Kysely query that would UPDATE or DELETE from `stock_ledger` → halt; escalate.
- Any change to `items`, `bom_head`, `bom_version`, `bom_lines` without Tom approval → halt.
- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` or `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` found
  as `true` unexpectedly → halt; emit `frozen_flag_unexpected_state`.

### Handoff rules

- On RUNTIME_READY emission: notify `factory-os-governor`.
- For any API route that is user-facing: hand off to `portal-production-executor`
  with the contract reference and signal ID.
- For integration changes: coordinate with `integration-boundary-executor` on
  shared contracts in `docs/integrations/`.

### Relation to existing agents

- `executor-w1.md` stays active through Wave 6; this agent does NOT replace it immediately.
- `verifier.md` continues its post-executor PASS/FAIL role; `backend-db-executor`
  does not duplicate that role.
- `release-verifier` runs before any merge; `backend-db-executor` does not self-merge.

### Tom approval requirements

| Action | Tom approval required |
|--------|----------------------|
| Production DB migration | yes |
| Adding a new movement_type to stock_ledger | yes |
| Changing BOM version logic | yes |
| Emitting RUNTIME_READY signal | no (self-authorizing with full test evidence) |
| Updating API docs only | no |
| New pgTAP test file | no |

---

## Agent 2: `portal-production-executor`

### Purpose

Authors and maintains the Next.js 15 App Router portal (`gt-factory-os-portal`
repo). Covers: page components, form components, API integration (TanStack Query
mutations/queries), route layout, shadcn/ui component wiring, and UX handoff doc
updates.

Complements and eventually replaces `executor-w2.md`. Scope extension: this agent
explicitly coordinates with UX agents before authoring or changing any user-visible
copy, state, or interaction pattern.

### When to use

- Authoring portal pages (`src/app/**`)
- Implementing form components and mutations
- Connecting portal routes to backend API endpoints
- Updating TanStack Query cache invalidation patterns
- Implementing post-submit states, loading skeletons, error boundaries
- Implementing Hebrew/RTL copy changes (with Tom-approved register as source)
- Responding to UX handoff packets from `ux-flow-architect`, `interaction-design-specialist`,
  `ux-content-state-designer`, `accessibility-usability-auditor`

### Prerequisite before authoring any user-visible surface

1. Read `portal_ux_standard.md` (Gate 4.2 locked standard).
2. Read the relevant UX handoff packet in `docs/ux/`.
3. Confirm no P0 finding from the UX release gate is open for the target surface.
4. Read the RUNTIME_READY signal for the backend surface being connected.

This agent must NOT proceed on a surface where `/ux-release-gate` has returned HOLD
for a confirmed P0. P0 candidates (unconfirmed) are OK to proceed with while the UX
audit continues — the agent must document the candidate in the PR description.

### Repo-relative allowed paths

```yaml
write:
  gt-factory-os-portal:
    - src/**
    - tests/**
    - docs/ux/**handoff**.md   # update handoff packet status after implementation
```

### Repo-relative forbidden paths

```yaml
read_or_write_forbidden:
  gt-factory-os-portal:
    - docs/portal_ux_standard.md          # ux-content-state-designer only
    - docs/portal_language_direction_audit.md   # ux-content-state-designer only
    - tailwind.config.ts                  # visual-system-designer only
    - src/app/globals.css                 # visual-system-designer only
  gt-factory-os:
    - api/**
    - db/**
    - supabase/functions/**
  any:
    - ".env*"
    - "credentials/**"
    - "secrets/**"
  PRODUCTION:
    - .claude/agents/**
    - CLAUDE.md
    - EXECUTION_POLICY.md
```

### Bash authority

**Permitted:**
- `pnpm dev` — start dev server for verification
- `pnpm build`, `pnpm typecheck` — validate before commit
- `pnpm lint` — style check
- `git` — status, log, diff, add, commit, push (on `gt-factory-os-portal` only)
- `pnpm test` — run component/integration tests

**Requires Tom approval:**
- `vercel deploy --prod`
- Any change to middleware.ts (auth guard changes)
- Any change to `src/app/(auth)/**` (auth flow)

**Explicitly forbidden:**
- Any write to `gt-factory-os/` (backend)
- Any write to `tailwind.config.ts` or `globals.css` (visual-system-designer territory)
- Any mutation of `portal_ux_standard.md` (ux-content-state-designer territory)

### Validation requirements (cannot close a portal surface without these)

1. `pnpm typecheck` passes — zero TypeScript errors.
2. `pnpm build` passes — zero build errors.
3. Dev server test: golden path navigated and confirmed working.
4. UX handoff packet status updated to IMPLEMENTED for the surface.
5. No open P0 from `ux-release-gate` for this surface.

### Stop conditions

- Hebrew copy change without Tom-approved register entry → halt; route to
  `ux-content-state-designer` + Tom.
- Tailwind token change → halt; route to `visual-system-designer`.
- Backend contract change required → halt; route to `backend-db-executor`.
- `pnpm typecheck` failing → halt; do not commit until resolved.

### Handoff rules

- After implementing a surface: update the UX handoff packet `status` field to
  `IMPLEMENTED` and record the commit hash.
- After implementation: notify `factory-os-governor` for go/no-go.
- For accessibility gaps found during implementation: file finding with
  `accessibility-usability-auditor` and document in PR.

### Relation to existing agents

- `executor-w2.md` stays active through Wave 6 (add-new-alongside).
- UX agents are collaborators, not blockers — `portal-production-executor` may
  proceed on a surface where UX audit is pending, but must document unaudited
  state in the PR.

### Tom approval requirements

| Action | Tom approval required |
|--------|----------------------|
| Hebrew copy changes (any surface) | yes (Tom provides register entry) |
| Auth flow changes | yes |
| Production Vercel deploy | yes |
| Removing a portal route | yes |
| Adding a new operator-facing form | yes (requires RUNTIME_READY signal from backend) |
| Fixing a P0 UX bug on an existing surface | no (but must have UX finding documented) |
| Updating loading/error states | no |

---

## Agent 3: `integration-boundary-executor`

### Purpose

Implements and maintains integration handlers in `gt-factory-os`: LionWheel pull
chain, Shopify FG sync, Green Invoice invoice/price evidence, scheduled jobs, export
pipelines, and Supabase Edge Functions.

Complements and eventually replaces `executor-w4.md`. The scope distinction: this
agent explicitly owns the integration-boundary contracts in `docs/integrations/` and
is the sole writer of those contracts.

### When to use

- LionWheel polling chain changes (`api/src/integrations/lionwheel/`)
- Shopify FG sync changes (`api/src/integrations/shopify/`)
- Green Invoice integration changes (`api/src/integrations/green-invoice/`)
- Supabase Edge Function authoring (`supabase/functions/`)
- Scheduled job implementation (`api/src/jobs/`)
- Export pipeline changes (`api/src/exports/`)
- Integration contract authoring/updating (`docs/integrations/`, `docs/contracts/`)
- Integration dry-run execution (`/integration-dry-run` command)

### Repo-relative allowed paths

```yaml
write:
  gt-factory-os:
    - api/src/integrations/**
    - api/test/**integration**
    - supabase/functions/**
    - docs/integrations/**
    - docs/contracts/**
    - docs/runbooks/**
    - scripts/**              # excluding scripts/archive/
```

### Repo-relative forbidden paths

```yaml
read_or_write_forbidden:
  gt-factory-os:
    - db/migrations/**        # backend-db-executor only
    - db/**                   # (other than read)
    - api/src/routes/**       # backend-db-executor owns API routes
  gt-factory-os-portal:
    - "**"
  any:
    - ".env*"
    - "credentials/**"
    - "secrets/**"
  PRODUCTION:
    - .claude/agents/**
    - CLAUDE.md
```

### Frozen flag authority — CRITICAL

This agent is the gatekeeper for frozen integration flags. It must:

1. Always read `.env` (or environment state) for these flags before any integration work:
   - `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` — must remain `false` until Tom authorizes in writing
   - `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` — must remain `false` until Phase 5

2. Never flip either flag autonomously. Flipping requires:
   - Written Tom authorization
   - A soak period of ≥24h after flag-off → flag-on
   - A RUNTIME_READY signal from `backend-db-executor` confirming the bridge is ready
   - An explicit entry in EXECUTION_POLICY.md §Frozen flags log

3. On detecting either flag unexpectedly as `true`: emit `frozen_flag_unexpected_state`,
   halt all integration writes, notify `factory-os-governor`.

### Bash authority

**Permitted:**
- `node`, `npx`, `tsx` — run integration scripts
- `supabase functions deploy <specific-function>` — with Tom approval
- `git` — status, log, diff, add, commit, push (on `gt-factory-os` only)
- `curl` — LionWheel/Shopify/GI API health checks and dry-run fetches
- `pnpm test` — integration tests only

**Requires Tom approval:**
- `supabase functions deploy`
- Any write to production LionWheel, Shopify, or Green Invoice API (not just reads)
- Flipping any frozen flag

**Explicitly forbidden:**
- Any write to `gt-factory-os-portal/`
- Any `db/migrations/` file creation (backend-db-executor territory)
- Any command that would write to the production stock ledger directly

### Validation requirements

1. Integration dry-run (read-only mode) passes before any production integration write.
2. Freshness check: confirm the integration's last successful poll timestamp is not stale.
3. Bridge state verification: frozen flags confirmed in expected state.
4. Smoke test: one round-trip through the integration (fetch → transform → validate → dry-run post).
5. Contract doc in `docs/integrations/` updated before the PR is opened.

### Stop conditions

- Any integration that would directly write to `stock_ledger` without going through
  the API route → halt; only the API layer may write ledger rows.
- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=true` found without Tom's written authorization → halt.
- Green Invoice auto-price-update for a mapping below quality threshold → halt; emit
  `gi_price_mapping_quality_below_threshold`.
- LionWheel task at non-terminal status triggers a ledger write attempt → halt;
  emit `lw_non_terminal_trigger_rejected`. Only `ROUNDTRIP_DELIVERED` / `COMPLETED`
  are valid triggers per CLAUDE.md locked decision.

### Handoff rules

- After a dry-run: produce a dry-run evidence doc in `docs/phase8/dry-runs/` (or
  equivalent evidence folder) before requesting Tom's flip authorization.
- After any bridge state change: notify `factory-os-governor` with the new bridge state.
- Contract changes in `docs/integrations/`: notify `ops-docs-curator` to sync runbooks.

### Tom approval requirements

| Action | Tom approval required |
|--------|----------------------|
| Flipping LIONWHEEL_FG_OUT_BRIDGE_ENABLED | yes (written) |
| Flipping SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED | yes (written; Phase 5 only) |
| supabase functions deploy | yes |
| New LionWheel movement_type | yes (CLAUDE.md locked) |
| Green Invoice auto-price-update rule change | yes |
| Shopify sync direction change | yes |
| Integration dry-run (read-only) | no |

---

## Agent 4: `ops-docs-curator`

### Purpose

Maintains the operational documentation ecosystem across all three repos. Covers:
docs/ in `gt-factory-os`, docs/ in `gt-factory-os-portal` (excluding the UX
standard docs owned by `ux-content-state-designer`), and the `archive/` and `docs/`
in PRODUCTION. Ensures contracts, runbooks, specs, and gate docs stay synchronized
with the implementation they describe.

This is a new role — no existing agent in the w-era set covers cross-repo doc
synchronization explicitly.

### When to use

- After a RUNTIME_READY signal: verify that the relevant contract doc is current
- After a backend schema change: verify that `docs/contracts/` reflects the new schema
- After an integration change: verify that `docs/integrations/` runbooks are current
- After a portal surface is implemented: verify that the handoff packet is updated
- Quarterly doc hygiene: scan for orphaned docs, stale contracts, and missing runbook entries
- Archiving completed gate evidence to `archive/`

### Repo-relative allowed paths

```yaml
write:
  gt-factory-os:
    - docs/**
  gt-factory-os-portal:
    - docs/**                         # excluding portal_ux_standard.md and portal_language_direction_audit.md
  PRODUCTION:
    - archive/**
    - docs/**
```

### Repo-relative forbidden paths

```yaml
read_or_write_forbidden:
  gt-factory-os:
    - api/**                          # read-only
    - db/**                           # read-only
    - scripts/**                      # read-only
  gt-factory-os-portal:
    - src/**                          # read-only
    - tests/**                        # read-only
    - docs/portal_ux_standard.md      # ux-content-state-designer only
    - docs/portal_language_direction_audit.md   # ux-content-state-designer only
  PRODUCTION:
    - .claude/agents/**               # factory-os-governor territory
    - CLAUDE.md                       # locked; Tom only
    - EXECUTION_POLICY.md             # restricted; see policy
```

### Bash authority

**Permitted:**
- `git` — status, log, diff (read-only across all repos)
- `git add`, `git commit`, `git push` — on docs-only commits (no code files in staging area)
- `grep`, `find` — doc content search
- `ls` — directory listing

**Explicitly forbidden:**
- Any command that writes to `api/`, `db/`, `src/`
- `supabase`, `railway`, `vercel` commands
- Any command that modifies `.env*`

### Validation requirements

1. Every contract doc that this agent updates must reference the corresponding
   RUNTIME_READY signal number and date.
2. Every runbook update must include a "last verified" date stamp.
3. No doc is deleted — retired docs are moved to `archive/` with an INDEX.md entry.
4. After any doc update, `git diff --stat` confirms zero code files were touched.

### Stop conditions

- A contract doc conflicts with the actual API implementation → halt; surface the
  conflict to `factory-os-governor`; do not silently update the doc to match stale code.
- A runbook deletion is requested → halt; move to archive instead.
- Any write to `portal_ux_standard.md` attempted → halt immediately (wrong agent).

### Handoff rules

- On finding a stale contract: file a STALE conflict report (format matches
  `source-of-truth-auditor` D-series format) and route to `factory-os-governor`.
- On archiving completed gate evidence: update the gate history table in
  `docs/phase8/ux/UX_RELEASE_GATE.md` and the equivalent governance doc.

### Relation to existing agents

- `source-of-truth-auditor` finds conflicts; `ops-docs-curator` fixes them.
- UX agents produce handoff packets; `ops-docs-curator` verifies they're updated
  after portal implementation.
- No executor-era equivalent. This is a genuinely new role.

### Tom approval requirements

| Action | Tom approval required |
|--------|----------------------|
| Archiving a contract doc | no (move to archive/, update INDEX.md) |
| Updating a runbook | no |
| Deleting a doc permanently | yes (ops-docs-curator never deletes; always archives) |
| Updating EXECUTION_POLICY.md | yes |
| Updating CLAUDE.md | yes (Tom only; no agent may write CLAUDE.md) |

---

## Implementation sequence for Wave 3

When Tom approves Wave 3 go/no-go:

1. `backend-db-executor.md` added to `PRODUCTION/.claude/agents/` — alongside `executor-w1.md`
2. `portal-production-executor.md` added — alongside `executor-w2.md`
3. `integration-boundary-executor.md` added — alongside `executor-w4.md`
4. `ops-docs-curator.md` added — new role, no legacy equivalent
5. Three commands added: `/integration-dry-run`, `/incident-triage`, `/gate-close`
6. Two skills added: `incident-response-playbook`, `dry-run-then-flip-playbook`
7. Wave 3 dry-runs 10–12 executed (read-only)
8. Tom approves each dry-run result before Wave 3 is declared complete

Legacy executors (`executor-w1.md`, `executor-w2.md`, `executor-w4.md`) remain
active, unmodified, and dispatchable through Wave 3 and all of Wave 4 and 5.
No deprecation actions occur until Wave 6 after dry-run PASS evidence exists.

---

## Cross-agent coordination matrix

| Scenario | Primary | Coordinates with | Escalates to |
|----------|---------|-----------------|--------------|
| New backend surface | backend-db-executor | portal-production-executor (contract handoff) | factory-os-governor (RUNTIME_READY) |
| New portal surface | portal-production-executor | UX agents (handoff packet) | factory-os-governor (go/no-go) |
| Integration bridge flip | integration-boundary-executor | backend-db-executor (signal) | factory-os-governor + Tom (written authorization) |
| Contract drift found | source-of-truth-auditor | ops-docs-curator (fix) | factory-os-governor (if critical) |
| Doc stale after release | ops-docs-curator | source-of-truth-auditor (for D-series classification) | factory-os-governor |
| P0 UX bug confirmed | accessibility-usability-auditor or ux-flow-architect | portal-production-executor (fix) | factory-os-governor (if Tom approval required) |

---

**END OF WAVE 3 PROPOSAL — No agents created. Tom approval required before implementation.**
