"""Check what readers outside the repository see of the current release.

Run: python scripts/check_release_public.py
Run it as the last release step, after the tag is pushed. It exits 1 and names the fix for
each gap, and exits 0 only when every public surface carries the release in package.json:

- the tag v<version> exists on origin and points at a commit on main;
- every v* tag has a published GitHub Release, and v<version> is the one marked Latest;
- the newest Pages deploy ran on the last main commit that touched site/, and succeeded.

The marketplace pin has its own check, scripts/check_marketplace_pin.py. The skills.sh
listing and the repository social preview have no API this script can read, so it prints
them as manual steps on every run.
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
REPO = "MrBinnacle/skills"
Run = Callable[[list[str]], str]

MANUAL = [
    "Compare https://www.skills.sh/MrBinnacle/skills with the folders under skills/<bucket>/; "
    "give each stale name a row in RETIRED.md (AGENTS.md, after the release merges).",
    "Check the repository social preview in Settings, General, Social preview (#481).",
]


def sh(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def tags(run: Run) -> dict[str, str]:
    """Map each v* tag on origin to the commit it names, peeling annotated tags."""
    out: dict[str, str] = {}
    for line in run(["git", "ls-remote", "--tags", "origin", "v*"]).splitlines():
        sha, ref = line.split("\t")
        name = ref.removeprefix("refs/tags/")
        if name.endswith("^{}"):
            out[name[:-3]] = sha
        else:
            out.setdefault(name, sha)
    return out


def check(version: str, run: Run) -> list[str]:
    gaps: list[str] = []
    tag = f"v{version}"
    found = tags(run)
    if tag not in found:
        gaps.append(f"{tag} is not tagged on origin: tag the release squash commit and push the tag.")
    else:
        try:
            run(["git", "merge-base", "--is-ancestor", found[tag], "origin/main"])
        except RuntimeError:
            gaps.append(f"{tag} names {found[tag][:7]}, which is not on main: tag the squash commit on main.")
    releases = {r["tagName"]: r for r in json.loads(run(
        ["gh", "release", "list", "--repo", REPO, "--limit", "200", "--json", "tagName,isDraft,isLatest"]))}
    for name in sorted(found):
        r = releases.get(name)
        if r is None:
            gaps.append(f"{name} has no GitHub Release: gh release create {name} --notes-file <its CHANGELOG section>.")
        elif r["isDraft"]:
            gaps.append(f"{name}'s GitHub Release is a draft: publish it.")
    latest = [n for n, r in releases.items() if r.get("isLatest")]
    if tag in found and latest != [tag]:
        gaps.append(f"GitHub marks {latest[0] if latest else 'no release'} as Latest, not {tag}: gh release edit {tag} --latest.")
    site = run(["git", "log", "-1", "--format=%H", "origin/main", "--", "site"])
    runs = json.loads(run(["gh", "run", "list", "--repo", REPO, "--workflow", "pages.yml", "--branch", "main",
                           "--limit", "1", "--json", "headSha,conclusion"]))
    if site and (not runs or runs[0]["headSha"] != site or runs[0]["conclusion"] != "success"):
        seen = f"{runs[0]['headSha'][:7]} ({runs[0]['conclusion'] or 'running'})" if runs else "none"
        gaps.append(f"The site's last change {site[:7]} is not deployed (newest Pages run: {seen}): "
                    "run the Pages workflow on main and wait for it to succeed.")
    return gaps


def main() -> int:
    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    gaps = check(version, sh)
    for gap in gaps:
        print("FAIL ", gap)
    for step in MANUAL:
        print("CHECK", step)
    print(f"public release check: {'PASS' if not gaps else f'{len(gaps)} gap(s)'} at v{version}")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
