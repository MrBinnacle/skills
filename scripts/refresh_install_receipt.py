"""Refresh the README install receipt from the CI run that verified it (#464).

What it does
    The README's "Verified forms" record names the plugin version the shell
    install forms were verified at, and the CI run that verified them. A bump
    PR leaves that record at the old version on purpose: the install it would
    cite has not run yet (test_install_form.py lets the receipt lag, never
    lead). After the bump merges, the first push run of `tests.yml` on main
    installs the new version from the published URL. This script finds that
    run and rewrites the receipt to cite it.

    A run qualifies when all of these hold:
    - it is a `push` run of `tests.yml` on `main`;
    - its conclusion is `success`, and every `Install form` job in it passed;
    - every plugin.json at its head commit declares the target version.
    The earliest qualifying run is cited. The target version is the one every
    plugin.json in this tree declares.

    Three sites in `## Install` move together: the shell marketplace-add date,
    the `at X (CI run N, date)` line, and the prose date of the shell forms.
    The interactive form keeps its own date; CI does not exercise it. The date
    is the run's `createdAt`, in UTC.

    It is the receipt step #330 describes. It stays out of `npm run version`
    because no run can qualify before the bump merges, so run it by hand
    after the merge (.changeset/README.md).

Run
    python scripts/refresh_install_receipt.py           # print the diff
    python scripts/refresh_install_receipt.py --write   # apply it

Exit status: 0 when the receipt is current or was rewritten (or would be,
without --write); 1 when no run qualifies or a receipt site is missing.
Needs `gh` authenticated against the repository, and `git`.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from test_install_form import branch_plugin_versions

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
WORKFLOW = "tests.yml"
RUN_LIMIT = 100
INSTALL_JOB_PREFIX = "Install form"
DATE = r"\d{4}-\d{2}-\d{2}"

# Each pattern captures the text around the values it replaces, so the
# rewrite touches only the version, run id and dates.
MARKETPLACE_SITE = re.compile(
    rf"(- shell `claude plugin marketplace add [^`]+` \(CI, ){DATE}(\))"
)
INSTALL_SITE = re.compile(
    rf"(- shell `claude plugin install` of all three plugins, at )\S+"
    rf"( \(CI run )\d+(, ){DATE}(\))"
)
PROSE_SITE = re.compile(rf"(The ){DATE}( shell forms ran in the `{INSTALL_JOB_PREFIX}` CI job)")


def select_receipt_run(
    runs: Iterable[dict],
    target: str,
    versions_at: Callable[[str], set[str]],
    install_jobs_passed: Callable[[int], bool],
) -> dict | None:
    """Earliest run that passed with every plugin at `target`, or None."""
    for run in sorted(runs, key=lambda r: r["createdAt"]):
        if run["conclusion"] != "success":
            continue
        if versions_at(run["headSha"]) != {target}:
            continue
        if install_jobs_passed(run["databaseId"]):
            return run
    return None


def rewrite_receipt(text: str, version: str, run_id: int, date: str) -> str:
    """Point every shell-form receipt site at `version`, `run_id` and `date`.

    Raises ValueError when a site does not appear exactly once, so a reworded
    README fails loudly instead of being half rewritten.
    """
    replacements = [
        (MARKETPLACE_SITE, rf"\g<1>{date}\g<2>"),
        (INSTALL_SITE, rf"\g<1>{version}\g<2>{run_id}\g<3>{date}\g<4>"),
        (PROSE_SITE, rf"\g<1>{date}\g<2>"),
    ]
    for pattern, replacement in replacements:
        text, count = pattern.subn(replacement, text)
        if count != 1:
            raise ValueError(
                f"README receipt site {pattern.pattern!r} matched {count} times, expected 1"
            )
    return text


class ReceiptError(Exception):
    """A lookup the receipt depends on could not be made."""


def run_tool(argv: list[str]) -> str:
    try:
        out = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT))
    except FileNotFoundError as exc:
        raise ReceiptError(f"{argv[0]} is not on PATH") from exc
    if out.returncode != 0:
        raise ReceiptError(f"{' '.join(argv)} exited {out.returncode}: {out.stderr.strip()}")
    return out.stdout


def versions_at(sha: str) -> set[str]:
    """Version every plugin.json declares at commit `sha`.

    A commit missing from this clone is an error, not a skip: skipping it
    would cite a later run than the first one that passed.
    """
    run_tool(["git", "cat-file", "-e", f"{sha}^{{commit}}"])
    versions: set[str] = set()
    for path in sorted(ROOT.glob("skills/*/.claude-plugin/plugin.json")):
        relative = path.relative_to(ROOT).as_posix()
        try:
            shown = run_tool(["git", "show", f"{sha}:{relative}"])
        except ReceiptError:
            return set()  # the plugin did not exist yet at that commit
        versions.add(json.loads(shown).get("version", ""))
    return versions


def gh_json(args: list[str]) -> Any:
    return json.loads(run_tool(["gh", *args]))


def main_push_runs() -> list[dict]:
    return gh_json(
        [
            "run", "list", "--workflow", WORKFLOW, "--branch", "main",
            "--event", "push", "--limit", str(RUN_LIMIT),
            "--json", "databaseId,headSha,conclusion,createdAt",
        ]
    )


def install_jobs_passed(run_id: int) -> bool:
    jobs = gh_json(["run", "view", str(run_id), "--json", "jobs"])["jobs"]
    install = [job for job in jobs if job["name"].startswith(INSTALL_JOB_PREFIX)]
    return bool(install) and all(job["conclusion"] == "success" for job in install)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refresh the README install receipt from the CI run that verified it."
    )
    parser.add_argument("--write", action="store_true", help="apply the rewrite")
    args = parser.parse_args(argv)

    versions = set(branch_plugin_versions().values())
    if len(versions) != 1:
        print(f"FAIL plugin.json files declare {sorted(versions)}, expected one version")
        return 1
    target = versions.pop()

    try:
        runs = main_push_runs()
        # A full window whose oldest run is already at the target may have
        # cut off an earlier qualifying run.
        if len(runs) >= RUN_LIMIT:
            oldest = min(runs, key=lambda r: r["createdAt"])
            if versions_at(oldest["headSha"]) == {target}:
                print(
                    f"FAIL all {RUN_LIMIT} listed runs may postdate the first run at "
                    f"{target}; raise RUN_LIMIT"
                )
                return 1
        run = select_receipt_run(runs, target, versions_at, install_jobs_passed)
    except ReceiptError as exc:
        print(f"FAIL {exc}")
        return 1
    if run is None:
        print(
            f"FAIL no passing push run of {WORKFLOW} on main installs {target} yet; "
            "the receipt stays dated until one does"
        )
        return 1
    date = run["createdAt"][:10]

    # newline="" keeps the README's line endings byte for byte.
    with README.open(encoding="utf-8", newline="") as handle:
        before = handle.read()
    try:
        after = rewrite_receipt(before, target, run["databaseId"], date)
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1

    if after == before:
        print(f"ok   receipt already cites run {run['databaseId']} at {target}")
        return 0
    sys.stdout.writelines(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            "a/README.md",
            "b/README.md",
        )
    )
    if args.write:
        with README.open("w", encoding="utf-8", newline="") as handle:
            handle.write(after)
        print(f"wrote README.md: receipt cites run {run['databaseId']} at {target}")
    else:
        print("dry run; pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
