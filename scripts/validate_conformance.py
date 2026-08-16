#!/usr/bin/env python3
"""Run the standing obligations (`conformance v1`) against the published tree.

SECURITY.md declares six standing obligations a published card owes for as long
as it stays published. This script is the driver behind that section. It reports
PASS / FAIL / CANNOT-CHECK per card per obligation, and CANNOT-CHECK is a
distinct reported state -- never folded into PASS. An obligation the collection
cannot verify from inside itself is a visible count, because a green line that
quietly includes the unverifiable claims more than it measured.

Output is ASCII-only so the Windows CI cell does not die on cp1252 when printing
a status line, matching validate_scoreboard.py and validate_skill_formats.py.
Run with PYTHONUTF8=1.

WHERE THE OBLIGATIONS COME FROM
    From OBLIGATIONS below -- a structured list, not a prose scrape. The
    throwaway prototype this script is promoted from read its obligations by
    substring-matching the published sentences out of SECURITY.md, and that
    coupled the checker to the file's hard wrapping: one sentence spanning a
    newline turned two conforming cards red. The prose and the list are instead
    held together by a test (test_validate_conformance.py) asserting that the
    identifiers and the count here match the SECURITY.md section exactly, so
    drift is a red suite rather than a silent miscount.

WHAT IS DELEGATED, AND WHY
    O1's format vocabulary is validate_skill_formats.py's predicate, imported
    and called rather than restated -- one vocabulary, one place to widen it.
    O4's controlled-field names are validate_scoreboard.py's CONTROLLED_FIELDS
    for the same reason. O6 is validate_scoreboard.py's whole run.

SCOPE: CARD VS REPO
    Four obligations are properties of one card and are scored per card. Two
    (O1's walk and O6's scoreboard) are repo-wide predicates whose subject is
    the tree, and are evaluated ONCE and reported in their own block. Copying a
    single repo verdict into nine identical cells would multiply one finding by
    the card count and make the totals lie about how much was checked.

Usage:
    python scripts/validate_conformance.py
    python scripts/validate_conformance.py --root <tree> --markdown
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_scoreboard as scoreboard  # noqa: E402
import validate_skill_formats as formats  # noqa: E402

PASS: Final[str] = "PASS"
FAIL: Final[str] = "FAIL"
CANT: Final[str] = "CANNOT-CHECK"

CONFORMANCE_VERSION: Final[str] = "conformance v1"

# The SECURITY.md section states this date as the trial's pre-registered exit.
# It is asserted equal by the suite so the workflow header, the policy section
# and the checker cannot state three different dates.
TRIAL_EXIT_DATE: Final[str] = "2026-11-07"

CARD = "card"
REPO = "repo"


@dataclass(frozen=True)
class Obligation:
    oid: str
    title: str
    scope: str


# The list the checker is written against. Identifiers and count are asserted
# against the SECURITY.md "Standing obligations" section by the suite.
OBLIGATIONS: Final[tuple[Obligation, ...]] = (
    Obligation("O1", "declared formats only", REPO),
    Obligation("O2", "no fetch-and-execute", CARD),
    Obligation("O3", "shipped scripts named in SKILL.md", CARD),
    Obligation("O4", "EVIDENCE.md present with all controlled fields", CARD),
    Obligation("O5", "controlled fields do not contradict a published receipt", CARD),
    Obligation("O6", "scoreboard lockstep", REPO),
)

CARD_OBLIGATIONS: Final[tuple[Obligation, ...]] = tuple(
    o for o in OBLIGATIONS if o.scope == CARD
)
REPO_OBLIGATIONS: Final[tuple[Obligation, ...]] = tuple(
    o for o in OBLIGATIONS if o.scope == REPO
)


@dataclass(frozen=True)
class Result:
    verdict: str
    detail: str


@dataclass(frozen=True)
class Card:
    name: str
    folder: Path
    root: Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


EVIDENCE_ROW_RE: Final[re.Pattern[str]] = re.compile(
    r"^\|\s*\*\*(?P<field>[^*]+)\*\*\s*\|\s*(?P<value>.*?)\s*\|\s*$",
    re.MULTILINE,
)


def evidence_rows(path: Path) -> dict[str, str]:
    """Return the named rows from one evidence-contract table."""
    return {
        match.group("field").strip(): match.group("value").strip()
        for match in EVIDENCE_ROW_RE.finditer(read(path))
    }


def find_cards(root: Path) -> list[Card]:
    """Published cards: a SKILL.md two levels under skills/.

    Deliberately narrower than the format gate's repo-wide SKILL.md marker
    scan. The obligations are what a PUBLISHED card owes; the fixture trees
    under scripts/fixtures/ are inputs to other validators and owe nothing.
    """
    return [
        Card(p.parent.name, p.parent, root)
        for p in sorted((root / "skills").glob("*/*/SKILL.md"))
    ]


# ------------------------------------------------------------ card obligations


# Known download-and-run shapes. This catches command lines, not English: a card
# that tells the agent to fetch a page and follow what it says ships no pattern
# at all. PASS here means "no known shape present", and the report says so.
FETCH_EXEC: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"curl[^\n|]*\|\s*(ba)?sh", re.I),
    re.compile(r"wget[^\n|]*\|\s*(ba)?sh", re.I),
    re.compile(r"iwr[^\n|]*\|\s*iex", re.I),
    re.compile(r"invoke-webrequest[^\n|]*\|\s*(iex|invoke-expression)", re.I),
    re.compile(r"eval\s*\(\s*(requests|urllib|fetch)", re.I),
    re.compile(r"pip\s+install\s+(https?|git\+)", re.I),
)

READABLE_SUFFIXES: Final[tuple[str, ...]] = (".md", ".txt", ".py", ".json")


def check_fetch_execute(card: Card) -> Result:
    hits = []
    for path in sorted(card.folder.rglob("*")):
        if not path.is_file() or path.suffix not in READABLE_SUFFIXES:
            continue
        for pattern in FETCH_EXEC:
            for match in pattern.finditer(read(path)):
                hits.append(f"{path.name}: {match.group(0)[:60]}")
    if hits:
        return Result(FAIL, "; ".join(hits))
    return Result(PASS, "no known download-and-run shape in any shipped file")


TEST_PREFIX: Final[str] = "test_"


def check_scripts_named(card: Card) -> Result:
    """O3: a SKILL.md names every script it asks the agent to run.

    SECURITY.md commitment 3 carves out the shipped test suites, which CI runs
    and no skill invokes. The carve-out is read out of SECURITY.md's own
    sentence rather than hardcoded, so a tree that drops the sentence loses the
    exemption -- that is what makes this the obligation with a demonstrated
    rejection: at the PR #47 tree the naming sentence did not exist and the
    scripts did, and this check reports the contradiction.
    """
    scripts = sorted(
        p for p in card.folder.rglob("*.py") if "__pycache__" not in p.parts
    )
    if not scripts:
        return Result(PASS, "ships no script")
    security = " ".join(read(card.root / "SECURITY.md").split())
    if "names the scripts it asks the agent to run" not in security:
        return Result(
            FAIL,
            "the tree states no script-naming obligation yet this card ships "
            + ", ".join(p.name for p in scripts),
        )
    exempt = "also ship their test suites" in security and card.name in security
    skill_md = read(card.folder / "SKILL.md")
    unnamed = [p.name for p in scripts if p.name not in skill_md]
    if not unnamed:
        return Result(PASS, f"all {len(scripts)} script(s) named in SKILL.md")
    still = [n for n in unnamed if not (exempt and n.startswith(TEST_PREFIX))]
    if still:
        return Result(FAIL, "not named in SKILL.md: " + ", ".join(sorted(still)))
    return Result(
        PASS,
        f"{len(scripts) - len(unnamed)} named; test suite(s) covered by the "
        "SECURITY.md carve-out: " + ", ".join(sorted(unnamed)),
    )


def check_evidence_fields(card: Card) -> Result:
    """O4: EVIDENCE.md present, with every controlled field stated.

    The field names come from validate_scoreboard.CONTROLLED_FIELDS so the two
    validators cannot disagree about what a controlled field is. An empty row
    is the same refusal as an absent one: the card has not said.
    """
    evidence = card.folder / "EVIDENCE.md"
    if not evidence.exists():
        return Result(FAIL, "no EVIDENCE.md")
    values = scoreboard.evidence_fields(evidence, scoreboard.CONTROLLED_FIELDS)
    missing = [
        f for f in scoreboard.CONTROLLED_FIELDS if not values.get(f, "").strip("* `")
    ]
    if missing:
        return Result(FAIL, "no stated " + " and no stated ".join(missing))
    return Result(
        PASS,
        "EVIDENCE.md states " + ", ".join(scoreboard.CONTROLLED_FIELDS),
    )


def check_receipt_agreement(card: Card) -> Result:
    """O5: controlled fields must not contradict a published harness receipt.

    This repository cannot run it. The measurement sibling's evidence store is
    private and single-copy, so there is nothing here to compare a controlled
    field against. It is checked on the maintainer's clock and reported as
    CANNOT-CHECK, which is why CANNOT-CHECK exists as a state: promising this
    one as CI would be a green line for a check that never ran.
    """
    return Result(
        CANT,
        "no citable published receipt to compare against from inside this "
        "repository; maintainer-clock obligation",
    )


CARD_CHECKS = {
    "O2": check_fetch_execute,
    "O3": check_scripts_named,
    "O4": check_evidence_fields,
    "O5": check_receipt_agreement,
}


# ------------------------------------------------------------ repo obligations


def check_declared_formats(root: Path) -> Result:
    """O1, delegated to the format gate's own predicate rather than restated."""
    gate_script = root / "scripts" / "validate_skill_formats.py"
    if not gate_script.exists():
        return Result(CANT, "scripts/validate_skill_formats.py absent from this tree")
    folders = formats.find_skill_folders(root)
    if not folders:
        return Result(CANT, "no skill folders found under this root")
    files = formats.guarded_files(folders)
    skipped = formats.ignored_files(root, files)
    bad = []
    for path in files:
        if path in skipped:
            continue
        reason = formats.violation(root, path)
        if reason is not None:
            bad.append(reason)
    if bad:
        return Result(FAIL, f"{len(bad)} file(s): " + "; ".join(bad[:5]))
    return Result(
        PASS,
        f"{len(files) - len(skipped)} guarded file(s) across {len(folders)} "
        "skill folder(s), all declared formats",
    )


