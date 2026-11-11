#!/usr/bin/env python3
"""Suite for check_overwrite_updaters.py: a write built from an earlier read is refused.

    Cases:
      - the line #645 shipped at c02288f (`update($, tip, () => current)`) is refused;
      - a zero-argument updater split over two lines is refused at the arrow's line;
      - an updater that takes the stored value passes;
      - the `_`, typed, generic and commented forms and a `$.state.set` without `ifVersion` are refused;
      - an overwrite with a reason on its own line passes; an empty, block-comment or other-line reason does not;
      - a nested hook file is read, and a named file is read in place of the tree;
      - the mods in this tree pass.
"""
from __future__ import annotations

import io
import sys
import tempfile
from contextlib import redirect_stdout
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
    for form in ("update($, tip, _ => x)", "update($, tip, (_) => x)", "update($, tip, (_: Tip | null) => x)",
                 "update($, tip, (): Tip => x)", "update<Tip>($, tip, () => x)", "update($, tip, /* blind */ () => x)",
                 "$.state.set(tip, x)"):
        check(f"the blind form {form!r} is refused", len(cou.findings(form)) == 1, cou.findings(form))
    check("a set that names the version it read passes", not cou.findings("$.state.set(tip, x, { ifVersion: v })"))
    two = "update($, a, () => x)\nupdate($, b, () => y) // overwrite: b is rebuilt on each start\n"
    check("a reason excuses only its own line", cou.findings(two) == [(1, "update($, a, () => x)")], cou.findings(two))
    check("a reason in a block comment is no reason",
          len(cou.findings("update($, tip, () => found) /* overwrite: newest wins */")) == 1)
    sep = "const s = 'a\u2028b'\nupdate($, tip, () => x)\n"
    check("a Unicode line separator does not shift the line shown", cou.findings(sep) == [(2, "update($, tip, () => x)")],
          cou.findings(sep))
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
            (hooks / "lib").mkdir()
            (hooks / "lib" / "state.ts").write_text("\ufeffupdate($, tip, () => x)\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()) as shown:
                code = cou.main([])
            check("a nested .ts hook file is read, and its byte-order mark is not shown",
                  code == 1 and "﻿" not in shown.getvalue() and "state.ts:1:" in shown.getvalue(), shown.getvalue())
            check("a named file is read in place of the tree", cou.main([str(hooks / "register.tsx")]) == 0)
        finally:
            cou.ROOT = real_root
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        return 1
    print("PASS: check_overwrite_updaters refuses a write built from an earlier read")
    return 0


if __name__ == "__main__":
    sys.exit(main())
