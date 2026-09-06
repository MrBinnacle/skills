---
"mrbinnacle-skills": patch
---

`AGENTS.md`: repair five defects in the authoring conventions, and put the section's model-behaviour claims under a dated screening mechanism recorded in a new `docs/rule-screens.md`.

The two authoring rules added earlier on 2026-09-06 were about to be propagated across fourteen published cards. An architecture review of the rules themselves, given the full conventions section rather than a three-rule extract, found defects in the rules. Migrating fourteen cards to a defective rule multiplies it, so the rules are repaired first.

**Cross-references.** The prior rule banned a trailing "Related" / "See also" section outright. Measured across the fourteen published cards: 21 of 47 reader-facing auxiliaries are named nowhere in their own `SKILL.md`, including `im-up`'s `PACKET-FORMAT.md`, which its card depends on. The count establishes that referencing is incomplete; it does not establish that the ban caused it, and that reading is recorded as a hypothesis. The replacement is role-based: operating resources linked at the step that needs them, evidence cited beside its claim, every reader-facing auxiliary reachable through local links, test and build resources out of the prose, an index permitted where it serves a lookup the inline pointers do not.

**Sizes.** "If `SKILL.md` is over 5 KB, split" was unconditional, which turns a size guideline into a reason to delete words. Above the target is now a mandatory review with a recorded disposition. The 7,168-byte ceiling is unchanged.

**The opening rule.** It required "one concrete thing it caught", which pressures an author to present an originating failure — or another mechanism's catch — as a catch by the card. Two cards did exactly that. It now requires the incident's evidentiary role to be named, and requires an unsettled attribution to stay unsettled.

**Frontmatter.** The rule said `name:` and `description:` "only" while the topology rule five lines below permits `disable-model-invocation:`. Both are now stated.

**`gotchas.md`.** The rule said to "replace or supplement" anticipated entries and, in the same sentence, never to delete them. Replacement is deletion. It now says append.

**The screening mechanism, in `docs/rule-screens.md`.** Every published card carries a `Re-screen trigger` row because a skill's worth depends on the model reading it. The rules governing those cards carried none.

A first draft of this put a paragraph in `AGENTS.md` dividing rules by audience — human-facing rules called stable, agent-facing rules called model-relative. That boundary does not hold: whether a `description` routes retrieval is a human-authored, human-installed property decided by the model. Rules are now classified by the property they preserve — `platform-compatibility`, `repository-integrity`, `human-comprehension`, `model-retrieval`, `model-execution` — and the new file specifies the trigger, scope, test surface, disposition vocabulary, record and owner.

The trigger is three events plus a 180-day lease, so the mechanism does not depend on anyone remembering it. The test surface for a model-behaviour claim is a screen in `skill-harness`; where none exists the disposition is `UNMEASURED`, which is a typed refusal and a legitimate outcome, never resolved by assertion. The file also states where authority stops, so the mechanism does not recurse: the rule set is the maintainer's, a model-behaviour claim inside it answers to a measurement, and the measurement lives outside `AGENTS.md`.

The first entry records every model-behaviour claim in the section as `UNMEASURED` as of 2026-09-06, which is the honest starting state, and carries the rationale for all five repairs so the rule text stays short.

`docs/rule-screens.md` also names which requirements are machine-checkable and ungated. Three of them are filed as skills#246.

No card changes in this changeset.
