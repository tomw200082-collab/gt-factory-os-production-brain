# /ux-flow-audit

Invoke `ux-flow-architect` to audit end-to-end operational flow quality on a named portal route.

## Purpose

Checks whether a portal surface supports the full factory operational cycle:
entry → processing → review → decision → terminal action → post-action visibility → auditability → user confidence.

Produces flow findings classified as DECISION_GRADE / FLOW_COMPLETION / POLISH_ACCELERATION, plus a
handoff packet for the portal executor.

## Usage

```
/ux-flow-audit <route>
/ux-flow-audit /(ops)/goods-receipt
/ux-flow-audit /(ops)/physical-count
/ux-flow-audit /(ops)/waste-adjustment
/ux-flow-audit /planning/blockers
/ux-flow-audit /planning/production-plan
/ux-flow-audit /po/[id]/edit
```

## Agents involved

Primary: `ux-flow-architect`
Supporting: `ux-content-state-designer` (for copy findings), `accessibility-usability-auditor` (if
a11y issues emerge during flow audit), `interaction-design-specialist` (for action/form issues)

## Required inputs

The `ux-flow-architect` reads (in order):
1. `portal_ux_standard.md` — locked UX standard.
2. `portal_language_direction_audit.md` — severity model.
3. Backend contract for the named route (from `gt-factory-os/docs/contracts/` or `gt-factory-os/docs/specs/`).
4. RUNTIME_READY signal for the route (from `runtime_ready.json`).
5. Portal route source files (`src/app/<route>/page.tsx`, `_components/`, `_lib/`).

## Required outputs

```
## ux-flow-architect audit — <Route>

### Flow coverage
| Stage | Status | Finding |

### Findings (classified)
#### [FLOW-NNN] <name>
- Class: DECISION_GRADE / FLOW_COMPLETION / POLISH_ACCELERATION / ARCH_REQUIRED
- Proposed fix: <plain English>
- Acceptance criterion: <verifiable>

### Handoff packet (to portal-production-executor)
[YAML format — see agent spec]

### Escalations required
[ARCH_REQUIRED items routed to factory-os-governor]
```

## Write policy

**Read-only.** No portal source edits. No DB changes. No backend changes.
Audit reports may be saved to `PRODUCTION/docs/phase8/dry-runs/` or
`gt-factory-os-portal/docs/ux/` (after Tom authorization).

## Stop conditions

- Flow gap requires backend contract change → ARCH_REQUIRED escalation; halt.
- RUNTIME_READY signal not emitted for route → BLOCKED; do not audit.
- Portal code contradicts backend contract materially → halt; surface to Tom.

## Local only / GitHub-readable

Output is structured markdown. Readable from GitHub or mobile without local tooling.
Findings are numbered and classified for easy triage.

## Not usable for

- Editing portal source code.
- Running database migrations.
- Proposing backend API changes without ARCH_REQUIRED classification.
- Auditing external integrations (use `/integration-dry-run` for that).
