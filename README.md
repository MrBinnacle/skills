<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="skills — that have to earn their keep, with the receipts to prove it" src="assets/banner-light.svg" width="620">
  </picture>
</p>

# skills

**A small collection of agent skills that have to earn their keep — with the receipts to prove it.**

```bash
npx skills add MrBinnacle/skills
```

That's the whole install — works with Claude Code and [70+ other agents](https://github.com/vercel-labs/skills).
You'll be shown the nine skills and can pick which to take.

## What this is

AI coding assistants like Claude Code can be given **skills** — small instruction files that
teach the assistant how to handle a specific situation. Think of a skill as a recipe card
pinned above the stove: when that situation comes up, the assistant reads the card and follows
it instead of improvising.

This repo is a collection of those cards. Most exist because an AI assistant actually got
something wrong — or nearly did — and the card stops it happening again. Two exist because I
wanted a better way to hand work between sessions, so I built one. Their records say that.

**What makes this collection different: every card has to earn its keep.** Most skill
collections only ever grow. This one also shrinks. Each card carries a plain record of where it
came from (`EVIDENCE.md`), and when new AI models get smart enough to no longer need a
card, I test for that and retire it — publicly. A skill you install from here is one that
still does something.

It is also **small on purpose**. Nine skills, not nine hundred. Adding a skill costs you
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

Seven of these skills answer a failure that actually happened. The other two I built because I
wanted them. They all fall into the same four failure modes, and where a skill has earned its
receipt, the section opens with a line from it.

### #1: Silent failure

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
- [`im-up`](skills/engineering/im-up/SKILL.md) — a handoff note saying the state was checked is
  not the same as state that was checked. The receiver re-checks branch and HEAD against the
  repo, tests every claim, won't run commands the packet hands it, and rejects a stale packet.
  The side that wrote it doesn't get to mark its own work.

### #2: Mini peer review (aka don't get your research (in)validated by a confused subagent)

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

### #3: Carrying too much momentum past the finish line

> "Synthesizing into a menu without executing is sequencing pretending to be orchestration."
>
> — [gotchas.md, closure-mode-at-boundaries](skills/engineering/closure-mode-at-boundaries/gotchas.md) (2026-05-24)

**The problem.** The moment one phase of work ends is exactly when an agent is most tempted to
charge into the next thing — leaving checks unrun and loose ends "probably fine."

**The fix**, at two scales:

- [`closure-mode-at-boundaries`](skills/engineering/closure-mode-at-boundaries/SKILL.md) — at a
  *phase* boundary, it sends a set of reviewers at the work in parallel and turns what they
  send back into a list of things to actually do — claims to check, estimates to re-audit,
  options to delete — which you work through before you are allowed to pick what's next. The
  origin session caught a migration whose real cost was 2–3× the plan's estimate, exactly at
  that boundary.
- [`im-down`](skills/engineering/im-down/SKILL.md) — the same idea at the end of a whole session:
  it writes the repo's real state — branch, HEAD, what you were doing, what failed — into one
  packet, and a validator refuses to sign it off until every claim in it carries a check that
  passes. The next session starts from that instead of from memory.

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
- [RETIRED.md](RETIRED.md) — the exit, in public. It has already fired both ways: in July 2026,
  four of my own candidates were tested at the admission gate and **the model passed
  every run without them**, so none got in — and one skill that *had* shipped was retired
  outright when a Claude Code change made it unnecessary, evidence record intact.

## The skills

The complete reference. Each entry tells you three things: **when it fires**, **what it
actually does when it runs**, and **what you are holding when it finishes**. Every skill
carries a dated evidence record — follow any **⊙ receipt** link.

Groups run from the broadest reach to the narrowest, and so do the skills inside them: the
first entry is the one nearly every repo needs, the last is for a specific situation you may
never be in.

Four of the nine are marked **hand-invoked** — they carry `disable-model-invocation: true`, so
your assistant will never start one on its own. You run them. That is deliberate: each one
decides something you should stay in charge of.

