<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# MRBINNACLE / skills

I wanted to know if you could tell if a skill was good.

This repository is my attempt to keep that question attached to each card. The card, its source, its tests, its evidence and the condition that would retire it belong together. A sensible-looking skill is not evidence that it changes anything. A run that never reaches the failure a card targets cannot establish that the card prevents it.

**Publication is not validation.**

## Install

This repository currently ships through three Claude Code plugin groups. Run the marketplace command and each install command separately.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

The other groups are `mrbinnacle-orchestration` and `mrbinnacle-meta`. Install either with the same command form, substituting its name. After installation, run `/reload-plugins`. If the reload is pending, use `/reload-plugins --force` or start a new Claude Code session.

The shell form is also supported. Run these as separate commands:

```bash
claude plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```bash
claude plugin install mrbinnacle-engineering
```

The [`skills` CLI route](https://github.com/vercel-labs/skills) is another way to install the collection:

```bash
npx skills add MrBinnacle/skills
```

Check the installed plugin versions with `claude plugin list`.

## What is here

| Group | What it covers | Index |
|---|---|---|
| Engineering | Git, tests, deployment checks, command guards and other places where a success signal can be wrong | [Engineering skills](skills/engineering/README.md) |
| Orchestration | Handoffs, delegated work and decisions that need a checkable return | [Orchestration skills](skills/orchestration/README.md) |
| Meta | Routing and dispatch failures inside the skill system | [Meta skills](skills/meta/README.md) |

The cards are not meant to cover every possible task. A skill is the wrong answer when the failure does not recur, the model already handles it, or a different control is the right place to act. Admission has a rule; adding a card is not the default.

## Read the record

A skill's `SKILL.md` is the instruction an agent receives. Its `evals/evals.json` holds test cases. Its `EVIDENCE.md` records the origin and the evidence available for that card. Read those files before treating the card as a recommendation.

- [Catalog and evidence map](CATALOG.md) links the published cards to their recorded states.
- [Admission policy](ADMISSION.md) sets the criteria for adding a card.
- [Retired cards](RETIRED.md) records what left and why.
- [Quarantine](./_quarantine/README.md) explains the status of candidates that have not been admitted.
- [Security commitments](SECURITY.md) describes the project's security posture.
- [`skill-harness`](https://github.com/MrBinnacle/skill-harness) holds the evaluation apparatus, not this repository.

Three distinctions matter when reading the evidence:

- **Origin is not effect.** `OBSERVED`, `DESIGNED` and `DISTILLED` say where a card came from. They do not say whether it helps.
- **A passing task is not automatically a skill effect.** The comparison must establish what changed between a run with the card and a run without it.
- **A missing or inconclusive result is not a pass.** `UNMEASURED` and `CANT_TELL_YET` are valid states. Their explanations belong beside the relevant card, not in a universal badge.

The admission policy asks whether an unaided failure exists, whether it recurs independently, whether a skill is the right control surface, and whether evidence supports admission and later retirement. An unanswered criterion counts as no. Candidates wait in quarantine; retirements stay in the record.

## The broader design under review

The proposed direction is to make this repository the published intervention catalog and adoption surface for a larger agent-reliability system. That system is not delivered end to end today. The current proposal separates responsibilities rather than copying everything into this repository.

| Surface | Intended responsibility | Boundary that remains important |
|---|---|---|
| GitHub | Canonical bytes and revisions for published capabilities | A knowledge-base description does not override the current file |
| Notion | Shared context, source relationships, hypotheses and accepted decisions | Context is not evidence that a runtime received a capability or that it worked |
| Pi | First implementation of an owner-controlled agent layer, with model and provider kept replaceable | The exact `skills-pi` distribution path is not yet verified |
| Claude Code | Current distribution and compatibility route | Shared `SKILL.md` format does not establish equivalent discovery, loading, invocation or behavior |
| `skill-harness` | Controlled evaluation, measurement and evidence receipts | The Pi evaluation adapter is not the same thing as a `skills-pi` installer or package |

The draft [product contract](docs/product/product-contract.md) defines the proposed capability, context, runtime-delivery, evaluation and lifecycle interfaces. The [product thesis](docs/product/agent-reliability-system-thesis.md) explains the intended operator journey. Both remain proposed until reviewed and accepted.

The next source checks are tracked in [#420, runtime delivery and artifact identity](https://github.com/MrBinnacle/skills/issues/420) and [#421, the Notion context audit](https://github.com/MrBinnacle/skills/issues/421). They are audits, not announcements that those integrations already work. No shared format, installer test or adapter test substitutes for evidence that a specific capability was delivered, invoked or had an effect.

## Adding a skill

Start with [ADMISSION.md](ADMISSION.md), not a blank card. Record the failure and independently counted occasions. Check that a skill is the right control surface. Preserve the evidence whether a candidate is admitted, held or refused. If the required evidence is missing, leave the state unresolved rather than fill the gap with a claim.

The point is not to make the inventory grow. It is to leave a record that can survive someone opening the files and checking it.
