# Vendored third-party skills

These skill directories were copied in from public upstream repositories on
2026-08-04. They are **not** GT Factory OS governance artifacts — they are
general-purpose development-workflow skills. Nothing here is authority; the
authority order in `CLAUDE.md` is unaffected.

| Upstream | License | Skills |
|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review` |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` |
| Anthropic `claude-plugins-official` | Apache-2.0 | `skill-creator` |

`skill-creator` was already present in the container's global `~/.claude/skills`
but that directory is ephemeral. Copying it here makes it survive session
restarts — the same outcome `/plugin install skill-creator@claude-plugins-official`
would produce, which is unavailable in the remote environment. Its
`LICENSE.txt` travelled with it.

Skills only. Upstream hooks, slash commands, subagent definitions, MCP servers,
and installer scripts were **not** copied, and `settings.json` was not modified.

## Notes before use

- **`caveman-compress` overwrites the file you point it at.** It rewrites
  `CLAUDE.md`-style files into compressed form in place, keeping a
  human-readable backup outside the repo tree. `CLAUDE.md` in this repo is
  Tom-sole-writer — do not run it against any authority doc.
- **`caveman-stats` needs the upstream mode-tracker hook** to produce numbers.
  Without it the skill has no data source.
- **`using-superpowers` is written as an always-on session-start skill.**
  Upstream injects it via a hook; here it only applies when invoked.
- `cavecrew` references subagents (`cavecrew-investigator` / `-builder` /
  `-reviewer`) that were not copied, so its delegation targets do not exist
  in this workspace.

## Updating

Re-clone the upstream repo and copy `skills/<name>/` over the local directory.
There is no lockfile or auto-update wired up.

## License

All three upstreams are MIT. Copyright remains with the respective authors:
Julius Brussee, Dietrich Gebert, and Jesse Vincent. The MIT license permits
this redistribution provided the copyright and permission notice are retained;
full license text is in each upstream repository's `LICENSE` file.
