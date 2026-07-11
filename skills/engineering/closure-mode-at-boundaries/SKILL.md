---
name: closure-mode-at-boundaries
description: Closure-mode discipline at workflow boundaries. Use when a sprint, phase, or vertical slice locks clean, or when a multi-candidate "what next" decision arises. Owns the closure→build transition.
---

# Closure Mode at Boundaries

## The Insight

The moment a phase of work finishes is exactly when you (or your agent) are most tempted to
charge into the next thing without review. Nothing can be called "done" until someone has
deliberately tried to break it — and you can't move to the next phase until this one is
certified. That deliberate try-to-break-it pass is **closure mode**.

Three cognitive modes:

- **Build mode** — expand, construct, progress.
- **Refinement mode** — optimize, tighten.
- **Closure mode** — stress, invert, challenge, simulate failure.

Closure mode is NOT continuous. It is a deliberate phase shift, invoked at completion edges, that produces an action list which the workflow MUST execute before re-entering build mode with the next vector.

## Recognition

Closure mode applies when ANY of these hold:

- A sprint, phase, or vertical-slice lock just completed in the current session.
- A "what should we do next" decision surfaces 2+ candidate forks.
- The user invokes team consultation or SME deliberation at a boundary.
- The current message is the first prompt after a clean completion event.
- A previously-authored "next step" is stale relative to recent product memory or research.

Closure mode does NOT apply mid-implementation, mid-debugging, when working a single bounded scope, or when explicitly skipped.

## Workflow

Two halves: a parallel SME swarm (the closure run), then a transition step that executes the swarm's output. Both required. Running only the swarm and forwarding its output as a menu IS the failure mode — see [gotchas.md](gotchas.md).

Before the first invocation, confirm your runtime and project surfaces — see [prerequisites.md](prerequisites.md).

1. **Dispatch the swarm.** See [swarm-composition.md](swarm-composition.md) for the standard roster and role-to-runtime mapping table. Concrete copy-pasteable per-role prompts are in [prompt-templates.md](prompt-templates.md).
2. **Execute the transition.** See [transition.md](transition.md). The swarm produces an action list — verifications, scope corrections, pre-flights, additions, subtractions — not a multi-voice menu. The transition is the load-bearing step.
3. **Present the revised frame** — only after the action list is executed. Name a single defensible pick if revisions converge; otherwise name the values axis separating survivors.

For a worked example showing both the failure case and the correct execution, see [case-study.md](case-study.md).

For wiring closure mode into a phase-lock-style terminal step so it runs automatically at boundaries, see [formalization.md](formalization.md).

## Discipline vs implementation

The **discipline** is the stable contract:

- Closure mode is a phase shift, not a continuous overlay.
- The swarm produces an action list, not a menu.
- The transition is execute-the-list, not synthesize-and-forward.
- Termination requires a single defensible pick OR a named values axis.

The **implementation surface** is illustrative and adapts to your project:

- Specific subagent IDs (the oh-my-claudecode ("OMC") plugin, native Anthropic, Codex, Gemini, prompt-a-role-into-a-general-agent) — see the mapping table in [swarm-composition.md](swarm-composition.md).
- Specific next-step authority paths (state file, kanban top card, issue tracker query, roadmap section) — see [prerequisites.md](prerequisites.md).
- Specific lock-skill names (`phase-lock`, post-merge CI hook, retro template, `/done` slash command) — see [formalization.md](formalization.md).

When adopting this skill, hold the discipline as the contract; substitute your project's implementation surface.

## Checklist per boundary

```
[ ] Prerequisites confirmed (parallel dispatch, ≥2 role-suitable agents, next-step authority identified)
[ ] Swarm dispatched in parallel (single message, multiple agent calls)
[ ] Critic specifically assigned frame-rejection ("what is MISSING?")
[ ] Verifications run (any phantom-claim, grep-checkable assertion)
[ ] Scope corrections run (audit blast radius where cost was estimated from one site)
[ ] Pre-flight requirements scheduled or executed
[ ] Dead candidates removed (do not leave for "completeness")
[ ] Missing candidates added
[ ] Revised frame presented — single pick named OR values axis named
```

## Ship criteria — adopt this skill into your project

The skill is "ready to use" in YOUR project when:

- (a) Runtime prerequisites verified — see [prerequisites.md](prerequisites.md).
- (b) Subagent roles mapped to your runtime — use the mapping table in [swarm-composition.md](swarm-composition.md).
- (c) Your project's "next step authority" surface identified (state file, kanban, issue tracker query, etc.).
- (d) At least one trial closure run completed and the team can recognize the failure modes in [gotchas.md](gotchas.md) before they happen.
