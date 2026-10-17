#!/usr/bin/env python3
"""Suite for validate_install_paths.py: the tree passes, and each over-budget form is refused.

The red cases are path strings, not files. A path over budget cannot be created on a
Windows runner without long paths, which is the defect the check guards against.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_install_paths as ip  # noqa: E402

ROOT = SCRIPT_DIR.parent


def _path(directory_length: int, file_length: int) -> str:
    """A path whose parent directory and whole length are exactly as given."""
    directory = "scripts/fixtures/" + "d" * (directory_length - len("scripts/fixtures/"))
    return directory + "/" + "f" * (file_length - directory_length - 1)


def main() -> int:
    failures: list[str] = []

    # The measured arithmetic, so a constant edit shows up as a suite failure.
    measured = (ip.WORST_CASE_ROOT, ip.CLONE_PREFIX, ip.FILE_BUDGET, ip.DIR_BUDGET)
    if measured != (37, 59, 163, 151):
        failures.append(f"budget arithmetic drifted: {measured}; measured 37, 59, 163, 151")

    live = ip.check(ip.tracked_paths(ROOT))
    if live:
        failures.append(f"tracked tree should pass, got {live}")

    if ip.check([_path(151, 163)]):
        failures.append("a 163-character path with a 151-character directory was refused")

    over = {
        "file over 163": (_path(100, 164), "is 164 characters"),
        "directory over 151": (_path(152, 160), "directory"),
    }
    for label, (path, expected) in over.items():
        errors = ip.check([path])
        if len(errors) != 1 or expected not in errors[0]:
            failures.append(f"{label} was not refused alone: {errors}")

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"PASS: install-path suite, {len(over) + 3} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
