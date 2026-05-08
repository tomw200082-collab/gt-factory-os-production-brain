# /operator-task-simulation

Invoke `ux-flow-architect` to trace a named factory operator task from entry to auditability,
identifying all gaps in process continuity and post-action visibility.

## Purpose

Simulates a specific factory workflow (e.g., "receive goods against PO #123", "file production
report for FG-DES-1L") end-to-end and maps every gap where the operator must guess, wait, or
resort to manual/developer intervention. Focuses on what the operator experiences, not what
the code does.

## Usage

```
/operator-task-simulation <task-name>
/operator-task-simulation goods-receipt-with-PO-prefill
/operator-task-simulation physical-count-submit-and-approve
/operator-task-simulation waste-adjustment-and-verify
/operator-task-simulation production-report-from-plan
/operator-task-simulation po-create-manual-and-attach-receipt
```

## Agents involved

Primary: `ux-flow-architect`
Supporting: `interaction-design-specialist` (for action gaps found in simulation)

## Required outputs

```
## operator-task-simulation — <Task name>

### Task definition
- Operator role: <operator / planner / admin>
- Entry point: <URL / button / form>
- Goal: <what the operator is trying to accomplish>
- Expected terminal state: <what "done" looks like>

### Step-by-step trace
| Step | UI element | Data needed | Data available | Gap |
|---|---|---|---|---|
| 1 | <page/form> | <what operator needs to see> | yes/no | — / FLOW-NNN |

### Post-action visibility
| After completing task | Operator sees | Finding |
|---|---|---|
| Success | <what is shown> | PASS / FLOW-NNN |
| Where to find result | <list / audit trail / inbox> | PASS / FLOW-NNN |

### Manual intervention required
<list of steps where operator must leave the portal, ask a developer, or use Excel>

### Findings
<FLOW-NNN findings from simulation>

### Handoff packet
[YAML]
```

## Write policy

**Read-only.** Reports may be saved to `PRODUCTION/docs/phase8/dry-runs/`.

## Stop conditions

- Simulation cannot proceed because a RUNTIME_READY signal has not been emitted for a required route.
- A step in the simulation requires a backend endpoint that does not exist → ARCH_REQUIRED finding.

## Not usable for

- Editing portal code.
- Creating test fixtures in the database.
- Running automated E2E tests (use the portal's Playwright test suite for that).
