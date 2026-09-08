# `_quarantine/` — candidate cards, not admitted skills

Nothing in this directory is a published skill. These are candidates: cards written when an
incident happened, held here until they either clear the admission gate or are cut.

## Why they live in this repository

Promotion is a `git mv` from `_quarantine/<card>` to `skills/<family>/<card>`. The card arrives
in the published tree carrying its own history — when it was first written, the incident that
produced it, and every refinement since.

Before this import the candidates lived outside the repository. Promotion across a repository
boundary is a copy: the card lands as one fresh commit with no past, and the record of how it
got good is gone. That contradicts this repository's discipline at the exact moment a card
starts making public claims.

A second consequence is that promotion becomes one reviewable diff — the `git mv` plus the
`EVIDENCE.md` the card must now carry — auditable against the `AGENTS.md` gauntlet in a single
pull request.

## What admission requires

A candidate is not admitted by sitting here. It clears `ADMISSION.md` on recorded evidence, and
the ritual in `AGENTS.md` governs the promotion. Read those files rather than this one for the
gate itself.

**The standing blocker is `ADMISSION.md` criterion 2: counted, independent recurrence.** A
candidate needs an `EVIDENCE.md` whose `Occasions counted` row names dated, separate occurrences
of the failure. Most candidates here have no `EVIDENCE.md` at all, so they have no counted
occasions and cannot clear that criterion whatever else is true of them. That is what holds the
directory, not the quality of the writing.

This README states no count of how many candidates are in which state. Any number written here
would go stale the next time a card is added, promoted or cut. Read the directory.

## The two conventions a candidate must satisfy before it can be promoted

Both are mechanical, both are cheap, and both were applied across the directory on 2026-09-08.

**The name is a leading word, not a proposition.** One to three tokens, preferring a word the
model already holds. A card's name sits in the pointer position — the directory, the install
listing, the first word of the description, the string someone types. `uniform-eol` is a name.
`uniform-eol-rewrite-evades-the-mixed-eol-guard` is a sentence about the finding, and it belongs
in the card, not on the door.

**The `description` is at most 200 characters.** It is a context pointer, read on every turn for
a model-invoked card whether or not the card ever fires. It states what the material is and names
the condition that should reach it. `scripts/validate_card_files.py` enforces this bar on
published cards; a candidate that fails it cannot be promoted without an edit.

Neither convention is a quality judgment, and satisfying both admits nothing.

## What publishing these does and does not claim

Publishing a candidate claims only that the incident happened and was written down. It makes no
claim that the card is measured, that its context cost is justified, or that it is recommended.

This is the same posture the repository already takes with `RETIRED.md` and with the cards
screened out at the admission gate. What is in the pipeline is visible, not hidden.

## Files a candidate carries

A candidate is not required to carry the four files a published card carries. Most hold a
`SKILL.md` and nothing else. Some carry a `gotchas.md`, an `EVIDENCE.md`, or supporting prose.
A `LANDING.md` marks a candidate that was landed on purpose rather than left untracked by
accident, and `scripts/validate_quarantine_landing.py` refuses a staged candidate without one.

## Related

- [`ADMISSION.md`](../ADMISSION.md) — the four admission criteria
- [`AGENTS.md`](../AGENTS.md) — the promotion gauntlet and the retirement ritual
- [`RETIRED.md`](../RETIRED.md) — cards that were admitted and later withdrawn
- [`README.md`](../README.md) — the published collection
