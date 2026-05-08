# GT Factory OS — Final AI Brain Acceptance

**Acceptance date:** 2026-05-08
**Run:** Phase 8 Run G — final governance closure
**Status:** PASS_FINAL_BRAIN_READY

> This document records that the PRODUCTION AI Brain has been declared complete, remote-preserved, and ready for normal future work. It is an acceptance record, not an authority layer. All durable rules live in `CLAUDE.md` and sibling docs.

---

## Runs that built the brain

| Run | Date | What landed |
|-----|------|------------|
| Phase 8 Run A | 2026-05-08 | `factory-os-governor`, `release-verifier`, `source-of-truth-auditor`, 5 UX agents, 3 governance commands (DR-001..003) |
| Phase 8 Run B | 2026-05-08 | 4 execution agents, 5 execution commands, `ACTIVE_SURFACE_REDUCTION_PLAN.md` (DR-012..016) |
| Phase 8 Run C | 2026-05-08 | FLOW-003 P0 closed (portal commit `9e2212e`), 9 authority-doc patches (DR-017) |
| Phase 8 Run F | 2026-05-08 | `CLAUDE.md` rewritten as thin kernel; `AI_BRAIN_ROUTER.md`, `AGENT_TEMPLATE.md`, `MODULE_TEMPLATE.md`, `AGENT_REGISTRY.md`, `COMMAND_REGISTRY.md`, `VERDICT_GLOSSARY.md`, `LOCKED_DECISIONS.md`, `SCHEMA_GUIDANCE.md` created; pre-kernel archive written |
| Phase 8 Run F.2b | 2026-05-08 | PRODUCTION pushed to private remote `gt-factory-os-production-brain` at HEAD `875424b` |
| Phase 8 Run G | 2026-05-08 | CONFLICT-003 closed (SIGNALS.md emitter policy); CURRENT_STATE.md + ACTIVE_NOW.md state refreshed; COMMAND_REGISTRY.md count corrected; PRODUCTION-REMOTE-PLAN.md status updated; this acceptance record created |

---

## Final brain file set

### Root authority docs
- `CLAUDE.md` — thin boot kernel (locked decisions, tiebreakers, stop conditions, boot sequence)
- `CURRENT_STATE.md` — live gate status, completion range, critical path, open gaps
- `EXECUTION_POLICY.md` — window ownership, lane policy, mode amendments, frozen flags
- `ACTIVE_NOW.md` — ephemeral active context
- `WORKSPACE_MAP.md` — repo geography

### Brain scaffolding (Run F)
- `AI_BRAIN_ROUTER.md` — routing decision engine with 6 worked examples
- `AGENT_REGISTRY.md` — 17 agents indexed
- `COMMAND_REGISTRY.md` — 15 commands indexed (7 UX + 3 governance + 5 execution)
- `VERDICT_GLOSSARY.md` — all verdict tokens with semantics and collision notes
- `AGENT_TEMPLATE.md` — required structure for new agents
- `MODULE_TEMPLATE.md` — required declaration for new modules (CRM, leads, etc.)

### Extracted decisions and contracts
- `docs/decisions/LOCKED_DECISIONS.md` — verbatim locked-decision text from pre-kernel CLAUDE.md
- `docs/contracts/SCHEMA_GUIDANCE.md` — schema, BOM, audit, integration, security, observability
- `docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md` — pre-rewrite CLAUDE.md preserved

### Agents (17 files in `.claude/agents/`)
3 core (governance) + 5 UX (read-only) + 4 execution (Phase 8) + 5 legacy (active until Wave 6). See `AGENT_REGISTRY.md` for full inventory.

### Commands (15 files in `.claude/commands/`)
7 UX + 3 governance + 5 execution. See `COMMAND_REGISTRY.md` for full inventory.

### Signals
- `.claude/SIGNALS.md` — signal semantics; RUNTIME_READY emitter policy (closed CONFLICT-003 in Run G)
- `.claude/state/runtime_ready.json` — 35 signals on disk (authoritative)
- `.claude/state/active_mode.json` — W2 mode (authoritative)

