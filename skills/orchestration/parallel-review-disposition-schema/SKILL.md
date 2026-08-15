---
name: parallel-review-disposition-schema
description: Use when 3+ isolated reviewers must decide what to do with already-verified findings. Give every seat one decision vocabulary, per-item block, ownership, and status so outputs join without erasing real disagreement.
---

# Parallel Review / Disposition Schema

## Problem

Independent reviewers preserve disagreement but default to incompatible prose. The synthesis pass
then reconciles formats instead of decisions and can mistake shared words for shared concepts.

This skill starts **after finding verification**. It makes adjudication outputs joinable; it does
not establish that a finding is real. For upstream verification use
[ADVERSARIAL-VERIFY-SEAT.md](ADVERSARIAL-VERIFY-SEAT.md).

## Trigger

Use when all are true:

- three or more isolated reviewers will adjudicate the same verified finding set;
- the decision is what to do with each finding, not whether the finding exists;
- the synthesizer needs comparable outputs without letting seats see one another.

Do not use for discovery, ordinary pair review, or verification-only work.

## Dispatch contract

Put the same four structures in every seat prompt.

1. **Decision vocabulary.** Derive a closed enum from the corpus's real decision space. Test it
   against representative findings before dispatch. Example:
   `NEW-ID | sub-item-of-<existing> | severity-change | scope-change | work-item | evidence-only | defer`.
2. **Per-item block.** Keep it compact:
   `{Item · Evidence reference · Disposition · Severity if applicable · Reasoning <=3 sentences · What-would-change-it}`.
3. **Ownership.** Assign each seat named items and its lens. Give all seats the same compressed
   corpus context; do not make each re-derive the whole set.
4. **Status.** End every result with
   `status: nominal | degraded [reason] | blocked [reason]`. Missing status halts synthesis.

## Synthesis contract

1. Reject or re-dispatch malformed seat outputs before counting agreement.
2. Group by item and disposition, not by prose similarity.
3. Classify disagreement as information, definition, or values; preserve unresolved splits.
4. Check same-enum/different-concept collisions before calling agreement.
5. Verify bounded cross-builds directly. If correction exceeds the declared read budget, re-dispatch
   the affected seat rather than silently expanding the hub's scope.
6. Report unaddressed items and degraded/blocked seats explicitly.

## Verification boundary

Already-verified does not mean infallible. A seat may cite and spot-check the evidence it relies on,
but if a load-bearing finding becomes doubtful, move it back to the verification stage. Do not let
adjudication quietly perform an unstructured verification pass.

## Output

Return:

- disposition table by item;
- agreements after semantic collision checks;
- unresolved disagreements with what would resolve them;
- unaddressed items;
- seat status summary;
- any re-verification or re-dispatch performed.

## Evidence

The origin case is recorded in [EVIDENCE.md](EVIDENCE.md); failure modes and replacement triggers
are in [gotchas.md](gotchas.md). The case demonstrates a plausible mechanism, not a controlled
with/without result. Current evidence remains `UNMEASURED` until the checked-in eval corpus is run
against this version and a baseline.
