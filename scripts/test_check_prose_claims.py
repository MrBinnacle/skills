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
    readme = root / "CATALOG.md"
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
    readme = root / "CATALOG.md"
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


def _set_paired_verdict(evidence: Path, verdict: str) -> bool:
    """Rewrite the record's Paired verdict row to open with VERDICT."""
    lines = evidence.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("| **Paired verdict** |"):
            lines[i] = f"| **Paired verdict** | {verdict}. Planted. |\n"
            evidence.write_text("".join(lines), encoding="utf-8")
            return True
    return False


def case_candidate_with_a_paired_run_is_refused(tmp: Path) -> None:
    """A candidate in `_quarantine/` records a run with and without the skill.

    RETIRED.md says no candidate carries one. This is the PR 510 shape: a
    "no candidate" sentence that a quarantine record had already made false.
    """
    root = _tree(tmp)
    evidence = root / "_quarantine" / "walk-the-recipe" / "EVIDENCE.md"
    if not _set_paired_verdict(evidence, "CANT_TELL_YET"):
        fail("case_candidate_with_a_paired_run_is_refused", "anchor absent: Paired verdict row")
        return
    expect_refusal("case_candidate_with_a_paired_run_is_refused", root, "walk-the-recipe")


def case_second_published_card_with_a_paired_run_is_refused(tmp: Path) -> None:
    """A second published card records a paired run; the prose names only one."""
    root = _tree(tmp)
    evidence = root / "skills" / "engineering" / "mocked-stub" / "EVIDENCE.md"
    if not _set_paired_verdict(evidence, "CANT_TELL_YET"):
        fail("case_second_published_card_with_a_paired_run_is_refused", "anchor absent: Paired verdict row")
        return
    expect_refusal("case_second_published_card_with_a_paired_run_is_refused", root, "mocked-stub")


def case_named_card_without_a_paired_run_is_refused(tmp: Path) -> None:
    """The card the prose names no longer records a paired run."""
    root = _tree(tmp)
    evidence = root / "skills" / "engineering" / "pull-rebase" / "EVIDENCE.md"
    if not _set_paired_verdict(evidence, "UNMEASURED (no_data)"):
        fail("case_named_card_without_a_paired_run_is_refused", "anchor absent: Paired verdict row")
        return
    expect_refusal("case_named_card_without_a_paired_run_is_refused", root, "pull-rebase")


def case_unrecognised_paired_verdict_is_uninterpretable(tmp: Path) -> None:
    """A Paired verdict outside the closed vocabulary refuses rather than guesses."""
    root = _tree(tmp)
    evidence = root / "_quarantine" / "uniform-eol" / "EVIDENCE.md"
    if not _set_paired_verdict(evidence, "TBD"):
        fail("case_unrecognised_paired_verdict_is_uninterpretable", "anchor absent: Paired verdict row")
        return
    result = _run(root)
    output = result.stdout + result.stderr
    if result.returncode != 2 or "unrecognised verdict" not in output:
        fail(
            "case_unrecognised_paired_verdict_is_uninterpretable",
            f"expected exit 2 naming the unrecognised verdict, got {result.returncode}\n{output}",
        )
        return
    print("  ok   case_unrecognised_paired_verdict_is_uninterpretable")


def _append_retired_row(root: Path, cell: str) -> bool:
    retired = root / "RETIRED.md"
    text = retired.read_text(encoding="utf-8")
    anchor = "| Skill | Retired | What made it unnecessary | Evidence |\n|---|---|---|---|\n"
    if anchor not in text:
        return False
    row = f"| `planted-card` | 2026-10 | {cell} | planted |\n"
    retired.write_text(text.replace(anchor, anchor + row, 1), encoding="utf-8")
    return True


def case_retired_row_with_a_screen_exit_is_refused(tmp: Path) -> None:
    """A card retires on a harness cut; both pages still say none has."""
    root = _tree(tmp)
    if not _append_retired_row(root, "`subsumed`. A current receipt carries CUT"):
        fail("case_retired_row_with_a_screen_exit_is_refused", "anchor absent: retired table header")
        return
    result = _run(root)
    output = result.stdout + result.stderr
    if result.returncode == 0:
        fail("case_retired_row_with_a_screen_exit_is_refused", f"ACCEPTED the planted defect\n{output}")
        return
    missing = [site for site in ("RETIRED.md", "CATALOG.md", "planted-card") if site not in output]
    if missing:
        fail("case_retired_row_with_a_screen_exit_is_refused", f"refusal does not name {missing}\n{output}")
        return
    print("  ok   case_retired_row_with_a_screen_exit_is_refused")


