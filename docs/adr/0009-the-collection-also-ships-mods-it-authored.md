# The collection also ships mods it authored

Status: proposed, 2026-10-23. Accepted when the owner merges the pull request that adds it.
Widens the scope stated in `CLAUDE.md` § Scope and non-goals. Leaves the four admission
questions in [`ADMISSION.md`](../../ADMISSION.md), [ADR 0004](0004-a-plugin-is-its-own-root.md)
and [ADR 0006](0006-the-collection-holds-only-what-it-authored.md) unchanged. Applies the prices
of [ADR 0002](0002-a-release-is-a-delivery-event.md), [ADR 0003](0003-a-cards-name-is-part-of-the-declared-surface.md)
and [ADR 0005](0005-the-install-route-is-what-a-consumer-resolves.md) to a mod.

## What happened

On 2026-10-23 the owner built `tips-anywhere`, a Claude Code mod. A mod is a plugin whose
`hooks/hooks.json` names a hooks module that Claude Code runs inside the session. It changes the
interface or the behaviour of Claude Code directly. It loads no text into the model's context
window. `tips-anywhere` takes the heads-up notes of Claude Code's built-in "You should know" side
agent and asks about each one in the chat, with buttons, so that the notes reach the phone and
tablet apps, which do not draw the band where the notes appear on a computer.

The owner ruled the same day that the mod is published from this repository, not from a
repository of its own. Before this record, `CLAUDE.md` scoped the repository to "the skills
themselves, their evidence records, the published template, and the public-facing surfaces that
explain both". A mod is none of those, so the ruling needs a scope change, and this record makes
it.

## Decision

**This collection ships Claude Code mods that it authored, beside its cards.** A mod lives at
`mods/<mod>/`. It is its own plugin root, as a bucket is under ADR 0004: its own
`.claude-plugin/plugin.json` states its name and version, and it lists no `skills`. Its
marketplace entry is a `git-subdir` pin of this repository, the same form as a bucket's entry.

**The authorship precondition applies to a mod.** ADR 0006 governs skill packages. Its reason,
that possession in a public tree reads as provenance, applies to any package, so this collection
holds no mod it did not author.

**The four admission questions do not apply to a mod.** They test whether a skill deserves its
place in the context window. Question 3 asks whether "a skill is the correct control surface",
and for a mod the answer is no by construction. The `EVIDENCE.md` rows, the occasion count, the
always-on bar and the card validators exist to answer those questions, so they do not apply
either. A mod enters on two conditions instead:

1. `claude plugin validate mods/<mod>` reports no error.
2. `claude plugin test mods/<mod>` passes, and the suite tests the behaviour the mod's README
   claims.

The mod's README states what was verified, on which Claude Code build and date, and what was not.

**A mod's version moves with the collection's.** `release_gate.py` G1 stamps every plugin's
`plugin.json` from `package.json`, and a mod's manifest is one of them.

**A mod is priced as a card.** Adding or removing a mod is minor, as admitting or retiring a card
is under ADR 0002. Renaming a mod is major, because an installed user resolves it by its plugin
name, which is part of the install route under ADR 0005. A correction inside a mod is a patch.

**A mod enters at the next release.** A new marketplace entry cannot pin a release commit that
predates it. Until the next release ships, the entry names the current pin, and an install of
the mod fails because the pinned commit does not hold its folder. The next release's
`check_marketplace_pin.py --write` moves the entry with every other entry. The cost is that
window. Its length is the time from the merge of the mod to the next release, and the owner
controls it.

## What the gates change

- `check_marketplace_pin.py` reads each entry's `plugin.json` at the pinned release commit, so a
  new entry fails it. The check gains one exception: an entry that the marketplace at the pinned
  release does not list, and whose path that release does not hold, is reported as entering and
  is not a failure. Every other field of the entry is still checked. An entry the release already
  lists gets no exception, so the exception cannot hide a deleted plugin.
- `release_gate.py` G10 counts a directory under `skills/*/*/` that holds a `SKILL.md` as a
  priced unit. It gains a second kind of unit: a directory `mods/*/` that holds
  `.claude-plugin/plugin.json`. Without this, case 3 refuses the minor bump this record prices
  for adding a mod, because the diff touches no card.
- `validate_conformance.py` O7 needs no change. It reads each entry's `plugin.json`, finds no
  `skills` list in a mod's, and compares no cards for it.

## Considered and rejected

**A repository of the mod's own.** Rejected by the owner on 2026-10-23. It needed no gate change,
and it would have given the mod a separate install route and a separate version. The owner chose
one marketplace for the collection's work.

**Treat a mod as a card and run the four questions on it.** Rejected. Question 3 fails for every
mod by construction, so the test would refuse every mod and say nothing about its worth.

**Price a mod outside the declared surface, so that every mod change is a patch.** Rejected. A
renamed or removed mod breaks an installed user's route in the same way a renamed card does, and
ADR 0005 prices that route.

## Decision status

- **Non-negotiable:** that this collection holds no mod it did not author. It follows from ADR
  0006's reason, which is the owner's ruling.
- **Revisable with new evidence:** that a mod enters on `validate` and `test` alone. *Revisit
  if:* a published mod ships a defect that its own suite passed, which would show that the two
  conditions do not answer whether a mod works.
- **Revisable with new evidence:** that a mod's version moves with the collection's. *Revisit
  if:* the collection ships enough mods that their releases and the cards' releases block each
  other.
