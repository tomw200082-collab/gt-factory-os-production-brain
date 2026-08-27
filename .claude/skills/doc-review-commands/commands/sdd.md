---
description: Update SDD artifacts (spec.md, plan.md, tasks.md, contracts)
allowed-tools: Bash(find:*), Bash(git:*), Read(*), Write(*), Edit(*), Grep(*), Glob(*)
---

# SDD Artifacts Update Command

## Context

- SDD files:
  !`find ./specs -name "spec.md" -o -name "plan.md" -o -name "tasks.md" | sort`
- Recent changes:
  !`git diff --name-only HEAD~5..HEAD 2>/dev/null || echo "No recent commits"`

## Task

**Update SDD artifacts for:** $ARGUMENTS

SDD stands for Specification-Driven Development.

**Target files:**

- specs/\*/spec.md - Functional requirements
- specs/\*/plan.md - Implementation plan
- specs/\*/tasks.md - Task breakdown
- specs/_/contracts/_.md - Design contracts

---

## Step 1: Identify Relevant Spec Directory

Based on $ARGUMENTS, determine which spec directory to update:

- Extract feature number (e.g., "feature 005" → specs/005-\*)
- Or identify by feature name
- List matching directories found

______________________________________________________________________

## Step 2: Update spec.md (Functional Requirements)

### Read Current spec.md

Read the relevant specs/\*/spec.md file.

### Update Requirements

**What to update:**

1. **Mark Completed Requirements:**

   - Find requirements (FR-\*) that are now implemented
   - Change status markers:
     - [ ] → [x] for completed
     - Add ✅ emoji if used in doc

1. **Add New Requirements (if discovered during implementation):**

```markdown
### FR-[N]: [Requirement Title]

**Priority:** [High/Medium/Low]
**Status:** [Planned/In Progress/Completed]

**Description:**
[What the requirement is]

**Acceptance Criteria:**

- [ ] Criterion 1
- [ ] Criterion 2

**Implementation Notes:**
[Details from actual implementation]
```

3. **Update Requirement Details:**
   - Add implementation notes to existing requirements
   - Update acceptance criteria based on what was actually built
   - Note any deviations from original plan

### Make Updates

Apply changes using Edit tool.

______________________________________________________________________

## Step 3: Update plan.md (Implementation Plan)

### Read Current plan.md

Read the relevant specs/\*/plan.md file.

### Update Plan Status

**What to update:**

1. **Phase Completion:**

```markdown
## Implementation Phases

### Phase 1: [Name]

**Status:** ✅ Completed
**Completion Date:** YYYY-MM-DD

**Implemented:**

- [What was built]
- [What was built]

**Deviations:**

- [Any changes from original plan]
```

2. **Architecture Decisions:**

```markdown
### Architecture Decision: [Title]

**Decision:** [What was decided]
**Rationale:** [Why this approach was chosen]
**Alternatives Considered:** [Other options]
**Implementation:** path/to/file.py:123
**Trade-offs:**

- Pro: [Benefit]
- Con: [Cost]
```

3. **Design Patterns Used:**

```markdown
### Design Pattern: [Pattern Name]

**Location:** path/to/implementation.py:123
**Purpose:** [Why this pattern was used]
**Implementation Details:** [How it's implemented]
```

4. **Risk Updates:**
   - Mark mitigated risks as resolved
   - Add any new risks discovered
   - Update risk status

### Make Updates

Apply changes using Edit tool.

______________________________________________________________________

## Step 4: Update tasks.md (Task Breakdown)

### Read Current tasks.md

Read the relevant specs/\*/tasks.md file.

### Update Task Status

**What to update:**

1. **Mark Completed Tasks:**

```markdown
- [x] Task name
  - **Status:** ✅ Completed
  - **Completion Date:** YYYY-MM-DD
  - **Implementation:** path/to/file.py:123
  - **Notes:** [Any lessons learned or important details]
```

2. **Update In-Progress Tasks:**

```markdown
- [ ] Task name
  - **Status:** 🔄 In Progress (60% complete)
  - **Current State:** [What's done, what's remaining]
  - **Blockers:** [Any issues]
```

3. **Add New Tasks (if discovered):**

```markdown
- [ ] New task discovered during implementation
  - **Priority:** High
  - **Dependency:** [Other tasks this depends on]
  - **Estimate:** [Time estimate]
```

### Make Updates

Apply changes using Edit tool.

______________________________________________________________________

## Step 5: Update Design Contracts (if applicable)

### Find Contract Files

Look for specs/_/contracts/_.md files related to this feature.

### Update Contracts

**What to update:**

1. **API Contracts:**

````markdown
## Endpoint: [Name]

**Method:** GET/POST/etc
**Path:** /api/v1/resource

**Request:**

```json
{
  "param": "value"
}
```
````

**Response:**

```json
{
  "result": "value"
}
```

**Implementation:** path/to/handler.py:123

````

2. **Interface Contracts:**
```markdown
## Interface: [ClassName]

**Location:** path/to/file.py:123

**Methods:**
- `method_name(param: Type) -> ReturnType`
  - Purpose: [What it does]
  - Example: [Usage example]
````

3. **Data Schema Contracts:**
   - Update schema definitions to match actual implementation
   - Add examples with real data
   - Document any schema changes

### Make Updates

Apply changes using Edit tool for each contract file.

______________________________________________________________________

## Step 6: SDD Consistency Validation

**Cross-check consistency:**

- [ ] spec.md requirements match implementation
- [ ] plan.md phases align with completed tasks
- [ ] tasks.md references correct file:line locations
- [ ] Contracts match actual API/interface implementation
- [ ] No orphaned requirements (in spec but not in plan/tasks)
- [ ] All completed tasks have corresponding requirement markers

**If inconsistencies found:**

- Document them
- Fix or note as deviations with explanation

______________________________________________________________________

## Output: Summary

### 📊 SDD Documentation Update Summary

**Scope:** $ARGUMENTS

**Spec Directory:** specs/[directory]

**Files Updated:**

| File | Updates Made | Lines Changed |
| -- | -- | -- |
| spec.md | [FR-X completed, FR-Y updated] | ~[estimate] |
| plan.md | [Phase X status, architecture decisions] | ~[estimate] |
| tasks.md | [X tasks completed, Y added] | ~[estimate] |
| contracts/\*.md | [Contracts updated] | ~[estimate] |

**Requirement Status:**

- Completed: [count] requirements
- In Progress: [count] requirements
- Remaining: [count] requirements

**Phase Status:**

- Completed phases: [list]
- Current phase: [name] ([%] complete)
- Remaining phases: [list]

**SDD Consistency:**

- [x] Requirements ↔ Implementation aligned
- [x] Plan ↔ Tasks aligned
- [x] Contracts ↔ Code aligned
- [x] No orphaned requirements
- [x] All references accurate

**Execution Time:** [X]s

______________________________________________________________________

## Next Steps

Recommended actions:

- [ ] Review SDD updates: `git diff specs/`
- [ ] Update core docs: `/ck:doc-review/core $ARGUMENTS`
- [ ] Run QA validation: `/ck:doc-review/qa`
- [ ] Commit SDD updates with message like: `docs(sdd): Update spec 005 for feature implementation`
