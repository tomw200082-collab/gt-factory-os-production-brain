---
name: wiki-init
description: Bootstrap a new wiki — scaffold raw/, wiki/, index.md, log.md, and a starter WIKI.md schema
---

# Wiki Init

Bootstrap a new LLM-maintained wiki in the current project directory.

## Usage

```
/wiki-init
```

Or naturally:

```
Create a new wiki
Initialize my knowledge base
Set up llm-wiki here
```

## Workflow

1. **Confirm location.** Ask the user where the wiki should live (default: `./wiki/`,
   sources at `./raw/`). Confirm before creating anything.

1. **Scaffold directories.**

   ```
   raw/          — drop source documents here
   wiki/         — LLM-generated pages live here
   ```

1. **Create `wiki/index.md`.** Starter catalog with empty category sections:

   ```markdown
   # Wiki Index

   _Last updated: YYYY-MM-DD_

   ## Sources
   <!-- one line per ingested source -->

   ## Concepts
   <!-- key concepts and topics -->

   ## Entities
   <!-- people, organizations, products -->

   ## Analyses
   <!-- comparisons, filed query answers, syntheses -->
   ```

1. **Create `wiki/log.md`.** Append-only chronological record:

   ```markdown
   # Wiki Log

   <!-- Each entry: ## [YYYY-MM-DD] <operation> | <title> -->
   <!-- grep "^## \[" wiki/log.md | tail -10  — last 10 entries -->

   ## [YYYY-MM-DD] init | Wiki created
   ```

1. **Create `WIKI.md` from the installed template** at
   `~/.claude/skills/llm-wiki/tools/wiki-schema-template.md`.
   Ask the user two questions before writing it:

   - What is this wiki about? (one sentence)
   - What are the main categories of content you expect? (e.g. people, companies, concepts)

   Populate the template with their answers, then write it as `WIKI.md` in the
   project root.

1. **Confirm.** Report what was created and tell the user:

   - Drop sources into `raw/` then say "ingest this: <filename>"
   - Ask questions with "what does my wiki say about X"
   - Periodically say "lint my wiki" to keep it healthy
