---
"mrbinnacle-skills": patch
---

`scripts/mutate_diff.py` runs at push. It breaks each clause a branch adds to `scripts/*.py`, one at a time, and fails when the paired `scripts/test_<name>.py` still passes, naming the file, the line and the mutant. Repository tooling only; installed users need do nothing.
