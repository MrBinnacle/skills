---
"mrbinnacle-skills": minor
---

The release gate gains mode-awareness and drops `continue-on-error`, which is the in-repo half of making it a required status check. Release-only checks are false on every ordinary pull request that adds a changeset, which is most of them, so a gate required on all pull requests without mode-awareness would block the process it is meant to protect.

The gate now distinguishes a release ref from an ordinary one by whether the `package.json` version changed relative to its merge-base with the default branch, and runs the release-only subset solely in release mode. The `--release` flag remains the override a fixture or an explicit run uses; auto-detection is what lets one gate serve both an ordinary PR (which adds a changeset) and a release PR (which bumps the version).

Two checks join the release-time subset, each blocking rather than reporting because release immutability is enabled on this repository and a spent tag name can never be reused:

- **G8 - the tag this release would cut is Semantic Versioning normal form.** The tag name is `v` + the `package.json` version, so a version that is not `X.Y.Z` produces a malformed tag. A botched release spends a version number permanently, so the gate refuses a non-normal version BEFORE the tag is cut. ADR 0002 takes the normal form from `v1.2.0` onward.
- **G9 - the working tree is clean.** A release that ships while the worktree carries uncommitted changes delivers something other than what the version bump commit recorded. Skips a tree with no HEAD commit (a fixture with only `git init`), which keeps the seeded-tree cases single-reason.

The release-gate job drops `continue-on-error` so a refusal fails the check rather than reporting and continuing, fetches full history and the base branch so the detector can compare against `origin/main`, and ships a poison control that proves an ordinary ref and a release ref receive different check sets by asserting the unconsumed-changesets check runs in one and not the other. Adding the job's status context (`Release gate (fit to release)`) to the `protect-main` ruleset is the remaining half of criterion 7 and is an operator ruleset edit, not a workflow-file edit.
