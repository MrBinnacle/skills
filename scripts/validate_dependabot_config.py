#!/usr/bin/env python3
"""Validate `.github/dependabot.yml` against the #329 acceptance criteria.

Actions in this repository are pinned by full commit SHA. Without a Dependabot
config those pins never receive update PRs. #329 requires a config that covers
the github-actions ecosystem, runs weekly, and groups its updates. This script
is the check behind that sentence: it parses the shipped file and refuses
anything that does not carry all three properties, plus the structural
requirements GitHub's own schema enforces on every update entry.

WHAT COUNTS AS VALID
    version: 2
    at least one updates entry whose package-ecosystem is github-actions
    that entry's schedule.interval is weekly
    that entry's groups is a non-empty mapping whose values carry a
    non-empty patterns list
    every updates entry states a directory (GitHub requires it)

The parser is a stdlib subset reader for the Dependabot v2 shape this
repository ships -- mappings, nested mappings, and lists of mappings. It is
not a general YAML engine. Dependabot configs are shallow; anything outside
that shape is refused rather than guessed at.

Output is ASCII-only so a cp1252 console does not die on a status line,
matching the other validators in this directory.

Usage:
    python scripts/validate_dependabot_config.py
    python scripts/validate_dependabot_config.py --root DIR
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Final

CONFIG_REL: Final[Path] = Path(".github") / "dependabot.yml"

REQUIRED_ECOSYSTEM: Final[str] = "github-actions"
REQUIRED_INTERVAL: Final[str] = "weekly"
REQUIRED_VERSION: Final[int] = 2


def fail(msg: str) -> None:
    print(f"REJECTED: {msg}")
    raise SystemExit(1)


# --------------------------------------------------------------------------
# Minimal YAML subset parser for Dependabot v2.
# --------------------------------------------------------------------------


def _strip_comment(line: str) -> str:
    """Drop a trailing `#` comment. Quotes protect a literal hash."""
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            if index == 0 or line[index - 1] in " \t":
                return line[:index]
    return line


def _parse_scalar(raw: str) -> Any:
    text = raw.strip()
    if not text:
        return None
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    lowered = text.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "~"}:
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def _parse_value(raw: str) -> Any:
    """Parse a scalar, or an inline list like `[]` or `["*"]`."""
    text = raw.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        parts: list[str] = []
        current: list[str] = []
        in_single = False
        in_double = False
        for char in inner:
            if char == "'" and not in_double:
                in_single = not in_single
                current.append(char)
            elif char == '"' and not in_single:
                in_double = not in_double
                current.append(char)
            elif char == "," and not in_single and not in_double:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)
        parts.append("".join(current))
        return [_parse_scalar(part) for part in parts]
    return _parse_scalar(text)


def parse_dependabot_config(text: str) -> dict[str, Any]:
    """Parse the Dependabot v2 subset into nested dicts and lists.

    Raises ValueError on any shape outside the subset. Callers treat that as
    a refusal, not as a skip.
    """
    entries: list[tuple[int, str]] = []
    for lineno, original in enumerate(text.splitlines(), start=1):
        if not original.strip():
            continue
        if original.lstrip().startswith("#"):
            continue
        stripped = _strip_comment(original)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if "\t" in stripped[:indent]:
            raise ValueError(f"line {lineno}: tabs are not allowed for indentation")
        entries.append((indent, stripped.strip()))

    if not entries:
        raise ValueError("config is empty")

    def build(position: int, indent: int) -> tuple[Any, int]:
        if position >= len(entries):
            return None, position
        current_indent, content = entries[position]
        if current_indent != indent:
            raise ValueError(
                f"unexpected indent {current_indent} (expected {indent}) at {content!r}"
            )
        if content.startswith("- ") or content == "-":
            items: list[Any] = []
            while position < len(entries) and entries[position][0] == indent:
                _, item_content = entries[position]
                if not (item_content.startswith("- ") or item_content == "-"):
                    break
                remainder = item_content[1:].strip()
                if not remainder:
                    value, position = build(position + 1, indent + 2)
                    items.append(value)
                    continue
                if ":" in remainder:
                    key, _, raw = remainder.partition(":")
                    key = key.strip()
                    raw = raw.strip()
                    mapping: dict[str, Any] = {}
                    if raw:
                        mapping[key] = _parse_value(raw)
                        position += 1
                    else:
                        child, position = build(position + 1, indent + 2)
                        mapping[key] = child
                    # Continuation keys of the same list item sit at indent+2.
                    while position < len(entries) and entries[position][0] == indent + 2:
                        _, cont = entries[position]
                        if cont.startswith("- ") or cont == "-":
                            break
                        if ":" not in cont:
                            raise ValueError(f"expected key: value at {cont!r}")
                        ckey, _, craw = cont.partition(":")
                        ckey = ckey.strip()
                        craw = craw.strip()
                        if craw:
                            mapping[ckey] = _parse_value(craw)
                            position += 1
                        else:
                            child, position = build(position + 1, indent + 4)
                            mapping[ckey] = child
                    items.append(mapping)
                else:
                    items.append(_parse_value(remainder))
                    position += 1
            return items, position

        # Mapping at this indent.
        mapping: dict[str, Any] = {}
        while position < len(entries) and entries[position][0] == indent:
            _, content = entries[position]
            if content.startswith("- ") or content == "-":
                break
            if ":" not in content:
                raise ValueError(f"expected key: value at {content!r}")
            key, _, raw = content.partition(":")
            key = key.strip()
            raw = raw.strip()
            if raw:
                mapping[key] = _parse_value(raw)
                position += 1
            else:
                # Nested block: either a mapping or a list, at greater indent.
                if position + 1 >= len(entries) or entries[position + 1][0] <= indent:
                    mapping[key] = None
                    position += 1
                else:
                    child_indent = entries[position + 1][0]
                    child, position = build(position + 1, child_indent)
                    mapping[key] = child
        return mapping, position

    first_indent = entries[0][0]
    if first_indent != 0:
        raise ValueError(f"top-level content must start at indent 0, found {first_indent}")
    value, consumed = build(0, 0)
    if consumed != len(entries):
        _, leftover = entries[consumed]
        raise ValueError(f"unparsed content at {leftover!r}")
    if not isinstance(value, dict):
        raise ValueError("top-level value is not a mapping")
    return value


# --------------------------------------------------------------------------
# Structural checks against the #329 criteria.
# --------------------------------------------------------------------------


def _github_actions_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    updates = data.get("updates")
    if not isinstance(updates, list):
        return []
    return [
        entry
        for entry in updates
        if isinstance(entry, dict) and entry.get("package-ecosystem") == REQUIRED_ECOSYSTEM
    ]


def validate_config(data: dict[str, Any]) -> None:
    """Refuse any config that fails a #329 acceptance property. Never returns on failure."""
    version = data.get("version")
    if version != REQUIRED_VERSION and version != str(REQUIRED_VERSION):
        fail(
            f"version must be {REQUIRED_VERSION}, found {version!r}. Dependabot "
            "v2 is the only schema this repository's config uses."
        )

    updates = data.get("updates")
    if not isinstance(updates, list) or not updates:
        fail("updates must be a non-empty list of update entries")

    for entry in updates:
        if not isinstance(entry, dict):
            fail(f"updates entry {entry!r} is not a mapping")
        if not entry.get("directory"):
            fail(
                f"updates entry for {entry.get('package-ecosystem')!r} states no "
                "directory. GitHub requires a directory on every entry."
            )

    entries = _github_actions_entries(data)
    if not entries:
        ecosystems = [
            entry.get("package-ecosystem")
            for entry in updates
            if isinstance(entry, dict)
        ]
        fail(
            f"no updates entry covers the {REQUIRED_ECOSYSTEM} ecosystem; "
            f"found {ecosystems!r}. #329 requires github-actions coverage."
        )

    # Validate every github-actions entry, not only the first: a second
    # ungrouped entry would otherwise slip past a first-entry-only check.
    for entry in entries:
        schedule = entry.get("schedule")
        interval = None
        if isinstance(schedule, dict):
            interval = schedule.get("interval")
        if interval != REQUIRED_INTERVAL:
            fail(
                f"schedule.interval must be {REQUIRED_INTERVAL!r} for the "
                f"{REQUIRED_ECOSYSTEM} entry, found {interval!r}"
            )

        groups = entry.get("groups")
        if not isinstance(groups, dict) or not groups:
            fail(
                f"updates for {REQUIRED_ECOSYSTEM} must be grouped: groups is "
                f"{groups!r}. #329 requires grouped updates."
            )
        for name, spec in groups.items():
            if not isinstance(spec, dict):
                fail(f"group {name!r} is not a mapping")
            patterns = spec.get("patterns")
            if not isinstance(patterns, list) or not patterns:
                fail(
                    f"group {name!r} states no non-empty patterns list; "
                    f"patterns is {patterns!r}"
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository whose .github/dependabot.yml is checked",
    )
    args = parser.parse_args(argv)

    path = args.root / CONFIG_REL
    if not path.is_file():
        fail(f"no {CONFIG_REL.as_posix()} under {args.root}. #329 requires the file.")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        fail(f"could not read {path}: {error}")

    try:
        data = parse_dependabot_config(text)
    except ValueError as error:
        fail(f"{CONFIG_REL.as_posix()} is not a parseable Dependabot v2 config: {error}")

    validate_config(data)

    entries = _github_actions_entries(data)
    groups = entries[0].get("groups") if entries else {}
    group_names = sorted(groups) if isinstance(groups, dict) else []
    print(
        "PASS: dependabot config - github-actions ecosystem, weekly schedule, "
        f"updates grouped under {group_names!r}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
