#!/usr/bin/env python3
"""Suite for the Dependabot github-actions config (#329).

Actions in this repository are pinned by full commit SHA, but nothing opened
update PRs for those pins until #329 added `.github/dependabot.yml`. This
suite pins the two acceptance criteria on that file:

  1. The config covers the github-actions ecosystem, on a weekly schedule,
     with updates grouped.
  2. The config validates -- `scripts/validate_dependabot_config.py` accepts
     the shipped file -- and the suite also proves that validator REFUSES the
     breach shapes named in the criteria, so a green live run is not a
     validator that cannot fail.

Each rejection case is built as a real tree on disk and run through the real
entrypoint as a subprocess. Calling a predicate in-process can stay green
while the command-line path is broken, and the command line is what a reader
runs.

Poison trees are built in a temp directory rather than checked in. A
committed breaching config would sit inside the guarded tree and turn the
real run permanently red.

Run directly:  python scripts/test_dependabot_config.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GATE = SCRIPT_DIR / "validate_dependabot_config.py"
REPO_ROOT = SCRIPT_DIR.parent
CONFIG_REL = Path(".github") / "dependabot.yml"

sys.path.insert(0, str(SCRIPT_DIR))

FAILURES: list[str] = []
NOTES: list[str] = []

# The shipped config this suite pins. Kept in one place so the poison
# fixtures below can start from a known-good body and mutate exactly one
# property -- a fixture that is wrong in two places cannot tell which
# assertion refused it.
CLEAN_BODY = """\
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      github-actions:
        patterns:
          - "*"
"""


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def note(text: str) -> None:
    """Record something the suite did NOT verify. Never silent."""
    print(f"note {text}")
    NOTES.append(text)


def run_gate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def write_config(root: Path, body: str) -> Path:
    path = root / CONFIG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def parse_live() -> dict:
    """Parse the live config with the shipped validator's own parser.

    Imported rather than restated: one parser, one place. If the module is
    absent the suite fails at import, which is the honest outcome -- the
    criterion cannot be checked without the instrument that defines valid.
    """
    import validate_dependabot_config as gate  # noqa: PLC0415

    return gate.parse_dependabot_config(
        (REPO_ROOT / CONFIG_REL).read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Criterion 1: the live file covers github-actions, weekly, grouped.
# ---------------------------------------------------------------------------


def case_live_file_exists() -> None:
    path = REPO_ROOT / CONFIG_REL
    check(
        "live .github/dependabot.yml exists",
        path.is_file(),
        f"expected {path} to exist",
    )


def case_live_shape() -> None:
    path = REPO_ROOT / CONFIG_REL
    if not path.is_file():
        check("live config shape", False, "no config to parse")
        return
    try:
        data = parse_live()
    except Exception as error:  # noqa: BLE001 - report, do not crash the suite
        check("live config shape", False, f"parse raised {error!r}")
        return

    version = data.get("version")
    check(
        "live config declares version 2",
        version == 2 or version == "2",
        f"version is {version!r}",
    )

    updates = data.get("updates")
    if not isinstance(updates, list) or not updates:
        check("live config has an updates list", False, f"updates is {updates!r}")
        return
    check("live config has an updates list", True)

    ecosystems = [
        entry.get("package-ecosystem")
        for entry in updates
        if isinstance(entry, dict)
    ]
    check(
        "live config covers the github-actions ecosystem",
        "github-actions" in ecosystems,
        f"package-ecosystem values are {ecosystems!r}",
    )

    action_entries = [
        entry
        for entry in updates
        if isinstance(entry, dict) and entry.get("package-ecosystem") == "github-actions"
    ]
    if not action_entries:
        check("live github-actions entry is well-formed", False, "no such entry")
        return

    entry = action_entries[0]
    interval = None
    schedule = entry.get("schedule")
    if isinstance(schedule, dict):
        interval = schedule.get("interval")
    check(
        "live github-actions schedule is weekly",
        interval == "weekly",
        f"schedule.interval is {interval!r}",
    )

    groups = entry.get("groups")
    grouped = isinstance(groups, dict) and bool(groups)
    check(
        "live github-actions updates are grouped",
        grouped,
        f"groups is {groups!r}",
    )
    if grouped:
        patterns_ok = False
        for spec in groups.values():
            if isinstance(spec, dict):
                patterns = spec.get("patterns")
                if isinstance(patterns, list) and patterns:
                    patterns_ok = True
        check(
            "live group carries a non-empty patterns list",
            patterns_ok,
            f"groups is {groups!r}",
        )


def case_live_validator_accepts() -> None:
    if not (REPO_ROOT / CONFIG_REL).is_file():
        check("validator accepts the live config", False, "no live config")
        return
    if not GATE.is_file():
        check("validator accepts the live config", False, f"no validator at {GATE}")
        return
    result = run_gate(REPO_ROOT)
    check(
        "validator accepts the live config",
        result.returncode == 0 and "PASS:" in result.stdout,
        f"exit {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}",
    )


# ---------------------------------------------------------------------------
# Criterion 2 poison controls: the validator refuses each breach shape.
# ---------------------------------------------------------------------------


def case_missing_file_is_refused(root: Path) -> None:
    result = run_gate(root)
    check(
        "a tree with no dependabot.yml is refused",
        result.returncode != 0,
        f"exit {result.returncode}; stdout={result.stdout!r}",
    )
    check(
        "the refusal names the missing file",
        "dependabot.yml" in (result.stdout + result.stderr),
        f"stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def case_wrong_ecosystem_is_refused(root: Path) -> None:
    body = CLEAN_BODY.replace('package-ecosystem: "github-actions"', 'package-ecosystem: "npm"')
    write_config(root, body)
    result = run_gate(root)
    check(
        "an npm-only config is refused",
        result.returncode != 0,
        f"exit {result.returncode}; stdout={result.stdout!r}",
    )
    combined = result.stdout + result.stderr
    check(
        "the refusal names github-actions",
        "github-actions" in combined,
        f"stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def case_monthly_interval_is_refused(root: Path) -> None:
    body = CLEAN_BODY.replace('interval: "weekly"', 'interval: "monthly"')
    write_config(root, body)
    result = run_gate(root)
    check(
        "a monthly schedule is refused",
        result.returncode != 0,
        f"exit {result.returncode}; stdout={result.stdout!r}",
    )
    combined = result.stdout + result.stderr
    check(
        "the refusal names weekly",
        "weekly" in combined,
        f"stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def case_ungrouped_is_refused(root: Path) -> None:
    body = """\
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
"""
    write_config(root, body)
    result = run_gate(root)
    check(
        "an ungrouped config is refused",
        result.returncode != 0,
        f"exit {result.returncode}; stdout={result.stdout!r}",
    )
    combined = result.stdout + result.stderr
    check(
        "the refusal names groups",
        "group" in combined.lower(),
        f"stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def case_empty_patterns_is_refused(root: Path) -> None:
    body = """\
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      github-actions:
        patterns: []
