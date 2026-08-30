#!/usr/bin/env python3
"""Refuse a voice specimen that has no provenance in VERBATIM.md.

BRAND.md's Voice section once derived the owner's voice by reading the shipped
front page. The front page opened with generated copy in his voice, so BRAND.md
promoted an assistant's sentence to the establishing example of how he writes,
and nothing in the loop was checkable because the only source was the page
itself. This script is the check behind the replacement rule: a voice specimen
is a line the owner wrote or ratified, cited to VERBATIM.md.

THE FORM A SPECIMEN MUST TAKE (BRAND.md Voice section)
    A markdown blockquote inside the `## Voice` section, followed by a line
    beginning `Source:`.

    An inline quotation -- `*"..."*` or any double-quoted span in that section --
    is REJECTED rather than checked. That is deliberate and it is the whole
    point: inline italics are the shape the original defect had. Every specimen
    this check replaced was written `*"..."*` with the front page named in the
    surrounding prose, so a blockquote-only check would pass the very file it
    exists to have caught. Prose in this section that needs to name a phrase
    should restructure or use single quotes.

    Scope of the citation check is the Voice section only. Other BRAND.md
    sections quote the shipped surfaces on purpose -- what the repository
    CLAIMS is properly read off what it ships. Only the claim about how the
    owner WRITES cannot be sourced that way.

FIRST-PERSON LINES ON SCANNED SURFACES
    README.md (and any further path in FIRST_PERSON_SURFACES) is scanned for
    first-person lines. Every such line must equal a recorded VERBATIM.md line
    exactly. The surface list is data: adding a surface is a data edit.

THE ASSERTIONS
    1. Every specimen is followed by an explicit `Source:` line.
       Not "a nearby line that mentions a .md file" -- incidental prose that
       happens to name the record must not discharge a citation requirement.
    2. That source names VERBATIM.md, and does not name a shipped public surface
       INSTEAD of it. Naming one alongside the record is fine: saying where else
       a line appears is not a provenance claim.
    3. The quoted text EQUALS a recorded line, exactly.
    4. The section and date in the citation are where that line actually sits.

    (3) is equality, not containment. Containment lets a specimen be any fragment
    of a recorded line, so selective truncation that inverts a sentence passes
    while the check certifies it as verbatim -- and a one-word specimen passes
    too. Equality also makes the comparison direction unmutable: a reversed
    containment test is a different check that a containment-based suite cannot
    distinguish. Quote a recorded line whole, or record the shorter line.

    (4) exists because a citation that carries a section name and a date is
    making a specific, checkable-looking claim to the reader. Leaving those two
    fields unverified publishes precision the check does not have.

    (1) through (4) together are what stop a citation from being an unchecked
    claim. A check that verified the CLAIM of provenance rather than provenance
    would reproduce this section's original defect one level up.

WHAT THIS DELIBERATELY DOES NOT DO
    It makes no judgement about whether a line sounds like the owner. It cannot,
    and a check that pretended to would be worse than none -- it would launder a
    resemblance verdict as a mechanical result. Resemblance is a human or
    cross-model read against intent, not a string match.

ROUGHNESS IS THE PROVENANCE
    The record keeps typos, double spaces, missing apostrophes and trailing
    hedges. Comparison joins wrapped lines with a single space and changes
    nothing else, so a quote may be re-wrapped to fit a paragraph but may not be
    smoothed. Deleting a double space or fixing an apostrophe turns the run red,
    which is intended: those characters are the evidence a human typed the line.

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
from typing import Final, NamedTuple, NoReturn

RECORD_NAME: Final[str] = "VERBATIM.md"

# Where the record keeps evidence. Blockquotes elsewhere in that file are
# illustration -- its "Why this file exists" section describes the fabricated
# front-page sentence, and quoting it there to show what was removed is the
# natural edit. Without this restriction that counter-example becomes citable as
# the owner's voice, which inverts the file.
RECORD_SECTION: Final[str] = "## The lines"

# Shipped public surfaces. Naming one INSTEAD of the record is the defect this
# check exists to catch. The list only sharpens the error message: assertion 2
# already requires the record by name, so an unlisted surface is refused anyway.
# It is not a security boundary and does not need to be exhaustive.
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
CITATION_PREFIX: Final[str] = "Source:"

# Surfaces to scan for first-person lines that must be recorded. This is a
# data-driven list: adding a surface is a data edit, not a code change.
FIRST_PERSON_SURFACES: Final[list[tuple[str, str]]] = [
    ("README.md", "first-person sentence"),
]

# The subject pronoun "I" as it appears in English prose, including the "I"
# inside I'm / I've / I'd / I'll. A verb whitelist is refused on purpose -- it
# would let an unlisted construction ("I believe", "I encountered") onto a
# public surface without a record. Coverage is the subject pronoun only: a line
# carrying "my", "me" or "mine" with no "I" is not scanned (widening to those
# forms is a separate change, because every line they match needs a record
# first). The unit is a source line, and only fenced code is stripped; an inline
# code span is scanned as prose. Case-sensitive.
FIRST_PERSON_RE: Final[re.Pattern[str]] = re.compile(r"\bI\b")
FENCE: Final[re.Pattern[str]] = re.compile(r"^\s*(```|~~~)")
MD_FILE: Final[re.Pattern[str]] = re.compile(r"([A-Za-z0-9_.-]+\.md)")
DATE: Final[re.Pattern[str]] = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
CITED_SECTION: Final[re.Pattern[str]] = re.compile(r"\*([^*]+)\*")
# Straight and curly double quotes. Built with chr() so this source file cannot
# itself contain the characters -- the repository's own guard refuses non-ASCII
# punctuation in a .py, and retyping the escape is not a fix.
QUOTE_CHARS: Final[str] = '"' + chr(0x201C) + chr(0x201D)
INLINE_QUOTE: Final[re.Pattern[str]] = re.compile(
    "[" + QUOTE_CHARS + "]([^" + QUOTE_CHARS + "]{2,})[" + QUOTE_CHARS + "]"
)


class Recorded(NamedTuple):
    text: str
    heading: str


def fail(msg: str) -> NoReturn:
    # ASCII only: no em dash, curly quotes, or ellipsis.
    print(f"REJECTED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def strip_fences(lines: list[str]) -> list[str]:
    """Blank out fenced code blocks, preserving line numbering.

    BRAND.md documents its own rules, so a fence in the Voice section showing a
    rejected specimen is a likely edit. Without this the illustration is read as
    a real specimen and the build goes red naming a line that does not exist.
    """
    out: list[str] = []
    inside = False
    for line in lines:
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return out


def section_lines(text: str, heading: str) -> list[str]:
    """Lines under `heading`, ending at the next heading of the same level or higher.

    Ending only at `## ` would let a later `# Appendix` be scanned as part of
    this section.
    """
    lines = text.split("\n")
    depth = len(heading) - len(heading.lstrip("#"))
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start is None:
        return []
    end = len(lines)
    for j in range(start, len(lines)):
        stripped = lines[j]
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if level <= depth and stripped[level : level + 1] == " ":
                end = j
                break
    return lines[start:end]


def join_quote(block: list[str]) -> str:
    """Collapse a wrapped blockquote to one line, changing nothing else."""
    parts = []
    for line in block:
        stripped = line.lstrip()
        if stripped.startswith(">"):
            stripped = stripped[1:]
            if stripped.startswith(" "):
                stripped = stripped[1:]
        parts.append(stripped.rstrip())
    return " ".join(p for p in parts if p).strip()


def quote_blocks(lines: list[str]) -> list[tuple[int, str, int]]:
    """Every blockquote as (start index, joined text, line count)."""
    blocks: list[tuple[int, str, int]] = []
    current: list[str] = []
    start = 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith(">"):
            if not current:
                start = i
            current.append(line)
            continue
        if current:
            blocks.append((start, join_quote(current), len(current)))
            current = []
    if current:
        blocks.append((start, join_quote(current), len(current)))
    return blocks


def citation_after(lines: list[str], start: int, length: int) -> str | None:
    """The `Source:` line following a blockquote, if there is one."""
    for k in range(start + length, len(lines)):
        line = lines[k]
        if not line.strip():
            continue
        if line.startswith("#") or line.lstrip().startswith(">"):
            return None
        return line if line.lstrip().startswith(CITATION_PREFIX) else None
    return None


def record_corpus(record_text: str) -> list[Recorded]:
    """Every recorded line under `## The lines`, with the heading it sits under."""
    lines = strip_fences(section_lines(record_text, RECORD_SECTION))
    headings: list[tuple[int, str]] = [
        (i, line.strip()) for i, line in enumerate(lines) if line.startswith("### ")
    ]
    corpus: list[Recorded] = []
    for start, text, _ in quote_blocks(lines):
        if not text:
            continue
        heading = ""
        for index, value in headings:
            if index < start:
                heading = value
            else:
                break
        corpus.append(Recorded(text, heading))
    return corpus


def excerpt(text: str) -> str:
    return text if len(text) <= 60 else text[:57] + "..."


def first_person_sentences(text: str) -> list[str]:
    """First-person sentences in text, after stripping fenced code blocks."""
    return [
        line.strip()
        for line in strip_fences(text.split("\n"))
        if FIRST_PERSON_RE.search(line)
    ]


def check_surface(
    root: Path,
    surface_path: str,
    corpus_by_text: dict[str, Recorded],
    problems: list[str],
) -> None:
    """Check that every first-person sentence on a surface is recorded."""
    path = root / surface_path
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    for sentence in first_person_sentences(text):
        if sentence not in corpus_by_text:
            problems.append(
                f'first-person sentence on {surface_path} is not recorded in '
                f"{RECORD_NAME}: \"{excerpt(sentence)}\". Every first-person "
                f"sentence on a public surface must be recorded in "
                f"{RECORD_NAME} with provenance."
            )


def validate(root: Path) -> None:
    brand = root / "BRAND.md"
    record = root / RECORD_NAME
    for path in (brand, record):
        if not path.is_file():
            fail(f"missing {path.name} at {root}")

    lines = strip_fences(section_lines(brand.read_text(encoding="utf-8"), SECTION_HEADING))
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
        fail(
            f"{RECORD_NAME} holds no recorded lines under '{RECORD_SECTION}'; "
            f"nothing can be cited to it"
        )
    by_text = {item.text: item for item in corpus}

    problems: list[str] = []

    # An inline quotation is the shape the original defect had. Refuse it rather
    # than try to check it -- a specimen is a blockquote with a Source line.
    quote_line_numbers = {
        index for start, _, length in specimens for index in range(start, start + length)
    }
    for i, line in enumerate(lines):
        if i in quote_line_numbers or line.lstrip().startswith(CITATION_PREFIX):
            continue
        for match in INLINE_QUOTE.finditer(line):
            problems.append(
                f'inline quotation "{excerpt(match.group(1))}" in the Voice '
                f"section. A voice specimen is a blockquote followed by a "
                f"{CITATION_PREFIX} line; inline italics are the form the "
                f"unsourced specimens took, so they are refused rather than "
                f"checked."
            )

    for start, text, length in specimens:
        shown = excerpt(text)
        citation = citation_after(lines, start, length)

        if citation is None:
            problems.append(
                f'voice specimen "{shown}" has no {CITATION_PREFIX} line. Every '
                f"specimen is followed by one naming {RECORD_NAME}, or is removed."
            )
            continue

        named = set(MD_FILE.findall(citation))
        if RECORD_NAME not in named:
            shipped = sorted(named & SHIPPED_SURFACES)
            if shipped:
                problems.append(
                    f'voice specimen "{shown}" cites a shipped public surface '
                    f"({', '.join(shipped)}) and not {RECORD_NAME}. A shipped "
                    f"surface cannot supply provenance; the page would be its "
                    f"own source."
                )
            else:
                problems.append(
                    f'voice specimen "{shown}" cites {sorted(named) or "no file"}, '
                    f"not {RECORD_NAME}. Voice provenance resolves to the record."
                )
            continue

        recorded = by_text.get(text)
        if recorded is None:
            problems.append(
                f'voice specimen "{shown}" is not a recorded line in '
                f"{RECORD_NAME}. It must match one exactly -- either it was "
                f"never recorded, or it was smoothed or truncated to fit. The "
                f"record keeps roughness on purpose, so change the sentence "
                f"around the quote rather than the quote."
            )
            continue

        cited_sections = [s.strip() for s in CITED_SECTION.findall(citation)]
        for name in cited_sections:
            if name and name.lower() not in recorded.heading.lower():
                problems.append(
                    f'voice specimen "{shown}" is cited to section "{name}", but '
                    f'the record files it under "{recorded.heading}".'
                )
        cited_dates = set(DATE.findall(citation))
        recorded_dates = set(DATE.findall(recorded.heading))
        if cited_dates and recorded_dates and not (cited_dates & recorded_dates):
            problems.append(
                f'voice specimen "{shown}" is cited to '
                f"{', '.join(sorted(cited_dates))}, but the record dates it "
                f"{', '.join(sorted(recorded_dates))}."
            )

    # Check surfaces for first-person sentences that must be recorded.
    for surface_name, _label in FIRST_PERSON_SURFACES:
        check_surface(root, surface_name, by_text, problems)

    if problems:
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        fail(
            f"{len(problems)} voice specimen problem(s). Voice comes from "
            f"{RECORD_NAME}; a shipped surface cannot supply provenance."
        )

    print(
        f"PASS: {len(specimens)} voice specimen(s), each equal to a recorded line "
        f"in {RECORD_NAME} and cited to the section and date that holds it"
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