**Engineering** — disciplines for shipping software

- [**git-pull-rebase-trap**](skills/engineering/git-pull-rebase-trap/SKILL.md)

  Fires when you are about to `git pull` and the repo might have `pull.rebase = true` set —
  often inherited from a team `.gitconfig` nobody re-reads. It has you run two config
  checks (`pull.rebase` and `branch.<current>.rebase`) *before* the pull. If either is
  true, it stops you using `git pull` at all and gives you the explicit two-step instead:
  `git fetch`, then either `git merge --no-ff` for a real merge commit or `git rebase` if
  you genuinely want the linear history. If you already pulled and it already happened,
  there is a recovery procedure — pull the old SHAs out of the reflog, map them to the new
  ones, backfill every state file and ledger that referenced them in a single commit
  labelled as a post-rebase backfill, and get explicit authorization before any force-push.
  You end up with a pull that merged or rebased because you chose it, and local commit SHAs
  that nothing silently rewrote. The fact underneath it: `--no-ff` is a *merge* flag, so
  under `pull.rebase=true` it is silently ignored and the rebase runs anyway. `--ff-only` is
  the one flag that refuses loudly instead.
  [⊙ receipt](skills/engineering/git-pull-rebase-trap/EVIDENCE.md)

- [**im-down**](skills/engineering/im-down/SKILL.md) · hand-invoked

  You run this when you are signing off and the next session has to resume from checked
  facts rather than from whatever the conversation remembers. It reads
  `.claude/session-boundary.json` and stops if that config is missing, then runs
  `snapshot_state.py` to generate a packet stamped with the branch and HEAD. You then fill
  in every `__REQUIRED__` marker it left: the objective, the exact next action, the
  approaches that failed and the things that turned up nothing, in the order they happened,
  and the decisions you made with the reasons you made them. Every load-bearing claim gets
  marked verified or unverified, and a verified one has to carry a typed probe — a path, a
  commit, or a command drawn from the config's allowlist. Finally `validate_packet.py` runs
  in produce mode, and the packet is not finished until that returns `ACCEPTED`. You finish
  holding one packet file, its ID, the HEAD it was cut against, and the exact command the
  next session should run. Two constraints worth knowing before you adopt it: write the
  packet *after* your last commit, because a later commit moves HEAD and the receiver will
  reject the packet as stale, and keep the packet directory out of version control.
  [⊙ receipt](skills/engineering/im-down/EVIDENCE.md)

- [**im-up**](skills/engineering/im-up/SKILL.md) · hand-invoked

  The other half. You run it at the start of a cold session, pointed at a packet, before any
  work begins — and it treats that packet as untrusted data, with the repository and the
  configured checks outranking anything the packet asserts. It runs `validate_packet.py` in
  receive mode against the repo root and rejects the packet outright if the branch or HEAD
  no longer match the repository, if a claim marked verified has a probe that fails, if a
  required field is missing, if a command probe is one the config never authorised, if there
  is an unfinished marker or something that looks like a secret in the file, or if the next
  action reaches past the scope the packet declared. It runs only the trusted checks named in
  your repo config, and it will not run a command that exists nowhere but inside the packet.
  You end with an acceptance receipt — the validator's JSON unchanged, plus two lines stating
  the objective and the next action — or with a rejection that goes back to the producer to
  fix. Work starts on `ACCEPTED` and not before. The point of the split: the side that wrote
  the packet does not get to grade it.
  [⊙ receipt](skills/engineering/im-up/EVIDENCE.md)

