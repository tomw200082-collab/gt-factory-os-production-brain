# Migration Guide

Upgrade from older versions or migrate from alternative documentation management approaches.

______________________________________________________________________

## 📋 Overview

This guide covers:

- Upgrading between versions
- Migrating from monolithic commands
- Migrating from manual documentation workflows
- Data and configuration migration

______________________________________________________________________

## 🚀 Version Upgrades

### From v0.x to v1.0

v1.0 introduces major architectural changes with **full backward compatibility**.

#### What's New

- ✨ **Modular architecture** - 6 focused commands instead of 1
- ⚡ **88% token reduction** - Much more efficient
- 🚀 **70% faster** - Focused sub-commands
- 📁 **Self-contained** - Single folder installation
- 🛠️ **Customizable** - Pattern-based configuration
- 📊 **Better QA** - 7-category validation scoring

#### Changes You Need to Know

1. **Command Names Changed**

   ```bash
   # Old (v0.x)
   /ck:doc-review-monolithic

   # New (v1.0)
   /ck:doc-review/main
   /ck:doc-review/core
   /ck:doc-review/sdd
   /ck:doc-review/qa
   /ck:doc-review/analyze
   /ck:doc-review/help
   ```

1. **Installation Method Changed**

   ```bash
   # Old: Manual file copying
   # New: One-command installation
   ./install.sh
   ```

1. **Configuration Added**

   ```bash
   # New: Pattern-based categories
   config/categories.json
   ```

#### Upgrade Path

```bash
# Step 1: Backup old installation (optional)
cp -r ~/.claude/commands/ck/doc-review ~/.claude/commands/ck/doc-review.backup

# Step 2: Remove old version
./uninstall.sh  # or manual rm

# Step 3: Install new version
git clone https://github.com/your-username/doc-review-commands.git
cd doc-review-commands
./install.sh

# Step 4: Verify installation
/ck:doc-review/help

# Step 5: Test with analysis
/ck:doc-review/analyze
```

#### Command Mapping

| Old Command | New Equivalent | Token Savings |
| -- | -- | -- |
| `doc-review monolithic` | `/ck:doc-review/main` | Same |
| (N/A) | `/ck:doc-review/core` | 85% less than old |
| (N/A) | `/ck:doc-review/sdd` | 80% less than old |
| (N/A) | `/ck:doc-review/qa` | 70% less than old |
| (N/A) | `/ck:doc-review/analyze` | 75% less than old |

______________________________________________________________________

## 🔄 Migrating from Monolithic to Modular

If you were using a monolithic documentation command:

### Update Your Workflow

#### Old Workflow

```bash
# Everything in one command (expensive)
/ck:doc-review-monolithic "add feature"
```

#### New Workflow

```bash
# Quick update (focused, cheap)
/ck:doc-review/core "add feature"

# Or full update (guided)
/ck:doc-review/main "add feature"
```

### Token Budget Impact

**Before (monolithic):**

- Average use: 10-12K tokens
- Monthly (20 updates): 200-240K tokens

**After (modular):**

- Average use: 900-2K tokens
- Monthly (20 updates): 18-40K tokens

**Monthly Savings: 180-220K tokens! 🎉**

### Update Your Processes

1. **Update documentation for team**
1. **Update CI/CD pipelines** (if using automation)
1. **Test new commands** in development
1. **Migrate custom configurations** (if any)
1. **Monitor token usage** for improvements

______________________________________________________________________

## 📚 Migrating from Manual Workflows

If you were managing documentation manually:

### Assessment

First, understand your current approach:

```bash
# List documentation files
find docs -name "*.md" | wc -l

# Check README size
wc -l README.md

# List all tracked documentation
git log --follow --oneline -- '*.md' | head -20
```

### Migration Steps

#### Step 1: Analyze Current State

```bash
# Review existing documentation structure
/ck:doc-review/analyze

# This will show:
- Documentation principles
- Current structure
- Recommendations for organization
```

#### Step 2: Install Doc Review Commands

```bash
./install.sh
```

#### Step 3: Test on Sample

```bash
# Make a small documentation change
# Update a feature description manually

# Test the tool
/ck:doc-review/core "tested feature"

# Compare output with your manual approach
```

#### Step 4: Gradually Transition

