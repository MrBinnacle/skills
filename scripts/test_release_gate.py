#!/usr/bin/env python3
"""Contract tests for scripts/release_gate.py (ADR 0002, issue #149).

ADR 0002 (docs/adr/0002-a-release-is-a-delivery-event.md) obliges the manifest
to carry a version on each plugin entry, generated from package.json and
asserted equal by a check -- never typed twice. These cases pin that contract.

Every case drives the shipped script as a subprocess against a seeded
temporary tree (--root), never against module internals: the contract is the
exit code and the printed verdict, because those are what CI and a local run
consume. A live-tree case runs the gate over this repository exactly as a
maintainer would, with no arguments.

THE SEEDED TREE PASSES BY CONSTRUCTION
    Each refusal case below is one mutation of `seeded_tree`, so a FAIL line a
    run prints is attributable to the mutation under test. Refusal cases assert
    the message that names the reason, not merely a non-zero exit -- two
    different faults share one exit code, which is the defect the vacuous
    changeset control documented in tests.yml.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GATE = SCRIPT_DIR / "release_gate.py"
REPO_ROOT = SCRIPT_DIR.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"

FAILURES: list[str] = []
NOTES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def note(text: str) -> None:
    """Record something the suite did NOT verify, rather than leave it silent."""
    print(f"note {text}")
    NOTES.append(text)


def run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def run_gate_with_env(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    """Run the gate under a controlled environment.

    G6 re-asserts the external spec validator, which needs `npx` and a package
    download. The suite refuses to require that (a suite that fails on a plane
    is a suite people stop running): instead it drives G6 down the validator's
    own `npx`-absent fail-closed path, which is deterministic and network-free.
    The env narrows PATH so `git` stays reachable (the validator enumerates
    cards through it) while `npx` does not, and `python` runs through
    sys.executable's absolute path."""
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


def git_init(root: Path) -> None:
    """Make a fixture a git tree the spec validator can enumerate with git ls-files."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(root), "add", "-A"], check=True, capture_output=True
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def package_json(version: str) -> str:
    return json.dumps({"name": "mrbinnacle-skills", "version": version}, indent=2) + "\n"


def changeset_md(package: str = "mrbinnacle-skills", level: str = "patch") -> str:
    """A changeset file the way changesets writes them."""
    return f'---\n"{package}": {level}\n---\n\nA described change.\n'


def changelog_md(section_version: str, *, dated: bool = True) -> str:
    """A changelog carrying one section, in this repository's shape.

    ``dated=False`` writes the heading without the release date - the
    half-rolled state behind criterion three.
    """
    date = " - 2026-08-10" if dated else ""
    return f"# Changelog\n\nAll notable changes.\n\n## v{section_version}{date}\n\nShipped.\n"


def manifest_json(versions: Sequence[str | None]) -> str:
    """A manifest shaped like the shipped one, with one entry per version given.

    ``None`` stamps an entry that declares no version at all -- the second
    direction of drift.
    """
    plugins = []
    for i, version in enumerate(versions):
        entry = {
            "name": f"fixture-plugin-{i}",
            "description": "fixture plugin",
            "source": "./",
            "strict": False,
            "skills": [],
        }
        if version is not None:
            entry["version"] = version
        plugins.append(entry)
    data = {
        "name": "fixture-skills",
        "owner": {"name": "fixture", "url": "https://example.invalid"},
        "metadata": {"description": "fixture"},
        "plugins": plugins,
    }
    return json.dumps(data, indent=2) + "\n"


def seeded_tree(
    root: Path, *, package: str = "1.2.0", versions: Sequence[str | None] | None = None
) -> Path:
    """The conforming baseline: every declared version equals the package's,
    and the changelog carries a dated section for that version."""
    write(root / "package.json", package_json(package))
    write(
        root / ".claude-plugin" / "marketplace.json",
        manifest_json([package] if versions is None else versions),
    )
    write(root / "CHANGELOG.md", changelog_md(package))
    return root


# ----------------------------------------------------------------- G1 lockstep


def case_lockstep_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        result = run_gate("--root", str(root))
        check(
            "a tree whose manifest versions equal the package version passes",
            result.returncode == 0,
            result.stdout + result.stderr,
        )
        check(
            "the pass line names the verdict and the derived version",
            "RELEASE GATE: PASS" in result.stdout and "1.2.0" in result.stdout,
            result.stdout,
        )


def case_declared_but_different_version_is_refused() -> None:
    """Direction one: an entry declares a value, and it is not the package's."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["9.9.9"])
        result = run_gate("--root", str(root))
        check(
            "a manifest version other than the package version is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal names the lockstep failure specifically",
            "version drift" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal names both values and the offending plugin",
            "9.9.9" in result.stdout and "1.2.0" in result.stdout and "fixture-plugin-0" in result.stdout,
            result.stdout,
        )


def case_missing_declaration_is_refused() -> None:
    """Direction two: an entry declares nothing. Absence is drift too -- the
    pre-#149 manifest failed here while declaring no wrong value anywhere."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=[None])
        result = run_gate("--root", str(root))
        check(
            "a plugin entry with no version is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the absence refusal is reported as version drift, not skipped",
            "version drift" in result.stdout and "declares no version" in result.stdout,
            result.stdout,
        )


def case_every_failure_reported_in_one_run() -> None:
    """One drifted value and one absent declaration must BOTH be listed by a
    single run. A first-fail gate hides the second fault until the first is
    fixed, which is how stale surfaces survive several review rounds."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["9.9.9", None])
        result = run_gate("--root", str(root))
        check(
            "two independent drifts are refused in one run",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "both failures are listed, not only the first",
            "fixture-plugin-0" in result.stdout and "fixture-plugin-1" in result.stdout,
            result.stdout,
        )
        check(
            "the blocked line counts every failure found",
            "2 stale surface(s)" in result.stdout,
            result.stdout,
        )


