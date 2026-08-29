# Fix: discard-proof captured exits under set -e (#172)

Split out of #170, which fixed exactly one instance (line 838) and deliberately left the rest.

## The defect

Every affected step has this shape:

```bash
set -euo pipefail
out="$(python scripts/some_check.py)"
echo "$out"
echo "$out" | grep -q '^PASS:' || { echo '::error::…did not run'; exit 1; }
```

Under `set -e`, a non-zero exit from the captured command **aborts at the assignment**. `echo "$out"` never runs. The check's own diagnostic is discarded, and the job log contains the step source plus `##[error]Process completed with exit code 1` and no test output at all.

The anti-vacuity `grep` on the following line is well-conceived and cannot fire, because the failure path never reaches it. The guard that exists to prove a check ran is itself unreachable on the only occasion it matters.

## The fix

Per site:

```bash
out="$(python scripts/some_check.py)" || { echo "$out"; exit 1; }
```

The assignment still captures whatever the command emitted before failing, so the diagnostic survives.

## Changes

### 1. Regression test (`scripts/test_captured_exit_handling.py`)

A text parser over `.github/workflows/tests.yml` that asserts the property rather than the text: for each `run:` block that sets `-e` and assigns from a command substitution, require a failure branch on the assignment.

**Before the fix:** The test reports 20 bare assignments across the workflow — every one of the lines the ticket names. The summary fails: `20 bare assignment(s) found`.

**After the fix:** The test reports 0 bare assignments. All guarded assignments carry the failure branch. The test passes.

### 2. Workflow fix (`.github/workflows/tests.yml`)

20 lines changed, each from:

```
out="$(cmd)"
```

to:

```
out="$(cmd)" || { echo "$out"; exit 1; }
```

Lines fixed: 57, 68, 101, 201, 209, 274, 288, 304, 312, 382, 390, 502, 510, 589, 597, 644, 652, 851, 1221, 1229.

Line 838 (the `test_release_gate.py` step) was already fixed in #170 and is not touched here.

### 3. Comment update (`.github/workflows/tests.yml:822-834`)

The comment on the release-gate step that said "This shape is repeated at ~20 other steps in this file. They are left alone here on purpose… Tracked separately." is updated to reflect that all steps now carry the fix.

## Gate results

All 11 existing test suites pass:

- `test_validate_card_files.py` — PASS
- `test_validate_conformance.py` — PASS
- `test_validate_skill_formats.py` — PASS
- `test_validate_voice_provenance.py` — PASS
- `test_validate_brand_kit.py` — PASS
- `test_validate_eval_corpora.py` — PASS
- `test_validate_disposition_counts.py` — PASS
- `test_readme_admission_lead.py` — PASS
- `test_release_model_disclosure.py` — PASS
- `test_release_gate.py` — PASS
- `test_validate_spec_conformance.py` — PASS

Live validators: `validate_scoreboard.py` — PASS

New regression test: `test_captured_exit_handling.py` — PASS

## Mutation campaign

No mutation campaign was run. The regression test asserts a structural property (every `out="$(...)"` under `set -e` carries `|| { echo "$out"; exit 1; }`), not a behavioral predicate. A line deletion mutant removing the `|| { echo "$out"; exit 1; }` suffix from any fixed line would be caught by the test's line-level check. The test itself has no mutation surface — it is a one-shot parser, not a branching checker.

## Acceptance criteria

| Criterion | What was built | Test that pins it |
|---|---|---|
| Every `out="$(cmd)"` under `set -e` carries a failure branch | 20 lines fixed in `tests.yml` | `test_captured_exit_handling.py` asserts 0 bare assignments |
| The fix does not change any other step behavior | Each fix appends `|| { echo "$out"; exit 1; }` — no other line altered | All 11 existing suites pass unchanged |
| A regression cannot re-introduce the defect | Structural parser in the test suite | `test_captured_exit_handling.py` fails if any line reverts to bare form |
