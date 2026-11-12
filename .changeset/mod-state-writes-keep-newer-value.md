---
"mrbinnacle-skills": patch
---

The tips-anywhere mod no longer loses a heads-up, and repeats one in fewer cases. Three writes read the waiting heads-up in one step and wrote it in a second: settling a heads-up, starting the `/tips` sample, and offering a new heads-up. A heads-up that arrived between the two steps could be cleared or replaced, and two scans of one heads-up could show it and ask about it twice. Two new tests reproduced both faults on the old code: the sample replaced a real heads-up that arrived during its delay, and two scans showed the heads-up twice and asked twice. Each write now reads and writes in one step and changes only the heads-up it meant. A heads-up skipped or handed over at the moment a check for new ones is running can still come back once. A new check, `scripts/check_overwrite_updaters.py`, refuses a mod state write that ignores the value stored now, unless its line says why the stored value does not matter.
