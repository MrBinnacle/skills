#!/usr/bin/env python3
"""Create a deterministic session packet scaffold from repository state."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def run_check(root: Path, check: dict) -> tuple[dict, str]:
    """Run one receiver check. Returns the manifest entry and the captured output."""
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result = subprocess.run(check["command"], cwd=root, shell=True, text=True, capture_output=True)
    entry = {
        "command": check["command"], "exit_code": result.returncode,
        "observed_at": observed_at, "head": git(root, "rev-parse", "HEAD")
    }
    return entry, (result.stdout + result.stderr)[-2000:]


def run_checks(root: Path, config: dict) -> tuple[list[dict], list[str]]:
    """Run every receiver check. Returns the manifest entries and the red ones' reports.

    A check the receiver will re-run and fail is known here, one session
    earlier than the receiver sees it, while the cause is still in context. So
    the producer refuses to write a packet after measuring a check red; a
    packet shipped in that state only moves the failure to the next session
    (skills#238).
    """
    entries: list[dict] = []
    reports: list[str] = []
    for check in config.get("receiver_checks", []):
        entry, output = run_check(root, check)
        entries.append(entry)
        if entry["exit_code"] != 0:
            reports.append(
                f"receiver check '{check.get('name', check['command'])}' exited "
                f"{entry['exit_code']}: {check['command']}\n{output}"
            )
    return entries, reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--next-action", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.repo_root.resolve()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    tests, red = run_checks(root, config)
    if red:
        print("refusing to write a packet: a receiver check is red", file=sys.stderr)
        for report in red:
            print(report, file=sys.stderr)
        return 1
    packet_dir = root / config["packet_dir"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    packet_id = str(uuid.uuid4())
    manifest = {
        "packet_version": "1", "packet_id": packet_id,
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "repository": {
            "root": str(root), "branch": git(root, "branch", "--show-current"),
            "head": git(root, "rev-parse", "HEAD"),
            "status_porcelain": git(root, "status", "--porcelain"),
        },
        "tests": tests,
        "skills_dispatched": {"source": "model-reported", "items": []},
        "objective": args.objective,
        "next_action": {"task": args.next_action, "purpose": args.purpose},
        "scope": {"include": [], "exclude": []},
        "blockers": [], "wake_conditions": config.get("wake_conditions", []),
        "failed_approaches": [], "claims": [], "references": [],
    }
    body = "\n".join([
        START := "<!-- SESSION-PACKET-V1",
        json.dumps(manifest, indent=2),
        "SESSION-PACKET-V1 -->",
        "", "## Narrative", "", "__REQUIRED__", "",
        "## Decisions", "", "__REQUIRED__", "",
        "## What We Tried", "", "__REQUIRED__", "",
        "## Resume Bootstrap", "", "__REQUIRED__", "",
    ])
    name = f"{now.strftime('%Y%m%dT%H%M%SZ')}-{packet_id[:8]}.md"
    path = packet_dir / name
    path.write_text(body, encoding="utf-8")
    print(path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
