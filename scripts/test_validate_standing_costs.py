#!/usr/bin/env python3
"""Suite for validate_standing_costs.py, including the committed poison fixture.

Every rejection case runs the real entrypoint against a real tree rather than a
stubbed one.  The poison fixture carries a deliberately wrong figure; the
conforming baseline runs against the live published tree.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_standing_costs.py"
REPO_ROOT = SCRIPT_DIR.parent
POISON = SCRIPT_DIR / "fixtures" / "standing-cost-drift"

sys.path.insert(0, str(SCRIPT_DIR))

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_checker(root: Path, *, use_snapshot: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(CHECKER), "--root", str(root)]
    if use_snapshot:
        command.append("--snapshot")
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
    )


CONFORMING_EVIDENCE = (
    "# EVIDENCE - fixture\n\n"
    "| Field | Value |\n|---|---|\n"
    "| **Occasions counted** | 0 - fixture card, no occurrence to count. RECURRENCE-THIN. |\n"
    "| **Dispatches recorded** | No recorded dispatch, fixture counter, measured 2026-01-01. |\n"
    "| **Re-screen trigger** | Fixture; never screened, never re-screened. |\n"
)


def write_card(
    root: Path, name: str, standing_cost_line: str, skill_md_content: str
) -> Path:
    card = root / "skills" / "engineering" / name
    card.mkdir(parents=True)
    (card / "SKILL.md").write_text(skill_md_content, encoding="utf-8", newline="")
    evidence = CONFORMING_EVIDENCE + f"| **Standing cost** | {standing_cost_line} |\n"
    (card / "EVIDENCE.md").write_text(evidence, encoding="utf-8", newline="")
    return card


def write_snapshot(root: Path, *, version: str = "0.3.0") -> None:
    scripts = root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    snapshot = dict(STANDING_COSTS)
    snapshot["skill_harness_version"] = version
    (scripts / "standing-costs.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8", newline=""
    )


# --- Load real card data for temp-tree tests ---

REAL_SKILL_MD = REPO_ROOT / "skills" / "engineering" / "clirunner-env" / "SKILL.md"
STANDING_COSTS = json.loads(
    (SCRIPT_DIR / "standing-costs.json").read_text(encoding="utf-8")
)
REAL_CLIRUNNER_TOKENS = STANDING_COSTS["cards"]["clirunner-env"]["standing_cost_tokens"]
REAL_CLIRUNNER_SKILL_MD = REAL_SKILL_MD.read_text(encoding="utf-8")
# Extract the real standing cost line from the real card for reconstruction
REAL_CLIRUNNER_EVIDENCE_LINE = (
    f"Description: {REAL_CLIRUNNER_TOKENS} tokens, measured by "
    f"`skill-harness skill audit` (skill-harness 0.3.0, 2026-09-22). "
    f"Body 5,866 B (measured 2026-08-24), loaded only on retrieval."
)


# --- Cases ---


def case_committed_poison_is_red() -> None:
    """The committed fixture card states 999 tokens; the audit says 21."""
    result = run_checker(POISON)
    check(
        "committed poison fixture is rejected",
        result.returncode != 0,
        f"stdout: {result.stdout}, stderr: {result.stderr}",
    )
    check(
        "rejection names the card",
        "standing-cost-drift-card" in result.stderr,
        result.stderr,
    )
    check(
        "rejection names stated number",
        "999" in result.stderr,
        result.stderr,
    )


def case_conforming_tree_is_green() -> None:
    """The published tree passes the check."""
    result = run_checker(REPO_ROOT)
    check(
        "live tree passes",
        result.returncode == 0,
        f"stdout: {result.stdout}, stderr: {result.stderr}",
    )


def case_snapshot_fallback_is_green() -> None:
    """The CI fallback validates the published tree without skill-harness."""
    result = run_checker(REPO_ROOT, use_snapshot=True)
    check(
        "published tree passes through snapshot fallback",
        result.returncode == 0 and "via standing-costs.json" in result.stdout,
        f"stdout: {result.stdout}, stderr: {result.stderr}",
    )


def case_wrong_figure_in_temp_tree() -> None:
    """A temp tree with the real SKILL.md but a wrong figure is rejected."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        wrong_tokens = REAL_CLIRUNNER_TOKENS + 999
        wrong_line = (
            f"Description: {wrong_tokens} tokens, measured by "
            f"`skill-harness skill audit` (skill-harness 0.3.0, 2026-09-22). "
            f"Body 5,866 B."
        )
        write_card(root, "clirunner-env", wrong_line, REAL_CLIRUNNER_SKILL_MD)
        write_snapshot(root)
        result = run_checker(root, use_snapshot=True)
        check(
            "wrong figure in temp tree is rejected",
            result.returncode != 0,
            f"stdout: {result.stdout}, stderr: {result.stderr}",
        )
        check(
            "rejection names the card",
            "clirunner-env" in result.stderr,
            result.stderr,
        )
        check(
            "rejection names both numbers",
            str(wrong_tokens) in result.stderr
            and str(REAL_CLIRUNNER_TOKENS) in result.stderr,
            result.stderr,
        )


