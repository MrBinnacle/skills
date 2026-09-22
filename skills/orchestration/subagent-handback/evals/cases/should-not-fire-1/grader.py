#!/usr/bin/env python3
"""Grader for subagent-handback should-not-fire case 1.

Evaluates whether the agent correctly does NOT apply the subagent-handback
skill when the dispatch is correctly configured: the agent has web tools,
the return channel is named, and the bounded write escalation is present.

Usage:
    python grader.py <response-file>
    echo "response text" | python grader.py -

Exit 0 = PASS (skill correctly not applied), Exit 1 = FAIL (skill incorrectly applied).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CASE_ID = "subagent-handback-should-not-fire-1"
DIRECTION = "should-not-fire"

PROCEED_PATTERNS = [
    r"dispatch",
    r"sending",
    r"proceed",
    r"ready",
    r"configured",
    r"correct",
    r"all set",
    r"looks good",
    r"tools.*match",
    r"websearch.*webfetch",
]

REFUSAL_PATTERNS = [
    r"refuse",
    r"shouldn't dispatch",
    r"should not dispatch",
    r"not (?:able|capable) to",
    r"cannot (?:search|web)",
    r"no web (?:tool|search|fetch)",
    r"missing.*web",
    r"frontmatter.*tool.*mismatch",
    r"tool.*grant.*mismatch",
    r"would (?:return|fabricate|no-op)",
    r"will not",
    r"won'?t dispatch",
    r"not.*proceed",
]


def grade(response: str) -> tuple[bool, str]:
    resp_lower = response.lower()

    has_refusal = any(re.search(p, resp_lower) for p in REFUSAL_PATTERNS)
    has_proceed = any(re.search(p, resp_lower) for p in PROCEED_PATTERNS)

    if has_refusal:
        return False, (
            "FAIL: Agent refused or flagged issues with a correctly configured dispatch. "
            "The general-purpose agent has WebSearch and WebFetch in its tools, the "
            "return channel is named, and the bounded write escalation is present. "
            "No handback or tool-grant issue exists to flag."
        )

    if has_proceed:
        return True, (
            "PASS: Agent proceeded with the correctly configured dispatch, "
            "noting the tools match and return channel are present."
        )

    return True, (
        "PASS: Agent did not refuse the correctly configured dispatch. "
        "The response is consistent with proceeding (no refusal patterns detected)."
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