# ------------------------------------------------------------- fail-closed G1


def case_absent_package_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        (root / "package.json").unlink()
        result = run_gate("--root", str(root))
        check(
            "an unreadable package.json is a failure, not a skip",
            result.returncode != 0 and "could not be read" in result.stdout,
            result.stdout,
        )


def case_unparseable_package_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / "package.json", "{not json")
        result = run_gate("--root", str(root))
        check(
            "an unparseable package.json is a failure, not a skip",
            result.returncode != 0 and "not parseable JSON" in result.stdout,
            result.stdout,
        )


def case_versionless_package_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / "package.json", '{"name": "mrbinnacle-skills"}\n')
        result = run_gate("--root", str(root))
        check(
            "a package.json stating no version is a failure - there is nothing to derive from",
            result.returncode != 0 and "states no version" in result.stdout,
            result.stdout,
        )


def case_absent_manifest_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        (root / ".claude-plugin" / "marketplace.json").unlink()
        result = run_gate("--root", str(root))
        check(
            "an unreadable manifest is a failure, not a skip",
            result.returncode != 0 and "could not be read" in result.stdout,
            result.stdout,
        )


def case_unparseable_manifest_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / ".claude-plugin" / "marketplace.json", '{"plugins": [}')
        result = run_gate("--root", str(root))
        check(
            "an unparseable manifest is a failure, not a skip",
            result.returncode != 0 and "not parseable JSON" in result.stdout,
            result.stdout,
        )
        check(
            "an unparseable manifest does not also report zero entries",
            "no plugin entries" not in result.stdout,
            result.stdout,
        )


