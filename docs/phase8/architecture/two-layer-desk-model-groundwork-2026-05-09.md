# Architecture iteration groundwork — Two-layer Desk model (2026-05-09)

> **Type:** design / audit pack. **Plan-only.** No agent files created. No commands created. No skills created. No ROUTER mutation. No registry rewrite. No runtime/code changes.
>
> **Purpose:** scope and structure a future two-layer agent architecture for GT Factory OS so that any commitment to it is informed, reversible, and cleanly piloted before mass migration. Output of Phase 8 Run F Wave 4 Phase B per Tom's PROCEED-WITH-CONSTRAINTS directive 2026-05-09.
>
> **Author:** factory-os-governor (proposes), under Tom approval. Writes only proposals; does not change current dispatch behavior.
>
> **Authority status:** proposal / read-only. Does not supersede `CLAUDE.md`, `EXECUTION_POLICY.md`, `AI_BRAIN_ROUTER.md`, `AGENT_REGISTRY.md`, or `COMMAND_REGISTRY.md`. Until Tom approves a pilot, the live system continues to operate under the current single-layer agent model.
>
> **Out of scope (hard boundaries):**
> - No new agents
> - No new skills
> - No ROUTER edit
> - No registry rewrite
> - No runtime work
> - No code changes
> - No behavior change

---

## Section 1 — Current artifact inventory

The inventory captures the live state on disk at 2026-05-09. The status column is the conservative reading: `active` = currently dispatchable; `legacy-active` = dispatchable until Wave 6 deprecation per `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`; `parked` = not currently dispatched and waiting on Tom decision; `retirement-candidate` = redundant with a successor, no value in keeping after Wave 6.

### 1.1 Agents (`PRODUCTION/.claude/agents/`, 17 files)

| # | Agent | Class | Current lane | Status | Successor (if legacy) | Notes |
|---|---|---|---|---|---|---|
| 1 | `factory-os-governor` | core | governance | active | — | Successor to `governor`. Read-only. Go/no-go decisions. |
| 2 | `release-verifier` | core | release-gate | active | — | Pre-merge / pre-deploy verification. Read-only. |
| 3 | `source-of-truth-auditor` | core | source-of-truth | active | — | Cross-doc drift classification. Read-only. |
| 4 | `ux-flow-architect` | UX | ux-audit | active | — | End-to-end operational flow. Read-only. |
| 5 | `interaction-design-specialist` | UX | ux-audit | active | — | Buttons, forms, undo/cancel/reversal. Read-only. |
| 6 | `visual-system-designer` | UX | ux-audit | active | — | Tokens, layout, typography. Read-only. |
| 7 | `ux-content-state-designer` | UX | ux-audit | active | — | Microcopy, status terms, error messages. Sole writer of `portal_ux_standard.md`. |
| 8 | `accessibility-usability-auditor` | UX | ux-audit | active | — | WCAG, ARIA, keyboard nav. Read-only. |
| 9 | `backend-db-executor` | execution | backend-db | active | — | Successor to `executor-w1`. write_with_approval. |
| 10 | `portal-production-executor` | execution | portal | active | — | Successor to `executor-w2`. write_with_approval. |
| 11 | `integration-boundary-executor` | execution | integration | active | — | Successor to `executor-w4`. Sole frozen-flag gatekeeper. write_with_approval. |
| 12 | `ops-docs-curator` | execution | docs | active | — | New role, no executor-era predecessor. write_with_approval (proposes archive moves). |
| 13 | `executor-w1` | legacy | backend-db | legacy-active | `backend-db-executor` | Wave 6 deprecation candidate. |
| 14 | `executor-w2` | legacy | portal | legacy-active | `portal-production-executor` | Wave 6 deprecation candidate. |
| 15 | `executor-w4` | legacy | integration | legacy-active | `integration-boundary-executor` | Wave 6 deprecation candidate. |
| 16 | `governor` | legacy | governance | legacy-active | `factory-os-governor` | Wave 6 deprecation candidate. |
| 17 | `verifier` | legacy | release-gate | legacy-active | n/a — kept indefinitely | `verifier.md` is preserved as the post-executor PASS/FAIL verifier (per `AGENT_REGISTRY.md`). |

### 1.2 Commands (`PRODUCTION/.claude/commands/`, 15 files)

| # | Command | Primary agent | Type | Status |
|---|---|---|---|---|
| 1 | `/button-logic-review` | `interaction-design-specialist` | UX audit | active |
| 2 | `/design-system-check` | `visual-system-designer` | UX audit | active |
| 3 | `/empty-error-state-audit` | `interaction-design-specialist` | UX audit | active |
| 4 | `/operator-task-simulation` | `ux-flow-architect` | UX audit | active |
| 5 | `/screen-scorecard` | UX agents (all 5) | UX audit | active |
| 6 | `/ux-flow-audit` | `ux-flow-architect` | UX audit | active |
| 7 | `/ux-release-gate` | UX agents (all 5) | UX gate | active |
| 8 | `/production-go-no-go` | `factory-os-governor` | gate | active |
| 9 | `/release-check` | `release-verifier` | gate | active |
| 10 | `/source-truth-audit` | `source-of-truth-auditor` | audit | active |
| 11 | `/docs-hygiene-check` | `ops-docs-curator` | audit | active |
| 12 | `/gate-close` | `factory-os-governor` | closure | active |
| 13 | `/incident-triage` | `integration-boundary-executor` | triage | active |
| 14 | `/integration-dry-run` | `integration-boundary-executor` | dry-run | active |
| 15 | `/portal-pr-review` | `portal-production-executor` | review | active |

### 1.3 Authority + governance docs (`PRODUCTION/` root, 11 files)

