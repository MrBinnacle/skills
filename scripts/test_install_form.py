"""Install-form contract for issue #333.

What this pins
    The published install path must name a marketplace source that works for a
    stranger with no SSH key. The GitHub shorthand `MrBinnacle/skills` resolved
    to SSH on a cold install of v3.0.1 and failed with
    `git@github.com: Permission denied (publickey)`. The HTTPS clone URL is a
    first-class `git` source in the Claude Code plugin CLI docs and was verified
    cold on 2026-10-02. Every reader-facing install site publishes that same
    HTTPS form.

What is asserted, and why these shapes
    External behaviour only: what a reader copies out of README.md,
    site/index.html, CATALOG.md, AGENTS.md and scripts/link-skills.ps1. The
    test does not import a resolver or re-implement source classification; a
    green run means the published bytes carry the form the CLI documents, not
    that a private predicate agrees with itself.

    Plugin names published in install lines are checked against
    `.claude-plugin/marketplace.json`, so a README that names a plugin the
    marketplace does not declare fails even when the CLI is absent. The
    "Verified forms" record is checked against the cold install's own
    `claude plugin list --json` output and against `claude --version`, so a
    README that states a stale version fails the same run that would have
    installed the real one.

    A tracked-file scan refuses any install surface, outside
    `docs/design/variants/**` and `.changeset/**`, that still publishes the
    SSH-prone shorthand. The changeset is exempt because its wording is a
    release decision held elsewhere; the design variants are historical
    previews, not install instructions.

Live cold install
    Two cases run when `claude` is on PATH. Both use a clean
    CLAUDE_CONFIG_DIR, an empty scratch HOME, the matching empty USERPROFILE
    (Windows OpenSSH and git read USERPROFILE, not HOME) and a fail-closed
    GIT_SSH_COMMAND.

    1. Published URL: the README's own `claude plugin marketplace add` and
       `claude plugin install` lines are executed exactly as written — argv[0]
       is replaced with the CLI path, nothing else. Remaining declared plugins
       are installed afterwards so the "all three" claim in the Verified forms
       record is exercised.
    2. Checked-out tree: `claude plugin marketplace add <path of this
       worktree>` in a separate clean config, then all three declared plugins
       installed from that tree. This is the case that would see a break this
       branch makes in `.claude-plugin/marketplace.json`.

    When `claude` is absent the suite FAILS rather than skips: a skip that
    prints a pass line is a check that never ran, which this repository
    already refuses elsewhere (test_link_skills_guard.py).

Run:  python scripts/test_install_form.py
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
SITE = ROOT / "site" / "index.html"
CATALOG = ROOT / "CATALOG.md"
AGENTS = ROOT / "AGENTS.md"
LINK_PS1 = ROOT / "scripts" / "link-skills.ps1"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

HTTPS_MARKETPLACE = "https://github.com/MrBinnacle/skills.git"
SHORTHAND = "MrBinnacle/skills"
# Built, never written as one literal: the tracked-file scan below would
# otherwise flag this test file for publishing the form it refuses.
SHORTHAND_ADD = f"marketplace add {SHORTHAND}"

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


def declared_plugins() -> set[str]:
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return {entry["name"] for entry in data.get("plugins", [])}


def branch_plugin_versions() -> dict[str, str]:
    """Version each plugin's own plugin.json declares on this branch."""
    versions: dict[str, str] = {}
    skills_root = ROOT / "skills"
    if not skills_root.is_dir():
        return versions
    for plugin_dir in sorted(skills_root.iterdir()):
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        name = data.get("name")
        version = data.get("version")
        if name and version:
            versions[name] = version
    return versions


def readme_shell_install_names(section: str) -> list[str]:
    """Every `claude plugin install <name>` line from README shell fences."""
    names: list[str] = []
    for fence in fence_blocks(section):
        for raw in fence.splitlines():
            line = raw.strip()
            if not line.startswith("claude plugin install"):
                continue
            try:
                parts = shlex.split(line)
            except ValueError:
                continue
            if len(parts) >= 4 and parts[1:3] == ["plugin", "install"]:
                names.append(parts[3])
    return names


def slash_install_names(text: str) -> list[str]:
    """Every `/plugin install <name>` line in README text or site text blocks."""
    names: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        name = name.strip().rstrip(".`'\"")
        if name and name not in seen:
            seen.add(name)
            names.append(name)

    for kbd in re.findall(r"<kbd>([^<]+)</kbd>", text):
        match = re.search(r"/plugin install\s+(\S+)", kbd)
        if match:
            add(match.group(1))
    for match in re.finditer(r"(?m)^/plugin install\s+(\S+)", text):
        add(match.group(1))
    for match in re.finditer(r"`/plugin install\s+([^`]+)`", text):
        add(match.group(1))
    return names


