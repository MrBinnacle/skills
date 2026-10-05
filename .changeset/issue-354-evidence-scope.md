---
"mrbinnacle-skills": major
---

Every published card's `EVIDENCE.md` gains an `Evidence scope` row, and CI refuses a card whose row is missing or disagrees with what its linked receipt shows. This changes the on-disk shape of a card, which ADR 0002 (`docs/adr/0002-a-release-is-a-delivery-event.md`) makes a major change: "Changing the install path, or the on-disk shape of a card, is a major change."

The row's value is derived from the receipt conformance O5 already resolves from the card's `Receipt:` clause under `--harness-root`, using the closed set from skills#353: `UNMEASURED — no receipt.`; `NOT DEMONSTRATED — receipt verdict <VERDICT>; no effect is shown.`; `UNSCOPED — the KEEP receipt carries no verdict_scope (SERS before 1.6.0).`; or, for a KEEP receipt with `verdict_scope`, skill-harness's scope line (standard and carried-forward forms). Thirteen cards read the UNMEASURED sentence; `pull-rebase` reads the NOT DEMONSTRATED sentence against its CANT_TELL_YET receipt. Quarantine cards and `scripts/fixtures/` are exempt.

The card-files validator adds `Evidence scope` to its contract-row set. The conformance validator checks the value, including the no-receipt case O5 skipped by returning CANNOT-CHECK. The scope-line templates are constants in `scripts/validate_conformance.py` with a comment naming their source in skill-harness; a drift test compares them with the harness render when `SKILL_HARNESS_ROOT` is set and skips with a named reason when it is not.
