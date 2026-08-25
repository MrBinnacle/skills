#!/usr/bin/env python3
"""Release gate -- refuses a release whose public surfaces have gone stale.

Why this exists: ADR 0002 (docs/adr/0002-a-release-is-a-delivery-event.md)
made a version bump's merge the act of delivering changed cards to installed
users, and obliged `.claude-plugin/marketplace.json` to carry a `version` on
each plugin entry. That value is GENERATED from `package.json` and asserted
equal by this script -- never typed twice. A hand-maintained second copy of a
derived value is the manual synchronisation this project has already ruled a
maintenance tax rather than a safeguard.

This is the tracer bullet (#149): one stated reason to refuse a release, end
to end -- a script that runs locally and in CI, a generated version surface,
and a control proving the refusal is real. Later checks join it as siblings.

Checks (all must pass; failures are listed, not first-fail):

  G1  Every plugin entry in .claude-plugin/marketplace.json declares exactly
      the version package.json declares. Both directions are drift: a declared
      value that differs, and a declaration missing entirely (the manifest
      shipped in that second state before #149, with no wrong value anywhere).
      Zero entries is its own refusal: a run that compared against nothing
      checked nothing.

  G2  The full pending changeset set assembles into a release plan: every
      .changeset/*.md names a package the workspace contains. This is the
      gate's own unscoped `changeset status`. The scoped `--since=origin/main`
      form examines an empty set when run on main, which is how a changeset
      naming @mrbinnacle/skills kept CI green from 2026-08-24 while blocking
      every release (#144 fixed CI; G2 gives the gate its own verdict). An
      unreadable frontmatter is the same refusal by another route: changesets
      itself would refuse to assemble over it.

  G3  (--release only) No unconsumed changeset remains. `changeset version`
      consumes every pending file when it rolls, so a file left in
      .changeset/ at the merge of the version bump means the release shipped
      while the plan still held entries - a change that silently misses the
      release it was filed against. Between releases, pending changesets are
      the process working, which is why this refusal exists only when the run
      declares itself a release: `--release`. The incident behind it: dozens
      of changesets pend against a changelog whose newest entry describes a
      version nobody ever received.

  G4  CHANGELOG.md carries a dated section for the version being released --
      the one package.json declares. The incident behind it: a sibling
      repository tagged a release whose changelog section had never been
      rolled. A heading that names the version but carries no date does not
      satisfy the requirement; half-rolled is still unrolled.

  G5  (--release only) The manifest and the published tree name the same
      cards, both directions. Re-asserts O7 at the moment a version becomes
      permanent. One direction is not enough: the sibling occasions check ran
      forward-only and an undercount stayed green until August 2026. Delegated
      to validate_conformance.check_plugin_manifest rather than restated. The
      only skip is O7's own vacuum ("no published cards... checked nothing"),
      which is the seeded-fixture state; a missing skills/ directory with a
      manifest that still names cards is a real disagreement and must refuse.

  G6  (--release only) The external specification validator is clean over the
      published tree. skills-ref is the only conformance instrument here the
      maintainer did not author -- it caught two published cards with invalid
      YAML frontmatter every local gate passed. Delegated as a subprocess so
      the allowance list lives in one place. Skips a non-git tree (the
      validator enumerates via git ls-files) and when nothing is published.

  G7  (--release only) Every workflow uses: action is pinned to a full 40-hex
      commit SHA. #147 pinned every action; this keeps the pins from rotting
      back. A floating tag is not a pin. Skips when there is no workflow
      directory.

  G8  (--release only) The tag this release would create -- ``v<version>`` --
      is Semantic Versioning normal form (``X.Y.Z``, no leading zeros, no
      prerelease or build metadata). ADR 0002 made the next release take the
      normal form from ``v1.2.0`` onward, and release immutability is enabled
      on this repository: a spent tag name can never be reused, so a botched
      release spends a version number permanently and a post-hoc check cannot
      serve. The gate refuses a version that is not normal form BEFORE the tag
      is cut, blocking rather than reporting.

  G9  (--release only) The working tree is clean. A release that ships while
      the worktree carries uncommitted changes delivers something other than
      what the version bump commit recorded, so the gate refuses a dirty
      tree. Skips a tree that is not a git work tree with a HEAD commit -- a
      fixture with only ``git init`` has no committed state to dirty, and the
      live checkout is always clean by construction in CI.

Mode detection (#153):
  A release ref is one whose ``package.json`` version CHANGED relative to its
  merge-base with the default branch. The release-only checks (G3, G5, G6, G7,
  G8, G9) run when the gate declares itself a release -- either via the
  ``--release`` flag (the override a fixture or an explicit run uses) or via
  this auto-detection. Release-only checks false on an ordinary pull request:
  ``changesets consumed`` is untrue of every ordinary PR that adds a changeset,
  which is most of them, so a gate that ran them unconditionally would
  deadlock the repository. Detection compares HEAD's package.json version to
  the version at ``git merge-base HEAD <base>`` for the first resolvable base
  ref (``origin/main``, ``main``, ``origin/master``, ``master``). A tree that
  is not a git work tree, has no HEAD commit, or names no resolvable base ref
  is ordinary -- so a fixture under RUNNER_TEMP with no history stays ordinary
  unless ``--release`` forces it, which is what keeps the seeded-tree cases
  single-reason.

Generation (--write) and verification live in this one module because they
must agree about what the correct value is; two modules cannot. --write stamps
every entry from package.json, then falls through to the same verification a
plain run performs, so what it produces is verified in the same process that
produced it.

Fail-closed contract: an input that cannot be read, parsed, or trusted for
shape is a listed failure -- never a skip and never a pass.

Where it runs:

- tests.yml, a REQUIRED (blocking) status check on the default branch, on
  every pull request and push to main. The mode-awareness above is what lets
  one required gate serve both an ordinary PR (which adds a changeset) and a
  release PR (which bumps the version) without deadlocking: release-only
  checks fire solely when the version changed.
- Anywhere locally: `python scripts/release_gate.py` takes no arguments and
  returns the verdict CI prints for the same tree.

Output is ASCII-only so the Windows CI cell cannot die on a status line,
matching this repository's other validators.

Run locally: ``python scripts/release_gate.py [--root <repo-root>] [--write]
[--release]``. Exit code 0 = releasable; 1 = at least one surface is stale
(each listed).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

REPO = SCRIPT_DIR.parent
PACKAGE_REL = "package.json"
MANIFEST_REL = ".claude-plugin/marketplace.json"
CHANGELOG_REL = "CHANGELOG.md"
CHANGESET_DIR_REL = ".changeset"
CHANGESET_README = "README.md"
WORKFLOW_DIR_REL = ".github/workflows"

# Delegated predicates, imported (not restated) so the release gate's
# re-assertion cannot drift from the per-PR check it re-runs. O7 lives in
# validate_conformance; the external spec validator is its own script run as a
# subprocess below.
import validate_conformance as conformance  # noqa: E402


class ManifestShapeError(ValueError):
    """The manifest parses as JSON but is not the shape the gate reads.

    Subclasses ValueError so one handler reports it as an unreadable manifest.
    validate_conformance.py documented the alternative the hard way: a
    wrong-shaped manifest raised AttributeError out past both handlers.
    """


class ChangesetHeaderError(ValueError):
    """A changeset file carries no frontmatter the release plan can read.

    Subclasses ValueError so one handler reports it as an unassemblable plan.
    `changeset version` refuses such a file outright, so the gate refusing it
    is the same verdict earlier and cheaper.
    """


def read_json(path: Path) -> object:
    """Read and parse JSON. Raises OSError on an unreadable file and
    ValueError (JSONDecodeError) on an unparsable one -- callers fail closed."""
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_or_report(path: Path, label: str, errors: list[str]) -> object | None:
    """Read JSON fail-closed: an input this gate cannot read is a listed
    failure, never a skip. Both modes report through here so generation and
    verification cannot phrase or handle the same fault differently."""
    try:
        return read_json(path)
    except OSError as exc:
        errors.append(f"G1: {label} could not be read: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"G1: {label} is not parseable JSON: {exc}")
    except ValueError as exc:
        errors.append(
            f"G1: {label} is not a readable manifest: {exc}"
            if label == MANIFEST_REL
            else f"G1: {label} is not usable: {exc}"
        )
    return None


def plugin_entries(data: object) -> list[dict]:
    """The plugin objects of a parsed manifest, or ManifestShapeError."""
    if not isinstance(data, dict):
        raise ManifestShapeError(f"top level is {type(data).__name__}, not an object")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise ManifestShapeError(f"plugins is {type(plugins).__name__}, not an array")
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            raise ManifestShapeError(
                f"plugins[{index}] is {type(plugin).__name__}, not an object"
            )
    return plugins


def source_version(data: object) -> str:
    """The single version every manifest entry must declare."""
    if not isinstance(data, dict):
        raise ManifestShapeError(f"top level is {type(data).__name__}, not an object")
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ManifestShapeError("states no version - nothing to derive the manifest version from")
    return version


def read_package_source(root: Path, errors: list[str]) -> tuple[object | None, str | None]:
    """Read package.json once for every check that derives from it.

    Reports faults under G1, whose lockstep comparison is the primary consumer
    and whose messages this preserves byte for byte. Returns (data, version);
    either may be None when the fault is already listed -- never silently.
    """
    data = read_json_or_report(root / PACKAGE_REL, PACKAGE_REL, errors)
    version: str | None = None
    if data is not None:
        try:
            version = source_version(data)
        except ValueError as exc:
            errors.append(f"G1: {PACKAGE_REL} is not usable: {exc}")
    return data, version


def workspace_packages(root: Path, data: object) -> set[str]:
    """Every package name a changeset may legally declare: the root package
    plus any npm/Yarn workspaces members. A member whose own manifest cannot
    be read contributes no name, so changesets naming it refuse as
    out-of-workspace -- the fail-closed direction."""
    names: set[str] = set()
    if not isinstance(data, dict):
        return names
    name = data.get("name")
    if isinstance(name, str) and name.strip():
        names.add(name)
    raw = data.get("workspaces")
    patterns: list[str] = []
    if isinstance(raw, list):
        patterns = [p for p in raw if isinstance(p, str)]
    elif isinstance(raw, dict):
        packages = raw.get("packages")
        if isinstance(packages, list):
            patterns = [p for p in packages if isinstance(p, str)]
    for pattern in patterns:
        for member in sorted(root.glob(pattern)):
            member_manifest = member / "package.json"
            if not member.is_dir() or not member_manifest.is_file():
                continue
            try:
                member_data = json.loads(member_manifest.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(member_data, dict):
                member_name = member_data.get("name")
                if isinstance(member_name, str) and member_name.strip():
                    names.add(member_name)
    return names


def changeset_header_packages(text: str) -> list[str]:
    """The package names one changeset declares, in file order.

    Raises ChangesetHeaderError when there is no frontmatter block at all, it
    never closes, or it names no package -- each a file `changeset version`
    would refuse when assembling the plan.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ChangesetHeaderError("frontmatter does not open with ---")
    closing = next(
        (i for i in range(1, len(lines)) if lines[i].strip() == "---"),
        None,
    )
    if closing is None:
        raise ChangesetHeaderError("frontmatter does not close with ---")
    keys: list[str] = []
    for line in lines[1:closing]:
        match = re.match(r'^\s*("?)([^":]+?)\1\s*:', line)
        if match:
            keys.append(match.group(2))
    if not keys:
        raise ChangesetHeaderError("frontmatter names no package")
    return keys


