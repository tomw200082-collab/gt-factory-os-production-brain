# Customization Guide

Adapt Doc Review Commands to your project's specific needs and documentation style.

______________________________________________________________________

## 🎯 Customization Overview

Doc Review Commands is **highly customizable** without code changes:

- 📋 Customize file categories via JSON config
- 🎨 Customize templates for documentation style
- 🔧 Customize analyzer behavior with bash functions
- ➕ Add new commands and workflows
- 🚀 Extend functionality for unique needs

______________________________________________________________________

## 📁 Configuration Files

### 1. Pattern Categories (`config/categories.json`)

The main customization file for how documentation is categorized.

**Location:** `~/.claude/commands/ck/doc-review/config/categories.json`

**What it controls:**

- How files are categorized by content patterns
- Essential root files to always consider
- File size thresholds for special handling

### Default Configuration

```json
{
  "categories": {
    "developer": {
      "patterns": ["## API", "### Endpoints"],
      "description": "API documentation"
    },
    "user": {
      "patterns": ["## Installation", "### Setup"],
      "description": "User guides"
    },
    "technical": {
      "patterns": ["## Architecture", "### Design"],
      "description": "Technical specs"
    },
    "ai-agents": {
      "patterns": ["AI", "Claude"],
      "description": "AI integration"
    }
  },
  "essential_root_files": [
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md"
  ],
  "large_file_threshold": 200
}
```

______________________________________________________________________

## 🎨 Customizing Categories

### Step 1: Add New Category

```json
{
  "categories": {
    "my-category": {
      "patterns": ["## My Section", "### My Pattern"],
      "description": "Description of this category"
    }
  }
}
```

### Step 2: Define Patterns

Patterns are regex-like strings that match heading styles and keywords:

```json
{
  "categories": {
    "devops": {
      "patterns": [
        "## CI/CD",
        "### Pipeline",
        "Docker",
        "Kubernetes",
        "Deploy",
        "Infrastructure"
      ],
      "description": "DevOps and deployment docs"
    }
  }
}
```

### Step 3: Use in Documentation

Create sections matching your patterns:

```markdown
## CI/CD Pipeline

# Infrastructure

### Deployment Strategy
```

### Common Categories to Add

#### API Documentation

```json
{
  "api": {
    "patterns": [
      "## API",
      "### Endpoints",
      "Request/Response",
      "curl",
      "POST",
      "GET",
      "PUT",
      "DELETE",
      "PATCH"
    ],
    "description": "REST API documentation"
  }
}
```

#### DevOps & Deployment

```json
{
  "devops": {
    "patterns": [
      "## Deployment",
      "### Docker",
      "## Infrastructure",
      "CI/CD",
      "Pipeline",
      "Kubernetes"
    ],
    "description": "Deployment and infrastructure docs"
  }
}
```

#### Security & Compliance

```json
{
  "security": {
    "patterns": [
      "## Security",
      "### Authentication",
      "## Privacy",
      "Compliance",
      "Encryption",
      "SSL/TLS"
    ],
    "description": "Security and compliance documentation"
  }
}
```

#### Performance & Optimization

```json
{
  "performance": {
    "patterns": [
      "## Performance",
      "### Optimization",
      "Benchmarks",
      "Caching",
      "Memory",
      "CPU"
    ],
    "description": "Performance and optimization guides"
  }
}
```

______________________________________________________________________

## 🔧 Customizing Essential Files

### Modify Essential Root Files

```json
{
  "essential_root_files": [
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md"
  ]
}
```

Use this to ensure specific files are always considered for updates.

### File Size Threshold

```json
{
  "large_file_threshold": 200
}
```

Files larger than 200 lines are handled differently (more careful updates).

______________________________________________________________________

## 📝 Customizing Templates

### Locate Template Files

Templates are defined in the command files:

- `commands/core.md` - README, CLAUDE, CHANGELOG templates
- `commands/sdd.md` - Spec, plan, tasks templates
- `commands/qa.md` - QA validation templates

### Modify README Template Section

Edit the "README Update Template" section in `commands/core.md`:

```markdown
## README Update Template

### Features Section

[Customize feature description format]

### Usage Section

[Customize usage example format]

### Commands Section

[Customize command reference table]
```

### Create Custom Template File

Create a file to store custom templates for your project:

**File:** `~/.claude/commands/ck/doc-review/templates/custom.md`

```markdown
# Custom Templates for [Your Project]

## API Endpoint Template

**Endpoint:** [URL]
**Method:** [GET|POST|PUT|DELETE]
**Authentication:** [Required|Optional]

[Your custom structure]
```

