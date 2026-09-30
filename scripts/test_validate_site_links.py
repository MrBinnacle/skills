#!/usr/bin/env python3
"""Suite for validate_site_links.py: the live site passes, and each broken form is refused."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_site_links as sl  # noqa: E402

ROOT = SCRIPT_DIR.parent


def _copy_with_href(href: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    for name in ("README.md", "CATALOG.md"):
        shutil.copy(ROOT / name, tmp / name)
    shutil.copytree(ROOT / "site", tmp / "site")
    shutil.copytree(ROOT / "assets", tmp / "assets")
    page = tmp / "site" / "index.html"
    html = page.read_text(encoding="utf-8")
    page.write_text(html.replace("</main>", f'<a href="{href}">x</a></main>'), encoding="utf-8", newline="")
    return tmp


def main() -> int:
    failures: list[str] = []

    if sl.check(ROOT):
        failures.append(f"live site should pass, got {sl.check(ROOT)}")

    if sl.github_slug("What this isn't") != "what-this-isnt":
        failures.append("slug of an apostrophe heading")
    if sl.github_slug("`skills`") != "skills":
        failures.append("slug of a code-span heading")

    broken = {
        "moved README anchor": "https://github.com/MrBinnacle/skills#card-evidence",
        "missing CATALOG anchor": "https://github.com/MrBinnacle/skills/blob/main/CATALOG.md#no-such-heading",
        "missing file": "https://github.com/MrBinnacle/skills/blob/main/NOPE.md",
        "missing page id": "#no-such-id",
        "missing local asset": "assets/no-such-file.svg",
    }
    for label, href in broken.items():
        tmp = _copy_with_href(href)
        try:
            if not sl.check(tmp):
                failures.append(f"{label} ({href}) was accepted")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"PASS: site link suite, {len(broken) + 3} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
