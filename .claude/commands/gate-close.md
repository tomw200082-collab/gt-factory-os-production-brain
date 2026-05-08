# /gate-close

Prepare the closure packet for a Phase / Wave / Gate. Coordinates the relevant executor,
`release-verifier`, `source-of-truth-auditor`, and `factory-os-governor` to assemble the exit
evidence required by the gate. Does not mark a gate closed without evidence. Does not edit
authority docs.

## Purpose

Bring a gate to a documented closure point. A "closure packet" is the canonical exit-evidence
artifact for a Phase or Wave: tests run, contracts ratified, parity verified, doc drift cleared,
RUNTIME_READY signals emitted, frozen flags confirmed, and Tom approvals captured. The packet is
the input to a Tom-approved Phase / Wave transition; it is not itself the transition.

## Usage

```
/gate-close <gate>
/gate-close phase:<n>
/gate-close wave:<n>
/gate-close gate:<n>            # Per CLAUDE.md gate model: 1=alignment, 2=foundation, 3=stock truth, 4=mirrors, 5=planning
/gate-close <gate> dry-run      # Produce the packet but do not request transition
```

## Arguments

| Arg | Required | Description |
|-----|---------|-------------|
| target | yes | `phase:<n>`, `wave:<n>`, or `gate:<n>` |
| dry-run | no | Append `dry-run` to produce the packet without requesting transition |

## Agents involved

| Agent | Role |
|-------|------|
| `factory-os-governor` | Final go/no-go on closure |
| `release-verifier` | Verifies exit-evidence checklist completeness |
| `source-of-truth-auditor` | Verifies no doc drift remains |
| `backend-db-executor` | Provides RUNTIME_READY signal evidence and parity proofs |
| `portal-production-executor` | Provides UX handoff packet status and surface implementation log |
| `integration-boundary-executor` | Provides bridge state and freshness evidence |
| `ops-docs-curator` | Confirms runbook freshness and archive integrity |

## Required inputs

1. The named gate (or phase or wave).
2. `PRODUCTION/CLAUDE.md` — gate model + non-negotiables.
3. `PRODUCTION/CURRENT_STATE.md` — live gate status (sole authority).
4. `PRODUCTION/EXECUTION_POLICY.md` — lane policy.
5. `PRODUCTION/.claude/state/runtime_ready.json` — RUNTIME_READY signals for the surfaces in scope.
6. The exit-evidence checklist for the gate (per CLAUDE.md):
   - Gate 1: artifacts internally consistent.
   - Gate 2: masters round-trip through API; nightly export green; jobs monitor records every run.
   - Gate 3: projection equals rebuild within tolerance; idempotency tests pass; count-freeze races
     pass; minimal Exceptions Inbox in place.
   - Gate 4: LionWheel mirror reconciles; forecast versioning + freeze enforced; freshness exceptions
     emit on stale integration.
   - Gate 5: planning runs reproducible; recommendations require human approval; Production Actual
     posts BOM-derived consumption against pinned BOM version; cost rollup matches manual fixture.
7. The current verdict from `/ux-release-gate` for any UX-visible gate.

## Required outputs

A closure packet at `PRODUCTION/docs/phase8/handoffs/GATE-<n>-closure-packet-<date>.md` containing:

1. **Gate identity** — gate number, gate name, applicable phase / wave.
2. **Exit-evidence matrix** — every CLAUDE.md exit criterion with green / red / pending status
   and the file path of the proof.
3. **RUNTIME_READY surfaces** — list of every signal emitted, signal id, surface, date.
4. **Test evidence** — pgTAP results, vitest results, parity / rebuild results, idempotency results,
   count-freeze race results.
5. **UX gate state** — `UX_RELEASE_GATE.md` verdict for every applicable surface; FLOW-003 state.
6. **Source-of-truth audit** — current drift report (D-classification: stale / conflicting /
   orphaned / authoritative).
7. **Frozen flag state** — both flags' value with timestamp.
8. **Doc hygiene** — runbook freshness, archive INDEX integrity, no flat-root regression.
9. **Tom approvals captured** — list of every Tom-written approval applicable to this gate.
10. **Open items** — anything unresolved; gate cannot close until each is resolved or
    explicitly waived by Tom.
11. **Verdict** — one of:
    - `READY_TO_CLOSE` — all evidence green; Tom approval is the only remaining step.
    - `READY_WITH_CONSTRAINTS` — green if listed waivers are accepted by Tom.
    - `NOT_READY` — named blockers; do not request transition.

## Allowed scope (read-mostly)

- Read all relevant authority docs, state files, contracts, runbooks, dry-run evidence.
- Write the closure packet under `PRODUCTION/docs/phase8/handoffs/`.
- Append a closure-packet entry to `PRODUCTION/docs/phase8/handoffs/INDEX.md` (creating it if
  it does not exist).

## Forbidden scope

- **No edits to authority docs** (`CLAUDE.md`, `EXECUTION_POLICY.md`, `WORKSPACE_MAP.md`,
  `CURRENT_STATE.md`).
- **No edits to UX standards.**
- **No marking a gate closed in any doc** — that is Tom's action, performed via a separate
  CURRENT_STATE.md patch that this command may propose but never apply.
- **No code changes.**
- **No external writes.**
- **No flag flips.**
- **No deploys.**
- **No merges.**

## Side-effect policy

Writes the closure packet doc and the optional INDEX.md entry. No other state changes.

## Validation requirements

The command must verify, before producing the packet:

1. Every exit criterion in CLAUDE.md for the gate has been checked against actual file state.
2. Every RUNTIME_READY signal claimed has a matching entry in `runtime_ready.json`.
3. Every UX-visible surface has a current `UX_RELEASE_GATE.md` verdict.
4. No FLOW-003 frozen file has been touched outside the FLOW-003 decision packet's allowed scope.
5. Source-of-truth drift report is current (≤ 7 days old; otherwise refresh via
   `/source-truth-audit` first).

## Tom approval triggers

The closure packet is read-only output. Tom must explicitly authorize:

- The transition itself (e.g. "Gate 3 closed; advance to Gate 4").
- Any waiver listed in the `READY_WITH_CONSTRAINTS` verdict.
- Any patch to `CURRENT_STATE.md` that records the closure.

The packet alone does not move the gate.

## Stop conditions

| Condition | Action |
|-----------|--------|
| Any exit criterion red without explicit Tom waiver | `NOT_READY` |
| Frozen flag at unexpected state | `NOT_READY` + `frozen_flag_unexpected_state` |
| FLOW-003 frozen file touched | `NOT_READY` + `flow_003_freeze_violation` |
| RUNTIME_READY signal claimed but missing from `runtime_ready.json` | `NOT_READY` + `signal_evidence_missing` |
| Source-of-truth drift report shows critical conflict | `NOT_READY` + `truth_conflict_unresolved` |
| Doc archive INDEX integrity violated | `NOT_READY` + `archive_integrity_failed` |

## GitHub / mobile usability

- The packet is plain markdown; suitable for paste into a Tom-approval conversation or PR comment.
- The command does not interact with GitHub.

## Local-only limitations

- All evidence must come from local file state and committed artifacts. The command does not
  invoke remote checks.

## Example

```
/gate-close phase:8 wave:2
/gate-close gate:3
/gate-close phase:8 wave:2 dry-run
```

## Not usable for

- Marking a gate closed in `CURRENT_STATE.md` (Tom-only edit).
- Issuing a Phase or Wave transition.
- Authorizing a flag flip.
- Authorizing a deploy.
- Authorizing a merge.
