# Basic Usage Examples

Common workflows and patterns for everyday use.

## Example 1: Added a New Feature

**Scenario:** You just implemented a new `UserAuth` module.

```bash
# Update core documentation
/ck:doc-review/core "UserAuth module implementation"
```

**What gets updated:**

- `README.md` - Usage examples for UserAuth
- `CLAUDE.md` - AI context about UserAuth module
- `CHANGELOG.md` - v1.2.0 entry with "Added UserAuth"

**Time:** 15-20 seconds

______________________________________________________________________

## Example 2: Completed Implementation Phase

**Scenario:** Phase 2 of your project is complete.

```bash
# Use orchestrator for guided update
/ck:doc-review/main "Phase 2 complete"
```

**Workflow:**

1. Analysis shown (principles, structure, changes, metrics)
1. You're asked: "Which areas to update?"
1. You select: "Core Files" + "SDD Artifacts"
1. Commands execute: `/core` then `/sdd`
1. Aggregated summary shown

**Time:** 60-90 seconds

______________________________________________________________________

## Example 3: Before Git Commit

**Scenario:** You updated several docs, want to ensure quality.

```bash
# Run quality validation
/ck:doc-review/qa
```

**Output:**

```
=== Documentation Quality Report ===

Link Validation: 156 valid, 3 broken
Version Consistency: 1 mismatch found
Overall Score: 87/100

Issues:
1. README.md:45 - broken link to guide.md
2. pyproject.toml version (1.1.5) != README (1.2.0)

Recommendations:
- Fix broken links
- Update pyproject.toml to 1.2.0
```

**Time:** 10-15 seconds

______________________________________________________________________

## Example 4: Understanding Documentation Needs

**Scenario:** Not sure what docs need updating.

```bash
# Run analysis only (no changes)
/ck:doc-review/analyze
```

**Output:**

```
=== Project Documentation Analysis ===

Principles: SDD workflow detected
Structure: 61 .md files (3 root, 17 docs/, 21 specs/)
Recent Changes: 5 files modified in src/

Recommendations:
- Update README.md (new feature in src/auth.py)
- Update CLAUDE.md (module context)
- Update specs/005/plan.md (Phase 2 status)
```

**Time:** < 1 second

______________________________________________________________________

## Example 5: SDD Update After Phase

**Scenario:** Finished implementing Phase 2, need to update specs.

```bash
# Update SDD artifacts only
/ck:doc-review/sdd "Phase 2 tasks complete"
```

**What gets updated:**

- `specs/*/spec.md` - Mark FR-005-1, FR-005-2 complete
- `specs/*/plan.md` - Phase 2 status = ✅ Completed
- `specs/*/tasks.md` - 15 tasks marked done with notes
- `specs/*/contracts/*.md` - Updated API specs

**Time:** 30-45 seconds

______________________________________________________________________

## Example 6: Custom Workflow

**Scenario:** You have a specific workflow.

```bash
# Step 1: Analyze
/ck:doc-review/analyze

# Step 2: Update core (if needed)
/ck:doc-review/core "feature X"

# Step 3: Run QA
/ck:doc-review/qa

# Step 4: Commit
git add .
git commit -m "docs: update for feature X"
```

**Benefits:** Full control, predictable, can interrupt at any step.

______________________________________________________________________

## Tips

1. **Use `:analyze` first** when unsure what needs updating
1. **Use `:core` for quick updates** (most common use case)
1. **Use `:qa` before commits** (catch issues early)
1. **Use `:help` anytime** (comprehensive guide, ~200 tokens)
1. **Use `:main` when overwhelmed** (guided workflow)
