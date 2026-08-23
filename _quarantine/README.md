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

**No candidate in this directory currently carries an `EVIDENCE.md`.** That is the standing
blocker on every one of them, and it is the reason none has been promoted.

## What publishing these does and does not claim

Publishing a candidate claims only that the incident happened and was written down. It makes no
claim that the card is measured, that it earns its context cost, or that it is recommended.

This is the same posture the repository already takes with `RETIRED.md` and with the cards
screened out at the admission gate. What is in the pipeline is visible, not hidden.

## Related

- [`ADMISSION.md`](../ADMISSION.md) — the four admission criteria
- [`AGENTS.md`](../AGENTS.md) — the promotion gauntlet and the retirement ritual
- [`RETIRED.md`](../RETIRED.md) — cards that were admitted and later withdrawn
