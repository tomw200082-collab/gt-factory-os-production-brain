# Tasks

> **Status**: DRAFT
> **Requires**: `specs/design.md` APPROVED
> **Last updated**: {{DATE}}

______________________________________________________________________

## Rules

- Tasks are executed in order unless marked `[parallel]`
- Commit after EACH task with message: `task(N): <title>`
- Mark `[x]` before committing
- If a task reveals new requirements → STOP, update `specs/requirements.md` first

______________________________________________________________________

## Task List

### Phase 1: Foundation

- [ ] **T01** — Project scaffold `[no deps]`
- [ ] **T02** — [Core component] `[deps: T01]`
- [ ] **T03** — Basic entrypoint `[deps: T01]`

### Phase 2: [Feature Name]

- [ ] **T04** — ... `[deps: T01, T02]`
- [ ] **T05** — ... `[deps: T04]`

### Phase 3: Testing & Docs

- [ ] **T10** — Unit tests for all components `[deps: T01–T09]`
- [ ] **T11** — Update README with usage examples `[deps: T10]`

______________________________________________________________________

## Completed

_(move tasks here when done)_

______________________________________________________________________

_No code changes without a task entry above_
