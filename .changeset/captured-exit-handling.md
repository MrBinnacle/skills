---
"mrbinnacle-skills": patch
---

CI: every `out="$(...)"` capture under `set -e` in `tests.yml` now carries a failure branch (`|| { echo "$out"; exit 1; }`), so a failing check's own diagnostic reaches the job log instead of being discarded at the assignment. Twenty sites fixed (#172; #170 fixed the twenty-first). A new suite, `scripts/test_captured_exit_handling.py`, parses the workflow and refuses any capture without the branch, and is itself wired into the workflow. No published card changes.
