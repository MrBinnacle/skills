---
"mrbinnacle-skills": patch
---

The `check_load_mode_markers.py` docstring no longer names a deleted caller of `runs_by_hand` (#636). Since #635 no script imports it. The docstring now says so and names `check_shared_readers.py`, which refuses a new copy of the reader under `scripts/`.
