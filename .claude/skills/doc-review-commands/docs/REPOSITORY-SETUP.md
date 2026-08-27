# Repository Setup Guide

Steps to publish doc-review-commands to GitHub.

## 1. Create GitHub Repository

1. Go to <https://github.com/new>
1. Repository name: `doc-review-commands`
1. Description: `AI-powered documentation management system for Claude Code`
1. Public repository
1. **Do NOT** initialize with README, .gitignore, or license (already have them)
1. Click "Create repository"

## 2. Push Local Repository

```bash
cd /Users/ckim/Projects/doc-review-commands

# Change default branch to main
git branch -M main

# Add remote (replace kimcharli)
git remote add origin https://github.com/kimcharli/doc-review-commands.git

# Push
git push -u origin main
```

## 3. Create First Release

1. Go to repository → Releases → "Create a new release"

1. Tag: `v1.0.0`

1. Release title: `v1.0.0 - Initial Release`

1. Description:

   ````markdown
   ## 🎉 Initial Release

   Doc Review Commands v1.0.0 is here! A modular documentation management system for Claude Code.

   ### ✨ Features

   - 6 modular commands for efficient documentation updates
   - 88% token reduction vs monolithic commands
   - 70% faster execution with focused sub-commands
   - External bash analyzer for instant analysis
   - Pattern-based file categorization
   - SDD (Specification-Driven Development) support
   - Quality validation with 7-category scoring
   - Professional documentation templates

   ### 📦 Installation

   ```bash
   git clone https://github.com/kimcharli/doc-review-commands.git
   cd doc-review-commands
   ./install.sh
   ```
   ````

   ### 🚀 Quick Start

   ```bash
   /ck:doc-review/help      # Show usage guide
   /ck:doc-review/core "X"  # Update core files
   /ck:doc-review/qa        # Quality check
   ```

   ### 📚 Documentation

   - [README](README.md)
   - [Quick Start](docs/QUICKSTART.md)
   - [Examples](examples/basic-usage.md)

   **Full Changelog**: Initial release

   ```

   ```

1. Click "Publish release"

## 4. Update README Links

After creating the repository, update these placeholders in README.md:

```bash
# Replace kimcharli with your GitHub username
sed -i '' 's/kimcharli/your-actual-username/g' README.md
sed -i '' 's/kimcharli/your-actual-username/g' CONTRIBUTING.md

# Commit the changes
git add README.md CONTRIBUTING.md
git commit -m "docs: update repository links"
git push
```

## 5. Repository Settings

### Topics/Tags

Add topics to help discovery:

- `claude-code`
- `documentation`
- `ai-tools`
- `automation`
- `bash`
- `command-line`
- `modular`
- `developer-tools`

### About Section

- Description: "AI-powered documentation management system for Claude Code - 88% token reduction, 70% faster"
- Website: (your blog if you have one)
- Topics: (as above)

### Issues

Enable issues for bug reports and feature requests

### Discussions

Enable discussions for community Q&A

## 6. Optional: GitHub Actions

Create `.github/workflows/test.yml` for automated testing (future enhancement):

```yaml
name: Test Installation

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test installation
        run: |
          ./install.sh
          # Add more tests here
```

## 7. Promote the Repository

- Share on Twitter/X with #ClaudeCode
- Post in Claude Code community
- Add to awesome-claude-code lists
- Share in relevant developer communities

## 8. Maintenance

Regular tasks:

- Respond to issues within 48 hours
- Review pull requests promptly
- Update CHANGELOG.md for each release
- Tag new versions with semantic versioning
- Keep documentation up to date

______________________________________________________________________

## Quick Command Reference

```bash
# Commit changes
git add .
git commit -m "type: description"
git push

# Create new release
git tag v1.1.0
git push origin v1.1.0
# Then create release on GitHub

# View repository
open https://github.com/kimcharli/doc-review-commands
```

______________________________________________________________________

**Your repository is ready to share with the world!** 🚀