def parse_verified_forms(section: str) -> tuple[str | None, str | None]:
    """Return (claude_code_version, plugin_version) from the Verified forms record."""
    record = section.partition("Verified forms")[2]
    claude_match = re.search(r"Claude Code\s+(\S+)", record)
    plugin_match = re.search(r"\bat\s+(\S+)", record)
    claude_version = (
        claude_match.group(1).rstrip(",.;") if claude_match else None
    )
    plugin_version = plugin_match.group(1).rstrip(",.;") if plugin_match else None
    return claude_version, plugin_version


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        check=True,
        cwd=str(ROOT),
    )
    return [path for path in result.stdout.decode("utf-8").split("\0") if path]


def scan_exempt(path: str) -> bool:
    return path.startswith("docs/design/variants/") or path.startswith(".changeset/")


def cold_env(base: Path) -> dict[str, str]:
    """Clean install environment: empty scratch home, no working SSH key."""
    config = base / "config"
    home = base / "home"
    config.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CLAUDE_CONFIG_DIR"] = str(config)
    env["HOME"] = str(home)
    # Windows OpenSSH and git read USERPROFILE, not HOME.
    env["USERPROFILE"] = str(home)
    env["GIT_SSH_COMMAND"] = (
        "ssh -o BatchMode=yes -o IdentityFile=/dev/null -o IdentitiesOnly=yes"
    )
    return env


def run_cli(
    claude: str, args: list[str], env: dict[str, str], cwd: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [claude, *args],
        capture_output=True,
        check=False,
        text=True,
        env=env,
        cwd=cwd,
    )


