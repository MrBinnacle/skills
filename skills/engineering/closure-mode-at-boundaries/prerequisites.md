# Prerequisites

Before invoking closure mode for the first time, confirm your runtime and project provide the capabilities the discipline assumes.

## Runtime capabilities

| Capability | Why it matters | Minimum acceptable |
|---|---|---|
| **Parallel agent dispatch in a single message** | The swarm cost model assumes N agents run concurrently. Serial dispatch is N× slower and discourages defaulting closure mode at every boundary. | Parallel preferred; serial acceptable for low-volume use. |
| **≥2 role-suitable subagents** | Critic + Architect is the minimum viable swarm. Below this, closure mode collapses to "ask one agent to play 5 roles," which loses independence and reduces frame-rejection signal. | 2 distinct agents minimum. 5 preferred. |
| **Agent invocation that accepts a self-contained prompt** | Closure-mode SMEs start cold and need the candidate set plus project context inline. Runtimes that require the agent to share the parent context window are inefficient but workable. | Self-contained prompt acceptance; enough context to hold the candidate set plus a project brief. |

If your runtime fails any of these, see [swarm-composition.md](swarm-composition.md) for the role-to-runtime mapping table and serial-dispatch fallback.

## Project surfaces

| Surface | Why it matters | Examples |
|---|---|---|
| **Next-step authority** — wherever your project's "what comes next" candidate set is authored | Closure mode acts on a candidate set. If the project has no authoritative source, the closure swarm has nothing concrete to evaluate. | A state-file field (e.g., `store.json:next_exact_step`), a sprint board top card, an issue tracker query (e.g., `gh issue list --label "ready"`), a kanban WIP column, a roadmap section. |
| **Stable completion edge** — wherever "all gates green for this scope" is observable | Closure mode requires a stable completion frame. Invoked mid-implementation it produces noise. | All tests passing, all gates PASS in a state file, CI green on the lock commit, scope marked DONE in a tracker. |
| **Project memory or research surface** — wherever named-but-missing features and prior research findings live | The Critic's "frame-rejection: what is MISSING?" carve-out depends on access to the project's product memory. Without it, the Critic can only rank within the surfaced frame. | A `MEMORY.md`, a personal notepad, a research watchlist, an ADR directory, a Notion database, an Obsidian vault. |

If your project lacks any of these surfaces, you can still use closure mode for ad-hoc decisions, but the formalization (wiring it into a lock terminal step — see [formalization.md](formalization.md)) requires all three.

## Adopter mapping example

For a project using a sprint board, GitHub Issues, and an Obsidian vault for product memory:

- Next-step authority → top card of the sprint board's "Backlog" column
- Stable completion edge → the lock commit's CI status (green)
- Project memory → the Obsidian vault's `Decisions/` and `Research/` directories

For a project using a state file, a roadmap doc, and inline ADRs:

- Next-step authority → the state file's `next_step` or equivalent field
- Stable completion edge → the state file's `gate_check` block all-PASS
- Project memory → the inline ADRs at `docs/decisions/`

Substitute analogously for your stack. The discipline does not care about the implementation; it cares that the three surfaces exist and are addressable.
