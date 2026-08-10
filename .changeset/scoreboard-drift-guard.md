---
"mrbinnacle-skills": patch
---

Add a scoreboard validator that refuses front-page count drift and admission-policy version drift.

The kept / retired / turned-away numbers are a conservation claim on the banner and README alt. A partial retirement edit could leave them wrong with nothing red. `scripts/validate_scoreboard.py` derives the three counts from the skill tree and `RETIRED.md`, asserts all five scoreboard sites, and checks the gate card's normative-status version against `ADMISSION.md`. It joins the existing `validator` job with a poison-control fixture, and emits ASCII-only `PASS:` / `REJECTED:` lines so the Windows matrix cell stays honest.
