#!/usr/bin/env python3
"""Suite for DESIGN.md enforcement-claim accuracy.

The file told readers to treat the token set as unenforced. It is enforced,
and has been since 2026-08-24. These tests pin the correction: the stale claim
must be gone, the truth must be present, and the two remaining open gaps must
be quoted from known_gaps as it now reads — including the real asset paths.

Each test reads the live DESIGN.md rather than a fixture, because the file is
the source of truth being verified. Gap paths are cross-checked against
assets/tokens.json so a renamed or invented path cannot green the suite.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGN = REPO_ROOT / "DESIGN.md"
TOKENS = REPO_ROOT / "assets" / "tokens.json"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def _design() -> str:
    return DESIGN.read_text(encoding="utf-8")


def _known_gaps() -> dict:
    return json.loads(TOKENS.read_text(encoding="utf-8"))["known_gaps"]


# --------------------------------------------------------------------------
# Criterion 1: stale passage removed
# --------------------------------------------------------------------------
def case_stale_enforcement_claim_removed() -> None:
    """The phrase 'Treat the token set as unenforced' must not appear."""
    text = _design()
    check(
        "stale enforcement claim removed",
        "Treat the token set as unenforced" not in text,
        "the phrase 'Treat the token set as unenforced' is still present",
    )


def case_stale_citation_removed() -> None:
    """The citation of known_gaps.not_enforced must not appear."""
    text = _design()
    check(
        "stale known_gaps.not_enforced citation removed",
        "known_gaps.not_enforced" not in text,
        "the citation of known_gaps.not_enforced is still present",
    )


def case_green_run_instruction_removed() -> None:
    """The instruction to discount a green CI run must not appear."""
    text = _design()
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
    text = _design()
    check(
        "validate_brand_kit.py named as enforcer",
        "validate_brand_kit.py" in text,
        "validate_brand_kit.py is not mentioned in DESIGN.md",
    )


def case_enforcement_described() -> None:
    """The file must state the token set IS enforced."""
    text = _design()
    lowered = text.lower()
    check(
        "enforcement positively stated",
        "the token set is enforced" in lowered or "token set is enforced" in lowered,
        "no statement that the token set is enforced found",
    )


def case_ci_gate_mentioned() -> None:
    """The file must state enforcement runs as a required status check."""
    text = _design()
    check(
        "CI gate mentioned",
        "required status check" in text.lower(),
        "no mention of enforcement as a required status check",
    )


# --------------------------------------------------------------------------
# Criterion 3: two remaining gaps quoted from known_gaps, real paths
# --------------------------------------------------------------------------
def case_social_preview_gap_mentioned() -> None:
    """The social preview raster gap must be stated with the live asset path."""
    text = _design()
    gaps = _known_gaps()
    assert "social_preview_raster_is_unreadable" in gaps
    check(
        "social preview raster gap stated",
        "assets/social-preview.png" in text
        and ("raster" in text.lower() or "social_preview_raster_is_unreadable" in text),
        "the social preview raster gap is not stated with assets/social-preview.png",
    )


def case_compact_mark_gap_mentioned() -> None:
    """The compact mark gap must name both lockups that known_gaps records."""
    text = _design()
    gaps = _known_gaps()
    gap_text = gaps["compact_mark_still_in_the_lockups"]
    # The two paths known_gaps itself names — inventing lockup-staged.svg must fail.
    required_paths = [
        p
        for p in ("assets/lockup-horizontal.svg", "assets/lockup-stacked.svg")
        if p in gap_text
    ]
    check(
        "compact mark gap paths match known_gaps",
        len(required_paths) == 2,
        "tokens.json known_gaps no longer names both lockup paths; re-read before pinning",
    )
    missing = [p for p in required_paths if p not in text]
    check(
        "compact mark gap stated with live lockup paths",
        not missing and ("compact mark" in text.lower() or "compact_mark_still_in_the_lockups" in text),
        f"DESIGN.md missing lockup path(s) recorded in known_gaps: {missing}",
    )


# --------------------------------------------------------------------------
# Criterion 4: adjacent statements preserved
# --------------------------------------------------------------------------
def case_currentcolor_rule_preserved() -> None:
    """The instruction to author new marks with currentColor must remain."""
    text = _design()
    check(
        "currentColor authoring rule preserved",
        "Author new marks with `currentColor`" in text or "Author new marks with currentColor" in text,
        "the currentColor authoring rule is missing",
    )


def case_img_fallback_preserved() -> None:
    """The warning about currentColor in <img> must remain."""
    text = _design()
    check(
        "img fallback warning preserved",
        "currentColor" in text and "<img" in text,
        "the warning about currentColor in img tags is missing",
    )


# --------------------------------------------------------------------------
# Criterion 5: open decisions updated
# --------------------------------------------------------------------------
def case_open_decisions_no_longer_stale() -> None:
    """The open decisions section must not reference the closed not_enforced gap."""
    text = _design()
    idx = text.find("## Open decisions")
    if idx == -1:
        check("open decisions section exists", False, "## Open decisions heading not found")
        return
    section = text[idx:]
    check(
        "open decisions section updated",
        "not_enforced" not in section and "two colour gaps" not in section.lower(),
        "the open decisions section still references the closed colour/enforcement gap",
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
        "PASS: DESIGN.md enforcement-claim accuracy verified; stale claims removed, "
        "truth stated, known_gaps paths quoted, adjacent rules preserved, and open "
        "decisions updated."
    )


if __name__ == "__main__":
    main()
