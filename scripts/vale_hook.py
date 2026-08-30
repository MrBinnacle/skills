#!/usr/bin/env python3
"""Run Vale at ERROR level for the pre-commit and commit-msg hooks.

WHY ERROR LEVEL AND NOT WARNING

    Every Taste row currently ships at `warning`. Vale exits non-zero only on an
    ERROR-level alert, so this hook is deliberately a no-op today: it installs the
    carrier now and starts refusing the moment the rows are promoted. Promotion is
    tracked upstream (the Taste-promotion ticket in the research repository) and is
    a decision about who the rules bind, not a config tweak.

    A hook that blocked on warnings would make the promotion decision by accident,
    which is the thing the two levels exist to keep apart.

WHY A MISSING BINARY SKIPS RATHER THAN FAILS

    Vale is not a Python dependency and a contributor may not have it. The sibling
    instrument learned this the expensive way: resolving the binary at import time
    made its ENTIRE test suite uncollectable for anyone without Vale installed, not
    merely the module that needed it. A missing binary here prints how to install it
    and exits 0. CI installs Vale explicitly, so the gate there is unaffected.

Usage:
    python scripts/vale_hook.py FILE [FILE ...]        # lint files
    python scripts/vale_hook.py --commit-msg FILE      # lint a commit message
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_HINT = (
    "Vale is not installed, so the prose hook was skipped.\n"
    "  Install: https://vale.sh/docs/vale-cli/installation/\n"
    "  Pinned version for this repository: see styles/Taste/STYLE_SOURCE.json"
)


def main(argv: list[str]) -> int:
    commit_msg = False
    if argv and argv[0] == "--commit-msg":
        commit_msg = True
        argv = argv[1:]

    paths = [p for p in argv if Path(p).is_file()]
    if not paths:
        return 0

    binary = shutil.which("vale")
    if binary is None:
        print(INSTALL_HINT, file=sys.stderr)
        return 0

    command = [binary, "--config", str(REPO_ROOT / ".vale.ini"), "--minAlertLevel", "error"]

    if commit_msg:
        # A commit message file has no extension. Vale cannot infer a format from
        # the path, and `--ext=.md` does NOT rescue a positional path - measured on
        # 3.9.1, that combination reports "0 files" and exits 0, which is a hook
        # that can never fire. Piping the text with `--ext=.md` is the form that
        # reads it. Stdin also draws the `[*.md]` section only, so a commit message
        # is checked against the Taste rows and not the marketing list, which
        # assets/tokens.json scopes to public asset copy.
        text = Path(paths[0]).read_text(encoding="utf-8", errors="replace")
        result = subprocess.run(
            [*command, "--ext=.md"], cwd=REPO_ROOT, input=text, text=True
        )
    else:
        result = subprocess.run([*command, *paths], cwd=REPO_ROOT)
    if result.returncode != 0:
        target = "commit message" if commit_msg else "staged prose"
        print(
            f"\nThe {target} breaks an error-level Taste row, named above with its "
            f"line.\nFix the line, or state why the row does not apply in the pull "
            f"request.",
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