- [**closure-mode-at-boundaries**](skills/engineering/closure-mode-at-boundaries/SKILL.md) ·
  hand-invoked

  You run this at the moment a sprint, a phase, or a vertical slice locks clean, or when a
  "what should we do next" question surfaces two or more real candidates — not mid-build and
  not mid-debug. It dispatches a roster of reviewer agents in parallel, in a single message,
  with one of them specifically assigned to attack the frame and say what is *missing*. What
  comes back is not a panel of opinions to read: the skill turns it into an action list —
  claims to go and grep-check, scope estimates to re-audit where the cost came from looking
  at one site, pre-flight work to schedule, candidates to add, dead candidates to delete
  outright rather than keep "for completeness" — and then you execute that list. Only after
  it is executed do you look at the decision again. You finish with the checks actually run,
  the dead options actually gone, and either one named pick or an honest statement of the
  values question separating the options that survived. The failure mode it exists to stop is
  running the review and forwarding its output as a menu, which is sequencing wearing
  orchestration's clothes. Adopting it needs a runtime that can dispatch agents in parallel,
  at least two agents suitable for the roles, and a decision about where your project's real
  "what's next" lives; sibling files map the roles to common runtimes and give you
  copy-pasteable prompts.
  [⊙ receipt](skills/engineering/closure-mode-at-boundaries/EVIDENCE.md)

- [**github-pages-deploy-verification**](skills/engineering/github-pages-deploy-verification/SKILL.md)

  Fires when you are about to push to a branch where merging *is* the production deploy on a
  CDN-fronted static host — GitHub Pages, Netlify, Vercel, Cloudflare Pages, S3 behind
  CloudFront. It makes you pick the poll marker properly first: run
  `git diff HEAD~1 | grep '^+'` and choose a string that genuinely did not exist before this
  push — a new CSS declaration, a new class, a new line of copy — never an element selector
  that already shipped, and never a token *name* when only its value changed. Then it has you
  prove the marker is new by grepping production for it right after the push and getting
  nothing back, run an until-loop that curls the live URL until the marker appears, and
  finish with a broader verification grep. You end up holding evidence that the CDN is
  serving your new bytes, which is a different claim from the deploy going green. Two things
  it saves you from: the platform's own status API, which reports `building` after the site
  is live and `built` before the edge has caught up, and `sleep N && curl` chains, which
  Claude Code's Bash tool blocks. And a self-check — if the loop exits in under five seconds
  on a platform that normally takes thirty, your marker matched old content and you need a
  new one.
  [⊙ receipt](skills/engineering/github-pages-deploy-verification/EVIDENCE.md)

**Orchestration** — disciplines for multi-agent work

- [**subagent-research-reliability**](skills/orchestration/subagent-research-reliability/SKILL.md)

  Fires twice: once when you are about to hand research to a helper agent, and again when
  that agent's findings come back and you are deciding what to act on. Before dispatch, it
  has you open the agent's own definition file and read the `tools:` line in its frontmatter
  rather than its description — because an agent advertised as "performs web research" can
  have a tool grant of `Read, Bash, Grep`, in which case it cannot search at all and will
  quietly answer from memory. If the grant is wrong, dispatch a general-purpose agent with
  the research protocol in the prompt instead. After the findings return, it has you dispatch
  a second, separate agent whose only job is to fetch each source URL and label it
  `VERIFIED`, `PARTIAL`, `UNRESOLVED`, or `UNCONFIRMABLE` — told explicitly to check whether
  the source exists and says what was claimed, and not to opine on quality. You end up with a
  findings list where only the survivors are actionable and the rest are dropped or annotated
  where they sit. It catches dead links, invented CVE and arXiv IDs, and the nastiest case:
  a real ID bolted onto a source that never mentions it.
  [⊙ receipt](skills/orchestration/subagent-research-reliability/EVIDENCE.md)

