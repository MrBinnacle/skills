#!/usr/bin/env python3
"""Check that every link on the Pages site resolves, anchors included.

lychee checks that a URL answers. It does not check the part after `#`, so a
link to a README heading that was renamed or moved keeps passing while the
reader lands at the top of the wrong page. That happened: #324 moved four
README sections to CATALOG.md and the site kept linking to all four
(skills_research audit S498, finding F4).

This script resolves each link against the working tree instead of the network:

- `#id` must name an `id` on the page itself.
- A relative path must exist under `site/`.
- `https://github.com/MrBinnacle/skills` links resolve to a file in this
  repository (`/blob/main/<path>`, or README.md for the bare repository URL),
  and a fragment must equal the GitHub slug of a heading in that file.
  `#readme` on the bare repository URL is GitHub's own anchor and is accepted.

Other hosts are lychee's job and are skipped here.

Exit 0 with a `PASS:` line, or 1 with one line per broken link.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_URL = "https://github.com/MrBinnacle/skills"
BLOB_PREFIX = REPO_URL + "/blob/main/"


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if name == "id":
                self.ids.add(value)
            elif name == "href":
                self.hrefs.append(value)


def github_slug(heading: str) -> str:
    """GitHub's heading anchor: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"`", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_slugs(markdown: Path) -> set[str]:
    slugs: set[str] = set()
    in_fence = False
    for line in markdown.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            match = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
            if match:
                slugs.add(github_slug(match.group(1)))
    return slugs


def check_repo_link(href: str, root: Path) -> str | None:
    target, _, fragment = href.partition("#")
    target = target.rstrip("/")
    if target == REPO_URL:
        if fragment in ("", "readme"):
            return None
        path = root / "README.md"
    elif target.startswith(BLOB_PREFIX):
        path = root / target[len(BLOB_PREFIX):]
    else:
        return None
    if not path.exists():
        return f"{href}: {path.relative_to(root).as_posix()} does not exist"
    if fragment and path.suffix == ".md" and fragment not in heading_slugs(path):
        return f"{href}: no heading with anchor #{fragment} in {path.relative_to(root).as_posix()}"
    return None


def check(root: Path) -> list[str]:
    site = root / "site"
    parser = _Links()
    parser.feed((site / "index.html").read_text(encoding="utf-8"))
    errors: list[str] = []
    for href in parser.hrefs:
        if href.startswith("#"):
            if href[1:] not in parser.ids:
                errors.append(f"{href}: no element with that id on the page")
        elif href.startswith(REPO_URL):
            error = check_repo_link(href, root)
            if error:
                errors.append(error)
        elif not re.match(r"^[a-z]+:", href):
            # pages.yml copies repository-root assets/ files in beside site/.
            if not ((site / href).exists() or (href.startswith("assets/") and (root / href).exists())):
                errors.append(f"{href}: neither site/{href} nor a root {href} exists")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that every link on the Pages site resolves.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    errors = check(args.root)
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print("PASS: every site link resolves, anchors included")
    return 0


if __name__ == "__main__":
    sys.exit(main())
