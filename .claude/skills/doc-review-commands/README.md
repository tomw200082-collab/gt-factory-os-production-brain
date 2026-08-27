# doc-review-commands

Keeps project documentation in sync with code changes. Six focused commands
instead of one monolithic tool — 88% token reduction, 70% faster execution.

______________________________________________________________________

## Installation

For marketplace setup and general install instructions, see the
[ck-skills README](../../../../README.md).

**Quick install:**

```bash
# Claude Code (installs the whole ck plugin)
claude plugin install ck@ck-skills

# Copilot CLI
copilot plugin install ck@ck-skills

# Manual
cp -r plugins/ck/skills/doc-review-commands ~/.claude/skills/doc-review-commands
```

______________________________________________________________________

## Usage

All commands are **AI-Native**. Just tell the tool what you want:

| Goal | Activation Intent |
| -- | -- |
| **Full Review** | "review my documentation and update everything" |
| **Analysis Only** | "analyze documentation health" |
| **Core Files (README, CHANGELOG)** | "update core documentation for [change]" |
| **SDD Specs & Tasks** | "update SDD artifacts for [feature]" |
| **Quality Check** | "run a documentation QA check" |

The AI will automatically activate the `doc-review-commands` skill and use its specialized sub-commands to keep your docs in sync.

______________________________________________________________________

## Customization

- Edit `config/categories.json` to customize file categorization patterns
- Modify `commands/*.md` to adjust command behavior
- Extend `tools/analyzer.sh` with custom bash analysis functions

See `docs/CUSTOMIZATION.md` for details.

______________________________________________________________________

## Uninstall

```bash
claude plugin uninstall doc-review-commands   # Claude Code
copilot plugin uninstall doc-review-commands  # Copilot CLI
./uninstall.sh                                # Manual
```

______________________________________________________________________

## Docs

- [Quick Start](docs/QUICKSTART.md)
- [Usage Guide](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Customization](docs/CUSTOMIZATION.md)

______________________________________________________________________

## Related

- [sdd-project-init](../sdd-project-init/README.md) — bootstrap new SDD projects
- [ck-skills](../../../../README.md) — full marketplace README
