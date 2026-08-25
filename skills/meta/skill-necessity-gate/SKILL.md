---
name: skill-necessity-gate
description: Decide whether a capability should become a skill. Use when asking "should this be a skill?", pruning a library, choosing skill vs CLAUDE.md vs MCP vs hook, or before building an eval instrument.
disable-model-invocation: true
---

> **Normative status.** The admission policy is [`ADMISSION.md`](../../../ADMISSION.md)
> (`admission-policy v1`). This skill is the reference method for answering it —
> not the binding rule.

# skill-necessity-gate

Most ideas for new skills should not become skills. Every skill you add costs context space
in every conversation, and most candidates are better served by a different layer — or by
nothing. This checklist catches them: six gates, run in order, and a candidate must pass all
six. The default answer is "not a skill," and the goal is a correct decision, not an
approved one.

This skill is itself a deliberately-invoked **procedure** (`disable-model-invocation: true`)
— you run it when contemplating a skill. That is the framework applied to itself.

## When to run
- Someone (incl. you) says "let's make a skill for X" / "should this be a skill?"
- Auditing an existing skill for whether its context cost is justified.
- Deciding skill vs CLAUDE.md vs memory vs MCP vs pre-tool hook vs named workflow.
- A skill library feels bloated (see Mode B in [absence-detection.md](absence-detection.md)).
- **Before building any instrument** (harness, miner, metric, oracle, eval): instruments
  are skill-shaped bets and run the same gates (GD-11) — prior-art sweep at Gate 0,
  recurrence at Gate 1, and at Gate 2 **name the pending decision the output would
  change**; no decision, no build.

## Mode A — Gate a candidate (the core procedure)

Run the six gates IN ORDER. A candidate must pass ALL of them. Stop at the first failure
and route it where the gate says. Earlier gates are cheaper and reject more.

### Gate 0 · Layer triage — is this even skill-shaped?  (most candidates die here)
- Is it a **fact / stable preference / repo rule**? → CLAUDE.md or memory. NOT a skill.
- Is it **access to a system/data** (API, DB, service)? → MCP / connector. NOT a skill.
- Is it **trivially discoverable from the codebase** (which build tool, file layout)? → let
  the agent read the repo. NOT a skill and NOT CLAUDE.md — encoding it elsewhere rots.
- Is it **already supplied by the harness at point of use**, or a **recurring fan-out
  orchestration**? → nothing (redundant, rots) / a named workflow script. NOT a skill.
- Is it a **multi-step procedure / reusable capability**? → continue.
- Then: relevant **every** session (→ push into CLAUDE.md, accept always-on cost) or only
  **sometimes** (→ a skill, loaded only when needed, is the right home)? Only "sometimes" continues.

### Gate 1 · Recurrence — does the pattern actually recur?
- Criterion is **frequency, not complexity.** Reject the "too simple" fallacy — trivial
  prompts you type constantly are prime skills.
- **Don't predict — measure.** Park the candidate in the skills folder and count how often
  you actually reach for it. Promote on demonstrated "freaking often" frequency.
- **Count occasions, not artifacts.** Recurrence mined from agent transcripts must be
  deduped by run: one orchestrated fire spawning N parallel seats is n=1, not n=N.
- If you keep running **two existing skills together** → MERGE them, don't add a third.
- Unproven + unmeasured → **park & observe, do not author yet.**

### Gate 2 · Worth — does value clear cost? Measure, don't argue.
- **Cost:** a *model-invocable* skill adds ~100 always-on tokens to the system prompt and
  competes in the skill-list budget (~1% of context; least-used descriptions get truncated
  then dropped at scale). Live skills also dilute each other's attention. *(A procedure —
  Gate 3 — costs ZERO standing tokens, so this gate is lenient for procedures.)*
- **Benefit — eval first:** build the eval BEFORE the docs so you solve a real problem, not
  an imagined one. Run **with-skill vs without-skill** on pass-rate / tokens / time — minding
  the traps that make naive skill benchmarks lie ([governing-dynamics.md](governing-dynamics.md) GD-11).
- Author only if measured benefit > cost. Exception: a zero-cost procedure that reliably
  enforces a process you care about passes on control value alone.

### Gate 3 · Invocation topology — if it should exist, what KIND?
Deciding question: **who does the strategic thinking?**
- Skill dictates **how/what** (planning, steps, the thinking), or has **side effects**
  (deploy/commit/send) → **PROCEDURE**, human-invoked. Set `disable-model-invocation: true`.
  "Do not delegate thinking to the model." Zero standing cost; you stay the strategic general.
- Background reference the model should pull when relevant → **ABILITY**, model-invoked
  (default). Pay ~100 tokens; the description IS the router (Gate 5).
- Two flags → four states: `disable-model-invocation` × `user-invocable`.
- **This is partly a user-values call.** SURFACE the budget math + the control tradeoff and
  ASK; do not auto-decide auto-vs-manual.
- **Autonomy axis (GD-10): "will this run inside an autonomous loop?"** If yes and the loop must
  fire it, do NOT set `disable-model-invocation` — in Claude Code such a skill goes **inert in
  `/loop`** (arrives as plain text). Keep it model-invocable with a sharp description +
  verification, or relocate it upstream as a human backlog gate. Full supplement:
  [loops-and-autonomy.md](loops-and-autonomy.md).

### Gate 4 · Statefulness — cross-session memory?
- Must it survive a blank-slate new session? → the skill's job includes enforcing read/write
  of durable file state. Design the persistence contract explicitly.
- If not → keep it stateless; don't add machinery you won't use.

### Gate 5 · Shape for low cost — once you commit
- **The description is the highest-leverage tokens.** Third person, "what it does + when to
  use it"; it competes with every other skill's description for dispatch. Write it as a ROUTER.
- **Concise enough to force a posture** (a 4–5 sentence skill can be powerful). Actionable
  procedure > documentation. Body < 500 lines; progressive disclosure, references one level deep.
- **Prefer positive procedures + deterministic enforcement over prohibitions (GD-9).**
  "Negative" instructions ("do not use npm") burn budget and are non-deterministic — use a
  **pre-tool hook**, not a prompt-based taboo.

## Refusal predicate (the fast "no")
Reject/route when it's: a fact (→ memory/CLAUDE.md) · access (→ MCP) · discoverable from the
repo (→ read the code) · harness-supplied at point of use (→ nothing) · a fan-out
orchestration (→ named workflow) · always-on (→ push) · recurrence unproven (→ park &
observe) · better merged (→ merge) · benefit ≤ cost for an ability · delegating strategic
thinking the human should own · a "ball of mud" of abstract rules · mostly negative
instructions (→ hook).

## Other modes
- **Mode B — library audit / anti-bloat** (incl. the retire-a-skill criteria) and
  **Mode C — absence detection** (what skills are MISSING?): see
  [absence-detection.md](absence-detection.md).

## Discipline vs implementation

The **discipline** (stable contract): six ordered gates, refusal predicate,
default-to-"not a skill", measure-don't-argue, GD-11. The **implementation surface**
(illustrative — swap for your runtime): the ~100-token / 1%-of-context numbers (Claude
Code, 2026), frontmatter flag names, `/loop` semantics, tools named in examples.

## Provenance
Evidence behind every gate (Matt Pocock's methodology triangulated against Anthropic's
skill docs + IFScale): [governing-dynamics.md](governing-dynamics.md). Record surprises
in [gotchas.md](gotchas.md) (append-only).