def gate_changeset_plan(root: Path, errors: list[str], workspace: set[str] | None) -> None:
    """G2: the full pending changeset set must assemble into a release plan.

    This is the gate's own unscoped `changeset status`: it examines EVERY
    pending changeset regardless of any compared ref, which is exactly what
    the scoped `--since=origin/main` check could not do on main, where that
    set is empty. One changeset naming a package outside the workspace means
    `changeset version` will refuse to run, so no release can be cut; an
    unreadable frontmatter means the same thing by a different route. Both are
    listed failures -- never skips.

    A None workspace means package.json was already reported unreadable or
    unusable upstream; nothing here can add to that verdict.
    """
    if workspace is None:
        return
    changeset_dir = root / CHANGESET_DIR_REL
    if not changeset_dir.is_dir():
        return
    files = sorted(p for p in changeset_dir.glob("*.md") if p.name != CHANGESET_README)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"G2: {path.name} could not be read: {exc}")
            continue
        try:
            packages = changeset_header_packages(text)
        except ValueError as exc:
            errors.append(
                f"G2: release plan does not assemble - {path.name} has "
                f"unreadable frontmatter: {exc}"
            )
            continue
        for package in packages:
            if package not in workspace:
                errors.append(
                    f"G2: release plan does not assemble - {path.name} names "
                    f"{package!r}, which is not in the workspace"
                )


