---
"mrbinnacle-skills": patch
---

Add a scoreboard validator that refuses front-page count drift and admission-policy version drift.

The kept / retired / turned-away numbers are a conservation claim on the banner and README alt. A partial retirement edit could leave them wrong with nothing red. `scripts/validate_scoreboard.py` derives the three counts from the skill tree and `RETIRED.md`, asserts all five scoreboard sites, and checks the gate card's normative-status version against `ADMISSION.md`. It joins the existing `validator` job with poison-control fixtures, and emits ASCII-only `PASS:` / `REJECTED:` lines so the Windows matrix cell stays honest.

`ADMISSION.md` now declares its version in exactly one place. The other two occurrences became prose that references the declaration instead of restating the string, and the validator refuses both a missing declaration and a second one. Fewer declaration sites is a stronger guarantee than a smarter checker: with one site a partial bump cannot be expressed, so it cannot be missed.
