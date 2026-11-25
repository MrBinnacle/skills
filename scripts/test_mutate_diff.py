#!/usr/bin/env python3
"""Suite for scripts/mutate_diff.py.

In-process cases pin each operator, the added-lines filter, the skips, the exemption
marker, the de-duplication and compile filter, and the kill rule. End-to-end cases build
throwaway git repositories and run the script on them: a clause no case kills is red,
naming file, line and suite; a case that kills it turns the run green, with a crash as a
note; a script with no paired suite and a suite red before any mutation are red; the
default base is the merge-base with origin/main; the suites see git and the working tree's
deletions; one script's mutant never leaks into another script's run; the working tree
is never written, and no worktree or temporary folder is left behind.

Run directly:  python scripts/test_mutate_diff.py
"""
from __future__ import annotations

import os
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


def labels(src: str) -> list[str]:
    return [m.text for m in md.mutants(src.encode("utf-8"), set(range(1, src.count("\n") + 2)))]


def case_operators() -> None:
    check("a statement is deleted", "pass\ny = 2\n" in outs("x = 1\ny = 2\n"))
    got = outs("if a and b:\n    pass\n")
    check("each and operand is dropped", {"if (b):\n    pass\n", "if (a):\n    pass\n"} <= got, got)
    got = outs("z = a or b\n")
    check("each or operand is dropped", {"z = (b)\n", "z = (a)\n"} <= got, got)
    check("the or label names or", "drops `a` from `or`" in labels("z = a or b\n"), labels("z = a or b\n"))
    got = outs("z = a == 1\n")
    check("a comparison becomes True and False", {"z = True\n", "z = False\n"} <= got, got)
    got = outs('P = ["a", "b", "c"]\n')
    check("each list element is dropped", {'P = ["b", "c"]\n', 'P = ["a", "c"]\n'} <= got, got)
    got = outs("T = (1, 2, 3)\n")
    check("a tuple keeps its comma only when one item is left",
          "T = (2, 3)\n" in got and "T = (1,)\n" in outs("T = (1, 2)\n"), got)
    check("a set keeps its braces", "S = {2, 3}\n" in outs("S = {1, 2, 3}\n"), outs("S = {1, 2, 3}\n"))
    check("a set left empty is set()", "S = set()\n" in outs("S = {1}\n"))
    check("a string is emptied", 'fix = ""\n' in outs('fix = "upload it"\n'))
    check("an empty string, a pass and a duplicate give nothing new",
          outs('x = ""\n') == {"pass\n"} and outs("pass\n") == set()
          and [m.source for m in md.mutants(b"z = a or a\n", {1})].count(b"z = (a)\n") == 1)
    check("a mutant that does not compile is dropped",
          "def f():\n    pass\n    def g():\n        nonlocal x\n"
          not in outs("def f():\n    x = 1\n    def g():\n        nonlocal x\n"))
    got = outs('R = re.compile(r"^a|b(c|d)$")\n')
    check("each top-level regex branch is dropped",
          {"R = re.compile('b(c|d)$')\n", "R = re.compile('^a')\n"} <= got, got)
    check("the ^ anchor is dropped", "R = re.compile('a|b(c|d)$')\n" in got, got)
    check("the $ anchor is dropped", "R = re.compile('^a|b(c|d)')\n" in got, got)
    others = ['R = x.compile("a|b")\n', 'R = re.search("a|b")\n', 'R = compile("a|b")\n', "R = re.compile(p)\n",
              "R = re.compile()\n", 'R = re.compile(b"a|b")\n', 'R = re.compile(f"a|{b}")\n']
    hits = [s for s in others if any(t.endswith(" in re.compile") for t in labels(s))]
    check("only a re.compile string literal gets regex mutants", not hits, hits)


def case_regex_split() -> None:
    check("| inside a group, class or escape does not split",
          md.split_branches(r"a(b|c)[|]\|d|e") == [r"a(b|c)[|]\|d", "e"], md.split_branches(r"a(b|c)[|]\|d|e"))
    check("a class ends at ]", md.split_branches("[a]|b") == ["[a]", "b"], md.split_branches("[a]|b"))
    want = [("drops branch '^a'", "b$"), ("drops branch 'b$'", "^a"), ("drops the ^ anchor", "a|b$"),
            ("drops the $ anchor", "^a|b")]
    check("regex variants are exactly the branches and anchors", md.regex_variants("^a|b$") == want,
          md.regex_variants("^a|b$"))
    check("a pattern with no anchor or branch gives none", md.regex_variants("ab") == [], md.regex_variants("ab"))
    check("an escaped $ keeps its anchor", md.regex_variants("a\\$") == [], md.regex_variants("a\\$"))


