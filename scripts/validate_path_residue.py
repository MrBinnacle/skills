#!/usr/bin/env python3
"""Refuse a tracked PATH that carries a de-personalization residue term.

WHY A SEPARATE HOOK AND NOT A FLAG ON THE CONTENT HOOKS

    The seven `pygrep` residue hooks in `.pre-commit-config.yaml` read file
    CONTENTS. They are configured on `*.md` and never see a path, so a private
    repository name in a filename passes them and reaches `main` (#243). A
    filename is the worse channel: it shows in the GitHub tree, the URL,
    `git log --stat` and every clone's directory listing without anyone opening
    the file.

WHY THE SEPARATOR CLASS

    Identifiers use underscores; filenames use hyphens and dots for the same
    word break. The content pattern `workspace_lint` misses `workspace-lint`.
    Every multi-word term here is matched with `[_.-]` between its words, so the
    underscore, hyphen and dot forms are one term. Matching is case-insensitive,
    because a filename's case is a convention and not a distinct identifier.

THE TERM LIST IS DUPLICATED, ON PURPOSE AND FOR NOW

    The content hooks keep their patterns in the yaml, where `pygrep` reads
    them. This script keeps the same terms in Python, where `re` reads them.
    Moving both to one shared source is the structural fix #243 names in its
    Revisit-if, and it is out of scope here. Until then: edit BOTH lists, and
    the suite's `case_every_yaml_residue_hook_has_a_path_term` fails when the
    yaml gains a residue hook this list does not carry.

WHAT IT READS

    `git ls-files` - the index. A file staged for the current commit is in the
    index, so a pre-commit run sees the new name before it is committed, and a
    `--all-files` run in CI sweeps every tracked path in the tree.

Usage:
    python scripts/validate_path_residue.py            # the repository this file lives in
    python scripts/validate_path_residue.py --root DIR # another checkout (the suite uses this)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Final

# One entry per residue hook in .pre-commit-config.yaml, in the same order.
# `(?<![a-z0-9])` / `(?![a-z0-9])` are word edges that treat `_`, `-` and `.`
# as breaks, which `\b` does not do for the underscore.
_EDGE_L: Final[str] = r"(?<![a-z0-9])"
_EDGE_R: Final[str] = r"(?![a-z0-9])"
_SEP: Final[str] = r"[_.\-]"

PATH_TERMS: Final[tuple[tuple[str, str], ...]] = (
    ("residue-writ", _EDGE_L + r"writ" + _EDGE_R),
    ("residue-sec-id", _EDGE_L + r"sec-[0-9]+"),
    ("residue-wi-id", _EDGE_L + r"wi-[0-9]+"),
    ("residue-research-dir", r"skills" + _SEP + r"research"),
    ("residue-private-repo-dir", r"youwontdoit"),
    ("residue-private-repo-link", r"mrbinnacle[_.\-/]writ" + _EDGE_R),
    ("residue-private-linter-repo", r"workspace" + _SEP + r"lint"),
)

_COMPILED: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (hook_id, re.compile(pattern, re.IGNORECASE)) for hook_id, pattern in PATH_TERMS
)


def tracked_paths(root: Path) -> list[str]:
    """Every path in the index, forward-slashed, as git reports it."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    return [p for p in result.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def findings(paths: list[str]) -> list[tuple[str, str, str]]:
    """(path, hook_id, matched_text) for every path that carries a term."""
    hits: list[tuple[str, str, str]] = []
    for path in paths:
        for hook_id, pattern in _COMPILED:
            match = pattern.search(path)
            if match is not None:
                hits.append((path, hook_id, match.group(0)))
    return hits


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository to sweep (default: the one this script lives in)",
    )
    args = parser.parse_args(argv)

    paths = tracked_paths(args.root)
    hits = findings(paths)
    if hits:
        print(f"FAIL: {len(hits)} tracked path(s) carry a residue term:")
        for path, hook_id, text in hits:
            print(f"  {path}  ->  {hook_id} matched {text!r}")
        print(
            "\nA residue term in a PATH is a disclosure even when the contents are clean.\n"
            "Rename the file or directory, or record why the name must stand."
        )
        return 1
    print(f"PASS: path residue - {len(paths)} tracked path(s), no residue term in any name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
