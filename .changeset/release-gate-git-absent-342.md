---
---

fix: `scripts/release_gate.py` refuses in its own words when git is not on PATH (#342).

Every git call now goes through `_run_git`, which turns a missing git executable into a
`GitUnavailableError`. The gate's G6, G9 and mode-detection paths report that git could not be
run and exit non-zero, where before they died with a `FileNotFoundError` traceback. It changes a
repository script and its tests only. No card and no package behaviour changes, so this changeset
is empty and the release is not bumped by it.
