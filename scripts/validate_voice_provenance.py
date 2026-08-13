#!/usr/bin/env python3
"""Refuse a voice specimen in BRAND.md that has no provenance.

BRAND.md's Voice section once derived the owner's voice by reading the shipped
front page. The front page opened with generated copy in his voice, so BRAND.md
promoted an assistant's sentence to the establishing example of how he writes,
and nothing in the loop was checkable because the only source was the page
itself. This script is the check behind the replacement rule: a voice specimen
is a line the owner wrote or ratified, cited to VERBATIM.md.

WHAT A SPECIMEN IS
    A markdown blockquote inside the `## Voice` section of BRAND.md. Blockquote
    syntax is the marker, so membership is syntactic rather than a guess about
    which italics are a quotation. Consecutive `>` lines are one specimen; a
    blank line ends it.

    Scope is the Voice section only, and that is deliberate rather than an
    oversight. Other sections quote the shipped surfaces on purpose -- what the
    repository CLAIMS is properly read off what it ships. Only the claim about
    how the owner WRITES cannot be sourced that way.

THE THREE ASSERTIONS
    1. Every specimen carries a citation.
    2. No citation names a shipped public surface as the origin.
    3. Every specimen appears in the record, as typed.

    (3) is not in the ticket's letter and is here on purpose. Without it a
    citation is an unchecked claim: a fabricated line with `VERBATIM.md` typed
    beside it passes (1) and (2) while violating the rule both exist to enforce.
    A check that verifies the CLAIM of provenance rather than provenance would
    reproduce this section's original defect one level up, and the fix's own
    documentation would certify a hole it had not closed.

WHAT THIS DELIBERATELY DOES NOT DO
    It makes no judgement about whether a line sounds like the owner. It cannot,
    and a check that pretended to would be worse than none -- it would launder a
    resemblance verdict as a mechanical result. Resemblance is a human or
    cross-model read against intent, not a string match.

ROUGHNESS IS THE PROVENANCE
    The record keeps typos, double spaces, missing apostrophes and trailing
    hedges. Assertion (3) compares text after joining wrapped lines with a single
    space and nothing else, so a quote may be re-wrapped to fit a paragraph but
    may not be smoothed. Deleting a double space or fixing an apostrophe turns
    the run red, which is the intended behaviour: those characters are the
    evidence that a human typed the line.

Output is ASCII-only so the Windows CI cell does not die on cp1252 when printing
a status line, matching validate_skill_formats.py and validate_scoreboard.py.

`main` currently has no branch protection and no required checks, so a nonzero
exit here is a signal, not a gate. Describe it as detecting violations, never as
preventing them.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final, NoReturn

# The record. Voice provenance resolves here and nowhere else.
RECORD_NAME: Final[str] = "VERBATIM.md"

# Shipped public surfaces. A voice specimen citing one of these is the exact
# defect this check exists to catch: the page becomes its own provenance.
# Widening this list is a reviewed change to the rule stated in BRAND.md, not a
# silent commit. It is a closed vocabulary rather than a per-line allowlist, so
# a new surface added to the repository is covered without anyone remembering.
SHIPPED_SURFACES: Final[frozenset[str]] = frozenset(
    {
        "README.md",
        "ADMISSION.md",
        "RETIRED.md",
        "EVIDENCE.md",
        "CONTEXT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "AGENTS.md",
        "CONTRIBUTING.md",
        "DESIGN.md",
        "BRAND.md",
    }
)

SECTION_HEADING: Final[str] = "## Voice"
MD_FILE: Final[re.Pattern[str]] = re.compile(r"([A-Za-z0-9_.-]+\.md)")


def fail(msg: str) -> NoReturn:
    # ASCII only: no em dash, curly quotes, or ellipsis.
    print(f"REJECTED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def voice_section(text: str) -> list[str]:
    """The lines of the `## Voice` section, exclusive of the next `## ` heading."""
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line.strip() == SECTION_HEADING:
            start = i + 1
            break
    if start is None:
        return []
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return lines[start:end]


def join_quote(block: list[str]) -> str:
    """Collapse a wrapped blockquote to one line, changing nothing else.

    Only the line join is normalised. Internal double spaces, typos and missing
    apostrophes survive, because they are the evidence the line was typed by a
    person rather than generated.
    """
    parts = []
    for line in block:
        stripped = line.lstrip()
        if stripped.startswith(">"):
            stripped = stripped[1:]
            if stripped.startswith(" "):
                stripped = stripped[1:]
        parts.append(stripped.rstrip())
    return " ".join(p for p in parts if p).strip()


def quote_blocks(lines: list[str]) -> list[tuple[int, str, list[str]]]:
    """Every blockquote in `lines` as (line number, joined text, raw block)."""
    blocks: list[tuple[int, str, list[str]]] = []
    current: list[str] = []
    start = 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith(">"):
            if not current:
                start = i
            current.append(line)
            continue
        if current:
            blocks.append((start, join_quote(current), list(current)))
            current = []
    if current:
        blocks.append((start, join_quote(current), list(current)))
    return blocks


def citation_after(lines: list[str], block_start: int, block_len: int) -> str | None:
    """The first non-blank line after a blockquote, if it cites a file.

    Returns None when the specimen is followed by a heading, another quote, or
    nothing -- all of which mean the specimen carries no citation.
    """
    for k in range(block_start + block_len, len(lines)):
        line = lines[k]
        if not line.strip():
            continue
        if line.startswith("#") or line.lstrip().startswith(">"):
            return None
        return line if MD_FILE.search(line) else None
    return None


def record_corpus(record_text: str) -> list[str]:
    """Every recorded line, joined the same way a specimen is."""
    return [text for _, text, _ in quote_blocks(record_text.split("\n")) if text]


def validate(root: Path) -> None:
    brand = root / "BRAND.md"
    record = root / RECORD_NAME
    for path in (brand, record):
        if not path.is_file():
            fail(f"missing {path.name} at {root}")

    lines = voice_section(brand.read_text(encoding="utf-8"))
    if not lines:
        fail(
            f"no '{SECTION_HEADING}' section in BRAND.md. A run that checks "
            f"nothing checks nothing; fix the heading rather than trusting green."
        )

    specimens = [b for b in quote_blocks(lines) if b[1]]
    if not specimens:
        fail(
            "no voice specimens found in the Voice section. This check guards "
            "specimens; zero of them means the section stopped quoting the "
            "record, not that it is clean."
        )

    corpus = record_corpus(record.read_text(encoding="utf-8"))
    if not corpus:
        fail(f"{RECORD_NAME} holds no recorded lines; nothing can be cited to it")

    problems: list[str] = []
    for start, text, block in specimens:
        excerpt = text if len(text) <= 60 else text[:57] + "..."
        citation = citation_after(lines, start, len(block))

        if citation is None:
            problems.append(
                f'voice specimen "{excerpt}" carries no citation. Every specimen '
                f"cites {RECORD_NAME}, or is removed."
            )
            continue

        named = set(MD_FILE.findall(citation))
        shipped = sorted(named & SHIPPED_SURFACES)
        if shipped:
            problems.append(
                f'voice specimen "{excerpt}" cites a shipped public surface '
                f"({', '.join(shipped)}). A shipped surface cannot supply "
                f"provenance; the page would be its own source."
            )
            continue
        if RECORD_NAME not in named:
            problems.append(
                f'voice specimen "{excerpt}" cites {sorted(named)}, not '
                f"{RECORD_NAME}. Voice provenance resolves to the record only."
            )
            continue

        if not any(text in recorded for recorded in corpus):
            problems.append(
                f'voice specimen "{excerpt}" is not in {RECORD_NAME} as typed. '
                f"Either it was never recorded, or it was smoothed to fit -- "
                f"the record keeps roughness on purpose, so change the sentence "
                f"around the quote rather than the quote."
            )

    if problems:
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        fail(
            f"{len(problems)} voice specimen problem(s) in BRAND.md. Voice comes "
            f"from {RECORD_NAME}; a shipped surface cannot supply provenance."
        )

    print(
        f"PASS: {len(specimens)} voice specimen(s), all cited to {RECORD_NAME} "
        f"and present in the record as typed"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Check BRAND.md voice provenance.")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="tree containing BRAND.md and the record (default: repository root)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parent.parent
    validate(root)


if __name__ == "__main__":
    main()
