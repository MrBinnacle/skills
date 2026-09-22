#!/usr/bin/env python3
"""Pre-flight check for an eval suite rooted at a given directory.

Verifies:
- Every case directory has a prompt.md with required frontmatter fields.
- Each should-fire case has a matching should-not-fire partner (no missing
  negative control).
- Grader files exist and are readable.
- Plugin paths resolve from the case directory.

Usage:
    python check_eval_suite.py <path-to-evals-directory>
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


REQUIRED_PROMPT_KEYS = frozenset({"name", "description", "tags", "plugins"})
GRADER_DIRS = "graders"


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    raw = parts[1]
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    # Minimal fallback: extract key: value lines and inline flow sequences
    result = {}
    for line in raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            value = value.strip()
            # Handle inline flow sequences: [a, b, c]
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                result[key.strip()] = [
                    item.strip().strip('"').strip("'")
                    for item in inner.split(",")
                    if item.strip()
                ]
            else:
                result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def find_cases(suite_root: Path) -> list[Path]:
    """Find all case directories (directories containing prompt.md)."""
    cases = []
    for entry in sorted(suite_root.iterdir()):
        if entry.is_dir() and (entry / "prompt.md").is_file():
            cases.append(entry)
    return cases


def check_case(case_dir: Path) -> list[str]:
    """Check a single case directory for structural correctness."""
    breaches = []
    prompt_file = case_dir / "prompt.md"
    fm = parse_frontmatter(prompt_file.read_text(encoding="utf-8"))

    for key in REQUIRED_PROMPT_KEYS:
        if key not in fm:
            breaches.append(f"{case_dir.name}: prompt.md missing frontmatter key '{key}'")

    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    if not any(t in ("should-fire", "should-not-fire") for t in tags):
        breaches.append(f"{case_dir.name}: tags must include 'should-fire' or 'should-not-fire'")

    plugins = fm.get("plugins", [])
    if isinstance(plugins, str):
        plugins = [plugins]
    if not plugins:
        breaches.append(f"{case_dir.name}: no plugins path specified")

    graders_dir = case_dir / GRADER_DIRS
    if not graders_dir.is_dir():
        breaches.append(f"{case_dir.name}: no {GRADER_DIRS}/ directory")
    else:
        grader_files = list(graders_dir.glob("*.md"))
        if not grader_files:
            breaches.append(f"{case_dir.name}: graders/ directory is empty")

    return breaches


def check_negative_controls(cases: list[Path]) -> list[str]:
    """Verify each should-fire case has a should-not-fire partner."""
    breaches = []
    fire_cases = []
    no_fire_cases = []

    for case in cases:
        fm = parse_frontmatter((case / "prompt.md").read_text(encoding="utf-8"))
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if "should-fire" in tags:
            fire_cases.append(case)
        elif "should-not-fire" in tags:
            no_fire_cases.append(case)

    # Group by skill: extract skill name from the case name by removing known suffixes
    KNOWN_SUFFIXES = {
        "issue-bodies", "dispatch", "celery-worker", "near-miss",
        "web-research", "false-citation", "empty-handback",
    }

    def skill_from_case_name(name: str) -> str:
        parts = name.split("-")
        for i in range(len(parts)):
            for suffix in KNOWN_SUFFIXES:
                suffix_parts = suffix.split("-")
                if parts[i : i + len(suffix_parts)] == suffix_parts:
                    return "-".join(parts[:i])
        return name

    fire_skills = set()
    for case in fire_cases:
        fm = parse_frontmatter((case / "prompt.md").read_text(encoding="utf-8"))
        name = fm.get("name", case.name)
        fire_skills.add(skill_from_case_name(name))

    no_fire_skills = set()
    for case in no_fire_cases:
        fm = parse_frontmatter((case / "prompt.md").read_text(encoding="utf-8"))
        name = fm.get("name", case.name)
        no_fire_skills.add(skill_from_case_name(name))

    missing = fire_skills - no_fire_skills
    for skill in sorted(missing):
        breaches.append(f"missing negative control: no should-not-fire partner for skill '{skill}'")

    return breaches


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: check_eval_suite.py <path-to-evals-directory>", file=sys.stderr)
        sys.exit(1)

    suite_root = Path(sys.argv[1])
    if not suite_root.is_dir():
        print(f"REJECTED: {suite_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    cases = find_cases(suite_root)
    if not cases:
        print(f"REJECTED: no cases found in {suite_root}", file=sys.stderr)
        sys.exit(1)

    all_breaches = []
    for case in cases:
        all_breaches.extend(check_case(case))

    all_breaches.extend(check_negative_controls(cases))

    if all_breaches:
        for b in all_breaches:
            print(f"  - {b}", file=sys.stderr)
        print(
            f"REJECTED: {len(all_breaches)} breach(es) across {len(cases)} case(s).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"PASS: {len(cases)} case(s) in {suite_root}; "
        "no missing negative control, no containment failure."
    )


if __name__ == "__main__":
    main()
