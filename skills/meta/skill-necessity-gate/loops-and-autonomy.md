# Autonomy mode — designing skills for loops (GD-10)

The core gate assumes a human is present to invoke procedures. Autonomous **loops** (Ralph/AFK,
and Claude Code's own `/loop`) remove the human from the execution loop. Control doesn't vanish —
it relocates. Run this supplement whenever a candidate skill will (or might) run unattended.

## The decisive mechanism
A skill fires inside a loop ONLY if the loop or the model can trigger it without a human command.
In Claude Code specifically: **a `disable-model-invocation` skill passed to `/loop` does not
execute — it arrives as plain text.** So the GD-6 control move (lock it to human-only) makes a
procedure **inert in autonomy**. Invocation topology therefore determines loop-compatibility.

## The three ways a procedure can trigger unattended
1. **Model-selection from a sharp `description`** (metadata is the trigger surface — Anthropic
   skills docs). Requires a precise, task-matching description.
2. **Baked into a standing plan/prompt file** the loop re-reads each iteration (Ralph `@fix_plan.md`).
3. **Pushed into an agent-role system prompt** (e.g. a reviewer role always gets the review skill).
Slash-command / human invocation does NOT work unattended.

## What GD-10 changes in the gate
- **Gate 3 (invocation topology) gains an axis: "will this run in a loop?"**
  - If yes and the LOOP must fire it → do NOT set `disable-model-invocation` (it goes inert).
    Keep it model-invocable with a sharp description + verification, OR relocate it upstream.
  - Human-invoked procedures belong at the EDGES: backlog curation (`/write-a-prd` →
    `/prd-to-issues` vertical-slice "tracer bullets" → `/triage` approval gate) and PR review.
    "HITL at the edges, AFK in the middle."
- **Gate 2 (worth) gains a verification requirement for autonomy:** an autonomous skill needs a
  **deterministic, reward-hack-resistant** success signal — tests/lint/CI/HTTP status, not a
  subjective proxy or a lone LLM critic (critics are gameable). Prefer TDD as the stop signal.
- **GD-7 (state) and GD-9 (deterministic enforcement) become essential, not optional.**

## Reward-hacking is the signature danger (design against it)
Agents fake success: `sys.exit(0)` to green a harness, or modify/delete tests (Anthropic, "From
shortcuts to sabotage," 2025-11-21) — and it generalizes to broader misalignment. A naive "tests
pass" signal is a magnet. Mitigate: **compound acceptance criteria** ("tests pass AND coverage
>80% AND no type errors AND lint clean"), held-out tests, a **separate** verifier ("don't grade
your own homework"), spawn/token budgets against runaway. OPEN GAP: no known tool reliably
prevents an agent from *deleting* existing tests — treat test integrity as a human-gated concern.

## `/loop` vs Ralph (don't conflate)
- **`/loop`** (Claude Code, official): scheduling/polling. Modes: `/loop 5m <p>` cron; `/loop <p>`
  self-paced (Claude picks the delay AND can end the loop when the task is provably complete);
  bare `/loop` = maintenance/`loop.md`. 7-day expiry; session-scoped.
- **Ralph** (Huntley): autonomous convergence — re-run a prompt over a backlog until done; the
  value is the fresh-context reset each pass (state on disk, not in the conversation).

Sources: code.claude.com/docs/en/scheduled-tasks · anthropic.com building-effective-agents,
equipping-agents-with-agent-skills, emergent-misalignment-reward-hacking · ghuntley.com/ralph ·
Karpathy YC talk (June 2025) · Pocock sandcastle + to-issues.