def parse_plugin_list(stdout: str) -> dict[str, dict]:
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, list):
        return {}
    plugins: dict[str, dict] = {}
    for plugin in data:
        if not isinstance(plugin, dict):
            continue
        plugin_id = plugin.get("id", "")
        short = plugin_id.partition("@")[0]
        if short:
            plugins[short] = plugin
    return plugins


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    site = SITE.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    agents = AGENTS.read_text(encoding="utf-8")
    link_ps1 = LINK_PS1.read_text(encoding="utf-8")
    section = install_section(readme)
    site_commands = re.findall(r"<kbd>([^<]+)</kbd>", site)
    verification_record = section.partition("Verified forms")[2]
    declared = declared_plugins()

    # --- Criterion 1: published form works without SSH ---------------------
    check("README install section exists", section != "")
    check(
        "README install block names the HTTPS marketplace URL",
        HTTPS_MARKETPLACE in section,
        f"expected {HTTPS_MARKETPLACE!r} in ## Install",
    )
    check(
        "site install block names the HTTPS marketplace URL",
        HTTPS_MARKETPLACE in site,
        f"expected {HTTPS_MARKETPLACE!r} in site/index.html",
    )
    check(
        "site install block does not publish the SSH-prone shorthand alone",
        SHORTHAND_ADD not in site,
        f"site still publishes `{SHORTHAND_ADD}`",
    )

    # The interactive form and the shell form must both carry the HTTPS URL.
    check(
        "README shows the interactive form with the HTTPS URL",
        f"/plugin marketplace add {HTTPS_MARKETPLACE}" in section,
        "interactive slash form missing or still shorthand",
    )
    check(
        "README shows the shell form with the HTTPS URL",
        f"claude plugin marketplace add {HTTPS_MARKETPLACE}" in section,
        "shell form missing or still shorthand",
    )
    check(
        "site interactive form uses the HTTPS URL",
        f"/plugin marketplace add {HTTPS_MARKETPLACE}" in site_commands,
        "site kbd block still shorthand or absent",
    )
    check(
        "plugin install step is still published beside the marketplace add",
        "/plugin install mrbinnacle-engineering" in section
        and "/plugin install mrbinnacle-engineering" in site_commands,
        "plugin install command missing from a reader surface",
    )

    # Fence content must carry the HTTPS URL (the block a reader copies).
    install_fences = [b for b in fence_blocks(section) if "marketplace add" in b]
    check(
        "README marketplace fence copies the HTTPS URL",
        any(HTTPS_MARKETPLACE in b for b in install_fences),
        f"fences={install_fences!r}",
    )
    check(
        "no README install fence publishes only the shorthand",
        all(HTTPS_MARKETPLACE in b for b in install_fences)
        if install_fences
        else False,
        "a published fence still uses only the GitHub shorthand",
    )

    # --- Requirement 4: every reader-facing site gives the same form --------
    check(
        "CATALOG install block names the HTTPS marketplace URL",
        f"marketplace add {HTTPS_MARKETPLACE}" in catalog,
        f"expected the HTTPS URL in CATALOG.md",
    )
    check(
        "AGENTS.md install line names the HTTPS marketplace URL",
        f"marketplace add {HTTPS_MARKETPLACE}" in agents,
        "expected the HTTPS URL in AGENTS.md",
    )
    check(
        "link-skills.ps1 refusal message names the HTTPS marketplace URL",
        f"marketplace add {HTTPS_MARKETPLACE}" in link_ps1,
        "expected the HTTPS URL in scripts/link-skills.ps1",
    )

    # Tracked-file scan: no install surface outside the exemptions may carry
    # the SSH-prone shorthand form.
    violations: list[str] = []
    for path in tracked_files():
        if scan_exempt(path):
            continue
        file_path = ROOT / path
        if not file_path.is_file():
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if SHORTHAND_ADD in text:
            violations.append(path)
    check(
        "no tracked install surface publishes the SSH-prone marketplace shorthand",
        not violations,
        f"files still carrying the shorthand form: {violations}",
    )

    # --- Requirement 2: published plugin names are declared -----------------
    shell_install_names = readme_shell_install_names(section)
    slash_names = slash_install_names(readme) + slash_install_names(site)
    check(
        "README shell fence provides runnable marketplace and plugin commands",
        any(
            "marketplace add" in fence and "plugin install" in fence
            for fence in install_fences
        )
        or (
            "claude plugin marketplace add" in section
            and shell_install_names
        ),
        "shell fence must contain both `claude plugin marketplace add` and `claude plugin install`",
    )
    check(
        "README shell install names are declared in marketplace.json",
        bool(shell_install_names)
        and all(name in declared for name in shell_install_names),
        f"names={shell_install_names}, declared={sorted(declared)}",
    )
    check(
        "README and site slash install names are declared in marketplace.json",
        bool(slash_names) and all(name in declared for name in slash_names),
        f"names={slash_names}, declared={sorted(declared)}",
    )

    # --- Requirement 5: README prose about the incident ---------------------
    check(
        "README cold-install transcript cites pull request #340",
        "pull request that changed this section (#340)" in readme,
        "transcript sentence must cite #340 (the pull request), not #333 (the issue)",
    )
    check(
        "README omits the private-path disclaimer",
        "private research checkout" not in readme,
        "delete the private-path sentence from README",
    )
    check(
        "README records issue #333 in the past tense",
        "Issue #333 recorded that failure" in readme
        and "Issue #333 tracks that failure" not in readme,
        'README must say "Issue #333 recorded that failure." — #333 closes on merge',
    )

    # --- Criterion 3: README says which forms were verified -----------------
    check(
        "README states which install forms were verified",
        verification_record != "",
        "## Install does not name a verification record",
    )
    check(
        "README names the interactive form among the verified surfaces",
        f"interactive `/plugin marketplace add {HTTPS_MARKETPLACE}`"
        in verification_record,
        "## Install does not say the interactive form was verified",
    )
    check(
        "README names the shell form among the verified surfaces",
        f"shell `claude plugin marketplace add {HTTPS_MARKETPLACE}`"
        in verification_record,
        "## Install does not say the shell form was verified",
    )
    readme_claude_version, readme_plugin_version = parse_verified_forms(section)
    check(
        "README Verified forms record states a Claude Code version",
        bool(readme_claude_version),
        "## Install does not state which Claude Code version was verified",
    )
    check(
        "README Verified forms record states a plugin version",
        bool(readme_plugin_version),
        "## Install does not state which plugin version was verified",
    )

    # --- Criterion 2 and requirement 6: live cold installs ------------------
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
        add_command = next(
            (
                shlex.split(line)
                for fence in install_fences
                for line in fence.splitlines()
                if line.strip().startswith("claude plugin marketplace add")
            ),
            None,
        )
        check(
            "README shell fence provides a runnable marketplace add command",
            add_command is not None,
            "shell fence must contain `claude plugin marketplace add`",
        )
        if add_command is None:
            print()
            print(f"{len(FAILURES)} FAILED")
            return 1

        # Case 1: published URL, README lines exactly as written.
        base = Path(tempfile.mkdtemp(prefix="install-form-333-"))
        env = cold_env(base)
        add_command[0] = claude
        add = run_cli(claude, add_command[1:], env, str(base))
        out = add.stdout + add.stderr
        check(
            "cold marketplace add (HTTPS form) succeeds without SSH",
            add.returncode == 0 and "Successfully added marketplace" in out,
            f"rc={add.returncode}\n{out}",
        )
        installs: list[tuple[str, int, str]] = []
        # Run every README install line exactly as written (argv[0] only).
        for name in shell_install_names:
            proc = run_cli(claude, ["plugin", "install", name], env, str(base))
            installs.append((name, proc.returncode, proc.stdout + proc.stderr))
        # The Verified forms record claims all three plugins; install any
        # declared plugin the README shell fence did not already name.
        for name in sorted(declared - set(shell_install_names)):
            proc = run_cli(claude, ["plugin", "install", name], env, str(base))
            installs.append((name, proc.returncode, proc.stdout + proc.stderr))
        check(
            "cold install of all three plugins succeeds",
            all(
                rc == 0 and "Successfully installed plugin" in plugin_out
                for _, rc, plugin_out in installs
            ),
            "\n".join(f"{p}: rc={rc}\n{o}" for p, rc, o in installs),
        )
        listed = run_cli(claude, ["plugin", "list", "--json"], env, str(base))
        installed = parse_plugin_list(listed.stdout)
        check(
            "installed plugins report one nonempty version from the cold install",
            listed.returncode == 0
            and set(installed) == declared
            and len({plugin.get("version") for plugin in installed.values()}) == 1
            and all(plugin.get("version") for plugin in installed.values()),
            listed.stdout[:2000],
        )
        # Cards sit at the plugin root, not under skills/. Count SKILL.md files.
        skill_count = 0
        for plugin in installed.values():
            root = Path(plugin["installPath"])
            skill_count += len(list(root.glob("*/SKILL.md")))
        check(
            "cold install carries cards in every requested plugin",
            skill_count >= len(declared),
            f"skill_count={skill_count}, plugins={[(p.get('id'), p.get('version')) for p in installed.values()]}",
        )

        # Requirement 3: the Verified forms record must match this cold install.
        version_out = run_cli(claude, ["--version"], env, str(base))
        cli_version = (version_out.stdout or version_out.stderr).strip().split()[0]
        check(
            "README Verified forms Claude Code version matches the installed CLI",
            bool(readme_claude_version)
            and readme_claude_version == cli_version,
            f"README says {readme_claude_version!r}, CLI reports {cli_version!r}",
        )
        installed_versions = {
            plugin.get("version") for plugin in installed.values()
        }
        check(
            "README Verified forms plugin version matches the cold install",
            bool(readme_plugin_version)
            and installed_versions == {readme_plugin_version},
            f"README says {readme_plugin_version!r}, cold install reports {installed_versions!r}",
        )
        print(f"cold-install transcript available under {base}")

        # Requirement 6: the tree under test, not only the published default branch.
        local_base = Path(tempfile.mkdtemp(prefix="install-form-local-333-"))
        local_env = cold_env(local_base)
        local_add = run_cli(
            claude,
            ["plugin", "marketplace", "add", str(ROOT)],
            local_env,
            str(local_base),
        )
        local_out = local_add.stdout + local_add.stderr
        check(
            "cold install from the checked-out tree succeeds",
            local_add.returncode == 0 and "Successfully added marketplace" in local_out,
            f"rc={local_add.returncode}\n{local_out}",
        )
        local_installs: list[tuple[str, int, str]] = []
        for name in sorted(declared):
            proc = run_cli(
                claude, ["plugin", "install", name], local_env, str(local_base)
            )
            local_installs.append((name, proc.returncode, proc.stdout + proc.stderr))
        check(
            "checked-out tree cold install carries every declared plugin",
            all(
                rc == 0 and "Successfully installed plugin" in plugin_out
                for _, rc, plugin_out in local_installs
            ),
            "\n".join(f"{p}: rc={rc}\n{o}" for p, rc, o in local_installs),
        )
        local_listed = run_cli(
            claude, ["plugin", "list", "--json"], local_env, str(local_base)
        )
        local_installed = parse_plugin_list(local_listed.stdout)
        branch_versions = branch_plugin_versions()
        local_versions = {
            name: plugin.get("version") for name, plugin in local_installed.items()
        }
        check(
            "checked-out tree cold install reports the branch plugin versions",
            local_listed.returncode == 0
            and set(local_installed) == declared
            and local_versions == branch_versions,
            f"installed={local_versions}, branch={branch_versions}",
        )
        local_skill_count = 0
        for plugin in local_installed.values():
            root = Path(plugin["installPath"])
            local_skill_count += len(list(root.glob("*/SKILL.md")))
        check(
            "checked-out tree cold install carries cards in every plugin",
            local_skill_count >= len(declared),
            f"skill_count={local_skill_count}",
        )
        print(f"checked-out-tree transcript available under {local_base}")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED")
        return 1
    print(
        "PASS: install form is the HTTPS URL on every reader surface, "
        "published and checked-out-tree cold installs are green, and the "
        "Verified forms record matches the CLI"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
