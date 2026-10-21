#!/usr/bin/env python3
"""Strip account residue from a stream-json trace, in place.

Dropped events:
  system            init and commands_changed list the replaying account's synced
                    skills, plugins and local tool paths.
  rate_limit_event  publishes the replaying account's billing and quota state.

Blanked values (every occurrence, at any depth), replaced with REDACTED:
  session_id, uuid, request_id   identifiers of the throwaway replay session.

Dropped keys (at any depth):
  total_cost_usd, modelUsage     the account's spend for the run.

None of these describe the recipe walk. Lines with none of them are kept byte for
byte; a changed line is re-serialized as compact JSON. Idempotent.

Usage: python -I strip_system.py <trace.ndjson.txt>
"""
import json
import sys
from pathlib import Path

DROP_EVENTS = {"system", "rate_limit_event"}
BLANK_KEYS = {"session_id", "uuid", "request_id"}
DROP_KEYS = {"total_cost_usd", "modelUsage"}
REDACTED = "REDACTED"


def scrub(value):
    if isinstance(value, dict):
        return {
            k: (REDACTED if k in BLANK_KEYS else scrub(v))
            for k, v in value.items()
            if k not in DROP_KEYS
        }
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def strip_line(line: str) -> str:
    try:
        event = json.loads(line)
    except ValueError:
        return line
    if not isinstance(event, dict):
        return line
    if event.get("type") in DROP_EVENTS:
        return ""
    clean = scrub(event)
    if clean == event:
        return line
    ending = "\n" if line.endswith("\n") else ""
    return json.dumps(clean, ensure_ascii=False, separators=(",", ":")) + ending


def main() -> None:
    path = Path(sys.argv[1])
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(strip_line(l) for l in lines), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
