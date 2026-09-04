---
"mrbinnacle-skills": patch
---

`dispositions/`: a disposition record for the 2026-09-04 review of twelve proposed card updates and additions held in the maintainer's private skills registry.

The registry supplied candidate architecture. This repository supplied executable truth, and where the two disagreed the repository decided. Four findings shaped the outcome.

The registry asserted a published card this repository had deleted. Its `skill-necessity-gate` row read `Lifecycle: Published` with a source link into `blob/main/skills/meta/skill-necessity-gate/SKILL.md`, a path removed on 2026-08-31. The proposal to extend that card had no artifact to extend, and re-admitting it would need an observed occurrence its record has never held. The useful half of the proposal is relocated to `AGENTS.md` as a convention.

The registry also recorded a per-card version number that published cards do not carry: two rows read `Version: 1.4.0`, which is the collection version in `package.json`, not a property of either card. Published card frontmatter holds `name` and `description` and nothing else.

One changeset against a published card is authorised, and its justification was already in the tree rather than in any annotation. `parallel-review-disposition-schema` carries an `[OBSERVED]` gotcha dated 2026-08-17 in which a reviewer-local identifier collision silently dropped a real finding for four commits. The entry names three mitigations and the card's prescribed schema carries none of them.

The compatibility question on `subagent-research-reliability` resolved against consuming a shared return envelope, on a structural ground: a dead letter produces no envelope, so a return contract cannot reduce the lost-return failure that card exists to catch.

The record authorises no rename, no overwrite of a published artifact, no evidence change, no trigger broadening, and no publication. Five candidates are deferred with their blocking measurements stated, and six exclusions are confirmed against repository rules rather than accepted on the filing.
