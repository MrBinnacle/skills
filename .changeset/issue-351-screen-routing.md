---
"mrbinnacle-skills": patch
---

`AGENTS.md` step 4 now names the one card that qualifies for a screen. It said `mocked-stub` and `walk-the-recipe` each carry a frozen fixture and counterfixture. Neither does on `main`: `mocked-stub`'s `EVIDENCE.md` records that no fixture pair exists, and `_quarantine/walk-the-recipe/` holds `SKILL.md` alone. The one card with a tracked pair is the quarantined `frontend-slop`, whose `fixtures.json` holds expect-pass and expect-fail cases for its oracle. The passage now names `frontend-slop` with that path, gives the evidence for `mocked-stub` and `walk-the-recipe`, points at skills#215 for the `walk-the-recipe` rebuild, and says why the validator fixtures under `im-up` and `im-down` do not count. No card changes.