def case_correct_figure_in_temp_tree() -> None:
    """A temp tree with the real SKILL.md and the correct figure passes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_card(root, "clirunner-env", REAL_CLIRUNNER_EVIDENCE_LINE, REAL_CLIRUNNER_SKILL_MD)
        write_snapshot(root)
        result = run_checker(root)
        check(
            "correct figure in temp tree passes",
            result.returncode == 0,
            f"stdout: {result.stdout}, stderr: {result.stderr}",
    )


def case_snapshot_version_is_pinned() -> None:
    """A snapshot measured by an unpinned harness version is rejected."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_card(root, "clirunner-env", REAL_CLIRUNNER_EVIDENCE_LINE, REAL_CLIRUNNER_SKILL_MD)
        write_snapshot(root, version="0.0.0")
        result = run_checker(root, use_snapshot=True)
        check(
            "unpinned snapshot version is rejected",
            result.returncode != 0
            and "expected pinned skill-harness 0.3.0, found '0.0.0'" in result.stderr,
            result.stderr,
        )


def _load(name: str):
    import importlib
    return importlib.import_module(name)


class _FakeRun:
    """Stand-in for subprocess.run: records kwargs, returns a fixed stdout."""

    def __init__(self, stdout):
        self.stdout = stdout
        self.calls: list[dict] = []

    def __call__(self, args, **kwargs):
        self.calls.append(kwargs)
        return subprocess.CompletedProcess(args, 0, stdout=self.stdout, stderr="")


def _with_fake(module, fake, fn):
    real = module.subprocess.run
    module.subprocess.run = fake
    try:
        return fn()
    finally:
        module.subprocess.run = real


def case_subprocess_decodes_utf8() -> None:
    """Every skill-harness call decodes UTF-8, not the locale code page (#359)."""
    card = Path("SKILL.md")
    for name in ("validate_standing_costs", "refresh_standing_costs"):
        module = _load(name)
        fake = _FakeRun("skill-harness, version 0.3.0")
        _with_fake(module, fake, module.installed_harness)
        fake_audit = _FakeRun("")
        try:
            _with_fake(module, fake_audit, lambda: module.audit_calibrated(["h"], card))
        except RuntimeError:
            pass
        calls = fake.calls[:1] + fake_audit.calls[:1]
        check(
            f"{name}: both subprocess calls pass encoding=utf-8, errors=replace",
            len(calls) == 2
            and all(c.get("encoding") == "utf-8" and c.get("errors") == "replace" for c in calls),
            repr(calls),
        )


