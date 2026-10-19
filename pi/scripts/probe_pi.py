"""Ask a fresh Pi process (RPC mode, no session) what it actually loaded.

Prints the effective model and thinking level, then every command grouped by source,
with skill commands shown alongside their SKILL.md path.

Usage: python pi/scripts/probe_pi.py [--expect-skills-dir DIR]
With --expect-skills-dir, exit 1 unless the loaded skill commands are exactly the
skill directories under DIR, each loaded from that directory.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REQUESTS = [{"type": "get_state", "id": "s"}, {"type": "get_commands", "id": "c"}]


def probe() -> tuple[dict, list[dict]]:
    stdin = "".join(json.dumps(r) + "\n" for r in REQUESTS)
    out = subprocess.run(
        "pi --mode rpc --no-session", shell=True, input=stdin, capture_output=True,
        text=True, encoding="utf-8", timeout=90,
    ).stdout
    state, commands = {}, []
    for line in out.splitlines():
        msg = json.loads(line)
        if msg.get("command") == "get_state":
            state = msg["data"]
        elif msg.get("command") == "get_commands":
            data = msg["data"]
            commands = data["commands"] if isinstance(data, dict) else data
    return state, commands


def main() -> int:
    expect_dir = None
    if "--expect-skills-dir" in sys.argv:
        expect_dir = Path(sys.argv[sys.argv.index("--expect-skills-dir") + 1]).resolve()

    state, commands = probe()
    print(f"model: {state['model']['provider']}/{state['model']['id']}  thinking: {state.get('thinkingLevel')}")
    by_source: dict[str, list[dict]] = {}
    for c in commands:
        by_source.setdefault(c["source"], []).append(c)
    for source, items in sorted(by_source.items()):
        print(f"\n[{source}] {len(items)}")
        for c in sorted(items, key=lambda c: c["name"]):
            path = (c.get("sourceInfo") or {}).get("path", "")
            print(f"  {c['name']}  {path if source == 'skill' else ''}".rstrip())

    if expect_dir is None:
        return 0
    want = {p.name for p in expect_dir.iterdir() if (p / "SKILL.md").is_file()}
    got: dict[str, Path] = {}
    for c in by_source.get("skill", []):
        got[c["name"].removeprefix("skill:")] = Path(c["sourceInfo"]["path"]).resolve()
    problems = [f"missing skill: {n}" for n in sorted(want - got.keys())]
    problems += [f"unexpected skill: {n} ({got[n]})" for n in sorted(got.keys() - want)]
    problems += [
        f"{n} loaded from {got[n]}, not {expect_dir}"
        for n in sorted(want & got.keys()) if expect_dir not in got[n].parents
    ]
    print()
    for p in problems:
        print("FAIL", p)
    print("OK: loaded skills match exactly" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
