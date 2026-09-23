#!/usr/bin/env python3
"""Suite for validate_standing_costs.py, including the committed poison fixture.

Every rejection case runs the real entrypoint against a real tree rather than a
stubbed one.  The poison fixture carries a deliberately wrong figure; the
conforming baseline runs against the live published tree.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
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
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
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


# --- Run all cases ---

case_committed_poison_is_red()
case_conforming_tree_is_green()
case_snapshot_fallback_is_green()
case_wrong_figure_in_temp_tree()
case_correct_figure_in_temp_tree()
case_snapshot_version_is_pinned()

if FAILURES:
    print(f"\nFAILED: {len(FAILURES)} case(s)")
    sys.exit(1)
else:
    print(f"\nAll cases passed (no failures)")
