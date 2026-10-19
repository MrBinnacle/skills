---
"mrbinnacle-skills": patch
---

The README's controlled-tests paragraph no longer says "No second run is funded yet." It now names the two later reads on `pull-rebase` that the card's `EVIDENCE.md` already recorded: the screens of 2026-09-21, where the task did not qualify, and the 2026-10-02 run that stopped at its cap of 97 looks. The verdict stays `CANT_TELL_YET`, and the paragraph still says no skill claims a measured benefit. `scripts/test_readme_admission_lead.py` now derives the verdict and the latest read's date from the card's Paired verdict row and fails when the paragraph omits either, or when it says no later run or read exists.
