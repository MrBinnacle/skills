#!/usr/bin/env python3
"""Suite for validate_conformance.py, including the poison controls.

A checker that has never rejected anything has not been shown to work, so every
rejection case here is built as a real tree on disk and run through the real
entrypoint as a subprocess. Calling a predicate in-process can stay green while
the command-line path is broken, and the command line is what CI runs.

Poison trees are built in a temp directory rather than checked in, for the same
reason the format gate's are: a committed breaching card would sit inside the
guarded set and turn the real run permanently red.

The two drift cases are the ones that matter. The SECURITY.md section and the
OBLIGATIONS list are the same statement written twice, and the failure the whole
design refuses is the two disagreeing without anything going red.

ASCII only, source and output both. Run with PYTHONUTF8=1.

Run directly:  python scripts/test_validate_conformance.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_conformance.py"
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))
import validate_conformance as conformance  # noqa: E402
import validate_scoreboard as scoreboard  # noqa: E402

FAILURES: list[str] = []
NOTES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def note(text: str) -> None:
    """Record something the suite did NOT verify. Never silent."""
    print(f"note {text}")
    NOTES.append(text)


def run_checker(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root), *extra],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Fixture trees: a minimal conforming repository, then breaches of it
# ---------------------------------------------------------------------------

CARDS = ("alpha-card", "beta-card")

SECURITY_STUB = """# Security policy

Everything this repository ships inside a skill folder is source you can read.

3. A skill's own `SKILL.md` names the scripts it asks the agent to run, so you
   can read them before you run them. `im-down` and `im-up` also ship their test
   suites.
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_tree(root: Path) -> None:
    """A tree that conforms on every card-scoped obligation.

    The repo-scoped obligations are deliberately NOT satisfied here: this stub
    has no scoreboard and no README, so O6 reports its own refusal. That is why
    the card-scoped breach cases assert on the reported cell and not only on
    the exit code.
    """
    write(root / "SECURITY.md", SECURITY_STUB)
    for name in CARDS:
        folder = root / "skills" / "engineering" / name
        write(folder / "SKILL.md", f"# {name}\n\nInstructions.\n")
        write(
            folder / "EVIDENCE.md",
            f"# EVIDENCE - {name}\n\n"
            "| Field | Value |\n|---|---|\n"
            "| **Screen result** | UNMEASURED. |\n"
            "| **Paired verdict** | UNMEASURED. |\n"
            "| **Evidence scope** | UNMEASURED — no receipt. |\n",
        )


def cell(stdout: str, card: str, oid: str) -> str:
    """The reported verdict for one card/obligation cell, from the real report."""
    lines = stdout.splitlines()
    for index, line in enumerate(lines):
        if line == card:
            for follow in lines[index + 1 :]:
                if not follow.startswith("  "):
                    break
                parts = follow.split()
                if len(parts) >= 2 and parts[1] == oid:
                    return parts[0]
    return "(cell not reported)"


# ---------------------------------------------------------------------------
# Green: the shape that must pass on the card-scoped obligations
# ---------------------------------------------------------------------------


def case_conforming_cards_pass(root: Path) -> None:
    make_tree(root)
    result = run_checker(root)
    for card in CARDS:
        for oid in ("O2", "O3", "O4"):
            check(
                f"conforming card {card} passes {oid}",
                cell(result.stdout, card, oid) == "PASS",
                result.stdout,
            )


def case_empty_root_refuses_rather_than_passing(root: Path) -> None:
    write(root / "SECURITY.md", SECURITY_STUB)
    result = run_checker(root)
    check(
        "a root with no published cards is refused, not silently green",
        result.returncode != 0 and "no published cards" in result.stderr,
        f"rc={result.returncode} err={result.stderr.strip()}",
    )


# ---------------------------------------------------------------------------
# Poison control 1: the historical breach shape -- a shipped script the card's
# SKILL.md does not name. This is the class the prototype rejected at the
# earlier tree, and the one obligation with a demonstrated rejection.
# ---------------------------------------------------------------------------


def case_unnamed_shipped_script_is_red(root: Path) -> None:
    make_tree(root)
    folder = root / "skills" / "engineering" / CARDS[0]
    write(folder / "helper.py", "print('hi')\n")
    result = run_checker(root)
    check(
        "a shipped script the SKILL.md does not name is FAIL on O3",
        cell(result.stdout, CARDS[0], "O3") == "FAIL",
        result.stdout,
    )
    check(
        "the unnamed script is named in the report",
        "helper.py" in result.stdout,
        result.stdout,
    )
    check(
        "an unnamed shipped script turns the run nonzero",
        result.returncode != 0,
        f"rc={result.returncode}",
    )
    check(
        "the rejection line says which edition rejected",
        "conformance v4" in result.stderr,
        result.stderr.strip(),
    )


def case_naming_the_script_clears_it(root: Path) -> None:
    """The same tree, one sentence added. A check that cannot go green either
    way is as useless as one that cannot go red."""
    make_tree(root)
    folder = root / "skills" / "engineering" / CARDS[0]
    write(folder / "helper.py", "print('hi')\n")
    write(folder / "SKILL.md", "# card\n\nRun `helper.py` to do the thing.\n")
    result = run_checker(root)
    check(
        "naming the script in SKILL.md clears O3",
        cell(result.stdout, CARDS[0], "O3") == "PASS",
        result.stdout,
    )


def case_tree_without_the_naming_sentence_is_red(root: Path) -> None:
    """The exact historical shape: the tree ships scripts and states no naming
    obligation at all. The carve-out is read out of SECURITY.md, so dropping
    the sentence loses the exemption rather than silently widening it."""
    make_tree(root)
    write(root / "SECURITY.md", "# Security policy\n\nNothing stated.\n")
    folder = root / "skills" / "engineering" / CARDS[0]
    write(folder / "helper.py", "print('hi')\n")
    write(folder / "SKILL.md", "# card\n\nRun `helper.py`.\n")
    result = run_checker(root)
    check(
        "a tree stating no naming obligation while shipping scripts is FAIL",
        cell(result.stdout, CARDS[0], "O3") == "FAIL",
        result.stdout,
    )


# ---------------------------------------------------------------------------
# Poison control 2: the planted undeclared format must still fail, and it must
# fail THROUGH the delegated format gate rather than through a second
# implementation of the vocabulary living here.
# ---------------------------------------------------------------------------


def case_planted_undeclared_format_is_red(root: Path) -> None:
    make_tree(root)
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(
        SCRIPT_DIR / "validate_skill_formats.py",
        root / "scripts" / "validate_skill_formats.py",
    )
    folder = root / "skills" / "engineering" / CARDS[0]
    write(folder / "install.sh", "#!/bin/sh\necho hi\n")
    result = run_checker(root)
    check(
        "a planted undeclared format turns the run nonzero",
        result.returncode != 0,
        f"rc={result.returncode} {result.stdout}",
    )
    check(
        "the planted file is reported under O1",
        "O1" in result.stdout and "install.sh" in result.stdout,
        result.stdout,
    )


