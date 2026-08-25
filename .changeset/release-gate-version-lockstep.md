---
"mrbinnacle-skills": minor
---

The repository can refuse a release for one stated reason, end to end.

ADR 0002 made the merge of a version-bump pull request the delivery event, and obliged `.claude-plugin/marketplace.json` to carry a `version` on each plugin entry — generated from `package.json`, never typed twice. This ships that mechanism as the tracer bullet (#149):

- **`scripts/release_gate.py`** — check G1 refuses manifest/package version drift in both directions: an entry declaring a different value than `package.json`, and an entry declaring nothing at all (the state every plugin shipped in before this change — no wrong value anywhere, and still no version). Every failure is listed in one run, and an input the gate cannot read, parse, or trust for shape is a listed failure rather than a skip. `--write` stamps every entry from `package.json`; generation and verification share one read path in the same module so they cannot disagree about what the correct value is.
- **The manifest** — all three plugin entries now declare `"version": "1.2.0"`, written by running the script's `--write` over the tree. The Claude Code platform resolves a plugin's version from the marketplace entry once present, instead of falling through to the commit SHA.
- **CI** — `tests.yml` gains a non-blocking `release-gate` job on every pull request: the contract suite, then the gate itself with no arguments (the same command a local run runs), then a poison control that plants one drifted entry into a tree built under `$RUNNER_TEMP` and requires the refusal to name `version drift`, the drifted plugin, and a single stale surface.
- **`scripts/test_release_gate.py`** — nineteen contract cases driving the shipped script as a subprocess against seeded trees, the live tree, and the workflow wiring itself; every refusal case asserts its own message, not merely a non-zero exit.

The job stays advisory on purpose for now: ADR 0002 owes a blocking pre-publication gate with the release pipeline, and until that pipeline exists a red verdict here has nothing to stop. When it lands, this job's command becomes its first requirement.
