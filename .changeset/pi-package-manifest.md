---
"mrbinnacle-skills": patch
---

The repository is now a Pi package. `pi install git:github.com/MrBinnacle/skills` loads the 14 cards and the four extensions in `mechanisms/`; before this change a Pi install loaded the cards and no extension. `scripts/test_pi_manifest.py` checks that the manifest names every shipped card and every mechanism, and nothing else.
