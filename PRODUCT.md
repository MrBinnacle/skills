# Product

<!-- impeccable:product-schema 1 -->

<!--
Written by `impeccable init`, 2026-08-25.

No interview was run. An answer mechanism already existed and was used instead: the three init
questions were answered from this repository with verbatim citations, in the owner's research
repo. Q2 and Q3 come from a compiled answer pack; Q1 was derived from the shipped cards'
EVIDENCE.md Origin rows by two independent agent passes.

⛔ This file does not restate inventory tallies. Every such count tracks repository state and goes
stale between writes -- three separate figures rotted between an answer pack compiled 2026-08-25
and this file written the same day. Where a tally matters, the derivation command is given instead
of the number. AGENTS.md:440 records the owner ruling against restating tallies. The few counts
that appear below are fixed properties of published artifacts (the banned-word list size, the
scoreboard assertion sites, the screened-out candidates recorded in RETIRED.md), not inventory
tallies that go false when a card moves.

⛔ Per BRAND.md:21-23 an agent may not approve copy onto a public surface. No line in this file is
new public copy. Every quoted line is quoted from a surface the owner already approved.
-->

## Platform

web

## Users

⚠ **Read the status line before using this section. It is not a claim about who uses this
repository.**

**Status: derived design hypothesis. Not observed, not measured, not claimable in public copy.**

No adoption receipts exist. This file states the rule the repository already lives by: *"No
verified adoption metrics (installs, stars, external users); do not claim any."* An
audience noun is a claim about who the users are, so **naming one publicly would be the same
defect as printing an unmeasured figure.** Owner ruling, 2026-08-25: *"I can't very well say
something like 'real engineers' cuz how would I know."*

⛔ **This section may steer design and structural decisions. It may NOT be quoted outward** — not
as a tagline, a README line, a repository description, or a social card. It is an input to
building, never an output to publish.

**The hypothesis.** Reasoned backward from what the shipped cards address, not from observation of
any person:

> The operator of an agent rig they built themselves. A working engineer who has automated enough
> of their own work that they no longer witness most of it, and who has therefore written their
> own layer of checks between themselves and their agents. Their unit of work is a session, not a
> file. They have delegated enough that the reports are all they have.

**Situation of use.** Not catalog browsing. Three entry moments:

1. **Post-incident** — something reported success and it was not true, and the reader now
   distrusts a whole class of report.
2. **Pre-build** — the reader is about to write a hook, guard, router predicate, retry loop,
   parallel dispatch or handoff packet, and wants the known silent-failure modes first.
3. **Setup or change of environment** — the runtime, project or workflow has changed, and the
   reader wants to know which controls actually apply before installing or enabling anything.
   This third moment is a design hypothesis carried by [the broader product map](https://github.com/MrBinnacle/skills/issues/418)
   and existing issue #407, not an observed user pattern.

**Explicit anti-trigger: coverage-driven browsing.** Do not optimize for a card for every possible task or for catalog size. The new product journey starts from the user's actual workflow, environment and observed failure; it decides whether a control is needed and at which layer. A skill is one possible answer, alongside a rule, guard, check, setup change or no intervention. The repository already refuses to maximize coverage, in its own words: *“The repository is not intended to maximize coverage. The admission policy keeps it small. If you want breadth, [Matt Pocock's skills collection] is a better place to browse.”* (CATALOG.md:31.) The wider product keeps that restraint while adding applicability-aware selection as an explicit design goal; it does not imply that per-card switching is available on every install route.


**Job.**

> When an agent, a test, a hook or a previous session reports that a step succeeded and I did not
> watch it happen, I want to know the specific ways that class of report is known to lie and the
> cheapest check that settles it, so I can keep delegating without silently shipping work that
> never ran.

**Three constraining properties**, each derived from the cards:

1. **The reader does not witness the work.** Every card addresses a moment where a person is
   reading a report instead of watching an action.
2. **The reader built the checking layer themselves.** In the majority of admitted cards the thing
   that failed was the author's own test, hook, guard, predicate, packet or dispatch — not a
   third-party tool.
