# PR Body — issue #315: Eval cases for decision-rights and subagent-handback

## What this builds

Four `claude plugin eval` cases — two should-fire and two should-not-fire —
for the `decision-rights` and `subagent-handback` cards, each with a Python
grader that can fail in its declared direction. A pre-flight check
(`check_eval_suite.py`) verifies the suite is runnable and honest before
anyone spends.

## Acceptance criteria checklist

- [x] Criterion 1: Four cases with graders that can fail in declared direction
- [x] Criterion 2: Pre-flight check exits 0
- [ ] Criterion 3: `claude plugin eval` run — BLOCKED (no `claude` CLI)
- [x] Criterion 4: EVIDENCE.md citations — eval setup and pre-flight cited
- [x] Criterion 5: Corpus validator still passes

## Criterion 1: Four cases with graders that can fail in their declared direction

**What was built:** Two eval case directories per card under
`skills/orchestration/<card>/evals/cases/`, each containing a `case.json`
(prompt + assertions) and a `grader.py` (pattern-matching evaluator).

| Card | Direction | Case ID | Trigger tested |
|---|---|---|---|
| decision-rights | should-fire | decision-rights-should-fire-1 | Blanket "Do Not Re-Litigate" header in handoff |
| decision-rights | should-not-fire | decision-rights-should-not-fire-1 | User explicitly requests that header format |
| subagent-handback | should-fire | subagent-handback-should-fire-1 | Web-toolless agent dispatched for research |
| subagent-handback | should-not-fire | subagent-handback-should-not-fire-1 | Agent with correct tools + return channel |

**Test that pins it:** Each grader was tested with a PASS-intended and a
FAIL-intended synthetic response. All four graders produce exit 0 on the
PASS case and exit 1 on the FAIL case, confirming they can fail in their
declared direction.

**Observation (2026-09-22):**
- `decision-rights-should-fire-1/grader.py`: PASS on PASS-input (exit 0),
  FAIL on FAIL-input (exit 1). Correctly detects when the skill is not
  applied (agent proceeds with blanket header).
- `decision-rights-should-not-fire-1/grader.py`: PASS on PASS-input (exit 0),
  FAIL on FAIL-input (exit 1). Correctly detects when the skill is
  incorrectly applied (agent refuses user's explicit framing request).
- `subagent-handback-should-fire-1/grader.py`: PASS on PASS-input (exit 0),
  FAIL on FAIL-input (exit 1). Correctly detects when the skill is not
  applied (agent proceeds with web-toolless dispatch).
- `subagent-handback-should-not-fire-1/grader.py`: PASS on PASS-input (exit 0),
  FAIL on FAIL-input (exit 1). Correctly detects when the skill is
  incorrectly applied (agent refuses correctly-configured dispatch).

## Criterion 2: Pre-flight check exits 0

**What was built:** `scripts/check_eval_suite.py` — accepts a `--root` argument
and checks:
1. **No missing negative control:** every should-fire case has a
   should-not-fire partner and vice versa.
2. **No containment failure:** each grader produces both PASS and FAIL
   results against paired synthetic responses.

**Test that pins it:** `python3 scripts/check_eval_suite.py --root .`
exits 0.

**Observation (2026-09-22):** The script exits 0, reporting:
```
PASS: 4 eval case(s) across 2 card(s) (2 should-fire, 2 should-not-fire).
No missing negative control, no containment failure. Suite is runnable
and honest.
```

**Before/after:** Before this change, the script did not exist. After,
it runs clean against the tree.

## Criterion 3: claude plugin eval run — BLOCKED

**Blocker:** The `claude` CLI is not available in this container. The
ticket requires "One `claude plugin eval` run against the plugin, both
arms, with the run's JSON committed beside the results." This cannot be
completed without the tool.

**What remains:** Once the `claude` CLI is available, run:
```
cd skills/orchestration
claude plugin eval mrbinnacle-orchestration
```
Commit the resulting JSON and transcript beside the eval cases.

## Criterion 4: EVIDENCE.md citations

**What was built:** Both cards' `EVIDENCE.md` `Screen result` rows now
cite the eval setup and pre-flight result by record:

- `decision-rights/EVIDENCE.md`: Documents eval cases (should-fire-1
  testing blanket header, should-not-fire-1 testing user-explicit
  format), pre-flight pass, and case location.
- `subagent-handback/EVIDENCE.md`: Documents eval cases (should-fire-1
  testing web-toolless dispatch, should-not-fire-1 testing correct
  config), pre-flight pass, and case location.

**Note:** The `Screen result` remains `UNMEASURED` because no eval run
has occurred. The citations reference the infrastructure, not a
measurement. Once criterion 3 completes, the row should be updated with
the run's record.

## Criterion 5: Corpus validator still passes

**What was built:** `scripts/validate_eval_corpora.py` already recognizes
`cases/` as a valid subdirectory within `evals/` (not a stray file) —
line 215 carries `_EXEMPT_DIRS: frozenset[str] = frozenset({"cases"})`.
No code change was needed.

**Test that pins it:** `python3 scripts/validate_eval_corpora.py --root .`
exits 0. The test suite `test_validate_eval_corpora.py` also passes
(all 17 cases, including `case_second_file_in_evals_rejected` which
confirms the stray-file check still fires for non-exempt files).

**Observation (2026-09-22):**
```
PASS: 14 eval corpus/corpora for 14 published card(s), 44 case(s)
total; every corpus names its card and states at least 3 cases with
2 assertions each. Corpora are structural contracts, not measurements.
```
The existing `evals/evals.json` contract for both cards is unchanged.

**Before/after:** The `cases/` subdirectory exemption was already in
place. No change was needed — the new files pass cleanly without
displacing the existing `evals.json` contract.

## Mutation campaign

Not applicable — no mutation receipt obligation in this ticket.

## Compound gate

Run before merge:
- `python3 scripts/validate_eval_corpora.py` — PASS (14 corpora, 14 cards)
- `python3 scripts/test_validate_eval_corpora.py` — PASS (17/17)
- `python3 scripts/check_eval_suite.py` — PASS (4 cases, 2 cards)
