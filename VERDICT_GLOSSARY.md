# GT Factory OS — Verdict Glossary

> **Authority layer:** canonical glossary of every verdict token used by any command in `PRODUCTION/.claude/commands/`.
>
> **Run F position (Tom decision E):** existing verdict tokens are **not renamed** in commands. This glossary documents semantics and collisions; it does not change command behavior. A future run may consider renaming if collisions cause real dispatch confusion.
>
> **Use:** when an agent or command emits a verdict token, the token's meaning is the one defined here. If a token is used outside the contexts listed, that is a drift case for `/source-truth-audit` to flag.

---

## How to read this glossary

Each entry has:
- **Token** — exact verdict string (uppercase + underscore).
- **Semantics** — what it means.
- **Emitting commands** — which `/command` files produce this token.
- **Blocks merge/deploy/apply?** — whether downstream action is gated.
- **Tom required?** — whether Tom must take action before the next step.
- **Ambiguity notes** — collisions or context-sensitive meanings.

---

## Go / no-go family

| Token | Semantics | Emitting commands | Blocks? | Tom required? | Notes |
|---|---|---|---|---|---|
| `PROCEED` | All checks pass; safe to proceed with the proposed action. | `/production-go-no-go` | no | no | The "green light" verdict. |
| `PROCEED_WITH_CONSTRAINTS` | Proposed action is allowed only if named, documented constraints continue to hold. | `/production-go-no-go` | no, with constraints | depends on constraints | Constraints must be specific and verifiable. |
| `HOLD` | One or more blocking conditions named; must be resolved before proceeding. | `/production-go-no-go`, `/ux-release-gate` | yes | usually yes | **Collision:** in `/production-go-no-go`, HOLD = dependency / lane / locked-decision blocker; in `/ux-release-gate`, HOLD = any P0 UX finding present. Same token, different domains. Dispatchers must read context. |
| `SWITCH_LANE` | Proposed action belongs to a different agent / executor / lane; routing redirected. | `/production-go-no-go` | yes (the original lane is wrong) | no (technical re-route) | Acts as a routing instruction, not a final verdict. |

## Closure / readiness family

| Token | Semantics | Emitting commands | Blocks? | Tom required? | Notes |
|---|---|---|---|---|---|
| `READY_TO_CLOSE` | All exit criteria green; gate / phase / wave can close. | `/gate-close` | no | usually yes (Tom signs the closure) | Final pre-Tom verdict from the executor side. |
| `READY_WITH_CONSTRAINTS` | All exit criteria green except for named, documented waivers. | `/gate-close`, `/production-go-no-go` | no, with named waivers | yes (waiver acceptance) | Waivers must be enumerated. |
| `NOT_READY` | Named blockers prevent closure / advance. | `/gate-close`, `/integration-dry-run` | yes | depends on blocker | **Cross-context use** (gate closure vs integration readiness); semantically compatible — different domains, same meaning. |
| `READY_FOR_FLIP_REQUEST` | Integration handler is dry-run-clean; Tom may now consider authorizing the frozen-flag flip. | `/integration-dry-run` | no | yes (flip is HARD-gated) | Flip itself requires written approval + ≥24h soak + RUNTIME_READY. |
| `READY_FOR_EXTERNAL_WRITE_REQUEST` | Integration handler is dry-run-clean; Tom may now consider authorizing an external write (POST/PUT/DELETE). | `/integration-dry-run` | no | yes (HARD-gated) | Distinct from the bridge flip. |

## Release / merge family

| Token | Semantics | Emitting commands | Blocks? | Tom required? | Notes |
|---|---|---|---|---|---|
| `SAFE_FOR_HUMAN_REVIEW` | Branch is safe for human merge review. | `/release-check` | no | yes (human merges) | Run F: no autonomous merge or push. |
| `CONDITIONALLY_SAFE` | Branch is safe IF named conditions hold; reviewer must verify. | `/release-check` | no, with conditions | yes | Parallel to `PROCEED_WITH_CONSTRAINTS` but in a different command. |
| `NOT_SAFE` | Policy-driven block (frozen flag, secrets, CLAUDE.md touched, cross-repo, migration + portal coupling, etc.). | `/release-check` | yes | yes | Auto-block; cannot be overridden without Tom written authorization. |
| `BLOCKED` | Manual block / explicit halt. | `/release-check`, `/screen-scorecard` | yes | yes | Distinct from `NOT_SAFE`: BLOCKED is reviewer-asserted; NOT_SAFE is policy-asserted. |
| `MERGE_OK` | PR may be merged. | `/portal-pr-review` | no | yes (human merges) | Per Tom decision A, no autonomous merge. |
| `MERGE_OK_WITH_CONSTRAINTS` | PR may be merged if named constraints hold. | `/portal-pr-review` | no, with constraints | yes | Constraints enumerated. |
| `BLOCK` | PR must not merge — confirmed blocker. | `/portal-pr-review` | yes | yes | Distinct from `HOLD_FOR_TOM`: BLOCK is automatic; HOLD_FOR_TOM is authority-dependent. |
| `HOLD_FOR_TOM` | PR must not merge until Tom authority decision (e.g., Hebrew register entry, FLOW-003-substrate touch). | `/portal-pr-review`, `/screen-scorecard` | yes | yes (Tom authority required) | Both BLOCK and HOLD_FOR_TOM block merge; the latter signals that Tom alone can unblock. |

