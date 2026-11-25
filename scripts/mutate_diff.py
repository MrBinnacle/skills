#!/usr/bin/env python3
"""Fail when a clause this branch adds to scripts/*.py survives being broken.

For every line the diff from the base adds to a top-level scripts/<name>.py (test files
excepted), this builds mutants with a fixed operator set and runs the paired suite
scripts/test_<name>.py against each one in a temporary git worktree. A mutant is killed
only when the suite exits nonzero AND prints a FAIL/FAILED/ERROR line its unmutated run
did not print. A crash or a timeout is not a kill: it is printed as a note and does not
fail the run, because the suite did go red. A mutant the suite passes fails the run.

Operators, the whole set: delete a statement; drop one operand of and/or; replace a
comparison with True and with False; drop one list, tuple or set element; empty a string
literal; in a re.compile literal, drop one top-level | branch or a ^ or $ anchor.

A line ending in "# equivalent-mutant: <why>" is exempt. A changed script with no paired
suite fails. The working tree is never written.

Usage:  python scripts/mutate_diff.py [--base REV] [--jobs N]
The base defaults to the merge-base of HEAD and origin/main.
"""
from __future__ import annotations

import argparse
import ast
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

MARKER = "# equivalent-mutant:"
SCRIPT = re.compile(r"scripts/(?!test_)([^/]+)\.py")  # fullmatch
FAIL_LINE = re.compile(r"\s*(FAIL|FAILED|ERROR)\b")  # match
HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", re.M)
NOT_DELETED = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom,
               ast.Global, ast.Nonlocal)
IGNORE = shutil.ignore_patterns(".git", "node_modules", "__pycache__")  # equivalent-mutant: the last two only save copy time


@dataclass(frozen=True)
class Mutant:
    line: int
    text: str
    source: bytes


def added_lines(diff: str) -> set[int]:
    """The new-side line numbers a `git diff -U0` adds."""
    out: set[int] = set()
    for m in HUNK.finditer(diff):
        start, count = int(m[1]), int(m[2] or 1)
        out.update(range(start, start + count))
    return out


def split_branches(pattern: str) -> list[str]:
    """Split a regex on its top-level | only, outside groups, classes and escapes."""
    parts, depth, cls, i, start = [], 0, False, 0, 0
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            i += 1
        elif cls:
            cls = c != "]"
        elif c == "[":
            cls = True
        elif c in "()":
            depth += 1 if c == "(" else -1
        elif c == "|" and depth == 0:
            parts.append(pattern[start:i])
            start = i + 1
        i += 1
    return parts + [pattern[start:]]


def regex_variants(pattern: str) -> list[tuple[str, str]]:
    """(label, pattern) pairs: each top-level branch dropped, then each anchor dropped."""
    branches = split_branches(pattern)
    out = [(f"drops branch {b!r}", "|".join(branches[:i] + branches[i + 1:]))
           for i, b in enumerate(branches) if len(branches) > 1]
    if pattern.startswith("^"):
        out.append(("drops the ^ anchor", pattern[1:]))
    if pattern.endswith("$") and not pattern.endswith("\\$"):
        out.append(("drops the $ anchor", pattern[:-1]))
    return out


class Source:
    """A file's bytes, addressed by ast positions (col offsets are UTF-8 byte offsets)."""

    def __init__(self, data: bytes):
        self.data = data
        self.starts = [0]
        for line in data.splitlines(keepends=True):
            self.starts.append(self.starts[-1] + len(line))

    def span(self, node: ast.AST) -> tuple[int, int]:
        return (self.starts[node.lineno - 1] + node.col_offset,
                self.starts[node.end_lineno - 1] + node.end_col_offset)

    def seg(self, node: ast.AST) -> str:
        a, b = self.span(node)
        return self.data[a:b].decode("utf-8")

    def lines(self, node: ast.AST) -> set[int]:
        return set(range(node.lineno, node.end_lineno + 1))


