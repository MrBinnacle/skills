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

Cases 1-3 judge only the changesets THIS BRANCH adds (new .changeset/*.md in
merge-base..HEAD), never every pending file on disk. Case 4, at release,
compares the version delta against the changesets the release CONSUMES --
read at the merge-base, because `changeset version` deletes them at HEAD.

When git is absent from PATH, G10 catches GitUnavailableError and refuses in
its own words when a declared bump is pending on disk (#347 / B1). Without a
pending bump G10 is silent; the other git-dependent checks still refuse.

Each control plants one shape of the defect into a temporary git tree and runs
the SHIPPED gate as a subprocess -- never module internals -- and requires the
refusal to name G10 and the specific fault. Asserting only a non-zero exit is
how a control passes for the wrong reason.

The inversion control is the one that changed under ADR 0003: a rename declared
major PASSES and the same rename declared minor is REFUSED. A control that only
tested the refusing direction would also pass under the superseded rule that
required minor.

R5-2: `changeset_declared_bumps` must refuse, not skip, a frontmatter line it
cannot parse. A named control per unparseable form kills the mutant that
restores the skip. Two forms ship: a `!!str`-tagged bump value and an unquoted
multi-word bump value. Either form used to parse to `{}`, so G10 had nothing to
classify and the gate stayed green over a changeset whose declared bump was
unreadable -- the root cause behind the R5-1 regex fix.

Run: python scripts/test_bump_classification.py
"""
from __future__ import annotations

import json
import os
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


def run_gate_env(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    """Run the shipped gate under a controlled environment (e.g. git absent)."""
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
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
    consumed: str | list[str] | None = None,
) -> Path:
    """A git tree whose branch diff and pending changeset the gate can classify.

    branch_change:
      none         - only a changeset is added on the branch
      rename       - skills/engineering/old-card -> new-card
      add_card     - a new card directory appears under skills/engineering/
      remove_card  - skills/engineering/old-card is deleted
      scripts_only - a file outside skills/*/*/ changes
      non_card     - a file under skills/*/*/ but outside any card changes
      modify_card  - a file inside an existing card changes (no rename/add)

    adr:
      real             - ADR 0003 text as shipped (rename=major, admit=minor)
      rename_is_patch  - ADR 0003 text rewritten so rename prices as patch
      missing          - no docs/adr/ files

    release=True sets head_version (default minor bump) so the tree is a release
    ref. `consumed` names the bump(s) the release plan held at the base commit;
    those .changeset files are deleted on the release commit, the way
    `changeset version` consumes them. G3 stays silent because HEAD holds no
    pending file.

    Cases 1-3 see only changesets this branch ADDS (written on the candidate
    after the base commit). A consumed plan is planted BEFORE the base commit
    so the release diff carries the deletions.
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

    # A release plan lives at the base commit: `changeset version` consumes
    # what main already held, then deletes the files in the release PR.
    if release and consumed is not None:
        levels = [consumed] if isinstance(consumed, str) else list(consumed)
        for index, level in enumerate(levels):
            write(root / ".changeset" / f"zzz-consumed-{index}.md", changeset_md(level))

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
    elif branch_change == "non_card":
        write(root / "skills" / SKILLS_BUCKET / "notes" / "note.md", "Not a card.\n")
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
        # Consumed plan: no pending files at HEAD, so G3 stays silent and G10
        # case 4 alone answers whether the version delta matches the plan the
        # release consumed at the merge-base.
        changeset_dir = root / ".changeset"
        if changeset_dir.is_dir():
            for path in changeset_dir.glob("*.md"):
                if path.name != "README.md":
                    path.unlink()

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


def init_base_repo(root: Path, *, base_version: str = BASE_VERSION) -> None:
    """A conforming main tip: one card, lockstep manifests, ADRs, no changesets."""
    write(root / "package.json", package_json(base_version))
    write(root / "CHANGELOG.md", changelog_md(base_version))
    plant_adrs(root)
    skill_card(root, "old-card")
    manifest_lockstep(root, ["old-card"], base_version)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    git(root, "branch", "-M", "main")


def set_origin_main(root: Path) -> None:
    """Point refs/remotes/origin/main at HEAD -- the state after a push to main."""
    git(root, "update-ref", "refs/remotes/origin/main", "HEAD")


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


def case_case2_add_declared_quoted_patch_is_refused(tmp: Path) -> None:
    """G10 must read a quoted YAML bump scalar as well as an unquoted one."""
    root = make_tree(tmp, declared='"patch"', branch_change="add_card")
    expect_g10_refusal(
        "case 2: a card admission declared quoted patch is refused",
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


def case_case3_commented_major_is_refused(tmp: Path) -> None:
    """A YAML comment cannot hide a declared bump from G10."""
    root = make_tree(
        tmp,
        declared="major # a valid YAML comment after the bump",
        branch_change="scripts_only",
    )
    expect_g10_refusal(
        "case 3: a commented major declaration is refused",
        root,
        "G10:",
        "skills/*/*/",
        "major",
    )


def case_case3_non_card_directory_declared_minor_is_refused(tmp: Path) -> None:
    """A directory below a bucket is not a card unless it carries SKILL.md."""
    root = make_tree(tmp, declared="minor", branch_change="non_card")
    expect_g10_refusal(
        "case 3: a non-card directory declared minor is refused",
        root,
        "G10:",
        "no file under skills/*/*/",
        "minor",
    )


def case_unparseable_yaml_tag_bump_is_refused(tmp: Path) -> None:
    """R5-2: a `!!str`-tagged bump line must be refused, never skipped.

    The R5-1 regex closed `major # comment` hiding a declared bump; the root
    cause behind that fix is a frontmatter line the parser does not recognise
    at all. Before R5-2 this fixture PASSED -- the parser skipped the line,
    returned {}, and G10 had nothing to classify. The skip mutant (the
    pre-R5-2 `if match: ...` with no else) is killed by this control's name:
    `case_unparseable_yaml_tag_bump_is_refused`. Single-reason: the tree is
    otherwise conforming, so G10 is the only fault.
    """
    root = make_tree(tmp, declared="!!str major", branch_change="scripts_only")
    expect_g10_refusal(
        "R5-2: a !!str-tagged bump line is refused, not skipped",
        root,
        "G10:",
        "zzz-classify.md",
        "!!str major",
    )
    result = run_gate("--root", str(root))
    output = result.stdout + result.stderr
    check(
        "R5-2: the !!str refusal is single-reason",
        "1 stale surface(s)" in output and output.count("G10:") == 1,
        output,
    )


def case_unparseable_multiword_bump_is_refused(tmp: Path) -> None:
    """R5-2: an unquoted multi-word bump value must be refused, never skipped.

    `major release` is a second YAML form the R5-1 regex misses. Named control
    `case_unparseable_multiword_bump_is_refused` kills the skip mutant for this
    form. Single-reason, same shape as the !!str control.
    """
    root = make_tree(tmp, declared="major release", branch_change="scripts_only")
    expect_g10_refusal(
        "R5-2: an unquoted multi-word bump line is refused, not skipped",
        root,
        "G10:",
        "zzz-classify.md",
        "major release",
    )
    result = run_gate("--root", str(root))
    output = result.stdout + result.stderr
    check(
        "R5-2: the multi-word refusal is single-reason",
        "1 stale surface(s)" in output and output.count("G10:") == 1,
        output,
    )


def case_higher_classification_governs_rename_plus_add(tmp: Path) -> None:
    """A rename and an addition in one changeset resolve to major.

    The fixture renames old-card and adds new-card on the same branch, with one
    changeset declaring MINOR -- the price an addition alone would cost. The
    higher class (major, from the rename) governs, so minor is refused. A
    mutant that took the lower price, or that priced only the addition, would
    accept this fixture; declaring minor is what kills it.
    """
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
    write(root / ".changeset" / "zzz-classify.md", changeset_md("minor"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "candidate")
    expect_g10_refusal(
        "rename + add in one changeset resolves to major (minor refused)",
        root,
        "G10:",
        "major",
    )


def case_case4_consumed_major_with_major_delta_passes(tmp: Path) -> None:
    """Case 4 positive half: the version delta matches the consumed plan.

    A release tree shaped like a real roll: the plan at the base commit prices
    major (plus patches), `changeset version` consumed those files, and the
    release PR wrote 2.0.0. The gate must stay silent."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="none",
        base_version="2.0.0",
        head_version="3.0.0",
        release=True,
        consumed=["major", "patch", "patch"],
    )
    expect_pass(
        "case 4: a major delta over a consumed-major plan stays silent",
        root,
        "--release",
    )


def case_case4_consumed_major_with_minor_delta_is_refused(tmp: Path) -> None:
    """Case 4 refuse half: minor written where the consumed plan prices major.

    The tree is the v3.0.0 shape -- same consumed plan, same release PR shape --
    with the version number dialed back to a minor bump. A wrong bump spends
    the wrong number permanently (ADR 0002), so G10 blocks."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="none",
        base_version="2.0.0",
        head_version="2.1.0",
        release=True,
        consumed=["major", "patch", "patch"],
    )
    expect_g10_refusal(
        "case 4: a minor delta over a consumed-major plan is REFUSED",
        root,
        "G10:",
        "2.0.0",
        "2.1.0",
        "major",
        release=True,
    )


def case_case4_consumed_patch_with_minor_delta_is_refused(tmp: Path) -> None:
    """Case 4 prices the plan, not only a lower bound: patch plan, minor written."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="scripts_only",
        base_version="1.2.0",
        head_version="1.3.0",
        release=True,
        consumed="patch",
    )
    expect_g10_refusal(
        "case 4: a minor delta over a consumed-patch plan is REFUSED",
        root,
        "G10:",
        "1.2.0",
        "1.3.0",
        "patch",
        release=True,
    )


def case_case4_consumed_patch_with_no_delta_is_refused(tmp: Path) -> None:
    """A consumed plan cannot pass unchanged as a release version."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="scripts_only",
        base_version="1.2.0",
        head_version="1.2.0",
        release=True,
        consumed="patch",
    )
    expect_g10_refusal(
        "case 4: a consumed patch plan with no version increment is REFUSED",
        root,
        "G10:",
        "1.2.0",
        "1.2.1",
        "patch",
        release=True,
    )


def case_case4_requires_the_exact_changesets_version(tmp: Path) -> None:
    """Matching a field is insufficient when changesets would write another version."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="scripts_only",
        base_version="1.2.0",
        head_version="1.2.9",
        release=True,
        consumed="patch",
    )
    expect_g10_refusal(
        "case 4: a patch plan must produce exactly the next patch version",
        root,
        "G10:",
        "1.2.9",
        "1.2.1",
        "patch",
        release=True,
    )


def case_case4_no_consumed_plan_with_delta_is_refused(tmp: Path) -> None:
    """A version number with no consumed plan behind it has nothing to justify it."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="scripts_only",
        head_version="1.3.0",
        release=True,
        consumed=None,
    )
    expect_g10_refusal(
        "case 4: a version delta with no consumed changeset is REFUSED",
        root,
        "G10:",
        "1.2.0",
        "1.3.0",
        "no changeset consumed",
        release=True,
    )


