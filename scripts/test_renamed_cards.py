#!/usr/bin/env python3
"""Every name the v2.0.0 rename retired maps to its current card in RETIRED.md.

skills.sh keeps listing the pre-2.0.0 names, and `npx skills add --skill <old>`
fails on each with "No matching skills found" (#474). A reader who searches this
repository for the old name has to land on the current card.

The rename table is read from the v2.0.0 section of CHANGELOG.md, the record of
the rename itself, and never restated here. The comparison is row by row: an old
name that appears anywhere in RETIRED.md but beside the wrong card still fails.

No network. The skills.sh listing is a third-party page, so comparing it with the
card names is a manual release step in AGENTS.md; this suite only checks that the
step names the listing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_scoreboard as scoreboard  # noqa: E402

ROOT = SCRIPT_DIR.parent
CHANGELOG = ROOT / "CHANGELOG.md"
RETIRED = ROOT / "RETIRED.md"
AGENTS = ROOT / "AGENTS.md"

RELEASE_HEADING = "v2.0.0"
RENAME_PR = "286"
RENAMED_HEADING = "Renamed in 2.0.0"
RENAME_COUNT = 11
LISTING_URL = "https://www.skills.sh/MrBinnacle/skills"

CHANGELOG_ROW = re.compile(r"^\s*\| `([^`]+)`\s*\| `([^`]+)`\s*\|\s*$", re.MULTILINE)
RETIRED_ROW = re.compile(
    r"^\| `([^`]+)` \| \[`([^`]+)`\]\((skills/[^/]+/([^/]+)/SKILL\.md)\) \|$",
    re.MULTILINE,
)

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def section(body: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\b[^\n]*\n(.*?)(?=^## |\Z)", body)
    return match.group(1) if match else ""


def changelog_renames(body: str) -> dict[str, str]:
    """The Was/Is table of the published-card rename entry only.

    The same release section carries a second Was/Is table, the quarantine
    candidates renamed in #281. Those were never published, so skills.sh never
    listed them, and reading the whole section parses 34 rows instead of 11.
    """
    entry = re.search(
        rf"(?ms)^- \[#{RENAME_PR}\].*?(?=^- \[#|\Z)", section(body, RELEASE_HEADING)
    )
    return dict(CHANGELOG_ROW.findall(entry.group(0))) if entry else {}


def retired_renames(body: str) -> dict[str, tuple[str, str]]:
    """old name -> (current name, the card directory its link names)."""
    rows = RETIRED_ROW.findall(section(body, RENAMED_HEADING))
    return {old: (new, link_dir) for old, new, _link, link_dir in rows}


def problems(renames: dict[str, str], retired_body: str, cards: set[str]) -> list[str]:
    mapped = retired_renames(retired_body)
    found: list[str] = []
    for old, new in sorted(renames.items()):
        if old not in mapped:
            found.append(f"{old}: not in RETIRED.md '## {RENAMED_HEADING}'")
            continue
        stated, link_dir = mapped[old]
        if stated != new:
            found.append(f"{old}: RETIRED.md says {stated}, the CHANGELOG says {new}")
        if link_dir != new:
            found.append(f"{old}: the link points at {link_dir}, not {new}")
        if new not in cards:
            found.append(f"{old}: current name {new} is not a published card directory")
    for old in sorted(set(mapped) - set(renames)):
        found.append(f"{old}: in RETIRED.md but not in the CHANGELOG rename table")
    return found


def case_changelog_table_parses(renames: dict[str, str]) -> None:
    check(
        f"the CHANGELOG {RELEASE_HEADING} rename table has {RENAME_COUNT} rows",
        len(renames) == RENAME_COUNT,
        f"parsed {len(renames)}: {renames}",
    )


def case_every_rename_is_mapped(renames: dict[str, str], cards: set[str]) -> None:
    found = problems(renames, RETIRED.read_text(encoding="utf-8"), cards)
    failed = {line.split(":")[0] for line in found}
    mapped = sum(1 for old in renames if old not in failed)
    check(
        f"RETIRED.md maps every renamed card to an existing card ({mapped} of {len(renames)})",
        not found,
        "\n  " + "\n  ".join(found),
    )


def case_release_step_names_the_listing() -> None:
    check(
        "the AGENTS.md release procedure names the skills.sh listing",
        LISTING_URL in AGENTS.read_text(encoding="utf-8"),
        f"{LISTING_URL} not found",
    )


def case_controls(renames: dict[str, str], cards: set[str]) -> None:
    """The check refuses a wrong mapping and a missing card, not only an absent section."""
    old, new = sorted(renames.items())[0]
    good = (
        f"## {RENAMED_HEADING}\n\n"
        f"| `{old}` | [`{new}`](skills/b/{new}/SKILL.md) |\n"
    )
    check("control: a correct single row passes", problems({old: new}, good, cards) == [])
    wrong = good.replace(f"[`{new}`]", "[`im-up`]")
    check("control: a row naming the wrong card fails", problems({old: new}, wrong, cards) != [])
    check(
        "control: a current name with no card directory fails",
        problems({old: new}, good, cards - {new}) != [],
    )
    elsewhere = f"Some prose naming `{old}` and `{new}`.\n"
    check(
        "control: names outside the section do not count",
        problems({old: new}, elsewhere, cards) != [],
    )


def main() -> None:
    renames = changelog_renames(CHANGELOG.read_text(encoding="utf-8"))
    cards = {path.name for path in scoreboard.iter_skill_dirs(ROOT)}
    case_changelog_table_parses(renames)
    if renames:
        case_every_rename_is_mapped(renames, cards)
        case_controls(renames, cards)
    case_release_step_names_the_listing()
    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: every v2.0.0 rename maps to its current card")


if __name__ == "__main__":
    main()
