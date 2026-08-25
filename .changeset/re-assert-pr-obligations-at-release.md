---
"mrbinnacle-skills": minor
---

The release gate re-asserts the obligations that already hold on every pull request at the moment a version becomes permanent -- the `--release` run of `scripts/release_gate.py` (#152).

Three checks join G1-G4 as release-time siblings, each because a one-directional or absent version of it has already failed here:

- **G5 - the manifest and the published tree name the same cards, both directions.** O7 was forward-only once and an undercount stayed green until August 2026, because nothing asked the reverse question. A manifest check that validates only the paths it names has the same hole: drop a card from the manifest and every named path still resolves. Delegated to `validate_conformance.check_plugin_manifest` rather than restated.
- **G6 - the external specification validator is clean over the published tree.** `skills-ref` is the only conformance instrument here the maintainer did not author, which is exactly why it caught two PUBLISHED cards carrying invalid YAML frontmatter that every repository-local gate passed. Re-run as a subprocess at release, so a direct push that bypasses the per-PR spec-conformance job still meets the spec before the version becomes permanent.
- **G7 - every workflow `uses:` action is pinned to a full 40-hex commit SHA.** #147 pinned every action; G7 keeps it from rotting back. A floating tag is not a pin (CVE-2025-30066 repointed every `tj-actions/changed-files` tag from v1 to v45 inside 24 hours), so any `uses:` whose ref is not a 40-hex SHA is a listed failure naming the file, the line, and the mutable ref.

Each ships its own poison control under the release-gate job in CI, asserting its own distinguishing message and a single-reason refusal. The release-gate job now sets up node (pinned) so the G6 control can run `npx`; that line is itself a `uses:` G7 re-asserts is pinned. G5's only skip is O7's own vacuum ("checked nothing") — the seeded-fixture state — so a missing `skills/` directory whose manifest still names cards is refused rather than skipped. G6 skips a non-git tree and when nothing is published; G7 skips when there is no workflow directory.
