#!/usr/bin/env python3
"""Contract tests for the README admission lead and evidence census.

THE CENSUS IS DERIVED THROUGH THE EXISTING VALIDATORS, NOT RESTATED HERE.
    Postures come from `validate_scoreboard.evidence_fields` and its closed
    verdict vocabulary; the occasions integer comes from
    `validate_card_files`'s own row regex; the cards come from
    `validate_scoreboard.iter_skill_dirs`. A second parser in this file would be
    a second copy of the two rules that function documents -- skip fenced
    blocks, first occurrence wins -- and the two copies would disagree on
    exactly the records that document their own row format.

    That is not hypothetical. The restated version this replaced read an
    `UNMEASURED` field that merely mentions `SKILL.md` as a measured result, and
    a real `KEEP` verdict written without a trailing period as no result at all.
    It also read fenced example rows as the card's values, and it walked
    `in-progress/`, so parking unshipped work -- which AGENTS.md sanctions --
    demanded a front-page row for a card that was never admitted.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_card_files as card_files  # noqa: E402
import validate_scoreboard as scoreboard  # noqa: E402

ROOT = SCRIPT_DIR.parent
README = ROOT / "README.md"
ADMISSION = ROOT / "ADMISSION.md"
DISPOSITION = ROOT / "dispositions" / "2026-08-15-S295-admission-triage.md"

# The origin tier the README's `origin-trace` posture is keyed to. Checked
# against the scoreboard's closed vocabulary below, so renaming a tier fails
# here instead of silently re-bucketing every card.
ORIGIN_TRACE_TIER = "OBSERVED"
ORIGIN_ROW = "Origin"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def section(body: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", body
    )
    return match.group(1) if match else ""


def posture(rows: dict[str, str]) -> str:
    """One card's evidence posture, on the scoreboard's closed vocabulary.

    A verdict outside that vocabulary is reported as itself rather than bucketed:
    reading an unknown opening as a result would put a measurement on the front
    page that may never have happened, which is the direction that flatters the
    page.
    """
    for field in scoreboard.CONTROLLED_FIELDS:
        opening = rows.get(field, "").lstrip("* `_").upper()
        if opening.startswith(scoreboard.MEASURED_VERDICTS):
            return "measured"
        if not opening.startswith(scoreboard.UNMEASURED_VERDICTS):
            return f"unrecognised {field}: {rows.get(field, '')[:40]!r}"
    if rows.get(ORIGIN_ROW, "").upper().startswith(ORIGIN_TRACE_TIER):
        return "origin-trace"
    return "unmeasured"


def occasions(rows: dict[str, str]) -> int:
    """The integer that opens the card's occasions row, or -1 if it states none.

    -1 matches no README cell, so a row that does not open with a number fails
    the comparison instead of being silently skipped.
    """
    counted = card_files.COUNT_RE.match(rows.get(card_files.OCCASIONS_ROW, ""))
    return int(counted.group(1)) if counted else -1


def readme_table(body: str) -> dict[str, tuple[str, int]]:
    result: dict[str, tuple[str, int]] = {}
    for card, stated_posture, count in re.findall(
        r"^\| \[`([^`]+)`\]\([^\n]+/EVIDENCE\.md\) \| "
        r"(measured|origin-trace|unmeasured) \| (\d+) \|$",
        body,
        re.MULTILINE,
    ):
        result[card] = (stated_posture, int(count))
    return result


def case_admission_method_leads() -> None:
    body = README.read_text(encoding="utf-8")
    positions = [
        body.find("## Admission method"),
        body.find("## Card map"),
        body.find("## Card evidence"),
    ]
    check(
        "admission method, card map, and card evidence are the first three H2 sections",
        positions[0] >= 0
        and positions == sorted(positions)
        and re.findall(r"^## .+$", body[: positions[2]], re.MULTILINE)
        == ["## Admission method", "## Card map"],
        str(positions),
    )


def case_three_instruments_are_referenced() -> None:
    body = section(README.read_text(encoding="utf-8"), "Admission method")
    check("admission lead links ADMISSION.md", "[admission policy](ADMISSION.md)" in body)
    check(
        "admission lead names the policy, gate card, and screen",
        all(term in body for term in ("admission policy", "gate card", "screen")),
        body.strip(),
    )
    policy = ADMISSION.read_text(encoding="utf-8")
    table = re.search(r"(?ms)^\| Prefer \| Means \| Lives \|.*?(?=\n\n)", policy)
    check(
        "the three-instrument table remains intact",
        table is not None
        and table.group(0).count("\n|") == 4
        and all(term in table.group(0) for term in ("admission policy", "gate card", "screen")),
    )


def case_card_map_names_four_types() -> None:
    body = section(README.read_text(encoding="utf-8"), "Card map")
    check(
        "card map names trap, procedure, gate, and schema",
        all(re.search(rf"\b{kind}\b", body, re.IGNORECASE) for kind in ("trap", "procedure", "gate", "schema")),
        body.strip(),
    )


def case_evidence_table_projects_the_card_rows() -> None:
    table = readme_table(section(README.read_text(encoding="utf-8"), "Card evidence"))
    check(
        "the origin-trace posture is keyed to a tier the scoreboard recognises",
        ORIGIN_TRACE_TIER in scoreboard.ORIGIN_TIERS,
        f"{ORIGIN_TRACE_TIER} not in {scoreboard.ORIGIN_TIERS}",
    )
    wanted = scoreboard.CONTROLLED_FIELDS + (ORIGIN_ROW, card_files.OCCASIONS_ROW)
    expected: dict[str, tuple[str, int]] = {}
    # Published cards only, by the same walk the scoreboard's `N admitted` uses:
    # a row for an unshipped `in-progress/` card would claim an admission that
    # never happened.
    for card in scoreboard.iter_skill_dirs(ROOT):
        evidence = card / "EVIDENCE.md"
        if not evidence.is_file():
            expected[card.name] = ("no EVIDENCE.md", -1)
            continue
        rows = scoreboard.evidence_fields(evidence, wanted)
        expected[card.name] = (posture(rows), occasions(rows))
    check(
        "per-card table matches each EVIDENCE.md posture and occasion count",
        table == expected,
        f"expected {expected}; got {table}",
    )


def case_disposition_is_linked() -> None:
    body = README.read_text(encoding="utf-8")
    target = "dispositions/2026-08-15-S295-admission-triage.md"
    check("README links the S295 disposition record", f"]({target})" in body)
    check("the linked disposition record exists", DISPOSITION.is_file())


def case_public_copy_avoids_banned_vocabulary() -> None:
    body = README.read_text(encoding="utf-8")
    banned = re.findall(
        r"\b(?:earned|grandiose|grandiosity|perhaps|possibly|arguably)\b|readers may conclude",
        body,
        re.IGNORECASE,
    )
    check("README contains no banned vocabulary", not banned, str(sorted(set(banned))))


def main() -> None:
    case_admission_method_leads()
    case_three_instruments_are_referenced()
    case_card_map_names_four_types()
    case_evidence_table_projects_the_card_rows()
    case_disposition_is_linked()
    case_public_copy_avoids_banned_vocabulary()
    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: README admission lead matches the card ledger")


if __name__ == "__main__":
    main()
