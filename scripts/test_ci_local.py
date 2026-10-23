#!/usr/bin/env python3
"""Suite for scripts/ci_local.py.

Each case writes a fixture workflow and runs the script as a maintainer does.
The states it must tell apart:

  - a passing step and a failing step: exit 1, the failure named;
  - step env, RUNNER_TEMP and GITHUB_BASE_REF reach the step;
  - pull_request-only, uses:, global-install and git-fetch steps are skipped,
    and so is a step that reads what a skipped step wrote;
  - git init makes master, as on the hosted runner;
  - an unmodelled step key or if: condition is refused, not run;
  - a filter that leaves nothing to run exits non-zero;
  - a job with a shallow CI checkout is named, and a full-history one is not;
    a checkout of another repository does not count, the last checkout of
    this one decides, and an expression depth is named as unknown.

Run directly:  python scripts/test_ci_local.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "ci_local.py"
FAILURES: list[str] = []
CHECKED: list[str] = []

WORKFLOW = """\
jobs:
  alpha:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Env reaches the step
        env:
          FIXTURE_VALUE: seen
        run: |
          test "$FIXTURE_VALUE" = seen
          test -d "$RUNNER_TEMP"
          test "$GITHUB_BASE_REF" = main
      - name: Ubuntu only
        if: matrix.os == 'ubuntu-latest'
        run: echo ubuntu
      - name: PR only
        if: github.event_name == 'pull_request'
        run: exit 7
      - name: Install a tool
        run: npm install --global left-pad
      - name: Fetch
        run: |
          git fetch origin main > "$RUNNER_TEMP/fetched"
      - name: Reads what Fetch wrote
        run: cat "$RUNNER_TEMP/fetched"
      - name: Git init makes master
        run: |
          git init -q "$RUNNER_TEMP/repo"
          git -C "$RUNNER_TEMP/repo" symbolic-ref HEAD | grep -qx refs/heads/master
  beta:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Broken step
        run: exit 3
"""


def check(label: str, ok: bool, detail: str = "") -> None:
    CHECKED.append(label)
    if not ok:
        FAILURES.append(f"{label}: {detail}")


def run(workflow: str, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tests.yml"
        path.write_text(workflow, encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), "--workflow", str(path), *args],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")


def main() -> int:
    whole = run(WORKFLOW)
    check("a failing step fails the run", whole.returncode == 1, f"rc={whole.returncode}")
    check("the failure is named", "FAILED beta[1] Broken step" in whole.stdout, whole.stdout)
    check("env and runner variables reach the step", "PASS rc=0 alpha[1] Env reaches the step" in whole.stdout,
          whole.stdout + whole.stderr)
    check("ubuntu-only steps run", "PASS rc=0 alpha[2] Ubuntu only" in whole.stdout, whole.stdout)
    for name in ("PR only", "Install a tool", "Fetch"):
        check(f"{name} is skipped", f"] {name} (" in whole.stdout, whole.stdout)
    check("a step needing a skipped step's output is skipped",
          "SKIP alpha[6] Reads what Fetch wrote (needs $RUNNER_TEMP/fetched from skipped step 5)" in whole.stdout,
          whole.stdout)
    check("git init makes master as on the runner", "PASS rc=0 alpha[7] Git init makes master" in whole.stdout,
          whole.stdout)
    check("the tally counts runs and skips", "4 ran, 4 skipped, 1 failed" in whole.stdout, whole.stdout)

    check("a shallow CI checkout is named", "NOTE alpha: CI checks out with fetch-depth 1" in whole.stdout,
          whole.stdout)
    check("a full-history checkout is not named", "NOTE beta" not in whole.stdout, whole.stdout)

    full = "      - uses: actions/checkout@v4\n        with:\n          fetch-depth: 0\n"
    other = "      - uses: actions/checkout@v4\n        with:\n          repository: o/other\n"
    side = WORKFLOW.replace(full, full + other)
    check("another repository's checkout does not count", "NOTE beta" not in run(side, "--list").stdout, side)
    later = WORKFLOW.replace("      - uses: actions/checkout@v4\n      - name: Env",
                             "      - uses: actions/checkout@v4\n" + full + "      - name: Env")
    check("the last checkout decides", "NOTE alpha" not in run(later, "--list").stdout, later)
    vendored = WORKFLOW.replace("      - uses: actions/checkout@v4\n      - name: Env",
                                "      - uses: actions/checkout-extra@v1\n      - name: Env")
    check("only actions/checkout counts", "NOTE alpha" not in run(vendored, "--list").stdout, vendored)
    expr = WORKFLOW.replace("fetch-depth: 0", "fetch-depth: ${{ inputs.depth }}")
    listed = run(expr, "--list")
    check("an expression depth is unknown, not a crash",
          listed.returncode == 0 and "NOTE beta: CI checks out with fetch-depth unknown" in listed.stdout,
          listed.stdout + listed.stderr)

    alpha = run(WORKFLOW, "--job", "alpha")
    check("a green job exits 0", alpha.returncode == 0, alpha.stdout + alpha.stderr)

    listing = run(WORKFLOW, "--list")
    check("--list runs nothing", listing.returncode == 0 and "PASS" not in listing.stdout, listing.stdout)
    check("--list marks skips", "alpha[3] PR only  (skip: if:" in listing.stdout, listing.stdout)

    empty = run(WORKFLOW, "--match", "no such step")
    check("an empty selection is not a pass", empty.returncode == 1, f"rc={empty.returncode}")

    unknown_key = run(WORKFLOW.replace("        run: exit 3", "        working-directory: sub\n        run: exit 3"))
    check("an unmodelled key is refused", unknown_key.returncode != 0 and "working-directory" in unknown_key.stderr,
          unknown_key.stdout + unknown_key.stderr)
    unknown_if = run(WORKFLOW.replace("matrix.os == 'ubuntu-latest'", "runner.os == 'Windows'"))
    check("an unmodelled if: is refused", unknown_if.returncode != 0 and "runner.os" in unknown_if.stderr,
          unknown_if.stdout + unknown_if.stderr)

    if FAILURES:
        print("FAIL: ci_local suite")
        for failure in FAILURES:
            print(f"  {failure}")
        return 1
    print(f"PASS: ci_local suite, {len(CHECKED)} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