def gate_unconsumed_changesets(root: Path, errors: list[str]) -> None:
    """G3 (--release): every pending changeset must be consumed by release
    time.

    `changeset version` consumes what it rolls, so a file left in .changeset/
    when the version bump merges means the release shipped while the plan
    still held entries - a change that silently misses the release it was
    filed against. Between releases this state is the process working, which
    is why the refusal exists only in --release mode. .changeset/README.md is
    changesets' own documentation and never counts.
    """
    changeset_dir = root / CHANGESET_DIR_REL
    if not changeset_dir.is_dir():
        return
    pending = sorted(p.name for p in changeset_dir.glob("*.md") if p.name != CHANGESET_README)
    if not pending:
        return
    errors.append(
        f"G3: {len(pending)} unconsumed changeset(s) remain at release time - "
        "run 'changeset version' to consume them before releasing: "
        + ", ".join(pending)
    )


def gate_changelog_section(root: Path, errors: list[str], declared: str | None) -> None:
    """G4: CHANGELOG.md must carry a dated section for the released version.

    The version being released is the one package.json declares. Its changelog
    section is the record that the roll happened; the incident behind this
    check is a release tagged while its changelog section had never been
    rolled. A section that names the version under an undated heading does not
    satisfy the requirement - half-rolled is still unrolled.

    A None version means package.json was already reported unreadable or
    unusable upstream; nothing here can add to that verdict.
    """
    if declared is None:
        return
    path = root / CHANGELOG_REL
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"G4: {CHANGELOG_REL} could not be read: {exc}")
        return
    version_re = re.compile(rf"(?<![\w.])v?{re.escape(declared)}(?![\w.])")
    date_re = re.compile(r"\d{4}-\d{2}-\d{2}")
    named = [
        line
        for line in text.splitlines()
        if line.startswith("## ") and version_re.search(line)
    ]
    if not named:
        errors.append(
            f"G4: {CHANGELOG_REL} has no dated section for version {declared} - "
            "the release would ship a version whose entry was never rolled"
        )
        return
    if not any(date_re.search(line) for line in named):
        errors.append(
            f"G4: {CHANGELOG_REL} names version {declared} under a heading that "
            "carries no release date - a dated section is required"
        )


