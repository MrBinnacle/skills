#!/usr/bin/env python3
"""Suite for validate_path_residue.py.

WHAT THIS SUITE HAS TO PROVE

    A hook that scans paths but matches nothing looks identical to a hook that
    works (#243). So the load-bearing cases are POISON: a file whose CONTENTS are
    clean and whose NAME carries a residue term, in each separator form the
    ticket names - underscore, hyphen, dot - and in a directory name as well as a
    filename. Each must turn the checker red, by the hook id that owns the term.

    The clean case proves the checker can pass, and the live-tree case is the
    backward sweep #243 asks for, run every time.

    The last case reads `.pre-commit-config.yaml` and asserts every residue hook
    there has a row in the script's term list. The two lists are duplicated on
    purpose (see the checker's docstring); this is what catches them drifting.

Every case builds a real temporary git repository and calls the real
entrypoint with `--root`. No poison fixture is committed: a residue-named file
in this tree would sit inside the guarded set and turn the real run red.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts" / "validate_path_residue.py"
YAML = REPO_ROOT / ".pre-commit-config.yaml"

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


def make_repo(root: Path, paths: list[str]) -> None:
    """A git repo whose index holds `paths`, every file with clean contents."""
    git(root, "init", "-q")
    for rel in paths:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("clean contents, no residue term here\n", encoding="utf-8")
    git(root, "add", "--", *paths)


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def expect_refusal(case: str, root: Path, path: str, hook_id: str) -> None:
    result = run(root)
    if result.returncode == 0:
        fail(case, f"accepted a tree whose path {path!r} carries a residue term")
        return
    if path not in result.stdout or hook_id not in result.stdout:
        fail(case, f"refused, but did not name {path!r} under {hook_id}:\n{result.stdout}")
        return
    print(f"  ok   {case}")


def case_clean_tree_passes(tmp: Path) -> None:
    case = "case_clean_tree_passes"
    make_repo(tmp, ["README.md", "skills/engineering/a-card/SKILL.md", "docs/notes.md"])
    result = run(tmp)
    if result.returncode != 0 or not result.stdout.startswith("PASS:"):
        fail(case, f"clean tree refused:\n{result.stdout}{result.stderr}")
        return
    print(f"  ok   {case}")


def case_underscore_form_in_filename_refused(tmp: Path) -> None:
    path = "docs/FIELD-REPORT-workspace_lint.md"
    make_repo(tmp, ["README.md", path])
    expect_refusal("case_underscore_form_in_filename_refused", tmp, path, "residue-private-linter-repo")


def case_hyphen_form_in_filename_refused(tmp: Path) -> None:
    # The exact shape #243 found: the content pattern is underscore-only, the
    # filename used a hyphen, and nothing in the repository caught it.
    path = "docs/FIELD-REPORT-2026-08-17-workspace-lint.md"
    make_repo(tmp, ["README.md", path])
    expect_refusal("case_hyphen_form_in_filename_refused", tmp, path, "residue-private-linter-repo")


def case_dot_form_in_filename_refused(tmp: Path) -> None:
    path = "docs/workspace.lint.md"
    make_repo(tmp, ["README.md", path])
    expect_refusal("case_dot_form_in_filename_refused", tmp, path, "residue-private-linter-repo")


def case_term_in_directory_name_refused(tmp: Path) -> None:
    path = "skills/skills-research/notes.md"
    make_repo(tmp, ["README.md", path])
    expect_refusal("case_term_in_directory_name_refused", tmp, path, "residue-research-dir")


def case_uppercase_form_refused(tmp: Path) -> None:
    path = "docs/YouWontDoIt-notes.md"
    make_repo(tmp, ["README.md", path])
    expect_refusal("case_uppercase_form_refused", tmp, path, "residue-private-repo-dir")


def case_every_content_term_has_a_path_form(tmp: Path) -> None:
    """One poison path per hook id, so no term in the list is decorative."""
    case = "case_every_content_term_has_a_path_form"
    samples = {
        "residue-writ": "docs/Writ-notes.md",
        "residue-sec-id": "docs/SEC-42-audit.md",
        "residue-wi-id": "docs/WI-7.md",
        "residue-research-dir": "docs/skills_research.md",
        "residue-private-repo-dir": "docs/youwontdoit.md",
        "residue-private-repo-link": "docs/MrBinnacle-writ.md",
        "residue-private-linter-repo": "docs/workspace-lint.md",
    }
    make_repo(tmp, ["README.md", *samples.values()])
    result = run(tmp)
    if result.returncode == 0:
        fail(case, "accepted a tree carrying every residue term in a path")
        return
    missing = [
        hook_id
        for hook_id, path in samples.items()
        if not re.search(re.escape(path) + r"\s+->\s+" + re.escape(hook_id), result.stdout)
    ]
    if missing:
        fail(case, f"hook id(s) never fired on their own sample: {missing}\n{result.stdout}")
        return
    print(f"  ok   {case}")


def case_word_edge_does_not_overreach(tmp: Path) -> None:
    """`written` and `security` are ordinary words; only whole tokens count."""
    case = "case_word_edge_does_not_overreach"
    make_repo(tmp, ["README.md", "docs/written-record.md", "docs/security-review.md", "docs/rewind.md"])
    result = run(tmp)
    if result.returncode != 0:
        fail(case, f"refused ordinary words:\n{result.stdout}")
        return
    print(f"  ok   {case}")


def case_every_yaml_residue_hook_has_a_path_term() -> None:
    case = "case_every_yaml_residue_hook_has_a_path_term"
    sys.path.insert(0, str(CHECKER.parent))
    import validate_path_residue  # noqa: E402  (imported after sys.path edit)

    # Only the pygrep hooks carry a content pattern; the residue-in-paths hook
    # itself is `language: system` and is the consumer of this list, not a term.
    yaml_ids = set(
        re.findall(
            r"^\s+- id: (residue-[a-z-]+)\n\s+name: .*\n\s+language: pygrep\s*$",
            YAML.read_text(encoding="utf-8"),
            re.M,
        )
    )
    script_ids = {hook_id for hook_id, _ in validate_path_residue.PATH_TERMS}
    if not yaml_ids:
        fail(case, "found no residue-* hook ids in .pre-commit-config.yaml - the parse is blind")
        return
    if yaml_ids != script_ids:
        fail(case, f"yaml hooks {sorted(yaml_ids)} != script terms {sorted(script_ids)}")
        return
    print(f"  ok   {case} ({len(yaml_ids)} terms)")


def case_live_tree_passes() -> None:
    """The backward sweep #243 asks for, run on every suite invocation."""
    case = "case_live_tree_passes"
    result = run(REPO_ROOT)
    if result.returncode != 0:
        fail(case, f"the live tree carries a residue term in a path:\n{result.stdout}")
        return
    print(f"  ok   {case}: {result.stdout.strip()}")


def main() -> None:
    in_tempdir = (
        case_clean_tree_passes,
        case_underscore_form_in_filename_refused,
        case_hyphen_form_in_filename_refused,
        case_dot_form_in_filename_refused,
        case_term_in_directory_name_refused,
        case_uppercase_form_refused,
        case_every_content_term_has_a_path_form,
        case_word_edge_does_not_overreach,
    )
    for case in in_tempdir:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))
    case_every_yaml_residue_hook_has_a_path_term()
    case_live_tree_passes()

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: path-residue checker verified across {len(in_tempdir)} temporary repositories "
        "plus the live tree; every separator form and every term is proven by a "
        "clean-content poison path, and the yaml and script term lists agree."
    )


if __name__ == "__main__":
    main()
