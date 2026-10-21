---
"mrbinnacle-skills": patch
---

The conformance suite now has a fixture that kills the O9 `skills/`-presence mutant (#533). A watched card present under `skills/` and named in no manifest or Retired row must report `FAIL` with the `skills/` path alone. Before, the only collision case also named a manifest, so a checker that skipped the `skills/` test stayed green. Verified by skipping that test: the new case turns red and the existing collision case stays green. No checker change and no card changes.