def case_shape_broken_manifest_fails_closed() -> None:
    """`{"plugins": ["x"]}` parsed fine once and raised AttributeError past the
    handler in validate_conformance.py's O7; this gate refuses the shape instead."""
    for bad, why in (
        ('{"plugins": ["x"]}', "a string where an object belongs"),
        ("[1, 2]", "a top-level array"),
        ("{}", "a missing plugins key"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = seeded_tree(Path(tmp))
            write(root / ".claude-plugin" / "marketplace.json", bad)
            result = run_gate("--root", str(root))
            check(
                f"a broken-shaped manifest ({why}) fails closed",
                result.returncode != 0 and "not a readable manifest" in result.stdout,
                result.stdout,
            )


def case_zero_plugins_rejected() -> None:
    """A run that compared against nothing checked nothing. Never a pass."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=[])
        result = run_gate("--root", str(root))
        check(
            "a manifest with no plugin entries is refused",
            result.returncode != 0 and "no plugin entries" in result.stdout,
            result.stdout,
        )


# ------------------------------------------------------- G2 release plan assembles
#
# The incident: `.changeset/quarantine-starts-shipping.md` declared
# `@mrbinnacle/skills` while the workspace package is `mrbinnacle-skills`, so
# `changeset version` refused to assemble a release plan - and the check written
# for that defect ran `changeset status --since=origin/main`, which examines an
# EMPTY set on main, so CI stayed green from 2026-08-24 over a tree no release
# could be cut from (#144 fixed CI; G2 gives the gate its own unscoped verdict).


def case_out_of_workspace_changeset_is_refused() -> None:
    """The full pending set must assemble into a release plan. One changeset
    naming a package outside the workspace means it never will, wherever the
    file sits relative to whatever ref a scoped comparison names."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(
            root / ".changeset" / "zzz-out-of-workspace.md",
            changeset_md(package="@mrbinnacle/skills"),
        )
        result = run_gate("--root", str(root))
        check(
            "a changeset naming a package outside the workspace is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal names the plan-assembly failure specifically",
            "does not assemble" in result.stdout and "not in the workspace" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal names the file and the offending package",
            "zzz-out-of-workspace.md" in result.stdout and "@mrbinnacle/skills" in result.stdout,
            result.stdout,
        )
        check(
            "the plan failure is the only fault the run finds in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_malformed_changeset_frontmatter_fails_closed() -> None:
    """A changeset whose header cannot be read is exactly as fatal to the plan
    as one naming a wrong package: changesets itself would refuse it. Fail
    closed - listed, never skipped."""
    for bad, why in (
        ('---\n"@mrbinnacle/skills": patch\n', "frontmatter that never closes"),
        ("prose only, no frontmatter\n", "no frontmatter at all"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = seeded_tree(Path(tmp))
            write(root / ".changeset" / "zzz-broken-header.md", bad)
            result = run_gate("--root", str(root))
            check(
                f"an unreadable changeset ({why}) fails closed",
                result.returncode != 0 and "unreadable frontmatter" in result.stdout,
                result.stdout,
            )


def case_valid_pending_changesets_pass_the_everyday_run() -> None:
    """Pending changesets are the process working between releases: well-formed
    ones naming workspace packages must never turn an ordinary run red."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / ".changeset" / "a-good-one.md", changeset_md(level="minor"))
        write(root / ".changeset" / "b-good-two.md", changeset_md())
        result = run_gate("--root", str(root))
        check(
            "well-formed pending changesets pass the ordinary run",
            result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
            result.stdout,
        )


# ------------------------------------------------- G3 unconsumed at release time
#
# The incident: dozens of changesets pend against a changelog whose newest
# entry describes a version nobody ever received. Between releases, pending
# changesets ARE the process working. At release time they are fatal: ADR 0002
# makes the version bump's merge the delivery event, and `changeset version`
# consumes every pending file when it rolls. One left behind means the release
# ships while the plan still holds entries - some change silently misses the
# release it was filed against.


def case_unconsumed_changesets_block_release_mode() -> None:
    """The ordinary run passes a pending changeset through; a declared release
    refuses it. The boundary is the point: mid-cycle accumulation is legal,
    releasing over an unconsumed plan is not."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / ".changeset" / "zzz-pending.md", changeset_md())
        plain = run_gate("--root", str(root))
        check(
            "the ordinary run passes one well-formed pending changeset",
            plain.returncode == 0 and "RELEASE GATE: PASS" in plain.stdout,
            plain.stdout,
        )
        release = run_gate("--release", "--root", str(root))
        check(
            "--release refuses while an unconsumed changeset remains",
            release.returncode != 0,
            release.stdout,
        )
        check(
            "the refusal names unconsumed changesets specifically",
            "unconsumed changeset" in release.stdout and "zzz-pending.md" in release.stdout,
            release.stdout,
        )


def case_release_mode_counts_every_remaining_changeset() -> None:
    """One finding, naming every file left: the count is the size of what the
    release would have shipped without."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / ".changeset" / "a-left-in.md", changeset_md(level="minor"))
        write(root / ".changeset" / "b-left-two.md", changeset_md())
        result = run_gate("--release", "--root", str(root))
        check(
            "--release reports every remaining file under one finding",
            result.returncode != 0
            and "2 unconsumed changeset(s)" in result.stdout
            and "a-left-in.md" in result.stdout
            and "b-left-two.md" in result.stdout,
            result.stdout,
        )
        check(
            "the unconsumed finding is the only fault in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_release_mode_ignores_the_changeset_readme() -> None:
    """.changeset/README.md ships with every changesets install. It is
    documentation, not a pending change, and must never block a release."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / ".changeset" / "README.md", "# Changesets\n\nHow to use them.\n")
        result = run_gate("--release", "--root", str(root))
        check(
            "--release passes a tree whose only .changeset markdown is README.md",
            result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
            result.stdout,
        )


# --------------------------------------------------- G4 dated changelog section
#
# The incident: a sibling repository tagged a release whose changelog section
# had never been rolled. The tag promised a version's worth of changes; the
# changelog had no entry for it. Here, the version being released is the one
# package.json declares, and its changelog section must exist AND carry a
# date - an undated heading is a section half-rolled.


def case_missing_changelog_section_is_refused() -> None:
    """package.json declares 1.3.0 while the newest rolled entry is 1.2.0:
    the release would ship a version whose entry was never written."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), package="1.3.0", versions=["1.3.0"])
        write(root / "CHANGELOG.md", changelog_md("1.2.0"))
        result = run_gate("--root", str(root))
        check(
            "a version with no changelog section is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal names the missing dated section and the version",
            "no dated section for version 1.3.0" in result.stdout,
            result.stdout,
        )
        check(
            "the changelog refusal is the only fault in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_undated_changelog_section_is_refused() -> None:
    """A section that names the version but carries no date is not a dated
    section: the roll never recorded when the version was delivered."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / "CHANGELOG.md", changelog_md("1.2.0", dated=False))
        result = run_gate("--root", str(root))
        check(
            "a version heading without a date is refused",
            result.returncode != 0 and "carries no release date" in result.stdout,
            result.stdout,
        )


def case_absent_changelog_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        (root / "CHANGELOG.md").unlink()
        result = run_gate("--root", str(root))
        check(
            "an unreadable CHANGELOG.md is a failure, not a skip",
            result.returncode != 0 and "could not be read" in result.stdout,
            result.stdout,
        )


def case_version_number_inside_a_larger_one_is_not_a_section_match() -> None:
    """1.2.0 must not be satisfied by a `## v11.2.0` heading: the match is
    boundary-checked in both directions."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / "CHANGELOG.md", changelog_md("11.2.0"))
        result = run_gate("--root", str(root))
        check(
            "a superset version heading does not satisfy the section requirement",
            result.returncode != 0 and "no dated section for version 1.2.0" in result.stdout,
            result.stdout,
        )


# ----------------------------------------------------- #152 re-asserted at release
#
# ADR 0002 makes the version bump's merge the moment a version becomes
# permanent, so the obligations that already hold on every pull request are
# re-asserted at that moment: the manifest and the published tree name the
# same cards (O7), the external specification validator is clean over the
# published tree, and every workflow action is still pinned to a commit SHA.
# Each is a --release check (it answers "may this version ship", not "are the
# surfaces healthy today") and each ships its own poison control in CI below.
#
# These cases build a tree that CARRIES a published `skills/` tree, because the
# seeded_tree helper above has none. A seeded tree with no skills is the state
# the lockstep/changeset/changelog cases above rely on to stay single-reason,
# so the new checks must skip cleanly when there is nothing published to
# re-assert - and they do, which is itself pinned by a case below.

SKILLS_BUCKET = "engineering"


def skill_card(root: Path, name: str, *, description: str = "fixture card") -> Path:
    """A minimal published card: a SKILL.md two levels under skills/."""
    folder = root / "skills" / SKILLS_BUCKET / name
    write(folder / "SKILL.md", f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n")
    return folder


def manifest_with_skills(root: Path, cards: tuple[str, ...], version: str = "1.2.0") -> None:
    """A manifest naming exactly the given cards, one plugin, in lockstep."""
    entries = ",\n".join(f'"./skills/{SKILLS_BUCKET}/{c}"' for c in cards)
    write(
        root / ".claude-plugin" / "marketplace.json",
        "{\n"
        '  "name": "fixture-skills",\n'
        '  "owner": {"name": "fixture", "url": "https://example.invalid"},\n'
        '  "plugins": [\n'
        "    {\n"
        '      "name": "fixture-engineering",\n'
        '      "description": "fixture",\n'
        '      "source": "./",\n'
        '      "strict": false,\n'
        f'      "skills": [{entries}],\n'
        f'      "version": "{version}"\n'
        "    }\n"
        "  ]\n"
        "}\n",
    )


def release_tree_with_skills(root: Path, cards: tuple[str, ...], package: str = "1.2.0") -> Path:
    """A tree releasable except for whatever the case plants: package in
    lockstep with a manifest naming every card, a dated changelog, no pending
    changesets, no workflows."""
    write(root / "package.json", package_json(package))
    manifest_with_skills(root, cards, version=package)
    write(root / "CHANGELOG.md", changelog_md(package))
    for name in cards:
        skill_card(root, name)
    return root


# ----------------------------------------------------- G5 manifest and tree agree


def case_manifest_and_tree_agree_passes_release() -> None:
    """A release tree whose manifest names every published card passes G5."""
    with tempfile.TemporaryDirectory() as tmp:
        root = release_tree_with_skills(Path(tmp), ("alpha-card", "beta-card"))
        result = run_gate("--release", "--root", str(root))
        check(
            "a release tree whose manifest covers the tree passes",
            result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
            result.stdout,
        )


def case_manifest_naming_a_missing_card_is_refused_at_release() -> None:
    """Direction one: the manifest points at a path with no card at it. O7 was
    forward-only once and an undercount stayed green; both directions are
    required, and this is the direction a forward-only check still passes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = release_tree_with_skills(Path(tmp), ("alpha-card",))
        # name a ghost card the tree does not publish
        manifest_with_skills(root, ("alpha-card", "ghost-card"))
        result = run_gate("--release", "--root", str(root))
        check(
            "a manifest naming a path with no card is refused at release",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal names the manifest/tree disagreement",
            "G5:" in result.stdout and "no card at the path" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal names the ghost card",
            "ghost-card" in result.stdout,
            result.stdout,
        )
        check(
            "the manifest/tree refusal is the only fault in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_unexposed_card_is_refused_at_release() -> None:
    """Direction two: a published card no plugin names. The forward-only
    check stays green here, which is the whole reason this direction exists."""
    with tempfile.TemporaryDirectory() as tmp:
        root = release_tree_with_skills(Path(tmp), ("alpha-card", "beta-card"))
        # drop beta-card from the manifest while leaving it published
        manifest_with_skills(root, ("alpha-card",))
        result = run_gate("--release", "--root", str(root))
        check(
            "a published card named by no plugin is refused at release",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal names the unexposed card",
            "G5:" in result.stdout
            and "named by no plugin" in result.stdout
            and "beta-card" in result.stdout,
            result.stdout,
        )
        check(
            "the unexposed-card refusal is the only fault in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_g5_skips_when_nothing_is_published() -> None:
    """A seeded tree (no skills/) must not turn red on G5: there is nothing
    published to re-assert. This is what keeps the lockstep/changeset/changelog
    cases single-reason."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        result = run_gate("--release", "--root", str(root))
        check(
            "a tree with no skills/ does not fail on the manifest/tree check",
            "G5:" not in result.stdout,
            result.stdout,
        )


def case_live_manifest_and_tree_agree() -> None:
    """The live assertion: the shipped manifest covers the live published
    tree, both directions. The conformance suite pins O7 over the live tree
    too; this pins the release gate's re-assertion of it."""
    sys.path.insert(0, str(SCRIPT_DIR))
    import release_gate as gate  # noqa: E402
    import validate_conformance as conformance  # noqa: E402
    result = conformance.check_plugin_manifest(REPO_ROOT)
    check(
        "the live manifest and published tree agree, both directions",
        result.verdict == "PASS",
        f"{result.verdict}: {result.detail}",
    )
    errors: list[str] = []
    gate.gate_manifest_tree_agreement(REPO_ROOT, errors)
    check(
        "the release gate's G5 re-assertion passes over the live tree",
        not errors,
        str(errors),
    )


# ----------------------------------------------------- G6 external spec validator


# A PATH that keeps `git` (the validator enumerates cards through it) and drops
# `npx`, so the external spec validator takes its own network-free fail-closed
# path instead of the suite needing a package download. `python` runs through
# sys.executable's absolute path, so it does not need to be on PATH here.
NO_NPX_PATH = "/usr/bin:/bin"


def case_g6_reds_when_the_spec_validator_cannot_run() -> None:
    """G6 wraps the external spec validator as a subprocess and reports its
    verdict. Driven down the validator's own `npx`-absent path so the suite needs
    no network: the validator refuses to run without npx, and G6 must refuse the
    release on that refusal -- a release the external validator never verified
    is not a release the gate may pass. The tree is a git tree with a published
    card and a manifest in lockstep, so G1/G5 are silent and G6 is the only
    finding."""
    with tempfile.TemporaryDirectory() as tmp:
        root = release_tree_with_skills(Path(tmp), ("alpha-card",))
        git_init(root)
        result = run_gate_with_env(
            {"PATH": NO_NPX_PATH, "PYTHONUTF8": "1"},
            "--release",
            "--root",
            str(root),
        )
        check(
            "a release whose external spec validator could not run is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal is reported under G6",
            "G6:" in result.stdout
            and "external specification validator" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal carries the validator's own reason (npx absent)",
            "npx" in result.stdout,
            result.stdout,
        )
        check(
            "the spec-validator refusal is the only fault in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_g6_passes_a_git_release_tree_the_suite_cannot_reach_npx_for() -> None:
    """The mirror of the case above, over a git tree. When npx IS reachable the
    validator runs; the suite cannot assume that, so this case is the one that
    would carry the live npx run and is therefore left to CI. It is asserted
    here only as wiring (the control exists) and as the skip that keeps a
    non-git fixture single-reason (the release_tree_with_skills cases above)."""
    note(
        "the live G6 subprocess run against the real reference validator is "
        "NOT exercised here -- it needs npx and a package download. CI's poison "
        "control under the release-gate job proves it reds; this suite proves "
        "G6 skips a non-git tree and refuses one whose validator could not run."
    )


# ----------------------------------------------------- G7 workflow actions pinned


def workflow_with_uses(root: Path, *uses_lines: str) -> None:
    """A workflow file whose steps carry the given `uses:` lines verbatim."""
    body = "name: control\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n"
    for line in uses_lines:
        body += f"      - {line}\n"
    write(root / ".github" / "workflows" / "control.yml", body)


def case_a_pinned_workflow_passes_release() -> None:
    """A workflow whose every `uses:` is pinned to a 40-hex SHA passes G7."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        workflow_with_uses(
            root,
            "uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4",
            "uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5",
        )
        result = run_gate("--release", "--root", str(root))
        check(
            "a workflow pinned to commit SHAs passes the release gate",
            result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
            result.stdout,
        )


def case_a_mutable_workflow_ref_is_refused_at_release() -> None:
    """A floating tag is not a pin (CVE-2025-30066 repointed every
    tj-actions/changed-files tag from v1 to v45 inside 24 hours). G7 must refuse
    it, naming the file, the line, and the mutable ref, and it must be the only
    fault in a tree whose every other surface is clean."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        workflow_with_uses(
            root,
            "uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4",
            "uses: actions/setup-python@v5",
            "uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0",
        )
        result = run_gate("--release", "--root", str(root))
        check(
            "a workflow using a mutable ref is refused at release",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal is reported under G7",
            "G7:" in result.stdout and "mutable ref" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal names the file and the offending line",
            ".github/workflows/control.yml:8" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal names the mutable ref a reader would type",
            "actions/setup-python@v5" in result.stdout,
            result.stdout,
        )
        check(
            "the two pinned lines are not also reported",
            result.stdout.count("G7:") == 1,
            result.stdout,
        )
        check(
            "the mutable-ref refusal is the only fault in this tree",
            "1 stale surface(s)" in result.stdout,
            result.stdout,
        )


def case_an_abbreviated_sha_is_not_a_pin() -> None:
    """A short SHA is still mutable: GitHub Actions requires the full 40 hex,
    and an abbreviated ref is the shape a careless re-pin takes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        workflow_with_uses(root, "uses: actions/checkout@11d5960a # abbreviated")
        result = run_gate("--release", "--root", str(root))
        check(
            "an abbreviated SHA is refused as a mutable ref",
            result.returncode != 0
            and "G7:" in result.stdout
            and "actions/checkout@11d5960a" in result.stdout,
            result.stdout,
        )


def case_a_local_action_is_not_in_scope() -> None:
    """A `./` action is repo code pinned by the commit, not a third-party
    action pinned by a SHA, so G7 must leave it alone."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        workflow_with_uses(root, "uses: ./.github/actions/local")
        result = run_gate("--release", "--root", str(root))
        check(
            "a local ./ action is not flagged as a mutable ref",
            result.returncode == 0 and "G7:" not in result.stdout,
            result.stdout,
        )


def case_g7_skips_when_no_workflows() -> None:
    """A tree with no workflow directory has nothing to re-pin. This is what
    keeps the seeded-tree lockstep/changeset/changelog cases single-reason."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        result = run_gate("--release", "--root", str(root))
        check(
            "a tree with no workflows does not fail on the pinning check",
            "G7:" not in result.stdout,
            result.stdout,
        )


def case_live_workflow_actions_are_pinned() -> None:
    """The live assertion: every shipped `uses:` is pinned to a full 40-hex SHA.
    This is the acceptance criterion pinned against the real artifact rather
    than only against fixtures built to pass."""
    sys.path.insert(0, str(SCRIPT_DIR))
    import release_gate as gate  # noqa: E402
    errors: list[str] = []
    gate.gate_workflow_pins(REPO_ROOT, errors)
    check(
        "every shipped workflow action is pinned to a full commit SHA",
        not errors,
        str(errors),
    )


# --------------------------------------------------------- compound refusal list


def case_all_three_refusals_land_in_one_run() -> None:
    """One tree, three unmet checks, three listed failures in a single run.
    A first-fail gate would show one and hide the other two until each was
    fixed in turn - three review rounds to learn what this run says at once.
    The manifest is held in lockstep so the count proves the three findings
    are exactly G2, G3 and G4."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), package="1.3.0", versions=["1.3.0"])
        write(root / "CHANGELOG.md", changelog_md("1.2.0"))
        write(root / ".changeset" / "a-valid.md", changeset_md(level="minor"))
        write(
            root / ".changeset" / "b-misnamed.md",
            changeset_md(package="@mrbinnacle/skills"),
        )
        result = run_gate("--release", "--root", str(root))
        check(
            "a tree failing all three checks is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the plan-assembly failure is listed",
            "does not assemble" in result.stdout
            and "@mrbinnacle/skills" in result.stdout,
            result.stdout,
        )
        check(
            "the unconsumed-changesets failure is listed",
            "unconsumed changeset(s) remain" in result.stdout,
            result.stdout,
        )
        check(
            "the missing dated section is listed",
            "no dated section for version 1.3.0" in result.stdout,
            result.stdout,
        )
        check(
            "all three failures are counted by the blocked line",
            "3 stale surface(s)" in result.stdout,
            result.stdout,
        )
        check(
            "lockstep stayed silent - the three findings are G2, G3 and G4 alone",
            "version drift" not in result.stdout,
            result.stdout,
        )


# ------------------------------------------------------------------- --write


def case_write_derives_every_entry_from_the_package() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["0.0.1", None])
        result = run_gate("--write", "--root", str(root))
        check(
            "--write exits 0 after stamping the seeded tree",
            result.returncode == 0,
            result.stdout + result.stderr,
        )
        stamped = json.loads((Path(tmp) / ".claude-plugin" / "marketplace.json").read_text("utf-8"))
        declared = {p["name"]: p.get("version") for p in stamped["plugins"]}
        check(
            "--write derives EVERY entry's version from package.json",
            set(declared.values()) == {"1.2.0"},
            str(declared),
        )
        verify = run_gate("--root", str(tmp))
        check(
            "the written tree verifies in lockstep",
            verify.returncode == 0,
            verify.stdout,
        )


def case_write_is_idempotent() -> None:
    """Generated data must be stable under re-runs; churn would make every
    unrelated commit carry a diff."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["0.0.1"])
        first = run_gate("--write", "--root", str(root))
        once = (Path(tmp) / ".claude-plugin" / "marketplace.json").read_bytes()
        second = run_gate("--write", "--root", str(root))
        twice = (Path(tmp) / ".claude-plugin" / "marketplace.json").read_bytes()
        check(
            "--write is idempotent: a second run writes identical bytes",
            first.returncode == 0 and second.returncode == 0 and once == twice,
            first.stdout + second.stdout,
        )


def case_write_fails_closed_on_unreadable_inputs() -> None:
    for victim, why in (("package.json", "unreadable source"), ("marketplace.json", "unreadable target")):
        with tempfile.TemporaryDirectory() as tmp:
            root = seeded_tree(Path(tmp))
            if victim == "package.json":
                (root / "package.json").unlink()
            else:
                (root / ".claude-plugin" / "marketplace.json").unlink()
            result = run_gate("--write", "--root", str(root))
            check(
                f"--write fails closed on an {why}, writing nothing",
                result.returncode != 0 and "RELEASE GATE: PASS" not in result.stdout,
                result.stdout,
            )


def case_live_tree_in_lockstep() -> None:
    """The shipped tree, checked exactly as a maintainer checks it: no
    arguments. This pins the acceptance criterion against the real artifact --
    every live plugin entry declares a version, derived by --write from
    package.json -- rather than only against fixtures built to pass."""
    result = run_gate()
    check(
        "the live tree passes the gate with no arguments",
        result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
        result.stdout + result.stderr,
    )
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    undeclared = [
        p["name"] for p in manifest["plugins"] if p.get("version") != package["version"]
    ]
    check(
        "every live plugin entry declares the package.json version",
        not undeclared,
        f"entries not at {package['version']}: {undeclared}",
    )


# ------------------------------------------------------------------ CI wiring
#
# The gate's verdict must not depend on where it runs: CI executes the same
# argument-less command a local run does, so neither surface can grow flags or
# context the other lacks. These cases read tests.yml the way the eval-corpus
# suite reads it -- as text, asserting the wiring that exists rather than
# parsing YAML into a different dialect.


def workflow_job(name: str) -> str:
    """One job's body from tests.yml, from its key to the next top-level job."""
    match = re.search(rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  \S|\Z)", WORKFLOW.read_text("utf-8"))
    return match.group(1) if match else ""


def named_step(job: str, step_name: str) -> str:
    """One step's body, from its `name:` line to the next `- name:` line."""
    match = re.search(
        rf"(?ms)^      - name: {re.escape(step_name)}\n(.*?)(?=^      - name: |\Z)", job
    )
    return match.group(1) if match else ""


def case_ci_runs_the_same_argumentless_command() -> None:
    """Criterion 6, CI half: what CI runs is what a local run runs. A gate
    whose CI form carries different flags verifies a different contract than
    the one the maintainer can run, and the difference would be invisible
    until the two disagreed about a release."""
    job = workflow_job("release-gate")
    step = named_step(job, "Run release gate")
    check(
        "the CI release-gate job exists",
        bool(job),
        "no 'release-gate:' job found in .github/workflows/tests.yml",
    )
    check(
        "CI runs the gate with no arguments - the same command a local run uses",
        "python scripts/release_gate.py" in step
        and "--root" not in step
        and "--write" not in step,
        step,
    )
    check(
        "CI asserts the PASS verdict line, not only an exit code",
        "RELEASE GATE: PASS" in step,
        step,
    )
    suite_step = named_step(job, "Release-gate suite")
    check(
        "CI runs this suite itself and requires its PASS line",
        "python scripts/test_release_gate.py" in suite_step and "^PASS:" in suite_step,
        suite_step,
    )


def case_ci_job_is_non_blocking_and_on_every_pull_request() -> None:
    """Criterion 7: advisory while the tracer matures. The blocking gate ADR
    0002 owes arrives with the release pipeline; until then a refusal must be
    visible without gating merges on a process that cannot act on it yet."""
    job = workflow_job("release-gate")
    triggers = WORKFLOW.read_text("utf-8")[: WORKFLOW.read_text("utf-8").index("jobs:")]
    check(
        "the release-gate job is non-blocking (continue-on-error)",
        "continue-on-error: true" in job,
        job,
    )
    check(
        "the workflow runs on pull_request",
        "pull_request:" in triggers,
        triggers,
    )


def case_ci_control_drives_the_gate_red_for_the_right_reason() -> None:
    """Criterion 8: the control proves the refusal is real AND specific. Two
    different faults share one exit code -- the changeset control below the
    release-gate job documents exiting identically with and without its
    poison -- so the control must require the message that names the lockstep
    failure, and the failure count that proves it failed for one reason."""
    control = named_step(
        workflow_job("release-gate"),
        "Poison control - a drifted manifest version must be rejected",
    )
    check(
        "CI carries the release-gate poison control",
        bool(control),
        "no such step found under the release-gate job",
    )
    check(
        "the control runs the SHIPPED gate against the planted tree",
        "python scripts/release_gate.py --root" in control,
        control,
    )
    check(
        "the control plants a conforming changelog so G4 cannot share the refusal",
        "CHANGELOG.md" in control and "v1.2.0" in control,
        control,
    )
    check(
        "the control requires the lockstep-specific message, not only a non-zero exit",
        "'version drift'" in control,
        control,
    )
    check(
        "the control requires the refusal to name the drifted plugin",
        "control-plugin-drifted" in control,
        control,
    )
    check(
        "the control requires a single-reason failure, not incidental breakage",
        "1 stale surface(s)" in control,
        control,
    )


def case_control_tree_is_temporary_not_committed() -> None:
    """Criterion 9: a committed breaching fixture would sit inside the guarded
    tree and turn the real run permanently red, buying back green with an
    exclusion list - the hole the format gate's control comment describes."""
    control = named_step(
        workflow_job("release-gate"),
        "Poison control - a drifted manifest version must be rejected",
    )
    check(
        "the control builds its breaching tree under RUNNER_TEMP",
        'tree="$RUNNER_TEMP/' in control,
        control,
    )
    tracked = subprocess.run(
        ["git", "ls-files", "scripts/fixtures"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    ).stdout
    check(
        "no release-gate fixture tree is committed under scripts/fixtures",
        "release" not in tracked.lower(),
        tracked,
    )


# ------------------------------------------------------- #150 controls in CI
#
# Each new check ships its own poison control, and each control asserts its
# own distinguishing message rather than a bare non-zero exit - two faults
# share one exit code, which is the exact defect the vacuous changeset
# control documented in this file's history.


def case_ci_control_refuses_a_changeset_outside_the_workspace() -> None:
    step = named_step(
        workflow_job("release-gate"),
        "Poison control - a changeset outside the workspace must be rejected",
    )
    check(
        "CI carries the G2 plan-assembly poison control",
        bool(step),
        "no such step found under the release-gate job",
    )
    check(
        "the G2 control plants an out-of-workspace changeset",
        '"@mrbinnacle/skills"' in step and ".changeset/zzz-poison-plan.md" in step,
        step,
    )
    check(
        "the G2 control verifies the plant before trusting the verdict",
        "was not mutated" in step,
        step,
    )
    check(
        "the G2 control runs the SHIPPED gate against the planted tree",
        'python scripts/release_gate.py --root "$tree"' in step,
        step,
    )
    check(
        "the G2 control requires the assembly-specific message, not only a non-zero exit",
        "'not in the workspace'" in step and "'zzz-poison-plan.md'" in step,
        step,
    )
    check(
        "the G2 control requires a single-reason refusal",
        "'1 stale surface(s)'" in step,
        step,
    )


def case_ci_control_blocks_a_declared_release_over_unconsumed_changesets() -> None:
    step = named_step(
        workflow_job("release-gate"),
        "Poison control - unconsumed changesets must block a declared release",
    )
    check(
        "CI carries the G3 release-mode poison control",
        bool(step),
        "no such step found under the release-gate job",
    )
    check(
        "the G3 control first requires the ordinary run to PASS the same tree",
        "^RELEASE GATE: PASS" in step,
        step,
    )
    check(
        "the G3 control then drives the declared release red",
        "--release --root" in step,
        step,
    )
    check(
        "the G3 control requires the unconsumed-specific message",
        "'unconsumed changeset(s) remain at release time'" in step,
        step,
    )
    check(
        "the G3 control requires a single-reason refusal",
        "'1 stale surface(s)'" in step,
        step,
    )


def case_ci_control_refuses_an_unrolled_changelog() -> None:
    step = named_step(
        workflow_job("release-gate"),
        "Poison control - an unrolled changelog must be rejected",
    )
    check(
        "CI carries the G4 changelog poison control",
        bool(step),
        "no such step found under the release-gate job",
    )
    check(
        "the G4 control plants a version with no rolled section",
        '"version": "1.2.0"' in step and "v0.9.0" in step,
        step,
    )
    check(
        "the G4 control runs the SHIPPED gate against the planted tree",
        'python scripts/release_gate.py --root "$tree"' in step,
        step,
    )
    check(
        "the G4 control requires the dated-section-specific message",
        "'no dated section for version 1.2.0'" in step,
        step,
    )
    check(
        "the G4 control requires a single-reason refusal",
        "'1 stale surface(s)'" in step,
        step,
    )


# ------------------------------------------------------- #152 controls in CI


def case_ci_control_refuses_a_manifest_disagreeing_with_the_tree() -> None:
    step = named_step(
        workflow_job("release-gate"),
        "Poison control - a manifest that disagrees with the published tree must be rejected",
    )
    check(
        "CI carries the G5 manifest/tree poison control",
        bool(step),
        "no such step found under the release-gate job",
    )
    check(
        "the G5 control plants a ghost card the tree does not publish",
        "./skills/engineering/ghost-card" in step and "alpha-card/SKILL.md" in step,
        step,
    )
    check(
        "the G5 control runs the SHIPPED gate at release against the planted tree",
        "release_gate.py --release --root" in step,
        step,
    )
    check(
        "the G5 control requires the manifest/tree-specific message",
        "'G5:'" in step and "'no card at the path'" in step and "'ghost-card'" in step,
        step,
    )
    check(
        "the G5 control requires a single-reason refusal",
        "'1 stale surface(s)'" in step,
        step,
    )


def case_ci_control_refuses_a_spec_violation_over_the_published_tree() -> None:
    step = named_step(
        workflow_job("release-gate"),
        "Poison control - a spec violation over the published tree must be rejected",
    )
    check(
        "CI carries the G6 spec-violation poison control",
        bool(step),
        "no such step found under the release-gate job",
    )
    check(
        "the G6 control plants the exact class that rejected two live cards",
        "broken: an unquoted scalar with a colon" in step,
        step,
    )
    check(
        "the G6 control makes the poison tree a git tree the validator can enumerate",
        "git -C \"$tree\" init" in step and "git -C \"$tree\" add" in step,
        step,
    )
    check(
        "the G6 control runs the SHIPPED gate at release against the planted tree",
        "release_gate.py --release --root" in step,
        step,
    )
    check(
        "the G6 control requires the spec-validator-specific message",
        "'G6:'" in step and "'external specification validator'" in step and "'Invalid YAML'" in step,
        step,
    )
    check(
        "the G6 control requires a single-reason refusal",
        "'1 stale surface(s)'" in step,
        step,
    )


def case_ci_control_refuses_a_mutable_workflow_ref() -> None:
    """Criterion 5: the pinning check reds when any `uses:` line is reverted to
    a mutable ref. The control reverts one pinned line back to a floating tag
    and requires the refusal to name the file, the ref, and itself."""
    step = named_step(
        workflow_job("release-gate"),
        "Poison control - a mutable workflow ref must be rejected",
    )
    check(
        "CI carries the G7 mutable-ref poison control",
        bool(step),
        "no such step found under the release-gate job",
    )
    check(
        "the G7 control reverts a pinned line to a mutable ref",
        "actions/setup-python@v5" in step,
        step,
    )
    check(
        "the G7 control keeps one line pinned so the control is not vacuous",
        "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in step,
        step,
    )
    check(
        "the G7 control runs the SHIPPED gate at release against the planted tree",
        "release_gate.py --release --root" in step,
        step,
    )
    check(
        "the G7 control requires the mutable-ref-specific message",
        "'G7:'" in step and "'mutable ref'" in step and "'actions/setup-python@v5'" in step,
        step,
    )
    check(
        "the G7 control requires the refusal to name the workflow file",
        "'control.yml'" in step,
        step,
    )
    check(
        "the G7 control requires a single-reason refusal",
        "'1 stale surface(s)'" in step,
        step,
    )


def case_ci_release_gate_sets_up_node_for_the_spec_validator() -> None:
    """The G6 control re-runs the external spec validator, which needs npx. The
    release-gate job must set up node -- and that line is itself a `uses:` that
    G7 re-asserts is pinned, closing the loop."""
    job = workflow_job("release-gate")
    check(
        "the release-gate job sets up node for npx",
        "actions/setup-node@" in job,
        job,
    )


def main() -> None:
    cases = (
        case_lockstep_passes,
        case_declared_but_different_version_is_refused,
        case_missing_declaration_is_refused,
        case_every_failure_reported_in_one_run,
        case_absent_package_fails_closed,
        case_unparseable_package_fails_closed,
        case_versionless_package_fails_closed,
        case_absent_manifest_fails_closed,
        case_unparseable_manifest_fails_closed,
        case_shape_broken_manifest_fails_closed,
        case_zero_plugins_rejected,
        case_out_of_workspace_changeset_is_refused,
        case_malformed_changeset_frontmatter_fails_closed,
        case_valid_pending_changesets_pass_the_everyday_run,
        case_unconsumed_changesets_block_release_mode,
        case_release_mode_counts_every_remaining_changeset,
        case_release_mode_ignores_the_changeset_readme,
        case_missing_changelog_section_is_refused,
        case_undated_changelog_section_is_refused,
        case_absent_changelog_fails_closed,
        case_version_number_inside_a_larger_one_is_not_a_section_match,
        case_all_three_refusals_land_in_one_run,
        case_write_derives_every_entry_from_the_package,
        case_write_is_idempotent,
        case_write_fails_closed_on_unreadable_inputs,
        case_live_tree_in_lockstep,
        case_ci_runs_the_same_argumentless_command,
        case_ci_job_is_non_blocking_and_on_every_pull_request,
        case_ci_control_drives_the_gate_red_for_the_right_reason,
        case_control_tree_is_temporary_not_committed,
        case_ci_control_refuses_a_changeset_outside_the_workspace,
        case_ci_control_blocks_a_declared_release_over_unconsumed_changesets,
        case_ci_control_refuses_an_unrolled_changelog,
        case_manifest_and_tree_agree_passes_release,
        case_manifest_naming_a_missing_card_is_refused_at_release,
        case_unexposed_card_is_refused_at_release,
        case_g5_skips_when_nothing_is_published,
        case_live_manifest_and_tree_agree,
        case_g6_reds_when_the_spec_validator_cannot_run,
        case_g6_passes_a_git_release_tree_the_suite_cannot_reach_npx_for,
        case_a_pinned_workflow_passes_release,
        case_a_mutable_workflow_ref_is_refused_at_release,
        case_an_abbreviated_sha_is_not_a_pin,
        case_a_local_action_is_not_in_scope,
        case_g7_skips_when_no_workflows,
        case_live_workflow_actions_are_pinned,
        case_ci_control_refuses_a_manifest_disagreeing_with_the_tree,
        case_ci_control_refuses_a_spec_violation_over_the_published_tree,
        case_ci_control_refuses_a_mutable_workflow_ref,
        case_ci_release_gate_sets_up_node_for_the_spec_validator,
    )
    for case in cases:
        case()
    print()
    for text in NOTES:
        print(f"NOT VERIFIED: {text}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: release gate verified across {len(cases)} contract case(s) - "
        "seeded trees, the live tree, and the CI wiring - every refusal "
        "asserting its own message, never only a non-zero exit."
    )


if __name__ == "__main__":
    main()
