# skills

**A small collection of agent skills that have to earn their keep — with the receipts to prove it.**

```bash
npx skills add MrBinnacle/skills
```

That's the whole install — works with Claude Code and [70+ other agents](https://github.com/vercel-labs/skills).
You'll be shown the seven skills and can pick which to take. Prefer to copy files by hand? See
[Install](#install) below.

## What this is

AI coding assistants like Claude Code can be given **skills** — small instruction files that
teach the assistant how to handle a specific situation. Think of a skill as a recipe card
pinned above the stove: when that situation comes up, the assistant reads the card and follows
it instead of improvising.

This repo is a collection of those cards. Each one exists because an AI assistant actually got
something wrong — or nearly did — and the card stops it happening again. Example: git has a
setting that can silently rewrite your commit history during an ordinary `git pull`. An
assistant hit it, 22 commits got rewritten, and now there's a card that checks for that setting
first.

**What makes this collection different: every card has to earn its keep.** Most skill
collections only ever grow. This one also shrinks. Each card carries a plain record of the real
incident behind it (`EVIDENCE.md`), and when new AI models get smart enough to no longer need a
card, we test for that and retire it — publicly. A skill you install from here is one that
still does something.

It is also **small on purpose**. Seven skills, not seven hundred. Adding a skill costs you
context space in every conversation, so each one here had to clear a bar most ideas fail.

## Install

One command, works with Claude Code and [70+ other agents](https://github.com/vercel-labs/skills):

```bash
npx skills add MrBinnacle/skills
```

You'll be shown the seven skills and can pick which to install. Prefer to do it by hand? Each
skill is just a folder — copy it into your skills directory:

```bash
git clone https://github.com/MrBinnacle/skills.git /tmp/mr-skills
cp -r /tmp/mr-skills/skills/engineering/git-pull-rebase-trap ~/.claude/skills/
```

## The skills

### [git-pull-rebase-trap](skills/engineering/git-pull-rebase-trap/SKILL.md)

If git is configured with `pull.rebase=true`, then `git pull --no-ff` **silently ignores your
flag** and rebases anyway — every local commit gets rewritten with a new ID. This skill makes
the assistant check that setting before pulling, and shows the safe alternative. Born from a
real incident that rewrote 22 commits. [The receipt →](skills/engineering/git-pull-rebase-trap/EVIDENCE.md)

### [parallel-review-disposition-schema](skills/orchestration/parallel-review-disposition-schema/SKILL.md)

When you send several AI reviewers to judge the same list of findings, their verdicts usually
come back in incompatible formats that can't be combined — five strong reviews that don't add
up to one decision. This skill makes every reviewer answer in the same fixed format, so the
results actually merge. Used in production twice before it was published.
[The receipt →](skills/orchestration/parallel-review-disposition-schema/EVIDENCE.md)

### [skill-necessity-gate](skills/meta/skill-necessity-gate/SKILL.md)

Most ideas for new skills should not become skills. This is a six-question checklist that tells
you whether a capability belongs in a skill, in your project rules, in a hook — or nowhere.
It's the gate this very collection uses to stay small. Grounded in
[Matt Pocock's methodology](https://github.com/mattpocock/skills) and Anthropic's official
skill-authoring guidance.

### [closure-mode-at-boundaries](skills/engineering/closure-mode-at-boundaries/SKILL.md)

The moment one phase of work finishes is exactly when an assistant is most tempted to charge
into the next thing. This skill forces a structured wrap-up first — checks actually run, loose
ends actually verified — before any "what's next" decision is made.

### [subagent-research-reliability](skills/orchestration/subagent-research-reliability/SKILL.md)

When an assistant sends out helper agents to do web research, two things go silently wrong: the
helper may not actually have search tools (so it makes up citations from memory), and even a
real search can return fabricated references. This skill adds a check before dispatch and a
verification pass after — both failure modes were caught in one real session.
[The receipt →](skills/orchestration/subagent-research-reliability/EVIDENCE.md)

### [downstream-instruction-framing](skills/orchestration/downstream-instruction-framing/SKILL.md)

When one AI session writes instructions for the next one, it tends to write orders — "do not
question these decisions" — to a reader who can see the actual code and knows better. This skill
flips the framing: prior decisions arrive as proposals with explicit conditions for revisiting
them, so the better-informed reader keeps their judgment.
[The receipt →](skills/orchestration/downstream-instruction-framing/EVIDENCE.md)

### [github-pages-deploy-verification](skills/engineering/github-pages-deploy-verification/SKILL.md)

"The deploy went green" is not the same as "the site actually changed." This skill makes the
assistant verify a static-site deploy by polling for content that genuinely didn't exist before
the push — the origin incident's verification loop passed instantly on *old* content and called
it done. Rare bonus: the origin incident is on a public repo, so
[the receipt →](skills/engineering/github-pages-deploy-verification/EVIDENCE.md) is
independently checkable.

## Is it safe to install these?

The right first question for anything you hand to an AI agent. Plainly:

- A skill is a **plain-text markdown file**. There is nothing to execute at install time — no
  binaries, no scripts that run on your machine, no network calls, nothing to phone home.
- But a skill **instructs your assistant**, and your assistant can run commands. So treat a
  skill like a pull request: read it before you adopt it. Every skill here is a few KB of
  English — a couple of minutes to read end to end.
- Installing via `npx skills add` copies the files locally; nothing updates behind your back.
  Updating is explicit, and you can diff what changed.

See [SECURITY.md](SECURITY.md) for the full policy and how to report a concern.

## The receipts, explained

*Confidence is not evidence* — including ours. So skills here carry an
[`EVIDENCE.md`](skills/engineering/git-pull-rebase-trap/EVIDENCE.md): a dated record of the
real failure that justified the skill, what it has been validated against, and its measured
result — including **UNMEASURED** stated plainly when something can't be measured yet, rather
than a made-up score.

The part most collections lack: **models improve, and a skill only matters against models that
still need it.** When a major model release lands, skills get re-screened with
[skill-harness](https://github.com/MrBinnacle/skill-harness) — a tool that runs the same task
with and without the skill and honestly reports the difference. A skill the new model no longer
needs gets retired in public, evidence record intact — see the [retirement log](RETIRED.md).
Model progress becomes collection history, not silent rot.

That mechanism has already fired once: in July 2026, four of the author's own candidate
skills were tested at the admission gate and **the model passed every run without them** —
so none got in. [The full record, receipts included →](RETIRED.md)

Five of the seven skills carry full evidence records today; the rest of the collection is being
brought under the same standard. The methodology — and why most "this skill scored 1.0!" benchmarks mislead —
lives in the harness repo:
[why naive skill benchmarks mislead](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md) ·
[the double-ceiling case study](https://github.com/MrBinnacle/skill-harness/blob/main/docs/case-studies/double-ceiling-structurally-unmeasured.md).

## Repository layout

```
skills/
  engineering/     workflow disciplines for shipping software
  orchestration/   disciplines for multi-agent work
  meta/            skills about the skill system itself
  in-progress/     unshipped; not listed above
```

Each skill folder contains `SKILL.md` (the entry point), usually `gotchas.md` (an append-only
log of observed failure modes — the skill's memory), and `EVIDENCE.md` where earned.

## Contributing

Issues and PRs welcome. New skills run the same gauntlet as ours:

1. It must pass the [skill-necessity-gate](skills/meta/skill-necessity-gate/SKILL.md) — most
   ideas correctly fail it.
2. It ships with a `gotchas.md` and, for anything claiming a real-incident origin, an
   `EVIDENCE.md` with the dated story.
3. Frontmatter is minimal (`name:` + `description:`, description ≤ 200 chars, quoted if it
   contains `: `), `SKILL.md` stays lean, and aux detail goes in sibling files.

Authored by [Matthew Gruber](https://github.com/MrBinnacle). Layout inspired by
[mattpocock/skills](https://github.com/mattpocock/skills).

## License

MIT — see [LICENSE](LICENSE).
