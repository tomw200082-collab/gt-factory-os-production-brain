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

## Visual evidence (required)

This gate is **render-grade**, not code-read-only. Every run renders the surfaces
under audit and attaches screenshots. Auth is the sanctioned dev-shim — never a
fake-session header.

Render recipe (the UX agents drive this via Bash; they never edit it — report-only):

```
NEXT_PUBLIC_ENABLE_DEV_SHIM_AUTH=true \
UX_SHOT_ROUTE=<route> UX_SHOT_ROLE=<operator|planner|admin|viewer> \
UX_SHOT_OUT=/tmp/ux-shots [UX_SHOT_FIXTURE=<fixture.json>] \
npx playwright test tests/e2e/ux-shot.spec.ts --grep @uxshot --project=chromium
```

- Harness: `gt-factory-os-portal/tests/e2e/ux-shot.spec.ts` (committed, parameterized).
- Per-surface API responses are supplied by a JSON fixture file (`UX_SHOT_FIXTURE`),
  not by editing the spec — so producing a screenshot never touches portal source.
- Evidence rule: a **visual / layout** finding MUST cite a screenshot path. A
  **structural / flow / copy / accessibility-semantic** finding cites `file:line`
  (a screenshot is not forced where it adds nothing).
- Forbidden: `X-Fake-Session` / `X-Test-Session`; Supabase production login in CI.

## Severity × effort + single ranked report

The gate emits **one** report, not five. The per-dimension sections feed a single
cross-dimension **Top-N ranked action list** — that ranked list is the
operator-facing deliverable.

- Every finding carries `severity` (P0 | P1 | P2) **×** `effort` (S | M | L).
- Rank by severity first, then ascending effort (a P0/S is the #1 action).
- The per-dimension tables below remain as the audit trail beneath the ranked list.

## How it is invoked (three doors → one gate)

All three call this same command — no forked logic:

1. **Manual** — `/ux-release-gate [--scope <routes>]` in an interactive session.
2. **Per-PR** — `gt-factory-os-portal/.github/workflows/portal-ux-gate.yml` (label-gated;
   checks out both repos so the agents resolve from `PRODUCTION/.claude`).
3. **Weekly** — a step in `portal-drift-weekly.yml` runs the full-portal sweep.

## Required outputs

```
## UX release gate

### Scope
<routes audited>

### Top-N ranked actions (the deliverable — one list, all dimensions)
| # | Sev | Effort | Dimension | Route | Finding | Proposed fix | Evidence |
|---|-----|--------|-----------|-------|---------|--------------|----------|
| 1 | P0 | S | Visual | /dashboard | <one line> | <plain-English fix> | shot:`<path>` |
| 2 | P0 | M | Flow | /planning/procurement | <one line> | <fix> | `file:line` |
| ... | ... | ... | ... | ... | ... | ... | ... |

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
