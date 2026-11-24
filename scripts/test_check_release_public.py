#!/usr/bin/env python3
"""Suite for scripts/check_release_public.py.

Each case feeds the check a fake git and gh, so no network is used. The states it must
tell apart:

  - everything public carries the release: green;
  - the tag is missing, or names a commit off main: red;
  - a v* tag has no GitHub Release, or only a draft: red, one gap per tag;
  - another release is marked Latest: red;
  - the newest Pages run is before the last commit pages.yml deploys on, or it failed: red;
  - a Pages run at a later commit, such as a manual run, deploys the site: green;
  - a repository with nothing pages.yml deploys: green;
  - a change to another path pages.yml deploys, such as the favicon, is not yet deployed: red;
  - an annotated tag is read by the commit it peels to;
  - GitHub serves assets/social-preview.png as the social preview: green;
  - it serves other bytes, or a generated preview: red, naming the upload as the fix;
  - the served image cannot be downloaded: red, not a traceback;
  - PAGES_PATHS names exactly the paths pages.yml deploys on, so no deployed file escapes the check;
  - the newest Pi install receipt tested the README's Pi pin: green; another pin, or no receipt: red;
    a README with no Pi command: green.

Run directly:  python scripts/test_check_release_public.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_release_public import PAGES_PATHS, PREVIEW, ROOT, check, pi_receipt_gaps  # noqa: E402

OURS = PREVIEW.read_bytes()
QUERY = 'query={repository(owner:"MrBinnacle",name:"skills"){openGraphImageUrl usesCustomOpenGraphImage}}'

GOOD = {
    "tags": "aaa\trefs/tags/v1.0.0\nbbb\trefs/tags/v1.1.0",
    "releases": [{"tagName": "v1.0.0", "isDraft": False, "isLatest": False},
                 {"tagName": "v1.1.0", "isDraft": False, "isLatest": True}],
    "on_main": {"aaa", "bbb", "ppp"},
    "site": "sss",
    "favicon": "",
    "pages": [{"headSha": "sss", "conclusion": "success"}],
    "after": {("sss", "sss"), ("sss", "later")},
    "custom": True,
    "served": OURS,
}


def fake(state: dict):
    def run(cmd: list[str]) -> str:
        if cmd[:2] == ["git", "ls-remote"]:
            return state["tags"]
        if cmd[:2] == ["git", "merge-base"]:
            if cmd[4] == "origin/main" and cmd[3] in state["on_main"]:
                return ""
            if cmd[4] != "origin/main" and (cmd[3], cmd[4]) in state["after"]:
                return ""
            raise RuntimeError("not an ancestor")
        if cmd[:3] == ["gh", "release", "list"]:
            return json.dumps(state["releases"])
        if cmd[:2] == ["git", "log"]:
            # The newest commit among the paths asked about; "favicon" is newer than "site".
            return state["favicon"] if "assets/favicon.svg" in cmd and state["favicon"] else state["site"]
        if cmd[:3] == ["gh", "run", "list"]:
            return json.dumps(state["pages"])
        if cmd[:3] == ["gh", "api", "graphql"]:
            assert cmd[-1] == QUERY, cmd[-1]  # this repository, both fields
            return json.dumps({"data": {"repository": {
                "openGraphImageUrl": "https://og.example/img", "usesCustomOpenGraphImage": state["custom"]}}})
        raise AssertionError(f"unexpected command {cmd}")
    return run


def make_root(readme: str, receipts: dict[str, str]) -> Path:
    """A repository root holding only a README and the named receipt files."""
    root = Path(tempfile.mkdtemp())
    (root / "README.md").write_text(readme, encoding="utf-8")
    (root / "docs" / "product" / "receipts").mkdir(parents=True)
    for name, text in receipts.items():
        (root / "docs" / "product" / "receipts" / name).write_text(text, encoding="utf-8")
    return root


def listed_backwards(root: Path) -> list[str]:
    """Run the check while the disk lists files in reverse name order, as ext4 may."""
    real = Path.glob
    Path.glob = lambda self, pattern: reversed(sorted(real(self, pattern)))
    try:
        return gaps(root=root)
    finally:
        Path.glob = real


def gaps(root: Path | None = None, **change) -> list[str]:
    state = {**GOOD, **change}

    def get(url: str) -> bytes:
        assert url == "https://og.example/img", url  # the address GitHub reported
        if state["served"] is None:
            raise OSError("timed out")
        return state["served"]
    return check("1.1.0", fake(state), get, root or make_root("Install in Claude Code only.", {}))


README_PI = "Run it:\n\n    pi install git:github.com/MrBinnacle/skills@v1.1.0\n"
RECEIPT_OLD = "The README command: `pi install git:github.com/MrBinnacle/skills@v1.0.0`. Exit code 0."
RECEIPT_NEW = "The README command: `pi install git:github.com/MrBinnacle/skills@v1.1.0`. Exit code 0."
PI_FIX = ("run the Pi install receipt at v1.1.0 and save it as docs/product/receipts/<date>-pi-install.md "
          "(see the newest receipt for the steps).")


def path_drift() -> list[str]:
    """Each path pages.yml's on.push.paths lists that PAGES_PATHS lacks, and the reverse."""
    lines = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8").splitlines()
    start = lines.index("    paths:") + 1
    listed = []
    for line in lines[start:]:
        if not line.startswith("      - "):
            break
        listed.append(line[8:].strip('"').removesuffix("/**"))
    return [f"pages.yml only: {x}" for x in listed if x not in PAGES_PATHS] +            [f"PAGES_PATHS only: {x}" for x in PAGES_PATHS if x not in listed]


