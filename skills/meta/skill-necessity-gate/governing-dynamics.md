# Governing dynamics — the "why" behind each gate

Derived from Matt Pocock's skills methodology (152-source corpus), triangulated against
Anthropic's official docs and one academic study. Each gate in SKILL.md implements one or
more of these. Status: 5/7 core laws supported against non-Pocock (Anthropic) sources.

## The families
- **Economic** (should it exist at all): GD-1, GD-2, GD-3, GD-4.
- **Architectural** (what kind, once justified): GD-5, GD-6, GD-7.
- **Design-quality**: GD-8 (measure worth), GD-9 (positive procedures + hooks).
- **Autonomy** (what changes when the human turn is removed): GD-10 (loops relocate control).
- **Reflexive**: GD-11 (the gate applies to instruments, not just skills).

## GD-1 · A skill is a bet that a pattern recurs
A skill saves work only if you use it repeatedly — in shorthand:
Value ≈ (re-derivation cost + transcription cost) × recurrence × stability. Frequency — not
complexity — is the criterion; Pocock's "too simple to require a skill" prompts often warrant
skills. Anthropic (code.claude.com/docs/en/skills): "Create a skill when you keep pasting the
same instructions... or when a section of CLAUDE.md has grown into a procedure rather than a fact."

## GD-2 · Every skill taxes the whole system (the standing cost)
Model-invocable skills load ~100 metadata tokens **always** (Anthropic overview: "loaded at
startup and included in the system prompt"). The skill-list budget ≈ **1% of context**; on
overflow, "descriptions for the skills you invoke least are dropped first" (Claude Code docs).
Live instructions also dilute attention. NOTE: Pocock's "300–500 instructions before
degradation" is his figure and is NOT Anthropic-backed — the real curve (IFScale, arXiv
2507.11538) is continuous + model-dependent (best reasoning models ~near-perfect to 100–250,
then ~63–69% at 500). Treat instruction budget as a *curve*, not a cliff.

## GD-3 · Equilibrium — benefit must exceed cost, and it's measurable
Anthropic operationalizes it: `skill-creator` "aggregates pass rate, time, and tokens for
with-skill versus without-skill" so you compare improvement against overhead. Don't argue
worth — measure it.

## GD-4 · The absence signal is repetition-without-crystallization
A skill that should exist shows up as the same reasoning/prompt re-performed manually across
sessions with no home. Pocock's method: park a candidate in the skills folder, count
reach-for-it frequency. Second signal: two skills always run together → a missing merged skill
(/grill-me + /ubiquitous-language → /grill-with-docs).

## GD-5 · Layer is prior to skill — push vs pull
The prior question is *which layer / loading discipline*: always-loaded push (CLAUDE.md) vs
on-demand pull (skill), via Anthropic's "progressive disclosure" (metadata always / body on
trigger / resources on demand). A skill is the wrong instrument for always-on knowledge.

## GD-6 · Invocation control — abilities vs procedures (four states)
Two independent Claude Code frontmatter flags: `disable-model-invocation` (Claude can't
auto-load; ALSO removes the description from context → zero standing cost) × `user-invocable`
(show/hide in the `/` menu). Pocock: a skill can exist to REMOVE the model's autonomy —
"procedures" the human invokes to force a process, keeping the human as strategic general
("do not delegate thinking to the model"). Anthropic's own guidance: disable model-invocation
"for workflows with side effects... You don't want Claude deciding to deploy."

## GD-7 · Statefulness — cross-session memory
Every session is a blank slate; a skill can exist to enforce read/write of durable file state
across sessions (Pocock's /teach). Only partly triangulated (mechanism confirmed by Anthropic;
the motivation is Pocock's).

## GD-8 · Worth is measurable — eval-first
Anthropic best-practices: "Create evaluations BEFORE writing extensive documentation. This
ensures your Skill solves real problems rather than documenting imagined ones." Pairs with
GD-4's frequency test (the demand side).

## GD-9 · Positive procedures + deterministic enforcement over prohibitions
Negative instructions ("do not use npm") burn budget on non-goals and are non-deterministic
(the model may do it anyway). For hard rules use a **deterministic pre-tool hook** (intercept
npm→pnpm via bash), not a prompt-based taboo. Badly designed skills are "balls of mud" of
abstract stylistic rules the model can't prioritize; well-designed skills are concise and
force a single posture.

## GD-10 · Autonomy relocates control (loops)
When a skill runs in an autonomous loop the question shifts from "worth a human calling it?" to
"can the loop/model trigger it reliably, and verify its output un-gameably?" Control relocates to
upstream backlog curation (human) + deterministic guardrails (TDD/CI). A loop-consumed skill must
be invocation-agnostic (NOT `disable-model-invocation` — that goes inert in `/loop`), leash-
tightening (small verifiable diffs), and paired with a reward-hack-resistant success signal. Full
treatment: [loops-and-autonomy.md](loops-and-autonomy.md). Anthropic def: agent = "LLMs using
tools based on environmental feedback in a loop." Sources: Karpathy YC talk (June 2025); Huntley
ghuntley.com/ralph (2025-07-14); Anthropic building-effective-agents + reward-hacking research.

## GD-11 · The gate applies to its own instruments (reflexivity)
Any instrument built to answer a skills/setup question — eval harness, corpus miner, metric,
synthetic oracle, dashboard — is itself a skill-shaped bet and must pass the same gates
BEFORE it is built: prior-art sweep first (Gate 0 — assume the field has this instrument
until a search says otherwise), "will this question recur?" (Gate 1), and **name the pending
decision the output would change** (Gate 2 — cheaper compute does not create value; a
pending decision does). Evidence (author's research program, 2026-07): every
instrument that skipped the gates was superseded or degenerated — a bespoke A/B falsified by
a 40-minute prior-art sweep; a synthetic bug-fix oracle whose own test docstring leaked the
gold fix to every arm. Every instrument that passed survived (passive telemetry, corpus
miner, regression canary). Corollary for oracle authoring: an eval task's visible artifacts
must never document their own fix — strip failing-test files to assertion-minimum. Status:
project-evidenced; external triangulation invited. Full findings:
https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md

## Sources
- Pocock corpus: 152-source research corpus (video/article transcripts), read at
  ground truth; every crisp claim triangulated before it entered a gate.
- Anthropic: code.claude.com/docs/en/skills · platform.claude.com/docs/en/agents-and-tools/
  agent-skills/{overview,best-practices} · anthropic.com/engineering/equipping-agents-for-the-
  real-world-with-agent-skills
- IFScale: arxiv.org/abs/2507.11538 ("How Many Instructions Can LLMs Follow at Once?").
