#!/usr/bin/env python3
"""Suite for check_shared_readers.py: a new copy of an owned reader is refused, an old one stands.

    Cases:
      - each reader shape is found outside its owner and ignored inside it;
      - a regex that only quotes the flag in an error message is not a reader;
      - in a temp repository, a commit that adds a second `iter_skill_dirs` or a
        load-mode regex goes red naming the owner to use, and a commit that
        leaves an older copy in place stays green.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import check_shared_readers as csr  # noqa: E402

FAILURES: list[str] = []
LOAD_REGEX = 're.compile(r"^disable-model-invocation:\\s*true\\s*$", re.MULTILINE)'


def check(case: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  ok   {case}")
    else:
        FAILURES.append(case)
        print(f"  FAIL {case}: {detail}")


def case_reader_shapes() -> None:
    kinds = {
        "def iter_skill_dirs(root):\n    return []\n": "iter_skill_dirs",
        f"import re\nFLAG_RE = {LOAD_REGEX}\n": "load-mode flag",
        'KEY = "disable-model-invocation"\n': "load-mode flag",
        "from validate_standing_costs import DISABLE_MODEL_INVOCATION_RE\n": "load-mode flag",
        "from validate_card_files import BY_HAND_RE\n": "load-mode flag",
        "import validate_standing_costs as sc\nsc.DISABLE_MODEL_INVOCATION_RE.search(text)\n": "load-mode flag",
    }
    for source, kind in kinds.items():
        found = csr.readers("scripts/other.py", source)
        check(f"found outside the owner: {source.splitlines()[-1].strip()}", {r[1] for r in found} == {kind}, str(found))
        owner = csr.OWNERS[kind][0]
        check(f"ignored inside {owner}: {source.splitlines()[-1].strip()}", not csr.readers(owner, source))
    quoted = 'import re\nMSG = re.compile(r"^Unexpected fields in frontmatter: disable-model-invocation\\.")\n'
    check("an error-message regex is not a reader", not csr.readers("scripts/other.py", quoted))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, encoding="utf-8"
    ).stdout.strip()


def run_check(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "check_shared_readers.py"), "--base", "base"],
        capture_output=True, text=True, encoding="utf-8",
    )


def case_only_additions_fail(tmp: Path) -> None:
    repo = tmp / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(SCRIPT_DIR / "check_shared_readers.py", repo / "scripts")
    (repo / "scripts" / "old.py").write_text(f"import re\nOLD_RE = {LOAD_REGEX}\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "suite@example.invalid")
    git(repo, "config", "user.name", "suite")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "branch", "base")

    (repo / "scripts" / "old.py").write_text(f"import re\n\nOLD_RE = {LOAD_REGEX}  # moved\n", encoding="utf-8")
    git(repo, "commit", "-qam", "touch the old copy")
    result = run_check(repo)
    check("an older copy, edited in place, stays green", result.returncode == 0, result.stdout)

    (repo / "scripts" / "new.py").write_text("def iter_skill_dirs(root):\n    return []\n", encoding="utf-8")
    (repo / "scripts" / "flag.py").write_text(f"import re\nNEW_RE = {LOAD_REGEX}\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "add two copies")
    result = run_check(repo)
    check(
        "an added iter_skill_dirs and an added load-mode regex go red, naming the owner",
        result.returncode == 1
        and "scripts/new.py: a second iter_skill_dirs reader" in result.stdout
        and "import iter_skill_dirs from scripts/validate_scoreboard.py" in result.stdout
        and "scripts/flag.py: a second load-mode flag reader" in result.stdout
        and "runs_by_hand or flag_set from scripts/check_load_mode_markers.py" in result.stdout
        and "old.py" not in result.stdout,
        result.stdout,
    )


def case_live_tree() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "check_shared_readers.py"), "--list"],
        capture_output=True, text=True, encoding="utf-8",
    )
    check("no iter_skill_dirs copy remains outside its owner", "iter_skill_dirs" not in result.stdout, result.stdout)


def main() -> None:
    case_reader_shapes()
    with tempfile.TemporaryDirectory() as tmp:
        case_only_additions_fail(Path(tmp))
    case_live_tree()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print("PASS: shared-reader check refuses a new reader copy and lets an older one stand")


if __name__ == "__main__":
    main()
