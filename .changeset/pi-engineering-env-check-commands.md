---
---

chore: declare this repository's check commands for the Pi verify-gate.

No installed card changes. `.pi/engineering-env.json` now lists two regexes. One matches
`python <path>/(validate_|test_|check_)*.py` and `release_gate.py`. The other matches
`pre-commit run`. Without the file the gate used its defaults (npm, pytest, cargo and so on),
and none of them matched the 41 distinct `python … .py` commands the workflows run. Measured
2026-10-11: the defaults matched 0 of 41, and the new list matches 41 of 41. It also matches
the im-up and im-down parity suites, run as `python test_validate_packet.py` from inside the
card directory.

The list replaces the defaults; it does not merge with them. So a check command this
repository adopts later must be added here, or the gate will not count it.