- [**downstream-instruction-framing**](skills/orchestration/downstream-instruction-framing/SKILL.md)

  Fires whenever you write something another reader will execute later — a handoff, a plan,
  an ADR proposing future work, a subagent dispatch prompt, a brief for a scheduled agent. It
  opens the document with a block that names the evidence asymmetry out loud (what you could
  not see when you wrote this), lists the concrete advantages the reader has that you did
  not, and licenses them to disagree with reasoning rather than silently comply. It makes
  every prior decision carry its own `Revisit if:` condition instead of sitting in a list
  headed "do not re-litigate" — a phrase it permits only when it is scoped to one named
  question closed in the current conversation. It converts imperative mood into proposal
  mood, with a lookup table for the common cases ("Execute the following plan" becomes
  "Recommended execution path"). Then it hands you a seven-point checklist to run over the
  draft before you send it. You end with a handoff the next reader can overrule on evidence,
  and — the part that pays off upstream — a test on your own thinking: if you cannot name the
  condition that would make you revisit a decision, that decision is probably
  under-justified. Subagent prompts are the riskiest case, because a subagent reads its
  prompt as near-system-tier and will rarely push back even when told it may.
  [⊙ receipt](skills/orchestration/downstream-instruction-framing/EVIDENCE.md)

- [**parallel-review-disposition-schema**](skills/orchestration/parallel-review-disposition-schema/SKILL.md)

  Fires when you are dispatching three or more isolated agents to decide *what to do* about a
  set of findings you have already confirmed are real. The isolation is what stops them
  groupthinking each other, and it is also what makes five good reviews fail to add up to one
  decision — so this skill fixes the output shape upstream, in the dispatch, because you
  cannot recover comparability afterwards. It puts four things in every seat's prompt: a
  closed list of allowed dispositions so each seat picks from the same vocabulary; one
  identical per-item block, including a "what would change this" field that exposes the
  load-bearing assumption; explicit ownership, so each seat is handed its own findings with
  the evidence inline instead of re-deriving the whole corpus; and a mandatory closing status
  line of `nominal`, `degraded`, or `blocked`. You end with verdicts you can group by
  disposition at synthesis rather than reconcile as prose, with disagreements you can
  classify, and with any seat that could not do its job saying so structurally — so a
  degraded seat's lone finding lands in "unaddressed" instead of vanishing. A sibling file
  covers the upstream stage, where the question is still "are these findings real."
  [⊙ receipt](skills/orchestration/parallel-review-disposition-schema/EVIDENCE.md)

**Meta** — skills about the skill system itself

- [**skill-necessity-gate**](skills/meta/skill-necessity-gate/SKILL.md) · hand-invoked

  You run this when someone — possibly you — says "let's make a skill for X", when auditing
  whether a skill you already have still earns its context cost, or before building any
  measurement instrument, which is the same kind of bet. It is six gates in order, cheapest
  first, and a candidate has to pass all six; you stop at the first failure and route the
  idea where that gate sends it. **Gate 0** asks whether it is skill-shaped at all — a fact
  or a stable preference belongs in your rules file, access to a system belongs in an MCP
  server, anything the agent could learn by reading the repo belongs nowhere, and anything
  relevant in *every* session should be pushed into always-on rules instead. Most candidates
  die here. **Gate 1** asks whether the pattern actually recurs, and tells you to measure it
  rather than predict it — park the idea and count how often you reach for it. **Gate 2**
  weighs value against cost, with the eval built before the docs and run with and without the
  skill. **Gate 3** picks the kind: a procedure you invoke by hand costs zero standing tokens
  and keeps the strategic thinking yours; an ability the model pulls in costs roughly a
  hundred always-on tokens and lives or dies by its description. **Gate 4** asks whether it
  needs to remember anything across sessions. **Gate 5** shapes it for low cost. You end with
  a routed decision and the reason for it — most often "not a skill, put it here instead."
  Two further modes cover auditing a bloated library and detecting the skills you are missing.
  [⊙ receipt](skills/meta/skill-necessity-gate/EVIDENCE.md)

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

*Confidence is not evidence* — including mine. So skills here carry an
[`EVIDENCE.md`](skills/engineering/git-pull-rebase-trap/EVIDENCE.md): a dated record of
where the skill came from, what it has been validated against, and its measured
result — including **UNMEASURED** stated plainly when something can't be measured yet, rather
than a made-up score.

