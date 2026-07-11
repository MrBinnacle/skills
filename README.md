# skills

**A small collection of agent skills that have to earn their keep — with the receipts to prove it.**

```bash
npx skills add MrBinnacle/skills
```

That's the whole install — works with Claude Code and [70+ other agents](https://github.com/vercel-labs/skills).
You'll be shown the eight skills and can pick which to take.

## What this is

AI coding assistants like Claude Code can be given **skills** — small instruction files that
teach the assistant how to handle a specific situation. Think of a skill as a recipe card
pinned above the stove: when that situation comes up, the assistant reads the card and follows
it instead of improvising.

This repo is a collection of those cards. Each one exists because an AI assistant actually got
something wrong — or nearly did — and the card stops it happening again.

**What makes this collection different: every card has to earn its keep.** Most skill
collections only ever grow. This one also shrinks. Each card carries a plain record of the real
incident behind it (`EVIDENCE.md`), and when new AI models get smart enough to no longer need a
card, we test for that and retire it — publicly. A skill you install from here is one that
still does something.

It is also **small on purpose**. Eight skills, not eight hundred. Adding a skill costs you
context space in every conversation, so each one here had to clear a bar most ideas fail.

## Quickstart

1. Run the installer and pick your skills:

   ```bash
   npx skills add MrBinnacle/skills
   ```

2. **Read what you installed.** Each skill is a few KB of English — a couple of minutes end to
   end. You're handing instructions to an agent that can run commands; treat a skill like a
   pull request, not a package.

3. That's it. The skills fire when their situation comes up.

Prefer to do it by hand? Each skill is just a folder — copy it into your skills directory:

```bash
git clone https://github.com/MrBinnacle/skills.git /tmp/mr-skills
cp -r /tmp/mr-skills/skills/engineering/git-pull-rebase-trap ~/.claude/skills/
```

## Why these skills exist

