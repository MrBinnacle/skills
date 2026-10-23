#!/usr/bin/env python3
"""Suite for scripts/check_marketplace_pin.py (#444).

Each case builds a throwaway git repository with a release history, writes a
marketplace pin, and runs the check as CI does. The states the check must tell
apart:

  - the pin names the latest release on main: green;
  - the pin names the wrong commit, an unpinned relative source, the SSH form,
    or a tag that points elsewhere: red, each for its own reason;
  - a release branch not yet on main, pin still on the previous release: green;
  - main holds the release commit but not the pin commit yet: RED, by design.
    Every run in that window is refused until the pin lands;
  - an entry added since the release, whose path the release lacks, pinned to
    that release: green, reported as entering (ADR 0009);
  - an entry the release already lists whose path it lacks: red;
  - --write on main after the release merges stamps the new pin: green.

Run directly:  python scripts/test_check_marketplace_pin.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_marketplace_pin.py"
URL = "https://github.com/example/skills.git"
FAILURES: list[str] = []


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def commit_version(root: Path, version: str, message: str) -> str:
    write_json(root / "package.json", {"name": "fixture", "version": version,
                                       "repository": {"url": URL.removesuffix(".git")}})
    write_json(root / "skills/alpha/.claude-plugin/plugin.json", {"name": "alpha", "version": version})
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")


def pin(root: Path, sha: str, ref: str, *, url: str = URL) -> None:
    source = {"source": "git-subdir", "url": url, "path": "skills/alpha", "ref": ref, "sha": sha}
    write_json(root / ".claude-plugin/marketplace.json", {"name": "fixture", "plugins": [
        {"name": "alpha", "source": source}]})


def pin_with_new(root: Path, sha: str, ref: str, new_path: str) -> None:
    pin(root, sha, ref)
    data = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    data["plugins"].append({"name": "beta", "source": {
        "source": "git-subdir", "url": URL, "path": new_path, "ref": ref, "sha": sha}})
    write_json(root / ".claude-plugin/marketplace.json", data)


def make_repo(tmp: Path) -> tuple[Path, str, str]:
    """main: 1.0.0 -> release 1.1.0 (tagged) -> a card commit. Returns root, c0, release."""
    root = tmp / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "fixture")
    git(root, "config", "core.autocrlf", "false")
    first = commit_version(root, "1.0.0", "initial")
    release = commit_version(root, "1.1.0", "chore(release): v1.1.0")
    git(root, "tag", "v1.1.0")
    (root / "skills/alpha/SKILL.md").write_text("card change past the release\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "card change")
    return root, first, release


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True)


def expect(case: str, proc: subprocess.CompletedProcess[str], ok: bool, needle: str) -> None:
    out = proc.stdout + proc.stderr
    if (proc.returncode == 0) == ok and needle in out:
        print(f"ok   {case}")
        return
    print(f"FAIL {case}: exit {proc.returncode}, wanted {needle!r} in:\n{out}")
    FAILURES.append(case)


def cases(tmp: Path) -> None:
    root, first, release = make_repo(tmp)

    pin(root, release, "v1.1.0")
    expect("right sha on main is green", run(root), True, f"pins v1.1.0 {release}")

    pin(root, first, "v1.1.0")
    expect("wrong sha is red", run(root), False, f"is not the latest release commit {release}")

    write_json(root / ".claude-plugin/marketplace.json",
               {"plugins": [{"name": "alpha", "source": "./skills/alpha"}]})
    expect("relative source is red", run(root), False, "is not a git-subdir pin")

    pin(root, release, "v1.1.0", url="example/skills")
    expect("owner/repo url is red", run(root), False, "url 'example/skills' is not")

    git(root, "tag", "v1.0.0", first)
    pin(root, release, "v1.0.0")
    expect("ref naming another release is red", run(root), False, "ref 'v1.0.0' is not 'v1.1.0'")

    git(root, "tag", "-f", "v1.1.0", first)
    pin(root, release, "v1.1.0")
    expect("tag pointing elsewhere is red", run(root), False, f"tag v1.1.0 is commit {first}")
    git(root, "tag", "-f", "v1.1.0", release)

    pin_with_new(root, release, "v1.1.0", "mods/beta")
    expect("entry added since the release is entering, not red", run(root), True,
           "entering at the next release, installs nothing yet: beta")
    pin(root, release, "v1.1.0")

    git(root, "switch", "-q", "-c", "release")
    commit_version(root, "1.2.0", "chore(release): v1.2.0")
    pin(root, release, "v1.1.0")
    expect("release ref keeps the previous pin green", run(root), True, "release ref")

    git(root, "switch", "-q", "main")
    git(root, "merge", "-q", "--ff-only", "release")
    expect("release merged without its pin is red", run(root), False, "is not the latest release commit")

    new_release = git(root, "rev-parse", "HEAD")
    git(root, "tag", "v1.2.0")
    expect("--write after the release merges is green", run(root, "--write"), True,
           f"pins v1.2.0 {new_release}")

    pin_with_new(root, new_release, "v1.2.0", "mods/beta")
    listed = commit_version(root, "1.3.0", "chore(release): v1.3.0 lists beta")
    git(root, "tag", "v1.3.0")
    pin_with_new(root, listed, "v1.3.0", "mods/beta")
    expect("entry the release already lists cannot claim entering", run(root), False,
           "beta: git show")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        cases(Path(tmp))
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        return 1
    print("PASS: marketplace pin check refuses every stale pin and accepts the release states")
    return 0


if __name__ == "__main__":
    sys.exit(main())
