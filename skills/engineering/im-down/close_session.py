#!/usr/bin/env python3
"""One public close action: write state, commit, then snapshot the packet.

Order is fixed in this process. Callers cannot reorder the stages. The state
commit moves HEAD; the packet then records that HEAD. Reversed, the packet
would record a pre-commit HEAD and the next open would reject it as stale.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=True,
    )
    return result.stdout.strip()


class CloseError(Exception):
    """Closeable failure with a JSON-serialisable payload."""

    def __init__(self, payload: dict):
        self.payload = payload
        super().__init__(payload.get("error", "close failed"))


def run_check(root: Path, check: dict) -> tuple[dict, str]:
    """Run one receiver check. Returns the manifest entry and the captured output."""
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result = subprocess.run(
        check["command"], cwd=root, shell=True, text=True, capture_output=True,
    )
    entry = {
        "command": check["command"],
        "exit_code": result.returncode,
        "observed_at": observed_at,
        "head": git(root, "rev-parse", "HEAD"),
    }
    return entry, (result.stdout + result.stderr)[-2000:]


def run_checks(root: Path, config: dict) -> list[dict]:
    """Run every receiver check; refuse the close when any is red.

    The receiver will re-run these and reject the packet on a red one. That
    is known here, one session earlier, while the cause is still in context,
    so no packet is written (skills#238). The close commit already made stays:
    it is durable state and is correct as written. Fix the cause and close
    again; the next close records a new HEAD.
    """
    entries: list[dict] = []
    red: list[dict] = []
    for check in config.get("receiver_checks", []):
        entry, output = run_check(root, check)
        entries.append(entry)
        if entry["exit_code"] != 0:
            red.append({
                "name": check.get("name", check["command"]),
                "command": check["command"],
                "exit_code": entry["exit_code"],
                "output": output,
            })
    if red:
        raise CloseError({
            "error": "refusing to write a packet: a receiver check is red",
            "failed_receiver_checks": red,
        })
    return entries


def write_state(root: Path, config: dict, objective: str, next_action: str,
                purpose: str) -> tuple[Path, str]:
    """Write durable state and commit it. Returns (state_path, post_commit_head)."""
    state_path_str = config.get("state_file")
    if not state_path_str:
        raise CloseError({"error": "config lacks state_file key"})

    state_path = Path(state_path_str)
    if not state_path.is_absolute():
        state_path = root / state_path

    head_before = git(root, "rev-parse", "HEAD")
    now = datetime.now(timezone.utc)
    state = {
        "session_boundary_state_version": "1",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "repository": {
            "root": str(root),
            "branch": git(root, "branch", "--show-current"),
            "head": head_before,
        },
        "objective": objective,
        "next_action": {"task": next_action, "purpose": purpose},
    }

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    if not state_path.is_file():
        raise CloseError({"error": "state file missing after write"})

    subprocess.run(
        ["git", "add", str(state_path)], cwd=root, check=True, capture_output=True,
    )
    close_commit = config.get("close_commit", {})
    marker = close_commit.get("contains", "SESSION-STATE:")
    commit_msg = f"chore(state): session close\n\n{marker} {now.isoformat()}"
    subprocess.run(
        ["git", "commit", "-m", commit_msg], cwd=root, check=True, capture_output=True,
    )

    head_after = git(root, "rev-parse", "HEAD")
    if head_after == head_before:
        raise CloseError({"error": "close commit did not move HEAD"})
    return state_path, head_after


def snapshot_packet(root: Path, config: dict, objective: str, next_action: str,
                    purpose: str, head: str) -> Path:
    """Write the packet scaffold at the post-commit HEAD already captured."""
    current_head = git(root, "rev-parse", "HEAD")
    if current_head != head:
        raise CloseError({
            "error": "HEAD moved between close commit and snapshot",
            "expected": head,
            "current": current_head,
        })
    tests = run_checks(root, config)
    packet_dir = root / config["packet_dir"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    packet_id = str(uuid.uuid4())
    manifest = {
        "packet_version": "1",
        "packet_id": packet_id,
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "repository": {
            "root": str(root),
            "branch": git(root, "branch", "--show-current"),
            "head": head,
            "status_porcelain": git(root, "status", "--porcelain"),
        },
        "tests": tests,
        "skills_dispatched": {"source": "model-reported", "items": []},
        "objective": objective,
        "next_action": {"task": next_action, "purpose": purpose},
        "scope": {"include": [], "exclude": []},
        "blockers": [],
        "wake_conditions": config.get("wake_conditions", []),
        "failed_approaches": [],
        "claims": [],
        "references": [],
    }
    body = "\n".join([
        "<!-- SESSION-PACKET-V1",
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
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Close a session: write state, commit, snapshot packet.",
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--objective", required=True)
    parser.add_argument("--next-action", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument(
        "--validate", action="store_true",
        help="Run produce-mode validation on the scaffold (markers still present).",
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    try:
        try:
            config = json.loads(args.config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CloseError({"error": f"config unreadable: {exc}"}) from exc
        if not isinstance(config, dict):
            raise CloseError({"error": "config must be a JSON object"})
        if "packet_dir" not in config:
            raise CloseError({"error": "config lacks packet_dir key"})

        # Stage 1–2: doctrine write + close commit (moves HEAD).
        state_path, head = write_state(
            root, config, args.objective, args.next_action, args.purpose,
        )
        # Stage 3: packet records the post-commit HEAD captured above.
        packet_path = snapshot_packet(
            root, config, args.objective, args.next_action, args.purpose, head,
        )

        result = {
            "state_path": str(state_path),
            "packet_path": str(packet_path),
            "head": head,
            "committed": True,
        }

        if args.validate:
            # Scaffold still carries __REQUIRED__ markers; produce mode will
            # reject them. --validate is for callers that filled the packet.
            proc = subprocess.run(
                [
                    sys.executable, str(HERE / "validate_packet.py"),
                    str(packet_path),
                    "--mode", "produce",
                    "--repo-root", str(root),
                    "--config", str(args.config.resolve()),
                ],
                text=True, capture_output=True,
            )
            result["validation_exit"] = proc.returncode
            try:
                result["validation"] = json.loads(proc.stdout)
            except json.JSONDecodeError:
                result["validation_stdout"] = proc.stdout
                result["validation_stderr"] = proc.stderr

        print(json.dumps(result, indent=2))
        return 0
    except CloseError as exc:
        print(json.dumps(exc.payload, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
