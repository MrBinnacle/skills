#!/usr/bin/env python3
"""Suite for validate_skill_formats.py, including the poison controls.

A guard that has never rejected anything has not been shown to work, so every
rejection case here is built as a real tree on disk and run through the real
entrypoint as a subprocess -- not by calling a predicate in-process, which can
stay green while the command-line path is broken.

Poison trees are built in a temp directory rather than checked in. A checked-in
violating fixture would sit inside the guarded set (the walker discovers by
SKILL.md marker, repo-wide) and turn the real run permanently red, which would
have to be bought back with an exclusion list -- a hole in exactly the check
that exists to have no holes.

Run directly:  python scripts/test_validate_skill_formats.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GATE = SCRIPT_DIR / "validate_skill_formats.py"
READER_SH = SCRIPT_DIR / "check-installed-skills.sh"
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
import validate_skill_formats as gate  # noqa: E402

FAILURES: list[str] = []
NOTES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def note(text: str) -> None:
    """Record something the suite did NOT verify. Never silent."""
    print(f"note {text}")
    NOTES.append(text)


def run_gate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def make_skill(root: Path, relative: str, marker: str = "SKILL.md") -> Path:
    folder = root / relative
    folder.mkdir(parents=True, exist_ok=True)
    (folder / marker).write_text("# a skill\n", encoding="utf-8")
    return folder


# ---------------------------------------------------------------------------
# Green: the shapes that must pass
# ---------------------------------------------------------------------------


def case_clean_tree_passes(root: Path) -> None:
    folder = make_skill(root, "skills/engineering/example")
    (folder / "gotchas.md").write_text("notes\n", encoding="utf-8")
    (folder / "notes.txt").write_text("notes\n", encoding="utf-8")
    (folder / "helper.py").write_text("print('hi')\n", encoding="utf-8")
    (folder / "CONFIG.example.json").write_text("{}\n", encoding="utf-8")
    result = run_gate(root)
    check("clean tree passes", result.returncode == 0, result.stderr.strip())
    check(
        "clean tree reports a PASS line",
        result.stdout.startswith("PASS:"),
        result.stdout.strip(),
    )


def case_bytecode_with_source_passes(root: Path) -> None:
    folder = make_skill(root, "skills/engineering/example")
    (folder / "helper.py").write_text("print('hi')\n", encoding="utf-8")
    cache = folder / "__pycache__"
    cache.mkdir()
    (cache / "helper.cpython-313.pyc").write_bytes(b"\x00compiled\n")
    (cache / "helper.cpython-313-pytest-8.4.1.pyc").write_bytes(b"\x00compiled\n")
    result = run_gate(root)
    check(
        "compiled Python with its source beside it passes",
        result.returncode == 0,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# Poison controls: each must fail, and for the right reason
# ---------------------------------------------------------------------------


def case_planted_shell_script_is_red(root: Path) -> None:
    folder = make_skill(root, "skills/engineering/example")
    (folder / "install.sh").write_text("#!/bin/sh\necho hi\n", encoding="utf-8")
    result = run_gate(root)
    check("planted .sh is rejected", result.returncode != 0)
    check(
        "planted .sh is rejected for the right reason",
        "install.sh" in result.stderr and ".sh is not a declared" in result.stderr,
        result.stderr.strip(),
    )


def case_orphan_bytecode_is_red(root: Path) -> None:
    folder = make_skill(root, "skills/engineering/example")
    (folder / "helper.py").write_text("print('hi')\n", encoding="utf-8")
    cache = folder / "__pycache__"
    cache.mkdir()
    (cache / "evil.cpython-313.pyc").write_bytes(b"\x00compiled\n")
    result = run_gate(root)
    check("bytecode with no source is rejected", result.returncode != 0)
    check(
        "bytecode with no source is rejected for the right reason",
        "evil.cpython-313.pyc" in result.stderr
        and "no readable source" in result.stderr,
        result.stderr.strip(),
    )


def case_extensionless_file_is_red(root: Path) -> None:
    folder = make_skill(root, "skills/engineering/example")
    (folder / "Makefile").write_text("all:\n", encoding="utf-8")
    result = run_gate(root)
    check("extensionless file is rejected", result.returncode != 0)
    check(
        "extensionless file names the reason",
        "Makefile" in result.stderr and "no extension" in result.stderr,
        result.stderr.strip(),
    )


def case_all_violations_listed_not_first_fail(root: Path) -> None:
    folder = make_skill(root, "skills/engineering/example")
    for name in ("a.sh", "b.exe", "c.bin"):
        (folder / name).write_text("x\n", encoding="utf-8")
    result = run_gate(root)
    listed = sum(name in result.stderr for name in ("a.sh", "b.exe", "c.bin"))
    check("every violation is listed, not just the first", listed == 3, result.stderr)
    check("the count is reported", "3 file(s)" in result.stderr, result.stderr.strip())


# ---------------------------------------------------------------------------
# Discovery: the marker, not the path
# ---------------------------------------------------------------------------


def case_marker_outside_skills_dir_is_guarded(root: Path) -> None:
    """A path-scoped gate would never see this. The marker-scoped one must."""
    make_skill(root, "skills/engineering/example")
    fixture = make_skill(root, "scripts/fixtures/some-fixture/skills/meta/dummy")
    (fixture / "payload.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    result = run_gate(root)
    check(
        "a SKILL.md folder outside skills/ is inside the guarded set",
        result.returncode != 0 and "payload.sh" in result.stderr,
        result.stderr.strip(),
    )


def case_lookalike_filename_is_not_a_marker(root: Path) -> None:
    """`propose-a-skill.md` ends with 'skill.md'. It must not create a guarded set."""
    make_skill(root, "skills/engineering/example")
    template = root / ".github" / "ISSUE_TEMPLATE"
    template.mkdir(parents=True)
    (template / "propose-a-skill.md").write_text("# template\n", encoding="utf-8")
    (template / "config.yml").write_text("blank: true\n", encoding="utf-8")
    result = run_gate(root)
    check(
        "a lookalike filename does not make a folder a skill folder",
        result.returncode == 0,
        result.stderr.strip(),
    )


def case_empty_root_refuses_rather_than_passing(root: Path) -> None:
    (root / "README.md").write_text("nothing here\n", encoding="utf-8")
    result = run_gate(root)
    check(
        "a root with no skill folders is refused, not silently green",
        result.returncode != 0 and "no skill folders" in result.stderr,
        result.stderr.strip(),
    )


def case_symlinked_skill_folder_is_walked(root: Path) -> None:
    """Installs are symlinked. A walk that does not follow them guards nothing."""
    real = make_skill(root / "real", "example")
    (real / "payload.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    link = root / "linked"
    link.mkdir()
    try:
        (link / "example").symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        note(
            "symlink case SKIPPED on this host (needs Developer Mode on Windows): "
            f"{exc}. The linux CI cell exercises it."
        )
        return
    result = run_gate(link)
    check(
        "a symlinked skill folder is walked through the link",
        result.returncode != 0 and "payload.sh" in result.stderr,
        result.stderr.strip(),
    )


# ---------------------------------------------------------------------------
# The reader-side command must not drift from the predicate
# ---------------------------------------------------------------------------


def case_reader_command_is_derived() -> None:
    text = gate.reader_command()
    missing = [s for s in gate.ALLOWED_SUFFIXES if f"! -name '*{s}'" not in text]
    check("reader command names every declared suffix", not missing, str(missing))
    named = set(re.findall(r"! -name '\*(\.[A-Za-z0-9]+)'", text))
    check(
        "reader command names no suffix the walker does not allow",
        named == set(gate.ALLOWED_SUFFIXES),
        f"{sorted(named)} != {sorted(gate.ALLOWED_SUFFIXES)}",
    )
    check("reader command follows symlinks", "find -L" in text)


def case_reader_script_embeds_the_generated_command() -> None:
    if not READER_SH.is_file():
        check("reader script exists", False, f"missing {READER_SH}")
        return
    body = READER_SH.read_text(encoding="utf-8")
    expected = gate.reader_command('"$TARGET"')
    check(
        "reader script embeds the generated command verbatim",
        expected in body,
        "check-installed-skills.sh has drifted from reader_command()",
    )


def case_reader_script_agrees_with_the_walker(root: Path) -> None:
    """Run both instruments over one tree and require the same verdict."""
    shell = shutil.which("sh")
    if shell is None or not READER_SH.is_file():
        note("reader-script agreement SKIPPED: no POSIX sh on this host")
        return
    folder = make_skill(root, "example")
    (folder / "helper.py").write_text("print('hi')\n", encoding="utf-8")
    cache = folder / "__pycache__"
    cache.mkdir()
    (cache / "helper.cpython-313.pyc").write_bytes(b"\x00\n")

    clean_sh = subprocess.run(
        [shell, str(READER_SH), str(folder)], capture_output=True, text=True
    )
    clean_gate = run_gate(root)
    check(
        "walker and reader script agree that a clean folder is clean",
        clean_sh.returncode == 0 and clean_gate.returncode == 0,
        f"sh={clean_sh.returncode} gate={clean_gate.returncode} "
        f"{clean_sh.stderr.strip()} {clean_gate.stderr.strip()}",
    )

    (cache / "evil.cpython-313.pyc").write_bytes(b"\x00\n")
    (folder / "payload.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    dirty_sh = subprocess.run(
        [shell, str(READER_SH), str(folder)], capture_output=True, text=True
    )
    dirty_gate = run_gate(root)
    check(
        "walker and reader script agree that a dirty folder is dirty",
        dirty_sh.returncode == 1 and dirty_gate.returncode == 1,
        f"sh={dirty_sh.returncode} gate={dirty_gate.returncode}",
    )
    for name in ("payload.sh", "evil.cpython-313.pyc"):
        check(
            f"both instruments name {name}",
            name in dirty_sh.stderr and name in dirty_gate.stderr,
            f"sh={dirty_sh.stderr.strip()} gate={dirty_gate.stderr.strip()}",
        )


# ---------------------------------------------------------------------------
# The live tree
# ---------------------------------------------------------------------------


def case_repository_fixture_trees_are_guarded() -> None:
    """Acceptance: the fixture trees under scripts/fixtures/ are inside the set."""
    folders = gate.find_skill_folders(REPO_ROOT)
    relative = {gate.describe(REPO_ROOT, f) for f in folders}
    fixtures = {f for f in relative if f.startswith("scripts/fixtures/")}
    check(
        "fixture skill folders under scripts/fixtures/ are discovered",
        len(fixtures) >= 2,
        f"found {sorted(fixtures)}",
    )
    check(
        "published skill folders under skills/ are discovered",
        len({f for f in relative if f.startswith("skills/")}) >= 5,
        f"found {sorted(relative)}",
    )


def main() -> None:
    isolated = [
        case_clean_tree_passes,
        case_bytecode_with_source_passes,
        case_planted_shell_script_is_red,
        case_orphan_bytecode_is_red,
        case_extensionless_file_is_red,
        case_all_violations_listed_not_first_fail,
        case_marker_outside_skills_dir_is_guarded,
        case_lookalike_filename_is_not_a_marker,
        case_empty_root_refuses_rather_than_passing,
        case_symlinked_skill_folder_is_walked,
        case_reader_script_agrees_with_the_walker,
    ]
    for func in isolated:
        with tempfile.TemporaryDirectory() as tmp:
            func(Path(tmp))

    case_reader_command_is_derived()
    case_reader_script_embeds_the_generated_command()
    case_repository_fixture_trees_are_guarded()

    print("")
    for text in NOTES:
        print(f"NOT VERIFIED: {text}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: skill-format gate suite, all cases correct")


if __name__ == "__main__":
    main()
