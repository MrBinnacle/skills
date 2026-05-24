# Closure Mode at Boundaries — Gotchas

Append-only log. Never delete entries. Seed entries marked `[ANTICIPATED]` are speculative until observed; observed gotchas replace or supplement them.

---

## [OBSERVED 2026-05-24] Closure→build transition collapse — synthesis into menu

After running the closure swarm (5 SMEs on a sprint fork pick), the agent synthesized the SMEs' action list into a multi-voice A/B/C menu and handed it back to the user. The SMEs had produced concrete verifications (a phantom-dep grep, a blast-radius INSERT-site audit, a pre-flight requirement on a schema-CHECK migration, a missing-feature addition), none of which were executed. The "revised frame" presented was the original frame with team commentary attached. See [case-study.md](case-study.md) for the full failure trace.

**Rule:** The closure swarm's output is an action list, not a multi-voice menu. The transition step is execute-the-list, then present the revised frame. Synthesizing into a menu without executing is sequencing pretending to be orchestration.

**Recognition:** if you find yourself writing "the team converged on X with caveats" or "here are the three branches the team surfaced," you are about to fail the transition. Stop. Execute the verifications first.

## [OBSERVED 2026-05-24] Closure mode framed as edge-case workflow extension

When the user invoked team consultation at a sprint boundary via an autonomous-workflow entry point, the agent treated the request as "repurposing the autonomous workflow for an edge case" rather than as the natural execution of closure mode at the boundary. The framing burned a clarification step and produced an explicit acknowledgment that the request "isn't the autonomous workflow's normal pipeline." Both wrong.

**Rule:** Team consultation at a sprint boundary is the default operating mode, not an edge case. If the workflow surface (autonomous workflow, resume command, lock skill, or any other entry point) is sitting at a fork-pick moment after a clean lock, closure mode runs without framing apology.

**Recognition:** if you find yourself writing "this isn't the autonomous workflow's normal X" or "this is a repurposing of Y," check whether what the user is actually invoking is closure mode at a boundary. If yes, drop the framing and just run it.

## [ANTICIPATED] Closure mode invoked mid-implementation

If closure mode is invoked while a phase is mid-implementation (red→green not complete, gates not all passing), it WILL produce noise. The SMEs will rank candidates that are not yet eligible because the current scope is not yet a stable completion frame.

**Rule:** Closure mode requires a stable completion edge. Check whichever state field your project uses to track "all gates passing" — all must be PASS — before invoking the closure swarm. If gates are not all PASS, the right move is finishing the current scope, not pressure-testing the next one.

## [ANTICIPATED] Critic over-fires on frame rejection

The Critic SME is assigned frame-rejection as its specific job. This can produce reject-the-frame verdicts on every candidate set, which collapses to "nothing is ever the right next thing." The user has named a particular feature as the next planned vector — that does not mean every closure run should re-litigate "should we do that other thing instead." Once a feature is on the queue and named by the user, frame-rejection on candidate META forks is appropriate, but frame-rejection on the named feature itself is not.

**Rule:** The Critic rejects the frame relative to product motion. If the candidate set is ALL META/hygiene and a named feature is in memory, frame-rejection is appropriate. If the candidate set already contains a named feature, the Critic's job is rescoping and risk-flagging, not re-questioning the feature's existence.

## [ANTICIPATED] Closure mode confused with refinement mode

Refinement mode (lint, lint-strict promotion, dead-code removal, formatter check, simplification) operates on existing code to tighten it. Closure mode operates on the candidate set for the NEXT vector to pressure-test the frame. These are not the same. Running a deslop pass on changed files is refinement; running a deslop pass as part of pre-commit gates is refinement; running a deslop pass to decide whether the next sprint should be a feature or a refactor is closure.

**Rule:** Closure mode acts on candidates, not on code. If the input to the discipline is "what should we do next," it's closure. If the input is "here is what we just did, tighten it," it's refinement.

## [ANTICIPATED] Stale next-step accepted without closure

A project's "next step" authority (next-action manifest, sprint-board top card, state-file field, etc.) is updated at lock and remains until the next lock. If a session resumes much later, the next-step candidate set may have gone stale relative to the current product memory (new memories, new research, new security findings). Resuming and immediately accepting the next-step queue without a closure pass risks acting on a stale frame.

**Rule:** If the next-step queue has been sitting since the last lock and product memory has moved meaningfully since then, run closure mode before accepting the candidate set as the next vector.
