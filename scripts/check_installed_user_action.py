#!/usr/bin/env python3
"""Refuse a major changeset that does not tell an installed user what to do (#364).

A release headed "Major Changes" sends an installed user looking for a break.
The changeset convention asked only for a summary, so two major changesets
explained validator internals and never said whether the user had to act.

The rule, stated in `.changeset/README.md` and AGENTS.md: a changeset that
declares `major` for any package ends with a line of the exact form

    Action for installed users: <text>

where `None.` is valid text. The line must be the last non-blank line of the
body and must carry text after the colon. Minor and patch changesets may omit it.

Bumps are read with release_gate's parser, so this check and the release gate
cannot disagree on what a frontmatter line declares. A changeset that parser
cannot read is refused here too: whether it is major is unknown, and a check
that skipped it would pass over exactly the file it exists to read.

Output is ASCII-only so the Windows CI cell cannot die on a status line.

Run: ``python scripts/check_installed_user_action.py [--root <repo-root>]``.
Exit 0 with one `PASS:` line, or 1 with one `FAIL:` line per refused changeset.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_gate import (  # noqa: E402
    ChangesetBumpParseError,
    ChangesetHeaderError,
    changeset_declared_bumps,
)

PREFIX = "Action for installed users:"
CHANGESET_DIR = ".changeset"
NOT_A_CHANGESET = "README.md"


def body_last_line(text: str) -> str:
    """The last non-blank line after the closing frontmatter fence, stripped."""
    lines = text.splitlines()
    closing = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    body = [line.strip() for line in lines[closing + 1:] if line.strip()]
    return body[-1] if body else ""


def verdict(rel: str, text: str) -> tuple[bool, str | None]:
    """(declares major, why it is refused or None)."""
    try:
        bumps = changeset_declared_bumps(text)
    except (ChangesetHeaderError, ChangesetBumpParseError) as exc:
        return False, f"{rel}: cannot read its bump, so cannot tell whether it is major ({exc})"
    if "major" not in bumps.values():
        return False, None
    last = body_last_line(text)
    if last.startswith(PREFIX) and last[len(PREFIX):].strip():
        return True, None
    return True, (
        f"{rel}: declares a major bump and does not end with an "
        f"'{PREFIX} <text>' line ('None.' is valid text)"
    )


def changeset_files(root: Path) -> list[Path]:
    return sorted(
        path for path in (root / CHANGESET_DIR).glob("*.md") if path.name != NOT_A_CHANGESET
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)

    files = changeset_files(args.root)
    refusals: list[str] = []
    majors = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        is_major, reason = verdict(f"{CHANGESET_DIR}/{path.name}", text)
        if reason:
            refusals.append(reason)
        elif is_major:
            majors += 1
    for line in refusals:
        print(f"FAIL: {line}".encode("ascii", "backslashreplace").decode("ascii"))
    if refusals:
        return 1
    print(
        f"PASS: {len(files)} changeset(s) read; each of the {majors} major one(s) "
        f"ends with an '{PREFIX}' line"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
