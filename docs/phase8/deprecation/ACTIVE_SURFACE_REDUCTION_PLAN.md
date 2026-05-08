# Active Surface Reduction Plan — Phase 8 Run B

**Status:** PROPOSAL ONLY. No agent archived. No agent disabled. No agent renamed.
No deletion.
**Date:** 2026-05-08
**Author:** factory-os-governor + ops-docs-curator (joint, read-only).
**Authorizes:** nothing — Tom must explicitly approve each archive step before execution.

---

## A. Current active agents (PRODUCTION/.claude/agents/)

After Run B Step 2, the agent set is:

### A.1 — Phase 8 Run A core production brain (3)

1. `factory-os-governor.md` — go/no-go, source-of-truth hierarchy, lane control
2. `release-verifier.md` — pre-merge / pre-deploy verification
3. `source-of-truth-auditor.md` — cross-doc drift classification

### A.2 — Phase 8 Run A UX/UI agents (5)

4. `ux-flow-architect.md` — flow doctrine
5. `interaction-design-specialist.md` — buttons, forms, undo, confirmations
6. `visual-system-designer.md` — tokens, layout, typography
7. `ux-content-state-designer.md` — copy, register, state language; sole writer of `portal_ux_standard.md`
8. `accessibility-usability-auditor.md` — a11y / WCAG basics

### A.3 — Phase 8 Run B execution agents (4 — added in this run)

9. `backend-db-executor.md` — backend API + DB + migrations + jobs
10. `portal-production-executor.md` — Next.js portal authoring
11. `integration-boundary-executor.md` — LionWheel / Shopify / GI / Edge Functions / contracts
12. `ops-docs-curator.md` — docs hygiene + archive index + deprecation planning

### A.4 — Legacy agents (5 — kept active)

13. `executor-w1.md` — legacy DB / schema / migrations / tests / verification
14. `executor-w2.md` — legacy canonical portal authoring
15. `executor-w4.md` — legacy integrations / jobs / exports / dashboard contracts
16. `governor.md` — legacy governor (predecessor of `factory-os-governor`)
17. `verifier.md` — legacy post-executor PASS/FAIL verifier

**Total active: 17 agents.**

---

## B. New production agents (Run B authored)

| New agent | Replaces | Add-new-alongside? |
|-----------|---------|---------------------|
| `backend-db-executor` | `executor-w1` | yes |
| `portal-production-executor` | `executor-w2` | yes |
| `integration-boundary-executor` | `executor-w4` | yes |
| `ops-docs-curator` | (no executor-era predecessor) | n/a — net new role |

`factory-os-governor` (Run A) replaces `governor.md` (legacy) — same add-new-alongside.
`release-verifier` (Run A) is **complementary** to `verifier.md`, not a replacement:
- `release-verifier` is **pre-merge / pre-deploy** verification (the one Run B uses).
- `verifier.md` is **post-executor PASS/FAIL** verification (the legacy executors use it).

The two verifiers stay paired: pre-merge gate + post-executor gate. They are not in conflict.

---

## C. One-to-one replacement map

| Legacy agent | New production agent | Status |
|-------------|---------------------|--------|
| `executor-w1.md` | `backend-db-executor.md` | both active; legacy still dispatchable |
| `executor-w2.md` | `portal-production-executor.md` | both active; legacy still dispatchable |
| `executor-w4.md` | `integration-boundary-executor.md` | both active; legacy still dispatchable |
| `governor.md` | `factory-os-governor.md` | both active; legacy still dispatchable |
| `verifier.md` | (no replacement; complemented by `release-verifier`) | both retain distinct roles |
| (no predecessor) | `ops-docs-curator.md` | new role; no legacy to retire |

---

## D. Agents that remain active temporarily

All 5 legacy agents (`executor-w1`, `executor-w2`, `executor-w4`, `governor`, `verifier`)
remain active through:

- All of Phase 8 Run B (this run).
- All of any subsequent Run C / D dry-runs.
- Until **Wave 6 deprecation gate** with explicit dry-run PASS evidence per `factory-os-governor.md`.

There is no time-based retirement. Retirement is evidence-based.

---

## E. Agents to archive later (with proof requirements)

### E.1 — `executor-w1.md`

**Proof required before archive:**

1. ≥ 3 successful real-world `backend-db-executor` runs that close `*_runtime_contract.md §3.3`
   for distinct surfaces.
2. Each of those runs emits a RUNTIME_READY signal accepted by `factory-os-governor`.
3. Each of those runs passes `release-verifier` for the merge / deploy.
4. No `executor-w1.md` invocation occurs in those runs.
5. Tom explicitly approves the archive in writing.

### E.2 — `executor-w2.md`

**Proof required before archive:**

