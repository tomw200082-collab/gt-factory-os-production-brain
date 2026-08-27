# Vendored third-party skills

These skill directories were copied in from public upstream repositories on
2026-08-04, `apple-design` on 2026-08-25, the four copywriting skills on
2026-08-26, and the nine `ck-skills` workflow skills on 2026-08-27. They are **not** GT Factory OS governance artifacts — they are general-purpose development-workflow skills.
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
| [kimcharli/ck-skills](https://github.com/kimcharli/ck-skills) | MIT (README only — no root `LICENSE` file) | `decision-capture`, `plan-doc`, `session-close`, `sdd-git-commit`, `doc-review-commands`, `sdd-project-init`, `python-repo-init`, `python-lint-fix`, `llm-wiki` |

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

The nine `ck-skills` skills were cloned from `kimcharli/ck-skills` at commit
`90ba1b4` (2026-07-17, the upstream tip on 2026-08-27), at Tom's request. They
are **workflow/governance** skills — spec-driven development, decision capture,
plan-first batches, session handoff — not design or copy skills.

**Licence is the weakest-but-one link in this directory.** The README says
"MIT — see [LICENSE](LICENSE)" but **the repo ships no root `LICENSE` file** and
that link is dead. No skill declares `license:` in its own frontmatter. The only
licence text anywhere in the tree is
`doc-review-commands/LICENSE` — MIT, "Copyright (c) 2025 doc-review-commands
contributors", which covers that one sub-tree and names no individual holder.
So: one of nine skills carries a real permission notice; the other eight are
covered only by a README word whose target does not exist. That is the same
class of gap as `boraoztunc/skills` above, and weaker in that even the README
link is broken. Stronger than `apple-design`, which has no grant at all.
Flagged for Tom.

Upstream lays the skills out under `plugins/ck/skills/<name>/`,
`plugins/llm-wiki/` and `plugins/python-repo-init/skills/python-repo-init/`.
They were flattened to `.claude/skills/<name>/` to match every other skill here.
No file contents were edited; every `name:` already equalled its directory name.
`llm-wiki/install.sh` and `llm-wiki/uninstall.sh` were **not** copied — they
write to `~/.claude` outside the repo, and installer scripts are excluded by the
rule at the end of this file. Everything else each skill needs to run
(`commands/`, `tools/`, `templates/`, `docs/`, `config/`, `scripts/`) came with
it: 97 files.

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

- **Three of the nine are Python-only and inert here.** `python-repo-init`,
  `python-lint-fix` and `sdd-project-init`'s Python branch assume uv/mise, ruff
  and pre-commit. This workspace is TypeScript, SQL and Next.js — `gt-factory-os`
  runs `npm run typecheck`, `tsx --test` and `pg_prove`. Do not run them against
  these repos expecting them to work; they are here for completeness.
- **`session-close` overlaps GT's own `close-session`.** Two skills, near-identical
  names, different jobs. GT's `close-session` is the one that knows this
  workspace: unmerged PRs, live triggers, PR webhook subscriptions, the
  production brain's knowledge layout. Upstream's `session-close` only refreshes
  a `specs/NEXT.md` pointer. **Reach for `close-session` in this workspace.**
- **`plan-doc` and `decision-capture` overlap GT's existing governance, and the
  GT rule wins.** Both write to `specs/` and commit on their own. In this
  workspace decisions belong in `Sales-Machine/doctrine/decisions.md` (Tom sole
  approver, rule 5) or `docs/decisions/` here — **not** a new `specs/` tree, and
  `CLAUDE.md` forbids new authority docs without a Tom decision. Use them for
  their interview-and-write-it-down discipline; route the output to the path GT
  already owns. `decision-capture` also commits and pushes by itself — know that
  before invoking it on a branch you care about.
- **`sdd-git-commit` will want to touch `CHANGELOG.md` and `TODO.md`.** Neither
  is the convention in these repos, and `git add -A` / `git add .` is a stop
  condition in `CLAUDE.md`. Read what it stages before letting it commit.
- **`llm-wiki` overlaps `graphify` and the `Sales-Machine/knowledge/` card
  system.** It maintains its own markdown wiki with its own index; GT already has
  a graded-card registry with authority grades and freshness classes that
  `llm-wiki` knows nothing about. Do not let it become a second knowledge store.
- **`doc-review-commands` carries 31 files, most of them its own documentation**
  (`docs/QA-REPORT.md`, `docs/OPTIMIZATION-ANALYSIS.md`, and so on) describing
  itself rather than helping you use it. The working parts are `SKILL.md`,
  `commands/` and `tools/analyzer.sh`.

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

The `kimcharli/ck-skills` upstream states MIT in its README but the `LICENSE`
link that README points at resolves to nothing — no root licence file exists.
Only `doc-review-commands/LICENSE` carries real MIT text, attributed to
"doc-review-commands contributors" with no named holder. The remaining eight
skills travel with no permission notice. Internal use only; do not redistribute.

`apple-design` carries no licence grant at all — see its note above. Treat it as the
weakest link in this directory and keep it internal.
