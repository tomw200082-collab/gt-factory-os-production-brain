# /ux-release-gate

Run the full UX release gate check before a portal release. Aggregates all UX agent audits and
produces a formal SHIP / CONDITIONAL_SHIP / HOLD verdict for UX quality.

## Purpose

Gate a portal release on UX quality. Requires zero P0 findings across all five UX dimensions
before issuing SHIP. Produces a structured verdict with named blockers and named conditional items.

This is the final UX check before a portal commit is considered production-ready.

## Usage

```
/ux-release-gate
/ux-release-gate --scope <route-list>
/ux-release-gate --focus <ops>      # all (ops) routes only
/ux-release-gate --focus <planning> # all /planning routes only
```

## Agents involved

All five UX agents:
1. `ux-flow-architect`
2. `interaction-design-specialist`
3. `visual-system-designer`
4. `ux-content-state-designer`
5. `accessibility-usability-auditor`

Supporting: `factory-os-governor` — issues formal SHIP / HOLD verdict

## Required outputs

```
## UX release gate

### Scope
<routes audited>

### P0 findings (all dimensions) — block ship if any present
| ID | Dimension | Route | Description |
|---|---|---|---|
| ... | ... | ... | ... |

### P1 findings — conditional ship items
| ID | Dimension | Route | Description |
|---|---|---|---|

### Per-dimension status
| Dimension | P0 | P1 | Status |
|---|---|---|---|
| Flow | 0 | 2 | GREEN |
| Interaction | 0 | 1 | GREEN |
| Visual | 0 | 3 | AMBER |
| Copy | 1 | 0 | RED |
| Accessibility | 0 | 1 | GREEN |

### portal_ux_standard.md compliance
<PASS / violations noted>

### Verdict
SHIP | CONDITIONAL_SHIP | HOLD

### Conditions (if CONDITIONAL_SHIP)
<named P1 items that must be resolved in next sprint>

### Blockers (if HOLD)
<named P0 items with exact location and fix>

### Tom approval required?
yes / no — reason

### Next action for Tom
<one concrete step>
```

**Verdict thresholds:**
- `SHIP` — zero P0 findings across all five dimensions.
- `CONDITIONAL_SHIP` — zero P0 findings; P1 findings noted for next sprint; Tom approval.
- `HOLD` — any P0 finding present.

## Write policy

**Read-only.** Gate reports saved to `PRODUCTION/docs/phase8/dry-runs/` by default.
After Tom approval, saved to `gt-factory-os-portal/docs/ux/` as a formal gate record.

## Stop conditions

- Any P0 finding → HOLD immediately.
- A UX agent cannot audit a route (no RUNTIME_READY signal) → BLOCKED; report to Tom.

## Not usable for

- Bypassing P0 findings to ship anyway.
- Editing portal code to fix findings.
- Merging or deploying the portal release.

## Relationship to release-verifier

`release-verifier` checks git/branch/lane safety.
`ux-release-gate` checks UX quality.
Both are required before a portal release is considered production-ready.
A SHIP verdict from `/ux-release-gate` does not replace a `/release-check` run.
