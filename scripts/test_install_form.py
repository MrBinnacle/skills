#!/usr/bin/env python3
"""Install-form contract for issue #333.

What this pins
    The published install path must name a marketplace source that works for a
    stranger with no SSH key. The GitHub shorthand `MrBinnacle/skills` resolved
    to SSH on a cold install of v3.0.1 and failed with
    `git@github.com: Permission denied (publickey)`. The HTTPS clone URL is a
    first-class `git` source in the Claude Code plugin CLI docs and was verified
    cold on 2026-10-02.

What is asserted, and why these shapes
    External behaviour only: what a reader copies out of README.md and
    site/index.html. The test does not import a resolver or re-implement source
    classification; a green run means the published bytes carry the form the
    CLI documents, not that a private predicate agrees with itself.

    Both reader surfaces are covered because both publish the install block.
    The README also must name the forms that were verified, so a later reader
    can tell tested from assumed.

Live cold install
    When `claude` is on PATH the suite runs the published shell form from a
    clean CLAUDE_CONFIG_DIR with SSH disabled. That run is the criterion-2
    evidence; its transcript is recorded in the pull request body. When
    `claude` is absent the suite FAILS rather than skips: a skip that prints a
    pass line is a check that never ran, which this repository already refuses
    elsewhere (test_link_skills_guard.py).

Run:  python scripts/test_install_form.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
SITE = ROOT / "site" / "index.html"

HTTPS_MARKETPLACE = "https://github.com/MrBinnacle/skills.git"
SHORTHAND = "MrBinnacle/skills"
PLUGIN_INSTALL = "/plugin install mrbinnacle-engineering"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def fence_blocks(text: str) -> list[str]:
    """Return the contents of fenced code blocks in a markdown document."""
    blocks: list[str] = []
    in_fence = False
    current: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            if in_fence:
                blocks.append("\n".join(current))
                current = []
            in_fence = not in_fence
            continue
        if in_fence:
            current.append(line)
    return blocks


def install_section(text: str) -> str:
    match = re.search(r"(?ms)^## Install\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    site = SITE.read_text(encoding="utf-8")

    # --- Criterion 1: published form works without SSH ---------------------
    check("README install section exists", install_section(readme) != "")
    check(
        "README install block names the HTTPS marketplace URL",
        HTTPS_MARKETPLACE in install_section(readme),
        f"expected {HTTPS_MARKETPLACE!r} in ## Install",
    )
    check(
        "site install block names the HTTPS marketplace URL",
        HTTPS_MARKETPLACE in site,
        f"expected {HTTPS_MARKETPLACE!r} in site/index.html",
    )
    check(
        "site install block does not publish the SSH-prone shorthand alone",
        f"marketplace add {SHORTHAND}" not in site,
        "site still publishes `marketplace add MrBinnacle/skills`",
    )

    # The interactive form and the shell form must both carry the HTTPS URL.
    check(
        "README shows the interactive form with the HTTPS URL",
        f"/plugin marketplace add {HTTPS_MARKETPLACE}" in install_section(readme),
        "interactive slash form missing or still shorthand",
    )
    check(
        "README shows the shell form with the HTTPS URL",
        f"claude plugin marketplace add {HTTPS_MARKETPLACE}" in install_section(readme),
        "shell form missing or still shorthand",
    )
    check(
        "site interactive form uses the HTTPS URL",
        f"/plugin marketplace add {HTTPS_MARKETPLACE}" in site,
        "site kbd block still shorthand",
    )
    check(
        "plugin install step is still published beside the marketplace add",
        PLUGIN_INSTALL in install_section(readme) and PLUGIN_INSTALL in site,
        "plugin install command missing from a reader surface",
    )

    # Fence content must carry the HTTPS URL (the block a reader copies).
    install_fences = [
        b for b in fence_blocks(install_section(readme)) if "marketplace add" in b
    ]
    check(
        "README marketplace fence copies the HTTPS URL",
        any(HTTPS_MARKETPLACE in b for b in install_fences),
        f"fences={install_fences!r}",
    )
    check(
        "no README install fence publishes only the shorthand",
        all(HTTPS_MARKETPLACE in b for b in install_fences) if install_fences else False,
        "a published fence still uses only MrBinnacle/skills",
    )

    # --- Criterion 3: README says which forms were verified -----------------
    section = install_section(readme)
    check(
        "README states which install forms were verified",
        re.search(r"(?i)verified", section) is not None,
        "## Install does not name a verification record",
    )
    check(
        "README names the interactive form among the verified surfaces",
        re.search(r"(?i)interactive", section) is not None,
        "## Install does not say the interactive form was verified",
    )
    check(
        "README names the shell form among the verified surfaces",
        re.search(r"(?i)shell", section) is not None,
        "## Install does not say the shell form was verified",
    )

    # --- Criterion 2: live cold install when the CLI is present ------------
    claude = shutil.which("claude")
    if claude is None:
        # Look beside a user-local install this container uses.
        candidate = Path.home() / ".local/claude-cli/node_modules/.bin/claude"
        claude = str(candidate) if candidate.is_file() else None
    if claude is None:
        check(
            "claude CLI available for the live cold-install check",
            False,
            "no claude on PATH; criterion 2 cannot be exercised here",
        )
    else:
        base = Path(tempfile.mkdtemp(prefix="install-form-333-"))
        config = base / "config"
        home = base / "home"
        config.mkdir()
        home.mkdir()
        env = os.environ.copy()
        env["CLAUDE_CONFIG_DIR"] = str(config)
        env["HOME"] = str(home)
        # No SSH key exists under this HOME, and GIT_SSH_COMMAND fails closed.
        env["GIT_SSH_COMMAND"] = (
            "ssh -o BatchMode=yes -o IdentityFile=/dev/null -o IdentitiesOnly=yes"
        )
        # Publish the HTTPS form only: never fall back to the shorthand.
        # The README's shell form is what a stranger runs.
        add = subprocess.run(
            [claude, "plugin", "marketplace", "add", HTTPS_MARKETPLACE],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(base),
        )
        out = add.stdout + add.stderr
        check(
            "cold marketplace add (HTTPS form) succeeds without SSH",
            add.returncode == 0 and "Successfully added marketplace" in out,
            f"rc={add.returncode}\n{out}",
        )
        installs = []
        for plugin in (
            "mrbinnacle-engineering",
            "mrbinnacle-orchestration",
            "mrbinnacle-meta",
        ):
            proc = subprocess.run(
                [claude, "plugin", "install", plugin],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(base),
            )
            installs.append((plugin, proc.returncode, proc.stdout + proc.stderr))
        check(
            "cold install of all three plugins succeeds",
            all(rc == 0 and "Successfully installed plugin" in out for _, rc, out in installs),
            "\n".join(f"{p}: rc={rc}\n{o}" for p, rc, o in installs),
        )
        listed = subprocess.run(
            [claude, "plugin", "list", "--json"],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(base),
        )
        check(
            "installed plugins report version 3.0.1 from the cold install",
            listed.returncode == 0 and '"version": "3.0.1"' in listed.stdout
            and listed.stdout.count('"version": "3.0.1"') >= 3,
            listed.stdout[:2000],
        )
        # Cards sit at the plugin root, not under skills/. Count SKILL.md files.
        try:
            data = json.loads(listed.stdout)
        except json.JSONDecodeError:
            data = []
        skill_count = 0
        for plugin in data:
            root = Path(plugin["installPath"])
            skill_count += len(list(root.glob("*/SKILL.md")))
        check(
            "cold install carries all 14 cards across the three plugins",
            skill_count == 14,
            f"skill_count={skill_count}, plugins={[(p.get('id'), p.get('version')) for p in data]}",
        )
        print(f"cold-install transcript available under {base}")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED")
        return 1
    print("PASS: install form is the HTTPS URL on README and site, and the cold path is green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
