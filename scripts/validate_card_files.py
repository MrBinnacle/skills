#!/usr/bin/env python3
"""Require every published card to carry the three card contract files.

AGENTS.md states the contract: a card ships SKILL.md, gotchas.md and
EVIDENCE.md. This is the check behind that sentence, and it checks presence
only -- what an EVIDENCE.md must say row by row is validate_conformance.py's
O4. Output is ASCII-only, matching the other validators, so a cp1252 console
cannot die on a status line.

DISCOVERY: BY DIRECTORY, NOT BY THE SKILL.md MARKER
    Deliberately wider than validate_conformance.py's `skills/*/*/SKILL.md`
    glob. A checker that finds cards *by* SKILL.md can never report the card
    whose missing file is SKILL.md: the one card it must refuse is the one it
    cannot see.

    What the wider walk costs is that every directory two levels under
    `skills/` gets claimed as a published card, so the two things the tree
    already says are not published are honoured here rather than re-decided --
    the unshipped buckets AGENTS.md sanctions for parking work in progress,
    and dot-directories. The vocabulary is validate_scoreboard.py's own
    frozenset, imported rather than restated, so widening it stays a one-place
    edit; that is the same delegation validate_conformance.py makes for the
    controlled-field names, and it keeps this script's `N published card(s)`
    and the front page's `N admitted` from being two different numbers.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_scoreboard as scoreboard  # noqa: E402

REQUIRED_FILES: Final[tuple[str, ...]] = ("SKILL.md", "gotchas.md", "EVIDENCE.md")


def find_cards(root: Path) -> list[Path]:
    skills = root / "skills"
    if not skills.is_dir():
        return []
    return sorted(
        card
        for bucket in skills.iterdir()
        if bucket.is_dir()
        and not bucket.name.startswith(".")
        and bucket.name not in scoreboard.UNSHIPPED_BUCKETS
        for card in bucket.iterdir()
        if card.is_dir()
    )


def validate(root: Path) -> None:
    cards = find_cards(root)
    if not cards:
        print(
            f"REJECTED: no published cards found under {root}/skills. "
            "A run that checked nothing is not a pass.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    missing = [
        (card, filename)
        for card in cards
        for filename in REQUIRED_FILES
        if not (card / filename).is_file()
    ]
    if missing:
        for card, filename in missing:
            # Bucket-qualified, not the bare directory name: two buckets may
            # hold a card of the same name, and "half-built: missing
            # gotchas.md" twice over names no file a maintainer can open.
            print(
                f"  - {card.relative_to(root).as_posix()}: missing {filename}",
                file=sys.stderr,
            )
        print(
            f"REJECTED: {len(missing)} required card file(s) missing across "
            f"{len(cards)} published card(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(
        f"PASS: {len(cards)} published card(s), all carry "
        + ", ".join(REQUIRED_FILES)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to validate (default: this repository)",
    )
    args = parser.parse_args()
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