def case_none_stdout_is_no_figure() -> None:
    """A None stdout takes the no-figure path instead of raising TypeError."""
    card = Path("SKILL.md")
    v = _load("validate_standing_costs")
    try:
        got = (_with_fake(v, _FakeRun(None), v.installed_harness),
               _with_fake(v, _FakeRun(None), lambda: v.audit_calibrated(["h"], card)))
        check("validate_standing_costs: None stdout is no figure", got == (None, None), repr(got))
    except TypeError as exc:
        check("validate_standing_costs: None stdout is no figure", False, repr(exc))
    r = _load("refresh_standing_costs")
    for label, fn in (("installed_harness", r.installed_harness),
                      ("audit_calibrated", lambda: r.audit_calibrated(["h"], card))):
        try:
            _with_fake(r, _FakeRun(None), fn)
            ok, detail = False, "returned"
        except RuntimeError:
            ok, detail = True, ""
        except TypeError as exc:
            ok, detail = False, repr(exc)
        check(f"refresh_standing_costs.{label}: None stdout raises RuntimeError", ok, detail)


DATE_POISON = SCRIPT_DIR / "fixtures" / "standing-cost-date-drift"


def case_stale_prose_date_is_red() -> None:
    """A README date that differs from calibrated_on is the single rejection (#472)."""
    for use_snapshot in (False, True):
        result = run_checker(DATE_POISON, use_snapshot=use_snapshot)
        lines = [l for l in result.stderr.splitlines() if l.startswith("  - ")]
        check(
            f"stale prose date fixture is rejected for that reason alone (snapshot={use_snapshot})",
            result.returncode != 0
            and lines == [
                "  - README.md:3: prose says 2026-09-22, "
                "standing-costs.json calibrated_on says 2026-10-19"
            ],
            result.stderr,
        )


def case_matching_prose_date_is_green() -> None:
    """The same fixture passes once its README carries calibrated_on."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "tree"
        shutil.copytree(DATE_POISON, root)
        readme = root / "README.md"
        readme.write_bytes(readme.read_bytes().replace(b"2026-09-22", b"2026-10-19"))
        result = run_checker(root, use_snapshot=True)
        check(
            "matching prose date passes",
            result.returncode == 0,
            f"stdout: {result.stdout}, stderr: {result.stderr}",
        )


def case_undated_prose_surface_is_red() -> None:
    """A prose surface that drops the dated sentence cannot silently pass."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "tree"
        shutil.copytree(DATE_POISON, root)
        (root / "README.md").write_text("# fixture\n", encoding="utf-8", newline="")
        result = run_checker(root, use_snapshot=True)
        check(
            "undated prose surface is rejected",
            result.returncode != 0
            and "README.md: no dated standing-cost sentence" in result.stderr,
            result.stderr,
        )


def case_refresher_writes_run_date() -> None:
    """The refresher stamps calibrated_on with the day it ran, not a literal."""
    r = _load("refresh_standing_costs")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_card(root, "clirunner-env", REAL_CLIRUNNER_EVIDENCE_LINE, REAL_CLIRUNNER_SKILL_MD)
        (root / "scripts").mkdir()
        fake = _FakeRun(
            "skill-harness, version 0.3.0\n"
            "Standing cost (mechanical): raw 40 tokens, calibrated 45 tokens\n"
        )
        _with_fake(r, fake, lambda: r.refresh(root))
        written = json.loads((root / "scripts" / "standing-costs.json").read_text(encoding="utf-8"))
        check(
            "refresher writes today's date as calibrated_on",
            written.get("calibrated_on") == date.today().isoformat(),
            repr(written.get("calibrated_on")),
        )


# --- Run all cases ---

case_committed_poison_is_red()
case_conforming_tree_is_green()
case_snapshot_fallback_is_green()
case_wrong_figure_in_temp_tree()
case_correct_figure_in_temp_tree()
case_snapshot_version_is_pinned()
case_subprocess_decodes_utf8()
case_none_stdout_is_no_figure()
case_stale_prose_date_is_red()
case_matching_prose_date_is_green()
case_undated_prose_surface_is_red()
case_refresher_writes_run_date()

if FAILURES:
    print(f"\nFAILED: {len(FAILURES)} case(s)")
    sys.exit(1)
else:
    print(f"\nAll cases passed (no failures)")
