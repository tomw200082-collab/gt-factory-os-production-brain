---
name: wiki-lint
description: Health-check the wiki — find orphan pages, contradictions, stale claims, missing cross-references, and knowledge gaps
---

# Wiki Lint

Periodically health-check the wiki. Catches the maintenance debt that accumulates
as the wiki grows.

## Usage

```
/wiki-lint
```

Or naturally:

```
Lint my wiki
Check wiki health
Find orphan pages
Clean up the wiki
```

## Workflow

### Step 1 — Read WIKI.md and index.md

Load the schema and the full page catalog. Build a mental map of what pages exist
and what categories they belong to.

### Step 2 — Orphan check

Find pages in `wiki/` that are not linked from `wiki/index.md` or from any other
wiki page. List them — these are candidates for either deletion or re-linking.

### Step 3 — Contradiction scan

Read the 10-15 most recently updated pages (check frontmatter `last_updated` or
the log). Flag any claims that contradict each other across pages. For each:

```
⚠ Contradiction: wiki/concepts/A.md claims X, but wiki/sources/B.md claims Y
```

### Step 4 — Stale claim check

Look for pages that reference sources but haven't been updated since a newer
source that contradicts or extends them was ingested (use `wiki/log.md` to
establish ingestion order). List pages that may need revisiting.

### Step 5 — Missing page suggestions

Scan all wiki pages for concept or entity names mentioned multiple times that
don't have their own dedicated page. These are candidates for new pages.

### Step 6 — Index consistency check

Verify that every page in `wiki/` appears in `wiki/index.md`. Report any that
are missing from the index.

### Step 7 — Knowledge gap suggestions

Based on what's in the wiki, suggest 3-5 questions that are not well-answered by
the current content — topics that would benefit from new sources or deeper
research. These are starting points for the user's next ingest session.

### Step 8 — Report and append log

Produce a structured lint report:

```markdown
## Lint Report — YYYY-MM-DD

**Orphan pages:** N found
**Contradictions:** N found
**Stale pages:** N found
**Missing from index:** N found
**New page suggestions:** N

### Actions taken
- <list of fixes applied automatically>

### Needs your attention
- <list of contradictions or decisions requiring human judgment>

### Suggested next sources
- <list of knowledge gap suggestions>
```

Append a summary to `wiki/log.md`:

```markdown
## [YYYY-MM-DD] lint | Health check

- Orphans: N | Contradictions: N | Stale: N | Index gaps: N
```
