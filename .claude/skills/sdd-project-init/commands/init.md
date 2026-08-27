---
name: init
description: Interview-driven SDD project initializer — creates AGENTS.md, specs/, docs/ fully populated
---

# /ck:sdd-init — SDD Project Initializer

Initialize a new project with Spec-Driven Development structure by running a
short interview, then calling `create-project.sh` to generate exact copies of
the model file tree with variable substitution.

> If the interview reveals a **Python** stack, suggest the `python-repo-init`
> skill instead (its Python-specific successor) before proceeding.

## Trigger Phrases

- `/ck:sdd-init`
- "initialize a new project"
- "set up a new repo with SDD"
- "create a project skeleton"
- "apply SDD to this project"

---

## Step 1 — Interview

Ask ALL questions before generating anything. Collect all answers first.

```
1. Project name?          (e.g. ck-apstra-tool)
2. What does it do?       (1–2 sentences)
3. Language / stack?      (e.g. Python/uv, Node/TypeScript, Go)
4. Runtime target?        (CLI | service | library | web app)
5. External integrations? (e.g. "Apstra REST API" — or press Enter to skip)
6. Full repo path?        (e.g. /Users/ckim/Projects/my-new-tool)
```

If the user skips a question, use a sensible default and note it.

______________________________________________________________________

## Step 2 — Run create-project.sh

After collecting all answers, run:

```bash
${CLAUDE_PLUGIN_ROOT}/tools/create-project.sh \
  --name       "<project_name>" \
  --purpose    "<project_purpose>" \
  --stack      "<language_stack>" \
  --runtime    "<runtime_target>" \
  --integrations "<integrations_or_empty>" \
  --path       "<repo_path>"
```

The script copies the model file tree from `template/`, substitutes variables,
and runs `git init` + initial commit.

______________________________________________________________________

## Step 3 — Confirm to the user

After the script succeeds, report:

```
✓ <project_name> initialized at <repo_path>

Files created:
  AGENTS.md                          — AI constitution + SDD gates
  README.md                          — project overview
  .gitignore
  docs/sdd-how-to-apply.md           — SDD workflow reference
  specs/requirements.md              — Phase 1 (Status: DRAFT)
  specs/design.md                    — Phase 2 (Status: DRAFT)
  specs/tasks.md                     — Phase 3 (Status: DRAFT)
  specs/features/_template.md        — per-feature spec template

Next step:
  Open specs/requirements.md and describe what you're building.
  Then: "Help me complete requirements for [first feature]."
```