1. ≥ 3 successful real-world `portal-production-executor` runs that ship distinct portal
   surfaces.
2. Each run consumes a UX handoff packet and updates the packet `status` to `IMPLEMENTED`.
3. Each run passes `release-verifier` and `factory-os-governor` MERGE_OK.
4. Each run passes `pnpm typecheck` + `pnpm build` + browser smoke test.
5. No `executor-w2.md` invocation in those runs.
6. Tom explicitly approves the archive in writing.

### E.3 — `executor-w4.md`

**Proof required before archive:**

1. ≥ 2 successful real-world `integration-boundary-executor` dry-runs (no flag flip needed
   — dry-run alone counts as proof of agent operation).
2. ≥ 1 successful real-world `integration-boundary-executor` integration code change with
   `release-verifier` pass.
3. Frozen flag state remains correct throughout all runs.
4. No `executor-w4.md` invocation in those runs.
5. Tom explicitly approves the archive in writing.

### E.4 — `governor.md`

**Proof required before archive:**

1. ≥ 5 successful real-world `factory-os-governor` invocations on distinct phases / waves /
   tasks.
2. Source-of-truth hierarchy enforcement demonstrated (at least one case where governor
   correctly resolved a doc conflict).
3. No `governor.md` invocation in those runs.
4. Tom explicitly approves the archive in writing.

### E.5 — `verifier.md`

**Treatment is different.** `verifier.md` is a post-executor PASS/FAIL verifier; it is
complementary to `release-verifier` (pre-merge gate), not a replacement. Possible outcomes:

- **Option E.5.a:** keep `verifier.md` indefinitely as the post-executor verifier; do not retire.
- **Option E.5.b:** retire `verifier.md` only when the new executor agents prove they
  self-validate (the new agents include explicit post-checks that match the verifier role)
  AND Tom approves.

This plan does NOT recommend retiring `verifier.md` in Wave 6. Recommend Option E.5.a until
Tom indicates otherwise.

---

## F. Commands to remove / retire later (if any)

After Run B's command additions, the active commands are:

### F.1 — Run A UX commands (7)

- `/ux-flow-audit`
- `/button-logic-review`
- `/empty-error-state-audit`
- `/design-system-check`
- `/screen-scorecard`
- `/operator-task-simulation`
- `/ux-release-gate`

### F.2 — Run A core commands (3)

- `/production-go-no-go`
- `/release-check`
- `/source-truth-audit`

### F.3 — Run B commands (5 — added in this run)

- `/portal-pr-review`
- `/integration-dry-run`
- `/gate-close`
- `/incident-triage`
- `/docs-hygiene-check`

**Total: 15 commands.**

### F.4 — Commands proposed for retirement: NONE

No command is proposed for retirement in this plan. The 15-command set is internally
consistent per DR-016. If a future scan finds an underused command, retirement should
follow the same evidence-based process as agent retirement.

---

## G. Memory files to review later

The following memory files (per `MEMORY.md`) should be reviewed during Wave 6 deprecation
to confirm they remain current:

| Memory | Review concern |
|--------|---------------|
| `project_gt_factory_os.md` | confirms authority structure split; should still be valid |
| `feedback_docs_not_bottleneck.md` | should still be valid — Run B respected the rule |
| `feedback_harness_state_authoritative.md` | confirms `runtime_ready.json` + `active_mode.json` priority; should still be valid |
| `reference_gt_factory_paths.md` | confirms repo paths; should still be valid |
| `feedback_conditional_vs_full_go.md` | should still be valid — Run B uses CONDITIONAL framing for human-only gates |

No memory file is proposed for archival or removal in this plan.

---

## H. What remains active truth after archive

After hypothetical Wave 6 archive (assuming Tom approves all proofs):

### H.1 — Active agents (12)

- `factory-os-governor`
- `release-verifier`
- `source-of-truth-auditor`
- `ux-flow-architect`
- `interaction-design-specialist`
- `visual-system-designer`
- `ux-content-state-designer`
- `accessibility-usability-auditor`
- `backend-db-executor`
- `portal-production-executor`
- `integration-boundary-executor`
- `ops-docs-curator`
- (`verifier.md` per Option E.5.a — keep)

### H.2 — Active commands (15)

Unchanged from current — no command retirement proposed.

### H.3 — Authority docs

- `CLAUDE.md` — locked decisions
- `EXECUTION_POLICY.md` — operational governance
- `CURRENT_STATE.md` — live gate status
- `WORKSPACE_MAP.md` — repo path map
- `ACTIVE_NOW.md` — ephemeral

---

## I. What must never be treated as active truth (after archive)

After archive, the following are **historical reference only**:

