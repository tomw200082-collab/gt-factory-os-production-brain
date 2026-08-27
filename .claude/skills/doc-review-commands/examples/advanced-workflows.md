# Advanced Workflows

Power user patterns and advanced use cases for Doc Review Commands.

______________________________________________________________________

## 📋 Overview

This guide covers:

- Batch processing workflows
- CI/CD integration
- Multi-phase project workflows
- Custom automation
- Team collaboration patterns

______________________________________________________________________

## 🚀 Advanced Patterns

### Pattern 1: Batch Documentation Updates

**Scenario:** Multiple features completed in a sprint

```bash
# Instead of updating each feature individually:

# Collect all changes
/ck:doc-review/analyze > /tmp/analysis.txt

# Review recommendations
cat /tmp/analysis.txt

# Single update for all changes
/ck:doc-review/core "Sprint 23: 5 features completed"

# Then validate once
/ck:doc-review/qa
```

**Benefits:**

- Single token cost instead of 5x
- One commit instead of 5
- Better documentation of release cohort

______________________________________________________________________

### Pattern 2: Phase-Based SDD Updates

**Scenario:** Multi-phase implementation

```bash
# At phase boundaries, do comprehensive SDD update

# Phase 1 complete
/ck:doc-review/sdd "Phase 1: Core architecture"

# Work on phase 2 (no doc updates)

# Phase 2 complete
/ck:doc-review/sdd "Phase 2: User authentication"

# Never run /sdd mid-phase (wastes tokens)
```

**Structure:**

```bash
Phase 1: Requirements gathering
├── Implement features
├── (no doc updates)
└── /ck:doc-review/sdd at end

Phase 2: Implementation
├── Build functionality
├── (no doc updates)
└── /ck:doc-review/sdd at end
```

______________________________________________________________________

### Pattern 3: Daily Workflow + Weekly QA

**Scenario:** High-velocity development

```bash
# Day 1-4: Quick updates, no QA (saves tokens)
/ck:doc-review/core "added feature"
/ck:doc-review/core "fixed bug"
/ck:doc-review/core "refactored module"

# Friday: Comprehensive QA
/ck:doc-review/qa

# Fix issues found
# (manually edit or re-run /core)

# Weekly commit
git commit -m "docs: weekly documentation update"
```

**Token Efficiency:**

- Daily updates: 1.2K × 4 = 4.8K
- Weekly QA: 1.8K
- **Total: 6.6K tokens**

vs. Daily QA would cost: 4.8K + 7.2K = 12K tokens

______________________________________________________________________

### Pattern 4: Pre-Release Documentation Sprint

**Scenario:** Preparing for release

```bash
# Week before release: Full documentation push

# Step 1: Analyze everything
/ck:doc-review/analyze

# Step 2: Update core files
/ck:doc-review/core "v2.0 release preparation"

# Step 3: Update SDD
/ck:doc-review/sdd "v2.0 release - all features complete"

# Step 4: Validate everything
/ck:doc-review/qa

# Repeat steps 2-4 until score >= 95

# Step 5: Create release
git tag -a v2.0 -m "Release v2.0"
git push origin v2.0
```

**QA Loop:**

```
/core → /qa → Fix → /core → /qa → ...

Continue until:
- Quality score: >= 95/100
- No broken links
- All requirements marked complete
```

______________________________________________________________________

## 🔄 CI/CD Integration

### GitHub Actions Integration

**File:** `.github/workflows/docs.yml`

```yaml
name: Documentation QA

on:
  pull_request:
    paths:
      - "docs/**"
      - "*.md"
      - "commands/**"

jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Doc Review Commands
        run: |
          git clone https://github.com/your-username/doc-review-commands.git
          cd doc-review-commands
          ./install.sh

      - name: Run documentation QA
        run: /ck:doc-review/qa

      - name: Check quality score
        run: |
          SCORE=$(/ck:doc-review/qa 2>&1 | grep "QUALITY SCORE" | grep -o "[0-9]*")
          if [ $SCORE -lt 80 ]; then
            echo "Documentation quality score too low: $SCORE"
            exit 1
          fi
```

### Pre-Commit Hook

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash

# Check if documentation files changed
DOCS_CHANGED=$(git diff --cached --name-only | grep -E '\.(md|yaml|json)$')

if [ ! -z "$DOCS_CHANGED" ]; then
  echo "🔍 Running documentation QA..."

  /ck:doc-review/qa
  SCORE=$((...))  # Extract score

  if [ $SCORE -lt 80 ]; then
    echo "❌ Documentation quality too low ($SCORE/100)"
    exit 1
  fi

  echo "✅ Documentation quality passed ($SCORE/100)"
fi

exit 0
```

### GitHub PR Template

**File:** `.github/pull_request_template.md`

```markdown
## Description

[Description of changes]

## Documentation Changes

- [ ] README updated
- [ ] CHANGELOG updated
- [ ] API docs updated (if applicable)

## Quality Checklist

