# Documentation Templates

Professional templates used by Doc Review Commands for consistent, high-quality documentation updates.

______________________________________________________________________

## 📋 Overview

Doc Review Commands uses pre-defined templates for:

- **README.md** - Features and quick start
- **CLAUDE.md** - AI context and module documentation
- **CHANGELOG.md** - Version entries
- **spec.md** - Specification documents
- **plan.md** - Implementation plans
- **tasks.md** - Task tracking

______________________________________________________________________

## 📖 README.md Templates

### Features Section Template

Used when adding new features to README:

```markdown
## 🎯 New Feature: [Feature Name]

**What it does:**

- ✅ [Benefit 1]
- ✅ [Benefit 2]
- ✅ [Benefit 3]

**When to use:**
[Use case description]

**Example:**
\`\`\`bash
[Example command or code]
\`\`\`

**Output:**
[Expected output]
```

### Quick Start Template

Used for installation and basic usage:

```markdown
## 🚀 Quick Start

### Installation

\`\`\`bash

# Command or instructions

\`\`\`

### Basic Usage

\`\`\`bash

# Common usage example

\`\`\`

**Time:** [Expected execution time]
**Tokens:** [Expected token cost]
```

### Command Reference Template

```markdown
## 🔍 Commands Reference

| Command | Purpose | Tokens | Time |
|------------|---------------|-----------|--------|
| `/command` | [Description] | ~XXX-XXXK | XX-XXs |

### `/command` - [Title]

**What it does:**

- ✅ [Capability 1]
- ✅ [Capability 2]

**When to use:**
[Use cases]

**Syntax:**
\`\`\`bash
/command "argument"
\`\`\`

**Example:**
\`\`\`bash
$ /command "example"
[Expected output]
\`\`\`
```

______________________________________________________________________

## 🤖 CLAUDE.md Templates

### Module Documentation Template

Used for documenting new modules or APIs:

```markdown
## [Module Name]

**Purpose:** [What this module does]

**Key Components:**

- [Component 1] - [Description]
- [Component 2] - [Description]
- [Component 3] - [Description]

**Usage:**
[How to use this module]

**Example:**
[Code example]

**Performance:**

- [Metric 1]: [Value]
- [Metric 2]: [Value]

**Dependencies:**
[Internal/external dependencies]

**Related:**

- [Related module 1]
- [Related module 2]
```

### Function/Class Documentation Template

```markdown
### [Function/Class Name]

**Signature:**
\`\`\`
[Function signature]
\`\`\`

**Parameters:**

- `param1` (type): [Description]
- `param2` (type): [Description]

**Returns:** [Return type and description]

**Example:**
\`\`\`python
[Code example]
\`\`\`

**Notes:**
[Important details, edge cases, gotchas]
```

### Tool/Configuration Template

```markdown
## Configuration

**File:** \`[config file path]\`

**Purpose:** [What this configuration does]

**Structure:**
\`\`\`json
[Example JSON structure]
\`\`\`

**Options:**

- \`key\`: [Description]
- \`key\`: [Description]

**Customization:**
[How users can customize]

**Examples:**
\`\`\`json
[Custom example 1]
\`\`\`
```

______________________________________________________________________

## 📝 CHANGELOG.md Templates

### Version Entry Template

```markdown
## [Version] - [YYYY-MM-DD]

### Added

- [New feature 1]
- [New feature 2]
- [New capability]

### Changed

- [Modified behavior 1]
- [Modified behavior 2]
- [Enhancement]

### Fixed

- [Bug fix 1]
- [Bug fix 2]

### Performance

- [Performance improvement 1]
- [Performance improvement 2]

### Architecture

- [Architecture change 1]
- [Architecture change 2]

### Deprecated

- [Deprecated feature 1]

### Security

- [Security fix 1]
```

### Release Notes Template

