# Closure → Build Transition

The load-bearing step of closure mode. The SME swarm produces an action list, not a menu. Converting it back into a menu and handing it to the user IS the failure mode — see [gotchas.md](gotchas.md).

## The five sub-steps

After the swarm returns, do NOT synthesize directly into a user-facing menu. Execute these in order.

### 1. Verifications

Any phantom-dep claims, "this codebase doesn't actually do X" claims, or grep-checkable assertions — RUN them. Cheap, deterministic, and kill bad candidates outright.

Examples: grep dependency manifests for a claimed dep; check whether a file path or function exists; verify a flag, feature, or migration is actually shipped.

### 2. Scope corrections

Where the Critic or any SME flagged cost false-precision, run the audit. Most common pattern: a candidate's cost is estimated from one change site when the actual blast radius is N sites.

### 3. Pre-flight requirements

Where Security or Architect demanded a pressure-test pre-flight before drafting (e.g., schema change against existing data needs a backfill policy decision), run it or mark the candidate as "pre-flight required, not shovel-ready." Do not present a candidate that has an outstanding pre-flight as if it is ready to pick up.

### 4. Frame additions

If the Critic surfaced a missing candidate the original frame omitted (commonly: a named feature in memory that the META candidate set ignored), size it and add it.

### 5. Frame subtractions

Kill candidates the verifications eliminated. Do not leave a dead candidate in the revised frame "for completeness." A dead candidate in a menu IS a vote for it.

## Then — and only then — present the revised frame

The revised frame contains:

- Only candidates that survived verification.
- Costs corrected per the scope audit.
- Pre-flight outputs attached (or pre-flight scheduled as a sequencing step).
- Any missing candidates the Critic added.

If revisions converge on a single defensible pick, NAME it. Do not present a menu when analysis is clear.

## Termination conditions

Closure mode terminates when EITHER:

- **(a)** A single revised pick is named with rationale and the user can accept or override, OR
- **(b)** 2-3 surviving candidates differ along a values axis the user must arbitrate, with the axis named explicitly.

Either case re-enters build mode with a new, stable scope.

## Deadlock escalation

If, after running the action list, no candidates survive AND no values axis cleanly separates a viable subset, closure mode is **deadlocked**. Do not invent a pick. Surface:

- The candidates eliminated and why.
- Any candidates surfaced by frame-addition and why none survived scoping.
- A request for a higher-order frame from the user — usually "what problem are we actually trying to solve this cycle?" — because deadlock usually means the candidate-set generation was upstream of a real frame error.

Deadlock is rare but real. Naming it explicitly beats grasping for the least-bad survivor.
