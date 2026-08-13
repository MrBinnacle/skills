#!/usr/bin/env python3
"""Suite for validate_voice_provenance.py, including the poison controls.

A guard that has never rejected anything has not been shown to work, so every
rejection case here builds a real BRAND.md and record on disk and runs the real
entrypoint as a subprocess -- not by calling a predicate in-process, which can
stay green while the command-line path is broken.

Each rejection case asserts the run failed AND that it failed for the assertion
under test, so a fixture that goes red for an unrelated reason cannot be read as
the control passing.

Poison fixtures are built in a temp directory rather than checked in. A
checked-in violating BRAND.md would have to be excluded from the real run, and
an exclusion is a hole in the check that exists to have none.

Run directly:  python scripts/test_validate_voice_provenance.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GATE = SCRIPT_DIR / "validate_voice_provenance.py"
REPO_ROOT = SCRIPT_DIR.parent

FAILURES: list[str] = []

# A recorded line carrying the roughness the record exists to preserve: a double
# space after "wrong", a missing apostrophe in "Im". Smoothing either one must
# turn the run red.
ROUGH_LINE = "Im wrong  like 200x a day - but i can iterate really fast"
PLAIN_LINE = "Follow the time stamps."

RECORD = f"""# The record

## The lines

### On method -- 2026-08-12

> {ROUGH_LINE}

> {PLAIN_LINE}
"""


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_gate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def build(root: Path, voice_body: str, record: str = RECORD) -> None:
    (root / "VERBATIM.md").write_text(record, encoding="utf-8")
    (root / "BRAND.md").write_text(
        "# BRAND.md\n\n## Polish\n\nSomething else.\n\n"
        f"## Voice\n\n{voice_body}\n\n## The name\n\nAfter the section.\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Green: the shapes that must pass
# ---------------------------------------------------------------------------


def case_cited_specimen_passes(root: Path) -> None:
    build(
        root,
        f"> {ROUGH_LINE}\n\nSource: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.\n",
    )
    result = run_gate(root)
    check("a cited specimen passes", result.returncode == 0, result.stderr.strip())
    check(
        "a clean run reports a PASS line",
        result.stdout.startswith("PASS:"),
        result.stdout.strip(),
    )


def case_rewrapped_quote_passes(root: Path) -> None:
    """A quote may be re-wrapped to fit a paragraph. It may not be smoothed."""
    build(
        root,
        "> Im wrong  like 200x a day - but i can\n"
        "> iterate really fast\n\n"
        "Source: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.\n",
    )
    result = run_gate(root)
    check(
        "a re-wrapped quote still matches the record",
        result.returncode == 0,
        result.stderr.strip(),
    )


def case_quote_outside_voice_is_ignored(root: Path) -> None:
    """Other sections quote shipped surfaces on purpose. Scope is Voice only."""
    (root / "VERBATIM.md").write_text(RECORD, encoding="utf-8")
    (root / "BRAND.md").write_text(
        "# BRAND.md\n\n## What the repository claims\n\n"
        "> a line quoted from the front page\n\n"
        "In the README's own words (README.md).\n\n"
        f"## Voice\n\n> {PLAIN_LINE}\n\n"
        "Source: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.\n",
        encoding="utf-8",
    )
    result = run_gate(root)
    check(
        "a README quote outside the Voice section is not a voice specimen",
        result.returncode == 0,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# Poison controls: each must fail, and for the right reason
# ---------------------------------------------------------------------------


def case_readme_sourced_specimen_is_red(root: Path) -> None:
    """The ticket's named control: a specimen sourced from README.md."""
    build(
        root,
        f"> {PLAIN_LINE}\n\nRead from [`README.md`](README.md), the shipped front page.\n",
    )
    result = run_gate(root)
    check("a README-sourced specimen is rejected", result.returncode != 0)
    check(
        "a README-sourced specimen is rejected for the right reason",
        "shipped public surface" in result.stderr and "README.md" in result.stderr,
        result.stderr.strip(),
    )


def case_uncited_specimen_is_red(root: Path) -> None:
    build(root, f"> {PLAIN_LINE}\n\n### Register by surface\n\nA table follows.\n")
    result = run_gate(root)
    check("an uncited specimen is rejected", result.returncode != 0)
    check(
        "an uncited specimen is rejected for the right reason",
        "carries no citation" in result.stderr,
        result.stderr.strip(),
    )


def case_smoothed_quote_is_red(root: Path) -> None:
    """The double space is the evidence. Removing it must turn the run red."""
    smoothed = ROUGH_LINE.replace("wrong  like", "wrong like")
    build(
        root,
        f"> {smoothed}\n\nSource: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.\n",
    )
    result = run_gate(root)
    check("a smoothed quote is rejected", result.returncode != 0)
    check(
        "a smoothed quote is rejected for the right reason",
        "not in VERBATIM.md as typed" in result.stderr,
        result.stderr.strip(),
    )


