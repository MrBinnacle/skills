#!/usr/bin/env python3
"""Require every published card to carry the card contract: files, then rows.

AGENTS.md states the contract: a card ships SKILL.md, gotchas.md and
EVIDENCE.md, and its EVIDENCE.md states the recurrence rows. This is the check
behind those sentences. Output is ASCII-only, matching the other validators, so
a cp1252 console cannot die on a status line.

WHY THE ROW CHECKS LIVE HERE AND NOT IN validate_conformance.py's O4
    An earlier edition of this file said row-level checks belong to O4. They do
    not, and the reason is a boundary SECURITY.md draws itself: O4 is about the
    CONTROLLED fields (`Screen result`, `Paired verdict`) that the front-page
    scoreboard is derived from, under `conformance v1`, whose stated bump rule
    makes "a material change to what counts as meeting one" a version bump --
    and that edition has pre-registered what its first bump carries. The rows
    below are the other contract: ADMISSION.md's criterion 2 (occasions are
    counted, not predicted) and criterion 4 (a card can leave). Admission is
    "getting in", O4 is "staying", and widening `conformance v1` to carry an
    admission row would bump an edition for a change that is not its subject.
    So: the scoreboard's controlled fields stay O4's; the card contract
    AGENTS.md states -- files and recurrence rows -- is this script's.

    The row TABLE is parsed by validate_scoreboard.evidence_fields, imported
    rather than restated. That function skips fenced blocks and takes the first
    occurrence of a row on purpose; a second parser here would be a second set
    of those rules, and the two would disagree on exactly the records that
    document their own format.

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
import re
import sys
from pathlib import Path
from typing import Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_scoreboard as scoreboard  # noqa: E402

REQUIRED_FILES: Final[tuple[str, ...]] = ("SKILL.md", "gotchas.md", "EVIDENCE.md")

# The two rows a published card's EVIDENCE.md owes. `Occasions counted` answers
# ADMISSION.md's criterion 2 in the card's own file; `Re-screen trigger` is what
# criterion 4 needs to let the card leave. Both were already convention; this is
# the check that makes them contract.
OCCASIONS_ROW: Final[str] = "Occasions counted"
RESCREEN_ROW: Final[str] = "Re-screen trigger"

# The measured-demand row (#106). A dispatch is one invocation of a card --
# demand evidence, never recurrence, lift or worth (docs/adr/0001: a dispatch
# count is fan-out, and writing it into the recurrence row is the inflation
# ADMISSION.md criterion 2 refuses). The row is required so it cannot be
# silently dropped, and its form is checked: it opens with an integer or the
# exact phrase "No recorded dispatch" (the two trap cards fire through hook
# mechanisms the platform counter cannot see, so their zero must read as "no
# recorded dispatch", never "unused"), and it carries its measurement date,
# because a measured figure without a date cannot be judged stale.
DISPATCH_ROW: Final[str] = "Dispatches recorded"
# [1-9]: a zero written as a numeral is refused -- the invariant is that a
# zero reads "No recorded dispatch", so the counter's blindness to hook and
# always-loaded firings cannot be read as "unused".
DISPATCH_OPEN_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:[1-9]\d*\b|No recorded dispatch\b)"
)
# The date check anchors on the "measured <date>" clause, not on any date in
# the row: every live row also carries the delta-log inception date in its
# boilerplate, so a bare DATE_RE search would stay satisfied after the actual
# measurement clause was dropped.
DISPATCH_MEASURED_RE: Final[re.Pattern[str]] = re.compile(
    r"\bmeasured 20\d{2}-\d{2}-\d{2}\b"
)

REQUIRED_EVIDENCE_ROWS: Final[tuple[str, ...]] = (
    OCCASIONS_ROW,
    DISPATCH_ROW,
    RESCREEN_ROW,
)

# ADMISSION.md criterion 2: the failure recurs independently, "it is not a
# one-off". One counted occasion is a one-off, so the card says so in its own
# file rather than leaving a reader to do the arithmetic. The label is required
# BELOW the threshold and refused at or above it: a stale honesty label is its
# own kind of dishonest, and a card that earned its way out of the tier should
# not keep wearing the warning.
INDEPENDENT_OCCASIONS: Final[int] = 2
THIN_LABEL: Final[str] = "RECURRENCE-THIN"

# The count opens the row, because the first thing the row says is the number.
COUNT_RE: Final[re.Pattern[str]] = re.compile(r"^\s*(\d+)\b")
DATE_RE: Final[re.Pattern[str]] = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")

# The reverse direction's scope rule (#105, settled by measurement 2026-08-24).
# Every row check below takes the row as subject and the card as reference;
# nothing asked whether the card records an occurrence the row failed to cite,
# so an undercount stayed green. The scope of the reverse check is a rule about
# HOW an occurrence is recorded, not a list of dates to ignore: a line carrying
# both a date and the collection's own term of art -- "occurrence" -- is an
# occurrence record, and every such date must be cited in the row.
#
# Why not every date in the card: measured against the nine published cards,
# a full-haystack demand flags all nine, on dates that are demonstrably not
# occurrences -- screen dates, methodology pins, verification dates, and
# validation-genre OBSERVED entries (the gate card's own record distinguishes
# "the gate correctly rejected a candidate" from the failure it addresses
# occurring). Measured the same day: zero occurrence-marked uncited lines
# across the nine cards, so this rule passes the live tree and bites on the
# recording convention going forward -- freshness enforcement without
# red-flagging a healthy card. AGENTS.md step 1 stays the human half: record
# the occurrence where it happened; this is the check that the row then
# counts it.
#
# The plural matches too -- cross-review reproduced a record worded "two
# further occurrences" evading a singular-only pattern, and the plural is the
# natural phrasing when several land in one line. The lookbehind refuses
# hyphenated compounds: "co-occurrences" is a correlational-texture term one
# live card uses in a row that explicitly disclaims being occurrence
# evidence, and matching inside it would red-flag that healthy card.
OCCURRENCE_MARK: Final[re.Pattern[str]] = re.compile(
    r"(?<![\w-])occurrences?\b", re.IGNORECASE
)


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


def missing_files(card: Path) -> list[str]:
    return [name for name in REQUIRED_FILES if not (card / name).is_file()]


def corroborating_text(card: Path, *rows: str) -> str:
    """Everything the card records EXCEPT the given rows themselves.

    A count is only as good as what it points at. Checking the row's dates
    against the row's own text would pass any number a card cares to write
    beside any dates it cares to invent, which is the self-certifying shape
    this collection exists to refuse. So the row is cut out of the haystack
    first, and every date it states has to appear in what is left.

    WHERE THAT STOPS SHORT, stated because the gap is load-bearing: the
    haystack is every `*.md` in the card, EVIDENCE.md included, so a SIBLING
    ROW of the same record corroborates the count. Two published cards rest on
    exactly that -- parallel-review-disposition-schema's 2026-07-10 and
    subagent-research-reliability's 2026-07-12 are recorded in `Validated
    against` and `Observed in use`, not in gotchas.md or a case study -- and
    they are the two cards whose count carries them past the thin threshold.
    Narrowing the haystack to the card's OTHER files turns both red, so it is
    a recount rather than a refactor: AGENTS.md step 1 says record the
    occurrence where it happened, and moving those records is a call for
    whoever holds them.

    The dispatch row is excised alongside the occasions row (cross-review
    finding, 2026-08-24): every published card's dispatch row carries its
    measurement date and the delta-log inception date, so leaving it in the
    haystack auto-corroborates those two dates for any count a maintainer
    cares to write -- a sibling row is corroboration only when it records
    something, and the dispatch row's dates are boilerplate, not records.
    """
    parts = []
    for path in sorted(card.rglob("*.md")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for row in rows:
            if row:
                text = text.replace(row, "")
        parts.append(text)
    return "\n".join(parts)


def evidence_breaches(card: Path) -> list[str]:
    """Contract breaches in one card's EVIDENCE.md rows, in report order."""
    evidence = card / "EVIDENCE.md"
    if not evidence.is_file():
        # Already reported as a missing required file. Saying it twice in
        # different words would inflate the breach count over one defect.
        return []
    rows = scoreboard.evidence_fields(evidence, REQUIRED_EVIDENCE_ROWS)
    breaches = [
        f"EVIDENCE.md states no {name} row (an empty row is the same refusal: "
        "the card has not said)"
        for name in REQUIRED_EVIDENCE_ROWS
        if not rows.get(name, "").strip("* `")
    ]
    dispatch = rows.get(DISPATCH_ROW, "")
    if dispatch.strip("* `"):
        if not DISPATCH_OPEN_RE.match(dispatch):
            breaches.append(
                f"{DISPATCH_ROW} must open with a nonzero integer count or "
                f"the exact phrase 'No recorded dispatch': {dispatch[:60]!r}"
            )
        elif not DISPATCH_MEASURED_RE.search(dispatch):
            breaches.append(
                f"{DISPATCH_ROW} states no 'measured <date>' clause. A "
                "measured figure without its measurement date cannot be "
                "re-derived or judged stale"
            )

    occasions = rows.get(OCCASIONS_ROW, "")
    counted = COUNT_RE.match(occasions)
    if not counted:
        if occasions.strip("* `"):
            breaches.append(
                f"{OCCASIONS_ROW} does not open with an integer: {occasions[:60]!r}. "
                "A count that is not a number cannot be checked against anything"
            )
        return breaches

    count = int(counted.group(1))
    dates = DATE_RE.findall(occasions)
    # Not de-duplicated, and that is a choice with a cost: two occasions can
    # honestly fall on one date, so collapsing repeats would refuse a true
    # count -- but it also means a repeated date satisfies the arithmetic,
    # which is the fan-out inflation ADMISSION.md criterion 2 names. The
    # arithmetic cannot tell the two apart; only a reader can.
    if count != len(dates):
        breaches.append(
            f"{OCCASIONS_ROW} states {count} but cites {len(dates)} dated "
            f"reference(s): {', '.join(dates) or 'none'}"
        )
    haystack = corroborating_text(card, occasions, dispatch)
    uncorroborated = [d for d in dates if d not in haystack]
    if uncorroborated:
        breaches.append(
            f"{OCCASIONS_ROW} cites {', '.join(uncorroborated)}, which no other "
            "file in the card records. Record the occurrence where it happened, "
            "then count it"
        )

    # The reverse direction: the card checked against the row. Scope rule and
    # its measurement are at OCCURRENCE_MARK's definition.
    uncited: list[str] = []
    cited = set(dates)
    for line in haystack.splitlines():
        if OCCURRENCE_MARK.search(line):
            uncited.extend(
                d for d in DATE_RE.findall(line)
                if d not in cited and d not in uncited
            )
    if uncited:
        breaches.append(
            f"the card records dated occurrence(s) {', '.join(uncited)} that "
            f"{OCCASIONS_ROW} does not cite. Count the occurrence, or reword "
            "the record if it is not one"
        )

    labelled = THIN_LABEL in evidence.read_text(encoding="utf-8", errors="replace")
    if count < INDEPENDENT_OCCASIONS and not labelled:
        breaches.append(
            f"{count} counted occasion(s) is under {INDEPENDENT_OCCASIONS}, so "
            f"EVIDENCE.md must carry the {THIN_LABEL} label. ADMISSION.md "
            "criterion 2 asks for a failure that is not a one-off"
        )
    if count >= INDEPENDENT_OCCASIONS and labelled:
        breaches.append(
            f"{count} counted occasions, so the {THIN_LABEL} label is stale and "
            "must come off"
        )
    return breaches


def validate(root: Path) -> None:
    cards = find_cards(root)
    if not cards:
        print(
            f"REJECTED: no published cards found under {root}/skills. "
            "A run that checked nothing is not a pass.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    breaches = [
        # Bucket-qualified, not the bare directory name: two buckets may hold a
        # card of the same name, and "half-built: missing gotchas.md" twice over
        # names no file a maintainer can open.
        f"  - {card.relative_to(root).as_posix()}: {detail}"
        for card in cards
        for detail in [f"missing {name}" for name in missing_files(card)]
        + evidence_breaches(card)
    ]
    if breaches:
        for line in breaches:
            print(line, file=sys.stderr)
        print(
            f"REJECTED: {len(breaches)} card contract breach(es) across "
            f"{len(cards)} published card(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(
        f"PASS: {len(cards)} published card(s), all carry "
        + ", ".join(REQUIRED_FILES)
        + "; every EVIDENCE.md states "
        + " and ".join(REQUIRED_EVIDENCE_ROWS)
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