def gate_manifest_tree_agreement(root: Path, errors: list[str]) -> None:
    """G5: the manifest and the published tree name the same cards, both ways.

    Re-asserted at release (the version bump's merge, per ADR 0002) rather than
    only on the pull request that introduced the change. The predicate is O7 in
    validate_conformance, imported and called rather than restated -- one
    direction is not enough, and the repository has the receipt for why: the
    sibling occasions check ran forward-only and an UNDERCOUNT stayed green
    until August 2026, because nothing asked the reverse question. A manifest
    check that validates only the paths it names has the same hole: drop a card
    from the manifest and every named path still resolves.

    The only skip is O7's own vacuum refusal: no published cards and nothing
    named, reported as "checked nothing". That is the seeded lockstep/
    changeset/changelog fixture state, and G5 must not turn those red. A
    missing skills/ directory is NOT a skip on its own -- O7 still catches a
    manifest that names ghost paths when the tree has been deleted, and
    gating the skip on directory presence left that disagreement green.
    """
    result = conformance.check_plugin_manifest(root)
    if result.verdict != conformance.FAIL:
        return
    # O7's vacuum only: "no published cards under this root, so the manifest
    # was compared against nothing. A run that checked nothing is not a pass".
    # Any other FAIL is a real disagreement (dangling path, unexposed card,
    # off-tree entry) and must block the release.
    if "checked nothing" in result.detail:
        return
    errors.append(f"G5: {result.detail}")


