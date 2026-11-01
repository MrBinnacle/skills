---
"mrbinnacle-skills": patch
---

The release gate on `main` is green again. `mods/tips-anywhere/.claude-plugin/plugin.json` is restamped to 3.1.0 by `release_gate.py --write`: #638 typed 3.2.0 into it by hand while its changeset said `patch`, and ADR 0009 keeps a mod's version in lockstep with the collection's, so G1 refused every run since. The mod's fix still reaches installs at the next cut through the marketplace pin, as before. `scripts/ci_local.py` now runs a step that follows a skipped `npm install --global` in its job without any `*_STRICT` env flag and prints a NOTE, because that step sees the machine's tool, not the version CI pins; the install-form step therefore reports the README's dated CLI record as a WARN on the maintainer's machine instead of failing on the version alone (#425). Two suite cases cover the dropped flag and the control.
