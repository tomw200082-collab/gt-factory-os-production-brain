# session-close

End-of-session checklist: refresh the repo's durable "what's next" pointer
(e.g. `specs/NEXT.md`), flag uncommitted work, and get your explicit
sign-off on the content before ending — so the next session (any tool)
can resume without re-deriving state.

## Why this exists

A mechanical pre-commit hook can force a pointer file to be *touched* on
qualifying commits, but it can't (a) verify the content is *true*, or
(b) catch sessions that end without any commit at all. This skill is the
manual backstop for both of those gaps — invoke it yourself every time,
since there's no automatic trigger for it by design (see
`47688-columbia-school-district/specs/workflow.md`'s 2026-07-08 log for
the discussion that led to this).

## How to invoke

```
/session-close
```

Also triggers on "close session", "end session", "wrap up", "before I
close".

## What it does

1. Locates the repo's pointer file (`specs/NEXT.md` or equivalent).
2. Checks `git status`/`git diff` for uncommitted work.
3. Drafts a truthful update to the pointer file based on what actually
   happened this session.
4. Shows you the diff and waits for your explicit confirmation before
   committing.
5. Runs the repo's existing test/convention-check commands.
6. Gives a ≤5-line summary: done / still open / commit status.