SPEC_SCRIPT = SCRIPT_DIR / "validate_spec_conformance.py"


def _is_git_work_tree(root: Path) -> bool:
    """True when `git ls-files` can enumerate under `root`.

    The external spec validator discovers cards through `git ls-files` (see its
    own docstring: a filesystem walk undercounts junctions on the maintainer's
    Windows host). A tree that is not a git repository has no `git ls-files`, so
    the validator cannot enumerate, so G6 cannot re-assert it. The live checkout
    is always a git tree; a fixture under RUNNER_TEMP is not, and G6 skipping it
    is what keeps the sibling poison controls single-reason.
    """
    probe = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return probe.returncode == 0


# The release-only checks fire when the gate is in release mode. Release mode
# is declared two ways: the --release flag (an override a fixture or explicit
# run uses) and auto-detection, which treats a ref whose package.json version
# CHANGED relative to its merge-base with the default branch as a release ref.
# A tree that is not a git work tree, has no HEAD commit, or names no
# resolvable base ref is ordinary -- so a fixture under RUNNER_TEMP with no
# history stays ordinary unless --release forces it, which is what keeps the
# seeded-tree cases single-reason.
BASE_REF_CANDIDATES = ("origin/main", "origin/master", "main", "master")


def _git_ok(root: Path, args: list[str]) -> tuple[bool, str]:
    """Run a git command in `root`, returning (ok, stdout-trimmed)."""
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, proc.stdout


def detect_release_ref(root: Path, current_version: str | None) -> bool:
    """True when this ref is a release ref: the package.json version changed
    relative to the merge-base with the default branch.

    Compares `current_version` (already read from package.json by the caller)
    against the version at ``git merge-base HEAD <base>`` for the first
    resolvable base ref in BASE_REF_CANDIDATES. A release ref is one whose
    version BUMPED on this branch -- exactly the PR that delivers a new
    version per ADR 0002, which is the moment the release-only obligations
    must hold.

    Returns False (ordinary) when the tree is not a git work tree, has no
    HEAD commit, names no resolvable base ref, or the base carries no
    readable package.json version. False here is the safe default: an
    ordinary ref skips the release-only checks, and ``--release`` remains the
    explicit override for fixtures and deliberate release runs.
    """
    if current_version is None:
        return False
    head_ok, _ = _git_ok(root, ["rev-parse", "--verify", "HEAD"])
    if not head_ok:
        return False
    base_ref: str | None = None
    for candidate in BASE_REF_CANDIDATES:
        ok, _ = _git_ok(root, ["rev-parse", "--verify", candidate])
        if ok:
            base_ref = candidate
            break
    if base_ref is None:
        return False
    mb_ok, merge_base = _git_ok(root, ["merge-base", "HEAD", base_ref])
    if not mb_ok or not merge_base.strip():
        return False
    show_ok, blob = _git_ok(root, ["show", f"{merge_base.strip()}:{PACKAGE_REL}"])
    if not show_ok:
        return False
    try:
        base_data = json.loads(blob)
    except ValueError:
        return False
    if not isinstance(base_data, dict):
        return False
    base_version = base_data.get("version")
    if not isinstance(base_version, str) or not base_version.strip():
        return False
    return base_version != current_version


