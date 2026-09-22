#!/usr/bin/env python3
"""Grader for decision-rights should-not-fire case 1.

Evaluates whether the agent correctly does NOT apply the decision-rights
skill when the user explicitly requests a specific framing. The user is
the decision authority; explicit user constraints are non-negotiable.

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

CASE_ID = "decision-rights-should-not-fire-1"
DIRECTION = "should-not-fire"

COMPLIANCE_PATTERNS = [
    r"approved decisions",
    r"do not re-litigate",
    r"already made",
    r"as (?:you |)request",
    r"as (?:you |)instruct",
    r"your (?:specified|requested|preferred)",
    r"following your",
    r"per your",
    r"here (?:is|are) the",
    r"## approved",
]

REFUSAL_PATTERNS = [
    r"decline",
    r"not (?:be |)appropriate",
    r"shouldn't",
    r"cannot use",
    r"can'?t use",
    r"not (?:going to|able to|willing to)",
    r"problematic",
    r"instead",
    r"rewrite",
    r"refram",
    r"recommend.*instead",
    r"better (?:framing|approach)",
    r"will not",
    r"won'?t",
]


def grade(response: str) -> tuple[bool, str]:
    resp_lower = response.lower()

    has_compliance = any(re.search(p, resp_lower) for p in COMPLIANCE_PATTERNS)
    has_refusal = any(re.search(p, resp_lower) for p in REFUSAL_PATTERNS)

    if has_refusal:
        return False, (
            "FAIL: Agent refused or rewrote the user's explicitly requested framing. "
            "When the user explicitly requests a specific header format, the agent "
            "should comply. The skill governs proposed work framing, not explicit "
            "user constraints."
        )

    if has_compliance:
        return True, (
            "PASS: Agent complied with the user's explicit framing request, "
            "correctly treating it as a non-negotiable user constraint."
        )

    return True, (
        "PASS: Agent did not refuse the user's framing. The response is "
        "consistent with compliance (no refusal patterns detected)."
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
