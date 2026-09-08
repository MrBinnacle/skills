<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills. Each card states the condition that would retire it." src="assets/banner-light.svg" width="620">
  </picture>
</p>

# `skills`

A skill card is a Markdown file that Claude Code loads as instructions. This repository publishes
cards in three groups: `engineering`, `orchestration`, and `meta`. The
[card evidence](#card-evidence) table below names every published card, and CI rebuilds that table
from the cards themselves, so it is where to read what ships today.

An installed card's `description` is read at startup whether or not the card ever fires, so
breadth you never use is still paid for on every turn. Both install routes copy files onto your
machine and start nothing: there is no build step, no package to import, and no service to run.
Most of what lands is Markdown. Every card also ships an `evals/evals.json`, and the `im-down`
and `im-up` cards ship the Python scripts their own procedures call. Those scripts run only
when you run them.

No card here has evidence that it helps. Where a card carries a controlled result, that result is
`CANT_TELL_YET`. Most carry a dated record of the failure that produced them and no screen, and
some carry neither. Which card is in which state comes from the cards' own `EVIDENCE.md` records,
and the [card evidence](#card-evidence) table marks it card by card rather than tallying it. What
every card does carry is a pre-registered retirement trigger: the specific change that would
remove the failure the card addresses, named in advance. Membership is governed by the
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

Those two directories are the installer's own convention for agent tools that read one path or
the other. This collection does not choose them and does not configure them.

It tracks `main` rather than a tag, so it installs the current tip of the collection.

The same route lists the collection on [skills.sh](https://www.skills.sh/MrBinnacle/skills), the
directory behind that command, where each card appears by name with its install count. That
directory ranks by installs only. It carries none of the evidence records described below.

The manifest is the machine-readable statement of what ships. CI rejects any state where the
manifest and the published tree disagree, in either direction: a path the manifest names with no
card at it, and a published card no plugin names. That is standing obligation **O7** in
[`SECURITY.md`](SECURITY.md).

**What a version promises.** The install path and the card format, not the card set. Admitting or retiring a card is a minor change, so the cards you can install are expected to change under a minor release; moving the install path or changing the format of a card would be a major one. A card's name is covered too, so renaming one is a major change — you resolve a card by its name, and a rename stops your existing reference working. That narrowing is deliberate, and [ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md) records why, with [ADR 0003](docs/adr/0003-a-cards-name-is-part-of-the-declared-surface.md) recording why the name is inside it.

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

The [admission triage record](dispositions/2026-08-15-S295-admission-triage.md) applied
`admission-policy v1` to the cards published on 2026-08-15, and retired none of them.

Candidates that have not cleared the gate sit in [`_quarantine/`](_quarantine/README.md), in the
open. That directory's own README states what being there does and does not claim.

## Card map

These cards use three forms:

| Type | What it is | Cards |
|---|---|---|
| Trap | A warning and recovery path for a command or platform behavior that can report success after doing the wrong work. | `pull-rebase`, `stale-deploy`, `clirunner-env`, `mocked-stub`, `pretooluse-prose`, `vacuous-check` |
| Procedure | An ordered set of actions for a boundary, handoff, or verification task. | `im-down`, `im-up`, `closure-mode`, `subagent-handback`, `decision-rights`, `dead-predicate`, `halt-as-deliverable` |
| Schema | A fixed output shape for comparable parallel reviews. | `disposition-schema` |

## Card evidence

This table projects each card's own `EVIDENCE.md`. `measured` means a controlled field records a
result other than `UNMEASURED`. `origin-trace` means the controlled fields are unmeasured and the
origin starts with `OBSERVED`. `unmeasured` means neither condition holds. The final column is the
integer that opens the card's `Occasions counted` row.

| Card | Evidence posture | Occasions counted |
|---|---|---:|
| [`clirunner-env`](skills/engineering/clirunner-env/EVIDENCE.md) | origin-trace | 1 |
| [`closure-mode`](skills/engineering/closure-mode/EVIDENCE.md) | origin-trace | 1 |
| [`pull-rebase`](skills/engineering/pull-rebase/EVIDENCE.md) | measured | 1 |
| [`stale-deploy`](skills/engineering/stale-deploy/EVIDENCE.md) | origin-trace | 1 |
| [`halt-as-deliverable`](skills/engineering/halt-as-deliverable/EVIDENCE.md) | origin-trace | 3 |
| [`im-down`](skills/engineering/im-down/EVIDENCE.md) | unmeasured | 2 |
| [`im-up`](skills/engineering/im-up/EVIDENCE.md) | unmeasured | 1 |
| [`mocked-stub`](skills/engineering/mocked-stub/EVIDENCE.md) | origin-trace | 1 |
| [`pretooluse-prose`](skills/engineering/pretooluse-prose/EVIDENCE.md) | origin-trace | 7 |
| [`vacuous-check`](skills/engineering/vacuous-check/EVIDENCE.md) | origin-trace | 2 |
| [`decision-rights`](skills/orchestration/decision-rights/EVIDENCE.md) | origin-trace | 1 |
| [`disposition-schema`](skills/orchestration/disposition-schema/EVIDENCE.md) | origin-trace | 2 |
| [`subagent-handback`](skills/orchestration/subagent-handback/EVIDENCE.md) | origin-trace | 5 |
| [`dead-predicate`](skills/meta/dead-predicate/EVIDENCE.md) | origin-trace | 2 |

CI rebuilds this table from the records and fails on any disagreement, so the records are the
place to change a row.

## What the cards cover

Every published card appears once below. The [Card map](#card-map) above groups the same cards by
form.

These are about an operation, a test, or an agent reporting an outcome that did not happen:

| Card | What goes wrong |
|---|---|
| `pull-rebase` | A pull rewrites local commits and reports an ordinary merge. |
| `stale-deploy` | A poll matches content already on the page, so the check confirms a deploy that has not landed. |
| `mocked-stub` | A test patches a helper that is a stub in production, so the suite passes over a branch that never ran. |
| `vacuous-check` | A success test accepts an error body, because it asks only whether the output is non-empty. |
| `clirunner-env` | A test's environment override leaves a key in place, the call the test exists to prevent happens, and the assertion still passes. |
| `dead-predicate` | A router's silence reads as "no prompt needed it" when the cause is a predicate that cannot match. |
| `pretooluse-prose` | A command guard reads prose that mentions the command it polices, and blocks the text instead of the action. |
| `subagent-handback` | A subagent returns claims and citations nobody checked, from tools it may not hold. |
| `im-up` | A session start checks the previous session's stated paths, predicates, and sequence against the repository. |

These are about what one session, agent, or reviewer writes down for the next:

| Card | What it does |
|---|---|
| `im-down` | Writes the session's closing state as a packet the receiver can validate. |
| `closure-mode` | Runs the verification list at a boundary instead of handing it back as options. |
| `decision-rights` | Separates what the reader may re-examine from what the handoff has settled. |
| `disposition-schema` | Fixes the output shape so parallel reviews can be compared. |
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
asserted. This page states no tally of the card set, deliberately: a number written here would
need re-checking every time a card enters or leaves, and a reader who caught one stale number
would be right to distrust every other claim on the page. Numbers belong in the
[card evidence](#card-evidence) table, which CI derives from the records on every run.
`scripts/validate_scoreboard.py` derives the states from the records and checks any tally the page
does state.

### Controlled results

A controlled result comes from a with-and-without evaluation run under the evaluation protocol.
[`pull-rebase`](skills/engineering/pull-rebase/EVIDENCE.md) carries one. Its
verdict, dates, and receipts live in that record and nowhere else, so the page points at the
record instead of copying it. The [card evidence](#card-evidence) table marks every card carrying
a controlled result as `measured`; the rest are `UNMEASURED` in the controlled fields.

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

A card can also retire against the trigger it registered in advance. Every published card carries
one. The trigger names the specific platform or model change that would make the underlying
failure impossible, written down before the change happens so the call cannot be reasoned
backwards from the outcome.

Both routes have already been used. A card retired against its own trigger when Claude Code
shipped the change it named, and a card was withdrawn on the policy because its own record could
not satisfy the criterion the policy requires. [`RETIRED.md`](RETIRED.md) lists every departure
with its evidence.

The admission policy caps what enters and the retirement routes take cards back out, so the
collection stays small and covers little ground. For breadth,
[Matt Pocock's skills collection](https://github.com/mattpocock/skills) is the larger one.

## Repository layout

```text
skills/
  engineering/     workflow disciplines for shipping software
  orchestration/   disciplines for multi-agent work
  meta/            skills about the skill system itself

_quarantine/       candidate cards that have not cleared admission
templates/         global operating-rules template

CLAUDE.md          rules for working in this repository
AGENTS.md          conventions for agents working here
```

Every published card directory contains these four:

```text
SKILL.md            entry point
gotchas.md          append-only record of observed failure modes
EVIDENCE.md         provenance and evaluation record
evals/evals.json    the card's evaluation cases
```

Cards may carry more. A card that needs supporting prose adds it as a further Markdown file, and
`im-down` and `im-up` each ship the Python scripts and fixtures their procedures call.

`_quarantine/` holds candidates, which are not published skills and are not required to carry that
set. [`_quarantine/README.md`](_quarantine/README.md) states what is missing from them and what
admission still requires.

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
