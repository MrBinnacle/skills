---
"mrbinnacle-skills": patch
---

Reconcile the README and the evidence records after the `im-down`/`im-up` pair was added.

The pair was bolted on rather than folded in, which left the collection saying several things
that were not true:

- The two new records used a different schema from the other seven (a bullet list against the
  documented table), so the README's "The receipts, explained" section described 7 of 9 receipts.
  Both are now on the schema `AGENTS.md` documents. `Promotion blocker` — a term used nowhere
  else in the repo — folds into `Screen result` as the registered screen task; `Fixture classes`
  folds into `Validated against`.
- All seven original records opened with a pointer to a README section called "Evidence records",
  which does not exist. The section is "The receipts, explained". Nine pointers repointed.
- The four failure modes explained 7 of 9 skills. `im-up` now sits under #1 (green lights you
  didn't earn) and `im-down` under #3 (momentum past the finish line), placed by the failure each
  one actually answers.
- The README said every skill exists because something went wrong. That was false for two of
  them: the session-boundary pair was built deliberately. Records now carry a `DESIGNED` origin
  with dates instead of an `OBSERVED` one, and the README says so plainly.
- `im-up`'s record said four fixture classes; nine is the measured figure. Corrected.

Both records now also carry what they were missing: the adversarial review by reproduction that
found and closed four verification holes, and the CI coverage on Linux and Windows.

README moves to the first person throughout.