"""
    write_config(root, body)
    result = run_gate(root)
    check(
        "a group with empty patterns is refused",
        result.returncode != 0,
        f"exit {result.returncode}; stdout={result.stdout!r}",
    )
    combined = result.stdout + result.stderr
    check(
        "the refusal names patterns",
        "pattern" in combined.lower(),
        f"stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def case_bad_version_is_refused(root: Path) -> None:
    body = CLEAN_BODY.replace("version: 2", "version: 1")
    write_config(root, body)
    result = run_gate(root)
    check(
        "a config declaring version 1 is refused",
        result.returncode != 0,
        f"exit {result.returncode}; stdout={result.stdout!r}",
    )
    combined = result.stdout + result.stderr
    check(
        "the refusal names version",
        "version" in combined.lower(),
        f"stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def case_clean_fixture_passes(root: Path) -> None:
    write_config(root, CLEAN_BODY)
    result = run_gate(root)
    check(
        "a clean github-actions weekly grouped config passes",
        result.returncode == 0 and "PASS:" in result.stdout,
        f"exit {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}",
    )


def main() -> None:
    isolated = [
        case_missing_file_is_refused,
        case_wrong_ecosystem_is_refused,
        case_monthly_interval_is_refused,
        case_ungrouped_is_refused,
        case_empty_patterns_is_refused,
        case_bad_version_is_refused,
        case_clean_fixture_passes,
    ]
    for func in isolated:
        with tempfile.TemporaryDirectory() as tmp:
            func(Path(tmp))

    case_live_file_exists()
    case_live_shape()
    case_live_validator_accepts()

    print("")
    for text in NOTES:
        print(f"NOT VERIFIED: {text}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print(
        "PASS: dependabot config suite - live file covers github-actions weekly "
        "and grouped, the validator accepts it, and every breach shape is refused"
    )


if __name__ == "__main__":
    main()
