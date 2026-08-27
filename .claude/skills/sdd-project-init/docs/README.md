# SDD Project Init

A Claude Code skill that initializes new projects with Spec-Driven Development
structure. Runs an interview and generates all files fully populated — no
placeholders left behind.

## What It Does

- Interviews you on project name, purpose, stack, AI tools
- Creates `AGENTS.md` as the single source of truth for AI instructions (honored by Claude Code, Gemini CLI v0.28.0+, and Copilot v0.19.0+)
- Creates `specs/requirements.md`, `specs/design.md`, `specs/tasks.md`
- Creates `docs/sdd-how-to-apply.md` as a human reference

## Installation

```bash
cp -r plugins/ck/skills/sdd-project-init ~/.claude/skills/sdd-project-init
```

Or from the marketplace (installs the whole `ck` plugin):

```
claude plugin install ck@ck-skills
```

## Usage

In any new project directory, tell Claude Code:

```
/ck:sdd-init
```

Or naturally:

```
Initialize a new project with SDD
Set up a new repo with SDD structure
```

Claude will ask 7 questions, then generate the full project structure in one pass.

## Generated Structure

```
your-project/
├── AGENTS.md                          ← AI constitution + SDD gates (Single Source of Truth)
├── README.md
├── .gitignore
├── docs/
│   └── sdd-how-to-apply.md
└── specs/
    ├── requirements.md                ← Phase 1 (Status: DRAFT)
    ├── design.md                      ← Phase 2 (Status: DRAFT)
    ├── tasks.md                       ← Phase 3 (Status: DRAFT)
    └── features/
        └── _template.md
```

## After Init

```
Open specs/requirements.md and describe what you're building.
Then ask Claude: "Help me complete the requirements for [first feature]."
```
