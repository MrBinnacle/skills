# `skills`

**These aren't the Claude Code skills you're looking for.**

Skills that started with problems I encountered.

A small collection of Claude Code skills I develop from problems encountered in actual use.

The collection is intentionally small. These are the skills I have found useful enough to keep developing and maintaining.

## Admission method

The [admission policy](ADMISSION.md) governs membership. It asks four questions: whether an
unaided failure exists, whether it recurs independently, whether a skill is the correct control
surface, and whether the evidence supports admission and retirement. The default answer is not
admitted.

The policy's [three-instrument table](ADMISSION.md#naming-the-gate) names the parts. The
**admission policy** states the rule. The **gate card** applies the rule. The **screen** measures
a model with and without the candidate. These names describe different instruments.

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

Two routes. Both copy skill files onto your machine. Neither installs a framework.

**Claude Code plugin marketplace.** The collection ships
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json), which groups the cards into
one plugin per bucket:

```text
/plugin marketplace add MrBinnacle/skills
/plugin install mrbinnacle-engineering
```

**Installer.** `npx skills add` copies cards into `.claude/skills/` under the directory you run it
in, or into your home directory with `--global`:

```text
npx skills add MrBinnacle/skills
```

## What this isn't

### Not a catalog

The repository is not intended to maximize coverage. If you want breadth, [Matt Pocock's skills collection](https://github.com/mattpocock/skills) is a better place to browse.

### Not proof that these skills work

One card has a controlled screen and its result is `CANT_TELL_YET`. The rest have no controlled result.

The records distinguish what is known from what has not been measured.

### Not a runtime

There is nothing to import and no framework to install.

The skills are Markdown. You can read one, use it, modify it, or delete it.
