# Claude Code Instructions

This project's conventions, execution rules, and dev workflow are defined in
[`AGENTS.md`](./AGENTS.md) — read it first, every session.

Before writing or modifying anything under `src/`, also read
[`specs/workflow.md`](./specs/workflow.md), which `AGENTS.md` points to.

Do not duplicate rules here. If Claude-specific behavior ever needs to diverge
from `AGENTS.md`, add it below this line — otherwise keep this file a thin
pointer to avoid drift between `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
