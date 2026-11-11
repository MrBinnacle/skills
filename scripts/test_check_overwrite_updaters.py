#!/usr/bin/env python3
"""Suite for check_overwrite_updaters.py: a write built from an earlier read is refused.

    Cases:
      - the line #645 shipped at c02288f (`update($, tip, () => current)`) is refused;
      - a zero-argument updater split over two lines is refused at the arrow's line;
      - an updater that takes the stored value passes;
      - an overwrite with a reason passes, and an empty reason does not;
      - the mods in this tree pass.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import check_overwrite_updaters as cou  # noqa: E402

FAILURES: list[str] = []
# mods/tips-anywhere/hooks/register.tsx line 225 at c02288f, the head the #645 verifier failed.
SHIPPED = "async function unsettle() {\n  await update($, tip, () => current)\n}\n"


def check(case: str, ok: bool, detail: object = "") -> None:
    print(f"  {'ok  ' if ok else 'FAIL'} {case}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILURES.append(case)


def main() -> int:
    got = cou.findings(SHIPPED)
    check("the #645 line is refused", got == [(2, "await update($, tip, () => current)")], got)
    split = "await update($, approved,\n  () => ({ lines, at }))\n"
    check("a split call is refused at the arrow", [n for n, _ in cou.findings(split)] == [2], cou.findings(split))
    check("async zero-argument updater is refused", len(cou.findings("update($, tip, async () => x)")) == 1)
    check("an updater of the stored value passes", not cou.findings("update($, tip, now => now?.line === l ? null : now)"))
    check("a named stored value passes", not cou.findings("update($, outcomes, all => ({ ...all, [k]: v }))"))
    check("an overwrite with a reason passes",
          not cou.findings("update($, tip, () => found) // overwrite: a new offer replaces the waiting note"))
    check("an empty reason is refused", len(cou.findings("update($, tip, () => found) // overwrite:")) == 1)
    check("the mods in this tree pass", cou.main([]) == 0)
    real_root = cou.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        hooks = Path(tmp) / "mods" / "demo" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "notes.md").write_text(SHIPPED, encoding="utf-8")
        cou.ROOT = Path(tmp)
        try:
            check("a tree with no .ts or .tsx hook file is an error, not a pass", cou.main([]) == 2)
            (hooks / "register.tsx").write_text(SHIPPED, encoding="utf-8")
            check("a hook file with the #645 line is rejected", cou.main([]) == 1)
            (hooks / "register.tsx").write_text("update($, tip, now => now)\n", encoding="utf-8")
            check("a clean hook file passes, and the .md beside it is not read", cou.main([]) == 0)
        finally:
            cou.ROOT = real_root
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        return 1
    print("PASS: check_overwrite_updaters refuses a write built from an earlier read")
    return 0


if __name__ == "__main__":
    sys.exit(main())
