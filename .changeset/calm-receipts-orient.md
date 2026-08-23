---
"mrbinnacle-skills": patch
---

Replace the banner's live scoreboard counts with the ruled orientation line and retire the
MB compact mark from the repo identity (owner rulings 2026-08-23, skill-harness #216).

The banner now reads `These aren't the Claude Code skills you're looking for.` at all five
validator sites. A static graphic that must track repository state is a maintenance tax, and
the line's job is orientation, not argument: it tells a visitor what kind of repository this
is; the repository makes any further case itself. `validate_scoreboard.py` now pins that
sentence byte-identically (a softened restatement fails) and keeps deriving the inventory
counts from the cards as a record-conformance check — the counts moved from the graphic to
the PASS line. The two obsolete poison fixtures were repurposed: `banner-line-drift` proves
a softened line goes red, `verdict-vocabulary-drift` proves the closed verdict vocabulary is
still refused. `assets/mark-mb.svg` is deleted: it is the owner's personal mark, and the
repository is not positioned around its owner. The receipt glyph is the repo's semantic
mark; no replacement is manufactured.
