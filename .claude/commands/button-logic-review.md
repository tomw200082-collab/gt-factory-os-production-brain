# /button-logic-review

Invoke `interaction-design-specialist` (and optionally `accessibility-usability-auditor`) to audit
every action on a named portal route for completeness of button/action logic.

## Purpose

Every action in the portal must have: label, disabled state, loading state, destructive marking,
irreversibility marking, post-action confirmation, and error state. This command checks each
action systematically and surfaces missing states as DECISION_GRADE (for irreversible actions)
or FLOW_COMPLETION (for others).

## Usage

```
/button-logic-review <route>
/button-logic-review /po/[id]/edit
/button-logic-review /(ops)/goods-receipt
/button-logic-review /(ops)/waste-adjustment
/button-logic-review --with-a11y   # include accessibility-usability-auditor
```

## Agents involved

Primary: `interaction-design-specialist`
Optional (on `--with-a11y`): `accessibility-usability-auditor` — checks accessible names and
keyboard reachability for all actions reviewed

## Required outputs

```
## button-logic-review — <Route>

### Action completeness matrix
| Action label | Disabled | Loading | Destructive | Irreversible | Confirm | Post-action | Error | Finding |
|---|---|---|---|---|---|---|---|---|
| <label> | ✓/✗ | ✓/✗ | yes/no | yes/no | ✓/✗ | ✓/✗ | ✓/✗ | INTER-NNN / — |

### Findings
#### [INTER-NNN] <name>
- Class: DECISION_GRADE / FLOW_COMPLETION
- Action: <label>
- Missing: <list of missing states>
- Proposed fix: <plain English>
- Acceptance criterion: <verifiable>

### Handoff packet
[YAML]
```

## Write policy

**Read-only.** Reports may be saved to `PRODUCTION/docs/phase8/dry-runs/`.

## Stop conditions

- Any action is irreversible and has no confirmation → P0 DECISION_GRADE finding; report immediately.
- An action requires a backend endpoint that does not exist → ARCH_REQUIRED; halt that finding and escalate.

## Not usable for

- Editing portal code.
- Adding backend endpoints.
- Automatically generating missing states.
