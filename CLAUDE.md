# GT Factory OS — Boot Kernel

> Locked decisions only. No execution policy, no schema, no state, no history.
> Full locked text: `docs/decisions/LOCKED_DECISIONS.md` · schema/integration: `docs/contracts/SCHEMA_GUIDANCE.md`.

**Authority order** (higher wins):
1. `CLAUDE.md` — locked decisions.
2. `EXECUTION_POLICY.md` — lanes, modes, signals, approvals, frozen flags.
3. `CURRENT_STATE.md` — live gate status, critical path, open gaps.
4. `.claude/state/runtime_ready.json` + `active_mode.json` — signals & W2 mode.
5. `ACTIVE_NOW.md` — ephemeral. Never overrides above.
6. Memory files, agent/command files — informational; verify before relying.

∴ lower doc contradicts this file → this file wins & lower doc ! be corrected.

## Identity

Narrow high-trust factory-ops platform for GT Everyday — small beverage factory, Israel. ⊥ ERP.
Wins when: stock truth trusted · operator flow beats workbook · planning reproducible & auditable · Excel carries ⊥ operational risk.
`GT_Factory_OS.xlsx` = current-state source only. ⊥ preserve its structure.

**Tiebreakers:** reliability > elegance · trust > scope · simple > irreversible-complex.

## Workspace

| Repo | Role |
|---|---|
| `gt-factory-os-production-brain/` | this repo. Governance, state, policy, agents, commands. ⊥ runtime code |
| `gt-factory-os/` | backend — Fastify, Postgres, migrations, jobs, integrations, Edge Functions |
| `gt-factory-os-portal/` | Next.js 15 portal (canonical; `window2-portal-sandbox/` = historical name, same tree) |
| `archive/`, `docs/archive/` | historical. ⊥ cite as active truth |

Paths repo-relative. ⊥ hardcode absolute machine paths. Geography: `WORKSPACE_MAP.md`.

## Boot

1. This file. 2. `CURRENT_STATE.md`. 3. `EXECUTION_POLICY.md`. 4. `ACTIVE_NOW.md`.
5. `AI_BRAIN_ROUTER.md` → classify → lane/agent/command. 6. Read only routed lane's files.

## Source of truth

| Domain | Authority |
|---|---|
| Master data post-seed | Postgres (`gt-factory-os` core schema) |
| Stock events + history | `stock_ledger` — append-only; corrections via reversal rows; ⊥ UPDATE/DELETE |
| Stock projections | `balance_anchors` + ledger projection (rebuild-verified nightly) |
| Open orders + shipment | LionWheel mirror |
| Shopify FG inventory | sync target only — platform wins on disagreement |
| Supplier invoice evidence | Green Invoice (⊥ active prices alone; validation rules !) |
| Workbook | transitional only. ⊥ round-trip ever |
| Gate status / completion / critical path | `CURRENT_STATE.md` (sole) |
| RUNTIME_READY signals | `.claude/state/runtime_ready.json` (sole) — ⊥ restate count in prose |
| W2 mode | `.claude/state/active_mode.json` (sole) |

## Non-negotiables

1. Stock truth ships before planning cutover.
2. Forms & integrations create events → Postgres stores truth → ledger stores immutable history → projections compute current → engine computes recommendations.
3. Dashboard & Excel consume curated read models only. ⊥ Excel round-trip ever.
4. Excel transitional only. ⊥ long-term system brain.
5. Simplest architecture that survives daily factory use.

## Lanes

≤4 simultaneous executor lanes: `backend-db` · `portal` · `integration` · `docs`.
Read-only, ⊥ count as lane: `governance` · `release-gate` · `source-of-truth` · `ux-audit`.
Inventory: `REGISTRY.md`. Verdict tokens: `VERDICT_GLOSSARY.md`.

## Authorization

Acting on connected systems is core to Claude's purpose here, ⊥ forbidden.
Claude MAY read, write, act through connected systems (Postgres/Supabase, LionWheel, Make, Shopify, Green Invoice, GitHub) — **only when confident action is correct & matches Tom's intent.**

