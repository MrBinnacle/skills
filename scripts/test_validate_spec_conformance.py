#!/usr/bin/env python3
"""Suite for validate_spec_conformance.py.

WHAT IS TESTED IN-PROCESS AND WHAT IS NOT
    The allowance classifier is a pure function over one error line, so it is
    tested directly against captured reference-validator output. The subprocess
    path needs `npx` and a package download, which is a network dependency this
    suite refuses to require: a suite that fails on a plane is a suite people
    stop running. The live run is exercised by CI instead, and this file says so
    out loud through `note()` rather than leaving the gap silent.

THE PROPERTY THAT MATTERS
    An allowance that matched too widely would turn this gate decorative. Every
    tolerated error is therefore pinned twice: once that it IS tolerated, and
    once that a NEIGHBOURING error which must not be tolerated is refused by the
    same pattern. The neighbour cases are the real assertions here.

ASCII only, source and output both. Run with PYTHONUTF8=1.

Run directly:  python scripts/test_validate_spec_conformance.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_spec_conformance as spec  # noqa: E402

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


# Captured verbatim from `skills-ref@0.1.5 validate` on 2026-08-24. Editing
# these to fit the patterns would defeat the file.
FIELD_ERR = (
    "Unexpected fields in frontmatter: {fields}. Only allowed-tools, "
    "compatibility, description, license, metadata, name are allowed."
)
LONG_DESC = "Description exceeds 1024 character limit ({n} chars)"


def tolerated(line: str, allowances) -> bool:
    return spec.allowance_for(line, allowances) is not None


def case_published_tolerates_only_the_declared_key() -> None:
    a = spec.PUBLISHED_ALLOWANCES
    check(
        "published tree tolerates disable-model-invocation",
        tolerated(FIELD_ERR.format(fields="disable-model-invocation"), a),
    )
    check(
        "published tree does NOT tolerate an over-long description",
        not tolerated(LONG_DESC.format(n=1271), a),
    )
    check(
        "published tree does NOT tolerate author/date/version",
        not tolerated(FIELD_ERR.format(fields="author, date, version"), a),
        "those are stripped on promotion; a PUBLISHED card carrying them is a breach",
    )
    check(
        "published tree does NOT tolerate invalid YAML",
        not tolerated("Invalid YAML in frontmatter: YAMLException: bad indentation", a),
        "this is the class that rejected two live cards on 2026-08-24",
    )


def case_candidate_tolerates_exactly_what_promotion_fixes() -> None:
    a = spec.CANDIDATE_ALLOWANCES
    for fields in ("author", "date", "version", "author, date", "author, date, version"):
        check(
            f"candidate tree tolerates promotion-stripped keys: {fields}",
            tolerated(FIELD_ERR.format(fields=fields), a),
        )
    check(
        "candidate tree tolerates an over-long description",
        tolerated(LONG_DESC.format(n=1034), a),
    )
    check(
        "candidate tree does NOT tolerate invalid YAML",
        not tolerated("Invalid YAML in frontmatter: YAMLException: bad indentation", a),
    )
    check(
        "candidate tree does NOT tolerate a missing name",
        not tolerated("Missing required field: name", a),
    )


def case_an_unknown_key_riding_alongside_a_known_one_is_refused() -> None:
    """The load-bearing neighbour case.

    A prefix match would tolerate `disable-model-invocation, evil` because it
    starts with the allowed spelling. The patterns stop at the period that ends
    the field list, so the list must match exactly and an extra key fails.
    """
    for allowances, label in (
        (spec.PUBLISHED_ALLOWANCES, "published"),
        (spec.CANDIDATE_ALLOWANCES, "candidate"),
    ):
        check(
            f"{label} tree refuses an unknown key riding with the allowed one",
            not tolerated(
                FIELD_ERR.format(fields="disable-model-invocation, something-else"),
                allowances,
            ),
        )
        check(
            f"{label} tree refuses an unknown key alone",
            not tolerated(FIELD_ERR.format(fields="something-else"), allowances),
        )


def case_candidate_allowances_are_a_superset_of_published() -> None:
    """Stated as a property so the two lists cannot drift apart by editing one.

    A candidate is a card on its way into `skills/`. Anything the published tree
    tolerates the queue must tolerate too, or promotion would be the first place
    a card ever passed.
    """
    published = {p.pattern for p, _ in spec.PUBLISHED_ALLOWANCES}
    candidate = {p.pattern for p, _ in spec.CANDIDATE_ALLOWANCES}
    check(
        "every published allowance is also a candidate allowance",
        published <= candidate,
        str(published - candidate),
    )


def case_error_lines_are_read_per_bullet() -> None:
    """One card can carry a tolerated error and a fatal one at once.

    Reading the whole output as a blob would let the tolerated one mask the
    fatal one. The parser returns bullets, and the caller classifies each.
    """
    output = (
        "Validation failed for _quarantine/x:\n"
        "  - " + FIELD_ERR.format(fields="author, date, version") + "\n"
        "  - Invalid YAML in frontmatter: YAMLException: bad indentation\n"
    )
    lines = spec.error_lines(output)
    check("both errors are parsed out separately", len(lines) == 2, str(lines))
    verdicts = [tolerated(line, spec.CANDIDATE_ALLOWANCES) for line in lines]
    check(
        "the tolerated error does not mask the fatal one beside it",
        verdicts == [True, False],
        str(verdicts),
    )


def case_a_success_run_yields_no_error_lines() -> None:
    check(
        "a passing card contributes no error lines",
        spec.error_lines("Valid skill: skills/engineering/x\n") == [],
    )


def case_declared_divergences_carry_reasons() -> None:
    for allowances, label in (
        (spec.PUBLISHED_ALLOWANCES, "published"),
        (spec.CANDIDATE_ALLOWANCES, "candidate"),
    ):
        check(
            f"every {label} allowance states a reason",
            all(reason.strip() for _, reason in allowances),
        )


def main() -> None:
    case_published_tolerates_only_the_declared_key()
    case_candidate_tolerates_exactly_what_promotion_fixes()
    case_an_unknown_key_riding_alongside_a_known_one_is_refused()
    case_candidate_allowances_are_a_superset_of_published()
    case_error_lines_are_read_per_bullet()
    case_a_success_run_yields_no_error_lines()
    case_declared_divergences_carry_reasons()

    note(
        "the live subprocess run against the real reference validator is NOT "
        "exercised here -- it needs npx and a package download. CI runs it."
    )

    print("")
    for text in NOTES:
        print(f"NOT VERIFIED: {text}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: spec-conformance allowance suite, all cases correct")


if __name__ == "__main__":
    main()
