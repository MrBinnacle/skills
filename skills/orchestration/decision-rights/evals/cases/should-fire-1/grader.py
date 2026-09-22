#!/usr/bin/env python3
"""Grader for decision-rights should-fire case 1.

Evaluates whether the agent correctly applies the decision-rights skill
when presented with a handoff draft carrying a blanket do-not-re-litigate
header.

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

CASE_ID = "decision-rights-should-fire-1"
DIRECTION = "should-fire"

REFUSAL_PATTERNS = [
    r"decline",
    r"not (?:be |)appropriate",
    r"instead",
    r"rewrite",
    r"refram",
    r"recommend",
    r"instead of",
    r"better (?:framing|approach|way)",
    r"evidence asymmetry",
    r"less-informed reviewer",
    r"proposal",
    r"revis(?:able|e if)",
    r"non-negotiable",
    r"do not re-litigate.*not",
    r"not.*do not re-litigate",
    r"avoid.*blanket",
    r"blanket.*avoid",
]


def grade(response: str) -> tuple[bool, str]:
    resp_lower = response.lower()

    refusal_match = any(re.search(p, resp_lower) for p in REFUSAL_PATTERNS)
    if not refusal_match:
        return False, (
            "FAIL: Agent did not decline or reframe the blanket do-not-re-litigate header. "
            "Expected the agent to拒绝 or rewrite the 'Approved Decisions (Already Made - "
            "Do Not Re-Litigate)' framing."
        )

    evidence_patterns = [
        r"evidence asymmetry",
        r"less-informed",
        r"downstream.*reader",
        r"evidence.*access",
        r"who.*evidence",
        r"can access.*evidence",
    ]
    has_evidence = any(re.search(p, resp_lower) for p in evidence_patterns)

    revisit_patterns = [
        r"revisit if",
        r"revisable",
        r"revisit.*clause",
        r"evidence.*change",
    ]
    has_revisit = any(re.search(p, resp_lower) for p in revisit_patterns)

    proposal_patterns = [
        r"proposal",
        r"recommend",
        r"informed",
        r"working direction",
        r"not.*order",
        r"not.*command",
    ]
    has_proposal = any(re.search(p, resp_lower) for p in proposal_patterns)

    failures = []
    if not has_evidence:
        failures.append("does not name the evidence asymmetry")
    if not has_revisit:
        failures.append("does not attach Revisit if clauses or label decisions revisable")
    if not has_proposal:
        failures.append("does not convert to proposal mood")

    if failures:
        return False, (
            f"FAIL: Agent declined the header but: {'; '.join(failures)}. "
            "Expected all three properties."
        )

    return True, (
        "PASS: Agent correctly declined the blanket header, named the evidence "
        "asymmetry, labeled decisions revisable with Revisit if clauses, and "
        "used proposal mood."
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