def case_o1_agrees_with_the_standalone_format_gate(root: Path) -> None:
    """Delegation is only real if the two instruments cannot disagree."""
    gate = SCRIPT_DIR / "validate_skill_formats.py"
    make_tree(root)
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(gate, root / "scripts" / "validate_skill_formats.py")

    clean_gate = subprocess.run(
        [sys.executable, str(gate), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    check(
        "O1 and the standalone gate agree a clean tree is clean",
        conformance.check_declared_formats(root).verdict == "PASS"
        and clean_gate.returncode == 0,
        f"gate={clean_gate.returncode} {clean_gate.stderr.strip()}",
    )

    write(root / "skills" / "engineering" / CARDS[0] / "payload.sh", "#!/bin/sh\n")
    dirty_gate = subprocess.run(
        [sys.executable, str(gate), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    check(
        "O1 and the standalone gate agree a dirty tree is dirty",
        conformance.check_declared_formats(root).verdict == "FAIL"
        and dirty_gate.returncode != 0,
        f"gate={dirty_gate.returncode}",
    )


def case_missing_format_gate_is_cannot_check_not_pass(root: Path) -> None:
    """A tree without the delegated gate must record the absence, not skip it.

    The prototype's own note: a conformance check that assumes its helpers are
    present would crash or, worse, go quietly green.
    """
    make_tree(root)
    result = conformance.check_declared_formats(root)
    check(
        "an absent format gate is CANNOT-CHECK, never PASS",
        result.verdict == "CANNOT-CHECK",
        f"{result.verdict} {result.detail}",
    )


# ---------------------------------------------------------------------------
# CANNOT-CHECK is a distinct state, not a quiet pass
# ---------------------------------------------------------------------------


def case_cannot_check_is_distinct_from_pass(root: Path) -> None:
    make_tree(root)
    result = run_checker(root)
    for card in CARDS:
        check(
            f"O5 is reported CANNOT-CHECK on {card}, not PASS",
            cell(result.stdout, card, "O5") == "CANNOT-CHECK",
            result.stdout,
        )
    counted = re.search(
        r"(\d+) PASS, (\d+) FAIL, (\d+) CANNOT-CHECK", result.stdout + result.stderr
    )
    check(
        "the summary counts the three states separately",
        counted is not None,
        result.stdout + result.stderr,
    )
    if counted:
        check(
            "the CANNOT-CHECK count is nonzero and not folded into PASS",
            int(counted.group(3)) >= len(CARDS),
            counted.group(0),
        )


def case_a_clean_run_says_cannot_check_is_not_a_pass() -> None:
    """On the live tree the run is green. The green line must still say how
    many cells it did not verify."""
    result = run_checker(REPO_ROOT)
    check(
        "the passing line states that CANNOT-CHECK is not a pass",
        result.returncode == 0 and "CANNOT-CHECK is not a pass" in result.stdout,
        result.stdout + result.stderr,
    )


def case_o5_is_never_pass_on_the_live_tree() -> None:
    """O5 cannot be satisfied from inside this repository. If a change ever
    makes it green here, that is a false promise of a CI check, not progress."""
    report = conformance.evaluate(REPO_ROOT)
    verdicts = {report.per_card[c.name]["O5"].verdict for c in report.cards}
    check(
        "O5 is CANNOT-CHECK on every published card",
        verdicts == {"CANNOT-CHECK"},
        str(verdicts),
    )


# ---------------------------------------------------------------------------
# O5 with --harness-root: receipt agreement checks
# ---------------------------------------------------------------------------

import hashlib


def skill_id_for(folder: Path) -> str:
    """SHA-256 hex of a card folder's SKILL.md bytes."""
    return hashlib.sha256(
        (folder / "SKILL.md").read_bytes()
    ).hexdigest()


def receipt_json(
    skill_name: str,
    skill_id: str,
    verdict: str,
    source_date: str = "2026-07-21",
    harness_version: str = "0.2.3",
    extra: dict | None = None,
) -> str:
    """A minimal SERS receipt as a JSON string.

    `extra` overlays fields the evidence-scope check reads: verdict_scope
    (object), currentness (object or null), subject_identity (object or null).
    """
    import json as _json

    data: dict = {
        "sers_version": "1.6.0",
        "skill_name": skill_name,
        "verdict": verdict,
        "cut_sub_reason": None,
        "unmeasured_sub_reason": None,
        "value_class": "trap-discipline",
        "wrong_instrument": False,
        "declared_synthetic_control": False,
        "evidence_admissibility": {"status": "admissible"},
        "cost": {
            "standing_tokens": {"refusal": "not_instrumented"},
            "fired_tokens": {"refusal": "not_instrumented"},
            "aux_tokens": {"refusal": "not_applicable"},
        },
        "instrument_identity": {
            "extractor_model": "test-model",
            "prompt_fingerprint": "test-fp",
            "schema_fingerprint": "test-sf",
        },
        "source": {"prose_path": "README.md", "date": source_date},
        "summary": f"Test receipt for {skill_name}.",
        "subject_identity": {
            "skill_id": skill_id,
            "harness_version": harness_version,
            "metric_version": "0.3.0",
            "implementation_hash": "a" * 64,
            "arms": ["null", "full"],
        },
        "currentness": None,
    }
    if extra:
        data.update(extra)
    return _json.dumps(data, indent=2)


def sers_keep_scope_fixture(
    *,
    delivery_mechanism: str | None = "hook-blocked",
    carried_forward: bool = False,
    skill_id: str | None = None,
    task_family: str = "trap-discipline",
) -> dict:
    """R2-shaped SERS 1.6.0 KEEP receipt for evidence-scope cases.

    Models skill-harness tests/fixtures/sers/poison_keep_*.json: top-level
    verdict, verdict_scope as an object with model_id / task_family /
    tested_at (and delivery_mechanism in the standard case), currentness as
    an object or null, subject_identity as an object or null, sers_version
    1.6.0. `delivery_mechanism=None` omits the field so the derivation must
    read `unknown delivery`. Carried-forward sets currentness.state and
    subject_identity.subject_model; SERS receipts carry no
    scope_carried_forward key.
    """
    scope = {
        "model_id": "claude-sonnet-5",
        "harness_version": "0.3.0",
        "fixture_version": "abc123",
        "task_id": "test-task",
        "tested_at": "2026-09-22T00:00:00Z",
        "task_family": task_family,
        "estimand": "treatment-policy",
    }
    if delivery_mechanism is not None:
        scope["delivery_mechanism"] = delivery_mechanism
    receipt: dict = {
        "sers_version": "1.6.0",
        "skill_name": "alpha-card",
        "verdict": "KEEP",
        "cut_sub_reason": None,
        "unmeasured_sub_reason": None,
        "value_class": "transformative-lift",
        "evidence_admissibility": {"status": "not_applicable"},
        "cost": {
            "standing_tokens": {"refusal": "not_applicable"},
            "fired_tokens": {"refusal": "not_applicable"},
            "aux_tokens": {"refusal": "not_applicable"},
        },
        "instrument_identity": {
            "extractor_model": {"refusal": "not_applicable"},
            "prompt_fingerprint": "a",
            "schema_fingerprint": "b",
        },
        "source": {"prose_path": "README.md"},
        "summary": "SERS 1.6.0 KEEP fixture for evidence-scope derivation.",
        "verdict_scope": scope,
        "currentness": None,
        "subject_identity": None,
    }
    if carried_forward:
        receipt["currentness"] = {
            "state": "CARRIED_FORWARD",
            "basis": "SENTINEL_PASS",
        }
        receipt["subject_identity"] = {
            "skill_id": skill_id or "b" * 64,
            "harness_version": "0.3.0",
            "metric_version": "0.3.0",
            "implementation_hash": "c" * 64,
            "arms": ["null", "full"],
            "subject_model": "claude-sonnet-6",
        }
    elif skill_id is not None:
        receipt["subject_identity"] = {
            "skill_id": skill_id,
            "harness_version": "0.3.0",
            "metric_version": "0.3.0",
            "implementation_hash": "c" * 64,
            "arms": ["null", "full"],
        }
    return receipt


def expected_scope_for_receipt(verdict: str, extra: dict | None = None) -> str:
    """The Evidence scope sentence the closed set derives from one receipt.

    Delegates to conformance.expected_evidence_scope so the suite cannot
    drift from the checker it grades.
    """
    receipt: dict = {"verdict": verdict}
    if extra:
        receipt.update(extra)
    return conformance.expected_evidence_scope([receipt])


def write_evidence_scope(folder: Path, value: str) -> None:
    """Set or replace the card's Evidence scope row, keeping other rows.

    An empty `value` writes an empty cell (`| **Evidence scope** |  |`),
    which the checker refuses with its own empty-row message.
    """
    evidence = folder / "EVIDENCE.md"
    text = evidence.read_text(encoding="utf-8")
    row = f"| **Evidence scope** | {value} |\n"
    if "| **Evidence scope** |" in text:
        lines = []
        for line in text.splitlines(keepends=True):
            if line.startswith("| **Evidence scope** |"):
                lines.append(row)
            else:
                lines.append(line)
        evidence.write_text("".join(lines), encoding="utf-8")
        return
    lines = text.splitlines(keepends=True)
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and line.startswith("| **Paired verdict** |"):
            out.append(row)
            inserted = True
    if not inserted:
        out.append(row)
    evidence.write_text("".join(out), encoding="utf-8")


def make_receipt_tree(
    root: Path,
    card_name: str,
    verdict: str = "CANT_TELL_YET",
    receipt_filename: str | None = None,
    source_date: str = "2026-07-21",
    harness_version: str = "0.2.3",
    skill_id_override: str | None = None,
    extra: dict | None = None,
    scope_override: str | None = None,
    receipt_data: dict | None = None,
) -> Path:
    """Build a tree with one card carrying a Receipt clause and a harness root.

    Returns the harness root path. By default the card's Evidence scope row is
    written to the sentence the closed set derives from this receipt, so a case
    that wants a WRONG scope uses `scope_override`. `receipt_data` writes a
    full receipt object (R2 SERS shape) instead of the minimal JSON.
    """
    folder = root / "skills" / "engineering" / card_name
    skill_id = skill_id_override or skill_id_for(folder)
    fname = receipt_filename or f"receipt-{card_name}.json"
    harness_root = root / "harness"
    receipt_dir = harness_root / "docs" / "sers" / "receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    if receipt_data is not None:
        import json as _json

        data = dict(receipt_data)
        si = data.get("subject_identity")
        if not isinstance(si, dict):
            # R2 lets subject_identity be null on a pure scope-line fixture;
            # O5 still requires a skill_id on any receipt a card links, so
            # the tree writer injects one. The drift test never goes through
            # this path -- it renders the fixture through the harness alone.
            data["subject_identity"] = {
                "skill_id": skill_id,
                "harness_version": harness_version,
                "metric_version": "0.3.0",
                "implementation_hash": "c" * 64,
                "arms": ["null", "full"],
            }
        elif skill_id_override is None:
            si = dict(si)
            si["skill_id"] = skill_id
            data["subject_identity"] = si
        (receipt_dir / fname).write_text(
            _json.dumps(data, indent=2), encoding="utf-8"
        )
        derived_receipt = data
    else:
        (receipt_dir / fname).write_text(
            receipt_json(card_name, skill_id, verdict, source_date, harness_version, extra),
            encoding="utf-8",
        )
        derived_receipt = {"verdict": verdict}
        if extra:
            derived_receipt.update(extra)
    evidence = folder / "EVIDENCE.md"
    evidence.write_text(
        f"# EVIDENCE - {card_name}\n\n"
        "| Field | Value |\n|---|---|\n"
        f'| **Screen result** | {verdict}. Receipt: `{fname}` |\n'
        "| **Paired verdict** | UNMEASURED. |\n",
        encoding="utf-8",
    )
    if scope_override is not None:
        write_evidence_scope(folder, scope_override)
    else:
        write_evidence_scope(
            folder, conformance.expected_evidence_scope([derived_receipt])
        )
    return harness_root


def case_o5_without_harness_root_is_cannot_check(root: Path) -> None:
    """Without --harness-root, O5 stays CANNOT-CHECK even if a receipt exists."""
    make_tree(root)
    make_receipt_tree(root, CARDS[0])
    result = run_checker(root)
    check(
        "O5 is CANNOT-CHECK on alpha-card without --harness-root",
        cell(result.stdout, CARDS[0], "O5") == "CANNOT-CHECK",
        result.stdout,
    )
    check(
        "O5 is CANNOT-CHECK on beta-card without --harness-root",
        cell(result.stdout, CARDS[1], "O5") == "CANNOT-CHECK",
        result.stdout,
    )


def case_o5_matching_receipt_is_pass(root: Path) -> None:
    """A matching card and receipt yield PASS on O5."""
    make_tree(root)
    harness_root = make_receipt_tree(root, CARDS[0])
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is PASS on alpha-card with a matching receipt",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )
    # beta-card has no receipt, still CANNOT-CHECK
    check(
        "O5 is CANNOT-CHECK on beta-card with no receipt",
        cell(result.stdout, CARDS[1], "O5") == "CANNOT-CHECK",
        result.stdout,
    )


def case_o5_matching_receipt_with_prose_is_pass(root: Path) -> None:
    """Opening verdict word only: prose between the verdict and Receipt must
    not be folded into the compared word. Live cards write that shape."""
    make_tree(root)
    harness_root = make_receipt_tree(root, CARDS[0], verdict="CANT_TELL_YET")
    folder = root / "skills" / "engineering" / CARDS[0]
    (folder / "EVIDENCE.md").write_text(
        "# EVIDENCE\n\n"
        "| Field | Value |\n|---|---|\n"
        "| **Screen result** | CANT_TELL_YET. Screened 2026-07-21 against "
        "this card's own registered screen; bare arm passed 3/3. "
        "Receipt: `receipt-alpha-card.json` in the measurement repo. "
        "Caveat bounds the number. |\n"
        "| **Paired verdict** | UNMEASURED. |\n"
        f"| **Evidence scope** | {expected_scope_for_receipt('CANT_TELL_YET')} |\n",
        encoding="utf-8",
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is PASS when prose sits between the opening verdict and Receipt",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )


def case_o5_matching_receipt_markdown_link_is_pass(root: Path) -> None:
    """Spec Receipt shape: [file.json](harness blob URL), not only backticks."""
    make_tree(root)
    harness_root = make_receipt_tree(root, CARDS[0], verdict="KEEP")
    folder = root / "skills" / "engineering" / CARDS[0]
    fname = "receipt-alpha-card.json"
    url = (
        "https://github.com/example/skill-harness/blob/abc123/"
        f"docs/sers/receipts/{fname}"
    )
    (folder / "EVIDENCE.md").write_text(
        "# EVIDENCE\n\n"
        "| Field | Value |\n|---|---|\n"
        f"| **Screen result** | KEEP. Receipt: [{fname}]({url}), "
        "dated 2026-07-21, harness 0.2.3. |\n"
        "| **Paired verdict** | UNMEASURED. |\n"
        f"| **Evidence scope** | {expected_scope_for_receipt('KEEP')} |\n",
        encoding="utf-8",
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is PASS on the spec markdown-link Receipt shape",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )


def case_o5_receipt_absent_is_fail(root: Path) -> None:
    """Condition 1: the linked receipt file is absent under the harness root."""
    make_tree(root)
    folder = root / "skills" / "engineering" / CARDS[0]
    # Write an EVIDENCE.md referencing a receipt that does not exist
    (folder / "EVIDENCE.md").write_text(
        "# EVIDENCE\n\n"
        "| Field | Value |\n|---|---|\n"
        '| **Screen result** | KEEP. Receipt: `nonexistent.json` |\n'
        "| **Paired verdict** | UNMEASURED. |\n",
        encoding="utf-8",
    )
    harness_root = root / "harness"
    harness_root.mkdir(parents=True, exist_ok=True)
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is FAIL on alpha-card when the receipt file is absent",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    check(
        "the failure message names the absent receipt",
        "absent" in result.stdout.lower() or "not found" in result.stdout.lower()
        or "nonexistent" in result.stdout,
        result.stdout,
    )
    check(
        "the run goes nonzero when O5 fails",
        result.returncode != 0,
        f"rc={result.returncode}",
    )


def case_o5_skill_id_mismatch_is_fail(root: Path) -> None:
    """Condition 2: the receipt's subject_identity.skill_id differs from
    sha256 of the card's SKILL.md bytes."""
    make_tree(root)
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        skill_id_override="b" * 64,  # wrong skill_id
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is FAIL on alpha-card when skill_id mismatches",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    check(
        "the failure message names skill_id",
        "skill_id" in result.stdout.lower(),
        result.stdout,
    )


def case_o5_verdict_mismatch_is_fail(root: Path) -> None:
    """Condition 3: the row's opening verdict word differs from the receipt's
    verdict."""
    make_tree(root)
    # The receipt says KEEP but the card's EVIDENCE.md says CANT_TELL_YET
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        verdict="KEEP",
    )
    # Overwrite EVIDENCE.md so the row opens with CANT_TELL_YET
    folder = root / "skills" / "engineering" / CARDS[0]
    (folder / "EVIDENCE.md").write_text(
        "# EVIDENCE\n\n"
        "| Field | Value |\n|---|---|\n"
        '| **Screen result** | CANT_TELL_YET. Receipt: `receipt-alpha-card.json` |\n'
        "| **Paired verdict** | UNMEASURED. |\n",
        encoding="utf-8",
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is FAIL on alpha-card when verdict mismatches",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    check(
        "the failure message names verdict",
        "verdict" in result.stdout.lower(),
        result.stdout,
    )


def case_o5_newer_receipt_exists_is_fail(root: Path) -> None:
    """Condition 4: a receipt with the same skill_id and a later source.date
    exists under the harness root that the row does not link."""
    make_tree(root)
    # The older receipt (linked by the card)
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        source_date="2026-07-21",
    )
    # A newer receipt (not linked) with the same skill_id
    folder = root / "skills" / "engineering" / CARDS[0]
    skill_id = skill_id_for(folder)
    receipt_dir = harness_root / "docs" / "sers" / "receipts"
    (receipt_dir / "newer-receipt.json").write_text(
        receipt_json(CARDS[0], skill_id, "KEEP", source_date="2026-08-15"),
        encoding="utf-8",
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is FAIL on alpha-card when a newer receipt exists",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    check(
        "the failure message names newer or later",
        "newer" in result.stdout.lower() or "later" in result.stdout.lower()
        or "stale" in result.stdout.lower(),
        result.stdout,
    )


def receipt_json_1_0_0(skill_name: str, verdict: str) -> str:
    """A SERS 1.0.0 receipt: no subject_identity block, because 1.0.0 predates it.

    This is the shape the rotation pass keeps as a history link, and the shape
    condition 2 cannot parse.
    """
    import json as _json

    return _json.dumps(
        {
            "sers_version": "1.0.0",
            "skill_name": skill_name,
            "verdict": verdict,
            "value_class": "trap-discipline",
            "source": {"prose_path": "README.md", "date": "2026-07-20"},
            "summary": f"Pre-subject_identity receipt for {skill_name}.",
        },
        indent=2,
    )


def make_1_0_0_receipt_tree(root: Path, card_name: str, declare: bool) -> Path:
    """One card whose only Receipt clause links a 1.0.0 receipt.

    `declare` decides whether the row types that link `not current:`. That one
    difference is the whole subject of these two cases.
    """
    harness_root = root / "harness"
    receipt_dir = harness_root / "docs" / "sers" / "receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    fname = f"legacy-{card_name}.json"
    (receipt_dir / fname).write_text(
        receipt_json_1_0_0(card_name, "CANT_TELL_YET"), encoding="utf-8"
    )
    clause = f"Receipt: `{fname}`, dated 2026-07-20, harness 1.0.0."
    if declare:
        clause += " wrong_instrument (trap-discipline); not current: no_skill_id."
    folder = root / "skills" / "engineering" / card_name
    (folder / "EVIDENCE.md").write_text(
        f"# EVIDENCE - {card_name}\n\n"
        "| Field | Value |\n|---|---|\n"
        f"| **Screen result** | CANT_TELL_YET. {clause} |\n"
        "| **Paired verdict** | UNMEASURED. |\n"
        f"| **Evidence scope** | {expected_scope_for_receipt('CANT_TELL_YET')} |\n",
        encoding="utf-8",
    )
    return harness_root


def case_o5_history_receipt_is_pass(root: Path) -> None:
    """A row that declares its own receipt `not current:` links history.

    The rotation pass (AGENTS.md step 5) instructs a card to keep that link. The
    card cannot satisfy both the ritual and a validator that parses the link as a
    current claim, so the history declaration retires conditions 1 to 3.
    """
    make_tree(root)
    harness_root = make_1_0_0_receipt_tree(root, CARDS[0], declare=True)
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is PASS when the row declares its 1.0.0 receipt not current",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )
    check(
        "the PASS reason names the history link",
        "history" in result.stdout.lower(),
        result.stdout,
    )


def case_o5_undeclared_1_0_0_receipt_is_fail(root: Path) -> None:
    """The negative control, and the reason the check exists.

    Same receipt, same card, same harness root. The row simply does not declare
    it not current. A fix that skips condition 2 for every unparsable receipt
    passes this case only by accident; a fix that keys on the declaration fails
    it, which is what the row is owed.
    """
    make_tree(root)
    harness_root = make_1_0_0_receipt_tree(root, CARDS[0], declare=False)
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 is FAIL on an undeclared receipt with no subject_identity",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    check(
        "the failure message names subject_identity",
        "subject_identity" in result.stdout,
        result.stdout,
    )


def case_o5_history_link_does_not_mask_a_newer_receipt(root: Path) -> None:
    """Condition 4 still fires alongside a history link.

    Skipping conditions 1 to 3 must not turn condition 4 off: a row carrying a
    history link plus a current link is still owed the newer-receipt check on the
    current one.
    """
    make_tree(root)
    harness_root = make_receipt_tree(root, CARDS[0], source_date="2026-07-21")
    folder = root / "skills" / "engineering" / CARDS[0]
    skill_id = skill_id_for(folder)
    receipt_dir = harness_root / "docs" / "sers" / "receipts"
    (receipt_dir / "legacy-alpha.json").write_text(
        receipt_json_1_0_0(CARDS[0], "CANT_TELL_YET"), encoding="utf-8"
    )
    (receipt_dir / "newer-receipt.json").write_text(
        receipt_json(CARDS[0], skill_id, "KEEP", source_date="2026-08-15"),
        encoding="utf-8",
    )
    (folder / "EVIDENCE.md").write_text(
        f"# EVIDENCE - {CARDS[0]}\n\n"
        "| Field | Value |\n|---|---|\n"
        "| **Screen result** | CANT_TELL_YET. Receipt: `legacy-alpha.json`, "
        "dated 2026-07-20, harness 1.0.0. not current: no_skill_id. |\n"
        "| **Paired verdict** | CANT_TELL_YET. Receipt: "
        f"`receipt-{CARDS[0]}.json` |\n"
        f"| **Evidence scope** | {expected_scope_for_receipt('CANT_TELL_YET')} |\n",
        encoding="utf-8",
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "O5 still FAILs on a newer unlinked receipt beside a history link",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )


# ---------------------------------------------------------------------------
# Evidence scope (#354): the closed set the row must state, derived from the
# receipt O5 resolves. Each fixture runs the real entrypoint; each refusal
# names the card and the row. KEEP fixtures use the SERS 1.6.0 shape (R2) and
# the skill-harness _scope_line wording (R1).
# ---------------------------------------------------------------------------

import os


def o5_detail(stdout: str, card: str) -> str:
    """The detail line reported for one card's O5 cell."""
    lines = stdout.splitlines()
    for index, line in enumerate(lines):
        if line == card:
            for follow in lines[index + 1 :]:
                if not follow.startswith("  "):
                    break
                parts = follow.split(None, 3)
                if len(parts) >= 2 and parts[1] == "O5":
                    return follow
    return "(cell not reported)"


def case_evidence_scope_no_receipt_wrong_sentence_is_fail(root: Path) -> None:
    """No-receipt card whose row is anything but the UNMEASURED sentence."""
    make_tree(root)
    folder = root / "skills" / "engineering" / CARDS[0]
    write_evidence_scope(folder, "Shown here: nothing measured.")
    result = run_checker(root)
    check(
        "a no-receipt card with a wrong Evidence scope sentence is FAIL",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    check(
        "the refusal names the card and the Evidence scope row",
        CARDS[0] in o5_detail(result.stdout, CARDS[0])
        and "Evidence scope" in o5_detail(result.stdout, CARDS[0]),
        o5_detail(result.stdout, CARDS[0]),
    )
    check(
        "the run goes nonzero when Evidence scope is wrong",
        result.returncode != 0,
        f"rc={result.returncode}",
    )


def case_evidence_scope_no_receipt_correct_sentence_is_cant(root: Path) -> None:
    """The green half: a correct UNMEASURED sentence on a no-receipt card."""
    make_tree(root)
    result = run_checker(root)
    check(
        "a no-receipt card with the UNMEASURED sentence is CANNOT-CHECK (receipt), not FAIL",
        cell(result.stdout, CARDS[0], "O5") == "CANNOT-CHECK",
        result.stdout,
    )
    check(
        "the CANT detail is the receipt-availability reason, not a scope refusal",
        "Evidence scope" not in o5_detail(result.stdout, CARDS[0]),
        o5_detail(result.stdout, CARDS[0]),
    )


def case_evidence_scope_cant_tell_yet_shown_here_is_fail(root: Path) -> None:
    """A CANT_TELL_YET receipt with a row reading `Shown here: ...`."""
    make_tree(root)
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        verdict="CANT_TELL_YET",
        scope_override="Shown here: the bare arm passed.",
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "a CANT_TELL_YET receipt with a Shown here: row is FAIL on O5",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    detail = o5_detail(result.stdout, CARDS[0])
    check(
        "the refusal names the card, the Evidence scope row and both sentences",
        CARDS[0] in detail
        and "Evidence scope" in detail
        and "Shown here" in detail
        and "NOT DEMONSTRATED" in detail,
        detail,
    )


def case_evidence_scope_keep_with_scope_exact_passes(root: Path) -> None:
    """KEEP receipt with verdict_scope (SERS object): the exact scope line passes."""
    make_tree(root)
    receipt = sers_keep_scope_fixture()
    expected = conformance.expected_evidence_scope([receipt])
    check(
        "the standard KEEP derivation is the harness _scope_line sentence",
        expected.startswith("Shown here: effect on trap-discipline, claude-sonnet-5")
        and "Not shown: other task families" in expected,
        expected,
    )
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        verdict="KEEP",
        receipt_data=receipt,
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "KEEP + verdict_scope with the exact scope line passes O5",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )


def case_evidence_scope_keep_one_word_change_is_fail(root: Path) -> None:
    """The same receipt, one word of the scope line changed: refused."""
    make_tree(root)
    receipt = sers_keep_scope_fixture()
    expected = conformance.expected_evidence_scope([receipt])
    bad_row = expected.replace("trap-discipline", "trap discipline")
    check(
        "the one-word mutant differs from the exact sentence",
        bad_row != expected and "trap discipline" in bad_row,
        f"expected={expected!r} bad={bad_row!r}",
    )
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        verdict="KEEP",
        receipt_data=receipt,
        scope_override=bad_row,
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "KEEP + verdict_scope with a one-word scope-line change is FAIL",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    detail = o5_detail(result.stdout, CARDS[0])
    check(
        "the one-word refusal names Evidence scope and both sentences",
        "Evidence scope" in detail
        and "Shown here" in detail
        and "trap-discipline" in detail,
        detail,
    )


def case_evidence_scope_keep_without_delivery_is_unknown_delivery(root: Path) -> None:
    """A KEEP fixture with delivery_mechanism absent yields `unknown delivery`."""
    make_tree(root)
    receipt = sers_keep_scope_fixture(delivery_mechanism=None)
    expected = conformance.expected_evidence_scope([receipt])
    check(
        "a KEEP receipt without delivery_mechanism reads unknown delivery",
        "unknown delivery" in expected and "hook-blocked" not in expected,
        expected,
    )
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        verdict="KEEP",
        receipt_data=receipt,
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "KEEP + missing delivery_mechanism with the unknown delivery sentence passes O5",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )


