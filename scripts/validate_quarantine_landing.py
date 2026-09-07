#!/usr/bin/env python3
"""Refuse a commit that stages a NEW `_quarantine/<skill>/` without a landing marker.

THE HAZARD

    `_quarantine/` is tracked - that is the promotion path - so a `git add -A`
    at the repository root sweeps an unfinished candidate skill into a public
    commit, and the admission gate is bypassed by a shell habit (#249). Adding
    the directory to `.gitignore` is NOT the fix: promotion reads it.

WHAT COUNTS AS NEW

    A `_quarantine/<skill>/` directory with no tracked file at HEAD. Editing or
    adding a file inside a directory HEAD already tracks is ordinary work on a
    landed candidate and passes. Files under `skills/` or anywhere else are not
    this guard's business.

THE MARKER

    `LANDING.md` inside the candidate directory, staged in the same commit,
    whose first line is exactly `intentional-landing: true`. A marker file is
    authored with the candidate and travels with it into review; a typed flag is
    the remembering-discipline #249 refuses. The name and the first line are the
    only load-bearing parts: `grep -rl '^intentional-landing: true' _quarantine`
    lists every declared landing. Any prose after the first line is the author's
    note on why the candidate is landing now.

WHAT IT READS

    The staged index - `git diff --cached`. When nothing is staged relative to
    HEAD, as under `pre-commit run --all-files` in CI, there is nothing to judge
    and the check passes with a note. A repository with no HEAD yet treats every
    staged quarantine directory as new.

Usage:
    python scripts/validate_quarantine_landing.py           # the repository at the cwd
    python scripts/validate_quarantine_landing.py --root DIR
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Final

QUARANTINE: Final[str] = "_quarantine"
MARKER_NAME: Final[str] = "LANDING.md"
MARKER_FIRST_LINE: Final[str] = "intentional-landing: true"


def git_lines(root: Path, *args: str, check: bool = True) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=check
    )
    return [p for p in result.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def has_head(root: Path) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "-q", "HEAD"],
            capture_output=True,
        ).returncode
        == 0
    )


def candidate_dir(path: str) -> str | None:
    """`_quarantine/<skill>` for a path inside a candidate directory, else None."""
    parts = PurePosixPath(path).parts
    if len(parts) < 3 or parts[0] != QUARANTINE:
        return None
    return f"{QUARANTINE}/{parts[1]}"


def staged_added(root: Path) -> list[str]:
    if has_head(root):
        return git_lines(root, "diff", "--cached", "--name-only", "--diff-filter=A", "-z")
    return git_lines(root, "ls-files", "--cached", "-z")


def tracked_at_head(root: Path, directory: str) -> bool:
    if not has_head(root):
        return False
    return bool(git_lines(root, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", directory))


def staged_marker_declares(root: Path, directory: str) -> bool:
    """True when `<directory>/LANDING.md` is STAGED and its staged first line is the declaration."""
    result = subprocess.run(
        ["git", "-C", str(root), "show", f":{directory}/{MARKER_NAME}"],
        capture_output=True,
    )
    if result.returncode != 0:
        return False
    first = result.stdout.decode("utf-8", "replace").splitlines()[:1]
    return bool(first) and first[0].strip() == MARKER_FIRST_LINE


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    root = args.root

    added = staged_added(root)
    new_dirs = sorted({d for d in (candidate_dir(p) for p in added) if d and not tracked_at_head(root, d)})
    if not added:
        print("PASS: quarantine landing - nothing staged, nothing to judge")
        return 0
    if not new_dirs:
        print(f"PASS: quarantine landing - {len(added)} staged addition(s), no new {QUARANTINE}/<skill>/")
        return 0

    undeclared = [d for d in new_dirs if not staged_marker_declares(root, d)]
    if undeclared:
        print(f"FAIL: {len(undeclared)} new {QUARANTINE}/<skill>/ director(ies) staged without a landing marker:")
        for d in undeclared:
            print(f"  {d}/")
        print(
            f"\nA candidate reaches the public tree only through the admission path.\n"
            f"If this landing is intended, add `{MARKER_NAME}` inside the directory with\n"
            f"`{MARKER_FIRST_LINE}` as its first line and stage it with the candidate.\n"
            f"Otherwise unstage it: git restore --staged -- <directory>"
        )
        return 1
    print(f"PASS: quarantine landing - {len(new_dirs)} new candidate(s) declared by {MARKER_NAME}: " + ", ".join(new_dirs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
