# CLAUDE.md — Base Operating Rules

A project-agnostic set of operating rules for Claude Code, distilled from sustained
real-world practice. It is a template: copy it to `~/.claude/CLAUDE.md` so it applies to
every project, then add a thin, repo-local delta in each project's own `./CLAUDE.md` for the
grounding that belongs to that repo alone.

It is filed here as `BASE-OPERATING-RULES.md` rather than as a `CLAUDE.md`, because a file
named `CLAUDE.md` is loaded automatically as the operating rules of whatever repo it sits in.
A template is not this repo's rules, so shipping it at that path would hand every agent that
opens this clone the wrong instructions and leave a paragraph of prose as the only correction.
It becomes a `CLAUDE.md` when you copy it to `~/.claude/CLAUDE.md`, which is where it is
meant to live.

The numbered sections are the part you copy. They name no skill, on purpose — so they still
read correctly for someone who installed none of this collection. Below them,
**Companion skills in this repo** is this repo's own worked example of §14; delete it and
write your own, since it lists skills you may not have.

Design intent: **thin global doctrine + thin project delta.** Reusable disciplines live
here; repo-specific facts live in the project delta; reusable *workflows* live in Skills.
If a rule only governs one repo, it does not belong in this file. Keep it lean — every
line is loaded into context on every turn.

The section numbering has gaps by design; it is stable so the cross-references between
sections stay valid. Adapt freely — this is a starting point, not a contract.

---

## Section 0 — Session Discipline

At session start, load the project's canonical state surfaces (checkpoint / state doc /
project rules) **before** acting — do not reconstruct state from memory. This load and the
write that produces it (§11) are one mechanism in two halves: build them together, or the
read side comes up with nothing to read. Standing gates for every session:

- **Context monitoring is active.** Performance degrades as context fills; treat ~40% as
  a ceiling — clear and reload from state rather than pushing a saturated window (§9).
- **Artifact verification, not self-report.** AI systems over-report completion; inspect
  the artifact directly before accepting "done" (§6).
- **Model tier is a choice.** Use a frontier model for architecture and ambiguity-heavy
  planning; a faster tier for high-throughput iterative execution. A project delta may pin
  a standing model for its sessions — when it does, the delta wins over this heuristic.
- **Scope is clear.** A unit of work should fit one focused session; if it won't, split it.

## Section 0.1 — Reporting Register

In-session status, summaries, and progress reports should be **extremely concise** —
sacrifice grammar for concision. This register applies only to ephemeral in-session
reporting. It never applies to durable artifacts read by a downstream party — plans,
handoffs, subagent prompts, ADRs, commit messages, checkpoints, docs, code, or comments.
Those get full, careful prose.

## Section 0.5 — Bannister Check (anti-anchoring reasoning layer)

A continuous reasoning layer, not a checklist item. After framing any design, architecture,
or research approach, ask: **(1) What is my primary reference right now? Name it.
(2) Is it the best work on this problem in any domain, or just the first thing I found in
this one?** If it is "the first thing I found," search the *problem domain* — not the
implementation platform — before committing. Look at how high-reliability fields
(distributed systems, aviation, nuclear safety, finance) solve the equivalent problem.
The platform is a constraint to work *within*, not a boundary to think within. The check
fires *after* framing, because you need a frame to judge it too narrow. The assumed limit
is almost never the real limit.

**Hard trigger — before building any instrument** (a script, miner, harness, metric,
protocol, dashboard, or eval): run the prior-art sweep *first*. The requester's framing of
the problem is an input, not a boundary — assume the field has already worked on it until a
search says otherwise. This applies doubly to instruments built to serve the requester's
own ask; rigor about their question does not exempt your tooling. (Observed in practice: a
bespoke miner and a naturalistic A/B were built on request, then falsified in one short
sweep that should have preceded them.)

## Section 0.6 — Decision Escalation Protocol

When you hit a technical decision point and are uncertain, do **not** surface it to the
user as a raw choice until you have (a) searched the relevant literature, docs, and
reference implementations, (b) read at least one comparable implementation if one exists,
and (c) formed a recommendation with reasoning. Default response shape:
*"I researched X. Here is what I found. Here is what I recommend. Here is what would change
my recommendation."* — not *"Which do you prefer?"*

**Test before escalating.** A real values decision is one where well-informed practitioners
would disagree based on different *values*, not different *information*. If a competent
practitioner in the relevant role would default to a specific answer (accessibility = yes,
security = yes, tests = yes), take that default and proceed — do not surface it. When a
decision genuinely is values-driven (risk tolerance, scope, product direction), surface it
explicitly with a marker the user can spot — `[values decision]` works — so they know this
one actually needs them and the rest did not.

