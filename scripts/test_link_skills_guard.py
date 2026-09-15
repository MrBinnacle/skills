#!/usr/bin/env python3
"""Cases for the destination guard in scripts/link-skills.ps1.

The guard refuses to write a link into a git working tree that does not ignore the link
path. It exists because that is not a hypothetical. Measured 2026-09-15: a config
repository held 15 links into this repo, ignored none of them, and therefore tracked this
repo's bytes in a second index. A routine `git checkout` there removed one link and its
tracked files left that index in a single operation.

A guard that has never refused is not a guard, so the refusing case is seeded and
asserted by the phrase the script prints. The allowed case is asserted too, because a
guard that refuses everything is equally useless.

Both cases drive the real script through `pwsh`. If `pwsh` is absent this suite FAILS
rather than skipping: a skip that prints a pass line is the vacuous check this repo
already refuses elsewhere.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "link-skills.ps1"

FAILURES = []


def check(label, ok, detail=None):
    print(("ok   " if ok else "FAIL ") + label)
    if not ok:
        FAILURES.append(label)
        if detail:
            print("       " + str(detail)[:600])


def git(cwd, *args):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True, text=True,
    )


def make_tracked_dest(root: Path, gitignore: str | None) -> Path:
    """A git working tree with a skills/ directory, optionally ignoring its contents."""
    tree = root / "consumer"
    (tree / "skills").mkdir(parents=True)
    git(tree, "init", "-q")
    if gitignore is not None:
        (tree / ".gitignore").write_text(gitignore, encoding="utf-8")
    (tree / "README.md").write_text("consumer\n", encoding="utf-8")
    git(tree, "add", "-A")
    git(tree, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
    return tree / "skills"


def run_script(dest: Path):
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if not pwsh:
        return None
    env = dict(os.environ, HOME=str(dest.parent.parent))
    return subprocess.run(
        [pwsh, "-NoProfile", "-File", str(SCRIPT), "-Dest", str(dest)],
        capture_output=True, text=True, env=env, cwd=str(REPO),
    )


if not (shutil.which("pwsh") or shutil.which("powershell")):
    print("FAIL no pwsh or powershell on PATH; this suite cannot verify the guard")
    print("     A skip here would print a pass line for a check that never ran.")
    sys.exit(1)

if not SCRIPT.is_file():
    print(f"FAIL {SCRIPT} does not exist")
    sys.exit(1)


# --- NEGATIVE: a tracked destination with no ignore rule must be refused -------------
with tempfile.TemporaryDirectory() as tmp:
    dest = make_tracked_dest(Path(tmp), gitignore=None)
    proc = run_script(dest)
    if proc is None:
        check("NEGATIVE: an unignored tracked destination is refused", False, "no pwsh")
    else:
        out = proc.stdout + proc.stderr
        check("NEGATIVE: an unignored tracked destination is refused",
              proc.returncode != 0, f"rc={proc.returncode}\n{out}")
        check("the refusal names the git working tree",
              "REFUSED" in out and "git working tree" in out, out)
        check("the refusal explains why a link is the defect",
              "ordinary files" in out, out)
        check("the refusal names the install remedy",
              "claude plugin marketplace add" in out, out)
        check("the refusal happens in DRY RUN, before any change",
              not any(dest.iterdir()), sorted(p.name for p in dest.iterdir()))


# --- POSITIVE: a tracked destination that ignores the paths is allowed ---------------
with tempfile.TemporaryDirectory() as tmp:
    dest = make_tracked_dest(Path(tmp), gitignore="skills/\n")
    proc = run_script(dest)
    if proc is None:
        check("POSITIVE: an ignored tracked destination is allowed", False, "no pwsh")
    else:
        out = proc.stdout + proc.stderr
        check("POSITIVE: an ignored tracked destination is allowed",
              proc.returncode == 0 and "REFUSED" not in out,
              f"rc={proc.returncode}\n{out}")
        check("the allowed run is still a dry run by default",
              "DRY RUN" in out, out)


# --- POSITIVE: a destination outside any git tree is allowed -------------------------
with tempfile.TemporaryDirectory() as tmp:
    dest = Path(tmp) / "plain" / "skills"
    dest.mkdir(parents=True)
    proc = run_script(dest)
    if proc is None:
        check("POSITIVE: a destination in no git tree is allowed", False, "no pwsh")
    else:
        out = proc.stdout + proc.stderr
        check("POSITIVE: a destination in no git tree is allowed",
              proc.returncode == 0 and "REFUSED" not in out,
              f"rc={proc.returncode}\n{out}")


print()
if FAILURES:
    print("%d FAILED" % len(FAILURES))
    sys.exit(1)
print("PASS: the link destination guard refuses an unignored tracked tree and allows the rest")
