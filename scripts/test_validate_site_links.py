#!/usr/bin/env python3
"""Suite for validate_site_links.py: the live site passes, and each broken form is refused.

It also pins the footer to the content column (#365): no rule that reaches the
footer list may reset the inline margins that .wrap sets.
"""
from __future__ import annotations

import re
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


INLINE_MARGIN = re.compile(r"^margin(-inline(-start|-end)?|-left|-right)?$")


def footer_margin_resets(css: str) -> list[str]:
    """Rules that reach `.foot ul` and declare an inline margin, which beats .wrap's auto."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    hits = []
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if not any(s.strip().endswith(".foot ul") for s in selectors.split(",")):
            continue
        for decl in body.split(";"):
            if INLINE_MARGIN.match(decl.split(":", 1)[0].strip()):
                hits.append(f"{' '.join(selectors.split())} {{ {decl.strip()} }}")
    return hits


def footer_column_failures() -> list[str]:
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    if not re.search(r'<footer class="foot">\s*<ul class="wrap">', html):
        return ["footer list no longer carries .wrap; the footer-column check would prove nothing"]
    css = (ROOT / "site" / "style.css").read_text(encoding="utf-8")
    failures = [f"footer list inline-margin reset beats .wrap: {hit}" for hit in footer_margin_resets(css)]
    if not footer_margin_resets(".isnt ul,\n.foot ul { list-style: none; margin: 0; padding: 0; }"):
        failures.append("footer-column check accepted the #365 reset")
    return failures


def main() -> int:
    failures: list[str] = footer_column_failures()

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
    print(f"PASS: site link suite, {len(broken) + 5} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