- [ ] Ran `/ck:doc-review/qa` locally
- [ ] Quality score >= 80
- [ ] All links valid
- [ ] No broken references

## Related Issues

[Issue numbers]
```

______________________________________________________________________

## 🛠️ Custom Workflows

### Workflow 1: API-First Documentation

For API-focused projects:

```bash
# Step 1: Define API in OpenAPI spec
# (external tool)

# Step 2: Generate documentation
/ck:doc-review/core "API v2.0 endpoints"

# Step 3: Update CLAUDE.md with API context
# (manual or custom command)

# Step 4: Validate
/ck:doc-review/qa

# Step 5: Publish
git commit -m "docs: API v2.0 documentation"
git push
```

### Workflow 2: Data Science Project

For ML/data projects:

```bash
# Custom categories in config/categories.json:
# - models
# - datasets
# - experiments

# Workflow:
1. Train new model
   /ck:doc-review/core "trained ResNet v2 model"

2. Run experiment
   /ck:doc-review/core "experiment X results"

3. Update dataset docs
   /ck:doc-review/core "refreshed training dataset"

# Weekly comprehensive update
/ck:doc-review/sdd "Week 10 complete"

# Monthly quality check
/ck:doc-review/qa
```

### Workflow 3: Enterprise Documentation

For large teams:

```bash
# Quarterly documentation overhaul

# Q1: Security documentation
/ck:doc-review/core "Q1: security guidelines"
/ck:doc-review/qa

# Q2: API documentation
/ck:doc-review/core "Q2: API reference update"
/ck:doc-review/qa

# Q3: Architecture documentation
/ck:doc-review/sdd "Q3: architecture refresh"
/ck:doc-review/qa

# Q4: Full documentation review
/ck:doc-review/main "Q4: comprehensive review"
```

______________________________________________________________________

## 👥 Team Collaboration

### Multi-Developer Workflow

**Scenario:** Team of 5 developers

```bash
# Shared guidelines in CLAUDE.md:
# "All features must update documentation"

Developer A:
/ck:doc-review/core "added user authentication"
→ Updates: README, CHANGELOG
→ Commits and pushes

Developer B:
/ck:doc-review/core "added audit logging"
→ Updates: README, CHANGELOG
→ Commits and pushes

Tech Lead (Friday):
/ck:doc-review/qa
→ Check overall quality
→ Fix any cross-cutting issues

Release Manager:
/ck:doc-review/main "v1.2.0 release"
→ Final comprehensive update
→ Tag release
```

### Code Review Checklist

For code reviewers:

```markdown
## Documentation Review

- [ ] Did developer update README? (if user-facing)
- [ ] Did developer update CHANGELOG?
- [ ] Run `/ck:doc-review/qa` on PR branch
- [ ] Quality score >= 80?
- [ ] All links valid?
- [ ] CLAUDE.md updated? (if internal API)
```

### Documentation Lead Role

If someone owns documentation:

```bash
# Daily: Quick review
/ck:doc-review/analyze

# Weekly: Full validation
/ck:doc-review/qa

# Biweekly: Comprehensive update
/ck:doc-review/main "2-week update"

# Monthly: Archive and metrics
# Track quality scores over time
```

______________________________________________________________________

## 📊 Advanced Validation

### Custom QA Workflows

**Scenario:** Very strict quality requirements

```bash
# Run QA multiple times
/ck:doc-review/qa > /tmp/qa-report-1.txt

# Fix issues
# (manual edits)

# Re-run until perfect
/ck:doc-review/qa > /tmp/qa-report-2.txt

# Only commit when score == 100
```

### QA Report Automation

```bash
#!/bin/bash

# Generate quality reports
mkdir -p reports

DATE=$(date +%Y-%m-%d)
OUTPUT="reports/qa-report-$DATE.md"

echo "# Documentation QA Report - $DATE" > $OUTPUT
echo "" >> $OUTPUT

/ck:doc-review/qa >> $OUTPUT

# Track metrics
SCORE=$(grep "QUALITY SCORE" $OUTPUT | grep -o "[0-9]*")
echo "Date,Score" >> reports/metrics.csv
echo "$DATE,$SCORE" >> reports/metrics.csv

# Show trend
tail -5 reports/metrics.csv
```

______________________________________________________________________

## 🚀 Advanced Customization Workflows

### Workflow 1: Project-Specific Categories

```bash
# Customize for your project type
# Edit: ~/.claude/commands/ck/doc-review/config/categories.json

{
  "categories": {
    "database-migration": {
      "patterns": ["## Database", "Migration", "Schema Change"],
      "description": "Database documentation"
    }
  }
}

# Use in your workflow:
/ck:doc-review/core "database schema migration"
```

### Workflow 2: Multi-Language Projects

```bash
# Create language-specific configs
config/categories.python.json
config/categories.javascript.json
config/categories.rust.json

# Use appropriate config based on context:
/ck:doc-review/core "Python API documentation"
# (uses Python config)
```

### Workflow 3: Documentation-as-Code

```bash
# Treat documentation like code

