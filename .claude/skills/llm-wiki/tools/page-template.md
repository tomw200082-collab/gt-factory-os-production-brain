# Page Frontmatter Reference

All wiki pages created by the LLM must include YAML frontmatter. Use the
appropriate template below based on the page type.

______________________________________________________________________

## Source page — `wiki/sources/<slug>.md`

```yaml
---
title: <source title>
type: source
date_ingested: YYYY-MM-DD
last_updated: YYYY-MM-DD
source_file: raw/<filename>
tags: []
---
```

Body structure:

1. One-sentence summary (the single most important claim)
1. 2-3 paragraph detailed summary
1. `## Key Claims` — bulleted list of notable assertions
1. `## Notable Quotes` — 1-3 direct quotes worth preserving
1. `## Connections` — links to related wiki pages

______________________________________________________________________

## Concept page — `wiki/concepts/<slug>.md`

```yaml
---
title: <concept name>
type: concept
date_created: YYYY-MM-DD
last_updated: YYYY-MM-DD
tags: []
sources: []
---
```

Body structure:

1. One-sentence definition
1. Extended explanation
1. `## Key Properties` or relevant sub-sections for this concept
1. `## Sources` — links to source pages that discuss this concept
1. `## Related Concepts` — links to related concept/entity pages

______________________________________________________________________

## Entity page — `wiki/entities/<slug>.md`

```yaml
---
title: <entity name>
type: entity
entity_kind: person | organization | product | place | other
date_created: YYYY-MM-DD
last_updated: YYYY-MM-DD
tags: []
sources: []
---
```

Body structure:

1. One-sentence description
1. Background / context
1. `## Key Facts` — notable claims sourced from ingested documents
1. `## Sources` — links to source pages mentioning this entity
1. `## Related Entities` — links to related entity/concept pages

______________________________________________________________________

## Analysis page — `wiki/analyses/<slug>.md`

```yaml
---
title: <descriptive title>
type: analysis
date_created: YYYY-MM-DD
last_updated: YYYY-MM-DD
question: <the original question that prompted this analysis>
tags: []
sources: []
---
```

Body structure:

1. Restate the question
1. Answer with inline citations
1. `## Evidence` — key supporting points with source links
1. `## Limitations` — what the wiki doesn't yet cover on this topic
1. `## Follow-up Questions` — questions this analysis raises

______________________________________________________________________

## Contradiction notation

When a new source contradicts an existing claim, add this blockquote to the
affected page immediately after the contradicted claim:

```markdown
> **Note (YYYY-MM-DD):** [source-title](wiki/sources/slug.md) contradicts this,
> claiming instead that <conflicting claim>. Not yet resolved.
```
