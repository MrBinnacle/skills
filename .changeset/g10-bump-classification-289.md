---
---

fix(release-gate): G10 refuses a changeset whose declared bump contradicts its diff (#289).

`release_gate.py` gains G10. It reads the declared-surface prices from ADR 0003 and ADR 0002 on disk — never from a constant in the gate — and refuses a changeset whose `major` / `minor` / `patch` line disagrees with what its diff does under `skills/*/*/`. Cases 1–3 judge only the changesets this branch adds (new `.changeset/*.md` in `merge-base..HEAD`), never every pending file on disk. A rename declared anything below `major` is refused (ADR 0003); an admission or retirement declared `patch` is refused; a change that touches no file under `skills/*/*/` may not declare `minor` or `major`. At release, the version must match the exact SemVer result of the changesets it consumes — read at the merge-base, because `changeset version` deletes those files at HEAD. An explicit `--release` run on a released, clean main (origin/main == HEAD, no plan consumed, version unchanged) is silent: there is no delta to price. When git is not on PATH the check refuses in its own words rather than dying with a traceback. Controls live in `scripts/test_bump_classification.py` and as CI poison controls under the release-gate job, including the ADR 0003 inversion: rename + `major` passes, the same rename + `minor` is refused.

No card and no package behaviour changes, so this changeset is empty and the release is not bumped by it.
