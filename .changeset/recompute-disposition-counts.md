---
"mrbinnacle-skills": patch
---

Recompute the front page's stated disposition counts from the record it links.

The README's "Admission method" paragraph restates what the S295 disposition found: how many cards it triaged, how many it stood, how many it called thin, and how many it called ceiling-likely. Those four counts were hand-maintained prose -- the same shape that left the origin tiering claiming seven when the records read six (2026-08-15), only this count was never re-derived at all.

`scripts/validate_disposition_counts.py` recomputes each stated count from the one record the page links -- the disposition record's `## Verdicts` table -- and refuses on disagreement, naming the count and both values. The verdict vocabulary is closed (`STANDS`, `RECURRENCE-THIN`, `CEILING-LIKELY`), so an unknown verdict is refused rather than miscounted, the same refusal discipline the measured and origin counts use. Stating a count stays optional (the ruling that retired the banner and origin tallies); a count the page does state must agree with the record.

The expected value is derived from the tree, never written into the check or its test. A number-word vocabulary (the same pattern `test_release_model_disclosure` uses) parses `nine`, `two`, `six`, `one` off the page; the record's own rows are counted by category. A poison control mutates a copy of the record so a disagreeing page is rejected for that reason, naming the count and both values.
