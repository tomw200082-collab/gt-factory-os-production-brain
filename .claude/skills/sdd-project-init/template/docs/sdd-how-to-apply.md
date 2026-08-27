# How to Apply Spec-Driven Development in This Project

This document is the human reference for the SDD workflow used in this project.
For AI agent behavioral rules, see `AGENTS.md`. For active specs, see `specs/`.

______________________________________________________________________

## Why SDD

AI coding tools are most effective when given complete context upfront. Without
a spec, the AI discovers requirements incrementally — leading to rework, drift,
and code that's hard to explain later. A spec written before coding:

- Forces clarity on _what_ and _why_ before _how_
- Gives the AI a single source of truth to validate against
- Becomes living documentation that outlasts any one session
- Makes switching AI tools frictionless — move the `specs/` folder, not the history

______________________________________________________________________

## The Three Documents

### `specs/requirements.md` — What & Why

Written before anything else. Answers: what problem, who is affected, what does
success look like, what is out of scope.

**Status flow:** DRAFT → APPROVED → IN-PROGRESS → DONE

### `specs/design.md` — How

Written after requirements are APPROVED. Answers: architecture, data models,
interfaces, tradeoffs.

**Status flow:** DRAFT → APPROVED → IN-PROGRESS → DONE

### `specs/tasks.md` — Ordered steps

Written after design is APPROVED. Atomic, committable tasks with dependencies.

**Status flow:** DRAFT → APPROVED → IN-PROGRESS → DONE

______________________________________________________________________

## The Gates

```
requirements APPROVED → design APPROVED → task exists in tasks.md
```

If any gate fails, the AI stops and tells you which gate failed.

______________________________________________________________________

## The Daily Loop

1. Open `specs/requirements.md`, describe the feature
1. Ask the AI: _"Read AGENTS.md and specs/requirements.md. Help me complete
   requirements for [feature]."_
1. Review and approve (change Status to `APPROVED`)
1. Ask the AI: _"Requirements approved. Write the design."_
1. Review and approve
1. Ask the AI: _"Design approved. Break this into tasks."_
1. Review and approve
1. Ask the AI: _"Execute T01."_ — implements, commits, marks `[x]`
1. Repeat per task

### Mid-feature discovery

If something new surfaces during implementation:

1. Stop: _"Hold on, this changes the requirements."_
1. Update `specs/requirements.md` (back to DRAFT)
1. Cascade through design and tasks before resuming

______________________________________________________________________

## What Belongs Where

| Content | Location |
| -- | -- |
| AI behavioral rules + gates | `AGENTS.md` |
| Active requirements / design / tasks | `specs/*.md` |
| Per-feature breakdown | `specs/features/*.md` |
| Human reference docs | `docs/` |
| Source code | `src/` |
| Tests | `tests/` |

______________________________________________________________________

## Common Mistakes

**Skipping to design before requirements are approved**
The gate exists because vague requirements produce vague designs.

**Treating tasks.md as a scratchpad**
Tasks should be atomic and committable. If a task takes more than ~1 hour, break it down.

**Not updating specs when requirements change**
If the code diverges from the spec without a spec update, the next session
starts with wrong context.

**Editing code directly without a task entry**
Always add the task, even if it's a one-liner.
