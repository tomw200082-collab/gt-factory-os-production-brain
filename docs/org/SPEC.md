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

## §R — research log (2026-07-21, Tom-requested: owner-bottleneck / Alex transition)

R1: EOS Accountability Chart — seats-first; exactly 1 accountable per seat; person MAY hold 2 seats, seat ⊥ 2 owners; fit = GWC (gets/wants/capacity). [Wickman, *Traction* 2011; eosworldwide.com/glossary]
R2: Visionary seat = big ideas/R&D, creative problem-solving, major external relationships, culture, selling big deals. Integrator seat = LMA, P&L/plan execution, integrating functions, removing obstacles, day-to-day tie-breaking. Maps 1:1 → Alex=Visionary, Tom=Integrator. [Wickman & Winters, *Rocket Fuel* 2015; eosworldwide.com/visionary-vs-integrator]
R3: Visionary failure mode = "in the weeds", follow-through weak, growth caps at his capacity; cure = "let go of the vine". Exactly Tom's problem statement on Alex. [eosworldwide.com/blog/let-go-of-the-vine]
R4: 5 V/I rules: monthly Same Page Meeting · no end runs (team ⊥ bypass to Visionary) · Integrator breaks day-to-day ties · Visionary ON not IN · mutual domain respect. [eosworldwide.com/the-5-rules]
R5: Monkey mechanism: ∀ "leave it with me" → next-move jumps to boss's back → boss = bottleneck, work stalls. = "אחריות שהוא לוקח לא מתבצעת". Cure: ∀ monkey → named owner; degrees-of-initiative ladder (act-then-advise). [Oncken & Wass, HBR 1974/1999]
R6: E-Myth: positions chart first, position contract per seat, staff seats out from under owner over time — valid even when 1 person temporarily holds several seats. [Gerber, *E-Myth Revisited* 1995]
R7: Greiner: delegation works only when top "manages by exception based on periodic reports". [HBR 1972/1998]
R8: Adizes Founder's Trap: "tasks are delegated rather than responsibilities"; cure = delegate responsibility WITH authority, judge on outputs. [Adizes, *Managing Corporate Lifecycles*]
R9: Single-A: shared accountability disappears; RACI exactly-1-A; Apple DRI ("never any confusion who is responsible"); RAPID one Decide per decision. [Atlassian RACI; Lashinsky *Inside Apple* 2012; Rogers & Blenko "Who Has the D?" HBR 2006]
R10: Transition instruments: Delegate-and-Elevate 4-quadrant audit of everything Alex touches, ≥1 handoff / 90d, target ≥80% time top-quadrants; weekly scorecard 5-15 owned numbers + L10-style meeting → Alex "plays from above" by exception. [eosworldwide.com/delegate-and-elevate, /level-10-meeting]
R11: Food-factory legitimacy: BRCGS-class standards REQUIRE documented org chart + 1 accountable + named deputy per function → present redesign to team as compliance-grade professionalization, not sidelining anyone. [brcgs.com guidance doc 63857]
R12: ⊥ established seat layout for ~7-person beverage plant — derive seats from GT's own processes (this corridor). Flags: EOS "3% of population" = vendor claim; term "visionary-dependence" UNSOURCED (McKeown concept verified).

(research pass 2 — SoD / TPM / 5S / leads / checklists, 2026-07-21:)

R13: SoD triad authorize|custody|record — ⊥ one person holds 2 of 3. AICPA/CIMA publish a 4-person SoD chart (workable at GT scale). Small-entity compensating controls = owner review + dual sign-off thresholds (COSO smaller-companies guidance). ACFE 2024: orgs <100 employees median fraud loss $141K; missing controls most-cited weakness. → Adi records+reconciles; Tom approves+releases payments + reads bank feed independently; stock counter ≠ adjustment approver (matches count_freezes flow). [AICPA/CIMA 4-person chart; COSO; ACFE RTTN 2024]
R14: TPM autonomous maintenance (jishu hozen) — production operator owns first-line care (clean, inspect, lubricate, tighten), escalates beyond; JIPM 7-step. → Denis owns machine first-line. [Nakajima, *Introduction to TPM*, 1988]
R15: 5S named-owner-per-zone + Sustain audit cadence (Toyota daily/weekly/monthly audits). → Denis owns RM+filling zones; Maxim owns FG zone; Tom monthly walk-through. [Hirano, *5 Pillars of the Visual Workplace*, 1995; lean.org lexicon]
R16: Lead response: contact within 1h → ~7x qualification odds vs 1h later, >60x vs 24h+ (1.25M-lead dataset; HBR **March** 2011 — not Dec); 2007 LRM study: contact odds 100x at 5min vs 30min. ⊥ cite "quality drops 80% after 5min" (untraceable). → Doreen lead SLA: first response within the hour when possible; same-day hard ceiling. [Oldroyd et al., HBR 2011/03; leadresponsemanagement.org]
R17: Short killer-item checklists beat long SOPs: WHO 19-item surgical checklist → deaths 1.5%→0.8% (~-47% rel), complications 11%→7% (NEJM 2009, 8 hospitals); aviation read-do cards. → per-person "3 iron rules" format; full SOPs = training only. [Gawande, *Checklist Manifesto* 2009; Haynes et al., NEJM 360:491]

→ feeds: questionnaire ch.5 structure (done), OD-9 resolution frame, T9 presentation skeleton (seats chart, V/I split, monkey rule, scorecard).

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
T11|x|world-research ×2 (Tom-requested): owner-bottleneck/EOS pass 1 → R1-R12; SoD/TPM/5S/leads/checklists pass 2 → R13-R17|—
T12|x|intake questionnaire v2+v3 (deepen ×2): person-centric, PRE-FILLED, then full proposal layer — every field ships a cited recommendation w/ accept/edit; given/suggested/confirmed states; iron-rules + V/I commitments|V5

T13|~|floor proposals P-1..P-4 (`PROPOSALS.md`): production-order loop (DIRECTION_AGREED), receiving square, daily briefing, dead-stock — Tom approval per item → realignment wave|V4

order (recalibrated 2026-07-21): T1→T2→T3→**T9→T10**, then T4→T8+T13 (system-realignment wave).

## §B

id|date|cause|fix
