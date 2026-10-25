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

from validate_standing_costs import PINNED_HARNESS_VERSION  # noqa: E402

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


def write_snapshot(root: Path, *, version: str = PINNED_HARNESS_VERSION) -> None:
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
    f"`skill-harness skill audit` (skill-harness {PINNED_HARNESS_VERSION}, 2026-09-22). "
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
            f"`skill-harness skill audit` (skill-harness {PINNED_HARNESS_VERSION}, 2026-09-22). "
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


def case_in_progress_card_is_skipped() -> None:
    """A card under skills/in-progress/ is not audited (#575 item 1).

    The planted card states a wrong figure and has no snapshot entry, so the
    check passes only while iter_skill_dirs skips the bucket.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_card(root, "clirunner-env", REAL_CLIRUNNER_EVIDENCE_LINE, REAL_CLIRUNNER_SKILL_MD)
        planted = write_card(
            root,
            "planted-unshipped-card",
            "Description: 999 tokens, measured by `skill-harness skill audit`.",
            REAL_CLIRUNNER_SKILL_MD,
        )
        parked = root / "skills" / "in-progress" / planted.name
        parked.parent.mkdir(parents=True)
        planted.rename(parked)
        write_snapshot(root)
        result = run_checker(root, use_snapshot=True)
        check(
            "a card under skills/in-progress/ is skipped",
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
            and f"expected pinned skill-harness {PINNED_HARNESS_VERSION}, found '0.0.0'" in result.stderr,
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
        fake = _FakeRun(f"skill-harness, version {PINNED_HARNESS_VERSION}")
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
    """A ledger date that differs from calibrated_on is the single rejection (#472)."""
    for use_snapshot in (False, True):
        result = run_checker(DATE_POISON, use_snapshot=use_snapshot)
        lines = [l for l in result.stderr.splitlines() if l.startswith("  - ")]
        check(
            f"stale prose date fixture is rejected for that reason alone (snapshot={use_snapshot})",
            result.returncode != 0
            and lines == [
                "  - docs/product/claims-ledger.md:3: prose says 2026-09-22, "
                "standing-costs.json calibrated_on says 2026-10-19"
            ],
            result.stderr,
        )


def case_matching_prose_date_is_green() -> None:
    """The same fixture passes once its ledger carries calibrated_on."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "tree"
        shutil.copytree(DATE_POISON, root)
        readme = root / "docs" / "product" / "claims-ledger.md"
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
        (root / "docs" / "product" / "claims-ledger.md").write_text("# fixture\n", encoding="utf-8", newline="")
        result = run_checker(root, use_snapshot=True)
        check(
            "undated prose surface is rejected",
            result.returncode != 0
            and "claims-ledger.md: no dated standing-cost sentence" in result.stderr,
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
            f"skill-harness, version {PINNED_HARNESS_VERSION}\n"
            "Standing cost (mechanical): raw 40 tokens, calibrated 45 tokens\n"
        )
        _with_fake(r, fake, lambda: r.refresh(root))
        written = json.loads((root / "scripts" / "standing-costs.json").read_text(encoding="utf-8"))
        check(
            "refresher writes today's date as calibrated_on",
            written.get("calibrated_on") == date.today().isoformat(),
            repr(written.get("calibrated_on")),
        )


COST_PARAGRAPH = (
    "Each card not marked \"by hand\" adds one line to every session: about 70 "
    "to 80 tokens, as `/context` counts it (Claude Code 2.1.305, measured "
    "2026-10-20, [#361](https://github.com/MrBinnacle/skills/issues/361))."
)


def readme_tree(tmp: str, paragraph: str) -> Path:
    """A date-fixture tree with a matching ledger date and the given README."""
    root = Path(tmp) / "tree"
    shutil.copytree(DATE_POISON, root)
    ledger = root / "docs" / "product" / "claims-ledger.md"
    ledger.write_bytes(ledger.read_bytes().replace(b"2026-09-22", b"2026-10-19"))
    (root / "README.md").write_text(
        "# fixture\n\n" + paragraph + "\n\nNext paragraph.\n", encoding="utf-8", newline=""
    )
    return root


def case_readme_cost_citation() -> None:
    """Each citation part dropped is red for that part alone; the whole is green (#536)."""
    drops = {
        "`/context`": ("`/context` counts it", "the host counts it"),
        "a Claude Code version": ("Claude Code 2.1.305, ", ""),
        "an ISO date": ("measured 2026-10-20, ", ""),
        "a link to the measurement": ("[#361](https://github.com/MrBinnacle/skills/issues/361)", "#361"),
    }
    with tempfile.TemporaryDirectory() as tmp:
        result = run_checker(readme_tree(tmp, COST_PARAGRAPH), use_snapshot=True)
        check("complete README cost citation is green", result.returncode == 0, result.stderr)
    for label, (old, new) in drops.items():
        assert old in COST_PARAGRAPH, label
        with tempfile.TemporaryDirectory() as tmp:
            result = run_checker(readme_tree(tmp, COST_PARAGRAPH.replace(old, new)), use_snapshot=True)
            lines = [l for l in result.stderr.splitlines() if l.startswith("  - ")]
            check(
                f"README cost paragraph without {label} is red for that part alone",
                result.returncode != 0
                and lines == [f"  - README.md: the session-cost paragraph does not name {label}"],
                result.stderr,
            )
    with tempfile.TemporaryDirectory() as tmp:
        result = run_checker(readme_tree(tmp, "No cost stated here."), use_snapshot=True)
        check(
            "README with no cost paragraph is red",
            result.returncode != 0 and "no paragraph states the per-skill session cost" in result.stderr,
            result.stderr,
        )
    live = run_checker(REPO_ROOT, use_snapshot=True)
    check("live README cost citation is green", live.returncode == 0, live.stderr)


# --- Run all cases ---

case_readme_cost_citation()
case_committed_poison_is_red()
case_conforming_tree_is_green()
case_snapshot_fallback_is_green()
case_wrong_figure_in_temp_tree()
case_correct_figure_in_temp_tree()
case_in_progress_card_is_skipped()
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