def case_case4_unchanged_version_with_no_consumed_plan_passes(tmp: Path) -> None:
    """N1: an explicit --release run on a released, clean main must PASS.

    After a release, origin/main == HEAD, package.json still declares the
    released version, and no plan remains to consume. The version is
    unchanged; that is not a release delta. Before the fix G10 refused this
    tree with the false message "release version changed from 1.2.0 to
    1.2.0". A control that only tested the refusing direction could not
    catch that regression (dfd1e45 -> 53a5b3a)."""
    root = tmp / "repo"
    init_base_repo(root)
    set_origin_main(root)
    expect_pass(
        "case 4: --release on an unchanged version with no consumed plan PASSES",
        root,
        "--release",
    )


def case_case4_minor_plan_resets_patch_field(tmp: Path) -> None:
    """R4-F3: a minor plan must reset the patch field.

    Base 1.2.1 with a consumed minor plan: ``changeset version`` writes
    1.3.0, not 1.3.1. The minor-reset mutant at release_gate.py:1065
    returns 1.3.1 (patch left unreset); the pass half dies on that mutant,
    and the refusal half names it by requiring 1.3.0 when 1.3.1 is written.
    Existing case-4 controls use bases whose patch field is already 0
    (1.2.0), so they cannot see this defect.
    """
    correct = make_tree(
        tmp / "correct",
        declared=None,
        branch_change="none",
        base_version="1.2.1",
        head_version="1.3.0",
        release=True,
        consumed="minor",
    )
    expect_pass(
        "R4-F3: minor plan over base 1.2.1 produces 1.3.0 "
        "(kills minor-reset mutant at release_gate.py:1065)",
        correct,
        "--release",
    )
    unreset = make_tree(
        tmp / "unreset",
        declared=None,
        branch_change="none",
        base_version="1.2.1",
        head_version="1.3.1",
        release=True,
        consumed="minor",
    )
    expect_g10_refusal(
        "R4-F3: minor plan over base 1.2.1 refuses unreset 1.3.1 "
        "(kills minor-reset mutant at release_gate.py:1065)",
        unreset,
        "G10:",
        "1.2.1",
        "1.3.1",
        "1.3.0",
        "minor",
        release=True,
    )


