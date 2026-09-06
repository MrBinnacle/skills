#!/usr/bin/env python3
"""Validate this Agent Skills package without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ALLOWED_TOP_LEVEL = {"SKILL.md", "gotchas.md", "README.md", "references", "assets", "scripts", "evals"}


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["SKILL.md must start with YAML frontmatter"]
    marker = text.find("\n---\n", 4)
    if marker < 0:
        return {}, ["SKILL.md frontmatter has no closing marker"]

    values: dict[str, str] = {}
    for line in text[4:marker].splitlines():
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values, errors


def validate_links(root: Path, text: str) -> list[str]:
    errors: list[str] = []
    for target in LINK_PATTERN.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        relative = target.split("#", 1)[0]
        if relative and not (root / relative).is_file():
            errors.append(f"Broken SKILL.md reference: {target}")
    return errors


def validate_json(path: Path) -> list[str]:
    try:
        with path.open(encoding="utf-8") as source:
            json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        return [f"Invalid JSON in {path.relative_to(path.parents[1])}: {error}"]
    return []


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return ["SKILL.md is missing"]

    text = skill_path.read_text(encoding="utf-8")
    values, frontmatter_errors = frontmatter(text)
    errors.extend(frontmatter_errors)

    name = values.get("name", "")
    description = values.get("description", "")
    if not NAME_PATTERN.fullmatch(name):
        errors.append("name must use lowercase letters, numbers, and single hyphens")
    if root.name != name:
        errors.append(f"directory name {root.name!r} must match skill name {name!r}")
    if not description:
        errors.append("description is required")
    if len(description) > 1024:
        errors.append(f"description has {len(description)} characters; maximum is 1024")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md exceeds 500 lines")

    errors.extend(validate_links(root, text))

    for json_path in sorted((root / "evals").glob("*.json")):
        errors.extend(validate_json(json_path))

    unexpected = sorted(path.name for path in root.iterdir() if path.name not in ALLOWED_TOP_LEVEL)
    if unexpected:
        errors.append(f"unexpected top-level entries: {', '.join(unexpected)}")

    snapshot = root / "scripts" / "snapshot.py"
    if not snapshot.is_file():
        errors.append("scripts/snapshot.py is missing")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {root.name} package is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
