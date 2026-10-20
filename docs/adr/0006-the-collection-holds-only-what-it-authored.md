# The collection holds only what it authored

Status: accepted, 2026-09-14 (recorded 2026-10-20). Resolves
[#310](https://github.com/MrBinnacle/skills/issues/310). Extends the publication ruling in
[`dispositions/2026-09-04-S404-notion-proposal-review.md`](../../dispositions/2026-09-04-S404-notion-proposal-review.md)
line 206 from publication to possession.

## Decision

**This collection does not publish, or hold, a skill it did not author.** To hold a package is to
keep its files anywhere in this repository's tree: a published card under `skills/`, a candidate
under `_quarantine/`, a fixture, or a vendored copy. A package another author wrote is not held
here in any of those places, whether or not it is promoted, and whatever its merits.

**Composing a third-party skill is permitted.** To compose a skill is to invoke it by name at run
time from the place its author publishes it. The collection's own text may name such a skill and
tell an agent to run it. That is a dependency on the other author's work, and it keeps their
name on it.

The line between the two is the tree. This repository is public, and a package in its tree reads
as this collection's work, so possession states provenance whether or not anyone promotes the
package.

The rule is about whole skill packages. A card this collection wrote may still reproduce or
adapt text from another project under that project's license. `AGENTS.md` §"Source of truth &
maintainer workflow", promotion step 2, already governs that case: name the source and license,
and attribute in place ([`AGENTS.md:132-137`](../../AGENTS.md)). This record does not change
that step. The rule also does not reach the non-skill files vendored from the owner's own
`MrBinnacle/skill-harness` repository, `styles/Taste/` and `scripts/vendor/`. They are not skills,
and their source of truth is this collection's owner.

## What happened

The `self-documenting-code` candidate was written by theswerd and taken from the public
`theswerd/aicode` repository. Commit `26e1b2b` (#216, PR #227) landed it under `_quarantine/`.
Its own `PROVENANCE.md` named that source and said the candidate "fails ADMISSION.md criteria 1,
2, and 4". On 2026-09-14 a proposal was open at
[#305](https://github.com/MrBinnacle/skills/issues/305) to make that card the parent orchestrator
of this collection. It would recruit a third author's installed plugin as specialists and put this
collection's identity on the verdict they produced.

On 2026-09-14 the owner ruled: do not publish it at all, and keep it for the local harness only.
Commit `b8017fb` ([#312](https://github.com/MrBinnacle/skills/pull/312)) removed the package from
the repository. It is archived outside every repository.

## Why this is not the existing rule restated

The S404 review already refused to publish an upstream-owned skill as a card while endorsing its
use: "Compose it; do not republish another author's skill under this collection's identity."
([`dispositions/2026-09-04-S404-notion-proposal-review.md:206`](../../dispositions/2026-09-04-S404-notion-proposal-review.md)).
That ruling governed publication. It said nothing about whether the tree may hold another
author's package as an unpromoted candidate, and from `26e1b2b` to `b8017fb` the tree held one.
`ADMISSION.md` was silent on authorship, and that silence is what let the candidate land. This
record closes that gap.

The permitted side has a precedent in this repository's own process. `AGENTS.md` §"Repair is
skill authoring, so stack the skill that does it" tells the repair pass to "Run the repair through
`writing-for-agents` (Pocock plugin, `productivity/writing-for-agents`)"
([`AGENTS.md:616`](../../AGENTS.md)). That sentence composes another author's skill by name and
holds none of its files. It is the shape this record permits.

## Considered and rejected

**Publish the card on its own merits.** Rejected. Merit does not change who wrote it, and a card
in this collection carries this collection's identity. The candidate also failed three of the four
admission questions on its own record, so it had no merits to publish on yet.

**Keep it quarantined indefinitely.** Rejected. `_quarantine/` is in the public tree. A package
there reads as this collection's candidate, and an indefinite hold is publication of provenance
without the admission test.

**The #305 orchestrator proposal.** Rejected. It would have made another author's package the
parent of this collection and put this collection's name on the output of a third author's
plugin. That is the provenance problem at its largest.

## Consequences

- `ADMISSION.md` gains an authorship precondition that cites this record. It sits beside the
  four questions, not among them: a candidate this collection did not author never reaches the
  test. The four questions and what counts as answering them are unchanged, so under
  `ADMISSION.md`'s own bump rule the policy stays at `admission-policy v1`. No card admitted
  before this record is affected; every one was authored here.
- `GLOSSARY.md` gains **Hold**, with **compose** as the term it must not be confused with.
- **The cost.** #216 criterion 5 asked for `0.1.0` to be kept as the frozen executable baseline.
  That baseline now lives outside version control, in the archive the owner named. This is a
  deliberate trade: provenance outranks a versioned baseline for a package this collection did not
  write. Anyone who needs the baseline again takes it from its author's repository or from that
  archive, not from this tree.
- **The limit.** Removal from `HEAD` does not erase the bytes. Commits `26e1b2b` through the
  parent of `b8017fb` still carry the package in this public repository's history. Erasing them
  needs a history rewrite, and the owner has not authorised one. This record governs what the tree
  holds from now on. It does not claim the history is clean.

## Decision status

- **Non-negotiable:** that this collection does not publish a skill it did not author. This is
  the owner's ruling of 2026-09-14, and it restates the S404 publication ruling. A later session
  may enforce it differently. It may not admit another author's card under this collection's
  identity.
- **Revisable with new evidence:** that the rule reaches possession and not only publication.
  *Revisit if:* the owner decides a third-party package may be held privately in a repository
  that is not public. That would make the rule a property of publication rather than of
  possession, and this record would be superseded rather than amended.
- **Revisable with new evidence:** that the authorship precondition does not bump the admission
  policy version. *Revisit if:* a candidate is turned away under the precondition that the four
  questions would have admitted, which would show the precondition changes what enters and is
  material under the bump rule.

*Revisit if:* this repository stops being public, or comes to ship a mechanism that installs
another author's skill from its author's own source as part of this collection's install route.
Either would move the line between holding and composing, and this record would need a successor.
