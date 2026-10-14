<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# `MRBINNACLE / skills`

A small collection of Claude Code skills I develop from problems encountered in actual use.

Most address a failure seen in real work: a pull that rewrites commits, a test that passes over code that never ran, a deploy check that confirms a deploy that has not landed, or a handoff that returns claims nobody checked. Any Claude Code user can hit these failures. `im-down` and `im-up` were designed for recurring work rather than written after an incident.

Each published card has an instruction, test cases, an evidence record and a stated condition that would retire it. Read those together. A plausible instruction is not evidence that it changes behavior. A run that never reaches the failure a card targets cannot establish that the card prevents it.

**A kept card is an inventory fact, not evidence that it works.**

The [admission policy](ADMISSION.md) governs additions. It asks whether the unaided failure exists, recurs independently, calls for a skill rather than another control, and has evidence adequate for admission and later retirement. An unanswered criterion counts as no.

## Install

Run these two commands one at a time. A paste of both in one block is read by Claude Code as a single malformed URL.

```text
/plugin marketplace add https://github.com/MrBinnacle/skills.git
```

```text
/plugin install mrbinnacle-engineering
```

The other plugins are `mrbinnacle-orchestration` and `mrbinnacle-meta`. Or install everything with `npx skills add MrBinnacle/skills`.

The cards appear after `/reload-plugins`. If Claude Code reports the reload as pending, run `/reload-plugins --force`. A new `claude` session in the same profile also loads them. The plugin docs at https://code.claude.com/docs/en/discover-plugins.md state this behaviour (read 2026-10-06).

Confirm what you installed with `claude plugin list`. It reports the installed plugins and their versions.

Shell form, same source:

```bash
claude plugin marketplace add https://github.com/MrBinnacle/skills.git
claude plugin install mrbinnacle-engineering
```

The HTTPS clone URL is what this README publishes. The GitHub shorthand `MrBinnacle/skills` is also a documented CLI source; on a machine with no working SSH key for github.com it can fail with `git@github.com: Permission denied (publickey)`, which is what a cold install of v3.0.1 recorded. Issue #333 recorded that failure.

Verified forms, Claude Code 2.1.287, 2026-10-02, from a clean `CLAUDE_CONFIG_DIR` with no SSH key:

- interactive `/plugin marketplace add https://github.com/MrBinnacle/skills.git`
- shell `claude plugin marketplace add https://github.com/MrBinnacle/skills.git`
- shell `claude plugin install` of all three plugins, at 3.0.1

The cold-install transcript is in the pull request that changed this section (#340).

## What ships now

| Group | What it covers | Index |
|---|---|---|
| Engineering | Git, tests, deployment checks, command guards and other places where a success signal can be wrong | [Engineering skills](skills/engineering/README.md) |
| Orchestration | Handoffs, delegated work and decisions that need a checkable return | [Orchestration skills](skills/orchestration/README.md) |
| Meta | Routing and dispatch failures inside the skill system | [Meta skills](skills/meta/README.md) |

The collection is not intended to cover every possible task. A skill is the wrong answer when the failure does not recur, the model already handles it, or a different control is the right place to act. The rule is admission, not coverage.

## Read the record

A skill's `SKILL.md` is the instruction an agent receives. Its `evals/evals.json` holds test cases. Its `EVIDENCE.md` records the origin and the evidence available for that card.

- [Catalog and evidence map](CATALOG.md) links published cards to their recorded states.
- [Admission policy](ADMISSION.md) sets the criteria for adding a card.
- [Retired cards](RETIRED.md) records what left and why.
- [Quarantine](./_quarantine/README.md) explains the status of candidates that have not been admitted.
- [Security commitments](SECURITY.md) describes the project's security posture.
- [`skill-harness`](https://github.com/MrBinnacle/skill-harness) holds the evaluation apparatus, not this repository.

Three distinctions matter when reading the evidence:

- **Origin is not effect.** A card's source record says where it came from. It does not say whether it helps.
- **A passing task is not automatically a skill effect.** The comparison must establish what changed between a run with the card and a run without it.
- **A missing or inconclusive result is not a pass.** `UNMEASURED` and `CANT_TELL_YET` are valid states. Their explanations belong beside the relevant card, not in a universal badge.

The [admission triage record](dispositions/2026-08-15-S295-admission-triage.md) also documents where earlier cards do not yet meet every admission criterion on recorded evidence. That is a limitation in the record, not a reason to infer a positive result.

## The wider system under review

The proposed direction is to make this repository the published intervention catalog and operator-facing adoption layer for a larger agent-reliability system. That system is not delivered end to end today. The proposal separates responsibilities instead of copying everything into this repository.

| Surface | Intended responsibility | Boundary that remains important |
|---|---|---|
| GitHub | Canonical bytes and revisions for published capabilities | A knowledge-base description does not override the current file |
| Notion | Shared context, source relationships, hypotheses and accepted decisions | Context is not evidence that a runtime received a capability or that it worked |
| Pi | First implementation of an owner-controlled agent layer, with model and provider kept replaceable | The exact `skills-pi` distribution path is not yet verified |
| Claude Code | Current distribution and compatibility route | Shared `SKILL.md` format does not establish equivalent discovery, loading, invocation or behavior |
| `skill-harness` | Controlled evaluation, measurement and evidence receipts | The Pi evaluation adapter is not the same thing as a `skills-pi` installer or package |

The proposed [product contract](docs/product/product-contract.md) defines capability, context, runtime-delivery, evaluation and lifecycle interfaces. The [product thesis](docs/product/agent-reliability-system-thesis.md) describes the intended operator journey. Both remain proposals until reviewed and accepted.

The source checks are tracked in [#420, runtime delivery and artifact identity](https://github.com/MrBinnacle/skills/issues/420) and [#421, the Notion context audit](https://github.com/MrBinnacle/skills/issues/421). They are audits, not claims that the integrations already work. A shared format, installer test or adapter test does not by itself prove a specific capability was delivered, invoked or had an effect.

## Adding a skill

Start with [ADMISSION.md](ADMISSION.md), not a blank card. Record the failure and independently counted occasions. Check that a skill is the right control surface. Preserve the evidence whether a candidate is admitted, held or refused. If evidence is missing, leave the state unresolved instead of filling the gap with a claim.

The point is not to make the inventory grow. It is to leave a record that can survive someone opening the files and checking it.
