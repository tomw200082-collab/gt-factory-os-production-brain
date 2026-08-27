# WIKI.md — Schema and Conventions

> **Domain:** <!-- one sentence describing what this wiki is about -->
> **Created:** <!-- YYYY-MM-DD -->
> **Schema version:** 1.0

This file is the configuration document for this wiki. The LLM reads it at the
start of every session to understand the wiki's structure and conventions. You
and the LLM should co-evolve it over time as you figure out what works for your
domain.

______________________________________________________________________

## Directory Structure

```
raw/                  — immutable source documents (LLM reads, never modifies)
wiki/
  index.md            — content catalog (LLM updates on every ingest)
  log.md              — append-only chronological record
  sources/            — one summary page per ingested source
  concepts/           — key ideas, topics, frameworks
  entities/           — people, organizations, products, places
  analyses/           — comparisons, syntheses, filed query answers
```

## Page Categories

<!-- Customize these to match your domain. Examples below. -->

- **sources/** — one page per ingested document. Slug = sanitized filename.
- **concepts/** — recurring ideas or frameworks worth tracking over time.
- **entities/** — named things (people, orgs, products) that appear across sources.
- **analyses/** — filed answers to queries or cross-source syntheses.

## Page Frontmatter

All wiki pages must include YAML frontmatter:

```yaml
---
title: Human-readable title
type: source | concept | entity | analysis
date_created: YYYY-MM-DD
last_updated: YYYY-MM-DD
tags: []
sources: []        # for concept/entity pages: list of raw source filenames
---
```

## Ingest Conventions

<!-- Document your preferences for how sources should be processed. -->

- Summarize sources in 2-3 paragraphs. Lead with the single most important claim.
- Flag contradictions using a `> **Note:** ...` blockquote on the affected page.
- Cross-link aggressively: every named entity or concept should link to its page.
- Do not create a new page for a concept mentioned only once; inline it instead.

## Query Conventions

- Always cite sources as wiki links: `[claim](wiki/path/to/page.md)`.
- Surface contradictions explicitly rather than silently resolving them.
- Offer to file substantive answers as `wiki/analyses/` pages.

## Log Format

Each log entry starts with a parseable prefix for unix tool compatibility:

```
## [YYYY-MM-DD] <operation> | <title>
```

Operations: `init`, `ingest`, `query`, `lint`.

Quick unix queries:

```bash
grep "^## \[" wiki/log.md | tail -10         # last 10 entries
grep "ingest" wiki/log.md                     # all ingests
grep "^## \[2026" wiki/log.md                 # entries from 2026
```

## Domain-Specific Notes

<!-- Add anything the LLM needs to know about your specific domain:
     - Key recurring entities to always cross-link
     - Terminology preferences
     - Sources to treat as authoritative vs. provisional
     - Page types specific to your use case
-->
