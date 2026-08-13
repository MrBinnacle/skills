#!/usr/bin/env python3
"""Suite for validate_voice_provenance.py, including the poison controls.

A guard that has never rejected anything has not been shown to work, so every
rejection case here builds a real BRAND.md and record on disk and runs the real
entrypoint as a subprocess -- not by calling a predicate in-process, which can
stay green while the command-line path is broken.

Each rejection case asserts the run failed AND that it failed for the assertion
under test, so a fixture that goes red for an unrelated reason cannot be read as
the control passing.

MUTATION-KILLERS -- read before deleting a case as redundant.
    An earlier version of this suite matched specimens by SUBSTRING containment
    and had no case between "identical passes" and "wholly unrelated fails".
    A review reversed the containment direction -- a semantically different check
    -- and the whole suite still passed 22/22 with both CI controls green. The
    cases marked MUTATION-KILLER below are the ones that discriminate:

      - case_strict_substring_is_red   (a fragment of a recorded line)
      - case_superset_quote_is_red     (a recorded line plus added words)

    Between them they pin equality in both directions. Removing either restores
    the gap a suite cannot see from the inside.

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
# space after "wrong", a missing apostrophe in "Im". Smoothing either must go red.
ROUGH_LINE = "Im wrong  like 200x a day - but i can iterate really fast"
PLAIN_LINE = "I told you - you could literally take me at my narrative."
SLOP_LINE = "I kept adding skills to my assistant and I never removed any."

# The record. Note the illustrative blockquote OUTSIDE `## The lines` -- it is
# the fabricated front-page sentence, quoted to show what was removed. It must
# never be citable as the owner's voice.
RECORD = f"""# The record

## Why this file exists

The front page used to open with a sentence the principal did not write:

> {SLOP_LINE}

## The lines

### On method -- 2026-08-12

> {ROUGH_LINE}

### On how it started -- 2026-08-11

