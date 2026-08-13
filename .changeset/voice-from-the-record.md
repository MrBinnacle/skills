---
"mrbinnacle-skills": patch
---

`BRAND.md` stops deriving the owner's voice by reading the shipped front page, and a check fails
when a voice specimen has no provenance.

The method was the defect, not the example. The file said its Voice section had been read off the
shipped surfaces, so it had no way to tell a line the owner wrote from AI copy already sitting on
the page — and it picked the copy, because generated prose is smoother and reads more like "voice"
than the real thing. The loop closed inside one session: the README fed `BRAND.md`, `BRAND.md` fed
the assistant, and the assistant offered the sentence back to its author as the model for how he
writes.

The replacement rule: a voice specimen is a line the owner wrote or ratified, cited to
`VERBATIM.md`. Provenance is a property of the line, and an unmarked shipped surface cannot supply
it. All five previous specimens cited `README.md`; two of them quoted the block deleted in #66 and
are gone, and the section is now sourced from the record throughout.

`scripts/validate_voice_provenance.py` checks three mechanical properties: every specimen carries a
citation, no citation names a shipped public surface, and every specimen appears in the record as
typed. The third is what stops a citation from being an unchecked claim — without it a fabricated
line with `VERBATIM.md` typed beside it would pass. Comparison joins wrapped lines and changes
nothing else, so a quote may be re-wrapped but not smoothed: deleting a double space or fixing an
apostrophe turns the run red, because that roughness is the evidence a person typed the line.

The check makes no judgement about whether a line sounds like the owner, and does not try. Two
poison controls run in CI — a specimen sourced from `README.md`, and a fabricated quote carrying a
correct citation — each asserting the run failed for that reason rather than incidentally.
