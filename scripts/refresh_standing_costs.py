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
PINNED_HARNESS_VERSION = "0.3.0"
VERSION_RE = re.compile(r"version\s+(\d+\.\d+\.\d+)")
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


def installed_harness() -> list[str]:
    for command in ([sys.executable, "-m", "skill_harness"], ["skill-harness"]):
        try:
            result = subprocess.run(
                [*command, "--version"], capture_output=True, text=True, timeout=30
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
        m = VERSION_RE.search(result.stdout)
        if result.returncode == 0 and m:
            if m.group(1) != PINNED_HARNESS_VERSION:
                raise RuntimeError(
                    "expected pinned skill-harness "
                    f"{PINNED_HARNESS_VERSION}, found {m.group(1)}"
                )
            return command
    raise RuntimeError("skill-harness is not installed")


def audit_calibrated(command: list[str], skill_md: Path) -> int:
    try:
        result = subprocess.run(
            [*command, "skill", "audit", str(skill_md)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    else:
        m = AUDIT_RE.search(result.stdout)
        if result.returncode == 0 and m:
            return int(m.group(1))
    raise RuntimeError(f"skill-harness audit failed for {skill_md}")


def refresh(root: Path) -> None:
    cards = iter_skill_dirs(root)
    data = {}
    command = installed_harness()
    for skill_dir in cards:
        card = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        # CRLF folded to LF: the checker hashes the same way, so a Windows
        # checkout and a Linux checkout of one file share one hash.
        sha = hashlib.sha256(
            skill_md.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        tokens = audit_calibrated(command, skill_md)
        data[card] = {
            "standing_cost_tokens": tokens,
            "skill_md_sha256": sha,
        }
        print(f"  {card}: {tokens} tokens")

    out = root / "scripts" / "standing-costs.json"
    snapshot = {
        "skill_harness_version": PINNED_HARNESS_VERSION,
        "calibrated_on": "2026-09-22",
        "cards": data,
    }
    out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8", newline="")
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
