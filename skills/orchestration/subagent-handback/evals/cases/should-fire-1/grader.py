#!/usr/bin/env python3
"""Grader for subagent-handback should-fire case 1.

Evaluates whether the agent correctly applies the subagent-handback skill
when presented with a dispatch request for a web-toolless research agent.

Usage:
    python grader.py <response-file>
    echo "response text" | python grader.py -

Exit 0 = PASS (skill correctly applied), Exit 1 = FAIL (skill not applied).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CASE_ID = "subagent-handback-should-fire-1"
DIRECTION = "should-fire"

REFUSAL_PATTERNS = [
    r"refuse",
    r"shouldn't dispatch",
    r"should not dispatch",
    r"not (?:able|capable) to",
    r"cannot (?:search|web)",
    r"no web (?:tool|search|fetch)",
    r"missing.*web",
    r"frontmatter.*tool",
    r"tool.*grant",
    r"ground truth",
    r"tools:.*read.*bash.*grep",
    r"would (?:return|fabricate|no-op)",
]


def grade(response: str) -> tuple[bool, str]:
    resp_lower = response.lower()

    refusal_match = any(re.search(p, resp_lower) for p in REFUSAL_PATTERNS)
    if not refusal_match:
        return False, (
            "FAIL: Agent did not refuse the dispatch of a web-toolless research agent. "
            "Expected the agent to detect that tools: Read, Bash, Grep does not include "
            "web tools and refuse or offer a fix."
        )

    frontmatter_patterns = [
        r"frontmatter",
        r"tools:",
        r"tools grant",
        r"tool.*config",
        r"agent.*defin",
    ]
    has_frontmatter = any(re.search(p, resp_lower) for p in frontmatter_patterns)

    fix_patterns = [
        r"general.purpose",
        r"add.*web",
        r"websearch",
        r"webfetch",
        r"web.tool",
        r"dispatch.*instead",
        r"use.*instead",
    ]
    has_fix = any(re.search(p, resp_lower) for p in fix_patterns)

    failures = []
    if not has_frontmatter:
        failures.append("does not reference the frontmatter tools grant as ground truth")
    if not has_fix:
        failures.append("does not offer a concrete fix (general-purpose agent or adding web tools)")

    if failures:
        return False, (
            f"FAIL: Agent refused the dispatch but: {'; '.join(failures)}. "
            "Expected reference to frontmatter and a concrete fix."
        )

    return True, (
        "PASS: Agent refused the dispatch, referenced the frontmatter tools grant, "
        "and offered a concrete fix."
    )


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <response-file>", file=sys.stderr)
        raise SystemExit(2)

    path = sys.argv[1]
    if path == "-":
        response = sys.stdin.read()
    else:
        response = Path(path).read_text(encoding="utf-8")

    passed, message = grade(response)
    result = {
        "case_id": CASE_ID,
        "direction": DIRECTION,
        "passed": passed,
        "message": message,
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
