# docs/org/ — GT Everyday Org Layer ("חוזה הפעלה חי")

> **Status: DRAFT — pending Tom written approval (= merge). Not authority until merged.**
> On approval this corridor becomes the single source of truth for **who is
> accountable for what** across GT Everyday — people, roles, personas, processes,
> protocols — bound to the live system (portal routes, DB state machines, skills).
> Subordinate to `CLAUDE.md` locked decisions; sibling to other `docs/` corridors.

## Files

| File | What | Who edits |
|---|---|---|
| `SPEC.md` | Goal, constraints, invariants, task list (caveman-encoded) | spec flow only |
| `org_map.yaml` | **The machine core.** Everything binds here | Claude proposes PR → Tom approves |
| `views/*.md` | Derived Hebrew views for the team (roster, matrix, per-person SOP) | Generated from map — never hand-edited |
| `PROPOSALS.md` | Living ops proposals (P-1 production-order loop, P-2 receiving square, P-3 daily briefing, P-4 dead-stock) — nothing executes without Tom | Claude proposes → Tom approves |

## Why this exists

Tom directive (2026-07-21): redo the responsibility split, boundaries, interfaces
and roles — bound to the system so **nothing falls between the chairs**. Before
this corridor, org truth was scattered: one Hebrew playbook here, a stale
ownership matrix in the backend repo, a DRAFT role doc, skills each carrying
their own ritual, and empty gt-axis registries. Known live contradiction at time
of harvest: Doreen = office-manager persona on `planner` system role (OD-1).

## Update protocol (default; Tom ratifies via OD-6)

1. Any change (new hire, process change, system change, drift finding) → Claude
   authors a PR touching `org_map.yaml` (+ regenerated views).
2. Tom approves in writing = merge. No direct-to-main. No agent self-approval.
3. Drift check on every PR + weekly: every route / role / enum / skill / person
   reference in the map must resolve against the live system; divergences become
   `open_decisions` entries — never silent fixes (SPEC §V7).
4. **Add-person:** new `people` entry (name, position, role binding, personas,
   external systems) + every process whose `accountable`/`handoff` changes, in
   one PR. No HR-sensitive data, ever (SPEC §V5).

## Consumers

- **Brain agents** — org/responsibility questions route here (boot step 6+).
- **Operating skills** — `daily-ops-guardian`, `procurement-planning`,
  `plan-production-14d`, `daily-delivery-dispatch`, `goods-receipt-from-invoice`,
  `route-print-pack` read accountable/handoff bindings from the map.
- **Tom** — `open_decisions` is the standing interview list; `decision_log` is history.
- **The team** — via derived Hebrew views only (distribution channel: OD-8).

## The redesign interview (T3) — protocol

Priority per Tom (2026-07-21): the factory's human layer comes first — the floor
does not run on clear roles today. Six stages, one question at a time (grill
style, each with a recommendation), answers land in `org_map.yaml` immediately;
playback ("הנה מה שהבנתי") between stages. Chat-based, mobile-friendly — S2
works best walking the floor. Output feeds T9 (deep presentation for Tom) →
iterate → T10 (employee version).

| # | Stage | Produces |
|---|---|---|
| S0 | Roster + constraints | full cast (incl. part-time / external / hiring), hours, what Tom stops holding himself |
| S1 | Pain harvest | 5-10 real recent failures + daily friction → the problem set the design must solve |
| S2 | Day + week walkthrough | timeline 06:00→close + Thu/Sun rhythm; owner-today vs. owner-should per block; hunts no-screen physical work |
| S3 | Domain ownership | ONE owner per domain; decides-alone / needs-Tom / backup (Owner-Approver-Informed) |
| S4 | Seams (התממשקות) | per handoff: trigger, artifact, deadline, failure protocol |
| S5 | Escalation + iron rules | when to call Tom; never-decide-alone list; 3 iron rules per person |

## Relation to existing docs (on approval)

| Doc | Becomes |
|---|---|
| `docs/playbook/operator-playbook-he.md` | Derived view (regenerated from map; history preserved) |
| `docs/phase8/ux/USER_ROLES_AND_CONTEXTS.md` | Points here for the human side; keeps UX context |
| `gt-factory-os/docs/integrations/downstream_ownership_matrix.md` §Human responsibilities | Points here (its "Alex (planner)" row is stale) |
| `gt-axis-*` skill registries (empty) | OD-7 — recommended: point-to-map, retire scaffold |

---
**Owner:** Tom. **Born:** 2026-07-21, branch `claude/roles-responsibilities-mapping-yck6ph`.
