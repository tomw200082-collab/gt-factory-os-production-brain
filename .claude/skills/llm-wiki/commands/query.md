---
name: wiki-query
description: Answer a question using wiki pages with citations; optionally file the answer as a new wiki page
---

# Wiki Query

Answer questions from the wiki. Use `wiki/index.md` as the entry point — read
it first, drill into relevant pages, then synthesize with citations.

## Usage

```
/wiki-query <question>
```

Or naturally:

```
What does my wiki say about X?
Search my knowledge base for Y
What do I know about Z?
Compare A and B from my notes
```

## Workflow

### Step 1 — Read WIKI.md and index.md

Read `WIKI.md` for schema context, then read `wiki/index.md` to get the full
catalog. Identify which pages are relevant to the question.

### Step 2 — Read relevant pages

Read the identified pages. If a page references other pages that seem relevant,
follow those links (up to 2 hops). Prioritize pages whose descriptions in the
index closely match the question.

### Step 3 — Synthesize the answer

Write a clear answer to the question. Include inline citations as wiki links:
`[claim](wiki/path/to/page.md)`. If pages contradict each other, surface the
contradiction explicitly rather than silently picking one.

Adapt the output format to the question:

- Factual lookup → direct answer with citations
- Comparison → markdown table
- Synthesis across many sources → structured markdown with sections
- Analysis that would be useful long-term → draft as a wiki page (see Step 4)

### Step 4 — Offer to file the answer

After responding, ask: "This seems worth keeping — should I file it as a wiki
page?" If yes:

1. Create `wiki/analyses/<slug>.md` with frontmatter:

   ```yaml
   ---
   title: <descriptive title>
   type: analysis
   date_created: YYYY-MM-DD
   tags: []
   ---
   ```

1. Add the page to `wiki/index.md` under **Analyses**.

1. Append to `wiki/log.md`:

   ```markdown
   ## [YYYY-MM-DD] query | <question summary>

   - Filed as: wiki/analyses/<slug>.md
   ```

### Step 5 — Note gaps

If the question revealed missing information, tell the user: what wasn't covered,
which sources might fill the gap, and whether a lint pass would help surface
related orphan pages.
