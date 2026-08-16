# Disposition record — S295 admission triage

Date: 2026-08-15. Source session: S295 of the maintainer's private research notebook (grill: cultivate the collection).
Method: all nine published cards re-tested against admission-policy v1 (ADMISSION.md), verdict from each card's own EVIDENCE.md. Triage provenance, census, and independent review receipt are in the maintainer's private research notebook (references below; private, kept for the maintainer's own audit trail).

## Verdicts

| Card | Verdict | Basis (from the card's own record) |
|---|---|---|
| orchestration/parallel-review-disposition-schema | STANDS | Two counted independent instantiations (origin contrast + 2026-07-10 4-seat × 72-item audit); falsifier named. |
| orchestration/subagent-research-reliability | STANDS (weakly) | Origin's two distinct catches plus two later independent field catches; attribution labeled pattern-match. |
| engineering/closure-mode-at-boundaries | RECURRENCE-THIN | Validated against the origin session only; no independent second occasion counted. |
| engineering/git-pull-rebase-trap | CEILING-LIKELY | Only executed screen in the collection: Null arm 3/3, p0 = 1.00, CANT_TELL_YET (wrong-instrument classification recorded). |
| engineering/github-pages-deploy-verification | RECURRENCE-THIN | Two symptoms within one task; fan-out from a single run, not independent recurrence. |
| engineering/im-down | RECURRENCE-THIN | DESIGNED origin; screen not yet run; one supporting observed gotcha. |
| engineering/im-up | RECURRENCE-THIN | DESIGNED origin; producer-to-receiver screen not yet run; CI fixtures validate the validator, not the premise. |
| orchestration/downstream-instruction-framing | RECURRENCE-THIN | Origin incident only; usage records self-labeled "not efficacy evidence". |
| meta/skill-necessity-gate | RECURRENCE-THIN | No triggering incident; validated against its own intake; retirement trigger well-formed. |

All nine cards carry a re-screen trigger. No card is retired by this record; retirement goes through this repo's rituals only.

## Wider triage (context)

Of 57 operator-authored skills (published + installed + quarantined), 7 passed all four admission criteria on recorded evidence. The systemic gap is criterion 2: incidents are recorded once and recurrence is never independently counted. The EVIDENCE.md occasions-counted row (issue #98) exists to close this.

## Links

- Census: research notebook, `docs/research/skill-census-S295.md`
- Round-2 synthesis (triage detail): research notebook, `docs/research/grill-round2-synthesis-S295.md`
- Independent cross-family review receipt: research notebook, `docs/audit/t1-grill-pick-S295/RESULTS.md`
- Identity ruling: research notebook, `docs/adr/0001-collection-identity-field-manual.md`
