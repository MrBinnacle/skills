#!/usr/bin/env python3
"""Verify each card's Standing cost row matches the skill-harness audit.

The ticket (MrBinnacle/skills#323) recorded a claim-integrity break: every
model-invocable card's EVIDENCE.md carried a hand-estimated description token
count, and every estimate disagreed with the calibrated figure from
`skill-harness skill audit`.  This script rechecks each card's figure.

Two paths:

  1. When `skill-harness` is installed, the script runs `skill-harness skill
     audit <SKILL.md>` and reads the calibrated standing cost from its output.

  2. When skill-harness is unavailable (typical in CI), the script reads the
     committed `standing-costs.json`, which carries the calibrated figure
     alongside a sha256 of the SKILL.md file.  If the hash has changed since
     the JSON was last written, the script reports staleness and fails.

In both cases the stated figure in EVIDENCE.md is compared against the
calibrated figure, and disagreement fails the check.

Output is ASCII-only, matching the other validators.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STANDING_COSTS_JSON = SCRIPT_DIR / "standing-costs.json"
STANDING_COST_ROW: str = "Standing cost"
# Pattern: "Description: N tokens, measured by ..."
# The N is the calibrated figure we verify.
CALIBRATED_RE = re.compile(r"Description:\s*(\d+)\s*tokens")
# The full audit line: "Standing cost (mechanical): raw N tokens · calibrated M tokens"
AUDIT_RE = re.compile(
    r"Standing cost \(mechanical\):.*?calibrated\s+(\d+)\s+tokens"
)


def iter_skill_dirs(root: Path) -> list[Path]:
    """Published skill directories: two levels under skills/, carrying SKILL.md."""
    skills = root / "skills"
    return sorted(
        d2
        for d in skills.iterdir()
        if d.is_dir() and not d.name.startswith(("."))
        for d2 in d.iterdir()
        if d2.is_dir() and (d2 / "SKILL.md").is_file()
    )


def extract_stated_tokens(evidence: Path) -> int | None:
    """Return the calibrated token count from the Standing cost row, or None."""
    fenced = False
    for line in evidence.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip("* ")
        if name == STANDING_COST_ROW:
            m = CALIBRATED_RE.search(cells[1])
            if m:
                return int(m.group(1))
            return None
    return None


def audit_calibrated(skill_md: Path) -> int | None:
    """Run skill-harness skill audit and extract the calibrated figure."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "skill_harness", "skill", "audit", str(skill_md)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    m = AUDIT_RE.search(result.stdout)
    if m:
        return int(m.group(1))
    # Fallback: try the CLI entrypoint
    try:
        result = subprocess.run(
            ["skill-harness", "skill", "audit", str(skill_md)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    m = AUDIT_RE.search(result.stdout)
    if m:
        return int(m.group(1))
    return None


def load_standing_costs() -> dict[str, dict]:
    """Load the committed standing-costs.json."""
    if not STANDING_COSTS_JSON.is_file():
        return {}
    return json.loads(STANDING_COSTS_JSON.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> None:
    cards = iter_skill_dirs(root)
    standing_costs = load_standing_costs()
    use_audit = shutil.which("skill-harness") is not None or _skill_harness_importable()

    blocking: list[str] = []

    for skill_dir in cards:
        card = skill_dir.name
        evidence = skill_dir / "EVIDENCE.md"
        skill_md = skill_dir / "SKILL.md"

        if not evidence.is_file():
            continue  # other gates catch missing files

        stated = extract_stated_tokens(evidence)
        if stated is None:
            # No calibrated figure in the row; other gates may enforce this
            continue

        if use_audit:
            calibrated = audit_calibrated(skill_md)
            if calibrated is None:
                blocking.append(
                    f"  - {card}: skill-harness audit failed to return a figure"
                )
                continue
            if stated != calibrated:
                blocking.append(
                    f"  - {card}: stated {stated} tokens, "
                    f"audit says {calibrated} tokens"
                )
        else:
            # Fallback: read standing-costs.json
            entry = standing_costs.get(card)
            if entry is None:
                blocking.append(
                    f"  - {card}: not found in standing-costs.json"
                )
                continue
            # Check freshness: SHA256 of SKILL.md must match the committed hash
            current_sha = file_sha256(skill_md)
            if current_sha != entry["skill_md_sha256"]:
                blocking.append(
                    f"  - {card}: SKILL.md has changed since standing-costs.json "
                    f"was written (expected sha256={entry['skill_md_sha256'][:16]}, "
                    f"got {current_sha[:16]}). Regenerate with: "
                    f"python scripts/refresh_standing_costs.py"
                )
                continue
            calibrated = entry["standing_cost_tokens"]
            if stated != calibrated:
                blocking.append(
                    f"  - {card}: stated {stated} tokens, "
                    f"standing-costs.json says {calibrated} tokens"
                )

    if blocking:
        for line in blocking:
            print(line, file=sys.stderr)
        print(
            f"REJECTED: {len(blocking)} standing-cost disagreement(s) across "
            f"{len(cards)} published card(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(
        f"PASS: {len(cards)} published card(s), all standing cost figures "
        f"match the audit"
        + (
            " (via standing-costs.json; skill-harness not available)"
            if not use_audit
            else ""
        )
    )


def _skill_harness_importable() -> bool:
    try:
        import skill_harness  # noqa: F401
        return True
    except ImportError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to validate (default: this repository)",
    )
    args = parser.parse_args()
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