def case_scope() -> None:
    got = outs("x = 1\ny = a and b\nz = a == 1\nw = 'q'\nv = [a]\n", {2})
    check("an unadded line is never mutated", got and all(g.startswith("x = 1\n") and "'q'" in g and "[a]" in g
                                                          and "a == 1" in g for g in got), got)
    got = outs('def f(a: "int") -> list[str]:\n    """Doc."""\n    return f"{a}x"\n')
    check("docstrings, annotations and f-string parts are left alone",
          got == {'def f(a: "int") -> list[str]:\n    """Doc."""\n    pass\n'}, got)
    got = outs('async def f(*a: "s", **k: "t") -> "u":\n    pass\nx: "v" = 1\n')
    check("async, vararg, kwarg, return and variable annotations are left alone", got == {
        'async def f(*a: "s", **k: "t") -> "u":\n    pass\npass\n'}, got)
    src = ("import os\nfrom os import path\nclass C:\n    pass\nasync def f():\n    pass\n"
           "def g():\n    global G\n    def h():\n        nonlocal G\n")
    check("no def, class, import, global or nonlocal is deleted", not [t for t in labels(src) if "deletes" in t],
          labels(src))
    check("a non-string expression statement is deleted", "pass\n" in outs("f(1)\n"))
    check("a string subscript and keyword are still emptied",
          {'d[""]\n', 'f(x="")\n'} <= outs('d["k"]\n') | outs('f(x="v")\n'))
    got = outs('if __name__ == "__main__":\n    main(a and b)\n')
    check("the main guard block is left alone", not got, got)
    got = outs('ap.add_argument("--x", help="text", description="more")\n')
    check("help and description text is left alone",
          got == {'ap.add_argument("", help="text", description="more")\n', "pass\n"}, got)
    got = outs("R = C[[str], int]\nQ = C[[a, b]]\n")
    check("a typing subscript keeps its list", got == {"pass\nQ = C[[a, b]]\n", "R = C[[str], int]\npass\n"}, got)
    check("a stored tuple keeps its targets", outs("a, b = f()\n") == {"pass\n"}, outs("a, b = f()\n"))
    check("the marker exempts its line",
          outs("x = 1  # equivalent-mutant: log only\n") == set(), outs("x = 1  # equivalent-mutant: log only\n"))
    check("the marker exempts only its line", "x = 1  # equivalent-mutant: no\npass\n"
          in outs("x = 1  # equivalent-mutant: no\ny = 2\n"))
    src = 'a = "é"; b = "q"\r\n'.encode("utf-8")
    news = {m.source for m in md.mutants(src, {1})}
    check("byte offsets past non-ASCII and CRLF endings hold", 'a = "é"; b = ""\r\n'.encode("utf-8") in news, news)
    check("hunks give the added lines", md.added_lines("@@ -1 +2,3 @@\n@@ -9,2 +12 @@\n@@ -20 +30,0 @@") == {2, 3, 4, 12})
    check("a hunk header inside a line is no hunk", md.added_lines('@@ -1 +2 @@\n+s = "@@ -1 +9 @@"\n') == {2})
    check("only scripts/<name>.py that is not a test is a target",
          md.SCRIPT.fullmatch("scripts/ci_local.py")[1] == "ci_local"
          and not any(md.SCRIPT.fullmatch(p) for p in ("scripts/test_x.py", "scripts/a/b.py", "scripts/x.pyc")))
    check("labels are one short line", md.short("a\n   b") == "a b" and md.short("x" * 60) == "x" * 60
          and md.short("x" * 61) == "x" * 57 + "...")


def case_kill_rule() -> None:
    check("a timeout is not a kill", md.verdict(None, "FAIL x", set()) == "times out")
    check("a passing suite means survival", md.verdict(0, "FAIL x", set()) == "survives")
    check("nonzero with a new FAIL line is a kill", md.verdict(1, "PASS a\nFAIL b\n", set()) == "killed")
    check("FAILED and ERROR lines name a case", md.verdict(1, "FAILED: 1", set()) == "killed"
          and md.verdict(1, "  ERROR: t (m)", set()) == "killed")
    check("nonzero with no FAIL line is a crash", md.verdict(1, "Traceback ...\nNameError", set()) == "crashes")
    check("a FAIL line the baseline printed is no kill", md.verdict(1, "FAIL known", {"FAIL known"}) == "crashes")
    check("FAIL mid-line is not a case", md.verdict(1, "PASS rc=1 FAIL", set()) == "crashes")


def case_timeout(tmp: Path) -> None:
    (tmp / "slow.py").write_text("import time\ntime.sleep(20)\n", encoding="utf-8")
    rc, out, secs = md.run_suite(tmp, "slow.py", 1)
    check("a suite past its timeout returns no exit code", rc is None and out == "" and 0.5 < secs < 15, (rc, out, secs))


SCRIPT = "def ok(n):\n    return n > 0\n"
CLAUSE = "def ok(n):\n    lim = 10\n    return n > 0 and n < lim\n"
SUITE = ("import os, subprocess, sys\nfrom foo import ok\n"
         "subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, capture_output=True)\n"
         "if os.path.exists('scripts/gone.txt'):\n    print('FAIL deleted file is back')\n    sys.exit(1)\n"
         "if not ok(1):\n    print('FAIL one')\n    sys.exit(1)\n")
