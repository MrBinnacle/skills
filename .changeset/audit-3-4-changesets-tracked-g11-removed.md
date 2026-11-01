---
"mrbinnacle-skills": patch
---

Two release-gate fixes from the 2026-10-31 audit. `.changeset/` is tracked again (operator ruling 2026-10-31): since #630 the directory was untracked, so G10, which lists a branch's changesets with `git ls-tree`, saw none and refused every card addition, rename and release as "declares no bump", and `check_changeset_for_branch.py` had no file to find. A changeset's text is what `CHANGELOG.md` publishes at the next release, so tracking it exposes nothing new. G11, the CI-state check, is removed with its suite and its workflow step: no test workflow has run on GitHub since #630, so the Actions API held no run for any commit and G11 refused every release; `scripts/ci_local.py` runs those steps on the releasing machine.
