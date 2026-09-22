# PR body — #315: Eval cases for decision-rights and subagent-handback

## What this PR builds

Four `claude plugin eval` cases for the orchestration bucket: two should-fire and two
should-not-fire, each with graders that can fail in its declared direction. The cases
live at the plugin root (`skills/orchestration/evals/`) so `claude plugin eval .` finds
them with no staging. The per-card `evals/evals.json` contracts are untouched.

Also includes `scripts/check_eval_suite.py`, the research pre-flight, which
verifies the suite can fail in both directions before anyone spends model calls.

## Acceptance criteria

### Criterion 1: Four cases with graders that can fail in declared direction

**Built:** Four case directories under `skills/orchestration/evals/`:

| Case | Type | Skill | Graders |
|------|------|-------|---------|
| `decision-rights-issue-bodies` | should-fire | decision-rights | `skill-fires.md` (LLM: checks framing block, evidence asymmetry, decision classification), `skill-fired.md` (tool_used: Skill invocation) |
| `decision-rights-near-miss` | should-not-fire | decision-rights | `skill-does-not-fire.md` (tool_used: Skill min=0 max=0), `answered-the-question.md` (LLM: checks no formal framing) |
| `subagent-handback-dispatch` | should-fire | subagent-handback | `skill-fires.md` (LLM: checks tool-grant detection, two return routes, bounded file write), `skill-fired.md` (tool_used: Skill invocation) |
| `subagent-handback-celery-worker` | should-not-fire | subagent-handback | `skill-does-not-fire.md` (tool_used: Skill min=0 max=0), `answered-the-question.md` (LLM: checks no subagent patterns) |

Each should-fire case has one LLM grader weighted at 2 that checks the skill's core
discipline and a `tool_used` grader proving the target skill was invoked. Each should-not-fire
case has a `tool_used` grader (arm: both, min: 0, max: 0) proving the skill was not invoked,
plus an LLM grader checking the output lacks the skill's signature patterns.

**Test:** `python scripts/check_eval_suite.py skills/orchestration/evals` exits 0.

**Before/after:** Before this change, no eval cases existed for either card. After, the
pre-flight reports 4 cases with no missing negative control and no containment failure.

### Criterion 2: Eval-suite pre-flight exits 0

**Built:** `scripts/check_eval_suite.py` accepts a suite root as an argument and checks:
- Every case has `prompt.md` with required frontmatter (name, description, tags, plugins)
- Tags include `should-fire` or `should-not-fire`
- Graders directory exists with at least one `.md` file
- Every case's plugin path resolves to a plugin root
- Every should-fire case has LLM outcome and target-Skill invocation graders
- Every should-not-fire case has LLM outcome and both-arm target-Skill containment graders
- Every should-fire case has a should-not-fire partner (no missing negative control)

**Test:** `python scripts/check_eval_suite.py skills/orchestration/evals` prints:
```
PASS: 4 case(s) in skills/orchestration/evals; no missing negative control, no containment failure.
```

**Before/after:** Before, the script did not exist in this repository. After, it passes
cleanly on the four new cases.

### Criterion 3: claude plugin eval run

**Not built in this PR.** Per S475 amendment: "No `claude plugin eval` run (it spends
model calls; it is a separate, priced step)." The eval run is a separate, priced action
that should be committed after this PR merges, with its JSON and with-arm transcript
beside the results.

### Criterion 4: EVIDENCE.md cites cases directory

**Built:** Each card's `EVIDENCE.md` `Paired verdict` row now names its cases directory
and states they have not been run:

- `decision-rights/EVIDENCE.md`: "Eval cases at `skills/orchestration/evals/decision-rights-issue-bodies/` and `skills/orchestration/evals/decision-rights-near-miss/` (should-fire and should-not-fire partners); not yet run."
- `subagent-handback/EVIDENCE.md`: "Eval cases at `skills/orchestration/evals/subagent-handback-dispatch/` and `skills/orchestration/evals/subagent-handback-celery-worker/` (should-fire and should-not-fire partners); not yet run."

