#!/usr/bin/env python3
"""Require every published card to carry the three card contract files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final

REQUIRED_FILES: Final[tuple[str, ...]] = ("SKILL.md", "gotchas.md", "EVIDENCE.md")


def find_cards(root: Path) -> list[Path]:
    skills = root / "skills"
    if not skills.is_dir():
        return []
    return sorted(
        card
        for bucket in skills.iterdir()
        if bucket.is_dir()
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
            print(f"  - {card.name}: missing {filename}", file=sys.stderr)
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
        default=Path(__file__).resolve().parent.parent,
        help="tree to validate (default: this repository)",
    )
    args = parser.parse_args()
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
