---
"mrbinnacle-skills": minor
---

The collection ships a distribution artifact, and CI refuses any state where it disagrees with the tree.

Until now there was no `.claude-plugin/marketplace.json`. The only documented route in was a third-party installer named once in this file's own preamble, so the native plugin mechanism — the one a Claude Code user reaches for — did not know this collection exists. A collection nobody can install is not shipped, whatever its receipts say.

**What ships.** `.claude-plugin/marketplace.json` declares three plugins, one per bucket: `mrbinnacle-engineering`, `mrbinnacle-orchestration`, `mrbinnacle-meta`. Together their `skills` arrays name every published card exactly once.

**Grouping is one plugin per bucket, and that is a decision.** Any other grouping requires a hand-maintained card-to-plugin mapping, which is a second census to keep in sync with the tree — and this repository has just finished removing three separate layers that each asserted a census of the same tree. Per-bucket makes the conformance check a pure derivation with no judgement in it.

**The front page carries an install path.** A one-line install pointer sits in the masthead and a full `## Install` section covers both routes, states where each one writes, and states no count of anything. It also says plainly that an installed card's `description` is loaded at startup whether the card fires or not, so a reader can decide to take one bucket rather than three.

**The guard is `O7`, inside the existing obligation tuple rather than an eighth validator.** The repository already runs seven validators and seven suites, and the number of gates is itself a documented burden. `O7` asserts that the manifest and the published tree name the same cards, and it checks **both directions**:

- a path the manifest names with no card at it, and
- a published card that no plugin names.

One direction would not be enough, and the receipt for that is in this repository. The sibling occasions check ran forward-only — a count could not rise without a record — and an **undercount stayed green until August 2026**, because nothing asked the reverse question. A manifest check that validates only the paths it names has exactly that hole: drop a card from the manifest and every remaining path still resolves.

A third breach class was found by attacking the check after it was written, and it is the one that matters most. **A `_quarantine/` candidate has a real `SKILL.md`**, so a manifest naming one is neither dangling nor missing a published card — the two-direction check reported `PASS` while the manifest shipped an unadmitted card to everyone who installs. That was demonstrated green on the live tree before the category existed, and it is now `FAIL`: a named path that resolves but sits outside `skills/` is its own reported breach. The same demonstration is red now, and the failure names the candidate.

An absent or unparseable manifest is `FAIL`, not `CANNOT-CHECK`. The file is this repository's own artifact, so its absence is a breach rather than an unanswerable question. `CANNOT-CHECK` stays reserved for what this repository genuinely cannot see from inside itself, which is `O5` and nothing else.

**Both directions are mutation-verified, and the verification read which assertion failed by name.** Disabling the forward direction failed `O7 is FAIL when the manifest names a path with no card at it`; disabling the reverse direction failed `O7 is FAIL when a published card is named by no plugin`. Each mutation was confirmed to parse before it was scored, so neither was a stillborn mutant killed by the compiler rather than by the control. Seven fixture classes cover the space: clean, missing card, unexposed card, absent manifest, malformed JSON, one card named twice, and a quarantine candidate exposed.

One suite assertion was caught being vacuous during that work and fixed: it searched the whole report for a card name, and the card name appears in the report as its own row heading regardless. Both name-checking assertions now read the `O7` line specifically. That is this collection's own `success-test-accepts-any-output` card, applied to the change that adds a control.

**The conformance edition is now `conformance v2`.** Adding a standing obligation is a material change to the obligations, and that section's own bump rule says a material change bumps the version. Editorial changes do not.

**One acceptance criterion is met in substance rather than to the letter, and it is flagged rather than quietly satisfied.** The ticket asked for the install section in the first screen. An existing guard, `test_readme_admission_lead.py`, pins Admission method, Card map and Card evidence as the first three `H2` sections — the front page leads with the rule that governs membership, not with promotion. Rather than weaken an owner-set guard to satisfy a new ticket, the install *pointer* sits in the masthead above every `H2`, and the full section follows the pinned three. Both constraints hold. If the intent was that the full section must lead, that is a change to the admission-lead guard and belongs in its own decision.

*Revisit if:* a bucket is added or renamed, at which point the manifest gains a plugin and `O7` reds until it does.
