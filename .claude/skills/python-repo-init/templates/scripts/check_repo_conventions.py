#!/usr/bin/env python3
"""Pre-commit guard for repo conventions documented in specs/workflow.md.

This script only checks mechanical, deterministic things -- it cannot verify
that a decision's reasoning was sound, or that an agent actually read
specs/memory.md. See specs/workflow.md Section 8 for full context and limits.

Checks:
  1. AGENTS.md stays under a line-count ceiling (catches re-inlining content
     that should live in docs/README.md or specs/workflow.md).
  2. AGENTS.md does not contain content-markers that belong in
     specs/workflow.md (provenance-header fields, skill-spec template).
  3. CLAUDE.md, GEMINI.md, and .github/copilot-instructions.md stay thin
     pointers: small line-count ceiling + must link to AGENTS.md.
  4. No staged text file under data/01_raw/ or data/03_generated/ contains an
     obvious plaintext secret (private-key header, AWS key, password /
     plain-text-password / pre-shared-key with a real value). A line ending in
     the marker 'conventions:allow-secret' is exempt -- use it for
     deliberately-committed non-secrets the patterns can't distinguish.
  5. Any staged file under data/03_generated/ contains the required provenance
     header (generated_by / spec / source / generated_at).
  6. Any commit touching src/**/*.py or data/03_generated/** also has a
     specs/**/*.md change -- either in the same commit/PR range, or (for a
     local single-commit check) in the immediately preceding commit. Coarse,
     intentionally narrow backstop for the spec-before-or-with-code practice
     (workflow.md Section 3).
  7. Any commit touching src/**/*.py, data/03_generated/**, or another
     specs/**/*.md file also touches specs/NEXT.md -- backstop for the "update
     the session-start pointer before ending" convention. Same one-commit
     lookback coarseness as check 6.

Exit code 0 = all checks pass. Non-zero = at least one violation, with a
human-readable explanation printed to stderr.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

AGENTS_MD_MAX_LINES = 70
POINTER_FILE_MAX_LINES = 20

# Markers that indicate engineering content has leaked back into AGENTS.md
# instead of staying in its canonical home (specs/workflow.md).
FORBIDDEN_AGENTS_MD_MARKERS = [
    (
        "generated_by:",
        "provenance-header detail belongs in specs/workflow.md Section 5a, not AGENTS.md",
    ),
    (
        "### Skill:",
        "the skill-spec template belongs in specs/workflow.md Section 5, not AGENTS.md",
    ),
]

POINTER_FILES = ["CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"]

PROVENANCE_FIELDS = ["generated_by", "spec", "source", "generated_at"]

# Directories whose staged text content is scanned for un-sanitized secrets.
SECRET_SCAN_PREFIXES = ("data/01_raw/", "data/03_generated/")

# (label, compiled regex). group(1) of a value-bearing pattern must not be a
# placeholder (see PLACEHOLDER_RE) to count as a violation.
SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"), None),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), None),
    (
        "plaintext password",
        re.compile(r"(?:plain-text-password|pre-shared-key\s+ascii-text)\s+(\S+)", re.IGNORECASE),
        1,
    ),
    (
        "password assignment",
        re.compile(r"(?:password|passwd|secret)\s*[:=]\s*(\S+)", re.IGNORECASE),
        1,
    ),
]
PLACEHOLDER_RE = re.compile(
    r"^[\"']?(redacted|placeholder|changeme|example|none|null|dummy|fake|sample|hashed|sanitized|x{3,}|\*{3,}|<[^>]+>|\$\{[^}]+\}|\.{3,})[\"']?$",
    re.IGNORECASE,
)

# Opt-out marker for check 4: a line carrying this string is never flagged.
# For values the placeholder heuristics can't recognize as safe (e.g. an
# already-hashed credential in a sanitized config dump).
ALLOW_SECRET_MARKER = "conventions:allow-secret"

errors: list[str] = []


def staged_files() -> list[str]:
    """Return the list of relevant changed files.

    In a local pre-commit hook, this is the staged diff. In CI, there is no
    staging area for a push/PR range, so CHECK_CONVENTIONS_BASE_REF (if set) is
    used to diff against instead -- see .github/workflows/repo-conventions.yml.
    Renames (R) are included so a rename-plus-tweak can't dodge content checks.
    """
    base_ref = os.environ.get("CHECK_CONVENTIONS_BASE_REF")
    if base_ref:
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR", base_ref, "HEAD"]
    else:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return [line for line in result.stdout.splitlines() if line]


def file_text(rel_path: str) -> str | None:
    """Content of rel_path as it will be committed, not as it sits on disk.

    In local pre-commit mode the staging area is authoritative, so read the
    staged blob (git show :path) -- otherwise an unstaged working-tree edit
    could mask or fake a violation. In CI mode the checkout IS the commit, and
    for paths not in the index (or no repo yet), fall back to the working tree.
    Returns None if the file has no readable content anywhere.
    """
    path = REPO_ROOT / rel_path
    if not os.environ.get("CHECK_CONVENTIONS_BASE_REF"):
        result = subprocess.run(
            ["git", "show", f":{rel_path}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            errors="ignore",
        )
        if result.returncode == 0:
            return result.stdout
    if not path.exists() or path.is_dir():
        return None
    try:
        return path.read_text(errors="ignore")
    except (UnicodeDecodeError, OSError):
        return None


def check_agents_md_size() -> None:
    content = file_text("AGENTS.md")
    if content is None:
        return
    line_count = len(content.splitlines())
    if line_count > AGENTS_MD_MAX_LINES:
        errors.append(
            f"AGENTS.md has {line_count} lines (ceiling: {AGENTS_MD_MAX_LINES}). "
            "AGENTS.md loads into every session -- keep it a minimal pointer map. "
            "Move domain content to docs/README.md or specs/workflow.md instead."
        )


def check_agents_md_duplication() -> None:
    content = file_text("AGENTS.md")
    if content is None:
        return
    for marker, reason in FORBIDDEN_AGENTS_MD_MARKERS:
        if marker in content:
            errors.append(f"AGENTS.md contains '{marker}': {reason}")


def check_pointer_files_thin() -> None:
    for rel_path in POINTER_FILES:
        content = file_text(rel_path)
        if content is None:
            errors.append(f"{rel_path} is missing -- required as a thin pointer to AGENTS.md.")
            continue
        line_count = len(content.splitlines())
        if line_count > POINTER_FILE_MAX_LINES:
            errors.append(
                f"{rel_path} has {line_count} lines (ceiling: {POINTER_FILE_MAX_LINES}). "
                "It must stay a thin pointer to AGENTS.md, not host duplicated content."
            )
        if "AGENTS.md" not in content:
            errors.append(f"{rel_path} does not reference AGENTS.md -- it must point to it.")


def check_no_secrets_in_data() -> None:
    for rel_path in staged_files():
        if not rel_path.startswith(SECRET_SCAN_PREFIXES):
            continue
        content = file_text(rel_path)
        if content is None:
            continue
        for lineno, line in enumerate(content.splitlines(), start=1):
            if ALLOW_SECRET_MARKER in line:
                continue
            for label, pattern, value_group in SECRET_PATTERNS:
                m = pattern.search(line)
                if not m:
                    continue
                if value_group is not None and PLACEHOLDER_RE.match(m.group(value_group)):
                    continue
                errors.append(
                    f"'{rel_path}':{lineno} contains an un-sanitized secret ({label}). "
                    "Sample inputs/outputs must be sanitized -- replace the value with a "
                    "placeholder or move the file to data/work/. See specs/workflow.md "
                    "Section 5a / check 4."
                )
                break


def check_generated_provenance() -> None:
    for rel_path in staged_files():
        if not rel_path.startswith("data/03_generated/"):
            continue
        if Path(rel_path).name == ".gitkeep":
            continue
        content = file_text(rel_path)
        if content is None:
            continue
        head = content[:2000]
        missing = [field for field in PROVENANCE_FIELDS if field not in head]
        if missing:
            errors.append(
                f"'{rel_path}' is under data/03_generated/ but is missing provenance "
                f"field(s) {missing} in its header. See specs/workflow.md Section 5a."
            )


def _is_code_change(rel_path: str) -> bool:
    return (rel_path.startswith("src/") and rel_path.endswith(".py")) or rel_path.startswith(
        "data/03_generated/"
    )


def _is_spec_change(rel_path: str) -> bool:
    return rel_path.startswith("specs/") and rel_path.endswith(".md")


def _previous_commit_files() -> list[str]:
    """Files touched in the commit at HEAD (the commit immediately preceding the
    one currently being staged). Only meaningful outside CI mode. Uses --root so
    this also works when HEAD is the repo's first commit. Returns [] if there is
    no HEAD yet.
    """
    has_head = subprocess.run(
        ["git", "rev-parse", "--verify", "-q", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if has_head.returncode != 0:
        return []
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def check_spec_before_or_with_code() -> None:
    """Backstop for the spec-before-or-with-code practice (workflow.md Section 3).

    In CI mode, staged_files() spans the full push/PR range, so a spec touched
    anywhere in that range satisfies the check. In local pre-commit mode, this
    also allows the spec to have landed in the immediately preceding commit.
    Known limitation: a chain of multiple code-only commits following one spec
    commit will fail past the first one -- intentional coarseness, not a bug.
    """
    files = staged_files()
    code_files = [f for f in files if _is_code_change(f)]
    if not code_files:
        return
    if any(_is_spec_change(f) for f in files):
        return
    if os.environ.get("CHECK_CONVENTIONS_BASE_REF"):
        errors.append(
            f"This push/PR touches {code_files} but no specs/**/*.md file changed "
            "anywhere in the range. Capture the design decision in specs/ before "
            "or alongside implementing it -- see specs/workflow.md Section 3."
        )
        return
    if any(_is_spec_change(f) for f in _previous_commit_files()):
        return
    errors.append(
        f"This commit touches {code_files} but no specs/**/*.md file was updated "
        "in this commit or the immediately preceding one. Per specs/workflow.md "
        "Section 3, capture the design decision in specs/ first (commit it on its "
        "own in the turn the decision is reached), then implement in a later commit."
    )


def check_next_md_updated() -> None:
    """Backstop for the specs/NEXT.md 'update before ending a session' convention.

    Triggers on the same code-change signal as check_spec_before_or_with_code,
    plus any *other* specs/**/*.md edit. Editing specs/NEXT.md itself never trips
    this check. Same CI-range vs. single-commit-lookback handling.
    """
    next_md = "specs/NEXT.md"
    files = staged_files()
    trigger_files = [
        f for f in files if f != next_md and (_is_code_change(f) or _is_spec_change(f))
    ]
    if not trigger_files:
        return
    if next_md in files:
        return
    if os.environ.get("CHECK_CONVENTIONS_BASE_REF"):
        errors.append(
            f"This push/PR touches {trigger_files} but {next_md} was not updated "
            "anywhere in the range. Refresh its 'Active work' pointer (or write "
            "'None.') before ending the session -- see specs/NEXT.md."
        )
        return
    if next_md in _previous_commit_files():
        return
    errors.append(
        f"This commit touches {trigger_files} but {next_md} was not updated in this "
        "commit or the immediately preceding one. Refresh its 'Active work' pointer "
        "(or write 'None.') before ending the session -- see specs/NEXT.md."
    )


SPEC_FILE_RE = re.compile(r"^specs/\d{3}-.*\.md$")
SPEC_SHALLOW_MAX_LINES = 400

advisories: list[str] = []


def check_spec_files_shallow() -> None:
    """Soft advisory (never fails the commit): a staged specs/NNN-*.md
    (excluding *-history.md siblings) over SPEC_SHALLOW_MAX_LINES lines gets
    a nudge to apply the two-file split — dated decision sections move
    verbatim to specs/NNN-<skill>-history.md behind a decision-index table.
    Run `python scripts/split_spec_history.py <spec>` to perform it. See
    specs/workflow.md Section 3a / Section 8 item 8."""
    for rel_path in staged_files():
        if not SPEC_FILE_RE.match(rel_path) or rel_path.endswith("-history.md"):
            continue
        content = file_text(rel_path)
        if content is None:
            continue
        line_count = len(content.splitlines())
        if line_count > SPEC_SHALLOW_MAX_LINES:
            advisories.append(
                f"'{rel_path}' is {line_count} lines (shallow-spec target: "
                f"{SPEC_SHALLOW_MAX_LINES}). Consider moving dated decision "
                "sections verbatim to its '-history.md' sibling behind a "
                "decision-index table — run "
                f"`python scripts/split_spec_history.py {rel_path}` — see "
                "specs/workflow.md Section 3a. Advisory only; your commit is "
                "not blocked."
            )


def main() -> int:
    check_agents_md_size()
    check_agents_md_duplication()
    check_pointer_files_thin()
    check_no_secrets_in_data()
    check_generated_provenance()
    check_spec_before_or_with_code()
    check_next_md_updated()
    check_spec_files_shallow()

    if advisories:
        print("repo convention advisory (non-blocking):\n", file=sys.stderr)
        for note in advisories:
            print(f"  - {note}", file=sys.stderr)
        print(file=sys.stderr)

    if errors:
        print("repo convention check failed:\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
