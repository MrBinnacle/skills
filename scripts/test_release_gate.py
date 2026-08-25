#!/usr/bin/env python3
"""Contract tests for scripts/release_gate.py (ADR 0002, issue #149).

ADR 0002 (docs/adr/0002-a-release-is-a-delivery-event.md) obliges the manifest
to carry a version on each plugin entry, generated from package.json and
asserted equal by a check -- never typed twice. These cases pin that contract.

Every case drives the shipped script as a subprocess against a seeded
temporary tree (--root), never against module internals: the contract is the
exit code and the printed verdict, because those are what CI and a local run
consume. A live-tree case runs the gate over this repository exactly as a
maintainer would, with no arguments.

THE SEEDED TREE PASSES BY CONSTRUCTION
    Each refusal case below is one mutation of `seeded_tree`, so a FAIL line a
    run prints is attributable to the mutation under test. Refusal cases assert
    the message that names the reason, not merely a non-zero exit -- two
    different faults share one exit code, which is the defect the vacuous
    changeset control documented in tests.yml.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GATE = SCRIPT_DIR / "release_gate.py"
REPO_ROOT = SCRIPT_DIR.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def package_json(version: str) -> str:
    return json.dumps({"name": "mrbinnacle-skills", "version": version}, indent=2) + "\n"


def manifest_json(versions: list[str | None]) -> str:
    """A manifest shaped like the shipped one, with one entry per version given.

    ``None`` stamps an entry that declares no version at all -- the second
    direction of drift.
    """
    plugins = []
    for i, version in enumerate(versions):
        entry = {
            "name": f"fixture-plugin-{i}",
            "description": "fixture plugin",
            "source": "./",
            "strict": False,
            "skills": [],
        }
        if version is not None:
            entry["version"] = version
        plugins.append(entry)
    data = {
        "name": "fixture-skills",
        "owner": {"name": "fixture", "url": "https://example.invalid"},
        "metadata": {"description": "fixture"},
        "plugins": plugins,
    }
    return json.dumps(data, indent=2) + "\n"


def seeded_tree(root: Path, *, package: str = "1.2.0", versions: list[str] | None = None) -> Path:
    """The conforming baseline: every declared version equals the package's."""
    write(root / "package.json", package_json(package))
    write(
        root / ".claude-plugin" / "marketplace.json",
        manifest_json([package] if versions is None else versions),
    )
    return root


# ----------------------------------------------------------------- G1 lockstep


def case_lockstep_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        result = run_gate("--root", str(root))
        check(
            "a tree whose manifest versions equal the package version passes",
            result.returncode == 0,
            result.stdout + result.stderr,
        )
        check(
            "the pass line names the verdict and the derived version",
            "RELEASE GATE: PASS" in result.stdout and "1.2.0" in result.stdout,
            result.stdout,
        )


def case_declared_but_different_version_is_refused() -> None:
    """Direction one: an entry declares a value, and it is not the package's."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["9.9.9"])
        result = run_gate("--root", str(root))
        check(
            "a manifest version other than the package version is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the refusal names the lockstep failure specifically",
            "version drift" in result.stdout,
            result.stdout,
        )
        check(
            "the refusal names both values and the offending plugin",
            "9.9.9" in result.stdout and "1.2.0" in result.stdout and "fixture-plugin-0" in result.stdout,
            result.stdout,
        )


def case_missing_declaration_is_refused() -> None:
    """Direction two: an entry declares nothing. Absence is drift too -- the
    pre-#149 manifest failed here while declaring no wrong value anywhere."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=[None])
        result = run_gate("--root", str(root))
        check(
            "a plugin entry with no version is refused",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "the absence refusal is reported as version drift, not skipped",
            "version drift" in result.stdout and "declares no version" in result.stdout,
            result.stdout,
        )


