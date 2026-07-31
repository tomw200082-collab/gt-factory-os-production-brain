# GT Factory OS — Module Declaration Template

> **Authority layer:** mandatory declaration for any new module added to the GT Factory OS AI Brain.
>
> **Hard rule (locked):** **No new module is built before this template is filled in for that module and Tom has approved the declaration in writing.** Adding code, schema, agents, commands, or UX surfaces for a module that lacks an approved declaration is forbidden. The router (`AI_BRAIN_ROUTER.md`) returns `verdict: NEW_MODULE_REQUIRED` for any input that requests work on an undeclared module.
>
> **Why this exists:** without module declarations, adding CRM, lead intake, sales workflow, marketing automation, or finance modules creates ad-hoc lane definitions, overlapping ownership, data-model contamination of factory-os core (especially stock truth), and verdict-vocabulary collisions. The template is the only entry point for new operating-system surfaces.
>
> **Use:** copy this file to `PRODUCTION/docs/decisions/modules/<module-name>-declaration.md`. Fill every required section. Submit to Tom. After approval, `factory-os-governor` updates `AI_BRAIN_ROUTER.md` §3 with the module's lane row(s) and the module's lane-scoped agents become dispatchable.

---

## Required sections

Sections marked **required** must be completed. Sections marked **conditional** apply only when the module has the relevant role.

---

## 1. Module name                        [required]

`<kebab-case-name>` (e.g., `crm`, `leads`, `sales`, `marketing`, `finance`)

## 2. Business purpose                   [required]

Two to four sentences:
- What operational problem does this module solve?
- Who is the primary user (operator / planner / admin / external customer / agent)?
- Why now? (What changed in factory-os or the business that makes this module necessary?)

## 3. Owner lane                         [required]

The module's primary owner lane. Pick one:
- `module-arch` (read-only architect, for early declaration phase)
- `<module>-backend-db`
- `<module>-portal`
- `<module>-integration`
- Cross-module owner (if no single lane fits — explain why)

The owner lane is the agent that decides ambiguous routing within the module.

## 4. Source of truth                    [required]

Which system stores authoritative truth for the module's primary entities? Examples:
- factory-os Postgres (sub-schema)
- External SaaS (e.g., HubSpot for CRM contacts)
- Hybrid (specify split)

For each authoritative entity, declare:
- Entity name
- Primary key
- Storage location
- Tiebreaker rule when sources disagree

## 5. Data model                          [required]

Enumerate every entity the module owns. For each:
- Table name (proposed) or external API resource
- Foreign keys to factory-os entities (if any) — these are the points where module ownership ends
- Primary key strategy (UUID / external ID / composite)
- Append-only or mutable
- Audit trail strategy

**Hard rule:** the module's tables live in a private schema scoped to the module (e.g., `crm_core`). The module's backend-db agent cannot touch factory-os core tables (`stock_ledger`, `balance_anchors`, `bom_*`, etc.). Cross-module reads are permitted via curated views; cross-module writes require explicit cross-lane authorization.

## 6. Upstream systems                    [required]

External systems the module reads from. For each:
- System name (e.g., Shopify, Google Workspace, HubSpot)
- Auth mechanism
- Read frequency (live / polled / webhook)
- Data freshness tolerance
- Failure mode if upstream is unavailable

## 7. Downstream consumers                [required]

Who reads the module's data? For each:
- Consumer name (factory-os planning engine / dashboard / portal / external API)
- Read pattern (polled view / event subscription / direct query)
- Stale-read tolerance

## 8. Write boundaries                    [required]

```yaml
may_write:
  - <table or external resource> by <agent name>
  - <table> by <agent name>
may_not_write:
  - factory-os core tables (stock_ledger, balance_anchors, items, components, bom_*, ...)
  - other modules' private schemas
  - .env*, credentials, secrets
  - PRODUCTION authority docs (only ops-docs-curator under governor approval)
```

## 9. Read boundaries                     [required]

```yaml
may_read:
  - <factory-os tables/views needed>
  - <other module curated views>
may_not_read:
  - other modules' private tables (use curated views only)
  - secrets/.env*
```

## 10. UX surfaces                        [conditional — only if module has portal pages]

For each route:
- URL path
- Role gating (operator / planner / admin / viewer / module-specific role)
- UX handoff packet path (under `gt-factory-os-portal/docs/ux/`)
- RUNTIME_READY signal name (if backend-bound)
- Hebrew copy register entry path (if user-visible Hebrew strings)

## 11. Integration surfaces               [conditional — only if module calls external systems]

For each external integration:
- Provider name
- Frozen-flag name (default `false`; flip requires Tom approval + dry-run + ≥24h soak + RUNTIME_READY)
- Contract doc path
- Idempotency key strategy
- Reversal handling

