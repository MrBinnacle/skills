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
DEMOS = [f"mechanisms/verify-gate/demo-{v}.svg" for v in ("dark", "light", "dark-narrow", "light-narrow")]
DEMO = DEMOS[1]
DEMO_CP = "cp mechanisms/verify-gate/demo-dark.svg mechanisms/verify-gate/demo-light.svg mechanisms/verify-gate/demo-dark-narrow.svg mechanisms/verify-gate/demo-light-narrow.svg _site/assets/"
UNRESOLVED = "not in site/, and no pages.yml cp line copies an existing file there"
# The order the page lists them: the two narrow sources, the dark source, the img src.
DEMO_UNRESOLVED = [f"assets/demo-{v}.svg: {UNRESOLVED}" for v in ("dark-narrow", "light-narrow", "dark", "light")]


def _copy_with(snippet: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    for name in ("README.md", "CATALOG.md", sl.PAGES_WORKFLOW, *DEMOS):
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp / name)
    shutil.copytree(ROOT / "site", tmp / "site")
    shutil.copytree(ROOT / "assets", tmp / "assets")
    page = tmp / "site" / "index.html"
    html = page.read_text(encoding="utf-8")
    page.write_text(html.replace("</main>", f"{snippet}</main>"), encoding="utf-8", newline="")
    return tmp


def _copy_with_href(href: str) -> Path:
    return _copy_with(f'<a href="{href}">x</a>')


def _drop_demo_cp(tmp: Path) -> None:
    workflow = tmp / sl.PAGES_WORKFLOW
    text = workflow.read_text(encoding="utf-8")
    workflow.write_text("\n".join(line for line in text.splitlines() if line.strip() != DEMO_CP), encoding="utf-8")


def src_failures() -> list[str]:
    """Each src form resolves the way pages.yml deploys it, and each unresolved form is refused whole."""
    failures: list[str] = []
    if 'src="assets/demo-light.svg"' not in (ROOT / "site" / "index.html").read_text(encoding="utf-8"):
        failures.append("live page no longer carries the demo src; the demo cases prove nothing")
    if DEMO_CP not in (ROOT / sl.PAGES_WORKFLOW).read_text(encoding="utf-8"):
        failures.append("pages.yml no longer carries the demo cp line; the demo cases prove nothing")

    cases = {
        "missing src": ('<img src="assets/no-such.svg" alt="">', None, [f"assets/no-such.svg: {UNRESOLVED}"]),
        # Root assets/ holds files pages.yml never copies; this one would 404 on the live site.
        "root asset the deploy does not copy": ('<img src="assets/banner-dark.svg" alt="">', None, [f"assets/banner-dark.svg: {UNRESOLVED}"]),
        # README.md exists one level up, but the deploy publishes nothing outside site/.
        "path that leaves site/": ('<a href="../README.md">x</a>', None, [f"../README.md: {UNRESOLVED}"]),
        # Pages is case-sensitive; site/favicon-32.png exists, but this spelling 404s live.
        "wrong letter case": ('<img src="FAVICON-32.PNG" alt="">', None, [f"FAVICON-32.PNG: {UNRESOLVED}"]),
        # site/fonts is a directory, which no browser can load as an image.
        "directory, not a file": ('<img src="fonts" alt="">', None, [f"fonts: {UNRESOLVED}"]),
        # A trailing slash asks Pages for a directory named favicon-32.png; none exists.
        "trailing slash": ('<img src="favicon-32.png/" alt="">', None, [f"favicon-32.png/: {UNRESOLVED}"]),
        # The font exists, but a web server reads "\" as part of the name, not as a separator.
        "backslash separator": (
            r'<img src="fonts\IBMPlexMono-Regular-Latin1.woff2" alt="">',
            None,
            [rf"fonts\IBMPlexMono-Regular-Latin1.woff2: {UNRESOLVED}"],
        ),
        # "./" is legal in a URL but adds nothing; refusing it keeps one spelling per file.
        "dot part": ('<img src="./favicon-32.png" alt="">', None, [f"./favicon-32.png: {UNRESOLVED}"]),
        "demo src copied by pages.yml": ("", None, []),
        "a srcset is checked like a src": ('<picture><source srcset="assets/nope.svg"><img src="assets/favicon.svg" alt=""></picture>', None, [f"assets/nope.svg: {UNRESOLVED}"]),
        "demo srcs without their cp line": ("", _drop_demo_cp, DEMO_UNRESOLVED),
        "demo src whose cp source is gone": ("", lambda tmp: (tmp / DEMO).unlink(), [f"assets/demo-light.svg: {UNRESOLVED}"]),
    }
    for label, (snippet, mutate, want) in cases.items():
        tmp = _copy_with(snippet)
        try:
            if mutate:
                mutate(tmp)
            # The fixture copies only a few repository files, so its repository links fail; local refs are the subject.
            got = [error for error in sl.check(tmp) if not error.startswith(sl.REPO_URL)]
            if got != want:
                failures.append(f"{label}: want {want}, got {got}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    workflow = "cp -r site/. _site/\n  cp x/a.svg b.png _site/assets/\n  cp m/d.svg _site/assets/demo.svg\ncp a b\nmv x/c.svg _site/assets/c.svg\n"
    want_copies = {"assets/a.svg": "x/a.svg", "assets/b.png": "b.png", "assets/demo.svg": "m/d.svg"}
    if sl.deploy_copies(workflow) != want_copies:
        failures.append(f"deploy_copies: want {want_copies}, got {sl.deploy_copies(workflow)}")
    return failures


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
    failures: list[str] = footer_column_failures() + src_failures()

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
            # The fixture copies a few files, so check() reports other links too; only the
            # injected link's own diagnostic proves it was refused (#704).
            if not any(error.startswith(f"{href}: ") for error in sl.check(tmp)):
                failures.append(f"{label} ({href}) was accepted")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"PASS: site link suite, {len(broken) + 10} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