def check_scoreboard_lockstep(root: Path) -> Result:
    """O6, delegated: the scoreboard validator's whole run over this tree."""
    script = root / "scripts" / "validate_scoreboard.py"
    if not script.exists():
        return Result(CANT, "scripts/validate_scoreboard.py absent from this tree")
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    lines = (proc.stdout + proc.stderr).strip().splitlines()
    tail = lines[-1].strip() if lines else "(no output)"
    return Result(PASS if proc.returncode == 0 else FAIL, tail)


REPO_CHECKS = {
    "O1": check_declared_formats,
    "O6": check_scoreboard_lockstep,
}


# ------------------------------------------------------------------ evaluation


@dataclass(frozen=True)
class Report:
    cards: list[Card]
    per_card: dict[str, dict[str, Result]]
    repo_wide: dict[str, Result]

    def counts(self) -> dict[str, int]:
        totals = {PASS: 0, FAIL: 0, CANT: 0}
        for row in self.per_card.values():
            for result in row.values():
                totals[result.verdict] += 1
        for result in self.repo_wide.values():
            totals[result.verdict] += 1
        return totals


# An obligation with no registered check is a hole exactly where the design
# refuses one: it would be stated in the policy, counted nowhere, and silently
# absent from every report. Refused at import so it cannot reach a run.
_UNIMPLEMENTED = [
    o.oid
    for o in OBLIGATIONS
    if o.oid not in (CARD_CHECKS if o.scope == CARD else REPO_CHECKS)
]
if _UNIMPLEMENTED:
    raise SystemExit(
        "REJECTED: obligation(s) with no registered check: "
        + ", ".join(_UNIMPLEMENTED)
        + ". State it and check it, or do not state it."
    )