---

## What is canonical vs deferred

### Canonical (no further work needed)
- Boot sequence, authority hierarchy, stop conditions — CLAUDE.md
- Lane model, signal policy, retry policy, mode amendments — EXECUTION_POLICY.md
- Routing logic — AI_BRAIN_ROUTER.md
- Agent + command inventory — registries
- Verdict semantics — VERDICT_GLOSSARY.md
- RUNTIME_READY emitter policy — SIGNALS.md (CONFLICT-003 closed)
- PRODUCTION remote — `gt-factory-os-production-brain` private repo, HEAD `875424b`

### Deferred (not blocking future work)
- **CONFLICT-009** — W2 mode timestamp stale line in EXECUTION_POLICY.md. Low-value; defer to a future governance pass.
- **D3 completion range** — `CURRENT_STATE.md` shows `NEEDS_TOM_CALIBRATION`. Tom sets the new range when ready; do not invent a percentage.
- **Wave 6 legacy archival** — 4 legacy agents remain active until proof criteria in `ACTIVE_SURFACE_REDUCTION_PLAN.md` are met. Tom must approve each step.
- **Hooks/settings/MCP rollout** — plan authored in `docs/phase8/WAVE4-HOOKS-SETTINGS-MCP-CLAUDE-PROPOSALS.md`; not yet implemented. Deferred.

---

## What is forbidden without Tom

- Editing `CLAUDE.md` — Tom is sole writer.
- Building any new module (CRM, leads, sales, marketing, finance) — requires filled `MODULE_TEMPLATE.md` + Tom written approval.
- Flipping frozen flags (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`) — requires Tom written approval + dry-run + ≥24h soak + RUNTIME_READY.
- Archiving any legacy agent — requires Wave 6 evidence + Tom written approval.
- Pushing `main`, merging, deploying — Tom only; no autonomous action.

---

## How to start a future session

1. Read `CLAUDE.md` (boot kernel).
2. Read `CURRENT_STATE.md` (live gate + completion).
3. Read `EXECUTION_POLICY.md` (operating law).
4. Read `ACTIVE_NOW.md` (ephemeral context).
5. Consult `AI_BRAIN_ROUTER.md` to classify the incoming request → lane → agent → command.
6. Read only the relevant agent / command files.

Boot sequence is complete when steps 1–5 are done. Step 6 is dispatch-specific.

---

## Future module entry path (CRM or any new module)

1. Copy `MODULE_TEMPLATE.md` to `docs/decisions/modules/<module-name>-declaration.md`.
2. Fill every required section (business purpose, owner lane, source of truth, data model, allowed paths, UX surfaces, tests, gates, rollback, isolation boundaries).
3. Submit to Tom for written approval.
4. After approval, `factory-os-governor` updates `AI_BRAIN_ROUTER.md` §3 with the module's lane row(s).
5. Module-scoped agents become dispatchable; they cannot touch factory-os core schema.

No CRM code, schema, agent, command, or UX surface may be built before step 3 is complete.

---

## Return-to-product recommendation

The AI Brain is ready. Recommended next non-brain work, in priority order:

1. **D-B3.1c / D-B3.2 — Shadow DB setup** (blocked; DATABASE_URL_SHADOW missing). Unblock shadow DB to resume backend migration work.
2. **Shopify External Boundary v2 Gate E** — GE-1 test SKU + GE-2 sentinel strategy (Option C) are open Tom decisions.
3. **Sunday 2026-05-10 physical count + bridge cutover** — per runbook `docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md`.
4. **Portal autonomous program** — UX audit releases blocked surfaces through the gate model.

---

**Owner:** `factory-os-governor` (governs this record).
**Accepted by:** Tom (implicit on PR merge).
**Last updated:** 2026-05-08 (Phase 8 Run G — initial creation).
