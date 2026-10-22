"""Offline suite for check_installed_user_action.py (issue #364).

What this pins
    1. The verdict on one changeset, as literal values: a major changeset that
       ends with the action line passes; one without it, one whose line is
       empty after the colon, one whose line is not the last, one with text
       before the prefix, and one with a lowercase prefix are refused with the
       exact message; blank lines after the action line are tolerated; patch,
       minor and empty changesets pass without the line; a bump line the
       release gate's parser cannot read is refused.
    2. The command line, run the way CI runs it: exit code and full output on a
       planted tree, `.changeset/README.md` skipped, and a PASS over this
       repository's own pending changesets.

Run:  python scripts/test_check_installed_user_action.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_installed_user_action import verdict  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "check_installed_user_action.py"
REL = ".changeset/fixture.md"
MISSING = (
    ".changeset/fixture.md: declares a major bump and does not end with an "
    "'Action for installed users: <text>' line ('None.' is valid text)"
)

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def changeset(header: str, body: str) -> str:
    return f"---\n{header}---\n\n{body}"


MAJOR = '"mrbinnacle-skills": major\n'
PATCH = '"mrbinnacle-skills": patch\n'

VERDICT_CASES = (
    ("a major changeset ending with the line passes",
     changeset(MAJOR, "Rename every card.\n\nAction for installed users: None.\n"),
     (True, None)),
    ("a major changeset with action text passes",
     changeset(MAJOR, "Rename every card.\n\nAction for installed users: run `claude plugin update`.\n"),
     (True, None)),
    ("a major changeset without the line is refused",
     changeset(MAJOR, "Rename every card.\n"),
     (True, MISSING)),
    ("a major changeset whose line has no text is refused",
     changeset(MAJOR, "Rename every card.\n\nAction for installed users:\n"),
     (True, MISSING)),
    ("a major changeset whose line is not last is refused",
     changeset(MAJOR, "Action for installed users: None.\n\nRename every card.\n"),
     (True, MISSING)),
    ("a major changeset whose last line has text before the prefix is refused",
     changeset(MAJOR, "Rename every card.\n\nNote. Action for installed users: None.\n"),
     (True, MISSING)),
    ("a major changeset whose prefix is lowercase is refused",
     changeset(MAJOR, "Rename every card.\n\naction for installed users: None.\n"),
     (True, MISSING)),
    ("blank lines after the action line pass",
     changeset(MAJOR, "Rename every card.\n\nAction for installed users: None.\n\n  \n\n"),
     (True, None)),
    ("a major bump on one package of two needs the line",
     changeset('"a": patch\n"b": major\n', "Two packages.\n"),
     (True, MISSING)),
    ("CRLF line endings pass",
     changeset(MAJOR, "Rename.\n\nAction for installed users: None.\n").replace("\n", "\r\n"),
     (True, None)),
    ("a patch changeset without the line passes",
     changeset(PATCH, "Fix a typo.\n"),
     (False, None)),
    ("a minor changeset without the line passes",
     changeset('"mrbinnacle-skills": minor\n', "Admit a card.\n"),
     (False, None)),
    ("an empty changeset passes",
     "---\n---\n",
     (False, None)),
    ("an unreadable bump line is refused",
     changeset('"mrbinnacle-skills": !!str major\n', "Tagged.\n"),
     (False, ".changeset/fixture.md: cannot read its bump, so cannot tell whether it is major "
             "(has a frontmatter line the bump parser cannot read: "
             "'\"mrbinnacle-skills\": !!str major')")),
    ("a file with no frontmatter is refused",
     "Rename every card.\n",
     (False, ".changeset/fixture.md: cannot read its bump, so cannot tell whether it is major "
             "(frontmatter does not open with ---)")),
)


def verdict_cases() -> None:
    for name, text, expected in VERDICT_CASES:
        got = verdict(REL, text)
        check(name, got == expected, repr(got))


def run_cli(files: dict[str, str] | None) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        args = [sys.executable, str(SCRIPT)]
        if files is not None:
            Path(tmp, ".changeset").mkdir()
            for name, text in files.items():
                Path(tmp, ".changeset", name).write_text(text, encoding="utf-8", newline="")
            args += ["--root", tmp]
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout


def cli_cases() -> None:
    readme = "# Changesets\n\nPick the bump (patch / minor / major).\n"
    got = run_cli({
        "README.md": readme,
        "good-major.md": changeset(MAJOR, "Rename.\n\nAction for installed users: None.\n"),
        "patch.md": changeset(PATCH, "Fix.\n"),
    })
    check(
        "the command line passes a good tree and skips README.md",
        got == (0, "PASS: 2 changeset(s) read; each of the 1 major one(s) ends with an "
                   "'Action for installed users:' line\n"),
        repr(got),
    )
    got = run_cli({
        "a-bad.md": changeset(MAJOR, "Rename.\n"),
        "b-good.md": changeset(MAJOR, "Rename.\n\nAction for installed users: None.\n"),
    })
    check(
        "the command line exits 1 naming only the refused file",
        got == (1, "FAIL: .changeset/a-bad.md: declares a major bump and does not end with an "
                   "'Action for installed users: <text>' line ('None.' is valid text)\n"),
        repr(got),
    )
    code, out = run_cli(None)
    check(
        "this repository's pending changesets pass",
        code == 0 and out.startswith("PASS: ") and out.count("\n") == 1,
        repr((code, out)),
    )


def main() -> int:
    verdict_cases()
    cli_cases()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED")
        return 1
    print(
        "PASS: a major changeset must end with an 'Action for installed users:' line "
        "carrying text; minor, patch and empty changesets need none; an unreadable bump is refused"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