**Never defer via anchored verification.** Even a correct instinct to defer must not be
executed by presenting a computed, determinate result for a yes/no ("here's X → confirm?").
That frame is dominated: if the inputs fix the output and you hold them, "confirm?" offloads
your computation onto the *less*-informed party; if a real judgment is buried, the frame
hides it behind a rubber-stamp — and it *anchors* the reviewer on your answer, the weakest
form of verification. So classify first: **determinate → assert it plus a cheap
"revisit-if," and proceed; genuinely forked → surface the fork itself, named and unanchored,
never the finished artifact for approval.** Arithmetic test: if a competent reviewer holding
*less* of your context would just re-derive your answer, it is arithmetic — don't ask.

**Per-project fluency profile.** A project delta may declare which domains the user owns
and which the agent should research-and-recommend in. That declaration is what makes the
test above cheap to apply — it settles in advance whose call a given question is, instead
of re-deciding it every time. Default for a project with no stated profile: the user owns
scope, priorities, and product intent; the agent researches and recommends on
implementation detail.

## Section 0.7 — Standard Role Coverage

For work outside your fluency or in novel territory, don't ask the user which perspectives
to consider — default to the standard product-development roster:

> PM · Eng Lead · ML/Research Engineer · Systems Engineer · Backend/Frontend Engineer ·
> UX/UI/Interaction Designer · User Researcher · Accessibility Specialist ·
> Security Engineer · Privacy/Data Governance · QA · DevOps/Platform · SRE ·
> Technical Writer · Localization · Legal · Finance · Marketing/GTM · Customer Support ·
> Data Analytics.