**Test:** The citations are verifiable by reading the files.

### Criterion 5: corpus validator still passes

**Built:** No edit to `evals.json` for either card. The new case directories sit in the
plugin-level `skills/orchestration/evals/`, not inside any card's `evals/` directory.

**Test:** `python scripts/validate_eval_corpora.py` prints:
```
PASS: 14 eval corpus/corpora for 14 published card(s), 44 case(s) total; ...
```

**Before/after:** Before, the validator found 14 corpora and 44 cases. After, the same
count — the new cases are plugin-level eval directories, not per-card corpus entries.

**Also:** `validate_card_files.py` passes (the `find_cards` function now excludes `evals/`
directories at card depth, since they are plugin-level eval suites, not cards — #315).
`validate_conformance.py` passes. `test_validate_card_files.py` passes.

## Validation output

```
$ python scripts/check_eval_suite.py skills/orchestration/evals
PASS: 4 case(s) in skills/orchestration/evals; no missing negative control, no containment failure.

$ python scripts/validate_eval_corpora.py
PASS: 14 eval corpus/corpora for 14 published card(s), 44 case(s) total; every corpus names its card and states at least 3 cases with 2 assertions each. Corpora are structural contracts, not measurements.

$ python scripts/validate_card_files.py
PASS: 14 published card(s), all carry SKILL.md, gotchas.md, EVIDENCE.md; ...

$ PYTHONUTF8=1 python scripts/validate_conformance.py --root .
PASS: conformance v4: 14 card(s) x 4 card obligation(s) + 4 repo obligation(s) = 60 cells: 46 PASS, 0 FAIL, 14 CANNOT-CHECK.

$ python scripts/test_validate_card_files.py
PASS: card-file conformance suite, all cases correct
```

## Files changed

| File | Change |
|------|--------|
| `skills/orchestration/evals/decision-rights-issue-bodies/prompt.md` | New: should-fire case for decision-rights |
| `skills/orchestration/evals/decision-rights-issue-bodies/graders/skill-fires.md` | New: LLM grader checking framing discipline |
| `skills/orchestration/evals/decision-rights-issue-bodies/graders/skill-fired.md` | New: tool_used grader checking decision-rights invocation |
| `skills/orchestration/evals/decision-rights-near-miss/prompt.md` | New: should-not-fire case for decision-rights |
| `skills/orchestration/evals/decision-rights-near-miss/graders/skill-does-not-fire.md` | New: tool_used grader (min=0, max=0) |
| `skills/orchestration/evals/decision-rights-near-miss/graders/answered-the-question.md` | New: LLM grader checking no formal framing |
| `skills/orchestration/evals/subagent-handback-dispatch/prompt.md` | New: should-fire case for subagent-handback |
| `skills/orchestration/evals/subagent-handback-dispatch/graders/skill-fires.md` | New: LLM grader checking tool-grant detection |
| `skills/orchestration/evals/subagent-handback-dispatch/graders/skill-fired.md` | New: tool_used grader checking subagent-handback invocation |
| `skills/orchestration/evals/subagent-handback-celery-worker/prompt.md` | New: should-not-fire case for subagent-handback |
| `skills/orchestration/evals/subagent-handback-celery-worker/graders/skill-does-not-fire.md` | New: tool_used grader (min=0, max=0) |
| `skills/orchestration/evals/subagent-handback-celery-worker/graders/answered-the-question.md` | New: LLM grader checking no subagent patterns |
| `skills/orchestration/decision-rights/EVIDENCE.md` | Updated: Paired verdict row cites cases directory |
| `skills/orchestration/subagent-handback/EVIDENCE.md` | Updated: Paired verdict row cites cases directory |
| `scripts/check_eval_suite.py` | New: pre-flight checker for eval suites |
| `scripts/test_check_eval_suite.py` | New: pre-flight controls for plugin paths and trigger-direction graders |
| `scripts/validate_card_files.py` | Updated: `find_cards` excludes `evals/` at card depth |
