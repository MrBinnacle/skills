"""Finish the CHANGELOG.md section that `changeset version` just wrote (#330).

What it does
    `changeset version` inserts the new release section directly under the
    `# Changelog` title, as a bare `## X.Y.Z` heading. That puts it above the
    preamble that states the release model (ADR 0002), and leaves it undated,
    which release gate G4 refuses. This step fixes both:

    - the heading becomes `## vX.Y.Z - YYYY-MM-DD`;
    - the preamble moves back above the new section.

    Everything after the preamble is left byte-for-byte as it was. Line
    endings follow the title line, so a CRLF file stays CRLF.

    The new section runs from its heading to the first line that starts at
    column 0 and is not blank, a `#` heading, or a `- ` bullet. Changesets
    indents every later line of a bullet, so that line is the first line of
    the preamble. The preamble runs to the next `## ` heading.

    A file whose first section is already dated for this version is left
    alone, so the step is safe to run twice. Any other first section is an
    error: the file is not in a shape this step understands.

Run
    npm run version                       # changeset version, then this
    python scripts/finish_changelog.py    # this step alone
    python scripts/finish_changelog.py --date 2026-10-20

Exit status: 0 when the file was finished or already was; 1 when its first
section is neither `## <version>` nor a dated heading for that version.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_REL = "CHANGELOG.md"


def _is_blank(line: str) -> bool:
    return not line.strip()


def _starts_preamble(line: str) -> bool:
    return not _is_blank(line) and not line[0].isspace() and not line.startswith(("#", "- "))


def _trim_blank_tail(lines: list[str]) -> list[str]:
    end = len(lines)
    while end and _is_blank(lines[end - 1]):
        end -= 1
    return lines[:end]


def finish_changelog(text: str, version: str, date: str) -> str:
    """Date the newest section and put the preamble back above it."""
    lines = text.splitlines(keepends=True)
    heading_at = next((i for i, line in enumerate(lines) if line.startswith("## ")), None)
    if heading_at is None:
        raise ValueError(f"{CHANGELOG_REL} has no '## ' section heading")
    heading = lines[heading_at].rstrip("\r\n")
    if re.fullmatch(rf"## v{re.escape(version)} - \d{{4}}-\d{{2}}-\d{{2}}", heading):
        return text
    if heading != f"## {version}":
        raise ValueError(
            f"{CHANGELOG_REL} first section is {heading!r}; expected '## {version}' "
            f"from changeset version, or an already dated '## v{version} - <date>'"
        )

    newline = "\r\n" if lines[0].endswith("\r\n") else "\n"
    section_end = next(
        (
            i
            for i in range(heading_at + 1, len(lines))
            if _starts_preamble(lines[i]) or lines[i].startswith("## ")
        ),
        len(lines),
    )
    preamble_end = next(
        (i for i in range(section_end, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    body = _trim_blank_tail(lines[heading_at + 1 : section_end])
    if body and not body[-1].endswith("\n"):
        body[-1] += newline
    preamble = _trim_blank_tail(lines[section_end:preamble_end])
    rest = lines[preamble_end:]

    out = lines[:heading_at]
    if preamble:
        out += preamble + [newline]
    out += [f"## v{version} - {date}{newline}"] + body
    if rest:
        out += [newline] + rest
    return "".join(out)


def _parse_date(value: str) -> str:
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a YYYY-MM-DD date: {value!r}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument(
        "--date",
        type=_parse_date,
        default=datetime.date.today().isoformat(),
        help="release date for the heading (default: today)",
    )
    args = parser.parse_args(argv)

    version = json.loads((args.root / "package.json").read_text(encoding="utf-8"))["version"]
    path = args.root / CHANGELOG_REL
    with path.open(encoding="utf-8", newline="") as handle:
        text = handle.read()
    try:
        finished = finish_changelog(text, version, args.date)
    except ValueError as exc:
        print(f"finish_changelog: {exc}", file=sys.stderr)
        return 1
    if finished == text:
        print(f"{CHANGELOG_REL}: section for {version} is already dated; nothing to do")
        return 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(finished)
    print(f"{CHANGELOG_REL}: dated the {version} section {args.date} and kept the preamble on top")
    return 0


if __name__ == "__main__":
    sys.exit(main())
