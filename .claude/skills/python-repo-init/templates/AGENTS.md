# Instructions

## Universal Execution Rules
- **No Filler:** No greetings, sign-offs, or prompt recaps. Start directly with the answer, fix, or code.
- **Ultra-Brief:** Explanations ≤ 1 sentence. Only output modified code lines unless full context is requested.
- **Contractor Autonomy:** Act as an elite, autonomous contractor. Never ask for guidance on obvious details; take full ownership. Still ask before acting on the human-decision items parked in `specs/NEXT.md`.
- **Surgical Changes:** Touch only what was explicitly requested. Do not refactor adjacent code.
- **Definition of Done:** Complete tasks fully with zero placeholders or `# TODO`s. Keep `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` compatible.
- **Goal-Driven:** Define clear success criteria (`uv run pytest`) instead of vibes.

## Standing Principle: Agent-Agnostic by Default
Every spec, tool choice, and instruction added here MUST be usable by any AI
coding tool (Copilot CLI, Claude Code, Gemini CLI, others), not just the one
that authored it. Mirror durable decisions into `specs/memory.md`; keep
tool-specific files thin pointers to this one. Binding rule — see
`specs/workflow.md` Section 1a.

## Repo Map
- `README.md` — user-facing "how to install/run this" (setup, CLI usage).
  Not engineering process — see `specs/` for the "why".
- `specs/NEXT.md` — **read this first, every session.** The single git-tracked
  pointer to current actionable work (session-local `todos` do not persist —
  this file is the durable handoff).
- `docs/` — domain analysis (start at `docs/README.md`); reserved for domain
  analysis only, not engineering process.
- `specs/` — engineering specs driving `src/` code, the `data/` contract, and
  cross-tool conventions (start at `specs/workflow.md`).
- `specs/memory.md` — durable facts/decisions log, agent-agnostic.
- `data/01_raw/`, `data/03_generated/`, `data/work/`, `data/tmp/` — see
  `specs/workflow.md` Section 5a for the tracked-vs-gitignored contract and
  provenance headers.

## Building in This Repo
- Before writing or modifying anything under `src/` or generated data
  (`data/03_generated/`), read `specs/workflow.md` — it defines the
  spec-first, one-skill-per-module, test-alongside workflow.
- Each skill module in `src/` requires a matching spec in
  `specs/NNN-<skill-name>.md` and a test in `tests/test_<skill-name>.py`.
- A pre-commit hook (`scripts/check_repo_conventions.py`, see
  `specs/workflow.md` Section 8) mechanically enforces some rules — run
  `git config core.hooksPath .githooks` once per clone (the hook is
  stdlib-only; `uv sync --dev` is only needed to run tests).

## Durable Facts / Memory
Read `specs/memory.md` for a git-tracked, agent-agnostic log of durable
decisions (mirrors GitHub Copilot's `store_memory`, invisible to other tools).
Append new durable facts there whenever they're recorded via any tool.
