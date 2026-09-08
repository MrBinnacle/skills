#!/usr/bin/env python3
"""Negative controls for `check_prose_claims.py`.

The check this file guards was added after three reader-facing surfaces were
found asserting things that were false while every gate in this repository was
green. A check written in response to a silent drift has to be shown going red
on that drift, or it is the same kind of green the drift already survived.

Each control below reintroduces one shape of the defect into a copy of the live
tree and requires the check to refuse it, AND requires the refusal to name that
defect. Asserting only a non-zero exit is how a control passes for the wrong
reason: the origin-tier fixture in this repository did exactly that on
2026-09-08, when a banner change made it fail before it reached the thing it
tests.

The positive control runs the check on the unmodified tree and requires it to
pass, so a control that fails for an unrelated reason -- a broken copy, a moved
file -- is distinguishable from one that fails because the check works.

Run: python scripts/test_check_prose_claims.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO_ROOT / "scripts" / "check_prose_claims.py"

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
    """A copy of the live tree, so a control edits a fixture and not the repo.

    The copy carries `.git`, because the check enumerates READMEs with
    `git ls-files` rather than a filesystem walk. A copy without it would make
    every control fail at enumeration and prove nothing about the detector.
    """
    root = tmp / "repo"
    shutil.copytree(
        _REPO_ROOT,
        root,
        ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".venv", ".sandcastle"),
    )
    return root


def fail(case: str, detail: str) -> None:
    _FAILURES.append(case)
    print(f"  FAIL {case}: {detail}")


def expect_refusal(case: str, root: Path, substring: str) -> None:
    """The check must reject, and the rejection must name this defect."""
    result = _run(root)
    if result.returncode == 0:
        fail(case, f"ACCEPTED the planted defect\n{result.stdout}{result.stderr}")
        return
    output = result.stdout + result.stderr
    if substring not in output:
        fail(case, f"rejected for the WRONG reason (wanted {substring!r})\n{output}")
        return
    print(f"  ok   {case}")


def case_live_tree_passes(tmp: Path) -> None:
    """Positive control: the unmodified tree passes, so a red below means something."""
    root = _tree(tmp)
    result = _run(root)
    if result.returncode != 0:
        fail(
            "case_live_tree_passes",
            f"the unmodified tree was REJECTED, so no control below is interpretable\n"
            f"{result.stdout}{result.stderr}",
        )
        return
    print("  ok   case_live_tree_passes")


def case_group_readme_omitting_a_card_is_refused(tmp: Path) -> None:
    """A card on disk that the group page does not name.

    This is the shape `_quarantine/README.md` had: the page told a reader the
    directory held less than it did.
    """
    root = _tree(tmp)
    readme = root / "skills" / "engineering" / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "- [**halt-as-deliverable**](halt-as-deliverable/SKILL.md)"
    if marker not in text:
        fail("case_group_readme_omitting_a_card_is_refused", f"anchor absent: {marker!r}")
        return
    cut = text.index(marker)
    readme.write_text(text[:cut].rstrip() + "\n", encoding="utf-8")
    expect_refusal(
        "case_group_readme_omitting_a_card_is_refused",
        root,
        "does not name",
    )


def case_group_readme_inventing_a_card_is_refused(tmp: Path) -> None:
    """A card the group page names that is not on disk."""
    root = _tree(tmp)
    readme = root / "skills" / "meta" / "README.md"
    text = readme.read_text(encoding="utf-8")
    text += "\n- [**a-card-that-does-not-exist**](a-card-that-does-not-exist/SKILL.md) - planted.\n"
    readme.write_text(text, encoding="utf-8")
    expect_refusal(
        "case_group_readme_inventing_a_card_is_refused",
        root,
        "enumerates a card that is not in",
    )


def case_documented_path_that_does_not_exist_is_refused(tmp: Path) -> None:
    """A layout block naming a directory that is not there.

    This is defect 3 exactly: a card README drew `references/`, `assets/` and
    `scripts/` beside a flat directory.
    """
    root = _tree(tmp)
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    anchor = "templates/         global operating-rules template\n"
    if anchor not in text:
        fail("case_documented_path_that_does_not_exist_is_refused", f"anchor absent: {anchor!r}")
        return
    text = text.replace(anchor, anchor + "references/        planted, and not on disk\n", 1)
    readme.write_text(text, encoding="utf-8")
    expect_refusal(
        "case_documented_path_that_does_not_exist_is_refused",
        root,
        "do not exist beside it",
    )


def case_nested_layout_is_read_with_its_indentation(tmp: Path) -> None:
    """A child indented under a parent is that parent's child, not a sibling.

    The first run of this check reported the repository's own README as naming
    three directories that do not exist. They exist, one level under `skills/`.
    Reading each line as a top-level path is the defect; this control plants a
    child that is genuinely absent and requires the refusal to name it WITH its
    parent prefix, which a parser ignoring indentation cannot do.
    """
    root = _tree(tmp)
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    anchor = "  meta/            skills about the skill system itself\n"
    if anchor not in text:
        fail("case_nested_layout_is_read_with_its_indentation", f"anchor absent: {anchor!r}")
        return
    text = text.replace(anchor, anchor + "  absent-group/    planted under skills/\n", 1)
    readme.write_text(text, encoding="utf-8")
    result = _run(root)
    if result.returncode == 0:
        fail("case_nested_layout_is_read_with_its_indentation", "ACCEPTED a planted child path")
        return
    output = result.stdout + result.stderr
    if "skills/absent-group/" not in output:
        fail(
            "case_nested_layout_is_read_with_its_indentation",
            "the refusal did not name the path with its parent prefix, so indentation "
            f"was not honoured\n{output}",
        )
        return
    print("  ok   case_nested_layout_is_read_with_its_indentation")


def case_edited_vendor_contract_is_refused(tmp: Path) -> None:
    """A local edit to the vendored contract fails rather than forking it."""
    root = _tree(tmp)
    contract = root / "scripts" / "vendor" / "population.py"
    contract.write_text(
        contract.read_text(encoding="utf-8") + "\n# planted local edit\n", encoding="utf-8"
    )
    expect_refusal(
        "case_edited_vendor_contract_is_refused",
        root,
        "does not match its pinned digest",
    )


def case_no_group_readme_is_uninterpretable(tmp: Path) -> None:
    """An empty population refuses rather than passing.

    A detector that receives no input reports no defect. That is the failure
    this whole contract exists to prevent, so it must exit 2, not 0.
    """
    root = _tree(tmp)
    for readme in (root / "skills").glob("*/README.md"):
        readme.unlink()
    result = _run(root)
    if result.returncode != 2:
        fail(
            "case_no_group_readme_is_uninterpretable",
            f"expected exit 2 (UNINTERPRETABLE), got {result.returncode}\n"
            f"{result.stdout}{result.stderr}",
        )
        return
    if "examined nothing" not in (result.stdout + result.stderr):
        fail(
            "case_no_group_readme_is_uninterpretable",
            f"exit 2 for the wrong reason\n{result.stdout}{result.stderr}",
        )
        return
    print("  ok   case_no_group_readme_is_uninterpretable")


CASES = (
    case_live_tree_passes,
    case_group_readme_omitting_a_card_is_refused,
    case_group_readme_inventing_a_card_is_refused,
    case_documented_path_that_does_not_exist_is_refused,
    case_nested_layout_is_read_with_its_indentation,
    case_edited_vendor_contract_is_refused,
    case_no_group_readme_is_uninterpretable,
)


def main() -> int:
    print(f"check_prose_claims controls ({len(CASES)} cases)")
    for case in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))
    if _FAILURES:
        print(f"\nFAIL: {len(_FAILURES)} control(s) did not hold: {', '.join(_FAILURES)}")
        return 1
    print(
        f"\nPASS: {len(CASES)} controls verified; the live tree passes and every planted "
        "defect is refused by name"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
