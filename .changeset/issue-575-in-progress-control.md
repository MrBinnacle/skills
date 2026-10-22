---
---

Two suites now plant a card under `skills/in-progress/` and require the shared `iter_skill_dirs` reader to skip it (#575 item 1). `test_validate_scoreboard.py` and `test_validate_standing_costs.py` each go red when the reader's `in-progress` exclusion is removed. No card changes, and installed users need do nothing.