def short(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= 60 else text[:57] + "..."


def skipped_nodes(tree: ast.AST) -> set[int]:
    """Ids of nodes no operator touches: annotations, f-string parts, docstrings, typing slices,
    help text, and the `if __name__ == "__main__":` entry block a suite that imports cannot reach."""
    roots: list[ast.AST | None] = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = n.args
            roots += [n.returns] + [x.annotation for x in a.posonlyargs + a.args + a.kwonlyargs]
            roots += [x.annotation for x in (a.vararg, a.kwarg) if x]
        elif isinstance(n, ast.AnnAssign):
            roots.append(n.annotation)
        elif isinstance(n, ast.JoinedStr):
            roots += n.values
        elif isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            roots.append(n)
        elif isinstance(n, ast.Subscript) and isinstance(n.slice, (ast.List, ast.Tuple)):
            roots.append(n.slice)
        elif isinstance(n, ast.keyword) and n.arg in ("help", "description"):
            roots.append(n.value)
        elif isinstance(n, ast.If) and ast.unparse(n.test) == "__name__ == '__main__'":
            roots.append(n)
    return {id(x) for r in roots if r is not None for x in ast.walk(r)}


def collection_text(node: ast.AST, items: list[str]) -> str:
    if isinstance(node, ast.List):
        return "[" + ", ".join(items) + "]"
    if isinstance(node, ast.Set):
        return "{" + ", ".join(items) + "}" if items else "set()"
    return "(" + ", ".join(items) + ("," if len(items) == 1 else "") + ")"


def edits(src: Source, node: ast.AST, added: set[int]):
    """Yield (line, label, (start, end), replacement) for every operator that applies to node."""
    if isinstance(node, ast.stmt) and not isinstance(node, NOT_DELETED) and node.lineno in added:
        yield node.lineno, f"deletes `{short(src.seg(node))}`", src.span(node), "pass"
    if isinstance(node, ast.BoolOp):
        op = "and" if isinstance(node.op, ast.And) else "or"
        for i, v in enumerate(node.values):
            if src.lines(v) & added:
                rest = [src.seg(x) for j, x in enumerate(node.values) if j != i]
                yield v.lineno, f"drops `{short(src.seg(v))}` from `{op}`", src.span(node), f"({f' {op} '.join(rest)})"
    if isinstance(node, ast.Compare) and src.lines(node) & added:
        for value in ("True", "False"):
            yield node.lineno, f"makes `{short(src.seg(node))}` {value}", src.span(node), value
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)) and not isinstance(getattr(node, "ctx", None), ast.Store):
        for i, e in enumerate(node.elts):
            if src.lines(e) & added:
                rest = [src.seg(x) for j, x in enumerate(node.elts) if j != i]
                yield e.lineno, f"drops element `{short(src.seg(e))}`", src.span(node), collection_text(node, rest)
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and src.lines(node) & added:
        yield node.lineno, f"empties `{short(src.seg(node))}`", src.span(node), '""'
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "compile"
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "re" and node.args
            and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
            and src.lines(node.args[0]) & added):
        for label, pattern in regex_variants(node.args[0].value):
            yield node.args[0].lineno, f"{label} in re.compile", src.span(node.args[0]), repr(pattern)


def mutants(data: bytes, added: set[int]) -> list[Mutant]:
    """Every compilable mutant of the added lines, minus lines marked equivalent."""
    src, tree = Source(data), ast.parse(data)
    text_lines = data.decode("utf-8").splitlines()
    exempt = {i + 1 for i, line in enumerate(text_lines) if MARKER in line}
    skip, seen, out = skipped_nodes(tree), {data}, []
    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        for line, label, (a, b), repl in edits(src, node, added):
            new = data[:a] + repl.encode("utf-8") + data[b:]
            if line in exempt or new in seen:
                continue
            seen.add(new)
            try:
                compile(new, "<mutant>", "exec")  # equivalent-mutant: the name only labels a traceback
            except SyntaxError:
                continue
            out.append(Mutant(line, label, new))
    return sorted(out, key=lambda m: m.line)


def fail_lines(output: str) -> set[str]:
    return {line.strip() for line in output.splitlines() if FAIL_LINE.match(line)}


def verdict(rc: int | None, output: str, baseline: set[str]) -> str:
    """killed only for a nonzero exit that names a failing case the baseline did not."""
    if rc is None:
        return "times out"
    if rc == 0:
        return "survives"
    return "killed" if fail_lines(output) - baseline else "crashes"


def run_suite(tree: Path, suite: str, timeout: float) -> tuple[int | None, str, float]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")  # equivalent-mutant: no .pyc is copied; ASCII reads alike
    start = time.monotonic()
    try:
        p = subprocess.run([sys.executable, suite], cwd=tree, env=env, capture_output=True,
                           encoding="utf-8", errors="replace", timeout=timeout)  # equivalent-mutant: see env
    except subprocess.TimeoutExpired:
        return None, "", time.monotonic() - start
    return p.returncode, p.stdout + p.stderr, time.monotonic() - start


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, encoding="utf-8",
                          errors="replace", check=True).stdout  # equivalent-mutant: git prints UTF-8 here


