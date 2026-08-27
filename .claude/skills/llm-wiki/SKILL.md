---
name: llm-wiki
description: >-
  Maintains a persistent, LLM-managed personal wiki. Activate when the user
  wants to ingest a source ("ingest this", "add to wiki", "process this article",
  "file this"), query their knowledge base ("what does my wiki say", "search my
  wiki", "answer from my notes"), lint the wiki ("lint wiki", "find orphan pages",
  "check wiki health", "clean up wiki"), or bootstrap a new wiki ("create wiki",
  "set up knowledge base", "initialize llm-wiki"). Handles single-source ingest
  workflows, index-first query synthesis, and structural health checks.
---

# LLM Wiki

This skill turns the LLM into a disciplined wiki maintainer. The user curates
sources and asks questions; the LLM handles all the bookkeeping — writing pages,
maintaining cross-references, updating the index, and appending to the log.

## Three-Layer Architecture

```
raw/          — immutable source documents (LLM reads, never modifies)
wiki/         — LLM-generated markdown pages (LLM writes, user reads)
WIKI.md       — schema: conventions, page types, ingest workflow for this domain
```

## Four Operations

- **init** — scaffold the wiki structure for a new project
- **ingest** — process one source into the wiki
- **query** — answer a question from wiki pages with citations
- **lint** — health-check for orphans, contradictions, and gaps

## References

- Original pattern: Andrej Karpathy — LLM Wiki gist
- Optional search: [qmd](https://github.com/tobi/qmd) — local BM25/vector search for markdown
- Optional UI: Obsidian with Graph View, Dataview plugin, Marp plugin
