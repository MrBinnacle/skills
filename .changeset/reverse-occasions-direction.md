---
"mrbinnacle-skills": patch
---

The card-contract checker now verifies the card against the occasions row, closing the undercount direction (#105).

The checker enforced four properties of the `Occasions counted` row — integer opening, count-equals-citations, corroboration of every cited date, and the recurrence-thin label in both directions — and every one took the row as subject and the card as reference. A newly recorded occurrence the row failed to cite passed green: the undercount direction had no check. The new reverse direction scans the card's corroborating text (the same haystack the forward check uses, row excised) and refuses any dated occurrence record the row does not cite, naming the uncited date.

The scope rule was settled by measurement, not argument: a full-haystack demand flags all nine published cards on dates that are demonstrably not occurrences (screen dates, methodology pins, verification dates, validation-genre entries), so the rule is about how an occurrence is recorded — a line carrying both a date and the word "occurrence" is an occurrence record. Measured zero uncited occurrence-marked lines across the live nine, so the check passes the tree today and enforces freshness on the recording convention going forward. The gotchas-only scan the issue body proposed was not built — it would have turned two healthy cards red whose counts rest on sibling-row records, and a regression fixture now protects exactly that shape.
