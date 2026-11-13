---
"mrbinnacle-skills": patch
---

The `im-up` and `im-down` test suite now finishes when one card is copied without the other. Before, it stopped with a `FileNotFoundError` because eight cases run a script that only the other card ships. Each of those cases now prints `NOT VERIFIED` with the missing script's name and stays out of the `PASS:` line, as the parity check already did. A new `single-card` case runs the suite from a copy of one card alone and fails if that run crashes or lists a case it skipped as passed. Three card sentences were wrong and are corrected: pytest exits 5 on the suite instead of reporting success, `im-down` no longer calls `/clear` one-way, because Claude Code keeps the cleared conversation for `/resume`, and the working-tree check names the packet the close wrote instead of config exclusions that do not exist. Both evidence records now say the suite ran in GitHub CI until 2026-10-24 and runs locally since.
