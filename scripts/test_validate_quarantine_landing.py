#!/usr/bin/env python3
"""Suite for validate_quarantine_landing.py.

WHAT THIS SUITE HAS TO PROVE

    A guard that never fires looks exactly like a guard that works (#249). The
    five fixtures #249 lists are each a named case here, refusing and passing as
    the ticket states:

      1. a new `_quarantine/<skill>/SKILL.md` with no tracked sibling - REFUSE
      2. an edit inside an existing tracked `_quarantine/<skill>/`       - PASS
      3. a new file under `skills/`                                       - PASS
      4. a declared intentional landing                                   - PASS
      5. a new `_quarantine/<skill>/` carrying only non-SKILL.md files    - REFUSE

    Then the run #249's Done-when names: staging the two candidate directories
    that sat untracked on `main` on 2026-09-06 must refuse BOTH, by name. The
    real directories live only in the maintainer's working tree; the case
    builds the same two names in a temporary repository so the proof runs
    anywhere, and the maintainer's check on the live tree is the same command.

    Three more cases pin the marker's edges: a marker whose first line is not
    the declaration does not count, a marker that exists on disk but is NOT
    staged does not count, and an empty index passes with a note (the CI shape).

Every case builds a real temporary git repository with `_quarantine/README.md`
tracked at HEAD, as the live tree has, and calls the real entrypoint.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts" / "validate_quarantine_landing.py"
MARKER = "LANDING.md"
DECLARATION = "intentional-landing: true\n\nLanded on purpose; see the pull request.\n"

# The two directories #249 measured untracked on main at 63252ec, 2026-09-06.
NAMED_CANDIDATES = (
    "_quarantine/curated-context-becomes-the-reviewers-boundary",
    "_quarantine/uniform-eol-rewrite-evades-the-mixed-eol-guard",
)

FAILURES: list[str] = []


def fail(case: str, detail: str) -> None:
    FAILURES.append(case)
    print(f"  FAIL {case}: {detail}")


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=suite", "-c", "user.email=suite@local", *args],
        check=True,
        capture_output=True,
    )


def write(root: Path, rel: str, text: str = "clean contents\n") -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def make_repo(root: Path) -> None:
    """HEAD tracks `_quarantine/README.md` and one landed candidate, as the live tree does."""
    git(root, "init", "-q")
    write(root, "_quarantine/README.md", "# quarantine\n")
    write(root, "_quarantine/landed-candidate/SKILL.md", "# landed\n")
    write(root, "skills/engineering/a-card/SKILL.md", "# card\n")
    git(root, "add", "--", "_quarantine/README.md", "_quarantine/landed-candidate/SKILL.md", "skills/engineering/a-card/SKILL.md")
    git(root, "commit", "-q", "-m", "baseline")


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def expect(case: str, root: Path, refuse: bool, must_name: tuple[str, ...] = ()) -> None:
    result = run(root)
    refused = result.returncode != 0
    if refused != refuse:
        verb = "accepted" if refuse else "refused"
        fail(case, f"{verb} unexpectedly:\n{result.stdout}{result.stderr}")
        return
    missing = [d for d in must_name if f"{d}/" not in result.stdout]
    if missing:
        fail(case, f"refused, but did not name {missing}:\n{result.stdout}")
        return
    print(f"  ok   {case}")


def case_new_candidate_skill_md_refused(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "_quarantine/fresh-candidate/SKILL.md", "# fresh\n")
    git(tmp, "add", "--", "_quarantine/fresh-candidate/SKILL.md")
    expect("case_new_candidate_skill_md_refused", tmp, refuse=True, must_name=("_quarantine/fresh-candidate",))


def case_edit_inside_tracked_candidate_passes(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "_quarantine/landed-candidate/SKILL.md", "# landed, edited\n")
    write(tmp, "_quarantine/landed-candidate/gotchas.md", "# new file in a tracked candidate\n")
    git(tmp, "add", "--", "_quarantine/landed-candidate/SKILL.md", "_quarantine/landed-candidate/gotchas.md")
    expect("case_edit_inside_tracked_candidate_passes", tmp, refuse=False)


def case_new_file_under_skills_passes(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "skills/engineering/new-card/SKILL.md", "# new card\n")
    git(tmp, "add", "--", "skills/engineering/new-card/SKILL.md")
    expect("case_new_file_under_skills_passes", tmp, refuse=False)


def case_declared_landing_passes(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "_quarantine/declared-candidate/SKILL.md", "# declared\n")
    write(tmp, f"_quarantine/declared-candidate/{MARKER}", DECLARATION)
    git(tmp, "add", "--", "_quarantine/declared-candidate")
    expect("case_declared_landing_passes", tmp, refuse=False)


def case_partial_candidate_without_skill_md_refused(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "_quarantine/partial-candidate/gotchas.md", "# only gotchas\n")
    write(tmp, "_quarantine/partial-candidate/worked-case.md", "# only a worked case\n")
    git(tmp, "add", "--", "_quarantine/partial-candidate")
    expect("case_partial_candidate_without_skill_md_refused", tmp, refuse=True, must_name=("_quarantine/partial-candidate",))


def case_the_two_named_candidates_refused_by_name(tmp: Path) -> None:
    """The run #249's Done-when names, on the same two directory names."""
    make_repo(tmp)
    files = {
        NAMED_CANDIDATES[0]: ("SKILL.md", "gotchas.md", "worked-case.md"),
        NAMED_CANDIDATES[1]: ("SKILL.md", "gotchas.md", "guard-design.md"),
    }
    for directory, names in files.items():
        for name in names:
            write(tmp, f"{directory}/{name}", f"# {name}\n")
    git(tmp, "add", "-A")
    expect("case_the_two_named_candidates_refused_by_name", tmp, refuse=True, must_name=NAMED_CANDIDATES)


