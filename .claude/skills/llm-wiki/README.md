# LLM Wiki

A skill for building and maintaining a persistent, LLM-managed personal knowledge
base. Implements the pattern described by Andrej Karpathy in
[karpathy/llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Core idea

Instead of re-deriving knowledge from raw documents on every query (RAG), the LLM
**incrementally builds and maintains a wiki** — a structured, interlinked set of
markdown files. Sources are ingested once; the resulting pages accumulate and
cross-reference automatically. The wiki gets richer with every source added and
every question asked.

The human curates sources and asks questions. The LLM handles all the
bookkeeping.

## Installation

```bash
bash plugins/llm-wiki/install.sh
```

Installs to `~/.agents/skills/llm-wiki` (or `~/.claude/skills/llm-wiki` if
`~/.agents` is not present). Supports `--agents`, `--claude`, and `--dir` flags.

## Operations

| Say | What happens |
| -- | -- |
| "create a wiki" | Scaffolds `raw/`, `wiki/`, `index.md`, `log.md`, `WIKI.md` |
| "ingest this: raw/file.md" | Extracts, writes pages, updates index + log |
| "what does my wiki say about X" | Index-first search, cited answer |
| "lint my wiki" | Orphan check, contradiction scan, gap suggestions |

## Wiki structure (in your project)

```
raw/                  — drop sources here (LLM reads, never modifies)
wiki/
  index.md            — full page catalog, updated on every ingest
  log.md              — append-only record (parseable with grep)
  sources/            — one summary page per source
  concepts/           — key ideas and frameworks
  entities/           — people, organizations, products
  analyses/           — filed query answers and syntheses
WIKI.md               — schema: conventions and domain rules (co-evolve this)
```

## WIKI.md

`WIKI.md` is the most important file. It tells the LLM how *your* wiki is
structured — page conventions, category definitions, domain-specific terminology,
and ingest preferences. The `wiki-init` command creates a starter version from a
template; you and the LLM should update it as your workflow evolves.

## Tips

- **Obsidian Web Clipper** converts web articles to markdown — useful for quickly
  populating `raw/`.
- **Obsidian Graph View** shows the shape of your wiki: hubs, orphans, clusters.
- **Dataview plugin** runs queries over page frontmatter (tags, dates, source counts).
- **qmd** ([github.com/tobi/qmd](https://github.com/tobi/qmd)) adds hybrid
  BM25/vector search once the wiki grows past ~100 pages.
- The wiki is a git repo of markdown files — version history and branching for free.
- Log entries use a parseable prefix: `grep "^## \[" wiki/log.md | tail -10`

## Uninstall

```bash
bash plugins/llm-wiki/uninstall.sh
```

Your wiki content (`raw/`, `wiki/`, `WIKI.md`) is never modified by uninstall.
