#!/usr/bin/env python3
"""Suite for check_message_residue.py: a commit message carrying a residue term is refused.

Poison text is assembled at run time, so this file carries no term itself.

    Cases:
      - every `residue-` hook in the yaml is applied, and no `leak-` hook is;
      - a message file with a codename in its subject or body is refused, naming
        the line, the hook and the hook's replacement text;
      - `--commit-msg` skips git's `# ` help lines and still reads a subject that
        opens `#327:`; a plain file (a PR body) keeps its `# ` heading lines;
      - a clean message passes;
      - in a temp repository, `--range` refuses the one poisoned commit of three.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import check_message_residue as cmr  # noqa: E402

SCRIPT = SCRIPT_DIR / "check_message_residue.py"
RESEARCH_DIR = "skills" + "_" + "research"
CODENAME = "W" + "rit"
FAILURES: list[str] = []


def check(case: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  ok   {case}")
    else:
        FAILURES.append(case)
        print(f"  FAIL {case}: {detail}")


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8", cwd=cwd
    )


def case_hook_selection() -> None:
    yaml_ids = set(cmr.parse_hooks())
    residue = {h for h in yaml_ids if h.startswith("residue-")}
    check("the yaml has residue hooks to apply", len(residue) >= 7, str(sorted(yaml_ids)))
    check("the yaml has leak hooks the check leaves out", any(h.startswith("leak-") for h in yaml_ids))


def case_message_files(tmp: Path) -> None:
    poisoned = tmp / "poisoned.txt"
    poisoned.write_text(f"#327: tidy the gate\n\nCarries {RESEARCH_DIR}#62 and {CODENAME} notes.\n", encoding="utf-8")
    result = run(str(poisoned))
    check("a poisoned message file exits 1", result.returncode == 1, result.stdout)
    check(
        "the refusal names the line, the hook and the replacement",
        f"poisoned.txt:3: residue-research-dir matched '{RESEARCH_DIR}'" in result.stdout
        and "-> a generic descriptor" in result.stdout
        and "residue-writ" in result.stdout,
        result.stdout,
    )

    hashed = tmp / "hashed.txt"
    hashed.write_text(f"#327: see {RESEARCH_DIR}\n# Please enter the commit message; {CODENAME} here is git help\n",
                      encoding="utf-8")
    result = run("--commit-msg", str(hashed))
    check(
        "--commit-msg reads a '#327:' subject and skips a '# ' help line",
        result.returncode == 1 and "hashed.txt:1:" in result.stdout and "residue-writ" not in result.stdout,
        result.stdout,
    )
    result = run(str(hashed))
    check("a plain file (a PR body) keeps its '# ' heading lines", "hashed.txt:2: residue-writ" in result.stdout,
          result.stdout)

    clean = tmp / "clean.txt"
    clean.write_text("docs(agents): name the private research directory generically\n", encoding="utf-8")
    result = run(str(clean))
    check("a clean message passes", result.returncode == 0 and result.stdout.startswith("PASS:"), result.stdout)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, encoding="utf-8"
    ).stdout.strip()


def case_range(tmp: Path) -> None:
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "suite@example.invalid")
    git(repo, "config", "user.name", "suite")
    for message in ("chore: base", f"docs: note from {RESEARCH_DIR}", "docs: clean follow-up"):
        git(repo, "commit", "-q", "--allow-empty", "-m", message)
    poisoned = git(repo, "rev-parse", "--short", "HEAD~1")
    result = run("--range", "HEAD~2..HEAD", cwd=repo)
    check(
        "--range refuses the poisoned commit and only it",
        result.returncode == 1 and f"{poisoned}:1: residue-research-dir" in result.stdout
        and "in 2 message(s)" in result.stdout and result.stdout.count("residue-") == 1,
        result.stdout + result.stderr,
    )


def main() -> None:
    case_hook_selection()
    with tempfile.TemporaryDirectory() as tmp:
        case_message_files(Path(tmp))
        case_range(Path(tmp))
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print("PASS: message residue check refuses a codename in a message file and in a commit range")


if __name__ == "__main__":
    main()
