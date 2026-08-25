# Vendored third-party skills

These skill directories were copied in from public upstream repositories on
2026-08-04, and `apple-design` on 2026-08-25. They are **not** GT Factory OS
governance artifacts — they are general-purpose development-workflow skills.
Nothing here is authority; the authority order in `CLAUDE.md` is unaffected.

| Upstream | License | Skills |
|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review` |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` |
| Anthropic `claude-plugins-official` | Apache-2.0 | `skill-creator` |
| Anthropic (supplied by Tom, 2026-08-05) | see note | `frontend-design` |
| [dickwu/apple-design-skill](https://github.com/dickwu/apple-design-skill) | none stated — see note | `apple-design` |

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

`apple-design` was cloned from `dickwu/apple-design-skill` at commit `d0bac1e`
(2026-02-27, the upstream tip on 2026-08-25). **Upstream ships no `LICENSE`
file** and its README says only "Use at your own discretion." The content is
Apple's publicly available Human Interface Guidelines, rewritten into
framework-agnostic prose — so the underlying material is Apple's, not the
packager's, and no licence grant travels with it. That is materially weaker
provenance than the MIT skills above. It is vendored for internal design review
only; do not redistribute it, and do not treat its text as GT-owned. Flagged
for Tom.

Only `SKILL.md`, `README.md` and `references/` were copied (56 files, ~600 KB).
The upstream `AGENTS.md`, `.cursorrules` and `.gitignore` are for other editors
and were left behind. The identical tree also lives at
`gt-factory-os-portal/.claude/skills/apple-design/`, where the portal
`.gitignore` carries an explicit `!.claude/skills/apple-design/` re-include
(that repo ignores `.claude/skills/*` by default). Keep the two copies
byte-identical when updating.

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
- **`apple-design` is scoped to *app* UI — mobile and desktop, not the web.**
  Its review process assumes Flutter / React Native / Tauri / Electron /
  SwiftUI. The portal is Next.js in a browser, so translate before applying:
  "bottom tab bar" and "safe area" have no portal equivalent, and its ≥44pt
  touch-target rule is the mobile figure. The principles (contrast, type scale,
  spacing, states, dark mode) carry over; the platform-conventions section
  largely does not.
- **`references/hig/right-to-left.md` is the one file worth reading verbatim**
  for this workspace — the Hebrew + `dir="rtl"` surfaces listed in the portal
  `CLAUDE.md` are exactly what it covers.
- **It overlaps `frontend-design` here and `ui-ux-pro-max` in the portal.**
  Three skills can answer "review this UI". `apple-design` is the one that
  cites a written rule per finding; reach for it when a review needs to be
  defensible, not just opinionated.
- `cavecrew` references subagents (`cavecrew-investigator` / `-builder` /
  `-reviewer`) that were not copied, so its delegation targets do not exist
  in this workspace.

## Updating

Re-clone the upstream repo and copy `skills/<name>/` over the local directory.
There is no lockfile or auto-update wired up.

## License

The caveman, ponytail and superpowers upstreams are MIT. Copyright remains with
the respective authors: Julius Brussee, Dietrich Gebert, and Jesse Vincent. The
MIT license permits this redistribution provided the copyright and permission
notice are retained; full license text is in each upstream repository's
`LICENSE` file.

`apple-design` carries no licence grant at all — see its note above. Treat it as the
weakest link in this directory and keep it internal.