```markdown
### Release Highlights

**Major Features:**
✨ [Feature 1] - [Description]
✨ [Feature 2] - [Description]

**Performance:**
⚡ [Improvement 1] - [Metric]
⚡ [Improvement 2] - [Metric]

**Quality:**
🐛 Fixed [Number] bugs
✅ Improved test coverage to XX%

**Migration:**
See [MIGRATION.md](docs/MIGRATION.md) for upgrade instructions
```

______________________________________________________________________

## 🔒 SDD Templates

### Specification Template

```markdown
# Feature [Number]: [Title]

**Status:** [Not Started | In Progress | Complete]

## Requirements

### Functional Requirements

- **FR-XXX-1:** [Requirement description]
  - Acceptance criteria: [Criteria]
  - Status: [✅ Complete | ⏳ In Progress]

- **FR-XXX-2:** [Requirement description]
  - Acceptance criteria: [Criteria]
  - Status: [✅ Complete | ⏳ In Progress]

### Non-Functional Requirements

- **NFR-XXX-1:** [Requirement description]
  - Status: [✅ Complete | ⏳ In Progress]

## Design

[Architecture decisions, design patterns]

## Implementation

[Implementation approach, key files modified]

## Testing

[Test strategy, test cases]
```

### Plan Template

```markdown
# Implementation Plan

## Phase [Number]: [Phase Name]

**Status:** [Not Started | In Progress | Complete]
**Target Completion:** [Date]
**Owner:** [Name]

### Objectives

1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

### Tasks

- [ ] [Task 1] (Est: Xs)
- [ ] [Task 2] (Est: Xs)
- [ ] [Task 3] (Est: Xs)

### Dependencies

- [Dependency 1]
- [Dependency 2]

### Success Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Risks

- [Risk 1]: [Mitigation]
- [Risk 2]: [Mitigation]

### Notes

[Any additional notes]
```

### Task Template

```markdown
## [Task Title]

**Status:** [To Do | In Progress | Done]
**Priority:** [High | Medium | Low]
**Estimated Time:** [Xs]
**Actual Time:** [Xs]

**Description:**
[What needs to be done]

**Acceptance Criteria:**

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

**Notes:**
[Implementation notes, blockers, dependencies]

**Related:**

- [Related task 1]
- [Related task 2]
```

______________________________________________________________________

## 🎨 General Templates

### Usage Pattern Template

```markdown
### Pattern [Number]: [Pattern Name]

**Scenario:** [When to use this pattern]

\`\`\`bash

# Step-by-step example

step1
step 2
step 3
\`\`\`

**Explanation:**
[Why this pattern works]

**Variations:**
[Alternative approaches]

**Best for:** [Use cases]
```

### Architecture Diagram Template

```markdown
### [System Component]

\`\`\`
┌─────────────────┐
│ Component 1 │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Component 2 │
└──────────────────┘
\`\`\`

**Flow:**

1. [Step 1]
2. [Step 2]
3. [Step 3]
```

### Example Template

```markdown
### Example: [Title]

\`\`\`bash

# Input

[Input/Setup]

# Command

[Command to run]

# Output

[Expected output]
\`\`\`

**Explanation:**
[What's happening and why]

**Key Points:**

- [Point 1]
- [Point 2]
```

### Troubleshooting Template

```markdown
### [Problem Description]

**Cause:** [Why this happens]

**Solution:**
\`\`\`bash
[Fix steps or commands]
\`\`\`

**Prevention:**
[How to avoid this issue]

**Related Issues:**

- [Similar issue 1]
- [Similar issue 2]
```

______________________________________________________________________

## 🎯 Template Customization

### When to Use Templates

- ✅ Adding new features
- ✅ Documenting new modules
- ✅ Recording version changes
- ✅ Updating specifications
- ✅ Creating new documentation

### When NOT to Use Templates

- ❌ Minor edits (typos, grammar)
- ❌ Updating existing sections (keep existing style)
- ❌ Internal refactoring (no doc updates needed)

### Adapting Templates

