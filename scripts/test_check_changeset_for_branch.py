"""Offline suite for check_changeset_for_branch.py.

What this pins
    1. The issue number read from a branch name, as literal values.
    2. The verdict: a numbered branch passes only on a changeset body citing
       its number, whatever the file times say; a frontmatter-only mention, a
       longer number and an HTML entity do not count; a branch with no number
       falls back to the file-time test and warns.
    3. The command line on a planted tree, including the replay of the #632
       false pass: every changeset newer than the base, none citing #632.
       Without --branch, GITHUB_HEAD_REF names the branch.

Run:  python scripts/test_check_changeset_for_branch.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_changeset_for_branch import Changeset, issue_number, verdict  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "check_changeset_for_branch.py"
BASE = 1_000.0

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def changeset(body: str) -> str:
    return f'---\n"mrbinnacle-skills": patch\n---\n\n{body}'


NUMBER_CASES = (
    ("fix/632-brand-kit-surfaces", "632"),
    ("feat/issue-632-x", "632"),
    ("feat/issue632", "632"),
    ("docs/gh-17-readme", "17"),
    ("fix/632", "632"),
    ("632-no-prefix", "632"),
    ("fix/changeset-step-content", None),
    ("automation/marketplace-pin-v3.1.0", None),
    ("chore/bump-node20", None),
    ("main", None),
    ("HEAD", None),
)


def number_cases() -> None:
    for branch, expected in NUMBER_CASES:
        got = issue_number(branch)
        check(f"issue number of {branch!r} is {expected!r}", got == expected, repr(got))


OLD_632 = Changeset("issue-632-brand-surfaces.md", changeset("Brand checks read buckets (#632).\n"), BASE - 5)
NEW_OTHER = Changeset("other.md", changeset("Something else (#630).\n"), BASE + 5)
NO_NUMBER = (
    "WARN: branch fix/changeset-step-content names no issue number, so this falls back to "
    "the weaker file-time check (a changeset modified after the merge-base commit). A copy "
    "of .changeset/ that does not keep file times passes it."
)
MISSING_632 = (
    "FAIL: branch fix/632-replay carries #632 but no changeset in .changeset/ mentions #632 "
    "in its body. Run npx changeset and cite #632."
)

VERDICT_CASES = (
    ("a numbered branch passes on an old changeset citing it",
     "fix/632-replay", [OLD_632],
     (True, ["PASS: branch fix/632-replay carries #632; .changeset/issue-632-brand-surfaces.md mentions it"])),
    ("a numbered branch fails when only unrelated changesets are newer than the base",
     "fix/632-replay", [NEW_OTHER], (False, [MISSING_632])),
    ("a mention in the frontmatter only does not count",
     "fix/632-replay",
     [Changeset("x.md", '---\n"mrbinnacle-skills": patch # 632 #632\n---\n\nNo cite.\n', BASE + 5)],
     (False, [MISSING_632])),
    ("#6320 does not cite #632",
     "fix/632-replay", [Changeset("x.md", changeset("See #6320.\n"), BASE + 5)], (False, [MISSING_632])),
    ("an HTML entity &#632; does not cite #632",
     "fix/632-replay", [Changeset("x.md", changeset("Glyph &#632; here.\n"), BASE + 5)],
     (False, [MISSING_632])),
    ("a branch with no number passes on a changeset newer than the base, with a warning",
     "fix/changeset-step-content", [OLD_632, NEW_OTHER],
     (True, [NO_NUMBER, "PASS: .changeset/other.md was modified after the merge-base commit"])),
    ("a branch with no number fails when every changeset is older than the base",
     "fix/changeset-step-content", [OLD_632],
     (False, [NO_NUMBER, "FAIL: this ref changes files but .changeset/ holds no changeset "
                         "modified after the merge-base commit. Run npx changeset."])),
)


def verdict_cases() -> None:
    for name, branch, changesets, expected in VERDICT_CASES:
        got = verdict(branch, changesets, BASE)
        check(name, got == expected, repr(got))


def run_cli(files: dict[str, str], branch: str | None, head_ref: str | None = None) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, ".changeset").mkdir()
        for name, text in files.items():
            path = Path(tmp, ".changeset", name)
            path.write_text(text, encoding="utf-8", newline="")
            os.utime(path, (BASE + 5, BASE + 5))
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_HEAD_REF"}
        if head_ref is not None:
            env["GITHUB_HEAD_REF"] = head_ref
        args = [sys.executable, str(SCRIPT), "--root", tmp, "--base-ts", str(BASE)]
        if branch is not None:
            args += ["--branch", branch]
        result = subprocess.run(args, capture_output=True, text=True, check=False, env=env)
        return result.returncode, result.stdout


def cli_cases() -> None:
    restored = {"README.md": "# Changesets\n\nSee #632.\n", "other.md": changeset("Unrelated (#630).\n")}
    got = run_cli(restored, "fix/632-replay")
    check(
        "the #632 replay fails though every changeset is newer than the base, and README.md is skipped",
        got == (1, MISSING_632 + "\n"),
        repr(got),
    )
    got = run_cli({**restored, "issue-632-brand-surfaces.md": OLD_632.text}, "fix/632-replay")
    check(
        "the #632 replay passes once its changeset is back",
        got == (0, "PASS: branch fix/632-replay carries #632; "
                   ".changeset/issue-632-brand-surfaces.md mentions it\n"),
        repr(got),
    )
    got = run_cli(restored, None, head_ref="fix/632-replay")
    check(
        "with no --branch, GITHUB_HEAD_REF names the branch",
        got == (1, MISSING_632 + "\n"),
        repr(got),
    )


def main() -> int:
    number_cases()
    verdict_cases()
    cli_cases()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED")
        return 1
    print(
        "PASS: a branch naming an issue needs a changeset body citing it, whatever the file "
        "times; a branch naming none falls back to the file-time test with a warning"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
