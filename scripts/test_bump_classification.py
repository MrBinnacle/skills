#!/usr/bin/env python3
"""Controls for release_gate.py G10: changeset bump type vs the declared surface.

ADR 0003 (docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md) settled
what this check encodes:

    Decision. A card's name is part of the declared surface. The card set is not.
    Renaming a card is a major change. Admitting or retiring one remains a minor
    change.

ADR 0002 prices corrections within a card as a patch and states that the card
set is outside the declared surface. A changeset declares its own bump type and
nothing used to check that declaration against the diff. A wrong bump spends the
wrong version number permanently (ADR 0002), so the gate must block.

Each control plants one shape of the defect into a temporary git tree and runs
the SHIPPED gate as a subprocess -- never module internals -- and requires the
refusal to name G10 and the specific fault. Asserting only a non-zero exit is
how a control passes for the wrong reason.

The inversion control is the one that changed under ADR 0003: a rename declared
major PASSES and the same rename declared minor is REFUSED. A control that only
tested the refusing direction would also pass under the superseded rule that
required minor.

Run: python scripts/test_bump_classification.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "scripts" / "release_gate.py"

FAILURES: list[str] = []

SKILLS_BUCKET = "engineering"
BASE_VERSION = "1.2.0"

# Real ADR 0003 decision sentence, including the line break the file carries.
ADR_0003_TEMPLATE = """# A card's name is part of the declared surface

Status: accepted, 2026-09-08.

**Decision. A card's name is part of the declared surface. The card set is not. Renaming a card
is a {rename} change. Admitting or retiring one remains a {admit_retire} change.**
"""

ADR_0002_TEMPLATE = """# A release is a delivery event

Status: accepted, 2026-08-24.