def case_marker_without_the_declaration_refused(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "_quarantine/mislabeled/SKILL.md", "# mislabeled\n")
    write(tmp, f"_quarantine/mislabeled/{MARKER}", "# Landing\n\nintentional-landing: true\n")
    git(tmp, "add", "--", "_quarantine/mislabeled")
    expect("case_marker_without_the_declaration_refused", tmp, refuse=True, must_name=("_quarantine/mislabeled",))


def case_unstaged_marker_does_not_count(tmp: Path) -> None:
    make_repo(tmp)
    write(tmp, "_quarantine/half-staged/SKILL.md", "# half staged\n")
    write(tmp, f"_quarantine/half-staged/{MARKER}", DECLARATION)
    git(tmp, "add", "--", "_quarantine/half-staged/SKILL.md")
    expect("case_unstaged_marker_does_not_count", tmp, refuse=True, must_name=("_quarantine/half-staged",))


def case_empty_index_passes_with_a_note(tmp: Path) -> None:
    case = "case_empty_index_passes_with_a_note"
    make_repo(tmp)
    result = run(tmp)
    if result.returncode != 0 or "nothing staged" not in result.stdout:
        fail(case, f"expected a pass with a note on an empty index:\n{result.stdout}{result.stderr}")
        return
    print(f"  ok   {case}")


def main() -> None:
    cases = (
        case_new_candidate_skill_md_refused,
        case_edit_inside_tracked_candidate_passes,
        case_new_file_under_skills_passes,
        case_declared_landing_passes,
        case_partial_candidate_without_skill_md_refused,
        case_the_two_named_candidates_refused_by_name,
        case_marker_without_the_declaration_refused,
        case_unstaged_marker_does_not_count,
        case_empty_index_passes_with_a_note,
    )
    for case in cases:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: quarantine-landing guard verified across {len(cases)} temporary repositories; "
        "the five #249 fixtures refuse and pass as listed, the two named candidates are "
        f"refused by name, and only a STAGED {MARKER} with the declaration on line 1 counts."
    )


if __name__ == "__main__":
    main()