def gate_spec_conformance(root: Path, errors: list[str]) -> None:
    """G6: the external specification validator is clean over the published tree.

    The only conformance instrument in this repository its maintainer did not
    author, which is exactly why it caught two PUBLISHED CARDS carrying invalid
    YAML frontmatter that every repository-local gate passed. Re-asserting it
    at release runs the same command the per-PR spec-conformance job runs, so a
    direct push that bypasses that job still meets the spec before the version
    becomes permanent.

    Delegated to validate_spec_conformance.py as a subprocess (the published
    tree plus the candidate queue, with the candidate allowances the queue
    earns) rather than restated: one allowance list, one place. Skips when
    nothing is published, and when the tree is not a git repository the
    validator cannot enumerate -- the live run is a git checkout, so the skip
    only ever applies to fixtures.
    """
    if not (root / "skills").is_dir():
        return
    if not _is_git_work_tree(root):
        return
    if not SPEC_SCRIPT.is_file():
        errors.append(
            "G6: scripts/validate_spec_conformance.py is absent - the external "
            "spec validator cannot run, so the published tree is unverified"
        )
        return
    proc = subprocess.run(
        [sys.executable, str(SPEC_SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        output = proc.stdout + proc.stderr
        # The validator prints one `BREACH <path>: <error>` line per violation;
        # surfacing those names the offending card and the class (the two live
        # cards rejected on 2026-08-24 failed as `Invalid YAML in frontmatter`).
        # When it could not run at all (no npx) it prints no BREACH lines, so the
        # REJECTED summary carries its own reason instead.
        breaches = [ln.strip() for ln in output.splitlines() if ln.strip().startswith("BREACH")]
        if breaches:
            detail = "; ".join(breaches[:5])
        else:
            lines = output.strip().splitlines()
            detail = lines[-1] if lines else "(no output)"
        errors.append(
            "G6: external specification validator did not pass over the "
            f"published tree: {detail}"
        )


USES_RE = re.compile(r"^\s*-?\s*uses:\s+(.+?)\s*$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _uses_value(raw: str) -> str:
    """One `uses:` scalar with its trailing comment stripped and quotes removed.

    `actions/checkout@<sha> # v4` is the house pinning style; the version lives
    in a comment so a reader can follow it while the action is locked to a SHA.
    Stripping the comment is what lets G7 read the ref a reader would type, not
    the annotation beside it.
    """
    value = re.sub(r"\s+#.*$", "", raw).strip()
    if value and value[0] in "\"'" and value[-1] == value[0]:
        value = value[1:-1]
    return value


def gate_workflow_pins(root: Path, errors: list[str]) -> None:
    """G7: every workflow `uses:` action is pinned to a full 40-hex commit SHA.

    #147 pinned every action; this keeps #147 from rotting back. A floating tag
    is not a pin (CVE-2025-30066 repointed every tj-actions/changed-files tag
    from v1 to v45 inside 24 hours), so any `uses:` whose ref is not a 40-hex
    SHA is a listed failure naming the file, the line, and the mutable ref. A
    local action (`./...` with no `@`) is repo code pinned by the commit, so it
    is not in scope.

    Skips when there is no workflow directory. Reads workflows as text because
    the ref is a scalar on one line; the repo's workflows all pin inline.
    """
    workflow_dir = root / WORKFLOW_DIR_REL
    if not workflow_dir.is_dir():
        return
    for path in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"G7: {path.name} could not be read: {exc}")
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            match = USES_RE.match(line)
            if not match:
                continue
            value = _uses_value(match.group(1))
            if "@" not in value:
                continue  # a local action, pinned by the commit
            ref = value.rsplit("@", 1)[1]
            if not SHA_RE.fullmatch(ref):
                rel = path.relative_to(root).as_posix()
                errors.append(
                    f"G7: {rel}:{lineno} uses a mutable ref, not a pinned commit "
                    f"SHA: {value}"
                )


# Semantic Versioning 2.0.0 normal form: MAJOR.MINOR.PATCH, each a non-negative
# integer with NO leading zeros, and nothing else -- no prerelease, no build
# metadata. ADR 0002 takes the normal form from the next release onward, so the
# tag this release cuts (v<version>) must round-trip through this.
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def gate_tag_normal_form(root: Path, errors: list[str], declared: str | None) -> None:
    """G8 (--release): the tag this release cuts is Semantic Versioning normal form.

    The tag name is ``v`` + the package.json version, so the version being
    normal form is the whole requirement -- a non-normal version produces a tag
    that is not ``vX.Y.Z``. Release immutability is enabled on this repository
    and a spent tag name can never be reused, so the gate refuses BEFORE the
    tag is cut, blocking rather than reporting: a botched release spends a
    version number permanently and a post-hoc check cannot recover it.

    A None version means package.json was already reported unreadable or
    unusable upstream; nothing here can add to that verdict.
    """
    if declared is None:
        return
    if not SEMVER_RE.fullmatch(declared):
        errors.append(
            f"G8: the release tag v{declared} is not Semantic Versioning normal "
            "form (X.Y.Z, no leading zeros, no prerelease or build metadata) - "
            "release immutability means a malformed tag cannot be re-cut later"
        )


def gate_clean_tree(root: Path, errors: list[str]) -> None:
    """G9 (--release): the working tree is clean at release time.

    A release that ships while the worktree carries uncommitted changes
    delivers something other than what the version bump commit recorded. The
    gate refuses a dirty tree. Skips a tree that is not a git work tree with a
    HEAD commit: a fixture with only ``git init`` (no commit) has no committed
    state to dirty, and the live checkout is always clean by construction in
    CI. The skip is what keeps the seeded-tree and G6-fixture cases
    single-reason.
    """
    head_ok, _ = _git_ok(root, ["rev-parse", "--verify", "HEAD"])
    if not head_ok:
        return
    status_ok, status = _git_ok(root, ["status", "--porcelain"])
    if not status_ok:
        # A git tree whose status cannot be read is a fail-closed input, not a
        # skip -- the gate cannot assert the tree is clean it cannot inspect.
        errors.append("G9: the working tree status could not be read")
        return
    if status.strip():
        dirty = [ln.strip() for ln in status.splitlines() if ln.strip()]
        preview = "; ".join(dirty[:5])
        errors.append(
            "G9: the working tree is not clean at release time - "
            f"{len(dirty)} uncommitted change(s): {preview}"
        )


def gate_manifest_version_lockstep(
    root: Path,
    errors: list[str],
    declared: str | None,
) -> str | None:
    """G1: manifest entry versions and package.json agree, both directions.

    `declared` comes from the shared package.json read; None means that read
    already reported its fault and there is nothing to compare against. Reads
    the manifest independently so one unreadable file still lets the other
    side report everything wrong with itself; every finding lands in `errors`
    because the gate reports EVERY failure in one run. Returns the declared
    version, or None when nothing derivable was read.
    """
    manifest_data = read_json_or_report(root / MANIFEST_REL, MANIFEST_REL, errors)
    if manifest_data is None:
        return declared
    try:
        entries = plugin_entries(manifest_data)
    except ValueError as exc:
        errors.append(f"G1: {MANIFEST_REL} is not a readable manifest: {exc}")
        return declared

    if not entries:
        errors.append(
            f"G1: {MANIFEST_REL} declares no plugin entries - a run that "
            "checked nothing is not a pass"
        )
        return declared

    for index, entry in enumerate(entries):
        name = entry.get("name", f"plugins[{index}]")
        entry_version = entry.get("version")
        if not isinstance(entry_version, str) or not entry_version.strip():
            errors.append(
                f"G1: version drift - {MANIFEST_REL} plugin {name!r} declares "
                "no version"
                + (f" (package.json declares {declared})" if declared else "")
            )
        elif declared is not None and entry_version != declared:
            errors.append(
                f"G1: version drift - {MANIFEST_REL} plugin {name!r} declares "
                f"{entry_version} but {PACKAGE_REL} declares {declared}"
            )
    return declared


def write_manifest_versions(root: Path, errors: list[str]) -> bool:
    """--write: stamp every plugin entry with the package.json version.

    Returns True when the manifest on disk now derives from package.json.
    Nothing is written unless every input read cleanly: a partial write would
    leave the surface half-generated, which is the state this gate exists to
    refuse.
    """
    data = read_json_or_report(root / PACKAGE_REL, PACKAGE_REL, errors)
    if data is None:
        return False
    try:
        version = source_version(data)
    except ValueError as exc:
        errors.append(f"G1: {PACKAGE_REL} is not usable: {exc}")
        return False

    path = root / MANIFEST_REL
    manifest_data = read_json_or_report(path, MANIFEST_REL, errors)
    if manifest_data is None:
        return False
    try:
        entries = plugin_entries(manifest_data)
    except ValueError as exc:
        errors.append(f"G1: {MANIFEST_REL} is not a readable manifest: {exc}")
        return False
    if not entries:
        errors.append(
            f"G1: {MANIFEST_REL} declares no plugin entries - a run that "
            "checked nothing is not a pass"
        )
        return False

    stale = [entry for entry in entries if entry.get("version") != version]
    if not stale:
        print(
            f"RELEASE GATE: WRITE - {MANIFEST_REL} already derives from "
            f"{PACKAGE_REL}; no change written."
        )
        return True

    for entry in entries:
        entry["version"] = version
    path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"RELEASE GATE: WRITE - set version {version} on {len(stale)} "
        f"plugin entry/entries in {MANIFEST_REL}."
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Release gate - refuses a release whose public surfaces have gone stale."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO,
        help="repo root to check (default: this script's repo)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"generate every {MANIFEST_REL} plugin version from {PACKAGE_REL}, then verify",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="force release mode: run the release-time checks (G3 unconsumed "
        "changesets, G5 manifest/tree, G6 external spec validator, G7 workflow "
        "pins, G8 tag normal form, G9 clean tree) in addition to the everyday "
        "ones. Without --release the gate auto-detects release mode: a ref "
        "whose package.json version changed relative to its merge-base with "
        "the default branch is a release ref and runs the release-time checks "
        "anyway. The flag is the override a fixture or an explicit run uses; "
        "an ordinary ref (version unchanged) answers 'are the surfaces "
        "healthy today', a release ref answers 'may this version ship'.",
    )
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()

    errors: list[str] = []
    if args.write and not write_manifest_versions(root, errors):
        print(f"RELEASE GATE: BLOCKED - {len(errors)} stale surface(s):")
        for error in errors:
            print(f"  FAIL  {error}")
        return 1

    package_data, declared = read_package_source(root, errors)
    workspace = workspace_packages(root, package_data) if package_data is not None else None
    version = gate_manifest_version_lockstep(root, errors, declared) or "unknown"
    gate_changeset_plan(root, errors, workspace)
    gate_changelog_section(root, errors, declared)
    # Release mode is declared two ways: the --release flag (an override a
    # fixture or explicit run uses) and auto-detection, which treats a ref
    # whose package.json version changed relative to its merge-base with the
    # default branch as a release ref. Release-only checks false on an
    # ordinary PR that adds a changeset, which is most PRs -- running them
    # unconditionally would deadlock the repository.
    release_mode = args.release or detect_release_ref(root, declared)
    if release_mode:
        gate_unconsumed_changesets(root, errors)
        gate_manifest_tree_agreement(root, errors)
        gate_spec_conformance(root, errors)
        gate_workflow_pins(root, errors)
        gate_tag_normal_form(root, errors, declared)
        gate_clean_tree(root, errors)

    if errors:
        print(f"RELEASE GATE: BLOCKED - {len(errors)} stale surface(s) at version {version}:")
        for error in errors:
            print(f"  FAIL  {error}")
        return 1
    if release_mode:
        print(
            f"RELEASE GATE: PASS - releasable at version {version}: plugin "
            f"versions in lockstep with {PACKAGE_REL}, release plan assembles, "
            "changelog section dated, no unconsumed changesets, manifest and "
            "published tree agree, external spec validator clean, workflow "
            "actions pinned, release tag is SemVer normal form, working tree "
            "clean."
        )
    else:
        print(
            f"RELEASE GATE: PASS - surfaces healthy at version {version}: "
            f"plugin versions in lockstep with {PACKAGE_REL}, release plan "
            "assembles, changelog section dated."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
