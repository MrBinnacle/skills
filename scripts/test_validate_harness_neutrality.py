#!/usr/bin/env python3
"""Suite for validate_harness_neutrality.py.

WHAT THIS SUITE HAS TO PROVE

    A gate that scans SKILL.md for harness names and matches nothing looks the
    same as one that works (vacuous-check). So the load-bearing cases are
    POISON: a planted card whose SKILL.md names a Claude Code tool, a Claude
    Code hook event, a `.claude/` path, and a Pi extension, each in a fresh
    tree with no allowlist cover. Each must turn the checker red, by the
    pattern id that owns the word, and the finding must name the line.

    The clean case proves the checker can pass. The aux-file case proves the
    scope is SKILL.md only: the same words in gotchas.md and EVIDENCE.md must
    not trip it, because the ledger is append-only and the receipt is a fact.
    The git-prefix case proves "Git Bash" (the shell this repository's own
    AGENTS.md names) is not read as the Claude Code `Bash` tool. The live-tree
    case is the sweep CI runs; it must pass with the allowlist as recorded.

Every case builds a temporary tree and calls the real entrypoint with
`--root`. No poison fixture is committed: a harness-naming card under
`skills/` would sit inside the guarded set and turn the real run red.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts" / "validate_harness_neutrality.py"

FAILURES: list[str] = []

NEUTRAL_SKILL = """---
name: planted
description: Use when a guard must refuse a shell command before it runs.
---

# planted

Install a pre-tool-call guard on the shell tool. The harness's rules file names it.
Open [gotchas.md](gotchas.md) when the guard blocks prose. It records false positives.
"""


def fail(case: str, detail: str) -> None:
    FAILURES.append(case)
    print(f"  FAIL {case}: {detail}")


def make_tree(root: Path, skill_md: str, extra: dict[str, str] | None = None) -> Path:
    card = root / "skills" / "engineering" / "planted"
    card.mkdir(parents=True)
    (card / "SKILL.md").write_text(skill_md, encoding="utf-8")
    for name, text in (extra or {}).items():
        (card / name).write_text(text, encoding="utf-8")
    return card


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**__import__("os").environ, "PYTHONUTF8": "1"},
    )


def expect_refusal(case: str, skill_md: str, pattern_id: str, needle: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        make_tree(Path(tmp), skill_md)
        result = run(Path(tmp))
    if result.returncode == 0:
        fail(case, f"accepted a SKILL.md that names {needle!r}")
        return
    if pattern_id not in result.stdout or repr(needle) not in result.stdout:
        fail(case, f"refused, but did not name {needle!r} under {pattern_id}:\n{result.stdout}")
        return
    if "planted/SKILL.md:" not in result.stdout:
        fail(case, f"refused, but did not name the file and line:\n{result.stdout}")
        return
    print(f"  ok   {case}")


def expect_pass(case: str, skill_md: str, extra: dict[str, str] | None = None) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        make_tree(Path(tmp), skill_md, extra)
        result = run(Path(tmp))
    if result.returncode != 0 or not result.stdout.startswith("PASS:"):
        fail(case, f"refused a neutral card:\n{result.stdout}")
        return
    print(f"  ok   {case}")


def main() -> int:
    print("validate_harness_neutrality suite")

    expect_refusal(
        "claude_code_tool_name_is_refused",
        NEUTRAL_SKILL.replace("the shell tool", "the Bash tool"),
        "claude-code-tool",
        "Bash tool",
    )
    expect_refusal(
        "claude_code_hook_event_is_refused",
        NEUTRAL_SKILL.replace("a pre-tool-call guard", "a `PreToolUse` hook"),
        "claude-code-hook",
        "PreToolUse",
    )
    expect_refusal(
        "claude_code_path_is_refused",
        NEUTRAL_SKILL.replace("The harness's rules file", "`.claude/settings.json`"),
        "claude-code-path",
        ".claude",
    )
    expect_refusal(
        "claude_code_name_is_refused",
        NEUTRAL_SKILL.replace("The harness's rules file", "Claude Code"),
        "claude-code-name",
        "Claude Code",
    )
    expect_refusal(
        "pi_extension_is_refused",
        NEUTRAL_SKILL.replace("a pre-tool-call guard", "a Pi extension"),
        "pi-name",
        "Pi extension",
    )
    expect_refusal(
        "description_is_scanned_too",
        NEUTRAL_SKILL.replace("refuse a shell command", "refuse a Bash tool command"),
        "claude-code-tool",
        "Bash tool",
    )

    expect_pass("neutral_card_passes", NEUTRAL_SKILL)
    expect_pass(
        "git_bash_is_not_the_bash_tool",
        NEUTRAL_SKILL + "\nThe shell here is Git Bash (MSYS).\n",
    )
    expect_pass(
        "aux_files_are_out_of_scope",
        NEUTRAL_SKILL,
        {
            "gotchas.md": "- [OBSERVED 2026-05-25] A PreToolUse hook in Claude Code blocked it.\n",
            "EVIDENCE.md": "| **Origin** | OBSERVED, Claude Code 2.1.197, `.claude/settings.json` |\n",
            "preventive-recipes.md": "## Claude Code `PreToolUse`\n\n## Pi extension `tool_call` handler\n",
        },
    )

    # Empty tree: a run that checked nothing is not a pass.
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "skills").mkdir()
        result = run(Path(tmp))
    if result.returncode == 0:
        fail("empty_tree_is_refused", "passed a tree with no cards")
    else:
        print("  ok   empty_tree_is_refused")

    # Stale allowlist entry: a repaired card must force its entry out.
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import validate_harness_neutrality as mod  # noqa: E402
    import io
    import contextlib

    saved = mod._ALLOWLIST
    try:
        mod._ALLOWLIST = frozenset({("skills/engineering/planted", "claude-code-tool")})
        with tempfile.TemporaryDirectory() as tmp:
            make_tree(Path(tmp), NEUTRAL_SKILL)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = mod.validate(Path(tmp))
        if code == 0 or "no longer applies" not in buf.getvalue():
            fail("stale_allowlist_entry_is_refused", f"exit {code}:\n{buf.getvalue()}")
        else:
            print("  ok   stale_allowlist_entry_is_refused")
    finally:
        mod._ALLOWLIST = saved

    # Live tree, as CI runs it.
    result = run(REPO_ROOT)
    if result.returncode != 0 or "PASS:" not in result.stdout:
        fail("live_tree_passes", f"the repository itself is refused:\n{result.stdout}")
    else:
        print("  ok   live_tree_passes")

    if FAILURES:
        print(f"FAIL: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        return 1
    print("PASS: validate_harness_neutrality suite, 12 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
