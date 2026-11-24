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
  - it serves other bytes, or a generated preview: red.

Run directly:  python scripts/test_check_release_public.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_release_public import PREVIEW, check  # noqa: E402

OURS = PREVIEW.read_bytes()

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
            return json.dumps({"data": {"repository": {
                "openGraphImageUrl": "https://og.example/img", "usesCustomOpenGraphImage": state["custom"]}}})
        raise AssertionError(f"unexpected command {cmd}")
    return run


def gaps(**change) -> list[str]:
    state = {**GOOD, **change}
    return check("1.1.0", fake(state), lambda url: state["served"])


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
    ("an annotated tag is read by its commit", gaps(tags="aaa\trefs/tags/v1.0.0\nttt\trefs/tags/v1.1.0\nbbb\trefs/tags/v1.1.0^{}")),
    ("an old social preview is a gap", gaps(served=b"old image"), "is not assets/social-preview.png"),
    ("a generated social preview is a gap", gaps(custom=False), "GitHub generates the social preview"),
]


def main() -> int:
    failed = sum(not expect(name, got, *needles) for name, got, *needles in CASES)
    print(f"{len(CASES) - failed} of {len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