Then reference in commands with:

```bash
See custom templates in templates/custom.md
```

______________________________________________________________________

## 🔨 Customizing the Analyzer

### Locate Analyzer

**File:** `~/.claude/commands/ck/doc-review/tools/analyzer.sh`

### Add Custom Analysis Function

```bash
#!/bin/bash

# ... existing code ...

# Add your custom function
analyze_custom() {
  echo "🔍 Running custom analysis..."

  # Your analysis logic
  grep -r "your-pattern" . | wc -l
}

# Call it in main analysis
main() {
  analyze_principles
  analyze_structure
  analyze_custom  # Your custom analysis
  analyze_impact
}
```

### Custom Analysis Examples

#### Check API Documentation Completeness

```bash
analyze_api_completeness() {
  local api_endpoints=$(grep -c "## API\|### Endpoint" docs/*.md)
  local documentation=$(grep -c "**Endpoint:**\|**Method:**" docs/*.md)

  echo "API endpoints found: $api_endpoints"
  echo "Documented endpoints: $documentation"

  if [ "$api_endpoints" -eq "$documentation" ]; then
    echo "✅ All API endpoints documented"
  else
    echo "⚠️ Missing documentation for $((api_endpoints - documentation)) endpoints"
  fi
}
```

#### Check Example Code Validity

