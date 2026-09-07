#!/usr/bin/env python3
"""Suite: the vale-prose hook and CI's Vale job lint the SAME set of paths (#244).

THE DEFECT

    CI ran `vale README.md skills/ docs/`; the hook took every staged `.md`.
    The hook refused commits CI accepted, and the skip became routine. #244
    chose option 1: narrow the hook to CI's three paths. This suite is what
    keeps the two sites agreeing after someone edits one of them.

HOW AGREEMENT IS PROVEN WITHOUT TRUSTING EITHER SITE'S COMMENT

    Both scopes are READ from their files - the hook's `files:` regex out of
    `.pre-commit-config.yaml`, the path arguments out of the two `vale` lines in
    `.github/workflows/vale.yml` - and applied to every tracked path in the live
    tree plus a fixed list of edge cases (`_quarantine/x/SKILL.md`, a `docsx/`
    prefix trap, non-markdown files under a linted directory). The two
    partitions must be identical.

    CI's predicate needs one fact about Vale: it lints only files that match a
    format section in `.vale.ini`, so "walk `skills/`" means "every `.md` under
    `skills/`". The suite reads `.vale.ini` and asserts every section is a
    markdown glob, so that fact is measured and not assumed.

    The comparison is proven non-vacuous by mutating the hook regex back to the
    defective every-markdown pattern and asserting the partitions then DIFFER.

WHEN VALE IS INSTALLED

    The last case plants the same error-level violation - an emoji, which
    `Taste.Dressing` refuses at error level - in `docs/` and in `_quarantine/`
    inside a temporary tree, runs CI's exact command there, and asserts it fails
    naming only the `docs/` file; the hook side is then the regex admitting the
    `docs/` path and rejecting the `_quarantine/` one, and `vale_hook.py` failing
    on the admitted file. Without the binary that case reports SKIPPED, the same
    way `vale_hook.py` itself skips; the partition proof above does not need it.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRE_COMMIT = REPO_ROOT / ".pre-commit-config.yaml"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "vale.yml"
VALE_INI = REPO_ROOT / ".vale.ini"
VALE_HOOK = REPO_ROOT / "scripts" / "vale_hook.py"

# U+2705 WHITE HEAVY CHECK MARK, an emoji Taste.Dressing refuses at error level.
# Built from its code point so this source file stays ASCII for the Windows console.
POISON_LINE = "This line carries a dressing emoji " + chr(0x2705) + " that the Taste style refuses.\n"

EDGE_CASES = (
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "skills/engineering/a-card/SKILL.md",
    "skills/engineering/a-card/helper.py",
    "skills/README.md",
    "docs/adr/0001-something.md",
    "docs/notes.txt",
    "_quarantine/x/SKILL.md",
    "_quarantine/README.md",
    ".changeset/some-change.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "styles/Taste/Voice.yml",
    "docsx/trap.md",
    "skillsx/trap.md",
    "README.md.bak",
    "sub/README.md",
)

FAILURES: list[str] = []


def fail(case: str, detail: str) -> None:
    FAILURES.append(case)
    print(f"  FAIL {case}: {detail}")


def read_hook_regex(text: str) -> str:
    block = re.search(r"- id: vale-prose\n(?:.*\n)*?\s+files: '([^']+)'", text)
    if block is None:
        raise SystemExit("could not find the vale-prose hook's files: regex")
    return block.group(1)


def read_ci_paths(text: str) -> list[list[str]]:
    """The positional paths of every `vale --config .vale.ini ...` line in the workflow."""
    found: list[list[str]] = []
    for line in text.splitlines():
        m = re.search(r"\bvale --config \.vale\.ini((?: \S+)+)\s*$", line)
        if m is None:
            continue
        found.append([tok for tok in m.group(1).split() if not tok.startswith("--")])
    return found


def read_ini_sections(text: str) -> list[str]:
    return re.findall(r"^\[([^\]]+)\]\s*$", text, re.M)


def ci_predicate(paths: list[str]):
    dirs = tuple(p for p in paths if p.endswith("/"))
    files = frozenset(p for p in paths if not p.endswith("/"))

    def in_ci(path: str) -> bool:
        if not path.endswith(".md"):
            return False
        return path in files or any(path.startswith(d) for d in dirs)

    return in_ci


def partition(predicate, sample: list[str]) -> frozenset[str]:
    return frozenset(p for p in sample if predicate(p))


def tracked_paths() -> list[str]:
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z"], capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def case_workflow_lines_agree(ci_lists: list[list[str]]) -> None:
    case = "case_workflow_lines_agree"
    if len(ci_lists) < 2:
        fail(case, f"expected the report and gate vale lines in vale.yml, found {len(ci_lists)}")
        return
    if any(lst != ci_lists[0] for lst in ci_lists[1:]):
        fail(case, f"the vale lines in vale.yml lint different paths: {ci_lists}")
        return
    print(f"  ok   {case}: {len(ci_lists)} vale lines, paths {ci_lists[0]}")


def case_ini_sections_are_markdown_globs(sections: list[str]) -> None:
    case = "case_ini_sections_are_markdown_globs"
    if not sections:
        fail(case, ".vale.ini has no format sections - the CI predicate has no basis")
        return
    bad = [s for s in sections if not s.endswith(".md")]
    if bad:
        fail(case, f"non-markdown sections in .vale.ini: {bad}; the CI predicate must widen")
        return
    print(f"  ok   {case}: {sections}")


def case_partitions_agree(hook_regex: str, in_ci, sample: list[str], label: str) -> None:
    case = f"case_partitions_agree_{label}"
    hook = re.compile(hook_regex)
    hook_set = partition(lambda p: hook.search(p) is not None, sample)
    ci_set = partition(in_ci, sample)
    if hook_set != ci_set:
        only_hook = sorted(hook_set - ci_set)[:10]
        only_ci = sorted(ci_set - hook_set)[:10]
        fail(case, f"hook-only {only_hook}; ci-only {only_ci}")
        return
    print(f"  ok   {case}: {len(sample)} paths, {len(ci_set)} in scope at both sites")


def case_quarantine_is_outside_both(hook_regex: str, in_ci) -> None:
    case = "case_quarantine_is_outside_both"
    path = "_quarantine/x/SKILL.md"
    if re.search(hook_regex, path) or in_ci(path):
        fail(case, f"{path} is linted at a site; #244 refused widening to _quarantine/")
        return
    print(f"  ok   {case}")


def case_defective_regex_is_detected(in_ci, sample: list[str]) -> None:
    """The comparison must go red on the pre-#244 hook scope, or it proves nothing."""
    case = "case_defective_regex_is_detected"
    hook = re.compile(r"\.md$")
    hook_set = partition(lambda p: hook.search(p) is not None, sample)
    ci_set = partition(in_ci, sample)
    if hook_set == ci_set:
        fail(case, "the old every-.md regex partitions the sample the same as CI - the sample cannot tell the scopes apart")
        return
    print(f"  ok   {case}: old regex admits {len(hook_set - ci_set)} path(s) CI never lints")


