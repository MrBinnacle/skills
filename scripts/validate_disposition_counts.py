#!/usr/bin/env python3
"""Assert the front page's stated disposition counts agree with the record.

The README's "Admission method" section restates what the S295 disposition
found: how many cards it triaged, how many it stood, how many it called thin,
and how many it called ceiling-likely. Those counts are hand-maintained prose
-- a card is re-triaged or the record changes and the page keeps the old
arithmetic, the same drift that left the origin tiering claiming seven when
the records read six (2026-08-15).

This check recomputes each stated count from the one record it counts -- the
disposition record the page itself links -- and refuses on disagreement,
naming the count and both values. The page is allowed to state no count at
all (stating is optional, the same ruling that retired the banner and origin
tallies); a count it DOES state must agree with the record. A verdict the
check has never seen is refused rather than guessed at, so an unknown verdict
cannot silently miscount the page's restatement.

Output is ASCII-only so the Windows CI cell does not die on cp1252.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NoReturn

# The verdict vocabulary is closed for the same reason every other count here
# is closed: an opening word this file has never seen is not a verdict to
# bucket, and reading it as one would put a number on the page the record may
# not support. "STANDS (weakly)" opens with STANDS, so the test is on the start
# of the cell.
VERDICT_TIERS = ("STANDS", "RECURRENCE-THIN", "CEILING-LIKELY")

# A stated count may be a digit or a word. The word map covers the range the
# page is ever likely to state; an unrecognised word is a refusal, because a
# count the check cannot read is a drift the check exists to catch.
_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

# Each stated count is a word or digit immediately before the phrase that
# identifies it. The phrases are anchored to the README's actual wording: a
# count written against a different phrase is not in the checked vocabulary
# and is skipped, the same optional-stating rule that retired the origin and
# banner tallies. Softening is not a refusal - it is an unstated count.
COUNT_PATTERNS = (
    ("total", re.compile(r"all\s+(\w+)\s+published\s+cards")),
    ("stand", re.compile(r"(\w+)\s+cards?\s+that\s+stand")),
    ("thin", re.compile(r"(\w+)\s+with\s+thin\s+recurrence\s+records")),
    ("ceiling", re.compile(r"(\w+)\s+with\s+a\s+ceiling-likely\s+screen\s+result")),
)

DISPOSITION_LINK_RE = re.compile(r"\]\((dispositions/[^)]+\.md)\)")


def fail(msg: str) -> NoReturn:
    # ASCII only. NoReturn makes the guard-clause discipline type-safe.
    print(f"REJECTED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1) if match else ""


def parse_count(token: str, where: str) -> int:
    token = token.strip().strip("*`")
    if token.isdigit():
        return int(token)
    key = token.lower()
    if key in _WORDS:
        return _WORDS[key]
    fail(
        f"{where}: stated count {token!r} is not a recognised number. A count "
        f"the check cannot read is a drift the check exists to catch; write a "
        f"digit or a word the map covers."
    )


def disposition_path(root: Path, admission_body: str) -> Path:
    link = DISPOSITION_LINK_RE.search(admission_body)
    if not link:
        fail(
            "README.md Admission method: does not link a disposition record "
            "(no ](dispositions/....md) link). The counts the section states "
            "derive from that record, so the link is what ties the check to "
            "the record it counts."
        )
    return root / link.group(1)


def derive_disposition_counts(disposition: Path) -> dict[str, int]:
    """Count the disposition's verdict rows by category, read from the record.

    Same refusal discipline as the scoreboard's measured and origin counts: a
    missing record, a missing Verdicts table, or a verdict outside the closed
    vocabulary is a refusal, not a zero. Deriving `0 stand` from an absent row
    would invent exactly the number this check exists to keep honest.
    """
    if not disposition.is_file():
        fail(f"missing disposition record at {disposition}")
    body = section(disposition.read_text(encoding="utf-8"), "Verdicts")
    if not body:
        fail(
            f"{disposition}: no '## Verdicts' section, so the stated counts "
            f"cannot be derived from it."
        )
    counts = dict.fromkeys(("total", *VERDICT_TIERS), 0)
    saw_table = False
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0].lower() == "card":
            continue
        if re.match(r"^[\s|:-]+$", line):
            continue
        saw_table = True
        counts["total"] += 1
        verdict = cells[1] if len(cells) > 1 else ""
        for tier in VERDICT_TIERS:
            if verdict.startswith(tier):
                counts[tier] += 1
                break
        else:
            fail(
                f"{disposition}: verdict {verdict!r} opens with a word outside "
                f"the closed vocabulary - {', '.join(VERDICT_TIERS)}. Reading "
                f"an unknown verdict as a tier would put a number on the page "
                f"the record may not support."
            )
    if not saw_table:
        fail(f"{disposition}: '## Verdicts' has no table rows to count.")
    return {"total": counts["total"], "stand": counts["STANDS"],
            "thin": counts["RECURRENCE-THIN"], "ceiling": counts["CEILING-LIKELY"]}


def stated_counts(readme_body: str) -> dict[str, int]:
    """The counts the README states, keyed by name. Only stated counts appear.

    Stating a count is optional (the same ruling that retired the origin and
    banner tallies); a count the page does not state is not checked. A count it
    does state must agree with the record, and an unrecognised number is a
    refusal rather than a silent miss.
    """
    stated: dict[str, int] = {}
    for name, pattern in COUNT_PATTERNS:
        m = pattern.search(readme_body)
        if not m:
            continue
        stated[name] = parse_count(m.group(1), f"README.md disposition count {name!r}")
    return stated


def validate(root: Path) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        fail(f"missing {readme}")
    admission = section(readme.read_text(encoding="utf-8"), "Admission method")
    if not admission:
        fail("README.md: no '## Admission method' section")
    disposition = disposition_path(root, admission)
    derived = derive_disposition_counts(disposition)
    stated = stated_counts(admission)
    if not stated:
        # The page states no disposition count. Stating is optional; the
        # derivation above still ran as the record-conformance discipline, so
        # a malformed record refuses here regardless of what the page says.
        print(
            f"PASS: README states no disposition count; record "
            f"{disposition.relative_to(root)} derives "
            f"{derived['total']} triaged, {derived['stand']} stand, "
            f"{derived['thin']} thin, {derived['ceiling']} ceiling-likely"
        )
        return
    disagreements = [
        f"{name}: README states {stated[name]}, records read {derived[name]}"
        for name in stated
        if stated[name] != derived[name]
    ]
    if disagreements:
        fail(
            f"README.md disposition counts disagree with the disposition record "
            f"({disposition.relative_to(root)}) - " + "; ".join(disagreements)
        )
    print(
        f"PASS: README disposition counts agree with "
        f"{disposition.relative_to(root)} - {derived['total']} triaged, "
        f"{derived['stand']} stand, {derived['thin']} thin, "
        f"{derived['ceiling']} ceiling-likely"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to validate (default: two levels above this script)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parent.parent
    validate(root)


if __name__ == "__main__":
    main()
