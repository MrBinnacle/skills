<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. 14 skill cards. Each states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# `skills`

A skill card is a Markdown file that Claude Code loads as instructions. This repository publishes
14 of them, grouped into `engineering`, `orchestration`, and `meta`.

An installed card's `description` is read at startup whether or not the card ever fires, so
breadth you never use is still paid for on every turn. Both install routes copy files onto your
machine and start nothing: there is no build step, no package to import, and no service to run.
Most of what lands is Markdown. Every card also ships an `evals/evals.json`, and two cards,
`im-down` and `im-up`, ship the Python scripts their own procedures call. Those scripts run only
when you run them.

No card here has evidence that it helps. One card carries a controlled result, and that result is
`CANT_TELL_YET`. Eleven carry a dated record of the failure that produced them and no screen. Two
carry neither. Those three counts come from the cards' own `EVIDENCE.md` records, and the
[card evidence](#card-evidence) table below is rebuilt from those records by CI. What all 14 do
carry is a pre-registered retirement trigger: the specific change that would remove the failure
each card addresses, named in advance. Membership is governed by the
[admission policy](ADMISSION.md).

## Install

**Claude Code plugin marketplace.** The collection ships
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json), which groups the cards into
one plugin per bucket:

```text
/plugin marketplace add MrBinnacle/skills
/plugin install mrbinnacle-engineering
```

The other two plugins are `mrbinnacle-orchestration` and `mrbinnacle-meta`. Install only the
buckets you want.

**Installer.** `npx skills add` writes three things under the directory you run it in: a copy of
every card in `.claude/skills/`, a second copy in `.agents/skills/`, and a `skills-lock.json`
recording each card's source path and a hash. `--global` writes to your home directory instead.

```text
npx skills add MrBinnacle/skills
```

The two card directories are the installer's own convention for agent tools that read one path or
the other. This collection does not choose them and does not configure them.

It tracks `main` rather than a tag, so it installs the current tip of the collection.

