#!/usr/bin/env python3
"""Check that every tracked path fits under the Windows path limit at install (#356).

`claude plugin marketplace add` clones the whole repository, every tracked file
included. git checks it out into a temporary directory beside the final one and
renames it after. For the published HTTPS form that directory is
`<config>\\plugins\\marketplaces\\temp_git_<13-digit ms>_<6 chars>..clone\\`, 59
characters after the config root; the final `mrbinnacle-skills\\` is only 40, and the
GitHub shorthand form's `MrBinnacle-skills..clone\\` is 47. `claude plugin install`
then copies one bucket to `<config>\\plugins\\cache\\mrbinnacle-skills\\mrbinnacle-<bucket>\\<version>\\`
(ADR 0004). That prefix stands in for `skills/<bucket>/` and is 13 characters shorter
than the clone's for any bucket and any version up to 99.99.99, so the clone binds.

Without `core.longpaths`, git for Windows refuses a file whose absolute path is 260
characters or more, and a directory of 248 or more: MAX_PATH and CreateDirectory's
MAX_PATH - 12 both count the terminating NUL. Measured on 2026-10-17, Claude Code
2.1.302, git 2.56.0.windows.1: a 106-character clone target checked out a 152-character
path (259 absolute) and a 107-character one failed (260); the shorthand install
succeeded from a 120-character config root (longest directory 120 + 47 + 80 = 247) and
failed from 121 on that same directory (248).

The budget assumes the worst default config root, `C:\\Users\\<20-character user>\\.claude`
(37 characters). A custom CLAUDE_CONFIG_DIR longer than that is out of scope: no
budget here can protect an unbounded root.

Exit 0 with a `PASS:` line, or 1 with one `FAIL:` line per path over budget.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Final

MAX_PATH: Final[int] = 260
MAX_DIR: Final[int] = 248
NUL: Final[int] = 1
WORST_CASE_ROOT: Final[int] = len("C:\\Users\\") + 20 + len("\\.claude")
# Claude Code's temporary checkout for an HTTPS marketplace URL; the timestamp is
# milliseconds since 1970, 13 digits until the year 2286.
CLONE_PREFIX: Final[int] = len("\\plugins\\marketplaces\\temp_git_1792264963169_5k2kxp..clone\\")
FILE_BUDGET: Final[int] = MAX_PATH - NUL - WORST_CASE_ROOT - CLONE_PREFIX
DIR_BUDGET: Final[int] = MAX_DIR - NUL - WORST_CASE_ROOT - CLONE_PREFIX


def check(tracked: list[str]) -> list[str]:
    errors: list[str] = []
    for path in tracked:
        if len(path) > FILE_BUDGET:
            errors.append(f"{path} is {len(path)} characters, file budget "
                          f"{FILE_BUDGET} = {MAX_PATH} - {NUL} - {WORST_CASE_ROOT} - {CLONE_PREFIX}")
        parent = path.rpartition("/")[0]
        if len(parent) > DIR_BUDGET:
            errors.append(f"directory {parent} is {len(parent)} characters, directory budget "
                          f"{DIR_BUDGET} = {MAX_DIR} - {NUL} - {WORST_CASE_ROOT} - {CLONE_PREFIX}")
    return errors


def tracked_paths(root: Path) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check tracked paths against the Windows path limit.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    tracked = tracked_paths(args.root)
    errors = check(tracked)
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    longest = max(tracked, key=len)
    deepest = max((p.rpartition("/")[0] for p in tracked), key=len)
    print(f"PASS: {len(tracked)} tracked paths fit at a {WORST_CASE_ROOT}-character config root; "
          f"longest file {len(longest)} of {FILE_BUDGET}, longest directory {len(deepest)} of {DIR_BUDGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