> {PLAIN_LINE}
"""

CITE = "Source: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-12."


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


def build(root: Path, voice_body: str, record: str = RECORD, tail: str = "## The name") -> None:
    (root / "VERBATIM.md").write_text(record, encoding="utf-8")
    (root / "BRAND.md").write_text(
        "# BRAND.md\n\n## Polish\n\nSomething else.\n\n"
        f"## Voice\n\n{voice_body}\n\n{tail}\n\nAfter the section.\n",
        encoding="utf-8",
    )


def red(root: Path, name: str, body: str, reason: str, **kw: object) -> None:
    build(root, body, **kw)  # type: ignore[arg-type]
    result = run_gate(root)
    check(f"{name} is rejected", result.returncode != 0, result.stdout.strip())
    check(
        f"{name} is rejected for the right reason",
        reason in result.stderr,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# Green: the shapes that must pass
# ---------------------------------------------------------------------------


def case_cited_specimen_passes(root: Path) -> None:
    build(root, f"> {ROUGH_LINE}\n\n{CITE}\n")
    result = run_gate(root)
    check("a cited specimen passes", result.returncode == 0, result.stderr.strip())
    check(
        "a clean run reports a PASS line",
        result.stdout.startswith("PASS:"),
        result.stdout.strip(),
    )


def case_rewrapped_quote_passes(root: Path) -> None:
    """A quote may be re-wrapped to fit a paragraph. It may not be smoothed."""
    build(root, "> Im wrong  like 200x a day - but i\n> can iterate really fast\n\n" + CITE + "\n")
    result = run_gate(root)
    check(
        "a re-wrapped quote still matches the record",
        result.returncode == 0,
        result.stderr.strip(),
    )


def case_co_mention_passes(root: Path) -> None:
    """Saying where else a line appears is not a provenance claim."""
    build(
        root,
        f"> {ROUGH_LINE}\n\nSource: [`VERBATIM.md`](VERBATIM.md), *On method*, "
        "2026-08-12. The same line also opens README.md.\n",
    )
    result = run_gate(root)
    check(
        "a citation naming the record AND a shipped surface passes",
        result.returncode == 0,
        result.stderr.strip(),
    )


def case_quote_outside_voice_is_ignored(root: Path) -> None:
    """Other sections quote shipped surfaces on purpose. Scope is Voice only."""
    (root / "VERBATIM.md").write_text(RECORD, encoding="utf-8")
    (root / "BRAND.md").write_text(
        "# BRAND.md\n\n## What the repository claims\n\n"
        "> a line quoted from the front page\n\n"
        "In the README's own words (README.md), and it says \"proven\" nowhere.\n\n"
        f"## Voice\n\n> {ROUGH_LINE}\n\n{CITE}\n",
        encoding="utf-8",
    )
    result = run_gate(root)
    check(
        "a README quote outside the Voice section is not a voice specimen",
        result.returncode == 0,
        result.stderr.strip(),
    )


def case_fenced_example_is_ignored(root: Path) -> None:
    """BRAND.md documents its own rules; a fenced example is not a specimen."""
    build(
        root,
        f"> {ROUGH_LINE}\n\n{CITE}\n\nA rejected specimen looks like this:\n\n"
        "```markdown\n> A line nobody said.\n\nRead from README.md.\n```\n",
    )
    result = run_gate(root)
    check(
        "a fenced markdown example is not scanned as a specimen",
        result.returncode == 0,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# Poison controls: each must fail, and for the right reason
# ---------------------------------------------------------------------------


def case_readme_sourced_specimen_is_red(root: Path) -> None:
    """The control the ticket names: a specimen sourced from README.md."""
    red(
        root,
        "a README-sourced specimen",
        f"> {ROUGH_LINE}\n\nSource: read from [`README.md`](README.md), the front page.\n",
        "shipped public surface",
    )


def case_uncited_specimen_is_red(root: Path) -> None:
    red(
        root,
        "an uncited specimen",
        f"> {ROUGH_LINE}\n\n### Register by surface\n\nA table follows.\n",
        "has no Source: line",
    )


def case_incidental_mention_is_not_a_citation(root: Path) -> None:
    """A sentence that happens to name the record must not discharge a citation."""
    red(
        root,
        "prose that merely mentions the record",
        f"> {ROUGH_LINE}\n\nUnlike most repos, we do not treat `VERBATIM.md` as optional.\n",
        "has no Source: line",
    )


def case_smoothed_quote_is_red(root: Path) -> None:
    """The double space is the evidence. Removing it must turn the run red."""
    red(
        root,
        "a smoothed quote",
        f"> {ROUGH_LINE.replace('wrong  like', 'wrong like')}\n\n{CITE}\n",
        "not a recorded line",
    )


def case_fabricated_quote_with_a_real_citation_is_red(root: Path) -> None:
    """A citation is a claim. Matching the record is what makes it checkable."""
    red(
        root,
        "a fabricated quote citing the record",
        f"> A sentence nobody ever said, generated to sound right.\n\n{CITE}\n",
        "not a recorded line",
    )


def case_strict_substring_is_red(root: Path) -> None:
    """MUTATION-KILLER. A fragment of a recorded line is not that line.

    Selective truncation can invert a sentence while every word is genuine, and
    a containment check certifies it as verbatim.
    """
    red(
        root,
        "a strict substring of a recorded line",
        f"> iterate really fast\n\n{CITE}\n",
        "not a recorded line",
    )


def case_superset_quote_is_red(root: Path) -> None:
    """MUTATION-KILLER. A recorded line with words added is not that line."""
    red(
        root,
        "a recorded line with words appended",
        f"> {ROUGH_LINE} and I always ship on time\n\n{CITE}\n",
        "not a recorded line",
    )


def case_inline_italic_quote_is_red(root: Path) -> None:
    """The defect in its ORIGINAL shape. Every replaced specimen looked like this."""
    build(
        root,
        f"> {ROUGH_LINE}\n\n{CITE}\n\n"
        f'**First person, owning the problem.** *"{SLOP_LINE}"* Read off the front page.\n',
    )
    result = run_gate(root)
    check("an inline italic quotation is rejected", result.returncode != 0)
    check(
        "an inline italic quotation is rejected for the right reason",
        "inline quotation" in result.stderr and "blockquote" in result.stderr,
        result.stderr.strip(),
    )


def case_record_prose_quote_is_not_citable(root: Path) -> None:
    """The record's own counter-example must not become citable evidence."""
    red(
        root,
        "a line quoted from the record's prose rather than its lines",
        f"> {SLOP_LINE}\n\n{CITE}\n",
        "not a recorded line",
    )


