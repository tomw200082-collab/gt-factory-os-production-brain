---
name: wiki-ingest
description: Process one raw source document and integrate it into the wiki — write/update pages, update index, append log entry
---

# Wiki Ingest

Process a single source document into the wiki. One source at a time; stay
involved rather than batch-ingesting unsupervised.

## Usage

```
/wiki-ingest <filename>
```

Or naturally:

```
Ingest this: research/paper.md
Add this article to my wiki
Process raw/meeting-notes.md
File this into the wiki
```

## Workflow

### Step 1 — Read WIKI.md

Read `WIKI.md` to load the schema: page conventions, category structure, and any
domain-specific ingest rules the user has established. If `WIKI.md` is missing,
prompt the user to run `wiki-init` first.

### Step 2 — Read the source

Read the source file from `raw/` (or the path the user specified). Read any
images referenced in the source separately if needed for context.

### Step 3 — Discuss key takeaways

Before writing anything, briefly summarize (3-5 bullets) what you found in the
source and ask: "Anything you want me to emphasize or de-emphasize before I
update the wiki?" Wait for the user's response.

### Step 4 — Write the source summary page

Create `wiki/sources/<slug>.md` using the page template frontmatter:

```yaml
---
title: <source title>
type: source
date_ingested: YYYY-MM-DD
source_file: raw/<filename>
tags: []
---
```

The page body: 2-3 paragraph summary, key claims, notable quotes, and a
"## Connections" section noting which wiki pages this source relates to.

### Step 5 — Update entity and concept pages

For each significant entity or concept mentioned in the source:

- If a wiki page already exists for it: read the existing page, then append or
  revise with new information. Note any contradictions with existing claims using
  a `> **Note:** This contradicts <page> which claims...` blockquote.
- If no page exists: create `wiki/<type>/<slug>.md` using the page template.

Aim to touch 5-15 pages per source. Prefer updating existing pages over creating
new ones unless the concept clearly warrants its own page.

### Step 6 — Update `wiki/index.md`

Add the source to the **Sources** section. Add or update entries for any new or
significantly updated concept/entity pages. One line per entry:

```markdown
- [Page Title](path/to/page.md) — one-line description
```

### Step 7 — Append to `wiki/log.md`

```markdown
## [YYYY-MM-DD] ingest | <source title>

- Summary page: wiki/sources/<slug>.md
- Pages created: <list>
- Pages updated: <list>
- Contradictions flagged: <count or "none">
```

### Step 8 — Report

Tell the user:

- How many pages were created vs. updated
- Any contradictions flagged
- Any questions or gaps you noticed that a future source could fill
