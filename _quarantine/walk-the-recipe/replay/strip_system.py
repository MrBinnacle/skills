#!/usr/bin/env python3
"""Drop the system events from a stream-json trace, in place.

System events (init, commands_changed) list the replaying account's synced skills, plugins and local
tool paths. They describe the agent's host, not the recipe walk, and they would
publish account residue. Every other event is kept byte for byte.

Usage: python -I strip_system.py <trace.jsonl>
"""
import json
import sys
from pathlib import Path


def keep(line: str) -> bool:
    try:
        event = json.loads(line)
    except ValueError:
        return True
    return event.get("type") != "system"


path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
path.write_text("".join(l for l in lines if keep(l)), encoding="utf-8", newline="")
