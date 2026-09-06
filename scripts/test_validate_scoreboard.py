#!/usr/bin/env python3
"""Negative controls for `check_controlled_section_restates_nothing`.

The check this file guards was added because the README carried
`paired verdict: not yet established` for three days after the card recorded
`CANT_TELL_YET` with a dated receipt, while every check in
`validate_scoreboard.py` passed. A check written in response to a silent drift
has to be shown going red on that drift, or it is the same kind of green the
drift already survived.

Each control below reintroduces one shape of the defect into a copy of the live
tree and requires the check to refuse it. The positive control runs the check on
the unmodified tree and requires it to pass, so a control that fails for an
unrelated reason -- a broken fixture, a moved section -- is distinguishable from
one that fails because the check works.

Run: python scripts/test_validate_scoreboard.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO_ROOT / "scripts" / "validate_scoreboard.py"

_FAILURES: list[str] = []


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _tree(tmp: Path) -> Path:
    """A copy of the live tree, so a control edits a fixture and not the repo."""
    root = tmp / "repo"
    shutil.copytree(
        _REPO_ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules", ".venv"),
    )
    return root


def _readme(root: Path) -> Path:
    return root / "README.md"


def _controlled_section(text: str) -> str:
    """The section the check guards, located the same way the check locates it."""
    start = text.index("### Controlled results")
    rest = text[start + len("### Controlled results") :]
    end = rest.index("\n### ") if "\n### " in rest else rest.index("\n## ")
    return rest[:end]


def check(name: str, condition: bool, detail: str) -> None:
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}: {detail}")
        _FAILURES.append(name)


def case_live_tree_passes() -> None:
    """Positive control: the check must pass on the tree as it stands.

    Without this, a control that goes red for an unrelated reason reads as proof
    the check works.
    """
    result = _run(_REPO_ROOT)
    check(
        "live tree passes",
        result.returncode == 0,
        f"exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}",
    )


def case_restated_verdict_is_refused() -> None:
    """The exact defect: a verdict copied into the page beside the card's record."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(Path(tmp))
        readme = _readme(root)
        text = readme.read_text(encoding="utf-8")
        section = _controlled_section(text)
        poisoned = text.replace(
            section, section + "\nIts paired verdict is `CANT_TELL_YET`.\n", 1
        )
        assert poisoned != text, "poisoning did not change the README"
        readme.write_text(poisoned, encoding="utf-8", newline="\n")

        result = _run(root)
        check(
            "a restated verdict is refused",
            result.returncode != 0 and "restates the verdict" in result.stdout + result.stderr,
            f"exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}",
        )


def case_stale_restatement_is_refused() -> None:
    """The original drift, verbatim: the wording that outlived the record.

    `not yet established` carries no verdict token, so a check that only looked
    for the closed vocabulary would let this exact sentence back in. It is caught
    because the section may not restate the card's controlled fields at all --
    the phrase sits beside the card name and the check refuses the verdict copy
    that accompanies it. Kept as its own control so the regression that motivated
    the check is named in the suite.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(Path(tmp))
        readme = _readme(root)
        text = readme.read_text(encoding="utf-8")
        section = _controlled_section(text)
        poisoned = text.replace(
            section,
            section + "\n* screen result: `CANT_TELL_YET`\n* paired verdict: not yet established\n",
            1,
        )
        readme.write_text(poisoned, encoding="utf-8", newline="\n")

        result = _run(root)
        check(
            "the original drifted wording is refused",
            result.returncode != 0,
            f"exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}",
        )


def case_naming_an_unmeasured_card_is_refused() -> None:
    """Identity drift: the page claims a card is measured when its record does not."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(Path(tmp))
        readme = _readme(root)
        text = readme.read_text(encoding="utf-8")
        section = _controlled_section(text)
        poisoned = text.replace(
            section, section + "\nAlso `halt-as-deliverable`.\n", 1
        )
        readme.write_text(poisoned, encoding="utf-8", newline="\n")

        result = _run(root)
        check(
            "naming an unmeasured card is refused",
            result.returncode != 0 and "disagree about which cards" in result.stdout + result.stderr,
            f"exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}",
        )


def case_dropping_a_measured_card_is_refused() -> None:
    """The other direction: the record carries a result the page does not name."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(Path(tmp))
        readme = _readme(root)
        text = readme.read_text(encoding="utf-8")
        section = _controlled_section(text)
        poisoned = text.replace(section, section.replace("git-pull-rebase-trap", "REMOVED"), 1)
        assert poisoned != text, "poisoning did not change the README"
        readme.write_text(poisoned, encoding="utf-8", newline="\n")

        result = _run(root)
        check(
            "dropping a measured card is refused",
            result.returncode != 0 and "disagree about which cards" in result.stdout + result.stderr,
            f"exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}",
        )


def case_missing_section_is_refused() -> None:
    """A renamed or deleted section must fail loudly rather than pass vacuously.

    This is the failure mode a section-scoped check invites: the anchor moves,
    the search finds nothing, and 'no violations in a section I could not find'
    reads identically to 'no violations'.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = _tree(Path(tmp))
        readme = _readme(root)
        text = readme.read_text(encoding="utf-8")
        poisoned = text.replace("### Controlled results", "### Results", 1)
        assert poisoned != text, "poisoning did not change the README"
        readme.write_text(poisoned, encoding="utf-8", newline="\n")

        result = _run(root)
        check(
            "a missing section is refused rather than passing vacuously",
            result.returncode != 0 and "no '### Controlled results' section" in result.stdout + result.stderr,
            f"exit {result.returncode}: {result.stdout.strip()} {result.stderr.strip()}",
        )


def main() -> int:
    print("validate_scoreboard: controlled-section restatement controls")
    case_live_tree_passes()
    case_restated_verdict_is_refused()
    case_stale_restatement_is_refused()
    case_naming_an_unmeasured_card_is_refused()
    case_dropping_a_measured_card_is_refused()
    case_missing_section_is_refused()
    if _FAILURES:
        print(f"\nFAILED: {len(_FAILURES)} control(s): {', '.join(_FAILURES)}")
        return 1
    print("\nPASS: every control fired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
