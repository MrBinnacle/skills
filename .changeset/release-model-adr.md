---
"mrbinnacle-skills": patch
---

Record what a release of this collection is, and what its version number promises.

Until now a release delivered nothing. Both documented install routes track `main`, the package
is private and has never been published to a registry, and `CHANGELOG.md` stated the position
outright: tags and the changelog are *"informational — a reading aid, not a pin."* `v1.2.0` sat
in `package.json` and the changelog while `git tag` stopped at `v1.1`, with 76 commits
accumulated past it.

`docs/adr/0002-a-release-is-a-delivery-event.md` records the decision that a release is the act
of delivering changed cards to installed users, the mechanism that makes it one — a `version`
on each plugin entry, which the platform documentation says is what stops users receiving every
commit — the two rejected alternatives, and the consequences that are now owed.

The same ADR makes the declaration Semantic Versioning requires and this repository had never
made. **The declared surface is the install path and the card format. The card set is not part
of it**, so admitting or retiring a card is a minor change. The narrow reading is deliberate:
under the wide one, every retirement is a breaking change, and a collection whose stated purpose
is to retire cards on evidence would either inflate its major number until it meant nothing or
acquire a standing reason not to retire.

`CONTEXT.md` gains the two terms this fixes in place — **Release** and **Declared surface** —
each with the words it displaces.

This changeset is a patch by the rule the ADR itself declares: no card changed, and the install
path did not move.

Nothing is implemented here. The manifest `version` fields, the generator that derives them from
`package.json` rather than duplicating them by hand, and the pre-publication gate are each named
in the ADR's consequences as owed work.
