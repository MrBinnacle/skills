#!/usr/bin/env python3
"""Suite for DESIGN.md enforcement-claim accuracy.

The file told readers to treat the token set as unenforced. It is enforced,
and has been since 2026-08-24. These tests pin the correction: the stale claim
must be gone, the truth must be present, and the two remaining open gaps must
be quoted.

Each test reads the live DESIGN.md rather than a fixture, because the file is
the source of truth being verified.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGN = REPO_ROOT / "DESIGN.md"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


# --------------------------------------------------------------------------
# Criterion 1: stale passage removed
# --------------------------------------------------------------------------
def case_stale_enforcement_claim_removed() -> None:
    """The phrase 'Treat the token set as unenforced' must not appear."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "stale enforcement claim removed",
        "Treat the token set as unenforced" not in text,
        "the phrase 'Treat the token set as unenforced' is still present",
    )


def case_stale_citation_removed() -> None:
    """The citation of known_gaps.not_enforced at line 115 must not appear."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "stale known_gaps.not_enforced citation removed",
        "known_gaps.not_enforced" not in text,
        "the citation of known_gaps.not_enforced is still present",
    )


def case_green_run_instruction_removed() -> None:
    """The instruction to discount a green CI run must not appear."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "green-run discount instruction removed",
        "Read a green CI run as silence" not in text,
        "the instruction to read a green run as silence is still present",
    )


# --------------------------------------------------------------------------
# Criterion 2: truth stated
# --------------------------------------------------------------------------
def case_enforcement_named() -> None:
    """The file must name validate_brand_kit.py as the enforcer."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "validate_brand_kit.py named as enforcer",
        "validate_brand_kit.py" in text,
        "validate_brand_kit.py is not mentioned in DESIGN.md",
    )


def case_enforcement_described() -> None:
    """The file must state the token set IS enforced."""
    text = DESIGN.read_text(encoding="utf-8")
    lowered = text.lower()
    check(
        "enforcement positively stated",
        "is enforced" in lowered or "enforced by" in lowered,
        "no statement that the token set is enforced found",
    )


def case_ci_gate_mentioned() -> None:
    """The file must state enforcement runs in CI as a required check."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "CI gate mentioned",
        "required" in text.lower() and "check" in text.lower(),
        "no mention of enforcement as a required CI check",
    )


# --------------------------------------------------------------------------
# Criterion 3: two remaining gaps quoted
# --------------------------------------------------------------------------
def case_social_preview_gap_mentioned() -> None:
    """The social preview raster gap must be stated."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "social preview raster gap stated",
        "social_preview_raster_is_unreadable" in text
        or "social preview" in text.lower() and "raster" in text.lower(),
        "the social preview raster gap is not mentioned",
    )


def case_compact_mark_gap_mentioned() -> None:
    """The compact mark gap must be stated."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "compact mark gap stated",
        "compact_mark_still_in_the_lockups" in text
        or ("compact mark" in text.lower() and "lockup" in text.lower()),
        "the compact mark gap is not mentioned",
    )


# --------------------------------------------------------------------------
# Criterion 4: adjacent statements preserved
# --------------------------------------------------------------------------
def case_currentcolor_rule_preserved() -> None:
    """The instruction to author new marks with currentColor must remain."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "currentColor authoring rule preserved",
        "currentColor" in text,
        "the currentColor authoring rule is missing",
    )


def case_img_fallback_preserved() -> None:
    """The warning about currentColor in <img> must remain."""
    text = DESIGN.read_text(encoding="utf-8")
    check(
        "img fallback warning preserved",
        "<img" in text,
        "the warning about currentColor in img tags is missing",
    )


# --------------------------------------------------------------------------
# Criterion 5: open decisions updated
# --------------------------------------------------------------------------
def case_open_decisions_no_longer_stale() -> None:
    """The 'two colour gaps' open decision must not reference the closed enforcement gap."""
    text = DESIGN.read_text(encoding="utf-8")
    # Find the open decisions section and check its colour-gaps entry
    idx = text.find("## Open decisions")
    if idx == -1:
        check("open decisions section exists", False, "## Open decisions heading not found")
        return
    section = text[idx:]
    check(
        "open decisions section updated",
        "not_enforced" not in section,
        "the open decisions section still references the closed not_enforced gap",
    )


def main() -> None:
    case_stale_enforcement_claim_removed()
    case_stale_citation_removed()
    case_green_run_instruction_removed()
    case_enforcement_named()
    case_enforcement_described()
    case_ci_gate_mentioned()
    case_social_preview_gap_mentioned()
    case_compact_mark_gap_mentioned()
    case_currentcolor_rule_preserved()
    case_img_fallback_preserved()
    case_open_decisions_no_longer_stale()

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: DESIGN.md enforcement-claim accuracy verified across "
        f"{len(FAILURES) + 11} assertion(s); stale claims removed, truth stated, "
        "adjacent rules preserved, and open decisions updated."
    )


if __name__ == "__main__":
    main()
