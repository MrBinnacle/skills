---
"mrbinnacle-skills": patch
---

`scripts/ci_local.py` now names the commit it tested, and any uncommitted changes, in its tally. A run exits 1 when the tree changes while it runs, because its result then describes no single state of the code. Repository tooling only; installed users need do nothing.
