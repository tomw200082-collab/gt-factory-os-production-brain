# Vendored third-party skills

These skill directories were copied in from public upstream repositories on
2026-08-04, `apple-design` on 2026-08-25, and the four copywriting skills on
2026-08-26. They are **not** GT Factory OS governance artifacts — they are general-purpose development-workflow skills.
Nothing here is authority; the authority order in `CLAUDE.md` is unaffected.

| Upstream | License | Skills |
|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | MIT | `caveman`, `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review` |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills` |
| Anthropic `claude-plugins-official` | Apache-2.0 | `skill-creator` |
| Anthropic (supplied by Tom, 2026-08-05) | see note | `frontend-design` |
| [dickwu/apple-design-skill](https://github.com/dickwu/apple-design-skill) | none stated — see note | `apple-design` |
| [boraoztunc/skills](https://github.com/boraoztunc/skills) | MIT (README only — no `LICENSE` file) | `ogilvy`, `copywriting`, `copy-editing`, `stop-slop` |

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

The four copywriting skills were cloned from `boraoztunc/skills` at commit
`645553c` (2026-08-15, the upstream tip on 2026-08-26), at Tom's request. That
repo is a **re-publisher**, not the origin of everything it ships: it carries
four separate upstream `LICENSE-*` files for the trees it vendored from others.
Of the four skills taken here, `ogilvy` and `stop-slop` declare `license: MIT`
in their own frontmatter (`stop-slop` also names its author, Hardik Pandya, and
its origin, `hardikpandya/stop-slop`). `copywriting` and `copy-editing` declare
no licence of their own and are covered only by the repo README's one-word
"## License / MIT" — **the repo ships no root `LICENSE` file**, so no copyright
holder and no permission notice travel with them. That is weaker than the MIT
skills above, though stronger than `apple-design`. Flagged for Tom.

`ogilvy/SKILL.md` was modified on adoption: its frontmatter said
`name: ogilvy-copywriting` while its directory is `ogilvy`. Every other skill in
this directory has `name` equal to its directory name, and upstream's own README
documents the command as `/ogilvy`. The `name` field was changed to `ogilvy`.
That is the only edit; the three other files are byte-identical to upstream.

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
- **The copywriting set is English-calibrated to different degrees.** `ogilvy`
  is principle-level (positioning, the promise, headline discipline) and carries
  over to Hebrew intact. `copywriting` and `copy-editing` are process skills —
  the passes and the frameworks (PAS, AIDA, and the rest in
  `copywriting/references/copy-frameworks.md`) are language-neutral, their
  examples are English. `copy-editing/references/plain-english-alternatives.md`
  is an English word-swap table and does nothing for Hebrew copy.
  **`stop-slop` is the outlier: most of its substance is English string
  matching** — a removal list of English throat-clearing phrases, "no em
  dashes", "sentence starts with a Wh- word", "kill the adverbs". Its
  general rules (be specific, active voice, vary rhythm, cut the pull-quote)
  transfer; its lists do not. Do not run it over Hebrew copy and treat the
  result as a clean pass.
- **`copywriting` and `copy-editing` both look for
  `.claude/product-marketing-context.md` and read it before asking questions.**
  That file does not exist in this workspace, so both skills fall back to
  interviewing the user every run. Writing it means writing GT positioning and
  brand voice — doctrine, Tom-approved only (`Sales-Machine/CLAUDE.md` rule 5).
  It was deliberately not authored here.
- **`copywriting` and `content-strategy` reference sibling skills that were not
  vendored** — `email-sequence`, `popup-cro`, `seo-audit`. Those pointers
  resolve to nothing here. Same class of dangling reference as `cavecrew` below.
  `content-strategy` itself was not taken; only the README's "Writing & Copy"
  four.
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

The `boraoztunc/skills` upstream states MIT in its README but ships no root
`LICENSE` file. `ogilvy` and `stop-slop` restate MIT in their own frontmatter;
`copywriting` and `copy-editing` restate nothing. Copyright for `stop-slop`
remains with Hardik Pandya (`hardikpandya/stop-slop`); for the other three,
upstream names no holder.

`apple-design` carries no licence grant at all — see its note above. Treat it as the
weakest link in this directory and keep it internal.

## `agent-reach` — vendored here, 2026-08-29

| Upstream | Commit | License | Skills |
|---|---|---|---|
| [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | `06c202b` (2026-08-25, v1.5.0) | MIT (`agent-reach/LICENSE`) | `agent-reach` |

Read-only access to 15 platforms — Instagram, Facebook, LinkedIn, YouTube
transcripts, Twitter/X, Reddit, RSS, GitHub, Exa web search, and any web page.
Vendored into this repo on Tom's call because the research-flavoured skills that
live here (`messi`, `chief-of-staff-daily`, `domain-investigation`,
`gt-marketing-architect`) are the ones most likely to reach for it.

**It is a Python CLI, not a skill collection.** Only upstream's
`agent_reach/skill/` directory was copied — the package, tests, config and
`pyproject.toml` were not, and must not be (this repo takes no runtime code).
**The commands in the routing table do not exist until `pip install agent-reach`
has run**, and that install is blocked in the remote Claude Code container. In a
web or remote session this skill is documentation, not capability.

**Instagram, Facebook, LinkedIn, Reddit and XiaoHongShu route through OpenCLI
reusing a real logged-in desktop Chrome session.** No container has one, so
those paths cannot work from here at all — only from Claude Code running on a
local machine. The zero-config channels (web page reading, YouTube transcripts,
RSS, GitHub, Exa search, V2EX) work anywhere.

### Account risk — decided 2026-08-29

Reading Instagram, Facebook and LinkedIn through a logged-in browser session is
against those platforms' terms of service, and the session at risk is a live GT
business account. Tom was told, said he understood the risk, and handed the
decision over. **The standing rule, workspace-wide, until Tom overrides it:**

- **Never point Agent Reach at a GT-owned social login.**
- **Use the zero-config channels freely** — public Instagram, Facebook and
  LinkedIn pages read fine through Jina Reader, no session involved.
- **Where authenticated data is genuinely needed**, use the platform's own
  sanctioned API (Meta Graph, LinkedIn), not a browser session.
- **If a logged-in read is ever unavoidable**, throwaway account only — never
  the business account.

Working rule, not doctrine. It changes nothing in the authority order.

### One edit on adoption

Upstream's description is `MUST USE ... anything on the internet`, which would
fire on a large share of ordinary requests in a workspace where the CLI is
absent, sending sessions after commands that do not exist. A **GT note** was
prepended to the body of `SKILL.md` telling the reader to run
`agent-reach doctor --json` first and stop if the command is not found. That is
the only change; the seven `references/` files and `SKILL_zh.md` are
byte-identical to upstream.

`SKILL.md` here is upstream's **English** `SKILL_en.md` (so the loader reads
English); the Chinese original is kept as `SKILL_zh.md`. Note `references/` is
Chinese-only upstream, the LinkedIn one included.

### Keep the two copies identical

The same tree lives at `Sales-Machine/.claude/skills/agent-reach/` and the two
are **byte-identical, GT note included**. Keep them that way when updating. The
note's `.claude/skills/VENDORED.md` pointer is repo-relative, so it resolves in
both. Not copied into `gt-factory-os` or `gt-factory-os-portal` — neither has
any use for reading Instagram, and their lane rules forbid writing outside the
dispatched lane.

Updating: re-clone upstream and copy `agent_reach/skill/` over both directories,
re-applying the English/Chinese filename swap and the GT note. Better: install
the real tool and let it ship its own current skill — upstream's whole value is
chasing platform breakage, which a frozen copy does not receive.

License: MIT, copyright (c) 2025 Agent Eyes; full text in `agent-reach/LICENSE`.

## Vendored in `Sales-Machine`, not here

`Sales-Machine/.claude/skills/` also carries 10 skills from
[google/skills](https://github.com/google/skills) `a7123f8` (Apache-2.0) — Google
Ads (5), Google Analytics (2), Data Manager (3, customer-PII uploads) — plus two
catalog loaders. Advertising and measurement APIs are sales work, so they live
in the sales brain and are **not** duplicated here; that repo's own `VENDORED.md`
carries the full entry. Seven mobile-ads/IMA skills from the same upstream were
taken and deleted the same day on Tom's call — GT has neither a mobile app nor a
video player. Recorded so nobody re-imports them.

Neither set is authority. Same standing as everything above: tools, not truth.
The authority order in `CLAUDE.md` is unaffected.
