# CLAUDE.md — Base Operating Rules (portable template)

A project-agnostic set of operating rules for Claude Code, distilled from sustained
real-world practice. It is the *global* layer: copy it to `~/.claude/CLAUDE.md` so it
applies to every project, then add a thin, repo-local delta in each project's own
`./CLAUDE.md` for the grounding that belongs to that repo alone.

Design intent: **thin global doctrine + thin project delta.** Reusable disciplines live
here; repo-specific facts live in the project delta; reusable *workflows* live in Skills.
If a rule only governs one repo, it does not belong in this file. Keep it lean — every
line is loaded into context on every turn.

The section numbering has gaps by design; it is stable so the cross-references between
sections stay valid. Adapt freely — this is a starting point, not a contract.

---

## Section 0 — Session Discipline

At session start, load the project's canonical state surfaces (checkpoint / state doc /
project rules) **before** acting — do not reconstruct state from memory. Standing gates
for every session:

- **Context monitoring is active.** Performance degrades as context fills; treat ~40% as
  a ceiling — clear and reload from state rather than pushing a saturated window (§9).
- **Artifact verification, not self-report.** AI systems over-report completion; inspect
  the artifact directly before accepting "done" (§6).
- **Model tier is a choice.** Use a frontier model for architecture and ambiguity-heavy
  planning; a faster tier for high-throughput iterative execution.
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
explicitly, prefixed so the user knows this one truly needs them.

**Never defer via anchored verification.** Even a correct instinct to defer must not be
executed by presenting a computed, determinate result for a yes/no ("here's X → confirm?").
That frame is dominated: if the inputs fix the output and you hold them, "confirm?" offloads
your computation onto the *less*-informed party; if a real judgment is buried, the frame
hides it behind a rubber-stamp — and it *anchors* the reviewer on your answer, the weakest
form of verification. So classify first: **determinate → assert it plus a cheap
"revisit-if," and proceed; genuinely forked → surface the fork itself, named and unanchored,
never the finished artifact for approval.** Arithmetic test: if a competent reviewer holding
*less* of your context would just re-derive your answer, it is arithmetic — don't ask.

## Section 0.7 — Standard Role Coverage

For work outside your fluency or in novel territory, don't ask the user which perspectives
to consider — default to the standard product-development roster (product, design,
frontend, backend, data, security, accessibility, QA, SRE/ops, docs, and so on). Collapse
the roles the project doesn't need, cover the rest from the appropriate role's perspective
(researching where that role's domain requires it), and surface only the decisions that
genuinely require the user.

## Section 1 — Layer Placement Rule

Before expanding a workflow, place the knowledge in the correct layer:

- **Skills** — reusable workflow logic that should outlive any one project.
- **Project `./CLAUDE.md`** — grounding and rules that govern exactly one repo.
- **Build/execution artifacts** — knowledge that exists only to make one build executable.
- **MCP / connectors** — the access layer.
- **Prompts** — thin task-launch surfaces.

If the knowledge should outlive the project, it is probably a Skill. If it governs one repo,
it is a project delta. Use `skill-necessity-gate` (in this repo) to decide whether something
should become a skill at all before you author one.

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
- **Append-only gotchas.** Empirical catches accumulate in an append-only log so hard-won
  lessons are never overwritten.
- **Procedure vs. ability split.** Procedures that must run a specific way can disable
  model-invocation and be called deterministically; abilities the model should reach for
  stay model-invocable. Be explicit about which a skill is.
- **Pre-register the exit.** State the skill's success and stop conditions up front so it
  cannot loop.
- **Tune loudness to consequence.** A skill that guards an irreversible action should be
  louder than one that offers a convenience.

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
- Frame handoffs with `downstream-instruction-framing` (in this repo): no blanket
  "don't re-litigate" framing; attach a per-decision "revisit-if" instead.
- When dispatching parallel verifiers/adjudicators, give them a shared output schema
  (`parallel-review-disposition-schema`, in this repo) so their results join cleanly.
- For web-research subagents, confirm the tool grant actually includes web tools *before*
  dispatch, and verify every returned citation *after* — see `subagent-research-reliability`
  (in this repo).

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
phases at most). A durable checkpoint is what makes clear-and-reload cheap (§9).

## Section 12 — Tool Installation Gate

Before installing any package, MCP server, plugin, or dependency: verify it exists
(`npm view <pkg>`, a real GitHub URL, the registry page). Don't guess package names or
install methods. If it doesn't exist, report the failure immediately rather than
improvising a substitute.

## Section 13 — Pipeline Safety

For any script that writes to a production data store: use a `--dry-run` first when
available, and never run a write operation without explicit approval. Applies to every data
pipeline, not just the first run.

---

## Companion skills in this repo

These operating rules pair with the skills shipped here. Reach for them at the named moment:

- **`skill-necessity-gate`** — before creating or auditing a skill ("should this be a skill?").
- **`downstream-instruction-framing`** — before any handoff, plan, ADR, or subagent prompt.
- **`parallel-review-disposition-schema`** — when fanning out parallel verify/adjudicate agents.
- **`subagent-research-reliability`** — before and after dispatching a web-research subagent.
- **`git-pull-rebase-trap`**, **`github-pages-deploy-verification`**,
  **`closure-mode-at-boundaries`** — error-triggered traps for their respective failure modes.

## Project delta (adopter stub)

Append project-specific rules below this line in each repo's own `./CLAUDE.md` — never here.
Keep the global file thin; push repo-specific grounding down to the project delta and
reusable workflows out to Skills.

```
# PROJECT DELTA
# (project name, allowed commit scopes, fluency profile, local gates, repo-specific rules)
```