The same route lists the collection on [skills.sh](https://www.skills.sh/MrBinnacle/skills), the
directory behind that command, where each card appears by name with its install count. That
directory ranks by installs only. It carries none of the evidence records described below.

The manifest is the machine-readable statement of what ships. CI rejects any state where the
manifest and the published tree disagree, in either direction: a path the manifest names with no
card at it, and a published card no plugin names. That is standing obligation **O7** in
[`SECURITY.md`](SECURITY.md).

**What a version promises.** The install path and the card format, not the card set. Admitting or retiring a card is a minor change, so the cards you can install are expected to change under a minor release; moving the install path or changing the format of a card would be a major one. That narrowing is deliberate, and [ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md) records why.

## Admission method

The [admission policy](ADMISSION.md) governs membership. It asks four questions: whether an
unaided failure exists, whether it recurs independently, whether a skill is the correct control
surface, and whether the evidence supports admission and retirement. A card is admitted only if
all four answers are yes. An unanswered question counts as no.

The policy's [naming table](ADMISSION.md#naming-the-gate) separates two live instruments. The
**admission policy** states the rule. The **screen** runs a model on the same task with the
candidate and without it. Screening happens in a separate repository,
[`skill-harness`](https://github.com/MrBinnacle/skill-harness), which reports what the evidence
supports about the difference and most often reports that it supports nothing. A third name was
retired on 2026-08-31 along with the card it named, so the four questions are now answered
directly rather than through a reference method.

Two limits belong beside any result that comes back. A task the model passes with the card
attached leaves open whether the card caused the pass; only the paired no-card arm can separate
those. A difference between two runs leaves open why the runs differed; run-to-run variation on
identical tasks is large enough to produce one on its own.
[Why naive skill benchmarks mislead](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md)
carries the measurement behind that second sentence.

The [nine-card admission triage record](dispositions/2026-08-15-S295-admission-triage.md) applied
`admission-policy v1` to the nine cards published on 2026-08-15, and retired none of them.

## Card map

These cards use three forms:

| Type | What it is | Cards |
|---|---|---|
| Trap | A warning and recovery path for a command or platform behavior that can report success after doing the wrong work. | `git-pull-rebase-trap`, `github-pages-deploy-verification`, `click-clirunner-env-none-deletes`, `mock-masked-stub-trap`, `pretooluse-bash-guard-prose-false-positive`, `success-test-accepts-any-output` |
| Procedure | An ordered set of actions for a boundary, handoff, or verification task. | `im-down`, `im-up`, `closure-mode-at-boundaries`, `subagent-research-reliability`, `downstream-instruction-framing`, `router-skill-predicate-gap`, `halt-as-deliverable` |
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

CI rebuilds this table from the records and fails on any disagreement, so the records are the
place to change a row.

## What the cards cover

Every published card appears once below. The [Card map](#card-map) above groups the same 14 by
form.

Nine are about an operation, a test, or an agent reporting an outcome that did not happen:

| Card | What goes wrong |
|---|---|
| `git-pull-rebase-trap` | A pull rewrites local commits and reports an ordinary merge. |
| `github-pages-deploy-verification` | A poll matches content already on the page, so the check confirms a deploy that has not landed. |
| `mock-masked-stub-trap` | A test patches a helper that is a stub in production, so the suite passes over a branch that never ran. |
| `success-test-accepts-any-output` | A success test accepts an error body, because it asks only whether the output is non-empty. |
| `click-clirunner-env-none-deletes` | A test's environment override leaves a key in place, the call the test exists to prevent happens, and the assertion still passes. |
| `router-skill-predicate-gap` | A router's silence reads as "no prompt needed it" when the cause is a predicate that cannot match. |
| `pretooluse-bash-guard-prose-false-positive` | A command guard reads prose that mentions the command it polices, and blocks the text instead of the action. |
| `subagent-research-reliability` | A subagent returns claims and citations nobody checked, from tools it may not hold. |
| `im-up` | A session start checks the previous session's stated paths, predicates, and sequence against the repository. |

Five are about what one session, agent, or reviewer writes down for the next:

| Card | What it does |
|---|---|
| `im-down` | Writes the session's closing state as a packet the receiver can validate. |
| `closure-mode-at-boundaries` | Runs the verification list at a boundary instead of handing it back as options. |
| `downstream-instruction-framing` | Separates what the reader may re-examine from what the handoff has settled. |
| `parallel-review-disposition-schema` | Fixes the output shape so parallel reviews can be compared. |
| `halt-as-deliverable` | Records a halt by your own gate as the result, rather than routing around it. |

## Evidence records

Each card has an `EVIDENCE.md`. It records where the card came from and what has been measured
about it, on two separate axes. A card holds one state from each.

Where the card came from:

| State | Meaning |
|---|---|
| `OBSERVED` | Originated in an observed failure or near-failure. |
| `DESIGNED` | Created intentionally for a recurring need. |
| `DISTILLED` | Derived from research. |

What has been measured:

| State | Meaning |
|---|---|
| `CONTROLLED` | A defined with-and-without evaluation produced a result. |
| `OBSERVED IN USE` | A documented event occurred during actual use. |
| `UNMEASURED` | No qualifying measurement exists yet. |

Each card states its own state in its own record, and that record is the only place the state is
asserted. This page states no tally of the provenance states, deliberately: a number here would
need re-checking every time a card enters or leaves.
`scripts/validate_scoreboard.py` derives the states from the records and checks any tally the page
does state.

### Controlled results

A controlled result comes from a with-and-without evaluation run under the evaluation protocol.
One card carries one:
[`git-pull-rebase-trap`](skills/engineering/git-pull-rebase-trap/EVIDENCE.md). Its verdict, dates,
and receipts live in that record and nowhere else, so the page points at the record instead of
copying it. Every other card is `UNMEASURED` in the controlled fields.

### Observed in use

`OBSERVED IN USE` records come from the owner's private work logs, mined by his own AI assistant
and re-checked by a second instance of the same system. That re-check catches extraction errors.
It supplies neither independent verification nor protection against self-selection, and what it
does supply is traceability: each accepted event points at a dated artifact, records the model
identifier where available, and marks itself as an observation rather than a measurement. An
`OBSERVED IN USE` record never populates the controlled fields.

## How a card leaves

Models improve, Claude Code changes, and a failure mode can stop occurring. A card that no longer
addresses a live failure still costs context, so the collection removes it.

Two routes lead out, and both are recorded in [`RETIRED.md`](RETIRED.md) with the evidence intact.

A card can be re-screened with
[`skill-harness`](https://github.com/MrBinnacle/skill-harness) when a major model or platform
change warrants it. The same task runs with the card and without it, and the result is reported
only as far as the evidence carries it.

A card can also retire against the trigger it registered in advance. All 14 published cards carry
one. The trigger names the specific platform or model change that would make the underlying
failure impossible, written down before the change happens so the call cannot be reasoned
backwards from the outcome. Two cards have already left: one retired against its own trigger when
Claude Code shipped the change it named, and one was withdrawn on the policy, because its own
record could not satisfy the criterion the policy requires.

The admission policy caps what enters and the retirement routes take cards back out, so the
collection stays small and covers little ground. For breadth,
[Matt Pocock's skills collection](https://github.com/mattpocock/skills) is the larger one.

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

Every card directory contains these four:

```text
SKILL.md            entry point
gotchas.md          append-only record of observed failure modes
EVIDENCE.md         provenance and evaluation record
evals/evals.json    the card's evaluation cases
```

Cards may carry more. A card that needs supporting prose adds it as a further Markdown file, and
`im-down` and `im-up` each ship the Python scripts and fixtures their procedures call.

`templates/BASE-OPERATING-RULES.md` holds the project-agnostic operating rules the owner uses
across repositories: anti-anchoring, decision escalation, layer placement, verification, and
context hygiene. Copy it to:

```text
~/.claude/CLAUDE.md
```

to use those rules globally. It sits under `templates/` rather than at the repository root because
a root-level `CLAUDE.md` is loaded automatically as instructions for the repository that contains
it, and this template is meant to be copied elsewhere. `CLAUDE.md` at the root holds the rules for
working on this repository.
