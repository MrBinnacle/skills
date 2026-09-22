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
CASE_TYPES = frozenset({"should-fire", "should-not-fire"})


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


def as_list(value: object) -> list[object]:
    """Normalize a frontmatter scalar or sequence to a sequence."""
    return [value] if isinstance(value, str) else value if isinstance(value, list) else []


def target_skill(tags: list[object]) -> str | None:
    """Return the one card tag paired with the case type."""
    skills = [tag for tag in tags if isinstance(tag, str) and tag not in CASE_TYPES]
    return skills[0] if len(skills) == 1 else None


def is_plugin_root(path: Path) -> bool:
    """A case plugin path must resolve to a directory Claude can load."""
    return (path / ".claude-plugin" / "plugin.json").is_file() or (path / "plugin.json").is_file()


def check_directional_graders(
    case_dir: Path, tags: list[object], grader_frontmatters: list[dict]
) -> list[str]:
    """Require each case to observe its declared trigger direction."""
    breaches = []
    case_types = {tag for tag in tags if isinstance(tag, str) and tag in CASE_TYPES}
    skill = target_skill(tags)
    if len(case_types) != 1:
        breaches.append(f"{case_dir.name}: tags must name exactly one case type")
        return breaches
    if skill is None:
        breaches.append(f"{case_dir.name}: tags must name exactly one target skill")
        return breaches

    def invokes_skill(grader: dict) -> bool:
        return (
            grader.get("type") == "tool_used"
            and grader.get("tool") == "Skill"
            and skill in str(grader.get("input_match", ""))
        )

    if "should-fire" in case_types:
        if not any(grader.get("type") == "llm" for grader in grader_frontmatters):
            breaches.append(f"{case_dir.name}: should-fire case needs an llm outcome grader")
        if not any(invokes_skill(grader) for grader in grader_frontmatters):
            breaches.append(
                f"{case_dir.name}: should-fire case needs a Skill invocation grader for '{skill}'"
            )
    else:
        containment_grader = any(
            invokes_skill(grader)
            and grader.get("min") == 0
            and grader.get("max") == 0
            and grader.get("arm") == "both"
            for grader in grader_frontmatters
        )
        if not containment_grader:
            breaches.append(
                f"{case_dir.name}: should-not-fire case needs a both-arm Skill containment grader for '{skill}'"
            )
        if not any(grader.get("type") == "llm" for grader in grader_frontmatters):
            breaches.append(f"{case_dir.name}: should-not-fire case needs an llm outcome grader")
    return breaches


def check_case(case_dir: Path) -> list[str]:
    """Check a single case directory for structural correctness."""
    breaches = []
    prompt_file = case_dir / "prompt.md"
    fm = parse_frontmatter(prompt_file.read_text(encoding="utf-8"))

    for key in REQUIRED_PROMPT_KEYS:
        if key not in fm:
            breaches.append(f"{case_dir.name}: prompt.md missing frontmatter key '{key}'")

    tags = as_list(fm.get("tags", []))
    if not any(tag in CASE_TYPES for tag in tags):
        breaches.append(f"{case_dir.name}: tags must include 'should-fire' or 'should-not-fire'")

    plugins = as_list(fm.get("plugins", []))
    if not plugins:
        breaches.append(f"{case_dir.name}: no plugins path specified")
    for plugin in plugins:
        if not isinstance(plugin, str) or not plugin:
            breaches.append(f"{case_dir.name}: plugins entries must be non-empty relative paths")
        elif Path(plugin).is_absolute() or not is_plugin_root(case_dir / plugin):
            breaches.append(f"{case_dir.name}: plugin path '{plugin}' does not resolve to a plugin root")

    graders_dir = case_dir / GRADER_DIRS
    if not graders_dir.is_dir():
        breaches.append(f"{case_dir.name}: no {GRADER_DIRS}/ directory")
    else:
        grader_files = list(graders_dir.glob("*.md"))
        if not grader_files:
            breaches.append(f"{case_dir.name}: graders/ directory is empty")
        else:
            grader_frontmatters = [
                parse_frontmatter(path.read_text(encoding="utf-8")) for path in grader_files
            ]
            breaches.extend(check_directional_graders(case_dir, tags, grader_frontmatters))

    return breaches


def check_negative_controls(cases: list[Path]) -> list[str]:
    """Verify each should-fire case has a should-not-fire partner."""
    breaches = []
    fire_cases = []
    no_fire_cases = []

    for case in cases:
        fm = parse_frontmatter((case / "prompt.md").read_text(encoding="utf-8"))
        tags = as_list(fm.get("tags", []))
        if "should-fire" in tags:
            fire_cases.append(case)
        elif "should-not-fire" in tags:
            no_fire_cases.append(case)

    fire_skills = set()
    for case in fire_cases:
        fm = parse_frontmatter((case / "prompt.md").read_text(encoding="utf-8"))
        skill = target_skill(as_list(fm.get("tags", [])))
        if skill:
            fire_skills.add(skill)

    no_fire_skills = set()
    for case in no_fire_cases:
        fm = parse_frontmatter((case / "prompt.md").read_text(encoding="utf-8"))
        skill = target_skill(as_list(fm.get("tags", [])))
        if skill:
            no_fire_skills.add(skill)

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
