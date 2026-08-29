#!/usr/bin/env python3
"""Structural guard for the GT Factory OS harness.

The .claude/ tree is this repo's product: 19 agents, 15 commands, 49 skills and
4 hooks. Nothing in it is compiled or type-checked, so a malformed file does not
raise an error -- the agent or skill simply stops being registered, silently.
This script is the mechanical backstop.

It runs identically in two places:

  * locally, before you commit:  python3 scripts/harness_guard.py
  * in CI, on every PR:          .github/workflows/harness-guard.yml

Read-only. It validates and reports; it never edits a file. Every check prints
an N/N count per the CLAUDE.md evidence standard, and a failure names the exact
file and what is wrong with it.

Stdlib only, by design -- this repo has no package manifest and should not grow
one just to lint itself.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_ACTIONS = bool(os.environ.get("GITHUB_ACTIONS"))

# Tracked paths that should never hold a credential.
SECRET_PATTERNS = (".env", ".pem", ".p12", ".pfx", "id_rsa", "id_ed25519", "credentials.json")


class Report:
    """Collects per-check results so one run reports every problem, not just the first."""

    def __init__(self) -> None:
        self.failed = False

    def check(self, title: str, passed: int, failures: list[tuple[Path | str, str]]) -> None:
        total = passed + len(failures)
        mark = "FAIL" if failures else "PASS"
        print(f"[{mark}] {title}: {passed}/{total}")
        for path, reason in failures:
            print(f"       {path} — {reason}")
            if IN_ACTIONS:
                print(f"::error file={path}::{reason}")
        if failures:
            self.failed = True


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_frontmatter(path: Path) -> dict[str, str] | None:
    """Return top-level `key: value` pairs from a YAML frontmatter block.

    Deliberately minimal: the harness only ever reads `name` and `description`
    off the top level, so a full YAML parser would be a dependency bought for
    nothing. Returns None when the file opens without a `---` fence.
    """
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if line.startswith((" ", "\t", "-")) or ":" not in line:
            continue  # nested value or list item — not a top-level key
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return None  # fence opened but never closed


def check_json_parses(report: Report) -> None:
    """Every JSON file under .claude/ must parse.

    settings.json is the one most at risk: tooling rewrites it wholesale, and a
    truncated write costs every hook and permission in the repo at once.
    """
    ok, bad = 0, []
    for path in sorted((ROOT / ".claude").rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
            ok += 1
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            bad.append((rel(path), f"does not parse as JSON: {exc}"))
    report.check("JSON under .claude/ parses", ok, bad)


def check_settings_hooks_exist(report: Report) -> None:
    """Every hook script settings.json dispatches must be on disk.

    A renamed or deleted hook script does not fail loudly — the harness just
    stops enforcing whatever that hook enforced.
    """
    settings = ROOT / ".claude" / "settings.json"
    try:
        config = json.loads(settings.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        report.check("settings.json hook scripts exist", 0, [(rel(settings), f"unreadable: {exc}")])
        return

    referenced: set[str] = set()
    for groups in config.get("hooks", {}).values():
        for group in groups:
            for hook in group.get("hooks", []):
                command = hook.get("command", "")
                for token in command.replace('"', " ").replace("'", " ").split():
                    if ".claude/hooks/" in token:
                        referenced.add(token[token.index(".claude/hooks/"):])

    ok, bad = 0, []
    for script in sorted(referenced):
        if (ROOT / script).is_file():
            ok += 1
        else:
            bad.append((".claude/settings.json", f"dispatches {script}, which does not exist"))
    report.check("settings.json hook scripts exist", ok, bad)


def check_agent_frontmatter(report: Report) -> None:
    """Agents need name + description, and the name must match the filename."""
    ok, bad = 0, []
    for path in sorted((ROOT / ".claude" / "agents").glob("*.md")):
        fields = read_frontmatter(path)
        if fields is None:
            bad.append((rel(path), "no closed YAML frontmatter block — agent will not register"))
        elif not fields.get("name"):
            bad.append((rel(path), "frontmatter has no `name`"))
        elif fields["name"] != path.stem:
            bad.append((rel(path), f"frontmatter name `{fields['name']}` != filename `{path.stem}`"))
        elif not fields.get("description"):
            bad.append((rel(path), "frontmatter has no `description` — the router cannot route to it"))
        else:
            ok += 1
    report.check("agent frontmatter", ok, bad)


def check_skill_frontmatter(report: Report) -> None:
    """Skills need SKILL.md with name + description, name matching the directory."""
    ok, bad = 0, []
    for directory in sorted(p for p in (ROOT / ".claude" / "skills").iterdir() if p.is_dir()):
        path = directory / "SKILL.md"
        if not path.is_file():
            bad.append((rel(directory), "skill directory has no SKILL.md"))
            continue
        fields = read_frontmatter(path)
        if fields is None:
            bad.append((rel(path), "no closed YAML frontmatter block — skill will not register"))
        elif not fields.get("name"):
            bad.append((rel(path), "frontmatter has no `name`"))
        elif fields["name"] != directory.name:
            bad.append((rel(path), f"frontmatter name `{fields['name']}` != directory `{directory.name}`"))
        elif not fields.get("description"):
            bad.append((rel(path), "frontmatter has no `description` — the skill will never be selected"))
        else:
            ok += 1
    report.check("skill frontmatter", ok, bad)


def check_command_heading(report: Report) -> None:
    """Commands in this repo carry no frontmatter; the H1 is the contract.

    Convention across all 15: the first line is `# /<filename>`.
    """
    ok, bad = 0, []
    for path in sorted((ROOT / ".claude" / "commands").glob("*.md")):
        expected = f"# /{path.stem}"
        try:
            first = path.read_text(encoding="utf-8-sig").splitlines()[0].strip()
        except (OSError, IndexError, UnicodeDecodeError):
            bad.append((rel(path), "empty or unreadable"))
            continue
        if first == expected:
            ok += 1
        else:
            bad.append((rel(path), f"first line is `{first}`, expected `{expected}`"))
    report.check("command headings", ok, bad)


def check_no_secret_files(report: Report) -> None:
    """No credential-shaped file may be tracked. CLAUDE.md forbids committing secrets."""
    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        report.check("no tracked secret files", 0, [("<git>", f"could not list tracked files: {exc}")])
        return

    bad = []
    for name in tracked:
        base = name.rsplit("/", 1)[-1]
        if base == ".env" or base.startswith(".env.") or any(
            base.endswith(p) or base.startswith(p) for p in SECRET_PATTERNS if p != ".env"
        ):
            bad.append((name, "credential-shaped file is tracked in git"))
    report.check("no tracked secret files", len(tracked) - len(bad), bad)


def main() -> int:
    print(f"harness guard — {rel(ROOT / '.claude')} structural checks\n")
    report = Report()
    check_json_parses(report)
    check_settings_hooks_exist(report)
    check_agent_frontmatter(report)
    check_skill_frontmatter(report)
    check_command_heading(report)
    check_no_secret_files(report)
    print()
    if report.failed:
        print("harness guard: FAIL — see the annotated lines above.")
        return 1
    print("harness guard: PASS — every check green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
