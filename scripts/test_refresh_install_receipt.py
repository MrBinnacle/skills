"""Offline suite for refresh_install_receipt.py (issue #464, part 2).

What this pins
    1. Run selection. The receipt cites the first push run on main whose
       head commit carries the target plugin version and whose run passed,
       including every `Install form` job. A run at the target version that
       failed is skipped: v3.1.0's receipt first cited run 39073914809, the
       red run #464 is about.
    2. The rewrite. The three shell-form receipt sites in `## Install` move
       together: the marketplace-add date, the `at X (CI run N, date)` line,
       and the prose date. The interactive form keeps its own date. Each site
       must match exactly once, or the rewrite refuses. The result still
       parses with test_install_form.parse_verified_forms, so the check that
       reads the receipt reads the new version.
    3. Line endings survive: a CRLF README stays CRLF.

No network and no `gh`: runs and versions are fakes passed to the pure
functions.

Run:  python scripts/test_refresh_install_receipt.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from refresh_install_receipt import (  # noqa: E402
    rewrite_receipt,
    select_receipt_run,
)
from test_install_form import install_section, parse_verified_forms  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


README = """# Title

## Install

Verified forms, Claude Code 2.1.287, from a clean `CLAUDE_CONFIG_DIR` with no SSH key:

- interactive `/plugin marketplace add https://github.com/MrBinnacle/skills.git` (2026-10-02)
- shell `claude plugin marketplace add https://github.com/MrBinnacle/skills.git` (CI, 2026-10-17)
- shell `claude plugin install` of all three plugins, at 3.1.0 (CI run 39073914809, 2026-10-17)

The 2026-10-02 cold-install transcript is in the pull request that changed this section (#340). The 2026-10-17 shell forms ran in the `Install form` CI job on Ubuntu and Windows.

## What's in it
"""


def run(run_id: int, sha: str, conclusion: str, created: str) -> dict:
    return {
        "databaseId": run_id,
        "headSha": sha,
        "conclusion": conclusion,
        "createdAt": created,
    }


def selection_cases() -> None:
    versions = {"old": {"3.0.1"}, "bump": {"3.1.0"}, "next": {"3.1.0"}}
    # gh lists newest first; the selector must not depend on that order.
    runs = [
        run(4, "next", "success", "2026-10-18T09:00:00Z"),
        run(3, "next", "success", "2026-10-17T22:36:03Z"),
        run(2, "bump", "failure", "2026-10-17T22:09:41Z"),
        run(1, "old", "success", "2026-10-16T12:00:00Z"),
    ]
    all_pass = lambda _run_id: True  # noqa: E731
    chosen = select_receipt_run(runs, "3.1.0", versions.__getitem__, all_pass)
    check(
        "a failed run at the target version is skipped",
        chosen is not None and chosen["databaseId"] == 3,
        f"chose {chosen}",
    )

    only_old = [run(1, "old", "success", "2026-10-16T12:00:00Z")]
    chosen = select_receipt_run(only_old, "3.1.0", versions.__getitem__, all_pass)
    check("a passing run at an older version does not qualify", chosen is None, f"chose {chosen}")

    install_red = lambda run_id: run_id != 3  # noqa: E731
    chosen = select_receipt_run(runs, "3.1.0", versions.__getitem__, install_red)
    check(
        "a run whose Install form jobs did not pass is skipped",
        chosen is not None and chosen["databaseId"] == 4,
        f"chose {chosen}",
    )

    mixed = {"bump": {"3.1.0", "3.0.1"}}
    chosen = select_receipt_run(
        [run(9, "bump", "success", "2026-10-17T00:00:00Z")],
        "3.1.0",
        mixed.__getitem__,
        all_pass,
    )
    check("a commit with mixed plugin versions does not qualify", chosen is None, f"chose {chosen}")


def rewrite_cases() -> None:
    out = rewrite_receipt(README, "3.2.0", 41000000001, "2026-11-02")
    check(
        "marketplace-add date moves",
        "skills.git` (CI, 2026-11-02)" in out,
        out,
    )
    check(
        "install line carries the new version, run and date",
        "at 3.2.0 (CI run 41000000001, 2026-11-02)" in out,
        out,
    )
    check(
        "prose date moves",
        "The 2026-11-02 shell forms ran in the `Install form` CI job" in out,
        out,
    )
    check(
        "interactive form keeps its own date",
        "skills.git` (2026-10-02)" in out and "The 2026-10-02 cold-install transcript" in out,
        out,
    )
    check(
        "test_install_form still reads the rewritten receipt",
        parse_verified_forms(install_section(out)) == ("2.1.287", "3.2.0"),
        repr(parse_verified_forms(install_section(out))),
    )
    check(
        "rewriting to the receipt already there is a no-op",
        rewrite_receipt(README, "3.1.0", 39073914809, "2026-10-17") == README,
    )

    broken = README.replace("of all three plugins, at", "of every plugin, at")
    try:
        rewrite_receipt(broken, "3.2.0", 1, "2026-11-02")
        refused = False
    except ValueError:
        refused = True
    check("a missing receipt site refuses instead of half-rewriting", refused)

    doubled = README.replace("## What's in it", README.split("## Install")[1] + "\n## What's in it")
    try:
        rewrite_receipt(doubled, "3.2.0", 1, "2026-11-02")
        refused = False
    except ValueError:
        refused = True
    check("a receipt site that appears twice refuses", refused)

    crlf = README.replace("\n", "\r\n")
    out = rewrite_receipt(crlf, "3.2.0", 1, "2026-11-02")
    check(
        "CRLF line endings survive the rewrite",
        out.count("\r\n") == crlf.count("\r\n") and "\n" not in out.replace("\r\n", ""),
    )


def main() -> int:
    selection_cases()
    rewrite_cases()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED")
        return 1
    print(
        "PASS: the receipt cites the first passing main run at the target "
        "version, and every shell-form receipt site moves together"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
