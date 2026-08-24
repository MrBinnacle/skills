---
"mrbinnacle-skills": patch
---

`CONTEXT.md` separates two quantities that had been sharing one word, and the first ADR records why.

An **occasion** is one independent occurrence of the failure a card addresses. A **dispatch** is one invocation of a card. `EVIDENCE.md`'s `Occasions counted` row answers `ADMISSION.md` criterion 2 and means the first; a proposal to write measured platform dispatch counters into that same row meant the second.

Criterion 2 decides it in its own words: occasions are *"counted, not predicted, and not inflated by fan-out from a single run."* A dispatch count is fan-out — 88 recorded dispatches of one card are 88 runs over some smaller, unknown number of independent failures. Writing them into the recurrence row is the specific inflation the criterion exists to refuse, not a near-miss against it.

`scripts/validate_card_files.py` already refuses the change on mechanical grounds, since the row's integer must equal the count of dated references cited in that row and `im-up` cites one. That is the symptom. The reason is the criterion, and the reason is what the ADR records, because the mechanical block could be argued away by widening the checker and the criterion cannot.

No validator, card or public count changes here. This is vocabulary and a recorded decision: the dispatch measurement is good data and gets a row of its own rather than the recurrence row, and `docs/adr/` exists from now on for decisions that are hard to reverse and would otherwise be re-proposed.