def case_case4_major_plan_resets_minor_and_patch(tmp: Path) -> None:
    """R4-F3: a major plan must reset the minor and patch fields.

    Base 2.1.1 with a consumed major plan: ``changeset version`` writes
    3.0.0, not 3.1.1 (nothing reset) and not 3.0.1 (patch left unreset).
    The major-reset mutant at release_gate.py:1063 returns 3.1.1; a
    mutant that resets minor but not patch returns 3.0.1. Existing
    case-4 major controls use base 2.0.0, whose minor and patch fields are
    already 0, so they cannot see either defect.
    """
    correct = make_tree(
        tmp / "correct",
        declared=None,
        branch_change="none",
        base_version="2.1.1",
        head_version="3.0.0",
        release=True,
        consumed="major",
    )
    expect_pass(
        "R4-F3: major plan over base 2.1.1 produces 3.0.0 "
        "(kills major-reset mutant at release_gate.py:1063)",
        correct,
        "--release",
    )
    unreset_both = make_tree(
        tmp / "unreset-both",
        declared=None,
        branch_change="none",
        base_version="2.1.1",
        head_version="3.1.1",
        release=True,
        consumed="major",
    )
    expect_g10_refusal(
        "R4-F3: major plan over base 2.1.1 refuses unreset 3.1.1 "
        "(kills major-reset mutant at release_gate.py:1063)",
        unreset_both,
        "G10:",
        "2.1.1",
        "3.1.1",
        "3.0.0",
        "major",
        release=True,
    )
    unreset_patch = make_tree(
        tmp / "unreset-patch",
        declared=None,
        branch_change="none",
        base_version="2.1.1",
        head_version="3.0.1",
        release=True,
        consumed="major",
    )
    expect_g10_refusal(
        "R4-F3: major plan over base 2.1.1 refuses unreset 3.0.1 "
        "(kills major-reset mutant at release_gate.py:1063)",
        unreset_patch,
        "G10:",
        "2.1.1",
        "3.0.1",
        "3.0.0",
        "major",
        release=True,
    )


