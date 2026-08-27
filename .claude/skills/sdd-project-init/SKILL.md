---
name: sdd-project-init
description: Bootstrap a new non-Python project with Spec-Driven Development (SDD) structure, including AGENTS.md, specs/, and docs/. For Python repos, prefer the python-repo-init skill instead.
---

# SDD Project Init

This skill bootstraps a new project with Spec-Driven Development structure. It runs a short interview, then generates all files fully populated.

> **Python repo?** Use the `python-repo-init` skill instead — it supersedes
> this one for Python: mechanical convention enforcement (pre-commit guard +
> CI), a lifecycle-staged `data/` contract, session handoff via `specs/NEXT.md`,
> and uv/mise tooling. This skill remains the language-agnostic scaffold.

## Procedures

1. **Interview**: Ask the user for the project name, purpose, stack, and runtime.
1. **Project Generation**: Call `tools/create-project.sh` with the provided information.
1. **SDD Structure**: Ensure the following files and directories are created:
   - `AGENTS.md` (AI constitution + SDD gates)
   - `README.md`
   - `.gitignore`
   - `docs/sdd-how-to-apply.md` (human workflow reference)
   - `specs/requirements.md`, `specs/design.md`, `specs/tasks.md`
   - `specs/features/_template.md`

## Instructions

- Use `AGENTS.md` as the single source of truth for AI instructions.
- Ensure the project structure follows the SDD standard.
- After initialization, guide the user to `specs/requirements.md` to start their first feature.
