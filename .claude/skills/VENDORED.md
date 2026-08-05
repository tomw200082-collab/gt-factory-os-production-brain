# Vendored third-party skills

These skill directories were copied in from public upstream repositories on
2026-08-04 (obsidian-skills: 2026-08-05). They are **not** GT Factory OS governance artifacts — they are
general-purpose development-workflow skills. Nothing here is authority; the
authority order in `CLAUDE.md` is unaffected.

| Upstream | License | Skills |
|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review` |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` |
| Anthropic `claude-plugins-official` | Apache-2.0 | `skill-creator` |
| Anthropic (supplied by Tom, 2026-08-05) | see note | `frontend-design` |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | MIT | `defuddle`, `json-canvas`, `obsidian-bases`, `obsidian-cli`, `obsidian-markdown` |

`frontend-design` was supplied directly by Tom on 2026-08-05, not cloned from a
public repo. Its frontmatter says `license: Complete terms in LICENSE.txt`, but
no `LICENSE.txt` came with the file, and Tom did not have it to hand when asked
the same day — so the reference stays dangling on purpose. The two sibling
Anthropic skills in this workspace (`skill-creator` here, `canvas-design` in the
portal) both ship Apache-2.0, which is suggestive but not proof, so no licence
text was copied in on that guess. Add the real one when it turns up.
The identical file also lives at
`gt-factory-os-portal/.claude/skills/frontend-design/SKILL.md`; the portal copy
predates this one and was updated to match byte-for-byte.

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
- **The obsidian-skills set targets an Obsidian vault, not this repo.**
  `obsidian-cli` needs the `obsidian` CLI plus a running Obsidian instance, and
  `defuddle` needs the `defuddle-cli` npm package — neither is installed in this
  container, so both are inert until their tool is present. `obsidian-markdown`,
  `obsidian-bases`, and `json-canvas` are pure syntax references and work as-is.
  None of them touch factory-os truth; they only apply to `.md` / `.base` /
  `.canvas` authoring.
- `cavecrew` references subagents (`cavecrew-investigator` / `-builder` /
  `-reviewer`) that were not copied, so its delegation targets do not exist
  in this workspace.

## Updating

Re-clone the upstream repo and copy `skills/<name>/` over the local directory.
There is no lockfile or auto-update wired up.

## License

The four MIT upstreams remain the copyright of their respective authors: Julius
Brussee, Dietrich Gebert, Jesse Vincent, and Steph Ango (@kepano). The MIT license permits
this redistribution provided the copyright and permission notice are retained;
full license text is in each upstream repository's `LICENSE` file.