def case_evidence_scope_keep_without_scope_is_unscoped(root: Path) -> None:
    """KEEP receipt with no verdict_scope object -> the UNSCOPED sentence."""
    make_tree(root)
    harness_root = make_receipt_tree(root, CARDS[0], verdict="KEEP")
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "KEEP without verdict_scope with the UNSCOPED sentence passes",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )
    folder = root / "skills" / "engineering" / CARDS[0]
    write_evidence_scope(
        folder,
        "Shown here: effect on invented, invented, invented, measured invented.",
    )
    bad = run_checker(root, "--harness-root", str(harness_root))
    check(
        "KEEP without verdict_scope with a Shown here: sentence is FAIL",
        cell(bad.stdout, CARDS[0], "O5") == "FAIL",
        bad.stdout,
    )
    detail = o5_detail(bad.stdout, CARDS[0])
    check(
        "the UNSCOPED refusal names the row and the SERS before 1.6.0 reason",
        "Evidence scope" in detail and "SERS before 1.6.0" in detail,
        detail,
    )


def case_evidence_scope_carried_forward_beats_standard(root: Path) -> None:
    """Carried-forward KEEP (currentness.state): the carried-forward sentence
    passes, the standard sentence is refused. SERS carries no
    scope_carried_forward key; currentness.state decides."""
    make_tree(root)
    receipt = sers_keep_scope_fixture(carried_forward=True)
    carried = conformance.expected_evidence_scope([receipt])
    standard = conformance.expected_evidence_scope(
        [{**receipt, "currentness": None}]
    )
    check(
        "the carried-forward derivation is the harness sentinel-rule sentence",
        carried.startswith("demonstrated on claude-sonnet-5")
        and "carried forward to claude-sonnet-6 under the sentinel rule" in carried
        and "not re-validated on claude-sonnet-6" in carried,
        carried,
    )
    check(
        "the standard sentence differs from the carried-forward sentence",
        standard.startswith("Shown here:") and standard != carried,
        f"standard={standard!r} carried={carried!r}",
    )
    harness_root = make_receipt_tree(
        root,
        CARDS[0],
        verdict="KEEP",
        receipt_data=receipt,
    )
    result = run_checker(root, "--harness-root", str(harness_root))
    check(
        "carried-forward KEEP with the carried-forward sentence passes",
        cell(result.stdout, CARDS[0], "O5") == "PASS",
        result.stdout,
    )
    folder = root / "skills" / "engineering" / CARDS[0]
    write_evidence_scope(folder, standard)
    bad = run_checker(root, "--harness-root", str(harness_root))
    check(
        "carried-forward KEEP with the standard sentence is FAIL",
        cell(bad.stdout, CARDS[0], "O5") == "FAIL",
        bad.stdout,
    )
    detail = o5_detail(bad.stdout, CARDS[0])
    check(
        "the refusal names Evidence scope and both sentence shapes",
        "Evidence scope" in detail
        and "carried forward" in detail
        and "Shown here" in detail,
        detail,
    )


