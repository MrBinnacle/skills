# Fresh-context review protocol

Use this protocol after a refactor or for an independent review.

## Reviewer input

Give the reviewer only:

- The task and acceptance criteria.
- The final diff.
- The affected public interfaces.
- The relevant test results.
- The assessment model in `references/assessment-model.md`.

Do not give the reviewer the implementation rationale. The reviewer must infer intent from the code and retained records.

## Reviewer prompt

```text
Review this diff as a cold reader.

Check whether the code states its vocabulary, contract, control flow, state,
units, side effects, and failure behavior. Preserve comments that carry
rationale or external facts. Report only evidence-backed defects that can
cause misunderstanding, unsafe change, or behavior drift.

For each finding, provide:
- reader question
- exact evidence
- required correction
- compatibility risk
- verification method

Do not report formatting preferences, optional abstractions, or names that are
clear in their local scope. Return no findings when the diff passes.
```

## Adjudication

For each finding, assign one disposition:

- **Accept:** The evidence shows a clarity or behavior defect.
- **Reject:** The finding is taste, duplicates an automated check, or lacks evidence.
- **Defer:** The correction needs facts, authority, or migration scope that is unavailable.

Do not accept a finding only because the reviewer produced it.

## Final checks

- Confirm that accepted corrections did not widen scope.
- Run focused checks again after accepted changes.
- Confirm that rejected findings need no code change.
- Record deferred facts outside the implementation.
- Return an empty finding set when evidence supports no defect.
