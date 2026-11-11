---
"mrbinnacle-skills": patch
---

The tips-anywhere mod no longer clears a newer heads-up. Two writes read the waiting heads-up and cleared it in a second step: settling a heads-up, and starting the `/tips` sample. A heads-up that arrived between the two steps was lost. Each write now reads and clears in one step, and clears only the heads-up it meant. A new check, `scripts/check_overwrite_updaters.py`, refuses a mod state write that ignores the value stored now, unless its line says why the stored value does not matter.
