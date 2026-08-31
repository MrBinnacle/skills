---
"mrbinnacle-skills": patch
---

Track four quarantine candidates that were sitting untracked and blocking the release gate at G9.

`_quarantine/` is a tracked, unshipped candidate area — sixteen candidates already sit there committed. These four were extracted and left untracked, so `git status --porcelain` reported them as a dirty tree and `release_gate.py --release` returned `BLOCKED` on G9. Tracking them is what that directory is for; it ships nothing and admits nothing.

- `agent-definition-snapshot-at-session-start`
- `container-green-host-red-detached-child-holds-tempdir`
- `private-steering-head-over-public-repos`
- `squash-merge-absorbs-unpushed-base-commits`

**None of the four is admitted, and none is promoted by this change.** `ADMISSION.md` criterion 2 requires that the failure recur independently, with occasions counted rather than predicted. Measured against the cards as written: three cite a single dated incident each, and the fourth cites three dated observations of *different* failure modes rather than a recurrence of one. The default answer in `ADMISSION.md` is "not admitted", and it stands for all four.

One residue fix rides along, required by the pre-commit gate: `container-green-host-red-detached-child-holds-tempdir` named a private repository and a bare cross-repository `#N` issue reference on its evidence line. Both are replaced with a generic descriptor. The bare cross-repository reference is the exact defect that `private-steering-head-over-public-repos` — one of the other three cards in this changeset — exists to describe.

Promotion for any of these remains open and needs what promotion has always needed: a counted second occurrence, an `EVIDENCE.md` with its three contractual rows, and the gauntlet run in order.
