#!/usr/bin/env python3
"""Run one recipe step in the declared target-user environment, or refuse it.

The replaying agent is given this script as its only shell tool. Each call is
one recipe step. The script enforces the replay's boundaries in code, not in
the prompt, so a recipe that tries to steer the agent still cannot widen them:

- Secret boundary: every environment variable whose name looks like a
  credential is dropped before the step runs. The step prints how many such
  names it still sees (it must be 0) so the receipt shows the boundary held.
- Target-user boundary: an empty scratch HOME and USERPROFILE, an empty
  global git config, no system git config, an SSH command that offers no
  identity, and a fresh CLAUDE_CONFIG_DIR. This mirrors cold_env() in
  scripts/test_install_form.py.
- Program allowlist: only the commands an install recipe of this collection
  needs. Anything else is refused with exit code 3.
- Irreversible-action gate: shapes that delete, push, publish or pipe a
  download into a shell are refused with exit code 4, before the allowlist.

Network is NOT firewalled. It is bounded only by the program allowlist. The
receipt says so.

Usage: python -I run_step.py <scratch-dir> "<command line>"
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|AUTH|SOCKET", re.I)

ALLOWED_PREFIXES = (
    ("claude", "plugin", "marketplace", "add"),
    ("claude", "plugin", "install"),
    ("claude", "plugin", "list"),
    ("claude", "--version"),
    ("git", "ls-remote"),
    ("git", "--version"),
)

IRREVERSIBLE = re.compile(
    r"\brm\b|\brmdir\b|\bdel\b|\bformat\b|\bmkfs\b|\bdd\b|git\s+push|"
    r"npm\s+publish|\bdeploy\b|\bshutdown\b|\|\s*(ba|z)?sh\b|curl|wget|"
    r"Remove-Item|>\s*/|chmod|chown",
    re.I,
)


def target_env(scratch: Path) -> dict[str, str]:
    home = scratch / "home"
    config = scratch / "config"
    home.mkdir(parents=True, exist_ok=True)
    config.mkdir(parents=True, exist_ok=True)
    git_config = home / ".gitconfig-empty"
    git_config.write_text("", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not SECRET_NAME.search(k)}
    env.update(
        CLAUDE_CONFIG_DIR=str(config),
        HOME=str(home),
        USERPROFILE=str(home),
        GIT_CONFIG_GLOBAL=str(git_config),
        GIT_CONFIG_NOSYSTEM="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_SSH_COMMAND="ssh -o BatchMode=yes -o IdentityFile=/dev/null -o IdentitiesOnly=yes",
    )
    return env


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: run_step.py <scratch-dir> <command line>")
        return 2
    sys.stdout.reconfigure(encoding="ascii", errors="replace")
    scratch, line = Path(argv[1]), argv[2]
    print(f"STEP: {line}")
    if IRREVERSIBLE.search(line):
        print("REFUSED (irreversible-action gate): step not run")
        return 4
    tokens = shlex.split(line)
    if not any(tuple(tokens[: len(p)]) == p for p in ALLOWED_PREFIXES):
        print("REFUSED (program allowlist): step not run")
        return 3
    env = target_env(scratch)
    leaked = sorted(k for k in env if SECRET_NAME.search(k))
    print(f"SECRET-NAMED VARS IN STEP ENV: {len(leaked)}")
    exe = "claude.exe" if tokens[0] == "claude" and os.name == "nt" else tokens[0]
    try:
        done = subprocess.run(
            [exe, *tokens[1:]], env=env, cwd=scratch, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"STEP ERROR: {exc}")
        return 5
    print(done.stdout.rstrip())
    print(done.stderr.rstrip())
    print(f"EXIT: {done.returncode}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
