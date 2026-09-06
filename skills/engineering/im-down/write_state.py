#!/usr/bin/env python3
"""Write durable session state and commit it before the packet is produced.

This is the state-write half of the close ritual. It writes a JSON state file
with the session's objective, next action, timestamp, and repository facts, then
commits it with the close_commit marker so that validate_packet.py can confirm
the close happened before the packet recorded HEAD.

The ordering is structural, not procedural: this script commits (moving HEAD),
and only then does snapshot_state.py record HEAD into the packet. Reversed, the
packet records a HEAD the close then moves, and the receiver rejects the packet
as stale at the next session.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write durable session state and commit it.",
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--objective", required=True)
    parser.add_argument("--next-action", required=True)
    parser.add_argument("--purpose", required=True)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    config = json.loads(args.config.read_text(encoding="utf-8"))

    state_path_str = config.get("state_file")
    if not state_path_str:
        print(json.dumps({"error": "config lacks state_file key"}))
        return 1

    state_path = Path(state_path_str)
    if not state_path.is_absolute():
        state_path = root / state_path

    now = datetime.now(timezone.utc)
    state = {
        "session_boundary_state_version": "1",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "repository": {
            "root": str(root),
            "branch": git(root, "branch", "--show-current"),
            "head": git(root, "rev-parse", "HEAD"),
        },
        "objective": args.objective,
        "next_action": {
            "task": args.next_action,
            "purpose": args.purpose,
        },
    }

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    subprocess.run(["git", "add", str(state_path)], cwd=root, check=True)

    close_commit = config.get("close_commit", {})
    marker = close_commit.get("contains", "SESSION-STATE:")
    commit_msg = f"chore(state): session close\n\n{marker} {now.isoformat()}"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=root, check=True)

    print(json.dumps({
        "state_path": str(state_path),
        "head": git(root, "rev-parse", "HEAD"),
        "committed": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
