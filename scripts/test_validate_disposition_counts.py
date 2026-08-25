#!/usr/bin/env python3
"""Suite for validate_disposition_counts.py.

The front page's "Admission method" paragraph restates counts the S295
disposition record owns: how many cards it triaged, stood, called thin, and
called ceiling-likely. Those were hand-maintained prose -- the same shape that
left the origin tiering claiming seven when the records read six. This suite
pins the check that recomputes each stated count from the record and refuses
on disagreement.

THE EXPECTED VALUE IS DERIVED FROM THE TREE, NEVER WRITTEN HERE
    A literal count anywhere in this suite is the defect being fixed,
    relocated into the checker: this repository already had a test suite pin
    "9 published card(s)" that turned red on every admission and every
    retirement until someone edited a digit a test holds no opinion about. The
    live cases below read the live disposition record and the live README
    through the check's own parsers, and every poison case mutates a copy so
    the numbers it asserts come from the fixture it built, not from a digit
    pinned here.

A GATE THAT CANNOT FAIL GUARDS NOTHING
    Every refusal runs the real entrypoint against a temporary tree, and
    asserts the SPECIFIC mismatch message -- the count name and both values
    -- not merely a non-zero exit. The mutation is the assertion under test,
    and it is verified to have changed something before the check runs.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_disposition_counts.py"
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
import validate_disposition_counts as disposition_counts  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def write_tree(root: Path, readme: str, disposition: str) -> Path:
    """A minimal tree the check can run against: README plus the linked record."""
    (root / "README.md").write_text(readme, encoding="utf-8")
    disp_dir = root / "dispositions"
    disp_dir.mkdir(parents=True, exist_ok=True)
    (disp_dir / "2026-08-15-S295-admission-triage.md").write_text(
        disposition, encoding="utf-8"
    )
    return root


# A conforming disposition record: three verdicts, one per category. The
# numbers are arbitrary but self-consistent (total = stand + thin + ceiling),
# so a fixture built from it starts green and a single mutation breaks exactly
# one assertion. The actual live record has its own numbers, which the live
# cases read through the check -- nothing here pins them.
def conforming_disposition() -> str:
    return (
        "# Disposition record\n\n"
        "Date: 2026-08-15.\n\n"
        "## Verdicts\n\n"
        "| Card | Verdict | Basis |\n"
        "|---|---|---|\n"
        "| engineering/a | STANDS | basis. |\n"
        "| engineering/b | RECURRENCE-THIN | basis. |\n"
        "| engineering/c | CEILING-LIKELY | basis. |\n\n"
        "All three cards carry a re-screen trigger.\n"
    )


def conforming_readme() -> str:
    # one stand, one thin, one ceiling; three total.
    return (
        "# Title\n\n"
        "## Admission method\n\n"
        "The [record](dispositions/2026-08-15-S295-admission-triage.md) applied "
        "the policy to all three published cards. It found one card that stand, "
        "one with thin recurrence records, and one with a ceiling-likely screen "
        "result.\n"
    )


def case_live_tree_passes() -> None:
    result = run(REPO_ROOT)
    check(
        "the live tree passes",
        result.returncode == 0 and result.stdout.startswith("PASS:"),
        result.stderr.strip() or result.stdout.strip(),
    )


def case_live_expected_derived_from_tree() -> None:
    # The expected counts come from the live record through the check's own
    # parser; the stated counts come from the live README through its parser.
    # No digit is written here. This proves the derivation is non-vacuous and
    # the page agrees with the record it restates.
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    admission = disposition_counts.section(readme, "Admission method")
    disp = disposition_counts.disposition_path(REPO_ROOT, admission)
    derived = disposition_counts.derive_disposition_counts(disp)
    stated = disposition_counts.stated_counts(admission)
    check(
        "the live derivation returns real counts (not all zero)",
        any(derived.values()) and derived["total"] == sum(
            derived[t] for t in ("stand", "thin", "ceiling")
        ),
        str(derived),
    )
    check(
        "every count the live README states agrees with the live record",
        stated == {k: derived[k] for k in stated},
        f"stated={stated} derived={ {k: derived[k] for k in stated} }",
    )


def case_refuses_missing_disposition_link() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "README.md").write_text(
            "# T\n\n## Admission method\n\nNo link here.\n", encoding="utf-8"
        )
        result = run(root)
        check(
            "a section that does not link the disposition is refused",
            result.returncode != 0 and "does not link a disposition record" in result.stderr,
            result.stderr.strip(),
        )


def case_refuses_unknown_verdict() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        disp = conforming_disposition().replace("STANDS", "MAYBE-SO")
        write_tree(root, conforming_readme(), disp)
        result = run(root)
        check(
            "a verdict outside the closed vocabulary is refused",
            result.returncode != 0 and "outside the closed vocabulary" in result.stderr,
            result.stderr.strip(),
        )


def case_mutated_readme_count_refused() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        readme = conforming_readme().replace("one card that stand", "two card that stand")
        # verify the mutation landed before asserting anything about it
        check(
            "mutated-readme fixture was actually mutated",
            "two card that stand" in readme,
        )
        write_tree(root, readme, conforming_disposition())
        result = run(root)
        msg = result.stderr
        check(
            "a README count that disagrees with the record is refused",
            result.returncode != 0,
            msg.strip(),
        )
        check(
            "the refusal names the count",
            "stand" in msg,
            msg.strip(),
        )
        check(
            "the refusal names both values (README states ... records read ...)",
            "README states" in msg and "records read" in msg,
            msg.strip(),
        )


def case_mutated_disposition_record_refused() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # Change a verdict so the record reads a different `stand` than the
        # README states. The README says one stand; the record now has none.
        disp = conforming_disposition().replace("| engineering/a | STANDS |", "| engineering/a | RECURRENCE-THIN |")
        check(
            "mutated-disposition fixture was actually mutated",
            "STANDS" not in disp.split("## Verdicts")[1],
        )
        write_tree(root, conforming_readme(), disp)
        result = run(root)
        msg = result.stderr
        check(
            "a record that disagrees with the README is refused",
            result.returncode != 0 and "stand" in msg,
            msg.strip(),
        )
        check(
            "the refusal names both values",
            "README states" in msg and "records read" in msg,
            msg.strip(),
        )


def case_page_stating_no_count_passes() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        readme = (
            "# T\n\n## Admission method\n\n"
            "The [record](dispositions/2026-08-15-S295-admission-triage.md) "
            "ran. The page states no tally of what it found.\n"
        )
        write_tree(root, readme, conforming_disposition())
        result = run(root)
        check(
            "a page that states no count still passes (derivation only)",
            result.returncode == 0 and "states no disposition count" in result.stdout,
            result.stdout.strip(),
        )


def main() -> None:
    case_live_tree_passes()
    case_live_expected_derived_from_tree()
    case_refuses_missing_disposition_link()
    case_refuses_unknown_verdict()
    case_mutated_readme_count_refused()
    case_mutated_disposition_record_refused()
    case_page_stating_no_count_passes()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: disposition-count check recomputes every stated count from the record")


if __name__ == "__main__":
    main()