**The declared surface is the install path and the card format. The card set is not part of
it.** Adding or retiring a card is a {admit_retire} change. Changing the install path, or the
on-disk shape of a card, is a major change. Corrections within a card are a {patch}.
"""


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(root: Path, *args: str) -> None:
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }
    )
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        env=env,
    )


def package_json(version: str) -> str:
    return json.dumps({"name": "mrbinnacle-skills", "version": version}, indent=2) + "\n"


def changelog_md(version: str) -> str:
    return f"# Changelog\n\nAll notable changes.\n\n## v{version} - 2026-08-10\n\nShipped.\n"


def changeset_md(level: str | None) -> str:
    """A changeset the way changesets writes them. None = empty (no bump)."""
    if level is None:
        return "---\n---\n\nNo release.\n"
    return f'---\n"mrbinnacle-skills": {level}\n---\n\nA described change.\n'


def skill_card(root: Path, name: str) -> Path:
    folder = root / "skills" / SKILLS_BUCKET / name
    write(
        folder / "SKILL.md",
        f"---\nname: {name}\ndescription: fixture card\n---\n\n# {name}\n",
    )
    return folder


def plant_adrs(
    root: Path,
    *,
    rename: str = "major",
    admit_retire: str = "minor",
    patch: str = "patch",
) -> None:
    write(
        root / "docs" / "adr" / "0003-a-cards-name-is-part-of-the-declared-surface.md",
        ADR_0003_TEMPLATE.format(rename=rename, admit_retire=admit_retire),
    )
    write(
        root / "docs" / "adr" / "0002-a-release-is-a-delivery-event.md",
        ADR_0002_TEMPLATE.format(admit_retire=admit_retire, patch=patch),
    )


def manifest_lockstep(root: Path, cards: list[str], version: str) -> None:
    """Marketplace + bucket plugin.json naming exactly `cards`, version in lockstep."""
    source = f"./skills/{SKILLS_BUCKET}"
    write(
        root / ".claude-plugin" / "marketplace.json",
        json.dumps(
            {
                "name": "fixture-skills",
                "owner": {"name": "fixture", "url": "https://example.invalid"},
                "plugins": [
                    {
                        "name": "fixture-engineering",
                        "source": source,
                        "description": "fixture",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / source / ".claude-plugin" / "plugin.json",
        json.dumps(
            {
                "name": "fixture-engineering",
                "version": version,
                "skills": [f"./{c}" for c in cards],
            },
            indent=2,
        )
        + "\n",
    )


def make_tree(
    tmp: Path,
    *,
    declared: str | None = "patch",
    branch_change: str = "none",
    adr: str = "real",
    base_version: str = BASE_VERSION,
    head_version: str | None = None,
    release: bool = False,
) -> Path:
    """A git tree whose branch diff and pending changeset the gate can classify.

    branch_change:
      none         - only a changeset is added on the branch
      rename       - skills/engineering/old-card -> new-card
      add_card     - a new card directory appears under skills/engineering/
      remove_card  - skills/engineering/old-card is deleted
      scripts_only - a file outside skills/*/*/ changes
      modify_card  - a file inside an existing card changes (no rename/add)

    adr:
      real             - ADR 0003 text as shipped (rename=major, admit=minor)
      rename_is_patch  - ADR 0003 text rewritten so rename prices as patch
      missing          - no docs/adr/ files

    release=True sets head_version (default minor bump) so the tree is a release
    ref, and leaves .changeset/ empty so G3 is not the fault under test.
    """
    root = tmp / "repo"
    head = head_version or (None if not release else "1.3.0")

    # Base commit always carries base_version. Head-version files are written
    # only on the candidate branch, so the release detector sees a real delta.
    write(root / "package.json", package_json(base_version))
    write(root / "CHANGELOG.md", changelog_md(base_version))

    base_cards = ["old-card"]

    if adr == "missing":
        pass
    elif adr == "rename_is_patch":
        plant_adrs(root, rename="patch", admit_retire="minor", patch="patch")
    else:
        plant_adrs(root, rename="major", admit_retire="minor", patch="patch")

    for name in base_cards:
        skill_card(root, name)

    def cards_after_change() -> list[str]:
        cards = list(base_cards)
        if branch_change == "add_card":
            cards.append("new-card")
        elif branch_change == "remove_card":
            cards = []
        elif branch_change == "rename":
            cards = ["new-card"]
        return cards

    # Base manifests name the base cards at the base version.
    manifest_lockstep(root, base_cards, base_version)

    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    git(root, "branch", "-M", "main")
    git(root, "checkout", "-q", "-b", "candidate")

    if branch_change == "rename":
        git(root, "mv", f"skills/{SKILLS_BUCKET}/old-card", f"skills/{SKILLS_BUCKET}/new-card")
        write(
            root / "skills" / SKILLS_BUCKET / "new-card" / "SKILL.md",
            "---\nname: new-card\ndescription: fixture card\n---\n\n# new-card\n",
        )
    elif branch_change == "add_card":
        skill_card(root, "new-card")
    elif branch_change == "remove_card":
        git(root, "rm", "-r", "-q", f"skills/{SKILLS_BUCKET}/old-card")
    elif branch_change == "scripts_only":
        write(root / "scripts" / "only-outside-surface.py", "print('hello')\n")
    elif branch_change == "modify_card":
        write(
            root / "skills" / SKILLS_BUCKET / "old-card" / "gotchas.md",
            "# gotchas\n\nA dated note.\n",
        )

    if head is not None:
        # Candidate-only: version bump, lockstep manifests, dated changelog.
        manifest_lockstep(root, cards_after_change(), head)
        write(root / "package.json", package_json(head))
        write(root / "CHANGELOG.md", changelog_md(head))
    else:
        manifest_lockstep(root, cards_after_change(), base_version)

    if not release:
        write(root / ".changeset" / "zzz-classify.md", changeset_md(declared))
    else:
        # Consumed plan: no pending files, so G3 stays silent and G10 alone
        # answers whether the version delta matches the release diff.
        changeset_dir = root / ".changeset"
        if changeset_dir.is_dir():
            shutil.rmtree(changeset_dir)

    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "candidate")
    return root


def expect_pass(case: str, root: Path, *args: str) -> None:
    result = run_gate("--root", str(root), *args)
    if result.returncode != 0:
        check(case, False, f"ACCEPTED nothing but refused\n{result.stdout}{result.stderr}")
        return
    check(case, "RELEASE GATE: PASS" in result.stdout, result.stdout)


def expect_g10_refusal(case: str, root: Path, *needles: str, release: bool = False) -> None:
    args = ["--root", str(root)]
    if release:
        args = ["--release", *args]
    result = run_gate(*args)
    if result.returncode == 0:
        check(case, False, f"ACCEPTED the planted defect\n{result.stdout}{result.stderr}")
        return
    output = result.stdout + result.stderr
    if "G10:" not in output:
        check(case, False, f"refused without naming G10\n{output}")
        return
    missing = [n for n in needles if n not in output]
    if missing:
        check(case, False, f"refusal missed {missing!r}\n{output}")
        return
    check(case, True)


# --------------------------------------------------------------------- controls


def case_positive_correct_classification_is_silent(tmp: Path) -> None:
    """A correctly classified changeset must not turn the gate red.

    Scripts-only change declared patch: nothing under skills/*/*/ moves, so the
    declared surface is untouched and patch is the price ADR 0002 gives work
    that reaches no card."""
    root = make_tree(tmp, declared="patch", branch_change="scripts_only")
    expect_pass("a correctly classified changeset stays silent", root)


def case_positive_rename_major_passes(tmp: Path) -> None:
    """Inversion pin, passing half: ADR 0003 prices a rename as major."""
    root = make_tree(tmp, declared="major", branch_change="rename")
    expect_pass("a rename declared major PASSES under ADR 0003", root)


def case_positive_add_minor_passes(tmp: Path) -> None:
    """Admitting a card is minor under ADR 0003; minor must pass."""
    root = make_tree(tmp, declared="minor", branch_change="add_card")
    expect_pass("a card admission declared minor PASSES", root)


def case_case1_rename_declared_patch_is_refused(tmp: Path) -> None:
    """Case 1, the refusing half of the superseded rule: rename + patch."""
    root = make_tree(tmp, declared="patch", branch_change="rename")
    expect_g10_refusal(
        "case 1: a rename declared patch is refused",
        root,
        "G10:",
        "rename",
        "major",
    )


def case_case1_rename_declared_minor_is_refused(tmp: Path) -> None:
    """Inversion pin, refusing half: rename + minor is REFUSED (was required
    before ADR 0003; is now wrong)."""
    root = make_tree(tmp, declared="minor", branch_change="rename")
    expect_g10_refusal(
        "case 1 / inversion: a rename declared minor is REFUSED",
        root,
        "G10:",
        "rename",
        "major",
    )


def case_case2_add_declared_patch_is_refused(tmp: Path) -> None:
    """Case 2: admitting a card declared patch is refused."""
    root = make_tree(tmp, declared="patch", branch_change="add_card")
    expect_g10_refusal(
        "case 2: a card admission declared patch is refused",
        root,
        "G10:",
        "add",
        "minor",
    )


def case_case2_remove_declared_patch_is_refused(tmp: Path) -> None:
    """Case 2, the other direction: retiring a card declared patch is refused."""
    root = make_tree(tmp, declared="patch", branch_change="remove_card")
    expect_g10_refusal(
        "case 2: a card retirement declared patch is refused",
        root,
        "G10:",
        "retire",
        "minor",
    )


def case_case3_no_surface_declared_minor_is_refused(tmp: Path) -> None:
    """Case 3: nothing under skills/*/*/ changes, yet the changeset declares minor."""
    root = make_tree(tmp, declared="minor", branch_change="scripts_only")
    expect_g10_refusal(
        "case 3: no declared-surface change declared minor is refused",
        root,
        "G10:",
        "skills/*/*/",
        "minor",
    )


def case_case3_no_surface_declared_major_is_refused(tmp: Path) -> None:
    """Case 3, the other over-classification."""
    root = make_tree(tmp, declared="major", branch_change="scripts_only")
    expect_g10_refusal(
        "case 3: no declared-surface change declared major is refused",
        root,
        "G10:",
        "skills/*/*/",
        "major",
    )


def case_higher_classification_governs_rename_plus_add(tmp: Path) -> None:
    """A rename and an addition in one changeset resolve to major.

    The fixture renames old-card and adds new-card on the same branch, with one
    changeset declaring patch. The higher class (major, from the rename)
    governs, so patch is refused."""
    root = tmp / "repo"
    write(root / "package.json", package_json(BASE_VERSION))
    write(root / "CHANGELOG.md", changelog_md(BASE_VERSION))
    plant_adrs(root)
    skill_card(root, "old-card")
    manifest_lockstep(root, ["old-card"], BASE_VERSION)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    git(root, "branch", "-M", "main")
    git(root, "checkout", "-q", "-b", "candidate")
    git(root, "mv", f"skills/{SKILLS_BUCKET}/old-card", f"skills/{SKILLS_BUCKET}/new-card")
    write(
        root / "skills" / SKILLS_BUCKET / "new-card" / "SKILL.md",
        "---\nname: new-card\ndescription: fixture card\n---\n\n# new-card\n",
    )
    skill_card(root, "added-card")
    manifest_lockstep(root, ["new-card", "added-card"], BASE_VERSION)
    write(root / ".changeset" / "zzz-classify.md", changeset_md("patch"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "candidate")
    expect_g10_refusal(
        "rename + add in one changeset resolves to major (patch refused)",
        root,
        "G10:",
        "major",
    )


def case_case4_release_delta_under_required_is_refused(tmp: Path) -> None:
    """Case 4: version bumped minor while the release diff only edits scripts.

    The release is real (version changed, manifests in lockstep, no pending
    changesets) but the tree's declared surface did not move, so a minor delta
    spends the wrong number."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="scripts_only",
        head_version="1.3.0",
        release=True,
    )
    expect_g10_refusal(
        "case 4: a minor version delta over a scripts-only release is refused",
        root,
        "G10:",
        "1.2.0",
        "1.3.0",
        release=True,
    )


