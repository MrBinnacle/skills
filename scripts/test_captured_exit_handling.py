#!/usr/bin/env python3
"""Suite that every out="$(cmd)" under set -e carries a failure branch.

The defect: under set -e, a non-zero exit from the captured command aborts at
the assignment. echo "$out" never runs. The anti-vacuity grep on the next line
is unreachable on the only occasion it matters.  The fix appends
'|| { echo "$out"; exit 1; }' to the assignment so the diagnostic survives.

This test parses tests.yml as text, finds run: blocks that set -e, and asserts
that every out="$(...)" assignment in those blocks carries the failure branch.
It also asserts that this suite itself is wired into the workflow, so a
regression cannot re-introduce the defect by simply never running the check.

Run directly:  python scripts/test_captured_exit_handling.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"

FAILURES: list[str] = []
NOTES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def note(text: str) -> None:
    print(f"note {text}")
    NOTES.append(text)


# Any line that begins an out="$(...)" capture. The body of the substitution is
# matched non-greedily up to the closing )" so a trailing failure branch is not
# swallowed into the command text.
ASSIGN_LINE_RE = re.compile(r'^\s*out="\$\(')
FAILURE_BRANCH_RE = re.compile(
    r'^\s*out="\$\(.*?\)"\s*\|\|\s*\{\s*echo\s+"\$out"\s*;\s*exit\s+1\s*;\s*\}\s*$'
)


def parse_run_blocks(text: str) -> list[tuple[int, str]]:
    """Extract (first_body_line_1indexed, body) for every run: | block."""
    lines = text.splitlines()
    blocks: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        if re.match(r"^\s*run:\s*\|", lines[i]):
            # first body line is 1-indexed i+2 (lines[i] is run: | at 1-index i+1)
            first_body = i + 2
            m = re.match(r"^(\s*)", lines[i])
            base_indent = len(m.group(1)) if m else 0
            i += 1
            body_lines: list[str] = []
            while i < len(lines):
                line = lines[i]
                if line.strip() == "":
                    body_lines.append(line)
                    i += 1
                    continue
                line_indent = len(line) - len(line.lstrip())
                if line_indent > base_indent:
                    body_lines.append(line)
                    i += 1
                else:
                    break
            blocks.append((first_body, "\n".join(body_lines)))
        else:
            i += 1
    return blocks


def case_every_assignment_carries_failure_branch(text: str) -> int:
    """Return the number of guarded assignments found."""
    blocks = parse_run_blocks(text)
    note(f"parsed {len(blocks)} run: blocks from {WORKFLOW.name}")

    set_e_blocks = 0
    found = 0
    for first_body, body in blocks:
        if not re.search(r"set\s+-e", body):
            continue
        set_e_blocks += 1
        for offset, line in enumerate(body.splitlines()):
            if not ASSIGN_LINE_RE.match(line):
                continue
            line_no = first_body + offset
            found += 1
            check(
                f"line {line_no}: assignment has failure branch",
                bool(FAILURE_BRANCH_RE.match(line)),
                'out="$(...)" without || { echo "$out"; exit 1; }',
            )

    note(f"{set_e_blocks} run: blocks with set -e; {found} out=\"$(...)\" assignment(s)")
    # Anti-vacuity: a workflow that simply deleted every capture would otherwise
    # pass a pure forall-over-empty check. The measured extent at the ticket
    # was 21; require at least one so the suite cannot pass by disappearing.
    check(
        "at least one guarded assignment exists",
        found >= 1,
        f"found {found}",
    )
    return found


def case_suite_is_wired_into_tests_yml(text: str) -> None:
    """A suite that never runs cannot stop a regression (#172)."""
    check(
        "tests.yml invokes this suite",
        "scripts/test_captured_exit_handling.py" in text,
        str(WORKFLOW),
    )
    check(
        "tests.yml requires this suite's PASS line",
        bool(
            re.search(
                r"test_captured_exit_handling\.py.*\n(?:.*\n){0,5}.*\^PASS:",
                text,
            )
        ),
        "no anti-vacuity grep for this suite's PASS line",
    )


def main() -> int:
    if not WORKFLOW.exists():
        print(f"FAIL workflow file not found: {WORKFLOW}")
        return 1

    text = WORKFLOW.read_text(encoding="utf-8")
    case_every_assignment_carries_failure_branch(text)
    case_suite_is_wired_into_tests_yml(text)

    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s)")
        return 1
    print(f"\nPASS: captured-exit handling, all assignments carry a failure branch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
