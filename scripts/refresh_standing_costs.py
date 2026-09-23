#!/usr/bin/env python3
"""Regenerate scripts/standing-costs.json from the live skill-harness audit.

Run this after editing any SKILL.md frontmatter (name or description) to keep
the freshness hashes in sync.  Requires `skill-harness` to be installed.

Usage:
    python scripts/refresh_standing_costs.py [--root <repo-root>]

The script writes `scripts/standing-costs.json` (relative to --root).  Commit
the result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STANDING_COSTS_JSON = SCRIPT_DIR / "standing-costs.json"
AUDIT_RE = re.compile(
    r"Standing cost \(mechanical\):.*?calibrated\s+(\d+)\s+tokens"
)


def iter_skill_dirs(root: Path) -> list[Path]:
    skills = root / "skills"
    return sorted(
        d2
        for d in skills.iterdir()
        if d.is_dir() and not d.name.startswith(("."))
        for d2 in d.iterdir()
        if d2.is_dir() and (d2 / "SKILL.md").is_file()
    )


def audit_calibrated(skill_md: Path) -> int:
    for cmd in [
        [sys.executable, "-m", "skill_harness", "skill", "audit", str(skill_md)],
        ["skill-harness", "skill", "audit", str(skill_md)],
    ]:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
        if result.returncode == 0:
            m = AUDIT_RE.search(result.stdout)
            if m:
                return int(m.group(1))
    raise RuntimeError(f"skill-harness audit failed for {skill_md}")


def refresh(root: Path) -> None:
    cards = iter_skill_dirs(root)
    data = {}
    for skill_dir in cards:
        card = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        sha = hashlib.sha256(skill_md.read_bytes()).hexdigest()
        tokens = audit_calibrated(skill_md)
        data[card] = {
            "standing_cost_tokens": tokens,
            "skill_md_sha256": sha,
        }
        print(f"  {card}: {tokens} tokens")

    out = root / "scripts" / "standing-costs.json"
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to refresh (default: this repository)",
    )
    args = parser.parse_args()
    refresh(args.root.resolve())


if __name__ == "__main__":
    main()
