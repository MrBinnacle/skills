# An occasion is not a dispatch

Status: accepted, 2026-08-24.

Every published card's `EVIDENCE.md` carries one `Occasions counted` row, answering
`ADMISSION.md` criterion 2 — does the failure recur independently. Issue #106 measured a
different quantity, the platform's lifetime dispatch counters per card, and proposed writing
those numbers into that same row. We are keeping the two apart: `Occasions counted` keeps its
meaning, and measured dispatch counts get a row of their own.

The deciding reason is in criterion 2's own words. Occasions are *"counted, not predicted, and
not inflated by fan-out from a single run."* A dispatch count **is** fan-out — the 88 recorded
for `downstream-instruction-framing` are 88 runs arising from some smaller, unknown number of
independent failures. Substituting one for the other is not a near-miss against the criterion;
it is the inflation the criterion exists to refuse.

There is a mechanical consequence that makes this visible immediately, and it is the symptom
rather than the reason. `scripts/validate_card_files.py` requires the row's integer to equal the
number of dated references cited in that row, each corroborated elsewhere in the card. `im-up`
records `1 — 2026-06-11 wrong-handoff occurrence`; writing `40` there would oblige the card to
cite forty dated references, so the change turns CI red on every card it touches.

## Considered options

**One row, richer semantics — #106 as written.** Its benefit was real: recurrence becomes
measured for every published card at no marginal effort per session, and the gate card's single
lifetime dispatch becomes a datum its next re-screen must face. Rejected because the front
page's recurrence claims would inflate by a factor nobody can bound, every `RECURRENCE-THIN`
label would come off on evidence that does not support removing it, and the collection's central
claim — that it turns cards away on recorded evidence — would rest on a number the admission
policy names and refuses.

**Widen the checker to accept either quantity.** Rejected. A row that accepts two incompatible
meanings cannot report which one a card asserted, which is the state the row exists to make
legible.

Recording both, because the first will be proposed again: the dispatch data is genuinely good
and the pull toward the single row is the obvious move.

## Consequences

- #106 is re-scoped to add a row rather than overwrite one, and to state the dispatch semantics
  beside the number. A dispatch count is blind to hook-injected and always-loaded firings, so a
  recorded zero reads as *no recorded dispatch* and never as *unused*.
- A second row is now owed on the published cards. Its name, its place in the `EVIDENCE.md`
  contract, and whether a checker enforces it are open.
- The dispatch delta log stays an independent count source. #105 names an undercount class in
  the occasions row and the log can corroborate a dated occurrence — but it never supplies the
  count.
- Reversal is asymmetric. Keeping the quantities apart costs one row. Merging them and reverting
  later means re-deriving the recurrence evidence for all nine published cards from records that
  would by then have been overwritten.

*Revisit if:* criterion 2 is rewritten to admit a run-count as recurrence evidence. That is a
change to what the collection claims publicly, and it is the principal's.
