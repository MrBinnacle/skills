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

`scripts/validate_voice_provenance.py` checks four mechanical properties: every specimen is
followed by an explicit `Source:` line; that source names `VERBATIM.md` rather than a shipped
surface; the quoted text **equals** a recorded line exactly; and the section and date in the
citation are where that line actually sits.

Equality rather than containment, because a fragment of a recorded line is not that line —
selective truncation can invert a sentence while every word is genuine, and a containment check
would certify it as verbatim. Comparison joins wrapped lines and changes nothing else, so a quote
may be re-wrapped but not smoothed: deleting a double space or fixing an apostrophe turns the run
red, because that roughness is the evidence a person typed the line.

An **inline** quotation in the Voice section is refused rather than checked. That is the shape
every replaced specimen had — `*"..."*` with the front page named in the surrounding prose — so a
blockquote-only check would have passed the very file it exists to have caught.

The check makes no judgement about whether a line sounds like the owner, and does not try. Three
poison controls run in CI — a specimen sourced from `README.md`, a fabricated quote carrying a
correct citation, and an inline italic quotation — each asserting the run failed for that reason
rather than incidentally.
