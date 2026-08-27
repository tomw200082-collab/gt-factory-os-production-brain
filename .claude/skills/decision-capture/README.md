# decision-capture

Mid-session workflow: as soon as a design decision is reached in
conversation, write it into the repo's spec/decision documentation, get
your explicit sign-off on the diff, commit it on its own (no implementation
code bundled in), and push.

## Why this exists

Chat history doesn't persist across sessions/tools, but decisions made in
conversation need to. Waiting until session end (`session-close`) to
capture them risks losing nuance or bundling them awkwardly with whatever
code got written in between. This skill closes that gap by firing
immediately, once per decision.

## How to invoke

```
/decision-capture
```

Also triggers on "capture this decision", "write this to specs", "record
this decision", "commit that decision".

## What it does

1. Restates the decision back for confirmation before writing anything.
2. Locates this repo's existing decision-recording convention (a spec
   file, a dated log, or asks if none exists).
3. Drafts the update, matching the existing format/detail level, noting
   alternatives considered and who confirmed it.
4. Updates the "what's next" pointer file too, if the decision changes it.
5. Shows the diff and waits for your explicit sign-off.
6. Commits the spec/decision change alone -- never bundled with code.
7. Pushes (unless the repo indicates otherwise).
8. Reports the commit hash and push result.

## How it differs from session-close

| | `decision-capture` | `session-close` |
|---|---|---|
| When | Immediately, per decision | Once, at session end |
| Frequency | Many times per session | Once |
| Scope | One decision's spec/log update | Full uncommitted-work sweep, pointer refresh, test run |
| Commits code? | Never | N/A (also spec/docs only) |
