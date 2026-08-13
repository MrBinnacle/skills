#!/usr/bin/env python3
"""Assert front-page scoreboard numbers match the repository, and that the
gate card's normative-status version matches ADMISSION.md.

A test, not a generator: banners and the README alt stay hand-edited; this
script only refuses drift. Output is ASCII-only so the Windows CI cell does
not die on cp1252 when printing a status line.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NoReturn

# The words are ruled and the separator is not: the five sites use commas or
# middots as each already did, so the pattern skips whatever sits between the
# fields. `solutions looking for a problem` is matched in full on purpose --
# the judgement in that phrase is deliberate, and a pattern that accepted a
# softened restatement would let the softening ship.
SCOREBOARD_RE = re.compile(
    r"(\d+)\s+admitted\b.*?"
    r"(\d+)\s+measured\b.*?"
    r"(\d+)\s+retired\b.*?"
    r"(\d+)\s+solutions looking for a problem",
    re.DOTALL,
)
FIELD_NAMES = ("admitted", "measured", "retired", "solutions looking for a problem")
CONTROLLED_FIELDS = ("Screen result", "Paired verdict")
POLICY_VERSION_RE = re.compile(r"admission-policy\s+v\d+")
DECLARED_VERSION_RE = re.compile(
    r"\*\*Declared version:\*\*\s*`?(admission-policy\s+v\d+)`?"
)
GATE_HEADER_VERSION_RE = re.compile(
    r"Normative status\..*?\((`?)(admission-policy\s+v\d+)\1\)",
    re.DOTALL | re.IGNORECASE,
)


def fail(msg: str) -> NoReturn:
    # ASCII only: no em dash, curly quotes, or middle dots.
    # NoReturn is not decoration: it tells a type checker that every `m.group()`
    # after a `if not m: fail(...)` is reachable only when m is not None, which is
    # what makes the guard clauses below type-safe without redundant asserts.
    print(f"REJECTED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def iter_skill_dirs(root: Path) -> list[Path]:
    skills = root / "skills"
    if not skills.is_dir():
        fail(f"missing skills directory at {skills}")
    found = []
    for bucket in sorted(skills.iterdir()):
        if not bucket.is_dir() or bucket.name.startswith("."):
            continue
        for skill in sorted(bucket.iterdir()):
            if skill.is_dir() and (skill / "SKILL.md").is_file():
                found.append(skill)
    return found


def count_admitted(root: Path) -> int:
    return len(iter_skill_dirs(root))


def controlled_field_values(evidence: Path) -> dict[str, str]:
    """Return the card's two controlled-field values, keyed by field name.

    Reads the `| **Field** | Value |` rows of the evidence table. Both fields
    must be present: a card that states neither has not been measured *and has
    not said so*, which is a different thing, and the difference is the whole
    point of the record.
    """
    values: dict[str, str] = {}
    for line in evidence.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip("* ")
        if name in CONTROLLED_FIELDS:
            values[name] = cells[1]
    return values


def count_measured(root: Path) -> int:
    """Count cards carrying a controlled result, read from their own records.

    A card counts as measured when either controlled field states something
    other than UNMEASURED. The test is on the START of the value because the
    verdict is the first thing the field says; prose further along may discuss
    an earlier UNMEASURED run without the field itself being one.

    A missing record, or a record missing a controlled field, is refused rather
    than counted as zero. Deriving `0 measured` from an absent record would be
    inventing the number this line exists to keep honest.
    """
    n = 0
    for skill in iter_skill_dirs(root):
        evidence = skill / "EVIDENCE.md"
        if not evidence.is_file():
            fail(
                f"{skill.name}: no EVIDENCE.md, so the measured count cannot be "
                f"derived. The front page states how many cards carry a controlled "
                f"result; a card with no record cannot answer that either way, and "
                f"counting it as unmeasured would invent the answer."
            )
        values = controlled_field_values(evidence)
        # An absent row and a present-but-empty one are the same refusal: the
        # card has not said. Only the blank case is worth calling out separately,
        # because "not UNMEASURED" would otherwise read a blank as a result and
        # silently inflate the count in the direction that flatters the page.
        missing = [f for f in CONTROLLED_FIELDS if not values.get(f, "").strip("* `")]
        if missing:
            fail(
                f"{skill.name}: EVIDENCE.md has no stated {' and no stated '.join(missing)}, "
                f"so the measured count cannot be derived from it. An empty controlled "
                f"field is not a result."
            )
        if any(
            not values[f].lstrip("* `").upper().startswith("UNMEASURED")
            for f in CONTROLLED_FIELDS
        ):
            n += 1
    return n


def table_row_count(text: str, heading_prefix: str) -> int:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith(heading_prefix):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("|"):
            j += 1
        if j >= len(lines):
            fail(f"no table under heading starting {heading_prefix!r}")
        # header row
        j += 1
        if j < len(lines) and re.match(r"^\|[\s|:-]+$", lines[j]):
            j += 1
        count = 0
        while j < len(lines) and lines[j].startswith("|"):
            count += 1
            j += 1
        return count
    fail(f"heading not found: {heading_prefix!r}")


def derive_counts(root: Path) -> tuple[int, int, int, int]:
    retired_md = root / "RETIRED.md"
    if not retired_md.is_file():
        fail(f"missing {retired_md}")
    text = retired_md.read_text(encoding="utf-8")
    admitted = count_admitted(root)
    measured = count_measured(root)
    retired = table_row_count(text, "## Retired from the collection")
    turned = table_row_count(text, "## Screened out at the gate")
    return admitted, measured, retired, turned


def extract_scoreboard(label: str, text: str) -> tuple[int, int, int, int]:
    m = SCOREBOARD_RE.search(text)
    if not m:
        fail(
            f"{label}: no scoreboard pattern (N admitted, M measured, K retired, "
            f"J solutions looking for a problem). The words are ruled; only the "
            f"separator is free."
        )
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))


# Where each number comes from, named in the failure so a reader is told which
# artifact to go and look at rather than which line to go and edit.
DERIVED_FROM = (
    "the skill folders",
    "the cards' controlled fields",
    "RETIRED.md",
    "RETIRED.md",
)


def assert_site(label: str, text: str, expected: tuple[int, int, int, int]) -> None:
    found = extract_scoreboard(label, text)
    if found == expected:
        return
    disagreements = [
        f"{name} {got} != {want} derived from {source}"
        for name, got, want, source in zip(FIELD_NAMES, found, expected, DERIVED_FROM)
        if got != want
    ]
    fail(f"{label}: scoreboard disagrees with the repository - " + "; ".join(disagreements))


def check_scoreboard_sites(root: Path, expected: tuple[int, int, int, int]) -> None:
    sites = [
        ("assets/banner-light.svg aria-label", root / "assets" / "banner-light.svg", True),
        ("assets/banner-light.svg text", root / "assets" / "banner-light.svg", False),
        ("assets/banner-dark.svg aria-label", root / "assets" / "banner-dark.svg", True),
        ("assets/banner-dark.svg text", root / "assets" / "banner-dark.svg", False),
        ("README.md img alt", root / "README.md", False),
    ]
    for label, path, aria_only in sites:
        if not path.is_file():
            fail(f"{label}: missing file {path}")
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".svg" and aria_only:
            m = re.search(r'aria-label="([^"]*)"', text)
            if not m:
                fail(f"{label}: no aria-label")
            assert_site(label, m.group(1), expected)
        elif path.suffix == ".svg":
            # Rendered text element(s), not the aria-label.
            texts = re.findall(r"<text\b[^>]*>(.*?)</text>", text, flags=re.DOTALL)
            if len(texts) < 2:
                fail(f"{label}: expected a scoreboard <text> element")
            assert_site(label, texts[-1], expected)
        elif path.name == "README.md":
            m = re.search(r'<img\b[^>]*\balt="([^"]*)"', text)
            if not m:
                fail(f"{label}: no img alt on banner")
            assert_site(label, m.group(1), expected)
        else:
            assert_site(label, text, expected)


def policy_version(root: Path) -> str:
    """Return the ONE authoritative version declared in ADMISSION.md.

    Two properties are asserted here, and both are load-bearing:

      1. The canonical declaration EXISTS. There is deliberately no fallback to
         "any version string in the file". A fallback makes the check pass after
         the canonical line is deleted, which is a silent downgrade to a weaker
         guarantee than the one this function claims to provide.
      2. It is the ONLY occurrence. The governing decision on this was that
         fewer declaration sites beat a smarter checker: with one site, a partial
         bump cannot be expressed, so it cannot be missed. Restating the string
         elsewhere in the file re-creates exactly the drift this guards against.

    Tradeoff, stated because it is real: this refuses a legitimate quotation of a
    historical version inside ADMISSION.md (a migration example, or "what v1 used
    to say"). That failure is loud and self-explaining rather than silent, and the
    fix is to reference the declaration instead of restating the string.
    """
    path = root / "ADMISSION.md"
    if not path.is_file():
        fail(f"missing {path}")
    text = path.read_text(encoding="utf-8")
    m = DECLARED_VERSION_RE.search(text)
    if not m:
        fail(
            "ADMISSION.md: no canonical '**Declared version:** `admission-policy vN`' "
            "line. That line is the single authoritative declaration; without it "
            "there is nothing for the gate card to agree with."
        )
    declared = m.group(1)
    occurrences = POLICY_VERSION_RE.findall(text)
    if len(occurrences) != 1:
        fail(
            f"ADMISSION.md: expected exactly 1 admission-policy version string, "
            f"found {len(occurrences)} ({', '.join(sorted(set(occurrences)))}). "
            f"Keep one canonical declaration and reference it in prose elsewhere "
            f"rather than restating the version, so a partial bump cannot happen."
        )
    return declared


def gate_card_version(root: Path) -> str:
    path = root / "skills" / "meta" / "skill-necessity-gate" / "SKILL.md"
    if not path.is_file():
        fail(f"missing gate card at {path}")
    text = path.read_text(encoding="utf-8")
    # The normative-status header is the only place the card may pin the policy
    # version. No fallback to "any version string on the card": that would let a
    # passing mention in body prose stand in for the header, so deleting the
    # header would silently keep the check green.
    m = GATE_HEADER_VERSION_RE.search(text)
    if not m:
        fail(
            "gate card SKILL.md: no admission-policy version in the normative-status "
            "header. The header is where the card pins the policy edition it "
            "describes; a mention elsewhere on the card is not a substitute."
        )
    return m.group(2)


def check_policy_version(root: Path) -> None:
    declared = policy_version(root)
    on_card = gate_card_version(root)
    if declared != on_card:
        fail(
            f"admission policy version drift: ADMISSION.md has {declared!r}, "
            f"gate card header has {on_card!r}"
        )


def validate(root: Path) -> None:
    expected = derive_counts(root)
    check_scoreboard_sites(root, expected)
    check_policy_version(root)
    admitted, measured, retired, turned = expected
    print(
        f"PASS: scoreboard {admitted} admitted, {measured} measured, {retired} retired, "
        f"{turned} solutions looking for a problem; admission policy version agrees"
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
