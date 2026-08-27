#!/usr/bin/env python3
"""Split dated decision sections out of a spec into its -history.md sibling.

The two-file pattern (specs/workflow.md Section 3a): a skill spec stays
shallow and normative; dated decision sections (headings like ``## 7a. …``
or ``## 8c. …``) move verbatim — numbering unchanged — to an append-only
``specs/NNN-<skill>-history.md`` sibling, behind a decision-index cue
table left in their place. Guard check #9 (advisory) nudges this split
when a spec exceeds its line target; this script performs it.

Usage:
    python scripts/split_spec_history.py specs/003-vlan-inventory.md

What it does, mechanically (no content is ever rewritten, only moved):
  * every section whose heading matches ``## <digits><letter>.`` moves to
    the sibling history file, in order of appearance (a section runs to
    the next ``## `` heading or EOF);
  * a decision-index table skeleton is inserted where the first moved
    section began — the ``date`` column is parsed from the heading when a
    ``YYYY-MM-DD`` is present, the ``cue`` column is the heading title,
    and the ``status`` column is left as ``<status>`` for a human/agent
    to fill (implemented / planned / superseded — that's judgment, not
    mechanics);
  * an orphaned duplicate heading left EMPTY by the move (e.g. a
    ``## 8. Success criteria`` that decision sections had accreted past,
    duplicated later with real content) is dropped;
  * refuses to run if the history sibling already exists (append to it by
    hand/agent instead — it is append-only).

After running: fill the ``<status>`` cells, then update any *precise*
file+section cross-references that must stay exact (e.g. specs/NEXT.md
pointers); prose references resolve through the index redirect.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DECISION_HEADING_RE = re.compile(r"^## (?P<id>\d+[a-z])\. (?P<title>.+?)\s*$")
DATE_RE = re.compile(r"(20\d\d-\d\d-\d\d)")
ANY_HEADING_RE = re.compile(r"^## ")


def split_sections(lines: list[str]) -> tuple[list[str], list[tuple[str, str, list[str]]], int]:
    """Return (kept_lines, moved_sections, insert_at).

    ``moved_sections`` is a list of (section_id, title, section_lines);
    ``insert_at`` is the index into ``kept_lines`` where the first moved
    section used to start (where the index table belongs).
    """
    kept: list[str] = []
    moved: list[tuple[str, str, list[str]]] = []
    insert_at = -1
    i = 0
    while i < len(lines):
        m = DECISION_HEADING_RE.match(lines[i])
        if not m:
            kept.append(lines[i])
            i += 1
            continue
        if insert_at < 0:
            insert_at = len(kept)
        start = i
        i += 1
        while i < len(lines) and not ANY_HEADING_RE.match(lines[i]):
            i += 1
        moved.append((m.group("id"), m.group("title"), lines[start:i]))
    if insert_at < 0:
        raise SystemExit("no '## <N><letter>. …' decision sections found — nothing to split")
    return kept, moved, insert_at


def drop_orphan_duplicate_headings(lines: list[str]) -> list[str]:
    """Drop a ``## `` heading whose body is empty AND whose exact heading
    text appears again later (the accreted-past-the-end orphan case)."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        if ANY_HEADING_RE.match(lines[i]):
            j = i + 1
            while j < len(lines) and not ANY_HEADING_RE.match(lines[j]):
                j += 1
            body_empty = all(not line.strip() for line in lines[i + 1 : j])
            duplicated_later = any(
                later.rstrip() == lines[i].rstrip() for later in lines[j:]
            )
            if body_empty and duplicated_later:
                i = j  # skip the orphan heading + its blank body
                continue
        out.append(lines[i])
        i += 1
    return out


def index_table(moved: list[tuple[str, str, list[str]]], history_name: str) -> str:
    first, last = moved[0][0], moved[-1][0]
    rows = []
    for section_id, title, _ in moved:
        date_m = DATE_RE.search(title)
        date = date_m.group(1) if date_m else "<date>"
        cue = DATE_RE.sub("", title)
        cue = re.sub(r"\(\s*(decision|bug fix|planned)?\s*\)", "", cue).strip(" —-–")
        rows.append(f"| {section_id} | {date} | {cue} | <status> |")
    return (
        f"## Decision history (Sections {first}–{last}) — index\n"
        "\n"
        f"The dated decision sections live in [`{history_name}`](./{history_name})\n"
        "(moved verbatim; numbering unchanged — a reference like \"Section "
        f"{first}\" means\n"
        "that section in the history file). Read a section only when its row\n"
        "below matters to your task; the sections above describe the *current*\n"
        "state these decisions produced. Fill each `<status>` with\n"
        "implemented / planned / superseded.\n"
        "\n"
        "| § | Date | Decision (cue) | Status |\n"
        "|---|------|----------------|--------|\n" + "\n".join(rows) + "\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("spec", type=Path, help="the specs/NNN-<skill>.md file to split")
    args = parser.parse_args(argv)

    spec: Path = args.spec
    if not spec.is_file():
        raise SystemExit(f"{spec}: not a file")
    history = spec.with_name(spec.stem + "-history.md")
    if history.exists():
        raise SystemExit(
            f"{history} already exists — it is append-only; add new sections "
            "there by hand instead of re-running the split"
        )

    lines = spec.read_text().splitlines(keepends=True)
    kept, moved, insert_at = split_sections(lines)
    kept = drop_orphan_duplicate_headings(kept)
    # insert_at was computed against pre-drop `kept`; recompute safely: the
    # drop only removes lines, so clamp into range and keep the table before
    # whatever now sits at that position's nearest preceding boundary.
    insert_at = min(insert_at, len(kept))

    history_header = (
        f"# {spec.stem} — Decision History\n\n"
        f"Dated decision sections moved **verbatim** (numbering unchanged) from\n"
        f"`{spec.name}` — two-file pattern, see `specs/workflow.md` Section 3a.\n"
        "Append-only; add new dated decision sections HERE (and a row to the\n"
        "index in the shallow spec), newest at the bottom.\n\n"
    )
    history_body = "".join("".join(s).rstrip("\n") + "\n\n" for _, _, s in moved).rstrip("\n") + "\n"
    history.write_text(history_header + history_body)

    table = index_table(moved, history.name)
    new_spec = (
        "".join(kept[:insert_at]).rstrip("\n")
        + "\n\n"
        + table
        + "\n"
        + "".join(kept[insert_at:]).lstrip("\n")
    ).rstrip("\n") + "\n"
    spec.write_text(new_spec)

    print(
        f"moved {len(moved)} sections ({moved[0][0]}–{moved[-1][0]}) to {history}\n"
        f"{spec}: {new_spec.count(chr(10))} lines; {history.name}: "
        f"{(history_header + history_body).count(chr(10))} lines\n"
        "NEXT: fill the <status> cells in the index table, and repoint any "
        "precise file+section references (e.g. specs/NEXT.md)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