def case_case4_release_delta_matches_rename_is_silent(tmp: Path) -> None:
    """Case 4 positive half: a major delta over a rename release is correct."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="rename",
        head_version="2.0.0",
        release=True,
    )
    expect_pass(
        "case 4: a major version delta over a rename release stays silent",
        root,
        "--release",
    )


def case_ard_text_is_read_not_hardcoded(tmp: Path) -> None:
    """The classification must come from the ADR on disk, not a constant.

    This fixture rewrites ADR 0003 so a rename prices as patch, then plants a
    rename declared patch. Under a hardcoded major rule the gate would refuse;
    because the checker reads the repository, it passes."""
    root = make_tree(
        tmp,
        declared="patch",
        branch_change="rename",
        adr="rename_is_patch",
    )
    expect_pass(
        "ADR text is read, not hardcoded: rename-as-patch ADR accepts rename+patch",
        root,
    )


def case_missing_ard_fails_closed_when_classification_needed(tmp: Path) -> None:
    """Without ADR text the checker cannot classify, so it must refuse."""
    root = make_tree(
        tmp,
        declared="major",
        branch_change="rename",
        adr="missing",
    )
    result = run_gate("--root", str(root))
    output = result.stdout + result.stderr
    check(
        "a missing ADR fails closed when classification is needed",
        result.returncode != 0 and "G10:" in output and "ADR" in output,
        output,
    )


def case_empty_changeset_is_not_a_classification_fault(tmp: Path) -> None:
    """`changeset add --empty` declares no bump; G10 must not invent one."""
    root = make_tree(tmp, declared=None, branch_change="scripts_only")
    expect_pass("an empty changeset is not refused by G10", root)


def case_live_tree_gate_stays_green(tmp: Path) -> None:
    """The shipped repository, as a maintainer runs it with no arguments."""
    result = run_gate("--root", str(REPO_ROOT))
    check(
        "the live repository still passes the gate after G10",
        result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
        result.stdout + result.stderr,
    )


def _workflow_job(name: str) -> str:
    workflow = REPO_ROOT / ".github" / "workflows" / "tests.yml"
    text = workflow.read_text(encoding="utf-8")
    match = __import__("re").search(
        rf"(?ms)^  {name}:\n(.*?)(?=^  \S|\Z)", text
    )
    return match.group(1) if match else ""


def _named_step(job: str, step_name: str) -> str:
    match = __import__("re").search(
        rf"(?ms)^      - name: {step_name}\n(.*?)(?=^      - name: |\Z)", job
    )
    return match.group(1) if match else ""


def case_ci_runs_the_bump_classification_suite(tmp: Path) -> None:
    """The controls in this file must run in CI, not only on a maintainer laptop."""
    job = _workflow_job("release-gate")
    step = _named_step(job, "Bump-classification suite")
    check(
        "CI carries the bump-classification suite step",
        bool(step),
        "no 'Bump-classification suite' step under the release-gate job",
    )
    check(
        "the suite step runs this file and requires its PASS line",
        "python scripts/test_bump_classification.py" in step and "^PASS:" in step,
        step,
    )


def case_ci_carries_the_inversion_poison_control(tmp: Path) -> None:
    """The inversion is the criterion ADR 0003 changed; CI must pin both halves."""
    job = _workflow_job("release-gate")
    step = _named_step(
        job,
        "Poison control - a card rename must be refused unless declared major",
    )
    check(
        "CI carries the rename/inversion poison control",
        bool(step),
        "no rename poison control under the release-gate job",
    )
    check(
        "the control plants a rename declared minor and requires G10",
        "minor" in step and "G10:" in step and "rename" in step,
        step,
    )
    check(
        "the control also requires the major half to PASS",
        "major" in step and "RELEASE GATE: PASS" in step,
        step,
    )


def case_ci_carries_case1_to_case4_poison_controls(tmp: Path) -> None:
    """Each refusable class must have a CI control that plants it."""
    job = _workflow_job("release-gate")
    for step_name, needles in (
        (
            "Poison control - a rename declared below major must be rejected",
            ("G10:", "rename", "major"),
        ),
        (
            "Poison control - a card admission declared patch must be rejected",
            ("G10:", "add", "minor"),
        ),
        (
            "Poison control - no surface change declaring minor or major must be rejected",
            ("G10:", "skills/", "minor"),
        ),
        (
            "Poison control - a release version delta that overstates the surface must be rejected",
            ("G10:", "1.2.0", "1.3.0"),
        ),
    ):
        step = _named_step(job, step_name)
        check(
            f"CI carries the control {step_name!r}",
            bool(step),
            "no such step under the release-gate job",
        )
        missing = [n for n in needles if n not in step]
        check(
            f"the control {step_name!r} plants the defect and names G10",
            not missing,
            f"missing {missing!r} in step" if missing else "",
        )


CASES = (
    case_positive_correct_classification_is_silent,
    case_positive_rename_major_passes,
    case_positive_add_minor_passes,
    case_case1_rename_declared_patch_is_refused,
    case_case1_rename_declared_minor_is_refused,
    case_case2_add_declared_patch_is_refused,
    case_case2_remove_declared_patch_is_refused,
    case_case3_no_surface_declared_minor_is_refused,
    case_case3_no_surface_declared_major_is_refused,
    case_higher_classification_governs_rename_plus_add,
    case_case4_release_delta_under_required_is_refused,
    case_case4_release_delta_matches_rename_is_silent,
    case_ard_text_is_read_not_hardcoded,
    case_missing_ard_fails_closed_when_classification_needed,
    case_empty_changeset_is_not_a_classification_fault,
    case_live_tree_gate_stays_green,
    case_ci_runs_the_bump_classification_suite,
    case_ci_carries_the_inversion_poison_control,
    case_ci_carries_case1_to_case4_poison_controls,
)


def main() -> int:
    print(f"bump-classification controls ({len(CASES)} cases)")
    for case in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))
    if FAILURES:
        print(f"\nFAIL: {len(FAILURES)} control(s) did not hold: {', '.join(FAILURES)}")
        return 1
    print(
        f"\nPASS: {len(CASES)} controls verified; each planted defect is refused "
        "by G10, the inversion is pinned, and the ADR text on disk drives classification"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
