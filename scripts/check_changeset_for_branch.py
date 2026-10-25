#!/usr/bin/env python3
"""Refuse a branch that changes files but adds no changeset of its own.

Until #630 the CI step asked git which changesets a branch added
(`changeset status --since=origin/main`). #630 untracked `.changeset/`, so git
sees none, and #632 swapped in a file-time test: a changeset modified after the
merge-base commit counted as the branch's own. File times are not content. A
restore of `.changeset/` with plain `cp -r` stamps every old pending changeset
as new, and the step then passed a branch that added nothing.

The rule now reads content. When the branch name carries an issue number
(`fix/632-brand-surfaces`, `feat/issue-632-x`), the branch passes only if some
changeset body mentions `#632`. A branch name with no number falls back to the
file-time test and prints a WARN line naming it as the weaker check.

The issue number is the first run of digits after the type prefix (the text up
to the first `/`) that stands alone between separators (`-`, `_`, `/`, or the
ends), after an optional `issue-` or `gh-`. So `automation/marketplace-pin-v3.1.0`
carries no number: `v3` is not a separate run.

Branch name: `--branch`, else `GITHUB_HEAD_REF`, else
`git rev-parse --abbrev-ref HEAD`.

Run: ``python scripts/check_changeset_for_branch.py --base-ts <unix seconds>
[--branch <name>] [--root <repo-root>]``. Exit 0 with one `PASS:` line (after a
`WARN:` line on the fallback), or 1 with one `FAIL:` line.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_installed_user_action import changeset_files  # noqa: E402

ISSUE_IN_BRANCH = re.compile(r"(?:^|[-_/])(?:issue-?|gh-?)?(\d+)(?=[-_/]|$)", re.IGNORECASE)


@dataclass(frozen=True)
class Changeset:
    name: str
    text: str
    mtime: float


def issue_number(branch: str) -> str | None:
    rest = branch.split("/", 1)[1] if "/" in branch else branch
    match = ISSUE_IN_BRANCH.search(rest)
    return match.group(1) if match else None


def body(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    return "" if closing is None else "\n".join(lines[closing + 1:])


def mentions(text: str, number: str) -> bool:
    return re.search(rf"(?<![\w&])#{number}(?!\d)", body(text)) is not None


def verdict(branch: str, changesets: list[Changeset], base_ts: float) -> tuple[bool, list[str]]:
    number = issue_number(branch)
    if number is not None:
        hits = [c.name for c in changesets if mentions(c.text, number)]
        if hits:
            return True, [f"PASS: branch {branch} carries #{number}; .changeset/{hits[0]} mentions it"]
        return False, [
            f"FAIL: branch {branch} carries #{number} but no changeset in .changeset/ "
            f"mentions #{number} in its body. Run npx changeset and cite #{number}."
        ]
    warn = (
        f"WARN: branch {branch} names no issue number, so this falls back to the weaker "
        f"file-time check (a changeset modified after the merge-base commit). A copy of "
        f".changeset/ that does not keep file times passes it."
    )
    fresh = sorted(c.name for c in changesets if c.mtime > base_ts)
    if fresh:
        return True, [warn, f"PASS: .changeset/{fresh[0]} was modified after the merge-base commit"]
    return False, [
        warn,
        "FAIL: this ref changes files but .changeset/ holds no changeset modified after "
        "the merge-base commit. Run npx changeset.",
    ]


def current_branch() -> str:
    head_ref = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if head_ref:
        return head_ref
    out = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-ts", type=float, required=True)
    parser.add_argument("--branch")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)

    changesets = [
        Changeset(p.name, p.read_text(encoding="utf-8"), p.stat().st_mtime)
        for p in changeset_files(args.root)
    ]
    ok, lines = verdict(args.branch or current_branch(), changesets, args.base_ts)
    for line in lines:
        print(line.encode("ascii", "backslashreplace").decode("ascii"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
