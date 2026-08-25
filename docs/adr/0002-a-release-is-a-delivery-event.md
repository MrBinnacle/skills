# A release is a delivery event

Status: accepted, 2026-08-24.

Until this decision, a release of this collection delivered nothing to anyone. Both documented
install routes track `main`: the plugin marketplace resolves the repository's default branch,
and `README.md` states the installer *"tracks `main` rather than a tag, so it installs the
current tip of the collection."* `package.json` carries `"private": true`, so no registry
artifact has ever existed. `CHANGELOG.md` said as much at the top of the file — *"tags and this
file are informational — a reading aid, not a pin."*

The consequence was that every merge reached every installed user at once, and the version
number described nothing a consumer could obtain. `v1.2.0` sat in `CHANGELOG.md` and
`package.json` while `git tag` stopped at `v1.1`, and 76 commits accumulated past that tag
without any of them being released in a sense a consumer could act on.

**A release is now the act of delivering changed cards to installed users.** Delivery happens
when a version bump merges to `main`. The tag and the GitHub release record that event; they do
not constitute it.

The mechanism is a field this repository was not setting. Claude Code resolves a plugin's
version from `plugin.json`, then from the marketplace entry, then from the commit SHA. This
repository has no `plugin.json` and declares no `version` in
`.claude-plugin/marketplace.json`, so resolution fell through to the SHA — which is why
consumers track the branch. The platform documentation states the rule directly: *"Setting
`version` means users only receive updates when you change this field, so bump it on every
release."* Setting it makes the release the delivery event rather than a label applied after the
fact.

## What the version number promises

Semantic Versioning requires a declaration before a number means anything: *"Software using
Semantic Versioning MUST declare a public API."* This collection has never made one.

**The declared surface is the install path and the card format. The card set is not part of
it.** Adding or retiring a card is a minor change. Changing the install path, or the on-disk
shape of a card, is a major change. Corrections within a card are a patch.

This is a deliberate narrowing, and it is the reverse of the obvious reading. Under the wide
reading — the card set is the surface — every retirement is a breaking change. This collection
retires cards on recorded evidence and says so on its front page. A scheme under which the
collection's stated purpose forces a major bump every time would either inflate the major
number until it carried no information, or create a standing incentive not to retire. Declaring
the narrow surface keeps the promise honest and keeps retirement cheap.

The obligation this creates is disclosure, not comfort. The front page must tell a reader that
the card set is expected to change under a minor bump, so that nobody infers a stability which
was never offered.

## Considered options

**Keep the reading aid, and stop implying otherwise.** Consumers continue to track `main`; the
tag and changelog stay narrative for human readers. This was the cheapest option, and the
repository was already half-committed to it in prose. Rejected because it accepts, with no
available mitigation, the best-evidenced failure mode in the release-engineering literature —
that a published version is immutable and the name pointing at it must not move. A
branch-tracked collection is exposed to that the same way a compiled package is, and the
exposure is not reduced by describing it accurately.

**Drop the ceremony entirely.** Every merge is the release; delete the version machinery and the
pending changesets with it. Rejected because it removes the only point at which a
pre-publication gate could run. The literature is consistent that such a gate must prohibit
publication rather than advise it, and a model with no publication act has nothing to gate.

## Consequences

- `.claude-plugin/marketplace.json` gains a `version` on each plugin entry. Nothing derives it
  today, which would make it a second copy of the `package.json` version maintained by hand —
  the manual synchronization of derived data this project has already identified as a
  maintenance tax rather than a safeguard. It must therefore be **generated** from
  `package.json` at release time and asserted equal by a check, never typed twice.
- A pre-publication gate is now owed. Release immutability is enabled on this repository, and
  the platform documentation is explicit: *"If you delete the immutable release, you can delete
  the tag, but you cannot reuse the same tag name."* A botched release spends a version number
  permanently, so a post-hoc check cannot serve. The gate must block.
- Existing tags are unaffected and stay as historical marks. `v1.0` and `v1.1` are not Semantic
  Versioning normal forms, which require `X.Y.Z`. Tags take the normal form from the next
  release onward.
- `v1.2.0` is not backfilled as a tag. No consumer ever received it, and a tag asserting a
  delivery that did not happen is worse than the gap it fills.
- The publication act moves. Delivery is the merge of the version-bump pull request, not a tag
  push, so any restriction on publication authority has to attach to that merge.

## Decision status

- **Non-negotiable:** that a release is a delivery event. This is the principal's decision,
  taken 2026-08-24 against the three options recorded above. A later session may implement it
  differently; it may not quietly revert to a model in which the version number describes
  nothing obtainable.
- **Revisable with new evidence:** the narrow declared surface. *Revisit if:* anything is found
  to depend on a specific card existing — a downstream document, a script, or another
  repository resolving a card by name. That would make the card set part of the surface in
  fact, and the declaration would then be false rather than merely narrow.
- **Revisable with new evidence:** generating the manifest version from `package.json` rather
  than maintaining it separately. *Revisit if:* the platform gains a mechanism that reads the
  version from one place, which would make the generator redundant.

*Revisit if:* the install routes stop tracking the default branch by default. That would change
what a consumer receives without any decision here having been revisited.
