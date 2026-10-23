#!/usr/bin/env python3
"""Run the shell steps of .github/workflows/tests.yml on this machine, one at a time.

CI runs about a hundred `run:` steps across five jobs. Copying them by hand into a
local session dropped steps and cost a long transcript on 2026-10-23, so this
script reads the workflow and runs each step as CI would: in bash, from the repo
root, with the step's `env`, and with RUNNER_TEMP, GITHUB_WORKSPACE and
GITHUB_BASE_REF set to local stand-ins.

Skipped, and listed as skipped:
  - `uses:` steps (checkout, setup-python, setup-node, setup-bun);
  - steps whose `if:` holds only on a pull_request event;
  - steps that install software globally (`npm install --global`, `pip install`)
    or fetch from the remote (`git fetch`);
  - steps that read a `$RUNNER_TEMP/<name>` path a skipped step in the same job uses.
`git init` makes `master`, as on the hosted runner, whatever the local git config says.
`matrix.os == 'ubuntu-latest'` is treated as true, so this runs the ubuntu leg.
A job whose actions/checkout is shallow in CI (no `fetch-depth: 0`) gets a NOTE line:
this clone has full history and every remote ref, so a step that walks history or
resolves origin/<branch> can pass here and fail there (PR #622, 2026-10-23).
A step key the script does not model (`working-directory`, `shell`) is an error,
so the runner fails loudly when the workflow grows one.

Needs PyYAML (maintainer machine only; CI does not run this script).

  python scripts/ci_local.py --list
  python scripts/ci_local.py --job release-gate --match "Poison control"
"""

from __future__ import annotations

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
MODELLED_KEYS = {"name", "run", "env", "if", "id"}
TRUE_IFS = {"matrix.os == 'ubuntu-latest'"}
SKIP_IFS = {"github.event_name == 'pull_request'"}
SKIP_COMMANDS = re.compile(r"npm install --global|pip install|git fetch")
RUNNER_TEMP_PATH = re.compile(r"\$RUNNER_TEMP/[\w.-]+")
# The hosted runner's git has no init.defaultBranch, so `git init` makes `master`; fixture steps rely on it.
RUNNER_GIT = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "init.defaultBranch", "GIT_CONFIG_VALUE_0": "master"}


@dataclass(frozen=True)
class Step:
    job: str
    index: int
    name: str
    run: str
    env: dict[str, str]
    skip: str | None


def load_steps(workflow: Path) -> list[Step]:
    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    steps = []
    for job, spec in data["jobs"].items():
        # A step that reads a $RUNNER_TEMP path a skipped step builds would fail for that reason alone.
        skipped_paths: dict[str, int] = {}
        for index, raw in enumerate(spec["steps"]):
            if "run" not in raw:
                continue
            unknown = set(raw) - MODELLED_KEYS
            if unknown:
                raise SystemExit(f"{job} step {index}: unmodelled key(s) {sorted(unknown)}; teach ci_local.py first")
            paths = set(RUNNER_TEMP_PATH.findall(raw["run"]))
            skip = skip_reason(raw)
            needed = sorted(p for p in paths if p in skipped_paths)
            if not skip and needed:
                skip = f"needs {needed[0]} from skipped step {skipped_paths[needed[0]]}"
            if skip:
                skipped_paths.update({p: index for p in paths if p not in skipped_paths})
            steps.append(Step(job, index, raw.get("name", f"step {index}"), raw["run"],
                              {k: str(v) for k, v in (raw.get("env") or {}).items()}, skip))
    return steps


def shallow_jobs(workflow: Path) -> dict[str, str]:
    """Map each job whose checkout of this repo fetches less than full history to its CI fetch-depth.

    The last `actions/checkout` step without `repository:` decides, as it leaves the workspace's history.
    A depth that is not a literal integer (an expression) is reported as unknown, not read as full.
    """
    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    shallow = {}
    for job, spec in data["jobs"].items():
        depth = None
        for raw in spec["steps"]:
            options = raw.get("with") or {}
            if str(raw.get("uses", "")).split("@")[0] == "actions/checkout" and "repository" not in options:
                depth = str(options.get("fetch-depth", 1)).strip()
        if depth is not None and depth != "0":
            shallow[job] = depth if depth.isdigit() else f"unknown ({depth})"
    return shallow


def skip_reason(raw: dict) -> str | None:
    condition = str(raw.get("if", "")).strip()
    if condition in SKIP_IFS:
        return f"if: {condition}"
    if condition and condition not in TRUE_IFS:
        raise SystemExit(f"step {raw.get('name')!r}: unmodelled if: {condition}")
    found = SKIP_COMMANDS.search(raw["run"])
    return f"installs or fetches ({found.group(0)})" if found else None


def run_step(step: Step, bash: str, temp: Path) -> int:
    env = {**os.environ, **RUNNER_GIT, **step.env, "RUNNER_TEMP": str(temp), "GITHUB_WORKSPACE": str(ROOT),
           "GITHUB_BASE_REF": "main"}
    return subprocess.run([bash, "-c", step.run], cwd=ROOT, env=env).returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run the shell steps of the CI workflow locally.")
    parser.add_argument("--list", action="store_true", help="print the steps and exit")
    parser.add_argument("--job", action="append", help="run only this job (repeatable)")
    parser.add_argument("--match", help="run only steps whose name contains this text")
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    parser.add_argument("--bash", default=shutil.which("bash"), help="bash to run steps with")
    args = parser.parse_args(argv)
    steps = [s for s in load_steps(args.workflow)
             if (not args.job or s.job in args.job) and (not args.match or args.match in s.name)]
    shallow = shallow_jobs(args.workflow)
    for job in sorted({s.job for s in steps} & shallow.keys()):
        print(f"NOTE {job}: CI checks out with fetch-depth {shallow[job]}; this clone has full history and every"
              " remote ref, so a step that walks history or resolves origin/<branch> can pass here and fail in CI")
    if args.list:
        for s in steps:
            print(f"{s.job}[{s.index}] {s.name}" + (f"  (skip: {s.skip})" if s.skip else ""))
        return 0
    if not args.bash:
        print("no bash on PATH; pass --bash", file=sys.stderr)
        return 2
    failed, skipped, ran = [], 0, 0
    temps: dict[str, Path] = {}
    try:
        for s in steps:
            if s.skip:
                skipped += 1
                print(f"SKIP {s.job}[{s.index}] {s.name} ({s.skip})", flush=True)
                continue
            temp = temps.setdefault(s.job, Path(tempfile.mkdtemp(prefix=f"ci-local-{s.job}-")))
            rc = run_step(s, args.bash, temp)
            ran += 1
            print(f"{'PASS' if rc == 0 else 'FAIL'} rc={rc} {s.job}[{s.index}] {s.name}", flush=True)
            if rc:
                failed.append(f"{s.job}[{s.index}] {s.name}")
    finally:
        for temp in temps.values():
            shutil.rmtree(temp, ignore_errors=True)
    print(f"\n{ran} ran, {skipped} skipped, {len(failed)} failed")
    for name in failed:
        print(f"  FAILED {name}")
    return 1 if failed or not ran else 0


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