## 12. Agent ownership                    [required]

Module-scoped agents. For each, an `AGENT_TEMPLATE.md` file must exist before the agent is created.

| Lane | Agent name | Status |
|---|---|---|
| module-arch | `<module>-architect` | required for declaration phase |
| backend-db | `<module>-backend-builder` | required if module has backend |
| portal | `<module>-portal-builder` | required if module has UI |
| integration | `<module>-integration-builder` | required if module has external systems |

A module-scoped agent's allowed-paths are scoped to the module's directories only. The agent cannot touch factory-os core schema.

## 13. Commands needed                    [conditional — only if module has bespoke workflows]

List slash commands the module needs that are not already covered by the existing 15 factory-os commands. For each:
- Command name (`/<module>-<verb>`)
- Purpose
- Primary agent
- Output verdict tokens (must match `VERDICT_GLOSSARY.md` or extend it)

A new command requires factory-os-governor PROCEED + Tom approval before creation.

## 14. Tests required                     [required]

For each test category, declare what coverage is required for module v1:
- Unit tests
- Integration tests (within module)
- Cross-module reconciliation tests (if module FKs into factory-os)
- E2E golden-path tests
- Idempotency tests (if module accepts forms)
- Failure-mode tests (upstream unavailable, partial writes, retries)

## 15. Gates                              [required]

Module v1 ships when ALL these gates pass. List per-gate exit criteria:

| Gate | Exit criteria |
|---|---|
| Module Gate 1 — Declaration | This file approved by Tom |
| Module Gate 2 — Foundation | Schema in place; agents exist; tests scaffolded |
| Module Gate 3 — Truth | Module's primary entity round-trips through API; tests green |
| Module Gate 4 — UX (if applicable) | UX release gate passes for all module routes |
| Module Gate 5 — Integration (if applicable) | All external integrations dry-run clean; frozen flags still `false` |
| Module Gate 6 — Cross-module | Reconciliation tests with factory-os pass; no contamination of core truth |

## 16. Rollback / disable strategy        [required]

If the module breaks after launch, how is it disabled without affecting factory-os core?
- Feature flag controlling module entry points
- Schema-level isolation that allows the module's tables to be dropped without affecting core
- Cron / job disable strategy
- UX surface hide strategy
- Communication plan (who gets notified)

## 17. Tom decisions required             [required]

Enumerate every decision Tom must make before the module ships:
- Authentication / authorization model
- External integration credentials
- Cost / vendor approvals
- Cross-module data sharing rules
- Hebrew register entries (per surface)

Decisions are tracked in `PRODUCTION/docs/decisions/modules/<module>-decisions.md`.

## 18. Definition of done                 [required]

A binary checklist of conditions that must all be true before the module is considered v1:
- [ ] All gates in §15 closed with evidence.
- [ ] All Tom decisions in §17 answered.
- [ ] All UX surfaces audited and SHIP-verdict from `/ux-release-gate`.
- [ ] All tests in §14 green; coverage report attached.
- [ ] Rollback strategy in §16 dry-run-tested.
- [ ] Module added to `AI_BRAIN_ROUTER.md` §3 lane table.
- [ ] Module agents added to `REGISTRY.md`.
- [ ] Module commands added to `REGISTRY.md`.
- [ ] CURRENT_STATE.md updated to record module live status.

---

## What this template prevents

Without this template, a CRM build would likely:
- Add `customer` columns to factory-os tables (data-model contamination).
- Create a generic `crm-builder` agent with no allowed-paths declaration (lane drift).
- Reuse Shopify customer records as CRM contacts without reconciliation rules (source-of-truth ambiguity).
- Ship UX surfaces in Hebrew without register entries (locked-decision violation).
- Flip frozen flags during integration setup (HARD violation).

The template forces every one of these decisions to be made explicitly, in writing, before code is touched.

---

## Process

1. Dispatcher receives a module request.
2. Router emits `verdict: NEW_MODULE_REQUIRED`.
3. Dispatcher copies this template to `PRODUCTION/docs/decisions/modules/<module>-declaration.md`.
4. Dispatcher fills every required section.
5. Submit to Tom for approval.
6. On Tom approval (in writing): `factory-os-governor` updates `AI_BRAIN_ROUTER.md` §3 with the module's lane row(s).
7. Module-scoped agents are created using `AGENT_TEMPLATE.md`.
8. Module work begins per the gates in §15.

---

**Owner:** `factory-os-governor` (governs declarations).
**Approver:** Tom (every module declaration).
**Last updated:** 2026-05-08 (Phase 8 Run F Wave 2 — initial creation).
