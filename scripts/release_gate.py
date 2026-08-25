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

Generation (--write) and verification live in this one module because they
must agree about what the correct value is; two modules cannot. --write stamps
every entry from package.json, then falls through to the same verification a
plain run performs, so what it produces is verified in the same process that
produced it.

Fail-closed contract: an input that cannot be read, parsed, or trusted for
shape is a listed failure -- never a skip and never a pass.

Where it runs:

- tests.yml, a NON-BLOCKING job on every pull request and push to main.
  Non-blocking while the tracer matures: the blocking pre-publication gate
  ADR 0002 owes lands with the release pipeline, not with this ticket.
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
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE_REL = "package.json"
MANIFEST_REL = ".claude-plugin/marketplace.json"
CHANGELOG_REL = "CHANGELOG.md"
CHANGESET_DIR_REL = ".changeset"
CHANGESET_README = "README.md"


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
        help="run the release-time checks as well: refuse while unconsumed "
        "changesets remain (G3). The argument-less run answers 'are the "
        "surfaces healthy today'; this one answers 'may this version ship'.",
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
    if args.release:
        gate_unconsumed_changesets(root, errors)

    if errors:
        print(f"RELEASE GATE: BLOCKED - {len(errors)} stale surface(s) at version {version}:")
        for error in errors:
            print(f"  FAIL  {error}")
        return 1
    if args.release:
        print(
            f"RELEASE GATE: PASS - releasable at version {version}: plugin "
            f"versions in lockstep with {PACKAGE_REL}, release plan assembles, "
            "changelog section dated, no unconsumed changesets."
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
