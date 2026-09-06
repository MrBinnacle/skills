# Rule screens

`AGENTS.md` governs how cards are written. Some of its rules make claims about model behaviour, and model behaviour changes. This file is where those claims are screened, and where the rationale for each amendment lives so the rule text itself can stay short.

Two things this file settles, because `AGENTS.md` points at it rather than restating them.

## Why the rules need this at all

Every published card carries a `Re-screen trigger` row, because a skill's worth depends on the model reading it. The rules governing those cards carried no equivalent until 2026-09-06. They were being applied as settled twelve hours after being written.

That asymmetry has a limit worth stating plainly, because the obvious fix recurses. If `AGENTS.md` says rules must be evidence-backed, and `AGENTS.md` is itself a rule, what validates it?

The recursion stops here, at one level, in two moves. **Authority over the rule set is the maintainer's** — a rule is in force because the maintainer put it in force, not because a document says rules should be evidence-backed. **Authority for a model-behaviour claim inside a rule is the measurement**, and the measurement is recorded in this file, which is not `AGENTS.md`. A rule can therefore be in force and `UNMEASURED` at the same time; that combination is legal, it is visible, and it is the honest state for most rules today.

Evidence travels one way. A measurement can oblige a rule to be reconsidered and can supply the finding that a screen records. It cannot amend the rule by itself, and a pending measurement does not suspend a rule that is already in force.

## Classify by the property preserved, not by who reads it

The first draft of this mechanism divided rules by audience: rules serving a human deciding whether to install were called stable across model generations, rules serving an agent executing were called model-relative.

That boundary does not hold. A human-facing rule can still turn on model behaviour. Whether a `description` successfully routes retrieval is decided by the model, not by the reader who wrote it. Whether a compact procedure can be followed, whether an omitted prerequisite gets inferred, whether a resource index is actually traversed — all are installation-time concerns settled by model capability.

So a rule is classified by the property it preserves. Five classes:

| Class | The property | Re-screened when |
|---|---|---|
| `platform-compatibility` | A limit imposed from outside this repository | The external contract changes |
| `repository-integrity` | Required files, schemas, append-only guarantees, gate behaviour | The repository contract changes |
| `human-comprehension` | A reader can tell what the card does and decide to install it | Reader evidence says otherwise |
| `model-retrieval` | The card gets reached when it should | The retrieval surface or the model changes |
| `model-execution` | The card is followed correctly once loaded | The executing model changes |

A rule may carry more than one class. Record every class that applies; a rule screened under one class and silent on another is `UNMEASURED` for the other.

## The mechanism

**Trigger.** A screen is due when any of these is observed. The first three are events; the fourth is a lease, and it is what makes the mechanism survive nobody remembering it.

1. The model serving Claude Code by default changes.
2. The skill-retrieval mechanism, the frontmatter schema, or the context budget available to a card changes.
3. A card fails in a way attributable to a rule in `AGENTS.md`.
4. 180 days elapse since a rule's last recorded screen.

A screen is not due merely because a model was released. A release that changes none of the surfaces above changes nothing here.

**Scope.** Rules classified `model-retrieval` or `model-execution` are screened on triggers 1, 2, 3 and 4. Rules classified `platform-compatibility` or `repository-integrity` are screened on triggers 2, 3 and 4. Rules classified `human-comprehension` only are screened on triggers 3 and 4. A rule's classes are recorded here on its first screen and carried forward.

**Test surface.** A `model-retrieval` or `model-execution` claim is tested by a screen in `skill-harness`, which is the instrument that exists for exactly this question. Its receipt is the evidence, and its verdict vocabulary is the vocabulary that evidence is reported in. **It is a measurement surface, not a source of authority over this contract.** A screen produces evidence that may require a rule to be reconsidered; it does not rewrite the rule, and an experiment running against the instrument does not redefine what the instrument means here. The disposition is recorded against the rule, and the rule remains the maintainer's. Where no screen exists for the claim, the disposition is `UNMEASURED`. Do not substitute a judgement for a measurement, and do not manufacture a number in place of a missing one. A `repository-integrity` or `platform-compatibility` claim is tested by running the validator or reading the external contract, and the command and its output are the evidence. A `human-comprehension` claim is tested by a reader who has not seen the card before, and their report is the evidence.

**Disposition.** One of three, per rule, per screen.

- `NO CHANGE` — the rule was tested against the named surface and held. Requires the evidence, not an assertion that nothing looked different.
- `REVISE` — the rule was tested and did not hold. Names what failed and what replaces it.
- `UNMEASURED` — no test surface existed, or the test could not run. Names the search that established that, and what would close it. This is a typed refusal and it is a legitimate outcome. A screen consisting entirely of `UNMEASURED` rows is an honest screen.