3. **The reader's problems survive a frontier model.** ADMISSION.md admits a card only where a
   current frontier model, without the skill, still fails. This structurally excludes everything
   the model already handles.

**Grade of this finding.** Two convergent agent derivations. That is a T1-grade result under the
owner's tiered-grader ladder — enough to steer this file, **not** enough to place a persona
sentence on a public page. That would want the T3 rung, an external human respondent.

⚠ **Undecided, and the record points both ways.** Whether the intended primary user is anyone
other than the author. Toward the author: every card origin and every counted occasion is his;
an unselected front-page draft said *"the skills I have found useful enough to keep developing and
maintaining"* (docs/design/variants/front-page/variant-1.md:20); BRAND.md:75-76 says the account
starts with his question, *"not with a market."* Toward other people: two
install routes, a plugin marketplace manifest, an admission policy written to be read by
strangers, and a design draft costing out context for the installer — *"breadth you do not use is
still paid for"* (docs/design/variants/front-page/variant-5.md:38). **This is a
product-direction decision and it is the owner's. Recorded undecided rather than invented.**

## Product Purpose

**Current shipped surface.** This repository currently distributes agent skill cards, each with an evidence record of where it came from and what has and has not been tested. The record is published so the record can be checked by someone who did not write it. This is the current implementation, not the permanent boundary of the product.

**Owner-directed product scope (2026-10-13).** The product ambition now extends beyond “Skills.” Treat this repository as the intervention catalog and operator-facing adoption layer of an evidence-governed reliability system for delegated AI work. Its intended job is to help an operator determine which control, if any, applies to their actual workflow and environment; provide that intervention at the right layer; and keep the resulting claims checkable over time. A skill is one control type and a current delivery format, not the product's defining boundary.

The intended loop is: understand environment and exposure → choose the correct control layer → deliver the intervention → qualify the exact task, subject/runtime and mechanism → observe outcome and consequence → retain scope, cost, provenance, evidence and re-check triggers → update, disable or retire. This is a product-design direction directed by the owner, not a verified claim about users, adoption, efficacy or market demand. The working thesis and sequence are in [the agent-reliability product thesis](docs/product/agent-reliability-system-thesis.md).

**What this repository owns.** It owns the intervention catalog and its admission/evidence contracts, the skill cards and portable operating-rules template, and the operator-facing adoption work that helps people choose and configure applicable controls. Evaluation execution and verdict machinery remain with the sibling measurement instrument; research and method development remain in the research/decision layer. Share explicit contracts across those surfaces rather than duplicating their internals or collapsing repositories without a concrete reason.

**Success.** An operator can map real conditions to an appropriate control or a justified no-control answer, understand the control's costs and limits, check what was actually tested, and know when it should be re-evaluated or removed. The operator can do so without treating a published or admitted card as empirically proven.

**Admission remains binding for skill cards.** [ADMISSION.md](ADMISSION.md) continues to govern what may enter the skill collection, with “not admitted” as its default. Other control types do not automatically pass through that policy by analogy; each needs an appropriate, explicit contract and evidence path before it becomes a deliverable.

## Positioning

The mechanism a neighbouring collection could not truthfully copy: **this collection turns
candidates away, including its own author's, and publishes the refusals with the measurement plan
filed before the runs.**

RETIRED.md:3, 26: *"Most collections only ever grow. This one also turns skills away —
including its own... Turning away your own work costs something: it makes the collection look
smaller. That cost is the point."*

RETIRED.md:93-107: *"In July 2026, four of the author's own candidate skills were screened before
admission... All four returned three passes out of three with no skill present... including
skills the author was personally convinced were valuable."*

One skill, `claude-code-stop-hook-envelope`, was retired against a trigger registered before the
platform change that fired it.

The current distinction belongs to the skill-collection surface. At the broader product level, the working positioning hypothesis is the complete control lifecycle: identify applicable conditions, choose the correct control layer, qualify the intervention, preserve the evidence, and remove or revise controls when their conditions no longer hold. That system-level distinction is not yet implemented end to end and must not be quoted outward as a current capability.

