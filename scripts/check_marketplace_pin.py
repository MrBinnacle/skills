#!/usr/bin/env python3
"""Marketplace pin check -- a fresh install receives the latest release (#444).

Why this exists: a relative-path plugin source resolves to whatever the
default branch holds, so a fresh install received `main`'s tip under the
version label of the last release. Each entry in
.claude-plugin/marketplace.json is now a `git-subdir` source that pins the
release commit by `ref` (the tag) and `sha` (the commit). A squash-merged
commit cannot contain its own SHA, so the pin lands as a separate commit after
the release merges (ADR 0002, 2026-10-20 append). This script asserts the pin
and, with --write, generates it. A 40-hex SHA typed by hand into three entries
is the hand-kept copy of a derived value ADR 0002 rules out.

The latest release is the newest commit on HEAD's first-parent history whose
package.json version differs from its first parent's. Every entry must name:

  - `"source": "git-subdir"` and the HTTPS URL of `repository.url` in
    package.json, with `.git` (the `owner/repo` form needs SSH, #333);
  - `sha` equal to the latest release commit, and `ref` equal to
    `v<version at that commit>`; the tag, when it resolves, must be that commit;
  - a `path` whose `.claude-plugin/plugin.json` at that commit carries the
    entry's name and the version package.json declares.

Three states, by where the latest release commit sits:

  - Ordinary tree (the release is on the base branch, HEAD past it): the pin
    must name that release. Green after the pin commit lands.
  - Release ref (the release commit is not on the base branch yet: a release
    PR's merge commit, or a local release branch): the pin still names the
    previous release, because the new commit does not exist on main yet.
  - Between the release squash and the pin commit, every run is RED, by
    design. A push of the release commit to main, and every PR opened before
    the pin lands, is refused until the pin commit merges. That refusal is the
    forcing function for "a release ships with its pin commit missing".

Run: python scripts/check_marketplace_pin.py [--root <repo>] [--write]
Exit 0 = pinned; 1 = refused (each reason listed).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_conformance import local_source  # noqa: E402

REPO = SCRIPT_DIR.parent
MANIFEST_REL = ".claude-plugin/marketplace.json"
PLUGIN_MANIFEST_REL = ".claude-plugin/plugin.json"
BASE_REFS = ("origin/main", "main")
FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")


class PinError(Exception):
    """An input the check cannot read; reported as a refusal, never a pass."""


@dataclass(frozen=True)
class Release:
    sha: str
    version: str
    pending: bool


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        raise PinError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def git_ok(root: Path, *args: str) -> bool:
    try:
        git(root, *args)
    except PinError:
        return False
    return True


def json_at(root: Path, rev: str, rel: str) -> dict:
    try:
        data = json.loads(git(root, "show", f"{rev}:{rel}"))
    except ValueError as exc:
        raise PinError(f"{rel} at {rev[:12]} is not JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PinError(f"{rel} at {rev[:12]} is not an object")
    return data


def version_at(root: Path, rev: str) -> str | None:
    try:
        return json_at(root, rev, "package.json").get("version")
    except PinError:
        return None


def latest_release(root: Path, rev: str) -> str | None:
    """Newest first-parent commit at or before `rev` that changed the version."""
    for commit in git(root, "rev-list", "--first-parent", rev, "--", "package.json").split():
        parent = f"{commit}^1"
        before = version_at(root, parent) if git_ok(root, "rev-parse", "--verify", "-q", parent) else None
        if before != version_at(root, commit):
            return commit
    return None


def base_ref(root: Path) -> str:
    for ref in BASE_REFS:
        if git_ok(root, "rev-parse", "--verify", "-q", ref):
            return ref
    raise PinError(f"no base branch resolves (tried {', '.join(BASE_REFS)})")


def expected_release(root: Path) -> Release:
    """The release the pin must name, and whether HEAD is an unmerged release."""
    latest = latest_release(root, "HEAD")
    if latest is None:
        raise PinError("HEAD's first-parent history holds no release commit")
    pending = not git_ok(root, "merge-base", "--is-ancestor", latest, base_ref(root))
    if pending:
        previous = latest_release(root, f"{latest}^1")
        if previous is None:
            raise PinError(f"release {latest[:12]} has no earlier release to stay pinned to")
        latest = previous
    version = version_at(root, latest)
    if not version:
        raise PinError(f"package.json at {latest[:12]} declares no version")
    return Release(latest, version, pending)


def repo_url(root: Path) -> str:
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    url = (package.get("repository") or {}).get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise PinError("package.json repository.url is not an HTTPS URL")
    return url if url.endswith(".git") else f"{url}.git"


def read_manifest(root: Path) -> dict:
    data = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
    plugins = data.get("plugins") if isinstance(data, dict) else None
    if not isinstance(plugins, list) or not plugins:
        raise PinError(f"{MANIFEST_REL} declares no plugin entries")
    return data


def entry_errors(root: Path, entry: dict, release: Release, url: str) -> list[str]:
    name = entry.get("name")
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "git-subdir":
        return [f"{name}: source {source!r} is not a git-subdir pin"]
    errors: list[str] = []
    if source.get("url") != url:
        errors.append(f"{name}: url {source.get('url')!r} is not {url!r}")
    sha, ref = source.get("sha"), source.get("ref")
    if sha != release.sha:
        errors.append(f"{name}: sha {sha!r} is not the latest release commit {release.sha}")
    if ref != f"v{release.version}":
        errors.append(f"{name}: ref {ref!r} is not 'v{release.version}'")
    elif git_ok(root, "rev-parse", "--verify", "-q", f"refs/tags/{ref}"):
        tagged = git(root, "rev-parse", f"refs/tags/{ref}^{{commit}}")
        if tagged != sha:
            errors.append(f"{name}: tag {ref} is commit {tagged}, not sha {sha}")
    errors.extend(plugin_errors(root, name, source.get("path"), release))
    return errors


def plugin_errors(root: Path, name: object, path: object, release: Release) -> list[str]:
    if not isinstance(path, str) or not path:
        return [f"{name}: path {path!r} names no bucket"]
    try:
        plugin = json_at(root, release.sha, f"{path}/{PLUGIN_MANIFEST_REL}")
    except PinError as exc:
        return [f"{name}: {exc}"]
    errors = []
    if plugin.get("name") != name:
        errors.append(f"{name}: {path}/{PLUGIN_MANIFEST_REL} at the pin is named {plugin.get('name')!r}")
    if plugin.get("version") != release.version:
        errors.append(
            f"{name}: {path}/{PLUGIN_MANIFEST_REL} at the pin declares "
            f"{plugin.get('version')!r}, package.json there declares {release.version}"
        )
    return errors


def check(root: Path) -> tuple[Release, list[str]]:
    release = expected_release(root)
    url = repo_url(root)
    errors = [e for entry in read_manifest(root)["plugins"] for e in entry_errors(root, entry, release, url)]
    declared = json.loads((root / "package.json").read_text(encoding="utf-8")).get("version")
    if not release.pending and declared != release.version:
        errors.append(f"package.json declares {declared}, the pinned release is {release.version}")
    return release, errors


def bucket_path(source: object) -> str:
    path = local_source(source)
    if path is None:
        raise PinError(f"source {source!r} names no bucket path")
    return path.removeprefix("./")


def write(root: Path) -> str:
    release = expected_release(root)
    if release.pending:
        raise PinError("HEAD's release is not on the base branch yet; merge it, then --write")
    data = read_manifest(root)
    url = repo_url(root)
    sources = []
    for entry in data["plugins"]:
        entry["source"] = {
            "source": "git-subdir",
            "url": url,
            "path": bucket_path(entry.get("source")),
            "ref": f"v{release.version}",
            "sha": release.sha,
        }
        sources.append(entry["source"])
        entry["source"] = f"@@SOURCE{len(sources) - 1}@@"
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    # One line per source keeps the line numbers other documents cite.
    for index, source in enumerate(sources):
        text = text.replace(f'"@@SOURCE{index}@@"', json.dumps(source, separators=(", ", ": ")))
    (root / MANIFEST_REL).write_text(text, encoding="utf-8", newline="\n")
    return f"v{release.version} {release.sha}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--write", action="store_true", help="stamp the pin from the latest release")
    args = parser.parse_args(argv)
    try:
        if args.write:
            print(f"MARKETPLACE PIN: WRITE - pinned every entry to {write(args.root)}")
        release, errors = check(args.root)
    except (PinError, OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print(f"MARKETPLACE PIN: BLOCKED - {len(errors)} reason(s):")
        for error in errors:
            print(f"  FAIL  {error}")
        return 1
    state = " (release ref: the pin stays on the previous release until this merges)" if release.pending else ""
    print(f"MARKETPLACE PIN: PASS - every entry pins v{release.version} {release.sha}{state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