def case_wrong_section_is_red(root: Path) -> None:
    red(
        root,
        "a citation naming the wrong section",
        f"> {PLAIN_LINE}\n\nSource: [`VERBATIM.md`](VERBATIM.md), *On method*, 2026-08-11.\n",
        "the record files it under",
    )


def case_wrong_date_is_red(root: Path) -> None:
    red(
        root,
        "a citation carrying the wrong date",
        f"> {ROUGH_LINE}\n\nSource: [`VERBATIM.md`](VERBATIM.md), *On method*, 1999-01-01.\n",
        "but the record dates it",
    )


def case_wrong_file_citation_is_red(root: Path) -> None:
    red(
        root,
        "a citation to some other file",
        f"> {ROUGH_LINE}\n\nSource: [`NOTES.md`](NOTES.md), some other file.\n",
        "not VERBATIM.md",
    )


def case_every_problem_listed_not_first_fail(root: Path) -> None:
    build(
        root,
        f"> {ROUGH_LINE}\n\nSource: read from [`README.md`](README.md).\n\n"
        f"> Another line nobody said.\n\n{CITE}\n\n"
        f"> {PLAIN_LINE}\n\n### Register by surface\n",
    )
    result = run_gate(root)
    check("multiple problems are all rejected", result.returncode != 0)
    check(
        "every problem is listed, not just the first",
        "3 voice specimen problem(s)" in result.stderr,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# Section bounds and vacuous runs
# ---------------------------------------------------------------------------


def case_h1_closes_the_section(root: Path) -> None:
    """An H1 appendix must not be pulled into Voice scope."""
    build(
        root,
        f"> {ROUGH_LINE}\n\n{CITE}\n",
        tail="# Appendix\n\n> a line quoted from README\n\nRead from README.md.",
    )
    result = run_gate(root)
    check(
        "an H1 heading closes the Voice section",
        result.returncode == 0,
        result.stderr.strip(),
    )


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


def case_record_without_the_lines_refuses(root: Path) -> None:
    build(root, f"> {ROUGH_LINE}\n\n{CITE}\n", record="# The record\n\nNo lines section.\n")
    result = run_gate(root)
    check(
        "a record with no '## The lines' section is refused, not silently green",
        result.returncode != 0 and "holds no recorded lines" in result.stderr,
        result.stderr.strip(),
    )


def case_missing_record_refuses(root: Path) -> None:
    (root / "BRAND.md").write_text(
        f"# BRAND.md\n\n## Voice\n\n> {ROUGH_LINE}\n\n{CITE}\n", encoding="utf-8"
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
        check(f"{label} is gone from BRAND.md", fragment not in body, "still present")


def main() -> None:
    isolated = [
        case_cited_specimen_passes,
        case_rewrapped_quote_passes,
        case_co_mention_passes,
        case_quote_outside_voice_is_ignored,
        case_fenced_example_is_ignored,
        case_readme_sourced_specimen_is_red,
        case_uncited_specimen_is_red,
        case_incidental_mention_is_not_a_citation,
        case_smoothed_quote_is_red,
        case_fabricated_quote_with_a_real_citation_is_red,
        case_strict_substring_is_red,
        case_superset_quote_is_red,
        case_inline_italic_quote_is_red,
        case_record_prose_quote_is_not_citable,
        case_wrong_section_is_red,
        case_wrong_date_is_red,
        case_wrong_file_citation_is_red,
        case_every_problem_listed_not_first_fail,
        case_h1_closes_the_section,
        case_missing_voice_section_refuses,
        case_empty_voice_section_refuses,
        case_record_without_the_lines_refuses,
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
