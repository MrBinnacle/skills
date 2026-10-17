# The install route is what a consumer resolves

Status: accepted, 2026-10-17. Amends [ADR 0002](0002-a-release-is-a-delivery-event.md) on one
clause: what counts as a change to the install path. ADR 0002's principal decision, that a
release is the act of delivering changed cards to installed users, is untouched and remains
non-negotiable. [ADR 0003](0003-a-cards-name-is-part-of-the-declared-surface.md) is untouched:
a card's name stays in the declared surface and a rename stays major.

## What happened

On 2026-10-17 the surface audit for [#443](https://github.com/MrBinnacle/skills/issues/443)
reclassified `.changeset/install-form-https-333.md` from `major` to `patch`
([#449](https://github.com/MrBinnacle/skills/pull/449)). That work found four texts on `main`
that price the same kind of change differently
([#447](https://github.com/MrBinnacle/skills/issues/447)):

1. ADR 0002: "Changing the install path, or the on-disk shape of a card, is a major change."
2. `GLOSSARY.md` defined **Install path** as "the plugin marketplace commands and the installer
   command in `README.md` §Install." Under that definition an edit to the command text is an
   install-path change, and ADR 0002 prices it major.
3. `scripts/release_gate.py` G10 case 3 refused a `minor` or `major` changeset whose diff touches
   no file under `skills/*/*/`. A real install-path change, such as a new marketplace name,
   touches no card, so G10 refused the `major` bump ADR 0002 required for it.
4. The owner ruling of 2026-10-17 on
   [#418](https://github.com/MrBinnacle/skills/issues/418#issuecomment-6230197669): "Real
   compatibility changes, not scope, decide the version."

[#340](https://github.com/MrBinnacle/skills/pull/340) (merged 2026-10-05) declared `major` for
an edit to README §Install under text 2. It changed the documented marketplace source from
`MrBinnacle/skills` to `https://github.com/MrBinnacle/skills.git`. Both strings resolve to the
same marketplace, `mrbinnacle-skills`, with the same three plugin names. Under text 2 the next
release would have been 4.0.0, and no installed user would have had anything to do.

## Decision

**A version is a promise to installed users. A change is major only when an installed user who
takes no action loses something they had, or must act to keep it.** The things such a user has
are a card, a card's name, and a working install route.

**Decision. Changing the install route is a major change.**

The install route is what a consumer resolves:

- the marketplace `name` in `.claude-plugin/marketplace.json`;
- the source repository that the marketplace is added from;
- the plugin `name` of each entry in that file's `plugins` list.

The install route is not the spelling of a command in `README.md` §Install. Two spellings that
resolve to the same marketplace, repository and plugin names are one route. An edit that only
changes the spelling is a correction to documentation, and a correction is a patch.

The other prices do not change. Admitting or retiring a card remains minor, as ADR 0002 and ADR
0003 say, for the reason ADR 0002 gives: the collection retires cards on recorded evidence, and
a scheme that made each retirement breaking would inflate the major number until it carried no
information. Renaming a card remains major under ADR 0003.

## Why the resolved route and not the command text

**An installed user does not re-run the install command.** Claude Code records the marketplace
and the plugins the user enabled, and resolves them by name on each update. When README §Install
changes its spelling, that record does not change, and the next update reaches the same
marketplace and the same plugins. The user gains nothing and loses nothing. A version number that
tells them to act in that case is a false alarm, and repeated false alarms teach users to ignore
the major number. ADR 0002 was written to end a version number that described nothing a consumer
could act on. A major bump for a spelling change repeats that failure from the other direction.

**A changed name does break that record.** If the marketplace `name` changes, the user's
recorded marketplace no longer matches the published one. If a plugin `name` changes or
disappears, the plugin the user enabled no longer resolves. If the repository moves, the
recorded source no longer serves the collection. In each case a user who takes no action loses a
route that worked. That is the major change this ADR prices.

**#333 is a fact about a new install, not an installed one.** The shorthand
`MrBinnacle/skills` resolved to SSH on a cold install of v3.0.1 and failed without an SSH key.
That is a transport failure for a user who is installing for the first time. It does not take a
route away from a user who already has one: their marketplace and plugin names are the same
before and after #340. The fix documents a form that works for the new user, which is a
correction, so it is a patch.

## How the gate sees it

G10 case 5 reads `.claude-plugin/marketplace.json` at the merge-base and at `HEAD`, parses both,
and compares the marketplace `name` and the set of plugin `name`s. It reports a route change when
the marketplace name differs, or when a plugin name present at the merge-base is absent at
`HEAD`. A route change requires the price this ADR's decision sentence states. The gate reads
that price from this file on each run, as it reads the other prices from ADR 0002 and ADR 0003,
and fails closed when a route change needs the price and this file cannot supply it.

Three boundaries, each deliberate:

- **A plugin name that is only added is not a route change.** No installed user had it, so no
  installed user loses it. A new plugin ships cards, and the existing card rules price those.
- **An edit to a description or to any field other than a name is not a route change.** Case 3
  still refuses `minor` or `major` for a diff that touches neither a card nor a route name.
- **The source repository is in the rule but not in the gate.** No file in this repository names
  the repository it is published from, so no diff here can show it moving. A transfer or rename
  of `MrBinnacle/skills` is a major change under this ADR, and the changeset that records it must
  declare `major` by hand.

## Considered and rejected

**Keep the command text as the install path, and fix G10 to see README §Install.** This is the
literal reading of ADR 0002 and the glossary. Rejected because it prices a change no installed
user can observe. #340 is the worked case: under that reading the next release is 4.0.0, and the
release notes would tell every installed user that something broke when nothing did.

**Price only by what G10 already sees, and drop the install route from the surface.** Rejected
because a marketplace or plugin rename does break installed users, and the version number would
then fail to warn them.

## Consequences

- `GLOSSARY.md` **Install path** now defines the route by what a consumer resolves, and names the
  command text as outside it.
- G10 gains case 5, with controls in `scripts/test_bump_classification.py` for a marketplace
  rename and a plugin rename in both directions, a description-only edit, and a missing ADR 0005.
- #449's reclassification of `.changeset/install-form-https-333.md` to `patch` now rests on this
  rule rather than only on the #418 ruling. The next release that #449 computes is 3.1.0.
- Nothing changes for an installed user. This ADR changes how future changes are priced, not
  anything a user has installed.

## Decision status

- **Non-negotiable:** that a release is a delivery event. Inherited from ADR 0002, restated here
  only so this amendment cannot be read as reopening it.
- **Revisable with new evidence:** that a change of command spelling which resolves to the same
  marketplace is not an install-route change. *Revisit if:* a concrete installed user is found
  whose route broke under such a spelling change, or the platform documentation shows that the
  command form itself changes what gets resolved. Either finding would put the command text back
  inside the route, ADR 0002's literal reading would stand, and
  `.changeset/install-form-https-333.md` would return to `major`.
- **Revisable with new evidence:** that the gate watches names and not the source repository.
  *Revisit if:* a file in this repository comes to name the repository it is published from,
  which would make a repository move observable in a diff.