def case_every_failure_reported_in_one_run() -> None:
    """One drifted value and one absent declaration must BOTH be listed by a
    single run. A first-fail gate hides the second fault until the first is
    fixed, which is how stale surfaces survive several review rounds."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["9.9.9", None])
        result = run_gate("--root", str(root))
        check(
            "two independent drifts are refused in one run",
            result.returncode != 0,
            result.stdout,
        )
        check(
            "both failures are listed, not only the first",
            "fixture-plugin-0" in result.stdout and "fixture-plugin-1" in result.stdout,
            result.stdout,
        )
        check(
            "the blocked line counts every failure found",
            "2 stale surface(s)" in result.stdout,
            result.stdout,
        )


# ------------------------------------------------------------- fail-closed G1


def case_absent_package_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        (root / "package.json").unlink()
        result = run_gate("--root", str(root))
        check(
            "an unreadable package.json is a failure, not a skip",
            result.returncode != 0 and "could not be read" in result.stdout,
            result.stdout,
        )


def case_unparseable_package_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / "package.json", "{not json")
        result = run_gate("--root", str(root))
        check(
            "an unparseable package.json is a failure, not a skip",
            result.returncode != 0 and "not parseable JSON" in result.stdout,
            result.stdout,
        )


def case_versionless_package_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / "package.json", '{"name": "mrbinnacle-skills"}\n')
        result = run_gate("--root", str(root))
        check(
            "a package.json stating no version is a failure - there is nothing to derive from",
            result.returncode != 0 and "states no version" in result.stdout,
            result.stdout,
        )


def case_absent_manifest_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        (root / ".claude-plugin" / "marketplace.json").unlink()
        result = run_gate("--root", str(root))
        check(
            "an unreadable manifest is a failure, not a skip",
            result.returncode != 0 and "could not be read" in result.stdout,
            result.stdout,
        )


def case_unparseable_manifest_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp))
        write(root / ".claude-plugin" / "marketplace.json", '{"plugins": [}')
        result = run_gate("--root", str(root))
        check(
            "an unparseable manifest is a failure, not a skip",
            result.returncode != 0 and "not parseable JSON" in result.stdout,
            result.stdout,
        )
        check(
            "an unparseable manifest does not also report zero entries",
            "no plugin entries" not in result.stdout,
            result.stdout,
        )


def case_shape_broken_manifest_fails_closed() -> None:
    """`{"plugins": ["x"]}` parsed fine once and raised AttributeError past the
    handler in validate_conformance.py's O7; this gate refuses the shape instead."""
    for bad, why in (
        ('{"plugins": ["x"]}', "a string where an object belongs"),
        ("[1, 2]", "a top-level array"),
        ("{}", "a missing plugins key"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = seeded_tree(Path(tmp))
            write(root / ".claude-plugin" / "marketplace.json", bad)
            result = run_gate("--root", str(root))
            check(
                f"a broken-shaped manifest ({why}) fails closed",
                result.returncode != 0 and "not a readable manifest" in result.stdout,
                result.stdout,
            )


def case_zero_plugins_rejected() -> None:
    """A run that compared against nothing checked nothing. Never a pass."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=[])
        result = run_gate("--root", str(root))
        check(
            "a manifest with no plugin entries is refused",
            result.returncode != 0 and "no plugin entries" in result.stdout,
            result.stdout,
        )


# ------------------------------------------------------------------- --write


def case_write_derives_every_entry_from_the_package() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["0.0.1", None])
        result = run_gate("--write", "--root", str(root))
        check(
            "--write exits 0 after stamping the seeded tree",
            result.returncode == 0,
            result.stdout + result.stderr,
        )
        stamped = json.loads((Path(tmp) / ".claude-plugin" / "marketplace.json").read_text("utf-8"))
        declared = {p["name"]: p.get("version") for p in stamped["plugins"]}
        check(
            "--write derives EVERY entry's version from package.json",
            set(declared.values()) == {"1.2.0"},
            str(declared),
        )
        verify = run_gate("--root", str(tmp))
        check(
            "the written tree verifies in lockstep",
            verify.returncode == 0,
            verify.stdout,
        )


def case_write_is_idempotent() -> None:
    """Generated data must be stable under re-runs; churn would make every
    unrelated commit carry a diff."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seeded_tree(Path(tmp), versions=["0.0.1"])
        first = run_gate("--write", "--root", str(root))
        once = (Path(tmp) / ".claude-plugin" / "marketplace.json").read_bytes()
        second = run_gate("--write", "--root", str(root))
        twice = (Path(tmp) / ".claude-plugin" / "marketplace.json").read_bytes()
        check(
            "--write is idempotent: a second run writes identical bytes",
            first.returncode == 0 and second.returncode == 0 and once == twice,
            first.stdout + second.stdout,
        )


def case_write_fails_closed_on_unreadable_inputs() -> None:
    for victim, why in (("package.json", "unreadable source"), ("marketplace.json", "unreadable target")):
        with tempfile.TemporaryDirectory() as tmp:
            root = seeded_tree(Path(tmp))
            if victim == "package.json":
                (root / "package.json").unlink()
            else:
                (root / ".claude-plugin" / "marketplace.json").unlink()
            result = run_gate("--write", "--root", str(root))
            check(
                f"--write fails closed on an {why}, writing nothing",
                result.returncode != 0 and "RELEASE GATE: PASS" not in result.stdout,
                result.stdout,
            )


def case_live_tree_in_lockstep() -> None:
    """The shipped tree, checked exactly as a maintainer checks it: no
    arguments. This pins the acceptance criterion against the real artifact --
    every live plugin entry declares a version, derived by --write from
    package.json -- rather than only against fixtures built to pass."""
    result = run_gate()
    check(
        "the live tree passes the gate with no arguments",
        result.returncode == 0 and "RELEASE GATE: PASS" in result.stdout,
        result.stdout + result.stderr,
    )
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    undeclared = [
        p["name"] for p in manifest["plugins"] if p.get("version") != package["version"]
    ]
    check(
        "every live plugin entry declares the package.json version",
        not undeclared,
        f"entries not at {package['version']}: {undeclared}",
    )


# ------------------------------------------------------------------ CI wiring
#
# The gate's verdict must not depend on where it runs: CI executes the same
# argument-less command a local run does, so neither surface can grow flags or
# context the other lacks. These cases read tests.yml the way the eval-corpus
# suite reads it -- as text, asserting the wiring that exists rather than
# parsing YAML into a different dialect.


def workflow_job(name: str) -> str:
    """One job's body from tests.yml, from its key to the next top-level job."""
    match = re.search(rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  \S|\Z)", WORKFLOW.read_text("utf-8"))
    return match.group(1) if match else ""


def named_step(job: str, step_name: str) -> str:
    """One step's body, from its `name:` line to the next `- name:` line."""
    match = re.search(
        rf"(?ms)^      - name: {re.escape(step_name)}\n(.*?)(?=^      - name: |\Z)", job
    )
    return match.group(1) if match else ""


def case_ci_runs_the_same_argumentless_command() -> None:
    """Criterion 6, CI half: what CI runs is what a local run runs. A gate
    whose CI form carries different flags verifies a different contract than
    the one the maintainer can run, and the difference would be invisible
    until the two disagreed about a release."""
    job = workflow_job("release-gate")
    step = named_step(job, "Run release gate")
    check(
        "the CI release-gate job exists",
        bool(job),
        "no 'release-gate:' job found in .github/workflows/tests.yml",
    )
    check(
        "CI runs the gate with no arguments - the same command a local run uses",
        "python scripts/release_gate.py" in step
        and "--root" not in step
        and "--write" not in step,
        step,
    )
    check(
        "CI asserts the PASS verdict line, not only an exit code",
        "RELEASE GATE: PASS" in step,
        step,
    )
    suite_step = named_step(job, "Release-gate suite")
    check(
        "CI runs this suite itself and requires its PASS line",
        "python scripts/test_release_gate.py" in suite_step and "^PASS:" in suite_step,
        suite_step,
    )


def case_ci_job_is_non_blocking_and_on_every_pull_request() -> None:
    """Criterion 7: advisory while the tracer matures. The blocking gate ADR
    0002 owes arrives with the release pipeline; until then a refusal must be
    visible without gating merges on a process that cannot act on it yet."""
    job = workflow_job("release-gate")
    triggers = WORKFLOW.read_text("utf-8")[: WORKFLOW.read_text("utf-8").index("jobs:")]
    check(
        "the release-gate job is non-blocking (continue-on-error)",
        "continue-on-error: true" in job,
        job,
    )
    check(
        "the workflow runs on pull_request",
        "pull_request:" in triggers,
        triggers,
    )


def case_ci_control_drives_the_gate_red_for_the_right_reason() -> None:
    """Criterion 8: the control proves the refusal is real AND specific. Two
    different faults share one exit code -- the changeset control below the
    release-gate job documents exiting identically with and without its
    poison -- so the control must require the message that names the lockstep
    failure, and the failure count that proves it failed for one reason."""
    control = named_step(
        workflow_job("release-gate"),
        "Poison control - a drifted manifest version must be rejected",
    )
    check(
        "CI carries the release-gate poison control",
        bool(control),
        "no such step found under the release-gate job",
    )
    check(
        "the control runs the SHIPPED gate against the planted tree",
        "python scripts/release_gate.py --root" in control,
        control,
    )
    check(
        "the control requires the lockstep-specific message, not only a non-zero exit",
        "'version drift'" in control,
        control,
    )
    check(
        "the control requires the refusal to name the drifted plugin",
        "control-plugin-drifted" in control,
        control,
    )
    check(
        "the control requires a single-reason failure, not incidental breakage",
        "1 stale surface(s)" in control,
        control,
    )


def case_control_tree_is_temporary_not_committed() -> None:
    """Criterion 9: a committed breaching fixture would sit inside the guarded
    tree and turn the real run permanently red, buying back green with an
    exclusion list - the hole the format gate's control comment describes."""
    control = named_step(
        workflow_job("release-gate"),
        "Poison control - a drifted manifest version must be rejected",
    )
    check(
        "the control builds its breaching tree under RUNNER_TEMP",
        'tree="$RUNNER_TEMP/' in control,
        control,
    )
    tracked = subprocess.run(
        ["git", "ls-files", "scripts/fixtures"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    ).stdout
    check(
        "no release-gate fixture tree is committed under scripts/fixtures",
        "release" not in tracked.lower(),
        tracked,
    )


def main() -> None:
    cases = (
        case_lockstep_passes,
        case_declared_but_different_version_is_refused,
        case_missing_declaration_is_refused,
        case_every_failure_reported_in_one_run,
        case_absent_package_fails_closed,
        case_unparseable_package_fails_closed,
        case_versionless_package_fails_closed,
        case_absent_manifest_fails_closed,
        case_unparseable_manifest_fails_closed,
        case_shape_broken_manifest_fails_closed,
        case_zero_plugins_rejected,
        case_write_derives_every_entry_from_the_package,
        case_write_is_idempotent,
        case_write_fails_closed_on_unreadable_inputs,
        case_live_tree_in_lockstep,
        case_ci_runs_the_same_argumentless_command,
        case_ci_job_is_non_blocking_and_on_every_pull_request,
        case_ci_control_drives_the_gate_red_for_the_right_reason,
        case_control_tree_is_temporary_not_committed,
    )
    for case in cases:
        case()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: release gate verified across {len(cases)} contract case(s) - "
        "seeded trees, the live tree, and the CI wiring - every refusal "
        "asserting its own message, never only a non-zero exit."
    )


if __name__ == "__main__":
    main()
