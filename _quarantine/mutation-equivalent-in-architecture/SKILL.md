---
name: mutation-equivalent-in-architecture
description: |
  Use when a mutation-testing campaign produces a surviving mutant that LOOKS
  like a genuine test-coverage gap but cannot be killed by ANY falsifiable test
  in the current code architecture. The honest disposition is RE-CLASSIFY as
  EQUIVALENT-IN-CURRENT-ARCHITECTURE and document the architectural constraint
  blocking independent killability — NOT ship a disjunction-based test that
  passes either way under the mutation (which is itself slop by the
  mutation-testing rubric's own discipline). Common trigger: sequential guards
  where guard N+1 can only fire when guard N also fires; mutating guard N+1's
  threshold is structurally unreachable so the surviving mutant is equivalent
  not gap. Sibling discipline to ai-slop-sentinel's "non-falsifying test"
  taxonomy: a test that passes under both current code AND the proposed
  mutation is exactly the slop pattern the mutation-testing rubric exists to
  surface — so writing one to "kill" the mutant defeats the entire purpose.
author: Claude Code
version: 1.0.0
date: 2026-06-07
---

# Mutation Equivalent-In-Current-Architecture

## Problem

Mutation testing surfaces surviving mutants. The default disposition is to
write a killing test (close the gap). But some surviving mutants are
**structurally unreachable** by any falsifiable test in the current code
architecture — usually because they're on a guard or branch that's never the
FIRST guard/branch to fire on the relevant input domain.

Naive response: write a test using a disjunction (`assert reason in ("A", "B")`)
that "passes" against both current code and the mutation. This is double-slop:

1. The mutation isn't killed (the test passes under the mutation).
2. The test itself is the canonical ai-slop "tautological assertion / disjunction
   that passes either way" pattern that mutation testing exists to surface.

Honest response: declare the mutant **EQUIVALENT-IN-CURRENT-ARCHITECTURE**,
document the architectural constraint that blocks independent killability, and
defer the architectural refactor (if desired) to a v-next punch list. The
mutant remains uncovered in the report but the disposition is honest about why.

## Context / Trigger Conditions

- A mutation-testing tool reports a surviving mutant.
- Initial reading of the mutant suggests it's a genuine coverage gap.
- On closer inspection, the mutated code path can only be reached via inputs
  that ALSO trigger an earlier guard which short-circuits before reaching the
  mutated line.
- The earlier guard ALSO has a mutation on it (or a separate test); the mutant
  in question can't be made independently observable.

Specific architectural shapes that produce this:

1. **Sequential guards over a shared computation.** E.g.,
   `if α̂ <= 0: raise; if β̂ <= 0: raise` where α̂ and β̂ are computed from the
   same input and share sign — `β̂ <= 0 ⟺ α̂ <= 0`, so the β̂ guard never fires
   alone.
2. **Defensive fallbacks for an already-validated invariant.** A `try/except`
   on an operation that the type system already excludes from failing.
3. **Conditional branches over a single-valued enum.** A branch that's
   technically reachable but only via a state that's never written.
4. **Logging/observability code paths.** Mutations on log messages that don't
   affect behavior (most mutation tools should be configured to skip these).

## Solution

### Step 1 · Verify the mutant cannot be killed independently

Manually apply the mutation. Run the FULL test suite. Confirm zero tests fail.

Then attempt to construct a killing test:
- Identify the smallest input that reaches the mutated line via the SECOND
  guard without firing the FIRST guard.
- If such an input is constructable, the mutant IS a genuine gap — write the
  test. Done.
- If such an input is NOT constructable due to a mathematical / type-system /
  state-machine constraint, the mutant is EQUIVALENT-IN-CURRENT-ARCHITECTURE.

### Step 2 · Document the architectural constraint

In the mutation-testing fix-brief, write the re-classification with:

```
M<N> · RE-CLASSIFIED · EQUIVALENT-IN-CURRENT-ARCHITECTURE
  - Mutation: <verbatim diff>
  - Why equivalent: <the mathematical / structural argument that proves
    independent killability is impossible>
  - Proof: <minimal demonstration — e.g., "in _ebmom: α̂ = m·common,
    β̂ = (1-m)·common with m ∈ (0,1) → sign(α̂) = sign(β̂); so the α̂
    guard always fires first when the β̂ guard would fire">
  - Architectural fix (v-next): <how to make the mutant independently
    observable — usually involves splitting the guards into independent
    functions>
  - Deferred to: <v0.2 punch list / Phase 3.x-bis / etc.>
```

### Step 3 · Do NOT ship a fake killing test

Reject the temptation to write:

```python
def test_beta_guard():
    ...
    with pytest.raises(ConvergenceFailure) as exc:
        _ebmom(...)
    assert exc.value.reason in ("alpha_le_zero", "beta_le_zero")  # SLOP
```

This passes under both current code (raises `alpha_le_zero`) and the mutation
(still raises `alpha_le_zero`, because the α̂ guard is upstream). The
disjunction is a tautology. Per any mutation-testing rubric's own discipline:
tests must be falsifiable against the specific mutation.

### Step 4 · Record the deferral in the project's carry-forward list

The architectural refactor (split guards into independent functions) is real
v-next work, not a phantom. The fix-brief should add it to the carry-forward
punch list with the explicit rationale: "M<N> mutant becomes independently
killable after this refactor."

## Verification

A correctly-classified EQUIVALENT-IN-CURRENT-ARCHITECTURE mutant satisfies:

1. The mutation is applied; ALL tests pass (confirms surviving).
2. No test can be written that passes against current code AND fails against
   the mutation (the falsifiability test for the test itself).
3. The architectural argument is provable, not hand-waving. ("They share sign
   because alpha = m·X, beta = (1-m)·X" is provable. "The β̂ branch isn't
   really used" is hand-waving.)
4. A documented refactor would make the mutant independently killable.

If any of these fail, the mutant is NOT equivalent — it's just a gap you
didn't find the right test for. Try harder before reclassifying.

## Example

**From the Skill Harness Phase 3.3 fix-loop (2026-06-07):**

Mutation `fit.py:314 beta_hat <= 0.0 → beta_hat < 0.0` survived.

Initial reading: "convergence guard boundary; symmetric to mut_83 (`alpha_hat`
boundary); write a parametrized test for β̂ ∈ {-0.001, 0.0, 0.001}."

The fix-loop agent's draft test asserted:
```python
assert exc.value.reason in ("alpha_le_zero", "beta_le_zero")
```

The agent's self-review caught the disjunction:
- Test passes against current code: GREEN (raises with `reason="alpha_le_zero"`)
- Test passes against the mutation: GREEN (still raises with
  `reason="alpha_le_zero"` because α̂ guard at fit.py:306 fires first)
- The β̂ guard at fit.py:314 was NEVER the firing guard for this input.

The agent ran the mutation manually with a non-disjunction test (`assert reason
== "beta_le_zero"`) to verify. It went RED against current code too — proving
the β̂ guard cannot fire independently.

**Mathematical proof of equivalence**: in `_ebmom`,
- `m = sample_mean ∈ (0, 1)`
- `common = m·(1-m)/v − 1`
- `α̂ = m·common`
- `β̂ = (1-m)·common`

Since `m ∈ (0, 1)`: `m > 0` and `(1-m) > 0`. Therefore
`sign(α̂) = sign(β̂) = sign(common)`. So `β̂ ≤ 0 ⟺ α̂ ≤ 0`, and the α̂ guard
at fit.py:306 ALWAYS fires before the β̂ guard at fit.py:314 can be reached.

**Disposition**: M5 RE-CLASSIFIED as EQUIVALENT-IN-CURRENT-ARCHITECTURE.
Architectural fix deferred: split `_validate_alpha(α̂)` and `_validate_beta(β̂)`
into independent module-level functions; tests can then call each directly with
arbitrary inputs. Punch-list entry: Phase 3.3-bis or v0.2.

The fix-loop's commit body documented the re-classification verbatim instead
of shipping the disjunction test. Result: 13 GREEN + 1 honest EQUIVALENT vs
the alternative 14 GREEN with 1 silent slop test.

## Notes

- Equivalent-in-architecture is NOT the same as a tool's built-in "equivalent
  mutant" detection. Tool detection catches syntactic equivalents (e.g.,
  `range(n)` vs `range(0, n)`). Architectural equivalence is SEMANTIC and
  requires human/agent reasoning about the surrounding control flow.
- The architectural refactor that makes the mutant independently killable is
  usually beneficial in its own right (it improves separation of concerns).
  Treat the punch-list entry as a v-next improvement, not a workaround.
- Mutation testing tools should NOT auto-classify these — the architectural
  argument requires lens-specific reasoning the tool can't do.
- Self-review by the agent producing the fix-loop is the most likely place to
  catch the failed-to-kill case. The discipline pairs well with
  `ai-slop-sentinel` invoked against your OWN diff before commit (look for
  disjunction assertions that pass either way).
- Honesty discipline: shipping `M<N> · GREEN` when the test is a disjunction
  is misleading. Shipping `M<N> · RE-CLASSIFIED` with the architectural
  argument is honest. The mutation-test kill-rate number takes a hit
  (denominator stays, numerator decreases by 1), but the kill-rate is more
  trustworthy.

## See also

- `mutation-testing:mutation-testing` — the tool-running skill this discipline
  augments
- `ai-slop-sentinel` — the slop-detection skill that catches the disjunction
  tautology pattern this skill helps avoid in advance
- `bayesian-eval-discipline` — context for understanding sequential-guard
  patterns in statistical code (where this skill most often applies)
