# __PROJECT_NAME__

__DESCRIPTION__

For engineering conventions and decision history, see
[`specs/workflow.md`](specs/workflow.md); for domain analysis, see
[`docs/README.md`](docs/README.md).

## Status

**Scaffolded (__DATE__).** AI-agent workflow governance is in place; see
[`specs/NEXT.md`](specs/NEXT.md) for what's next.

## Setup

```bash
git config core.hooksPath .githooks # once per clone (convention guard, stdlib-only)
uv sync --dev                       # deps + test tooling
```

## Usage

```bash
uv run pytest                       # run tests
```

## Why the repo is shaped this way

The engineering workflow — spec-first, one-skill-per-module, test-alongside,
mechanical convention enforcement — is documented in
[`specs/workflow.md`](specs/workflow.md) and [`specs/memory.md`](specs/memory.md).
The read-this-first session pointer is [`specs/NEXT.md`](specs/NEXT.md).
