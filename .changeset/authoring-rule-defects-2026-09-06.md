---
"mrbinnacle-skills": patch
---

`AGENTS.md`: repair five defects in the authoring conventions, and lodge a re-screen trigger on the section itself.

The two authoring rules added earlier on 2026-09-06 were about to be propagated across fourteen published cards. A second architecture review, given the full conventions section rather than a three-rule extract, found defects in the rules themselves. Migrating fourteen cards to a defective rule multiplies it, so the rules are repaired first.

**Cross-references.** The prior rule banned a trailing "Related" / "See also" section outright. Measured across the fourteen published cards that day: 21 of 47 reader-facing auxiliaries are named nowhere in their own `SKILL.md`, including `im-up`'s `PACKET-FORMAT.md`, which its card depends on. The count establishes that referencing is incomplete; it does not establish that the ban caused it, and the amendment says so. The new rule is role-based: operating resources are linked at the step that needs them, evidence is cited beside its claim, every reader-facing auxiliary is reachable through local links, and test and build resources stay out of the prose. An index is permitted where it serves a lookup the inline pointers do not.

**Sizes.** "If `SKILL.md` is over 5 KB, split" was an unconditional command. It turns a size guideline into a reason to shave words, and 5,120 and 5,162 bytes have no different operating property. Above the target is now a mandatory review with a recorded disposition, not a compulsory split. The 7,168-byte ceiling is unchanged.

**The opening rule.** It required "one concrete thing it caught". That wording pressures an author to present an originating failure, or another mechanism's catch, as a catch by the card. It is now required to name the incident's evidentiary role — originating failure, later application, or a catch attributable to this card — and to leave the attribution unsettled where the record cannot settle it. A date supplies provenance, not causality.

**Frontmatter.** The rule read `name:` + `description:` only, while the topology rule five lines below permits `disable-model-invocation:`. The schema now states both.

**`gotchas.md`.** The rule said to "replace or supplement" anticipated entries and, in the same sentence, never to delete them. Replacement is deletion. It now says to append an observed entry or a status update naming the earlier one.

**A re-screen trigger on this section.** Every published card carries a `Re-screen trigger` row because a skill's worth depends on the model reading it. The rules governing those cards carried none. The new clause divides rule intent by who it serves: a rule serving a human deciding whether to install is stable as models change, and a rule serving an agent executing is not, because a more capable reader needs less scaffolding. The section is now re-screened when a frontier release changes what a card must spell out, with the finding recorded — including a finding of no change.

No card changes in this changeset.
