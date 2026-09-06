---
"mrbinnacle-skills": patch
---

`README.md`: the front page points at the cards' records instead of restating their values, and a check refuses the copy it removed.

The controlled-results section stated `paired verdict: not yet established` for `git-pull-rebase-trap`. That card's `EVIDENCE.md` records `CANT_TELL_YET` with a receipt dated 2026-09-03, typed reason hazard not met. The page was three days behind its own source of record. Every check in `validate_scoreboard.py` passed throughout, because none of them read the prose — the file derives counts from the records and never compared the page's sentences to them.

The admission paragraph stated `admission-policy v1` was applied "to all nine published cards". That was true on 2026-08-15 and reads as a statement about the current set. Fourteen cards are published now, and cards promoted after that date did not go through that pass.

Both fixes are cuts. The section names the measured card and links its record, stating no verdict, no date and no receipt; the admission paragraph is scoped to the nine cards and the date, with no findings summary. An accurate copy is still a copy, and the next edit to a card desynchronises it again, so the page points rather than restates.

`check_controlled_section_restates_nothing` enforces two rules on that section: the cards it names are exactly the cards whose records carry a controlled result, and no measured verdict appears in the section at all. `UNMEASURED` stays allowed — it is the residual statement about every other card, it is derivable from the absence of a measured verdict, and it cannot drift toward claiming a measurement that did not happen.

`scripts/test_validate_scoreboard.py` runs six controls, because a check written in response to a silent drift has to be shown going red on that drift rather than merely present. The live tree passes, so a control that fails for an unrelated reason stays distinguishable from one that fails because the check works. A restated verdict is refused. The original drifted wording is refused verbatim. Naming an unmeasured card is refused, and so is dropping a measured one. A renamed or missing section is refused rather than passing vacuously, which is the failure a section-scoped check invites: "no violations in a section I could not find" reads identically to "no violations".

No card's `EVIDENCE.md` changed. The records were correct; the page was not.
