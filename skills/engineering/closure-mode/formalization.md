# Formalization — wiring closure mode into the lock terminal step

Closure mode currently runs only when invoked manually. The minimum-cost change to make it the default at workflow boundaries is to extend whichever skill or hook owns your project's terminal lock step.

## Current terminal step (typical)

```
commit + state-write
```

## Proposed terminal step

```
commit + state-write + closure-mode run + closure→build transition + next-frame proposal
```

The two new sub-steps invoke the swarm — see [swarm-composition.md](swarm-composition.md) — and the [transition](transition.md), against the project's existing "next step" candidate set.

## Why this belongs at the lock terminal step

A phase-lock, sprint-lock, or merge-to-main event is the only privileged moment where "what just shipped" is stable AND "what comes next" is genuinely undetermined. Every other moment is inside build mode. Without this wiring, closure mode depends on user invocation — which means the next vector is often picked from the project's "next step" authority without any frame check, exactly as [case-study.md](case-study.md) demonstrates.

## Wire it into your project's lock surface

The wiring belongs in whichever surface owns the post-commit, post-lock terminal moment in YOUR project. Common candidates:

- A custom phase-lock or sprint-lock skill (if your project has one).
- The post-merge CI hook on the default branch (`main` / `master`).
- A retro template invoked at the end of each iteration.
- A `/done` slash command (if your runtime supports custom commands).
- A scheduled job at sprint-end timestamps.

Pick the one that fires reliably AND only once per boundary.

If your project has both a "discipline" skill (encodes gate order, conventions) and an "executor" skill (runs the gates, commits, writes state), the wiring belongs in the DISCIPLINE skill, not the executor — the executor's terminal moment is the discipline's entry point.

## Out of scope for this skill

This skill defines the discipline. The actual lock-surface extension is a separate change made by your project, with this skill as the reference.
