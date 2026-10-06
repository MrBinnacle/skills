"""Install-form contract for issue #333, extended by issue #408.

What this pins
    The published install path must name a marketplace source that works for a
    stranger with no SSH key. The GitHub shorthand `MrBinnacle/skills` resolved
    to SSH on a cold install of v3.0.1 and failed with
    `git@github.com: Permission denied (publickey)`. The HTTPS clone URL is a
    first-class `git` source in the Claude Code plugin CLI docs and was verified
    cold on 2026-10-02. Every reader-facing install site publishes that same
    HTTPS form.

    Issue #408 adds three further contracts on the same surfaces:
    1. No copyable unit in the README Install section or on the landing page
       holds more than one `/plugin` command. A pasted multi-line block of
       slash commands is read as one command by Claude Code, so the second
       line becomes part of the URL and fails on a reader's first action.
    2. The README states when the cards appear after install (`/reload-plugins`,
       `/reload-plugins --force` for a pending reload, or the next start) and
       cites the vendor page with the date it was read.
    3. The README names `claude plugin list` so a reader can confirm what was
       installed from the tool rather than from prose.

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
    (Windows OpenSSH and git read USERPROFILE, not HOME), an empty
    GIT_CONFIG_GLOBAL with GIT_CONFIG_NOSYSTEM=1 (so no system or user git
    config, such as a credential helper, reaches the clone) and a fail-closed
    GIT_SSH_COMMAND. Each isolation clause has its own named check.

    1. Published URL: the README's own `claude plugin marketplace add` and
       `claude plugin install` lines are executed exactly as written, every
       token included. argv[0] is replaced with the CLI path, nothing else.
       Remaining declared plugins are installed afterwards so the "all three"
       claim in the Verified forms record is exercised.
    2. Checked-out tree: `claude plugin marketplace add <path of this
       worktree>` in a separate clean config, then all three declared plugins
       installed from that tree. This is the case that would see a break this
       branch makes in `.claude-plugin/marketplace.json`.

    Both cases live under one temporary root that is removed when the suite
    exits, whether it passes, fails or raises; a named check compares the
    temp-folder listing before and after.

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
import stat
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

# Issue #408: Claude Code's plugin docs state that a plugin loads on
# `/reload-plugins` or the next start, and that a reload left pending stays
# pending until `/reload-plugins --force`. The README must tell the reader
# this, with the vendor page and the date the page was read.
PLUGIN_DOCS_URL = "https://code.claude.com/docs/en/discover-plugins.md"
PLUGIN_DOCS_READ = "2026-10-06"

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


def slash_commands_in(block: str) -> list[str]:
    """Every `/plugin ...` command line inside one copyable unit.

    Issue #408: Claude Code reads a multi-line paste of slash commands as one
    command and takes the second line as part of the URL, so a copyable block
    that holds two of them fails on a reader's first action.
    """
    return [
        line.strip()
        for line in block.splitlines()
        if line.strip().startswith("/plugin")
    ]


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


def readme_shell_install_commands(section: str) -> list[list[str]]:
    """Every `claude plugin install ...` line from README shell fences, as argv.

    The whole line is kept, every token included, so the live cold install
    can run it exactly as a reader would copy it.
    """
    commands: list[list[str]] = []
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
                commands.append(parts)
    return commands


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
    """Clean install environment: empty scratch home, no working SSH key,
    no global or system git configuration."""
    config = base / "config"
    home = base / "home"
    config.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    git_config = home / ".gitconfig-empty"
    git_config.write_text("", encoding="utf-8")
    env = os.environ.copy()
    env["CLAUDE_CONFIG_DIR"] = str(config)
    env["HOME"] = str(home)
    # Windows OpenSSH and git read USERPROFILE, not HOME.
    env["USERPROFILE"] = str(home)
    # A system git config (for example a Windows credential.helper=manager)
    # would otherwise still apply to the published-URL clone.
    env["GIT_CONFIG_GLOBAL"] = str(git_config)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_SSH_COMMAND"] = (
        "ssh -o BatchMode=yes -o IdentityFile=/dev/null -o IdentitiesOnly=yes"
    )
    return env


def check_cold_env(base: Path) -> None:
    """Observe each isolation clause of cold_env directly."""
    env = cold_env(base / "probe")
    home = env.get("HOME", "")
    check(
        "cold_env sets USERPROFILE to the scratch HOME",
        bool(home)
        and env.get("USERPROFILE") == home
        and Path(home).resolve().is_relative_to(base.resolve()),
        f"HOME={home!r}, USERPROFILE={env.get('USERPROFILE')!r}, base={str(base)!r}",
    )
    global_config = env.get("GIT_CONFIG_GLOBAL", "")
    check(
        "cold_env points GIT_CONFIG_GLOBAL at an empty file in the scratch home",
        bool(global_config)
        and Path(global_config).resolve().is_relative_to(base.resolve())
        and Path(global_config).is_file()
        and Path(global_config).stat().st_size == 0,
        f"GIT_CONFIG_GLOBAL={global_config!r}, base={str(base)!r}",
    )
    check(
        "cold_env sets GIT_CONFIG_NOSYSTEM=1",
        env.get("GIT_CONFIG_NOSYSTEM") == "1",
        f"GIT_CONFIG_NOSYSTEM={env.get('GIT_CONFIG_NOSYSTEM')!r}",
    )


TEMP_PREFIX = "install-form-"


def temp_listing() -> set[str]:
    """Names of this suite's temporary roots in the system temp folder."""
    temp_dir = Path(tempfile.gettempdir())
    return {p.name for p in temp_dir.glob(f"{TEMP_PREFIX}*")}