def evaluate(root: Path) -> Report:
    cards = find_cards(root)
    per_card = {
        card.name: {o.oid: CARD_CHECKS[o.oid](card) for o in CARD_OBLIGATIONS}
        for card in cards
    }
    repo_wide = {o.oid: REPO_CHECKS[o.oid](root) for o in REPO_OBLIGATIONS}
    return Report(cards, per_card, repo_wide)


def render(report: Report, markdown: bool) -> None:
    headers = [o.oid for o in CARD_OBLIGATIONS]
    if markdown:
        print("| Card | " + " | ".join(headers) + " |")
        print("|" + "---|" * (len(headers) + 1))
        for card in report.cards:
            row = report.per_card[card.name]
            print(
                f"| `{card.name}` | "
                + " | ".join(row[oid].verdict for oid in headers)
                + " |"
            )
    else:
        for card in report.cards:
            print(card.name)
            for obligation in CARD_OBLIGATIONS:
                result = report.per_card[card.name][obligation.oid]
                print(
                    f"  {result.verdict:<12} {obligation.oid} "
                    f"{obligation.title} -- {result.detail}"
                )
            print("")

    print("repo-wide obligations (evaluated once over the tree, not per card):")
    for obligation in REPO_OBLIGATIONS:
        result = report.repo_wide[obligation.oid]
        print(
            f"  {result.verdict:<12} {obligation.oid} {obligation.title} "
            f"-- {result.detail}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to check (default: this repository)",
    )
    parser.add_argument(
        "--markdown", action="store_true", help="emit the per-card table as markdown"
    )
    args = parser.parse_args()
    root = args.root.resolve()

    report = evaluate(root)
    if not report.cards:
        print(
            f"REJECTED: no published cards found under {root}/skills. A run that "
            "checked nothing is not a pass.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    render(report, args.markdown)
    totals = report.counts()
    cells = sum(totals.values())
    print("")
    summary = (
        f"{len(report.cards)} card(s) x {len(CARD_OBLIGATIONS)} card obligation(s) "
        f"+ {len(REPO_OBLIGATIONS)} repo obligation(s) = {cells} cells: "
        f"{totals[PASS]} PASS, {totals[FAIL]} FAIL, {totals[CANT]} {CANT}"
    )
    if totals[FAIL]:
        print(f"REJECTED: {CONFORMANCE_VERSION}: {summary}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"PASS: {CONFORMANCE_VERSION}: {summary}. {CANT} is not a pass -- "
        f"{totals[CANT]} cell(s) were not verified by this run."
    )


if __name__ == "__main__":
    main()
