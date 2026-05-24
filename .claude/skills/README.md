# `.claude/skills/` — Skill Inventory & Usage Policy

> Operational guidance only. Not an authority doc. Does not override
> `CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, agent allowed-paths,
> or stop conditions.

## Installed skills

| Skill | Version | Source | Purpose |
|-------|---------|--------|---------|
| `ui-ux-pro-max` | 2.5.0 | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | UI/UX design intelligence: 50+ styles, 161 color palettes, 57 font pairings, 99 UX guidelines, 25 chart types, across 16 stacks. |

## `ui-ux-pro-max` — Smart Usage Policy

The skill's own `SKILL.md` carries a full `When to Apply / Must Use / Recommended / Skip`
section. This README narrows it to **how it should be invoked from within the
Production Brain repo**, so it's used when it adds value and stays silent otherwise.

### Invoke when

- Planning or reviewing portal (`gt-factory-os-portal`) screens, components, layouts,
  navigation, forms, charts, or empty/loading/error states.
- Drafting a UX handoff packet (`docs/phase8/handoffs/`), portal contract, or
  dashboard contract that prescribes visual/interaction behavior.
- Routing into a portal lane via `AI_BRAIN_ROUTER.md` where the task touches
  visual design, accessibility, typography, color, or interaction.
- A `ux-audit` read-only pass needs concrete guideline citations (use it to ground
  findings in the `ux-guidelines.csv` / stack-specific rules, not just opinion).
- Tom asks for design recommendations, palette/typography options, or a style call
  for a portal surface.

### Skip when

- Working in `backend-db`, `integration`, `docs` (non-UX), `release-gate`,
  `source-of-truth` lanes — the skill adds nothing to schema, ledger,
  integration boundaries, or governance writing.
- Editing authority docs (`CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`,
  `AI_BRAIN_ROUTER.md`, `AGENT_REGISTRY.md`, `COMMAND_REGISTRY.md`,
  `VERDICT_GLOSSARY.md`, `WORKSPACE_MAP.md`).
- Editing agent / command / contract / decision files — these are governance,
  not UI.
- Schema, migrations, jobs, ledger semantics, projection math, or any
  `gt-factory-os/` backend work.
- Pure documentation tidying, glossary edits, or audit log writing.

### How to query (when it IS invoked)

The skill includes a Python 3 search engine. Run from repo root:

```bash
# Domain search
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> -n <max_results>

# Stack search (portal is Next.js)
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack nextjs
```

**Domains:** `product`, `style`, `typography`, `color`, `landing`, `chart`, `ux`.
**Stack to use for portal:** `nextjs` (or `shadcn` for shadcn/ui components).

### Discipline

- Cite the rule (`Category` / `Issue` / source CSV) when applying a finding —
  the skill's value is *evidence-backed* design calls, not vibes.
- Don't run the search for every UI mention. One targeted query per real
  decision; not per sentence.
- If the task is a backend or integration question that *also* mentions a UI
  side-effect, route the UI sub-question to a separate, scoped invocation —
  don't pull the skill into the backend turn.
- The skill is operational tooling, not an authority. If its guidance conflicts
  with `LOCKED_DECISIONS.md`, the locked decision wins.

## Adding more skills

Per `docs/phase8/decisions/STEP4-SKILLS-DECISION.md`, a new skill is justified
only when the same multi-step protocol is invoked > 3×/week, has a single
canonical entry point, measurably shortens the operator's prompt, and isn't
already covered by an agent or command. Document each addition in the table
above with its source, version, and a one-line purpose.