def remove_tree(path: Path) -> None:
    """Remove a temporary root, including read-only git pack files on Windows."""

    def make_writable_and_retry(func, target, _exc) -> None:
        os.chmod(target, stat.S_IWRITE)
        func(target)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=make_writable_and_retry)
    else:
        shutil.rmtree(path, onerror=make_writable_and_retry)


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

    # --- Issue #408, criterion 1: one /plugin command per copyable unit -----
    # A pasted multi-line block of slash commands is read as one command by
    # Claude Code; the second line becomes part of the URL. One command per
    # fence (README) and per copyable action (site) removes the failure.
    all_install_fences = fence_blocks(section)
    multi_command_fences = [
        block for block in all_install_fences if len(slash_commands_in(block)) > 1
    ]
    check(
        "no README Install fence holds more than one /plugin command",
        not multi_command_fences,
        f"fences holding multiple slash commands: {multi_command_fences!r}",
    )
    site_actions = re.findall(
        r'<p class="action">(.*?)</p>', site, flags=re.DOTALL
    )
    multi_command_site_actions = [
        action
        for action in site_actions
        if sum(
            len(slash_commands_in(kbd))
            for kbd in re.findall(r"<kbd>([^<]+)</kbd>", action)
        )
        > 1
    ]
    check(
        "no site Install action holds more than one /plugin command",
        not multi_command_site_actions,
        "site actions holding multiple slash commands: "
        f"{multi_command_site_actions!r}",
    )

    # --- Issue #408, criterion 2: reload / --force after install ------------
    # The vendor docs say a plugin loads on /reload-plugins or the next start,
    # and that a reload left pending stays pending until /reload-plugins --force.
    # The README must say so, with the page and the date it was read.
    install_command_at = section.find("/plugin install mrbinnacle-engineering")
    reload_guidance_at = section.find("/reload-plugins")
    check(
        "README puts reload guidance after the install commands",
        0 <= install_command_at < reload_guidance_at,
        "## Install does not tell the reader when the cards appear",
    )
    check(
        "README gives /reload-plugins --force for a pending reload",
        bool(
            re.search(
                r"(?is)pending.{0,160}/reload-plugins --force", section
            )
        ),
        "## Install does not name the --force form for a pending reload",
    )
    check(
        "README cites the Claude Code plugin docs URL with a read date",
        PLUGIN_DOCS_URL in section and f"read {PLUGIN_DOCS_READ}" in section,
        f"expected {PLUGIN_DOCS_URL} and a read date of {PLUGIN_DOCS_READ} in ## Install",
    )

    # --- Issue #408, criterion 3: confirm what is installed ------------------
    # The version and the plugin list come from the tool, not from prose the
    # README would have to retype on every release.
    check(
        "README says claude plugin list reports installed plugins and versions",
        bool(
            re.search(
                r"(?is)claude plugin list.{0,200}installed plugins.{0,100}versions",
                section,
            )
        ),
        "## Install does not name a command that shows the installed plugin and version",
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
    shell_install_commands = readme_shell_install_commands(section)
    shell_install_names = [command[3] for command in shell_install_commands]
    slash_names = slash_install_names(readme) + slash_install_names(site)
    check(
        "README shell fence provides runnable marketplace and plugin commands",
        any(
            "marketplace add" in fence and "plugin install" in fence
            for fence in install_fences
        )
        or (
            "claude plugin marketplace add" in section
            and bool(shell_install_names)
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

    # --- Criterion 2, requirement 6 and round 2: live cold installs ---------
    # Every directory the live half creates sits under one temporary root,
    # removed on the way out whether the run passes, fails or raises.
    temp_before = temp_listing()
    temp_root = Path(tempfile.mkdtemp(prefix=f"{TEMP_PREFIX}333-"))
    try:
        check_cold_env(temp_root)
        live_cold_installs(
            temp_root,
            install_fences,
            shell_install_commands,
            declared,
            readme_claude_version,
            readme_plugin_version,
        )
    finally:
        # A cleanup error must not bury an error from the live half, nor skip
        # the leftover check below; that check reports what remains.
        cleanup_error = ""
        try:
            remove_tree(temp_root)
        except OSError as exc:
            cleanup_error = f"; cleanup raised {exc!r}"
    leftover = sorted(temp_listing() - temp_before)
    check(
        f"suite leaves no {TEMP_PREFIX}* directory in the temp folder",
        not leftover,
        f"left behind under {tempfile.gettempdir()}: {leftover}{cleanup_error}",
    )

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


def find_claude() -> str | None:
    claude = shutil.which("claude")
    if claude is None:
        # Look beside a user-local install this container uses.
        candidate = Path.home() / ".local/claude-cli/node_modules/.bin/claude"
        claude = str(candidate) if candidate.is_file() else None
    return claude


def installed_card_counts(installed: dict[str, dict]) -> dict[str, int]:
    # Cards sit at the plugin root, not under skills/. Each plugin must carry
    # one; a total can hide an empty plugin.
    return {
        name: len(list(Path(plugin.get("installPath", "")).glob("*/SKILL.md")))
        if plugin.get("installPath")
        else 0
        for name, plugin in installed.items()
    }


def live_cold_installs(
    temp_root: Path,
    install_fences: list[str],
    shell_install_commands: list[list[str]],
    declared: set[str],
    readme_claude_version: str | None,
    readme_plugin_version: str | None,
) -> None:
    claude = find_claude()
    if claude is None:
        check(
            "claude CLI available for the live cold-install check",
            False,
            "no claude on PATH; criterion 2 cannot be exercised here",
        )
        return
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
        return

    # Case 1: published URL, README lines exactly as written.
    base = temp_root / "published"
    env = cold_env(base)
    add = run_cli(claude, add_command[1:], env, str(base))
    out = add.stdout + add.stderr
    check(
        "cold marketplace add (HTTPS form) succeeds without SSH",
        add.returncode == 0 and "Successfully added marketplace" in out,
        f"rc={add.returncode}\n{out}",
    )
    # Run every README install line exactly as written, every token
    # included; only argv[0] is replaced with the CLI path.
    readme_installs: list[tuple[str, int, str]] = []
    for command in shell_install_commands:
        proc = run_cli(claude, command[1:], env, str(base))
        readme_installs.append(
            (shlex.join(command), proc.returncode, proc.stdout + proc.stderr)
        )
    check(
        "README shell install lines run as written succeed",
        bool(readme_installs)
        and all(
            rc == 0 and "Successfully installed plugin" in plugin_out
            for _, rc, plugin_out in readme_installs
        ),
        "\n".join(f"{c}: rc={rc}\n{o}" for c, rc, o in readme_installs),
    )
    # The Verified forms record claims all three plugins; install any
    # declared plugin the README shell fence did not already name.
    named = {command[3] for command in shell_install_commands}
    installs = list(readme_installs)
    for name in sorted(declared - named):
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
    card_counts = installed_card_counts(installed)
    check(
        "cold install carries cards in every requested plugin",
        set(card_counts) == declared
        and all(count > 0 for count in card_counts.values()),
        f"card_counts={card_counts}",
    )

    # The Verified forms record must match this cold install.
    version_out = run_cli(claude, ["--version"], env, str(base))
    version_words = (version_out.stdout or version_out.stderr).split()
    cli_version = version_words[0] if version_words else ""
    check(
        "README Verified forms Claude Code version matches the installed CLI",
        bool(readme_claude_version) and readme_claude_version == cli_version,
        f"README says {readme_claude_version!r}, CLI reports {cli_version!r}",
    )
    installed_versions = {plugin.get("version") for plugin in installed.values()}
    check(
        "README Verified forms plugin version matches the cold install",
        bool(readme_plugin_version)
        and installed_versions == {readme_plugin_version},
        f"README says {readme_plugin_version!r}, cold install reports {installed_versions!r}",
    )

    # Case 2: the tree under test, not only the published default branch.
    local_base = temp_root / "local"
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
    local_card_counts = installed_card_counts(local_installed)
    check(
        "checked-out tree cold install carries cards in every plugin",
        set(local_card_counts) == declared
        and all(count > 0 for count in local_card_counts.values()),
        f"card_counts={local_card_counts}",
    )


if __name__ == "__main__":
    sys.exit(main())
