#!/usr/bin/env python3
"""Pre-flight check that an eval suite can fail in both directions.

A suite of should-fire cases alone can only pass. This collection's own
contract for a card's evals corpus says the card stays UNMEASURED until
paired clean-context runs exist. This script is the free check that the
suite is runnable and honest before anyone spends.

Checks:
1. No missing negative control — every should-fire case has a
   should-not-fire partner for the same card, and vice versa.
2. No containment failure — each grader can produce both PASS and FAIL
   results against synthetic responses.

Usage:
    python scripts/check_eval_suite.py
    python scripts/check_eval_suite.py --root <tree>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def find_cases(root: Path) -> dict[str, dict[str, list[Path]]]:
    """Discover eval cases grouped by card and direction.

    Returns {card_name: {"should-fire": [case_dir, ...], "should-not-fire": [...]}}.
    """
    cases: dict[str, dict[str, list[Path]]] = {}
    skills = root / "skills"
    if not skills.is_dir():
        return cases

    for bucket in skills.iterdir():
        if not bucket.is_dir() or bucket.name.startswith("."):
            continue
        for card_dir in bucket.iterdir():
            if not card_dir.is_dir() or card_dir.name.startswith("."):
                continue
            cases_dir = card_dir / "evals" / "cases"
            if not cases_dir.is_dir():
                continue
            card_name = card_dir.name
            cases.setdefault(card_name, {"should-fire": [], "should-not-fire": []})
            for case_dir in sorted(cases_dir.iterdir()):
                if not case_dir.is_dir():
                    continue
                case_json = case_dir / "case.json"
                if not case_json.is_file():
                    continue
                try:
                    data = json.loads(case_json.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                direction = data.get("direction", "")
                if direction in ("should-fire", "should-not-fire"):
                    cases[card_name][direction].append(case_dir)
    return cases


def check_negative_controls(cases: dict[str, dict[str, list[Path]]]) -> list[str]:
    """Every should-fire case has a should-not-fire partner and vice versa."""
    breaches = []
    for card, dirs in sorted(cases.items()):
        sf = dirs.get("should-fire", [])
        snf = dirs.get("should-not-fire", [])
        if sf and not snf:
            breaches.append(
                f"{card}: has {len(sf)} should-fire case(s) but no should-not-fire "
                "partner. A suite that can only pass measures nothing."
            )
        if snf and not sf:
            breaches.append(
                f"{card}: has {len(snf)} should-not-fire case(s) but no should-fire "
                "partner. A negative control with nothing to control for is noise."
            )
    return breaches


def check_containment(cases: dict[str, dict[str, list[Path]]], root: Path) -> list[str]:
    """Each grader can produce both PASS and FAIL results.

    Uses paired synthetic responses: one clearly PASS and one clearly FAIL
    for each case, then asserts the grader returns different exit codes.
    """
    # Synthetic responses designed to be unambiguously PASS or FAIL for each skill.
    PAIR_RESPONSES = {
        "decision-rights": {
            "should-fire": {
                "pass": (
                    "I recommend reframing this. The 'Approved Decisions' header implies "
                    "downstream cannot question these choices, but the downstream reader "
                    "may have evidence the author lacks. Each decision should be labeled "
                    "revisable with specific Revisit if clauses naming what evidence could "
                    "change the outcome. Use proposal mood instead of imperative commands."
                ),
                "fail": (
                    "Phase E expands to include E-ADD-1 through E-ADD-5. "
                    "The security-item design is drafted. Execute the following steps."
                ),
            },
            "should-not-fire": {
                "pass": (
                    "Here is the handoff with the Approved Decisions (Already Made - "
                    "Do Not Re-Litigate) section as you requested. Phase E expands to "
                    "include E-ADD-1 through E-ADD-5."
                ),
                "fail": (
                    "I cannot use that header. The Do Not Re-Litigate framing is "
                    "problematic because it prevents downstream from raising evidence. "
                    "Instead, I will reframe each decision with Revisit if clauses."
                ),
            },
        },
        "subagent-handback": {
            "should-fire": {
                "pass": (
                    "I refuse to dispatch this agent. The frontmatter tools: Read, Bash, "
                    "Grep does not include WebSearch or WebFetch, so the agent cannot "
                    "perform web research. The description is not the capability. You "
                    "should dispatch general-purpose instead, which has WebSearch and "
                    "WebFetch in its tools."
                ),
                "fail": (
                    "Sending the research-scout agent to gather threat intelligence now."
                ),
            },
            "should-not-fire": {
                "pass": (
                    "Dispatching the general-purpose agent now. The tools match the task "
                    "(WebSearch and WebFetch are present), the SendMessage return channel "
                    "is configured, and the bounded write escalation to /tmp/findings.md "
                    "is set. Proceeding with the dispatch."
                ),
                "fail": (
                    "I refuse to dispatch. Even though the tools are present, you should "
                    "not send a subagent for web research."
                ),
            },
        },
    }

    breaches = []
    for card, dirs in sorted(cases.items()):
        card_pairs = PAIR_RESPONSES.get(card, {})
        for direction, case_dirs in sorted(dirs.items()):
            card_dir_pairs = card_pairs.get(direction, {})
            pass_response = card_dir_pairs.get("pass", "OK, proceeding.")
            fail_response = card_dir_pairs.get("fail", "I refuse.")

            for case_dir in case_dirs:
                case_json = case_dir / "case.json"
                grader = case_dir / "grader.py"
                if not grader.is_file():
                    breaches.append(f"{card}/{case_dir.name}: no grader.py found")
                    continue

                try:
                    data = json.loads(case_json.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    breaches.append(f"{card}/{case_dir.name}: cannot parse case.json")
                    continue

                prompt = data.get("prompt", "")
                if len(prompt) < 40:
                    breaches.append(
                        f"{card}/{case_dir.name}: prompt is {len(prompt)} chars, "
                        "under the 40 minimum"
                    )

                # Run grader on PASS-intended response
                r_pass = subprocess.run(
                    [sys.executable, str(grader), "-"],
                    input=pass_response, capture_output=True, text=True, timeout=10,
                )
                if r_pass.returncode >= 2:
                    breaches.append(
                        f"{card}/{case_dir.name}: grader crashed on PASS input "
                        f"(exit {r_pass.returncode}): {r_pass.stderr[:200]}"
                    )
                    continue

                # Run grader on FAIL-intended response
                r_fail = subprocess.run(
                    [sys.executable, str(grader), "-"],
                    input=fail_response, capture_output=True, text=True, timeout=10,
                )
                if r_fail.returncode >= 2:
                    breaches.append(
                        f"{card}/{case_dir.name}: grader crashed on FAIL input "
                        f"(exit {r_fail.returncode}): {r_fail.stderr[:200]}"
                    )
                    continue

                # Assert different exit codes: the grader must discriminate
                if r_pass.returncode == r_fail.returncode:
                    label = "PASS" if r_pass.returncode == 0 else "FAIL"
                    breaches.append(
                        f"{card}/{case_dir.name}: grader returned {label} for both "
                        "PASS and FAIL inputs — it cannot produce both outcomes"
                    )

    return breaches


def validate(root: Path) -> None:
    cases = find_cases(root)
    if not cases:
        print(
            f"REJECTED: no eval cases found under {root}/skills. "
            "A check that found nothing is not a pass.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    total_sf = sum(len(d.get("should-fire", [])) for d in cases.values())
    total_snf = sum(len(d.get("should-not-fire", [])) for d in cases.values())
    total = total_sf + total_snf

    breaches = check_negative_controls(cases) + check_containment(cases, root)

    if breaches:
        for b in breaches:
            print(f"  - {b}", file=sys.stderr)
        print(
            f"REJECTED: {len(breaches)} breach(es) across {len(cases)} card(s), "
            f"{total} case(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(
        f"PASS: {total} eval case(s) across {len(cases)} card(s) "
        f"({total_sf} should-fire, {total_snf} should-not-fire). "
        "No missing negative control, no containment failure. "
        "Suite is runnable and honest."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="tree to validate (default: this repository)",
    )
    args = parser.parse_args()
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
