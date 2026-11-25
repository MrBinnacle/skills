---
"mrbinnacle-skills": patch
---

`scripts/ci_local.py` now explains a filter that selects no step. It still exits 1, and it prints the job names and says that `--match` filters step names and `--job` selects a job. Repository tooling only; installed users need do nothing.