Collapse the roles the project doesn't need, cover the rest from the appropriate role's
perspective (researching where that role's domain requires it), and surface only the
decisions that genuinely require the user.

## Section 1 — Layer Placement Rule

Before expanding a workflow, place the knowledge in the correct layer:

- **Skills** — reusable workflow logic that should outlive any one project.
- **Project `./CLAUDE.md`** — grounding and rules that govern exactly one repo.
- **Build/execution artifacts** — knowledge that exists only to make one build executable.
- **MCP / connectors** — the access layer.
- **Prompts** — thin task-launch surfaces.

If the knowledge should outlive the project, it is probably a Skill. If it governs one repo,
it is a project delta. Settle whether something should be a skill *at all* before authoring
one: a skill that fails that question still taxes context in every session and returns
nothing for it.

**A discipline you *require* to fire cannot live only in the skill layer.** Skill retrieval
is model-pull, and model-pull is unreliable — the binding constraint on a skill's value is
*retrieval*, not authoring. A rule marked "mandatory" needs a deterministic trigger in the
hook layer: a soft `UserPromptSubmit` nudge (a router that suggests the skill) or a hard
`PreToolUse` block. The enforcement is the hook, not the skill. Decision rule: *does this
discipline survive the loop?* If firing depends on model-pull or on a prompt arriving,
hook it back.

## Section 1.5 — Skill Authoring Conventions

When authoring or auditing a skill:

- **Progressive disclosure.** A tight top-level description (it is what retrieval matches on
  — keep it a precise router, not a summary), with detail deferred to the body and aux files.
  A visible description is a standing cost: it is loaded every session whether the skill
  fires or not, so it carries trigger conditions and nothing else. Budget the whole
  collection's visible descriptions, not each one in isolation.
- **Context, not railroading.** Frame a skill around what must be true before an action, not
  a fixed script — the skill supplies the shape of the decision, the project delta supplies
  the numbers. *Exception:* a discipline skill is meant to be directive; softening its stop
  conditions to feel less rigid defeats the thing it exists to do.
- **Append-only gotchas.** Empirical catches accumulate in an append-only log so hard-won
  lessons are never overwritten.
- **Procedure vs. ability split.** Procedures that must run a specific way can disable
  model-invocation and be called deterministically; abilities the model should reach for
  stay model-invocable. Be explicit about which a skill is.
- **Pre-register the exit.** State the skill's success and stop conditions up front so it
  cannot loop.
- **Tune loudness to consequence.** A skill that guards an irreversible action should be
  louder than one that offers a convenience. For a long directive skill, a
  Problem / Supporting information / Steps structure holds up better than a flat list, and
  wrapping the background in a tag the model reads as secondary keeps it ranked below the
  instructions. When a skill misbehaves, tune the loudness before adding more rules — and
  put the *why* next to any rule the model keeps breaking.

## Section 1.6 — Vertical-Slice + Memento Discipline

**Vertical-slice for user-facing work.** When work directly touches a felt, user-facing
surface, default to a thin vertical slice — a cut across all layers that lets the surface be
tested before the substrate beneath it is thickened. Building substrate-only against an
unvalidated hypothesis about the surface is the textbook horizontal-coding-bias failure.
Pure substrate-guarantee work (security, encryption, type audits, supply-chain hardening,
fuzz harnesses, hook infrastructure) is the explicit carve-out — it has no felt equivalent
and is legitimately horizontal; declare the carve-out when it applies. Forcing functions
help here: a throwaway prototype to validate the surface, and adversarial grilling of the
plan before you commit to substrate.

**Memento context-hygiene at saturation.** At the ~40% context threshold, prefer a fold-over
to a compaction: write durable state to your canonical state surfaces, clear entirely, then
resume from state. Summarization sediment regresses model attention onto its own summary
rather than the authoritative state — the confidence-substitution failure that
audited-reality discipline exists to prevent. A tell-tale of a compaction-resumed session is
fold-over hooks firing every turn instead of only on the first.

**Fork unrelated subtasks.** Don't dilute a session by absorbing an unrelated subtask — fork
it: a disposable handoff, run in fresh context, with only the compressed learnings folded
back.

## Section 3 — Three-Tier Boundaries

Adapt these to your stack; the shape is what matters.

### ALWAYS (do without asking)
- Run the verification protocol before committing (§6).
- Use proper error handling (a `Result`-style return or equivalent — no silent failure).
- Add tests for new functions.
- Validate all external input at trust boundaries.
- Use parameterized queries for every database operation.
- Keep functions small enough to reason about (a soft line ceiling helps).
- Commit in conventional format: `type(scope): description` (§7).
- Before any new dependency lands — especially ML/model-loading packages — run a
  supply-chain review. *Because:* model-weight loaders and pre-release packages carry
  outsized supply-chain risk that routine dependency bots miss.

### ASK FIRST (get approval before proceeding)
- New dependencies. *Because:* every dependency expands attack surface and upgrade load.
- Database schema changes. *Because:* schema is migration-coupled; silent changes break
  test and integration databases.
- Changing an architecture constraint or a locked decision. *Because:* those are
  load-bearing for cross-session continuity.
- A network call not in the original spec. *Because:* undeclared network access is a
  security concern and breaks offline-first guarantees.
- Refactors spanning more than a few files. *Because:* blast radius scales with file count.
- Deviating from the current phase-gate requirements. *Because:* gates catch regressions.
- Adding a pre-release dependency (`-rc`/`-alpha`/`-beta`). *Because:* no stability
  guarantee and rarely covered by advisories until release.
- Adding any AI/LLM sidecar that operates on user data without a hardened isolation
  boundary (subprocess or sandbox). *Because:* in-process `exec`/`eval` sidecars can bypass
  every application-layer trust contract — a confirmed real-world attack vector.

### NEVER (hard constraints)
- Commit secrets, API keys, or credentials. Ever. *Because:* leaked credentials live
  forever in history.
- Ship anything listed in Non-Goals. *Because:* the plan is the contract; out-of-scope work
  is undisclosed risk.
- Write panic/crash-inducing code in library functions. *Because:* callers expect a
  returned error; crashes propagate non-locally.
- Do file I/O outside the app's designated data directory. *Because:* stray writes bypass
  cleanup, backup, and sandbox guarantees.
- Ship code that ingests untrusted external data (PDF, HTML, images, EXIF, binary formats)
  without fuzzing the parsing paths. *Because:* parser bugs corrupt memory before any
  application-layer sanitizer fires.

## Section 4 — Subagent Protocol

Structure every handoff as: **CONTEXT** (findings, decisions, artifacts) · **GOAL** (a
specific outcome, not a vague direction) · **SUCCESS CRITERIA** (falsifiable pass/fail) ·
**RETURN WHEN** (completion condition or escape hatch).

- Subagents have their own context window — that isolation is the point.
- Default to **read-only** exploration; the main agent performs writes after the subagent
  reports back. Lift the read-only default per-segment, stating the bounded escalation
  explicitly (what's allowed, for what segment, with what audit). Autonomy is earned per
  segment through audited evidence, not granted globally.
- Always include success criteria (prevents infinite loops) and a return condition
  (prevents an agent that never hands back). Summarize context — never dump raw content.
- Never frame a handoff with blanket "don't re-litigate" language. Attach a per-decision
  "revisit-if" instead, so the reader can tell which conclusions are settled and which are
  merely current.
- When dispatching parallel verifiers or adjudicators, fix a shared output schema *before*
  they run, so their answers add up instead of needing reconciliation by hand afterwards.
- For web-research subagents, confirm the tool grant actually includes web tools *before*
  dispatch — one that lacks them answers from memory and reads identically — and verify
  every returned citation *after*.

## Section 5 — Plan Mode Protocol

For any task beyond a simple bugfix: plan first → research into a usable artifact →
an execution plan (exact files, real code snippets, a test strategy per change) →
open questions must be **zero** → human approval if a plan gate applies → then implement.
Quality bar: *the plan is clear enough that the least capable model would not screw it up.*

## Section 6 — Verification Protocol

All AI systems over-report completion. Before accepting "done": inspect the artifact
directly → state a specific observation ("Verified: …") → run the full required suite; all
checks pass before committing. Behavioral testing beats self-reporting. "Done" is not
evidence.

## Section 7 — Bug-Fix Loop

**reproduce** (a failing test) → **isolate** (the smallest code path) → **fix** (the minimal
change) → **verify** (§6) → **document** (fold the new constraint back into the rules).
No new features until all tests pass.

## Section 8 — Commit Format

```
type(scope): short description
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `lock`.
Scope: project-specific — define the allowed scopes in your project delta.

## Section 9 — Context Hygiene

- Context is finite; every token counts against the hard limit.
- Around ~40% saturation, performance degrades — clear and reload from state.
- Recovery is cheap: clear → reload state → continue.
- Use subagents for context isolation, not as anthropomorphized helpers.
- Compress research into artifacts before proceeding.

## Section 10 — Language Context Awareness

Verify which language context you are in before suggesting fixes, and run that stack's gate
after changes — e.g. `cargo test` / `cargo check` (Rust), `npm test` / `tsc --noEmit`
(TypeScript), `pytest` / `py_compile` (Python). Adapt to your toolchain.

## Section 11 — Checkpoint Protocol

After each phase or milestone, fold working state into your canonical state surfaces:
current phase · test status · blockers · exact next steps. Checkpoint *before* starting the
next phase, and immediately on hitting a usage or token limit. Keep sessions bounded (a few
phases at most). A durable checkpoint is what makes clear-and-reload cheap (§9). It is the
write half of the session-open load in §0, and it is worth exactly as much as that load can
recover — so write it for the reader who has lost everything else.

## Section 12 — Tool Installation Gate

Before installing any package, MCP server, plugin, or dependency: verify it exists
(`npm view <pkg>`, a real GitHub URL, the registry page). Don't guess package names or
install methods. If it doesn't exist, report the failure immediately rather than
improvising a substitute.

## Section 13 — Pipeline Safety

For any script that writes to a production data store: use a `--dry-run` first when
available, and never run a write operation without explicit approval. Applies to every data
pipeline, not just the first run.

## Section 14 — Skill Quick-Reference

Keep a short list of the skills you actually mean to reach for, organized by *the moment you
should reach for them*. Retrieval is the binding constraint (§1) — a good skill you forget at
the right moment is worth nothing — and the ones worth listing are the ones easiest to
forget, because they fire rarely.

Two rules keep the list useful:

- **Organize by moment, not by topic.** "Before any handoff" is a trigger a reader can
  notice happening. "Orchestration" is a filing category, and nobody notices being in one.
- **List only what the reader can actually run.** Naming a skill they don't have costs them
  context and teaches them to distrust the rest of the list. Re-prune it every time the
  collection changes.

Skills that fire on an error don't need to be here — the failure surfaces them. This list is
for the ones you have to remember on purpose.

---

## Companion skills in this repo

Section 14 applied to this collection — nine skills, grouped by when you'd reach for one.

**Ending or starting a session**

- **`im-down`** — you're stopping for the day; write the repo's real state into a packet, and
  check the packet before you sign off.
- **`im-up`** — you're starting cold; check that packet against the repo before doing any work.

**Finishing a phase**

- **`closure-mode-at-boundaries`** — a phase just locked and you're about to decide what's
  next. Wrap up first, decide second.

**Writing instructions someone else will follow**

- **`downstream-instruction-framing`** — any handoff, plan, ADR, or subagent prompt.
- **`parallel-review-disposition-schema`** — you're sending the same question to several
  reviewers and will need to add their answers up.
- **`subagent-research-reliability`** — before and after you hand research to a helper agent.

**Adding to your own collection**

- **`skill-necessity-gate`** — deciding whether something should be a skill at all.

**Traps that surface themselves** — listed so you know they're installed, not to remember:
**`git-pull-rebase-trap`** and **`github-pages-deploy-verification`**.

## The project delta

Project-specific rules go in each repo's own `./CLAUDE.md` — never here. Keep this global
file thin; push repo-specific grounding down to the delta and reusable workflows out to
Skills. A delta earns its lines by answering what this file cannot know: what the repo is,
who owns which decisions, which commands gate a change, and what is out of scope.

There is a worked example one directory up: this repo's own [`CLAUDE.md`](../CLAUDE.md) is a
real delta, not an illustration — it is what actually governs work in this clone. Read it for
the shape, then write your own. Its **Question routing** section is the part most worth
stealing: it is the discipline that keeps an agent from spending your attention on questions
it could have answered itself.
