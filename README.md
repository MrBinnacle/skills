<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills — These aren't the Claude Code skills you're looking for." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# `skills`

**These aren't the Claude Code skills you're looking for.**

A small collection of Claude Code skills I develop from problems encountered in actual use.

The collection is intentionally small. These are the skills I have found useful enough to keep developing and maintaining.

**Install it** with `/plugin marketplace add MrBinnacle/skills` in Claude Code, or
`npx skills add MrBinnacle/skills` at a shell. Both routes, and what each one puts where, are in
[Install](#install) below.

## Admission method

The [admission policy](ADMISSION.md) governs membership. It asks four questions: whether an
unaided failure exists, whether it recurs independently, whether a skill is the correct control
surface, and whether the evidence supports admission and retirement. The default answer is not
admitted.

The policy's [three-instrument table](ADMISSION.md#naming-the-gate) names the parts. The
**admission policy** states the rule. The **gate card** applies the rule. The **screen** measures
a model with and without the candidate. These names describe different instruments.

The [S295 disposition record](dispositions/2026-08-15-S295-admission-triage.md) applied
`admission-policy v1` to all nine published cards on 2026-08-15. It found two cards that stand,
six with thin recurrence records, and one with a ceiling-likely screen result. It retired no
card.

## Card map

These cards use four forms:

| Type | What it is | Cards |
|---|---|---|
| Trap | A warning and recovery path for a command or platform behavior that can report success after doing the wrong work. | `git-pull-rebase-trap`, `github-pages-deploy-verification`, `click-clirunner-env-none-deletes`, `mock-masked-stub-trap`, `pretooluse-bash-guard-prose-false-positive`, `success-test-accepts-any-output` |
| Procedure | An ordered set of actions for a boundary, handoff, or verification task. | `im-down`, `im-up`, `closure-mode-at-boundaries`, `subagent-research-reliability`, `downstream-instruction-framing`, `router-skill-predicate-gap`, `halt-as-deliverable` |
| Gate | A decision sequence that accepts, routes, or rejects a candidate. | `skill-necessity-gate` |
| Schema | A fixed output shape for comparable parallel reviews. | `parallel-review-disposition-schema` |

## Card evidence

This table projects each card's own `EVIDENCE.md`. `measured` means a controlled field records a
result other than `UNMEASURED`. `origin-trace` means the controlled fields are unmeasured and the
origin starts with `OBSERVED`. `unmeasured` means neither condition holds. The final column is the
integer that opens the card's `Occasions counted` row.

| Card | Evidence posture | Occasions counted |
|---|---|---:|
| [`click-clirunner-env-none-deletes`](skills/engineering/click-clirunner-env-none-deletes/EVIDENCE.md) | origin-trace | 1 |
| [`closure-mode-at-boundaries`](skills/engineering/closure-mode-at-boundaries/EVIDENCE.md) | origin-trace | 1 |
| [`git-pull-rebase-trap`](skills/engineering/git-pull-rebase-trap/EVIDENCE.md) | measured | 1 |
| [`github-pages-deploy-verification`](skills/engineering/github-pages-deploy-verification/EVIDENCE.md) | origin-trace | 1 |
| [`halt-as-deliverable`](skills/engineering/halt-as-deliverable/EVIDENCE.md) | origin-trace | 3 |
| [`im-down`](skills/engineering/im-down/EVIDENCE.md) | unmeasured | 2 |
| [`im-up`](skills/engineering/im-up/EVIDENCE.md) | unmeasured | 1 |
| [`mock-masked-stub-trap`](skills/engineering/mock-masked-stub-trap/EVIDENCE.md) | origin-trace | 1 |
| [`pretooluse-bash-guard-prose-false-positive`](skills/engineering/pretooluse-bash-guard-prose-false-positive/EVIDENCE.md) | origin-trace | 5 |
| [`success-test-accepts-any-output`](skills/engineering/success-test-accepts-any-output/EVIDENCE.md) | origin-trace | 2 |
| [`downstream-instruction-framing`](skills/orchestration/downstream-instruction-framing/EVIDENCE.md) | origin-trace | 1 |
| [`parallel-review-disposition-schema`](skills/orchestration/parallel-review-disposition-schema/EVIDENCE.md) | origin-trace | 2 |
| [`subagent-research-reliability`](skills/orchestration/subagent-research-reliability/EVIDENCE.md) | origin-trace | 5 |
| [`router-skill-predicate-gap`](skills/meta/router-skill-predicate-gap/EVIDENCE.md) | origin-trace | 2 |
| [`skill-necessity-gate`](skills/meta/skill-necessity-gate/EVIDENCE.md) | unmeasured | 0 |

## Install

Two routes. Both copy skill files onto your machine. Neither installs a framework — see
[Not a runtime](#not-a-runtime).

**Claude Code plugin marketplace.** The collection ships
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json), which groups the cards into
one plugin per bucket:

```text
/plugin marketplace add MrBinnacle/skills
/plugin install mrbinnacle-engineering
```

The other two plugins are `mrbinnacle-orchestration` and `mrbinnacle-meta`. Install only the
buckets you want. An installed card's `description` is loaded at startup whether or not the card
ever fires, so breadth you do not use is still paid for.

**Installer.** `npx skills add` copies cards into `.claude/skills/` under the directory you run it
in, or into your home directory with `--global`:

```text
npx skills add MrBinnacle/skills
```

It tracks `main` rather than a tag, so it installs the current tip of the collection.

The manifest is the machine-readable statement of what ships. CI refuses any state where the
manifest and the published tree disagree, in either direction — a path the manifest names with no
card at it, and a published card no plugin names. That is standing obligation **O7** in
[`SECURITY.md`](SECURITY.md).

**What a version promises.** The install path and the card format — not the card set. Admitting
or retiring a card is a minor change, so the cards you can install are expected to change under
a minor release; moving the install path or changing the format of a card would be a major one.
That narrowing is deliberate, and [ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md)
records why.

## Where these came from

Every card here is here because I had a reason to make it.

Most originated in something that went wrong, or nearly did. I recorded the failure pattern and developed a reusable intervention. Their records say `OBSERVED`, with dates.

Some were designed for recurring work that I wanted to handle differently. Their records say `DESIGNED`.

One, `skill-necessity-gate`, was distilled from research on when a skill should exist. Its record says `DISTILLED`.

These are **provenance categories, not quality scores**.

* **OBSERVED** — originated in an observed failure or near-failure.
* **DESIGNED** — created intentionally for a recurring need.
* **DISTILLED** — derived from research rather than an incident.

Each card states its own tier in its `EVIDENCE.md`, and that record is the only place the tier is asserted. This page states no tally of them, deliberately: a number here would have to be re-checked every time a card enters or leaves, and that is a maintenance tax with no reader on the other end. `scripts/validate_scoreboard.py` still derives the tiers from the records and checks any tally the page does state, so a figure here can be wrong but cannot be wrong quietly.

## What they address

The cards currently fall into four areas.

### Success that looks successful

Operations that report success even though the intended result did not occur.

* `git-pull-rebase-trap`
* `github-pages-deploy-verification`
* `im-up`

### Delegation

Failure modes introduced when work moves between agents: unsupported research claims, incompatible review outputs, and handoffs that discourage appropriate re-examination.

* `subagent-research-reliability`
* `parallel-review-disposition-schema`
* `downstream-instruction-framing`

### Boundaries

Checks and cleanup that get skipped when one phase or session ends and another begins.

* `closure-mode-at-boundaries`
* `im-down`

### Unnecessary skills

A skill has a context and maintenance cost. Models and platforms change. A skill that no longer provides enough value should be removable.

* `skill-necessity-gate`

## Evidence

Each skill has an `EVIDENCE.md` recording its provenance, validation status, and measured results.

`UNMEASURED` is a valid state. It means no qualifying measurement exists yet.

The repository separates **where a skill came from** from **what evidence exists for it**.

### Provenance

| State       | Meaning                                            |
| ----------- | -------------------------------------------------- |
| `OBSERVED`  | Originated in an observed failure or near-failure. |
| `DESIGNED`  | Created intentionally for a recurring need.        |
| `DISTILLED` | Derived from research.                             |

### Evidence

| State             | Meaning                                              |
| ----------------- | ---------------------------------------------------- |
| `CONTROLLED`      | A defined with/without evaluation produced a result. |
| `OBSERVED IN USE` | A documented event occurred during actual use.       |
| `UNMEASURED`      | No qualifying measurement exists yet.                |

These states make different claims. They are not interchangeable.

### Controlled results

Controlled results come from with-versus-without evaluations under the evaluation protocol.

One skill has been screened:

* `git-pull-rebase-trap`
* screened 2026-07-21
* screen result: `CANT_TELL_YET`
* paired verdict: not yet established

Every other card is `UNMEASURED` in the controlled fields.

`scripts/validate_scoreboard.py` checks that the summary agrees with the individual records.

### Observed in use

Some records document events from my own sessions.

Those observations come from private work logs mined by my own AI assistant and re-checked by a second instance of the same system. This can catch extraction errors. It does not provide independent verification or prevent self-selection.

Each accepted event traces to a dated artifact, records the model identifier where available, and distinguishes observation from measurement.

Observed-in-use records do not populate the controlled fields.

## How a skill leaves

Models improve. Claude Code changes. Failure modes disappear. A skill can stop providing enough value to justify its context and maintenance cost.

When a major model or platform change warrants it, a skill can be re-screened with [`skill-harness`](https://github.com/MrBinnacle/skill-harness): the same task is run with and without the skill, and the result is reported only to the extent the evidence supports one.

Some skills also have a pre-registered retirement trigger. The trigger names a specific change that would remove the underlying failure mode. When that change occurs, the skill can retire against its own criterion.

A skill has already retired this way.

Retirement does not erase the record. [`RETIRED.md`](RETIRED.md) preserves the admissions and departures.

## What this isn't

### Not a catalog

This is a short list, and it is meant to stay one.

The repository is not intended to maximize coverage. If you want breadth, [Matt Pocock's skills collection](https://github.com/mattpocock/skills) is a better place to browse.

### Not proof that these skills work

Publication is not validation.

One card has a controlled screen and its result is `CANT_TELL_YET`. The rest have no controlled result.

The records distinguish what is known from what has not been measured.

### Not a runtime

There is nothing to import and no framework to install.

The skills are Markdown. You can read one, use it, modify it, or delete it.

## The evaluation work

I am also building [`skill-harness`](https://github.com/MrBinnacle/skill-harness) to investigate what Claude Code skills actually change.

It runs with/without comparisons and records insufficient evidence instead of producing a result that the evidence does not support.

The two repositories were developed concurrently. The relationship between the skills and the evaluation system is still being investigated.

The skills are the things being evaluated.

The harness is the thing being used to evaluate them.

Whether the harness provides valid evidence about skill efficacy is itself an open question.

## Why a skill score is not necessarily a skill effect

A successful task does not establish that a skill caused the success.

A difference between two runs does not establish why the runs differed.

A repeatable measurement does not establish that the measurement is valid.

A score can therefore be useful as a measurement without being evidence of the claim someone wants to make from it.

[The write-up](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md) covers the problem in more detail.

## Repository layout

```text
skills/
  engineering/     workflow disciplines for shipping software
  orchestration/   disciplines for multi-agent work
  meta/            skills about the skill system itself

templates/         global operating-rules template

CLAUDE.md          rules for working in this repository
AGENTS.md          conventions for agents working here
```

Each skill directory contains:

```text
SKILL.md            entry point
gotchas.md          append-only record of observed failure modes
EVIDENCE.md         provenance and evaluation record
```

### Operating rules

`templates/BASE-OPERATING-RULES.md` contains the project-agnostic operating rules I use across repositories: anti-anchoring, decision escalation, layer placement, verification, and context hygiene.

Copy it to:

```text
~/.claude/CLAUDE.md
```

to use those rules globally.

It lives under `templates/` rather than at the repository root because a root-level `CLAUDE.md` is automatically loaded as instructions for the repository that contains it. The template is intended to be copied, not loaded here as this repository's operating rules.

`CLAUDE.md` contains the rules for working on this repository itself.