> "The first principle is that you must not fool yourself — and you are the easiest person to fool."
>
> Richard Feynman, [Cargo Cult Science](https://calteches.library.caltech.edu/51/2/CargoCult.htm) (1974)

Every skill here answers a failure that actually happened. They cluster into four failure
modes — and where a skill has earned its receipt, the section opens with a line from it.

### #1: Green lights you didn't earn

> "…the rebase silently proceeded, rewriting **22 local commits**…"
>
> — [EVIDENCE.md, git-pull-rebase-trap](skills/engineering/git-pull-rebase-trap/EVIDENCE.md) (2026-05-25)

**The problem.** The most dangerous agent failure is not a crash — it's success theater. Exit
code 0. CI green. "Deploy verified." A hook wired in config. All of it can be true while the
thing you actually wanted did not happen, and nothing anywhere errors.

**The fix** is one skill per specific lie:

- [`git-pull-rebase-trap`](skills/engineering/git-pull-rebase-trap/SKILL.md) — with
  `pull.rebase=true` configured, `git pull --no-ff` **silently ignores your flag** and rebases
  anyway, rewriting every local commit. Check the config before pulling.
- [`github-pages-deploy-verification`](skills/engineering/github-pages-deploy-verification/SKILL.md) —
  "the deploy went green" is not "the site changed." The origin incident's verification loop
  passed instantly on *old* content. Poll for content that didn't exist before the push.
- [`claude-code-stop-hook-envelope`](skills/engineering/claude-code-stop-hook-envelope/SKILL.md) —
  a Claude Code Stop hook receives a JSON envelope on stdin, **not** the assistant's reply. A
  hook that greps stdin never fires and never errors: two production checks sat wired, green,
  and dead until an audit asked "has this *ever* fired?"

### #2: Help that quietly makes things up

> "…attributed to an arXiv paper that does not cite them — a fabricated cross-reference on real IDs."
>
> — [EVIDENCE.md, subagent-research-reliability](skills/orchestration/subagent-research-reliability/EVIDENCE.md) (2026-05-28)

**The problem.** The moment an assistant delegates to helper agents, three failures appear
that single-agent work never taught you to expect: a "research" agent that has no web tools
and fabricates citations from memory; parallel reviewers whose verdicts come back in formats
that can't be combined into one decision; and handoff documents that *order* the next agent —
which can see the actual code and knows better — not to question anything.

**The fix**, one skill per failure:

- [`subagent-research-reliability`](skills/orchestration/subagent-research-reliability/SKILL.md) —
  before dispatch, verify the helper actually has search tools; after return, verify the
  citations. Both failure modes were caught in one real session.
- [`parallel-review-disposition-schema`](skills/orchestration/parallel-review-disposition-schema/SKILL.md) —
  every reviewer answers in the same fixed format, so five strong reviews add up to one
  decision. Used in production twice before it was published.
- [`downstream-instruction-framing`](skills/orchestration/downstream-instruction-framing/SKILL.md) —
  prior decisions arrive as proposals with explicit "revisit if" conditions, so the
  better-informed reader keeps their judgment.

### #3: Momentum past the finish line

**The problem.** The moment one phase of work ends is exactly when an agent is most tempted to
charge into the next thing — leaving checks unrun and loose ends "probably fine."

**The fix:** [`closure-mode-at-boundaries`](skills/engineering/closure-mode-at-boundaries/SKILL.md)
forces a structured wrap-up first — checks actually run, loose ends actually verified — before
any "what's next" decision is made.

*(No epigraph on this one: it hasn't earned its receipt yet. It's one of two skills still owing
an evidence record — tracked in the open, [issue #1](https://github.com/MrBinnacle/skills/issues/1).)*

### #4: Most skills shouldn't exist

> "A list that shrinks when the models improve is the one telling you the truth about which skills still earn their keep."
>
> — [RETIRED.md](RETIRED.md), the retirement log

**The problem.** Skill collections have their own failure mode: accumulation. Every card you
add costs context space in every conversation, models keep improving past the cards, and
almost nobody tests whether a skill still changes the outcome.

**The fix** is the gate and the exit:

- [`skill-necessity-gate`](skills/meta/skill-necessity-gate/SKILL.md) — six questions that tell
  you whether a capability belongs in a skill, in your project rules, in a hook — or nowhere.
  It's the gate this very collection uses to stay small. Grounded in
  [Matt Pocock's methodology](https://github.com/mattpocock/skills) and Anthropic's official
  skill-authoring guidance.
- [RETIRED.md](RETIRED.md) — the exit, in public. It has already fired: in July 2026, four of
  the author's own candidates were tested at the admission gate and **the model passed every
  run without them** — so none got in.

## The skills

The complete reference. Skills marked **⊙ receipt** carry a full dated
[`EVIDENCE.md`](skills/engineering/git-pull-rebase-trap/EVIDENCE.md); the two that don't say so
plainly and are being brought under the same standard.

**Engineering** — disciplines for shipping software

- [**git-pull-rebase-trap**](skills/engineering/git-pull-rebase-trap/SKILL.md) — check
  `pull.rebase` before any pull; `--no-ff` won't save you.
  [⊙ receipt](skills/engineering/git-pull-rebase-trap/EVIDENCE.md)
- [**github-pages-deploy-verification**](skills/engineering/github-pages-deploy-verification/SKILL.md) —
  verify a deploy by polling for content that didn't exist pre-push. Origin incident is on a
  public repo — independently checkable.
  [⊙ receipt](skills/engineering/github-pages-deploy-verification/EVIDENCE.md)
- [**claude-code-stop-hook-envelope**](skills/engineering/claude-code-stop-hook-envelope/SKILL.md) —
  Stop hooks get an envelope, not the reply; read `transcript_path`, and prove your hook is
  alive. [⊙ receipt](skills/engineering/claude-code-stop-hook-envelope/EVIDENCE.md)
- [**closure-mode-at-boundaries**](skills/engineering/closure-mode-at-boundaries/SKILL.md) —
  structured wrap-up at phase boundaries before any "what's next." *(receipt owed —
  [#1](https://github.com/MrBinnacle/skills/issues/1))*

**Orchestration** — disciplines for multi-agent work

- [**subagent-research-reliability**](skills/orchestration/subagent-research-reliability/SKILL.md) —
  verify tools before dispatch, citations after return.
  [⊙ receipt](skills/orchestration/subagent-research-reliability/EVIDENCE.md)
- [**parallel-review-disposition-schema**](skills/orchestration/parallel-review-disposition-schema/SKILL.md) —
  one fixed answer format so parallel verdicts actually merge.
  [⊙ receipt](skills/orchestration/parallel-review-disposition-schema/EVIDENCE.md)
- [**downstream-instruction-framing**](skills/orchestration/downstream-instruction-framing/SKILL.md) —
  handoffs as proposals with revisit-conditions, never orders.
  [⊙ receipt](skills/orchestration/downstream-instruction-framing/EVIDENCE.md)

**Meta** — skills about the skill system itself

- [**skill-necessity-gate**](skills/meta/skill-necessity-gate/SKILL.md) — should this even be a
  skill? Six questions; most ideas correctly fail. *(receipt owed —
  [#1](https://github.com/MrBinnacle/skills/issues/1))*

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

Six of the eight skills carry full evidence records today; the rest of the collection is being
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

Authored by [Matthew Gruber](https://github.com/MrBinnacle). Structure inspired by
[mattpocock/skills](https://github.com/mattpocock/skills) — the epigraphs here quote our own
evidence records instead of the classics, because that's the shelf we stock.

## License

MIT — see [LICENSE](LICENSE).
