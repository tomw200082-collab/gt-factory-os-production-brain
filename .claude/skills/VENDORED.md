# Vendored third-party skills

These skill directories were copied in from public upstream repositories on
2026-08-04, and the `taste-skill` pack on 2026-08-09. They are **not** GT
Factory OS governance artifacts — they are general-purpose development-workflow
and design skills. Nothing here is authority; the authority order in `CLAUDE.md`
is unaffected.

| Upstream | License | Skills |
|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review` |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | MIT | `design-taste-frontend`, `design-taste-frontend-v1`, `gpt-taste`, `image-to-code`, `redesign-existing-projects`, `high-end-visual-design`, `full-output-enforcement`, `minimalist-ui`, `industrial-brutalist-ui`, `stitch-design-taste`, `imagegen-frontend-web`, `imagegen-frontend-mobile`, `brandkit` |
| Anthropic `claude-plugins-official` | Apache-2.0 | `skill-creator` |
| Anthropic (supplied by Tom, 2026-08-05) | see note | `frontend-design` |

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
- `cavecrew` references subagents (`cavecrew-investigator` / `-builder` /
  `-reviewer`) that were not copied, so its delegation targets do not exist
  in this workspace.

### The `taste-skill` pack (13 skills, 2026-08-09)

- **Only 2 of the 13 were mirrored to the portal** — `redesign-existing-projects`
  and `full-output-enforcement`. The rest live here only, deliberately. See
  `gt-factory-os-portal/.claude/skills/VENDORED.md` for the reasoning.
- **`design-taste-frontend` scopes itself out of the portal.** Its own first line
  reads "Landing pages, portfolios, and redesigns. Not dashboards, not data
  tables, not multi-step product UI." That is a precise description of
  `gt-factory-os-portal`. Use it for marketing pages, brand sites, and decks —
  not for operator surfaces.
- **The aesthetic skills contradict each other by design.** `high-end-visual-design`
  (agency/cinematic), `minimalist-ui` (warm monochrome editorial), and
  `industrial-brutalist-ui` (Swiss/military terminal) each mandate a different
  type scale, palette, and motion budget. Invoke at most one per task; loading
  two produces incoherent output.
- **`gpt-taste` and `image-to-code` are written for GPT/Codex**, not Claude.
  `gpt-taste` additionally mandates GSAP and "Python-driven true randomization".
  Kept for completeness; expect to adapt rather than follow literally.
- **`stitch-design-taste` targets Google Stitch**, which is not a tool in this
  workspace. It emits a `DESIGN.md`; it does not write application code.
- **`design-taste-frontend-v1` exists only for backward compatibility** with
  projects pinned to v1 behaviour. Nothing here is pinned to it — it was taken
  because Tom asked for the full pack. Candidate to drop if the near-duplicate
  description starts competing with v2 in trigger-matching.
- **None of the 13 account for RTL or Hebrew.** The portal's Hebrew surfaces are
  enumerated in `gt-factory-os-portal/CLAUDE.md`; these skills know nothing
  about them.
- **Directory names were changed on the way in.** Upstream directory names do not
  match their `name:` frontmatter (`skills/taste-skill/` declares
  `name: design-taste-frontend`), and this workspace requires directory ==
  skill name. The rename map is in **Updating** below.

## Updating

Re-clone the upstream repo and copy `skills/<name>/` over the local directory.
There is no lockfile or auto-update wired up.

Do **not** use `npx skills add` — it installs to the container's global
`~/.claude/skills`, which is ephemeral and does not survive a session restart.
That is the same problem documented for `skill-creator` above.

`taste-skill` is the exception to the copy rule: its upstream directory names do
not match the `name:` in each file's frontmatter, so copy `skills/<upstream>/`
to `.claude/skills/<skill name>/` using this map.

| upstream `skills/` dir | local dir (== skill name) |
|---|---|
| `taste-skill` | `design-taste-frontend` |
| `taste-skill-v1` | `design-taste-frontend-v1` |
| `gpt-tasteskill` | `gpt-taste` |
| `image-to-code-skill` | `image-to-code` |
| `redesign-skill` | `redesign-existing-projects` |
| `soft-skill` | `high-end-visual-design` |
| `output-skill` | `full-output-enforcement` |
| `minimalist-skill` | `minimalist-ui` |
| `brutalist-skill` | `industrial-brutalist-ui` |
| `stitch-skill` | `stitch-design-taste` |
| `imagegen-frontend-web` | unchanged |
| `imagegen-frontend-mobile` | unchanged |
| `brandkit` | unchanged |

Upstream `skills/llms.txt` is an index file and was not copied.
`stitch-design-taste/DESIGN.md` is part of that skill and travels with it.

## License

All four upstreams are MIT. Copyright remains with the respective authors:
Julius Brussee, Dietrich Gebert, Jesse Vincent, and Leonxlnx (`taste-skill`,
Copyright (c) 2026). The MIT license permits this redistribution provided the
copyright and permission notice are retained; full license text is in each
upstream repository's `LICENSE` file.
