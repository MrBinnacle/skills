# GLOSSARY.md — vocabulary of record

A small collection of agent skills, kept only while evidence supports keeping them. This
glossary fixes what each term means, on every surface — public copy, governance files, skill
cards, and issue titles alike.

Which words may appear in *public asset copy* is a narrower question, answered by
[`assets/tokens.json`](assets/tokens.json) (`copy.words_to_prefer`, `copy.words_to_avoid`). This
file does not restate that list.

## Language

**Card**:
A single skill in this collection — its `SKILL.md`, `gotchas.md` and `EVIDENCE.md` together.
_Avoid_: entry, module, prompt, plugin

**Social preview**:
The image GitHub shows when a link to this repository is shared. Named for the repository
setting it populates.
_Avoid_: card, preview card, social card, OG image

**Scoreboard states**:
The four derived, validator-enforced front-page counts — **admitted** (from the skill
directories), **measured** (from each card's `EVIDENCE.md` controlled fields), **retired** and
**solutions looking for a problem** (both from `RETIRED.md`). These are admission-side labels
about inventory, not measurement verdicts.
_Avoid_: "kept" as an admission label — `KEEP` is the measurement instrument's verdict word,
and rendering admission state in verdict vocabulary implies an admitted card is empirically
proven, the exact confusion the rejection checklist screens for.

**Admitted**:
In the collection. Says nothing about measurement — an admitted card can be `UNMEASURED`.
_Avoid_: kept, approved, validated

**Admissible (card)**:
Passes all four admission criteria on recorded evidence today. Distinct from the measurement
instrument's *evidence admissibility*, which gates whether an observation may feed
aggregation — a card can be admissible while every observation about it is inadmissible.
Qualify on contact when both senses are near: "admissible card" vs "admissible evidence".

**Hold (a package)**:
To keep a skill package's files anywhere in this repository's tree, as a published card, a
candidate under `_quarantine/`, a fixture or a vendored copy, promoted or not. The collection
holds only packages it authored, because the tree is public and possession reads as provenance.
Settled by
[`docs/adr/0006-the-collection-holds-only-what-it-authored.md`](docs/adr/0006-the-collection-holds-only-what-it-authored.md).
_Avoid_: compose, which is to invoke another author's skill by name from its own source and is
permitted. Avoid also reading "unpromoted" as "not held": a candidate in `_quarantine/` is held.

**Occasion**:
One independent occurrence of the failure a card addresses, counted and dated after the fact.
Two is the threshold below which a card carries `RECURRENCE-THIN`.
_Avoid_: use, usage, invocation, dispatch — each counts runs of the card, and `ADMISSION.md`
criterion 2 refuses a count inflated by fan-out.

**Always-on**:
A card whose description loads into every session, so the model can invoke it on its own. A
published card may be always-on only when it clears the **always-on bar**: its `EVIDENCE.md`
counts two or more occasions, or a `Screen result` or `Paired verdict` row records a result other
than `UNMEASURED`. Settled by
[`docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md`](docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md).
_Avoid_: active, enabled, live. A by-hand card is installed and enabled too.

**By hand**:
A card whose `SKILL.md` frontmatter sets `disable-model-invocation: true`. Its description does
not load, the model cannot invoke it on its own, and the user runs it by name. A card ships by
hand when it is below the always-on bar, or when the topology rule in `AGENTS.md` makes it a
procedure.
_Avoid_: disabled, inactive, procedure as a synonym. A by-hand card works when invoked, and a
by-hand card need not be a procedure.

**Dispatch**:
One invocation of a card. Evidence of demand, never of recurrence, lift or worth.
_Avoid_: occasion — a card invoked many times over one failure has many dispatches and one
occasion.

**Release**:
The act of delivering changed cards to installed users. Delivery happens when a version bump
merges to `main`; the tag and the GitHub release record it afterwards. Before 2026-08-24 the
word named a tag that delivered nothing, because both install routes track `main`.
_Avoid_: tag, publish — a tag records a release and does not constitute one.

**Install path**:
The route by which the collection is installed, defined by what a consumer resolves: the
marketplace `name` and the plugin `name`s in `.claude-plugin/marketplace.json`, and the source
repository the marketplace is added from. Changing any of them is a major change, because an
installed user who takes no action loses a route that worked. The spelling of a command in
`README.md` §Install is not the route: two spellings that resolve to the same marketplace,
repository and plugin names are one route, and correcting the spelling is a patch. Settled by
[`docs/adr/0005-the-install-route-is-what-a-consumer-resolves.md`](docs/adr/0005-the-install-route-is-what-a-consumer-resolves.md).
Not a card's directory: that is the card's *name*, which is a separate part of the declared
surface and is priced differently.
_Avoid_: using it for `skills/<group>/<name>/`. The undefined phrase carried both senses until
2026-09-08 and is what made the surface question unanswerable from this glossary. _Avoid_ also
using it for the command text in `README.md` §Install, which it named until 2026-10-17.

**Declared surface**:
What the version number promises: the install path, a card's name, and the on-disk shape of a
card. The card *set* is deliberately outside it, so admitting or retiring a card is a minor
change rather than a breaking one — but renaming a card is a major change, because consumers
resolve a card by its name. Moving a card from always-on to by hand is also a major change,
because an installed user who takes no action loses a card that fired on its own; moving it back
is minor. This is Semantic Versioning's *public API* for this collection,
declared in
[`docs/adr/0002-a-release-is-a-delivery-event.md`](docs/adr/0002-a-release-is-a-delivery-event.md),
amended on the name by
[`docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md`](docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md),
and priced for load mode by
[`docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md`](docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md).
_Avoid_: bare "public API" — this collection ships no code interface, and the unqualified phrase
invites a reader to assume the card set is covered when it is not. _Avoid_ also treating a rename
as a retirement plus an admission: they are the same operation inside the repository and opposite
promises outside it.
