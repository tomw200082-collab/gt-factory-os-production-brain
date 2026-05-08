# /empty-error-state-audit

Invoke `interaction-design-specialist` and `accessibility-usability-auditor` to audit all
loading, empty, and error states on a named portal route.

## Purpose

Every portal surface must correctly implement exactly one primary state at a time (loading /
error / empty / loaded). Chips and counts must be gated on `query.data !== undefined && !query.isError`.
Empty states must have a primary CTA. Error states must be actionable. This command checks
all state transitions systematically.

## Usage

```
/empty-error-state-audit <route>
/empty-error-state-audit /(ops)/waste-adjustment
/empty-error-state-audit /planning/blockers
/empty-error-state-audit /planning/production-plan
```

## Agents involved

Primary: `interaction-design-specialist` — state transition logic, missing states
`accessibility-usability-auditor` — screen-reader announcements for state changes, `aria-live` coverage

## Required outputs

```
## empty-error-state-audit — <Route>

### State coverage matrix
| Surface / component | Loading | Error | Empty | Loaded | Post-action | Mixed-state bug |
|---|---|---|---|---|---|---|
| <component> | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ | yes/no |

### Chip/count gating review
| Chip | Gated on query.data? | Gated on !query.isError? | Finding |
|---|---|---|---|

### Screen-reader announcements
| State transition | aria-live region | Announcement text | Finding |
|---|---|---|---|

### Findings
<INTER-NNN and A11Y-NNN findings>

### Handoff packet
[YAML]
```

## Write policy

**Read-only.** Reports may be saved to `PRODUCTION/docs/phase8/dry-runs/`.

## Stop conditions

- A component shows "0 items" during a loading state → P0 finding; surface immediately.
- An error state shows raw API error body → P0 COPY finding; surface immediately; route to ux-content-state-designer.

## Not usable for

- Editing portal code.
- Changing API error shapes.
- Implementing aria-live regions directly.
