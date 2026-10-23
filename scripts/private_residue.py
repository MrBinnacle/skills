#!/usr/bin/env python3
"""Refuse a tracked file, path or message that carries a private residue term.

WHY THE TERMS ARE NOT IN THE TREE

    The `residue-` hooks in `.pre-commit-config.yaml` keep their terms in plain
    text. Some names cannot sit there: a public block-list that names a private
    repository discloses that repository (#580). Those terms come from two
    places outside the tree, and the check reads both:

      - the `RESIDUE_PRIVATE_TERMS` environment variable, one term per line.
        CI sets it from the repository secret of the same name;
      - `.residue-private.local` at the repository root, one term per line,
        `#` for a comment. The file is git-ignored.

WHY NO MATCH IS EVER PRINTED

    A CI log of a public repository is public. GitHub masks the stored secret
    value only, and a match in another spelling (spaced, hyphenated, mixed case)
    is a different string, so it would print unmasked. A refusal therefore names
    the file, the line and the term's number, and never the text that matched.

HOW A TERM MATCHES

    The term is split into words at spaces, `_`, `.` and `-`. The words then
    match with any run of those separators between them, or none, in any case.
    `alpha beta` matches `alpha-beta`, `Alpha_Beta`, `ALPHA BETA` and
    `alphabeta`. Word edges treat the separators as breaks, as in
    `validate_path_residue.py`.

FAIL-CLOSED IN CI, QUIET ON A CLONE WITHOUT TERMS

    With `--require`, a run that loads no term exits 2: a missing secret must
    not read as a clean tree. Without it, a clone that holds no overlay file
    passes with a note, because a contributor's clone has no private terms to
    check.

Usage:
    python scripts/private_residue.py FILE [FILE ...]  # contents of these files, and every tracked path
    python scripts/private_residue.py --all            # contents and path of every tracked file
    python scripts/private_residue.py --all --require  # the CI form: no term loaded is exit 2
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
TERMS_ENV: Final[str] = "RESIDUE_PRIVATE_TERMS"
OVERLAY: Final[str] = ".residue-private.local"
# Points the overlay elsewhere. The suites set it, so a maintainer's own
# overlay never decides a control's result.
OVERLAY_ENV: Final[str] = "RESIDUE_PRIVATE_OVERLAY"
_SEPARATORS: Final[str] = r"[\s_.\-]"


def load_terms(root: Path = REPO_ROOT, environ: Mapping[str, str] = os.environ) -> list[str]:
    """Every term from the environment variable and the overlay file, de-duplicated, in order."""
    lines = environ.get(TERMS_ENV, "").splitlines()
    overlay = Path(environ[OVERLAY_ENV]) if environ.get(OVERLAY_ENV) else root / OVERLAY
    if overlay.is_file():
        lines += overlay.read_text(encoding="utf-8", errors="replace").splitlines()
    terms: list[str] = []
    for line in lines:
        term = line.strip()
        if term and not term.startswith("#") and term.lower() not in (t.lower() for t in terms):
            terms.append(term)
    return terms


def term_pattern(term: str) -> re.Pattern[str]:
    """The term in any case, with any run of separators, or none, between its words."""
    words = [re.escape(w) for w in re.split(_SEPARATORS + "+", term) if w]
    body = (_SEPARATORS + "*").join(words)
    return re.compile(r"(?<![a-z0-9])" + body + r"(?![a-z0-9])", re.IGNORECASE)


def patterns(root: Path = REPO_ROOT, environ: Mapping[str, str] = os.environ) -> list[re.Pattern[str]]:
    return [term_pattern(t) for t in load_terms(root, environ)]


def text_breaches(label: str, text: str, pats: list[re.Pattern[str]]) -> list[str]:
    """One line per (line, term) match. The matched text is never included."""
    out: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        for index, pat in enumerate(pats, 1):
            if pat.search(line):
                out.append(f"{label}:{number}: private term {index}")
    return out


def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True)
    return [p for p in result.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    parser.add_argument("--all", action="store_true", help="read the contents of every tracked file")
    parser.add_argument("--require", action="store_true", help="exit 2 when no private term is loaded")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository to read (the suite uses this)")
    parser.add_argument("files", nargs="*", help="files whose contents to read, as pre-commit passes them")
    args = parser.parse_args(argv)

    pats = patterns(args.root)
    if not pats:
        if args.require:
            print(
                f"UNINTERPRETABLE: no private residue term loaded. Set the {TERMS_ENV} "
                f"repository secret (CI) or write {OVERLAY} (a local clone)."
            )
            return 2
        print(f"PASS: no private residue term loaded ({TERMS_ENV} unset, no {OVERLAY}); nothing to check")
        return 0

    paths = tracked_paths(args.root)
    breaches = [
        f"tracked path {i} (git ls-files order): private term {n}"
        for i, p in enumerate(paths, 1)
        for n, pat in enumerate(pats, 1)
        if pat.search(p)
    ]
    files = paths if args.all else args.files
    for name in files:
        target = args.root / name
        if target.is_file():
            # A name that carries a term is reported above by number; never print it.
            label = "a file whose path carries a term" if any(p.search(name) for p in pats) else name
            text = target.read_bytes().decode("utf-8", "replace")
            breaches += text_breaches(label, text, pats)

    for breach in breaches:
        print(f"  - {breach}")
    if breaches:
        print(
            f"REJECTED: {len(breaches)} private residue match(es). The term's text is not printed, "
            f"because this log may be public. Find it with your own copy of the term list."
        )
        return 1
    print(
        f"PASS: {len(files)} file(s) and {len(paths)} path(s) read against "
        f"{len(pats)} private residue term(s), no match"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
