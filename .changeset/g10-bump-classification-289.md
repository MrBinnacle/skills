---
---

fix(release-gate): G10 refuses a changeset whose declared bump contradicts its diff (#289).

`release_gate.py` gains G10. It reads the declared-surface prices from ADR 0003 and ADR 0002 on disk — never from a constant in the gate — and refuses a changeset whose `major` / `minor` / `patch` line disagrees with what its diff does under `skills/*/*/`. A rename declared anything below `major` is refused (ADR 0003); an admission or retirement declared `patch` is refused; a change that touches no file under `skills/*/*/` may not declare `minor` or `major`. At release, the version delta must match what the release diff requires. Controls live in `scripts/test_bump_classification.py` and as CI poison controls under the release-gate job, including the ADR 0003 inversion: rename + `major` passes, the same rename + `minor` is refused.

No card and no package behaviour changes, so this changeset is empty and the release is not bumped by it.