def case_b2a_push_to_main_after_admission_passes(tmp: Path) -> None:
    """B2(a): a push to main after an admission merged with minor must PASS.

    The admission's changeset sits on main and declares minor correctly. Once
    the merge lands, origin/main == HEAD and the branch diff is empty. G10
    must not re-judge main's pending file against an empty diff -- that was
    the defect: a correct minor declaration refused as case 3."""
    root = tmp / "repo"
    init_base_repo(root)
    git(root, "checkout", "-q", "-b", "candidate")
    skill_card(root, "new-card")
    manifest_lockstep(root, ["old-card", "new-card"], BASE_VERSION)
    write(root / ".changeset" / "zzz-admit.md", changeset_md("minor"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "admit")
    git(root, "checkout", "-q", "main")
    git(root, "merge", "-q", "--no-ff", "candidate", "-m", "merge admit")
    set_origin_main(root)
    expect_pass(
        "B2(a): push to main after a correctly declared minor admission PASSES",
        root,
    )


def case_b2b_next_scripts_only_pr_passes(tmp: Path) -> None:
    """B2(b): the next scripts-only PR after that admission must PASS.

    main still holds the admission's pending minor changeset. The new PR adds
    only a scripts file and a patch changeset. Cases 1-3 must judge the
    branch-added patch file, not main's leftover minor -- otherwise every
    ordinary PR after an admission goes red."""
    root = tmp / "repo"
    init_base_repo(root)
    git(root, "checkout", "-q", "-b", "candidate")
    skill_card(root, "new-card")
    manifest_lockstep(root, ["old-card", "new-card"], BASE_VERSION)
    write(root / ".changeset" / "zzz-admit.md", changeset_md("minor"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "admit")
    git(root, "checkout", "-q", "main")
    git(root, "merge", "-q", "--no-ff", "candidate", "-m", "merge admit")
    set_origin_main(root)
    git(root, "checkout", "-q", "-b", "scripts-pr")
    write(root / "scripts" / "only-outside-surface.py", "print('hello')\n")
    write(root / ".changeset" / "zzz-scripts.md", changeset_md("patch"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "scripts")
    expect_pass(
        "B2(b): the next scripts-only PR after that admission PASSES",
        root,
    )


def case_b2c_replay_push_to_main_at_316_passes(tmp: Path) -> None:
    """B2(c): a replay of the push to main at #316 (correct major) must PASS.

    #316 added a major changeset and re-shaped packaging, then landed on main.
    After the push, origin/main == HEAD and the branch diff is empty. The
    pending major on disk is correct for work already in history; G10 must
    not refuse it as case 3."""
    root = tmp / "repo"
    init_base_repo(root)
    write(root / ".changeset" / "zzz-older-patch.md", changeset_md("patch"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "older pending")
    git(root, "checkout", "-q", "-b", "candidate")
    # #316 shape: major changeset + bucket plugin.json + a SKILL.md touch.
    write(root / ".changeset" / "plugin-is-its-own-root.md", changeset_md("major"))
    write(
        root / "skills" / SKILLS_BUCKET / ".claude-plugin" / "plugin.json",
        json.dumps(
            {
                "name": "fixture-engineering",
                "version": BASE_VERSION,
                "skills": ["./old-card"],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / "skills" / SKILLS_BUCKET / "old-card" / "SKILL.md",
        "---\nname: old-card\ndescription: fixture card\n---\n\n# old-card\n\ntouched\n",
    )
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "plugin roots")
    git(root, "checkout", "-q", "main")
    git(root, "merge", "-q", "--no-ff", "candidate", "-m", "merge 316")
    set_origin_main(root)
    expect_pass(
        "B2(c): replay of the push to main at #316 (major) PASSES",
        root,
    )


def case_b3_v300_shaped_release_passes(tmp: Path) -> None:
    """B3 positive: a tree shaped like the real v3.0.0 release PASSES.

    The real release (4c00b0e) consumed a major changeset plus several patch
    ones and wrote 2.0.0 -> 3.0.0. This fixture mirrors that shape: consumed
    plan at the base, files deleted at HEAD, version major, changelog dated."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="none",
        base_version="2.0.0",
        head_version="3.0.0",
        release=True,
        consumed=["major", "patch", "patch", "patch"],
    )
    expect_pass(
        "B3: a v3.0.0-shaped release (consumed major, delta major) PASSES",
        root,
        "--release",
    )


def case_b3_v300_shaped_release_minor_delta_refused(tmp: Path) -> None:
    """B3 refuse: the same tree with a minor bump where the plan prices major."""
    root = make_tree(
        tmp,
        declared=None,
        branch_change="none",
        base_version="2.0.0",
        head_version="2.1.0",
        release=True,
        consumed=["major", "patch", "patch", "patch"],
    )
    expect_g10_refusal(
        "B3: the v3.0.0-shaped tree with a minor delta is REFUSED",
        root,
        "G10:",
        "2.0.0",
        "2.1.0",
        "major",
        release=True,
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
    # F1 (S512): half two must recreate `.changeset/` after `git checkout
    # main` removes the empty directory half one left behind. Without this the
    # step dies under `set -e` before the major half runs, and steps 18-23
    # never execute in CI.
    major_half = step.split("Half two")[-1] if "Half two" in step else step
    check(
        "half two recreates .changeset before writing the major changeset",
        'mkdir -p "$tree/.changeset"' in major_half
        and 'zzz-rename.md' in major_half
        and "major" in major_half,
        "half two writes zzz-rename.md without mkdir -p $tree/.changeset "
        "(the empty dir is removed by git checkout main; CI dies under set -e)",
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
            "Poison control - a release version delta that disagrees with the consumed plan",
            ("G10:", "2.0.0", "2.1.0", "major"),
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


def case_ci_carries_unparseable_bump_controls(tmp: Path) -> None:
    """R5-2 needs a named CI control per unparseable form, not only suite cases."""
    job = _workflow_job("release-gate")
    for step_name, needles in (
        (
            "Poison control - a !!str-tagged bump line must be refused",
            ("G10:", "!!str", "zzz-unparseable-tag.md", "1 stale surface(s)"),
        ),
        (
            "Poison control - an unquoted multi-word bump line must be refused",
            ("G10:", "major release", "zzz-unparseable-word.md", "1 stale surface(s)"),
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


def case_ci_carries_b2_and_b3_controls(tmp: Path) -> None:
    """B2 and B3 each need a CI control, not only a suite case."""
    job = _workflow_job("release-gate")
    step_b2 = _named_step(
        job,
        "Poison control - a push to main must not re-judge main's pending changesets",
    )
    check(
        "CI carries the control 'Poison control - a push to main must not re-judge main's pending changesets'",
        bool(step_b2),
        "no such step under the release-gate job",
    )
    for needle in (
        "RELEASE GATE: PASS",
        "316",
        "major",
        "plugin-is-its-own-root.md",
    ):
        check(
            f"the B2 control carries the required assertion {needle!r}",
            needle in step_b2,
            f"missing {needle!r} in B2 step" if needle not in step_b2 else "",
        )
    step_b3 = _named_step(
        job,
        "Poison control - a v3.0.0-shaped release must pass and a minor delta must be refused",
    )
    check(
        "CI carries the control 'Poison control - a v3.0.0-shaped release must pass and a minor delta must be refused'",
        bool(step_b3),
        "no such step under the release-gate job",
    )
    for needle in ("RELEASE GATE: PASS", "G10:", "2.0.0", "2.1.0"):
        check(
            f"the B3 control carries the required assertion {needle!r}",
            needle in step_b3,
            f"missing {needle!r} in B3 step" if needle not in step_b3 else "",
        )


def case_g10_refuses_in_its_own_words_when_git_is_absent(tmp: Path) -> None:
    """B1: when git is not on PATH, G10 refuses in its own words, no traceback.

    Since #347, `_is_git_work_tree` and `_git_ok` raise GitUnavailableError
    when git is missing. G10 must catch that and refuse under its own check
    ID -- naming git and the pending changeset -- rather than dying with a
    FileNotFoundError traceback. The tree carries a declared pending bump on
    disk so G10 has something to refuse; without that file G10 has nothing to
    say and is silent, which is also correct.
    """
    root = make_tree(tmp, declared="minor", branch_change="add_card")
    empty = tmp / "empty-path"
    empty.mkdir()
    env = {"PYTHONUTF8": "1", "PATH": str(empty)}
    result = run_gate_env(env, "--root", str(root))
    output = result.stdout + result.stderr
    check(
        "G10 with git absent exits non-zero",
        result.returncode != 0,
        output,
    )
    check(
        "the git-unavailable refusal names G10",
        "G10:" in output,
        output,
    )
    check(
        "the refusal names git as the missing dependency",
        "git" in output and "could not be run" in output,
        output,
    )
    check(
        "the refusal names the pending changeset that cannot be checked",
        "zzz-classify.md" in output,
        output,
    )
    check(
        "no traceback reaches the reader",
        "Traceback" not in output,
        output,
    )


def case_g10_is_silent_when_git_absent_and_no_declared_bump(tmp: Path) -> None:
    """With no pending declared bump on disk, G10 has nothing to refuse.

    Cases 1-3 judge only branch-added changesets that declare a bump. An empty
    changeset tree with git absent must not invent a G10 fault; G9 and the
    other git-dependent checks still refuse, under their own IDs.
    """
    root = make_tree(tmp, declared=None, branch_change="none")
    empty = tmp / "empty-path-2"
    empty.mkdir()
    env = {"PYTHONUTF8": "1", "PATH": str(empty)}
    result = run_gate_env(env, "--root", str(root))
    output = result.stdout + result.stderr
    check(
        "G10 is absent from the refusal when no declared bump is pending",
        "G10:" not in output,
        output,
    )
    check(
        "the run still refuses under another check (git is a missing dependency)",
        result.returncode != 0 and "git" in output and "could not be run" in output,
        output,
    )
    check(
        "no traceback reaches the reader",
        "Traceback" not in output,
        output,
    )


CASES = (
    case_positive_correct_classification_is_silent,
    case_positive_rename_major_passes,
    case_positive_add_minor_passes,
    case_case1_rename_declared_patch_is_refused,
    case_case1_rename_declared_minor_is_refused,
    case_case2_add_declared_patch_is_refused,
    case_case2_add_declared_quoted_patch_is_refused,
    case_case2_remove_declared_patch_is_refused,
    case_case3_no_surface_declared_minor_is_refused,
    case_case3_no_surface_declared_major_is_refused,
    case_case3_commented_major_is_refused,
    case_case3_non_card_directory_declared_minor_is_refused,
    case_unparseable_yaml_tag_bump_is_refused,
    case_unparseable_multiword_bump_is_refused,
    case_higher_classification_governs_rename_plus_add,
    case_case4_consumed_major_with_major_delta_passes,
    case_case4_consumed_major_with_minor_delta_is_refused,
    case_case4_consumed_patch_with_minor_delta_is_refused,
    case_case4_consumed_patch_with_no_delta_is_refused,
    case_case4_requires_the_exact_changesets_version,
    case_case4_no_consumed_plan_with_delta_is_refused,
    case_case4_unchanged_version_with_no_consumed_plan_passes,
    case_case4_minor_plan_resets_patch_field,
    case_case4_major_plan_resets_minor_and_patch,
    case_b2a_push_to_main_after_admission_passes,
    case_b2b_next_scripts_only_pr_passes,
    case_b2c_replay_push_to_main_at_316_passes,
    case_b3_v300_shaped_release_passes,
    case_b3_v300_shaped_release_minor_delta_refused,
    case_ard_text_is_read_not_hardcoded,
    case_missing_ard_fails_closed_when_classification_needed,
    case_empty_changeset_is_not_a_classification_fault,
    case_live_tree_gate_stays_green,
    case_g10_refuses_in_its_own_words_when_git_is_absent,
    case_g10_is_silent_when_git_absent_and_no_declared_bump,
    case_ci_runs_the_bump_classification_suite,
    case_ci_carries_the_inversion_poison_control,
    case_ci_carries_case1_to_case4_poison_controls,
    case_ci_carries_unparseable_bump_controls,
    case_ci_carries_b2_and_b3_controls,
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
        "by G10, the inversion is pinned, cases 1-3 judge only branch-added "
        "changesets, case 4 prices the consumed plan and the SemVer reset "
        "fields (R4-F3: minor over 1.2.1 -> 1.3.0, major over 2.1.1 -> 3.0.0), "
        "the ADR text on disk drives classification, G10 refuses in its own "
        "words when git is absent and a declared bump is pending, an unchanged "
        "version at explicit --release stays silent when no plan was consumed, "
        "and the CI poison controls carry the inversion, cases 1-4, B2(a-c), "
        "B3, and the R5-2 unparseable-bump refusals"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