**Record.** One dated section per screen, appended below. Never rewritten — a screen is a record of what was found on a date, and editing it destroys the only property it has. A correction is a new entry naming the earlier one.

**Owner.** The maintainer. An agent may run a screen and propose its dispositions; the maintainer decides whether a `REVISE` lands.

## Which rules are gated, and which are judgement

`AGENTS.md` states normative requirements that nothing currently checks. That gap is named here rather than left implicit, because this repository's stated position is that a discipline you require to fire cannot depend on someone remembering it.

| Requirement | Status |
|---|---|
| `SKILL.md` within 400–7,168 bytes | **Gated** by `scripts/validate_card_files.py` (skills#246). |
| Every reader-facing auxiliary reachable from `SKILL.md` | **Gated** by `scripts/validate_card_files.py`, with a reviewed exemption list for test and build files (skills#246). |
| Local links resolve, including case | **Gated** by `scripts/validate_card_files.py` (skills#246). |
| Required files present, required evidence rows present | **Gated** by `scripts/validate_card_files.py`. |
| `description` at or under 200 characters | **Gated.** |
| The opening names the incident's evidentiary role | Partly syntax-checkable; the honesty of the classification is not. Judgement. |
| Size disposition recorded above the target | Judgement. |
| Plain writing | Judgement. A word-count test cannot establish it. |
| This screening mechanism | Judgement. |

A requirement in the judgement rows is not weaker. It is one that a checker would report green on while being wrong, which is worse than no checker.

---

# Screens

## 2026-09-06 — the section's first amendment, and why

This entry is the rationale for the amendments landed that day. It is not itself a screen: nothing here was tested against a model, and every model-behaviour claim in the section is therefore `UNMEASURED` as of this date. That is the honest starting state.

**Cross-references — `REVISE`, on repository evidence.** The prior rule read *"inline at moment-of-need. No trailing 'Related' / 'See also' section."*

Measured across the fourteen published cards: **21 of 47 reader-facing auxiliaries are named nowhere in their own `SKILL.md`.** `im-up` ships a `PACKET-FORMAT.md` its card depends on and never mentions. Twelve of fourteen cards do not link `EVIDENCE.md`.

An earlier count said 32 of 59. That figure counted test fixtures and a test script as discoverability failures; no reader should traverse those. 21 of 47 is the count by role.

The count establishes that referencing is incomplete. **It does not establish that the prohibition caused it.** That reading is a hypothesis and is recorded as one; the replacement rule does not depend on it. Class: `human-comprehension`, `model-execution`. The `model-execution` half is `UNMEASURED` — whether an unreachable auxiliary changes what an agent does has not been screened.

**Sizes — `REVISE`, on internal inconsistency.** The prior rule read *"If `SKILL.md` is over 5 KB, split."* An unconditional split command converts a size guideline into a reason to delete words. Observed the same day: a card reached 5,162 bytes after a 45% reduction and one sound extraction, and the only remaining move to clear 5,120 was shaving individual words against the plain-writing rule. 5,120 and 5,162 bytes have no known different operating property. No consumer is known to reject a card at either size, and no search for one has been run — so `UNMEASURED`, not "no such consumer exists". If one is found, that number becomes a compatibility limit and the rule is rewritten around it. Class: `platform-compatibility`, `model-execution`.

**The opening rule — `REVISE`, on two measured instances.** The prior wording required *"one concrete thing it caught."* That pressures an author to present an originating failure, or another mechanism's catch, as a catch by the card.

Two cards did exactly that. `halt-as-deliverable` asserted that a gate catching its author *"proves the discipline works on real, unrehearsed material"*; the record shows the catching was performed by a measurement harness's own pre-flight gates, and the card governs what to publish afterward. `subagent-research-reliability`'s two 2026-05-28 incidents motivated its checks rather than being caught by them. A third card, `closure-mode-at-boundaries`, could not be classified from its record at all and stays `UNCERTAIN`. Class: `human-comprehension`.

**Frontmatter — `REVISE`, on internal contradiction.** The rule said `name:` and `description:` "only" while the topology rule five lines below permits `disable-model-invocation:`. Class: `repository-integrity`.

**`gotchas.md` — `REVISE`, on internal contradiction.** The rule said to "replace or supplement" anticipated entries and, in the same sentence, never to delete them. Replacement is deletion. Class: `repository-integrity`.

**Next screen due:** 2027-03-05 by lease, or earlier on trigger 1, 2 or 3.