Templates are **guidelines**, not absolute rules:

1. **Keep the structure** - Sections, hierarchy
1. **Adapt content** - Use your own examples, language
1. **Adjust depth** - Add/remove details as needed
1. **Maintain consistency** - Match existing documentation style

______________________________________________________________________

## 📚 Template Usage in Commands

### `/ck:doc-review/core`

Uses these templates:

- README features section
- CLAUDE.md module documentation
- CHANGELOG.md version entry

### `/ck:doc-review/sdd`

Uses these templates:

- spec.md requirement sections
- plan.md phase sections
- tasks.md task entries

### `/ck:doc-review/main`

Uses all templates above

______________________________________________________________________

## 🔧 Creating Custom Templates

### Step 1: Identify Pattern

Look for repeating documentation structures in your project:

```bash
# Example: Your project always documents APIs like this
## API: [Name]
**Endpoint:** [URL]
**Method:** [GET|POST|etc]
**Response:** [Type]
```

### Step 2: Create Template

```markdown
## API: [Name]

**Endpoint:** `[URL]`
**Method:** [GET|POST|PUT|DELETE|PATCH]
**Authentication:** [Required|Optional|None]

**Request:**
\`\`\`json
[Example request]
\`\`\`

**Response:**
\`\`\`json
[Example response]
\`\`\`

**Status Codes:**

- `200` - [Success description]
- `400` - [Error description]
```

### Step 3: Document Template

Create a section in your CLAUDE.md or custom templates file:

```markdown
## Custom API Documentation Template

[Your template]

**Usage:**
Used when documenting REST API endpoints.

**Examples:**
[Examples of how template is used]
```

### Step 4: Use in Commands

Mention your custom template in command files, and it will be used for updates.

______________________________________________________________________

## 💡 Best Practices

### 1. Keep Templates Simple

- ✅ Clear sections
- ✅ Easy to fill in
- ❌ Don't over-specify
- ❌ Avoid unnecessary complexity

### 2. Be Consistent

- Use same templates across project
- Maintain consistent style
- Update all templates when adding new patterns

### 3. Provide Examples

- Show filled-in template examples
- Demonstrate before/after
- Include multiple variations

### 4. Document Templates

- Explain when to use each template
- List required vs optional sections
- Provide customization guidelines

### 5. Review Regularly

- Update templates based on usage
- Simplify if too complex
- Add new templates for new patterns

______________________________________________________________________

## 📖 Example: Complete Feature Documentation

Here's a complete example using templates:

### README Section

```markdown
## 🎯 New QA Command

Comprehensive quality validation with 7-category scoring.

**What it does:**

- ✅ Validates all markdown links
- ✅ Checks file:line references
- ✅ Verifies terminology consistency
- ✅ Generates quality score (0-100)

**When to use:**
Before committing documentation changes.

**Example:**
\`\`\`bash
/ck:doc-review/qa
\`\`\`

**Output:**
[Sample QA output with scoring]
```

### CLAUDE.md Section

```markdown
## QA Command

**Purpose:** Validate documentation quality across the project

**Key Functions:**

- Link validation
- Cross-reference checking
- Terminology consistency
- Completeness verification

**Usage:**
\`\`\`bash
/ck:doc-review/qa
\`\`\`

**Scoring Categories:**

1. Link Validation (20%)
2. Cross-References (15%)
3. Terminology (15%)
4. Versions (15%)
5. SDD (15%)
6. Examples (10%)
7. Completeness (10%)

**Related:** analyzer tool, main command
```

### CHANGELOG Section

```markdown
### Added

- New `/ck:doc-review/qa` command for quality validation
- 7-category documentation scoring system
- Broken link detection and reporting
- Terminology consistency checking
```

______________________________________________________________________

**Templates Guide Complete**

For usage examples, see [USAGE.md](USAGE.md)
For customization, see [CUSTOMIZATION.md](CUSTOMIZATION.md)
