#!/usr/bin/env python3
"""Suite for validate_card_files.py, including the committed poison fixture."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_card_files.py"
REPO_ROOT = SCRIPT_DIR.parent
POISON = SCRIPT_DIR / "fixtures" / "card-missing-gotchas"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def case_committed_poison_is_red() -> None:
    result = run_checker(POISON)
    check("committed poison fixture is rejected", result.returncode != 0)
    check(
        "missing-file report names the card and file",
        "poison-card" in result.stderr and "gotchas.md" in result.stderr,
        result.stderr.strip(),
    )


def case_zero_cards_is_red(root: Path) -> None:
    (root / "skills").mkdir()
    result = run_checker(root)
    check(
        "a tree with zero cards is rejected",
        result.returncode != 0 and "no published cards" in result.stderr,
        f"rc={result.returncode} err={result.stderr.strip()}",
    )


def case_live_nine_cards_pass() -> None:
    result = run_checker(REPO_ROOT)
    check("the live tree passes", result.returncode == 0, result.stderr.strip())
    check(
        "the live run reports all nine cards",
        "PASS: 9 published card(s)" in result.stdout,
        result.stdout.strip(),
    )


def case_linkcheck_lane_runs_checker() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "links.yml").read_text(
        encoding="utf-8"
    )
    linkcheck = re.search(r"(?ms)^  linkcheck:\n(.*?)(?=^  \S|\Z)", workflow)
    body = linkcheck.group(1) if linkcheck else ""
    check("links workflow has a linkcheck job", linkcheck is not None)
    check(
        "linkcheck runs the card-file suite",
        "python scripts/test_validate_card_files.py" in body,
        body,
    )
    check(
        "linkcheck runs the live card-file checker",
        "python scripts/validate_card_files.py" in body,
        body,
    )


def main() -> None:
    case_committed_poison_is_red()
    with tempfile.TemporaryDirectory() as tmp:
        case_zero_cards_is_red(Path(tmp))
    case_live_nine_cards_pass()
    case_linkcheck_lane_runs_checker()

    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: card-file conformance suite, all cases correct")


if __name__ == "__main__":
    main()
