#!/usr/bin/env python3
"""Suite that CI acquires skill-harness only at a pinned point (#468).

The defect: the Evidence scope drift step ran `git clone --depth 1` on
skill-harness with no ref, so CI tested whatever the harness default branch
held that day. A harness change could turn this repository's CI red, or green,
without any change here. On 2026-10-18 that branch was 215 commits past the
v0.3.0 tag and announced a breaking report_schema_version change.

The rule this suite enforces, per workflow step that acquires skill-harness:

- a `pip install` names a released version with `==`, and that version equals
  PINNED_HARNESS_VERSION in validate_standing_costs.py;
- a git acquisition never uses `git clone` (it checks out the default branch).
  The step declares SKILL_HARNESS_REF as a full 40-hex commit SHA and fetches
  exactly "$SKILL_HARNESS_REF".

The SHA form is the interim. `_scope_line`, which the drift step compares
against, is in no skill-harness release yet; 0.3.0 predates it. When a release
carries it, the step moves to `pip install skill-harness==<that version>` and
the version pin moves with it.

Fixture cases show each rule going red before the real workflows are read.

Run directly:  python scripts/test_harness_pin.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_standing_costs import PINNED_HARNESS_VERSION  # noqa: E402

FAILURES: list[str] = []

STEP_SPLIT_RE = re.compile(r"(?m)^\s*- (?=name:|uses:)")
HARNESS_GIT_RE = re.compile(r"github\.com[/:]MrBinnacle/skill-harness\b")
HARNESS_PIP_RE = re.compile(r"pip install[^\n]*?\bskill-harness\b(==(\S+))?")
REF_DECL_RE = re.compile(r"(?m)^\s*SKILL_HARNESS_REF:\s*(\S+)\s*$")
REF_FETCH_RE = re.compile(r'git\b[^\n]*\bfetch\b[^\n]*"\$SKILL_HARNESS_REF"')
FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def harness_pin_violations(workflow: str, pinned_version: str) -> tuple[int, list[str]]:
    """Return (steps that acquire skill-harness, violations found in them)."""
    acquiring = 0
    violations: list[str] = []
    # A YAML comment names a command without running it.
    code = "\n".join(line for line in workflow.splitlines() if not line.lstrip().startswith("#"))
    for step in STEP_SPLIT_RE.split(code):
        name = step.splitlines()[0].strip() if step.strip() else "?"
        pips = list(HARNESS_PIP_RE.finditer(step))
        git = HARNESS_GIT_RE.search(step)
        if not pips and not git:
            continue
        acquiring += 1
        for pip in pips:
            if pip.group(2) is None:
                violations.append(f"{name}: pip installs skill-harness with no == version")
            elif pip.group(2) != pinned_version:
                violations.append(
                    f"{name}: pip installs skill-harness=={pip.group(2)}, "
                    f"PINNED_HARNESS_VERSION is {pinned_version}"
                )
        if not git:
            continue
        if re.search(r"git\b[^\n]*\bclone\b[^\n]*skill-harness", step):
            violations.append(f"{name}: git clone checks out the skill-harness default branch")
        ref = REF_DECL_RE.search(step)
        if ref is None or not FULL_SHA_RE.fullmatch(ref.group(1)):
            violations.append(f"{name}: SKILL_HARNESS_REF is not declared as a full commit SHA")
        if not REF_FETCH_RE.search(step):
            violations.append(f'{name}: no git fetch of "$SKILL_HARNESS_REF"')
    return acquiring, violations


SHA = "0123456789abcdef0123456789abcdef01234567"
PINNED_STEP = f"""
      - name: drift
        env:
          SKILL_HARNESS_REF: {SHA}
        run: |
          git -C "$d" fetch --depth 1 https://github.com/MrBinnacle/skill-harness.git "$SKILL_HARNESS_REF"
"""
FIXTURES: list[tuple[str, str, int]] = [
    # (label, workflow text, expected violation count)
    (
        "the pre-#468 unpinned clone",
        "      - name: drift\n        run: |\n"
        "          git clone --depth 1 https://github.com/MrBinnacle/skill-harness.git \"$d\"\n",
        3,
    ),
    ("a branch name as the ref", PINNED_STEP.replace(SHA, "main"), 1),
    ("a short SHA as the ref", PINNED_STEP.replace(SHA, SHA[:12]), 1),
    ("a declared ref that is never fetched", PINNED_STEP.replace('"$SKILL_HARNESS_REF"', "main"), 1),
    ("an unversioned pip install", "      - name: i\n        run: pip install skill-harness\n", 1),
    ("a released version that disagrees", "      - name: i\n        run: pip install skill-harness==0.0.1\n", 1),
    ("a full-SHA fetch", PINNED_STEP, 0),
    ("a comment that quotes an install", "      # then pip install skill-harness\n" + PINNED_STEP, 0),
    ("the pinned released version", "      - name: i\n        run: pip install skill-harness=={v}\n", 0),
]


def case_fixtures() -> None:
    for label, text, expected in FIXTURES:
        text = text.replace("{v}", PINNED_HARNESS_VERSION)
        acquiring, violations = harness_pin_violations(text, PINNED_HARNESS_VERSION)
        check(
            f"fixture, {label}: {expected} violation(s)",
            acquiring == 1 and len(violations) == expected,
            f"acquiring={acquiring}, violations={violations}",
        )


def case_real_workflows() -> None:
    total = 0
    for path in sorted(WORKFLOWS.glob("*.yml")):
        acquiring, violations = harness_pin_violations(
            path.read_text(encoding="utf-8"), PINNED_HARNESS_VERSION
        )
        total += acquiring
        for violation in violations:
            check(f"{path.name}: skill-harness acquired at a pinned point", False, violation)
    # Anti-vacuity: the drift step acquires the harness. A suite over zero
    # acquiring steps would pass after the step was deleted or renamed away.
    check("at least one workflow step acquires skill-harness", total >= 1, f"found {total}")


def case_suite_is_wired_into_tests_yml() -> None:
    text = (WORKFLOWS / "tests.yml").read_text(encoding="utf-8")
    check(
        "tests.yml runs this suite and requires its PASS line",
        bool(re.search(r"test_harness_pin\.py.*\n(?:.*\n){0,5}.*\^PASS:", text)),
        "no invocation followed by a PASS-line grep",
    )


def main() -> int:
    case_fixtures()
    case_real_workflows()
    case_suite_is_wired_into_tests_yml()
    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s)")
        return 1
    print(f"\nPASS: skill-harness pin, every CI acquisition is pinned ({len(FIXTURES)} fixtures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
