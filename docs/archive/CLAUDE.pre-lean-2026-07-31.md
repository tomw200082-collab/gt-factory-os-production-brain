# GT Factory OS — Boot Kernel

> **Authority layer:** boot kernel. Thinnest authority document. Loaded first by every agent.
> Contains only locked decisions, non-negotiables, boot sequence, source-of-truth tiebreakers, stop conditions, forbidden assumptions, and pointers to deeper docs.
> No execution policy. No schema details. No integration semantics. No transient state. No history.
>
> **Pre-rewrite full text** (Phase 8 Run F, 2026-05-08): `docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md`.
> **Full locked-decision text:** `docs/decisions/LOCKED_DECISIONS.md`.
> **Full schema/integration guidance:** `docs/contracts/SCHEMA_GUIDANCE.md`.
>
> **Authority hierarchy (locked):**
> 1. `CLAUDE.md` (this file) — wins on every conflict on locked decisions.
> 2. `EXECUTION_POLICY.md` — operating law (lanes, modes, signals, retry, approvals, frozen flags).
> 3. `CURRENT_STATE.md` — sole authority on live gate status, completion range, active critical path, open gaps.
> 4. `.claude/state/runtime_ready.json` + `.claude/state/active_mode.json` — sole authority on signals and W2 mode.
> 5. `ACTIVE_NOW.md` — ephemeral context only; never overrides above.
> 6. Memory files — informational only; verify against current files before relying.
> 7. Agent / command files — operational defaults; may be overridden by policy.
>
> **Sibling docs:**
> `EXECUTION_POLICY.md` · `CURRENT_STATE.md` · `ACTIVE_NOW.md` · `WORKSPACE_MAP.md` · `AI_BRAIN_ROUTER.md` · `AGENT_REGISTRY.md` · `COMMAND_REGISTRY.md` · `VERDICT_GLOSSARY.md` · `AGENT_TEMPLATE.md` · `MODULE_TEMPLATE.md` · `docs/decisions/LOCKED_DECISIONS.md` · `docs/contracts/SCHEMA_GUIDANCE.md`.

---

## Project identity
GT Factory OS is a narrow, high-trust factory operations platform for GT Everyday — a small beverage factory in Israel (cocktails, teas, smoothies, margaritas). It is not an ERP. It succeeds when stock truth is trusted, operator workflows beat the workbook, planning recommendations are reproducible and auditable, and Excel stops carrying operational risk. The workbook `GT_Factory_OS.xlsx` is a current-state source only — do not preserve its structure.

**Tiebreakers:** reliability over elegance; trust over scope; simpler path over irreversible complexity.