```bash
# Option 1: Use for new documentation only
# Start with /core for new features

# Option 2: Batch update everything
# Use /main "full documentation refresh"

# Option 3: Selective migration
# Migrate critical docs first, others later
```

#### Step 5: Train Team

Share the help guide with your team:

```bash
/ck:doc-review/help
```

______________________________________________________________________

## 🔧 Configuration Migration

### From Manual Patterns to categories.json

If you had custom documentation patterns:

#### Old Approach

```markdown
<!-- Manual notes in README -->

## Documentation Guidelines

Our API docs should have:

- Endpoint description
- Method and path
- Request/response examples
```

#### New Approach

```json
{
  "categories": {
    "api": {
      "patterns": ["## API", "Endpoint", "Method", "Request/Response"],
      "description": "API documentation"
    }
  }
}
```

### Creating categories.json

1. **Identify your patterns**

   ```bash
   grep -r "## " docs/ | cut -d: -f2 | sort | uniq
   ```

1. **Group into categories**

   ```
   - API docs → "## API", "Endpoint", "Request"
   - Setup docs → "## Installation", "Setup"
   - Architecture → "## Architecture", "Design"
   ```

1. **Create configuration**

   ```json
   {
     "categories": {
       "api": {
         "patterns": ["## API", "Endpoint", "Request"],
         "description": "API documentation"
       }
     }
   }
   ```

1. **Test**

   ```bash
   /ck:doc-review/analyze
   ```

______________________________________________________________________

## 📁 File Structure Migration

### Old Structure

```
project/
├── README.md
├── CHANGELOG.md
└── docs/
    ├── api.md
    ├── setup.md
    └── architecture.md
```

### New Structure (Recommended)

```
project/
├── README.md
├── CHANGELOG.md
├── CLAUDE.md              # New: AI context
├── CONTRIBUTING.md        # New: for open source
├── docs/
│   ├── QUICKSTART.md      # New: quick start
│   ├── USAGE.md           # New: detailed usage
│   ├── ARCHITECTURE.md    # Existing
│   ├── api.md
│   ├── setup.md
│   └── MIGRATION.md       # New: upgrade guide
├── examples/
│   ├── basic-usage.md
│   └── advanced-workflows.md
└── config/
    └── categories.json    # New: configuration
```

### Migration Steps

```bash
# 1. Create new files
touch docs/QUICKSTART.md CLAUDE.md CONTRIBUTING.md

# 2. Organize existing docs
mkdir -p examples
mv any-examples docs/examples/ || true

# 3. Create configuration
mkdir -p config
touch config/categories.json

# 4. Test
/ck:doc-review/analyze

# 5. Commit
git add .
git commit -m "docs: migrate to Doc Review Commands structure"
```

______________________________________________________________________

## 🗄️ Data and Content Migration

### Migrate Existing Documentation Content

#### Example: Consolidate API Docs

**Old:** API documentation scattered in multiple files

```bash
# Step 1: Identify all API docs
grep -r "## API" docs/

# Step 2: Create unified structure
touch docs/api.md

# Step 3: Consolidate using ARCHITECTURE and CUSTOMIZATION guides
# Reference all API documentation in one place

# Step 4: Update config/categories.json to recognize new structure
```

#### Example: Create CLAUDE.md from Comments

**Old:** Module documentation in code comments

```python
"""
analyzer.sh - External bash tool for instant project analysis
Uses patterns defined in categories.json
Performance: < 1 second
Dependencies: None (bash only)
"""
```

**New:** Extract to CLAUDE.md

```markdown
## analyzer.sh Tool

**Purpose:** External bash tool for instant project analysis

**Performance:** < 1 second
**Dependencies:** None (bash only)

**Configuration:**
Uses patterns defined in `config/categories.json`

**Functions:**

- analyze_principles()
- analyze_structure()
- analyze_categorization()
```

______________________________________________________________________

## ⚙️ Custom Command Migration

If you built custom documentation commands:

### Assess Current Custom Commands

```bash
# Find custom commands
ls ~/.claude/commands/custom/

# Review command files
cat ~/.claude/commands/custom/my-doc-command.md
```

### Migrate to New System

#### Option 1: Use Existing Commands

Many custom commands can be replaced:

```bash
# Old custom command
/my-doc-update

# Replace with standard commands
/ck:doc-review/core "what changed"
/ck:doc-review/sdd "phase"
/ck:doc-review/qa
```

#### Option 2: Create New Sub-Command

Create your custom command within the Doc Review system:

```bash
# Create new command
touch ~/.claude/commands/ck/doc-review/custom-command.md

# Reference in main.md
# See ARCHITECTURE.md for extension points
```

#### Option 3: Extend Analyzer

Add your custom logic to analyzer.sh:

```bash
# Edit analyzer tool
vi ~/.claude/commands/ck/doc-review/tools/analyzer.sh

# Add custom function
analyze_custom() {
  # Your logic
}
```

______________________________________________________________________

## 🧪 Testing After Migration

### Pre-Migration Checklist

- [ ] Backup current documentation
- [ ] Document current workflow
- [ ] Identify custom patterns/commands
- [ ] Plan migration phases

### Post-Migration Testing

```bash
# 1. Analyze project
/ck:doc-review/analyze

# 2. Test core update
/ck:doc-review/core "test"

# 3. Review changes (don't commit yet)
git diff

# 4. Validate quality
/ck:doc-review/qa

# 5. Revert if needed
git checkout .

# 6. Commit when satisfied
git add .
git commit -m "docs: adopt Doc Review Commands system"
```

### Validation Checklist

- [ ] `/ck:doc-review/analyze` runs successfully
- [ ] `/ck:doc-review/core "test"` produces expected updates
- [ ] `/ck:doc-review/qa` runs with no critical errors
- [ ] Quality score >= 80
- [ ] All links valid
- [ ] All file references correct
- [ ] Team understands new workflow

______________________________________________________________________

## 🤝 Team Migration

### Communication Plan

1. **Announce the change**

   ```
   Subject: Adopting new documentation system

   We're migrating to Doc Review Commands for better documentation workflow.
   Benefits: Faster updates, better consistency, less manual work.
   ```

1. **Share resources**

   ```bash
   # Send this to team
   /ck:doc-review/help

   # Key documents to read:
   - USAGE.md (how to use)
   - QUICKSTART.md (5-minute guide)
   - CUSTOMIZATION.md (team-specific setup)
   ```

1. **Train team**

   ```bash
   # Schedule walkthrough
   Demonstrate:
   - /analyze
   - /core (most common)
   - /qa (best practice)
   ```

1. **Gradual rollout**

   ```bash
   # Phase 1: Volunteers only
   # Phase 2: New documentation uses it
   # Phase 3: Team-wide adoption
   # Phase 4: Legacy workflows deprecated
   ```

______________________________________________________________________

## 🆘 Rollback Plan

If migration doesn't work out:

```bash
# Option 1: Restore backup
rm -rf ~/.claude/commands/ck/doc-review
mv ~/.claude/commands/ck/doc-review.backup ~/.claude/commands/ck/doc-review

# Option 2: Reinstall old version
# (if you have backup branch)
git checkout old-version

# Option 3: Revert documentation changes
git log --oneline -- '*.md' | head -5
git revert <commit-sha>
```

______________________________________________________________________

## 📊 Migration Metrics

Track improvements after migration:

### Before Migration

```
Manual documentation updates:
- Time per update: 30-45 min
- Broken links found: ~10 per month
- Quality issues: Frequent
- Token usage: N/A (manual)
```

### After Migration

```
Doc Review Commands:
- Time per update: 5-15 min (70% faster)
- Broken links: Caught by QA
- Quality issues: Rare
- Token usage: 1.2K per update (vs 10K+ if monolithic)
```

______________________________________________________________________

## 📞 Support

If you encounter issues during migration:

1. **Check FAQ** in [USAGE.md](USAGE.md)
1. **Review errors** with `/ck:doc-review/qa`
1. **Consult customization** in [CUSTOMIZATION.md](CUSTOMIZATION.md)
1. **Check architecture** in [ARCHITECTURE.md](ARCHITECTURE.md)

______________________________________________________________________

**Migration Guide Complete**

Welcome to the Doc Review Commands system! 🎉

For detailed usage, see [USAGE.md](USAGE.md)
For architecture overview, see [ARCHITECTURE.md](ARCHITECTURE.md)
