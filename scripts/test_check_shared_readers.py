#!/usr/bin/env python3
"""Suite for check_shared_readers.py: a new copy of an owned reader is refused, an old one stands.

    Cases:
      - each reader shape is found outside its owner and ignored inside it;
      - a regex that only quotes the flag in an error message is not a reader;
      - a fixture write of the landing page and a path string in data are not readers;
      - test_install_form.py at e5e3e6d, the raw read #696 broke, is a landing-page reader;
      - in a temp repository, a commit that adds a second `iter_skill_dirs`, a
        load-mode regex or a raw landing-page read goes red naming the owner to
        use, and a commit that leaves an older copy in place stays green;
      - on the live tree, only the three landing-page reads that predate the owner remain.
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
# test_install_form.py's raw read at e5e3e6d, the one #696 broke and #706 fixed.
PAGE_READ = 'SITE = ROOT / "site" / "index.html"\nsite = SITE.read_text(encoding="utf-8")\n'
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
        PAGE_READ: "landing page",
        'html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")\n': "landing page",
        'PAGE: Path = ROOT / "site/index.html"\nPAGE.read_bytes()\n': "landing page",
    }
    for source, kind in kinds.items():
        found = csr.readers("scripts/other.py", source)
        check(f"found outside the owner: {source.splitlines()[-1].strip()}", {r[1] for r in found} == {kind}, str(found))
        owner = csr.OWNERS[kind][0]
        check(f"ignored inside {owner}: {source.splitlines()[-1].strip()}", not csr.readers(owner, source))
    quoted = 'import re\nMSG = re.compile(r"^Unexpected fields in frontmatter: disable-model-invocation\\.")\n'
    check("an error-message regex is not a reader", not csr.readers("scripts/other.py", quoted))
    write = 'page = tmp / "site" / "index.html"\npage.write_text(html, encoding="utf-8")\n'
    check("a fixture write of the landing page is not a reader", not csr.readers("scripts/other.py", write))
    data = 'SURFACES = [("site/index.html", "first-person sentence")]\nMSG = f"expected {x!r} in site/index.html"\n'
    check("a path string in data or a message is not a reader", not csr.readers("scripts/other.py", data))


def case_real_mistake() -> None:
    source = git(SCRIPT_DIR.parent, "show", "e5e3e6d:scripts/test_install_form.py")
    found = csr.readers("scripts/test_install_form.py", source)
    check("test_install_form.py at e5e3e6d is a landing-page reader", {r[1] for r in found} == {"landing page"},
          str(found))


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
    (repo / "scripts" / "site_read.py").write_text(PAGE_READ, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "add three copies")
    result = run_check(repo)
    check(
        "an added iter_skill_dirs, load-mode regex and landing-page read go red, naming the owner",
        result.returncode == 1
        and "scripts/new.py: a second iter_skill_dirs reader" in result.stdout
        and "import iter_skill_dirs from scripts/validate_scoreboard.py" in result.stdout
        and "scripts/flag.py: a second load-mode flag reader" in result.stdout
        and "runs_by_hand or flag_set from scripts/check_load_mode_markers.py" in result.stdout
        and "scripts/site_read.py: a second landing page reader" in result.stdout
        and "call landing_page from scripts/validate_site_links.py" in result.stdout
        and "old.py" not in result.stdout,
        result.stdout,
    )


def case_live_tree() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "check_shared_readers.py"), "--list"],
        capture_output=True, text=True, encoding="utf-8",
    )
    check("no iter_skill_dirs copy remains outside its owner", "iter_skill_dirs" not in result.stdout, result.stdout)
    check("the checker does not count itself", csr.SELF not in result.stdout, result.stdout)
    pages = sorted(line.split(":")[0].strip() for line in result.stdout.splitlines() if ": landing page:" in line)
    check("only the three landing-page reads that predate the owner remain", pages == [
        "scripts/test_release_model_disclosure.py", "scripts/test_validate_brand_kit.py",
        "scripts/test_validate_site_links.py"], str(pages))


def main() -> None:
    case_reader_shapes()
    case_real_mistake()
    with tempfile.TemporaryDirectory() as tmp:
        case_only_additions_fail(Path(tmp))
    case_live_tree()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print("PASS: shared-reader check refuses a new reader copy and lets an older one stand")


if __name__ == "__main__":
    main()
