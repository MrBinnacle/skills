#!/usr/bin/env python3
"""Refuse any file inside a skill folder that is not a declared readable format.

SECURITY.md commits to a closed vocabulary: every file inside a skill folder is
`.md`, `.txt`, `.py` or `.json`. This script is the check behind that sentence.
It walks, evaluates a predicate per file, and lists everything that fails. There
is no per-file allowlist anywhere in it, so a new violating file turns the run
red with nobody remembering to update a list.

Output is ASCII-only so the Windows CI cell does not die on cp1252 when printing
a status line, matching validate_scoreboard.py.

WHAT COUNTS AS A SKILL FOLDER
    Any directory containing a file named exactly `SKILL.md` -- the same marker
    the installer keys on -- plus everything beneath it. Deliberately NOT the
    literal path `skills/**`: the fixture trees under `scripts/fixtures/` carry
    real `SKILL.md` files outside `skills/`, and a path-scoped gate would never
    look at them. Keying on the marker closes that by construction. The match is
    exact and case-sensitive, so `propose-a-skill.md` is not a marker.

COMPILED PYTHON
    A skill that ships a script leaves `__pycache__/*.pyc` behind the first time
    it runs. Nobody shipped those files; the reader's own interpreter wrote them.
    Blanket-skipping `__pycache__` would answer that, and would also carve out a
    directory the check never opens -- a hiding place at exactly the boundary
    this check exists to hold. So bytecode is admitted only when the source it
    derives from is present and readable beside it: `__pycache__/mod.*.pyc`
    passes if and only if `mod.py` sits in the parent directory. A payload at
    `__pycache__/evil.pyc` has no `evil.py` and fails.

    Note what this does NOT admit. Test-runner state (`.pytest_cache/`) derives
    from nothing readable in the folder, so it is not admitted by the bytecode
    rule. It is instead excluded earlier, by the gitignore rule below, because
    it is not a file in the repository at all.

GIT-IGNORED PATHS
    A file git ignores is not in the published tree and never will be, so this
    gate does not judge it. Without that rule the gate was unreadable exactly
    where it mattered: a maintainer who ran `im-up`'s test suite -- which its
    own SKILL.md tells them to run -- planted `.pytest_cache/` inside a skill
    folder and got six rejections on files CI has never seen. CI stayed green on
    a fresh checkout, so the only person the gate ever shouted at was the only
    person who could act on it, about something that was never a violation. A
    guard that cries wolf locally trains its reader to route around the family.

    The question is put to git itself, via `git check-ignore`, one call for the
    whole file list. Two properties of that command are why it is used here
    rather than `git ls-files`:

      - It answers "would git ignore this?", so an untracked file that no rule
        ignores -- a `payload.sh` dropped into a skill folder five minutes ago --
        is still judged. Deriving the list from `git ls-files` instead would
        skip every untracked file, which quietly turns the gate into a check on
        what is already committed and opens the exact hole it exists to close.
      - It consults the index, so a TRACKED file is never reported as ignored
        even when a pattern matches it. A file in the repository is judged,
        full stop.

    FALLBACK for a tree that is not a git work tree (a released tarball, a
    reader's install directory, the temp trees the poison controls build): no
    filtering happens and every file is judged. That direction is deliberate --
    losing the filter costs a false alarm, while losing the check costs the
    guarantee -- and the run says which mode it was in on its status line, so
    nobody has to infer it.

SYMLINKS
    The walk follows them. Installs are symlinked (and on Windows, junctioned),
    and a walk that does not follow links silently skips the very files it is
    supposed to guard -- a bare `find` undercounts this corpus by ~43%. Each
    real directory is entered once, so a link cycle terminates.

WHAT THIS IS AND IS NOT
    This makes the published claim MAINTAINABLE, not VERIFIABLE. The walker is
    code in the repository it guards, run by CI configured in that repository,
    on a commit from the same authority. One commit can add a violating file and
    widen this vocabulary in the same diff. Deriving rather than enumerating buys
    resistance to forgetting; it buys nothing against intent. And green CI is
    invisible downstream -- a reader cannot tell whether this ever ran. That is
    why it ships paired with a command the reader runs on their own copy:
    `--print-reader-command`.

    `main` currently has no branch protection and no required checks, so a
    nonzero exit here is a signal, not a gate. Describe it as detecting
    violations, never as preventing them.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Final, Iterator, NoReturn

# The declared vocabulary. Widening it is a reviewed change to the published
# security commitment in SECURITY.md, not a silent commit. Everything else in
# this file -- including the reader-side command -- is derived from this tuple,
# so the check and the published text cannot disagree.
ALLOWED_SUFFIXES: Final[tuple[str, ...]] = (".md", ".txt", ".py", ".json")

SKILL_MARKER: Final[str] = "SKILL.md"
PYCACHE_DIR: Final[str] = "__pycache__"


def fail(msg: str) -> NoReturn:
    # ASCII only: no em dash, curly quotes, or middle dots.
    print(f"REJECTED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def walk(root: Path) -> Iterator[tuple[Path, list[Path]]]:
    """Yield (directory, files) beneath root, following symlinks once each.

    `is_dir()` and `is_file()` follow links by default, which is what makes this
    agree with `find -L`. Real paths are tracked so a cycle cannot loop.
    """
    seen: set[Path] = set()
    stack: list[Path] = [root]
    while stack:
        current = stack.pop()
        try:
            real = current.resolve()
        except OSError:
            continue
        if real in seen:
            continue
        seen.add(real)
        try:
            entries = sorted(current.iterdir())
        except OSError:
            continue
        files: list[Path] = []
        for entry in entries:
            try:
                if entry.is_dir():
                    stack.append(entry)
                elif entry.is_file():
                    files.append(entry)
            except OSError:
                continue
        yield current, files


def find_skill_folders(root: Path) -> list[Path]:
    """Every directory under root that contains a SKILL.md, sorted."""
    found = [
        directory
        for directory, files in walk(root)
        if any(f.name == SKILL_MARKER for f in files)
    ]
    return sorted(found)


def guarded_files(skill_folders: list[Path]) -> list[Path]:
    """Every file inside any skill folder, each real file once."""
    seen: set[Path] = set()
    collected: list[Path] = []
    for folder in skill_folders:
        for _, files in walk(folder):
            for path in files:
                try:
                    real = path.resolve()
                except OSError:
                    real = path
                if real in seen:
                    continue
                seen.add(real)
                collected.append(path)
    return sorted(collected)


def is_git_work_tree(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
    except OSError:
        # git is not installed, or not on PATH. Same answer as "not a work
        # tree": judge everything.
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def ignored_files(root: Path, files: list[Path]) -> set[Path]:
    """The subset of `files` that git ignores, or an empty set if git cannot say.

    One `git check-ignore` call for the whole list. `-z` on both sides because a
    path may contain anything a filesystem allows, and a newline-delimited
    protocol would mis-split it -- in the direction of skipping a file that was
    never ignored.

    Exit codes: 0 means some paths matched, 1 means none did, anything else is
    an error and returns the empty set, which judges every file. Errors here
    must never subtract from what is checked.
    """
    if not files or not is_git_work_tree(root):
        return set()
    payload = "\0".join(str(f) for f in files)
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--stdin", "-z"],
            input=payload,
            capture_output=True,
            text=True,
        )
    except OSError:
        return set()
    if result.returncode not in (0, 1):
        return set()
    reported = {line for line in result.stdout.split("\0") if line}
    # Match on the same strings that were sent, so no path normalisation sits
    # between the question and the answer.
    return {f for f in files if str(f) in reported}


def bytecode_source(path: Path) -> Path | None:
    """The .py a compiled file derives from, or None if it is not compiled Python.

    CPython writes `mod.cpython-313.pyc`, and pytest writes
    `test_mod.cpython-313-pytest-8.4.1.pyc`. The module name is the part before
    the first dot in either case.
    """
    if path.suffix != ".pyc" or path.parent.name != PYCACHE_DIR:
        return None
    module = path.name.split(".", 1)[0]
    return path.parent.parent / f"{module}.py"


def describe(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def violation(root: Path, path: Path) -> str | None:
    """The reason this file is not a declared readable format, or None."""
    if path.suffix in ALLOWED_SUFFIXES:
        return None
    source = bytecode_source(path)
    if source is not None:
        if source.is_file():
            return None
        return (
            f"{describe(root, path)}: compiled Python with no readable source "
            f"beside it (expected {describe(root, source)})"
        )
    kind = path.suffix if path.suffix else "no extension"
    return f"{describe(root, path)}: {kind} is not a declared readable format"


def reader_command(target: str = "<the folder you installed>") -> str:
    """The check a reader runs against their own installed copy.

    Generated from ALLOWED_SUFFIXES rather than typed out a second time, so the
    published text cannot drift from the predicate this script enforces.

    THE ONE-LEVEL ANCHOR, and it is the part that is easy to get wrong.
        `bytecode_source()` admits a `.pyc` only when it is a DIRECT child of a
        `__pycache__` directory -- `path.parent.name == PYCACHE_DIR`. A bare
        `-path '*/__pycache__/*.pyc'` is weaker than that, because `*` spans
        slashes: it also matches `__pycache__/anything/deeper/x.pyc`. Without
        the `! -path '*/__pycache__/*/*'` guard on both steps, a payload nested
        one level down is excluded by step 1 and then passed by step 2, whose
        `${f%/__pycache__/*}` resolves back to the skill root where an unrelated
        `helper.py` may sit. The reader gets a clean bill on a tree this gate
        rejects, in the paragraph published so they need not trust us.
    """
    names = " ".join(f"! -name '*{suffix}'" for suffix in ALLOWED_SUFFIXES)
    nested = f"! -path '*/{PYCACHE_DIR}/*/*'"
    return "\n".join(
        [
            "# 1. Nothing but the declared formats. Compiled Python is step 2.",
            f"find -L {target} -type f \\",
            f"  {names} \\",
            f"  ! \\( -path '*/{PYCACHE_DIR}/*.pyc' {nested} \\)",
            "",
            "# 2. Every compiled file sits directly in __pycache__ with its source beside it.",
            f"find -L {target} -path '*/{PYCACHE_DIR}/*.pyc' {nested} -exec sh -c \\",
            f"  'for f; do d=${{f%/{PYCACHE_DIR}/*}}; b=${{f##*/}}; "
            '[ -f "$d/${b%%.*}.py" ] || echo "$f"; done\' _ {} +',
            "",
            "# Both print nothing when the commitment holds on your machine.",
            "# -L matters: installs are symlinked, and find without it skips them.",
        ]
    )


def validate(root: Path) -> None:
    if not root.is_dir():
        fail(f"not a directory: {root}")
    folders = find_skill_folders(root)
    if not folders:
        fail(
            f"no skill folders found under {root}. A run that guards nothing "
            f"guards nothing; check the root rather than trusting this green."
        )
    files = guarded_files(folders)
    skipped = ignored_files(root, files)
    files = [f for f in files if f not in skipped]
    scope = (
        f", {len(skipped)} git-ignored file(s) skipped"
        if is_git_work_tree(root)
        else ", not a git work tree so nothing was skipped"
    )
    violations = [v for v in (violation(root, f) for f in files) if v is not None]
    if violations:
        for item in violations:
            print(f"  - {item}", file=sys.stderr)
        declared = ", ".join(ALLOWED_SUFFIXES)
        fail(
            f"{len(violations)} file(s) inside a skill folder are not a declared "
            f"readable format ({declared}). Adding a format is a reviewed change "
            f"to SECURITY.md, not a silent commit."
        )
    print(
        f"PASS: {len(folders)} skill folder(s), {len(files)} file(s), "
        f"all declared readable formats ({', '.join(ALLOWED_SUFFIXES)})"
        f"{scope}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="tree to validate (default: one level above this script)",
    )
    parser.add_argument(
        "--print-reader-command",
        action="store_true",
        help="print the check a reader runs against their own installed copy",
    )
    args = parser.parse_args()
    if args.print_reader_command:
        print(reader_command())
        return
    root = args.root.resolve() if args.root else Path(__file__).resolve().parent.parent
    validate(root)


if __name__ == "__main__":
    main()
