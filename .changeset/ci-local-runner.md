---
---

`scripts/ci_local.py` runs the shell steps of the test workflow on a maintainer's machine and names each step it skips. It needs PyYAML, so CI runs neither it nor its suite, `scripts/test_ci_local.py`. No card changes.