## UX gate family

| Token | Semantics | Emitting commands | Blocks? | Tom required? | Notes |
|---|---|---|---|---|---|
| `SHIP` | Zero P0 findings across all dimensions; surface ships. | `/ux-release-gate` | no | no | The full-green UX verdict. |
| `CONDITIONAL_SHIP` | Zero P0 findings; P1s noted for next sprint. | `/ux-release-gate` | no, with noted P1 backlog | usually no | Stop-gap when polish remains but no critical defects. |
| `SHIP_READY` | Per-route status from scorecard; route-level "all dimensions GREEN". | `/screen-scorecard` | no | no | Route-level analogue of SHIP. |
| `NEEDS_WORK` | Per-route status; not yet ship-ready. | `/screen-scorecard` | yes (at route level) | no | Not a hard gate; informational. |
| `NOT_AUDITED` | Surface has not been audited at source level (typically because RUNTIME_READY signal missing or auditor lacked access). | `/ux-release-gate`, `/screen-scorecard` | implicit (cannot SHIP) | depends | Indicator of coverage gap, not a decision. |

## Triage family

| Token | Semantics | Emitting commands | Blocks? | Tom required? | Notes |
|---|---|---|---|---|---|
| `ROUTED` | Triage complete; incident routed to the named agent. | `/incident-triage` | no | depends on incident | Triage produces a routing decision, not a remediation. |
| `NEEDS_TOM` | Decision required before remediation begins (flag flip, rollback, direct ledger touch suggested). | `/incident-triage` | yes | yes | Always requires Tom authority. |
| `NO_INCIDENT` | No observable defect found; the reported symptom did not reproduce. | `/incident-triage` | no | no | Equivalent: `NO_INCIDENT_VERIFIED`. |
| `NO_LOCAL_STATE` | Cannot access state to triage; returns placeholder triage block. | `/operator-task-simulation` | yes | depends | Indicates the agent could not gather facts; do not act on the placeholder. |

## Drift / hygiene family

| Token | Semantics | Emitting commands | Blocks? | Tom required? | Notes |
|---|---|---|---|---|---|
| `CLEAN` | All checks green; no drift. | `/docs-hygiene-check` | no | no | The all-green hygiene verdict. |
| `MINOR_DRIFT` | Small, low-risk drift; proposals limited to one or two categories. | `/docs-hygiene-check` | no | no | Apply patches at convenience. |
| `SIGNIFICANT_DRIFT` | Multiple categories with proposals; not blocking but should be addressed. | `/docs-hygiene-check` | no | no | Schedule a hygiene cycle. |
| `CRITICAL_DRIFT` | Authority doc reference broken, flat-root regression, or duplicate source-of-truth. | `/docs-hygiene-check` | yes (production work pauses until resolved) | usually yes | Highest hygiene severity. |

## Source-of-truth conflict classes

These are not verdicts but conflict labels emitted by `/source-truth-audit`:

| Token | Semantics | Notes |
|---|---|---|
| `STALE` | A copy is outdated relative to the authoritative source. | Patch is mechanical. |
| `CONFLICTING` | Two copies exist and disagree; both claim authority. | May require Tom decision. |
| `ORPHANED` | Reference points to an artifact that no longer exists. | Reference must be deleted or re-pointed. |
| `SHADOW` | Multiple copies agree (correctly); one is informational and references the canonical source. No action needed. | Confirms the duplicate is intentional and accurate. |

## Finding-code namespaces

These are not verdicts; they are stable ID prefixes for findings recorded in dry-run reports:

| Prefix | Owner | Examples |
|---|---|---|
| `P0` / `P1` / `P2` / `P3` | severity classification across audits | P0 = production data at risk / decision-grade; P1 = operator blocked; P2 = degraded; P3 = cosmetic |
| `FLOW-NNN` | `ux-flow-architect` | FLOW-003 = planning blockers CTA dead-end (closed Run C) |
| `INTER-NNN` | `interaction-design-specialist` | INTER-001 = Cancel-PO confirmation polish |
| `A11Y-NNN` | `accessibility-usability-auditor` | A11Y-001 = waste-adjustments form-label gap |
| `VISUAL-NNN` | `visual-system-designer` | (visual-system findings) |
| `INC-NNN` | `/incident-triage` | (per-incident IDs) |
| `HC-NNN` | `/docs-hygiene-check` | (per-hygiene-cycle IDs) |
| `DR-NNN` | dry-run records under `docs/phase8/dry-runs/` | DR-017 = FLOW-003 closure recheck |
| `CONFLICT-NNN` | `/source-truth-audit` findings | CONFLICT-002 = signal count drift |

## Failure-class signals

These are not verdicts; they are emitted as signal names when an agent halts:

| Signal | Semantics | Reference |
|---|---|---|
| `contract_failure` | Locked contract has been violated; zero retries; human checkpoint mandatory. | `EXECUTION_POLICY.md` §Stop semantics, `.claude/SIGNALS.md` |
| `assumption_failure` | An agent could not verify an assumption; cannot continue. | Same. |
| `tool_failure` | A tool repeatedly failed; W4 variant marks artifact `TOOL_FAILURE_UNCLEARED`. | Same. |
| `ownership_conflict` | A move crossed a window boundary without W5 / governor approval. | Same. |
| `frozen_flag_unexpected_state` | A frozen flag was found in a non-default state without authorization. | `EXECUTION_POLICY.md` §Frozen flags log |
| `direct_ledger_write_attempted` | An integration handler tried to write `stock_ledger` directly bypassing the API path. | `backend-db-executor.md` §Stop conditions |
| `destructive_migration_blocked` | A migration would `DROP COLUMN` or `DROP TABLE` in production. | Same. |
| `ledger_mutation_attempted` | Code tried to UPDATE/DELETE on `stock_ledger`. | Same. |
| `bom_change_unauthorized` | Change to `items`, `bom_head`, `bom_version`, or `bom_lines` without explicit Tom approval. | Same. |
| `parity_failed` | Stock projection no longer matches rebuild-from-ledger. | Same. |
| `stale_contract_reference` | A contract doc references a symbol that no longer exists in implementation. | Same. |
| `validation_gate_failed` | Tests did not pass. | Same. |
| `typecheck_failed` | TypeScript typecheck failed. | Same. |
| `lw_pick_pre_anchor_skipped` | LionWheel pick row skipped because event_at <= latest_anchor_at. | `CLAUDE.md` §LionWheel pickup → ledger decrement |
| `flow_003_freeze_violation` | A change touched FLOW-003 frozen substrate without decision-packet authority. | `/portal-pr-review.md` |
| `data_failure` | A required data source could not be loaded (e.g., credential missing). | `/integration-dry-run.md` |

---

## Documented collisions (Run F, NOT resolved)

Per Tom decision E, the following collisions are documented but **not renamed**:

1. **`HOLD`** — used by `/production-go-no-go` (dependency-blocked) and `/ux-release-gate` (P0 UX finding). Different domains; dispatchers must read context to disambiguate.
2. **`BLOCK` vs `HOLD_FOR_TOM`** in `/portal-pr-review` — both block merge; differ on whether escalation is automatic (`BLOCK`) or authority-dependent (`HOLD_FOR_TOM`).
3. **`NOT_READY`** — used by `/gate-close` (gate closure) and `/integration-dry-run` (handler readiness). Semantically compatible (both = blockers exist) in different domains.
4. **`CONDITIONALLY_SAFE` (`/release-check`) vs `PROCEED_WITH_CONSTRAINTS` (`/production-go-no-go`)** — parallel vocabularies for similar semantics; no cross-reference exists between commands.

A future run may consolidate. For now, dispatchers and Tom must read context.

---

## Glossary integrity check

Every verdict token in any `.claude/commands/*.md` file should appear in this glossary. If a verdict is found in a command file but missing here, `/source-truth-audit` flags it as `ORPHANED` (token without canonical definition).

---

**Owner:** `factory-os-governor` (governs definitions; consults UX agents on UX verdicts).
**Approver:** Tom (for new verdict tokens; existing tokens are documented as-is).
**Last updated:** 2026-05-08 (Phase 8 Run F Wave 2 — initial creation).