KILLER = SUITE + "if ok(10) or ok(0):\n    print('FAIL bounds')\n    sys.exit(1)\n"


def repo(tmp: Path, files: dict[str, str]) -> Path:
    root = tmp / "r"
    (root / "scripts").mkdir(parents=True)
    for rel, text in files.items():
        (root / rel).write_text(text, encoding="utf-8")
    for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"],
                ["update-ref", "refs/remotes/origin/main", "HEAD"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, capture_output=True)
    return root


def run(root: Path, tmp: Path, *args: str) -> subprocess.CompletedProcess:
    scratch = tmp / "tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMP=str(scratch), TEMP=str(scratch), TMPDIR=str(scratch))
    return subprocess.run([sys.executable, str(HERE / "mutate_diff.py"), "--jobs", "2", *args], cwd=root, env=env,
                          capture_output=True, encoding="utf-8", errors="replace", timeout=300)


def clean(root: Path, tmp: Path) -> bool:
    trees = subprocess.run(["git", "worktree", "list"], cwd=root, capture_output=True, encoding="utf-8").stdout
    return len(trees.splitlines()) == 1 and not any((tmp / "tmp").iterdir())


def case_end_to_end(tmp: Path) -> None:
    root = repo(tmp, {"scripts/foo.py": SCRIPT, "scripts/test_foo.py": SUITE, "scripts/gone.txt": "x\n"})
    (root / "scripts" / "gone.txt").unlink()
    (root / "scripts" / "foo.py").write_text(CLAUSE, encoding="utf-8")
    p = run(root, tmp)
    want = "scripts/foo.py:3 mutant drops `n < lim` from `and` survives scripts/test_foo.py"
    check("an unkilled clause is red and named, from origin/main by default",
          p.returncode == 1 and want in p.stdout, p.stdout + p.stderr)
    check("the working tree is not written", (root / "scripts" / "foo.py").read_text(encoding="utf-8") == CLAUSE)
    check("no worktree or temporary folder is left behind", clean(root, tmp))
    (root / "scripts" / "test_foo.py").write_text(KILLER, encoding="utf-8")
    p = run(root, tmp, "--base", "HEAD")
    check("a case that kills every mutant is green", p.returncode == 0 and "no mutant survives" in p.stdout,
          p.stdout + p.stderr)
    note = "note: scripts/foo.py:2 mutant deletes `lim = 10` crashes scripts/test_foo.py without naming a failing case"
    notes = [line for line in p.stdout.splitlines() if line.startswith("note:")]
    check("a crash is a note, and a killed mutant prints nothing", notes == [note], p.stdout)
    (root / "scripts" / "bar.py").write_text("X = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "scripts/bar.py"], cwd=root, check=True)
    p = run(root, tmp, "--base", "HEAD")
    check("a script with no paired suite is red, and only that",
          p.returncode == 1 and "scripts/test_bar.py does not exist" in p.stdout and "bar.py:1" not in p.stdout
          and "fails before" not in p.stdout,
          p.stdout + p.stderr)
    (root / "scripts" / "test_foo.py").write_text("import sys\nprint('FAIL red')\nsys.exit(1)\n", encoding="utf-8")
    p = run(root, tmp, "--base", "HEAD")
    check("a suite red before mutation gives no verdict", p.returncode == 1 and "fails before any mutation" in p.stdout,
          p.stdout + p.stderr)


def case_no_leak(tmp: Path) -> None:
    """With one tree, the last foo.py mutant breaks ok(1); zed's run must still see the real foo.py."""
    root = repo(tmp, {"scripts/foo.py": "def ok(n):\n    return 1\n", "scripts/zed.py": "",
                      "scripts/test_foo.py": "", "scripts/test_zed.py":
                      "import sys\nfrom foo import ok\nif not ok(1):\n    print('FAIL foo leaked')\n    sys.exit(1)\n"})
    (root / "scripts" / "foo.py").write_text("def ok(n):\n    return n > 0\n", encoding="utf-8")
    (root / "scripts" / "zed.py").write_text("Y = 1\n", encoding="utf-8")
    p = run(root, tmp, "--base", "HEAD", "--jobs", "1")
    check("a mutant of one script never reaches another script's run",
          "scripts/zed.py:1 mutant deletes `Y = 1` survives" in p.stdout, p.stdout + p.stderr)


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    try:
        cases = [("operators", case_operators), ("regex split", case_regex_split), ("scope", case_scope),
                 ("kill rule", case_kill_rule), ("timeout", lambda: case_timeout(tmp)),
                 ("end to end", lambda: case_end_to_end(tmp / "a")), ("no leak", lambda: case_no_leak(tmp / "b"))]
        for name, case in cases:
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