def case_evidence_scope_empty_row_is_refused_with_its_own_message(root: Path) -> None:
    """R4: an empty Evidence scope row is refused with its own message.

    Deleting the `if not stated:` branch in evidence_scope_breaches leaves
    this case red: the checker then reports the mismatch sentence instead of
    the empty-row refusal.
    """
    make_tree(root)
    folder = root / "skills" / "engineering" / CARDS[0]
    write_evidence_scope(folder, "")
    result = run_checker(root)
    check(
        "an empty Evidence scope row is FAIL on O5",
        cell(result.stdout, CARDS[0], "O5") == "FAIL",
        result.stdout,
    )
    detail = o5_detail(result.stdout, CARDS[0])
    check(
        "the empty-row refusal names the card and uses the empty-row message",
        CARDS[0] in detail
        and "EVIDENCE.md states no Evidence scope row" in detail
        and "empty row is the same refusal" in detail,
        detail,
    )


def case_evidence_scope_constants_are_the_closed_set() -> None:
    """The constants equal the closed-set sentences #353 and R1 quote.

    One word of a constant is a red drift. This case pins the three fixed
    sentences and the two KEEP templates without needing a harness checkout;
    the render-based drift test below covers the harness comparison.
    """
    check(
        "SCOPE_NO_RECEIPT is the closed-set no-receipt sentence",
        conformance.SCOPE_NO_RECEIPT == "UNMEASURED — no receipt.",
        conformance.SCOPE_NO_RECEIPT,
    )
    check(
        "SCOPE_NOT_DEMONSTRATED_FMT names the verdict and the no-effect clause",
        conformance.SCOPE_NOT_DEMONSTRATED_FMT
        == "NOT DEMONSTRATED — receipt verdict {verdict}; no effect is shown.",
        conformance.SCOPE_NOT_DEMONSTRATED_FMT,
    )
    check(
        "SCOPE_UNSCOPED is the closed-set scopeless-KEEP sentence",
        conformance.SCOPE_UNSCOPED
        == "UNSCOPED — the KEEP receipt carries no verdict_scope (SERS before 1.6.0).",
        conformance.SCOPE_UNSCOPED,
    )
    check(
        "SCOPE_LINE_TEMPLATE is the harness standard KEEP scope line",
        conformance.SCOPE_LINE_TEMPLATE
        == "Shown here: effect on {task_family}, {model}, {delivery}, "
        "measured {tested_at}. Not shown: other task families, models, "
        "environments, or real-world incidence.",
        conformance.SCOPE_LINE_TEMPLATE,
    )
    check(
        "SCOPE_LINE_CARRIED_TEMPLATE is the harness carried-forward KEEP scope line",
        conformance.SCOPE_LINE_CARRIED_TEMPLATE
        == "demonstrated on {model}; carried forward to {current_model} "
        "under the sentinel rule; not re-validated on {current_model}.",
        conformance.SCOPE_LINE_CARRIED_TEMPLATE,
    )
    check(
        "expected_evidence_scope(no receipt) is the UNMEASURED sentence",
        conformance.expected_evidence_scope([]) == conformance.SCOPE_NO_RECEIPT,
        conformance.expected_evidence_scope([]),
    )


