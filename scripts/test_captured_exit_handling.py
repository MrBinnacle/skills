#!/usr/bin/env python3
"""Suite that every out="$(cmd)" under set -e carries a failure branch.

The defect: under set -e, a non-zero exit from the captured command aborts at
the assignment. echo "$out" never runs. The anti-vacuity grep on the next line
is unreachable on the only occasion it matters.  The fix appends
"|| { echo "$out"; exit 1; }" to the assignment so the diagnostic survives.

This test parses tests.yml as text, finds run: blocks that set -e, and asserts
that every out="$(...)" assignment in those blocks carries the failure branch.

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


ASSIGN_RE = re.compile(r'^\s*out="\$\(([^)]+)\)"\s*$')
ASSIGN_WITH_ENV_RE = re.compile(r'^\s*out="\$\(.*?PYTHONUTF8=1\s+python\b[^)]+\)"\s*$')
FAILURE_BRANCH_RE = re.compile(r'^\s*out="\$\(.*\)"\s*\|\|\s*\{\s*echo\s+"\$out"\s*;\s*exit\s+1\s*;\s*\}\s*$')


def parse_run_blocks(text: str) -> list[tuple[int, str]]:
    """Extract (start_line, body) for every run: | block."""
    lines = text.splitlines()
    blocks: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        if re.match(r'^\s*run:\s*\|', lines[i]):
            start = i + 1  # 1-indexed
            # determine indentation of block content
            m = re.match(r'^(\s*)', lines[i])
            base_indent = len(m.group(1)) if m else 0
            i += 1
            body_lines: list[str] = []
            while i < len(lines):
                line = lines[i]
                # blank lines belong to the block
                if line.strip() == "":
                    body_lines.append(line)
                    i += 1
                    continue
                # check indentation
                line_indent = len(line) - len(line.lstrip())
                if line_indent > base_indent:
                    body_lines.append(line)
                    i += 1
                else:
                    break
            blocks.append((start, "\n".join(body_lines)))
        else:
            i += 1
    return blocks


def main() -> int:
    if not WORKFLOW.exists():
        print(f"FAIL workflow file not found: {WORKFLOW}")
        return 1

    text = WORKFLOW.read_text()
    blocks = parse_run_blocks(text)

    note(f"parsed {len(blocks)} run: blocks from {WORKFLOW.name}")

    guarded = 0
    flagged = 0
    for start_line, body in blocks:
        has_set_e = bool(re.search(r'set\s+-e', body))
        if not has_set_e:
            continue
        guarded += 1

        # find all out="$(...)" assignments (not the failure-branch form)
        for i, line in enumerate(body.splitlines(), start=start_line + 1):
            if ASSIGN_RE.match(line) and not ASSIGN_WITH_ENV_RE.match(line) and not FAILURE_BRANCH_RE.match(line):
                flagged += 1
                check(
                    f"line {i}: assignment has failure branch",
                    False,
                    f"out=\"$(...)\" without || {{ echo \"$out\"; exit 1; }}",
                )

        # also check the env-prefixed form
        for i, line in enumerate(body.splitlines(), start=start_line + 1):
            if ASSIGN_WITH_ENV_RE.match(line) and not FAILURE_BRANCH_RE.match(line):
                flagged += 1
                check(
                    f"line {i}: env-prefixed assignment has failure branch",
                    False,
                    f"out=\"$($(...) python ...)\" without || {{ echo \"$out\"; exit 1; }}",
                )

    note(f"{guarded} run: blocks with set -e; {flagged} bare assignments found")

    if flagged == 0:
        check("all guarded assignments carry failure branch", True)
    else:
        check("all guarded assignments carry failure branch", False,
              f"{flagged} bare assignment(s) found")

    # Summary
    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s)")
        return 1
    print(f"\n{len(NOTES)} note(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
