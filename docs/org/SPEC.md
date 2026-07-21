# SPEC — org layer ("חוזה הפעלה חי")

> Corridor: `docs/org/` in `gt-factory-os-production-brain`.
> **Status: DRAFT — pending Tom written approval (= merge of this PR). Not authority until merged.**
> Encoding: caveman (grill → spec → build chain). Owner: Tom. Mutation: Claude proposes PR → Tom approves.
> Born: 2026-07-21, session `claude/roles-responsibilities-mapping-yck6ph`, from Tom directive: redo responsibility split, boundaries, interfaces, roles — bound to the system so nothing falls between chairs.

## §G

org layer = living operating contract. One machine-readable truth source:
person ↔ system-role ↔ persona ↔ process ↔ surface ↔ state-transition ↔ skill.
Agents read + enforce ∀ dispatch. Hebrew team SOPs derived from it.
NEW responsibility split defined here → system realigns to map. ⊥ reverse.

## §C

- PRIORITY (Tom recalibration 2026-07-21): factory floor runs TODAY w/o clear role separation — human-level order FIRST ("מחוץ למערכת"). Deliverable #1 = deep presentation → Tom (order in his head), then employee version. System linkage / drift / realignment = substrate, AFTER. Interview must also cover no-screen physical work (⊥ system-biased harvest).
- home: `docs/org/` (this repo). Authority only after Tom merge (CLAUDE.md: "no new authority docs w/o Tom approval").
- single source: on approval supersedes scattered org facts — `docs/playbook/operator-playbook-he.md` → derived view; `gt-factory-os/docs/integrations/downstream_ownership_matrix.md` §Human responsibilities + `docs/phase8/ux/USER_ROLES_AND_CONTEXTS.md` → point here. ⊥ second writable org source.
- scope: whole company — factory-ops, office/bookkeeping, planning/procurement, delivery, marketing-sales, finance, tech/AI. Deep system-linkage only where system exists (routes / enums / skills). ⊥ invent links to systems that do not exist. `sales` module = declared DRAFT (`docs/decisions/modules/sales-declaration.md`) — map references it, ⊥ duplicates it.
- ⊥ HR-sensitive: salary, contracts, evaluations, personal data ∉ this repo. Roster = name + position + bindings only.
- ⊥ code/schema changes in this corridor. System-realignment items → `open_decisions` → separate tranches via `AI_BRAIN_ROUTER.md`.
- done gate: ∀ state-machine transition (16 machines) & ∀ portal route (77, `route-manifest.json`) & ∀ operating skill → exactly 1 accountable + defined handoff; drift check = 0 dangling refs, 0 silent contradictions. Reported N/N.
- acceptance: 10 real scenarios → map answers who / what / where-in-system in 1 lookup.
- update protocol (default; Tom ratifies via OD-6): change = Claude-authored PR → Tom written approval (merge). Drift check ∀ PR + weekly. ⊥ direct-to-main.
- lang: map core = English ids matching system literals verbatim; human views = Hebrew.
- ? OD-1 Doreen: bookkeeper persona on `planner` role — resolve in interview.
- ? OD-8 SOP distribution channel: print | WhatsApp | portal page.
- ? OD-7 gt-axis-* empty registries: recommend point-to-map, retire scaffold. Tom call.
- ? roster completeness: hiring active — add-person protocol in README covers.

## §I

- file: `docs/org/org_map.yaml` → machine core. Schema v1 documented in file header.
- file: `docs/org/README.md` → corridor charter: authority status, update + add-person protocol, consumers.
- file: `docs/org/views/*.md` → derived Hebrew views (roster, responsibility matrix, per-person SOP). Generated from map. ⊥ hand-edit.
- check: drift check v1 = `source-of-truth-auditor` dispatch over map vs live inventories (`gt-factory-os-portal/docs/portal-os/route-manifest.json`, `app_users` roles, migration enums, `.claude/skills/`). Script only if skill threshold met (`docs/phase8/decisions/STEP4-SKILLS-DECISION.md`).
- consumers: brain agents (boot step 6+ when routed to org questions), operating skills (`daily-ops-guardian`, `procurement-planning`, `plan-production-14d`, `daily-delivery-dispatch`, `goods-receipt-from-invoice`, `route-print-pack`), Tom, team via views.

## §V

V1: ∀ transition ∈ org_map.processes → exactly 1 `accountable` (person-id | role-id) & named `handoff`. 0 orphans.
V2: ∀ ref (route, system_role, enum value, skill, person, module) → resolves against live inventory. 0 dangling.
V3: ∀ persona → exactly 1 system_role; persona↔role capability mismatch → explicit `open_decisions` entry. ⊥ silent.
V4: map mutation only via PR + Tom written approval. ⊥ direct-to-main. ⊥ agent self-approval.
V5: HR-sensitive fields ∉ `docs/org/**`.
V6: views derived from map only. Hand-edited view = drift.
V7: system↔map divergence → `open_decisions` entry routed to Tom. ⊥ silent auto-fix in either direction.
V8: ∀ open_decisions entry → owner=Tom, dated, options listed. Resolved → move to `decision_log` with date. ⊥ delete.

## §T

id|status|task|cites
T1|~|corridor skeleton: SPEC + README + org_map.yaml schema|V4
T2|~|harvest current truth → map: 4 people, 4 roles, 7 personas, 21 processes, 16 state machines, surfaces, skills (system exam 2026-07-21)|V2,V3
T3|~|staged redesign interview S0-S5 with Tom (protocol: README) — resolves ∀ OD incl. OD-5 core; fills accountable ∀ process incl. no-screen physical work|V1,V3,V8
T4|.|drift check v1 run → first N/N report vs route-manifest + enums + skills|V1,V2
T5|.|derive Hebrew views: roster, matrix, per-person SOP v2 (playbook superseded in place, history preserved)|V5,V6
T6|.|10-scenario acceptance drill with Tom|—
T7|.|consumer wiring: propose CLAUDE.md pointer (Tom sole writer) + skill read-paths|V4
T8|.|realignment backlog: ∀ resolved OD → tranche/lane routing per AI_BRAIN_ROUTER.md|V7
T9|.|deep presentation → Tom: RTL Hebrew artifact — domain map, role card per person, handoff diagram, escalation ladder, before/after|V5
T10|.|employee version: per-person one-pagers + team deck; rollout Doreen/Denis/Maxim/Adi|V5,V6
T11|~|world-research (Tom-requested): owner-bottleneck, EOS visionary/integrator, single-point accountability → §R; grounds OD-9 + presentation|—
T12|~|intake questionnaire v2 (deepen pass): person-centric, PRE-FILLED from Tom brief, seams chapter, Tom↔Alex chapter, system-gaps chapter|V5

order (recalibrated 2026-07-21): T1→T2→T3→**T9→T10**, then T4→T8 (system-realignment wave).

## §B

id|date|cause|fix