**Claude MAY, autonomously:**
- `git push` + PR **merge** — required checks green & change verified (Tom 2026-06-20). ⊥ merge on red checks or unverified high-blast-radius change.
- **Prod deploy + prod-DB migration apply** — deploy gates green: pre-flight stock-truth check, CI green, migration applies cleanly, post-deploy health check (Tom 2026-07-24). Post one-line announcement immediately before dispatch — visibility, ⊥ permission; ⊥ wait for reply.
- Reversible, single-scope, low-blast-radius external writes.

**Claude ! ask first:**
- Irreversible, destructive, mass-scale (bulk / many records), or money-/customer-facing writes — cancel or re-assign live deliveries, mass status changes, place real supplier/customer orders, customer-visible changes. State exactly what will happen, get Tom's go.
- Any frozen-flag or code-sentinel flip (below).

**Always:** understand before write — inspect real API field/endpoint semantics; ⊥ guess LionWheel or Green Invoice fields · every external write logged, traceable, reversible-by-design · unsure → ⊥ write, ask.

**Stock truth stays sacred regardless.** `stock_ledger` append-only, corrections via reversal only. ⊥ direct ledger/projection mutation. Deploy autonomy moved *mechanics* only — relaxes nothing about ledger semantics.

## Write boundaries

- Agent allowed-paths declarations exhaustive. Path ∉ list → ⊥ writable.
- `CLAUDE.md` — Tom sole writer.
- Other authority docs — `ops-docs-curator` writes under `factory-os-governor` approval.
- `.claude/state/*.json` — emitting executors append only. ⊥ overwrite.
- Frozen: env flags `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` + code sentinels `SHOPIFY_FG_SYNC_LIVE_ADAPTER_WIRED`, `SHOPIFY_FULFILLMENT_BRIDGE_LIVE_ADAPTER_WIRED` — stay `false` until Tom written approval + dry-run + ≥24h soak + RUNTIME_READY.

## Stop conditions

Any agent HALTS, emits signal, routes to `factory-os-governor`. ⊥ silently continue.

1. Frozen flag / sentinel would flip without Tom written approval.
2. Locked decision here (or `docs/decisions/LOCKED_DECISIONS.md`) would be violated.
3. Artifact unverifiable — no path, no paste, summary only.
4. `contract_failure` | `assumption_failure`.
5. Git baseline at risk — uncommitted authority docs, `.gitignore` bypass, `git add -A` / `git add .`.
6. Change touches product code outside an authorized lane.

## Evidence

Tests report N/N. Projection = rebuild-from-ledger within tolerance. RUNTIME_READY only when every check green. "It should work" ⊥ evidence.
Every PASS states: files changed · tests N/N · contracts referenced · signals emitted · stop conditions tripped · Tom approvals required · rollback plan · next handoff.

## Handoff

Every agent run ends: STATUS (PASS | FAIL | BLOCKED | HOLD_FOR_TOM) + the 8 PASS fields. Tokens ! match `VERDICT_GLOSSARY.md`. Template: `AGENT_TEMPLATE.md`.

## New modules

New module (CRM, leads, sales, marketing, finance, any surface beyond factory-os) ⊥ built until `MODULE_TEMPLATE.md` filled & Tom approves in writing. Until then router returns `verdict: NEW_MODULE_REQUIRED`. Per-module isolation: module agents ⊥ touch factory-os core schema.

## Forbidden assumptions

- ⊥ preserve workbook structure. ⊥ assume Excel stays editable long-term.
- ⊥ second writable fallback system. ⊥ second planning service in v1.
- ⊥ model FEFO / expiry / location / bin / customer pricing in v1.
- ⊥ duplicate `BOUGHT_FINISHED` into components.
- ⊥ guess live API field names (LionWheel, Green Invoice) without inspection.
- ⊥ add new authority docs without Tom approval. ⊥ promote dry-runs or proposals to authority.

## Uncertainty

Uncertain → ⊥ guess. Mark assumption explicitly, halt until resolved. Live UNRESOLVED list: `CURRENT_STATE.md`.

---
**Owner:** Tom (sole writer). **Amended:** 2026-07-24 deploy autonomy · 2026-06-20 external-action authorization.
**History:** `docs/archive/CLAUDE.pre-lean-2026-07-31.md` · `docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md`.
