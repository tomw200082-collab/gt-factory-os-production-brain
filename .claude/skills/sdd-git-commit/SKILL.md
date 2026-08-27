---
name: sdd-git-commit
description: Orchestrates a professional Git commit workflow including hygiene checks, documentation parity (SDD), project state tracking (CHANGELOG, TODO, Session Memos), and post-commit reflection.
---

# SDD Git Commit

Use this skill when asked to commit code, push changes, or document progress. It ensures the repository remains clean, documented, and synchronized with its specifications.

## Workflow

### Step 1: Hygiene & Inspection

Review what is about to be committed and ensure no sensitive or temporary files are accidentally staged.

1. **Review Diff**: Run `git diff --staged` (or `git diff HEAD` if nothing is staged) to understand the changes.

1. **Hygiene Check**: Verify that no secrets, local configs, or build artifacts are being committed.

   ```bash
   git status --short
   git diff HEAD --name-only | grep -iE '(cache|node_modules|\.env$|\.secret|\.key$|dist/|build/|__pycache__)' || true
   ```

   _Action_: If matched, unstage the file, update `.gitignore`, and stage `.gitignore`.

### Step 2: Quality & Linting (Optional)

If the project has automated linting or formatting tools, run them now.

```bash
# Example (adjust for project stack: npm run lint, ruff check, etc.)
[ -f "scripts/lint.sh" ] && bash scripts/lint.sh && git add -u
```

### Step 3: Documentation Parity (SDD Gate)

Ensure the codebase and its specifications remain in sync. This is mandatory for any changes in source directories (e.g., `src/`, `lib/`, `app/`).

1. **Identify Specs**: For every modified source file, find its corresponding specification file (usually in `specs/` or `docs/specs/`).
1. **Check Alignment**: Verify that new/modified public functions, classes, CLI signatures, or architectural changes are reflected in the spec.
1. **Update Specs**: Mark implemented components as completed (e.g., in an "Implementation Status" table) and ensure no documentation is left stale.
1. **Stage Changes**: `git add <spec-files>`

### Step 4: Project State Tracking

Update the files that track the project's continuity and history.

| File | Requirement | Action |
| -- | -- | -- |
| `CHANGELOG.md` | **Mandatory** | Prepend a new entry under `# Changelog`. Use `## [Unreleased] - YYYY-MM-DD`. |
| `docs/tasks.md` or `TODO.md` | **Required** | Mark completed tasks `[x]`, newly started tasks `[~]`, or add new tasks. |
| `SESSION_MEMO.md` | **Recommended** | Update "Current Status" and "Next Steps" for hand-off/continuity. |
| `repo-context.md` | **As Needed** | Update if structural architecture, environment, or stack has drifted. |

**Changelog Rules**:

- Sections: `### Added`, `### Changed`, `### Fixed`, `### Removed` (omit empty ones).
- Format: `- **Subject**: concise description`. Write for a reader who did not see the diff.

**Stage Changes**: `git add CHANGELOG.md docs/tasks.md TODO.md SESSION_MEMO.md` (as applicable).

### Step 5: Commit Generation

Follow **Conventional Commits** format.

```text
<type>(<scope>): <short imperative description>

[optional body describing "why" if not obvious]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

- **Subject**: Max 72 chars, present tense, no period.
- **Scope**: Specific component or module (e.g., `api`, `ui`, `parser`).

```bash
git commit -m "<type>(<scope>): <description>"
```

### Step 6: Post-Commit Reflection (Lessons Learned)

Briefly reflect on the work. Was anything surprising, painful, or worth remembering?

1. **Project Specific**: Append to `docs/lessons-learned.md` if it's a project-specific quirk or edge case.
1. **Generic/Reusable**: If you discovered a reusable technique or tool behavior, create/update a dedicated **SKILL** in the appropriate skills directory.
1. **Amending**: If reflection leads to a minor doc update, `git commit --amend` or make a follow-up `docs` commit.

______________________________________________________________________

_Note: This skill is designed to be flexible. Adapt paths (e.g., `specs/` vs `docs/specs/`) and state files to the local project structure._
