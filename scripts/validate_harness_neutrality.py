#!/usr/bin/env python3
"""Refuse a published SKILL.md that names one agent harness's tools, hooks or paths.

THE RULE (AGENTS.md, "Authoring conventions" -> "Harness neutrality", 2026-10-10)

    A published card's SKILL.md is the instruction surface every harness loads:
    Claude Code through the plugin manifest, Pi through its `skills` setting,
    any Agent Skills reader through the directory. A sentence in it that only
    makes sense in one harness -- "block the Bash tool call with PreToolUse",
    "put this in ~/.claude/settings.json", "a Pi extension can block it" -- is
    dead text in every other harness, and a reader there has no way to tell
    which sentences are for them. So the body and the description name the
    action (a pre-tool-call guard, the shell tool, the harness's rules file)
    and leave the harness-specific recipe to a sibling file, one per harness.

WHAT IT READS, AND WHY ONLY THAT

    `SKILL.md` only, frontmatter and body, fenced code included. The other
    files a card ships are deliberately outside the rule:

    - `gotchas.md` is an append-only ledger. Entries already written stay as
      written (AGENTS.md: "append-only wins"), and several record incidents
      that happened in a named harness.
    - `EVIDENCE.md` records facts about measurements, and a measurement ran
      somewhere: "Claude Code 2.1.197", "a PreToolUse hook blocked all 7".
      Neutralising a receipt would falsify it.
    - A recipe sibling (`preventive-recipes.md`) is where the harness-specific
      text is SUPPOSED to live, one section per harness.

    A card whose whole subject is one harness's mechanism (today
    `pretooluse-prose`) cannot be neutral without becoming a different card.
    That is a per-card decision for the operator, not a pattern this check
    can take; until it is taken the card sits on the allowlist below.

THE ALLOWLIST CAN ONLY SHRINK

    The gate's first run is a measurement of the tree as it stood on
    2026-10-10, not a migration. Every (card, pattern) pair that was already
    breaching is recorded below so the gate lands green on the four cards the
    migration neutralised and red on any NEW breach anywhere. An entry whose
    breach no longer occurs is reported stale and FAILS the gate, so repairing
    a card forces its entry out. Nothing here can rot unnoticed.

Usage:
    python scripts/validate_harness_neutrality.py            # this repository
    python scripts/validate_harness_neutrality.py --root DIR # another tree (the suite uses this)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_card_files as card_files  # noqa: E402

# (pattern id, regex, what a neutral card says instead). Every id names ONE
# harness, so a reader of a finding knows which harness's word leaked. The
# Claude Code set is the porting lint's list (pi/scripts/lint_pi_skills.py,
# 2026-10-10), which found zero residue on twelve ported cards; the Pi set
# is the reverse direction, because a card neutralised BY a Pi port is the
# obvious way to trade one harness's words for another's.
PATTERNS: Final[tuple[tuple[str, str, str], ...]] = (
    (
        "claude-code-name",
        r"\bClaude Code\b",
        "say 'the harness' or name the action; a harness-specific recipe goes in a sibling file",
    ),
    (
        "claude-code-tool",
        r"\b(?:Bash|Agent|Task|Skill|SendMessage|TodoWrite|AskUserQuestion|WebFetch|WebSearch"
        r"|NotebookEdit|MultiEdit|Glob|Grep|Read|Write|Edit)\s+tool\b"
        r"|`(?:Bash|Agent|Task|Skill|SendMessage|TodoWrite|AskUserQuestion|MultiEdit|Glob|Grep|NotebookEdit)`"
        r"|(?<!Git )(?<!git )\bBash\b",
        "say 'the shell tool', 'a subagent', 'the file-edit tool'",
    ),
    (
        "claude-code-hook",
        r"\b(?:PreToolUse|PostToolUse|UserPromptSubmit|SessionStart|SubagentStop|PreCompact)\b"
        r"|\bhookSpecificOutput\b|\bpermissionDecision\b",
        "say 'a pre-tool-call guard', 'a post-tool-call handler', 'a prompt-submit router'",
    ),
    (
        "claude-code-path",
        r"(?<![\w-])\.claude(?:-plugin)?\b|\bCLAUDE\.md\b|\bsettings\.local\.json\b|\bhooks\.json\b|\$ARGUMENTS\b",
        "say 'the harness's rules file' / 'the harness's settings'; a path goes in a sibling file",
    ),
    (
        "pi-name",
        r"\bPi extension\b|\bPi tool\b|\bin Pi\b|\bPi's\b",
        "say 'the harness' or 'an extension that runs on the tool call'",
    ),
    (
        "pi-path",
        r"(?<![\w-])\.pi/|\bpi\.on\(|\bctx\.executeTool\b|\bExtensionAPI\b",
        "a Pi recipe goes in a sibling file, one section per harness",
    ),
)

_COMPILED: Final[tuple[tuple[str, re.Pattern[str], str], ...]] = tuple(
    (pid, re.compile(rx), hint) for pid, rx, hint in PATTERNS
)

# Pre-existing breaches, recorded on the day the gate landed. See the module
# docstring: this list can only shrink.
_ALLOWLIST_RECORDED: Final[str] = "2026-10-10"
_ALLOWLIST: Final[frozenset[tuple[str, str]]] = frozenset({
    # Subject IS a Claude Code mechanism. Per-card decision pending (handoff
    # 2026-10-10: "a sibling file per harness, not a copy of the card").
    ("skills/engineering/pretooluse-prose", "claude-code-name"),
    ("skills/engineering/pretooluse-prose", "claude-code-tool"),
    ("skills/engineering/pretooluse-prose", "claude-code-hook"),
    # Session-boundary pair: config path and transcript path are Claude Code's.
    ("skills/engineering/im-down", "claude-code-name"),
    ("skills/engineering/im-down", "claude-code-path"),
    ("skills/engineering/im-up", "claude-code-name"),
    ("skills/engineering/im-up", "claude-code-path"),
    # Names the harness and its shell tool in the trap description.
    ("skills/engineering/stale-deploy", "claude-code-name"),
    ("skills/engineering/stale-deploy", "claude-code-tool"),
    # Router hook is named by harness and event.
    ("skills/meta/dead-predicate", "claude-code-name"),
    ("skills/meta/dead-predicate", "claude-code-hook"),
    # Subagent definition path, and the Agent / SendMessage / Bash tool names,
    # are Claude Code's.
    ("skills/orchestration/subagent-handback", "claude-code-path"),
    ("skills/orchestration/subagent-handback", "claude-code-tool"),
})


def findings(card: Path) -> list[tuple[str, int, str, str]]:
    """(pattern id, line number, matched text, hint) for one card's SKILL.md."""
    skill = card / "SKILL.md"
    if not skill.is_file():
        return []
    hits: list[tuple[str, int, str, str]] = []
    text = skill.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), 1):
        for pid, rx, hint in _COMPILED:
            for m in rx.finditer(line):
                hits.append((pid, lineno, m.group(0), hint))
    return hits