def case_screen_exit_not_opening_with_its_word_is_refused(tmp: Path) -> None:
    """A screen exit that mentions the pre-registered trigger is still a screen exit."""
    root = _tree(tmp)
    cell = "A re-screen against the pre-registered trigger returned `CUT`, sub-reason `subsumed`"
    if not _append_retired_row(root, cell):
        fail("case_screen_exit_not_opening_with_its_word_is_refused", "anchor absent: retired table header")
        return
    expect_refusal("case_screen_exit_not_opening_with_its_word_is_refused", root, "screen exit for: planted-card")


def case_on_watch_row_on_the_screen_route_is_refused(tmp: Path) -> None:
    """A card on watch after `CUT(subsumed)` has left the served set on a screen."""
    root = _tree(tmp)
    retired = root / "RETIRED.md"
    text = retired.read_text(encoding="utf-8")
    anchor = "| Card | Removed (release, install SHA, clock start) | Route |"
    cut = text.find(anchor)
    sep = text.find("|---", cut)
    end = text.find("\n", sep) + 1
    if cut < 0 or sep < 0:
        fail("case_on_watch_row_on_the_screen_route_is_refused", "anchor absent: On watch header")
        return
    row = "| `watched-card` | 4.1.0 | `CUT(subsumed)` | planted | 2027-01 | 0 | none | open |\n"
    retired.write_text(text[:end] + row + text[end:], encoding="utf-8")
    expect_refusal("case_on_watch_row_on_the_screen_route_is_refused", root, "watched-card")


def case_retired_routes_disagreeing_with_two_used_is_refused(tmp: Path) -> None:
    """CATALOG.md says the trigger and policy routes were used; drop the policy row."""
    root = _tree(tmp)
    retired = root / "RETIRED.md"
    lines = retired.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in lines if not line.startswith("| `skill-necessity-gate` |")]
    if len(kept) == len(lines):
        fail("case_retired_routes_disagreeing_with_two_used_is_refused", "anchor absent: policy row")
        return
    retired.write_text("".join(kept), encoding="utf-8")
    expect_refusal(
        "case_retired_routes_disagreeing_with_two_used_is_refused",
        root,
        "routes have been used, but RETIRED.md records: platform-fix",
    )


def case_unclassifiable_retired_row_is_uninterpretable(tmp: Path) -> None:
    """A retired row naming no known route cannot answer which exit it took."""
    root = _tree(tmp)
    if not _append_retired_row(root, "It stopped being useful"):
        fail("case_unclassifiable_retired_row_is_uninterpretable", "anchor absent: retired table header")
        return
    result = _run(root)
    output = result.stdout + result.stderr
    if result.returncode != 2 or "planted-card" not in output:
        fail(
            "case_unclassifiable_retired_row_is_uninterpretable",
            f"expected exit 2 naming planted-card, got {result.returncode}\n{output}",
        )
        return
    print("  ok   case_unclassifiable_retired_row_is_uninterpretable")


def case_reworded_claim_sentence_is_refused(tmp: Path) -> None:
    """A pinned sentence that is reworded leaves the check guarding nothing for it."""
    root = _tree(tmp)
    catalog = root / "CATALOG.md"
    text = catalog.read_text(encoding="utf-8")
    sentence = "No card has left on a screen result yet."
    if sentence not in text:
        fail("case_reworded_claim_sentence_is_refused", f"anchor absent: {sentence!r}")
        return
    catalog.write_text(text.replace(sentence, "No card has left on a screen so far.", 1), encoding="utf-8")
    expect_refusal("case_reworded_claim_sentence_is_refused", root, "pinned claim sentence")


CASES = (
    case_live_tree_passes,
    case_candidate_with_a_paired_run_is_refused,
    case_second_published_card_with_a_paired_run_is_refused,
    case_named_card_without_a_paired_run_is_refused,
    case_unrecognised_paired_verdict_is_uninterpretable,
    case_retired_row_with_a_screen_exit_is_refused,
    case_screen_exit_not_opening_with_its_word_is_refused,
    case_on_watch_row_on_the_screen_route_is_refused,
    case_retired_routes_disagreeing_with_two_used_is_refused,
    case_unclassifiable_retired_row_is_uninterpretable,
    case_reworded_claim_sentence_is_refused,
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
