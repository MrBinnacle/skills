---
"mrbinnacle-skills": patch
---

Complete the writing-for-agents body pass on the six cards promoted 2026-08-23.

The six promotions shipped with rewritten descriptions and normalized frontmatter, and
their bodies untouched. Measured on 2026-08-24, four of the six exceeded the 5 KB split
threshold that `AGENTS.md` sets, and three exceeded its ~7 KB ceiling. An earlier partial
pass on one card had made it larger, not smaller — 8448 to 8736 bytes — which is the
recorded evidence that commentary without cuts does not pay; that branch was parked rather
than merged. This change finishes the pass.

**What changed, per card, with before → after sizes:**

- `router-skill-predicate-gap` 8736 → 6967 B. The origin incident was told three times
  (trigger bullet, Example, and in full in `gotchas.md`); it is now told once in a
  compressed Example whose full record stays in `gotchas.md`, where the append-only log
  already carried it. The step-1 and step-5 probe loops were the same loop written twice;
  step 5 now runs the step-1 loop with different inputs. The earlier partial pass's three
  genuine fixes (the unrunnable `for p in ...; do ... done` literal made a complete loop,
  the step renumbering, the prohibition rewritten positive) are kept.
- `success-test-accepts-any-output` 8197 → 7031 B. The 2026-08-17 outage incident appeared
  in a trigger bullet, a rule-1 caveat and the Example; the stringify defect appeared four
  times. Each now has one home: the pattern in its rule, the incident in the Example. The
  dated `gh api` claim-status caveat is compressed but keeps its substance: `--silent` is
  documented, the error stream is not, and the claim rests on a reproduced-once observation.
- `halt-as-deliverable` 7422 → 5423 B. Steps 2 and 4 ("resist the quiet re-run" / "make it
  loud") stated one instruction from two directions and are merged; the behavioral-economics
  aside folded into that step; one Note that restated a Solution step is cut. The decision
  table and the four-point verification list survive intact.
- `click-clirunner-env-none-deletes` 6582 → 5866 B. The monkeypatch advice appeared in both
  Fix and Notes; it now lives in Fix. The trailing References section is removed per this
  repository's own cross-reference convention: two of its three links moved inline to their
  moment of need (the testing-module source into Root cause, the monkeypatch reference into
  Fix), and the third — the general CLI-testing guide — is cut as redundant with the more
  specific API-reference link the Notes already carried. The dated signature-verification
  paragraph is compressed without dropping the claim's basis.

The remaining two promoted cards, `pretooluse-bash-guard-prose-false-positive` (4395 B) and
`mock-masked-stub-trap` (4156 B), were assessed under the same pass and their bodies left
unchanged: both are under every threshold and carry no internal duplication worth a diff.

All six cards' `EVIDENCE.md` standing-cost rows now state exact, dated byte counts — the
four edited cards because their sizes changed, and the two unchanged cards because their
rows were stale approximations from before the description rewrites. All seven repository
validators and the spec validator (`skills-ref` 0.1.5) pass over the edited tree.

An independent fresh-context review ran twice over the cuts. Round one found four defects,
all fixed: the compression had deleted a Notes sentence that `gotchas.md` quotes verbatim
(the "a router rule deserves a test suite" claim — restored); a `§ 1b` pointer in that same
`gotchas.md` had dangled since this branch's own renumbering (corrected to `§ 2`); the
link-migration claim in an earlier draft of this changeset overcounted by one (corrected
above); and the draft described the review in the past tense before it had run — the
false-confidence tell the review lens exists to catch, recorded here rather than smoothed
over. Round two returned seven lesser findings: four dropped-content items were restored
and paid for by cuts elsewhere (the stderr-capture fallback and the GraphQL-routing fact in
`success-test-accepts-any-output`, the entry-point symptom in
`click-clirunner-env-none-deletes`); two were declined with reasons recorded on the pull
request (a repeated leading word that is not a repeated meaning; a removed attribution
whose idea survives); and the size figures above were re-corrected after the restorations.

One boundary stated rather than fixed: no gate checks card size — the 5 KB and ~7 KB
figures live in `AGENTS.md` prose only, the same enforcement shape the description bar had
before it became a gate. Per the cross-family adjudication of 2026-08-24, a prose bound
earns a gate on observed recurrence, not on shape; this pass is occurrence one after that
ruling.
