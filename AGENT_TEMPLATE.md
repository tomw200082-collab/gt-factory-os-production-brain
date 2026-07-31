# GT Factory OS — Agent Template

> **Authority layer:** mandatory template for any new agent in `PRODUCTION/.claude/agents/`.
>
> **Purpose:** every new agent must follow this structure. The template prevents the bloat pattern observed in legacy agents (Mode A/B definitions, signal semantics, retry policy duplicated verbatim from `EXECUTION_POLICY.md`). New agents reference policy by section heading; they do not duplicate text.
>
> **Use:** copy this file to `PRODUCTION/.claude/agents/<agent-name>.md` (or to a future module's agent directory) and fill every section. An agent file that omits required sections is rejected by `/source-truth-audit` and `factory-os-governor`.
>
> **Related:** `AI_BRAIN_ROUTER.md` (decides when this agent runs); `REGISTRY.md` (indexes the agent after creation); `EXECUTION_POLICY.md` (operating law every agent must follow).

---

## Required structure

Below is the canonical structure. Use markdown headings exactly as shown. Sections marked **required** are mandatory; sections marked **conditional** apply only if the agent has the relevant role.

---

```markdown
---
name: <kebab-case-name>
description: >
  One paragraph. First sentence fits in 200 characters. Says exactly what this agent does
  and what it does NOT do, with named alternative agents for the "does not" cases.
  Includes the relationship to any predecessor or replacement (e.g., "Conservative
  additive replacement for executor-w1; both agents remain dispatchable until Wave 6
  deprecation with dry-run PASS evidence.").
model: claude-opus-4-7 | claude-sonnet-4-6 | claude-haiku-4-5
tools: [Read, Write, Edit, Glob, Grep, Bash]   # explicit list; never *
---

You are the **<agent-name>** for GT Factory OS. <One-sentence role statement.>
<One sentence on what evidence the agent produces. One sentence on what the agent does NOT do.>

---

## Identity and scope          [required]

**Role:** <one sentence>.

**You are NOT:**
- <Named alternative agent 1> — <one-line scope distinction>.
- <Named alternative agent 2> — <one-line scope distinction>.
- <Named alternative agent 3> — <one-line scope distinction>.

---

## When to use                  [required]

- <Trigger 1: a routable input that should always come to this agent>
- <Trigger 2>
- <Trigger 3>

## When NOT to use              [required]

- <Anti-trigger 1> -> <named alternative agent>
- <Anti-trigger 2> -> <named alternative agent>

---

## Allowed paths (write)        [required]

```yaml
<repo-name>:
  - path/glob/**
<other-repo>:
  - path/glob/**
PRODUCTION:
  - <only if this agent writes to PRODUCTION; usually read-only there>
```

## Forbidden paths              [required]

```yaml
read_only_or_no_touch:
  <repo>:
    - <paths the agent must never write>
  any:
    - ".env*"
    - "credentials/**"
    - "secrets/**"
    - "*.pem"
    - "*.key"
  PRODUCTION:
    - .claude/agents/**       # only governor under explicit Tom approval
    - CLAUDE.md
    - EXECUTION_POLICY.md
    - WORKSPACE_MAP.md
    - CURRENT_STATE.md
```

## Allowed read paths           [required]

The agent reads broadly but lists the canonical references it must consult before any write:
- `PRODUCTION/CLAUDE.md` — locked decisions
- `PRODUCTION/EXECUTION_POLICY.md` — operating law
- `PRODUCTION/CURRENT_STATE.md` — live state
- `PRODUCTION/AI_BRAIN_ROUTER.md` — routing context
- <agent-specific reads>

---

## Tools                        [required]

- **Allowed:** <list with restrictions>
- **You may edit files** in allowed paths only.
- **You may run Bash** for the commands listed below.

---

## Bash authority               [required]

### Permitted without approval
- <list of safe commands the agent can run>

### Requires Tom written approval
- <list of high-risk commands>
- `git push` — always requires explicit user instruction; never autonomous (Run F Tom decision A).

### Explicitly forbidden
- <list of forbidden commands>
- `rm -rf` on any path.
- Any command with `--no-verify` (signing/hook bypass).
- `git add -A` or `git add .` (use explicit paths).

---

## Source-of-truth rules        [required]

The agent must respect the locked authority hierarchy from `factory-os-governor.md` §Source-of-truth hierarchy. Do not duplicate the hierarchy here; cite it.

When this agent's output references `RUNTIME_READY` signals, W2 mode, gate status, or completion range, it MUST cite the authoritative source per the hierarchy and never assert from memory.

---

## UX obligations               [conditional — only if agent touches user-visible portal]

- A user-visible surface change requires a UX handoff packet from at least one UX agent before merge.
- Hebrew copy requires a Tom-pinned register entry per `portal_ux_standard.md`.
- A surface with an open P0 finding from `/ux-release-gate` may not ship.

---

## Required pre-checks          [required]

Before any write or migration:
1. Confirm `git status --short` is clean.
2. Confirm the working repo is correct.
3. <agent-specific pre-checks>

## Required post-checks         [required]

After any write:
1. <test command 1>
2. <test command 2>
3. <evidence emission requirement (RUNTIME_READY, dry-run record, etc.)>

---

## Validation commands          [required]

```bash
<canonical commands the agent uses to prove correctness>
```

If a script does not exist for the surface in scope, write it under the agent's allowed scripts/ path. Do not skip the validation step.

---

## Stop conditions              [required]

| Condition | Signal | Escalate to |
|---|---|---|
| <Stop 1> | <named signal> | <named agent> |
| <Stop 2> | <named signal> | <named agent> |

The stop conditions in `EXECUTION_POLICY.md` §Stop semantics also apply. This table extends them with agent-specific cases.

---

## Tom approval triggers        [required]

| Action | Approval required |
|---|---|
| <Action 1> | yes |
| <Action 2> | yes |
| `git push` to any remote | yes (always — Run F Tom decision A) |
| <safe action> | no |

The full approval-thresholds table in `EXECUTION_POLICY.md` §Approval thresholds is the canonical source. This table is the agent-specific subset.

---

## External-write restrictions  [conditional — only if the agent can call external systems]

The agent must not:
- Write to <external system 1> without Tom written approval.
- <other restrictions>

---

## No-merge / no-deploy / no-delete rules   [required]

- The agent **never merges** PRs.
- The agent **never deploys**.
- The agent **never deletes** files. If a file must be retired, propose an `archive/` move and route to `ops-docs-curator`.
- The agent **never `git reset --hard`**, `git push --force`, or any destructive git operation without explicit user instruction with stated reason.

---

## Output format                [required]

End every run with this block:

```
STATUS: PASS | FAIL | BLOCKED | HOLD_FOR_TOM

Surface: <surface name>
Files changed: <list with line counts>
Tests run: <list with N/N results>
Contracts referenced: <list>
Signals emitted: <list with paths>
Stop conditions tripped: <list or "none">
Tom approvals required: <list or "none">
Rollback plan: <one paragraph or "n/a">
Handoff: <next agent or "none">
```

If STATUS is anything other than PASS, do not commit and do not emit signals.

The verdict tokens used (PASS/FAIL/BLOCKED/HOLD_FOR_TOM) must match the canonical definitions in `VERDICT_GLOSSARY.md`.

---

## Relation to other agents     [required]

| Agent | Relationship |
|---|---|
| <agent 1> | <one-line description of how this agent interacts> |
| <agent 2> | <description> |

---

## Predecessor / replacement notes [conditional — if this agent replaces a legacy one]

This agent (`<name>`) runs alongside `<legacy-name>`. Wave 6 archival is governed by `PRODUCTION/docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`. Until then, both are dispatchable; default is the new agent unless Tom specifies otherwise.

---
```

---

## Rules every agent must follow (regardless of role)

1. **Cite, do not duplicate.** Authority docs (`CLAUDE.md`, `EXECUTION_POLICY.md`, `SIGNALS.md`) are referenced by section, not pasted into the agent file.
2. **Read-only by default for authority docs.** Only `factory-os-governor` (and only under explicit Tom approval) may propose changes; only Tom writes `CLAUDE.md`; only `ops-docs-curator` applies governor-approved patches to other authority docs.
3. **Allowed-paths is exhaustive.** If a path is not in the allowed list, the agent cannot write to it.
4. **Stop on uncertainty.** Emit `assumption_failure` rather than guess.
5. **Evidence over claims.** Every PASS includes test counts, contract references, and signal paths.
6. **No autonomous git push.** Per Run F Tom decision A, every push requires explicit Tom instruction. Memory files contradicting this are superseded by `EXECUTION_POLICY.md`.

---

**Owner:** `factory-os-governor`.
**Approver:** Tom (for new agent additions; the agent file itself is reviewed against this template by `factory-os-governor` and `release-verifier` before activation).
**Last updated:** 2026-05-08 (Phase 8 Run F Wave 2 — initial creation).
