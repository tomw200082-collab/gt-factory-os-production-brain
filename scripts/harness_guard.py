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

Requires PyYAML. Frontmatter is validated with a real YAML parser rather than a
line reader, because the whole point is to reject what Claude Code would reject:
`description: Routes: production work` looks fine line-by-line and is invalid
YAML, and a guard that passes it defeats its own purpose.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    sys.exit(
        "harness guard needs PyYAML to validate frontmatter honestly.\n"
        "Install it with:  python3 -m pip install pyyaml"
    )

ROOT = Path(__file__).resolve().parents[1]
IN_ACTIONS = bool(os.environ.get("GITHUB_ACTIONS"))

# Tracked paths that should never hold a credential.
SECRET_PATTERNS = (".env", ".pem", ".p12", ".pfx", "id_rsa", "id_ed25519", "credentials.json")

# A script path inside a hook command, in any of the shapes settings.json uses.
SCRIPT_TOKEN = re.compile(r"[^\s\"'`;|&()]+\.(?:sh|bash|py|mjs|cjs|js|ts)\b")
# Leading ${CLAUDE_PROJECT_DIR:-.}/ or $CLAUDE_PROJECT_DIR/ — resolves to the repo root.
PROJECT_DIR_PREFIX = re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*(?::-[^}]*)?\}/|^\$[A-Za-z_][A-Za-z0-9_]*/")


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


def read_frontmatter(path: Path) -> tuple[dict | None, str]:
    """Parse a file's YAML frontmatter. Returns (mapping, "") or (None, reason)."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"unreadable: {exc}"
    if not lines or lines[0].strip() != "---":
        return None, "no YAML frontmatter block — the asset will not register"
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, "frontmatter fence opened but never closed"
    try:
        data = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0]
        return None, f"frontmatter is not valid YAML ({detail}) — the asset will not register"
    if not isinstance(data, dict):
        kind = type(data).__name__
        return None, f"frontmatter parses as {kind}, not a mapping of fields"
    return data, ""


def check_named_asset(
    report: Report, title: str, targets: list[tuple[Path, str, str]]
) -> None:
    """Shared frontmatter contract: name + description, name matching its owner.

    targets is (file, expected name, what the name must match) — the filename for
    agents, the directory for skills.
    """
    ok, bad = 0, []
    for path, expected, owner in targets:
        if not path.is_file():
            bad.append((rel(path.parent), f"{owner} has no {path.name}"))
            continue
        fields, reason = read_frontmatter(path)
        if fields is None:
            bad.append((rel(path), reason))
        elif not fields.get("name"):
            bad.append((rel(path), "frontmatter has no `name`"))
        elif fields["name"] != expected:
            bad.append((rel(path), f"frontmatter name `{fields['name']}` != {owner} `{expected}`"))
        elif not fields.get("description"):
            bad.append((rel(path), "frontmatter has no `description` — it can never be selected"))
        else:
            ok += 1
    report.check(title, ok, bad)


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
    """Every repo-local script a hook dispatches must be on disk.

    Not just .claude/hooks/ — SessionStart also runs scripts/setup-graphify.sh,
    and a hook whose script has been deleted does not fail loudly; enforcement
    just stops.
    """
    settings = ROOT / ".claude" / "settings.json"
    try:
        config = json.loads(settings.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        report.check("hook scripts exist", 0, [(rel(settings), f"unreadable: {exc}")])
        return

    tokens: set[str] = set()
    for groups in config.get("hooks", {}).values():
        for group in groups:
            for hook in group.get("hooks", []):
                command = hook.get("command", "").replace('"', " ").replace("'", " ")
                tokens.update(SCRIPT_TOKEN.findall(command))

    ok, bad = 0, []
    where = ".claude/settings.json"
    for token in sorted(tokens):
        script = PROJECT_DIR_PREFIX.sub("", token)
        if script.startswith("./"):
            script = script[2:]
        if script.startswith("/"):
            bad.append((where, f"dispatches absolute path {token} — CLAUDE.md forbids machine paths"))
        elif "$" in script:
            bad.append((where, f"dispatches {token}, whose path cannot be resolved to verify it exists"))
        elif (ROOT / script).is_file():
            ok += 1
        else:
            bad.append((where, f"dispatches {token}, which does not exist"))
    report.check("hook scripts exist", ok, bad)


def check_command_heading(report: Report) -> None:
    """Commands in this repo carry no frontmatter; the H1 is the contract.

    Convention across all 15: the first line is `# /` plus the filename.
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
    check_named_asset(
        report,
        "agent frontmatter",
        [(p, p.stem, "filename") for p in sorted((ROOT / ".claude" / "agents").glob("*.md"))],
    )
    check_named_asset(
        report,
        "skill frontmatter",
        [
            (d / "SKILL.md", d.name, "directory")
            for d in sorted(p for p in (ROOT / ".claude" / "skills").iterdir() if p.is_dir())
        ],
    )
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
