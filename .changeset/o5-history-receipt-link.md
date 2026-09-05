---
"mrbinnacle-skills": patch
---

`validate_conformance.py` O5: a receipt link a controlled row has already declared `not current:` is read as history, so a card that follows the rotation ritual no longer fails the check for following it.

`git-pull-rebase-trap` failed O5 today with `receipt 'reclass-git-pull-rebase-trap.json' has no subject_identity block`. The row it reads is `Screen result`, which links a 2026-07-20 receipt on SERS 1.0.0 — a schema version that predates the `subject_identity` block — and the row's own text says so: `not current: no_skill_id`. The validator parsed the first `Receipt:` clause in the field, found no `subject_identity`, and returned FAIL before reaching conditions 2, 3 and 4 or the `Paired verdict` row that carries the current receipt.

`AGENTS.md` step 5 instructs the rotation pass to keep a not-current receipt link as history. A card obeying that instruction could not also satisfy the validator, and the validator was scoring a card for a link the card had already retired in the same sentence. The failure surfaced only when a maintainer ran O5 by hand against a harness root, which is the moment it matters, because CI has no harness root and reports CANNOT-CHECK there.

`check_receipt_agreement` now skips conditions 1 to 3 for a receipt link inside a field carrying the text `not current:`. A missing file, an absent `subject_identity` or a superseded verdict is what such a row states, not a contradiction of it. The link still counts as linked for condition 4, so a row that has moved on to a newer receipt is not then reported as failing to link it. A receipt with no `subject_identity` in a field that makes no such declaration stays a FAIL: that is the case the condition exists for.

Three cases join `test_validate_conformance.py`. Two are the pair the behaviour turns on — the same 1.0.0 receipt, the same card, the same harness root, differing only in whether the row declares it not current: PASS with a reason naming the history link, and FAIL naming `subject_identity`. The third is a control against turning condition 4 off by accident: a row carrying a history link beside a current one must still fail when a newer unlinked receipt exists.

Verified against the live tree: O5 on `git-pull-rebase-trap` returns FAIL before the change and PASS after it, with no edit to the card.
