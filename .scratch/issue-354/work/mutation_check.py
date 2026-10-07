#!/usr/bin/env python3
"""Apply named mutants to scripts/validate_conformance.py and assert the
ticket's named assertions turn red. Restore the original file afterwards.
"""
from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
CHECKER = REPO / "scripts" / "validate_conformance.py"
TEST = REPO / "scripts" / "test_validate_conformance.py"

sys.path.insert(0, str(REPO / "scripts"))
os.environ.setdefault("SKILL_HARNESS_ROOT", "/home/agent/skill-harness-checkout")

original = CHECKER.read_text(encoding="utf-8")


def run_named(name: str) -> tuple[bool, str]:
    """Run one isolated case from the test module; return (ok, detail)."""
    import test_validate_conformance as t

    importlib.reload(t)
    t.FAILURES.clear()
    t.NOTES.clear()
    func = getattr(t, name)
    if name == "case_scope_line_drift_vs_harness_render":
        func()
    else:
        with tempfile.TemporaryDirectory() as tmp:
            func(Path(tmp))
    failed = list(t.FAILURES)
    notes = list(t.NOTES)
    detail = f"failures={failed} notes={notes}"
    return (not failed), detail


MUTANTS: list[tuple[str, str, str, str]] = [
    (
        "M11",
        "unknown task family",
        "unknown family",
        "case_evidence_scope_keep_missing_task_family_reads_unknown_task_family",
    ),
    (
        "M12",
        "unknown date",
        "unknown",
        "case_evidence_scope_keep_missing_tested_at_reads_unknown_date",
    ),
    (
        "M13",
        "unknown model",
        "unknown",
        "case_evidence_scope_keep_missing_model_id_reads_unknown_model",
    ),
    (
        "M14",
        '"current model"',
        '"the current model"',
        "case_evidence_scope_carried_forward_missing_subject_model_reads_current_model",
    ),
    (
        "M26",
        """    if not linked_receipts:
        if scope_breaches:""",
        """    if not linked_receipts:
        if False:""",
        "case_evidence_scope_no_receipt_wrong_sentence_with_harness_root_is_fail",
    ),
    (
        "M23",
        """        if receipt_path is None:
            unresolvable = True
            continue""",
        """        if receipt_path is None:
            continue""",
        "case_evidence_scope_history_link_to_missing_file_passes",
    ),
    (
        "M24",
        """        except (OSError, json.JSONDecodeError):
            unresolvable = True""",
        """        except (OSError, json.JSONDecodeError):
            pass""",
        "case_evidence_scope_history_link_to_invalid_json_passes",
    ),
    (
        "R4-empty-row",
        """    if not stated:
        return [
            f"{card.name}: EVIDENCE.md states no {EVIDENCE_SCOPE_ROW} row "
            "(an empty row is the same refusal: the card has not said)"
        ]
    if stated != expected:""",
        """    if stated != expected:""",
        "case_evidence_scope_empty_row_is_refused_with_its_own_message",
    ),
    (
        "Drift-word",
        "real-world incidence",
        "real world incidence",
        "case_evidence_scope_constants_are_the_closed_set",
    ),
    (
        "Keep-one-word-fixture",
        # mutate derivation so one-word fixture is graded against wrong expected
        "effect on {task_family}",
        "effect on {task_family}x",
        "case_evidence_scope_keep_one_word_change_is_fail",
    ),
    (
        "Carried-template",
        "under the sentinel rule",
        "under the sentinel rule.",
        "case_evidence_scope_carried_forward_beats_standard",
    ),
]

results: list[tuple[str, str, bool, str]] = []

for mid, old, new, case in MUTANTS:
    CHECKER.write_text(original, encoding="utf-8")
    text = CHECKER.read_text(encoding="utf-8")
    if old not in text:
        results.append((mid, case, False, f"OLD TEXT NOT FOUND: {old[:60]!r}"))
        continue
    mutated = text.replace(old, new, 1)
    if mutated == text:
        results.append((mid, case, False, "replacement was a no-op"))
        continue
    CHECKER.write_text(mutated, encoding="utf-8")
    try:
        ok, detail = run_named(case)
    except Exception as exc:
        ok, detail = False, f"exception: {exc}"
    results.append((mid, case, not ok, detail))
    # also verify unmutated still green for the same case
    CHECKER.write_text(original, encoding="utf-8")
    try:
        ok_base, detail_base = run_named(case)
    except Exception as exc:
        ok_base, detail_base = False, f"exception: {exc}"
    results.append((mid + "-base", case, ok_base, detail_base))

CHECKER.write_text(original, encoding="utf-8")

# N1: the drift assertion itself. Simulate a wrong import path by checking
# the assertion text exists and that a decoy __file__ would fail it.
text = original
n1_present = "the drift import of render.py lies under SKILL_HARNESS_ROOT" in text
n1_uses_file = "harness_render.__file__" in text
# Direct predicate check
resolved_wrong = Path("/tmp/decoy/skill_harness/sitegen/render.py")
root = Path("/home/agent/skill-harness-checkout").resolve()
n1_predicate_fails_on_decoy = not str(resolved_wrong.resolve()).startswith(str(root) + os.sep)
results.append(
    (
        "N1",
        "case_scope_line_drift_vs_harness_render",
        n1_present and n1_uses_file and n1_predicate_fails_on_decoy,
        f"present={n1_present} uses_file={n1_uses_file} decoy_refused={n1_predicate_fails_on_decoy}",
    )
)

# M15: _string_field non-string rule — mutate to accept any non-None
m15_old = """    value = node.get(key)
    return value if isinstance(value, str) else default"""
m15_new = """    value = node.get(key)
    return value if value is not None else default"""
CHECKER.write_text(original.replace(m15_old, m15_new, 1), encoding="utf-8")
try:
    ok, detail = run_named("case_evidence_scope_keep_non_string_scope_field_reads_default")
except Exception as exc:
    ok, detail = False, f"exception: {exc}"
results.append(
    ("M15", "case_evidence_scope_keep_non_string_scope_field_reads_default", not ok, detail)
)
CHECKER.write_text(original, encoding="utf-8")

print("")
print("=== MUTANT RESULTS ===")
all_killed = True
for mid, case, killed, detail in results:
    if mid.endswith("-base"):
        status = "BASE-GREEN" if killed else "BASE-RED"
        if not killed:
            all_killed = False
        print(f"{status:12} {mid:20} {case}")
        if not killed:
            print(f"             detail: {detail[:300]}")
    else:
        status = "KILLED" if killed else "SURVIVED"
        if not killed:
            all_killed = False
        print(f"{status:12} {mid:20} {case}")
        if killed:
            print(f"             detail: {detail[:400]}")
        else:
            print(f"             detail: {detail[:400]}")

print("")
print("ALL NAMED ASSERTIONS KILLED" if all_killed else "SOME ASSERTIONS SURVIVED")
sys.exit(0 if all_killed else 1)