⚠ **The problem addressed is a credence-good problem**, stated for the sibling instrument and true
here: a reader cannot evaluate a skill before installing it, and mostly cannot tell afterwards
either. The response is not a better claim. It is a checkable record.

⛔ **Two framings are excluded from this file and must not be reintroduced.**

- Any "N of M" selectivity ratio. One such figure was carried for several sessions and was
  falsified — no source contained it.
- The private population census gated on an open owner fork. Its existence is noted; its contents
  are not reproduced.

⚠ **Not ratified as copy:** a proposed buying-criterion line exists in the owner's research repo,
recorded there as a recommendation. No source records the owner adopting it. It is deliberately
not reproduced here, because doing so would launder a candidate line into a product record.

## Operating Context

- **Distribution** is GitHub plus a plugin marketplace manifest. The plugin version is stamped
  from `package.json` at release; a consumer receives a version bump, not every merge to `main`.
- **A release is a delivery event**, per ADR 0002
  (docs/adr/0002-a-release-is-a-delivery-event.md): changed cards reach installed users when a
  version bump merges to `main`. site/index.html:164 states what a version promises — the install
  path, a card's name and the card format.
- **The reader's environment** is Claude Code across multiple sessions and parallel subagents,
  against real repositories. A card is consumed by an agent at runtime and by a human deciding
  whether to install.
- **Context is a cost the reader pays.** A design draft costing out that cost:
  *"breadth you do not use is still paid for"* (docs/design/variants/front-page/variant-5.md:38).
  Every published card's description is capped at 200 characters, CI-checked.
- **Every shipped card carries three files**: `SKILL.md`, `EVIDENCE.md`, `gotchas.md`. A card
  missing from its bucket README or the top-level listing is by definition not shipped.
- **Cards under `_quarantine/`** are candidates. They are not shipped and not installable.

## Capabilities and Constraints

**Governed lifecycle.** Admission, placement, promotion and retirement are repository behaviour
enforced by executable checks, not prose someone must remember to apply. `AGENTS.md` carries the
rituals; read them there rather than from memory.

**Mechanically derived counts.** The scoreboard is asserted in five places across three files, and
`scripts/validate_scoreboard.py` derives the values from the skill directories and `RETIRED.md`,
refusing a partial edit. ⛔ **Any count is re-derived at use, never quoted:**

```
git ls-files 'skills/**/SKILL.md' | wc -l        # shipped cards
git ls-files '_quarantine/**/SKILL.md' | wc -l   # candidates
```

**Provenance categories are not quality scores.** CATALOG.md:158-160 and AGENTS.md:435-436 define
OBSERVED / DESIGNED / DISTILLED as where a card came from, and CATALOG.md:151-152 keeps that axis
separate from what has been measured. The distinction must survive any presentation change.

**Terminology is fixed.** `GLOSSARY.md` is the glossary of record and fixes the meaning of *Card*,
*Occasion*, *Dispatch*, *Admitted*, *Admissible*, *Release* and *Declared surface* on every
surface. ⚠ It deliberately defines no term for the user; see `## Users`.

**Undecided product facts, recorded rather than invented** — all owner-only, all already open in
the repository:

- The social card's primary line, deliberately unset.
- Which of the GitHub About text and `package.json`'s description is authoritative where they
  diverge. They currently do.
- Whether the intended user is anyone other than the author (see `## Users`).

One formerly undecided fact is settled and is not repeated above: a public project page exists.
`site/index.html` deploys to https://mrbinnacle.github.io/skills/ (the pages workflow; the
homepage was measured as set on 2026-09-06).

## Brand Commitments

**Authorship of public lines is the owner's.** BRAND.md:21-23, verbatim: *"The owner writes the
public lines. An agent drafts candidates and labels them as candidates. Approving your own copy
onto a public surface is outside your authority."*

**Voice specimens must be cited.** Every specimen cites `VERBATIM.md`; uncited specimens are
removed rather than kept. Roughness — double spaces, missing apostrophes, hedges — is provenance
and is preserved deliberately.

