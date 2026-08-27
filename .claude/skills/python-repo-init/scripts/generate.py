"""Scaffold a new Python repo with the AI-agent workflow governance pattern.

Usage (works from any cwd -- paths are resolved relative to this file):
    python3 /path/to/scripts/generate.py <target-dir> [--name NAME]
        [--package PKG] [--author AUTHOR] [--description DESC]
        [--python VERSION] [--force]

Copies templates/ into <target-dir>, substituting placeholders. Lays down files
only -- it does NOT run git init, uv sync, or wire hooks; it prints those next
steps for the human/agent to run. Idempotency: refuses to write into a
non-empty target unless --force is given.
"""

from __future__ import annotations

import argparse
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"

DEFAULT_PYTHON = "3.14"

# Path-segment and content placeholders.
PATH_PLACEHOLDER = "__PKG_NAME__"


def default_author() -> str:
    """Owner handle from git config; neutral placeholder if unset."""
    for key in ("user.name", "user.email"):
        result = subprocess.run(
            ["git", "config", "--get", key], capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return "TODO-set-author"


def sanitize_package(name: str) -> str:
    """Turn a project name into a valid Python package (import) name."""
    pkg = re.sub(r"[^0-9a-zA-Z_]", "_", name.strip().lower())
    pkg = re.sub(r"_+", "_", pkg).strip("_")
    if not pkg:
        pkg = "pkg"
    if pkg[0].isdigit():
        pkg = f"pkg_{pkg}"
    return pkg


def substitutions(args: argparse.Namespace) -> dict[str, str]:
    return {
        "__PROJECT_NAME__": args.name,
        "__PKG_NAME__": args.package,
        "__AUTHOR__": args.author,
        "__DATE__": args.date,
        "__DESCRIPTION__": args.description,
        "__PYTHON_VERSION__": args.python,
    }


def apply(text: str, subs: dict[str, str]) -> str:
    for key, value in subs.items():
        text = text.replace(key, value)
    return text


def is_nonempty_dir(path: Path) -> bool:
    return path.is_dir() and any(path.iterdir())


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="python-repo-init", description=__doc__)
    p.add_argument("target", help="Directory to scaffold the new repo into.")
    p.add_argument("--name", help="Project name (default: target dir basename).")
    p.add_argument("--package", help="Python package name (default: sanitized name).")
    p.add_argument("--author", help="Owner handle (default: git config user.name/user.email).")
    p.add_argument("--description", default="", help="Short project description.")
    p.add_argument(
        "--python",
        default=DEFAULT_PYTHON,
        help=f"Python version for pyproject.toml/mise.toml (default: {DEFAULT_PYTHON}).",
    )
    p.add_argument("--force", action="store_true", help="Write even if target is non-empty.")
    args = p.parse_args(argv)

    if not re.fullmatch(r"3\.\d+(\.\d+)?", args.python):
        p.error(f"--python must look like '3.14' or '3.14.1', got {args.python!r}")

    args.target_path = Path(args.target).expanduser().resolve()
    args.name = args.name or args.target_path.name
    args.package = args.package or sanitize_package(args.name)
    args.author = args.author or default_author()
    args.description = args.description or f"{args.name} — TODO: describe this project."
    args.date = datetime.date.today().isoformat()
    return args


def scaffold(args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    subs = substitutions(args)
    target = args.target_path
    written: list[Path] = []
    overwritten: list[Path] = []

    for src in sorted(TEMPLATES_DIR.rglob("*")):
        rel = src.relative_to(TEMPLATES_DIR)
        rel_str = str(rel).replace(PATH_PLACEHOLDER, args.package)
        dest = target / rel_str

        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            overwritten.append(dest)
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dest)
        else:
            dest.write_text(apply(text, subs), encoding="utf-8")
        shutil.copymode(src, dest)
        # Git hooks must be executable regardless of the template's stored mode.
        if dest.parent.name == ".githooks":
            dest.chmod(dest.stat().st_mode | 0o111)
        written.append(dest)

    return written, overwritten


def print_next_steps(args: argparse.Namespace) -> None:
    rel = args.target_path
    print("\nScaffolded", args.name, "->", rel)
    print("\nNext steps (run yourself; the generator intentionally does not):")
    print(f"  cd {rel}")
    print("  git init")
    print("  git config core.hooksPath .githooks   # once per clone; hook is stdlib-only")
    print("  uv sync --dev                         # deps + test tooling")
    print("  git add -A && git commit -m 'chore: scaffold repo governance'")
    print("\nThen read specs/NEXT.md for the first skill to build.")
    print("Human decisions parked in specs/NEXT.md: enabling GitHub Actions, etc.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if not TEMPLATES_DIR.is_dir():
        print(f"error: templates dir not found at {TEMPLATES_DIR}", file=sys.stderr)
        return 2

    if is_nonempty_dir(args.target_path) and not args.force:
        print(
            f"error: {args.target_path} exists and is not empty. "
            "Re-run with --force to scaffold into it anyway.",
            file=sys.stderr,
        )
        return 1

    written, overwritten = scaffold(args)
    print(f"Wrote {len(written)} files.")
    if overwritten:
        print(f"Overwrote {len(overwritten)} pre-existing file(s):")
        for path in overwritten:
            print(f"  {path.relative_to(args.target_path)}")
    print_next_steps(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
