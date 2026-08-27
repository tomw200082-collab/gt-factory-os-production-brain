---
name: doc-review-commands
description: Analyze and keep documentation in sync with code changes using specialized commands for core, sdd, qa, and main review workflows.
---

# Doc Review Commands

This skill provides specialized commands to help keep your project's documentation (README, CHANGELOG, Specs, etc.) in sync with code changes.

## Available Commands

- **/ck:doc-review/core**: Update README and CHANGELOG based on recent changes.
- **/ck:doc-review/sdd**: Update Spec-Driven Development (SDD) artifacts (`specs/requirements.md`, `specs/design.md`, `specs/tasks.md`).
- **/ck:doc-review/qa**: Perform a quality check of documentation before commit.
- **/ck:doc-review/main**: Perform a full orchestrated documentation update.
- **/ck:doc-review/analyze**: Run a quick analysis of documentation health.

## Procedures

1. **Analysis**: Use `tools/analyzer.sh` to identify documentation gaps or inconsistencies.
1. **Review**: Review the changes provided by the user and update the relevant documentation files.
1. **Validation**: Use the QA command to ensure all documentation standards are met before finishing.

## Instructions

- Prefer focused sub-commands over a single massive update for better token efficiency.
- Ensure the `CHANGELOG.md` follows standard formatting.
- When updating SDD artifacts, maintain the approval status gates (`DRAFT` vs `APPROVED`).
