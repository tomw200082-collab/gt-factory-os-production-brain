---
name: session-close
description: >
  Session end-of-work checklist. Refreshes the repo's durable "what's next"
  pointer file (e.g. specs/NEXT.md) so a future session can resume without
  re-discovering state, checks for uncommitted work, and gets explicit
  human sign-off on the content before ending. Use when the user says
  "close session", "end session", "wrap up", "before I close", "session
  close", or invokes /session-close. This is a manual, user-invoked
  backstop for sessions that end without a qualifying commit (mechanical
  pre-commit hooks, where they exist, only fire on git commit).
---

Run this as the last thing before ending a working session. Goal: never
leave the repo in a state where the *next* session (any AI tool, or a
human) has to re-derive "what's done" and "what's next" from scratch.

## Steps

1. **Find the durable pointer file for this repo, if one exists.**
   Look for (in order): `specs/NEXT.md`, `NEXT.md`, or whatever this
   repo's own `AGENTS.md`/`CLAUDE.md`/root instructions say is the
   session-start pointer. If none exists and the repo has meaningful
   ongoing multi-session work, ask the user whether to create one instead
   of silently skipping this step.

2. **Check for uncommitted work.** Run `git status --short` and
   `git diff --stat`. If there's uncommitted work that represents a real
   decision or completed step, flag it plainly — don't silently leave it
   uncommitted without saying so.

3. **Draft an accurate update to the pointer file**, based on what
   actually happened this session (recent `git log`, the conversation,
   any spec files touched) — not a copy-paste of what was already there.
   Rules for the content itself:
   - Exactly one concrete "Active work" item if something is genuinely
     pending: name it, say the one-line next action, and give a direct
     file/section pointer (not "see spec" — the actual section).
   - If nothing is pending, write "None." explicitly. Do not leave a
     stale item from a prior session.
   - **Never stack completed "Prior:" history in the pointer file.** The
     pointer file must stay readable in one glance at session start.
     Completed-work narrative belongs in the repo's append-only dated log
     if it has one (e.g. `specs/workflow-log.md`, a `## Log` section, a
     changelog) — see the next step.
   - Do not touch the file just to satisfy a mechanical check (if one
     exists) — the content must be true, not just present.

3a. **Append this session's dated entry to the repo's decision/work log**
   (e.g. `specs/workflow-log.md`), if the repo keeps one: what was
   decided/completed, with file pointers. The log is append-only —
   newest at the bottom; never rewrite old entries. This is where the
   history the pointer file must NOT accumulate actually goes. If the
   repo has no such log, skip (or offer to create one only if the repo
   clearly has multi-session decision traffic).

4. **Show the exact diff of the pointer-file update to the user and ask
   for explicit confirmation before committing it.** This is the human
   sanity check that no mechanical hook can replace — a check can verify
   the file changed, never that the content is accurate. Do not assume
   approval; wait for it.

5. **Run this repo's existing test/lint/convention-check commands** if
   any are documented (e.g. a `scripts/check_*.py`, `pytest`, `npm test`)
   — reuse whatever the repo's own docs say, don't invent new tooling.
   Report pass/fail plainly.

6. **Summarize in ≤5 lines**: what was completed this session, what (if
   anything) remains open, and whether the working tree is fully
   committed. If something is intentionally left uncommitted, say why.

## What this skill deliberately does NOT do

- It does not replace a repo's own mechanical pre-commit/CI enforcement
  where one exists — it's a backstop for the case such a check can't
  reach (sessions that end without a qualifying commit), and a human
  accuracy check for the case no mechanical check ever can reach.
- It does not invent a new repo convention if the repo has none — ask
  the user first rather than assuming this repo wants a `specs/NEXT.md`-
  style file.
