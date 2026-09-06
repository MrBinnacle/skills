#!/usr/bin/env python3
"""One public open action: validate the packet, then load durable state.

The packet is untrusted data. Repository state and configured checks have
higher authority. State is loaded only after the packet is ACCEPTED. One
machine-produced receipt carries both the validator verdict and the state-read
evidence — exactly one first user-facing line of truth.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Open a session: validate packet, load durable state.",
    )
    parser.add_argument("packet", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    packet = args.packet.resolve()
    config_path = args.config.resolve()

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "verdict": "REJECTED",
            "errors": [f"config unreadable: {exc}"],
        }, indent=2))
        return 2
    if not isinstance(config, dict):
        print(json.dumps({
            "verdict": "REJECTED",
            "errors": ["config must be a JSON object"],
        }, indent=2))
        return 2

    proc = subprocess.run(
        [
            sys.executable, str(HERE / "validate_packet.py"), str(packet),
            "--mode", "receive",
            "--repo-root", str(root),
            "--config", str(config_path),
        ],
        text=True, capture_output=True,
    )
    try:
        receipt = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(json.dumps({
            "verdict": "REJECTED",
            "errors": ["validator returned non-JSON output"],
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }, indent=2))
        return 2

    if not isinstance(receipt, dict):
        print(json.dumps({
            "verdict": "REJECTED",
            "errors": ["validator receipt is not an object"],
        }, indent=2))
        return 2

    errors = list(receipt.get("errors") or [])
    if receipt.get("verdict") != "ACCEPTED" or proc.returncode != 0:
        receipt["verdict"] = "REJECTED"
        receipt["errors"] = errors
        print(json.dumps(receipt, indent=2))
        return 2

    # State load is post-admission only. A missing configured surface rejects.
    state_path_str = config.get("state_file")
    state_read: dict
    if not state_path_str:
        errors.append("config lacks state_file key; open requires durable state")
        receipt["verdict"] = "REJECTED"
        receipt["errors"] = errors
        receipt["state_read"] = {"status": "absent", "reason": "no state_file in config"}
        print(json.dumps(receipt, indent=2))
        return 2

    state_path = Path(state_path_str)
    if not state_path.is_absolute():
        state_path = root / state_path
    if not state_path.is_file():
        errors.append(f"durable state file missing: {state_path}")
        receipt["verdict"] = "REJECTED"
        receipt["errors"] = errors
        receipt["state_read"] = {
            "status": "missing",
            "path": str(state_path),
        }
        print(json.dumps(receipt, indent=2))
        return 2

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"durable state unreadable: {exc}")
        receipt["verdict"] = "REJECTED"
        receipt["errors"] = errors
        receipt["state_read"] = {
            "status": "unreadable",
            "path": str(state_path),
        }
        print(json.dumps(receipt, indent=2))
        return 2

    state_read = {
        "status": "loaded",
        "path": str(state_path),
        "objective": state.get("objective"),
        "next_action": state.get("next_action"),
        "created_at": state.get("created_at"),
        "session_boundary_state_version": state.get("session_boundary_state_version"),
    }
    receipt["state_read"] = state_read
    receipt["verdict"] = "ACCEPTED"
    receipt["errors"] = errors
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