Evidence in these records comes in named tiers, so you always know which one you are
reading. **Controlled results** (the Screen / Paired-verdict fields) come from with-vs-without
runs under the pre-registered harness protocol. **Origin incidents** are the dated real-world
failures behind most of these skills, marked `OBSERVED` with the date. Two records say
`DESIGNED` instead: I built the session-boundary pair because I wanted it, not because
something broke. Different thing, different label. The weakest tier,
**Observed in use (self-reported)**, is
field observation from my own sessions: events mined from my private work logs by my
own AI assistant and re-checked by a second instance of the same AI system — a process
that catches extraction errors, not self-favoring selection, and involves no independent
verification. Admission bar for that tier: every event traces to a dated artifact, carries its
model ID, and states plainly what is observed versus not measured; events that cannot meet the
bar stay out. Self-reported rows never fill or color the controlled fields — those stay
UNMEASURED until a real screen runs. (Aviation's incident-reporting system and clinical case
reports work the same way: self-report the reader cannot re-check is a legitimate evidence
class exactly as long as it is labeled as such.)

The part most collections lack: **the ground moves — models improve, and so does the platform
they run on — and a skill only matters while something still needs it.** When a major model
release lands, skills get re-screened with
[skill-harness](https://github.com/MrBinnacle/skill-harness) — a tool that runs the same task
with and without the skill and honestly reports the difference. A skill the new model no longer
needs — or one the platform has fixed outright — gets retired in public, evidence record intact:
see the [retirement log](RETIRED.md). Progress becomes collection history, not silent rot.

Every skill in the collection carries an evidence record — down to honest **UNMEASURED**
fields where no controlled test has run yet. The methodology — and why most "this skill scored 1.0!" benchmarks mislead —
lives in the harness repo:
[why naive skill benchmarks mislead](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md) ·
[the double-ceiling case study](https://github.com/MrBinnacle/skill-harness/blob/main/docs/case-studies/double-ceiling-structurally-unmeasured.md).

## Repository layout

```
skills/
  engineering/     workflow disciplines for shipping software
  orchestration/   disciplines for multi-agent work
  meta/            skills about the skill system itself
CLAUDE.md          the base operating rules — portable global doctrine for ~/.claude/CLAUDE.md
AGENTS.md          conventions for agents working inside this repo
```

Each skill folder contains `SKILL.md` (the entry point), `gotchas.md` (an append-only
log of observed failure modes — the skill's memory), and `EVIDENCE.md` (every shipped
skill carries one).

[`CLAUDE.md`](CLAUDE.md) is the reusable *global* operating-rules layer these skills
assume — the project-agnostic disciplines (Bannister anti-anchoring, decision escalation,
layer placement, verification, context hygiene) distilled from practice. It is the doctrine
this repo itself runs on; copy it to `~/.claude/CLAUDE.md`, then keep each repo's own
`./CLAUDE.md` thin.

## Contributing

Issues and PRs welcome — the full guide is [CONTRIBUTING.md](CONTRIBUTING.md). New skills run
the same gauntlet as mine:

1. It must pass the [skill-necessity-gate](skills/meta/skill-necessity-gate/SKILL.md) — most
   ideas correctly fail it.
2. It ships with a `gotchas.md` and, for anything claiming a real-incident origin, an
   `EVIDENCE.md` with the dated story.
3. Frontmatter is minimal (`name:` + `description:`, description ≤ 200 chars, quoted if it
   contains `: `), `SKILL.md` stays lean, and aux detail goes in sibling files.

Authored by [Matthew Gruber](https://github.com/MrBinnacle). Structure inspired by
[mattpocock/skills](https://github.com/mattpocock/skills) — the epigraphs here quote my own
evidence records instead of the classics, because that's the shelf I stock.

## License

MIT — see [LICENSE](LICENSE).
