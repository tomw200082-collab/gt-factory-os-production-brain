# {{PROJECT_NAME}} — Project Constitution

## Purpose

{{PROJECT_PURPOSE}}

## Stack & Environment

- **Language**: {{LANGUAGE_STACK}}
- **Runtime**: {{RUNTIME_TARGET}}
  {{INTEGRATIONS_LINE}}

## Project Structure

```
{{PROJECT_NAME}}/
├── AGENTS.md                    # This file — read first, always
├── README.md
├── specs/
│   ├── requirements.md          # What + Why  (edit before any feature)
│   ├── design.md                # How         (edit after requirements approved)
│   ├── tasks.md                 # Ordered tasks (edit after design approved)
│   └── features/                # Per-feature spec files
│       └── _template.md
├── src/
│   └── {{PACKAGE_NAME}}/
├── tests/
└── pyproject.toml
```

## Conventions

- All source code lives under `src/{{PACKAGE_NAME}}/`
- Tests mirror the source tree under `tests/`
- Commit after every completed task in `specs/tasks.md`
- Mark tasks `[x]` in `specs/tasks.md` before committing

## SDD Gates — check before every coding session

Read `specs/requirements.md`, `specs/design.md`, and `specs/tasks.md` at the
start of every session. Then enforce these gates in order:

1. **requirements gate** — `specs/requirements.md` status must be `APPROVED`
   → If DRAFT: stop, tell the user, help them complete requirements first
1. **design gate** — `specs/design.md` status must be `APPROVED`
   → If DRAFT: stop, tell the user, help them complete design first
1. **task gate** — the work must map to an open `[ ]` item in `specs/tasks.md`
   → If missing: add the task entry before writing any code

If a gate fails, refuse to write code and name the gate that failed.
If a requirement changes mid-implementation, stop and update specs first.

## Claude Code Workflow

- Use Opus for spec phases (requirements, design)
- Use Sonnet for implementation phases (tasks, code)
- Spawn subagents per task in `specs/tasks.md` for parallel execution

## Tool Compatibility

AGENTS.md is the single source of truth for all AI tools:

- **Claude Code** — reads AGENTS.md natively
- **Gemini CLI** — reads AGENTS.md since v0.28.0
- **GitHub Copilot Chat** — reads AGENTS.md since v0.19.0
