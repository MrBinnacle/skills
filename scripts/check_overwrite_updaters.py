#!/usr/bin/env python3
"""Refuse a mod state write that ignores the value stored now.

`update($, atom, () => value)` stores a value built from an earlier read, so a
newer value stored in between is lost. Verifiers failed #645 twice and #661 on
this. Pass the stored value instead, `update($, atom, now => ...)`, and return
`now` unless it is the value you read. A write that must replace whatever is
stored ends its line with `// overwrite: <why the stored value does not matter>`.

Run: python scripts/check_overwrite_updaters.py [file ...]
With no file, it reads every hook file under mods/*/hooks/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLIND = re.compile(r"\bupdate\(\s*\$\s*,\s*[\w.]+\s*,\s*(?:async\s*)?\(\s*\)\s*=>")
REASON = re.compile(r"//\s*overwrite:\s*\S")
FIX = ("pass `now => ...` and return `now` unless it is the value you read, "
       "or end the line with `// overwrite: <why the stored value does not matter>`")


def findings(source: str) -> list[tuple[int, str]]:
    lines = source.splitlines()
    out = []
    for m in BLIND.finditer(source):
        n = source.count("\n", 0, m.end())
        if not REASON.search(lines[n]):
            out.append((n + 1, lines[n].strip()))
    return out


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or sorted(p for p in (ROOT / "mods").glob("*/hooks/**/*") if p.suffix in (".ts", ".tsx"))
    if not files:
        print("ERROR: no mod hook file found; the check read nothing")
        return 2
    bad = 0
    for f in files:
        for n, text in findings(f.read_text(encoding="utf-8")):
            print(f"  - {f.as_posix()}:{n}: this update ignores the value stored now: {text}\n    Instead, {FIX}.")
            bad += 1
    if bad:
        print(f"REJECTED: {bad} state write(s) that can lose a newer value")
        return 1
    print(f"PASS: no state write ignores the stored value in {len(files)} mod hook file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
