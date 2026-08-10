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

SCOREBOARD_RE = re.compile(
    r"(\d+)\s+kept\b.*?(\d+)\s+retired\b.*?(\d+)\s+turned away\b",
    re.DOTALL,
)
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


def count_kept(root: Path) -> int:
    skills = root / "skills"
    if not skills.is_dir():
        fail(f"missing skills directory at {skills}")
    n = 0
    for bucket in sorted(skills.iterdir()):
        if not bucket.is_dir() or bucket.name.startswith("."):
            continue
        for skill in sorted(bucket.iterdir()):
            if skill.is_dir() and (skill / "SKILL.md").is_file():
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


def derive_counts(root: Path) -> tuple[int, int, int]:
    retired_md = root / "RETIRED.md"
    if not retired_md.is_file():
        fail(f"missing {retired_md}")
    text = retired_md.read_text(encoding="utf-8")
    kept = count_kept(root)
    retired = table_row_count(text, "## Retired from the collection")
    turned = table_row_count(text, "## Screened out at the gate")
    return kept, retired, turned


def extract_scoreboard(label: str, text: str) -> tuple[int, int, int]:
    m = SCOREBOARD_RE.search(text)
    if not m:
        fail(f"{label}: no scoreboard pattern (N kept, M retired, K turned away)")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def assert_site(label: str, text: str, expected: tuple[int, int, int]) -> None:
    found = extract_scoreboard(label, text)
    if found != expected:
        fail(
            f"{label}: scoreboard {found[0]} kept, {found[1]} retired, "
            f"{found[2]} turned away != derived {expected[0]} kept, "
            f"{expected[1]} retired, {expected[2]} turned away"
        )


def check_scoreboard_sites(root: Path, expected: tuple[int, int, int]) -> None:
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
    kept, retired, turned = expected
    print(
        f"PASS: scoreboard {kept} kept, {retired} retired, {turned} turned away; "
        f"admission policy version agrees"
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
