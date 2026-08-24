---
"@mrbinnacle/skills": minor
---

Promote six cards out of `_quarantine/` into the collection, and stop the page counting itself.

These are the first promotions the collection has made. Twenty-two candidates had accumulated
in `_quarantine/` since the mechanism was staged on 2026-08-19 and none had ever moved; every
previously published card entered before quarantine existed. The gap was not a shortage of
evidence. It was that the maintenance pass which was supposed to move them described itself as
a hygiene sweep, ended its output contract at "branch to PR", and kept no field capable of
recording a promotion — so ten logged passes moved zero cards while executing their own
procedure faithfully.

Promoted, each by `git mv` so the card keeps its history:

- `engineering/pretooluse-bash-guard-prose-false-positive` — a `PreToolUse` Bash guard reads
  the whole command string, so it blocks the commit message, heredoc or document that only
  mentions what it forbids. Four counted occasions across three projects and four guards.
- `engineering/success-test-accepts-any-output` — a check that accepts any non-empty output
  passes when the operation failed, because failure output is non-empty too. Two counted
  occasions, the second in the mirror direction: a probe reporting NOT-FOUND for a whole batch
  because the tool never ran.
- `engineering/halt-as-deliverable` — when a pre-registration or pre-flight gate refuses to
  produce the thing you came for, the refusal is often worth more than the thing. Three counted
  occasions across two projects.
- `engineering/mock-masked-stub-trap` — an implementation reports all gates green while a
  load-bearing branch is stubbed in production, because the test patches the helper that is the
  stub. One counted occasion; carries `RECURRENCE-THIN`.
- `engineering/click-clirunner-env-none-deletes` — Click's `CliRunner.invoke(env=...)`
  overrides only the keys the dict names, so a key omitted is not deleted. One counted
  occasion; carries `RECURRENCE-THIN`.
- `meta/router-skill-predicate-gap` — a router rule can be live, healthy and match nothing
  anyone types. Two counted occasions.

Each card gained the published contract it lacked: an `EVIDENCE.md` stating all three enforced
rows, an `evals/` corpus, normalized frontmatter, and a description rewritten to the
200-character router bar that every published card already met and no candidate did.

Three counts are deliberately lower than the dated records would support. Two tracks in one
session, and a retry loop and a test harness in one session, are each counted as one occasion,
because ADMISSION.md criterion 2 refuses a count inflated by fan-out from a single run. One
card's second dated event is link rot in its own citations rather than another instance of its
trap, and is not counted at all.

`click-clirunner-env-none-deletes` had its load-bearing library claim re-checked against the
current published Click source. The signature still types the parameter
`Mapping[str, str | None] | None`, which is the evidence that `None` is a delete rather than an
omission. The claim survived; the version pin was dropped, because a version number rots on the
library's schedule and the signature does not.

**The page no longer counts itself.** `README.md` stated the collection's size in four places
and its origin tiering in two, and `scripts/validate_scoreboard.py` *required* those two tier
statements to exist — so every admission and every retirement turned the build red until
someone re-derived the arithmetic by hand, in prose no reader had asked for. The same pin sat
inside `scripts/test_validate_card_files.py` as the literal `9 published card(s)`, and as a
hard-coded six-and-three split of which cards carry `RECURRENCE-THIN`. All of it is gone. The
guarantee that remains is the one worth keeping: any tally the page states must agree with the
records, and zero tallies is now the expected case. The test suite asserts the label rule as an
invariant read from each card's own row instead of a roster, and both directions of that
assertion were verified to fail by name under a deliberate mutation.

This is the same reasoning that retired the banner's counts on 2026-08-23. A surface that must
track repository state is a maintenance tax. The receipts live in the cards.