| Doc | Owner | Status | Notes |
|---|---|---|---|
| `CLAUDE.md` | Tom (sole writer) | authoritative | Boot kernel; locked decisions. |
| `EXECUTION_POLICY.md` | `ops-docs-curator` (under governance) | authoritative | Operating law. Run F Wave 4 lane-rename completed 2026-05-09. |
| `CURRENT_STATE.md` | `ops-docs-curator` (under governance) | authoritative | Live runtime gate status. Run F Wave 4 Hole 2 cleanup completed 2026-05-09. |
| `ACTIVE_NOW.md` | `ops-docs-curator` | authoritative on today's dispatch context only | Run F Wave 4 Hole 2 cleanup completed 2026-05-09. |
| `WORKSPACE_MAP.md` | `ops-docs-curator` (under governance) | authoritative | Repo geography. |
| `AI_BRAIN_ROUTER.md` | `factory-os-governor` (proposes), Tom approves | authoritative | Routing decision engine. |
| `AGENT_REGISTRY.md` | `ops-docs-curator` (under governance) | authoritative | 17/17 agents indexed; integrity verified 2026-05-09. |
| `COMMAND_REGISTRY.md` | `ops-docs-curator` (under governance) | authoritative | 15/15 commands indexed; integrity verified 2026-05-09. |
| `VERDICT_GLOSSARY.md` | `ops-docs-curator` | authoritative | Verdict tokens with semantics. `HOLD` collision documented, not renamed. |
| `AGENT_TEMPLATE.md` | `ops-docs-curator` | template | Required structure for new agents. |
| `MODULE_TEMPLATE.md` | `ops-docs-curator` | template | Required declaration for new modules. |

### 1.4 User-level skills (`C:/Users/tomw2/.claude/skills/`)

User-level skills are not part of the PRODUCTION repo; they are local to Tom's machine. They are listed here because some are factory-os-relevant.

| Skill | Factory-OS scope | Current trigger | Notes |
|---|---|---|---|
| `factory-os-advance` | yes | "advance the project", "תקדם את הפרוייקט" | Orchestrator. Already exists. |
| `factory-os-autonomous-builder` | yes | classifying pasted Claude messages tied to factory-os | Governor + prompt-writer. Already exists. |
| `daily-inventory-agent` | yes | daily inventory work | Already exists. |
| `daily-inventory-ops` | yes | daily inventory operations | Already exists. |
| `finished-goods-inventory-update` | yes | FG inventory updates | Already exists. |
| `lionwheel-route-invoices` | yes | LionWheel route invoices | Already exists. |
| `stock-event-accuracy-audit` | yes | stock event accuracy auditing | Already exists. |
| `adversarial-system-audit` | yes | adversarial audits | Already exists. |
| `expert-second-opinion` | no (general) | general second opinions | Not factory-os specific. |
| `notebooklm` | no (general) | general notebooks | Not factory-os specific. |

### 1.5 Slash-skills via PRODUCTION

The PRODUCTION-side slash-commands listed in §1.2 are operationalized via `.claude/commands/*.md` files. There is **no** `PRODUCTION/.claude/skills/` directory; `factory-os-*` skills live at user level only.

### 1.6 Status summary

- **17 agents on disk → 12 production + 5 legacy.** Production set is complete and stable; legacy set runs on a deprecation timeline.
- **15 commands on disk → all production.** No legacy commands.
- **11 authority docs at root → all in good standing post-Hole-2 cleanup.**
- **No PRODUCTION-side skills directory exists today.** Future skill packs are an open question.
- **Retirement candidates after Wave 6:** `executor-w1`, `executor-w2`, `executor-w4`, `governor`. (`verifier` is kept indefinitely.)

---

## Section 2 — Proposed Desk taxonomy

A "Desk" is a Layer-1 authority boundary. Each Desk owns a clear domain, has scoped allowed-paths and verification gates, and routes its own sub-agents (Layer 2) to do the work. Desks do not implement work directly; they classify, gate, and route within their domain. (This separates dispatch logic from execution, and makes per-domain skill packs possible.)

