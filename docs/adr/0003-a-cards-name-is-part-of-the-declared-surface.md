# A card's name is part of the declared surface

Status: accepted, 2026-09-08. Amends [ADR 0002](0002-a-release-is-a-delivery-event.md) on one
clause: what the version number promises. ADR 0002's principal decision — that a release is the
act of delivering changed cards to installed users — is untouched and remains non-negotiable.

ADR 0002 declared a deliberately narrow surface: the install path and the on-disk shape of a
card, with the card set outside it. It also named the evidence that would reopen that narrowing:

> **Revisable with new evidence:** the narrow declared surface. *Revisit if:* anything is found
> to depend on a specific card existing — a downstream document, a script, or another repository
> resolving a card by name. That would make the card set part of the surface in fact, and the
> declaration would then be false rather than merely narrow.

Renaming eleven published cards in [#286](https://github.com/MrBinnacle/skills/pull/286) produced
that evidence.

**Decision. A card's name is part of the declared surface. The card set is not. Renaming a card
is a major change. Admitting or retiring one remains a minor change.**

## The evidence, measured

Three named-resolution dependencies, each of a kind ADR 0002 lists.

**Eleven live installs broke.** The published cards are junctioned from `~/.claude/skills/` into
a working clone. When the renames landed, all eleven old-name links returned `exists=False`, and
eleven installed skills stopped resolving until the links were rebuilt by hand. This is the
strongest of the three: a real consumer, not a document.

**A sibling repository names a card at a pinned SHA.** `skills/engineering/pull-rebase/EVIDENCE.md`
links four receipt files in `MrBinnacle/skill-harness` named `reclass-git-pull-rebase-trap.json`.
Renaming the card here does not rename them there. The links still resolve, because a pinned SHA
is immutable, but the coupling is by name and it is across repositories.

**Repository files resolve cards by name.** `.gitattributes` and `.github/workflows/tests.yml`
both name card directories and both needed repointing. Weaker than an external consumer, and the
same mechanism.

## Why the name and not the set

**ADR 0002's argument is preserved exactly, because it was never about names.** 0002 chose the
narrow surface to keep retirement cheap: under a wide surface every retirement is breaking, which
would inflate the major number until it carried no information and create a standing incentive
not to retire — defeating a collection whose stated purpose is retiring cards on recorded
evidence. That reasoning holds. Retirement stays minor. Nothing here touches it.

**The same reasoning points the other way for renames.** A version scheme should price the
behaviours the project wants. Retirement is routine and intended, so it must stay cheap. Renaming
is rare and avoidable — #286 is the first published-card rename since the release regime began —
so it should be expensive. Making a rename major creates the incentive to name a card well the
first time, which is the lesson #286 was.

Retiring and renaming look similar from inside the repository and are opposites from outside it.
Retiring removes something a consumer was told could be removed. Renaming moves something a
consumer was told nothing about, and had already resolved by name.

**Without names, the surface is nearly empty.** If a card's name is not covered, what a consumer
may rely on reduces to the install route and the on-disk file shape. The version number would
once again describe almost nothing a consumer could act on — the precise failure ADR 0002 was
written to end. Covering names is the reading that makes 0002 coherent with itself.

## The term that was doing two jobs

`CONTEXT.md` defined **Declared surface** as "the install path and the on-disk shape of a card"
and never defined *install path*. The phrase has two live referents in this repository: the
install **route** in `README.md` §Install, and a card's **directory**. The whole of the question
this ADR settles sat inside that ambiguity, and a reader could reach either answer from the
glossary as written. `CONTEXT.md` now defines **Install path** as the route, and states the name
separately.

## Considered and rejected

**A deprecation alias.** Publish a renamed card under both names for one minor release, then drop
the old name in the next major. This is the standard practice in package ecosystems and it would
make a rename cheap without lying to consumers. Rejected on mechanism rather than on merit:
`scripts/validate_conformance.py:616-644` refuses a card "named by more than one plugin" and
asserts each published card is "named exactly once by the manifest." An alias requires changing
that conformance rule first, which is a larger decision than this one and should be made on its
own. If renames become frequent enough to be worth the machinery, that is the ticket to open.

**Widening the surface to the whole card set.** Rejected for the reasons ADR 0002 gives, which
this ADR does not disturb.

## Consequences

- The next release is **2.0.0**, not 1.6.1. The changeset for #286 was written `patch`, corrected
  to `minor` in [#287](https://github.com/MrBinnacle/skills/pull/287) under ADR 0002 as it then
  stood, and is corrected again to `major` under this ADR. Both corrections were right when made;
  the second is a consequence of this decision rather than a defect in the first.
- Nothing had shipped when this was decided. `python scripts/release_gate.py --release` reported
  `BLOCKED - G3: 6 unconsumed changeset(s)`, so both corrections happened before publication.
  ADR 0002 built the blocking gate for this case: "a botched release spends a version number
  permanently, so a post-hoc check cannot serve."
- The release gate does not read a changeset's declared bump type.
  `grep -nE '\b(major|minor|patch)\b' scripts/release_gate.py` returns no match, and the only
  hit for `bump` in that file is a docstring sentence at line 36 describing when a release
  shipped. So a declared type is carried to `changeset version` unchecked. This ADR is what such
  a check would encode. Tracked as [#289](https://github.com/MrBinnacle/skills/issues/289).
- A future rename now owes consumers a major bump and a changelog entry naming the old and new
  names. It does not owe them an alias, because none can exist under the current conformance rule.

## Decision status

- **Non-negotiable:** that a release is a delivery event. Inherited from ADR 0002, restated here
  only so this amendment cannot be read as reopening it.
- **Revisable with new evidence:** that a rename is major rather than minor. *Revisit if:* renames
  become frequent enough that the major number inflates until it carries no information — the same
  failure mode ADR 0002 guarded against for retirement, arriving by the other door. The remedy
  then is the alias mechanism above, not a reclassification.
- **Revisable with new evidence:** that no alias mechanism is available. *Revisit if:*
  `validate_conformance.py`'s one-name rule is changed for some other reason, which would make the
  alias cheap.

*Revisit if:* a card is found to be resolved by something other than its name — a stable id, a
digest — which would move the surface off the name and onto that.
