# /screen-scorecard

Produce a structured quality scorecard for a named portal screen covering flow, interaction,
visual, copy, and accessibility dimensions.

## Purpose

Aggregates findings from all five UX agents into a single screen health report.
Produces a scored summary (P0/P1/P2/P3 counts per dimension) to support prioritization.
Use before a sprint to identify which screens need work, or before a release gate check.

## Usage

```
/screen-scorecard <route>
/screen-scorecard /(ops)/goods-receipt
/screen-scorecard /planning/production-plan
/screen-scorecard /planning/blockers
/screen-scorecard --all-ops   # score all (ops) routes
```

## Agents involved

All five UX agents in sequence:
1. `ux-flow-architect` — flow coverage score
2. `interaction-design-specialist` — interaction quality score
3. `visual-system-designer` — visual system score
4. `ux-content-state-designer` — copy quality score
5. `accessibility-usability-auditor` — a11y score

## Required outputs

```
## Screen scorecard — <Route>

### Scores
| Dimension | P0 | P1 | P2 | P3 | Status |
|---|---|---|---|---|---|
| Flow | <count> | ... | ... | ... | RED/AMBER/GREEN |
| Interaction | ... | ... | ... | ... | ... |
| Visual | ... | ... | ... | ... | ... |
| Copy | ... | ... | ... | ... | ... |
| Accessibility | ... | ... | ... | ... | ... |

### Overall rating
SHIP_READY / NEEDS_WORK / BLOCKED

### Top P0 findings (all dimensions)
1. [FLOW/INTER/VISUAL/COPY/A11Y]-NNN — <one-line description>
...

### Recommended work order
<prioritized list by P0→P1, most impactful first>
```

**Status thresholds:**
- `GREEN` — 0 P0, ≤2 P1
- `AMBER` — 0 P0, >2 P1 OR ≤1 P0 non-blocking
- `RED` — ≥1 P0 blocking issue

**Overall rating:**
- `SHIP_READY` — all dimensions GREEN
- `NEEDS_WORK` — any AMBER
- `BLOCKED` — any RED

## Write policy

**Read-only.** Scorecards may be saved to `PRODUCTION/docs/phase8/dry-runs/` or
`PRODUCTION/docs/phase8/ux/`.

## Not usable for

- Automatically fixing any finding.
- Merging or deploying portal code.
- Replacing individual `/ux-flow-audit`, `/button-logic-review`, `/design-system-check` runs
  when depth is needed (scorecard is breadth-first; detailed commands are depth-first).
