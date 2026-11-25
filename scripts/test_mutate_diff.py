#!/usr/bin/env python3
"""Suite for scripts/mutate_diff.py.

In-process cases pin each operator, the added-lines filter, the skips, the exemption
marker and the kill rule. End-to-end cases build a throwaway git repository and run the
script on it: a clause no case kills is red, naming file, line and suite; a case that
kills it turns the run green; a script with no paired suite and a suite red before any
mutation are red; the working tree is never written and no worktree is left behind.

Run directly:  python scripts/test_mutate_diff.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mutate_diff as md  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: object = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + str(detail) if not ok and detail else ''}")
    if not ok:
        FAILURES.append(name)


def outs(src: str, added: set[int] | None = None) -> set[str]:
    data = src.encode("utf-8")
    lines = set(range(1, src.count("\n") + 2)) if added is None else added
    return {m.source.decode("utf-8") for m in md.mutants(data, lines)}


def case_operators() -> None:
    check("a statement is deleted", "pass\ny = 2\n" in outs("x = 1\ny = 2\n"))
    got = outs("if a and b:\n    pass\n")
    check("each and operand is dropped", {"if (b):\n    pass\n", "if (a):\n    pass\n"} <= got, got)
    got = outs("z = a or b\n")
    check("each or operand is dropped", {"z = (b)\n", "z = (a)\n"} <= got, got)
    got = outs("z = a == 1\n")
    check("a comparison becomes True and False", {"z = True\n", "z = False\n"} <= got, got)
    got = outs('P = ["a", "b"]\n')
    check("each list element is dropped", {'P = ["b"]\n', 'P = ["a"]\n'} <= got, got)
    check("a tuple keeps its comma", "T = (1,)\n" in outs("T = (1, 2)\n"))
    check("a set left empty is set()", "S = set()\n" in outs("S = {1}\n"))
    check("a string is emptied", 'fix = ""\n' in outs('fix = "upload it"\n'))
    got = outs('R = re.compile(r"^a|b(c|d)$")\n')
    check("each top-level regex branch is dropped",
          {"R = re.compile('b(c|d)$')\n", "R = re.compile('^a')\n"} <= got, got)
    check("the ^ anchor is dropped", "R = re.compile('a|b(c|d)$')\n" in got, got)
    check("the $ anchor is dropped", "R = re.compile('^a|b(c|d)')\n" in got, got)


def case_regex_split() -> None:
    check("| inside a group, class or escape does not split",
          md.split_branches(r"a(b|c)[|]\|d|e") == [r"a(b|c)[|]\|d", "e"], md.split_branches(r"a(b|c)[|]\|d|e"))
    check("an escaped $ keeps its anchor", ("drops the $ anchor", "a\\") not in md.regex_variants("a\\$"))
    check("a pattern with one branch drops none",
          not [v for v in md.regex_variants("abc") if v[0].startswith("drops branch")])


def case_scope() -> None:
    got = outs("x = 1\ny = a and b\n", {2})
    check("an unadded line is never mutated", all(g.startswith("x = 1\n") for g in got) and got, got)
    got = outs('def f(a: "int") -> list[str]:\n    """Doc."""\n    return f"{a}x"\n')
    check("docstrings, annotations and f-string parts are left alone",
          got == {'def f(a: "int") -> list[str]:\n    """Doc."""\n    pass\n'}, got)
    check("a def and an import are not deleted", not outs("import os\ndef f():\n    pass\n"))
    got = outs("R = C[[str], int]\n")
    check("a typing subscript keeps its list", got == {"pass\n"}, got)
    check("the marker exempts its line",
          outs("x = 1  # equivalent-mutant: log only\n") == set(), outs("x = 1  # equivalent-mutant: log only\n"))
    check("the marker exempts only its line", "x = 1  # equivalent-mutant: no\npass\n"
          in outs("x = 1  # equivalent-mutant: no\ny = 2\n"))
    src = 'a = "é"; b = "q"\r\n'.encode("utf-8")
    news = {m.source for m in md.mutants(src, {1})}
    check("byte offsets past non-ASCII and CRLF endings hold", 'a = "é"; b = ""\r\n'.encode("utf-8") in news, news)
    check("hunks give the added lines", md.added_lines("@@ -1 +2,3 @@\n@@ -9,2 +12 @@\n@@ -20 +30,0 @@") == {2, 3, 4, 12})


def case_kill_rule() -> None:
    check("a timeout is not a kill", md.verdict(None, "FAIL x", set()) == "times out")
    check("a passing suite means survival", md.verdict(0, "FAIL x", set()) == "survives")
    check("nonzero with a new FAIL line is a kill", md.verdict(1, "PASS a\nFAIL b\n", set()) == "killed")
    check("FAILED and ERROR lines name a case", md.verdict(1, "FAILED: 1", set()) == "killed"
          and md.verdict(1, "ERROR: t (m)", set()) == "killed")
    check("nonzero with no FAIL line is a crash", md.verdict(1, "Traceback ...\nNameError", set()) == "crashes")
    check("a FAIL line the baseline printed is no kill", md.verdict(1, "FAIL known", {"FAIL known"}) == "crashes")
    check("FAIL mid-line is not a case", md.verdict(1, "PASS rc=1 FAIL", set()) == "crashes")


SCRIPT = "def ok(n):\n    return n > 0\n"
CLAUSE = "def ok(n):\n    return n > 0 and n < 10\n"
SUITE = "import sys\nfrom foo import ok\nif not ok(1):\n    print('FAIL one')\n    sys.exit(1)\n"
KILLER = SUITE + "if ok(10) or ok(0):\n    print('FAIL bounds')\n    sys.exit(1)\n"


def repo(tmp: Path) -> Path:
    root = tmp / "r"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "foo.py").write_text(SCRIPT, encoding="utf-8")
    (root / "scripts" / "test_foo.py").write_text(SUITE, encoding="utf-8")
    for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, capture_output=True)
    return root


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HERE / "mutate_diff.py"), "--base", "HEAD", "--jobs", "2"],
                          cwd=root, capture_output=True, encoding="utf-8", errors="replace", timeout=300)


def case_end_to_end(tmp: Path) -> None:
    root = repo(tmp)
    (root / "scripts" / "foo.py").write_text(CLAUSE, encoding="utf-8")
    p = run(root)
    want = "scripts/foo.py:2 mutant drops `n < 10` from `and` survives scripts/test_foo.py"
    check("an unkilled clause is red and named", p.returncode == 1 and want in p.stdout, p.stdout + p.stderr)
    check("the working tree is not written", (root / "scripts" / "foo.py").read_text(encoding="utf-8") == CLAUSE)
    trees = subprocess.run(["git", "worktree", "list"], cwd=root, capture_output=True, encoding="utf-8").stdout
    check("no worktree is left behind", len(trees.splitlines()) == 1, trees)
    (root / "scripts" / "test_foo.py").write_text(KILLER, encoding="utf-8")
    p = run(root)
    check("a case that kills every mutant is green", p.returncode == 0 and "every mutant killed" in p.stdout,
          p.stdout + p.stderr)
    (root / "scripts" / "test_foo.py").write_text("import sys\nprint('FAIL red')\nsys.exit(1)\n", encoding="utf-8")
    p = run(root)
    check("a suite red before mutation gives no verdict", p.returncode == 1 and "fails before any mutation" in p.stdout,
          p.stdout + p.stderr)
    (root / "scripts" / "bar.py").write_text("X = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "scripts/bar.py"], cwd=root, check=True)
    p = run(root)
    check("a script with no paired suite is red", p.returncode == 1 and "scripts/test_bar.py does not exist" in p.stdout,
          p.stdout + p.stderr)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="test_mutate_diff_"))
    try:
        for name, case in [("operators", case_operators), ("regex split", case_regex_split), ("scope", case_scope),
                           ("kill rule", case_kill_rule), ("end to end", lambda: case_end_to_end(tmp))]:
            try:
                case()
            except Exception:  # a crash inside a case is that case failing, named
                check(f"{name} ran", False, traceback.format_exc(limit=1))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        return 1
    print("PASS: mutate_diff suite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