def strip_scope_line(html: str) -> str:
    """The harness scope-line text with the HTML wrapper removed and unescaped.

    skill-harness _scope_line returns
    `<p class="scope-line">…</p>`. The row value is that text with the wrapper
    removed and without HTML escaping (R1).
    """
    import html as _html

    match = re.search(r'<p class="scope-line">(.*?)</p>', html, re.DOTALL)
    if not match:
        return ""
    return _html.unescape(match.group(1))


def case_scope_line_drift_vs_harness_render() -> None:
    """R3 drift test: the constants must equal the harness render when a
    skill-harness checkout is available; skip with a named reason when not.

    Imports skill_harness.sitegen.render._scope_line from <root>/src and
    renders the R2 KEEP fixtures through it. It does not look for named
    constants in the harness.
    """
    harness_root = os.environ.get("SKILL_HARNESS_ROOT")
    if not harness_root or not Path(harness_root).is_dir():
        note(
            "scope-line drift skipped: SKILL_HARNESS_ROOT is not set to a "
            "skill-harness checkout; the drift test imports "
            "skill_harness.sitegen.render._scope_line from that root and "
            "renders the R2 KEEP fixtures through it"
        )
        return
    render_py = Path(harness_root) / "src" / "skill_harness" / "sitegen" / "render.py"
    if not render_py.is_file():
        note(
            f"scope-line drift skipped: {render_py} not found under "
            "SKILL_HARNESS_ROOT"
        )
        return
    src = str(Path(harness_root) / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    try:
        from skill_harness.sitegen import render as harness_render
    except Exception as exc:  # pragma: no cover - environment-dependent
        check(
            "skill-harness render.py imports under SKILL_HARNESS_ROOT",
            False,
            str(exc),
        )
        return
    if not hasattr(harness_render, "_scope_line"):
        check("skill-harness exposes _scope_line", False, "attribute missing")
        return
    fixtures = (
        ("standard KEEP with delivery_mechanism", sers_keep_scope_fixture()),
        (
            "standard KEEP without delivery_mechanism",
            sers_keep_scope_fixture(delivery_mechanism=None),
        ),
        ("carried-forward KEEP", sers_keep_scope_fixture(carried_forward=True)),
    )
    for label, receipt in fixtures:
        html = harness_render._scope_line(receipt)
        rendered = strip_scope_line(html)
        ours = conformance.expected_evidence_scope([receipt])
        check(
            f"skills derivation equals harness _scope_line for {label}",
            ours == rendered,
            f"ours={ours!r} harness={rendered!r} html={html!r}",
        )


def case_evidence_scope_quarantine_card_with_no_row_passes(root: Path) -> None:
    """A quarantine candidate owes no Evidence scope row."""
    write(root / "SECURITY.md", SECURITY_STUB)
    folder = root / "skills" / "engineering" / CARDS[0]
    write(folder / "SKILL.md", f"# {CARDS[0]}\n\nInstructions.\n")
    write(
        folder / "EVIDENCE.md",
        f"# EVIDENCE - {CARDS[0]}\n\n"
        "| Field | Value |\n|---|---|\n"
        "| **Screen result** | UNMEASURED. |\n"
        "| **Paired verdict** | UNMEASURED. |\n"
        "| **Evidence scope** | UNMEASURED — no receipt. |\n",
    )
    q = root / "_quarantine" / "not-yet-card"
    write(q / "SKILL.md", "# not-yet-card\n\nCandidate.\n")
    write(
        q / "EVIDENCE.md",
        "# EVIDENCE - not-yet-card\n\n"
        "| Field | Value |\n|---|---|\n"
        "| **Screen result** | UNMEASURED. |\n"
        "| **Paired verdict** | UNMEASURED. |\n",
    )
    result = run_checker(root)
    check(
        "a quarantine card with no Evidence scope row does not fail conformance",
        cell(result.stdout, CARDS[0], "O5") == "CANNOT-CHECK",
        result.stdout,
    )
    check(
        "the published card's correct UNMEASURED sentence is accepted",
        "Evidence scope" not in o5_detail(result.stdout, CARDS[0]),
        o5_detail(result.stdout, CARDS[0]),
    )


def case_evidence_scope_live_tree_rows_match_the_closed_set() -> None:
    """The live tree: 13 UNMEASURED no-receipt sentences and pull-rebase's
    NOT DEMONSTRATED sentence, read from the cards themselves."""
    from validate_card_files import find_cards as card_files_find_cards

    counts = {"UNMEASURED": 0, "NOT DEMONSTRATED": 0, "other": []}
    for card in card_files_find_cards(REPO_ROOT):
        rows = scoreboard.evidence_fields(card / "EVIDENCE.md", ("Evidence scope",))
        value = rows.get("Evidence scope", "").strip("* `")
        if value == conformance.SCOPE_NO_RECEIPT:
            counts["UNMEASURED"] += 1
        elif value == conformance.expected_evidence_scope([{"verdict": "CANT_TELL_YET"}]):
            counts["NOT DEMONSTRATED"] += 1
        else:
            counts["other"].append(f"{card.name}: {value!r}")
    check(
        "live tree: 13 cards carry the UNMEASURED no-receipt sentence",
        counts["UNMEASURED"] == 13,
        f"count={counts['UNMEASURED']} other={counts['other']}",
    )
    check(
        "live tree: pull-rebase carries the NOT DEMONSTRATED CANT_TELL_YET sentence",
        counts["NOT DEMONSTRATED"] == 1,
        f"count={counts['NOT DEMONSTRATED']} other={counts['other']}",
    )
    check(
        "live tree: no card carries a fourth shape",
        not counts["other"],
        counts["other"],
    )


# ---------------------------------------------------------------------------
# O7: the plugin manifests and the published tree must agree, BOTH directions.
#
# One direction is not enough, and this repository has the receipt: the sibling
# occasions check ran forward-only -- a count could not rise without a record --
# and an UNDERCOUNT stayed green until August 2026, because nothing asked the
# reverse question. A manifest check that only validates the paths it names has
# the same hole: delete a card from a plugin's list and every named path still
# resolves. So there are two failing directions here, and each has its own case.
#
# The marketplace entry names a plugin and its source; the plugin.json under
# that source names the plugin's cards. Both are data, so every class is cheap
# to build in isolation.
# ---------------------------------------------------------------------------

MANIFEST_PATH = ".claude-plugin/marketplace.json"
PLUGIN_MANIFEST_PATH = ".claude-plugin/plugin.json"
PLUGIN_NAME = "fixture-engineering"
PLUGIN_SOURCE = "./skills/engineering"


def marketplace_for(entries: tuple[tuple[str, str], ...]) -> str:
    """A minimal well-formed marketplace listing (name, source) entries."""
    plugins = [
        {"name": name, "source": source, "description": "fixture"}
        for name, source in entries
    ]
    return json.dumps(
        {
            "name": "fixture",
            "owner": {"name": "fixture", "url": "https://example.invalid"},
            "plugins": plugins,
        },
        indent=2,
    ) + "\n"


def plugin_json_for(name: str, skills: list[str]) -> str:
    return json.dumps({"name": name, "version": "1.0.0", "skills": skills}, indent=2) + "\n"


def plant_plugin(
    root: Path,
    skills: list[str],
    *,
    entry_name: str = PLUGIN_NAME,
    plugin_name: str = PLUGIN_NAME,
    source: str = PLUGIN_SOURCE,
) -> None:
    """One marketplace entry, and its plugin.json naming `skills` under `source`."""
    write(root / MANIFEST_PATH, marketplace_for(((entry_name, source),)))
    write(root / source / PLUGIN_MANIFEST_PATH, plugin_json_for(plugin_name, skills))


def card_paths(cards: tuple[str, ...]) -> list[str]:
    return [f"./{c}" for c in cards]


def repo_line(stdout: str, oid: str) -> str:
    """The whole reported line for a repo-wide obligation, from the real report."""
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == oid and line.startswith("  "):
            return line
    return "(cell not reported)"


def repo_cell(stdout: str, oid: str) -> str:
    """The reported verdict for a repo-wide obligation, from the real report."""
    line = repo_line(stdout, oid)
    return line.split()[0] if line.startswith("  ") else "(cell not reported)"


def case_manifest_naming_every_card_passes(root: Path) -> None:
    make_tree(root)
    plant_plugin(root, card_paths(CARDS))
    result = run_checker(root)
    check(
        "O7 passes when the plugin names every published card exactly once",
        repo_cell(result.stdout, "O7") == "PASS",
        result.stdout,
    )


def case_manifest_naming_a_missing_card_is_red(root: Path) -> None:
    """Direction one: the plugin points at a path with no card at it."""
    make_tree(root)
    plant_plugin(root, card_paths(CARDS + ("ghost-card",)))
    result = run_checker(root)
    check(
        "O7 is FAIL when the plugin names a path with no card at it",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )
    check(
        "the O7 failure names the missing card rather than a bare count",
        "ghost-card" in repo_line(result.stdout, "O7"),
        repo_line(result.stdout, "O7"),
    )


def case_unexposed_card_is_red(root: Path) -> None:
    """Direction two: a published card no plugin names. The forward-only check
    stays green here, which is the whole reason this case exists."""
    make_tree(root)
    plant_plugin(root, card_paths(CARDS[:1]))
    result = run_checker(root)
    check(
        "O7 is FAIL when a published card is named by no plugin",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )
    check(
        "the O7 failure names the unexposed card",
        CARDS[1] in repo_line(result.stdout, "O7"),
        repo_line(result.stdout, "O7"),
    )


def case_absent_manifest_is_red(root: Path) -> None:
    """Absent is FAIL, not CANNOT-CHECK. The manifest is this repository's own
    artifact: if it is gone, the collection ships no install path, and that is a
    breach rather than an unanswerable question. CANNOT-CHECK is reserved for
    what this repository genuinely cannot see, which is O5 and nothing else."""
    make_tree(root)
    result = run_checker(root)
    check(
        "O7 is FAIL when the manifest is absent, not CANNOT-CHECK",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )
    # The verdict alone cannot pin this branch. Deleting the `is not a file`
    # branch entirely leaves a FileNotFoundError that the OSError handler turns
    # into the same FAIL, so a verdict-only assertion passed with the branch
    # gone -- demonstrated by mutation on 2026-08-24. Assert the message, which
    # is the only thing that distinguishes "no install path" from "unreadable".
    check(
        "the absent-manifest failure says the manifest is absent",
        "absent" in repo_line(result.stdout, "O7"),
        repo_line(result.stdout, "O7"),
    )


def case_malformed_manifest_is_red(root: Path) -> None:
    make_tree(root)
    write(root / MANIFEST_PATH, '{"plugins": [ this is not json ]}\n')
    result = run_checker(root)
    check(
        "O7 is FAIL when the manifest is not parseable JSON",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )
    line = repo_line(result.stdout, "O7")
    check(
        "the malformed-JSON failure says so rather than reporting zero cards",
        "JSON" in line or "json" in line,
        line,
    )


def case_duplicate_exposure_is_red(root: Path) -> None:
    """`exactly once` is in the acceptance criterion, so it gets a case. Two
    plugins naming one card is a real state -- it is what a bucket move looks
    like when only half of it lands."""
    make_tree(root)
    plant_plugin(root, card_paths(CARDS + (CARDS[0],)))
    result = run_checker(root)
    check(
        "O7 is FAIL when one card is named by more than one plugin entry",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )


WRONG_SHAPES = (
    ("top-level array", "[]\n"),
    ("top-level null", "null\n"),
    ("top-level number", "123\n"),
    ("plugin entry is a string", '{"plugins": ["x"]}\n'),
    ("plugins is an object", '{"plugins": {"a": 1}}\n'),
    ("source is missing", '{"plugins": [{"name": "x"}]}\n'),
    ("source is not a string", '{"plugins": [{"name": "x", "source": {"a": 1}}]}\n'),
)


def case_parseable_but_wrong_shape_is_red(root: Path) -> None:
    """Valid JSON of the wrong shape is a FAIL, not a traceback.

    Every one of these parses, so the JSON handler never sees them. Before the
    shape guard they raised AttributeError out of the check, past both
    handlers, and aborted the whole report before a single obligation rendered
    -- while the docstring promised FAIL. The O1-O6 rows went down with it.
    """
    for label, text in WRONG_SHAPES:
        make_tree(root)
        write(root / MANIFEST_PATH, text)
        result = run_checker(root)
        check(
            f"O7 is FAIL when the manifest is valid JSON of the wrong shape: {label}",
            repo_cell(result.stdout, "O7") == "FAIL",
            (result.stdout + result.stderr)[-400:],
        )
        check(
            f"the report still renders the other obligations: {label}",
            repo_cell(result.stdout, "O1") in ("PASS", "FAIL", "CANNOT-CHECK"),
            (result.stdout + result.stderr)[-400:],
        )


def case_spelled_paths_are_not_reported_as_unpublished(root: Path) -> None:
    """A published card spelled with `././` or a backslash is still published.

    `off_tree` carries the most alarming label this check emits -- "named but
    not published". It must not be reachable by spelling a path that resolves
    to a real published card, and the source is spelled oddly too.
    """
    make_tree(root)
    plant_plugin(
        root,
        [f"././{CARDS[0]}", f".\\{CARDS[1]}"],
        source="././skills/engineering",
    )
    result = run_checker(root)
    check(
        "O7 passes when published cards are named with . segments or backslashes",
        repo_cell(result.stdout, "O7") == "PASS",
        repo_line(result.stdout, "O7"),
    )


def case_wrong_depth_under_skills_is_red(root: Path) -> None:
    """A SKILL.md under skills/ at the wrong depth is not a published card.

    It resolves, so it is not dangling; its first segment is `skills`, so a
    leading-segment test called it published. It would then contribute a
    phantom name to `exposed` and be validated by neither direction -- the
    exact hole the two-direction design exists to refuse.
    """
    make_tree(root)
    write(root / "skills" / "engineering" / CARDS[0] / "nested" / "SKILL.md", "# n\n")
    plant_plugin(root, card_paths(CARDS) + [f"./{CARDS[0]}/nested"])
    result = run_checker(root)
    check(
        "O7 is FAIL when a named path is under skills/ at the wrong depth",
        repo_cell(result.stdout, "O7") == "FAIL",
        repo_line(result.stdout, "O7"),
    )


def case_quarantine_card_in_the_manifest_is_red(root: Path) -> None:
    """The breach that RESOLVES, and the reason off-tree is its own category.

    A `_quarantine/` candidate has a real SKILL.md. Named by a plugin it is
    neither dangling nor missing, so the two-state version of this check
    reported PASS while shipping an unadmitted card to every installer. That was
    demonstrated on the live tree before this case existed. The candidate is
    named by a second plugin rooted at the repository, which is the one source
    from which a quarantine path resolves inside its plugin.
    """
    make_tree(root)
    write(root / "_quarantine" / "candidate" / "SKILL.md", "# candidate\n")
    write(
        root / MANIFEST_PATH,
        marketplace_for(((PLUGIN_NAME, PLUGIN_SOURCE), ("fixture-root", "./"))),
    )
    write(
        root / PLUGIN_SOURCE / PLUGIN_MANIFEST_PATH,
        plugin_json_for(PLUGIN_NAME, card_paths(CARDS)),
    )
    write(
        root / PLUGIN_MANIFEST_PATH,
        plugin_json_for("fixture-root", ["./_quarantine/candidate"]),
    )
    result = run_checker(root)
    check(
        "O7 is FAIL when a plugin names a card outside skills/",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )
    check(
        "the off-tree failure names the unadmitted card",
        "candidate" in repo_line(result.stdout, "O7"),
        repo_line(result.stdout, "O7"),
    )


def case_quarantine_name_collision_is_red(root: Path) -> None:
    """O8: a _quarantine/<name>/ matching a published card name is refused.

    The poison control plants a directory in _quarantine/ whose name matches
    one of the published cards, and asserts O8 reports FAIL.
    """
    make_tree(root)
    write(root / "_quarantine" / CARDS[0] / "PROVENANCE.md", "# staged\n")
    plant_plugin(root, card_paths(CARDS))
    result = run_checker(root)
    check(
        "O8 is FAIL when a quarantine name matches a published card",
        repo_cell(result.stdout, "O8") == "FAIL",
        repo_line(result.stdout, "O8"),
    )
    check(
        "the collision names the offending directory",
        CARDS[0] in repo_line(result.stdout, "O8"),
        repo_line(result.stdout, "O8"),
    )


def case_quarantine_no_collision_is_green(root: Path) -> None:
    """O8: quarantine candidates with distinct names pass silently."""
    make_tree(root)
    write(root / "_quarantine" / "unique-candidate" / "PROVENANCE.md", "# staged\n")
    plant_plugin(root, card_paths(CARDS))
    result = run_checker(root)
    check(
        "O8 is PASS when quarantine names do not collide with published cards",
        repo_cell(result.stdout, "O8") == "PASS",
        repo_line(result.stdout, "O8"),
    )


def case_no_quarantine_dir_is_green(root: Path) -> None:
    """O8: absence of _quarantine/ is a pass, not a refusal."""
    make_tree(root)
    plant_plugin(root, card_paths(CARDS))
    result = run_checker(root)
    check(
        "O8 is PASS when no _quarantine/ directory exists",
        repo_cell(result.stdout, "O8") == "PASS",
        repo_line(result.stdout, "O8"),
    )


def case_skill_path_leaving_its_plugin_is_red(root: Path) -> None:
    """A path that climbs out of its plugin's source does not ship with it.

    The install copies the source directory and nothing outside it, so a card
    in another bucket named with `../` resolves in the repository and is absent
    from the installed plugin. It must read as dangling, never as exposed.
    """
    make_tree(root)
    write(root / "skills" / "meta" / "other-card" / "SKILL.md", "# other\n")
    plant_plugin(root, card_paths(CARDS) + ["../meta/other-card"])
    result = run_checker(root)
    line = repo_line(result.stdout, "O7")
    check(
        "O7 is FAIL when a plugin names a card outside its own source",
        repo_cell(result.stdout, "O7") == "FAIL",
        line,
    )
    check(
        "the out-of-plugin path is reported as dangling",
        "no card at the path: ../meta/other-card" in line,
        line,
    )


def case_absent_plugin_json_is_red(root: Path) -> None:
    """An entry whose source holds no plugin.json exposes no cards. The report
    names the entry, not only the cards it failed to carry."""
    make_tree(root)
    write(root / MANIFEST_PATH, marketplace_for(((PLUGIN_NAME, PLUGIN_SOURCE),)))
    result = run_checker(root)
    line = repo_line(result.stdout, "O7")
    check(
        "O7 is FAIL when a plugin entry's source has no plugin.json",
        repo_cell(result.stdout, "O7") == "FAIL",
        line,
    )
    check(
        "the absent-plugin.json failure names the entry",
        f"no {PLUGIN_MANIFEST_PATH} at its source: {PLUGIN_NAME}" in line,
        line,
    )


def case_unreadable_plugin_json_is_red(root: Path) -> None:
    for label, text in (
        ("not JSON", '{"name": [ nope }\n'),
        ("skills is a string", json.dumps({"name": PLUGIN_NAME, "skills": "x"})),
    ):
        make_tree(root)
        write(root / MANIFEST_PATH, marketplace_for(((PLUGIN_NAME, PLUGIN_SOURCE),)))
        write(root / PLUGIN_SOURCE / PLUGIN_MANIFEST_PATH, text)
        result = run_checker(root)
        line = repo_line(result.stdout, "O7")
        check(
            f"O7 is FAIL when the plugin.json is unreadable: {label}",
            repo_cell(result.stdout, "O7") == "FAIL",
            line,
        )
        check(
            f"the unreadable-plugin.json failure says so: {label}",
            "is unreadable: " + PLUGIN_NAME in line,
            line,
        )


def case_plugin_name_mismatch_is_red(root: Path) -> None:
    """The marketplace entry and the plugin.json name the same plugin twice.
    When they disagree, the install and the listing name different things."""
    make_tree(root)
    plant_plugin(root, card_paths(CARDS), plugin_name="fixture-renamed")
    result = run_checker(root)
    line = repo_line(result.stdout, "O7")
    check(
        "O7 is FAIL when plugin.json names a different plugin than its entry",
        repo_cell(result.stdout, "O7") == "FAIL",
        line,
    )
    check(
        "the name-mismatch failure names both spellings",
        "name differs from the marketplace entry" in line
        and PLUGIN_NAME in line
        and "fixture-renamed" in line,
        line,
    )


def case_source_escaping_the_root_is_red(root: Path) -> None:
    """A source outside the repository is refused, even when a valid plugin
    sits there. The repository sits one level down so the planted outside
    plugin stays inside the temp directory."""
    repo = root / "repo"
    make_tree(repo)
    write(
        repo / MANIFEST_PATH,
        marketplace_for(((PLUGIN_NAME, PLUGIN_SOURCE), ("fixture-outside", "../outside"))),
    )
    write(
        repo / PLUGIN_SOURCE / PLUGIN_MANIFEST_PATH,
        plugin_json_for(PLUGIN_NAME, card_paths(CARDS)),
    )
    write(
        root / "outside" / PLUGIN_MANIFEST_PATH,
        plugin_json_for("fixture-outside", []),
    )
    result = run_checker(repo)
    line = repo_line(result.stdout, "O7")
    check(
        "O7 is FAIL when a plugin source escapes the repository root",
        repo_cell(result.stdout, "O7") == "FAIL",
        line,
    )
    check(
        "the escaping-source failure names the entry and says why",
        "escapes the repository root: fixture-outside (../outside)" in line,
        line,
    )


def case_live_manifest_covers_the_live_tree() -> None:
    """The live assertion. A fixture-only proof would leave the shipped manifest
    unchecked, which is the state this obligation exists to end."""
    report = conformance.evaluate(REPO_ROOT)
    result = report.repo_wide["O7"]
    check(
        "the shipped manifests cover the live published tree",
        result.verdict == "PASS",
        f"{result.verdict}: {result.detail}",
    )


# ---------------------------------------------------------------------------
# Drift: the prose and the list are one statement written twice
# ---------------------------------------------------------------------------

SECTION_HEADING = "## Standing obligations"
# The obligation bullets in SECURITY.md open `- **O1 ` and continue with an em
# dash. The identifier is all this needs, and stopping before the dash keeps
# this file ASCII -- which is what keeps the Windows CI cell alive.
OBLIGATION_RE = re.compile(r"^- \*\*(O\d+) ", re.MULTILINE)


def security_section(root: Path) -> str:
    text = (root / "SECURITY.md").read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    rest = text[start + len(SECTION_HEADING) :]
    end = rest.find("\n## ")
    return rest if end == -1 else rest[:end]


def case_obligations_match_the_security_section() -> None:
    section = security_section(REPO_ROOT)
    stated = OBLIGATION_RE.findall(section)
    coded = [o.oid for o in conformance.OBLIGATIONS]
    check(
        "SECURITY.md states the same number of obligations the checker runs",
        len(stated) == len(coded),
        f"SECURITY.md {len(stated)} vs checker {len(coded)}",
    )
    check(
        "SECURITY.md states the same obligation identifiers, in the same order",
        stated == coded,
        f"{stated} != {coded}",
    )


def case_version_is_declared_once() -> None:
    text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    declarations = re.findall(r"This edition is `conformance v\d+`", text)
    check(
        "the conformance edition is declared in exactly one place",
        len(declarations) == 1,
        f"{len(declarations)} declaration(s)",
    )
    check(
        "the declared edition is the one the checker stamps",
        f"This edition is `{conformance.CONFORMANCE_VERSION}`" in text,
        conformance.CONFORMANCE_VERSION,
    )
    check(
        "the bump rule travels with the declaration",
        "bumps the version" in text and "Editorial changes" in text,
    )


def case_trial_exit_date_agrees_everywhere() -> None:
    date = conformance.TRIAL_EXIT_DATE
    security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    workflow_path = REPO_ROOT / ".github" / "workflows" / "conformance-schedule.yml"
    check(f"SECURITY.md states the trial exit date {date}", date in security)
    if not workflow_path.is_file():
        check("the scheduled workflow exists", False, str(workflow_path))
        return
    check(
        f"the scheduled workflow header states the same date {date}",
        date in workflow_path.read_text(encoding="utf-8"),
    )


def case_o5_is_not_promised_as_ci() -> None:
    section = security_section(REPO_ROOT)
    check(
        "O5 is stated as a maintainer-clock item, never as a CI check",
        "maintainer's clock" in section
        and "not, and will not be, promised as a CI" in section,
        section[:400],
    )


# ---------------------------------------------------------------------------
# The live tree
# ---------------------------------------------------------------------------


def case_live_tree_is_checked_and_conforms() -> None:
    result = run_checker(REPO_ROOT)
    check(
        "the live tree passes conformance v4",
        result.returncode == 0,
        result.stdout + result.stderr,
    )
    check(
        "the live run emits a PASS line",
        "PASS: conformance v4" in result.stdout,
        result.stdout,
    )
    check(
        "the live tree has no quarantine-published name collision",
        repo_cell(result.stdout, "O8") == "PASS",
        repo_line(result.stdout, "O8"),
    )
    report = conformance.evaluate(REPO_ROOT)
    check(
        "every published card was actually walked",
        len(report.cards) >= 5,
        f"{len(report.cards)} card(s)",
    )


def main() -> None:
    isolated = [
        case_conforming_cards_pass,
        case_empty_root_refuses_rather_than_passing,
        case_unnamed_shipped_script_is_red,
        case_naming_the_script_clears_it,
        case_tree_without_the_naming_sentence_is_red,
        case_planted_undeclared_format_is_red,
        case_o1_agrees_with_the_standalone_format_gate,
        case_missing_format_gate_is_cannot_check_not_pass,
        case_cannot_check_is_distinct_from_pass,
        case_o5_without_harness_root_is_cannot_check,
        case_o5_matching_receipt_is_pass,
        case_o5_matching_receipt_with_prose_is_pass,
        case_o5_matching_receipt_markdown_link_is_pass,
        case_o5_receipt_absent_is_fail,
        case_o5_skill_id_mismatch_is_fail,
        case_o5_verdict_mismatch_is_fail,
        case_o5_newer_receipt_exists_is_fail,
        case_o5_history_receipt_is_pass,
        case_o5_undeclared_1_0_0_receipt_is_fail,
        case_o5_history_link_does_not_mask_a_newer_receipt,
        case_evidence_scope_no_receipt_wrong_sentence_is_fail,
        case_evidence_scope_no_receipt_correct_sentence_is_cant,
        case_evidence_scope_cant_tell_yet_shown_here_is_fail,
        case_evidence_scope_keep_with_scope_exact_passes,
        case_evidence_scope_keep_one_word_change_is_fail,
        case_evidence_scope_keep_without_delivery_is_unknown_delivery,
        case_evidence_scope_keep_without_scope_is_unscoped,
        case_evidence_scope_carried_forward_beats_standard,
        case_evidence_scope_empty_row_is_refused_with_its_own_message,
        case_evidence_scope_quarantine_card_with_no_row_passes,
        case_manifest_naming_every_card_passes,
        case_manifest_naming_a_missing_card_is_red,
        case_unexposed_card_is_red,
        case_absent_manifest_is_red,
        case_malformed_manifest_is_red,
        case_duplicate_exposure_is_red,
        case_quarantine_card_in_the_manifest_is_red,
        case_quarantine_name_collision_is_red,
        case_quarantine_no_collision_is_green,
        case_no_quarantine_dir_is_green,
        case_parseable_but_wrong_shape_is_red,
        case_spelled_paths_are_not_reported_as_unpublished,
        case_wrong_depth_under_skills_is_red,
        case_skill_path_leaving_its_plugin_is_red,
        case_absent_plugin_json_is_red,
        case_unreadable_plugin_json_is_red,
        case_plugin_name_mismatch_is_red,
        case_source_escaping_the_root_is_red,
    ]
    for func in isolated:
        with tempfile.TemporaryDirectory() as tmp:
            func(Path(tmp))

    case_a_clean_run_says_cannot_check_is_not_a_pass()
    case_o5_is_never_pass_on_the_live_tree()
    case_obligations_match_the_security_section()
    case_version_is_declared_once()
    case_trial_exit_date_agrees_everywhere()
    case_o5_is_not_promised_as_ci()
    case_live_manifest_covers_the_live_tree()
    case_live_tree_is_checked_and_conforms()
    case_evidence_scope_constants_are_the_closed_set()
    case_scope_line_drift_vs_harness_render()
    case_evidence_scope_live_tree_rows_match_the_closed_set()

    print("")
    for text in NOTES:
        print(f"NOT VERIFIED: {text}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: conformance v4 suite, all cases correct")


if __name__ == "__main__":
    main()