# Create spec for documentation
docs/spec.md
docs/plan.md
docs/tasks.md

# Update specs as documentation evolves
/ck:doc-review/sdd "documentation spec v2"

# Use QA as CI/CD gate
/ck:doc-review/qa

# Require score >= 90 to merge
```

______________________________________________________________________

## 📈 Metrics & Reporting

### Track Documentation Quality Over Time

```bash
#!/bin/bash

# Weekly quality tracking
DATE=$(date +%Y-%m-%d)

# Run analysis
/ck:doc-review/analyze > /tmp/analysis.txt
/ck:doc-review/qa > /tmp/qa.txt

# Extract metrics
LINKS=$(grep "Valid links:" /tmp/qa.txt | grep -o "[0-9]*")
BROKEN=$(grep "Broken links:" /tmp/qa.txt | grep -o "[0-9]*")
SCORE=$(grep "QUALITY SCORE:" /tmp/qa.txt | grep -o "[0-9]*")

# Log metrics
echo "$DATE,$LINKS,$BROKEN,$SCORE" >> metrics.csv

# Generate report
echo "# Documentation Metrics"
echo "Date,Valid Links,Broken Links,Quality Score"
cat metrics.csv
```

### Documentation Health Dashboard

```bash
# Create metrics file (run weekly)
metrics.csv

# Create dashboard visualization
# (using your preferred tool: Excel, Python, etc.)

Week 1: Score 75 → Issues found
Week 2: Score 82 → Improved
Week 3: Score 90 → Good!
Week 4: Score 95 → Excellent!
```

______________________________________________________________________

## 🎓 Learning Workflows

### For New Team Members

```bash
# Week 1: Learn the system
/ck:doc-review/help

# Week 2: Make small docs change
/ck:doc-review/core "added new user to team"

# Week 3: Understand quality
/ck:doc-review/qa

# Week 4: Learn SDD
/ck:doc-review/sdd "example update"

# Week 5: Ready for independent work
```

### For Onboarding Projects

```bash
# When starting new project:

# Step 1: Understand current state
/ck:doc-review/analyze

# Step 2: Set up configuration
# Copy and customize config/categories.json

# Step 3: Initial documentation review
/ck:doc-review/qa

# Step 4: Document findings
mkdir docs/
cp examples/custom-config.json config/

# Step 5: Full documentation update
/ck:doc-review/main "project onboarding setup"
```

______________________________________________________________________

## 🔧 Troubleshooting Advanced Workflows

### Issue: Too Many QA Failures

```bash
# Problem: /qa finds many broken links each time
# Solution: Use /analyze first

/ck:doc-review/analyze
# Review recommendations

# Fix systematically
/ck:doc-review/core "bulk link updates"
```

### Issue: Team Not Using System

```bash
# Problem: Team still updates docs manually
# Solution: Make it easier

# Create team shortcuts
alias docs-update="/ck:doc-review/core"
alias docs-check="/ck:doc-review/qa"

# Add to .zshrc / .bashrc for team
```

### Issue: Merging Documentation Changes

```bash
# Problem: Merge conflicts in generated documentation
# Solution: Consolidate updates

# Instead of: Multiple feature branches updating docs
# Each branch: /ck:doc-review/core separately

# Better: Batch update on main
# Each feature branch: leaves docs alone
# Main branch: Single /ck:doc-review/core for all

# This avoids merge conflicts
```

______________________________________________________________________

## 💡 Advanced Tips

### Tip 1: Use Aliases for Speed

```bash
# Add to shell config
alias dcmd="/ck:doc-review"
alias dcmd-analyze="/ck:doc-review/analyze"
alias dcmd-core="/ck:doc-review/core"
alias dcmd-qa="/ck:doc-review/qa"

# Usage
dcmd-core "feature X"
dcmd-qa
```

### Tip 2: Batch Git Operations

```bash
# After documentation updates
git diff docs/ | head -100  # Preview
git add docs/ *.md          # Stage
git commit -m "docs: $(date +%Y-%m-%d) update"
git push
```

### Tip 3: Leverage Scripting

```bash
#!/bin/bash
# doc-workflow.sh - Automated workflow

for feature in "auth" "api" "ui"; do
  echo "Updating docs for $feature..."
  /ck:doc-review/core "completed $feature implementation"
done

echo "Running quality check..."
/ck:doc-review/qa

echo "Committing..."
git add .
git commit -m "docs: automated update"
```

### Tip 4: Documentation Reviews

```bash
# Treat documentation like code reviews

# Reviewer checklist:
- [ ] Quality score >= 85
- [ ] No broken links
- [ ] All requirements updated
- [ ] Clear and consistent
- [ ] Examples are valid
```

______________________________________________________________________

## 📚 Further Reading

- [USAGE.md](../docs/USAGE.md) - Detailed command reference
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
- [CUSTOMIZATION.md](../docs/CUSTOMIZATION.md) - Advanced customization

______________________________________________________________________

**Advanced Workflows Complete**

You now have patterns and strategies for professional-grade documentation management!
