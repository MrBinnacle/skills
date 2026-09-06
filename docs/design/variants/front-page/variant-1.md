> **Provenance.** This is an unselected front-page draft from 2026-08-30, recovered from the
> branch `rescue/191-front-page-variants` at commit `c80099c` before that branch was deleted
> (`#201`). It is raw material, not a foundation, and not evidence that any question about the
> front page was already answered — that is the operator's ruling of 2026-08-25, and it governs
> every prior brand and design artifact in this project. This draft settles nothing and selects
> nothing. The front-page direction belongs to `#62`, which runs its own Context → Direction →
> Make → Check pass and is the only place a selection among these drafts gets made.
>
> **This variant.** The baseline draft: no tagline, no admission-instrument paragraph, no
> evidence table — the plainest of the five.

---

# `skills`

Skills that started with problems I encountered.

A small collection of Claude Code skills I develop from problems encountered in actual use.

The collection is intentionally small. These are the skills I have found useful enough to keep developing and maintaining.

## Admission method

The [admission policy](ADMISSION.md) governs membership. It asks four questions: whether an
unaided failure exists, whether it recurs independently, whether a skill is the correct control
surface, and whether the evidence supports admission and retirement. The default answer is not
admitted.

## Card map

These cards use four forms:

| Type | What it is | Cards |
|---|---|---|
| Trap | A warning and recovery path for a command or platform behavior that can report success after doing the wrong work. | `git-pull-rebase-trap`, `github-pages-deploy-verification`, `click-clirunner-env-none-deletes`, `mock-masked-stub-trap`, `pretooluse-bash-guard-prose-false-positive`, `success-test-accepts-any-output` |
| Procedure | An ordered set of actions for a boundary, handoff, or verification task. | `im-down`, `im-up`, `closure-mode-at-boundaries`, `subagent-research-reliability`, `downstream-instruction-framing`, `router-skill-predicate-gap`, `halt-as-deliverable` |
| Gate | A decision sequence that accepts, routes, or rejects a candidate. | `skill-necessity-gate` |
| Schema | A fixed output shape for comparable parallel reviews. | `parallel-review-disposition-schema` |

## Install

Two routes. Both copy skill files onto your machine. Neither installs a framework.

**Claude Code plugin marketplace.** The collection ships
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json), which groups the cards into
one plugin per bucket:

```text
/plugin marketplace add MrBinnacle/skills
/plugin install mrbinnacle-engineering
```

The other two plugins are `mrbinnacle-orchestration` and `mrbinnacle-meta`. Install only the
buckets you want.

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
