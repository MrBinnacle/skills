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

Run locally: ``python scripts/release_gate.py [--root <repo-root>] [--write]``.
Exit code 0 = releasable; 1 = at least one surface is stale (each listed).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE_REL = "package.json"
MANIFEST_REL = ".claude-plugin/marketplace.json"


class ManifestShapeError(ValueError):
    """The manifest parses as JSON but is not the shape the gate reads.

    Subclasses ValueError so one handler reports it as an unreadable manifest.
    validate_conformance.py documented the alternative the hard way: a
    wrong-shaped manifest raised AttributeError out past both handlers.
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


def gate_manifest_version_lockstep(root: Path, errors: list[str]) -> str | None:
    """G1: manifest entry versions and package.json agree, both directions.

    Reads each input independently so one unreadable file still lets the other
    side report everything wrong with itself; every finding lands in `errors`
    because the gate reports EVERY failure in one run. Returns the derived
    version, or None when nothing derivable was read.
    """
    version: str | None = None
    data = read_json_or_report(root / PACKAGE_REL, PACKAGE_REL, errors)
    if data is not None:
        try:
            version = source_version(data)
        except ValueError as exc:
            errors.append(f"G1: {PACKAGE_REL} is not usable: {exc}")

    manifest_data = read_json_or_report(root / MANIFEST_REL, MANIFEST_REL, errors)
    if manifest_data is None:
        return version
    try:
        entries = plugin_entries(manifest_data)
    except ValueError as exc:
        errors.append(f"G1: {MANIFEST_REL} is not a readable manifest: {exc}")
        return version

    if not entries:
        errors.append(
            f"G1: {MANIFEST_REL} declares no plugin entries - a run that "
            "checked nothing is not a pass"
        )
        return version

    for index, entry in enumerate(entries):
        name = entry.get("name", f"plugins[{index}]")
        declared = entry.get("version")
        if not isinstance(declared, str) or not declared.strip():
            errors.append(
                f"G1: version drift - {MANIFEST_REL} plugin {name!r} declares "
                "no version"
                + (f" (package.json declares {version})" if version else "")
            )
        elif version is not None and declared != version:
            errors.append(
                f"G1: version drift - {MANIFEST_REL} plugin {name!r} declares "
                f"{declared} but {PACKAGE_REL} declares {version}"
            )
    return version


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
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()

    errors: list[str] = []
    if args.write:
        if not write_manifest_versions(root, errors):
            version = "unknown"
            print(f"RELEASE GATE: BLOCKED - {len(errors)} stale surface(s):")
            for error in errors:
                print(f"  FAIL  {error}")
            return 1

    version = gate_manifest_version_lockstep(root, errors)

    if errors:
        print(f"RELEASE GATE: BLOCKED - {len(errors)} stale surface(s) at version {version or 'unknown'}:")
        for error in errors:
            print(f"  FAIL  {error}")
        return 1
    print(
        f"RELEASE GATE: PASS - plugin versions in lockstep with {PACKAGE_REL} "
        f"at version {version}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