````bash
analyze_examples() {
  local total=$(grep -c '```' docs/*.md)
  local python=$(grep -c '```python' docs/*.md)
  local bash=$(grep -c '```bash' docs/*.md)

  echo "Code examples found: $total"
  echo "  Python: $python"
  echo "  Bash: $bash"
}
````

#### Check Documentation Coverage

```bash
analyze_coverage() {
  local total_files=$(find . -name "*.py" -o -name "*.js" | wc -l)
  local documented=$(grep -l "## Documentation\|documented" docs/*.md | wc -l)
  local percentage=$((documented * 100 / total_files))

  echo "Documentation coverage: $percentage%"

  if [ $percentage -ge 80 ]; then
    echo "✅ Good coverage"
  else
    echo "⚠️ Coverage needs improvement"
  fi
}
```

______________________________________________________________________

## ➕ Creating Custom Commands

### Basic Custom Command Structure

**File:** `~/.claude/commands/ck/doc-review/custom-feature.md`

```markdown
---
description: What your custom command does
allowed-tools: Read(*), Write(*), Edit(*), Bash(*)
---

## Context

[Load any external data needed]

## Task

$ARGUMENTS

## Implementation

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Summary

[Show results]
```

### Example: Custom "Generate Diagrams" Command

```markdown
---
description: Generate Mermaid diagrams from documentation
allowed-tools: Read(*), Write(*), Bash(mermaid)
---

## Context

Mermaid diagram generator for documentation

## Task

Generate diagrams for: $ARGUMENTS

## Implementation

1. Identify architecture sections in documentation
2. Extract components and relationships
3. Generate Mermaid diagram syntax
4. Create diagrams/[name].mmd file
5. Display preview

## Output

📊 Diagram generated: diagrams/[name].mmd

View with:

- GitHub (automatic rendering)
- Mermaid Live Editor
- IDE extensions
```

### Example: Custom "Generate API Docs" Command

```markdown
---
description: Generate API documentation from code
allowed-tools: Read(src/**), Write(docs/api/*)
---

## Context

API documentation generator

## Task

Generate API docs for: $ARGUMENTS

## Implementation

1. Scan source code for API endpoints
2. Extract request/response signatures
3. Generate OpenAPI spec
4. Create formatted documentation
5. Update docs/api/

## Output

📚 API documentation generated for $ARGUMENTS
```

______________________________________________________________________

## 🎯 Customization Patterns

### Pattern 1: Project-Specific Categories

```json
{
  "categories": {
    "database": {
      "patterns": ["## Database", "## Schema", "SQL"],
      "description": "Database documentation"
    },
    "frontend": {
      "patterns": ["## UI", "## Components", "React"],
      "description": "Frontend documentation"
    },
    "backend": {
      "patterns": ["## API", "## Endpoints", "Backend"],
      "description": "Backend documentation"
    }
  }
}
```

### Pattern 2: Extended Essential Files

```json
{
  "essential_root_files": [
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "PRIVACY.md",
    "DEPLOYMENT.md"
  ]
}
```

### Pattern 3: Company-Specific Style

```json
{
  "categories": {
    "company-standards": {
      "patterns": ["Company Policy", "Internal Standards", "Team Guidelines"],
      "description": "Company and team specific docs"
    }
  }
}
```

______________________________________________________________________

## 🔄 Advanced Customizations

### Conditional Configuration

Create environment-specific configs:

```bash
# production config
config/categories.production.json

# development config
config/categories.development.json

# Load based on environment
if [ "$ENV" = "production" ]; then
  CONFIG="config/categories.production.json"
else
  CONFIG="config/categories.development.json"
fi
```

### Multi-Project Configuration

Maintain different configs per project:

```
~/.claude/commands/ck/doc-review/
├── config/
│   ├── categories.json           # Default
│   ├── categories.api-project.json
│   ├── categories.data-project.json
│   └── categories.ml-project.json
```

### Project-Specific Analyzer

```bash
~/.claude/commands/ck/doc-review/tools/
├── analyzer.sh                  # Default
├── analyzer.api.sh              # API-specific
├── analyzer.data.sh             # Data-specific
└── analyzer.ml.sh               # ML-specific
```

______________________________________________________________________

## 🚀 Performance Tuning

### Adjust File Threshold

```json
{
  "large_file_threshold": 250
}
```

- Larger threshold: Faster analysis, less detail
- Smaller threshold: Slower analysis, more detail

### Optimize Patterns

```json
{
  "categories": {
    "api": {
      "patterns": [
        "^## API", // More specific patterns
        "^### Endpoint" // Use regex anchors
      ]
    }
  }
}
```

More specific patterns = faster matching

______________________________________________________________________

## ✅ Customization Checklist

When setting up for your project:

- [ ] Review default categories
- [ ] Add project-specific categories
- [ ] Update essential files list
- [ ] Customize analyzer if needed
- [ ] Create custom commands if needed
- [ ] Test with `/ck:doc-review/analyze`
- [ ] Document custom configurations
- [ ] Share config with team

______________________________________________________________________

## 📚 Customization Examples

### Example 1: Data Science Project

```json
{
  "categories": {
    "models": {
      "patterns": ["## Model", "### Architecture", "Training"],
      "description": "ML model documentation"
    },
    "datasets": {
      "patterns": ["## Data", "### Dataset", "Schema"],
      "description": "Data documentation"
    },
    "experiments": {
      "patterns": ["## Experiment", "### Results", "Metrics"],
      "description": "Experiment tracking"
    }
  }
}
```

### Example 2: Web Application

```json
{
  "categories": {
    "frontend": {
      "patterns": ["## UI", "## Components", "## Design"],
      "description": "Frontend/UI documentation"
    },
    "backend": {
      "patterns": ["## API", "## Endpoints", "## Database"],
      "description": "Backend API documentation"
    },
    "deployment": {
      "patterns": ["## Deployment", "## Docker", "## AWS"],
      "description": "Deployment documentation"
    }
  }
}
```

### Example 3: Microservices Architecture

```json
{
  "categories": {
    "services": {
      "patterns": ["## Service", "### Interface", "## API"],
      "description": "Service documentation"
    },
    "communication": {
      "patterns": ["## Communication", "## Message", "## Protocol"],
      "description": "Inter-service communication"
    },
    "infrastructure": {
      "patterns": ["## Infrastructure", "## Network", "## Config"],
      "description": "Infrastructure and deployment"
    }
  }
}
```

______________________________________________________________________

## 🐛 Troubleshooting Customization

### Issue: Categories Not Applied

**Cause:** Config file not loaded or has syntax errors

**Solution:**

```bash
# Verify config syntax
cat ~/.claude/commands/ck/doc-review/config/categories.json

# Check for JSON errors
python -m json.tool config/categories.json
```

### Issue: Patterns Not Matching

**Cause:** Patterns don't match your documentation style

**Solution:**

1. Check exact heading text in your docs
1. Update patterns to match exactly
1. Test with grep: `grep "pattern" docs/*.md`

### Issue: Analyzer Not Running

**Cause:** analyzer.sh not executable or missing

**Solution:**

```bash
chmod +x ~/.claude/commands/ck/doc-review/tools/analyzer.sh
```

______________________________________________________________________

## 📖 Further Reading

- [Architecture Guide](ARCHITECTURE.md) - System design
- [Templates Guide](TEMPLATES.md) - Documentation templates
- [Usage Guide](USAGE.md) - Command reference

______________________________________________________________________

**Customization Guide Complete**

Your Doc Review Commands system is now ready to adapt to your unique needs!