## Workspace
- **PRODUCTION/** — AI brain (this folder). Governance, state, policy, agents, commands, decisions, contracts. No runtime code.
- **gt-factory-os/** (`C:/Users/tomw2/Projects/gt-factory-os/`) — backend (Fastify, Postgres, migrations, jobs, integrations).
- **gt-factory-os-portal/** (working tree: `window2-portal-sandbox/` — folder name historical, this IS the canonical portal) — Next.js 15 portal.
- **archive/** — historical only. Never cite as active truth.
- Full geography: `WORKSPACE_MAP.md`.

## Boot sequence (every session)
1. Read this file (locked decisions + tiebreakers + stop conditions).
2. Read `CURRENT_STATE.md` (live gate status + critical path + open gaps).
3. Read `EXECUTION_POLICY.md` (operating law).
4. Read `ACTIVE_NOW.md` (active lanes — defer to `CURRENT_STATE.md` on any conflict).
5. Consult `AI_BRAIN_ROUTER.md` to classify the incoming request and pick lane / agent / command.
6. Read only the agent / command files relevant to the routed lane.

## Source-of-truth (locked tiebreakers)

| Domain | Authority |
|---|---|
| Master data after seed import | Postgres (`gt-factory-os` core schema) |
| Stock events + history | `stock_ledger` (append-only; corrections via reversal rows; never UPDATE/DELETE) |
| Stock projections | `balance_anchors` + ledger projection table (rebuild-verified nightly) |
| Open orders + shipment state | LionWheel mirror |
| Shopify FG inventory | Sync target only — platform wins on disagreement |
| Supplier invoice evidence | Green Invoice (not active prices alone — validation rules required) |
| Workbook | Transitional only — never long-term truth; no round-trip ever |
| Live gate status / completion / critical path | `CURRENT_STATE.md` (sole) |
| RUNTIME_READY signals | `.claude/state/runtime_ready.json` (sole) |
| W2 mode | `.claude/state/active_mode.json` (sole) |

## Absolute non-negotiables
1. **Stock truth ships before planning cutover.**
2. Forms and integrations create events; Postgres stores truth; ledger stores immutable history; projections compute current state; planning engine computes recommendations.
3. Dashboard and Excel consume curated read models only. **No Excel round-trip ever.**
4. Excel is transitional only — not the long-term system brain.
5. Prefer the simplest architecture that survives daily factory use.

Full locked-decision text (UX/UI doctrine, deployment, tech stack, auth/roles, UI language, ledger semantics, stock model, RM batch/expiry, orders/integrations, LionWheel pickup→ledger decrement trigger, Excel rules, forecast, production reporting v1, counting v1, receipts/POs, workflow rules, testing posture, final framing): `docs/decisions/LOCKED_DECISIONS.md`. Schema, BOM modeling, audit semantics, integration guidance, security, observability: `docs/contracts/SCHEMA_GUIDANCE.md`.

## Router / lane model (compact)

Every dispatch consults `AI_BRAIN_ROUTER.md` to classify input → lane → agent → command → permissions → evidence.

- **Max 4 simultaneous executor lanes:** `backend-db`, `portal`, `integration`, `docs`.
- **Read-only (do not count as a lane, always-on or on-demand):** `governance`, `release-gate`, `source-of-truth`, `ux-audit`.
- **Production agents (Phase 8 Run B):** `backend-db-executor`, `portal-production-executor`, `integration-boundary-executor`, `ops-docs-curator`, `factory-os-governor`, `release-verifier`, `source-of-truth-auditor`, plus 5 UX agents. Legacy `executor-w1/w2/w4`, `governor`, `verifier` remain dispatchable until Wave 6 deprecation per `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`. Full inventory: `AGENT_REGISTRY.md`. Full command set: `COMMAND_REGISTRY.md`. Verdict semantics: `VERDICT_GLOSSARY.md`.

## Write boundaries

- Each agent's allowed-paths declaration is exhaustive — paths not listed cannot be written.
- `CLAUDE.md` — Tom is sole writer.
- Other authority docs (EXECUTION_POLICY.md, CURRENT_STATE.md, WORKSPACE_MAP.md, ACTIVE_NOW.md, AI_BRAIN_ROUTER.md) — `ops-docs-curator` writes under `factory-os-governor` approval.
- `.claude/state/*.json` — only emitting executors append; never overwrite.
- Frozen flags (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`) — `false` until Tom written approval + dry-run + ≥24h soak + RUNTIME_READY signal.
- `git push` + PR **merge** — Claude MAY do autonomously when required checks are green and the change is verified (Tom-granted in writing 2026-06-20; supersedes the prior Phase 8 Run F "Tom only / no autonomous push"). Do not merge with red/failing required checks or an unverified high-blast-radius change. **Production deploy** and **applying migrations to the production database** — Claude MAY also do autonomously (Tom-granted in writing 2026-07-24; supersedes the prior "deliberate, explicitly-flagged, never silent" framing for the deploy *mechanics* only) when the deploy's own gates are green: pre-flight stock-truth check, CI green, migration applies cleanly, post-deploy health check passes. Still post a one-line chat announcement immediately before dispatching, for visibility — not permission; do not wait for a reply. This does not relax stock-ledger append-only semantics or reversal-only corrections in any way — only the deploy *mechanics* moved from "ask first" to "announce and proceed."

## External-action authorization (Tom-granted in writing, 2026-06-20)

Supersedes the prior blanket prohibition on writing to external systems / being
in the live operational path. Acting on connected systems is **core to Claude's
purpose here**, not forbidden.

Claude MAY read, write, and perform real actions through the systems it is
connected to (Postgres/Supabase, LionWheel, Make, Shopify, Green Invoice,
GitHub, etc.) — **only when confident the action is correct and matches Tom's
intent.** Clear boundaries, always:

1. **Understand before you write.** Inspect current state + real API
   field/endpoint semantics first. Never guess (the LionWheel / Green Invoice
   no-guess rule stands).
2. **Confirm-before-acting on high-risk writes.** Anything irreversible,
   destructive, mass-scale (bulk / many records), or money-/customer-facing —
   e.g. cancelling or re-assigning live deliveries, mass status changes, placing
   real supplier/customer orders, customer-visible changes — state exactly what
   will happen and get Tom's go first. Reversible, single-scope, low-blast-radius
   writes may proceed when confident.
3. **Stock truth stays sacred.** `stock_ledger` append-only (corrections via
   reversal only); no direct ledger/projection mutation. The two named frozen
   flags above still gate ledger-affecting auto-bridges until their dry-run/soak.
4. **Merge is Claude's to do** (Tom-granted 2026-06-20) when required checks are
   green and the change is verified — no waiting for Tom.
5. **Production deploy is also Claude's to do autonomously** (Tom-granted in
   writing 2026-07-24) — migrations + API deploy — when the deploy's own gates
   are green (pre-flight stock-truth check, CI green, migration applies
   cleanly, post-deploy health check). No waiting for a reply required. Still
   post a one-line chat announcement immediately before dispatching, for
   visibility, not permission. This does **not** relax anything about the
   ledger itself — still append-only, still reversal-only corrections — only
   the deploy *mechanics* moved from "ask first" to "announce and proceed."
6. **Audit + reversibility.** Every external write is logged/traceable and
   reversible-by-design where possible.
7. **When unsure — do NOT write. Ask.** Uncertainty discipline still holds.

This is the operating basis for the planned daily-ops skill: Tom queues intent,
the skill executes via sanctioned APIs under these boundaries.

## Stop conditions (any agent halts)

1. A frozen flag would be flipped without Tom written approval.
2. A locked decision in this file (or `LOCKED_DECISIONS.md`) would be violated.
3. An artifact cannot be verified (no path, no paste, only summary).
4. `contract_failure` or `assumption_failure` detected.
5. PRODUCTION git baseline at risk (uncommitted authority docs, `.gitignore` bypass, `git add -A` / `git add .`).
6. A change would touch product code outside an explicitly authorized lane.

In any of the above: **HALT, emit signal, route to `factory-os-governor`. Never silently continue.**

## Evidence standard

- Tests must report N/N counts.
- Stock projection must equal rebuild-from-ledger within tolerance.
- RUNTIME_READY emitted only after every check is green.
- "It should work" is not evidence.
- Every PASS includes: files changed, tests run, contracts referenced, signals emitted, stop conditions tripped, Tom approvals required, rollback plan, next handoff.

## Future module rule

A new module — CRM, lead intake, sales workflow, marketing automation, finance, or any operating-system surface beyond factory-os — cannot be built until `MODULE_TEMPLATE.md` is filled in for that module and Tom approves the declaration in writing. Until then, the router returns `verdict: NEW_MODULE_REQUIRED` for any input that requests work on the undeclared module. Per-module lane isolation: each module's agents have allowed-paths scoped to the module; module agents cannot touch factory-os core schema.

## Forbidden assumptions

- Do not preserve workbook structure.
- Do not assume Excel remains editable long-term.
- Do not build a second writable fallback system.
- Do not introduce a second planning service in v1.
- Do not model FEFO / expiry / location / bin / customer pricing in v1.
- Do not duplicate `BOUGHT_FINISHED` items into components.
- Do not guess live API field names for LionWheel or Green Invoice without inspection.
- Claude tooling/skills MAY be part of the live operational path and MAY write to connected systems — per "External-action authorization" above, within its boundaries (confident, audited, reversible, confirm-before-acting on high-risk). Supersedes the prior blanket "MCP is not a runtime input channel" prohibition (Tom, 2026-06-20).
- Do not add new authority docs without explicit Tom approval. Do not promote dry-runs or proposals to authority.

## Uncertainty discipline

When uncertain, do **not** guess. Mark assumptions explicitly and halt until resolved. Live UNRESOLVED items list: `CURRENT_STATE.md`. Skill creation threshold: `docs/phase8/decisions/STEP4-SKILLS-DECISION.md` (no skills created unless threshold met).

## Handoff contract (every agent run)

Every agent run ends with: STATUS (PASS / FAIL / BLOCKED / HOLD_FOR_TOM), files changed, tests run with N/N counts, contracts referenced, signals emitted, stop conditions tripped, Tom approvals required, rollback plan, next handoff agent. Verdict tokens must match `VERDICT_GLOSSARY.md`. Full template: `AGENT_TEMPLATE.md`.

---

**Owner:** Tom (sole writer of this file).
**Last amended:** 2026-07-24 (Tom-directed, in writing this session): production deploy + prod-DB migration apply moved from "deliberate, ask-first" to "Claude's to do autonomously when the deploy's own gates are green, announce-then-proceed" — mirrors the 2026-06-20 merge-autonomy grant. Stock-ledger append-only semantics are explicitly untouched. Transcribed at Tom's explicit instruction; Tom remains owner.
**Previously amended:** 2026-06-20 (Tom-directed, in writing that session): added "External-action authorization" + reworded the MCP/operational-path forbidden assumption. Transcribed at Tom's explicit instruction; Tom remains owner.
**Last rewritten:** 2026-05-08 (Phase 8 Run F Wave 4 — kernel extraction + thin-boot rewrite).
**Pre-rewrite full text preserved at:** `docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md`.
