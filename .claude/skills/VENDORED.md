# Vendored third-party skills

These skill directories were copied from public upstream repositories. They are general-purpose tools, not GT governance artifacts. Nothing here is authority, and the authority order in `CLAUDE.md` is unaffected.

On 2026-09-26 the set was pruned to what this workspace uses (`docs/plans/2026-09-26-workspace-ledger.md`, Layer 1). The history of everything removed is in git.

| Upstream | License | Skills | Taken |
|---|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `caveman` | 2026-08-04 |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `ponytail`, `ponytail-review` | 2026-08-04 |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` | 2026-08-04 |
| [boraoztunc/skills](https://github.com/boraoztunc/skills) `645553c` | MIT (README only; no `LICENSE` file) | `ogilvy`, `copywriting`, `copy-editing`, `stop-slop` (2026-08-26); `landing-page`, `page-cro` (moved here from Sales-Machine on 2026-09-26) | 2026-08-26 |
| [mattpocock/skills](https://github.com/mattpocock/skills) `c55ee46` | MIT (`LICENSE` in each directory) | `grill-with-docs`, `grilling`, `domain-modeling` | 2026-09-26 |

## Edits made here

- `ogilvy`: its frontmatter `name` was changed from `ogilvy-copywriting` to match its directory.
- 2026-09-26: the descriptions of `caveman`, `ponytail`, `ponytail-review`, `ogilvy`, `copywriting`, `copy-editing` and `page-cro` were shortened to 300 characters or less, so the whole skill listing fits the per-session budget. The `page-cro` and `copywriting` descriptions also lost their pointers to sibling skills that were never vendored (`signup-flow-cro`, `onboarding-cro`, `form-cro`, `popup-cro`, `email-sequence`).
- For `grill-with-docs`, `grilling` and `domain-modeling`, `SKILL.md` and the reference files are byte-identical to upstream. Upstream's `agents/openai.yaml` configures OpenAI's Codex and was not taken.

## Notes before use

- **The superpowers set stays whole.** Its core skills call its helpers, and `masterprompt` calls two of them. `using-superpowers` is written to run at every session start; here it applies only when invoked.
- **`caveman`** mentions "/caveman-compress exempt". That helper was removed on 2026-09-26.
- **The copy set is calibrated to English.**
  - `ogilvy` works at the level of principle and carries over to Hebrew intact.
  - `copywriting` and `copy-editing` are process skills whose examples are English.
  - Most of `stop-slop` is English string matching, so running it over Hebrew copy is not a clean pass.
- **`copywriting` and `copy-editing` look for `.claude/product-marketing-context.md`.** That file does not exist. Writing it means writing GT positioning, which is doctrine and needs Tom's approval, so both skills interview the user instead.
- **Some pointers resolve to nothing.** The bodies of `copywriting` and `landing-page` point to sibling skills that were never taken (`email-sequence`, `popup-cro`, `seo-audit`).
- **`grill-with-docs` runs only as `/grill-with-docs`** (`disable-model-invocation: true`). Its one-line `SKILL.md` loads `grilling`, which runs the interview, and `domain-modeling`, which writes the files.
  - If a session leaves no `CONTEXT.md`, ask which skills it loaded; a partial load is upstream's most-reported failure.
  - It writes a glossary (`CONTEXT.md`, at the brain root since 2026-09-26) and, rarely, ADRs. Neither is authority: locked decisions stay in `docs/decisions/LOCKED_DECISIONS.md`.
  - Run it live with Tom, not inside a pipeline. It is an interview, and upstream reports that the file-writing half silently fails inside another orchestration layer.

## Removed on 2026-09-26

- `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats` and `cavecrew`.
- `ponytail-audit`, `ponytail-debt`, `ponytail-gain` and `ponytail-help`.
- `agent-reach`: its command-line tool cannot run in cloud sessions. Its account-safety rule moved to the workspace plan.
- `skill-creator`: the claude.ai account keeps Anthropic's copy.
- The brain's copies of `apple-design` and `frontend-design`: the portal keeps identical copies, with their provenance notes in its own `VENDORED.md`.
- All 24 of Sales-Machine's vendored skills, removed or moved (`landing-page`, `page-cro`) the same day.

## Updating

Re-clone the upstream and copy `skills/<name>/` over the local directory, then reapply the edits listed above. No lockfile or auto-update is wired up.