def validate(root: Path) -> int:
    cards = card_files.find_cards(root)
    if not cards:
        print(
            f"REJECTED: no published cards found under {root}/skills. "
            "A run that checked nothing is not a pass."
        )
        return 1

    found: list[tuple[str, str, int, str, str]] = []
    for card in cards:
        rel = card.relative_to(root).as_posix()
        for pid, lineno, text, hint in findings(card):
            found.append((rel, pid, lineno, text, hint))

    allowed = [f for f in found if (f[0], f[1]) in _ALLOWLIST]
    blocking = [f for f in found if (f[0], f[1]) not in _ALLOWLIST]

    present = {card.relative_to(root).as_posix() for card in cards}
    live = {(rel, pid) for rel, pid, *_ in found}
    applicable = {entry for entry in _ALLOWLIST if entry[0] in present}
    stale = sorted(applicable - live)

    if allowed:
        print(
            f"ALLOWED: {len(allowed)} pre-existing harness-specific line(s) "
            f"recorded {_ALLOWLIST_RECORDED}, not repaired by this gate:"
        )
        for rel, pid, lineno, text, _ in allowed:
            print(f"  ~ {rel}/SKILL.md:{lineno}: {pid} matched {text!r}")

    if blocking or stale:
        for rel, pid, lineno, text, hint in blocking:
            print(f"  - {rel}/SKILL.md:{lineno}: {pid} matched {text!r}. Instead: {hint}")
        for rel, pid in stale:
            print(
                f"  - allowlist entry no longer applies and must be removed: "
                f"{rel} ({pid}). Recorded {_ALLOWLIST_RECORDED}; that breach is fixed."
            )
        print(
            f"REJECTED: {len(blocking)} harness-specific line(s) and {len(stale)} stale "
            f"allowlist entr(y/ies) across {len(cards)} published card(s). "
            "A card's SKILL.md names the action, not one harness's tool, hook or path; "
            "the harness-specific recipe goes in a sibling file."
        )
        return 1

    print(
        f"PASS: harness neutrality - {len(cards)} published card(s), no SKILL.md names a "
        "harness-specific tool, hook or path"
        + (
            f" -- EXCEPT the {len(allowed)} allowlisted line(s) listed above, "
            f"recorded {_ALLOWLIST_RECORDED} and not repaired by this gate"
            if allowed
            else ""
        )
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to validate (default: this repository)",
    )
    args = parser.parse_args(argv)
    return validate(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
