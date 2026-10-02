---
---

fix: `scripts/test_release_gate.py` passes on a Windows developer host (#272).

Two fixture faults made the suite fail on a clean tree where the gate itself was correct. The
environment that drops `npx` now keeps `git` reachable on Windows, and the temporary repository
renames its first branch to `main` instead of force-updating a branch that is checked out. It
changes a test only. No card and no package behaviour changes, so this changeset is empty and the
release is not bumped by it.
