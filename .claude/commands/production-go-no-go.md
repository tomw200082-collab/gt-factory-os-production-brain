# /production-go-no-go

Invoke the `factory-os-governor` to determine whether a phase, release, branch, or task may proceed.

## Purpose

Produces a formal go/no-go verdict before any phase transition, release, merge, or significant
task execution. Forces evidence review against locked contracts, gate status, frozen flags, and
lane ownership before movement.

## Usage

```
/production-go-no-go
/production-go-no-go <target>
/production-go-no-go phase:<n>
/production-go-no-go branch:<branch-name>
/production-go-no-go task:<short-description>
/production-go-no-go release:<tag-or-description>
```

**With no argument:** audit the current production state against the active gate in `CURRENT_STATE.md`
and return a go/no-go verdict for the next recommended action.

**With argument:** focus the verdict on the named target.

## Agents involved

Primary: `factory-os-governor`
Supporting: `release-verifier` (if a branch or PR is named), `source-of-truth-auditor` (if authority doc drift is detected)

## Required inputs

The governor reads (in order):
1. Caller's target / question.
2. `PRODUCTION/CLAUDE.md` — locked decisions.
3. `PRODUCTION/CURRENT_STATE.md` — live gate status.
4. `PRODUCTION/EXECUTION_POLICY.md` — lane policy.
5. `PRODUCTION/ACTIVE_NOW.md` — operator context.
6. `PRODUCTION/.claude/state/runtime_ready.json` — signal state.
7. `PRODUCTION/.claude/state/active_mode.json` — W2 mode.
8. Any artifact at a verified path named by the caller.

## Required outputs

Exactly one of:
- `PROCEED` — all checks pass.
- `PROCEED_WITH_CONSTRAINTS` — passes with named constraints.
- `HOLD` — named blockers must be resolved first.
- `SWITCH_LANE` — proposed action belongs to a different agent; routing instruction given.

Plus: evidence inspected, rationale, constraints or blockers, Tom-approval flag, next action.

## Write policy

**Read-only.** No file writes. No git mutations. No production data writes. No external calls.
Reports may be saved to `PRODUCTION/docs/phase8/dry-runs/` when run in dry-run mode.

## Stop conditions

- Frozen flag at risk → HOLD immediately.
- Locked decision would be violated → HOLD.
- Artifact not readable (summary only) → `assumption_failure`.
- `contract_failure` or `assumption_failure` → zero retries, escalate.

## Side effects

None. This command is read-only. Running it does not change any state.

## Example: dry-run call

```
/production-go-no-go phase:8 wave:1
```

Governor inspects gate status, open UNRESOLVED items, frozen flags, and W2 mode, then returns
a formal PROCEED / HOLD verdict with the current evidence set.

## Not usable for

- Approving database migrations autonomously.
- Merging PRs.
- Deploying to production.
- Flipping environment flags.
- Any action that requires Tom's explicit written authorization.