- `archive/legacy-agents/executor-w1.md`
- `archive/legacy-agents/executor-w2.md`
- `archive/legacy-agents/executor-w4.md`
- `archive/legacy-agents/governor.md`
- (possibly: `archive/legacy-agents/verifier.md` if Option E.5.b is chosen)

Any reference to these in active docs should be updated to point to the new agents OR be
archived along with the legacy agent.

The `factory-os-advance` skill mentions "executor-w1/w2/w4" by name. That skill must be
updated alongside the agent archive — its description names the legacy executors directly.
This is a **prerequisite** for archive: skill must be updated first.

---

## J. Exact proposed archive destination

When Tom approves archive:

```
PRODUCTION/.claude/agents/executor-w1.md
  → PRODUCTION/archive/legacy-agents/executor-w1-archived-2026-XX-XX.md

PRODUCTION/.claude/agents/executor-w2.md
  → PRODUCTION/archive/legacy-agents/executor-w2-archived-2026-XX-XX.md

PRODUCTION/.claude/agents/executor-w4.md
  → PRODUCTION/archive/legacy-agents/executor-w4-archived-2026-XX-XX.md

PRODUCTION/.claude/agents/governor.md
  → PRODUCTION/archive/legacy-agents/governor-archived-2026-XX-XX.md

(Optional)
PRODUCTION/.claude/agents/verifier.md
  → PRODUCTION/archive/legacy-agents/verifier-archived-2026-XX-XX.md
```

`PRODUCTION/archive/INDEX.md` must be updated with one entry per archived file showing:
- Original path
- Archive path
- Archive date
- Replacement agent (or "none — role retained" for verifier.md)
- Tom approval reference

The `factory-os-advance` skill must be updated to no longer reference
`executor-w1/w2/w4` — the references must point to new agents, or the skill must be
deprecated entirely, BEFORE the archive proceeds.

---

## K. Rollback plan

If a Wave 6 archive proves premature (a real production incident requires the legacy agent):

1. **Move file back from archive:** `git mv archive/legacy-agents/executor-w1-archived-*.md
   .claude/agents/executor-w1.md` (preserving git history).
2. **Update `archive/INDEX.md`:** mark the entry as "rollback — restored YYYY-MM-DD; reason: …".
3. **Update `factory-os-advance` skill back to its pre-archive references.**
4. **File a `factory-os-governor` finding** explaining what the new agent could not handle and
   what proof is needed before retiring again.

Rollback must be a Tom-approved operation; not autonomous.

---

## L. Go / no-go checklist for deprecation wave

When Wave 6 is reached, the deprecation can proceed only when ALL of these are green:

| Check | Required state |
|-------|---------------|
| `backend-db-executor` real-run proof count | ≥ 3 |
| `portal-production-executor` real-run proof count | ≥ 3 |
| `integration-boundary-executor` dry-run + integration-change proof | ≥ 2 + ≥ 1 |
| `factory-os-governor` real-run proof count | ≥ 5 |
| `ops-docs-curator` real-run proof count | ≥ 1 (`/docs-hygiene-check` real-data scan) |
| All proofs produced clean `release-verifier` PASS | yes |
| `factory-os-advance` skill updated to remove legacy executor references | yes |
| Any other skill / hook / settings reference to legacy agents updated | yes |
| `archive/INDEX.md` integrity verified | yes |
| Tom written approval for the wave | yes |
| FLOW-003 P0 status | resolved (or explicitly waived for the wave) |
| Frozen flags state | both `false`; or any `true` is Tom-approved with soak |

**If any cell is "no", the wave does not proceed.**

---

## M. Why archive is gated by evidence

Premature archive risks losing institutional memory in the legacy agent definitions. Each
legacy agent encodes years of operational rules. The new agents inherit most rules but may
miss edge cases not exercised in dry-runs.

The wave-6 evidence-bar is:
- Proves the new agent handles real production work end-to-end.
- Proves no regression in the role.
- Proves the new agent's rules are at least as protective as the legacy agent's.

A premature archive that loses an institutional rule is a worse outcome than a slightly
larger active surface for one extra wave.

---

## N. STATUS block

```
STATUS: PASS

Scope: Active surface reduction plan (Wave 6 readiness)
Agents archived: 0 (proposal only)
Agents disabled: 0 (proposal only)
Agents renamed: 0 (proposal only)
Files deleted: 0 (forbidden — always archive)
Replacement map: complete
Proof requirements: defined per legacy agent
Rollback plan: documented
Go/no-go checklist: 12 cells; current Run B fills 0 of them (intentional — Run B is dry-run)
Tom approvals required: each archive step requires explicit Tom written approval
Handoff: factory-os-governor — wave 6 readiness review when proofs accumulate
```

---

**END OF ACTIVE SURFACE REDUCTION PLAN — No agent archived in Run B; no legacy agent modified.**
