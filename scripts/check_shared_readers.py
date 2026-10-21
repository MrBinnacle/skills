#!/usr/bin/env python3
"""Refuse a new copy of a reader that one module already owns.

WHY THIS EXISTS

    An agent that needs "the published cards" or "does this card load by hand"
    writes the reader again in the file it has open. The copies then disagree:
    4f268c3 added two more `iter_skill_dirs`, and only the original in
    validate_scoreboard.py skips `skills/in-progress/`. The load-mode flag was read by a fourth regex in
    validate_card_files.py (d4b7a88), a test that used the standing-cost regex
    instead of the shared frontmatter reader (#553, fixed by d412996), and an
    import of that regex into the release gate (62a7e0a).

WHAT IT REFUSES

    Each reader has one owner. Outside the owner, the check refuses:
      - a `def iter_skill_dirs`  -> import it from scripts/validate_scoreboard.py;
      - a `re.compile` whose pattern reads `disable-model-invocation:`, a name
        bound to the bare string "disable-model-invocation", or an import or
        attribute use of `DISABLE_MODEL_INVOCATION_RE` or `BY_HAND_RE`
                                 -> call `runs_by_hand` or `flag_set` from
                                    scripts/check_load_mode_markers.py.

ONLY ADDITIONS FAIL

    Three load-mode readers predate this check (validate_card_files.py,
    validate_standing_costs.py, release_gate.py). Folding them into the owner
    changes what each reads, so it is its own change. This check compares the
    readers at HEAD with the readers at the merge-base of `--base` and fails only
    on one the base did not have.

Usage:
    python scripts/check_shared_readers.py                # against origin/main
    python scripts/check_shared_readers.py --base REF     # against another ref
    python scripts/check_shared_readers.py --list         # every reader at HEAD, no verdict
"""
from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLAG = "disable-model-invocation"
FLAG_REGEX_NAMES = {"DISABLE_MODEL_INVOCATION_RE", "BY_HAND_RE"}
OWNERS = {
    "iter_skill_dirs": ("scripts/validate_scoreboard.py", "import iter_skill_dirs from scripts/validate_scoreboard.py"),
    "load-mode flag": (
        "scripts/check_load_mode_markers.py",
        "call runs_by_hand or flag_set from scripts/check_load_mode_markers.py",
    ),
}


def readers(path: str, source: str) -> set[tuple[str, str, str]]:
    """(path, reader kind, detail) for every reader copy in one file outside its owner."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    found: set[tuple[str, str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "iter_skill_dirs":
            found.add((path, "iter_skill_dirs", "def iter_skill_dirs"))
        elif isinstance(node, ast.Call) and _is_re_compile(node) and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str) and f"{FLAG}:" in first.value:
                found.add((path, "load-mode flag", f"re.compile({first.value!r})"))
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and node.value.value == FLAG:
            found.add((path, "load-mode flag", f"a name bound to {FLAG!r}"))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in FLAG_REGEX_NAMES:
                    found.add((path, "load-mode flag", f"from {node.module} import {alias.name}"))
        elif isinstance(node, ast.Attribute) and node.attr in FLAG_REGEX_NAMES and isinstance(node.value, ast.Name):
            found.add((path, "load-mode flag", f"{node.value.id}.{node.attr}"))
    return {r for r in found if OWNERS[r[1]][0] != path}


def _is_re_compile(node: ast.Call) -> bool:
    func = node.func
    return isinstance(func, ast.Attribute) and func.attr == "compile" and isinstance(func.value, ast.Name) \
        and func.value.id == "re"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, check=True, text=True, encoding="utf-8"
    ).stdout


def readers_at(rev: str | None) -> set[tuple[str, str, str]]:
    """Every reader copy under scripts/ at a revision, or in the working tree when rev is None."""
    if rev is None:
        files = [p for p in git("ls-files", "scripts").split("\n") if p.endswith(".py")]
        return {r for p in files if (REPO_ROOT / p).is_file()
                for r in readers(p, (REPO_ROOT / p).read_text(encoding="utf-8", errors="replace"))}
    files = [p for p in git("ls-tree", "-r", "--name-only", rev, "--", "scripts").split("\n") if p.endswith(".py")]
    return {r for p in files for r in readers(p, git("show", f"{rev}:{p}"))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--base", default="origin/main", help="compare with the merge-base of HEAD and this ref")
    parser.add_argument("--list", action="store_true", help="print every reader copy at HEAD and exit 0")
    args = parser.parse_args()

    head = readers_at(None)
    if args.list:
        for path, kind, detail in sorted(head):
            print(f"  {path}: {kind}: {detail}")
        return 0
    try:
        base = git("merge-base", "HEAD", args.base).strip()
    except subprocess.CalledProcessError:
        print(f"ERROR: cannot resolve a merge-base with {args.base!r}; fetch it (CI needs fetch-depth: 0)")
        return 2
    added = sorted(head - readers_at(base))
    for path, kind, detail in added:
        print(f"  - {path}: a second {kind} reader ({detail}). Instead, {OWNERS[kind][1]}.")
    if added:
        print(f"REJECTED: {len(added)} new reader copy(ies) since {base[:7]}; each reader has one owner.")
        return 1
    print(f"PASS: no new copy of a shared reader since {base[:7]} ({len(head)} older copies stand)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