def case_fabricated_quote_with_a_real_citation_is_red(root: Path) -> None:
    """A citation is a claim. Assertion 3 is what makes it checkable."""
    build(
        root,
        "> A sentence nobody ever said, generated to sound right.\n\n"
        "Source: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.\n",
    )
    result = run_gate(root)
    check("a fabricated quote citing the record is rejected", result.returncode != 0)
    check(
        "a fabricated quote is rejected for the right reason",
        "not in VERBATIM.md as typed" in result.stderr,
        result.stderr.strip(),
    )


def case_wrong_file_citation_is_red(root: Path) -> None:
    build(
        root,
        f"> {PLAIN_LINE}\n\nSource: [`NOTES.md`](NOTES.md), some other file.\n",
    )
    result = run_gate(root)
    check("a citation to some other file is rejected", result.returncode != 0)
    check(
        "a wrong-file citation is rejected for the right reason",
        "not VERBATIM.md" in result.stderr,
        result.stderr.strip(),
    )


def case_every_problem_listed_not_first_fail(root: Path) -> None:
    build(
        root,
        f"> {PLAIN_LINE}\n\nRead from [`README.md`](README.md).\n\n"
        "> Another line nobody said.\n\n"
        "Source: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12.\n\n"
        f"> {ROUGH_LINE}\n\n### Register by surface\n",
    )
    result = run_gate(root)
    check("multiple problems are all rejected", result.returncode != 0)
    check(
        "every problem is listed, not just the first",
        "3 voice specimen problem(s)" in result.stderr,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# Refusing rather than passing green on a vacuous run
# ---------------------------------------------------------------------------


def case_missing_voice_section_refuses(root: Path) -> None:
    (root / "VERBATIM.md").write_text(RECORD, encoding="utf-8")
    (root / "BRAND.md").write_text("# BRAND.md\n\n## Polish\n\nNo voice here.\n", encoding="utf-8")
    result = run_gate(root)
    check(
        "a BRAND.md with no Voice section is refused, not silently green",
        result.returncode != 0 and "no '## Voice' section" in result.stderr,
        result.stderr.strip(),
    )


def case_empty_voice_section_refuses(root: Path) -> None:
    build(root, "Prose about voice, but no specimens at all.\n")
    result = run_gate(root)
    check(
        "a Voice section with zero specimens is refused, not silently green",
        result.returncode != 0 and "no voice specimens" in result.stderr,
        result.stderr.strip(),
    )


def case_missing_record_refuses(root: Path) -> None:
    (root / "BRAND.md").write_text(
        f"# BRAND.md\n\n## Voice\n\n> {PLAIN_LINE}\n\nSource: [`VERBATIM.md`](VERBATIM.md).\n",
        encoding="utf-8",
    )
    result = run_gate(root)
    check(
        "a missing record is refused",
        result.returncode != 0 and "missing VERBATIM.md" in result.stderr,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# The live tree
# ---------------------------------------------------------------------------


def case_live_tree_is_clean() -> None:
    result = run_gate(REPO_ROOT)
    check(
        "the shipped BRAND.md passes its own check",
        result.returncode == 0,
        result.stderr.strip(),
    )


def case_deleted_block_specimens_are_gone() -> None:
    """Acceptance: the two specimens quoting the block #66 deleted are gone.

    Checked against the whole file, not only the Voice section, so moving one
    into another section cannot satisfy it.
    """
    body = (REPO_ROOT / "BRAND.md").read_text(encoding="utf-8")
    for fragment, label in (
        ("I kept adding skills to my assistant", "the fabricated opening line"),
        ("recipe card pinned above the stove", "the recipe-card analogy"),
    ):
        check(
            f"{label} is gone from BRAND.md",
            fragment not in body,
            "still present",
        )


def main() -> None:
    isolated = [
        case_cited_specimen_passes,
        case_rewrapped_quote_passes,
        case_quote_outside_voice_is_ignored,
        case_readme_sourced_specimen_is_red,
        case_uncited_specimen_is_red,
        case_smoothed_quote_is_red,
        case_fabricated_quote_with_a_real_citation_is_red,
        case_wrong_file_citation_is_red,
        case_every_problem_listed_not_first_fail,
        case_missing_voice_section_refuses,
        case_empty_voice_section_refuses,
        case_missing_record_refuses,
    ]
    for func in isolated:
        with tempfile.TemporaryDirectory() as tmp:
            func(Path(tmp))

    case_live_tree_is_clean()
    case_deleted_block_specimens_are_gone()

    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: voice-provenance suite, all cases correct")


if __name__ == "__main__":
    main()