def case_error_level_violation_fails_inside_and_not_outside(hook_regex: str, ci_paths: list[str], tmp: Path) -> None:
    case = "case_error_level_violation_fails_inside_and_not_outside"
    vale = shutil.which("vale")
    if vale is None:
        print(f"  SKIP {case}: vale is not installed here; CI installs it and runs this case")
        return
    shutil.copy(VALE_INI, tmp / ".vale.ini")
    shutil.copytree(REPO_ROOT / "styles", tmp / "styles")
    inside, outside = "docs/poison.md", "_quarantine/poison/SKILL.md"
    for rel, text in (("README.md", "# Clean\n"), ("skills/README.md", "# Clean\n"), (inside, POISON_LINE), (outside, POISON_LINE)):
        target = tmp / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    ci = subprocess.run(
        [vale, "--config", ".vale.ini", "--minAlertLevel=error", "--output=line", *ci_paths],
        cwd=tmp, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if ci.returncode == 0:
        fail(case, "CI's command accepted a tree with an error-level violation in docs/ - the poison is not poison")
        return
    if "poison.md" not in ci.stdout.replace("\\", "/") or "_quarantine" in ci.stdout:
        fail(case, f"CI's command named the wrong file(s):\n{ci.stdout}")
        return
    hook = re.compile(hook_regex)
    if hook.search(inside) is None or hook.search(outside) is not None:
        fail(case, "the hook regex does not admit docs/ while rejecting _quarantine/")
        return
    hook_run = subprocess.run(
        [sys.executable, str(VALE_HOOK), str(tmp / inside)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if hook_run.returncode == 0:
        fail(case, "vale_hook.py accepted the in-scope violation, so 'fails both' does not hold")
        return
    print(f"  ok   {case}: CI refused {inside} only; the hook admits it and refuses it, and never sees {outside}")


def main() -> None:
    hook_regex = read_hook_regex(PRE_COMMIT.read_text(encoding="utf-8"))
    ci_lists = read_ci_paths(WORKFLOW.read_text(encoding="utf-8"))
    sections = read_ini_sections(VALE_INI.read_text(encoding="utf-8"))

    case_workflow_lines_agree(ci_lists)
    case_ini_sections_are_markdown_globs(sections)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)

    ci_paths = ci_lists[0]
    in_ci = ci_predicate(ci_paths)
    live = tracked_paths()
    case_partitions_agree(hook_regex, in_ci, list(EDGE_CASES), "edge_cases")
    case_partitions_agree(hook_regex, in_ci, live, "live_tree")
    case_quarantine_is_outside_both(hook_regex, in_ci)
    case_defective_regex_is_detected(in_ci, list(EDGE_CASES) + live)
    with tempfile.TemporaryDirectory() as tmp:
        case_error_level_violation_fails_inside_and_not_outside(hook_regex, ci_paths, Path(tmp))

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: vale scope - hook regex {hook_regex!r} and CI paths {ci_paths} partition "
        f"{len(EDGE_CASES)} edge cases and {len(live)} live tracked paths identically; "
        "the comparison is proven non-vacuous against the pre-#244 regex."
    )


if __name__ == "__main__":
    main()