def make_tree(root: Path, parent: Path, n: int) -> Path:
    """A detached worktree at HEAD with the working tree's files (untracked included) on top."""
    tree = parent / f"t{n}"
    git(root, "worktree", "add", "--detach", "--quiet", str(tree), "HEAD")
    shutil.copytree(root, tree, ignore=IGNORE, dirs_exist_ok=True)
    for rel in git(root, "diff", "--name-only", "--diff-filter=D", "HEAD").splitlines():
        (tree / rel).unlink(missing_ok=True)
    return tree


def plan(root: Path, base: str) -> tuple[dict[str, list[Mutant]], list[str]]:
    """Mutants per changed script, and the errors for scripts with no paired suite."""
    found, errors = {}, []
    for rel in git(root, "diff", "--name-only", "--diff-filter=AM", base, "--", "scripts").splitlines():
        m = SCRIPT.fullmatch(rel)
        if not m:
            continue
        suite = f"scripts/test_{m[1]}.py"
        if not (root / suite).is_file():
            errors.append(f"{rel}: changed, but its paired suite {suite} does not exist: add it")
            continue
        added = added_lines(git(root, "diff", "-U0", base, "--", rel))
        found[rel] = mutants((root / rel).read_bytes(), added)
    return found, errors


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", help="revision to diff from (default: merge-base of HEAD and origin/main)")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 2))  # equivalent-mutant: speed only
    args = ap.parse_args(argv)
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
    base = args.base or git(root, "merge-base", "HEAD", "origin/main").strip()
    found, errors = plan(root, base)
    total = sum(len(v) for v in found.values())
    if total:
        errors += judge(root, found, max(1, min(args.jobs, total)))
    for line in errors:
        print(line)
    blocking = [e for e in errors if not e.startswith("note: ")]
    print(f"mutate_diff: {total} mutant(s) in {len(found)} script(s) from {base[:12]}: "
          f"{len(errors) - len(blocking)} note(s), "
          f"{'FAIL, ' + str(len(blocking)) + ' problem(s)' if blocking else 'no mutant survives'}")
    return 1 if blocking else 0


def judge(root: Path, found: dict[str, list[Mutant]], jobs: int) -> list[str]:
    parent = Path(tempfile.mkdtemp())
    trees: list[Path] = []
    try:
        for n in range(jobs):  # one at a time, so a failed add still leaves the earlier trees to remove
            trees.append(make_tree(root, parent, n))
        return judge_in(trees, found)
    finally:
        for tree in trees:  # --force: each tree holds overlaid and mutated files by design
            subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=root, capture_output=True)
        shutil.rmtree(parent, ignore_errors=True)


def judge_in(trees: list[Path], found: dict[str, list[Mutant]]) -> list[str]:
    errors, baselines = [], {}
    for rel in found:
        suite = "scripts/test_" + rel.removeprefix("scripts/")
        rc, out, secs = run_suite(trees[0], suite, 900)
        if rc != 0:
            errors.append(f"{rel}: {suite} fails before any mutation (rc={rc}), so no mutant can be judged: fix it first")
        else:
            baselines[rel] = (suite, fail_lines(out), max(60.0, 5 * secs))
    free: queue.Queue[Path] = queue.Queue()
    for tree in trees:
        free.put(tree)

    def one(rel: str, m: Mutant) -> str | None:
        suite, base_fails, timeout = baselines[rel]
        tree = free.get()
        target = tree / rel
        original = target.read_bytes()
        try:
            target.write_bytes(m.source)
            rc, out, _ = run_suite(tree, suite, timeout)
        finally:
            target.write_bytes(original)
            free.put(tree)
        v = verdict(rc, out, base_fails)
        if v == "killed":
            return None
        if v != "survives":  # the suite went red, just not through a named case: report, do not block
            return f"note: {rel}:{m.line} mutant {m.text} {v} {suite} without naming a failing case"
        return (f'{rel}:{m.line} mutant {m.text} survives {suite}: add a case that kills it, '
                f'or mark the line "{MARKER} <why>"')

    with ThreadPoolExecutor(len(trees)) as pool:
        results = [pool.submit(one, rel, m) for rel in baselines for m in found[rel]]
        errors += [r for r in (f.result() for f in results) if r]
    return errors


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
