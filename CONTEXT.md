# MrBinnacle / skills

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

**Occasion**:
One independent occurrence of the failure a card addresses, counted and dated after the fact.
Two is the threshold below which a card carries `RECURRENCE-THIN`.
_Avoid_: use, usage, invocation, dispatch — each counts runs of the card, and `ADMISSION.md`
criterion 2 refuses a count inflated by fan-out.

**Dispatch**:
One invocation of a card. Evidence of demand, never of recurrence, lift or worth.
_Avoid_: occasion — a card invoked many times over one failure has many dispatches and one
occasion.

**Release**:
The act of delivering changed cards to installed users. Delivery happens when a version bump
merges to `main`; the tag and the GitHub release record it afterwards. Before 2026-08-24 the
word named a tag that delivered nothing, because both install routes track `main`.
_Avoid_: tag, publish — a tag records a release and does not constitute one.

**Declared surface**:
What the version number promises: the install path and the on-disk shape of a card. The card
set is deliberately outside it, so admitting or retiring a card is a minor change rather than a
breaking one. This is Semantic Versioning's *public API* for this collection, declared in
[`docs/adr/0002-a-release-is-a-delivery-event.md`](docs/adr/0002-a-release-is-a-delivery-event.md).
_Avoid_: bare "public API" — this collection ships no code interface, and the unqualified phrase
invites a reader to assume the card set is covered when it is not.