The proposed initial Desk set (per Tom's directive):

1. **backend-db-truth desk**
2. **portal-operator-ux desk**
3. **integrations-boundary desk**
4. **planning-procurement desk**
5. **finance-economics desk**
6. **governance-docs-router desk**

The audit below confirms the split holds; one minor refinement is noted (planning-procurement currently has no dedicated execution sub-agent — the planning engine work has historically been done inside backend-db-truth and portal-operator-ux territory).

### 2.1 backend-db-truth desk

| Field | Value |
|---|---|
| **Authority boundary** | All Postgres schema, migrations, pgTAP, ledger semantics, balance projections, jobs, fixtures, BOM modeling at the schema level. Sole authority on emitting `RUNTIME_READY(form)` signals. |
| **Owns** | `gt-factory-os/api/**`, `gt-factory-os/db/**`, `gt-factory-os/scripts/**` (excl. archive). Authoritative on stock_ledger, balance_anchors, current_balances, projection table, BOM cluster. |
| **Does not own** | Portal UI, integration runtime handlers (those have skeletons here but contracts live in integrations-boundary desk), dashboard UI, planning engine UX, finance / cost rollup logic, governance docs. |
| **Input triggers** | Any request that touches schema, migrations, ledger, projections, server-side handlers, scheduled jobs (Postgres-side), import scripts. |
| **Output contract** | Migration file + pgTAP test + parity verification + RUNTIME_READY signal entry (when applicable) + handoff packet to portal-operator-ux. |
| **Allowed handoffs** | → portal-operator-ux (when a backend surface is ready for portal authoring); → integrations-boundary (when an integration handler stack is ready for contract tightening); → governance-docs-router (for source-of-truth or release-gate review). |
| **Forbidden overlaps** | No portal source authorship; no integration external-write authoring; no governance doc edits (proposals only via ops-docs-curator); no flag flips. |
| **Verification gates** | Migration applied to live DB; pgTAP green; parity gate green; rebuild_verifier=0; RUNTIME_READY emitted with full evidence (or explicit reason for skipping). |

### 2.2 portal-operator-ux desk

| Field | Value |
|---|---|
| **Authority boundary** | All canonical portal authoring, route tree, form components, TanStack Query mutations/queries, post-submit/loading/error states, Hebrew/RTL register entries (Tom-approved only), shadcn/ui wiring. UX audits (read-only) live here too. |
| **Owns** | `gt-factory-os-portal/src/**`, `window2-portal-sandbox/src/**`, `portal_ux_standard.md` (writer = ux-content-state-designer). |
| **Does not own** | Backend code, schema, migrations, integration handlers, dashboard read-model contracts, planning engine logic, integration external writes. |
| **Input triggers** | Any user-visible portal surface change, UX audit request, portal PR review, UX release gate. |
| **Output contract** | Portal source diff + handoff packet from UX agents (when authoring a UX-changed surface) + Playwright real-HTTP smoke + role-matrix walkthrough + active_mode.json mode-exit row. |
| **Allowed handoffs** | → backend-db-truth (when a portal change requires a new contract — emits `assumption_failure` if no `RUNTIME_READY(form)`); → integrations-boundary (for portal mirror routes); → governance-docs-router (for portal release gate). |
| **Forbidden overlaps** | No backend authorship; no schema; no integration external writes; no flag flips; no Hebrew copy without Tom register entry; no FLOW-003-style structural changes without explicit Tom approval. |
| **Verification gates** | Typecheck + build + lint + Playwright smoke green; `RUNTIME_READY(form)` present for backend-bound surfaces; UX handoff packet exists for any user-visible change; `active_mode.json` mode-exit row landed. |

### 2.3 integrations-boundary desk

| Field | Value |
|---|---|
| **Authority boundary** | All external integration contract authoring + dry-run execution + frozen-flag gatekeeping (LionWheel, Shopify, Green Invoice, Supabase Edge Functions, scheduled jobs, export pipelines). Sole writer of `gt-factory-os/docs/integrations/**` and `gt-factory-os/docs/contracts/**`. |
| **Owns** | Contract docs under `docs/integrations/` and `docs/contracts/`; integration handler skeletons under `gt-factory-os/api/src/integrations/**`; the `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` and `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` frozen-flag gate. |
| **Does not own** | Stock ledger writes (those are backend-db-truth via the LionWheel pickup → ledger decrement chain); portal UI; schema migrations (those are backend-db-truth); finance/cost rollup. |
| **Input triggers** | Frozen-flag flip request, integration contract change, dry-run request, incident on a sync/export job. |
| **Output contract** | Contract diff + dry-run record under `docs/phase8/dry-runs/` + freshness log entry + soak-window evidence (≥24h) + RUNTIME_READY signal where applicable. |
| **Allowed handoffs** | → backend-db-truth (for handler implementation under contract); → governance-docs-router (for release gate, source-of-truth on integration contracts). |
| **Forbidden overlaps** | No DB migration authorship; no portal source; no direct ledger write attempts; no frozen-flag flip without Tom written approval + dry-run + ≥24h soak + RUNTIME_READY; no live writes against external APIs without explicit Tom approval. |
| **Verification gates** | Dry-run PASS evidence cited; soak ≥24h documented; RUNTIME_READY emitted for the relevant scope; frozen flag gate state explicitly stated; no silent flag flip. |

### 2.4 planning-procurement desk

| Field | Value |
|---|---|
| **Authority boundary** | Planning engine logic, recommendations (purchase + production), BOM/recipe modeling at the engine level, demand layer, planning corridor authoring orchestration. **Does not currently have a dedicated execution sub-agent**; the work has been carried by backend-db-truth (engine functions, migrations) and portal-operator-ux (planning surfaces). |
| **Owns (proposed)** | Planning engine functions in Postgres (`fn_compute_fg_net_requirements`, `fn_compute_component_net_purchase`, `fn_explode_bom_to_components`, `v_planning_demand`, `fn_generate_*_recommendations`); planning corridor authoring orchestration (multi-tranche cycles); BOM head/version/lines truth (locked CLAUDE.md decisions). |
| **Does not own** | Portal UI for planning (lives in portal-operator-ux); schema authoring for planning tables (lives in backend-db-truth); integration runtime contracts (lives in integrations-boundary); cost rollup (lives in finance-economics). |
| **Input triggers** | Planning corridor cycle dispatch, BOM repair, planning-engine bug fix, planning recommendation contract change, forecast freeze/publish change. |
| **Output contract** | Planning engine migration + pgTAP + reproducibility proof (byte-equal) + planning run substrate update + planning corridor handoff packet. |
| **Allowed handoffs** | → backend-db-truth (for the actual migration authoring); → portal-operator-ux (for the planning surface authoring); → finance-economics (for cost rollup integration). |
| **Forbidden overlaps** | No portal source authorship directly; no schema migrations directly; no integration external writes; no relaxation of A3/A4 locked decisions without Tom written approval. |
| **Verification gates** | A3/A4 locked invariants preserved; FG netting inbound = 0 preserved; planning run reproducibility (byte-equal) preserved; demand bucketing semantics preserved (all open orders to current ISO week per A3). |
| **Status note** | **No current dedicated execution sub-agent.** Work has been done by backend-db-truth + portal-operator-ux. The planning-procurement desk is largely an **orchestration / authority abstraction** today; it would need a dedicated sub-agent only if planning corridor cycles get fast enough that cross-desk coordination becomes the bottleneck. |

### 2.5 finance-economics desk

| Field | Value |
|---|---|
| **Authority boundary** | Cost rollup (Gate 5 Phase 10, deferred), Green Invoice supplier-price ingest semantics, money-domain precision/scale (locked principle in CLAUDE.md; concrete values pending), pricing audit trail. |
| **Owns (proposed)** | Cost rollup engine (when authored), Green Invoice line-item-to-component mapping logic (validation rules, not auto-creation), money-domain precision lock-in. |
| **Does not own** | Stock ledger (lives in backend-db-truth); supplier-side integration calls (live in integrations-boundary); planning engine (lives in planning-procurement); portal UI for finance views (lives in portal-operator-ux). |
| **Input triggers** | Cost rollup activation request, Green Invoice price-feed validation rule change, money-domain precision pin request. |
| **Output contract** | Cost rollup migration + pgTAP + manual reconciliation match (Phase 10 stretch criterion); Green Invoice mapping validation rules + threshold rules. |
| **Allowed handoffs** | → backend-db-truth (for migration authoring); → integrations-boundary (for Green Invoice contract); → governance-docs-router (for source-of-truth on locked money-domain values). |
| **Forbidden overlaps** | No auto-creation of components from Green Invoice line items (forbidden in CLAUDE.md); no auto-update of supplier prices without threshold rules; no relaxation of audit-trail invariants. |
| **Verification gates** | Cost rollup matches manual reconciliation (Phase 10 exit criterion); Green Invoice price changes pass mapping-quality + threshold gates before commit; pricing audit trail preserved on every price change. |
| **Status note** | **No current dedicated execution sub-agent.** Cost rollup is post-Gate-5 stretch. Green Invoice mapping is partially in integrations-boundary today. The finance-economics desk would acquire dedicated work only when Phase 10 cost rollup activates or Green Invoice validation rules become decision-grade. |

### 2.6 governance-docs-router desk

| Field | Value |
|---|---|
| **Authority boundary** | All governance, source-of-truth, release-gate, docs hygiene, archive curation, ROUTER decisions, agent/command registry curation, dispatch arbitration, frozen-flag gate verdicts. |
| **Owns** | `CLAUDE.md` (Tom sole writer; this desk proposes patches), `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, `ACTIVE_NOW.md`, `WORKSPACE_MAP.md`, `AI_BRAIN_ROUTER.md`, `AGENT_REGISTRY.md`, `COMMAND_REGISTRY.md`, `VERDICT_GLOSSARY.md`, all of `PRODUCTION/docs/**` (except authority docs), `PRODUCTION/archive/**`. |
| **Does not own** | Any product runtime code; any schema; any integration external write; any portal source. |
| **Input triggers** | Pasted Claude update, approval request, gate close, release request, drift audit, docs hygiene check, archive move, ROUTER edit proposal. |
| **Output contract** | Verdict block (PROCEED / PROCEED_WITH_CONSTRAINTS / HOLD / SWITCH_LANE / NEW_MODULE_REQUIRED) + structured router output (when classifying input) + audit/closure/hygiene report (when running a command). |
| **Allowed handoffs** | → any other desk (this is the dispatcher); ← any other desk (for review / arbitration). |
| **Forbidden overlaps** | No code authorship; no schema authorship; no portal authorship; no integration external write; no autonomous push / merge / deploy (Tom only). |
| **Verification gates** | Authority hierarchy preserved; locked decisions not relaxed; cross-doc drift classified (STALE/CONFLICTING/ORPHANED/SHADOW); release gate applied before merge; archive integrity (INDEX.md per archived subdir). |

---

## Section 3 — Proposed Sub-agent matrix

Layer-2 sub-agents are the actual workers. Each sub-agent has a tight repeated operating role within a single Desk. Most current agents map cleanly to a sub-agent under a Desk; a few open questions are flagged.

### 3.1 backend-db-truth desk → sub-agents

| Name | Role | Owns | Does not own | Inputs | Outputs | Required skills/checklists | Allowed commands | Handoff target | Stop conditions | Duplication risk | When |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `backend-db-executor` | schema / migration / handler / pgTAP / RUNTIME_READY | `api/**`, `db/**`, `scripts/**` | portal, integration runtime, governance docs | migration request, handler request, pgTAP test, parity verifier | migration file, pgTAP, parity gate evidence, RUNTIME_READY signal | FR1→write→FR2 bracket; ledger immutability checklist; rebuild_verifier discipline | none today; future: `/release-check`, `/integration-dry-run` consumer | portal-operator-ux (on RUNTIME_READY); integrations-boundary (handler under contract) | direct ledger write; DROP COLUMN/TABLE in prod; flag flip | low (sole production successor of executor-w1) | now |
| `executor-w1` (legacy) | same as above | same | same | same | same | same | same | same | same | medium (overlaps backend-db-executor; Wave 6 archives this) | now (until Wave 6); after = retire |

Future possible sub-agents under this desk (NOT proposed for creation now):
- `migration-author` — narrow sub-role for pure migration writing without handler authoring.
- `pgtap-author` — narrow sub-role for test authoring.
- These are over-decomposition unless the desk grows; flagged for awareness only.

### 3.2 portal-operator-ux desk → sub-agents

| Name | Role | Owns | Does not own | Inputs | Outputs | Required skills/checklists | Allowed commands | Handoff target | Stop conditions | Duplication risk | When |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `portal-production-executor` | canonical portal authoring | `gt-factory-os-portal/src/**`, `window2-portal-sandbox/src/**` | backend, schema, integration, governance docs | UX handoff packet, RUNTIME_READY(form), Tom-approved Hebrew register entry | portal source, Playwright smoke evidence, active_mode.json exit row | portal_ux_standard.md compliance; FLOW-003 boundary; route normalization rules | `/portal-pr-review` | backend-db-truth (on contract gap); governance (on release gate) | missing UX handoff; missing RUNTIME_READY for backend-bound surface; missing Tom Hebrew register entry; FLOW-003 without Tom approval | low (sole production successor) | now |
| `executor-w2` (legacy) | same | same | same | same | same | same | same | same | same | medium (Wave 6 archives this) | now (until Wave 6); after = retire |
| `ux-flow-architect` | end-to-end flow audit | (read-only); produces handoff packets only | portal source; backend; integration | route name, surface scope, audit request | findings table, handoff packet | UX_OPERATING_PRINCIPLES.md compliance | `/ux-flow-audit`, `/operator-task-simulation`, `/ux-release-gate` | portal-production-executor (handoff) | P0 finding → escalate to governance; missing RUNTIME_READY for backend-bound surface | low (read-only; parallel-safe with other UX agents) | now |
| `interaction-design-specialist` | buttons/forms/states audit | (read-only); decision-grade vs flow-completion classification | portal source; backend | route, action surface, audit request | findings, handoff packet | INTER-NNN finding codes | `/button-logic-review`, `/empty-error-state-audit`, `/operator-task-simulation`, `/ux-release-gate`, `/ux-flow-audit` | portal-production-executor | P0 → governance | low | now |
| `visual-system-designer` | visual hierarchy / tokens audit | (read-only); proposes system rules, never one-off decoration | portal source; tokens; backend | route, audit request | VISUAL-NNN findings | design tokens; shadcn/ui conventions | `/design-system-check`, `/ux-release-gate`, `/screen-scorecard` | portal-production-executor | one-off decoration without system rule → reject | low | now |
| `ux-content-state-designer` | microcopy / status terms / Hebrew clarity | sole writer of `portal_ux_standard.md` | portal source code; backend | copy change request, register entry proposal | copy diff (proposal-only on portal_ux_standard.md) | Hebrew/English register direction; CONTENT-NNN finding codes | `/ux-flow-audit`, `/empty-error-state-audit`, `/button-logic-review`, `/ux-release-gate` | portal-production-executor | Hebrew without Tom register entry → halt | low | now |
| `accessibility-usability-auditor` | WCAG / ARIA / keyboard nav | (read-only); A11Y-NNN finding codes | portal source; backend | route, audit request | findings, handoff packet | WCAG basics; ARIA name-role-value; screen-reader announcements | `/empty-error-state-audit`, `/button-logic-review`, `/ux-release-gate` | portal-production-executor | none beyond standard | low | now |

### 3.3 integrations-boundary desk → sub-agents

| Name | Role | Owns | Does not own | Inputs | Outputs | Required skills/checklists | Allowed commands | Handoff target | Stop conditions | Duplication risk | When |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `integration-boundary-executor` | integration contract authoring + dry-run + frozen-flag gatekeeping | `docs/integrations/**`, `docs/contracts/**`, `api/src/integrations/**` (skeleton only) | DB migrations, portal source | LionWheel/Shopify/Green Invoice contract change, dry-run request, frozen-flag flip request | contract diff, dry-run record under `docs/phase8/dry-runs/`, freshness log append | LionWheel pickup → ledger decrement locked decision; Shopify v2 phase plan; Green Invoice validation rules; frozen-flag prerequisites | `/integration-dry-run`, `/incident-triage` | backend-db-truth (handler implementation); governance (release gate) | flag flip without Tom written approval + dry-run + ≥24h soak + RUNTIME_READY; direct ledger write attempt; non-terminal LionWheel status trigger | low (sole production successor) | now |
| `executor-w4` (legacy) | same | same | same | same | same | same | same | same | same | medium (Wave 6 archives) | now (until Wave 6); after = retire |

Future possible sub-agents (NOT proposed now):
- `lionwheel-runtime-watcher` — monitors LionWheel chain health, parses live samples, flags schema drift.
- `shopify-bridge-watcher` — monitors Shopify bridge, flags bridge-starvation patterns.
- Defer until Sunday cutover (2026-05-10) closes and the monitoring corridor is settled.

### 3.4 planning-procurement desk → sub-agents

| Name | Role | Owns | Does not own | Inputs | Outputs | Required skills/checklists | Allowed commands | Handoff target | Stop conditions | Duplication risk | When |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **(none currently)** | — | — | — | — | — | — | — | — | — | — | not now — defer until decoupling needed |

The planning-procurement desk currently routes all execution work to backend-db-truth (engine functions, migrations, demand layer) and portal-operator-ux (planning surfaces). This is acceptable while the planning corridor is on a single dispatch cadence. A dedicated planning sub-agent would only justify itself if multi-cycle planning corridors run in parallel with backend or portal work and create lane-collision risk. Today they don't.

### 3.5 finance-economics desk → sub-agents

| Name | Role | Owns | Does not own | Inputs | Outputs | Required skills/checklists | Allowed commands | Handoff target | Stop conditions | Duplication risk | When |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **(none currently)** | — | — | — | — | — | — | — | — | — | — | not now — defer until Phase 10 or decision-grade Green Invoice work activates |

Cost rollup is post-Gate-5 stretch (per A11). Green Invoice supplier-price evidence is partially handled by integrations-boundary today. There is no current finance work that justifies a dedicated sub-agent.

### 3.6 governance-docs-router desk → sub-agents

| Name | Role | Owns | Does not own | Inputs | Outputs | Required skills/checklists | Allowed commands | Handoff target | Stop conditions | Duplication risk | When |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `factory-os-governor` | go/no-go verdicts; lane control; arbitration | (read-only) | code, schema, portal, integration | pasted Claude update, approval request, ownership collision, contract_failure, assumption_failure | verdict block (PROCEED / PROCEED_WITH_CONSTRAINTS / HOLD / SWITCH_LANE / NEW_MODULE_REQUIRED), evidence under `docs/phase8/` | EXECUTION_POLICY.md compliance; CLAUDE.md tiebreakers | `/production-go-no-go`, `/gate-close` | any sub-agent | locked decision relaxation attempt; frozen-flag bypass attempt | low (read-only) | now |
| `release-verifier` | pre-merge / pre-deploy verification | (read-only) | code, schema, portal | PR/branch ready for merge or deploy | verdict (SAFE_FOR_HUMAN_REVIEW / CONDITIONALLY_SAFE / NOT_SAFE / BLOCKED) | git status check; changed-file scope; PR risk | `/release-check` | factory-os-governor (final go/no-go), Tom (deploy) | any code authorship attempt | low (read-only) | now |
| `source-of-truth-auditor` | cross-doc drift classification | (read-only) | edits to authority docs | drift audit request | drift report (STALE/CONFLICTING/ORPHANED/SHADOW with D-IDs); patch proposals | drift classification rules; D1–D10 scan IDs | `/source-truth-audit` | ops-docs-curator (apply patches under governor approval); Tom (CLAUDE.md changes) | CLAUDE.md violation suggested; unresolvable by hierarchy | low (read-only) | now |
| `ops-docs-curator` | docs hygiene; archive curation; authority doc patches under governance approval | `PRODUCTION/docs/**` (excl. authority), `PRODUCTION/archive/**` (proposes moves) | runtime code; backend; portal; integration; authority docs (proposes only) | hygiene scan request, archive move request, doc move proposal | hygiene report under `docs/phase8/hygiene/`; archive INDEX update; doc move/proposal | docs hygiene checklist; archive INDEX rules; flat-root regression rule | `/docs-hygiene-check` | factory-os-governor | authority doc edit without governor PROCEED; archive without proposal-first; deletion attempt | low | now |
| `governor` (legacy) | same as factory-os-governor | same | same | same | same | same | same | same | same | medium (Wave 6 archives) | now (until Wave 6); after = retire |
| `verifier` (legacy) | post-executor PASS/FAIL verifier | (read-only) | code | executor PASS claim | PASS/FAIL/BLOCKED/HOLD_FOR_TOM | locked-contract verification; success-evidence audit | (none defined) | factory-os-governor | none beyond standard | low (kept indefinitely per AGENT_REGISTRY note) | keep indefinitely |

---

## Section 4 — Skill Pack mapping

A "Skill Pack" is a domain-scoped checklist or reference artifact that a sub-agent must follow. Today, factory-os relevant skills live at user level (Tom's machine, `C:/Users/tomw2/.claude/skills/`). PRODUCTION-side has no skills directory. The mapping below proposes which sub-agent uses each existing skill, which mistakes each prevents, and whether each should be a skill, command, checklist, or reference doc.

| Existing artifact | Type today | Used by (proposed) | Trigger condition | Mistake prevented | Output improved | Recommended type | Status |
|---|---|---|---|---|---|---|---|
| `factory-os-advance` (skill) | user-level skill | governance-docs-router desk dispatcher | "advance the project", "תקדם את הפרוייקט" | Tom-side: silent inactivity; system-side: every-lane-parked dead-air | Concrete next operator action per active lane | **stays a skill** | exists |
| `factory-os-autonomous-builder` (skill) | user-level skill | governance-docs-router desk (specifically `factory-os-governor`) | classifying pasted Claude messages tied to factory-os | Misclassification; silent contract-gap healing; drift between windows | Reply that respects authority hierarchy | **stays a skill** | exists |
| `daily-inventory-agent` (skill) | user-level skill | planning-procurement OR portal-operator-ux desk (TBD by trigger) | daily inventory cycle | Inventory drift; missed daily ops | Daily inventory walk-through | **stays a skill** | exists |
| `daily-inventory-ops` (skill) | user-level skill | planning-procurement desk | daily inventory operations | Missed ops steps; out-of-order ops | Ordered ops execution | **stays a skill** | exists |
| `finished-goods-inventory-update` (skill) | user-level skill | backend-db-truth desk (FG balance projection) | FG balance update request | Stale FG `current_balances`; ledger drift | Reconciled FG inventory | **stays a skill** | exists |
| `lionwheel-route-invoices` (skill) | user-level skill | integrations-boundary desk (LionWheel-specific) | LionWheel route invoice request | Wrong combined-PDF order; missing credentials | Correct route invoice batch | **stays a skill** | exists |
| `stock-event-accuracy-audit` (skill) | user-level skill | backend-db-truth OR governance-docs-router desk | stock event audit request | Silent ledger drift; missed exception | Verified stock event accuracy report | **stays a skill** | exists |
| `adversarial-system-audit` (skill) | user-level skill | governance-docs-router desk | adversarial audit request | False-green; unverified PASS claims | Adversarial review evidence | **stays a skill** | exists |
| Pre-write FR1→write→FR2 bracket (in EXECUTION_POLICY.md §integration) | inline policy text | integration-boundary-executor | every integration artifact referencing migration filenames by number | W1↔integration migration-number race | Deterministic write window with directory verification | **could be a checklist file** if it grows beyond inline policy | exists as policy text; no separate file needed today |
| Ledger immutability rules (CLAUDE.md + SCHEMA_GUIDANCE) | inline policy text | backend-db-truth desk | every ledger-touching change | UPDATE/DELETE on stock_ledger | Append-only correctness | **stays inline** in authority docs | exists as policy text |
| UX_OPERATING_PRINCIPLES.md | reference doc | portal-operator-ux desk (UX agents) | every UX audit | Decoration without system rule; copy without register entry | UX audit consistency | **stays a reference doc** | exists |
| FLOW-003 boundary | inline policy text | portal-operator-ux desk | every `/planning/blockers` substrate change | FLOW-003 violation | Tom-approved boundary preserved | **stays inline** | exists |

**Skill Pack proposals (NOT created in this groundwork; flagged for future):**

| Proposed pack | Sub-agent | Trigger | Mistake prevented | Why not now |
|---|---|---|---|---|
| Stock-truth invariants checklist | backend-db-truth | every backend-db migration that touches ledger / projections | direct ledger write; projection drift; rebuild_verifier ≠ 0 | Currently distributed across CLAUDE.md, SCHEMA_GUIDANCE, EXECUTION_POLICY; consolidating early risks duplicating authority. Defer until backend-db-truth pilots. |
| Portal post-submit observability checklist | portal-operator-ux | every form submission surface | post-submit "looks green" without ledger event | Currently distributed across portal_ux_standard.md and CLAUDE.md §non-negotiables. Defer until portal-operator-ux pilots. |
| Frozen-flag flip checklist | integrations-boundary | flag flip request | bypass any of (Tom written approval / dry-run / ≥24h soak / RUNTIME_READY) | Currently distributed across CLAUDE.md and EXECUTION_POLICY §Frozen flags log. Defer; risk of authority duplication. |
| Drift triage checklist | governance-docs-router | every `/source-truth-audit` and `/docs-hygiene-check` run | misclassifying STALE vs CONFLICTING; missing ORPHANED items | The current command bodies cover this. Defer. |

---

## Section 5 — ROUTER impact analysis

**Do NOT edit `AI_BRAIN_ROUTER.md` in this groundwork.** This section analyzes whether the existing YAML output contract can support a future desk/sub-agent/skill model.

### 5.1 What the current contract supports

Current ROUTER output (`AI_BRAIN_ROUTER.md` §6):

```yaml
classification: <input_type>
target_module: factory-os | crm | leads | sales | marketing | finance | cross-system
owner_lane: backend-db | portal | integration | docs | ux-audit | governance | release-gate | source-of-truth
recommended_agent: <agent name from AGENT_REGISTRY.md>
recommended_command: <command from COMMAND_REGISTRY.md, or "direct dispatch (no command)">
allowed_paths: [...]
forbidden_paths: [...]
write_mode: read_only | proposal_only | write_with_approval | write
tom_decisions_required: [...]
backend_readiness_required: { required, signal }
ux_handoff_required: { required, packet }
first_checkpoint: <one concrete first step>
stop_conditions: [...]
expected_evidence: [...]
collision_risk: none | <named lane>
verdict: ROUTED | NEEDS_TOM | NO_VALID_LANE | NEW_MODULE_REQUIRED
```

### 5.2 What desk/sub-agent routing would add

**Minimum addition:** a `desk` field. Each `recommended_agent` already implicitly belongs to a desk (e.g., `backend-db-executor` → backend-db-truth desk). Adding `desk: <desk-name>` makes this explicit and lets ROUTER use desk as the primary classification axis (then sub-agent as the secondary).

```yaml
desk: backend-db-truth | portal-operator-ux | integrations-boundary | planning-procurement | finance-economics | governance-docs-router
sub_agent: <agent name from AGENT_REGISTRY.md>   # was: recommended_agent
required_skill_packs: [...]   # NEW — explicit skill packs the sub-agent must apply
```

The existing `owner_lane` value would become a property of the desk (e.g., backend-db-truth has lane `backend-db`), so it can either be removed from the output (computed from desk) or kept for back-compat. Removal is cleaner; back-compat is safer.

### 5.3 What can be achieved without changing the ROUTER contract

A surprising amount:

- **Implicit desks:** the current `recommended_agent` already names a single agent that belongs to exactly one desk. We can document the desk-to-agent mapping in `AGENT_REGISTRY.md` (e.g., add a "Parent desk" column) **without** changing the ROUTER output. Every consumer that reads the ROUTER output today gets the desk by lookup, not by direct field.
- **Implicit skill packs:** the same pattern — document required skill packs for each agent in `AGENT_REGISTRY.md`. The ROUTER continues to emit just `recommended_agent`; downstream the agent's required skills are looked up.

This means a desk pilot can run **without ROUTER mutation**. The only thing changing is how `AGENT_REGISTRY.md` indexes its 17 agents (parent desk column added; required-skill-pack column added). That's a registry edit, not a routing-contract edit.

### 5.4 What would push us to a v2 ROUTER contract

Three triggers would justify a v2:

1. **Multi-sub-agent dispatch within a desk.** If a single input genuinely needs two sub-agents under one desk to run in parallel (e.g., backend-db migration sub-agent + pgTAP sub-agent), the current single-`recommended_agent` field can't express it. Today this never happens; both sub-roles live in the same `backend-db-executor`.
2. **Cross-desk sub-agent composition.** If a future workflow needs a sub-agent in desk A to hand off to a sub-agent in desk B that requires a particular skill pack from desk C, the current contract can't express the cross-desk skill requirement cleanly.
3. **Per-skill-pack routing.** If skill packs are large enough (>10) that picking the right ones becomes a routing problem rather than an agent-internal problem, then a `required_skill_packs` field becomes necessary in output, not a downstream lookup.

None of those triggers are in scope today. **Defer ROUTER v2 indefinitely.**

### 5.5 Risks of expanding routing too early

- **Authority diffusion.** Today the ROUTER is a single decision tree owned by `factory-os-governor`. Adding desk/sub-agent/skill-pack structure to the output without a corresponding desk-routing implementation would create ambiguity (which one is authoritative — `desk` or `recommended_agent` if they disagree?).
- **Test surface explosion.** ROUTER changes are governance-authority changes. Each output-contract change implicates every downstream consumer (every command file, every agent file, every dispatch convention). Premature changes mean churn without substance.
- **Migration debt.** If desks are introduced in the contract before the registry-side desk-to-agent mapping is canonicalized, existing dispatches will silently fall back to old shapes; the system will look like it adopted desks but actually be running single-layer.

**Recommendation:** **do not** edit ROUTER until at least one desk pilot has produced ≥2 cycles of evidence at the registry-and-conventions layer. Then revisit with concrete data.

---

## Section 6 — Pilot recommendation

Tom's stated preference: **governance-docs-router desk + backend-db-truth desk** as the first two pilots.

This is the right pair. Reasons:

### 6.1 Why governance-docs-router first

- **Drift reduction:** the desk's mandate is exactly the sort of work that flagged Hole 1 + Hole 2 + Hole 3 in this very tranche. A canonicalized desk means the next round of drift is caught faster.
- **No false-authority risk:** the desk is read-only or proposal-only across all of its sub-agents. Piloting it cannot break the runtime.
- **Sub-agents already exist and are stable:** `factory-os-governor`, `release-verifier`, `source-of-truth-auditor`, `ops-docs-curator` are all production-active with clean allowed-paths.
- **Pilot output:** two `AGENT_REGISTRY.md` columns added (parent desk, required skill packs); each of the 4 sub-agents gets an explicit "parent desk" annotation; one cycle of `/source-truth-audit` and one cycle of `/docs-hygiene-check` are run with the desk framing recorded; verdict is whether desk framing improved either output.

### 6.2 Why backend-db-truth second

- **Stock-truth-impacting:** this is where authority hierarchy actually pays off. Every backend-db dispatch touches ledger semantics, parity, RUNTIME_READY emission. A clean desk means the locked-decision boundary is enforced at the desk gate, not hoped-for at the agent level.
- **Future-proof:** the FR1→write→FR2 bracket is already a desk-grade discipline (it's the right kind of constraint to attach to a desk, not to a single agent). Piloting backend-db-truth would surface whether other backend-db-grade disciplines (ledger immutability, parity rebuild) belong as skill packs or stay inline.
- **Sub-agents already exist:** `backend-db-executor` (production) + `executor-w1` (legacy, Wave 6 candidate). Pilot would also formalize the legacy → production transition path under the desk's gate.
- **Pilot output:** the two backend-db sub-agents get explicit "parent desk" annotation in `AGENT_REGISTRY.md`; one backend-db migration dispatch is run with the desk framing; verdict is whether the desk gate caught any boundary violation that the current single-agent model would have missed.

### 6.3 Pilot guardrails

- **Pilot is documentation-only.** No runtime change. No agent-file rewrite. The pilot adds two columns to `AGENT_REGISTRY.md` and runs ≥2 dispatches under each desk's framing, recording the verdict.
- **One pilot at a time.** Run governance-docs-router pilot fully before opening backend-db-truth pilot. If governance-docs-router pilot fails or produces ambiguous evidence, backend-db-truth pilot does not start until that's resolved.
- **Reversal is free.** If a desk pilot fails, the rollback is to remove the two columns from `AGENT_REGISTRY.md`. No ROUTER, no agent file, no command file is touched.
- **Evidence requirement:** each pilot produces a record under `docs/phase8/architecture/pilot-records/` with: dispatches run, desk-framing applied, what the desk gate caught vs missed, would the current single-agent model have produced the same output, recommendation (continue / abandon / refine).

### 6.4 What to defer past these two pilots

- **portal-operator-ux desk pilot:** defer until the planning corridor settles into Tranche 4+ work. The portal desk has 6 sub-agents already; piloting it requires more scaffolding than the first two desks.
- **integrations-boundary desk pilot:** defer until after Sunday 2026-05-10 cutover and the monitoring corridor closes. Live integration corridor + desk pilot = unacceptable risk.
- **planning-procurement desk pilot:** defer until that desk acquires a dedicated execution sub-agent (not today).
- **finance-economics desk pilot:** defer until Phase 10 cost rollup activates or Green Invoice work becomes decision-grade (not today).

---

## Appendix A — open questions for Tom

These are the open architecture questions surfaced by this groundwork. They are NOT decisions; they are flagged for Tom's consideration before any pilot starts.

1. **Should a "desk" exist as an agent file in `.claude/agents/`?** Or is it a logical authority boundary documented in `AGENT_REGISTRY.md` only? Recommendation: documented in registry only. A desk that is itself an agent risks creating a 3-layer model (desk-agent → sub-agent → skill) without clear benefit.
2. **Should planning-procurement and finance-economics desks be declared now (with no sub-agents) or deferred until they need work?** Recommendation: declare in this groundwork as desks-of-record, leave sub-agents empty. This way the authority boundary is preserved when work starts; the alternative (defer declaration) means we re-do the audit when work activates.
3. **Should sub-agent allowed-paths be desk-scoped or stay agent-file-scoped?** Recommendation: keep agent-file-scoped (status quo). Desk-scoping would require ROUTER changes and is harder to audit per dispatch.
4. **Should skill packs live in `PRODUCTION/.claude/skills/` (new directory) or stay user-level?** Recommendation: defer until ≥1 desk pilot produces ≥1 skill pack. Today no skill pack exists at PRODUCTION level.

---

## Appendix B — verification (this groundwork pack itself)

Hard boundaries respected:
- ✅ No new agents created (verified `ls .claude/agents/*.md | wc -l` = 17, unchanged)
- ✅ No new commands created (verified `ls .claude/commands/*.md | wc -l` = 15, unchanged)
- ✅ No skills created (verified no `PRODUCTION/.claude/skills/` directory exists)
- ✅ No ROUTER mutation (`AI_BRAIN_ROUTER.md` untouched in this dispatch)
- ✅ No registry rewrite (`AGENT_REGISTRY.md` and `COMMAND_REGISTRY.md` untouched in this dispatch)
- ✅ No runtime work
- ✅ No code changes
- ✅ No behavior change

This pack is plan-only. It commits the system to nothing. The next step is Tom's go/no-go on the recommended pilot pair (governance-docs-router + backend-db-truth, in that order).

---

**Owner:** factory-os-governor (proposes).
**Approver:** Tom.
**Last updated:** 2026-05-09 (Phase 8 Run F Wave 4 Phase B initial creation).
