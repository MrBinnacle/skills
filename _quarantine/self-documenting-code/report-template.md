# Self-documenting code review

## Bottom line

[State whether the target code exposes its intent and contracts. Name the highest-impact gap.]

## Scope

- Target: [diff, files, module, or interface]
- Revision: [commit or branch]
- Mode: [review or refactor]
- Evidence limit: [checks or context that were unavailable]

## Findings

| Priority | Reader question | Evidence | Correction | Risk | Verification |
|---|---|---|---|---|---|
| Required or Recommended | [Question the code cannot answer] | [File, symbol, and exact behavior] | [Smallest correction] | [Compatibility or behavior risk] | [Executable check] |

Return `No evidence-backed findings` when this table would otherwise contain style preferences.

## External rationale

- Retained: [comments or documents that carry reasons or constraints]
- Missing: [external fact that needs a record]

## Verification

- Baseline: [command and result]
- Focused checks: [command and result]
- Broader checks: [command and result]
- Unverified: [specific claim and required test]

## Disposition

- Behavior changed: [yes or no]
- Public interface changed: [yes or no]
- Remaining action: [one action or none]
