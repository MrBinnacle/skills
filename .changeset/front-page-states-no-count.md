---
"mrbinnacle-skills": patch
---

The front page, the banners and the quarantine README stop asserting things that go stale or were
already false.

**The card count came out of enduring content.** The README stated it eleven times: "publishes 14
of them", "One card carries a controlled result", "Eleven carry a dated record", "Two carry
neither", "What all 14 do carry", "the same 14 by form", "Nine are about an operation", "Five are
about what one session writes down", "All 14 published cards carry one", "Two cards have already
left", "One card carries one". Both banner SVGs carried it twice each, in the rendered text and in
the `aria-label`, and the README's `<img alt>` repeated it.

Every one of those rots the moment a card is admitted or retired. The same README also carried a
paragraph asserting that it "states no tally of the provenance states, deliberately: a number here
would need re-checking every time a card enters or leaves." Both statements cannot be true, and a
reader who caught the contradiction would be right to distrust the rest of the page.

The ruled banner line is now `Each card states the condition that would retire it.` — the same
claim, true whatever the card set is. `scripts/validate_scoreboard.py` no longer derives a count
into that sentence. Deriving it was the wrong repair: CI kept the repository internally consistent
and still shipped a rendered SVG and a social card telling a stranger a number, and no reader's
browser regenerates those. The number now reaches a reader in one place only, the card-evidence
table CI rebuilds from the cards themselves.

**`_quarantine/README.md` asserted something false.** In bold: "No candidate in this directory
currently carries an `EVIDENCE.md`. That is the standing blocker on every one of them." Three
candidates carry one. The real blocker is stated instead — `ADMISSION.md` criterion 2 needs
counted, independent recurrence, and a candidate without an `EVIDENCE.md` has no counted occasions
whatever else is true of it. The file now also states the two mechanical conventions a candidate
must satisfy before promotion, the leading-word name and the 200-character description, and states
no count of its own contents.

**`_quarantine/self-documenting-code/README.md` documented a package that does not exist.** It
described `references/`, `assets/` and `scripts/` subdirectories and the command
`python scripts/validate_package.py .`. The files are flat and that path is wrong. The README now
lists the real layout, and records that the card's own `validate_package.py` **exits 1 on the
card's own directory** — the checker was written against a nested layout the card does not use.
Nothing in CI runs that checker, because candidates are not gated, which is how a red self-check
sat unreported on one of the two candidates closest to publication. The disagreement is recorded
rather than papered over; resolving it is a promotion-gate matter, not a README fix.

The README also now points at `_quarantine/` from the admission section and the repository layout,
which it did not before.

No card, evidence field, verdict or date is modified. `validate_card_files.py`,
`validate_scoreboard.py`, `test_validate_quarantine_landing.py` and `test_readme_admission_lead.py`
all PASS.

**What this does not fix.** No gate would have caught any of the three. `validate_scoreboard.py`
checks the tallies it already knows the wording of; it cannot see a number in a sentence nobody
told it about. The defect class is a prose assertion about repository state that nothing
re-derives from the state, and this changeset repairs three instances of it without building the
detector that would catch the fourth.
