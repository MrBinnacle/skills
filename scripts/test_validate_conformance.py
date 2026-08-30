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
            "| **Paired verdict** | UNMEASURED. |\n",
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
        "conformance v2" in result.stderr,
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
) -> str:
    """A minimal SERS 1.1.0 receipt as a JSON string."""
    import json as _json

    return _json.dumps(
        {
            "sers_version": "1.1.0",
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
        },
        indent=2,
    )


def make_receipt_tree(
    root: Path,
    card_name: str,
    verdict: str = "CANT_TELL_YET",
    receipt_filename: str | None = None,
    source_date: str = "2026-07-21",
    harness_version: str = "0.2.3",
    skill_id_override: str | None = None,
) -> Path:
    """Build a tree with one card carrying a Receipt clause and a harness root.

    Returns the harness root path.
    """
    folder = root / "skills" / "engineering" / card_name
    skill_id = skill_id_override or skill_id_for(folder)
    fname = receipt_filename or f"receipt-{card_name}.json"
    harness_root = root / "harness"
    receipt_dir = harness_root / "docs" / "sers" / "receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    (receipt_dir / fname).write_text(
        receipt_json(card_name, skill_id, verdict, source_date, harness_version),
        encoding="utf-8",
    )
    # Overwrite EVIDENCE.md with a Receipt clause
    evidence = folder / "EVIDENCE.md"
    evidence.write_text(
        f"# EVIDENCE - {card_name}\n\n"
        "| Field | Value |\n|---|---|\n"
        f'| **Screen result** | {verdict}. Receipt: `{fname}` |\n'
        "| **Paired verdict** | UNMEASURED. |\n",
        encoding="utf-8",
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
        "| **Paired verdict** | UNMEASURED. |\n",
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
        "| **Paired verdict** | UNMEASURED. |\n",
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


# ---------------------------------------------------------------------------
# O7: the plugin manifest and the published tree must agree, BOTH directions.
#
# One direction is not enough, and this repository has the receipt: the sibling
# occasions check ran forward-only -- a count could not rise without a record --
# and an UNDERCOUNT stayed green until August 2026, because nothing asked the
# reverse question. A manifest check that only validates the paths it names has
# the same hole: delete a card from the manifest and every named path still
# resolves. So there are two failing directions here, and each has its own case.
#
# The manifest is data, so all five classes are cheap to build in isolation.
# ---------------------------------------------------------------------------

MANIFEST_PATH = ".claude-plugin/marketplace.json"


def manifest_for(cards: tuple[str, ...]) -> str:
    """A minimal well-formed manifest exposing exactly the named cards."""
    entries = ",\n".join(f'        "./skills/engineering/{c}"' for c in cards)
    return (
        "{\n"
        '  "name": "fixture",\n'
        '  "owner": {"name": "fixture", "url": "https://example.invalid"},\n'
        '  "plugins": [\n'
        "    {\n"
        '      "name": "fixture-engineering",\n'
        '      "description": "fixture",\n'
        '      "source": "./",\n'
        '      "strict": false,\n'
        '      "skills": [\n' + entries + "\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )


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
    write(root / MANIFEST_PATH, manifest_for(CARDS))
    result = run_checker(root)
    check(
        "O7 passes when the manifest names every published card exactly once",
        repo_cell(result.stdout, "O7") == "PASS",
        result.stdout,
    )


def case_manifest_naming_a_missing_card_is_red(root: Path) -> None:
    """Direction one: the manifest points at a path with no card at it."""
    make_tree(root)
    write(root / MANIFEST_PATH, manifest_for(CARDS + ("ghost-card",)))
    result = run_checker(root)
    check(
        "O7 is FAIL when the manifest names a path with no card at it",
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
    write(root / MANIFEST_PATH, manifest_for(CARDS[:1]))
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
    write(root / MANIFEST_PATH, manifest_for(CARDS + (CARDS[0],)))
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
    ("skills is a string", '{"plugins": [{"skills": "x"}]}\n'),
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
    to a real published card.
    """
    make_tree(root)
    entries = ",\n".join(
        f'        "{spelling}"'
        for spelling in (
            f"././skills/engineering/{CARDS[0]}",
            f"skills\\\\engineering\\\\{CARDS[1]}",
        )
    )
    write(
        root / MANIFEST_PATH,
        manifest_for(CARDS).split('"skills": [')[0]
        + '"skills": [\n'
        + entries
        + "\n      ]\n    }\n  ]\n}\n",
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
    manifest = manifest_for(CARDS).replace(
        f'        "./skills/engineering/{CARDS[0]}"',
        f'        "./skills/engineering/{CARDS[0]}",\n'
        f'        "./skills/engineering/{CARDS[0]}/nested"',
    )
    write(root / MANIFEST_PATH, manifest)
    result = run_checker(root)
    check(
        "O7 is FAIL when a named path is under skills/ at the wrong depth",
        repo_cell(result.stdout, "O7") == "FAIL",
        repo_line(result.stdout, "O7"),
    )


def case_quarantine_card_in_the_manifest_is_red(root: Path) -> None:
    """The breach that RESOLVES, and the reason off-tree is its own category.

    A `_quarantine/` candidate has a real SKILL.md. Named by the manifest it is
    neither dangling nor missing, so the two-state version of this check
    reported PASS while shipping an unadmitted card to every installer. That was
    demonstrated on the live tree before this case existed.
    """
    make_tree(root)
    write(root / "_quarantine" / "candidate" / "SKILL.md", "# candidate\n")
    manifest = manifest_for(CARDS).replace(
        f'        "./skills/engineering/{CARDS[0]}"',
        f'        "./skills/engineering/{CARDS[0]}",\n'
        '        "./_quarantine/candidate"',
    )
    write(root / MANIFEST_PATH, manifest)
    result = run_checker(root)
    check(
        "O7 is FAIL when the manifest names a card outside skills/",
        repo_cell(result.stdout, "O7") == "FAIL",
        result.stdout,
    )
    check(
        "the off-tree failure names the unadmitted card",
        "candidate" in repo_line(result.stdout, "O7"),
        repo_line(result.stdout, "O7"),
    )


def case_live_manifest_covers_the_live_tree() -> None:
    """The live assertion. A fixture-only proof would leave the shipped manifest
    unchecked, which is the state this obligation exists to end."""
    report = conformance.evaluate(REPO_ROOT)
    result = report.repo_wide["O7"]
    check(
        "the shipped manifest covers the live published tree",
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
        "the live tree passes conformance v2",
        result.returncode == 0,
        result.stdout + result.stderr,
    )
    check(
        "the live run emits a PASS line",
        "PASS: conformance v2" in result.stdout,
        result.stdout,
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
        case_manifest_naming_every_card_passes,
        case_manifest_naming_a_missing_card_is_red,
        case_unexposed_card_is_red,
        case_absent_manifest_is_red,
        case_malformed_manifest_is_red,
        case_duplicate_exposure_is_red,
        case_quarantine_card_in_the_manifest_is_red,
        case_parseable_but_wrong_shape_is_red,
        case_spelled_paths_are_not_reported_as_unpublished,
        case_wrong_depth_under_skills_is_red,
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

    print("")
    for text in NOTES:
        print(f"NOT VERIFIED: {text}")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: conformance v2 suite, all cases correct")


if __name__ == "__main__":
    main()