**Polish is a failure mode here.** BRAND.md:35-41: *"a draft that reads smoother than the README
is off-voice regardless of how good it is... Polish is the verbal form of dressing... both make a
limitation look like a claim."*

**Register is fixed per surface.** README, repository description and social card: plain first
person, shortest true version. ADMISSION, AGENTS and skill cards: technical and procedural.
`EVIDENCE.md`: flat and factual, adjectives off results. `RETIRED.md`: matter-of-fact, without
apology or triumph.

**Banned words**, enforced by `validate_brand_kit.py` against `assets/tokens.json`. Fifteen
words, listed at `copy.words_to_avoid`, binding every line of prose this repository publishes
and not public asset copy alone: the operator ruled on 2026-09-06 that one list governs every
line in every repository. `copy.words_to_avoid_digest` publishes the sha256 of the list
itself, so a vendored copy can prove it is current without diffing this file.

**The one absolute visual rule.** DESIGN.md § Dressing: *"dressing the inventory as a measurement.
A skill being kept is an inventory fact. A skill having been measured is an evidence fact. Any
move that makes the first look like the second is dressing, and it breaks the only claim the
repository makes."* The sibling instrument's palette is banned here for exactly this reason.

⚠ **A cautionary precedent, closed on 2026-09-06.** The retired tagline, quoted in full at
`tokens.json > copy.words_to_avoid_notes`, was cleared from three text surfaces and survived on
`assets/social-preview.png`. The raster is now an export of `assets/social-preview.svg`, checked
by `validate_brand_kit.py` as part of the `assets/*.svg` banned-copy surface, with the SVG and
PNG recorded as a hash pair. A word ban that holds in text can still fail in a raster asset.

## Evidence on Hand

**Real and checkable:**

- `EVIDENCE.md` per shipped card, carrying a dated origin incident, a recurrence count and a
  stated screen result.
- `ADMISSION.md`, the admission policy, versioned.
- `RETIRED.md`, recording one retirement against a pre-registered trigger, and four of the
  author's own candidates screened out before admission.
- `VERBATIM.md`, the voice-specimen source of record.
- `assets/tokens.json`, the design token source of record, CI-checked.
- The sibling measurement instrument and its published receipts site, which is where efficacy
  questions are answered rather than here.

⛔ **Absences future work must not fabricate.** Stated so they cannot be filled by inference:

- **No verified adoption metrics.** No installs, stars, external users or downloads. This file
  forbids claiming any; the rule is stated in `## Users` and here.
- **No efficacy claim for any shipped card.** Screening establishes that an unaided failure
  existed. It does not establish that the card fixes it.
- **No testimonials, case studies, press, customers or usage data.** None exist.
- **No user research.** `## Users` is derived from artifacts, not from any person.
- ⛔ `assets/tokens.json` `evidence_rules`, verbatim: *"Every number must resolve to a repository
  artifact."* and *"Never invent waveform traces, terminal output, sample verdicts, user counts,
  stars, testimonials, or performance metrics."*

## Product Principles

1. **Default answer: not admitted.** Growth is not the goal. A smaller collection that can be
   checked beats a larger one that cannot.
2. **Inventory state is never rendered as evidence state.** Kept is not measured. This is the one
   failure the whole system exists to prevent.
3. **A refusal is publishable content.** Turning away the author's own work, and saying so by
   name, is a cost the collection pays on purpose.
4. **Every number resolves to a repository artifact, or it is not stated.** A count that cannot be
   re-derived at read time does not belong on a surface.
5. **The author is not an admissible source about the author.** Quality and audience claims
   require a party who is not the owner. This is why `## Users` carries its grade and stops at the
   design layer.

## Accessibility & Inclusion

No product-specific standard has been established for this repository, and none is invented here.

One factual practice is already in place and future work must preserve it: every SVG asset under
`assets/` carries `role="img"` and an `aria-label`. For the two banners that `aria-label` is one of
the five scoreboard assertion sites `scripts/validate_scoreboard.py` holds in lockstep — so an
accessibility attribute is also a validated claim here, and editing one without the others turns
the build red.
