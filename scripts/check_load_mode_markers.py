#!/usr/bin/env python3
"""A bucket README marks a card *(by hand)* exactly when its frontmatter says so.

Each bucket README restates one fact from every card's SKILL.md frontmatter:
`disable-model-invocation: true` means the card runs only when invoked by name,
and its README line carries *(by hand)*. ADR 0008 moved four cards to by hand
and their markers were edited by hand, with nothing comparing the two (#558).

The frontmatter is parsed as key and value inside the leading `---` block, so a
quoted value or a mention of the key in the body cannot change the answer. The
standing-cost check reads the same fact with DISABLE_MODEL_INVOCATION_RE over
the whole file; a card on which the two readers disagree is refused here too,
because one of them is then wrong about it.

`runs_by_hand` is the shared reader: the root README Loads check
(test_readme_admission_lead.py, #553) imports it rather than parsing the flag a
second time.

A card line is `- [**name**](name/SKILL.md)`, and the marker counts only when it
is the first thing after the link. A marker placed later in the line reads as
unmarked, and the refusal says so. A missing card line is refused in the words
check_prose_claims.py uses for the same cause: the bucket holds a card the
README does not name.

Exit 0 prints a PASS line. Exit 1 prints one REJECTED line per breach, naming
the card and the README.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_scoreboard as scoreboard  # noqa: E402
from validate_standing_costs import DISABLE_MODEL_INVOCATION_RE  # noqa: E402

FLAG_KEY = "disable-model-invocation"
BY_HAND_MARKER = "*(by hand)*"
# A bucket README card line: `- [**name**](name/SKILL.md) *(by hand)* ...`.
CARD_LINE_RE = re.compile(r"^- \[\*\*([a-z0-9-]+)\*\*\]\(([a-z0-9-]+)/SKILL\.md\)(.*)$")


def frontmatter(text: str) -> dict[str, str]:
    """Top-level `key: value` pairs of the leading `---` block; empty when absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.split(" #", 1)[0].strip().strip("'\"")
        fields[key.strip()] = value
    return {}


def flag_set(skill_text: str) -> bool:
    """Whether SKILL.md text sets `disable-model-invocation: true` in its frontmatter."""
    return frontmatter(skill_text).get(FLAG_KEY, "").lower() == "true"


def runs_by_hand(skill_md: Path) -> bool:
    """Whether the card's frontmatter sets `disable-model-invocation: true`."""
    return flag_set(skill_md.read_text(encoding="utf-8"))


def readme_card_lines(text: str) -> dict[str, list[bool]]:
    """Card name -> the by-hand marker state of every README line listing it."""
    lines: dict[str, list[bool]] = {}
    for line in text.splitlines():
        match = CARD_LINE_RE.match(line)
        if not match or match.group(1) != match.group(2):
            continue
        marked = match.group(3).lstrip().startswith(BY_HAND_MARKER)
        lines.setdefault(match.group(1), []).append(marked)
    return lines


def card_problems(skill_dir: Path, readme_lines: dict[str, list[bool]] | None) -> list[str]:
    """Every breach for one card; `readme_lines` is None when the bucket has no README."""
    card, bucket = skill_dir.name, skill_dir.parent.name
    label = f"skills/{bucket}/README.md"
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    flagged = flag_set(skill_text)
    problems: list[str] = []
    if bool(DISABLE_MODEL_INVOCATION_RE.search(skill_text)) != flagged:
        problems.append(
            f"{card}: the frontmatter reads {FLAG_KEY}={'true' if flagged else 'unset'}, "
            "but the standing-cost check's DISABLE_MODEL_INVOCATION_RE reads it the other way"
        )
    if readme_lines is None:
        return problems + [f"{card}: {label} does not exist, so no line lists this card"]
    marks = readme_lines.get(card, [])
    if not marks:
        return problems + [
            f"{card}: skills/{bucket}/ holds a card the README does not name "
            f"({label} has no `- [**{card}**]({card}/SKILL.md)` line)"
        ]
    if len(marks) > 1:
        problems.append(f"{card}: {label} lists it on {len(marks)} lines, expected one")
    for marked in marks:
        if marked and not flagged:
            problems.append(
                f"{card}: {label} marks it {BY_HAND_MARKER}, "
                f"but its SKILL.md frontmatter does not set {FLAG_KEY}: true"
            )
        if flagged and not marked:
            problems.append(
                f"{card}: its SKILL.md frontmatter sets {FLAG_KEY}: true, "
                f"but {label} does not mark it {BY_HAND_MARKER} right after the link "
                "(a marker later in the line is not read)"
            )
    return problems


def check(root: Path) -> tuple[list[Path], list[str]]:
    cards = scoreboard.iter_skill_dirs(root)
    problems: list[str] = []
    for skill_dir in cards:
        readme = skill_dir.parent / "README.md"
        lines = readme_card_lines(readme.read_text(encoding="utf-8")) if readme.is_file() else None
        problems.extend(card_problems(skill_dir, lines))
    return cards, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=SCRIPT_DIR.parent)
    args = parser.parse_args(argv)
    cards, problems = check(args.root)
    if not cards:
        print("REJECTED: no published card was found, so nothing was compared")
        return 1
    if problems:
        for problem in problems:
            print(f"REJECTED: {problem}")
        return 1
    by_hand = sum(runs_by_hand(d / "SKILL.md") for d in cards)
    print(
        f"PASS: {len(cards)} published cards, {by_hand} by hand; every bucket README "
        "line agrees with its card's frontmatter"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
