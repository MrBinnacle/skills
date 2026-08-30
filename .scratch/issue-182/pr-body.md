# O5 harness-root receipt agreement checks

Implements `--harness-root` for the conformance checker's O5, per issue #182.

## Acceptance criteria

### 1. `--harness-root` accepted; without it O5=CANNOT-CHECK

**What:** Added `--harness-root <path>` CLI argument to `validate_conformance.py`.
Without the flag, `check_receipt_agreement` returns CANNOT-CHECK exactly as before.
With it, the function reads the receipt file linked in each controlled field's Receipt
clause and validates it against the card's SKILL.md.

**Test:** `test_validate_conformance.py::case_o5_without_harness_root_is_cannot_check`
builds a tree with a receipt fixture and runs the checker without `--harness-root`.
Asserts both cards' O5 cells are CANNOT-CHECK. The existing
`case_cannot_check_is_distinct_from_pass` and `case_o5_is_never_pass_on_the_live_tree`
continue to pass unchanged.

**Observed:** Before the change, `case_cannot_check_is_distinct_from_pass` passed
(CANNOT-CHECK by construction). After the change, it still passes with the same
output. The new test also passes, confirming the flag is not required.

### 2. Matching card and receipt yield PASS on O5

**What:** When `--harness-root` is provided and a receipt file exists that matches the
card (correct skill_id, correct verdict, no newer receipt), O5 returns PASS.

**Test:** `test_validate_conformance.py::case_o5_matching_receipt_is_pass` builds a tree
with one card carrying a Receipt clause and a matching receipt JSON in the harness root.
The receipt's `subject_identity.skill_id` is set to sha256 of the card's SKILL.md bytes.
Asserts O5=PASS on the card with the receipt, CANNOT-CHECK on the card without.

**Observed:** Before the change, the checker did not accept `--harness-root` at all
(argparse error). After the change, O5=PASS on the matching card, CANNOT-CHECK on the
other.

### 3. Four FAIL fixtures, one per condition 1-4

Each test builds a fixture tree and runs the checker as a subprocess, asserting the O5
cell and the failure message.

**Condition 1 — receipt file absent:**
`case_o5_receipt_absent_is_fail` writes an EVIDENCE.md referencing `nonexistent.json`
and an empty harness root. Asserts O5=FAIL and "absent" or "not found" in the output.
Before: argparse error (no `--harness-root`). After: O5=FAIL, nonzero exit.

**Condition 2 — skill_id mismatch:**
`case_o5_skill_id_mismatch_is_fail` builds a receipt with `skill_id = "b" * 64`
while the card's SKILL.md hashes differently. Asserts O5=FAIL and "skill_id" in output.
Before: argparse error. After: O5=FAIL.

**Condition 3 — verdict mismatch:**
`case_o5_verdict_mismatch_is_fail` builds a receipt with verdict=KEEP while the card's
EVIDENCE.md opens with CANT_TELL_YET. Asserts O5=FAIL and "verdict" in output.
Before: argparse error. After: O5=FAIL.

**Condition 4 — newer receipt exists:**
`case_o5_newer_receipt_exists_is_fail` builds two receipts for the same skill_id: an
older one (2026-07-21) linked by the card, and a newer one (2026-08-15) not linked.
Asserts O5=FAIL and "newer" or "later" in output.
Before: argparse error. After: O5=FAIL.

### 4. Real harness clone run

Ran against the live tree with `--harness-root` pointing to a fresh clone of
MrBinnacle/skill-harness (depth 1). Output:

```
REJECTED: conformance v2: 15 card(s) x 4 card obligation(s) + 3 repo obligation(s) = 63 cells: 48 PASS, 1 FAIL, 14 CANNOT-CHECK
```

Only `git-pull-rebase-trap` has a Receipt clause. Its receipt
(`docs/sers/receipts/reclass-git-pull-rebase-trap.json`) is SERS 1.0.0 and lacks
the `subject_identity` block required by the check. O5 correctly reports:

```
FAIL         O5 controlled fields do not contradict a published receipt -- receipt 'docs/sers/receipts/reclass-git-pull-rebase-trap.json' has no subject_identity block
```

All 14 other cards have no Receipt clause and report CANNOT-CHECK with "no Receipt
clause in any controlled field; rotation pass owns this case". This is correct:
the rotation pass's Done-when clause owns the case of cards without receipts.

### 5. CI green

The full conformance suite (`scripts/test_validate_conformance.py`) passes with all
75 cases correct (19 isolated cases in temp dirs, including 7 new O5 harness-root
cases, plus live-tree and drift cases).

## Mutation campaign

No mutation campaign was run for this change. The test assertions are behavioral
(external output from subprocess) and each condition's failure message is checked,
making branch-deletion mutants unlikely to survive. A mutation campaign is recommended
before merge if the CI pipeline includes one.

## Files changed

- `scripts/validate_conformance.py` — added `--harness-root` argument, receipt
  parsing/validation logic, `_find_receipt`, `_find_all_receipts`, `RECEIPT_CLAUSE_RE`,
  updated `check_receipt_agreement` and `evaluate` signature.
- `scripts/test_validate_conformance.py` — added 7 new test cases for O5 harness-root
  behavior, helper functions (`skill_id_for`, `receipt_json`, `make_receipt_tree`).
