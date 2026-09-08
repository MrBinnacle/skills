---
"mrbinnacle-skills": patch
---

Every quarantine candidate's `description` now fits the 200-character router bar.

Measured before the change: 25 candidates carry a `SKILL.md`, and 3 of them had a description
within 200 characters. The other 22 ran between 566 and 1,272 characters. Most were the card's
whole problem statement plus a numbered trigger list, copied into the frontmatter.

A description is a context pointer. It is loaded on every turn for a model-invoked skill, and its
job is to state what the material is and name the branches that should reach it. A 900-character
description does not do that job better than a 190-character one; it spends nine hundred
characters of every turn's attention to do it worse, because the trigger is buried in the middle.
The published cards already sit under the bar, which is what `validate_card_files.py` enforces, so
this was the difference between a candidate and a card rather than a matter of taste.

Each of the 22 was rewritten to lead with the condition that should fire it and to state the
mechanism in one clause. The finding itself stays in the card body, which is where a reader who
has already been routed there needs it. `skill-family-curation` carries
`disable-model-invocation: true`, so its description is human-facing and drops the trigger list
entirely.

No card body, evidence field, verdict, count or date is modified. The diff is 22 insertions
against 270 deletions across 22 files, one line changed per file.

Effect on the mechanical publication bars: candidates within the 200-character description bar go
from 3 to 25, candidates within the 7,168-byte `SKILL.md` ceiling go from 16 to 17 (the shorter
frontmatter carried one file under it), and candidates clearing every mechanical bar at once go
from 1 to 2 — `self-documenting-code` and `uniform-eol-rewrite-evades-the-mixed-eol-guard`.
`anti-slop-frontend-secure` is now blocked on size alone, at 7,816 bytes.

This clears a clerical blocker, not a substantive one. `ADMISSION.md` criterion 2 requires counted,
independent recurrence, and 22 of the 25 candidates still carry no `EVIDENCE.md` and therefore no
counted occasions. None of them is admitted by this change.