def expect(name: str, got: list[str], *needles: str) -> bool:
    ok = len(got) == len(needles) and all(any(n in g for g in got) for n in needles)
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f": {got}"))
    return ok


CASES = [
    ("all public surfaces carry the release", gaps()),
    ("a missing tag is a gap", gaps(tags="aaa\trefs/tags/v1.0.0",
                                    releases=[{"tagName": "v1.0.0", "isDraft": False, "isLatest": True}]),
     "v1.1.0 is not tagged"),
    ("a tag off main is a gap", gaps(on_main={"aaa"}), "not on main"),
    ("a tag without a release is a gap", gaps(releases=[{"tagName": "v1.1.0", "isDraft": False, "isLatest": True}]),
     "v1.0.0 has no GitHub Release"),
    ("a draft release is a gap", gaps(releases=[{"tagName": "v1.0.0", "isDraft": True, "isLatest": False},
                                                {"tagName": "v1.1.0", "isDraft": False, "isLatest": True}]),
     "draft"),
    ("another Latest is a gap", gaps(releases=[{"tagName": "v1.0.0", "isDraft": False, "isLatest": True},
                                               {"tagName": "v1.1.0", "isDraft": False, "isLatest": False}]),
     "marks v1.0.0 as Latest"),
    ("an undeployed site change is a gap", gaps(pages=[{"headSha": "old", "conclusion": "success"}]),
     "not deployed"),
    ("a failed Pages run is a gap", gaps(pages=[{"headSha": "sss", "conclusion": "failure"}]), "not deployed"),
    ("no Pages run is a gap", gaps(pages=[]), "newest Pages run: none"),
    ("a later successful Pages run deploys the site", gaps(pages=[{"headSha": "later", "conclusion": "success"}])),
    ("nothing to deploy is no gap", gaps(site="", pages=[])),
    ("an undeployed favicon change is a gap", gaps(favicon="fff"), "last change fff is not deployed"),
    ("the check reads every path pages.yml deploys on", path_drift()),
    ("an annotated tag is read by its commit", gaps(tags="aaa\trefs/tags/v1.0.0\nttt\trefs/tags/v1.1.0\nbbb\trefs/tags/v1.1.0^{}")),
    ("an old social preview is a gap", gaps(served=b"old image"),
     "The social preview GitHub serves (fbb22b3adc86) is not assets/social-preview.png: upload assets/social-preview.png in Settings, General, Social preview."),
    ("a generated social preview is a gap", gaps(custom=False),
     "GitHub generates the social preview instead of serving ours: upload assets/social-preview.png in Settings, General, Social preview."),
    ("a failed download is a gap", gaps(served=None), "Could not download the social preview GitHub serves (timed out): run the check again."),
    ("a receipt at the README's Pi pin is no gap", pi_receipt_gaps(README_PI, [RECEIPT_OLD, RECEIPT_NEW])),
    ("a receipt at an older Pi pin is a gap", pi_receipt_gaps(README_PI, [RECEIPT_NEW, RECEIPT_OLD]),
     "The newest Pi install receipt tested v1.0.0, but the README sends Pi users to v1.1.0: " + PI_FIX),
    ("no Pi install receipt is a gap", pi_receipt_gaps(README_PI, []),
     "No Pi install receipt names a pin, but the README sends Pi users to v1.1.0: " + PI_FIX),
    ("a receipt naming no pin is a gap", pi_receipt_gaps(README_PI, ["# Receipt\nno command here"]),
     "No Pi install receipt names a pin, but the README sends Pi users to v1.1.0: " + PI_FIX),
    ("a README with no Pi command needs no receipt", pi_receipt_gaps("Install in Claude Code only.", [])),
    ("another repository's Pi command needs no receipt",
     pi_receipt_gaps("pi install git:github.com/someone/else@v9.9.9", [])),
    ("the check reads the newest dated receipt from the repository",
     gaps(root=make_root(README_PI, {"2026-01-02-pi-install.md": RECEIPT_OLD,
                                     "2026-01-01-pi-install.md": RECEIPT_NEW})),
     "The newest Pi install receipt tested v1.0.0, but the README sends Pi users to v1.1.0: " + PI_FIX),
    ("a Pi gap is reported beside the other gaps",
     gaps(root=make_root(README_PI, {"2026-01-01-pi-install.md": RECEIPT_OLD}), on_main={"aaa"},
          served=b"old image"),
     "names bbb, which is not on main",
     "The social preview GitHub serves (fbb22b3adc86) is not assets/social-preview.png",
     "The newest Pi install receipt tested v1.0.0, but the README sends Pi users to v1.1.0: " + PI_FIX),
    ("the newest receipt wins whatever order the disk lists files in",
     listed_backwards(make_root(README_PI, {"2026-01-01-pi-install.md": RECEIPT_OLD,
                                           "2026-01-02-pi-install.md": RECEIPT_NEW}))),
    ("a newest receipt at the pin, beside other files, is no gap",
     gaps(root=make_root(README_PI, {"2026-01-01-pi-install.md": RECEIPT_OLD,
                                     "2026-01-02-pi-install.md": RECEIPT_NEW,
                                     "2026-01-03-notes.md": RECEIPT_OLD}))),
]


def main() -> int:
    failed = sum(not expect(name, got, *needles) for name, got, *needles in CASES)
    print(f"{len(CASES) - failed} of {len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
