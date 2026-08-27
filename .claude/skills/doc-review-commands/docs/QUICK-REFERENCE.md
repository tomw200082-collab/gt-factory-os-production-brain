# doc-review-commands Quick Reference

**Optimized for speed, efficiency, and minimal token usage**

______________________________________________________________________

## Command Overview

| Command | Use Case | Tokens | Time | Cache |
| -- | -- | -- | -- | -- |
| **quick** | Simple updates (README/CLAUDE/CHANGELOG) | 400-600 | < 30s | ✅ |
| **analyze** | Understand what needs updating | 600-800 | 2-3s | ✅ |
| **core** | Full README/CLAUDE/CHANGELOG update | 1.2-1.5K | 2-3s | ✅ |
| **sdd** | Update SDD artifacts (spec/plan/tasks) | 1.5-1.8K | 2-3s | — |
| **validate** | Check links, references, versions | < 200 | < 5s | — |
| **qa** | Full quality assurance | 1.8-2K | 2-3s | — |

______________________________________________________________________

## When to Use Each Command

### 🚀 QUICK (Fastest - Recommended for most updates)

**Use when:**

- Adding a feature to README
- Documenting new module in CLAUDE.md
- Adding CHANGELOG entry
- You know exactly what to change

**Command:**

```bash
/ck:doc-review:quick "added payment integration feature"
```

**Cost:** 400-600 tokens | **Time:** < 30s

______________________________________________________________________

### 📊 ANALYZE (Understanding impact)

**Use when:**

- You want to see what needs updating
- Making complex changes
- First time working with the system

**Command:**

```bash
/ck:doc-review:analyze
```

**Cost:** 600-800 first run, 100-200 on cache hit | **Time:** 2-3s

______________________________________________________________________

### ✏️ CORE (Full standard documentation update)

**Use when:**

- Multiple documentation updates needed
- Want analysis before updating
- Full README/CLAUDE/CHANGELOG refresh

**Command:**

```bash
/ck:doc-review:core "new API endpoints"
```

**Cost:** 1.2-1.5K | **Time:** 2-3s

______________________________________________________________________

### 📝 SDD (Specification Driven Development)

**Use when:**

- Updating spec.md requirements
- Documenting implementation plan
- Marking tasks as complete
- Updating design contracts

**Command:**

```bash
/ck:doc-review:sdd "phase 1 completion"
```

**Cost:** 1.5-1.8K | **Time:** 2-3s

______________________________________________________________________

### ✔️ VALIDATE (Fast bash validation)

**Use when:**

- Checking documentation before commit
- Verifying links aren't broken
- Checking file references are valid
- Ensuring version consistency

**Commands:**

```bash
# All validation checks
/ck:doc-review:validate

# Specific checks
~/.claude/tools/doc-analyzer.sh validate-links
~/.claude/tools/doc-analyzer.sh validate-references
~/.claude/tools/doc-analyzer.sh validate-versions
```

**Cost:** < 200 tokens | **Time:** < 5s

______________________________________________________________________

### 🔍 QA (Complete quality assurance)

**Use when:**

- Before committing documentation changes
- Want comprehensive validation
- Need full quality report

**Command:**

```bash
/ck:doc-review:qa
```

**Cost:** 1.8-2K | **Time:** 2-3s

______________________________________________________________________

## Cache Management

**Check cache status:**

```bash
~/.claude/tools/doc-analyzer.sh cache
```

**Clear all cache:**

```bash
~/.claude/tools/doc-analyzer.sh clear-cache
```

**Clear specific cache:**

```bash
~/.claude/tools/doc-analyzer.sh clear-cache principles
```

**Cache TTL:**

- Analysis: 1 hour
- Impact: 30 minutes
- Metrics: 24 hours

______________________________________________________________________

## Token Savings Tips

### 50-70% Savings (Quick Mode)

```bash
# Instead of:
/ck:doc-review:core "new feature"  # 1.2-1.5K tokens

# Do this:
/ck:doc-review:quick "new feature"  # 400-600 tokens
```

### 85% Savings (Cached Analysis)

```bash
# First analysis run: 600-800 tokens
/ck:doc-review:analyze

# 5 minutes later: 100-200 tokens (cached!)
/ck:doc-review:analyze
```

### 100% Savings (Bash Validation)

```bash
# Validation: 0 AI tokens (pure bash)
/ck:doc-review:validate
```

______________________________________________________________________

## Common Workflows

### Adding a New Feature

**Step 1: Quick update (400-600 tokens)**

```bash
/ck:doc-review:quick "added user authentication"
```

**Step 2: Validate before commit (< 200 tokens)**

```bash
/ck:doc-review:validate
```

**Total: ~600 tokens**

______________________________________________________________________

### Complex Documentation Update

**Step 1: Analyze impact (600-800 tokens, or 100-200 cached)**

```bash
/ck:doc-review:analyze
```

**Step 2: Full update (1.2-1.5K tokens)**

```bash
/ck:doc-review:core "refactored API"
```

**Step 3: Quality check (1.8-2K tokens)**

```bash
/ck:doc-review:qa
```

**Total: ~3.6-4.3K tokens**

______________________________________________________________________

### Releasing a Version

**Step 1: Quick CHANGELOG update (400-600 tokens)**

```bash
/ck:doc-review:quick "version 2.0.0 release"
```

**Step 2: Validate (< 200 tokens)**

```bash
~/.claude/tools/doc-analyzer.sh validate-versions
```

**Total: ~600 tokens**

______________________________________________________________________

## Quick Decision Tree

```
What do you need?
│
├─ Just update README/CLAUDE/CHANGELOG?
│  └─ /ck:doc-review:quick
│
├─ Want to understand impact first?
│  └─ /ck:doc-review:analyze
│
├─ Need full analysis + update?
│  └─ /ck:doc-review:core
│
├─ Updating SDD artifacts?
│  └─ /ck:doc-review:sdd
│
├─ Check before committing?
│  └─ /ck:doc-review:validate
│
└─ Everything + quality assurance?
   └─ /ck:doc-review:qa
```

______________________________________________________________________

## Token Budget Examples

### Light Usage (5 updates/month)

```
3 x quick:        1.2-1.8K tokens
1 x analyze:      0.6-0.8K tokens
1 x validate:     < 0.2K tokens
─────────────────────────────────
Total: ~2-2.8K tokens/month
```

### Medium Usage (15 updates/month)

```
8 x quick:        3.2-4.8K tokens
4 x analyze:      0.4-0.8K tokens (cached)
2 x core:         2.4-3K tokens
1 x qa:           1.8-2K tokens
─────────────────────────────────
Total: ~8-11K tokens/month
```

### Heavy Usage (30 updates/month)

```
15 x quick:       6-9K tokens
8 x analyze:      0.8-1.6K tokens (mostly cached)
5 x core:         6-7.5K tokens
1 x sdd:          1.5-1.8K tokens
1 x qa:           1.8-2K tokens
─────────────────────────────────
Total: ~16-22K tokens/month
```

______________________________________________________________________

## Documentation Files

- **OPTIMIZATION-ANALYSIS.md** - Complete optimization strategy and implementation details
- **../commands/quick.md** - Lightweight mode guide
- **~/.claude/tools/doc-analyzer.sh help** - Tool documentation

______________________________________________________________________

## Support

For detailed optimization information:

```bash
cat docs/OPTIMIZATION-ANALYSIS.md
```

For quick command help:

```bash
~/.claude/tools/doc-analyzer.sh help
```

______________________________________________________________________

**Last Updated:** 2025-10-24
**Version:** Optimization Complete (Phases 1-4)
**Expected Token Savings:** 40% overall reduction
