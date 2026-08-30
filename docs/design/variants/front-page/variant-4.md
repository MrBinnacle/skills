# `skills`

A small collection of Claude Code skills developed from problems encountered in actual use.

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

These states make different claims.

### Controlled results

Controlled results come from with-versus-without evaluations under the evaluation protocol.

One skill has been screened:

* `git-pull-rebase-trap`
* screened 2026-07-21
* screen result: `CANT_TELL_YET`
* paired verdict: not yet established

Every other card is `UNMEASURED` in the controlled fields.

### Observed in use

Some records document events from actual sessions.

Observed-in-use records do not populate the controlled fields.

## Card evidence

This table projects each card's own `EVIDENCE.md`. `measured` means a controlled field records a
result other than `UNMEASURED`. `origin-trace` means the controlled fields are unmeasured and the
origin starts with `OBSERVED`. `unmeasured` means neither condition holds.

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

## Admission method

The [admission policy](ADMISSION.md) governs membership. It asks four questions: whether an
unaided failure exists, whether it recurs independently, whether a skill is the correct control
surface, and whether the evidence supports admission and retirement. The default answer is not
admitted.

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
